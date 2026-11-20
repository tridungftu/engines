"""Bảy điểm sau rà soát PL-2/PL-3; đã kiểm bằng Core giả (CoreGia).

Chỉ dữ liệu DEMO; kiểm retry trên cùng việc SDK, CAS sau lần chạy dở,
hết hạn và thứ tự phân trang theo khóa khai báo trong phiếu.
"""
from copy import copy, deepcopy
from dataclasses import replace
from decimal import Decimal, localcontext
from hashlib import sha256
import json

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau, doi_bac, ket_qua, ngan_chung, ngan_ket_qua, quy_trinh, tien, ty_le
from e_phan_luong.chay import app
from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.loi import CAU_LOI
from e_phan_luong.ngan_luot import ghi_luot, tra_nop_lai
from test_pl2_ngan_luot import chay_ngan, dong_demo, luot_demo
from test_pl2_phan_luong import HG, KHAU, chay, lay_kq, lo_mot, tham_so
from test_pl3_ngan_ket_qua import (
    THAM_SO, chay_ghi, dong_demo as dong_kiem, dung_luot, kiem_loi,
    ma_hoa, tep_demo, trong_viec, truong,
)


def _chay_trong_viec(core, viec, raw):
    viec.tham_so = tham_so()
    kq = quy_trinh.chay_phan_luong(viec, doc_lo_json(raw), raw)
    return kq, core.doc_tep(kq["tep_json"]["tep_id"])


@pytest.mark.parametrize("bat_buoc", [False, True])
def test_m1_core_giao_lai_cung_viec_dung_hat_giong_da_luu_va_cung_bytes(monkeypatch, bat_buoc):
    core = CoreGia()
    raw = ma_hoa(lo_mot(co_do_cung=bat_buoc))
    cac_lan_sinh = []

    def sinh():
        cac_lan_sinh.append(True)
        assert len(cac_lan_sinh) == 1, "Giao lại phải dùng hạt giống đã lưu."
        return HG

    monkeypatch.setattr(chon_mau, "sinh_hat_giong", sinh)
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: True)

    def kiem(viec):
        t1, raw1 = _chay_trong_viec(core, viec, raw)
        cu = {b: core.xem_ngan(app.ma, b) for b in ("luot", "dong_luot")}
        giao_lai = copy(viec)
        giao_lai.lan_thu += 1
        t2, raw2 = _chay_trong_viec(core, giao_lai, raw)
        bam = "sha256:" + sha256(raw).hexdigest()
        ma = "PL-" + sha256(("e_phan_luong|luot|" + viec.id + "|" + bam).encode("utf-8")).hexdigest()
        assert t1["ma_luot"] == t2["ma_luot"] == ma
        assert t1["bam_hat_giong"] == t2["bam_hat_giong"] == chon_mau.bam_hat_giong(HG)
        assert raw1 == raw2
        assert json.loads(raw2)["nghiep_vu"][0]["ly_do"] == (["CO_DO_CUNG"] if bat_buoc else ["CHON_MAU"])
        assert {b: core.xem_ngan(app.ma, b) for b in cu} == cu

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    assert len(cac_lan_sinh) == 1


def test_m1_tai_hien_cung_hat_giong_dau_vao_viec_id_va_viec_moi_co_ma_moi(monkeypatch):
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HG)
    raw = ma_hoa(lo_mot())
    cac_kq = []
    for _ in range(2):
        core = CoreGia()

        def kiem(viec):
            kq, noi_dung = _chay_trong_viec(core, viec, raw)
            cac_kq.append((viec.id, kq["ma_luot"], noi_dung))

        assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    assert cac_kq[0] == cac_kq[1]
    cac_ma = []
    core = CoreGia()
    for _ in range(2):
        def kiem(viec):
            kq, _ = _chay_trong_viec(core, viec, raw)
            cac_ma.append(kq["ma_luot"])
        assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    assert len(set(cac_ma)) == 2  # Cùng hạt giống và đầu vào vẫn khác nếu khác việc.


def test_m1_dau_vao_khac_cung_viec_co_ma_luot_khac(monkeypatch):
    core = CoreGia()
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HG)

    def kiem(viec):
        kq1, _ = _chay_trong_viec(core, viec, ma_hoa(lo_mot(co_do_cung=True)))
        kq2, raw2 = _chay_trong_viec(core, viec, ma_hoa(lo_mot()))
        assert kq1["ma_luot"] != kq2["ma_luot"]
        assert json.loads(raw2)["nghiep_vu"][0]["ly_do"] == ["NOP_LAI"]

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"


