"""OCR-CR-8: cửa Admin Core đối chiếu lượt ABBYY; không gọi engine bên ngoài.

GET lấy pháp nhân từ query; POST dùng X-Phap-Nhan-Id của Core. Chốt bằng
CAS, không nhận băm hoặc danh tính người chốt từ trình duyệt.
"""
from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from . import dispatcher as d, mtq, phien
from .http import LoiHTTP, PhanHoi
from ..sdk_core.ngu_canh import _xoa_loi


TIEN_TO = '/api/v1/quan-tri/ocr/chua-ro'
_MA = '^ocr:[0-9a-f]{1,124}$'
_SO = {'type': 'integer', 'minimum': 1, 'maximum': 2**63 - 1}
_LOI = {
    400: ('OCR_ADMIN_DAU_VAO', 'Thông tin đối chiếu lượt nhận dạng chưa hợp lệ.'),
    401: ('OCR_ADMIN_PHIEN', 'Phiên đăng nhập đã hết. Cần đăng nhập lại.'),
    403: ('OCR_ADMIN_QUYEN', 'Không có quyền quản trị để đối chiếu lượt nhận dạng.'),
    404: ('OCR_ADMIN_KHONG_THAY', 'Không tìm thấy lượt nhận dạng cần đối chiếu.'),
    405: ('OCR_ADMIN_PHUONG_THUC', 'Thao tác đối chiếu chưa được hỗ trợ.'),
    409: ('OCR_ADMIN_XUNG_DOT', 'Lượt nhận dạng đã thay đổi hoặc còn đang xử lý. Cần tải lại danh sách.'),
    413: ('OCR_ADMIN_QUA_LON', 'Nội dung đối chiếu vượt dung lượng cho phép.'),
    415: ('OCR_ADMIN_DINH_DANG', 'Định dạng nội dung đối chiếu chưa được hỗ trợ.'),
    422: ('OCR_ADMIN_DAU_VAO', 'Thông tin đối chiếu lượt nhận dạng chưa hợp lệ.'),
    502: ('OCR_ADMIN_KET_QUA', 'Chưa xác nhận được kết quả đối chiếu lượt nhận dạng.'),
    503: ('OCR_ADMIN_CHUA_SAN_SANG', 'Chưa xử lý được yêu cầu đối chiếu. Cần kiểm tra lại trạng thái trước khi chốt.'),
}


def _loi(status, *, ghi_chu=False):
    status = status if status in _LOI else 503
    ma, thong_diep = _LOI[status]
    if ghi_chu and status in (400, 422):
        thong_diep = 'Cần ghi bằng chứng đối chiếu ABBYY.'
    return LoiHTTP(status, ma=ma, thong_diep=thong_diep)


def _object(fields, required=None):
    return dict(type='object', additionalProperties=False, properties=fields,
                required=list(fields) if required is None else required)


_CHOT_RA = _object(dict(ma_tuong_quan={'type': 'string', 'pattern': _MA},
    so_trang={'type': 'integer', 'minimum': 1, 'maximum': 2**31 - 1},
    trang_thai={'enum': ['DA_TIEU_TRANG', 'HOAN_TRANG']}, phien_ban=_SO))
_DONG = _object({**_CHOT_RA['properties'],
    'trang_thai': {'enum': ['CHUA_RO', 'DANG_GIU']},
    'giu_luc': {'type': 'string', 'pattern': r'^[0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}$'},
    'module': {'type': 'string', 'pattern': '^[a-z][a-z0-9_]{0,30}$'},
    'ma_bam_dau': {'type': 'string', 'pattern': '^[0-9a-f]{1,8}$'}})


class _RouteOCR(d.Route):
    @property
    def chong_trung(self):
        # CAS của biên nhận OCR là căn cứ chốt duy nhất; không ghi biên nhận thứ hai.
        return False


