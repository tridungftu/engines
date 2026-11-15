from dataclasses import dataclass, field
import unicodedata


class PrivacyError(ValueError):
    """Lỗi nội bộ; cổng chỉ được trả câu LoiNghiepVu cố định, không dùng str(lỗi)."""


@dataclass
class Extracted:
    text: str
    warnings: list[str] = field(default_factory=list)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return "".join(c for c in text if c in "\n\t" or not unicodedata.category(c).startswith("C"))


def chuan_hoa_vi_tri(van_ban: str):
    """Bản dò NFC và khoảng ký tự gốc; None khi vị trí không đổi.

    Không sửa khoảng trắng/ký tự điều khiển của văn bản trả về.
    """
    if unicodedata.is_normalized("NFC", van_ban):
        return van_ban, None
    phan, vi_tri, dau = [], [], 0
    for cuoi in range(1, len(van_ban) + 1):
        if cuoi < len(van_ban) and unicodedata.combining(van_ban[cuoi]):
            continue
        cum = unicodedata.normalize("NFC", van_ban[dau:cuoi])
        phan.append(cum)
        vi_tri.extend([(dau, cuoi)] * len(cum))
        dau = cuoi
    return "".join(phan), vi_tri
