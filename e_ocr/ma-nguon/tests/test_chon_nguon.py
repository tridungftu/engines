"""OCR-CHON: dữ liệu DEMO, sổ tạm và backend giả; không gọi ABBYY thật."""

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import io
import json
import math
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from kho_tri_thuc.engines.e_ocr import abbyy, chay, chon_nguon as chon
from kho_tri_thuc.engines.e_ocr.ket_noi_abbyy import KetNoiABBYY, LoiKetNoiABBYY
from kho_tri_thuc.engines.e_ocr.lib import cong_ocr as ocr
from kho_tri_thuc.engines.e_ocr.lib.cong_ocr import CongOCR
from kho_tri_thuc.engines.e_ocr.lop_chu import KetQuaLopChu, LoiLopChu
from kho_tri_thuc.engines.e_ocr.tests.test_lop_chu import pdf_demo
from kho_tri_thuc.sdk_core.primitives import DataError


LUC = datetime(2026, 11, 7, 12, tzinfo=timezone.utc).timestamp()
CHU = 'Công ty DEMO Ánh Dương\n1.000.000 VND\n07/11/2026'


def ket_qua(n=1):
    return KetQuaLopChu(CHU, [], n, [dict(number=i, text=CHU, source='mask_ocr') for i in range(1, n + 1)])


