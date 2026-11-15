"""Kiểm công cụ bằng giả lập, không kết nối mạng."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("thu_local", Path(__file__).with_name("thu_local_ai_that.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class KiemCongCu(unittest.TestCase):
    def test_chay_kho_khong_goi_mang(self):
        with patch.object(mod, "thuc_hien", side_effect=AssertionError("gọi mạng")):
            self.assertEqual(mod.main([]), 0)
            self.assertEqual(mod.main(["--url", "http://127.0.0.1:1"]), 0)
            with self.assertRaises(SystemExit):
                mod.main(["--that"])

    def test_ket_qua_va_local_tat(self):
        from e_hoi_ai.chon_model import DanhSachModel, ModelLocal
        danh_sach = DanhSachModel("demo", (), (ModelLocal("model-demo", True), ModelLocal("model-tat", False)))
        with patch.object(mod.chon_model.BoPhatHienModel, "phat_hien", return_value=danh_sach), \
             patch.object(mod.NhaCungCapLocal, "hoi", return_value='{"truong":[{"gia_tri":"1.000.000 VND","trich_dan":"Số tiền thanh toán là 1.000.000 VND."},{"gia_tri":"30/10/2026","trich_dan":"Ngày thanh toán là 30/10/2026."}]}'):
            bao_cao = mod.thuc_hien("http://127.0.0.1:1")
        self.assertTrue(bao_cao["ket_qua"][0]["dung"])
        self.assertTrue(bao_cao["ket_qua"][0]["co_trich_dan"])
        self.assertFalse(bao_cao["ket_qua"][1]["dung"])
        self.assertTrue(bao_cao["local_tat_gia_lap"]["khong_san_sang"])
        self.assertEqual(bao_cao["so_luot_cloud"], 0)

    def test_khong_phat_hien(self):
        with patch.object(mod.chon_model.BoPhatHienModel, "phat_hien", return_value=None):
            report = mod.thuc_hien("http://127.0.0.1:1")
        self.assertEqual(report["phat_hien"], "khong_san_sang")
        self.assertEqual(report["ket_qua"], [])


    def test_ghi_json_trong_thu_muc_chay(self):
        report = {"ket_qua": [], "local_tat_gia_lap": {"khong_san_sang": True}, "so_luot_cloud": 0}
        cu = os.getcwd()
        with tempfile.TemporaryDirectory() as thu_muc:
            try:
                os.chdir(thu_muc)
                with patch.object(mod, "thuc_hien", return_value=report):
                    self.assertEqual(mod.main(["--that", "--url", "http://127.0.0.1:1"]), 1)
                tep = list(Path.cwd().glob("ket-qua-local-demo-*.json"))
                self.assertEqual(len(tep), 1)
                self.assertEqual(json.loads(tep[0].read_text(encoding="utf-8")), report)
            finally:
                os.chdir(cu)


if __name__ == "__main__":
    unittest.main()
