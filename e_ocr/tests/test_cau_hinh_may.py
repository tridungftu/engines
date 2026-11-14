"""Cấu hình máy chỉ dùng JSON DEMO trong thư mục tạm của test."""

import json
from pathlib import Path

import pytest

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_ocr.cau_hinh_may import CAU_HINH_TOI_DA_BYTE, THU_MUC_GOI, doc_cau_hinh


def _dat_cau_hinh(tmp_path, monkeypatch, du_lieu):
    tep = tmp_path / "cau_hinh.DEMO.json"
    tep.write_text(json.dumps(du_lieu), encoding="utf-8")
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    return tep


def test_thieu_cau_hinh_khong_can_tao_tep(tmp_path):
    assert doc_cau_hinh() is None
    assert not (tmp_path / "may-DEMO").exists()
    with pytest.raises(LoiNghiepVu) as loi:
        doc_cau_hinh(bat_buoc=True)
    assert loi.value.ma == "CHUA_CAU_HINH"
    assert str(tmp_path) not in str(loi.value)


def test_doc_mac_dinh_tu_programdata(tmp_path):
    tep = tmp_path / "may-DEMO" / "KhoTriThuc" / "engines" / "e_ocr" / "cau_hinh.json"
    tep.parent.mkdir(parents=True)
    tep.write_text("{}", encoding="utf-8")
    assert doc_cau_hinh() == {
        "abbyy": {
            "bat": False, "thu_muc_vao": "", "thu_muc_ra": "",
            "thoi_han_giay": 900, "han_muc_trang_30_ngay": 5000,
        },
        "tesseract": {"duong_dan": "", "ngon_ngu": "vie+eng"},
    }


def test_doc_json_ngoai_goi_khong_truy_cap_nguon_ocr(tmp_path, monkeypatch):
    vao = tmp_path / "HotFolder-DEMO-vao-chua-tao"
    ra = tmp_path / "HotFolder-DEMO-ra-chua-tao"
    _dat_cau_hinh(tmp_path, monkeypatch, {
        "abbyy": {"bat": True, "thu_muc_vao": str(vao), "thu_muc_ra": str(ra), "thoi_han_giay": 60},
        "tesseract": {"duong_dan": "tesseract-DEMO.exe"},
    })
    kq = doc_cau_hinh(bat_buoc=True)
    assert kq["abbyy"]["bat"] is True
    assert kq["abbyy"]["thu_muc_vao"] == str(vao)
    assert kq["abbyy"]["han_muc_trang_30_ngay"] == 5000
    assert kq["tesseract"]["ngon_ngu"] == "vie+eng"
    assert not vao.exists() and not ra.exists()
    kq["abbyy"]["han_muc_trang_30_ngay"] = 0
    assert doc_cau_hinh()["abbyy"]["han_muc_trang_30_ngay"] == 5000


@pytest.mark.parametrize("du_lieu", [
    [], None, True,
    {"abbyy": []},
    {"abbyy": {"bat": "true"}},
    {"abbyy": {"thoi_han_giay": True}},
    {"abbyy": {"thoi_han_giay": 0}},
    {"abbyy": {"thoi_han_giay": 901}},
    {"abbyy": {"han_muc_trang_30_ngay": -1}},
    {"abbyy": {"han_muc_trang_30_ngay": 5001}},
    {"abbyy": {"han_muc_trang_30_ngay": 1.5}},
    {"abbyy": {"thu_muc_vao": 42}},
    {"tesseract": {"ngon_ngu": ""}},
    {"tesseract": {"duong_dan": "A" * 4097}},
    {"khoa_DEMO": "bi_mat_gia_DEMO"},
    {"abbyy": {"khoa_DEMO": "bi_mat_gia_DEMO"}},
])
def test_tu_choi_sai_schema_khong_lo_gia_tri(tmp_path, monkeypatch, du_lieu):
    tep = _dat_cau_hinh(tmp_path, monkeypatch, du_lieu)
    with pytest.raises(LoiNghiepVu) as loi:
        doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
    assert str(tep) not in str(loi.value)
    assert "bi_mat_gia_DEMO" not in str(loi.value)
    assert loi.value.__suppress_context__


@pytest.mark.parametrize("noi_dung", [
    b"{", b"\xff", b'{"abbyy":{},"abbyy":{}}',
    b'{"abbyy":{"thoi_han_giay":NaN}}',
    b" " * (CAU_HINH_TOI_DA_BYTE + 1),
], ids=["cu_phap", "utf8", "lap_khoa", "so_khong_huu_han", "qua_lon"])
def test_tu_choi_json_hong_lap_khoa_qua_lon(tmp_path, monkeypatch, noi_dung):
    tep = tmp_path / "hong-DEMO.json"
    tep.write_bytes(noi_dung)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    with pytest.raises(LoiNghiepVu) as loi:
        doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"


def test_doc_duoc_utf8_bom(tmp_path, monkeypatch):
    tep = tmp_path / "BOM-DEMO.json"
    tep.write_text("{}", encoding="utf-8-sig")
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    assert doc_cau_hinh()["abbyy"]["bat"] is False


@pytest.mark.parametrize("tep", [str(THU_MUC_GOI / "demo" / "cau_hinh.demo.json"), ""])
def test_tu_choi_cau_hinh_trong_goi_hoac_duong_dan_rong(monkeypatch, tep):
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", tep)
    with pytest.raises(LoiNghiepVu) as loi:
        doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"


def test_loi_he_thong_khong_lo_duong_dan(tmp_path, monkeypatch):
    tep = _dat_cau_hinh(tmp_path, monkeypatch, {})
    mo_goc = Path.open

    def mo_gia(self, *args, **kwargs):
        if self == tep:
            raise PermissionError(f"Khong du quyen DEMO: {tep}")
        return mo_goc(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", mo_gia)
    with pytest.raises(LoiNghiepVu) as loi:
        doc_cau_hinh()
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
    assert str(tep) not in str(loi.value)
