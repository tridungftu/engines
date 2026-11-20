"""Kiểm PL-4A bằng dữ liệu DEMO trong RAM, không dùng Core thật."""
import hashlib
import json
import logging
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import date, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import ho_so, nguong
from e_phan_luong.co import HoSoLoai
from e_phan_luong.kieu import NghiepVu, Nguong, Tien


NGAY = date(2026, 11, 20)
BAM = hashlib.sha256(b"DEMO-NCC-001").hexdigest()[:32]


def dong(so="1", bam=BAM, ngay=NGAY):
    return (Tien(Decimal(so), "VND") if so is not None else None, bam, ngay)


def moi():
    return ho_so.moi("kt_kiem", "thanh_toan_ncc")


def test_moi_frozen_va_khong_chia_se_du_lieu():
    hs = moi()
    assert hs.so_nghiep_vu == 0
    assert hs.ky_lam_moi is None
    assert not hs.bieu_do and not hs.doi_tac and not hs.tong_ngay
    with pytest.raises(FrozenInstanceError):
        hs.khau = "khac"
    a, _ = ho_so.cong(hs, [dong()], ky="2026-11")
    b, _ = ho_so.cong(a, [dong("2")], ky="2026-11")
    assert hs == moi()
    assert a.so_nghiep_vu == 1
    assert a.tong_ngay[BAM][NGAY.isoformat()] == 1
    assert b.tong_ngay[BAM][NGAY.isoformat()] == 3


@pytest.mark.parametrize("so,bucket", [
    ("0", 0), ("0.000001", 0), ("0.999999", 0), ("1", 0),
    ("1.258925", 0), ("1.258926", 1), ("2.5", 3),
    ("9.99", 9), ("9.9999999999999999999999999999999999999999", 9),
    ("10", 10), ("1000000000", 90), ("1000000000.000001", 90),
    ("999999999999999999.999999", 179), ("-10.25", 10),
])
def test_bien_bucket_khong_phu_thuoc_precision(so, bucket):
    with localcontext() as ctx:
        ctx.prec = 6
        hs, bo = ho_so.cong(moi(), [dong(so)], ky="2026-11")
    assert hs.bieu_do == {"2026-11": {bucket: 1}}
    assert bo == 0


def test_cong_thang_doi_tac_va_tien_none():
    hs, _ = ho_so.cong(moi(), [dong(), dong(None, "bam-demo-khong-tien"),
                              dong("3", None)], ky="2026-11")
    hs, _ = ho_so.cong(hs, [dong("2")], ky="2026-10")
    assert hs.bieu_do == {"2026-11": {0: 1, 4: 1}, "2026-10": {3: 1}}
    assert hs.so_nghiep_vu == 3
    assert hs.doi_tac == {BAM: "2026-11", "bam-demo-khong-tien": "2026-11"}
    assert hs.tong_ngay == {BAM: {"2026-11-20": Decimal(3)}}


def test_q8_cong_lai_khong_khu_trung():
    hs, _ = ho_so.cong(moi(), [dong("1.25")], ky="2026-11")
    hs, _ = ho_so.cong(hs, [dong("1.25")], ky="2026-11")
    assert hs.so_nghiep_vu == 2
    assert hs.tong_ngay[BAM]["2026-11-20"] == Decimal("2.50")


@pytest.mark.parametrize("so_dong,mong_doi", [(49, None), (50, Decimal(10))])
def test_phan_vi_49_50(so_dong, mong_doi):
    hs, _ = ho_so.cong(moi(), [dong("9.99")] * so_dong, ky="2026-11")
    anh = ho_so.anh_chup(hs, tien_te_nguong="VND")
    assert isinstance(anh, HoSoLoai)
    assert anh.phan_vi_95 == mong_doi
    assert anh.so_nghiep_vu == so_dong
    assert anh.bam_doi_tac == frozenset({BAM})


@pytest.mark.parametrize("so_nho,mong_doi", [(95, Decimal(2)), (94, Decimal(13))])
def test_phan_vi_thu_hang_va_can_tren_lam_tron_len(so_nho, mong_doi):
    hs, _ = ho_so.cong(moi(), [dong("1")] * so_nho, ky="2026-10")
    hs, _ = ho_so.cong(hs, [dong("10")] * (100 - so_nho), ky="2026-11")
    with localcontext() as ctx:
        ctx.prec = 3
        assert ho_so.anh_chup(hs, tien_te_nguong="VND").phan_vi_95 == mong_doi


def test_phan_vi_so_lon_khong_float():
    hs, _ = ho_so.cong(moi(), [dong("1000000000")] * 50, ky="2026-11")
    assert ho_so.anh_chup(hs, tien_te_nguong="VND").phan_vi_95 == Decimal("1258925412")


