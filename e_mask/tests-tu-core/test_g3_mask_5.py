"""MASK-5a: hồi quy luồng Core bằng mock, không mở mạng hay chạy tiến trình.

QĐ cuối e_mask §2.3/§5.3 bỏ launcher, khóa RAM và lượt có hạn.
Giữ kiểm ACK, heartbeat, lease bằng chay.xu_ly_viec thay khung tiến trình cũ.
"""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

from engines.e_mask import chay as mask
from engines.e_mask.tests.test_noi_core import KenhGia, KhoCoreGia
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.sdk_core.engine import LoiEngine, SDKEngine
from tests.test_mask_kho import tai_nguyen_demo

RAW = 'DEMO 1.234.567 đồng, 31/10/2026'
META = dict(bien_the='mask_demo', ma_contract='khung_mask_demo',
            phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
            revision_truoc=0, nguon=[])
QD_BO_VONG_DOI = ('docs/47-core/g3/QUYET-DINH-CUOI-e_mask.md §2.3, §5.3: bỏ mở/đóng danh mục, '
                  'khóa qua bộ nhớ và lượt có hạn; Core quản lý mã yêu cầu.')


def _sdk(kenh, dong_ho=None, *, lease_giay=120):
    giu = GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:MASK:LAP',
        instance_id=uuid4(), the_he=1, ma=MaBiMat('n' * 43),
        giu_den=(dong_ho() if dong_ho else datetime.now(timezone.utc))
        + timedelta(seconds=lease_giay))
    return SDKEngine(giu, kenh_core=kenh, dong_ho=dong_ho)


def _kenh():
    yc = dict(van_ban=RAW, ma_yeu_cau=str(uuid4()), ma_luot=str(uuid4()))
    envelope = dict(capability='mask.che_van_ban',
        yeu_cau={'tham_chieu_tep': {'tep_id': str(uuid4())}},
        du_lieu_ket_qua=META.copy(), revision_tep_truoc=0)
    return KenhGia(envelope, json.dumps(yc, ensure_ascii=False).encode('utf-8'))


class DongHoGia:
    """Điều khiển lịch heartbeat bằng Condition; không chờ 30/120 giây thật."""
    def __init__(self):
        self.gio = datetime(2026, 10, 31, tzinfo=timezone.utc)
        self.khoa = threading.Condition()
        self.da_cho = threading.Event()
        self.dung = False
        self.lich = []

    def __call__(self):
        with self.khoa:
            return self.gio

    def wait(self, giay):
        with self.khoa:
            den = self.gio + timedelta(seconds=giay)
            self.lich.append(giay)
            self.da_cho.set()
            self.khoa.wait_for(lambda: self.dung or self.gio >= den)
            return self.dung

    def set(self):
        with self.khoa:
            self.dung = True
            self.khoa.notify_all()

    def tang(self, giay=30):
        self.cho_nhip()
        with self.khoa:
            self.da_cho.clear()
            self.gio += timedelta(seconds=giay)
            self.khoa.notify_all()
        self.cho_nhip()

    def cho_nhip(self):
        if not self.da_cho.wait(2):
            raise AssertionError('Thiếu lịch heartbeat khi giữ việc')

    def seam_threading(self):
        gia = MagicMock(wraps=threading)
        gia.Event.side_effect = [self, threading.Event()]
        return gia


