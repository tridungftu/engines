"""Đọc cấu hình máy ngoài gói; chưa khai tài nguyên."""
import json
import os
from pathlib import Path
from kho_tri_thuc_sdk.engine import LoiNghiepVu

GOI = Path(__file__).resolve().parents[1]

def _loi():
    return LoiNghiepVu("MASK_CAU_HINH_KHONG_HOP_LE", "Cấu hình máy không hợp lệ. Hãy nhờ quản trị viên kiểm tra.")

def duong_dan_cau_hinh():
    gia_tri = os.environ.get("KTT_ENGINE_CAU_HINH")
    if gia_tri is None:
        if os.name != "nt" or not os.environ.get("PROGRAMDATA"):
            return None
        duong_dan = Path(os.environ["PROGRAMDATA"]) / "KhoTriThuc" / "engines" / "e_mask" / "cau_hinh.json"
    elif not gia_tri.strip():
        raise _loi()
    else:
        duong_dan = Path(gia_tri)
    try:
        duong_dan = duong_dan.resolve()
        if duong_dan.is_relative_to(GOI):
            raise ValueError
        return duong_dan
    except (OSError, RuntimeError, ValueError):
        raise _loi() from None

def _cap_khong_trung(cac_cap):
    ket_qua = {}
    for khoa, gia_tri in cac_cap:
        if khoa in ket_qua:
            raise ValueError
        ket_qua[khoa] = gia_tri
    return ket_qua

def _khong_huu_han(_):
    raise ValueError

def doc_cau_hinh():
    duong_dan = duong_dan_cau_hinh()
    if duong_dan is None:
        return None
    try:
        noi_dung = duong_dan.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, ValueError):
        raise _loi() from None
    try:
        cau_hinh = json.loads(noi_dung, object_pairs_hook=_cap_khong_trung, parse_constant=_khong_huu_han)
        schema = json.loads((Path(__file__).parent / "schemas" / "cau_hinh_may.schema.json").read_text(encoding="utf-8"))
        if not isinstance(cau_hinh, dict) or (not schema["additionalProperties"] and cau_hinh.keys() - schema["properties"].keys()):
            raise ValueError
        return cau_hinh
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise _loi() from None

def yeu_cau_cau_hinh():
    cau_hinh = doc_cau_hinh()
    if cau_hinh is None:
        raise LoiNghiepVu("MASK_CHUA_CAU_HINH", "Chưa có cấu hình máy. Hãy nhờ quản trị viên thiết lập.")
    return cau_hinh
