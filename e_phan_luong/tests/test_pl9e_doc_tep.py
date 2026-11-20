"""PL-9E: đọc tệp DEMO; tiền không suy đoán và giữ Decimal sau biên Excel."""
from decimal import Decimal
import json

import pytest

from e_phan_luong import doc_bang, doc_lo, hoa_don, nguong
from e_phan_luong.loi import CAU_LOI, LoiNghiepVu
from demo.sinh_bang_demo import khuon_demo, sinh_csv, sinh_xlsx


def _khuon(cac_ma):
    return {"phien_ban": 1, "sheet": "DEMO", "cot": [
        {"ma": ma, "tu_khoa": [ma], "bat_buoc": ma in doc_bang.BAT_BUOC}
        for ma in cac_ma], "dong_dung": []}


def _doc(hang, cac_ma, kieu="xlsx", *, khuon=None):
    raw = (sinh_xlsx([cac_ma] + hang, cong_thuc=False) if kieu == "xlsx"
           else sinh_csv([cac_ma] + hang))
    return doc_bang.doc_lo_bang(
        raw, kieu, khuon_cot_json=json.dumps(khuon or _khuon(cac_ma)),
        ma_module="demo_thanh_toan", tien_te="VND", ky="2026-11")


def _bat_loi(ham, *args, ma="DU_LIEU_KHONG_HOP_LE", **kwargs):
    with pytest.raises(LoiNghiepVu) as bat:
        ham(*args, **kwargs)
    assert bat.value.ma == ma
    assert bat.value.thong_diep == CAU_LOI[ma]


@pytest.mark.parametrize("kieu", ["csv", "xlsx"])
@pytest.mark.parametrize("co_trong_khuon", [False, True])
def test_quy_doi_khong_co_cot_tien_te_khong_lay_du_phong(kieu, co_trong_khuon):
    cac_ma = ["ma", "ngay", "so_tien", "so_tien_quy_doi"]
    khuon = _khuon(cac_ma + (["tien_te_quy_doi"] if co_trong_khuon else []))
    nv, = _doc([["PC-DEMO-001", "2026-10-30", "1", "999999"]],
               cac_ma, kieu, khuon=khuon).nghiep_vu
    assert nv.so_tien_quy_doi is None
    assert nv.so_tien.tien_te == "VND"
    ng = nguong.doc_nguong({k: {"so": v, "tien_te": "VND"}
                            for k, v in (("pm", "1000"), ("te", "100"), ("sad", "10"))}, None)
    assert nguong.tien_so_sanh(nv, ng) == (nv.so_tien, None)


@pytest.mark.parametrize("kieu", ["csv", "xlsx"])
def test_quy_doi_co_tien_te_rieng_va_o_trong_khong_duoc_lap(kieu):
    cac_ma = ["ma", "ngay", "so_tien", "so_tien_quy_doi", "tien_te_quy_doi"]
    lo = _doc([["PC-DEMO-001", "2026-10-30", "1", "2", "USD"],
               ["PC-DEMO-002", "2026-10-30", "1", "2", ""]], cac_ma, kieu)
    assert lo.nghiep_vu[0].so_tien_quy_doi.tien_te == "USD"
    assert lo.nghiep_vu[1].so_tien_quy_doi.tien_te is None


@pytest.mark.parametrize("ma", [" ", "   ", "\u00a0\u2003"])
@pytest.mark.parametrize("duong_vao", ["json", "csv", "xlsx", "doc_dong"])
def test_ma_trang_co_do_cung_bi_chan_ngay_khi_doc(ma, duong_vao):
    dong = {"ma": ma, "ngay": "2026-10-30", "so_tien": {"so": "1", "tien_te": "VND"},
            "co_do_cung": True}
    if duong_vao == "json":
        _bat_loi(doc_lo.doc_lo_json, json.dumps({"phien_ban": 1,
                 "ma_module": "demo_thanh_toan", "nghiep_vu": [dong]}).encode())
    elif duong_vao == "doc_dong":
        _bat_loi(doc_lo._doc_dong, dong, 0)
    else:
        _bat_loi(_doc, [[ma, "2026-10-30", "1", True]],
                 ["ma", "ngay", "so_tien", "co_do_cung"], duong_vao)


