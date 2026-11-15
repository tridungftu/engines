"""Tập con JSON Schema 2020-12, kiểm offline và từ chối từ khóa ngoài tập hỗ trợ.

Không tự tải $ref. Trần độ sâu 64 bảo vệ cả schema lẫn dữ liệu; không âm thầm
bỏ qua điều kiện mà bộ kiểm không hiểu. Không phụ thuộc thư viện ngoài SDK.
"""
import json
import math
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

KIEU = {"object", "array", "string", "number", "integer", "boolean", "null"}
CHU_THICH = {"$schema", "$id", "$comment", "title", "description", "default", "examples"}
TU_KHOA = CHU_THICH | {
    "$ref", "$defs", "type", "enum", "const", "properties", "required",
    "additionalProperties", "items", "prefixItems", "minItems", "maxItems", "uniqueItems",
    "minLength", "maxLength", "minimum", "maximum", "exclusiveMinimum",
    "exclusiveMaximum", "multipleOf", "minProperties", "maxProperties", "allOf", "anyOf",
    "oneOf", "not",
}


def json_chuan(gia_tri):
    """UTF-8, sắp khóa, không khoảng trắng, giữ Unicode và giá trị JSON hữu hạn."""
    return json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def doc_json(text):
    def khong_trung(cap):
        kq = {}
        for k, v in cap:
            if k in kq:
                raise ValueError
            kq[k] = v
        return kq

    def cam_hang_so(_):
        raise ValueError

    kq = json.loads(text, object_pairs_hook=khong_trung, parse_constant=cam_hang_so)
    json_chuan(kq)  # Bác cả 1e999 và surrogate không thể mã hóa UTF-8.
    return kq


def _tham_chieu(goc, ref):
    if not isinstance(ref, str) or (ref != "#" and not ref.startswith("#/")):
        raise ValueError
    kq = goc
    cac_khoa = ref[2:].split("/") if ref != "#" else []
    cac_khoa_da_giai = []
    for khoa in cac_khoa:
        if re.search(r"~(?![01])", khoa):
            raise ValueError
        cac_khoa_da_giai.append(khoa.replace("~1", "/").replace("~0", "~"))
    i = 0
    while i < len(cac_khoa_da_giai):
        khoa = cac_khoa_da_giai[i]
        # Chỉ tham chiếu vị trí schema, không coi const/default/examples là schema.
        if khoa in {"properties", "$defs"} and i + 1 < len(cac_khoa_da_giai):
            kq = kq[khoa][cac_khoa_da_giai[i + 1]]
            i += 2
        elif khoa in {"allOf", "anyOf", "oneOf", "prefixItems"} and i + 1 < len(cac_khoa_da_giai):
            chi_so = cac_khoa_da_giai[i + 1]
            if not re.fullmatch(r"0|[1-9][0-9]*", chi_so):
                raise ValueError
            kq = kq[khoa][int(chi_so)]
            i += 2
        elif khoa in {"additionalProperties", "items", "not"}:
            kq = kq[khoa]
            i += 1
        else:
            raise ValueError
    if not isinstance(kq, (dict, bool)):
        raise ValueError
    return kq


def _kiem_khai_bao(s, goc, sau=0, da_kiem=None, dang_kiem=None):
    if sau > 64 or not isinstance(s, (dict, bool)):
        raise ValueError
    if isinstance(s, bool):
        return
    if da_kiem is None:
        da_kiem = set()
        dang_kiem = set()
    if id(s) in dang_kiem:
        raise ValueError  # Tập con không nhận schema có vòng $ref.
    if id(s) in da_kiem:
        return
    da_kiem.add(id(s))
    dang_kiem.add(id(s))
    if not s.keys() <= TU_KHOA:
        raise ValueError
    if "$schema" in s and s["$schema"] != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError
    if "$id" in s and not isinstance(s["$id"], str):
        raise ValueError
    # Tập con chỉ có một không gian $ref ở gốc, không hỗ trợ resource lồng.
    if sau and "$id" in s:
        raise ValueError
    if "$ref" in s:
        _kiem_khai_bao(_tham_chieu(goc, s["$ref"]), goc, sau + 1, da_kiem, dang_kiem)
    if "type" in s:
        ts = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not ts or any(not isinstance(t, str) or t not in KIEU for t in ts) or len(set(ts)) != len(ts):
            raise ValueError
    if "enum" in s:
        if not isinstance(s["enum"], list) or not s["enum"]:
            raise ValueError
        if any(_bang(a, b) for i, a in enumerate(s["enum"]) for b in s["enum"][:i]):
            raise ValueError
    if "required" in s:
        r = s["required"]
        if not isinstance(r, list) or any(not isinstance(k, str) for k in r) or len(set(r)) != len(r):
            raise ValueError
    for k in ("minItems", "maxItems", "minLength", "maxLength", "minProperties", "maxProperties"):
        if k in s and (type(s[k]) is not int or s[k] < 0):
            raise ValueError
    for k in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"):
        if k in s and (type(s[k]) not in (int, float) or type(s[k]) is float and not math.isfinite(s[k])
                       or (k == "multipleOf" and s[k] <= 0)):
            raise ValueError
    if "uniqueItems" in s and type(s["uniqueItems"]) is not bool:
        raise ValueError
    for k in ("properties", "$defs"):
        if k in s:
            if not isinstance(s[k], dict):
                raise ValueError
            for v in s[k].values():
                _kiem_khai_bao(v, goc, sau + 1, da_kiem, dang_kiem)
    for k in ("additionalProperties", "items", "not"):
        if k in s:
            _kiem_khai_bao(s[k], goc, sau + 1, da_kiem, dang_kiem)
    for k in ("prefixItems", "allOf", "anyOf", "oneOf"):
        if k in s:
            if not isinstance(s[k], list) or not s[k]:
                raise ValueError
            for v in s[k]:
                _kiem_khai_bao(v, goc, sau + 1, da_kiem, dang_kiem)
    dang_kiem.remove(id(s))


