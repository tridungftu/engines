"""PL-6A: chỉ DEMO trong RAM; không nối Core thật."""
from copy import deepcopy
from decimal import Decimal
from io import BytesIO
from io import StringIO
import csv
import json
from pathlib import Path
import struct
import sys
from zipfile import ZipFile, ZIP_DEFLATED

import openpyxl
import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from e_phan_luong import doc_bang
from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.loi import CAU_LOI
from demo.sinh_bang_demo import (hang_demo, khuon_demo, lo_json_demo, sinh_csv, sinh_xlsx)


def doc(raw, kieu="csv", *, khuon=None, **tham_so):
    return doc_bang.doc_lo_bang(raw, kieu, khuon_cot_json=json.dumps(
        khuon_demo() if khuon is None else khuon, ensure_ascii=False),
        **({"ma_module": "demo_thanh_toan", "ky": "2026-11", "tien_te": None} | tham_so))


def bat_loi(ma, ham, *args, **kwargs):
    with pytest.raises(LoiNghiepVu) as bat:
        ham(*args, **kwargs)
    assert bat.value.ma == ma
    assert bat.value.thong_diep == CAU_LOI[ma]


@pytest.mark.parametrize("dau", [",", ";"])
@pytest.mark.parametrize("bom", [False, True])
def test_csv_cung_lo_json(dau, bom):
    assert doc(sinh_csv(dau=dau, bom=bom)) == doc_lo_json(lo_json_demo())


def test_xlsx_cung_lo_json_va_gia_tri_luu():
    raw = sinh_xlsx()
    wb = openpyxl.load_workbook(BytesIO(raw), read_only=True, data_only=False)
    try:
        assert wb["DEMO"]["C4"].value == "=1000000+0.25"
    finally:
        wb.close()
    assert doc(raw, "xlsx") == doc_lo_json(lo_json_demo())


@pytest.mark.parametrize("raw,ten,mime,ket_qua", [
    (b'\xef\xbb\xbf \n {"phien_ban":1}', None, None, "json"),
    (sinh_csv(), "DEMO.CSV", None, "csv"),
    (sinh_csv(), None, "text/csv; charset=utf-8", "csv"),
    (sinh_xlsx(), "DEMO.XLSX", "application/octet-stream", "xlsx"),
])
def test_nhan_dien(raw, ten, mime, ket_qua):
    assert doc_bang.nhan_dien(raw, ten, mime) == ket_qua


@pytest.mark.parametrize("raw,ten,mime", [
    (doc_bang.OLE + b"DEMO", "DEMO.xls", "text/csv"),
    (b"DEMO", "DEMO.txt", "text/plain"),
    (sinh_xlsx(), "DEMO.xlsm", None),
])
def test_khong_ho_tro(raw, ten, mime):
    bat_loi("TEP_KHONG_HO_TRO", doc_bang.nhan_dien, raw, ten, mime)


@pytest.mark.parametrize("ma", ["ma", "ngay", "so_tien"])
def test_thieu_cot_bat_buoc(ma):
    k = khuon_demo()
    i = next(i for i, c in enumerate(k["cot"]) if c["ma"] == ma)
    hang = hang_demo()
    hang[1] = list(hang[1])
    hang[1][i] = "Cột DEMO khác"
    bat_loi("THAM_SO_KHONG_HOP_LE", doc, sinh_csv(hang))
    k["cot"].pop(i)
    bat_loi("THAM_SO_KHONG_HOP_LE", doc, sinh_csv(), khuon=k)


def test_tien_te_chua_ro_va_cai_dat():
    k = khuon_demo()
    k["cot"] = [c for c in k["cot"] if c["ma"] != "tien_te"]
    assert doc(sinh_csv(), khuon=k).nghiep_vu[0].so_tien.tien_te is None
    assert doc(sinh_csv(), khuon=k, tien_te="EUR").nghiep_vu[0].so_tien.tien_te == "EUR"
    hang = hang_demo()
    hang[3][3] = ""
    assert doc(sinh_csv(hang), tien_te="EUR").nghiep_vu[0].so_tien.tien_te is None
    assert doc(sinh_csv(), tien_te="EUR").nghiep_vu[0].so_tien.tien_te == "VND"


