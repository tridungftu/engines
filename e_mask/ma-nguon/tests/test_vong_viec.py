"""MASK-J8: hàng việc/kho DEMO trong RAM; không PG, mạng hay server."""
import ast
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import logging
from pathlib import Path
import re
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from engines.e_mask import chay
from engines.e_mask.tests.test_noi_core import (
    CHE, META, GiuViec, KenhGia, KhoCoreGia, MaBiMat,
)
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine
from tests.test_mask_kho import TEN, VAN_BAN, tai_nguyen_demo


def viec_demo():
    giu = GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:MASK:LAP',
        instance_id=uuid4(), the_he=1, ma=MaBiMat('n' * 43),
        giu_den=datetime.now(timezone.utc) + timedelta(seconds=120))
    yc = dict(van_ban=VAN_BAN, ma_yeu_cau=str(uuid4()), ma_luot=str(uuid4()))
    envelope = dict(capability=CHE, yeu_cau={'tham_chieu_tep': {'tep_id': str(uuid4())}},
                    du_lieu_ket_qua=deepcopy(META), revision_tep_truoc=0)
    kenh = KenhGia(envelope, json.dumps(yc, ensure_ascii=False).encode('utf-8'))
    return SimpleNamespace(giu=giu, yc=yc, kenh=kenh, kho=KhoCoreGia(), ket_qua_id=None)


class HangGia(KenhCore):
    def __init__(self, cac_viec, dung):
        self.cac_viec, self.dung = list(cac_viec), dung
        self.hien_tai = None
        self.da_nhan, self.da_xong, self.ket_thuc_goi, self.kho_goi = [], [], [], []
        self.chua_ket_thuc = []
        self.ket_thuc_loi = []
        self.khi_nhan = self.khi_kho = None

    def nhan_viec(self):
        # Core nhận việc mới được cả khi lease cũ đang chờ thu hồi/khôi phục.
        if self.hien_tai is not None:
            self.chua_ket_thuc.append(self.hien_tai)
            self.hien_tai = None
        if not self.cac_viec:
            return None
        self.hien_tai = self.cac_viec.pop(0)
        self.da_nhan.append(self.hien_tai)
        if self.khi_nhan:
            self.khi_nhan()
        return self.hien_tai.giu

    def goi(self, operation, giu_viec, **payload):
        assert giu_viec.viec_id == self.hien_tai.giu.viec_id
        try:
            return self.hien_tai.kenh.goi(operation, giu_viec, **payload)
        finally:
            if (operation == 'ghi_ket_qua' and self.hien_tai.kenh.ban_giao
                    and not self.hien_tai.kenh.mat_lease):
                # Mô phỏng commit trước ACK, kể cả khi ACK không tới engine.
                self.hien_tai.ket_qua_id = 'DEMO_ACK'

    def goi_mask(self, operation, giu, **payload):
        assert giu is self.hien_tai.giu
        self.kho_goi.append((giu, operation, deepcopy(payload)))
        if self.khi_kho:
            self.khi_kho(operation, payload)
        return self.hien_tai.kho(operation, **payload)

    def ket_thuc(self, giu, **payload):
        assert giu is self.hien_tai.giu
        self.ket_thuc_goi.append((giu, payload))
        trang_thai, ket_qua_id, ma_loi = (
            payload['trang_thai'], payload['ket_qua_id'], payload['ma_loi'])
        if (ket_qua_id != self.hien_tai.ket_qua_id
                or (trang_thai == 'XONG' and ket_qua_id is None)):
            raise LoiEngine('KENH_KHONG_DU_QUYEN')
        if (trang_thai not in {'XONG', 'LOI', 'DA_DUNG', 'CHUA_RO', 'CHO'}
                or (trang_thai in {'LOI', 'CHUA_RO', 'CHO'} and ma_loi is None)
                or (ma_loi is not None and (not isinstance(ma_loi, str)
                    or not re.fullmatch('[A-Z][A-Z0-9_]{0,79}', ma_loi)))
                or (trang_thai != 'XONG' and ket_qua_id is not None)):
            raise ValueError('Kết luận lần thử không hợp lệ')
        if self.ket_thuc_loi:
            loi = self.ket_thuc_loi.pop(0)
            if isinstance(loi, Exception):
                raise loi
            if loi is not True:
                return loi
        self.da_xong.append(self.hien_tai)
        self.hien_tai = None
        if not self.cac_viec:
            self.dung.set()
        return True


class VongViecTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(tai_nguyen_demo())
        self.dung = threading.Event()
        self.sleep = self.enterContext(patch.object(chay.time, 'sleep'))

        def gioi_han_cho(_):
            self.assertLessEqual(self.sleep.call_count, 20,
                                 'Vòng chạy lặp vô hạn sau khi Core từ chối kết thúc.')

        self.sleep.side_effect = gioi_han_cho

    def chay(self, *cac_viec, kenh=None):
        kenh = HangGia(cac_viec, self.dung) if kenh is None else kenh
        chay.chay_vong(kenh, goi_kho=kenh.goi_mask, dung=self.dung)
        return kenh

    def test_hai_viec_lien_tiep_ack_roi_ket_thuc_tung_lease(self):
        a, b = viec_demo(), viec_demo()
        kenh = self.chay(a, b)
        self.assertEqual(kenh.da_xong, [a, b])
        self.assertIsNone(kenh.hien_tai)
        for viec, (giu, p) in zip((a, b), kenh.ket_thuc_goi):
            self.assertIs(giu, viec.giu)
            self.assertEqual(p, dict(trang_thai='XONG', ket_qua_id='DEMO_ACK', ma_loi=None))
            self.assertEqual(viec.kenh.operations[-1], 'ghi_ket_qua')
            self.assertTrue(viec.kenh.luong[0].closed)
        self.assertEqual([p['ma_luot'] for _, op, p in kenh.kho_goi if op == 'snapshot_luot'],
                         [a.yc['ma_luot'], b.yc['ma_luot']])

    def test_viec_loi_dau_vao_ket_thuc_loi_viec_sau_van_xong(self):
        a, b = viec_demo(), viec_demo()
        a.kenh.raw = b'{'
        kenh = self.chay(a, b)
        self.assertEqual(kenh.da_xong, [a, b])
        self.assertEqual(kenh.ket_thuc_goi[0][1], dict(
            trang_thai='LOI', ket_qua_id=None, ma_loi='MASK_XU_LY'))
        self.assertEqual(kenh.ket_thuc_goi[1][1]['trang_thai'], 'XONG')

    def test_dung_trong_luc_xu_ly_van_ack_ket_thuc_khong_nhan_viec_sau(self):
        a, b = viec_demo(), viec_demo()
        kenh = HangGia([a, b], self.dung)
        kenh.khi_kho = lambda op, p: self.dung.set()
        self.chay(kenh=kenh)
        self.assertEqual(kenh.da_xong, [a])
        self.assertEqual(kenh.cac_viec, [b])
        self.assertEqual(kenh.ket_thuc_goi[0][1]['trang_thai'], 'XONG')

    def test_dung_den_cung_luc_nhan_khong_bo_lease(self):
        kenh = HangGia([viec_demo(), viec_demo()], self.dung)
        kenh.khi_nhan = self.dung.set
        self.chay(kenh=kenh)
        self.assertEqual(len(kenh.da_nhan), 1)
        self.assertEqual(len(kenh.da_xong), 1)
        self.assertIsNone(kenh.hien_tai)

    def test_da_dung_khong_nhan(self):
        kenh = HangGia([viec_demo()], self.dung)
        self.dung.set()
        self.chay(kenh=kenh)
        self.assertEqual(kenh.da_nhan, [])

    def test_hang_rong_cho_co_gioi_han_khong_quay_vong_ban(self):
        kenh = HangGia([], self.dung)
        da_cho = []

        def cho(han):
            da_cho.append(han)
            if len(da_cho) == 3:
                self.dung.set()
            return self.dung.is_set()

        with patch.object(self.dung, 'wait', side_effect=cho), \
                patch.object(kenh, 'nhan_viec', wraps=kenh.nhan_viec) as nhan:
            self.chay(kenh=kenh)
        self.assertEqual(nhan.call_count, 3)
        self.assertEqual(da_cho, [chay.CHO_NHAN_VIEC_GIAY] * 3)
        self.assertTrue(all(0 < han <= 1 for han in da_cho))

    def test_chua_san_sang_cho_roi_nhan_lai(self):
        kenh = HangGia([viec_demo()], self.dung)
        loi = LoiEngine('CHUA_SAN_SANG')
        loi.thu_lai_duoc = True
        nhan_that = kenh.nhan_viec
        lan_nhan = []

        def nhan():
            lan_nhan.append(True)
            if len(lan_nhan) == 1:
                raise loi
            return nhan_that()

        with patch.object(kenh, 'nhan_viec', side_effect=nhan), \
                patch.object(self.dung, 'wait', return_value=False) as cho:
            self.chay(kenh=kenh)
        cho.assert_called_once_with(chay.CHO_NHAN_VIEC_GIAY)
        self.assertEqual(len(kenh.da_xong), 1)

    def test_xung_dot_thu_lai_cung_ma_luot_snapshot_moi(self):
        a = viec_demo()
        kenh = HangGia([a], self.dung)
        so_chot = []

        def xung_dot(op, p):
            if op == 'chot_luot':
                so_chot.append(True)
                if len(so_chot) < chay.MAX_LAN_XU_LY:
                    a.kho.snap['phien_ban'] = str(len(so_chot))
                    raise LoiEngine('MASK_XUNG_DOT_LUOT')

        kenh.khi_kho = xung_dot
        self.chay(kenh=kenh)
        self.assertEqual(len(so_chot), chay.MAX_LAN_XU_LY)
        snaps = [p for _, op, p in kenh.kho_goi if op == 'snapshot_luot']
        self.assertEqual(len(snaps), chay.MAX_LAN_XU_LY)
        self.assertTrue(all(p['ma_luot'] == a.yc['ma_luot'] for p in snaps))
        self.assertEqual(len(a.kenh.ban_giao), 1)
        self.assertEqual(kenh.ket_thuc_goi[0][1]['trang_thai'], 'XONG')

    def test_xung_dot_het_ba_luot_ket_thuc_loi_roi_chay_viec_sau(self):
        a, b = viec_demo(), viec_demo()
        kenh = HangGia([a, b], self.dung)

        def xung_dot(op, p):
            if kenh.hien_tai is a:
                raise LoiEngine('MASK_XUNG_DOT_LUOT')

        kenh.khi_kho = xung_dot
        self.chay(kenh=kenh)
        self.assertEqual(sum(giu is a.giu for giu, _, _ in kenh.kho_goi), chay.MAX_LAN_XU_LY)
        self.assertEqual(kenh.ket_thuc_goi[0][1], dict(
            trang_thai='LOI', ket_qua_id=None, ma_loi='MASK_XUNG_DOT_LUOT'))
        self.assertEqual(kenh.da_xong, [a, b])
        self.assertEqual(kenh.ket_thuc_goi[1][1]['trang_thai'], 'XONG')
        self.assertEqual(a.kenh.ban_giao, [])

    def test_mat_ack_chi_gui_lai_ket_qua_khong_xu_ly_lai(self):
        a = viec_demo()
        a.kenh.mat_ack = 2
        kenh = self.chay(a)
        self.assertEqual(len(a.kenh.ban_giao), 3)
        self.assertEqual([op for _, op, _ in kenh.kho_goi], ['snapshot_luot', 'chot_luot'])
        self.assertEqual(kenh.ket_thuc_goi[0][1]['trang_thai'], 'XONG')

    def test_mat_ack_sau_commit_ngung_heartbeat_khong_ket_thuc_va_chay_tiep(self):
        a, b = viec_demo(), viec_demo()
        a.kenh.mat_ack = 99
        kenh = HangGia([a, b], self.dung)
        cac_luong = []
        tao_luong = threading.Thread

        def luong(**kwargs):
            worker = tao_luong(**kwargs)
            cac_luong.append(worker)
            return worker

        def khi_nhan():
            if kenh.hien_tai is b:
                self.assertEqual(len(cac_luong), 1)
                self.assertFalse(cac_luong[0].is_alive())
                self.assertEqual(a.kenh.operations.count('heartbeat'), 1)
                self.assertEqual(kenh.ket_thuc_goi, [])

        kenh.khi_nhan = khi_nhan
        with patch.object(chay.threading, 'Thread', side_effect=luong), \
                self.assertLogs(chay.__name__, level='WARNING') as nhat_ky:
            self.chay(kenh=kenh)
        self.assertEqual(len(a.kenh.ban_giao), chay.MAX_LAN_GUI_KET_QUA)
        self.assertEqual(a.ket_qua_id, 'DEMO_ACK')
        self.assertEqual([op for giu, op, _ in kenh.kho_goi if giu is a.giu],
                         ['snapshot_luot', 'chot_luot'])
        self.assertEqual(kenh.chua_ket_thuc, [a])
        self.assertEqual(kenh.da_xong, [b])
        self.assertEqual(kenh.ket_thuc_goi, [(b.giu, dict(
            trang_thai='XONG', ket_qua_id='DEMO_ACK', ma_loi=None))])
        self.assertTrue(all(not worker.is_alive() for worker in cac_luong))
        self.assertTrue(all(luong.closed for luong in a.kenh.luong))
        self.assertEqual([r.getMessage() for r in nhat_ky.records], ['MASK_KET_QUA_CHUA_RO'])
        self.assertFalse(nhat_ky.records[0].args)
        self.assertIsNone(nhat_ky.records[0].exc_info)
        for chuoi in (TEN, VAN_BAN):
            self.assertNotIn(chuoi, ''.join(nhat_ky.output))

    def test_ack_thieu_ma_khong_bao_xong(self):
        for ack in (None, {}, {'ket_qua_id': ''}, {'ket_qua_id': ' '}, {'ket_qua_id': 3}):
            with self.subTest(ack=ack):
                self.dung.clear()
                a, b = viec_demo(), viec_demo()
                goi_that = a.kenh.goi

                def goi(operation, giu, **payload):
                    kq = goi_that(operation, giu, **payload)
                    return ack if operation == 'ghi_ket_qua' else kq

                with patch.object(a.kenh, 'goi', side_effect=goi), \
                        self.assertLogs(chay.__name__, level='WARNING') as nhat_ky:
                    kenh = self.chay(a, b)
                self.assertEqual(a.ket_qua_id, 'DEMO_ACK')
                self.assertEqual(kenh.chua_ket_thuc, [a])
                self.assertEqual(kenh.da_xong, [b])
                self.assertEqual([giu for giu, _ in kenh.ket_thuc_goi], [b.giu])
                self.assertEqual([r.getMessage() for r in nhat_ky.records],
                                 ['MASK_KET_QUA_CHUA_RO'])

    def test_dung_van_cho_ack_ket_thuc_va_gia_han_lease(self):
        a = viec_demo()
        kenh = HangGia([a], self.dung)
        kenh.khi_kho = lambda op, p: self.dung.set()
        kenh.ket_thuc_loi = [RuntimeError(TEN), False, True]
        self.chay(kenh=kenh)
        self.assertEqual(len(kenh.ket_thuc_goi), 3)
        self.assertTrue(all(p == kenh.ket_thuc_goi[0][1] for _, p in kenh.ket_thuc_goi))
        self.assertGreaterEqual(a.kenh.operations.count('heartbeat'), 3)
        self.assertEqual(kenh.da_xong, [a])

    def test_ket_thuc_loi_khong_nhan_lease_ke_tiep_truoc_xac_nhan(self):
        kenh = HangGia([viec_demo(), viec_demo()], self.dung)
        kenh.ket_thuc_loi = [RuntimeError(TEN), True]
        self.chay(kenh=kenh)
        self.assertEqual(len(kenh.da_xong), 2)
        self.assertEqual(len(kenh.ket_thuc_goi), 3)
        self.assertEqual(kenh.chua_ket_thuc, [])

    def test_mat_lease_core_xac_nhan_khong_treo_vong(self):
        a, b = viec_demo(), viec_demo()
        a.kenh.mat_lease = True
        kenh = HangGia([a, b], self.dung)
        ket_that = kenh.ket_thuc

        def ket_thuc(giu, **p):
            if giu is a.giu:
                kenh.ket_thuc_goi.append((giu, p))
                kenh.hien_tai = None  # Core xác nhận lease không còn thuộc worker.
                raise LoiEngine('VIEC_MAT_LEASE')
            return ket_that(giu, **p)

        with patch.object(kenh, 'ket_thuc', side_effect=ket_thuc):
            self.chay(kenh=kenh)
        self.assertEqual(kenh.da_xong, [b])
        self.assertEqual(kenh.ket_thuc_goi[0][1]['trang_thai'], 'LOI')

    def test_loi_khong_lo_van_ban_cum_bi_danh_trong_log_va_ma_loi(self):
        a, b = viec_demo(), viec_demo()
        bi_danh = '[[DEMO-BI-DANH-RIENG]]'
        a.kho = Mock(side_effect=RuntimeError(VAN_BAN + TEN + bi_danh))
        out, err, log = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(log)
        logging.getLogger().addHandler(handler)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                kenh = self.chay(a, b)
        finally:
            logging.getLogger().removeHandler(handler)
        hien_thi = out.getvalue() + err.getvalue() + log.getvalue() + repr(kenh.ket_thuc_goi)
        for chuoi in (VAN_BAN, TEN, bi_danh):
            self.assertNotIn(chuoi, hien_thi)
        self.assertEqual(kenh.ket_thuc_goi[0][1]['ma_loi'], 'MASK_XU_LY')
        self.assertEqual(len(kenh.da_xong), 2)


