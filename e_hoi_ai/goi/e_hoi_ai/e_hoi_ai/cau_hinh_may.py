"""Đọc cấu hình không chứa bí mật ở ngoài gói; chưa có thì trả None.

Chỉ kiểm các từ khóa đang dùng trong schema cấu hình, không thay bộ kiểm
JSON Schema tổng quát của các lát xử lý AI sau này. Không gọi mạng.
"""
import json
import math
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

from kho_tri_thuc_sdk.engine import LoiNghiepVu

THU_MUC_GOI = Path(__file__).resolve().parents[1]


def _loi_cau_hinh():
    return LoiNghiepVu(
        "CAU_HINH_KHONG_HOP_LE",
        "Cấu hình máy Hỏi AI không hợp lệ. Hãy nhờ quản trị viên kiểm tra lại.",
    )


def duong_dan_cau_hinh():
    """Ưu tiên KTT_ENGINE_CAU_HINH; mặc định nằm dưới PROGRAMDATA."""
    gia_tri = os.environ.get("KTT_ENGINE_CAU_HINH")
    if gia_tri is None:
        goc = os.environ.get("PROGRAMDATA")
        if not goc:
            return None
        duong_dan = Path(goc) / "KhoTriThuc" / "engines" / "e_hoi_ai" / "cau_hinh.json"
    else:
        if not gia_tri.strip():
            raise _loi_cau_hinh()
        duong_dan = Path(gia_tri)
    try:
        duong_dan = duong_dan.resolve()
    except (OSError, RuntimeError, ValueError):
        raise _loi_cau_hinh() from None
    if duong_dan.is_relative_to(THU_MUC_GOI):
        raise _loi_cau_hinh()
    return duong_dan


def _khop_schema(gia_tri, schema):
    """Kiểm đúng tập từ khóa của contract/cau_hinh_may.schema.json."""
    kieu = schema["type"]
    if kieu == "object":
        if not isinstance(gia_tri, dict):
            return False
        cac_truong = schema["properties"]
        return (
            all(k in gia_tri for k in schema.get("required", []))
            and (schema.get("additionalProperties", True) or gia_tri.keys() <= cac_truong.keys())
            and all(_khop_schema(v, cac_truong[k]) for k, v in gia_tri.items() if k in cac_truong)
        )
    if kieu == "array":
        return isinstance(gia_tri, list) and all(_khop_schema(v, schema["items"]) for v in gia_tri)
    if kieu == "string":
        return (
            isinstance(gia_tri, str)
            and len(gia_tri) >= schema.get("minLength", 0)
            and ("pattern" not in schema or re.search(schema["pattern"], gia_tri) is not None)
        )
    if kieu == "number":
        return (
            type(gia_tri) in (int, float)
            and (not isinstance(gia_tri, float) or math.isfinite(gia_tri))
            and ("exclusiveMinimum" not in schema or gia_tri > schema["exclusiveMinimum"])
        )
    raise ValueError("Schema cấu hình dùng kiểu chưa được hỗ trợ.")


def _khong_trung_khoa(cac_cap):
    ket_qua = {}
    for khoa, gia_tri in cac_cap:
        if khoa in ket_qua:
            raise ValueError("Tệp JSON có khóa trùng.")
        ket_qua[khoa] = gia_tri
    return ket_qua


def _tu_choi_hang_so(gia_tri):
    raise ValueError("Tệp JSON chứa số không hữu hạn.")


def doc_cau_hinh():
    """Không có tệp thì trả None; lỗi khác được chuyển thành câu an toàn."""
    duong_dan = duong_dan_cau_hinh()
    if duong_dan is None:
        return None
    try:
        noi_dung = duong_dan.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return None
    except UnicodeError:
        raise _loi_cau_hinh() from None
    except (OSError, ValueError):
        raise LoiNghiepVu(
            "CAU_HINH_KHONG_DOC_DUOC",
            "Không đọc được cấu hình máy Hỏi AI. Hãy nhờ quản trị viên kiểm tra lại.",
            thu_lai_duoc=True,
        ) from None
    try:
        cau_hinh = json.loads(noi_dung, object_pairs_hook=_khong_trung_khoa,
                              parse_constant=_tu_choi_hang_so)
        schema = json.loads((THU_MUC_GOI / "contract" / "cau_hinh_may.schema.json").read_text(encoding="utf-8"))
        if not _khop_schema(cau_hinh, schema):
            raise ValueError
        url = urlsplit(cau_hinh["local_ai"]["url"])
        if (not url.hostname or url.username is not None or url.password is not None
                or url.query or url.fragment
                or any(ky_tu.isspace() for ky_tu in cau_hinh["local_ai"]["url"])):
            raise ValueError
        # Truy cập port để bác giá trị sai kiểu hoặc vượt miền cổng.
        url.port
        return cau_hinh
    except (ValueError, RecursionError):
        raise _loi_cau_hinh() from None


def yeu_cau_cau_hinh():
    """Dùng khi xử lý việc cần Local AI; không gọi lúc khởi động engine."""
    cau_hinh = doc_cau_hinh()
    if cau_hinh is None:
        raise LoiNghiepVu(
            "CHUA_CAU_HINH",
            "Chưa cấu hình kết nối Local AI. Hãy nhờ quản trị viên thiết lập trước khi hỏi AI.",
        )
    return cau_hinh