def test_ngay_va_dong_dung_va_bo_dau():
    hang = hang_demo()
    hang[1] = [doc_bang.chuan(t).upper() for t in hang[1]]
    lo = doc(sinh_csv(hang, dau=";", bom=True))
    assert len(lo.nghiep_vu) == 2
    assert lo.nghiep_vu[0].ngay.isoformat() == "2026-10-30"


@pytest.mark.parametrize("kieu", ["csv", "xlsx"])
@pytest.mark.parametrize("gia_tri", ["PC-DEMO-0001", "PC-DEMO-\x7f", "", "X" * 121])
def test_luat_ma_dung_chung(kieu, gia_tri):
    hang = hang_demo()
    hang[4][0] = gia_tri
    raw = sinh_csv(hang) if kieu == "csv" else sinh_xlsx(hang, cong_thuc=False)
    bat_loi("DU_LIEU_KHONG_HOP_LE", doc, raw, kieu)


@pytest.mark.parametrize("gia_tri", ["1e3", "NaN", "1,000", "1.1234567", "1000000000000000000"])
def test_so_chu_dung_parser_tien(gia_tri):
    hang = hang_demo()
    hang[3][2] = gia_tri
    bat_loi("DU_LIEU_KHONG_HOP_LE", doc, sinh_csv(hang))


def test_float_excel_chuyen_decimal_repr():
    hang = hang_demo(excel=True)
    hang[3][2] = 0.1
    assert doc(sinh_xlsx(hang, cong_thuc=False), "xlsx").nghiep_vu[0].so_tien.so == Decimal("0.1")


def test_sheet_va_dong_dau_tien():
    k = khuon_demo()
    k["sheet"] = None
    assert doc(sinh_xlsx(), "xlsx", khuon=k) == doc_lo_json(lo_json_demo())
    k["sheet"] = "Khong co DEMO"
    bat_loi("THAM_SO_KHONG_HOP_LE", doc, sinh_xlsx(), "xlsx", khuon=k)


def test_tran_20_mib():
    raw = b" " * (doc_bang.TOI_DA_BYTE + 1)
    bat_loi("VUOT_GIOI_HAN", doc, raw)
    bat_loi("VUOT_GIOI_HAN", doc_bang.nhan_dien, raw, "DEMO.csv", None)


def test_tran_50000_dong():
    k = khuon_demo()
    k["cot"] = k["cot"][:3]
    hang = [["Mã", "Ngày", "Số tiền"]] + [
        [f"PC-DEMO-{i}", "2026-10-30", "1"] for i in range(50000)]
    assert len(doc(sinh_csv(hang), khuon=k).nghiep_vu) == 50000
    hang.append(["PC-DEMO-50000", "2026-10-30", "1"])
    bat_loi("VUOT_GIOI_HAN", doc, sinh_csv(hang), khuon=k)


def test_bom_nen_tran_khai_bao_truoc_openpyxl(monkeypatch):
    raw = bytearray(sinh_xlsx())
    i = raw.index(b"PK\x01\x02")
    struct.pack_into("<I", raw, i + 24, doc_bang.GIAI_NEN_TOI_DA_BYTE + 1)
    def cam(*args, **kwargs):
        pytest.fail("Không được mở workbook trước kiểm trần ZIP")
    monkeypatch.setattr(doc_bang.openpyxl, "load_workbook", cam)
    bat_loi("VUOT_GIOI_HAN", doc_bang.nhan_dien, bytes(raw), "DEMO.xlsx", None)
    bat_loi("VUOT_GIOI_HAN", doc, bytes(raw), "xlsx")


def test_tran_entry():
    raw = BytesIO()
    with ZipFile(raw, "w", compression=ZIP_DEFLATED) as goi:
        for i in range(doc_bang.ENTRY_TOI_DA + 1):
            goi.writestr(f"DEMO-{i}", b"")
    bat_loi("VUOT_GIOI_HAN", doc_bang.nhan_dien, raw.getvalue(), "DEMO.xlsx", None)


