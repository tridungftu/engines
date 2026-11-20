"""PL-9E: đối chiếu bytes PL-8 và đo xuất 20.000 dòng Đỏ DEMO trên máy chạy."""
from hashlib import sha256
from io import BytesIO
from time import perf_counter
from zipfile import ZipFile

import openpyxl
import pytest

from e_phan_luong import kieu, xuat_excel


META = dict(ma_luot="PL-DEMO-9E", ma_module="demo_thanh_toan",
            khau="ktt_duyet", phien_ban_engine="0.1.0")


def _ds_demo():
    return [kieu.KetQuaDong("=PC-DEMO-001", "do", kieu.THU_TU_LY_DO,
                            kieu.THU_TU_CO, "tam_ung", "module"),
            kieu.KetQuaDong("PC-DEMO-XANH", "xanh", (kieu.KHONG_CHON,), (),
                            "tam_ung", "quy_tac"),
            kieu.KetQuaDong("PC-DEMO-002", "do", (kieu.CHON_MAU,), (),
                            "chua_phan_loai", "chua_phan_loai")]


@pytest.mark.parametrize("lua_chon,bam_cu", [
    ("rong", "89ebaed8b80be9b06f8ee96f38e5895b171c07345925222fcaa0579a7bea589f"),
    ("xanh", "89ebaed8b80be9b06f8ee96f38e5895b171c07345925222fcaa0579a7bea589f"),
    ("hon_hop", "f92bdb41402e25bbae93781158bc2259856bb44eb956292a35e010a0522184ea"),
])
def test_bytes_giong_ban_cu_pl8(lua_chon, bam_cu):
    # Nội dung từng entry từ HEAD PL-8 trước sửa, cùng openpyxl 3.1.5.
    # Bỏ lớp nén ZIP để chạy trên cả Windows/Linux có phiên bản zlib khác nhau.
    ds = {"rong": [], "xanh": _ds_demo()[1:2], "hon_hop": _ds_demo()}[lua_chon]
    bam = sha256()
    with ZipFile(BytesIO(xuat_excel.lap_ds_do(ds, **META))) as z:
        for ten in sorted(z.namelist()):
            bam.update(ten.encode() + b"\0" + z.read(ten))
    assert bam.hexdigest() == bam_cu


def test_20000_dong_do_duoi_30_giay():
    ds = [kieu.KetQuaDong(f"PC-DEMO-{i:05}", "do", (kieu.CO_DO_CUNG,), (),
                          "tam_ung", "module") for i in range(20_000)]
    bat_dau = perf_counter()
    raw = xuat_excel.lap_ds_do(ds, **META)
    so_giay = perf_counter() - bat_dau
    print(f"\nPL-9E: 20.000 dòng Đỏ DEMO: {so_giay:.3f} giây; {len(raw)} byte.")
    assert so_giay < 30
    wb = openpyxl.load_workbook(BytesIO(raw), read_only=False)
    try:
        ws = wb["Can kiem"]
        assert ws.max_row == 20_002
        assert ws["A3"].value == ds[0].ma
        assert ws["A20002"].value == ds[-1].ma
        assert str(ws.data_validations.dataValidation[0].sqref) == "F3:F20002"
        assert ws.auto_filter.ref == "A2:I20002"
    finally:
        wb.close()
