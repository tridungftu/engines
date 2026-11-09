"""AI-5b: nghiệm thu DEMO qua CongAI/SDK thật, mọi transport đều giả.

MaskV2 dùng phản hồi API trong RAM, không có bộ che/detector mới. Core giả
giữ metadata trong RAM để kiểm restart adapter; không chứng nhận độ chính
xác model, Mask thật, Windows ACL/Job hay độ bền kho Core production.
AI-5c kiểm nối bí mật và thu hồi từ lifecycle thật, lỗi Mask không thoát cổng.
AI-5d kiểm drain chờ ACK nhật ký, khóa thu hồi giữa lượt và lỗi seam Mask.
AI-5f kiểm quá hạn vẫn giữ socket/retry, thu khóa sớm và dừng cứng không giả ACK.
QD-20261106-01: runtime bản 1 chỉ Local; ca Cloud bên dưới chỉ kiểm cổng dùng chung.
Chạy: Python 3.12 -B -X utf8 -m unittest discover -s tests -p test_g3_ai_5b.py
"""

import base64
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import io
import json
import logging
import os
from pathlib import Path
import sys
import traceback
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from kho_tri_thuc.core.phien import MaBiMat
from kho_tri_thuc.core.dispatcher import KiemSchema
from kho_tri_thuc.core.viec import GiuViec
from kho_tri_thuc.engines.e_hoi_ai import bi_mat as bm, chay as runtime
from kho_tri_thuc.engines.e_hoi_ai.hoi import AdapterHoiAI
from kho_tri_thuc.engines.e_hoi_ai.nhat_ky import BoGhiQuaCore
from kho_tri_thuc.sdk_core import bootstrap as bs
from kho_tri_thuc.sdk_core.engine import KenhCore, SDKEngine
from kho_tri_thuc.tri_thuc import cong_ai as ca


CANARY = 'AI5B_DEMO_SECRET_0123456789'
KEY_NAME = 'AI5B_DEMO_API_KEY'
LOAI = 'BOC_TACH_HOP_DONG'
TEN = 'Công ty DEMO AI5B'
BI_DANH = '[CONG_TY_005]'
TIEN = '1.234.567 đồng'
NGAY = '02/11/2026'
VAN_BAN = f'{TEN} thanh toán {TIEN} ngày {NGAY}.'
DA_CHE = f'{BI_DANH} thanh toán {TIEN} ngày {NGAY}.'
CHI_DAN = f'Trích số tiền và ngày của {TEN}.'
CHI_DAN_CHE = f'Trích số tiền và ngày của {BI_DANH}.'
YEU_CAU = ca.YeuCauAI(LOAI, VAN_BAN, CHI_DAN, ('so_tien', 'ngay'),
                       ((TEN, 'CONG_TY'),))
TEP = '00000000-0000-4000-8000-000000000001'
LUOT = '00000000-0000-4000-8000-000000000002'
METADATA = dict(bien_the='ai_demo', ma_contract='nhat_ky_ai_demo',
                phien_ban_contract='1', trang_thai='DEMO', ly_do=None,
                revision_truoc=0, nguon=[])


def settings(rate=0.0, *, model_demo=False):
    # Các tỷ lệ chỉ là cấu hình DEMO, không chốt lịch giảm mới của TL48.
    cfg = {'local_ai': {'enabled': True, 'model': 'ai5b-local-demo',
                        'url': 'http://127.0.0.1:1234/v1/chat/completions'},
            'cong_ai': {'cloud_bat': True, 'bien_khoa_api': KEY_NAME,
                        'model': 'ai5b-cloud-demo', 'kiem_xac_suat': {
                            'ty_le_ban_dau': rate, 'ty_le_san': 0.05,
                            'cua_so': 4, 'bac_thang': [[2, 0.95, 0.1]]}}}
    if model_demo:
        cfg.update(model_phat_hien=[dict(loai_phan_mem='openai_compatible',
            id_model=model, trang_thai='san_sang',
            phat_hien_luc='2026-11-07T00:00:00Z', bat=True)
            for model in ('gpt-oss-20b', 'qwen3-8b', 'gemma')],
            quy_tac_model=[dict(module='*', function='*', uu_tien='gpt-oss-20b',
                du_phong=['qwen3-8b', 'gemma'], che_do='tu_chon', bat=True)])
    return cfg


def tra_loi(*, masked=False, confidence=0.99, tien=TIEN, quote=None):
    return json.dumps({'truong': [
        {'ten': 'so_tien', 'gia_tri': tien,
         'trich_dan': quote or (DA_CHE if masked else VAN_BAN)},
        {'ten': 'ngay', 'gia_tri': NGAY,
         'trich_dan': quote or (DA_CHE if masked else VAN_BAN)}],
        'do_tin_cay': confidence}, ensure_ascii=False)


def lenh(kieu):
    return {'protocol': bs.PROTOCOL, 'kieu': kieu}


def nhan_bootstrap(raw, *, tham_so=None, commands=None):
    """Bootstrap thật nhận dòng bí mật riêng; socket/FILETIME hoàn toàn giả."""
    cfg = dict(protocol=bs.PROTOCOL, kieu='khoi_dong', pid=os.getpid(),
               dinh_danh_lan_tao='AI5B_DEMO', cong=23456,
               dia_chi_nghe='127.0.0.1', phien_ban=runtime.PHIEN_BAN,
               the_he=1, issuer='DEMO', module='e_hoi_ai', instance_id='DEMO',
               nonce_khoi_dong='DEMO', socket='REVNTw==',
               tham_so={'cong_khai': 'DEMO'} if tham_so is None else tham_so)
    vao, ra = io.BytesIO(), io.BytesIO()
    for dong in (cfg, {**lenh('bi_mat'), 'du_lieu': base64.b64encode(
            json.dumps(raw).encode('utf-8')).decode('ascii')},
            *(commands if commands is not None else
              [lenh('nhan_accept'), lenh('thu_hoi')])):
        bs.gui_thong_diep(vao, dong)
    vao.seek(0)
    nghe = Mock()
    nghe.getsockname.return_value = ('127.0.0.1', 23456)
    with patch.object(bs, 'dinh_danh_lan_tao', return_value='AI5B_DEMO'), \
            patch.object(bs.socket, 'fromshare', return_value=nghe, create=True), \
            patch.object(bs, 'BoDocNguCanh'):
        return bs.Bootstrap.nhan(kiem_chu_ky=lambda *a: None,
                                 stdin=vao, stdout=ra)


