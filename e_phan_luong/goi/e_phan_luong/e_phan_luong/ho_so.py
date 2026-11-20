"""Hồ sơ hành vi thuần trong RAM; chỉ xuất số liệu gộp và băm đối tác.

Bên gọi chỉ truyền tiền đã quy về tiền tệ ngưỡng và băm theo hợp đồng §2.4.
Không giữ mã giao dịch, đối tác thô hay diễn giải; không khử trùng nộp lại (Q8).
"""
from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal, DecimalException, ROUND_CEILING, localcontext

from .co import HoSoLoai
from .kieu import Tien


TOI_DA_DOI_TAC = 20_000
_NHAT_KY = logging.getLogger(__name__)


@dataclass(frozen=True)
class HoSo:
    """Số liệu một (khâu, loại); các phép biến đổi luôn sao chép từ hồ sơ cũ."""

    khau: str
    loai: str
    bieu_do: dict[str, dict[int, int]] = field(default_factory=dict)
    doi_tac: dict[str, str] = field(default_factory=dict)
    tong_ngay: dict[str, dict[str, Decimal]] = field(default_factory=dict)
    ky_lam_moi: str | None = None
    tien_te: str | None = None

    @property
    def so_nghiep_vu(self) -> int:
        return sum(sum(thang.values()) for thang in self.bieu_do.values())


def moi(khau: str, loai: str) -> HoSo:
    return HoSo(khau, loai)


def _so_thang(ky: str) -> int:
    if not isinstance(ky, str) or re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", ky) is None:
        raise ValueError("Kỳ phải có dạng YYYY-MM.")
    nam, thang = map(int, ky.split("-"))
    if nam < 1:
        raise ValueError("Năm không hợp lệ.")
    return nam * 12 + thang - 1


def _doi_tuong(chuoi: str) -> dict:
    gia_tri = json.loads(chuoi)
    if not isinstance(gia_tri, dict):
        raise ValueError("Số liệu gộp phải là đối tượng JSON.")
    return gia_tri


def tu_ban_ghi(ban_ghi: dict) -> HoSo:
    """JSON hỏng/sai cấu trúc: bỏ toàn bộ số liệu, ghi cảnh báo không kèm dữ liệu."""
    hs = moi(ban_ghi["khau"], ban_ghi["loai"])
    try:
        bieu_do = {}
        for ky, thang in _doi_tuong(ban_ghi["bieu_do"]).items():
            _so_thang(ky)
            if not isinstance(thang, dict):
                raise ValueError
            bieu_do[ky] = {}
            for bucket, so_luong in thang.items():
                if (re.fullmatch(r"0|[1-9][0-9]*", bucket) is None
                        or type(so_luong) is not int or so_luong < 0):
                    raise ValueError
                bieu_do[ky][int(bucket)] = so_luong
        doi_tac = _doi_tuong(ban_ghi["bam_doi_tac"])
        for bam, ky in doi_tac.items():
            if not bam:
                raise ValueError
            _so_thang(ky)
        tong_ngay = {}
        for bam, cac_ngay in _doi_tuong(ban_ghi["tong_7_ngay"]).items():
            if bam not in doi_tac or not isinstance(cac_ngay, dict):
                raise ValueError
            tong_ngay[bam] = {}
            for ngay, chuoi in cac_ngay.items():
                if date.fromisoformat(ngay).isoformat() != ngay or not isinstance(chuoi, str):
                    raise ValueError
                so = Decimal(chuoi)
                if not so.is_finite() or so < 0:
                    raise ValueError
                tong_ngay[bam][ngay] = so
        ky_lam_moi = ban_ghi.get("ky_lam_moi")
        if ky_lam_moi is not None:
            _so_thang(ky_lam_moi)
        tien_te = ban_ghi.get("tien_te")
        if tien_te is not None and (not isinstance(tien_te, str)
                                    or re.fullmatch(r"[A-Z]{3}", tien_te) is None):
            raise ValueError
        return HoSo(hs.khau, hs.loai, bieu_do, doi_tac, tong_ngay, ky_lam_moi, tien_te)
    except (ValueError, TypeError, KeyError, DecimalException, RecursionError):
        _NHAT_KY.warning("Hồ sơ hành vi hỏng; đã dùng hồ sơ mới.")
        return hs


