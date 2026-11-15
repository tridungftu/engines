"""So có dấu, gắn nhóm bỏ dấu; script phủ kín nguyên văn và bản chuẩn hóa."""
from bisect import bisect_right
from copy import deepcopy
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import time
import unicodedata
import uuid

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ho_so as hs
from .can_chinh import can_chinh, dung_cay, khong_can, khop_thu_tu, kiem_trang
from .chuan_hoa import chuan_hoa, kiem_bo
from .ngan import NganXungDot
from .vi_tri import loi

_SCHEMA_CH = json.loads((Path(__file__).resolve().parent.parent / "cau_hinh.schema.json").read_text(encoding="utf-8"))
# Snapshot đã điền mặc định ở DC-3; bộ kiểm hồ sơ không nhận từ khóa default.
_SCHEMA_CH["properties"] = {k: {x: y for x, y in s.items() if x != "default"}
                            for k, s in _SCHEMA_CH["properties"].items()}
_TRAN = {"so_trang_toi_da": 60, "ky_tu_moi_tai_lieu": 500000, "ky_tu_hai_tai_lieu": 1000000,
         "diem_lech_toi_da": 10000, "ho_so_mib": 20, "tep_mib": 20, "pixel_anh": 20000000,
         "tong_byte_tep_con": 128 * hs.MIB, "docx_giai_nen_mib": 100, "docx_so_muc": 2000}


class _ViecCoHan:
    def __init__(self, viec, thoi_han):
        self.viec, self.han = viec, time.perf_counter() + min(thoi_han, 300)

    def __getattr__(self, ten):
        return getattr(self.viec, ten)

    def kiem_huy(self):
        self.viec.kiem_huy()
        if time.perf_counter() >= self.han:
            loi("DC_QUA_GIOI_HAN")


def bo_dau(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
                   if unicodedata.category(c) != "Mn")


def _so_lat(a, b, a0, a1, b0, b1, ghi, kiem, can_cu):
    """Neo từ có thứ tự; so ký tự trong cụm nhỏ, giữ cả cụm lớn chưa có neo.

    Không dùng autojunk và không chạy SequenceMatcher trên chuỗi lớn/lặp.
    Phép thay bảo thủ vẫn giữ toàn bộ nội dung, chưa quyết định mức.
    """
    x, y = a0, b0
    while x + 1024 <= a1 and y + 1024 <= b1 and a[x:x + 1024] == b[y:y + 1024]:
        kiem()
        x, y = x + 1024, y + 1024
    while x < a1 and y < b1 and a[x] == b[y]:
        x, y = x + 1, y + 1
    if x > a0:
        ghi("giu", a0, x, b0, y, can_cu)
    ae, be = a1, b1
    while ae - 1024 >= x and be - 1024 >= y and a[ae - 1024:ae] == b[be - 1024:be]:
        kiem()
        ae, be = ae - 1024, be - 1024
    while ae > x and be > y and a[ae - 1] == b[be - 1]:
        ae, be = ae - 1, be - 1

    def cum(i, j, k, l):
        kiem()
        if i == j and k == l:
            return
        if i == j or k == l:
            ghi("chen" if i == j else "xoa", i, j, k, l, can_cu)
        elif (j - i) * (l - k) <= 65536:
            for op, xa, xb, ya, yb in SequenceMatcher(None, a[i:j], b[k:l], autojunk=False).get_opcodes():
                kiem()
                ghi({"equal": "giu", "replace": "thay", "insert": "chen", "delete": "xoa"}[op],
                    i + xa, i + xb, k + ya, k + yb, can_cu)
        else:
            ghi("thay", i, j, k, l, can_cu + ["giu_toan_cum_khong_co_neo"])

    if x < ae and y < be and (ae - x) * (be - y) > 65536:
        xx = [(m.group(), x + m.start(), x + m.end()) for m in re.finditer(r"\w+|\W", a[x:ae])]
        yy = [(m.group(), y + m.start(), y + m.end()) for m in re.finditer(r"\w+|\W", b[y:be])]
        anchors = khop_thu_tu([v[0] for v in xx], [v[0] for v in yy], kiem)
        i, j = x, y
        for ix, iy in anchors:
            kiem()
            _, xa, xb = xx[ix]
            _, ya, yb = yy[iy]
            cum(i, xa, j, ya)
            ghi("giu", xa, xb, ya, yb, can_cu)
            i, j = xb, yb
        cum(i, ae, j, be)
    else:
        cum(x, ae, y, be)
    if ae < a1:
        ghi("giu", ae, a1, be, b1, can_cu)


