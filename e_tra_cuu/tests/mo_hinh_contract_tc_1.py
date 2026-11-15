"""Mô hình đặc tả TC-1 CHỈ trong tests; không phải handler/validator chung.

CoreGia giữ bytes thật. Quyền/metadata cấp qua adapter test độc lập với payload;
không chứng nhận RLS Core thật. TC-2…7 phải triển khai kiểm miền riêng.
"""

from copy import deepcopy
from hashlib import sha256
import json
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia


GIAI_DOAN = {
    "phan_loai": {"da_nhan", "cho_ai", "cho_phan_loai", "da_phan_loai"},
    "cat_doan": {"da_nhan", "da_cat_doan"},
    "phan_tich_cau_hoi": {"da_nhan", "cho_ai", "da_phan_tich"},
    "xep_hang_lai": {"da_nhan", "cho_ai", "da_xep_hang"},
    "soan_tra_loi": {"da_nhan", "cho_ai", "da_soan"},
}
CAU_LOI = {
    "TC_SAI_NGUON": "Chưa kiểm chứng được nguồn tra cứu. Anh gửi lại yêu cầu từ hồ sơ được cấp quyền.",
    "TC_SAI_GIAI_DOAN": "Hồ sơ chưa ở đúng bước xử lý. Anh chạy lại từ bước nhận yêu cầu.",
    "TC_THIEU_NGU_CANH": "Chưa đủ ngữ cảnh tra cứu. Anh gửi lại yêu cầu từ hồ sơ.",
    "TC_QUA_GIOI_HAN": "Yêu cầu vượt giới hạn xử lý. Anh chia lại hồ sơ trước khi gửi.",
    "TC_DAU_VAO_KHONG_HOP_LE": "Yêu cầu tra cứu không hợp lệ. Anh kiểm tra lại hồ sơ.",
}


def loi(ma):
    raise LoiNghiepVu(ma, CAU_LOI[ma])


def kiem_giai_doan(tac_vu, giai_doan):
    if giai_doan not in GIAI_DOAN.get(tac_vu, set()):
        loi("TC_SAI_GIAI_DOAN")


