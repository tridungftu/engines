"""Chỉ dùng DEMO và CoreGia; không cho test nối mạng."""

from pathlib import Path
import socket
import sys

import pytest

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / 'goi' / 'e_kiem_excel'
sys.path[:0] = [str(GOI), str(TESTS / 'demo'), str(TESTS)]


@pytest.fixture(autouse=True)
def cach_ly_demo(monkeypatch):
    def cam(*args, **kwargs):
        raise AssertionError('Test Excel chỉ dùng CoreGia trong RAM; cấm mạng.')
    monkeypatch.setattr(socket.socket, 'connect', cam)
    monkeypatch.setattr(socket, 'create_connection', cam)


@pytest.fixture(scope='session')
def demo(tmp_path_factory):
    from sinh_demo import sinh
    thu_muc = tmp_path_factory.mktemp('excel-DEMO')
    sinh(thu_muc)
    return thu_muc
