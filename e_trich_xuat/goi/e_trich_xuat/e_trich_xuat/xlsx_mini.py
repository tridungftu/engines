"""
xlsx_mini.py — Ghi file Excel .xlsx chỉ bằng thư viện chuẩn Python (không cần cài openpyxl).
    write_xlsx(BytesIO, {"Ten_sheet": {"rows": [[...], ...], "widths": [10, 40, ...]}, ...})
Dòng đầu mỗi sheet là tiêu đề (in đậm, nền xanh nhạt, cố định khi cuộn). Ô tự xuống dòng.
Ô có giá trị bắt đầu bằng "KIỂM TRA" hoặc "SAI" được tô vàng; "ĐÚNG"/"OK" tô xanh.
"""
import math
import re
import zipfile

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from xml.sax.saxutils import escape


def _col(n):
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _cell(ref, v, style):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("Số Excel phải hữu hạn.")
        return f'<c r="{ref}" s="{style}"><v>{v}</v></c>'
    t = str(v if v is not None else "")
    # Kiểm đơn vị UTF-16 trước XML escape; không cắt dữ liệu.
    if len(t.encode("utf-16-le")) // 2 > 32767:
        raise LoiNghiepVu("O_EXCEL_QUA_DAI", "Có ô vượt giới hạn Excel; không thể xuất đầy đủ.")
    # Bảo toàn ký tự XML cấm và literal _xHHHH_ bằng escape OOXML.
    t = re.sub(r"_x[0-9A-Fa-f]{4}_", lambda m: "_x005F_" + m[0][1:], t)
    t = "".join(("_x%04X_" % ord(c)) if (ord(c) < 32 and c not in "\t\n" or ord(c) in (0xFFFE, 0xFFFF)) else c for c in t)
    t = escape(t)
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{t}</t></is></c>'


def _sheet(rows, widths, kiem_huy):
    cols = "".join(f'<col min="{i+1}" max="{i+1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths or []))
    out = []
    for r, row in enumerate(rows):
        kiem_huy()
        cells = []
        for c, v in enumerate(row):
            style = 1 if r == 0 else 2
            sv = str(v) if v is not None else ""
            if r > 0 and (sv.startswith("KIỂM TRA") or sv.startswith("SAI") or sv.startswith("THIẾU")):
                style = 3
            elif r > 0 and sv in ("OK", "ĐÚNG"):
                style = 4
            cells.append(_cell(f"{_col(c)}{r+1}", v, style))
        out.append(f'<row r="{r+1}">{"".join(cells)}</row>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
            + (f"<cols>{cols}</cols>" if cols else "") + f'<sheetData>{"".join(out)}</sheetData></worksheet>')


STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
          '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
          '<fills count="5"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
          '<fill><patternFill patternType="solid"><fgColor rgb="FFDDEBF7"/></patternFill></fill>'
          '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/></patternFill></fill>'
          '<fill><patternFill patternType="solid"><fgColor rgb="FFE2EFDA"/></patternFill></fill></fills>'
          '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
          '<cellXfs count="5"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
          '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
          '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
          '<xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
          '<xf numFmtId="0" fontId="0" fillId="4" borderId="0" xfId="0" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
          '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')


def write_xlsx(path, sheets, *, kiem_huy=lambda: None):
    names = list(sheets)
    if (not names or any(not isinstance(n, str) or not 1 <= len(n) <= 31
                         or re.search(r"[\\/*?:\[\]]", n) for n in names)
            or len({n.casefold() for n in names}) != len(names)):
        raise ValueError("Tên trang Excel không hợp lệ.")
    kiem_huy()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   + "".join(f'<Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(len(names)))
                   + "</Types>")
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join(f'<sheet name="{escape(n, {chr(34): "&quot;"})}" sheetId="{i+1}" r:id="rId{i+1}"/>' for i, n in enumerate(names))
                   + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>' for i in range(len(names)))
                   + f'<Relationship Id="rId{len(names)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                   + "</Relationships>")
        z.writestr("xl/styles.xml", STYLES)
        for i, n in enumerate(names):
            z.writestr(f"xl/worksheets/sheet{i+1}.xml", _sheet(sheets[n]["rows"], sheets[n].get("widths"), kiem_huy))

