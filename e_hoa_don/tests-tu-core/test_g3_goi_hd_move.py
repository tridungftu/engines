"""G3-GOI-21: gói hóa đơn — shim namespace, discovery, ví dụ contract. Dữ liệu giả, thuần."""

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
GOI = ROOT / 'engines' / 'e_hoa_don'
CO_SCHEMA = (importlib.util.find_spec('jsonschema') is not None
             and importlib.util.find_spec('referencing') is not None)


class GoiHoaDonMove(unittest.TestCase):
    def test_shim_tro_ve_goi_moi_va_giu_ten(self):
        for ten in ('chay', 'doc', 'tai', 'phien'):
            mod = importlib.import_module('kho_tri_thuc.engines.e_hoa_don.' + ten)
            self.assertEqual(Path(mod.__file__).resolve(), (GOI / (ten + '.py')).resolve())
        self.assertFalse((ROOT / 'src/kho_tri_thuc/engines/e_hoa_don/engine.json').exists())
        for ten in ('bang_ke.cjs', 'portal.cjs'):
            self.assertFalse((ROOT / 'src/kho_tri_thuc/engines/e_hoa_don' / ten).exists())
            self.assertTrue((GOI / ten).is_file())

    def test_import_tu_cwd_khac(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as cwd:
            out = subprocess.run(
                [sys.executable, '-X', 'utf8', '-B', '-c',
                 'import kho_tri_thuc.engines.e_hoa_don.doc as m; print(m.__file__)'],
                cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                env={**os.environ, 'PYTHONPATH': os.environ.get('PYTHONPATH', str(ROOT / 'src'))})
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        self.assertEqual(Path(out.stdout.strip()).resolve(), (GOI / 'doc.py').resolve())

    def test_discovery_nhan_engine_json_cua_goi(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as tmp:
            root = Path(tmp) / 'engines'
            shutil.copytree(GOI, root / 'e_hoa_don', ignore=shutil.ignore_patterns('__pycache__'))
            kq = nap.doc_engines(root, phien_ban_core='1.0.0')
        self.assertEqual(len(kq), 1)
        self.assertEqual(kq[0].ma, 'e_hoa_don')
        self.assertIn(kq[0].ket_luan, ('DAT',) if CO_SCHEMA else ('DAT', 'CHUA_KIEM'), kq[0].ly_do)

    def test_discovery_quet_thang_thu_muc_engines_cua_repo(self):
        kq = [r for r in nap.doc_engines(ROOT / 'engines', phien_ban_core='1.0.0')
              if r.ma == 'e_hoa_don']
        self.assertEqual(len(kq), 1)
        self.assertIn(kq[0].ket_luan, ('DAT', 'CHUA_KIEM'), kq[0].ly_do)

    def test_schemas_trung_ban_core(self):
        core = json.loads((ROOT / 'src/kho_tri_thuc/core/contract/ky_thuat.json')
                          .read_text(encoding='utf-8'))
        goi_s = json.loads((GOI / 'contract/schemas.json').read_text(encoding='utf-8'))
        self.assertEqual(set(goi_s), {'urn:ktt:contract:chung.v1',
                                      'urn:ktt:contract:tham_chieu_tep.v1',
                                      'urn:ktt:contract:hoa_don.v1'})
        for k, v in goi_s.items():
            self.assertEqual(v, core[k], k)

    @unittest.skipUnless(CO_SCHEMA, 'CHUA_KIEM: thiếu jsonschema/referencing')
    def test_vi_du_hop_le_va_ca_am(self):
        Validator, checker, registry, _, schemas = goi.dung_registry_schema()
        vi_du = json.loads((GOI / 'contract/vi_du.json').read_text(encoding='utf-8'))['tham_chieu_tep.v1']
        v = Validator(schemas['urn:ktt:contract:tham_chieu_tep.v1'], registry=registry,
                      format_checker=checker)
        for ca in vi_du['hop_le']:
            v.validate(ca)
        for ca in vi_du['ca_am']:
            with self.assertRaises(Exception, msg=ca['mo_ta']):
                v.validate(ca['du_lieu'])


if __name__ == '__main__':
    unittest.main()
