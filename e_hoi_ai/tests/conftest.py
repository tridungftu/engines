"""Nạp gói độc lập; giữ gói sạch tệp biên dịch khi chạy pytest."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"))

import pytest
from kho_tri_thuc_sdk.engine import NganEngine
from kho_tri_thuc_sdk.thu import CoreGia
from e_hoi_ai.chay import app
import local_gia


@pytest.fixture(autouse=True)
def ngan_demo_rieng(monkeypatch):
    core = CoreGia(app)
    monkeypatch.setattr(local_gia, "_CORE_DEMO", core)
    monkeypatch.setattr(app, "ngan", NganEngine(core.duong_truyen(app.ma), app._cfg))
    monkeypatch.setattr(app, "cau_hinh", {})
