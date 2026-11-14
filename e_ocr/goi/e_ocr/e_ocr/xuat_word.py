"""Dựng DOCX trong bộ nhớ từ van_ban_tai_lieu, không nhận dạng lại.

Chuyển quy tắc ô gốc/ô phủ và gridSpan/vMerge của ma-nguon/bang.py,
vendor/mask_ocr/layout.py sang chiều xuất. Bản vendor trong repo chỉ có
parser, không có bộ ghi Word; phần đóng gói OOXML dùng thư viện chuẩn.
"""

import io
import math
import re
from xml.etree import ElementTree as ET
import zipfile

from kho_tri_thuc_sdk.engine import LoiNghiepVu


MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
XML = "{http://www.w3.org/XML/1998/namespace}"
_KY_TU_CAM = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]")


def _loi():
    return LoiNghiepVu(
        "CAU_TRUC_WORD_KHONG_HOP_LE",
        "Không thể giữ đầy đủ bố cục tài liệu khi xuất Word. Hãy kiểm tra lại kết quả nhận dạng.",
    )


def _nut(cha, ten, **thuoc_tinh):
    return ET.SubElement(cha, W + ten, {W + k: str(v) for k, v in thuoc_tinh.items()})


def _twip(so):
    return str(round(so * 20))


def _so(so):
    if type(so) not in (int, float) or not math.isfinite(so):
        raise _loi()
    return so


def _hop(hop, rong, cao):
    if not isinstance(hop, (list, tuple)) or len(hop) != 4:
        raise _loi()
    x0, y0, x1, y1 = map(_so, hop)
    if not (0 <= x0 < x1 <= rong and 0 <= y0 < y1 <= cao):
        raise _loi()
    return x0, y0, x1, y1


def _chu(chu):
    # Tab và xuống dòng được ghi thành phần tử OOXML; không lọc/cắt ký tự.
    if not isinstance(chu, str) or _KY_TU_CAM.search(chu):
        raise _loi()
    return chu


def _doan(cha, chu="", hop=None):
    p = _nut(cha, "p")
    pr = _nut(p, "pPr")
    if hop is not None:
        x0, y0, x1, _ = hop
        _nut(pr, "framePr", w=_twip(x1 - x0), x=_twip(x0), y=_twip(y0),
             hAnchor="page", vAnchor="page", wrap="none")
    _nut(pr, "spacing", before=0, after=0)
    run = _nut(p, "r")
    rpr = _nut(run, "rPr")
    _nut(rpr, "rFonts", ascii="Arial", hAnsi="Arial", eastAsia="Arial", cs="Arial")
    _nut(rpr, "sz", val=20)
    for phan in re.split(r"(\t|\r\n|\r|\n)", chu):
        if phan == "\t":
            _nut(run, "tab")
        elif phan in ("\r\n", "\r", "\n"):
            _nut(run, "br")
        elif phan:
            t = _nut(run, "t")
            t.set(XML + "space", "preserve")
            t.text = phan
    return p


def _luoi(bang, rong, cao, kiem_huy):
    hop = _hop(bang["hop"], rong, cao)
    cells = bang["o"]
    if not isinstance(cells, list) or not cells:
        raise _loi()
    occupied, rows, cols = {}, 0, 0
    for cell in cells:
        kiem_huy()
        r, c, rs, cs = (cell[k] for k in ("hang", "cot", "gop_hang", "gop_cot"))
        if any(type(v) is not int for v in (r, c, rs, cs)) or min(r, c) < 0 or min(rs, cs) < 1:
            raise _loi()
        if r + rs > 100 or c + cs > 40:
            raise LoiNghiepVu("BANG_QUA_LON", "Bảng vượt 100 hàng hoặc 40 cột. Hãy chia nhỏ tài liệu.")
        _chu(cell["van_ban"])
        for y in range(r, r + rs):
            for x in range(c, c + cs):
                if (y, x) in occupied:
                    raise _loi()
                occupied[y, x] = cell
        rows, cols = max(rows, r + rs), max(cols, c + cs)
    if len(occupied) != rows * cols:
        # Không tự lấp ô thiếu: ô trống phải hiện diện trong cấu trúc nguồn.
        raise _loi()

    def bien(truc, dem):
        start, end = (hop[0], hop[2]) if truc == "cot" else (hop[1], hop[3])
        spans = "gop_cot" if truc == "cot" else "gop_hang"
        a, b = (0, 2) if truc == "cot" else (1, 3)
        points = {0: start, dem: end}
        for cell in cells:
            if "hop" not in cell:
                continue
            box = _hop(cell["hop"], rong, cao)
            if not (hop[0] <= box[0] < box[2] <= hop[2] and hop[1] <= box[1] < box[3] <= hop[3]):
                raise _loi()
            for index, value in ((cell[truc], box[a]), (cell[truc] + cell[spans], box[b])):
                if index in points and abs(points[index] - value) > 0.05:
                    raise _loi()
                points[index] = value
        # Schema không bắt buộc tọa độ từng ô. Chỉ chia đều khoảng chưa có mốc.
        known = sorted(points)
        for left, right in zip(known, known[1:]):
            for index in range(left + 1, right):
                points[index] = points[left] + (points[right] - points[left]) * (index - left) / (right - left)
        values = [round(points[i] * 20) for i in range(dem + 1)]
        if any(b <= a for a, b in zip(values, values[1:])):
            raise _loi()
        return [b - a for a, b in zip(values, values[1:])]

    return hop, occupied, rows, cols, bien("cot", cols), bien("hang", rows)