def json_chuan(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def bam(b):
    return "sha256:" + sha256(b).hexdigest()


def doc_json(b):
    def cap(pairs):
        kq = {}
        for k, v in pairs:
            if k in kq:
                raise ValueError("Khóa trùng")
            kq[k] = v
        return kq

    def cam_hang(v):
        raise ValueError("Số không hữu hạn")

    try:
        v = json.loads(b.decode("utf-8"), object_pairs_hook=cap, parse_constant=cam_hang)
        json_chuan(v)  # kiểm surrogate và số overflow như 1e999
        return v
    except (ValueError, UnicodeError):
        loi("TC_DAU_VAO_KHONG_HOP_LE")


def kiem_schema_moi(v, s, goc):
    """Chỉ tập từ khóa schema TC-1; không dùng cho ba schema chung/runtime."""
    tu_khoa = {"$schema", "$id", "$comment", "title", "description", "$defs",
               "$ref", "type", "required", "properties", "additionalProperties",
               "const", "enum", "minLength", "pattern", "minimum", "maximum",
               "items", "oneOf"}
    assert s.keys() <= tu_khoa, "Từ khóa ngoài bộ đánh giá test TC-1"
    if "$ref" in s:
        assert s["$ref"].startswith("#/$defs/")
        kiem_schema_moi(v, goc["$defs"][s["$ref"].split("/")[-1]], goc)
    if "type" in s:
        cac_kieu = s["type"] if isinstance(s["type"], list) else [s["type"]]
        # Schema mới chỉ dùng integer, không number; không coi bool là int.
        kieu = {dict: "object", list: "array", str: "string", int: "integer",
                bool: "boolean", type(None): "null"}.get(type(v))
        assert kieu in cac_kieu
    if "oneOf" in s:
        dat = 0
        for con in s["oneOf"]:
            try:
                kiem_schema_moi(v, con, goc)
                dat += 1
            except AssertionError:
                pass
        assert dat == 1
    for k in ("const", "enum"):
        if k in s:
            tap = s[k] if k == "enum" else [s[k]]
            assert any(type(v) is type(x) and v == x for x in tap)
    if isinstance(v, str):
        assert len(v) >= s.get("minLength", 0)
        if "pattern" in s:
            assert re.search(s["pattern"], v)
    if type(v) is int:
        assert v >= s.get("minimum", v)
        assert v <= s.get("maximum", v)
    if type(v) is dict:
        assert set(s.get("required", [])) <= v.keys()
        for k, con in s.get("properties", {}).items():
            if k in v:
                kiem_schema_moi(v[k], con, goc)
    if type(v) is list and "items" in s:
        for x in v:
            kiem_schema_moi(x, s["items"], goc)


class KhoCoreGia:
    """Quyền giả do test cấp ngoài phong bì; không fallback cho engine."""

    def __init__(self):
        self.core = CoreGia()
        self.cap_quyen = {}
        self.tong_doc = 0

    def tai(self, ten, b, phap_nhan="DEMO-P", mime="application/json"):
        tep = self.core.them_tep(ten, b, mime)
        self.cap_quyen[tep["tep_id"]] = (deepcopy(tep), phap_nhan)
        return {"tep": tep, "bam": bam(b)}

    def mo(self, ref, phap_nhan):
        tep = ref["tep"]
        if tep["kich_thuoc"] > 20 * 1024**2:
            loi("TC_QUA_GIOI_HAN")
        try:
            metadata, p = self.cap_quyen[tep["tep_id"]]
        except KeyError:
            loi("TC_SAI_NGUON")
        if metadata != tep or p != phap_nhan:
            loi("TC_SAI_NGUON")
        b = self.core.doc_tep(tep["tep_id"])
        self.tong_doc += len(b)
        if len(b) > 20 * 1024**2 or self.tong_doc > 64 * 1024**2:
            loi("TC_QUA_GIOI_HAN")
        if len(b) != tep["kich_thuoc"] or bam(b).lower() != ref["bam"].lower():
            loi("TC_SAI_NGUON")
        return b


def fixture_cat_doan():
    kho = KhoCoreGia()
    van_ban = "DEMO Công ty Ánh Dương\nGiá trị 1.000.000 VND, ngày 2026-10-30."
    goc = kho.tai("nguon-DEMO.txt", van_ban.encode("utf-8"), mime="text/plain")
    phong_bi_vb = {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
        "phien_ban": 1, "van_ban": van_ban, "so_trang": 0, "trang": [],
        "nguon_doc": "docx", "ly_do_chuyen_nguon": None,
        "phien_ban_engine": "e_ocr 0.1.0", "bam_dau_vao": goc["bam"], "canh_bao": [],
    }}
    vb = kho.tai("van-ban-DEMO.json", json_chuan(phong_bi_vb))
    cau_hinh = {"phien_ban": 1, "cat_doan": {"do_dai_muc_tieu": 2000}}
    snapshot = {
        "phien_ban": 1, "ma_yeu_cau": "DEMO-YC-1", "tac_vu": "cat_doan",
        "giai_doan": "da_cat_doan",
        "ngu_canh_core": {"phap_nhan_id": "DEMO-P", "module": "DEMO-M",
            "nhom": ["02"], "nguoi_hoi_id": "DEMO-N", "ma_pham_vi": "DEMO-PV",
            "thoi_diem": "2026-11-15T12:36:00+07:00"},
        "cau_hinh": {"gia_tri": cau_hinh, "row_version": 1},
        "nguon": [{"ma_nguon": "DEMO-NGUON-1", "phien_ban_nguon": "1",
                   "goc": goc, "van_ban": vb}],
        "du_lieu": {"metadata_core": {"nhom": "02", "loai": "DEMO-LOAI",
                     "trang_thai_duyet": "da_duyet", "con_hieu_luc": True}},
        "ket_qua": {"doan": [{"ma_doan": "DEMO-DOAN-1", "ma_nguon": "DEMO-NGUON-1",
            "nguyen_van": van_ban, "bat_dau": 0, "ket_thuc": len(van_ban),
            "trang": None, "hop": None}]},
    }
    ref = kho.tai("snapshot-DEMO.json", json_chuan(snapshot))
    phong_bi = {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": {
        "phien_ban": 1, "ma_yeu_cau": snapshot["ma_yeu_cau"], "tac_vu": "cat_doan",
        "giai_doan": "da_cat_doan", "ho_so": ref["tep"], "bam_ho_so": ref["bam"],
        "bam_cau_hinh": bam(json_chuan(cau_hinh)), "bam_danh_muc": None,
        "phien_ban_engine": "e_tra_cuu 0.1.0", "canh_bao": [],
        "tom_tat": {"trang_thai": "da_cat_doan", "so_doan": 1, "so_ung_vien": None,
                    "tang": None, "co_can_cu": None, "co_mau_thuan": None,
                    "can_duyet": None, "nhan": None},
    }}
    return kho, phong_bi, snapshot


