from dataclasses import dataclass, field
import re
import unicodedata


class PrivacyError(ValueError):
    """Lỗi nội bộ; cổng chỉ được trả câu LoiNghiepVu cố định, không dùng str(lỗi)."""


@dataclass
class Extracted:
    text: str
    warnings: list[str] = field(default_factory=list)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", bo_ky_tu_vo_hinh(text))
    return "".join(c for c in text if c in "\n\t" or not unicodedata.category(c).startswith("C"))


def la_ky_tu_vo_hinh(c: str) -> bool:
    """Mọi Cf và variation selector, kể cả các selector ngoài BMP."""
    so = ord(c)
    return (unicodedata.category(c) == "Cf" or 0xFE00 <= so <= 0xFE0F
            or 0xE0100 <= so <= 0xE01EF or 0x180B <= so <= 0x180D or so == 0x180F)


# Lập tập theo bảng Unicode của Python một lần, sau đó quét bằng regex C.
# Không duy trì danh sách Cf thủ công nên không bỏ sót Cf ngoài các ví dụ.
_VO_HINH = re.compile('[' + re.escape(''.join(chr(i) for i in range(0x110000)
                                           if la_ky_tu_vo_hinh(chr(i)))) + ']')


def bo_ky_tu_vo_hinh(text: str) -> str:
    return text if text.isascii() else _VO_HINH.sub('', text)


def chuan_hoa_vi_tri(van_ban: str):
    """Bỏ ký tự vô hình rồi dò NFC; mỗi ký tự giữ khoảng trong nguyên văn.

    Khoảng bao trùm cả ký tự vô hình nằm giữa chữ/dấu tổ hợp. Không ánh xạ
    được thì từ chối, không dùng tọa độ gần đúng để phát hành văn bản.
    """
    if van_ban.isascii():
        return van_ban, None
    co_an = _VO_HINH.search(van_ban) is not None
    if not co_an and unicodedata.is_normalized("NFC", van_ban):
        return van_ban, None
    goc = [(i, i + 1) for i, c in enumerate(van_ban) if not la_ky_tu_vo_hinh(c)] if co_an else None
    chu = "".join(van_ban[a] for a, _ in goc) if co_an else van_ban
    if unicodedata.is_normalized("NFC", chu):
        return chu, goc
    phan, vi_tri, dau = [], [], 0
    for cuoi in range(1, len(chu) + 1):
        if cuoi < len(chu) and unicodedata.combining(chu[cuoi]):
            continue
        cum = unicodedata.normalize("NFC", chu[dau:cuoi])
        phan.append(cum)
        khoang = (goc[dau][0], goc[cuoi - 1][1]) if goc is not None else (dau, cuoi)
        vi_tri.extend([khoang] * len(cum))
        dau = cuoi
    ban_do = "".join(phan)
    if ban_do != unicodedata.normalize("NFC", chu):
        raise PrivacyError("Không thể xác định vị trí ký tự an toàn.") from None
    return ban_do, vi_tri
