"""Chính sách và bản ghi tỷ lệ nội bộ của engine (không phải trường ra C5)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, replace
from decimal import Decimal, InvalidOperation

from .kieu import (
    CHE_DO_BAC, CHE_DO_TOAN_BO, CHUA_PHAN_LOAI, CUOI_KY, DOI_TAC_MOI,
    NGAY_NGHI, NHAP_TAY, SO_TIEN_BAT_THUONG, SO_TRON, THU_TU_CO,
)
from .loi import loi


@dataclass(frozen=True)
class ChinhSach:
    bac: tuple[Decimal, ...] = tuple(map(Decimal, ("0.30", "0.20", "0.10", "0.05")))
    nguong_xuong: tuple[Decimal, ...] = tuple(map(Decimal, ("0.10", "0.05", "0.03")))
    mau_toi_thieu: tuple[Decimal, ...] = tuple(map(Decimal, ("30", "60", "100")))
    ty_le_chua_phan_loai: Decimal = Decimal("0.30")
    mau_sach_toan_bo: Decimal = Decimal(30)
    nguong_diem_rui_ro: Decimal = Decimal("0.10")
    do_tin_cay: Decimal = Decimal("0.95")
    he_so: dict[str, Decimal] = field(default_factory=lambda: {
        SO_TIEN_BAT_THUONG: Decimal(2), DOI_TAC_MOI: Decimal(2),
        SO_TRON: Decimal("1.5"), NGAY_NGHI: Decimal("1.5"),
        CUOI_KY: Decimal("1.5"), NHAP_TAY: Decimal("1.5"),
    })
    don_vi_so_tron: Decimal = Decimal(10000000)
    ty_le_duoi_sad: Decimal = Decimal("0.02")
    san: Decimal = Decimal("0.05")


def _so(gia_tri, ma_loi: str) -> Decimal:
    if isinstance(gia_tri, bool) or not isinstance(gia_tri, (str, int, Decimal)):
        raise loi(ma_loi)
    try:
        so = Decimal(gia_tri)
    except InvalidOperation:
        raise loi(ma_loi) from None
    if not so.is_finite():
        raise loi(ma_loi)
    return so


def _so_chinh_sach(gia_tri) -> Decimal:
    # JSON số là số, không nhận chuỗi hay boolean thay cho một tỷ lệ.
    if not isinstance(gia_tri, (int, Decimal)) or isinstance(gia_tri, bool):
        raise loi("THAM_SO_KHONG_HOP_LE")
    return _so(gia_tri, "THAM_SO_KHONG_HOP_LE")


def _doi_tuong(cac_cap):
    ket_qua = {}
    for khoa, gia_tri in cac_cap:
        if khoa in ket_qua:
            raise loi("THAM_SO_KHONG_HOP_LE")
        ket_qua[khoa] = gia_tri
    return ket_qua


def _hang_so_khong_hop_le(_):
    raise loi("THAM_SO_KHONG_HOP_LE")


def _kiem_chinh_sach(cs: ChinhSach) -> None:
    if (not cs.bac or any(not Decimal(0) < b <= Decimal(1) for b in cs.bac)
            or any(a <= b for a, b in zip(cs.bac, cs.bac[1:]))
            or len(cs.nguong_xuong) != len(cs.bac) - 1
            or len(cs.mau_toi_thieu) != len(cs.bac) - 1):
        raise loi("THAM_SO_KHONG_HOP_LE")
    cac_ty_le = (*cs.nguong_xuong, cs.ty_le_chua_phan_loai,
                 cs.nguong_diem_rui_ro, cs.ty_le_duoi_sad, cs.san)
    if any(not Decimal(0) <= p <= Decimal(1) for p in cac_ty_le):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if (not Decimal(0) < cs.do_tin_cay < Decimal(1) or cs.don_vi_so_tron <= 0
            or any(h < 1 for h in cs.he_so.values())
            or any(n <= 0 or n != n.to_integral_value()
                   for n in (*cs.mau_toi_thieu, cs.mau_sach_toan_bo))):
        raise loi("THAM_SO_KHONG_HOP_LE")


def doc_chinh_sach(
    chuoi: str | None,
    *,
    ty_le_duoi_sad: Decimal | None = None,
) -> ChinhSach:
    """Đọc JSON tối đa 8 KiB; khóa vắng giữ mặc định, hệ số ghi đè theo cờ.

    Tham số bước ty_le_duoi_sad thay mặc định; JSON vẫn ghi đè từng khóa.
    """
    cs = ChinhSach()
    cap_nhat = {}
    if ty_le_duoi_sad is not None:
        cap_nhat["ty_le_duoi_sad"] = _so_chinh_sach(ty_le_duoi_sad)
    if chuoi is not None:
        if not isinstance(chuoi, str):
            raise loi("THAM_SO_KHONG_HOP_LE")
        try:
            if len(chuoi.encode("utf-8")) > 8192:
                raise loi("THAM_SO_KHONG_HOP_LE")
            du_lieu = json.loads(
                chuoi, parse_float=Decimal, parse_int=Decimal,
                parse_constant=_hang_so_khong_hop_le, object_pairs_hook=_doi_tuong,
            ) if chuoi.strip() else {}
        except (ValueError, UnicodeError, RecursionError):
            raise loi("THAM_SO_KHONG_HOP_LE") from None
        if not isinstance(du_lieu, dict) or du_lieu.keys() - {f.name for f in fields(cs)}:
            raise loi("THAM_SO_KHONG_HOP_LE")
        for khoa, gia_tri in du_lieu.items():
            if khoa in {"bac", "nguong_xuong", "mau_toi_thieu"}:
                if not isinstance(gia_tri, list):
                    raise loi("THAM_SO_KHONG_HOP_LE")
                cap_nhat[khoa] = tuple(_so_chinh_sach(v) for v in gia_tri)
            elif khoa == "he_so":
                if not isinstance(gia_tri, dict) or gia_tri.keys() - set(THU_TU_CO):
                    raise loi("THAM_SO_KHONG_HOP_LE")
                cap_nhat[khoa] = {**cs.he_so, **{
                    co: _so_chinh_sach(h) for co, h in gia_tri.items()
                }}
            else:
                cap_nhat[khoa] = _so_chinh_sach(gia_tri)
    cs = replace(cs, **cap_nhat)
    _kiem_chinh_sach(cs)
    return cs


@dataclass(frozen=True)
class TrangThai:
    khau: str
    loai: str
    bac: Decimal
    che_do: str = CHE_DO_BAC
    mau_tu_doi_bac: int = 0
    loi_tu_doi_bac: int = 0
    mau_sach_toan_bo: int = 0
    mau_12t: int = 0
    loi_12t: int = 0
    loi_sad_12t: int = 0
    loi_ngoai_mau_12t: int = 0
    diem: Decimal | None = None
    nhan: frozenset[str] = frozenset()
    doi_bac_luc: str | None = None


def moi(khau: str, loai: str, cs: ChinhSach) -> TrangThai:
    return TrangThai(khau=khau, loai=loai, bac=cs.bac[0])


_COT_DEM = (
    "mau_tu_doi_bac", "loi_tu_doi_bac", "mau_sach_toan_bo", "mau_12t",
    "loi_12t", "loi_sad_12t", "loi_ngoai_mau_12t",
)


def tu_ban_ghi(ban_ghi: dict) -> TrangThai:
    """Chuyển các cột ngăn Core thành kiểu nội bộ; bỏ qua cột hệ thống."""
    if not isinstance(ban_ghi, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    try:
        gia_tri = {f.name: ban_ghi[f.name] for f in fields(TrangThai)}
        for cot in ("bac", "diem", *_COT_DEM):
            if cot == "diem" and gia_tri[cot] is None:
                continue
            so = _so(gia_tri[cot], "DU_LIEU_KHONG_HOP_LE")
            if so < 0 or (cot in _COT_DEM and so != so.to_integral_value()):
                raise loi("DU_LIEU_KHONG_HOP_LE")
            gia_tri[cot] = int(so) if cot in _COT_DEM else so
        if (not isinstance(gia_tri["nhan"], str)
                or gia_tri["che_do"] not in {CHE_DO_BAC, CHE_DO_TOAN_BO}
                or not Decimal(0) < gia_tri["bac"] <= Decimal(1)
                or (gia_tri["diem"] is not None and gia_tri["diem"] > 1)
                or gia_tri["loi_12t"] > gia_tri["mau_12t"]
                or gia_tri["loi_tu_doi_bac"] > gia_tri["mau_tu_doi_bac"]):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        gia_tri["nhan"] = frozenset(n for n in gia_tri["nhan"].split(",") if n)
        return TrangThai(**gia_tri)
    except (KeyError, TypeError):
        raise loi("DU_LIEU_KHONG_HOP_LE") from None


def ve_ban_ghi(tt: TrangThai) -> dict:
    """Đúng các cột bảng ty_le; mọi số thành chuỗi thập phân, không dùng số mũ."""
    ban_ghi = {f.name: getattr(tt, f.name) for f in fields(tt)}
    for cot in ("bac", "diem", *_COT_DEM):
        if ban_ghi[cot] is not None:
            ban_ghi[cot] = format(ban_ghi[cot], "f") if cot in {"bac", "diem"} else str(ban_ghi[cot])
    ban_ghi["nhan"] = ",".join(sorted(tt.nhan))
    return ban_ghi


def p_bac(tt: TrangThai, cs: ChinhSach) -> Decimal:
    if tt.che_do == CHE_DO_TOAN_BO:
        return Decimal(1)
    if tt.loai == CHUA_PHAN_LOAI:
        return cs.ty_le_chua_phan_loai
    return tt.bac
