"""Cận trên một phía Clopper-Pearson, chỉ dùng thư viện chuẩn.

Tổng nhị thức được cộng từ đầu đuôi gần nhất, với số hạng đầu tính
trong miền log để tránh tràn số. Chia đôi 64 vòng rồi làm tròn lên
6 chữ số lẻ; trường hợp không lỗi dùng công thức đóng bằng Decimal.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, localcontext
from math import comb, exp, expm1, lgamma, log, log1p

from .loi import loi


def _log_to_hop(n: int, k: int) -> float:
    k = min(k, n - k)
    if k <= 32:
        return sum(log(n - j) - log(j + 1) for j in range(k))
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def _xac_suat_tich_luy(k: int, n: int, p: float, log_to_hop: float) -> float:
    """P(X <= k); cộng đuôi có các số hạng giảm dần tương đối."""
    q = 1.0 - p
    tong = so_hang = 1.0
    if p > k / n:
        j = k
        while j > 0:
            so_hang *= j * q / ((n - j + 1) * p)
            tong += so_hang
            if so_hang <= tong * 2e-16:
                break
            j -= 1
        log_dau = log_to_hop + k * log(p) + (n - k) * log1p(-p)
        return min(1.0, exp(log_dau + log(tong)))

    # P(X <= k) = 1 - P(X >= k + 1); không cộng từ một số hạng cực nhỏ.
    j = k + 1
    while j < n:
        so_hang *= (n - j) * p / ((j + 1) * q)
        tong += so_hang
        if so_hang <= tong * 2e-16:
            break
        j += 1
    log_dau = (log_to_hop + log(n - k) - log(k + 1)
               + (k + 1) * log(p) + (n - k - 1) * log1p(-p))
    return max(0.0, -expm1(min(0.0, log_dau + log(tong))))


def can_tren(
    so_loi: int,
    so_mau: int,
    do_tin_cay: Decimal = Decimal("0.95"),
) -> Decimal:
    """Trả cận trên p sao cho P(X <= so_loi | so_mau, p) = 1 - độ tin cậy."""
    if (type(so_loi) is not int or type(so_mau) is not int
            or not 0 <= so_loi <= so_mau):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if (not isinstance(do_tin_cay, Decimal) or not do_tin_cay.is_finite()
            or not Decimal(0) < do_tin_cay < Decimal(1)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if so_mau == 0 or so_loi == so_mau:
        return Decimal(1)

    with localcontext() as ngu_canh:
        ngu_canh.prec = 50
        alpha = Decimal(1) - do_tin_cay
        if so_loi == 0:
            p = Decimal(1) - (alpha.ln() / Decimal(so_mau)).exp()
        else:
            log_to_hop = _log_to_hop(so_mau, so_loi)
            trai, phai = 0.0, 1.0
            for _ in range(64):
                giua = (trai + phai) / 2.0
                if giua == 0.0 or giua == 1.0:
                    continue
                if _xac_suat_tich_luy(so_loi, so_mau, giua, log_to_hop) <= float(alpha):
                    phai = giua
                else:
                    trai = giua
            p = Decimal(str(phai))
            # Ở cỡ mẫu nhỏ, xác minh chính xác nếu cận sát một mốc 6 chữ số:
            # tránh sai số float đẩy cận đúng bằng 0,5 thành 0,500001.
            moc = p.quantize(Decimal("0.000001"))
            if (so_mau <= 128 and Decimal(0) < moc < Decimal(1)
                    and abs(p - moc) < Decimal("1e-10")):
                with localcontext() as chinh_xac:
                    # Mốc có mẫu số 10^6: 6*n + 10 chữ số đủ biểu diễn
                    # chính xác mọi số hạng và tổng nhị thức hữu hạn này.
                    chinh_xac.prec = 6 * so_mau + 10
                    tong = sum(Decimal(comb(so_mau, j)) * moc**j
                               * (Decimal(1) - moc)**(so_mau - j)
                               for j in range(so_loi + 1))
                    p = moc if Decimal(1) - tong >= do_tin_cay else moc + Decimal("0.000001")
        return p.quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
