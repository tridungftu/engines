"""Kiểm so từ khóa PL-1C bằng dữ liệu DEMO, không cần Core."""
import sys
from pathlib import Path
import unicodedata

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import tu_khoa
from e_phan_luong.loi import CAU_LOI, loi


def test_chuan_dau_viet_nfc_nfd_va_khoang_trang():
    chu = "  ĐỀ NGHỊ\tthanh toán\nđợt 1 DEMO  "
    for dang in ("NFC", "NFD"):
        assert tu_khoa.chuan(unicodedata.normalize(dang, chu)) == "de nghi thanh toan dot 1 demo"
    assert tu_khoa.chuan(None) == ""


@pytest.mark.parametrize("tu,chu,dat", [
    ("THANH TOÁN", "DEMO thanh toán đợt 1", True),
    ("=từ", "DEMO: TỪ!", True),
    ("=từ", "DEMO từng đợt", False),
    ("=từ", "DEMO _từ từ_ từ2 2từ", False),
    ("=từ", "DEMO từng, từ", True),
    ("=đợt 1", "DEMO đợt 12", False),
    ("=đợt 1", "DEMO (đợt 1)", True),
    ("đợt #", "DEMO đợt 123", True),
    ("đợt #", "DEMO đợt ١٢", True),
    ("đợt #", "DEMO đợt ", False),
    ("đợt #", "DEMO đợt một", False),
    ("=đợt #", "DEMO đợt 12a", False),
    ("=đợt #", "DEMO (đợt 12)", True),
    ("=đợt #", "DEMO đợt 12a, đợt 34", True),
    ("##", "DEMO 1", False),
    ("##", "DEMO 12", True),
    ("mã #-#", "DEMO mã 12-345", True),
    ("mã #-#", "DEMO mã 12-", False),
    (".*", "DEMO thanh toán", False),
    (".*", "DEMO .*", True),
    ("[a-z]+", "DEMO abc", False),
    ("[a-z]+", "DEMO [a-z]+", True),
    ("(a|b)", "DEMO a", False),
    ("(a|b)", "DEMO (a|b)", True),
    (r"\d+", "DEMO 123", False),
    (r"\d+", r"DEMO \d+", True),
    (".*#", "DEMO abc123", False),
    (".*#", "DEMO .*123", True),
    ("=a+b", "DEMO (a+b)", True),
])
def test_khop_tu_khoa(tu, chu, dat):
    assert tu_khoa.khop_tu_khoa(tu, chu) is dat


def test_dieu_kien_and_or_va_khong_co():
    dk = {"tat_ca": [["tạm ứng", "=thanh toán"], ["đợt #"]],
          "khong_co": ["hủy", "=chưa"]}
    assert tu_khoa.kiem_dieu_kien(dk) == 5
    assert tu_khoa.khop_dieu_kien(dk, "DEMO thanh toán đợt 12")
    assert tu_khoa.khop_dieu_kien(dk, "DEMO tạm ứng đợt 1")
    assert not tu_khoa.khop_dieu_kien(dk, "DEMO thanh toán")
    assert not tu_khoa.khop_dieu_kien(dk, "DEMO đợt 1")
    assert not tu_khoa.khop_dieu_kien(dk, "DEMO CHƯA thanh toán đợt 1")
    assert not tu_khoa.khop_dieu_kien(dk, "DEMO hủy thanh toán đợt 1")


@pytest.mark.parametrize("tu", [None, 1, [], "", "  ", "=", "= \t", "\u0301"])
def test_tu_khoa_sai(tu):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        tu_khoa.khop_tu_khoa(tu, "DEMO")
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"
    assert bat.value.thong_diep == CAU_LOI[bat.value.ma]


@pytest.mark.parametrize("dk", [
    None, [], {}, {"tat_ca": []}, {"tat_ca": ["demo"]},
    {"tat_ca": [[]]}, {"tat_ca": [[1]]},
    {"tat_ca": [["DEMO"]], "khong_co": "hủy"},
    {"tat_ca": [["DEMO"]], "khong_co": [""]},
    {"tat_ca": [["DEMO"]], "vung": ["dien_giai"]},
])
def test_dieu_kien_sai(dk):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        tu_khoa.kiem_dieu_kien(dk)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"


@pytest.mark.parametrize("chuoi", [
    b"{}", "{", '{"demo":1,"demo":2}', '{"demo":NaN}',
    '{"demo":Infinity}', '{"demo":-Infinity}', '"\ud800"',
])
def test_json_khong_hop_le(chuoi):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        tu_khoa.doc_json(chuoi)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"


def test_json_tran_32kib_theo_byte_utf8():
    chuoi = '"' + "Đ" * 16383 + '"'
    assert len(chuoi.encode("utf-8")) == 32768
    assert tu_khoa.doc_json(chuoi) == "Đ" * 16383
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        tu_khoa.doc_json(chuoi + " ")
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"
