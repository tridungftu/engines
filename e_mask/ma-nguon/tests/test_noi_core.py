"""MASK-3E: dữ liệu DEMO, SDK/kho giả; không CSDL, mạng hay tiến trình."""
import ast
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import inspect
import io
import json
import logging
from pathlib import Path
import threading
import traceback
import unicodedata
import unittest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from engines.e_mask import chay
from engines.e_mask.che_van_ban import Kho
from engines.e_mask.kho_qua_core import KhoQuaCore, LoiKhoQuaCore
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine
from tests.test_mask_kho import TEN, VAN_BAN, tai_nguyen_demo


CHE, MO = 'mask.che_van_ban', 'mask.mo_che_van_ban'
META = dict(bien_the='mask_demo', ma_contract='mask_noi_bo_demo',
            phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
            revision_truoc=0, nguon=[])


class KhoCoreGia:
    """Cùng hợp đồng 3D; nhật ký nhạy cảm là đầu vào kho, tách khỏi log."""
    def __init__(self):
        self.snap = dict(da_chot=False,
                         phien_ban='{ "cum": {}, "bi_danh": {}, "yeu_cau": null }',
                         danh_muc=[], yeu_cau=None)
        self.cac_goi, self.da_chot = [], {}
        self.ma_duoc_mo = None
        self.loi_snapshot = self.loi_chot = False

    def __call__(self, operation, **p):
        self.cac_goi.append((operation, deepcopy(p)))
        khoa = p['ma_yeu_cau'], p['ma_luot'], p['loai']
        if operation == 'snapshot_luot':
            if self.loi_snapshot or (p['loai'] == 'mo_che' and p['ma_yeu_cau'] != self.ma_duoc_mo):
                raise RuntimeError('Từ chối DEMO: '+TEN)
            if khoa in self.da_chot:
                return {'da_chot': True}
            return deepcopy(self.snap)
        assert operation == 'chot_luot'
        if self.loi_chot:
            raise RuntimeError('Xung đột hoặc chưa commit DEMO: '+TEN)
        if khoa in self.da_chot:
            assert all(p[k] is None for k in ('phien_ban', 'nhat_ky', 'ket_qua'))
            return deepcopy(self.da_chot[khoa])
        assert p['phien_ban'] == self.snap['phien_ban']
        assert set(p['nhat_ky']) == {'cum', 'bi_danh_tam_moi', 'bi_danh_da_dung',
                                     'dong_yeu_cau', 'cum_da_tra', 'bi_danh_da_tra'}
        self.da_chot[khoa] = deepcopy(p['ket_qua'])
        return deepcopy(p['ket_qua'])


class KenhGia(KenhCore):
    def __init__(self, envelope, raw):
        self.envelope, self.raw = envelope, raw
        self.operations, self.ban_giao, self.luong = [], [], []
        self.mat_ack = 0
        self.mat_lease = False
        self.tep = None

    def goi(self, operation, giu_viec, **p):
        self.operations.append(operation)
        if operation == 'heartbeat':
            return replace(giu_viec, giu_den=datetime.now(timezone.utc)+timedelta(seconds=120))
        if operation == 'doc_dau_vao':
            return deepcopy(self.envelope)
        if operation == 'mo_doc':
            assert p == {'tep_id': self.envelope['yeu_cau']['tham_chieu_tep']['tep_id']}
            self.tep = io.BytesIO(self.raw)
            return self.tep
        assert operation == 'ghi_ket_qua'
        self.ban_giao.append((p['luong'].read(), deepcopy(p['du_lieu']), p['revision_tep_truoc']))
        self.luong.append(p['luong'])
        if self.mat_lease:
            raise LoiEngine('VIEC_MAT_LEASE')
        if len(self.ban_giao) <= self.mat_ack:
            raise RuntimeError('Mất ACK DEMO: '+TEN)
        return {'ket_qua_id': 'DEMO_ACK'}


def sdk(kenh):
    giu = GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
                  phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:MASK:LAP',
                  instance_id=uuid4(), the_he=1, ma=MaBiMat('n'*43),
                  giu_den=datetime.now(timezone.utc)+timedelta(seconds=120))
    return SDKEngine(giu, kenh_core=kenh)


