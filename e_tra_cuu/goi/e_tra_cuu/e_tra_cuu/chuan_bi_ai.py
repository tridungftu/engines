"""TC-4: ghim yêu cầu Local AI tại Core; không chọn/gọi model."""

from copy import deepcopy
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .kiem_dau_vao import (DocNguonCore, bam, doi_tuong, json_chuan, kiem_bam,
                          kiem_du_lieu, loi, ma)
from .ngu_canh_ai import dung_ngu_canh, dung_khuon, kiem_ngan_sach, qua_ngan_sach


TAC_VU_AI = {"phan_loai", "phan_tich_cau_hoi", "xep_hang_lai", "soan_tra_loi"}
_TRAN_DOC = {"tep_toi_da_byte": 20971520, "tong_doc_toi_da_byte": 67108864,
             "ho_so_toi_da_byte": 65536}
_TOM_TAT = ("trang_thai", "so_doan", "so_ung_vien", "tang", "co_can_cu",
            "co_mau_thuan", "can_duyet", "nhan")


def kiem_tham_so(tham_so, tac_vu):
    """Kiểm lại ở biên nghiệp vụ, kể cả khi caller không qua SDK."""
    if tham_so.get("tac_vu") not in TAC_VU_AI or tham_so["tac_vu"] != tac_vu:
        loi("TC_SAI_GIAI_DOAN")
    for k, tran in (("ma_prompt", 200), ("phien_ban_prompt", 100), ("prompt", 16000)):
        v = tham_so.get(k)
        if type(v) is not str or not v.strip():
            raise LoiNghiepVu("THIEU_PROMPT", "Chức năng chưa có prompt. Anh nhờ quản trị viên module bổ sung.")
        if len(v) > tran:
            qua_ngan_sach()
    # Cùng miền định danh consumer AI-2, không suy module/quyền từ các mã này.
    for k in ("ma_prompt", "phien_ban_prompt"):
        if not re.fullmatch(r"[A-Za-z0-9_.:-]+", tham_so[k]):
            loi()
    model = tham_so.get("model_uu_tien")
    if type(model) is str and not model.strip():
        model = None
    if model is not None and (type(model) is not str or len(model) > 200
                             or not re.fullmatch(r"[A-Za-z0-9._:/-]+", model)):
        loi()
    json_chuan(tham_so)  # Từ chối surrogate lẻ, giữ nguyên NFC/NFD.
    return {k: tham_so[k] for k in ("ma_prompt", "phien_ban_prompt", "prompt")} | {"model_uu_tien": model}


def _bo_van_ban_da_nap(n):
    n = deepcopy(doi_tuong(n, ("ma_nguon", "phien_ban_nguon", "goc", "van_ban", "van_ban_tai_lieu"), ()))
    n.pop("van_ban_tai_lieu")
    return n


