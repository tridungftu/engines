"""Fixture XLSX DEMO trong RAM, oracle literal; không dùng writer runtime."""

import struct
import zlib

from ho_tro_mask_b1 import S, R, CT_S, them_phan, excel_demo, dong_goi, nen_raw

CP = 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
DC = 'http://purl.org/dc/elements/1.1/'
DCT = 'http://purl.org/dc/terms/'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
EP = 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
CUSTOM = 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
VT = 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'

STYLES = f'''<styleSheet xmlns="{S}">
<numFmts count="2"><numFmt numFmtId="164" formatCode="yyyy-mm-dd"/><numFmt numFmtId="165" formatCode="#,##0&quot; VND&quot;"/></numFmts>
<fonts count="2"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/><scheme val="minor"/></font><font><b/><sz val="11"/><color rgb="FF000000"/><name val="Arial"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/><xf numFmtId="165" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"><alignment wrapText="1"/></xf></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles><dxfs count="0"/><tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>
</styleSheet>'''


def theme_demo():
    scheme = ''.join(f'<a:{n}><a:srgbClr val="{v}"/></a:{n}>' for n, v in (
        ('dk1', '000000'), ('lt1', 'FFFFFF'), ('dk2', '1F497D'), ('lt2', 'EEECE1'),
        ('accent1', '4F81BD'), ('accent2', 'C0504D'), ('accent3', '9BBB59'), ('accent4', '8064A2'),
        ('accent5', '4BACC6'), ('accent6', 'F79646'), ('hlink', '0000FF'), ('folHlink', '800080')))
    font = '<a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/>'
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    line = '<a:ln w="6350" cap="flat" cmpd="sng" algn="ctr">' + fill + '<a:prstDash val="solid"/><a:miter lim="800000"/></a:ln>'
    effect = '<a:effectStyle><a:effectLst/></a:effectStyle>'
    return (f'<a:theme xmlns:a="{A}" name="Office Theme"><a:themeElements><a:clrScheme name="Office">' + scheme
            + '</a:clrScheme><a:fontScheme name="Office"><a:majorFont>' + font + '</a:majorFont><a:minorFont>' + font
            + '</a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst>' + fill * 3
            + '</a:fillStyleLst><a:lnStyleLst>' + line * 3 + '</a:lnStyleLst><a:effectStyleLst>' + effect * 3
            + '</a:effectStyleLst><a:bgFillStyleLst>' + fill * 3 + '</a:bgFillStyleLst></a:fmtScheme></a:themeElements>'
            + '<a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')


