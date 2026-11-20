"""Kiểm tiền PL-1A bằng giá trị DEMO, không đọc tệp nghiệp vụ."""
from decimal import Decimal, localcontext
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import kieu, loi, tien


@pytest.mark.parametrize(
    "gia_tri, mong_doi",
    [
        (1000000000000, Decimal("1000000000000")),
        ("999999999999999999.123456", Decimal("999999999999999999.123456")),
        ("-1000000000000.123456", Decimal("-1000000000000.123456")),
        (Decimal("2500000000000.000001"), Decimal("2500000000000.000001")),
        (Decimal("2.5E+12"), Decimal("2500000000000")),
        (0, Decimal(0)),
        ("0.000001", Decimal("0.000001")),
        ("-0.000001", Decimal("-0.000001")),
    ],
)
def test_doc_tien_chinh_xac(gia_tri, mong_doi):
    # Độ chính xác không được phụ thuộc context Decimal của caller.
    with localcontext() as ngu_canh:
        ngu_canh.prec = 6
        ket_qua = tien.doc_tien({"so": gia_tri, "tien_te": "VND"})
    assert ket_qua == kieu.Tien(mong_doi, "VND")
    assert isinstance(ket_qua.so, Decimal)


@pytest.mark.parametrize("bo_tien_te", [{}, {"tien_te": None}])
def test_thieu_tien_te_khong_tu_gan_vnd(bo_tien_te):
    ket_qua = tien.doc_tien({"so": "1000000", **bo_tien_te})
    assert ket_qua == kieu.Tien(Decimal("1000000"), None)
    assert tien.tien_ra(ket_qua) == {"so": "1000000", "tien_te": None}


@pytest.mark.parametrize("tien_te", ["VND", "USD", "EUR", "DEM"])
def test_tien_te_chap_nhan_ba_chu_hoa(tien_te):
    assert tien.doc_tien({"so": 1000000, "tien_te": tien_te}).tien_te == tien_te


@pytest.mark.parametrize(
    "gia_tri",
    [
        None, {}, [], "DEMO", 1000000,
        {"so": None}, {"so": True}, {"so": False}, {"so": []},
        {"so": 1000.0}, {"so": float("nan")}, {"so": float("inf")},
        *({"so": so} for so in [
            "1e3", "NaN", "Infinity", "-Infinity", "sNaN", "1,000", "1 000",
            "+1000", " 1000", "1000 ", ".5", "1.", "", "١٢٣", "1000\n",
            Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity"),
            "1000000000000000000", -1000000000000000000,
            "0.1234567", Decimal("0.0000001"),
        ]),
        *({"so": "1000000", "tien_te": ma} for ma in [
            "vnd", "Vnd", "VN", "VNDD", "123", "VND\n", " VND", "", 123, True, [],
        ]),
    ],
)
def test_du_lieu_tien_sai_dung_cau_loi(gia_tri):
    with pytest.raises(loi.LoiNghiepVu) as bat:
        tien.doc_tien(gia_tri)
    assert bat.value.ma == "DU_LIEU_KHONG_HOP_LE"
    assert bat.value.thong_diep == loi.CAU_LOI[bat.value.ma]
    assert not bat.value.thu_lai_duoc
    assert "DEMO" not in str(bat.value)


def test_null_chi_duoc_khi_cho_phep():
    assert tien.doc_tien(None, cho_phep_null=True) is None
    assert tien.tien_ra(None) is None
    with pytest.raises(loi.LoiNghiepVu):
        tien.doc_tien({}, cho_phep_null=True)


@pytest.mark.parametrize(
    "so, chuoi",
    [
        ("2.5E+12", "2500000000000"),
        ("999999999999999999.123456", "999999999999999999.123456"),
        ("-1000000.123400", "-1000000.1234"),
        ("1000000.000000", "1000000"),
        ("0.000001", "0.000001"),
        ("0.000000", "0"),
        ("-0.000000", "0"),
    ],
)
def test_tien_ra_khong_mu_khong_mat_do_chinh_xac(so, chuoi):
    with localcontext() as ngu_canh:
        ngu_canh.prec = 6
        ket_qua = tien.tien_ra(kieu.Tien(Decimal(so), "VND"))
    assert ket_qua == {"so": chuoi, "tien_te": "VND"}
    assert tien.doc_tien(ket_qua).so == Decimal(so)