class _ViTri:
    """Cây khoảng: chỉ chọn nút nguồn thực bao trọn lát, không đoán hộp."""
    def __init__(self, ds, kiem):
        self.kiem = kiem
        ds = [p for p in ds if p["loai"] != "tai_lieu" and p["bat_dau"] < p["ket_thuc"]]
        self.cay = self._dung(ds)

    def _dung(self, ds):
        self.kiem()
        if not ds:
            return None
        center = sorted((p["bat_dau"] + p["ket_thuc"]) // 2 for p in ds)[len(ds) // 2]
        trai, phai, giua = [], [], []
        for p in ds:
            if p["ket_thuc"] <= center:
                trai.append(p)
            elif p["bat_dau"] > center:
                phai.append(p)
            else:
                giua.append(p)
        return center, sorted(giua, key=lambda p: p["bat_dau"]), sorted(giua, key=lambda p: -p["ket_thuc"]), self._dung(trai), self._dung(phai)

    def lay(self, a, b):
        if a == b:
            return None
        ds, node = [], self.cay
        while node:
            c, dau, cuoi, trai, phai = node
            if b <= c:
                for p in dau:
                    if p["bat_dau"] > a:
                        break
                    ds.append(p)
                node = trai
            elif a > c:
                for p in cuoi:
                    if p["ket_thuc"] < b:
                        break
                    ds.append(p)
                node = phai
            else:
                ds.extend(p for p in dau if p["bat_dau"] <= a and b <= p["ket_thuc"])
                break
        ds = [p for p in ds if p["bat_dau"] <= a and b <= p["ket_thuc"]]
        if not ds:
            return None
        p = min(ds, key=lambda p: (p["ket_thuc"] - p["bat_dau"], -len(p["duong_dan"])))
        return {"so_trang": p.get("so_trang"), "hop": deepcopy(p.get("hop")),
                **{k: deepcopy(v) for k, v in p.items() if k not in ("bat_dau", "ket_thuc", "so_trang", "hop")}}


def so_hai_ban(snapshot, kiem, toi_da_diem, *, phan_trang_core=None):
    ch = snapshot["chuan_hoa"]
    a, b = [ch[k]["van_ban"] for k in ("word", "ban_ky")]
    if len(a) > 500000 or len(b) > 500000 or len(a) + len(b) > 1000000:
        loi("DC_QUA_GIOI_HAN")
    trees, maps, vt = {}, {}, {}
    for ben in ("word", "ban_ky"):
        kiem()
        trees[ben], maps[ben] = dung_cay(snapshot["van_ban"][ben]["van_ban_tai_lieu"], ch[ben], kiem)
        vt[ben] = _ViTri(ch[ben]["vi_tri"], kiem)
    # Không nhận hai văn bản không còn một neo chữ/cấu trúc để ghép.
    if not set(re.findall(r"\w{2,}", a)) & set(re.findall(r"\w{2,}", b)) and a != b:
        khong_can()
    ops, issues = [], []

    def ghi(phep, a0, a1, b0, b1, can_cu):
        if a0 == a1 and b0 == b1:
            return
        if (ops and ops[-1][0] == phep == "giu" and ops[-1][2] == a0 and ops[-1][4] == b0):
            ops[-1][2], ops[-1][4] = a1, b1
            ops[-1][5] = ["tai_lieu", "so_co_dau"]
        else:
            ops.append([phep, a0, a1, b0, b1, list(can_cu)])

    def them_ct(phep, n, m, can_cu):
        kiem()
        issues.append((phep, n, m, can_cu))
        if len(issues) > toi_da_diem:
            loi("DC_QUA_GIOI_HAN")

    can_chinh(trees["word"], trees["ban_ky"], a, b,
              lambda a0, a1, b0, b1, cc: _so_lat(a, b, a0, a1, b0, b1, ghi, kiem, cc), kiem, them_ct)
    if ch["word"]["nguyen_van"] == ch["ban_ky"]["nguyen_van"]:
        # Cùng nguyên văn nhưng nguồn OCR có thể thiếu biên đoạn/ô mà
        # DOCX đã có: chuẩn hóa hai bên khi đó khác ngắt dòng. Cấu trúc
        # vẫn đã kiểm ở trên; không tạo khác biệt chữ từ biên dẫn xuất.
        ops = [["giu", 0, len(a), 0, len(b), ["nguyen_van_trung_nhau"]]]
    # Không cắt giữa một cụm NFC co/giãn. Hợp cả thao tác kề biên đó;
    # phép thay mở rộng vẫn chứa toàn bộ cụm nguồn, không lặp offset.
    gop = []
    for op in ops:
        kiem()
        if gop and (not maps["word"].bien_an_toan(op[1]) or not maps["ban_ky"].bien_an_toan(op[3])):
            cu = gop[-1]
            cu[0] = "giu" if cu[0] == op[0] == "giu" else "thay"
            cu[2], cu[4] = op[2], op[4]
            cu[5] = ["tai_lieu", "cum_unicode_khong_tach"]
        else:
            gop.append(op)
    script, points = [], []
    pin = {"nguon": {k: {"bam": v["bam"].lower(), "phien_ban": v["phien_ban"]} for k, v in snapshot["nguon"].items()},
           "bam_bo": snapshot["bo_quy_tac"]["bam"].lower(), "thuat_toan": "DC-4-1",
           "bam_chuan": [hs.bam(x.encode("utf-8")) for x in (a, b)]}

    def ben(k, x, y):
        ga, gb = maps[k].ve_goc(x), maps[k].ve_goc(y)
        return {"nguyen_van": ch[k]["nguyen_van"][ga:gb], "bat_dau": ga, "ket_thuc": gb,
                "chuan_hoa": {"bat_dau": x, "ket_thuc": y, "van_ban": ch[k]["van_ban"][x:y]},
                "vi_tri": vt[k].lay(ga, gb)}

    def them_diem(phep, word, ky, can_cu, nhom="khac_biet_chu", **phu):
        kiem()
        if len(points) >= toi_da_diem:
            loi("DC_QUA_GIOI_HAN")
        data = {"phep": phep, "word": word, "ban_ky": ky, "can_cu": can_cu, "nhom": nhom}
        ma = "DC-" + hs.bam(hs.json_bytes({"pin": pin, **data}))[7:]
        points.append({"ma_diem": ma, **data, "muc_san": None, "muc": None, "cho_phan_loai": True,
                       "quy_tac_trung": [], "vung_bao_ve": [], **phu})
        return ma

    for op, a0, a1, b0, b1, cc in gop:
        kiem()
        word, ky = ben("word", a0, a1), ben("ban_ky", b0, b1)
        p = op
        if word["nguyen_van"] == ky["nguyen_van"]:
            p = "giu"
        elif a[a0:a1] == b[b0:b1]:
            p = "tuong_duong_chuan_hoa"
        ma = None
        if p not in ("giu", "tuong_duong_chuan_hoa"):
            nhom = "chi_lech_dau" if bo_dau(a[a0:a1]) == bo_dau(b[b0:b1]) else "khac_biet_chu"
            ma = them_diem(p, word, ky, {"phuong_phap": "so_co_dau", "cap_can": cc}, nhom)
        script.append({"phep": p, "word": word, "ban_ky": ky, "ma_diem": ma,
                       "can_cu": {"phuong_phap": "so_co_dau", "cap_can": cc}})
    moc_trai, moc_phai = [op[1] for op in gop], [op[3] for op in gop]
    for phep, n, m, cc in issues:
        if n is None:
            op = gop[max(0, bisect_right(moc_phai, m.a) - 1)]
            word = ben("word", op[1], op[1])
        else:
            word = ben("word", n.a, n.b)
        if m is None:
            op = gop[max(0, bisect_right(moc_trai, n.a) - 1)]
            ky = ben("ban_ky", op[3], op[3])
        else:
            ky = ben("ban_ky", m.a, m.b)
        them_diem(phep, word, ky, {"phuong_phap": cc,
                   "word": None if n is None else {"loai": n.loai, "nhan": n.nhan, "cau_truc": n.du_lieu},
                   "ban_ky": None if m is None else {"loai": m.loai, "nhan": m.nhan, "cau_truc": m.du_lieu}}, "cau_truc")
    trang = kiem_trang(snapshot, kiem, phan_trang_core)
    for d in trang["diem"]:
        # Không có chữ/offset Word của ảnh render: null, giữ bằng chứng ảnh
        # thật và số trang vật lý trong căn cứ, không bịa đoạn Word.
        them_diem(d["phep"], None, None, {"phuong_phap": d["can_cu"],
                   "word": deepcopy(d["word"]), "ban_ky": deepcopy(d["ban_ky"])}, "trang")
    kiem_tai_dung(script, ch, kiem)
    if len({p["ma_diem"] for p in points}) != len(points):
        khong_can()
    return script, points, {k: v for k, v in trang.items() if k != "diem"}


def kiem_tai_dung(script, ch, kiem=lambda: None):
    """Kiểm cả lát nguồn và lát chuẩn hóa, liên tục từ 0 tới hết hai bản."""
    for k in ("word", "ban_ky"):
        g = c = 0
        raw, normalized = [], []
        for step in script:
            kiem()
            p = step[k]
            q = p["chuan_hoa"]
            if (p["bat_dau"] != g or q["bat_dau"] != c or p["ket_thuc"] < g or q["ket_thuc"] < c or
                    ch[k]["nguyen_van"][g:p["ket_thuc"]] != p["nguyen_van"] or
                    ch[k]["van_ban"][c:q["ket_thuc"]] != q["van_ban"]):
                khong_can()
            raw.append(p["nguyen_van"])
            normalized.append(q["van_ban"])
            g, c = p["ket_thuc"], q["ket_thuc"]
        if "".join(raw) != ch[k]["nguyen_van"] or "".join(normalized) != ch[k]["van_ban"]:
            khong_can()


def _doc_ho_so(viec, cau_hinh):
    dv = viec.dau_vao
    p = dv.get("ho_so_doi_chieu") if type(dv) is dict else None
    tep = p.get("ho_so") if type(p) is dict else None
    if type(tep) is dict and type(tep.get("kich_thuoc")) is int and tep["kich_thuoc"] > min(20, cau_hinh["ho_so_mib"]) * hs.MIB:
        loi("DC_QUA_GIOI_HAN")
    hs.kiem_schema(viec.dau_vao, hs._SCHEMA_HS)
    if len(hs.json_bytes(viec.dau_vao)) > 65536:
        loi("DC_QUA_GIOI_HAN")
    p = viec.dau_vao["ho_so_doi_chieu"]
    if p["giai_doan"] != "da_nhan":
        loi("DC_SAI_DAU_VAO")
    doc = hs._DocTep(viec, cau_hinh)
    raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, cau_hinh["ho_so_mib"] * hs.MIB)
    s = hs.doc_json(raw, viec.kiem_huy)
    if hs._phong_bi(s, p["ho_so"], raw) != viec.dau_vao:
        loi()
    hs.kiem_schema(s["cau_hinh"], _SCHEMA_CH)
    if (s["edit_script"] is not None or s["diem_lech"] is not None or s["ket_luan"] is not None or
            s["da_kiem_du"] or not s["de_nghi_chan"] or any(v is not None for v in s["tom_tat"].values()) or
            s["kiem_tra"] != {k: "dat" if k == "doc_hai_ban" else "chua_kiem" for k in hs._KIEM} or
            any(k not in s["cau_hinh"] for k in _TRAN)):
        loi()
    effective = deepcopy(s["cau_hinh"])
    for k, tr in _TRAN.items():
        effective[k] = min(effective[k], cau_hinh[k], tr)
    doc.cau_hinh = effective
    if len(raw) > effective["ho_so_mib"] * hs.MIB or len(raw) > effective["tong_byte_tep_con"]:
        loi("DC_QUA_GIOI_HAN")
    keys = ("phien_ban", "ma_cap", "nguon", "anh_trang", "ban_chuan_phan_trang", "kiem_dau_vao")
    cap = {k: deepcopy(s[k]) for k in keys}
    cap.update(van_ban=s["tham_chieu_van_ban"], bo_quy_tac={k: s["bo_quy_tac"][k] for k in ("tep", "bam", "phien_ban")},
               bang_chung_ocr_lai=[{k: r[k] for k in ("tep", "bam")} for r in s["bang_chung_ocr_lai"]])
    if "anh_trang_word" in s:
        cap["anh_trang_word"] = s["anh_trang_word"]
    hs._kiem_cap(cap, effective)
    bo_raw = doc.doc(cap["bo_quy_tac"], 65536)
    bo = hs.doc_json(bo_raw, viec.kiem_huy)
    param = viec.tham_so.get("bo_quy_tac_json")
    if type(param) is not str or len(param) > 65536 or len(param.encode("utf-8")) > 65536:
        loi("DC_QUA_GIOI_HAN")
    if (hs.bam(param.encode("utf-8")) != hs._bam(viec.tham_so.get("bam_bo_quy_tac")) or
            hs.bam(bo_raw) != hs._bam(p["bam_bo_quy_tac"]) or hs.bam(param.encode("utf-8")) != hs.bam(bo_raw) or
            bo != s["bo_quy_tac"]["noi_dung"]):
        loi()
    q = kiem_bo(bo, cap["bo_quy_tac"]["phien_ban"], s["cau_hinh"])
    vb, anh = hs._doc_hai_ban(cap, doc, effective, s["phien_ban_engine"])
    if vb != s["van_ban"] or anh != s["kiem_anh"]:
        loi()
    for k, v in vb.items():
        viec.kiem_huy()
        if chuan_hoa(v["van_ban_tai_lieu"], q, viec.kiem_huy) != s["chuan_hoa"][k]:
            loi()
    if (any(len(c["van_ban"]) > effective["ky_tu_moi_tai_lieu"] for c in s["chuan_hoa"].values()) or
            sum(len(c["van_ban"]) for c in s["chuan_hoa"].values()) > effective["ky_tu_hai_tai_lieu"]):
        loi("DC_QUA_GIOI_HAN")
    for ref in s["bang_chung_ocr_lai"]:
        if hs.doc_json(doc.doc(ref, effective["ho_so_mib"] * hs.MIB), viec.kiem_huy) != ref["noi_dung"]:
            loi()
    return s, doc, effective


