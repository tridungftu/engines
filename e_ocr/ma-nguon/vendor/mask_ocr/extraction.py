from __future__ import annotations

import io
import posixpath
import re
import threading
import unicodedata
import zipfile
from pathlib import Path

import pymupdf
from defusedxml import ElementTree as ET

from .common import Extracted, ExtractionError, normalize

MODEL_DIR = Path(__file__).parent / "models"
MAX_BYTES = 20 * 1024**2
MAX_PAGES = 60
MAX_TEXT = 500_000
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
# MuPDF is not thread safe. Serialize all parsing/OCR operations in this process.
PDF_LOCK = threading.Lock()


def prepare_pdf_rotation(pdf):
    """Preserve annotation appearances before rotating the in-memory document."""
    annotated = {page.number + 1 for page in pdf
                 if page.first_annot is not None or page.first_widget is not None}
    if any(pdf[number - 1].rotation for number in annotated):
        # remove_rotation() can misrotate annotation appearance streams.
        # Bake only in this working document; callers fetch fresh pages below.
        pdf.bake(annots=True, widgets=True)
        for number in range(len(pdf)):
            pdf.reload_page(pdf[number])
    return annotated


def normalize_pdf_rotation(page):
    """Use displayed-page coordinates without changing the visible crop.

    Work only on the document opened in RAM. MuPDF OCR returns unrotated
    coordinates; leaving /Rotate in place can reorder and even clip its text.
    """
    if not page.rotation:
        return
    crop = pymupdf.Rect(page.cropbox)
    media = pymupdf.Rect(page.mediabox)
    full = pymupdf.Rect(media.x0, 0, media.x1, media.height)
    # remove_rotation() resets CropBox when it swaps the MediaBox dimensions.
    # Map the original visible crop through the full-page rotation first.
    page.set_cropbox(full)
    rotated_crop = crop * pymupdf.Matrix(1, 0, 0, 1, -full.x0, 0) * page.rotation_matrix
    page.remove_rotation()
    page.set_cropbox(rotated_crop * pymupdf.Matrix(1, 0, 0, 1, page.mediabox.x0, 0))


def ocr_ready() -> bool:
    from .runtime import tesseract_info
    return tesseract_info()["ready"]


def require_ocr():
    from .runtime import tesseract_info
    info = tesseract_info()
    if not info["ready"]:
        raise ExtractionError("Chưa có bộ OCR tiếng Việt/Anh. Chạy setup-ocr.bat trong thư mục OCR module trước khi xử lý scan hoặc ảnh nhúng.")
    return info


def ocr_page(page, full: bool = False):
    info = require_ocr()
    if page.rect.width * page.rect.height > 2_000_000:
        raise ExtractionError("Trang quá lớn để OCR. Hãy chia hoặc giảm kích thước trang.")
    try:
        return page.get_textpage_ocr(language=info["language"], dpi=300, full=full, tessdata=info["tessdata"])
    except Exception:
        raise ExtractionError("OCR không hoàn tất. Hãy kiểm tra bộ ngôn ngữ hoặc chất lượng tài liệu.") from None


def image_text(data: bytes) -> str:
    info = require_ocr()
    try:
        image = pymupdf.Pixmap(data)
        if image.width * image.height > 20_000_000:
            raise ExtractionError("Ảnh nhúng vượt 20 triệu pixel. Hãy giảm kích thước ảnh.")
        if image.colorspace is None:
            raise ExtractionError("Ảnh nhúng có định dạng chưa được hỗ trợ. Hãy chuyển Word sang PDF.")
        if image.colorspace.n != 3:
            image = pymupdf.Pixmap(pymupdf.csRGB, image)
        if image.alpha:
            image = pymupdf.Pixmap(image, 0)
        pdf_bytes = image.pdfocr_tobytes(language=info["language"], tessdata=info["tessdata"])
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            return pdf[0].get_text(sort=True).strip()
    except ExtractionError:
        raise
    except Exception:
        raise ExtractionError("Không đọc được ảnh nhúng. Hãy chuyển tài liệu sang PDF rồi thử lại.") from None


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


