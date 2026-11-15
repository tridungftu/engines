"""Fixture DEMO TX-3 dùng phiếu và handlers thật; không đăng ký thay runtime."""

from copy import deepcopy
import json
from pathlib import Path

from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import GOC_GOI, tao_app
from e_trich_xuat.tham_so import bam_bytes, json_bytes


PHIEU = json.loads((GOC_GOI / "engine.json").read_text(encoding="utf-8"))
VD = next(v for v in PHIEU["chay_thu_demo"] if v["nang_luc"] == "trich.chuan_bi@1")


def app_tx3(core):
    app = tao_app()
    core.nap_engine(app)
    core.dat_cau_hinh(app.ma, {"ngan_sach_token_vao_toi_da": 100000})
    return app


def ts_demo(bo=None, **doi):
    ts = deepcopy(VD["tham_so"])
    if bo is not None:
        ts["bo_tham_so_json"] = json_bytes(bo).decode("utf-8")
        ts["bam_bo_tham_so"] = bam_bytes(ts["bo_tham_so_json"].encode("utf-8"))
    ts.update(doi)
    return ts


def chuan_bi_demo(core=None, app=None, *, ts=None, dau_vao=None):
    core = core or CoreGia()
    app = app or app_tx3(core)
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
    from e_trich_xuat.demo import nap_ho_so_demo
    core = CoreGia()
    app = app_tx3(core)
    nap_ho_so_demo(core, app)
    return [kq for kq in core.chay_thu_demo(app)
            if kq["ten"] in {vd["ten"] for vd in PHIEU["chay_thu_demo"]
                             if vd["nang_luc"] in ("trich.hau_kiem@1", "trich.xuat_ket_qua@1")}]
