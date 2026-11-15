"""DC-5: sàn Python, vùng bảo vệ và kiểm tiền nội bộ; không gọi AI."""
from bisect import bisect_right
from collections import Counter
from copy import deepcopy
import re
import time
import uuid

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ho_so as hs
from . import so_chu as sc
from .can_chinh import BanDo
from .chuan_hoa import chuan_hoa
from .ngan import NganXungDot
from .tien_chu import chuan_chu, doc_ngay, doc_so, doc_tien_chu, doc_tien_so, so_json
from .vi_tri import loi

PHIEN_BAN = "DC-5-1"
CAC_VUNG = ("ben_ky", "nguoi_dai_dien", "chuc_vu", "mst", "stk", "dia_chi", "so_hop_dong")
CAC_QUY_TAC = ("DC_CHU_SO", "DC_NGAY_THOI_HAN", "DC_TIEN_TY_LE", "DC_TIEN_CHU",
               "DC_DINH_DANH", "DC_CAU_TRUC", "DC_PHU_DINH_BAT_BUOC", "DC_OCR_NHAM")
_NHAN = {
    "ben_ky": r"bên\s+(?:a|b|c|d|ký|thuê|cho\s+thuê|mua|bán|vay|cho\s+vay|giao\s+thầu|nhận\s+thầu)|party\s+[abcd]",
    "nguoi_dai_dien": r"(?:người\s+)?đại\s+diện|represented\s+by|representative",
    "chuc_vu": r"chức\s+vụ|position|title",
    "mst": r"mst|mã\s+số\s+thuế|tax\s+(?:code|id)",
    "stk": r"stk|số\s+tài\s+khoản|tài\s+khoản|bank\s+account",
    "dia_chi": r"địa\s+chỉ|address",
    "so_hop_dong": r"số\s+hợp\s+đồng|hợp\s+đồng\s+số|contract\s+(?:no\.?|number)",
}
_SO = re.compile(r"(?<!\w)[+\-−]?[0-9]+(?:[.,][0-9]+|[ \u00a0][0-9]{3}(?![0-9]))*")
_NGAY = re.compile(r"(?<!\w)(?:[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{4})(?!\w)")
_PHU = re.compile(r"\b(?:ngoại\s+trừ|có\s+thể|không|chưa|chỉ|trừ|phải|được|not|shall|must|may|except)\b", re.I)
_TU = re.compile(r"\w+", re.UNICODE)
_MUC = {"nhieu_ocr": 0, "hinh_thuc": 1, "can_xem": 2, "nghiem_trong": 3}


def bo_khong_hop_le():
    raise LoiNghiepVu("DC_BO_QUY_TAC_KHONG_HOP_LE", "Bộ quy tắc đối chiếu chưa hợp lệ. Anh chọn lại bộ đã được duyệt.")


def kiem_bo_cung(bo):
    """Bộ DC-3 cũ vẫn so được nhưng thiếu nhận diện thì không đủ kiểm.

    Phần quy_tac_cung là quy ước ghim trong bộ, không đổi API/schema chung.
    Quy tắc bắt buộc luôn bật, bộ không có tùy chọn tắt hoặc hạ sàn.
    """
    if type(bo) is not dict:
        bo_khong_hop_le()
    q = bo.get("quy_tac_cung")
    if "quy_tac_cung" not in bo:
        return {"phien_ban": 1, "dinh_dang_so": [], "don_vi_tien": {},
                "dinh_dang_ngay": ["YYYY-MM-DD"], "vung_bao_ve": [], "da_khai": False}
    if (type(q) is not dict or set(q) != {"phien_ban", "dinh_dang_so", "don_vi_tien", "dinh_dang_ngay", "vung_bao_ve"}
            or type(q["phien_ban"]) is not int or q["phien_ban"] != 1):
        bo_khong_hop_le()
    if type(q["dinh_dang_so"]) is not list or len(q["dinh_dang_so"]) > 10:
        bo_khong_hop_le()
    for f in q["dinh_dang_so"]:
        if (type(f) is not dict or set(f) != {"nghin", "thap_phan"} or
                f["nghin"] not in (None, ".", ",", " ") or f["thap_phan"] not in (None, ".", ",") or
                f["nghin"] is not None and f["nghin"] == f["thap_phan"]):
            bo_khong_hop_le()
    dv = q["don_vi_tien"]
    if type(dv) is not dict or len(dv) > 100:
        bo_khong_hop_le()
    for ten, ma in dv.items():
        if (type(ten) is not str or not ten.strip() or len(ten) > 100 or
                type(ma) is not str or not re.fullmatch(r"[A-Z]{3}", ma)):
            bo_khong_hop_le()
    keys = [chuan_chu(x) for x in dv]
    if len(set(keys)) != len(keys):
        bo_khong_hop_le()
    # Mã tường minh không được khai trái thành loại tiền khác.
    if any(re.fullmatch(r"[A-Z]{3}", t) and t != ma or
           chuan_chu(t) in ("đồng", "vnđ") and ma != "VND" for t, ma in dv.items()):
        bo_khong_hop_le()
    ngay = q["dinh_dang_ngay"]
    if (type(ngay) is not list or not ngay or len(ngay) > 3 or
            any(type(x) is not str or x not in ("YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY") for x in ngay)):
        bo_khong_hop_le()
    vung = q["vung_bao_ve"]
    if type(vung) is not list or len(vung) > 1000:
        bo_khong_hop_le()
    for v in vung:
        if (type(v) is not dict or set(v) != {"ben", "loai", "bat_dau", "ket_thuc", "nguyen_van", "bam_van_ban"}
                or v["ben"] not in ("word", "ban_ky") or v["loai"] not in CAC_VUNG
                or type(v["bat_dau"]) is not int or type(v["ket_thuc"]) is not int
                or not 0 <= v["bat_dau"] < v["ket_thuc"] <= 500000
                or type(v["nguyen_van"]) is not str or not v["nguyen_van"].strip()
                or type(v["bam_van_ban"]) is not str or not hs._BAM.fullmatch(v["bam_van_ban"])):
            bo_khong_hop_le()
    return {**deepcopy(q), "da_khai": True}