def _lay_so_cu(doc, ban, truoc):
    pb = hs._lay_cu(doc, ban)
    p = pb["ho_so_doi_chieu"]
    raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, doc.cau_hinh["ho_so_mib"] * hs.MIB)
    s = hs.doc_json(raw, doc.viec.kiem_huy)
    if (s.get("giai_doan") != "da_so" or s.get("thuat_toan_so") != "DC-4-1" or
            s.get("ho_so_truoc", {}).get("bam") != doc.viec.dau_vao["ho_so_doi_chieu"]["bam_ho_so"] or
            any(s.get(k) != truoc[k] for k in ("nguon", "van_ban", "chuan_hoa", "bo_quy_tac")) or
            s["tom_tat"]["so_diem"] != len(s["diem_lech"]) or
            len(s["diem_lech"]) > doc.cau_hinh["diem_lech_toi_da"] or
            s["ket_luan"] is not None or s["da_kiem_du"] or not s["de_nghi_chan"]):
        loi()
    # Quyền tới snapshot tiền nhiệm vẫn bắt buộc khi tái dùng hồ sơ đã so.
    doc.doc(s["ho_so_truoc"], doc.cau_hinh["ho_so_mib"] * hs.MIB)
    kiem_tai_dung(s["edit_script"], s["chuan_hoa"], doc.viec.kiem_huy)
    return pb


