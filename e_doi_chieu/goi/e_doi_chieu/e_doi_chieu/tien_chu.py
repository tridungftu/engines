"""Phân tích tiền hữu hạn, chỉ dùng quy ước/đơn vị đã khai; không sửa OCR."""
from datetime import datetime
from decimal import Decimal, InvalidOperation, localcontext
import re
import unicodedata


def chuan_chu(chu):
    return " ".join(unicodedata.normalize("NFC", chu).casefold().split())


def doc_so(chu, dinh_dang=()):
    """None khi mơ hồ. Không có quy ước chỉ nhận số nguyên không phân cách.

    Kết quả là Decimal; caller giữ nguyên chuỗi mã/số 0 đầu riêng biệt.
    Nhiều quy ước cùng đọc ra các giá trị khác nhau cũng là mơ hồ.
    """
    if type(chu) is not str or not 1 <= len(chu) <= 200:
        return None
    chu = chu.replace("\u00a0", " ").strip()
    ket_qua = set()
    for q in dinh_dang or ({"nghin": None, "thap_phan": None},):
        nghin, tp = q["nghin"], q["thap_phan"]
        so = r"[0-9]+"
        if nghin:
            so = r"(?:[0-9]+|[0-9]{1,3}(?:" + re.escape(nghin) + r"[0-9]{3})+)"
        if tp:
            so += r"(?:" + re.escape(tp) + r"[0-9]+)?"
        if not re.fullmatch(r"[+-]?" + so, chu):
            continue
        text = chu.replace(nghin, "") if nghin else chu
        if tp:
            text = text.replace(tp, ".")
        try:
            with localcontext() as ctx:
                ctx.prec = 220
                ket_qua.add(Decimal(text))
        except InvalidOperation:
            continue
    return next(iter(ket_qua)) if len(ket_qua) == 1 else None


def so_json(so):
    """Số nguyên hoặc chuỗi thập phân chính xác trong JSON snapshot, không float."""
    return int(so) if so == so.to_integral_value() else format(so, "f")


def doc_ngay(chu, dinh_dang=("YYYY-MM-DD",)):
    mau = {"YYYY-MM-DD": (r"[0-9]{4}-[0-9]{2}-[0-9]{2}", "%Y-%m-%d"),
           "DD/MM/YYYY": (r"[0-9]{2}/[0-9]{2}/[0-9]{4}", "%d/%m/%Y"),
           "MM/DD/YYYY": (r"[0-9]{2}/[0-9]{2}/[0-9]{4}", "%m/%d/%Y")}
    ds = set()
    for ten in dinh_dang:
        pat, fmt = mau[ten]
        if re.fullmatch(pat, chu):
            try:
                ds.add(datetime.strptime(chu, fmt).date().isoformat())
            except ValueError:
                pass
    return next(iter(ds)) if len(ds) == 1 else None


_DON = {"không": 0, "một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5,
        "sáu": 6, "bảy": 7, "tám": 8, "chín": 9}
_HANG = {"tỷ": 9, "tỉ": 9, "triệu": 6, "nghìn": 3, "ngàn": 3}


def _tram(tu):
    if not tu:
        return None
    kq = 0
    co_tram = len(tu) >= 2 and tu[0] in _DON and tu[1] == "trăm"
    if co_tram:
        kq, tu = _DON[tu[0]] * 100, tu[2:]
        if not tu:
            return kq
        if tu[0] in ("linh", "lẻ"):
            return kq + _DON[tu[1]] if len(tu) == 2 and tu[1] in _DON and _DON[tu[1]] > 0 else None
    if len(tu) == 1:
        # Sau hàng trăm phải đọc rõ linh/lẻ hoặc hàng chục.
        return (10 if tu[0] == "mười" else _DON.get(tu[0])) if not co_tram else (kq + 10 if tu[0] == "mười" else None)
    if tu[0] == "mười":
        chuc, du = 1, tu[1:]
    elif len(tu) >= 2 and tu[0] in _DON and _DON[tu[0]] >= 2 and tu[1] == "mươi":
        chuc, du = _DON[tu[0]], tu[2:]
    else:
        return None
    if not du:
        return kq + chuc * 10
    if len(du) != 1:
        return None
    don = du[0]
    if don == "lăm":
        n = 5
    elif don in ("mốt", "tư") and chuc >= 2:
        n = {"mốt": 1, "tư": 4}[don]
    elif don in _DON and _DON[don] > 0 and don != "năm":
        n = _DON[don]
    else:
        return None
    return kq + chuc * 10 + n


def doc_chu_so(chu):
    """Ngữ pháp tiếng Việt từ 0 tới dưới 10^12; ngoài phạm vi trả None.

    Không đoán cụm thiếu (triệu đồng), thứ tự sai, viết tắt hoặc chữ OCR sai.
    """
    tu = chuan_chu(chu).split()
    if not tu or len(tu) > 100:
        return None
    if tu[-1] == "chẵn":
        tu = tu[:-1]
    tong, nhom, truoc = 0, [], 12
    for t in tu:
        if t not in _HANG:
            nhom.append(t)
            continue
        bac = _HANG[t]
        n = _tram(nhom)
        if n is None or n == 0 or bac >= truoc:
            return None
        tong += n * 10 ** bac
        nhom, truoc = [], bac
    if nhom:
        n = _tram(nhom)
        if n is None:
            return None
        tong += n
    elif not tong:
        return None
    return tong


def doc_tien_chu(chu, don_vi):
    """Chỉ nhận khi toàn bộ cụm và đơn vị đã được khai, không suy từ ký hiệu $."""
    text = chuan_chu(chu).strip(" .;\t\r\n")
    if text.endswith(" chẵn"):
        text = text[:-5].rstrip()
    ds = []
    for ten, ma in don_vi.items():
        ten = chuan_chu(ten)
        if text.endswith(" " + ten):
            n = doc_chu_so(text[:-len(ten)].strip())
            if n is not None:
                ds.append({"so": n, "tien_te": ma})
    return ds[0] if ds and all(x == ds[0] for x in ds) else None


def doc_tien_so(chu, don_vi, dinh_dang):
    text = chuan_chu(chu).strip(" .;\t\r\n")
    ds = []
    for ten, ma in don_vi.items():
        ten = chuan_chu(ten)
        if text.endswith(ten):
            so = doc_so(text[:-len(ten)].strip(), dinh_dang)
            if so is not None:
                ds.append({"so": so_json(so), "tien_te": ma})
    return ds[0] if ds and all(x == ds[0] for x in ds) else None
