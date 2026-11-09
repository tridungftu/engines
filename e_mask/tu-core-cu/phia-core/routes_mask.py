"""MASK-3H: cửa Admin chạy thử DEMO qua hàng việc Core, mặc định tắt.

Composition tiêm DichVuChayThuMask; không mở CSDL, engine hay kho riêng.
chuan_bi(conn, *, loai, du_lieu, nguoi_dung_id, phap_nhan_id, chu_phien,
khoa_dedupe, nguon_goc) tạo tài liệu/nguồn trong cùng transaction, trả
NguonChayThuMask đã ghim. Mở che phải dùng lại tài liệu của nguon_goc.
Toàn văn chỉ đi vào kho đầu vào có kiểm quyền của provider này, tuyệt đối
không vào metadata hàng việc, biên nhận, audit hay lỗi. Provider không commit.
doc_ket_qua(conn, *, viec_id, nguon, ma, nguoi_dung_id, phap_nhan_id,
chu_phien) đọc việc/kết quả qua cửa Core có kiểm quyền; trả {trang_thai,
ket_qua}, ket_qua là DTO mask_chot_ra_noi_bo.v1 hoặc None khi chưa xong.

Sổ sở hữu chỉ giữ ID/nguồn, không giữ nội dung; cùng vòng đời kho phiên WSGI
một tiến trình. Khởi động lại đóng quyền đọc việc cũ, không suy chủ từ actor.
"""
from dataclasses import dataclass, replace
from datetime import timedelta
import hashlib
import hmac
import re
import secrets
from threading import RLock
from uuid import UUID

from . import dispatcher as d, phien
from .dich_vu_engine import DichVuEngine
from .http import GIOI_HAN_JSON, LoiHTTP, PhanHoi


TIEN_TO = '/api/v1/quan-tri/engine/e_mask/chay-thu'
_ID = {'type': 'string', 'format': 'uuid'}
_VAN_BAN = {'type': 'string', 'minLength': 1, 'maxLength': 500_000}
_RA = 'urn:ktt:contract:mask_chot_ra_noi_bo.v1'
_TRANG_THAI = ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'cancel_requested')
_LOI = {
    400: ('MASK_THU_YEU_CAU', 'Yêu cầu chạy thử chưa hợp lệ.'),
    401: ('MASK_THU_PHIEN', 'Phiên đăng nhập đã hết. Đăng nhập lại để tiếp tục.'),
    403: ('MASK_THU_QUYEN', 'Không có quyền chạy thử hoặc đọc kết quả này.'),
    404: ('MASK_THU_KHONG_THAY', 'Không tìm thấy việc chạy thử trong phiên hiện tại.'),
    409: ('MASK_THU_XUNG_DOT', 'Yêu cầu đang được xử lý. Thử lại sau.'),
    413: ('MASK_THU_QUA_LON', 'Văn bản vượt dung lượng cho phép. Cần rút ngắn nội dung.'),
    415: ('MASK_THU_NOI_DUNG', 'Định dạng nội dung chạy thử chưa được hỗ trợ.'),
    422: ('MASK_THU_DAU_VAO', 'Nội dung chạy thử chưa hợp lệ hoặc vượt giới hạn cho phép.'),
    429: ('MASK_THU_HAN_MUC', 'Đã đạt giới hạn chạy thử. Thử lại sau.'),
    502: ('MASK_THU_KET_QUA', 'Chưa xác nhận được kết quả chạy thử. Thử lại sau.'),
    503: ('MASK_THU_CHUA_SAN_SANG', 'Chưa xử lý được yêu cầu chạy thử. Thử lại sau.'),
}


def _loi(status):
    code, message = _LOI.get(status, _LOI[503])
    return LoiHTTP(status if status in _LOI else 503, ma=code, thong_diep=message)


def _object(fields):
    return {'type': 'object', 'additionalProperties': False,
            'required': list(fields), 'properties': fields}


