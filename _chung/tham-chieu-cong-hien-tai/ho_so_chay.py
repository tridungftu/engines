"""EM-CFG-1: hồ sơ hệ thống, caller giữ transaction; chưa nối HTTP.

Schema/manifest chỉ được bộ cài Core đã kiểm gói truyền vào dang_ky_goi.
Mapping ket_ref do két Core đăng ký sau khi xác minh mục két; module này
không đọc két, không nhận giá trị két, không khởi động lại engine.
Origin/CSRF/cookie thuộc HTTP; mã phiên ở đây là mã nội bộ G2-03.
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import wraps
import hashlib
import json
import re
from uuid import UUID

from . import goi
from .phien import _ma
from .tiep_nhan import _tx
from ..sdk_core.ngu_canh import _xoa_loi


_CU = {'row_version', 'ho_so_mau_id', 'cho_khoi_dong_giay',
       'ranh_toi_da_giay', 'che_do_chay'}
_MOI = {'phien_ban_engine', 'ma_bam_schema', 'cau_hinh'}
_MA = r'[a-z][a-z0-9_]{0,30}'
_TEN = r'[a-z][a-z0-9_]{0,63}'
_BI_MAT = re.compile(
    r'(^|[^a-z0-9_])(?:sk-[a-z0-9_-]{8,}|AKIA[A-Z0-9]{16}|ghp_[a-z0-9_]+|xoxb-[a-z0-9-]+|AIza[a-z0-9_-]+)|'
    r'-----BEGIN .*PRIVATE KEY-----|(^|[^a-z0-9_])Bearer\s+\S+|'
    r'(?:password|passwd|mat_khau|api[_-]?key|access_token|client_secret)\s*[:=]|'
    r'[a-z][a-z0-9+.-]*://[^/\s]*@|'
    r'(^|[^a-z0-9_])(?:postgres(?:ql)?://|host\s*=)', re.I)
_TEN_BI_MAT = re.compile(
    # Tên đếm token là metadata; tên bí mật khớp theo đoạn, không khớp khoang_cach.
    r'^(?!so_token_toi_da$)(?:[a-z0-9]*_)*(?:password|passwd|mat_khau|matkhau|'
    r'secret|token|api_key|apikey|private_key|privatekey|credential|dsn|khoa|'
    r'bi_mat|mat_ma|pwd|passphrase|cookie|authorization)(?:_|$)', re.I)
_THAM_CHIEU = {'type': 'object', 'additionalProperties': False,
              'x-bi-mat': True, 'required': ['ket_ref'],
              'properties': {'ket_ref': {'type': 'string', 'format': 'uuid'}}}
_LOI = {
    'HO_SO_CHAY_DAU_VAO': 422, 'PHIEN_BAN_DU_LIEU_KHONG_HO_TRO': 422,
    'CAU_HINH_CHUA_KHAI_BAO': 422, 'CAU_HINH_SCHEMA_KHONG_HOP_LE': 422,
    'CAU_HINH_KHONG_HOP_LE': 422, 'THAM_CHIEU_KET_KHONG_HOP_LE': 422,
    'CAU_HINH_SCHEMA_DA_DOI': 409, 'XUNG_DOT_PHIEN_BAN': 409,
    'KHOA_CHONG_TRUNG_KHAC_NOI_DUNG': 409, 'KHOA_CHONG_TRUNG_HET_HAN': 409,
    'HO_SO_CHAY_CHI_ADMIN': 403, 'HO_SO_CHAY_CHI_CORE': 403,
    'HO_SO_CHAY_CHI_CAI_DAT': 403, 'HO_SO_CHAY_KHONG_THAY': 404,
    'HO_SO_CHAY_THAT_BAI': 503,
}


class LoiHoSoChay(RuntimeError):
    def __init__(self, ma='HO_SO_CHAY_THAT_BAI'):
        self.ma = ma if ma in _LOI else 'HO_SO_CHAY_THAT_BAI'
        self.http_status = _LOI[self.ma]
        super().__init__(self.ma)


def _an_loi(ham):
    @wraps(ham)
    def goi_an(*args, **kwargs):
        ma = 'HO_SO_CHAY_THAT_BAI'
        try:
            return ham(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, LoiHoSoChay):
                ma = exc.ma
            else:
                chinh = getattr(getattr(exc, 'diag', None), 'message_primary', None)
                if isinstance(chinh, str) and chinh in _LOI:
                    ma = chinh
            _xoa_loi(exc)
        finally:
            args = kwargs = chinh = None
        raise LoiHoSoChay(ma) from None
    return goi_an


def _sai(ma='HO_SO_CHAY_DAU_VAO'):
    raise LoiHoSoChay(ma)


def _json(value):
    # Không ép kiểu, không default=str; NaN/Infinity/khóa không chuỗi bị từ chối.
    def kiem(v, sau=0):
        if sau > 64:
            _sai()
        if type(v) is dict:
            if any(type(k) is not str for k in v):
                _sai()
            for x in v.values():
                kiem(x, sau+1)
        elif type(v) is list:
            for x in v:
                kiem(x, sau+1)
        elif v is not None and type(v) not in (str, int, float, bool):
            _sai()
    kiem(value)
    try:
        raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False)
        if len(raw.encode('utf-8')) > 1048576:
            _sai()
        return raw
    except (ValueError, TypeError, UnicodeError):
        _sai()


def _uuid(value):
    if type(value) is not str or not re.fullmatch(
            r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', value):
        _sai()
    return str(UUID(value))


def _ban(value):
    if (type(value) is not str or not re.fullmatch(r'[1-9][0-9]{0,18}', value)
            or int(value) > 2**63-1):
        _sai()
    return value


def _chon(value):
    if value not in (None, '1.2'):
        _sai('PHIEN_BAN_DU_LIEU_KHONG_HO_TRO')
    return value == '1.2'


def _ma_engine(value):
    if type(value) is not str or not re.fullmatch(_MA, value):
        _sai()
    return value


def _goi(conn, ham, ts):
    _tx(conn)
    row = conn.execute('SELECT loi.' + ham + '(' + ','.join(['%s'] * len(ts)) + ') AS r', ts).fetchone()
    return row['r'] if isinstance(row, Mapping) else row[0]


def _quet(value):
    """Kiểm bổ sung, không coi heuristic là bảo đảm nhận diện mọi bí mật."""
    if isinstance(value, str) and _BI_MAT.search(value):
        _sai('CAU_HINH_KHONG_HOP_LE')
    if isinstance(value, dict):
        for key, child in value.items():
            _quet(key)
            _quet(child)
    elif isinstance(value, list):
        for child in value:
            _quet(child)


def _nut_schema(schema):
    """Duyệt vị trí schema, không nhầm dữ liệu enum/default là schema."""
    if type(schema) not in (dict, bool):
        _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
    if type(schema) is not dict:
        yield schema
        return
    for key in ('$defs', 'definitions', 'properties', 'patternProperties', 'dependentSchemas'):
        if key in schema and type(schema[key]) is not dict:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
    for key in ('allOf', 'anyOf', 'oneOf', 'prefixItems'):
        if key in schema and type(schema[key]) is not list:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
    yield schema
    for child in goi._schema_children(schema):
        yield from _nut_schema(child)


def _kiem_schema(schema):
    _json(schema)
    _quet(schema)
    if (type(schema) is not dict or schema.get('$schema') != goi.DRAFT
            or schema.get('type') != 'object' or schema.get('additionalProperties') is not False):
        _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
    pending, seen, nodes = [schema], set(), []
    while pending:
        for node in _nut_schema(pending.pop()):
            if id(node) in seen:
                continue
            seen.add(id(node))
            nodes.append(node)
            resolved = _giai_schema(schema, node)
            if resolved is not node:
                pending.append(resolved)
    for node in nodes:
        if type(node) is not dict:
            if node is not False:
                _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
            continue
        for key in ('$ref', '$dynamicRef'):
            if key in node and (type(node[key]) is not str or not node[key].startswith('#/')):
                _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        # Không cho đổi base URI trong inline schema hoặc giấu trường trong pattern.
        if any(k in node for k in ('$id', '$dynamicAnchor', 'patternProperties')):
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        # Mỗi vị trí phải có kiểu rõ hoặc tham chiếu nội bộ đã giải được.
        # Không cho {} / true / schema chỉ có enum mở đường nhận object tự do.
        resolved = _giai_schema(schema, node)
        types = node.get('type', [])
        if isinstance(types, str):
            types = [types]
        if (type(types) is not list or any(type(t) is not str for t in types)):
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        if not types and resolved is node:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        if ('object' in types or 'properties' in node) and node.get('additionalProperties') is not False:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        if 'object' in types and not node.get('properties'):
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        if 'array' in types and 'items' not in node:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        if 'x-bi-mat' in node:
            core = {k: v for k, v in node.items() if k not in {'title', 'description', '$comment'}}
            if node['x-bi-mat'] is not True or core != _THAM_CHIEU:
                _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        for key, child in node.get('properties', {}).items():
            if (not re.fullmatch(_TEN, key, re.I)
                    or key.lower() == 'ket_ref' and node.get('x-bi-mat') is not True
                    or key.lower() in {'shell', 'command', 'lenh_shell', 'executable'}
                    or _TEN_BI_MAT.search(key) and not _la_tham_chieu(_giai_schema(schema, child))):
                _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
    # Dùng đúng validator 2020-12/offline của bộ kiểm gói; thiếu thì đóng cổng.
    Validator, checker, registry, _ = goi._bo_schema()
    try:
        Validator.check_schema(schema)
    except Exception:
        _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
    validator = Validator(schema, format_checker=checker, registry=registry)
    return validator


def _la_tham_chieu(node):
    return type(node) is dict and {
        k: v for k, v in node.items() if k not in {'title', 'description', '$comment'}
    } == _THAM_CHIEU


def _giai_schema(root, node):
    for _ in range(65):
        if type(node) is not dict or not any(k in node for k in ('$ref', '$dynamicRef')):
            return node
        refs = [k for k in ('$ref', '$dynamicRef') if k in node]
        if len(refs) != 1 or set(node) - {refs[0], 'title', 'description', '$comment'}:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        ref = node[refs[0]]
        if type(ref) is not str or not ref.startswith('#/') or '%' in ref:
            _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
        node = root
        for part in ref[2:].split('/'):
            part = part.replace('~1', '/').replace('~0', '~')
            if type(node) is not dict or part not in node:
                _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')
            node = node[part]
    _sai('CAU_HINH_SCHEMA_KHONG_HOP_LE')


@_an_loi
def kiem_schema(schema):
    """Cửa kiểm bổ sung cho bộ cài; trả hash, không sửa manifest/SDK hiện tại."""
    _kiem_schema(schema)
    return hashlib.sha256(_json(schema).encode('utf-8')).hexdigest()


def _kiem_cau_hinh(schema, cau_hinh):
    if type(cau_hinh) is not dict:
        _sai('CAU_HINH_KHONG_HOP_LE')
    _json(cau_hinh)
    _quet(cau_hinh)
    validator = _kiem_schema(schema)
    try:
        if next(validator.iter_errors(cau_hinh), None) is not None:
            _sai('CAU_HINH_KHONG_HOP_LE')
    except Exception:
        _sai('CAU_HINH_KHONG_HOP_LE')
    # Chỉ x-bi-mat mới chứa ket_ref; cấm khóa bí mật rõ cả ở nhánh lồng sâu.
    def kiem(v):
        if type(v) is dict:
            if 'ket_ref' in v:
                if set(v) != {'ket_ref'}:
                    _sai('THAM_CHIEU_KET_KHONG_HOP_LE')
                _uuid(v['ket_ref'])
            for key, child in v.items():
                if _TEN_BI_MAT.search(key):
                    if type(child) is not dict or set(child) != {'ket_ref'}:
                        _sai('THAM_CHIEU_KET_KHONG_HOP_LE')
                    _uuid(child['ket_ref'])
                kiem(child)
        elif type(v) is list:
            for child in v:
                kiem(child)
    kiem(cau_hinh)


def _ho_so(data, moi):
    _json(data)
    if type(data) is not dict or set(data) != (_CU | _MOI if moi else _CU):
        _sai()
    _ban(data['row_version'])
    _uuid(data['ho_so_mau_id'])
    for key, low, high in [('cho_khoi_dong_giay', 1, 120), ('ranh_toi_da_giay', 60, 86400)]:
        if type(data[key]) is not int or not low <= data[key] <= high:
            _sai()
    if data['che_do_chay'] not in ('tu_kich_hoat_tu_dong', 'giu_lau_hon', 'luon_chay'):
        _sai()
    if moi and (type(data['phien_ban_engine']) is not str or not 1 <= len(data['phien_ban_engine']) <= 64
                or type(data['ma_bam_schema']) is not str or not re.fullmatch('[0-9a-f]{64}', data['ma_bam_schema'])):
        _sai()
    return data


@_an_loi
def dang_ky_goi(conn, manifest, ho_so_mau_id, *, cau_hinh=None):
    """Bộ cài truyền manifest đã kiểm và cấu hình đầu tiên; không tự điền {}.

    Gói mới thiếu schema vẫn được đăng ký với NULL. Cùng phiên bản không
    được đổi schema. Bản nâng cấp tạo phiên bản cấu hình mới ghim schema/engine
    mới dưới khóa transaction SQL; tăng row_version cho CAS, giữ lịch sử cũ.
    """
    _json(manifest)
    _quet(manifest)
    ma = _ma_engine(manifest['ma'])
    version = manifest['phien_ban']
    if type(version) is not str or not 1 <= len(version) <= 64:
        _sai()
    schema = manifest.get('cau_hinh_schema')
    if 'cau_hinh_schema' in manifest:
        digest = kiem_schema(schema)
        _kiem_cau_hinh(schema, cau_hinh)
    else:
        digest = None
        if cau_hinh is not None:
            _sai('CAU_HINH_CHUA_KHAI_BAO')
    return _goi(conn, 'ho_so_chay_dang_ky', (ma, version, _uuid(ho_so_mau_id),
        _json(schema) if schema is not None else None, digest,
        _json(cau_hinh) if cau_hinh is not None else None))


@_an_loi
def dang_ky_ket(conn, ma_engine, ket_ref, *, hoat_dong=True):
    """Chỉ Core két gọi sau khi xác minh tồn tại; không tạo/đọc bí mật."""
    if type(hoat_dong) is not bool:
        _sai()
    return _goi(conn, 'ho_so_chay_gan_ket', (_ma_engine(ma_engine), _uuid(ket_ref), hoat_dong))


@_an_loi
def doc_schema(conn, ma_engine, *, ma):
    return _goi(conn, 'ho_so_chay_doc_schema', (_ma_engine(ma_engine), _ma(ma)))


@_an_loi
def doc(conn, ma_engine, *, ma, phien_ban_du_lieu=None, row_version=None):
    moi = _chon(phien_ban_du_lieu)
    if row_version is not None:
        _ban(row_version)
    return _goi(conn, 'ho_so_chay_doc', (_ma_engine(ma_engine), _ma(ma), moi, row_version))


@_an_loi
def ghi(conn, ma_engine, du_lieu, *, ma, request_id, khoa_chong_trung, phien_ban_du_lieu=None):
    moi = _chon(phien_ban_du_lieu)
    name = _ma_engine(ma_engine)
    _ho_so(du_lieu, moi)
    if type(khoa_chong_trung) is not str or not re.fullmatch(r'[A-Za-z0-9._:-]{16,128}', khoa_chong_trung):
        _sai()
    token = _ma(ma)
    raw = _json(du_lieu)
    # Kiểm quyền trước phát lại; schema đổi sau kết quả cũ không phá idempotency.
    replay = _goi(conn, 'ho_so_chay_phat_lai', (name, token, moi, raw, khoa_chong_trung))
    if replay is not None:
        return replay
    if moi:
        # Cửa SQL kiểm quyền trước khi trả metadata; SQL ghi kiểm lại dưới khóa.
        pinned = doc_schema(conn, name, ma=ma)
        if (du_lieu['phien_ban_engine'], du_lieu['ma_bam_schema']) != (
                pinned['phien_ban_engine'], pinned['ma_bam_schema']):
            _sai('CAU_HINH_SCHEMA_DA_DOI')
        _kiem_cau_hinh(pinned['cau_hinh_schema'], du_lieu['cau_hinh'])
    return _goi(conn, 'ho_so_chay_ghi', (name, token, moi, raw,
        _uuid(str(request_id)), khoa_chong_trung))


@_an_loi
def bootstrap(conn, ma_engine, row_version):
    """Core ghim bản cho kênh bootstrap/stdin G2-21; chỉ tham chiếu, không két.

    Caller dùng kênh pipe đã bảo vệ. Không gửi cấu hình vào args/env/log.
    """
    return _goi(conn, 'ho_so_chay_bootstrap', (_ma_engine(ma_engine), _ban(row_version)))
