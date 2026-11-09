"""AI export for Excel (2.3.0): a new, values-only XLSX built from a masking plan.

ChatGPT/Claude read workbooks with pandas/openpyxl and do not recalculate formulas, so
the AI export keeps what they need: masked cell values (formula results included),
number/date formats, merged cells, column widths, hidden state, and optionally the
formulas as text. Links, drawings, images, pivots, printer settings and file metadata
are not copied. Written with the standard library only: no new runtime dependency.
"""
from __future__ import annotations

import io
import re
import zipfile
from xml.sax.saxutils import escape

from .core import TOKEN, literal_pattern
from .types import PrivacyError

MAX_CELL_TEXT = 32767
STYLE = {None: 0, "date": 1, "datetime": 2, "time": 3, "percent": 4, "grouped": 5, "grouped_decimal": 6}
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff￾￿]")
SHEET_NAME_BAD = re.compile(r"[\[\]:*?/\\]")
DATE_1904_OFFSET = 1462

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    '{sheets}</Types>')
SHEET_TYPE = ('<Override PartName="/xl/worksheets/sheet{n}.xml" '
              'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
ROOT_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
             'Target="xl/workbook.xml"/></Relationships>')
STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<numFmts count="3"><numFmt numFmtId="164" formatCode="dd/mm/yyyy"/>'
    '<numFmt numFmtId="165" formatCode="dd/mm/yyyy hh:mm"/><numFmt numFmtId="166" formatCode="hh:mm:ss"/></numFmts>'
    '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="7"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="166" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="10" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="3" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
    '<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')


def clean_text(value: str) -> str:
    return CONTROL.sub("", value)[:MAX_CELL_TEXT]


def safe_sheet_name(name: str, taken: set[str]) -> str:
    """Excel sheet names: no []:*?/\\, at most 31 characters, unique (case-insensitive)."""
    base = SHEET_NAME_BAD.sub("", clean_text(name)).strip("' ") or "Sheet"
    candidate, index = base[:31], 2
    while candidate.casefold() in taken:
        suffix = f" ({index})"
        candidate, index = base[:31 - len(suffix)] + suffix, index + 1
    taken.add(candidate.casefold())
    return candidate


