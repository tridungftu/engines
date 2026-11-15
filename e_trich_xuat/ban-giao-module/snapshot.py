"""TX-5: chuyển kết quả E1 thành snapshot cho module; không lưu hoặc kích hoạt."""
import hashlib
import json
import re

from kho_tri_thuc_sdk import danh_muc_tham_so as e1
from kho_tri_thuc_sdk.engine import LoiNghiepVu


def _loi(vuot=False):
    if vuot:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Bộ tham số vượt giới hạn xử lý.") from None
    raise LoiNghiepVu("BO_THAM_SO_KHONG_HOP_LE", "Bộ tham số không đúng cấu trúc; hãy kiểm tra bảng Excel.") from None


def tao_snapshot(excel, *, module, loai_hop_dong, phien_ban_bo):
    """Trả tham số bước và băm E1; caller sở hữu lựa chọn, prompt và kho bộ."""
    if not all(isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,200}", x)
               for x in (module, loai_hop_dong, phien_ban_bo)):
        _loi()
    try:
        dm = e1.doc_danh_muc(excel)
    except e1.LoiDanhMuc as exc:
        _loi(any(v.ma == "TEP_QUA_LON" for v in exc.loi))
    if dm.tom_tat["so_dang_dung"] > 200:
        _loi(True)
    bo = {"phien_ban": 1, "module": module, "loai_hop_dong": loai_hop_dong,
          "phien_ban_bo": phien_ban_bo, "cac_dong": dm.cac_dong,
          "quy_tac": dm.quy_tac, "bam_tep_goc": "sha256:" + dm.ma_bam,
          "ma_bam_noi_dung": dm.ma_bam_noi_dung}
    try:
        raw = json.dumps(bo, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError):
        _loi()
    if len(raw) > 64 * 1024:
        _loi(True)
    return {"bo_tham_so_json": raw.decode("utf-8"),
            "bam_bo_tham_so": "sha256:" + hashlib.sha256(raw).hexdigest()}
