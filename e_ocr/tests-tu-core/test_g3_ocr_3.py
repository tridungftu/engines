"""OCR-3: DOCX DEMO tạo trong RAM; parser nguồn chỉ đọc, không dịch vụ/COM."""

from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from xml.sax.saxutils import escape
import zipfile

from kho_tri_thuc.engines.e_ocr import bang
from kho_tri_thuc.ha_tang.primitives import DataError
import test_g2_17 as schema_tests


DOCX_ID = "10000000-0000-4000-8000-000000000001"
DETAIL_ID = "10000000-0000-4000-8000-000000000002"
PDF_ID = "10000000-0000-4000-8000-000000000003"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def paragraph(text):
    return '<w:p><w:r><w:t xml:space="preserve">' + escape(text) + '</w:t></w:r></w:p>'


def cell(text="", *, span=1, merge=None):
    props = f'<w:gridSpan w:val="{span}"/>' if span != 1 else ''
    if merge is not None:
        props += '<w:vMerge/>' if merge == 'continue' else '<w:vMerge w:val="restart"/>'
    texts = text if isinstance(text, list) else [text]
    return '<w:tc><w:tcPr>' + props + '</w:tcPr>' + ''.join(map(paragraph, texts)) + '</w:tc>'


def table(rows, cols=3):
    return ('<w:tbl><w:tblGrid>' + '<w:gridCol w:w="1440"/>' * cols + '</w:tblGrid>'
            + ''.join('<w:tr>' + row + '</w:tr>' for row in rows) + '</w:tbl>')