class _ChiMuc:
    def __init__(self, ds):
        self.ds = sorted(ds, key=lambda v: (v["bat_dau"], v["ket_thuc"]))
        self.dau, self.cuoi = [], []
        e = -1
        for v in self.ds:
            self.dau.append(v["bat_dau"])
            e = max(e, v["ket_thuc"])
            self.cuoi.append(e)

    def lay(self, a, b):
        out = []
        i = bisect_right(self.dau, b) - 1
        while i >= 0 and self.cuoi[i] >= a:
            v = self.ds[i]
            x, y = v["bat_dau"], v["ket_thuc"]
            if x < b and a < y or a == b and x <= a <= y:
                out.append(v)
            i -= 1
        return out


class _Ban:
    def __init__(self, snapshot, ben, kiem):
        self.ben, self.kiem = ben, kiem
        v = snapshot["van_ban"][ben]["van_ban_tai_lieu"]
        # Quét cả phần đầu/chân trang, không chỉ phần DC-3 đã cho phép bỏ.
        q = {"unicode": "NFC", "khoang_trang": "giu_nguyen", "dau_nhay": "giu_nguyen",
             "gach_noi": "giu_nguyen", "ngat_dong": "giu_nguyen", "ngat_tu_cuoi_dong": "giu_nguyen",
             "dau_chan_trang": [], "bo_so_trang": False}
        ch = chuan_hoa(v, q, kiem)
        self.raw, self.text, self.map = v["van_ban"], ch["van_ban"], BanDo(ch)
        self.bam = hs.bam(self.raw.encode("utf-8"))
        self.tu = _ChiMuc([self.vung(m.start(), m.end(), "tu") for m in _TU.finditer(self.text)])

    def vung(self, a, b, loai, **phu):
        while a > 0 and not self.map.bien_an_toan(a):
            a -= 1
        while b < len(self.text) and not self.map.bien_an_toan(b):
            b += 1
        x, y = self.map.ve_goc(a), self.map.ve_goc(b)
        return {"ben": self.ben, "loai": loai, "bat_dau": x, "ket_thuc": y,
                "nguyen_van": self.raw[x:y], "bam_vung": hs.bam(self.raw[x:y].encode("utf-8")),
                "bam_van_ban": self.bam, **phu}

    def token(self, p):
        ds = self.tu.lay(p["bat_dau"], p["ket_thuc"])
        if sum(len(v["nguyen_van"]) for v in ds) > 200:
            return ""
        return " ".join(chuan_chu(v["nguyen_van"]) for v in reversed(ds))


def _tham_chieu(v):
    """Nguyên văn nằm trong nguồn bất biến; không nhân cả dòng dài vào mỗi điểm."""
    return {k: deepcopy(x) for k, x in v.items() if k != "nguyen_van"}


def _vung_bao_ve(ban, q):
    ds = []
    for loai, pat in _NHAN.items():
        ban.kiem()
        # Nhãn và giá trị cùng dòng/ô; không cắt tại dấu chấm trong tên/địa chỉ.
        rx = re.compile(r"\b(?:" + pat + r")\b[^\n\f\t;]*", re.I)
        for m in rx.finditer(ban.text):
            ban.kiem()
            nhan = re.match(r"(?:" + pat + r")", m.group(), re.I)
            ds.append(ban.vung(m.start(), m.end(), loai, nguon="nhan_python",
                               co_gia_tri=bool(m.group()[nhan.end():].strip(" :：.-"))))
    for v in q["vung_bao_ve"]:
        if v["ben"] != ban.ben:
            continue
        if v["bam_van_ban"].lower() != ban.bam or ban.raw[v["bat_dau"]:v["ket_thuc"]] != v["nguyen_van"]:
            loi()
        ds.append({**deepcopy(v), "bam_vung": hs.bam(v["nguyen_van"].encode("utf-8")), "nguon": "metadata_da_kiem"})
    return ds