@dataclass(frozen=True, repr=False)
class NguonChayThuMask:
    module: str
    hanh_dong: str
    capability: str
    loai_viec: str
    phien_ban: int
    tai_lieu_id: UUID
    bang_tham_chieu: str
    tham_chieu_id: UUID


@dataclass(frozen=True, repr=False)
class DichVuChayThuMask:
    engine: DichVuEngine
    chuan_bi: object
    doc_ket_qua: object

    def __post_init__(self):
        if (not isinstance(self.engine, DichVuEngine)
                or not callable(self.chuan_bi) or not callable(self.doc_ket_qua)):
            raise ValueError('Cần dịch vụ chạy thử do Core cấp.')


@dataclass(frozen=True, repr=False)
class _Viec:
    id: str
    chu_phien: str
    nguoi_dung_id: UUID
    phap_nhan_id: UUID
    loai: str
    nguon: NguonChayThuMask
    het_han: object
    khoa: str
    yeu_cau_id: str | None = None


def routes_mask():
    che = _object(dict(van_ban=_VAN_BAN, dinh_danh_da_biet={
        'type': 'array', 'maxItems': 500, 'items': _object(dict(
            gia_tri={'type': 'string', 'minLength': 2, 'maxLength': 300},
            nhom={'type': 'string', 'minLength': 1, 'maxLength': 20}))}))
    mo = _object(dict(ma_yeu_cau=_ID, van_ban_co_bi_danh=_VAN_BAN,
                      dong_viec={'type': 'boolean'}))
    accepted = _object(dict(viec_id=_ID, trang_thai={'const': 'queued'}, request_id=_ID))
    result = _object(dict(viec_id=_ID, trang_thai={'enum': list(_TRANG_THAI)},
        ket_qua={'oneOf': [{'type': 'null'}, {'$ref': _RA}]}, request_id=_ID))
    def handler(conn, context):
        raise _loi(503)  # Biên riêng giữ toàn văn ngoài biên nhận chung.
    return tuple(d.Route(method, TIEN_TO + suffix, 'core', 'CORE.MASK.THU.' + operation,
        'CORE:ENGINE:XEM', schema, {status: out}, lambda p, b: {}, handler=handler,
        viec_lau=method == 'POST', path_schema=_object(path))
        for method, suffix, operation, schema, status, out, path in (
            ('POST', '/che-van-ban', 'CHE', che, 202, accepted, {}),
            ('POST', '/mo-che-van-ban', 'MO_CHE', mo, 202, accepted, {}),
            ('GET', '/{viec_id}', 'DOC', {'type': 'null'}, 200, result, {'viec_id': _ID})))


