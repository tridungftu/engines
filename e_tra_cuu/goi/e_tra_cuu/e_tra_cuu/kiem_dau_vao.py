"""Kiểm miền TC-2; không phải validator JSON Schema tổng quát.

C-TC-02/03 chưa có trong SDK 2.0: cửa nguồn được chủ Core gắn ngoài payload,
trả giấy cấp theo viec_id. Không cờ JSON nào thay được cửa này. Không đọc đĩa,
không truy vấn kho kết quả/engine khác; mọi bytes chỉ qua viec.mo_tep.
"""

import base64
from copy import deepcopy
from datetime import date, datetime
from hashlib import sha256
import json
import math
import re

from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu


CAU_LOI = {
    "TC_DAU_VAO_KHONG_HOP_LE": "Yêu cầu tra cứu không hợp lệ. Anh kiểm tra lại hồ sơ.",
    "TC_SAI_NGUON": "Chưa kiểm chứng được nguồn tra cứu. Anh gửi lại yêu cầu từ hồ sơ được cấp quyền.",
    "TC_THIEU_NGU_CANH": "Chưa đủ ngữ cảnh tra cứu. Anh gửi lại yêu cầu từ hồ sơ.",
    "TC_CHUA_CO_CUA_CORE": "Core chưa cấp đủ cửa nguồn và quyền tra cứu. Anh nhờ quản trị viên kiểm tra.",
    "TC_QUA_GIOI_HAN": "Yêu cầu vượt giới hạn xử lý. Anh chia lại hồ sơ trước khi gửi.",
}
TAC_VU = {"phan_loai", "cat_doan", "phan_tich_cau_hoi", "xep_hang_lai", "soan_tra_loi"}
_BAM = re.compile(r"sha256:[0-9a-fA-F]{64}\Z")
_ID = re.compile(r"[^\s/\\:\x00-\x1f]+\Z")
_MIME = re.compile(r"[a-zA-Z0-9!#$&^_.+-]+/[a-zA-Z0-9!#$&^_.+-]+\Z")
_CAM = re.compile(r"[a-z][a-z0-9+.-]*://|\b(?:data|file):|[a-z]:[/\\]|\\\\|(?:^|\s)/|\.\.[/\\]", re.I)
_KHOA_CAM = {"url", "uri", "path", "duong_dan", "base64", "noi_dung_base64",
             "sql", "code", "ma_thuc_thi", "da_loc_quyen"}


def loi(ma="TC_DAU_VAO_KHONG_HOP_LE"):
    raise LoiNghiepVu(ma, CAU_LOI[ma])


def json_chuan(gia_tri):
    try:
        return json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
        loi()


def bam(noi_dung):
    return "sha256:" + sha256(noi_dung).hexdigest()


def kiem_bam(gia_tri):
    if type(gia_tri) is not str or not _BAM.fullmatch(gia_tri):
        loi("TC_SAI_NGUON")
    return gia_tri.lower()


def doc_json(noi_dung):
    def cap_khoa(cac_cap):
        kq = {}
        for k, v in cac_cap:
            if k in kq:
                raise ValueError()
            kq[k] = v
        return kq

    def cam_hang(gia_tri):
        raise ValueError()

    try:
        kq = json.loads(noi_dung.decode("utf-8"), object_pairs_hook=cap_khoa,
                        parse_constant=cam_hang)
        json_chuan(kq)  # Cả 1e999 và surrogate lẻ phải bị từ chối.
        return kq
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        loi()


def doi_tuong(v, bat_buoc=(), tuy_chon=None):
    if type(v) is not dict or not set(bat_buoc) <= v.keys():
        loi()
    if tuy_chon is not None and not v.keys() <= set(bat_buoc) | set(tuy_chon):
        loi()
    return v


def chuoi(v, toi_da=None):
    if type(v) is not str or not v.strip():
        loi()
    if toi_da is not None and len(v) > toi_da:
        loi("TC_QUA_GIOI_HAN")
    return v


def ma(v):
    if type(v) is not str or not _ID.fullmatch(v) or v in {".", ".."}:
        loi()
    return v


