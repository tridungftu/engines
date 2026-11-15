"""DC-6: chỉ hậu kiểm phản hồi Local do Core chuyển, không gọi nhà cung cấp."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from . import ho_so as hs
from . import quy_tac as qt
from . import so_chu as sc
from . import chuan_bi_ai as cb
from .vi_tri import loi

_SCHEMA_TL = json.loads((Path(__file__).resolve().parent.parent / "tra_loi_ai.schema.json").read_text(encoding="utf-8"))


def _schema(value, schema):
    try:
        hs.kiem_schema(value, schema)
    except LoiNghiepVu:
        cb.loi_ai("DC_AI_SAI_KHUON")


def _doc_ghim(viec, ngan, cau_hinh, r):
    ct = r["chuyen_tiep"]
    if len(hs.json_bytes(ct)) > cb.TRAN_CHUYEN_TIEP:
        cb.loi_ai("DC_QUA_NGAN_SACH_AI")
    p = ct.get("doi_chieu")
    if type(p) is not dict or type(p.get("ho_so")) is not dict or not p.get("bam_ho_so"):
        loi()
    doc = hs._DocTep(viec, cau_hinh)
    raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, min(20, cau_hinh["ho_so_mib"]) * hs.MIB)
    s = hs.doc_json(raw, viec.kiem_huy)
    if s.get("giai_doan") != "cho_ai" or type(s.get("ai")) is not dict or s["ai"].get("phien_ban") != cb.PHIEN_BAN:
        loi()
    if hs.json_bytes(cb.chuyen_tiep(s, p["ho_so"], raw)) != hs.json_bytes(ct):
        loi()
    scope = cb.pham_vi(viec)
    if s["ai"]["pham_vi"] != scope:
        loi()
    cb.da_ghim(ngan, scope["phap_nhan_id"], hs._phong_bi(s, p["ho_so"], raw), "cho_ai", viec.kiem_huy)
    goc, doc, _ = cb.doc_goc(viec, ngan, cau_hinh, s["ai"]["ho_so_goc"], doc)
    qt.kiem_bat_bien(s, goc)  # Gốc đọc lại từ Core, tuyệt đối không nhận từ nội dung model.
    bo = ("giai_doan", "phien_ban_engine", "ai")
    if {k: v for k, v in s.items() if k not in bo} != {k: v for k, v in goc.items() if k not in bo}:
        loi()
    yc, ban_do, ids = cb.dung_yeu_cau(goc, s["ai"]["tham_so"], viec.kiem_huy)
    if yc != s["ai"]["yeu_cau"] or ban_do != s["ai"]["ban_do"] or ids != s["ai"]["ma_diem"]:
        loi()
    request = cb.phong_bi_yeu_cau(s, p["ho_so"], raw)
    if (r["ma_prompt"] != yc["ma_prompt"] or r["phien_ban_prompt"] != yc["phien_ban_prompt"] or
            r["bam_dau_vao"].lower() != hs.bam(hs.json_bytes(request))):
        loi()
    return s, goc, doc, request


def _trich(cit, m, tai_lieu, goc, diem=None):
    """Kiểm đồng thời ngữ cảnh AI, phía nguồn, offset gốc và phủ vị trí lệch."""
    if cit is None or not m["co_nguon"]:
        return None
    a, b = cit["bat_dau"], cit["ket_thuc"]
    if not m["bat_dau_ai"] <= a < b <= m["ket_thuc_ai"] or tai_lieu[a:b] != cit["cau"]:
        return None
    x, y = a - m["bat_dau_ai"] + m["bat_dau_nguon"], b - m["bat_dau_ai"] + m["bat_dau_nguon"]
    text = goc["van_ban"][m["ben"]]["van_ban_tai_lieu"]["van_ban"]
    if text[x:y] != cit["cau"]:
        return None
    if diem is not None and (diem[m["ben"]] is None or
            not x <= diem[m["ben"]]["bat_dau"] <= diem[m["ben"]]["ket_thuc"] <= y):
        return None
    return {"ben": m["ben"], "cau": cit["cau"], "bat_dau_ai": a, "ket_thuc_ai": b,
            "bat_dau_nguon": x, "ket_thuc_nguon": y}


def phan_loai_diem_lech(viec, ngan, cau_hinh, *, phien_ban_engine):
    viec = sc._ViecCoHan(viec, 300)
    viec.kiem_huy()
    r = viec.dau_vao.get("tra_loi_ai")
    if type(r) is dict and r.get("nha_cung_cap") == "cloud":
        cb.loi_ai("DC_CHI_LOCAL")
    try:
        # JSON hữu hạn/UTF-8/độ sâu nghiêm trước khi kiểm khuôn model.
        hs.doc_json(hs.json_bytes(viec.dau_vao), viec.kiem_huy)
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError, LoiNghiepVu):
        cb.loi_ai("DC_AI_SAI_KHUON")
    _schema(viec.dau_vao, _SCHEMA_TL)
    if r["nha_cung_cap"] != "local":
        cb.loi_ai("DC_CHI_LOCAL")
    if len(hs.json_bytes(viec.dau_vao)) > min(20, cau_hinh["ho_so_mib"]) * hs.MIB:
        cb.loi_ai("DC_QUA_NGAN_SACH_AI")
    viec.tien_do(5, "Đang đọc lại hồ sơ và kiểm nguồn phản hồi Local AI")
    s, goc, doc, request = _doc_ghim(viec, ngan, cau_hinh, r)
    ai, yc = s["ai"], request["yeu_cau_ai"]
    _schema(r["du_lieu"], yc["khuon_tra_loi"])
    rows = r["du_lieu"]["diem"]
    ids = [d["ma_diem"] for d in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(ai["ma_diem"]) or any(not row["ly_do"].strip() for row in rows):
        cb.loi_ai("DC_AI_SAI_KHUON")
    khoa = {"phap_nhan_id": ai["pham_vi"]["phap_nhan_id"], "bam_bo": goc["bo_quy_tac"]["bam"],
        "phien_ban_engine": phien_ban_engine, "bam_cap": hs.bam(hs.json_bytes({"buoc": cb.PHIEN_BAN + ":hau_kiem",
            "pham_vi": ai["pham_vi"], "bam_phan_hoi": hs.bam(hs.json_bytes(viec.dau_vao))}))}
    with cb.luot(viec, ngan, khoa, "dang_hau_kiem_ai", "da_hau_kiem") as (cu, chot):
        if cu is not None:
            p = cu["ho_so_doi_chieu"]
            raw = doc.doc({"tep": p["ho_so"], "bam": p["bam_ho_so"]}, doc.cau_hinh["ho_so_mib"] * hs.MIB)
            out = hs.doc_json(raw, viec.kiem_huy)
            if hs._phong_bi(out, p["ho_so"], raw) != cu:
                loi()
            qt.kiem_bat_bien(out, goc)
            return cu
        out = deepcopy(goc)
        points = {d["ma_diem"]: d for d in out["diem_lech"]}
        maps = {(m["ma_diem"], m["ben"]): m for m in ai["ban_do"]}
        tai_lieu = yc["tai_lieu"]
        co_can_cu = (r["trang_thai"] == "co_can_cu" and r["kiem_trich_dan"]["dat"] and
            not r["kiem_trich_dan"]["loi"] and bool(r["trich_dan"]) and all(
                any(_trich(c, m, tai_lieu, goc) is not None for m in ai["ban_do"]) for c in r["trich_dan"]))
        ket_qua = []
        for row in rows:
            viec.kiem_huy()
            d = points[row["ma_diem"]]
            trich = {ben: _trich(row[key], maps[(row["ma_diem"], ben)], tai_lieu, goc, d)
                     for ben, key in (("word", "trai"), ("ban_ky", "phai"))}
            khong_chac = row["nhan"] == "khong_chac" or any(k in sc.bo_dau(row["ly_do"]).casefold()
                for k in ("khong chac", "chua chac", "khong du can cu", "khong thay can cu"))
            dat = co_can_cu and all(v is not None for v in trich.values()) and not khong_chac
            # Hình thức/nhiễu chỉ là đề nghị cho DC-7, không hạ sàn can_xem của DC-5.
            if dat and row["nhan"] == "nghiem_trong":
                d["muc"] = "nghiem_trong"
            d.update(ly_do_ai=row["ly_do"], cho_phan_loai=False)
            ket_qua.append({**deepcopy(row), "trich_dan_dat": dat, "anh_xa_nguon": trich,
                "cho_dc7": dat and row["nhan"] in ("hinh_thuc", "nhieu_ocr"), "muc_ap_dung": d["muc"]})
        out.update(giai_doan="da_hau_kiem", phien_ban_engine=phien_ban_engine, ho_so_truoc={
            "tep": deepcopy(yc["chuyen_tiep"]["doi_chieu"]["ho_so"]), "bam": yc["chuyen_tiep"]["doi_chieu"]["bam_ho_so"]},
            ai={"phien_ban": cb.PHIEN_BAN, "nha_cung_cap": "local", "model": r["model"],
                "ma_prompt": r["ma_prompt"], "phien_ban_prompt": r["phien_ban_prompt"],
                "bam_yeu_cau": r["bam_dau_vao"], "bam_phan_hoi": hs.bam(hs.json_bytes(viec.dau_vao)),
                "trang_thai": r["trang_thai"], "ket_qua": ket_qua}, da_kiem_du=False, de_nghi_chan=True, ket_luan=None)
        out["kiem_tra"]["phan_loai_ai"] = "dat" if all(k["trich_dan_dat"] for k in ket_qua) else "khong_dat"
        dem = Counter(d["muc"] for d in out["diem_lech"])
        out["tom_tat"].update({"so_" + k: dem[k] for k in qt._MUC})
        out["canh_bao"].append("Đã hậu kiểm phản hồi Local AI; đề nghị hình thức hoặc nhiễu còn chờ đủ bằng chứng Python và OCR.")
        qt.kiem_bat_bien(out, goc)
        raw = hs.json_bytes(out)
        if len(raw) > doc.cau_hinh["ho_so_mib"] * hs.MIB:
            cb.loi_ai("DC_QUA_NGAN_SACH_AI")
        viec.tien_do(85, "Đang gửi hồ sơ hậu kiểm và giữ nguyên sàn quy tắc lên Core")
        tep = viec.tai_tep_ra("ho-so-da-hau-kiem-ai.json", raw, "application/json")
        pb = hs._phong_bi(out, tep, raw)
        chot(pb)
        viec.kiem_huy()
        return pb