class CoreGia(KenhCore):
    """Chỉ phía Core fixture giữ metadata; engine đi qua SDKEngine thật."""

    def __init__(self):
        self.files = {}
        self.payloads = []
        self.ack = True
        self.loi_doc = False

    def goi(self, operation, giu_viec, **payload):
        if operation == 'doc_dau_vao':
            if self.loi_doc:
                raise RuntimeError(CANARY)
            return {'nhat_ky_ai': {'tep_ids': list(self.files),
                    'du_lieu_ket_qua': deepcopy(METADATA), 'revision_tep_truoc': 0}}
        if operation == 'mo_doc':
            return io.BytesIO(self.files[payload['tep_id']])
        if operation != 'ghi_ket_qua':
            raise AssertionError('Operation ngoài fixture AI5B')
        raw = payload['luong'].read()
        self.payloads.append(raw)
        data = json.loads(raw)
        # Cùng lượt/đường được Core giả nhận lại idempotent khi mất ACK.
        tid = data['ma_yeu_cau'] + ':' + data['duong']
        self.files[tid] = raw
        return {'ket_qua_id': tid, 'da_ban_giao': self.ack}


def bo_ghi(core):
    lease = GiuViec(viec_id=uuid4(), buoc_viec_id=uuid4(), lan_thu_id=uuid4(),
        phap_nhan_id=uuid4(), module='demo', hanh_dong='DEMO:AI:LAP',
        instance_id=uuid4(), the_he=1,
        giu_den=datetime.now(timezone.utc) + timedelta(minutes=2),
        ma=MaBiMat('AI5B_LEASE_DEMO_' + 'x' * 32))
    return BoGhiQuaCore(SDKEngine(lease, kenh_core=core))


class _FixtureAI5b(unittest.TestCase):
    model_demo = False

    def setUp(self):
        # Chặn ngay cả khi code vô tình chọn transport/provider mặc định.
        self.io_guards = []
        for target in ('socket.socket', 'socket.create_connection',
                       'socket.getaddrinfo', 'urllib.request.OpenerDirector.open',
                       'subprocess.Popen'):
            self.io_guards.append(self.enterContext(
                patch(target, side_effect=AssertionError('Cấm I/O thật'))))
        for name in ('doc_khoa_mask', 'BoGhiPostgres',
                     'NhaCungCapAnthropic', 'NhaCungCapOpenAI'):
            self.io_guards.append(self.enterContext(patch.object(ca, name,
                                          side_effect=AssertionError('Cấm nguồn thật'))))
        self.enterContext(patch.object(ca.os, 'environ',
                                       {KEY_NAME: 'AI5B_ENV_CAM',
                                        'ANTHROPIC_API_KEY': 'AI5B_ENV_CAM'}))
        self.events = []
        self.core = CoreGia()
        self.bo = bo_ghi(self.core)
        self.local = Mock(side_effect=self._local)
        self.cloud = Mock()
        self.cloud.tra_loi.side_effect = self._cloud
        # Giữ thuật toán kiểm gui_duoc/con_sot của MaskV2; chỉ thay transport.
        self.mask = object.__new__(ca.MaskV2)
        self.mask.co_khoa = Mock(return_value=True)
        self.mask._goi = Mock(side_effect=self._mask_api)
        self.mask_reply = dict(gui_duoc=True, con_sot=[], danh_muc='da_mo',
                              ma_luot='AI5B-MASK-DEMO', van_ban_da_che=
                              ca.noi_dung_nguoi_dung(replace(YEU_CAU,
                                  van_ban=DA_CHE, chi_dan=CHI_DAN_CHE)))
        self.cfg = settings(model_demo=self.model_demo)
        self.kiem_schema = KiemSchema().kiem
        self.enterContext(patch.object(ca.ai_cuc_bo, 'discover_local_models',
            return_value=dict(ma_loi='', model_phat_hien=deepcopy(
                self.cfg.get('model_phat_hien', [dict(
                    id_model=self.cfg['local_ai']['model'], trang_thai='san_sang')])))))
        self.bootstrap = nhan_bootstrap({KEY_NAME: CANARY})
        self.ram = bm.BiMatRAM.tu_bootstrap(self.bootstrap, self.cfg)
        self.addCleanup(self.ram.thu_hoi)
        self.cong = self.tao_cong()

    def tearDown(self):
        # CongAI có thể bắt AssertionError của transport: vẫn phải báo test lỗi.
        for guard in self.io_guards:
            guard.assert_not_called()

    def tao_cong(self, *, cfg=None, bo=None, ram=None):
        return bm.tao_cong_ai(self.cfg if cfg is None else cfg,
            bi_mat=self.ram if ram is None else ram, mask=self.mask,
            bo_ghi=self.bo if bo is None else bo, nha_cung_cap=self.cloud,
            local_transport=self.local)

    def _local(self, url, body):
        self.events.append('LOCAL')
        return tra_loi()

    def _cloud(self, he_thong, noi_dung, **kwargs):
        self.events.append('CLOUD')
        self.assertEqual(kwargs['khoa'], CANARY)
        self.assertNotIn(TEN, he_thong + noi_dung)
        self.assertIn(DA_CHE, noi_dung)
        self.assertIn(CHI_DAN_CHE, noi_dung)
        self.assertIn(TIEN, noi_dung)
        self.assertIn(NGAY, noi_dung)
        return ca.PhanHoiCloud(tra_loi(masked=True), 'ai5b-cloud-thuc-demo', 12, 8)

    def _mask_api(self, path, body):
        self.events.append(path)
        if path == '/api/v1/trang-thai':
            return {'danh_muc': 'da_mo'}
        if path == '/api/v1/che':
            self.assertIn(VAN_BAN, body['van_ban'])
            self.assertIn(CHI_DAN, body['van_ban'])
            self.assertIn(TIEN, body['van_ban'])
            self.assertIn(NGAY, body['van_ban'])
            return deepcopy(self.mask_reply)
        if path == '/api/v1/mo-che':
            self.assertEqual(body['ma_luot'], 'AI5B-MASK-DEMO')
            self.assertIs(body['ket_thuc_luot'], True)
            # Mở duy nhất bí danh DEMO đã biết, không triển khai bộ che mới.
            return {'van_ban': body['van_ban'].replace(BI_DANH, TEN)}
        raise AssertionError('Endpoint ngoài Mask v2')

    def local_loi(self):
        def loi(*args):
            self.events.append('LOCAL')
            raise RuntimeError(CANARY)
        self.local.side_effect = loi

    def goi(self, **kwargs):
        return self.cong.goi(YEU_CAU, **kwargs)

    def adapter_goi(self, chi_cuc_bo):
        adapter = AdapterHoiAI(self.cong, kiem_schema=self.kiem_schema,
                               tham_chieu_luot_che=lambda *a, **k: LUOT)
        return adapter.goi(dict(loai_viec=LOAI, van_ban=VAN_BAN, chi_dan=CHI_DAN,
            truong=list(YEU_CAU.truong), dinh_danh_da_biet=[[TEN, 'CONG_TY']],
            chi_cuc_bo=chi_cuc_bo), revision=1, nguon_tep_ids=[TEP],
            vi_tri={'tep_id': TEP, 'dinh_vi': 'doan:1'})

    def thong_ke(self, cong=None):
        return next(r for r in (cong or self.cong).thong_ke() if r['loai_viec'] == LOAI)


