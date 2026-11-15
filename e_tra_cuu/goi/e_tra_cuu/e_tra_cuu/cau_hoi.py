"""TC-6: hậu kiểm Local không tin cậy; không thực thi hàm module.

Cửa doc_quyen vẫn là dependency CHƯA có ở Core/SDK thật. Metadata phân giải
chỉ lấy từ cửa này, không từ phản hồi/model/cờ JSON của người gửi.
"""

from calendar import monthrange
from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation, localcontext
import math
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .chuan_bi_ai import _bo_van_ban_da_nap, kiem_tham_so
from .kiem_dau_vao import (DocNguonCore, bam, doi_tuong, json_chuan, kiem_bam,
                          kiem_du_lieu, loi, thoi_diem)
from .ngu_canh_ai import dung_khuon, dung_ngu_canh, kiem_ngan_sach, qua_ngan_sach


_TRAN_DOC = {"tep_toi_da_byte": 20971520, "tong_doc_toi_da_byte": 67108864,
             "ho_so_toi_da_byte": 65536}
_TOM_TAT = ("trang_thai", "so_doan", "so_ung_vien", "tang", "co_can_cu",
            "co_mau_thuan", "can_duyet", "nhan")
_THOI_DIEM = re.compile(
    r"(?<!\w)(?:hiện nay|hiện tại|hiện hành|hôm nay|bây giờ|lúc này|tháng này|"
    r"tuần này|quý này|năm nay|năm này|sắp đáo hạn|sắp đến hạn|mới nhất)(?!\w)", re.I)
_LENH_CAM = re.compile(
    r"[a-z][a-z0-9+.-]*://|\b(?:select\b[\s\S]*?\bfrom|insert\s+into|"
    r"update\b[\s\S]*?\bset|delete\s+from|drop\s+table|exec(?:ute)?\s*\(|"
    r"eval\s*\(|__import__|import\s+\w|lambda\b|def\s+\w|file:|data:)", re.I)
_KHOA_CAM = {"sql", "code", "url", "uri", "path", "duong_dan", "ma_thuc_thi", "base64"}


def sai_khuon():
    raise LoiNghiepVu("TC_AI_SAI_KHUON", "Phản hồi AI chưa đúng khuôn hoặc căn cứ tra cứu. Anh thử lại từ hồ sơ.")


def ham_khong_duoc_phep():
    raise LoiNghiepVu("TC_HAM_KHONG_DUOC_PHEP", "Hàm hoặc tham số tra cứu chưa được Core cho phép. Anh kiểm tra lại yêu cầu.")


def _json_ai(v):
    try:
        return json_chuan(v)
    except LoiNghiepVu:
        sai_khuon()


