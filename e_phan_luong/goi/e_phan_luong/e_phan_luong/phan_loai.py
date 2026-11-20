"""Đọc danh mục, so quy tắc theo thứ tự và chốt loại nghiệp vụ (PL-1C)."""
from __future__ import annotations

from dataclasses import dataclass
import re

from .kieu import (CHUA_PHAN_LOAI, NGUON_CHUA, NGUON_MODULE,
                   NGUON_QUY_TAC, NghiepVu)
from .loi import loi
from .tu_khoa import (TOI_DA_TU_KHOA, doc_json, khop_dieu_kien,
                      kiem_dieu_kien)

TOI_DA_BYTE_DANH_MUC = 16 * 1024
TOI_DA_LOAI = 100
_MA_LOAI = re.compile(r"[a-z][a-z0-9_]{0,39}")


@dataclass(frozen=True)
class BoPhanLoai:
    """Bộ đã kiểm cấu trúc; tim trả mã của quy tắc đầu tiên khớp."""
    quy_tac: tuple[dict, ...] = ()

    def tim(self, noi_dung: str | None) -> str | None:
        if noi_dung is None:
            return None
        for qt in self.quy_tac:
            if any(khop_dieu_kien(dk, noi_dung) for dk in qt["khi"]):
                return qt["loai"]
        return None


def doc_danh_muc_loai(chuoi: str | None) -> dict[str, dict]:
    if chuoi is None or chuoi == "":
        return {}
    ds = doc_json(chuoi, TOI_DA_BYTE_DANH_MUC)
    if not isinstance(ds, list) or len(ds) > TOI_DA_LOAI:
        raise loi("THAM_SO_KHONG_HOP_LE")
    danh_muc = {}
    for muc in ds:
        if (not isinstance(muc, dict) or set(muc) != {"ma", "ten", "mo_ta"}
                or not isinstance(muc["ma"], str)
                or not _MA_LOAI.fullmatch(muc["ma"])
                or muc["ma"] == CHUA_PHAN_LOAI or muc["ma"] in danh_muc
                or not isinstance(muc["ten"], str) or not muc["ten"].strip()
                or not isinstance(muc["mo_ta"], str)):
            raise loi("THAM_SO_KHONG_HOP_LE")
        danh_muc[muc["ma"]] = muc
    return danh_muc


def doc_bo_phan_loai(chuoi: str | None, danh_muc) -> BoPhanLoai:
    if chuoi is None or chuoi == "":
        return BoPhanLoai()
    d = doc_json(chuoi)
    if (not isinstance(d, dict) or set(d) != {"phien_ban", "quy_tac"}
            or type(d["phien_ban"]) is not int or d["phien_ban"] != 1
            or not isinstance(d["quy_tac"], list)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    for qt in d["quy_tac"]:
        if (not isinstance(qt, dict) or set(qt) != {"loai", "khi"}
                or not isinstance(qt["loai"], str) or qt["loai"] not in danh_muc
                or not isinstance(qt["khi"], list) or not qt["khi"]):
            raise loi("THAM_SO_KHONG_HOP_LE")
        so_tu = 0
        for dk in qt["khi"]:
            so_tu += kiem_dieu_kien(dk)
            if so_tu > TOI_DA_TU_KHOA:
                raise loi("THAM_SO_KHONG_HOP_LE")
    return BoPhanLoai(tuple(d["quy_tac"]))


def lay_noi_dung(nv: NghiepVu, truong_phan_loai: str | None) -> str | None:
    if truong_phan_loai is None or truong_phan_loai == "":
        return None
    if (not isinstance(truong_phan_loai, str) or len(truong_phan_loai) > 60
            or not (truong_phan_loai in {"dien_giai", "tai_khoan_no", "tai_khoan_co"}
                    or (truong_phan_loai.startswith("thuoc_tinh.")
                        and len(truong_phan_loai) > len("thuoc_tinh.")))):
        raise loi("THAM_SO_KHONG_HOP_LE")
    return nv.noi_dung.get(truong_phan_loai)


def gan_loai(nv, danh_muc, bo, truong_phan_loai) -> tuple[str | None, str | None]:
    noi_dung = lay_noi_dung(nv, truong_phan_loai)
    if nv.loai is not None:
        if not isinstance(nv.loai, str) or nv.loai not in danh_muc:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        return nv.loai, NGUON_MODULE
    loai = bo.tim(noi_dung)
    if loai is not None:
        return loai, NGUON_QUY_TAC
    return None, None


def chot_loai(ket_qua) -> tuple[str, str]:
    """Giữ kết quả đã gán; phần chưa có kết quả chuyển về loại dành riêng."""
    if ket_qua == (None, None):
        return CHUA_PHAN_LOAI, NGUON_CHUA
    return ket_qua
