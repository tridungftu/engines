"""MASK-6: seam Core DEMO và khung launcher cũ; không server/CSDL/Mask thật.

Ca danh mục/vé RAM đã bỏ được skip theo QĐ cuối e_mask §2.3/§5.3.
ACK, lease, lỗi trước bàn giao và xung đột vẫn kiểm qua luồng Core mới.
"""

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import traceback
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from engines.e_mask import chay
from engines.e_mask.vong_doi import VongDoiMask
from engines.e_mask.kho_qua_core import KhoQuaCore, LoiKhoQuaCore
from tests.test_g3_mask_5 import _kenh, _sdk, QD_BO_VONG_DOI
from engines.e_mask.tests.test_noi_core import KhoCoreGia
from tests.test_mask_kho import tai_nguyen_demo
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine


DEMO = b'DEMO_MASK6_CANARY'
RAW = 'DEMO 1.234.567 đồng, 01/11/2026'.encode('utf-8')
META = dict(bien_the='mask_demo', ma_contract='khung_mask_demo',
            phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
            revision_truoc=0, nguon=[])


class TienTrinhGia:
    def __init__(self):
        self.stdin = io.BytesIO()
        self.returncode = None
        self.so_dung = 0
        self.cho_thoat = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.so_dung += 1
        if not self.cho_thoat:
            self.returncode = 0

    def wait(self, timeout):
        if self.returncode is None:
            raise subprocess.TimeoutExpired('DEMO', timeout)
        return self.returncode


class KenhGia(KenhCore):
    def __init__(self):
        self.da_gui = threading.Event()
        self.nhan = threading.Event()
        self.luong = []
        self.raw = []
        self.loi_tam = False
        self.mat_lease = False

    def goi(self, operation, giu_viec, **payload):
        if operation == 'doc_dau_vao':
            return RAW
        if operation != 'ghi_ket_qua':
            raise AssertionError('Operation DEMO ngoài dự kiến')
        self.luong.append(payload['luong'])
        self.raw.append(payload['luong'].read())
        if self.mat_lease:
            raise LoiEngine('VIEC_MAT_LEASE')
        if self.loi_tam and len(self.luong) == 1:
            raise RuntimeError(DEMO.decode())
        self.da_gui.set()
        if not self.nhan.wait(3):
            raise LoiEngine('VIEC_MAT_LEASE')
        return {'ket_qua_id': 'DEMO_ACK'}




