"""Xuất kết quả PL-2 trong RAM; trường công bố không mang chính sách (C5)."""
from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal, localcontext
import json

from .kieu import (
    CHON_MAU, CHUA_PHAN_LOAI, CHUA_QUY_DOI, CHUA_RO_TIEN_TE, CO_DO_CUNG,
    LY_DO_BAT_BUOC, NGHI_CHIA_NHO, NOP_LAI, THU_TU_LY_DO, VUOT_PM, VUOT_TE,
    KetQuaDong, Lo, Nguong, Tien,
)
from .nguong import tien_so_sanh
from .tien import tien_ra


_CAU_LY_DO = {
    VUOT_PM: "Đạt hoặc vượt ngưỡng PM.",
    VUOT_TE: "Đạt hoặc vượt ngưỡng TE.",
    CHUA_QUY_DOI: "Chưa quy đổi về tiền tệ của ngưỡng.",
    CHUA_RO_TIEN_TE: "Chưa rõ tiền tệ.",
    NGHI_CHIA_NHO: "Có dấu hiệu chia nhỏ nghiệp vụ.",
    CO_DO_CUNG: "Module yêu cầu kiểm tra bắt buộc.",
    NOP_LAI: "Lần nộp trước cần kiểm nhưng chưa có kết quả kiểm.",
    CHON_MAU: "Được chọn kiểm tra.",
}


def tao_tep_json(ds_dong: Sequence[KetQuaDong], *, thong_tin: dict) -> bytes:
    """Tuần tự hóa theo danh sách cột cố định, ổn định từng byte (UTF-8/LF)."""
    du_lieu = {
        "phien_ban": 1,
        **{cot: thong_tin[cot] for cot in (
            "ma_luot", "bam_hat_giong", "bam_dau_vao", "phien_ban_engine", "khau", "ma_module",
        )},
        "nghiep_vu": [{
            "ma": d.ma, "luong": d.luong, "ly_do": list(d.ly_do), "co": list(d.co),
            "loai": d.loai, "nguon_loai": d.nguon_loai,
        } for d in ds_dong],
    }
    return (json.dumps(du_lieu, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def canh_bao(ds_dong: Sequence[KetQuaDong]) -> str:
    """Chỉ câu lý do Đỏ cố định; toàn bộ danh mục ngắn hơn 500 ký tự."""
    cac_ma = {ma for d in ds_dong if d.luong == "do" for ma in d.ly_do}
    return " ".join(_CAU_LY_DO[ma] for ma in THU_TU_LY_DO if ma in cac_ma and ma in _CAU_LY_DO)


def tao_truong_ra(
    lo: Lo, ng: Nguong, ds_dong: Sequence[KetQuaDong], *, thong_tin: dict, tep_json: dict,
) -> dict:
    """Đủ trường phiếu §5.5; tổng theo tiền so ngưỡng (trị tuyệt đối).

    Một dòng Đỏ chưa so được tiền tệ làm tổng là null. Không có dòng Đỏ:
    tổng bằng không, kèm tiền tệ của ngưỡng. Excel để null tới PL-8.
    """
    ds_do = [d for d in ds_dong if d.luong == "do"]
    ma_do = {d.ma for d in ds_do}
    tien_do = [tien_so_sanh(nv, ng)[0] for nv in lo.nghiep_vu if nv.ma in ma_do]
    if any(t is None for t in tien_do):
        tong = None
    else:
        # 50.000 khoản, tối đa 18 chữ số nguyên + 6 chữ số lẻ: không mất lẻ.
        with localcontext() as ctx:
            ctx.prec = 40
            tong = Tien(sum((t.so for t in tien_do), Decimal(0)), ng.tien_te)
    return {
        **{cot: thong_tin[cot] for cot in ("ma_luot", "bam_hat_giong", "bam_dau_vao", "phien_ban_engine")},
        "luong": "do" if ds_do else "xanh", "can_nguoi_kiem": bool(ds_do),
        "canh_bao": canh_bao(ds_dong),
        "so_nghiep_vu": len(ds_dong), "so_do": len(ds_do),
        "so_do_bat_buoc": sum(bool(set(d.ly_do) & LY_DO_BAT_BUOC) for d in ds_do),
        "so_do_chon_mau": sum(CHON_MAU in d.ly_do for d in ds_do),
        "so_xanh": len(ds_dong) - len(ds_do),
        "so_chua_phan_loai": sum(d.loai == CHUA_PHAN_LOAI for d in ds_dong),
        "tong_tien_do": tien_ra(tong), "tep_json": tep_json, "tep_ds_do": None,
    }