def doc_snapshot_ai(viec, cua, phien_ban, kiem_cau_hinh):
    pb = doi_tuong(viec.dau_vao, ("loai", "ho_so_tra_cuu"), ())
    if pb["loai"] != "ho_so_tra_cuu":
        loi()
    h = doi_tuong(pb["ho_so_tra_cuu"], ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan",
        "ho_so", "bam_ho_so", "bam_cau_hinh", "bam_danh_muc", "phien_ban_engine", "tom_tat", "canh_bao"), ())
    if h["tac_vu"] not in TAC_VU_AI or h["giai_doan"] != "da_nhan":
        loi("TC_SAI_GIAI_DOAN")
    ts = kiem_tham_so(viec.tham_so, h["tac_vu"])
    if type(h["phien_ban"]) is not int or h["phien_ban"] != 1:
        loi("TC_SAI_NGUON")
    ma(h["ma_yeu_cau"])
    for k in ("bam_ho_so", "bam_cau_hinh"):
        kiem_bam(h[k])
    if h["bam_danh_muc"] is not None:
        kiem_bam(h["bam_danh_muc"])
    if h["phien_ban_engine"] != "e_tra_cuu " + phien_ban:
        loi("TC_SAI_NGUON")
    doi_tuong(h["tom_tat"], _TOM_TAT, ())
    if h["canh_bao"] != []:
        loi("TC_SAI_NGUON")
    if len(json_chuan(pb)) > _TRAN_DOC["ho_so_toi_da_byte"]:
        qua_ngan_sach()
    p = viec.ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if cua is None or not callable(getattr(cua, "doc_quyen", None)):
        loi("TC_CHUA_CO_CUA_CORE")
    cap = cua.doc_quyen(viec.id)
    if type(cap) is not dict or any(type(cap.get(k)) is not dict for k in ("tep", "nguon", "dau_vao", "ngu_canh_core")):
        loi("TC_CHUA_CO_CUA_CORE")
    if json_chuan(cap["dau_vao"]) != json_chuan(pb):
        loi("TC_SAI_NGUON")
    if cap["ngu_canh_core"].get("phap_nhan_id") != p:
        loi("TC_CHUA_CO_CUA_CORE")
    if cap.get("ma_yeu_cau") != h["ma_yeu_cau"] or cap.get("tac_vu") != h["tac_vu"]:
        loi("TC_SAI_NGUON")
    doc = DocNguonCore(viec, _TRAN_DOC.copy())
    doc.giay_cap = deepcopy(cap)
    s = doc.doc_ref({"tep": h["ho_so"], "bam": h["bam_ho_so"]})
    doi_tuong(s, ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ngu_canh_core",
                   "cau_hinh", "nguon", "du_lieu", "ket_qua"), ())
    if (type(s["phien_ban"]) is not int or s["phien_ban"] != 1 or s["ket_qua"] is not None
            or any(s[k] != h[k] for k in ("ma_yeu_cau", "tac_vu", "giai_doan"))):
        loi("TC_SAI_NGUON")
    if json_chuan(s["ngu_canh_core"]) != json_chuan(cap["ngu_canh_core"]):
        loi("TC_CHUA_CO_CUA_CORE")
    ch = kiem_cau_hinh(s["cau_hinh"])
    if (json_chuan(ch) != json_chuan(s["cau_hinh"])
            or bam(json_chuan(ch["gia_tri"])) != kiem_bam(h["bam_cau_hinh"])):
        loi("TC_SAI_NGUON")
    doc.tran = ch["gia_tri"]["ngan_sach"]
    if (h["ho_so"]["kich_thuoc"] > doc.tran["tep_toi_da_byte"]
            or doc.tong_doc > doc.tran["tong_doc_toi_da_byte"]):
        loi("TC_QUA_GIOI_HAN")
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        qua_ngan_sach()
    kiem_ngan_sach(s["du_lieu"], doc.tran)
    d = deepcopy(s["du_lieu"])
    if "tai_lieu" in d:
        d["tai_lieu"] = _bo_van_ban_da_nap(d["tai_lieu"])
    if "nguon" in d and not (s["tac_vu"] == "soan_tra_loi" and d["tang"] == 1):
        d["nguon"] = [_bo_van_ban_da_nap(n) for n in d["nguon"]]
    da_kiem = kiem_du_lieu(doc, {"tac_vu": s["tac_vu"], "du_lieu": d, "ngu_canh_core": s["ngu_canh_core"]})
    if (json_chuan(da_kiem) != json_chuan(s["du_lieu"])
            or json_chuan(list(doc.nguon.values())) != json_chuan(s["nguon"])):
        loi("TC_SAI_NGUON")
    dm = da_kiem.get("danh_muc")
    bam_dm = bam(json_chuan(dm)) if dm is not None else None
    if (kiem_bam(h["bam_danh_muc"]) if h["bam_danh_muc"] is not None else None) != bam_dm:
        loi("TC_SAI_NGUON")
    tt = dict.fromkeys(_TOM_TAT)
    if s["tac_vu"] == "xep_hang_lai":
        tt["so_ung_vien"] = len(da_kiem["ung_vien"])
    if s["tac_vu"] == "soan_tra_loi":
        tt["tang"] = da_kiem["tang"]
    if json_chuan(tt) != json_chuan(h["tom_tat"]):
        loi("TC_SAI_NGUON")
    # Core chọn nhánh Python; không chế yêu cầu AI rỗng để giữ chuỗi tuyến tính.
    if s["tac_vu"] == "soan_tra_loi" and (da_kiem["tang"] == 1 or not da_kiem["bang_chung"]):
        loi("TC_SAI_GIAI_DOAN")
    return h, s, doc, ts


def chuan_bi_ai(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh):
    viec.kiem_huy()
    h, s, doc, ts = doc_snapshot_ai(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh)
    viec.tien_do(20, "Đã kiểm hồ sơ và quyền nguồn chuẩn bị AI.")
    tai_lieu, maps, doan = dung_ngu_canh(s, viec)
    khuon = dung_khuon(s)
    ns = doc.tran
    if len(tai_lieu) > ns["ai_toi_da_ky_tu"] or len(json_chuan(khuon)) > ns["khuon_toi_da_byte"]:
        qua_ngan_sach()
    s["giai_doan"] = "cho_ai"
    s["ai"] = {**ts, "khuon_tra_loi": khuon, "tai_lieu": tai_lieu, "map_nguon": maps,
               "doan": doan, "bam_ngu_canh_ai": bam(tai_lieu.encode("utf-8")),
               "ngan_sach": {"so_ky_tu": len(tai_lieu), "so_byte_utf8": len(tai_lieu.encode("utf-8")),
                            "khuon_byte": len(json_chuan(khuon)), "token_thuc": None, "trang_thai_token": "chua_do"}}
    noi_dung = json_chuan(s)
    if len(noi_dung) > ns["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    ct = {"tra_cuu": {"phien_ban": 1, "ma_yeu_cau": h["ma_yeu_cau"], "tac_vu": h["tac_vu"],
          "ho_so": None, "bam_ho_so": bam(noi_dung), "bam_cau_hinh": h["bam_cau_hinh"],
          "bam_ngu_canh_ai": s["ai"]["bam_ngu_canh_ai"]}}
    if len(json_chuan(ct)) > ns["chuyen_tiep_toi_da_byte"]:
        qua_ngan_sach()
    viec.tien_do(90, "Đang ghim ngữ cảnh và khuôn AI tại Core.")
    tep = viec.tai_tep_ra("ho-so-chuan-bi-ai.json", noi_dung, "application/json")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ho-so-chuan-bi-ai.json" or tep["kich_thuoc"] != len(noi_dung):
        loi("TC_SAI_NGUON")
    ct["tra_cuu"]["ho_so"] = tep
    if len(json_chuan(ct)) > ns["chuyen_tiep_toi_da_byte"]:
        qua_ngan_sach()
    return {"loai": "yeu_cau_ai", "yeu_cau_ai": {"phien_ban": 1, **ts, "tai_lieu": tai_lieu,
            "khuon_tra_loi": khuon, "bat_buoc_trich_dan": True, "chuyen_tiep": ct}}
