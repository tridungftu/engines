"""Cờ hành vi của lớp 3; chỉ dùng ảnh chụp hồ sơ trong bộ nhớ."""
from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from decimal import Decimal

from .kieu import (
    CUOI_KY,
    DOI_TAC_MOI,
    NGAY_NGHI,
    NHAP_TAY,
    SO_TIEN_BAT_THUONG,
    SO_TRON,
    THU_TU_CO,
    NghiepVu,
    Tien,
)


@dataclass(frozen=True)
class HoSoLoai:
    """Ảnh chụp hồ sơ một cặp khâu, loại; PL-4 cung cấp."""

    so_nghiep_vu: int
    phan_vi_95: Decimal | None
    bam_doi_tac: frozenset[str]


def tinh_co(
    nv: NghiepVu,
    tien_ss: Tien | None,
    ho_so: HoSoLoai | None,
    bam_dt: str | None,
    cs,
) -> tuple[str, ...]:
    """Xét tiền đã quy về đơn vị ngưỡng, trả cờ theo THU_TU_CO.

    Không tự quy đổi tiền hoặc suy đoán hồ sơ khi chưa được cung cấp.
    Chính sách chỉ cần thuộc tính don_vi_so_tron, không phụ thuộc PL-2A.
    """
    co = set()
    if ho_so is not None:
        if (
            ho_so.so_nghiep_vu >= 50
            and ho_so.phan_vi_95 is not None
            and tien_ss is not None
            and tien_ss.so > ho_so.phan_vi_95
        ):
            co.add(SO_TIEN_BAT_THUONG)
        if bam_dt and bam_dt not in ho_so.bam_doi_tac:
            co.add(DOI_TAC_MOI)

    if (
        tien_ss is not None
        and tien_ss.so > 0
        and tien_ss.so % cs.don_vi_so_tron == 0
    ):
        co.add(SO_TRON)
    if nv.ngay.weekday() >= 5:
        co.add(NGAY_NGHI)
    if nv.ngay.day > monthrange(nv.ngay.year, nv.ngay.month)[1] - 3:
        co.add(CUOI_KY)
    if nv.nhap_tay:
        co.add(NHAP_TAY)
    return tuple(ma for ma in THU_TU_CO if ma in co)


def tich_he_so(co, cs) -> Decimal:
    """Nhân hệ số các cờ đã bật; không có cờ thì hệ số bằng 1."""
    ket_qua = Decimal(1)
    for ma in co:
        ket_qua *= cs.he_so[ma]
    return ket_qua