@pytest.mark.parametrize("thay_doi", ["ty_le", "lich_su"])
def test_m1_giao_lai_khong_doi_quyet_dinh_da_chot_khi_ngan_da_thay_doi(monkeypatch, thay_doi):
    core = CoreGia()
    raw = ma_hoa(lo_mot())
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HG)
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: a[-1] == 1)

    def kiem(viec):
        _, raw1 = _chay_trong_viec(core, viec, raw)
        assert json.loads(raw1)["nghiep_vu"][0]["ly_do"] == ["KHONG_CHON"]
        if thay_doi == "ty_le":
            tt = replace(ty_le.moi(KHAU, "chi_phi_khac", ty_le.ChinhSach()), che_do="toan_bo")
            ngan_chung.ghi_lay_hoac_tao_nhieu(viec, "ty_le", [(
                {"khau": KHAU, "loai": "chi_phi_khac"}, ty_le.ve_ban_ghi(tt))])
        else:
            ghi_luot(viec, luot_demo("PL-DEMO-MOI"), [dong_demo("PC-DEMO-001")])
        _, raw2 = _chay_trong_viec(core, copy(viec), raw)
        assert raw2 == raw1

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"


def test_m1_chay_do_sua_cas_ca_tram_dong_cu_theo_hat_giong_moi(monkeypatch):
    core = CoreGia()
    lo = lo_mot()
    lo["nghiep_vu"] = [{**lo["nghiep_vu"][0], "ma": f"PC-DEMO-{i:04}"} for i in range(101)]
    raw = ma_hoa(lo)
    hg_moi = bytes(reversed(HG))
    cac_hat = iter((HG, hg_moi))
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: next(cac_hat))
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda hg, *a: hg == hg_moi)
    ghi_goc = core._ngan_ghi_lo
    da_gay = []
    cac_lo = []

    def ghi(ma, instance, lenh, khoa, **kw):
        cac_lo.append(deepcopy(lenh))
        if len(core.xem_ngan(app.ma, "dong_luot")) == 100 and not da_gay:
            da_gay.append(True)
            core.gay_xung_dot_ngan("dong_luot", so_lan=4)
        return ghi_goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)

    def kiem(viec):
        with pytest.raises(LoiNghiepVu) as exc:
            _chay_trong_viec(core, viec, raw)
        assert exc.value.ma == "NGAN_BAN"
        assert core.xem_ngan(app.ma, "luot") == []
        cu = core.xem_ngan(app.ma, "dong_luot")
        assert len(cu) == 100 and all(d["ly_do"] == "KHONG_CHON" for d in cu)
        core.gay_xung_dot_ngan("dong_luot", so_lan=1)  # CAS cũng phải thử lại.
        kq, raw_moi = _chay_trong_viec(core, copy(viec), raw)
        ds = core.xem_ngan(app.ma, "dong_luot")
        assert len(ds) == 101 and all(d["ly_do"] == "CHON_MAU" for d in ds)
        assert all((d["loai"], d["nguon_loai"]) == ("chi_phi_khac", "module") for d in ds)
        assert all(d["row_version"] == 2 for d in ds if d["ma"] != "PC-DEMO-0100")
        luot, = core.xem_ngan(app.ma, "luot")
        assert luot["hat_giong"] == hg_moi.hex() and luot["ma_luot"] == kq["ma_luot"]
        assert all(d["ma_luot"] == luot["ma_luot"] for d in ds)
        assert all(d["ly_do"] == ["CHON_MAU"] for d in json.loads(raw_moi)["nghiep_vu"])
        assert any(len(nhom) == 100 and all(c["thao_tac"] == "sua" and c["row_version"] == 1 for c in nhom)
                   for nhom in cac_lo)
        assert all(len(nhom) <= 100 for nhom in cac_lo)
        # Lead PL-4: luot nằm ở lô cuối cùng, đi cùng phép cộng hồ sơ (nguyên tử).
        vi_tri_luot = next(i for i, nhom in enumerate(cac_lo) if any(c["bang"] == "luot" for c in nhom))
        assert vi_tri_luot == len(cac_lo) - 1
        assert [c["bang"] for c in cac_lo[vi_tri_luot]] == ["ho_so_hanh_vi", "luot"]

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"


