"""Chỉ kiểm gói mới, dùng thư mục DEMO và không sinh bytecode trong gói."""

from pathlib import Path
import sys

import pytest


sys.dont_write_bytecode = True
THU_MUC_GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
sys.path.insert(0, str(THU_MUC_GOI))


@pytest.fixture(autouse=True)
def moi_truong_demo(monkeypatch, tmp_path):
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "may-DEMO"))
    monkeypatch.delenv("KTT_ENGINE_CAU_HINH", raising=False)
    monkeypatch.delenv("KTT_ENGINE_DU_LIEU", raising=False)
