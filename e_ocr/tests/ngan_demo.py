"""Fixture dùng CoreGia SDK 2.2.0; mọi view ngăn thuộc một việc còn lease.

Không cài đặt lại ngữ nghĩa ngăn. Việc thử giữ sống bằng Engine/SDK thật,
được kết thúc khi fixture đóng. Dữ liệu bền của mọi App mới ở cùng CoreGia.
"""

import json
from copy import deepcopy
from pathlib import Path
from queue import Queue
from threading import Event, Thread, RLock

from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_ocr.chon_nguon import SoHanMuc as SoHanMucGoc

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
KHAI = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
_core = None
_viec = {}
_luong = []
_khoa_view = RLock()


def khoi_tao():
    global _core, _viec, _luong
    _core = CoreGia(KHAI, thu_muc_goi=GOI)
    _viec, _luong = {}, []


def core_demo():
    assert _core is not None, "Test cần fixture CoreGia DEMO."
    return _core


def viec_demo(pn="pn-demo"):
    with _khoa_view:
        return _tao_viec_demo(pn)


def _tao_viec_demo(pn):
    if pn not in _viec:
        q, dung = Queue(), Event()
        p = deepcopy(KHAI)
        ma = f"thu.ngan_{len(_luong)}@1"
        p["nang_luc"] = [{"ma": ma, "ten": "Giữ việc DEMO để kiểm ngăn",
            "nhan": ["van_ban"], "tra": "van_ban", "gioi_han": {"thoi_han_giay": 900}}]
        p["chay_thu_demo"] = []
        app = Engine(p, thu_muc_goi=GOI)

        @app.nang_luc(ma)
        def giu(viec):
            q.put(viec)
            assert dung.wait(120), "Việc ngăn DEMO chưa được đóng."
            return {"loai": "van_ban", "van_ban": "Đã kiểm DEMO"}

        core_demo().giao_viec(ma, {"loai": "van_ban", "van_ban": "DEMO"}, phap_nhan_id=pn)
        t = Thread(target=core_demo().chay, args=(app,), kwargs={"khoang_gia_han": 20}, daemon=True)
        _luong.append((t, dung))
        t.start()
        _viec[pn] = q.get(timeout=10)
    return _viec[pn]


def ngan_demo(pn="pn-demo"):
    return viec_demo(pn).ngan


def dong():
    for _, dung in _luong:
        dung.set()
    for t, _ in _luong:
        t.join(5)
        assert not t.is_alive(), "Còn luồng SDK DEMO."


def dat_cau_hinh(gia_tri):
    core_demo().dat_cau_hinh("e_ocr", gia_tri)


def bo_cau_hinh():
    dat_cau_hinh({})


def cau_hinh_hien_tai():
    return core_demo().duong_truyen("e_ocr").doc_cau_hinh()["cau_hinh"]


class SoHanMuc(SoHanMucGoc):
    def __init__(self, ngan=None, *, dong_ho=None):
        super().__init__(ngan if ngan is not None else ngan_demo(), dong_ho=dong_ho)


def ghi_so(so, gia_tri):
    anh, _ = so._doc()
    with so.ngan.lo() as lo:
        so._ghi(lo, anh, gia_tri)


def ghi_luot(nk, gia_tri):
    cu = nk.ngan.doc("luot_abbyy", nk._khoa())
    # Core kiểm cấu trúc; dữ liệu hỏng nhưng đúng kiểu đi qua CAS thật.
    with nk.ngan.lo() as lo:
        lo.sua("luot_abbyy", nk._khoa(), nk._gia_tri(gia_tri), row_version=cu.row_version)
