"""Chuyen parser DOCX tu mask_ocr; PDF dung lop chu SDK 2.0 da co.

Khong nhap MuPDF, model hay runtime worker cu. OCR anh do caller cung cap.
"""
import io
import posixpath
import re
import zipfile
from pathlib import Path

from . import common as ET
from .common import Extracted, ExtractionError, normalize

MAX_BYTES = 20 * 1024**2
MAX_TEXT = 500_000
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def image_text(data):
    raise ExtractionError("Chưa cấp bộ đọc Tesseract cho ảnh nhúng trong DOCX.")


def paragraph_text(node) -> str:
    parts = []
    for el in node.iter():
        if el.tag == W + "t":
            parts.append(el.text or "")
        elif el.tag == W + "tab":
            parts.append("\t")
        elif el.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def word_blocks(node) -> list[str]:
    result = []
    for child in node:
        if child.tag == W + "p":
            result.append(paragraph_text(child))
        elif child.tag == W + "tbl":
            # The blank separator keeps adjacent Word tables distinct on export.
            result.append("")
            for row in child.findall(W + "tr"):
                cells = []
                for cell in row.findall(W + "tc"):
                    if cell.find(".//" + W + "tbl") is not None:
                        raise ExtractionError("Word có bảng lồng bảng. Hãy chuyển sang PDF để duyệt bố cục.")
                    cells.append(" / ".join(word_blocks(cell)).replace("\t", " ").replace("\n", " / ").strip())
                result.append("\t".join(cells))
            result.append("")
        elif child.tag not in {W + "sectPr", W + "tcPr", W + "sdtPr"}:
            result.extend(word_blocks(child))
    return result