def _bang_gia_tri(a, b):
    """So giá trị JSON: bool khác số; không ép chuỗi mã thành số."""
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(_bang_gia_tri(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(_bang_gia_tri(x, y) for x, y in zip(a, b))
    return a == b


def khop_khuon(v, s, *, goc=None, kiem_huy=lambda: None, sau=0, dong_object=False):
    """Kiểm đúng tập từ khóa TC-4 đã ghim; không validator Draft tổng quát.

    Không tải ref, không gọi engine khác. Từ khóa lạ/schema hỏng thất bại đóng.
    Kiểm thêm miền/hàm/thực thể sau khuôn; schema không chứng minh nghiệp vụ.
    """
    kiem_huy()
    if sau > 64:
        return False
    if type(s) is bool:
        return s and not (dong_object and type(v) is dict and v)
    if type(s) is not dict:
        return False
    goc = s if goc is None else goc
    tu_khoa = {"$schema", "$id", "$defs", "$ref", "$comment", "title", "description", "default", "examples",
               "type", "enum", "const", "properties", "required", "additionalProperties", "items",
               "prefixItems", "minItems", "maxItems", "uniqueItems", "minLength", "maxLength",
               "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
               "minProperties", "maxProperties", "allOf", "anyOf", "oneOf", "not"}
    if not s.keys() <= tu_khoa:
        return False

    def khop(con, schema):
        return khop_khuon(con, schema, goc=goc, kiem_huy=kiem_huy, sau=sau + 1,
                          dong_object=dong_object)

    if "$ref" in s:
        ref = s["$ref"]
        if type(ref) is not str or not ref.startswith("#/") or re.search(r"~(?![01])", ref):
            return False
        dich = goc
        try:
            for k in ref[2:].split("/"):
                k = k.replace("~1", "/").replace("~0", "~")
                dich = dich[int(k)] if type(dich) is list else dich[k]
        except (KeyError, IndexError, ValueError, TypeError):
            return False
        if not khop(v, dich):
            return False
    kieu = {"object": type(v) is dict, "array": type(v) is list, "string": type(v) is str,
            "integer": type(v) is int or (type(v) is float and math.isfinite(v) and v.is_integer()),
            "number": type(v) in (int, float) and (type(v) is int or math.isfinite(v)),
            "boolean": type(v) is bool, "null": v is None}
    if "type" in s:
        ds = s["type"] if type(s["type"]) is list else [s["type"]]
        if not ds or any(type(k) is not str or k not in kieu for k in ds) or not any(kieu[k] for k in ds):
            return False
    if "const" in s and not _bang_gia_tri(v, s["const"]):
        return False
    if "enum" in s and (type(s["enum"]) is not list or not any(_bang_gia_tri(v, x) for x in s["enum"])):
        return False
    for ten in ("allOf", "anyOf", "oneOf"):
        if ten in s:
            if type(s[ten]) is not list or not s[ten]:
                return False
            so_dat = sum(khop(v, x) for x in s[ten])
            if (ten == "allOf" and so_dat != len(s[ten])) or (ten == "anyOf" and not so_dat) or (ten == "oneOf" and so_dat != 1):
                return False
    if "not" in s and khop(v, s["not"]):
        return False
    if type(v) in (int, float):
        if type(v) is float and not math.isfinite(v):
            return False
        for k, dat in (("minimum", lambda a, b: a >= b), ("maximum", lambda a, b: a <= b),
                       ("exclusiveMinimum", lambda a, b: a > b), ("exclusiveMaximum", lambda a, b: a < b)):
            if k in s and (type(s[k]) not in (int, float) or not dat(v, s[k])):
                return False
        if "multipleOf" in s:
            m = s["multipleOf"]
            if type(m) not in (int, float) or m <= 0:
                return False
            try:
                with localcontext() as ctx:
                    ctx.prec = max(len(str(v)), len(str(m))) + 512
                    if Decimal(str(v)) % Decimal(str(m)) != 0:
                        return False
            except InvalidOperation:
                return False
    for ten, dung in (("string", type(v) is str), ("array", type(v) is list), ("object", type(v) is dict)):
        if dung:
            nho, lon = {"string": ("minLength", "maxLength"), "array": ("minItems", "maxItems"),
                        "object": ("minProperties", "maxProperties")}[ten]
            for k in (nho, lon):
                if k in s and (type(s[k]) is not int or s[k] < 0):
                    return False
            if len(v) < s.get(nho, 0) or (lon in s and len(v) > s[lon]):
                return False
    if type(v) is dict:
        props, required = s.get("properties", {}), s.get("required", [])
        if type(props) is not dict or type(required) is not list or any(type(k) is not str for k in required):
            return False
        if not set(required) <= v.keys():
            return False
        # Ref/combinator tự kiểm tại nhánh đã resolve; const/enum khai nguyên
        # giá trị. Không để type dạng mảng/boolean mở nhận khóa tham số thừa.
        if (dong_object and not v.keys() <= props.keys()
                and not any(k in s for k in ("$ref", "allOf", "anyOf", "oneOf", "const", "enum"))):
            return False
        for k, con in v.items():
            if not khop(con, props.get(k, s.get("additionalProperties", True))):
                return False
    if type(v) is list:
        prefix = s.get("prefixItems", [])
        if type(prefix) is not list or ("uniqueItems" in s and type(s["uniqueItems"]) is not bool):
            return False
        if s.get("uniqueItems") and any(_bang_gia_tri(x, y) for i, x in enumerate(v) for y in v[:i]):
            return False
        for i, con in enumerate(v):
            if not khop(con, prefix[i] if i < len(prefix) else s.get("items", True)):
                return False
    return True


def doc_phan_hoi(viec, cua, phien_ban, kiem_cau_hinh, tac_vu):
    """Đọc lại snapshot/quyền và tái dựng nguyên yêu cầu TC-4 trước hậu kiểm."""
    viec.kiem_huy()
    pb = viec.dau_vao
    raw = _json_ai(pb)
    if len(raw) > _TRAN_DOC["tep_toi_da_byte"] or len(raw.decode("utf-8")) > 500000:
        loi("TC_QUA_GIOI_HAN")
    if type(pb) is not dict or set(pb) != {"loai", "tra_loi_ai"} or pb["loai"] != "tra_loi_ai":
        sai_khuon()
    a = pb["tra_loi_ai"]
    truong = {"phien_ban", "trang_thai", "tra_loi", "du_lieu", "trich_dan", "kiem_trich_dan",
              "nha_cung_cap", "model", "ly_do_chon_model", "ma_prompt", "phien_ban_prompt",
              "phien_ban_engine", "bam_dau_vao", "chuyen_tiep", "canh_bao"}
    if type(a) is not dict or set(a) != truong or type(a["phien_ban"]) is not int or a["phien_ban"] != 1:
        sai_khuon()
    if a["nha_cung_cap"] == "cloud":
        raise LoiNghiepVu("TC_CHI_LOCAL", "Tra cứu hiện chỉ nhận phản hồi Local AI. Anh kiểm tra lại quy trình.")
    if a["nha_cung_cap"] != "local":
        loi("TC_SAI_NGUON")
    for k in ("tra_loi", "model", "ly_do_chon_model", "phien_ban_engine"):
        if type(a[k]) is not str or not a[k].strip():
            sai_khuon()
    if not re.fullmatch(r"e_hoi_ai \d+\.\d+\.\d+", a["phien_ban_engine"]):
        loi("TC_SAI_NGUON")
    ct = doi_tuong(a["chuyen_tiep"], ("tra_cuu",), ())
    c = doi_tuong(ct["tra_cuu"], ("phien_ban", "ma_yeu_cau", "tac_vu", "ho_so", "bam_ho_so",
                                  "bam_cau_hinh", "bam_ngu_canh_ai"), ())
    if type(c["phien_ban"]) is not int or c["phien_ban"] != 1 or c["tac_vu"] != tac_vu:
        loi("TC_SAI_NGUON")
    if viec.tham_so:
        sai_khuon()
    p = viec.ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if cua is None or not callable(getattr(cua, "doc_quyen", None)):
        loi("TC_CHUA_CO_CUA_CORE")
    cap = cua.doc_quyen(viec.id)
    if type(cap) is not dict or any(type(cap.get(k)) is not dict for k in ("tep", "nguon", "dau_vao", "ngu_canh_core")):
        loi("TC_CHUA_CO_CUA_CORE")
    if (json_chuan(cap["dau_vao"]) != _json_ai(pb) or cap.get("ma_yeu_cau") != c["ma_yeu_cau"]
            or cap.get("tac_vu") != tac_vu or cap["ngu_canh_core"].get("phap_nhan_id") != p):
        loi("TC_SAI_NGUON")
    doc = DocNguonCore(viec, _TRAN_DOC.copy())
    doc.giay_cap = deepcopy(cap)
    s = doc.doc_ref({"tep": c["ho_so"], "bam": c["bam_ho_so"]})
    doi_tuong(s, ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ngu_canh_core", "cau_hinh",
                   "nguon", "du_lieu", "ket_qua", "ai"), ())
    if (type(s["phien_ban"]) is not int or s["phien_ban"] != 1 or s["ma_yeu_cau"] != c["ma_yeu_cau"]
            or s["tac_vu"] != tac_vu or s["ket_qua"] is not None):
        loi("TC_SAI_NGUON")
    if s["giai_doan"] != "cho_ai":
        loi("TC_SAI_GIAI_DOAN")
    if json_chuan(s["ngu_canh_core"]) != json_chuan(cap["ngu_canh_core"]):
        loi("TC_SAI_NGUON")
    ch = kiem_cau_hinh(s["cau_hinh"])
    if (json_chuan(ch) != json_chuan(s["cau_hinh"])
            or bam(json_chuan(ch["gia_tri"])) != kiem_bam(c["bam_cau_hinh"])):
        loi("TC_SAI_NGUON")
    doc.tran = ch["gia_tri"]["ngan_sach"]
    if c["ho_so"]["kich_thuoc"] > doc.tran["tep_toi_da_byte"] or doc.tong_doc > doc.tran["tong_doc_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    if len(_json_ai(ct)) > doc.tran["chuyen_tiep_toi_da_byte"]:
        qua_ngan_sach()
    kiem_ngan_sach(s["du_lieu"], doc.tran)
    d = deepcopy(s["du_lieu"])
    if "nguon" in d:
        d["nguon"] = [_bo_van_ban_da_nap(n) for n in d["nguon"]]
    da_kiem = kiem_du_lieu(doc, {"tac_vu": tac_vu, "du_lieu": d, "ngu_canh_core": s["ngu_canh_core"]})
    if (json_chuan(da_kiem) != json_chuan(s["du_lieu"])
            or json_chuan(list(doc.nguon.values())) != json_chuan(s["nguon"])):
        loi("TC_SAI_NGUON")
    ai = doi_tuong(s["ai"], ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien", "khuon_tra_loi",
                            "tai_lieu", "map_nguon", "doan", "bam_ngu_canh_ai", "ngan_sach"), ())
    ts = kiem_tham_so({**{k: ai[k] for k in ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien")},
                      "tac_vu": tac_vu}, tac_vu)
    tl, maps, doan = dung_ngu_canh(s, viec)
    khuon = dung_khuon(s)
    ngan_sach_ai = {"so_ky_tu": len(tl), "so_byte_utf8": len(tl.encode("utf-8")),
                   "khuon_byte": len(json_chuan(khuon)), "token_thuc": None, "trang_thai_token": "chua_do"}
    if len(tl) > doc.tran["ai_toi_da_ky_tu"] or len(json_chuan(khuon)) > doc.tran["khuon_toi_da_byte"]:
        qua_ngan_sach()
    if (ai["tai_lieu"] != tl or json_chuan(ai["map_nguon"]) != json_chuan(maps)
            or json_chuan(ai["doan"]) != json_chuan(doan)
            or json_chuan(ai["ngan_sach"]) != json_chuan(ngan_sach_ai)
            or json_chuan(ai["khuon_tra_loi"]) != json_chuan(khuon)
            or kiem_bam(ai["bam_ngu_canh_ai"]) != bam(tl.encode("utf-8"))
            or kiem_bam(c["bam_ngu_canh_ai"]) != kiem_bam(ai["bam_ngu_canh_ai"])):
        loi("TC_SAI_NGUON")
    yc = {"loai": "yeu_cau_ai", "yeu_cau_ai": {"phien_ban": 1, **ts, "tai_lieu": tl,
          "khuon_tra_loi": khuon, "bat_buoc_trich_dan": True, "chuyen_tiep": ct}}
    if (a["ma_prompt"] != ai["ma_prompt"] or a["phien_ban_prompt"] != ai["phien_ban_prompt"]
            or kiem_bam(a["bam_dau_vao"]) != bam(json_chuan(yc))):
        loi("TC_SAI_NGUON")
    if (a["trang_thai"] not in {"co_can_cu", "khong_thay_can_cu"}
            or type(a["canh_bao"]) is not list or any(type(x) is not str for x in a["canh_bao"])):
        sai_khuon()
    kt = a["kiem_trich_dan"]
    if (type(kt) is not dict or set(kt) != {"dat", "loi"} or type(kt["dat"]) is not bool
            or type(kt["loi"]) is not list or any(type(x) is not str for x in kt["loi"])):
        sai_khuon()
    # Không lấy cờ dat làm bằng chứng. Cờ thất bại cũng không được biến thành XONG rỗng.
    if not kt["dat"] or kt["loi"] or a["trang_thai"] != "co_can_cu":
        sai_khuon()
    if type(a["trich_dan"]) is not list or not a["trich_dan"]:
        sai_khuon()
    for q in a["trich_dan"]:
        viec.kiem_huy()
        if type(q) is not dict or set(q) != {"cau", "bat_dau", "ket_thuc"}:
            sai_khuon()
        x, z = q["bat_dau"], q["ket_thuc"]
        if (type(x) is not int or type(z) is not int or not 0 <= x < z <= len(tl)
                or type(q["cau"]) is not str or q["cau"] != tl[x:z]
                or not any(m["ai_bat_dau"] <= x < z <= m["ai_ket_thuc"] for m in maps)):
            sai_khuon()
    _json_ai(a["du_lieu"])
    return s, doc, cap, a


def luu_ket_qua(viec, s, doc, ket_qua, giai_doan, phien_ban, *, canh_bao=()):
    """Chỉ trả hồ sơ khi Core đã xác nhận upload; không tệp/cache/log cục bộ."""
    s = deepcopy(s)
    s.update(giai_doan=giai_doan, ket_qua=ket_qua)
    raw = json_chuan(s)
    if len(raw) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    tt = dict.fromkeys(_TOM_TAT)
    tt["trang_thai"] = giai_doan
    if s["tac_vu"] == "xep_hang_lai":
        tt["so_ung_vien"] = len(s["du_lieu"]["ung_vien"])
    h = {"phien_ban": 1, "ma_yeu_cau": s["ma_yeu_cau"], "tac_vu": s["tac_vu"],
         "giai_doan": giai_doan, "ho_so": None, "bam_ho_so": bam(raw),
         "bam_cau_hinh": bam(json_chuan(s["cau_hinh"]["gia_tri"])), "bam_danh_muc": None,
         "phien_ban_engine": "e_tra_cuu " + phien_ban, "tom_tat": tt, "canh_bao": list(canh_bao)}
    pb = {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": h}
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    viec.tien_do(90, "Đang gửi kết quả hậu kiểm tra cứu lên Core.")
    tep = viec.tai_tep_ra("ho-so-hau-kiem.json", raw, "application/json")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ho-so-hau-kiem.json" or tep["kich_thuoc"] != len(raw):
        loi("TC_SAI_NGUON")
    h["ho_so"] = tep
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    return pb


def phu_thuoc(s, thuc_the, phu_thuoc_thoi_diem, *, ham=()):
    return {"nguon": deepcopy(s["nguon"]), "thuc_the": deepcopy(thuc_the),
            "ngu_canh_core": deepcopy(s["ngu_canh_core"]), "ham": deepcopy(list(ham)),
            "phu_thuoc_thoi_diem": phu_thuoc_thoi_diem,
            "duoc_tai_dung_cache": False if phu_thuoc_thoi_diem else None}


def _vi_tri_dau(chu, cum, *, flags=0):
    # Không NFC/NFD/casefold mã; không lấy A là một phần AB hoặc bỏ số 0 đầu.
    # Một căn cứ cho mỗi thực thể/cụm ý định; không nhân tích danh mục × số
    # lần lặp trong câu hỏi thành hàng triệu bản sao chứng cứ trong RAM.
    m = re.search(r"(?<![\w-])" + re.escape(cum) + r"(?![\w-])", chu, flags)
    return [(m.start(), m.end())] if m else []


def _phan_giai(s, cap, viec):
    c = cap.get("phan_giai_cau_hoi")
    if type(c) is not dict or set(c) != {"bam_cau_hoi", "thuc_the", "y_dinh", "can_lam_ro", "ham"}:
        loi("TC_CHUA_CO_CUA_CORE")
    if len(json_chuan(c)) > 65536:
        loi("TC_QUA_GIOI_HAN")
    q = s["du_lieu"]["cau_hoi"]
    if kiem_bam(c["bam_cau_hoi"]) != bam(q.encode("utf-8")):
        loi("TC_SAI_NGUON")
    if type(c["can_lam_ro"]) is not bool or type(c["ham"]) is not dict:
        loi("TC_CHUA_CO_CUA_CORE")
    for ten in ("thuc_the", "y_dinh"):
        if type(c[ten]) is not list or len(c[ten]) > 1000:
            loi("TC_QUA_GIOI_HAN")
    thuc_the, can_cu, da_gap = [], [], set()
    for x in c["thuc_the"]:
        viec.kiem_huy()
        if type(x) is not dict or set(x) != {"loai", "ma", "gia_tri"} or any(type(v) is not str or not v.strip() for v in x.values()):
            loi("TC_CHUA_CO_CUA_CORE")
        dinh_danh = (x["loai"], x["ma"])
        if dinh_danh in da_gap:
            loi("TC_SAI_NGUON")
        da_gap.add(dinh_danh)
        vi_tri = _vi_tri_dau(q, x["gia_tri"])
        if vi_tri:
            thuc_the.append(deepcopy(x))
            can_cu.extend({"thuc_the": deepcopy(x), "cau": q[a:z], "bat_dau": a, "ket_thuc": z} for a, z in vi_tri)
    y_dinh, da_gap = [], set()
    for x in c["y_dinh"]:
        viec.kiem_huy()
        if (type(x) is not dict or set(x) != {"ma", "cum_tu", "phu_thuoc_thoi_diem"}
                or type(x["ma"]) is not str or not x["ma"].strip() or type(x["cum_tu"]) is not list
                or not x["cum_tu"] or any(type(v) is not str or not v.strip() for v in x["cum_tu"])
                or type(x["phu_thuoc_thoi_diem"]) is not bool or x["ma"] in da_gap):
            loi("TC_CHUA_CO_CUA_CORE")
        da_gap.add(x["ma"])
        vi_tri = [(a, z) for cum in x["cum_tu"] for a, z in _vi_tri_dau(q, cum, flags=re.I)]
        if vi_tri:
            y_dinh.append((x, vi_tri))
    nhom = [x["loai"] for x in thuc_the]
    vi_tri = [(x["bat_dau"], x["ket_thuc"]) for x in can_cu]
    can_lam_ro = (c["can_lam_ro"] or not thuc_the or len(nhom) != len(set(nhom))
                  or len(vi_tri) != len(set(vi_tri)) or len(y_dinh) != 1)
    moc_truoc = 0
    for x in sorted(can_cu, key=lambda x: x["bat_dau"]):
        viec.kiem_huy()
        if x["bat_dau"] < moc_truoc:
            can_lam_ro = True
        moc_truoc = max(moc_truoc, x["ket_thuc"])
    phu_thuoc_td = bool(_THOI_DIEM.search(q)) or any(x[0]["phu_thuoc_thoi_diem"] for x in y_dinh)
    moc = {"thoi_diem": s["ngu_canh_core"]["thoi_diem"], "tu_ngay": None, "den_ngay": None}
    if re.search(r"(?<!\w)tháng này(?!\w)", q, re.I):
        dt = datetime.fromisoformat(moc["thoi_diem"])
        moc.update(tu_ngay=f"{dt.year:04}-{dt.month:02}-01",
                   den_ngay=f"{dt.year:04}-{dt.month:02}-{monthrange(dt.year, dt.month)[1]:02}")
    return c, thuc_the, can_cu, y_dinh, can_lam_ro, phu_thuoc_td, moc


def _cam_lenh(v, viec):
    viec.kiem_huy()
    if type(v) is str and _LENH_CAM.search(v):
        ham_khong_duoc_phep()
    if type(v) is dict:
        for k, con in v.items():
            if k.lower() in _KHOA_CAM:
                ham_khong_duoc_phep()
            _cam_lenh(con, viec)
    elif type(v) is list:
        for con in v:
            _cam_lenh(con, viec)


def _kiem_ham(de_xuat, s, c, thuc_the, y_dinh, viec):
    allow = {(x["ten"], x["phien_ban"]): x for x in s["du_lieu"]["ham"]}
    ket_qua, da_gap = [], set()
    for h in de_xuat:
        viec.kiem_huy()
        _cam_lenh(h, viec)
        if type(h) is not dict or set(h) != {"ten", "phien_ban", "tham_so"}:
            sai_khuon()
        if type(h["ten"]) is not str or type(h["phien_ban"]) is not str:
            sai_khuon()
        khoa = (h["ten"], h["phien_ban"])
        if khoa not in allow or khoa in da_gap:
            ham_khong_duoc_phep()
        da_gap.add(khoa)
        goc = allow[khoa]
        if not khop_khuon(h["tham_so"], goc["schema_tham_so"], kiem_huy=viec.kiem_huy, dong_object=True):
            sai_khuon()
        nc, quyen = s["ngu_canh_core"], goc["quyen"]
        if not quyen.keys() <= {"nhom", "phap_nhan_id", "module", "nguoi_hoi_id", "ma_pham_vi"}:
            ham_khong_duoc_phep()
        for k, v in quyen.items():
            if k == "nhom":
                nhom = v if type(v) is list else [v]
                if not nhom or any(type(x) is not str or x not in nc["nhom"] for x in nhom):
                    ham_khong_duoc_phep()
            elif not _bang_gia_tri(v, nc[k]):
                ham_khong_duoc_phep()
        b = c["ham"].get(h["ten"])
        if (type(b) is not dict or set(b) != {"phien_ban", "rang_buoc", "trang_thai", "moc_cong_bo", "y_dinh"}
                or b["phien_ban"] != h["phien_ban"] or type(b["rang_buoc"]) is not dict
                or type(b["y_dinh"]) is not list or not b["y_dinh"] or any(type(x) is not str for x in b["y_dinh"])
                or b["trang_thai"] not in {"kha_dung", "chua_chay", "khong_kha_dung"}
                or (b["moc_cong_bo"] is not None and type(b["moc_cong_bo"]) is not str)):
            loi("TC_CHUA_CO_CUA_CORE")
        if y_dinh not in b["y_dinh"]:
            ham_khong_duoc_phep()
        if b["moc_cong_bo"] is not None:
            thoi_diem(b["moc_cong_bo"])
        # Ràng buộc từng tham số gốc: entity/context hoặc tập giá trị Core đã
        # giới hạn. Object/array con phải có schema kín và khớp toàn giá trị ghim.
        if type(h["tham_so"]) is not dict or not h["tham_so"].keys() <= b["rang_buoc"].keys():
            ham_khong_duoc_phep()
        if any(type(r) is not dict or (r.get("loai") in {"thuc_the", "ngu_canh"} and k not in h["tham_so"])
               for k, r in b["rang_buoc"].items()):
            ham_khong_duoc_phep()
        for k, v in h["tham_so"].items():
            viec.kiem_huy()
            r = b["rang_buoc"][k]
            if type(r) is not dict:
                loi("TC_CHUA_CO_CUA_CORE")
            if r.get("loai") == "thuc_the" and set(r) == {"loai", "loai_thuc_the", "truong"} and r["truong"] in {"ma", "gia_tri"}:
                cac_gia_tri = [x[r["truong"]] for x in thuc_the if x["loai"] == r["loai_thuc_the"]]
            elif r.get("loai") == "ngu_canh" and set(r) == {"loai", "truong"} and r["truong"] in nc:
                cac_gia_tri = [nc[r["truong"]]]
            elif r.get("loai") == "gia_tri" and set(r) == {"loai", "cho_phep"} and type(r["cho_phep"]) is list:
                cac_gia_tri = r["cho_phep"]
            else:
                loi("TC_CHUA_CO_CUA_CORE")
            if not any(_bang_gia_tri(v, x) for x in cac_gia_tri):
                ham_khong_duoc_phep()
        trang_thai = {"kha_dung": "de_xuat_cho_core", "chua_chay": "cho", "khong_kha_dung": "khong_kha_dung"}[b["trang_thai"]]
        ket_qua.append({**deepcopy(h), "trang_thai": trang_thai, "moc_cong_bo": b["moc_cong_bo"],
                        "bam_schema_tham_so": bam(json_chuan(goc["schema_tham_so"]))})
    return ket_qua


def phan_tich_cau_hoi(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh):
    s, doc, cap, a = doc_phan_hoi(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh, "phan_tich_cau_hoi")
    d = a["du_lieu"]
    _cam_lenh(d.get("ham_de_xuat") if type(d) is dict else d, viec)
    if not khop_khuon(d, s["ai"]["khuon_tra_loi"], kiem_huy=viec.kiem_huy):
        sai_khuon()
    c, thuc_the, can_cu, y_dinh, can_lam_ro, phu_thuoc_td, moc = _phan_giai(s, cap, viec)
    if (sorted(_json_ai(x) for x in d["thuc_the"]) != sorted(json_chuan(x) for x in thuc_the)
            or d["phu_thuoc_thoi_diem"] != phu_thuoc_td):
        sai_khuon()
    yd = y_dinh[0][0]["ma"] if len(y_dinh) == 1 else "can_lam_ro"
    if d["y_dinh"] != yd:
        sai_khuon()
    # Căn cứ thực thể phải nằm trong quote câu hỏi, không quote mô tả hàm.
    map_q = next(m for m in s["ai"]["map_nguon"] if m["duong_dan_snapshot"] == ["du_lieu", "cau_hoi"])
    vi_tri_y_dinh = [{"bat_dau": x, "ket_thuc": z} for _, vi_tri in y_dinh for x, z in vi_tri]
    for x in can_cu + vi_tri_y_dinh:
        viec.kiem_huy()
        bat_dau = map_q["ai_bat_dau"] + x["bat_dau"]
        ket_thuc = map_q["ai_bat_dau"] + x["ket_thuc"]
        if not any(q["bat_dau"] <= bat_dau < ket_thuc <= q["ket_thuc"] for q in a["trich_dan"]):
            sai_khuon()
    ham = _kiem_ham(d["ham_de_xuat"], s, c, thuc_the, yd, viec)
    if can_lam_ro:
        ham = []  # Không chọn bừa giữa các khoản vay/hợp đồng cùng loại.
    trang_thai = ("can_lam_ro" if can_lam_ro else "cho" if any(x["trang_thai"] == "cho" for x in ham)
                  else "chua_thuc_hien" if any(x["trang_thai"] == "de_xuat_cho_core" for x in ham) else "khong_kha_dung")
    kq = {"y_dinh": yd, "thuc_the": thuc_the, "can_cu_thuc_the": can_cu,
          "bam_phan_giai_core": bam(json_chuan(c)),
          "can_cu_y_dinh": [{"cau": s["du_lieu"]["cau_hoi"][x:z], "bat_dau": x, "ket_thuc": z}
                           for _, vi_tri in y_dinh for x, z in vi_tri],
          "ham_de_xuat": ham, "can_lam_ro": can_lam_ro, "phu_thuoc_thoi_diem": phu_thuoc_td,
          "moc_thoi_diem": moc, "tang_1": {"trang_thai": trang_thai,
          "ly_do": {"can_lam_ro": "Cần làm rõ thực thể hoặc ý định trước khi tra cứu.",
                    "cho": "Module chưa chạy; Core có thể chọn nguồn tầng 2 đúng quyền.",
                    "chua_thuc_hien": "Mới đề xuất hàm; Core chưa thực thi tra cứu tầng 1.",
                    "khong_kha_dung": "Chưa có hàm khả dụng; Core có thể chọn nguồn tầng 2 đúng quyền."}[trang_thai]},
          "de_nghi_tang_2": trang_thai in {"cho", "khong_kha_dung"},
          "phu_thuoc_cache": phu_thuoc(s, thuc_the, phu_thuoc_td, ham=ham)}
    return luu_ket_qua(viec, s, doc, kq, "da_phan_tich", phien_ban_engine,
                      canh_bao=[kq["tang_1"]["ly_do"]])
