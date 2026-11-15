"""Sinh fixture DOCX DEMO xác định bằng thư viện chuẩn; không cần Word."""

import io
from pathlib import Path
import zipfile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT = """<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
REL = """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
NUM = f"""<w:numbering xmlns:w="{W_NS}">
<w:abstractNum w:abstractNumId="0">
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="Điều %1."/></w:lvl>
<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1.%2."/></w:lvl>
</w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
<w:num w:numId="2"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""


def p(chu="", pr=""):
    from xml.sax.saxutils import escape
    return f"<w:p>{pr}<w:r><w:t xml:space=\"preserve\">{escape(chu)}</w:t></w:r></w:p>"


def so(chu, nid=1, muc=0):
    return p(chu, f'<w:pPr><w:numPr><w:ilvl w:val="{muc}"/><w:numId w:val="{nid}"/></w:numPr></w:pPr>')


def o(chu="", pr=""):
    return f"<w:tc><w:tcPr>{pr}</w:tcPr>{p(chu)}</w:tc>"


def bang_demo():
    return ("<w:tbl><w:tblGrid><w:gridCol/><w:gridCol/><w:gridCol/></w:tblGrid>"
            "<w:tr>" + o("Hạng mục DEMO") + o("") + o("1.000.000 VND") + "</w:tr>"
            "<w:tr>" + o("Ô gộp DEMO", '<w:gridSpan w:val="2"/><w:vMerge w:val="restart"/>')
            + o("2026-10-30") + "</w:tr>"
            "<w:tr>" + o("", '<w:gridSpan w:val="2"/><w:vMerge/>') + o("")
            + "</w:tr></w:tbl>")


def goi_docx(noi_dung=None, *, numbering=None, styles=None, them=None, raw_xml=None,
             nen=zipfile.ZIP_DEFLATED, alias="w"):
    noi_dung = p("DEMO — DỮ LIỆU GIẢ, KHÔNG CÓ GIÁ TRỊ GIAO DỊCH.") if noi_dung is None else noi_dung
    xml = raw_xml if raw_xml is not None else f'<w:document xmlns:w="{W_NS}"><w:body>{noi_dung}</w:body></w:document>'
    if alias != "w":
        xml = xml.replace("w:", alias + ":").replace("xmlns:w=", "xmlns:" + alias + "=")
    ds = {"[Content_Types].xml": CT, "_rels/.rels": REL, "word/document.xml": xml}
    if numbering is not None:
        ds["word/numbering.xml"] = numbering
    if styles is not None:
        ds["word/styles.xml"] = styles
    ds.update(them or {})
    f = io.BytesIO()
    with zipfile.ZipFile(f, "w") as z:
        for ten, v in ds.items():
            i = zipfile.ZipInfo(ten, date_time=(2026, 10, 30, 0, 0, 0))
            i.compress_type = nen
            z.writestr(i, v.encode("utf-8") if isinstance(v, str) else v)
    return f.getvalue()


def mau_thuong():
    return goi_docx(p("DEMO — DỮ LIỆU GIẢ, KHÔNG CÓ GIÁ TRỊ GIAO DỊCH.")
                   + p("Công ty DEMO Ánh Dương") + so("Giá trị hợp đồng DEMO")
                   + so("Giá trị là 1.000.000 VND, ngày ký 2026-10-30.", muc=1)
                   + bang_demo() + so("Thanh toán DEMO") + p("Kết thúc DEMO."), numbering=NUM)


def mau_track():
    return goi_docx(p("DEMO — DỮ LIỆU GIẢ, KHÔNG CÓ GIÁ TRỊ GIAO DỊCH.")
                   + '<w:p><w:del w:id="1"><w:r><w:delText>Giá trị DEMO cũ</w:delText></w:r></w:del>'
                   + '<w:ins w:id="2"><w:r><w:t>Giá trị DEMO mới: 1.000.000 VND.</w:t></w:r></w:ins></w:p>',
                   alias="x")


if __name__ == "__main__":
    demo = Path(__file__).resolve().parents[1] / "goi/e_trich_xuat/demo"
    demo.mkdir(parents=True, exist_ok=True)
    (demo / "DEMO-hop-dong.docx").write_bytes(mau_thuong())
    (demo / "DEMO-track-changes.docx").write_bytes(mau_track())
