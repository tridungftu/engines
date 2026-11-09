"""G3-GOI-15: gói OCR chuyển vị trí — shim namespace và discovery. Dữ liệu giả, thuần."""

import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from kho_tri_thuc.core import nap_engine as nap

ROOT = Path(__file__).resolve().parents[1]
GOI = ROOT / 'engines' / 'e_ocr'


class GoiOcrMove(unittest.TestCase):
    def test_shim_tro_ve_goi_moi_va_giu_ten(self):
        for ten in ('abbyy', 'bang', 'ban_giao', 'chay', 'van_ban'):
            mod = importlib.import_module('kho_tri_thuc.engines.e_ocr.' + ten)
            self.assertEqual(Path(mod.__file__).resolve(), (GOI / (ten + '.py')).resolve())
        self.assertFalse((ROOT / 'src/kho_tri_thuc/engines/e_ocr/engine.json').exists())

    def test_import_tu_cwd_khac(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as cwd:
            out = subprocess.run(
                [sys.executable, '-X', 'utf8', '-B', '-c',
                 'import kho_tri_thuc.engines.e_ocr.van_ban as m; print(m.__file__)'],
                cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                env={**os.environ, 'PYTHONPATH': os.environ.get('PYTHONPATH', str(ROOT / 'src'))})
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        self.assertEqual(Path(out.stdout.strip()).resolve(), (GOI / 'van_ban.py').resolve())

    def test_discovery_nhan_engine_json_cua_goi(self):
        with tempfile.TemporaryDirectory(prefix='g3-goi-DEMO-') as tmp:
            root = Path(tmp) / 'engines'
            shutil.copytree(GOI, root / 'e_ocr', ignore=shutil.ignore_patterns('__pycache__'))
            kq = nap.doc_engines(root, phien_ban_core='1.0.0')
        self.assertEqual(len(kq), 1)
        self.assertEqual(kq[0].ma, 'e_ocr')
        self._kiem_chua_dat(kq[0])

    def test_discovery_quet_thang_thu_muc_engines_cua_repo(self):
        kq = [r for r in nap.doc_engines(ROOT / 'engines', phien_ban_core='1.0.0') if r.ma == 'e_ocr']
        self.assertEqual(len(kq), 1)
        self._kiem_chua_dat(kq[0])

    def _kiem_chua_dat(self, r):
        # Gói OCR chưa có contract/ (lát khác bổ sung) và parser nguồn còn CHUA_KIEM:
        # discovery nhận ra engine.json nhưng KHÔNG coi là đạt. Khi có contract thì chấp nhận DAT/CHUA_KIEM.
        if (GOI / 'contract').is_dir():
            self.assertIn(r.ket_luan, ('DAT', 'CHUA_KIEM'), r.ly_do)
        else:
            self.assertNotEqual(r.ket_luan, 'DAT')
            self.assertEqual(r.ket_luan, 'KHONG_DAT', r.ly_do)


if __name__ == '__main__':
    unittest.main()
