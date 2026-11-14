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

    # Chỉ ca HTTP đăng ký đúng cổng MayChuGia vừa mở; mọi mạng khác bị chặn.
    cong_core_gia = set()
    ket_noi = socket.socket.connect
    tao_ket_noi = socket.create_connection

    def kiem_dia_chi(dia_chi):
        assert dia_chi in cong_core_gia, "Test chỉ được nối đúng MayChuGia loopback."

    def noi(sock, dia_chi):
        kiem_dia_chi(dia_chi)
        return ket_noi(sock, dia_chi)

    def tao(dia_chi, *args, **kwargs):
        kiem_dia_chi(dia_chi)
        return tao_ket_noi(dia_chi, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", noi)
    monkeypatch.setattr(socket, "create_connection", tao)
    return cong_core_gia


@pytest.fixture
def xml_demo():
    return (GOI / "demo" / "hoa-don-DEMO.xml").read_bytes()