def docx(body, *, image=False, header=None):
    stream = io.BytesIO()
    if image:
        body += ('<w:p><w:r><a:blip xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                 'r:embed="img1"/></w:r></w:p>')
    with zipfile.ZipFile(stream, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types/>')
        archive.writestr('word/document.xml', f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>')
        if image:
            archive.writestr('word/_rels/document.xml.rels',
                             '<Relationships><Relationship Id="img1" Target="media/demo.png"/></Relationships>')
            archive.writestr('word/media/demo.png', b'DEMO deliberately not a valid image')
        if header is not None:
            archive.writestr('word/header1.xml', f'<w:hdr xmlns:w="{W}">{header}</w:hdr>')
    return stream.getvalue()


def ref(raw):
    return {"contract": "tham_chieu_tep.v1", "phien_ban": "1.0.0", "tep_id": DOCX_ID,
            "ten_tep": "bang-DEMO.docx", "mime": bang.MIME_DOCX,
            "kich_thuoc": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "het_han_luc": None}


def read(raw, **kwargs):
    return bang.trich_bang(raw, ref(raw), phan_hoi_nguon_tep_id=DETAIL_ID, **kwargs)


class DocxNguonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Chỉ skip khi thiếu dependency thật; thiếu vendor nội bộ phải đỏ.
        try:
            bang._nhap_parser_nguon()
        except ModuleNotFoundError as exc:
            if exc.name not in {'pymupdf', 'defusedxml'}:
                raise
            raise unittest.SkipTest(f"CHUA_KIEM dependency parser nguồn: {exc.name}") from None
        schema_tests.BundleContractTest.setUpClass()
        cls.validator = schema_tests.BundleContractTest()

    def check(self, raw, **kwargs):
        result = read(raw, **kwargs)
        self.validator.validate("urn:ktt:contract:du_lieu_bang.v1", result.bang)
        json.dumps(result.phan_hoi_nguon, ensure_ascii=False, allow_nan=False)
        return result

    def test_o_rong_va_hang_rong_khong_mat(self):
        raw = docx(table([cell('A') + cell() + cell('0007'), cell() * 3]))
        result = self.check(raw)
        t = result.bang['bang'][0]
        self.assertEqual((t['so_dong'], len(t['cot']), len(t['o'])), (2, 3, 6))
        self.assertEqual([c['gia_tri']['gia_tri'] for c in t['o']], ['A', '', '0007', '', '', ''])
        self.assertEqual(t['o'][1]['ma_vung_nguon'], [])
        self.assertIn('/row/0/col/1', t['o'][1]['vi_tri']['dinh_vi'])

    def test_gop_hang_cot_va_gop_hinh_chu_nhat(self):
        raw = docx(table([
            cell('Gộp 2x2', span=2, merge='restart') + cell('A'),
            cell('', span=2, merge='continue') + cell('B'),
            cell('C') + cell('D') + cell('E'),
        ]))
        t = self.check(raw).bang['bang'][0]
        self.assertEqual(len(t['o']), 6)
        anchor = t['o'][0]
        self.assertEqual([anchor[k] for k in ('dong', 'cot', 'gop_dong', 'gop_cot')], [0, 0, 2, 2])
        self.assertEqual(anchor['gia_tri']['gia_tri'], 'Gộp 2x2')
        self.assertFalse(any(c['dong'] == 1 and c['cot'] < 2 for c in t['o']))

    def test_o_gop_rong_van_co_anchor(self):
        t = self.check(docx(table([cell('', span=3)]))).bang['bang'][0]
        self.assertEqual(len(t['o']), 1)
        self.assertEqual((t['o'][0]['gop_cot'], t['o'][0]['gia_tri']['gia_tri']), (3, ''))

    def test_bang_dai_100_hang_khong_cat_hang_cuoi(self):
        raw = docx(table([cell(f'DEMO {r:03d}') + cell() + cell('1.000,50') for r in range(100)]))
        t = self.check(raw).bang['bang'][0]
        self.assertEqual((t['so_dong'], len(t['o'])), (100, 300))
        self.assertEqual(t['o'][-3]['gia_tri']['gia_tri'], 'DEMO 099')
        self.assertEqual(t['o'][-1]['dong'], 99)

    def test_bang_40_cot_khong_cat_cot_cuoi(self):
        t = self.check(docx(table([''.join(cell(str(c)) for c in range(40))], 40))).bang['bang'][0]
        self.assertEqual((len(t['cot']), len(t['o'])), (40, 40))
        self.assertEqual(t['o'][-1]['cot'], 39)

    def test_grid_before_giu_vi_tri_khong_tu_them_o_rong(self):
        raw = docx(table(['<w:trPr><w:gridBefore w:val="1"/></w:trPr>' + cell('B') + cell('C')]))
        t = self.check(raw).bang['bang'][0]
        self.assertEqual(len(t['cot']), 3)
        self.assertEqual([c['cot'] for c in t['o']], [1, 2])

    def test_content_control_trong_o_khong_thanh_rong_hoac_mat_mot_phan(self):
        control = '<w:sdt><w:sdtContent>' + paragraph('DEMO 123.456') + '</w:sdtContent></w:sdt>'
        for prefix in ('', paragraph('DEMO đã đọc')):
            body = table(['<w:tc>' + prefix + control + '</w:tc>'], 1)
            for in_header in (False, True):
                raw = docx('', header=body) if in_header else docx(body)
                extract, layout = bang._nhap_parser_nguon()
                legacy = extract(raw, image_reader=lambda _data: '')
                self.assertIn('DEMO 123.456', legacy.text)
                source = layout(raw, legacy, embedded_pages=[])
                self.assertFalse(any('123.456' in u['text'] for u in source['units']))
                with self.subTest(prefix=prefix, header=in_header):
                    with self.assertRaises(DataError) as ctx:
                        read(raw)
                    self.assertEqual(ctx.exception.code, 'OCR_BANG_DOCX_INVALID')

    def test_grid_after_khong_tra_thanh_cong_bang_mat_cot_cuoi(self):
        for before, cols in ((0, 3), (1, 4)):
            props = (f'<w:trPr><w:gridBefore w:val="{before}"/>'
                     '<w:gridAfter w:val="1"/></w:trPr>')
            body = table([props + cell('DEMO A') + cell('DEMO B')], cols)
            for in_header in (False, True):
                raw = docx('', header=body) if in_header else docx(body)
                with self.subTest(before=before, header=in_header):
                    with self.assertRaises(DataError) as ctx:
                        read(raw)
                    self.assertEqual(ctx.exception.code, 'OCR_BANG_DOCX_INVALID')

    def test_content_control_noi_tuyen_va_grid_after_0_van_doc_du(self):
        inline = ('<w:tc><w:p><w:sdt><w:sdtContent><w:r><w:t>DEMO 123.456</w:t>'
                  '</w:r></w:sdtContent></w:sdt></w:p></w:tc>')
        raw = docx(table(['<w:trPr><w:gridAfter w:val="0"/></w:trPr>' + inline], 1))
        t = self.check(raw).bang['bang'][0]
        self.assertEqual((len(t['cot']), len(t['o'])), (1, 1))
        self.assertEqual(t['o'][0]['gia_tri']['gia_tri'], 'DEMO 123.456')
        self.assertTrue(t['o'][0]['ma_vung_nguon'])

    def test_vuot_gioi_han_nguon_bao_loi_khong_tra_bang_cat(self):
        for rows, cols in ((101, 1), (1, 41)):
            with self.subTest(rows=rows, cols=cols), self.assertRaises(DataError) as ctx:
                read(docx(table([cell('DEMO') * cols for _ in range(rows)], cols)))
            self.assertEqual(ctx.exception.code, 'OCR_BANG_DOCX_INVALID')

    def test_khong_suy_bang_tu_van_ban(self):
        raw = docx(paragraph('Mã\tTiền\n0001 | 1.000,50\n0002 | 2.000,00'))
        self.assertEqual(self.check(raw).bang['bang'], [])

    def test_nhieu_bang_va_header_dinh_vi_khong_trung(self):
        t1 = table([cell('A')], 1)
        result = self.check(docx(paragraph('DEMO') + t1 + paragraph('Giữa') + t1, header=t1))
        tables = result.bang['bang']
        self.assertEqual(len(tables), 3)
        self.assertEqual(len({t['ma'] for t in tables}), 3)
        self.assertEqual(len({t['vi_tri']['dinh_vi'] for t in tables}), 3)
        for t in tables:
            index = int(t['vi_tri']['dinh_vi'].rsplit('/', 1)[1])
            source = result.phan_hoi_nguon['layout']['blocks'][index]
            self.assertEqual(source['type'], 'table')
            self.assertEqual(t['vi_tri']['tep_id'], DOCX_ID)
            self.assertNotIn('trang', t['vi_tri'])
            self.assertNotIn('bbox', t['o'][0]['vi_tri'])

    def test_khong_suy_tieu_de_kieu_so_don_vi(self):
        texts = ['0007', '1.234,50 VND', '31/10/2026']
        t = self.check(docx(table([cell(texts), cell('DEMO')], 1))).bang['bang'][0]
        self.assertEqual(t['so_dong'], 2)
        self.assertEqual(t['o'][0]['gia_tri'], {'kieu': 'van_ban', 'gia_tri': '\n'.join(texts)})
        self.assertEqual(t['cot'], [{'ma': 'cot_0', 'ten': 'Cột 1', 'kieu': 'van_ban', 'don_vi': None}])

    def test_chan_ocr_anh_nhung_va_giu_canh_bao(self):
        extract_docx, word_layout = bang._nhap_parser_nguon()
        extraction = sys.modules[extract_docx.__module__]
        layout = sys.modules[word_layout.__module__]
        with patch.object(extraction, 'image_text', side_effect=AssertionError('Không OCR')), \
                patch.object(layout, 'word_layout', wraps=layout.word_layout) as spy:
            result = self.check(docx(table([cell('DEMO')], 1), image=True))
        self.assertEqual(spy.call_args.kwargs, {'embedded_pages': []})
        self.assertTrue(any('Ảnh nhúng' in w for w in result.phan_hoi_nguon['canh_bao']))
        self.assertEqual(result.bang['bang'][0]['o'][0]['gia_tri']['gia_tri'], 'DEMO')

    def test_docx_hong_va_track_changes_bi_tu_choi(self):
        for raw in (b'not-docx', docx('<w:ins>' + paragraph('DEMO') + '</w:ins>')):
            with self.subTest(raw=raw[:15]), self.assertRaises(DataError) as ctx:
                read(raw)
            self.assertEqual(ctx.exception.code, 'OCR_BANG_DOCX_INVALID')

    def test_revision_hash_nguon_va_phan_hoi_doc_lap(self):
        raw = docx(table([cell('DEMO')], 1))
        result = self.check(raw, revision=7, nguon_tep_ids=[PDF_ID, PDF_ID])
        self.assertEqual(result.bang['revision'], 7)
        self.assertEqual(result.bang['nguon_tep_ids'], [PDF_ID, DOCX_ID])
        self.assertEqual(result.phan_hoi_nguon['tham_chieu_tep']['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.bang['phan_hoi_nguon_tep_id'], DETAIL_ID)
        self.assertTrue(result.bang['bang'][0]['can_soat'])
        self.assertNotIn('provenance', result.bang)
        result.phan_hoi_nguon['layout']['blocks'][0]['cells'][0]['row'] = 20
        self.assertEqual(result.bang['bang'][0]['o'][0]['dong'], 0)


class BaoVeVaSeamTests(unittest.TestCase):
    def test_dau_vao_sai_chan_truoc_parser(self):
        raw = b'DEMO'
        mutations = ({'sha256': '0' * 64}, {'kich_thuoc': True}, {'mime': 'text/plain'},
                     {'tep_id': 'khong-phai-uuid'}, {'ten_tep': '../demo.docx'},
                     {'het_han_luc': '2020-01-01T00:00:00Z'}, {'het_han_luc': 'sai'},
                     {'phien_ban': '2.0.0'}, {'them': True})
        for change in mutations:
            with self.subTest(change=change):
                source = ref(raw)
                source.update(change)
                parser = Mock(side_effect=AssertionError('Không được gọi'))
                with self.assertRaises(DataError):
                    bang.trich_bang(raw, source, phan_hoi_nguon_tep_id=DETAIL_ID,
                                   extract_docx=parser, word_layout=parser)
                parser.assert_not_called()

    def test_revision_id_trung_va_bytes_rong(self):
        for kwargs in ({'revision': True}, {'revision': 0}, {'phan_hoi_nguon_tep_id': DOCX_ID},
                       {'nguon_tep_ids': [DETAIL_ID]}, {'nguon_tep_ids': ['sai']}):
            with self.subTest(kwargs=kwargs), self.assertRaises(DataError):
                bang.trich_bang(b'DEMO', ref(b'DEMO'),
                               **({'phan_hoi_nguon_tep_id': DETAIL_ID} | kwargs))
        with self.assertRaises(DataError):
            read(b'')

    def test_layout_sai_khong_tra_bang_thieu(self):
        raw = docx(table([cell('DEMO')], 1))
        # Seam vẫn qua cổng cấu trúc DOCX thật, cần dependency của cổng này.
        try:
            bang._kiem_cau_truc_chua_ho_tro(raw)
        except ModuleNotFoundError as exc:
            if exc.name != 'defusedxml':
                raise
            self.skipTest(f"CHUA_KIEM dependency parser nguồn: {exc.name}")
        base = {'warnings': [], 'units': [{'id': 'u0', 'text': 'DEMO'}], 'blocks': [
            {'type': 'table', 'rows': 1, 'cols': 1, 'cells': [
                {'row': 0, 'col': 0, 'rowspan': 1, 'colspan': 1, 'unit_ids': ['u0']}]}]}
        result = read(raw, extract_docx=lambda *a, **k: SimpleNamespace(ocr_pages=0),
                      word_layout=lambda *a, **k: deepcopy(base))
        self.assertEqual(result.bang['bang'][0]['o'][0]['gia_tri']['gia_tri'], 'DEMO')
        variants = []
        for field, value in (('row', 1), ('col', -1), ('rowspan', 0), ('colspan', True), ('unit_ids', ['missing'])):
            layout = deepcopy(base)
            layout['blocks'][0]['cells'][0][field] = value
            variants.append(layout)
        duplicate = deepcopy(base)
        duplicate['blocks'][0]['cells'] *= 2
        variants.append(duplicate)
        for layout in variants:
            parser = Mock(return_value=layout)
            with self.subTest(layout=layout), self.assertRaises(DataError) as ctx:
                read(raw, extract_docx=lambda *a, **k: SimpleNamespace(ocr_pages=0),
                     word_layout=parser)
            self.assertEqual(ctx.exception.code, 'OCR_BANG_DOCX_INVALID')
            parser.assert_called_once()

    def test_nap_vendor_bo_qua_env_va_giu_nguyen_trang_thai(self):
        before_path, before_bytecode = sys.path[:], sys.dont_write_bytecode
        extract, layout = Mock(), Mock()
        def load(name, package):
            self.assertEqual(package, bang.__package__)
            self.assertEqual(sys.path, before_path)
            self.assertEqual(sys.dont_write_bytecode, before_bytecode)
            return SimpleNamespace(extract_docx=extract) if name.endswith('extraction') else SimpleNamespace(word_layout=layout)
        with patch.dict(os.environ, {'KTT_NGUON_OCR': 'DEMO/source'}), \
                patch.object(Path, 'is_dir', side_effect=AssertionError('Không dò nguồn ngoài')), \
                patch.object(bang.importlib, 'import_module', side_effect=load) as loader:
            self.assertEqual(bang._nhap_parser_nguon(), (extract, layout))
        self.assertEqual([c.args for c in loader.call_args_list], [
            ('.vendor.mask_ocr.extraction', bang.__package__),
            ('.vendor.mask_ocr.layout', bang.__package__),
        ])
        self.assertEqual(sys.path, before_path)
        self.assertEqual(sys.dont_write_bytecode, before_bytecode)

    def test_import_loi_cung_khoi_phuc_path_va_bytecode(self):
        before_path, before_bytecode = sys.path[:], sys.dont_write_bytecode
        with patch.dict(os.environ, {'KTT_NGUON_OCR': 'DEMO/source'}), \
                patch.object(Path, 'is_dir', side_effect=AssertionError('Không dò nguồn ngoài')), \
                patch.object(bang.importlib, 'import_module', side_effect=ImportError('DEMO')):
            with self.assertRaises(ImportError):
                bang._nhap_parser_nguon()
        self.assertEqual(sys.path, before_path)
        self.assertEqual(sys.dont_write_bytecode, before_bytecode)

    def test_thieu_vendor_hoac_dependency_khong_am_tham_fallback(self):
        before_path, before_bytecode = sys.path[:], sys.dont_write_bytecode
        for missing in (bang.__package__ + '.vendor.mask_ocr', 'pymupdf', 'defusedxml'):
            error = ModuleNotFoundError(name=missing)
            with self.subTest(missing=missing), \
                    patch.dict(os.environ, {'KTT_NGUON_OCR': 'DEMO/missing'}), \
                    patch.object(Path, 'is_dir', side_effect=AssertionError('Không dò nguồn ngoài')), \
                    patch.object(bang.importlib, 'import_module', side_effect=error) as loader:
                with self.assertRaises(ModuleNotFoundError) as caught:
                    bang._nhap_parser_nguon()
                self.assertIs(caught.exception, error)
            loader.assert_called_once_with('.vendor.mask_ocr.extraction', bang.__package__)
        self.assertEqual(sys.path, before_path)
        self.assertEqual(sys.dont_write_bytecode, before_bytecode)


if __name__ == '__main__':
    unittest.main()
