"""PL-9B ca nhỏ; đã kiểm bằng Core giả (CoreGia), không đo 50.000 trong pytest."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json

import pytest
from kho_tri_thuc_sdk.engine import NganXungDot
from kho_tri_thuc_sdk.thu import CoreGia

from do_hieu_nang import (CAC_CA, CACH_DEM, CoreDem, CoreChiMuc, TOI_DA_DONG,
                         app, bang_uoc_tinh, do_mot, ma_hoa, tao_lo, uoc_tinh_dem)
from test_pl0_ngan_chung import chay_ngan, ds_dong


@pytest.mark.parametrize("ca", CAC_CA)
def test_do_nho_va_dem_khop_core_gia(ca):
    goc = do_mot(ca, 12, lop_core=CoreDem)
    nhanh = do_mot(ca, 12, lop_core=CoreChiMuc, bo_nho=True)
    assert goc["dem"] == nhanh["dem"]
    assert goc["sha256"] == nhanh["sha256"]
    assert goc["ket_qua_dem"] == nhanh["ket_qua_dem"]
    assert nhanh["giay_co_tracemalloc"] > 0
    assert goc["tong_goi"] == sum(goc["dem"].get(k, 0) for k in CACH_DEM)
    assert 0 < nhanh["giay"] < nhanh["thoi_han_giay"] / 2
    assert nhanh["MB"] == round(nhanh["tracemalloc_dinh_byte"] / 1000000, 3)
    assert nhanh["MB"] > 0
    assert nhanh["dem"]["tai_tep_vao"] == 1
    if not ca.startswith("ghi"):
        assert nhanh["dem"]["tra_nop_lai_tim"] == 12
        assert nhanh["dem"]["tai_tep_ra"] == 2


@pytest.mark.parametrize("lop", [CoreGia, CoreChiMuc])
def test_chi_muc_loc_sort_phan_trang_cas_nguyen_tu_idem(lop):
    core = lop()
    def ham(viec):
        for dau in range(0, 120, 100):
            with viec.ngan.lo() as lo:
                for khoa, gt in ds_dong(120)[dau:dau + 100]:
                    lo.lay_hoac_tao("dong_luot", khoa, gt)
        loc = {"ma_module": "demo_thanh_toan", "khau": "ktt_duyet"}
        ds, tiep = [], None
        while True:
            trang = viec.ngan.tim("dong_luot", loc=loc, gioi_han=17, tiep=tiep,
                                  sap_xep=[{"truong": "ma", "giam": True}])
            ds.extend(d.gia_tri["ma"] for d in trang.danh_sach)
            tiep = trang.tiep
            if tiep is None:
                break
        assert ds == sorted([k["ma"] for k, _ in ds_dong(120)], reverse=True)
        khoa, _ = ds_dong(1)[0]
        bg = viec.ngan.doc("dong_luot", khoa)
        with pytest.raises(NganXungDot):
            with viec.ngan.lo() as lo:
                lo.lay_hoac_tao("dong_luot", {**khoa, "ma": "PC-DEMO-ROLLBACK"},
                               {"ma_module": "demo_thanh_toan", "khau": "ktt_duyet", "ly_do": "KHONG_CHON"})
                lo.sua("dong_luot", khoa, {"ly_do": "CHON_MAU"}, row_version=999)
        assert viec.ngan.doc("dong_luot", {**khoa, "ma": "PC-DEMO-ROLLBACK"}) is None
        assert viec.ngan.doc("dong_luot", khoa).row_version == bg.row_version
        with viec.ngan.lo() as lo:
            lo.sua("dong_luot", khoa, {"ly_do": "CHON_MAU"}, row_version=bg.row_version)
        assert viec.ngan.doc("dong_luot", khoa).row_version == bg.row_version + 1
        assert viec.ngan.tim("dong_luot", loc={"ly_do": "CHON_MAU"}).danh_sach[0].gia_tri["ma"] == khoa["ma"]
        # Lô tạo lại giữ nguyên bản ghi đã sửa; unique "them" phải xung đột.
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("dong_luot", khoa, {"ly_do": "KHONG_CHON"})
        assert viec.ngan.doc("dong_luot", khoa).gia_tri["ly_do"] == "CHON_MAU"
        with pytest.raises(NganXungDot):
            with viec.ngan.lo() as lo:
                lo.them("dong_luot", {**khoa, "ma_module": "demo_thanh_toan", "khau": "ktt_duyet", "ly_do": "KHONG_CHON"})
        # Kiểm cả lọc bằng số, giá trị CoreGia chuẩn hóa thành chuỗi.
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("ty_le", {"khau": "ktt_duyet", "loai": "chi_phi_demo"}, {"bac": "0.30"})
        assert len(viec.ngan.tim("ty_le", loc={"bac": 0.3}).danh_sach) == 1
    kq = chay_ngan(core, ham)
    assert kq["trang_thai"] == "XONG", kq
    assert len(core.xem_ngan(app.ma, "dong_luot")) == 120


@pytest.mark.parametrize("lop", [CoreGia, CoreChiMuc])
def test_chi_muc_het_han_phap_nhan_mat_phan_hoi(lop):
    core = lop()
    def ham(viec):
        khoa, gt = ds_dong(1)[0]
        core.gay_mat_xac_nhan("ngan", 1)
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("dong_luot", khoa, gt)
        assert len(core.xem_ngan(app.ma, "dong_luot")) == 1
        # Chỉ sửa thời gian hệ thống trong fake để kiểm nhánh hết hạn.
        rows = (core.kho[app.ma, "dong_luot"].values() if isinstance(core, CoreChiMuc)
                else core._ngan[app.ma, "dong_luot"])
        for d in rows:
            d["het_han_luc"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        assert viec.ngan.doc("dong_luot", khoa) is None
        assert viec.ngan.doc("dong_luot", khoa, gom_het_han=True) is not None
        assert not viec.ngan.tim("dong_luot", loc=khoa).danh_sach
        assert len(viec.ngan.tim("dong_luot", loc=khoa, gom_het_han=True).danh_sach) == 1
        core._viec[viec.id]["phap_nhan_id"] = 999
        assert viec.ngan.doc("dong_luot", khoa, gom_het_han=True) is None
    kq = chay_ngan(core, ham)
    assert kq["trang_thai"] == "XONG", kq


def test_ngoai_suy_va_cong_thuc_do_tre():
    mau = [{"ca": "json_trong", "so_dong": n, "dem": {"doc": 2*n+3, "tim": n+2,
            "lo_ghi": n//100+1, "tai_tep_vao": 1, "tai_tep_ra": 2,
            "tra_nop_lai_tim": n}} for n in (1000, 5000, 10000)]
    dem = uoc_tinh_dem(mau)
    assert dem["doc"]["uoc_tinh"] == 100003
    assert dem["tra_nop_lai_tim"]["uoc_tinh"] == 50000
    bang = bang_uoc_tinh(mau, [{"ca": "json_trong", "so_dong": 50000,
                               "giay": 10, "thoi_han_giay": 300}])
    assert [d["tre_ms"] for d in bang] == [2, 5, 10]
    for d in bang:
        assert d["giay_uoc_tinh"] == round(10 + d["tong_goi_uoc_tinh"] * d["tre_ms"] / 1000, 3)
        assert d["co_lo_an_toan_uoc_tinh_du_2_lan"] <= 50000
        assert "ước tính" in d["nhan"]


def test_mau_demo_tat_dinh_va_dung_tran():
    assert TOI_DA_DONG == 50000
    a, b = ma_hoa(tao_lo(3)), ma_hoa(tao_lo(3))
    assert a == b
    assert len({d["ma"] for d in json.loads(a)["nghiep_vu"]}) == 3
    assert "Công ty DEMO Ánh Dương" in a.decode("utf-8")


@pytest.mark.parametrize("so", [0, TOI_DA_DONG + 1])
def test_khong_sinh_lo_vuot_tran(so):
    with pytest.raises(ValueError):
        tao_lo(so)
