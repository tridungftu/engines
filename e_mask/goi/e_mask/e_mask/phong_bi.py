"""Phong bì văn bản: kiểm ngữ nghĩa trước xử lý, không tin cờ an toàn caller."""
from copy import deepcopy
from hashlib import sha256
import json
import math
import re
from pathlib import Path

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .che_van_ban import _kiem_dinh_danh, LoiCheVanBan
from .nguon.privacy.types import PrivacyError, bo_ky_tu_vo_hinh, chuan_hoa_vi_tri, la_ky_tu_vo_hinh


# Bộ kiểm loại riêng thuộc engine; không phụ thuộc helper riêng của NGAN-0.
def _kiem_schema(gia_tri, schema, *, goc=None):
    goc = schema if goc is None else goc
    if '$ref' in schema:
        muc = goc
        for khoa in schema['$ref'].removeprefix('#/').split('/'):
            muc = muc[khoa]
        return _kiem_schema(gia_tri, muc, goc=goc)
    if 'oneOf' in schema:
        dat = 0
        for nhanh in schema['oneOf']:
            try:
                _kiem_schema(gia_tri, nhanh, goc=goc)
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
                _kiem_schema(muc, thuoc_tinh[khoa], goc=goc)
            elif schema.get('additionalProperties') is False:
                raise ValueError('Dữ liệu có trường chưa khai báo.')
    if isinstance(gia_tri, list):
        if len(gia_tri) < schema.get('minItems', 0) or len(gia_tri) > schema.get('maxItems', float('inf')):
            raise ValueError('Số mục chưa hợp lệ.')
        for muc in gia_tri:
            _kiem_schema(muc, schema.get('items', {}), goc=goc)
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



def loi(ma='MASK_DAU_VAO'):
    cau = {'MASK_DAU_VAO': 'Nội dung yêu cầu chưa hợp lệ.',
           'MASK_QUA_GIOI_HAN': 'Nội dung vượt giới hạn cho phép. Cần chia nhỏ yêu cầu.',
           'MASK_MA_YEU_CAU': 'Không xác minh được quyền mở che cho yêu cầu này.'}
    return LoiNghiepVu(ma, cau[ma])


