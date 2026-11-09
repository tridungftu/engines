"""Mở/đóng cầu nối KN2 tạm trên máy hiện tại; không khởi động ABBYY.

Chạy mo --chay-kho để xem các bước. Khi mở thật, cần --ip-core, --ket,
--chung-thu, --khoa-tls, --hot-folder; --dia-chi mặc định 127.0.0.1,
--gio mặc định 8. Các tham số còn thiếu được nhập trong cửa sổ tương tác.
Chứng thư do vận hành cấp trước; không tự đổi mạng/tường lửa hay cấp TLS.
Khóa chỉ đi vào KetBiMat và stdin pipe của tiến trình KN2, không args/env.
Không dò/đọc Hot Folder lúc mở. Core chưa được nối để gửi tài liệu thật.
"""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime
from ipaddress import ip_address, ip_network
import json
import logging
import math
import os
from pathlib import Path
import queue
import secrets
import ssl
import subprocess
import sys
import threading
import time
from uuid import uuid4

sys.dont_write_bytecode = True
GOC = Path(__file__).resolve().parents[1]
# Đường dẫn có dấu nằm trong Python; launcher .cmd chỉ có ASCII.
PHU_THUOC = Path('D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/'
                'var/app-runtime/app-runtime-20261019-092310-807/deps')
sys.path.insert(0, str(GOC / 'src'))
sys.path.insert(1, str(PHU_THUOC))

from kho_tri_thuc.core import bi_mat, kenh_bi_mat
from kho_tri_thuc.sdk_core.bootstrap import PROTOCOL, doc_thong_diep, gui_thong_diep

TRANG_THAI = GOC / 'var' / 'abbyy-ket-noi-tam.json'
LOG = logging.getLogger('abbyy_ket_noi_tam')


class LoiKetNoi(RuntimeError):
    """Chỉ chứa câu cố định, không chứa ngoại lệ phụ thuộc hay khóa."""


class TienTrinhWindows:
    """Giữ HANDLE khi so thời điểm tạo và dừng, tránh PID tái sử dụng."""

    def __init__(self):
        if sys.platform != 'win32':
            raise LoiKetNoi('Chỉ mở kết nối tạm trên máy Windows đã chuẩn bị.')
        import ctypes as ct
        from ctypes import wintypes as wt
        self.ct, self.wt = ct, wt
        self.api = a = ct.WinDLL('kernel32', use_last_error=True)
        for ham, ra, vao in (
            (a.OpenProcess, wt.HANDLE, (wt.DWORD, wt.BOOL, wt.DWORD)),
            (a.CloseHandle, wt.BOOL, (wt.HANDLE,)),
            (a.GetProcessTimes, wt.BOOL, (wt.HANDLE, *([ct.POINTER(wt.FILETIME)] * 4))),
            (a.WaitForSingleObject, wt.DWORD, (wt.HANDLE, wt.DWORD)),
            (a.TerminateProcess, wt.BOOL, (wt.HANDLE, wt.UINT)),
        ):
            ham.restype, ham.argtypes = ra, vao

    @contextmanager
    def _handle(self, pid, *, dung=False):
        # QUERY_LIMITED_INFORMATION | SYNCHRONIZE | (PROCESS_TERMINATE).
        h = self.api.OpenProcess(0x1000 | 0x100000 | int(dung), False, pid)
        if not h:
            if self.ct.get_last_error() == 87:  # PID không tồn tại.
                yield None
                return
            raise LoiKetNoi('Không kiểm tra được tiến trình kết nối tạm.')
        try:
            yield h
        finally:
            self.api.CloseHandle(h)

    def _danh_tinh(self, h):
        doi = self.api.WaitForSingleObject(h, 0)
        if doi == 0:
            return None
        if doi != 258:
            raise LoiKetNoi('Không kiểm tra được tiến trình kết nối tạm.')
        cac_moc = [self.wt.FILETIME() for _ in range(4)]
        if not self.api.GetProcessTimes(h, *(self.ct.byref(x) for x in cac_moc)):
            raise LoiKetNoi('Không xác minh được tiến trình kết nối tạm.')
        return str((cac_moc[0].dwHighDateTime << 32) | cac_moc[0].dwLowDateTime)

    def danh_tinh(self, pid):
        with self._handle(pid) as h:
            return self._danh_tinh(h) if h else None

    def dung(self, pid, tao_luc):
        with self._handle(pid, dung=True) as h:
            if not h:
                return
            that = self._danh_tinh(h)
            if that is None:
                return
            if that != tao_luc:
                raise LoiKetNoi('Tiến trình đã thay đổi. Cần kiểm tra trước khi đóng.')
            if (not self.api.TerminateProcess(h, 0)
                    or self.api.WaitForSingleObject(h, 10_000) != 0):
                raise LoiKetNoi('Chưa dừng được kết nối tạm. Cần thử đóng lại.')


