"""AI-1b-01: giữ contract v1, thêm v2 bản 1 chỉ Local; chỉ kiểm offline.

Thiếu jsonschema thì meta-schema là CHUA_KIEM; fallback không thay chứng nhận.
Không gọi AI, dịch vụ ngoài hoặc đọc dữ liệu thật.
"""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_g2_17 as bundle


CONTRACT_ID = 'urn:ktt:contract:hoi_ai.v1'


class HoiAIContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = json.loads(
            (bundle.CONTRACT_DIR / 'ky_thuat.json').read_text(encoding='utf-8'))
        cls.schema = cls.schemas[CONTRACT_ID]
        blocks = bundle._blocks(bundle.SPEC)
        index = next(i for i, obj in enumerate(blocks)
                     if obj.get('$id') == CONTRACT_ID)
        cls.documented_schema, cls.demo = blocks[index:index + 2]
        if bundle.Draft202012Validator:
            def offline(uri):
                raise bundle.NoSuchResource(ref=uri)
            registry = bundle.Registry(retrieve=offline).with_resources(
                (key, bundle.Resource.from_contents(schema))
                for key, schema in cls.schemas.items())
            cls.validator = bundle.Draft202012Validator(cls.schema, registry=registry)

    def validate(self, value):
        with patch('socket.socket', side_effect=AssertionError('Cấm mạng trong AI-1b')):
            if bundle.Draft202012Validator:
                self.validator.validate(value)
            bundle._minimal(value, self.schema, self.schema, self.schemas)

    def reject(self, **changes):
        value = {**deepcopy(self.demo), **changes}
        with patch('socket.socket', side_effect=AssertionError('Cấm mạng trong AI-1b')):
            if bundle.Draft202012Validator:
                from jsonschema.exceptions import ValidationError
                with self.assertRaises(ValidationError):
                    self.validator.validate(value)
            with self.assertRaises(ValueError):
                bundle._minimal(value, self.schema, self.schema, self.schemas)

    @unittest.skipUnless(bundle.Draft202012Validator,
                         'CHUA_KIEM: thiếu jsonschema để kiểm meta-schema 2020-12')
    def test_meta_schema_2020_12(self):
        bundle.Draft202012Validator.check_schema(self.schema)

    def test_schema_khop_tai_lieu_va_ban_dau_khong_vo_noi_dung(self):
        self.assertEqual(self.schema, self.documented_schema)
        self.assertEqual(self.schema['$id'], CONTRACT_ID)
        self.assertEqual(self.schema['$schema'], bundle.DRAFT)
        self.assertIn('1.0.0', self.schema['$comment'])
        self.assertEqual(set(self.schema['required']), {'loai_viec', 'van_ban', 'chi_dan'})
        self.assertNotIn('vo_noi_dung', json.dumps(self.schema))
        self.assertEqual(self.schema['properties']['truong']['default'], [])
        self.assertEqual(self.schema['properties']['dinh_danh_da_biet']['default'], [])
        self.assertIs(self.schema['properties']['chi_cuc_bo']['default'], False)
        # Core chỉ duyệt schema object; false ở annotation/keyword vẫn hợp lệ.
        for node in bundle._nodes(self.schema):
            self.assertIsInstance(node, dict)
        pair = self.schema['$defs']['dinh_danh']['oneOf'][1]
        self.assertEqual(pair['prefixItems'], [{'type': 'string'}, {'type': 'string'}])
        self.assertEqual((pair['minItems'], pair['maxItems']), (2, 2))
        self.assertNotIn('items', pair)

    def test_demo_du_ba_dang_dinh_danh_dat(self):
        self.validate(deepcopy(self.demo))

    def test_bo_qua_tuy_chon_chi_dan_rong_va_nhom_rong_dat(self):
        value = {'loai_viec': 'HOI_DAP_VAY', 'van_ban': 'DEMO', 'chi_dan': ''}
        original = deepcopy(value)
        self.validate(value)
        self.assertEqual(value, original)  # default không tự điền payload.
        value.update(truong=[], chi_cuc_bo=False,
                     dinh_danh_da_biet=['', ['DEMO', ''], {'gia_tri': '', 'nhom': ''}])
        self.validate(value)

    def test_van_ban_chi_khoang_trang_bi_bac(self):
        self.reject(van_ban=' \t\r\n')

    def test_khoa_la_bi_bac(self):
        self.reject(khoa_la='DEMO')

    def test_ten_truong_rong_bi_bac(self):
        self.reject(truong=[''])

    def test_co_null_bi_bac(self):
        self.reject(chi_cuc_bo=None)

    def test_cap_dinh_danh_mot_phan_tu_bi_bac(self):
        self.reject(dinh_danh_da_biet=[['DEMO']])

    def test_object_dinh_danh_thieu_nhom_bi_bac(self):
        self.reject(dinh_danh_da_biet=[{'gia_tri': 'DEMO'}])

    def test_loai_viec_rong_bi_bac(self):
        self.reject(loai_viec='')

    def test_dinh_danh_da_biet_null_bi_bac(self):
        self.reject(dinh_danh_da_biet=None)

    def test_cap_dinh_danh_phai_dung_hai_chuoi_va_object_dong_khoa(self):
        for item in (['DEMO', 1], [1, 'CONG_TY'], ['DEMO', 'CONG_TY', 'THUA'],
                     {'gia_tri': 'DEMO', 'nhom': '', 'khoa_la': 'DEMO'}):
            with self.subTest(item=item):
                self.reject(dinh_danh_da_biet=[item])


