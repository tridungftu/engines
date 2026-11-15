"""Dấu chống trùng cục bộ: chỉ băm/mã trạng thái; không chứa nội dung.

Khóa trên tệp riêng không bị thay inode khi thay JSON. Ghi tạm, fsync rồi
os.replace trong cùng thư mục. Mọi lỗi kho đều dừng xử lý, không có kho RAM
thay thế. Đây không phải kho tên gốc hoặc nơi lưu kết quả mở che.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import errno
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .quyen_yeu_cau import loi_kho


_GOI = Path(__file__).resolve().parents[1]
_BAM = re.compile(r'[0-9a-f]{64}')
_RONG = '0' * 64
# 1: đã giữ dấu đầu vào; 2: chuẩn bị chốt; 3: chưa rõ; 4: đã chốt.
_TRUONG = {'yeu_cau', 'dau_vao', 'chot', 'tuong_quan', 'trang_thai'}


def _loi():
    return LoiNghiepVu('MASK_KHO_TAM_LOI',
                      'Không đọc hoặc ghi được dữ liệu tạm. Hãy nhờ quản trị viên kiểm tra.')


def _bam(gia_tri):
    return sha256(gia_tri.encode('utf-8')).hexdigest()


def _cap_khong_trung(cac_cap):
    kq = {}
    for khoa, gia_tri in cac_cap:
        if khoa in kq:
            raise ValueError
        kq[khoa] = gia_tri
    return kq


def _kiem(du_lieu):
    if (not isinstance(du_lieu, dict) or set(du_lieu) != {'phien_ban', 'luot'}
            or type(du_lieu['phien_ban']) is not int or du_lieu['phien_ban'] != 1
            or not isinstance(du_lieu['luot'], dict)):
        raise ValueError
    for khoa, muc in du_lieu['luot'].items():
        if (not isinstance(khoa, str) or not _BAM.fullmatch(khoa)
                or not isinstance(muc, dict) or set(muc) != _TRUONG
                or type(muc['trang_thai']) is not int or muc['trang_thai'] not in {1, 2, 3, 4}
                or any(not isinstance(muc[k], str) or not _BAM.fullmatch(muc[k])
                       for k in _TRUONG - {'trang_thai'})):
            raise ValueError


def _khong_lien_ket(duong_dan):
    st = duong_dan.lstat()
    if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
        raise ValueError
    return st


def duong_dan_du_lieu():
    gia_tri = os.environ.get('KTT_ENGINE_DU_LIEU')
    if gia_tri is None:
        if os.name != 'nt' or not os.environ.get('PROGRAMDATA'):
            raise _loi()
        return Path(os.environ['PROGRAMDATA']) / 'KhoTriThuc' / 'engines' / 'e_mask' / 'du-lieu'
    if not gia_tri.strip():
        raise _loi()
    return Path(gia_tri)


class KhoTam:
    def __init__(self, thu_muc=None, *, cho_khoa_giay=5):
        try:
            dd = Path(thu_muc) if thu_muc is not None else duong_dan_du_lieu()
            if not dd.is_absolute() or cho_khoa_giay <= 0:
                raise ValueError
            for muc in (dd, *dd.parents):
                if muc.exists() or muc.is_symlink():
                    _khong_lien_ket(muc)
            dd = dd.resolve()
            if dd.is_relative_to(_GOI):
                raise ValueError
            self._thu_muc, self._cho_khoa = dd, cho_khoa_giay
        except (OSError, ValueError, RuntimeError):
            raise _loi() from None

    def __repr__(self):
        return 'KhoTam(<ẩn>)'

    @contextmanager
    def _khoa(self):
        self._thu_muc.mkdir(parents=True, exist_ok=True)
        tep = self._thu_muc / 'mask.khoa'
        if tep.exists() or tep.is_symlink():
            if not stat.S_ISREG(_khong_lien_ket(tep).st_mode):
                raise ValueError
        with os.fdopen(os.open(tep, os.O_RDWR | os.O_CREAT, 0o600), 'r+b', buffering=0) as f:
            if os.fstat(f.fileno()).st_size == 0:
                f.write(b'\0')
            if os.name == 'nt':
                import msvcrt
                def khoa():
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                def mo():
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                def khoa():
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                def mo():
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            han = time.monotonic() + self._cho_khoa
            while True:
                try:
                    khoa()
                    break
                except OSError as exc:
                    if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK} or time.monotonic() >= han:
                        raise
                    time.sleep(0.02)
            try:
                yield
            finally:
                mo()

    def _doc(self):
        tep = self._thu_muc / 'mask.json'
        try:
            st = _khong_lien_ket(tep)
        except FileNotFoundError:
            return {'phien_ban': 1, 'luot': {}}
        if not stat.S_ISREG(st.st_mode):
            raise ValueError
        du_lieu = json.loads(tep.read_text(encoding='utf-8'), object_pairs_hook=_cap_khong_trung)
        _kiem(du_lieu)
        return du_lieu

    def _ghi(self, du_lieu):
        _kiem(du_lieu)
        ten_tam = None
        try:
            fd, ten_tam = tempfile.mkstemp(prefix='mask-', suffix='.tam', dir=self._thu_muc)
            with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(du_lieu, f, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(ten_tam, self._thu_muc / 'mask.json')
            ten_tam = None
            if os.name != 'nt':
                fd = os.open(self._thu_muc, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
        finally:
            if ten_tam is not None:
                # Chỉ dọn tệp tạm do chính lần ghi này tạo.
                Path(ten_tam).unlink(missing_ok=True)

    def ghi(self, *, vung, ma_luot, ma_yeu_cau, bam_dau_vao,
            trang_thai=1, bam_chot=None):
        """Đọc/đổi/ghi dưới cùng khóa. Không có cửa ghi JSON tùy ý.

        Mã opaque cũng được băm trước lưu; tên trường và trạng thái cố định.
        Cùng lượt khác yêu cầu/đầu vào là xung đột, không ghi đè dấu cũ.
        """
        try:
            if (not isinstance(vung, str) or vung not in {'DEMO', 'THAT'}
                    or any(not isinstance(v, str) or not v for v in (ma_luot, ma_yeu_cau))
                    or not isinstance(bam_dau_vao, str) or not _BAM.fullmatch(bam_dau_vao)
                    or type(trang_thai) is not int or trang_thai not in {1, 2, 3, 4}
                    or (bam_chot is not None and (not isinstance(bam_chot, str) or not _BAM.fullmatch(bam_chot)))):
                raise ValueError
            khoa = _bam(json.dumps([vung, ma_luot], ensure_ascii=True))
            moi = dict(yeu_cau=_bam(ma_yeu_cau), dau_vao=bam_dau_vao,
                       chot=bam_chot or _RONG, tuong_quan=khoa, trang_thai=trang_thai)
            with self._khoa():
                du_lieu = self._doc()
                cu = du_lieu['luot'].get(khoa)
                if cu and any(cu[k] != moi[k] for k in ('yeu_cau', 'dau_vao')):
                    raise loi_kho('MASK_XUNG_DOT')
                if cu and bam_chot is None:
                    moi['chot'] = cu['chot']
                if cu and (trang_thai == 1 or cu['trang_thai'] == 4):
                    moi = cu
                du_lieu['luot'][khoa] = moi
                self._ghi(du_lieu)
                return deepcopy(moi)
        except LoiNghiepVu:
            raise
        except (OSError, ValueError, UnicodeError, RuntimeError, RecursionError):
            raise _loi() from None
