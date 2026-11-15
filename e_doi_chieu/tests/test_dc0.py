import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

ROOT = Path(__file__).resolve().parents[2]
GOI = ROOT / "e_doi_chieu" / "goi" / "e_doi_chieu"
sys.path.insert(0, str(GOI))
chay = importlib.import_module("e_doi_chieu.chay")


def test_mau_ngan_nguyen_ban():
    for ten in ("ngan.py", "cau_hinh.py"):
        def bam(path):
            return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).digest()
        assert bam(GOI / "e_doi_chieu" / ten) == bam(ROOT / "_chung" / "mau-ma" / ten)


def test_core_gia_docx_hong_khong_tra_ket_qua():
    core = CoreGia()
    tep = core.them_tep("DEMO.docx", b"DEMO", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    kq = core.chay_thu(chay.app, "doi_chieu.doc_docx@1", {"loai": "tep", "tep": tep})
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "DC_WORD_KHONG_DOC_DUOC"
    assert kq["ket_qua"] is None


def test_thieu_cau_hinh_khong_chan_khoi_dong(monkeypatch):
    monkeypatch.setattr(chay, "ngan", chay.NganBoNho())
    with pytest.raises(LoiNghiepVu) as exc:
        chay.can_cau_hinh()
    assert exc.value.ma == "CHUA_CAU_HINH"
    CoreGia().chay(chay.app)


def test_chon_ngan_va_schema(monkeypatch):
    ngan = chay.NganBoNho()
    class App: pass
    app = App()
    app.ngan = ngan
    assert chay.chon_ngan(app) is ngan
    monkeypatch.setattr(chay, "ngan", ngan)
    with ngan.lo() as lo:
        lo.them("cau_hinh", {}, {"phien_ban_cau_hinh":"DEMO", "ma_bo_chuan_hoa":"DEMO", "bam_bo_chuan_hoa":"DEMO", "ma_tu_dien":"DEMO", "bam_tu_dien":"DEMO", "phuong_phap_detector":"DEMO", "phien_ban_detector":"DEMO"})
    assert chay.can_cau_hinh()["nguong_ocr_kem"] is None
    assert ngan.doc("cau_hinh", {}).gia_tri.get("nguong_ocr_kem", "thieu") == "thieu"


def test_manifest_khung():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert not ({"ngan_du_lieu", "cau_hinh", "giao_dien_quan_tri"} & phieu.keys())
    assert phieu["chay_thu_demo"]
    assert [n["ma"] for n in phieu["nang_luc"]] == ["doi_chieu.doc_docx@1"]
