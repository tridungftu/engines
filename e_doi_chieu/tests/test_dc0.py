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


def test_cong_tam_da_luu_tru_khong_nam_trong_goi():
    luu = ROOT / "e_doi_chieu/LUU-TRU/DC-S22"
    for ten in ("ngan.py", "cau_hinh.py", "KHAI-SDK-2.1.json"):
        assert (luu / ten).is_file()
        assert not (GOI / "e_doi_chieu" / ten).exists()
    assert not (GOI / "KHAI-SDK-2.1.json").exists()


def test_core_gia_docx_hong_khong_tra_ket_qua():
    core = CoreGia()
    tep = core.them_tep("DEMO.docx", b"DEMO", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    kq = core.chay_thu(chay.app, "doi_chieu.doc_docx@1", {"loai": "tep", "tep": tep})
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "DC_WORD_KHONG_DOC_DUOC"
    assert kq["ket_qua"] is None


def test_thieu_cau_hinh_khong_chan_khoi_dong(monkeypatch):
    from types import SimpleNamespace
    with pytest.raises(LoiNghiepVu) as exc:
        chay.can_cau_hinh(SimpleNamespace(cau_hinh={}))
    assert exc.value.ma == "CHUA_CAU_HINH"
    CoreGia().chay(chay.app)


def test_chon_ngan_va_schema(monkeypatch):
    from types import SimpleNamespace
    core = CoreGia(chay.app)
    config = {k: "DEMO" for k in chay._BAT_BUOC}
    core.dat_cau_hinh(chay.app.ma, config)
    core.chay(chay.app)
    assert chay.app.cau_hinh["nguong_ocr_kem"] is None
    assert chay.can_cau_hinh(SimpleNamespace(cau_hinh=chay.app.cau_hinh))["so_trang_toi_da"] == 60
    assert "nguong_ocr_kem" not in config


def test_manifest_khung():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert phieu["tuong_thich"]["sdk"] == ">=2.2.0 <3.0.0"
    assert "cau_hinh" not in {b["bang"] for b in phieu["ngan_du_lieu"]}
    assert phieu["chay_thu_demo"]
    assert [n["ma"] for n in phieu["nang_luc"]] == ["doi_chieu.doc_docx@1", "doi_chieu.nhan_cap@1", "doi_chieu.so_van_ban@1", "doi_chieu.phat_hien_sua_tay@1", "doi_chieu.chuan_bi_ai@1", "doi_chieu.phan_loai_diem_lech@1", "doi_chieu.xuat_ket_qua@1"]
