"""G3-GOI-06: lõi cổng AI nằm trong gói engine, bridge cũ cùng module, Postgres thuộc Core."""
import ast
import sys
import unittest
from pathlib import Path

from kho_tri_thuc.core import nhat_ky_ai_legacy
from kho_tri_thuc.engines.e_hoi_ai.lib import ai_cuc_bo as loi_cuc_bo
from kho_tri_thuc.engines.e_hoi_ai.lib import cong_ai as loi
from kho_tri_thuc.tri_thuc import ai_cuc_bo as cu_cuc_bo
from kho_tri_thuc.tri_thuc import cong_ai as cu

GOC = Path(loi.__file__).resolve().parents[3]
CAM = ("psycopg", "psycopg2", "sqlite3", "asyncpg")


class LoiAITests(unittest.TestCase):
    def test_bridge_la_cung_module_loi(self):
        self.assertIs(cu, loi)
        self.assertIs(cu_cuc_bo, loi_cuc_bo)
        self.assertIs(sys.modules["kho_tri_thuc.tri_thuc.cong_ai"], loi)
        self.assertIs(loi.ai_cuc_bo, loi_cuc_bo)
        self.assertTrue(loi.__file__.replace("\\", "/").endswith("engines/e_hoi_ai/lib/cong_ai.py"))

    def test_api_cu_con_du(self):
        for ten in ("CongAI", "YeuCauAI", "KetQuaAI", "TruongAI", "BanGhiCongAI", "BoGhiBoNho",
                    "BoGhiNhatKy", "BoGhiPostgres", "cong_ai_settings", "loai_viec", "LOAI_VIEC", "MaskV2"):
            self.assertTrue(hasattr(cu, ten), ten)

    def test_postgres_thuoc_core(self):
        self.assertIs(cu.BoGhiPostgres, nhat_ky_ai_legacy.BoGhiPostgres)
        ma = Path(loi.__file__).read_text(encoding="utf-8")
        self.assertNotIn("class BoGhiPostgres", ma)
        self.assertNotIn("nhat_ky.cong_ai_goi (", ma)

    def test_goi_ai_khong_import_csdl_hay_ha_tang(self):
        for tep in (GOC / "engines" / "e_hoi_ai" / "lib").glob("*.py"):
            for n in ast.walk(ast.parse(tep.read_text(encoding="utf-8"))):
                ten = []
                if isinstance(n, ast.Import):
                    ten = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    ten = [n.module or ""]
                    if n.level:
                        self.assertIn(n.module, (None, "sdk_core.ngu_canh"), (tep.name, n.module))
                for t in ten:
                    self.assertFalse(t.split(".")[0] in CAM or ".core" in "." + t or "ha_tang" in t or "m4" in t.split("."),
                                     (tep.name, t))

    def test_patch_globals_toi_cung_module(self):
        from unittest.mock import patch
        with patch.object(cu, "_luc", return_value="X"):
            self.assertEqual(loi._luc(), "X")
        self.assertEqual(loi.cong_ai_settings(None)["cloud_bat"], False)


if __name__ == "__main__":
    unittest.main()
