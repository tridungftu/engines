"""DOCX DEMO mô phỏng các part chuẩn khi Word lưu; chỉ dựng bytes RAM.

Không dùng Office, make_docx, python-docx, tệp thật hoặc writer của engine.
"""

import struct
import zlib

from ho_tro_mask_b1 import W, R, CT_W, dong_goi, nen_raw, them_phan, word_demo

CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCT = "http://purl.org/dc/terms/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
CUSTOM = "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties"
VT = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
FMTID = "{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"
CT_CHUNG = "application/vnd.openxmlformats-officedocument."


def p(chu):
    return f'<w:p><w:r><w:t>{chu}</w:t></w:r></w:p>'


def theme_demo():
    colors = ''.join(f'<a:{t}><a:srgbClr val="123456"/></a:{t}>' for t in
                     'dk1 lt1 dk2 lt2 accent1 accent2 accent3 accent4 accent5 accent6 hlink folHlink'.split())
    theme = (f'<a:theme xmlns:a="{A}" name="Office Theme">'
        f'<a:themeElements><a:clrScheme name="Office">{colors}</a:clrScheme>'
        '<a:fontScheme name="Office"><a:majorFont><a:latin typeface="Calibri Light"/>'
        '<a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
        '<a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>'
        '<a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="50000"/></a:schemeClr></a:gs>'
        '<a:gs pos="100000"><a:srgbClr val="FFFFFF"/></a:gs></a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill></a:fillStyleLst>'
        '<a:lnStyleLst><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:prstDash val="solid"/><a:miter lim="800000"/></a:ln></a:lnStyleLst>'
        '<a:effectStyleLst><a:effectStyle><a:effectLst><a:outerShdw blurRad="40000" dist="20000" dir="5400000" rotWithShape="0">'
        '<a:srgbClr val="000000"><a:alpha val="38000"/></a:srgbClr></a:outerShdw></a:effectLst></a:effectStyle></a:effectStyleLst>'
        '<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>'
        '</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')
    # Style matrix của theme Office có ba phần tử mỗi danh sách; không dùng
    # theme rỗng làm chứng cứ tương thích. Vẫn chưa là kiểm mở bằng Office.
    theme = theme.replace('</a:fillStyleLst>', '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>')
    for tag in ('lnStyleLst', 'effectStyleLst', 'bgFillStyleLst'):
        start = theme.index('<a:' + tag + '>') + len('<a:' + tag + '>')
        end = theme.index('</a:' + tag + '>')
        theme = theme[:start] + theme[start:end] * 3 + theme[end:]
    return theme