def _dac_trung(ban, q):
    ds = []
    for m in _SO.finditer(ban.text):
        ban.kiem()
        n = doc_so(m.group(), q["dinh_dang_so"])
        ds.append(ban.vung(m.start(), m.end(), "so", gia_tri=None if n is None else so_json(n)))
    for m in _PHU.finditer(ban.text):
        ds.append(ban.vung(m.start(), m.end(), "phu_dinh"))
    for m in _NGAY.finditer(ban.text):
        ds.append(ban.vung(m.start(), m.end(), "ngay", ngay=doc_ngay(m.group(), q["dinh_dang_ngay"])))
    for loai, pat in (
        ("thoi_han", r"\b(?:thời\s+hạn|thời\s+điểm|hạn\s+(?:trả|giao|thanh\s+toán)|ngày|tháng|năm|date|duration|term|days?|months?|years?|deadline)\b"),
        ("tien", r"\b(?:số\s+tiền|đơn\s+vị\s+tiền(?:\s+tệ)?|bằng\s+chữ|giá\s+trị|thanh\s+toán|tỷ\s+lệ|lãi\s+suất|VND|VNĐ|USD|EUR|GBP|JPY)\b|\b(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|trăm|nghìn|ngàn|triệu|tỷ)\s+đồng\b|[%‰$€¥£₫]"),
    ):
        # Mở rộng tới đầu/cuối câu hoặc ô: thay một chữ cạnh nhãn cũng phải bắt.
        for m in re.finditer(r"[^\n\f\t;!?]+", ban.text):
            ban.kiem()
            if re.search(pat, m.group(), re.I):
                ds.append(ban.vung(m.start(), m.end(), loai))
    # Đơn vị khác do bộ khai được nhận như vùng tiền, không chỉ mã có sẵn.
    if q["don_vi_tien"]:
        pat = r"(?<!\w)(?:" + "|".join(re.escape(x) for x in sorted(q["don_vi_tien"], key=len, reverse=True)) + r")(?!\w)"
        for m in re.finditer(pat, ban.text, re.I):
            ds.append(ban.vung(m.start(), m.end(), "don_vi_tien"))
    # Mã tiền chưa có quy ước vẫn là vùng phải bảo vệ, không tự suy giá trị.
    for m in re.finditer(r"(?<!\w)[+\-]?[0-9]+(?:[.,][0-9]+)*\s*[A-Z]{3}(?!\w)", ban.text):
        ban.kiem()
        ds.append(ban.vung(m.start(), m.end(), "tien"))
    return ds


def _can_cu(d, ma, **chi_tiet):
    if ma not in d["quy_tac_trung"]:
        d["quy_tac_trung"].append(ma)
    d["can_cu_quy_tac"].append({"quy_tac": ma, **chi_tiet})


