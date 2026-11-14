"""AI-2 đã kiểm bằng Core giả (CoreGia), Local HTTP giả và hàng rào 0 Cloud."""
from copy import deepcopy
from hashlib import sha256
import json

import pytest
from kho_tri_thuc_sdk.thu import CoreGia
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_hoi_ai import chay
from e_hoi_ai.khuon_json import boc_khuon, doc_json, json_chuan, khop, kiem_khuon
from local_gia import LocalGia, TAI_LIEU, TRA_LOI, ghi_cau_hinh
from test_hoi_tai_lieu import khong_mang_ngoai_va_khong_cloud, local

KHUON = {"type": "object", "required": ["so_tien", "ngay"], "additionalProperties": False,
         "properties": {
             "so_tien": {"type": "object", "required": ["so", "tien_te"], "additionalProperties": False,
                         "properties": {"so": {"type": "integer", "minimum": 0}, "tien_te": {"const": "VND"}}},
             "ngay": {"type": "string", "enum": ["2026-10-30"]},
         }}
DU_LIEU = {"so_tien": {"so": 1000000, "tien_te": "VND"}, "ngay": "2026-10-30"}
PHAN_HOI = {"du_lieu": DU_LIEU, **TRA_LOI}
YEU_CAU = {"phien_ban": 1, "ma_prompt": "demo.hoi", "phien_ban_prompt": "3",
           "prompt": "DEMO: Trích số tiền kèm mã tiền tệ và ngày thanh toán YYYY-MM-DD.",
           "tai_lieu": TAI_LIEU, "khuon_tra_loi": KHUON, "bat_buoc_trich_dan": True,
           "model_uu_tien": None, "chuyen_tiep": {}}


def hoi(*, core=None, **sua):
    return (core or CoreGia()).chay_thu(chay.app, "ai.hoi_theo_yeu_cau@1",
                                       {"loai": "yeu_cau_ai", "yeu_cau_ai": deepcopy({**YEU_CAU, **sua})})


@pytest.mark.parametrize("ollama", [False, True], ids=["openai_compatible", "ollama"])
def test_co_khuon_du_lieu_dung_schema_va_api_cau_truc(local, ollama):
    local.tra_loi = PHAN_HOI
    if ollama:
        local.tags = [{"name": "model-demo"}]
    kq = hoi()
    assert kq["trang_thai"] == "XONG", kq
    ra = kq["ket_qua"]["tra_loi_ai"]
    assert kq["ket_qua"]["loai"] == "tra_loi_ai"
    assert ra["du_lieu"] == DU_LIEU and khop(ra["du_lieu"], KHUON)
    assert ra["phien_ban"] == 1 and ra["trang_thai"] == "co_can_cu"
    assert ra["kiem_trich_dan"] == {"dat": True, "loi": []}
    assert ra["canh_bao"] == [] and ra["nha_cung_cap"] == "local"
    assert ra["ma_prompt"] == "demo.hoi" and ra["phien_ban_prompt"] == "3"
    assert ra["phien_ban_engine"] == "e_hoi_ai " + chay.app.phieu["phien_ban"]
    assert ra["bam_dau_vao"] == "sha256:" + sha256(json_chuan({"loai": "yeu_cau_ai", "yeu_cau_ai": YEU_CAU})).hexdigest()
    for trich in ra["trich_dan"]:
        assert TAI_LIEU[trich["bat_dau"]:trich["ket_thuc"]] == trich["cau"]
    assert [m[0] for m in kq["tien_do"]] == [10, 90]
    assert local.so_luot_hoi == 1
    request = local.yeu_cau[0]
    if ollama:
        assert local.luot[-1] == ("POST", "/api/chat")
        khuon_gui = request["format"]
        assert "response_format" not in request and request["options"] == {"temperature": 0}
    else:
        assert local.luot[-1] == ("POST", "/v1/chat/completions")
        assert request["response_format"]["type"] == "json_schema"
        khuon_gui = request["response_format"]["json_schema"]["schema"]
        assert "format" not in request
    assert khop(PHAN_HOI, khuon_gui)
    assert not khop({**PHAN_HOI, "du_lieu": {}}, khuon_gui)


@pytest.mark.parametrize("sai", [
    {**PHAN_HOI, "du_lieu": {}}, {**PHAN_HOI, "du_lieu": {**DU_LIEU, "ngoai": "DEMO"}},
    {**PHAN_HOI, "du_lieu": {**DU_LIEU, "ngay": 2026}}, {**PHAN_HOI, "du_lieu": None},
    {**PHAN_HOI, "du_lieu": []}, "DEMO không phải JSON", '{"du_lieu":{},"du_lieu":{}}',
    '{"du_lieu":{"so":NaN}}', '{"du_lieu":{"so":1e999}}',
])
def test_sai_khuon_chi_hoi_lai_mot_lan_roi_bao_loi(local, sai):
    local.tra_loi = sai
    kq = hoi()
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "AI_TRA_SAI_KHUON" and not kq["loi"]["thu_lai_duoc"]
    assert local.so_luot_hoi == 2
    assert "Lần trước dữ liệu sai khuôn" in local.yeu_cau[1]["messages"][1]["content"]


