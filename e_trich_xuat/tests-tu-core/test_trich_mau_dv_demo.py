"""LHD-02B: DOCX/TSV DEMO, kiểm tất định; không AI/COM/CSDL/server.

Chỉ sinh tệp DEMO trong mkdtemp và giữ lại, không cleanup/xóa.
Không đọc danh mục/đáp án/hợp đồng ngoài bộ mẫu tự soạn của lát này.
"""

from dataclasses import replace
from io import BytesIO, StringIO
import csv
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import unicodedata
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

from tests.fixtures.trich_mau_dv_demo import (
    MA_DV, MA_TAT_DV, bo_mau_dv_demo, dap_an_tsv, docx_bytes,
)
from kho_tri_thuc.engines.e_trich_xuat import docx
from kho_tri_thuc.m4.review_goc.trich_xuat import cau_truc, kiem_tra


class MauDVDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mau = bo_mau_dv_demo()
        cls.root = Path(tempfile.mkdtemp(prefix="LHD-02B-DEMO-"))
        cls.paths = []
        for mau in cls.mau:
            path = cls.root / (mau.ma + ".docx")
            path.write_bytes(docx_bytes(mau))
            cls.paths.append(path)

    def test_ba_mau_dv_doc_lap_co_nhan_demo(self):
        self.assertEqual(len(self.mau), 3)
        self.assertEqual(len({m.ma for m in self.mau}), 3)
        self.assertEqual(len({m.van_ban for m in self.mau}), 3)
        for mau in self.mau:
            self.assertEqual(mau.loai_hop_dong, "DV")
            self.assertIn("DEMO", mau.ma)
            self.assertIn("DEMO", mau.ten)
            self.assertTrue(mau.van_ban.startswith("DEMO — Dữ liệu giả"))

    def test_dung_30_ma_dv_va_27_ma_bat_theo_tl44(self):
        expected = {f"TC-{i:02d}" for i in range(1, 9)} | {
            "TT-01", "TT-02", "TT-03", "TT-04", "TT-05", "TT-06", "TT-10", "TT-11",
            "TT-13", "TT-20", "TT-21", "TT-22", "TT-23", "TT-24", "TT-72", "TT-80",
            "TT-81", "TT-82", "TT-32", "TT-54", "TT-55", "TT-25",
        }
        self.assertEqual(set(MA_DV), expected)
        self.assertEqual(set(MA_TAT_DV), {"TT-13", "TT-81", "TT-25"})
        for mau in self.mau:
            self.assertEqual(tuple(d.ma for d in mau.dap_an), MA_DV)
            self.assertEqual(len(mau.dap_an), 30)
            self.assertEqual(sum(d.ma not in MA_TAT_DV for d in mau.dap_an), 27)
            for row in mau.dap_an:
                self.assertTrue(row.gia_tri.strip())
                self.assertIn("DEMO", row.ghi_chu)

    def test_docx_doc_duoc_bang_parser_that_khong_word_mang_tien_trinh(self):
        # LHD-E2: vendor G3-GOI-32 chỉ đọc XML, đã bỏ seam _word.
        with patch.object(socket, "socket", side_effect=AssertionError("Cấm mạng")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("Cấm tiến trình")):
            for mau, path in zip(self.mau, self.paths):
                with self.subTest(mau=mau.ma):
                    before = path.read_bytes()
                    info = docx.read_contract(path)
                    self.assertEqual(info["text"], mau.van_ban)
                    self.assertEqual(tuple(info["articles"]), (1, 2, 3, 4, 5, 6))
                    self.assertEqual(info["chunks"], [])
                    self.assertEqual(info["report"]["warnings"], [])
                    self.assertEqual(path.read_bytes(), before)

    def test_moi_dap_an_co_trich_dan_dung_vi_tri_trong_docx(self):
        for mau, path in zip(self.mau, self.paths):
            info = docx.read_contract(path)
            rows = cau_truc.build_structure(info)
            by_position = {cau_truc.vi_tri(r): cau_truc.than(r) for r in rows}
            for row in mau.dap_an:
                with self.subTest(mau=mau.ma, ma=row.ma):
                    self.assertIn(row.trich_dan, info["text"])
                    self.assertIn(row.trich_dan, by_position[row.vi_tri])

    def test_tsv_load_key_goc_doc_dung_cot_va_so_ma(self):
        for mau in self.mau:
            for chi_dang_dung, count in ((True, 27), (False, 30)):
                with self.subTest(mau=mau.ma, dang_dung=chi_dang_dung):
                    text = dap_an_tsv(mau, chi_dang_dung=chi_dang_dung)
                    rows = list(csv.reader(StringIO(text), delimiter="\t"))
                    self.assertEqual(rows[0], ["Mã", "Tên", "Vị trí", "Đáp án", "Ghi chú"])
                    self.assertEqual(len(rows), count + 1)
                    self.assertTrue(all(len(r) == 5 for r in rows))
                    path = self.root / f"{mau.ma}-{count}-DAP_AN_DEMO.tsv"
                    path.write_text(text, encoding="utf-8")
                    key = kiem_tra.load_key(path)
                    expected = {d.ma: d.gia_tri for d in mau.dap_an
                                if not chi_dang_dung or d.ma not in MA_TAT_DV}
                    self.assertEqual(key, expected)
                    self.assertEqual(len(key), count)

    def test_bao_tri_tron_goi_tam_ung_va_thanh_toan_khop(self):
        values = {d.ma: d.gia_tri for d in self.mau[0].dap_an}
        self.assertEqual(values["TT-01"], "Trọn gói")
        self.assertIn("110.000.000 đồng", values["TT-02"])
        self.assertIn("40% (44.000.000 đồng)", values["TT-10"])
        self.assertIn("có xuất hóa đơn", values["TT-10"])
        self.assertIn("60% (66.000.000 đồng)", values["TT-20"])
        self.assertIn("Khấu trừ toàn bộ", values["TT-11"])
        self.assertEqual(44_000_000 + 66_000_000, 110_000_000)

    def test_tam_tinh_khong_suy_thue_thoi_han_hay_so_tien_con_lai(self):
        mau = self.mau[1]
        values = {d.ma: d.gia_tri for d in mau.dap_an}
        self.assertIn("Tạm tính", values["TT-01"])
        self.assertEqual(values["TT-03"], "Không")
        self.assertEqual(values["TT-04"], "Không ghi")
        self.assertIn("không xuất hóa đơn", values["TT-10"])
        self.assertIn("giá trị nghiệm thu thực tế", values["TT-20"])
        self.assertIn("7–10 ngày", values["TT-22"])
        self.assertEqual(values["TT-80"], "Không quy định (để trống)")
        self.assertEqual(values["TT-55"], "Không quy định")
        self.assertEqual(len(mau.canh_bao), 3)
        self.assertIn("cần rà soát thời hạn để trống", dap_an_tsv(mau))

    def test_dinh_ky_khong_tam_ung_co_moc_va_ho_so_thang(self):
        values = {d.ma: d.gia_tri for d in self.mau[2].dap_an}
        self.assertEqual(values["TT-01"], "Đơn giá theo kỳ tháng")
        self.assertEqual(values["TT-10"], "Không tạm ứng")
        self.assertIn("Hàng tháng trả sau: 22.000.000 đồng", values["TT-20"])
        self.assertIn("nghiệm thu tháng: 1 bản gốc", values["TT-23"])
        self.assertEqual(values["TT-80"], "Hàng tháng từ 01/01/2027 đến 31/12/2027, tổng 12 tháng")
        self.assertEqual(12 * 22_000_000, 264_000_000)

    def test_nhan_dien_gia_lap_ngay_chuan_va_chu_viet_utf8(self):
        for mau in self.mau:
            text = mau.van_ban + dap_an_tsv(mau)
            self.assertEqual(text, unicodedata.normalize("NFC", text))
            self.assertNotIn("\ufffd", text)
            self.assertNotIn("?", text)
            self.assertIn("mã số thuế DEMO-MST-", text)
            accounts = re.findall(r"tài khoản (\S+)", text)
            self.assertTrue(accounts)
            self.assertTrue(all(re.fullmatch(r"\*{4}\d{4}[;.]*", a) for a in accounts))
            for date in re.findall(r"\b\d{1,4}/\d{1,2}/\d{1,4}\b", text):
                self.assertRegex(date, r"^\d{2}/\d{2}/\d{4}$")
            for code in ("TC-06", "TC-07", "TC-04", "TC-05"):
                value = next(d.gia_tri for d in mau.dap_an if d.ma == code)
                self.assertIn("DEMO", value)

    def test_docx_du_thanh_phan_xml_escape_va_khong_lien_ket_ngoai(self):
        mau = replace(self.mau[0], cac_doan=("DEMO <kiểm tra> & đối chiếu",))
        raw = docx_bytes(mau)
        with zipfile.ZipFile(BytesIO(raw)) as archive:
            self.assertEqual(set(archive.namelist()), {
                "[Content_Types].xml", "_rels/.rels", "word/document.xml"})
            for name in archive.namelist():
                root = ET.fromstring(archive.read(name))
                self.assertFalse(any(e.get("TargetMode") == "External" for e in root.iter()))
            document = ET.fromstring(archive.read("word/document.xml"))
            self.assertEqual("".join(document.itertext()), mau.van_ban)

    def test_sinh_lap_lai_bat_bien_va_khong_can_doc_tep(self):
        with patch("builtins.open", side_effect=AssertionError("Không đọc tệp")), \
                patch.object(Path, "open", side_effect=AssertionError("Không đọc đường dẫn")), \
                patch.object(socket, "socket", side_effect=AssertionError("Không mạng")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("Không tiến trình")):
            again = bo_mau_dv_demo()
            self.assertEqual(self.mau, again)
            for first, second in zip(self.mau, again):
                self.assertEqual(docx_bytes(first), docx_bytes(second))
                self.assertEqual(dap_an_tsv(first), dap_an_tsv(second))


if __name__ == "__main__":
    unittest.main()