@pytest.mark.parametrize("xml,ma", [
    ('<!DOCTYPE worksheet [<!ENTITY demo "DEMO">]><worksheet/>', "DU_LIEU_KHONG_HOP_LE"),
    ('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:XFD1048576"/></worksheet>', "VUOT_GIOI_HAN"),
])
def test_xml_nguy_hiem(xml, ma):
    raw = BytesIO()
    with ZipFile(raw, "w", compression=ZIP_DEFLATED) as goi:
        goi.writestr("[Content_Types].xml", "<Types/>")
        goi.writestr("xl/workbook.xml", "<workbook/>")
        goi.writestr("xl/worksheets/sheet1.xml", xml)
    bat_loi(ma, doc_bang.nhan_dien, raw.getvalue(), "DEMO.xlsx", None)


def test_demo_tai_hien():
    assert sinh_xlsx() == sinh_xlsx()
    assert sinh_csv(bom=True) == sinh_csv(bom=True)


@pytest.mark.parametrize("sua", [
    lambda k: k.update(phien_ban=True),
    lambda k: k["cot"].append(deepcopy(k["cot"][0])),
    lambda k: k["cot"][0].update(ma="thuoc_tinh."),
    lambda k: k.update(dong_dung=[""]),
    lambda k: k.update(dong_dung=["DEMO"] * 201),
])
def test_khuon_sai(sua):
    k = khuon_demo()
    sua(k)
    bat_loi("THAM_SO_KHONG_HOP_LE", doc, sinh_csv(), khuon=k)


def test_csv_khong_utf8():
    bat_loi("TEP_KHONG_HO_TRO", doc, b"\xffDEMO")


@pytest.mark.parametrize("dau", [",", ";"])
def test_csv_quote_all(dau):
    raw = StringIO(newline="")
    csv.writer(raw, delimiter=dau, quoting=csv.QUOTE_ALL).writerows(hang_demo())
    assert doc(raw.getvalue().encode("utf-8")) == doc_lo_json(lo_json_demo())


def test_csv_o_dai_trong_tran_va_khoi_phuc_gioi_han():
    hang = hang_demo()
    hang[3][4] = "DEMO" * 40000
    cu = csv.field_size_limit()
    assert doc(sinh_csv(hang)).nghiep_vu[0].noi_dung["dien_giai"] == hang[3][4]
    assert csv.field_size_limit() == cu


def test_tieu_de_dau_tien_duoc_chon():
    hang = hang_demo()
    # Tiêu đề lặp sau bảng không được dùng để bỏ qua dữ liệu sai ở bảng đầu.
    hang.insert(4, list(hang[1]))
    bat_loi("DU_LIEU_KHONG_HOP_LE", doc, sinh_csv(hang))


def test_bom_nen_thuc_te(monkeypatch):
    monkeypatch.setattr(doc_bang, "GIAI_NEN_TOI_DA_BYTE", 1024 * 1024)
    raw = BytesIO()
    with ZipFile(raw, "w", compression=ZIP_DEFLATED) as goi:
        goi.writestr("DEMO", b"0" * (1024 * 1024 + 1))
    bat_loi("VUOT_GIOI_HAN", doc_bang.nhan_dien, raw.getvalue(), "DEMO.xlsx", None)


def test_xlsx_dung_che_do_doc(monkeypatch):
    goc = openpyxl.load_workbook
    def mo(*args, **kwargs):
        assert kwargs["read_only"] is True
        assert kwargs["data_only"] is True
        return goc(*args, **kwargs)
    monkeypatch.setattr(doc_bang.openpyxl, "load_workbook", mo)
    assert doc(sinh_xlsx(), "xlsx").nguong is None


def test_sheet_null_tim_bang_dau_tien():
    wb = openpyxl.Workbook()
    wb.active.append(["Trang bìa DEMO"])
    ws = wb.create_sheet("DEMO")
    for hang in hang_demo(excel=True):
        ws.append(hang)
    raw = BytesIO()
    try:
        wb.save(raw)
    finally:
        wb.close()
    k = khuon_demo()
    k["sheet"] = None
    assert doc(raw.getvalue(), "xlsx", khuon=k) == doc_lo_json(lo_json_demo())
