"""PL-4B đã kiểm bằng Core giả (CoreGia), dữ liệu DEMO qua viec.ngan.

SDK 2.2.0 không nhận tham số het_han khi ghi. Dòng DEMO hết hạn được
dựng bằng đồng hồ lùi 366 ngày lúc ghi; CoreGia tự đặt hạn 365 ngày.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from threading import Barrier

import pytest
from kho_tri_thuc_sdk import thu as sdk_thu
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, NganEngine
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chot_ky, ngan_chung
from e_phan_luong.chay import app
from e_phan_luong.doi_bac import MotKetQua, cap_nhat
from e_phan_luong.kieu import (
    CHE_DO_TOAN_BO, KQ_DAT, KQ_KHONG_KIEM, KQ_SAI, MAU_BAT_BUOC,
    MAU_CHON, MAU_NGOAI, MUC_NHO, MUC_SAD, MUC_TE,
    NHAN_LOI_NGOAI_MAU, NHAN_RUI_RO_CAO,
)
from e_phan_luong.loi import CAU_LOI
from e_phan_luong.thong_ke import can_tren
from e_phan_luong.ty_le import ChinhSach, moi, tu_ban_ghi, ve_ban_ghi


GIO_VN = timezone(timedelta(hours=7))
LUC = datetime(2026, 12, 1, tzinfo=GIO_VN)
CS = ChinhSach()
KHOA = {"khau": "ktt_duyet_demo", "loai": "chi_phi_demo"}
MA_NANG_LUC = "demo.chot_ky@1"
DAU_VAO = {"loai": "van_ban", "van_ban": "DEMO chốt kỳ"}


def _app_thu(ham):
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = [{
        "ma": MA_NANG_LUC, "ten": "Chốt kỳ DEMO bằng CoreGia",
        "nhan": ["van_ban"], "tra": "van_ban",
        "gioi_han": {"thoi_han_giay": 300},
    }]
    # Fixture chỉ khai demo.chot_ky; DEMO phân luồng thuộc phiếu runtime.
    phieu["chay_thu_demo"] = []
    thu = Engine(phieu)

    @thu.nang_luc(MA_NANG_LUC)
    def kiem(viec):
        ham(viec)
        return {"loai": "van_ban", "van_ban": "DEMO"}

    return thu


def _chay(core, ham, *, phap_nhan_id="pn-demo"):
    thu = _app_thu(ham)
    ma_viec = core.giao_viec(MA_NANG_LUC, DAU_VAO, phap_nhan_id=phap_nhan_id)
    # Không gia hạn trong lúc dịch đồng hồ tạo dòng hết hạn DEMO.
    core.chay(thu, khoang_gia_han=30)
    return core.xem(ma_viec)


def _chay_dat(core, ham, **kw):
    kq = _chay(core, ham, **kw)
    assert kq["trang_thai"] == "XONG", kq


def _chot(core, *, cs=CS, luc=LUC, lam_moi_ho_so=None):
    so = []
    _chay_dat(core, lambda viec: so.append(chot_ky.chot_neu_can(
        viec, cs, luc=luc, lam_moi_ho_so=lam_moi_ho_so)))
    return so[0]


def _them_ty_le(viec, khoa=None, **so_lieu):
    khoa = KHOA if khoa is None else khoa
    tt = replace(moi(**khoa, cs=CS), **so_lieu)
    with viec.ngan.lo() as lo:
        lo.lay_hoac_tao("ty_le", khoa, ve_ban_ghi(tt))
    return tt


def _them_ho_so(viec, khoa=None):
    khoa = KHOA if khoa is None else khoa
    with viec.ngan.lo() as lo:
        lo.lay_hoac_tao("ho_so_hanh_vi", khoa, {
            **khoa, "so_nghiep_vu": 5, "bieu_do": "{}", "bam_doi_tac": "{}",
            "tong_7_ngay": "{}", "ky_lam_moi": "2026-11",
        })


def _them_ket_qua(viec, ds, *, khoa=None, ma_luot="PL-DEMO-12T"):
    khoa = KHOA if khoa is None else khoa
    for dau in range(0, len(ds), 100):
        with viec.ngan.lo() as lo:
            for i, (nguon, kq, muc) in enumerate(ds[dau:dau + 100], dau):
                lo.lay_hoac_tao("ket_qua_kiem", {
                    "ma_luot": ma_luot, "ma": f"PC-DEMO-{i:06}", "khau": khoa["khau"],
                }, {**khoa, "ma_module": "demo_thanh_toan", "ket_qua": kq,
                    "nguon_mau": nguon, "muc_sai": muc, "nguon_loai_sai": None})


def _ban(core, bang, khoa=None):
    khoa = KHOA if khoa is None else khoa
    return next(b for b in core.xem_ngan(app.ma, bang)
                if all(b.get(k) == v for k, v in khoa.items()))


def _lam_moi(gia_tri, ky):
    cot = ("khau", "loai", "so_nghiep_vu", "bieu_do", "bam_doi_tac", "tong_7_ngay")
    return {**{k: gia_tri[k] for k in cot}, "ky_lam_moi": ky}


@pytest.mark.parametrize("luc,mong", [
    (datetime(2026, 11, 30, 16, 59, 59, tzinfo=timezone.utc), "2026-11"),
    (datetime(2026, 11, 30, 17, tzinfo=timezone.utc), "2026-12"),
    (datetime(2026, 12, 31, 17, tzinfo=timezone.utc), "2027-01"),
    (datetime(2026, 12, 1, 0, tzinfo=timezone(timedelta(hours=9))), "2026-11"),
    (datetime(2026, 12, 1, 0), "2026-12"),
    (datetime(1, 2, 1, tzinfo=GIO_VN), "0001-02"),
])
def test_ky_hien_tai_theo_gio_viet_nam(luc, mong):
    assert chot_ky.ky_hien_tai(luc) == mong


def test_ky_hien_tai_mac_dinh_dung_utc7(monkeypatch):
    class DongHoDemo(datetime):
        @classmethod
        def now(cls, tz=None):
            assert tz.utcoffset(None) == timedelta(hours=7)
            return datetime(2026, 12, 1, tzinfo=tz)

    monkeypatch.setattr(chot_ky, "datetime", DongHoDemo)
    assert chot_ky.ky_hien_tai() == "2026-12"


@pytest.mark.parametrize("ky,mong", [
    ("2026-12", "2026-11"), ("2026-01", "2025-12"), ("0001-02", "0001-01"),
])
def test_ky_truoc(ky, mong):
    assert chot_ky.ky_truoc(ky) == mong


@pytest.mark.parametrize("ky", ["2026-00", "2026-13", "2026-1", "2026-11-01", "0000-12", "0001-01", None])
def test_ky_sai_bao_loi_tieng_viet(ky):
    with pytest.raises(LoiNghiepVu) as exc:
        chot_ky.ky_truoc(ky)
    assert exc.value.ma == "THAM_SO_KHONG_HOP_LE"


def test_thang_dau_chua_co_ty_le_khong_chot():
    core = CoreGia()
    assert _chot(core) == 0
    assert core.xem_ngan(app.ma, "chot_ky") == []
    assert [l for l in core.nhat_ky if l[0] == "ngan"] == []


def test_ba_cap_chot_mot_lan_va_sang_thang_sau_phan_trang(monkeypatch):
    core = CoreGia()
    cac_khoa = [KHOA, {**KHOA, "loai": "doanh_thu_demo"}, {**KHOA, "khau": "cfo_demo"}]
    cu = []

    def dung(viec):
        for i, khoa in enumerate(cac_khoa, 1):
            cu.append(_them_ty_le(viec, khoa, mau_12t=i, loi_12t=0))

    _chay_dat(core, dung)
    tim_goc = NganEngine.tim

    def tim_it(ngan, bang, **kw):
        kw["gioi_han"] = 1
        return tim_goc(ngan, bang, **kw)

    monkeypatch.setattr(NganEngine, "tim", tim_it)
    assert _chot(core) == 3
    for khoa, tt in zip(cac_khoa, cu):
        chot = _ban(core, "chot_ky", {"ky": "2026-11", **khoa})
        assert {k: chot[k] for k in ve_ban_ghi(tt)} == ve_ban_ghi(tt)
    cac_chot = deepcopy(core.xem_ngan(app.ma, "chot_ky"))
    so_ghi = core.so_lan_ghi["ngan"]
    assert _chot(core) == 0
    assert core.so_lan_ghi["ngan"] == so_ghi
    assert core.xem_ngan(app.ma, "chot_ky") == cac_chot
    assert _chot(core, luc=datetime(2027, 1, 1, tzinfo=GIO_VN)) == 3
    assert len(core.xem_ngan(app.ma, "chot_ky")) == 6
    assert {b["ky"] for b in core.xem_ngan(app.ma, "chot_ky")} == {"2026-11", "2026-12"}


def test_12_thang_dem_dung_nguon_bo_het_han_va_giu_bac(monkeypatch):
    core = CoreGia()
    ds = [(MAU_CHON, KQ_DAT, None), (MAU_CHON, KQ_DAT, None),
          (MAU_CHON, KQ_SAI, MUC_NHO), (MAU_BAT_BUOC, KQ_SAI, MUC_SAD),
          (MAU_NGOAI, KQ_SAI, MUC_TE), (MAU_NGOAI, KQ_SAI, MUC_NHO),
          (MAU_BAT_BUOC, KQ_DAT, MUC_TE), (MAU_NGOAI, KQ_DAT, None),
          (MAU_CHON, KQ_KHONG_KIEM, MUC_TE), (MAU_CHON, "DEMO_bo_qua", MUC_TE)]
    truoc = []

    class DongHoCuDemo(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(tz) - timedelta(days=366)

    def dung(viec):
        truoc.append(_them_ty_le(
            viec, bac=CS.bac[2], che_do=CHE_DO_TOAN_BO,
            mau_tu_doi_bac=17, loi_tu_doi_bac=2, mau_sach_toan_bo=7,
            mau_12t=999, loi_12t=123, loi_sad_12t=99, loi_ngoai_mau_12t=88,
            doi_bac_luc="2026-09-01T00:00:00+07:00"))
        for ky in ["2025-12", *(f"2026-{m:02d}" for m in range(1, 12))]:
            _them_ket_qua(viec, ds, ma_luot=f"PL-DEMO-{ky}")
        _them_ket_qua(viec, [(MAU_CHON, KQ_SAI, MUC_TE)],
                     khoa={**KHOA, "khau": "khau_khac_demo"})
        _them_ket_qua(viec, [(MAU_CHON, KQ_SAI, MUC_TE)],
                     khoa={**KHOA, "loai": "loai_khac_demo"}, ma_luot="PL-DEMO-khac")
        with monkeypatch.context() as m:
            m.setattr(sdk_thu, "datetime", DongHoCuDemo)
            _them_ket_qua(viec, [(MAU_CHON, KQ_SAI, MUC_TE),
                                (MAU_BAT_BUOC, KQ_SAI, MUC_SAD),
                                (MAU_NGOAI, KQ_SAI, MUC_TE)], ma_luot="PL-DEMO-het-han")
        tat_ca = ngan_chung.tim_tat_ca(viec, "ket_qua_kiem", KHOA)
        assert len(tat_ca) == 120
        trang = viec.ngan.tim("ket_qua_kiem", loc=KHOA, gom_het_han=True, gioi_han=500)
        assert len(trang.danh_sach) == 123

    _chay_dat(core, dung)
    cs = replace(CS, do_tin_cay=CS.do_tin_cay - CS.san)
    tim_goc = NganEngine.tim

    def tim_phan_trang(ngan, bang, **kw):
        kw["gioi_han"] = 17
        return tim_goc(ngan, bang, **kw)

    monkeypatch.setattr(NganEngine, "tim", tim_phan_trang)
    assert _chot(core, cs=cs) == 1
    tt = tu_ban_ghi(_ban(core, "ty_le"))
    assert (tt.mau_12t, tt.loi_12t, tt.loi_sad_12t, tt.loi_ngoai_mau_12t) == (36, 12, 24, 24)
    assert tt.diem == can_tren(12, 36, cs.do_tin_cay)
    assert tt.nhan == frozenset({NHAN_RUI_RO_CAO, NHAN_LOI_NGOAI_MAU})
    for cot in ("bac", "che_do", "mau_tu_doi_bac", "loi_tu_doi_bac", "mau_sach_toan_bo", "doi_bac_luc"):
        assert getattr(tt, cot) == getattr(truoc[0], cot)
    chot = _ban(core, "chot_ky", {"ky": "2026-11", **KHOA})
    assert chot["mau_12t"] == "999"
    assert chot["loi_12t"] == "123"


@pytest.mark.parametrize("ds,nhan", [
    ([], set()),
    ([(MAU_CHON, KQ_DAT, None)] * 30, set()),
    ([(MAU_CHON, KQ_DAT, None)], {NHAN_RUI_RO_CAO}),
    ([(MAU_BAT_BUOC, KQ_SAI, MUC_SAD)], {NHAN_RUI_RO_CAO}),
    ([(MAU_BAT_BUOC, KQ_SAI, MUC_TE)], {NHAN_RUI_RO_CAO}),
    ([(MAU_NGOAI, KQ_SAI, MUC_NHO)], {NHAN_LOI_NGOAI_MAU}),
    ([(MAU_CHON, KQ_KHONG_KIEM, MUC_TE)], set()),
])
def test_diem_nhan_nhu_doi_bac_va_go_nhan_cu(ds, nhan):
    core = CoreGia()

    def dung(viec):
        _them_ty_le(viec, mau_12t=10, loi_12t=1, loi_sad_12t=1, loi_ngoai_mau_12t=1,
                    nhan=frozenset({NHAN_RUI_RO_CAO, NHAN_LOI_NGOAI_MAU, "DEMO_khac"}))
        _them_ket_qua(viec, ds)

    _chay_dat(core, dung)
    assert _chot(core) == 1
    tt = tu_ban_ghi(_ban(core, "ty_le"))
    doi_chieu = moi(**KHOA, cs=CS)
    for nguon, kq, muc in ds:
        doi_chieu, _ = cap_nhat(doi_chieu, MotKetQua(nguon, kq, muc), CS, luc=LUC.isoformat())
    assert tt.diem == doi_chieu.diem
    assert tt.nhan == frozenset(nhan | {"DEMO_khac"})


@pytest.mark.parametrize("bang_xung_dot", ["ty_le", "ho_so_hanh_vi"])
def test_cas_xung_dot_dung_mot_lan_thu_lai_ca_lo(bang_xung_dot, monkeypatch):
    core = CoreGia()

    def dung(viec):
        _them_ty_le(viec, mau_12t=7)
        _them_ho_so(viec)
        _them_ket_qua(viec, [(MAU_CHON, KQ_DAT, None)])

    _chay_dat(core, dung)
    core.gay_xung_dot_ngan(bang_xung_dot, so_lan=1)
    lan_thu_lai = []
    gia_tri_cu = []
    ghi_goc = ngan_chung.ghi_lo_thu_lai

    def ghi(viec, lap_lenh, **kw):
        so = ghi_goc(viec, lap_lenh, **kw)
        lan_thu_lai.append(so)
        return so

    def lam_moi(gia_tri, ky):
        gia_tri_cu.append((gia_tri["row_version"], gia_tri["so_nghiep_vu"]))
        kq = _lam_moi(gia_tri, ky)
        kq["so_nghiep_vu"] = int(gia_tri["so_nghiep_vu"]) + 1
        return kq

    monkeypatch.setattr(ngan_chung, "ghi_lo_thu_lai", ghi)
    assert _chot(core, lam_moi_ho_so=lam_moi) == 1
    assert lan_thu_lai == [0, 1]
    assert gia_tri_cu == [(1, "5"), (1, "5")]
    assert _ban(core, "ty_le")["row_version"] == 2
    assert _ban(core, "ty_le")["mau_12t"] == "1"
    assert _ban(core, "ho_so_hanh_vi")["row_version"] == 2
    assert _ban(core, "ho_so_hanh_vi")["so_nghiep_vu"] == "6"
    assert _ban(core, "ho_so_hanh_vi")["ky_lam_moi"] == "2026-12"
    assert len(core.xem_ngan(app.ma, "chot_ky")) == 1


def test_cas_het_ba_lan_thu_lai_bao_ngan_ban_khong_sua_nua_lo():
    core = CoreGia()

    def dung(viec):
        _them_ty_le(viec, mau_12t=7)
        _them_ho_so(viec)

    _chay_dat(core, dung)
    core.gay_xung_dot_ngan("ho_so_hanh_vi", so_lan=4)
    so_goi = []

    def lam_moi(gia_tri, ky):
        so_goi.append(1)
        return _lam_moi(gia_tri, ky)

    kq = _chay(core, lambda v: chot_ky.chot_neu_can(v, CS, luc=LUC, lam_moi_ho_so=lam_moi))
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"] == {"ma": "NGAN_BAN", "thong_diep": CAU_LOI["NGAN_BAN"], "thu_lai_duoc": True}
    assert len(so_goi) == 4
    assert _ban(core, "ty_le")["mau_12t"] == "7"
    assert _ban(core, "ty_le")["row_version"] == 1
    assert _ban(core, "ho_so_hanh_vi")["ky_lam_moi"] == "2026-11"
    assert _ban(core, "ho_so_hanh_vi")["row_version"] == 1
    # Bản chốt đã ghi ở lô trước, không có cơ chế rollback liên lô trong SDK.
    assert len(core.xem_ngan(app.ma, "chot_ky")) == 1


def test_cas_doc_lai_khi_viec_khac_da_ghi_so_lieu_moi(monkeypatch):
    core = CoreGia()
    _chay_dat(core, lambda v: _them_ty_le(v, mau_tu_doi_bac=7))
    doc_goc = NganEngine.doc
    cac_phien_ban = []

    def doc_co_viec_khac(ngan, bang, khoa, **kw):
        ban = doc_goc(ngan, bang, khoa, **kw)
        if bang == "ty_le":
            cac_phien_ban.append(ban.row_version)
            if len(cac_phien_ban) == 2:
                # Việc khác ghi sau lần đọc CAS đầu: bộ đếm và kết quả
                # mới phải được giữ khi bên chốt đọc lại row_version.
                with ngan.lo() as lo:
                    lo.sua("ty_le", khoa, {"mau_tu_doi_bac": 42}, row_version=ban.row_version)
                    lo.lay_hoac_tao("ket_qua_kiem", {
                        "ma_luot": "PL-DEMO-dong-thoi", "ma": "PC-DEMO-moi", "khau": khoa["khau"],
                    }, {**khoa, "ma_module": "demo_thanh_toan", "ket_qua": KQ_DAT,
                        "nguon_mau": MAU_CHON, "muc_sai": None, "nguon_loai_sai": None})
        return ban

    monkeypatch.setattr(NganEngine, "doc", doc_co_viec_khac)
    assert _chot(core) == 1
    assert cac_phien_ban == [1, 1, 2]
    tt = _ban(core, "ty_le")
    assert tt["row_version"] == 3
    assert tt["mau_tu_doi_bac"] == "42"
    assert tt["mau_12t"] == "1"
    assert tt["diem"] == str(can_tren(0, 1))


@pytest.mark.parametrize("co_callback,co_ho_so", [(False, True), (True, False)])
def test_ho_so_vang_hoac_khong_callback_khong_tao_sua(co_callback, co_ho_so):
    core = CoreGia()

    def dung(viec):
        _them_ty_le(viec)
        if co_ho_so:
            _them_ho_so(viec)

    _chay_dat(core, dung)
    so_goi = []

    def lam_moi(gia_tri, ky):
        so_goi.append(1)
        return _lam_moi(gia_tri, ky)

    assert _chot(core, lam_moi_ho_so=lam_moi if co_callback else None) == 1
    assert so_goi == []
    if co_ho_so:
        assert _ban(core, "ho_so_hanh_vi")["row_version"] == 1
    else:
        assert core.xem_ngan(app.ma, "ho_so_hanh_vi") == []


def test_hai_viec_dong_thoi_chi_ben_da_tao_moi_cap_nhat(monkeypatch):
    core = CoreGia()

    def dung(viec):
        _them_ty_le(viec, mau_12t=8)
        _them_ho_so(viec)

    _chay_dat(core, dung)
    hen = Barrier(2)
    tim_goc = NganEngine.tim

    def tim_cung_luc(ngan, bang, **kw):
        trang = tim_goc(ngan, bang, **kw)
        if bang == "chot_ky":
            assert trang.danh_sach == []
            hen.wait(timeout=5)
        return trang

    monkeypatch.setattr(NganEngine, "tim", tim_cung_luc)
    so_chot, so_lam_moi = [], []

    def lam_moi(gia_tri, ky):
        so_lam_moi.append(1)
        return _lam_moi(gia_tri, ky)

    def chot(viec):
        so_chot.append(chot_ky.chot_neu_can(viec, CS, luc=LUC, lam_moi_ho_so=lam_moi))

    cac_app = [_app_thu(chot), _app_thu(chot)]
    cac_viec = [core.giao_viec(MA_NANG_LUC, DAU_VAO) for _ in range(2)]
    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_luot = [nhom.submit(core.chay, thu, khoang_gia_han=30) for thu in cac_app]
        for luot in cac_luot:
            luot.result(timeout=10)
    assert [core.xem(v)["trang_thai"] for v in cac_viec] == ["XONG", "XONG"]
    assert sorted(so_chot) == [0, 1]
    assert so_lam_moi == [1]
    assert _ban(core, "ty_le")["row_version"] == 2
    assert _ban(core, "ho_so_hanh_vi")["row_version"] == 2
    assert len(core.xem_ngan(app.ma, "chot_ky")) == 1


def test_ban_chup_c4_chi_co_cot_thong_ke(monkeypatch):
    core = CoreGia()
    _chay_dat(core, lambda v: _them_ty_le(v, mau_12t=9))
    doc_goc = NganEngine.doc
    chi_tiet_demo = {
        "so_tien": {"so": "123456789.12", "tien_te": "VND"},
        "ngay": "2026-10-30", "doi_tac": "DEMO-NCC-khong-duoc-chup",
        "noi_dung": "DEMO dien giai khong duoc chup",
    }

    def doc_them_chi_tiet(ngan, bang, khoa, **kw):
        ban = doc_goc(ngan, bang, khoa, **kw)
        if bang == "ty_le" and ban is not None:
            return replace(ban, gia_tri={**ban.gia_tri, **chi_tiet_demo})
        return ban

    monkeypatch.setattr(NganEngine, "doc", doc_them_chi_tiet)
    assert _chot(core) == 1
    chot = _ban(core, "chot_ky", {"ky": "2026-11", **KHOA})
    cot_he_thong = {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
    assert set(chot) == set(ve_ban_ghi(moi(**KHOA, cs=CS))) | {"ky"} | cot_he_thong
    chuoi = json.dumps(chot, ensure_ascii=False)
    for dau_hieu in ("123456789.12", "2026-10-30", "DEMO-NCC-khong-duoc-chup", "DEMO dien giai khong duoc chup"):
        assert dau_hieu not in chuoi
    assert not set(chi_tiet_demo) & set(chot)


def test_chot_khong_doc_cheo_phap_nhan():
    core = CoreGia()
    _chay_dat(core, lambda v: _them_ty_le(v, mau_12t=5), phap_nhan_id="pn-demo-khac")
    assert _chot(core) == 0
    assert core.xem_ngan(app.ma, "chot_ky") == []
    assert _ban(core, "ty_le")["mau_12t"] == "5"
