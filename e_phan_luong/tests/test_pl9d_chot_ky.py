"""PL-9D: đếm theo trang và cô lập lỗi chốt kỳ; đã kiểm bằng Core giả (CoreGia)."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import logging
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk import engine as sdk_engine, thu as sdk_thu
from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganEngine, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chot_ky, ho_so, ngan_chung, ty_le
from e_phan_luong.chay import app
from test_pl4b_chot_ky import (
    CS, KHOA, _ban, _chay, _chay_dat, _them_ho_so, _them_ket_qua, _them_ty_le,
)


GIO_VN = timezone(timedelta(hours=7))


@pytest.fixture(autouse=True)
def ghim_gio(monkeypatch):
    luc = [datetime(2026, 11, 20, 12, tzinfo=GIO_VN)]

    class DongHo(datetime):
        @classmethod
        def now(cls, tz=None):
            return luc[0].astimezone(tz) if tz is not None else luc[0].replace(tzinfo=None)

    for module in (chot_ky, sdk_engine, sdk_thu):
        monkeypatch.setattr(module, "datetime", DongHo)
    return luc


def _sang_thang(luc):
    luc[0] = datetime(2026, 12, 1, tzinfo=GIO_VN)


def _lam_moi(ban, ky):
    return ho_so.ve_ban_ghi(ho_so.lam_moi(ho_so.tu_ban_ghi(ban), ky))


def test_dem_theo_trang_coregia_du_loc_va_thu_tu(monkeypatch):
    core = CoreGia()
    ds = [("chon_mau", "dat", None), ("chon_mau", "sai", "sad"),
          ("ngoai_mau", "sai", "te"), ("bat_buoc", "dat", None),
          ("chon_mau", "khong_kiem", None)]
    _chay_dat(core, lambda v: _them_ket_qua(v, ds))
    tim_goc = NganEngine.tim
    trang_da_doc = []

    def tim(ngan, bang, **kw):
        assert kw["sap_xep"] == [{"truong": c, "giam": False}
                                 for c in ("ma_luot", "ma", "khau")]
        assert kw["loc"] == KHOA and "gom_het_han" not in kw
        trang_da_doc.append(kw["tiep"])
        kw["gioi_han"] = 2
        return tim_goc(ngan, bang, **kw)

    monkeypatch.setattr(NganEngine, "tim", tim)
    nhan = []
    _chay_dat(core, lambda v: ngan_chung.dem_theo_trang(
        v, "ket_qua_kiem", KHOA, lambda b: nhan.append(b.gia_tri["ma"])))
    assert len(trang_da_doc) == 3 and len(nhan) == 5
    assert nhan == sorted(set(nhan))


def test_tinh_lai_hon_200000_dong_khong_gom_danh_sach(monkeypatch):
    core = CoreGia()
    tong = 200_003
    so_trang = []

    def tim(ngan, bang, **kw):
        assert bang == "ket_qua_kiem" and kw["loc"] == KHOA
        dau = int(kw["tiep"] or 0)
        cuoi = min(dau + kw["gioi_han"], tong)
        so_trang.append(cuoi - dau)
        return SimpleNamespace(danh_sach=[SimpleNamespace(gia_tri={
            "ket_qua": "sai" if i % 1000 == 0 else "dat",
            "nguon_mau": "chon_mau", "muc_sai": "sad" if i % 1000 == 0 else None,
        }) for i in range(dau, cuoi)], tiep=str(cuoi) if cuoi < tong else None)

    def cam_gom(*args, **kw):
        raise AssertionError("Không được gom toàn bộ kết quả kiểm vào RAM.")

    monkeypatch.setattr(NganEngine, "tim", tim)
    monkeypatch.setattr(ngan_chung, "tim_tat_ca", cam_gom)
    kq = []
    _chay_dat(core, lambda v: kq.append(chot_ky._tinh_lai(v, ty_le.moi(**KHOA, cs=CS), CS)))
    assert (kq[0].mau_12t, kq[0].loi_12t, kq[0].loi_sad_12t) == (tong, 201, 201)
    assert len(so_trang) == 401 and max(so_trang) == 500 and sum(so_trang) == tong


def test_con_tro_lap_bao_ngan_ban(monkeypatch):
    core = CoreGia()
    monkeypatch.setattr(NganEngine, "tim", lambda *a, **kw: SimpleNamespace(
        danh_sach=[], tiep="DEMO-con-tro-lap"))
    kq = _chay(core, lambda v: ngan_chung.dem_theo_trang(v, "ket_qua_kiem", KHOA, lambda b: None))
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "NGAN_BAN"


@pytest.mark.parametrize("loi_o", ["dem", "lam_moi", "thoi_diem"])
def test_mot_cap_loi_khong_chan_cap_khac_va_luot_sau_thu_lai(
        monkeypatch, ghim_gio, caplog, loi_o):
    core = CoreGia()
    hong = {**KHOA, "loai": "a_demo_loi"}
    tot = {**KHOA, "loai": "b_demo_dat"}

    def dung(v):
        for khoa in (hong, tot):
            _them_ty_le(v, khoa, mau_12t=7)
            _them_ho_so(v, khoa)
            _them_ket_qua(v, [("chon_mau", "dat", None)], khoa=khoa,
                         ma_luot="PL-DEMO-" + khoa["loai"])

    _chay_dat(core, dung)
    _sang_thang(ghim_gio)
    so = []
    tinh_goc, tao_goc = chot_ky._tinh_lai, chot_ky._tao_tu_ky

    def tinh(v, tt, cs):
        if loi_o == "dem" and tt.loai == hong["loai"]:
            raise ValueError("DEMO chi tiết không được lộ")
        return tinh_goc(v, tt, cs)

    def lam_moi(ban, ky):
        if loi_o == "lam_moi" and ban["loai"] == hong["loai"]:
            raise ValueError("DEMO chi tiết không được lộ")
        return _lam_moi(ban, ky)

    def tao(ban, ky):
        if loi_o == "thoi_diem" and ban.gia_tri["loai"] == hong["loai"]:
            raise ValueError("DEMO chi tiết không được lộ")
        return tao_goc(ban, ky)

    with monkeypatch.context() as m, caplog.at_level(logging.WARNING, logger=chot_ky.__name__):
        m.setattr(chot_ky, "_tinh_lai", tinh)
        m.setattr(chot_ky, "_tao_tu_ky", tao)
        _chay_dat(core, lambda v: so.append(chot_ky.chot_neu_can(v, CS, lam_moi_ho_so=lam_moi)))
    assert so == [1]
    assert _ban(core, "ty_le", hong)["mau_12t"] == "7"
    assert _ban(core, "ho_so_hanh_vi", hong)["ky_lam_moi"] == "2026-11"
    assert _ban(core, "ty_le", tot)["mau_12t"] == "1"
    assert len(core.xem_ngan(app.ma, "chot_ky")) == 1
    assert "sẽ thử lại ở lượt sau" in caplog.text
    assert "DEMO chi tiết" not in caplog.text and hong["loai"] not in caplog.text
    _chay_dat(core, lambda v: so.append(chot_ky.chot_neu_can(v, CS, lam_moi_ho_so=_lam_moi)))
    assert so == [1, 1] and len(core.xem_ngan(app.ma, "chot_ky")) == 2
    assert _ban(core, "ty_le", hong)["mau_12t"] == "1"


def test_ho_so_chua_co_ty_le_loi_van_lam_moi_ho_so_khac(ghim_gio):
    core = CoreGia()
    hong, tot = {**KHOA, "loai": "a_demo_loi"}, {**KHOA, "loai": "b_demo_dat"}
    _chay_dat(core, lambda v: [_them_ho_so(v, khoa) for khoa in (hong, tot)])
    _sang_thang(ghim_gio)

    def lam_moi(ban, ky):
        if ban["loai"] == hong["loai"]:
            raise ValueError("DEMO")
        return _lam_moi(ban, ky)

    _chay_dat(core, lambda v: chot_ky.chot_neu_can(v, CS, lam_moi_ho_so=lam_moi))
    assert _ban(core, "ho_so_hanh_vi", hong)["ky_lam_moi"] == "2026-11"
    assert _ban(core, "ho_so_hanh_vi", tot)["ky_lam_moi"] == "2026-12"


@pytest.mark.parametrize("so_lan", [1, 4])
def test_cas_chot_ky_thu_lai_va_ngan_ban_van_day_len_core(ghim_gio, so_lan):
    core = CoreGia()
    _chay_dat(core, lambda v: (_them_ty_le(v, mau_12t=7), _them_ho_so(v)))
    _sang_thang(ghim_gio)
    core.gay_xung_dot_ngan("ho_so_hanh_vi", so_lan=so_lan)
    kq = _chay(core, lambda v: chot_ky.chot_neu_can(v, CS, lam_moi_ho_so=_lam_moi))
    if so_lan == 1:
        assert kq["trang_thai"] == "XONG"
        assert len(core.xem_ngan(app.ma, "chot_ky")) == 1
        assert _ban(core, "ty_le")["row_version"] == 2
    else:
        assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "NGAN_BAN"
        assert kq["loi"]["thu_lai_duoc"] is True
        assert core.xem_ngan(app.ma, "chot_ky") == []
        assert _ban(core, "ty_le")["row_version"] == 1
        _chay_dat(core, lambda v: chot_ky.chot_neu_can(v, CS, lam_moi_ho_so=_lam_moi))
        assert len(core.xem_ngan(app.ma, "chot_ky")) == 1


def test_huy_viec_khong_bi_nuot_nhu_loi_mot_cap(monkeypatch, ghim_gio):
    core = CoreGia()
    _chay_dat(core, lambda v: _them_ty_le(v))
    _sang_thang(ghim_gio)

    def huy(*a):
        raise ViecDaHuy()

    monkeypatch.setattr(chot_ky, "_tinh_lai", huy)
    assert _chay(core, lambda v: chot_ky.chot_neu_can(v, CS))["trang_thai"] == "HUY"
    assert core.xem_ngan(app.ma, "chot_ky") == []
