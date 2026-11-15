"""Chỉ DEMO, không mạng; thêm đúng thư mục gói độc lập."""

from pathlib import Path
import socket
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_tra_cuu"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


@pytest.fixture(autouse=True)
def cam_mang(monkeypatch):
    def tu_choi(*args, **kwargs):
        raise AssertionError("Test DEMO không được gọi mạng.")
    monkeypatch.setattr(socket.socket, "connect", tu_choi)
    monkeypatch.setattr(socket.socket, "connect_ex", tu_choi)
    monkeypatch.setattr(socket, "create_connection", tu_choi)
    monkeypatch.setattr(socket, "getaddrinfo", tu_choi)