def word_day_du():
    than = (
        '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">DEMO Nguy&#7877;n </w:t></w:r>'
        '<w:r><w:rPr><w:rStyle w:val="Emphasis"/><w:i/></w:rPr><w:t xml:space="preserve">Va\u200bn </w:t></w:r>'
        '<w:r><w:rPr><w:rStyle w:val="Strong"/></w:rPr><w:t>A\u0301nh</w:t></w:r></w:p>'
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/></w:tblPr><w:tblGrid>'
        '<w:gridCol w:w="1000"/><w:gridCol w:w="1000"/><w:gridCol w:w="1000"/></w:tblGrid>'
        '<w:tr><w:tc><w:tcPr><w:gridSpan w:val="2"/><w:vMerge w:val="restart"/></w:tcPr>'
        + p('Ô gốc DEMO') + '</w:tc><w:tc>' + p('Ô khác DEMO') + '</w:tc></w:tr>'
        '<w:tr><w:tc><w:tcPr><w:gridSpan w:val="2"/><w:vMerge/></w:tcPr>'
        '<w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>Tên DEMO ô nối</w:t></w:r></w:p>'
        '</w:tc><w:tc>' + p('Ô cuối DEMO') + '</w:tc></w:tr></w:tbl>'
        '<w:p><w:r><w:t>DEMO &#x1F600; A&amp;B\r\nC&#13;D&#xA;E</w:t>'
        '<w:tab/><w:t>1.000.000 VND 30/10/2026</w:t><w:br/>'
        '<w:footnoteReference w:id="2"/><w:footnoteReference w:id="2"/><w:endnoteReference w:id="3"/></w:r></w:p>'
        '<w:sectPr><w:headerReference w:type="default" r:id="rId2"/>'
        '<w:footerReference w:type="default" r:id="rId3"/><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
    )
    phan = word_demo(noi_dung=than)
    for ten, root, chu, rid in [('header', 'hdr', 'Đầu trang DEMO', 'rId2'), ('footer', 'ftr', 'Chân trang DEMO', 'rId3')]:
        them_phan(phan, f'word/{ten}1.xml', f'<w:{root} xmlns:w="{W}">{p(chu)}</w:{root}>', CT_W + ten + '+xml', ten, rid=rid)
    notes = f'<w:footnotes xmlns:w="{W}"><w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
    notes += '<w:footnote w:id="2">' + p('Ghi chú DEMO lặp') + '</w:footnote><w:footnote w:id="4">' + p('Ghi chú DEMO lặp') + '</w:footnote></w:footnotes>'
    them_phan(phan, 'word/footnotes.xml', notes, CT_W + 'footnotes+xml', 'footnotes', rid='rId4')
    them_phan(phan, 'word/endnotes.xml', f'<w:endnotes xmlns:w="{W}"><w:endnote w:id="3">{p("Cuối tài liệu DEMO")}</w:endnote></w:endnotes>', CT_W + 'endnotes+xml', 'endnotes', rid='rId5')
    core = (f'<cp:coreProperties xmlns:cp="{CP}" xmlns:dc="{DC}" xmlns:dcterms="{DCT}" xmlns:xsi="{XSI}">'
            '<dc:title>Tiêu đề DEMO</dc:title><dc:subject>Chủ đề DEMO</dc:subject><dc:creator>Người tạo DEMO</dc:creator>'
            '<dc:description>Mô tả DEMO</dc:description><cp:lastModifiedBy>Người sửa DEMO</cp:lastModifiedBy>'
            '<cp:keywords>Từ khóa DEMO</cp:keywords><cp:revision>1</cp:revision>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">2026-10-30T00:00:00Z</dcterms:created>'
            '<dcterms:modified xsi:type="dcterms:W3CDTF">2026-10-30T00:00:00Z</dcterms:modified></cp:coreProperties>')
    them_phan(phan, 'docProps/core.xml', core, 'application/vnd.openxmlformats-package.core-properties+xml', 'core-properties', chu='', rid='rId6')
    phan['_rels/.rels'] = phan['_rels/.rels'].replace(R + '/core-properties', 'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties')
    app = (f'<Properties xmlns="{EP}" xmlns:vt="{VT}"><Template>Normal.dotm</Template><Manager>Quản lý DEMO</Manager>'
           '<Company>Công ty DEMO Ánh Dương</Company><Pages>1</Pages><Words>100</Words><Characters>500</Characters>'
           '<Application>Microsoft Office Word</Application><DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop>'
           '<HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Title</vt:lpstr></vt:variant>'
           '<vt:variant><vt:i4>1</vt:i4></vt:variant></vt:vector></HeadingPairs>'
           '<TitlesOfParts><vt:vector size="1" baseType="lpstr"><vt:lpstr>Tựa DEMO</vt:lpstr></vt:vector></TitlesOfParts>'
           '<LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinkBase/>'
           '<HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion></Properties>')
    them_phan(phan, 'docProps/app.xml', app, CT_CHUNG + 'extended-properties+xml', 'extended-properties', chu='', rid='rId7')
    custom = (f'<Properties xmlns="{CUSTOM}" xmlns:vt="{VT}">'
              f'<property fmtid="{FMTID}" pid="2" name="Tên DEMO &amp; X"><vt:lpwstr>Giá trị DEMO</vt:lpwstr></property>'
              f'<property fmtid="{FMTID}" pid="3" name="Số tiền DEMO (VND)"><vt:i4>1000000</vt:i4></property></Properties>')
    them_phan(phan, 'docProps/custom.xml', custom, CT_CHUNG + 'custom-properties+xml', 'custom-properties', chu='', rid='rId8')
    styles = (f'<w:styles xmlns:w="{W}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr></w:rPrDefault></w:docDefaults>'
              '<w:latentStyles w:defLockedState="0" w:defUIPriority="99" w:defSemiHidden="1" w:defUnhideWhenUsed="1" w:defQFormat="0" w:count="1">'
              '<w:lsdException w:name="Tên kiểu DEMO" w:semiHidden="0" w:uiPriority="0" w:unhideWhenUsed="0" w:qFormat="1"/></w:latentStyles>'
              '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
              '<w:style w:type="character" w:styleId="Emphasis"><w:name w:val="Kiểu DEMO nghiêng"/><w:rPr><w:i/></w:rPr></w:style>'
              '<w:style w:type="character" w:styleId="Strong"><w:name w:val="Kiểu DEMO đậm ẩn"/><w:rPr><w:b/><w:vanish/></w:rPr></w:style></w:styles>')
    them_phan(phan, 'word/styles.xml', styles, CT_W + 'styles+xml', 'styles', rid='rId9')
    numbering = (f'<w:numbering xmlns:w="{W}"><w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>'
                 '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="Mục DEMO %1"/></w:lvl></w:abstractNum>'
                 '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>')
    them_phan(phan, 'word/numbering.xml', numbering, CT_W + 'numbering+xml', 'numbering', rid='rId10')
    settings = (f'<w:settings xmlns:w="{W}"><w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/>'
                '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
                '<w:rsids><w:rsidRoot w:val="1234ABCD"/><w:rsid w:val="01234567"/></w:rsids></w:settings>')
    them_phan(phan, 'word/settings.xml', settings, CT_W + 'settings+xml', 'settings', rid='rId11')
    fonts = f'<w:fonts xmlns:w="{W}"><w:font w:name="Calibri"><w:panose1 w:val="020F0502020204030204"/><w:family w:val="swiss"/><w:pitch w:val="variable"/></w:font></w:fonts>'
    them_phan(phan, 'word/fontTable.xml', fonts, CT_W + 'fontTable+xml', 'fontTable', rid='rId12')
    them_phan(phan, 'word/webSettings.xml', f'<w:webSettings xmlns:w="{W}"><w:optimizeForBrowser/><w:allowPNG/></w:webSettings>', CT_W + 'webSettings+xml', 'webSettings', rid='rId13')
    them_phan(phan, 'word/theme/theme1.xml', theme_demo(), CT_CHUNG + 'theme+xml', 'theme', rid='rId14', dich='theme/theme1.xml')
    return phan


