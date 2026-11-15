"""TC-5: phản hồi Local là dữ liệu không tin cậy; tự kiểm snapshot/căn cứ."""

from copy import deepcopy
import math

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .chuan_bi_ai import kiem_tham_so
from .kiem_dau_vao import (DocNguonCore, bam, doi_tuong, json_chuan, kiem_bam,
                          kiem_du_lieu, loi)
from .ngu_canh_ai import dung_khuon, dung_ngu_canh, kiem_ngan_sach, qua_ngan_sach
from .quy_tac_nhom import ap_quy_tac, kiem_bo_quy_tac


_TRAN_DOC = {"tep_toi_da_byte": 20971520, "tong_doc_toi_da_byte": 67108864,
             "ho_so_toi_da_byte": 65536}
_TRUONG_AI = ("phien_ban", "trang_thai", "tra_loi", "du_lieu", "trich_dan", "kiem_trich_dan",
              "nha_cung_cap", "model", "ly_do_chon_model", "ma_prompt", "phien_ban_prompt",
              "phien_ban_engine", "bam_dau_vao", "chuyen_tiep", "canh_bao")
_TRUONG_CT = ("phien_ban", "ma_yeu_cau", "tac_vu", "ho_so", "bam_ho_so", "bam_cau_hinh", "bam_ngu_canh_ai")
_TRUONG_KQ = ("nhom_de_xuat", "loai_de_xuat", "doi_tuong", "diem", "can_cu", "ly_do_cho", "de_nghi_chuyen_bo")


def sai_khuon():
    raise LoiNghiepVu("TC_AI_SAI_KHUON", "Trả lời AI chưa đúng khuôn hoặc căn cứ. Anh gửi lại hồ sơ để kiểm tra.")


def _kiem_doi_tuong_ai(v, cac_truong):
    if type(v) is not dict or set(v) != set(cac_truong):
        sai_khuon()
    return v


def _mang_chu(v):
    return type(v) is list and all(type(x) is str for x in v)


