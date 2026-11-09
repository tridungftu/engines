"""OCR-MAY-1: bài máy mức engine, cầu ABBYY GIẢ, không mạng/Core/PG.

Các ca dùng seam giả chỉ chứng minh engine định tuyến/đọc/cắt đúng.
Ca Tesseract thật chỉ chạy khi đủ dependency và model trong gói; không
thay bằng OCR giả rồi báo đã đo. Nhật ký JSONL là bằng chứng của bài máy,
không phải kiểm nhật ký hàng chờ/màn quản trị Core.
"""

from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import io
import json
import logging
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

import pdfplumber
from PIL import Image, ImageChops

from kho_tri_thuc.engines.e_ocr import chay, chon_nguon, lop_chu, vung
from kho_tri_thuc.engines.e_ocr.lib.cong_ocr import CongOCR
from kho_tri_thuc.engines.e_ocr.tests.demo.tao_bo_demo import tao_bo_demo
from kho_tri_thuc.sdk_core.primitives import DataError


GOI = Path(__file__).resolve().parents[1]
GIO_VIET_NAM = timezone(timedelta(hours=7))


class CauABBYYGia:
    """Transport PDF chỉ đọc fixture DEMO, không gửi Hot Folder hay tính trang."""

    def __init__(self, bo):
        self.bat, self.het_han_muc = True, False
        self.loi_ket_noi = False
        self.so_lan_kiem, self.luot_gui = 0, []
        self.ket_qua = {
            hashlib.sha256(path.read_bytes()).hexdigest(): result.read_bytes()
            for path, result in ((bo.pdf_quet, bo.pdf_abbyy_gia),
                                 (bo.anh_png, bo.pdf_abbyy_anh),
                                 (bo.anh_jpeg, bo.pdf_abbyy_anh))
        }

    def san_sang(self):
        self.so_lan_kiem += 1
        if self.loi_ket_noi:
            raise ConnectionError(r'DEMO D:\DEMO\duong-dan-khong-duoc-lo, khoa=DEMO-KIN')
        return self.bat

    def doc_pdf(self, raw, duoi, *, huy=None):
        self.luot_gui.append(duoi)
        if not self.bat:
            raise ConnectionError('Cầu nối DEMO đang tắt.')
        if self.het_han_muc:
            raise DataError('OCR_HET_HAN_MUC', 'DEMO — Đã hết hạn mức nhận dạng.')
        return self.ket_qua[hashlib.sha256(raw).hexdigest()]


class OcrMayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bat_dau_bo = time.perf_counter()
        # Giữ tệp tạm; không TemporaryDirectory/cleanup/xóa theo quy định lát.
        cls.root = Path(tempfile.mkdtemp(prefix='ktt-ocr-may-demo-'))
        cls.bo = tao_bo_demo(cls.root / 'DEMO')
        cls.dap_an = json.loads(cls.bo.dap_an.read_text(encoding='utf-8'))
        cls.nhat_ky = cls.root / 'OCR-MAY-1.jsonl'
        cls.nhat_ky.write_text('', encoding='utf-8')
        cls.dong_ky = []

    @classmethod
    def tearDownClass(cls):
        print(f'OCR-MAY-1: tong_giay={time.perf_counter() - cls.bat_dau_bo:.3f}; '
              f'so_ban_ghi={len(cls.dong_ky)}; chi_du_lieu_DEMO; khong_mang', flush=True)

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name in ('socket.socket', 'socket.create_connection', 'subprocess.Popen'):
            self.stack.enter_context(patch(name, side_effect=AssertionError('Bài máy không được mở kết nối/tiến trình.')))
        self.stack.enter_context(patch('kho_tri_thuc.engines.e_ocr.lib.cong_ocr._xoa'))
        self.luc = datetime.now(GIO_VIET_NAM).strftime('%d/%m/%Y %H:%M:%S%z')
        self.bat_dau = time.perf_counter()
        self.nguon, self.ghi_chu = 'khong_ap_dung', None
        self.ket_luan, self.so_do = 'DA_KIEM_ENGINE_GIA', None
        self.ca = int(self._testMethodName.split('_')[2])
        self.tmp = self.root / self._testMethodName
        self.tmp.mkdir()
        self.cong = CongOCR(self.tmp / 'hot-folder-DEMO', tep_so_trang=self.tmp / 'so-DEMO.json',
                           thu_muc_dem=self.tmp / 'dem-DEMO', nghi=0.01)
        self.abbyy = CauABBYYGia(self.bo)
        self.mask = Mock(side_effect=self._mask_gia)
        self.chon = chon_nguon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=self.cong, mask_ocr=self.mask)

    def _dong_nhat_ky(self):
        return dict(ca=self.ca, bai_test=self._testMethodName, luc=self.luc,
                    cho_giay=None, chay_giay=round(time.perf_counter() - self.bat_dau, 6),
                    nguon_doc=self.nguon, ket_qua=self.ket_luan, ghi_chu=self.ghi_chu, so_do=self.so_do)

    def tearDown(self):
        result = self._outcome.result
        if any(test is self or getattr(test, 'test_case', None) is self for test, _ in result.failures):
            self.ket_luan = 'FAIL'
        if any(test is self or getattr(test, 'test_case', None) is self for test, _ in result.errors):
            self.ket_luan = 'ERROR'
        row = self._dong_nhat_ky()
        self.dong_ky.append(row)
        text = json.dumps(row, ensure_ascii=False, allow_nan=False)
        with self.nhat_ky.open('a', encoding='utf-8') as stream:
            stream.write(text + '\n')
        print('OCR-MAY ' + text, flush=True)

    def _chua_kiem(self, reason):
        self.ket_luan, self.ghi_chu = 'CHUA_KIEM', reason
        self.skipTest('CHUA_KIEM: ' + reason)

    def _so_trang(self):
        return sum(row[1] for row in self.cong._doc_so())

    def _mask_gia(self, raw, duoi, *, huy=None):
        n = 3 if duoi == 'pdf' else 1
        pages = [dict(number=p['so_trang'], text='\n'.join(p['dong']), source='mask_ocr')
                 for p in self.dap_an['trang'][:n]]
        return lop_chu.KetQuaLopChu('\n\n'.join(p['text'] for p in pages), [], n, pages)

    def _doc(self, path, *, chon=None, huy=None):
        result = chay.xu_ly_tai_lieu(path.read_bytes(), path.suffix, chon_nguon=chon or self.chon, huy=huy)
        self.nguon, self.ghi_chu = result.nguon_doc, result.ly_do_chuyen
        return result

    def _kiem_truong(self, result):
        for page in result.pages:
            for text in self.dap_an['truong'].values():
                self.assertIn(text, page['text'])

    def test_ca_01_quan_ly_engine(self):
        self._chua_kiem('Cần màn Quản lý engine của Core; chưa xác nhận ABBYY thật hoặc phiên bản trên màn.')

    def test_ca_02_abbyy_pdf_co_chu_vi_tri_tien_ngay(self):
        result = self._doc(self.bo.pdf_quet)
        self.assertEqual(result.nguon_doc, 'ABBYY')
        self.assertIsNone(result.ly_do_chuyen)
        self.assertEqual(result.ocr_pages, 0)
        self.assertEqual([p['number'] for p in result.pages], [1, 2, 3])
        self._kiem_truong(result)
        for page, answer in zip(result.pages, self.dap_an['trang']):
            self.assertEqual(page['text'], '\n'.join(answer['dong']))
            self.assertEqual(page['source'], 'ABBYY')
            for unit in page['units']:
                x0, y0, x1, y1 = unit['bbox']
                self.assertTrue(0 <= x0 < x1 <= page['width'])
                self.assertTrue(0 <= y0 < y1 <= page['height'])
                self.assertTrue(unit['parts'])
                for part in unit['parts']:
                    a, b, c, d = part['bbox']
                    self.assertTrue(x0 <= a < c <= x1 and y0 <= b < d <= y1)
                    self.assertEqual(part['source'], 'ABBYY')
        self.assertEqual(self.abbyy.luot_gui, ['pdf'])
        self.mask.assert_not_called()
        self.assertEqual(self._so_trang(), 3)
        self.ghi_chu = 'Cầu ABBYY giả; Word/bảng đầu ra chưa kiểm qua đường PDF lớp chữ.'

    def test_ca_02_word_va_bang_dau_ra(self):
        self._chua_kiem('Đường PDF lớp chữ chưa xuất Word/ô bảng; Word trong bộ DEMO chỉ là đáp án.')

    def test_ca_03_hai_anh_lien_tiep_muc_engine(self):
        for path in (self.bo.anh_png, self.bo.anh_jpeg):
            result = self._doc(path)
            self.assertEqual(result.nguon_doc, 'ABBYY')
            self.assertEqual(len(result.pages), 1)
            self._kiem_truong(result)
        self.assertEqual(self.abbyy.luot_gui, ['png', 'jpg'])
        self.assertEqual(self._so_trang(), 2)
        self.mask.assert_not_called()
        self.ghi_chu = 'Đã đọc lần lượt PNG/JPEG; thứ tự và chống trùng hàng chờ Core chưa kiểm.'

    def test_ca_03_chong_gui_trung_hang_cho(self):
        self._chua_kiem('Engine không có hàng chờ/chống gửi trùng; cần hàng chờ Core để gửi trùng và kiểm thứ tự.')

    def test_ca_04_het_han_muc_dinh_tuyen_gia(self):
        self.cong.tep_so_trang.write_text(json.dumps([[time.time(), 5000]]), encoding='utf-8')
        result = self._doc(self.bo.pdf_quet)
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'het_han_muc'))
        self.assertIn('5.000', result.ly_do_chuyen)
        self.assertEqual(self.abbyy.luot_gui, [])
        self.assertEqual(self._so_trang(), 5000)
        self.mask.assert_called_once_with(self.bo.pdf_quet.read_bytes(), 'pdf', huy=None)
        self.ghi_chu = 'Định tuyến bằng seam giả; không dùng chữ giả làm số đo chất lượng OCR.'

    def test_ca_04_cau_gia_bao_het_han_muc_hoan_trang(self):
        self.abbyy.het_han_muc = True
        result = self._doc(self.bo.pdf_quet)
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'het_han_muc'))
        self.assertEqual(self.abbyy.luot_gui, ['pdf'])
        self.assertEqual(self._so_trang(), 0)
        self.mask.assert_called_once()

    def test_ca_04_tesseract_that_va_so_do_dap_an(self):
        missing = [name for name in ('pymupdf', 'defusedxml') if importlib.util.find_spec(name) is None]
        if missing:
            self._chua_kiem('Thiếu dependency nhận dạng thật: ' + ', '.join(missing) + '; không cài thêm.')
        from kho_tri_thuc.engines.e_ocr.vendor.mask_ocr import runtime

        # Cấu hình DEMO trong RAM: tuyệt đối không đọc settings/config thật.
        cfg = {'tesseract_language': 'vie+eng'}
        info = runtime.tesseract_info(cfg)
        if not info['ready']:
            self._chua_kiem('Thiếu model Tesseract vie+eng trong gói; CLI bên ngoài không chứng minh engine sẵn sàng.')
        self.stack.enter_context(patch.object(runtime, 'settings', return_value=cfg))
        self.cong.tep_so_trang.write_text(json.dumps([[time.time(), 5000]]), encoding='utf-8')
        chon = chon_nguon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=self.cong)
        result = self._doc(self.bo.pdf_quet, chon=chon)
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'het_han_muc'))
        self.assertEqual(len(result.pages), 3)
        self.assertTrue(all(p['source'] == 'mask_ocr' and p['text'].strip() for p in result.pages))
        self.assertEqual(result.ocr_pages, 3)
        detail = [dict(trang=p['number'], **{key: value in p['text']
                  for key, value in self.dap_an['truong'].items()}) for p in result.pages]
        dung = sum(row[key] for row in detail for key in self.dap_an['truong'])
        self.so_do = dict(don_vi='Trường khớp nguyên văn theo từng trang', tong=9, dung=dung, sai=9 - dung,
                          chi_tiet=detail)
        self.ket_luan = 'DA_DO_CHUA_CHOT_NGUONG'
        self.ghi_chu = 'Đã đo OCR thật; ngưỡng chất lượng chờ chốt sau lần đo đầu.'
        self.assertEqual(self.abbyy.luot_gui, [])
        self.assertEqual(self._so_trang(), 5000)

    def test_ca_05_tat_cau_noi_chuyen_mask_co_ly_do(self):
        self.abbyy.bat = False
        result = self._doc(self.bo.anh_png)
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'khong_ket_noi'))
        self.assertEqual(result.ly_do_chuyen, 'Không kết nối được máy ABBYY.')
        self.assertEqual(self.abbyy.luot_gui, [])
        self.assertEqual(self._so_trang(), 0)
        self.mask.assert_called_once_with(self.bo.anh_png.read_bytes(), 'png', huy=None)
        self.ghi_chu = result.ly_do_chuyen + ' Đã kiểm định tuyến; bộ đọc dự phòng giả.'

    def test_ca_06_trich_dung_vung_co_chu_va_co_nghi_ngo(self):
        raw = self.bo.anh_vung.read_bytes()
        answer = self.dap_an['vung']
        ref = dict(contract='tham_chieu_tep.v1', phien_ban='1.0.0',
                   tep_id='10000000-0000-4000-8000-000000000001', ten_tep='DEMO-vung.png',
                   mime='image/png', kich_thuoc=len(raw), sha256=hashlib.sha256(raw).hexdigest(), het_han_luc=None)
        request = dict(contract='vung_anh.v1', phien_ban='1.0.0', tham_chieu_tep=ref,
                       bon_diem=deepcopy(answer['bon_diem']))

        def doc_anh_cat(png):
            self.assertNotEqual(png, raw)
            with Image.open(io.BytesIO(png)) as crop, Image.open(self.bo.anh_da_cat) as expected:
                self.assertEqual(list(crop.size), answer['kich_thuoc_cat'])
                self.assertIsNone(ImageChops.difference(crop, expected).getbbox())
            return answer['van_ban']

        read = Mock(side_effect=doc_anh_cat)
        result = chay.xu_ly_function(vung.CAPABILITY, raw, request, image_text=read)
        read.assert_called_once()
        self.assertEqual(result['van_ban'], answer['van_ban'])
        self.assertEqual(result['bon_diem'], answer['bon_diem'])
        self.assertEqual(result['nguon_doc'], 'mask_ocr_tesseract')
        self.assertTrue(result['nghi_ngo'])
        self.assertFalse(result['vung_rong'])
        self.assertIsNone(result['do_tin_cay'])
        self.assertIn('chua_co_do_tin_cay', result['ly_do_nghi_ngo'])
        self.nguon = result['nguon_doc']
        self.ghi_chu = 'Cắt ảnh thật, kiểm pixel với ảnh cắt đáp án; nhận dạng vùng giả.'

    def test_ca_07_qua_co_qua_trang_hong_khong_tru_han_muc(self):
        self.cong.tep_so_trang.write_text(json.dumps([[time.time(), 17]]), encoding='utf-8')
        before = self.cong._doc_so()
        for path, code, text in ((self.bo.tep_qua_co, 'OCR_KICH_THUOC', '20 MiB'),
                                 (self.bo.pdf_61_trang, 'OCR_TAI_LIEU', '60 trang'),
                                 (self.bo.tep_hong, 'OCR_TAI_LIEU', 'Không đọc được tài liệu')):
            with self.subTest(tep=path.name):
                with self.assertRaises(DataError) as caught:
                    self._doc(path)
                self.assertEqual(caught.exception.code, code)
                self.assertIn(text, str(caught.exception))
                self.assertNotIn(str(self.root), str(caught.exception))
                self.assertEqual(self.cong._doc_so(), before)
        self.assertEqual(self.abbyy.so_lan_kiem, 0)
        self.assertEqual(self.abbyy.luot_gui, [])
        self.mask.assert_not_called()
        self.ghi_chu = 'Cả ba tệp bị từ chối trước khi kiểm cầu nối, nhận dạng hoặc trừ hạn mức.'

    def test_ca_07_huy_truoc_khi_engine_nhan_dang(self):
        huy = threading.Event()
        huy.set()
        with self.assertRaises(DataError) as caught:
            self._doc(self.bo.pdf_quet, huy=huy)
        self.assertEqual(caught.exception.code, 'OCR_HUY')
        self.assertIn('Đã hủy', str(caught.exception))
        self.assertEqual(self._so_trang(), 0)
        self.assertEqual(self.abbyy.so_lan_kiem, 0)
        self.assertEqual(self.abbyy.luot_gui, [])
        self.mask.assert_not_called()
        self.ghi_chu = 'Đã kiểm tín hiệu hủy trước nhận dạng; chưa phải hủy việc trong hàng chờ Core.'

    def test_ca_07_huy_viec_dang_cho_core(self):
        self._chua_kiem('Cần hàng chờ Core để hủy một việc đang chờ; engine chỉ nhận tín hiệu hủy.')

    def test_ca_08_bao_ve_cau_noi_that(self):
        self._chua_kiem('Cần cầu nối ABBYY thật, màn Core và quyền mở kết nối; lát này không gọi mạng.')

    def test_ca_09_nhat_ky_thoi_gian_nguon_khong_lo_duong_dan(self):
        self.abbyy.loi_ket_noi = True
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger('kho_tri_thuc.engines.e_ocr')
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        self.addCleanup(logger.setLevel, old_level)
        logger.addHandler(handler)
        self.addCleanup(logger.removeHandler, handler)
        result = self._doc(self.bo.anh_jpeg)
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'khong_ket_noi'))
        rows = [json.loads(line) for line in self.nhat_ky.read_text(encoding='utf-8').splitlines()]
        self.assertEqual(rows, self.dong_ky)
        # Chạy riêng ca 9 cũng hợp lệ: không phụ thuộc ca khác đã chạy trước.
        rows.append(self._dong_nhat_ky())
        for row in rows:
            self.assertIn(row['ca'], range(1, 10))
            datetime.strptime(row['luc'], '%d/%m/%Y %H:%M:%S%z')
            self.assertGreaterEqual(row['chay_giay'], 0)
            self.assertIsNone(row['cho_giay'], 'Engine không có hàng chờ; không tự đặt thời gian chờ bằng 0.')
            self.assertIn(row['nguon_doc'], ('ABBYY', 'mask_ocr', 'mask_ocr_tesseract', 'khong_ap_dung'))
        text = json.dumps(rows, ensure_ascii=False) + stream.getvalue() + repr(result.du_lieu())
        for forbidden in (str(self.root), 'D:\\DEMO', 'DEMO-KIN', 'duong-dan-khong-duoc-lo'):
            self.assertNotIn(forbidden, text)
        self.ghi_chu = 'Nhật ký bài máy có ngày giờ, thời gian chạy, nguồn; thời gian chờ cần Core.'


class BoDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bo = tao_bo_demo(Path(tempfile.mkdtemp(prefix='ktt-ocr-may-fixture-')))
        cls.answer = json.loads(cls.bo.dap_an.read_text(encoding='utf-8'))

    def test_pdf_quet_chi_anh_va_ban_gia_cung_anh_co_lop_chu(self):
        with pdfplumber.open(self.bo.pdf_quet) as scan, pdfplumber.open(self.bo.pdf_abbyy_gia) as text_pdf:
            self.assertEqual((len(scan.pages), len(text_pdf.pages)), (3, 3))
            for number, (page, text_page) in enumerate(zip(scan.pages, text_pdf.pages), 1):
                self.assertEqual(page.chars, [])
                self.assertEqual(page.extract_text(), '')
                self.assertEqual(len(page.images), 1)
                self.assertEqual((page.images[0]['srcsize']), (1240, 1754))
                self.assertEqual(page.images[0]['stream'].get_rawdata(), text_page.images[0]['stream'].get_rawdata())
                self.assertTrue(text_page.chars)
                self.assertIn(f'Trang {number}', text_page.extract_text())
                for field in self.answer['truong'].values():
                    self.assertIn(field, text_page.extract_text())
        with self.assertRaises(lop_chu.LoiLopChu) as caught:
            lop_chu.doc_lop_chu(self.bo.pdf_quet.read_bytes())
        self.assertEqual(caught.exception.ma, 'OCR_PDF_KHONG_LOP_CHU')

    def test_anh_bang_o_trong_o_gop_va_cac_tep_bien(self):
        for path, fmt in ((self.bo.anh_png, 'PNG'), (self.bo.anh_jpeg, 'JPEG')):
            with Image.open(path) as image:
                self.assertEqual(image.format, fmt)
                self.assertEqual(image.size, (1240, 1754))
                self.assertEqual(getattr(image, 'n_frames', 1), 1)
                image.verify()
        with Image.open(self.bo.anh_png) as image:
            # Vạch cột chỉ bắt đầu dưới hàng gộp; ô trống không chứa chữ.
            self.assertEqual(image.getpixel((430, 580)), (255, 255, 255))
            self.assertEqual(image.getpixel((430, 650)), (0, 0, 0))
            self.assertEqual(image.crop((836, 686, 1134, 764)).getextrema(), ((255, 255),) * 3)
        with pdfplumber.open(self.bo.pdf_61_trang) as pdf:
            self.assertEqual(len(pdf.pages), 61)
        self.assertEqual(self.bo.tep_qua_co.stat().st_size, 20 * 1024**2 + 1)
        self.assertEqual(self.answer['nhan'], 'DEMO — HỒ SƠ HOÀN TOÀN GIẢ')
        self.assertEqual(self.answer['truong'], dict(cong_ty='Công ty DEMO Ánh Dương',
                                                   so_tien='1.000.000 VND', ngay='30/10/2026'))
        self.assertEqual(self.answer['bang']['o_trong'], [[2, 2]])
        self.assertEqual(self.answer['bang']['o_gop'], [dict(hang=0, cot=0, so_cot=3, so_hang=1)])

    def test_word_dap_an_tuy_thu_vien_san_co(self):
        if self.bo.word_dap_an is None:
            self.assertFalse(self.answer['word']['da_tao'])
            self.assertIn('python-docx', self.answer['word']['ghi_chu'])
            self.skipTest('CHUA_KIEM Word đáp án: chưa có python-docx; đã có JSON.')
        from docx import Document

        document = Document(self.bo.word_dap_an)
        self.assertEqual(len(document.tables), 3)
        self.assertIn('KHÔNG PHẢI KẾT QUẢ NHẬN DẠNG', document.paragraphs[0].text)
        for table in document.tables:
            self.assertEqual((len(table.rows), len(table.columns)), (4, 3))
            self.assertEqual(table.cell(2, 2).text, '')
            self.assertEqual(table.cell(2, 1).text, self.answer['truong']['so_tien'])
            self.assertEqual(table.cell(3, 1).text, self.answer['truong']['ngay'])
            self.assertEqual(table.cell(0, 0)._tc.grid_span, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