def test_hoi_lai_sua_dung_khuon(local):
    local.tra_loi_tung_luot = [{**PHAN_HOI, "du_lieu": {}}, PHAN_HOI]
    kq = hoi()
    assert kq["trang_thai"] == "XONG" and kq["ket_qua"]["tra_loi_ai"]["du_lieu"] == DU_LIEU
    assert local.so_luot_hoi == 2 and [m[0] for m in kq["tien_do"]] == [10, 50, 90]


@pytest.mark.parametrize("s,dat", [(True, True), (False, False), ({"type": "array"}, False)])
def test_schema_boolean_va_contract_du_lieu_chi_nhan_object(local, s, dat):
    local.tra_loi = PHAN_HOI
    kq = hoi(khuon_tra_loi=s)
    if dat:
        assert kq["trang_thai"] == "XONG" and local.so_luot_hoi == 1
    else:
        assert kq["loi"]["ma"] == "AI_TRA_SAI_KHUON" and local.so_luot_hoi == 2


def test_khong_khuon_khong_ep_json_schema_du_lieu_null(local):
    kq = hoi(khuon_tra_loi=None)
    assert kq["trang_thai"] == "XONG"
    ra = kq["ket_qua"]["tra_loi_ai"]
    assert ra["du_lieu"] is None and ra["trang_thai"] == "co_can_cu"
    assert ra["tra_loi"] == "1.000.000 VND\n30/10/2026"
    assert "response_format" not in local.yeu_cau[0] and "format" not in local.yeu_cau[0]


def test_ollama_remote_bi_chan_truoc_gui_du_lieu(local):
    local.tags = [{"name": "model-demo", "remote_host": "cloud.demo.invalid"}]
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and local.so_luot_hoi == 0


def test_ollama_khong_theo_redirect_native_chat(local):
    local.tags = [{"name": "model-demo"}]
    local.chuyen_huong = ("/api/chat", 307)
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and local.so_luot_hoi == 1
    assert local.luot[-1] == ("POST", "/api/chat")


@pytest.mark.parametrize("khuon", [None, KHUON])
def test_rao_json_nguyen_khoi_tuong_thich_ai1(local, khuon):
    local.tra_loi = "```json\n" + json.dumps(TRA_LOI if khuon is None else PHAN_HOI) + "\n```"
    assert hoi(khuon_tra_loi=khuon)["ket_qua"]["tra_loi_ai"]["trang_thai"] == "co_can_cu"


def test_khong_thay_can_cu(local):
    local.tra_loi = {"truong": []}
    ra = hoi(khuon_tra_loi=None)["ket_qua"]["tra_loi_ai"]
    assert ra["trang_thai"] == "khong_thay_can_cu" and ra["tra_loi"] == "không thấy căn cứ"
    assert ra["trich_dan"] == [] and ra["kiem_trich_dan"] == {"dat": True, "loi": []}


@pytest.mark.parametrize("bat_buoc", [True, False])
@pytest.mark.parametrize("phan_hoi", [
    {**PHAN_HOI, "truong": [{"gia_tri": "9.000.000 VND", "trich_dan": "DEMO bịa 9.000.000 VND"}]},
    {**PHAN_HOI, "truong": []},
    {**PHAN_HOI, "du_lieu": {**DU_LIEU, "so_tien": {"so": 9999999, "tien_te": "VND"}}},
    {**PHAN_HOI, "truong": "DEMO sai kiểu"},
])
def test_sai_trich_dan_hoac_du_lieu_khong_duoc_chung_minh_ha_trang_thai(local, bat_buoc, phan_hoi):
    local.tra_loi = phan_hoi
    ra = hoi(bat_buoc_trich_dan=bat_buoc)["ket_qua"]["tra_loi_ai"]
    assert ra["trang_thai"] == "khong_thay_can_cu"
    assert ra["kiem_trich_dan"]["dat"] is False and ra["canh_bao"]
    assert ra["tra_loi"] == "không thấy căn cứ"
    assert khop(ra["du_lieu"], KHUON)  # Giữ khuôn, bước hậu kiểm đọc trạng thái/cảnh báo.
    assert local.so_luot_hoi == 1  # Sai dẫn chứng không được tự hỏi lại như lỗi khuôn.


