"""Kiểm ghép PL-1 bằng DEMO; chưa nối năng lực và chưa dùng CoreGia."""
import copy
import json
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))

from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.kieu import (
    CHUA_PHAN_LOAI, CHUA_QUY_DOI, CHUA_RO_TIEN_TE, CO_DO_CUNG,
    NGHI_CHIA_NHO, NGUON_CHUA, VUOT_PM, VUOT_TE,
    VUNG_BAT_BUOC, VUNG_CHON_MAU, VUNG_DUOI_SAD, Tien,
)
from e_phan_luong.loi import loi
from e_phan_luong.nguong import doc_nguong
from e_phan_luong.phan_loai import BoPhanLoai, doc_bo_phan_loai, doc_danh_muc_loai
from e_phan_luong.phan_luong import QuyetDinhLop1, bam_doi_tac, xet_lop1_lo

DEMO = Path(__file__).resolve().parent / "demo"


@pytest.fixture(scope="module")
def du_lieu():
    lo = doc_lo_json((DEMO / "lo-500-DEMO.json").read_bytes())
    danh_muc = doc_danh_muc_loai((DEMO / "danh-muc-loai-DEMO.json").read_text(encoding="utf-8"))
    bo = doc_bo_phan_loai((DEMO / "bo-phan-loai-DEMO.json").read_text(encoding="utf-8"), danh_muc)
    return lo, {
        "nguong": doc_nguong(lo.nguong, None), "danh_muc": danh_muc,
        "bo": bo, "truong_phan_loai": "dien_giai",
    }


@pytest.mark.parametrize("khau", ["kt_kiem", "ktt_duyet", "cfo_duyet"])
def test_500_dong_khop_dap_an_tung_ma(du_lieu, khau):
    lo, cau_hinh = du_lieu
    truoc = copy.deepcopy((lo, cau_hinh))
    dap_an = json.loads((DEMO / "dap-an-lop1.json").read_text(encoding="utf-8"))["theo_ma"]
    ket_qua = xet_lop1_lo(lo, {"khau": khau}, **cau_hinh)

    assert isinstance(ket_qua, tuple)
    assert len(ket_qua) == len(dap_an) == 500
    assert tuple(qd.nv.ma for qd in ket_qua) == tuple(nv.ma for nv in lo.nghiep_vu)
    assert {qd.nv.ma for qd in ket_qua} == set(dap_an)
    for qd in ket_qua:
        assert isinstance(qd, QuyetDinhLop1)
        assert {"ly_do": list(qd.bat_buoc), "loai": qd.loai,
                "nguon_loai": qd.nguon_loai} == dap_an[qd.nv.ma], qd.nv.ma
        assert (qd.vung == VUNG_BAT_BUOC) == bool(qd.bat_buoc), qd.nv.ma
    assert (lo, cau_hinh) == truoc


def test_bam_co_dinh_utf8_va_phan_biet_module():
    # Giá trị đối chiếu tính độc lập theo công thức đã khóa ở GIAO-CODEX §2.4.
    assert bam_doi_tac("demo_thanh_toan", "DEMO-NCC-Ánh Dương") == "cd68fb65aada43b9a2c9eaf5a2193aa2"
    assert bam_doi_tac("demo_khac", "DEMO-NCC-Ánh Dương") != bam_doi_tac(
        "demo_thanh_toan", "DEMO-NCC-Ánh Dương")
    assert bam_doi_tac("demo_thanh_toan", "DEMO-NCC-01") != bam_doi_tac(
        "demo_thanh_toan", "DEMO-NCC-01 ")


