"""Cấu hình DEMO, không gọi Local/Cloud, không dùng tệp cấu hình thật."""
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_hoi_ai import cau_hinh_may as ch


@pytest.fixture
def tep_cau_hinh(tmp_path, monkeypatch):
    tep = tmp_path / "cau_hinh_DEMO.json"
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    monkeypatch.delenv("PROGRAMDATA", raising=False)
    return tep


@pytest.fixture
def cau_hinh_demo():
    return {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60},
            "quy_tac_model": [{"mau_ma_prompt": "demo.*", "uu_tien": "model-demo",
                              "du_phong": ["model-du-phong-demo"]}]}


def test_chua_co_tep_khong_lam_engine_chet(tep_cau_hinh):
    assert ch.doc_cau_hinh() is None
    with pytest.raises(LoiNghiepVu) as loi:
        ch.yeu_cau_cau_hinh()
    assert loi.value.ma == "CHUA_CAU_HINH"
    assert str(tep_cau_hinh) not in str(loi.value)


def test_khong_co_bien_tren_linux_khong_tu_doc_tep_khac(monkeypatch):
    monkeypatch.delenv("KTT_ENGINE_CAU_HINH", raising=False)
    monkeypatch.delenv("PROGRAMDATA", raising=False)
    assert ch.duong_dan_cau_hinh() is None
    assert ch.doc_cau_hinh() is None


def test_mac_dinh_programdata_va_uu_tien_bien_moi_truong(tmp_path, monkeypatch, cau_hinh_demo):
    monkeypatch.delenv("KTT_ENGINE_CAU_HINH", raising=False)
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path))
    tep_mac_dinh = tmp_path / "KhoTriThuc" / "engines" / "e_hoi_ai" / "cau_hinh.json"
    tep_mac_dinh.parent.mkdir(parents=True)
    tep_mac_dinh.write_text(json.dumps(cau_hinh_demo), encoding="utf-8")
    assert ch.duong_dan_cau_hinh() == tep_mac_dinh
    assert ch.doc_cau_hinh() == cau_hinh_demo
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "chua-co-DEMO.json"))
    assert ch.doc_cau_hinh() is None  # Không tự dùng cấu hình khác khi đường dẫn ưu tiên thiếu tệp.


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_doc_json_ngoai_goi_khong_ghi_lai(tep_cau_hinh, cau_hinh_demo, encoding):
    tep_cau_hinh.write_text(json.dumps(cau_hinh_demo, ensure_ascii=False), encoding=encoding)
    noi_dung_cu = tep_cau_hinh.read_bytes()
    assert ch.doc_cau_hinh() == cau_hinh_demo
    assert ch.yeu_cau_cau_hinh() == cau_hinh_demo
    assert tep_cau_hinh.read_bytes() == noi_dung_cu
    cau_hinh_demo["local_ai"]["timeout_giay"] = 15.5
    cau_hinh_demo.pop("quy_tac_model")
    tep_cau_hinh.write_text(json.dumps(cau_hinh_demo), encoding="utf-8")
    assert ch.doc_cau_hinh() == cau_hinh_demo  # Không giữ cấu hình cũ trong cache.


def test_duong_dan_tuong_doi_ngoai_goi(tep_cau_hinh, cau_hinh_demo, monkeypatch):
    tep_cau_hinh.write_text(json.dumps(cau_hinh_demo), encoding="utf-8")
    monkeypatch.chdir(tep_cau_hinh.parent)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", tep_cau_hinh.name)
    assert ch.doc_cau_hinh() == cau_hinh_demo


def test_tu_choi_tep_trong_goi_truoc_khi_doc(tmp_path, monkeypatch):
    monkeypatch.setattr(ch, "THU_MUC_GOI", tmp_path)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "cau_hinh_DEMO.json"))
    with pytest.raises(LoiNghiepVu) as loi:
        ch.doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"


@pytest.mark.parametrize("noi_dung", [
    b"{", b"\xff", b"[]", b"null", b"{}", b'{"local_ai": null}',
    b'{"local_ai": {"url": "http://127.0.0.1:12345"}}',
    b'{"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": NaN}}',
    b'{"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": Infinity}}',
    b'{"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 1e999}}',
    b'{"local_ai": {}, "local_ai": {}}',
])
def test_tu_choi_json_sai_khong_lo_noi_dung(tep_cau_hinh, noi_dung, capsys):
    tep_cau_hinh.write_bytes(noi_dung)
    with pytest.raises(LoiNghiepVu) as loi:
        ch.doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
    assert str(tep_cau_hinh) not in str(loi.value)
    assert loi.value.__suppress_context__
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("sua", [
    {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": True}},
    {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": "60"}},
    {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 0}},
    {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": -1}},
    {"khoa_demo": "DU_LIEU_GIA_DEMO"},
    {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60, "khoa_demo": "DEMO"}},
    {"quy_tac_model": {}},
    {"quy_tac_model": [{"mau_ma_prompt": "*", "du_phong": []}]},
    {"quy_tac_model": [{"mau_ma_prompt": "*", "uu_tien": "demo", "du_phong": "demo"}]},
    {"quy_tac_model": [{"mau_ma_prompt": "*", "uu_tien": "demo", "du_phong": [" "]}]},
])
def test_tu_choi_cau_hinh_sai_schema(tep_cau_hinh, cau_hinh_demo, sua):
    cau_hinh_demo.update(sua)
    tep_cau_hinh.write_text(json.dumps(cau_hinh_demo), encoding="utf-8")
    with pytest.raises(LoiNghiepVu) as loi:
        ch.doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
    assert "DU_LIEU_GIA_DEMO" not in str(loi.value)


@pytest.mark.parametrize("url", [
    "", "ftp://127.0.0.1", "http://", "http://127.0.0.1:99999", "http://127.0.0.1:DEMO",
    "http://ten-demo:gia-tri-demo@127.0.0.1", "http://127.0.0.1?demo=1", "http://127.0.0.1#demo",
    "http://127.0.0.1\n",
])
def test_url_khong_chua_thong_tin_dang_nhap(tep_cau_hinh, cau_hinh_demo, url):
    cau_hinh_demo["local_ai"]["url"] = url
    tep_cau_hinh.write_text(json.dumps(cau_hinh_demo), encoding="utf-8")
    with pytest.raises(LoiNghiepVu) as loi:
        ch.doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
    assert "gia-tri-demo" not in str(loi.value)


def test_khong_du_quyen_doc_bao_loi_an_toan(tep_cau_hinh, monkeypatch):
    def bi_chan(*args, **kwargs):
        raise PermissionError("Chi tiết đường dẫn DEMO không được hiện.")
    monkeypatch.setattr(Path, "read_text", bi_chan)
    with pytest.raises(LoiNghiepVu) as loi:
        ch.doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_DOC_DUOC"
    assert loi.value.thu_lai_duoc
    assert "Chi tiết đường dẫn DEMO" not in str(loi.value)


def test_bien_duong_dan_rong_khong_bi_bo_qua(monkeypatch):
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", " ")
    with pytest.raises(LoiNghiepVu) as loi:
        ch.doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
