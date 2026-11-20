"""Kiểm đọc lô PL-1A; mọi bytes và dữ liệu DEMO được dựng trong test."""
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import doc_lo, kieu, loi


def _dong_demo():
    return {
        "ma": "PC-DEMO-0001", "ngay": "2026-10-30",
        "so_tien": {"so": "1000000000000.123456", "tien_te": "VND"},
        "loai": "loai_demo_chua_kiem_danh_muc", "doi_tac": "DEMO-NCC-01",
        "dien_giai": "Thanh toán DEMO Công ty DEMO Ánh Dương",
        "tai_khoan_no": "331", "tai_khoan_co": "1121",
        "nhap_tay": True, "co_do_cung": False,
        "thuoc_tinh": {"bo_phan": "Bộ phận DEMO", "so_dot": 2},
    }


def _lo_demo():
    return {
        "phien_ban": 1, "ma_module": "demo_thanh_toan", "ky": "2026-11",
        "nguong": {"pm": {"so": "5000000000000", "tien_te": "VND"}},
        "nghiep_vu": [_dong_demo()],
    }


def _bytes(lo):
    return json.dumps(lo, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _kiem_loi(du_lieu, ma="DU_LIEU_KHONG_HOP_LE"):
    with pytest.raises(loi.LoiNghiepVu) as bat:
        doc_lo.doc_lo_json(du_lieu)
    assert bat.value.ma == ma
    assert bat.value.thong_diep == loi.CAU_LOI[ma]
    assert str(bat.value) == f"{ma}: {loi.CAU_LOI[ma]}"
    assert not bat.value.thu_lai_duoc
    for noi_dung in ("PC-DEMO", "DEMO-NCC", "Ánh Dương", "1000000000000", "demo_thanh_toan"):
        assert noi_dung not in bat.value.thong_diep


@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"])
def test_doc_lo_utf8_bom_va_du_noi_dung(bom):
    lo = doc_lo.doc_lo_json(bom + _bytes(_lo_demo()))
    assert isinstance(lo, kieu.Lo)
    assert (lo.phien_ban, lo.ma_module, lo.ky) == (1, "demo_thanh_toan", "2026-11")
    assert lo.nguong == _lo_demo()["nguong"]
    assert isinstance(lo.nghiep_vu, tuple)
    nv, = lo.nghiep_vu
    assert nv.chi_so == 0
    assert nv.ma == "PC-DEMO-0001"
    assert nv.ngay == date(2026, 10, 30)
    assert nv.so_tien == kieu.Tien(Decimal("1000000000000.123456"), "VND")
    assert nv.so_tien_quy_doi is None
    assert nv.loai == "loai_demo_chua_kiem_danh_muc"
    assert nv.doi_tac == "DEMO-NCC-01"
    assert nv.nhap_tay is True and nv.co_do_cung is False
    assert nv.noi_dung == {
        "dien_giai": "Thanh toán DEMO Công ty DEMO Ánh Dương",
        "tai_khoan_no": "331", "tai_khoan_co": "1121",
        "thuoc_tinh.bo_phan": "Bộ phận DEMO", "thuoc_tinh.so_dot": "2",
    }


def test_so_json_thap_phan_am_khong_qua_float():
    du_lieu = _bytes(_lo_demo()).replace(
        b'"1000000000000.123456"', b'-1000000000000.123456'
    ).replace(b'"so_dot":2', b'"so_dot":2.123456')
    nv, = doc_lo.doc_lo_json(du_lieu).nghiep_vu
    assert nv.so_tien.so == Decimal("-1000000000000.123456")
    assert nv.noi_dung["thuoc_tinh.so_dot"] == "2.123456"


def test_truong_tuy_chon_va_tien_te_chua_ro():
    lo = {"phien_ban": 1, "ma_module": "demo_thanh_toan", "nghiep_vu": [
        {"ma": "PC-DEMO-0001", "ngay": "2028-02-29", "so_tien": {"so": -1000000}},
        {"ma": "PC-DEMO-0002", "ngay": "2026-11-20", "so_tien": {"so": 1, "tien_te": None},
         "so_tien_quy_doi": {"so": "25000.123456", "tien_te": "VND"}},
    ]}
    ket_qua = doc_lo.doc_lo_json(_bytes(lo))
    assert ket_qua.ky is None and ket_qua.nguong is None
    assert [nv.chi_so for nv in ket_qua.nghiep_vu] == [0, 1]
    for nv in ket_qua.nghiep_vu:
        assert nv.so_tien.tien_te is None
        assert nv.loai is None and nv.doi_tac is None
        assert nv.noi_dung == {}
        assert nv.nhap_tay is False and nv.co_do_cung is False
    assert ket_qua.nghiep_vu[1].so_tien_quy_doi == kieu.Tien(Decimal("25000.123456"), "VND")


@pytest.mark.parametrize("khoa", ["phien_ban", "ma_module", "nghiep_vu"])
def test_thieu_tung_truong_lo(khoa):
    lo = _lo_demo()
    del lo[khoa]
    _kiem_loi(_bytes(lo))


@pytest.mark.parametrize("khoa", ["ma", "ngay", "so_tien"])
def test_thieu_tung_truong_dong(khoa):
    lo = _lo_demo()
    del lo["nghiep_vu"][0][khoa]
    _kiem_loi(_bytes(lo))


@pytest.mark.parametrize("ngay", [
    "2026-02-29", "2026-11-31", "2026-13-01", "0000-01-01", "2026-1-01",
    "20261120", "20/11/2026", "2026-11-20T00:00:00", "2026-11-20\n", None, 20261120,
])
def test_ngay_sai(ngay):
    lo = _lo_demo()
    lo["nghiep_vu"][0]["ngay"] = ngay
    _kiem_loi(_bytes(lo))


@pytest.mark.parametrize("khoa, gia_tri", [
    ("phien_ban", 2), ("phien_ban", True), ("phien_ban", "1"), ("phien_ban", 1.0),
    ("ma_module", None), ("ma_module", ""), ("ma_module", "Demo"),
    ("ma_module", "1demo"), ("ma_module", "demo-module"),
    ("ma_module", "demo\n"), ("ma_module", "d" * 32),
    ("ky", "2026-00"), ("ky", "2026-13"), ("ky", "2026-1"), ("ky", "0000-01"),
    ("ky", "2026-11\n"), ("ky", 202611), ("nguong", []),
    ("nghiep_vu", {}), ("nghiep_vu", None), ("nghiep_vu", [None]),
])
def test_cau_truc_lo_sai(khoa, gia_tri):
    lo = _lo_demo()
    lo[khoa] = gia_tri
    _kiem_loi(_bytes(lo))


@pytest.mark.parametrize("khoa, gia_tri", [
    ("ma", None), ("ma", 1), ("ma", ""), ("ma", "PC-DEMO-" + "a" * 113),
    ("ma", "PC-DEMO-\x00"), ("ma", "PC-DEMO-\n"), ("ma", "PC-DEMO-\x7f"),
    ("ma", "PC-DEMO-\x85"),
    ("so_tien", None), ("so_tien", {}), ("so_tien", {"so": "1e3"}),
    ("so_tien", {"so": "1000000", "tien_te": "vnd"}),
    ("so_tien_quy_doi", {"so": "NaN", "tien_te": "VND"}),
    ("nhap_tay", 1), ("nhap_tay", None), ("nhap_tay", "false"),
    ("co_do_cung", 0), ("co_do_cung", None), ("co_do_cung", "true"),
    ("thuoc_tinh", []), ("thuoc_tinh", None), ("thuoc_tinh", {"DEMO": True}),
    ("thuoc_tinh", {"DEMO": None}), ("thuoc_tinh", {"DEMO": []}),
    ("thuoc_tinh", {"DEMO": {}}), ("loai", 1), ("doi_tac", []),
    ("dien_giai", {}), ("tai_khoan_no", 331), ("tai_khoan_co", 1121),
])
def test_cau_truc_dong_sai(khoa, gia_tri):
    lo = _lo_demo()
    lo["nghiep_vu"][0][khoa] = gia_tri
    _kiem_loi(_bytes(lo))


@pytest.mark.parametrize("cu, moi", [
    (b'"phien_ban":1', b'"phien_ban":1,"phien_ban":1'),
    (b'"ma":"PC-DEMO-0001"', b'"ma":"PC-DEMO-0001","ma":"PC-DEMO-0002"'),
    (b'"tien_te":"VND"', b'"tien_te":"VND","tien_te":"USD"'),
    (b'"so_dot":2', b'"so_dot":2,"so_dot":3'),
    (b'"ma":"PC-DEMO-0001"', b'"ma":"PC-DEMO-0001","m\\u0061":"PC-DEMO-0002"'),
])
def test_khoa_trung_moi_cap_ke_ca_unicode_escape(cu, moi):
    _kiem_loi(_bytes(_lo_demo()).replace(cu, moi, 1))


def test_ma_trung_khong_cat_ngam():
    lo = _lo_demo()
    lo["nghiep_vu"].append(_dong_demo())
    _kiem_loi(_bytes(lo))


@pytest.mark.parametrize("hang_so", [
    b"NaN", b"Infinity", b"-Infinity", b"1e999999999999999999999", b"1e-999999999999999999999",
])
def test_json_hang_so_khong_huu_han(hang_so):
    _kiem_loi(_bytes(_lo_demo()).replace(b'"1000000000000.123456"', hang_so))


@pytest.mark.parametrize("du_lieu", [
    b"", b"DEMO khong phai JSON", b"<DEMO/>", b"PK\x03\x04DEMO", b"\xffDEMO",
    b'{"DEMO":', b'{"DEMO":1,}', b'{} {}',
])
def test_khong_phai_json(du_lieu):
    _kiem_loi(du_lieu, "TEP_KHONG_HO_TRO")


@pytest.mark.parametrize("du_lieu", [b"null", b"[]", b"1", b'"DEMO"', b"true"])
def test_json_dung_cu_phap_sai_kieu(du_lieu):
    _kiem_loi(du_lieu)


def test_dung_50000_dong_doc_du_va_vuot_50000_tu_choi():
    lo = _lo_demo()
    lo["nghiep_vu"] = [
        {"ma": f"PC-DEMO-{i:05d}", "ngay": "2026-11-20", "so_tien": {"so": 1000000}}
        for i in range(50000)
    ]
    ket_qua = doc_lo.doc_lo_json(_bytes(lo))
    assert len(ket_qua.nghiep_vu) == 50000
    assert ket_qua.nghiep_vu[-1].chi_so == 49999
    lo["nghiep_vu"].append({})
    _kiem_loi(_bytes(lo), "VUOT_GIOI_HAN")


def test_dung_20_mib_va_vuot_20_mib_tu_choi_truoc_parse():
    assert doc_lo.TOI_DA_BYTE == 20 * 1048576
    assert doc_lo.TOI_DA_DONG == 50000
    du_lieu = _bytes(_lo_demo())
    dung_tran = du_lieu + b" " * (20 * 1048576 - len(du_lieu))
    assert len(doc_lo.doc_lo_json(dung_tran).nghiep_vu) == 1
    _kiem_loi(dung_tran + b" ", "VUOT_GIOI_HAN")
    _kiem_loi(b"DEMO" + b" " * (20 * 1048576), "VUOT_GIOI_HAN")


def test_cac_bien_ma_va_ky_hop_le():
    lo = _lo_demo()
    lo["ma_module"] = "d" * 31
    lo["ky"] = "2028-02"
    lo["nghiep_vu"][0]["ma"] = "D" * 120
    assert doc_lo.doc_lo_json(_bytes(lo)).nghiep_vu[0].ma == "D" * 120


def test_lo_rong_va_truong_null_tuy_chon():
    lo = _lo_demo()
    for khoa in ("loai", "doi_tac", "dien_giai", "tai_khoan_no", "tai_khoan_co"):
        lo["nghiep_vu"][0][khoa] = None
    lo["ky"] = lo["nguong"] = None
    nv, = doc_lo.doc_lo_json(_bytes(lo)).nghiep_vu
    assert nv.noi_dung == {"thuoc_tinh.bo_phan": "Bộ phận DEMO", "thuoc_tinh.so_dot": "2"}
    lo["nghiep_vu"] = []
    assert doc_lo.doc_lo_json(_bytes(lo)).nghiep_vu == ()