def test_chi_ngoai_te_khong_quy_doi_thi_moi_dong_bat_buoc(du_lieu):
    lo, cau_hinh = du_lieu
    dong = tuple(replace(nv, so_tien=Tien(Decimal(so), "USD"),
                         so_tien_quy_doi=quy_doi, doi_tac="DEMO-NCC-USD",
                         co_do_cung=False)
                 for nv, so, quy_doi in zip(lo.nghiep_vu, ("1", "999999999999", "-5000000000"),
                                            (None, None, Tien(Decimal("9000000000"), "EUR"))))
    ket_qua = xet_lop1_lo(replace(lo, nghiep_vu=dong), {}, **cau_hinh)
    assert len(ket_qua) == 3
    assert all(qd.vung == VUNG_BAT_BUOC and qd.bat_buoc == (CHUA_QUY_DOI,)
               and qd.tien_ss is None for qd in ket_qua)


@pytest.mark.parametrize("cua_so,bi_gan", [(1, False), (2, True), (7, True),
                                         (Decimal("2"), True), (2.0, True)])
def test_cua_so_tu_tham_so_va_gop_co_do_cung(du_lieu, cua_so, bi_gan):
    lo, cau_hinh = du_lieu
    dong = tuple(replace(nv, ngay=date(2026, 11, ngay),
                         so_tien=Tien(Decimal("1600000000"), "VND"),
                         doi_tac="DEMO-NCC-CHIA-NHO", co_do_cung=True)
                 for nv, ngay in zip(lo.nghiep_vu, (1, 2)))
    ket_qua = xet_lop1_lo(replace(lo, nghiep_vu=dong),
                         {"cua_so_chia_nho_ngay": cua_so}, **cau_hinh)
    ly_do = (NGHI_CHIA_NHO, CO_DO_CUNG) if bi_gan else (CO_DO_CUNG,)
    assert all(qd.bat_buoc == ly_do and qd.vung == VUNG_BAT_BUOC for qd in ket_qua)


def test_chia_nho_nhan_lich_su_bang_bam_dung_module(du_lieu):
    lo, cau_hinh = du_lieu
    nv = replace(lo.nghiep_vu[0], ngay=date(2026, 11, 10), doi_tac="DEMO-NCC-LICH-SU",
                 so_tien=Tien(Decimal("1100000000"), "VND"))
    cac_lan_goi = []
    bam = bam_doi_tac(lo.ma_module, nv.doi_tac)

    def tong_truoc(khoa, ngay):
        cac_lan_goi.append((khoa, ngay))
        return Decimal("1900000000") if ngay == date(2026, 11, 9) else Decimal(0)

    lo_nho = replace(lo, nghiep_vu=(nv,))
    assert xet_lop1_lo(lo_nho, {}, **cau_hinh)[0].bat_buoc == ()
    qd, = xet_lop1_lo(lo_nho, {}, tong_truoc=tong_truoc, **cau_hinh)
    assert qd.bat_buoc == (NGHI_CHIA_NHO,)
    assert qd.vung == VUNG_BAT_BUOC
    assert cac_lan_goi and all(khoa == bam for khoa, _ in cac_lan_goi)


@pytest.mark.parametrize("so,vung,ly_do", [
    ("-5000000000", VUNG_BAT_BUOC, (VUOT_PM,)),
    ("-3000000000", VUNG_BAT_BUOC, (VUOT_TE,)),
    ("-250000000", VUNG_CHON_MAU, ()),
    ("-249999999.999999", VUNG_DUOI_SAD, ()),
])
def test_so_am_so_theo_gia_tri_tuyet_doi(du_lieu, so, vung, ly_do):
    lo, cau_hinh = du_lieu
    nv = replace(lo.nghiep_vu[0], so_tien=Tien(Decimal(so), "VND"), doi_tac=None)
    qd, = xet_lop1_lo(replace(lo, nghiep_vu=(nv,)), {}, **cau_hinh)
    assert (qd.vung, qd.bat_buoc, qd.tien_ss) == (vung, ly_do, Tien(Decimal(so).copy_abs(), "VND"))
    with pytest.raises(FrozenInstanceError):
        qd.vung = VUNG_DUOI_SAD


