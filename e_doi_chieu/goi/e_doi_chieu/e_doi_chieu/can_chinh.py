"""Căn Điều/Khoản/câu và bảng/dòng/ô; mọi khoảng đều được giữ.

Neo theo lần xuất hiện + LIS để văn bản lặp không làm phép so bậc hai.
Không suy tọa độ hoặc phân trang Word từ số dòng/đoạn.
"""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import re
import unicodedata

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .ho_so import bam
from .vi_tri import loi


def khong_can():
    raise LoiNghiepVu("DC_KHONG_CAN_DUOC", "Chưa căn được cấu trúc hai bản. Anh kiểm tra bản chuẩn và bản nhận dạng.")


@dataclass
class Nut:
    loai: str
    a: int
    b: int
    nhan: str = ""
    con: list = field(default_factory=list)
    du_lieu: object = None


class BanDo:
    """Tra biên Unicode bằng chỉ mục; không quét lại toàn bộ map cho mỗi điểm."""
    def __init__(self, ch):
        self.ch = ch
        self.runs = ch["anh_xa"]
        self.chuan = [x[0] for x in self.runs]
        self.goc_cuoi = [x[3] for x in self.runs]

    def ve_chuan(self, moc):
        if moc >= len(self.ch["nguyen_van"]):
            return len(self.ch["van_ban"])
        # Một ký tự nguồn có thể sinh hai ký tự NFC, kể cả khi run đầu
        # đã gộp với tiền tố 1:1. Chọn run đầu phủ nguồn, không run cuối.
        i = bisect_right(self.goc_cuoi, moc)
        if i == len(self.runs):
            return len(self.ch["van_ban"])
        x, y, a, b = self.runs[i]
        if moc < a:
            return x
        return x + moc - a if y - x == b - a else x

    def ve_goc(self, moc):
        if moc == 0:
            return 0
        if moc == len(self.ch["van_ban"]):
            return len(self.ch["nguyen_van"])
        i = bisect_right(self.chuan, moc) - 1
        x, y, a, b = self.runs[i]
        return a + moc - x if y - x == b - a else a

    def bien_an_toan(self, moc):
        if moc in (0, len(self.ch["van_ban"])):
            return True
        def lat(i):
            x, y, a, b = self.runs[bisect_right(self.chuan, i) - 1]
            return (a + i - x, a + i - x + 1) if y - x == b - a else (a, b)
        # Hai ký tự chuẩn hóa dùng chung nguồn thì không được tách điểm.
        return lat(moc - 1)[1] <= lat(moc)[0]


def khop_thu_tu(trai, phai, kiem):
    """Ghép từng lần xuất hiện, giữ chuỗi neo không giao nhau O(n log n)."""
    def danh_so(ds):
        dem, out = Counter(), []
        for i, x in enumerate(ds):
            if i % 256 == 0:
                kiem()
            out.append((x, dem[x]))
            dem[x] += 1
        return out
    a, b = danh_so(trai), danh_so(phai)
    chi_muc = {k: j for j, k in enumerate(b)}
    ung_vien = [(i, chi_muc[k]) for i, k in enumerate(a) if k in chi_muc]
    duoi, nut_duoi, truoc = [], [], []
    for at, (_, j) in enumerate(ung_vien):
        if at % 256 == 0:
            kiem()
        p = bisect_left(duoi, j)
        truoc.append(nut_duoi[p - 1] if p else -1)
        if p == len(duoi):
            duoi.append(j)
            nut_duoi.append(at)
        else:
            duoi[p], nut_duoi[p] = j, at
    out = []
    at = nut_duoi[-1] if nut_duoi else -1
    while at >= 0:
        out.append(ung_vien[at])
        at = truoc[at]
    return out[::-1]