def pdf_text(page, textpage=None) -> str:
    if textpage is not None:
        # Preserve rough columns by grouping words on the same baseline.
        words = sorted(page.get_text("words", textpage=textpage), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
        lines = []
        for word in words:
            center = (word[1] + word[3]) / 2
            if not lines or abs(lines[-1][0] - center) > max(3, (word[3] - word[1]) * .4):
                lines.append((center, [word]))
            else:
                lines[-1][1].append(word)
        result = []
        for _, line in lines:
            line.sort(key=lambda w: w[0])
            text = line[0][4]
            for prev, word in zip(line, line[1:]):
                text += ("\t" if word[0] - prev[2] > 22 else " ") + word[4]
            result.append(text)
        return "\n".join(result)
    tables = page.find_tables().tables
    if not tables:
        return page.get_text(sort=True)
    items = []
    boxes = []
    for table in tables:
        rows = table.extract()
        items.append((table.bbox[1], "\n".join("\t".join((v or "").replace("\n", " / ") for v in row) for row in rows)))
        boxes.append(pymupdf.Rect(table.bbox))
    # Text lines, rather than whole blocks, avoid discarding paragraphs adjacent to tables.
    for block in page.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT, sort=True)["blocks"]:
        for line in block.get("lines", []):
            rect = pymupdf.Rect(line["bbox"])
            if not any(box.contains((rect.tl + rect.br) / 2) for box in boxes):
                items.append((rect.y0, "".join(s["text"] for s in line["spans"])))
    return "\n\n".join(text for _, text in sorted(items, key=lambda item: item[0]))


MODE_LABELS = {"native": "Đọc chữ có sẵn", "regions": "OCR vùng ảnh", "full": "OCR toàn trang"}


def barcode_translation(page):
    """Decode the known Code39 symbol-font encoding, never discard identifiers."""
    mappings = {}
    for block in page.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if "Code39Barcode" in span["font"]:
                    for char in span["text"]:
                        if 0xF020 <= ord(char) <= 0xF07E:
                            mappings[ord(char)] = chr(ord(char) - 0xF000)
    return mappings


def native_quality(text):
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return False
    bad = sum(c == "\ufffd" or unicodedata.category(c) in {"Co", "Cc", "Cn"} for c in chars)
    return bad / len(chars) < .02 and any(c.isalnum() for c in chars)


def meaningful_images(page):
    # Ignore tiny placeholder pixels even when stretched over an entire page.
    return [img for img in page.get_image_info() if img["width"] >= 32 and img["height"] >= 32
            and pymupdf.Rect(img["bbox"]).get_area() >= 100]


