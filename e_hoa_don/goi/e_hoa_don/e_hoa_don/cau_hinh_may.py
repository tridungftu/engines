"""Cấu hình JSON ngoài gói; XML thuần không gọi hàm này hay tạo dữ liệu bền."""

from __future__ import annotations

import json
import os
from pathlib import Path

from kho_tri_thuc_sdk.engine import LoiNghiepVu

THU_MUC_GOI = Path(__file__).resolve().parents[1]
CAU_HINH_TOI_DA_BYTE = 64 * 1024


def _tep_mac_dinh() -> Path | None:
    goc = os.environ.get("PROGRAMDATA")
    if goc is None and os.name == "nt":
        goc = "C:/ProgramData"
    # Linux không tự suy đường máy Windows; test cấp đường DEMO tạm.
    if not goc:
        return None
    return Path(goc) / "KhoTriThuc" / "engines" / "e_hoa_don" / "cau_hinh.json"


def _khong_lap_khoa(cac_cap):
    ket_qua = {}
    for khoa, gia_tri in cac_cap:
        if khoa in ket_qua:
            raise ValueError("JSON có khóa lặp.")
        ket_qua[khoa] = gia_tri
    return ket_qua


def _tu_choi_hang_so(gia_tri):
    raise ValueError("JSON có hằng số không hợp lệ.")


def doc_cau_hinh(*, bat_buoc: bool = False) -> dict | None:
    """Không đọc ở import/khởi động. Chỉ tính năng cần mới yêu cầu cấu hình."""
    try:
        ten = os.environ.get("KTT_ENGINE_CAU_HINH")
        if ten is not None and not ten.strip():
            raise ValueError("Đường cấu hình rỗng.")
        tep = Path(ten) if ten is not None else _tep_mac_dinh()
        if tep is not None:
            tep = tep.resolve()
            if tep.is_relative_to(THU_MUC_GOI):
                raise ValueError("Cấu hình nằm trong gói.")
            try:
                with tep.open("rb") as luong:
                    raw = luong.read(CAU_HINH_TOI_DA_BYTE + 1)
            except FileNotFoundError:
                raw = None
        else:
            raw = None
        if raw is None:
            if bat_buoc:
                raise LoiNghiepVu("CHUA_CAU_HINH", "Chưa cấu hình chức năng này.")
            return None
        if len(raw) > CAU_HINH_TOI_DA_BYTE:
            raise ValueError("Cấu hình vượt trần.")
        du_lieu = json.loads(
            raw.decode("utf-8-sig"), object_pairs_hook=_khong_lap_khoa,
            parse_constant=_tu_choi_hang_so,
        )
        # Tập con schema duy nhất của HD-0: không ép bool/float thành integer.
        if (type(du_lieu) is not dict or set(du_lieu) != {"phien_ban"}
                or type(du_lieu["phien_ban"]) is not int or du_lieu["phien_ban"] != 1):
            raise ValueError("Cấu hình không đúng schema phiên bản 1.")
        return du_lieu
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise LoiNghiepVu(
            "CAU_HINH_MAY_KHONG_HOP_LE",
            "Cấu hình máy không hợp lệ. Hãy liên hệ quản trị viên.",
        ) from None