def so_van_ban(viec, ngan, cau_hinh, *, phien_ban_engine, thoi_han_viec_giay):
    viec = _ViecCoHan(viec, thoi_han_viec_giay)
    viec.kiem_huy()
    viec.tien_do(5, "Đang kiểm hồ sơ và nguồn đã ghim")
    s, doc, cau_hinh = _doc_ho_so(viec, cau_hinh)
    phap_nhan = viec.ngu_canh.get("phap_nhan_id")
    if type(phap_nhan) is not str or not phap_nhan.strip():
        loi("DC_THIEU_NGUON")
    pin = viec.dau_vao["ho_so_doi_chieu"]
    phan_trang_core = viec.ngu_canh.get("doi_chieu_phan_trang")
    if phan_trang_core is not None and len(hs.json_bytes(phan_trang_core)) > 16384:
        loi("DC_QUA_GIOI_HAN")
    khoa = {"phap_nhan_id": phap_nhan, "bam_cap": hs.bam(hs.json_bytes({
        "buoc": "so_van_ban@1", "bam_ho_so_nhan": pin["bam_ho_so"], "gioi_han": cau_hinh,
        "phan_trang_core": phan_trang_core})),
        "bam_bo": pin["bam_bo_quy_tac"].lower(), "phien_ban_engine": phien_ban_engine}
    chu = uuid.uuid4().hex
    ban, giu = None, False
    try:
        for lan in range(4):
            viec.kiem_huy()
            try:
                luc = time.time()
                chiem = {"trang_thai": "dang_so", "chu_so_huu": chu, "luc_chiem": luc,
                         "han_chiem": luc + thoi_han_viec_giay + 60}
                with ngan.lo() as lo:
                    kq = lo.lay_hoac_tao("luot_doi_chieu", khoa, {**khoa, "ma_luot": uuid.uuid4().hex, **chiem})
                ban = kq.ban_ghi
                if kq.da_tao:
                    giu = True
                    break
                if ban.gia_tri["trang_thai"] == "da_so":
                    try:
                        return _lay_so_cu(doc, ban, s)
                    except LoiNghiepVu as exc:
                        if exc.ma != "DC_THIEU_NGUON":
                            raise
                    chiem["trang_thai"] = "dang_so"
                elif not (ban.gia_tri["trang_thai"] == "can_thu_lai" or ban.gia_tri.get("han_chiem", 0) <= luc):
                    raise LoiNghiepVu("DC_DANG_XU_LY", "Cặp tài liệu đang được xử lý. Anh thử lại sau.", thu_lai_duoc=True)
                with ngan.lo() as lo:
                    kq = lo.sua("luot_doi_chieu", {"phap_nhan_id": phap_nhan, "ma_luot": ban.gia_tri["ma_luot"]},
                                chiem, row_version=ban.row_version)
                ban, giu = kq.ban_ghi, True
                break
            except NganXungDot:
                if lan == 3:
                    raise
        viec.tien_do(25, "Đang căn cấu trúc và so văn bản có dấu")
        script, points, trang = so_hai_ban(s, viec.kiem_huy, cau_hinh["diem_lech_toi_da"], phan_trang_core=phan_trang_core)
        s.update(giai_doan="da_so", phien_ban_engine=phien_ban_engine, edit_script=script, diem_lech=points,
                 kiem_trang=trang, ho_so_truoc={"tep": deepcopy(pin["ho_so"]), "bam": pin["bam_ho_so"]},
                 thuat_toan_so="DC-4-1", da_kiem_du=False, ket_luan=None, de_nghi_chan=True)
        s["tom_tat"].update(so_diem=len(points))
        s["kiem_tra"].update(so_van_ban="dat", trang=trang["trang_thai"])
        s["canh_bao"] = ["Chưa áp quy tắc cứng, chưa phân loại điểm lệch, chưa kiểm OCR kém và chưa quét vùng sửa tay."]
        if trang["trang_thai"] == "chua_kiem":
            s["canh_bao"].append(trang["ly_do"])
        raw = hs.json_bytes(s)
        viec.kiem_huy()
        if len(raw) > cau_hinh["ho_so_mib"] * hs.MIB:
            loi("DC_QUA_GIOI_HAN")
        viec.tien_do(85, "Đang gửi hồ sơ so văn bản đầy đủ lên Core")
        tep = viec.tai_tep_ra("ho-so-da-so.json", raw, "application/json")
        pb = hs._phong_bi(s, tep, raw)
        for lan in range(3):
            viec.kiem_huy()
            try:
                with ngan.lo() as lo:
                    lo.sua("luot_doi_chieu", {"phap_nhan_id": phap_nhan, "ma_luot": ban.gia_tri["ma_luot"]},
                           {"trang_thai": "da_so", "phong_bi": pb}, row_version=ban.row_version)
                giu = False
                break
            except NganXungDot:
                ban = ngan.doc("luot_doi_chieu", khoa)
                if (ban is None or ban.gia_tri.get("chu_so_huu") != chu or
                        ban.gia_tri["trang_thai"] != "dang_so" or lan == 2):
                    raise
        viec.tien_do(100, "Đã so văn bản và giữ đầy đủ điểm lệch tại Core")
        viec.kiem_huy()
        return pb
    finally:
        if giu and ban is not None and ban.gia_tri.get("chu_so_huu") == chu:
            try:
                with ngan.lo() as lo:
                    lo.sua("luot_doi_chieu", {"phap_nhan_id": phap_nhan, "ma_luot": ban.gia_tri["ma_luot"]},
                           {"trang_thai": "can_thu_lai"}, row_version=ban.row_version)
            except Exception:
                pass