class NoiCoreTests(unittest.TestCase):
    def setUp(self):
        self.kho = KhoCoreGia()
        self.yc = dict(van_ban=VAN_BAN, ma_yeu_cau=str(uuid4()), ma_luot=str(uuid4()))
        self.envelope = dict(capability=CHE, yeu_cau={'tham_chieu_tep': {'tep_id': str(uuid4())}},
                             du_lieu_ket_qua=deepcopy(META), revision_tep_truoc=0)
        self.addCleanup(self._tai_nguyen_dong)
        self.tai_nguyen = tai_nguyen_demo()
        self.tai_nguyen.__enter__()

    def _tai_nguyen_dong(self):
        self.tai_nguyen.__exit__(None, None, None)

    def kenh(self, yc=None, envelope=None):
        return KenhGia(deepcopy(self.envelope if envelope is None else envelope),
                       json.dumps(self.yc if yc is None else yc, ensure_ascii=False).encode('utf-8'))

    def function(self, cap=CHE, yc=None):
        return chay.xu_ly_function(cap, self.yc if yc is None else yc, goi_kho=self.kho)

    def assert_an(self, exc):
        self.assertNotIn(TEN, ''.join(traceback.format_exception(exc)))
        self.assertIsNone(exc.__cause__)
        self.assertIsNone(exc.__context__)

    def test_envelope_tham_chieu_che_chot_truoc_ban_giao(self):
        kenh = self.kenh()
        self.assertNotIn(TEN, json.dumps(self.envelope, ensure_ascii=False))
        self.assertEqual(chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho), {'ket_qua_id': 'DEMO_ACK'})
        self.assertEqual(kenh.operations, ['heartbeat', 'doc_dau_vao', 'mo_doc', 'ghi_ket_qua'])
        self.assertTrue(kenh.tep.closed)
        self.assertTrue(kenh.luong[0].closed)
        raw, meta, rev = kenh.ban_giao[0]
        kq = json.loads(raw)
        self.assertTrue(kq['gui_duoc'])
        self.assertNotIn(TEN, raw.decode('utf-8'))
        self.assertIn('1.000.000 VND', kq['van_ban_da_che'])
        self.assertIn('07/11/2026', kq['van_ban_da_che'])
        self.assertEqual((meta, rev), (META, 0))
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot', 'chot_luot'])
        self.assertFalse(self.kho.cac_goi[-1][1]['nhat_ky']['dong_yeu_cau'])
        self.assertNotIn('nhat_ky', kq)
        self.assertNotIn('danh_muc', kq)

    def test_envelope_sai_khong_doc_tep_hoac_goi_kho(self):
        cac_sai = [None, {}, dict(self.envelope, capability='mask.la'),
                   dict(self.envelope, van_ban=TEN), dict(self.envelope, ma_yeu_cau=TEN),
                   dict(self.envelope, yeu_cau={'van_ban': TEN}),
                   dict(self.envelope, yeu_cau={'tham_chieu_tep': {'tep_id': TEN}}),
                   dict(self.envelope, du_lieu_ket_qua={'van_ban': TEN}),
                   dict(self.envelope, revision_tep_truoc=True),
                   dict(self.envelope, du_lieu_ket_qua=dict(META, revision_truoc=-1))]
        for env in cac_sai:
            with self.subTest(env=env):
                kenh = self.kenh(envelope=env) if env is not None else KenhGia(None, b'')
                with self.assertRaises(chay.LoiMask) as bat:
                    chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
                self.assert_an(bat.exception)
                self.assertNotIn('mo_doc', kenh.operations)
                self.assertEqual(kenh.ban_giao, [])
        self.assertEqual(self.kho.cac_goi, [])

    def test_tep_rieng_sai_json_utf8_trung_truong_tran(self):
        for raw in (b'{', b'\xff', b'[]', b'{"a":1,"a":2}', b'{"a":NaN}',
                    b' '*(chay.MAX_BYTES+1)):
            with self.subTest(loai=raw[:20]):
                kenh = KenhGia(self.envelope, raw)
                with self.assertRaises(chay.LoiMask) as bat:
                    chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
                self.assert_an(bat.exception)
                self.assertTrue(kenh.tep.closed)
                self.assertEqual(kenh.ban_giao, [])
        self.assertEqual(self.kho.cac_goi, [])

    def test_khong_day_toan_van_vao_khung_ipc_mot_mib(self):
        kenh = self.kenh()
        kenh.raw = b' '*(1024*1024+1) + kenh.raw
        chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        self.assertTrue(json.loads(kenh.ban_giao[0][0])['gui_duoc'])

    def test_yeu_cau_sai_khong_lay_snapshot(self):
        for yc in ({}, dict(self.yc, van_ban=42), dict(self.yc, ma_yeu_cau=TEN),
                   dict(self.yc, ma_luot=None), dict(self.yc, module='gia_mao'),
                   dict(self.yc, van_ban='a'*500001),
                   dict(self.yc, dinh_danh_da_biet=[{'gia_tri': TEN, 'nhom': 'sai'}])):
            with self.subTest(truong=tuple(yc)):
                with self.assertRaises(chay.LoiMask) as bat:
                    self.function(yc=yc)
                self.assert_an(bat.exception)
        self.assertEqual(self.kho.cac_goi, [])

    def test_con_sot_chan_van_ban_null_khong_lo_cum_goc(self):
        with patch.object(chay.che_van_ban, '_kiem_con_sot',
                          return_value=([{'bat_dau': 0, 'ket_thuc': 5, 'ly_do': 'Cần kiểm tra.'}], True)):
            kenh = self.kenh()
            chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        kq = json.loads(kenh.ban_giao[0][0])
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertNotIn(TEN, json.dumps(kq, ensure_ascii=False))
        self.assertTrue(self.kho.cac_goi[-1][1]['nhat_ky']['dong_yeu_cau'])

    def test_kiem_tien_ngay_chua_dat_cung_chan(self):
        with patch.object(chay.che_van_ban, '_kiem_tien_ngay', return_value=False):
            kq = self.function()
        self.assertFalse(kq['kiem_tien_ngay'])
        self.assertFalse(kq['gui_duoc'])
        self.assertIsNone(kq['van_ban_da_che'])
        self.assertTrue(self.kho.cac_goi[-1][1]['nhat_ky']['dong_yeu_cau'])

    def test_che_tai_dung_bi_danh_cum_cho_toan_vung(self):
        bi_danh = '[[MASKTAM-00000000000000000000000000000004]]'
        self.kho.snap['cum_cho_toan_vung'] = {
            '91152e933b01541b3f0fa2d5c5530b33b185362867afd44be40612a6ff3463cd':
                dict(nhom='CONG_TY', bi_danh=bi_danh, nguon='tam')}
        kq = self.function()
        self.assertTrue(kq['gui_duoc'])
        self.assertIn(bi_danh, kq['van_ban_da_che'])
        self.assertEqual(kq['bi_danh'], [dict(nhom='CONG_TY', bi_danh=bi_danh, nguon='tam')])
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 0)
        nhat_ky = self.kho.cac_goi[-1][1]['nhat_ky']
        self.assertEqual(nhat_ky['bi_danh_tam_moi'], [])
        self.assertEqual(nhat_ky['bi_danh_da_dung'], [bi_danh])
        self.assertEqual(nhat_ky['cum'], [dict(gia_tri=TEN.lower(), nhom='CONG_TY',
                                             bi_danh=bi_danh, chi_gap_lai=True)])

    def test_che_cum_cho_khac_nhom_giu_nhom_cua_core(self):
        bi_danh = '[[MASKTAM-00000000000000000000000000000004]]'
        self.kho.snap['cum_cho_toan_vung'] = {
            '91152e933b01541b3f0fa2d5c5530b33b185362867afd44be40612a6ff3463cd':
                dict(nhom='KHAC', bi_danh=bi_danh, nguon='tam')}
        yc = dict(self.yc, dinh_danh_da_biet=[dict(gia_tri=TEN, nhom='CONG_TY')])
        kq = self.function(yc=yc)
        self.assertTrue(kq['gui_duoc'])
        self.assertIn(bi_danh, kq['van_ban_da_che'])
        self.assertEqual(kq['bi_danh'], [dict(nhom='KHAC', bi_danh=bi_danh, nguon='tam')])
        self.assertEqual(kq['cho_duyet']['so_cum_vua_them'], 0)
        nhat_ky = self.kho.cac_goi[-1][1]['nhat_ky']
        self.assertEqual(nhat_ky['bi_danh_tam_moi'], [])
        self.assertEqual(nhat_ky['bi_danh_da_dung'], [bi_danh])
        self.assertEqual(nhat_ky['cum'], [dict(gia_tri=TEN.lower(), nhom='KHAC',
                                             bi_danh=bi_danh, chi_gap_lai=True)])

    def test_mo_che_ma_yeu_cau_dung_va_dong(self):
        che = self.function()
        self.kho.snap['danh_muc'] = [dict(gia_tri=TEN, nhom='CONG_TY',
            bi_danh=che['bi_danh'][0]['bi_danh'], nguon='tam', so_lan_gap=1)]
        self.kho.snap['yeu_cau'] = {'trang_thai': 'DANG_XU_LY'}
        self.kho.ma_duoc_mo = self.yc['ma_yeu_cau']
        yc = dict(van_ban=che['van_ban_da_che'], ma_yeu_cau=self.yc['ma_yeu_cau'],
                  ma_luot=str(uuid4()), dong_viec=True)
        kenh = self.kenh(yc, dict(self.envelope, capability=MO))
        chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        kq = json.loads(kenh.ban_giao[0][0])
        # Định danh chỉ được phép trong nội dung mở che gửi về Core đã kiểm quyền.
        self.assertEqual(kq['van_ban_da_mo_che'], VAN_BAN)
        self.assertTrue(kq['mo_day_du'])
        self.assertEqual(kq['trang_thai_ma_yeu_cau'], 'DA_DONG')
        self.assertTrue(self.kho.cac_goi[-1][1]['nhat_ky']['dong_yeu_cau'])

    def test_mo_che_sai_ma_khong_cong_bo(self):
        self.kho.ma_duoc_mo = str(uuid4())
        kenh = self.kenh(dict(self.yc, van_ban='[[KH-DEMO-01]]'), dict(self.envelope, capability=MO))
        with self.assertRaises(chay.LoiMask) as bat:
            chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        self.assert_an(bat.exception)
        self.assertEqual(kenh.ban_giao, [])
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot'])

    def test_mat_ack_gui_lai_dung_byte_khong_che_chot_lai(self):
        kenh = self.kenh()
        kenh.mat_ack = 2
        with patch.object(chay.che_van_ban, 'che', wraps=chay.che_van_ban.che) as che, \
                patch.object(chay.time, 'sleep'):
            chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        self.assertEqual(che.call_count, 1)
        self.assertEqual(len(kenh.ban_giao), 3)
        self.assertTrue(all(p == kenh.ban_giao[0] for p in kenh.ban_giao))
        self.assertEqual(len({id(s) for s in kenh.luong}), 1)
        self.assertEqual(len(self.kho.cac_goi), 2)

    def test_heartbeat_tiep_tuc_khi_core_dang_giu_ack(self):
        event_that = threading.Event
        da_gia_han = event_that()
        kenh = self.kenh()
        goi = kenh.goi
        so_nhip = []

        class EventNhanh(event_that):
            def wait(self, timeout=None):
                # Chỉ rút lịch heartbeat; vẫn dùng Thread/Event thật, không ngủ 30s.
                return super().wait(0.001 if timeout in (30, 1) else timeout)

        def cho_ack(operation, giu_viec, **p):
            if operation == 'heartbeat':
                so_nhip.append(True)
                if len(so_nhip) > 1:
                    da_gia_han.set()
            if operation == 'ghi_ket_qua':
                self.assertTrue(da_gia_han.wait(2), 'Thiếu heartbeat trong lúc chờ ACK.')
            return goi(operation, giu_viec, **p)

        kenh.goi = cho_ack
        with patch.object(chay.threading, 'Event', EventNhanh):
            chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        self.assertGreaterEqual(len(so_nhip), 2)
        self.assertEqual(len(self.kho.cac_goi), 2)
        self.assertEqual(len(kenh.ban_giao), 1)

    def test_chi_tra_ket_qua_core_da_chot(self):
        def goi(operation, **p):
            kq = self.kho(operation, **p)
            return dict(kq, van_ban_da_che='Đã chốt DEMO.') if operation == 'chot_luot' else kq

        kq = chay.xu_ly_function(CHE, self.yc, goi_kho=goi)
        self.assertEqual(kq['van_ban_da_che'], 'Đã chốt DEMO.')

    def test_mo_che_bi_danh_la_giu_ma_yeu_cau_dang_xu_ly(self):
        self.kho.ma_duoc_mo = self.yc['ma_yeu_cau']
        self.kho.snap['yeu_cau'] = {'trang_thai': 'DANG_XU_LY'}
        yc = dict(self.yc, van_ban='[[KH-DEMO-LA]]', dong_viec=True)
        kq = self.function(MO, yc)
        self.assertFalse(kq['mo_day_du'])
        self.assertEqual(kq['trang_thai_ma_yeu_cau'], 'DANG_XU_LY')
        self.assertFalse(self.kho.cac_goi[-1][1]['nhat_ky']['dong_yeu_cau'])

    def test_mo_che_yeu_cau_da_dong_khong_chot(self):
        self.kho.ma_duoc_mo = self.yc['ma_yeu_cau']
        self.kho.snap['yeu_cau'] = {'trang_thai': 'DA_DONG'}
        with self.assertRaises(chay.LoiMask) as bat:
            self.function(MO)
        self.assert_an(bat.exception)
        self.assertEqual([x[0] for x in self.kho.cac_goi], ['snapshot_luot'])

    def test_mat_lease_khong_retry_ban_giao(self):
        kenh = self.kenh()
        kenh.mat_lease = True
        with self.assertRaises(chay.LoiMask) as bat, patch.object(chay.time, 'sleep') as cho:
            chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
        self.assertEqual(bat.exception.ma, 'VIEC_MAT_LEASE')
        self.assert_an(bat.exception)
        self.assertEqual(len(kenh.ban_giao), 1)
        self.assertTrue(kenh.luong[0].closed)
        cho.assert_not_called()

    def test_phat_lai_da_chot_khong_che_lai_va_van_kiem_quyen(self):
        cu = self.function()
        with patch.object(chay.che_van_ban, 'che') as che:
            self.assertEqual(self.function(), cu)
        che.assert_not_called()
        self.assertIsNone(self.kho.cac_goi[-1][1]['nhat_ky'])
        self.kho.loi_chot = True
        with self.assertRaises(chay.LoiMask) as bat:
            self.function()
        self.assert_an(bat.exception)

    def test_loi_snapshot_chot_va_xu_ly_khong_lo_cum_trong_log(self):
        nhat_ky = io.StringIO()
        handler = logging.StreamHandler(nhat_ky)
        logging.getLogger().addHandler(handler)
        self.addCleanup(logging.getLogger().removeHandler, handler)
        for cua in ('snapshot', 'chot', 'xu_ly'):
            self.kho.loi_snapshot = cua == 'snapshot'
            self.kho.loi_chot = cua == 'chot'
            kenh = self.kenh()
            with self.subTest(cua=cua), redirect_stdout(nhat_ky), redirect_stderr(nhat_ky):
                with patch.object(chay.che_van_ban, 'che',
                        side_effect=RuntimeError(TEN)) if cua == 'xu_ly' else patch.object(
                            chay.che_van_ban, 'che', wraps=chay.che_van_ban.che):
                    with self.assertRaises(chay.LoiMask) as bat:
                        chay.xu_ly_viec(sdk(kenh), goi_kho=self.kho)
                self.assert_an(bat.exception)
                self.assertEqual(kenh.ban_giao, [])
        self.assertEqual(nhat_ky.getvalue(), '')

    def test_chua_noi_callable_khong_dung_core_sql_thay_the(self):
        kenh = self.kenh()
        with self.assertRaises(chay.LoiMask) as bat:
            chay.xu_ly_viec(sdk(kenh), goi_kho=None)
        self.assertEqual(bat.exception.ma, 'MASK_KHO_CHUA_NOI')
        self.assertEqual(kenh.operations, [])

    def test_launcher_cu_da_bo_ke_ca_du_seam(self):
        cap, ready, stop = (Mock(return_value=True) for _ in range(3))
        khung = chay.TienTrinhMask(thu_muc_mask='KHONG_DOC', cong=19357,
                                  cap_khoa=cap, kiem_san_sang=ready, cho_phep_dung=stop)
        with patch.object(chay.subprocess, 'Popen') as spawn:
            with self.assertRaises(chay.LoiMask) as bat:
                khung.khoi_dong()
        self.assertEqual(bat.exception.ma, 'MASK_LAUNCHER_DA_BO')
        for seam in (spawn, cap, ready, stop):
            seam.assert_not_called()


