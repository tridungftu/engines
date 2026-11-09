"""KN2: cầu HTTPS trên máy ABBYY, mặc định tắt, không I/O khi import.

Bootstrap tin cậy cấp khóa bytes và SSLContext đã nạp chứng thư trong RAM.
Không có CLI/biến môi trường/tệp cấu hình cấp khóa. Chỉ chay() mở socket.
CauNoiABBYY.xu_ly() nhận luồng và socket do transport cấp; có thể mock toàn bộ.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
import json
import logging
import math
import ssl
import threading
import time

from .lib.cong_ocr import HotFolderPDF, chuan_hoa_ma_tuong_quan


@dataclass(frozen=True)
class CauHinhCauNoi:
    bat: bool = False
    khoa: bytes = field(default=b'', repr=False)
    ip_core: tuple[str, ...] = ()
    thu_muc_hot_folder: object = field(default=None, repr=False)
    tls: object = field(default=None, repr=False)
    dia_chi: str = '127.0.0.1'
    cong: int = 9443
    toi_da_byte: int = 20 * 1024**2
    toi_da_byte_ra: int = 40 * 1024**2
    toi_da_giay: float = 300.0
    cho_hang_giay: float = 10.0
    doc_giay: float = 10.0
    toi_da_cho: int = 4
    toi_da_ket_noi: int = 8
    toi_da_ma: int = 10_000


@dataclass(frozen=True)
class YeuCau:
    """ket_noi phải là socket của transport, không lấy địa chỉ từ payload."""

    ket_noi: object = field(repr=False)
    headers: object = field(repr=False)
    luong: object = field(repr=False)
    phuong_thuc: str = 'POST'
    duong_dan: str = field(default='/ocr/pdf', repr=False)


@dataclass(frozen=True)
class PhanHoi:
    ma_http: int
    noi_dung: bytes = field(repr=False)
    loai_noi_dung: str
    ma_tuong_quan: str


class _HetHan:
    """Deadline hợp tác với HotFolderPDF, không tạo worker gửi ngầm."""

    def __init__(self, het_luc, dong_ho):
        self.het_luc, self.dong_ho = het_luc, dong_ho

    def con_lai(self):
        con = self.het_luc - self.dong_ho()
        if con <= 0:
            raise TimeoutError
        return con

    def is_set(self):
        self.con_lai()
        return False

    def wait(self, giay):
        time.sleep(min(giay, self.con_lai()))
        return self.is_set()


def _ip(dia_chi):
    dia_chi = ip_address(dia_chi)
    return getattr(dia_chi, 'ipv4_mapped', None) or dia_chi


def _header(headers, ten):
    # Không gộp header trùng; tránh cách diễn giải khác nhau giữa hai tầng.
    values = [v for k, v in headers.items() if k.lower() == ten.lower()]
    return values[0] if len(values) == 1 and isinstance(values[0], str) else ''


def _kiem_cau_hinh(c):
    try:
        if type(c.bat) is not bool:
            raise ValueError
        for ten in ('toi_da_byte', 'toi_da_byte_ra', 'toi_da_ket_noi', 'toi_da_ma'):
            if type(getattr(c, ten)) is not int or getattr(c, ten) <= 0:
                raise ValueError
        if type(c.toi_da_cho) is not int or c.toi_da_cho < 0:
            raise ValueError
        if type(c.cong) is not int or not 1 <= c.cong <= 65535:
            raise ValueError
        for ten in ('toi_da_giay', 'cho_hang_giay', 'doc_giay'):
            value = getattr(c, ten)
            if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                raise ValueError
        if c.bat:
            if (not isinstance(c.khoa, bytes) or not 32 <= len(c.khoa) <= 256
                    or not all(33 <= b <= 126 for b in c.khoa) or not c.ip_core):
                raise ValueError
            for dia_chi in c.ip_core:
                _ip(dia_chi)
    except (TypeError, ValueError, AttributeError):
        raise ValueError('Cấu hình cầu nhận dạng chưa hợp lệ.') from None


class CauNoiABBYY:
    def __init__(self, cau_hinh=None, *, hot_folder=None, ghi_log=None, dong_ho=None):
        self.cau_hinh = c = cau_hinh or CauHinhCauNoi()
        _kiem_cau_hinh(c)
        self._ip_core = frozenset(_ip(x) for x in c.ip_core) if c.bat else frozenset()
        self._hot_folder = hot_folder
        if c.bat and hot_folder is None:
            self._hot_folder = HotFolderPDF(c.thu_muc_hot_folder, bat=True,
                                           cho_toi_da=c.toi_da_giay)
        self._dong_ho = dong_ho or time.monotonic
        self._ghi_log = ghi_log or self._log
        self._khoa = threading.Lock()
        self._xu_ly = threading.Lock()
        self._ma_da_nhan = set()
        self._dang_nhan = 0

    @staticmethod
    def _log(ban_ghi):
        logging.getLogger(__name__).info(json.dumps(ban_ghi, ensure_ascii=False))

    def xu_ly(self, yeu_cau: YeuCau) -> PhanHoi:
        """Xử lý thuần theo transport tiêm; không bind socket hoặc tự gửi lại."""
        c, bat_dau, ma = self.cau_hinh, self._dong_ho(), ''
        da_nhan = da_khoa = False
        phan_hoi = None

        def loi(status, thong_bao):
            return PhanHoi(status, json.dumps({'thong_bao': thong_bao},
                           ensure_ascii=False).encode('utf-8'),
                           'application/json; charset=utf-8', ma)

        try:
            if not c.bat:
                phan_hoi = loi(503, 'Cầu nhận dạng đang tắt.')
                return phan_hoi
            try:
                khoa_gui = _header(yeu_cau.headers, 'Authorization').encode('ascii')
            except UnicodeEncodeError:
                khoa_gui = b''
            dung_khoa = hmac.compare_digest(khoa_gui, b'Bearer ' + c.khoa)
            try:
                dung_ip = _ip(yeu_cau.ket_noi.getpeername()[0]) in self._ip_core
            except (OSError, ValueError, TypeError, IndexError):
                dung_ip = False
            if not (dung_khoa and dung_ip):
                phan_hoi = loi(403, 'Không được phép sử dụng cầu nhận dạng.')
                return phan_hoi
            if yeu_cau.phuong_thuc != 'POST' or yeu_cau.duong_dan != '/ocr/pdf':
                phan_hoi = loi(404, 'Không tìm thấy chức năng yêu cầu.')
                return phan_hoi
            so_byte = _header(yeu_cau.headers, 'Content-Length')
            ma_gui = _header(yeu_cau.headers, 'X-Request-ID')
            try:
                ma_gui = chuan_hoa_ma_tuong_quan(ma_gui, cho_ma_hd=True)
                if not so_byte.isascii() or not so_byte.isdecimal() or len(so_byte) > 12:
                    raise ValueError
                so_byte = int(so_byte)
                if (so_byte <= 0 or any(k.lower() == 'transfer-encoding' for k in yeu_cau.headers)
                        or _header(yeu_cau.headers, 'Content-Type').lower() != 'application/pdf'):
                    raise ValueError
            except (ValueError, TypeError, AttributeError):
                phan_hoi = loi(400, 'Yêu cầu nhận dạng chưa hợp lệ.')
                return phan_hoi
            # KN3 gửi chính mã Core đã cấp sau khi giữ lượt thành công.
            # Phản hồi/log giữ nguyên mã; Hot Folder ánh xạ tên tệp Windows.
            ma = ma_gui
            if so_byte > c.toi_da_byte:
                phan_hoi = loi(413, 'Tài liệu vượt dung lượng cho phép.')
                return phan_hoi
            with self._khoa:
                if ma_gui in self._ma_da_nhan:
                    phan_hoi = loi(409, 'Yêu cầu này đã được tiếp nhận. Cần đối chiếu kết quả trước khi gửi lại.')
                elif self._dang_nhan >= 1 + c.toi_da_cho or len(self._ma_da_nhan) >= c.toi_da_ma:
                    phan_hoi = loi(503, 'Cầu nhận dạng đang đầy. Vui lòng thử lại sau.')
                else:
                    self._ma_da_nhan.add(ma_gui)
                    self._dang_nhan += 1
                    da_nhan = True
            if phan_hoi is not None:
                return phan_hoi
            han = _HetHan(bat_dau + c.toi_da_giay, self._dong_ho)
            raw = bytearray()
            doc = getattr(yeu_cau.luong, 'read1', None) or yeu_cau.luong.read
            while len(raw) < so_byte:
                yeu_cau.ket_noi.settimeout(min(c.doc_giay, han.con_lai()))
                phan = doc(min(64 * 1024, so_byte - len(raw)))
                han.con_lai()
                if not isinstance(phan, bytes) or not phan or len(phan) > so_byte - len(raw):
                    phan_hoi = loi(400, 'Chưa nhận đủ tài liệu hợp lệ.')
                    return phan_hoi
                raw.extend(phan)
            if not raw.startswith(b'%PDF-') or not raw.rstrip().endswith(b'%%EOF'):
                phan_hoi = loi(400, 'Tài liệu PDF chưa hợp lệ.')
                return phan_hoi
            da_khoa = self._xu_ly.acquire(timeout=min(c.cho_hang_giay, han.con_lai()))
            if not da_khoa:
                raise TimeoutError
            han.con_lai()
            tham_so = dict(huy=han, toi_da_byte_ra=c.toi_da_byte_ra)
            if isinstance(self._hot_folder, HotFolderPDF):
                tham_so['ma_tuong_quan'] = ma
            # Backend tiêm theo seam cũ vẫn dùng nguyên chữ ký trước đây.
            ket_qua = self._hot_folder.doc_pdf(bytes(raw), 'pdf', **tham_so)
            try:
                han.con_lai()
            except TimeoutError:
                try:
                    self._ghi_log(dict(ma_tuong_quan=ma, ket_qua='kết quả muộn',
                                       thoi_gian_giay=round(max(0, self._dong_ho() - bat_dau), 3),
                                       so_trang=None))
                except Exception:
                    pass
                raise
            if (not isinstance(ket_qua, bytes) or len(ket_qua) > c.toi_da_byte_ra
                    or not ket_qua.startswith(b'%PDF-') or not ket_qua.rstrip().endswith(b'%%EOF')):
                phan_hoi = loi(502, 'Chưa nhận được kết quả nhận dạng hợp lệ.')
            else:
                phan_hoi = PhanHoi(200, ket_qua, 'application/pdf', ma)
            return phan_hoi
        except TimeoutError:
            phan_hoi = loi(504, 'Đã quá thời gian chờ nhận dạng. Cần đối chiếu trước khi gửi lại.')
            return phan_hoi
        except Exception as exc:
            # Không str(exc), traceback, header hoặc đường dẫn trong phản hồi/log.
            if getattr(exc, 'code', None) == 'OCR_QUA_GIO':
                phan_hoi = loi(504, 'Đã quá thời gian chờ nhận dạng. Cần đối chiếu trước khi gửi lại.')
            else:
                phan_hoi = loi(502, 'Không hoàn tất nhận dạng tài liệu. Cần đối chiếu kết quả.')
            return phan_hoi
        finally:
            if da_khoa:
                self._xu_ly.release()
            if da_nhan:
                with self._khoa:
                    self._dang_nhan -= 1
            try:
                self._ghi_log({'ma_tuong_quan': ma,
                               'ket_qua': phan_hoi.ma_http if phan_hoi else 502,
                               'thoi_gian_giay': round(max(0, self._dong_ho() - bat_dau), 3),
                               'so_trang': None})
            except Exception:
                pass  # Lỗi nơi nhận log không làm phát tán dữ liệu hoặc gửi lại OCR.


class _DocHTTP:
    """Giới hạn tổng thời gian đọc header, kể cả kết nối nhỏ giọt."""

    def __init__(self, luong, ket_noi, han):
        self.luong, self.ket_noi, self.han = luong, ket_noi, han
        self.dem = bytearray()

    def readline(self, limit=65537):
        while True:
            con = self.han.con_lai()
            n = self.dem.find(b'\n') + 1
            if n or len(self.dem) >= limit:
                n = min(n or len(self.dem), limit)
                raw = bytes(self.dem[:n])
                del self.dem[:n]
                return raw
            self.ket_noi.settimeout(con)
            raw = self.luong.read1(min(4096, limit - len(self.dem)))
            if not raw:
                raw = bytes(self.dem)
                self.dem.clear()
                return raw
            self.dem.extend(raw)

    def read1(self, n):
        if self.dem:
            raw = bytes(self.dem[:n])
            del self.dem[:n]
            return raw
        return self.luong.read1(n)

    def close(self):
        self.luong.close()


class _XuLyHTTP(BaseHTTPRequestHandler):
    # HTTP/1.0 + đóng kết nối: không tái sử dụng phần body bị từ chối/chưa đọc.
    def setup(self):
        super().setup()
        c = self.server.cau_noi.cau_hinh
        self.rfile = _DocHTTP(self.rfile, self.connection,
                             _HetHan(time.monotonic() + c.doc_giay, time.monotonic))

    def do_POST(self):
        phan_hoi = self.server.cau_noi.xu_ly(YeuCau(
            self.connection, self.headers, self.rfile, self.command, self.path))
        self.close_connection = True
        self.connection.settimeout(self.server.cau_noi.cau_hinh.doc_giay)
        self.send_response_only(phan_hoi.ma_http)
        self.send_header('Content-Type', phan_hoi.loai_noi_dung)
        self.send_header('Content-Length', str(len(phan_hoi.noi_dung)))
        self.send_header('X-Correlation-ID', phan_hoi.ma_tuong_quan)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(phan_hoi.noi_dung)

    def send_error(self, code, message=None, explain=None):
        # Parser của stdlib có thể nhận URL/header ác ý trong message.
        self.close_connection = True
        raw = 'Yêu cầu nhận dạng chưa hợp lệ.'.encode('utf-8')
        self.send_response_only(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format, *args):
        pass

    def handle_expect_100(self):
        self.send_error(417)
        return False


class _MayChuHTTPS(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, cau_noi):
        self.cau_noi = cau_noi
        c = cau_noi.cau_hinh
        self._ket_noi = threading.BoundedSemaphore(c.toi_da_ket_noi)
        self.request_queue_size = c.toi_da_ket_noi
        super().__init__((c.dia_chi, c.cong), _XuLyHTTP)

    def get_request(self):
        ket_noi, dia_chi = super().get_request()
        try:
            if _ip(ket_noi.getpeername()[0]) not in self.cau_noi._ip_core:
                raise OSError
            ket_noi.settimeout(self.cau_noi.cau_hinh.doc_giay)
            ket_noi = self.cau_noi.cau_hinh.tls.wrap_socket(ket_noi, server_side=True)
            return ket_noi, dia_chi
        except Exception:
            ket_noi.close()
            raise OSError('Không thiết lập được kết nối bảo mật.') from None

    def process_request(self, request, client_address):
        if not self._ket_noi.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self._ket_noi.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._ket_noi.release()

    def handle_error(self, request, client_address):
        pass  # Tắt traceback mặc định của socketserver.


def chay(cau_hinh: CauHinhCauNoi):
    """Chỉ bootstrap gọi tường minh; SSLContext/chứng thư do vận hành cấp."""
    _kiem_cau_hinh(cau_hinh)
    if not cau_hinh.bat:
        return None
    if (not isinstance(cau_hinh.tls, ssl.SSLContext)
            or cau_hinh.tls.protocol != ssl.PROTOCOL_TLS_SERVER
            or cau_hinh.tls.minimum_version < ssl.TLSVersion.TLSv1_2):
        raise ValueError('Cần cấu hình chứng thư và kết nối bảo mật hợp lệ.')
    cau_noi = CauNoiABBYY(cau_hinh)
    may_chu = _MayChuHTTPS(cau_noi)
    try:
        may_chu.serve_forever()
    finally:
        may_chu.server_close()