def _kiem_ai(pb):
    _kiem_doi_tuong_ai(pb, ("loai", "tra_loi_ai"))
    if pb["loai"] != "tra_loi_ai":
        sai_khuon()
    a = _kiem_doi_tuong_ai(pb["tra_loi_ai"], _TRUONG_AI)
    if a["nha_cung_cap"] == "cloud":
        raise LoiNghiepVu("TC_CHI_LOCAL", "Phân loại tài liệu chỉ dùng AI cục bộ. Anh chọn lại quy trình Local.")
    if (a["nha_cung_cap"] != "local" or type(a["phien_ban"]) is not int or a["phien_ban"] != 1
            or a["trang_thai"] not in ("co_can_cu", "khong_thay_can_cu")
            or type(a["tra_loi"]) is not str or type(a["trich_dan"]) is not list
            or not _mang_chu(a["canh_bao"])):
        sai_khuon()
    for k in ("model", "ly_do_chon_model", "ma_prompt", "phien_ban_prompt", "phien_ban_engine"):
        if type(a[k]) is not str or not a[k].strip():
            sai_khuon()
    kt = _kiem_doi_tuong_ai(a["kiem_trich_dan"], ("dat", "loi"))
    if type(kt["dat"]) is not bool or not _mang_chu(kt["loi"]):
        sai_khuon()
    try:
        kich_thuoc = len(json_chuan(pb))
    except LoiNghiepVu:
        sai_khuon()
    if kich_thuoc > _TRAN_DOC["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    return a


def _doc_snapshot(viec, cua, a, kiem_cau_hinh):
    p = viec.ngu_canh.get("phap_nhan_id")
    if type(p) is not str or not p.strip():
        loi("TC_THIEU_NGU_CANH")
    if cua is None or not callable(getattr(cua, "doc_quyen", None)):
        loi("TC_CHUA_CO_CUA_CORE")
    cap = cua.doc_quyen(viec.id)
    if type(cap) is not dict or any(type(cap.get(k)) is not dict for k in
            ("tep", "nguon", "ngu_canh_core", "yeu_cau_ai", "nguon_ai")):
        loi("TC_CHUA_CO_CUA_CORE")
    if cap["ngu_canh_core"].get("phap_nhan_id") != p:
        loi("TC_CHUA_CO_CUA_CORE")
    # Giấy cấp gắn yêu cầu AI nguyên gốc và provenance của bước Hỏi AI, không
    # lấy các trường đó từ model/caller rồi tự coi đã xác thực nguồn.
    yc_pb = doi_tuong(cap["yeu_cau_ai"], ("loai", "yeu_cau_ai"), ())
    yc = doi_tuong(yc_pb["yeu_cau_ai"])
    if yc_pb["loai"] != "yeu_cau_ai":
        loi("TC_SAI_NGUON")
    ct_all = doi_tuong(a["chuyen_tiep"], ("tra_cuu",), ())
    ct = doi_tuong(ct_all["tra_cuu"], _TRUONG_CT, ())
    if (json_chuan(ct_all) != json_chuan(yc.get("chuyen_tiep"))
            or type(ct["phien_ban"]) is not int or ct["phien_ban"] != 1
            or ct["tac_vu"] != "phan_loai" or cap.get("tac_vu") != "phan_loai"
            or cap.get("ma_yeu_cau") != ct["ma_yeu_cau"]
            or kiem_bam(a["bam_dau_vao"]) != bam(json_chuan(yc_pb))
            or any(cap["nguon_ai"].get(k) != a[k] for k in ("nha_cung_cap", "model", "phien_ban_engine"))
            or any(yc.get(k) != a[k] for k in ("ma_prompt", "phien_ban_prompt"))):
        loi("TC_SAI_NGUON")
    if len(json_chuan(ct_all)) > 65536:
        qua_ngan_sach()
    doc = DocNguonCore(viec, _TRAN_DOC.copy())
    doc.giay_cap = deepcopy(cap)
    s = doc.doc_ref({"tep": ct["ho_so"], "bam": ct["bam_ho_so"]})
    doi_tuong(s, ("phien_ban", "ma_yeu_cau", "tac_vu", "giai_doan", "ngu_canh_core",
                   "cau_hinh", "nguon", "du_lieu", "ket_qua", "ai"), ())
    if (type(s["phien_ban"]) is not int or s["phien_ban"] != 1 or s["ket_qua"] is not None
            or s["giai_doan"] != "cho_ai" or s["tac_vu"] != "phan_loai"
            or s["ma_yeu_cau"] != ct["ma_yeu_cau"]):
        loi("TC_SAI_NGUON")
    if json_chuan(s["ngu_canh_core"]) != json_chuan(cap["ngu_canh_core"]):
        loi("TC_CHUA_CO_CUA_CORE")
    ch = kiem_cau_hinh(s["cau_hinh"])
    if (json_chuan(ch) != json_chuan(s["cau_hinh"])
            or bam(json_chuan(ch["gia_tri"])) != kiem_bam(ct["bam_cau_hinh"])):
        loi("TC_SAI_NGUON")
    doc.tran = ch["gia_tri"]["ngan_sach"]
    if ct["ho_so"]["kich_thuoc"] > doc.tran["tep_toi_da_byte"] or doc.tong_doc > doc.tran["tong_doc_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    if len(json_chuan(ct_all)) > doc.tran["chuyen_tiep_toi_da_byte"]:
        qua_ngan_sach()
    kiem_ngan_sach(s["du_lieu"], doc.tran)
    d = deepcopy(s["du_lieu"])
    tl = doi_tuong(d["tai_lieu"], ("ma_nguon", "phien_ban_nguon", "goc", "van_ban", "van_ban_tai_lieu"), ())
    tl.pop("van_ban_tai_lieu")
    da_kiem = kiem_du_lieu(doc, {"tac_vu": "phan_loai", "du_lieu": d, "ngu_canh_core": s["ngu_canh_core"]})
    if (json_chuan(da_kiem) != json_chuan(s["du_lieu"])
            or json_chuan(list(doc.nguon.values())) != json_chuan(s["nguon"])):
        loi("TC_SAI_NGUON")
    ai = doi_tuong(s["ai"], ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien", "khuon_tra_loi",
        "tai_lieu", "map_nguon", "doan", "bam_ngu_canh_ai", "ngan_sach"), ())
    ts = kiem_tham_so({"tac_vu": "phan_loai", **{k: ai[k] for k in
                         ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien")}}, "phan_loai")
    tai_lieu, ban_do, doan = dung_ngu_canh(s, viec)
    khuon = dung_khuon(s)
    yeu_cau_dung = {"phien_ban": 1, **ts, "tai_lieu": tai_lieu, "khuon_tra_loi": khuon,
                "bat_buoc_trich_dan": True, "chuyen_tiep": ct_all}
    if (json_chuan(yeu_cau_dung) != json_chuan(yc)
            or any(json_chuan(ai[k]) != json_chuan(v) for k, v in
                   (("tai_lieu", tai_lieu), ("map_nguon", ban_do), ("doan", doan), ("khuon_tra_loi", khuon)))
            or kiem_bam(ai["bam_ngu_canh_ai"]) != bam(tai_lieu.encode("utf-8"))
            or kiem_bam(ct["bam_ngu_canh_ai"]) != ai["bam_ngu_canh_ai"]):
        loi("TC_SAI_NGUON")
    ns_ai = {"so_ky_tu": len(tai_lieu), "so_byte_utf8": len(tai_lieu.encode("utf-8")),
             "khuon_byte": len(json_chuan(khuon)), "token_thuc": None, "trang_thai_token": "chua_do"}
    if json_chuan(ai["ngan_sach"]) != json_chuan(ns_ai):
        loi("TC_SAI_NGUON")
    if len(tai_lieu) > doc.tran["ai_toi_da_ky_tu"] or len(json_chuan(khuon)) > doc.tran["khuon_toi_da_byte"]:
        qua_ngan_sach()
    # Không có bộ mặc định trong mã. Mở bộ quy tắc cấu hình đã ghim qua Core.
    ref = ch["gia_tri"]["quy_tac_nhom"]
    cap_ref = cap["tep"].get(ref["tep_id"])
    if cap_ref is None:
        loi("TC_CHUA_CO_CUA_CORE")
    if kiem_bam(cap_ref.get("bam")) != kiem_bam(ref["bam"]):
        loi("TC_SAI_NGUON")
    bo = kiem_bo_quy_tac(doc.doc_ref(cap_ref), da_kiem["danh_muc"])
    return ct, s, doc, bo


def _kiem_de_xuat(a, s):
    v = _kiem_doi_tuong_ai(a["du_lieu"], _TRUONG_KQ)
    dm = s["du_lieu"]["danh_muc"]
    for k, ds in (("nhom_de_xuat", dm["nhom"]), ("loai_de_xuat", [x for x in dm["loai"] if x["trang_thai"] == "hoat_dong"]),
                  ("doi_tuong", dm["doi_tuong"])):
        if v[k] is not None and (type(v[k]) is not str or v[k] not in {x["ma"] for x in ds}):
            sai_khuon()
    diem = v["diem"]
    if (type(diem) not in (int, float) or (type(diem) is float and not math.isfinite(diem))
            or not 0 <= diem <= 1 or type(v["de_nghi_chuyen_bo"]) is not bool
            or not _mang_chu(v["ly_do_cho"]) or any(not x.strip() for x in v["ly_do_cho"])
            or type(v["can_cu"]) is not list):
        sai_khuon()
    return v


def _kiem_cau(c, s, *, co_ma):
    _kiem_doi_tuong_ai(c, ("cau", "bat_dau", "ket_thuc", "ma_nguon", "ma_doan") if co_ma
            else ("cau", "bat_dau", "ket_thuc"))
    a, z = c["bat_dau"], c["ket_thuc"]
    ai = s["ai"]
    if co_ma and any(type(c[k]) is not str or not c[k].strip() for k in ("ma_nguon", "ma_doan")):
        sai_khuon()
    if (type(a) is not int or type(z) is not int or type(c["cau"]) is not str or not c["cau"].strip()
            or not 0 <= a < z <= len(ai["tai_lieu"]) or ai["tai_lieu"][a:z] != c["cau"]):
        sai_khuon()
    ban_do = [m for m in ai["map_nguon"] if m["ma_nguon"] is not None and m["vai_tro"] == "noi_dung"
            and m["ai_bat_dau"] <= a < z <= m["ai_ket_thuc"]]
    if len(ban_do) != 1:
        sai_khuon()
    m = ban_do[0]
    if co_ma and (c["ma_nguon"] != m["ma_nguon"] or c["ma_doan"] != m["ma_doan"]):
        loi("TC_SAI_NGUON")
    n = next(n for n in s["nguon"] if n["ma_nguon"] == m["ma_nguon"])
    x, y = m["nguon_bat_dau"] + a - m["ai_bat_dau"], m["nguon_bat_dau"] + z - m["ai_bat_dau"]
    vb = s["du_lieu"]["tai_lieu"]["van_ban_tai_lieu"]["van_ban_tai_lieu"]["van_ban"]
    if vb[x:y] != c["cau"]:
        sai_khuon()
    return {"cau": c["cau"], "bat_dau": x, "ket_thuc": y,
            "ai_bat_dau": a, "ai_ket_thuc": z, "ma_doan": m["ma_doan"],
            "nguon": {k: n[k] for k in ("ma_nguon", "tep_id", "phien_ban_nguon", "bam_goc", "bam_van_ban")}}


def phan_loai_tai_lieu(viec, cua_nguon, phien_ban_engine, kiem_cau_hinh):
    viec.kiem_huy()
    if viec.tham_so:
        loi()
    a = _kiem_ai(viec.dau_vao)
    try:
        ct, s, doc, bo = _doc_snapshot(viec, cua_nguon, a, kiem_cau_hinh)
    except LoiNghiepVu as exc:
        if exc.ma == "TC_DAU_VAO_KHONG_HOP_LE":
            loi("TC_SAI_NGUON")
        raise
    if len(json_chuan(viec.dau_vao)) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    v = _kiem_de_xuat(a, s)
    viec.tien_do(30, "Đã đối chiếu yêu cầu AI, nguồn và danh mục tại Core.")
    # Cờ kiểm của Hỏi AI chỉ là dữ liệu tham khảo; không là điều kiện đủ/cần.
    for c in a["trich_dan"]:
        viec.kiem_huy()
        _kiem_cau(c, s, co_ma=False)
    can_cu = []
    for c in v["can_cu"]:
        viec.kiem_huy()
        can_cu.append(_kiem_cau(c, s, co_ma=True))
    giai_doan, kq = ap_quy_tac(s, a, v, can_cu, bo)
    s["ket_qua"], s["giai_doan"] = kq, giai_doan
    s["hau_kiem_ai"] = {k: a[k] for k in ("nha_cung_cap", "model", "phien_ban_engine", "bam_dau_vao")}
    noi_dung = json_chuan(s)
    if len(noi_dung) > doc.tran["tep_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    h = {"phien_ban": 1, "ma_yeu_cau": s["ma_yeu_cau"], "tac_vu": "phan_loai", "giai_doan": giai_doan,
         "ho_so": None, "bam_ho_so": bam(noi_dung), "bam_cau_hinh": ct["bam_cau_hinh"],
         "bam_danh_muc": bam(json_chuan(s["du_lieu"]["danh_muc"])),
         "phien_ban_engine": "e_tra_cuu " + phien_ban_engine,
         "tom_tat": {"trang_thai": giai_doan, "so_doan": None, "so_ung_vien": None, "tang": None,
                     "co_can_cu": bool(can_cu) and a["trang_thai"] == "co_can_cu",
                     "co_mau_thuan": None, "can_duyet": True, "nhan": None},
         "canh_bao": ["Mọi phân loại máy là đề xuất; Core quyết định xếp và duyệt.",
                      "Điểm model không phải xác suất đã hiệu chỉnh."]}
    pb = {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": h}
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    viec.tien_do(90, "Đang gửi đề xuất phân loại và lý do chờ lên Core.")
    tep = viec.tai_tep_ra("ho-so-phan-loai.json", noi_dung, "application/json")
    viec.kiem_huy()
    doc.kiem_tep(tep, json=True)
    if tep["ten"] != "ho-so-phan-loai.json" or tep["kich_thuoc"] != len(noi_dung):
        loi("TC_SAI_NGUON")
    h["ho_so"] = tep
    if len(json_chuan(pb)) > doc.tran["ho_so_toi_da_byte"]:
        loi("TC_QUA_GIOI_HAN")
    return pb
