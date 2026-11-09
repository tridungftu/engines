"""OCR-NOI: PDF DEMO tự viết trong RAM, lớp chữ ẩn trên ảnh nền.

Không cần bộ sinh PDF, font hệ thống hoặc dịch vụ OCR. ToUnicode ánh xạ
trực tiếp chữ Việt; ảnh nền 1 pixel chỉ dùng để chứng minh không OCR lại.
"""

from dataclasses import fields
import importlib.util
import io
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import Mock, patch

from kho_tri_thuc.engines.e_ocr import abbyy, lop_chu


CHU = 'Công ty DEMO Ánh Dương'
TIEN = '1.000.000 VND'
NGAY = '30/10/2026'


def pdf_demo(*pages, rotate=0, text_matrices=None):
    """PDF tối thiểu hợp lệ: Type0 + ToUnicode, ảnh nền và 3 Tr (chữ ẩn)."""
    chars = sorted(set(''.join(text for lines in pages for text in lines)))

    def stream(data, attrs=b''):
        return (b'<< /Length ' + str(len(data)).encode('ascii') + b' ' + attrs
                + b' >>\nstream\n' + data + b'\nendstream')

    mapping = '\n'.join(f'<{ord(c):04X}> <{c.encode("utf-16-be").hex()}>' for c in chars)
    cmap = (f'/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n'
            '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n'
            '/CMapName /DemoUnicode def\n/CMapType 2 def\n'
            '1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n'
            f'{len(chars)} beginbfchar\n{mapping}\nendbfchar\n'
            'endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend').encode('ascii')
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< /Type /Font /Subtype /Type0 /BaseFont /DEMO /Encoding /Identity-H '
               b'/DescendantFonts [4 0 R] /ToUnicode 6 0 R >>',
               b'<< /Type /Font /Subtype /CIDFontType2 /BaseFont /DEMO /DW 600 '
               b'/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> '
               b'/FontDescriptor 5 0 R /CIDToGIDMap /Identity >>',
               b'<< /Type /FontDescriptor /FontName /DEMO /Flags 4 /FontBBox [0 -200 1000 900] '
               b'/ItalicAngle 0 /Ascent 800 /Descent -200 /CapHeight 700 /StemV 80 >>',
               stream(cmap),
               stream(b'FFFFFF>', b'/Type /XObject /Subtype /Image /Width 1 /Height 1 '
                      b'/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /ASCIIHexDecode')]
    page_ids = []
    for lines in pages:
        page_id = len(objects) + 1
        page_ids.append(page_id)
        objects.append((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Rotate {rotate} '
                        '/Resources << /Font << /F1 3 0 R >> /XObject << /Im1 7 0 R >> >> '
                        f'/Contents {page_id + 1} 0 R >>').encode('ascii'))
        content = b'q 595 0 0 842 0 0 cm /Im1 Do Q\nBT /F1 12 Tf 3 Tr\n'
        for index, line in enumerate(lines):
            matrix = (text_matrices or {}).get(index, (1, 0, 0, 1, 50, 750 - 24 * index))
            content += ' '.join(map(str, matrix)).encode('ascii') + b' Tm\n'
            content += b'<' + line.encode('utf-16-be').hex().encode('ascii') + b'> Tj\n'
        objects.append(stream(content + b'ET'))
    kids = ' '.join(f'{number} 0 R' for number in page_ids)
    objects[1] = f'<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>'.encode('ascii')
    raw, offsets = b'%PDF-1.4\n', [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(raw))
        raw += f'{number} 0 obj\n'.encode('ascii') + obj + b'\nendobj\n'
    xref = len(raw)
    raw += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode('ascii')
    raw += b''.join(f'{offset:010d} 00000 n \n'.encode('ascii') for offset in offsets[1:])
    raw += (f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n'
            f'startxref\n{xref}\n%%EOF\n').encode('ascii')
    return raw


