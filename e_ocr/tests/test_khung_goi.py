"""Kiểm cổng SDK, loại dữ liệu chung và tính độc lập của khung OCR-0."""

from hashlib import sha256
import json
from pathlib import Path

import pytest

from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia, nap_engine_tu_goi

from kiem_doc_lap import kiem_doc_lap


GOC_REPO = Path(__file__).resolve().parents[2]
GOI = GOC_REPO / "e_ocr" / "goi" / "e_ocr"
CAC_NANG_LUC = {
    "ocr.doc_tai_lieu@1": "van_ban_tai_lieu",
    "ocr.doc_van_ban@1": "van_ban",
    "ocr.xuat_word@1": "tep",
}


def test_tu_khai_bao_va_nap_goi_khi_thieu_cau_hinh():
    from e_ocr import PHIEN_BAN

    app = Engine.tu_khai_bao(GOI / "engine.json")
    assert app.ma == "e_ocr"
    assert app.phieu["phien_ban"] == PHIEN_BAN
    assert app.phieu["phien_ban_manifest"] == 2
    assert nap_engine_tu_goi(GOI).ma == app.ma
    assert app.phieu["loai_du_lieu_rieng"] == [
        {"ma": "van_ban_tai_lieu", "ten": "Văn bản tài liệu có vị trí"}
    ]
    assert {muc["ma"]: muc["tra"] for muc in app.phieu["nang_luc"]} == CAC_NANG_LUC
    for muc in app.phieu["nang_luc"]:
        assert muc["nhan"] == ["tep"]
        assert muc["gioi_han"] == {
            "tep_toi_da_mib": 20,
            "mime": ["application/pdf", "image/png", "image/jpeg"],
            "thoi_han_giay": 900,
        }
        assert muc["huy_duoc"] is True
        tham_so, = muc["tham_so"]
        assert (tham_so["ma"], tham_so["kieu"], tham_so["mac_dinh"]) == ("nguon", "chon", "tu_dong")
        assert [chon["ma"] for chon in tham_so["lua_chon"]] == ["tu_dong", "chi_abbyy", "chi_tesseract"]


@pytest.mark.parametrize("nang_luc", ["ocr.xuat_word@1"])
@pytest.mark.parametrize("nguon", [None, "chi_abbyy", "chi_tesseract"])
def test_ham_tam_bao_chua_lam_qua_core_gia(nang_luc, nguon):
    core = CoreGia()
    tep = core.them_tep("DEMO.png", b"DEMO", "image/png")
    kq = core.chay_thu(
        nap_engine_tu_goi(GOI), nang_luc, {"loai": "tep", "tep": tep},
        {} if nguon is None else {"nguon": nguon},
    )
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "CHUA_LAM"
    assert kq["loi"]["thu_lai_duoc"] is False
    assert kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0


def test_schema_sao_chep_dung_bam():
    chung = GOC_REPO / "_chung" / "contract" / "van_ban_tai_lieu.schema.json"
    trong_goi = GOI / "contract" / chung.name
    assert sha256(trong_goi.read_bytes()).digest() == sha256(chung.read_bytes()).digest()
    schema = json.loads(trong_goi.read_text(encoding="utf-8"))
    assert set(schema["properties"]) == {"loai", "van_ban_tai_lieu"}
    assert set(schema["properties"]["van_ban_tai_lieu"]["properties"]) == {
        "phien_ban", "van_ban", "trang", "nguon_doc", "ly_do_chuyen_nguon", "so_trang",
        "phien_ban_engine", "bam_dau_vao", "canh_bao",
    }
    assert "dong" not in schema["$defs"]["doan"]["required"]
    assert "tu" not in schema["$defs"]["dong"]["required"]
    assert "nghi_ngo" not in schema["$defs"]["tu"]["required"]


def test_goi_doc_lap():
    assert kiem_doc_lap(GOI) == []


@pytest.mark.parametrize("ma", [
    "import kho_tri_thuc",
    "from kho_tri_thuc.sdk_core.engine import Engine",
    "from kho_tri_thuc_sdk import Bootstrap",
    "from kho_tri_thuc_sdk.engine_legacy import SDKEngine",
    "__import__('kho_tri_thuc.core')",
    "import importlib\nimportlib.import_module('kho_tri_thuc.core')",
    "import thu_vien_chua_duoc_phep",
])
def test_kiem_doc_lap_phat_hien_import_cam(tmp_path, ma):
    (tmp_path / "DEMO.py").write_text(ma, encoding="utf-8")
    assert kiem_doc_lap(tmp_path)


@pytest.mark.parametrize("ten", ["__pycache__", "DEMO.pyc"])
def test_kiem_doc_lap_phat_hien_tep_cam(tmp_path, ten):
    (tmp_path / ten).touch()
    assert kiem_doc_lap(tmp_path)
