"""G3-GOI-27: gói Mask chuyển vị trí — shim namespace, chưa công bố. Dữ liệu giả, thuần."""

import importlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from kho_tri_thuc.core import nap_engine as nap

ROOT = Path(__file__).resolve().parents[1]
GOI = ROOT / 'engines' / 'e_mask'
CU = ROOT / 'src/kho_tri_thuc/engines/e_mask'


class GoiMaskMove(unittest.TestCase):
    def test_shim_tro_ve_goi_moi_va_giu_ten(self):
        for ten in ('chay', 'vong_doi'):
            mod = importlib.import_module('kho_tri_thuc.engines.e_mask.' + ten)
            self.assertEqual(Path(mod.__file__).resolve(), (GOI / (ten + '.py')).resolve())

    def test_khong_con_tep_o_duong_cu_ngoai_shim(self):
        con_lai = sorted(p.relative_to(CU).as_posix() for p in CU.rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts)
        self.assertEqual(con_lai, ['__init__.py'])

    def test_import_tu_cwd_khac(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as cwd:
            out = subprocess.run(
                [sys.executable, '-X', 'utf8', '-B', '-c',
                 'import kho_tri_thuc.engines.e_mask.vong_doi as m; print(m.__file__)'],
                cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                env={**os.environ, 'PYTHONPATH': os.environ.get('PYTHONPATH', str(ROOT / 'src'))})
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        self.assertEqual(Path(out.stdout.strip()).resolve(), (GOI / 'vong_doi.py').resolve())

    def test_mask_van_cho_khong_cong_bo(self):
        for ten in ('engine.json', 'contract/schemas.json', 'contract/vi_du.json'):
            self.assertFalse((GOI / ten).exists(), ten)
        self.assertTrue((GOI / 'contract/du_thao.json').is_file())
        # Không engine.json -> discovery không được coi Mask là engine đạt.
        kq = [r for r in nap.doc_engines(ROOT / 'engines', phien_ban_core='1.0.0') if r.ma == 'e_mask']
        for r in kq:
            self.assertNotEqual(r.ket_luan, 'DAT', r.ly_do)


if __name__ == '__main__':
    unittest.main()
