"""Khung tương thích đã ngừng dùng; không còn vòng đời khóa/danh mục.

Quyết định cuối e_mask §5.3 bỏ mở/đóng danh mục và vé giữ lượt. Core quản
lý mã yêu cầu bằng kho riêng; adapter mới ở chay.xu_ly_viec không dùng lớp này.
"""
from .chay import LoiMask, TienTrinhMask


class VongDoiMask(TienTrinhMask):
    def __init__(self, *, thu_muc_mask, cong, danh_muc_da_mo,
                 cho_phep_dung, cap_khoa=None, kiem_san_sang=None):
        if not callable(danh_muc_da_mo) or not callable(cho_phep_dung):
            raise LoiMask('THIEU_SEAM_VONG_DOI')
        super().__init__(thu_muc_mask=thu_muc_mask, cong=cong,
                         cap_khoa=cap_khoa, kiem_san_sang=kiem_san_sang,
                         cho_phep_dung=cho_phep_dung)
