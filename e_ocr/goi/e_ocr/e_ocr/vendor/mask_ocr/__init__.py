"""Bộ đọc nội bộ từ mask_ocr; chỉ Tesseract, PDF chữ sẵn và DOCX."""
from .common import Extracted, ExtractionError
from .extraction import extract, extract_docx

__all__ = ["Extracted", "ExtractionError", "extract", "extract_docx"]