def _cham_diem(d, bans, idx, bao_ve, q):
    d.update(muc_san="can_xem", muc="can_xem", cho_phan_loai=True, quy_tac_trung=[],
             can_cu_quy_tac=[], vung_bao_ve=[])
    feats, tokens = {}, {}
    for ben in ("word", "ban_ky"):
        p = d[ben]
        feats[ben], tokens[ben] = [], ""
        if p is not None:
            feats[ben] = idx[ben].lay(p["bat_dau"], p["ket_thuc"])
            tokens[ben] = bans[ben].token(p)
            d["vung_bao_ve"].extend(_tham_chieu(v) for v in bao_ve[ben].lay(p["bat_dau"], p["ket_thuc"]))
    all_f = feats["word"] + feats["ban_ky"]
    types = {f["loai"] for f in all_f}
    a, b = ["" if d[k] is None else d[k]["nguyen_van"] for k in ("word", "ban_ky")]
    format_only = False
    so = [[f for f in feats[k] if f["loai"] == "so"] for k in ("word", "ban_ky")]
    if all(len(x) == 1 for x in so) and not d["vung_bao_ve"]:
        x, y = so[0][0], so[1][0]
        # Chỉ chuẩn phân cách nếu cùng chuỗi chữ số (giữ cả 0 đầu), đọc được
        # cùng giá trị theo bộ. Không dùng Decimal để làm bằng hai mã khác.
        format_only = (x["gia_tri"] is not None and y["gia_tri"] is not None and
                       x["gia_tri"] == y["gia_tri"] and
                       re.sub(r"[^0-9+\-]", "", x["nguyen_van"]) == re.sub(r"[^0-9+\-]", "", y["nguyen_van"]) and
                       x["nguyen_van"] != y["nguyen_van"])
    if not format_only and (re.search(r"[0-9]", a + b) or "so" in types):
        _can_cu(d, "DC_CHU_SO", so_hai_ban=[[_tham_chieu(v) for v in ds] for ds in so])
    if "ngay" in types or "thoi_han" in types:
        _can_cu(d, "DC_NGAY_THOI_HAN", ngay=[f for f in all_f if f["loai"] == "ngay"])
    if not format_only and types & {"tien", "don_vi_tien"}:
        _can_cu(d, "DC_TIEN_TY_LE")
    if "phu_dinh" in types:
        _can_cu(d, "DC_PHU_DINH_BAT_BUOC", cum_tu=[f for f in all_f if f["loai"] == "phu_dinh"])
    if d["vung_bao_ve"]:
        _can_cu(d, "DC_DINH_DANH", loai=sorted({v["loai"] for v in d["vung_bao_ve"]}))
    if d["nhom"] in ("cau_truc", "trang"):
        _can_cu(d, "DC_CAU_TRUC", phuong_phap=d["can_cu"]["phuong_phap"])
    # So từ trọn vẹn vì diff có thể chỉ chứa một chữ trong MST/tên.
    trans = str.maketrans({"o": "0", "l": "1", "s": "5", "b": "8"})
    x, y = tokens["word"], tokens["ban_ky"]
    if (not x or not y) and len(a) <= 200 and len(b) <= 200:
        x, y = chuan_chu(a), chuan_chu(b)
    if x and y and x != y and x.translate(trans) == y.translate(trans) and re.search(r"[0158]", x + y):
        _can_cu(d, "DC_OCR_NHAM", ghi_chu="Nghi nhầm OCR; vẫn giữ Nghiêm trọng.")
    if d["quy_tac_trung"]:
        d.update(muc_san="nghiem_trong", muc="nghiem_trong", cho_phan_loai=False)
    elif format_only:
        d.update(muc_san="hinh_thuc", muc="hinh_thuc", cho_phan_loai=False)
        d["can_cu_quy_tac"].append({"quy_tac": "chuan_phan_cach_da_khai", "dinh_dang_so": deepcopy(q["dinh_dang_so"])})
    d["quy_tac_trung"].sort()


def _lat(ban, a, b):
    v = ban.vung(a, b, "tien")
    return {"nguyen_van": v["nguyen_van"], "bat_dau": v["bat_dau"], "ket_thuc": v["ket_thuc"], "vi_tri": None}


def _kiem_tien_noi_bo(ban, q, kiem):
    """Ghép duy nhất trong cùng dòng/ô; không nối một số với chữ ở khoản khác."""
    ds = []
    units = sorted(set(q["don_vi_tien"]) | {"VND", "VNĐ", "USD", "EUR", "GBP", "JPY", "đồng", "đô la", "đô la Mỹ", "$", "€", "¥", "£", "₫"}, key=len, reverse=True)
    pat_don_vi = r"(?:" + "|".join(re.escape(x) for x in units) + r"|[A-Z]{3})(?!\w)"
    pat_tien = r"(?<!\w)[+\-−]?[0-9]+(?:[.,][0-9]+|[ \u00a0][0-9]{3}(?![0-9]))*\s*" + pat_don_vi
    for line in re.finditer(r"[^\n\f\t|]+", ban.text):
        kiem()
        text, off = line.group(), line.start()
        marks = list(re.finditer(r"\b(?:bằng\s+chữ|in\s+words)\s*[:：]?\s*", text, re.I))
        # Tìm mọi cụm số + đơn vị, kể cả đơn vị chưa biết. Không suy tiền tệ.
        amounts = list(re.finditer(pat_tien, text, re.I))
        words_money = re.search(r"\b(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|trăm|triệu|tỷ)\b.*\b(?:đồng|VND|USD|EUR)\b", text, re.I)
        if not marks and not amounts and not words_money:
            continue
        so, chu, tien_so, tien_chu = None, None, None, None
        ly_do = "Chưa nhận diện duy nhất cặp tiền bằng số và bằng chữ trong cùng dòng hoặc ô."
        if len(marks) == 1:
            m = marks[0]
            # Lấy trọn phần sau nhãn; chỉ bỏ ngoặc đóng/dấu câu kết thúc.
            end = len(text.rstrip(" .;"))
            if end > m.end() and text[end - 1:end] == ")":
                end -= 1
            chu = _lat(ban, off + m.end(), off + end)
            tien_chu = doc_tien_chu(text[m.end():end], q["don_vi_tien"])
            before = [x for x in amounts if x.end() <= m.start()]
            # Không chấp nhận một dòng có nhiều số tiền dù có thể chọn số gần nhất.
            if len(before) == 1 and len(amounts) == 1:
                x = before[0]
                so = _lat(ban, off + x.start(), off + x.end())
                tien_so = doc_tien_so(x.group(), q["don_vi_tien"], q["dinh_dang_so"])
        elif len(amounts) == 1:
            x = amounts[0]
            so = _lat(ban, off + x.start(), off + x.end())
        du = tien_so is not None and tien_chu is not None
        if du:
            khop = tien_so["tien_te"] == tien_chu["tien_te"] and doc_so(str(tien_so["so"]), [{"nghin": None, "thap_phan": "."}]) == tien_chu["so"]
            ly_do = "Đã phân tích đủ số, chữ và đơn vị theo bộ đã ghim."
        else:
            khop = None
        ds.append({"so": so, "chu": chu, "tien_bang_so": tien_so, "tien_bang_chu": tien_chu,
                   "nguyen_van": _lat(ban, line.start(), line.end()), "da_kiem_du": du, "khop": khop, "ly_do": ly_do})
    return ds


