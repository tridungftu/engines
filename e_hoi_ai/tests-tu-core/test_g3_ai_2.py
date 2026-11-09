"""AI-1b-03: adapter bản 1 chỉ Local giả, khóa Cloud kể cả cờ false.

Ca M9 chỉ là mẫu module giả; lead grep mọi lời gọi M9 thật ở cổng kiểm.
Thiếu jsonschema thì dùng seam kiểm tối thiểu của bộ test G2-17;
meta-schema đầy đủ được ghi CHUA_KIEM, không coi fallback là chứng nhận.
"""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_g2_17 as bundle

from kho_tri_thuc.engines.e_hoi_ai.hoi import (
    AdapterHoiAI, HOI, TRA_LOI, HOI_V2, TRA_LOI_V2)
from kho_tri_thuc.tri_thuc import cong_ai as ca


TEP = '00000000-0000-4000-8000-000000000001'
PHAP_NHAN = '00000000-0000-4000-8000-000000000002'
VIEC = '00000000-0000-4000-8000-000000000003'
LUOT = '00000000-0000-4000-8000-000000000004'
VAN_BAN = 'Lãi suất DEMO 8%/năm, điều chỉnh 9%/năm.'
NGUON = dict(revision=1, nguon_tep_ids=[TEP],
             vi_tri={'tep_id': TEP, 'dinh_vi': 'doan:1'},
             phap_nhan_id=PHAP_NHAN, viec_id=VIEC)


def dau_vao(**changes):
    return dict(loai_viec='BOC_TACH_HOP_DONG', van_ban=VAN_BAN,
                chi_dan='Trích lãi suất DEMO.', truong=['lai_suat'], **changes)


def tra_loi(value='8%/năm', do_tin_cay=0.95, trich_dan=VAN_BAN):
    return json.dumps({'truong': [{'ten': 'lai_suat', 'gia_tri': value,
                                  'trich_dan': trich_dan}],
                       'do_tin_cay': do_tin_cay}, ensure_ascii=False)


def m9_gia_hoi(sdk_core):
    """Ca mẫu: module M9 giả, không thay cổng grep M9 thật của lead."""
    return sdk_core.goi('ai.hoi@1', {
        **dau_vao(chi_cuc_bo=True), 'loai_viec': 'HOI_DAP_VAY'})


class MaskGia:
    """Chỉ dữ liệu DEMO không có định danh; không chứng nhận bộ che thật."""

    def __init__(self):
        self.che = Mock(side_effect=lambda text, ids: ca.LuotChe('mask-DEMO', text))
        self.mo_che = Mock(side_effect=lambda ma, text, **kw: text)
        self.ket_thuc = Mock()
        self.co_khoa = Mock(return_value=True)


class AdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {}
        for name in ('ky_thuat.json', 'manifest.json'):
            cls.schemas.update(json.loads(
                (bundle.CONTRACT_DIR / name).read_text(encoding='utf-8')))
        if bundle.Draft202012Validator:
            def offline(uri):
                raise bundle.NoSuchResource(ref=uri)
            cls.registry = bundle.Registry(retrieve=offline).with_resources(
                (uri, bundle.Resource.from_contents(schema))
                for uri, schema in cls.schemas.items())

    def kiem(self, schema, value):
        try:
            # Luôn chạy fallback chỉ trong test, đồng thời chạy validator đầy đủ nếu có.
            bundle._minimal(value, schema, schema, self.schemas)
            if bundle.Draft202012Validator:
                bundle.Draft202012Validator(schema, registry=self.registry,
                    format_checker=bundle.FormatChecker()).validate(value)
            return True
        except ValueError:
            return False
        except Exception as exc:
            if bundle.Draft202012Validator:
                from jsonschema.exceptions import ValidationError
                if isinstance(exc, ValidationError):
                    return False
            raise

    def setUp(self):
        self.enterContext(patch('socket.socket', side_effect=AssertionError('Cấm mạng')))
        self.enterContext(patch.dict(ca.ai_cuc_bo._CONNECTION_FAILURES, {}, clear=True))
        self.duong_cloud = self.enterContext(patch.object(
            ca.CongAI, '_cloud', side_effect=AssertionError('Bản 1 không chạy đường Cloud')))
        self.enterContext(patch.object(ca, 'doc_khoa_mask',
                                      side_effect=AssertionError('Cấm đọc tệp khóa')))
        self.local = Mock(return_value=tra_loi())
        self.cloud = Mock()
        self.cloud.tra_loi.return_value = ca.PhanHoiCloud(tra_loi('9%/năm'),
                                                       'cloud-DEMO-thuc', 10, 20)
        self.mask = MaskGia()
        self.ghi = ca.BoGhiBoNho()
        self.chon_kiem = Mock(return_value=True)
        self.cong = ca.CongAI({
            'local_ai': {'enabled': True, 'model': 'local-DEMO',
                         'url': 'http://127.0.0.1:1234/v1/chat/completions'},
            'cong_ai': {'cloud_bat': True}}, bo_ghi=self.ghi,
            nha_cung_cap=self.cloud, mask=self.mask, local_transport=self.local,
            moi_truong={'ANTHROPIC_API_KEY': 'khoa-DEMO'},
            kiem_xac_suat=self.chon_kiem)
        self.luot = Mock(return_value=LUOT)
        self.adapter = AdapterHoiAI(self.cong, kiem_schema=self.kiem,
                                    tham_chieu_luot_che=self.luot)

    def tearDown(self):
        self.duong_cloud.assert_not_called()
        self.cloud.tra_loi.assert_not_called()
        self.chon_kiem.assert_not_called()
        self.mask.co_khoa.assert_not_called()
        self.mask.che.assert_not_called()
        self.mask.mo_che.assert_not_called()
        self.mask.ket_thuc.assert_not_called()
        self.luot.assert_not_called()

    def goi(self, payload=None, **source):
        result = self.adapter.goi(dau_vao() if payload is None else payload,
                                 **{**deepcopy(NGUON), **source})
        self.assertTrue(self.kiem({'$ref': TRA_LOI}, result))
        return result

    def cau_hinh_chon_model(self):
        config = dict(model_phat_hien=[dict(
            loai_phan_mem='lm_studio', id_model=model, trang_thai='san_sang',
            phat_hien_luc='2026-11-07T10:00:00Z', bat=True)
            for model in ('gpt-oss-20b', 'qwen3-8b', 'gemma')],
            quy_tac_model=[dict(module='*', function='*', uu_tien='gpt-oss-20b',
                du_phong=['qwen3-8b', 'gemma'], che_do='tu_chon', bat=True)])
        settings = dict(local_ai=deepcopy(self.cong.local_ai),
                        cong_ai={'cloud_bat': True}, **config)
        self.cong = ca.CongAI(settings, bo_ghi=self.ghi,
            nha_cung_cap=self.cloud, mask=self.mask, local_transport=self.local,
            moi_truong={}, kiem_xac_suat=self.chon_kiem)
        self.adapter = AdapterHoiAI(self.cong, kiem_schema=self.kiem)
        self.assertIsNot(self.cong.cau_hinh_model['model_phat_hien'],
                         settings['model_phat_hien'])
        self.enterContext(patch.object(ca.ai_cuc_bo, 'discover_local_models', return_value=dict(
            ma_loi='', model_phat_hien=deepcopy(config['model_phat_hien']))))
        return self.cong.cau_hinh_model

    def goi_v2(self, function='trich_lai', module='m9', *, payload=None, **source):
        nguon = dict(deepcopy(NGUON), ma_module=module, ma_function=function,
                     ma_prompt='trich_lai_demo', phien_ban_prompt='1.0.0')
        nguon.update(source)
        if payload is None:
            payload = dict(dau_vao(), **{key: nguon[key] for key in
                ('ma_function', 'ma_prompt', 'phien_ban_prompt')})
        original = deepcopy((payload, nguon))
        result = self.adapter.goi(payload, nguon_core=nguon)
        self.assertTrue(self.kiem({'$ref': TRA_LOI_V2}, result))
        self.assertEqual((payload, nguon), original)
        return result

    def kiem_model_da_gui(self, out, model, reason):
        self.assertEqual((out['duong'], out['muc']), ('LOCAL', 'VANG'))
        self.assertEqual(json.loads(self.local.call_args.args[1])['model'], model)
        self.assertEqual(out['mo_hinh'][0]['ten'], model)
        record = self.ghi.ban_ghi[-1]
        self.assertEqual((record.duong, record.model, record.da_gui), ('LOCAL', model, True))
        self.assertIn(reason, record.ly_do)

    def test_model_uu_tien_san_sang_va_snapshot_khong_doi(self):
        config = self.cau_hinh_chon_model()
        original = deepcopy((config, self.cong.local_ai, self.cong.cai_dat))
        self.kiem_model_da_gui(self.goi_v2(), 'gpt-oss-20b', 'uu_tien')
        self.assertEqual((config, self.cong.local_ai, self.cong.cai_dat), original)

    def test_model_uu_tien_mat_hoac_chua_san_sang_dung_du_phong_1(self):
        for state in (None, 'khong_con', 'da_tai', 'chua_ro'):
            with self.subTest(state=state):
                config = self.cau_hinh_chon_model()
                if state is None:
                    config['model_phat_hien'] = config['model_phat_hien'][1:]
                else:
                    config['model_phat_hien'][0]['trang_thai'] = state
                self.kiem_model_da_gui(self.goi_v2(), 'qwen3-8b', 'du_phong:1')

    def test_model_tat_bi_bo_qua_giu_dung_thu_tu_du_phong(self):
        config = self.cau_hinh_chon_model()
        config['model_phat_hien'][0]['bat'] = False
        config['model_phat_hien'][1]['bat'] = False
        self.kiem_model_da_gui(self.goi_v2(), 'gemma', 'du_phong:2')

    def test_model_co_dinh_chi_dung_uu_tien(self):
        config = self.cau_hinh_chon_model()
        config['quy_tac_model'][0]['che_do'] = 'co_dinh'
        self.kiem_model_da_gui(self.goi_v2(), 'gpt-oss-20b', 'co_dinh')

    def test_model_co_dinh_mat_hoac_tat_loi_local_khong_tu_chuyen(self):
        for changes in (None, {'trang_thai': 'chua_ro'}, {'bat': False}):
            with self.subTest(changes=changes):
                config = self.cau_hinh_chon_model()
                config['quy_tac_model'][0]['che_do'] = 'co_dinh'
                if changes is None:
                    config['model_phat_hien'] = config['model_phat_hien'][1:]
                else:
                    config['model_phat_hien'][0].update(changes)
                out = self.goi_v2()
                self.assertEqual((out['duong'], out['muc']), ('KHONG', 'DO'))
                self.assertIn('LOCAL_MODEL_CO_DINH_KHONG_SAN_SANG', out['ly_do'])
                self.assertIn('Cố định chưa sẵn sàng', out['thong_bao'])
                self.assertEqual(out['mo_hinh'], [])
                self.assertFalse(self.ghi.ban_ghi[-1].da_gui)
        self.local.assert_not_called()

    def test_model_quy_tac_rieng_thang_wildcard_ca_khi_tat(self):
        config = self.cau_hinh_chon_model()
        rule = dict(module='m9', function='trich_lai', uu_tien='gemma',
                    du_phong=[], che_do='tu_chon', bat=True)
        config['quy_tac_model'].append(rule)
        self.kiem_model_da_gui(self.goi_v2(), 'gemma', 'uu_tien')
        self.kiem_model_da_gui(self.goi_v2('doi_chieu'), 'gpt-oss-20b', 'uu_tien')
        self.kiem_model_da_gui(self.goi_v2(module='m4'), 'gpt-oss-20b', 'uu_tien')
        rule['bat'] = False
        self.local.reset_mock()
        out = self.goi_v2()
        self.assertIn('LOCAL_KHONG_CO_MODEL', out['ly_do'])
        self.local.assert_not_called()

    def test_model_wildcard_tung_chieu(self):
        config = self.cau_hinh_chon_model()
        config['quy_tac_model'].extend([
            dict(module='*', function='trich_lai', uu_tien='qwen3-8b',
                 du_phong=[], che_do='tu_chon', bat=True),
            dict(module='m9', function='*', uu_tien='gemma',
                 du_phong=[], che_do='tu_chon', bat=True)])
        self.kiem_model_da_gui(self.goi_v2(), 'gemma', 'uu_tien')
        self.kiem_model_da_gui(self.goi_v2(module='m4'), 'qwen3-8b', 'uu_tien')

    def test_model_het_model_hoac_quy_tac_khong_dung_model_mac_dinh(self):
        for mode in ('khong_cau_hinh', 'rong', 'tat', 'khong_khop', 'khong_quy_tac'):
            with self.subTest(mode=mode):
                config = self.cau_hinh_chon_model()
                if mode == 'khong_cau_hinh':
                    config.clear()
                elif mode == 'rong':
                    config['model_phat_hien'] = []
                elif mode == 'tat':
                    for model in config['model_phat_hien']:
                        model['bat'] = False
                elif mode == 'khong_quy_tac':
                    config['quy_tac_model'] = []
                else:
                    config['quy_tac_model'][0]['module'] = 'm4'
                out = self.goi_v2()
                self.assertEqual((out['duong'], out['muc']), ('KHONG', 'DO'))
                self.assertIn('LOCAL_KHONG_CO_MODEL', out['ly_do'])
                self.assertEqual(out['mo_hinh'], [])
                self.assertIn('Local AI', out['thong_bao'])
                self.assertNotIn('LOCAL_KHONG_CO_MODEL', out['thong_bao'])
        self.local.assert_not_called()

    def test_model_khong_lay_context_tu_payload_hoac_nguon_khong_khop(self):
        self.cau_hinh_chon_model()
        payload = dict(dau_vao(), ma_function='trich_lai',
                       ma_prompt='trich_lai_demo', phien_ban_prompt='1.0.0')
        for key in ('ma_function', 'ma_prompt', 'phien_ban_prompt'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.goi_v2(payload={**payload, key: 'gia_mao'})
        with self.assertRaises(ValueError):
            self.goi_v2(payload={**payload, 'nguon_core': {'ma_module': 'm9'}})
        with self.assertRaises(ValueError):
            self.adapter.goi(payload, **deepcopy(NGUON))
        with self.assertRaises(ValueError):
            self.goi_v2(vi_tri={'tep_id': LUOT, 'dinh_vi': 'doan:1'})
        self.local.assert_not_called()

    def test_model_hai_function_dong_thoi_khong_lan_cau_hinh_nhat_ky(self):
        config = self.cau_hinh_chon_model()
        config['quy_tac_model'].append(dict(module='m9', function='doi_chieu',
            uu_tien='gemma', du_phong=[], che_do='co_dinh', bat=True))
        original = deepcopy((config, self.cong.local_ai, self.cong.cai_dat))
        entered, release = threading.Event(), threading.Event()

        def transport(url, body):
            if json.loads(body)['model'] == 'gpt-oss-20b':
                entered.set()
                if not release.wait(5):
                    raise AssertionError('Không hoàn tất hai function đồng thời')
            return tra_loi()

        self.local.side_effect = transport
        with ThreadPoolExecutor(1) as pool:
            first = pool.submit(self.goi_v2)
            try:
                self.assertTrue(entered.wait(5))
                second = self.goi_v2('doi_chieu')
                self.assertEqual(second['mo_hinh'][0]['ten'], 'gemma')
                self.assertEqual(self.ghi.ban_ghi[-1].ly_do, ('co_dinh',))
            finally:
                release.set()
            self.assertEqual(first.result(5)['mo_hinh'][0]['ten'], 'gpt-oss-20b')
        self.assertEqual(self.ghi.ban_ghi[-1].ly_do, ('uu_tien',))
        self.assertEqual((config, self.cong.local_ai, self.cong.cai_dat), original)
        self.assertEqual({json.loads(call.args[1])['model'] for call in
                          self.local.call_args_list}, {'gpt-oss-20b', 'gemma'})

    def test_model_chon_khong_lam_doi_ket_qua_khong_thay_can_cu(self):
        self.cau_hinh_chon_model()
        self.local.return_value = json.dumps({'truong': [], 'do_tin_cay': 0.99})
        out = self.goi_v2()
        self.assertEqual(out['ly_do'], ['KHONG_THAY_CAN_CU'])
        self.assertEqual(self.ghi.ban_ghi[-1].ly_do, ('KHONG_THAY_CAN_CU', 'uu_tien'))

    def test_model_cong_chung_khoa_cloud_ca_khi_thieu_context_hoac_local_loi(self):
        self.cau_hinh_chon_model()
        yc = ca.YeuCauAI('BOC_TACH_HOP_DONG', VAN_BAN, 'Trích lãi DEMO.')
        out = self.cong.goi(yc)
        self.assertIn('LOCAL_KHONG_CO_MODEL', out.ly_do)
        self.local.assert_not_called()
        self.local.side_effect = ValueError('Lỗi Local DEMO')
        out = self.cong.goi(yc, ma_module='m9', ma_function='trich_lai')
        self.assertIn('LOCAL_LOI', out.ly_do)
        self.assertEqual(self.ghi.ban_ghi[-1].model, 'gpt-oss-20b')
        self.assertIn('uu_tien', self.ghi.ban_ghi[-1].ly_do)
        self.cong.cau_hinh_model.clear()
        self.local.reset_mock()
        out = self.cong.goi(yc, ma_module='m9', ma_function='trich_lai')
        self.assertIn('LOCAL_KHONG_CO_MODEL', out.ly_do)
        self.local.assert_not_called()

    def test_chi_local_khi_local_loi(self):
        self.local.side_effect = ValueError('Local DEMO lỗi')
        out = self.goi(dau_vao(chi_cuc_bo=True))
        self.assertEqual((out['duong'], out['muc']), ('KHONG', 'DO'))
        self.assertIn('CLOUD_TAT', out['ly_do'])
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()

    def test_dan_chung_chuan_hoa_khoang_trang_qua_adapter(self):
        for van_ban in (VAN_BAN.replace('DEMO ', 'DEMO\n'),
                        VAN_BAN.replace(' ', '   \t ')):
            for chi_cuc_bo in (True, False):
                with self.subTest(van_ban=van_ban, chi_cuc_bo=chi_cuc_bo):
                    out = self.goi({**dau_vao(chi_cuc_bo=chi_cuc_bo),
                                    'van_ban': van_ban})
                    self.assertEqual(out['duong'], 'LOCAL')
                    self.assertEqual(out['truong'][0]['dan_chung'],
                                     [dict(vi_tri=NGUON['vi_tri'], trich_dan=VAN_BAN)])
                    self.assertEqual(out['kiem_tra']['trich_dan'], 'dat')
                    self.assertEqual(out['truong_bi_loai'], [])

    def test_dan_chung_ngoai_van_ban_bi_cong_goc_loai_qua_adapter(self):
        answer = tra_loi(trich_dan='Lãi suất DEMO 10%/năm.')
        self.local.return_value = answer
        self.cloud.tra_loi.return_value = ca.PhanHoiCloud(answer, 'cloud-DEMO-thuc', 10, 20)
        yc = ca.YeuCauAI('BOC_TACH_HOP_DONG', VAN_BAN, 'Trích lãi suất DEMO.',
                         ('lai_suat',))
        for chi_cuc_bo in (True, False):
            with self.subTest(chi_cuc_bo=chi_cuc_bo):
                goc = ca.danh_gia(ca.doc_json_tra_loi(answer), yc,
                                  ca.loai_viec(yc.loai_viec),
                                  'LOCAL')
                self.assertEqual(goc.bi_loai, {'lai_suat': 'TRICH_DAN_SAI'})
                out = self.goi(dau_vao(chi_cuc_bo=chi_cuc_bo))
                self.assertEqual(out['truong'], [])
                self.assertEqual(out['truong_bi_loai'], list(goc.bi_loai))
                self.assertIn('TRICH_DAN_SAI', out['ly_do'])
                self.assertEqual(out['kiem_tra']['trich_dan'], 'chua_kiem')

    def test_chi_local_khi_khong_chac(self):
        self.local.return_value = tra_loi(do_tin_cay=0.4)
        out = self.goi(dau_vao(chi_cuc_bo=True))
        self.assertEqual(out['duong'], 'LOCAL')
        self.assertIn('CLOUD_TAT', out['ly_do'])
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()

    def test_chi_local_chan_chon_kiem_xac_suat(self):
        self.chon_kiem.return_value = True
        self.goi(dau_vao(chi_cuc_bo=True))
        self.chon_kiem.assert_not_called()
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()
        # Cờ false cũng không mở Cloud ở bản 1.
        self.goi(dau_vao(chi_cuc_bo=False))
        self.chon_kiem.assert_not_called()
        self.cloud.tra_loi.assert_not_called()

    def test_hai_request_khac_co_chay_xen_ke(self):
        entered, release = threading.Event(), threading.Event()
        original = deepcopy(self.cong.cai_dat)

        def transport(url, body):
            if threading.current_thread().name.startswith('local-only'):
                entered.set()
                if not release.wait(5):
                    raise AssertionError('Không hoàn tất xen kẽ')
            return tra_loi()

        self.local.side_effect = transport
        with ThreadPoolExecutor(1, thread_name_prefix='local-only') as pool:
            first = pool.submit(self.goi, dau_vao(chi_cuc_bo=True))
            try:
                self.assertTrue(entered.wait(5))
                second = self.goi(dau_vao(chi_cuc_bo=False))
                self.assertEqual(second['duong'], 'LOCAL')
                self.assertEqual(self.cong.cai_dat, original)
            finally:
                release.set()
            self.assertEqual(first.result(5)['duong'], 'LOCAL')
        self.cloud.tra_loi.assert_not_called()
        self.assertEqual(self.cong.cai_dat, original)
        self.assertIs(self.cong.bo_ghi, self.ghi)

    def test_false_khong_tu_bat_cloud_toan_cuc(self):
        self.cong.cai_dat['cloud_bat'] = False
        for answer in (tra_loi(), tra_loi(do_tin_cay=0.4), None):
            with self.subTest(answer=answer):
                self.local.return_value = answer
                self.goi(dau_vao(chi_cuc_bo=False))
        self.cloud.tra_loi.assert_not_called()
        self.mask.che.assert_not_called()
        self.assertIs(self.cong.cai_dat['cloud_bat'], False)

    def test_mac_dinh_va_anh_xa_dto_khong_sua_payload(self):
        payload = dau_vao(dinh_danh_da_biet=[
            'Công ty DEMO', ['Công ty DEMO B', 'CONG_TY'],
            {'gia_tri': 'DEMO-01', 'nhom': ''}])
        original = deepcopy(payload)
        calls = []
        goi_goc = ca.CongAI.goi

        def record(cong, yc, **kw):
            calls.append((cong, yc))
            return goi_goc(cong, yc, **kw)

        with patch.object(ca.CongAI, 'goi', record):
            self.goi(payload)
        cong, yc = calls[0]
        self.assertIsNot(cong, self.cong)
        self.assertIsNot(cong.cai_dat, self.cong.cai_dat)
        self.assertEqual(yc.truong, ('lai_suat',))
        self.assertEqual(yc.dinh_danh_da_biet[1], ('Công ty DEMO B', 'CONG_TY'))
        self.assertEqual((yc.phap_nhan_id, yc.viec_id), (PHAP_NHAN, VIEC))
        self.assertEqual(payload, original)
        self.assertIs(cong.cai_dat['cloud_bat'], False)
        self.assertIs(self.cong.cai_dat['cloud_bat'], True)
        self.cloud.tra_loi.assert_not_called()

    def test_dau_vao_sai_schema_bi_bac_truoc_ai(self):
        invalid = [None, [], {}, {**dau_vao(), 'chi_cuc_bo': 'true'},
                   {**dau_vao(), 'chi_cuc_bo': 1},
                   {**dau_vao(), 'chi_cuc_bo': None},
                   {**dau_vao(), 'van_ban': ' \n\t'},
                   {**dau_vao(), 'truong': ['']},
                   {**dau_vao(), 'dinh_danh_da_biet': None},
                   {**dau_vao(), 'dinh_danh_da_biet': [['DEMO']]},
                   {**dau_vao(), 'dinh_danh_da_biet': [{'gia_tri': 'DEMO'}]},
                   {**dau_vao(), 'phap_nhan_id': PHAP_NHAN},
                   {**dau_vao(), 'loai_viec': 'KHONG_CO'}]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.adapter.goi(payload, **deepcopy(NGUON))
        self.local.assert_not_called()
        self.cloud.tra_loi.assert_not_called()

    def test_tra_loi_giu_gia_tri_local_dan_chung_va_model(self):
        out = self.goi()
        field = out['truong'][0]
        self.assertIsNone(out['cau_tra_loi'])
        self.assertEqual(field['gia_tri'], {'kieu': 'van_ban', 'gia_tri': '8%/năm'})
        self.assertIsNone(field['gia_tri_local'])
        self.assertEqual(field['dan_chung'], [dict(vi_tri=NGUON['vi_tri'], trich_dan=VAN_BAN)])
        self.assertNotIn('luot_che_id', out)
        self.luot.assert_not_called()
        self.assertEqual(out['kiem_tra'], {'trich_dan': 'dat', 'mo_che': 'khong_ap_dung'})
        self.assertEqual([(m['ten'], m['can_cu']) for m in out['mo_hinh']],
                         [('local-DEMO', 'cau_hinh')])
        self.assertTrue(all(r.viec_id == VIEC for r in self.ghi.ban_ghi))
        self.assertEqual([r.duong for r in self.ghi.ban_ghi], ['LOCAL'])

    def test_cloud_loi_khong_bien_ket_qua_local_thanh_cloud(self):
        self.cloud.tra_loi.side_effect = ValueError('Cloud DEMO lỗi')
        out = self.goi()
        self.assertEqual(out['duong'], 'LOCAL')
        self.assertNotIn('luot_che_id', out)
        self.assertEqual([m['duong'] for m in out['mo_hinh']], ['LOCAL'])
        self.assertNotIn('CLOUD_LOI', out['ly_do'])

    def test_local_khong_dung_seam_luot_che(self):
        for seam in (None, Mock(side_effect=AssertionError('Cấm gọi Mask'))):
            with self.subTest(seam=seam):
                self.adapter._tham_chieu_luot_che = seam
                out = self.goi()
                self.assertNotIn('luot_che_id', out)
                self.assertEqual(out['duong'], 'LOCAL')

    def test_nguon_khong_hop_le_bi_bac_truoc_ai(self):
        for changes in ({'revision': 0}, {'nguon_tep_ids': []},
                        {'vi_tri': {'tep_id': LUOT, 'dinh_vi': 'doan:1'}},
                        {'viec_id': 'gia-mao'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.goi(**changes)
        self.local.assert_not_called()

    def test_khong_fallback_env_hoac_tep_khoa(self):
        for name in ('_moi_truong', '_mask'):
            cong = deepcopy(self.cong)
            setattr(cong, name, None)
            with self.subTest(name=name), self.assertRaises(ValueError):
                AdapterHoiAI(cong, kiem_schema=self.kiem)
        self.cong._moi_truong = {}
        with patch.dict(ca.os.environ, {'ANTHROPIC_API_KEY': 'khoa-env-DEMO'}):
            self.local.return_value = tra_loi(do_tin_cay=0.4)
            out = self.goi()
        self.assertNotIn('CHUA_CO_KHOA_API', out['ly_do'])
        self.cloud.tra_loi.assert_not_called()

    def test_dung_nguyen_prompt_function_va_giu_khung_chung(self):
        for prompt in ('  Trích lãi suất theo hợp đồng DEMO.\n\t',
                       'Đối chiếu điều khoản điều chỉnh lãi suất DEMO.'):
            with self.subTest(prompt=prompt):
                payload = {**dau_vao(), 'chi_dan': prompt}
                original = deepcopy(payload)
                self.goi(payload)
                _, body = self.local.call_args.args
                messages = json.loads(body)['messages']
                self.assertEqual(messages[1]['content'], ca.HUONG_DAN_DINH_DANG +
                    '\n\n' + prompt + '\n\nCác trường cần điền: lai_suat\n\nVăn bản:\n' + VAN_BAN)
                self.assertIn('NGUYÊN VĂN', messages[1]['content'])
                self.assertIn('không thấy căn cứ', messages[1]['content'])
                self.assertEqual(payload, original)

    def test_thieu_prompt_bi_tu_choi_co_ma_va_ly_do_truoc_ai(self):
        thieu = dau_vao()
        thieu.pop('chi_dan')
        payloads = [thieu] + [{**dau_vao(), 'chi_dan': value}
                              for value in (None, '', ' \t\r\n', '\u2003\u00a0')]
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(ca.ThieuPrompt) as err:
                self.goi(payload)
            self.assertEqual(err.exception.ma, 'THIEU_PROMPT')
            self.assertIn('Chức năng chưa gửi nội dung yêu cầu', str(err.exception))
        self.local.assert_not_called()
        self.assertEqual(self.ghi.ban_ghi, [])

    def test_cong_chung_khong_co_prompt_mac_dinh(self):
        for value in (None, '', ' \t\n'):
            with self.subTest(value=value), self.assertRaises(ca.ThieuPrompt) as err:
                self.cong.goi(ca.YeuCauAI('BOC_TACH_HOP_DONG', VAN_BAN, value))
            self.assertEqual(err.exception.ma, 'THIEU_PROMPT')
        self.local.assert_not_called()

    def test_khong_thay_can_cu_la_ket_qua_hop_le(self):
        for flag in ({}, {'chi_cuc_bo': False}, {'chi_cuc_bo': True}):
            for confidence in (0, 0.99):
                with self.subTest(flag=flag, confidence=confidence):
                    self.local.return_value = json.dumps({'truong': [], 'do_tin_cay': confidence})
                    out = self.goi(dau_vao(**flag))
                    self.assertEqual((out['duong'], out['muc']), ('LOCAL', 'VANG'))
                    self.assertEqual(out['cau_tra_loi'], 'Không thấy căn cứ trong tài liệu.')
                    self.assertEqual(out['ly_do'], ['KHONG_THAY_CAN_CU'])
                    self.assertEqual(out['truong'], [])
                    self.assertEqual(out['truong_bi_loai'], [])
                    self.assertEqual(self.ghi.ban_ghi[-1].ket_qua, 'DAT')
                    self.assertNotIn('thử lại', out['thong_bao'])
        self.assertTrue(all(r.duong == 'LOCAL' for r in self.ghi.ban_ghi))

    def test_phan_hoi_hong_va_trich_dan_bi_loai_khong_phai_thieu_can_cu(self):
        for answer, checker in (
                ('không thấy căn cứ', None),
                ('{"truong": []}', None),
                ('{"truong": [], "do_tin_cay": true}', None),
                ('{"truong": [], "do_tin_cay": -1}', None),
                ('{"truong": [{}], "do_tin_cay": 0.99}', None),
                (tra_loi(trich_dan='Ngoài nguồn DEMO.'), None),
                (tra_loi(trich_dan=''), None),
                (tra_loi(), lambda *args: ['lai_suat'])):
            with self.subTest(answer=answer):
                self.local.return_value = answer
                out = self.goi(kiem_tra=checker)
                self.assertEqual((out['duong'], out['muc']), ('KHONG', 'DO'))
                self.assertIsNone(out['cau_tra_loi'])
                self.assertNotIn('KHONG_THAY_CAN_CU', out['ly_do'])

    def test_cloud_bi_khoa_du_co_thieu_false_true_va_cau_hinh_bat(self):
        for flag in ({}, {'chi_cuc_bo': False}, {'chi_cuc_bo': True}):
            for answer in (tra_loi(), tra_loi(do_tin_cay=0.1), 'JSON hỏng'):
                with self.subTest(flag=flag, answer=answer):
                    self.local.return_value = answer
                    out = self.goi(dau_vao(**flag))
                    self.assertNotIn(out['duong'], ('CLOUD', 'LOCAL+CLOUD'))
                    self.assertIs(self.cong.cai_dat['cloud_bat'], True)
        self.assertTrue(all(r.duong == 'LOCAL' for r in self.ghi.ban_ghi))

    def test_local_loi_bao_ro_va_co_the_thu_lai(self):
        for flag in ({}, {'chi_cuc_bo': False}, {'chi_cuc_bo': True}):
            for error, code in ((ca.ai_cuc_bo.LocalAIUnavailable('Lỗi kết nối DEMO'),
                                 'LOCAL_KHONG_CHAY'),
                                (ValueError('Model DEMO chưa sẵn sàng'), 'LOCAL_LOI')):
                with self.subTest(flag=flag, code=code):
                    self.local.side_effect = error
                    out = self.goi(dau_vao(**flag))
                    self.assertEqual((out['duong'], out['muc']), ('KHONG', 'DO'))
                    self.assertIn(code, out['ly_do'])
                    self.assertIn('chưa sẵn sàng', out['thong_bao'])
                    self.assertIn('thử lại', out['thong_bao'])
                    self.assertIsNone(out['cau_tra_loi'])
                    self.assertNotIn('KHONG_THAY_CAN_CU', out['ly_do'])
                    ca.ai_cuc_bo._CONNECTION_FAILURES.clear()
                    self.local.side_effect = None
                    self.local.return_value = tra_loi()
                    self.assertEqual(self.goi(dau_vao(**flag))['duong'], 'LOCAL')

    def test_local_chua_bat_khong_thanh_thieu_can_cu(self):
        self.cong.local_ai['enabled'] = False
        out = self.goi()
        self.assertEqual((out['duong'], out['muc']), ('KHONG', 'DO'))
        self.assertIn('LOCAL_TAT', out['ly_do'])
        self.assertIn('thử lại', out['thong_bao'])
        self.assertIsNone(out['cau_tra_loi'])
        self.local.assert_not_called()

    def test_m9_luon_gui_chi_cuc_bo_true_ca_mau(self):
        sdk = Mock()
        sdk.goi.side_effect = lambda capability, payload: self.goi(payload)
        out = m9_gia_hoi(sdk)
        capability, payload = sdk.goi.call_args.args
        self.assertEqual(capability, 'ai.hoi@1')
        self.assertIs(payload['chi_cuc_bo'], True)
        self.assertEqual(out['duong'], 'LOCAL')
        self.cloud.tra_loi.assert_not_called()

    def test_manifest_schema_g2_17b_va_chi_capability_da_kiem(self):
        manifest = json.loads((bundle.ROOT / 'engines/e_hoi_ai/engine.json')
                              .read_text(encoding='utf-8'))
        self.assertTrue(self.kiem({'$ref': 'urn:ktt:manifest:engine.v1'}, manifest))
        self.assertEqual([(c['ma'], c['dau_vao'], c['dau_ra']) for c in manifest['capability']],
                         [('ai.hoi@1', 'hoi_ai.v2', 'tra_loi_ai.v2')])
        self.assertIs(manifest['ho_so_chay_mau']['headless'], True)
        self.assertIs(manifest['ho_so_chay_mau']['login_csdl'], False)
        self.assertEqual(manifest['ban_giao_ket_qua'], 'core_xac_nhan_truoc_giai_phong')

    @unittest.skipUnless(bundle.Draft202012Validator,
                         'CHUA_KIEM: thiếu jsonschema kiểm meta-schema 2020-12')
    def test_meta_schema_day_du(self):
        for ref in (HOI, TRA_LOI, HOI_V2, TRA_LOI_V2, 'urn:ktt:manifest:engine.v1'):
            bundle.Draft202012Validator.check_schema(self.schemas[ref])


if __name__ == '__main__':
    unittest.main()