@pytest.mark.parametrize("bac_cu,bac_mong", [("0.30", "0.40"), ("0.20", "0.25"), ("0.10", "0.15"), ("0.01", "0.05")])
@pytest.mark.parametrize("nguon", ["chon_mau", "bat_buoc"])
def test_m3_thang_moi_chon_bac_gan_nhat_khong_thap_hon_va_khong_xuong_ngay(bac_cu, bac_mong, nguon):
    cs = replace(ty_le.ChinhSach(), bac=tuple(map(Decimal, ("0.40", "0.25", "0.15", "0.05"))))
    cu = replace(ty_le.moi(KHAU, "chi_phi_demo", cs), bac=Decimal(bac_cu),
                 mau_tu_doi_bac=1000, mau_12t=1000)
    moi, doi = doi_bac.cap_nhat(cu, doi_bac.MotKetQua(nguon, "dat"), cs, luc="2026-11-20T22:10:00+07:00")
    assert doi and moi.bac == Decimal(bac_mong) >= cu.bac
    assert moi.che_do == "bac" and moi.mau_tu_doi_bac == moi.loi_tu_doi_bac == 0
    assert moi.mau_12t == 1000 + int(nguon == "chon_mau")
    assert moi.doi_bac_luc == "2026-11-20T22:10:00+07:00"
    assert cu.mau_tu_doi_bac == 1000


def test_m3_loi_nho_sau_doi_thang_van_len_mot_bac_va_thang_qua_thap_kiem_toan_bo():
    cs = replace(ty_le.ChinhSach(), bac=tuple(map(Decimal, ("0.40", "0.25", "0.15", "0.05"))))
    cu = replace(ty_le.moi(KHAU, "chi_phi_demo", cs), bac=Decimal("0.20"))
    moi, doi = doi_bac.cap_nhat(cu, doi_bac.MotKetQua("chon_mau", "sai", "nho"), cs, luc="DEMO")
    assert doi and moi.bac == Decimal("0.40") and moi.loi_12t == 1
    cu = replace(cu, bac=Decimal("0.80"))
    moi, doi = doi_bac.cap_nhat(cu, doi_bac.MotKetQua("chon_mau", "dat"), cs, luc="DEMO")
    assert doi and moi.bac in cs.bac and moi.che_do == "toan_bo"
    assert ty_le.p_bac(moi, cs) == 1


@pytest.mark.parametrize("ket_qua_cu,giu_do", [("dat", False), ("sai", False), ("khong_kiem", True)])
def test_t1_ket_qua_het_365_ngay_khong_lam_nop_lai_giu_do_sai(monkeypatch, ket_qua_cu, giu_do):
    core = CoreGia()

    def kiem(viec):
        ghi_luot(viec, luot_demo(), [dong_demo()])
        ngan_chung.ghi_lay_hoac_tao_nhieu(viec, "ket_qua_kiem", [(
            {"ma_luot": "PL-DEMO", "ma": "PC-DEMO", "khau": KHAU},
            {"ma_module": "demo_thanh_toan", "loai": "chi_phi_khac", "ket_qua": ket_qua_cu})])
        monkeypatch.setattr(core, "_con_han", lambda d: "ket_qua" not in d)
        assert viec.ngan.doc("ket_qua_kiem", {"ma_luot": "PL-DEMO", "ma": "PC-DEMO", "khau": KHAU}) is None
        assert tra_nop_lai(viec, "demo_thanh_toan", KHAU, ["PC-DEMO"]) == (
            frozenset({"PC-DEMO"}) if giu_do else frozenset())

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"


@pytest.mark.parametrize("bang", [b["bang"] for b in app.phieu["ngan_du_lieu"]])
def test_t2_moi_trang_sap_xep_du_cac_cot_khoa_theo_phieu(monkeypatch, bang):
    core = CoreGia()
    cot_khoa = next(b["khoa"] for b in app.phieu["ngan_du_lieu"] if b["bang"] == bang)

    def kiem(viec):
        ds = [({cot: f"demo_{i:02}" for cot in cot_khoa}, {}) for i in (2, 0, 1)]
        ngan_chung.ghi_lay_hoac_tao_nhieu(viec, bang, ds)
        tim_goc = viec.ngan.tim
        cac_trang = []

        def tim(b, **kw):
            assert b == bang
            assert kw["sap_xep"] == [{"truong": cot, "giam": False} for cot in cot_khoa]
            cac_trang.append(kw["tiep"])
            return tim_goc(b, **kw)

        monkeypatch.setattr(viec.ngan, "tim", tim)
        ds_doc = ngan_chung.tim_tat_ca(viec, bang, {}, gioi_han=1)
        assert [tuple(d.gia_tri[c] for c in cot_khoa) for d in ds_doc] == [
            tuple(f"demo_{i:02}" for c in cot_khoa) for i in (0, 1, 2)]
        assert len(cac_trang) == 3 and cac_trang[0] is None
        assert cac_trang[1] is not None and cac_trang[2] != cac_trang[1]

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"