class MaskTest(unittest.TestCase):
    def setUp(self):
        self.kho = KhoCoreGia()
        self.enterContext(tai_nguyen_demo())

    def _tao(self, **doi):
        cfg = dict(thu_muc_mask=Path(__file__).parent, cong=19357,
                   cap_khoa=Mock(return_value=True), kiem_san_sang=Mock(return_value=True),
                   cho_phep_dung=Mock(return_value=True))
        cfg.update(doi)
        return mask.TienTrinhMask(**cfg)

    def _chay(self, kenh, **sdk_cfg):
        return mask.xu_ly_viec(_sdk(kenh, **sdk_cfg), goi_kho=self.kho)

    def _chan(self, ma, **doi):
        khung = self._tao(**doi)
        with patch.object(mask.subprocess, 'Popen') as spawn:
            with self.assertRaises(mask.LoiMask) as bat:
                khung.khoi_dong()
        self.assertEqual(bat.exception.ma, ma)
        spawn.assert_not_called()
        return khung

    def test_thieu_seam_khoa_chan_truoc_khi_chay_nguon(self):
        for seam in (None, False, 'DEMO'):
            with self.subTest(seam=seam):
                self._chan('THIEU_SEAM_CAP_KHOA', cap_khoa=seam)

    def test_thieu_kiem_vong_doi_khong_chay(self):
        for field in ('kiem_san_sang', 'cho_phep_dung'):
            with self.subTest(field=field):
                self._chan('THIEU_SEAM_VONG_DOI', **{field: None})

    def test_cong_sai_khong_chay(self):
        for cong in (True, 0, 1023, 65536, '1234'):
            with self.subTest(cong=cong), self.assertRaises(mask.LoiMask) as bat:
                self._tao(cong=cong)
            self.assertEqual(bat.exception.ma, 'CONG_KHONG_HOP_LE')

    def test_launcher_cu_bi_khoa_ke_ca_du_seam_khong_cap_khoa(self):
        # Thay ca spawn + truyền khóa stdin cũ, theo QĐ §2.3/§5.3.
        cap, ready, stop = (Mock(return_value=True) for _ in range(3))
        self._chan('MASK_LAUNCHER_DA_BO', cap_khoa=cap,
                   kiem_san_sang=ready, cho_phep_dung=stop)
        for seam in (cap, ready, stop):
            seam.assert_not_called()

    def test_readiness_sai_va_cap_khoa_loi_van_chan_truoc_callback(self):
        for field in ('kiem_san_sang', 'cap_khoa'):
            for ket_qua in (False, RuntimeError('DEMO_SECRET_EXCEPTION')):
                callback = Mock(side_effect=ket_qua) if isinstance(ket_qua, Exception) else Mock(return_value=ket_qua)
                with self.subTest(field=field, kieu=type(ket_qua).__name__):
                    self._chan('MASK_LAUNCHER_DA_BO', **{field: callback})
                    callback.assert_not_called()

    def test_khong_thu_cong_hoac_chay_nguon_ke_ca_goi_lai_launcher(self):
        # Thay ca listener chiếm cổng; launcher bỏ nên không mở socket thử cổng.
        khung = self._tao()
        with patch.object(mask.subprocess, 'Popen') as spawn:
            for _ in range(2):
                with self.assertRaises(mask.LoiMask) as bat:
                    khung.khoi_dong()
                self.assertEqual(bat.exception.ma, 'MASK_LAUNCHER_DA_BO')
        spawn.assert_not_called()

    def test_giu_cung_luong_den_ack_ke_ca_retry(self):
        kenh = _kenh()
        kenh.mat_ack = 1
        da_gui, nhan = threading.Event(), threading.Event()
        goc = kenh.goi
        ket_qua, loi = [], []

        def goi(operation, giu, **p):
            if operation == 'ghi_ket_qua' and kenh.ban_giao:
                da_gui.set()
                if not nhan.wait(2):
                    raise AssertionError('Thiếu ACK DEMO')
            return goc(operation, giu, **p)

        kenh.goi = goi
        def viec():
            try:
                ket_qua.append(self._chay(kenh))
            except Exception as exc:
                loi.append(exc)

        with patch.object(mask.time, 'sleep'), patch.object(
                mask.che_van_ban, 'che', wraps=mask.che_van_ban.che) as che:
            worker = threading.Thread(target=viec)
            worker.start()
            try:
                self.assertTrue(da_gui.wait(2))
                self.assertEqual(ket_qua, [])
                self.assertFalse(kenh.luong[0].closed)
            finally:
                nhan.set()
                worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertEqual(loi, [])
        self.assertEqual(ket_qua, [{'ket_qua_id': 'DEMO_ACK'}])
        self.assertEqual(che.call_count, 1)
        self.assertEqual(kenh.ban_giao[0], kenh.ban_giao[1])
        self.assertIs(kenh.luong[0], kenh.luong[1])
        self.assertTrue(kenh.luong[0].closed)
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot', 'chot_luot'])

    def test_heartbeat_tiep_tuc_qua_han_lease_ban_dau(self):
        dong_ho, kenh = DongHoGia(), _kenh()
        goc, nhip = kenh.goi, []
        bat_dau = dong_ho()
        def goi(operation, giu, **p):
            if operation == 'heartbeat':
                nhip.append(dong_ho())
                return replace(giu, giu_den=dong_ho() + timedelta(seconds=120))
            if operation == 'ghi_ket_qua':
                for _ in range(5):
                    dong_ho.tang()
            return goc(operation, giu, **p)
        kenh.goi = goi
        with patch.object(mask, 'threading', dong_ho.seam_threading()):
            self.assertEqual(self._chay(kenh, dong_ho=dong_ho), {'ket_qua_id': 'DEMO_ACK'})
        self.assertGreater(dong_ho(), bat_dau + timedelta(seconds=120))
        self.assertEqual(len(nhip), 6)
        self.assertEqual(len(kenh.ban_giao), 1)
        self.assertTrue(kenh.luong[0].closed and dong_ho.dung)

    def test_lease_con_10_giay_xu_ly_15_giay_gia_han_truoc_xu_ly(self):
        dong_ho, kenh = DongHoGia(), _kenh()
        goc, xu_ly = kenh.goi, mask.xu_ly_function
        def goi(operation, giu, **p):
            if operation == 'heartbeat':
                return replace(giu, giu_den=dong_ho() + timedelta(seconds=120))
            return goc(operation, giu, **p)
        kenh.goi = goi
        def cham(*args, **kwargs):
            self.assertEqual(kenh.operations, ['doc_dau_vao', 'mo_doc'])
            with dong_ho.khoa:
                dong_ho.gio += timedelta(seconds=15)
            return xu_ly(*args, **kwargs)
        with patch.object(mask, 'threading', dong_ho.seam_threading()), \
                patch.object(mask, 'xu_ly_function', side_effect=cham):
            self.assertEqual(self._chay(kenh, dong_ho=dong_ho, lease_giay=10),
                             {'ket_qua_id': 'DEMO_ACK'})
        self.assertEqual(len(kenh.ban_giao), 1)
        self.assertTrue(dong_ho.dung)

    def test_lich_heartbeat_thu_lai_sau_loi_tam(self):
        dong_ho, kenh = DongHoGia(), _kenh()
        goc, xu_ly, nhip = kenh.goi, mask.xu_ly_function, []
        def goi(operation, giu, **p):
            if operation == 'heartbeat':
                nhip.append(dong_ho())
                if len(nhip) == 2:
                    raise RuntimeError('DEMO_HEARTBEAT_TAM_LOI')
                return replace(giu, giu_den=dong_ho() + timedelta(seconds=120))
            return goc(operation, giu, **p)
        kenh.goi = goi
        def cham(*args, **kwargs):
            for cho in (30, 1, 30):
                dong_ho.cho_nhip()
                self.assertEqual(dong_ho.lich[-1], cho)
                dong_ho.tang(cho)
            return xu_ly(*args, **kwargs)
        with patch.object(mask, 'threading', dong_ho.seam_threading()), \
                patch.object(mask, 'xu_ly_function', side_effect=cham):
            self.assertEqual(self._chay(kenh, dong_ho=dong_ho), {'ket_qua_id': 'DEMO_ACK'})
        self.assertEqual(len(nhip), 4)
        self.assertTrue(dong_ho.dung)

    def test_heartbeat_khi_xu_ly_hoac_cho_ack_bi_chan(self):
        for giai_doan in ('xu_ly', 'cho_ack'):
            with self.subTest(giai_doan=giai_doan):
                dong_ho, kenh = DongHoGia(), _kenh()
                goc, xu_ly, nhip = kenh.goi, mask.xu_ly_function, []
                def goi(operation, giu, **p):
                    if operation == 'heartbeat':
                        nhip.append(dong_ho())
                        return replace(giu, giu_den=dong_ho() + timedelta(seconds=120))
                    if operation == 'ghi_ket_qua' and giai_doan == 'cho_ack':
                        dong_ho.tang()
                    return goc(operation, giu, **p)
                kenh.goi = goi
                def cham(*args, **kwargs):
                    if giai_doan == 'xu_ly':
                        dong_ho.tang()
                    return xu_ly(*args, **kwargs)
                with patch.object(mask, 'threading', dong_ho.seam_threading()), \
                        patch.object(mask, 'xu_ly_function', side_effect=cham):
                    self.assertEqual(self._chay(kenh, dong_ho=dong_ho), {'ket_qua_id': 'DEMO_ACK'})
                self.assertEqual(len(nhip), 2)
                self.assertTrue(dong_ho.dung and kenh.luong[0].closed)

    def test_mat_lease_dung_retry_dung_ma(self):
        for noi in ('doc_dau_vao', 'ghi_ket_qua', 'heartbeat', 'het_han_cuc_bo'):
            with self.subTest(noi=noi):
                kenh, dong_ho = _kenh(), DongHoGia()
                goc, go = kenh.goi, []
                def goi(operation, giu, **p):
                    go.append(operation)
                    if operation == noi:
                        raise LoiEngine('VIEC_MAT_LEASE')
                    if operation == 'heartbeat':
                        return replace(giu, giu_den=dong_ho() + timedelta(seconds=120))
                    return goc(operation, giu, **p)
                kenh.goi = goi
                sdk = _sdk(kenh, dong_ho)
                if noi == 'het_han_cuc_bo':
                    dong_ho.gio += timedelta(seconds=121)
                with patch.object(mask.time, 'sleep') as cho, \
                        self.assertRaises(mask.LoiMask) as bat:
                    mask.xu_ly_viec(sdk, goi_kho=self.kho)
                self.assertEqual(bat.exception.ma, 'VIEC_MAT_LEASE')
                self.assertLessEqual(go.count('ghi_ket_qua'), 1)
                self.assertEqual(kenh.ban_giao, [])
                cho.assert_not_called()
                if noi == 'het_han_cuc_bo':
                    self.assertEqual(go, [])

    @unittest.skip(QD_BO_VONG_DOI)
    def test_danh_muc_mo_va_luot_con_dung_chan_drain(self):
        pass

    def test_loi_truoc_ack_khong_cong_bo_ket_qua(self):
        kenh = _kenh()
        with patch.object(mask.che_van_ban, 'che', side_effect=RuntimeError('DEMO_SECRET_EXCEPTION')):
            with self.assertRaises(mask.LoiMask) as bat:
                self._chay(kenh)
        self.assertEqual(bat.exception.ma, 'MASK_XU_LY')
        self.assertEqual(kenh.ban_giao, [])
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot'])

    def test_het_tran_gui_dong_luong_va_khong_ngu_sau_lan_cuoi(self):
        kenh, dong_ho = _kenh(), DongHoGia()
        kenh.mat_ack = 100
        with patch.object(mask, 'threading', dong_ho.seam_threading()), \
                patch.object(mask.time, 'sleep') as cho, self.assertRaises(mask.LoiMask) as bat:
            self._chay(kenh, dong_ho=dong_ho)
        self.assertEqual(bat.exception.ma, 'MASK_BAN_GIAO_CHUA_XAC_NHAN')
        self.assertEqual(len(kenh.ban_giao), mask.MAX_LAN_GUI_KET_QUA)
        self.assertEqual(cho.call_count, mask.MAX_LAN_GUI_KET_QUA - 1)
        self.assertTrue(all(s is kenh.luong[0] and s.closed for s in kenh.luong))
        self.assertTrue(all(kq == kenh.ban_giao[0] for kq in kenh.ban_giao))
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot', 'chot_luot'])
        self.assertTrue(dong_ho.dung)

    def test_core_rut_han_lease_dung_gui_khi_da_het_han(self):
        # SDK chưa công khai hạn mới để bám lịch Core 1/10 giây.
        # Giữ kiểm chặn an toàn khi hết hạn; không coi đây là kiểm gia hạn kịp.
        for han_moi in (1, 10):
            with self.subTest(han_moi=han_moi):
                kenh, dong_ho = _kenh(), DongHoGia()
                goc, xu_ly, nhip = kenh.goi, mask.xu_ly_function, []
                def goi(operation, giu, **p):
                    if operation == 'heartbeat':
                        nhip.append(True)
                        return replace(giu, giu_den=dong_ho() + timedelta(seconds=han_moi))
                    return goc(operation, giu, **p)
                kenh.goi = goi
                def cham(*args, **kwargs):
                    dong_ho.cho_nhip()
                    with dong_ho.khoa:
                        dong_ho.gio += timedelta(seconds=han_moi + 1)
                        dong_ho.khoa.notify_all()
                    return xu_ly(*args, **kwargs)
                with patch.object(mask, 'threading', dong_ho.seam_threading()), \
                        patch.object(mask, 'xu_ly_function', side_effect=cham):
                    with self.assertRaises(mask.LoiMask) as bat:
                        self._chay(kenh, dong_ho=dong_ho)
                self.assertEqual(bat.exception.ma, 'VIEC_MAT_LEASE')
                self.assertEqual(len(nhip), 1)
                self.assertEqual(kenh.ban_giao, [])
                self.assertTrue(dong_ho.dung)

    def test_mat_lease_tu_heartbeat_dung_retry_va_don_thread(self):
        kenh, dong_ho = _kenh(), DongHoGia()
        mat = threading.Event()
        proxy = dong_ho.seam_threading()
        proxy.Event.side_effect = [dong_ho, mat]
        kenh.mat_ack = 100
        goc, nhip = kenh.goi, []
        def goi(operation, giu, **p):
            if operation == 'heartbeat':
                nhip.append(True)
                if len(nhip) == 2:
                    raise LoiEngine('VIEC_MAT_LEASE')
                return replace(giu, giu_den=dong_ho() + timedelta(seconds=120))
            return goc(operation, giu, **p)
        kenh.goi = goi
        def cho(_):
            dong_ho.cho_nhip()
            with dong_ho.khoa:
                dong_ho.gio += timedelta(seconds=30)
                dong_ho.khoa.notify_all()
            self.assertTrue(mat.wait(2))
        with patch.object(mask, 'threading', proxy), patch.object(mask.time, 'sleep', side_effect=cho):
            with self.assertRaises(mask.LoiMask) as bat:
                self._chay(kenh, dong_ho=dong_ho)
        self.assertEqual(bat.exception.ma, 'VIEC_MAT_LEASE')
        self.assertEqual(len(kenh.ban_giao), 1)
        self.assertTrue(dong_ho.dung and kenh.luong[0].closed)

    def test_ack_lan_cuoi_van_thanh_cong(self):
        kenh = _kenh()
        kenh.mat_ack = mask.MAX_LAN_GUI_KET_QUA - 1
        with patch.object(mask.time, 'sleep') as cho:
            self.assertEqual(self._chay(kenh), {'ket_qua_id': 'DEMO_ACK'})
        self.assertEqual(len(kenh.ban_giao), mask.MAX_LAN_GUI_KET_QUA)
        self.assertEqual(cho.call_count, mask.MAX_LAN_GUI_KET_QUA - 1)
        self.assertTrue(kenh.luong[0].closed)

    def test_phat_lai_sau_het_tran_khong_che_hoac_chot_lai(self):
        kenh = _kenh()
        kenh.mat_ack = 100
        with patch.object(mask.time, 'sleep'), self.assertRaises(mask.LoiMask):
            self._chay(kenh)
        cu = kenh.ban_giao[0]
        self.kho.cac_goi.clear()
        kenh.mat_ack = 0
        with patch.object(mask.che_van_ban, 'che') as che:
            self.assertEqual(self._chay(kenh), {'ket_qua_id': 'DEMO_ACK'})
        che.assert_not_called()
        self.assertEqual(kenh.ban_giao[-1], cu)
        self.assertIsNone(self.kho.cac_goi[-1][1]['nhat_ky'])


if __name__ == '__main__':
    unittest.main()
