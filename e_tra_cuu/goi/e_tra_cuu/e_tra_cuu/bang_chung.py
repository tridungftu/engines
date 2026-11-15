"""TC-7: nguồn/snapshot và quan hệ trường do cửa Core cấp, không từ model.

kiem_chung_tra_loi là seam C-TC-03 CHƯA có trong SDK thật. Tầng 1 dùng
trích dẫn đã được Core duyệt cùng trường; không mở lại tệp theo QĐ-4.
"""

from copy import deepcopy
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .cau_hoi import sai_khuon
from .chuan_bi_ai import _bo_van_ban_da_nap, kiem_tham_so
from .kiem_dau_vao import (DocNguonCore, bam, json_chuan, kiem_bam,
                          kiem_du_lieu, loi)
from .ngu_canh_ai import (_ma_doan, RANH_GIOI, dung_khuon, dung_ngu_canh,
                          kiem_ngan_sach, qua_ngan_sach)


TOM_TAT = ("trang_thai", "so_doan", "so_ung_vien", "tang", "co_can_cu",
           "co_mau_thuan", "can_duyet", "nhan")
_TRAN = {"tep_toi_da_byte": 20971520, "tong_doc_toi_da_byte": 67108864,
         "ho_so_toi_da_byte": 65536}


def _doi_tuong(v, keys, *, ai=False):
    if type(v) is not dict or set(v) != set(keys):
        if ai:
            sai_khuon()
        loi("TC_SAI_NGUON")
    return v


def _phan_hoi(pb):
    _doi_tuong(pb, ("loai", "tra_loi_ai"), ai=True)
    a = _doi_tuong(pb["tra_loi_ai"], ("phien_ban", "trang_thai", "tra_loi", "du_lieu", "trich_dan",
        "kiem_trich_dan", "nha_cung_cap", "model", "ly_do_chon_model", "ma_prompt", "phien_ban_prompt",
        "phien_ban_engine", "bam_dau_vao", "chuyen_tiep", "canh_bao"), ai=True)
    if pb["loai"] != "tra_loi_ai" or type(a["phien_ban"]) is not int or a["phien_ban"] != 1:
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
    if (a["trang_thai"] not in ("co_can_cu", "khong_thay_can_cu")
            or type(a["trich_dan"]) is not list or type(a["canh_bao"]) is not list
            or any(type(x) is not str for x in a["canh_bao"])):
        sai_khuon()
    kt = _doi_tuong(a["kiem_trich_dan"], ("dat", "loi"), ai=True)
    if type(kt["dat"]) is not bool or type(kt["loi"]) is not list or any(type(x) is not str for x in kt["loi"]):
        sai_khuon()
    return a


