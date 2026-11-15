"""Nạp gói độc lập; giữ gói sạch tệp biên dịch khi chạy pytest."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"))

import json
import pytest
from e_hoi_ai.chay import app
from e_hoi_ai.ngan import NganBoNho


@pytest.fixture(autouse=True)
def ngan_demo_rieng(monkeypatch):
    khai = json.loads((app.thu_muc_goi / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(app, "ngan", NganBoNho(khai["ngan_du_lieu"]), raising=False)
