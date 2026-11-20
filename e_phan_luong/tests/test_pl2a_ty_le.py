"""Chính sách Anh duyệt và chuyển đổi đúng các cột bảng ty_le."""
import json
import sys
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import ty_le
from e_phan_luong.kieu import (
    CHE_DO_BAC, CHE_DO_TOAN_BO, CHUA_PHAN_LOAI, CUOI_KY, DOI_TAC_MOI,
    NGAY_NGHI, NHAP_TAY, NHAN_LOI_NGOAI_MAU, NHAN_RUI_RO_CAO,
    SO_TIEN_BAT_THUONG, SO_TRON,
)
from e_phan_luong.loi import CAU_LOI, loi


@pytest.mark.parametrize("chuoi", [None, "", "   ", "{}"])
def test_mac_dinh_dung_toan_bo_chinh_sach_anh_duyet(chuoi):
    cs = ty_le.doc_chinh_sach(chuoi)
    assert cs.bac == tuple(map(Decimal, ("0.30", "0.20", "0.10", "0.05")))
    assert cs.nguong_xuong == tuple(map(Decimal, ("0.10", "0.05", "0.03")))
    assert cs.mau_toi_thieu == tuple(map(Decimal, ("30", "60", "100")))
    assert cs.ty_le_chua_phan_loai == Decimal("0.30")
    assert cs.mau_sach_toan_bo == Decimal(30)
    assert cs.nguong_diem_rui_ro == Decimal("0.10")
    assert cs.do_tin_cay == Decimal("0.95")
    assert cs.he_so == {
        SO_TIEN_BAT_THUONG: Decimal(2), DOI_TAC_MOI: Decimal(2),
        SO_TRON: Decimal("1.5"), NGAY_NGHI: Decimal("1.5"),
        CUOI_KY: Decimal("1.5"), NHAP_TAY: Decimal("1.5"),
    }
    assert cs.don_vi_so_tron == Decimal(10000000)
    assert cs.ty_le_duoi_sad == Decimal("0.02")
    assert cs.san == Decimal("0.05")
    for f in fields(cs):
        gia_tri = getattr(cs, f.name)
        cac_so = gia_tri.values() if isinstance(gia_tri, dict) else gia_tri if isinstance(gia_tri, tuple) else (gia_tri,)
        assert all(isinstance(so, Decimal) for so in cac_so)
    with pytest.raises(FrozenInstanceError):
        cs.san = Decimal("0.1")


def test_json_ghi_de_tung_khoa_va_he_so_tung_co():
    cs = ty_le.doc_chinh_sach(json.dumps({
        "bac": [0.4, 0.25, 0.1], "nguong_xuong": [0.08, 0.04],
        "mau_toi_thieu": [40, 80], "ty_le_chua_phan_loai": 0.35,
        "mau_sach_toan_bo": 40, "nguong_diem_rui_ro": 0.12,
        "do_tin_cay": 0.99, "he_so": {SO_TRON: 3},
        "don_vi_so_tron": 20000000, "ty_le_duoi_sad": 0.04, "san": 0.06,
    }))
    assert cs.bac == tuple(map(Decimal, ("0.4", "0.25", "0.1")))
    assert cs.nguong_xuong == (Decimal("0.08"), Decimal("0.04"))
    assert cs.mau_toi_thieu == (Decimal(40), Decimal(80))
    assert cs.ty_le_chua_phan_loai == Decimal("0.35")
    assert cs.mau_sach_toan_bo == Decimal(40)
    assert cs.nguong_diem_rui_ro == Decimal("0.12")
    assert cs.do_tin_cay == Decimal("0.99")
    assert cs.he_so[SO_TRON] == Decimal(3)
    assert cs.he_so[DOI_TAC_MOI] == Decimal(2)
    assert cs.don_vi_so_tron == Decimal(20000000)
    assert cs.ty_le_duoi_sad == Decimal("0.04")
    assert cs.san == Decimal("0.06")
    assert ty_le.doc_chinh_sach(None).he_so[SO_TRON] == Decimal("1.5")


def test_tham_so_duoi_sad_thay_mac_dinh_va_json_ghi_de():
    assert ty_le.doc_chinh_sach(None, ty_le_duoi_sad=Decimal("0.04")).ty_le_duoi_sad == Decimal("0.04")
    assert ty_le.doc_chinh_sach('{"ty_le_duoi_sad": 0.03}', ty_le_duoi_sad=Decimal("0.04")).ty_le_duoi_sad == Decimal("0.03")


@pytest.mark.parametrize("chuoi", [
    "[]", "null", "3", "true", "{", '{"khoa_la": 1}', '{"bac": null}',
    '{"bac": []}', '{"bac": [0.1, 0.2, 0.3, 0.4]}',
    '{"bac": [0.3, 0.2, 0.2, 0.05]}', '{"bac": [1.1, 0.2, 0.1, 0.05]}',
    '{"bac": [0.3, 0.2, 0.1, 0]}', '{"bac": [0.3, 0.2, 0.1]}',
    '{"bac": ["0.3", 0.2, 0.1, 0.05]}', '{"bac": [true, 0.2, 0.1, 0.05]}',
    '{"nguong_xuong": [0.1, 0.05]}', '{"nguong_xuong": [1.1, 0.05, 0.03]}',
    '{"mau_toi_thieu": [30, 60]}', '{"mau_toi_thieu": [30.5, 60, 100]}',
    '{"mau_toi_thieu": [0, 60, 100]}', '{"mau_sach_toan_bo": -1}',
    '{"he_so": []}', '{"he_so": {"SO_TRON": 0.99}}',
    '{"he_so": {"SO_TRON": true}}', '{"he_so": {"CO_LA": 2}}',
    '{"he_so": {"SO_TRON": NaN}}', '{"do_tin_cay": 0}', '{"do_tin_cay": 1}',
    '{"san": -0.1}', '{"ty_le_duoi_sad": 1.1}', '{"don_vi_so_tron": 0}',
    '{"do_tin_cay": Infinity}', '{"do_tin_cay": 0.95, "do_tin_cay": 0.9}',
])
def test_chinh_sach_sai_bi_tu_choi_dung_ma_va_cau(chuoi):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        ty_le.doc_chinh_sach(chuoi)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"
    assert bat.value.thong_diep == CAU_LOI[bat.value.ma]


