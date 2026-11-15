# -*- coding: utf-8 -*-
"""
kiem_tra.py — Python tự kiểm kết quả AI (bước 5) và so đáp án.
  - Trích dẫn phải có NGUYÊN VĂN trong HĐ (khớp gần đúng nếu chỉ khác dấu câu/khoảng trắng).
  - Mọi số trong giá trị phải nằm trong trích dẫn (trừ giá trị "Suy ra").
  - Điều/Khoản do PYTHON suy lại từ trích dẫn (không tin nhãn AI ghi).
  - Giá trị ≥ 8 ký tự có chữ và có nguyên văn trong HĐ → "OK (giá trị có nguyên văn trong HĐ)".
"""
import re
import unicodedata
from decimal import Decimal, InvalidOperation


KHONG_CO = ("không quy định", "không tìm thấy")


def norm(s):
    """Chuẩn hoá để so nguyên văn: Unicode NFC (chữ tổ hợp = chữ dựng sẵn), ngoặc kép thẳng, gộp khoảng trắng, chữ thường."""
    s = unicodedata.normalize("NFC", s or "")
    return re.sub(r"\s+", " ", s.replace("“", '"').replace("”", '"').replace("’", "'")).strip().lower()


def loose(s):
    """Bỏ mọi dấu câu/khoảng trắng (giữ chữ có dấu và số) — để so trích dẫn gần đúng."""
    return re.sub(r"[\W_]+", "", norm(s))


def so_chuan(tok):
    """7.915.563.292 = 7,915,563,292 → '7915563292'; 0,15 = 0.15 → '0.15'."""
    t = tok.strip(".,")
    seps = [c for c in t if c in ".,"]
    if len(set(seps)) == 2:
        dec = t[max(t.rfind("."), t.rfind(","))]
        t = t.replace("," if dec == "." else ".", "").replace(dec, ".")
    elif len(seps) > 1:
        t = t.replace(seps[0], "")
    elif len(seps) == 1:
        a, b = re.split(r"[.,]", t)
        t = a + b if (len(b) == 3 and 1 <= len(a) <= 3 and not a.startswith("0")) else a + "." + b
    try:
        return format(Decimal(t).normalize(), "f")
    except InvalidOperation:
        return tok


def cac_so(s):
    return {so_chuan(n) for n in re.findall(r"\d[\d\.,]*\d|\d", s or "")}


def la_khong_co(v):
    return (v or "").strip().lower().startswith(KHONG_CO)


def la_khong_ap_dung(v):
    return (v or "").strip().lower().startswith(("không áp dụng", "khong ap dung"))


def khop_dieu_khoan(dk, sent_rows):
    """dieu_khoan có trỏ tới ít nhất một đoạn đã gửi không."""
    if not sent_rows:
        return True
    for part in re.split(r"[;,]|\bvà\b", (dk or "").lower()):
        part = part.strip()
        if not part:
            continue
        khoans = re.findall(r"\d+(?:\.\d+)+", part)
        dieus = [int(x) for x in re.findall(r"điều\s*(\d+)", part)]
        doans = [int(x) for x in re.findall(r"đoạn\s*(\d+)", part)]
        for r in sent_rows:
            if r.get("doan"):
                if r["doan"] in doans or (r["doan"] == 1 and not (khoans or dieus or doans)):
                    return True
                continue
            d, k = int(r["dieu"]), r["khoan"]
            if khoans:
                if any(int(x.split(".")[0]) == d and (not k or x == k or x.startswith(k + ".") or k.startswith(x + "."))
                       for x in khoans):
                    return True
            elif dieus:
                if d in dieus:
                    return True
            elif d == 0:
                return True
    return False


def gia_tri_nguyen_van(v, full_norm):
    """Giá trị ≥ 8 ký tự, có chữ cái, có nguyên văn trong HĐ (không tính 'Không quy định/áp dụng')."""
    n = norm(v)
    return (len(n) >= 8 and re.search(r"[^\W\d_]", n) is not None and not la_khong_co(v) and not la_khong_ap_dung(v)
            and n in full_norm)


def check_legacy(item, full_norm, full_loose=None, sent_rows=None):
    """Tự kiểm 1 kết quả → chuỗi bắt đầu bằng 'OK' (xanh) hoặc 'KIỂM TRA: …' / 'THIẾU …' (vàng)."""
    q = item.get("trich_dan", "") or ""
    v = item.get("gia_tri", "") or ""
    if not v:
        return "THIẾU giá trị"
    if la_khong_co(v):
        return "KIỂM TRA: AI báo HĐ không quy định"
    if full_loose is None:
        full_loose = loose(full_norm)
    parts = [p for p in re.split(r"\.\.\.|…", q) if p.strip()]
    if parts and all(norm(p) in full_norm for p in parts):
        khop = "OK"
    elif parts and all(loose(p) and loose(p) in full_loose for p in parts):
        khop = "OK (khớp gần đúng)"
    else:
        khop = None
    suy_ra = "suy ra" in (item.get("ghi_chu") or "").lower()
    if not q:
        kq = "KIỂM TRA: giá trị suy ra" if suy_ra else "KIỂM TRA: thiếu trích dẫn"
    elif not khop:
        kq = "KIỂM TRA: trích dẫn không khớp nguyên văn"
    elif not suy_ra and not cac_so(v) <= cac_so(q):
        kq = "KIỂM TRA: số liệu không có trong trích dẫn"
    elif not khop_dieu_khoan(item.get("dieu_khoan", ""), sent_rows):
        kq = "KIỂM TRA: điều khoản không thuộc các đoạn đã gửi"
    else:
        return khop
    if gia_tri_nguyen_van(v, full_norm):
        return "OK (giá trị có nguyên văn trong HĐ)"
    return kq