def routes_ocr_doi_chieu():
    return (
        _RouteOCR('GET', TIEN_TO, 'core', 'CORE.OCR.DOI_CHIEU.DANH_SACH',
            'CORE:ENGINE:XEM', {'type': 'null'},
            {200: _object(dict(danh_sach={'type': 'array', 'maxItems': 100, 'items': _DONG},
                               co_quyen_chot={'type': 'boolean'}))},
            lambda p, b: {}, query_schema=_object(dict(
                phap_nhan_id={'type': 'string', 'format': 'uuid'},
                gioi_han={'type': 'string', 'pattern': '^[1-9][0-9]{0,2}$'}), ['phap_nhan_id'])),
        _RouteOCR('POST', TIEN_TO + '/{ma}/chot', 'core', 'CORE.OCR.DOI_CHIEU.CHOT',
            'CORE:ENGINE:CAU_HINH', _object(dict(ket_qua={'enum': ['da_tieu', 'hoan_trang']},
                phien_ban={'type': 'integer', 'minimum': 1, 'maximum': 2**63 - 2},
                ghi_chu={'type': 'string', 'minLength': 1, 'maxLength': 500,
                         'pattern': r'\S'})), {200: _CHOT_RA}, lambda p, b: {},
            path_schema=_object(dict(ma={'type': 'string', 'pattern': _MA}))),
    )


def _dong(raw, *, danh_sach=False):
    if not isinstance(raw, Mapping):
        raise _loi(502)
    fields = _DONG['properties'] if danh_sach else _CHOT_RA['properties']
    try:
        result = {key: raw[key] for key in fields}
        if danh_sach:
            luc = result['giu_luc']
            if not isinstance(luc, str):
                raise ValueError()
            luc = datetime.fromisoformat(luc.replace('Z', '+00:00'))
            if luc.tzinfo is None:
                raise ValueError()
            result['giu_luc'] = luc.astimezone(timezone(timedelta(hours=7))).strftime('%d/%m/%Y %H:%M:%S')
        return result
    except (KeyError, TypeError, ValueError, OverflowError):
        raise _loi(502) from None


def _co_quyen_chot(core, conn, ma, context):
    """Chỉ công bố quyền đã xác minh tại máy chủ; POST vẫn kiểm lại đầy đủ."""
    identity = phien.xac_minh_phien(conn, ma=ma, module='core',
        phap_nhan_id=context.phap_nhan_id, hanh_dong='CORE:ENGINE:CAU_HINH')
    if (identity is None or identity.nguoi_dung_id != context.nguoi_dung_id
            or identity.module != 'core' or identity.phap_nhan_id != context.phap_nhan_id
            or identity.hanh_dong != 'CORE:ENGINE:CAU_HINH'
            or identity.viec_id is not None or identity.the_he is not None):
        return False
    chot = replace(context, operation='CORE.OCR.DOI_CHIEU.CHOT', hanh_dong='CORE:ENGINE:CAU_HINH')
    return core.quyen_he_thong is None or core.quyen_he_thong(conn, chot) is True


