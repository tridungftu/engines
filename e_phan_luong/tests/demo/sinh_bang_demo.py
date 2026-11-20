"""Sinh bảng DEMO tái hiện được bằng thư viện chuẩn, không cần Excel.

Chạy: python sinh_bang_demo.py <thu_muc_demo>. Test dùng bytes trong RAM.
"""
from datetime import datetime
from io import BytesIO, StringIO
import csv
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

TIEU_DE = ["Mã", "Ngày", "Số tiền", "Tiền tệ", "Diễn giải", "Đối tác",
           "Số tiền quy đổi", "Tiền tệ quy đổi", "Nhập tay", "Cờ đỏ cứng", "Bộ phận"]


def khuon_demo():
    cac_ma = ["ma", "ngay", "so_tien", "tien_te", "dien_giai", "doi_tac",
              "so_tien_quy_doi", "tien_te_quy_doi", "nhap_tay", "co_do_cung",
              "thuoc_tinh.bo_phan"]
    return {"phien_ban": 1, "sheet": "DEMO", "cot": [
        {"ma": ma, "tu_khoa": [ten], "bat_buoc": ma in {"ma", "ngay", "so_tien"}}
        for ma, ten in zip(cac_ma, TIEU_DE)], "dong_dung": ["Cộng", "Tổng cộng"]}


def hang_demo(*, excel=False):
    return [["Công ty DEMO Ánh Dương"], TIEU_DE, [],
            ["PC-DEMO-0001", datetime(2026, 10, 30) if excel else "30/10/2026",
             1000000.25 if excel else "1000000.25", "VND", "Thanh toán DEMO, đợt 1; thử",
             "DEMO-NCC-01", None, None, True if excel else "true", False if excel else "false", "DEMO-KT"],
            ["PC-DEMO-0002", "2026-11-01", -25.125 if excel else "-25.125", "USD",
             "Thanh toán DEMO đợt 2", "DEMO-NCC-02", 625000 if excel else "625000", "VND",
             False if excel else "false", True if excel else "true", "DEMO-KT"],
            ["Cộng", None, 1000000 if excel else "1000000"],
            ["PC-DEMO-SAU-CONG", "2026-11-01", "99", "VND"]]


def lo_json_demo():
    return json.dumps({"phien_ban": 1, "ma_module": "demo_thanh_toan", "ky": "2026-11",
                       "nguong": None, "nghiep_vu": [
        {"ma": "PC-DEMO-0001", "ngay": "2026-10-30", "so_tien": {"so": "1000000.25", "tien_te": "VND"},
         "dien_giai": "Thanh toán DEMO, đợt 1; thử", "doi_tac": "DEMO-NCC-01", "nhap_tay": True,
         "co_do_cung": False, "thuoc_tinh": {"bo_phan": "DEMO-KT"}},
        {"ma": "PC-DEMO-0002", "ngay": "2026-11-01", "so_tien": {"so": "-25.125", "tien_te": "USD"},
         "so_tien_quy_doi": {"so": "625000", "tien_te": "VND"}, "dien_giai": "Thanh toán DEMO đợt 2",
         "doi_tac": "DEMO-NCC-02", "nhap_tay": False, "co_do_cung": True,
         "thuoc_tinh": {"bo_phan": "DEMO-KT"}}]}, ensure_ascii=False).encode("utf-8")


def sinh_csv(hang=None, *, dau=",", bom=False):
    bo_nho = StringIO(newline="")
    csv.writer(bo_nho, delimiter=dau, lineterminator="\n").writerows(
        hang_demo() if hang is None else hang)
    return bo_nho.getvalue().encode("utf-8-sig" if bom else "utf-8")


def _cot(i):
    chu = ""
    while i:
        i, du = divmod(i - 1, 26)
        chu = chr(65 + du) + chu
    return chu


def sinh_xlsx(hang=None, *, sheet="DEMO", cong_thuc=True):
    """Ghi XML trực tiếp; C4 có công thức + <v> đã lưu, B4 có kiểu ngày."""
    hang = hang_demo(excel=True) if hang is None else hang
    cac_dong = []
    for r, ds in enumerate(hang, 1):
        cac_o = []
        for c, v in enumerate(ds, 1):
            if v is None:
                continue
            ref = f"{_cot(c)}{r}"
            if isinstance(v, datetime):
                so = (v - datetime(1899, 12, 30)).days
                o = f'<c r="{ref}" s="1"><v>{so}</v></c>'
            elif type(v) is bool:
                o = f'<c r="{ref}" t="b"><v>{int(v)}</v></c>'
            elif type(v) in (int, float):
                f = "<f>1000000+0.25</f>" if cong_thuc and ref == "C4" else ""
                o = f'<c r="{ref}">{f}<v>{repr(v)}</v></c>'
            else:
                o = f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>'
            cac_o.append(o)
        cac_dong.append(f'<row r="{r}">{"".join(cac_o)}</row>')
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/package/2006/relationships"
    office = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    tep = {
        "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
        "_rels/.rels": f'<Relationships xmlns="{rel}"><Relationship Id="rId1" Type="{office}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<workbook xmlns="{ns}" xmlns:r="{office}"><sheets><sheet name="{escape(sheet)}" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<Relationships xmlns="{rel}"><Relationship Id="rId1" Type="{office}/worksheet" Target="worksheets/sheet1.xml"/>'
        f'<Relationship Id="rId2" Type="{office}/styles" Target="styles.xml"/></Relationships>',
        "xl/styles.xml": f'<styleSheet xmlns="{ns}"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs>'
        '<cellXfs count="2"><xf numFmtId="0"/><xf numFmtId="14" applyNumberFormat="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{ns}"><sheetData>{"".join(cac_dong)}</sheetData></worksheet>',
    }
    bo_nho = BytesIO()
    with ZipFile(bo_nho, "w", compression=ZIP_DEFLATED) as goi:
        for ten, xml in tep.items():
            info = ZipInfo(ten, date_time=(2026, 10, 30, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            goi.writestr(info, xml.encode("utf-8"))
    return bo_nho.getvalue()


def main():
    dich = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    dich.mkdir(parents=True, exist_ok=True)
    (dich / "bang-DEMO.xlsx").write_bytes(sinh_xlsx())
    (dich / "bang-DEMO.json").write_bytes(lo_json_demo())
    for dau, ten in ((",", "phay"), (";", "cham-phay")):
        for bom in (False, True):
            (dich / f"bang-DEMO-{ten}-{'bom' if bom else 'utf8'}.csv").write_bytes(sinh_csv(dau=dau, bom=bom))


if __name__ == "__main__":
    main()