def json_chu(gia_tri):
    try:
        return json.dumps(gia_tri, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise loi() from None


def kiem_chuyen_tiep(gia_tri):
    if not isinstance(gia_tri, dict):
        raise loi()
    try:
        if len(json_chu(gia_tri).encode('utf-8')) > 65536:
            raise loi('MASK_QUA_GIOI_HAN')
    except UnicodeError:
        raise loi() from None


def kiem_van_ban(chu, *, cho_rong=False, cho_dinh_dang=False, gioi_han=500000):
    if not isinstance(chu, str) or not cho_rong and not chu.strip():
        raise loi()
    try:
        chu.encode('utf-8')
    except UnicodeError:
        raise loi() from None
    if not cho_dinh_dang and any(la_ky_tu_vo_hinh(c) for c in chu):
        raise LoiNghiepVu('MASK_DAU_VAO', 'Văn bản còn ký tự định dạng vô hình. Cần kiểm tra lại trước khi gửi.') from None
    if not cho_rong and not bo_ky_tu_vo_hinh(chu).strip():
        raise loi()
    if gioi_han is not None and len(chu) > gioi_han:
        raise loi('MASK_QUA_GIOI_HAN')
    if cho_dinh_dang:
        try:
            chuan_hoa_vi_tri(chu)
        except PrivacyError:
            raise LoiNghiepVu('MASK_DAU_VAO', 'Không thể xác định vị trí ký tự an toàn. Cần kiểm tra lại văn bản.') from None


def _cap(cac_cap):
    kq = {}
    for k, v in cac_cap:
        if k in kq:
            raise ValueError
        kq[k] = v
    return kq


def _doc_json(viec):
    tep = viec.dau_vao.get('tep')
    if not isinstance(tep, dict) or tep.get('mime') != 'application/json':
        raise loi()
    try:
        with viec.mo_tep(tep['tep_id']) as f:
            raw = f.read(4 * 1024 * 1024 + 1)
        if len(raw) > 4 * 1024 * 1024:
            raise loi('MASK_QUA_GIOI_HAN')
        def cam(hang):
            raise ValueError
        kq = json.loads(raw.decode('utf-8'), object_pairs_hook=_cap, parse_constant=cam)
        if not isinstance(kq, dict):
            raise ValueError
        return kq
    except (KeyError, ValueError, TypeError, UnicodeError, RecursionError):
        raise loi() from None


def kiem_loai(dau, ma):
    try:
        if not isinstance(dau, dict) or set(dau) != {'loai', ma} or dau['loai'] != ma:
            raise ValueError
        schema = json.loads((Path(__file__).parent / 'schemas' / (ma + '.schema.json')).read_text('utf-8'))
        _kiem_schema(deepcopy(dau), schema)
        json_chu(dau).encode('utf-8')
        if 'chuyen_tiep' in dau[ma]:
            kiem_chuyen_tiep(dau[ma]['chuyen_tiep'])
        if ma == 'van_ban_da_che':
            kiem_van_ban(dau[ma]['van_ban'], gioi_han=None)
    except (ValueError, TypeError, KeyError, RecursionError, UnicodeError):
        raise loi() from None
    return deepcopy(dau[ma])


def doc_che(viec):
    dau = viec.dau_vao
    loai = dau.get('loai')
    ds = []
    if loai == 'van_ban':
        if set(dau) != {'loai', 'van_ban'}:
            raise loi()
        chu = dau['van_ban']
    elif loai == 'van_ban_tai_lieu':
        chu = kiem_loai(dau, loai)['van_ban']
    elif loai == 'tep':
        muc = _doc_json(viec)
        if set(muc) - {'van_ban', 'dinh_danh_da_biet'}:
            raise loi()
        chu, ds = muc.get('van_ban'), muc.get('dinh_danh_da_biet', [])
    else:
        raise loi()
    kiem_van_ban(chu, cho_dinh_dang=True)
    if isinstance(ds, (list, tuple)):
        if len(ds) > 500:
            raise loi('MASK_QUA_GIOI_HAN')
        for muc in ds:
            if not isinstance(muc, dict) or set(muc) - {'gia_tri', 'nhom'}:
                raise loi()
            if any(isinstance(muc.get(k), str) and len(muc[k]) > n for k, n in [('gia_tri', 300), ('nhom', 20)]):
                raise loi('MASK_QUA_GIOI_HAN')
    try:
        _kiem_dinh_danh(ds, la_khai_bao=True)
    except LoiCheVanBan:
        raise loi() from None
    return chu, ds


def cac_chu(gia_tri, duong=()):
    if isinstance(gia_tri, str):
        yield duong, gia_tri
    elif isinstance(gia_tri, dict):
        for k, v in gia_tri.items():
            yield from cac_chu(v, duong + (k,))
    elif isinstance(gia_tri, list):
        for i, v in enumerate(gia_tri):
            yield from cac_chu(v, duong + (i,))


def doc_mo(viec):
    dau, ai = viec.dau_vao, None
    dong = viec.tham_so.get('dong_viec', False)
    if dau.get('loai') == 'tep':
        muc = _doc_json(viec)
        if set(muc) - {'van_ban', 'ma_yeu_cau', 'dong_viec'}:
            raise loi()
        ma, chu = muc.get('ma_yeu_cau'), muc.get('van_ban')
        dong = muc.get('dong_viec', dong)
        kiem_van_ban(chu, cho_rong=True)
    elif dau.get('loai') == 'tra_loi_ai':
        ai = kiem_loai(dau, 'tra_loi_ai')
        kiem_chuyen_tiep(ai['chuyen_tiep'])
        ma, chu = ai['chuyen_tiep'].get('ma_yeu_cau'), ai['tra_loi']
        chuoi = [chu] + [c for _, c in cac_chu(ai['du_lieu'])] + [m['cau'] for m in ai['trich_dan']]
        for c in chuoi:
            kiem_van_ban(c, cho_rong=True)
        if sum(map(len, chuoi)) > 500000:
            raise loi('MASK_QUA_GIOI_HAN')
    else:
        raise loi()
    if not isinstance(ma, str) or not ma:
        raise loi('MASK_MA_YEU_CAU')
    if type(dong) is not bool:
        raise loi()
    return chu, ma, dong, ai


def ket_qua_che(kq, chu):
    # Dùng danh sách trường cho phép; không chép metadata nguồn/OCR/nhật ký kho.
    muc = dict(phien_ban=1, van_ban=kq['van_ban_da_che'], ma_yeu_cau=kq['ma_yeu_cau'],
               con_sot=kq['con_sot'], kiem_tien_ngay=kq['kiem_tien_ngay'], chuyen_tiep={},
               so_cho_thay=kq['so_cho_thay'], bi_danh=kq['bi_danh'], cho_duyet=kq['cho_duyet'],
               vung_da_quet=['than_van_ban'], phien_ban_engine='e_mask 1.0.0',
               bam_dau_vao='sha256:' + sha256(chu.encode('utf-8')).hexdigest(), canh_bao=kq['canh_bao'])
    dau = {'loai': 'van_ban_da_che', 'van_ban_da_che': muc}
    kiem_loai(dau, 'van_ban_da_che')
    return dau


def ket_qua_mo(kq, ai):
    return {'loai': 'truong', 'truong': {
        'van_ban_da_mo_che': kq['van_ban_da_mo_che'], 'so_cho_mo': kq['so_cho_mo'],
        'bi_danh_khong_ro_json': json_chu(kq['bi_danh_khong_ro']), 'mo_day_du': kq['mo_day_du'],
        'trang_thai_ma_yeu_cau': kq['trang_thai_ma_yeu_cau'],
        'tra_loi_ai_da_mo_json': json_chu(ai) if ai is not None else None}}
