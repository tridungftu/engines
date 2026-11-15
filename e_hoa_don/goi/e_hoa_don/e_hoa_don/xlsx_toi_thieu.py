"""OOXML tối thiểu trong RAM; mọi ô là inline string, kể cả tiền và STT."""

import io
import re
import zipfile
from xml.sax.saxutils import escape

from kho_tri_thuc_sdk.engine import LoiNghiepVu

CELL_TOI_DA = 16000
XLSX_TOI_DA = 32 * 1024 * 1024
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def vuot_tran():
    raise LoiNghiepVu("HD_BANG_KE_VUOT_GIOI_HAN",
                     "Bảng kê vượt giới hạn xử lý. Anh hãy chia nhỏ dữ liệu đầu vào.")


def chu_xml(value):
    text = "" if value is None else str(value)
    if len(text) > CELL_TOI_DA:
        vuot_tran()
    # OOXML ST_Xstring: bảo toàn cả chuỗi trông như escape và control XML 1.0.
    text = re.sub(r"_x[0-9a-fA-F]{4}_", lambda m: "_x005F_" + m[0][1:], text)
    text = "".join(c if (c in "\t\n\r" or 0x20 <= ord(c) <= 0xD7FF
                         or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)
                   else f"_x{ord(c):04X}_" for c in text)
    # CR phải là character reference, tránh XML chuẩn hóa thành LF.
    return escape(text).replace("\r", "&#13;")


def ten_cot(index):
    text = ""
    while index:
        index, rem = divmod(index - 1, 26)
        text = chr(65 + rem) + text
    return text


class _BoDem(io.BytesIO):
    def write(self, data):
        if self.tell() + len(data) > XLSX_TOI_DA:
            vuot_tran()
        return super().write(data)


def tao_xlsx(hoa_don, kiem_ke, thong_tin, cot_hoa_don, cot_kiem_ke, kiem_tra):
    """Sheet kiểm kê có khối thông tin đầu, header cuối khối được đóng băng."""
    buffer = _BoDem()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as goi:
        goi.writestr("[Content_Types].xml", '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''')
        goi.writestr("_rels/.rels", f'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>''')
        goi.writestr("xl/workbook.xml", f'''<workbook xmlns="{NS}" xmlns:r="{REL}"><sheets><sheet name="Hoa don" sheetId="1" r:id="rId1"/><sheet name="Kiem ke tep" sheetId="2" r:id="rId2"/></sheets></workbook>''')
        goi.writestr("xl/_rels/workbook.xml.rels", f'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{REL}/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="{REL}/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="{REL}/styles" Target="styles.xml"/></Relationships>''')
        goi.writestr("xl/styles.xml", f'''<styleSheet xmlns="{NS}">
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF264653"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="2"><xf numFmtId="49" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf><xf numFmtId="49" fontId="1" fillId="2" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>''')
        for so, cot, du_lieu, dau in ((1, cot_hoa_don, hoa_don, []),
                                       (2, cot_kiem_ke, kiem_ke, thong_tin)):
            kiem_tra()
            header = len(dau) + 1
            with goi.open(f"xl/worksheets/sheet{so}.xml", "w") as sheet:
                def ghi(text):
                    kiem_tra()
                    sheet.write(text.encode("utf-8"))
                ghi(f'<worksheet xmlns="{NS}"><sheetViews><sheetView workbookViewId="0"><pane ySplit="{header}" topLeftCell="A{header + 1}" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols>')
                for i, (_, width) in enumerate(cot, 1):
                    ghi(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>')
                ghi('</cols><sheetData>')
                rows = [*dau, [c[0] for c in cot], *du_lieu]
                for r, row in enumerate(rows, 1):
                    ghi(f'<row r="{r}">')
                    for c, value in enumerate(row, 1):
                        ghi(f'<c r="{ten_cot(c)}{r}" s="{1 if r == header else 0}" t="inlineStr"><is><t xml:space="preserve">{chu_xml(value)}</t></is></c>')
                    ghi('</row>')
                ghi('</sheetData></worksheet>')
    kiem_tra()
    return buffer.getvalue()