class VongDoiTest(unittest.TestCase):
    def setUp(self):
        self.kho = KhoCoreGia()
        self.enterContext(tai_nguyen_demo())
        self.proc = TienTrinhGia()
        self.mo = Mock(return_value=True)
        self.core_cho_dung = Mock(return_value=True)
        self.cap_khoa = Mock(side_effect=lambda stdin: (
            stdin.write(DEMO) == len(DEMO)))
        self.ready = Mock(return_value=True)

    def tao(self, **doi):
        cfg = dict(thu_muc_mask=Path(__file__).parent, cong=55006,
                   danh_muc_da_mo=self.mo, cho_phep_dung=self.core_cho_dung,
                   cap_khoa=self.cap_khoa, kiem_san_sang=self.ready)
        cfg.update(doi)
        return VongDoiMask(**cfg)

    def chay(self, **doi):
        khung = self.tao(**doi)
        with patch.object(chay.subprocess, 'Popen', return_value=self.proc):
            self.assertTrue(khung.khoi_dong())
        return khung

    def test_thieu_seam_vong_doi_khong_khoi_chay(self):
        for field in ('danh_muc_da_mo', 'cho_phep_dung'):
            for value in (None, False, 'DEMO'):
                with self.subTest(field=field, value=value), \
                        patch.object(chay.subprocess, 'Popen') as popen:
                    with self.assertRaisesRegex(chay.LoiMask, 'THIEU_SEAM_VONG_DOI'):
                        self.tao(**{field: value})
                    popen.assert_not_called()

    def test_vong_doi_cu_bi_khoa_khong_cap_khoa_hoac_spawn(self):
        # QĐ cuối e_mask §2.3/§5.3 bỏ bootstrap khóa và launcher nguồn ngoài.
        khung = self.tao()
        with patch.object(chay.subprocess, 'Popen') as popen:
            with self.assertRaises(chay.LoiMask) as bat:
                khung.khoi_dong()
        self.assertEqual(bat.exception.ma, 'MASK_LAUNCHER_DA_BO')
        self.assertIsInstance(khung, chay.TienTrinhMask)
        for seam in (popen, self.cap_khoa, self.ready, self.mo, self.core_cho_dung):
            seam.assert_not_called()
        self.assertEqual(self.proc.stdin.getvalue(), b'')

    def test_thieu_seam_khoa_khong_chay_nguon(self):
        khung = self.tao(cap_khoa=None)
        with patch.object(chay.subprocess, 'Popen') as popen:
            with self.assertRaisesRegex(chay.LoiMask, 'THIEU_SEAM_CAP_KHOA'):
                khung.khoi_dong()
            popen.assert_not_called()

    @unittest.skip(QD_BO_VONG_DOI)
    def test_danh_muc_khoa_cho_anh_mo_tai_may_chu(self):
        self.mo.return_value = False
        khung = self.chay()
        with self.assertRaisesRegex(chay.LoiMask, 'MASK_DANH_MUC_DANG_KHOA'):
            khung.giu_luot()
        self.assertEqual(self.proc.so_dung, 0)
        self.mo.return_value = True  # Giả lập Anh mở bằng UI tại máy chủ.
        ve = khung.giu_luot()
        khung.tra_luot(ve)
        self.assertEqual(self.proc.so_dung, 0)

    @unittest.skip(QD_BO_VONG_DOI)
    def test_danh_muc_mo_luc_ranh_khong_tu_dong(self):
        khung = self.chay()
        khung.ngung_accept()
        for _ in range(10):
            self.assertFalse(khung.drain())
        self.assertEqual(self.proc.so_dung, 0)
        self.core_cho_dung.assert_not_called()
        self.mo.assert_called_with(self.proc)
        self.mo.return_value = False  # Chỉ sau khi Anh đóng thủ công.
        self.assertTrue(khung.drain())
        self.assertEqual(self.proc.so_dung, 1)

    @unittest.skip(QD_BO_VONG_DOI)
    def test_dang_nhan_viec_chua_drain_ke_ca_danh_muc_khoa(self):
        self.mo.return_value = False
        khung = self.chay()
        self.assertFalse(khung.drain())
        self.mo.assert_not_called()
        khung.ngung_accept()
        self.assertTrue(khung.drain())

    @unittest.skip(QD_BO_VONG_DOI)
    def test_trang_thai_khong_ro_chan_drain_va_giu_luot(self):
        for value in (None, 0, 1, '', 'False', {}, []):
            with self.subTest(value=value):
                self.setUp()
                self.mo.return_value = value
                khung = self.chay()
                with self.assertRaisesRegex(chay.LoiMask, 'MASK_DANH_MUC_CHUA_RO'):
                    khung.giu_luot()
                khung.ngung_accept()
                self.assertFalse(khung.drain())
                self.assertEqual(self.proc.so_dung, 0)
                self.core_cho_dung.assert_not_called()

    @unittest.skip(QD_BO_VONG_DOI)
    def test_loi_doc_danh_muc_khong_lo_canary(self):
        khung = self.chay()
        self.mo.side_effect = RuntimeError(DEMO.decode())
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            try:
                khung.giu_luot()
            except chay.LoiMask as exc:
                self.assertEqual(exc.ma, 'MASK_DANH_MUC_CHUA_RO')
                output.write(''.join(traceback.format_exception(exc)))
                output.write(repr(exc) + repr(khung))
            else:
                self.fail('Phải chặn trạng thái danh mục lỗi')
            khung.ngung_accept()
            self.assertFalse(khung.drain())
        self.assertNotIn(DEMO.decode(), output.getvalue())
        self.assertEqual(self.proc.so_dung, 0)

    @unittest.skip(QD_BO_VONG_DOI)
    def test_core_chua_cho_dung_hoac_loi_khong_drain(self):
        for value in (False, None, 1, 'True', RuntimeError(DEMO.decode())):
            with self.subTest(value=type(value)):
                self.setUp()
                self.mo.return_value = False
                if isinstance(value, Exception):
                    self.core_cho_dung.side_effect = value
                else:
                    self.core_cho_dung.return_value = value
                khung = self.chay()
                khung.ngung_accept()
                self.assertFalse(khung.drain())
                self.assertEqual(self.proc.so_dung, 0)
                self.core_cho_dung.assert_called_once_with(self.proc)

    @unittest.skip(QD_BO_VONG_DOI)
    def test_nhieu_ben_dung_luot_phai_tra_du_ke_ca_danh_muc_dong(self):
        khung = self.chay()
        ve1, ve2 = khung.giu_luot(), khung.giu_luot()
        self.assertIsNot(ve1, ve2)
        self.mo.return_value = False
        khung.ngung_accept()
        for _ in range(10):
            self.assertFalse(khung.drain())
        khung.tra_luot(ve1)
        self.assertFalse(khung.drain())
        self.assertEqual(self.proc.so_dung, 0)
        khung.tra_luot(ve2)
        self.assertTrue(khung.drain())

    @unittest.skip(QD_BO_VONG_DOI)
    def test_ve_la_va_tra_hai_lan_khong_giai_phong_luot_khac(self):
        khung, khac = self.chay(), self.chay()
        ve, ve_khac = khung.giu_luot(), khac.giu_luot()
        for invalid in (object(), ve_khac, None, [], DEMO):
            with self.subTest(invalid=type(invalid)), self.assertRaisesRegex(
                    chay.LoiMask, 'MASK_LUOT_KHONG_HOP_LE'):
                khung.tra_luot(invalid)
        self.mo.return_value = False
        khung.ngung_accept()
        self.assertFalse(khung.drain())
        khung.tra_luot(ve)
        with self.assertRaisesRegex(chay.LoiMask, 'MASK_LUOT_KHONG_HOP_LE'):
            khung.tra_luot(ve)
        self.assertTrue(khung.drain())

    @unittest.skip(QD_BO_VONG_DOI)
    def test_khong_nhan_luot_truoc_start_sau_stop_hoac_process_chet(self):
        khung = self.tao()
        with self.assertRaisesRegex(chay.LoiMask, 'MASK_KHONG_NHAN_VIEC'):
            khung.giu_luot()
        khung = self.chay()
        self.proc.returncode = 7
        with self.assertRaisesRegex(chay.LoiMask, 'MASK_KHONG_NHAN_VIEC'):
            khung.giu_luot()
        self.proc.returncode = None
        khung.ngung_accept()
        with self.assertRaisesRegex(chay.LoiMask, 'MASK_KHONG_NHAN_VIEC'):
            khung.giu_luot()

    @unittest.skip(QD_BO_VONG_DOI)
    def test_drain_chua_start_va_drain_lap_lai(self):
        self.assertTrue(self.tao().drain())
        self.mo.return_value = False
        khung = self.chay()
        self.proc.cho_thoat = True
        khung.ngung_accept()
        self.assertFalse(khung.drain())
        self.assertFalse(khung.drain())
        self.assertEqual(self.proc.so_dung, 1)
        self.assertFalse(self.proc.stdin.closed)
        self.proc.returncode = 0
        self.assertTrue(khung.drain())
        self.assertTrue(khung.drain())
        self.assertEqual(self.proc.so_dung, 1)
        self.assertTrue(self.proc.stdin.closed)

    @unittest.skip(QD_BO_VONG_DOI)
    def test_dong_mo_lai_khong_dung_trang_thai_dong_cu(self):
        self.mo.return_value = False
        self.core_cho_dung.return_value = False
        khung = self.chay()
        khung.ngung_accept()
        self.assertFalse(khung.drain())
        self.mo.return_value = True
        self.core_cho_dung.return_value = True
        self.assertFalse(khung.drain())
        self.assertEqual(self.proc.so_dung, 0)

    @unittest.skip(QD_BO_VONG_DOI)
    def test_mo_lai_ngay_truoc_terminate_chan_dung(self):
        self.mo.side_effect = [False, True]
        khung = self.chay()
        khung.ngung_accept()
        self.assertFalse(khung.drain())
        self.assertEqual(self.proc.so_dung, 0)
        self.mo.side_effect = None
        self.mo.return_value = False
        self.assertTrue(khung.drain())

    @unittest.skip(QD_BO_VONG_DOI)
    def test_loi_khoi_dong_khong_tu_dong_danh_muc_mo_hoac_chua_ro(self):
        for mo in (True, None, RuntimeError(DEMO.decode())):
            with self.subTest(mo=type(mo)):
                self.setUp()
                if isinstance(mo, Exception):
                    self.mo.side_effect = mo
                else:
                    self.mo.return_value = mo
                khung = self.tao(kiem_san_sang=lambda *_: False)
                with patch.object(chay.subprocess, 'Popen', return_value=self.proc) as popen:
                    with self.assertRaisesRegex(chay.LoiMask, '^MASK_CHUA_SAN_SANG$'):
                        khung.khoi_dong()
                    self.assertEqual(self.proc.so_dung, 0)
                    self.assertFalse(khung.drain())
                    with self.assertRaisesRegex(chay.LoiMask, '^DA_KHOI_DONG$'):
                        khung.khoi_dong()
                    popen.assert_called_once()
                self.mo.side_effect = None
                self.mo.return_value = False
                self.assertTrue(khung.drain())

    @unittest.skip(QD_BO_VONG_DOI)
    def test_loi_khoi_dong_danh_muc_khoa_duoc_core_cho_thi_don(self):
        self.mo.return_value = False
        khung = self.tao(cap_khoa=lambda _: False)
        with patch.object(chay.subprocess, 'Popen', return_value=self.proc):
            with self.assertRaisesRegex(chay.LoiMask, '^CAP_KHOA_MASK_LOI$'):
                khung.khoi_dong()
        self.assertEqual(self.proc.so_dung, 1)
        self.assertTrue(self.proc.stdin.closed)
        self.assertTrue(khung.drain())

    @unittest.skip(QD_BO_VONG_DOI)
    def test_drain_va_dang_ky_luot_dung_cung_khoa(self):
        khung = self.chay()
        dang_doc, cho_doc, da_kiem = (threading.Event() for _ in range(3))
        ve, khoa_ranh, ket_qua = [], [], []
        def doc(proc):
            dang_doc.set()
            if not cho_doc.wait(3):
                raise RuntimeError('DEMO hết hạn chờ')
            return True
        self.mo.side_effect = doc
        def dung():
            ranh = khung._khoa.acquire(blocking=False)
            khoa_ranh.append(ranh)
            if ranh:
                khung._khoa.release()
            da_kiem.set()
            khung.ngung_accept()
            ket_qua.append(khung.drain())
        nhan = threading.Thread(target=lambda: ve.append(khung.giu_luot()))
        drain = threading.Thread(target=dung)
        nhan.start()
        try:
            self.assertTrue(dang_doc.wait(2))
            drain.start()
            self.assertTrue(da_kiem.wait(2))
            self.assertEqual(khoa_ranh, [False])
        finally:
            cho_doc.set()
            nhan.join(3)
            if drain.ident is not None:
                drain.join(3)
        self.assertFalse(nhan.is_alive() or drain.is_alive())
        self.assertEqual(len(ve), 1)
        self.assertEqual(ket_qua, [False])
        self.assertEqual(self.proc.so_dung, 0)
        khung.tra_luot(ve[0])
        self.mo.side_effect = None
        self.mo.return_value = False
        self.assertTrue(khung.drain())

    def test_ban_giao_retry_giu_cung_ket_qua_va_ma_yeu_cau_doc_lap(self):
        # Thay giữ vé RAM bằng hai yêu cầu Core độc lập (QĐ §2.3/§5.3).
        cac_kenh = [_kenh(), _kenh()]
        with patch.object(chay.time, 'sleep'):
            for kenh in cac_kenh:
                kenh.mat_ack = 1
                self.assertEqual(chay.xu_ly_viec(_sdk(kenh), goi_kho=self.kho),
                                 {'ket_qua_id': 'DEMO_ACK'})
                self.assertEqual(kenh.ban_giao[0], kenh.ban_giao[1])
                self.assertIs(kenh.luong[0], kenh.luong[1])
                self.assertTrue(kenh.luong[0].closed)
        ma = [json.loads(k.ban_giao[0][0])['ma_yeu_cau'] for k in cac_kenh]
        self.assertNotEqual(*ma)
        for kenh in cac_kenh:
            kq = json.loads(kenh.ban_giao[0][0])
            for field in ('het_han_sau_giay', 'luot_con_giu', 'danh_muc', 'ket_thuc_luot'):
                self.assertNotIn(field, kq)

    def test_chua_bao_thanh_cong_truoc_khi_core_ack(self):
        kenh = _kenh()
        da_gui, nhan = threading.Event(), threading.Event()
        goc, ket_qua, loi = kenh.goi, [], []
        def goi(operation, giu, **p):
            if operation == 'ghi_ket_qua':
                da_gui.set()
                if not nhan.wait(2):
                    raise AssertionError('Thiếu ACK DEMO')
            return goc(operation, giu, **p)
        kenh.goi = goi
        def viec():
            try:
                ket_qua.append(chay.xu_ly_viec(_sdk(kenh), goi_kho=self.kho))
            except Exception as exc:
                loi.append(exc)
        worker = threading.Thread(target=viec)
        worker.start()
        try:
            self.assertTrue(da_gui.wait(2))
            self.assertEqual(ket_qua, [])
            self.assertTrue(worker.is_alive())
        finally:
            nhan.set()
            worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertEqual(loi, [])
        self.assertEqual(ket_qua, [{'ket_qua_id': 'DEMO_ACK'}])
        self.assertTrue(kenh.luong[0].closed)

    def test_mat_lease_khong_coi_ket_qua_da_nhan(self):
        kenh = _kenh()
        kenh.mat_lease = True
        with patch.object(chay.time, 'sleep') as cho, self.assertRaises(chay.LoiMask) as bat:
            chay.xu_ly_viec(_sdk(kenh), goi_kho=self.kho)
        self.assertEqual(bat.exception.ma, 'VIEC_MAT_LEASE')
        self.assertEqual(len(kenh.ban_giao), 1)
        self.assertTrue(kenh.luong[0].closed)
        cho.assert_not_called()

    def test_loi_xu_ly_truoc_ban_giao_khong_tu_coi_da_xong(self):
        kenh = _kenh()
        with patch.object(chay.che_van_ban, 'che', side_effect=RuntimeError(DEMO.decode())):
            with self.assertRaises(chay.LoiMask) as bat:
                chay.xu_ly_viec(_sdk(kenh), goi_kho=self.kho)
        self.assertEqual(bat.exception.ma, 'MASK_XU_LY')
        self.assertEqual(kenh.ban_giao, [])
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot'])
        self.assertNotIn(DEMO.decode(), ''.join(traceback.format_exception(bat.exception)))
        self.assertIsNone(bat.exception.__context__)

    @unittest.skip('CHUA_KIEM: QĐ cuối e_mask §4, bài tổng thể qua Core do lead chạy; không gọi API thật trong test thuần.')
    def test_api_mask_v2_that(self):
        pass


