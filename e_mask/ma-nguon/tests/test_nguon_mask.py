"""MASK-1: kiểm lõi đã chép bằng dữ liệu DEMO trong RAM, không chạy dịch vụ."""

import ast
import hashlib
import importlib
import io
from pathlib import Path
import re
import subprocess
import sys
import unittest
import zipfile


ENGINE = Path(__file__).resolve().parents[1]
NGUON = ENGINE / "nguon"
GOI = "engines.e_mask.nguon.privacy"
TEP = {
    "__init__.py", "core.py", "types.py", "detectors.py", "company_names.py",
    "person_names.py", "variants.py", "docx_revisions.py", "excel.py",
    "excel_values.py", "leftovers.py",
}
QUY_TAC = [{"source": "Doanh nghiệp DEMO", "token": "[CONG_TY_001]",
            "category": "CONG_TY", "enabled": True}]
# Chỉ các ví dụ cố định đã ghi tại NGUON.md §2, giới hạn theo từng tệp.
SO_GIA_DUOC_PHEP = {
    "privacy/core.py": {"001234567890"},
    "privacy/detectors.py": {"1250000000", "1912345678901", "5000000000"},
    "privacy/excel.py": {"1234567890"},
    "privacy/leftovers.py": {"1250000000", "1912345678901"},
}


def module(ten):
    return importlib.import_module(GOI + "." + ten)


def goi_zip(parts):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for ten, noi_dung in parts.items():
            archive.writestr(ten, noi_dung)
    return stream.getvalue()