class _BienOCR:
    def __init__(self, bien, routes):
        self.bien, self.routes = bien, routes

    def __getattr__(self, name):
        return getattr(self.bien, name)

    def dispatch(self, request):
        if not (request.path == TIEN_TO or request.path.startswith(TIEN_TO + '/')):
            return self.bien.dispatch(request)
        status = 503
        note = request.body.get('ghi_chu') if isinstance(request.body, Mapping) else None
        ghi_chu_sai = request.method == 'POST' and (
            not isinstance(note, str) or not note.strip() or len(note) > 500)
        try:
            route, path = self.registry.tra(request.method, request.path)
            if route not in self.routes:
                raise _loi(404)
            if request.method == 'GET':
                pn = request.query.get('phap_nhan_id', '')
                try:
                    pn = str(UUID(pn))
                    header = request.headers.get('x-phap-nhan-id')
                    if header is not None and UUID(header) != UUID(pn):
                        raise ValueError()
                except (ValueError, TypeError, AttributeError):
                    raise _loi(400) from None
                request = replace(request, headers={**request.headers, 'x-phap-nhan-id': pn})
            context = self.core._context(request, route, path)
            limit = int(context.query.get('gioi_han', '25'))
            if not 1 <= limit <= 100:
                raise _loi(400)
            ma = request.phien.lay_ma('core', context.phap_nhan_id)
            if not isinstance(ma, phien.MaBiMat):
                raise _loi(401)
            with self.core.ket_noi() as conn:
                if conn.info.transaction_status != 0:
                    raise _loi(503)
                with conn.transaction():
                    identity = phien.xac_minh_phien(conn, ma=ma, module='core',
                        phap_nhan_id=context.phap_nhan_id, hanh_dong=route.hanh_dong)
                    if identity is None:
                        raise _loi(401)
                    if (identity.nguoi_dung_id != context.nguoi_dung_id or identity.module != 'core'
                            or identity.phap_nhan_id != context.phap_nhan_id
                            or identity.hanh_dong != route.hanh_dong
                            or identity.viec_id is not None or identity.the_he is not None):
                        raise _loi(403)
                    admin = conn.execute('SELECT loi.la_admin_bootstrap(%s)',
                        (context.nguoi_dung_id,)).fetchone()
                    if admin is None or admin[0] is not True:
                        raise _loi(403)
                    if self.core.quyen_he_thong is not None and self.core.quyen_he_thong(conn, context) is not True:
                        raise _loi(403)
                    mtq.dat_ngu_canh(conn, ma=ma, module='core', phap_nhan_id=context.phap_nhan_id,
                                     hanh_dong=route.hanh_dong)
                    if route.method == 'GET':
                        row = conn.execute('SELECT loi_tai_lieu.ocr_chua_ro_ds(%s,%s)',
                            (context.phap_nhan_id, limit)).fetchone()
                    else:
                        row = conn.execute('SELECT loi_tai_lieu.ocr_chua_ro_chot_admin(%s,%s,%s,%s,%s,%s)',
                            (context.phap_nhan_id, context.path['ma'], context.body['phien_ban'],
                             context.body['ket_qua'], context.body['ghi_chu'],
                             UUID(request.request_id))).fetchone()
                    raw = row[0] if row else None
                    if route.method == 'GET':
                        if not isinstance(raw, list) or len(raw) > limit:
                            raise _loi(502)
                        result = dict(danh_sach=[_dong(x, danh_sach=True) for x in raw],
                                      co_quyen_chot=_co_quyen_chot(self.core, conn, ma, context))
                    else:
                        result = _dong(raw)
                        expected = 'DA_TIEU_TRANG' if context.body['ket_qua'] == 'da_tieu' else 'HOAN_TRANG'
                        if (result['ma_tuong_quan'] != context.path['ma']
                                or result['phien_ban'] != context.body['phien_ban'] + 1
                                or result['trang_thai'] != expected):
                            raise _loi(502)
                    response = d._kiem_phan_hoi(route, PhanHoi(200, result), self.core.kiem, request.request_id)
                if conn.info.transaction_status != 0:
                    raise _loi(503)
            self.bien.kho.hoat_dong(request)
            return response
        except Exception as exc:
            status = exc.status if isinstance(exc, LoiHTTP) else {
                '42501': 403, '22023': 400, '40001': 409, '40P01': 409,
                '55P03': 409, '25000': 409}.get(getattr(exc, 'sqlstate', None), 503)
            _xoa_loi(exc)
        raise _loi(status, ghi_chu=ghi_chu_sai) from None


def dang_ky_ocr_doi_chieu(app):
    """Chỉ đăng ký; không mở kết nối khi dựng ứng dụng."""
    routes = routes_ocr_doi_chieu()
    bien = app.http.dispatcher
    for route in routes:
        bien.core.registry.dang_ky(route)
    app.http.dispatcher = _BienOCR(bien, routes)
    base = type(app.http)

    class HTTPOCR(base):
        def _nhan(self, env, request_id):
            path = env.get('PATH_INFO', '')
            if not (path == TIEN_TO or path.startswith(TIEN_TO + '/')):
                return super()._nhan(env, request_id)
            try:
                return super()._nhan(env, request_id)
            except LoiHTTP as exc:
                raise _loi(exc.status) from None

    app.http.__class__ = HTTPOCR
    return app