def la_ok(ck):
    return str(ck or "").startswith("OK")



def bo_dau(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def trich_dan_dung(q, van_ban):
    """Kiểm từng câu bằng offset Python, không chuẩn hóa hoặc tin cờ AI."""
    return (isinstance(q, dict) and isinstance(q.get("cau"), str)
            and type(q.get("bat_dau")) is int and type(q.get("ket_thuc")) is int
            and 0 <= q["bat_dau"] < q["ket_thuc"] <= len(van_ban)
            and van_ban[q["bat_dau"]:q["ket_thuc"]] == q["cau"])


def co_nguyen_van(gia_tri, dan_chung):
    """Giá trị phải nguyên văn trong câu đã kiểm, không khớp 10 với 100."""
    if not isinstance(gia_tri, str) or not gia_tri.strip():
        return False
    dau = r"(?<!\w)" if gia_tri[0].isalnum() else ""
    cuoi = r"(?!\w)" if gia_tri[-1].isalnum() else ""
    return any(re.search(dau + re.escape(gia_tri) + cuoi, q["cau"]) for q in dan_chung)


def dinh_vi(q, tai_lieu, cau_truc):
    """Chỉ ánh xạ vị trí có căn cứ; không đoán hộp từ câu lặp."""
    nhan = next((r["nhan"] for r in cau_truc
                 if r["bat_dau"] <= q["bat_dau"] < r["ket_thuc"]), "Phần mở đầu")
    if tai_lieu["nguon_doc"] == "docx":
        return {"loai": "doan", "nhan": nhan, "so_trang": None, "hop": None}
    cac_trang = tai_lieu["van_ban"].split("\f")
    dau = 0
    for i, text in enumerate(cac_trang):
        cuoi = dau + len(text)
        if dau <= q["bat_dau"] < q["ket_thuc"] <= cuoi and i < len(tai_lieu["trang"]):
            trang = tai_lieu["trang"][i]
            khoi = trang["khoi"]
            chu = [k.get("van_ban", "\n".join(o["van_ban"] for o in k.get("o", [])))
                   for k in khoi]
            hop = None
            if "\n".join(chu) == text:
                moc = dau
                for k, t in zip(khoi, chu):
                    if moc <= q["bat_dau"] < q["ket_thuc"] <= moc + len(t):
                        hop = k.get("hop")
                        break
                    moc += len(t) + 1
            return {"loai": "trang", "nhan": nhan, "so_trang": trang["so"], "hop": hop}
        dau = cuoi + 1
    return {"loai": "doan", "nhan": nhan, "so_trang": None, "hop": None}



def dan_chung_da_kiem(dung, tai_lieu, cau_truc):
    """Tách câu qua trang/khối OCR theo offset thật; giữ câu AI gốc riêng."""
    if tai_lieu["nguon_doc"] == "docx":
        cac_doan = [(q["bat_dau"], q["ket_thuc"]) for q in dung]
    else:
        cac_vung, moc = [], 0
        for text, trang in zip(tai_lieu["van_ban"].split("\f"), tai_lieu["trang"]):
            chu = [k.get("van_ban", "\n".join(o["van_ban"] for o in k.get("o", [])))
                   for k in trang["khoi"]]
            if "\n".join(chu) == text:
                dau = moc
                for t in chu:
                    if t:
                        cac_vung.append((dau, dau + len(t)))
                    dau += len(t) + 1
            elif text:
                cac_vung.append((moc, moc + len(text)))
            moc += len(text) + 1
        cac_doan = [(max(a, q["bat_dau"]), min(b, q["ket_thuc"]))
                    for q in dung for a, b in cac_vung
                    if max(a, q["bat_dau"]) < min(b, q["ket_thuc"])]
    out = []
    for a, b in cac_doan:
        q = {"cau": tai_lieu["van_ban"][a:b], "bat_dau": a, "ket_thuc": b}
        out.append({**q, "vi_tri": dinh_vi(q, tai_lieu, cau_truc)})
    return out

def kiem_o(item, tai_lieu, cau_truc, *, bo_sot=False):
    """Ô sai về null/cần soát; dấu legacy chỉ để E6 đối chiếu."""
    ly_do = ["AI bỏ sót mã cần trích."] if bo_sot else []
    q_ai = item["trich_dan"]
    dung = [q for q in q_ai if trich_dan_dung(q, tai_lieu["van_ban"])]
    if len(dung) != len(q_ai):
        ly_do.append("Trích dẫn không khớp nguyên văn hoặc chỉ số Unicode.")
    v = item["gia_tri"]
    if not bo_sot and (v is None or not v.strip()):
        ly_do.append("AI không tìm thấy giá trị có căn cứ.")
    elif not bo_sot and not q_ai:
        ly_do.append("Giá trị chưa có trích dẫn để đối chiếu.")
    elif not bo_sot and not co_nguyen_van(v, dung):
        ly_do.append("Giá trị không có nguyên văn trong trích dẫn đã kiểm.")
    if "suy ra" in norm(item["ghi_chu"]) or "suy ra" in norm(v):
        ly_do.append("Giá trị suy ra chưa có quy tắc được duyệt.")
    legacy = check_legacy({"gia_tri": v, "ghi_chu": item["ghi_chu"],
                           "trich_dan": "\n".join(q.get("cau", "") for q in q_ai
                            if isinstance(q, dict) and isinstance(q.get("cau"), str))},
                          norm(tai_lieu["van_ban"]))
    return {"gia_tri": None if ly_do else v, "ly_do": ly_do,
            "dan_chung": dan_chung_da_kiem(dung, tai_lieu, cau_truc),
            "kiem_tra_legacy": legacy}