def extract_pdf(data: bytes, force_ocr: bool = False, progress=None) -> Extracted:
    from .runtime import TesseractPool, settings, tesseract_info
    warnings = ["Bố cục PDF/bảng phục hồi theo khả năng đọc được. Đối chiếu số liệu và thứ tự cột trước khi duyệt."]
    pages, details, tasks, translations_by_page = [], [], [], {}
    cfg = settings()
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        if pdf.needs_pass or not 0 < len(pdf) <= MAX_PAGES:
            raise ExtractionError(f"PDF có mật khẩu, rỗng hoặc vượt {MAX_PAGES} trang.")
        if pdf.embfile_count():
            warnings.append("PDF có file đính kèm: không đọc và không đưa file đính kèm vào bản xuất.")
        annotated_pages = prepare_pdf_rotation(pdf)
        for index, page in enumerate(pdf, 1):
            normalize_pdf_rotation(page)
            translations = barcode_translation(page)
            native = page.get_text().translate(translations).strip()
            good_native = native_quality(native)
            mode = "full" if force_ocr or not good_native else "regions" if meaningful_images(page) else "native"
            page_warnings = []
            if mode != "native":
                text = ""
                tasks.append((index, {"page_index": index - 1, "full": mode == "full"}))
                page_warnings.append(f"Trang {index}: {MODE_LABELS[mode]}; cần đối chiếu chữ và số với bản gốc.")
                if force_ocr and good_native:
                    page_warnings.append(f"Trang {index} có lớp chữ đọc được. OCR toàn trang có thể làm giảm độ chính xác; nên thử Tự động.")
            else:
                try:
                    text = pdf_text(page)
                except Exception:
                    raise ExtractionError(f"Không đọc đầy đủ bảng ở trang {index}. Thử tùy chọn OCR toàn trang.") from None
            text = normalize(text.translate(translations)).strip()
            if translations:
                page_warnings.append(f"Trang {index}: có font mã vạch Code39; phần mã đọc được được giữ thành chữ/số. Đối chiếu mã với bản gốc.")
            if index in annotated_pages:
                page_warnings.append(f"Trang {index} có ghi chú/form: bản xuất chỉ chứa văn bản trích xuất; kiểm tra phần này với bản gốc.")
            details.append({"number": index, "text": text, "mode": mode, "warnings": page_warnings})
            translations_by_page[index] = translations
            if progress:
                progress(index, len(pdf), "Chuẩn bị danh sách trang")
            if sum(len(p["text"]) for p in details) > MAX_TEXT:
                raise ExtractionError("Nội dung quá dài. Hãy chia nhỏ tài liệu.")
    if tasks:
        info = tesseract_info(cfg)
        with TesseractPool(data, cfg, workers=min(cfg["tesseract_workers"], len(tasks))) as pool:
            for done, (number, response) in enumerate(pool.map(iter(tasks)), 1):
                if response.get("number") != number:
                    raise ExtractionError("OCR trả về sai tham chiếu trang.")
                detail = details[number - 1]
                detail["text"] = normalize(response["text"].translate(translations_by_page[number])).strip()
                detail.update(ocr_language=info["language"], tesseract_model=info["model"])
                if sum(len(p["text"]) for p in details) > MAX_TEXT:
                    raise ExtractionError("Nội dung quá dài. Hãy chia nhỏ tài liệu.")
                if progress:
                    progress(done, len(tasks), f"Tesseract {info['language']} — {info['model']}")
    for detail in details:
        number, text = detail["number"], detail["text"]
        if not text:
            detail["warnings"].append(f"Trang {number} không nhận được chữ. Xác nhận trang trống/hình ảnh không cần nội dung trước khi duyệt.")
        warnings.extend(detail["warnings"])
        pages.append(f"[Trang {number}]\n{text}")
    result_text = normalize("\n\n".join(pages))
    if len(result_text) > MAX_TEXT:
        raise ExtractionError("Nội dung quá dài. Hãy chia nhỏ tài liệu.")
    return Extracted(result_text, warnings, len(tasks), details)


def extract(data: bytes, filename: str, force_ocr: bool = False, progress=None) -> Extracted:
    if not 0 < len(data) <= MAX_BYTES:
        raise ExtractionError("Mỗi file phải từ 1 byte đến 20 MB.")
    suffix = Path(filename).suffix.lower()
    if suffix not in {".docx", ".pdf"}:
        raise ExtractionError("Bản đầu chỉ nhận DOCX/PDF. DOC cũ cần Save As DOCX; Excel được xử lý ở giai đoạn sau.")
    with PDF_LOCK:
        pymupdf.TOOLS.mupdf_display_errors(False)
        pymupdf.TOOLS.mupdf_display_warnings(False)
        try:
            result = extract_docx(data) if suffix == ".docx" else extract_pdf(data, force_ocr, progress)
            if not result.text.strip() or len(result.text) > MAX_TEXT:
                raise ExtractionError("Không có nội dung đọc được hoặc nội dung vượt giới hạn. Hãy kiểm tra bản gốc.")
            return result
        except ExtractionError:
            raise
        except Exception:
            raise ExtractionError("Không đọc được cấu trúc tài liệu. File có thể hỏng, mã hóa hoặc có nội dung chưa hỗ trợ.") from None
