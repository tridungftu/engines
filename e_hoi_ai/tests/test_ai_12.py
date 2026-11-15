"""AI-12: fixture DEMO chép độc lập; CoreGia + Local HTTP giả, 0 Cloud."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from e_hoi_ai import chay
from e_hoi_ai.khuon_json import doc_json, json_chuan, khop
from e_hoi_ai.vai_tro_khuon import TIEN_TO
from local_gia import core_demo
from test_hoi_tai_lieu import khong_mang_ngoai_va_khong_cloud, local


BO = doc_json((Path(__file__).with_name("fixture_ai_12.json")).read_bytes())
CAC_CA = BO["ca"]


def hoi(local, ca):
    local.tra_loi = deepcopy(ca["phan_hoi"])
    return core_demo().chay_thu(chay.app, "ai.hoi_theo_yeu_cau@1", deepcopy(ca["yeu_cau"]))


@pytest.mark.parametrize("ca", CAC_CA, ids=lambda c: c["ten"])
def test_khuon_producer_di_qua_xong_va_co_can_cu(local, ca):
    truoc = json_chuan(ca)
    kq = hoi(local, ca)
    assert kq["trang_thai"] == "XONG", kq
    ra = kq["ket_qua"]["tra_loi_ai"]
    assert ra["kiem_trich_dan"] == {"dat": True, "loi": []}, ra["kiem_trich_dan"]
    assert ra["trang_thai"] == "co_can_cu" and ra["canh_bao"] == []
    assert ra["du_lieu"] == ca["phan_hoi"]["du_lieu"]
    vao = ca["yeu_cau"]["yeu_cau_ai"]
    assert khop(ra["du_lieu"], vao["khuon_tra_loi"])
    assert json_chuan(ra["chuyen_tiep"]) == json_chuan(vao["chuyen_tiep"])
    assert ra["bam_dau_vao"] == "sha256:" + sha256(json_chuan(ca["yeu_cau"])).hexdigest()
    assert ra["nha_cung_cap"] == "local" and local.so_luot_hoi == 1
    for t in ra["trich_dan"]:
        assert vao["tai_lieu"][t["bat_dau"]:t["ket_thuc"]] == t["cau"]
    wire = json_chuan(local.yeu_cau).decode("utf-8")
    assert vao["chuyen_tiep"][next(iter(vao["chuyen_tiep"]))]["ho_so"]["tep_id"] not in wire
    assert json_chuan(ca) == truoc


def ca_sua(i, duong, gia_tri):
    ca = deepcopy(CAC_CA[i])
    v = ca["phan_hoi"]["du_lieu"]
    for k in duong[:-1]:
        v = v[k]
    v[duong[-1]] = gia_tri
    return ca


def bi_chan(ra, ma=None):
    assert ra["trang_thai"] == "XONG", ra
    r = ra["ket_qua"]["tra_loi_ai"]
    assert r["trang_thai"] == "khong_thay_can_cu"
    assert r["tra_loi"] == "không thấy căn cứ" and r["canh_bao"]
    assert r["kiem_trich_dan"]["dat"] is False
    if ma:
        assert ma in r["kiem_trich_dan"]["loi"]


@pytest.mark.parametrize("i,path,v", [
    (0, ["nhom_de_xuat"], "99"),
    (0, ["loai_de_xuat"], "DEMO-NGOAI-DANH-MUC"),
    (0, ["diem"], 1.01),
    (0, ["de_nghi_chuyen_bo"], "false"),
    (1, ["ham_de_xuat", 0, "ten"], "m9.ham_khong_duoc_cap"),
    (1, ["phu_thuoc_thoi_diem"], 0),
    (2, ["xep_hang", 0, "ma_ung_vien"], "DEMO-KHONG-CO"),
    (2, ["xep_hang", 0, "diem"], 1.1),
    (3, ["co_mau_thuan"], "false"),
    (4, ["diem", 0, "nhan"], "da_duyet"),
    (4, ["diem", 0, "ma_diem"], "DEMO-DIEM-KHONG-CO"),
])
def test_metadata_sai_enum_const_kieu_van_bi_chan(local, i, path, v):
    kq = hoi(local, ca_sua(i, path, v))
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None, kq
    assert kq["loi"]["ma"] == "AI_TRA_SAI_KHUON"
    assert local.so_luot_hoi == 2


@pytest.mark.parametrize("i,path,v", [
    (1, ["thuc_the", 0, "gia_tri"], "DEMO-VAY-BIA"),
    (1, ["ham_de_xuat", 0, "tham_so", "ma_khoan_vay"], "DEMO-VAY-BIA"),
    (3, ["khang_dinh", 0, "gia_tri", "so"], 9999999),
    (3, ["khang_dinh", 0, "gia_tri", "so"], 100),
    (3, ["khang_dinh", 0, "gia_tri", "tien_te"], "USD"),
    (3, ["khang_dinh", 1, "gia_tri"], "2026-10-31"),
    (3, ["khang_dinh", 1, "gia_tri"], "2026-10-3"),
    (3, ["khang_dinh", 0, "don_vi"], "USD"),
])
def test_bia_gia_tri_trich_van_bi_chan(local, i, path, v):
    bi_chan(hoi(local, ca_sua(i, path, v)), "DU_LIEU_NGOAI_TRICH_DAN")
    assert local.so_luot_hoi == 1


@pytest.mark.parametrize("i,path", [(0, ["can_cu", 0]), (3, ["khang_dinh", 0, "can_cu", 0]), (4, ["diem", 0, "trai"])])
@pytest.mark.parametrize("sai", ["cau", "bat_dau", "ket_thuc"])
def test_cau_trich_va_offset_phai_khop_dung_khong_tu_chua(local, i, path, sai):
    ca = deepcopy(CAC_CA[i])
    v = ca["phan_hoi"]["du_lieu"]
    for k in path:
        v = v[k]
    v[sai] = "DEMO câu không tồn tại." if sai == "cau" else v[sai] + 1
    bi_chan(hoi(local, ca), "TRICH_DAN_SAI")
    assert local.so_luot_hoi == 1


@pytest.mark.parametrize("i", range(5))
def test_quote_ngoai_bia_khong_duoc_metadata_che_loi(local, i):
    ca = deepcopy(CAC_CA[i])
    ca["phan_hoi"]["truong"][0] = {"gia_tri": "DEMO bịa", "trich_dan": "DEMO bịa"}
    bi_chan(hoi(local, ca), "TRICH_DAN_SAI")


def test_khong_lay_gia_tri_tu_quote_cua_khoan_khac(local):
    ca = ca_sua(3, ["khang_dinh", 0, "gia_tri"], {"so": 2000000, "tien_te": "USD"})
    cau_khac = "Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, ngày 2026-11-01."
    ca["phan_hoi"]["truong"].append({"gia_tri": cau_khac, "trich_dan": cau_khac})
    bi_chan(hoi(local, ca), "DU_LIEU_NGOAI_TRICH_DAN")


def test_khong_ghep_so_va_tien_te_khac_cum_trong_quote_rong(local):
    ca = ca_sua(3, ["khang_dinh", 0, "gia_tri", "tien_te"], "USD")
    vao = ca["yeu_cau"]["yeu_cau_ai"]
    # Quote chứa cả 1.000.000 VND và 2.000.000 USD; 1.000.000 USD vẫn là bịa.
    q = ca["phan_hoi"]["truong"][0]["trich_dan"]
    q += "\nKhoản vay DEMO-VAY-B có giá trị 2.000.000 USD, ngày 2026-11-01."
    a = vao["tai_lieu"].index(q)
    cc = ca["phan_hoi"]["du_lieu"]["khang_dinh"][0]["can_cu"][0]
    cc.update(cau=q, bat_dau=a, ket_thuc=a + len(q))
    bi_chan(hoi(local, ca), "DU_LIEU_NGOAI_TRICH_DAN")


def test_cau_tong_hop_khong_duoc_bia_them_so(local):
    ca = ca_sua(3, ["tra_loi"], "DEMO giá trị 9.000.000 VND.")
    bi_chan(hoi(local, ca), "SO_NGOAI_NGUON")


def ca_chu_thich(schema, du_lieu, *, tai_lieu="DEMO giá trị 1.000.000 VND, ngày 2026-10-30."):
    ca = deepcopy(CAC_CA[0])
    vao = ca["yeu_cau"]["yeu_cau_ai"]
    vao.update(tai_lieu=tai_lieu, khuon_tra_loi=schema, chuyen_tiep={})
    ca["phan_hoi"] = {"du_lieu": du_lieu, "truong": [{"gia_tri": tai_lieu, "trich_dan": tai_lieu}]}
    return ca


def mot_truong(s):
    return {"type": "object", "required": ["DEMO"], "additionalProperties": False, "properties": {"DEMO": s}}


@pytest.mark.parametrize("cach", ["truc_tiep", "ref", "allOf", "oneOf", "anyOf"])
def test_annotation_metadata_theo_schema_thuc_su_ap_dung(local, cach):
    node = {"type": "string", "enum": ["can_xem"], "$comment": TIEN_TO + "metadata"}
    s = mot_truong(node)
    if cach == "ref":
        s["$defs"] = {"nhan": node}
        s["properties"]["DEMO"] = {"$ref": "#/$defs/nhan"}
    elif cach != "truc_tiep":
        s["properties"]["DEMO"] = {cach: [node] + ([] if cach == "allOf" else [{"type": "integer"}])}
    ra = hoi(local, ca_chu_thich(s, {"DEMO": "can_xem"}))
    assert ra["ket_qua"]["tra_loi_ai"]["kiem_trich_dan"] == {"dat": True, "loi": []}
    assert ra["ket_qua"]["tra_loi_ai"]["trang_thai"] == "co_can_cu"


@pytest.mark.parametrize("cach", ["anyOf", "oneOf"])
def test_annotation_trong_nhanh_khong_khop_khong_mien_kiem(local, cach):
    s = mot_truong({cach: [{"type": "integer", "$comment": TIEN_TO + "metadata"}, {"type": "string"}]})
    bi_chan(hoi(local, ca_chu_thich(s, {"DEMO": "DEMO bịa"})), "DU_LIEU_NGOAI_TRICH_DAN")


def test_annotation_xung_dot_khong_ha_chuan_trich_xuat(local):
    s = mot_truong({"type": "integer", "$comment": TIEN_TO + "metadata",
                   "allOf": [{"$comment": TIEN_TO + "trich_xuat"}]})
    bi_chan(hoi(local, ca_chu_thich(s, {"DEMO": 9999999})), "DU_LIEU_NGOAI_TRICH_DAN")


@pytest.mark.parametrize("node", [
    {"type": "integer", "$comment": TIEN_TO + "chua_co"},
    {"type": "object", "$comment": TIEN_TO + "metadata"},
    {"type": "array", "$comment": TIEN_TO + "metadata"},
])
def test_annotation_sai_tu_choi_truoc_goi_local(local, node):
    ra = hoi(local, ca_chu_thich(mot_truong(node), {"DEMO": 1}))
    assert ra["loi"]["ma"] == "KHUON_KHONG_HOP_LE" and local.so_luot_hoi == 0


@pytest.mark.parametrize("gia_tri", ["2026-10-31", "2026-10-3", "100"])
def test_enum_const_khong_tu_duoc_mien_kiem_gia_tri_trich(local, gia_tri):
    ca = ca_chu_thich(mot_truong({"type": "string", "enum": [gia_tri]}), {"DEMO": gia_tri})
    bi_chan(hoi(local, ca), "DU_LIEU_NGOAI_TRICH_DAN")


def test_chuyen_tiep_tu_khai_khong_mien_khuon_khac(local):
    ca = ca_chu_thich(mot_truong({"type": "integer"}), {"DEMO": 9999999})
    ca["yeu_cau"]["yeu_cau_ai"]["chuyen_tiep"] = {"tra_cuu": {"phien_ban": 1, "tac_vu": "phan_loai"}}
    bi_chan(hoi(local, ca), "DU_LIEU_NGOAI_TRICH_DAN")


def test_profile_khong_cho_danh_dau_gia_tri_thanh_metadata(local):
    ca = deepcopy(CAC_CA[3])
    item = ca["yeu_cau"]["yeu_cau_ai"]["khuon_tra_loi"]["properties"]["khang_dinh"]["items"]
    item["properties"]["gia_tri"]["$comment"] = TIEN_TO + "metadata"
    ra = hoi(local, ca)
    assert ra["loi"]["ma"] == "KHUON_KHONG_HOP_LE" and local.so_luot_hoi == 0


def schema_span():
    return {"type": "object", "$comment": TIEN_TO + "trich_dan", "additionalProperties": False,
            "required": ["cau", "bat_dau", "ket_thuc"], "properties": {
                "cau": {"type": "string"}, "bat_dau": {"type": "integer"}, "ket_thuc": {"type": "integer"}}}


def test_giu_tung_lan_cau_lap_unicode_khong_index_chua_offset(local):
    q = "DEMO A\u0301nh\u200b Dương 😀."
    vb = q + "\n" + q
    spans = [{"cau": q, "bat_dau": a, "ket_thuc": a + len(q)} for a in (0, len(q) + 1)]
    ca = ca_chu_thich(mot_truong({"type": "array", "items": schema_span()}), {"DEMO": spans}, tai_lieu=vb)
    ca["phan_hoi"]["truong"] = [{"gia_tri": q, "trich_dan": q}]
    ra = hoi(local, ca)["ket_qua"]["tra_loi_ai"]
    assert ra["trang_thai"] == "co_can_cu" and ra["trich_dan"] == spans


def test_can_cu_rong_khong_muon_quote_ngoai(local):
    s = {"type": "object", "required": ["gia_tri", "can_cu"], "properties": {
        "gia_tri": {"type": "integer", "$comment": TIEN_TO + "trich_xuat"},
        "can_cu": {"type": "array", "items": schema_span()}}}
    ca = ca_chu_thich(s, {"gia_tri": 1000000, "can_cu": []})
    bi_chan(hoi(local, ca), "DU_LIEU_NGOAI_TRICH_DAN")


@pytest.mark.parametrize("a", [True, 1.0])
def test_offset_phai_int_thuc_khong_chua_thanh_int(local, a):
    ca = ca_sua(4, ["diem", 0, "trai", "bat_dau"], a)
    ra = hoi(local, ca)
    if a is True:
        assert ra["loi"]["ma"] == "AI_TRA_SAI_KHUON"
    else:
        bi_chan(ra, "TRICH_DAN_SAI")


def test_trich_dan_null_dung_khuon_dc_khong_phai_gia_tri_bia(local):
    ca = ca_sua(4, ["diem", 0, "trai"], None)
    ra = hoi(local, ca)["ket_qua"]["tra_loi_ai"]
    assert ra["kiem_trich_dan"] == {"dat": True, "loi": []}
    assert ra["du_lieu"]["diem"][0]["trai"] is None


def test_khong_dung_annotation_citation_de_giau_gia_tri_khac(local):
    s = schema_span()
    s["properties"]["gia_tri"] = {"type": "integer"}
    q = "DEMO"
    ca = ca_chu_thich(s, {"cau": q, "bat_dau": 0, "ket_thuc": 4, "gia_tri": 9999999}, tai_lieu=q)
    bi_chan(hoi(local, ca), "TRICH_DAN_SAI")
