"""G3-GOI-19/20: SDK và một gói OCR; closure nguồn và lock thư viện.

DOCX DEMO tạo trong RAM. Nhóm mock chỉ thay dependency ngoài bằng stdlib,
giữ nguyên parser vendor và adapter. Nhóm thật ghi CHUA_KIEM nếu thiếu
dependency; không cài thêm. Có thể chạy nguyên bộ trong môi trường chỉ
cài SDK wheel candidate và gói OCR, không cần repo/src trong PYTHONPATH.
"""

import ast
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import importlib.util
from importlib import metadata
import io
import json
from pathlib import Path
import re
import sys
from types import ModuleType
import unittest
from unittest.mock import patch
from uuid import UUID
from xml.etree import ElementTree
from xml.sax.saxutils import escape
import zipfile

from kho_tri_thuc.engines.e_ocr import bang, chay
from kho_tri_thuc.sdk_core.engine import GiuViec, KenhCore, SDKEngine
from kho_tri_thuc.sdk_core.ngu_canh import MaBiMat
from kho_tri_thuc.sdk_core.primitives import DataError


GOI = Path(__file__).resolve().parents[1]
TEN_GOI = 'kho_tri_thuc.engines.e_ocr'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
DOCX_ID = '10000000-0000-4000-8000-000000000001'
DETAIL_ID = '10000000-0000-4000-8000-000000000002'