def _luoi(k, kiem):
    """Tuần tự hóa đúng quy ước DC-2, kể cả ô trống và chỗ ô gộp phủ."""
    cells = {}
    if type(k.get("o")) is not list or len(k["o"]) > 50000:
        loi("DC_QUA_GIOI_HAN")
    hang = cot = 0
    phu = set()
    for o in k["o"]:
        kiem()
        if (any(type(o.get(x)) is not int for x in ("hang", "cot", "gop_hang", "gop_cot")) or
                o["hang"] < 0 or o["cot"] < 0 or o["gop_hang"] < 1 or o["gop_cot"] < 1 or
                type(o.get("van_ban")) is not str):
            khong_can()
        h, c = o["hang"], o["cot"]
        if h + o["gop_hang"] > 50000 or c + o["gop_cot"] > 256:
            loi("DC_QUA_GIOI_HAN")
        if len(phu) + o["gop_hang"] * o["gop_cot"] > 50000:
            loi("DC_QUA_GIOI_HAN")
        for r in range(h, h + o["gop_hang"]):
            kiem()
            for s in range(c, c + o["gop_cot"]):
                if (r, s) in phu:
                    khong_can()
                phu.add((r, s))
        if len(phu) > 50000:
            loi("DC_QUA_GIOI_HAN")
        cells[h, c] = o
        hang, cot = max(hang, h + o["gop_hang"]), max(cot, c + o["gop_cot"])
    for key, dem in (("so_hang", hang), ("so_cot", cot)):
        if key in k and (type(k[key]) is not int or k[key] < dem):
            khong_can()
    hang, cot = k.get("so_hang", hang), k.get("so_cot", cot)
    if hang * cot > 50000 or cot > 256:
        loi("DC_QUA_GIOI_HAN")
    if not hang or not cot:
        khong_can()
    rows, offsets, pos = [], [], 0
    for h in range(hang):
        kiem()
        chu, os = [], []
        for c in range(cot):
            o = cells.get((h, c))
            text = o["van_ban"] if o else ""
            os.append((pos, pos + len(text), o))
            chu.append(text)
            pos += len(text) + (3 if c < cot - 1 else 0)
        rows.append(" | ".join(chu))
        offsets.append(os)
        pos += 1
    return "\n".join(rows), offsets, (hang, cot, sorted(
        (h, c, o["gop_hang"], o["gop_cot"]) for (h, c), o in cells.items()))


