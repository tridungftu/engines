"""Test chỉ dùng DEMO trong RAM và CoreGia; cấm kết nối mạng."""

from pathlib import Path
import socket
import sys

import pytest

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / "goi" / "e_phan_luong"
sys.path[:0] = [str(GOI), str(TESTS)]


@pytest.fixture(autouse=True)
def cach_ly_demo(monkeypatch):
    def cam(*args, **kwargs):
        raise AssertionError("Chỉ dùng Core giả (CoreGia) trong RAM; cấm mạng.")

    monkeypatch.setattr(socket.socket, "connect", cam)
    monkeypatch.setattr(socket, "create_connection", cam)
