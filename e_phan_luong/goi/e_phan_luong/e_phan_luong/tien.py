"""Đọc và xuất tiền chính xác theo GIAO-CODEX §2.3, không suy đoán tiền tệ."""
from __future__ import annotations

from decimal import Decimal
import re

from .kieu import Tien
from .loi import loi


def doc_so_thap_phan(gia_tri) -> Decimal:
    r"""Đọc str/int/Decimal hữu hạn, tối đa 18 chữ số nguyên và 6 chữ số lẻ.

    Chuỗi phải đúng -?[0-9]+(\.[0-9]+)?, không mũ/khoảng trắng/float.
    Chữ số lẻ được đếm sau khi bỏ số 0 thừa, không làm tròn theo context.
    """
    so = gia_tri
    if isinstance(so, str):
        if re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", so) is None:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        so = Decimal(so)
    elif type(so) is int:
        so = Decimal(so)
    elif not isinstance(so, Decimal):
        # bool cũng không phải số tiền; tuyệt đối không chuyển float sang Decimal.
        raise loi("DU_LIEU_KHONG_HOP_LE")

    if not so.is_finite():
        raise loi("DU_LIEU_KHONG_HOP_LE")
    _, chu_so, so_mu = so.as_tuple()
    so_khong_thua = 0
    for chu in reversed(chu_so):
        if chu != 0:
            break
        so_khong_thua += 1
    so_le = 0 if so.is_zero() else max(0, -so_mu - so_khong_thua)
    if so_le > 6 or (not so.is_zero() and so.adjusted() >= 18):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return so


def doc_tien(gia_tri, *, cho_phep_null: bool = False) -> Tien | None:
    """Đọc số theo doc_so_thap_phan, kèm tiền tệ có thể chưa rõ."""
    if gia_tri is None and cho_phep_null:
        return None
    if not isinstance(gia_tri, dict) or "so" not in gia_tri:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    so = doc_so_thap_phan(gia_tri["so"])

    tien_te = gia_tri.get("tien_te")
    if tien_te is not None and (
        not isinstance(tien_te, str) or re.fullmatch(r"[A-Z]{3}", tien_te) is None
    ):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return Tien(so, tien_te)


def tien_ra(t: Tien | None) -> dict | None:
    """Xuất chuỗi không mũ, bỏ số 0 lẻ thừa, giữ nguyên tiền tệ chưa rõ."""
    if t is None:
        return None
    chuoi = "0" if t.so.is_zero() else format(t.so, "f")
    if "." in chuoi:
        chuoi = chuoi.rstrip("0").rstrip(".")
    return {"so": chuoi, "tien_te": t.tien_te}