def dung_cay(v, ch, kiem):
    """Đọc cấu trúc nguồn đã ghim; bảng OCR mơ hồ thì từ chối căn."""
    text, goc = ch["van_ban"], ch["nguyen_van"]
    bd, tables, nested, ngoai = BanDo(ch), [], defaultdict(list), []

    def them_bang(k, a, b, parent=None):
        chu, rows, shape = _luoi(k, kiem)
        if chu != goc[a:b]:
            khong_can()
        t = (a, b, rows, shape)
        tables.append(t)
        (ngoai if parent is None else nested[id(parent)]).append(t)
        return t

    def docx(ds, parent=None):
        if type(ds) is not list:
            khong_can()
        for k in ds:
            kiem()
            if k["loai"] == "bang":
                t = them_bang(k, k["bat_dau"], k["ket_thuc"], parent)
                for o in k["o"]:
                    docx(o["khoi"], t)
    if v["nguon_doc"] == "docx":
        docx(v["khoi_docx"])
    else:
        def ocr(ds, dau, cuoi, parent=None, sau=0):
            if type(ds) is not list:
                khong_can()
            if sau > 16:
                loi("DC_QUA_GIOI_HAN")
            for k in ds:
                kiem()
                if k["loai"] != "bang":
                    continue
                serialized, rows, _ = _luoi(k, kiem)
                if "bat_dau" in k or "ket_thuc" in k:
                    a, b = k.get("bat_dau"), k.get("ket_thuc")
                    if type(a) is not int or type(b) is not int or not dau <= a <= b <= cuoi or goc[a:b] != serialized:
                        khong_can()
                else:
                    a = goc.find(serialized, dau, cuoi)
                    if a < 0 or goc.find(serialized, a + 1, cuoi) >= 0:
                        khong_can()
                    b = a + len(serialized)
                t = them_bang(k, a, b, parent)
                for row in rows:
                    for oa, ob, o in row:
                        if o is not None and "khoi" in o:
                            ocr(o["khoi"], a + oa, a + ob, t, sau + 1)
        pos = 0
        pages = goc.split("\f")
        for page, chu in zip(v["trang"], pages):
            ocr(page["khoi"], pos, pos + len(chu))
            pos += len(chu) + 1
    # Chỉ cần tìm vùng bảng ngoài cùng khi loại nhãn Điều/Khoản trong ô.
    for ds in (ngoai, *nested.values()):
        ds.sort(key=lambda x: (x[0], -x[1]))
        if any(x[1] > y[0] for x, y in zip(ds, ds[1:])):
            khong_can()
    dau_bang = [t[0] for t in ngoai]

    def trong_bang(a):
        i = bisect_right(dau_bang, a) - 1
        return i >= 0 and a < ngoai[i][1]

    nhan, pos = [[], []], 0
    mau_nhan = re.compile(r"[ \t]*(?:(?P<dieu>Điều)[ \t]+(?P<so>[0-9]{1,7})\b|"
                          r"Khoản[ \t]+(?P<co_ten>[0-9]{1,7}(?:\.[0-9]{1,7})*)\b[.)]?[ \t]+|"
                          r"(?P<khoan>[0-9]{1,7}(?:\.[0-9]{1,7})*)[.)][ \t]+)", re.IGNORECASE)
    for line in goc.splitlines(keepends=True):
        kiem()
        m = mau_nhan.match(unicodedata.normalize("NFC", line))
        # Nhãn có thể ở dạng NFD; đầu dòng nguồn vẫn là biên Unicode thật.
        a = pos + len(line) - len(line.lstrip(" \t"))
        if m and not trong_bang(a):
            nhan[0 if m["dieu"] else 1].append((bd.ve_chuan(a), m["so"] or m["co_ten"] or m["khoan"]))
        pos += len(line)
    moc_nhan = [[x for x, _ in ds] for ds in nhan]

    def cau(a, b):
        ds, dau = [], a
        for m in re.finditer(r"[.!?;](?=\s)|[\n\f]", text[a:b]):
            kiem()
            cuoi = a + m.end()
            ds.append(Nut("cau", dau, cuoi))
            dau = cuoi
        if dau < b or not ds:
            ds.append(Nut("cau", dau, b))
        return ds

    def bang(t):
        a, b, rows, shape = t
        ds = []
        for h, row in enumerate(rows):
            kiem()
            ra = bd.ve_chuan(a + row[0][0])
            rb = bd.ve_chuan(a + rows[h + 1][0][0]) if h + 1 < len(rows) else bd.ve_chuan(b)
            os = []
            for c, (oa, ob, o) in enumerate(row):
                x = bd.ve_chuan(a + oa)
                y = bd.ve_chuan(a + row[c + 1][0]) if c + 1 < len(row) else rb
                child = [bang(u) for u in nested[id(t)] if a + oa <= u[0] and u[1] <= a + ob]
                os.append(Nut("o", x, y, str(c), voi_bang(x, y, child),
                              None if o is None else {k: o[k] for k in ("hang", "cot", "gop_hang", "gop_cot")}))
            ds.append(Nut("dong", ra, rb, con=os))
        return Nut("bang", bd.ve_chuan(a), bd.ve_chuan(b), con=ds, du_lieu=shape)

    def voi_bang(a, b, ds_bang):
        ds, pos = [], a
        for t in ds_bang:
            if t.a < pos or t.b > b:
                khong_can()
            if t.a > pos:
                ds.extend(cau(pos, t.a))
            ds.append(t)
            pos = t.b
        if pos < b or not ds:
            ds.extend(cau(pos, b))
        return ds

    bang_ngoai = [bang(t) for t in ngoai]
    moc_bang = [t.a for t in bang_ngoai]
    def noi_dung(a, b):
        cuoi = bisect_right(moc_bang, b) if b == len(text) else bisect_left(moc_bang, b)
        return voi_bang(a, b, bang_ngoai[bisect_left(moc_bang, a):cuoi])

    def muc(a, b, cap):
        if cap == 2:
            return noi_dung(a, b)
        ds, pos = [], a
        events = nhan[cap][bisect_left(moc_nhan[cap], a):bisect_left(moc_nhan[cap], b)]
        for i, (x, n) in enumerate(events):
            if x < pos:
                khong_can()
            if x > pos:
                ds.extend(muc(pos, x, cap + 1))
            y = events[i + 1][0] if i + 1 < len(events) else b
            ds.append(Nut("dieu" if cap == 0 else "khoan", x, y, n, muc(x, y, cap + 1)))
            pos = y
        if pos < b or not ds:
            ds.extend(muc(pos, b, cap + 1))
        return ds

    root = Nut("tai_lieu", 0, len(text), con=muc(0, len(text), 0))
    return root, bd