class HoiAIBanMotContractTest(unittest.TestCase):
    """Chỉ kiểm cấu trúc; xác minh binding/lease thật thuộc lát Core."""

    HOI = 'urn:ktt:contract:hoi_ai.v2'
    TRA_LOI = 'urn:ktt:contract:tra_loi_ai.v2'
    TEP = '10000000-0000-4000-8000-000000000001'
    TU_CHOI = {
        'ma': 'THIEU_PROMPT',
        'thong_bao': 'Chức năng chưa gửi nội dung yêu cầu. '
                     'Cần bổ sung nội dung yêu cầu trước khi hỏi AI.',
    }

    @classmethod
    def setUpClass(cls):
        cls.bundles = [bundle._json(path.read_text(encoding='utf-8')) for path in (
            bundle.CONTRACT_DIR / 'ky_thuat.json',
            bundle.ROOT / 'engines/e_hoi_ai/contract/schemas.json',
        )]
        if bundle.Draft202012Validator:
            def offline(uri):
                raise bundle.NoSuchResource(ref=uri)
            cls.registries = [bundle.Registry(retrieve=offline).with_resources(
                (key, bundle.Resource.from_contents(schema))
                for key, schema in schemas.items()) for schemas in cls.bundles]
            from kho_tri_thuc.core.dispatcher import KiemSchema
            cls.core_checker = KiemSchema()

    def dau_vao(self):
        return dict(loai_viec='BOC_TACH_HOP_DONG',
                    van_ban='Số tiền DEMO 1.000.000 VND, ngày 30/10/2026.',
                    chi_dan='Trích số tiền DEMO kèm căn cứ.',
                    ma_function='trich_hop_dong_demo', ma_prompt='trich_tien_demo',
                    phien_ban_prompt='1.0.0')

    def nguon_core(self):
        return dict(ma_module='m_demo', ma_function='trich_hop_dong_demo',
                    ma_prompt='trich_tien_demo', phien_ban_prompt='1.0.0',
                    phap_nhan_id='10000000-0000-4000-8000-000000000002',
                    viec_id='10000000-0000-4000-8000-000000000003', revision=1,
                    nguon_tep_ids=[self.TEP],
                    vi_tri=dict(tep_id=self.TEP, dinh_vi='doan:1'))

    def tra_loi(self):
        return dict(contract='tra_loi_ai.v2', phien_ban='2.0.0', revision=1,
                    nguon_tep_ids=[self.TEP], cau_tra_loi=None,
                    truong=[dict(ten='so_tien', nguon='LOCAL', gia_tri_local=None,
                        gia_tri=dict(kieu='van_ban', gia_tri='1.000.000 VND'),
                        dan_chung=[dict(vi_tri=dict(tep_id=self.TEP, dinh_vi='doan:1'),
                            trich_dan='Số tiền DEMO 1.000.000 VND, ngày 30/10/2026.')])],
                    duong='LOCAL', mo_hinh=[dict(duong='LOCAL', ten='Model DEMO',
                        phien_ban=None, can_cu='cau_hinh')], muc='VANG',
                    thong_bao='Có kết quả DEMO kèm trích dẫn.', ly_do=[],
                    truong_bi_loai=[], ma_yeu_cau_nguon='DEMO-01',
                    kiem_tra=dict(trich_dan='dat', mo_che='khong_ap_dung'))

    def khong_can_cu(self):
        value = self.tra_loi()
        value.update(cau_tra_loi='Không thấy căn cứ trong tài liệu.', truong=[],
                     thong_bao='Không thấy căn cứ trong tài liệu.',
                     ly_do=['KHONG_THAY_CAN_CU'])
        value['kiem_tra']['trich_dan'] = 'chua_kiem'
        return value

    def loi_local(self, code='LOCAL_KHONG_CHAY'):
        value = self.tra_loi()
        value.update(cau_tra_loi=None, truong=[], mo_hinh=[], duong='KHONG',
                     muc='DO', ly_do=[code],
                     thong_bao='Local AI chưa sẵn sàng. Có thể thử lại.')
        value['kiem_tra']['trich_dan'] = 'chua_kiem'
        return value

    def kiem(self, ref, value, dat=True):
        original = deepcopy(value)
        with patch('socket.socket', side_effect=AssertionError('Cấm mạng AI-1b-01')):
            for i, schemas in enumerate(self.bundles):
                with self.subTest(bundle=i, ref=ref):
                    schema, root = bundle._resolve(ref, {}, schemas)
                    if dat:
                        bundle._minimal(value, schema, root, schemas)
                    else:
                        with self.assertRaises(ValueError):
                            bundle._minimal(value, schema, root, schemas)
                    if bundle.Draft202012Validator:
                        validator = bundle.Draft202012Validator(
                            {'$ref': ref}, registry=self.registries[i],
                            format_checker=bundle.FormatChecker())
                        self.assertEqual(validator.is_valid(value), dat)
            if bundle.Draft202012Validator:
                self.assertEqual(self.core_checker.kiem({'$ref': ref}, value), dat)
        self.assertEqual(value, original)

    @unittest.skipUnless(bundle.Draft202012Validator,
                         'CHUA_KIEM: thiếu jsonschema để kiểm meta-schema 2020-12')
    def test_meta_schema_v2_va_closure_goi_doc_lap(self):
        for schemas in self.bundles:
            for key in (self.HOI, self.TRA_LOI):
                bundle.Draft202012Validator.check_schema(schemas[key])
                for node in bundle._nodes(schemas[key]):
                    if '$ref' in node:
                        bundle._resolve(node['$ref'], schemas[key], schemas)

    def test_core_va_goi_engine_khop_ca_v1_v2(self):
        for key in (CONTRACT_ID, 'urn:ktt:contract:tra_loi_ai.v1', self.HOI, self.TRA_LOI):
            self.assertEqual(self.bundles[0][key], self.bundles[1][key])

    def test_dau_vao_hop_le_co_metadata_va_khong_tu_dien_co(self):
        value = self.dau_vao()
        self.kiem(self.HOI, value)
        self.assertNotIn('chi_cuc_bo', value)
        self.kiem(self.HOI, dict(value, chi_cuc_bo=True, truong=[], dinh_danh_da_biet=[]))

    def test_thieu_tung_truong_bat_buoc_bi_bac(self):
        for field in self.dau_vao():
            value = self.dau_vao()
            value.pop(field)
            with self.subTest(field=field):
                self.kiem(self.HOI, value, False)

    def test_metadata_rong_trang_sai_kieu_bi_bac(self):
        for field in ('ma_function', 'ma_prompt', 'phien_ban_prompt'):
            for value in ('', ' \t\r\n', '\u00a0\u2003', None, 1, True, [], {}):
                with self.subTest(field=field, value=value):
                    self.kiem(self.HOI, {**self.dau_vao(), field: value}, False)

    def test_prompt_rong_trang_sai_kieu_khong_co_mac_dinh(self):
        for prompt in ('', ' \t\r\n', '\u00a0\u2003', None, 1, True, [], {}):
            with self.subTest(prompt=prompt):
                self.kiem(self.HOI, dict(self.dau_vao(), chi_dan=prompt), False)

    def test_van_ban_rong_trang_bi_bac(self):
        for text in ('', ' \t\r\n', None):
            with self.subTest(text=text):
                self.kiem(self.HOI, dict(self.dau_vao(), van_ban=text), False)

    def test_tu_choi_prompt_co_ma_va_cau_co_dinh(self):
        ref = self.HOI + '#/$defs/tu_choi_thieu_prompt'
        self.kiem(ref, self.TU_CHOI)
        for changes in ({'ma': 'LOCAL_LOI'}, {'thong_bao': 'DEMO tùy ý'},
                        {'chi_dan': 'Không được phản chiếu nội dung DEMO'}):
            self.kiem(ref, {**self.TU_CHOI, **changes}, False)

    def test_payload_khong_nhan_nguon_tin_cay_tu_khai(self):
        for field, value in {**self.nguon_core(),
                'nguon_core': self.nguon_core(), 'da_xac_minh': True,
                'nguon_tin_cay': True, 'ham': 'adapter_demo'}.items():
            if field in ('ma_function', 'ma_prompt', 'phien_ban_prompt'):
                continue  # Core đối chiếu ba giá trị này với khai báo gói module.
            with self.subTest(field=field):
                self.kiem(self.HOI, {**self.dau_vao(), field: value}, False)

    def test_context_core_tach_khoi_payload_khong_co_co_tu_xac_minh(self):
        ref = self.HOI + '#/$defs/nguon_core'
        self.kiem(ref, self.nguon_core())
        for field in self.nguon_core():
            value = self.nguon_core()
            value.pop(field)
            with self.subTest(field=field):
                self.kiem(ref, value, False)
        self.kiem(ref, dict(self.nguon_core(), da_xac_minh=True), False)

    def test_context_core_bac_nguon_thieu_va_sai_cau_truc(self):
        for changes in ({'revision': 0}, {'revision': True}, {'nguon_tep_ids': []},
                {'nguon_tep_ids': [self.TEP, self.TEP]}, {'phap_nhan_id': 'DEMO'},
                {'vi_tri': {'tep_id': self.TEP}}, {'ma_module': ' '},
                {'ma_prompt': ' '}, {'ma_function': ''}, {'phien_ban_prompt': None}):
            with self.subTest(changes=changes):
                self.kiem(self.HOI + '#/$defs/nguon_core',
                          {**self.nguon_core(), **changes}, False)

    def test_khong_co_co_payload_bat_cloud(self):
        for flag in (False, None, 0, 1, 'true', 'false'):
            with self.subTest(flag=flag):
                self.kiem(self.HOI, dict(self.dau_vao(), chi_cuc_bo=flag), False)
        for field in ('cloud_bat', 'cho_phep_cloud', 'duong', 'luot_che_id', 'cai_dat'):
            with self.subTest(field=field):
                self.kiem(self.HOI, {**self.dau_vao(), field: True}, False)

    def test_v1_giu_tuong_thich_va_khong_tu_nhan_payload_v2(self):
        old = dict(loai_viec='HOI_DAP_VAY', van_ban='DEMO', chi_dan='', chi_cuc_bo=False)
        self.kiem(CONTRACT_ID, old)
        self.kiem(self.HOI, old, False)
        self.kiem(CONTRACT_ID, self.dau_vao(), False)

    def test_tra_loi_local_co_dan_chung_hop_le(self):
        self.kiem(self.TRA_LOI, self.tra_loi())

    def test_thieu_tung_truong_ket_qua_bi_bac(self):
        for field in self.tra_loi():
            value = self.tra_loi()
            value.pop(field)
            with self.subTest(field=field):
                self.kiem(self.TRA_LOI, value, False)

    def test_khong_thay_can_cu_la_ket_qua_local_rieng(self):
        self.kiem(self.TRA_LOI, self.khong_can_cu())

    def test_khong_thay_can_cu_khong_tron_loi_hoac_bia_trich_dan(self):
        for changes in ({'duong': 'KHONG'}, {'muc': 'DO'}, {'cau_tra_loi': None},
                {'thong_bao': 'Chưa có kết quả AI, cần người làm.'},
                {'ly_do': ['KHONG_THAY_CAN_CU', 'LOCAL_LOI']},
                {'truong': self.tra_loi()['truong']}, {'truong_bi_loai': ['DEMO']},
                {'kiem_tra': dict(trich_dan='dat', mo_che='khong_ap_dung')}):
            with self.subTest(changes=changes):
                self.kiem(self.TRA_LOI, {**self.khong_can_cu(), **changes}, False)

    def test_local_tat_mat_ket_noi_model_loi_tach_khoi_thieu_can_cu(self):
        for code in ('LOCAL_TAT', 'LOCAL_KHONG_CHAY', 'LOCAL_LOI'):
            value = self.loi_local(code)
            self.kiem(self.TRA_LOI, value)
            self.kiem(self.TRA_LOI, dict(value, ly_do=[code, 'KHONG_THAY_CAN_CU']), False)
            self.kiem(self.TRA_LOI, dict(self.tra_loi(), ly_do=[code]), False)

    def test_loi_local_khong_tra_loi_hay_ket_qua_gia(self):
        for changes in ({'cau_tra_loi': 'Câu trả lời DEMO bịa'}, {'muc': 'VANG'},
                        {'truong': self.tra_loi()['truong']}, {'ly_do': []}):
            with self.subTest(changes=changes):
                self.kiem(self.TRA_LOI, {**self.loi_local(), **changes}, False)
        self.kiem(self.TRA_LOI, dict(self.tra_loi(), truong=[]), False)

    def test_ket_qua_bac_cloud_o_moi_duong_va_luot_che(self):
        for direction in ('CLOUD', 'LOCAL+CLOUD'):
            self.kiem(self.TRA_LOI, dict(self.tra_loi(), duong=direction), False)
        value = self.tra_loi()
        value['truong'][0]['nguon'] = 'CLOUD'
        self.kiem(self.TRA_LOI, value, False)
        value = self.tra_loi()
        value['mo_hinh'][0]['duong'] = 'CLOUD'
        self.kiem(self.TRA_LOI, value, False)
        self.kiem(self.TRA_LOI, dict(self.tra_loi(), luot_che_id=self.TEP), False)
        for status in ('dat', 'khong_dat', 'chua_kiem'):
            value = self.tra_loi()
            value['kiem_tra']['mo_che'] = status
            self.kiem(self.TRA_LOI, value, False)

    def test_truong_ket_qua_phai_co_dan_chung_va_kiem_python(self):
        value = self.tra_loi()
        value['truong'][0]['dan_chung'] = []
        self.kiem(self.TRA_LOI, value, False)
        value = self.tra_loi()
        value['kiem_tra']['trich_dan'] = 'chua_kiem'
        self.kiem(self.TRA_LOI, value, False)

    def test_ket_qua_dong_khoa_va_phien_ban_khong_doi_am_tham(self):
        for changes in ({'contract': 'tra_loi_ai.v1'}, {'phien_ban': '1.0.0'},
                        {'nguon_core': self.nguon_core()}, {'cloud_bat': False}):
            with self.subTest(changes=changes):
                self.kiem(self.TRA_LOI, {**self.tra_loi(), **changes}, False)


if __name__ == '__main__':
    unittest.main()
