"""Kiểm PL-1B bằng dữ liệu DEMO, dựng kiểu trực tiếp, không dùng PL-1A."""
import json
import sys
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))

from e_phan_luong import nguong
from e_phan_luong.kieu import (
    CHUA_QUY_DOI, CHUA_RO_TIEN_TE, CO_DO_CUNG, VUOT_PM, VUOT_TE,
    VUNG_BAT_BUOC, VUNG_CHON_MAU, VUNG_DUOI_SAD, NghiepVu, Nguong, Tien,
)
from e_phan_luong.loi import loi


def tien(so, tien_te="VND"):
    return Tien(Decimal(so), tien_te)


def khoi(pm="5000000000", te="3000000000", sad="250000000", tien_te="VND"):
    return {ten: {"so": so, "tien_te": tien_te}
            for ten, so in (("pm", pm), ("te", te), ("sad", sad))}


NG = Nguong(tien("5000000000"), tien("3000000000"), tien("250000000"))


def nv(ma="PC-DEMO-01", so="1100000000", ngay="2026-11-01", **them):
    return NghiepVu(0, ma, date.fromisoformat(ngay), tien(so), **them)


def bam(doi_tac):
    return "bam-DEMO-" + doi_tac


def kiem_loi(ma, ham, *args):
    with pytest.raises(type(loi(ma))) as bat:
        ham(*args)
    assert bat.value.ma == ma
    assert str(bat.value) == str(loi(ma))


def test_tep_thang_tham_so_ke_ca_tham_so_sai():
    assert nguong.doc_nguong(khoi(), "khong-phai-json") == NG
    assert nguong.doc_nguong(khoi(), json.dumps(khoi(pm="6", te="5", sad="1"))) == NG
    kiem_loi("THIEU_NGUONG", nguong.doc_nguong, {}, json.dumps(khoi()))


def test_doc_tham_so_khi_khong_co_khoi_tep():
    assert nguong.doc_nguong(None, json.dumps(khoi())) == NG
    assert nguong.doc_nguong(khoi(pm=5000000000, te=Decimal("3000000000")), None) == NG
    assert nguong.doc_nguong(None, '{"pm":{"so":5.5,"tien_te":"USD"},'
                            '"te":{"so":3.3,"tien_te":"USD"},'
                            '"sad":{"so":1.1,"tien_te":"USD"}}').te == tien("3.3", "USD")


@pytest.mark.parametrize("tham_so", [None, "", " \n\t"])
def test_thieu_ca_hai(tham_so):
    kiem_loi("THIEU_NGUONG", nguong.doc_nguong, None, tham_so)


@pytest.mark.parametrize("chuoi", ["[]", "null", "1", '"DEMO"', "true", "{", "NaN"])
def test_tham_so_khong_phai_json_object(chuoi):
    kiem_loi("THAM_SO_KHONG_HOP_LE", nguong.doc_nguong, None, chuoi)


@pytest.mark.parametrize("pm,te,sad", [(5, 3, 3), (5, 3, 4), (2, 3, 1),
                                      (0, 3, 1), (5, 0, 1), (5, 3, 0),
                                      (-5, 3, 1), (5, -3, 1), (5, 3, -1)])
def test_thu_tu_nguong_sai(pm, te, sad):
    kiem_loi("THIEU_NGUONG", nguong.doc_nguong, khoi(pm, te, sad), None)


def test_te_bang_pm_hop_le():
    ng = nguong.doc_nguong(khoi(pm=3, te=3, sad=1), None)
    assert nguong.xet_lop1(nv(so=3), ng) == (VUNG_BAT_BUOC, (VUOT_PM,))


@pytest.mark.parametrize("ten", ["pm", "te", "sad"])
@pytest.mark.parametrize("gia_tri", [None, {}, {"so": "1"}, {"so": "1", "tien_te": None},
                                     {"so": "1", "tien_te": "USD"},
                                     {"so": True, "tien_te": "VND"},
                                     {"so": 1.1, "tien_te": "VND"},
                                     {"so": "NaN", "tien_te": "VND"},
                                     {"so": "Infinity", "tien_te": "VND"},
                                     {"so": "DEMO", "tien_te": "VND"},
                                     {"so": "1", "tien_te": "vnd"},
                                     {"so": "1e18", "tien_te": "VND"},
                                     {"so": "0.0000001", "tien_te": "VND"}])
def test_khoi_tien_nguong_khong_hop_le(ten, gia_tri):
    du_lieu = khoi()
    du_lieu[ten] = gia_tri
    kiem_loi("THIEU_NGUONG", nguong.doc_nguong, du_lieu, None)