def extract_docx(data: bytes, image_reader=None) -> Extracted:
    if not 0 < len(data) <= MAX_BYTES:
        raise ExtractionError("DOCX rỗng hoặc vượt 20 MiB.")
    warnings = ["Bố cục đã đơn giản hóa; ảnh/logo/chữ ký không đi theo bản xuất. Chữ OCR từ ảnh được đưa riêng ở cuối."]
    pieces = []
    images: set[str] = set()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        names = {e.filename for e in entries}
        if len(entries) > 3000 or len(names) != len(entries) or sum(e.file_size for e in entries) > 80 * 1024**2:
            raise ExtractionError("Cấu trúc DOCX quá lớn hoặc bất thường.")
        if not {"[Content_Types].xml", "word/document.xml"}.issubset(names):
            raise ExtractionError("File không phải DOCX hợp lệ.")
        roots = {}
        for entry in entries:
            name = entry.filename
            if entry.flag_bits & 1 or name.startswith("/") or ".." in name.split("/") or "\\" in name:
                raise ExtractionError("DOCX mã hóa hoặc có cấu trúc không hợp lệ.")
            if any(s in name.lower() for s in ("vbaproject", "activex", "embeddings/", "word/charts/", "word/diagrams/")):
                raise ExtractionError("Word chứa macro/đối tượng nhúng/biểu đồ/SmartArt chưa hỗ trợ. Hãy xuất PDF trước.")
            if name.endswith((".xml", ".rels")):
                if entry.file_size > 15 * 1024**2:
                    raise ExtractionError("Thành phần Word quá lớn.")
                roots[name] = ET.fromstring(archive.read(entry))
        for name, root in roots.items():
            for el in root.iter():
                tag = el.tag.rsplit("}", 1)[-1]
                if tag in {"ins", "del", "moveFrom", "moveTo"} and name.startswith("word/"):
                    raise ExtractionError("Word có Track Changes. Hãy chấp nhận/từ chối thay đổi rồi lưu bản DOCX sạch.")
                if tag in {"altChunk", "object", "oMath", "oMathPara"}:
                    raise ExtractionError("Word chứa nội dung chưa đọc được đầy đủ. Hãy chuyển sang PDF trước.")
        content_parts = ["word/document.xml"] + sorted(
            n for n in names if re.fullmatch(r"word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml", n)
        )
        for part in content_parts:
            root = roots[part]
            if part == "word/document.xml":
                body = root.find(W + "body")
                if body is None:
                    raise ExtractionError("DOCX không có nội dung chính hợp lệ.")
                lines = word_blocks(body)
            else:
                lines = word_blocks(root)
            if lines:
                if part != "word/document.xml":
                    pieces.append("\n[Phần đầu/cuối trang hoặc chú thích]")
                pieces.extend(lines)
            relpath = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
            relationships = {el.attrib.get("Id"): el.attrib for el in roots.get(relpath, [])}
            for el in root.iter():
                tag = el.tag.rsplit("}", 1)[-1]
                if tag not in {"blip", "imagedata"}:
                    continue
                rid = el.attrib.get(R + "embed") or el.attrib.get(R + "id") or el.attrib.get(R + "link")
                rel = relationships.get(rid)
                if not rel or rel.get("TargetMode", "").lower() == "external":
                    raise ExtractionError("Word có ảnh liên kết ngoài hoặc ảnh lỗi. Hãy nhúng ảnh vào file hoặc xuất PDF.")
                target = posixpath.normpath(posixpath.join(posixpath.dirname(part), rel.get("Target", "")))
                if target not in names or not target.startswith("word/media/"):
                    raise ExtractionError("Không xác định được ảnh nhúng trong Word.")
                images.add(target)
        if "word/comments.xml" in names:
            warnings.append("Comments đã được loại khỏi bản xuất. Nếu chứa nội dung cần phân tích, hãy đưa vào phần chính trước.")
        if any(el.tag in {W + "gridSpan", W + "vMerge"} for root in roots.values() for el in root.iter()):
            warnings.append("Có ô gộp trong Word: kiểm tra lại sự tương ứng giữa tiêu đề cột và số liệu.")
        if any(el.tag == W + "vanish" for root in roots.values() for el in root.iter()):
            warnings.append("Có thuộc tính chữ ẩn trong Word. Nội dung đọc được vẫn được đưa ra để kiểm tra.")
        if any(el.tag == W + "instrText" for root in roots.values() for el in root.iter()):
            warnings.append("Word có trường động: chỉ giữ giá trị đang lưu, không cập nhật liên kết hay công thức.")
        for index, name in enumerate(sorted(images), 1):
            text = (image_reader or image_text)(archive.read(name))
            pieces.append(f"\n[Chữ từ ảnh nhúng {index} — cần đối chiếu]\n{text or '(Không nhận được chữ; hình ảnh bị loại khỏi bản xuất.)'}")
        if images:
            warnings.append("OCR ảnh có thể sai hoặc thiếu chữ/số. Đối chiếu nội dung ảnh trước khi duyệt.")
    return Extracted(normalize("\n".join(pieces)).strip(), warnings, len(images))



def extract(data: bytes, filename: str, *, image_reader=None, kiem_huy=lambda: None) -> Extracted:
    """Doc chu san va bang; DOCX chua khai them trong phieu API cua engine."""
    if not 0 < len(data) <= MAX_BYTES:
        raise ExtractionError("Tài liệu rỗng hoặc vượt 20 MiB.")
    kiem_huy()
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        from ...lop_chu import doc_lop_chu
        result = doc_lop_chu(data, kiem_huy=kiem_huy)
        return Extracted(result.text, result.warnings, 0, result.pages)
    if suffix != ".docx":
        raise ExtractionError("Bộ đọc văn bản có sẵn chỉ nhận PDF hoặc DOCX.")
    result = extract_docx(data, image_reader=image_reader)
    if not result.text.strip() or len(result.text) > MAX_TEXT:
        raise ExtractionError("DOCX không có nội dung đọc được hoặc vượt giới hạn văn bản.")
    from .layout import word_layout
    result.pages = [word_layout(data, result)]
    kiem_huy()
    return result