class NguonTinh(unittest.TestCase):
    def test_chi_co_ma_va_tai_lieu_duoc_phep(self):
        self.assertTrue((NGUON / "privacy").is_dir())
        duoc_phep = {"PHU-THUOC.md"} | {"privacy/" + ten for ten in TEP}
        thuc_te = set()
        for path in NGUON.rglob("*"):
            self.assertFalse(path.is_symlink(), path.name)
            if path.is_file():
                thuc_te.add(path.relative_to(NGUON).as_posix())
            else:
                self.assertEqual(path.relative_to(NGUON).as_posix(), "privacy")
        self.assertEqual(thuc_te, duoc_phep)

    def test_khong_con_ma_hoac_chuoi_nhan_dang_chu(self):
        self.assertEqual({p.name for p in NGUON.rglob("*.py")}, TEP)
        for path in NGUON.rglob("*.py"):
            with self.subTest(tep=path.name):
                text = path.read_text("utf-8")
                self.assertNotRegex(text, re.compile(r"ocr|tesseract|vietocr", re.I))
                self.assertNotIn("\ufffd", text)
                for nut in ast.walk(ast.parse(text)):
                    if isinstance(nut, ast.ImportFrom):
                        self.assertFalse((nut.module or "").startswith("privacy"))

    def test_bam_dich_khop_bang_nguon(self):
        tai_lieu = (ENGINE / "NGUON.md").read_text("utf-8")
        self.assertIn("| Tệp gốc | Tệp đích (từ e_mask) | SHA nguồn | SHA sau chỉnh | Điều chỉnh |",
                      tai_lieu)
        self.assertEqual({p.name for p in NGUON.rglob("*.py")}, TEP)
        for path in NGUON.rglob("*.py"):
            dich = path.relative_to(ENGINE).as_posix()
            bam = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.subTest(tep=dich):
                dong = next((line for line in tai_lieu.splitlines()
                             if "`" + dich + "`" in line), "")
                cot = [c.strip() for c in dong.strip("|").split("|")]
                self.assertEqual(len(cot), 5)
                self.assertRegex(cot[2], r"^`[0-9a-f]{64}`$")
                self.assertEqual(cot[3], "`" + bam + "`")

    def test_khong_con_chuoi_so_ngoai_danh_sach_so_gia(self):
        tai_lieu = (ENGINE / "NGUON.md").read_text("utf-8")
        for tep, cac_so in SO_GIA_DUOC_PHEP.items():
            dong = "| `" + tep + "` | " + ", ".join("`" + so + "`" for so in sorted(cac_so)) + " |"
            self.assertIn(dong, tai_lieu)
        for path in NGUON.rglob("*"):
            if not path.is_file():
                continue
            tep = path.relative_to(NGUON).as_posix()
            duoc_phep = SO_GIA_DUOC_PHEP.get(tep, set())
            for so_dong, dong in enumerate(path.read_text("utf-8").splitlines(), 1):
                ngoai_danh_sach = any(m.group() not in duoc_phep
                                     for m in re.finditer(r"(?<!\d)\d{9,16}(?!\d)", dong))
                # Chỉ báo vị trí; không đưa số chưa được phép vào log khi đỏ.
                self.assertFalse(ngoai_danh_sach,
                                 f"{tep}:{so_dong}: có chuỗi số ngoài danh sách số giả")

    def test_nhap_tat_ca_module_khong_mo_mang_hay_tien_trinh(self):
        # Tiến trình Python sạch: không dùng module đã được các ca DEMO import.
        code = '''
import importlib
from pathlib import Path
import socket
import subprocess
import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])

def cam_ghi(event, args):
    if event == "open":
        mode, flags = args[1], args[2]
        import os
        if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)):
            raise AssertionError("Import không được ghi tệp")
sys.addaudithook(cam_ghi)
with patch.object(socket, "socket", side_effect=AssertionError("Cấm mạng")), \\
        patch.object(subprocess, "Popen", side_effect=AssertionError("Cấm chạy dịch vụ")), \\
        patch.object(Path, "read_text", side_effect=AssertionError("Cấm đọc từ điển khi import")), \\
        patch.object(Path, "read_bytes", side_effect=AssertionError("Cấm đọc dữ liệu khi import")):
    for ten in sys.argv[2:]:
        imported = importlib.import_module(ten)
        assert Path(imported.__file__).parent == Path(sys.argv[1]) / "engines/e_mask/nguon/privacy"
'''
        modules = [GOI if ten == "__init__.py" else GOI + "." + ten[:-3]
                   for ten in sorted(TEP)]
        result = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", "-B", "-c", code,
             str(ENGINE.parents[1]), *modules],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class LoiDemo(unittest.TestCase):
    def test_che_van_ban_giu_tien_ngay(self):
        core = module("core")
        truoc = "Dữ liệu giả — DEMO: Doanh nghiệp DEMO, 1.000.000 VND, 06/11/2026."
        sau, so_cho = core.replace(truoc, core.validate_rules(QUY_TAC))
        self.assertEqual(so_cho, 1)
        self.assertNotIn("Doanh nghiệp DEMO", sau)
        self.assertIn("[CONG_TY_001]", sau)
        self.assertIn("1.000.000 VND, 06/11/2026", sau)
        self.assertFalse(core.numeric_review(truoc, sau, QUY_TAC)["changed"])

    def test_word_tao_tu_van_ban_da_che(self):
        core = module("core")
        from docx import Document
        text, _ = core.replace("Dữ liệu giả — DEMO\nDoanh nghiệp DEMO\t1.000.000 VND\t06/11/2026", QUY_TAC)
        data = core.make_docx(text)
        doc = Document(io.BytesIO(data))
        self.assertIn("Dữ liệu giả", doc.paragraphs[0].text)
        self.assertEqual([c.text for c in doc.tables[0].rows[0].cells],
                         ["[CONG_TY_001]", "1.000.000 VND", "06/11/2026"])
        self.assertEqual(doc.core_properties.author, "")

    def test_word_chap_nhan_lich_su_sua_trong_ram(self):
        revisions = module("docx_revisions")
        xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
               '<w:body><w:p><w:del><w:r><w:delText>Tên cũ DEMO</w:delText></w:r></w:del>'
               '<w:ins><w:r><w:t>Tên mới DEMO</w:t></w:r></w:ins></w:p></w:body></w:document>')
        data, so_dau = revisions.accept_tracked_changes(goi_zip({"word/document.xml": xml}))
        self.assertEqual(so_dau, 2)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            result = archive.read("word/document.xml").decode("utf-8")
        self.assertNotIn("Tên cũ DEMO", result)
        self.assertIn("Tên mới DEMO", result)

    def excel_demo(self, ten_sheet="DEMO"):
        values = module("excel_values")
        plan = {"sheets": [{"name": ten_sheet, "state": "visible", "cells": [
            (1, 1, "s", "Doanh nghiệp DEMO", None),
            (1, 2, "n", "1000000", "grouped"), (1, 3, "n", "46332", "date"),
        ]}, {"name": "Ẩn DEMO", "state": "hidden", "cells": [
            (1, 1, "s", "Doanh nghiệp DEMO", None),
        ]}]}
        return values.build_values_workbook(plan)

    def test_excel_che_ca_sheet_an_giu_so_va_dinh_dang(self):
        excel = module("excel")
        data = self.excel_demo()
        result = excel.ExcelWorkbook(data, "DU-LIEU-GIA-DEMO.xlsx").mask(QUY_TAC)
        self.assertEqual(result.blockers, [])
        self.assertIsNotNone(result.output)
        with zipfile.ZipFile(io.BytesIO(data)) as truoc, \
                zipfile.ZipFile(io.BytesIO(result.output)) as sau:
            self.assertEqual(truoc.read("xl/styles.xml"), sau.read("xl/styles.xml"))
            self.assertIn(b' state="hidden"', sau.read("xl/workbook.xml"))
            self.assertIn(b"<v>1000000</v>", sau.read("xl/worksheets/sheet1.xml"))
            self.assertIn(b"<v>46332</v>", sau.read("xl/worksheets/sheet1.xml"))
            for n in (1, 2):
                text = sau.read(f"xl/worksheets/sheet{n}.xml").decode("utf-8")
                self.assertNotIn("Doanh nghiệp DEMO", text)
                self.assertIn("[CONG_TY_001]", text)

    def test_excel_ten_sheet_co_dinh_danh_chan_xuat_giu_cau_truc(self):
        excel = module("excel")
        values = module("excel_values")
        result = excel.ExcelWorkbook(self.excel_demo("Doanh nghiệp DEMO"), "DEMO.xlsx").mask(QUY_TAC)
        self.assertIsNone(result.output)
        self.assertTrue(result.blockers)
        self.assertTrue(result.ai["renamed_sheets"])
        data = values.build_values_workbook(result.ai_plan)
        self.assertEqual(values.verify_values_workbook(data, QUY_TAC), [])

    def excel_openpyxl_demo(self):
        from openpyxl import Workbook

        workbook = Workbook()
        workbook.active.title = "DEMO"
        workbook.active.append(["Doanh nghiệp DEMO", 1000000, "06/11/2026"])
        stream = io.BytesIO()
        workbook.save(stream)
        workbook.close()
        return stream.getvalue()

    def test_excel_chan_tep_hong(self):
        with self.assertRaisesRegex(module("types").PrivacyError, "Không đọc được XLSX"):
            module("excel").ExcelWorkbook(b"Du lieu gia DEMO", "DEMO.xlsx")

    def test_excel_chan_dinh_dang_chua_ho_tro_voi_workbook_hop_le(self):
        excel = module("excel")
        data = self.excel_openpyxl_demo()
        # Cùng byte hợp lệ, chỉ đổi đuôi: bỏ kiểm đuôi phải làm ba ca này đỏ.
        for ten in ("DEMO.xls", "DEMO.xlsm", "DEMO.xlsb"):
            with self.subTest(tep=ten), self.assertRaisesRegex(
                    module("types").PrivacyError, r"chưa nhận \.xls, \.xlsm hoặc \.xlsb"):
                excel.ExcelWorkbook(data, ten)

    def test_excel_xlsx_hop_le_di_qua(self):
        from openpyxl import load_workbook

        data = self.excel_openpyxl_demo()
        result = module("excel").ExcelWorkbook(data, "DEMO.xlsx").mask(QUY_TAC)
        self.assertEqual(result.blockers, [])
        self.assertIsNotNone(result.output)
        workbook = load_workbook(io.BytesIO(result.output))
        self.assertEqual(list(workbook["DEMO"].values),
                         [("[CONG_TY_001]", 1000000, "06/11/2026")])
        workbook.close()

    def test_thieu_tu_dien_khong_tu_coi_la_kiem_het_dinh_danh(self):
        detectors = module("detectors")
        detectors.surnames.cache_clear()
        with self.assertRaises(FileNotFoundError):
            detectors.surnames()


if __name__ == "__main__":
    unittest.main()