def _imports_engine():
    """Quét cả vendor và lazy import mà không nạp dependency/config/model."""
    for tep in sorted(GOI.rglob('*.py')):
        rel = tep.relative_to(GOI)
        if rel.parts[0] == 'tests':
            continue
        package = '.'.join((TEN_GOI, *rel.parts[:-1]))
        for node in ast.walk(ast.parse(tep.read_text(encoding='utf-8'))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [importlib.util.resolve_name('.' * node.level + (node.module or ''), package)]
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == '__import__':
                    raise AssertionError(f'{rel}:{node.lineno}: không cho phép __import__')
                if isinstance(func, ast.Attribute) and func.attr == 'import_module':
                    if (not node.args or not isinstance(node.args[0], ast.Constant)
                            or not isinstance(node.args[0].value, str)):
                        raise AssertionError(f'{rel}:{node.lineno}: cần tên import tường minh')
                    names = [importlib.util.resolve_name(node.args[0].value, package)]
            for name in names:
                yield str(rel), node.lineno, name


def _ten_goi(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def paragraph(text):
    return '<w:p><w:r><w:t xml:space="preserve">' + escape(text) + '</w:t></w:r></w:p>'


def cell(text='', props=''):
    return '<w:tc><w:tcPr>' + props + '</w:tcPr>' + paragraph(text) + '</w:tc>'


def table(rows, cols):
    return ('<w:tbl><w:tblGrid>' + '<w:gridCol w:w="1440"/>' * cols + '</w:tblGrid>'
            + ''.join('<w:tr>' + row + '</w:tr>' for row in rows) + '</w:tbl>')


def docx(body, *, header=None, image=False):
    if image:
        body += ('<w:p><w:r><a:blip xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                 'r:embed="img1"/></w:r></w:p>')
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types/>')
        archive.writestr('word/document.xml',
                         f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>')
        if header is not None:
            archive.writestr('word/header1.xml', f'<w:hdr xmlns:w="{W}">{header}</w:hdr>')
        if image:
            archive.writestr('word/_rels/document.xml.rels',
                             '<Relationships><Relationship Id="img1" Target="media/demo.png"/></Relationships>')
            archive.writestr('word/media/demo.png', b'DEMO image must not be read by OCR')
    return stream.getvalue()


def read(raw, **kwargs):
    ref = dict(contract='tham_chieu_tep.v1', phien_ban='1.0.0', tep_id=DOCX_ID,
               ten_tep='bang-DEMO.docx', mime=bang.MIME_DOCX, kich_thuoc=len(raw),
               sha256=hashlib.sha256(raw).hexdigest(), het_han_luc=None)
    return bang.trich_bang(raw, ref, phan_hoi_nguon_tep_id=DETAIL_ID, **kwargs)


class GoiDocLapTests(unittest.TestCase):
    def test_manifest_chua_cong_bo_capability_bang(self):
        manifest = json.loads((GOI / 'engine.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['ma'], 'e_ocr')
        self.assertEqual([c['ma'] for c in manifest['capability']],
                         ['ocr.trich_van_ban@1', 'ocr.trich_vung@1'])
        self.assertEqual(manifest['ho_so_chay_mau']['diem_vao'], TEN_GOI + '.chay')

    def test_byte_vendor_khop_sha_da_ghim(self):
        nguon = (GOI / 'NGUON.md').read_text(encoding='utf-8')
        rows = re.findall(
            r'^\| `vendor/mask_ocr/([^`]+\.py)` \| `[a-f0-9]{64}` \| `([a-f0-9]{64})` \|$',
            nguon, re.MULTILINE)
        self.assertEqual(len(rows), 5)
        for name, expected in rows:
            with self.subTest(tep=name):
                self.assertEqual(hashlib.sha256((GOI / 'vendor/mask_ocr' / name).read_bytes()).hexdigest(),
                                 expected)

    def test_import_ke_ca_lazy_chi_noi_bo_sdk_va_dependency(self):
        def kiem_ten(name):
            if name.split('.')[0] in sys.stdlib_module_names | {'pymupdf', 'defusedxml', 'pdfplumber', 'PIL', 'numpy'}:
                return
            self.assertTrue(name == TEN_GOI or name.startswith(TEN_GOI + '.')
                            or name == 'kho_tri_thuc.sdk_core'
                            or name.startswith('kho_tri_thuc.sdk_core.'), name)

        for rel, line, name in _imports_engine():
            with self.subTest(tep=rel, dong=line):
                kiem_ten(name)

    def test_nhan_viec_demo_bang_sdk_that_va_kenh_gia(self):
        luc = datetime(2026, 11, 6, tzinfo=timezone.utc)
        lease = GiuViec(UUID(int=1), UUID(int=2), UUID(int=3), UUID(int=4),
                        'demo', 'ocr', UUID(int=5), 1, luc + timedelta(minutes=1), MaBiMat('DEMO'))
        dau_vao = dict(van_ban_demo='DEMO Ánh Dương, 06/11/2026',
                       revision_tep_truoc=2, du_lieu_ket_qua=dict(
                           bien_the='demo', ma_contract='van_ban_tai_lieu.v1',
                           phien_ban_contract='1.0.0', trang_thai='DEMO', ly_do=None,
                           revision_truoc=0, nguon=[]))
        calls = []

        class KenhGia(KenhCore):
            def goi(self, operation, giu_viec, **payload):
                calls.append((operation, giu_viec))
                if operation == 'doc_dau_vao':
                    return dau_vao
                if operation != 'ghi_ket_qua':
                    raise AssertionError('Lời gọi ngoài ca DEMO')
                self.raw = payload['luong'].read()
                self.payload = payload
                return {'da_ban_giao': True}

        kenh = KenhGia()
        sdk = SDKEngine(lease, kenh_core=kenh, dong_ho=lambda: luc)
        self.assertEqual(chay.xu_ly_viec(sdk, backend=chay.BackendOCRGia()), {'da_ban_giao': True})
        self.assertEqual(calls, [('doc_dau_vao', lease), ('ghi_ket_qua', lease)])
        self.assertEqual(kenh.raw.decode('utf-8'), dau_vao['van_ban_demo'])
        self.assertEqual(kenh.payload['du_lieu'], dau_vao['du_lieu_ket_qua'])
        self.assertEqual(kenh.payload['revision_tep_truoc'], 2)
        self.assertIs(bang.DataError, DataError)


class KhoaThuVienTests(unittest.TestCase):
    # Ngoại lệ/bắc cầu có phạm vi cụ thể; thêm comment không hợp thức hóa gói lạ.
    IMPORT_DA_CAI = {'pdfplumber': 'pdfplumber', 'PIL': 'pillow', 'numpy': 'numpy'}
    IMPORT_CHUA_CAI = {'pymupdf': 'pymupdf', 'defusedxml': 'defusedxml'}
    BAC_CAU = {'pdfminer-six': 'pdfplumber', 'pypdfium2': 'pdfplumber',
               'charset-normalizer': 'pdfminer-six', 'cryptography': 'pdfminer-six',
               'cffi': 'cryptography', 'pycparser': 'cffi'}

    def setUp(self):
        self.lock = (GOI / 'requirements.lock').read_text(encoding='utf-8')

    def _kiem_khoa(self, text):
        pins, nhap, thieu, bac_cau = {}, {}, {}, {}
        for line in text.splitlines():
            if not line.strip():
                continue
            if line.startswith('#'):
                if not line.startswith(('# import:', '# bac-cau:', '# chua-cai:')):
                    continue
                row = re.fullmatch(
                    r'# (import|bac-cau|chua-cai): ([\w.-]+) \| ([\w.-]+) \| (.+)', line)
                self.assertIsNotNone(row, 'Khai báo thiếu tên hoặc lý do: ' + line)
                kind, name, target, reason = row.groups()
                self.assertGreaterEqual(len(reason.strip()), 10, 'Cần lý do cụ thể: ' + line)
                entries = {'import': nhap, 'chua-cai': thieu, 'bac-cau': bac_cau}[kind]
                key = _ten_goi(name) if kind == 'bac-cau' else name
                self.assertNotIn(key, entries, 'Khai báo lặp: ' + name)
                entries[key] = _ten_goi(target)
                continue
            pin = re.fullmatch(r'([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][A-Za-z0-9.!+_-]*)', line)
            self.assertIsNotNone(pin, 'Chỉ chấp nhận exact pin: ' + line)
            name, version = pin.groups()
            name = _ten_goi(name)
            self.assertNotIn(name, pins, 'Pin lặp: ' + name)
            pins[name] = version
        self.assertEqual(nhap, self.IMPORT_DA_CAI)
        self.assertEqual(thieu, self.IMPORT_CHUA_CAI)
        self.assertEqual(bac_cau, self.BAC_CAU)
        imports = {name.split('.')[0] for _, _, name in _imports_engine()
                   if name.split('.')[0] not in sys.stdlib_module_names
                   and not (name == TEN_GOI or name.startswith(TEN_GOI + '.')
                            or name == 'kho_tri_thuc.sdk_core'
                            or name.startswith('kho_tri_thuc.sdk_core.'))}
        self.assertEqual(imports, set(nhap) | set(thieu), 'Import chưa khai/khai thừa')
        self.assertEqual(set(pins), set(nhap.values()) | set(bac_cau), 'Pin thiếu/thừa')
        self.assertFalse(set(thieu.values()) & set(pins), 'Không pin gói chưa cài')
        self.assertTrue(set(bac_cau.values()) <= set(pins), 'Dependency cha chưa ghim')
        return pins

    def test_lock_phu_het_import_vendor_lazy_khong_ghim_sdk(self):
        self._kiem_khoa(self.lock)

    def test_pin_khop_metadata_thuc_khong_cai_them(self):
        missing = []
        for name, version in self._kiem_khoa(self.lock).items():
            with self.subTest(goi=name):
                try:
                    installed = metadata.version(name)
                except metadata.PackageNotFoundError:
                    missing.append(name)
                else:
                    self.assertEqual(installed, version, 'Metadata khác mốc lock; không tự nâng gói')
        if missing:
            self.skipTest('CHUA_KIEM metadata thật: thiếu ' + ', '.join(missing) + '; không cài thêm')

    def test_ngoai_le_chua_cai_dung_metadata_thuc(self):
        for name in self.IMPORT_CHUA_CAI.values():
            with self.subTest(goi=name), self.assertRaises(metadata.PackageNotFoundError):
                metadata.version(name)

    def test_bac_cau_co_quan_he_that_trong_metadata(self):
        for name, parent in self.BAC_CAU.items():
            with self.subTest(goi=name, do_goi=parent):
                try:
                    requires = metadata.requires(parent) or []
                except metadata.PackageNotFoundError:
                    self.skipTest('CHUA_KIEM metadata thật: thiếu ' + parent + '; không cài thêm')
                dependencies = {_ten_goi(re.match(r'[\w.-]+', item).group()) for item in requires
                                if 'extra ==' not in item and 'extra==' not in item}
                self.assertIn(name, dependencies)

    def test_lock_sha_nguon_va_vendor_khop_tai_lieu_va_bytes(self):
        rows = re.findall(
            r'^# vendor-sha256: (vendor/mask_ocr/[\w.]+\.py) \| ([a-f0-9]{64}) \| ([a-f0-9]{64})$',
            self.lock, re.MULTILINE)
        nguon = re.findall(
            r'^\| `(vendor/mask_ocr/[^`]+\.py)` \| `([a-f0-9]{64})` \| `([a-f0-9]{64})` \|$',
            (GOI / 'NGUON.md').read_text(encoding='utf-8'), re.MULTILINE)
        self.assertEqual(len(rows), 5)
        self.assertEqual(sorted(rows), sorted(nguon))
        for path, original, bundled in rows:
            with self.subTest(tep=path):
                self.assertEqual(hashlib.sha256((GOI / path).read_bytes()).hexdigest(), bundled)

    def test_ca_am_thieu_thua_pin_gia_va_thieu_ly_do_bi_bat(self):
        variants = {
            'thiếu import PIL': self.lock.replace('# import: PIL | Pillow |', '# bỏ khai báo PIL | Pillow |'),
            'thiếu pin trực tiếp': self.lock.replace('numpy==2.5.3\n', ''),
            'thiếu pin bắc cầu': self.lock.replace('pycparser==3.0\n', ''),
            'gói thừa': self.lock + '\nrequests==2.0.0\n',
            'gói thừa dù ghi lý do': self.lock + '\n# bac-cau: requests | pdfplumber | Lý do không đúng closure.\nrequests==2.0.0\n',
            'pin gói chưa cài': self.lock + '\npymupdf==1.28.2\n',
            'pin SDK candidate': self.lock + '\nkho-tri-thuc-sdk==1.4.1\n',
            'khoảng thay exact pin': self.lock.replace('numpy==2.5.3', 'numpy>=2.5.3'),
            'pin lặp': self.lock + '\nPILLOW==12.3.0\n',
            'ngoại lệ không lý do': re.sub(r'(# chua-cai: defusedxml \| defusedxml \| ).*', r'\1', self.lock),
        }
        for reason, text in variants.items():
            with self.subTest(ca=reason), self.assertRaises(AssertionError):
                self._kiem_khoa(text)
        imports = list(_imports_engine()) + [('vendor/mask_ocr/extraction.py', 1, 'requests')]
        with patch(__name__ + '._imports_engine', return_value=imports), self.assertRaises(AssertionError):
            self._kiem_khoa(self.lock)


class _BangCases:
    def test_import_moi_module_va_parser_cung_vendor_sdk(self):
        before_path, before_bytecode = sys.path[:], sys.dont_write_bytecode
        modules = {name: importlib.import_module(TEN_GOI + '.' + name) for name in (
            'abbyy', 'ban_giao', 'bang', 'chay', 'van_ban', 'lib.cong_ocr',
            'vendor.mask_ocr.common', 'vendor.mask_ocr.extraction',
            'vendor.mask_ocr.layout', 'vendor.mask_ocr.runtime')}
        for module in modules.values():
            self.assertTrue(Path(module.__file__).resolve().is_relative_to(GOI))
        extract_docx, word_layout = bang._nhap_parser_nguon()
        extraction, layout = modules['van_ban']._nhap_parser_nguon()
        self.assertIs(extraction, modules['vendor.mask_ocr.extraction'])
        self.assertIs(layout, modules['vendor.mask_ocr.layout'])
        self.assertIs(extract_docx, extraction.extract_docx)
        self.assertIs(word_layout, layout.word_layout)
        for name in ('bang', 'ban_giao', 'van_ban', 'lib.cong_ocr'):
            self.assertIs(modules[name].DataError, DataError)
        self.assertEqual(sys.path, before_path)
        self.assertEqual(sys.dont_write_bytecode, before_bytecode)

    def test_o_trong_hang_trong_va_van_ban_khong_doi_kieu(self):
        t = read(docx(table([cell('0007') + cell() + cell('1.234,50 VND'), cell() * 3], 3))).bang['bang'][0]
        self.assertEqual((t['so_dong'], len(t['cot']), len(t['o'])), (2, 3, 6))
        self.assertEqual([c['gia_tri']['gia_tri'] for c in t['o']], ['0007', '', '1.234,50 VND', '', '', ''])
        self.assertEqual(t['o'][1]['ma_vung_nguon'], [])
        self.assertTrue(all(c['gia_tri']['kieu'] == 'van_ban' for c in t['o']))

    def test_gop_hinh_chu_nhat_va_o_gop_rong(self):
        rows = [cell('Gộp 2x2', '<w:gridSpan w:val="2"/><w:vMerge w:val="restart"/>') + cell('A'),
                cell('', '<w:gridSpan w:val="2"/><w:vMerge/>') + cell(),
                cell('', '<w:gridSpan w:val="3"/>')]
        t = read(docx(table(rows, 3))).bang['bang'][0]
        self.assertEqual((t['so_dong'], len(t['o'])), (3, 4))
        self.assertEqual([t['o'][0][k] for k in ('dong', 'cot', 'gop_dong', 'gop_cot')], [0, 0, 2, 2])
        self.assertEqual(t['o'][0]['gia_tri']['gia_tri'], 'Gộp 2x2')
        self.assertEqual((t['o'][-1]['gop_cot'], t['o'][-1]['gia_tri']['gia_tri']), (3, ''))

    def test_vi_tri_bang_header_grid_before_va_phan_hoi_doc_lap(self):
        row = '<w:trPr><w:gridBefore w:val="1"/></w:trPr>' + cell('Ánh Dương 06/11/2026')
        tbl = table([row], 2)
        result = read(docx(paragraph('DEMO') + tbl + paragraph('Giữa') + tbl, header=tbl), revision=7)
        self.assertEqual(result.bang['contract'], 'du_lieu_bang.v1')
        self.assertEqual(result.bang['phien_ban'], '1.0.0')
        self.assertEqual(result.bang['revision'], 7)
        self.assertEqual(result.bang['nguon_tep_ids'], [DOCX_ID])
        self.assertEqual(result.bang['phan_hoi_nguon_tep_id'], DETAIL_ID)
        tables = result.bang['bang']
        self.assertEqual(len(tables), 3)
        self.assertEqual(len({t['vi_tri']['dinh_vi'] for t in tables}), 3)
        for t in tables:
            loc = t['vi_tri']['dinh_vi']
            index = int(loc.rsplit('/', 1)[1])
            source = result.phan_hoi_nguon['layout']['blocks'][index]
            self.assertEqual(source['type'], 'table')
            self.assertEqual([c['cot'] for c in t['o']], [1])
            self.assertEqual(t['o'][0]['vi_tri'], {'tep_id': DOCX_ID, 'dinh_vi': loc + '/row/0/col/1'})
            self.assertTrue(t['can_soat'])
            self.assertNotIn('trang', t['vi_tri'])
            self.assertNotIn('bbox', t['o'][0]['vi_tri'])
            source['cells'][0]['col'] = 20
            self.assertEqual(t['o'][0]['cot'], 1)
        json.dumps(result.bang, ensure_ascii=False, allow_nan=False)
        json.dumps(result.phan_hoi_nguon, ensure_ascii=False, allow_nan=False)

    def test_gioi_han_giu_hang_cot_cuoi_va_tu_choi_bang_vuot(self):
        for rows, cols in ((100, 3), (1, 40)):
            with self.subTest(rows=rows, cols=cols):
                t = read(docx(table([cell('DEMO') * cols for _ in range(rows)], cols))).bang['bang'][0]
                self.assertEqual((t['so_dong'], len(t['o'])), (rows, rows * cols))
                self.assertEqual((t['o'][-1]['dong'], t['o'][-1]['cot']), (rows - 1, cols - 1))
        for rows, cols in ((101, 1), (1, 41)):
            with self.subTest(rows=rows, cols=cols), self.assertRaises(DataError) as caught:
                read(docx(table([cell('DEMO') * cols for _ in range(rows)], cols)))
            self.assertEqual(caught.exception.code, 'OCR_BANG_DOCX_INVALID')

    def test_tu_choi_docx_hong_cau_truc_thieu_va_track_changes(self):
        wrapper = '<w:tc><w:sdt><w:sdtContent>' + paragraph('DEMO') + '</w:sdtContent></w:sdt></w:tc>'
        after = '<w:trPr><w:gridAfter w:val="1"/></w:trPr>' + cell('DEMO')
        for raw in (b'DEMO hong', docx(table([wrapper], 1)), docx(table([after], 2)),
                    docx('<w:ins>' + paragraph('DEMO') + '</w:ins>')):
            with self.subTest(raw=raw[:12]), self.assertRaises(DataError) as caught:
                read(raw)
            self.assertEqual(caught.exception.code, 'OCR_BANG_DOCX_INVALID')

    def test_khong_suy_bang_tu_text_va_khong_goi_ocr_anh_nhung(self):
        self.assertEqual(read(docx(paragraph('Mã | Tiền\n0007 | 1.000 VND'))).bang['bang'], [])
        extract_docx, word_layout = bang._nhap_parser_nguon()
        extraction = sys.modules[extract_docx.__module__]
        layout = sys.modules[word_layout.__module__]
        with patch.object(extraction, 'image_text', side_effect=AssertionError('Không OCR ảnh')), \
                patch.object(layout, 'word_layout', wraps=layout.word_layout) as spy:
            result = read(docx(table([cell('DEMO')], 1), image=True))
        self.assertEqual(spy.call_args.kwargs, {'embedded_pages': []})
        self.assertTrue(any('Ảnh nhúng' in w for w in result.phan_hoi_nguon['canh_bao']))


class BangDependencyMockTests(_BangCases, unittest.TestCase):
    def setUp(self):
        # Stdlib XML chỉ cho DOCX DEMO sạch trong ca kiểm, không thay defusedxml
        # của sản phẩm. Patch được khôi phục kể cả khi ca kiểm lỗi.
        xml = ModuleType('defusedxml')
        xml.ElementTree = ElementTree
        self.modules = patch.dict(sys.modules, {'pymupdf': ModuleType('pymupdf'), 'defusedxml': xml})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        for name in list(sys.modules):
            if name == TEN_GOI + '.vendor.mask_ocr' or name.startswith(TEN_GOI + '.vendor.mask_ocr.'):
                sys.modules.pop(name)


class BangDependencyThatTests(_BangCases, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for name in ('pymupdf', 'defusedxml'):
            if importlib.util.find_spec(name) is None:
                raise unittest.SkipTest('CHUA_KIEM dependency thật: thiếu ' + name + '; không cài thêm')
        bang._nhap_parser_nguon()


if __name__ == '__main__':
    unittest.main()