class CongCloudTest(_FixtureAI5b):
    def test_local_chac_khong_lay_mau_khong_mask_cloud(self):
        out = self.goi()
        self.assertEqual(out.duong, 'LOCAL')
        self.assertEqual(self.events, ['LOCAL'])
        self.cloud.tra_loi.assert_not_called()
        self.mask._goi.assert_not_called()
        self.assertTrue(self.bo.da_ban_giao())

    def test_local_loi_roi_mask_cloud_mo_che_giu_tien_ngay(self):
        self.local_loi()
        out = self.goi()
        self.assertEqual(self.events, ['LOCAL', '/api/v1/trang-thai',
            '/api/v1/che', 'CLOUD', '/api/v1/mo-che'])
        self.assertEqual((out.duong, out.muc), ('CLOUD', 'VANG'))
        self.assertEqual(out.truong['so_tien'].gia_tri, TIEN)
        self.assertEqual(out.truong['ngay'].gia_tri, NGAY)
        self.assertEqual(out.truong['so_tien'].trich_dan, VAN_BAN)
        records = [json.loads(raw) for raw in self.core.files.values()]
        self.assertEqual([r['duong'] for r in records], ['LOCAL', 'CLOUD'])
        self.assertEqual(records[-1]['model'], 'ai5b-cloud-thuc-demo')
        self.assertEqual((records[-1]['token_vao'], records[-1]['token_ra']), (12, 8))

    def test_local_khong_chac_thieu_dan_chung_va_python_bac_deu_thu_cloud(self):
        for answer, kiem in ((tra_loi(confidence=0.3), None),
                             (tra_loi(quote='Ngoài nguồn DEMO'), None),
                             (tra_loi(), Mock(side_effect=[['so_tien'], []]))):
            with self.subTest(answer=answer):
                self.local.side_effect = None
                self.local.return_value = answer
                self.cloud.tra_loi.reset_mock()
                out = self.goi(kiem_tra=kiem)
                self.cloud.tra_loi.assert_called_once()
                self.assertEqual(out.duong, 'CLOUD')

    def test_mask_con_sot_khong_gui_ke_ca_gui_duoc_true(self):
        self.local_loi()
        self.mask_reply['con_sot'] = [{'gia_tri': 'Dinh danh DEMO mới'}]
        out = self.goi()
        self.assertIn('MASK_CON_SOT', out.ly_do)
        self.cloud.tra_loi.assert_not_called()
        record = json.loads(list(self.core.files.values())[-1])
        self.assertFalse(record['da_gui'])
        self.assertEqual(record['ly_do_khong_gui'], 'MASK_CON_SOT')

    def test_mask_phai_xac_nhan_ro_khong_con_sot_va_cho_gui(self):
        self.local_loi()
        original = deepcopy(self.mask_reply)
        for changes in ({'con_sot': None}, {'con_sot': '[]'}, {'gui_duoc': False},
                        {'gui_duoc': 1}, {'danh_muc': 'khoa'}):
            with self.subTest(changes=changes):
                self.mask_reply = {**original, **changes}
                self.assertEqual(self.goi().duong, 'KHONG')
        self.mask_reply = {k: v for k, v in original.items() if k != 'con_sot'}
        self.assertEqual(self.goi().duong, 'KHONG')
        self.cloud.tra_loi.assert_not_called()

    def test_mask_bao_sach_nhung_dinh_danh_da_biet_con_lai_van_chan(self):
        self.local_loi()
        self.mask_reply['van_ban_da_che'] = ca.noi_dung_nguoi_dung(YEU_CAU)
        out = self.goi()
        self.assertIn('CON_SOT_DINH_DANH', out.ly_do)
        self.cloud.tra_loi.assert_not_called()
        self.assertEqual(self.events[-1], '/api/v1/mo-che')  # Kết thúc lượt RAM.

    def test_mask_khoa_khong_chay_phan_hoi_hong_khong_vuot_cong(self):
        self.local_loi()
        for error in (ca.MaskKhongGui('MASK_DANH_MUC_KHOA'),
                      ca.MaskKhongGui('MASK_KHONG_CHAY'), RuntimeError(CANARY)):
            with self.subTest(kieu=type(error).__name__):
                self.mask._goi.side_effect = error
                out = self.goi()
                self.assertEqual(out.duong, 'KHONG')
                self.assertNotIn(CANARY, repr(out))
        self.cloud.tra_loi.assert_not_called()

    def test_mask_loi_kiem_khoa_phai_duoc_cong_chan_va_an_canary(self):
        """Không giữ exception gốc, kể cả cause/context có bí mật."""
        self.local_loi()
        original = RuntimeError(CANARY)
        original.__cause__ = ValueError(CANARY)
        original.__context__ = KeyError(CANARY)
        chain = [original, original.__cause__, original.__context__]
        self.mask.co_khoa.side_effect = original
        error = None
        result = None
        try:
            result = self.goi()
        except Exception as exc:
            error = exc
        self.cloud.tra_loi.assert_not_called()
        self.mask._goi.assert_not_called()
        self.assertIsNone(error, 'Cổng phải chuyển lỗi kiểm khóa Mask thành kết quả an toàn')
        self.assertEqual(result.duong, 'KHONG')
        self.assertIn('MASK_PHAN_HOI_LOI', result.ly_do)
        self.assertNotIn(CANARY, repr(result))
        for exc in chain:
            self.assertIsNone(exc.__context__)
            self.assertIsNone(exc.__cause__)
            self.assertIsNone(exc.__traceback__)
            self.assertNotIn(CANARY, repr(exc))
        record = json.loads(list(self.core.files.values())[-1])
        self.assertEqual(record['ly_do_khong_gui'], 'MASK_PHAN_HOI_LOI')
        self.assertNotIn(CANARY, repr(self.core.payloads))

    def test_loi_kiem_khoa_mask_giu_local_va_trang_thai_an_toan(self):
        self.mask.co_khoa.side_effect = RuntimeError(CANARY)
        # Local chắc không lấy mẫu: không đụng Mask.
        self.assertEqual(self.goi().duong, 'LOCAL')
        self.mask.co_khoa.assert_not_called()
        self.cong = self.tao_cong(cfg=settings(1.0))
        self.cong._kiem_xac_suat = lambda loai: True
        out = self.goi()
        self.assertEqual(out.duong, 'LOCAL')
        self.assertIn('MASK_PHAN_HOI_LOI', out.ly_do)
        state = self.cong.trang_thai(kiem_mask=True)
        self.assertEqual(state['cloud']['ma'], 'MASK_PHAN_HOI_LOI')
        self.assertFalse(state['cloud']['dung_duoc'])
        self.assertNotIn(CANARY, repr(state))
        self.cloud.tra_loi.assert_not_called()
        self.mask._goi.assert_not_called()

    def test_mo_che_het_han_hoac_loi_khong_nhan_ket_qua_cloud(self):
        self.local_loi()
        original = self._mask_api
        def expired(path, body):
            if path == '/api/v1/mo-che':
                raise ca.MaskKhongGui('MASK_LUOT_HET_HAN')
            return original(path, body)
        self.mask._goi.side_effect = expired
        out = self.goi()
        self.cloud.tra_loi.assert_called_once()
        self.assertEqual(out.duong, 'KHONG')
        self.assertIn('MASK_MO_CHE_LOI', out.ly_do)

    def test_khoa_thu_hoi_sau_che_khong_goi_cloud(self):
        self.local_loi()
        original = self.mask.che

        def che(*args):
            luot = original(*args)
            self.ram.thu_hoi()
            return luot

        with patch.object(self.mask, 'che', side_effect=che), \
                patch.object(self.mask, 'ket_thuc', wraps=self.mask.ket_thuc) as done:
            out = self.goi()
        self.assertEqual(out.duong, 'KHONG')
        self.assertIn('CHUA_CO_KHOA_API', out.ly_do)
        self.cloud.tra_loi.assert_not_called()
        done.assert_called_once_with('AI5B-MASK-DEMO')
        record = json.loads(list(self.core.files.values())[-1])
        self.assertFalse(record['da_gui'])
        self.assertEqual(record['ly_do_khong_gui'], 'CHUA_CO_KHOA_API')

    def test_mask_trang_thai_nem_loi_phai_an_ca_exception_chain(self):
        for error in (RuntimeError(CANARY), ca.MaskKhongGui('MASK_KHONG_CHAY')):
            with self.subTest(kieu=type(error).__name__):
                expected = ('MASK_KHONG_CHAY' if isinstance(error, ca.MaskKhongGui)
                            else 'MASK_PHAN_HOI_LOI')
                error.__cause__ = ValueError(CANARY)
                error.__context__ = KeyError(CANARY)
                chain = [error, error.__cause__, error.__context__]
                with patch.object(self.mask, 'trang_thai', side_effect=error):
                    state = self.cong.trang_thai(kiem_mask=True)
                self.assertEqual(state['cloud']['ma'], expected)
                self.assertFalse(state['cloud']['dung_duoc'])
                self.assertNotIn(CANARY, repr(state))
                for exc in chain:
                    self.assertIsNone(exc.__context__)
                    self.assertIsNone(exc.__cause__)
                    self.assertIsNone(exc.__traceback__)
                    self.assertNotIn(CANARY, repr(exc))
        self.cloud.tra_loi.assert_not_called()

    def test_mask_ket_thuc_nem_loi_khong_thoat_goi_khong_lo_canary(self):
        self.local_loi()
        original_reply = deepcopy(self.mask_reply)
        for stage in ('con_sot', 'cloud_loi', 'json_loi'):
            with self.subTest(stage=stage):
                self.mask_reply = deepcopy(original_reply)
                self.cloud.tra_loi.side_effect = self._cloud
                self.cloud.tra_loi.reset_mock()
                if stage == 'con_sot':
                    self.mask_reply['van_ban_da_che'] = ca.noi_dung_nguoi_dung(YEU_CAU)
                elif stage == 'cloud_loi':
                    self.cloud.tra_loi.side_effect = RuntimeError(CANARY)
                else:
                    self.cloud.tra_loi.side_effect = None
                    self.cloud.tra_loi.return_value = ca.PhanHoiCloud('invalid', 'demo', 1, 1)
                error = RuntimeError(CANARY)
                error.__cause__ = ValueError(CANARY)
                error.__context__ = KeyError(CANARY)
                chain = [error, error.__cause__, error.__context__]
                logs = io.StringIO()
                handler = logging.StreamHandler(logs)
                ca._LOG.addHandler(handler)
                try:
                    with patch.object(self.mask, 'ket_thuc', side_effect=error) as done:
                        out = self.goi()
                finally:
                    ca._LOG.removeHandler(handler)
                expected = ('MASK_MO_CHE_LOI' if stage == 'json_loi'
                            else 'MASK_PHAN_HOI_LOI')
                self.assertEqual(out.duong, 'KHONG')
                self.assertIn(expected, out.ly_do)
                done.assert_called_once_with('AI5B-MASK-DEMO')
                if stage == 'con_sot':
                    self.cloud.tra_loi.assert_not_called()
                else:
                    self.cloud.tra_loi.assert_called_once()
                for exc in chain:
                    self.assertIsNone(exc.__context__)
                    self.assertIsNone(exc.__cause__)
                    self.assertIsNone(exc.__traceback__)
                    self.assertNotIn(CANARY, repr(exc))
                record = json.loads(list(self.core.files.values())[-1])
                self.assertEqual(record['da_gui'], stage != 'con_sot')
                self.assertEqual(record['ly_do_khong_gui'] if stage == 'con_sot'
                                 else record['loi'], expected)
                self.assertNotIn(CANARY, repr(out) + logs.getvalue() + repr(self.core.payloads))

    def test_cloud_dan_chung_sai_sau_mo_che_bi_loai(self):
        self.local_loi()
        self.cloud.tra_loi.side_effect = None
        self.cloud.tra_loi.return_value = ca.PhanHoiCloud(
            tra_loi(masked=True, quote='Dẫn chứng ngoài nguồn DEMO'), 'demo', 1, 1)
        out = self.goi()
        self.assertEqual(out.duong, 'KHONG')
        self.assertEqual(set(out.truong_bi_loai), {'so_tien', 'ngay'})
        self.assertIn('TRICH_DAN_SAI', out.ly_do)

    def test_chi_cuc_bo_zero_cloud_khi_local_loi_khong_chac_va_lay_mau(self):
        self.cong = self.tao_cong(cfg=settings(1.0))
        chon = Mock(return_value=True)
        self.cong._kiem_xac_suat = chon
        adapter = AdapterHoiAI(self.cong, kiem_schema=self.kiem_schema,
                               tham_chieu_luot_che=lambda *a, **k: LUOT)
        dau_vao = dict(loai_viec=LOAI, van_ban=VAN_BAN, chi_dan=CHI_DAN,
            truong=list(YEU_CAU.truong), dinh_danh_da_biet=[[TEN, 'CONG_TY']])
        # CD-098 / QD-20261106-01: bản 1 chỉ Local, 0 lượt Cloud/Mask,
        # kể cả cờ false/thiếu và cấu hình Cloud bật trên cùng instance.
        for co in ({'chi_cuc_bo': True}, {'chi_cuc_bo': False}, {}):
            for answer in (tra_loi(), tra_loi(confidence=0.1), None):
                with self.subTest(co=co, answer=answer):
                    if answer is None:
                        self.local_loi()
                    else:
                        self.local.side_effect = None
                        self.local.return_value = answer
                    out = adapter.goi({**dau_vao, **co}, revision=1,
                        nguon_tep_ids=[TEP], vi_tri={'tep_id': TEP, 'dinh_vi': 'doan:1'})
                    self.assertNotIn(out['duong'], ('CLOUD', 'LOCAL+CLOUD'))
                    self.assertEqual(out['duong'], 'KHONG' if answer is None else 'LOCAL')
                    self.assertTrue(self.cong.cai_dat['cloud_bat'])
        self.assertEqual(self.local.call_count, 9)
        chon.assert_not_called()
        self.cloud.tra_loi.assert_not_called()
        self.mask.co_khoa.assert_not_called()
        self.mask._goi.assert_not_called()

    def test_xac_suat_dung_ty_le_cau_hinh_va_bien_nho_hon(self):
        # Vô hiệu bậc giảm trong ca này để đo đúng ranh giới cấu hình.
        cfg = settings(0.37)
        cfg['cong_ai']['kiem_xac_suat']['bac_thang'] = []
        self.cong = self.tao_cong(cfg=cfg)
        for draw, duong in ((0.369999, 'CLOUD'), (0.37, 'LOCAL'), (0.99, 'LOCAL')):
            with self.subTest(draw=draw), patch.object(ca.random, 'random', return_value=draw) as rng:
                out = self.goi()
                self.assertEqual(out.duong, duong)
                rng.assert_called_once_with()
        self.cloud.tra_loi.assert_called_once()
        self.assertEqual(self.thong_ke()['so_kiem'], 1)
        self.assertEqual(self.thong_ke()['phan_tram_chinh_xac'], 100)

    def test_ty_le_theo_loai_ghi_de_ty_le_chung(self):
        cfg = settings(1.0)
        cfg['cong_ai']['kiem_xac_suat']['ty_le_theo_loai'] = {LOAI: 0.23}
        cfg['cong_ai']['kiem_xac_suat']['bac_thang'] = []
        self.cong = self.tao_cong(cfg=cfg)
        with patch.object(ca.random, 'random', return_value=0.23):
            self.assertEqual(self.goi().duong, 'LOCAL')
        with patch.object(ca.random, 'random', return_value=0.229999):
            self.assertEqual(self.goi().duong, 'CLOUD')

    def test_restart_bo_ghi_giu_so_do_va_giam_kiem_tu_core(self):
        cfg = settings(0.4)
        self.cong = self.tao_cong(cfg=cfg)
        with patch.object(ca.random, 'random', return_value=0.0):
            self.goi()
            self.goi()
        before = self.thong_ke()
        self.assertEqual((before['so_kiem'], before['phan_tram_chinh_xac'],
                          before['ty_le_kiem_hien_hanh']), (2, 100, 0.1))
        moi = self.tao_cong(cfg=cfg, bo=bo_ghi(self.core))
        self.assertEqual(self.thong_ke(moi), before)
        with patch.object(ca.random, 'random', return_value=0.1):
            self.assertEqual(moi.goi(YEU_CAU).duong, 'LOCAL')
        self.assertEqual(self.cloud.tra_loi.call_count, 2)

    def test_cloud_khac_local_giu_gia_tri_cu_va_cham_sai(self):
        self.cong = self.tao_cong(cfg=settings(1.0))
        self.local.side_effect = None
        self.local.return_value = tra_loi(tien='234.567 đồng')
        with patch.object(ca.random, 'random', return_value=0.0):
            out = self.goi()
        self.assertEqual(out.truong['so_tien'].gia_tri, TIEN)
        self.assertEqual(out.truong['so_tien'].gia_tri_local, '234.567 đồng')
        tk = self.thong_ke()
        self.assertEqual((tk['so_kiem'], tk['phan_tram_chinh_xac']), (1, 0))
        self.assertEqual(tk['canh_bao'], 'LOCAL_DUOI_NGUONG_CHINH_XAC')

    def test_mat_ack_giu_metadata_thu_lai_khong_goi_lai_ai(self):
        self.local_loi()
        self.core.ack = False
        with self.assertLogs(ca._LOG, level='ERROR'):
            self.assertEqual(self.goi().duong, 'CLOUD')
        self.assertFalse(self.bo.da_ban_giao())
        self.core.ack = True
        self.bo.thu_lai()
        self.assertTrue(self.bo.da_ban_giao())
        self.assertEqual(len(self.core.files), 2)
        self.local.assert_called_once()
        self.cloud.tra_loi.assert_called_once()

    def test_bi_mat_dung_kenh_bootstrap_va_cung_settings_tuy_chinh(self):
        self.assertIs(self.cong._moi_truong, self.ram)
        self.assertEqual(self.bootstrap.tham_so, {'cong_khai': 'DEMO'})
        with self.assertRaisesRegex(bs.LoiBootstrap, 'BM_DA_LAY'):
            self.bootstrap.bi_mat.lay_mot_lan()
        self.local_loi()
        self.assertEqual(self.goi().duong, 'CLOUD')
        self.assertEqual(self.cloud.tra_loi.call_args.kwargs['khoa'], CANARY)
        # Thiếu cùng settings sẽ từ chối khóa tùy chỉnh, không fallback.
        with self.assertRaises(bm.LoiBiMat):
            self.tao_cong(cfg={})
        other = nhan_bootstrap({KEY_NAME: CANARY})
        with self.assertRaises(bm.LoiBiMat):
            bm.BiMatRAM.tu_bootstrap(other, {})

    def test_bi_mat_trong_tham_so_bi_bootstrap_bac(self):
        with self.assertRaisesRegex(bs.LoiBootstrap, 'BM_TRONG_THAM_SO') as caught:
            nhan_bootstrap({}, tham_so={'bi_mat': {KEY_NAME: CANARY}})
        self.assertNotIn(CANARY, ''.join(traceback.format_exception(caught.exception)))

    def test_tu_bootstrap_thu_hoi_ram_neu_kenh_bi_mat_nem_loi(self):
        original_revoke = bm.BiMatRAM.thu_hoi
        for ma in ('BM_DA_LAY', 'BM_KHONG_HOP_LE', 'BM_SAI_THU_TU'):
            with self.subTest(ma=ma):
                b = nhan_bootstrap({KEY_NAME: CANARY})
                with patch.object(bs.BiMatBootstrap, 'lay_mot_lan',
                                  side_effect=bs.LoiBootstrap(ma)), \
                        patch.object(bm.BiMatRAM, 'thu_hoi', autospec=True,
                                     side_effect=original_revoke) as revoke:
                    with self.assertRaises(bm.LoiBiMat) as caught:
                        bm.BiMatRAM.tu_bootstrap(b, self.cfg)
                    revoke.assert_called_once()
                    self.assertEqual(len(revoke.call_args.args[0]), 0)
                    self.assertIsNone(caught.exception.__context__)
                    self.assertNotIn(CANARY, ''.join(
                        traceback.format_exception(caught.exception)))
                b.bi_mat.thu_hoi()

    def test_thu_hoi_ram_khong_fallback_env_local_van_chay(self):
        self.ram.thu_hoi()
        self.ram.thu_hoi()
        self.assertEqual(len(self.ram), 0)
        self.assertEqual(self.goi().duong, 'LOCAL')
        self.local_loi()
        out = self.goi()
        self.assertIn('CHUA_CO_KHOA_API', out.ly_do)
        self.cloud.tra_loi.assert_not_called()
        self.mask._goi.assert_not_called()

    def test_canary_khong_lo_log_loi_ket_qua_va_metadata_core(self):
        out, err, logs = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(logs)
        ca._LOG.addHandler(handler)
        self.addCleanup(ca._LOG.removeHandler, handler)
        results = []
        with redirect_stdout(out), redirect_stderr(err):
            self.local_loi()
            results.append(self.goi())
            self.cloud.tra_loi.side_effect = RuntimeError(CANARY)
            results.append(self.goi())
            self.mask._goi.side_effect = RuntimeError(CANARY)
            results.append(self.goi())
            with self.assertRaises(bm.LoiBiMat) as caught:
                self.tao_cong(cfg={})
            traces = ''.join(traceback.format_exception(caught.exception))
            with self.assertRaises(KeyError) as caught:
                self.ram[CANARY]
            traces += ''.join(traceback.format_exception(caught.exception))
            self.core.loi_doc = True
            results.append(self.cong.thong_ke())
            print(self.ram, self.bootstrap, self.bo, results)
        visible = (out.getvalue() + err.getvalue() + logs.getvalue() + traces
                   + repr(results) + repr(self.core.payloads))
        self.assertNotIn(CANARY, visible)
        for raw in self.core.files.values():
            for forbidden in (CANARY, VAN_BAN, CHI_DAN, TIEN, NGAY):
                self.assertNotIn(forbidden, raw.decode('utf-8'))