def test_t3_module_cai_dat_khac_tep_tu_choi_truoc_khi_ghi():
    core = CoreGia()
    kq = chay(core, lo_mot(), tham_so(ma_module="demo_khac"))
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"] == {"ma": "DU_LIEU_KHONG_HOP_LE", "thong_diep": CAU_LOI["DU_LIEU_KHONG_HOP_LE"], "thu_lai_duoc": False}
    assert all(core.xem_ngan(app.ma, b["bang"]) == [] for b in app.phieu["ngan_du_lieu"])


@pytest.mark.parametrize("module", ["", "demo_thanh_toan"])
def test_t3_module_trong_hoac_khop_tep_van_phan_luong(module):
    core = CoreGia()
    _, tep, _ = lay_kq(core, chay(core, lo_mot(), tham_so(ma_module=module)))
    assert tep["ma_module"] == "demo_thanh_toan"


@pytest.mark.parametrize("so", ["1000000.000000000", "0.000001000000000", "-999999999999999999.9999990000", "0.000000000000000"])
def test_t4_bo_so_khong_le_thua_truoc_khi_dem_dung_chung_luat_tien(so):
    t = {"so": so, "tien_te": "VND"}
    raw = ma_hoa(tep_demo([dong_kiem(ket_qua="sai", so_tien_sai=t)]))
    with localcontext() as ctx:
        ctx.prec = 6
        dong, = ket_qua.doc_ket_qua_json(raw).dong
        assert dong.so_tien_sai == tien.doc_tien(t)
        assert dong.so_tien_sai.so == Decimal(so)


@pytest.mark.parametrize("so", ["1.0000001", "1000000000000000000.0000000", "+1", "1e3", "NaN", True, 1.5])
def test_t4_so_khong_hop_le_bi_tu_choi_nhu_luat_tien_chung(so):
    for doc in (ket_qua._doc_tien, tien.doc_tien):
        with pytest.raises(LoiNghiepVu) as exc:
            doc({"so": so, "tien_te": "VND"})
        assert exc.value.ma == "DU_LIEU_KHONG_HOP_LE"


@pytest.mark.parametrize("nguong_json", ["{DEMO", "[]", '{"pm":0}', 42, {"pm": "DEMO"}])
@pytest.mark.parametrize("cac_kq", [[], ["dat"], ["dat", "khong_kiem"]])
def test_t5_khong_co_sai_bo_qua_ca_nguong_tep_va_cai_dat_hong(nguong_json, cac_kq, monkeypatch):
    core = CoreGia()
    dung_luot(core, len(cac_kq))
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo(
        [dong_kiem(i, ket_qua=kq) for i, kq in enumerate(cac_kq)], nguong={"pm": "DEMO-hong"})))

    def cam_doc(*a, **kw):
        raise AssertionError("Không có dòng sai thì không được đọc/kiểm ngưỡng.")

    monkeypatch.setattr(ngan_ket_qua.nguong, "doc_nguong", cam_doc)

    def ghi(viec):
        viec.tham_so = {**THAM_SO, "nguong_json": nguong_json}
        return ngan_ket_qua.ghi_ket_qua(viec, tep)

    dem = trong_viec(core, ghi)
    assert dem["so_dong_nhan"] == len(cac_kq) and dem["so_trung"] == 0


@pytest.mark.parametrize("nguong_json,ma_loi", [("{DEMO", "THAM_SO_KHONG_HOP_LE"), (None, "THIEU_NGUONG")])
def test_t5_chi_mot_dong_sai_cung_bat_buoc_kiem_nguong_truoc_moi_lenh_ghi(nguong_json, ma_loi):
    core = CoreGia()
    dung_luot(core, 2)
    tep = tep_demo([dong_kiem(), dong_kiem(1, ket_qua="sai", so_tien_sai={"so": "1000000", "tien_te": "VND"})], nguong=None)
    kiem_loi(chay_ghi(core, tep, ts={"nguong_json": nguong_json}), ma_loi)
    assert core.xem_ngan(app.ma, "ket_qua_kiem") == core.xem_ngan(app.ma, "ty_le") == []
