"""LHD-E1: danh mục ghim và dữ liệu giả trong RAM, không PG/AI/dữ liệu thật."""

import ast
from copy import deepcopy
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile

from kho_tri_thuc.sdk_core import danh_muc_tham_so as dm
from kho_tri_thuc.sdk_core import xlsx_mini


ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "src/kho_tri_thuc/sdk_core"
CATALOG = ROOT / "src/kho_tri_thuc/m4/review_goc/trich_xuat/DANH_MUC_THAM_SO.xlsx"
CATALOG_SHA256 = "05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd"
# QD-TAM-20261106-05: chép nguyên byte, không thêm docstring đổi SHA nguồn.
XLSX_MINI_SHA256 = "45d7845f0ba97487cb7948a5b55af5bab5446296049d88a17a6761b895f24e8b"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def dong(ma="DV-01", **doi):
    row = [ma, "Dịch vụ", "Nội dung dịch vụ (DEMO)", "@mo_dau", "dịch vụ; công việc",
           "Có", 2, "dịch vụ", "", "Không"]
    for key, value in doi.items():
        row[dm.KHOA.index(key)] = value
    return row


def excel(rows=None, **sheets):
    out = io.BytesIO()
    xlsx_mini.write_xlsx(out, {"Danh_muc": {"rows": rows if rows is not None else [dm.HEADER, dong()]}, **sheets})
    return out.getvalue()


def sua_zip(raw, ten, sua):
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as z, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dest:
        for item in z.infolist():
            data = z.read(item.filename)
            dest.writestr(item.filename, sua(data) if item.filename == ten else data)
    return out.getvalue()


def sua_sheet(raw, sua):
    def edit(data):
        root = ET.fromstring(data)
        sua(root)
        return ET.tostring(root, encoding="utf-8")
    return sua_zip(raw, "xl/worksheets/sheet1.xml", edit)