class VanHanhTest(_FixtureAI5b):
    model_demo = True

    def setUp(self):
        super().setUp()
        goi = ca.CongAI.goi

        def goi_core_demo(provider, yeu_cau, **kwargs):
            # Các ca lifecycle gọi cổng trực tiếp; Core fixture cấp ngữ cảnh DEMO.
            return goi(provider, yeu_cau, ma_module='demo',
                       ma_function='hoi_demo', **kwargs)

        self.enterContext(patch.object(ca.CongAI, 'goi', goi_core_demo))

    def kiem_drain_nhat_ky(self, *, ack_sau=None, dung_cung=None):
        b = nhan_bootstrap({KEY_NAME: CANARY})
        vong = Mock()
        vong.drain.return_value = True
        received, retries, delays = [], [], []
        clock = [0.0]
        self.core.ack = False
        self.local_loi()
        original_retry = BoGhiQuaCore.thu_lai

        def tao_vong(bootstrap, nhan_viec, provider):
            received.append(provider)
            # QD-20261106-01: thay cặp Local/Cloud bằng hai lượt Local lỗi,
            # giữ nguyên kiểm drain/ACK khi có nhiều bản ghi đang chờ.
            for _ in range(2):
                self.assertEqual(provider.goi(YEU_CAU).duong, 'KHONG')
            self.assertFalse(self.bo.da_ban_giao())
            return vong

        def retry(bo):
            self.assertNotIn(b'da_thu_hoi', b._ra.getvalue())
            b.socket.close.assert_not_called()
            if vong.ngung_accept.called:
                # Worker đã xong: bàn giao nhật ký không còn giữ khóa AI.
                self.assertEqual(len(received[0]._moi_truong), 0)
                retries.append(clock[0])
                if clock[0] >= runtime.HAN_DRAIN_GIAY:
                    self.assertIn(b'drain_chua_xong', b._ra.getvalue())
                if ack_sau is not None and len(retries) >= ack_sau:
                    self.core.ack = True
            else:
                self.assertEqual(received[0]._moi_truong[KEY_NAME], CANARY)
            return original_retry(bo)

        def sleep(seconds):
            self.assertLessEqual(len(retries), 12, 'Runtime không dừng theo fixture')
            self.assertGreater(seconds, 0)
            self.assertEqual(len(received[0]._moi_truong), 0)
            b.socket.close.assert_not_called()
            self.assertFalse(self.bo.da_ban_giao())
            self.assertNotIn(b'da_thu_hoi', b._ra.getvalue())
            delays.append(seconds)
            clock[0] += seconds
            if dung_cung is not None and len(retries) >= 8:
                raise dung_cung

        original_gui = bs.gui_thong_diep

        def gui(kenh, data):
            if data['kieu'] == 'drain_chua_xong':
                self.assertGreaterEqual(clock[0], runtime.HAN_DRAIN_GIAY)
                b.socket.close.assert_not_called()
            if data['kieu'] == 'da_thu_hoi':
                self.assertTrue(self.bo.da_ban_giao())
                self.assertEqual(len(received[0]._moi_truong), 0)
            original_gui(kenh, data)

        with patch.object(runtime.Bootstrap, 'nhan', return_value=b), \
                patch.object(runtime, '_VongNhan', side_effect=tao_vong), \
                patch.object(runtime, 'HAN_DRAIN_GIAY', 0.25), \
                patch.object(runtime, 'time') as timer, \
                patch.object(BoGhiQuaCore, 'thu_lai', autospec=True, side_effect=retry), \
                patch.object(runtime, 'gui_thong_diep', side_effect=gui), \
                patch.object(bs, 'gui_thong_diep', side_effect=gui), \
                self.assertLogs(ca._LOG, level='ERROR'):
            timer.monotonic.side_effect = lambda: clock[0]
            timer.sleep.side_effect = sleep
            error = None
            try:
                runtime.chay(kiem_schema=self.kiem_schema,
                             kiem_chu_ky=lambda *a: None, nhan_viec=lambda *a: None,
                             settings=self.cfg, mask=self.mask, bo_ghi=self.bo,
                             nha_cung_cap=self.cloud, local_transport=self.local)
            except (KeyboardInterrupt, SystemExit) as exc:
                error = exc
        self.assertTrue(retries)
        self.assertEqual(len(received[0]._moi_truong), 0)
        self.assertEqual(self.local.call_count, 2)
        self.cloud.tra_loi.assert_not_called()
        self.mask.co_khoa.assert_not_called()
        self.mask._goi.assert_not_called()
        messages = [json.loads(line)['kieu'] for line in b._ra.getvalue().splitlines()]
        qua_han = retries[-1] >= 0.25
        self.assertEqual(messages.count('drain_chua_xong'), int(qua_han))
        self.assertEqual(delays, sorted(delays))
        b.socket.close.assert_called()
        b.socket.shutdown.assert_not_called()
        if dung_cung is not None:
            self.assertIs(error, dung_cung)
            self.assertEqual(vong.drain.call_count, 1)  # Không chờ drain lại khi buộc dừng.
            self.assertGreaterEqual(sum(t >= 0.25 for t in retries), 3)
            self.assertNotIn('da_thu_hoi', messages)
            self.assertFalse(self.bo.da_ban_giao())
        else:
            self.assertIsNone(error)
            self.assertEqual(len(retries), ack_sau)
            self.assertTrue(self.bo.da_ban_giao())
            self.assertEqual(messages[-1], 'da_thu_hoi')
        self.assertEqual(len(self.core.files), 1 if dung_cung is not None else 2)
        self.assertNotIn(CANARY, repr(self.core.payloads))

    def test_runtime_mat_ack_qua_han_giu_socket_retry_va_thu_khoa_den_dung_cung(self):
        self.kiem_drain_nhat_ky(dung_cung=SystemExit('CORE_DUNG_CUNG'))

    def test_runtime_ack_muon_qua_han_dong_sach_va_xac_nhan_thu_hoi(self):
        self.kiem_drain_nhat_ky(ack_sau=9)

    def test_runtime_tin_hieu_ket_thuc_dong_socket_khi_nhat_ky_con_cho(self):
        self.kiem_drain_nhat_ky(dung_cung=KeyboardInterrupt())

    def test_runtime_ack_truoc_han_thu_khoa_som_va_xac_nhan(self):
        self.kiem_drain_nhat_ky(ack_sau=2)

    def chay_runtime(self, *, commands=None, ready=True, drain_error=False):
        b = nhan_bootstrap({KEY_NAME: CANARY}, commands=commands)
        vong = Mock()
        vong.drain.return_value = True
        if drain_error:
            vong.drain.side_effect = [bs.LoiBootstrap('DRAIN_DEMO'), True]
        # Không khởi thread/worker thật; mọi lời gọi lifecycle vẫn là mã chay.py.
        with patch.object(runtime.Bootstrap, 'nhan', return_value=b), \
                patch.object(runtime, '_kiem_local', return_value=ready), \
                patch.object(runtime, '_VongNhan', return_value=vong), \
                patch.object(bm.BiMatRAM, 'tu_bootstrap',
                             wraps=bm.BiMatRAM.tu_bootstrap) as acquire, \
                patch.object(bm, 'tao_cong_ai', wraps=bm.tao_cong_ai) as factory, \
                patch.object(bm.BiMatRAM, 'thu_hoi', autospec=True) as revoke:
            error = None
            try:
                runtime.chay(kiem_schema=self.kiem_schema, kiem_chu_ky=lambda *a: None,
                             nhan_viec=lambda *a: None,
                             settings=self.cfg, mask=self.mask, bo_ghi=self.bo,
                             nha_cung_cap=self.cloud, local_transport=self.local)
            except bs.LoiBootstrap as exc:
                error = exc
            return b, vong, acquire, factory, revoke, error

    def test_runtime_nhan_ram_truoc_readiness(self):
        """Runtime tiêu thụ kênh bootstrap và dùng cùng settings cho cổng."""
        b, vong, acquire, factory, revoke, error = self.chay_runtime()
        self.assertIsNone(error)
        acquire.assert_called_once()
        self.assertIs(acquire.call_args.args[0], b)
        factory.assert_called_once()
        acquire_settings = (acquire.call_args.args[1] if len(acquire.call_args.args) > 1
                            else acquire.call_args.kwargs['settings'])
        factory_settings = (factory.call_args.args[0] if factory.call_args.args
                            else factory.call_args.kwargs['settings'])
        self.assertIs(acquire_settings, factory_settings)

    def test_runtime_drain_phai_goi_thu_hoi_bi_mat_ram(self):
        """Drain xong thu RAM đúng một lần."""
        b, vong, acquire, factory, revoke, error = self.chay_runtime()
        self.assertIsNone(error)
        vong.drain.assert_called()
        revoke.assert_called_once()

    def kiem_loi_thu_hoi(self, **kwargs):
        b, vong, acquire, factory, revoke, error = self.chay_runtime(**kwargs)
        self.assertIsInstance(error, bs.LoiBootstrap)
        self.assertNotIn(CANARY, ''.join(traceback.format_exception(error)))
        revoke.assert_called_once()

    def test_loi_bootstrap_preflight_phai_thu_hoi_ram(self):
        self.kiem_loi_thu_hoi(ready=False)

    def test_loi_bootstrap_nhan_accept_phai_thu_hoi_ram(self):
        self.kiem_loi_thu_hoi(commands=[lenh('bi_mat')])

    def test_loi_bootstrap_thu_hoi_phai_thu_hoi_ram(self):
        self.kiem_loi_thu_hoi(commands=[lenh('nhan_accept'), lenh('sai_demo')])

    def test_loi_bootstrap_trong_drain_phai_thu_hoi_ram(self):
        self.kiem_loi_thu_hoi(drain_error=True)

    def test_runtime_giu_khoa_den_drain_xong_va_thu_truoc_ack(self):
        b = nhan_bootstrap({KEY_NAME: CANARY})
        vong = Mock()
        received = []

        def tao_vong(bootstrap, nhan_viec, provider):
            self.assertIs(bootstrap, b)
            self.assertEqual(b._ra.getvalue(), b'')  # Chưa readiness.
            self.assertIsInstance(provider, ca.CongAI)
            self.assertIsInstance(provider._moi_truong, bm.BiMatRAM)
            self.assertEqual(provider._moi_truong[KEY_NAME], CANARY)
            with self.assertRaisesRegex(bs.LoiBootstrap, 'BM_DA_LAY'):
                b.bi_mat.lay_mot_lan()
            received.append(provider)
            return vong

        def drain():
            ram = received[0]._moi_truong
            if vong.drain.call_count <= 2:
                self.assertEqual(ram[KEY_NAME], CANARY)
                return vong.drain.call_count == 2
            self.assertEqual(len(ram), 0)
            return True

        vong.drain.side_effect = drain
        original_gui = runtime.gui_thong_diep

        def gui(kenh, data):
            if data['kieu'] == 'da_thu_hoi':
                self.assertEqual(len(received[0]._moi_truong), 0)
            original_gui(kenh, data)

        with patch.object(runtime.Bootstrap, 'nhan', return_value=b), \
                patch.object(runtime, '_VongNhan', side_effect=tao_vong), \
                patch.object(bs, 'gui_thong_diep', side_effect=gui):
            runtime.chay(kiem_schema=self.kiem_schema,
                         kiem_chu_ky=lambda *a: None, nhan_viec=lambda *a: None,
                         settings=self.cfg, mask=self.mask, bo_ghi=self.bo,
                         nha_cung_cap=self.cloud, local_transport=self.local)
        self.assertEqual(len(received[0]._moi_truong), 0)
        self.assertIn(b'da_thu_hoi', b._ra.getvalue())
        # Cổng còn giữ cùng mapping rỗng; QD-20261106-01 vẫn khóa Cloud.
        self.assertEqual(received[0].goi(YEU_CAU).duong, 'LOCAL')
        self.local_loi()
        self.assertIn('CLOUD_TAT', received[0].goi(YEU_CAU).ly_do)
        self.cloud.tra_loi.assert_not_called()
        self.mask._goi.assert_not_called()

    def test_runtime_thoat_loi_o_factory_worker_va_cleanup_deu_thu_ram(self):
        for stage in ('factory', 'worker', 'start', 'stop', 'drain', 'close'):
            with self.subTest(stage=stage):
                b = nhan_bootstrap({KEY_NAME: CANARY})
                vong = Mock()
                vong.drain.return_value = True
                if stage == 'start':
                    vong.bat_dau.side_effect = RuntimeError('DEMO')
                elif stage == 'stop':
                    vong.ngung_accept.side_effect = RuntimeError('DEMO')
                elif stage == 'drain':
                    vong.drain.side_effect = RuntimeError('DEMO')
                elif stage == 'close':
                    b.socket.close.side_effect = RuntimeError('DEMO')
                original_revoke = bm.BiMatRAM.thu_hoi
                with patch.object(runtime.Bootstrap, 'nhan', return_value=b), \
                        patch.object(runtime, '_VongNhan', return_value=vong,
                            side_effect=RuntimeError('DEMO') if stage == 'worker' else None), \
                        patch.object(bm, 'tao_cong_ai', wraps=bm.tao_cong_ai,
                            side_effect=RuntimeError('DEMO') if stage == 'factory' else None), \
                        patch.object(bm.BiMatRAM, 'thu_hoi', autospec=True,
                                     side_effect=original_revoke) as revoke:
                    with self.assertRaises(RuntimeError):
                        runtime.chay(kiem_schema=self.kiem_schema, kiem_chu_ky=lambda *a: None,
                            nhan_viec=lambda *a: None, settings=self.cfg,
                            mask=self.mask, bo_ghi=self.bo,
                            nha_cung_cap=self.cloud, local_transport=self.local)
                    revoke.assert_called_once()
                    self.assertEqual(len(revoke.call_args.args[0]), 0)

    def test_runtime_cloud_bat_local_loi_khong_goi_mask_cloud_va_thu_lai(self):
        """QD-20261106-01: lỗi Local ở runtime bản 1 không mở Mask/Cloud."""
        self.enterContext(patch.dict(ca.ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        original = deepcopy(self.cfg)
        self.assertIs(self.cfg['cong_ai']['cloud_bat'], True)
        for error, code in ((ca.ai_cuc_bo.LocalAIUnavailable('Lỗi kết nối DEMO'),
                             'LOCAL_KHONG_CHAY'),
                            (ValueError('Model DEMO chưa sẵn sàng'), 'LOCAL_LOI')):
            with self.subTest(code=code):
                b = nhan_bootstrap({KEY_NAME: CANARY})
                vong = Mock()
                vong.drain.return_value = True

                def tao_vong(bootstrap, nhan_viec, provider):
                    self.local.side_effect = error
                    out = provider.goi(YEU_CAU)
                    self.assertEqual((out.duong, out.muc), ('KHONG', 'DO'))
                    self.assertIn(code, out.ly_do)
                    self.assertIn('CLOUD_TAT', out.ly_do)
                    self.assertIn('chưa sẵn sàng', out.thong_bao)
                    self.assertIn('thử lại', out.thong_bao)
                    self.assertNotIn('KHONG_THAY_CAN_CU', out.ly_do)
                    self.assertNotIn(CANARY, out.thong_bao)
                    # Mô phỏng lần thử lại sau khoảng nghỉ kết nối.
                    ca.ai_cuc_bo._CONNECTION_FAILURES.clear()
                    self.local.side_effect = self._local
                    self.assertEqual(provider.goi(YEU_CAU).duong, 'LOCAL')
                    return vong

                with patch.object(runtime.Bootstrap, 'nhan', return_value=b), \
                        patch.object(runtime, '_VongNhan', side_effect=tao_vong), \
                        patch.object(ca.CongAI, '_cloud', side_effect=AssertionError(
                            'Runtime bản 1 không chạy Cloud')) as cloud_route:
                    runtime.chay(kiem_schema=self.kiem_schema, kiem_chu_ky=lambda *a: None,
                        nhan_viec=lambda *a: None, settings=self.cfg,
                        mask=self.mask, bo_ghi=self.bo, nha_cung_cap=self.cloud,
                        local_transport=self.local)
                cloud_route.assert_not_called()
        self.assertEqual(self.local.call_count, 4)
        self.cloud.tra_loi.assert_not_called()
        self.mask.co_khoa.assert_not_called()
        self.mask._goi.assert_not_called()
        self.assertEqual(self.cfg, original)
        records = [json.loads(raw) for raw in self.core.files.values()]
        self.assertEqual([r['duong'] for r in records], ['LOCAL'] * 4)

    def test_runtime_worker_chi_local_ke_ca_lay_mau_va_kem_tin_cay(self):
        """Thay kỳ vọng Local → Cloud cũ theo QD-20261106-01, bản 1 chỉ Local."""
        b = nhan_bootstrap({KEY_NAME: CANARY})
        vong = Mock()
        vong.drain.return_value = True
        self.cfg = settings(rate=1.0, model_demo=True)
        original = deepcopy(self.cfg)
        chon_kiem = Mock(return_value=True)

        def tao_vong(bootstrap, nhan_viec, provider):
            self.assertFalse(provider.trang_thai(kiem_mask=True)['cloud']['dung_duoc'])
            self.assertEqual(provider.goi(YEU_CAU).duong, 'LOCAL')
            self.assertEqual(self.events, ['LOCAL'])
            self.local.side_effect = None
            for answer, code in ((tra_loi(confidence=0.1), 'DUOI_NGUONG'),
                                 ('JSON hỏng', 'PHAN_HOI_KHONG_HOP_LE')):
                self.local.return_value = answer
                out = provider.goi(YEU_CAU)
                self.assertIn(code, out.ly_do)
                self.assertIn('CLOUD_TAT', out.ly_do)
                self.assertNotIn(out.duong, ('CLOUD', 'LOCAL+CLOUD'))
            return vong

        with patch.object(runtime.Bootstrap, 'nhan', return_value=b), \
                patch.object(runtime, '_VongNhan', side_effect=tao_vong), \
                patch.object(ca.CongAI, '_cloud', side_effect=AssertionError(
                    'Runtime bản 1 không chạy Cloud')) as cloud_route:
            runtime.chay(kiem_schema=self.kiem_schema,
                         kiem_chu_ky=lambda *a: None, nhan_viec=lambda *a: None,
                         settings=self.cfg, mask=self.mask, bo_ghi=self.bo,
                         nha_cung_cap=self.cloud, local_transport=self.local,
                         kiem_xac_suat=chon_kiem)
        self.assertEqual(self.local.call_count, 3)
        chon_kiem.assert_not_called()
        cloud_route.assert_not_called()
        self.cloud.tra_loi.assert_not_called()
        self.mask.co_khoa.assert_not_called()
        self.mask._goi.assert_not_called()
        self.assertEqual(self.cfg, original)
        records = [json.loads(raw) for raw in self.core.files.values()]
        self.assertEqual([r['duong'] for r in records], ['LOCAL'] * 3)


if __name__ == '__main__':
    unittest.main()
