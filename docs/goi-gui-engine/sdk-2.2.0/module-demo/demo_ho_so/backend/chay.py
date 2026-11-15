"""Điểm vào backend (`backend.diem_vao` = "backend.chay"): Core gọi `chay(...)` khi khởi chạy tiến trình module.

Giao bảng xử lý `{hanh_dong.ma: hàm}` và bảng sự kiện cho bộ chạy module (hợp đồng a.10 điểm 6). SDK 2.0 phía
module có điểm vào chung (`module_runtime.chay_theo_khai_bao`, tên đề xuất, W3 chốt) thì dùng nó; chưa có thì
dùng bộ chạy tạm trong gói (`bo_chay.py`, dựng ModuleRuntime hiện hành từ module.json).
"""

from __future__ import annotations

from . import xu_ly


def chay(**tham_so_core):
    from kho_tri_thuc_sdk import module_runtime

    chay_theo_khai_bao = getattr(module_runtime, "chay_theo_khai_bao", None)
    if chay_theo_khai_bao is not None:
        return chay_theo_khai_bao(xu_ly.XU_LY, su_kien=xu_ly.SU_KIEN, loi_nghiep_vu=xu_ly.LoiNghiepVu, **tham_so_core)
    from . import bo_chay
    return bo_chay.chay(xu_ly.XU_LY, loi_nghiep_vu=xu_ly.LoiNghiepVu, **tham_so_core)