def phan_demo(*, day_du=False):
    phan = excel_demo(noi_dung=(
        '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>0</v></c>'
        '<c r="C1" t="inlineStr"><is><r><rPr><b/><rFont val="Arial"/></rPr><t>DEMO Trần </t></r>'
        '<r><rPr><i/></rPr><t>Ánh </t></r><r><t>Dương</t></r></is></c></row>'
        '<row r="2" hidden="1"><c r="A2" t="inlineStr"><is><t>DEMO Nguyễn Lan</t></is></c>'
        '<c r="B2" s="2"><v>1000000</v></c><c r="C2" s="1" t="n"><v>46325</v></c>'
        '<c r="D2" t="b"><v>1</v></c><c r="E2" t="inlineStr"><is><t>0000123</t></is></c></row>'
        '<row r="3"><c r="A3" t="inlineStr"><is><t>DEMO ô gộp</t></is></c></row>'))
    sheet = phan['xl/worksheets/sheet1.xml']
    phan['xl/worksheets/sheet1.xml'] = sheet.replace('<sheetData>',
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/><cols><col min="1" max="1" width="12" hidden="1" customWidth="1"/></cols><sheetData>').replace(
        '</worksheet>', '<mergeCells count="1"><mergeCell ref="A3:B3"/></mergeCells></worksheet>')
    them_phan(phan, 'xl/styles.xml', STYLES, CT_S + 'styles+xml', 'styles', rid='rId10', chu='xl/workbook.xml')
    them_phan(phan, 'xl/sharedStrings.xml', f'<sst xmlns="{S}" count="2" uniqueCount="2"><si><t>DEMO Công ty Ánh Dương</t></si><si><t>DEMO tên chưa dùng</t></si></sst>',
              CT_S + 'sharedStrings+xml', 'sharedStrings', rid='rId11', chu='xl/workbook.xml')
    if day_du:
        them_phan(phan, 'xl/theme/theme1.xml', theme_demo(),
                  'application/vnd.openxmlformats-officedocument.theme+xml', 'theme', rid='rId12', chu='xl/workbook.xml')
        them_phan(phan, 'xl/calcChain.xml', f'<calcChain xmlns="{S}"/>', CT_S + 'calcChain+xml', 'calcChain', rid='rId13', chu='xl/workbook.xml')
        them_phan(phan, 'docProps/core.xml', f'<cp:coreProperties xmlns:cp="{CP}" xmlns:dc="{DC}" xmlns:dcterms="{DCT}" xmlns:xsi="{XSI}">'
                  '<dc:title>DEMO hồ sơ Ánh Dương</dc:title><dc:creator>DEMO Nguyễn Lan</dc:creator><cp:lastModifiedBy>DEMO Trần Hà</cp:lastModifiedBy>'
                  '<dcterms:created xsi:type="dcterms:W3CDTF">2026-10-30T00:00:00Z</dcterms:created><cp:revision>1</cp:revision></cp:coreProperties>',
                  'application/vnd.openxmlformats-package.core-properties+xml', 'core-properties', rid='rId2', chu='')
        phan['_rels/.rels'] = phan['_rels/.rels'].replace(R + '/core-properties',
                    'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties')
        them_phan(phan, 'docProps/app.xml', f'<Properties xmlns="{EP}" xmlns:vt="{VT}"><Application>Microsoft Excel</Application>'
                  '<DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop><Manager>DEMO Trần Minh</Manager><Company>DEMO Ánh Dương</Company>'
                  '<HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>'
                  '<vt:variant><vt:i4>1</vt:i4></vt:variant></vt:vector></HeadingPairs><TitlesOfParts><vt:vector size="1" baseType="lpstr">'
                  '<vt:lpstr>DEMO 1</vt:lpstr></vt:vector></TitlesOfParts><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc>'
                  '<HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0300</AppVersion></Properties>',
                  'application/vnd.openxmlformats-officedocument.extended-properties+xml', 'extended-properties', rid='rId3', chu='')
        them_phan(phan, 'docProps/custom.xml', f'<Properties xmlns="{CUSTOM}" xmlns:vt="{VT}"><property fmtid="{{D5CDD505-2E9C-101B-9397-08002B2CF9AE}}" pid="2" name="DEMO chủ hồ sơ">'
                  '<vt:lpwstr>DEMO Lê Hạ</vt:lpwstr></property><property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="3" name="DEMO ngày">'
                  '<vt:filetime>2026-10-30T00:00:00Z</vt:filetime></property></Properties>',
                  'application/vnd.openxmlformats-officedocument.custom-properties+xml', 'custom-properties', rid='rId4', chu='')
    return phan


def goi_office(phan, *, co=6, descriptor=True, chu_ky=True, cach=8):
    """ZIP classic mô phỏng Excel: cờ 0x0006, descriptor 12/16 bytes thật."""
    local, central = bytearray(), bytearray()
    for ten, value in phan.items():
        ten = ten.encode()
        raw = value.encode() if isinstance(value, str) else value
        data = nen_raw(raw) if cach == 8 else raw
        crc, n, size = zlib.crc32(raw), len(data), len(raw)
        flags = co | (8 if descriptor else 0)
        off = len(local)
        local.extend(struct.pack('<4s5H3I2H', b'PK\x03\x04', 20, flags, cach, 0, 0x21,
                                 0 if descriptor else crc, 0 if descriptor else n,
                                 0 if descriptor else size, len(ten), 0))
        local.extend(ten + data)
        if descriptor:
            local.extend((b'PK\x07\x08' if chu_ky else b'') + struct.pack('<3I', crc, n, size))
        central.extend(struct.pack('<4s6H3I5H2I', b'PK\x01\x02', 20, 20, flags, cach, 0,
                                   0x21, crc, n, size, len(ten), 0, 0, 0, 0, 32, off))
        central.extend(ten)
    return bytes(local + central + struct.pack('<4s4H2IH', b'PK\x05\x06', 0, 0, len(phan), len(phan), len(central), len(local), 0))