class _BienMask:
    def __init__(self, bien, service, clock, routes):
        self.bien, self.service, self.clock = bien, service, clock
        self.routes = routes
        self._bi_mat, self._khoa = secrets.token_bytes(32), RLock()
        self._viec = {}

    def __getattr__(self, name):
        return getattr(self.bien, name)

    def _bam(self, *parts):
        # Chỉ danh tính phiên/ID/khóa HTTP, không băm toàn văn hay cụm gốc.
        return hmac.new(self._bi_mat, d._json(parts), hashlib.sha256).hexdigest()

    def _kiem_admin_demo(self, conn, request, context):
        ma = request.phien.lay_ma('core', context.phap_nhan_id)
        self._xac_minh(conn, ma, context, 'core', 'CORE:ENGINE:XEM')
        admin = conn.execute('SELECT loi.la_admin_bootstrap(%s)',
                             (context.nguoi_dung_id,)).fetchone()
        if (admin is None or admin[0] is not True
                or (self.core.quyen_he_thong is not None
                    and self.core.quyen_he_thong(conn, context) is not True)):
            raise _loi(403)
        # Cửa 047 xác minh phiên/thành viên và đọc la_demo phía Core; không
        # SELECT bảng riêng, không tin cờ DEMO từ browser hay tên pháp nhân.
        after = (None, None)
        while True:
            rows = conn.execute('SELECT id, ten, la_demo, nguoi_dung_id '
                'FROM loi.phap_nhan_cua_toi(%s,%s,%s,%s)',
                (ma.lay_de_truyen(), 100, *after)).fetchall()
            for pn, _, demo, actor in rows:
                if actor != context.nguoi_dung_id:
                    raise _loi(403)
                if pn == context.phap_nhan_id:
                    if demo is not True:
                        raise _loi(403)
                    return
            if len(rows) <= 100:
                raise _loi(403)
            key = (rows[99][1], rows[99][0])
            if key == after:
                raise _loi(503)
            after = key

    @staticmethod
    def _xac_minh(conn, ma, context, module, action):
        if not isinstance(ma, phien.MaBiMat):
            raise _loi(401)
        identity = phien.xac_minh_phien(conn, ma=ma, module=module,
            phap_nhan_id=context.phap_nhan_id, hanh_dong=action)
        if identity is None:
            raise _loi(401)
        if (identity.nguoi_dung_id != context.nguoi_dung_id or identity.module != module
                or identity.phap_nhan_id != context.phap_nhan_id or identity.hanh_dong != action
                or identity.viec_id is not None or identity.the_he is not None):
            raise _loi(403)

    def _kiem_nguon(self, source, original):
        if (not isinstance(source, NguonChayThuMask)
                or not isinstance(source.module, str) or source.module == 'core'
                or not re.fullmatch('[a-z][a-z0-9_]{0,30}', source.module)
                or not isinstance(source.hanh_dong, str)
                or not re.fullmatch(re.escape(source.module.upper()) + r':[A-Z0-9_]+:(LAP|SUA|DUYET)',
                                    source.hanh_dong)
                or type(source.phien_ban) is not int or source.phien_ban < 1
                or not isinstance(source.tai_lieu_id, UUID)
                or not isinstance(source.tham_chieu_id, UUID)
                or not isinstance(source.bang_tham_chieu, str)
                or not re.fullmatch('[a-z][a-z0-9_]{0,79}', source.bang_tham_chieu)):
            raise _loi(503)
        pin = self.service.engine._ghim.get(source.capability)
        binding = self.service.engine._loai_viec.get((source.module, source.loai_viec, source.phien_ban))
        if (pin is None or pin.ma_engine != 'e_mask' or binding is None
                or binding.capability != source.capability
                or (original is not None and (source.module, source.tai_lieu_id)
                    != (original.module, original.tai_lieu_id))):
            raise _loi(503)

    def _quyen_nguon(self, conn, request, context, source, *, doc=False):
        ma = request.phien.lay_ma(source.module, context.phap_nhan_id)
        action = source.hanh_dong.rsplit(':', 1)[0] + ':XEM' if doc else source.hanh_dong
        self._xac_minh(conn, ma, context, source.module, action)
        decision = d.mtq.quyet_dinh_phien(conn, ma=ma, module=source.module,
            phap_nhan_id=context.phap_nhan_id, hanh_dong=action,
            doi_tuong={'bang': source.bang_tham_chieu, 'id': str(source.tham_chieu_id)},
            phien_ban_contract='1')
        if decision.get('ket_luan') != 'DAT' or decision.get('cho_phep') is not True:
            raise _loi(503 if decision.get('ket_luan') == 'CHO' else 403)
        return dict(ma=ma, module=source.module, phap_nhan_id=context.phap_nhan_id,
                    hanh_dong=action)

    def dispatch(self, request):
        try:
            route, path = self.registry.tra(request.method, request.path)
        except LoiHTTP as exc:
            if exc.status not in {404, 405}:
                raise
            return self.bien.dispatch(request)
        if route not in self.routes:
            return self.bien.dispatch(request)
        failed = False
        try:
            context = self.core._context(request, route, path)
            from .ung_dung import _KhoPhien
            owner = self._bam(_KhoPhien._tim(request))
            with self._khoa:
                now = self.clock()
                self._viec = {id_: v for id_, v in self._viec.items() if v.het_han > now}
                with self.core.ket_noi() as conn:
                    if conn.info.transaction_status != 0:
                        raise _loi(503)
                    with conn.transaction():
                        self._kiem_admin_demo(conn, request, context)
                        if self.service is None:
                            raise LoiHTTP(503, ma='MASK_THU_CHUA_BAT',
                                thong_diep='Chức năng chạy thử chưa được bật')
                        if route.method == 'POST':
                            response, record = self._gui(conn, request, route, context, owner, now)
                        else:
                            response, record = self._doc(conn, request, route, context, owner)
                        response = d._kiem_phan_hoi(route, response, self.core.kiem, request.request_id)
                        if response.status == 202:
                            response = replace(response, headers={**response.headers,
                                'Location': TIEN_TO + '/' + record.id})
                    if conn.info.transaction_status != 0:
                        raise _loi(503)
                # Chỉ công bố sổ sở hữu sau commit gốc thành công.
                self._viec[record.id] = record
            self.bien.kho.hoat_dong(request)
            return response
        except LoiHTTP as exc:
            # Mã lỗi provider cũng là dữ liệu không tin cậy; không chuyển
            # tiếp thông điệp ngay cả khi trùng prefix/mã lỗi của route.
            if self.service is None and exc.ma == 'MASK_THU_CHUA_BAT':
                raise LoiHTTP(503, ma='MASK_THU_CHUA_BAT',
                    thong_diep='Chức năng chạy thử chưa được bật') from None
            raise _loi(exc.status) from None
        except Exception:
            failed = True
        # Ngoài except: không giữ lỗi provider/driver có toàn văn trong chain.
        if failed:
            raise _loi(503)

    def _gui(self, conn, request, route, context, owner, now):
        # Parser HTTP vẫn giữ 1 MiB; kiểm lại bytes trước provider/kênh.
        if len(d._json(context.body)) > GIOI_HAN_JSON:
            raise _loi(413)
        text = context.body.get('van_ban', context.body.get('van_ban_co_bi_danh', ''))
        if not text.strip():
            raise _loi(422)
        kind = 'che' if route.operation.endswith('.CHE') else 'mo_che'
        key = 'mask-http:' + self._bam(owner, str(context.phap_nhan_id),
                                     context.operation, context.khoa)
        previous = next((v for v in self._viec.values() if v.khoa == key), None)
        if previous is not None:
            self._quyen_nguon(conn, request, context, previous.nguon)
            return self._da_nhan(previous.id, request.request_id), previous
        if len(self._viec) >= 4096:
            raise _loi(429)
        original = None
        if kind == 'mo_che':
            original = next((v.nguon for v in self._viec.values()
                if v.chu_phien == owner and v.nguoi_dung_id == context.nguoi_dung_id
                and v.phap_nhan_id == context.phap_nhan_id and v.loai == 'che'
                and v.yeu_cau_id == context.body['ma_yeu_cau']), None)
            if original is None:
                raise _loi(403)
            self._quyen_nguon(conn, request, context, original, doc=True)
        source = self.service.chuan_bi(conn, loai=kind, du_lieu=context.body,
            nguoi_dung_id=context.nguoi_dung_id, phap_nhan_id=context.phap_nhan_id,
            chu_phien=owner, khoa_dedupe=key, nguon_goc=original)
        self._kiem_nguon(source, original)
        ctx = self._quyen_nguon(conn, request, context, source)
        # Cùng cửa với cong_sdk._engine/engine.gui_viec; không tự tạo queue.
        id_ = str(UUID(str(self.service.engine.gui_viec(conn, source.capability,
            loai=source.loai_viec, phien_ban=source.phien_ban, khoa_dedupe=key,
            bang_tham_chieu=source.bang_tham_chieu, tham_chieu_id=source.tham_chieu_id, **ctx))))
        if id_ in self._viec:
            raise _loi(503)
        record = _Viec(id_, owner, context.nguoi_dung_id, context.phap_nhan_id,
            kind, source, now + timedelta(hours=8), key,
            context.body.get('ma_yeu_cau') if kind == 'mo_che' else None)
        return self._da_nhan(id_, request.request_id), record

    @staticmethod
    def _da_nhan(id_, request_id):
        return PhanHoi(202, dict(viec_id=id_, trang_thai='queued', request_id=request_id))

    def _doc(self, conn, request, route, context, owner):
        record = self._viec.get(str(UUID(context.path['viec_id'])))
        if record is None:
            raise _loi(404)
        if (record.chu_phien != owner or record.nguoi_dung_id != context.nguoi_dung_id
                or record.phap_nhan_id != context.phap_nhan_id):
            raise _loi(403)
        ctx = self._quyen_nguon(conn, request, context, record.nguon, doc=True)
        value = self.service.doc_ket_qua(conn, viec_id=UUID(record.id), nguon=record.nguon,
            ma=ctx['ma'], nguoi_dung_id=context.nguoi_dung_id,
            phap_nhan_id=context.phap_nhan_id, chu_phien=owner)
        if (type(value) is not dict or value.keys() != {'trang_thai', 'ket_qua'}
                or value['trang_thai'] not in _TRANG_THAI):
            raise _loi(502)
        result = value['ket_qua']
        if value['trang_thai'] == 'succeeded':
            schema = {'$ref': _RA + '#/$defs/' + record.loai}
            if not self.core.kiem.kiem(schema, result):
                raise _loi(502)
            if record.loai == 'che':
                # Kiểm điều kiện chặn cả khi test validator chỉ hỗ trợ subset.
                if ((result['gui_duoc'] and (result['con_sot'] or not result['kiem_tien_ngay']))
                        or (not result['gui_duoc'] and result['van_ban_da_che'] is not None)):
                    raise _loi(502)
                record = replace(record, yeu_cau_id=result['ma_yeu_cau'])
            elif (result['ma_yeu_cau'] != record.yeu_cau_id
                    or result['mo_day_du'] != (not result['bi_danh_khong_ro'])):
                raise _loi(502)
        elif result is not None:
            # Việc lỗi/chưa xong không được phản chiếu thông báo hoặc nội dung.
            raise _loi(502)
        return PhanHoi(200, dict(viec_id=record.id, **value,
                                request_id=request.request_id)), record


