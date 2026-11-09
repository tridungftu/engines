"""Kênh kéo SDKEngine, trên socket/credential bootstrap đã cấp, không mở listener.

KenhCore chỉ giữ transport. WorkerEngine giữ provider Core; không trao provider,
kết nối DB hoặc kho tệp cho engine. Composition root cấp binding đã ghim và cửa
kiểm instance (epoch/PID/lần tạo/thế hệ); thiếu provider thì không mở kênh.
"""
from __future__ import annotations

from contextlib import contextmanager, ExitStack
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import hmac
import io
import json
import re
import secrets
import socket
import struct
import tempfile
import threading
import time
from uuid import UUID, uuid4

from ..sdk_core import kenh_khung as k
from ..sdk_core.engine import KenhCore as KenhTruuTuong, SDKEngine, LoiEngine
from ..sdk_core.ngu_canh import _xoa_loi
from . import viec, phien, tai_lieu
from .ket_qua import KhoTepEngine, _thong_tin_luong, _LuongDaKiem


CUA_SO_CHUNK = 4
OPERATION_MASK = frozenset({'mask.snapshot', 'mask.chot_luot'})
# tra_loi_ai.v2 giữ lý do chi tiết trong tệp nội dung, không khai enum cho metadata.
# Dùng cùng tập mã đóng tại cửa đầu vào và trước ACK; None là chưa có lý do.
_LY_DO_METADATA_HOI_AI = frozenset({
    'uu_tien', 'co_dinh', 'khong_thay_can_cu', 'loi_local',
    *(f'du_phong:{i}' for i in range(1, 10))})


_FUNCTION_CACHE = {}
_FUNCTION_LOCK = threading.RLock()


def doc_function_chay_thu_hoi_ai(conn):
    """Metadata theo thế hệ gói đã cài; lỗi một mục không đóng cả danh sách."""
    from copy import deepcopy
    import logging
    from . import dang_ky, ho_so_module
    from .van_ban_an_toan import la_van_ban_mo_ta_an_toan
    rows = [r for r in dang_ky.doc_dang_ky(conn, loai='phien_ban_module')
            if r['module'] != 'core' and r['trang_thai'] == 'da_cai']
    generation = json.dumps(sorted(rows, key=lambda r: (r['module'], r['so_phien_ban'])),
                            sort_keys=True, default=str)
    # Tách CSDL; id/thời điểm/thế hệ cài lại nằm trong snapshot registry.
    info = getattr(conn, 'info', None)
    scope = tuple(getattr(info, name, None) for name in ('host', 'port', 'dbname', 'user'))
    scope = scope if isinstance(scope[2], str) and all(type(x) in (str, int, type(None)) for x in scope) else id(conn)
    key = (scope, generation)
    with _FUNCTION_LOCK:
        if key in _FUNCTION_CACHE:
            return deepcopy(_FUNCTION_CACHE[key])
    result, seen, duplicate = {}, set(), set()
    logger = logging.getLogger(__name__)
    for row in rows:
        module, version, digest = row['module'], row['so_phien_ban'], row['ma_bam_goi']
        try:
            data = conn.execute('SELECT loi.cd060_doc_runtime_hien_hanh(%s,%s)',
                                (module, digest)).fetchone()
            data = next(iter(data.values())) if isinstance(data, dict) else data[0]
            _, package = ho_so_module._doc_goi_da_cai(data, module=module, phien_ban=version, bam=digest)
        except Exception as exc:
            _xoa_loi(exc)
            logger.warning('AI_THU_GOI_BO_QUA')
            continue
        for entry in package.manifest.get('ham_hoi_ai', []):
            try:
                function_key = module, entry['ma_function']
                if function_key in seen:
                    duplicate.add(function_key)
                    result.pop(function_key, None)
                    raise ValueError('Chức năng trùng khai báo.')
                seen.add(function_key)
                prompt = package.cac_tep[entry['tep_prompt']].decode('utf-8')
                if not prompt.strip():
                    raise ValueError('Thiếu hướng dẫn.')
                label, module_label = entry.get('mo_ta', ''), package.manifest.get('ten', '')
                result[function_key] = dict(ma_module=module, ma_function=entry['ma_function'],
                    ten_module=module_label if la_van_ban_mo_ta_an_toan(module_label, 255) else 'Nghiệp vụ đã cài',
                    ten_function=label if la_van_ban_mo_ta_an_toan(label, 255) else 'Chức năng hỏi đáp',
                    ma_prompt=entry['ma_prompt'], phien_ban_prompt=str(entry['phien_ban_prompt']),
                    phien_ban_module=version, ma_bam_goi=digest)
            except Exception as exc:
                _xoa_loi(exc)
                logger.warning('AI_THU_FUNCTION_BO_QUA')
    values = [result[key] for key in sorted(result) if key not in duplicate][:1000]
    with _FUNCTION_LOCK:
        if len(_FUNCTION_CACHE) >= 16:
            _FUNCTION_CACHE.pop(next(iter(_FUNCTION_CACHE)))
        _FUNCTION_CACHE[key] = deepcopy(values)
    return values


class _TuChoiNhanViec(k.LoiKenh):
    """Từ chối trước cấp lease; phản hồi xong vẫn dùng được kênh."""


class _XungDotLuotMask(k.LoiKenh):
    """Lượt Mask chưa chốt; giữ lease/kênh để lấy snapshot mới hoặc kết thúc."""


class _DocStream(io.RawIOBase):
    """Reader SDK: giữ tối đa một chunk, ACK theo tốc độ caller đọc.

    Bỏ dở stream đóng kênh để frame cũ không lọt sang call tiếp theo.
    """
    def __init__(self, kenh, h, descriptor, han):
        self.kenh, self.h, self.d, self.han = kenh, h, descriptor, han
        self.dem = k.BoDemStream(descriptor, gioi_han=kenh._limit)
        self.pending, self.xong = b'', False

    def readable(self):
        return True

    def _ket_thuc(self, f):
        k._can(f.header['kieu'] == 'end' and
               f.header['stream_id'] == self.d['stream_id'] and
               f.header['kich_thuoc_byte'] == self.dem.tong_byte)
        self.dem.ket_thuc()
        self.xong = True
        self.kenh._stream = None

    def readinto(self, target):
        self._checkClosed()
        if not target:
            return 0
        with self.kenh._lock:
            try:
                while not self.pending and not self.xong:
                    f = self.kenh._nhan(self.h, self.han)
                    if f.header['kieu'] == 'end':
                        self._ket_thuc(f)
                        return 0
                    k._can(f.header['kieu'] == 'chunk')
                    self.dem.nhan_chunk(f.header['stream_id'], f.header['thu_tu_chunk'], f.than)
                    self.pending = f.than
                    if ((f.header['thu_tu_chunk']+1) % CUA_SO_CHUNK == 0 or
                            self.dem.tong_byte == self.d['kich_thuoc_byte']):
                        self.kenh._wire.gui(_control('ack_chunk', self.h,
                            stream_id=f.header['stream_id'], thu_tu_chunk=f.header['thu_tu_chunk']), b'', self.han)
                    if self.dem.tong_byte == self.d['kich_thuoc_byte']:
                        self._ket_thuc(self.kenh._nhan(self.h, self.han))
                n = min(len(target), len(self.pending))
                target[:n], self.pending = self.pending[:n], self.pending[n:]
                return n
            except Exception as exc:
                ma = 'VIEC_MAT_LEASE' if getattr(exc, 'ma', None) in (
                    'MAT_LEASE', 'VIEC_MAT_LEASE') else 'ENGINE_CORE'
                self.pending = b''
                self.kenh.dong()
                _xoa_loi(exc)
                raise LoiEngine(ma) from None

    def close(self):
        if not self.closed and not self.xong:
            self.pending = b''
            self.kenh.dong()
        super().close()


def _control(kieu, h, raw=b'', **them):
    return dict(protocol=k.PROTOCOL, phien_ban=k.PHIEN_BAN, kieu=kieu,
        chieu=h['chieu'], request_id=h['request_id'], call_id=h['call_id'],
        hash_than=hashlib.sha256(raw).hexdigest(), **them)


def _doc(sock, n, han, cho=None):
    raw = bytearray()
    while len(raw) < n:
        con = han-time.monotonic()
        k._can(con > 0, 'PHAN_HOI_QUA_HAN')
        sock.settimeout(min(.25 if cho is not None else 15, con))
        try:
            chunk = sock.recv(n-len(raw))
        except TimeoutError:
            if cho is None:
                raise
            cho()
            continue
        if not chunk:
            raise EOFError()
        if not raw:
            han = min(han, time.monotonic()+30)
        raw.extend(chunk)
    return bytes(raw)


