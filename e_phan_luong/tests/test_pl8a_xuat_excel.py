"""PL-8A: chỉ dữ liệu DEMO trong RAM; tích hợp parser khi lead ghép PL-3A."""
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys
import unicodedata
from zipfile import ZipFile

import openpyxl
import pytest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import kieu, xuat_excel
from e_phan_luong.loi import CAU_LOI, LoiNghiepVu


META = dict(ma_luot="PL-DEMO-001", ma_module="demo_thanh_toan",
            khau="ktt_duyet", phien_ban_engine="0.1.0")
COT = ("Mã", "Lý do", "Cờ", "Loại", "Nguồn loại", "Kết quả",
       "Số tiền sai", "Tiền tệ", "Loại đúng")


@pytest.fixture
def ds_demo():
    return (
        kieu.KetQuaDong("PC-DEMO-001", "do", (kieu.VUOT_PM, kieu.VUOT_TE),
                        kieu.THU_TU_CO, "thanh_toan_ncc", "module"),
        kieu.KetQuaDong("PC-DEMO-XANH", "xanh", (kieu.KHONG_CHON,), (),
                        "tam_ung", "quy_tac"),
        kieu.KetQuaDong("PC-DEMO-002", "do", (kieu.CHON_MAU,), (), "tam_ung", "ai"),
        kieu.KetQuaDong("PC-DEMO-003", "do",
                        (kieu.NGHI_CHIA_NHO, kieu.CO_DO_CUNG, kieu.NOP_LAI), (),
                        "thu_tien", "quy_tac"),
        kieu.KetQuaDong("PC-DEMO-004", "do",
                        (kieu.CHUA_QUY_DOI, kieu.CHUA_RO_TIEN_TE), (),
                        "chua_phan_loai", "chua_phan_loai"),
    )


def _lap(ds):
    return xuat_excel.lap_ds_do(ds, **META)


def _sua(du_lieu, sua):
    wb = openpyxl.load_workbook(BytesIO(du_lieu))
    try:
        sua(wb)
        out = BytesIO()
        wb.save(out)  # Chỉ helper test; runtime dùng lớp ghi XML trong RAM.
        return out.getvalue()
    finally:
        wb.close()


def _dien(wb):
    ws = wb["Can kiem"]
    ws["F3"] = "dat"
    ws["F4"] = "sai"
    ws["G4"] = "1000000000000.123456"
    ws["H4"] = "VND"
    ws["I4"] = "chi_phi_khac"
    ws["F5"] = "khong_kiem"
    ws["G6"] = "Dòng chưa ghi Kết quả phải được bỏ qua"


def _bo_dau(chu):
    return "".join(c for c in unicodedata.normalize("NFD", chu)
                   if unicodedata.category(c) != "Mn").lower().replace("đ", "d")


def test_ten_du_ma_va_khong_lo_thong_tin_noi_bo():
    assert set(xuat_excel.TEN_LY_DO) == set(kieu.THU_TU_LY_DO)
    assert set(xuat_excel.TEN_CO) == set(kieu.THU_TU_CO)
    assert xuat_excel.TEN_LY_DO[kieu.VUOT_TE] == "Vượt ngưỡng TE"
    for ten in (*xuat_excel.TEN_LY_DO.values(), *xuat_excel.TEN_CO.values()):
        assert ten and not any(c.isdigit() for c in ten)
        assert not any(c in _bo_dau(ten) for c in ("ty le", "xac suat", "bac", "hat giong"))


