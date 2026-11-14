"""Kho tạm: dữ liệu DEMO, ghi nguyên tử và khóa thật giữa tiến trình."""

import json
import multiprocessing
import os
from pathlib import Path

import pytest

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_ocr.cau_hinh_may import THU_MUC_GOI
from e_ocr.kho_tam import KhoTam


def _ghi_dong_thoi(thu_muc, ma, kenh, bat_dau):
    kho = KhoTam(thu_muc)
    kenh.send("da_cho")
    if not bat_dau.wait(10):
        raise RuntimeError("Không nhận được tín hiệu chạy DEMO.")
    for i in range(30):
        gia_tri = {"ma_tuong_quan": f"DEMO-{ma}-{i}", "so_dem": i, "so_trang": 1}
        kho.ghi(f"luot:{ma}:{i}", gia_tri)
        kho.ghi("luot-chung", gia_tri)
    kenh.send("da_ghi")
    kenh.close()


def _ghi_mot_khoa(thu_muc, kenh, thoi_han=10):
    kenh.send("bat_dau")
    try:
        KhoTam(thu_muc, thoi_han_khoa_giay=thoi_han).ghi("DEMO", {"so_trang": 1})
        kenh.send("da_ghi")
    except LoiNghiepVu as loi:
        kenh.send((loi.ma, loi.thu_lai_duoc))
    finally:
        kenh.close()


def _doi_tin(kenh):
    assert kenh.poll(15), "Tiến trình DEMO không phản hồi trong thời hạn."
    return kenh.recv()


def _dung_tien_trinh(cac_tien_trinh):
    for tien_trinh in cac_tien_trinh:
        tien_trinh.join(timeout=10)
        if tien_trinh.is_alive():
            tien_trinh.terminate()
            tien_trinh.join(timeout=5)
        assert tien_trinh.exitcode == 0


def test_doc_ghi_theo_khoa_va_giu_qua_khoi_dong(tmp_path, monkeypatch):
    monkeypatch.setenv("KTT_ENGINE_DU_LIEU", str(tmp_path / "kho-DEMO"))
    kho = KhoTam()
    assert kho.doc("chua-co") is None
    assert kho.doc("chua-co", 42) == 42
    luot = {
        "ma_tuong_quan": "DEMO-001", "bam_noi_dung": "sha256:" + "a" * 64,
        "phap_nhan_id": "phap-nhan-DEMO", "so_trang": 3, "trang_thai": "dang_gui",
        "ngay": "2026-11-14", "co_giu": True,
    }
    kho.ghi("luot:DEMO-001", luot)
    kho.ghi("han-muc:2026-11-14", 3)
    assert KhoTam().doc("luot:DEMO-001") == luot
    assert KhoTam().doc("han-muc:2026-11-14") == 3
    da_doc = kho.doc("luot:DEMO-001")
    da_doc["so_trang"] = 999
    assert kho.doc("luot:DEMO-001")["so_trang"] == 3


def test_duong_dan_mac_dinh(tmp_path):
    kho = KhoTam()
    assert kho.thu_muc == tmp_path / "may-DEMO" / "KhoTriThuc" / "engines" / "e_ocr" / "du-lieu"
    assert not kho.thu_muc.exists()


@pytest.mark.parametrize("gia_tri", [
    b"noi-dung-DEMO", {"ma": b"noi-dung-DEMO"},
    {"van_ban": "DEMO"}, {"noi_dung": "DEMO"}, {"tai_lieu": "DEMO"},
    "Công ty DEMO Ánh Dương", "DEMO text", "../DEMO.pdf",
    "A" * 201, -1, 1.5, float("nan"), float("inf"),
    {"ma": [b"DEMO"]}, {"ma": {"prompt": "DEMO"}},
    ["A" * 200] * 400,
], ids=[
    "bytes", "bytes_long", "van_ban", "noi_dung", "tai_lieu", "chu_co_dau",
    "chu_co_khoang_trang", "duong_dan", "chuoi_dai", "so_am", "so_thuc", "nan", "inf",
    "bytes_trong_danh_sach", "prompt_long", "qua_lon",
])
def test_khong_nhan_noi_dung_tai_lieu_hoac_du_lieu_sai(tmp_path, gia_tri):
    kho = KhoTam(tmp_path / "kho-DEMO")
    with pytest.raises(LoiNghiepVu) as loi:
        kho.ghi("DEMO", gia_tri)
    assert loi.value.ma == "KHO_TAM_DU_LIEU_SAI"
    assert not kho.thu_muc.exists()


@pytest.mark.parametrize("khoa", ["", "../DEMO", "a/b", "A" * 201, b"DEMO"])
def test_khoa_sai_khong_thoat_thu_muc(tmp_path, khoa):
    kho = KhoTam(tmp_path / "kho-DEMO")
    with pytest.raises(LoiNghiepVu) as loi:
        kho.doc(khoa)
    assert loi.value.ma == "KHO_TAM_KHOA_SAI"
    with pytest.raises(LoiNghiepVu) as loi:
        kho.ghi(khoa, 1)
    assert loi.value.ma == "KHO_TAM_DU_LIEU_SAI"
    assert not kho.thu_muc.exists()


@pytest.mark.parametrize("noi_dung", [b"{", b"[]", b"\xff", b'{"DEMO":1,"DEMO":2}'])
def test_kho_hong_khong_bi_ghi_de(tmp_path, noi_dung):
    tep = tmp_path / "kho.json"
    tep.write_bytes(noi_dung)
    kho = KhoTam(tmp_path)
    with pytest.raises(LoiNghiepVu) as loi:
        kho.doc("DEMO")
    assert loi.value.ma == "KHO_TAM_HONG"
    with pytest.raises(LoiNghiepVu) as loi:
        kho.ghi("DEMO", 1)
    assert loi.value.ma == "KHO_TAM_HONG"
    assert tep.read_bytes() == noi_dung