def test_chuyen_tiep_nguyen_ven_theo_byte_json_chuan_va_khong_gui_local(local):
    chuyen = {"DEMO_khong_gui": "DEMO_CHUYEN_TIEP_RIENG", "a": [None, True, False, 0, -0.0, 1.5,
             {"unicode": "Ánh Dương\n\\\"", "tham_so": [[], {}, ""]}], "bam": "sha256:DEMO"}
    truoc = json_chuan(chuyen)
    local.tra_loi = PHAN_HOI
    ra = hoi(chuyen_tiep=chuyen)["ket_qua"]["tra_loi_ai"]
    assert json_chuan(ra["chuyen_tiep"]) == truoc == json_chuan(chuyen)
    assert "DEMO_CHUYEN_TIEP_RIENG" not in json.dumps(local.yeu_cau, ensure_ascii=False)


@pytest.mark.parametrize("khoa,tran", [("chuyen_tiep", 65536), ("khuon_tra_loi", 32768)])
@pytest.mark.parametrize("vuot", [0, 1])
def test_tran_byte_utf8_dung_bien_khong_cat_ngam(local, khoa, tran, vuot):
    gia_tri = {"DEMO": ""} if khoa == "chuyen_tiep" else {"type": "object", "description": ""}
    n = tran - len(json_chuan(gia_tri)) + vuot
    gia_tri["DEMO" if khoa == "chuyen_tiep" else "description"] = "Á" * (n // 2) + "D" * (n % 2)
    assert len(json_chuan(gia_tri)) == tran + vuot
    local.tra_loi = {**PHAN_HOI, "du_lieu": {}} if khoa == "khuon_tra_loi" else PHAN_HOI
    kq = hoi(**{khoa: gia_tri})
    if vuot:
        assert kq["loi"]["ma"] == "VUOT_GIOI_HAN" and not local.luot
    else:
        assert kq["trang_thai"] == "XONG" and local.so_luot_hoi == 1
        if khoa == "chuyen_tiep":
            assert json_chuan(kq["ket_qua"]["tra_loi_ai"][khoa]) == json_chuan(gia_tri)


@pytest.mark.parametrize("prompt", ["", " \t\n", None])
def test_thieu_prompt(local, prompt):
    kq = hoi(prompt=prompt)
    assert kq["loi"]["ma"] == "THIEU_PROMPT" and not local.luot


@pytest.mark.parametrize("sua", [{"phien_ban": True}, {"phien_ban": 2}, {"tai_lieu": 123},
                                    {"chuyen_tiep": []}, {"chuyen_tiep": {"so": float("nan")}},
                                    {"bat_buoc_trich_dan": 1}, {"model_uu_tien": []}])
def test_dau_vao_sai_khong_goi_local(local, sua):
    kq = hoi(**sua)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and not local.luot


@pytest.mark.parametrize("khoa", ["prompt", "tai_lieu"])
def test_vuot_tran_van_ban_loai_rieng(local, khoa):
    kq = hoi(**{khoa: "D" * 500001})
    assert kq["loi"]["ma"] == "VUOT_GIOI_HAN" and not local.luot


def test_local_tat_khong_cloud(tmp_path, monkeypatch):
    with LocalGia() as may:
        tep = ghi_cau_hinh(tmp_path, may.url, thoi_han=0.1)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"]


def test_local_loi_luc_hoi_lai_khong_bao_sai_khuon(local):
    local.tra_loi = {**PHAN_HOI, "du_lieu": {}}
    def loi_lan_hai(phuong_thuc, duong):
        if phuong_thuc == "POST" and local.so_luot_hoi == 2:
            local.ma_http = 503
    local.khi_nhan = loi_lan_hai
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"]
    assert local.so_luot_hoi == 2


def test_huy_truoc_lan_hoi_lai_khong_post_them(local, monkeypatch):
    core = CoreGia()
    local.tra_loi = {**PHAN_HOI, "du_lieu": {}}
    goc = core._tien_do
    def huy(ma, viec_id, pt, cau):
        if pt == 50:
            core.huy(viec_id)
        return goc(ma, viec_id, pt, cau)
    monkeypatch.setattr(core, "_tien_do", huy)
    kq = hoi(core=core)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert local.so_luot_hoi == 1 and core.so_lan_ghi["ket_qua"] == 0


def test_mat_xac_nhan_khong_goi_lai_local(local):
    local.tra_loi = PHAN_HOI
    core = CoreGia()
    core.gay_mat_xac_nhan("ket_qua")
    assert hoi(core=core)["trang_thai"] == "XONG"
    assert local.so_luot_hoi == 1 and core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1


def test_nhat_ky_khong_lo_noi_dung(local, capsys):
    local.tra_loi = PHAN_HOI
    hoi(chuyen_tiep={"DEMO": "KHONG_GHI_DEMO"})
    out = capsys.readouterr()
    ban_ghi = json.loads(out.err)
    assert set(ban_ghi) == {"ma_prompt", "phien_ban_prompt", "model", "ly_do_chon", "thoi_gian_ms", "ket_qua_kiem"}
    assert ban_ghi["ket_qua_kiem"] == "DAT" and ban_ghi["phien_ban_prompt"] == "3"
    assert not out.out
    assert all(v not in out.err for v in [TAI_LIEU, YEU_CAU["prompt"], "1.000.000", "KHONG_GHI_DEMO"])


@pytest.mark.parametrize("s", [
    {"type": "DEMO"}, {"type": ["object", "object"]}, {"required": "DEMO"}, {"properties": []},
    {"minItems": True}, {"minimum": "DEMO"}, {"multipleOf": 0}, {"enum": []},
    {"enum": [1, 1.0]}, {"items": []}, {"anyOf": []}, {"uniqueItems": 1},
    {"pattern": "DEMO"}, {"format": "date"}, {"unevaluatedProperties": False},
    {"$ref": "https://demo.invalid/schema.json"}, {"$ref": "#/$defs/khong_co"},
    {"$ref": "#/const", "const": {"tu_khoa_la": True}},
    {"$defs": {"x": {"$id": "urn:demo"}}},
])
def test_khuon_sai_hoac_chua_ho_tro_tu_choi_truoc_mang(local, s):
    kq = hoi(khuon_tra_loi=s)
    assert kq["loi"]["ma"] == "KHUON_KHONG_HOP_LE" and not local.luot


@pytest.mark.parametrize("v,s,dat", [
    (True, {"type": "integer"}, False), (1.0, {"type": "integer"}, True),
    (1, {"const": True}, False), (1.0, {"enum": [1]}, True),
    ({"a": None}, {"required": ["a"], "properties": {"a": {"type": ["string", "null"]}}}, True),
    ({"a": 1}, {"properties": {"a": {"type": "string"}}}, False),
    ({"a": 1}, {"additionalProperties": {"type": "integer"}, "minProperties": 1}, True),
    ({}, {"required": ["a"]}, False), ({"a": 1}, {"additionalProperties": False}, False),
    ([1, "DEMO"], {"prefixItems": [{"type": "integer"}], "items": {"type": "string"}}, True),
    ([1, 2], {"prefixItems": [{"type": "integer"}], "items": False}, False),
    ([1, 1.0], {"uniqueItems": True}, False), ([1, True], {"uniqueItems": True}, True),
    ([1], {"minItems": 2}, False), ("Ánh", {"minLength": 3, "maxLength": 3}, True),
    (0.3, {"multipleOf": 0.1}, True), (0.31, {"multipleOf": 0.1}, False),
    (5, {"minimum": 5, "exclusiveMaximum": 6}, True), (5, {"exclusiveMinimum": 5}, False),
    (1, {"allOf": [{"type": "integer"}, {"not": {"const": 2}}]}, True),
    (1, {"anyOf": [{"type": "string"}, {"type": "number"}]}, True),
    (1, {"oneOf": [{"type": "integer"}, {"type": "number"}]}, False),
    ({}, True, True), ({}, False, False),
    ({"x": 1}, {"$defs": {"so": {"type": "integer"}}, "properties": {"x": {"$ref": "#/$defs/so"}}}, True),
])
def test_bo_kiem_schema_tap_con(v, s, dat):
    kiem_khuon(s)
    assert khop(v, s) is dat


def test_ref_noi_bo_duoc_chuyen_goc_khi_gui_local_khong_doi_khuon(local):
    s = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "urn:demo:ai2",
         "$defs": {"tien/te": {"const": "VND"}}, "type": "object", "required": ["tien_te"],
         "properties": {"tien_te": {"$ref": "#/$defs/tien~1te"}}}
    truoc = json_chuan(s)
    local.tra_loi = {"du_lieu": {"tien_te": "VND"}, **TRA_LOI}
    assert hoi(khuon_tra_loi=s)["trang_thai"] == "XONG"
    schema_gui = local.yeu_cau[0]["response_format"]["json_schema"]["schema"]
    assert khop(local.tra_loi, schema_gui)
    assert not khop({**local.tra_loi, "du_lieu": {"tien_te": "USD"}}, schema_gui)
    assert json_chuan(s) == truoc


def test_ref_de_quy_khong_treo_bo_kiem():
    s = {"$ref": "#"}
    with pytest.raises(LoiNghiepVu) as exc:
        kiem_khuon(s)
    assert exc.value.ma == "KHUON_KHONG_HOP_LE"
    assert not khop({}, s)