def ve_ban_ghi(hs: HoSo) -> dict:
    def chuoi_json(gia_tri) -> str:
        return json.dumps(gia_tri, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    # Khóa bucket chuyển thành chữ trước khi sort_keys để sắp theo chuẩn JSON.
    return {
        "khau": hs.khau,
        "loai": hs.loai,
        "so_nghiep_vu": hs.so_nghiep_vu,
        "bieu_do": chuoi_json({ky: {str(b): n for b, n in thang.items()}
                               for ky, thang in hs.bieu_do.items()}),
        "bam_doi_tac": chuoi_json(hs.doi_tac),
        "tong_7_ngay": chuoi_json({bam: {ngay: format(so, "f") for ngay, so in ngay_so.items()}
                                   for bam, ngay_so in hs.tong_ngay.items()}),
        "ky_lam_moi": hs.ky_lam_moi,
        "tien_te": hs.tien_te,
    }


def _bucket(so: Decimal) -> int:
    so = so.copy_abs()
    if so < 1:
        return 0
    # floor(10*log10(x)) = floor(log10(x**10)). Lũy thừa chính xác tránh
    # log10 làm tròn qua biên, kể cả khi context của bên gọi có precision thấp.
    with localcontext() as ctx:
        ctx.prec = max(40, 10 * len(so.as_tuple().digits))
        return (so ** 10).adjusted()


def _cong_tien(a: Decimal, b: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = max(40, max(a.adjusted(), b.adjusted())
                       - min(a.as_tuple().exponent, b.as_tuple().exponent) + 2)
        return a + b


def _bo_ngay_tuong_lai(tong_ngay, ngay_xu_ly: date | None = None):
    # Cùng nguồn đồng hồ UTC+7 với kỳ chốt; không dùng ngày nghiệp vụ làm giờ hệ thống.
    if ngay_xu_ly is None:
        from .chot_ky import ngay_hien_tai

        ngay_xu_ly = ngay_hien_tai()
    tran = ngay_xu_ly.toordinal() + 1
    return {bam: giu for bam, ngay_so in tong_ngay.items()
            if (giu := {ngay: so for ngay, so in ngay_so.items()
                        if date.fromisoformat(ngay).toordinal() <= tran})}


def theo_tien_te(hs: HoSo, tien_te_nguong: str) -> HoSo:
    """Đổi đơn vị thì bỏ số liệu tiền, giữ đối tác; hồ sơ cũ nhận đơn vị lần đầu ghi."""
    if not isinstance(tien_te_nguong, str) or re.fullmatch(r"[A-Z]{3}", tien_te_nguong) is None:
        raise ValueError("Mã tiền tệ phải gồm ba chữ cái in hoa.")
    if hs.tien_te is not None and hs.tien_te != tien_te_nguong:
        return replace(hs, bieu_do={}, tong_ngay={}, tien_te=tien_te_nguong)
    return replace(hs, tien_te=tien_te_nguong)


def cong(
    hs: HoSo,
    ds: Iterable[tuple[Tien | None, str | None, date]],
    *,
    ky: str,
    cua_so_ngay: int = 7,
    te: Decimal | None = None,
    tien_te_nguong: str | None = None,
    ngay_xu_ly: date | None = None,
) -> tuple[HoSo, int]:
    """Biểu đồ nhận mọi khoản; lịch sử chia nhỏ chỉ nhận khoản < TE và ngày hợp lệ."""
    _so_thang(ky)
    if type(cua_so_ngay) is not int or cua_so_ngay < 1:
        raise ValueError("Cửa sổ ngày phải là số nguyên dương.")
    if te is not None and (not isinstance(te, Decimal) or not te.is_finite() or te <= 0):
        raise ValueError("TE phải là số thập phân dương hữu hạn.")
    if tien_te_nguong is not None:
        hs = theo_tien_te(hs, tien_te_nguong)
    bieu_do = {k: dict(v) for k, v in hs.bieu_do.items()}
    doi_tac = dict(hs.doi_tac)
    tong_ngay = {k: dict(v) for k, v in hs.tong_ngay.items()}
    for tien, bam, ngay in ds:
        if bam:
            doi_tac[bam] = max(doi_tac.get(bam, ky), ky)
        if tien is None:
            continue
        if hs.tien_te is None and tien.tien_te is not None:
            hs = theo_tien_te(hs, tien.tien_te)
        if tien.tien_te != hs.tien_te:
            raise ValueError("Tiền cộng hồ sơ phải cùng đơn vị ngưỡng.")
        so = tien.so.copy_abs()
        bucket = _bucket(so)
        thang = bieu_do.setdefault(ky, {})
        thang[bucket] = thang.get(bucket, 0) + 1
        if bam and (te is None or so < te):
            ngay_so = tong_ngay.setdefault(bam, {})
            khoa_ngay = ngay.isoformat()
            ngay_so[khoa_ngay] = _cong_tien(ngay_so.get(khoa_ngay, Decimal(0)), so)

    tong_ngay = _bo_ngay_tuong_lai(tong_ngay, ngay_xu_ly)
    ngay_lon_nhat = max((ngay for ngay_so in tong_ngay.values() for ngay in ngay_so), default=None)
    if ngay_lon_nhat is not None:
        moc = date.fromisoformat(ngay_lon_nhat).toordinal() - cua_so_ngay
        tong_ngay = {bam: giu for bam, ngay_so in tong_ngay.items()
                     if (giu := {ngay: so for ngay, so in ngay_so.items()
                                 if date.fromisoformat(ngay).toordinal() > moc})}
    so_bo = max(0, len(doi_tac) - TOI_DA_DOI_TAC)
    if so_bo:
        for bam in sorted(doi_tac, key=lambda bam: (doi_tac[bam], bam))[:so_bo]:
            del doi_tac[bam]
            tong_ngay.pop(bam, None)
    return HoSo(hs.khau, hs.loai, bieu_do, doi_tac, tong_ngay, hs.ky_lam_moi, hs.tien_te), so_bo


def anh_chup(hs: HoSo, *, tien_te_nguong: str) -> HoSoLoai:
    """Ảnh cho co.py, tiền đã ở đơn vị ngưỡng; không tự quy đổi tiền tệ.

    Khác đơn vị thì chỉ dùng tập đối tác, không dùng số đếm hay phân vị cũ.
    Phân vị dùng thứ hạng ceil(95*n/100), lấy cận trên bucket cho thận trọng.
    """
    hs = theo_tien_te(hs, tien_te_nguong)
    phan_vi = None
    if hs.so_nghiep_vu >= 50:
        tan_suat: dict[int, int] = {}
        for thang in hs.bieu_do.values():
            for b, n in thang.items():
                tan_suat[b] = tan_suat.get(b, 0) + n
        hang = (95 * hs.so_nghiep_vu + 99) // 100
        tong = 0
        for b, n in sorted(tan_suat.items()):
            tong += n
            if tong >= hang:
                with localcontext() as ctx:
                    ctx.prec = max(50, (b + 1) // 10 + 30)
                    can_tren = Decimal(10) ** (Decimal(b + 1) / Decimal(10))
                    phan_vi = can_tren.to_integral_value(rounding=ROUND_CEILING)
                break
    return HoSoLoai(hs.so_nghiep_vu, phan_vi, frozenset(hs.doi_tac))


def tong_truoc(hs: HoSo) -> Callable[[str, date], Decimal]:
    """Chụp tổng ngày trước lượt mới; bên gọi phải lấy trước khi cong lô mới."""
    du_lieu = {bam: dict(ngay_so) for bam, ngay_so in hs.tong_ngay.items()}

    def lay(bam: str, ngay: date) -> Decimal:
        return du_lieu.get(bam, {}).get(ngay.isoformat(), Decimal(0))

    return lay


def lam_moi(hs: HoSo, ky_moi: str, *, ngay_xu_ly: date | None = None) -> HoSo:
    """Giữ 12 tháng [ky_moi - 12, ky_moi), bỏ ngày tổng vượt ngày xử lý + 1."""
    cuoi = _so_thang(ky_moi)
    bieu_do = {ky: dict(thang) for ky, thang in hs.bieu_do.items()
               if cuoi - 12 <= _so_thang(ky) < cuoi}
    doi_tac = {bam: ky for bam, ky in hs.doi_tac.items()
               if cuoi - 12 <= _so_thang(ky) < cuoi}
    tong_ngay = {bam: dict(ngay_so) for bam, ngay_so in hs.tong_ngay.items() if bam in doi_tac}
    tong_ngay = _bo_ngay_tuong_lai(tong_ngay, ngay_xu_ly)
    return HoSo(hs.khau, hs.loai, bieu_do, doi_tac, tong_ngay, ky_moi, hs.tien_te)