@contextmanager
def _khoa(tep, *, doi_khoa=False):
    """Khóa bền cùng tệp trạng thái; không xóa lock sau khi dùng."""
    tep.parent.mkdir(parents=True, exist_ok=True)
    with tep.with_suffix('.lock').open('a+b') as f:
        f.seek(0, os.SEEK_END)
        if f.tell() == 0:
            f.write(b'0')
            f.flush()
        f.seek(0)
        if os.name == 'nt':
            import msvcrt

            def nhan():
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)

            def tra():
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            def nhan():
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

            def tra():
                fcntl.flock(f, fcntl.LOCK_UN)
        han = time.monotonic() + 25
        while True:
            try:
                nhan()
                break
            except OSError:
                if not doi_khoa or time.monotonic() >= han:
                    raise LoiKetNoi('Đang có thao tác kết nối tạm. Cần thử lại sau.') from None
                time.sleep(0.05)
        try:
            yield
        finally:
            tra()


def _doc(tep):
    try:
        with tep.open('r', encoding='utf-8') as f:
            raw = f.read(16_385)
    except FileNotFoundError:
        return None
    s = json.loads(raw)
    if (len(raw) > 16_384 or not isinstance(s, dict)
            or s.get('phien_ban') != 1
            or s.get('trang_thai') not in ('dang-mo', 'dang-chuan-bi', 'da-dong', 'het-han')
            or not isinstance(s.get('phien'), str) or len(s['phien']) != 32
            or any(c not in '0123456789abcdef' for c in s['phien'])
            or s.get('ten_khoa') != 'abbyy-tam-' + s['phien']
            or not isinstance(s.get('ket'), str) or not Path(s['ket']).is_absolute()
            or type(s.get('can_thu_hoi')) is not bool
            or not isinstance(s.get('het_luc'), (int, float))
            or not math.isfinite(s['het_luc'])
            or (s.get('pid') is not None and (type(s['pid']) is not int or s['pid'] <= 0))
            or (s.get('pid') is not None and
                (not isinstance(s.get('tao_luc'), str) or not s['tao_luc'].isdigit()))):
        raise LoiKetNoi('Trạng thái kết nối tạm chưa hợp lệ. Cần kiểm tra lại.')
    return s


