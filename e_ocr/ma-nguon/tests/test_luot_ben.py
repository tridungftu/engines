"""OCR-CR-4: SDK/ABBYY giả, PDF DEMO và sổ thử; không mạng hoặc PostgreSQL."""

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
import textwrap
import threading
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from kho_tri_thuc.engines.e_ocr import abbyy, chon_nguon as chon
from kho_tri_thuc.engines.e_ocr.ket_noi_abbyy import KetNoiABBYY, LoiKetNoiABBYY
from kho_tri_thuc.engines.e_ocr.lib import cong_ocr as ocr
from kho_tri_thuc.engines.e_ocr.lop_chu import KetQuaLopChu
from kho_tri_thuc.engines.e_ocr.tests.test_lop_chu import pdf_demo
from kho_tri_thuc.sdk_core.engine import LoiEngine, SDKEngine
from kho_tri_thuc.sdk_core.primitives import DataError


class LuotBenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='ocr-cr4-DEMO-'))
        self.ma = str(uuid4())
        self.raw = pdf_demo(('DEMO tài liệu gốc',))
        self.pdf = pdf_demo(('DEMO kết quả nhận dạng',))
        self.sdk = Mock(spec=SDKEngine)
        self.sdk.ocr_doc_luot.return_value = dict(trang_thai='khong_co')
        self.sdk.ocr_giu_luot.return_value = dict(
            ma_tuong_quan=self.ma, trang_thai='dang_giu', phien_ban=7)
        self.sdk.ocr_chot_luot.side_effect = lambda **kw: dict(trang_thai=kw['ket_qua'])
        self.backend = Mock(san_sang=Mock(return_value=True), doc_pdf=Mock(return_value=self.pdf))
        self.mask = Mock(return_value=KetQuaLopChu('DEMO dự phòng', [], 1,
            [dict(number=1, text='DEMO dự phòng', source='mask_ocr')]))
        for patcher in (patch.object(ocr, '_xoa'), patch.object(chon, '_LUOT_CHO', {}),
                        patch.object(chon, '_LUOT_XONG', OrderedDict())):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.cong = self.tao_cong()
        self.selector = self.tao_chon()

    def tao_cong(self):
        return ocr.CongOCR(self.tmp / 'hot-folder-DEMO', tep_so_trang=self.tmp / 'so_trang.json',
                          thu_muc_dem=self.tmp / 'dem-DEMO', nghi=0.01)

    def tao_chon(self, **kw):
        return chon.ChonNguonOCR(**(dict(abbyy=self.backend, cong_ocr=self.cong,
            mask_ocr=self.mask, sdk=self.sdk) | kw))

    def so_trang(self):
        return sum(row[1] for row in self.cong._doc_so())

    def cho_doi_chieu(self, selector=None):
        with self.assertRaises(DataError) as bat:
            (selector or self.selector).doc(self.raw, 'pdf')
        self.assertEqual(bat.exception.code, 'OCR_CHO_DOI_CHIEU')
        self.assertIn('đang chờ đối chiếu', str(bat.exception))
        self.assertIsNone(bat.exception.__context__)
        self.assertIsNone(bat.exception.__cause__)
        self.assertNotIn('DEMO kín', str(bat.exception) + repr(vars(bat.exception)))
        return bat.exception

    def test_thu_tu_doc_giu_commit_so_gui_va_chot_dung_cas(self):
        thu_tu = []
        giu = self.sdk.ocr_giu_luot.return_value

        def giu_core(**kw):
            thu_tu.append('Core đã commit')
            self.assertEqual(self.so_trang(), 0)
            self.backend.doc_pdf.assert_not_called()
            return giu

        def gui(*args, **kw):
            thu_tu.append('gửi ABBYY')
            self.assertEqual(self.so_trang(), 2)
            self.assertEqual(self.cong._doc_so()[0][2], self.ma)
            self.sdk.ocr_chot_luot.assert_not_called()
            return pdf_demo(('DEMO trang 1',), ('DEMO trang 2',))

        def chot(**kw):
            thu_tu.append('chốt đã tiêu')
            self.backend.doc_pdf.assert_called_once()
            return dict(trang_thai=kw['ket_qua'])

        self.sdk.ocr_giu_luot.side_effect = giu_core
        self.backend.doc_pdf.side_effect = gui
        self.sdk.ocr_chot_luot.side_effect = chot
        raw = pdf_demo(('DEMO nguồn 1',), ('DEMO nguồn 2',))
        result = self.selector.doc(raw, '.PDF', ma_yeu_cau=str(uuid4()))
        bam = hashlib.sha256(raw).hexdigest()
        self.sdk.ocr_doc_luot.assert_called_once_with(bam_noi_dung=bam)
        self.sdk.ocr_giu_luot.assert_called_once_with(bam_noi_dung=bam, so_trang=2)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='da_tieu', phien_ban=7)
        self.assertEqual(thu_tu, ['Core đã commit', 'gửi ABBYY', 'chốt đã tiêu'])
        self.assertEqual((result.nguon_doc, len(result.pages)), ('ABBYY', 2))
        self.assertNotIn(self.ma, self.cong._giu_cho)
        self.mask.assert_not_called()

    def test_cau_noi_nhan_ma_core_khong_doi_seam_hot_folder(self):
        client = Mock(spec=KetNoiABBYY)
        client.san_sang.return_value = True
        client.doc_pdf.return_value = self.pdf
        selector = self.tao_chon(abbyy=abbyy.BackendKetNoiABBYY(ket_noi=client))
        selector.doc(self.raw, 'pdf', ma_yeu_cau=str(uuid4()))
        client.doc_pdf.assert_called_once_with(self.raw, 'pdf', huy=None, ma_yeu_cau=self.ma)
        self.assertEqual(self.cong._doc_so()[0][2], self.ma)

    def test_sdk_cu_thieu_thao_tac_giu_nguyen_backend_va_so_cu(self):
        class BackendCu:
            def san_sang(inner):
                return True

            def doc_pdf(inner, raw, duoi, *, huy=None):
                return self.backend.doc_pdf(raw, duoi, huy=huy)

        for sdk in (None, object(), Mock(spec=['doc_dau_vao'])):
            with self.subTest(sdk=type(sdk).__name__), \
                    patch.object(chon.kenh_khung, 'kiem_dto_ocr', None):
                selector = self.tao_chon(abbyy=BackendCu(), sdk=sdk)
                selector.doc(pdf_demo((f'DEMO seam cũ {self.so_trang()}',)), 'pdf')
        self.assertEqual(self.so_trang(), 3)
        self.assertEqual(self.backend.doc_pdf.call_count, 3)
        self.sdk.ocr_giu_luot.assert_not_called()
        self.assertTrue(all(row[2] != self.ma for row in self.cong._doc_so()))

    def test_luot_dang_giu_chua_ro_khong_gui_khong_fallback_khong_hoan(self):
        for status in ('dang_giu', 'chua_ro'):
            for san_sang in (False, True):
                with self.subTest(status=status, san_sang=san_sang):
                    self.sdk.ocr_doc_luot.return_value = dict(trang_thai=status, phien_ban=2)
                    self.backend.san_sang.return_value = san_sang
                    self.cho_doi_chieu()
        self.sdk.ocr_giu_luot.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()
        self.backend.doc_pdf.assert_not_called()
        self.mask.assert_not_called()
        self.assertEqual(self.so_trang(), 0)

    def test_core_chan_nguyen_tu_sau_doc_khong_tu_gui_lai(self):
        self.sdk.ocr_giu_luot.side_effect = LoiEngine('OCR_LUOT_DANG_BI_CHAN')
        self.cho_doi_chieu()
        self.sdk.ocr_giu_luot.assert_called_once()
        self.sdk.ocr_chot_luot.assert_not_called()
        self.backend.doc_pdf.assert_not_called()
        self.mask.assert_not_called()
        self.assertEqual(self.so_trang(), 0)

    def test_mat_phan_hoi_giu_sau_commit_khoi_dong_lai_van_chan(self):
        def mat_phan_hoi(**kw):
            self.sdk.ocr_doc_luot.return_value = dict(trang_thai='chua_ro', phien_ban=2)
            raise ConnectionResetError('DEMO kín sau commit')

        self.sdk.ocr_giu_luot.side_effect = mat_phan_hoi
        self.cho_doi_chieu()
        with patch.object(chon, '_LUOT_CHO', {}), patch.object(chon, '_LUOT_XONG', OrderedDict()):
            self.cho_doi_chieu(self.tao_chon(cong_ocr=self.tao_cong()))
        self.sdk.ocr_giu_luot.assert_called_once()
        self.sdk.ocr_chot_luot.assert_not_called()
        self.backend.doc_pdf.assert_not_called()
        self.assertEqual(self.so_trang(), 0)

    def test_phan_hoi_giu_khong_cap_quyen_gui_bi_chan_huu_han(self):
        mau = self.sdk.ocr_giu_luot.return_value
        for data in (None, {}, mau | {'trang_thai': 'chua_ro'},
                     mau | {'phien_ban': True}, mau | {'phien_ban': 0},
                     mau | {'ma_tuong_quan': '../DEMO kín'}, mau | {'bam_noi_dung': 'f' * 64}):
            with self.subTest(data=data):
                self.sdk.ocr_giu_luot.return_value = data
                self.cho_doi_chieu()
        self.backend.doc_pdf.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()
        self.mask.assert_not_called()
        self.assertEqual(self.so_trang(), 0)

    def test_doc_loi_hoac_sai_dto_khong_bien_thanh_quyen_gui(self):
        for exc in (ConnectionResetError('DEMO kín'), LoiEngine('VIEC_MAT_LEASE')):
            with self.subTest(exc=type(exc).__name__):
                self.sdk.ocr_doc_luot.side_effect = exc
                self.cho_doi_chieu()
        self.sdk.ocr_doc_luot.side_effect = None
        for data in (None, {}, dict(trang_thai='khong_co', phien_ban=1)):
            with self.subTest(data=data):
                self.sdk.ocr_doc_luot.return_value = data
                self.cho_doi_chieu()
        self.sdk.ocr_giu_luot.assert_not_called()
        self.backend.doc_pdf.assert_not_called()

    def test_da_tieu_khong_gui_lai_sau_khoi_dong_lai(self):
        self.selector.doc(self.raw, 'pdf')
        self.sdk.ocr_doc_luot.return_value = dict(trang_thai='da_tieu', phien_ban=8)
        with patch.object(chon, '_LUOT_CHO', {}), patch.object(chon, '_LUOT_XONG', OrderedDict()):
            with self.assertRaises(DataError) as bat:
                self.tao_chon(cong_ocr=self.tao_cong()).doc(self.raw, 'pdf')
        self.assertEqual(bat.exception.code, 'OCR_DA_XU_LY')
        self.backend.doc_pdf.assert_called_once()
        self.sdk.ocr_giu_luot.assert_called_once()
        self.assertEqual(self.so_trang(), 1)

    def test_mat_ket_noi_khong_biet_da_gui_giu_trang_khong_chot(self):
        errors = (TimeoutError('DEMO kín'), ConnectionResetError('DEMO kín'),
                  RuntimeError('DEMO kín'),
                  LoiKetNoiABBYY('ABBYY_CHUA_RO_DA_NHAN', chua_ro_da_nhan=True))
        for i, exc in enumerate(errors):
            with self.subTest(exc=type(exc).__name__):
                self.ma = str(uuid4())
                self.sdk.ocr_giu_luot.return_value = dict(
                    ma_tuong_quan=self.ma, trang_thai='dang_giu', phien_ban=7)
                self.raw = pdf_demo((f'DEMO tài liệu lỗi {i}',))
                self.backend.doc_pdf.side_effect = exc
                result = self.selector.doc(self.raw, 'pdf')
                self.assertEqual((result.nguon_doc, result.trang_thai_abbyy), ('mask_ocr', 'chua_ro'))
                self.assertEqual(result.ma_tuong_quan, self.ma)
        self.assertEqual(self.so_trang(), len(errors))
        self.sdk.ocr_chot_luot.assert_not_called()
        self.sdk.ocr_doc_luot.return_value = dict(trang_thai='chua_ro', phien_ban=2)
        self.cho_doi_chieu(self.tao_chon(cong_ocr=self.tao_cong()))
        self.assertEqual(self.backend.doc_pdf.call_count, len(errors))

    def test_hot_folder_chac_chan_chua_publish_chot_hoan(self):
        backend = ocr.HotFolderPDF(self.tmp / 'hot-folder-DEMO', bat=True, nghi=0.01)
        selector = self.tao_chon(abbyy=backend)
        # Giả lập thư mục vừa mất sau kiểm sẵn sàng: mở part thất bại trước publish.
        with patch.object(backend, 'san_sang', return_value=True):
            result = selector.doc(self.raw, 'pdf')
        self.assertEqual(result.nguon_doc, 'mask_ocr')
        self.assertIsNone(result.trang_thai_abbyy)
        self.assertEqual(self.so_trang(), 0)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='hoan_trang', phien_ban=7)

    def test_hot_folder_khong_co_bang_chung_rut_tep_khong_chot(self):
        backend = ocr.HotFolderPDF(self.tmp / 'hot-folder-DEMO', bat=True, nghi=0.01)
        selector = self.tao_chon(abbyy=backend)
        with patch.object(backend, 'san_sang', return_value=True), \
                patch.object(backend, '_van_chuyen', side_effect=TimeoutError('DEMO kín sau gửi')):
            result = selector.doc(self.raw, 'pdf')
        self.assertEqual(result.trang_thai_abbyy, 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_not_called()

    def kiem_huy_hot_folder(self, dau_vet):
        d = self.cong.thu_muc()
        backend = ocr.HotFolderPDF(self.cong.thu_muc_goc, bat=True,
                                  nghi=0.01, on_dinh=0.01, cho_nhan=1, cho_toi_da=2)
        selector = self.tao_chon(abbyy=backend)
        huy = threading.Event()
        doi_that, moves = ocr.os.replace, []
        liet_ke_that = Path.iterdir

        def liet_ke(tep):
            if dau_vet == 'khong_kiem_duoc' and tep == d['out']:
                raise PermissionError('DEMO không kiểm được output')
            return liet_ke_that(tep)

        def doi(src, dst):
            src, dst = Path(src), Path(dst)
            doi_that(src, dst)
            moves.append((src, dst))
            if dst.parent == d['in']:
                if dau_vet in ('nhan', 'out'):
                    # ABBYY trả PDF nhưng vẫn giữ input trong hàng chờ.
                    (d['out'] / dst.name).write_bytes(self.pdf)
                elif dau_vet == 'log':
                    (d['out'] / dst.with_suffix('.log').name).write_text(
                        'DEMO đã xử lý tài liệu', encoding='utf-8')
                if dau_vet != 'nhan':
                    huy.set()
            elif dst.parent == d['nhan']:
                huy.set()

        # Giữ nguyên _van_chuyen, _rut, giữ/hoàn sổ và toàn bộ selector.
        with patch.object(ocr.os, 'replace', side_effect=doi), \
                patch.object(Path, 'iterdir', liet_ke), \
                patch.object(backend, '_don_sau'), \
                patch.object(self.cong, '_hoan_trang', wraps=self.cong._hoan_trang) as hoan:
            with self.assertRaises(DataError) as bat:
                selector.doc(self.raw, 'pdf', huy=huy)

        self.assertEqual(bat.exception.code, 'OCR_HUY')
        inputs = [dst for src, dst in moves if dst.parent == d['in']]
        self.assertEqual(len(inputs), 1)
        self.assertIn((inputs[0], d['tam'] / inputs[0].with_suffix('.rut').name), moves)
        if dau_vet == 'nhan':
            self.assertIn((d['out'] / inputs[0].name, d['nhan'] / inputs[0].name), moves)
        self.sdk.ocr_giu_luot.assert_called_once()
        self.mask.assert_not_called()
        return bat.exception, hoan

    def kiem_huy_sau_nhan_khong_hoan(self):
        loi, hoan = self.kiem_huy_hot_folder('nhan')
        self.assertEqual(getattr(loi, 'trang_thai_abbyy', None), 'chua_ro')
        self.assertEqual(loi.ma_tuong_quan, self.ma)
        self.assertEqual(self.so_trang(), 1)
        hoan.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_hot_folder_huy_sau_chuyen_output_vao_nhan_rut_duoc_input_van_khong_hoan(self):
        self.kiem_huy_sau_nhan_khong_hoan()

    def test_hot_folder_huy_khi_input_chua_roi_hang_cho_khong_output_duoc_hoan(self):
        loi, hoan = self.kiem_huy_hot_folder('khong_co')
        self.assertIsNone(getattr(loi, 'trang_thai_abbyy', None))
        self.assertEqual(self.so_trang(), 0)
        hoan.assert_called_once_with(self.ma)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='hoan_trang', phien_ban=7)

    def test_hot_folder_huy_khi_co_output_chua_kip_doc_van_khong_hoan(self):
        loi, hoan = self.kiem_huy_hot_folder('out')
        self.assertEqual(getattr(loi, 'trang_thai_abbyy', None), 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        hoan.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_hot_folder_huy_khi_co_dau_vet_ma_tep_van_khong_hoan(self):
        loi, hoan = self.kiem_huy_hot_folder('log')
        self.assertEqual(getattr(loi, 'trang_thai_abbyy', None), 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        hoan.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_hot_folder_rut_duoc_nhung_khong_kiem_duoc_output_khong_hoan(self):
        loi, hoan = self.kiem_huy_hot_folder('khong_kiem_duoc')
        self.assertEqual(getattr(loi, 'trang_thai_abbyy', None), 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        hoan.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_hot_folder_ma_loi_chua_nhan_khong_thang_output_vua_den(self):
        d = self.cong.thu_muc()
        backend = ocr.HotFolderPDF(self.cong.thu_muc_goc, bat=True,
                                  nghi=0.01, on_dinh=0.01, cho_nhan=0.01, cho_toi_da=2)
        rut_that = backend._rut

        def rut(d, ma, duoi):
            da_rut = rut_that(d, ma, duoi)
            (d['out'] / (ma + '.pdf')).write_bytes(self.pdf)
            return da_rut

        with patch.object(backend, '_rut', side_effect=rut), \
                patch.object(backend, '_don_sau'), \
                patch.object(self.cong, '_hoan_trang', wraps=self.cong._hoan_trang) as hoan:
            result = self.tao_chon(abbyy=backend).doc(self.raw, 'pdf')
        self.assertEqual((result.nguon_doc, result.trang_thai_abbyy), ('mask_ocr', 'chua_ro'))
        self.assertEqual(self.so_trang(), 1)
        hoan.assert_not_called()
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_mutation_dieu_kien_rut_cu_bi_test_tich_hop_bat(self):
        source = textwrap.dedent(inspect.getsource(ocr._VanChuyenHotFolder._van_chuyen))
        dau = source.index('    finally:\n')
        don = source.index('        self._don(d, ma)', dau)
        source = (source[:dau] + '    finally:\n'
                  '        chua_nhan = not da_dua or self._rut(d, ma, duoi)\n' + source[don:])
        namespace = {}
        exec(compile(source, '<OCR-CR-4-mutation-DEMO>', 'exec'), vars(ocr), namespace)
        with patch.object(ocr._VanChuyenHotFolder, '_van_chuyen', namespace['_van_chuyen']), \
                self.assertRaisesRegex(AssertionError, "None != 'chua_ro'"):
            self.kiem_huy_sau_nhan_khong_hoan()

    def test_thoat_bat_thuong_sau_gui_khong_chot(self):
        self.backend.doc_pdf.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt) as bat:
            self.selector.doc(self.raw, 'pdf')
        self.assertEqual(bat.exception.trang_thai_abbyy, 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_not_called()
        self.mask.assert_not_called()

    def test_ket_qua_thieu_lop_chu_khong_chot_da_tieu_hoac_hoan(self):
        self.backend.doc_pdf.return_value = pdf_demo(())
        result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual(result.trang_thai_abbyy, 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_bang_chung_chua_gui_hoan_so_roi_chot_hoan(self):
        self.backend.doc_pdf.side_effect = LoiKetNoiABBYY('ABBYY_KHONG_KET_NOI', chua_ro_da_nhan=False)

        def chot(**kw):
            self.assertEqual(self.so_trang(), 0)
            return dict(trang_thai=kw['ket_qua'])

        self.sdk.ocr_chot_luot.side_effect = chot
        result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual(result.nguon_doc, 'mask_ocr')
        self.assertIsNone(result.trang_thai_abbyy)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='hoan_trang', phien_ban=7)

    def test_khong_du_han_muc_khong_gui_chot_hoan_dung_luot(self):
        self.cong._giu_trang(5000, 'DEMO nền')
        result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual(result.ma_ly_do_chuyen, 'het_han_muc')
        self.assertEqual(self.so_trang(), 5000)
        self.backend.doc_pdf.assert_not_called()
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='hoan_trang', phien_ban=7)

    def test_huy_sau_giu_truoc_gui_hoan_va_chot(self):
        huy = threading.Event()
        giu_trang = self.cong._giu_trang

        def giu(*args, **kw):
            giu_trang(*args, **kw)
            huy.set()

        with patch.object(self.cong, '_giu_trang', side_effect=giu):
            with self.assertRaises(DataError) as bat:
                self.selector.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual(bat.exception.code, 'OCR_HUY')
        self.assertEqual(self.so_trang(), 0)
        self.backend.doc_pdf.assert_not_called()
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='hoan_trang', phien_ban=7)

    def test_huy_sau_gui_khong_chot_khong_hoan(self):
        huy = threading.Event()

        def gui(*args, **kw):
            huy.set()
            return self.pdf

        self.backend.doc_pdf.side_effect = gui
        with self.assertRaises(DataError) as bat:
            self.selector.doc(self.raw, 'pdf', huy=huy)
        self.assertEqual((bat.exception.code, bat.exception.trang_thai_abbyy), ('OCR_HUY', 'chua_ro'))
        self.assertEqual(bat.exception.ma_tuong_quan, self.ma)
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_not_called()
        self.mask.assert_not_called()

    def test_chot_da_tieu_mat_phan_hoi_khong_thu_lai_hay_hoan(self):
        self.sdk.ocr_chot_luot.side_effect = ConnectionResetError('DEMO kín sau commit')
        result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual(result.trang_thai_abbyy, 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='da_tieu', phien_ban=7)

    def test_chot_hoan_loi_khong_suy_da_hoan_core(self):
        self.backend.doc_pdf.side_effect = LoiKetNoiABBYY('ABBYY_KHOA_SAI', chua_ro_da_nhan=False)
        self.sdk.ocr_chot_luot.side_effect = LoiEngine('OCR_LUOT_XUNG_DOT')
        result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual((result.trang_thai_abbyy, result.ma_tuong_quan), ('chua_ro', self.ma))
        self.assertEqual(self.so_trang(), 0)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=self.ma, ket_qua='hoan_trang', phien_ban=7)

    def test_so_chua_xac_nhan_hoan_khong_chot_hoan_core(self):
        self.backend.doc_pdf.side_effect = LoiKetNoiABBYY('ABBYY_KHOA_SAI', chua_ro_da_nhan=False)
        with patch.object(self.cong, '_hoan_trang', side_effect=OSError('DEMO kín')):
            result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual(result.trang_thai_abbyy, 'chua_ro')
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_not_called()

    def test_admin_doi_chieu_hoan_xong_ram_khong_chan_luot_moi(self):
        self.backend.doc_pdf.side_effect = TimeoutError('DEMO kín')
        self.selector.doc(self.raw, 'pdf')
        self.cong._hoan_trang(self.ma)  # Giả lập Admin đã đối chiếu sổ.
        self.sdk.ocr_doc_luot.return_value = dict(trang_thai='hoan_trang', phien_ban=8)
        ma_moi = str(uuid4())
        self.sdk.ocr_giu_luot.return_value = dict(
            ma_tuong_quan=ma_moi, trang_thai='dang_giu', phien_ban=1)
        self.backend.doc_pdf.side_effect = None
        result = self.selector.doc(self.raw, 'pdf')
        self.assertEqual(result.nguon_doc, 'ABBYY')
        self.assertEqual(self.so_trang(), 1)
        self.sdk.ocr_chot_luot.assert_called_once_with(
            ma_tuong_quan=ma_moi, ket_qua='da_tieu', phien_ban=1)

    def test_dong_thoi_trong_phien_khong_gui_hai_lan(self):
        da_gui, tiep_tuc = threading.Event(), threading.Event()

        def gui(*args, **kw):
            da_gui.set()
            if not tiep_tuc.wait(5):
                raise AssertionError('Lượt DEMO chưa được tiếp tục')
            return self.pdf

        self.backend.doc_pdf.side_effect = gui
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.selector.doc, self.raw, 'pdf')
            try:
                self.assertTrue(da_gui.wait(5))
                with self.assertRaises(DataError) as bat:
                    self.tao_chon(cong_ocr=self.tao_cong()).doc(self.raw, 'pdf')
                self.assertEqual(bat.exception.code, 'OCR_DANG_XU_LY')
                self.sdk.ocr_giu_luot.assert_called_once()
                self.backend.doc_pdf.assert_called_once()
            finally:
                tiep_tuc.set()
            self.assertEqual(future.result(timeout=5).nguon_doc, 'ABBYY')

    def test_ma_ben_doc_lai_so_khong_cong_trang_hai_lan_va_hoan_dung_dong(self):
        self.cong._giu_trang(3, 'DEMO khác')
        self.cong._giu_trang(2, self.ma, ma_ben=self.ma)
        rows = self.cong._doc_so()
        cong_moi = self.tao_cong()
        cong_moi._giu_trang(2, self.ma, ma_ben=self.ma)
        self.assertEqual(cong_moi._doc_so(), rows)
        cong_moi._hoan_trang(self.ma)
        self.assertEqual(self.so_trang(), 3)
        self.assertEqual(len(self.cong._doc_so()), 1)

    def test_ma_ben_trung_khac_so_trang_hoac_hai_dong_khong_duoc_sua_so(self):
        self.cong._giu_trang(1, self.ma, ma_ben=self.ma)
        for rows, so_trang in ((self.cong._doc_so(), 2), (self.cong._doc_so() * 2, 1)):
            with self.subTest(so_trang=so_trang):
                self.cong.tep_so_trang.write_text(json.dumps(rows), encoding='utf-8')
                with self.assertRaises(DataError):
                    self.tao_cong()._giu_trang(so_trang, self.ma, ma_ben=self.ma)
                self.assertEqual(self.cong._doc_so(), rows)


if __name__ == '__main__':
    unittest.main()
