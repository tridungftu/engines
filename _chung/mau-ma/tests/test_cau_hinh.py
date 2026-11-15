from copy import deepcopy
from types import SimpleNamespace

import pytest

from cau_hinh import CauHinhKhongHopLe, doc_cau_hinh


def luu(ngan, v):
    with ngan.lo() as lo:
        lo.them("cau_hinh", {}, v)


def test_thieu_config_khong_tu_tao_bang_default(ngan):
    assert doc_cau_hinh(ngan, {"type": "object", "default": {"DEMO": True}}) is None
    assert ngan.doc("cau_hinh", {}) is None


def test_default_long_nhau_khong_ghi_nguoc_va_khong_sua_schema(ngan):
    schema = {"type": "object", "required": ["local_ai"], "additionalProperties": False,
              "properties": {"local_ai": {"type": "object", "default": {}, "required": ["timeout"],
                                          "properties": {"timeout": {"type": "integer", "default": 30, "minimum": 1}}},
                             "model": {"type": "array", "default": ["DEMO"]}}}
    cu = deepcopy(schema)
    luu(ngan, {})
    ban = ngan.doc("cau_hinh", {})
    kq = doc_cau_hinh(ngan, schema)
    assert kq == {"local_ai": {"timeout": 30}, "model": ["DEMO"]}
    kq["model"].append("DEMO-2")
    assert doc_cau_hinh(ngan, schema)["model"] == ["DEMO"]
    assert schema == cu
    assert ngan.doc("cau_hinh", {}).gia_tri == {}
    assert ngan.doc("cau_hinh", {}).row_version == ban.row_version


@pytest.mark.parametrize("s,v,dat", [
    ({"type": "integer", "minimum": 1, "maximum": 10}, 1, True),
    ({"type": "integer"}, True, False),
    ({"type": "integer"}, 1.5, False),
    ({"type": "integer"}, 1.0, True),
    ({"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 10}, 0, False),
    ({"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 10}, 10, False),
    ({"type": "number", "minimum": 1}, 0, False),
    ({"type": "number", "maximum": 1}, 2, False),
    ({"type": "string", "minLength": 2, "maxLength": 4, "pattern": "^DE"}, "DEMO", True),
    ({"type": "string", "minLength": 2}, "D", False),
    ({"type": "string", "maxLength": 2}, "DEMO", False),
    ({"type": "string", "pattern": "^DE"}, "MO", False),
    ({"type": "boolean"}, False, True),
    ({"type": "boolean"}, 0, False),
    ({"type": "null"}, None, True),
    ({"type": "null"}, "", False),
    ({"enum": [1]}, True, False),
    ({"enum": [1]}, 1.0, True),
    ({"const": "DEMO"}, "DEMO-2", False),
    ({"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 2}, ["DEMO"], True),
    ({"type": "array", "items": {"type": "string"}}, [1], False),
    ({"type": "array", "minItems": 1}, [], False),
    ({"type": "array", "maxItems": 1}, [1, 2], False),
    ({"type": "array", "uniqueItems": True}, [1, 1.0], False),
    ({"type": "array", "uniqueItems": True}, [1, True], True),
    ({"type": "object", "required": ["DEMO"]}, {}, False),
    ({"type": "object", "additionalProperties": False}, {"DEMO": 1}, False),
    ({"type": "object", "additionalProperties": {"type": "string"}}, {"DEMO": 1}, False),
    ({"type": "object", "minProperties": 1}, {}, False),
    ({"type": "object", "maxProperties": 0}, {"DEMO": 1}, False),
    (False, "DEMO", False), (True, "DEMO", True),
])
def test_tap_con_schema(ngan, s, v, dat):
    luu(ngan, {"DEMO": v})
    schema = {"type": "object", "properties": {"DEMO": s}}
    if dat:
        assert doc_cau_hinh(ngan, schema) == {"DEMO": v}
    else:
        with pytest.raises(CauHinhKhongHopLe):
            doc_cau_hinh(ngan, schema)


@pytest.mark.parametrize("schema", [
    {"type": "khong_co"}, {"$ref": "https://DEMO.invalid/schema"}, {"oneOf": []},
    {"format": "uri"}, {"type": ["string", "null"]}, {"minimum": True},
    {"pattern": "["}, {"properties": {"chua_dung": {"$ref": "DEMO"}}},
    {"items": []}, {"required": "DEMO"}, {"minLength": -1}, {"uniqueItems": 1},
    {"enum": []}, {"properties": []},
])
def test_schema_sai_hoac_chua_ho_tro_bi_tu_choi(ngan, schema):
    luu(ngan, {})
    with pytest.raises(CauHinhKhongHopLe):
        doc_cau_hinh(ngan, schema)


def test_default_sai_cung_phai_kiem(ngan):
    luu(ngan, {})
    with pytest.raises(CauHinhKhongHopLe):
        doc_cau_hinh(ngan, {"properties": {"DEMO": {"type": "integer", "default": "DEMO"}}})


@pytest.mark.parametrize("v", [{"DEMO": float("nan")}, {"DEMO": float("inf")}, [], {"DEMO": object()}])
def test_config_khong_json_va_loi_khong_lo_gia_tri(v):
    class NganGia:
        def doc(self, bang, khoa):
            return SimpleNamespace(gia_tri=v)
    with pytest.raises(CauHinhKhongHopLe) as loi:
        doc_cau_hinh(NganGia(), {"type": "object"})
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"
    assert str(loi.value) == CauHinhKhongHopLe.thong_diep
