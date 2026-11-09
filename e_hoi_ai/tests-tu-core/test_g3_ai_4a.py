"""AI-4a: provider/Core giả; bootstrap/listener/Windows Job/tiến trình thật.

Wire DEMO là seam test; child cấm mọi connect/DNS, chỉ accept loopback Core.
Không model Local, Cloud, Mask, bí mật hoặc CSDL thật.
"""

from dataclasses import replace
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kho_tri_thuc.core import tien_trinh as tt
from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.engines.e_hoi_ai import chay as ai
from kho_tri_thuc.engines.e_hoi_ai.dto import KetQuaAI, TruongAI, YeuCauAI
from kho_tri_thuc.sdk_core import bootstrap as bs
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine

try:
    from .test_g2_21 import SoGia, _dong
except ImportError:
    from test_g2_21 import SoGia, _dong


VAN_BAN = 'DEMO hóa đơn 0001: 1.234.567 đồng; 31/10/2026'
YEU_CAU = YeuCauAI('DEMO', VAN_BAN, 'Echo DEMO', ('noi_dung',))
METADATA = dict(bien_the='ai_demo', ma_contract='khung_ai_demo',
    phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
    revision_truoc=0, nguon=[])


def _lease():
    return GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:AI:LAP',
        instance_id=uuid4(), the_he=1,
        giu_den=datetime.now(timezone.utc) + timedelta(minutes=2),
        ma=MaBiMat('n' * 43))


class KenhGia(KenhCore):
    def __init__(self, conn=None, giu=False, loi_lan_dau=False):
        self.conn, self.giu, self.loi_lan_dau = conn, giu, loi_lan_dau
        self.da_goi = []
        self.raw = None
        self.luong_cho_ack = None

    def goi(self, operation, giu_viec, **payload):
        self.da_goi.append(operation)
        if operation == 'doc_dau_vao':
            return dict(yeu_cau_demo=YEU_CAU, du_lieu_ket_qua=dict(METADATA),
                        revision_tep_truoc=0)
        if operation != 'ghi_ket_qua':
            raise AssertionError('Operation ngoài test')
        raw = payload['luong'].read()
        if self.loi_lan_dau:
            if self.luong_cho_ack is None:
                self.luong_cho_ack, self.raw = payload['luong'], raw
                self.conn.sendall(b'loi_truoc_ack\n')
                raise RuntimeError('AI4A_CANARY')
            assert payload['luong'] is self.luong_cho_ack
            assert not self.luong_cho_ack.closed
            assert raw == self.raw
            self.conn.sendall(b'thu_lai_cho_ack\n')
            assert self.conn.recv(32) == b'core_da_nhan\n'
        self.raw = raw
        assert payload['du_lieu'] == METADATA
        assert payload['revision_tep_truoc'] == 0
        assert payload['ten'] == 'ai-demo.json'
        if self.conn is not None:
            if self.giu:
                self.conn.sendall(b'cho_core\n')
                assert self.conn.recv(32) == b'core_da_nhan\n'
            self.conn.sendall(self.raw + b'\n')
        return {'ket_qua_id': 'DEMO_DA_NHAN'}


