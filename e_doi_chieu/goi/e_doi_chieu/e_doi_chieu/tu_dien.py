"""DC-7: từ điển hữu hạn đã ghim; vắng mục chỉ có nghĩa là chưa biết.

Chưa có nguồn DC-Q14. Bộ DEMO chỉ ở tests, không có từ điển mặc định.
"""
from bisect import bisect_right
import unicodedata

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ho_so as hs
from .so_chu import bo_dau
from .vi_tri import loi

CAP_CO_NGHIA = (("thuê", "thuế"), ("lãi", "lại"), ("phạt", "phát"),
               ("bán", "bàn"), ("không", "khống"), ("hạn", "hàn"))
_CO_NGHIA = frozenset(t for cap in CAP_CO_NGHIA for t in cap)


def chuan(text):
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def thieu():
    raise LoiNghiepVu("DC_THIEU_TU_DIEN", "Chưa có bộ từ điển đã duyệt và được ghim đúng phiên bản. Anh nhờ quản trị viên bổ sung; điểm lệch vẫn cần xem.")


class CacTu:
    """Một lần quét nguyên văn, offset Unicode; token cách nhau bởi khoảng trắng.

    Bỏ dấu câu ở hai mép; giữ dấu câu trong token (kể cả số 1.000.000).
    Token phải chứa chữ hoặc số. Không đếm nút khối/dòng/từ OCR lồng nhau.
    """
    def __init__(self, text, kiem=lambda: None):
        self.text, self.tu, self.dau, self.cuoi = text, [], [], []
        a, dau, cuoi, so = None, None, None, 1
        for i, c in enumerate(text + " "):
            if i % 256 == 0:
                kiem()
            if c.isspace():
                if dau is not None:
                    self.tu.append({"bat_dau": dau, "ket_thuc": cuoi, "van_ban": text[dau:cuoi], "so_trang": so})
                    self.dau.append(dau)
                    self.cuoi.append(cuoi)
                a = dau = cuoi = None
                if c == "\f":
                    so += 1
            else:
                if a is None:
                    a = i
                if c.isalnum():
                    if dau is None:
                        dau = i
                    cuoi = i + 1
                elif dau is not None and unicodedata.category(c).startswith("M"):
                    cuoi = i + 1

    def lay(self, a, b):
        if a == b:
            return []
        i, j = bisect_right(self.cuoi, a), bisect_right(self.dau, b - 1)
        return list(range(i, j))


class TuDien:
    def __init__(self, value, kiem):
        keys = {"phien_ban", "ma", "phien_ban_bo", "nguon", "giay_phep", "pham_vi",
                "am_tiet_co_nghia", "tu_co_nghia", "cap_vo_nghia_co_can_cu"}
        if (type(value) is not dict or set(value) != keys or type(value["phien_ban"]) is not int or value["phien_ban"] != 1):
            loi()
        for k in ("ma", "phien_ban_bo", "nguon", "giay_phep", "pham_vi"):
            if type(value[k]) is not str or not 1 <= len(value[k]) <= 1000 or not value[k].strip():
                loi()
        self.meta = {k: value[k] for k in ("ma", "phien_ban_bo", "nguon", "giay_phep", "pham_vi")}
        self.co_nghia, self.vo_nghia = set(_CO_NGHIA), {}
        for k in ("am_tiet_co_nghia", "tu_co_nghia"):
            if type(value[k]) is not list or len(value[k]) > 100000:
                loi()
            da_co = set()
            for t in value[k]:
                kiem()
                if type(t) is not str or not 1 <= len(t) <= 200 or not chuan(t) or chuan(t) in da_co:
                    loi()
                da_co.add(chuan(t))
            self.co_nghia.update(da_co)
        ds = value["cap_vo_nghia_co_can_cu"]
        if type(ds) is not list or len(ds) > 10000:
            loi()
        for cap in ds:
            kiem()
            if type(cap) is not dict or set(cap) != {"word", "ocr", "can_cu"}:
                loi()
            if any(type(cap[k]) is not str or not 1 <= len(cap[k]) <= 1000 or not cap[k].strip() for k in cap):
                loi()
            w, o = chuan(cap["word"]), chuan(cap["ocr"])
            if (w == o or bo_dau(w) != bo_dau(o) or w not in self.co_nghia or
                    o in self.co_nghia or (w, o) in self.vo_nghia):
                loi()
            self.vo_nghia[w, o] = cap["can_cu"]

    def tra(self, word, ocr):
        w, o = chuan(word), chuan(ocr)
        # Từ/cụm có nghĩa luôn thắng chứng nhận vô nghĩa, kể cả bộ hữu hạn thiếu mục.
        if w in self.co_nghia and o in self.co_nghia:
            return "ca_hai_co_nghia", None
        if (w, o) in self.vo_nghia:
            return "vo_nghia_co_can_cu", self.vo_nghia[w, o]
        return "chua_biet", None


def doc_tu_dien(s, doc, cau_hinh, kiem):
    q = s["bo_quy_tac"]["noi_dung"].get("lech_dau", {})
    ref = q.get("tu_dien") if type(q) is dict else None
    if type(ref) is not dict:
        thieu()
    try:
        hs._ref(ref, ("application/json",), min(20, cau_hinh["ho_so_mib"]) * hs.MIB, True)
    except LoiNghiepVu as exc:
        if exc.ma == "DC_SAI_DAU_VAO":
            loi()
        raise
    if not cau_hinh.get("ma_tu_dien") or not cau_hinh.get("bam_tu_dien"):
        thieu()
    if hs._bam(cau_hinh["bam_tu_dien"]) != hs._bam(ref["bam"]):
        loi()
    try:
        raw = doc.doc(ref, min(20, cau_hinh["ho_so_mib"]) * hs.MIB)
    except LoiNghiepVu as exc:
        if exc.ma == "DC_THIEU_NGUON":
            thieu()
        raise
    td = TuDien(hs.doc_json(raw, kiem), kiem)
    if td.meta["ma"] != cau_hinh["ma_tu_dien"] or td.meta["phien_ban_bo"] != ref["phien_ban"]:
        loi()
    return td, {**td.meta, "tep": ref["tep"], "bam": ref["bam"]}