def can_chinh(trai, phai, a, b, so_doan, kiem, them_cau_truc):
    """Gọi so_doan cho mọi khoảng, kể cả đuôi không có neo."""
    def key(n, text):
        if n.loai in ("dieu", "khoan", "o"):
            return n.loai, n.nhan
        return n.loai, bam(text[n.a:n.b].encode("utf-8"))

    def kiem_nhan(xs, ys, loai):
        x = [n for n in xs if n.loai == loai]
        y = [n for n in ys if n.loai == loai]
        groups = defaultdict(list)
        for n in y:
            groups[n.nhan].append(n)
        dem, pairs = Counter(), []
        for n in x:
            kiem()
            j = dem[n.nhan]
            dem[n.nhan] += 1
            if j < len(groups[n.nhan]):
                pairs.append((n, groups[n.nhan][j]))
            else:
                them_cau_truc("xoa", n, None, "thieu_" + loai)
        for nhan, ds in groups.items():
            for n in ds[dem[nhan]:]:
                them_cau_truc("chen", None, n, "thua_" + loai)
        jxs = [p[1].a for p in pairs]
        # Mỗi phần tử tham gia nghịch thế đều được ghi; không chỉ phần bị LIS bỏ.
        left, right = [], []
        cur = -1
        for j in jxs:
            left.append(cur)
            cur = max(cur, j)
        cur = len(b) + 1
        for j in jxs[::-1]:
            right.append(cur)
            cur = min(cur, j)
        for (n, m), l, r in zip(pairs, left, right[::-1]):
            if m.a < l or m.a > r:
                them_cau_truc("dao", n, m, "dao_" + loai)
        return pairs

    def kiem_outline(n, m):
        kiem()
        for loai in ("dieu", "khoan"):
            for x, y in kiem_nhan(n.con, m.con, loai):
                # Kiểm cả Khoản trong Điều bị đảo, dù script chữ phải giữ
                # thứ tự trái/phải và không thể dùng neo giao nhau đó.
                kiem_outline(x, y)

    def cap(n, m, duong):
        kiem()
        if n.loai == m.loai == "bang" and n.du_lieu != m.du_lieu:
            them_cau_truc("thay", n, m, "doi_cau_truc_bang")
        if not n.con or not m.con:
            so_doan(n.a, n.b, m.a, m.b, duong)
            return
        xs, ys = n.con, m.con
        anchors = khop_thu_tu([key(x, a) for x in xs], [key(y, b) for y in ys], kiem)
        ix = iy = 0

        def khoang(xe, ye):
            nonlocal ix, iy
            xx, yy = xs[ix:xe], ys[iy:ye]
            tx, ty = [x for x in xx if x.loai == "bang"], [y for y in yy if y.loai == "bang"]
            if tx and ty:
                # Khác biên câu/ngắt dòng không được làm mất neo bảng
                # đã kiểm nguyên văn/offset ở hai nguồn.
                x0 = xx[0].a
                y0 = yy[0].a
                for x, y in zip(tx, ty):
                    so_doan(x0, x.a, y0, y.a, duong + ["khoang_truoc_bang"])
                    cap(x, y, duong + ["bang"])
                    x0, y0 = x.b, y.b
                so_doan(x0, xx[-1].b, y0, yy[-1].b, duong + ["khoang_sau_bang"])
                for x in tx[len(ty):]:
                    them_cau_truc("xoa", x, None, "thieu_bang")
                for y in ty[len(tx):]:
                    them_cau_truc("chen", None, y, "thua_bang")
            elif len(xx) == len(yy) and all(x.loai == y.loai and x.loai not in ("dieu", "khoan") for x, y in zip(xx, yy)):
                for x, y in zip(xx, yy):
                    cap(x, y, duong + [x.loai])
            elif xx or yy:
                for x in xx:
                    if x.loai == "bang":
                        them_cau_truc("xoa", x, None, "thieu_bang")
                for y in yy:
                    if y.loai == "bang":
                        them_cau_truc("chen", None, y, "thua_bang")
                x0 = xx[0].a if xx else (xs[ix].a if ix < len(xs) else n.b)
                y0 = yy[0].a if yy else (ys[iy].a if iy < len(ys) else m.b)
                so_doan(x0, xx[-1].b if xx else x0, y0, yy[-1].b if yy else y0,
                         duong + ["khoang_khong_ghep"])
            ix, iy = xe, ye
        for x, y in anchors:
            khoang(x, y)
            cap(xs[x], ys[y], duong + [xs[x].loai])
            ix, iy = x + 1, y + 1
        khoang(len(xs), len(ys))
    kiem_outline(trai, phai)
    cap(trai, phai, ["tai_lieu"])


