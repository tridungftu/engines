"""Test chỉ dùng DEMO trong RAM và CoreGia; cấm kết nối mạng."""

from pathlib import Path
import os
import socket
import sys

import pytest

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / "goi" / "e_phan_luong"
sys.path[:0] = [str(GOI), str(TESTS)]


def pytest_configure(config):
    config.addinivalue_line("markers", "sau: kiểm sâu khi đặt KIEM_SAU=1")


def pytest_collection_modifyitems(items):
    if os.environ.get("KIEM_SAU") == "1":
        return
    bo_qua = pytest.mark.skip(reason="kiểm sâu: đặt KIEM_SAU=1")
    for item in items:
        if item.get_closest_marker("sau") is not None:
            item.add_marker(bo_qua)


def trang_thai_so_sanh():
    """Giữ seed 0–19 ở kiểm nhanh; CI kiểm đủ 240 trạng thái ban đầu."""
    return [pytest.param(i, marks=pytest.mark.sau) if i >= 20 else i
            for i in range(240)]


@pytest.fixture(autouse=True)
def cach_ly_demo(monkeypatch):
    def cam(*args, **kwargs):
        raise AssertionError("Chỉ dùng Core giả (CoreGia) trong RAM; cấm mạng.")

    monkeypatch.setattr(socket.socket, "connect", cam)
    monkeypatch.setattr(socket, "create_connection", cam)