class ChonNguonTests(unittest.TestCase):
    def setUp(self):
        # Giữ tệp tạm theo quy định không xóa; không ghi dữ liệu vào repo.
        self.tmp = Path(tempfile.mkdtemp(prefix='ktt-ocr-chon-demo-'))
        self.clock = patch('kho_tri_thuc.engines.e_ocr.lib.cong_ocr.time.time', return_value=LUC)
        self.now = self.clock.start()
        self.addCleanup(self.clock.stop)
        self.no_delete = patch('kho_tri_thuc.engines.e_ocr.lib.cong_ocr._xoa')
        self.no_delete.start()
        self.addCleanup(self.no_delete.stop)
        self.cong = self.tao_cong()
        self.raw = pdf_demo(('DEMO nguồn scan',))
        self.pdf = pdf_demo(tuple(CHU.splitlines()))
        self.abbyy = Mock(san_sang=Mock(return_value=True), doc_pdf=Mock(return_value=self.pdf))
        self.mask = Mock(return_value=ket_qua())
        self.chon = chon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=self.cong, mask_ocr=self.mask)

    def tao_cong(self):
        return CongOCR(self.tmp / 'hot-folder-DEMO', tep_so_trang=self.tmp / 'so_trang.json',
                       thu_muc_dem=self.tmp / 'dem-DEMO', nghi=0.01)

    def ghi_so(self, rows):
        self.cong.tep_so_trang.write_text(json.dumps(rows), encoding='utf-8')

    def so_trang(self):
        return sum(x[1] for x in self.cong._doc_so())

    def test_abbyy_truoc_doc_lop_chu_that_va_dem_dung_so_trang_gui(self):
        raw = pdf_demo(('DEMO trang 1',), ('DEMO trang 2',))
        self.abbyy.doc_pdf.return_value = pdf_demo(('DEMO trang 1',), ('DEMO trang 2',))
        result = chay.xu_ly_tai_lieu(raw, 'pdf', chon_nguon=self.chon)
        self.assertEqual(result.nguon_doc, 'ABBYY')
        self.assertIsNone(result.ma_ly_do_chuyen)
        self.assertIsNone(result.ly_do_chuyen)
        self.assertEqual(result.ocr_pages, 0)
        self.assertEqual(len(result.pages), 2)
        self.assertEqual(result.pages[1]['source'], 'ABBYY')
        self.abbyy.doc_pdf.assert_called_once_with(raw, 'pdf', huy=None)
        self.mask.assert_not_called()
        self.assertEqual(self.so_trang(), 2)

    def test_het_han_muc_khong_goi_abbyy_va_dung_nguon_goc(self):
        self.ghi_so([[LUC - 1, 5000]])
        result = self.chon.doc(self.raw, '.PDF')
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'het_han_muc'))
        self.assertIn('5.000', result.ly_do_chuyen)
        self.abbyy.doc_pdf.assert_not_called()
        self.mask.assert_called_once_with(self.raw, 'pdf', huy=None)
        self.assertEqual(self.so_trang(), 5000)

    def test_backend_seam_cu_chay_duoc_khong_can_tham_so_tran(self):
        gui = Mock(return_value=self.pdf)

        class BackendSeamCu:
            def san_sang(self):
                return True

            def doc_pdf(self, raw, duoi, *, huy=None):
                return gui(raw, duoi, huy=huy)

        selector = chon.ChonNguonOCR(abbyy=BackendSeamCu(), cong_ocr=self.cong, mask_ocr=self.mask)
        huy = threading.Event()
        result = selector.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual(result.nguon_doc, 'ABBYY')
        self.assertIsNone(result.trang_thai_abbyy)
        self.assertEqual(selector.trang_thai()['luot_chua_ro'], [])
        gui.assert_called_once_with(self.raw, 'pdf', huy=huy)
        self.mask.assert_not_called()
        self.assertEqual(self.so_trang(), 1)

    def test_loi_chuan_bi_backend_truoc_goi_hoan_trang_khong_danh_dau_chua_ro(self):
        gui = Mock(return_value=self.pdf)

        class BackendLoiChuanBi:
            loi = None

            def san_sang(self):
                return True

            @property
            def doc_pdf(self):
                if self.loi is not None:
                    raise self.loi
                return gui

        backend = BackendLoiChuanBi()
        selector = chon.ChonNguonOCR(abbyy=backend, cong_ocr=self.cong, mask_ocr=self.mask)
        nen = [[LUC - 1, 37]]
        self.ghi_so(nen)
        for exc in (TypeError('DEMO sai tham số'), RuntimeError('DEMO lỗi dựng backend')):
            with self.subTest(loi=type(exc).__name__):
                backend.loi = exc
                with patch.object(self.cong, '_hoan_trang', wraps=self.cong._hoan_trang) as hoan:
                    result = selector.doc(self.raw, 'pdf')
                hoan.assert_called_once()
                self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen),
                                 ('mask_ocr', 'loi_nhan_dang'))
                self.assertIsNone(result.trang_thai_abbyy)
                self.assertEqual(selector.trang_thai()['luot_chua_ro'], [])
                self.assertEqual(self.cong._doc_so(), nen)
                self.assertEqual(self.cong._giu_cho, {})
                gui.assert_not_called()
        backend.loi = None
        self.assertEqual(selector.doc(self.raw, 'pdf').nguon_doc, 'ABBYY')
        gui.assert_called_once_with(self.raw, 'pdf', huy=None)
        self.assertEqual(self.so_trang(), 38)

    def test_khong_du_cho_ca_tai_lieu_chuyen_toan_bo(self):
        self.ghi_so([[LUC, 4999]])
        self.mask.return_value = ket_qua(2)
        result = self.chon.doc(pdf_demo(('DEMO 1',), ('DEMO 2',)), 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'het_han_muc')
        self.abbyy.doc_pdf.assert_not_called()
        self.assertEqual(self.so_trang(), 4999)

    def test_may_tat_false_hoac_khong_ket_noi_deu_chuyen(self):
        for ready in (False, ConnectionError('DEMO đường dẫn/khóa không được lộ')):
            with self.subTest(ready=type(ready).__name__):
                self.abbyy.san_sang.side_effect = ready if isinstance(ready, Exception) else None
                self.abbyy.san_sang.return_value = ready
                result = self.chon.doc(self.raw, 'pdf')
                self.assertEqual(result.ma_ly_do_chuyen, 'khong_ket_noi')
                self.assertEqual(self.so_trang(), 0)
        self.abbyy.doc_pdf.assert_not_called()

    def test_loi_xac_dinh_truoc_nhan_khong_tru_trang(self):
        for exc, reason in (
            (LoiKetNoiABBYY('ABBYY_KHONG_KET_NOI'), 'khong_ket_noi'),
            (LoiKetNoiABBYY('OCR_QUA_GIO'), 'qua_thoi_gian'),
            (LoiKetNoiABBYY('ABBYY_CHUNG_THU'), 'loi_nhan_dang'),
            (DataError('OCR_KHONG_NHAN', 'DEMO bí mật'), 'khong_ket_noi'),
            (LoiKetNoiABBYY('ABBYY_KHOA_HOAC_IP'), 'loi_nhan_dang'),
        ):
            with self.subTest(reason=reason):
                self.abbyy.doc_pdf.side_effect = exc
                result = self.chon.doc(self.raw, 'pdf')
                self.assertEqual(result.ma_ly_do_chuyen, reason)
                self.assertEqual(self.so_trang(), 0)
                self.assertNotIn('bí mật', repr(result.du_lieu()))

    def test_pdf_thieu_lop_chu_chuyen_nguon_goc_giu_trang_doi_chieu(self):
        self.abbyy.doc_pdf.return_value = pdf_demo(())
        result = self.chon.doc(self.raw, 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'chua_ro')
        self.mask.assert_called_once_with(self.raw, 'pdf', huy=None)
        self.assertEqual(self.so_trang(), 1)

    def test_pdf_abbyy_thieu_trang_khong_tra_thanh_cong_mot_phan(self):
        self.mask.return_value = ket_qua(2)
        result = self.chon.doc(pdf_demo(('DEMO 1',), ('DEMO 2',)), 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'chua_ro')
        self.assertEqual(self.so_trang(), 2)

    def test_ca_hai_nguon_loi_tra_loi_sach_khong_thanh_cong_gia(self):
        self.abbyy.doc_pdf.side_effect = LoiKetNoiABBYY('ABBYY_KHOA_SAI')
        self.mask.side_effect = RuntimeError('DEMO KEY đường dẫn')
        with self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf')
        self.assertEqual(caught.exception.code, 'OCR_KHONG_DOC_DUOC')
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn('KEY', str(caught.exception))
        self.assertEqual(self.so_trang(), 0)

    def test_mask_rong_hoac_sai_so_trang_khong_thanh_cong_gia(self):
        self.abbyy.san_sang.return_value = False
        for result in (None, KetQuaLopChu(''), KetQuaLopChu(CHU, pages=[])):
            with self.subTest(result=type(result).__name__):
                self.mask.return_value = result
                with self.assertRaises(DataError) as caught:
                    self.chon.doc(self.raw, 'pdf')
                self.assertEqual(caught.exception.code, 'OCR_KHONG_DOC_DUOC')

    def test_huy_truoc_gui_hoan_trang_sau_goi_giu_trang(self):
        huy = threading.Event()
        huy.set()
        with self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual(caught.exception.code, 'OCR_HUY')
        self.abbyy.doc_pdf.assert_not_called()
        self.mask.assert_not_called()
        huy.clear()
        self.abbyy.doc_pdf.side_effect = LoiLopChu('OCR_HUY', 'Đã hủy DEMO')
        with self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual(caught.exception.code, 'OCR_HUY')
        self.mask.assert_not_called()
        self.assertEqual(self.so_trang(), 1)
        self.assertEqual(self.chon.trang_thai()['trang_thai_may_abbyy'], 'chưa rõ')

    def test_huy_trong_khi_abbyy_tra_ket_qua_khong_hoan_trang_da_gui(self):
        self.ghi_so([[LUC - 1, 37]])
        huy = threading.Event()

        def doc(*args, **kwargs):
            huy.set()
            return self.pdf

        self.abbyy.doc_pdf.side_effect = doc
        with self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual(caught.exception.code, 'OCR_HUY')
        self.assertEqual(self.so_trang(), 38)
        self.mask.assert_not_called()

    def test_mask_bao_huy_khong_bi_doi_thanh_loi_chung(self):
        self.abbyy.san_sang.return_value = False
        self.mask.side_effect = LoiLopChu('OCR_HUY', 'Đã hủy DEMO')
        with self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf')
        self.assertEqual(caught.exception.code, 'OCR_HUY')
        self.assertEqual(self.so_trang(), 0)

    def test_cua_so_truot_bien_30_ngay_va_luu_qua_doi_tuong_moi(self):
        self.ghi_so([[LUC - 30 * 86400 - 1, 5000], [LUC - 30 * 86400, 4999]])
        self.chon.doc(self.raw, 'pdf')
        other = chon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=self.tao_cong(), mask_ocr=self.mask)
        status = chay.trang_thai_nguon(chon_nguon=other)
        self.assertEqual(status['han_muc_da_dung'], 5000)
        self.assertEqual(status['han_muc_con_lai'], 0)
        self.assertEqual(status['ngay_bat_dau_ky'], '08/10/2026')
        self.assertEqual(status['trang_thai_may_abbyy'], 'sẵn sàng')
        self.now.return_value = LUC + 1
        self.assertEqual(other.trang_thai()['han_muc_da_dung'], 1)

    def test_trang_thai_khong_ket_noi_loi_gan_nhat_va_hoi_phuc(self):
        self.abbyy.san_sang.return_value = False
        self.assertEqual(self.chon.trang_thai()['trang_thai_may_abbyy'], 'không kết nối')
        self.abbyy.san_sang.return_value = True
        self.abbyy.doc_pdf.side_effect = LoiKetNoiABBYY('OCR_QUA_GIO')
        self.chon.doc(self.raw, 'pdf')
        status = self.chon.trang_thai()
        self.assertEqual(status['trang_thai_may_abbyy'], 'lỗi gần nhất')
        self.assertNotIn('KEY', json.dumps(status, ensure_ascii=False))
        self.abbyy.doc_pdf.side_effect = None
        self.chon.doc(self.raw, 'pdf')
        self.assertEqual(self.chon.trang_thai()['trang_thai_may_abbyy'], 'sẵn sàng')

    def test_so_hong_khong_reset_ve_khong_va_khong_goi_abbyy(self):
        self.cong.tep_so_trang.write_text('DEMO sổ hỏng', encoding='utf-8')
        result = self.chon.doc(self.raw, 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'so_han_muc_can_kiem_tra')
        self.abbyy.doc_pdf.assert_not_called()
        status = self.chon.trang_thai()
        self.assertIsNone(status['han_muc_da_dung'])
        self.assertIsNone(status['han_muc_con_lai'])
        self.assertEqual(self.cong.tep_so_trang.read_text(encoding='utf-8'), 'DEMO sổ hỏng')

    def test_loi_ghi_so_khong_gui_abbyy_va_khong_bao_da_hoan_gia(self):
        with patch.object(self.cong, '_ghi_so', side_effect=OSError('DEMO đường dẫn kín')):
            result = self.chon.doc(self.raw, 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'so_han_muc_can_kiem_tra')
        self.abbyy.doc_pdf.assert_not_called()
        self.abbyy.doc_pdf.side_effect = LoiKetNoiABBYY('OCR_QUA_GIO')
        with patch.object(self.cong, '_hoan_trang', side_effect=OSError('DEMO đường dẫn kín')):
            result = self.chon.doc(self.raw, 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'so_han_muc_can_kiem_tra')
        self.assertEqual(self.so_trang(), 1)
        self.assertIn('Chưa xác nhận', self.chon.trang_thai()['loi_gan_nhat'])

    def _kiem_chuoi_a_b_c(self):
        """A lưu, B lỗi trước lưu, C lưu trước khi B chạy nhánh hoàn."""
        self.ghi_so([])
        cong_a, cong_b, cong_c = (self.tao_cong() for _ in range(3))
        abbyy_b = Mock(san_sang=Mock(return_value=True), doc_pdf=Mock(return_value=self.pdf))
        selectors = [chon.ChonNguonOCR(abbyy=backend, cong_ocr=cong, mask_ocr=self.mask)
                     for cong, backend in ((cong_a, self.abbyy), (cong_b, abbyy_b),
                                           (cong_c, self.abbyy))]
        self.assertEqual(selectors[0].doc(self.raw, 'pdf').nguon_doc, 'ABBYY')
        hang_a = cong_a._doc_so()
        hoan_b, ghi_b = cong_b._hoan_trang, cong_b._ghi_so
        truoc_hoan, hang_a_c = [], []

        def ghi_loi(ds, *, them=None, bot=None):
            if them is not None:
                raise OSError('DEMO lượt B lỗi trước khi lưu')
            return ghi_b(ds, bot=bot)

        def chen_c(ma):
            truoc_hoan.append(dict(cong_b._giu_cho))
            self.assertEqual(selectors[2].doc(pdf_demo(('DEMO tài liệu C',)), 'pdf').nguon_doc, 'ABBYY')
            hang_a_c.extend(cong_c._doc_so())
            return hoan_b(ma)

        with patch.object(cong_b, '_ghi_so', side_effect=ghi_loi) as ghi, \
                patch.object(cong_b, '_hoan_trang', side_effect=chen_c):
            result = selectors[1].doc(pdf_demo(('DEMO tài liệu B',)), 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'so_han_muc_can_kiem_tra')
        abbyy_b.doc_pdf.assert_not_called()
        self.assertEqual(sum(row[1] for row in cong_b._doc_so()), 2,
                         'Lượt B không được hoàn trang của A hoặc C')
        self.assertEqual(cong_b._doc_so(), hang_a_c)
        self.assertEqual(hang_a_c[:1], hang_a)
        self.assertEqual(truoc_hoan, [{}], 'Không đặt con trỏ khi chưa lưu được bản ghi')
        self.assertEqual(ghi.call_count, 1, 'Ghi lỗi trước lưu không được ghi hoàn')
        self.assertTrue(all(not cong._giu_cho for cong in (cong_a, cong_b, cong_c)))

    def test_chuoi_a_b_c_ghi_loi_truoc_luu_khong_hoan_nham(self):
        self._kiem_chuoi_a_b_c()

    def test_giu_trang_ma_uuid_rieng_va_chi_dat_con_tro_sau_xac_nhan(self):
        ghi_so, doc_so = self.cong._ghi_so, self.cong._doc_so
        luc_ghi, luc_doc_sau_ghi = [], []

        def ghi(ds, **kwargs):
            luc_ghi.append(dict(self.cong._giu_cho))
            return ghi_so(ds, **kwargs)

        def doc():
            rows = doc_so()
            if rows:
                luc_doc_sau_ghi.append(dict(self.cong._giu_cho))
            return rows

        for ma in ('luot-DEMO-1', 'luot-DEMO-2'):
            with patch.object(self.cong, '_ghi_so', side_effect=ghi), \
                    patch.object(self.cong, '_doc_so', side_effect=doc):
                self.chon._giu_trang(1, ma)
            self.assertIn(ma, self.cong._giu_cho)
            self.cong._giu_cho.pop(ma)
        rows = doc_so()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(row) == 3 for row in rows), 'Bản ghi mới phải có mã giữ chỗ')
        self.assertEqual([row[:2] for row in rows], [[LUC, 1], [LUC, 1]])
        self.assertEqual(len({str(UUID(row[2])) for row in rows}), 2)
        self.assertEqual(luc_ghi, [{}, {}])
        self.assertTrue(luc_doc_sau_ghi)
        self.assertTrue(all(not ptr for ptr in luc_doc_sau_ghi))

    def test_ghi_khong_luu_dung_ma_khong_dat_con_tro_khong_gui_abbyy(self):
        nen = [[LUC, 1, str(uuid4())]]
        self.ghi_so(nen)
        with patch.object(self.cong, '_ghi_so') as ghi:
            result = self.chon.doc(self.raw, 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'so_han_muc_can_kiem_tra')
        self.abbyy.doc_pdf.assert_not_called()
        self.assertEqual(self.cong._doc_so(), nen)
        self.assertEqual(self.cong._giu_cho, {})
        self.assertEqual(ghi.call_count, 1)

    def _kiem_hoan_dung_ma_giu_nguyen_hang_cu(self):
        ma_a, ma_b = str(uuid4()), str(uuid4())
        cu, hang_a, hang_b = [LUC, 1], [LUC, 1, ma_a], [LUC, 1, ma_b]
        self.ghi_so([cu, hang_a, hang_b])
        self.assertEqual(self.cong._doc_so(), [cu, hang_a, hang_b])
        self.cong._giu_cho['luot-DEMO-B'] = hang_b
        self.cong._hoan_trang('luot-DEMO-B')
        self.assertEqual(self.cong._doc_so(), [cu, hang_a])
        self.assertEqual(self.cong._giu_cho, {})

    def test_doc_so_hai_ba_cot_hoan_chi_dung_ma_khong_dung_hang_cu(self):
        self._kiem_hoan_dung_ma_giu_nguyen_hang_cu()

    def test_so_cu_hai_cot_van_doc_tinh_han_muc_va_khong_bi_hoan(self):
        nen = [[LUC - 30 * 86400, 37], [LUC, 1], [LUC, 1]]
        self.ghi_so([[LUC - 30 * 86400 - 1, 5000]] + nen)
        self.assertEqual(self.cong._doc_so(), nen)
        self.assertEqual(self.chon.trang_thai()['han_muc_da_dung'], 39)
        self.abbyy.doc_pdf.side_effect = LoiKetNoiABBYY('OCR_QUA_GIO')
        self.assertEqual(self.chon.doc(self.raw, 'pdf').ma_ly_do_chuyen, 'qua_thoi_gian')
        self.assertEqual(self.cong._doc_so(), nen)
        # Con trỏ cũ không có mã cũng không cho phép trừ bản ghi hai cột.
        self.cong._giu_cho['con-tro-cu-DEMO'] = [LUC, 1]
        self.cong._hoan_trang('con-tro-cu-DEMO')
        self.assertEqual(self.cong._doc_so(), nen)

    def test_so_ba_cot_sai_ma_hoac_sai_cau_truc_khong_duoc_coi_la_rong(self):
        for row in ([LUC, 1, None], [LUC, 1, ''], [LUC, 1, []], [LUC, 1, 'ma', 'du']):
            with self.subTest(row=row):
                self.ghi_so([row])
                with self.assertRaises(ValueError):
                    self.cong._doc_so()

    def test_mutation_dat_con_tro_truoc_ghi_bi_chuoi_a_b_c_bat(self):
        def giu_som(selector, trang, ma, *, huy=None):
            with chon._khoa_tep(selector._cong.tep_so_trang.with_suffix('.lock'),
                               selector._cong.nghi, huy):
                ds = selector._cong._doc_so()
                ban_ghi = [LUC, trang, str(uuid4())]
                selector._cong._giu_cho[ma] = ban_ghi
                selector._cong._ghi_so(ds + [ban_ghi], them=ban_ghi)

        with patch.object(chon.ChonNguonOCR, '_giu_trang', giu_som), \
                self.assertRaisesRegex(AssertionError, 'Không đặt con trỏ'):
            self._kiem_chuoi_a_b_c()

    def test_mutation_hoan_theo_hai_cot_bi_bat(self):
        def hoan_sai(cong, ma):
            ban_ghi = cong._giu_cho[ma]
            ds = cong._doc_so()
            nham = next(row for row in ds if row[:2] == ban_ghi[:2])
            ds.remove(nham)
            cong._ghi_so(ds, bot=nham)
            cong._giu_cho.pop(ma)

        with patch.object(CongOCR, '_hoan_trang', hoan_sai), self.assertRaises(AssertionError):
            self._kiem_hoan_dung_ma_giu_nguyen_hang_cu()

    def test_mutation_co_che_cu_hai_cot_hoan_nham_c_bi_bat(self):
        def giu_cu(selector, trang, ma, *, huy=None):
            with chon._khoa_tep(selector._cong.tep_so_trang.with_suffix('.lock'),
                               selector._cong.nghi, huy):
                ds = selector._cong._doc_so()
                row = [LUC, trang]
                while row in ds:
                    row[0] = math.nextafter(row[0], math.inf)
                selector._cong._giu_cho[ma] = row
                selector._cong._ghi_so(ds + [row], them=row)

        def hoan_cu(cong, ma):
            row = cong._giu_cho.get(ma)
            if row is not None:
                ds = cong._doc_so()
                if row in ds:
                    ds.remove(row)
                cong._ghi_so(ds, bot=row)
                cong._giu_cho.pop(ma, None)

        with patch.object(chon.ChonNguonOCR, '_giu_trang', giu_cu), \
                patch.object(CongOCR, '_hoan_trang', hoan_cu), \
                self.assertRaisesRegex(AssertionError, 'Lượt B không được hoàn'):
            self._kiem_chuoi_a_b_c()

    def test_loi_doc_xac_nhan_sau_ghi_hoan_trang_khong_gui_abbyy(self):
        doc_so = self.cong._doc_so
        for nen in ([], [[LUC - 1, 37]]):
            with self.subTest(nen=nen):
                self.ghi_so(nen)
                self.mask.reset_mock()
                da_loi = False

                def doc():
                    nonlocal da_loi
                    rows = doc_so()
                    # Chỉ lỗi sau os.replace: trang đã nằm trên đĩa thật.
                    if not da_loi and any(row[:2] == [LUC, 1] for row in rows):
                        da_loi = True
                        raise OSError('DEMO lỗi đọc xác nhận sau ghi')
                    return rows

                with patch.object(self.cong, '_doc_so', side_effect=doc):
                    result = self.chon.doc(self.raw, 'pdf')
                self.assertTrue(da_loi)
                self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen),
                                 ('mask_ocr', 'so_han_muc_can_kiem_tra'))
                self.abbyy.doc_pdf.assert_not_called()
                self.mask.assert_called_once_with(self.raw, 'pdf', huy=None)
                self.assertEqual(doc_so(), nen)
                self.assertEqual(self.cong._giu_cho, {})

    def test_docx_loi_xac_nhan_khong_de_con_tro_moi_trong_ram(self):
        doc_so = self.cong._doc_so
        da_loi = False

        def doc():
            nonlocal da_loi
            rows = doc_so()
            if rows and not da_loi:
                da_loi = True
                raise OSError('DEMO lỗi xác nhận trên đường DOCX cũ')
            return rows

        with patch.object(self.cong, '_doc_so', side_effect=doc), \
                patch.object(self.cong, '_chay_hot_folder') as gui, self.assertRaises(DataError):
            self.cong.ocr(self.raw, 'pdf')
        self.assertTrue(da_loi)
        gui.assert_not_called()
        self.assertEqual(self.cong._giu_cho, {})
        # Giữ chính sách cũ khi lỗi xác nhận: không tự hoàn bản ghi đã lưu.
        self.assertEqual(sum(row[1] for row in doc_so()), 1)

    def _kiem_hai_lan_doc_loi(self, loi=OSError, loi_phuc_hoi=OSError, *, docx=False):
        # Cùng thời điểm/số trang: chỉ mã giữ chỗ mới cho phép nhận đúng lượt.
        nen = [[LUC, 1], [LUC, 1, str(uuid4())]]
        self.ghi_so(nen)
        doc_so, da_loi = self.cong._doc_so, []
        loi_goc = loi('DEMO xác nhận ' + str(self.tmp))
        loi_sau = loi_phuc_hoi('DEMO phục hồi ' + str(self.tmp))

        def doc():
            rows = doc_so()
            if len(rows) > len(nen):
                da_loi.append(True)
                raise loi_goc if len(da_loi) == 1 else loi_sau
            return rows

        with patch.object(self.cong, '_doc_so', side_effect=doc), \
                patch.object(self.cong, '_chay_hot_folder') as gui, \
                patch.object(ocr._LOG, 'warning') as log:
            if docx or not isinstance(loi_goc, Exception):
                with self.assertRaises(DataError if docx and isinstance(loi_goc, Exception)
                                       else type(loi_goc)) as caught:
                    if docx:
                        self.cong.ocr(self.raw, 'pdf')
                    else:
                        self.chon.doc(self.raw, 'pdf')
                if not isinstance(loi_goc, Exception):
                    self.assertIs(caught.exception, loi_goc, 'Giữ lỗi gốc khi phục hồi cũng lỗi')
            else:
                try:
                    result = self.chon.doc(self.raw, 'pdf')
                except KeyboardInterrupt:
                    self.fail('Lỗi phục hồi không được thay lỗi xác nhận ban đầu')
                self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen),
                                 ('mask_ocr', 'so_han_muc_can_kiem_tra'))
        self.assertEqual(len(da_loi), 2, 'Ghi thật rồi lỗi cả xác nhận lẫn phục hồi')
        gui.assert_not_called()
        self.abbyy.doc_pdf.assert_not_called()
        self.assertEqual(self.cong._giu_cho, {})
        # Đọc JSON trực tiếp để chưa kích hoạt đối chiếu ở lượt đọc kế tiếp.
        du = json.loads(self.cong.tep_so_trang.read_text(encoding='utf-8'))
        self.assertEqual(du[:2], nen)
        self.assertEqual(sum(row[1] for row in du), 3)
        return nen, du, log

    def test_hai_lan_doc_loi_giu_du_va_trang_thai_luot_sau_hoan_dung_mot_trang(self):
        nen, du, log = self._kiem_hai_lan_doc_loi()
        self.mask.assert_called_once_with(self.raw, 'pdf', huy=None)
        # Cùng tiến trình, khác đối tượng vẫn đối chiếu cùng sổ.
        khac = self.tao_cong()
        selector = chon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=khac, mask_ocr=self.mask)
        with patch.object(khac, '_ghi_so', wraps=khac._ghi_so) as ghi:
            self.assertEqual(selector.trang_thai()['han_muc_da_dung'], 2)
            self.assertEqual(ghi.call_count, 1)
            self.assertEqual(ghi.call_args.kwargs['bot'], du[-1])
            self.assertEqual(selector.trang_thai()['han_muc_da_dung'], 2)
            self.assertEqual(ghi.call_count, 1, 'Đối chiếu xong không hoàn lần thứ hai')
        self.assertEqual(self.cong._doc_so(), nen)
        log.assert_called_once()
        self.assertNotIn(str(self.tmp), str(log.call_args))
        self.assertNotIn('DEMO xác nhận', str(log.call_args))

    def test_hai_lan_doc_loi_luot_giu_ke_tiep_hoan_truoc_khi_kiem_han_muc(self):
        nen, _, _ = self._kiem_hai_lan_doc_loi()
        # Hạn mức tạm hạ để bắt việc đối chiếu phải xảy ra trước kiểm tra chỗ trống.
        with patch.object(ocr, 'HAN_MUC', 3):
            result = self.chon.doc(self.raw, 'pdf')
        self.assertEqual(result.nguon_doc, 'ABBYY')
        rows = self.cong._doc_so()
        self.assertEqual(rows[:2], nen)
        self.assertEqual(sum(row[1] for row in rows), 3)
        self.abbyy.doc_pdf.assert_called_once()

    def test_doc_phuc_hoi_keyboard_interrupt_khong_lam_mat_doi_chieu(self):
        nen, _, _ = self._kiem_hai_lan_doc_loi(loi_phuc_hoi=KeyboardInterrupt)
        self.assertEqual(self.cong._doc_so(), nen)

    def test_keyboard_interrupt_ca_hai_lan_doc_van_doi_chieu_va_giu_loi_goc(self):
        nen, _, _ = self._kiem_hai_lan_doc_loi(KeyboardInterrupt, KeyboardInterrupt)
        self.mask.assert_not_called()
        self.assertEqual(self.cong._doc_so(), nen)

    def test_doi_chieu_loi_ghi_giu_cho_den_lan_doc_thanh_cong_sau(self):
        nen, du, _ = self._kiem_hai_lan_doc_loi()
        with patch.object(self.cong, '_ghi_so', side_effect=OSError('DEMO chưa hoàn được')):
            state = self.chon.trang_thai()
        self.assertIsNone(state['han_muc_da_dung'])
        self.assertIsNotNone(state['loi_han_muc'])
        self.assertEqual(json.loads(self.cong.tep_so_trang.read_text(encoding='utf-8')), du)
        self.assertEqual(self.chon.trang_thai()['han_muc_da_dung'], 2)
        self.assertEqual(self.cong._doc_so(), nen)

    def test_doi_chieu_khong_thay_ma_thi_bo_cho_khong_ghi_hoan(self):
        nen, du, _ = self._kiem_hai_lan_doc_loi()
        self.ghi_so(nen)  # Review đã ghi mất lượt chưa xác nhận.
        with patch.object(self.cong, '_ghi_so', wraps=self.cong._ghi_so) as ghi:
            self.assertEqual(self.cong._doc_so(), nen)
            ghi.assert_not_called()
            # Mã đã được bỏ khỏi chờ; không hoàn một bản ghi đến sau.
            self.ghi_so(du)
            self.assertEqual(self.cong._doc_so(), du)
            ghi.assert_not_called()

    def test_doi_chieu_da_ghi_hoan_nhung_doc_xac_nhan_loi_khong_hoan_them(self):
        nen, _, _ = self._kiem_hai_lan_doc_loi()
        doc_goc = self.cong._doc_so_goc

        def doc():
            rows = doc_goc()
            if rows == nen:
                raise OSError('DEMO đọc xác nhận hoàn lỗi')
            return rows

        with patch.object(self.cong, '_doc_so_goc', side_effect=doc):
            self.assertIsNone(self.chon.trang_thai()['han_muc_da_dung'])
        self.assertEqual(json.loads(self.cong.tep_so_trang.read_text(encoding='utf-8')), nen)
        with patch.object(self.cong, '_ghi_so', wraps=self.cong._ghi_so) as ghi:
            self.assertEqual(self.cong._doc_so(), nen)
            ghi.assert_not_called()

    def test_review_chen_lai_ma_sau_xac_nhan_hoan_van_giu_cho_doi_chieu(self):
        nen, du, _ = self._kiem_hai_lan_doc_loi()
        ghi_so = self.cong._ghi_so

        def ghi(ds, **kwargs):
            ghi_so(ds, **kwargs)
            # Review cũ không giữ khóa, ghi lại ngay sau lần xác nhận hoàn.
            self.ghi_so(du)

        with patch.object(self.cong, '_ghi_so', side_effect=ghi):
            self.assertIsNone(self.chon.trang_thai()['han_muc_da_dung'])
        self.assertEqual(self.cong._doc_so(), nen)

    def test_docx_hai_lan_doc_loi_khong_gui_va_lan_doc_sau_tu_doi_chieu(self):
        nen, _, _ = self._kiem_hai_lan_doc_loi(docx=True)
        self.mask.assert_not_called()
        self.assertEqual(self.cong._doc_so(), nen)

    def test_huy_sau_ghi_truoc_xac_nhan_van_hoan_trang(self):
        self.ghi_so([[LUC - 1, 37]])
        huy = threading.Event()
        doc_so = self.cong._doc_so

        def doc():
            rows = doc_so()
            if not huy.is_set() and any(row[:2] == [LUC, 1] for row in rows):
                huy.set()
                raise DataError('OCR_HUY', 'Đã hủy DEMO sau ghi sổ')
            return rows

        with patch.object(self.cong, '_doc_so', side_effect=doc), self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual(caught.exception.code, 'OCR_HUY')
        self.assertTrue(huy.is_set())
        self.assertEqual(doc_so(), [[LUC - 1, 37]])
        self.assertEqual(self.cong._giu_cho, {})
        self.abbyy.doc_pdf.assert_not_called()
        self.mask.assert_not_called()

    def test_thoat_bat_thuong_sau_goi_khong_hoan_trang(self):
        self.ghi_so([[LUC - 1, 37]])
        self.abbyy.doc_pdf.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.chon.doc(self.raw, 'pdf')
        self.assertEqual(self.so_trang(), 38)
        self.assertEqual(self.chon.trang_thai()['trang_thai_may_abbyy'], 'chưa rõ')
        self.mask.assert_not_called()

    def test_anh_png_that_duoc_dem_mot_trang(self):
        from PIL import Image
        with io.BytesIO() as stream:
            Image.new('RGB', (16, 16), 'white').save(stream, format='PNG')
            raw = stream.getvalue()
        result = self.chon.doc(raw, 'png')
        self.assertEqual(result.nguon_doc, 'ABBYY')
        self.abbyy.doc_pdf.assert_called_once_with(raw, 'png', huy=None)
        self.assertEqual(self.so_trang(), 1)

    def test_hai_doi_tuong_dong_thoi_khong_vuot_han_muc(self):
        self.ghi_so([[LUC, 4999]])
        cong_khac = self.tao_cong()
        other = chon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=cong_khac, mask_ocr=self.mask)
        bat_dau = threading.Barrier(2)
        da_doc_1, dang_giu_2, da_doc_2 = (threading.Event() for _ in range(3))
        doc_so_1, doc_so_2 = self.cong._doc_so, cong_khac._doc_so

        def san_sang_1():
            bat_dau.wait(5)
            return None

        def san_sang_2():
            bat_dau.wait(5)
            if not da_doc_1.wait(5):
                raise AssertionError('DEMO lượt thứ nhất chưa đọc sổ')
            dang_giu_2.set()
            return None

        def doc_1():
            rows = doc_so_1()
            if not da_doc_1.is_set():
                da_doc_1.set()
                if not dang_giu_2.wait(5):
                    raise AssertionError('DEMO lượt thứ hai chưa giữ trang')
                # Dừng giữa đọc và ghi. Có khóa: lượt 2 chưa đọc được;
                # bỏ khóa: cả hai cùng đọc 4999 và đều định giữ thêm trang.
                # Timeout hữu hạn để bản có khóa tiếp tục, không deadlock.
                da_doc_2.wait(1)
            return rows

        def doc_2():
            rows = doc_so_2()
            da_doc_2.set()
            return rows

        with patch.object(self.chon, '_kiem_may', side_effect=san_sang_1), \
                patch.object(other, '_kiem_may', side_effect=san_sang_2), \
                patch.object(self.cong, '_doc_so', side_effect=doc_1), \
                patch.object(cong_khac, '_doc_so', side_effect=doc_2), \
                ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(selector.doc, raw, 'pdf') for selector, raw in
                       ((self.chon, self.raw), (other, pdf_demo(('DEMO tài liệu khác',))))]
            results = [future.result(timeout=5) for future in futures]
        self.assertEqual([result.nguon_doc for result in results], ['ABBYY', 'mask_ocr'])
        self.assertEqual(results[1].ma_ly_do_chuyen, 'het_han_muc')
        self.assertEqual(self.so_trang(), 5000)
        self.assertEqual(self.abbyy.doc_pdf.call_count, 1)
        self.mask.assert_called_once_with(pdf_demo(('DEMO tài liệu khác',)), 'pdf', huy=None)
        self.assertEqual(self.cong._giu_cho, {})
        self.assertEqual(cong_khac._giu_cho, {})

    def test_dau_vao_hong_qua_trang_qua_co_khong_gui_ocr(self):
        for raw, duoi in (('DEMO hỏng'.encode('utf-8'), 'pdf'), (self.raw, 'docx'),
                          (b'x' * (20 * 1024**2 + 1), 'pdf'),
                          (pdf_demo(*[('DEMO',)] * 61), 'pdf')):
            with self.subTest(duoi=duoi, size=len(raw)), self.assertRaises(DataError):
                self.chon.doc(raw, duoi)
        self.abbyy.doc_pdf.assert_not_called()
        self.mask.assert_not_called()

    def _tiem_kn3(self):
        client = Mock(spec=KetNoiABBYY)
        client.san_sang.return_value = True
        client.doc_pdf.return_value = self.pdf
        self.chon = chon.ChonNguonOCR(abbyy=abbyy.BackendKetNoiABBYY(ket_noi=client),
                                     cong_ocr=self.cong, mask_ocr=self.mask)
        return client

    def test_kn4_khong_tiem_mac_dinh_tat_khong_doc_cau_hinh_hay_goi_mang(self):
        with patch('builtins.open', side_effect=AssertionError('Không đọc cấu hình')), \
                patch.object(Path, 'read_text', side_effect=AssertionError('Không đọc cấu hình')), \
                patch('http.client.HTTPSConnection', side_effect=AssertionError('Không gọi mạng')):
            backend = abbyy.BackendKetNoiABBYY()
            self.assertIs(backend.san_sang(), False)
            self.assertIs(abbyy.BackendKetNoiABBYY(ket_noi=KetNoiABBYY()).san_sang(), False)
            with self.assertRaises(LoiKetNoiABBYY) as caught:
                backend.doc_pdf(self.raw)
            self.assertIs(caught.exception.chua_ro_da_nhan, False)
        selector = chon.ChonNguonOCR(cong_ocr=self.cong, mask_ocr=self.mask)
        self.assertEqual(selector.trang_thai()['trang_thai_may_abbyy'], 'không kết nối')
        result = selector.doc(self.raw, 'pdf')
        self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'khong_ket_noi'))
        self.assertEqual(self.so_trang(), 0)

    def test_kn4_tiem_client_san_sang_dung_va_truyen_cung_ma_xuong_kn3(self):
        client = self._tiem_kn3()
        ma, huy = str(uuid4()), threading.Event()
        result = self.chon.doc(self.raw, '.PDF', ma_yeu_cau=ma, huy=huy)
        self.assertEqual(result.nguon_doc, 'ABBYY')
        client.doc_pdf.assert_called_once_with(self.raw, 'pdf', huy=huy, ma_yeu_cau=ma)
        self.assertEqual(self.so_trang(), 1)
        self.mask.assert_not_called()
        with self.assertRaises(TypeError):
            self.chon._abbyy.doc_pdf(self.raw, endpoint='https://DEMO.invalid')
        self.assertNotIn('DEMO', repr(self.chon._abbyy))

    def test_kn4_loi_truoc_gui_hoan_trang_fallback_va_co_the_gui_luot_moi(self):
        client = self._tiem_kn3()
        for code in ('ABBYY_KHONG_KET_NOI', 'ABBYY_CHUNG_THU', 'ABBYY_KHOA_SAI', 'OCR_KICH_THUOC'):
            with self.subTest(code=code):
                client.doc_pdf.side_effect = LoiKetNoiABBYY(code, chua_ro_da_nhan=False)
                with patch.object(self.cong, '_hoan_trang', wraps=self.cong._hoan_trang) as hoan:
                    result = self.chon.doc(self.raw, 'pdf')
                hoan.assert_called_once()
                self.assertEqual(result.nguon_doc, 'mask_ocr')
                self.assertEqual(self.so_trang(), 0)
                self.assertEqual(self.chon.trang_thai()['luot_chua_ro'], [])
        self.assertEqual(client.doc_pdf.call_count, 4)

    def test_kn4_timeout_sau_gui_giu_trang_chua_ro_va_khong_gui_lai(self):
        client = self._tiem_kn3()
        ma = str(uuid4())
        client.doc_pdf.side_effect = LoiKetNoiABBYY('ABBYY_CHUA_RO_DA_NHAN',
            ma_yeu_cau='DEMO bí mật không được tin', chua_ro_da_nhan=True, nguyen_nhan='OCR_QUA_GIO')
        with patch.object(self.cong, '_hoan_trang', wraps=self.cong._hoan_trang) as hoan:
            result = self.chon.doc(self.raw, 'pdf', ma_yeu_cau=ma)
            self.assertEqual((result.nguon_doc, result.ma_ly_do_chuyen), ('mask_ocr', 'chua_ro'))
            self.assertEqual((result.trang_thai_abbyy, result.ma_tuong_quan), ('chua_ro', ma))
            # Cùng sổ, đối tượng mới, máy đã tắt cũng không được bỏ chặn.
            other = chon.ChonNguonOCR(cong_ocr=self.tao_cong(), mask_ocr=self.mask)
            for selector, raw, key in ((self.chon, self.raw, ma), (self.chon, self.raw, str(uuid4())),
                                       (other, pdf_demo(('DEMO tài liệu khác',)), ma),
                                       (other, self.raw, None)):
                with self.subTest(key=key), self.assertRaises(DataError) as caught:
                    selector.doc(raw, 'pdf', ma_yeu_cau=key)
                self.assertEqual(caught.exception.code, 'OCR_CHUA_RO_KET_QUA')
                self.assertEqual(caught.exception.ma_tuong_quan, ma)
            hoan.assert_not_called()
        status = other.trang_thai()
        self.assertEqual(status['trang_thai_may_abbyy'], 'chưa rõ')
        self.assertEqual(status['luot_chua_ro'], [dict(ma_tuong_quan=ma, so_trang=1)])
        self.assertEqual((status['han_muc_da_dung'], status['han_muc_con_lai']), (1, 4999))
        self.assertNotIn('bí mật', repr(result.du_lieu()) + repr(status))
        client.doc_pdf.assert_called_once()
        self.mask.assert_called_once()

    def test_kn4_loi_khong_co_bang_chung_chua_nhan_deu_giu_trang(self):
        client = self._tiem_kn3()
        for i, exc in enumerate((TimeoutError('DEMO KEY đường dẫn'), ConnectionResetError('DEMO KEY'),
                                 RuntimeError('DEMO KEY'), TypeError('DEMO KEY'),
                                 LoiKetNoiABBYY('ABBYY_YEU_CAU_TRUNG', chua_ro_da_nhan=True))):
            with self.subTest(loi=type(exc).__name__):
                client.doc_pdf.side_effect = exc
                raw = pdf_demo((f'DEMO tài liệu {i}',))
                result = self.chon.doc(raw, 'pdf')
                self.assertEqual(result.trang_thai_abbyy, 'chua_ro')
                self.assertNotIn('KEY', repr(result.du_lieu()))
                with self.assertRaises(DataError):
                    self.chon.doc(raw, 'pdf')
        self.assertEqual(self.so_trang(), 5)
        self.assertEqual(client.doc_pdf.call_count, 5)

    def test_kn4_ca_hai_nguon_loi_van_tra_chua_ro_cung_ma_va_chan_gui_lai(self):
        client = self._tiem_kn3()
        client.doc_pdf.side_effect = TimeoutError('DEMO KEY')
        self.mask.side_effect = RuntimeError('DEMO KEY')
        with self.assertRaises(DataError) as caught:
            self.chon.doc(self.raw, 'pdf')
        self.assertEqual(caught.exception.code, 'OCR_CHUA_RO_KET_QUA')
        self.assertIsNone(caught.exception.__context__)
        self.assertIsNone(caught.exception.__cause__)
        ma = caught.exception.ma_tuong_quan
        with self.assertRaises(DataError) as again:
            self.chon.doc(self.raw, 'pdf')
        self.assertEqual(again.exception.ma_tuong_quan, ma)
        with self.assertRaises(DataError) as same_key:
            self.chon.doc(pdf_demo(('DEMO khác',)), 'pdf', ma_yeu_cau=ma)
        self.assertEqual(same_key.exception.ma_tuong_quan, ma)
        self.assertEqual(self.so_trang(), 1)
        client.doc_pdf.assert_called_once()

    def _anh_jpeg(self):
        from PIL import Image
        with io.BytesIO() as stream:
            Image.new('RGB', (16, 16), 'white').save(stream, format='JPEG')
            return stream.getvalue()

    def test_kn4_chua_ro_doi_duoi_jpg_jpeg_va_uuid_van_chi_gui_mot_lan(self):
        raw, ma = self._anh_jpeg(), str(uuid4())
        client = self._tiem_kn3()
        client.doc_pdf.side_effect = TimeoutError('DEMO timeout đọc')
        result = self.chon.doc(raw, 'jpg', ma_yeu_cau=ma)
        self.assertEqual((result.trang_thai_abbyy, result.ma_tuong_quan), ('chua_ro', ma))
        other = chon.ChonNguonOCR(abbyy=self.chon._abbyy, cong_ocr=self.tao_cong(), mask_ocr=self.mask)
        for selector, duoi in ((self.chon, 'jpeg'), (other, '.JPEG')):
            with self.subTest(duoi=duoi), self.assertRaises(DataError) as caught:
                selector.doc(raw, duoi, ma_yeu_cau=str(uuid4()))
            self.assertEqual(caught.exception.code, 'OCR_CHUA_RO_KET_QUA')
            self.assertEqual((caught.exception.trang_thai_abbyy, caught.exception.ma_tuong_quan),
                             ('chua_ro', ma))
        self.assertEqual(self.so_trang(), 1)
        client.doc_pdf.assert_called_once_with(raw, 'jpg', huy=None, ma_yeu_cau=ma)
        self.mask.assert_called_once()

    def test_kn4_timeout_doc_roi_fallback_huy_hoac_loi_deu_co_ma_doi_chieu(self):
        client = self._tiem_kn3()
        for mode in ('truoc_mask', 'trong_mask', 'sau_mask', 'loi_mask'):
            with self.subTest(mode=mode):
                raw, ma, huy = pdf_demo((f'DEMO {mode}',)), str(uuid4()), threading.Event()

                def timeout(*args, **kwargs):
                    if mode == 'truoc_mask':
                        huy.set()
                    raise TimeoutError('DEMO timeout đọc')

                def mask(*args, **kwargs):
                    if mode == 'trong_mask':
                        raise LoiLopChu('OCR_HUY', 'Đã hủy DEMO')
                    if mode == 'sau_mask':
                        huy.set()
                        return ket_qua()
                    raise RuntimeError('DEMO KEY đường dẫn kín')

                client.doc_pdf.side_effect = timeout
                self.mask.side_effect = mask
                with self.assertRaises(DataError) as caught:
                    self.chon.doc(raw, 'pdf', ma_yeu_cau=ma, huy=huy)
                exc = caught.exception
                self.assertEqual(exc.code, 'OCR_CHUA_RO_KET_QUA' if mode == 'loi_mask' else 'OCR_HUY')
                self.assertEqual((exc.trang_thai_abbyy, exc.ma_tuong_quan), ('chua_ro', ma))
                self.assertIsNone(exc.__context__)
                self.assertIsNone(exc.__cause__)
                self.assertNotIn('KEY', str(exc))
                with self.assertRaises(DataError) as again:
                    self.chon.doc(raw, 'pdf', ma_yeu_cau=str(uuid4()))
                self.assertEqual(again.exception.ma_tuong_quan, ma)
        self.assertEqual(self.so_trang(), 4)
        self.assertEqual(client.doc_pdf.call_count, 4)
        self.assertEqual(self.mask.call_count, 3)

    def test_kn4_sau_thanh_cong_doi_duoi_uuid_khong_gui_lai_hay_giu_them_trang(self):
        raw, ma = self._anh_jpeg(), str(uuid4())
        client = self._tiem_kn3()
        self.assertEqual(self.chon.doc(raw, 'jpg', ma_yeu_cau=ma).nguon_doc, 'ABBYY')
        other = chon.ChonNguonOCR(abbyy=self.chon._abbyy, cong_ocr=self.tao_cong(), mask_ocr=self.mask)
        for selector, body, duoi, key in ((self.chon, raw, 'jpg', ma),
                (self.chon, raw, 'jpeg', str(uuid4())), (other, raw, '.JPEG', None),
                (other, self.raw, 'pdf', ma)):
            with self.subTest(duoi=duoi), self.assertRaises(DataError) as caught:
                selector.doc(body, duoi, ma_yeu_cau=key)
            self.assertEqual(caught.exception.code, 'OCR_DA_XU_LY')
            self.assertEqual(caught.exception.ma_tuong_quan, ma)
        self.assertEqual(self.so_trang(), 1)
        client.doc_pdf.assert_called_once()
        self.mask.assert_not_called()

    def test_kn4_khoa_noi_dung_va_uuid_theo_phap_nhan_dung_chung_cac_module(self):
        client = self._tiem_kn3()
        phap_nhan_a, phap_nhan_b = str(uuid4()), str(uuid4())
        ma = str(uuid4())

        def tao(phap_nhan, ben_goi):
            return chon.ChonNguonOCR(abbyy=self.chon._abbyy, cong_ocr=self.tao_cong(),
                                    mask_ocr=self.mask, phap_nhan_id=phap_nhan, ben_goi=ben_goi)

        selector = tao(phap_nhan_a, 'm4')
        client.doc_pdf.side_effect = TimeoutError('DEMO timeout đọc')
        selector.doc(self.raw, 'pdf', ma_yeu_cau=ma)
        for ben_goi in ('m4', 'm9'):
            with self.subTest(ben_goi=ben_goi):
                same = tao(phap_nhan_a.upper(), ben_goi)
                with self.assertRaises(DataError) as caught:
                    same.doc(self.raw, 'pdf', ma_yeu_cau=str(uuid4()))
                self.assertEqual(caught.exception.code, 'OCR_CHUA_RO_KET_QUA')
                self.assertEqual(caught.exception.ma_tuong_quan, ma)
                self.assertEqual(same.trang_thai()['luot_chua_ro'],
                                 [dict(ma_tuong_quan=ma, so_trang=1)])
                self.assertEqual((self.so_trang(), client.doc_pdf.call_count), (1, 1))
        client.doc_pdf.side_effect = None
        for ben_goi in ('m4', 'm9'):
            with self.subTest(ben_goi=ben_goi):
                other = tao(phap_nhan_b, ben_goi)
                self.assertEqual(other.trang_thai()['luot_chua_ro'], [])
                if ben_goi == 'm4':
                    self.assertEqual(other.doc(self.raw, 'pdf', ma_yeu_cau=ma).nguon_doc, 'ABBYY')
                with self.assertRaises(DataError) as done:
                    other.doc(self.raw, 'pdf', ma_yeu_cau=str(uuid4()))
                self.assertEqual(done.exception.code, 'OCR_DA_XU_LY')
        self.assertEqual((self.so_trang(), client.doc_pdf.call_count), (2, 2))

    def test_kn4_pham_vi_thieu_hoac_sai_bi_tu_choi(self):
        for phap_nhan, ben_goi in ((str(uuid4()), None), (None, 'm4'), ('DEMO sai', 'm4'),
                                  (str(uuid4()), ''), (str(uuid4()), [])):
            with self.subTest(ben_goi=ben_goi), self.assertRaises(TypeError):
                chon.ChonNguonOCR(abbyy=self.abbyy, cong_ocr=self.cong, mask_ocr=self.mask,
                                 phap_nhan_id=phap_nhan, ben_goi=ben_goi)
        self.abbyy.doc_pdf.assert_not_called()

    def test_kn4_lru_thanh_cong_co_gioi_han_khong_quen_luot_chua_ro(self):
        client = self._tiem_kn3()
        raws = [pdf_demo((f'DEMO LRU {i}',)) for i in range(4)]
        with patch.object(chon, '_LUOT_XONG', OrderedDict()), patch.object(chon, '_TOI_DA_LUOT_XONG', 2):
            client.doc_pdf.side_effect = TimeoutError('DEMO timeout đọc')
            unclear = self.chon.doc(raws[0], 'pdf')
            client.doc_pdf.side_effect = None
            for raw in raws[1:3]:
                self.chon.doc(raw, 'pdf')
            with self.assertRaises(DataError) as first:
                self.chon.doc(raws[1], 'pdf')
            self.assertEqual(first.exception.code, 'OCR_DA_XU_LY')
            self.chon.doc(raws[3], 'pdf')
            with self.assertRaises(DataError) as recent:
                self.chon.doc(raws[1], 'pdf')
            self.assertEqual(recent.exception.code, 'OCR_DA_XU_LY')
            with self.assertRaises(DataError) as pending:
                self.chon.doc(raws[0], 'pdf', ma_yeu_cau=str(uuid4()))
            self.assertEqual((pending.exception.code, pending.exception.ma_tuong_quan),
                             ('OCR_CHUA_RO_KET_QUA', unclear.ma_tuong_quan))
            self.assertEqual(self.chon.doc(raws[2], 'pdf').nguon_doc, 'ABBYY')
            self.assertEqual(len(chon._LUOT_XONG), 2)
        self.assertEqual((self.so_trang(), client.doc_pdf.call_count), (5, 5))

    def _kiem_gui_trung(self):
        client = self._tiem_kn3()
        da_gui, tiep_tuc = threading.Event(), threading.Event()
        ma = str(uuid4())

        def gui(*args, **kwargs):
            if not da_gui.is_set():
                da_gui.set()
                if not tiep_tuc.wait(5):
                    raise AssertionError('Lượt đầu chưa được tiếp tục')
            return self.pdf

        client.doc_pdf.side_effect = gui
        other = chon.ChonNguonOCR(abbyy=self.chon._abbyy, cong_ocr=self.tao_cong(), mask_ocr=self.mask)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.chon.doc, self.raw, 'pdf', ma_yeu_cau=ma)
            try:
                self.assertTrue(da_gui.wait(5))
                for selector, raw, key in ((self.chon, self.raw, None), (other, self.raw, str(uuid4())),
                                           (other, pdf_demo(('DEMO tài liệu khác',)), ma)):
                    with self.assertRaises(DataError) as caught:
                        selector.doc(raw, '.PDF', ma_yeu_cau=key)
                    self.assertEqual(caught.exception.code, 'OCR_DANG_XU_LY')
                    self.assertEqual(caught.exception.ma_tuong_quan, ma)
                self.assertEqual(client.doc_pdf.call_count, 1, 'Tài liệu đang chờ chỉ được gửi một lần')
                self.assertEqual(self.so_trang(), 1)
            finally:
                tiep_tuc.set()
            self.assertEqual(future.result(timeout=5).nguon_doc, 'ABBYY')
        self.mask.assert_not_called()

    def test_kn4_goi_trung_dong_thoi_cung_tai_lieu_hoac_khoa_chi_gui_mot_lan(self):
        self._kiem_gui_trung()

    def test_kn4_mutation_bo_chong_trung_bi_bat(self):
        def khong_chan(selector, raw, duoi, so_trang, ma):
            return chon._LuotCho(ma or str(uuid4()), so_trang), []

        with patch.object(chon.ChonNguonOCR, '_dang_ky', khong_chan), \
                self.assertRaisesRegex(AssertionError, 'DataError not raised'):
            self._kiem_gui_trung()

    def test_kn4_log_chi_truong_cho_phep_va_log_loi_khong_gui_lai(self):
        client = self._tiem_kn3()
        client.doc_pdf.side_effect = TimeoutError('DEMO KEY đường dẫn bí mật')
        with patch.object(chon._LOG, 'info') as log:
            result = self.chon.doc(self.raw, 'pdf')
        record = json.loads(log.call_args.args[1])
        self.assertEqual(set(record), {'ma_tuong_quan', 'ket_qua', 'thoi_gian', 'so_trang'})
        self.assertEqual(record['ma_tuong_quan'], result.ma_tuong_quan)
        self.assertEqual(record['ket_qua'], 'chưa rõ')
        self.assertNotIn('KEY', repr(log.call_args))
        client.doc_pdf.side_effect = None
        with patch.object(chon._LOG, 'info', side_effect=RuntimeError('DEMO KEY')):
            self.assertEqual(self.chon.doc(pdf_demo(('DEMO mới',)), 'pdf').nguon_doc, 'ABBYY')
        self.assertEqual(client.doc_pdf.call_count, 2)


