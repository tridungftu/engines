"""Đọc và xuất tiền chính xác theo GIAO-CODEX §2.3, không suy đoán tiền tệ."""
from __future__ import annotations

from decimal import Decimal
import re

from .kieu import Tien
from .loi import loi


def doc_tien(gia_tri, *, cho_phep_null: bool = False) -> Tien | None:
    """Chỉ nhận số thập phân hữu hạn, tối đa 18 chữ số nguyên và 6 chữ số lẻ."""
    if gia_tri is None and cho_phep_null:
        return None
    if not isinstance(gia_tri, dict) or "so" not in gia_tri:
        raise loi("DU_LIEU_KHONG_HOP_LE")

    so = gia_tri["so"]
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
    if so.as_tuple().exponent < -6 or (not so.is_zero() and so.adjusted() >= 18):
        raise loi("DU_LIEU_KHONG_HOP_LE")

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
