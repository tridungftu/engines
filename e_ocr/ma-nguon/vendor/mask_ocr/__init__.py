"""Standalone local DOCX/PDF extraction and Vietnamese/English OCR."""
from .common import Extracted, ExtractionError
from .extraction import extract, ocr_ready

__all__ = ["Extracted", "ExtractionError", "extract", "ocr_ready"]