class HopDongKhoTests(unittest.TestCase):
    def _assert_tu_choi_cum_cho(self, cum_cho):
        for loai, capability in (('che', CHE), ('mo_che', MO)):
            with self.subTest(loai=loai):
                core = KhoCoreGia()
                ma, luot = str(uuid4()), str(uuid4())
                core.ma_duoc_mo = ma
                core.snap['cum_cho_toan_vung'] = deepcopy(cum_cho)
                with self.assertRaises(LoiKhoQuaCore) as bat:
                    KhoQuaCore(goi_kho=core, ma_yeu_cau=ma, ma_luot=luot, loai=loai)
                self.assertEqual(str(bat.exception),
                                 'Thông tin định danh chờ duyệt chưa hợp lệ.')
                self.assertNotIn(TEN, ''.join(traceback.format_exception(bat.exception)))
                self.assertEqual([goi[0] for goi in core.cac_goi], ['snapshot_luot'])
                core.cac_goi.clear()
                with patch.object(chay.che_van_ban, 'che') as che, \
                        patch.object(chay.che_van_ban, 'mo_che') as mo_che:
                    with self.assertRaises(chay.LoiMask) as bat:
                        chay.xu_ly_function(capability, dict(
                            van_ban=VAN_BAN, ma_yeu_cau=ma, ma_luot=luot), goi_kho=core)
                self.assertEqual(bat.exception.ma, 'MASK_XU_LY')
                self.assertNotIn(TEN, ''.join(traceback.format_exception(bat.exception)))
                self.assertIsNone(bat.exception.__cause__)
                self.assertIsNone(bat.exception.__context__)
                che.assert_not_called()
                mo_che.assert_not_called()
                self.assertEqual([goi[0] for goi in core.cac_goi], ['snapshot_luot'])
                self.assertEqual(core.da_chot, {})

    def _assert_tu_choi_muc_cho(self, muc):
        # Kiểm cả mục được tra và mục không nằm trong văn bản của lượt này.
        for bam in ('91152e933b01541b3f0fa2d5c5530b33b185362867afd44be40612a6ff3463cd',
                    'f' * 64):
            with self.subTest(bam=bam):
                self._assert_tu_choi_cum_cho({
                    'a' * 64: dict(nhom='CONG_TY', bi_danh='[[DEMO-01]]', nguon='tam'),
                    bam: muc})

    def test_cum_cho_thieu_truong_tu_choi_ca_snapshot(self):
        for khoa in ('nhom', 'bi_danh', 'nguon'):
            with self.subTest(thieu=khoa):
                muc = dict(nhom='CONG_TY', bi_danh='[[DEMO-01]]', nguon='tam')
                self._assert_tu_choi_muc_cho({k: v for k, v in muc.items() if k != khoa})

    def test_cum_cho_khoa_la_tu_choi_ca_snapshot(self):
        self._assert_tu_choi_muc_cho(dict(
            nhom='CONG_TY', bi_danh='[[DEMO-01]]', nguon='tam', truong_la=TEN))

    def test_cum_cho_nhom_sai_kieu_hoac_rong_tu_choi_ca_snapshot(self):
        for nhom in (3, True, None, [], {}, ''):
            with self.subTest(nhom=nhom):
                self._assert_tu_choi_muc_cho(dict(
                    nhom=nhom, bi_danh='[[DEMO-01]]', nguon='tam'))

    def test_cum_cho_bi_danh_sai_kieu_hoac_rong_tu_choi_ca_snapshot(self):
        for bi_danh in (3, True, None, [TEN], {'gia_tri': TEN}, ''):
            with self.subTest(bi_danh=bi_danh):
                self._assert_tu_choi_muc_cho(dict(
                    nhom='CONG_TY', bi_danh=bi_danh, nguon='tam'))

    def test_cum_cho_nguon_khac_tam_tu_choi_ca_snapshot(self):
        for nguon in ('chinh_thuc', TEN, '', None, True, 3, [], {}):
            with self.subTest(nguon=nguon):
                self._assert_tu_choi_muc_cho(dict(
                    nhom='CONG_TY', bi_danh='[[DEMO-01]]', nguon=nguon))

    def test_cum_cho_sai_cau_truc_tu_choi_ca_snapshot(self):
        for muc in (None, [], TEN, 3):
            with self.subTest(muc=muc):
                self._assert_tu_choi_muc_cho(muc)
        for cum_cho in (None, [], TEN, 3):
            with self.subTest(cum_cho=cum_cho):
                self._assert_tu_choi_cum_cho(cum_cho)
        for bam in (TEN, 'A' * 64, 'a' * 63, 'a' * 65, 'g' * 64, 'a' * 64 + '\n', 3):
            with self.subTest(bam=bam):
                self._assert_tu_choi_cum_cho({bam: dict(
                    nhom='CONG_TY', bi_danh='[[DEMO-01]]', nguon='tam')})

    def test_cum_cho_chuoi_khong_rong_dung_dto_khong_tu_them_enum_pattern(self):
        for nhom, bi_danh in (('Nhóm DEMO tùy chọn', 'Bí danh DEMO'), (' ', ' ')):
            with self.subTest(nhom=nhom, bi_danh=bi_danh):
                core = KhoCoreGia()
                core.snap['cum_cho_toan_vung'] = {
                    '91152e933b01541b3f0fa2d5c5530b33b185362867afd44be40612a6ff3463cd':
                        dict(nhom=nhom, bi_danh=bi_danh, nguon='tam')}
                kho = KhoQuaCore(goi_kho=core, ma_yeu_cau=str(uuid4()),
                                 ma_luot=str(uuid4()), loai='che')
                with kho.giao_dich():
                    self.assertEqual(kho.tra_bi_danh(TEN), dict(
                        nhom=nhom, bi_danh=bi_danh, nguon='tam'))

    def test_port_cung_chu_ky_kho(self):
        for name, func in Kho.__dict__.items():
            if not name.startswith('_') and callable(func):
                self.assertEqual(inspect.signature(getattr(KhoQuaCore, name)).parameters.keys(),
                                 inspect.signature(func).parameters.keys(), name)

    def test_vector_kho_luot_dung_chung(self):
        vector = json.loads(Path(__file__).with_name('vector_kho_luot.json').read_text('utf-8'))
        self.assertEqual(vector['phien_ban_vector'], 1)
        ma, luot = vector['ma_yeu_cau'], vector['ma_luot']
        for ca in vector['cac_ca']:
            with self.subTest(vector=ca['ma']):
                core = KhoCoreGia()
                core.ma_duoc_mo = ma
                core.snap = deepcopy(vector['snapshot_mac_dinh'])
                core.snap.update(deepcopy(ca['snapshot']))
                snapshot_goc = deepcopy(core.snap)
                kho = KhoQuaCore(goi_kho=core, ma_yeu_cau=ma, ma_luot=luot, loai=ca['loai'])
                with patch('engines.e_mask.kho_qua_core.uuid4',
                           return_value=UUID(vector['uuid_cap'])), kho.giao_dich():
                    for buoc in ca['thao_tac']:
                        kq = getattr(kho, buoc['goi'])(*buoc['doi'])
                        self.assertEqual(list(kq) if isinstance(kq, tuple) else kq,
                                         buoc['ket_qua'], buoc['goi'])
                self.assertEqual(len(core.cac_goi), 1)  # Các port chỉ xử lý RAM.
                self.assertEqual(kho.nhat_ky, ca['nhat_ky'])
                ban_sao = kho.nhat_ky
                for gia_tri in ban_sao.values():
                    if isinstance(gia_tri, list):
                        gia_tri.append('Thay đổi bản sao DEMO')
                self.assertEqual(kho.nhat_ky, ca['nhat_ky'])
                dau_ra = deepcopy(ca['ket_qua_chot'])
                kq_chot = kho.chot(dau_ra)
                self.assertEqual(dau_ra, ca['ket_qua_chot'])
                self.assertEqual(kq_chot, dict(dau_ra, ma_yeu_cau=ma, ma_luot=luot))
                self.assertEqual(core.cac_goi[-1], ('chot_luot', dict(
                    ma_yeu_cau=ma, ma_luot=luot, loai=ca['loai'],
                    phien_ban=snapshot_goc['phien_ban'], nhat_ky=ca['nhat_ky_chot'],
                    ket_qua=kq_chot)))
                self.assertEqual(kho.nhat_ky, ca['nhat_ky'])
                self.assertEqual(core.snap, snapshot_goc)

    def test_adapter_khong_import_ma_core(self):
        cay = ast.parse(Path(__file__).parents[1].joinpath('kho_qua_core.py').read_text('utf-8'))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.Import):
                ten = [alias.name for alias in nut.names]
            elif isinstance(nut, ast.ImportFrom):
                ten = [nut.module or '']
            else:
                continue
            self.assertFalse(any(t == 'kho_tri_thuc.core' or t.startswith('kho_tri_thuc.core.')
                                 for t in ten))

    def test_nhat_ky_tra_ban_sao_chong_dem_lap(self):
        core = KhoCoreGia()
        ma, luot = str(uuid4()), str(uuid4())
        kho = KhoQuaCore(goi_kho=core, ma_yeu_cau=ma, ma_luot=luot, loai='che')
        bi_danh = '[[MASKTAM-'+uuid4().hex+']]'
        with kho.giao_dich():
            kho._nhat_ky['bi_danh_tam_moi'].append(bi_danh)
            muc, moi = kho.ghi_cho_duyet(TEN, 'CONG_TY', bi_danh, ma)
            self.assertTrue(moi)
            self.assertNotIn('gia_tri', muc)
            for _ in range(3):
                kho.ghi_nhan_gap_lai(ma, TEN.lower(), 'CONG_TY')
                kho.ghi_bi_danh_da_dung(ma, [bi_danh]*2)
        self.assertEqual(kho.nhat_ky, dict(
            cum=[dict(gia_tri=TEN, nhom='CONG_TY', bi_danh=bi_danh, chi_gap_lai=False)],
            bi_danh_tam_moi=[bi_danh], bi_danh_da_dung=[bi_danh], dong_yeu_cau=False,
            cum_da_tra=['91152e933b01541b3f0fa2d5c5530b33b185362867afd44be40612a6ff3463cd'],
            bi_danh_da_tra=[]))
        copy = kho.nhat_ky
        copy['cum'].clear()
        self.assertEqual(len(kho.nhat_ky['cum']), 1)
        self.assertEqual(len(core.cac_goi), 1)  # Không RPC trong giao_dich.
        self.assertNotIn(TEN, repr(kho))

    def test_rollback_huy_nhat_ky_khong_the_chot(self):
        core = KhoCoreGia()
        ma = str(uuid4())
        kho = KhoQuaCore(goi_kho=core, ma_yeu_cau=ma, ma_luot=str(uuid4()), loai='che')
        with self.assertRaises(RuntimeError), kho.giao_dich():
            kho.ghi_cho_duyet(TEN, 'CONG_TY', kho.cap_bi_danh_tam(), ma)
            raise RuntimeError('Lỗi DEMO')
        with self.assertRaises(LoiKhoQuaCore):
            kho.chot({})
        with self.assertRaises(LoiKhoQuaCore), kho.giao_dich():
            pass
        self.assertEqual(len(core.cac_goi), 1)

    def test_byte_utf8_nfc_khong_bom_mat_dau(self):
        for ten in ('chay.py', 'kho_qua_core.py', 'vong_doi.py', 'tests/test_noi_core.py',
                    'tests/vector_kho_luot.json', 'NGUON.md'):
            raw = (Path(__file__).resolve().parents[1]/ten).read_bytes()
            chu = raw.decode('utf-8', errors='strict')
            self.assertFalse(raw.startswith(b'\xef\xbb\xbf'))
            self.assertEqual(chu, unicodedata.normalize('NFC', chu))
            self.assertNotIn('\ufffd', chu)


if __name__ == '__main__':
    unittest.main()
