"""Chuẩn hóa chữ và số, chuyển từ master_hd.py dòng 43–72."""

from decimal import Decimal, InvalidOperation
import re
import unicodedata


def nfc(s):
    return unicodedata.normalize("NFC", str(s or ""))


def bo_dau(s):
    s = nfc(s).replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", s.lower()).strip()


def so(txt):
    """Giữ quy tắc dấu phân cách của nguồn; tính bằng Decimal."""
    t = str(txt).strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        return Decimal(t.replace(".", ""))
    return Decimal(t.replace(".", "").replace(",", ".")) if "," in t else Decimal(t)


def num(v):
    if v is None or v == "":
        return None
    try:
        d = Decimal(str(v) if isinstance(v, (int, float, Decimal)) else str(v).replace(",", ""))
        return d if d.is_finite() else None
    except InvalidOperation:
        return None


def so_tien(v, tien_te):
    """Giá trị trường SDK: chưa rõ tiền tệ thì cả trường là null."""
    if not tien_te:
        return None
    if not re.fullmatch(r"[A-Z]{3}", tien_te):
        from kho_tri_thuc_sdk.engine import LoiNghiepVu
        raise LoiNghiepVu("THAM_SO_KHONG_HOP_LE", "Mã tiền tệ phải gồm ba chữ in hoa.")
    d = num(v)
    return {"so": format(d, "f"), "tien_te": tien_te} if d is not None else None