def test_quy_doi_va_thieu_tien_te_khong_doan_loai(du_lieu):
    lo, cau_hinh = du_lieu
    nv = replace(lo.nghiep_vu[0], loai=None, noi_dung={}, doi_tac=None,
                 so_tien=Tien(Decimal("5000000000"), None))
    quy_doi = Tien(Decimal("-3000000000"), "VND")
    dong = (nv, replace(nv, ma="PC-DEMO-QUY-DOI", so_tien_quy_doi=quy_doi))
    ket_qua = xet_lop1_lo(replace(lo, nghiep_vu=dong), {}, **cau_hinh)
    assert ket_qua[0].bat_buoc == (CHUA_RO_TIEN_TE,) and ket_qua[0].tien_ss is None
    assert ket_qua[1].bat_buoc == (VUOT_TE,)
    assert ket_qua[1].tien_ss == Tien(Decimal("3000000000"), "VND")
    assert all((qd.loai, qd.nguon_loai) == (CHUA_PHAN_LOAI, NGUON_CHUA) for qd in ket_qua)


def test_khong_co_bo_thi_khong_doan_loai_tu_noi_dung(du_lieu):
    lo, cau_hinh = du_lieu
    nv = replace(lo.nghiep_vu[0], loai=None)
    assert nv.noi_dung["dien_giai"]
    qd, = xet_lop1_lo(replace(lo, nghiep_vu=(nv,)), {}, **{**cau_hinh, "bo": BoPhanLoai()})
    assert (qd.loai, qd.nguon_loai) == (CHUA_PHAN_LOAI, NGUON_CHUA)


def test_chia_nho_so_am_va_quy_doi_khong_bu_tru_nhau(du_lieu):
    lo, cau_hinh = du_lieu
    dong = tuple(replace(nv, ngay=date(2026, 11, 10),
                         so_tien=Tien(Decimal(so), "VND"), doi_tac="DEMO-NCC-AM")
                 for nv, so in zip(lo.nghiep_vu, ("-1600000000", "1600000000")))
    dong = (dong[0], replace(dong[1], so_tien=Tien(Decimal("1"), "USD"),
                            so_tien_quy_doi=dong[1].so_tien))
    ket_qua = xet_lop1_lo(replace(lo, nghiep_vu=dong), {}, **cau_hinh)
    assert all(qd.bat_buoc == (NGHI_CHIA_NHO,) and qd.vung == VUNG_BAT_BUOC for qd in ket_qua)


def test_dao_thu_tu_lo_khong_doi_quyet_dinh(du_lieu):
    lo, cau_hinh = du_lieu
    truoc = xet_lop1_lo(lo, {}, **cau_hinh)
    sau = xet_lop1_lo(replace(lo, nghiep_vu=tuple(reversed(lo.nghiep_vu))), {}, **cau_hinh)
    assert sau == tuple(reversed(truoc))
    assert xet_lop1_lo(replace(lo, nghiep_vu=()), {}, **cau_hinh) == ()


@pytest.mark.parametrize("cua_so", [True, False, None, "7", 0, -1, Decimal("1.5"),
                                   Decimal("NaN"), Decimal("Infinity"), float("inf")])
def test_cua_so_sai_bao_loi_chuan(du_lieu, cua_so):
    lo, cau_hinh = du_lieu
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        xet_lop1_lo(lo, {"cua_so_chia_nho_ngay": cua_so}, **cau_hinh)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"
    assert str(bat.value) == str(loi("THAM_SO_KHONG_HOP_LE"))


def test_module_gan_loai_ngoai_danh_muc_thi_tu_choi(du_lieu):
    lo, cau_hinh = du_lieu
    nv = replace(lo.nghiep_vu[0], loai="loai_DEMO_khong_co")
    with pytest.raises(type(loi("DU_LIEU_KHONG_HOP_LE"))) as bat:
        xet_lop1_lo(replace(lo, nghiep_vu=(nv,)), {}, **cau_hinh)
    assert bat.value.ma == "DU_LIEU_KHONG_HOP_LE"