class _Socket:
    def __init__(self, sock, proof):
        self.sock, self.proof = sock, proof

    def gui(self, h, raw, han):
        con = han-time.monotonic()
        k._can(con > 0, 'PHAN_HOI_QUA_HAN')
        self.sock.settimeout(min(15, con))
        self.sock.sendall(k.ma_hoa_frame(h, raw, self.proof))

    def nhan(self, han, kiem=None, cho=None):
        cho_frame = han is None
        han = float('inf') if cho_frame else han
        con = han-time.monotonic()
        k._can(con > 0, 'PHAN_HOI_QUA_HAN')
        self.sock.settimeout(min(15, con))
        raw = bytearray()
        for index, limit in enumerate((k.GIOI_HAN_HEADER, k.GIOI_HAN_JSON, k.GIOI_HAN_PROOF)):
            prefix = _doc(self.sock, 4, han, cho=cho if index == 0 else None)
            if cho_frame and index == 0:
                han = time.monotonic()+30
            n = struct.unpack('!I', prefix)[0]
            k._can(n <= limit, 'VUOT_GIOI_HAN_KICH_THUOC')
            raw.extend(prefix)
            raw.extend(_doc(self.sock, n, han))
        return k.giai_ma_frame(bytes(raw), self.proof, kiem_the=kiem)

    def dong(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()


def _giu_json(g):
    return {**{key: str(getattr(g, key)) for key in (
        'viec_id', 'buoc_viec_id', 'lan_thu_id', 'phap_nhan_id', 'instance_id')},
        'module': g.module, 'hanh_dong': g.hanh_dong, 'the_he': g.the_he,
        'giu_den': g.giu_den.isoformat(), 'ma': g.ma.lay_de_truyen()}


def _giu_doc(data, ma=None):
    k._dong(data, {'viec_id', 'buoc_viec_id', 'lan_thu_id', 'phap_nhan_id',
        'instance_id', 'module', 'hanh_dong', 'the_he', 'giu_den', 'ma'})
    return viec.GiuViec(*(UUID(data[key]) for key in (
        'viec_id', 'buoc_viec_id', 'lan_thu_id', 'phap_nhan_id')),
        data['module'], data['hanh_dong'], UUID(data['instance_id']), data['the_he'],
        datetime.fromisoformat(data['giu_den']), ma or phien.MaBiMat(data['ma']))


class KenhCore(KenhTruuTuong):
    """Đầu engine: một call/socket; bootstrap có thể cấp nhiều socket hữu hạn.

    Không nhận callback nghiệp vụ/SQL, không import provider từ SDK. Toàn bộ
    thông tin ngu_canh đến từ bootstrap; Core ký thẻ trước từng request.
    """
    __slots__ = ('_wire', '_kiem', '_binding', '_lock', '_ready', '_dong', '_limit', '_stream')

    def __init__(self, sock, *, proof, kiem_the, ngu_canh, gioi_han=k.GIOI_HAN_TEP):
        k._can(isinstance(kiem_the, k.BoKiemThe) and 0 < gioi_han <= k.GIOI_HAN_TEP)
        self._wire, self._kiem = _Socket(sock, proof), kiem_the
        self._binding, self._lock = dict(ngu_canh), threading.Lock()
        self._ready = self._dong = False
        self._limit = gioi_han
        self._stream = None

    def dong(self):
        self._dong = True
        self._wire.dong()

    def nhan_viec(self):
        data = self.goi('nhan_viec', None)
        return None if data is None else _giu_doc(data)

    def cap_sdk(self):
        giu = self.nhan_viec()
        return None if giu is None else SDKEngine(giu, kenh_core=self)

    def ket_thuc(self, giu_viec, *, trang_thai='XONG', ket_qua_id=None, ma_loi=None):
        return self.goi('ket_thuc', giu_viec, trang_thai=trang_thai,
            ket_qua_id=None if ket_qua_id is None else str(ket_qua_id), ma_loi=ma_loi)

    def goi(self, operation, giu_viec, **payload):
        ma = 'ENGINE_CORE'
        loi_nhan = None
        try:
            with self._lock, ExitStack() as stack:
                return self._goi(operation, giu_viec, payload, stack)
        except Exception as exc:
            if isinstance(exc, _TuChoiNhanViec):
                loi_nhan = LoiEngine(exc.ma)
                loi_nhan.http_status = exc.http_status
                loi_nhan.thu_lai_duoc, loi_nhan.retry_after = exc.thu_lai_duoc, exc.retry_after
            elif getattr(exc, 'ma', None) in ('MAT_LEASE', 'VIEC_MAT_LEASE'):
                ma = 'VIEC_MAT_LEASE'
            elif operation in OPERATION_MASK and getattr(exc, 'ma', None) == 'XUNG_DOT':
                loi_nhan = LoiEngine('MASK_XUNG_DOT_LUOT')
                loi_nhan.http_status = exc.http_status
                loi_nhan.thu_lai_duoc, loi_nhan.retry_after = True, None
            elif operation in k.OPERATION_OCR_GHI | k.OPERATION_OCR_DOC:
                code = getattr(exc, 'ma', None)
                if code in k.MA_LOI_HTTP:
                    ma = code
            _xoa_loi(exc)
        finally:
            payload = giu_viec = None
        if loi_nhan is not None:
            raise loi_nhan from None
        self.dong()
        raise LoiEngine(ma) from None

    def goi_mask(self, operation, giu_viec, **payload):
        """G tiêm callable gắn với lease; không truyền provider/DB cho engine."""
        ten = {'snapshot_luot': 'mask.snapshot', 'chot_luot': 'mask.chot_luot'}
        try:
            if not isinstance(operation, str) or operation not in ten:
                raise LoiEngine('ENGINE_CORE')
            return self.goi(ten[operation], giu_viec, **payload)
        finally:
            payload = giu_viec = None

    def _goi(self, operation, giu, payload, stack):
        # Operation kho chỉ nằm trong envelope nội bộ. Dùng carrier SDK đã có,
        # không sửa whitelist/proof, không mở RPC kho cho module hay nâng SDK.
        la_mask = operation in OPERATION_MASK
        if la_mask:
            payload = {'mask': {'operation': operation, 'du_lieu': payload}}
            operation = 'doc_dau_vao'
        la_ocr = operation in k.OPERATION_OCR_GHI | k.OPERATION_OCR_DOC
        khoa = payload.pop('khoa', None) if la_ocr else None
        if la_ocr:
            payload = k.kiem_dto_ocr(operation, payload)
            k._can((khoa is not None) == (operation in k.OPERATION_OCR_GHI))
        op = operation if la_ocr else 'engine.' + operation
        k._can(not self._dong and self._stream is None and op in k.OPERATION_ENGINE)
        k._can((giu is None) == (operation == 'nhan_viec'))
        han = time.monotonic()+30
        if not self._ready:
            f = self._wire.nhan(han)
            k._can(f.header['kieu'] == 'challenge' and f.than == b'')
            self._wire.gui(_control('xac_thuc', {**f.header, 'chieu': 'con_den_core'}), b'', han)
            self._ready = True
        descriptor, content = None, None
        if operation == 'ghi_ket_qua':
            content = stack.enter_context(tempfile.TemporaryFile())
            info = _thong_tin_luong(payload.pop('luong'), self._limit, dich=content)
            descriptor = dict(stream_id=str(uuid4()), **info, ten=payload['ten'])
        if operation == 'mo_doc':
            payload['tep_id'] = str(payload['tep_id'])
        raw = k._json(payload)
        u = dict(loai='INSTANCE', ma='instance', viec_id=None, the_he_lease=None)
        if giu is not None:
            u = dict(loai='UY_NHIEM_VIEC', ma=giu.ma.lay_de_truyen(),
                     viec_id=str(giu.viec_id), the_he_lease=giu.the_he)
            payload = {**payload, 'lan_thu_id': str(giu.lan_thu_id)}
            raw = k._json(payload)
        h = dict(self._binding, protocol=k.PROTOCOL, phien_ban=k.PHIEN_BAN,
            kieu='request', chieu='con_den_core', operation=op,
            request_id=str(uuid4()), call_id=str(uuid4()), parent_call_id=None,
            thu_tu_con=None, module_nguon=self._binding['module'], uy_nhiem=u,
            khoa=khoa, deadline=datetime.fromtimestamp(time.time()+30, timezone.utc).isoformat(),
            stream=descriptor, hash_than=hashlib.sha256(raw).hexdigest(), http=None)
        prep = k._json(h)
        self._wire.gui(_control('chuan_bi', h, prep), prep, han)
        cap = self._nhan(h, han)
        k._can(cap.header['kieu'] == 'cap_the')
        signed = k._doc_json(cap.than)
        self._kiem.kiem(signed)
        k._can({key: val for key, val in signed.items() if key != 'the_ky'} == h)
        self._wire.gui(signed, raw, han)
        if descriptor is not None:
            self._gui_stream(h, descriptor, content, han)
        try:
            f = self._nhan(h, han)
        except k.LoiKenh as exc:
            if operation == 'nhan_viec' and exc.ma in (
                    'CHUA_SAN_SANG', 'YEU_CAU_KHONG_HOP_LE'):
                raise _TuChoiNhanViec(exc.ma, retry_after=exc.retry_after) from None
            raise
        k._can(f.header['kieu'] == 'response')
        if la_mask or la_ocr or operation in ('nhan_viec', 'heartbeat', 'ghi_ket_qua', 'ket_thuc'):
            k._can(f.header['da_commit'] is True, 'PHAN_HOI_SAI_CONTRACT')
        if f.header['stream'] is not None:
            k._can(operation == 'mo_doc')
            self._stream = _DocStream(self, h, f.header['stream'], han)
            return io.BufferedReader(self._stream, buffer_size=k.GIOI_HAN_CHUNK)
        envelope = k._doc_json(f.than)
        k._dong(envelope, {'ket_qua'})
        data = envelope['ket_qua']
        if operation == 'heartbeat':
            return _giu_doc(data, ma=giu.ma)
        return data

    def _nhan(self, h, han):
        f = self._wire.nhan(han)
        k._can((f.header['request_id'], f.header['call_id']) ==
               (h['request_id'], h['call_id']))
        if f.header['kieu'] == 'response':
            k._can(f.header['operation'] == h['operation'])
            if f.header['status'] >= 400:
                raise k.LoiKenh(f.header['loi']['ma'],
                    retry_after=f.header.get('retry_after'))
        return f

    def _gui_stream(self, h, d, content, han):
        def gui(header, raw):
            try:
                self._wire.gui(header, raw, han)
            except OSError:
                # Core có thể đã gửi lỗi rồi đóng khi từ chối lease trước chunk.
                # Đọc response có proof/call_id đúng trước khi bọc lỗi gửi socket.
                self._nhan(h, han)
                raise

        dem = k.BoDemStream(d, gioi_han=self._limit)
        i = 0
        while dem.tong_byte < d['kich_thuoc_byte']:
            chunk = content.read(k.GIOI_HAN_CHUNK)
            k._can(bool(chunk))
            dem.nhan_chunk(d['stream_id'], i, chunk)
            gui(_control('chunk', h, chunk, stream_id=d['stream_id'],
                thu_tu_chunk=i, kich_thuoc_byte=len(chunk)), chunk)
            if (i+1) % CUA_SO_CHUNK == 0 or dem.tong_byte == d['kich_thuoc_byte']:
                ack = self._nhan(h, han)
                k._can(ack.header == _control('ack_chunk', {**h, 'chieu': 'core_den_con'},
                    stream_id=d['stream_id'], thu_tu_chunk=i) and ack.than == b'')
            i += 1
        dem.ket_thuc()
        gui(_control('end', h, stream_id=d['stream_id'],
            kich_thuoc_byte=dem.tong_byte), b'')


@dataclass(frozen=True, repr=False)
class DauVaoMask:
    """Mã ổn định Core gắn với việc, tách khỏi dữ liệu do engine gửi."""
    ma_yeu_cau: UUID
    ma_luot: UUID
    loai: str

    def __post_init__(self):
        k._can(isinstance(self.ma_yeu_cau, UUID) and isinstance(self.ma_luot, UUID)
            and self.loai in ('che', 'mo_che'))


@dataclass(frozen=True, repr=False)
class DauVaoEngine:
    """Provider Core chọn theo việc/registry; không dựng từ payload engine."""
    tai_lieu_id: UUID
    tep: tuple
    du_lieu: dict
    het_han_luc: str | None = None
    mask: DauVaoMask | None = None


class HangViecCore:
    """Adapter hàng việc thật. Các hàm nhận tx; không tự commit.

    Composition root cấp cả ghim_loai_viec và dich_vu_engine cho việc E2.
    Provider giữ binding Core, kiểm lại readiness/instance mỗi lần kéo; không
    nhận capability/contract từ payload engine và không lùi sang cửa legacy.
    Bỏ cả hai chỉ dành cho việc cũ có binding NULL.
    """
    def __init__(self, *, ctx, dau_vao, kho_tep=None, ban_giao=None,
                 ghim_loai_viec=None, dich_vu_engine=None):
        k._can(callable(dau_vao) and (kho_tep is not None or ban_giao is not None))
        if ghim_loai_viec is not None or dich_vu_engine is not None:
            from .dich_vu_engine import DichVuEngine
            g = ghim_loai_viec
            k._can(isinstance(g, viec.GhimLoaiViec)
                and isinstance(dich_vu_engine, DichVuEngine)
                and ctx.get('module') == g.module
                and dich_vu_engine._loai_viec.get((g.module, g.loai, g.phien_ban)) == g,
                'KENH_KHONG_DU_QUYEN')
        self._ghim, self._dich_vu = ghim_loai_viec, dich_vu_engine
        self.ctx, self._input = dict(ctx), dau_vao
        if ban_giao is None:
            from .ket_qua import BanGiaoKetQua
            ban_giao = BanGiaoKetQua(kho_tep, xac_minh_core=self.nguon, cua_engine_069=True)
        self.ban_giao = ban_giao

    def nguon(self, conn, giu):
        from .ket_qua import NguonCore
        data = viec._goi(conn,
            'SELECT loi.nguon_lease_engine(%s,%s,%s,%s,%s,%s,%s,%s) AS r',
            (*viec._giu(conn, giu), giu.lan_thu_id))
        return NguonCore(giu.module, giu.phap_nhan_id, data['phien_ban_module'],
            UUID(data['engine_id']), data['ham'], data['phien_ban_ham'], giu.viec_id,
            giu.the_he, UUID(data['buoc_id']), UUID(data['lan_thu_id']))

    def nhan(self, conn, instance):
        if self._ghim is not None:
            g = self._ghim
            from .dich_vu_engine import LoiDichVuEngine
            try:
                return self._dich_vu.nhan_viec(conn, g.capability, loai=g.loai,
                    phien_ban=g.phien_ban, instance_id=instance, **self.ctx)
            except LoiDichVuEngine as exc:
                if exc.ma == 'ENGINE_CHUA_SAN_SANG':
                    loi = _TuChoiNhanViec('CHUA_SAN_SANG', retry_after=2)
                elif exc.ma == 'ENGINE_LOAI_VIEC_KHONG_KHOP':
                    loi = _TuChoiNhanViec('YEU_CAU_KHONG_HOP_LE')
                else:
                    raise
                _xoa_loi(exc)
            raise loi from None
        ma = phien.MaBiMat(secrets.token_urlsafe(32))
        args = viec._ctx(conn, self.ctx)
        data = viec._goi(conn, 'SELECT loi.nhan_viec_engine(%s,%s,%s,%s,%s,%s,%s) AS r',
            (*args, instance, ma.lay_de_truyen(), 120))
        return None if data is None else _giu_doc({**data, 'ma': ma.lay_de_truyen()}, ma)

    def kiem(self, conn, giu):
        state = viec.trang_thai_lease(conn, giu)
        k._can(state['con_giu'] is True and str(state['lan_thu_id']) == str(giu.lan_thu_id), 'MAT_LEASE')
        if self.la_chay_thu_hoi_ai():
            viec._goi(conn, 'SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s) AS r',
                (giu.ma.lay_de_truyen(), giu.phap_nhan_id, giu.viec_id, giu.instance_id, giu.the_he))
        else:
            self.nguon(conn, giu)

    def la_chay_thu_hoi_ai(self):
        g = self._ghim
        return g is not None and (g.module, g.loai, g.phien_ban, g.capability,
            g.ma_contract, g.phien_ban_contract) == (
                'core', 'CHAY_THU_HOI_AI', 1, 'ai.hoi@1', 'tra_loi_ai.v2', '2.0.0')

    def dau_vao(self, conn, giu):
        if self.la_chay_thu_hoi_ai():
            data = self._dich_vu.nguon_hoi_ai(conn, ghim=self._ghim, giu=giu,
                dau_vao=None, phien_ban_module=None)
            return DauVaoEngine(UUID(data['nguon_core']['vi_tri']['tep_id']), (), data)
        result = self._input(conn, giu)
        k._can(isinstance(result, DauVaoEngine))
        if self._ghim is not None and self._ghim.capability == 'ai.hoi@1':
            nguon = self.nguon(conn, giu)
            data = self._dich_vu.nguon_hoi_ai(conn, ghim=self._ghim, giu=giu,
                dau_vao=result.du_lieu, phien_ban_module=nguon.phien_ban_module)
            result = replace(result, du_lieu=data)
        return result

    gia_han = staticmethod(viec.gia_han)

    def ket_thuc(self, conn, giu, trang_thai='XONG', *, ket_qua_id=None, ma_loi=None):
        if not self.la_chay_thu_hoi_ai():
            return viec.ket_thuc(conn, giu, trang_thai, ket_qua_id=ket_qua_id, ma_loi=ma_loi)
        k._can(trang_thai == 'LOI' and ket_qua_id is None, 'KENH_KHONG_DU_QUYEN')
        return self.ghi_chay_thu(conn, giu, 'loi', dict(tra_loi='', model='', ly_do_chon='',
            loi=dict(thong_diep_viet='Chưa thực hiện được lượt chạy thử. Có thể gửi lượt mới.',
                     ma_ho_tro='AI_THU_XU_LY')))

    @staticmethod
    def ghi_chay_thu(conn, giu, state, result):
        return viec._goi(conn, 'SELECT loi.ai_chay_thu_ghi_ket_qua(%s,%s,%s,%s,%s,%s,%s,%s::jsonb) AS r',
            (giu.ma.lay_de_truyen(), giu.phap_nhan_id, giu.viec_id, giu.instance_id, giu.the_he,
             'dang_chay', state, json.dumps(result, ensure_ascii=False, allow_nan=False)))


class WorkerEngine:
    """Đầu Core; không giữ transaction trong khi chờ socket/stream/engine.

    Một lease hoạt động mỗi socket. Drain giữ lease/ACK đang chạy; crash đóng
    kênh và gọi thu_hoi để manager thu credential/lease trước khi cấp lại.
    """
    _ai_thu_ack = None

    def __init__(self, sock, *, proof, kiem_the, khoa_rieng, kiem_instance,
                 ket_noi, hang_viec, kho_tep, instance_id, thu_hoi,
                 ngu_canh, kho_mask=None, ocr_doi_chieu=None, gioi_han=k.GIOI_HAN_TEP):
        k._can(isinstance(kiem_the, k.BoKiemThe) and callable(kiem_instance)
            and callable(ket_noi) and callable(thu_hoi)
            and (kho_mask is None or callable(kho_mask))
            and (ocr_doi_chieu is None or callable(ocr_doi_chieu))
            and type(gioi_han) is int and 0 < gioi_han <= k.GIOI_HAN_TEP)
        self._wire, self._kiem, self._key = _Socket(sock, proof), kiem_the, khoa_rieng
        self._song, self._ket_noi = kiem_instance, ket_noi
        self._hang, self._kho, self._instance = hang_viec, KhoTepEngine.boc(kho_tep), UUID(str(instance_id))
        self._thu_hoi, self._limit = thu_hoi, gioi_han
        self._lease, self._drain, self._dong = None, False, False
        self._drain_luc, self.loi_drain = None, None
        self._busy, self._lock = False, threading.RLock()
        self._ket_qua = None
        self._hoi_ai_dau_vao = None
        self._ai_thu_ack = None
        self._kho_mask = kho_mask
        # Provider chỉ do Core cấp; không trao kết nối/dịch vụ cho SDK.
        self._ocr_doi_chieu = ocr_doi_chieu
        self._mask_schema = None
        self._binding = dict(ngu_canh)
        if isinstance(hang_viec, HangViecCore) and hang_viec._ghim is not None:
            g = hang_viec._ghim
            k._can((self._binding.get('module'), self._binding.get('contract_id'),
                    self._binding.get('phien_ban_contract')) ==
                   (g.module, g.ma_contract, g.phien_ban_contract), 'KENH_KHONG_DU_QUYEN')

    def __repr__(self):
        return 'WorkerEngine(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize worker')

    def drain(self):
        with self._lock:
            self._drain = True
            if self._drain_luc is None:
                self._drain_luc = time.monotonic()
            return not self._busy and self._lease is None

    def _cho_yeu_cau(self):
        self._kiem_song()
        with self._lock:
            if self._drain:
                if self._lease is None and not self._busy:
                    raise EOFError()
                if time.monotonic()-self._drain_luc > 300:
                    # Giữ drain/cổng/lease cho manager đối chiếu; không kill mù.
                    self.loi_drain = 'DRAIN_QUA_HAN'

    def crash(self):
        with self._lock:
            if self._dong:
                return
            self._dong = True
            self._hoi_ai_dau_vao = None
        self._wire.dong()
        try:
            self._thu_hoi(self._instance)
        except Exception as exc:
            _xoa_loi(exc)

    def _kiem_song(self):
        k._can(not self._dong and self._song() is True, 'KENH_XAC_THUC_KHONG_HOP_LE')

    @contextmanager
    def _tx(self, han):
        self._kiem_song()
        with self._ket_noi() as conn:
            k._can(conn.info.transaction_status == 0, 'LOI_NOI_BO')
            with conn.transaction():
                conn.execute("SELECT set_config('lock_timeout','100ms',true)")
                conn.execute("SELECT set_config('statement_timeout',%s,true)",
                             (str(max(1, int((han-time.monotonic())*1000)))+'ms',))
                yield conn
                self._kiem_song()
                k._can(time.monotonic() < han, 'PHAN_HOI_QUA_HAN')

    def _kiem_header(self, h):
        self._kiem_song()
        k.kiem_header(h, can_the=False)
        k._can(h['operation'] in k.OPERATION_ENGINE
            and ((h['khoa'] is not None) if h['operation'] in k.OPERATION_OCR_GHI
                 else h['khoa'] is None)
            and h['parent_call_id'] is None and h['thu_tu_con'] is None
            and all(h[key] == val for key, val in self._kiem._rang_buoc.items())
            and all(h[key] == val for key, val in self._binding.items())
            and h['module_nguon'] == h['module'], 'KENH_KHONG_DU_QUYEN')
        k._can(h['stream'] is None or h['operation'] == 'engine.ghi_ket_qua')
        if h['operation'] == 'engine.nhan_viec':
            k._can(h['uy_nhiem'] == dict(loai='INSTANCE', ma='instance',
                viec_id=None, the_he_lease=None) and self._lease is None and not self._drain,
                'CHUA_SAN_SANG')
        else:
            g, u = self._lease, h['uy_nhiem']
            k._can(g is not None and g.giu_den > datetime.now(timezone.utc), 'MAT_LEASE')
            k._can(str(g.instance_id) == h['instance_id'] and h['module'] == g.module
                and h['phap_nhan_id'] == str(g.phap_nhan_id) and h['hanh_dong'] == g.hanh_dong
                and u['loai'] == 'UY_NHIEM_VIEC' and u['viec_id'] == str(g.viec_id)
                and u['the_he_lease'] == g.the_he
                and hmac.compare_digest(u['ma'], g.ma.lay_de_truyen()), 'MAT_LEASE')
        if h['operation'] in k.OPERATION_OCR_GHI | k.OPERATION_OCR_DOC:
            k._can(self._ocr_doi_chieu is not None, 'CHUA_SAN_SANG')
        k._can(0 < datetime.fromisoformat(h['deadline']).timestamp()-time.time() <= 30,
               'PHAN_HOI_QUA_HAN')

    def phuc_vu(self):
        """Chạy trên worker thread do Core sở hữu; không khởi động server."""
        try:
            han = time.monotonic()+30
            seed = dict(chieu='core_den_con', request_id=str(uuid4()), call_id=str(uuid4()))
            self._wire.gui(_control('challenge', seed), b'', han)
            ack = self._wire.nhan(han)
            k._can(ack.header == _control('xac_thuc', {**seed, 'chieu': 'con_den_core'}) and ack.than == b'')
            while not self._dong:
                self._mot_call()
        except Exception as exc:
            _xoa_loi(exc)
        finally:
            self.crash()

    def _mot_call(self):
        self._h_loi = None
        try:
            self._mot_call_goc()
        except Exception as exc:
            ma = getattr(exc, 'ma', None)
            ma = 'MAT_LEASE' if ma == 'VIEC_MAT_LEASE' else ma
            if ma in k.MA_LOI_HTTP and self._h_loi is not None:
                h = self._h_loi
                loi = k.LoiKenh(ma, retry_after=getattr(exc, 'retry_after', None))
                if isinstance(exc, _XungDotLuotMask):
                    loi.thu_lai_duoc = True
                out = dict(protocol=k.PROTOCOL, phien_ban=k.PHIEN_BAN, kieu='response',
                    chieu='core_den_con', request_id=h['request_id'], call_id=h['call_id'],
                    operation=h['operation'], status=loi.http_status, da_commit=False,
                    bien_nhan=None, stream=None, hash_than=hashlib.sha256(b'').hexdigest(),
                    loi=dict(ma=ma, thong_diep=ma, request_id=h['request_id'],
                        thu_lai_duoc=loi.thu_lai_duoc, http_status=loi.http_status))
                if loi.retry_after is not None:
                    out['retry_after'] = loi.retry_after
                try:
                    self._wire.gui(out, b'', time.monotonic()+1)
                    if isinstance(exc, _TuChoiNhanViec) and h['operation'] == 'engine.nhan_viec':
                        _xoa_loi(exc)
                        return
                    if isinstance(exc, _XungDotLuotMask):
                        _xoa_loi(exc)
                        return
                except Exception as send_error:
                    _xoa_loi(send_error)
            raise
        finally:
            self._h_loi = None

    def _mot_call_goc(self):
        prep = self._wire.nhan(None, cho=self._cho_yeu_cau)
        han = time.monotonic()+30
        k._can(prep.header['kieu'] == 'chuan_bi')
        h = k._doc_json(prep.than)
        k.kiem_header(h, can_the=False)
        self._h_loi = h
        self._kiem_header(h)
        k._can((prep.header['call_id'], prep.header['request_id']) == (h['call_id'], h['request_id']))
        han = min(han, time.monotonic()+datetime.fromisoformat(h['deadline']).timestamp()-time.time())
        signed = {**h, 'the_ky': k.cap_the(h, self._key).lay_de_truyen()}
        cap = k._json(signed)
        self._wire.gui(_control('cap_the', {**h, 'chieu': 'core_den_con'}, cap), cap, han)
        frame = self._wire.nhan(han, self._kiem)
        k._can(frame.header == signed)
        self._kiem_header(h)
        with self._lock:
            self._busy = True
        stack = ExitStack()
        try:
            data = k._doc_json(frame.than)
            operation = (h['operation'] if h['operation'] in k.OPERATION_OCR_GHI | k.OPERATION_OCR_DOC
                         else h['operation'].split('.')[1])
            if operation != 'nhan_viec':
                k._can(data.pop('lan_thu_id', None) == str(self._lease.lan_thu_id), 'MAT_LEASE')
                if operation == 'doc_dau_vao' and data:
                    # Carrier Mask phải được cấp kho trước cả transaction kiểm lease.
                    k._can(self._kho_mask is not None, 'KENH_KHONG_DU_QUYEN')
                if self._ai_thu_ack is None:
                    with self._tx(han) as conn:
                        self._hang.kiem(conn, self._lease)
            content = self._nhan_stream(h, han, stack) if h['stream'] else None
            result, stream, after = self._thuc_thi(operation, data, content, h, han, stack)
            raw = b'' if stream is not None else k._json({'ket_qua': result})
            response = dict(protocol=k.PROTOCOL, phien_ban=k.PHIEN_BAN, kieu='response',
                chieu='core_den_con', request_id=h['request_id'], call_id=h['call_id'],
                operation=h['operation'], status=200, da_commit=True, bien_nhan=None,
                hash_than=hashlib.sha256(raw).hexdigest(), stream=None if stream is None else stream[0], loi=None)
            self._kiem_song()
            self._wire.gui(response, raw, han)
            if stream is not None:
                self._gui_stream(response, *stream, han)
            if after is not None:
                after()
        finally:
            stack.close()
            with self._lock:
                self._busy = False

    def _nhan_stream(self, h, han, stack):
        dem = k.BoDemStream(h['stream'], gioi_han=self._limit)
        raw = stack.enter_context(tempfile.TemporaryFile())
        while True:
            self._kiem_song()
            f = self._wire.nhan(han)
            k._can((f.header['call_id'], f.header['request_id']) == (h['call_id'], h['request_id']))
            if self._ai_thu_ack is None:
                with self._tx(han) as conn:
                    self._hang.kiem(conn, self._lease)
            if f.header['kieu'] == 'end':
                k._can(f.header['stream_id'] == h['stream']['stream_id'] and
                       f.header['kich_thuoc_byte'] == dem.tong_byte)
                dem.ket_thuc()
                raw.seek(0)
                info = _thong_tin_luong(raw, self._limit)
                k._can(info['mime'] == h['stream']['mime'], 'MIME_KHONG_HO_TRO')
                return _LuongDaKiem(raw, **info)
            k._can(f.header['kieu'] == 'chunk')
            dem.nhan_chunk(f.header['stream_id'], f.header['thu_tu_chunk'], f.than)
            raw.write(f.than)
            if ((f.header['thu_tu_chunk']+1) % CUA_SO_CHUNK == 0 or
                    dem.tong_byte == h['stream']['kich_thuoc_byte']):
                self._wire.gui(_control('ack_chunk', {**h, 'chieu': 'core_den_con'},
                    stream_id=f.header['stream_id'], thu_tu_chunk=f.header['thu_tu_chunk']), b'', han)

    def _gui_stream(self, h, d, raw, kiem, han):
        dem = k.BoDemStream(d, gioi_han=self._limit)
        i = 0
        while dem.tong_byte < d['kich_thuoc_byte']:
            kiem()
            chunk = raw.read(k.GIOI_HAN_CHUNK)
            k._can(bool(chunk))
            dem.nhan_chunk(d['stream_id'], i, chunk)
            self._wire.gui(_control('chunk', h, chunk, stream_id=d['stream_id'],
                thu_tu_chunk=i, kich_thuoc_byte=len(chunk)), chunk, han)
            if (i+1) % CUA_SO_CHUNK == 0 or dem.tong_byte == d['kich_thuoc_byte']:
                ack = self._wire.nhan(han)
                k._can(ack.header == _control('ack_chunk', {**h, 'chieu': 'con_den_core'},
                    stream_id=d['stream_id'], thu_tu_chunk=i) and ack.than == b'')
            i += 1
        dem.ket_thuc()
        kiem()
        self._wire.gui(_control('end', h, stream_id=d['stream_id'],
            kich_thuoc_byte=dem.tong_byte), b'', han)

    def _kiem_doc(self, g, inp, ref, han):
        """Transaction ngắn trước mỗi chunk/end; không giữ tx khi chờ ACK."""
        k._can(g.giu_den > datetime.now(timezone.utc), 'MAT_LEASE')
        with self._tx(han) as conn:
            self._hang.kiem(conn, g)
            current = self._hang.dau_vao(conn, g)
            k._can(current.tai_lieu_id == inp.tai_lieu_id and ref in current.tep,
                   'KENH_KHONG_DU_QUYEN')
            self._kho.tham_chieu(conn, tai_lieu_id=inp.tai_lieu_id,
                tep_id=ref['tep_id'], bien_the=ref['bien_the'], ma=g.ma,
                module=g.module, phap_nhan_id=g.phap_nhan_id,
                hanh_dong=g.hanh_dong.rsplit(':', 1)[0]+':XEM',
                viec_id=g.viec_id, the_he=g.the_he)

    def _kiem_metadata_hoi_ai(self, meta, so_nguon):
        """Vỏ tra_loi_ai.v2 chỉ giữ mã metadata đóng, không mang nội dung AI."""
        k._can(isinstance(meta, dict) and set(meta) == {
            'bien_the', 'ma_contract', 'phien_ban_contract', 'trang_thai',
            'ly_do', 'revision_truoc', 'nguon'}, 'KENH_DU_LIEU_KHONG_HOP_LE')
        k._can(isinstance(meta['bien_the'], str) and len(meta['bien_the']) <= 32
            and meta['bien_the'] in tai_lieu._BIEN_THE
            and (meta['ma_contract'], meta['phien_ban_contract']) == ('tra_loi_ai.v2', '2.0.0')
            and meta['trang_thai'] in ('cho', 'dang_xu_ly', 'thanh_cong', 'loi')
            and type(meta['revision_truoc']) is int and meta['revision_truoc'] >= 0,
            'KENH_DU_LIEU_KHONG_HOP_LE')
        ly_do, refs = meta['ly_do'], meta['nguon']
        k._can(ly_do is None or isinstance(ly_do, str) and ly_do in _LY_DO_METADATA_HOI_AI,
            'KENH_DU_LIEU_KHONG_HOP_LE')
        k._can(isinstance(refs, list) and len(refs) <= so_nguon
            and all(isinstance(r, dict) and set(r) == {'tep_id', 'sha256'}
                and isinstance(r['tep_id'], str) and len(r['tep_id']) == 36
                and k._uuid(r['tep_id']) and k._hash(r['sha256']) for r in refs),
            'KENH_DU_LIEU_KHONG_HOP_LE')

    def _kiem_nguon_hoi_ai(self, conn, g, inp, ctx):
        """Cấp văn bản cùng nguồn đã kiểm quyền, không tin danh sách tự khai.

        Dùng lại cửa metadata tài liệu/lease; không đọc kho hoặc chờ AI trong tx.
        Hash nguồn và revision lấy từ Core, đối chiếu lại trước bàn giao kết quả.
        """
        hang = self._hang
        if not (isinstance(hang, HangViecCore) and hang._ghim is not None
                and hang._ghim.capability == 'ai.hoi@1'):
            k._can(self._binding.get('contract_id') != 'tra_loi_ai.v2', 'KENH_KHONG_DU_QUYEN')
            return
        data, nguon = inp.du_lieu, inp.du_lieu['nguon_core']
        if hang.la_chay_thu_hoi_ai():
            snapshot = k._json(data)
            k._can(self._hoi_ai_dau_vao is None or self._hoi_ai_dau_vao == snapshot,
                'KENH_KHONG_DU_QUYEN')
            self._hoi_ai_dau_vao = snapshot
            return
        ids = nguon['nguon_tep_ids']
        k._can(ids and len(ids) == len(set(ids))
            and nguon['vi_tri']['tep_id'] in ids
            and set(ids) == {r['tep_id'] for r in inp.tep}, 'KENH_KHONG_DU_QUYEN')
        refs = []
        for item in inp.tep:
            view = tai_lieu.lay(conn, tai_lieu_id=inp.tai_lieu_id,
                bien_the=item['bien_the'], **ctx)
            k._can((view['id'], view['module'], view['phap_nhan_id']) ==
                (str(inp.tai_lieu_id), g.module, str(g.phap_nhan_id)), 'KENH_KHONG_DU_QUYEN')
            ref = self._kho.tham_chieu(conn, tai_lieu_id=inp.tai_lieu_id,
                tep_id=item['tep_id'], bien_the=item['bien_the'], **ctx)
            k._can(ref['tep_id'] == item['tep_id'], 'KENH_KHONG_DU_QUYEN')
            refs.append(dict(tep_id=ref['tep_id'], sha256=ref['sha256']))
        meta = data['du_lieu_ket_qua']
        self._kiem_metadata_hoi_ai(meta, len(ids))
        k._can(type(data['revision_tep_truoc']) is int and data['revision_tep_truoc'] >= 0
            and nguon['revision'] == meta['revision_truoc'] + 1,
            'KENH_DU_LIEU_KHONG_HOP_LE')
        data['du_lieu_ket_qua'] = {**meta, 'nguon': refs}
        snapshot = k._json(data)
        k._can(self._hoi_ai_dau_vao is None or self._hoi_ai_dau_vao == snapshot,
            'KENH_KHONG_DU_QUYEN')
        self._hoi_ai_dau_vao = snapshot

    def _kiem_ket_qua_hoi_ai(self, conn, content, data, inp):
        """Engine không được tự đổi nguồn, revision hoặc dẫn chứng khi gửi lại."""
        hang = self._hang
        if not (isinstance(hang, HangViecCore) and hang._ghim is not None
                and hang._ghim.capability == 'ai.hoi@1'):
            return
        from .dispatcher import KiemSchema
        self._kiem_metadata_hoi_ai(data['du_lieu'],
            len(inp.du_lieu['nguon_core']['nguon_tep_ids']))
        k._can(data['du_lieu'] == inp.du_lieu['du_lieu_ket_qua']
            and data['revision_tep_truoc'] == inp.du_lieu['revision_tep_truoc'],
            'KENH_KHONG_DU_QUYEN')
        content.seek(0)
        try:
            out = json.load(content)
        except (ValueError, UnicodeError):
            raise k.LoiKenh('PHAN_HOI_SAI_CONTRACT') from None
        finally:
            content.seek(0)
        nguon = inp.du_lieu['nguon_core']
        k._can(KiemSchema().kiem({'$ref': 'urn:ktt:contract:tra_loi_ai.v2'}, out)
            and out['revision'] == nguon['revision']
            and out['nguon_tep_ids'] == nguon['nguon_tep_ids']
            and all(d['vi_tri'] == nguon['vi_tri'] for t in out['truong'] for d in t['dan_chung']),
            'PHAN_HOI_SAI_CONTRACT')
        if hang.la_chay_thu_hoi_ai():
            # Chỉ tài liệu gốc là căn cứ; van_ban còn chứa cả câu hỏi.
            # Đọc qua cửa lease trong cùng transaction, không tách theo nhãn
            # "Câu hỏi:" vì nhãn có thể có sẵn trong tài liệu hoặc câu hỏi.
            g = self._lease
            row = viec._goi(conn, 'SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s) AS r',
                (g.ma.lay_de_truyen(), g.phap_nhan_id, g.viec_id, g.instance_id, g.the_he))
            # Cổng AI gộp khoảng trắng trong trích dẫn, kể cả xuống dòng/tab.
            text = ' '.join(row['dau_vao']['tai_lieu'].split())
            quotes = [' '.join(d['trich_dan'].split()) for t in out['truong'] for d in t['dan_chung']]
            k._can(all(quote and quote in text for quote in quotes),
                'PHAN_HOI_SAI_CONTRACT')
        return out

    def _ghi_chay_thu(self, conn, g, out):
        from .van_ban_an_toan import la_van_ban_mo_ta_an_toan
        local_error = any(code.startswith('LOCAL_') for code in out['ly_do'])
        state = 'loi' if local_error or out['duong'] != 'LOCAL' else 'xong'
        answer = out['cau_tra_loi'] or '\n'.join(
            str(t['gia_tri'].get('gia_tri', '')) + '\nCăn cứ: ' +
            '\n'.join(d['trich_dan'] for d in t['dan_chung']) for t in out['truong'])
        models = [m['ten'] for m in out['mo_hinh'] if m['duong'] == 'LOCAL' and m['ten']]
        model = models[-1] if models else ''
        model = model if la_van_ban_mo_ta_an_toan(model, 128) else ''
        # Không thấy căn cứ: tra_loi_ai.v2 khóa ly_do chỉ KHONG_THAY_CAN_CU.
        # Core chưa có cửa đọc nhật ký provenance Hỏi AI theo việc/mã tương quan;
        # giữ model từ mo_hinh, để trống lý do chọn thay vì suy lại từ cấu hình.
        choices = [reason for reason in out['ly_do']
                   if isinstance(reason, str) and re.fullmatch(r'uu_tien|co_dinh|du_phong:[1-9][0-9]*', reason)]
        result = dict(tra_loi=answer[:20000] if state == 'xong' else '', model=model,
            ly_do_chon=choices[-1] if model and choices else '', loi=None)
        if state == 'loi':
            result['loi'] = dict(thong_diep_viet='Máy AI cục bộ chưa trả được kết quả hợp lệ. Có thể gửi lượt mới.',
                                ma_ho_tro='AI_THU_LOCAL' if local_error else 'AI_THU_XU_LY')
        k._can(self._hang.ghi_chay_thu(conn, g, state, result) is True, 'LOI_NOI_BO')
        return dict(ket_qua_id=out['nguon_tep_ids'][0], da_ban_giao=True)

    def _thuc_thi(self, op, data, content, h, han, stack):
        if op in k.OPERATION_OCR_GHI | k.OPERATION_OCR_DOC:
            k._can(content is None)
            return self._ocr(op, data, h, han), None, None
        if op == 'doc_dau_vao' and data:
            k._dong(data, {'mask'})
            k._can(content is None)
            return self._mask(data['mask'], h, han), None, None
        fields = {'nhan_viec': set(), 'doc_dau_vao': set(), 'mo_doc': {'tep_id'},
            'heartbeat': {'lease_giay'}, 'ghi_ket_qua': {'ten', 'du_lieu', 'revision_tep_truoc'},
            'ket_thuc': {'trang_thai', 'ket_qua_id', 'ma_loi'}}
        k._dong(data, fields[op])
        k._can((content is not None) == (op == 'ghi_ket_qua'))
        g, stream, after = self._lease, None, None
        if self._ai_thu_ack is not None:
            # Kết quả và việc đã commit chung. Chỉ phát lại ACK cùng nội dung,
            # hoặc xác nhận kết thúc; không dùng lease đã thu hồi để làm việc mới.
            ack, fingerprint = self._ai_thu_ack
            if op == 'ghi_ket_qua':
                content.seek(0)
                actual = hashlib.sha256(k._json(data) + content.read()).hexdigest()
                k._can(actual == fingerprint, 'KENH_KHONG_DU_QUYEN')
                return dict(ack), None, None
            if op == 'heartbeat':
                return _giu_json(g), None, None
            k._can(op == 'ket_thuc' and data == dict(trang_thai='XONG',
                ket_qua_id=ack['ket_qua_id'], ma_loi=None), 'KENH_KHONG_DU_QUYEN')
            return True, None, lambda: self._bo_lease()
        ai_thu_ack = None
        with self._tx(han) as conn:
            if op == 'nhan_viec':
                k._can(not self._drain, 'CHUA_SAN_SANG')
                g = self._hang.nhan(conn, self._instance)
                if g is not None:
                    k._can(g.instance_id == self._instance and g.module == h['module']
                        and str(g.phap_nhan_id) == h['phap_nhan_id'] and g.hanh_dong == h['hanh_dong'], 'MAT_LEASE')
                result = None if g is None else _giu_json(g)
            else:
                self._hang.kiem(conn, g)
                ctx = dict(ma=g.ma, module=g.module, phap_nhan_id=g.phap_nhan_id,
                    hanh_dong=g.hanh_dong.rsplit(':', 1)[0]+':XEM', viec_id=g.viec_id, the_he=g.the_he)
                if op == 'heartbeat':
                    g = self._hang.gia_han(conn, g, **data)
                    result = _giu_json(g)
                elif op == 'ket_thuc':
                    k._can(data['ket_qua_id'] == self._ket_qua, 'KENH_KHONG_DU_QUYEN')
                    result = self._hang.ket_thuc(conn, g, data['trang_thai'],
                        ket_qua_id=data['ket_qua_id'], ma_loi=data['ma_loi'])
                    after = lambda: self._bo_lease()
                else:
                    inp = self._hang.dau_vao(conn, g)
                    self._kiem_nguon_hoi_ai(conn, g, inp, ctx)
                    if op == 'doc_dau_vao':
                        result = inp.du_lieu
                    elif op == 'mo_doc':
                        ref = next((r for r in inp.tep if r['tep_id'] == data['tep_id']), None)
                        k._can(ref is not None, 'KENH_KHONG_DU_QUYEN')
                        src = stack.enter_context(self._kho.mo_doc(conn, tai_lieu_id=inp.tai_lieu_id,
                            tep_id=data['tep_id'], bien_the=ref['bien_the'], **ctx))
                        info = _thong_tin_luong(src, self._limit)
                        d = dict(stream_id=str(uuid4()), **info, ten=ref['ten'])
                        stream, result = (d, src, lambda: self._kiem_doc(g, inp, ref, han)), None
                    else:
                        k._can(data['ten'] == h['stream']['ten'])
                        out = self._kiem_ket_qua_hoi_ai(conn, content, data, inp)
                        if isinstance(self._hang, HangViecCore) and self._hang.la_chay_thu_hoi_ai():
                            result = self._ghi_chay_thu(conn, g, out)
                            content.seek(0)
                            ai_thu_ack = (dict(result), hashlib.sha256(k._json(data) + content.read()).hexdigest())
                        else:
                            result = self._hang.ban_giao.ghi(conn, giu_viec=g,
                                tai_lieu_id=inp.tai_lieu_id, luong=content,
                                request_id=UUID(h['request_id']), het_han_luc=inp.het_han_luc,
                                **data, **{key: val for key, val in ctx.items() if key not in ('viec_id', 'the_he')}
                                | {'hanh_dong': g.hanh_dong})
                if op != 'ket_thuc' and ai_thu_ack is None:
                    self._hang.kiem(conn, g)
        # Ra khỏi transaction gốc thật trước công bố lease/ACK.
        if op == 'nhan_viec' or op == 'heartbeat':
            self._lease = g
        if op == 'ghi_ket_qua':
            if ai_thu_ack is not None:
                self._ai_thu_ack = ai_thu_ack
            else:
                with self._ket_noi() as reader:
                    result = self._hang.ban_giao.xac_nhan_da_commit(reader,
                        tai_lieu_id=inp.tai_lieu_id, ket_qua_id=result['ket_qua_id'],
                        bien_the=data['du_lieu']['bien_the'], **ctx)
            k._can(result['da_ban_giao'] is True, 'LOI_NOI_BO')
            self._ket_qua = result['ket_qua_id']
        return result, stream, after

    def _nguon_ocr(self, conn, g):
        """Chỉ lấy băm và đối tượng từ nguồn Core đã kiểm quyền của lease."""
        self._hang.kiem(conn, g)
        inp = self._hang.dau_vao(conn, g)
        ctx = dict(ma=g.ma, module=g.module, phap_nhan_id=g.phap_nhan_id,
            hanh_dong=g.hanh_dong.rsplit(':', 1)[0]+':XEM', viec_id=g.viec_id, the_he=g.the_he)
        refs = []
        for item in inp.tep:
            ref = self._kho.tham_chieu(conn, tai_lieu_id=inp.tai_lieu_id,
                tep_id=item['tep_id'], bien_the=item['bien_the'], **ctx)
            k._can(ref['tep_id'] == item['tep_id'] and k._hash(ref['sha256']),
                'KENH_KHONG_DU_QUYEN')
            refs.append((ref['tep_id'], item['bien_the'], ref['sha256']))
        k._can(bool(refs), 'KENH_KHONG_DU_QUYEN')
        # Dùng cửa 068 hiện có, không truy cập bảng/module khác hoặc tin payload.
        source = viec._goi(conn,
            'SELECT loi.nguon_lease_engine(%s,%s,%s,%s,%s,%s,%s,%s) AS r',
            (*viec._giu(conn, g), g.lan_thu_id))
        k._can(source['engine_id'] == str(self._hang._ghim.engine_id)
            and source['buoc_id'] == str(g.buoc_viec_id)
            and source['lan_thu_id'] == str(g.lan_thu_id)
            and source['phien_ban_contract'] == self._hang._ghim.phien_ban_contract
            and k._chuoi(source['bang']) and k._uuid(source['id']), 'KENH_KHONG_DU_QUYEN')
        binding = dict(doi_tuong=dict(bang=source['bang'], id=source['id']),
            phien_ban_contract=source['phien_ban_contract'])
        self._hang.kiem(conn, g)
        return inp.tai_lieu_id, tuple(refs), binding

    @staticmethod
    def _ket_qua_ocr(op, row):
        from .ocr_doi_chieu import KetQuaLuotOCR, TrangThaiLuotOCR
        if row is None:
            k._can(op == 'ocr.doc_luot', 'PHAN_HOI_SAI_CONTRACT')
            return dict(trang_thai='khong_co', phien_ban=None)
        k._can(isinstance(row, KetQuaLuotOCR)
            and isinstance(row.trang_thai, TrangThaiLuotOCR), 'PHAN_HOI_SAI_CONTRACT')
        states = {'GIU': 'dang_giu', 'CHUA_RO': 'chua_ro',
            'DA_TIEU_TRANG': 'da_tieu', 'HOAN_TRANG': 'hoan_trang'}
        result = dict(trang_thai=states[row.trang_thai.value])
        if op != 'ocr.chot_luot':
            result['phien_ban'] = row.phien_ban
        if op == 'ocr.giu_luot':
            result['ma_tuong_quan'] = row.ma_tuong_quan
        return k.kiem_dto_ocr(op, result, phan_hoi=True)

    def _ocr(self, op, data, h, han):
        """Biên nhận GHI bền trước gọi provider, ACK sau các commit riêng.

        Provider 126 sở hữu transaction trên kết nối rảnh. Nếu gián đoạn giữa
        hai commit, dấu đang xử lý chặn phát lại; không suy đoán đã gửi/hoàn.
        Đọc chỉ trả snapshot, không cấp lại mã tương quan để gửi nhận dạng.
        """
        from . import tiep_nhan
        from .ocr_doi_chieu import LoiOCRDoiChieu, NguCanhOCR, TrangThaiLuotOCR
        ma = 'LOI_NOI_BO'
        try:
            self._kiem_header(h)
            data = k.kiem_dto_ocr(op, data)
            g, hang = self._lease, self._hang
            k._can(isinstance(hang, HangViecCore) and hang._ghim is not None
                and hang._dich_vu is not None, 'KENH_KHONG_DU_QUYEN')
            pin = hang._dich_vu._ghim.get(hang._ghim.capability)
            k._can(pin is not None and pin.ma_engine == 'e_ocr'
                and pin.engine_id == hang._ghim.engine_id, 'KENH_KHONG_DU_QUYEN')
            ghi = op in k.OPERATION_OCR_GHI
            with self._tx(han) as conn:
                source = self._nguon_ocr(conn, g)
                hashes = {r[2] for r in source[1]}
                if op != 'ocr.chot_luot':
                    k._can(data['bam_noi_dung'] in hashes, 'KENH_KHONG_DU_QUYEN')
                if ghi:
                    ctx = dict(ma=g.ma, module=g.module, phap_nhan_id=g.phap_nhan_id,
                        hanh_dong=g.hanh_dong, viec_id=g.viec_id, the_he=g.the_he)
                    ts = dict(operation=op, khoa=h['khoa'], **source[2], **ctx,
                        noi_dung=dict(du_lieu=data, viec_id=str(g.viec_id),
                            the_he=g.the_he, lan_thu_id=str(g.lan_thu_id)))
                    quyen = dict(**source[2], hanh_dong=g.hanh_dong.rsplit(':', 1)[0]+':XEM')
                    old = tiep_nhan.tra_core(conn, **ts)
                    if old is not None:
                        k._can(old['ket_qua'] != {'cho_doi_chieu': True}, 'XUNG_DOT')
                        return k.kiem_dto_ocr(op, old['ket_qua'], phan_hoi=True)
                    tiep_nhan.ghi_core(conn, **ts, quyen_doc=quyen,
                        ket_qua={'cho_doi_chieu': True}, trang_thai='DANG_XU_LY')
                hang.kiem(conn, g)
            self._kiem_header(h)
            with self._ket_noi() as conn:
                k._can(conn.info.transaction_status == 0, 'LOI_NOI_BO')
                provider = self._ocr_doi_chieu(conn, ngu_canh=NguCanhOCR.tu_lease(g))
                if op == 'ocr.giu_luot':
                    gid, corr = uuid4(), 'ocr:' + uuid4().hex
                    row = provider.giu_luot(ma_bam=data['bam_noi_dung'],
                        so_trang=data['so_trang'], giu_trang_id=gid, ma_tuong_quan=corr)
                    result = self._ket_qua_ocr(op, row)
                    k._can((row.giu_trang_id, row.viec_id, row.ma_tuong_quan, row.so_trang,
                            row.phien_ban) == (gid, g.viec_id, corr, data['so_trang'], 1),
                        'PHAN_HOI_SAI_CONTRACT')
                elif op == 'ocr.doc_luot':
                    result = self._ket_qua_ocr(op,
                        provider.doc_trang_thai(ma_bam=data['bam_noi_dung']))
                else:
                    matches = []
                    for bam in sorted(hashes):
                        row = provider.doc_trang_thai(ma_bam=bam)
                        self._ket_qua_ocr('ocr.doc_luot', row)
                        if row is not None and row.ma_tuong_quan == data['ma_tuong_quan']:
                            matches.append((bam, row))
                    k._can(len(matches) == 1 and matches[0][1].viec_id == g.viec_id,
                        'KENH_KHONG_DU_QUYEN')
                    bam, row = matches[0]
                    k._can(row.phien_ban == data['phien_ban'] and row.dang_chan_gui, 'XUNG_DOT')
                    state = {'da_tieu': TrangThaiLuotOCR.DA_TIEU_TRANG,
                        'hoan_trang': TrangThaiLuotOCR.HOAN_TRANG}[data['ket_qua']]
                    final = provider.chot_luot(ma_bam=bam, giu_trang_id=row.giu_trang_id,
                        phien_ban=data['phien_ban'], trang_thai_cu=row.trang_thai, trang_thai_moi=state)
                    result = self._ket_qua_ocr(op, final)
                    k._can((final.giu_trang_id, final.viec_id, final.ma_tuong_quan,
                            final.phien_ban, final.trang_thai) == (row.giu_trang_id, g.viec_id,
                            row.ma_tuong_quan, data['phien_ban']+1, state), 'PHAN_HOI_SAI_CONTRACT')
            self._kiem_header(h)
            with self._tx(han) as conn:
                k._can(self._nguon_ocr(conn, g) == source, 'KENH_KHONG_DU_QUYEN')
                if ghi:
                    tiep_nhan.ghi_core(conn, **ts, quyen_doc=quyen, ket_qua=result)
                hang.kiem(conn, g)
            return result
        except Exception as exc:
            if isinstance(exc, k.LoiKenh):
                ma = exc.ma
            elif isinstance(exc, LoiOCRDoiChieu):
                ma = {'42501': 'KENH_KHONG_DU_QUYEN', 'OCR_LUOT_DAU_VAO': 'YEU_CAU_KHONG_HOP_LE',
                    'OCR_LUOT_DANG_BI_CHAN': 'XUNG_DOT', 'OCR_LUOT_XUNG_DOT': 'XUNG_DOT',
                    'OCR_LUOT_GIAO_DICH': 'XUNG_DOT'}.get(exc.ma, 'LOI_NOI_BO')
            elif isinstance(exc, tiep_nhan.LoiTiepNhan):
                ma = {'KHOA_CHONG_TRUNG_KHAC_NOI_DUNG': 'KHOA_CHONG_TRUNG_KHAC_NOI_DUNG',
                    'YEU_CAU_DANG_XU_LY': 'XUNG_DOT', 'BIEN_NHAN_CORE_HET_HAN': 'XUNG_DOT',
                    'BIEN_NHAN_KHONG_THAY': 'KENH_KHONG_DU_QUYEN'}.get(exc.ma, 'LOI_NOI_BO')
            elif isinstance(exc, viec.LoiViec) and exc.ma == 'VIEC_MAT_LEASE':
                ma = 'MAT_LEASE'
            _xoa_loi(exc)
        finally:
            data = source = hashes = ts = ctx = quyen = old = provider = row = final = result = matches = None
        raise k.LoiKenh(ma) from None

    def _kiem_mask_schema(self, ten, data, *, dau_ra=False):
        if self._mask_schema is None:
            from .dispatcher import KiemSchema
            self._mask_schema = KiemSchema()
        k._can(self._mask_schema.kiem(
            {'$ref': 'urn:ktt:contract:mask_' + ten + '_noi_bo.v1'}, data),
            'PHAN_HOI_SAI_CONTRACT' if dau_ra else 'KENH_DU_LIEU_KHONG_HOP_LE')

    def _mask(self, envelope, h, han):
        """Cửa kho riêng của Mask: kiểm binding trước khi gọi cửa SQL 119/120.

        Mask._goi sở hữu transaction và commit. Không lồng vào _tx, không
        ghép snapshot/nhật ký vào đầu vào thường hay kết quả công bố cho module.
        """
        k._can(self._kho_mask is not None, 'KENH_KHONG_DU_QUYEN')
        from .mask import XungDotLuotMask
        k._dong(envelope, {'operation', 'du_lieu'})
        op, data, g = envelope['operation'], envelope['du_lieu'], self._lease
        k._can(isinstance(op, str) and op in OPERATION_MASK)
        self._kiem_header(h)
        hang = self._hang
        k._can(isinstance(hang, HangViecCore) and hang._ghim is not None
            and hang._dich_vu is not None, 'KENH_KHONG_DU_QUYEN')
        ghim = hang._ghim
        pin = hang._dich_vu._ghim.get(ghim.capability)
        k._can(pin is not None and pin.ma_engine == 'e_mask'
            and pin.engine_id == ghim.engine_id, 'KENH_KHONG_DU_QUYEN')
        ten = 'snapshot' if op == 'mask.snapshot' else 'chot'
        self._kiem_mask_schema(ten + '_vao', data)
        with self._tx(han) as conn:
            hang.kiem(conn, g)
            inp = hang.dau_vao(conn, g)
            binding = inp.mask
            k._can(isinstance(binding, DauVaoMask)
                and (data['ma_yeu_cau'], data['ma_luot'], data['loai']) ==
                    (str(binding.ma_yeu_cau), str(binding.ma_luot), binding.loai),
                'KENH_KHONG_DU_QUYEN')
        if ten == 'chot' and data['ket_qua'] is not None:
            kq = data['ket_qua']
            k._can((kq['ma_yeu_cau'], kq['ma_luot']) ==
                (data['ma_yeu_cau'], data['ma_luot'])
                and ('van_ban_da_che' in kq) == (binding.loai == 'che'))
        loi_xung_dot = False
        try:
            with self._ket_noi() as conn:
                self._kiem_song()
                k._can(conn.info.transaction_status == 0, 'LOI_NOI_BO')
                kho = self._kho_mask(conn, ma=g.ma, module=g.module, phap_nhan_id=g.phap_nhan_id,
                    hanh_dong=g.hanh_dong, tai_lieu_id=inp.tai_lieu_id,
                    viec_id=g.viec_id, the_he=g.the_he)
                args = () if ten == 'snapshot' else (data['phien_ban'],
                    None if data['nhat_ky'] is None else json.dumps(data['nhat_ky'], ensure_ascii=False),
                    None if data['ket_qua'] is None else json.dumps(data['ket_qua'], ensure_ascii=False))
                result = kho._goi(ten, binding.ma_yeu_cau, binding.ma_luot, binding.loai, *args)
            self._kiem_header(h)
            with self._tx(han) as conn:
                hang.kiem(conn, g)
            self._kiem_mask_schema(ten + '_ra', result, dau_ra=True)
            if ten == 'snapshot' and binding.loai == 'che':
                k._can(not result.get('bi_danh_bo_sung'), 'PHAN_HOI_SAI_CONTRACT')
            if ten == 'chot':
                k._can((result['ma_yeu_cau'], result['ma_luot']) ==
                    (data['ma_yeu_cau'], data['ma_luot'])
                    and ('van_ban_da_che' in result) == (binding.loai == 'che'),
                    'PHAN_HOI_SAI_CONTRACT')
            return result
        except XungDotLuotMask as exc:
            loi_xung_dot = True
            _xoa_loi(exc)
        except Exception as exc:
            ma = getattr(exc, 'ma', 'LOI_NOI_BO')
            _xoa_loi(exc)
        finally:
            envelope = data = result = args = kho = inp = None
        if loi_xung_dot:
            raise _XungDotLuotMask('XUNG_DOT') from None
        raise k.LoiKenh(ma) from None

    def _bo_lease(self):
        self._lease, self._ket_qua = None, None
        self._hoi_ai_dau_vao = None
        self._ai_thu_ack = None
