"""Đọc cấu hình máy ngoài gói, không đọc bí mật hay truy cập nguồn OCR."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path

from kho_tri_thuc_sdk.engine import LoiNghiepVu


THU_MUC_GOI = Path(__file__).resolve().parents[1]
TEP_SCHEMA = THU_MUC_GOI / "contract" / "cau_hinh_may.schema.json"
CAU_HINH_TOI_DA_BYTE = 64 * 1024


def _thu_muc_may() -> Path:
    # Linux dùng /var/lib khi không giả lập PROGRAMDATA; test luôn dùng DEMO.
    goc = os.environ.get("PROGRAMDATA")
    if not goc:
        goc = "C:/ProgramData" if os.name == "nt" else "/var/lib"
    return Path(goc) / "KhoTriThuc" / "engines" / "e_ocr"


def _khong_lap_khoa(cac_cap):
    ket_qua = {}
    for khoa, gia_tri in cac_cap:
        if khoa in ket_qua:
            raise ValueError("JSON có khóa lặp.")
        ket_qua[khoa] = gia_tri
    return ket_qua


def _tu_choi_hang_so(gia_tri):
    raise ValueError("JSON có số không hữu hạn.")


def _kiem_va_dien_mac_dinh(gia_tri, schema):
    """Chỉ hỗ trợ tập con schema cấu hình trong gói, bằng thư viện chuẩn."""
    kieu = schema["type"]
    if kieu == "object":
        if type(gia_tri) is not dict:
            raise ValueError("Cấu hình phải là đối tượng.")
        cac_truong = schema["properties"]
        if set(gia_tri) - set(cac_truong):
            raise ValueError("Cấu hình có trường không được phép.")
        ket_qua = {}
        for ma, truong in cac_truong.items():
            if ma in gia_tri:
                ket_qua[ma] = _kiem_va_dien_mac_dinh(gia_tri[ma], truong)
            elif "default" in truong:
                ket_qua[ma] = _kiem_va_dien_mac_dinh(deepcopy(truong["default"]), truong)
        return ket_qua
    if kieu == "boolean":
        dung = type(gia_tri) is bool
    elif kieu == "integer":
        dung = type(gia_tri) is int
        if dung:
            dung = schema.get("minimum", gia_tri) <= gia_tri <= schema.get("maximum", gia_tri)
    elif kieu == "string":
        dung = type(gia_tri) is str
        if dung:
            dung = schema.get("minLength", 0) <= len(gia_tri) <= schema.get("maxLength", len(gia_tri))
    else:
        raise ValueError("Schema cấu hình có kiểu chưa hỗ trợ.")
    if not dung:
        raise ValueError("Giá trị cấu hình không đúng schema.")
    return gia_tri


def doc_cau_hinh(*, bat_buoc: bool = False) -> dict | None:
    """Thiếu tệp trả None; việc cần cấu hình gọi với bat_buoc=True.

    Không tạo tệp, không đọc Hot Folder hoặc tệp thực thi. Cấu hình phải ở
    ngoài gói; các trường ngoài schema (kể cả khóa dịch vụ) bị từ chối.
    """
    try:
        ten_tep = os.environ.get("KTT_ENGINE_CAU_HINH")
        if ten_tep is not None and not ten_tep.strip():
            raise ValueError("Chưa chọn tệp cấu hình.")
        tep = Path(ten_tep) if ten_tep is not None else _thu_muc_may() / "cau_hinh.json"
        tep = tep.resolve()
        if tep.is_relative_to(THU_MUC_GOI):
            raise ValueError("Cấu hình phải ở ngoài gói.")
        try:
            with tep.open("rb") as luong:
                noi_dung = luong.read(CAU_HINH_TOI_DA_BYTE + 1)
        except FileNotFoundError:
            if bat_buoc:
                raise LoiNghiepVu(
                    "CHUA_CAU_HINH", "Chưa cấu hình nguồn đọc tài liệu. Hãy liên hệ quản trị viên."
                ) from None
            return None
        if len(noi_dung) > CAU_HINH_TOI_DA_BYTE:
            raise ValueError("Tệp cấu hình quá lớn.")
        du_lieu = json.loads(
            noi_dung.decode("utf-8-sig"),
            object_pairs_hook=_khong_lap_khoa,
            parse_constant=_tu_choi_hang_so,
        )
        schema = json.loads(TEP_SCHEMA.read_text(encoding="utf-8"))
        return _kiem_va_dien_mac_dinh(du_lieu, schema)
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise LoiNghiepVu(
            "CAU_HINH_KHONG_HOP_LE",
            "Không đọc được cấu hình nguồn OCR hoặc cấu hình không hợp lệ. Hãy kiểm tra với quản trị viên.",
        ) from None
