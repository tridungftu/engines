"""PL-9E: kiểm bytes mẫu Excel và đo xuất 20.000 dòng Đỏ DEMO trên máy chạy."""
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


@pytest.mark.parametrize("lua_chon,bam_mau", [
    ("rong", "3c0260d868f2230aab5f9bca841d040fd920ed79d59689f328ce50c7cec8a953"),
    ("xanh", "3c0260d868f2230aab5f9bca841d040fd920ed79d59689f328ce50c7cec8a953"),
    ("hon_hop", "acef57ff27a312ea1c2f60309334267360d72637c89c7c3cac2703fdcb86887c"),
])
def test_bytes_dung_mau_10_cot_pl10c(lua_chon, bam_mau):
    # PL-10C: cập nhật băm do thêm cột Giải thích, bộ lọc A:J và hướng dẫn.
    # Lead: băm tính trong môi trường chỉ có thư viện requirements.lock (không lxml);
    # openpyxl có lxml ghi XML khác byte.
    # 9 cột đầu được đối chiếu từng ô với PL-8 trong test_pl10c_giai_thich.py.
    # Bỏ lớp nén ZIP để chạy trên cả Windows/Linux có phiên bản zlib khác nhau.
    ds = {"rong": [], "xanh": _ds_demo()[1:2], "hon_hop": _ds_demo()}[lua_chon]
    bam = sha256()
    with ZipFile(BytesIO(xuat_excel.lap_ds_do(ds, **META))) as z:
        for ten in sorted(z.namelist()):
            bam.update(ten.encode() + b"\0" + z.read(ten))
    assert bam.hexdigest() == bam_mau


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
        assert ws.auto_filter.ref == "A2:J20002"  # PL-10C: thêm cột Giải thích.
    finally:
        wb.close()