def column_letters(number: int) -> str:
    letters = ""
    while number:
        number, rem = divmod(number - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def _cell_xml(row: int, col: int, kind: str, value, fmt: str | None) -> str:
    ref = f"{column_letters(col)}{row}"
    if kind == "s":
        text = escape(clean_text(str(value)))
        return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'
    if kind == "b":
        return f'<c r="{ref}" t="b"><v>{1 if str(value).strip() in {"1", "true", "TRUE"} else 0}</v></c>'
    if kind == "e":
        return f'<c r="{ref}" t="e"><v>{escape(str(value))}</v></c>'
    style = STYLE.get(fmt, 0)
    attr = f' s="{style}"' if style else ""
    return f'<c r="{ref}"{attr}><v>{value}</v></c>'


def _sheet_xml(sheet: dict) -> str:
    rows: dict[int, list] = {}
    for row, col, kind, value, fmt in sheet["cells"]:
        rows.setdefault(row, []).append((col, kind, value, fmt))
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    if sheet.get("frozen_header"):
        parts.append('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
                     'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
    cols = []
    for c in sheet.get("cols", []):
        try:  # malformed widths are skipped, not fatal
            low, high, width = int(c["min"]), int(c["max"]), float(c.get("width", "10"))
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= low <= high <= 16384 and 0 <= width <= 255:
            hidden = ' hidden="1"' if c.get("hidden") in {"1", "true"} else ""
            cols.append(f'<col min="{low}" max="{high}" width="{width:.2f}" customWidth="1"{hidden}/>')
    if cols:
        parts.append("<cols>" + "".join(cols) + "</cols>")
    parts.append("<sheetData>")
    for row in sorted(rows):
        cells = "".join(_cell_xml(row, col, kind, value, fmt) for col, kind, value, fmt in sorted(rows[row]))
        parts.append(f'<row r="{row}">{cells}</row>')
    parts.append("</sheetData>")
    merges = [ref for ref in sheet.get("merges", []) if re.fullmatch(r"[A-Z]{1,3}\d+(?::[A-Z]{1,3}\d+)?", ref)]
    if merges:
        parts.append(f'<mergeCells count="{len(merges)}">' +
                     "".join(f'<mergeCell ref="{ref}"/>' for ref in merges) + "</mergeCells>")
    parts.append("</worksheet>")
    return "".join(parts)


def build_values_workbook(plan: dict) -> bytes:
    sheets = plan["sheets"]
    if not sheets:
        raise PrivacyError("Workbook không còn sheet nào để xuất.")
    if all(s.get("state") != "visible" for s in sheets):
        sheets[0]["state"] = "visible"  # Excel needs at least one visible sheet
    workbook = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']
    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for n, sheet in enumerate(sheets, 1):
        state = sheet.get("state", "visible")
        state = "" if state not in {"hidden", "veryHidden"} else f' state="{state}"'
        workbook.append(f'<sheet name="{escape(sheet["name"], {chr(34): "&quot;"})}" sheetId="{n}"{state} r:id="rId{n}"/>')
        rels.append(f'<Relationship Id="rId{n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    f'relationships/worksheet" Target="worksheets/sheet{n}.xml"/>')
    styles_id = len(sheets) + 1
    rels.append(f'<Relationship Id="rId{styles_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/styles" Target="styles.xml"/></Relationships>')
    workbook.append("</sheets></workbook>")
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        stamp = (2000, 1, 1, 0, 0, 0)  # neutral timestamp: no original file times
        def write(name, text):
            archive.writestr(zipfile.ZipInfo(name, stamp), text.encode("utf-8"), zipfile.ZIP_DEFLATED)
        write("[Content_Types].xml", CONTENT_TYPES.format(
            sheets="".join(SHEET_TYPE.format(n=n) for n in range(1, len(sheets) + 1))))
        write("_rels/.rels", ROOT_RELS)
        write("xl/workbook.xml", "".join(workbook))
        write("xl/_rels/workbook.xml.rels", "".join(rels))
        write("xl/styles.xml", STYLES)
        for n, sheet in enumerate(sheets, 1):
            write(f"xl/worksheets/sheet{n}.xml", _sheet_xml(sheet))
    return stream.getvalue()


def verify_values_workbook(data: bytes, rules: list[dict]) -> list[str]:
    """Read the generated package back: every text node, attribute and cell value of every part.

    Reports an enabled source phrase still present, or a number whose digits equal a selected
    identifier. Uses expat, like the reader, so decoding matches what Excel/openpyxl will see.
    """
    from xml.parsers import expat

    active = [r for r in rules if r.get("enabled")]
    if not active:
        return []
    expression = re.compile("|".join(literal_pattern(r["source"]) for r in active), re.I)
    digits = {re.sub(r"\D", "", r["source"]).lstrip("0") for r in active
              if re.fullmatch(r"[\d .-]{6,}", r["source"].strip())}
    digits.discard("")
    findings = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            stack = []

            def check(text, where=name):
                if not text:
                    return
                number = re.fullmatch(r"[+-]?(\d+)(?:\.0*)?", text.strip())
                if expression.search(TOKEN.sub(" ", text)) or (number and number[1].lstrip("0") in digits):
                    findings.append(f"{where}: {text[:120]}")

            def start(tag, attrs):
                stack.append([])
                for value in attrs.values():
                    check(value)

            def end(tag):
                check("".join(stack.pop()))

            def chars(value):
                if stack:
                    stack[-1].append(value)

            parser = expat.ParserCreate()
            parser.StartElementHandler, parser.EndElementHandler = start, end
            parser.CharacterDataHandler = chars
            try:
                parser.Parse(archive.read(name), True)
            except expat.ExpatError:
                findings.append(f"{name}: XML không hợp lệ")
    return findings
