"""G3-GOI-01 / AI-1b-02: gói AI, bản ghim và ví dụ DEMO; thuần/offline.

Contract v2 được giao song song ở AI-1b-01. Thiếu schema phải báo lỗi;
không dùng schema tự dựng hoặc bỏ kiểm để coi gói đã đủ điều kiện chạy.
"""

from copy import deepcopy
import importlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from kho_tri_thuc.core import goi, nap_engine as nap

ROOT = Path(__file__).resolve().parents[1]
GOI = ROOT / 'engines' / 'e_hoi_ai'
CO_SCHEMA = (importlib.util.find_spec('jsonschema') is not None
             and importlib.util.find_spec('referencing') is not None)


class GoiAiMau(unittest.TestCase):
    def doc_json(self, ten):
        return json.loads((GOI / ten).read_text(encoding='utf-8'))

    def bo_kiem_v2(self, ma):
        Validator, checker, registry, _, schemas = goi.dung_registry_schema()
        identity = 'urn:ktt:contract:' + ma
        self.assertTrue(identity in schemas, 'Cần ghép contract v2 của AI-1b-01 trước khi nghiệm thu: ' + ma)
        return Validator(schemas[identity], registry=registry, format_checker=checker)

    def test_shim_tro_ve_goi_moi_va_giu_ten(self):
        for ten in ('chay', 'dto', 'hoi', 'bi_mat', 'nhat_ky'):
            mod = importlib.import_module('kho_tri_thuc.engines.e_hoi_ai.' + ten)
            self.assertEqual(Path(mod.__file__).resolve(), (GOI / (ten + '.py')).resolve())
        self.assertFalse((ROOT / 'src/kho_tri_thuc/engines/e_hoi_ai/engine.json').exists())

    def test_import_tu_cwd_khac(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as cwd:
            out = subprocess.run(
                [sys.executable, '-X', 'utf8', '-B', '-c',
                 'import kho_tri_thuc.engines.e_hoi_ai.hoi as m; print(m.__file__)'],
                cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                env={**os.environ, 'PYTHONPATH': os.environ.get('PYTHONPATH', str(ROOT / 'src'))})
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        self.assertEqual(Path(out.stdout.strip()).resolve(), (GOI / 'hoi.py').resolve())

    def test_discovery_nhan_engine_json_cua_goi(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as tmp:
            root = Path(tmp) / 'engines'
            shutil.copytree(GOI, root / 'e_hoi_ai', ignore=shutil.ignore_patterns('__pycache__'))
            kq = nap.doc_engines(root, phien_ban_core='1.0.0')
        self.assertEqual(len(kq), 1)
        self.assertEqual(kq[0].ma, 'e_hoi_ai')
        self.assertIn(kq[0].ket_luan, ('DAT',) if CO_SCHEMA else ('DAT', 'CHUA_KIEM'), kq[0].ly_do)

    def test_discovery_quet_thang_thu_muc_engines_cua_repo(self):
        kq = [r for r in nap.doc_engines(ROOT / 'engines', phien_ban_core='1.0.0')
              if r.ma == 'e_hoi_ai']
        self.assertEqual(len(kq), 1)
        self.assertIn(kq[0].ket_luan, ('DAT', 'CHUA_KIEM'), kq[0].ly_do)

    @unittest.skipUnless(CO_SCHEMA, 'CHUA_KIEM: thiếu jsonschema/referencing')
    def test_vi_du_hop_le_va_ca_am(self):
        Validator, checker, registry, _, schemas = goi.dung_registry_schema()
        vi_du = json.loads((GOI / 'contract/vi_du.json').read_text(encoding='utf-8'))['hoi_ai.v1']
        v = Validator(schemas['urn:ktt:contract:hoi_ai.v1'], registry=registry, format_checker=checker)
        for ca in vi_du['hop_le']:
            with self.subTest(loai='hop_le', ca=ca):
                v.validate(ca)
        from jsonschema.exceptions import ValidationError
        for ca in vi_du['ca_am']:
            with self.subTest(ca=ca['mo_ta']), self.assertRaises(ValidationError):
                v.validate(ca['du_lieu'])

    def test_manifest_ghim_v2_va_co_vi_du_hai_chieu(self):
        caps = self.doc_json('engine.json')['capability']
        self.assertEqual([(c['ma'], c['dau_vao'], c['dau_ra']) for c in caps],
                         [('ai.hoi@1', 'hoi_ai.v2', 'tra_loi_ai.v2')])
        vi_du = self.doc_json('contract/vi_du.json')
        self.assertIn('Dữ liệu giả (DEMO)', vi_du['luu_y'])
        self.assertIn('hoi_ai.v1', vi_du)
        for ma in (caps[0]['dau_vao'], caps[0]['dau_ra']):
            self.assertTrue(vi_du[ma]['hop_le'])
            self.assertTrue(vi_du[ma]['ca_am'])

    def test_vi_du_metadata_prompt_va_nguon_demo(self):
        vi_du = self.doc_json('contract/vi_du.json')
        for ca in vi_du['hoi_ai.v2']['hop_le']:
            with self.subTest(ca=ca):
                for ten in ('ma_function', 'ma_prompt', 'phien_ban_prompt', 'chi_dan'):
                    self.assertIsInstance(ca[ten], str)
                    self.assertTrue(ca[ten].strip())
                self.assertIn('DEMO', ca['van_ban'])
                self.assertIn('DEMO', ca['chi_dan'])
                self.assertIs(ca['chi_cuc_bo'], True)
                self.assertFalse({'nguon_core', 'phap_nhan_id', 'viec_id', 'da_xac_minh'} & ca.keys())
        for ca in vi_du['tra_loi_ai.v2']['hop_le']:
            with self.subTest(ca=ca['ma_yeu_cau_nguon']):
                self.assertEqual((ca['contract'], ca['phien_ban']), ('tra_loi_ai.v2', '2.0.0'))
                self.assertIn('DEMO', ca['ma_yeu_cau_nguon'])
                self.assertIn(ca['duong'], ('LOCAL', 'KHONG'))
                self.assertTrue(all(m['duong'] == 'LOCAL' and 'DEMO' in m['ten']
                                    for m in ca['mo_hinh']))
                self.assertNotIn('luot_che_id', ca)

    @unittest.skipUnless(CO_SCHEMA, 'CHUA_KIEM: thiếu jsonschema/referencing')
    def test_vi_du_v2_qua_schema_core_va_goi(self):
        from jsonschema.exceptions import ValidationError
        vi_du = self.doc_json('contract/vi_du.json')
        bundle = self.doc_json('contract/schemas.json')
        validators = {ma: self.bo_kiem_v2(ma) for ma in ('hoi_ai.v2', 'tra_loi_ai.v2')}
        for ma in ('hoi_ai.v2', 'tra_loi_ai.v2'):
            with self.subTest(contract=ma):
                v = validators[ma]
                identity = 'urn:ktt:contract:' + ma
                self.assertTrue(identity in bundle, 'Bộ schema gói cần ghép từ AI-1b-01: ' + ma)
                self.assertEqual(bundle[identity], v.schema)
                for ca in vi_du[ma]['hop_le']:
                    v.validate(ca)
                for ca in vi_du[ma]['ca_am']:
                    with self.subTest(ca=ca['mo_ta']), self.assertRaises(ValidationError):
                        v.validate(ca['du_lieu'])

    @unittest.skipUnless(CO_SCHEMA, 'CHUA_KIEM: thiếu jsonschema/referencing')
    def test_v2_bac_thieu_trang_sai_kieu_prompt_va_nguon_tu_khai(self):
        from jsonschema.exceptions import ValidationError
        v = self.bo_kiem_v2('hoi_ai.v2')
        ca = self.doc_json('contract/vi_du.json')['hoi_ai.v2']['hop_le'][0]
        v.validate(ca)
        for ten in ('ma_function', 'ma_prompt', 'phien_ban_prompt', 'chi_dan'):
            thieu = deepcopy(ca)
            thieu.pop(ten)
            with self.subTest(truong=ten, loai='thieu'), self.assertRaises(ValidationError):
                v.validate(thieu)
            for value in ('', ' \t\n ', None, 1):
                with self.subTest(truong=ten, value=value), self.assertRaises(ValidationError):
                    v.validate({**ca, ten: value})
        for them in ({'chi_cuc_bo': False}, {'khac': 'DEMO'},
                     {'nguon_core': {'ma_module': 'demo', 'da_xac_minh': True}}):
            with self.subTest(them=them), self.assertRaises(ValidationError):
                v.validate({**ca, **them})
        khong_co_co = deepcopy(ca)
        khong_co_co.pop('chi_cuc_bo')
        v.validate(khong_co_co)

    def test_vi_du_co_can_cu_khong_can_cu_va_loi_local_rieng_biet(self):
        vi_du = self.doc_json('contract/vi_du.json')
        co, khong, loi = vi_du['tra_loi_ai.v2']['hop_le']
        van_ban = vi_du['hoi_ai.v2']['hop_le'][0]['van_ban']
        for truong in co['truong']:
            self.assertEqual(truong['nguon'], 'LOCAL')
            for dan_chung in truong['dan_chung']:
                self.assertIn(dan_chung['trich_dan'], van_ban)
                self.assertIn(dan_chung['vi_tri']['tep_id'], co['nguon_tep_ids'])
                self.assertIn(truong['gia_tri']['gia_tri'], dan_chung['trich_dan'])
        self.assertEqual((khong['duong'], khong['muc']), ('LOCAL', 'VANG'))
        self.assertEqual(khong['ly_do'], ['KHONG_THAY_CAN_CU'])
        self.assertEqual(khong['cau_tra_loi'], 'Không thấy căn cứ trong tài liệu.')
        self.assertEqual(khong['thong_bao'], khong['cau_tra_loi'])
        self.assertEqual((khong['truong'], khong['truong_bi_loai']), ([], []))
        self.assertEqual((loi['duong'], loi['muc']), ('KHONG', 'DO'))
        self.assertIsNone(loi['cau_tra_loi'])
        self.assertIn('LOCAL_KHONG_CHAY', loi['ly_do'])
        self.assertNotIn('KHONG_THAY_CAN_CU', loi['ly_do'])

    @unittest.skipUnless(CO_SCHEMA, 'CHUA_KIEM: thiếu jsonschema/referencing')
    def test_v2_bac_khong_can_cu_nham_loi_local_va_ket_qua_cloud(self):
        from jsonschema.exceptions import ValidationError
        v = self.bo_kiem_v2('tra_loi_ai.v2')
        co, khong, loi = self.doc_json('contract/vi_du.json')['tra_loi_ai.v2']['hop_le']
        for ca in (co, khong, loi):
            v.validate(ca)
        ca_am = [
            {**khong, 'duong': 'KHONG'},
            {**khong, 'muc': 'DO'},
            {**khong, 'cau_tra_loi': None},
            {**khong, 'truong': co['truong']},
            {**khong, 'ly_do': ['KHONG_THAY_CAN_CU', 'LOCAL_KHONG_CHAY']},
            {**loi, 'ly_do': ['KHONG_THAY_CAN_CU']},
            {**co, 'duong': 'CLOUD'},
            {**co, 'duong': 'LOCAL+CLOUD'},
            {**co, 'mo_hinh': [{**co['mo_hinh'][0], 'duong': 'CLOUD'}]},
            {**co, 'truong': [{**co['truong'][0], 'nguon': 'CLOUD'}]},
            {**co, 'contract': 'tra_loi_ai.v1', 'phien_ban': '1.0.0'},
        ]
        for ca in ca_am:
            with self.subTest(ca=ca), self.assertRaises(ValidationError):
                v.validate(ca)


if __name__ == '__main__':
    unittest.main()