def kiem_khuon(khuon):
    try:
        json_chuan(khuon)
        _kiem_khai_bao(khuon, khuon)
    except (ValueError, TypeError, KeyError, IndexError, RecursionError, OverflowError):
        raise LoiNghiepVu(
            "KHUON_KHONG_HOP_LE",
            "Khuôn trả lời không hợp lệ hoặc dùng điều kiện chưa được hỗ trợ. Hãy nhờ quản trị viên module kiểm tra.",
        ) from None


def _bang(a, b):
    # JSON Schema phân biệt boolean với number, coi 1 và 1.0 là cùng giá trị.
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_bang(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_bang(x, y) for x, y in zip(a, b))
    return a == b


def _la_kieu(v, t):
    return {"object": isinstance(v, dict), "array": isinstance(v, list),
            "string": isinstance(v, str), "number": type(v) in (int, float),
            "integer": type(v) is int or type(v) is float and v.is_integer(),
            "boolean": type(v) is bool, "null": v is None}[t]


class _QuaTranKiem(ValueError):
    pass


def khop(v, s, goc=None, sau=0, ngan_sach=None):
    """Schema đã được kiem_khuon trước; False khi vượt trần hoặc ref đệ quy quá sâu."""
    if ngan_sach is None:
        try:
            return khop(v, s, goc, sau, [100_000])
        except _QuaTranKiem:
            return False
    ngan_sach[0] -= 1
    if sau > 64 or ngan_sach[0] < 0:
        raise _QuaTranKiem
    if isinstance(s, bool):
        return s
    if goc is None:
        goc = s
    def con(x, k):
        return khop(x, k, goc, sau + 1, ngan_sach)
    if "$ref" in s and not con(v, _tham_chieu(goc, s["$ref"])):
        return False
    if "type" in s and not any(_la_kieu(v, t) for t in (s["type"] if isinstance(s["type"], list) else [s["type"]])):
        return False
    if "const" in s and not _bang(v, s["const"]):
        return False
    if "enum" in s and not any(_bang(v, a) for a in s["enum"]):
        return False
    for k in ("allOf", "anyOf", "oneOf"):
        if k in s:
            n = sum(con(v, a) for a in s[k])
            if (k == "allOf" and n != len(s[k])) or (k == "anyOf" and n == 0) or (k == "oneOf" and n != 1):
                return False
    if "not" in s and con(v, s["not"]):
        return False
    if isinstance(v, dict):
        props = s.get("properties", {})
        if (not all(k in v for k in s.get("required", []))
                or not s.get("minProperties", 0) <= len(v) <= s.get("maxProperties", math.inf)):
            return False
        return all(con(x, props[k] if k in props else s.get("additionalProperties", True)) for k, x in v.items())
    if isinstance(v, list):
        if not s.get("minItems", 0) <= len(v) <= s.get("maxItems", math.inf):
            return False
        if s.get("uniqueItems") and any(_bang(x, y) for i, x in enumerate(v) for y in v[:i]):
            return False
        prefix = s.get("prefixItems", [])
        return all(con(x, prefix[i] if i < len(prefix) else s.get("items", True)) for i, x in enumerate(v))
    if isinstance(v, str):
        return s.get("minLength", 0) <= len(v) <= s.get("maxLength", math.inf)
    if type(v) in (int, float):
        from fractions import Fraction
        if type(v) is float and not math.isfinite(v):
            return False
        if "multipleOf" in s and Fraction(str(v)) % Fraction(str(s["multipleOf"])) != 0:
            return False
        return (v >= s.get("minimum", -math.inf) and v <= s.get("maximum", math.inf)
                and v > s.get("exclusiveMinimum", -math.inf) and v < s.get("exclusiveMaximum", math.inf))
    return True


def boc_khuon(khuon):
    """Khuôn truyền Local: giữ riêng dữ liệu module và các dẫn chứng AI-1.

    $ref nội bộ được chuyển gốc vào $defs/khuon; không thay đổi khuôn đầu vào.
    """
    def chuyen(s):
        if isinstance(s, bool):
            return s
        kq = {k: v for k, v in s.items() if k not in {"$id", "$schema"}}
        if "$ref" in kq:
            kq["$ref"] = "#/$defs/khuon" + kq["$ref"][1:]
        for k in ("properties", "$defs"):
            if k in kq:
                kq[k] = {n: chuyen(v) for n, v in kq[k].items()}
        for k in ("additionalProperties", "items", "not"):
            if k in kq:
                kq[k] = chuyen(kq[k])
        for k in ("prefixItems", "allOf", "anyOf", "oneOf"):
            if k in kq:
                kq[k] = [chuyen(v) for v in kq[k]]
        return kq

    return {"type": "object", "required": ["du_lieu", "truong"], "additionalProperties": False,
            "$defs": {"khuon": chuyen(khuon)}, "properties": {
                "du_lieu": {"allOf": [{"type": "object"}, {"$ref": "#/$defs/khuon"}]},
                "truong": {"type": "array", "items": {"type": "object",
                    "required": ["gia_tri", "trich_dan"], "additionalProperties": False,
                    "properties": {"ten": {"type": "string"}, "gia_tri": {"type": "string"},
                                   "trich_dan": {"type": "string"}}}},
            }}