def danh_sach(v, toi_da=None):
    if type(v) is not list:
        loi()
    if toi_da is not None and len(v) > toi_da:
        loi("TC_QUA_GIOI_HAN")
    return v


def so(v, nho=None, lon=None, nguyen=False):
    if (type(v) not in ((int,) if nguyen else (int, float))
            or (type(v) is float and not math.isfinite(v))
            or (nho is not None and v < nho) or (lon is not None and v > lon)):
        loi()
    return v


def thoi_diem(v):
    try:
        if type(v) is not str or datetime.fromisoformat(v).utcoffset() is None:
            loi()
    except ValueError:
        loi()


def kiem_noi_dung_json(v):
    """Cấm kênh lấy dữ liệu/mã inline trong JSON yêu cầu và tài nguyên cấu trúc.

    Toàn văn OCR là chứng cứ bất hoạt, kiểm riêng, giữ nguyên phong bì. Nó
    không được dùng làm URL/path hay mã thực thi ngay cả khi có chữ như vậy.
    """
    try:
        cho = [v]
        while cho:
            x = cho.pop()
            if type(x) is dict:
                for k, con in x.items():
                    if k.lower() in _KHOA_CAM or "base64" in k.lower():
                        loi()
                    cho.extend((k, con))
            elif type(x) is list:
                cho.extend(x)
            elif type(x) is str:
                if _CAM.search(x):
                    loi()
                # Không suy ID ngắn là base64. Chuỗi có padding hoặc payload
                # dài đúng bảng mã bị từ chối; SHA/ID có '-' không bị nhầm.
                if (len(x) >= 16 and ("=" in x or len(x) >= 64)
                        and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", x)):
                    try:
                        base64.b64decode(x, validate=True)
                    except ValueError:
                        pass
                    else:
                        loi()
    except (RecursionError, UnicodeError):
        loi()


class DocNguonCore:
    """Bộ đọc một việc, không đệm bền. Giấy cấp là dependency tin cậy riêng."""

    def __init__(self, viec, tran):
        self.viec, self.tran = viec, tran
        self.tong_doc = 0
        self.giay_cap = None
        self.nguon = {}
        self.van_ban = {}

    def kiem_tep(self, tep, *, json=False):
        doi_tuong(tep, ("tep_id", "ten", "mime", "kich_thuoc"), ())
        ma(tep["tep_id"])
        ten = chuoi(tep["ten"])
        if len(ten) > 255 or any(c in ten for c in '/\\:\0') or any(ord(c) < 32 for c in ten):
            loi("TC_SAI_NGUON")
        if type(tep["mime"]) is not str or not _MIME.fullmatch(tep["mime"]):
            loi("TC_SAI_NGUON")
        if json and tep["mime"] != "application/json":
            loi("TC_SAI_NGUON")
        so(tep["kich_thuoc"], 0, nguyen=True)
        if tep["kich_thuoc"] > self.tran["tep_toi_da_byte"]:
            loi("TC_QUA_GIOI_HAN")

    def _doc(self, tep, bam_tep, *, chinh=False):
        self.kiem_tep(tep)
        kiem_bam(bam_tep)
        tran = self.tran["json_chinh_toi_da_byte"] if chinh else self.tran["tep_toi_da_byte"]
        if tep["kich_thuoc"] > tran:
            loi("TC_QUA_GIOI_HAN")
        if not chinh:
            cap = self.giay_cap["tep"].get(tep["tep_id"])
            if cap is None:
                loi("TC_CHUA_CO_CUA_CORE")
            if (json_chuan(cap.get("tep")) != json_chuan(tep)
                    or kiem_bam(cap.get("bam")) != kiem_bam(bam_tep)):
                loi("TC_SAI_NGUON")
            if self.tong_doc + tep["kich_thuoc"] > self.tran["tong_doc_toi_da_byte"]:
                loi("TC_QUA_GIOI_HAN")
        self.viec.kiem_huy()
        try:
            with self.viec.mo_tep(tep["tep_id"]) as f:
                noi_dung = f.read(tran + 1)
        except LoiDuongTruyen as exc:
            if exc.http_status == 413:
                loi("TC_QUA_GIOI_HAN")
            if exc.http_status == 403:
                loi("TC_CHUA_CO_CUA_CORE")
            raise  # SDK xử lý mất lease 404/409/410, hủy và lỗi trao đổi.
        except LoiNghiepVu as exc:
            if exc.ma == "VUOT_GIOI_HAN":
                loi("TC_QUA_GIOI_HAN")
            raise
        self.viec.kiem_huy()
        if not chinh:
            self.tong_doc += len(noi_dung)
        if len(noi_dung) > tran or self.tong_doc > self.tran["tong_doc_toi_da_byte"]:
            loi("TC_QUA_GIOI_HAN")
        if len(noi_dung) != tep["kich_thuoc"] or bam(noi_dung) != kiem_bam(bam_tep):
            loi("TC_SAI_NGUON")
        return noi_dung

    def doc_ref(self, ref, *, json=True):
        doi_tuong(ref, ("tep", "bam"), ())
        self.kiem_tep(ref["tep"], json=json)
        noi_dung = self._doc(ref["tep"], ref["bam"])
        return doc_json(noi_dung) if json else noi_dung

    def tai_nguyen(self, v):
        if type(v) is dict and "tep" in v:
            v = self.doc_ref(v)
        kiem_noi_dung_json(v)
        return v

    def yeu_cau(self, cua_nguon):
        p = self.viec.ngu_canh.get("phap_nhan_id")
        if type(p) is not str or not p.strip():
            loi("TC_THIEU_NGU_CANH")
        dau_vao = doi_tuong(self.viec.dau_vao, ("loai", "tep"), ())
        if dau_vao["loai"] != "tep":
            loi()
        self.kiem_tep(dau_vao["tep"], json=True)
        bam_yc = kiem_bam(self.viec.tham_so.get("bam_yeu_cau"))
        yc = doc_json(self._doc(dau_vao["tep"], bam_yc, chinh=True))
        cac_truong_nc = {"phap_nhan_id", "module", "nhom", "nguoi_hoi_id", "thoi_diem", "ma_pham_vi"}
        if (type(yc) is dict and (type(yc.get("ngu_canh_core")) is not dict
                or not cac_truong_nc <= yc["ngu_canh_core"].keys())):
            loi("TC_THIEU_NGU_CANH")
        doi_tuong(yc, ("phien_ban", "ma_yeu_cau", "tac_vu", "ngu_canh_core", "du_lieu"), ())
        kiem_noi_dung_json(yc)
        if type(yc["phien_ban"]) is not int or yc["phien_ban"] != 1 or yc["tac_vu"] not in TAC_VU:
            loi()
        ma(yc["ma_yeu_cau"])
        nc = doi_tuong(yc["ngu_canh_core"], ("phap_nhan_id", "module", "nhom",
                      "nguoi_hoi_id", "thoi_diem", "ma_pham_vi"), ())
        for k in ("phap_nhan_id", "module", "nguoi_hoi_id", "ma_pham_vi"):
            ma(nc[k])
        ds_nhom = danh_sach(nc["nhom"], 8)
        if not ds_nhom or any(type(n) is not str or n not in {f"{i:02}" for i in range(1, 9)} for n in ds_nhom):
            loi()
        if len(set(ds_nhom)) != len(ds_nhom):
            loi()
        thoi_diem(nc["thoi_diem"])
        if nc["phap_nhan_id"] != p:
            loi("TC_CHUA_CO_CUA_CORE")
        if cua_nguon is None or not callable(getattr(cua_nguon, "doc_quyen", None)):
            loi("TC_CHUA_CO_CUA_CORE")
        # Không truyền payload cho cửa rồi chấp nhận một cờ True trả lại.
        cap = cua_nguon.doc_quyen(self.viec.id)
        if (type(cap) is not dict or type(cap.get("tep")) is not dict
                or type(cap.get("nguon")) is not dict):
            loi("TC_CHUA_CO_CUA_CORE")
        if json_chuan(cap.get("ngu_canh_core")) != json_chuan(nc):
            loi("TC_CHUA_CO_CUA_CORE")
        if (cap.get("ma_yeu_cau") != yc["ma_yeu_cau"] or cap.get("tac_vu") != yc["tac_vu"]
                or kiem_bam(cap.get("bam_yeu_cau")) != bam_yc):
            loi("TC_SAI_NGUON")
        self.giay_cap = deepcopy(cap)
        cap_chinh = cap["tep"].get(dau_vao["tep"]["tep_id"])
        if cap_chinh is None:
            loi("TC_CHUA_CO_CUA_CORE")
        if json_chuan(cap_chinh) != json_chuan({"tep": dau_vao["tep"], "bam": cap["bam_yeu_cau"]}):
            loi("TC_SAI_NGUON")
        return yc

    def kiem_nguon_da_cap(self, n):
        doi_tuong(n, ("ma_nguon", "phien_ban_nguon", "tep_id", "bam_goc", "bam_van_ban"), ())
        for k in ("ma_nguon", "phien_ban_nguon", "tep_id"):
            ma(n[k])
        for k in ("bam_goc", "bam_van_ban"):
            kiem_bam(n[k])
        cap = self.giay_cap["nguon"].get(n["ma_nguon"])
        if cap is None:
            loi("TC_CHUA_CO_CUA_CORE")
        n_chuan = {**n, "bam_goc": n["bam_goc"].lower(), "bam_van_ban": n["bam_van_ban"].lower()}
        if json_chuan(cap) != json_chuan(n_chuan):
            loi("TC_SAI_NGUON")
        return n_chuan

    def tai_lieu(self, n):
        doi_tuong(n, ("ma_nguon", "phien_ban_nguon", "goc", "van_ban"), ())
        ma(n["ma_nguon"])
        ma(n["phien_ban_nguon"])
        # Kiểm phiên bản với nguồn Core trước khi đọc nội dung con.
        cap = self.giay_cap["nguon"].get(n["ma_nguon"])
        if cap is None:
            loi("TC_CHUA_CO_CUA_CORE")
        if cap.get("phien_ban_nguon") != n["phien_ban_nguon"]:
            loi("TC_SAI_NGUON")
        if n["ma_nguon"] in self.nguon:
            loi("TC_SAI_NGUON")
        self.doc_ref(n["goc"], json=False)
        vb = self.doc_ref(n["van_ban"])
        kiem_van_ban(vb, self.tran)
        noi_dung = vb["van_ban_tai_lieu"]
        if kiem_bam(noi_dung["bam_dau_vao"]) != kiem_bam(n["goc"]["bam"]):
            loi("TC_SAI_NGUON")
        nguon = self.kiem_nguon_da_cap({
            "ma_nguon": n["ma_nguon"], "phien_ban_nguon": n["phien_ban_nguon"],
            "tep_id": n["goc"]["tep"]["tep_id"], "bam_goc": n["goc"]["bam"],
            "bam_van_ban": bam(noi_dung["van_ban"].encode("utf-8")),
        })
        self.nguon[n["ma_nguon"]] = {**nguon, "goc": n["goc"], "van_ban": n["van_ban"]}
        self.van_ban[n["ma_nguon"]] = noi_dung
        return {**n, "van_ban_tai_lieu": vb}


def kiem_hop(v):
    if type(v) is not list or len(v) != 4:
        loi("TC_SAI_NGUON")
    for x in v:
        so(x)
    if v[0] > v[2] or v[1] > v[3]:
        loi("TC_SAI_NGUON")


def kiem_van_ban(pb, tran):
    doi_tuong(pb, ("loai", "van_ban_tai_lieu"))
    if pb["loai"] != "van_ban_tai_lieu":
        loi("TC_SAI_NGUON")
    v = doi_tuong(pb["van_ban_tai_lieu"], ("phien_ban", "van_ban", "trang", "nguon_doc",
                     "ly_do_chuyen_nguon", "so_trang", "phien_ban_engine", "bam_dau_vao", "canh_bao"))
    if type(v["phien_ban"]) is not int or v["phien_ban"] != 1:
        loi("TC_SAI_NGUON")
    if type(v["van_ban"]) is not str or not v["van_ban"].strip():
        loi("TC_SAI_NGUON")
    chuoi(v["van_ban"], tran["van_ban_toi_da_ky_tu"])
    so(v["so_trang"], 0, nguyen=True)
    if v["so_trang"] > tran["so_trang_toi_da"]:
        loi("TC_QUA_GIOI_HAN")
    trang = danh_sach(v["trang"], tran["so_trang_toi_da"])
    if len(trang) != v["so_trang"] or v["nguon_doc"] not in {"abbyy", "tesseract", "lop_chu_san", "docx"}:
        loi("TC_SAI_NGUON")
    if v["ly_do_chuyen_nguon"] is not None and type(v["ly_do_chuyen_nguon"]) is not str:
        loi("TC_SAI_NGUON")
    chuoi(v["phien_ban_engine"])
    kiem_bam(v["bam_dau_vao"])
    if any(type(c) is not str for c in danh_sach(v["canh_bao"])):
        loi("TC_SAI_NGUON")
    for i, p in enumerate(trang, 1):
        doi_tuong(p, ("so", "rong", "cao", "don_vi", "khoi"))
        if type(p["so"]) is not int or p["so"] != i:
            loi("TC_SAI_NGUON")
        for k in ("rong", "cao"):
            if so(p[k], 0) == 0:
                loi("TC_SAI_NGUON")
        chuoi(p["don_vi"])
        for khoi in danh_sach(p["khoi"]):
            doi_tuong(khoi, ("loai", "hop"))
            kiem_hop(khoi["hop"])
            if khoi["loai"] == "doan":
                if type(khoi.get("van_ban")) is not str:
                    loi("TC_SAI_NGUON")
                for dong in danh_sach(khoi.get("dong", [])):
                    doi_tuong(dong, ("van_ban", "hop"))
                    kiem_hop(dong["hop"])
                    if type(dong["van_ban"]) is not str:
                        loi("TC_SAI_NGUON")
                    for tu in danh_sach(dong.get("tu", [])):
                        doi_tuong(tu, ("van_ban", "hop"))
                        kiem_hop(tu["hop"])
                        if type(tu["van_ban"]) is not str or ("nghi_ngo" in tu and type(tu["nghi_ngo"]) is not bool):
                            loi("TC_SAI_NGUON")
            elif khoi["loai"] == "bang":
                for o in danh_sach(khoi.get("o")):
                    doi_tuong(o, ("hang", "cot", "gop_hang", "gop_cot", "van_ban"))
                    for k in ("hang", "cot", "gop_hang", "gop_cot"):
                        so(o[k], 1 if k.startswith("gop_") else 0, nguyen=True)
                    if type(o["van_ban"]) is not str:
                        loi("TC_SAI_NGUON")
            else:
                loi("TC_SAI_NGUON")


def kiem_danh_muc(v, tran):
    doi_tuong(v, ("nhom", "loai", "loai_hinh_phap_nhan", "doi_tuong"), ())
    tong = 0
    for ten, ds in v.items():
        danh_sach(ds, tran)
        tong += len(ds)
        cac_ma = []
        for muc in ds:
            doi_tuong(muc, ("ma", "ten"))
            cac_ma.append(ma(muc["ma"]))
            chuoi(muc["ten"])
            if ten == "loai" and muc.get("trang_thai") not in {"hoat_dong", "cho_kich_hoat", "ngung_nhan_moi"}:
                loi()
        if len(set(cac_ma)) != len(cac_ma):
            loi()
    if tong > tran:
        loi("TC_QUA_GIOI_HAN")
    if {n["ma"] for n in v["nhom"]} != {f"{i:02}" for i in range(1, 9)}:
        loi()


def kiem_doan(doc, d):
    doi_tuong(d, ("ma_nguon", "phien_ban_nguon", "bam_goc", "bam_van_ban",
                    "nguyen_van", "bat_dau", "ket_thuc", "vi_tri"))
    n = doc.nguon.get(d["ma_nguon"])
    if n is None:
        loi("TC_SAI_NGUON")
    if (d["phien_ban_nguon"] != n["phien_ban_nguon"]
            or any(kiem_bam(d[k]) != n[k] for k in ("bam_goc", "bam_van_ban"))):
        loi("TC_SAI_NGUON")
    vb = doc.van_ban[d["ma_nguon"]]
    a, z = so(d["bat_dau"], 0, nguyen=True), so(d["ket_thuc"], 0, nguyen=True)
    if not a < z <= len(vb["van_ban"]) or vb["van_ban"][a:z] != d["nguyen_van"]:
        loi("TC_SAI_NGUON")
    vt = doi_tuong(d["vi_tri"], ("trang", "hop"))
    if vt["trang"] is None:
        if vt["hop"] is not None:
            loi("TC_SAI_NGUON")
    else:
        so(vt["trang"], 1, vb["so_trang"], nguyen=True)
        if vt["hop"] is not None:
            kiem_hop(vt["hop"])


def kiem_gia_tri(kieu, v):
    if kieu not in {"van_ban", "so", "so_tien", "ngay", "co_khong", "tep"}:
        loi()
    if v is None:
        return
    if kieu == "so":
        so(v)
    elif kieu == "so_tien":
        doi_tuong(v, ("so", "tien_te"), ())
        # Số tiền float không đủ bảo đảm chính xác; chuỗi thập phân hoặc int.
        if not (type(v["so"]) is int or (type(v["so"]) is str and re.fullmatch(r"-?\d+(?:\.\d+)?", v["so"]))):
            loi()
        if type(v["tien_te"]) is not str or not re.fullmatch(r"[A-Z]{3}", v["tien_te"]):
            loi()
    elif kieu == "ngay":
        try:
            if type(v) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                loi()
            date.fromisoformat(v)
        except ValueError:
            loi()
    elif kieu == "co_khong":
        if type(v) is not bool:
            loi()
    elif kieu == "van_ban":
        if type(v) is not str:
            loi()
    else:
        doi_tuong(v, ("tep_id", "ten", "mime", "kich_thuoc"), ())


def kiem_du_lieu(doc, yc):
    t, ns = yc["tac_vu"], doc.tran
    bat_buoc = {
        "phan_loai": ("tai_lieu", "danh_muc", "phan_loai_cu", "quan_he_phu_luc"),
        "cat_doan": ("tai_lieu", "metadata_core"),
        "phan_tich_cau_hoi": ("cau_hoi", "ham"),
        "xep_hang_lai": ("cau_hoi", "thuc_the", "ung_vien", "nguon", "thang_diem"),
        "soan_tra_loi": ("cau_hoi", "thuc_the", "tang", "bang_chung", "co_van_ban_moi_cho_duyet", "phu_thuoc_cache"),
    }
    tuy_chon = {"cat_doan": {"danh_muc"}, "soan_tra_loi": {"nguon"}}
    d = deepcopy(doi_tuong(yc["du_lieu"], bat_buoc[t], tuy_chon.get(t, set())))
    if "cau_hoi" in d:
        chuoi(d["cau_hoi"], ns["cau_hoi_toi_da_ky_tu"])
    for k in ("danh_muc", "metadata_core", "ham", "ung_vien", "bang_chung",
              "thuc_the", "nguon", "phu_thuoc_cache", "phan_loai_cu", "quan_he_phu_luc"):
        if k in d and d[k] is not None:
            d[k] = doc.tai_nguyen(d[k])
    for k, ngan_sach in (("ham", "so_ham_toi_da"), ("ung_vien", "so_ung_vien_toi_da"),
                        ("bang_chung", "so_ung_vien_toi_da")):
        if k in d:
            danh_sach(d[k], ns[ngan_sach])
    if t == "phan_loai" or d.get("danh_muc") is not None:
        kiem_danh_muc(d["danh_muc"], ns["so_muc_danh_muc_toi_da"])
    for k in ("phan_loai_cu", "quan_he_phu_luc"):
        if d.get(k) is not None:
            doi_tuong(d[k])
    if "tai_lieu" in d:
        d["tai_lieu"] = doc.tai_lieu(d["tai_lieu"])
    if "metadata_core" in d:
        m = doi_tuong(d["metadata_core"], ("nhom", "loai", "trang_thai_duyet", "con_hieu_luc"))
        if m["nhom"] not in yc["ngu_canh_core"]["nhom"]:
            loi("TC_CHUA_CO_CUA_CORE")
        ma(m["loai"])
        if m["trang_thai_duyet"] not in {"da_duyet", "cho_duyet", "tu_choi"} or type(m["con_hieu_luc"]) is not bool:
            loi()
    if "thuc_the" in d:
        for thuc_the in danh_sach(d["thuc_the"]):
            doi_tuong(thuc_the, ("loai", "ma", "gia_tri"))
            ma(thuc_the["loai"])
            ma(thuc_the["ma"])
    if t == "phan_tich_cau_hoi":
        ds = danh_sach(d["ham"], ns["so_ham_toi_da"])
        ten = []
        for h in ds:
            doi_tuong(h, ("ten", "phien_ban", "mo_ta", "schema_tham_so", "schema_dau_ra", "gioi_han", "quyen"))
            ten.append(ma(h["ten"]))
            ma(h["phien_ban"])
            chuoi(h["mo_ta"])
            for k in ("schema_tham_so", "schema_dau_ra", "gioi_han", "quyen"):
                doi_tuong(h[k])
        if len(set(ten)) != len(ten):
            loi()
    if "nguon" in d:
        ds_nguon = danh_sach(d["nguon"])
        if t == "soan_tra_loi" and d["tang"] == 1:
            # QĐ-4: descriptor Core đủ cho tầng 1; không mở lại tệp gốc/OCR.
            d["nguon"] = [doc.kiem_nguon_da_cap(n) for n in ds_nguon]
            for n in d["nguon"]:
                if n["ma_nguon"] in doc.nguon:
                    loi("TC_SAI_NGUON")
                doc.nguon[n["ma_nguon"]] = n
        else:
            d["nguon"] = [doc.tai_lieu(n) for n in ds_nguon]
    if t == "xep_hang_lai":
        ds = danh_sach(d["ung_vien"], ns["so_ung_vien_toi_da"])
        thang = doi_tuong(d["thang_diem"], ("toi_thieu", "toi_da"), ())
        so(thang["toi_thieu"])
        so(thang["toi_da"], thang["toi_thieu"])
        cac_ma = []
        for uv in ds:
            kiem_doan(doc, uv)
            cac_ma.append(ma(uv.get("ma_ung_vien")))
            so(uv.get("diem_tim_kiem"), thang["toi_thieu"], thang["toi_da"])
        if len(set(cac_ma)) != len(cac_ma):
            loi("TC_SAI_NGUON")
    if t == "soan_tra_loi":
        so(d["tang"], 1, 3, nguyen=True)
        if type(d["co_van_ban_moi_cho_duyet"]) is not bool:
            loi()
        for bc in danh_sach(d["bang_chung"], ns["so_ung_vien_toi_da"]):
            if d["tang"] == 1:
                doi_tuong(bc, ("nguon", "thuc_the", "truong", "kieu", "gia_tri", "don_vi",
                               "trang_thai_duyet", "con_hieu_luc", "do_tin_cay", "moc_cong_bo"))
                n = doc.kiem_nguon_da_cap(bc["nguon"])
                doc.nguon[n["ma_nguon"]] = n
                ma(bc["truong"])
                kiem_gia_tri(bc["kieu"], bc["gia_tri"])
                if bc["trang_thai_duyet"] not in {"da_duyet", "cho_duyet", "tu_choi"} or type(bc["con_hieu_luc"]) is not bool:
                    loi()
                so(bc["do_tin_cay"], 0, 1)
                thoi_diem(bc["moc_cong_bo"])
            else:
                kiem_doan(doc, bc)
        for phu_thuoc in danh_sach(d["phu_thuoc_cache"]):
            doi_tuong(phu_thuoc, ("nguon", "thuc_the", "trang_thai_duyet", "moc_cong_bo",
                                  "ma_pham_vi", "phu_thuoc_thoi_diem"))
            doc.kiem_nguon_da_cap(phu_thuoc["nguon"])
            if (phu_thuoc["ma_pham_vi"] != yc["ngu_canh_core"]["ma_pham_vi"]
                    or type(phu_thuoc["phu_thuoc_thoi_diem"]) is not bool):
                loi("TC_CHUA_CO_CUA_CORE")
            thoi_diem(phu_thuoc["moc_cong_bo"])
    doc.viec.kiem_huy()
    return d
