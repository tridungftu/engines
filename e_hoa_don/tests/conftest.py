"""Test chỉ dùng DEMO, cấu hình trong thư mục tạm và CoreGia trong bộ nhớ."""

from pathlib import Path
import socket
import sys

import pytest

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_hoa_don"
sys.dont_write_bytecode = True
sys.path.insert(0, str(GOI))


@pytest.fixture(autouse=True)
def cach_ly_demo(tmp_path, monkeypatch):
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "cau-hinh-DEMO.json"))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "PROGRAMDATA-DEMO"))

    def cam_mang(*args, **kwargs):
        raise AssertionError("Test XML chỉ được dùng CoreGia, không gọi mạng.")

    monkeypatch.setattr(socket.socket, "connect", cam_mang)
    monkeypatch.setattr(socket, "create_connection", cam_mang)


@pytest.fixture
def xml_demo():
    return (GOI / "demo" / "hoa-don-DEMO.xml").read_bytes()
