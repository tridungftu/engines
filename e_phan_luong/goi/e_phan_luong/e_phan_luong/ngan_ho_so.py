"""Hồ sơ hành vi qua ngăn Core; mỗi lần CAS đều áp lại phép cập nhật thuần."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from kho_tri_thuc_sdk.engine import BanGhi

from . import ho_so, ngan_chung
from .chot_ky import ky_hien_tai
from .loi import loi


def doc_ho_so_khau(viec, khau: str) -> dict[str, tuple[ho_so.HoSo, BanGhi | None]]:
    """Đọc đủ mọi loại của khâu, gồm cả loại không xuất hiện trong lô mới."""
    return {
        ban.gia_tri["loai"]: (ho_so.tu_ban_ghi(ban.gia_tri), ban)
        for ban in ngan_chung.tim_tat_ca(viec, "ho_so_hanh_vi", {"khau": khau})
    }


def ghi_ho_so(
    viec, khau: str, loai: str, ham_cap_nhat: Callable[[ho_so.HoSo], ho_so.HoSo],
) -> ho_so.HoSo:
    """Tạo hồ sơ rỗng nếu thiếu, rồi đọc/sửa CAS; trả hồ sơ đã ghi thành công.

    ham_cap_nhat có thể chạy lại khi xung đột nên không tự ghi ngăn hay log
    số đã bỏ. Hồ sơ mới đã thuộc kỳ hiện tại, không cần làm mới lần nữa
    trong tháng tạo (kể cả khi chưa có kết quả kiểm để tạo dòng ty_le).
    """
    khoa = {"khau": khau, "loai": loai}
    if viec.ngan.doc("ho_so_hanh_vi", khoa) is None:
        rong = replace(ho_so.moi(khau, loai), ky_lam_moi=ky_hien_tai())

        def tao(lo):
            lo.lay_hoac_tao("ho_so_hanh_vi", khoa, ho_so.ve_ban_ghi(rong))

        ngan_chung.ghi_lo_thu_lai(viec, tao)

    da_ghi = None

    def cap_nhat(lo):
        nonlocal da_ghi
        ban = viec.ngan.doc("ho_so_hanh_vi", khoa)
        if ban is None:
            raise loi("NGAN_BAN")
        da_ghi = ham_cap_nhat(ho_so.tu_ban_ghi(ban.gia_tri))
        lo.sua("ho_so_hanh_vi", khoa, ho_so.ve_ban_ghi(da_ghi), row_version=ban.row_version)

    ngan_chung.ghi_lo_thu_lai(viec, cap_nhat)
    return da_ghi