def test_ghi_nguyen_tu_tu_tep_tam_cung_thu_muc(tmp_path, monkeypatch):
    kho = KhoTam(tmp_path)
    kho.ghi("DEMO", {"so_trang": 1})
    thay_goc = os.replace
    da_thay = []

    def thay_gia(nguon, dich):
        nguon, dich = Path(nguon), Path(dich)
        assert nguon.parent == dich.parent == tmp_path
        assert json.loads(dich.read_text(encoding="utf-8"))["DEMO"]["so_trang"] == 1
        assert json.loads(nguon.read_text(encoding="utf-8"))["DEMO"]["so_trang"] == 2
        da_thay.append(True)
        thay_goc(nguon, dich)

    monkeypatch.setattr(os, "replace", thay_gia)
    kho.ghi("DEMO", {"so_trang": 2})
    assert da_thay == [True]
    assert kho.doc("DEMO") == {"so_trang": 2}
    assert not list(tmp_path.glob(".kho-*.tmp"))


def test_hong_khi_thay_tep_giu_ban_cu_va_nha_khoa(tmp_path, monkeypatch):
    kho = KhoTam(tmp_path)
    kho.ghi("DEMO", {"so_trang": 1})
    cu = (tmp_path / "kho.json").read_bytes()

    def thay_loi(*args):
        raise PermissionError(f"Loi DEMO: {tmp_path}")

    with monkeypatch.context() as tam:
        tam.setattr(os, "replace", thay_loi)
        with pytest.raises(LoiNghiepVu) as loi:
            kho.ghi("DEMO", {"so_trang": 2})
        assert loi.value.ma == "KHO_TAM_KHONG_TRUY_CAP"
        assert str(tmp_path) not in str(loi.value)
    assert (tmp_path / "kho.json").read_bytes() == cu
    assert not list(tmp_path.glob(".kho-*.tmp"))
    kho.ghi("DEMO", {"so_trang": 3})
    assert kho.doc("DEMO")["so_trang"] == 3


def test_hai_tien_trinh_ghi_dong_thoi_khong_mat_khoa(tmp_path):
    # spawn trên cả Windows và Linux, không phụ thuộc fork hoặc mock khóa.
    ctx = multiprocessing.get_context("spawn")
    bat_dau = ctx.Event()
    cac_tien_trinh, cac_kenh = [], []
    for ma in ("A", "B"):
        cha, con = ctx.Pipe()
        tien_trinh = ctx.Process(target=_ghi_dong_thoi, args=(str(tmp_path), ma, con, bat_dau))
        tien_trinh.start()
        con.close()
        cac_tien_trinh.append(tien_trinh)
        cac_kenh.append(cha)
    try:
        assert [_doi_tin(kenh) for kenh in cac_kenh] == ["da_cho", "da_cho"]
        bat_dau.set()
        assert [_doi_tin(kenh) for kenh in cac_kenh] == ["da_ghi", "da_ghi"]
    finally:
        bat_dau.set()
        _dung_tien_trinh(cac_tien_trinh)
        for kenh in cac_kenh:
            kenh.close()
    kho = KhoTam(tmp_path)
    for ma in ("A", "B"):
        for i in range(30):
            assert kho.doc(f"luot:{ma}:{i}") == {
                "ma_tuong_quan": f"DEMO-{ma}-{i}", "so_dem": i, "so_trang": 1,
            }
    assert kho.doc("luot-chung") in [
        {"ma_tuong_quan": f"DEMO-{ma}-29", "so_dem": 29, "so_trang": 1} for ma in ("A", "B")
    ]
    assert len(json.loads((tmp_path / "kho.json").read_text(encoding="utf-8"))) == 61
    assert not list(tmp_path.glob(".kho-*.tmp"))


def test_tien_trinh_khac_phai_doi_khoa(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    cha, con = ctx.Pipe()
    kho = KhoTam(tmp_path)
    tien_trinh = ctx.Process(target=_ghi_mot_khoa, args=(str(tmp_path), con))
    try:
        with kho._khoa_tep():
            tien_trinh.start()
            con.close()
            assert _doi_tin(cha) == "bat_dau"
            assert not cha.poll(0.15)
            assert not (tmp_path / "kho.json").exists()
        assert _doi_tin(cha) == "da_ghi"
    finally:
        _dung_tien_trinh([tien_trinh])
        cha.close()
    assert kho.doc("DEMO") == {"so_trang": 1}


def test_het_han_cho_khoa_bao_loi_thu_lai_duoc(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    cha, con = ctx.Pipe()
    kho = KhoTam(tmp_path)
    tien_trinh = ctx.Process(target=_ghi_mot_khoa, args=(str(tmp_path), con, 0.15))
    try:
        with kho._khoa_tep():
            tien_trinh.start()
            con.close()
            assert _doi_tin(cha) == "bat_dau"
            assert _doi_tin(cha) == ("KHO_TAM_DANG_BAN", True)
    finally:
        _dung_tien_trinh([tien_trinh])
        cha.close()
    kho.ghi("DEMO", 1)
    assert kho.doc("DEMO") == 1


@pytest.mark.parametrize("thu_muc", [str(THU_MUC_GOI / "du-lieu"), ""])
def test_tu_choi_kho_trong_goi_va_bien_rong(monkeypatch, thu_muc):
    monkeypatch.setenv("KTT_ENGINE_DU_LIEU", thu_muc)
    with pytest.raises(LoiNghiepVu) as loi:
        KhoTam()
    assert loi.value.ma == "KHO_TAM_CHUA_CAU_HINH"
