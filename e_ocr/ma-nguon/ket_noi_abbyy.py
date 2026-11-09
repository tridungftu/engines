"""KN3: client HTTPS do Core tiêm cấu hình/khóa/CA trong RAM, mặc định tắt.

Chỉ vận chuyển PDF, không giữ/hoàn trang, không tự gửi lại. san_sang() chỉ
kiểm cấu hình cục bộ; không chứng minh máy ABBYY đang chạy. KN4 phải đọc
chua_ro_da_nhan trước khi quyết định hoàn hạn mức hoặc gửi lại.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import http.client
from ipaddress import ip_address
import math
import re
import socket
import ssl
import threading
import time
from uuid import uuid4

from .lib.cong_ocr import chuan_hoa_ma_tuong_quan
from ...sdk_core.ngu_canh import _xoa_loi
from ...sdk_core.primitives import DataError


@dataclass(frozen=True)
class CauHinhKetNoi:
    bat: bool = False
    may_chu: str = field(default='', repr=False)
    cong: int = 9443
    khoa: bytes = field(default=b'', repr=False)
    tls: object = field(default=None, repr=False)
    ket_noi_giay: float = 10.0
    doc_giay: float = 310.0
    toi_da_giay: float = 330.0
    toi_da_byte: int = 20 * 1024**2
    toi_da_byte_ra: int = 40 * 1024**2


_THONG_BAO = {
    'ABBYY_CAU_HINH': 'Cấu hình kết nối nhận dạng chưa hợp lệ.',
    'ABBYY_KHONG_KET_NOI': 'Không kết nối được máy nhận dạng.',
    'ABBYY_CHUNG_THU': 'Không xác minh được chứng thư máy nhận dạng.',
    'OCR_QUA_GIO': 'Đã quá thời gian chờ máy nhận dạng.',
    'OCR_HUY': 'Đã hủy nhận dạng tài liệu.',
    'OCR_DINH_DANG': 'Kết nối này chỉ nhận tài liệu PDF hợp lệ.',
    'OCR_KICH_THUOC': 'Tài liệu vượt dung lượng cho phép.',
    'ABBYY_KHOA_SAI': 'Khóa kết nối nhận dạng không hợp lệ.',
    'ABBYY_KHOA_HOAC_IP': 'Khóa hoặc địa chỉ máy chủ chưa được phép kết nối.',
    'ABBYY_PHAN_HOI_SAI': 'Máy nhận dạng trả kết quả không hợp lệ.',
    'ABBYY_PHAN_HOI_QUA_CO': 'Kết quả nhận dạng vượt dung lượng cho phép.',
    'ABBYY_CHUA_RO_DA_NHAN': 'Chưa rõ máy nhận dạng đã nhận tài liệu; cần đối chiếu trước khi gửi lại.',
    'ABBYY_YEU_CAU_TRUNG': 'Yêu cầu đã được tiếp nhận; cần đối chiếu kết quả.',
    'ABBYY_BAN': 'Máy nhận dạng chưa thể nhận thêm tài liệu.',
    'ABBYY_LOI_XU_LY': 'Máy nhận dạng chưa hoàn tất xử lý; cần đối chiếu kết quả.',
}


class LoiKetNoiABBYY(DataError):
    """Mã hữu hạn và trạng thái tiếp nhận cho Core, không mang lỗi/header gốc."""

    def __init__(self, ma, *, ma_yeu_cau=None, chua_ro_da_nhan=False, nguyen_nhan=None):
        super().__init__(ma, _THONG_BAO[ma])
        self.ma = ma
        self.ma_yeu_cau = ma_yeu_cau
        self.chua_ro_da_nhan = chua_ro_da_nhan
        self.nguyen_nhan = nguyen_nhan or ma


def _hop_le(c):
    try:
        if type(c.bat) is not bool or type(c.cong) is not int or not 1 <= c.cong <= 65535:
            return False
        for ten in ('ket_noi_giay', 'doc_giay', 'toi_da_giay'):
            v = getattr(c, ten)
            if isinstance(v, bool) or not math.isfinite(v) or v <= 0:
                return False
        for ten in ('toi_da_byte', 'toi_da_byte_ra'):
            if type(getattr(c, ten)) is not int or getattr(c, ten) <= 0:
                return False
        if not c.bat:
            return True
        if (not isinstance(c.khoa, bytes) or not 32 <= len(c.khoa) <= 256
                or not all(33 <= b <= 126 for b in c.khoa)
                or not isinstance(c.may_chu, str) or not c.may_chu):
            return False
        if ':' in c.may_chu:
            if '%' in c.may_chu or ip_address(c.may_chu).version != 6:
                return False
        elif not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?', c.may_chu):
            return False
        return (isinstance(c.tls, ssl.SSLContext) and c.tls.check_hostname
                and c.tls.verify_mode == ssl.CERT_REQUIRED
                and c.tls.minimum_version >= ssl.TLSVersion.TLSv1_2)
    except (AttributeError, ValueError, TypeError):
        return False


class KetNoiABBYY:
    def __init__(self, cau_hinh=None):
        self._c = cau_hinh if cau_hinh is not None else CauHinhKetNoi()
        if not _hop_le(self._c):
            raise LoiKetNoiABBYY('ABBYY_CAU_HINH')

    def san_sang(self):
        return self._c.bat is True and _hop_le(self._c)

    def doc_pdf(self, raw, duoi='pdf', *, huy=None, ma_yeu_cau=None):
        """Một POST duy nhất; nhận mã Core ocr:<hex> hoặc UUID của seam cũ.

        Header và metadata giữ nguyên mã Core ocr:<32 hex> để đối chiếu.

        Hủy hợp tác giữa các khối, kèm luồng chỉ đóng socket để ngắt I/O
        khi chờ. Luồng này không gửi dữ liệu. Phân giải DNS do hệ điều hành
        quản lý; hủy trong DNS được nhận ngay khi connect trả quyền.
        """
        c = self._c
        ket_noi = phan_hoi = luong_huy = socket_tls = None
        dung = threading.Event()
        da_huy = threading.Event()
        da_het_han = threading.Event()
        da_gui = False
        ma = None
        loi = None
        ket_qua = None
        het_luc = time.monotonic() + c.toi_da_giay

        def bao_loi(code, *, chua_ro=None, nguyen_nhan=None):
            raise LoiKetNoiABBYY(code, ma_yeu_cau=ma,
                                 chua_ro_da_nhan=da_gui if chua_ro is None else chua_ro,
                                 nguyen_nhan=nguyen_nhan)

        def kiem():
            if da_huy.is_set() or (huy is not None and huy.is_set()):
                bao_loi('OCR_HUY')
            con = het_luc - time.monotonic()
            if da_het_han.is_set() or con <= 0:
                raise TimeoutError
            return con

        def dat_han(giay):
            han = min(giay, kiem())
            ket_noi.timeout = han
            sock = ket_noi.sock if ket_noi.sock is not None else socket_tls
            if sock is not None:
                sock.settimeout(han)

        def canh_huy():
            while not dung.wait(0.05):
                try:
                    if huy is not None and huy.is_set():
                        da_huy.set()
                    elif time.monotonic() >= het_luc:
                        da_het_han.set()
                    else:
                        continue
                    sock = ket_noi.sock if ket_noi.sock is not None else socket_tls
                    if sock is not None:
                        try:
                            sock.shutdown(socket.SHUT_RDWR)
                        finally:
                            sock.close()
                    return
                except Exception as exc:
                    # Callback hủy/socket có thể chứa bí mật trong lỗi gốc.
                    if not da_het_han.is_set():
                        da_huy.set()
                    _xoa_loi(exc)
                    return

        try:
            kiem()
            if not self.san_sang():
                bao_loi('ABBYY_KHONG_KET_NOI', chua_ro=False)
            if (not isinstance(duoi, str) or duoi.lower().lstrip('.') != 'pdf'
                    or not isinstance(raw, bytes) or not raw.startswith(b'%PDF-')
                    or not raw.rstrip().endswith(b'%%EOF')):
                bao_loi('OCR_DINH_DANG', chua_ro=False)
            if len(raw) > c.toi_da_byte:
                bao_loi('OCR_KICH_THUOC', chua_ro=False)
            try:
                ma = chuan_hoa_ma_tuong_quan(uuid4() if ma_yeu_cau is None else ma_yeu_cau)
            except (ValueError, TypeError, AttributeError):
                bao_loi('ABBYY_CAU_HINH', chua_ro=False)
            # http.client không dùng proxy từ env, không redirect, không retry.
            ket_noi = http.client.HTTPSConnection(c.may_chu, c.cong,
                                                  timeout=min(c.ket_noi_giay, kiem()),
                                                  context=c.tls)
            ket_noi.set_debuglevel(0)
            luong_huy = threading.Thread(target=canh_huy, daemon=True)
            luong_huy.start()
            ket_noi.connect()
            socket_tls = ket_noi.sock
            kiem()
            # Kiểm lại context được tiêm để từ chối thay đổi trước lúc gửi khóa.
            if not self.san_sang():
                bao_loi('ABBYY_CAU_HINH', chua_ro=False)
            ket_noi.putrequest('POST', '/ocr/pdf', skip_accept_encoding=True)
            ket_noi.putheader('Authorization', 'Bearer ' + c.khoa.decode('ascii'))
            ket_noi.putheader('Content-Type', 'application/pdf')
            ket_noi.putheader('Content-Length', str(len(raw)))
            ket_noi.putheader('X-Request-ID', ma)
            ket_noi.putheader('Connection', 'close')
            dat_han(c.doc_giay)
            # sendall có thể gửi một phần rồi lỗi: không chứng minh chưa nhận.
            da_gui = True
            ket_noi.endheaders()
            for i in range(0, len(raw), 64 * 1024):
                dat_han(c.doc_giay)
                ket_noi.send(raw[i:i + 64 * 1024])
            dat_han(c.doc_giay)
            phan_hoi = ket_noi.getresponse()
            kiem()
            status = phan_hoi.status
            if status != 200:
                code = {401: 'ABBYY_KHOA_SAI', 403: 'ABBYY_KHOA_HOAC_IP',
                        409: 'ABBYY_YEU_CAU_TRUNG', 413: 'OCR_KICH_THUOC',
                        503: 'ABBYY_BAN', 504: 'ABBYY_CHUA_RO_DA_NHAN',
                        502: 'ABBYY_LOI_XU_LY'}.get(status, 'ABBYY_PHAN_HOI_SAI')
                bao_loi(code, chua_ro=status not in (400, 401, 403, 404, 413, 503),
                         nguyen_nhan='OCR_QUA_GIO' if status == 504 else None)
            headers = phan_hoi.getheaders()

            def header(ten):
                values = [v for k, v in headers if k.lower() == ten]
                if len(values) > 1 or any(not isinstance(v, str) for v in values):
                    bao_loi('ABBYY_PHAN_HOI_SAI')
                return values[0].strip().lower() if values else ''

            if (header('content-type').split(';')[0].strip() != 'application/pdf'
                    or header('content-encoding') not in ('', 'identity')):
                bao_loi('ABBYY_PHAN_HOI_SAI')
            do_dai = header('content-length')
            chuyen = header('transfer-encoding')
            if chuyen not in ('', 'chunked') or (chuyen and do_dai):
                bao_loi('ABBYY_PHAN_HOI_SAI')
            if do_dai:
                if not do_dai.isascii() or not do_dai.isdecimal() or len(do_dai) > 12:
                    bao_loi('ABBYY_PHAN_HOI_SAI')
                do_dai = int(do_dai)
                if do_dai > c.toi_da_byte_ra:
                    bao_loi('ABBYY_PHAN_HOI_QUA_CO')
            else:
                do_dai = None
            result = bytearray()
            while True:
                dat_han(c.doc_giay)
                phan = phan_hoi.read1(min(64 * 1024, c.toi_da_byte_ra + 1 - len(result)))
                kiem()
                if not isinstance(phan, bytes):
                    bao_loi('ABBYY_PHAN_HOI_SAI')
                if not phan:
                    break
                result.extend(phan)
                if len(result) > c.toi_da_byte_ra:
                    bao_loi('ABBYY_PHAN_HOI_QUA_CO')
            if do_dai is not None and len(result) != do_dai:
                bao_loi('ABBYY_CHUA_RO_DA_NHAN', nguyen_nhan='ABBYY_PHAN_HOI_SAI')
            if not result.startswith(b'%PDF-') or not result.rstrip().endswith(b'%%EOF'):
                bao_loi('ABBYY_PHAN_HOI_SAI')
            ket_qua = bytes(result)
        except Exception as exc:
            try:
                if huy is not None and huy.is_set():
                    da_huy.set()
            except Exception as loi_huy:
                da_huy.set()
                _xoa_loi(loi_huy)
            if isinstance(exc, LoiKetNoiABBYY):
                loi = (exc.code, exc.chua_ro_da_nhan, exc.nguyen_nhan)
            else:
                if da_huy.is_set():
                    code = 'OCR_HUY'
                elif da_het_han.is_set():
                    code = 'OCR_QUA_GIO'
                elif isinstance(exc, ssl.SSLError):
                    code = 'ABBYY_CHUNG_THU'
                elif isinstance(exc, TimeoutError):
                    code = 'OCR_QUA_GIO'
                elif isinstance(exc, (OSError, http.client.HTTPException)):
                    code = 'ABBYY_KHONG_KET_NOI'
                else:
                    code = 'ABBYY_PHAN_HOI_SAI'
                loi = ('ABBYY_CHUA_RO_DA_NHAN' if da_gui and code != 'OCR_HUY' else code,
                       da_gui, code)
            _xoa_loi(exc)
        finally:
            dung.set()
            if luong_huy is not None and luong_huy.ident is not None:
                luong_huy.join()
            for obj in (phan_hoi, ket_noi):
                if obj is not None:
                    try:
                        obj.close()
                    except Exception as exc:
                        _xoa_loi(exc)
        if loi is not None:
            raise LoiKetNoiABBYY(loi[0], ma_yeu_cau=ma,
                                 chua_ro_da_nhan=loi[1], nguyen_nhan=loi[2]) from None
        return ket_qua