@pytest.mark.parametrize("so,vung,ly_do", [
    ("249999999.999999", VUNG_DUOI_SAD, ()),
    ("250000000", VUNG_CHON_MAU, ()),
    ("2999999999.999999", VUNG_CHON_MAU, ()),
    ("3000000000", VUNG_BAT_BUOC, (VUOT_TE,)),
    ("4999999999.999999", VUNG_BAT_BUOC, (VUOT_TE,)),
    ("5000000000", VUNG_BAT_BUOC, (VUOT_PM,)),
    ("6000000000", VUNG_BAT_BUOC, (VUOT_PM,)),
    ("-3000000000", VUNG_BAT_BUOC, (VUOT_TE,)),
])
def test_bien_lop1(so, vung, ly_do):
    assert nguong.xet_lop1(nv(so=so), NG) == (vung, ly_do)


def test_tien_quy_doi_dung_tien_te_duoc_uu_tien():
    dong = replace(nv(), so_tien=tien("1", "USD"), so_tien_quy_doi=tien("5000000000"))
    assert nguong.tien_so_sanh(dong, NG) == (tien("5000000000"), None)
    assert nguong.xet_lop1(dong, NG) == (VUNG_BAT_BUOC, (VUOT_PM,))
    assert nguong.tien_so_sanh(replace(dong, so_tien=tien("2")), NG)[0] == tien("5000000000")
    assert nguong.tien_so_sanh(replace(dong, so_tien=tien("2", None)), NG)[0] == tien("5000000000")


def test_quy_doi_sai_tien_te_thi_dung_tien_goc_hop_le():
    dong = nv(so_tien_quy_doi=tien("9000000000", "USD"))
    assert nguong.tien_so_sanh(dong, NG) == (dong.so_tien, None)


@pytest.mark.parametrize("tien_te,ly_do", [("USD", CHUA_QUY_DOI), (None, CHUA_RO_TIEN_TE)])
@pytest.mark.parametrize("quy_doi", [None, tien("9000000000", "EUR"), tien("9000000000", None)])
def test_thieu_du_lieu_so_tien(tien_te, ly_do, quy_doi):
    dong = replace(nv(), so_tien=tien("9000000000", tien_te), so_tien_quy_doi=quy_doi)
    assert nguong.tien_so_sanh(dong, NG) == (None, ly_do)
    assert nguong.xet_lop1(dong, NG) == (VUNG_BAT_BUOC, (ly_do,))


@pytest.mark.parametrize("so,tien_te,ly_do", [("1", "VND", (CO_DO_CUNG,)),
    ("3000000000", "VND", (VUOT_TE, CO_DO_CUNG)),
    ("5000000000", "VND", (VUOT_PM, CO_DO_CUNG)),
    ("1", "USD", (CHUA_QUY_DOI, CO_DO_CUNG)),
    ("1", None, (CHUA_RO_TIEN_TE, CO_DO_CUNG))])
def test_co_do_cung_cong_don(so, tien_te, ly_do):
    dong = replace(nv(co_do_cung=True), so_tien=tien(so, tien_te))
    assert nguong.xet_lop1(dong, NG) == (VUNG_BAT_BUOC, ly_do)


def ba_khoan():
    return [nv(ma=f"PC-DEMO-{i}", ngay=ngay, doi_tac="DEMO-NCC-01")
            for i, ngay in enumerate(("2026-11-01", "2026-11-04", "2026-11-07"))]


def test_chia_nho_ba_khoan_trong_bay_ngay_va_khong_phu_thuoc_thu_tu():
    ds = ba_khoan()
    for dong in (ds, ds[::-1], [ds[1], ds[0], ds[2]]):
        assert nguong.tim_chia_nho(dong, NG, bam=bam) == frozenset(n.ma for n in ds)


def test_chia_nho_cach_tam_ngay_khong_gan():
    ds = ba_khoan()
    ds[2] = replace(ds[2], ngay=date(2026, 11, 9))
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset()
    ds[2] = replace(ds[2], ngay=date(2026, 11, 8))
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset()


@pytest.mark.parametrize("doi_tac", [None, "khac_nhau"])
def test_khong_gom_khac_doi_tac_hoac_thieu_doi_tac(doi_tac):
    ds = [replace(n, doi_tac=None if doi_tac is None else f"DEMO-NCC-{i}")
          for i, n in enumerate(ba_khoan())]
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset()


