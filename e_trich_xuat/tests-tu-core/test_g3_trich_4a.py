"""TRICH-4a: TSV/JSON/DOCX DEMO tự tạo, không AI/COM/CSDL/hồ sơ thật.

Dùng mkdtemp, giữ tệp thử; không cleanup/xóa theo quy tắc worker.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from kho_tri_thuc.engines.e_trich_xuat import do_chinh_xac as do
from kho_tri_thuc.engines.e_trich_xuat.vendor.review import danh_muc
from kho_tri_thuc.m4.review_goc.trich_xuat import kiem_tra


class DoChinhXacTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="ktt_demo_trich_4a_"))
        self.codes = [p[0] for p in danh_muc.MAC_DINH]
        self.gold = {ma: f"DEMO đáp án {ma}" for ma in self.codes}
        self.key = self.root / "DAP_AN_DEMO.tsv"
        self.result = self.root / "DEMO-ket-qua.json"
        self.input = self.root / "DEMO.docx"
        with zipfile.ZipFile(self.input, "w") as z:
            z.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>DEMO hợp đồng</w:t></w:r></w:p></w:body></w:document>')
        self.source = self.root / "DEMO-pipeline.py"
        self.source.write_text('# DEMO không chạy pipeline\n', encoding="utf-8")
        self.config = {"temperature": 0, "seed": 7, "num_ctx": 8192,
                       "prompt": "DEMO-v1", "cloud": None}
        self.write_key(self.gold)
        self.write_result(self.gold)

    def write_key(self, values, bom=True):
        text = "Mã\tTên\tVị trí\tĐáp án\tGhi chú\n" + "\n".join(
            f"{ma}\tDEMO tên\tĐiều 1\t{v}\tDEMO không chấm cột 5"
            for ma, v in values.items()) + "\n"
        self.key.write_text(text, encoding="utf-8-sig" if bom else "utf-8")

    def write_result(self, values):
        self.result.write_text(json.dumps({"bang": [
            {"ma": ma, "gia_tri": v, "kiem_tra": "OK", "trich_dan": "DEMO"}
            for ma, v in values.items()]}, ensure_ascii=False), encoding="utf-8")

    def measure(self, **changes):
        args = dict(dap_an=self.key, ket_qua=self.result, tep_nguon=self.input,
                    nguon=self.source, phien_ban_nguon="DEMO-v1", model="DEMO-AI-gia",
                    cau_hinh=self.config)
        args.update(changes)
        return do.do_chinh_xac(**args)

    def test_du_37_cham_cot_4_giu_thu_tu_danh_muc_goc(self):
        self.write_key(dict(reversed(list(self.gold.items()))))
        report = self.measure()
        self.assertEqual(len(report["tham_so"]), 37)
        self.assertEqual([r["ma"] for r in report["tham_so"]], self.codes)
        self.assertEqual(kiem_tra.load_key(self.key), self.gold)
        self.assertEqual(report["tong_hop"], dict(tong=37, da_do=37, chua_do=0,
            dat=37, sai=0, ty_le=1, trang_thai="đã đo"))

    def test_dung_ham_cham_goc_ngay_unicode_so_va_chua_chuoi(self):
        cases = [("ngày 1 tháng 2 năm 2026", "Ngày 01/02/2026", "ĐÚNG"),
                 ("1.000.000 đồng", "1,000,000 đồng", "ĐÚNG"),
                 ("Công ty ký", "Co\u0302ng ty kí", "ĐÚNG"),
                 ("DEMO nội dung dài", "nội dung", "ĐÚNG"),
                 ("DEMO đáp án", "Hoàn toàn khác", "SAI / cần xem")]
        for gold, got, status in cases:
            with self.subTest(gold=gold, got=got):
                self.write_key({self.codes[0]: gold}, bom=False)
                self.write_result({self.codes[0]: got})
                row = self.measure()["tham_so"][0]
                self.assertEqual(row["trang_thai"], status)
                self.assertEqual(row["trang_thai"], kiem_tra.compare(gold, got))

    def test_thieu_phep_do_khong_tinh_0_hay_dung(self):
        report = self.measure(ket_qua=None)
        self.assertEqual(report["tong_hop"], dict(tong=37, da_do=0, chua_do=37,
            dat=None, sai=None, ty_le=None, trang_thai="chưa đo"))
        self.assertIsNone(report["ket_qua"])
        for row in report["tham_so"]:
            self.assertEqual(row["trang_thai"], "chưa đo")
            self.assertIsNone(row["dat"])
            self.assertIsNone(row["ty_le"])
        self.assertEqual(report["ca_sai"], [])

    def test_thieu_dong_none_rong_khong_vao_mau_so(self):
        values = deepcopy(self.gold)
        del values[self.codes[0]]
        values[self.codes[1]] = None
        values[self.codes[2]] = " \t "
        self.write_result(values)
        report = self.measure()
        self.assertEqual(report["tong_hop"]["da_do"], 34)
        self.assertEqual(report["tong_hop"]["dat"], 34)
        self.assertEqual(report["tong_hop"]["chua_do"], 3)
        self.assertEqual(report["tong_hop"]["trang_thai"], "chưa đo đủ")
        self.assertTrue(all(r["dat"] is None for r in report["tham_so"][:3]))

    def test_thieu_dap_an_va_ket_qua_toan_rong(self):
        for gold in ({}, {self.codes[0]: "  "}):
            with self.subTest(gold=gold):
                self.write_key(gold)
                report = self.measure()
                self.assertEqual(report["tong_hop"]["chua_do"], 37)
                self.assertIsNone(report["tong_hop"]["ty_le"])
                self.assertIn("thiếu đáp án", report["tham_so"][0]["ly_do"])
        self.write_key(self.gold)
        self.write_result({})
        self.assertIsNone(self.measure()["tong_hop"]["dat"])

    def test_zero_la_gia_tri_da_do_khong_phai_thieu(self):
        self.write_key({self.codes[0]: "0"})
        for got, passed in (("0", 1), ("9", 0)):
            with self.subTest(got=got):
                self.write_result({self.codes[0]: got})
                report = self.measure()
                self.assertEqual(report["tong_hop"]["da_do"], 1)
                self.assertEqual(report["tong_hop"]["dat"], passed)
                self.assertEqual(report["tong_hop"]["ty_le"], passed)

    def test_khong_quy_dinh_la_ket_qua_tuong_minh(self):
        self.write_key({self.codes[0]: "Không quy định"})
        self.write_result({self.codes[0]: "Không quy định"})
        self.assertEqual(self.measure()["tong_hop"]["dat"], 1)

    def test_ca_sai_tach_biet_chua_do_khong_tin_co_ok(self):
        values = deepcopy(self.gold)
        values[self.codes[0]] = "Hoàn toàn khác"
        values.pop(self.codes[1])
        self.write_result(values)
        report = self.measure()
        self.assertEqual(report["ca_sai"], [self.codes[0]])
        self.assertEqual(report["tong_hop"]["dat"], 35)
        self.assertEqual(report["tong_hop"]["sai"], 1)
        self.assertEqual(report["tong_hop"]["ty_le"], 35 / 36)

    def test_provenance_hash_dung_tep_va_snapshot_cau_hinh(self):
        before = {p: p.read_bytes() for p in (self.key, self.result, self.input, self.source)}
        report = self.measure()
        for key, path in (("dap_an", self.key), ("ket_qua", self.result),
                          ("tep_nguon", self.input), ("nguon", self.source)):
            self.assertEqual(report[key]["duong_dan"], str(path.resolve()))
            self.assertEqual(report[key]["sha256"], hashlib.sha256(before[path]).hexdigest())
            self.assertEqual(path.read_bytes(), before[path])
        self.assertEqual(report["nguon"]["phien_ban"], "DEMO-v1")
        self.assertEqual(report["model"], "DEMO-AI-gia")
        self.assertEqual(report["cau_hinh"], self.config)
        self.config["temperature"] = 1
        self.assertEqual(report["cau_hinh"]["temperature"], 0)
        self.assertEqual(report["cach_cham"]["sha256"], do.NGUON_CHAM_SHA256)
        self.assertEqual(report["cach_cham"]["id"], do.CACH_CHAM)
        self.assertTrue(report["do_luc_utc"].endswith("+00:00"))
        json.dumps(report, ensure_ascii=False, allow_nan=False)

    def test_hash_ghi_nhan_lai_moi_lan_do(self):
        first = self.measure()
        self.write_result({})
        second = self.measure()
        self.assertNotEqual(first["ket_qua"]["sha256"], second["ket_qua"]["sha256"])
        self.assertEqual(first["dap_an"], second["dap_an"])
        self.assertIsNone(second["tong_hop"]["ty_le"])

    def test_thieu_model_phien_ban_hoac_cau_hinh_khong_am_tham_do(self):
        for change in ({"model": ""}, {"phien_ban_nguon": " "}, {"cau_hinh": None},
                       {"cau_hinh": {"temperature": float("nan")}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.measure(**change)

    def test_tsv_trung_ma_la_thieu_cot_va_dong_hong_bi_chan(self):
        for line in (f"{self.codes[0]}\tDEMO\tĐ1\tDEMO\n" * 2,
                     "TT-999\tDEMO\tĐ1\tDEMO\n", f"{self.codes[0]}\tDEMO\n",
                     "ma_sai\tDEMO\tĐ1\tDEMO\n"):
            with self.subTest(line=line), self.assertRaises(ValueError):
                self.key.write_text(line, encoding="utf-8")
                self.measure()

    def test_json_trung_ma_la_sai_kieu_va_hong_bi_chan(self):
        rows = [{"ma": self.codes[0], "gia_tri": "DEMO"}]
        invalid = [{"bang": rows * 2}, {"bang": [{"ma": "TC-99"}]},
                   {"bang": [{"ma": self.codes[0], "gia_tri": 0}]},
                   {"bang": [None]}, {"bang": [{"gia_tri": "DEMO"}]},
                   {"bang": {}}, {}, []]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.result.write_text(json.dumps(value), encoding="utf-8")
                self.measure()
        self.result.write_text("{DEMO", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.measure()

    def test_ten_dap_an_va_tep_thieu_khong_thanh_phep_do(self):
        with self.assertRaisesRegex(ValueError, "DAP_AN_TSV"):
            self.measure(dap_an=self.result)
        with self.assertRaises(FileNotFoundError):
            self.measure(ket_qua=self.root / "DEMO-thieu.json")

    def test_nguon_cham_doi_hash_phai_dung(self):
        with patch.object(do, "NGUON_CHAM_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "NGUON_CHAM_SAI_HASH"):
                self.measure()

    def test_khong_tu_tao_catalog_va_khong_nhan_danh_muc_doi(self):
        with patch.object(danh_muc, "load_params", side_effect=AssertionError("XLSX")), \
                patch.object(danh_muc, "create_catalog", side_effect=AssertionError("ghi XLSX")):
            self.assertEqual(self.measure()["tong_hop"]["tong"], 37)
        with patch.object(do, "DANH_MUC_NGUON_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "DANH_MUC_SAI_HASH"):
                self.measure()
        with patch.object(danh_muc, "MAC_DINH", danh_muc.MAC_DINH[:-1]):
            with self.assertRaisesRegex(ValueError, "DANH_MUC_SAI_37_MA"):
                self.measure()

    def test_thuan_khong_goi_mang_com_hay_trich_xuat(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("mạng")) as network, \
                patch("subprocess.run", side_effect=AssertionError("COM")) as process, \
                patch("kho_tri_thuc.engines.e_trich_xuat.tham_so.TrichXuat.xu_ly",
                      side_effect=AssertionError("trích xuất")) as extraction:
            self.assertEqual(self.measure()["tong_hop"]["dat"], 37)
            network.assert_not_called()
            process.assert_not_called()
            extraction.assert_not_called()


if __name__ == "__main__":
    unittest.main()