def test_ma_hop_le_giu_nguyen_khoang_trang_ben_ngoai():
    nv, = _doc([[" PC-DEMO-001 ", "2026-10-30", "1"]],
               ["ma", "ngay", "so_tien"]).nghiep_vu
    assert nv.ma == " PC-DEMO-001 "


def test_hoa_don_ma_trang_co_do_cung_bi_chan_khi_doc():
    _bat_loi(hoa_don.lo_tu_hoa_don, {
        "mau_so": " ", "ky_hieu": " ", "so_hoa_don": " ", "ngay_lap": "2026-10-30",
        "tong_thanh_toan": {"so": "1", "tien_te": "VND"}, "can_kiem_tra": True},
        ma_module="demo_thanh_toan", loai_nghiep_vu=None)


@pytest.mark.parametrize("so,chuan", [(0.30000000000000004, "0.3"),
    (1234.5600000000002, "1234.56"), (-1234.5600000000002, "-1234.56"),
    (1.1234560000000002, "1.123456"), (0.0000010000000000000002, "0.000001")])
def test_float_excel_15_chu_so_co_nghia_roi_decimal(so, chuan):
    nv, = _doc([["PC-DEMO-001", "2026-10-30", so, so, "USD"]],
               ["ma", "ngay", "so_tien", "so_tien_quy_doi", "tien_te_quy_doi"]).nghiep_vu
    assert isinstance(nv.so_tien.so, Decimal)
    assert nv.so_tien.so == nv.so_tien_quy_doi.so == Decimal(chuan)


@pytest.mark.parametrize("so", [0.1234567, 1234.1234567, -0.0000001, float("inf"), float("nan")])
def test_float_that_su_qua_6_so_le_hoac_khong_huu_han_bi_tu_choi(so):
    _bat_loi(_doc, [["PC-DEMO-001", "2026-10-30", so]], ["ma", "ngay", "so_tien"])


@pytest.mark.parametrize("kieu", ["csv", "xlsx"])
def test_chuoi_tien_khong_duoc_lam_tron(kieu):
    _bat_loi(_doc, [["PC-DEMO-001", "2026-10-30", "0.30000000000000004"]],
             ["ma", "ngay", "so_tien"], kieu)


def test_xlsx_du_50000_dong_va_30_cot():
    cac_ma = ["ma", "ngay", "so_tien"] + [f"thuoc_tinh.demo_{i}" for i in range(27)]
    hang = [[f"PC-DEMO-{i:05}", "2026-10-30", 1] + ["DEMO"] * 24 + [None] * 3
            for i in range(doc_lo.TOI_DA_DONG)]
    lo = _doc(hang, cac_ma)
    assert len(lo.nghiep_vu) == doc_lo.TOI_DA_DONG
    assert lo.nghiep_vu[-1].ma == "PC-DEMO-49999"
    assert len(lo.nghiep_vu[-1].noi_dung) == 24


@pytest.mark.parametrize("vung", ["A1:A500001", "A1:XFD1048576"])
def test_vung_thua_van_bi_chan_o_tran_cu(vung):
    from io import BytesIO
    from zipfile import ZipFile, ZIP_DEFLATED
    raw = BytesIO()
    with ZipFile(raw, "w", compression=ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("xl/workbook.xml", "<workbook/>")
        z.writestr("xl/worksheets/sheet1.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/'
                   f'spreadsheetml/2006/main"><dimension ref="{vung}"/></worksheet>')
    _bat_loi(doc_bang._kiem_xlsx, raw.getvalue(), ma="VUOT_GIOI_HAN")


def test_tran_o_van_tu_choi_khi_vuot(monkeypatch):
    monkeypatch.setattr(doc_bang, "O_TOI_DA", 5)
    _bat_loi(_doc, [["PC-DEMO-001", "2026-10-30", 1]],
             ["ma", "ngay", "so_tien"], ma="VUOT_GIOI_HAN")