def test_mo_lai_chi_dong_do_va_cot_ghi_trong(ds_demo):
    wb = openpyxl.load_workbook(BytesIO(_lap(ds_demo)))
    try:
        assert wb.sheetnames == ["Can kiem", "Huong dan"]
        ws = wb["Can kiem"]
        assert tuple(c.value for c in ws[1]) == (
            "ma_luot", META["ma_luot"], "khau", META["khau"],
            "ma_module", META["ma_module"], "phien_ban_engine", "0.1.0", None)
        assert tuple(c.value for c in ws[2]) == COT
        assert [r[0] for r in ws.iter_rows(min_row=3, values_only=True)] == [
            "PC-DEMO-001", "PC-DEMO-002", "PC-DEMO-003", "PC-DEMO-004"]
        assert ws["B3"].value == "Vượt ngưỡng PM; Vượt ngưỡng TE"
        assert ws["C3"].value == "; ".join(xuat_excel.TEN_CO[m] for m in kieu.THU_TU_CO)
        assert ws["D4"].value == "tam_ung"
        assert ws["E4"].value == "ai"
        assert all(c.value is None for r in ws.iter_rows(min_row=3, min_col=6) for c in r)
        dv, = ws.data_validations.dataValidation
        assert dv.type == "list"
        assert dv.formula1 == '"dat,sai,khong_kiem"'
        assert str(dv.sqref) == "F3:F6"
        assert dv.showErrorMessage and dv.errorStyle == "stop" and dv.allow_blank
        assert ws["G3"].number_format == "@"
        for sheet in wb:
            for row in sheet:
                for cell in row:
                    chu = _bo_dau(str(cell.value or "")).replace("_", " ")
                    assert not any(c in chu for c in ("ty le", "xac suat", "bac", "hat giong"))
    finally:
        wb.close()


def test_tai_hien_bytes_khi_doi_dong_ho(ds_demo, monkeypatch):
    dau = _lap(ds_demo)
    monkeypatch.setattr("zipfile.time.localtime", lambda *a: (2030, 12, 31, 23, 59, 58, 1, 1, 0))
    assert _lap(ds_demo) == dau
    with ZipFile(BytesIO(dau)) as z:
        assert {i.date_time for i in z.infolist()} == {(2000, 1, 1, 0, 0, 0)}
    wb = openpyxl.load_workbook(BytesIO(dau))
    try:
        assert wb.properties.created == wb.properties.modified == datetime(2000, 1, 1)
    finally:
        wb.close()


def test_xuat_khong_tao_tep_tam(ds_demo, monkeypatch):
    def cam(*args, **kwargs):
        pytest.fail("Engine không được ghi XML sheet ra tệp tạm")
    monkeypatch.setattr("openpyxl.worksheet._writer.NamedTemporaryFile", cam)
    assert xuat_excel.doc_ds_do_da_ghi(_lap(ds_demo))["ket_qua"] == []


@pytest.mark.parametrize("chi_xanh", [False, True])
def test_khong_co_dong_do_van_doc_duoc(ds_demo, chi_xanh):
    ds = [ds_demo[1]] if chi_xanh else []
    assert xuat_excel.doc_ds_do_da_ghi(_lap(ds)) == {
        "phien_ban": 1, "ma_module": "demo_thanh_toan", "ket_qua": []}


def test_khu_hoi_du_ba_ket_qua_bao_toan_tien(ds_demo):
    kq = xuat_excel.doc_ds_do_da_ghi(_sua(_lap(ds_demo), _dien))
    assert kq == {"phien_ban": 1, "ma_module": "demo_thanh_toan", "ket_qua": [
        {"ma_luot": "PL-DEMO-001", "ma": "PC-DEMO-001", "khau": "ktt_duyet",
         "ket_qua": "dat", "so_tien_sai": None, "loai_dung": None},
        {"ma_luot": "PL-DEMO-001", "ma": "PC-DEMO-002", "khau": "ktt_duyet",
         "ket_qua": "sai", "so_tien_sai": {"so": "1000000000000.123456", "tien_te": "VND"},
         "loai_dung": "chi_phi_khac"},
        {"ma_luot": "PL-DEMO-001", "ma": "PC-DEMO-003", "khau": "ktt_duyet",
         "ket_qua": "khong_kiem", "so_tien_sai": None, "loai_dung": None},
    ]}
    json.dumps(kq, ensure_ascii=False, allow_nan=False)


