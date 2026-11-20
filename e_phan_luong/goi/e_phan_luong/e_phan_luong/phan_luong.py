"""Ghép phân loại và lớp 1; chưa nối năng lực hay chọn mẫu (PL-2).

Chỉ xử lý trong bộ nhớ. Lịch sử tổng ngày, nếu có, do bên gọi cấp;
không lưu đối tác hoặc chi tiết nghiệp vụ.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import re

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
    """Quyết định trung gian; vùng chưa bắt buộc còn chờ lớp 2 và 3.

    tien_ss giữ đúng giá trị nguong.tien_so_sanh trả về, đã lấy trị tuyệt đối
    theo Q3, để truyền tiếp cho lớp sau; nv vẫn giữ số tiền gốc có dấu.
    """
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

    Cửa sổ mặc định 7 ngày; nhận int/Decimal/float/chuỗi số nguyên trong 1..31.
    tong_truoc nhận băm theo module và ngày, trả tổng cùng tiền tệ ngưỡng,
    không chứa lại dòng của lô hiện tại (hợp đồng tim_chia_nho).
    """
    khau = tham_so.get("khau")
    if not isinstance(khau, str) or re.fullmatch(r"[a-z][a-z0-9_]{0,39}", khau) is None:
        raise loi("THAM_SO_KHONG_HOP_LE")
    if not isinstance(lo.ma_module, str) or re.fullmatch(
        r"[a-z][a-z0-9_]{0,30}", lo.ma_module
    ) is None:
        raise loi("DU_LIEU_KHONG_HOP_LE")

    cua_so = tham_so.get("cua_so_chia_nho_ngay", 7)
    if isinstance(cua_so, bool) or not isinstance(cua_so, (int, float, Decimal, str)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    try:
        cua_so = Decimal(str(cua_so))
    except (InvalidOperation, ValueError):
        raise loi("THAM_SO_KHONG_HOP_LE") from None
    if not cua_so.is_finite() or not 1 <= cua_so <= 31 or cua_so != cua_so.to_integral_value():
        raise loi("THAM_SO_KHONG_HOP_LE")
    so_ngay = int(cua_so)

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