def test_gioi_han_tam_kib_khong_cat_ngam():
    assert ty_le.doc_chinh_sach("{}" + " " * 8190) == ty_le.ChinhSach()
    for chuoi in ("{}" + " " * 8191, " " * 8193):
        with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
            ty_le.doc_chinh_sach(chuoi)
        assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"


@pytest.mark.parametrize("gia_tri", [True, 0.03, "0.03", Decimal("NaN"), Decimal("1.1")])
def test_tham_so_duoi_sad_sai(gia_tri):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        ty_le.doc_chinh_sach(None, ty_le_duoi_sad=gia_tri)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"


def test_moi_khoi_tao_dung_bac_va_cac_bo_dem():
    tt = ty_le.moi("kt_kiem", "thanh_toan_demo", ty_le.ChinhSach())
    assert tt.khau == "kt_kiem" and tt.loai == "thanh_toan_demo"
    assert tt.bac == Decimal("0.30") and tt.che_do == CHE_DO_BAC
    assert (tt.mau_tu_doi_bac, tt.loi_tu_doi_bac, tt.mau_sach_toan_bo,
            tt.mau_12t, tt.loi_12t, tt.loi_sad_12t, tt.loi_ngoai_mau_12t) == (0,) * 7
    assert tt.diem is None and tt.nhan == frozenset() and tt.doi_bac_luc is None
    with pytest.raises(FrozenInstanceError):
        tt.bac = Decimal("0.20")


@pytest.mark.parametrize("che_do", [CHE_DO_BAC, CHE_DO_TOAN_BO])
@pytest.mark.parametrize("diem", [None, Decimal("0.123456")])
def test_ban_ghi_khu_hoi_va_chi_co_dung_cot(che_do, diem):
    tt = ty_le.TrangThai(
        "kt_kiem", "thanh_toan_demo", Decimal("0.10"), che_do,
        29, 2, 7, 100, 3, 2, 1, diem,
        frozenset({NHAN_RUI_RO_CAO, NHAN_LOI_NGOAI_MAU}), "2026-11-20T19:46:00+07:00",
    )
    ban_ghi = ty_le.ve_ban_ghi(tt)
    assert set(ban_ghi) == {
        "khau", "loai", "bac", "che_do", "mau_tu_doi_bac", "loi_tu_doi_bac",
        "mau_sach_toan_bo", "mau_12t", "loi_12t", "loi_sad_12t", "loi_ngoai_mau_12t",
        "diem", "nhan", "doi_bac_luc",
    }
    assert ban_ghi["nhan"] == "loi_ngoai_mau,rui_ro_cao"
    assert ban_ghi["bac"] == "0.10"
    assert ban_ghi["mau_12t"] == "100"
    assert ty_le.tu_ban_ghi({**ban_ghi, "row_version": 7, "id": "DEMO"}) == tt


def test_ban_ghi_moi_khu_hoi_va_so_khong_dung_so_mu():
    tt = ty_le.moi("kt_kiem", "thanh_toan_demo", ty_le.ChinhSach())
    assert ty_le.tu_ban_ghi(ty_le.ve_ban_ghi(tt)) == tt
    tt = replace(tt, diem=Decimal("1E-7"))
    assert ty_le.ve_ban_ghi(tt)["diem"] == "0.0000001"


@pytest.mark.parametrize("cot,gia_tri", [("bac", "NaN"), ("mau_12t", "1.5"), ("mau_12t", "-1"), ("loi_12t", "1"), ("che_do", "khac")])
def test_ban_ghi_hong_khong_bien_thanh_trang_thai(cot, gia_tri):
    ban_ghi = ty_le.ve_ban_ghi(ty_le.moi("kt_kiem", "thanh_toan_demo", ty_le.ChinhSach()))
    ban_ghi[cot] = gia_tri
    with pytest.raises(type(loi("DU_LIEU_KHONG_HOP_LE"))) as bat:
        ty_le.tu_ban_ghi(ban_ghi)
    assert bat.value.ma == "DU_LIEU_KHONG_HOP_LE"


def test_p_bac_dung_ba_nhanh_va_thu_tu_uu_tien():
    cs = ty_le.ChinhSach()
    tt = replace(ty_le.moi("kt_kiem", "thanh_toan_demo", cs), bac=Decimal("0.10"))
    assert ty_le.p_bac(tt, cs) == Decimal("0.10")
    assert ty_le.p_bac(replace(tt, loai=CHUA_PHAN_LOAI), cs) == Decimal("0.30")
    assert ty_le.p_bac(replace(tt, che_do=CHE_DO_TOAN_BO), cs) == Decimal(1)
    assert ty_le.p_bac(replace(tt, che_do=CHE_DO_TOAN_BO, loai=CHUA_PHAN_LOAI), cs) == Decimal(1)