def test_khu_hoi_dung_cot_json_chuan_va_tien_chuoi():
    hs, _ = ho_so.cong(moi(), [dong("123.4500"), dong("1E+9", "bam-demo-á")], ky="2026-11")
    hs = replace(hs, ky_lam_moi="2026-11")
    ban_ghi = ho_so.ve_ban_ghi(hs)
    assert set(ban_ghi) == {"khau", "loai", "so_nghiep_vu", "bieu_do",
                            "bam_doi_tac", "tong_7_ngay", "ky_lam_moi"}
    for cot in ("bieu_do", "bam_doi_tac", "tong_7_ngay"):
        assert isinstance(ban_ghi[cot], str)
        assert ban_ghi[cot] == json.dumps(json.loads(ban_ghi[cot]), ensure_ascii=False,
                                         sort_keys=True, separators=(",", ":"))
    assert "á" in ban_ghi["bam_doi_tac"]
    tien = json.loads(ban_ghi["tong_7_ngay"])
    assert tien[BAM]["2026-11-20"] == "123.4500"
    assert tien["bam-demo-á"]["2026-11-20"] == "1000000000"
    assert ho_so.tu_ban_ghi(ban_ghi) == hs
    # Số đếm là thuộc tính tính từ biểu đồ, không tin cột dư thừa.
    assert ho_so.tu_ban_ghi({**ban_ghi, "so_nghiep_vu": 999}).so_nghiep_vu == 2


@pytest.mark.parametrize("cot", ["bieu_do", "bam_doi_tac", "tong_7_ngay"])
@pytest.mark.parametrize("hong", ["{DEMO-CHUOI-HONG", "[]", "null", "42"])
def test_chuoi_hong_lam_moi_toan_bo_va_log_an_toan(cot, hong, caplog):
    hs, _ = ho_so.cong(moi(), [dong()], ky="2026-11")
    ban_ghi = ho_so.ve_ban_ghi(hs)
    ban_ghi[cot] = hong
    with caplog.at_level(logging.WARNING, logger=ho_so.__name__):
        assert ho_so.tu_ban_ghi(ban_ghi) == moi()
    assert "Hồ sơ hành vi hỏng" in caplog.text
    assert hong not in caplog.text


@pytest.mark.parametrize("cot,hong", [
    ("bieu_do", '{"2026-13":{"0":1}}'),
    ("bieu_do", '{"2026-11":{"0":true}}'),
    ("bieu_do", '{"2026-11":{"0":-1}}'),
    ("bam_doi_tac", '{"bam-demo":"khong-phai-ky"}'),
    ("tong_7_ngay", json.dumps({BAM: {"2026-11-20": "NaN"}})),
    ("tong_7_ngay", json.dumps({BAM: {"2026-11-20": 1.2}})),
    ("tong_7_ngay", json.dumps({BAM: {"2026-11-31": "1"}})),
])
def test_json_dung_cu_phap_nhung_sai_cau_truc(cot, hong):
    hs, _ = ho_so.cong(moi(), [dong()], ky="2026-11")
    assert ho_so.tu_ban_ghi({**ho_so.ve_ban_ghi(hs), cot: hong}) == moi()


def test_cua_so_7_ngay_toan_ho_so_khong_phu_thuoc_thu_tu():
    ds = [dong("1.1", ngay=NGAY - timedelta(days=i)) for i in range(9)]
    ds += [dong("2", "bam-demo-cu", NGAY - timedelta(days=7))]
    a, _ = ho_so.cong(moi(), ds, ky="2026-11")
    b, _ = ho_so.cong(moi(), reversed(ds), ky="2026-11")
    assert a == b
    assert set(a.tong_ngay[BAM]) == {(NGAY - timedelta(days=i)).isoformat() for i in range(7)}
    assert "bam-demo-cu" not in a.tong_ngay
    assert "bam-demo-cu" in a.doi_tac
    assert a.so_nghiep_vu == 10
    # Lô kế tiếp đẩy cửa sổ của cả đối tác không xuất hiện trong lô mới.
    c, _ = ho_so.cong(a, [dong("3", "bam-demo-moi", NGAY + timedelta(days=7))], ky="2026-11")
    assert c.tong_ngay == {"bam-demo-moi": {"2026-11-27": Decimal(3)}}


def test_cua_so_tuy_chon_va_ngay_nho_nhat():
    hs, _ = ho_so.cong(moi(), [dong(ngay=date.min), dong(ngay=date(1, 1, 2))],
                        ky="0001-01", cua_so_ngay=1)
    assert hs.tong_ngay[BAM] == {"0001-01-02": Decimal(1)}


def test_cong_tien_chinh_xac_context_thap():
    with localcontext() as ctx:
        ctx.prec = 4
        hs, _ = ho_so.cong(moi(), [dong("999999999999999999.999999"),
                                  dong("0.000001")], ky="2026-11")
    assert hs.tong_ngay[BAM]["2026-11-20"] == Decimal("1000000000000000000.000000")


