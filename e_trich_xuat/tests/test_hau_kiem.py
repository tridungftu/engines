"""TX-3 hậu kiểm: chỉ DEMO, CoreGia + NganBoNho, 0 Cloud/model thật."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_trich_xuat import hau_kiem as hk
from e_trich_xuat.kiem_tra import kiem_o
from e_trich_xuat.logic import kiem_tra_logic
from e_trich_xuat.tham_so import bam_bytes, json_bytes
from mau_tx3 import (PHIEU, VD, ai_demo, app_tx3, bang_demo, chuan_bi_demo,
                     o_ai, ts_demo)


def chay_ai(doi=None, *, data=None):
    core, app, req = chuan_bi_demo()
    ai = ai_demo(req, data)
    if doi:
        doi(ai["tra_loi_ai"])
    return core.chay_thu(app, "trich.hau_kiem@1", ai), core


def dat(kq):
    assert kq["trang_thai"] == "XONG", kq
    return kq["ket_qua"]["bang_trich_xuat"]


def loi(kq, ma):
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None, kq
    assert kq["loi"] == {"ma": ma, "thong_diep": hk.CAU_LOI[ma], "thu_lai_duoc": False}


def bam_ai(ai, hs):
    r = {"tai_lieu": hs["tai_lieu"]["van_ban"], **hs["yeu_cau_ai"],
         "chuyen_tiep": ai["chuyen_tiep"]}
    ai["bam_dau_vao"] = bam_bytes(json_bytes({"loai": "yeu_cau_ai", "yeu_cau_ai": r}))


def doi_ho_so(core, ai, doi):
    ct = ai["chuyen_tiep"]["trich_xuat"]
    hs = json.loads(core.doc_tep(ct["ho_so_hau_kiem"]["tep_id"]))
    doi(hs)
    raw = json_bytes(hs)
    ct["ho_so_hau_kiem"] = core.them_tep("DEMO-ho-so.json", raw, "application/json")
    ct["bam_ho_so_hau_kiem"] = bam_bytes(raw)
    bam_ai(ai, hs)
    return hs


def test_dung_du_o_thu_tu_tom_tat_bam_nguon_va_dang_ky_that():
    core, app, pb = bang_demo()
    b = pb["bang_trich_xuat"]
    assert [r["ma"] for r in b["bang"]] == ["TT-01", "TT-02"]
    assert [r["gia_tri"] for r in b["bang"]] == ["DEMO-001", "1.000.000 VND"]
    assert b["tom_tat"] == {"so_tham_so": 2, "so_can_soat": 0, "co_can_cu": True}
    assert b["nguon"]["bam_dau_vao"] != b["nguon"]["bam_van_ban"]
    assert b["ai"]["nha_cung_cap"] == "local" and b["ai"]["model"] == "DEMO-model-gia"
    assert b["don_vi_offset"] == "unicode"
    assert all(r["kieu_da_chuyen"] is False for r in b["bang"])
    assert all(r["dau_kiem_tam_e6"].startswith("OK") and "kiem_tra_legacy" not in r for r in b["bang"])
    assert [n["ma"] for n in PHIEU["nang_luc"]] == [
        "trich.doc_docx@1", "trich.chuan_bi@1", "trich.hau_kiem@1", "trich.xuat_ket_qua@1"]
    goc = Path(__file__).resolve().parents[2]
    schema = json.loads((goc / "_chung/contract/bang_trich_xuat.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(pb)
    # Bốn loại chung trước giữ nguyên.
    a = (goc / "_chung/contract/tra_loi_ai.schema.json").read_bytes()
    z = (goc / "e_trich_xuat/goi/e_trich_xuat/contract/tra_loi_ai.schema.json").read_bytes()
    assert a == z and hashlib.sha256(a).digest() == hashlib.sha256(z).digest()
    _, _, req = chuan_bi_demo()
    Draft202012Validator(json.loads(a)).validate(ai_demo(req))


@pytest.mark.parametrize("doi", [
    lambda q: q.update(bat_dau=-1),
    lambda q: q.update(ket_thuc=999999),
    lambda q: q.update(ket_thuc=q["bat_dau"]),
    lambda q: q.update(bat_dau=True),
    lambda q: q.update(ket_thuc=1.0),
    lambda q: q.update(cau="Câu bịa DEMO"),
    lambda q: q.update(bat_dau=q["bat_dau"] + 1, ket_thuc=q["ket_thuc"] + 1),
    lambda q: q.pop("bat_dau"),
])
def test_cau_gia_ha_rieng_o_du_co_chung_true(doi):
    def sua(ai):
        doi(ai["du_lieu"]["TT-02"]["trich_dan"][0])
    kq, _ = chay_ai(sua)
    b = dat(kq)
    assert b["bang"][0]["gia_tri"] == "DEMO-001"
    o = b["bang"][1]
    assert o["gia_tri"] is None and o["can_soat"]
    assert o["nguyen_van"] == "1.000.000 VND" and o["phan_hoi_ai"]["trich_dan"]
    assert "Trích dẫn không khớp" in o["ly_do"][0]
    assert b["tom_tat"] == {"so_tham_so": 2, "so_can_soat": 2, "co_can_cu": True}
    assert b["bang"][0]["kiem_tra_logic"]  # Quy tắc E1 phát hiện thiếu ô đối chiếu.


def test_co_chung_false_khong_ha_o_dung_va_legacy_khong_thay_kiem_nghiem():
    kq, _ = chay_ai(lambda ai: ai.update(kiem_trich_dan={"dat": False, "loi": ["DEMO"]}))
    assert all(not o["can_soat"] for o in dat(kq)["bang"])
    def doi(ai):
        o = ai["du_lieu"]["TT-02"]
        o["trich_dan"] = []  # legacy chấp nhận giá trị tự có trong toàn văn.
    kq, _ = chay_ai(doi)
    o = dat(kq)["bang"][1]
    assert o["gia_tri"] is None and o["can_soat"]
    assert o["dau_kiem_tam_e6"] == "OK (giá trị có nguyên văn trong HĐ)"


def test_mot_cau_gia_trong_nhieu_cau_van_ha_o_va_giu_cau_dung():
    def doi(ai):
        ai["du_lieu"]["TT-02"]["trich_dan"].append({"cau": "DEMO giả", "bat_dau": 0, "ket_thuc": 8})
    kq, _ = chay_ai(doi)
    o = dat(kq)["bang"][1]
    assert o["gia_tri"] is None and len(o["dan_chung"]) == 1
    assert len(o["phan_hoi_ai"]["trich_dan"]) == 2


@pytest.mark.parametrize("v", [None, "", "9.999.999 USD"])
def test_null_thieu_can_cu_khong_tu_suy_tien(v):
    def doi(ai):
        ai["du_lieu"]["TT-02"]["gia_tri"] = v
    kq, _ = chay_ai(doi)
    o = dat(kq)["bang"][1]
    assert o["gia_tri"] is None and o["can_soat"] and o["nguyen_van"] == v
    assert o["kieu"] == "van_ban"


def test_bo_sot_van_du_dong_phan_biet_khong_thay_can_cu():
    kq, _ = chay_ai(lambda ai: ai["du_lieu"].pop("TT-02"))
    b = dat(kq)
    assert [r["ma"] for r in b["bang"]] == ["TT-01", "TT-02"]
    assert b["bang"][1]["ly_do"] == ["AI bỏ sót mã cần trích.", "QT: thiếu giá trị đối chiếu theo bộ đã ghim."]
    assert b["bang"][1]["phan_hoi_ai"] is None
    kq, _ = chay_ai(lambda ai: ai.update(du_lieu=None, trang_thai="khong_thay_can_cu"))
    b = dat(kq)
    assert all(r["gia_tri"] is None and r["can_soat"] for r in b["bang"])
    assert b["tom_tat"]["co_can_cu"] is False
    assert all("không tìm thấy" in r["ly_do"][0] for r in b["bang"])


@pytest.mark.parametrize("doi", [
    lambda ai: ai["du_lieu"].update({"TT-99": deepcopy(ai["du_lieu"]["TT-01"])}),
    lambda ai: ai.update(du_lieu=list(ai["du_lieu"].items()) * 2),
    lambda ai: ai.update(du_lieu=dict(reversed(list(ai["du_lieu"].items())))),
    lambda ai: ai["du_lieu"]["TT-01"].pop("gia_tri"),
    lambda ai: ai["du_lieu"]["TT-01"].update(gia_tri=1000000),
    lambda ai: ai["du_lieu"]["TT-01"].update(trich_dan="DEMO"),
    lambda ai: ai["du_lieu"]["TT-01"].update(la=True),
    lambda ai: ai.pop("du_lieu"),
    lambda ai: ai.update(du_lieu=None),
    lambda ai: ai.update(phien_ban=True),
])
def test_sai_khuon_ma_la_trung_dao_thu_tu_va_thieu_truong(doi):
    kq, _ = chay_ai(doi)
    loi(kq, "AI_TRA_SAI_KHUON")


@pytest.mark.parametrize("doi", [
    lambda ai: ai.update(nha_cung_cap="cloud"),
    lambda ai: ai.update(ma_prompt="DEMO-khac"),
    lambda ai: ai.update(phien_ban_prompt="DEMO-2"),
    lambda ai: ai.update(bam_dau_vao=bam_bytes(b"DEMO-khac")),
    lambda ai: ai["chuyen_tiep"]["trich_xuat"].update(module="module_khac"),
    lambda ai: ai["chuyen_tiep"]["trich_xuat"].update(phien_ban_bo="DEMO-2"),
    lambda ai: ai["chuyen_tiep"]["trich_xuat"].update(loai_hop_dong="KCN"),
    lambda ai: ai["chuyen_tiep"]["trich_xuat"].update(phien_ban=True),
    lambda ai: ai["chuyen_tiep"]["trich_xuat"].update(bam_ho_so_hau_kiem=bam_bytes(b"DEMO-khac")),
    lambda ai: ai["chuyen_tiep"]["trich_xuat"]["ho_so_hau_kiem"].update(kich_thuoc=1),
])
def test_khong_khop_metadata_da_ghim(doi):
    kq, _ = chay_ai(doi)
    loi(kq, "HO_SO_HAU_KIEM_KHONG_HOP_LE")


@pytest.mark.parametrize("doi", [
    lambda h: h.update(phien_ban=2),
    lambda h: h.update(phien_ban=True),
    lambda h: h["bo_tham_so"].update(module="DEMO-module-khac"),
    lambda h: h["tham_so_viec"].update(phien_ban_prompt="DEMO-2"),
    lambda h: h.update(bam_van_ban=bam_bytes(b"DEMO-khac")),
    lambda h: h.update(ma_truong_can_trich=["TT-02", "TT-01"]),
    lambda h: h.update(cac_dong_e1=[]),
    lambda h: h["yeu_cau_ai"].update(tai_lieu="DEMO khác"),
    lambda h: h["cau_truc"][0].update(ket_thuc=999),
    lambda h: h["ngu_canh"].update(phap_nhan_id="DEMO-khac"),
])
def test_ho_so_bam_dung_nhung_quan_he_sai_khong_thay_quyen_core(doi):
    core, app, req = chuan_bi_demo()
    ai = ai_demo(req)
    doi_ho_so(core, ai["tra_loi_ai"], doi)
    loi(core.chay_thu(app, "trich.hau_kiem@1", ai), "HO_SO_HAU_KIEM_KHONG_HOP_LE")


def test_unicode_ngoai_bmp_va_dau_to_hop_offset_python():
    dv = deepcopy(VD["dau_vao"])
    text = "DEMO 😀 e\u0301\nĐiều 1. Thông tin\nCông ty DEMO Ánh Dương 😀."
    dv["van_ban_tai_lieu"]["van_ban"] = text
    core, app, req = chuan_bi_demo(dau_vao=dv)
    data = {"TT-01": o_ai("Công ty DEMO Ánh Dương 😀", text), "TT-02": o_ai(None, text)}
    ai = ai_demo(req, data)
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai))
    o = b["bang"][0]
    assert o["gia_tri"] == data["TT-01"]["gia_tri"]
    q = o["dan_chung"][0]
    assert text[q["bat_dau"]:q["ket_thuc"]] == q["cau"]
    assert q["vi_tri"]["so_trang"] is q["vi_tri"]["hop"] is None
    ai["tra_loi_ai"]["du_lieu"]["TT-01"]["trich_dan"][0]["bat_dau"] += 1
    assert dat(core.chay_thu(app, "trich.hau_kiem@1", ai))["bang"][0]["gia_tri"] is None


def test_tien_ngay_giu_nguyen_van_tt21_suy_ra_chua_xac_nhan():
    dv = deepcopy(VD["dau_vao"])
    text = "DEMO thanh toán 90%; ký 30/10/2026; giá 1.000.000 VND; dự toán 9.000.000 USD."
    dv["van_ban_tai_lieu"]["van_ban"] = text
    bo = json.loads(VD["tham_so"]["bo_tham_so_json"])
    bo["quy_tac"] = []
    bo["cac_dong"] = [dict(bo["cac_dong"][0], ma="TT-20"), dict(bo["cac_dong"][1], ma="TT-21")]
    core, app, req = chuan_bi_demo(ts=ts_demo(bo=bo), dau_vao=dv)
    data = {"TT-20": o_ai("90%", text), "TT-21": o_ai("10%", text, "thanh toán 90%")}
    data["TT-21"]["ghi_chu"] = "Suy ra từ 100% - 90%."
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req, data)))
    assert b["bang"][1]["gia_tri"] is None and b["bang"][1]["nguyen_van"] == "10%"
    # Không lấy số lớn nhất hoặc đoán tiền tệ/ngày từ tên mã.
    assert b["bang"][0]["kieu"] == "van_ban" and b["bang"][0]["gia_tri"] == "90%"


@pytest.mark.parametrize("loai, duoc", [("XD", True), ("KCN", False), ("HD_DEMO", False)])
def test_logic_xd_l2_l3_l5_khong_ap_ma_xd_cho_loai_khac(loai, duoc):
    params = [{"ma": m} for m in ("TT-20", "TT-21", "TT-52", "TT-53", "TT-54")]
    data = {"TT-20": {"gia_tri": "90%", "trich_dan": "thanh toán 90%"},
            "TT-21": {"gia_tri": "15%", "trich_dan": "giữ lại 15%"},
            "TT-52": {"gia_tri": "0,05% và 0,10%", "trich_dan": "phạt 0,05% và 0,10%"}}
    kq = kiem_tra_logic(data, params, loai_hop_dong=loai)
    assert any("L2:" in x for xs in kq.values() for x in xs) is duoc
    assert any("L5:" in x for xs in kq.values() for x in xs) is duoc
    data["TT-20"] = {"gia_tri": "90% và 95%", "trich_dan": "đợt 90% và 95%"}
    kq = kiem_tra_logic(data, params, loai_hop_dong=loai)
    assert any("L3:" in x for xs in kq.values() for x in xs) is duoc


def test_logic_l1_l4_kcn_va_gia_tri_co_can_cu_vi_pham_van_giu():
    params = [{"ma": "TC-01", "bat_buoc": ["thuê đất"], "loai_tru": ["xây dựng"]}]
    data = {"TC-01": {"gia_tri": "Không áp dụng", "trich_dan": "Không áp dụng 10% xây dựng"}}
    kq = kiem_tra_logic(data, params, loai_hop_dong="KCN")
    assert any("L1:" in x for x in kq["TC-01"])
    data["TC-01"]["gia_tri"] = "10%"
    kq = kiem_tra_logic(data, params, loai_hop_dong="KCN")
    assert len(kq["TC-01"]) == 2 and all(x.startswith("L4:") for x in kq["TC-01"])
    bo = json.loads(VD["tham_so"]["bo_tham_so_json"])
    bo["cac_dong"][1]["bat_buoc"] = "thuê đất"
    core, app, req = chuan_bi_demo(ts=ts_demo(bo=bo))
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req)))
    assert b["bang"][1]["gia_tri"] == "1.000.000 VND" and b["bang"][1]["can_soat"]


def test_quy_tac_e1_tong_ty_le_va_ngay_chi_soat_khong_sua():
    from e_trich_xuat.logic import kiem_quy_tac_bo
    bang = {"TT-01": {"gia_tri": "90%"}, "TT-02": {"gia_tri": "15%"}}
    q = [{"kieu": "Tổng tỷ lệ", "ma_tham_so": ["TT-01", "TT-02"], "dieu_kien": "=", "doi_chieu": "100"}]
    assert set(kiem_quy_tac_bo(bang, q)) == {"TT-01", "TT-02"}
    bang["TT-01"]["gia_tri"], bang["TT-02"]["gia_tri"] = "2026-11-01", "2026-10-30"
    q[0] = {"kieu": "Ngày không sau", "ma_tham_so": ["TT-01"], "dieu_kien": "<=", "doi_chieu": "TT-02"}
    assert set(kiem_quy_tac_bo(bang, q)) == {"TT-01", "TT-02"}
    bang["TT-01"]["gia_tri"] = "01/11/2026"
    assert not kiem_quy_tac_bo(bang, q)


def test_doi_bo_dang_kich_hoat_khong_anh_huong_ho_so_cu():
    core, app, req1 = chuan_bi_demo()
    bo = json.loads(VD["tham_so"]["bo_tham_so_json"])
    bo.update(module="module_demo_2", phien_ban_bo="DEMO-2", loai_hop_dong="KCN")
    _, _, req2 = chuan_bi_demo(core, app, ts=ts_demo(bo=bo, phien_ban_prompt="DEMO-2"))
    # Cấm mọi truy cập ngăn ở hậu kiểm: chỉ dùng tệp đã ghim.
    app.ngan.doc = lambda *a, **k: pytest.fail("Không đọc bộ/cấu hình đang kích hoạt")
    b1 = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req1)))
    b2 = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req2)))
    assert b1["phien_ban_bo"] == "DEMO-1" and b1["module"] == "crm_demo"
    assert b2["phien_ban_bo"] == "DEMO-2" and b2["module"] == "module_demo_2"


@pytest.mark.parametrize("moc", [20, 100])
def test_hau_kiem_huy_va_mat_ack(monkeypatch, moc):
    core, app, req = chuan_bi_demo()
    bao = core._tien_do
    def huy(ma, viec, pt, cau):
        if pt == moc:
            core.huy(viec)
        return bao(ma, viec, pt, cau)
    monkeypatch.setattr(core, "_tien_do", huy)
    truoc = core.so_lan_ghi["ket_qua"]
    kq = core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req))
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == truoc


def test_hau_kiem_mat_ack_chi_ghi_mot_lan():
    core, app, req = chuan_bi_demo()
    truoc = core.so_lan_ghi["ket_qua"]
    core.gay_mat_xac_nhan("ket_qua")
    dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req)))
    assert core.so_lan_ghi["ket_qua"] == truoc + 1


def test_hau_kiem_du_200_ma_doc_lap():
    bo = json.loads(VD["tham_so"]["bo_tham_so_json"])
    bo["quy_tac"] = []
    bo["cac_dong"] = [dict(bo["cac_dong"][0], ma=f"TT-{i:03}", mo_ta="Thông tin DEMO") for i in range(200)]
    core, app, req = chuan_bi_demo(ts=ts_demo(bo=bo))
    text = req["yeu_cau_ai"]["tai_lieu"]
    data = {ma: o_ai("DEMO-001", text) for ma in req["yeu_cau_ai"]["khuon_tra_loi"]["required"]}
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req, data)))
    assert len(b["bang"]) == 200 and b["tom_tat"] == {
        "so_tham_so": 200, "so_can_soat": 0, "co_can_cu": True}


def test_ho_so_loi_van_hanh_khong_thanh_bang_khong_can_cu(monkeypatch):
    from kho_tri_thuc_sdk.engine import LoiDuongTruyen
    core, app, req = chuan_bi_demo()
    def hong(*a, **k):
        raise LoiDuongTruyen("DEMO_TU_CHOI_QUYEN", "Không mở được tệp DEMO.", http_status=403)
    monkeypatch.setattr(core, "_mo_tep", hong)
    kq = core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req))
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] not in ("HO_SO_HAU_KIEM_KHONG_HOP_LE", "AI_TRA_SAI_KHUON")


def test_ho_so_khong_doc_bom_khoa_lap_va_byte_vuot_tran(monkeypatch):
    core, app, req = chuan_bi_demo()
    for raw in (b'{"phien_ban":1,"phien_ban":1}', b'{"phien_ban":NaN}', b"\xef\xbb\xbf{}"):
        ai = ai_demo(req)
        ct = ai["tra_loi_ai"]["chuyen_tiep"]["trich_xuat"]
        ct["ho_so_hau_kiem"] = core.them_tep("DEMO-ho-so.json", raw, "application/json")
        ct["bam_ho_so_hau_kiem"] = bam_bytes(raw)
        loi(core.chay_thu(app, "trich.hau_kiem@1", ai), "HO_SO_HAU_KIEM_KHONG_HOP_LE")
    ai = ai_demo(req)
    ai["tra_loi_ai"]["chuyen_tiep"]["trich_xuat"]["ho_so_hau_kiem"]["kich_thuoc"] = hk.JSON_TOI_DA + 1
    monkeypatch.setattr(core, "_mo_tep", lambda *a, **k: pytest.fail("Không mở tệp đã khai vượt trần"))
    loi(core.chay_thu(app, "trich.hau_kiem@1", ai), "VUOT_GIOI_HAN")


def test_so_trong_gia_tri_khong_khop_mot_phan_so_lon():
    dv = deepcopy(VD["dau_vao"])
    dv["van_ban_tai_lieu"]["van_ban"] = "DEMO số tiền 1000 VND."
    core, app, req = chuan_bi_demo(dau_vao=dv)
    data = {"TT-01": o_ai("100", req["yeu_cau_ai"]["tai_lieu"], "1000 VND"), "TT-02": o_ai(None, "")}
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req, data)))
    assert b["bang"][0]["gia_tri"] is None


@pytest.mark.parametrize("cau, v, dung", [
    ("5.000.000 đồng", "5", False),
    ("Lãi 10,5% năm", "10", False),
    ("Phạt 0,5% giá trị", "5%", False),
    ("Giá 1.100 đồng", "100", False),
    ("1.000.000 đồng", "1.000", False),
    ("01/01/2025", "2025", False),
    ("1.000", ".000", False),
    ("1 100", " 100", False),
    ("10-5", "-5", False),
    ("5.000.000 đồng", "5.000.000", True),
    ("Lãi 10,5% năm", "10,5%", True),
    ("  100 đồng  ", " 100 ", True),
    ("DEMO giá 1.000.000 VND.", "1.000.000 VND", True),
    ("DEMO-001", "DEMO-001", True),
    ("Giá 1000 VND", "100", False),
    ("Giá 100 VND", "10", False),
    ("Lãi 10% năm", "10", False),
    ("Giá 1\u00a0100 đồng", "100", False),
    ("Mã ABC100", "100", False),
    ("100ABC", "100", False),
    ("-5 đồng", "-5", True),
    ("01/01/2025", "01/01/2025", True),
    ("10,5 đồng; giá 10 đồng", "10", True),
])
def test_gia_tri_phai_tron_token_hoac_cum_nguyen_van(cau, v, dung):
    dv = deepcopy(VD["dau_vao"])
    dv["van_ban_tai_lieu"]["van_ban"] = cau
    core, app, req = chuan_bi_demo(
        ts=ts_demo(ma_truong_can_trich_json='["TT-01"]'), dau_vao=dv)
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req, {"TT-01": o_ai(v, cau, cau)})))
    o = b["bang"][0]
    assert o["gia_tri"] == (v if dung else None)
    assert o["can_soat"] is not dung
    assert o["nguyen_van"] == v
    if not dung:
        assert "Giá trị không có nguyên văn" in o["ly_do"][0]


@pytest.mark.parametrize("ds", [["TT-01"], ["TT-02", "TT-01"]])
def test_hoi_co_muc_tieu_giu_thu_tu_khong_soat_ma_ngoai_pham_vi(ds):
    core, app, req = chuan_bi_demo(ts=ts_demo(ma_truong_can_trich_json=json.dumps(ds)))
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req)))
    assert [r["ma"] for r in b["bang"]] == ds
    assert all(not r["can_soat"] for r in b["bang"])


def test_model_uu_tien_trong_tx2_da_chuan_hoa_null():
    core, app, req = chuan_bi_demo(ts=ts_demo(model_uu_tien="  "))
    assert req["yeu_cau_ai"]["model_uu_tien"] is None
    dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req)))


def test_hau_kiem_doc_ho_so_gon_va_ho_so_tx2_cu():
    core, app, req = chuan_bi_demo()
    ai = ai_demo(req)
    meta = ai["tra_loi_ai"]["chuyen_tiep"]["trich_xuat"]
    hs = json.loads(core.doc_tep(meta["ho_so_hau_kiem"]["tep_id"]))
    assert "tai_lieu" not in hs["yeu_cau_ai"]
    gon = dat(core.chay_thu(app, "trich.hau_kiem@1", ai))
    doi_ho_so(core, ai["tra_loi_ai"], lambda h: h["yeu_cau_ai"].update(tai_lieu=h["tai_lieu"]["van_ban"]))
    cu = dat(core.chay_thu(app, "trich.hau_kiem@1", ai))
    assert gon["bang"] == cu["bang"] and gon["tom_tat"] == cu["tom_tat"]


@pytest.mark.parametrize("noi", ["\f", "\n"])
def test_cau_qua_nhieu_trang_khoi_giu_tung_hop_that_va_cau_ai_goc(noi):
    dv = deepcopy(VD["dau_vao"])
    tl = dv["van_ban_tai_lieu"]
    chu = ["DEMO-001", "Giá trị 1.000.000 VND"]
    khoi = [{"loai": "doan", "van_ban": t, "hop": [i, 10, 90, 30]} for i, t in enumerate(chu, 1)]
    if noi == "\f":
        trang = [{"so": i, "rong": 100, "cao": 200, "don_vi": "pt", "khoi": [k]}
                 for i, k in enumerate(khoi, 1)]
    else:
        trang = [{"so": 1, "rong": 100, "cao": 200, "don_vi": "pt", "khoi": khoi}]
    text = noi.join(chu)
    tl.update(van_ban=text, trang=trang, so_trang=len(trang), nguon_doc="tesseract")
    core, app, req = chuan_bi_demo(dau_vao=dv)
    data = {"TT-01": o_ai("DEMO-001", text, text), "TT-02": o_ai("1.000.000 VND", text, text)}
    b = dat(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req, data)))
    ds = b["bang"][0]["dan_chung"]
    assert [q["vi_tri"]["hop"] for q in ds] == [[1, 10, 90, 30], [2, 10, 90, 30]]
    assert [q["vi_tri"]["so_trang"] for q in ds] == ([1, 2] if noi == "\f" else [1, 1])
    assert all(text[q["bat_dau"]:q["ket_thuc"]] == q["cau"] for q in ds)
    assert b["bang"][0]["phan_hoi_ai"]["trich_dan"][0]["cau"] == text


def test_ho_so_sdk_413_tra_ma_vuot_gioi_han_co_dinh(monkeypatch):
    from kho_tri_thuc_sdk.engine import LoiDuongTruyen
    core, app, req = chuan_bi_demo()
    def qua_lon(*a, **k):
        raise LoiDuongTruyen("VUOT_GIOI_HAN_KICH_THUOC", "DEMO quá lớn.", http_status=413)
    monkeypatch.setattr(core, "_mo_tep", qua_lon)
    loi(core.chay_thu(app, "trich.hau_kiem@1", ai_demo(req)), "VUOT_GIOI_HAN")
