"""Đọc cấu hình từ ngăn; bản tạm chờ NGAN-0, chỉ dùng thư viện chuẩn."""
from copy import deepcopy
import math
import re


def _kiem(gia_tri, schema):
    kieu = schema.get("type")
    dung = {"object": isinstance(gia_tri, dict), "array": isinstance(gia_tri, list),
            "string": isinstance(gia_tri, str), "boolean": type(gia_tri) is bool,
            "integer": type(gia_tri) is int, "null": gia_tri is None,
            "number": type(gia_tri) in (int, float) and math.isfinite(gia_tri)}
    if kieu is not None and not dung.get(kieu, False):
        raise ValueError("Cấu hình không đúng kiểu dữ liệu.")
    if "enum" in schema and gia_tri not in schema["enum"]:
        raise ValueError("Giá trị cấu hình không được chấp nhận.")
    if "const" in schema and gia_tri != schema["const"]:
        raise ValueError("Giá trị cấu hình không được chấp nhận.")
    if isinstance(gia_tri, dict):
        thuoc_tinh = schema.get("properties", {})
        for k, s in thuoc_tinh.items():
            if k not in gia_tri and "default" in s:
                gia_tri[k] = deepcopy(s["default"])
        if any(k not in gia_tri for k in schema.get("required", [])):
            raise ValueError("Cấu hình thiếu trường bắt buộc.")
        for k, v in gia_tri.items():
            if k in thuoc_tinh:
                _kiem(v, thuoc_tinh[k])
            elif schema.get("additionalProperties") is False:
                raise ValueError("Cấu hình có trường chưa được hỗ trợ.")
    if isinstance(gia_tri, list):
        if not schema.get("minItems", 0) <= len(gia_tri) <= schema.get("maxItems", math.inf):
            raise ValueError("Số mục cấu hình vượt giới hạn.")
        for v in gia_tri:
            _kiem(v, schema.get("items", {}))
    if isinstance(gia_tri, str):
        if not schema.get("minLength", 0) <= len(gia_tri) <= schema.get("maxLength", math.inf):
            raise ValueError("Độ dài cấu hình vượt giới hạn.")
        if "pattern" in schema and re.search(schema["pattern"], gia_tri) is None:
            raise ValueError("Nội dung cấu hình không đúng định dạng.")
    if type(gia_tri) in (int, float):
        if not math.isfinite(gia_tri) or any((
            "minimum" in schema and gia_tri < schema["minimum"],
            "maximum" in schema and gia_tri > schema["maximum"],
            "exclusiveMinimum" in schema and gia_tri <= schema["exclusiveMinimum"],
        )):
            raise ValueError("Giá trị số cấu hình vượt giới hạn.")


def doc_cau_hinh(ngan, schema):
    """Bản ghi hệ thống khóa rỗng; trả None khi chưa cấu hình, bản sao đã điền mặc định."""
    ban_ghi = ngan.doc("cau_hinh", {})
    if ban_ghi is None:
        return None
    gia_tri = deepcopy(ban_ghi.gia_tri)
    _kiem(gia_tri, schema)
    return gia_tri
