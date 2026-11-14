"""MASK-0: kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO."""
import importlib
import sys
from pathlib import Path
import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_mask"
sys.path.insert(0, str(GOI))

@pytest.fixture
def module(monkeypatch):
    monkeypatch.chdir(GOI)
    return importlib.import_module("e_mask.chay")

def test_phieu():
    app = Engine.tu_khai_bao(str(GOI / "engine.json"))
    assert app.ma == "e_mask"
    assert len(app.phieu["nang_luc"]) == 2

def test_stub_core_gia(module):
    for vd in module.app.phieu["chay_thu_demo"]:
        kq = CoreGia().chay_thu(module.app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
        assert kq["trang_thai"] == "LOI"
        assert kq["loi"]["ma"] == "CHUA_LAM"
        assert kq["loi"]["thong_diep"] == "Chức năng này chưa được hoàn tất."
        assert kq["ket_qua"] is None

def test_cau_hinh_thieu(tmp_path, monkeypatch):
    from e_mask import cau_hinh_may as ch
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "demo.json"))
    assert ch.doc_cau_hinh() is None
    with pytest.raises(LoiNghiepVu) as exc: ch.yeu_cau_cau_hinh()
    assert exc.value.ma == "MASK_CHUA_CAU_HINH"
    assert str(tmp_path) not in str(exc.value)

@pytest.mark.parametrize("noi_dung", ["{", "{\"la\": 1}", "{\"a\":1,\"a\":2}", "NaN"])
def test_cau_hinh_hong(tmp_path, monkeypatch, noi_dung):
    from e_mask import cau_hinh_may as ch
    tep = tmp_path / "demo.json"
    tep.write_text(noi_dung, encoding="utf-8")
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    with pytest.raises(LoiNghiepVu) as exc: ch.doc_cau_hinh()
    assert str(tmp_path) not in str(exc.value)
    assert exc.value.ma == "MASK_CAU_HINH_KHONG_HOP_LE"

def test_cau_hinh_rong(tmp_path, monkeypatch):
    from e_mask import cau_hinh_may as ch
    tep = tmp_path / "demo.json"
    tep.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    assert ch.yeu_cau_cau_hinh() == {}

def test_kiem_doc_lap_chan(tmp_path):
    from kiem_doc_lap import kiem_tra
    (tmp_path / "demo.py").write_text("import sqlite3", encoding="utf-8")
    assert kiem_tra(tmp_path)
