"""PL-4 ghép hồ sơ/chốt kỳ: đã kiểm bằng Core giả (CoreGia), chỉ DEMO."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
import logging
from threading import Barrier

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganEngine
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau, chot_ky, ho_so, ngan_chung, ngan_ho_so, ngan_luot, quy_trinh, ty_le
from e_phan_luong.chay import app
from e_phan_luong.kieu import DOI_TAC_MOI, NGHI_CHIA_NHO, SO_TIEN_BAT_THUONG, Tien
from e_phan_luong.phan_luong import bam_doi_tac
from test_pl2_ngan_luot import chay_ngan
from test_pl2_phan_luong import HG, KHAU, chay, lay_kq, lo_mot, tham_so
from test_pl4b_chot_ky import DAU_VAO, MA_NANG_LUC, _app_thu


MODULE = "demo_thanh_toan"
LOAI = "chi_phi_khac"
DOI_TAC = "DEMO-NCC-HANH-VI"
KHOA = {"khau": KHAU, "loai": LOAI}


@pytest.fixture(autouse=True)
def dong_ho(monkeypatch):
    ky = ["2026-11"]
    monkeypatch.setattr(chot_ky, "ky_hien_tai", lambda luc=None: ky[0])
    # ngan_ho_so dùng cùng đồng hồ cho kỳ khởi tạo hồ sơ.
    monkeypatch.setattr(ngan_ho_so, "ky_hien_tai", lambda: ky[0])
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HG)
    return ky


def _dong(ma, *, so="1100000000", ngay="2026-11-16", loai=LOAI, doi_tac=DOI_TAC, **them):
    return {**lo_mot()["nghiep_vu"][0], "ma": ma, "loai": loai, "ngay": ngay,
            "so_tien": {"so": so, "tien_te": "VND"}, "doi_tac": doi_tac,
            "dien_giai": "Diễn giải DEMO chỉ trong RAM", **them}


def _lo(*dong, ma_module=MODULE):
    lo = lo_mot()
    lo.update(ma_module=ma_module, nghiep_vu=list(dong))
    return lo


def _hs(core, *, khau=KHAU, loai=LOAI):
    ban = next(b for b in core.xem_ngan(app.ma, "ho_so_hanh_vi")
               if b["khau"] == khau and b["loai"] == loai)
    return ho_so.tu_ban_ghi(ban)


def _them_ho_so(core, hs):
    def ghi(viec):
        ngan_chung.ghi_lay_hoac_tao_nhieu(viec, "ho_so_hanh_vi", [(
            {"khau": hs.khau, "loai": hs.loai}, ho_so.ve_ban_ghi(hs))])
    assert chay_ngan(core, ghi)["trang_thai"] == "XONG"


def test_chia_nho_qua_hai_lo_cong_moi_loai_trong_khau():
    core = CoreGia()
    _, tep1, _ = lay_kq(core, chay(core, _lo(
        _dong("PC-DEMO-LO1-A"),
        _dong("PC-DEMO-LO1-B", ngay="2026-11-17", loai="tam_ung"))))
    assert all(NGHI_CHIA_NHO not in d["ly_do"] for d in tep1["nghiep_vu"])
    _, tep2, _ = lay_kq(core, chay(core, _lo(
        _dong("PC-DEMO-LO2", ngay="2026-11-19", loai="luong"))))
    dong, = tep2["nghiep_vu"]
    assert dong["luong"] == "do" and NGHI_CHIA_NHO in dong["ly_do"]
    assert {_hs(core, loai=l).so_nghiep_vu for l in (LOAI, "tam_ung", "luong")} == {1}


@pytest.mark.parametrize("doi", ["khau", "module", "doi_tac", "ngoai_7_ngay"])
def test_chia_nho_khong_lan_khau_module_doi_tac_va_cua_so(doi):
    core = CoreGia()
    lay_kq(core, chay(core, _lo(_dong("PC-DEMO-CU1"), _dong("PC-DEMO-CU2"))))
    ts = tham_so(khau="cfo_duyet" if doi == "khau" else KHAU)
    lo = _lo(_dong("PC-DEMO-MOI",
                   ngay="2026-11-23" if doi == "ngoai_7_ngay" else "2026-11-18",
                   doi_tac="DEMO-NCC-KHAC" if doi == "doi_tac" else DOI_TAC),
             ma_module="demo_khac" if doi == "module" else MODULE)
    _, tep, _ = lay_kq(core, chay(core, lo, ts))
    assert NGHI_CHIA_NHO not in tep["nghiep_vu"][0]["ly_do"]


def test_q8_nop_lai_cung_ma_van_cong_vao_ho_so(monkeypatch):
    core = CoreGia()
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: False)
    for _ in range(2):
        lay_kq(core, chay(core, _lo(_dong("PC-DEMO-NOP-LAI"))))
    hs = _hs(core)
    bam = bam_doi_tac(MODULE, DOI_TAC)
    assert hs.so_nghiep_vu == 2
    assert hs.tong_ngay[bam]["2026-11-16"] == Decimal("2200000000")
    _, tep, _ = lay_kq(core, chay(core, _lo(_dong("PC-DEMO-LAN3", ngay="2026-11-18"))))
    assert NGHI_CHIA_NHO in tep["nghiep_vu"][0]["ly_do"]


def test_doi_tac_moi_dung_anh_chup_truoc_lo_va_theo_tung_loai():
    core = CoreGia()
    _, tep1, _ = lay_kq(core, chay(core, _lo(
        _dong("PC-DEMO-L1-A", so="1000001"), _dong("PC-DEMO-L1-B", so="1000001"))))
    assert all(DOI_TAC_MOI in d["co"] for d in tep1["nghiep_vu"])
    _, tep2, _ = lay_kq(core, chay(core, _lo(
        _dong("PC-DEMO-DA-GAP", so="1000001"),
        _dong("PC-DEMO-CHUA-GAP", so="1000001", doi_tac="DEMO-NCC-MOI"),
        _dong("PC-DEMO-LOAI-MOI", so="1000001", loai="tam_ung"))))
    a, b, c = tep2["nghiep_vu"]
    assert DOI_TAC_MOI not in a["co"]
    assert DOI_TAC_MOI in b["co"] and DOI_TAC_MOI in c["co"]


def test_khoa_cho_ho_so_du_lich_su_moi_bat_co():
    core = CoreGia()
    ts = tham_so(chinh_sach_json='{"toi_thieu_ho_so_doi_tac_moi":3}')
    for i in range(4):
        _, tep, _ = lay_kq(core, chay(core, _lo(
            _dong(f"PC-DEMO-{i}", so="1000001", doi_tac=f"DEMO-NCC-{i}")), ts))
        assert (DOI_TAC_MOI in tep["nghiep_vu"][0]["co"]) == (i >= 3)


@pytest.mark.parametrize("gia_tri", [0, 1, 50, 20000])
def test_doc_khoa_chinh_sach_so_nguyen_khong_am(gia_tri):
    cs = ty_le.doc_chinh_sach(json.dumps({"toi_thieu_ho_so_doi_tac_moi": gia_tri}))
    assert cs.toi_thieu_ho_so_doi_tac_moi == gia_tri
    assert type(cs.toi_thieu_ho_so_doi_tac_moi) is int
    assert ty_le.doc_chinh_sach(None).toi_thieu_ho_so_doi_tac_moi == 0


@pytest.mark.parametrize("gia_tri", [-1, 0.5, True, None, "50", [], {}])
def test_khoa_chinh_sach_sai_bi_tu_choi(gia_tri):
    with pytest.raises(LoiNghiepVu) as exc:
        ty_le.doc_chinh_sach(json.dumps({"toi_thieu_ho_so_doi_tac_moi": gia_tri}))
    assert exc.value.ma == "THAM_SO_KHONG_HOP_LE"


@pytest.mark.parametrize("n,mong", [(49, False), (50, True)])
def test_so_tien_bat_thuong_chi_tu_50_nghiep_vu(n, mong):
    core = CoreGia()
    hs, _ = ho_so.cong(ho_so.moi(KHAU, LOAI), [
        (Tien(Decimal("1000"), "VND"), bam_doi_tac(MODULE, DOI_TAC), date(2026, 11, 15)),
    ] * n, ky="2026-11")
    _them_ho_so(core, replace(hs, ky_lam_moi="2026-11"))
    _, tep, _ = lay_kq(core, chay(core, _lo(_dong("PC-DEMO-BAT-THUONG"))))
    dong, = tep["nghiep_vu"]
    assert (SO_TIEN_BAT_THUONG in dong["co"]) is mong
    assert DOI_TAC_MOI not in dong["co"]


def test_c4_ho_so_chi_so_lieu_gop_bam_khong_ma_giao_dich_dien_giai():
    core = CoreGia()
    lo = _lo(
        _dong("PC-DEMO-AM", so="-1100000000"),
        _dong("PC-DEMO-NGOAI-TE", so_tien={"so": "123", "tien_te": "USD"}),
        _dong("PC-DEMO-QUY-DOI", so_tien={"so": "3", "tien_te": "USD"},
              so_tien_quy_doi={"so": "-1000001", "tien_te": "VND"}))
    lay_kq(core, chay(core, lo))
    hs = _hs(core)
    bam = bam_doi_tac(MODULE, DOI_TAC)
    assert hs.so_nghiep_vu == 2
    assert hs.tong_ngay[bam]["2026-11-16"] == Decimal("1101000001")
    du_lieu = core.xem_ngan(app.ma, "ho_so_hanh_vi")
    chuoi = json.dumps(du_lieu, ensure_ascii=False)
    for cam in [DOI_TAC, "Diễn giải DEMO chỉ trong RAM", *(d["ma"] for d in lo["nghiep_vu"])]:
        assert cam not in chuoi
    for bg in du_lieu:
        assert not {"so_tien", "doi_tac", "ma", "dien_giai", "ngay", "noi_dung"} & bg.keys()
    assert set(hs.doi_tac) == {bam} and len(bam) == 32


def test_doc_ho_so_khau_doc_du_trang_va_khong_lan_khau(monkeypatch):
    core = CoreGia()
    for khau, loai in [(KHAU, LOAI), (KHAU, "tam_ung"), ("cfo_duyet", LOAI)]:
        _them_ho_so(core, ho_so.moi(khau, loai))
    tim_goc = NganEngine.tim
    cac_trang = []

    def tim(ngan, bang, **kw):
        assert bang == "ho_so_hanh_vi" and kw["loc"] == {"khau": KHAU}
        cac_trang.append(kw["tiep"])
        kw["gioi_han"] = 1
        return tim_goc(ngan, bang, **kw)

    monkeypatch.setattr(NganEngine, "tim", tim)

    def kiem(viec):
        ds = ngan_ho_so.doc_ho_so_khau(viec, KHAU)
        assert set(ds) == {LOAI, "tam_ung"}
        assert all(hs.khau == KHAU and ban.row_version == 1 for hs, ban in ds.values())

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    assert len(cac_trang) == 2


def test_cas_ho_so_xung_dot_doc_lai_ap_lai_dung_mot_lan(monkeypatch):
    core = CoreGia()
    _them_ho_so(core, ho_so.moi(KHAU, LOAI))
    core.gay_xung_dot_ngan("ho_so_hanh_vi", so_lan=1)
    lan_thu_lai, so_lan_cap_nhat = [], []
    ghi_goc = ngan_chung.ghi_lo_thu_lai

    def ghi(viec, lap_lenh, **kw):
        so = ghi_goc(viec, lap_lenh, **kw)
        lan_thu_lai.append(so)
        return so

    def cap_nhat(hs):
        so_lan_cap_nhat.append(hs.so_nghiep_vu)
        return ho_so.cong(hs, [(Tien(Decimal("1000001"), "VND"), "a" * 32,
                               date(2026, 11, 16))], ky="2026-11")[0]

    monkeypatch.setattr(ngan_chung, "ghi_lo_thu_lai", ghi)
    assert chay_ngan(core, lambda v: ngan_ho_so.ghi_ho_so(v, KHAU, LOAI, cap_nhat))["trang_thai"] == "XONG"
    assert lan_thu_lai == [1] and so_lan_cap_nhat == [0, 0]
    assert _hs(core).so_nghiep_vu == 1


def test_hai_viec_cong_cung_ho_so_khong_mat_cap_nhat(monkeypatch):
    core = CoreGia()
    # Tạo bằng đúng đường runtime (lay_hoac_tao rồi sửa CAS).
    assert chay_ngan(core, lambda v: ngan_ho_so.ghi_ho_so(v, KHAU, LOAI, lambda hs: hs))["trang_thai"] == "XONG"
    hen = Barrier(2)
    so_thu = []
    ghi_goc = ngan_chung.ghi_lo_thu_lai

    def ghi(viec, lap_lenh, **kw):
        so = ghi_goc(viec, lap_lenh, **kw)
        so_thu.append(so)
        return so

    def cong(viec):
        lan = 0

        def cap_nhat(hs):
            nonlocal lan
            lan += 1
            if lan == 1:
                hen.wait(timeout=5)
            return ho_so.cong(hs, [(Tien(Decimal("1000001"), "VND"), "b" * 32,
                                   date(2026, 11, 16))], ky="2026-11")[0]

        ngan_ho_so.ghi_ho_so(viec, KHAU, LOAI, cap_nhat)

    monkeypatch.setattr(ngan_chung, "ghi_lo_thu_lai", ghi)
    cac_app = [_app_thu(cong), _app_thu(cong)]
    cac_viec = [core.giao_viec(MA_NANG_LUC, DAU_VAO) for _ in range(2)]
    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_luot = [nhom.submit(core.chay, thu, khoang_gia_han=30) for thu in cac_app]
        for luot in cac_luot:
            luot.result(timeout=10)
    assert [core.xem(v)["trang_thai"] for v in cac_viec] == ["XONG", "XONG"]
    assert sorted(so_thu) == [0, 1]
    assert _hs(core).so_nghiep_vu == 2
    assert _hs(core).tong_ngay["b" * 32]["2026-11-16"] == Decimal("2000002")


def test_ghi_ho_so_sau_dau_hoan_tat_luot(monkeypatch):
    core = CoreGia()
    thu_tu = []
    ghi_goc = core._ngan_ghi_lo

    def ghi(ma, instance, lenh, khoa, **kw):
        thu_tu.extend(c["bang"] for c in lenh)
        return ghi_goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    lay_kq(core, chay(core, _lo(_dong("PC-DEMO-THU-TU"))))
    assert thu_tu == ["dong_luot", "luot", "ho_so_hanh_vi", "ho_so_hanh_vi"]


def test_ghi_luot_that_bai_khong_cong_ho_so(monkeypatch):
    core = CoreGia()

    def hong(*a, **kw):
        raise LoiNghiepVu("NGAN_BAN", "Dữ liệu DEMO đang được cập nhật.")

    monkeypatch.setattr(ngan_luot, "ghi_luot", hong)
    kq = chay(core, _lo(_dong("PC-DEMO-LOI-GHI")))
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "NGAN_BAN"
    assert core.xem_ngan(app.ma, "ho_so_hanh_vi") == []


def test_q9_log_so_bo_chi_sau_cas_thanh_cong(caplog):
    core = CoreGia()
    hs = ho_so.HoSo(KHAU, LOAI, {"2026-11": {10: 1}},
                   {f"{i:032x}": "2026-11" for i in range(20000)}, {}, "2026-11")
    _them_ho_so(core, hs)
    core.gay_xung_dot_ngan("ho_so_hanh_vi", so_lan=1)
    with caplog.at_level(logging.WARNING, logger="e_phan_luong.quy_trinh"):
        lay_kq(core, chay(core, _lo(
            _dong("PC-DEMO-TRAN-A", so="1000001", doi_tac="DEMO-NCC-TRAN-A"),
            _dong("PC-DEMO-TRAN-B", so="1000001", doi_tac="DEMO-NCC-TRAN-B"))))
    hs = _hs(core)
    assert len(hs.doi_tac) == 20000 and hs.so_nghiep_vu == 3
    assert "0" * 32 not in hs.doi_tac and f"{1:032x}" not in hs.doi_tac
    cac_log = [r for r in caplog.records if r.name == "e_phan_luong.quy_trinh"]
    assert len(cac_log) == 1 and cac_log[0].args == (2,)
    assert "DEMO-NCC" not in cac_log[0].getMessage()


def test_bat_dau_sang_thang_lam_moi_ca_ho_so_chua_co_ty_le_dung_mot_lan(dong_ho):
    core = CoreGia()
    cac_ky = ["2025-11", "2025-12", *(f"2026-{m:02d}" for m in range(1, 12))]
    hs = ho_so.HoSo(KHAU, LOAI, {ky: {10: 1} for ky in cac_ky},
                   {sha256(ky.encode()).hexdigest()[:32]: ky for ky in cac_ky}, {}, "2026-11")
    _them_ho_so(core, hs)
    dong_ho[0] = "2026-12"
    so_chot = []
    assert chay_ngan(core, lambda v: so_chot.append(quy_trinh.bat_dau(v)))["trang_thai"] == "XONG"
    moi = _hs(core)
    assert so_chot == [0] and moi.so_nghiep_vu == 12 and moi.ky_lam_moi == "2026-12"
    assert "2025-11" not in moi.bieu_do
    assert "2025-11" not in moi.doi_tac.values()
    so_ghi = core.so_lan_ghi["ngan"]
    assert chay_ngan(core, quy_trinh.bat_dau)["trang_thai"] == "XONG"
    assert core.so_lan_ghi["ngan"] == so_ghi


def test_ho_so_moi_khong_bi_bo_nghiep_vu_trong_cung_thang():
    core = CoreGia()
    lay_kq(core, chay(core, _lo(_dong("PC-DEMO-CUNG-THANG1", so="1000001"))))
    lay_kq(core, chay(core, _lo(_dong("PC-DEMO-CUNG-THANG2", so="1000001"))))
    assert _hs(core).so_nghiep_vu == 2
    assert _hs(core).ky_lam_moi == "2026-11"
    assert core.xem_ngan(app.ma, "ty_le") == []


def test_chay_thu_demo_pl4_van_dat():
    core = CoreGia()
    cac_kq = core.chay_thu_demo(app)
    assert len(cac_kq) == 1 and all(kq["trang_thai"] == "XONG" for kq in cac_kq)
    assert core.xem_ngan(app.ma, "ho_so_hanh_vi")
