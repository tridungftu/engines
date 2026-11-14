"""Bàn giao Word qua SDK 2.0; thay adapter ACK/SDK cũ trong ma-nguon.

Không giữ bản sao hay nhật ký nội dung trên đĩa. SDK quản lý lease, hủy,
gửi lại và xác nhận kết quả; không tự tạo một kênh bàn giao thứ hai.
"""

from pathlib import PurePosixPath

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .xuat_word import MIME_DOCX, dung_docx


def ban_giao_word(viec, tai_lieu):
    ten_goc = viec.dau_vao["tep"]["ten"]
    # Chỉ lấy tên tệp, xử lý cả dấu phân cách Windows khi test trên Linux.
    ten = PurePosixPath(ten_goc.replace("\\", "/")).stem
    if not ten or ten in (".", "..") or len(ten + "-OCR.docx") > 255 or any(ord(c) < 32 for c in ten):
        raise LoiNghiepVu("TEN_TEP_KHONG_HOP_LE", "Tên tệp gốc không hợp lệ. Hãy đổi tên tệp rồi thử lại.")
    viec.kiem_huy()
    raw = dung_docx(tai_lieu, kiem_huy=viec.kiem_huy)
    viec.kiem_huy()
    tep = viec.tai_tep_ra(f"{ten}-OCR.docx", raw, MIME_DOCX)
    return {"loai": "tep", "tep": tep}
