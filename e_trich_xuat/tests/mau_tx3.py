"""Fixture DEMO TX-3: đăng ký tạm chỉ trong test, không thay manifest runtime."""

from copy import deepcopy
import json
from pathlib import Path

from kho_tri_thuc_sdk.engine import kiem_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import EngineTrichXuat, GOC_GOI, ghim_cau_hinh, tao_app
from e_trich_xuat.docx import doc_docx
from e_trich_xuat.hau_kiem import hau_kiem
from e_trich_xuat.ngan import NganBoNho
from e_trich_xuat.tham_so import bam_bytes, json_bytes
from e_trich_xuat.tich_hop import chuan_bi
from e_trich_xuat.xuat import xuat_ket_qua


PHIEU = json.loads((GOC_GOI / "engine.json").read_text(encoding="utf-8"))
VD = next(v for v in PHIEU["chay_thu_demo"] if v["nang_luc"] == "trich.chuan_bi@1")
HAU_KIEM = {"ma": "trich.hau_kiem@1", "ten": "Hậu kiểm từng ô DEMO, chưa đăng ký",
            "nhan": ["tra_loi_ai"], "tra": "bang_trich_xuat",
            "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 120}, "huy_duoc": True}
XUAT = {"ma": "trich.xuat_ket_qua@1", "ten": "Xuất JSON/Excel DEMO, chưa đăng ký",
        "nhan": ["bang_trich_xuat"], "tra": "truong",
        "truong_ra": [{"ma": "tep_json", "ten": "Tệp JSON", "kieu": "tep"},
                      {"ma": "tep_excel", "ten": "Tệp Excel", "kieu": "tep"},
                      {"ma": "so_tham_so", "ten": "Số tham số", "kieu": "so"},
                      {"ma": "so_can_soat", "ten": "Số cần soát", "kieu": "so"},
                      {"ma": "co_can_cu", "ten": "Có căn cứ", "kieu": "co_khong"}],
        "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 120}, "huy_duoc": True}


def app_tx3():
    p = deepcopy(PHIEU)
    p["nang_luc"] += [deepcopy(HAU_KIEM), deepcopy(XUAT)]
    p["loai_du_lieu_rieng"] += [{"ma": "tra_loi_ai", "ten": "Trả lời AI có trích dẫn"},
                                {"ma": "bang_trich_xuat", "ten": "Bảng thông tin trích xuất"}]
    p["chay_thu_demo"] = []
    assert kiem_phieu(p, GOC_GOI) == []
    app = EngineTrichXuat(p, thu_muc_goi=GOC_GOI)
    app.ngan = NganBoNho()
    with app.ngan.lo() as lo:
        lo.them("cau_hinh", {}, {"ngan_sach_token_vao_toi_da": 100000})
    app.nang_luc("trich.doc_docx@1")(lambda viec: doc_docx(viec, phien_ban_engine="e_trich_xuat 0.3.0"))
    app.nang_luc("trich.chuan_bi@1")(lambda viec: chuan_bi(
        viec, ghim_cau_hinh(viec, app), phien_ban_engine="e_trich_xuat 0.3.0"))
    app.nang_luc("trich.hau_kiem@1")(hau_kiem)
    app.nang_luc("trich.xuat_ket_qua@1")(xuat_ket_qua)
    return app


def ts_demo(bo=None, **doi):
    ts = deepcopy(VD["tham_so"])
    if bo is not None:
        ts["bo_tham_so_json"] = json_bytes(bo).decode("utf-8")
        ts["bam_bo_tham_so"] = bam_bytes(ts["bo_tham_so_json"].encode("utf-8"))
    ts.update(doi)
    return ts


def chuan_bi_demo(core=None, app=None, *, ts=None, dau_vao=None):
    core, app = core or CoreGia(), app or app_tx3()
    kq = core.chay_thu(app, "trich.chuan_bi@1", deepcopy(dau_vao or VD["dau_vao"]),
                      ts or ts_demo())
    assert kq["trang_thai"] == "XONG", kq
    return core, app, kq["ket_qua"]


def o_ai(v, tai_lieu, cau=None):
    cau = cau if cau is not None else v
    ds = []
    if cau:
        dau = tai_lieu.index(cau)
        ds = [{"cau": cau, "bat_dau": dau, "ket_thuc": dau + len(cau)}]
    return {"gia_tri": v, "don_vi": None, "ghi_chu": None, "trich_dan": ds}


def ai_demo(req, data=None):
    r = req["yeu_cau_ai"]
    if data is None:
        vals = {"TT-01": "DEMO-001", "TT-02": "1.000.000 VND"}
        data = {ma: o_ai(vals.get(ma) if vals.get(ma) in r["tai_lieu"] else None, r["tai_lieu"])
                if vals.get(ma) else o_ai(None, r["tai_lieu"]) for ma in r["khuon_tra_loi"]["required"]}
    return {"loai": "tra_loi_ai", "tra_loi_ai": {
        "phien_ban": 1, "trang_thai": "co_can_cu", "tra_loi": "Phản hồi AI giả DEMO.",
        "du_lieu": deepcopy(data), "trich_dan": [],
        "kiem_trich_dan": {"dat": True, "loi": []}, "nha_cung_cap": "local",
        "model": "DEMO-model-gia", "ly_do_chon_model": "DEMO",
        "ma_prompt": r["ma_prompt"], "phien_ban_prompt": r["phien_ban_prompt"],
        "phien_ban_engine": "DEMO-ai-gia 1", "bam_dau_vao": bam_bytes(json_bytes(req)),
        "chuyen_tiep": deepcopy(r["chuyen_tiep"]), "canh_bao": []}}


def bang_demo():
    core, app, req = chuan_bi_demo()
    ai = ai_demo(req)
    kq = core.chay_thu(app, "trich.hau_kiem@1", ai)
    assert kq["trang_thai"] == "XONG", kq
    return core, app, kq["ket_qua"]


def chay_demo_tx3():
    core, app, req = chuan_bi_demo()
    ai = ai_demo(req)
    bang = core.chay_thu(app, "trich.hau_kiem@1", ai)
    assert bang["trang_thai"] == "XONG", bang
    app.phieu["chay_thu_demo"] = [
        {"nang_luc": HAU_KIEM["ma"], "ten": "Hậu kiểm độc lập từng ô DEMO (chưa đăng ký)",
         "dau_vao": ai},
        {"nang_luc": XUAT["ma"], "ten": "Xuất đủ JSON/Excel DEMO (chưa đăng ký)",
         "dau_vao": bang["ket_qua"]},
    ]
    return core.chay_thu_demo(app)
