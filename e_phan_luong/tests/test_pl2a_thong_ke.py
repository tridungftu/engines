"""Đối chiếu thống kê bằng nhị thức Fraction, không dùng thuật toán của mô-đun."""
import sys
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
from math import comb
from pathlib import Path
from time import perf_counter

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import thong_ke
from e_phan_luong.loi import CAU_LOI, loi


def _bang_tra_doc_lap(k: int, n: int, tin_cay=Fraction(19, 20)) -> Decimal:
    """Chia đôi trên lưới 1/10^6, cộng C(n,j)p^j(1-p)^(n-j) hoàn toàn hữu tỷ.

    Tìm điểm lưới nhỏ nhất có CDF <= alpha: kiểm đúng cả chiều làm tròn lên,
    không dựa vào lgamma, float hay kết quả can_tren để sinh đáp án.
    """
    trai, phai = 0, 1_000_000
    while phai - trai > 1:
        giua = (trai + phai) // 2
        p = Fraction(giua, 1_000_000)
        tong = sum((comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k + 1)), Fraction(0))
        if tong <= 1 - tin_cay:
            phai = giua
        else:
            trai = giua
    return Decimal(phai) / Decimal(1_000_000)


@pytest.mark.parametrize("n", [1, 29, 30, 59, 60, 99, 100, 100_000])
def test_khong_loi_dung_cong_thuc_va_lam_tron_len(n):
    with localcontext() as ngu_canh:
        ngu_canh.prec = 60
        dung = Decimal(1) - (Decimal("0.05").ln() / Decimal(n)).exp()
        lam_tron = dung.quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
    ket_qua = thong_ke.can_tren(0, n)
    assert isinstance(ket_qua, Decimal)
    assert ket_qua == lam_tron
    assert Decimal(0) <= ket_qua - dung <= Decimal("0.000001")


@pytest.mark.parametrize("n", [29, 60, 100])
@pytest.mark.parametrize("k", range(1, 6))
def test_mot_den_nam_loi_khop_bang_tra_huu_ty(k, n):
    assert thong_ke.can_tren(k, n) == _bang_tra_doc_lap(k, n)


@pytest.mark.parametrize("tin_cay", [Decimal("0.01"), Decimal("0.5"), Decimal("0.8"), Decimal("0.99")])
def test_do_tin_cay_tuy_chinh_khop_bang_tra(tin_cay):
    assert thong_ke.can_tren(3, 30, tin_cay) == _bang_tra_doc_lap(3, 30, Fraction(tin_cay))


@pytest.mark.parametrize("n,k", [(3, 1), (5, 2), (10, 3)])
@pytest.mark.parametrize("p", [Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(9, 10)])
def test_can_dung_moc_lam_tron_khong_tang_thua_mot_don_vi(n, k, p):
    tin_cay = 1 - sum((comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k + 1)), Fraction(0))
    with localcontext() as ngu_canh:
        ngu_canh.prec = 100
        tin_cay_decimal = Decimal(tin_cay.numerator) / Decimal(tin_cay.denominator)
    assert thong_ke.can_tren(k, n, tin_cay_decimal) == Decimal(p.numerator) / Decimal(p.denominator)


@pytest.mark.parametrize("n", [0, 1, 30, 100_000])
def test_chua_co_mau_hoac_tat_ca_deu_loi(n):
    assert thong_ke.can_tren(n, n) == Decimal(1)


def test_don_dieu_theo_so_loi_va_so_mau():
    theo_loi = [thong_ke.can_tren(k, 100) for k in range(101)]
    assert theo_loi == sorted(theo_loi)
    for k in (0, 1, 5, 20):
        theo_mau = [thong_ke.can_tren(k, n) for n in (20, 29, 30, 59, 60, 99, 100, 500, 100_000)]
        assert theo_mau == sorted(theo_mau, reverse=True)


@pytest.mark.parametrize("k", [0, 1, 5, 50_000, 99_999])
def test_mot_tram_nghin_mau_duoi_mot_phan_muoi_giay(k):
    bat_dau = perf_counter()
    ket_qua = thong_ke.can_tren(k, 100_000)
    giay = perf_counter() - bat_dau
    print(f"can_tren({k}, 100000): {giay:.6f} giây")
    assert isinstance(ket_qua, Decimal)
    assert giay < 0.1


def test_khong_phu_thuoc_cach_lam_tron_cua_ben_goi():
    truoc = (thong_ke.can_tren(0, 30), thong_ke.can_tren(3, 100))
    with localcontext() as ngu_canh:
        ngu_canh.prec = 6
        ngu_canh.rounding = ROUND_FLOOR
        assert (thong_ke.can_tren(0, 30), thong_ke.can_tren(3, 100)) == truoc


@pytest.mark.parametrize("k,n", [(-1, 30), (1, 0), (31, 30), (0, -1), (True, 30), (1, False), (1.0, 30), (1, "30")])
def test_so_dem_khong_hop_le(k, n):
    with pytest.raises(type(loi("DU_LIEU_KHONG_HOP_LE"))) as bat:
        thong_ke.can_tren(k, n)
    assert bat.value.ma == "DU_LIEU_KHONG_HOP_LE"
    assert bat.value.thong_diep == CAU_LOI[bat.value.ma]


@pytest.mark.parametrize("tin_cay", [Decimal(0), Decimal(1), Decimal("NaN"), Decimal("Infinity"), 0.95, True])
def test_do_tin_cay_khong_hop_le(tin_cay):
    with pytest.raises(type(loi("THAM_SO_KHONG_HOP_LE"))) as bat:
        thong_ke.can_tren(0, 30, tin_cay)
    assert bat.value.ma == "THAM_SO_KHONG_HOP_LE"
