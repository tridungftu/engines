"""TX-3: lõi đề xuất, CHƯA đăng ký runtime/contract trước review chi tiết.

Hồ sơ và mọi tệp đều qua cổng SDK. Hash chỉ kiểm toàn vẹn; quyền đọc,
ghim module/pháp nhân và vòng đời tệp thuộc Core (C-TX-01/02).
"""

from copy import deepcopy
from datetime import date
import math
import re

from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu

from .cau_truc import build_structure, doc_tai_lieu
from .kiem_tra import kiem_o
from .logic import kiem_tra_logic, kiem_quy_tac_bo
from .tham_so import (BAM, MA, bam_bytes, chon_tham_so, doc_bo, doc_json,
                      json_bytes, kiem_hoi_them)
from .tich_hop import HO_SO_TOI_DA_BYTE, build_prompt, kiem_ngan_sach, tao_khuon


DONG_TOI_DA = 200
JSON_TOI_DA = 20 * 1024 * 1024
CAU_LOI = {
    "HO_SO_HAU_KIEM_KHONG_HOP_LE": "Hồ sơ đối chiếu không khớp yêu cầu đã ghim.",
    "AI_TRA_SAI_KHUON": "Kết quả AI thiếu trường hoặc không đúng cấu trúc.",
    "KET_QUA_KHONG_HOP_LE": "Bảng kết quả không đúng cấu trúc đã khai báo.",
    "VUOT_GIOI_HAN": "Kết quả vượt giới hạn xử lý.",
    "O_EXCEL_QUA_DAI": "Có ô vượt giới hạn Excel; không thể xuất đầy đủ.",
    "XUAT_KET_QUA_LOI": "Không tạo được đầy đủ tệp kết quả; hãy thử lại.",
}
LOI_CAU_TRUC = (ValueError, TypeError, KeyError, IndexError, RecursionError,
               OverflowError, UnicodeError, AttributeError)


def loi(ma):
    raise LoiNghiepVu(ma, CAU_LOI[ma]) from None


def _can(dieu_kien, ma="HO_SO_HAU_KIEM_KHONG_HOP_LE"):
    if not dieu_kien:
        loi(ma)


def _chu(v):
    return isinstance(v, str) and bool(v.strip())


def _bam(v):
    return isinstance(v, str) and BAM.fullmatch(v) is not None


