"""Cửa SDK cho kho nhận diện MASK-R1/R2.

Không tạo kho dự phòng. Kho này không giữ ánh xạ mở che theo chuỗi.
"""
from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganEngine


THOI_HAN_ANH_XA_MAC_DINH = 600
THOI_HAN_ANH_XA_TOI_THIEU = 60
THOI_HAN_ANH_XA_TOI_DA = 900
PHIEN_BAN_CHUAN_HOA = 'NFC_CF_KHOANG_TRANG_LOWER_1'


def can_bao_dam_core():
    """C-P4-03: chưa có cửa xác nhận duy nhất bí mật và dấu gặp chống lặp.

    Không nhận cờ từ cấu hình/payload để bật ghi. Khóa ngẫu nhiên mỗi lô
    của SDK chỉ chống gửi lại chính lô ấy, không chống việc được giao lại.
    """
    raise LoiNghiepVu(
        'MASK_KHO_CAN_CORE',
        'Kho định danh chưa có bảo đảm chống trùng và xử lý gửi lại của Core. '
        'Anh hãy nhờ quản trị viên kiểm tra trước khi tiếp tục.',
    ) from None


def ngan_cua_viec(viec):
    """Chỉ nhận cửa ngăn SDK của việc, không tự tạo ngăn trong bộ nhớ."""
    ngan = getattr(viec, 'ngan', None)
    if not isinstance(ngan, NganEngine):
        raise LoiNghiepVu(
            'MASK_NGAN_CHUA_CO',
            'Chưa kết nối được ngăn dữ liệu của Core. Anh hãy thử lại sau.',
            thu_lai_duoc=True,
        ) from None
    return ngan


def thoi_han_anh_xa_giay(viec):
    """Đọc TTL từ bản chụp cấu hình SDK; chưa tạo hay gia hạn ánh xạ RAM."""
    cau_hinh = getattr(viec, 'cau_hinh', None)
    if isinstance(cau_hinh, dict) and not set(cau_hinh) - {'thoi_han_anh_xa_giay'}:
        giay = cau_hinh.get('thoi_han_anh_xa_giay', THOI_HAN_ANH_XA_MAC_DINH)
        if (type(giay) is int
                and THOI_HAN_ANH_XA_TOI_THIEU <= giay <= THOI_HAN_ANH_XA_TOI_DA):
            return giay
    raise LoiNghiepVu(
        'MASK_CAU_HINH_KHONG_HOP_LE',
        'Thời hạn ánh xạ phải là số nguyên từ 60 đến 900 giây.',
    ) from None
