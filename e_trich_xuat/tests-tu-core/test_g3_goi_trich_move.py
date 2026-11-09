"""G3-GOI-31: gói trích tham số — shim namespace, discovery, ví dụ contract. Dữ liệu giả, thuần."""

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
GOI = ROOT / 'engines' / 'e_trich_xuat'
CO_SCHEMA = (importlib.util.find_spec('jsonschema') is not None
             and importlib.util.find_spec('referencing') is not None)


class GoiTrichMove(unittest.TestCase):
    def test_shim_tro_ve_goi_moi_va_giu_ten(self):
        for ten in ('chay', 'docx', 'tham_so', 'tich_hop', 'quy_trinh', 'ai_chung', 'do_chinh_xac'):
            mod = importlib.import_module('kho_tri_thuc.engines.e_trich_xuat.' + ten)
            self.assertEqual(Path(mod.__file__).resolve(), (GOI / (ten + '.py')).resolve())
        self.assertFalse((ROOT / 'src/kho_tri_thuc/engines/e_trich_xuat/engine.json').exists())
        for ten in ('ai_chung.py', 'chay.py', 'docx.py', 'do_chinh_xac.py',
                    'quy_trinh.py', 'tham_so.py', 'tich_hop.py'):
            self.assertFalse((ROOT / 'src/kho_tri_thuc/engines/e_trich_xuat' / ten).exists())
            self.assertTrue((GOI / ten).is_file())
        con_lai = [p.name for p in (ROOT / 'src/kho_tri_thuc/engines/e_trich_xuat').iterdir()
                   if p.name != '__pycache__']
        self.assertEqual(con_lai, ['__init__.py'])

    def test_import_tu_cwd_khac(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as cwd:
            out = subprocess.run(
                [sys.executable, '-X', 'utf8', '-B', '-c',
                 'import kho_tri_thuc.engines.e_trich_xuat.docx as m; print(m.__file__)'],
                cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                env={**os.environ, 'PYTHONPATH': os.environ.get('PYTHONPATH', str(ROOT / 'src'))})
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        self.assertEqual(Path(out.stdout.strip()).resolve(), (GOI / 'docx.py').resolve())

    def test_discovery_nhan_engine_json_cua_goi(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as tmp:
            root = Path(tmp) / 'engines'
            shutil.copytree(GOI, root / 'e_trich_xuat', ignore=shutil.ignore_patterns('__pycache__'))
            kq = nap.doc_engines(root, phien_ban_core='1.0.0')
        self.assertEqual(len(kq), 1)
        self.assertEqual(kq[0].ma, 'e_trich_xuat')
        self.assertIn(kq[0].ket_luan, ('DAT',) if CO_SCHEMA else ('DAT', 'CHUA_KIEM'), kq[0].ly_do)

    def test_discovery_quet_thang_thu_muc_engines_cua_repo(self):
        kq = [r for r in nap.doc_engines(ROOT / 'engines', phien_ban_core='1.0.0')
              if r.ma == 'e_trich_xuat']
        self.assertEqual(len(kq), 1)
        self.assertIn(kq[0].ket_luan, ('DAT', 'CHUA_KIEM'), kq[0].ly_do)

    def test_schemas_trung_ban_core(self):
        core = json.loads((ROOT / 'src/kho_tri_thuc/core/contract/ky_thuat.json')
                          .read_text(encoding='utf-8'))
        goi_s = json.loads((GOI / 'contract/schemas.json').read_text(encoding='utf-8'))
        self.assertEqual(set(goi_s), {'urn:ktt:contract:chung.v1',
                                      'urn:ktt:contract:tham_chieu_tep.v1',
                                      'urn:ktt:contract:tham_so.v1'})
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
