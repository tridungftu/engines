from dataclasses import dataclass, field
import unicodedata


class ExtractionError(ValueError):
    """Tai lieu khong doc duoc day du hoac an toan."""


@dataclass
class Extracted:
    text: str
    warnings: list[str] = field(default_factory=list)
    ocr_pages: int = 0
    pages: list[dict] = field(default_factory=list)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(c for c in text if c in "\n\t" or not unicodedata.category(c).startswith("C"))


def fromstring(data):
    """OOXML chi nhan UTF-8, tu choi DTD/entity truoc parser thu vien chuan."""
    import re
    from xml.etree import ElementTree
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
        raise ExtractionError("DOCX có khai báo XML không được hỗ trợ.")
    return ElementTree.fromstring(text)
