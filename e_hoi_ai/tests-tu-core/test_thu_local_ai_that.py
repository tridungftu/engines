"""Lát 8: thuần/mock; không mở socket, không đọc cấu hình thật, không xóa tệp."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, mock_open, patch


GOC = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("thu_local_ai_that", GOC / "tools" / "thu_local_ai_that.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

CFG = {"enabled": True, "url": "http://192.168.10.20:1234/v1/chat/completions",
       "model": "gpt-oss-20b", "timeout_seconds": 2}
IDS = ("openai/gpt-oss-20b", "qwen/qwen3:8b", "google/gemma-3-12b")


def discovery():
    return {"model_phat_hien": [{"id_model": model, "trang_thai": "san_sang",
            "loai_phan_mem": "lm_studio"} for model in IDS], "ma_loi": ""}


def tra_loi(**changes):
    data = {"truong": [{"ten": ten, "gia_tri": value, "trich_dan": tool.VAN_BAN_DEMO}
                       for ten, value in tool.GIA_TRI_DEMO.items()], "do_tin_cay": 0.95}
    data.update(changes)
    return json.dumps(data, ensure_ascii=False)


class ThuLocalTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch("socket.socket", side_effect=AssertionError("Cấm mạng thật")))
        self.enterContext(patch.object(tool.ca, "doc_khoa_mask", side_effect=AssertionError("Cấm đọc khóa")))
        self.duong_cloud = self.enterContext(patch.object(tool.ca.CongAI, "_cloud",
            side_effect=AssertionError("Cấm đường Cloud")))
        self.enterContext(patch.dict(tool.ai._CONNECTION_FAILURES, {}, clear=True))
        self.detect = self.enterContext(patch.object(tool.ai, "discover_local_models", return_value=discovery()))
        self.local = self.enterContext(patch.object(tool.ai, "ask_local", return_value=tra_loi()))

    def tearDown(self):
        self.duong_cloud.assert_not_called()

    def cli(self, args, raw=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        opening = mock_open(read_data=json.dumps(raw or {"settings": {"local_ai": CFG}}, ensure_ascii=False))
        with patch.object(Path, "open", opening), patch.object(Path, "exists", return_value=False), \
                patch.object(Path, "is_dir", return_value=True), redirect_stdout(stdout), redirect_stderr(stderr):
            code = tool.main(args)
        return code, stdout.getvalue() + stderr.getvalue(), opening

    def test_chay_kho_mac_dinh_khong_discovery_khong_goi_khong_ghi(self):
        for flags in ([], ["--chay-kho"], ["--chay-kho", "--dia-chi-sai"]):
            with self.subTest(flags=flags):
                code, output, opening = self.cli(["--cau-hinh", "local-demo.json", *flags])
                self.assertEqual(code, 0)
                self.assertIn("Chạy khô", output)
                self.assertIn("0 lượt Cloud", output)
                self.assertNotIn("192.168.10.20", output)
                self.assertEqual(len(opening.call_args_list), 1)
        self.detect.assert_not_called()
        self.local.assert_not_called()

    def test_ba_model_qua_cong_ai_dung_cau_hoi_demo_co_dinh(self):
        original = deepcopy(CFG)
        report = tool.thuc_hien(CFG)
        self.assertEqual(CFG, original)
        self.assertEqual([row["model"] for row in report["ket_qua"]], list(tool.MODELS))
        self.assertTrue(all(row["dat"] and row["con"] and row["san_sang"] for row in report["ket_qua"]))
        self.assertEqual([call.args[0]["model"] for call in self.local.call_args_list], list(IDS))
        self.assertTrue(all(tool.VAN_BAN_DEMO in call.args[1] for call in self.local.call_args_list))
        self.assertEqual(report["so_luot_cloud"], 0)
        self.assertRegex(report["ngay_thu"], r"^\d{2}/\d{2}/\d{4}$")
        self.assertTrue(all(type(row["thoi_gian_ms"]) is int and row["thoi_gian_ms"] >= 0
                            for row in report["ket_qua"]))

    def test_model_mat_va_lm_studio_chua_san_sang_khong_gui(self):
        result = discovery()
        result["model_phat_hien"].pop()
        result["model_phat_hien"][1]["trang_thai"] = "da_tai"
        self.detect.return_value = result
        rows = tool.thuc_hien(CFG)["ket_qua"]
        self.assertTrue(rows[0]["dat"])
        self.assertTrue(rows[1]["con"])
        self.assertFalse(rows[1]["san_sang"])
        self.assertEqual(rows[1]["ma_loi_local"], "LOCAL_MODEL_CHUA_SAN_SANG")
        self.assertFalse(rows[2]["con"])
        self.assertEqual(rows[2]["ma_loi_local"], "LOCAL_KHONG_CO_MODEL")
        self.local.assert_called_once()

    def test_ollama_da_tai_va_openai_chua_ro_chi_san_sang_sau_goi(self):
        for software, state in (("ollama", "da_tai"), ("openai_compatible", "chua_ro")):
            result = discovery()
            for model in result["model_phat_hien"]:
                model.update(loai_phan_mem=software, trang_thai=state)
            self.detect.return_value = result
            with self.subTest(software=software):
                self.assertTrue(all(row["dat"] and row["san_sang"]
                                    for row in tool.thuc_hien(CFG)["ket_qua"]))

    def test_discovery_mat_ket_noi_khong_gui_cau_hoi(self):
        self.detect.return_value = {"model_phat_hien": [], "ma_loi": "LOCAL_AI_KET_NOI_LOI"}
        report = tool.thuc_hien(CFG)
        self.assertTrue(all(row["ma_loi_local"] == "LOCAL_AI_KET_NOI_LOI" and not row["dat"]
                            for row in report["ket_qua"]))
        self.local.assert_not_called()

    def test_mat_ket_noi_sau_discovery_khong_cloud(self):
        self.local.side_effect = tool.ai.LocalAIUnavailable("DEMO 192.168.10.20 khoa-DEMO")
        report = tool.thuc_hien(CFG)
        self.assertTrue(all(row["ma_loi_local"] == "LOCAL_KHONG_CHAY" and not row["san_sang"]
                            for row in report["ket_qua"]))
        self.assertNotIn("192.168.10.20", json.dumps(report))
        self.assertNotIn("khoa-DEMO", json.dumps(report))
        self.assertEqual(report["so_luot_cloud"], 0)

    def test_ca_dia_chi_sai_van_qua_cong_ai(self):
        self.detect.side_effect = [discovery(), {"model_phat_hien": [], "ma_loi": "LOCAL_AI_KET_NOI_LOI"}]
        self.local.side_effect = [tra_loi(), tra_loi(), tra_loi(), tool.ai.LocalAIUnavailable("DEMO")]
        report = tool.thuc_hien(CFG, tool.DIA_CHI_SAI)
        self.assertTrue(report["mat_ket_noi"]["dat"])
        self.assertEqual(report["mat_ket_noi"]["ma_loi_local"], "LOCAL_KHONG_CHAY")
        self.assertEqual(self.local.call_args.args[0]["url"], tool.DIA_CHI_SAI)
        self.assertEqual(self.local.call_args.args[0]["timeout_seconds"], 1)
        self.assertEqual(report["so_luot_cloud"], 0)

    def test_dia_chi_sai_van_tra_loi_thi_ca_khong_dat(self):
        self.assertFalse(tool.thuc_hien(CFG, tool.DIA_CHI_SAI)["mat_ket_noi"]["dat"])

    def test_mock_cong_ai_khoa_cloud_env_rong_va_khong_cham_mask(self):
        fields = {ten: tool.ca.TruongAI(ten, value, tool.VAN_BAN_DEMO, "LOCAL")
                  for ten, value in tool.GIA_TRI_DEMO.items()}
        cong = Mock(cai_dat={"cloud_bat": True})
        cong.goi.return_value = tool.ca.KetQuaAI("BOC_TACH_HOP_DONG", "VANG", fields, "LOCAL", "DEMO")
        with patch.object(tool.ca, "CongAI", return_value=cong) as factory:
            self.assertTrue(all(row["dat"] for row in tool.thuc_hien(CFG)["ket_qua"]))
        self.assertEqual(factory.call_count, 3)
        self.assertIs(cong.cai_dat["cloud_bat"], False)
        for call in factory.call_args_list:
            self.assertIs(call.args[0]["cong_ai"]["cloud_bat"], False)
            self.assertEqual(call.kwargs["moi_truong"], {})
            self.assertFalse(call.kwargs["kiem_xac_suat"](None))
            with self.assertRaises(RuntimeError):
                call.kwargs["nha_cung_cap"].tra_loi()
            self.assertFalse(call.kwargs["mask"].co_khoa())

    def test_sai_gia_tri_trich_dan_thieu_truong_json_hong_tin_cay_thap(self):
        base = json.loads(tra_loi())
        cases = ["không phải JSON", tra_loi(do_tin_cay=0.1), tra_loi(truong=[]),
                 tra_loi(truong=base["truong"][:2])]
        for key, value in (("gia_tri", "999 VND"), ("trich_dan", "ngoài tài liệu DEMO")):
            changed = deepcopy(base)
            changed["truong"][0][key] = value
            cases.append(json.dumps(changed, ensure_ascii=False))
        for answer in cases:
            with self.subTest(answer=answer):
                self.local.return_value = answer
                self.assertTrue(all(not row["dat"] for row in tool.thuc_hien(CFG)["ket_qua"]))

    def test_preview_loc_chi_truong_demo_khong_dia_chi_khoa_noi_dung_tu_do(self):
        self.local.return_value = tra_loi(ghi_chu="http://192.168.10.20 khoa-DEMO " + "x" * 500)
        text = json.dumps(tool.thuc_hien(CFG), ensure_ascii=False)
        self.assertNotIn("192.168.10.20", text)
        self.assertNotIn("khoa-DEMO", text)
        for row in tool.thuc_hien(CFG)["ket_qua"]:
            self.assertLessEqual(len(row["trich_doan"]), 200)
            self.assertIn("DEMO-001", row["trich_doan"])
            self.assertNotIn("ghi_chu", row["trich_doan"])

    def test_cli_ghi_json_unicode_khong_in_dia_chi_khoa_ke_ca_cloud_bat(self):
        code, output, opening = self.cli(["--thuc-hien", "--cau-hinh", "local-demo.json", "--ra", "ket-qua-demo.json"],
            {"local_ai": CFG, "cong_ai": {"cloud_bat": True, "mask_tep_khoa": "CAM-DOC", "khoa": "khoa-DEMO"}})
        self.assertEqual(code, 0)
        self.assertIn("Số lượt Cloud: 0", output)
        self.assertNotIn("192.168.10.20", output)
        self.assertNotIn("khoa-DEMO", output)
        self.assertEqual(opening.call_args.args[0], "x")
        content = "".join(call.args[0] for call in opening().write.call_args_list)
        report = json.loads(content)
        self.assertEqual(len(report["ket_qua"]), 3)
        self.assertIn("Số hợp đồng", content)

    def test_cli_thieu_cau_hinh_thieu_ra_va_loi_khong_phan_chieu_tham_so(self):
        for args in ([], ["--cau-hinh", "local-demo.json", "--thuc-hien"],
                     ["--khoa=192.168.10.20-khoa-DEMO"],
                     ["--cau-hinh", "local-demo.json", "--chay-kho", "--thuc-hien"]):
            with self.subTest(args=args):
                code, output, _ = self.cli(args)
                self.assertEqual(code, 2)
                self.assertNotIn("192.168.10.20", output)
                self.assertNotIn("khoa-DEMO", output)
        self.detect.assert_not_called()

    def test_cli_local_loi_van_luu_bao_cao_va_tra_ma_chua_dat(self):
        self.local.side_effect = tool.ai.LocalAIUnavailable("DEMO 192.168.10.20 khoa-DEMO")
        code, output, opening = self.cli(["--thuc-hien", "--cau-hinh", "local-demo.json",
                                          "--ra", "ket-qua-demo.json"])
        self.assertEqual(code, 1)
        content = "".join(call.args[0] for call in opening().write.call_args_list)
        report = json.loads(content)
        self.assertTrue(all(row["ma_loi_local"] == "LOCAL_KHONG_CHAY" for row in report["ket_qua"]))
        self.assertIn("thử lại", output)
        self.assertNotIn("192.168.10.20", output + content)
        self.assertNotIn("khoa-DEMO", output + content)

    def test_chi_nhan_json_demo_khong_doc_duong_cam(self):
        for name in (".env", "cau_hinh.that.toml", "var/plhn-that/demo.json", "var/web-that/demo.json",
                     "D:/DU-LIEU-KE-TOAN/bi-mat/demo.json", ".git/demo.json"):
            with self.subTest(name=name):
                code, _, opening = self.cli(["--cau-hinh", name])
                self.assertEqual(code, 2)
                opening.assert_not_called()

    def test_cau_hinh_bat_buoc_local_bat_dung_kieu_va_dia_chi_an_toan(self):
        for value in ({}, {"local_ai": {}}, {"local_ai": {**CFG, "enabled": "true"}},
                      {"local_ai": {**CFG, "model": {}}},
                      {"local_ai": {**CFG, "remote_host": "DEMO"}},
                      {"local_ai": {**CFG, "url": "https://192.168.10.20:1234/v1/chat/completions"}},
                      {"local_ai": {**CFG, "url": "http://8.8.8.8:1234/v1/chat/completions"}},
                      {"local_ai": {**CFG, "url": "http://ai.example:1234/v1/chat/completions"}}):
            with self.subTest(value=value):
                with patch.object(Path, "open", mock_open(read_data=json.dumps(value))):
                    with self.assertRaises(tool.LoiChuanBi):
                        tool.doc_cau_hinh("local-demo.json")
        self.detect.assert_not_called()

    def test_dung_ham_kiem_dia_chi_chung_ca_dia_chi_sai(self):
        with patch.object(tool.ai, "local_ai_settings", wraps=tool.ai.local_ai_settings) as check:
            code, _, _ = self.cli(["--cau-hinh", "local-demo.json", "--dia-chi-sai",
                                  "http://8.8.8.8:1234/v1/chat/completions"])
            self.assertEqual(code, 2)
            self.assertEqual(check.call_count, 2)
        self.detect.assert_not_called()

    def test_nhieu_bien_the_khong_chon_tuy_tien_va_khong_nham_80b(self):
        result = discovery()
        result["model_phat_hien"].extend([
            {"id_model": "other/qwen3-8b-Q4", "trang_thai": "san_sang"},
            {"id_model": "qwen3-80b", "trang_thai": "san_sang"}])
        self.detect.return_value = result
        row = tool.thuc_hien(CFG)["ket_qua"][1]
        self.assertEqual(row["ma_loi_local"], "LOCAL_NHIEU_MODEL_PHU_HOP")
        self.assertTrue(row["con"])
        self.assertFalse(row["dat"])
        picked, code = tool._chon_model(result["model_phat_hien"], "Qwen3 8B", "qwen/qwen3:8b")
        self.assertEqual(picked["id_model"], "qwen/qwen3:8b")
        self.assertEqual(code, "")

    def test_khong_ghi_de_tep_khong_hop_le_va_dia_chi_sai_trung_dia_chi_chinh(self):
        for flags in (["--ra", "var/web-that/demo.json"], ["--dia-chi-sai", CFG["url"]]):
            code, _, _ = self.cli(["--cau-hinh", "local-demo.json", "--thuc-hien", *flags])
            self.assertEqual(code, 2)
        with patch.object(tool, "doc_cau_hinh", return_value=CFG), \
                patch.object(Path, "exists", return_value=True), redirect_stderr(io.StringIO()):
            self.assertEqual(tool.main(["--cau-hinh", "local-demo.json", "--thuc-hien",
                                        "--ra", "ket-qua-demo.json"]), 2)
        self.detect.assert_not_called()

    def test_ma_loi_discovery_la_khong_xuat_noi_dung_tho(self):
        self.detect.return_value = {"model_phat_hien": [], "ma_loi": "192.168.10.20 khoa-DEMO"}
        result = json.dumps(tool.thuc_hien(CFG))
        self.assertNotIn("192.168.10.20", result)
        self.assertNotIn("khoa-DEMO", result)

    def test_cmd_chi_ascii_khong_chcp_mac_dinh_chay_kho(self):
        raw = (GOC / "MO-THU-LOCAL-AI.cmd").read_bytes()
        text = raw.decode("ascii")
        self.assertNotIn("chcp", text.casefold())
        self.assertIn("--chay-kho", text)
        self.assertIn("-X utf8 -B", text)
        self.assertNotIn("--thuc-hien", text)
        self.assertIn("%~dp0tools\\thu_local_ai_that.py", text)


if __name__ == "__main__":
    unittest.main()