def kiem_trang(snapshot, kiem, phan_trang_core=None):
    """Chỉ chứng minh thứ tự bằng định danh ảnh trang khớp chính xác.

    PDF render + số trang tự khai chưa là ánh xạ Word→trang đáng tin.
    Ảnh khác/khác dàn trang: chưa kiểm, không suy thiếu/thừa trang.
    """
    a = snapshot.get("anh_trang_word", [])
    b = snapshot["anh_trang"]
    out = {"trang_thai": "chua_kiem", "so_trang_word": len(a) if a else None,
           "so_trang_ban_ky": len(b), "diem": [],
           "ly_do": "Chưa đủ bằng chứng ghép trang vật lý với bản chuẩn đã phân trang."}
    if snapshot["ban_chuan_phan_trang"] is None or not a:
        return out
    # Tham chiếu PDF/ảnh trong JSON không tự chứng minh đó là render của
    # Word này. Chỉ nhận liên kết do Core cấp trong ngữ cảnh tin cậy;
    # trường cùng tên trong snapshot/caller không được dùng làm bằng chứng.
    if phan_trang_core is None:
        return out
    mong_doi = {"phien_ban": 1, "bam_word": snapshot["nguon"]["word"]["bam"].lower(),
                "phien_ban_word": snapshot["nguon"]["word"]["phien_ban"],
                "bam_pdf_chuan": snapshot["ban_chuan_phan_trang"]["bam"].lower(),
                "bam_ban_ky": snapshot["nguon"]["ban_ky"]["bam"].lower(),
                "anh_word": [p["bam"].lower() for p in a], "anh_ban_ky": [p["bam"].lower() for p in b]}
    if type(phan_trang_core) is not dict or type(phan_trang_core.get("phien_ban")) is not int or phan_trang_core != mong_doi:
        loi()
    out["bang_chung_core"] = mong_doi
    aa, bb = [p["bam"].lower() for p in a], [p["bam"].lower() for p in b]
    if Counter(aa) != Counter(bb):
        return out
    out.update(trang_thai="dat", ly_do="Đã ghép toàn bộ trang bằng băm ảnh trùng bản chuẩn phân trang đã ghim.")
    if aa != bb:
        indices, seen = defaultdict(list), Counter()
        for j, k in enumerate(bb):
            indices[k].append(j)
        for i, k in enumerate(aa):
            kiem()
            j = indices[k][seen[k]]
            seen[k] += 1
            if i != j:
                out["diem"].append({"phep": "dao", "word": a[i], "ban_ky": b[j],
                                    "can_cu": "dao_trang_anh_trung_bam"})
        out["trang_thai"] = "khong_dat"
    return out