def _bang(cha, bang, rong, cao, kiem_huy):
    hop, occupied, rows, cols, widths, heights = _luoi(bang, rong, cao, kiem_huy)
    tbl = _nut(cha, "tbl")
    pr = _nut(tbl, "tblPr")
    _nut(pr, "tblpPr", horzAnchor="page", vertAnchor="page", tblpX=_twip(hop[0]),
         tblpY=_twip(hop[1]), leftFromText=0, rightFromText=0, topFromText=0, bottomFromText=0)
    _nut(pr, "tblW", w=sum(widths), type="dxa")
    borders = _nut(pr, "tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        _nut(borders, side, val="single", sz=4, color="auto")
    _nut(pr, "tblLayout", type="fixed")
    grid = _nut(tbl, "tblGrid")
    for width in widths:
        _nut(grid, "gridCol", w=width)
    for r in range(rows):
        kiem_huy()
        tr = _nut(tbl, "tr")
        trpr = _nut(tr, "trPr")
        _nut(trpr, "cantSplit")
        # atLeast để Word không cắt mất chữ nếu font/thước dòng khác nguồn.
        _nut(trpr, "trHeight", val=heights[r], hRule="atLeast")
        c = 0
        while c < cols:
            cell = occupied[r, c]
            cs = cell["gop_cot"]
            tc = _nut(tr, "tc")
            tcpr = _nut(tc, "tcPr")
            _nut(tcpr, "tcW", w=sum(widths[c:c + cs]), type="dxa")
            if cs > 1:
                _nut(tcpr, "gridSpan", val=cs)
            if cell["gop_hang"] > 1:
                _nut(tcpr, "vMerge", val="restart" if r == cell["hang"] else "continue")
            _doan(tc, cell["van_ban"] if r == cell["hang"] else "")
            c += cs


def _phan_trang(cha, trang, *, cuoi):
    if cuoi:
        sect = _nut(cha, "sectPr")
    else:
        sect = _nut(_nut(_nut(cha, "p"), "pPr"), "sectPr")
    _nut(sect, "type", val="nextPage")
    attrs = {"w": _twip(trang["rong"]), "h": _twip(trang["cao"])}
    if trang["rong"] > trang["cao"]:
        attrs["orient"] = "landscape"
    _nut(sect, "pgSz", **attrs)
    _nut(sect, "pgMar", top=0, right=0, bottom=0, left=0, header=0, footer=0, gutter=0)


def _khong_huy():
    pass


def dung_docx(tai_lieu, *, kiem_huy=_khong_huy):
    """Giữ ô gốc, văn bản, tọa độ bảng (point) và phân trang nguồn.

    Từ chối cấu trúc thiếu/chồng ô hoặc đơn vị chưa hỗ trợ; không sửa ngầm.
    Word có thể dàn lại chữ theo font máy, không cam kết khớp từng pixel.
    """
    kiem_huy()
    try:
        pages = tai_lieu["trang"]
        if tai_lieu["phien_ban"] != 1 or not isinstance(pages, list) or not pages:
            raise _loi()
        if len(pages) > 60:
            raise LoiNghiepVu("QUA_SO_TRANG", "Tài liệu vượt 60 trang. Hãy chia thành các tệp nhỏ hơn.")
        if tai_lieu["so_trang"] != len(pages):
            raise _loi()
        if any(type(p["so"]) is not int or p["so"] < 1 for p in pages):
            raise _loi()
        if len({p["so"] for p in pages}) != len(pages):
            raise _loi()
        root = ET.Element(W + "document")
        body = _nut(root, "body")
        total = 0
        for index, page in enumerate(sorted(pages, key=lambda p: p["so"])):
            kiem_huy()
            rong, cao = _so(page["rong"]), _so(page["cao"])
            if page["don_vi"] != "pt" or not (0 < rong <= 1584 and 0 < cao <= 1584):
                raise _loi()
            for block in page["khoi"]:
                kiem_huy()
                if block["loai"] == "doan":
                    chu = _chu(block["van_ban"])
                    _doan(body, chu, _hop(block["hop"], rong, cao))
                    total += len(chu)
                elif block["loai"] == "bang":
                    _bang(body, block, rong, cao, kiem_huy)
                    _doan(body)
                    total += sum(len(cell["van_ban"]) for cell in block["o"])
                else:
                    raise _loi()
                if total > 500_000:
                    raise LoiNghiepVu("QUA_DO_DAI", "Nội dung vượt giới hạn xuất Word. Hãy chia nhỏ tài liệu.")
            # Đoạn neo sau bảng cũng phân cách hai bảng liền nhau.
            _doan(body)
            _phan_trang(body, page, cuoi=index == len(pages) - 1)
    except (KeyError, TypeError, ValueError, OverflowError):
        raise _loi() from None
    kiem_huy()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", (
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>'
        ))
        archive.writestr("_rels/.rels", (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/></Relationships>'
        ))
        archive.writestr("word/document.xml", ET.tostring(root, encoding="utf-8", xml_declaration=True))
    kiem_huy()
    return output.getvalue()