class DanhMucTests(unittest.TestCase):
    def bat_loi(self, ham, *args, **kwargs):
        with self.assertRaises(dm.LoiDanhMuc) as bat:
            ham(*args, **kwargs)
        return bat.exception.loi

    def test_xlsx_mini_nguyen_byte_vendor_va_sha_ghim(self):
        source = (ROOT / "engines/e_trich_xuat/vendor/review/xlsx_mini.py").read_bytes()
        copied = (SDK / "xlsx_mini.py").read_bytes()
        self.assertEqual(source, copied)
        self.assertEqual(hashlib.sha256(copied).hexdigest(), XLSX_MINI_SHA256)

    def test_xd_dung_sha_va_bang_dung_danh_muc_xd(self):
        from kho_tri_thuc.engines.e_trich_xuat.tham_so import danh_muc_xd
        raw = CATALOG.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), CATALOG_SHA256)
        result = dm.doc_danh_muc(raw)
        self.assertEqual(result.ma_bam, CATALOG_SHA256)
        self.assertEqual(result.tham_so, danh_muc_xd())
        self.assertEqual(len(result.tham_so), 37)
        rows = xlsx_mini.read_xlsx(io.BytesIO(raw))
        self.assertEqual(dm.kiem_tra_danh_muc(rows).tham_so, danh_muc_xd())

    def test_header_chap_nhan_khoa_khoa_khong_doi_nguon(self):
        head = [s.replace("khoá", "khóa") for s in dm.HEADER]
        rows = [head, dong()]
        saved = deepcopy(rows)
        self.assertEqual(dm.kiem_tra_danh_muc(rows).tham_so[0]["ma"], "DV-01")
        self.assertEqual(rows, saved)

    def test_header_thieu_sai_thu_tu_va_thua(self):
        for head, code, cot in ((dm.HEADER[:-1], "THIEU_COT", dm.HEADER[-1]),
                                 (dm.HEADER[:7] + dm.HEADER[8:], "THIEU_COT", dm.HEADER[7]),
                                 ([dm.HEADER[1], dm.HEADER[0]] + dm.HEADER[2:], "SAI_COT", dm.HEADER[0]),
                                 (dm.HEADER + ["Thừa"], "THUA_COT", None)):
            with self.subTest(code=code):
                loi = self.bat_loi(dm.kiem_tra_danh_muc, [head, dong()])
                self.assertIn((code, 1, cot), [(v.ma, v.dong, v.cot) for v in loi])

    def test_cot_van_ban_khong_ep_ngam_so_bool_hoac_danh_sach(self):
        for key, value in (("nhom", 123), ("mo_ta", True), ("tk", ["abc"])):
            with self.subTest(key=key):
                loi = self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(**{key: value})])
                self.assertIn(("SAI_KIEU_O", 2, dm.HEADER[dm.KHOA.index(key)]),
                              [(v.ma, v.dong, v.cot) for v in loi])

    def test_loi_nhieu_dong_khong_bo_dong_thieu_ma(self):
        rows = [dm.HEADER, dong(), [], dong(), dong("", mo_ta="", nhom="")]
        loi = self.bat_loi(dm.kiem_tra_danh_muc, rows)
        self.assertEqual({(v.ma, v.dong) for v in loi},
                         {("TRUNG_MA", 4), ("THIEU_MA", 5), ("THIEU_MO_TA", 5), ("THIEU_NHOM", 5)})
        self.assertIn("trùng dòng 2", str(loi[0].thong_bao))

    def test_ma_chi_dung_dinh_dang_khong_danh_cho_hoi_them(self):
        for ma in ("Y-01", "dv-01", "DV-1", "DV-0000", "ABCD-01", "DV-０１", "DV-01\nx"):
            with self.subTest(ma=ma):
                loi = self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(ma)])
                self.assertIn("SAI_MA", [v.ma for v in loi])
        self.assertEqual(dm.kiem_tra_danh_muc([dm.HEADER, dong("ABC-123")]).cac_dong[0]["ma"], "ABC-123")

    def test_mo_ta_nhom_bat_buoc_va_gioi_han(self):
        for doi, code in (({"nhom": " "}, "THIEU_NHOM"), ({"mo_ta": None}, "THIEU_MO_TA"),
                           ({"mo_ta": "ấ" * 1001}, "MO_TA_QUA_DAI")):
            with self.subTest(code=code):
                self.assertIn(code, [v.ma for v in self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(**doi)])])
        self.assertEqual(len(dm.kiem_tra_danh_muc([dm.HEADER, dong(mo_ta="ấ" * 1000)]).cac_dong[0]["mo_ta"]), 1000)

    def test_bool_chi_co_khong_khong_ep_kieu(self):
        for key in ("dung", "luon_cloud"):
            for value in ("x", "co", "khong", "có", "1", 1, 0, True, False, None, ""):
                with self.subTest(key=key, value=value):
                    loi = self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(**{key: value})])
                    self.assertIn(("SAI_CO_KHONG", 2, dm.HEADER[dm.KHOA.index(key)]),
                                  [(v.ma, v.dong, v.cot) for v in loi])

    def test_muc_la_so_nguyen_0_den_3_khong_cat_hoac_mac_dinh(self):
        for value in (None, "", -1, 4, "2.5", "2.0", "2e0", 2.0, True, False, "nan"):
            with self.subTest(value=value):
                loi = self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(muc=value)])
                self.assertIn("SAI_MUC", [v.ma for v in loi])
        for value in (0, 1, 2, 3, " 0 ", "3"):
            self.assertEqual(dm.kiem_tra_danh_muc([dm.HEADER, dong(muc=value)]).cac_dong[0]["muc"], int(value))

    def test_tu_khoa_gioi_han_vi_tri_at_va_chuyen_pipeline(self):
        for key, value, code in (("tk", "a" * 61, "TU_KHOA_QUA_DAI"),
                                  ("tk", "@dau", "SAI_TU_KHOA"), ("bk", "@mo_dau", "SAI_TU_KHOA"),
                                  ("bat_buoc", "abc@xyz", "SAI_TU_KHOA"), ("loai_tru", "@mo_dau", "SAI_TU_KHOA")):
            with self.subTest(key=key):
                self.assertIn(code, [v.ma for v in self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(**{key: value})])])
        result = dm.kiem_tra_danh_muc([dm.HEADER, dong(tk="@mo_dau; TIÊU ĐỀ", bk="NỘI DUNG; a\nb")])
        self.assertEqual(result.tham_so[0]["tieu_de_kws"], ["@mo_dau", "tiêu đề"])
        self.assertEqual(result.tham_so[0]["noi_dung_kws"], ["nội dung", "a", "b"])

    def test_it_nhat_mot_dang_dung_giu_dong_tat_va_tom_tat(self):
        self.assertIn("KHONG_CO_THAM_SO_DUNG", [v.ma for v in self.bat_loi(dm.kiem_tra_danh_muc, [dm.HEADER, dong(dung="Không")])])
        result = dm.kiem_tra_danh_muc([dm.HEADER, dong(), dong("DV-02", dung="Không", muc=3, luon_cloud="Có")])
        self.assertEqual(len(result.cac_dong), 2)
        self.assertEqual(len(result.tham_so), 1)
        self.assertEqual(result.tom_tat, {"so_tham_so": 2, "so_dang_dung": 1, "so_muc_3": 1,
                                         "so_luon_hoi": 1, "co_quy_tac": False})
        self.assertNotIn("mo_ta", str(result.tom_tat))

    def test_canh_bao_khong_chan_va_ma_bam_noi_dung(self):
        rows = [dm.HEADER] + [dong(f"DV-{i:02d}", tk="", bk="", bat_buoc="") for i in range(1, 62)]
        result = dm.kiem_tra_danh_muc(rows)
        result2 = dm.kiem_tra_danh_muc(rows, ma_bam_da_co=[result.ma_bam_noi_dung])
        self.assertEqual(result.ma_bam_noi_dung, result2.ma_bam_noi_dung)
        codes = [v.ma for v in result2.canh_bao]
        self.assertEqual(codes.count("KHONG_TU_KHOA"), 61)
        self.assertIn("NHIEU_THAM_SO", codes)
        self.assertIn("TRUNG_NOI_DUNG", codes)
        rong = dm.kiem_tra_danh_muc([dm.HEADER, dong(tk=" ; ; ", bk="\n;", bat_buoc="")])
        self.assertIn("KHONG_TU_KHOA", [v.ma for v in rong.canh_bao])
        changed = deepcopy(rows)
        changed[-1][5] = "Không"
        self.assertNotEqual(dm.kiem_tra_danh_muc(changed).ma_bam_noi_dung, result.ma_bam_noi_dung)
        self.assertNotEqual(dm.kiem_tra_danh_muc([rows[0]] + rows[:0:-1]).ma_bam_noi_dung, result.ma_bam_noi_dung)

    def test_quy_tac_ba_kieu_va_loi_ma_tham_chieu(self):
        rows = [dm.HEADER, dong(), dong("DV-02")]
        rules = [dm.QUY_TAC_HEADER, ["Tổng tỷ lệ", "DV-01; DV-02", "=", 100],
                 ["Tổng tỷ lệ", "DV-01", "<=", 100], ["Ngày không sau", "DV-01", "<=", "DV-02"],
                 ["Có thì phải có", "DV-01", "", "DV-02"]]
        result = dm.kiem_tra_danh_muc(rows, quy_tac=rules)
        self.assertEqual(len(result.quy_tac), 4)
        self.assertTrue(result.tom_tat["co_quy_tac"])
        for rule, code in ((["Không biết", "DV-01", "", ""], "SAI_QUY_TAC"),
                           (["Tổng tỷ lệ", "DV-01", ">=", 100], "SAI_QUY_TAC"),
                           (["Ngày không sau", "DV-01", "<=", "DV-99"], "QUY_TAC_MA_KHONG_CO"),
                           (["Có thì phải có", "DV-99", "", "DV-02"], "QUY_TAC_MA_KHONG_CO")):
            with self.subTest(rule=rule):
                loi = self.bat_loi(dm.kiem_tra_danh_muc, rows, quy_tac=[dm.QUY_TAC_HEADER, rule])
                self.assertIn((code, 2), [(v.ma, v.dong) for v in loi])

    def test_khac_biet_them_bo_doi_bat_tat_va_thu_tu(self):
        a = dm.kiem_tra_danh_muc([dm.HEADER, dong(), dong("DV-02"), dong("DV-03")])
        b = dm.kiem_tra_danh_muc([dm.HEADER, dong("DV-02", mo_ta="Đổi mô tả", dung="Không"), dong(), dong("DV-04")])
        saved = deepcopy((a.cac_dong, b.cac_dong))
        diff = dm.khac_biet(a, b)
        self.assertEqual(diff["them"], ["DV-04"])
        self.assertEqual(diff["bo"], ["DV-03"])
        self.assertEqual(diff["doi"], [{"ma": "DV-02", "cot": "Mô tả cho AI", "truoc": "Nội dung dịch vụ (DEMO)", "sau": "Đổi mô tả"}])
        self.assertEqual(diff["bat_tat"], [{"ma": "DV-02", "cot": "Dùng (Có/Không)", "truoc": True, "sau": False}])
        self.assertTrue(diff["doi_thu_tu"])
        self.assertEqual((a.cac_dong, b.cac_dong), saved)
        c = dm.kiem_tra_danh_muc([dm.HEADER, dong("DV-04"), dong(), dong("DV-02"), dong("DV-03")])
        self.assertFalse(dm.khac_biet(a, c)["doi_thu_tu"])
        self.assertEqual(dm.khac_biet(a, a), {"them": [], "bo": [], "doi": [], "bat_tat": [], "doi_thu_tu": False, "doi_quy_tac": False})

    def test_khac_biet_quy_tac(self):
        a = dm.kiem_tra_danh_muc([dm.HEADER, dong()])
        b = dm.kiem_tra_danh_muc([dm.HEADER, dong()], quy_tac=[dm.QUY_TAC_HEADER, ["Tổng tỷ lệ", "DV-01", "=", 100]])
        self.assertTrue(dm.khac_biet(a, b)["doi_quy_tac"])

    def test_mau_excel_trong_dung_header_huong_dan_quy_tac_tuy_chon(self):
        for co_qt in (False, True):
            raw = dm.tao_mau_excel(co_quy_tac=co_qt)
            self.assertEqual(xlsx_mini.read_xlsx(io.BytesIO(raw)), [dm.HEADER])
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                names = [s.get("name") for s in ET.fromstring(z.read("xl/workbook.xml")).find(f"{NS}sheets")]
            self.assertEqual(names, ["Danh_muc", "Huong_dan"] + (["Quy_tac"] if co_qt else []))
            if co_qt:
                self.assertEqual(xlsx_mini.read_xlsx(io.BytesIO(raw), 2), [dm.QUY_TAC_HEADER])
            self.assertEqual([v.ma for v in self.bat_loi(dm.doc_danh_muc, raw)], ["KHONG_CO_THAM_SO_DUNG"])

    def test_chon_danh_muc_khi_khong_phai_sheet_dau_va_fallback(self):
        for name in ("Danh_muc", "Trang_1"):
            out = io.BytesIO()
            sheets = {name: {"rows": [dm.HEADER, dong()]}}
            if name == "Danh_muc":
                sheets = {"Huong_dan": {"rows": [["Hướng dẫn"]]}, **sheets}
            xlsx_mini.write_xlsx(out, sheets)
            self.assertEqual(dm.doc_danh_muc(out.getvalue()).tham_so[0]["ma"], "DV-01")

    def test_quy_tac_xlsx_va_ma_bam_tep(self):
        raw = excel(Quy_tac={"rows": [dm.QUY_TAC_HEADER, ["Tổng tỷ lệ", "DV-01", "<=", 100]]})
        result = dm.doc_danh_muc(raw)
        self.assertEqual(result.ma_bam, hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.quy_tac[0]["dieu_kien"], "<=")
        self.assertEqual(result.ma_bam_noi_dung, dm.doc_danh_muc(excel()).ma_bam_noi_dung)

    def test_tu_choi_duoi_tep_sai_zip_va_qua_kich_thuoc(self):
        for raw, name, code in ((excel(), "mau.xlsm", "SAI_TEP"), (b"khong phai zip", "mau.xlsx", "SAI_TEP"),
                                 (b"x" * (dm.GIOI_HAN_TEP + 1), "mau.xlsx", "TEP_QUA_LON"),
                                 ("duong-dan.xlsx", "mau.xlsx", "SAI_TEP")):
            with self.subTest(code=code):
                self.assertEqual(self.bat_loi(dm.doc_danh_muc, raw, name)[0].ma, code)

    def test_tu_choi_macro_ke_ca_gia_duoi_xlsx(self):
        raw = sua_zip(excel(), "[Content_Types].xml", lambda v: v.replace(b"spreadsheetml.sheet.main", b"ms-excel.sheet.macroEnabled.main"))
        self.assertEqual(self.bat_loi(dm.doc_danh_muc, raw)[0].ma, "TEP_CO_MACRO")

    def test_tu_choi_zip_phinh_truoc_doc_xml(self):
        raw = sua_zip(excel(), "xl/styles.xml", lambda _: b"x" * (dm.GIOI_HAN_GIAI_NEN + 1))
        self.assertLess(len(raw), dm.GIOI_HAN_TEP)
        self.assertEqual(self.bat_loi(dm.doc_danh_muc, raw)[0].ma, "TEP_QUA_LON")

    def test_cong_thuc_co_cache_o_gop_va_bool_xml(self):
        def edit(root):
            cells = {c.get("r"): c for c in root.iter(f"{NS}c")}
            ET.SubElement(cells["G2"], f"{NS}f").text = "1+1"
            cells["J2"].set("t", "b")
            ET.SubElement(cells["J2"], f"{NS}v").text = "0"
            merges = ET.SubElement(root, f"{NS}mergeCells")
            ET.SubElement(merges, f"{NS}mergeCell", ref="B2:C2")
        loi = self.bat_loi(dm.doc_danh_muc, sua_sheet(excel(), edit))
        self.assertTrue({("O_CONG_THUC", 2, "G"), ("O_GOP", 2, "B"), ("SAI_KIEU_O", 2, "J")}
                        <= {(v.ma, v.dong, v.cot) for v in loi})

    def test_so_dong_vat_ly_sau_khoang_trong(self):
        def edit(root):
            row = root.find(f"{NS}sheetData")[2]
            row.set("r", "12")
            for c in row:
                c.set("r", c.get("r")[:-1] + "12")
        raw = sua_sheet(excel([dm.HEADER, dong(), dong()]), edit)
        loi = self.bat_loi(dm.doc_danh_muc, raw)
        trung = next(v for v in loi if v.ma == "TRUNG_MA")
        self.assertEqual(trung.dong, 12)
        self.assertIn("trùng dòng 2", trung.thong_bao)

    def test_khong_co_dong_tieu_de_khong_lay_dong_2_thay_the(self):
        def edit(root):
            data = root.find(f"{NS}sheetData")
            data.remove(data[0])
        loi = self.bat_loi(dm.doc_danh_muc, sua_sheet(excel(), edit))
        self.assertEqual(sum(v.ma == "THIEU_COT" for v in loi), 10)

    def test_xml_hong_lien_ket_ngoai_va_thuc_the(self):
        raw = excel()
        variants = [sua_zip(raw, "xl/workbook.xml", lambda _: b"<broken>"),
                    sua_zip(raw, "xl/workbook.xml", lambda _: b'<!DOCTYPE a [<!ENTITY x "abc">]><a>&x;</a>'),
                    sua_zip(raw, "xl/_rels/workbook.xml.rels", lambda v: v.replace(b'<Relationship Id=', b'<Relationship TargetMode="External" Id='))]
        for value in variants:
            with self.subTest(value=value[:10]):
                self.assertEqual(self.bat_loi(dm.doc_danh_muc, value)[0].ma, "SAI_TEP")

    def test_hai_module_moi_khong_import_core_ha_tang_nguon_engines(self):
        stdlib = {"__future__", "dataclasses", "hashlib", "io", "json", "posixpath", "re", "unicodedata", "xml", "zipfile", "zlib"}
        for name in ("danh_muc_tham_so.py", "xlsx_mini.py"):
            tree = ast.parse((SDK / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertIn(alias.name.split(".")[0], stdlib)
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        self.assertEqual(node.level, 1)
                        self.assertIsNone(node.module)
                        self.assertEqual([v.name for v in node.names], ["xlsx_mini"])
                    else:
                        self.assertIn(node.module.split(".")[0], stdlib)
        # Tách riêng hai module mới khỏi bootstrap SDK hiện hữu; chỉ có stdlib,
        # không site-packages, không shims M4/engine/Core và không thư mục repo.
        code = (
            "import sys, types\n"
            f"p = types.ModuleType('kho_tri_thuc'); p.__path__ = {[str(SDK.parent)]!r}\n"
            "sys.modules[p.__name__] = p\n"
            f"s = types.ModuleType('kho_tri_thuc.sdk_core'); s.__path__ = {[str(SDK)]!r}\n"
            "sys.modules[s.__name__] = s\n"
            "from kho_tri_thuc.sdk_core.danh_muc_tham_so import tao_mau_excel\n"
            "assert tao_mau_excel().startswith(b'PK')\n"
            "assert not any(n.startswith(('kho_tri_thuc.core', 'kho_tri_thuc.ha_tang', 'kho_tri_thuc.nguon', 'kho_tri_thuc.engines', 'kho_tri_thuc.m4')) for n in sys.modules)\n"
        )
        result = subprocess.run([sys.executable, "-I", "-S", "-X", "utf8", "-B", "-c", code],
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