def _dau_diem(d):
    return {k: deepcopy(d[k]) for k in ("ma_diem", "muc_san", "quy_tac_trung", "can_cu_quy_tac", "vung_bao_ve")}


def _kiem_truoc_chuan_hoa(out, bans, features, protect, q, kiem, toi_da, kiem_byte):
    """Không để chuẩn gạch/nháy/khoảng trắng che mất lệch trong vùng cứng.

    NFC tương đương vẫn được duyệt. Chỉ giữ các lát khác còn chạm số,
    đơn vị hoặc vùng bảo vệ; không dùng cả dòng
    chứa tiền/ngày để nâng một thay đổi khoảng trắng bên ngoài vùng đó.
    """
    idx = {k: _ChiMuc([f for f in ds if f["loai"] not in ("tien", "thoi_han", "phu_dinh")]) for k, ds in features.items()}
    for op in out["edit_script"]:
        kiem()
        if op["phep"] != "tuong_duong_chuan_hoa":
            continue
        lo = {k: (bans[k].map.ve_chuan(op[k]["bat_dau"]), bans[k].map.ve_chuan(op[k]["ket_thuc"])) for k in bans}
        def ghi(phep, a, b, c, d, can_cu):
            kiem()
            if phep == "giu":
                return
            w, ky = _lat(bans["word"], a, b), _lat(bans["ban_ky"], c, d)
            if not w["nguyen_van"].strip() and not ky["nguyen_van"].strip():
                # Khoảng trắng bên ngoài token không phải sửa chữ số; với
                # lát rỗng chỉ nhận khi ở bên trong vùng, không tại mép.
                cham = False
                for ben, p in (("word", w), ("ban_ky", ky)):
                    x, y = p["bat_dau"], p["ket_thuc"]
                    for v in idx[ben].lay(x, y) + protect[ben].lay(x, y):
                        if x < y or v["bat_dau"] < x < v["ket_thuc"]:
                            cham = True
                            break
                if not cham:
                    return
            data = {"phep": phep, "nhom": "bao_ve_truoc_chuan_hoa", "word": w, "ban_ky": ky,
                    "can_cu": {"phuong_phap": "kiem_nguyen_van_truoc_chuan_hoa"}}
            ma = "DC-" + hs.bam(hs.json_bytes({"thuat_toan": PHIEN_BAN, "bam_bo": out["bo_quy_tac"]["bam"],
                "nguon": {k: v["bam"] for k, v in out["nguon"].items()}, **data}))[7:]
            point = {"ma_diem": ma, **data}
            _cham_diem(point, bans, idx, protect, q)
            if point["quy_tac_trung"] or point["muc_san"] == "hinh_thuc":
                kiem_byte(point)
                out["diem_lech"].append(point)
                if len(out["diem_lech"]) > toi_da:
                    loi("DC_QUA_GIOI_HAN")
        sc._so_lat(bans["word"].text, bans["ban_ky"].text, *lo["word"], *lo["ban_ky"], ghi, kiem, [])


def kiem_bat_bien(snapshot, goc=None):
    """goc phải là snapshot tin cậy đọc lại từ Core, không nhận từ phản hồi AI."""
    try:
        return _kiem_bat_bien(snapshot, goc)
    except (KeyError, TypeError, ValueError):
        loi()


def _kiem_bat_bien(snapshot, goc):
    points = snapshot["diem_lech"]
    ds = [_dau_diem(d) for d in points]
    if (snapshot.get("nhat_ky_quy_tac") != ds or snapshot.get("bam_nhat_ky_quy_tac") != hs.bam(hs.json_bytes(ds)) or
            len({d["ma_diem"] for d in points}) != len(points) or
            any(d["muc"] not in _MUC or _MUC[d["muc"]] < _MUC[d["muc_san"]] or
                d["quy_tac_trung"] and d["muc_san"] != "nghiem_trong" for d in points)):
        loi()
    if goc is not None:
        # Không cho tự băm lại nhật ký, mất điểm hoặc thay văn bản/căn cứ.
        for k in ("nhat_ky_quy_tac", "bam_nhat_ky_quy_tac", "nguon", "van_ban", "chuan_hoa", "bo_quy_tac", "edit_script"):
            if snapshot[k] != goc[k]:
                loi()
        if [{k: v for k, v in d.items() if k not in ("muc", "ly_do_ai", "cho_phan_loai")} for d in points] != [
                {k: v for k, v in d.items() if k not in ("muc", "ly_do_ai", "cho_phan_loai")} for d in goc["diem_lech"]]:
            loi()
        if any(_MUC[d["muc"]] < _MUC[cu["muc"]] for d, cu in zip(points, goc["diem_lech"])):
            loi()
    return True


