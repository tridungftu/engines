"""Chuẩn hóa theo bộ ghim; map Unicode về nguyên văn, không bỏ dấu."""
from bisect import bisect_right
import re
import unicodedata

from .vi_tri import lap_vi_tri, loi

_NHAY = str.maketrans({"‘": "'", "’": "'", "‚": "'", "“": '"', "”": '"', "„": '"'})
_GACH = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-"})


def kiem_bo(bo, phien_ban, cau_hinh):
    if (type(bo) is not dict or type(bo.get("phien_ban")) is not int or bo["phien_ban"] != 1 or
            bo.get("phien_ban_bo") != phien_ban or bo.get("ma_bo_chuan_hoa") != cau_hinh["ma_bo_chuan_hoa"]):
        loi()
    q = bo.get("chuan_hoa")
    lua_chon = {"unicode": ("NFC",), "khoang_trang": ("gop", "giu_nguyen"),
                "dau_nhay": ("thang", "giu_nguyen"), "gach_noi": ("thong_nhat", "giu_nguyen"),
                "ngat_dong": ("noi_trong_doan", "giu_nguyen"),
                "ngat_tu_cuoi_dong": ("chi_gach_noi_mem", "giu_nguyen")}
    if type(q) is not dict or set(q) != set(lua_chon) | {"dau_chan_trang", "bo_so_trang"}:
        loi()
    if any(type(q[k]) is not str or q[k] not in v for k, v in lua_chon.items()):
        loi()
    if (type(q["bo_so_trang"]) is not bool or type(q["dau_chan_trang"]) is not list or
            len(q["dau_chan_trang"]) > 100 or any(type(x) is not str or not 1 <= len(x) <= 1000 for x in q["dau_chan_trang"])):
        loi()
    return q


def _vung_bo(v, vi_tri, q, kiem_huy=lambda: None):
    bo = []
    duoc_bo = set(q["dau_chan_trang"])
    phan_phu, trang_theo_chu = set(), {}
    for x in v.get("vung_docx", []):
        kiem_huy()
        if x["loai"] in ("hdr", "ftr"):
            phan_phu.add(x["phan"])

    def o_le(p):
        trang = p.get("so_trang")
        if not trang or "hop" not in p:
            return False
        h = v["trang"][trang - 1]["cao"]
        return p["hop"][3] <= h * 0.08 or p["hop"][1] >= h * 0.92

    # Lập một lần, đếm trang phân biệt: nhiều nút cùng trang không đủ căn cứ.
    for p in vi_tri:
        kiem_huy()
        if o_le(p):
            text = v["van_ban"][p["bat_dau"]:p["ket_thuc"]]
            if text in duoc_bo:
                trang_theo_chu.setdefault(text, set()).add(p["so_trang"])
    # Chỉ chuỗi whitelist đã ghim; không suy từ việc lặp hoặc tên file header.
    for p in vi_tri:
        kiem_huy()
        a, b = p["bat_dau"], p["ket_thuc"]
        text = v["van_ban"][a:b]
        trang = p.get("so_trang")
        phu_word = p.get("phan") in phan_phu
        le = o_le(p)
        if not phu_word and not le:
            continue
        # Số trang cần số trang vật lý thật và nguyên dòng có nhãn rõ.
        m = re.fullmatch(r"\s*Trang\s+([0-9]+)(?:\s*/\s*([0-9]+))?\s*", text, re.IGNORECASE)
        so_trang = bool(q["bo_so_trang"] and le and m and int(m[1]) == trang and
                       (m[2] is None or int(m[2]) == v["so_trang"]))
        nhay_cam = bool(re.search(r"\d|\b(?:VND|USD|EUR|đồng|hợp\s+đồng|MST|STK)\b", text, re.IGNORECASE))
        duyet = text in duoc_bo and not nhay_cam
        if duyet and le:
            # OCR cần lặp nguyên dòng trong vùng lề ở ít nhất hai trang thực.
            duyet = len(trang_theo_chu[text]) >= 2
        if (so_trang or duyet) and b > a:
            bo.append({"bat_dau": a, "ket_thuc": b, "ly_do": "so_trang_da_xac_minh" if so_trang else "dau_chan_trang_da_duyet",
                       "duong_dan": p["duong_dan"]})
    # Khối và dòng/từ có thể cùng phủ một khoảng: chỉ bỏ mỗi ký tự một lần.
    ket_qua = []
    for x in sorted(bo, key=lambda k: (k["bat_dau"], -k["ket_thuc"])):
        kiem_huy()
        if not ket_qua or x["bat_dau"] >= ket_qua[-1]["ket_thuc"]:
            ket_qua.append(x)
    return ket_qua