def _cam_mang(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.gethostbyname'):
        raise AssertionError('AI-4a không được kết nối mạng/DNS')


def _child():
    sys.addaudithook(_cam_mang)

    def nhan_viec(conn, bo_doc):
        # Chỉ lease DEMO sau marker test; runtime không bỏ kiểm chữ ký thật.
        raw = conn.recv(64)
        assert raw in (b'DEMO_AI4A\n', b'DEMO_AI4A_GIU\n', b'DEMO_AI4A_LOI\n')
        return SDKEngine(_lease(), kenh_core=KenhGia(
            conn, raw.endswith(b'_GIU\n'), raw.endswith(b'_LOI\n')))

    def khong_nhan_the(sig, msg):
        raise ValueError('Test này không cấp thẻ request')

    ai.chay(kiem_chu_ky=khong_nhan_the, nhan_viec=nhan_viec, demo=True)


class AIThuanTest(unittest.TestCase):
    def test_provider_gia_dung_dto_giu_unicode_tien_ngay(self):
        provider = ai.ProviderAIGia()
        self.assertTrue(provider.san_sang())
        with patch('socket.socket', side_effect=AssertionError('Mạng')), \
                patch('subprocess.Popen', side_effect=AssertionError('Local thật')):
            kq = provider.goi(YEU_CAU)
        self.assertIsInstance(kq, KetQuaAI)
        self.assertIsInstance(kq.truong['noi_dung'], TruongAI)
        self.assertEqual(kq.truong['noi_dung'].gia_tri, VAN_BAN)
        self.assertEqual(kq.truong['noi_dung'].trich_dan, VAN_BAN)
        self.assertEqual((kq.muc, kq.ly_do), ('VANG', ('GIA_LAP',)))
        for value in (None, b'bytes', 123, 'x' * 16385):
            with self.subTest(value=type(value)), self.assertRaises(ValueError):
                provider.goi(replace(YEU_CAU, van_ban=value))
        with self.assertRaises(TypeError):
            provider.goi({})

    def test_viec_chi_doc_va_ban_giao_qua_sdk_core(self):
        kenh = KenhGia()
        kq = ai.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh),
                          provider=ai.ProviderAIGia(), demo=True)
        self.assertEqual(kenh.da_goi, ['doc_dau_vao', 'ghi_ket_qua'])
        self.assertEqual(json.loads(kenh.raw)['truong']['noi_dung']['gia_tri'], VAN_BAN)
        self.assertEqual(kq, {'ket_qua_id': 'DEMO_DA_NHAN'})

    def test_mat_lease_khong_goi_provider_hoac_ban_giao(self):
        lease = replace(_lease(), giu_den=datetime.now(timezone.utc) - timedelta(seconds=1))
        kenh, provider = KenhGia(), MagicMock()
        with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
            ai.xu_ly_viec(SDKEngine(lease, kenh_core=kenh), provider=provider, demo=True)
        self.assertEqual(kenh.da_goi, [])
        provider.goi.assert_not_called()

    def test_seam_phai_cap_sdk_engine_va_provider_tra_dto(self):
        with self.assertRaises(TypeError):
            ai.xu_ly_viec(object(), provider=ai.ProviderAIGia(), demo=True)
        kenh = KenhGia()
        with self.assertRaises(TypeError):
            ai.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh),
                          provider=MagicMock(goi=lambda _: {}), demo=True)
        self.assertEqual(kenh.da_goi, ['doc_dau_vao'])

    def test_preflight_chua_dat_khong_ready_khong_worker(self):
        b = bs.Bootstrap()
        b.socket, b.bo_doc = MagicMock(), MagicMock()
        b._duoc_accept, b._ra = False, io.BytesIO()
        provider = MagicMock()
        provider.san_sang.return_value = False
        with patch.object(ai.Bootstrap, 'nhan', return_value=b), \
                patch.object(ai._VongNhan, 'bat_dau') as start:
            with self.assertRaisesRegex(bs.LoiBootstrap, 'CHUA_SAN_SANG'):
                ai.chay(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None,
                        provider=provider, demo=True)
        start.assert_not_called()
        provider.goi.assert_not_called()
        b.socket.close.assert_called_once()
        self.assertEqual(b._ra.getvalue(), b'')

    def test_loi_ban_giao_giu_bo_dem_thu_lai_khong_goi_lai_provider(self):
        kenh = KenhGia()
        goi = kenh.goi
        loi = RuntimeError('AI4A_CANARY')
        luong_cho_ack = []
        provider = MagicMock(wraps=ai.ProviderAIGia())
        bao_loi = MagicMock()

        def ban_giao(operation, giu, **payload):
            if operation == 'ghi_ket_qua':
                luong = payload['luong']
                self.assertFalse(luong.closed)
                self.assertEqual(luong.tell(), 0)
                if not luong_cho_ack:
                    luong_cho_ack.append(luong)
                    kenh.raw = luong.read()  # Lỗi sau khi transport đã đọc hết.
                    kenh.da_goi.append(operation)
                    raise loi
                self.assertIs(luong, luong_cho_ack[0])
                self.assertEqual(luong.getvalue(), kenh.raw)
            return goi(operation, giu, **payload)

        kenh.goi = ban_giao
        ket_qua = ai.xu_ly_viec(SDKEngine(_lease(), kenh_core=kenh),
                               provider=provider, khi_loi_ban_giao=bao_loi, demo=True)
        self.assertEqual(ket_qua, {'ket_qua_id': 'DEMO_DA_NHAN'})
        self.assertEqual(kenh.da_goi, ['doc_dau_vao', 'ghi_ket_qua', 'ghi_ket_qua'])
        provider.goi.assert_called_once_with(YEU_CAU)
        bao_loi.assert_called_once_with()
        self.assertTrue(luong_cho_ack[0].closed)
        self.assertNotIn('AI4A_CANARY', repr(loi))

    def test_import_khong_khoi_dong_local_hay_mang(self):
        code = '''
import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
with patch('socket.socket', side_effect=AssertionError('Không mở socket')), \\
     patch('socket.getaddrinfo', side_effect=AssertionError('Không DNS')), \\
     patch('subprocess.Popen', side_effect=AssertionError('Không chạy Local')), \\
     patch('threading.Thread.start', side_effect=AssertionError('Không worker')):
    from kho_tri_thuc.engines.e_hoi_ai import chay
'''
        p = subprocess.run([sys.executable, '-B', '-X', 'utf8', '-c', code,
                            str(Path(__file__).resolve().parents[1] / 'src')],
                           capture_output=True, timeout=15, env=tt.env_con())
        self.assertEqual(p.returncode, 0, p.stderr.decode('utf-8', errors='replace'))


def _dau_vao_v2(lease):
    tep = str(uuid4())
    return dict(yeu_cau=dict(loai_viec='BOC_TACH_HOP_DONG', van_ban=VAN_BAN,
            chi_dan='Trích số tiền DEMO kèm căn cứ.', truong=['so_tien'],
            ma_function='trich_hop_dong', ma_prompt='trich_tien', phien_ban_prompt='1.0.0'),
        nguon_core=dict(ma_module=lease.module, ma_function='trich_hop_dong',
            ma_prompt='trich_tien', phien_ban_prompt='1.0.0',
            phap_nhan_id=str(lease.phap_nhan_id), viec_id=str(lease.viec_id),
            revision=1, nguon_tep_ids=[tep], vi_tri=dict(tep_id=tep, dinh_vi='doan:1')),
        du_lieu_ket_qua=dict(bien_the='ocr', ma_contract='tra_loi_ai.v2',
            phien_ban_contract='2.0.0', trang_thai='thanh_cong', ly_do=None,
            revision_truoc=0, nguon=[dict(tep_id=tep, sha256='a'*64)]), revision_tep_truoc=0)


class KenhHoiV2(KenhCore):
    def __init__(self, lease):
        self.input = _dau_vao_v2(lease)
        self.lease, self.calls, self.results = lease, [], []
        self.ack = {'ket_qua_id': str(uuid4()), 'da_ban_giao': True}
        self.on_end = lambda: None

    def nhan_viec(self):
        self.calls.append('nhan_viec')
        return self.lease

    def ket_thuc(self, giu, **data):
        self.calls.append(('ket_thuc', data))
        self.on_end()
        return True

    def goi(self, operation, giu_viec, **payload):
        self.calls.append(operation)
        if operation == 'heartbeat':
            return giu_viec
        if operation == 'doc_dau_vao':
            return deepcopy(self.input)
        if operation == 'ghi_ket_qua':
            assert payload['ten'] == 'tra-loi-ai.json'
            assert payload['du_lieu'] == self.input['du_lieu_ket_qua']
            self.results.append(json.load(payload['luong']))
            return self.ack
        raise AssertionError(operation)


