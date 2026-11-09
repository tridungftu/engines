"""LHD-01: chỉ hợp đồng/đáp án DEMO tự tạo, không AI/COM/PG/server.

Giữ tệp DEMO trong thư mục tạm, không cleanup/xóa tệp theo handoff.
"""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from kho_tri_thuc.m4.review_goc.trich_xuat import cau_truc, danh_muc, doc_hop_dong, kiem_tra

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "kiem_nhanh_trich.py"
spec = importlib.util.spec_from_file_location("kiem_nhanh_trich_demo", SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class KiemNhanhTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="LHD-01-DEMO-"))
        self.codes = [p[0] for p in danh_muc.MAC_DINH]
        self.muc3 = next(p[0] for p in danh_muc.MAC_DINH if p[5] == 3)
        self.gold = {code: "DEMO đáp án đầy đủ " + code for code in self.codes}
        self.docx = self.root / "DEMO-HOP-DONG-KHONG-DUOC-IN.docx"
        with zipfile.ZipFile(self.docx, "w") as archive:
            archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                             '<w:p><w:r><w:t>HỢP ĐỒNG DEMO — DỮ LIỆU GIẢ</w:t></w:r></w:p>'
                             '<w:p><w:r><w:t>Điều 1. DEMO Giá hợp đồng</w:t></w:r></w:p>'
                             '<w:p><w:r><w:t>1.1 DEMO Giá hợp đồng 1.000.000 đồng.</w:t></w:r></w:p>'
                             '</w:body></w:document>')
        self.key = self.root / "DAP_AN_DEMO.tsv"
        self.write_key(self.gold)
        self.goc = self.root / "DEMO-goc.json"
        self.engine = self.root / "DEMO-engine.json"
        self.write_result(self.goc, self.gold)
        self.write_result(self.engine, self.gold)
        # Tạo cấu trúc từ DOCX giả bằng hàm thuần gốc, không cần XLSX catalog.
        info = doc_hop_dong.read_contract(str(self.docx))
        rows = cau_truc.build_structure(info)
        params = [{"ma": p[0], "nhom": p[1], "ten": p[2],
                   "tieu_de_kws": ["giá hợp đồng"], "noi_dung_kws": ["DEMO"]}
                  for p in danh_muc.MAC_DINH]
        self.structure = {"file": info["report"]["file"], "phieu_kiem_tra": info["report"],
                          "cau_truc": rows, "vi_tri_tham_so": cau_truc.locate(rows, params)}
        self.sg = self.root / "DEMO-goc_cau_truc.json"
        self.se = self.root / "DEMO-engine_cau_truc.json"
        self.write_json(self.sg, self.structure)
        self.write_json(self.se, self.structure)
        sources = [self.root / ("DEMO-" + name + ".py") for name in
                   ("quy_trinh", "danh_muc", "kiem_tra", "tich_hop")]
        for path in sources:
            path.write_text("# DEMO mã nguồn giả, không thực thi\n", encoding="utf-8")
        self.args = dict(dap_an=self.key, tep_nguon=self.docx, ket_qua_goc=self.goc,
                         ket_qua_engine=self.engine, cau_truc_goc=self.sg, cau_truc_engine=self.se,
                         nguon_goc=sources[:3], nguon_engine=sources[3:],
                         phien_ban_goc="DEMO-goc", phien_ban_engine="DEMO-engine",
                         model="DEMO-Local-gia", cau_hinh={"cloud": False, "ra_lai": True,
                                                           "tham_so_them": []})

    def write_json(self, path, data):
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def write_key(self, values):
        self.key.write_text("Mã\tTên\tVị trí\tĐáp án\tGhi chú\n" + "".join(
            f"{code}\tDEMO tên\tĐiều 1\t{value}\tDEMO\n" for code, value in values.items()),
            encoding="utf-8-sig")

    def write_result(self, path, values):
        self.write_json(path, {"hop_dong": self.docx.name, "bang": [
            {"ma": code, "gia_tri": value, "trich_dan": "DEMO DẪN CHỨNG KHÔNG ĐƯỢC IN"}
            for code, value in values.items()]})

    def measure(self, **changes):
        return tool.kiem_nhanh(**(self.args | changes))

    def cli(self, **changes):
        values = self.args | changes
        argv = []
        for key, value in values.items():
            argv.append("--" + key.replace("_", "-"))
            if isinstance(value, list):
                argv.extend(str(item) for item in value)
            else:
                argv.append(json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else str(value))
        return argv

    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            result = tool.main(argv)
        return result, out.getvalue(), err.getvalue()

    def test_du_37_dung_sha_va_khong_thay_dau_vao(self):
        paths = [self.docx, self.key, self.goc, self.engine, self.sg, self.se,
                 *self.args["nguon_goc"], *self.args["nguon_engine"]]
        before = {p: p.read_bytes() for p in paths}
        report = self.measure()
        self.assertTrue(report["dat"])
        self.assertEqual((report["co_dap_an"], report["khop"], report["khac"], report["chua_so"]), (37, 37, 0, 0))
        self.assertEqual(report["goc"], dict(dung=37, sai=0, chua_do=0))
        self.assertEqual(report["engine"], report["goc"])
        self.assertEqual(report["sha256"]["hop_dong"], hashlib.sha256(before[self.docx]).hexdigest())
        self.assertEqual(report["sha256"]["nguon_goc"], [tool._sha(p) for p in self.args["nguon_goc"]])
        self.assertEqual(before, {p: p.read_bytes() for p in paths})

    def test_dung_lai_ham_cham_va_giong_nhau_ke_ca_phep_chua_chuoi(self):
        values = dict(self.gold)
        values[self.codes[0]] = "DEMO đáp án"
        self.write_result(self.engine, values)
        with patch.object(tool.do, "do_chinh_xac", wraps=tool.do.do_chinh_xac) as scorer, \
                patch.object(kiem_tra, "giong_nhau", wraps=kiem_tra.giong_nhau) as same:
            report = self.measure()
        self.assertEqual(scorer.call_count, 2)
        self.assertEqual(same.call_count, 37)
        self.assertTrue(report["dat"])
        self.assertEqual(report["khop"], 37)

    def test_so_ket_qua_theo_ma_khong_theo_thu_tu_dong(self):
        self.write_result(self.engine, dict(reversed(list(self.gold.items()))))
        self.assertTrue(self.measure()["dat"])

    def test_cau_truc_chi_khac_dinh_dang_json_van_trung(self):
        self.se.write_text(json.dumps(dict(reversed(list(self.structure.items()))), indent=3,
                                      ensure_ascii=True), encoding="utf-8-sig")
        self.assertTrue(self.measure()["cau_truc_khop"])

    def test_cau_truc_phan_biet_so_bool_va_thu_tu_ung_vien(self):
        original = deepcopy(self.structure)
        original["phieu_kiem_tra"]["DEMO_chi_tieu"] = 0
        self.write_json(self.sg, original)
        changed = deepcopy(original)
        changed["phieu_kiem_tra"]["DEMO_chi_tieu"] = False
        self.write_json(self.se, changed)
        self.assertFalse(self.measure()["cau_truc_khop"])
        # Thứ tự ứng viên là một phần của kết quả tất định, không được sort.
        original["vi_tri_tham_so"][0]["vi_tri"] = ["DEMO 1", "DEMO 2"]
        original["vi_tri_tham_so"][0]["row_ids"] = [original["cau_truc"][0]["id"]] * 2
        self.write_json(self.sg, original)
        changed = deepcopy(original)
        changed["vi_tri_tham_so"][0]["vi_tri"].reverse()
        self.write_json(self.se, changed)
        self.assertFalse(self.measure()["cau_truc_khop"])

    def test_bat_lech_tat_ca_phan_tat_dinh_khong_bo_ten_tep(self):
        for key in ("file", "phieu_kiem_tra", "cau_truc", "vi_tri_tham_so"):
            changed = deepcopy(self.structure)
            if key == "file":
                changed[key] = "DEMO-ten-khac.docx"
            elif key == "phieu_kiem_tra":
                changed[key]["warnings"].append("DEMO cảnh báo thêm")
            elif key == "cau_truc":
                changed[key][0]["noi_dung"] += " DEMO nội dung khác"
            else:
                changed[key][0]["vi_tri"][0] = "DEMO vị trí khác"
            self.write_json(self.se, changed)
            with self.subTest(key=key):
                report = self.measure()
                self.assertFalse(report["cau_truc_khop"])
                self.assertFalse(report["dat"])

    def test_cau_truc_thieu_hong_khong_duoc_trung_gia(self):
        cases = [{}, {"file": "DEMO"}, self.structure | {"cau_truc": []},
                 self.structure | {"vi_tri_tham_so": []},
                 self.structure | {"cau_truc": ["DEMO sai"]}]
        bad = deepcopy(self.structure)
        bad["vi_tri_tham_so"][0]["row_ids"] = ["DEMO-khong-co"]
        cases.append(bad)
        for data in cases:
            self.write_json(self.sg, data)
            self.write_json(self.se, data)
            with self.subTest(data_type=type(data).__name__), self.assertRaises(ValueError):
                self.measure()

    def test_y_lon_hon_x_nhung_mat_ma_muc_3_van_khong_dat(self):
        low = [p[0] for p in danh_muc.MAC_DINH if p[5] < 3][:2]
        original, engine = dict(self.gold), dict(self.gold)
        for code in low:
            original[code] = "DEMO sai hoàn toàn"
        engine[self.muc3] = "DEMO sai hoàn toàn"
        self.write_result(self.goc, original)
        self.write_result(self.engine, engine)
        report = self.measure()
        self.assertGreater(report["engine"]["dung"], report["goc"]["dung"])
        self.assertEqual(report["giam_muc_3"], [self.muc3])
        self.assertFalse(report["dat"])
        self.assertEqual(report["lech"][2]["ma"], self.muc3)

    def test_y_nho_hon_x_khong_dat_du_khong_giam_muc_3(self):
        values = dict(self.gold)
        values[self.codes[0]] = "DEMO sai hoàn toàn"
        self.write_result(self.engine, values)
        report = self.measure()
        self.assertFalse(report["dat"])
        self.assertEqual(report["giam_muc_3"], [])

    def test_y_lon_hon_x_va_khong_giam_muc_3_dat_du_co_khac(self):
        values = dict(self.gold)
        values[self.codes[0]] = "DEMO sai hoàn toàn"
        self.write_result(self.goc, values)
        report = self.measure()
        self.assertTrue(report["dat"])
        self.assertEqual(report["khac"], 1)

    def test_thieu_gia_tri_ke_ca_ca_hai_khong_tinh_khop(self):
        for value in (None, "", " \t "):
            values = dict(self.gold)
            values[self.muc3] = value
            self.write_result(self.goc, values)
            self.write_result(self.engine, values)
            with self.subTest(value=value):
                report = self.measure()
                self.assertEqual((report["khop"], report["chua_so"]), (36, 1))
                self.assertFalse(report["dat"])
                self.assertFalse(report["du_phep_do"])
        values = dict(self.gold)
        values.pop(self.muc3)
        self.write_result(self.engine, values)
        self.assertEqual(self.measure()["chua_so"], 1)

    def test_engine_thieu_ma_muc_3_la_giam_khong_phai_dung(self):
        values = dict(self.gold)
        values.pop(self.muc3)
        self.write_result(self.engine, values)
        self.assertEqual(self.measure()["giam_muc_3"], [self.muc3])

    def test_dap_an_thieu_rong_va_khong_co_dap_an(self):
        for gold, count in (({self.codes[0]: self.gold[self.codes[0]]}, 1),
                            ({self.codes[0]: " "}, 0), ({}, 0)):
            self.write_key(gold)
            with self.subTest(count=count):
                report = self.measure()
                self.assertEqual(report["co_dap_an"], count)
                self.assertEqual(report["goc"]["chua_do"], 37 - count)
                self.assertEqual(report["dat"], bool(count))
                if not count:
                    self.assertIsNone(report["goc"]["dung"])

    def test_so_khong_la_da_do(self):
        gold = dict(self.gold)
        gold[self.codes[0]] = "0"
        self.write_key(gold)
        self.write_result(self.goc, gold)
        self.write_result(self.engine, gold)
        self.assertEqual(self.measure()["khop"], 37)
        self.assertTrue(self.measure()["dat"])

    def test_json_ma_la_trung_va_gia_tri_sai_kieu_bi_chan(self):
        for bang in ([{"ma": "DEMO-MA-LA", "gia_tri": "DEMO"}],
                     [{"ma": self.codes[0], "gia_tri": "DEMO"}] * 2,
                     [{"ma": self.codes[0], "gia_tri": 0}]):
            self.write_json(self.engine, {"bang": bang})
            with self.subTest(bang=bang), self.assertRaises(ValueError):
                self.measure()

    def test_json_hong_khoa_trung_nan_bi_chan(self):
        for raw in ('{"bang":', '{"bang": [], "bang": []}', '{"bang": [], "DEMO": NaN}'):
            self.engine.write_text(raw, encoding="utf-8")
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.measure()

    def test_chan_dieu_kien_cloud_ra_lai_hoi_them_doc_lan_do(self):
        for config in ({}, self.args["cau_hinh"] | {"cloud": True},
                       self.args["cau_hinh"] | {"ra_lai": False},
                       self.args["cau_hinh"] | {"tham_so_them": ["DEMO thêm"]}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                self.measure(cau_hinh=config)
        for changes in (dict(tep_nguon="DEMO.doc"), dict(lan_do=3), dict(lan_do=True),
                        dict(nguon_goc=[]), dict(nguon_engine=[])):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.measure(**changes)

    def test_lead_chay_lai_mot_lan_roi_dung_khong_tu_goi_pipeline(self):
        values = dict(self.gold)
        values[self.muc3] = "DEMO sai hoàn toàn"
        self.write_result(self.engine, values)
        first, second = self.measure(), self.measure(lan_do=2)
        self.assertEqual((first["can_chay_lai"], first["dung"]), (True, False))
        self.assertEqual((second["can_chay_lai"], second["dung"]), (False, True))

    def test_khong_goi_ai_com_csdl_server_hay_doc_noi_khac(self):
        # Bộ chấm hiện hành kiểm SHA của đúng hai tệp nguồn vendor này.
        vendor = SCRIPT.parent.parent / "engines/e_trich_xuat/vendor/review"
        allowed = {Path(p).resolve() for p in
                   (self.docx, self.key, self.goc, self.engine, self.sg, self.se,
                    *self.args["nguon_goc"], *self.args["nguon_engine"],
                    tool.do.__file__, danh_muc.__file__, kiem_tra.__file__,
                    vendor / "kiem_tra.py", vendor / "danh_muc.py")}
        read_bytes, read_text = Path.read_bytes, Path.read_text
        def guard(method):
            def read(path, *args, **kwargs):
                self.assertIn(path.resolve(), allowed)
                return method(path, *args, **kwargs)
            return read
        with patch.object(Path, "read_bytes", guard(read_bytes)), \
                patch.object(Path, "read_text", guard(read_text)), \
                patch.object(socket, "socket", side_effect=AssertionError("DEMO cấm mạng")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("DEMO cấm tiến trình")), \
                patch.object(doc_hop_dong, "read_contract", side_effect=AssertionError("DEMO cấm đọc lại DOCX")), \
                patch.object(danh_muc, "load_params", side_effect=AssertionError("DEMO cấm đọc catalog")):
            self.assertTrue(self.measure()["dat"])

    def test_cli_bao_cao_chi_so_khong_lo_noi_dung_duong_dan(self):
        output = self.root / "DEMO-bao-cao.json"
        code, stdout, stderr = self.run_cli(self.cli() + ["--ra", str(output)])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("Tham số có đáp án: 37/37", stdout)
        serialized = stdout + stderr + output.read_text(encoding="utf-8")
        for secret in (str(self.root), self.docx.name, "DEMO đáp án", "DEMO DẪN CHỨNG",
                       self.args["model"], "DEMO-goc", "DEMO-engine"):
            self.assertNotIn(secret, serialized)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), self.measure())
        old = output.read_bytes()
        self.assertEqual(self.run_cli(self.cli() + ["--ra", str(output)])[0], 2)
        self.assertEqual(output.read_bytes(), old)

    def test_cli_lech_va_chua_do_tra_1_khong_hien_so_0_gia(self):
        self.write_key({})
        code, stdout, stderr = self.run_cli(self.cli())
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "")
        self.assertIn("đúng chưa đo; sai chưa đo", stdout)
        self.write_result(self.engine, {self.codes[0]: "DEMO khác"})
        self.assertEqual(self.run_cli(self.cli())[0], 1)

    def test_cli_loi_doc_json_khong_in_ten_tep_noi_dung_hay_traceback(self):
        for changes in (dict(ket_qua_engine=self.root / "DEMO-TEN-NHAY-CAM.json"),
                        dict(cau_hinh="DEMO-LOI-NHAY-CAM")):
            argv = self.cli(**changes)
            code, stdout, stderr = self.run_cli(argv)
            self.assertEqual(code, 2)
            self.assertEqual(stdout, "")
            self.assertNotIn("DEMO", stderr)
            self.assertNotIn("Traceback", stderr)
            self.assertNotIn(str(self.root), stderr)
        for argv in (["--DEMO-TEN-NHAY-CAM"], self.cli(lan_do="DEMO-NHAY-CAM")):
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err), self.assertRaises(SystemExit) as caught:
                tool.main(argv)
            self.assertEqual(caught.exception.code, 2)
            self.assertNotIn("DEMO", err.getvalue())

    def test_diem_vao_script_chay_bang_python_handoff_khong_lo_du_lieu(self):
        # Interpreter chính là Python được lead chỉ định khi chạy unittest.
        completed = subprocess.run([sys.executable, "-X", "utf8", "-B", str(SCRIPT), *self.cli()],
                                   capture_output=True, encoding="utf-8", timeout=30, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Đạt: 1", completed.stdout)
        self.assertNotIn(self.docx.name, completed.stdout + completed.stderr)
        self.assertNotIn("DEMO đáp án", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
