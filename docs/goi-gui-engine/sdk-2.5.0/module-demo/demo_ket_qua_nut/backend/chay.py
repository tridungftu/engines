"""Điểm vào SDK module; Core cấp tiến trình và ngữ cảnh."""
from . import xu_ly


def chay(**tham_so_core):
    from kho_tri_thuc_sdk import module_runtime
    return module_runtime.chay_theo_khai_bao(
        xu_ly.XU_LY, su_kien=xu_ly.SU_KIEN,
        loi_nghiep_vu=xu_ly.LoiNghiepVu, **tham_so_core)
