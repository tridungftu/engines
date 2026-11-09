from dataclasses import dataclass, field
import unicodedata


class ExtractionError(ValueError):
    """Input cannot be safely/readably extracted."""


@dataclass
class Extracted:
    text: str
    warnings: list[str] = field(default_factory=list)
    ocr_pages: int = 0
    pages: list[dict] = field(default_factory=list)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(c for c in text if c in "\n\t" or not unicodedata.category(c).startswith("C"))