def _ghi(tep, s):
    # Các bên đọc/ghi giữ cùng lock. Ghi lại trạng thái, không xóa tệp.
    tep.write_text(json.dumps(s, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _nhat_ky(tep):
    logging.basicConfig(filename=tep.with_suffix('.log'), encoding='utf-8',
                        level=logging.INFO, format='%(asctime)s %(name)s %(message)s')


def _ip_noi_bo(value):
    ip = ip_address(value)
    ip = getattr(ip, 'ipv4_mapped', None) or ip
    tailscale = ip.version == 4 and ip in ip_network('100.64.0.0/10')
    if (not (ip.is_private or tailscale) or ip.is_unspecified
            or ip.is_multicast or ip.is_reserved):
        raise LoiKetNoi('Chỉ sử dụng địa chỉ IP nội bộ cụ thể.')
    return str(ip)


def _kiem_ket(duong):
    path = kenh_bi_mat.kiem_thu_muc(duong)
    if (path == GOC or GOC in path.parents or not path.is_dir()
            or not kenh_bi_mat.kiem_acl(path)):
        raise LoiKetNoi('Cần thư mục két có sẵn ngoài mã nguồn, đúng quyền tài khoản Core.')
    return path


def _cau_hinh(args):
    for ten, cau in (
        ('ip_core', 'Địa chỉ IP máy chủ Core: '),
        ('ket', 'Thư mục két hiện có của Core: '),
        ('chung_thu', 'Tệp chứng thư kết nối bảo mật: '),
        ('khoa_tls', 'Tệp khóa riêng của chứng thư: '),
        ('hot_folder', 'Thư mục nhận dạng đã được chuẩn bị: '),
    ):
        if not getattr(args, ten):
            if not sys.stdin.isatty():
                raise LoiKetNoi('Cần cung cấp IP Core, két, chứng thư và thư mục nhận dạng.')
            setattr(args, ten, input(cau).strip().strip('"'))
    if not math.isfinite(args.gio) or args.gio <= 0 or not 1 <= args.cong <= 65535:
        raise LoiKetNoi('Thời hạn và cổng kết nối chưa hợp lệ.')
    ket = _kiem_ket(args.ket)
    # Chỉ nhận đường dẫn Hot Folder, tuyệt đối không dò nội dung lúc mở.
    hot = Path(args.hot_folder)
    if not hot.is_absolute():
        raise LoiKetNoi('Cần đường dẫn đầy đủ đến thư mục nhận dạng đã chuẩn bị.')
    c = dict(ip_core=_ip_noi_bo(args.ip_core), dia_chi=_ip_noi_bo(args.dia_chi),
             cong=args.cong, chung_thu=args.chung_thu, khoa_tls=args.khoa_tls,
             hot_folder=str(hot))
    _tls(c)  # Chứng thư phải dùng được trước khi sinh/lưu khóa.
    return ket, c


def _tls(c):
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.minimum_version = ssl.TLSVersion.TLSv1_2
    # Khóa TLS có mật khẩu: từ chối, không chờ nhập ngầm trong tiến trình con.
    tls.load_cert_chain(c['chung_thu'], c['khoa_tls'], password=lambda: '')
    return tls


def _tao_tien_trinh():
    return subprocess.Popen(
        [sys.executable, '-X', 'utf8', '-B', str(Path(__file__).resolve()), '--phuc-vu'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        cwd=GOC, close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW)


def _cap_cho_con(p, s, c, khoa, tep):
    gui_thong_diep(p.stdin, {'protocol': PROTOCOL, 'kieu': 'abbyy_tam',
                            'du_lieu': {'trang_thai': s, 'cau_hinh': c, 'tep': str(tep)}})
    bi_mat.gui_cho_con(p, khoa)
    p.stdin.close()
    hang = queue.Queue(maxsize=1)

    def doc_san_sang():
        try:
            hang.put(p.stdout.readline(64))
        except Exception:
            hang.put(b'')

    threading.Thread(target=doc_san_sang, daemon=True).start()
    try:
        if hang.get(timeout=20) not in (b'SAN_SANG\n', b'SAN_SANG\r\n'):
            raise LoiKetNoi('Chưa mở được kết nối bảo mật. Cần kiểm tra cấu hình.')
    except queue.Empty:
        raise LoiKetNoi('Quá thời gian chờ mở kết nối tạm.') from None


def _thu_hoi(s, ket_factory):
    if s['can_thu_hoi']:
        path = _kiem_ket(s['ket'])
        # Phiên có thể bị ngắt trước luu(), hoặc sau rename nhưng trước ghi
        # trạng thái. Tên cũ đã vắng thì không còn khóa để cấp theo tên đó.
        if _co_tep_khoa(path, s['ten_khoa']):
            ket_factory(path).thu_hoi(s['ten_khoa'])
        else:
            LOG.info('Khóa của phiên không còn được cấp theo tên cũ.')
        s['can_thu_hoi'] = False


def mo(args, *, tep=TRANG_THAI, ket_factory=None, tien_trinh=None):
    ket_factory = ket_factory or bi_mat.KetBiMat
    duong_ket, c = _cau_hinh(args)
    tt = tien_trinh or TienTrinhWindows()
    with _khoa(tep):
        cu = _doc(tep)
        if cu and (cu['can_thu_hoi'] or cu['pid'] is not None):
            raise LoiKetNoi('Cần đóng phiên kết nối tạm trước khi mở phiên mới.')
        _nhat_ky(tep)
        phien = uuid4().hex
        s = dict(phien_ban=1, phien=phien, trang_thai='dang-chuan-bi',
                 pid=None, tao_luc=None, ket=str(duong_ket), ten_khoa='abbyy-tam-' + phien,
                 can_thu_hoi=False, het_luc=time.time() + args.gio * 3600)
        if not math.isfinite(s['het_luc']):
            raise LoiKetNoi('Thời hạn kết nối chưa hợp lệ.')
        ket = ket_factory(duong_ket)
        khoa = bi_mat.BiMat(secrets.token_urlsafe(48).encode('ascii'))
        p = None
        try:
            # Ghi dấu trước khi lưu: nếu bị ngắt, dong còn tên để thu hồi.
            s['can_thu_hoi'] = True
            _ghi(tep, s)
            ket.luu(s['ten_khoa'], khoa)
            target = duong_ket / (s['ten_khoa'] + '.dpapi')
            kenh_bi_mat.dat_acl(target)
            if not kenh_bi_mat.kiem_acl(target):
                raise LoiKetNoi('Chưa bảo đảm quyền tệp khóa trong két.')
            p = _tao_tien_trinh()
            s['pid'], s['tao_luc'] = p.pid, tt.danh_tinh(p.pid)
            if s['tao_luc'] is None:
                raise LoiKetNoi('Tiến trình kết nối tạm đã dừng khi khởi động.')
            _ghi(tep, s)
            _cap_cho_con(p, s, c, khoa, tep)
            if time.time() >= s['het_luc'] or tt.danh_tinh(p.pid) != s['tao_luc']:
                raise LoiKetNoi('Phiên kết nối đã dừng hoặc hết hạn khi khởi động.')
            s['trang_thai'] = 'dang-mo'
            _ghi(tep, s)
            LOG.info('Đã mở kết nối nhận dạng tạm.')
        except BaseException:
            # Popen giữ HANDLE của đúng tiến trình vừa tạo, kể cả khi chưa có identity.
            if p is not None:
                p.terminate()
                p.wait(timeout=10)
            s['pid'], s['tao_luc'] = None, None
            # Không bỏ dấu thu hồi nếu ghi két/thu hồi chưa hoàn tất.
            if _co_tep_khoa(duong_ket, s['ten_khoa']):
                _thu_hoi(s, ket_factory)
            else:
                s['can_thu_hoi'] = False
            s['trang_thai'] = 'da-dong'
            _ghi(tep, s)
            LOG.warning('Mở kết nối nhận dạng tạm thất bại; đã đóng.')
            raise
        finally:
            khoa = None
            if p is not None:
                if p.stdin and not p.stdin.closed:
                    p.stdin.close()
                if p.stdout:
                    p.stdout.close()
    print('Đã mở kết nối nhận dạng tạm. Tự đóng lúc '
          + datetime.fromtimestamp(s['het_luc']).strftime('%d/%m/%Y %H:%M:%S') + '.')
    return 0


def _co_tep_khoa(duong_ket, ten):
    # Chỉ kiểm tệp của phiên vừa tạo; không đọc/giải mã hay quét két.
    return (duong_ket / (ten + '.dpapi')).exists()


def dong(*, tep=TRANG_THAI, ket_factory=None, tien_trinh=None):
    if not tep.exists():
        print('Chưa có phiên kết nối nhận dạng tạm.')
        return 0
    with _khoa(tep):
        s = _doc(tep)
        _nhat_ky(tep)
        if s['pid'] is not None:
            (tien_trinh or TienTrinhWindows()).dung(s['pid'], s['tao_luc'])
            s['pid'], s['tao_luc'] = None, None
            _ghi(tep, s)  # Thu hồi lỗi vẫn có thể chạy dong lại.
        _thu_hoi(s, ket_factory or bi_mat.KetBiMat)
        s['trang_thai'] = 'da-dong'
        _ghi(tep, s)
        LOG.info('Đã đóng kết nối nhận dạng tạm và thu hồi khóa.')
    print('Đã đóng kết nối nhận dạng tạm và thu hồi khóa.')
    return 0


def trang_thai(*, tep=TRANG_THAI, tien_trinh=None):
    if not tep.exists():
        print('Chưa có phiên kết nối nhận dạng tạm.')
        return 0
    with _khoa(tep):
        s = _doc(tep)
    if s['pid'] is None:
        print('Kết nối nhận dạng tạm đã đóng.' if not s['can_thu_hoi']
              else 'Kết nối chưa hoàn tất. Cần chạy đóng để thu hồi khóa.')
    else:
        that = (tien_trinh or TienTrinhWindows()).danh_tinh(s['pid'])
        if that != s['tao_luc']:
            print('Phiên kết nối tạm không còn hoạt động. Cần chạy đóng để đối chiếu khóa.')
        elif time.time() >= s['het_luc']:
            print('Kết nối tạm đã hết hạn. Cần kiểm tra việc tự đóng.')
        else:
            print('Kết nối nhận dạng tạm đang mở. Tự đóng lúc '
                  + datetime.fromtimestamp(s['het_luc']).strftime('%d/%m/%Y %H:%M:%S') + '.')
    return 0


def _tao_may_chu(c, khoa):
    # Dùng nguyên transport/TLS/allowlist KN2; chỉ thêm vòng đời có thời hạn.
    from kho_tri_thuc.engines.e_ocr.cau_noi_abbyy import (
        CauHinhCauNoi, CauNoiABBYY, _MayChuHTTPS)
    cau_hinh = CauHinhCauNoi(bat=True, khoa=khoa.lay_de_truyen(),
                             ip_core=(_ip_noi_bo(c['ip_core']),),
                             dia_chi=_ip_noi_bo(c['dia_chi']), cong=c['cong'],
                             thu_muc_hot_folder=Path(c['hot_folder']), tls=_tls(c))
    return _MayChuHTTPS(CauNoiABBYY(cau_hinh))


def _phuc_vu(data, khoa, *, dong_ho=time.time, don_dieu=time.monotonic,
             doi=None):
    s, c, tep = data['trang_thai'], data['cau_hinh'], Path(data['tep'])
    # Deadline đơn điệu ngăn việc chỉnh lùi giờ kéo dài phiên.
    han = don_dieu() + max(0, s['het_luc'] - dong_ho())
    may = None
    da_dung = threading.Event()
    doi = doi or da_dung.wait
    try:
        if dong_ho() >= s['het_luc'] or don_dieu() >= han:
            return
        may = _tao_may_chu(c, khoa)

        def phuc_vu():
            try:
                may.serve_forever(poll_interval=0.2)
            except Exception:
                pass  # Không in lỗi transport chứa dữ liệu/đường dẫn.
            finally:
                da_dung.set()

        # Transport/TLS có thể đang chờ socket; bộ đếm hạn chạy độc lập.
        # Luồng daemon không giữ tiến trình còn sống sau khi main hết hạn.
        threading.Thread(target=phuc_vu, daemon=True).start()
        print('SAN_SANG', flush=True)  # Pipe riêng, không phải màn người dùng.
        while (not da_dung.is_set() and dong_ho() < s['het_luc']
               and don_dieu() < han):
            doi(min(0.5, max(0, han - don_dieu())))
    finally:
        if may is not None:
            may.server_close()
        # Không thu hồi khóa của phiên khác nếu tệp trạng thái đã thay đổi.
        with _khoa(tep, doi_khoa=True):
            hien_tai = _doc(tep)
            if hien_tai and hien_tai['phien'] == s['phien']:
                _nhat_ky(tep)
                _thu_hoi(hien_tai, bi_mat.KetBiMat)
                het_han = dong_ho() >= s['het_luc'] or don_dieu() >= han
                hien_tai.update(pid=None, tao_luc=None,
                                trang_thai='het-han' if het_han else 'da-dong')
                _ghi(tep, hien_tai)
                LOG.info('Kết nối nhận dạng tạm đã tự đóng; đã thu hồi khóa.')


def _nhan_kenh():
    cau_hinh = doc_thong_diep(sys.stdin.buffer.readline(65_536))
    khoa = doc_thong_diep(sys.stdin.buffer.readline(65_536))
    if (cau_hinh.get('protocol') != PROTOCOL or cau_hinh.get('kieu') != 'abbyy_tam'
            or khoa.get('protocol') != PROTOCOL or khoa.get('kieu') != 'bi_mat'):
        raise LoiKetNoi('Kênh cấp kết nối tạm chưa hợp lệ.')
    return cau_hinh['du_lieu'], bi_mat.BiMat(base64.b64decode(khoa['du_lieu'], validate=True))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ['--phuc-vu']:
        try:
            _phuc_vu(*_nhan_kenh())
            return 0
        except Exception:
            return 1  # Không in ngoại lệ/traceback/bootstrap chứa khóa.
    parser = argparse.ArgumentParser(description='Quản lý kết nối nhận dạng ABBYY tạm thời.')
    parser.add_argument('lenh', choices=('mo', 'dong', 'trang-thai'))
    parser.add_argument('--chay-kho', action='store_true', help='Chỉ xem bước dự kiến, không thay đổi.')
    parser.add_argument('--ip-core', help='IP nội bộ của máy chủ Core được phép kết nối.')
    parser.add_argument('--dia-chi', default='127.0.0.1', help='IP nội bộ cụ thể để lắng nghe.')
    parser.add_argument('--cong', type=int, default=9443)
    parser.add_argument('--gio', type=float, default=8)
    parser.add_argument('--ket', help='Thư mục két hiện có, ngoài mã nguồn.')
    parser.add_argument('--chung-thu', help='Tệp chứng thư đã chuẩn bị.')
    parser.add_argument('--khoa-tls', help='Tệp khóa riêng của chứng thư.')
    parser.add_argument('--hot-folder', help='Thư mục nhận dạng đã chuẩn bị; không dò nội dung khi mở.')
    args = parser.parse_args(argv)
    if args.chay_kho:
        buoc = {
            'mo': 'Kiểm IP nội bộ và chứng thư; sinh khóa, lưu thẳng vào két Core; '
                  'mở cầu bảo mật chỉ nhận IP Core; ghi trạng thái không chứa khóa; '
                  f'tự đóng sau {args.gio:g} giờ và thu hồi khóa bằng đổi tên.',
            'dong': 'Đối chiếu tiến trình của phiên đã ghi; dừng đúng tiến trình; '
                    'thu hồi khóa bằng đổi tên trong két; ghi trạng thái đã đóng.',
            'trang-thai': 'Đọc trạng thái và kiểm tiến trình, không đọc giá trị khóa.',
        }
        print('Chạy khô: ' + buoc[args.lenh])
        print('Không thay đổi tệp, két, tiến trình, mạng hoặc tường lửa; không chạy ABBYY.')
        return 0
    try:
        if args.lenh == 'mo':
            return mo(args)
        if args.lenh == 'dong':
            return dong()
        return trang_thai()
    except (Exception, KeyboardInterrupt):
        # Không str(exc), repr(exc) hay traceback: phụ thuộc có thể chứa khóa.
        print('Chưa hoàn tất thao tác kết nối tạm. Cần kiểm tra cấu hình, quyền và trạng thái; '
              'chạy đóng để đối chiếu trước khi mở lại.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