def zip_office(phan, *, co=6, descriptor=False, chu_ky=True, local_day_du=False):
    """General purpose 0x0006; descriptor 12/16 bytes, ZIP cổ điển độc lập."""
    local, central = bytearray(), bytearray()
    flags = co | (8 if descriptor else 0)
    for ten, text in phan.items():
        name = ten.encode('utf-8')
        raw = text.encode() if isinstance(text, str) else text
        data = nen_raw(raw)
        crc, size, n = zlib.crc32(raw), len(raw), len(data)
        offset = len(local)
        ls = (crc, n, size) if not descriptor or local_day_du else (0, 0, 0)
        local.extend(struct.pack('<4s5H3I2H', b'PK\x03\x04', 20, flags, 8, 0, 0x21, *ls, len(name), 0))
        local.extend(name)
        local.extend(data)
        if descriptor:
            if chu_ky:
                local.extend(b'PK\x07\x08')
            local.extend(struct.pack('<3I', crc, n, size))
        central.extend(struct.pack('<4s6H3I5H2I', b'PK\x01\x02', 20, 20, flags, 8, 0, 0x21,
                                   crc, n, size, len(name), 0, 0, 0, 0, 0x20, offset))
        central.extend(name)
    return bytes(local + central + struct.pack('<4s4H2IH', b'PK\x05\x06', 0, 0, len(phan), len(phan), len(central), len(local), 0))
