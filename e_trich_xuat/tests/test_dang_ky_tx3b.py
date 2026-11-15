"""Contract và DEMO đăng ký thật TX-3b, chỉ dữ liệu DEMO/CoreGia."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import tao_app
from e_trich_xuat.demo import nap_ho_so_demo
from e_trich_xuat.hau_kiem import kiem_bang
from e_trich_xuat.tham_so import bam_bytes, json_bytes
from mau_tx3 import GOC_GOI, PHIEU, bang_demo


SCHEMA = json.loads((GOC_GOI / "contract/bang_trich_xuat.schema.json").read_text(encoding="utf-8"))
KIEM = Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)


def test_schema_nguon_va_goi_khop_sha_lf():
    goc = Path(__file__).resolve().parents[2]
    a = (goc / "_chung/contract/bang_trich_xuat.schema.json").read_bytes().replace(b"\r\n", b"\n")
    b = (GOC_GOI / "contract/bang_trich_xuat.schema.json").read_bytes().replace(b"\r\n", b"\n")
    assert a == b and hashlib.sha256(a).digest() == hashlib.sha256(b).digest()
    Draft202012Validator.check_schema(SCHEMA)
    KIEM.validate(bang_demo()[2])


def test_khai_bao_hau_kiem_xuat_va_loai_du_lieu_dung_hop_dong():
    nl = {n["ma"]: n for n in PHIEU["nang_luc"]}
    assert (nl["trich.hau_kiem@1"]["nhan"], nl["trich.hau_kiem@1"]["tra"]) == (["tra_loi_ai"], "bang_trich_xuat")
    xuat = nl["trich.xuat_ket_qua@1"]
    assert (xuat["nhan"], xuat["tra"]) == (["bang_trich_xuat"], "truong")
    assert [(r["ma"], r["kieu"]) for r in xuat["truong_ra"]] == [
        ("tep_json", "tep"), ("tep_excel", "tep"), ("so_tham_so", "so"),
        ("so_can_soat", "so"), ("co_can_cu", "co_khong")]
    assert {r["ma"]: r["ten"] for r in PHIEU["loai_du_lieu_rieng"]} == {
        "van_ban_tai_lieu": "Văn bản tài liệu có vị trí", "yeu_cau_ai": "Yêu cầu hỏi AI",
        "tra_loi_ai": "Trả lời AI có trích dẫn", "bang_trich_xuat": "Bảng thông tin trích xuất"}


def test_mau_manifest_co_ho_so_that_va_chay_bang_handlers_that():
    core, app = CoreGia(), tao_app()
    # Làm thay tep_id để kiểm helper không dựa ID/thuộc tính nội bộ CoreGia.
    core.them_tep("DEMO-khac.txt", b"DEMO")
    truoc = deepcopy(app.phieu)
    nap_ho_so_demo(core, app)
    assert core.xem_ngan(app.ma, "cau_hinh") == []  # Helper không tự điền cấu hình.
    assert truoc == PHIEU
    mau = {v["nang_luc"]: v for v in app.phieu["chay_thu_demo"]}
    ai = mau["trich.hau_kiem@1"]["dau_vao"]
    meta = ai["tra_loi_ai"]["chuyen_tiep"]["trich_xuat"]
    raw = core.doc_tep(meta["ho_so_hau_kiem"]["tep_id"])
    assert raw == (GOC_GOI / "demo/DEMO-ho-so-hau-kiem.json").read_bytes()
    assert len(raw) == meta["ho_so_hau_kiem"]["kich_thuoc"] > 0
    assert bam_bytes(raw) == meta["bam_ho_so_hau_kiem"]
    kq = core.chay_thu(app, "trich.hau_kiem@1", ai)
    assert kq["trang_thai"] == "XONG", kq
    KIEM.validate(kq["ket_qua"])
    # Mẫu xuất là bảng thật do hậu kiểm tạo, chỉ remap mã tệp/băm request.
    assert kq["ket_qua"] == mau["trich.xuat_ket_qua@1"]["dau_vao"]
    kq = core.chay_thu(app, "trich.xuat_ket_qua@1", kq["ket_qua"])
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    assert core.doc_tep(t["tep_json"]["tep_id"]) == json_bytes(mau["trich.xuat_ket_qua@1"]["dau_vao"])
    assert core.doc_tep(t["tep_excel"]["tep_id"]).startswith(b"PK")


@pytest.mark.parametrize("kieu,v", [
    ("van_ban", "DEMO"), ("so", 1.25), ("so_tien", {"so": "1000000.00", "tien_te": "VND"}),
    ("ngay", "2026-10-30"), ("co_khong", False),
    ("tep", {"tep_id": "DEMO-tep", "ten": "DEMO.txt", "mime": "text/plain", "kich_thuoc": 1}),
])
def test_schema_sau_kieu_va_null_can_soat(kieu, v):
    b = deepcopy(PHIEU["chay_thu_demo"][-1]["dau_vao"])
    r = b["bang_trich_xuat"]["bang"][0]
    r.update(kieu=kieu, kieu_da_chuyen=True, gia_tri=v)
    KIEM.validate(b)
    r.update(gia_tri=None, can_soat=True, ly_do=["DEMO cần soát."])
    b["bang_trich_xuat"]["tom_tat"]["so_can_soat"] = 1
    KIEM.validate(b)
    kiem_bang(b)


@pytest.mark.parametrize("doi", [
    lambda b: b.update(don_vi_offset="utf16"),
    lambda b: b.pop("don_vi_offset"),
    lambda b: b["nguon"].pop("bam_dau_vao"),
    lambda b: b["nguon"].update(bam_van_ban="DEMO-sai-bam"),
    lambda b: b["bang"][0].pop("kieu_da_chuyen"),
    lambda b: b["bang"][0].update(kieu="ngay", kieu_da_chuyen=False, gia_tri="2026-10-30"),
    lambda b: b["bang"][0].update(kieu="ngay", kieu_da_chuyen=True, gia_tri="2026-02-30"),
    lambda b: b["bang"][0].update(kieu="so_tien", kieu_da_chuyen=True, gia_tri={"so": "1,000", "tien_te": "VND"}),
    lambda b: b["bang"][0].update(kieu="so_tien", kieu_da_chuyen=True, gia_tri={"so": True, "tien_te": "VND"}),
    lambda b: b["bang"][0].update(kieu="so_tien", kieu_da_chuyen=True, gia_tri={"so": "1.5"}),
    lambda b: b["bang"][0].update(kieu="so", kieu_da_chuyen=True, gia_tri=True),
    lambda b: b["bang"][0].update(gia_tri=None, can_soat=False),
    lambda b: b["bang"][0]["dan_chung"].clear(),
    lambda b: b["bang"][0]["dan_chung"][0]["vi_tri"].update(so_trang=1),
    lambda b: b["bang"][0].pop("dau_kiem_tam_e6"),
    lambda b: b["bang"][0].pop("phan_hoi_ai"),
    lambda b: b["bang"].extend([deepcopy(b["bang"][0])] * 200),
])
def test_schema_chan_payload_sai(doi):
    pb = deepcopy(PHIEU["chay_thu_demo"][-1]["dau_vao"])
    doi(pb["bang_trich_xuat"])
    with pytest.raises(ValidationError):
        KIEM.validate(pb)


def test_phan_hoi_ai_chi_kiem_toan_khong_xac_nhan_cau_gia():
    from mau_tx3 import ai_demo, chuan_bi_demo
    core, app, req = chuan_bi_demo()
    ai = ai_demo(req)
    ai["tra_loi_ai"]["du_lieu"]["TT-01"]["trich_dan"][0]["cau"] = "Câu giả DEMO"
    kq = core.chay_thu(app, "trich.hau_kiem@1", ai)
    assert kq["trang_thai"] == "XONG", kq
    KIEM.validate(kq["ket_qua"])
    r = kq["ket_qua"]["bang_trich_xuat"]["bang"][0]
    assert r["gia_tri"] is None and r["can_soat"] and not r["dan_chung"]
    assert r["phan_hoi_ai"] == ai["tra_loi_ai"]["du_lieu"]["TT-01"]
    assert "kiểm toán" in SCHEMA["$defs"]["dong"]["properties"]["phan_hoi_ai"]["description"].lower()
