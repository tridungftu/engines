"""Ngăn PL-2: đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO."""
from dataclasses import replace
from copy import deepcopy
from decimal import Decimal

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong.chay import app
from e_phan_luong.kieu import CHON_MAU, KHONG_CHON, KetQuaDong
from e_phan_luong.ngan_luot import doc_ty_le, ghi_luot, tra_nop_lai
from e_phan_luong.ngan_chung import ghi_lay_hoac_tao_nhieu
from e_phan_luong import ty_le

KHAU = "ktt_duyet"
MODULE = "demo_thanh_toan"


def chay_ngan(core, ham):
    """Phiếu năng lực giả độc lập DEMO nghiệp vụ của phiếu runtime."""
    phieu = deepcopy(app.phieu)
    phieu["chay_thu_demo"] = []
    nl = phieu["nang_luc"][0]
    nl.update(nhan=["van_ban"], tra="van_ban")
    nl.pop("truong_ra")
    phieu["nang_luc"] = [nl]
    thu = Engine(phieu)

    @thu.nang_luc(nl["ma"])
    def kiem(viec):
        ham(viec)
        return {"loai": "van_ban", "van_ban": "DEMO"}

    return core.chay_thu(thu, nl["ma"], {"loai": "van_ban", "van_ban": "DEMO"}, {"khau": KHAU})


def luot_demo(ma="PL-DEMO", **ghi_de):
    return {"ma_luot": ma, "ma_module": MODULE, "khau": KHAU,
            "hat_giong": bytes(range(32)).hex(), "bam_dau_vao": "sha256:" + "a" * 64, **ghi_de}


def dong_demo(ma="PC-DEMO", ly_do=CHON_MAU):
    return KetQuaDong(ma, "xanh" if ly_do == KHONG_CHON else "do", (ly_do,), (), "chi_phi_khac", "module")


def test_doc_ty_le_moi_khong_ghi_va_doc_ban_da_co():
    core = CoreGia()
    cs = ty_le.ChinhSach()

    def ham(viec):
        assert doc_ty_le(viec, KHAU, "chi_phi_khac", cs) == ty_le.moi(KHAU, "chi_phi_khac", cs)
        assert core.xem_ngan(app.ma, "ty_le") == []
        tt = replace(ty_le.moi(KHAU, "chi_phi_khac", cs), bac=Decimal("0.10"), mau_12t=60)
        ghi_lay_hoac_tao_nhieu(viec, "ty_le", [(
            {"khau": KHAU, "loai": "chi_phi_khac"}, ty_le.ve_ban_ghi(tt))])
        truoc = core.xem_ngan(app.ma, "ty_le")
        assert doc_ty_le(viec, KHAU, "chi_phi_khac", cs) == tt
        assert core.xem_ngan(app.ma, "ty_le") == truoc
        assert doc_ty_le(viec, "cfo_duyet", "chi_phi_khac", cs).bac == Decimal("0.30")

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"


@pytest.mark.parametrize("ket_qua,giu_do", [(None, True), ("khong_kiem", True), ("dat", False), ("sai", False)])
@pytest.mark.parametrize("ly_do", [CHON_MAU, "NOP_LAI", "CO_DO_CUNG", "VUOT_TE"])
def test_q5_do_chi_giu_khi_chua_co_ket_qua_kiem(ket_qua, giu_do, ly_do):
    core = CoreGia()

    def ham(viec):
        ghi_luot(viec, luot_demo(), [dong_demo(ly_do=ly_do)])
        if ket_qua:
            ghi_lay_hoac_tao_nhieu(viec, "ket_qua_kiem", [(
                {"ma_luot": "PL-DEMO", "ma": "PC-DEMO", "khau": KHAU},
                {"ma_module": MODULE, "loai": "chi_phi_khac", "ket_qua": ket_qua})])
        assert tra_nop_lai(viec, MODULE, KHAU, ["PC-DEMO", "PC-DEMO-CHUA-CO"]) == (
            frozenset({"PC-DEMO"}) if giu_do else frozenset())
        assert tra_nop_lai(viec, "demo_khac", KHAU, ["PC-DEMO"]) == frozenset()
        assert tra_nop_lai(viec, MODULE, "cfo_duyet", ["PC-DEMO"]) == frozenset()

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"


