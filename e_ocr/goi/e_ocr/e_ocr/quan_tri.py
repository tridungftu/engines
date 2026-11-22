"""Kiểm nguồn OCR, không gửi tài liệu, không ghi cấu hình hoặc hạn mức.

SDK 2.5.0 chưa có cổng quản trị. Core nối các hàm trong THAO_TAC theo
KHAI-SDK-2.1.json khi mở cổng chung; không đăng ký thành năng lực OCR.
"""

import os
from pathlib import Path
from types import SimpleNamespace

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .abbyy import BackendABBYY
from .tesseract import _kiem_bo_doc


def _cau_hinh(tac, nhom):
    dau_vao = tac.dau_vao
    if type(dau_vao) is not dict or set(dau_vao) != {nhom}:
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Cần gửi đúng phần cấu hình nguồn đang kiểm tra.")
    cfg = dau_vao[nhom]
    if type(cfg) is not dict:
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Cấu hình nguồn cần là một nhóm các trường hợp lệ.")
    return cfg


def kiem_hot_folder(tac):
    """Chỉ kiểm metadata/quyền, không liệt kê hoặc mở hồ sơ Hot Folder.

    os.access không chứng minh quyền ghi ACL thực tế hoặc FineReader đang
    theo dõi thư mục. Không tạo tệp thăm dò vì có thể kích hoạt OCR thật.
    """
    cfg = _cau_hinh(tac, "abbyy")
    for ma in ("thu_muc_vao", "thu_muc_ra"):
        if type(cfg.get(ma)) is not str or not cfg[ma].strip() or len(cfg[ma]) > 4096:
            raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Cần nhập đủ thư mục nhận tài liệu và thư mục trả kết quả.")
    try:
        nguon = BackendABBYY({**cfg, "bat": True, "thoi_han_giay": 900})
        if not all(os.access(p, os.R_OK | os.W_OK | os.X_OK) for p in (nguon._vao, nguon._ra)):
            raise OSError
    except (LoiNghiepVu, OSError, ValueError):
        return {"dat": False, "ma": "HOT_FOLDER_KHONG_TRUY_CAP"}
    return {"dat": True, "ma": "HOT_FOLDER_TRUY_CAP_DUOC"}


def kiem_tesseract(tac):
    """Kiểm bộ ngôn ngữ bằng --list-langs, tối đa 10 giây; không OCR ảnh."""
    cfg = _cau_hinh(tac, "tesseract")
    ten, ngon_ngu = cfg.get("duong_dan", ""), cfg.get("ngon_ngu", "vie+eng")
    if (type(ten) is not str or len(ten) > 4096 or
            ngon_ngu not in ("vie", "eng", "vie+eng", "eng+vie")):
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Cần nhập đường dẫn Tesseract và chọn ngôn ngữ trong danh sách.")
    # Nút quản trị không trở thành cửa chạy một chương trình tùy ý.
    if ten and Path(ten.replace("\\", "/")).name.lower() not in ("tesseract", "tesseract.exe"):
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Đường dẫn phải trỏ tới chương trình tesseract hoặc tesseract.exe.")
    try:
        viec_kiem = SimpleNamespace(kiem_huy=getattr(tac, "kiem_huy", lambda: None))
        _kiem_bo_doc({"duong_dan": ten, "ngon_ngu": ngon_ngu}, viec_kiem)
    except LoiNghiepVu as loi:
        ma = "TESSERACT_QUA_THOI_HAN" if loi.ma == "TESSERACT_QUA_THOI_HAN" else "TESSERACT_CHUA_DUNG_DUOC"
        return {"dat": False, "ma": ma}
    return {"dat": True, "ma": "TESSERACT_DU_NGON_NGU"}


THAO_TAC = {"kiem_hot_folder": kiem_hot_folder, "kiem_tesseract": kiem_tesseract}