def test_tong_truoc_dung_khoa_bam_va_cua_so():
    ds = [nv(doi_tac="DEMO-NCC-01", ngay="2026-11-07")]
    da_goi = []

    def lich_su(khoa, ngay):
        da_goi.append((khoa, ngay))
        return Decimal("1900000000") if ngay == date(2026, 11, 1) else Decimal(0)

    assert nguong.tim_chia_nho(ds, NG, bam=bam, tong_truoc=lich_su) == {ds[0].ma}
    assert all(khoa == bam("DEMO-NCC-01") for khoa, _ in da_goi)
    assert (bam("DEMO-NCC-01"), date(2026, 10, 31)) not in da_goi
    assert nguong.tim_chia_nho([replace(ds[0], ngay=date(2026, 11, 8))], NG,
                             bam=bam, tong_truoc=lich_su) == frozenset()


def test_cua_so_lich_su_ket_thuc_o_ngay_khong_co_dong_moi():
    dong = nv(doi_tac="DEMO-NCC-01")
    assert nguong.tim_chia_nho([dong], NG, bam=bam, tong_truoc=lambda _, ngay:
        Decimal("1900000000") if ngay == date(2026, 11, 2) else Decimal(0)) == {dong.ma}


def test_khong_cong_lan_tien_te_va_khong_cong_dong_tu_te():
    ds = ba_khoan()
    assert nguong.tim_chia_nho([*ds[:2], replace(ds[2], so_tien=tien("1100000000", "USD"))],
                             NG, bam=bam) == frozenset()
    assert nguong.tim_chia_nho([*ds[:2], replace(ds[2], so_tien=tien("1100000000", None))],
                             NG, bam=bam) == frozenset()
    assert nguong.tim_chia_nho([*ds[:2], replace(ds[2], so_tien=tien("3000000000"))],
                             NG, bam=bam) == frozenset()
    ds[2] = replace(ds[2], so_tien=tien("1", "USD"), so_tien_quy_doi=tien("1100000000"))
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset(n.ma for n in ds)


def test_chi_gan_dong_thuoc_cua_so_dat_nguong_va_gan_tat_ca_cung_ngay():
    ds = [replace(n, ngay=date(2026, 11, 10)) for n in ba_khoan()]
    ds += [nv(ma="PC-DEMO-xa", ngay="2026-11-01", doi_tac="DEMO-NCC-01")]
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset(n.ma for n in ds[:3])


def test_chia_nho_bang_te_tuyet_doi_va_cua_so_tuy_chinh():
    ds = [replace(n, so_tien=tien("-1000000000")) for n in ba_khoan()]
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset(n.ma for n in ds)
    assert nguong.tim_chia_nho(ds, NG, cua_so_ngay=6, bam=bam) == frozenset()
    assert nguong.tim_chia_nho([], NG, bam=bam) == frozenset()


def test_tien_khong_bi_lam_tron_theo_context_ben_goi():
    with localcontext() as ctx:
        ctx.prec = 6
        assert nguong.xet_lop1(nv(so="-2999999999.999999"), NG) == (VUNG_CHON_MAU, ())
        ds = [nv(ma=f"PC-DEMO-{i}", so=so, doi_tac="DEMO-NCC-01") for i, so in enumerate(
            ("1000000000", "1000000000", "999999999.999999"))]
        assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset()


@pytest.mark.parametrize("cua_so", [0, -1, True, 1.5])
def test_cua_so_khong_hop_le(cua_so):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        nguong.tim_chia_nho([], NG, cua_so_ngay=cua_so, bam=bam)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"


def test_cua_so_truot_khop_cach_tinh_vet_can():
    # DEMO xác định, gồm cửa sổ chồng lấp và tiền tệ không so sánh được.
    ds = [nv(ma=f"PC-DEMO-{i}", so=str((i % 4 + 1) * 310000000),
             ngay=(date(2026, 11, 1) + timedelta(days=(i * 5) % 25)).isoformat(),
             doi_tac=f"DEMO-NCC-{i % 2}") for i in range(40)]
    ds[5] = replace(ds[5], so_tien=tien("9999999999", "USD"))
    mong_doi = set()
    for dong in ds:
        cua_so = [n for n in ds if n.doi_tac == dong.doi_tac
                  and 0 <= (dong.ngay - n.ngay).days < 7 and n.so_tien.tien_te == "VND"]
        if sum((n.so_tien.so for n in cua_so), Decimal(0)) >= NG.te.so:
            mong_doi.update(n.ma for n in cua_so)
    assert nguong.tim_chia_nho(ds, NG, bam=bam) == frozenset(mong_doi)
