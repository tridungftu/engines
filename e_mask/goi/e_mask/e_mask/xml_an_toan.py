"""XML stdlib không tin cậy; ngân sách dùng chung cho toàn gói MASK-B1.

Chép có sửa bộ dựng cây có trần của mẫu DOCX; Expat kiểm cú pháp thật,
không tiền xử lý bằng biểu thức tìm kiếm hoặc tải tài nguyên ngoài.
"""

from dataclasses import dataclass
import xml.etree.ElementTree as ET
from xml.parsers import expat

from .zip_an_toan import PHAN_TOI_DA, _sai, _vuot

DO_SAU_TOI_DA = 64
SO_NUT_TOI_DA = 100000
SO_SHEET_TOI_DA = 50
SO_O_TOI_DA = 20000
KY_TU_VAO_TOI_DA = 500000

# URI là định danh XML, không phải địa chỉ để truy cập.
GOC_NS = "http" + "://schemas.openxmlformats.org/"
W_NS = GOC_NS + "wordprocessingml/2006/main"
S_NS = GOC_NS + "spreadsheetml/2006/main"
R_NS = GOC_NS + "officeDocument/2006/relationships"
CT_NS = GOC_NS + "package/2006/content-types"
REL_NS = GOC_NS + "package/2006/relationships"
CP_NS = GOC_NS + "package/2006/metadata/core-properties"
EP_NS = GOC_NS + "officeDocument/2006/extended-properties"
CUSTOM_NS = GOC_NS + "officeDocument/2006/custom-properties"
VT_NS = GOC_NS + "officeDocument/2006/docPropsVTypes"
XML_NS = "http" + "://www.w3.org/XML/1998/namespace"
DC_NS = "http" + "://purl.org/dc/elements/1.1/"
DCT_NS = "http" + "://purl.org/dc/terms/"
XSI_NS = "http" + "://www.w3.org/2001/XMLSchema-instance"
A_NS = GOC_NS + "drawingml/2006/main"

_TIEN_TO = {
    W_NS: {"", "w"}, S_NS: {"", "s", "x"}, R_NS: {"r"},
    CT_NS: {"", "ct"}, REL_NS: {"", "pr"}, CP_NS: {"", "cp"},
    EP_NS: {"", "ep"}, CUSTOM_NS: {"", "cust"}, VT_NS: {"vt"},
    XML_NS: {"xml"}, DC_NS: {"dc"}, DCT_NS: {"dcterms"},
    XSI_NS: {"xsi"}, A_NS: {"", "a"},
}


@dataclass
class NganSachXML:
    so_nut: int = 0
    so_ky_tu: int = 0
    so_sheet: int = 0
    so_o: int = 0

    def them_chu(self, so):
        self.so_ky_tu += so
        if self.so_ky_tu > KY_TU_VAO_TOI_DA:
            _vuot()


class _BoDungCay:
    def __init__(self, namespace, ngan_sach, kiem_huy):
        self.cay = ET.TreeBuilder()
        self.namespace = frozenset(namespace)
        self.ngan_sach = ngan_sach
        self.kiem_huy = kiem_huy
        self.sau = 0

    def _ten(self, ten, *, thuoc_tinh=False):
        if "}" not in ten:
            if not thuoc_tinh:
                _sai()
            return ten
        ns, local = ten.rsplit("}", 1)
        if ns not in self.namespace:
            _sai()
        return "{" + ns + "}" + local

    def khai_namespace(self, prefix, uri):
        self.kiem_huy()
        if uri not in self.namespace or (prefix or "") not in _TIEN_TO.get(uri, set()):
            _sai()

    def start(self, ten, thuoc_tinh):
        self.kiem_huy()
        self.sau += 1
        ns = self.ngan_sach
        ns.so_nut += 1
        if self.sau > DO_SAU_TOI_DA or ns.so_nut > SO_NUT_TOI_DA:
            _vuot()
        ten = self._ten(ten)
        if ten == "{" + S_NS + "}sheet":
            ns.so_sheet += 1
            if ns.so_sheet > SO_SHEET_TOI_DA:
                _vuot()
        if ten == "{" + S_NS + "}c":
            ns.so_o += 1
            if ns.so_o > SO_O_TOI_DA:
                _vuot()
        attrs = {}
        for khoa, gia_tri in thuoc_tinh.items():
            # B1 đếm bảo thủ cả text/tail và giá trị attribute, không preview.
            ns.them_chu(len(gia_tri))
            attrs[self._ten(khoa, thuoc_tinh=True)] = gia_tri
        return self.cay.start(ten, attrs)

    def end(self, ten):
        self.sau -= 1
        return self.cay.end(self._ten(ten))

    def data(self, chu):
        self.kiem_huy()
        self.ngan_sach.them_chu(len(chu))
        self.cay.data(chu)


def _cam(*args):
    _sai()


def _khai_xml(phien_ban, encoding, doc_lap):
    # XML declaration hợp lệ là sự kiện riêng, không phải PI.
    if phien_ban != "1.0" or (encoding and encoding.casefold() not in {
            "utf-8", "utf-16", "utf-16le", "utf-16be"}):
        _sai()


def doc_xml(raw, *, namespace, ngan_sach, kiem_huy):
    """Bytes → cây nội bộ sau kiểm; không giữ parser hoặc dữ liệu ngoài việc."""
    if type(raw) is not bytes:
        _sai()
    if len(raw) > PHAN_TOI_DA:
        _vuot()
    kiem_huy()
    dung = _BoDungCay(namespace, ngan_sach, kiem_huy)
    parser = expat.ParserCreate(namespace_separator="}")
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    parser.StartElementHandler = dung.start
    parser.EndElementHandler = dung.end
    parser.CharacterDataHandler = dung.data
    parser.StartNamespaceDeclHandler = dung.khai_namespace
    parser.XmlDeclHandler = _khai_xml
    parser.StartDoctypeDeclHandler = _cam
    parser.EntityDeclHandler = _cam
    parser.UnparsedEntityDeclHandler = _cam
    parser.ExternalEntityRefHandler = _cam
    parser.SkippedEntityHandler = _cam
    parser.ProcessingInstructionHandler = _cam
    # Comment có thể mang định danh ngoài reader: ngoài profile thì từ chối.
    parser.CommentHandler = _cam
    try:
        for pos in range(0, len(raw), 8192):
            kiem_huy()
            try:
                parser.Parse(raw[pos:pos + 8192], False)
            except expat.ExpatError:
                _sai()
        kiem_huy()
        try:
            parser.Parse(b"", True)
        except expat.ExpatError:
            _sai()
        kiem_huy()
        return dung.cay.close()
    finally:
        # Gỡ callback đóng vòng tham chiếu, cả khi parser/hủy từ chối giữa tệp.
        parser.StartElementHandler = None
        parser.EndElementHandler = None
        parser.CharacterDataHandler = None
        parser.StartNamespaceDeclHandler = None
        parser = None
