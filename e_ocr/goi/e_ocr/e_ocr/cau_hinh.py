"""Đọc cấu hình từ ngăn; lớp bọc tạm theo NGAN-0, chỉ thư viện chuẩn."""

from copy import deepcopy
import json
import math
import re


def _kiem(gia_tri, schema):
    kieu = schema.get("type")
    hop_le = {
        "object": type(gia_tri) is dict, "array": type(gia_tri) is list,
        "string": type(gia_tri) is str, "integer": type(gia_tri) is int,
        "number": type(gia_tri) in (int, float) and math.isfinite(gia_tri),
        "boolean": type(gia_tri) is bool, "null": gia_tri is None,
    }
    if kieu is not None and not hop_le.get(kieu, False):
        raise ValueError("Giá trị cấu hình không đúng kiểu.")
    if "enum" in schema and gia_tri not in schema["enum"]:
        raise ValueError("Giá trị cấu hình không thuộc danh sách cho phép.")
    if kieu == "object":
        cac_truong = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(gia_tri) - set(cac_truong):
            raise ValueError("Cấu hình có trường không được phép.")
        gia_tri = deepcopy(gia_tri)
        for ma, truong in cac_truong.items():
            if ma not in gia_tri and "default" in truong:
                gia_tri[ma] = deepcopy(truong["default"])
            if ma in gia_tri:
                gia_tri[ma] = _kiem(gia_tri[ma], truong)
        if set(schema.get("required", [])) - set(gia_tri):
            raise ValueError("Cấu hình thiếu trường bắt buộc.")
    elif kieu == "array":
        if not schema.get("minItems", 0) <= len(gia_tri) <= schema.get("maxItems", len(gia_tri)):
            raise ValueError("Danh sách cấu hình vượt giới hạn.")
        gia_tri = [_kiem(v, schema.get("items", {})) for v in gia_tri]
    elif kieu == "string":
        if (not schema.get("minLength", 0) <= len(gia_tri) <= schema.get("maxLength", len(gia_tri))
                or ("pattern" in schema and re.search(schema["pattern"], gia_tri) is None)):
            raise ValueError("Chuỗi cấu hình không hợp lệ.")
    elif kieu in {"integer", "number"}:
        if not schema.get("minimum", gia_tri) <= gia_tri <= schema.get("maximum", gia_tri):
            raise ValueError("Số trong cấu hình vượt giới hạn.")
    return gia_tri


def doc_cau_hinh(ngan, schema):
    ban_ghi = ngan.doc("cau_hinh", {"ma": "cau_hinh"})
    if ban_ghi is None:
        return None
    gia_tri = deepcopy(ban_ghi.gia_tri)
    gia_tri.pop("ma", None)
    if len(json.dumps(gia_tri, ensure_ascii=False, allow_nan=False).encode("utf-8")) > 65536:
        raise ValueError("Cấu hình vượt giới hạn 64 KiB.")
    return _kiem(gia_tri, schema)
