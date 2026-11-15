"""Đọc cấu hình trong ngăn, điền default và kiểm tập con JSON Schema.

Không đọc tệp, không gọi mạng. Từ khóa ngoài tập hỗ trợ bị từ chối để tránh
chấp nhận nhầm cấu hình chưa được kiểm. Engine đổi ngoại lệ thành LoiNghiepVu.
"""

from copy import deepcopy
import json
import math
import re


class CauHinhKhongHopLe(ValueError):
    ma = "CAU_HINH_KHONG_HOP_LE"
    thong_diep = "Cấu hình engine không hợp lệ. Hãy nhờ quản trị viên kiểm tra lại."
    thu_lai_duoc = False

    def __init__(self):
        super().__init__(self.thong_diep)


_KIEU = {"object", "array", "string", "integer", "number", "boolean", "null"}
_TU_KHOA = {
    "$schema", "$id", "$comment", "title", "description", "examples",
    "type", "default", "enum", "const", "properties", "required",
    "additionalProperties", "items", "minLength", "maxLength", "pattern",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minItems", "maxItems", "uniqueItems", "minProperties", "maxProperties",
}


def _json(gia_tri):
    if type(gia_tri) is dict:
        if any(type(k) is not str for k in gia_tri):
            raise CauHinhKhongHopLe()
        for v in gia_tri.values():
            _json(v)
    elif type(gia_tri) is list:
        for v in gia_tri:
            _json(v)
    elif gia_tri is not None and type(gia_tri) not in (str, bool, int, float):
        raise CauHinhKhongHopLe()
    json.dumps(gia_tri, allow_nan=False)


def _kiem_schema(s):
    if type(s) is bool:
        return
    if type(s) is not dict or not s.keys() <= _TU_KHOA:
        raise CauHinhKhongHopLe()
    if "type" in s and (type(s["type"]) is not str or s["type"] not in _KIEU):
        raise CauHinhKhongHopLe()
    if "enum" in s and (type(s["enum"]) is not list or not s["enum"]):
        raise CauHinhKhongHopLe()
    if "properties" in s:
        if type(s["properties"]) is not dict:
            raise CauHinhKhongHopLe()
        for con in s["properties"].values():
            _kiem_schema(con)
    if "required" in s:
        r = s["required"]
        if type(r) is not list or any(type(k) is not str for k in r) or len(r) != len(set(r)):
            raise CauHinhKhongHopLe()
    for k in ("additionalProperties", "items"):
        if k in s:
            _kiem_schema(s[k])
    for k in ("minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties"):
        if k in s and (type(s[k]) is not int or s[k] < 0):
            raise CauHinhKhongHopLe()
    for k in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        if k in s and (type(s[k]) not in (int, float) or not math.isfinite(s[k])):
            raise CauHinhKhongHopLe()
    if "uniqueItems" in s and type(s["uniqueItems"]) is not bool:
        raise CauHinhKhongHopLe()
    if "pattern" in s:
        if type(s["pattern"]) is not str:
            raise CauHinhKhongHopLe()
        re.compile(s["pattern"])


def _bang_nhau(a, b):
    # JSON Schema phân biệt true với 1, nhưng coi 1 và 1.0 là cùng một số.
    if type(a) is bool or type(b) is bool:
        return type(a) is type(b) and a == b
    if type(a) is dict and type(b) is dict:
        return a.keys() == b.keys() and all(_bang_nhau(a[k], b[k]) for k in a)
    if type(a) is list and type(b) is list:
        return len(a) == len(b) and all(_bang_nhau(x, y) for x, y in zip(a, b))
    return a == b


def _kiem(v, s):
    if s is True:
        return v
    if s is False:
        raise CauHinhKhongHopLe()
    kieu = s.get("type")
    so = type(v) in (int, float)
    dung_kieu = {
        "object": type(v) is dict, "array": type(v) is list,
        "string": type(v) is str, "boolean": type(v) is bool,
        "number": so, "integer": so and (type(v) is int or v.is_integer()),
        "null": v is None,
    }
    if kieu is not None and not dung_kieu[kieu]:
        raise CauHinhKhongHopLe()
    if type(v) is dict:
        v = deepcopy(v)
        thuoc_tinh = s.get("properties", {})
        for k, con in thuoc_tinh.items():
            if k not in v and isinstance(con, dict) and "default" in con:
                v[k] = deepcopy(con["default"])
        if not set(s.get("required", [])) <= v.keys():
            raise CauHinhKhongHopLe()
        for k in v:
            v[k] = _kiem(v[k], thuoc_tinh.get(k, s.get("additionalProperties", True)))
        if not s.get("minProperties", 0) <= len(v) <= s.get("maxProperties", math.inf):
            raise CauHinhKhongHopLe()
    elif type(v) is list:
        v = [_kiem(x, s.get("items", True)) for x in v]
        if not s.get("minItems", 0) <= len(v) <= s.get("maxItems", math.inf):
            raise CauHinhKhongHopLe()
        if s.get("uniqueItems", False) and any(_bang_nhau(x, y) for i, x in enumerate(v) for y in v[:i]):
            raise CauHinhKhongHopLe()
    elif type(v) is str:
        if (not s.get("minLength", 0) <= len(v) <= s.get("maxLength", math.inf)
                or ("pattern" in s and re.search(s["pattern"], v) is None)):
            raise CauHinhKhongHopLe()
    elif so:
        if (v < s.get("minimum", -math.inf) or v > s.get("maximum", math.inf)
                or ("exclusiveMinimum" in s and v <= s["exclusiveMinimum"])
                or ("exclusiveMaximum" in s and v >= s["exclusiveMaximum"])):
            raise CauHinhKhongHopLe()
    if "enum" in s and not any(_bang_nhau(v, x) for x in s["enum"]):
        raise CauHinhKhongHopLe()
    if "const" in s and not _bang_nhau(v, s["const"]):
        raise CauHinhKhongHopLe()
    return v


def doc_cau_hinh(ngan, schema):
    """schema là dict đã đọc từ schema trong gói; thiếu bản ghi trả None.

    Giá trị bản ghi chính là cấu hình, không bọc thêm trường gia_tri. Không tự
    tạo cấu hình bằng default khi chưa được admin lưu. Không ghi ngược ngăn.
    """
    ban = ngan.doc("cau_hinh", {})
    if ban is None:
        return None
    try:
        _json(schema)
        _kiem_schema(schema)
        _json(ban.gia_tri)
        if type(ban.gia_tri) is not dict:
            raise CauHinhKhongHopLe()
        return _kiem(deepcopy(ban.gia_tri), schema)
    except (ValueError, TypeError, RecursionError, OverflowError, re.error):
        raise CauHinhKhongHopLe() from None