class AIRuntimeV2Test(unittest.TestCase):
    def setUp(self):
        from kho_tri_thuc.core.dispatcher import KiemSchema
        from kho_tri_thuc.engines.e_hoi_ai.lib import cong_ai as ca
        self.ca, self.check = ca, KiemSchema().kiem
        self.lease = _lease()
        self.kenh = KenhHoiV2(self.lease)
        self.local = MagicMock(return_value=json.dumps(dict(truong=[dict(ten='so_tien',
            gia_tri='1.234.567 đồng', trich_dan=VAN_BAN)], do_tin_cay=0.99), ensure_ascii=False))
        self.cfg = {'local_ai': {'enabled': True, 'model': 'local-DEMO',
            'url': 'http://127.0.0.1:1234/v1/chat/completions'}, 'cong_ai': {'cloud_bat': True},
            'model_phat_hien': [dict(id_model='local-DEMO', trang_thai='san_sang', bat=True)],
            'quy_tac_model': [dict(module='*', function='*', uu_tien='local-DEMO',
                du_phong=[], che_do='tu_chon', bat=True)]}
        self.bo = ca.BoGhiBoNho()
        self.cong = ca.CongAI(self.cfg, bo_ghi=self.bo, moi_truong={},
            mask=ai._MaskTat(), local_transport=self.local)
        self.enterContext(patch('socket.socket', side_effect=AssertionError('Cấm mạng thật')))
        self.enterContext(patch.object(ca, 'doc_khoa_mask', side_effect=AssertionError('Cấm đọc khóa')))
        self.cloud = self.enterContext(patch.object(ca.CongAI, '_cloud',
            side_effect=AssertionError('Cấm Cloud')))
        self.enterContext(patch.dict(ai.ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        self.discover = self.enterContext(patch.object(ai.ai_cuc_bo, 'discover_local_models',
            return_value=dict(ma_loi='', model_phat_hien=[
                dict(id_model=model, trang_thai='san_sang')
                for model in ('local-DEMO', 'function-DEMO', 'khac-DEMO')])))

    def goi(self):
        return ai.xu_ly_viec(SDKEngine(self.lease, kenh_core=self.kenh),
            provider=self.cong, kiem_schema=self.check)

    def test_v2_thuc_thi_cong_local_khong_mask_khoa_cloud_giu_unicode(self):
        original = deepcopy(self.kenh.input)
        self.assertEqual(self.goi(), self.kenh.ack)
        out, = self.kenh.results
        self.assertTrue(self.check({'$ref': ai.TRA_LOI}, out))
        self.assertEqual((out['contract'], out['phien_ban'], out['duong']),
                         ('tra_loi_ai.v2', '2.0.0', 'LOCAL'))
        self.assertEqual(out['truong'][0]['gia_tri']['gia_tri'], '1.234.567 đồng')
        self.assertEqual(out['nguon_tep_ids'], original['nguon_core']['nguon_tep_ids'])
        self.assertEqual(self.kenh.input, original)
        self.cloud.assert_not_called()

    def test_v2_thieu_trang_prompt_binding_sai_va_co_cloud_bi_chan_truoc_model(self):
        for doi in ({'chi_dan': ''}, {'chi_dan': ' \t\n'}, {'ma_function': 'gia_danh'},
                    {'ma_prompt': 'gia_danh'}, {'phien_ban_prompt': '2'}, {'chi_cuc_bo': False}):
            with self.subTest(doi=doi):
                self.kenh.input = _dau_vao_v2(self.lease)
                self.kenh.input['yeu_cau'].update(doi)
                with self.assertRaises(ValueError):
                    self.goi()
        self.local.assert_not_called()
        self.assertEqual(self.kenh.results, [])

    def cau_hinh_model_theo_function(self):
        config = self.cong.cau_hinh_model
        config['model_phat_hien'].extend(dict(id_model=model, trang_thai='san_sang', bat=True)
            for model in ('function-DEMO', 'khac-DEMO'))
        config['quy_tac_model'].extend([
            dict(module=self.lease.module, function='*', uu_tien='local-DEMO',
                du_phong=[], che_do='tu_chon', bat=True),
            dict(module=self.lease.module, function='trich_hop_dong', uu_tien='function-DEMO',
                du_phong=['local-DEMO'], che_do='tu_chon', bat=True),
            dict(module=self.lease.module, function='gia_danh', uu_tien='khac-DEMO',
                du_phong=[], che_do='co_dinh', bat=True)])
        return config

    def test_v2_runtime_chon_model_theo_function_core_va_du_phong_dung_quy_tac(self):
        config = self.cau_hinh_model_theo_function()
        for san_sang, model, reason in ((True, 'function-DEMO', 'uu_tien'),
                                       (False, 'local-DEMO', 'du_phong:1')):
            with self.subTest(san_sang=san_sang):
                config['model_phat_hien'][1]['bat'] = san_sang
                original = deepcopy((self.kenh.input, self.cfg, config, self.cong.local_ai))
                self.assertEqual(self.goi(), self.kenh.ack)
                out = self.kenh.results[-1]
                self.assertEqual(json.loads(self.local.call_args.args[1])['model'], model)
                self.assertEqual(out['mo_hinh'][0]['ten'], model)
                record = self.bo.ban_ghi[-1]
                self.assertEqual((record.model, record.da_gui), (model, True))
                self.assertIn(reason, record.ly_do)
                self.assertEqual((self.kenh.input, self.cfg, config, self.cong.local_ai), original)
        self.cloud.assert_not_called()

    def test_v2_runtime_khong_chon_function_gia_danh_tu_payload(self):
        self.cau_hinh_model_theo_function()
        original = deepcopy(self.kenh.input)
        for doi in ({'ma_function': 'gia_danh'}, {'ma_prompt': 'gia_danh'},
                    {'phien_ban_prompt': '2'},
                    {'nguon_core': {**original['nguon_core'], 'ma_function': 'gia_danh'}}):
            with self.subTest(doi=doi):
                self.kenh.input = deepcopy(original)
                self.kenh.input['yeu_cau'].update(doi)
                with self.assertRaises(ValueError):
                    self.goi()
        self.assertEqual(self.kenh.input['nguon_core'], original['nguon_core'])
        self.local.assert_not_called()
        self.cloud.assert_not_called()
        self.assertEqual(self.bo.ban_ghi, [])
        self.assertEqual(self.kenh.results, [])

    def test_v2_khong_can_cu_khac_loi_ket_noi_va_model_khong_fallback(self):
        self.local.return_value = json.dumps(dict(truong=[], do_tin_cay=0.99))
        self.goi()
        out = self.kenh.results[-1]
        self.assertEqual(out['ly_do'], ['KHONG_THAY_CAN_CU'])
        self.assertEqual(out['cau_tra_loi'], 'Không thấy căn cứ trong tài liệu.')
        for exc in (ValueError('Model DEMO lỗi'), ai.ai_cuc_bo.LocalAIUnavailable('Mất kết nối DEMO')):
            with self.subTest(exc=type(exc).__name__):
                self.local.side_effect = exc
                self.goi()
                out = self.kenh.results[-1]
                self.assertEqual(out['duong'], 'KHONG')
                self.assertNotIn('KHONG_THAY_CAN_CU', out['ly_do'])
        self.cloud.assert_not_called()

    def test_v2_retry_ack_khong_goi_model_lan_hai_mat_lease_dung(self):
        goc, gui = self.kenh.goi, []
        def goi(op, giu, **kw):
            if op == 'ghi_ket_qua':
                gui.append(kw['luong'])
                if len(gui) == 1:
                    kw['luong'].read()
                    raise RuntimeError('DEMO mất ACK')
            return goc(op, giu, **kw)
        self.kenh.goi = goi
        self.goi()
        self.assertIs(gui[0], gui[1])
        self.local.assert_called_once()
        def mat(op, giu, **kw):
            if op == 'ghi_ket_qua':
                raise LoiEngine('VIEC_MAT_LEASE')
            return goc(op, giu, **kw)
        self.kenh.goi = mat
        with self.assertRaisesRegex(LoiEngine, 'VIEC_MAT_LEASE'):
            self.goi()

    def test_hang_viec_lease_heartbeat_ack_ket_thuc_va_drain(self):
        vong = ai._VongNhan(MagicMock(), MagicMock(), self.cong)
        vong.kiem_schema = self.check
        self.kenh.on_end = vong.ngung_accept
        vong._chay_kenh(self.kenh)
        self.assertEqual(self.kenh.calls[:3], ['nhan_viec', 'heartbeat', 'doc_dau_vao'])
        self.assertEqual(self.kenh.calls[-1], ('ket_thuc', dict(trang_thai='XONG',
            ket_qua_id=self.kenh.ack['ket_qua_id'], ma_loi=None)))
        self.local.assert_called_once()

    def test_ngat_kenh_khi_chua_nhan_viec_thoat_sach_va_drain_xong(self):
        bootstrap, conn = MagicMock(), MagicMock()
        bootstrap.accept.side_effect = [(conn, None), bs.LoiBootstrap('CHUA_CO_QUYEN_ACCEPT')]
        kenh = self.kenh
        kenh.nhan_viec = MagicMock(side_effect=LoiEngine())
        nhan = MagicMock(return_value=kenh)
        vong = ai._VongNhan(bootstrap, nhan, self.cong)
        vong.bat_dau()
        vong.worker.join(2)
        self.assertFalse(vong.worker.is_alive())
        self.assertFalse(vong.loi)
        self.assertTrue(vong.drain())
        self.assertEqual(kenh.calls, [])
        self.local.assert_not_called()

    def test_chua_san_sang_va_hang_rong_tiep_tuc_cho_truoc_khi_ngat_kenh(self):
        bootstrap, conn = MagicMock(), MagicMock()
        bootstrap.accept.side_effect = [(conn, None), bs.LoiBootstrap('CHUA_CO_QUYEN_ACCEPT')]
        chua_san_sang = LoiEngine('CHUA_SAN_SANG')
        chua_san_sang.thu_lai_duoc = True
        self.kenh.nhan_viec = MagicMock(side_effect=[chua_san_sang, None, LoiEngine()])
        vong = ai._VongNhan(bootstrap, MagicMock(return_value=self.kenh), self.cong)
        vong.bat_dau()
        vong.worker.join(2)
        self.assertFalse(vong.worker.is_alive())
        self.assertEqual(self.kenh.nhan_viec.call_count, 3)
        self.assertFalse(vong.loi)
        self.assertTrue(vong.drain())
        self.local.assert_not_called()

    def test_v2_drain_giu_ket_qua_va_cho_ca_ack_ket_thuc(self):
        vong = ai._VongNhan(MagicMock(), MagicMock(), self.cong)
        vong.kiem_schema = self.check
        cho_ack, da_ack = threading.Event(), threading.Event()
        goc, gui, end_calls = self.kenh.goi, [], []
        def goi(op, giu, **kw):
            if op == 'ghi_ket_qua':
                gui.append(kw['luong'])
                if len(gui) == 1:
                    raise RuntimeError('DEMO chưa ACK')
                cho_ack.set()
                if not da_ack.wait(3):
                    raise AssertionError('Không nhận ACK giả')
            return goc(op, giu, **kw)
        def ket_thuc(giu, **kw):
            end_calls.append(kw)
            if len(end_calls) == 1:
                raise LoiEngine()
            return True
        self.kenh.goi, self.kenh.ket_thuc = goi, ket_thuc
        vong.worker = threading.Thread(target=vong._chay_kenh, args=(self.kenh,))
        vong.worker.start()
        try:
            self.assertTrue(cho_ack.wait(2))
            vong.ngung_accept()
            self.assertFalse(vong.drain())
            self.assertFalse(gui[0].closed)
            self.assertEqual(end_calls, [])
        finally:
            da_ack.set()
            vong.worker.join(3)
        self.assertFalse(vong.worker.is_alive())
        self.assertTrue(vong.drain())
        self.assertIs(gui[0], gui[1])
        self.assertEqual(end_calls, [end_calls[0]] * 2)
        self.local.assert_called_once()

    def test_mac_dinh_khong_provider_demo_va_readiness_dung_model(self):
        with patch.object(ai, 'ProviderAIGia') as gia, patch.object(ai.Bootstrap, 'nhan') as nhan:
            with self.assertRaises(TypeError):
                ai.chay(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None)
        gia.assert_not_called()
        nhan.assert_not_called()
        with patch.object(ai.ai_cuc_bo, 'discover_local_models') as discover:
            for model, status, error, dat in (
                ('local-DEMO', 'san_sang', '', True), ('local-DEMO', 'da_tai', '', True),
                ('khac-DEMO', 'san_sang', '', False), ('local-DEMO', 'chua_ro', '', False),
                ('local-DEMO', 'san_sang', 'LOCAL_AI_KET_NOI_LOI', False)):
                discover.return_value = dict(ma_loi=error,
                    model_phat_hien=[dict(id_model=model, trang_thai=status)])
                self.assertEqual(ai._kiem_local(self.cong), dat)

    def cau_hinh_du_phong(self, module='*', function='*', che_do='tu_chon'):
        config = self.cong.cau_hinh_model
        config['model_phat_hien'] = [
            dict(id_model='local-DEMO', trang_thai='san_sang', bat=True),
            dict(id_model='du-phong-DEMO', trang_thai='san_sang', bat=True)]
        config['quy_tac_model'] = [dict(module=module, function=function,
            uu_tien='local-DEMO', du_phong=['du-phong-DEMO'], che_do=che_do, bat=True)]
        return config

    def test_readiness_du_phong_theo_wildcard_va_quy_tac_rieng_khi_model_cu_mat(self):
        for module, function in (('*', '*'), (self.lease.module, '*'),
                                 ('*', 'trich_hop_dong'), (self.lease.module, 'trich_hop_dong')):
            with self.subTest(module=module, function=function):
                config = self.cau_hinh_du_phong(module, function)
                original = deepcopy((self.cfg, config, self.cong.local_ai))
                with patch.object(ai.ai_cuc_bo, 'discover_local_models', return_value=dict(
                        ma_loi='', model_phat_hien=[dict(id_model='du-phong-DEMO',
                            trang_thai='san_sang', bat=False)])):
                    self.assertTrue(ai._kiem_local(self.cong))
                    self.assertEqual(self.goi(), self.kenh.ack)
                self.assertEqual((self.cfg, config, self.cong.local_ai), original)
                self.assertEqual(json.loads(self.local.call_args.args[1])['model'], 'du-phong-DEMO')
                record = self.bo.ban_ghi[-1]
                self.assertEqual((record.model, record.ly_do_chon_model),
                                 ('du-phong-DEMO', 'du_phong:1'))
                self.assertIn('du_phong:1', record.ly_do)
        self.cloud.assert_not_called()

    def test_runtime_co_dinh_model_mat_khong_gui_du_phong(self):
        config = self.cau_hinh_du_phong(che_do='co_dinh')
        original = deepcopy(config)
        self.discover.return_value = dict(ma_loi='', model_phat_hien=[
            dict(id_model='du-phong-DEMO', trang_thai='san_sang')])
        self.assertFalse(ai._kiem_local(self.cong))
        self.assertEqual(self.goi(), self.kenh.ack)
        out = self.kenh.results[-1]
        self.assertEqual(out['duong'], 'KHONG')
        self.assertIn('LOCAL_MODEL_CO_DINH_KHONG_SAN_SANG', out['ly_do'])
        self.assertEqual(out['mo_hinh'], [])
        self.assertEqual(config, original)
        self.assertFalse(self.bo.ban_ghi[-1].da_gui)
        self.local.assert_not_called()
        self.cloud.assert_not_called()

    def test_runtime_do_lai_discovery_sau_readiness_khong_dung_ket_qua_cu(self):
        config = self.cau_hinh_du_phong()
        original = deepcopy(config)
        def snapshot(*models, ma_loi=''):
            return dict(ma_loi=ma_loi, model_phat_hien=[
                dict(id_model=model, trang_thai='san_sang') for model in models])
        snapshots = [snapshot('local-DEMO', 'du-phong-DEMO'),
                     snapshot('du-phong-DEMO'), snapshot('local-DEMO'),
                     snapshot('local-DEMO', ma_loi='LOCAL_AI_KET_NOI_LOI'), snapshot()]
        self.discover.side_effect = deepcopy(snapshots)
        self.assertTrue(ai._kiem_local(self.cong))
        for model, reason in (('du-phong-DEMO', 'du_phong:1'), ('local-DEMO', 'uu_tien')):
            with self.subTest(model=model):
                self.goi()
                self.assertEqual(json.loads(self.local.call_args.args[1])['model'], model)
                record = self.bo.ban_ghi[-1]
                self.assertEqual((record.model, record.ly_do_chon_model), (model, reason))
        for _ in range(2):
            self.goi()
            out = self.kenh.results[-1]
            self.assertEqual(out['duong'], 'KHONG')
            self.assertIn('LOCAL_KHONG_CO_MODEL', out['ly_do'])
            self.assertFalse(self.bo.ban_ghi[-1].da_gui)
        self.assertEqual((self.discover.call_count, self.local.call_count), (5, 2))
        self.assertEqual(config, original)
        self.cloud.assert_not_called()

    def test_runtime_discovery_du_phong_provenance_ban_giao_core_dung_model_ly_do(self):
        from kho_tri_thuc.engines.e_hoi_ai.nhat_ky import BoGhiQuaCore
        config = self.cau_hinh_du_phong()
        original = deepcopy(config)
        sdk = MagicMock(spec_set=SDKEngine)
        for key in ('yeu_cau', 'nguon_core'):
            self.kenh.input[key]['phien_ban_prompt'] = '1'
        sdk.doc_dau_vao.return_value = dict(nguon_core=deepcopy(self.kenh.input['nguon_core']),
            nhat_ky_ai=dict(tep_ids=[], du_lieu_ket_qua=deepcopy(METADATA), revision_tep_truoc=0))
        rows = []
        def ghi(**kw):
            rows.append(json.load(kw['luong']))
            self.assertEqual(kw['ten'], 'nhat-ky-ai.json')
            return dict(da_ban_giao=True)
        sdk.ghi_ket_qua.side_effect = ghi
        self.cong.bo_ghi = BoGhiQuaCore(sdk)
        self.discover.return_value = dict(ma_loi='', model_phat_hien=[
            dict(id_model='du-phong-DEMO', trang_thai='san_sang')])
        self.assertTrue(ai._kiem_local(self.cong))
        self.goi()
        row, = rows
        self.assertEqual((row['model'], row['ly_do_chon_model'], row['duong']),
                         ('du-phong-DEMO', 'du_phong:1', 'LOCAL'))
        self.assertEqual(row['ma_function'], 'trich_hop_dong')
        self.assertEqual(row['ma_prompt'], self.kenh.input['nguon_core']['ma_prompt'])
        self.assertEqual((row['da_gui'], row['ket_qua_kiem']), (True, 'dat'))
        self.assertTrue(self.cong.bo_ghi.da_ban_giao())
        self.assertEqual(config, original)
        self.cloud.assert_not_called()

    def test_readiness_khong_can_model_cu_khi_quy_tac_co_model_hop_le(self):
        self.cong.local_ai['model'] = ''
        with patch.object(ai.ai_cuc_bo, 'discover_local_models', return_value=dict(
                ma_loi='', model_phat_hien=[dict(id_model='local-DEMO', trang_thai='san_sang')])):
            self.assertTrue(ai._kiem_local(self.cong))

    def test_readiness_khong_model_duoc_phep_chon_thi_khong_san_sang(self):
        original = deepcopy(self.cong.cau_hinh_model)
        for case in ('tat_model', 'model_chua_san_sang', 'tat_quy_tac', 'thieu_quy_tac',
                     'khong_model', 'model_ngoai_quy_tac', 'co_dinh_mat_uu_tien'):
            with self.subTest(case=case):
                config = self.cong.cau_hinh_model = deepcopy(original)
                rule = config['quy_tac_model'][0]
                if case == 'tat_model':
                    config['model_phat_hien'][0]['bat'] = False
                elif case == 'model_chua_san_sang':
                    config['model_phat_hien'][0]['trang_thai'] = 'chua_ro'
                elif case == 'tat_quy_tac':
                    rule['bat'] = False
                elif case == 'thieu_quy_tac':
                    config['quy_tac_model'] = []
                elif case == 'khong_model':
                    config['model_phat_hien'] = []
                else:
                    rule['uu_tien'] = 'model-da-mat-DEMO'
                    if case == 'co_dinh_mat_uu_tien':
                        rule.update(che_do='co_dinh', du_phong=['local-DEMO'])
                with patch.object(ai.ai_cuc_bo, 'discover_local_models', return_value=dict(
                        ma_loi='', model_phat_hien=[dict(id_model='local-DEMO',
                            trang_thai='san_sang', bat=True)])):
                    self.assertFalse(ai._kiem_local(self.cong))
        self.local.assert_not_called()
        self.cloud.assert_not_called()

    def test_bootstrap_local_khong_mask_khoa_va_cong_bo_contract_manifest(self):
        b = bs.Bootstrap()
        b.socket, b.bo_doc = MagicMock(), MagicMock()
        b.bi_mat = bs.BiMatBootstrap(b'{}')
        b._duoc_accept, b._ra = False, io.BytesIO()
        seen = []
        def ready(**kw):
            self.assertEqual(kw['contracts'], ai.CONTRACTS)
            self.assertIs(kw['kiem_san_sang'](), True)
        bo = MagicMock()
        bo.da_ban_giao.return_value = True
        with patch.object(ai.Bootstrap, 'nhan', return_value=b), \
                patch.object(ai.Bootstrap, 'bao_san_sang', side_effect=ready), \
                patch.object(ai.Bootstrap, 'cho_thu_hoi',
                    side_effect=lambda **kw: seen.append(kw['drain']())), \
                patch.object(ai._VongNhan, 'bat_dau'), \
                patch.object(ai, '_kiem_local', return_value=True):
            ai.chay(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None,
                settings=self.cfg, bo_ghi=bo, kiem_schema=self.check, local_transport=self.local)
        manifest = json.loads((Path(__file__).resolve().parents[1] /
            'engines/e_hoi_ai/engine.json').read_text(encoding='utf-8'))
        self.assertEqual(ai.CAPABILITY, manifest['capability'][0]['ma'])
        self.assertEqual(ai.CONTRACTS, [manifest['capability'][0][x] for x in ('dau_vao', 'dau_ra')])
        self.assertEqual(seen, [True])
        self.local.assert_not_called()

    def test_doc_cau_hinh_manifest_chap_nhan_noi_bo_khong_doi_dau_vao(self):
        for address in ('http://127.0.0.1:1234', 'http://192.168.90.123:1234',
                        'http://10.0.0.2:1234', 'http://100.100.1.2:1234',
                        'http://[fd7a:115c:a1e0::2]:1234'):
            config = deepcopy(self.cfg)
            config['local_ai']['url'] = address + '/v1/chat/completions'
            original = deepcopy(config)
            with self.subTest(address=address):
                read = ai.doc_cau_hinh_local(config, kiem_schema=self.check)
                self.assertEqual(read, config)
                self.assertIsNot(read, config)
                self.assertEqual(config, original)
        self.local.assert_not_called()
        self.cloud.assert_not_called()
        self.discover.assert_not_called()

    def test_cau_hinh_cu_khoa_la_url_ngoai_noi_bo_chan_truoc_worker_va_thu_hoi_bootstrap(self):
        cases = [dict(local_ai=dict(models=[], quy_tac=[], dia_chi='DEMO'))]
        for section in (None, 'local_ai', 'model_phat_hien', 'quy_tac_model'):
            config = deepcopy(self.cfg)
            target = config if section is None else config[section]
            if isinstance(target, list):
                target = target[0]
            target['truong_la'] = True
            cases.append(config)
        for address in ('http://8.8.8.8:1234/v1/chat/completions',
                        'http://ai.example.invalid:1234/v1/chat/completions',
                        'http://169.254.1.2:1234/v1/chat/completions'):
            config = deepcopy(self.cfg)
            config['local_ai']['url'] = address
            cases.append(config)
        for config in cases:
            original = deepcopy(config)
            bootstrap = bs.Bootstrap()
            bootstrap.socket = MagicMock()
            bootstrap.bi_mat = bs.BiMatBootstrap(b'{}')
            with self.subTest(config=config), patch.object(ai, '_VongNhan') as worker, \
                    patch.object(ai.bm.BiMatRAM, 'tu_bootstrap') as secret:
                with self.assertRaisesRegex(bs.LoiBootstrap, 'Cần lưu lại cấu hình'):
                    ai.chay_tu_core(bootstrap=bootstrap, kiem_chu_ky=MagicMock(),
                        nhan_viec=MagicMock(), settings=config, bo_ghi=MagicMock(), kiem_schema=self.check)
                worker.assert_not_called()
                secret.assert_not_called()
                bootstrap.socket.close.assert_called_once()
                with self.assertRaises(bs.LoiBootstrap):
                    bootstrap.bi_mat.lay_mot_lan()
                self.assertEqual(config, original)
        self.local.assert_not_called()
        self.cloud.assert_not_called()
        self.discover.assert_not_called()

    def test_readiness_local_loi_khong_ready_khong_worker_thu_hoi_ram(self):
        b = bs.Bootstrap()
        b.socket, b.bo_doc = MagicMock(), MagicMock()
        b.bi_mat = bs.BiMatBootstrap(b'{}')
        b._duoc_accept, b._ra = False, io.BytesIO()
        with patch.object(ai.Bootstrap, 'nhan', return_value=b), \
                patch.object(ai._VongNhan, 'bat_dau') as start, \
                patch.object(ai.ai_cuc_bo, 'discover_local_models', return_value=dict(
                    ma_loi='LOCAL_AI_KET_NOI_LOI', model_phat_hien=[])):
            with self.assertRaisesRegex(bs.LoiBootstrap, 'CHUA_SAN_SANG'):
                ai.chay(kiem_chu_ky=lambda *_: None, nhan_viec=lambda *_: None,
                    settings=self.cfg, bo_ghi=MagicMock(), kiem_schema=self.check)
        start.assert_not_called()
        self.local.assert_not_called()
        b.socket.close.assert_called_once()
        self.assertEqual(b._ra.getvalue(), b'')


@unittest.skipUnless(os.name == 'nt' and hasattr(socket.socket, 'share'),
                     'CHUA_KIEM: cần Windows share/fromshare và Job')
class AITienTrinhTest(unittest.TestCase):
    def setUp(self):
        self.controllers = []
        self.addCleanup(self._dong)

    def _dong(self):
        for c in self.controllers:
            if c._proc is not None:
                try:
                    c.thu_hoi(timeout=5)
                except tt.LoiTienTrinh:
                    c._job.ket_thuc()  # Chỉ Job test sở hữu.
                    c._proc.wait(5)
                    c.kiem_con()
            c.dong()

    def _tao(self, cong=None):
        if cong is None:
            with socket.socket() as tam:
                tam.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                tam.bind(('127.0.0.1', 0))
                cong = tam.getsockname()[1]
        d = _dong()
        d.update(module=None, engine_ho_so_id=str(uuid4()), cong=cong)
        so = SoGia(d)
        c = tt.TienTrinhCore(so_cong_id=d['id'], giao_dich=so.giao_dich,
            lenh=[sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--child'],
            phien_ban=ai.PHIEN_BAN, issuer='core-demo', contracts=[], ma_chu='e_hoi_ai',
            cho_khoi_dong=10, cho_dung=0.2)
        self.controllers.append(c)
        return c, so

    def _ket_noi(self, so):
        conn = socket.create_connection(('127.0.0.1', so.dong['cong']), timeout=3)
        self.addCleanup(conn.close)
        return conn

    def _kiem_ket_qua(self, reader):
        kq = json.loads(reader.readline())
        self.assertEqual(kq['ly_do'], ['GIA_LAP'])
        self.assertEqual(kq['truong']['noi_dung']['gia_tri'], VAN_BAN)

    def test_khoi_dong_job_ready_viec_gia_va_drain_cung_listener(self):
        c, so = self._tao()
        c.khoi_dong()
        proc, job = c._proc, c._job
        self.assertEqual((c.trang_thai, c.chu_accept), ('ready', 'con'))
        self.assertGreaterEqual(job.so_tien_trinh(), 1)
        self.assertEqual(so.dong['trang_thai'], 'CON_GIU')
        with self.assertRaisesRegex(tt.LoiTienTrinh, 'CORE_KHONG_CO_QUYEN_ACCEPT'):
            c.accept()
        with self._ket_noi(so) as conn:
            conn.sendall(b'DEMO_AI4A\n')
            with conn.makefile('rb') as reader:
                self._kiem_ket_qua(reader)
        self.assertTrue(c.thu_hoi(timeout=5))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual((c.chu_accept, so.dong['trang_thai']), ('core', 'TRONG'))
        with self._ket_noi(so):
            accepted, _ = c.accept(timeout=3)
            accepted.close()

    def test_drain_cho_core_ack_sau_6_giay_khong_kill_khong_nhan_viec_moi(self):
        c, so = self._tao()
        c.khoi_dong()
        proc, job = c._proc, c._job
        conn = self._ket_noi(so)
        conn.sendall(b'DEMO_AI4A_GIU\n')
        reader = conn.makefile('rb')
        self.addCleanup(reader.close)
        self.assertEqual(reader.readline(), b'cho_core\n')
        bat_dau_cho = time.monotonic()
        with self.assertRaisesRegex(tt.LoiTienTrinh, 'DUNG_CHUA_XAC_NHAN'):
            c.thu_hoi(timeout=0.05)
        self.assertIsNone(proc.poll())
        self.assertGreaterEqual(job.so_tien_trinh(), 1)
        self.assertEqual((c.trang_thai, c.chu_accept), ('dang_dung', 'con'))
        self.assertNotIn('tra', [ten for ten, _ in so.go])
        moi = self._ket_noi(so)
        moi.sendall(b'DEMO_AI4A\n')
        moi.settimeout(0.1)
        with self.assertRaises(socket.timeout):
            moi.recv(1024)
        time.sleep(max(0, 6 - (time.monotonic() - bat_dau_cho)))
        self.assertIsNone(proc.poll())
        self.assertGreaterEqual(job.so_tien_trinh(), 1)
        self.assertEqual((c.trang_thai, c.chu_accept), ('dang_dung', 'con'))
        self.assertNotIn('tra', [ten for ten, _ in so.go])
        conn.sendall(b'core_da_nhan\n')
        self._kiem_ket_qua(reader)
        proc.wait(5)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(c.kiem_con())
        self.assertEqual(so.dong['trang_thai'], 'TRONG')

    def test_ranh_thu_hoi_va_restart_doi_nonce_giu_cong(self):
        c, so = self._tao()
        c.khoi_dong()
        nonce, instance, listener = c._nonce, c.instance_id, c._nghe
        self.assertTrue(c.thu_hoi(timeout=5))
        c.khoi_dong()
        self.assertEqual(c.the_he, 2)
        self.assertNotEqual(c._nonce, nonce)
        self.assertNotEqual(c.instance_id, instance)
        self.assertIs(c._nghe, listener)
        with self._ket_noi(so) as conn:
            conn.sendall(b'DEMO_AI4A\n')
            with conn.makefile('rb') as reader:
                self._kiem_ket_qua(reader)
        self.assertTrue(c.thu_hoi(timeout=5))

    def test_loi_truoc_ack_tien_trinh_song_bao_chua_drain_thu_lai_dat(self):
        c, so = self._tao()
        c.khoi_dong()
        proc, job = c._proc, c._job
        conn = self._ket_noi(so)
        conn.sendall(b'DEMO_AI4A_LOI\n')
        reader = conn.makefile('rb')
        self.addCleanup(reader.close)
        self.assertEqual(reader.readline(), b'loi_truoc_ack\n')
        self.assertIsNone(proc.poll())
        self.assertEqual(reader.readline(), b'thu_lai_cho_ack\n')
        with self.assertRaisesRegex(tt.LoiTienTrinh, 'DUNG_CHUA_XAC_NHAN'):
            c.thu_hoi(timeout=0.3)
        self.assertEqual(bs.doc_thong_diep(tt._doc_dong(proc.stdout, 3)), {
            'protocol': bs.PROTOCOL, 'kieu': 'drain_chua_xong'})
        self.assertIsNone(proc.poll())
        self.assertGreaterEqual(job.so_tien_trinh(), 1)
        self.assertEqual((c.trang_thai, c.chu_accept), ('dang_dung', 'con'))
        self.assertNotIn('tra', [ten for ten, _ in so.go])
        conn.sendall(b'core_da_nhan\n')
        self._kiem_ket_qua(reader)
        self.assertEqual(bs.doc_thong_diep(tt._doc_dong(proc.stdout, 5)), {
            'protocol': bs.PROTOCOL, 'kieu': 'da_thu_hoi'})
        proc.wait(5)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(c.kiem_con())
        self.assertEqual(so.dong['trang_thai'], 'TRONG')

    def test_version_hoac_capability_sai_khong_ready(self):
        for truong, value in (('_phien_ban', 'KHAC_BAN_RUNTIME'),
                              ('_contracts', ['ai.hoi@1'])):
            with self.subTest(truong=truong):
                c, so = self._tao()
                setattr(c, truong, value)
                self._kiem_ba_lan_loi_khoi_dong(c, so, 'TIEN_TRINH_KHONG_HOP_LE')
                self.assertNotIn('san_sang', [ten for ten, _ in so.go])

    def _kiem_ba_lan_loi_khoi_dong(self, c, so, ma_loi):
        for lan, giay in ((1, 2), (2, 4), (3, None)):
            truoc = datetime.now(timezone.utc)
            ma = ma_loi if lan < 3 else 'KHOI_DONG_BI_KHOA'
            with self.assertRaisesRegex(tt.LoiTienTrinh, ma):
                c.khoi_dong()
            sau = datetime.now(timezone.utc)
            self.assertEqual(so.dong['so_loi_khoi_dong'], lan)
            self.assertEqual(so.dong['trang_thai'], 'LOI' if lan == 3 else 'CORE_GIU')
            self.assertEqual(so.dong['ma_loi'], ma_loi if lan == 3 else None)
            self.assertEqual(so.dong['ma_loi_khoi_dong'], ma_loi)
            if giay is not None:
                han = datetime.fromisoformat(so.dong['thu_lai_sau'])
                self.assertGreaterEqual(han, truoc + timedelta(seconds=giay))
                self.assertLessEqual(han, sau + timedelta(seconds=giay))
                with patch.object(tt, 'datetime', wraps=datetime) as dong_ho:
                    dong_ho.now.return_value = han - timedelta(seconds=giay)
                    with self.assertRaisesRegex(tt.LoiTienTrinh, 'KHOI_DONG_LOI') as bat:
                        c.khoi_dong()
                self.assertEqual(bat.exception.headers, {'Retry-After': str(giay)})
                self.assertEqual(so.dong['so_loi_khoi_dong'], lan)
                # Cho hết hạn trong fixture, giữ nguyên counter và mã lỗi.
                so.dong['thu_lai_sau'] = (truoc - timedelta(seconds=1)).isoformat()
            else:
                self.assertIsNone(so.dong['thu_lai_sau'])
        with self.assertRaisesRegex(tt.LoiTienTrinh, 'KHOI_DONG_BI_KHOA'):
            c.khoi_dong()
        self.assertEqual(so.dong['so_loi_khoi_dong'], 3)

    def test_cong_bi_chiem_khong_doi_cong_khong_dung_chu_listener(self):
        with socket.socket() as la:
            la.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            la.bind(('127.0.0.1', 0))
            la.listen()
            c, so = self._tao(la.getsockname()[1])
            self._kiem_ba_lan_loi_khoi_dong(c, so, 'CONG_BI_CHIEM')
            self.assertEqual(so.dong['ma_loi'], 'CONG_BI_CHIEM')
            with self._ket_noi(so):
                accepted, _ = la.accept()
                accepted.close()


if __name__ == '__main__':
    if '--child' in sys.argv:
        _child()
    else:
        unittest.main()
