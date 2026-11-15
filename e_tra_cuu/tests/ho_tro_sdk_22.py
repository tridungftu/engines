"""Dựng việc SDK thật trên CoreGia 2.2.0; không thay ngăn bằng mock riêng."""

from contextlib import ExitStack, contextmanager
from copy import deepcopy
from threading import Event, Thread

from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay


@contextmanager
def mo_viec_ngan(core, phap_nhan="DEMO-P"):
    phieu = deepcopy(chay.app.phieu)
    phieu["nang_luc"] = [{"ma": "demo.ngan@1", "ten": "Kiểm ngăn DEMO",
                           "nhan": ["van_ban"], "tra": "van_ban",
                           "gioi_han": {"thoi_han_giay": 60}}]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=chay.app.thu_muc_goi)
    da_nhan, dung = Event(), Event()
    nhan = []

    @app.nang_luc("demo.ngan@1")
    def giu_viec(viec):
        nhan.append(viec)
        da_nhan.set()
        if not dung.wait(30):
            raise AssertionError("Test chưa trả việc DEMO.")
        return {"loai": "van_ban", "van_ban": "Đã kiểm DEMO"}

    core.giao_viec("demo.ngan@1", {"loai": "van_ban", "van_ban": "DEMO"},
                  phap_nhan_id=phap_nhan)
    luong = Thread(target=core.chay, args=(app,), daemon=True)
    luong.start()
    try:
        assert da_nhan.wait(5), "CoreGia chưa cấp việc DEMO."
        yield nhan[0]
    finally:
        dung.set()
        luong.join(5)
        assert not luong.is_alive()


class BoNganSDK:
    def __init__(self):
        self.core = CoreGia()
        self.stack = ExitStack()
        self.cac_viec = {}

    def viec(self, phap_nhan="DEMO-P"):
        if phap_nhan not in self.cac_viec:
            self.cac_viec[phap_nhan] = self.stack.enter_context(mo_viec_ngan(self.core, phap_nhan))
        return self.cac_viec[phap_nhan]

    def ngan(self, phap_nhan="DEMO-P"):
        return self.viec(phap_nhan).ngan

    def close(self):
        self.stack.close()