def chuan_hoa(v, q, kiem_huy=lambda: None):
    """Map nửa mở bốn số; các run 1:1 được nén, đoạn thay đổi giữ cả lát gốc."""
    goc = v["van_ban"]
    vi_tri, bien, chua_neo = lap_vi_tri(v, kiem_huy)
    bo = _vung_bo(v, vi_tri, q, kiem_huy)
    cac_bien = sorted(bien)
    # Token là (chữ sau NFC, đầu gốc, cuối gốc); NFC xử lý cả Hangul Jamo.
    def nfc():
        a, cum, i_bo = 0, [], 0
        for i, c in enumerate(goc):
            if i % 1024 == 0:
                kiem_huy()
            while i_bo < len(bo) and bo[i_bo]["ket_thuc"] <= i:
                i_bo += 1
            if i_bo < len(bo) and bo[i_bo]["bat_dau"] <= i < bo[i_bo]["ket_thuc"]:
                if cum:
                    yield from phat("".join(cum), a)
                    cum = []
                continue
            if cum and unicodedata.combining(c) == 0:
                # Starter thường kết thúc cụm; Jamo có thể còn ghép với nhau.
                text = "".join(cum)
                if unicodedata.normalize("NFC", text + c) == unicodedata.normalize("NFC", text) + unicodedata.normalize("NFC", c):
                    yield from phat(text, a)
                    cum = []
            if not cum:
                a = i
            cum.append(c)
        if cum:
            yield from phat("".join(cum), a)

    def phat(cum, a):
        moi = unicodedata.normalize("NFC", cum)
        if moi == cum:
            for j, c in enumerate(moi):
                yield c, a + j, a + j + 1
        else:
            for c in moi:
                yield c, a, a + len(cum)

    tokens = iter(nfc())
    chu, anh_xa, moc = [], [], 0

    def ghi(c, a, b):
        nonlocal moc
        if q["dau_nhay"] == "thang":
            c = c.translate(_NHAY)
        if q["gach_noi"] == "thong_nhat":
            c = c.translate(_GACH)
        chu.append(c)
        # Chỉ gộp run tịnh tiến 1:1, không gộp vùng co/giãn có map khác.
        if (anh_xa and len(c) == b - a and anh_xa[-1][1] - anh_xa[-1][0] == anh_xa[-1][3] - anh_xa[-1][2]
                and anh_xa[-1][1] == moc and anh_xa[-1][3] == a):
            anh_xa[-1][1], anh_xa[-1][3] = moc + len(c), b
        else:
            anh_xa.append([moc, moc + len(c), a, b])
        moc += len(c)

    cho = next(tokens, None)
    while cho is not None:
        c, a, b = cho
        cho = next(tokens, None)
        if (c == "\u00ad" and q["ngat_tu_cuoi_dong"] == "chi_gach_noi_mem" and
                cho and cho[1] == b and cho[0] in ("\r", "\n")):
            # Chỉ soft hyphen thực, không xóa '-' hoặc nối mã/số hợp đồng.
            cuoi = b
            while cho and cho[1] == cuoi and cho[0] in ("\r", "\n", " ", "\t"):
                cuoi = cho[2]
                cho = next(tokens, None)
            idx = bisect_right(cac_bien, a)
            if (chu and chu[-1][-1:].isalpha() and anh_xa[-1][3] == a and
                    cho and cho[1] == cuoi and cho[0].isalpha() and
                    (idx == len(cac_bien) or cac_bien[idx] >= cuoi)):
                bo.append({"bat_dau": a, "ket_thuc": cuoi, "ly_do": "ngat_tu_mem_trong_doan"})
                continue
            ghi(c, a, b)
            ghi("\n", b, cuoi)
            continue
        if c.isspace():
            cuoi, nhom = b, c
            while cho and cho[0].isspace() and cho[1] == cuoi:
                nhom += cho[0]
                cuoi = cho[2]
                cho = next(tokens, None)
            idx = bisect_right(cac_bien, a)
            tach = idx < len(cac_bien) and cac_bien[idx] <= cuoi or a in bien or cuoi in bien
            if q["khoang_trang"] == "giu_nguyen" and q["ngat_dong"] == "giu_nguyen":
                ghi(nhom, a, cuoi)
            elif "\f" in nhom:
                ghi("\f", a, cuoi)
            elif "\n" in nhom or "\r" in nhom:
                ghi("\n" if tach or q["ngat_dong"] == "giu_nguyen" else " ", a, cuoi)
            else:
                ghi(" " if q["khoang_trang"] == "gop" else nhom, a, cuoi)
        else:
            ghi(c, a, b)
    return {"don_vi_offset": "unicode_code_point", "nguyen_van": goc, "van_ban": "".join(chu),
            "anh_xa": anh_xa, "vi_tri": vi_tri, "da_bo": sorted(bo, key=lambda x: x["bat_dau"]),
            "chua_neo_cau_truc": chua_neo}