def ap_muc_ai(snapshot, de_xuat):
    """Cửa thuần cho DC-6: chỉ đổi mức/lý do, không nhận sàn/quy tắc từ AI."""
    kiem_bat_bien(snapshot)
    out = deepcopy(snapshot)
    points = {d["ma_diem"]: d for d in out["diem_lech"]}
    if (type(de_xuat) is not list or len(de_xuat) != len(points) or
            any(type(x) is not dict or set(x) != {"ma_diem", "muc", "ly_do"} or
                type(x["ma_diem"]) is not str or type(x["muc"]) is not str for x in de_xuat) or
            len({x["ma_diem"] for x in de_xuat}) != len(points)):
        loi()
    for x in de_xuat:
        d = points.get(x["ma_diem"])
        if d is None or x["muc"] not in _MUC or type(x["ly_do"]) is not str:
            loi()
        if _MUC[x["muc"]] < max(_MUC[d["muc_san"]], _MUC[d["muc"]]):
            raise LoiNghiepVu("DC_HA_MUC_TRAI_QUY_TAC", "Không thể hạ mức điểm lệch trái quy tắc Python.")
        d.update(muc=x["muc"], ly_do_ai=x["ly_do"], cho_phan_loai=False)
    kiem_bat_bien(out, snapshot)
    dem = Counter(d["muc"] for d in out["diem_lech"])
    out["tom_tat"].update({"so_" + k: dem[k] for k in _MUC})
    return out


