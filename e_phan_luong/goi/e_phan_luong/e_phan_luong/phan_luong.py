"""Ghép phân loại và lớp 1; chưa nối năng lực hay chọn mẫu (PL-2).

Chỉ xử lý trong bộ nhớ. Lịch sử tổng ngày, nếu có, do bên gọi cấp;
không lưu đối tác hoặc chi tiết nghiệp vụ.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from hashlib import sha256

from .kieu import (
    NGHI_CHIA_NHO, THU_TU_LY_DO, VUNG_BAT_BUOC,
    Lo, NghiepVu, Nguong, Tien,
)
from .loi import loi
from .nguong import tien_so_sanh, tim_chia_nho, xet_lop1
from .phan_loai import BoPhanLoai, chot_loai, gan_loai


def bam_doi_tac(ma_module: str, doi_tac: str) -> str:
    """32 hex đầu SHA-256 UTF-8 của e_phan_luong|doi_tac|module|đối tác.

    Công thức cố định theo GIAO-CODEX §2.4, không chuẩn hóa mã đầu vào.
    """
    chuoi = "e_phan_luong|doi_tac|" + ma_module + "|" + doi_tac
    return sha256(chuoi.encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class QuyetDinhLop1:
    """Quyết định trung gian; vùng chưa bắt buộc còn chờ lớp 2 và 3."""
    nv: NghiepVu
    loai: str
    nguon_loai: str
    tien_ss: Tien | None
    bat_buoc: tuple[str, ...]
    vung: str


def xet_lop1_lo(
    lo: Lo, tham_so: Mapping[str, object], *, nguong: Nguong,
    danh_muc: dict[str, dict], bo: BoPhanLoai,
    truong_phan_loai: str | None,
    tong_truoc: Callable[[str, date], Decimal] | None = None,
) -> tuple[QuyetDinhLop1, ...]:
    """Giữ thứ tự lô, gộp mọi lý do bắt buộc theo THU_TU_LY_DO.

    Cửa sổ mặc định 7 ngày; tham số kiểu số phải có giá trị nguyên dương.
    tong_truoc nhận băm theo module và ngày, trả tổng cùng tiền tệ ngưỡng,
    không chứa lại dòng của lô hiện tại (hợp đồng tim_chia_nho).
    """
    cua_so = tham_so.get("cua_so_chia_nho_ngay", 7)
    if isinstance(cua_so, bool) or not isinstance(cua_so, (int, float, Decimal)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    try:
        so_ngay = int(cua_so)
    except (ValueError, OverflowError):
        raise loi("THAM_SO_KHONG_HOP_LE") from None
    if cua_so != so_ngay or so_ngay < 1:
        raise loi("THAM_SO_KHONG_HOP_LE")

    ket_qua = []
    for nv in lo.nghiep_vu:
        loai, nguon_loai = chot_loai(gan_loai(nv, danh_muc, bo, truong_phan_loai))
        vung, bat_buoc = xet_lop1(nv, nguong)
        tien_ss, _ = tien_so_sanh(nv, nguong)
        ket_qua.append(QuyetDinhLop1(nv, loai, nguon_loai, tien_ss, bat_buoc, vung))

    chia_nho = tim_chia_nho(
        lo.nghiep_vu, nguong, cua_so_ngay=so_ngay, tong_truoc=tong_truoc,
        bam=lambda doi_tac: bam_doi_tac(lo.ma_module, doi_tac),
    )
    for i, qd in enumerate(ket_qua):
        if qd.nv.ma in chia_nho:
            cac_ma = {*qd.bat_buoc, NGHI_CHIA_NHO}
            ket_qua[i] = replace(
                qd, bat_buoc=tuple(ma for ma in THU_TU_LY_DO if ma in cac_ma),
                vung=VUNG_BAT_BUOC,
            )
    return tuple(ket_qua)
