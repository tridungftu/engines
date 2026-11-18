"""Tách tham chiếu và mẫu công thức; chuyển nguyên thuật toán nguồn đã ghim."""

import difflib
import re
from openpyxl.utils import column_index_from_string
from .chuan_hoa import bo_dau

LOI = ("#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?", "#NUM!", "#NULL!")
# tham chiếu có tên sheet (kể cả file ngoài [n]) và tham chiếu trong sheet
QREF = re.compile(r"(?:'((?:[^']|'')+)'|((?:\[\d+\])?[^\s'!(),;:+\-*/^&=<>{}\"]+))!"
                  r"(\$?)([A-Z]{1,3})(\$?)(\d+)(?::(\$?)([A-Z]{1,3})(\$?)(\d+))?")
LREF = re.compile(r"(?<![A-Za-z0-9_.!'\]$])(\$?)([A-Z]{1,3})(\$?)(\d+)(?::(\$?)([A-Z]{1,3})(\$?)(\d+))?(?![\w(!])")
CHUOI = re.compile(r'"(?:[^"]|"")*"')
SO_NHUNG = re.compile(r"(?<![\w.$\[])(\d+(?:\.\d+)?%?)(?![\w.\[])")

MUC = {"Cao": 1, "Trung bình": 2, "Kiểm soát": 3}


def bo_chuoi(f):
    return CHUOI.sub('""', f)


def tach_tham_chieu(f, sh_hien):
    """-> list dict(sh, c1, r1, c2, r2, ngoai, abs flags)."""
    out = []
    body = bo_chuoi(f)
    for m in QREF.finditer(body):
        sh = (m.group(1) or "").replace("''", "'") or m.group(2)
        ngoai = None
        mm = re.match(r"\[(\d+)\](.*)", sh)
        if mm:
            ngoai, sh = int(mm.group(1)), mm.group(2)
        out.append(dict(sh=sh, c1=column_index_from_string(m.group(4)), r1=int(m.group(6)),
                        c2=column_index_from_string(m.group(8) or m.group(4)), r2=int(m.group(10) or m.group(6)), ngoai=ngoai))
    body = QREF.sub(" ", body)
    for m in LREF.finditer(body):
        out.append(dict(sh=sh_hien, c1=column_index_from_string(m.group(2)), r1=int(m.group(4)),
                        c2=column_index_from_string(m.group(6) or m.group(2)), r2=int(m.group(8) or m.group(4)), ngoai=None))
    return out


def mau_cong_thuc(f, r, c):
    """Chuẩn hoá công thức về dạng tương đối (kiểu R1C1) để so 'cùng mẫu' giữa các dòng."""
    body = bo_chuoi(f)

    def tok(col_abs, col, row_abs, row):
        cc = column_index_from_string(col)
        rr = int(row)
        return (f"C{cc}" if col_abs else f"C[{cc - c}]") + (f"R{rr}" if row_abs else f"R[{rr - r}]")

    def q(m):
        s = tok(m.group(3), m.group(4), m.group(5), m.group(6))
        if m.group(8):
            s += ":" + tok(m.group(7), m.group(8), m.group(9), m.group(10))
        return f"<{m.group(1) or m.group(2)}>!" + s

    body = QREF.sub(q, body)

    def l(m):
        s = tok(m.group(1), m.group(2), m.group(3), m.group(4))
        if m.group(6):
            s += ":" + tok(m.group(5), m.group(6), m.group(7), m.group(8))
        return s

    return LREF.sub(l, body).replace(" ", "")


def la_tong(f):
    return bool(re.match(r"^=\s*(SUM|SUBTOTAL|SUMIF|SUMPRODUCT)\(", f, re.I))


def hang_so_nhung(f):
    """Hằng số đứng cạnh phép nhân / chia trong công thức (bỏ tham chiếu, chuỗi, đối số làm tròn)."""
    body = bo_chuoi(f)
    body = QREF.sub("X", body)
    body = LREF.sub("X", body)
    body = re.sub(r",\s*-?\d+\s*\)", ")", body)            # ROUND(x,0), INDEX(..,2)
    out = []
    for m in SO_NHUNG.finditer(body):
        a, b = body[:m.start()].rstrip()[-1:], body[m.end():].lstrip()[:1]
        if a in ("*", "/") or b in ("*", "/"):
            s = m.group(1)
            if s not in ("1", "0", "100", "1000"):
                out.append(s)
    return out


def la_so(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def la_cong_thuc(v):
    return isinstance(v, str) and v.startswith("=")


def giong(a, b):
    a, b = bo_dau(a), bo_dau(b)
    if not a or not b:
        return None
    if a == b or a in b or b in a:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