def ap_quy_tac(snapshot, kiem=lambda: None, toi_da_diem=10000, *, toi_da_byte=20 * hs.MIB):
    """Nhận snapshot đã so DC-4, trả bản sao; nguyên văn/edit script bất biến."""
    if "thuat_toan_quy_tac" in snapshot:
        if snapshot["thuat_toan_quy_tac"] != PHIEN_BAN:
            loi()
        kiem_bat_bien(snapshot)
        return deepcopy(snapshot)
    out = deepcopy(snapshot)
    tong_byte = len(hs.json_bytes({k: v for k, v in out.items() if k != "diem_lech"}))
    if tong_byte > toi_da_byte:
        loi("DC_QUA_GIOI_HAN")
    byte_diem = {}
    def kiem_byte(d):
        nonlocal tong_byte
        kiem()
        size = len(hs.json_bytes(d)) + len(hs.json_bytes(_dau_diem(d))) + 2
        tong_byte += size - byte_diem.get(d["ma_diem"], 0)
        byte_diem[d["ma_diem"]] = size
        if tong_byte > toi_da_byte:
            loi("DC_QUA_GIOI_HAN")
    q = kiem_bo_cung(out["bo_quy_tac"]["noi_dung"])
    bans = {k: _Ban(out, k, kiem) for k in ("word", "ban_ky")}
    regions = {k: _vung_bao_ve(v, q) for k, v in bans.items()}
    features = {k: _dac_trung(v, q) for k, v in bans.items()}
    idx = {k: _ChiMuc(v) for k, v in features.items()}
    protect = {k: _ChiMuc(v) for k, v in regions.items()}
    for d in out["diem_lech"]:
        kiem()
        _cham_diem(d, bans, idx, protect, q)
        kiem_byte(d)
    _kiem_truoc_chuan_hoa(out, bans, features, protect, q, kiem, toi_da_diem, kiem_byte)
    # Các lát chữ/ngắt dòng thuộc thao tác thiếu/thừa/đảo cùng giữ sàn
    # cấu trúc; không chỉ điểm tổng hợp riêng do DC-4 tạo ra.
    ct = {}
    for ben in bans:
        ct[ben] = _ChiMuc([{"bat_dau": max(0, d[ben]["bat_dau"] - 1),
                            "ket_thuc": min(len(bans[ben].raw), d[ben]["ket_thuc"] + 1),
                            "ma_diem": d["ma_diem"]}
                           for d in out["diem_lech"] if d["nhom"] == "cau_truc" and d[ben] is not None])
    for d in out["diem_lech"]:
        kiem()
        lien_quan = sorted({v["ma_diem"] for ben in bans if d[ben] is not None
                             for v in ct[ben].lay(d[ben]["bat_dau"], d[ben]["ket_thuc"])})
        if lien_quan and "DC_CAU_TRUC" not in d["quy_tac_trung"]:
            _can_cu(d, "DC_CAU_TRUC", diem_cau_truc=lien_quan)
            d["quy_tac_trung"].sort()
            d.update(muc_san="nghiem_trong", muc="nghiem_trong", cho_phan_loai=False)
            kiem_byte(d)
    tien = _kiem_tien_noi_bo(bans["ban_ky"], q, kiem)
    for kt in tien:
        kiem()
        if kt["khop"] is True:
            continue
        muc = "nghiem_trong" if kt["da_kiem_du"] else "can_xem"
        data = {"nhom": "tien_trong_ban_ky", "word": None, "ban_ky": kt["nguyen_van"],
                "phep": "kiem_noi_bo", "can_cu": {"phuong_phap": "so_tien_bang_so_va_chu", "kiem_tien": kt}}
        ma = "DC-" + hs.bam(hs.json_bytes({"thuat_toan": PHIEN_BAN,
            "nguon": {k: v["bam"] for k, v in out["nguon"].items()}, "bam_bo": out["bo_quy_tac"]["bam"], **data}))[7:]
        point = {"ma_diem": ma, **data, "muc_san": muc, "muc": muc,
            "cho_phan_loai": not kt["da_kiem_du"], "quy_tac_trung": ["DC_TIEN_CHU"] if kt["da_kiem_du"] else [],
            "can_cu_quy_tac": [{"quy_tac": "DC_TIEN_CHU", "da_kiem_du": kt["da_kiem_du"], "ly_do": kt["ly_do"]}], "vung_bao_ve": []}
        kiem_byte(point)
        out["diem_lech"].append(point)
        if len(out["diem_lech"]) > toi_da_diem:
            loi("DC_QUA_GIOI_HAN")
    covered = {k: sorted({v["loai"] for v in ds}) for k, ds in regions.items()}
    # Nhãn tự động để bắt lệch, không tự chứng nhận đã nhận diện đủ mọi bên.
    xac_minh = {k: sorted({v["loai"] for v in ds if v["nguon"] == "metadata_da_kiem"}) for k, ds in regions.items()}
    missing = {k: sorted(set(CAC_VUNG) - set(ds)) for k, ds in xac_minh.items()}
    so_du = q["da_khai"] and all(f.get("gia_tri") is not None for ds in features.values() for f in ds if f["loai"] == "so")
    ngay_du = all(f.get("ngay") is not None for ds in features.values() for f in ds if f["loai"] == "ngay")
    # Ngày/thời hạn bằng lời chưa có parser đủ căn cứ vẫn bảo vệ điểm lệch,
    # nhưng không coi đã phân tích đầy đủ ngày chỉ vì regex số không thấy.
    thoi_gian_chua_doc = {}
    for k, ds in features.items():
        kiem()
        ngay_idx = _ChiMuc([f for f in ds if f["loai"] == "ngay"])
        thoi_gian_chua_doc[k] = [f for f in ds if f["loai"] == "thoi_han" and not any(
            f["bat_dau"] <= n["bat_dau"] < n["ket_thuc"] <= f["ket_thuc"]
            for n in ngay_idx.lay(f["bat_dau"], f["ket_thuc"]))]
    out["kiem_quy_tac"] = {
        "phien_ban": PHIEN_BAN, "vung_bao_ve": {"da_kiem_du": q["da_khai"] and not any(missing.values()), "da_nhan_dien": covered, "metadata_da_kiem": xac_minh, "con_thieu": missing},
        "so_va_ngay": {"da_kiem_du": so_du and ngay_du and not any(thoi_gian_chua_doc.values()),
                       "thoi_gian_chua_phan_tich": thoi_gian_chua_doc},
        "tien_bang_chu": {"da_kiem_du": q["da_khai"] and bool(tien) and all(x["da_kiem_du"] for x in tien), "danh_sach": tien},
        "phuong_phap": "Quét Python toàn văn hai bên và vùng metadata đã kiểm; không dùng nhận diện AI."}
    du = all(out["kiem_quy_tac"][k]["da_kiem_du"] for k in ("vung_bao_ve", "so_va_ngay", "tien_bang_chu"))
    out["kiem_tra"]["quy_tac_cung"] = "dat" if du else "chua_kiem"
    dem = Counter(d["muc"] for d in out["diem_lech"])
    out["tom_tat"].update(so_diem=len(out["diem_lech"]), **{"so_" + k: dem[k] for k in _MUC})
    out.update(da_kiem_du=False, de_nghi_chan=True, ket_luan=None, thuat_toan_quy_tac=PHIEN_BAN)
    out["nhat_ky_quy_tac"] = [_dau_diem(d) for d in out["diem_lech"]]
    out["bam_nhat_ky_quy_tac"] = hs.bam(hs.json_bytes(out["nhat_ky_quy_tac"]))
    out["canh_bao"] = ["Chưa kiểm OCR kém, chưa quét vùng sửa tay và chưa phân loại phần cần xem bằng Local AI."]
    if not du:
        out["canh_bao"].append("Chưa kiểm đủ quy tắc: thiếu nhận diện vùng bảo vệ hoặc chưa phân tích đủ số, ngày, tiền bằng chữ.")
    if out["kiem_tra"]["trang"] == "chua_kiem":
        out["canh_bao"].append(out["kiem_trang"]["ly_do"])
    kiem_bat_bien(out)
    if len(hs.json_bytes(out)) > toi_da_byte:
        loi("DC_QUA_GIOI_HAN")
    return out