def test_khu_hoi_hop_parser_ket_qua_json(ds_demo):
    if importlib.util.find_spec("e_phan_luong.ket_qua") is None:
        pytest.skip("Worktree chưa có ket_qua.py của PL-3A; lead chạy lại khi ghép.")
    from e_phan_luong.ket_qua import doc_ket_qua_json
    kq = xuat_excel.doc_ds_do_da_ghi(_sua(_lap(ds_demo), _dien))
    da_doc = doc_ket_qua_json(json.dumps(kq, ensure_ascii=False).encode("utf-8"))
    assert da_doc.ma_module == "demo_thanh_toan"
    assert len(da_doc.dong) == 3
    assert da_doc.dong[1].so_tien_sai.so == Decimal("1000000000000.123456")
    assert da_doc.dong[1].loai_dung == "chi_phi_khac"


@pytest.mark.parametrize("so, chuan", [(0, "0"), (1250, "1250"), (12.5, "12.5"),
                                      ("-2500.010000", "-2500.01")])
def test_doc_tien_co_don_vi_khong_tu_gan(ds_demo, so, chuan):
    def sua(wb):
        ws = wb["Can kiem"]
        ws["F3"], ws["G3"], ws["H3"] = "sai", so, "USD"
    kq = xuat_excel.doc_ds_do_da_ghi(_sua(_lap(ds_demo), sua))
    assert kq["ket_qua"][0]["so_tien_sai"] == {"so": chuan, "tien_te": "USD"}


@pytest.mark.parametrize("o, gia_tri", [
    ("A2", "Mã khác mẫu"), ("A1", "nhan_sai"), ("B1", None), ("D1", None),
    ("F1", "Module sai dạng"), ("H1", None), ("F3", "khac"), ("G3", None),
    ("G3", True), ("G3", "NaN"), ("G3", "1e3"), ("G3", "1.1234567"),
    ("H3", None), ("H3", "vnd"), ("I3", "loai sai"), ("A3", None),
    ("G3", "=1+1"), ("F3", '=IF(1,"dat","sai")'),
])
def test_sai_mau_tra_loi_co_dinh(ds_demo, o, gia_tri):
    def sua(wb):
        ws = wb["Can kiem"]
        ws["F3"], ws["G3"], ws["H3"] = "sai", "1000000", "VND"
        ws[o] = gia_tri
    with pytest.raises(LoiNghiepVu) as err:
        xuat_excel.doc_ds_do_da_ghi(_sua(_lap(ds_demo), sua))
    assert err.value.ma == "DU_LIEU_KHONG_HOP_LE"
    assert err.value.thong_diep == CAU_LOI[err.value.ma]


@pytest.mark.parametrize("du_lieu", [b"", b"Khong phai Excel DEMO", b"PK\x03\x04hong", None])
def test_tep_hong_khong_lo_chi_tiet(du_lieu):
    with pytest.raises(LoiNghiepVu) as err:
        xuat_excel.doc_ds_do_da_ghi(du_lieu)
    assert err.value.ma == "DU_LIEU_KHONG_HOP_LE"


def test_thieu_sheet_huong_dan_bi_tu_choi(ds_demo):
    def sua(wb):
        wb.remove(wb["Huong dan"])
    with pytest.raises(LoiNghiepVu) as err:
        xuat_excel.doc_ds_do_da_ghi(_sua(_lap(ds_demo), sua))
    assert err.value.ma == "DU_LIEU_KHONG_HOP_LE"


def test_ma_co_dau_bang_duoc_giu_nguyen_van():
    ds = [kieu.KetQuaDong("=PC-DEMO-001", "do", (kieu.CHON_MAU,), (), "tam_ung", "module")]
    def sua(wb):
        assert wb["Can kiem"]["A3"].data_type == "s"
        wb["Can kiem"]["F3"] = "dat"
    assert xuat_excel.doc_ds_do_da_ghi(_sua(_lap(ds), sua))["ket_qua"][0]["ma"] == "=PC-DEMO-001"


def test_vuot_tran_tep_khong_cat_ngam():
    with pytest.raises(LoiNghiepVu) as err:
        xuat_excel.doc_ds_do_da_ghi(b"0" * (20 * 1048576 + 1))
    assert err.value.ma == "VUOT_GIOI_HAN"