class LopChuTests(unittest.TestCase):
    def test_pdf_that_chu_an_giu_chu_viet_tien_ngay_va_vi_tri(self):
        import pdfplumber

        with patch.object(pdfplumber.page.Page, 'to_image', side_effect=AssertionError('Không vẽ ảnh')), \
                patch('socket.socket', side_effect=AssertionError('Không mạng')), \
                patch('subprocess.Popen', side_effect=AssertionError('Không OCR ngoài')):
            result = lop_chu.doc_lop_chu(pdf_demo((CHU, TIEN, NGAY)))
        self.assertIsInstance(result, lop_chu.KetQuaLopChu)
        self.assertEqual([f.name for f in fields(result)], ['text', 'warnings', 'ocr_pages', 'pages'])
        self.assertEqual(result.ocr_pages, 0)
        page = result.pages[0]
        self.assertEqual(page['text'], '\n'.join((CHU, TIEN, NGAY)))
        self.assertEqual(result.text, '[Trang 1]\n' + page['text'])
        self.assertEqual((page['number'], page['width'], page['height']), (1, 595, 842))
        self.assertEqual(page['mode'], 'native')
        self.assertEqual(page['source'], 'ABBYY')
        self.assertEqual([line['text'] for line in page['units']], [CHU, TIEN, NGAY])
        units = {line['id']: line for line in page['units']}
        self.assertEqual([uid for block in page['blocks'] for uid in block['unit_ids']], list(units))
        for block in page['blocks']:
            self.assertEqual(block['type'], 'paragraph')
            self.assertEqual(block['source'], 'ABBYY')
            self.assertTrue(block['bbox'])
        for line in page['units']:
            self.assertEqual(line['source'], 'ABBYY')
            self.assertEqual(' '.join(w['text'] for w in line['parts']), line['text'])
            x0, top, x1, bottom = line['bbox']
            self.assertTrue(0 <= x0 < x1 <= page['width'])
            self.assertTrue(0 <= top < bottom <= page['height'])
            for word in line['parts']:
                self.assertTrue(word['id'].startswith(line['id'] + '-w'))
                self.assertEqual(word['source'], 'ABBYY')
                a, b, c, d = word['bbox']
                self.assertTrue(x0 <= a < c <= x1 and top <= b < d <= bottom)
        self.assertAlmostEqual(page['units'][0]['bbox'][0], 50)
        self.assertAlmostEqual(page['units'][0]['bbox'][1], 82.4)
        json.dumps(result.pages, ensure_ascii=False, allow_nan=False)

    def test_nhieu_trang_khong_trung_dinh_vi_khong_mat_dau(self):
        result = lop_chu.doc_lop_chu(pdf_demo((CHU, TIEN), (NGAY, 'DEMO trang 2')))
        self.assertEqual([p['number'] for p in result.pages], [1, 2])
        self.assertIn('[Trang 2]\n' + NGAY, result.text)
        ids = [item['id'] for p in result.pages for u in p['units'] for item in [u, *u['parts']]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_trang_xoay_giu_thu_tu_chu_tu_va_vi_tri_hien_thi(self):
        for rotation in (90, 180, 270):
            with self.subTest(rotation=rotation):
                result = lop_chu.doc_lop_chu(pdf_demo((CHU, TIEN, NGAY), rotate=rotation))
                page = result.pages[0]
                self.assertEqual(page['text'], '\n'.join((CHU, TIEN, NGAY)))
                self.assertEqual((page['width'], page['height']),
                                 (595, 842) if rotation == 180 else (842, 595))
                for line in page['units']:
                    self.assertEqual(' '.join(w['text'] for w in line['parts']), line['text'])
                    for item in [line, *line['parts']]:
                        x0, top, x1, bottom = item['bbox']
                        self.assertTrue(0 <= x0 < x1 <= page['width'])
                        self.assertTrue(0 <= top < bottom <= page['height'])

    def test_pdf_chi_anh_bao_loi_de_chon_nguon_khac(self):
        with self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(pdf_demo(()))
        self.assertIsInstance(caught.exception, ValueError)
        self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_LOP_CHU')
        self.assertIn('Trang 1 không có lớp chữ', str(caught.exception))

    def test_ma_tran_chu_xoay_khong_tra_thanh_cong_voi_tien_ngay_dao(self):
        import pdfplumber

        for matrix in ((-1, 0, 0, -1, 450, 250), (0, 1, -1, 0, 350, 150)):
            for tron_chu_thang in (False, True):
                with self.subTest(matrix=matrix, tron_chu_thang=tron_chu_thang):
                    lines = (CHU, TIEN + ' ' + NGAY) if tron_chu_thang else (TIEN + ' ' + NGAY,)
                    raw = pdf_demo(lines, text_matrices={len(lines) - 1: matrix})
                    with pdfplumber.open(io.BytesIO(raw)) as pdf:
                        self.assertEqual(pdf.pages[0].rotation, 0)
                        self.assertEqual(pdf.pages[0].chars[-1]['matrix'][:4], matrix[:4])
                        # Xoay 180 độ vẫn được thư viện đánh dấu upright=True.
                        self.assertEqual(pdf.pages[0].chars[-1]['upright'], matrix[0] == -1)
                    with self.assertRaises(lop_chu.LoiLopChu) as caught:
                        lop_chu.doc_lop_chu(raw)
                    self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_LOP_CHU')
                    self.assertIn('Trang 1', str(caught.exception))
                    self.assertIn('chuyển nguồn nhận dạng', str(caught.exception))

    def test_trang_sau_co_chu_xoay_khong_tra_ket_qua_mot_phan(self):
        raw = pdf_demo((CHU,), (CHU, TIEN + ' ' + NGAY),
                       text_matrices={1: (-1, 0, 0, -1, 450, 250)})
        with self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(raw)
        self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_LOP_CHU')
        self.assertIn('Trang 2', str(caught.exception))

    def test_bbox_dong_va_tu_sai_bi_tu_choi(self):
        import pdfplumber

        invalid = [('x0', -1), ('top', -1), ('x1', 596), ('bottom', 843),
                   ('x1', 50), ('bottom', 82),
                   *((key, float('nan')) for key in ('x0', 'top', 'x1', 'bottom'))]
        for target, name in ((pdfplumber.page.Page, 'extract_text_lines'),
                             (pdfplumber.utils, 'extract_words')):
            original = getattr(target, name)
            for key, value in invalid:
                with self.subTest(vi_tri=name, toa_do=key, gia_tri=value):
                    def sai_vi_tri(*args, **kwargs):
                        items = original(*args, **kwargs)
                        items[0][key] = value
                        return items

                    with patch.object(target, name, sai_vi_tri), \
                            self.assertRaises(lop_chu.LoiLopChu) as caught:
                        lop_chu.doc_lop_chu(pdf_demo((TIEN,)))
                    self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_HOP_LE')
                    self.assertIsNone(caught.exception.__context__)

    def test_khong_tra_thanh_cong_mot_phan_khi_trang_sau_chi_anh(self):
        with self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(pdf_demo((CHU,), ()))
        self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_LOP_CHU')
        self.assertIn('Trang 2', str(caught.exception))

    def test_lop_chu_chi_khoang_trang_cung_bi_tu_choi(self):
        with self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(pdf_demo(('   ',)))
        self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_LOP_CHU')

    def test_import_luoi_thieu_pdfplumber_khong_lam_hong_import_engine(self):
        name = lop_chu.__package__ + '._kiem_import_luoi'
        spec = importlib.util.spec_from_file_location(name, Path(lop_chu.__file__))
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'pdfplumber': None, name: module,
                                     lop_chu.__package__ + '.vendor.mask_ocr': None}):
            spec.loader.exec_module(module)
            with self.assertRaises(module.LoiLopChu) as caught:
                module.doc_lop_chu(pdf_demo((CHU,)))
        self.assertEqual(caught.exception.ma, 'OCR_LOP_CHU_THIEU_THU_VIEN')
        self.assertIn('cần kiểm tra môi trường xử lý', str(caught.exception))
        self.assertNotIn('pdfplumber', str(caught.exception))
        self.assertIsNone(caught.exception.__context__)

    def test_pdf_hong_tra_loi_tieng_viet_khong_lo_exception_nguon(self):
        for raw in (b'%PDF-1.4\nDEMO hong', b'Khong phai PDF'):
            with self.subTest(raw=raw), self.assertRaises(lop_chu.LoiLopChu) as caught:
                lop_chu.doc_lop_chu(raw)
            self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_HOP_LE')
            self.assertIn('Không đọc được PDF', str(caught.exception))
            self.assertIsNone(caught.exception.__context__)

    def test_dau_vao_chi_nhan_bytes_trong_ram(self):
        for raw in (None, '', b'', 'DEMO.pdf', bytearray(b'%PDF')):
            with self.subTest(raw=raw), self.assertRaises(lop_chu.LoiLopChu) as caught:
                lop_chu.doc_lop_chu(raw)
            self.assertEqual(caught.exception.ma, 'OCR_PDF_DAU_VAO')

    def test_gioi_han_kich_thuoc_so_trang_va_so_chu(self):
        raw = pdf_demo((CHU,), (NGAY,))
        for ten, limit in (('MAX_BYTES', 10), ('MAX_PAGES', 1), ('MAX_TEXT', 10)):
            with self.subTest(ten=ten), patch.object(lop_chu, ten, limit), \
                    self.assertRaises(lop_chu.LoiLopChu) as caught:
                lop_chu.doc_lop_chu(raw)
            self.assertEqual(caught.exception.ma, 'OCR_PDF_GIOI_HAN')

    def test_huy_truoc_khi_doc_va_sau_khi_doc_trang(self):
        import pdfplumber

        huy = threading.Event()
        huy.set()
        with patch.object(pdfplumber, 'open') as mo, self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(pdf_demo((CHU,)), huy=huy)
        self.assertEqual(caught.exception.ma, 'OCR_HUY')
        mo.assert_not_called()
        huy.clear()
        original = pdfplumber.page.Page.extract_text_lines

        def doc_roi_huy(page, **kwargs):
            result = original(page, **kwargs)
            huy.set()
            return result

        with patch.object(pdfplumber.page.Page, 'extract_text_lines', doc_roi_huy), \
                self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(pdf_demo((CHU,)), huy=huy)
        self.assertEqual(caught.exception.ma, 'OCR_HUY')

    def _backend(self, *, acl=True):
        def sid(rid):
            return f'S-1-5-21-111-222-333-{rid}'

        cfg = abbyy.CauHinhABBYY(sid(4), sid(1), sid(2), (sid(3),), 4, 1)
        identity = abbyy.DanhTinhWindows(sid(4), 4, True, True)
        cong = Mock(spec=abbyy.CongOCR)
        backend = abbyy.BackendABBYY(cau_hinh=cfg, cong_ocr=cong,
                                     kiem_phien=lambda: (identity, identity),
                                     kiem_acl=lambda *_: acl)
        return backend, cong

    def test_adapter_abbyy_doc_pdf_khong_gui_ocr_lan_hai(self):
        backend, cong = self._backend()
        result = backend.doc_lop_chu(pdf_demo((CHU, TIEN, NGAY)))
        self.assertEqual(result.pages[0]['source'], 'ABBYY')
        self.assertIn(CHU, result.text)
        cong.ocr.assert_not_called()

    def test_adapter_abbyy_kiem_quyen_truoc_khi_doc(self):
        backend, cong = self._backend(acl=False)
        with patch.object(lop_chu, 'doc_lop_chu') as doc, self.assertRaises(abbyy.LoiABBYY):
            backend.doc_lop_chu(pdf_demo((CHU,)))
        doc.assert_not_called()
        cong.ocr.assert_not_called()


if __name__ == '__main__':
    unittest.main()
