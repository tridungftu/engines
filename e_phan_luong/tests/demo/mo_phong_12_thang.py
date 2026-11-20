"""Sinh DEMO PL-9A tất định, không ghi tệp và không dùng random toàn cục.

Mặc định: 80 nghiệp vụ/loại/tháng (xấp xỉ 100), 3 loại, một khâu ktt_duyet;
thêm một dòng Đỏ cứng của loại lỗi vào tháng 4/8/12 để kiểm lỗi >= SAD.
Loại sạch có NHAP_TAY (x1,5), đủ quan sát cả ba lần xuống bậc trong 12 tháng.
Ca lớn: 100 nghiệp vụ lỗi/tháng, không cài lỗi SAD; DOI_TAC_MOI x NHAP_TAY
(x3) làm p = 90%/60% ở bậc 30%/20%, vẫn là CHON_MAU theo hợp đồng.
Tỷ lệ lỗi nền 8%
là xác suất theo SHA-256 của mã nghiệp vụ, không ép đúng 8% từng lô.

Chạy ``python -B tests/demo/mo_phong_12_thang.py`` từ thư mục engine
để nhận JSON UTF-8 qua stdout; cùng tham số cho cùng bytes trên Windows/Linux.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from fractions import Fraction
from hashlib import sha256
import json
import sys


CONG_TY = "Công ty DEMO Ánh Dương"
MA_MODULE = "demo_anh_duong"
KHAU = "ktt_duyet"
LOAI_SACH = "sach_demo"
LOAI_LOI = "loi_8_demo"
CHUA_PHAN_LOAI = "chua_phan_loai"
CAC_LOAI = (LOAI_SACH, LOAI_LOI, CHUA_PHAN_LOAI)
SO_MOI_LOAI = 80
SO_CA_LON = 100
HAT_GIONG = sha256(b"PL-9A|Cong ty DEMO Anh Duong|2026|v1").digest()
NGUONG = {ten: {"so": str(so), "tien_te": "VND"} for ten, so in (
    ("pm", 5_000_000_000), ("te", 3_000_000_000), ("sad", 250_000_000))}


def ma_hoa(gia_tri) -> bytes:
    """JSON chuẩn, không BOM/CRLF, không phụ thuộc thứ tự khóa."""
    return (json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def ngay_lam_viec(thang: int) -> date:
    ngay = date(2026, thang, 10)
    while ngay.weekday() >= 5:
        ngay += timedelta(days=1)
    return ngay


def sinh_lo(thang: int, *, so_moi_loai: int = SO_MOI_LOAI,
            cac_loai: tuple[str, ...] = CAC_LOAI, them_sad: bool = True,
            nhap_tay_sach: bool = False, tang_mau_loi: bool = False) -> dict:
    """Tiền vùng chọn mẫu; mặc định không cờ, các cờ DEMO bật tường minh."""
    if not 1 <= thang <= 12 or so_moi_loai < 1 or not set(cac_loai) <= set(CAC_LOAI):
        raise ValueError("Tham số sinh DEMO chưa hợp lệ.")
    dong = []
    for loai in cac_loai:
        for stt in range(so_moi_loai):
            dong.append({
                "ma": f"PC-DEMO-{thang:02d}-{loai}-{stt:05d}",
                "loai": None if loai == CHUA_PHAN_LOAI else loai,
                "ngay": ngay_lam_viec(thang).isoformat(),
                "so_tien": {"so": "300000001", "tien_te": "VND"},
                "doi_tac": f"DEMO-NCC-{thang:02d}-{stt:05d}" if tang_mau_loi else None,
                "dien_giai": CONG_TY,
                "nhap_tay": (nhap_tay_sach and loai == LOAI_SACH) or tang_mau_loi,
                "co_do_cung": False,
            })
        if them_sad and loai == LOAI_LOI and thang in (4, 8, 12):
            dong.append({**dong[-1], "ma": f"PC-DEMO-{thang:02d}-{loai}-SAD",
                         "co_do_cung": True})
    return {"phien_ban": 1, "ma_module": MA_MODULE, "ky": f"2026-{thang:02d}",
            "nguong": NGUONG, "nghiep_vu": dong}


def ket_qua_nguoi_kiem(dong: dict) -> dict:
    """Chỉ nhận dòng Đỏ; băm mã nghiệp vụ, độc lập băm chọn mẫu."""
    if dong["luong"] != "do":
        raise ValueError("Người kiểm DEMO chỉ kiểm dòng Đỏ.")
    bam = int.from_bytes(sha256(dong["ma"].encode("utf-8")).digest(), "big")
    sad = dong["ma"].endswith("-SAD")
    sai = dong["loai"] == LOAI_LOI and (sad or Fraction(bam, 2**256) < Fraction(8, 100))
    return {"ma": dong["ma"], "khau": KHAU, "ket_qua": "sai" if sai else "dat",
            "so_tien_sai": {"so": "250000000" if sad else "1" if sai else "0",
                            "tien_te": "VND"}, "loai_dung": None}


def sinh_kich_ban(*, ca_lon: bool = False) -> bytes:
    return ma_hoa({
        "cong_ty": CONG_TY, "khau": KHAU, "hat_giong_hex": HAT_GIONG.hex(),
        "so_nghiep_vu_moi_loai_moi_thang": SO_CA_LON if ca_lon else SO_MOI_LOAI,
        "lo": [sinh_lo(thang, so_moi_loai=SO_CA_LON if ca_lon else SO_MOI_LOAI,
                       cac_loai=(LOAI_LOI,) if ca_lon else CAC_LOAI,
                       them_sad=not ca_lon, nhap_tay_sach=not ca_lon,
                       tang_mau_loi=ca_lon) for thang in range(1, 13)],
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sinh dữ liệu DEMO PL-9A tất định.")
    parser.add_argument("--ca-lon", action="store_true", help="100 nghiệp vụ lỗi/tháng, hệ số cờ x3.")
    sys.stdout.buffer.write(sinh_kich_ban(ca_lon=parser.parse_args().ca_lon))
