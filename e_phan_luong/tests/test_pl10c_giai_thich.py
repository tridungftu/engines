"""PL-10C: giải thích người kiểm, chỉ dữ liệu Công ty DEMO Ánh Dương trong RAM."""
from datetime import date, datetime
from io import BytesIO
import json
from time import perf_counter
import unicodedata

import openpyxl
import pytest
from openpyxl.worksheet.worksheet import Worksheet

from e_phan_luong import kieu, xuat_excel
from e_phan_luong.ket_qua import doc_ket_qua_json
from e_phan_luong.loi import CAU_LOI, LoiNghiepVu


META = dict(ma_luot="PL-DEMO-10C", ma_module="demo_thanh_toan",
            khau="ktt_duyet", phien_ban_engine="0.1.0")
GIAI_THICH = "Công ty DEMO Ánh Dương: AI gán nhầm loại.\nCần kiểm nội dung\tchứng từ."
COT_CU = ("Mã", "Lý do", "Cờ", "Loại", "Nguồn loại", "Kết quả",
          "Số tiền sai", "Tiền tệ", "Loại đúng")
HUONG_DAN = ("Giải thích: bắt buộc khi AI kiểm sai (Kết quả = sai ở dòng AI chưa gắn cờ, "
             "hoặc sửa Loại đúng cho loại AI gán) — ghi vì sao AI sai để AI học.")


def _dong(**them):
    return {"ma_luot": META["ma_luot"], "ma": "PC-DEMO-001", "khau": META["khau"],
            "ket_qua": "dat", **them}


def _doc(*dong):
    return doc_ket_qua_json(json.dumps({"phien_ban": 1, "ma_module": META["ma_module"],
                                      "ket_qua": dong}, ensure_ascii=False).encode("utf-8"))


def _bat_loi(ham, *args):
    with pytest.raises(LoiNghiepVu) as bat:
        ham(*args)
    assert bat.value.ma == "DU_LIEU_KHONG_HOP_LE"
    assert bat.value.thong_diep == CAU_LOI[bat.value.ma]


def _ds():
    return [kieu.KetQuaDong("=PC-DEMO-001", "do", (kieu.VUOT_TE, kieu.CO_DO_CUNG),
                            (kieu.NHAP_TAY,), "tam_ung", "ai"),
            kieu.KetQuaDong("PC-DEMO-XANH", "xanh", (kieu.KHONG_CHON,), (),
                            "tam_ung", "quy_tac"),
            kieu.KetQuaDong("PC-DEMO-002", "do", (kieu.CHON_MAU,), (),
                            "chua_phan_loai", "chua_phan_loai")]


def _excel(giai_thich=None, *, sua=None):
    wb = openpyxl.load_workbook(BytesIO(xuat_excel.lap_ds_do(_ds(), **META)))
    try:
        ws = wb["Can kiem"]
        ws["F3"] = "dat"
        ws["J3"] = giai_thich
        if sua:
            sua(ws)
        out = BytesIO()
        wb.save(out)
        return out.getvalue()
    finally:
        wb.close()


def test_json_khong_co_khoa_giai_thich():
    assert _doc(_dong()).dong[0].giai_thich is None


@pytest.mark.parametrize("gia_tri,chuan", [
    (None, None), ("", None), ("   \t\n\u00a0\u2003", None),
    (GIAI_THICH, GIAI_THICH), (" \n" + GIAI_THICH + "\t ", GIAI_THICH),
    (unicodedata.normalize("NFD", GIAI_THICH), GIAI_THICH),
    ("á" * 2000, "á" * 2000),
    (unicodedata.normalize("NFD", "á" * 2000), "á" * 2000),
    ("  " + "á" * 2000 + "  ", "á" * 2000),
])
def test_json_chuan_hoa_va_bien_2000(gia_tri, chuan):
    assert _doc(_dong(giai_thich=gia_tri)).dong[0].giai_thich == chuan


@pytest.mark.parametrize("gia_tri", [
    "á" * 2001, unicodedata.normalize("NFD", "á" * 2001),
    123, 1.25, True, [], {},
    *["DEMO" + chr(i) + "giải thích" for i in (*range(9), 11, 12, *range(13, 32),
                                               *range(127, 160))],
    "\rDEMO", "DEMO\r", "\x1c",  # strip không được che mất ký tự điều khiển.
])
def test_json_tu_choi_giai_thich_sai(gia_tri):
    _bat_loi(_doc, _dong(giai_thich=gia_tri))


def test_json_trung_dong_giu_dau_va_van_kiem_dinh_dang():
    kq = _doc(_dong(giai_thich=GIAI_THICH), _dong(giai_thich="DEMO khác"))
    assert len(kq.dong) == kq.so_trung_trong_tep == 1
    assert kq.dong[0].giai_thich == GIAI_THICH
    _bat_loi(_doc, _dong(), _dong(giai_thich=123))
    _bat_loi(_doc, _dong(), _dong(giai_thich="DEMO\x00"))


def test_json_khoa_json_trung_van_bi_tu_choi():
    raw = json.dumps({"phien_ban": 1, "ma_module": META["ma_module"],
                      "ket_qua": [_dong(giai_thich="DEMO")]})
    raw = raw.replace('"giai_thich": "DEMO"', '"giai_thich": "DEMO", "giai_thich": null')
    _bat_loi(doc_ket_qua_json, raw.encode())


