"""Đọc cấu hình qua Ngan; bản tạm theo NGAN-0, không đọc/ghi giá trị ra đĩa."""

from copy import deepcopy
import json
import math
import re


def kiem_schema(gia_tri, schema, *, goc=None):
    """Tập con JSON Schema dùng cho tài nguyên cấu hình; lỗi không mang giá trị."""
    goc = schema if goc is None else goc
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise ValueError("Chỉ hỗ trợ tham chiếu schema trong gói.")
        s = goc
        for k in ref[2:].split("/"):
            s = s[k.replace("~1", "/").replace("~0", "~")]
        return kiem_schema(gia_tri, s, goc=goc)
    for nhanh in ("oneOf", "anyOf"):
        if nhanh in schema:
            dat = 0
            for s in schema[nhanh]:
                try:
                    kiem_schema(gia_tri, s, goc=goc)
                    dat += 1
                except ValueError:
                    pass
            if not dat or (nhanh == "oneOf" and dat != 1):
                raise ValueError("Dữ liệu không đúng schema.")
    kieu = schema.get("type")
    ds = kieu if isinstance(kieu, list) else [kieu] if kieu else []
    dung = {"object": isinstance(gia_tri, dict), "array": isinstance(gia_tri, list),
            "string": isinstance(gia_tri, str), "integer": type(gia_tri) is int,
            "number": type(gia_tri) in (int, float), "boolean": type(gia_tri) is bool,
            "null": gia_tri is None}
    if ds and not any(dung.get(k, False) for k in ds):
        raise ValueError("Dữ liệu không đúng kiểu cấu hình.")
    if "const" in schema and (type(gia_tri) is not type(schema["const"]) or gia_tri != schema["const"]):
        raise ValueError("Dữ liệu không đúng giá trị cố định.")
    if "enum" in schema and gia_tri not in schema["enum"]:
        raise ValueError("Dữ liệu không thuộc danh sách cho phép.")
    if isinstance(gia_tri, dict):
        props = schema.get("properties", {})
        if any(k not in gia_tri for k in schema.get("required", [])):
            raise ValueError("Cấu hình thiếu trường bắt buộc.")
        if schema.get("additionalProperties") is False and set(gia_tri) - set(props):
            raise ValueError("Cấu hình có trường chưa được khai báo.")
        for k, v in gia_tri.items():
            if k in props:
                kiem_schema(v, props[k], goc=goc)
    elif isinstance(gia_tri, list):
        if not schema.get("minItems", 0) <= len(gia_tri) <= schema.get("maxItems", math.inf):
            raise ValueError("Số phần tử vượt giới hạn schema.")
        for v in gia_tri:
            kiem_schema(v, schema.get("items", {}), goc=goc)
    elif isinstance(gia_tri, str):
        if not schema.get("minLength", 0) <= len(gia_tri) <= schema.get("maxLength", math.inf):
            raise ValueError("Độ dài vượt giới hạn schema.")
        if "pattern" in schema and re.search(schema["pattern"], gia_tri) is None:
            raise ValueError("Chuỗi không đúng mẫu schema.")
    elif type(gia_tri) in (int, float):
        if ((type(gia_tri) is float and not math.isfinite(gia_tri))
                or gia_tri < schema.get("minimum", -math.inf)
                or gia_tri > schema.get("maximum", math.inf)
                or gia_tri <= schema.get("exclusiveMinimum", -math.inf)
                or gia_tri >= schema.get("exclusiveMaximum", math.inf)):
            raise ValueError("Giá trị số vượt giới hạn cấu hình.")


def _dien_mac_dinh(v, schema):
    v = deepcopy(v)
    if isinstance(v, dict):
        for k, s in schema.get("properties", {}).items():
            if k not in v and "default" in s:
                v[k] = deepcopy(s["default"])
            if k in v:
                v[k] = _dien_mac_dinh(v[k], s)
    return v


def doc_cau_hinh(ngan, schema):
    ban_ghi = ngan.doc("cau_hinh", {"ma": "mac_dinh"})
    if ban_ghi is None:
        return None
    v = ban_ghi.gia_tri.get("gia_tri")
    try:
        raw = json.dumps(v, ensure_ascii=False, allow_nan=False,
                         separators=(",", ":")).encode("utf-8")
        if len(raw) > 65536:
            raise ValueError
        if not isinstance(v, dict):
            raise ValueError
        v = _dien_mac_dinh(v, schema)
        kiem_schema(v, schema)
        if len(json.dumps(v, ensure_ascii=False, allow_nan=False).encode("utf-8")) > 65536:
            raise ValueError
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise ValueError("Cấu hình không đúng cấu trúc hoặc vượt 64 KiB.") from None
    return v
