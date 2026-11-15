"""TC-8: xuất kết quả đã hậu kiểm qua kho tệp Core."""
from copy import deepcopy

from .kiem_dau_vao import DocNguonCore, bam, doi_tuong, json_chuan, kiem_bam, loi

_TRAN = {"tep_toi_da_byte": 20971520, "tong_doc_toi_da_byte": 67108864, "ho_so_toi_da_byte": 65536}
_TT = ("trang_thai", "so_doan", "so_ung_vien", "tang", "co_can_cu", "co_mau_thuan", "can_duyet", "nhan")
_GD = {"cat_doan": {"da_cat_doan"}, "phan_loai": {"da_phan_loai", "cho_phan_loai"},
       "phan_tich_cau_hoi": {"da_phan_tich"}, "xep_hang_lai": {"da_xep_hang"}, "soan_tra_loi": {"da_soan"}}


def xuat_ket_qua(viec, cua, phien_ban, kiem_cau_hinh):
    viec.kiem_huy()
    pb = doi_tuong(viec.dau_vao, ("loai", "ho_so_tra_cuu"), ())
    if len(json_chuan(pb)) > _TRAN["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    if pb["loai"] != "ho_so_tra_cuu":
        loi("TC_SAI_NGUON")
    h = doi_tuong(pb["ho_so_tra_cuu"], ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ho_so", "bam_ho_so", "bam_cau_hinh", "bam_danh_muc", "phien_ban_engine", "tom_tat", "canh_bao"), ())
    tac = h["tac_vu"]
    if tac not in _GD or h["giai_doan"] not in _GD[tac]:
        loi("TC_SAI_GIAI_DOAN")
    if type(h["phien_ban"]) is not int or h["phien_ban"] != 1 or h["phien_ban_engine"] != "e_tra_cuu " + phien_ban:
        loi("TC_SAI_NGUON")
    tt = doi_tuong(h["tom_tat"], _TT, ())
    p = viec.ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if cua is None or not callable(getattr(cua, "doc_quyen", None)):
        loi("TC_CHUA_CO_CUA_CORE")
    cap = cua.doc_quyen(viec.id)
    if type(cap) is not dict or any(type(cap.get(k)) is not dict for k in ("tep", "nguon", "dau_vao", "ngu_canh_core")):
        loi("TC_CHUA_CO_CUA_CORE")
    if (json_chuan(cap["dau_vao"]) != json_chuan(pb) or cap.get("ma_yeu_cau") != h["ma_yeu_cau"]
            or cap.get("tac_vu") != tac or cap["ngu_canh_core"].get("phap_nhan_id") != p):
        loi("TC_SAI_NGUON")
    doc = DocNguonCore(viec, _TRAN.copy())
    doc.giay_cap = deepcopy(cap)
    s = doc.doc_ref({"tep": h["ho_so"], "bam": h["bam_ho_so"]})
    if type(s) is dict and (s.get("tac_vu") != tac or s.get("giai_doan") != h["giai_doan"]):
        loi("TC_SAI_GIAI_DOAN")
    if (type(s) is not dict or s.get("ma_yeu_cau") != h["ma_yeu_cau"]
            or type(s.get("phien_ban")) is not int or s["phien_ban"] != 1
            or json_chuan(s.get("ngu_canh_core")) != json_chuan(cap["ngu_canh_core"])):
        loi("TC_SAI_NGUON")
    ch = kiem_cau_hinh(s["cau_hinh"])
    if json_chuan(ch) != json_chuan(s["cau_hinh"]) or bam(json_chuan(ch["gia_tri"])) != kiem_bam(h["bam_cau_hinh"]):
        loi("TC_SAI_NGUON")
    doc.tran = ch["gia_tri"]["ngan_sach"]
    if h["ho_so"]["kich_thuoc"] > doc.tran["tep_toi_da_byte"] or len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    nguon = s["nguon"]
    if type(nguon) is not list:
        loi("TC_SAI_NGUON")
    for n in nguon:
        if type(n) is not dict or n.get("ma_nguon") not in cap["nguon"]:
            loi("TC_SAI_NGUON")
        goc = cap["nguon"][n["ma_nguon"]]
        if type(goc) is not dict or any(n.get(k) != v for k, v in goc.items()):
            loi("TC_SAI_NGUON")
        for k in ("goc", "van_ban"):
            if k in n:
                ref = n[k]
                if type(ref) is not dict or cap["tep"].get(ref.get("tep", {}).get("tep_id")) != ref:
                    loi("TC_SAI_NGUON")
    d, kq = s["du_lieu"], s["ket_qua"]
    if type(d) is not dict or type(kq) is not dict:
        loi("TC_SAI_NGUON")
    # Mọi mã nguồn trong kết quả phải thuộc giấy cấp hiện hành; các trường
    # định danh/băm xuất hiện trong trích dẫn phải khớp bản Core đã cấp.
    def kiem_nguon(v):
        if type(v) is list:
            for x in v:
                kiem_nguon(x)
        elif type(v) is dict:
            if v.get("ma_nguon") is not None:
                g = cap["nguon"].get(v["ma_nguon"])
                if type(g) is not dict or any(v[k] != g[k] for k in g if k in v):
                    loi("TC_SAI_NGUON")
            for x in v.values():
                kiem_nguon(x)
    kiem_nguon(kq)
    dm = d.get("danh_muc")
    if (kiem_bam(h["bam_danh_muc"]) if h["bam_danh_muc"] is not None else None) != (bam(json_chuan(dm)) if dm is not None else None):
        loi("TC_SAI_NGUON")
    expected = dict.fromkeys(_TT)
    expected["trang_thai"] = h["giai_doan"]
    if tac == "cat_doan":
        ds = kq["doan"]
        if type(ds) is not list:
            loi("TC_SAI_NGUON")
        if len(ds) > 5000:
            loi("TC_QUA_GIOI_HAN")
        expected["so_doan"] = len(ds)
    elif tac == "phan_loai":
        expected.update(co_can_cu=tt["co_can_cu"], can_duyet=True)
        if type(tt["co_can_cu"]) is not bool or (tt["co_can_cu"] and not kq["can_cu"]):
            loi("TC_SAI_NGUON")
    elif tac == "xep_hang_lai":
        uv, ds = d["ung_vien"], kq["xep_hang"]
        if type(uv) is not list or type(ds) is not list or len(uv) > 50 or len(uv) != len(ds) or len({x["ma_ung_vien"] for x in ds}) != len(ds) or {x["ma_ung_vien"] for x in uv} != {x["ma_ung_vien"] for x in ds}:
            loi("TC_SAI_NGUON")
        expected["so_ung_vien"] = len(uv)
    elif tac == "phan_tich_cau_hoi":
        if type(kq.get("thuc_the")) is not list or type(kq.get("ham_de_xuat")) is not list:
            loi("TC_SAI_NGUON")
    else:
        expected.update({k: kq[k] for k in ("trang_thai", "tang", "co_can_cu", "co_mau_thuan", "can_duyet", "nhan")})
        if (expected["trang_thai"] not in ("co_can_cu", "khong_thay_can_cu") or expected["tang"] not in (1, 2, 3)
                or any(type(expected[k]) is not bool for k in ("co_can_cu", "co_mau_thuan", "can_duyet"))
                or type(expected["tang"]) is not int or expected["nhan"] not in (None, "vang", "xanh")
                or (expected["co_can_cu"] and expected["trang_thai"] != "co_can_cu")
                or (expected["nhan"] == "xanh" and (expected["tang"] != 1 or expected["can_duyet"] or kq.get("ai") is not None))
                or (expected["co_mau_thuan"] and (not expected["can_duyet"] or expected["nhan"] == "xanh"))
                or (not expected["co_can_cu"] and (expected["trang_thai"] != "khong_thay_can_cu" or expected["nhan"] is not None))):
            loi("TC_SAI_NGUON")
    if json_chuan(tt) != json_chuan(expected):
        loi("TC_SAI_NGUON")
    out = {"phien_ban": 1, "ma_yeu_cau": h["ma_yeu_cau"], "tac_vu": tac,
           "giai_doan": h["giai_doan"], "tom_tat": deepcopy(tt), "ket_qua": deepcopy(kq),
           "nguon": deepcopy(nguon), "bam_ho_so": h["bam_ho_so"], "bam_cau_hinh": h["bam_cau_hinh"],
           "bam_danh_muc": h["bam_danh_muc"], "phien_ban_engine": h["phien_ban_engine"], "canh_bao": deepcopy(h["canh_bao"])}
    raw = json_chuan(out)
    if len(raw) > min(_TRAN["tep_toi_da_byte"], doc.tran["tep_toi_da_byte"]):
        loi("TC_QUA_GIOI_HAN")
    viec.kiem_huy()
    tep = viec.tai_tep_ra("ket-qua-tra-cuu.json", raw, "application/json")
    viec.tien_do(95, "Đang kiểm xác nhận tệp kết quả từ Core.")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ket-qua-tra-cuu.json" or tep["kich_thuoc"] != len(raw):
        loi("TC_SAI_NGUON")
    truong = {"tac_vu": tac, **{k: expected[k] for k in _TT}, "tra_loi": kq.get("tra_loi") if tac == "soan_tra_loi" else None,
              "nhom_de_xuat": kq.get("nhom_de_xuat") if tac == "phan_loai" else None,
              "loai_de_xuat": kq.get("loai_de_xuat") if tac == "phan_loai" else None, "tep_json": tep}
    return {"loai": "truong", "truong": truong}