def doc_ho_so(viec, cua, phien_ban, kiem_cau_hinh, *, chuan_bi=False):
    """Kiểm bytes/quyền sống trước khi xét có hoặc không có căn cứ."""
    viec.kiem_huy()
    pb = viec.dau_vao
    raw = json_chuan(pb)
    if len(raw) > _TRAN["tep_toi_da_byte"] or len(raw.decode("utf-8")) > 500000:
        loi("TC_QUA_GIOI_HAN")
    a = _phan_hoi(pb) if pb.get("loai") == "tra_loi_ai" else None
    if a is None:
        _doi_tuong(pb, ("loai", "ho_so_tra_cuu"))
        if pb["loai"] != "ho_so_tra_cuu":
            loi("TC_SAI_NGUON")
        h = _doi_tuong(pb["ho_so_tra_cuu"], ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ho_so",
            "bam_ho_so", "bam_cau_hinh", "bam_danh_muc", "phien_ban_engine", "tom_tat", "canh_bao"))
        c = h
        if h["giai_doan"] != "da_nhan":
            loi("TC_SAI_GIAI_DOAN")
        if h["phien_ban_engine"] != "e_tra_cuu " + phien_ban or h["bam_danh_muc"] is not None or h["canh_bao"] != []:
            loi("TC_SAI_NGUON")
        if len(raw) > _TRAN["ho_so_toi_da_byte"]:
            loi("TC_QUA_GIOI_HAN")
    else:
        ct = _doi_tuong(a["chuyen_tiep"], ("tra_cuu",))
        c = _doi_tuong(ct["tra_cuu"], ("phien_ban", "ma_yeu_cau", "tac_vu", "ho_so", "bam_ho_so",
                                     "bam_cau_hinh", "bam_ngu_canh_ai"))
    if type(c["phien_ban"]) is not int or c["phien_ban"] != 1 or c["tac_vu"] != "soan_tra_loi":
        loi("TC_SAI_NGUON")
    if viec.tham_so and not chuan_bi:
        sai_khuon()
    p = viec.ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if cua is None or not callable(getattr(cua, "doc_quyen", None)):
        loi("TC_CHUA_CO_CUA_CORE")
    cap = cua.doc_quyen(viec.id)
    if type(cap) is not dict or any(type(cap.get(k)) is not dict for k in ("tep", "nguon", "dau_vao", "ngu_canh_core")):
        loi("TC_CHUA_CO_CUA_CORE")
    if (json_chuan(cap["dau_vao"]) != raw or cap.get("ma_yeu_cau") != c["ma_yeu_cau"]
            or cap.get("tac_vu") != c["tac_vu"] or cap["ngu_canh_core"].get("phap_nhan_id") != p):
        loi("TC_SAI_NGUON")
    doc = DocNguonCore(viec, _TRAN.copy())
    doc.giay_cap = deepcopy(cap)
    s = doc.doc_ref({"tep": c["ho_so"], "bam": c["bam_ho_so"]})
    keys = {"phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ngu_canh_core", "cau_hinh", "nguon", "du_lieu", "ket_qua"}
    _doi_tuong(s, keys | ({"ai", "kiem_chung_core"} if a is not None and s.get("du_lieu", {}).get("tang") == 1
                         else {"ai"} if a is not None else set()))
    if (type(s["phien_ban"]) is not int or s["phien_ban"] != 1 or s["ket_qua"] is not None
            or any(s[k] != c[k] for k in ("ma_yeu_cau", "tac_vu"))):
        loi("TC_SAI_NGUON")
    if s["giai_doan"] != ("cho_ai" if a is not None else "da_nhan"):
        loi("TC_SAI_GIAI_DOAN")
    if json_chuan(s["ngu_canh_core"]) != json_chuan(cap["ngu_canh_core"]):
        loi("TC_SAI_NGUON")
    ch = kiem_cau_hinh(s["cau_hinh"])
    if json_chuan(ch) != json_chuan(s["cau_hinh"]) or bam(json_chuan(ch["gia_tri"])) != kiem_bam(c["bam_cau_hinh"]):
        loi("TC_SAI_NGUON")
    doc.tran = ch["gia_tri"]["ngan_sach"]
    if c["ho_so"]["kich_thuoc"] > doc.tran["tep_toi_da_byte"] or doc.tong_doc > doc.tran["tong_doc_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    kiem_ngan_sach(s["du_lieu"], doc.tran)
    d = deepcopy(s["du_lieu"])
    if "nguon" in d and d["tang"] != 1:
        d["nguon"] = [_bo_van_ban_da_nap(n) for n in d["nguon"]]
    da_kiem = kiem_du_lieu(doc, {"tac_vu": "soan_tra_loi", "du_lieu": d, "ngu_canh_core": s["ngu_canh_core"]})
    if json_chuan(da_kiem) != json_chuan(s["du_lieu"]) or json_chuan(list(doc.nguon.values())) != json_chuan(s["nguon"]):
        loi("TC_SAI_NGUON")
    if a is None:
        tt = dict.fromkeys(TOM_TAT)
        tt["tang"] = d["tang"]
        if json_chuan(h["tom_tat"]) != json_chuan(tt) or len(raw) > doc.tran["ho_so_toi_da_byte"]:
            loi("TC_SAI_NGUON")
    else:
        ai = _doi_tuong(s["ai"], ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien", "khuon_tra_loi",
                                 "tai_lieu", "map_nguon", "doan", "bam_ngu_canh_ai", "ngan_sach"))
        ts = kiem_tham_so({**{k: ai[k] for k in ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien")},
                          "tac_vu": "soan_tra_loi"}, "soan_tra_loi")
        if d["tang"] == 1 and json_chuan(s["kiem_chung_core"]) != json_chuan(cap.get("kiem_chung_tra_loi")):
            loi("TC_SAI_NGUON")
        tl, maps, doan, khuon = ngu_canh_soan(s, viec)
        ns = ngan_sach_ai(tl, khuon, doc.tran)
        for k, v in {"tai_lieu": tl, "map_nguon": maps, "doan": doan, "khuon_tra_loi": khuon, "ngan_sach": ns}.items():
            if json_chuan(ai[k]) != json_chuan(v):
                loi("TC_SAI_NGUON")
        if (kiem_bam(ai["bam_ngu_canh_ai"]) != bam(tl.encode("utf-8"))
                or kiem_bam(c["bam_ngu_canh_ai"]) != kiem_bam(ai["bam_ngu_canh_ai"])):
            loi("TC_SAI_NGUON")
        yc = {"loai": "yeu_cau_ai", "yeu_cau_ai": {"phien_ban": 1, **ts, "tai_lieu": tl,
              "khuon_tra_loi": khuon, "bat_buoc_trich_dan": True, "chuyen_tiep": a["chuyen_tiep"]}}
        if (a["ma_prompt"] != ai["ma_prompt"] or a["phien_ban_prompt"] != ai["phien_ban_prompt"]
                or kiem_bam(a["bam_dau_vao"]) != bam(json_chuan(yc))):
            loi("TC_SAI_NGUON")
        if len(json_chuan(a["chuyen_tiep"])) > doc.tran["chuyen_tiep_toi_da_byte"]:
            qua_ngan_sach()
    return s, doc, cap, a


def ngan_sach_ai(tl, khuon, ns):
    if len(tl) > ns["ai_toi_da_ky_tu"] or len(json_chuan(khuon)) > ns["khuon_toi_da_byte"]:
        qua_ngan_sach()
    return {"so_ky_tu": len(tl), "so_byte_utf8": len(tl.encode("utf-8")),
            "khuon_byte": len(json_chuan(khuon)), "token_thuc": None, "trang_thai_token": "chua_do"}


def ngu_canh_soan(s, viec):
    if s["du_lieu"]["tang"] != 1:
        return (*dung_ngu_canh(s, viec), dung_khuon(s))
    # Trích dẫn đã duyệt trong hồ sơ Core, không giả nó là toàn văn vừa đọc.
    phan, maps, doan, dai = [], [], [], 0

    def ghi(chu):
        nonlocal dai
        viec.kiem_huy()
        if dai + len(chu) > s["cau_hinh"]["gia_tri"]["ngan_sach"]["ai_toi_da_ky_tu"]:
            qua_ngan_sach()
        phan.append(chu)
        dai += len(chu)

    ghi(json_chuan({"quy_tac": RANH_GIOI, "tac_vu": "soan_tra_loi", "tang": 1,
                   "cau_hoi": s["du_lieu"]["cau_hoi"], "thuc_the": s["du_lieu"]["thuc_the"]}).decode("utf-8") + "\n")
    cac_doan = []
    for i, b in enumerate(s["kiem_chung_core"]["bang_chung"]):
        n = b["nguon"]
        x = {**n, "bat_dau": b["bat_dau"], "ket_thuc": b["ket_thuc"]}
        md = _ma_doan(x)
        ghi(json_chuan({"ma_doan": md, "nguon": n, "truong": b["truong"], "thuc_the": b["thuc_the"],
                       "gia_tri": b["gia_tri"], "don_vi": b["don_vi"]}).decode("utf-8") + "\n")
        a = dai
        ghi(b["cau"])
        maps.append({"ai_bat_dau": a, "ai_ket_thuc": dai, "ma_nguon": n["ma_nguon"],
            "nguon_bat_dau": b["bat_dau"], "nguon_ket_thuc": b["ket_thuc"], "vai_tro": "noi_dung",
            "duong_dan_snapshot": ["kiem_chung_core", "bang_chung", i, "cau"], "snapshot_bat_dau": 0,
            "snapshot_ket_thuc": len(b["cau"]), "ma_doan": md, "ma_ung_vien": None})
        doan.append({"ma_doan": md, **{k: n[k] for k in ("ma_nguon", "phien_ban_nguon", "bam_goc", "bam_van_ban")},
                     "bat_dau": b["bat_dau"], "ket_thuc": b["ket_thuc"], "ai_bat_dau": a,
                     "ai_ket_thuc": dai, "ma_ung_vien": None})
        cac_doan.append({**x, "nguyen_van": b["cau"], "vi_tri": {k: b["vi_tri"][k] for k in ("trang", "hop")}})
        ghi("\n")
    khuon_s = deepcopy(s)
    khuon_s["du_lieu"]["bang_chung"] = cac_doan
    return "".join(phan), maps, doan, dung_khuon(khuon_s)


def chuan_bi_tang_mot(viec, cua, phien_ban, kiem_cau_hinh):
    """Lớp bọc TC-4 cho Core chọn AI tầng 1; kết quả luôn tối đa Vàng."""
    # Giữ nhánh TC-4 cũ từ chối nếu Core chưa cấp profile trường đã kiểm.
    cap = cua.doc_quyen(viec.id) if cua is not None else None
    if type(cap) is not dict or "kiem_chung_tra_loi" not in cap:
        loi("TC_SAI_GIAI_DOAN")
    s, doc, cap, _ = doc_ho_so(viec, cua, phien_ban, kiem_cau_hinh, chuan_bi=True)
    from .kiem_chung import kiem_bang_chung
    bang, ly_do, _ = kiem_bang_chung(s, doc, cap, viec)
    if ly_do or not bang:
        loi("TC_SAI_GIAI_DOAN")
    ts = kiem_tham_so(viec.tham_so, "soan_tra_loi")
    s["kiem_chung_core"] = deepcopy(cap["kiem_chung_tra_loi"])
    tl, maps, doan, khuon = ngu_canh_soan(s, viec)
    ns = ngan_sach_ai(tl, khuon, doc.tran)
    s.update(giai_doan="cho_ai", ai={**ts, "tai_lieu": tl, "map_nguon": maps, "doan": doan,
        "khuon_tra_loi": khuon, "bam_ngu_canh_ai": bam(tl.encode("utf-8")), "ngan_sach": ns})
    raw = json_chuan(s)
    if len(raw) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    ct = {"tra_cuu": {"phien_ban": 1, "ma_yeu_cau": s["ma_yeu_cau"], "tac_vu": "soan_tra_loi", "ho_so": None,
          "bam_ho_so": bam(raw), "bam_cau_hinh": bam(json_chuan(s["cau_hinh"]["gia_tri"])),
          "bam_ngu_canh_ai": s["ai"]["bam_ngu_canh_ai"]}}
    if len(json_chuan(ct)) > doc.tran["chuyen_tiep_toi_da_byte"]:
        qua_ngan_sach()
    viec.tien_do(90, "Đang ghim bằng chứng tầng một cho Local AI tại Core.")
    tep = viec.tai_tep_ra("ho-so-chuan-bi-ai.json", raw, "application/json")
    viec.tien_do(95, "Đã gửi bằng chứng tầng một, đang kiểm trạng thái việc.")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ho-so-chuan-bi-ai.json" or tep["kich_thuoc"] != len(raw):
        loi("TC_SAI_NGUON")
    ct["tra_cuu"]["ho_so"] = tep
    if len(json_chuan(ct)) > doc.tran["chuyen_tiep_toi_da_byte"]:
        qua_ngan_sach()
    return {"loai": "yeu_cau_ai", "yeu_cau_ai": {"phien_ban": 1, **ts, "tai_lieu": tl,
        "khuon_tra_loi": khuon, "bat_buoc_trich_dan": True, "chuyen_tiep": ct}}
