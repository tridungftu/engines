"""Kiểm schema/chỗ nối TC-1; mô hình test không phải handler nghiệp vụ."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_tra_cuu.cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from e_tra_cuu.ngan import NganBoNho
from mo_hinh_contract_tc_1 import (
    CAU_LOI, GIAI_DOAN, bam, doc_json, fixture_cat_doan, json_chuan,
    kiem_giai_doan, kiem_quan_he, kiem_schema_moi,
)

REPO = Path(__file__).resolve().parents[2]
GOI = REPO / "e_tra_cuu/goi/e_tra_cuu"
TEN = ["ho_so_tra_cuu", "van_ban_tai_lieu", "yeu_cau_ai", "tra_loi_ai"]
SCHEMA = json.loads((GOI / "contract/ho_so_tra_cuu.schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("ten", TEN)
def test_schema_nguon_ban_chep_nguyen_trang(ten):
    nguon = (REPO / "_chung/contract" / (ten + ".schema.json")).read_bytes()
    chep = (GOI / "contract" / (ten + ".schema.json")).read_bytes()
    assert sha256(nguon.replace(b"\r\n", b"\n")).digest() == sha256(chep.replace(b"\r\n", b"\n")).digest()
    assert nguon == chep
    assert json.loads(chep)["$id"] == f"urn:ktt:contract:{ten}:1"


def test_fixture_nap_bytes_that_va_offset_unicode():
    kho, pb, snapshot = fixture_cat_doan()
    kiem_schema_moi(pb, SCHEMA, SCHEMA)
    assert kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"}) == snapshot
    h = pb["ho_so_tra_cuu"]
    b = kho.core.doc_tep(h["ho_so"]["tep_id"])
    assert len(b) == h["ho_so"]["kich_thuoc"]
    assert bam(b) == h["bam_ho_so"]
    d = snapshot["ket_qua"]["doan"][0]
    assert d["ket_thuc"] < len(d["nguyen_van"].encode("utf-8"))
    assert d["trang"] is None and d["hop"] is None


@pytest.mark.parametrize("truong", SCHEMA["properties"]["ho_so_tra_cuu"]["required"])
def test_moi_truong_payload_required(truong):
    _, pb, _ = fixture_cat_doan()
    del pb["ho_so_tra_cuu"][truong]
    with pytest.raises(AssertionError):
        kiem_schema_moi(pb, SCHEMA, SCHEMA)


@pytest.mark.parametrize("truong", SCHEMA["$defs"]["tom_tat"]["required"])
def test_moi_truong_summary_required(truong):
    _, pb, _ = fixture_cat_doan()
    del pb["ho_so_tra_cuu"]["tom_tat"][truong]
    with pytest.raises(AssertionError):
        kiem_schema_moi(pb, SCHEMA, SCHEMA)


@pytest.mark.parametrize("duong,gia_tri", [
    (("phien_ban",), True), (("phien_ban",), 2), (("tac_vu",), "sql"),
    (("giai_doan",), "XONG"), (("ma_yeu_cau",), " "),
    (("bam_ho_so",), "sha256:DEMO"), (("bam_danh_muc",), ""),
    (("phien_ban_engine",), "0.1.0"), (("ho_so", "mime"), "text/plain"),
    (("ho_so", "kich_thuoc"), 20971521), (("ho_so", "kich_thuoc"), -1),
    (("tom_tat", "so_doan"), 5001), (("tom_tat", "so_doan"), -1),
    (("tom_tat", "so_ung_vien"), 51), (("tom_tat", "tang"), True),
    (("tom_tat", "co_can_cu"), 0), (("tom_tat", "nhan"), "do"),
])
def test_schema_tu_choi_sai_kieu_enum_tran(duong, gia_tri):
    _, pb, _ = fixture_cat_doan()
    v = pb["ho_so_tra_cuu"]
    for k in duong[:-1]:
        v = v[k]
    v[duong[-1]] = gia_tri
    with pytest.raises(AssertionError):
        kiem_schema_moi(pb, SCHEMA, SCHEMA)


@pytest.mark.parametrize("truong,gia_tri", [
    ("so_doan", 0), ("so_doan", 5000), ("so_doan", None),
    ("so_ung_vien", 50), ("tang", 3), ("nhan", "xanh"),
])
def test_schema_bien_hop_le_khong_chung_minh_nghiep_vu(truong, gia_tri):
    _, pb, _ = fixture_cat_doan()
    pb["ho_so_tra_cuu"]["tom_tat"][truong] = gia_tri
    kiem_schema_moi(pb, SCHEMA, SCHEMA)


def test_them_truong_tuy_chon_tuong_thich():
    _, pb, _ = fixture_cat_doan()
    pb["ho_so_tra_cuu"]["ghi_chu_phien_ban_sau"] = None
    kiem_schema_moi(pb, SCHEMA, SCHEMA)


@pytest.mark.parametrize("tac_vu,giai_doan", [
    (t, g) for t in GIAI_DOAN
    for g in SCHEMA["properties"]["ho_so_tra_cuu"]["properties"]["giai_doan"]["enum"]
    if g not in GIAI_DOAN[t]
])
def test_cap_tac_vu_giai_doan_sai(tac_vu, giai_doan):
    kho, pb, _ = fixture_cat_doan()
    pb["ho_so_tra_cuu"].update(tac_vu=tac_vu, giai_doan=giai_doan)
    kiem_schema_moi(pb, SCHEMA, SCHEMA)  # enum đúng vẫn sai quan hệ
    with pytest.raises(LoiNghiepVu) as e:
        kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"})
    assert e.value.ma == "TC_SAI_GIAI_DOAN"


@pytest.mark.parametrize("tac_vu,giai_doan", [
    (t, g) for t, tap in GIAI_DOAN.items() for g in sorted(tap)
])
def test_cap_tac_vu_giai_doan_hop_le_ve_mat_trang_thai(tac_vu, giai_doan):
    # Chỉ kiểm bảng trạng thái, không nhận là đã chạy 5 handler nghiệp vụ.
    assert kiem_giai_doan(tac_vu, giai_doan) is None


@pytest.mark.parametrize("kieu", ["hop_le", "dem_lech", "thieu", "them", "trung", "doi_nguon"])
def test_ung_vien_dem_va_hoan_vi(kieu):
    kho, pb, s = fixture_cat_doan()
    s.update(tac_vu="xep_hang_lai", giai_doan="da_xep_hang")
    s["du_lieu"]["ung_vien"] = [{"ma_ung_vien": "DEMO-UV1", "ma_nguon": "DEMO-NGUON-1"}]
    s["ket_qua"] = {"xep_hang": [{"ma_ung_vien": "DEMO-UV1", "ma_nguon": "DEMO-NGUON-1", "diem": 0.8}]}
    xh = s["ket_qua"]["xep_hang"]
    if kieu == "thieu":
        xh.clear()
    elif kieu == "them":
        xh.append({"ma_ung_vien": "DEMO-UV2", "ma_nguon": "DEMO-NGUON-2", "diem": 0.7})
    elif kieu == "trung":
        xh.append(deepcopy(xh[0]))
    elif kieu == "doi_nguon":
        xh[0]["ma_nguon"] = "DEMO-NGUON-2"
    ref = kho.tai("xep-hang-DEMO.json", json_chuan(s))
    h = pb["ho_so_tra_cuu"]
    h.update(tac_vu="xep_hang_lai", giai_doan="da_xep_hang", ho_so=ref["tep"], bam_ho_so=ref["bam"])
    h["tom_tat"].update(trang_thai="da_xep_hang", so_doan=None, so_ung_vien=2 if kieu == "dem_lech" else 1)
    if kieu == "hop_le":
        assert kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"}) == s
    else:
        with pytest.raises(LoiNghiepVu) as e:
            kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"})
        assert e.value.ma == "TC_SAI_NGUON"


@pytest.mark.parametrize("kieu", ["mat_ref", "sai_bam", "sai_size", "sai_ten", "sai_cau_hinh", "sai_danh_muc", "dem_lech"])
def test_sai_nguon_va_so_dem(kieu):
    kho, pb, _ = fixture_cat_doan()
    h = pb["ho_so_tra_cuu"]
    if kieu == "mat_ref":
        h["ho_so"]["tep_id"] = "DEMO-khong-ton-tai"
    elif kieu == "sai_bam":
        h["bam_ho_so"] = bam(b"DEMO bytes khac")
    elif kieu == "sai_size":
        h["ho_so"]["kich_thuoc"] += 1
    elif kieu == "sai_ten":
        h["ho_so"]["ten"] = "khac-DEMO.json"
    elif kieu == "sai_cau_hinh":
        h["bam_cau_hinh"] = bam(b"DEMO cau hinh khac")
    elif kieu == "sai_danh_muc":
        h["bam_danh_muc"] = bam(b"DEMO danh muc khac")
    else:
        h["tom_tat"]["so_doan"] = 2
    kiem_schema_moi(pb, SCHEMA, SCHEMA)
    with pytest.raises(LoiNghiepVu) as e:
        kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"})
    assert e.value.ma == "TC_SAI_NGUON"
    assert e.value.thong_diep == CAU_LOI["TC_SAI_NGUON"]


@pytest.mark.parametrize("kieu", ["phap_nhan_gia", "offset_sai", "ref_con_hong"])
def test_snapshot_bam_dung_van_khong_chung_minh_quyen_va_quan_he(kieu):
    kho, pb, s = fixture_cat_doan()
    if kieu == "phap_nhan_gia":
        s["ngu_canh_core"]["phap_nhan_id"] = "DEMO-Q"
    elif kieu == "offset_sai":
        s["ket_qua"]["doan"][0]["ket_thuc"] -= 1
    else:
        s["nguon"][0]["van_ban"]["tep"]["tep_id"] = "DEMO-con-khong-ton-tai"
    ref = kho.tai("snapshot-sai-DEMO.json", json_chuan(s))
    pb["ho_so_tra_cuu"].update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
    with pytest.raises(LoiNghiepVu) as e:
        kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"})
    assert e.value.ma == "TC_SAI_NGUON"


@pytest.mark.parametrize("p,ma", [(None, "TC_THIEU_NGU_CANH"), (" ", "TC_THIEU_NGU_CANH"), ("DEMO-Q", "TC_SAI_NGUON")])
def test_ngu_canh_thieu_hoac_khac_quyen(p, ma):
    kho, pb, _ = fixture_cat_doan()
    with pytest.raises(LoiNghiepVu) as e:
        kiem_quan_he(kho, pb, {"phap_nhan_id": p})
    assert e.value.ma == ma


def test_bam_bytes_truoc_parse_khong_bam_lai_object():
    kho, pb, s = fixture_cat_doan()
    b = json.dumps(s, ensure_ascii=False, indent=2).encode("utf-8")
    ref = kho.tai("snapshot-indent-DEMO.json", b)
    h = pb["ho_so_tra_cuu"]
    h.update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
    assert kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"}) == s
    h["bam_ho_so"] = bam(json_chuan(s))
    with pytest.raises(LoiNghiepVu) as e:
        kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"})
    assert e.value.ma == "TC_SAI_NGUON"


@pytest.mark.parametrize("kieu", ["phong_bi", "tep", "tong"])
def test_tran_khong_cat_ngam(kieu):
    kho, pb, _ = fixture_cat_doan()
    if kieu == "phong_bi":
        pb["ghi_chu_DEMO"] = "Đ" * 32768  # ít ký tự hơn bytes
    elif kieu == "tep":
        pb["ho_so_tra_cuu"]["ho_so"]["kich_thuoc"] = 20 * 1024**2 + 1
    else:
        kho.tong_doc = 64 * 1024**2  # mô phỏng đã đọc đủ trần, không tạo tệp lớn
    truoc = deepcopy(pb)
    with pytest.raises(LoiNghiepVu) as e:
        kiem_quan_he(kho, pb, {"phap_nhan_id": "DEMO-P"})
    assert e.value.ma == "TC_QUA_GIOI_HAN"
    assert pb == truoc


@pytest.mark.parametrize("b", [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1e999}', b'"\xff"', b'"\\ud800"'])
def test_json_nghiem(b):
    with pytest.raises(LoiNghiepVu) as e:
        doc_json(b)
    assert e.value.ma == "TC_DAU_VAO_KHONG_HOP_LE"


@pytest.mark.parametrize("ten", TEN)
def test_bo_doc_cau_hinh_khong_gia_lam_validator_chung(ten):
    schema = json.loads((GOI / "contract" / (ten + ".schema.json")).read_bytes())
    ngan = NganBoNho()
    # Thiếu bản ghi trả None trước khi kiểm schema; phải có giá trị để kiểm
    # đúng giới hạn bộ đọc, không sửa mẫu NGAN-0 vì giả định sai của test.
    with ngan.lo() as lo:
        lo.them("cau_hinh", {}, {"nhan": "DEMO"})
    with pytest.raises(CauHinhKhongHopLe):
        doc_cau_hinh(ngan, schema)
