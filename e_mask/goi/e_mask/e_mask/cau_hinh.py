"""Đọc cấu hình qua ngăn; bộ kiểm schema tối thiểu, không thư viện ngoài."""
from copy import deepcopy
import math
import re


def kiem_schema(gia_tri, schema, *, goc=None):
    goc = schema if goc is None else goc
    if '$ref' in schema:
        muc = goc
        for khoa in schema['$ref'].removeprefix('#/').split('/'):
            muc = muc[khoa]
        return kiem_schema(gia_tri, muc, goc=goc)
    if 'oneOf' in schema:
        dat = 0
        for nhanh in schema['oneOf']:
            try:
                kiem_schema(gia_tri, nhanh, goc=goc)
                dat += 1
            except ValueError:
                pass
        if dat != 1:
            raise ValueError('Dữ liệu chưa đúng cấu trúc.')
    kieu = schema.get('type')
    cac_kieu = kieu if isinstance(kieu, list) else [kieu]
    dung = {'object': type(gia_tri) is dict, 'array': type(gia_tri) is list,
            'string': isinstance(gia_tri, str), 'integer': type(gia_tri) is int,
            'number': type(gia_tri) in (int, float) and (type(gia_tri) is int or math.isfinite(gia_tri)),
            'boolean': type(gia_tri) is bool, 'null': gia_tri is None, None: True}
    if not any(dung.get(k, False) for k in cac_kieu):
        raise ValueError('Dữ liệu chưa đúng kiểu.')
    if 'const' in schema and (gia_tri != schema['const'] or type(gia_tri) is not type(schema['const'])):
        raise ValueError('Dữ liệu chưa đúng giá trị.')
    if 'enum' in schema and gia_tri not in schema['enum']:
        raise ValueError('Dữ liệu chưa đúng danh mục.')
    if isinstance(gia_tri, dict):
        thuoc_tinh = schema.get('properties', {})
        for khoa, muc in thuoc_tinh.items():
            if khoa not in gia_tri and 'default' in muc:
                gia_tri[khoa] = deepcopy(muc['default'])
        if any(k not in gia_tri for k in schema.get('required', [])):
            raise ValueError('Dữ liệu thiếu trường bắt buộc.')
        for khoa, muc in gia_tri.items():
            if khoa in thuoc_tinh:
                kiem_schema(muc, thuoc_tinh[khoa], goc=goc)
            elif schema.get('additionalProperties') is False:
                raise ValueError('Dữ liệu có trường chưa khai báo.')
    if isinstance(gia_tri, list):
        if len(gia_tri) < schema.get('minItems', 0) or len(gia_tri) > schema.get('maxItems', float('inf')):
            raise ValueError('Số mục chưa hợp lệ.')
        for muc in gia_tri:
            kiem_schema(muc, schema.get('items', {}), goc=goc)
    if isinstance(gia_tri, str):
        if len(gia_tri) < schema.get('minLength', 0) or len(gia_tri) > schema.get('maxLength', float('inf')):
            raise ValueError('Độ dài chưa hợp lệ.')
        if 'pattern' in schema and not re.search(schema['pattern'], gia_tri):
            raise ValueError('Dữ liệu chưa đúng mẫu.')
    if type(gia_tri) in (int, float):
        if gia_tri < schema.get('minimum', -float('inf')) or gia_tri > schema.get('maximum', float('inf')):
            raise ValueError('Số vượt giới hạn.')
        if gia_tri <= schema.get('exclusiveMinimum', -float('inf')):
            raise ValueError('Số vượt giới hạn.')
    return gia_tri


def doc_cau_hinh(ngan, schema):
    muc = ngan.doc('cau_hinh', {'ma': 'cau_hinh'})
    if muc is None:
        return None
    return kiem_schema(deepcopy(muc.gia_tri['gia_tri']), schema)
