"""Bảng lỗi người dùng của e_phan_luong (phiếu §7). Lead giữ; Codex KHÔNG sửa câu.

Dùng: `raise loi("THIEU_NGUONG")`. Câu không chứa đường dẫn, khóa, dữ liệu nghiệp vụ.
Chi tiết kỹ thuật (dòng nào, trường nào) chỉ ghi nhật ký engine, không đưa vào câu.
"""
from __future__ import annotations

from kho_tri_thuc_sdk.engine import LoiNghiepVu

CAU_LOI = {
    "TEP_KHONG_HO_TRO": "Chỉ nhận tệp JSON, Excel .xlsx hoặc CSV UTF-8.",
    "DU_LIEU_KHONG_HOP_LE": "Dữ liệu nghiệp vụ chưa đúng mẫu. Vui lòng kiểm tra lại tệp gửi.",
    "THIEU_NGUONG": "Chưa có ngưỡng PM/TE/SAD hợp lệ cho kỳ này. Quản trị viên cần nhập ngưỡng.",
    "THAM_SO_KHONG_HOP_LE": "Cài đặt bước chưa đúng. Quản trị viên kiểm tra lại cài đặt của quy trình.",
    "KHONG_PHAI_LOCAL": "Bước phân loại chỉ nhận kết quả từ AI nội bộ.",
    "CHUOI_KHONG_KHOP": "Không khớp dữ liệu giữa các bước. Vui lòng chạy lại kiểm tra cảnh báo.",
    "LUOT_KHONG_TON_TAI": "Không tìm thấy lượt phân luồng. Vui lòng chạy lại kiểm tra cảnh báo.",
    "NGAN_BAN": "Dữ liệu thống kê đang được cập nhật. Vui lòng thử lại sau ít phút.",
    "VUOT_GIOI_HAN": "Tệp vượt giới hạn xử lý. Vui lòng tách lô nhỏ hơn.",
    "THIEU_GIAI_THICH": "Dòng AI kiểm sai cần ghi giải thích để AI học từ lỗi. Vui lòng điền cột Giải thích rồi gửi lại.",
}

THU_LAI_DUOC = frozenset({"NGAN_BAN"})


def loi(ma: str) -> LoiNghiepVu:
    """Tạo LoiNghiepVu đúng câu của phiếu §7. Mã lạ là lỗi lập trình."""
    return LoiNghiepVu(ma, CAU_LOI[ma], thu_lai_duoc=ma in THU_LAI_DUOC)
