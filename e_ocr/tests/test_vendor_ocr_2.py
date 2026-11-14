"""Vendor mask_ocr: PDF/DOCX DEMO, không tải model hoặc gọi dịch vụ."""

import io
from pathlib import Path
import zipfile

import pytest

from demo.tao_pdf import DONG_DEMO, pdf_demo
from e_ocr.vendor.mask_ocr import ExtractionError, extract


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def docx_demo(*, xml=None):
    if xml is None:
        xml = f'''<w:document xmlns:w="{W}"><w:body>
<w:p><w:r><w:t>Công ty DEMO Ánh Dương</w:t></w:r></w:p>
<w:tbl><w:tblGrid><w:gridCol w:w="2000"/><w:gridCol w:w="2000"/><w:gridCol w:w="2000"/></w:tblGrid>
<w:tr><w:tc><w:tcPr><w:gridSpan w:val="3"/></w:tcPr><w:p><w:r><w:t>BẢNG DEMO</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:tcPr><w:vMerge w:val="restart"/></w:tcPr><w:p><w:r><w:t>DEMO</w:t></w:r></w:p></w:tc>
<w:tc><w:p><w:r><w:t>1.000.000 VND</w:t></w:r></w:p></w:tc><w:tc><w:p/></w:tc></w:tr>
<w:tr><w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p/></w:tc><w:tc><w:p><w:r><w:t>30/10/2026</w:t></w:r></w:p></w:tc><w:tc><w:p/></w:tc></w:tr>
</w:tbl><w:p><w:r><w:t>KẾT DEMO</w:t></w:r></w:p></w:body></w:document>'''
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("word/document.xml", xml)
    return data.getvalue()


def test_docx_giu_o_rong_gop_hang_gop_cot_va_thu_tu():
    result = extract(docx_demo(), "DEMO.docx")
    assert all(s in result.text for s in ("Công ty DEMO Ánh Dương", "1.000.000 VND", "30/10/2026"))
    page, = result.pages
    assert [b["type"] for b in page["blocks"]] == ["paragraph", "table", "paragraph"]
    bang = page["blocks"][1]
    assert (bang["rows"], bang["cols"]) == (3, 3)
    assert len(bang["cells"]) == 6
    assert bang["cells"][0]["colspan"] == 3
    assert bang["cells"][1]["rowspan"] == 2
    assert [(c["row"], c["col"]) for c in bang["cells"] if not c["unit_ids"]] == [(1, 2), (2, 2)]


def test_vendor_pdf_co_chu_giu_bang_va_o_rong():
    result = extract(pdf_demo(DONG_DEMO, bang=True), "DEMO.pdf")
    assert result.ocr_pages == 0
    bang, = [k for k in result.pages[0]["khoi"] if k["loai"] == "bang"]
    assert len(bang["o"]) == 7 and bang["o"][0]["gop_cot"] == 3
    assert len([c for c in bang["o"] if c["van_ban"] == ""]) == 2


@pytest.mark.parametrize("declaration", [
    '<!DOCTYPE document [<!ENTITY demo "DEMO">]>',
    '<!DOCTYPE document SYSTEM "file:///DEMO-khong-doc">',
])
def test_docx_tu_choi_dtd_va_entity_truoc_khi_doc(declaration):
    xml = f'{declaration}<w:document xmlns:w="{W}"><w:body><w:p/></w:body></w:document>'
    with pytest.raises(ExtractionError, match="XML"):
        extract(docx_demo(xml=xml), "DEMO.docx")


def test_vendor_khong_dong_runtime_model_ngoai_pham_vi():
    goc = Path(__file__).resolve().parents[1] / "goi/e_ocr/e_ocr/vendor/mask_ocr"
    assert {p.name for p in goc.iterdir()} == {"__init__.py", "common.py", "extraction.py", "layout.py", "LICENSE"}
    assert "phần mềm nội bộ, dùng nội bộ tập đoàn" in (goc / "LICENSE").read_text(encoding="utf-8")