def test_excel_10_cot_giu_nguyen_tung_o_9_cot_ban_truoc():
    wb = openpyxl.load_workbook(BytesIO(xuat_excel.lap_ds_do(_ds(), **META)))
    try:
        ws = wb["Can kiem"]
        # Ảnh chụp giá trị 9 cột đầu của PL-8/PL-9E trước PL-10C, cùng lô DEMO.
        ban_truoc = [
            ("ma_luot", "PL-DEMO-10C", "khau", "ktt_duyet", "ma_module",
             "demo_thanh_toan", "phien_ban_engine", "0.1.0", None),
            COT_CU,
            ("=PC-DEMO-001", "Vượt ngưỡng TE; Cảnh báo từ module", "Nhập tay",
             "tam_ung", "ai", None, None, None, None),
            ("PC-DEMO-002", "Được chọn kiểm tra", None, "chua_phan_loai",
             "chua_phan_loai", None, None, None, None),
        ]
        assert ws.max_column == 10 and ws.max_row == len(ban_truoc)
        for r, hang in enumerate(ban_truoc, 1):
            for c, gia_tri in enumerate(hang, 1):
                assert ws.cell(r, c).value == gia_tri, (r, c)
        assert ws["J2"].value == "Giải thích"
        assert ws.auto_filter.ref == "A2:J4"
        assert ws.column_dimensions["J"].width == 60
        assert not ws.protection.sheet
        for r in (3, 4):
            assert ws.cell(r, 10).value is None
            assert ws.cell(r, 10).number_format == "@"
            assert ws.cell(r, 10).alignment.wrap_text
        assert HUONG_DAN in [o[0].value for o in wb["Huong dan"]]
        for sheet in wb:
            for hang in sheet:
                for o in hang:
                    assert o.data_type != "f"
                    chu = unicodedata.normalize("NFD", str(o.value or "")).lower()
                    chu = "".join(c for c in chu if unicodedata.category(c) != "Mn")
                    assert not any(cam in chu.replace("_", " ")
                                   for cam in ("ty le", "xac suat", "bac", "hat giong"))
    finally:
        wb.close()


@pytest.mark.parametrize("gia_tri,chuan", [
    (GIAI_THICH, GIAI_THICH), (unicodedata.normalize("NFD", GIAI_THICH), GIAI_THICH),
    (None, None), ("", None), ("  \n\t ", None), ("  DEMO  ", "DEMO"),
    ("á" * 2000, "á" * 2000), (123, "123"), (12.5, "12.5"), (0, "0"),
    (date(2026, 10, 30), "2026-10-30 00:00:00"),
    (datetime(2026, 10, 30, 12, 34, 56), "2026-10-30 12:34:56"),
])
def test_excel_doc_nguoc_qua_json(gia_tri, chuan):
    gui = xuat_excel.doc_ds_do_da_ghi(_excel(gia_tri))
    assert gui["ket_qua"][0]["giai_thich"] == chuan
    assert doc_ket_qua_json(json.dumps(gui, ensure_ascii=False).encode()).dong[0].giai_thich == chuan


@pytest.mark.parametrize("gia_tri", ["á" * 2001, "DEMO\r", "DEMO\x7f", "=1+1", "#VALUE!"])
def test_excel_tu_choi_giai_thich_sai_va_cong_thuc(gia_tri):
    _bat_loi(xuat_excel.doc_ds_do_da_ghi, _excel(gia_tri))


def test_excel_chuoi_dau_bang_khong_phai_cong_thuc_duoc_doc():
    def sua(ws):
        ws["J3"].data_type = "s"
    assert xuat_excel.doc_ds_do_da_ghi(_excel("=DEMO giải thích", sua=sua))[
        "ket_qua"][0]["giai_thich"] == "=DEMO giải thích"


def test_excel_mau_9_cot_cu_bi_tu_choi():
    _bat_loi(xuat_excel.doc_ds_do_da_ghi, _excel(sua=lambda ws: ws.delete_cols(10)))


def test_excel_tieu_de_cot_10_sai_bi_tu_choi():
    _bat_loi(xuat_excel.doc_ds_do_da_ghi,
             _excel(sua=lambda ws: setattr(ws["J2"], "value", "DEMO sai tiêu đề")))


def test_20000_dong_do_duoi_30_giay_khong_doc_max_row(monkeypatch):
    ds = [kieu.KetQuaDong(f"PC-DEMO-{i:05}", "do", (kieu.CO_DO_CUNG,), (),
                          "tam_ung", "module") for i in range(20_000)]
    def cam(ws):
        pytest.fail("Xuất tuyến tính không được đọc ws.max_row.")
    with monkeypatch.context() as m:
        m.setattr(Worksheet, "max_row", property(cam))
        bat_dau = perf_counter()
        raw = xuat_excel.lap_ds_do(ds, **META)
        so_giay = perf_counter() - bat_dau
    print(f"\nPL-10C: 20.000 dòng Đỏ DEMO: {so_giay:.3f} giây; {len(raw)} byte.")
    assert so_giay < 30
    wb = openpyxl.load_workbook(BytesIO(raw), read_only=True)
    try:
        ws = wb["Can kiem"]
        assert (ws.max_row, ws.max_column) == (20_002, 10)
        assert ws["A20002"].value == ds[-1].ma
        assert ws["J20002"].value is None
    finally:
        wb.close()