class HopDongKetThucTests(unittest.TestCase):
    def test_mock_nhan_trang_thai_ket_thuc_core_cho_phep(self):
        for trang_thai in ('XONG', 'LOI', 'DA_DUNG', 'CHUA_RO', 'CHO'):
            with self.subTest(trang_thai=trang_thai):
                a = viec_demo()
                kenh = HangGia([a], threading.Event())
                kenh.nhan_viec()
                a.ket_qua_id = 'DEMO_ACK' if trang_thai == 'XONG' else None
                ma_loi = 'MASK_XU_LY' if trang_thai in {'LOI', 'CHUA_RO', 'CHO'} else None
                self.assertTrue(kenh.ket_thuc(a.giu, trang_thai=trang_thai,
                    ket_qua_id=a.ket_qua_id, ma_loi=ma_loi))
                self.assertEqual(kenh.da_xong, [a])

    def test_mock_tu_choi_trang_thai_va_ma_loi_sai(self):
        for trang_thai, ma_loi in (
                ('THAT_BAI', 'MASK_XU_LY'), ('LOI', None), ('CHUA_RO', None),
                ('CHO', None), ('LOI', ''), ('LOI', 'Lỗi DEMO'), ('LOI', 3)):
            with self.subTest(trang_thai=trang_thai, ma_loi=ma_loi):
                a = viec_demo()
                kenh = HangGia([a], threading.Event())
                kenh.nhan_viec()
                with self.assertRaises(ValueError):
                    kenh.ket_thuc(a.giu, trang_thai=trang_thai,
                                 ket_qua_id=None, ma_loi=ma_loi)
                self.assertEqual(kenh.da_xong, [])
                self.assertIs(kenh.hien_tai, a)

    def test_mock_bat_buoc_id_ket_qua_khop_core_ke_ca_mat_ack(self):
        for da_commit, trang_thai, ket_qua_id in (
                (False, 'XONG', None), (False, 'XONG', 'DEMO_ACK'),
                (True, 'XONG', None), (True, 'XONG', 'DEMO_SAI'),
                (True, 'LOI', None)):
            with self.subTest(da_commit=da_commit, trang_thai=trang_thai,
                              ket_qua_id=ket_qua_id):
                a = viec_demo()
                kenh = HangGia([a], threading.Event())
                kenh.nhan_viec()
                a.ket_qua_id = 'DEMO_ACK' if da_commit else None
                with self.assertRaises(LoiEngine) as bat:
                    kenh.ket_thuc(a.giu, trang_thai=trang_thai,
                        ket_qua_id=ket_qua_id, ma_loi='MASK_XU_LY' if trang_thai == 'LOI' else None)
                self.assertEqual(bat.exception.ma, 'KENH_KHONG_DU_QUYEN')
                self.assertEqual(kenh.da_xong, [])