def test_tran_20000_bo_ky_cu_roi_bam_tang_dan():
    cac_bam = [f"{i:032x}" for i in range(20_005)]
    hs = replace(moi(), doi_tac={b: "2026-11" for b in cac_bam},
                 tong_ngay={b: {"2026-11-20": Decimal(1)} for b in cac_bam},
                 bieu_do={"2026-11": {0: 20_005}})
    hs.doi_tac[cac_bam[-1]] = "2026-09"
    hs.doi_tac[cac_bam[-2]] = "2026-10"
    a, bo = ho_so.cong(hs, [], ky="2026-11")
    assert bo == 5
    assert len(a.doi_tac) == 20_000
    assert set(hs.doi_tac) - set(a.doi_tac) == set(cac_bam[:3] + cac_bam[-2:])
    assert set(a.tong_ngay) == set(a.doi_tac)
    assert a.so_nghiep_vu == 20_005
    assert len(hs.doi_tac) == 20_005
    b, bo = ho_so.cong(a, [dong(None, cac_bam[0])], ky="2026-12")
    assert bo == 1 and cac_bam[0] in b.doi_tac and cac_bam[3] not in b.doi_tac
    c, bo = ho_so.cong(b, [], ky="2026-12")
    assert bo == 0 and c == b


def test_tong_truoc_khong_co_tra_0_va_anh_chup_khong_bi_cong_lan():
    hs, _ = ho_so.cong(moi(), [dong("60")], ky="2026-11")
    lay = ho_so.tong_truoc(hs)
    assert lay(BAM, NGAY) == Decimal(60)
    assert lay("bam-demo-khac", NGAY) == Decimal(0)
    assert lay(BAM, NGAY - timedelta(days=1)) == Decimal(0)
    sau, _ = ho_so.cong(hs, [dong("50")], ky="2026-11")
    assert lay(BAM, NGAY) == 60
    assert ho_so.tong_truoc(sau)(BAM, NGAY) == 110


def test_callback_noi_nguong_tim_chia_nho():
    hs, _ = ho_so.cong(moi(), [dong("60", ngay=NGAY - timedelta(days=6))], ky="2026-11")
    ng = Nguong(Tien(Decimal(200), "VND"), Tien(Decimal(100), "VND"), Tien(Decimal(10), "VND"))
    nv = NghiepVu(0, "PC-DEMO-001", NGAY, Tien(Decimal(40), "VND"), doi_tac="DEMO-NCC-001")
    assert nguong.tim_chia_nho([nv], ng, tong_truoc=ho_so.tong_truoc(hs),
                               bam=lambda _: BAM) == frozenset({nv.ma})


def test_lam_moi_dung_12_thang_truoc_ky_moi():
    cac_ky = ["2025-10", "2025-11", "2025-12"] + [f"2026-{i:02d}" for i in range(1, 13)]
    hs = replace(moi(), bieu_do={ky: {0: 1} for ky in cac_ky},
                 doi_tac={f"bam-demo-{ky}": ky for ky in cac_ky},
                 tong_ngay={f"bam-demo-{ky}": {"2026-10-31": Decimal(1)} for ky in cac_ky})
    a = ho_so.lam_moi(hs, "2026-11")
    assert set(a.bieu_do) == set(cac_ky[1:13])
    assert a.so_nghiep_vu == 12
    assert set(a.doi_tac.values()) == set(a.bieu_do)
    assert set(a.tong_ngay) == set(a.doi_tac)
    assert a.ky_lam_moi == "2026-11"
    assert ho_so.lam_moi(a, "2026-11") == a
    assert hs.so_nghiep_vu == 15 and hs.ky_lam_moi is None
    a.bieu_do["2025-11"][0] = 99
    assert hs.bieu_do["2025-11"][0] == 1


def test_c4_ban_ghi_khong_co_doi_tac_tho_ma_giao_dich_dien_giai():
    dau_vet = ["DEMO-NCC-DAU-VET-THO", "PC-DEMO-MA-GIAO-DICH", "DEMO-DIEN-GIAI-NHAN-BIET"]
    nv = NghiepVu(0, dau_vet[1], NGAY, Tien(Decimal("1000000"), "VND"),
                  doi_tac=dau_vet[0], noi_dung={"dien_giai": dau_vet[2]})
    bam = hashlib.sha256(("e_phan_luong|doi_tac|demo_thanh_toan|" + nv.doi_tac).encode()).hexdigest()[:32]
    hs, _ = ho_so.cong(moi(), [(nv.so_tien, bam, nv.ngay)], ky="2026-11")
    # Cả trường lạ của bản ghi nguồn cũng không được phát ra lại.
    hs = ho_so.tu_ban_ghi({**ho_so.ve_ban_ghi(hs), "doi_tac": nv.doi_tac,
                          "ma": nv.ma, "dien_giai": dau_vet[2]})
    chuoi = json.dumps(ho_so.ve_ban_ghi(hs), ensure_ascii=False)
    for chu in dau_vet:
        assert chu not in chuoi
    assert bam in chuoi
