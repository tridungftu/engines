"""Đọc bytes JSON lô nghiệp vụ; chỉ giữ dữ liệu trong bộ nhớ của một việc."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
import json
import re
import unicodedata

from .kieu import Lo, NghiepVu
from .loi import loi
from .tien import doc_tien

TOI_DA_BYTE = 20 * 1048576
TOI_DA_DONG = 50000


def _doi_tuong(cac_cap: list[tuple[str, object]]) -> dict:
    ket_qua = {}
    for khoa, gia_tri in cac_cap:
        if khoa in ket_qua:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        ket_qua[khoa] = gia_tri
    return ket_qua


def _hang_so_khong_hop_le(_chuoi: str):
    raise loi("DU_LIEU_KHONG_HOP_LE")


def _chu_tuy_chon(dong: dict, khoa: str) -> str | None:
    gia_tri = dong.get(khoa)
    if gia_tri is not None and not isinstance(gia_tri, str):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return gia_tri


def _doc_dong(dong: dict, chi_so: int) -> NghiepVu:
    if not isinstance(dong, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ma = dong.get("ma")
    if not isinstance(ma, str) or not 1 <= len(ma) <= 120:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if any(unicodedata.category(ky_tu) == "Cc" for ky_tu in ma):
        raise loi("DU_LIEU_KHONG_HOP_LE")

    ngay = dong.get("ngay")
    if not isinstance(ngay, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", ngay) is None:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    try:
        ngay = date.fromisoformat(ngay)
    except ValueError:
        raise loi("DU_LIEU_KHONG_HOP_LE") from None

    nhap_tay = dong.get("nhap_tay", False)
    co_do_cung = dong.get("co_do_cung", False)
    if type(nhap_tay) is not bool or type(co_do_cung) is not bool:
        raise loi("DU_LIEU_KHONG_HOP_LE")

    noi_dung = {}
    for khoa in ("dien_giai", "tai_khoan_no", "tai_khoan_co"):
        gia_tri = _chu_tuy_chon(dong, khoa)
        if gia_tri is not None:
            noi_dung[khoa] = gia_tri
    thuoc_tinh = dong.get("thuoc_tinh", {})
    if not isinstance(thuoc_tinh, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    for khoa, gia_tri in thuoc_tinh.items():
        if not isinstance(khoa, str) or not (
            isinstance(gia_tri, (str, Decimal)) or type(gia_tri) is int
        ):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        if isinstance(gia_tri, Decimal):
            if not gia_tri.is_finite():
                raise loi("DU_LIEU_KHONG_HOP_LE")
            # str(Decimal) gọn cả với số mũ lớn; đây là nội dung, không phải tiền.
        noi_dung[f"thuoc_tinh.{khoa}"] = str(gia_tri)

    return NghiepVu(
        chi_so=chi_so,
        ma=ma,
        ngay=ngay,
        so_tien=doc_tien(dong.get("so_tien")),
        so_tien_quy_doi=doc_tien(dong.get("so_tien_quy_doi"), cho_phep_null=True),
        loai=_chu_tuy_chon(dong, "loai"),
        doi_tac=_chu_tuy_chon(dong, "doi_tac"),
        noi_dung=noi_dung,
        nhap_tay=nhap_tay,
        co_do_cung=co_do_cung,
    )


def doc_lo_json(du_lieu: bytes) -> Lo:
    """Đọc UTF-8 có/không BOM, từ chối khóa/mã trùng và vượt trần toàn lô."""
    if not isinstance(du_lieu, bytes):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(du_lieu) > TOI_DA_BYTE:
        raise loi("VUOT_GIOI_HAN")
    try:
        lo = json.loads(
            du_lieu.decode("utf-8-sig"),
            parse_float=Decimal,
            parse_constant=_hang_so_khong_hop_le,
            object_pairs_hook=_doi_tuong,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        raise loi("TEP_KHONG_HO_TRO") from None
    except (ValueError, InvalidOperation):
        # Số nguyên/số mũ JSON vượt giới hạn chuyển đổi của Python/Decimal.
        raise loi("DU_LIEU_KHONG_HOP_LE") from None

    if not isinstance(lo, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if type(lo.get("phien_ban")) is not int or lo["phien_ban"] != 1:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ma_module = lo.get("ma_module")
    if not isinstance(ma_module, str) or len(ma_module) > 31 or re.fullmatch(
        r"[a-z][a-z0-9_]*", ma_module
    ) is None:
        raise loi("DU_LIEU_KHONG_HOP_LE")

    ky = lo.get("ky")
    if ky is not None and (
        not isinstance(ky, str)
        or re.fullmatch(r"[0-9]{4}-(?:0[1-9]|1[0-2])", ky) is None
        or ky[:4] == "0000"
    ):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    nguong = lo.get("nguong")
    if nguong is not None and not isinstance(nguong, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ds = lo.get("nghiep_vu")
    if not isinstance(ds, list):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(ds) > TOI_DA_DONG:
        raise loi("VUOT_GIOI_HAN")

    cac_ma = set()
    nghiep_vu = []
    for chi_so, dong in enumerate(ds):
        nv = _doc_dong(dong, chi_so)
        if nv.ma in cac_ma:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        cac_ma.add(nv.ma)
        nghiep_vu.append(nv)
    return Lo(lo["phien_ban"], ma_module, ky, nguong, tuple(nghiep_vu))