class MaskTrongGoiTests(unittest.TestCase):
    def test_pdf_dung_image_text_tesseract_khong_tao_worker_khac(self):
        raw = pdf_demo(('DEMO',), ('DEMO trang 2',))
        extraction = Mock(image_text=Mock(return_value=CHU))
        extraction.PDF_LOCK = threading.Lock()
        page = Mock()
        page.get_pixmap.return_value.tobytes.return_value = b'DEMO PNG'
        page.rect.width, page.rect.height = 595, 842
        pdf = Mock(needs_pass=False)
        pdf.__len__ = Mock(return_value=2)
        pdf.__iter__ = Mock(return_value=iter([page, page]))
        pdf.__enter__ = Mock(return_value=pdf)
        pdf.__exit__ = Mock(return_value=False)
        extraction.pymupdf.open.return_value = pdf
        with patch.object(chon, '_nhap_parser_nguon', return_value=(extraction, Mock())), \
                patch('subprocess.Popen', side_effect=AssertionError('Không mở worker')):
            result = chon.doc_mask_ocr(raw, 'pdf')
        self.assertEqual(result.ocr_pages, 2)
        self.assertEqual(len(result.pages), 2)
        self.assertEqual(extraction.image_text.call_count, 2)
        extraction.image_text.assert_called_with(b'DEMO PNG')

    def test_anh_goi_dung_image_text_trong_goi(self):
        extraction = Mock(image_text=Mock(return_value=CHU))
        extraction.PDF_LOCK = threading.Lock()
        with patch.object(chon, '_nhap_parser_nguon', return_value=(extraction, Mock())):
            result = chon.doc_mask_ocr(b'DEMO PNG', 'png')
        extraction.image_text.assert_called_once_with(b'DEMO PNG')
        self.assertEqual((result.text, result.ocr_pages), ('[Trang 1]\n' + CHU, 1))


if __name__ == '__main__':
    unittest.main()
