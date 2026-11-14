"""Nguồn từ vựng chỉ do cấu hình tin cậy của lead cấp; mặc định đóng.

Không đọc cấu hình từ nội dung việc, không có từ điển dự phòng. Adapter sau
này gọi nap_cau_hinh trước khi nhận việc; MASK-2 chưa nối kênh cấu hình Core.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import re

from .nguon.privacy.types import PrivacyError

TEN_TAI_NGUYEN = frozenset({
    "vn_surnames.txt", "vn_places.txt", "common_acronyms.txt", "leftover_allowlist.txt",
})
_du_lieu = {}
_cac_cache = []


class ThieuTaiNguyen(PrivacyError):
    ma = "MASK_THIEU_TAI_NGUYEN"

    def __init__(self):
        super().__init__("Chưa có đủ tài nguyên nhận diện được phê duyệt. Hãy nhờ quản trị viên kiểm tra.")


def bo_nho(ham):
    """Cache từ vựng được xóa cả khi cấu hình thay đổi hoặc bị thu hồi."""
    ham = lru_cache(maxsize=None)(ham)
    _cac_cache.append(ham.cache_clear)
    return ham


def xoa_cache():
    for xoa in _cac_cache:
        xoa()


def nap_cau_hinh(cau_hinh):
    """Nạp snapshot whitelist {tai_nguyen: {tên: {duong_dan, sha256}}}.

    Đường tuyệt đối ngoài gói và SHA do lead cấp, không suy ra từ tên tệp.
    Kiểm toàn bộ trước khi công bố snapshot; cấu hình lỗi thu hồi bản cũ.
    Không lưu nội dung văn bản công việc hay tự tải nguồn nào.
    """
    global _du_lieu
    _du_lieu = {}
    xoa_cache()
    try:
        if not isinstance(cau_hinh, dict) or set(cau_hinh) != {"tai_nguyen"}:
            raise ValueError
        whitelist = cau_hinh["tai_nguyen"]
        if not isinstance(whitelist, dict) or set(whitelist) != TEN_TAI_NGUYEN:
            raise ValueError
        moi = {}
        goi = Path(__file__).resolve().parents[1]
        for ten, muc in whitelist.items():
            if not isinstance(muc, dict) or set(muc) != {"duong_dan", "sha256"}:
                raise ValueError
            if (not isinstance(muc["duong_dan"], str)
                    or not isinstance(muc["sha256"], str)
                    or not re.fullmatch(r"[0-9a-f]{64}", muc["sha256"])):
                raise ValueError
            duong = Path(muc["duong_dan"])
            if not duong.is_absolute() or duong.is_symlink():
                raise ValueError
            duong = duong.resolve(strict=True)
            if duong.is_relative_to(goi) or not duong.is_file():
                raise ValueError
            noi_dung = duong.read_bytes()
            if sha256(noi_dung).hexdigest() != muc["sha256"]:
                raise ValueError
            dong = tuple(s.strip() for s in noi_dung.decode("utf-8-sig").splitlines()
                         if s.strip() and not s.lstrip().startswith("#"))
            if not dong:
                raise ValueError
            moi[ten] = dong
        _du_lieu = moi
    except (OSError, ValueError, TypeError, RuntimeError):
        raise ThieuTaiNguyen() from None


def doc_dong(ten):
    if ten not in TEN_TAI_NGUYEN or ten not in _du_lieu:
        raise ThieuTaiNguyen()
    return _du_lieu[ten]
