"""Kiểm cờ PL-2B bằng dữ liệu DEMO, độc lập ChinhSach của PL-2A."""
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import co
from e_phan_luong.kieu import (
    CUOI_KY,
    DOI_TAC_MOI,
    NGAY_NGHI,
    NHAP_TAY,
    SO_TIEN_BAT_THUONG,
    SO_TRON,
    NghiepVu,
    Tien,
)


def chinh_sach_demo():
    return SimpleNamespace(
        don_vi_so_tron=Decimal("10000000"),
        he_so={
            SO_TIEN_BAT_THUONG: Decimal("2"),
            DOI_TAC_MOI: Decimal("2"),
            SO_TRON: Decimal("1.5"),
            NGAY_NGHI: Decimal("1.5"),
            CUOI_KY: Decimal("1.5"),
            NHAP_TAY: Decimal("1.5"),
        },
    )


def nghiep_vu_demo(**thay):
    return replace(
        NghiepVu(0, "PC-DEMO-0001", date(2026, 11, 20), Tien(Decimal("1000000"), "VND")),
        **thay,
    )


@pytest.mark.parametrize(
    "ngay,co_mong_doi",
    [
        (date(2026, 11, 20), ()),  # thứ 6
        (date(2026, 11, 21), (NGAY_NGHI,)),  # thứ 7
        (date(2026, 11, 22), (NGAY_NGHI,)),  # chủ nhật
        (date(2026, 11, 23), ()),
    ],
)
def test_ngay_nghi(ngay, co_mong_doi):
    nv = nghiep_vu_demo(ngay=ngay)
    assert co.tinh_co(nv, nv.so_tien, None, None, chinh_sach_demo()) == co_mong_doi


@pytest.mark.parametrize(
    "ngay,bat",
    [
        (date(2028, 2, 26), False),
        (date(2028, 2, 27), True),
        (date(2028, 2, 28), True),
        (date(2028, 2, 29), True),
        (date(2028, 3, 1), False),
        (date(2026, 11, 27), False),
        (date(2026, 11, 28), True),
        (date(2026, 11, 29), True),
        (date(2026, 11, 30), True),
        (date(2026, 12, 1), False),
        (date(2027, 2, 25), False),
        (date(2027, 2, 26), True),
        (date(2027, 2, 28), True),
        (date(2026, 12, 28), False),
        (date(2026, 12, 29), True),
        (date(2026, 12, 31), True),
    ],
)
def test_ba_ngay_cuoi_thang(ngay, bat):
    nv = nghiep_vu_demo(ngay=ngay)
    cac_co = co.tinh_co(nv, nv.so_tien, None, None, chinh_sach_demo())
    assert (CUOI_KY in cac_co) is bat


@pytest.mark.parametrize(
    "so,bat",
    [
        ("10000000", True),
        ("20000000.000000", True),
        ("15000000", False),
        ("9999999.999999", False),
        ("10000000.000001", False),
        ("0", False),
        ("-10000000", False),
    ],
)
def test_so_tron(so, bat):
    nv = nghiep_vu_demo()
    cac_co = co.tinh_co(nv, Tien(Decimal(so), "VND"), None, None, chinh_sach_demo())
    assert cac_co == ((SO_TRON,) if bat else ())


def test_so_tron_dung_don_vi_chinh_sach_va_tien_so_sanh():
    cs = SimpleNamespace(don_vi_so_tron=Decimal("3"))
    assert co.tinh_co(nghiep_vu_demo(), Tien(Decimal("6"), "USD"), None, None, cs) == (SO_TRON,)


@pytest.mark.parametrize(
    "so_nv,phan_vi,tien,bat",
    [
        (49, Decimal("100"), Tien(Decimal("101"), "VND"), False),
        (0, Decimal("100"), Tien(Decimal("101"), "VND"), False),
        (50, Decimal("100"), Tien(Decimal("101"), "VND"), True),
        (50, Decimal("100"), Tien(Decimal("100"), "VND"), False),
        (50, Decimal("100"), Tien(Decimal("99.999999"), "VND"), False),
        (50, Decimal("100"), Tien(Decimal("100.000001"), "VND"), True),
        (50, None, Tien(Decimal("101"), "VND"), False),
        (50, Decimal("100"), None, False),
    ],
)
def test_so_tien_bat_thuong(so_nv, phan_vi, tien, bat):
    ho_so = co.HoSoLoai(so_nv, phan_vi, frozenset())
    cac_co = co.tinh_co(nghiep_vu_demo(), tien, ho_so, None, chinh_sach_demo())
    assert cac_co == ((SO_TIEN_BAT_THUONG,) if bat else ())


@pytest.mark.parametrize(
    "bam_dt,bat",
    [(None, False), ("", False), ("bam-DEMO-cu", False), ("bam-DEMO-moi", True)],
)
def test_doi_tac_moi(bam_dt, bat):
    ho_so = co.HoSoLoai(0, None, frozenset({"bam-DEMO-cu"}))
    cac_co = co.tinh_co(nghiep_vu_demo(), None, ho_so, bam_dt, chinh_sach_demo())
    assert cac_co == ((DOI_TAC_MOI,) if bat else ())


def test_khong_ho_so_khong_bat_hai_co_dau():
    cac_co = co.tinh_co(
        nghiep_vu_demo(), Tien(Decimal("1000000000"), "VND"),
        None, "bam-DEMO-moi", chinh_sach_demo(),
    )
    assert cac_co == (SO_TRON,)


@pytest.mark.parametrize("nhap_tay", [False, True])
def test_nhap_tay_khi_khong_co_tien_va_ho_so(nhap_tay):
    nv = nghiep_vu_demo(nhap_tay=nhap_tay)
    assert co.tinh_co(nv, None, None, None, chinh_sach_demo()) == ((NHAP_TAY,) if nhap_tay else ())


def test_day_du_co_theo_thu_tu_va_tich_he_so():
    cs = chinh_sach_demo()
    ho_so = co.HoSoLoai(50, Decimal("9999999"), frozenset({"bam-DEMO-cu"}))
    nv = nghiep_vu_demo(ngay=date(2026, 11, 28), nhap_tay=True)
    cac_co = co.tinh_co(nv, Tien(Decimal("10000000"), "VND"), ho_so, "bam-DEMO-moi", cs)
    assert cac_co == (SO_TIEN_BAT_THUONG, DOI_TAC_MOI, SO_TRON, NGAY_NGHI, CUOI_KY, NHAP_TAY)
    assert co.tich_he_so(cac_co, cs) == Decimal("20.25")


def test_tich_he_so_rong_va_chinh_sach_tuy_chinh():
    cs = SimpleNamespace(he_so={SO_TRON: Decimal("1.25"), NHAP_TAY: Decimal("3")})
    assert co.tich_he_so((), cs) == Decimal(1)
    assert isinstance(co.tich_he_so((), cs), Decimal)
    assert co.tich_he_so((SO_TRON,), cs) == Decimal("1.25")
    assert co.tich_he_so((SO_TRON, NHAP_TAY), cs) == Decimal("3.75")


def test_ho_so_la_anh_chup_bat_bien():
    ho_so = co.HoSoLoai(50, Decimal("100"), frozenset())
    with pytest.raises(FrozenInstanceError):
        ho_so.so_nghiep_vu = 51
