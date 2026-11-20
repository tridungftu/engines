"""PL-9G: ca nhỏ, đã kiểm bằng Core giả (CoreGia); không có benchmark lớn."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import subprocess
import sys
import threading
import time
import gc
import weakref

import pytest

from do_hieu_nang import (CoreChiMuc, CoreDem, DongHoCore, TESTS, app, bang_uoc_tinh,
                         cac_cong_core, do_mot, xu_huong)


def test_boc_du_cua_sdk_va_khoi_phuc_khi_loi():
    can = {"_ngan_doc", "_ngan_tim", "_ngan_ghi_lo", "_mo_tep", "_tai_tep_ra",
           "_gia_han", "_tien_do", "_san_sang", "_nhan_viec", "_doc_dau_vao",
           "_nop_ket_qua", "_ket_thuc", "_doc_cau_hinh", "_hang_cho", "nap_engine"}
    assert can <= set(cac_cong_core())
    core = CoreDem()
    cu = dict(core.__dict__)
    with pytest.raises(ValueError), DongHoCore(core):
        assert all(ten in core.__dict__ for ten in cac_cong_core())
        raise ValueError("Lỗi DEMO")
    assert core.__dict__ == cu


def test_khong_cong_hai_lan_core_goi_noi_bo_va_dem_loi():
    gio = [0.0]
    class CoreLong(CoreDem):
        def _san_sang(self):
            gio[0] = 2
            self._doc_cau_hinh()
            gio[0] = 7
            raise ValueError("Lỗi DEMO")

        def _doc_cau_hinh(self):
            gio[0] = 5

    core = CoreLong()
    with DongHoCore(core, dong_ho=lambda: gio[0]) as do:
        with pytest.raises(ValueError):
            core._san_sang()
    assert do.dem == {"_san_sang": 1}
    assert do.giay_cua == {"_san_sang": 7}
    assert do.giay == 7
    assert do.dang_goi == 0


def test_hop_khoang_core_chong_luong_co_khoa():
    gio = [0.0]
    vao, xong = threading.Event(), threading.Event()
    core = CoreDem()
    do = DongHoCore(core, dong_ho=lambda: gio[0])
    def lau():
        vao.set()
        assert xong.wait(5)
        gio[0] = 7
    def ngan():
        gio[0] = 5
        raise ValueError("Lỗi DEMO")
    with ThreadPoolExecutor(max_workers=1) as pool:
        f = pool.submit(do.boc("lau", lau))
        assert vao.wait(5)
        gio[0] = 2
        try:
            with pytest.raises(ValueError):
                do.boc("ngan", ngan)()
        finally:
            xong.set()
        f.result(timeout=5)
    assert do.dem == {"lau": 1, "ngan": 1}
    assert do.giay_cua == {"lau": 7, "ngan": 3}
    assert do.giay == 7  # Tổng từng cửa = 10, hợp khoảng chỉ = 7.


@pytest.mark.parametrize("lop", [CoreDem, CoreChiMuc])
def test_so_do_tach_khop_tong_va_dem_cu(lop):
    kq = do_mot("json_trong", 8, lop_core=lop)
    assert kq["giay"] == pytest.approx(kq["giay_core_gia"] + kq["giay_engine_thuan"], abs=2e-6)
    assert 0 < kq["giay_core_gia"] < kq["giay"]
    assert kq["tong_moi_cong_core"] == sum(kq["dem_moi_cong_core"].values())
    for ten, cu in [("_ngan_doc", "doc"), ("_ngan_tim", "tim"), ("_ngan_ghi_lo", "lo_ghi"),
                    ("_mo_tep", "tai_tep_vao"), ("_tai_tep_ra", "tai_tep_ra")]:
        assert kq["dem_moi_cong_core"][ten] == kq["dem"][cu]
    assert kq["dem_moi_cong_core"]["_tien_do"] > 0
    assert kq["dem_moi_cong_core"]["_nop_ket_qua"] == 1
    assert kq["dem_moi_cong_core"]["_ket_thuc"] == 1


def test_do_core_cham_duoc_tru_va_ho_so_nam_o_luot_rieng():
    class CoreCham(CoreChiMuc):
        def _ngan_tim(self, *args, **kw):
            time.sleep(0.002)
            return super()._ngan_tim(*args, **kw)
    kq = do_mot("json_trong", 8, lop_core=CoreCham)
    assert kq["giay_core_theo_cua"]["_ngan_tim"] >= kq["dem"]["tim"] * 0.002
    prof = do_mot("json_trong", 8, lop_core=CoreChiMuc, ho_so=True)
    assert prof["co_profiler"]
    assert len(prof["ho_so"]["top_5_engine_self"]) == 5
    assert prof["ho_so"]["sdk_engine_py_self_giay_can_duoi"] > 0


def test_khong_giu_kho_core_gia_cua_mau_truoc_qua_app():
    refs = []
    class CoreTheoDoi(CoreChiMuc):
        def __init__(self):
            assert not any(ref() is not None for ref in refs)
            super().__init__()
            refs.append(weakref.ref(self))
    do_mot("json_trong", 8, lop_core=CoreTheoDoi)
    do_mot("json_trong", 8, lop_core=CoreTheoDoi, bo_nho=True)
    gc.collect()
    assert app._dt is None and app.ngan is None
    assert refs[-1]() is None


def mau_dem():
    return [{"ca": "json_trong", "so_dong": n, "giay": 10*n,
             "giay_engine_thuan": n/100, "giay_core_gia": n/10,
             "tong_moi_cong_core": 2*n+15, "dem": {"doc": n, "tim": n},
             "thoi_han_giay": 300} for n in [1000, 5000, 10000]]


def test_uoc_tinh_chi_dung_engine_thuan_va_calls_do_that_khong_ma_cung():
    mau = mau_dem()
    bang = bang_uoc_tinh(mau, [mau[-1]])
    assert [r["giay_uoc_tinh"] for r in bang] == [140.03, 200.075, 300.15]
    assert [r["trong_300_giay"] for r in bang] == [True, True, False]
    assert xu_huong(mau)["gan_tuyen_tinh_trong_mau"]
    for r in bang:
        n = r["co_lo_an_toan_uoc_tinh_du_2_lan"]
        assert n <= 10000
        assert n/100 + (2*n+15)*r["tre_ms"]/1000 <= 150
    doi = deepcopy(mau)
    doi[-1]["tong_moi_cong_core"] += 30
    assert bang_uoc_tinh(doi, [doi[-1]])[0]["giay_uoc_tinh"] == 140.09
    doi[-1]["giay_engine_thuan"] *= 2
    assert not xu_huong(doi)["gan_tuyen_tinh_trong_mau"]
    doi[-1]["co_profiler"] = True
    assert bang_uoc_tinh(doi, [doi[-1]]) == []
    del doi[-1]["co_profiler"]
    del doi[-1]["giay_engine_thuan"]
    with pytest.raises(KeyError):
        bang_uoc_tinh(doi, [doi[-1]])  # Không được âm thầm dùng tổng giây PL-9B.


def test_cli_ca_nho_co_bang_thuan_utf8_va_dem_core():
    for pha in ["core", "thuan"]:
        ra = subprocess.run([sys.executable, "-B", str(TESTS / "do_hieu_nang.py"),
                             "--pha", pha, "--ca", "json_trong", "--co-mau", "3",
                             "--co-mau", "6"], capture_output=True, encoding="utf-8", timeout=20)
        assert ra.returncode == 0, ra.stderr
        ds = [json.loads(d) for d in ra.stdout.splitlines()]
        mau = [d for d in ds if d.get("trang_thai") == "XONG"]
        assert [d["so_dong"] for d in mau] == [3, 6]
        assert all(d["giay_engine_thuan"] > 0 for d in mau)
        if pha == "thuan":
            assert len([d for d in ds if "lam_am_ngoai_bo_mau" in d]) == 1
            assert len([d for d in ds if "giay_uoc_tinh" in d]) == 3
        else:
            assert not any("lam_am_ngoai_bo_mau" in d for d in ds)
            assert any("dem_core_50000_uoc_tinh" in d for d in ds)