def _ds_chu(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _bang_json(a, b):
    # Python coi True == 1; snapshot JSON phải phân biệt hai kiểu này.
    return json_bytes(a) == json_bytes(b)


def _so(v):
    return type(v) in (int, float) and (type(v) is int or math.isfinite(v))


def kiem_tep(v, *, mime=None):
    return (isinstance(v, dict) and all(_chu(v.get(k)) for k in ("tep_id", "ten", "mime"))
            and type(v.get("kich_thuoc")) is int and v["kich_thuoc"] > 0
            and (mime is None or v["mime"] == mime))


def _json_co_tran(v, ma):
    try:
        raw = json_bytes(v)
    except LOI_CAU_TRUC:
        loi(ma)
    if len(raw) > JSON_TOI_DA:
        loi("VUOT_GIOI_HAN")
    return raw


def doc_tra_loi(dau_vao):
    ma = "AI_TRA_SAI_KHUON"
    _json_co_tran(dau_vao, ma)
    _can(isinstance(dau_vao, dict) and dau_vao.get("loai") == "tra_loi_ai", ma)
    ai = dau_vao.get("tra_loi_ai")
    can = {"phien_ban", "trang_thai", "tra_loi", "du_lieu", "trich_dan",
           "kiem_trich_dan", "nha_cung_cap", "model", "ly_do_chon_model",
           "ma_prompt", "phien_ban_prompt", "phien_ban_engine", "bam_dau_vao",
           "chuyen_tiep", "canh_bao"}
    _can(isinstance(ai, dict) and can <= ai.keys(), ma)
    _can(type(ai["phien_ban"]) is int and ai["phien_ban"] == 1
         and ai["trang_thai"] in ("co_can_cu", "khong_thay_can_cu")
         and isinstance(ai["tra_loi"], str)
         and (ai["du_lieu"] is None or isinstance(ai["du_lieu"], dict))
         and isinstance(ai["trich_dan"], list)
         and isinstance(ai["kiem_trich_dan"], dict)
         and type(ai["kiem_trich_dan"].get("dat")) is bool
         and _ds_chu(ai["kiem_trich_dan"].get("loi"))
         and all(_chu(ai[k]) for k in ("model", "ly_do_chon_model", "ma_prompt",
                                      "phien_ban_prompt", "phien_ban_engine"))
         and _bam(ai["bam_dau_vao"]) and isinstance(ai["chuyen_tiep"], dict)
         and _ds_chu(ai["canh_bao"]), ma)
    _can(ai["nha_cung_cap"] == "local")
    if len(json_bytes(ai["chuyen_tiep"])) > 64 * 1024:
        loi("VUOT_GIOI_HAN")
    return ai


def doc_ho_so(viec, ai):
    """Mở qua viec.mo_tep; lỗi vận hành của Core/hủy giữ nguyên phân loại."""
    meta = ai["chuyen_tiep"].get("trich_xuat")
    _can(isinstance(meta, dict))
    try:
        _can(type(meta["phien_ban"]) is int and meta["phien_ban"] == 1
             and kiem_tep(meta["ho_so_hau_kiem"], mime="application/json")
             and _bam(meta["bam_ho_so_hau_kiem"]))
        tep = meta["ho_so_hau_kiem"]
        if tep["kich_thuoc"] > HO_SO_TOI_DA_BYTE:
            loi("VUOT_GIOI_HAN")
    except LOI_CAU_TRUC:
        loi("HO_SO_HAU_KIEM_KHONG_HOP_LE")
    viec.kiem_huy()
    # Không đổi lỗi quyền/mạng/lease thành không thấy căn cứ hoặc bảng rỗng.
    try:
        with viec.mo_tep(tep["tep_id"]) as f:
            raw = f.read(HO_SO_TOI_DA_BYTE + 1)
    except LoiDuongTruyen as exc:
        if exc.http_status == 413:
            loi("VUOT_GIOI_HAN")
        raise
    except LoiNghiepVu as exc:
        if exc.ma == "VUOT_GIOI_HAN":
            loi("VUOT_GIOI_HAN")
        raise
    viec.kiem_huy()
    if len(raw) > HO_SO_TOI_DA_BYTE:
        loi("VUOT_GIOI_HAN")
    _can(len(raw) == tep["kich_thuoc"] and bam_bytes(raw) == meta["bam_ho_so_hau_kiem"])
    try:
        hs = doc_json(raw.decode("utf-8"))
        _can(type(hs["phien_ban"]) is int and hs["phien_ban"] == 1
             and _chu(hs["phien_ban_engine"]))
        bo, dm, bam_bo = doc_bo(hs["tham_so_viec"])
        params = chon_tham_so(hs["tham_so_viec"], dm)
        kiem_hoi_them(hs["tham_so_viec"])
        _can(hs["bo_tham_so_json"] == hs["tham_so_viec"]["bo_tham_so_json"]
             and _bang_json(hs["bo_tham_so"], bo) and _bang_json(hs["cac_dong_e1"], dm.cac_dong)
             and _bang_json(hs["quy_tac"], dm.quy_tac) and hs["yeu_cau_them"] == []
             and hs["bam_bo_tham_so"] == bam_bo == meta["bam_bo_tham_so"]
             and hs["ma_bam_noi_dung"] == dm.ma_bam_noi_dung == meta["ma_bam_noi_dung"]
             and hs["bam_tep_goc"] == bo.get("bam_tep_goc") == meta["bam_tep_goc"])
        for k in ("module", "loai_hop_dong", "phien_ban_bo"):
            _can(meta[k] == bo[k])
        _can(hs["ngu_canh"]["phap_nhan_id"] == viec.ngu_canh.get("phap_nhan_id"))
        tl = doc_tai_lieu({"van_ban_tai_lieu": hs["tai_lieu"]})
        _can(hs["bam_van_ban"] == bam_bytes(tl["van_ban"].encode("utf-8")))
        _kiem_trang(tl)
        _can(_bang_json(hs["cau_truc"], build_structure(tl["van_ban"], viec.kiem_huy)))
        # Hồ sơ gọn bỏ bản chép toàn văn trong request. Bản TX-2 cũ có
        # trường này vẫn được kiểm đúng giá trị, không ghi đè sai lệch.
        req = {"tai_lieu": tl["van_ban"], **hs["yeu_cau_ai"]}
        _can(hs["ma_truong_can_trich"] == [p["ma"] for p in params]
             and _bang_json(req["khuon_tra_loi"], tao_khuon(params))
             and req["tai_lieu"] == tl["van_ban"]
             and req["prompt"] == build_prompt(hs["tham_so_viec"], params)
             and req["bat_buoc_trich_dan"] is True
             and type(req["phien_ban"]) is int and req["phien_ban"] == 1
             and hs["bam_yeu_cau_ai"] == bam_bytes(json_bytes(req)) == meta["bam_yeu_cau_ai"])
        for k in ("ma_prompt", "phien_ban_prompt"):
            _can(ai[k] == req[k] == hs["tham_so_viec"][k])
        # AI-2 băm toàn phong bì yêu cầu, có chuyen_tiep; băm tài liệu gốc
        # vẫn nằm riêng trong tai_lieu.bam_dau_vao, không tráo với băm này.
        _can(ai["bam_dau_vao"] == bam_bytes(json_bytes({
            "loai": "yeu_cau_ai", "yeu_cau_ai": {**req, "chuyen_tiep": ai["chuyen_tiep"]}})))
        model = hs["tham_so_viec"].get("model_uu_tien")
        if isinstance(model, str) and not model.strip():
            model = None
        _can(req["model_uu_tien"] == model)
        cfg = hs["cau_hinh_da_ghim"]
        _can(isinstance(cfg, dict) and type(cfg["phien_ban_cau_hinh"]) is int
             and cfg["phien_ban_cau_hinh"] > 0
             and type(cfg["gia_tri"]["ngan_sach_token_vao_toi_da"]) is int
             and 1024 <= cfg["gia_tri"]["ngan_sach_token_vao_toi_da"] <= 100000)
        _can(_bang_json(hs["sang_loc_ngan_sach"], kiem_ngan_sach(
            hs["tham_so_viec"], cfg, req["prompt"], req["tai_lieu"], req["khuon_tra_loi"])))
    except LoiNghiepVu:
        loi("HO_SO_HAU_KIEM_KHONG_HOP_LE")
    except LOI_CAU_TRUC:
        loi("HO_SO_HAU_KIEM_KHONG_HOP_LE")
    return hs, meta, params


def _kiem_trang(tl):
    _can(tl["so_trang"] == len(tl["trang"]))
    if tl["nguon_doc"] == "docx":
        _can(tl["so_trang"] == 0)
    else:
        _can(len(tl["van_ban"].split("\f")) == tl["so_trang"])
    ds = []
    for t in tl["trang"]:
        _can(type(t["so"]) is int and t["so"] > 0
             and all(_so(t[k]) and t[k] > 0 for k in ("rong", "cao"))
             and _chu(t["don_vi"]) and isinstance(t["khoi"], list))
        ds.append(t["so"])
        for k in t["khoi"]:
            _can(isinstance(k, dict) and k["loai"] in ("doan", "bang")
                 and isinstance(k["hop"], list) and len(k["hop"]) == 4
                 and all(_so(x) for x in k["hop"]))
            if k["loai"] == "doan":
                _can(isinstance(k["van_ban"], str))
            else:
                _can(isinstance(k["o"], list)
                     and all(isinstance(o, dict) and isinstance(o["van_ban"], str) for o in k["o"]))
    _can(ds == sorted(set(ds)))


def _kiem_du_lieu(ai, ds):
    ma = "AI_TRA_SAI_KHUON"
    data = ai["du_lieu"]
    if data is None:
        _can(ai["trang_thai"] == "khong_thay_can_cu", ma)
        return {}
    # Mã bị bỏ sót được bổ sung ô null; mã lạ/trùng hoặc đảo thứ tự là sai khuôn.
    _can(list(data) == [m for m in ds if m in data], ma)
    for o in data.values():
        _can(isinstance(o, dict) and set(o) == {"gia_tri", "don_vi", "ghi_chu", "trich_dan"}, ma)
        _can(all(o[k] is None or isinstance(o[k], str) for k in ("gia_tri", "don_vi", "ghi_chu"))
             and isinstance(o["trich_dan"], list), ma)
    return data


def hau_kiem(viec, *, phien_ban_engine="e_trich_xuat 0.3.0"):
    viec.kiem_huy()
    ai = doc_tra_loi(deepcopy(viec.dau_vao))
    hs, meta, params = doc_ho_so(viec, ai)
    data = _kiem_du_lieu(ai, hs["ma_truong_can_trich"])
    viec.tien_do(20, "Đã kiểm hồ sơ đối chiếu đã ghim.")
    bang, cho_logic = [], {}
    trong = {"gia_tri": None, "don_vi": None, "ghi_chu": None, "trich_dan": []}
    for p in params:
        viec.kiem_huy()
        ma = p["ma"]
        o = data.get(ma, trong)
        ck = kiem_o(o, hs["tai_lieu"], hs["cau_truc"], bo_sot=ma not in data and ai["du_lieu"] is not None)
        bang.append({"ma": ma, "ten": p["ten"], "kieu": "van_ban", "kieu_da_chuyen": False,
                     **ck, "nguyen_van": o["gia_tri"], "don_vi_nguyen_van": o["don_vi"],
                     "ghi_chu": o["ghi_chu"], "phan_hoi_ai": deepcopy(data.get(ma)),
                     "can_soat": bool(ck["ly_do"]), "kiem_tra_logic": []})
        # Logic chỉ xét câu đã kiểm, giữ dấu nguyên văn AI để L1/L4 đối chiếu.
        cho_logic[ma] = {"gia_tri": o["gia_tri"],
                         "trich_dan": "\n".join(q["cau"] for q in ck["dan_chung"]),
                         "ghi_chu": o["ghi_chu"]}
    logic = kiem_tra_logic(cho_logic, params, loai_hop_dong=hs["bo_tham_so"]["loai_hop_dong"])
    # Quy tắc E1 đã nằm trong snapshot; không eval điều kiện hoặc tra bộ hiện hành.
    theo_ma = {r["ma"]: r for r in bang}
    for ma, ly_do in kiem_quy_tac_bo(theo_ma, hs["quy_tac"]).items():
        logic.setdefault(ma, []).extend(ly_do)
    for r in bang:
        r["kiem_tra_logic"] = logic.get(r["ma"], [])
        r["ly_do"].extend(r["kiem_tra_logic"])
        r["can_soat"] = bool(r["ly_do"])
    bo = hs["bo_tham_so"]
    kq = {"loai": "bang_trich_xuat", "bang_trich_xuat": {
        "phien_ban": 1, "don_vi_offset": "unicode",
        **{k: bo[k] for k in ("module", "loai_hop_dong", "phien_ban_bo")},
        "bam_bo_tham_so": hs["bam_bo_tham_so"], "ma_bam_noi_dung": hs["ma_bam_noi_dung"],
        "bam_tep_goc": hs["bam_tep_goc"],
        "ma_prompt": ai["ma_prompt"], "phien_ban_prompt": ai["phien_ban_prompt"],
        "phien_ban_engine": phien_ban_engine, "ma_truong_can_trich": hs["ma_truong_can_trich"],
        "nguon": {"nguon_doc": hs["tai_lieu"]["nguon_doc"],
                  "bam_dau_vao": hs["tai_lieu"]["bam_dau_vao"],
                  "bam_van_ban": hs["bam_van_ban"],
                  "ho_so_hau_kiem": deepcopy(meta["ho_so_hau_kiem"]),
                  "bam_ho_so_hau_kiem": meta["bam_ho_so_hau_kiem"],
                  "phien_ban_engine_doc": hs["tai_lieu"]["phien_ban_engine"],
                  "phien_ban_engine_chuan_bi": hs["phien_ban_engine"]},
        "ai": {k: deepcopy(ai[k]) for k in ("nha_cung_cap", "model", "phien_ban_engine",
                                           "bam_dau_vao", "trang_thai", "kiem_trich_dan")},
        "bang": bang, "tom_tat": tom_tat(bang),
        "canh_bao": (["Chưa phân trang Word; vị trí theo đoạn/Điều/Khoản."]
                     if hs["tai_lieu"]["nguon_doc"] == "docx" else []),
    }}
    kiem_bang(kq)
    viec.tien_do(100, "Đã hậu kiểm từng ô của bảng kết quả.")
    viec.kiem_huy()
    return kq


def tom_tat(bang):
    return {"so_tham_so": len(bang), "so_can_soat": sum(r["can_soat"] for r in bang),
            "co_can_cu": any(r["gia_tri"] is not None and r["dan_chung"] for r in bang)}


def _gia_tri_dung(v, kieu):
    if v is None:
        return True
    if kieu == "van_ban":
        return _chu(v)
    if kieu == "so":
        return _so(v)
    if kieu == "so_tien":
        return (isinstance(v, dict) and set(v) == {"so", "tien_te"}
                and (type(v["so"]) is int or isinstance(v["so"], str)
                     and re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", v["so"]) is not None)
                and isinstance(v["tien_te"], str) and re.fullmatch(r"[A-Z]{3}", v["tien_te"]) is not None)
    if kieu == "co_khong":
        return type(v) is bool
    if kieu == "tep":
        return kiem_tep(v)
    if kieu == "ngay" and isinstance(v, str):
        try:
            return date.fromisoformat(v).isoformat() == v
        except ValueError:
            return False
    return False


def _vi_tri_dung(v, nguon):
    if not (isinstance(v, dict) and set(v) == {"loai", "nhan", "so_trang", "hop"}
            and v["loai"] in ("doan", "trang") and _chu(v["nhan"])
            and (v["so_trang"] is None or type(v["so_trang"]) is int and v["so_trang"] > 0)
            and (v["hop"] is None or isinstance(v["hop"], list) and len(v["hop"]) == 4
                 and all(_so(n) for n in v["hop"]))):
        return False
    return (nguon != "docx" or v["loai"] == "doan" and v["so_trang"] is None and v["hop"] is None)


def kiem_bang(phong_bi):
    """Bộ kiểm đề xuất bằng Python; chưa phải schema contract đã duyệt."""
    ma = "KET_QUA_KHONG_HOP_LE"
    raw = _json_co_tran(phong_bi, ma)
    try:
        _can(set(phong_bi) == {"loai", "bang_trich_xuat"} and phong_bi["loai"] == "bang_trich_xuat", ma)
        b = phong_bi["bang_trich_xuat"]
        can = {"phien_ban", "don_vi_offset", "module", "loai_hop_dong", "phien_ban_bo", "bam_bo_tham_so",
               "ma_prompt", "phien_ban_prompt", "phien_ban_engine", "ma_truong_can_trich",
               "nguon", "ai", "bang", "tom_tat", "canh_bao"}
        _can(can <= b.keys() and type(b["phien_ban"]) is int and b["phien_ban"] == 1
             and b["don_vi_offset"] == "unicode", ma)
        _can(all(isinstance(b[k], str) and MA.fullmatch(b[k])
                 for k in ("module", "loai_hop_dong", "phien_ban_bo", "ma_prompt", "phien_ban_prompt"))
             and _chu(b["phien_ban_engine"]) and _bam(b["bam_bo_tham_so"])
             and _ds_chu(b["canh_bao"]), ma)
        ds, bang = b["ma_truong_can_trich"], b["bang"]
        _can(_ds_chu(ds) and isinstance(bang, list) and len(ds) == len(set(ds)), ma)
        if len(bang) > DONG_TOI_DA:
            loi("VUOT_GIOI_HAN")
        _can(1 <= len(bang) and [r["ma"] for r in bang] == ds, ma)
        n = b["nguon"]
        _can(n["nguon_doc"] in ("docx", "abbyy", "tesseract", "lop_chu_san")
             and all(_bam(n[k]) for k in ("bam_dau_vao", "bam_van_ban", "bam_ho_so_hau_kiem"))
             and kiem_tep(n["ho_so_hau_kiem"], mime="application/json"), ma)
        _can(b["ai"]["nha_cung_cap"] == "local" and _chu(b["ai"]["model"]), ma)
        for r in bang:
            _can(_chu(r["ma"]) and _chu(r["ten"]) and r["kieu"] in
                 ("van_ban", "so", "so_tien", "ngay", "co_khong", "tep")
                 and type(r["kieu_da_chuyen"]) is bool
                 and (r["kieu_da_chuyen"] or r["kieu"] == "van_ban")
                 and _gia_tri_dung(r["gia_tri"], r["kieu"])
                 and all(r[k] is None or isinstance(r[k], str)
                         for k in ("nguyen_van", "don_vi_nguyen_van", "ghi_chu"))
                 and type(r["can_soat"]) is bool and _ds_chu(r["ly_do"])
                 and _ds_chu(r["kiem_tra_logic"]) and isinstance(r["dan_chung"], list), ma)
            _can(r["can_soat"] == bool(r["ly_do"]) and all(x in r["ly_do"] for x in r["kiem_tra_logic"]), ma)
            _can(r["gia_tri"] is not None or r["can_soat"], ma)
            _can(r["gia_tri"] is None or bool(r["dan_chung"]), ma)
            for q in r["dan_chung"]:
                _can(_chu(q["cau"]) and type(q["bat_dau"]) is int and type(q["ket_thuc"]) is int
                     and 0 <= q["bat_dau"] < q["ket_thuc"]
                     and len(q["cau"]) == q["ket_thuc"] - q["bat_dau"]
                     and _vi_tri_dung(q["vi_tri"], n["nguon_doc"]), ma)
        t = b["tom_tat"]
        _can(set(t) == {"so_tham_so", "so_can_soat", "co_can_cu"}
             and type(t["so_tham_so"]) is type(t["so_can_soat"]) is int
             and type(t["co_can_cu"]) is bool and t == tom_tat(bang), ma)
    except LOI_CAU_TRUC:
        loi(ma)
    return raw