def kiem_quan_he(kho, phong_bi, ngu_canh):
    """Ví dụ thực thi quan hệ TC-1 cho hồ sơ cắt đoạn; không handler runtime."""
    p = ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if len(json_chuan(phong_bi)) > 65536:
        loi("TC_QUA_GIOI_HAN")
    h = phong_bi["ho_so_tra_cuu"]
    kiem_giai_doan(h["tac_vu"], h["giai_doan"])
    s = doc_json(kho.mo({"tep": h["ho_so"], "bam": h["bam_ho_so"]}, p))
    if s["ngu_canh_core"]["phap_nhan_id"] != p:
        loi("TC_SAI_NGUON")
    if any(h[k] != s[k] for k in ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan")):
        loi("TC_SAI_NGUON")
    if bam(json_chuan(s["cau_hinh"]["gia_tri"])) != h["bam_cau_hinh"]:
        loi("TC_SAI_NGUON")
    dm = s["du_lieu"].get("danh_muc")
    if h["bam_danh_muc"] != (bam(json_chuan(dm)) if dm is not None else None):
        loi("TC_SAI_NGUON")
    if h["tac_vu"] == "xep_hang_lai" and h["giai_doan"] == "da_xep_hang":
        ds = s["du_lieu"]["ung_vien"]
        xh = s["ket_qua"]["xep_hang"]
        ma_nguon = {x["ma_ung_vien"]: x["ma_nguon"] for x in ds}
        ma_xh = [x["ma_ung_vien"] for x in xh]
        if (h["tom_tat"]["so_ung_vien"] != len(ds)
                or len(ma_nguon) != len(ds) or len(set(ma_xh)) != len(ma_xh)
                or set(ma_xh) != set(ma_nguon)
                or any(x["ma_nguon"] != ma_nguon.get(x["ma_ung_vien"]) for x in xh)):
            loi("TC_SAI_NGUON")
    if h["tac_vu"] == "cat_doan" and h["giai_doan"] == "da_cat_doan":
        ds = s["ket_qua"]["doan"]
        if len(ds) > 5000:
            loi("TC_QUA_GIOI_HAN")
        if h["tom_tat"]["so_doan"] != len(ds) or h["tom_tat"]["trang_thai"] != "da_cat_doan":
            loi("TC_SAI_NGUON")
        nguon = {}
        for n in s["nguon"]:
            goc = kho.mo(n["goc"], p)
            vb = doc_json(kho.mo(n["van_ban"], p))["van_ban_tai_lieu"]
            if vb["bam_dau_vao"] != bam(goc):
                loi("TC_SAI_NGUON")
            nguon[n["ma_nguon"]] = vb["van_ban"]
        for d in ds:
            a, z = d["bat_dau"], d["ket_thuc"]
            vb = nguon.get(d["ma_nguon"])
            if vb is None or not 0 <= a < z <= len(vb) or vb[a:z] != d["nguyen_van"]:
                loi("TC_SAI_NGUON")
    return s