class DiemVaoTests(unittest.TestCase):
    def test_import_khong_nhan_bootstrap_hoac_chay_tien_trinh(self):
        spec = importlib.util.spec_from_file_location('engines.e_mask.kiem_import', chay.__file__)
        module = importlib.util.module_from_spec(spec)
        with patch.object(chay.Bootstrap, 'nhan') as nhan, \
                patch.object(chay.subprocess, 'Popen') as spawn:
            spec.loader.exec_module(module)
        nhan.assert_not_called()
        spawn.assert_not_called()
        self.assertTrue(callable(module.main))

    def test_engine_khong_import_core(self):
        cay = ast.parse(Path(chay.__file__).read_text('utf-8'))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.Import):
                ten = [alias.name for alias in nut.names]
            elif isinstance(nut, ast.ImportFrom):
                ten = [nut.module or '']
            else:
                continue
            self.assertFalse(any(t == 'kho_tri_thuc.core' or t.startswith('kho_tri_thuc.core.')
                                 for t in ten))

    def test_main_bootstrap_thu_hoi_drain_truoc_dong_kenh(self):
        da_nhan, tiep_tuc = threading.Event(), threading.Event()
        bootstrap = Mock()
        conn = Mock()
        conn.__enter__ = Mock(return_value=conn)
        conn.__exit__ = Mock(return_value=False)
        bootstrap.accept.return_value = (conn, None)
        kenh = HangGia([viec_demo(), viec_demo()], threading.Event())
        xu_ly_that = chay.xu_ly_viec

        def xu_ly(*args, **kwargs):
            da_nhan.set()
            if not tiep_tuc.wait(2):
                raise RuntimeError('Thiếu lệnh thu hồi giả.')
            return xu_ly_that(*args, **kwargs)

        def thu_hoi(*, ngung_accept, drain):
            self.assertTrue(da_nhan.wait(2))
            ngung_accept()
            self.assertEqual(kenh.da_xong, [])
            tiep_tuc.set()
            self.assertTrue(drain())
            self.assertEqual(len(kenh.da_xong), 1)
            conn.__exit__.assert_called_once()

        bootstrap.cho_thu_hoi.side_effect = thu_hoi
        nhan_kenh = Mock(return_value=kenh)
        with tai_nguyen_demo(), patch.object(chay.Bootstrap, 'nhan', return_value=bootstrap), \
                patch.object(chay, 'xu_ly_viec', side_effect=xu_ly):
            chay.main(kiem_chu_ky=Mock(), nhan_viec=nhan_kenh)
        nhan_kenh.assert_called_once_with(conn, bootstrap.bo_doc)
        conn.settimeout.assert_called_once_with(None)
        self.assertEqual(bootstrap.bao_san_sang.call_args.kwargs['contracts'], [])
        bootstrap.bi_mat.thu_hoi.assert_called_once()
        bootstrap.socket.close.assert_called_once()

    def test_main_loi_preflight_thu_hoi_bi_mat_khong_accept(self):
        bootstrap = Mock()
        bootstrap.bao_san_sang.side_effect = chay.LoiBootstrap('CHUA_SAN_SANG')
        with patch.object(chay.Bootstrap, 'nhan', return_value=bootstrap):
            with self.assertRaises(chay.LoiBootstrap):
                chay.main(kiem_chu_ky=Mock(), nhan_viec=Mock())
        bootstrap.accept.assert_not_called()
        bootstrap.bi_mat.thu_hoi.assert_called_once()
        bootstrap.socket.close.assert_called_once()

    def test_main_loi_kenh_khong_lo_noi_dung_va_van_don_bootstrap(self):
        da_goi = threading.Event()
        bootstrap = Mock()
        conn = Mock()
        conn.__enter__ = Mock(return_value=conn)
        conn.__exit__ = Mock(return_value=False)
        bootstrap.accept.return_value = (conn, None)

        def nhan_kenh(*args):
            da_goi.set()
            raise RuntimeError(TEN)

        def thu_hoi(*, ngung_accept, drain):
            self.assertTrue(da_goi.wait(2))
            ngung_accept()
            self.assertTrue(drain())

        bootstrap.cho_thu_hoi.side_effect = thu_hoi
        with patch.object(chay.Bootstrap, 'nhan', return_value=bootstrap):
            with self.assertRaises(chay.LoiMask) as bat:
                chay.main(kiem_chu_ky=Mock(), nhan_viec=nhan_kenh)
        self.assertEqual(bat.exception.ma, 'MASK_XU_LY')
        self.assertNotIn(TEN, str(bat.exception))
        self.assertIsNone(bat.exception.__context__)
        conn.__exit__.assert_called_once()
        bootstrap.bi_mat.thu_hoi.assert_called_once()
        bootstrap.socket.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