def dang_ky_mask(app, *, dich_vu=None):
    """Ghép như dang_ky_quan_tri; mặc định vẫn có route, fail closed 503."""
    if dich_vu is not None and not isinstance(dich_vu, DichVuChayThuMask):
        raise ValueError('Cần dịch vụ chạy thử do Core cấp.')
    routes = routes_mask()
    bien = app.http.dispatcher
    for route in routes:
        bien.core.registry.dang_ky(route)
    app.http.dispatcher = _BienMask(bien, dich_vu, app.http.dong_ho, routes)
    base = type(app.http)

    class HTTPMask(base):
        def _nhan(self, env, request_id):
            if not env.get('PATH_INFO', '').startswith(TIEN_TO + '/'):
                return super()._nhan(env, request_id)
            try:
                request = super()._nhan(env, request_id)
            except LoiHTTP as exc:
                status = exc.status
                if status == 403 and self._phien(env.get('HTTP_COOKIE', '')) is None:
                    status = 401
                raise _loi(status) from None
            if (request.phien is None or request.phien.tien_phien
                    or request.phien.nguoi_dung_id is None):
                raise _loi(401)
            # GET cũng cần CSRF: kết quả mở che chứa thông tin định danh.
            if not secrets.compare_digest(request.headers.get('x-csrf-token', '').encode('utf-8'),
                                           request.phien.csrf.lay_de_truyen().encode('utf-8')):
                raise _loi(403)
            return request

    app.http.__class__ = HTTPMask
    return app