def _lay_so_cu(doc, ban, truoc):
    pb = sc._lay_so_cu(doc, ban, truoc)
    p = pb["ho_so_doi_chieu"]
    raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, doc.cau_hinh["ho_so_mib"] * hs.MIB)
    s = hs.doc_json(raw, doc.viec.kiem_huy)
    if s.get("thuat_toan_quy_tac") != PHIEN_BAN:
        loi()
    kiem_bat_bien(s)
    dem = Counter(d["muc"] for d in s["diem_lech"])
    if any(s["tom_tat"]["so_" + k] != dem[k] for k in _MUC):
        loi()
    return pb


def so_van_ban(viec, ngan, cau_hinh, *, phien_ban_engine, thoi_han_viec_giay):
    """Cổng DC-5 dùng lõi/kiểm nguồn DC-4, chốt một snapshot đã áp quy tắc.

    Giữ nguyên so_chu.py để lát DC-4 độc lập; vòng giữ/chốt lượt theo cùng
    CAS/chủ/hạn của DC-4. Khóa thêm phiên bản quy tắc tránh dùng cache DC-4.
    """
    viec = sc._ViecCoHan(viec, thoi_han_viec_giay)
    viec.kiem_huy()
    viec.tien_do(5, "Đang kiểm hồ sơ và nguồn đã ghim")
    param = viec.tham_so.get("bo_quy_tac_json")
    if type(param) is not str:
        bo_khong_hop_le()
    if len(param) > 65536 or len(param.encode("utf-8")) > 65536:
        loi("DC_QUA_GIOI_HAN")
    try:
        bo = hs.doc_json(param.encode("utf-8"), viec.kiem_huy)
    except LoiNghiepVu as exc:
        if exc.ma == "DC_SAI_DAU_VAO":
            bo_khong_hop_le()
        raise
    if type(bo) is not dict:
        bo_khong_hop_le()
    kiem_bo_cung(bo)
    s, doc, cau_hinh = sc._doc_ho_so(viec, cau_hinh)
    phap_nhan = viec.ngu_canh.get("phap_nhan_id")
    if type(phap_nhan) is not str or not phap_nhan.strip():
        loi("DC_THIEU_NGUON")
    pin = viec.dau_vao["ho_so_doi_chieu"]
    phan_trang_core = viec.ngu_canh.get("doi_chieu_phan_trang")
    if phan_trang_core is not None and len(hs.json_bytes(phan_trang_core)) > 16384:
        loi("DC_QUA_GIOI_HAN")
    khoa = {"phap_nhan_id": phap_nhan, "bam_cap": hs.bam(hs.json_bytes({
        "buoc": "so_van_ban@1", "quy_tac": PHIEN_BAN, "bam_ho_so_nhan": pin["bam_ho_so"],
        "gioi_han": cau_hinh, "phan_trang_core": phan_trang_core})),
        "bam_bo": pin["bam_bo_quy_tac"].lower(), "phien_ban_engine": phien_ban_engine}
    chu, ban, giu = uuid.uuid4().hex, None, False
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
        viec.tien_do(25, "Đang căn cấu trúc và áp quy tắc Python toàn văn")
        script, points, trang = sc.so_hai_ban(s, viec.kiem_huy, cau_hinh["diem_lech_toi_da"], phan_trang_core=phan_trang_core)
        s.update(giai_doan="da_so", phien_ban_engine=phien_ban_engine, edit_script=script, diem_lech=points,
                 kiem_trang=trang, ho_so_truoc={"tep": deepcopy(pin["ho_so"]), "bam": pin["bam_ho_so"]},
                 thuat_toan_so="DC-4-1", da_kiem_du=False, ket_luan=None, de_nghi_chan=True)
        s["kiem_tra"].update(so_van_ban="dat", trang=trang["trang_thai"])
        s = ap_quy_tac(s, viec.kiem_huy, cau_hinh["diem_lech_toi_da"], toi_da_byte=cau_hinh["ho_so_mib"] * hs.MIB)
        raw = hs.json_bytes(s)
        viec.kiem_huy()
        if len(raw) > cau_hinh["ho_so_mib"] * hs.MIB:
            loi("DC_QUA_GIOI_HAN")
        viec.tien_do(85, "Đang gửi hồ sơ và sàn quy tắc Python lên Core")
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
        viec.tien_do(100, "Đã so văn bản và giữ sàn quy tắc Python tại Core")
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