class XungDotKhoTests(unittest.TestCase):
    def setUp(self):
        self.kho = KhoCoreGia()
        self.enterContext(tai_nguyen_demo())

    def _loi(self, *, ma=None, sqlstate=None):
        loi = RuntimeError(DEMO.decode())
        if ma is not None:
            loi.ma = ma
        if sqlstate is not None:
            loi.sqlstate = sqlstate
        return loi

    def _an(self, loi):
        self.assertNotIn(DEMO.decode(), ''.join(traceback.format_exception(loi)))
        self.assertIsNone(loi.__cause__)
        self.assertIsNone(loi.__context__)

    def test_port_phan_biet_xung_dot_lease_va_loi_khac(self):
        for thuoc_tinh, ma in (
                ({'sqlstate': '40001'}, 'MASK_XUNG_DOT_LUOT'),
                ({'sqlstate': '40P01'}, 'MASK_XUNG_DOT_LUOT'),
                ({'ma': 'MASK_XUNG_DOT_LUOT'}, 'MASK_XUNG_DOT_LUOT'),
                ({'ma': 'VIEC_MAT_LEASE', 'sqlstate': '40001'}, 'VIEC_MAT_LEASE'),
                ({'sqlstate': '42501'}, 'MASK_XU_LY'),
                ({'ma': DEMO.decode()}, 'MASK_XU_LY')):
            with self.subTest(thuoc_tinh=thuoc_tinh):
                goi = Mock(side_effect=self._loi(**thuoc_tinh))
                with self.assertRaises((LoiKhoQuaCore, LoiEngine)) as bat:
                    KhoQuaCore(goi_kho=goi, ma_yeu_cau=str(uuid4()),
                               ma_luot=str(uuid4()), loai='che')
                self.assertEqual(bat.exception.ma, ma)
                self._an(bat.exception)
                goi.assert_called_once()

    def test_function_xung_dot_chot_khong_tu_che_hoac_chot_lai(self):
        yc = json.loads(_kenh().raw)
        def goi(operation, **p):
            if operation == 'chot_luot':
                raise self._loi(sqlstate='40001')
            return self.kho(operation, **p)
        kenh_kho = Mock(side_effect=goi)
        with patch.object(chay.che_van_ban, 'che', wraps=chay.che_van_ban.che) as che:
            with self.assertRaises(chay.LoiMask) as bat:
                chay.xu_ly_function('mask.che_van_ban', yc, goi_kho=kenh_kho)
        self.assertEqual(bat.exception.ma, 'MASK_XUNG_DOT_LUOT')
        self._an(bat.exception)
        self.assertEqual(che.call_count, 1)
        self.assertEqual([g.args[0] for g in kenh_kho.call_args_list], ['snapshot_luot', 'chot_luot'])
        self.assertEqual(self.kho.da_chot, {})

    def test_viec_giu_ma_xung_dot_khong_gui_ket_qua(self):
        for cua in ('snapshot_luot', 'chot_luot'):
            with self.subTest(cua=cua):
                kenh = _kenh()
                def goi(operation, **p):
                    if operation == cua:
                        raise self._loi(ma='MASK_XUNG_DOT_LUOT')
                    return self.kho(operation, **p)
                with patch.object(chay.time, 'sleep') as cho:
                    with self.assertRaises(chay.LoiMask) as bat:
                        chay.xu_ly_viec(_sdk(kenh), goi_kho=goi)
                self.assertEqual(bat.exception.ma, 'MASK_XUNG_DOT_LUOT')
                self._an(bat.exception)
                self.assertEqual(kenh.ban_giao, [])
                cho.assert_not_called()

    def test_loi_chot_khac_van_la_loi_xu_ly_chung(self):
        kenh = _kenh()
        def goi(operation, **p):
            if operation == 'chot_luot':
                raise self._loi(sqlstate='42501')
            return self.kho(operation, **p)
        with self.assertRaises(chay.LoiMask) as bat:
            chay.xu_ly_viec(_sdk(kenh), goi_kho=goi)
        self.assertEqual(bat.exception.ma, 'MASK_XU_LY')
        self._an(bat.exception)
        self.assertEqual(kenh.ban_giao, [])


if __name__ == '__main__':
    unittest.main()