@pytest.mark.parametrize("moi_nhat", [CHON_MAU, KHONG_CHON])
def test_chon_theo_tao_luc_cua_luot_khong_theo_ma_hay_dong(moi_nhat):
    core = CoreGia()

    def ham(viec):
        # Thứ tự ghi, thứ tự mã, thứ tự chữ của timestamp đều khác thứ tự thời gian.
        cu_nhat = KHONG_CHON if moi_nhat == CHON_MAU else CHON_MAU
        ghi_luot(viec, luot_demo("PL-DEMO-Z"), [dong_demo(ly_do=cu_nhat)])
        ghi_luot(viec, luot_demo("PL-DEMO-A"), [dong_demo(ly_do=moi_nhat)])
        # Dòng chưa có dấu lượt không được tính dù được ghi sau.
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", [(
            {"ma_luot": "PL-DEMO-DO-DANG", "ma": "PC-DEMO"},
            {"ma_module": MODULE, "khau": KHAU, "ly_do": cu_nhat})])
        doc_goc = viec.ngan.doc

        def doc(bang, khoa, **kw):
            bg = doc_goc(bang, khoa, **kw)
            if bg is not None and bang == "luot":
                luc = {"PL-DEMO-Z": "2026-11-20T21:00:00+07:00", "PL-DEMO-A": "2026-11-20T14:01:00+00:00"}
                return replace(bg, gia_tri={**bg.gia_tri, "tao_luc": luc[khoa["ma_luot"]]})
            return bg

        viec.ngan.doc = doc
        assert tra_nop_lai(viec, MODULE, KHAU, ["PC-DEMO"]) == (
            frozenset({"PC-DEMO"}) if moi_nhat == CHON_MAU else frozenset())

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"


def test_lich_su_phan_trang_chi_mot_ma_va_bo_qua_luot_do_dang():
    core = CoreGia()

    def ham(viec):
        # 501 lịch sử khớp cùng mã: phải đi qua trang thứ hai.
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", [(
            {"ma_luot": f"PL-DEMO-{i:04}", "ma": "PC-DEMO"},
            {"ma_module": MODULE, "khau": KHAU, "ly_do": CHON_MAU}) for i in range(501)])
        assert tra_nop_lai(viec, MODULE, KHAU, ["PC-DEMO"]) == frozenset()
        ghi_luot(viec, luot_demo("PL-DEMO-0500"), [dong_demo()])
        assert tra_nop_lai(viec, MODULE, KHAU, ["PC-DEMO"]) == frozenset({"PC-DEMO"})

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"


@pytest.mark.parametrize("n", [0, 1, 100, 101, 500])
def test_dong_truoc_luot_sau_cung_lo_khong_qua_100_va_q2(monkeypatch, n):
    core = CoreGia()
    cac_lo = []
    ghi_goc = core._ngan_ghi_lo

    def ghi(ma, instance, lenh, khoa, **kw):
        cac_lo.append(lenh)
        if lenh[0]["bang"] == "luot":
            assert len(core.xem_ngan(app.ma, "dong_luot")) == n
        return ghi_goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    ds = [dong_demo(f"PC-DEMO-{i:04}", KHONG_CHON if i % 2 else CHON_MAU) for i in range(n)]
    assert chay_ngan(core, lambda v: ghi_luot(v, luot_demo(), ds))["trang_thai"] == "XONG"
    assert [len(nhom) for nhom in cac_lo] == [min(100, n - d) for d in range(0, n, 100)] + [1]
    assert all(c["thao_tac"] == "lay_hoac_tao" for nhom in cac_lo for c in nhom)
    assert [c["bang"] for c in cac_lo[-1]] == ["luot"]
    for dong in core.xem_ngan(app.ma, "dong_luot"):
        assert dong["loai"] == "chi_phi_khac" and dong["nguon_loai"] == "module"
    assert chay_ngan(core, lambda v: ghi_luot(v, luot_demo(), ds))["trang_thai"] == "XONG"
    assert len(core.xem_ngan(app.ma, "luot")) == 1
    assert len(core.xem_ngan(app.ma, "dong_luot")) == n


def test_lo_sau_xung_dot_khong_tao_dau_hoan_tat_va_gui_lai_tiep_duoc(monkeypatch):
    core = CoreGia()
    ghi_goc = core._ngan_ghi_lo
    da_gay = []

    def ghi(ma, instance, lenh, khoa, **kw):
        if len(core.xem_ngan(app.ma, "dong_luot")) == 100 and not da_gay:
            da_gay.append(True)
            core.gay_xung_dot_ngan("dong_luot", so_lan=4)
        return ghi_goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    ds = [dong_demo(f"PC-DEMO-{i:04}") for i in range(101)]

    def ham(viec):
        with pytest.raises(LoiNghiepVu) as exc:
            ghi_luot(viec, luot_demo(), ds)
        assert exc.value.ma == "NGAN_BAN"
        assert len(core.xem_ngan(app.ma, "dong_luot")) == 100
        assert core.xem_ngan(app.ma, "luot") == []
        assert tra_nop_lai(viec, MODULE, KHAU, [d.ma for d in ds]) == frozenset()
        ghi_luot(viec, luot_demo(), ds)
        assert len(core.xem_ngan(app.ma, "luot")) == 1
        assert len(core.xem_ngan(app.ma, "dong_luot")) == 101

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"
