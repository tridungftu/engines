"""LHD-02: đặc tả bước 1–3 tất định trên năm hợp đồng XD DEMO.

Chỉ dùng bộ đọc/cấu trúc/dò vị trí của đường engine đang chạy. Không chạy
pipeline AI hay PostgreSQL/server. Tệp DEMO ở mkdtemp được giữ lại, không
cleanup/xóa. Có vị trí ứng viên không đồng nghĩa trích đúng hay hết ô vàng.
"""

from contextlib import ExitStack
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

from tests.fixtures import trich_bien_the_xd as mau
from kho_tri_thuc.engines.e_trich_xuat import tich_hop as engine
from kho_tri_thuc.m4.review_goc.trich_xuat import doc_hop_dong, kiem_tra


# Số đo trên danh mục XD ghim 05846a2a…; không đổi kỳ vọng để che lỗi parser.
# Biến thể: (số Điều, số dòng cấu trúc, số đoạn tự chia, mã không có vị trí).
KY_VONG = {
    "V0": (8, 27, 0, ()),
    "V1": (8, 27, 0, ()),
    "V2": (0, 1, 1, ()),
    "V3": (7, 22, 0, ()),
    "V4": (8, 28, 0, ("TT-10",)),
}
CANH_BAO = {
    "V0": [],
    "V1": [],
    "V2": ["Không nhận diện được 'Điều N' → đã tự chia thành 1 đoạn ~3.000 ký tự "
           "(vị trí ghi 'Đoạn k'); nên soát kỹ kết quả"],
    "V3": ["Thiếu Điều số: [5]"],
    "V4": [],
}


class BienTheXDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="LHD-02-DEMO-test-"))
        cls.params = engine.danh_muc_xd()
        cls.files = mau.tao_bo_bien_the(cls.root)
        cls.results = {}
        cls.before = {ma: path.read_bytes() for ma, (path, _) in cls.files.items()}
        # Chặn các seam có thể chạy chương trình ngoài, AI, mạng, Word/PDF.
        with ExitStack() as stack:
            guards = [stack.enter_context(patch.object(obj, name,
                      side_effect=AssertionError("LHD-02 chỉ chạy bước 1–3")))
                      for obj, name in ((socket, "socket"), (subprocess, "Popen"),
                                        (doc_hop_dong, "_word"),
                                        (doc_hop_dong, "chuyen_docx"),
                                        (doc_hop_dong, "read_pdf"), (engine, "AIChung"))]
            for ma, (path, _) in cls.files.items():
                info = engine.read_contract(path)
                rows = engine.build_structure(info)
                loc = engine.locate(rows, cls.params)
                cls.results[ma] = (info, rows, loc)
            for guard in guards:
                guard.assert_not_called()

    def test_bang_so_do_tat_dinh_va_canh_bao_phieu(self):
        for ma, (articles, row_count, chunks, missing) in KY_VONG.items():
            with self.subTest(bien_the=ma):
                info, rows, loc = self.results[ma]
                self.assertEqual(len(info["articles"]), articles)
                self.assertEqual(info["report"]["articles"], articles)
                self.assertEqual(len(rows), row_count)
                self.assertEqual(len(info["chunks"]), chunks)
                self.assertEqual(tuple(x["ma"] for x in loc if not x["row_ids"]), missing)
                self.assertEqual(sum(bool(x["row_ids"]) for x in loc), 37 - len(missing))
                self.assertEqual(info["report"]["warnings"], CANH_BAO[ma])

    def test_docx_doc_du_noi_dung_utf8_khong_doi_tep(self):
        for ma, (path, _) in self.files.items():
            with self.subTest(bien_the=ma):
                info = self.results[ma][0]
                text = info["text"]
                self.assertEqual(text, "\n".join(mau.cac_doan(ma)))
                self.assertEqual(unicodedata.normalize("NFC", text), text)
                self.assertIn("DEMO — DỮ LIỆU GIẢ LẬP", text)
                self.assertIn("ngày 10/02/2026", text)
                self.assertNotIn("?", text)
                self.assertNotIn("\ufffd", text)
                self.assertEqual(path.read_bytes(), self.before[ma])
                self.assertEqual(info["report"]["file"], f"DEMO_XD_{ma}.docx")
                self.assertEqual(info["report"]["words"], info["report"]["raw_words"])
                for field in ("tables", "images", "track_changes_accepted", "numbered_paragraphs"):
                    self.assertEqual(info["report"][field], 0)

    def test_dap_an_du_37_ma_va_trich_dan_co_trong_moi_mau(self):
        codes = [p["ma"] for p in self.params]
        base = {row["ma"]: row["gia_tri"] for row in mau.dap_an()}
        self.assertEqual(len(codes), 37)
        for ma in mau.BIEN_THE:
            with self.subTest(bien_the=ma):
                answers = mau.dap_an(ma)
                self.assertEqual([r["ma"] for r in answers], codes)
                self.assertEqual(len({r["ma"] for r in answers}), 37)
                self.assertEqual({r["ma"]: r["gia_tri"] for r in answers}, base)
                for row in answers:
                    self.assertTrue(row["gia_tri"])
                    self.assertTrue(row["trich_dan"])
                    self.assertIn(row["trich_dan"], self.results[ma][0]["text"])
                _, key = self.files[ma]
                self.assertEqual(kiem_tra.load_key(key), base)
                self.assertEqual(engine.load_key(key), base)
                cells = key.read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(cells), 38)
                self.assertTrue(all(len(x.split("\t")) == 7 for x in cells))

    def test_dinh_danh_lien_he_chi_la_demo(self):
        text = self.results["V0"][0]["text"]
        for prefix in ("Số:", "Gói thầu:", "Dự án:", "Địa điểm:", "BÊN GIAO THẦU",
                       "BÊN NHẬN THẦU", "Mã số thuế:", "Điện thoại:", "Đại diện:", "Tài khoản số:"):
            line = next(x for x in text.splitlines() if x.startswith(prefix))
            self.assertIn("DEMO", line)
        self.assertNotRegex(text, r"\b\d{10,14}\b")

    def test_vi_tri_chi_troi_den_dong_co_that_toi_da_ba_ung_vien(self):
        for ma, (_, rows, loc) in self.results.items():
            with self.subTest(bien_the=ma):
                self.assertEqual([r["id"] for r in rows],
                                 [f"R{i:03d}" for i in range(1, len(rows) + 1)])
                by_id = {r["id"]: r for r in rows}
                self.assertEqual([x["ma"] for x in loc], [p["ma"] for p in self.params])
                for item in loc:
                    self.assertLessEqual(len(item["row_ids"]), 3)
                    self.assertEqual(len(set(item["row_ids"])), len(item["row_ids"]))
                    self.assertEqual(item["vi_tri"],
                                     [engine.vi_tri(by_id[rid]) for rid in item["row_ids"]])

    def test_v1_chi_doi_chu_hoa_va_dau_cham_cuoi_khoan(self):
        paragraphs = mau.cac_doan("V1")
        self.assertEqual(sum(x.startswith("ĐIỀU ") for x in paragraphs), 8)
        self.assertEqual(sum(bool(re.match(r"^\d+\.\d+\. ", x)) for x in paragraphs), 26)
        restored = [re.sub(r"^ĐIỀU (\d+): ", r"Điều \1. ", x) for x in paragraphs]
        restored = [re.sub(r"^(\d+\.\d+)\. ", r"\1 ", x) for x in restored]
        self.assertEqual(tuple(restored), mau.cac_doan("V0"))
        self.assertEqual(self.results["V1"][2], self.results["V0"][2])
        self.assertEqual([(r["dieu"], r["khoan"]) for r in self.results["V1"][1]],
                         [(r["dieu"], r["khoan"]) for r in self.results["V0"][1]])

    def test_v2_la_ma_di_duong_tu_chia_doan_co_canh_bao(self):
        info, rows, loc = self.results["V2"]
        self.assertNotRegex(info["text"], r"(?m)^Điều \d+")
        headings = [x.split(".", 1)[0] for x in mau.cac_doan("V2")
                    if re.match(r"^[IVX]+\. ", x)]
        self.assertEqual(tuple(headings), mau.LA_MA)
        self.assertEqual(info["articles"], {})
        self.assertEqual(info["report"]["chunks"], 1)
        self.assertEqual(info["chunks"], [info["text"]])
        self.assertEqual(rows[0]["doan"], 1)
        self.assertEqual(rows[0]["noi_dung"], info["text"])
        self.assertTrue(all(x["vi_tri"] == ["Đoạn 1"] for x in loc))

    def test_v3_tieu_de_so_bi_gop_vao_dieu_truoc_nhung_khong_mat_chu(self):
        v0 = mau.cac_doan("V0")
        v3 = mau.cac_doan("V3")
        self.assertEqual([(a, b) for a, b in zip(v0, v3) if a != b],
                         [("Điều 5. Quyết toán và bảo hành", "Điều 5. Thanh toán đợt 2")])
        info, rows, loc = self.results["V3"]
        self.assertEqual(tuple(info["articles"]), (1, 2, 3, 4, 6, 7, 8))
        self.assertIn("Điều 5. Thanh toán đợt 2", info["articles"][4]["text"])
        merged = next(r for r in rows if (r["dieu"], r["khoan"]) == ("4", "4.5"))
        for answer in mau.dap_an("V3"):
            if answer["dieu_khoan"].startswith("Điều 5"):
                self.assertIn(answer["trich_dan"], merged["noi_dung"])
        self.assertFalse(any(r["dieu"] == "5" for r in rows))
        # Khóa lại rủi ro đã biết, không coi ứng viên lệch Điều là trích đúng.
        self.assertEqual(next(x for x in loc if x["ma"] == "TT-30")["vi_tri"],
                         ["Điều 4 – Khoản 4.5"])

    def test_v4_giu_noi_dung_chuyen_cac_ben_va_doi_tu_ung_truoc(self):
        v0 = mau.cac_doan("V0")
        v4 = mau.cac_doan("V4")
        self.assertEqual(len(v0), len(v4))
        self.assertCountEqual(v4, [x.replace("Tạm ứng", "Ứng trước").replace("tạm ứng", "ứng trước")
                                  for x in v0])
        info, _, loc = self.results["V4"]
        self.assertNotIn("tạm ứng", info["text"].lower())
        self.assertIn("Ứng trước", info["text"])
        self.assertNotIn("BÊN GIAO THẦU", info["preamble"])
        self.assertNotIn("BÊN NHẬN THẦU", info["preamble"])
        self.assertIn("BÊN GIAO THẦU", info["articles"][1]["text"])
        self.assertIn("BÊN NHẬN THẦU", info["articles"][1]["text"])
        by_code = {x["ma"]: x for x in loc}
        self.assertEqual(by_code["TT-10"]["row_ids"], [])
        self.assertIn("Bên A ứng trước 15%", info["text"])
        for code in ("TC-06", "TC-07"):
            # @mo_dau vẫn cộng điểm dù các Bên đã chuyển đi: ứng viên cần AI soát.
            self.assertEqual(by_code[code]["vi_tri"][:2], ["Phần mở đầu", "Điều 1"])

    def test_docx_va_tsv_sinh_lai_trung_tung_byte(self):
        root = Path(tempfile.mkdtemp(prefix="LHD-02-DEMO-lap-lai-"))
        for ma, pair in mau.tao_bo_bien_the(root).items():
            with self.subTest(bien_the=ma):
                self.assertEqual([p.read_bytes() for p in pair],
                                 [p.read_bytes() for p in self.files[ma]])
                with zipfile.ZipFile(pair[0]) as z:
                    self.assertEqual(set(z.namelist()),
                                     {"[Content_Types].xml", "_rels/.rels", "word/document.xml"})
                    for name in z.namelist():
                        ET.fromstring(z.read(name))

    def test_dap_an_tra_ban_moi_khong_lam_ban_mau_chung(self):
        before = mau.dap_an("V0")
        modified = mau.dap_an("V0")
        modified[0]["gia_tri"] = "DEMO thay đổi cục bộ"
        self.assertEqual(mau.dap_an("V0"), before)
        self.assertIsInstance(mau.cac_doan("V0"), tuple)

    def test_bien_the_la_bi_chan_truoc_khi_ghi_tep(self):
        for ma in ("V5", "../DEMO", "", None):
            with self.subTest(bien_the=ma):
                with self.assertRaisesRegex(ValueError, "Biến thể DEMO"):
                    mau.cac_doan(ma)
                with self.assertRaises(ValueError):
                    mau.dap_an(ma)
                with patch.object(Path, "mkdir") as mkdir:
                    with self.assertRaises(ValueError):
                        mau.tao_hop_dong(self.root / "DEMO-khong-tao", ma)
                    mkdir.assert_not_called()

    def test_khong_ghi_de_docx_hoac_dap_an_co_san(self):
        for ma, pair in self.files.items():
            before = [p.read_bytes() for p in pair]
            with self.subTest(bien_the=ma), self.assertRaises(FileExistsError):
                mau.tao_hop_dong(self.root, ma)
            self.assertEqual([p.read_bytes() for p in pair], before)
        root = Path(tempfile.mkdtemp(prefix="LHD-02-DEMO-tsv-co-san-"))
        key = root / "DAP_AN_DEMO_XD_V0.tsv"
        key.write_text("DEMO đáp án giữ nguyên", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            mau.tao_hop_dong(root, "V0")
        self.assertEqual(key.read_text(encoding="utf-8"), "DEMO đáp án giữ nguyên")
        self.assertFalse((root / "DEMO_XD_V0.docx").exists())


if __name__ == "__main__":
    unittest.main()
