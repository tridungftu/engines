"""Hồ sơ Local nội bộ chỉ RAM theo P4; không có kho snapshot Core.

Các hàm bytes là bộ kiểm thuần trong RAM, không phải đường khôi phục.
KhoHoSoAI lịch sử bị đóng; bên tích hợp phải truyền handle kho R4.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from functools import wraps
from hashlib import sha256
import json
import re
from typing import Protocol
import unicodedata

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from .anh_xa_ai import AnhXaAI, LoiAnhXa, PhepSua, bam_chu, kiem_anh_xa
from .ngan import NganXungDot
from .nguon.privacy.types import la_bien_to_hop, la_ky_tu_vo_hinh
from .quyen_yeu_cau import xac_minh

PHIEN_BAN_HO_SO = 1
GIOI_HAN_HO_SO = 64 * 1024 * 1024
# Khai báo lịch sử chỉ để import hồi quy; R5 không dùng hoặc tạo chỉ mục.
KHAI_NGAN_HO_SO_AI = ({'bang': 'ho_so_ai', 'khoa': ['bam_yeu_cau'],
                       'pham_vi': 'engine', 'duy_nhat': []},)
_BAM = re.compile(r'sha256:[0-9a-f]{64}')
_MA_TEP = re.compile(r'[A-Za-z0-9_-][A-Za-z0-9_.:-]{0,199}')


def _loi(ma='MASK_AI_HO_SO'):
    cau = {'MASK_AI_HO_SO': 'Không xác minh được hồ sơ nội bộ. Cần thực hiện lại yêu cầu.',
           'MASK_AI_MAP': 'Không xác minh được ánh xạ văn bản an toàn.',
           'MASK_AI_QUYEN': 'Chưa xác minh được quyền truy cập hồ sơ nội bộ.',
           'MASK_AI_XUNG_DOT': 'Hồ sơ nội bộ đã thay đổi. Hãy thực hiện lại yêu cầu.'}
    return LoiNghiepVu(ma, cau[ma], thu_lai_duoc=ma == 'MASK_AI_XUNG_DOT')


def _chan_loi(ham):
    @wraps(ham)
    def goi(*a, **kw):
        try:
            return ham(*a, **kw)
        except (ChuaRo, ViecDaHuy, LoiDuongTruyen):
            raise
        except LoiAnhXa:
            raise _loi('MASK_AI_MAP') from None
        except NganXungDot:
            raise _loi('MASK_AI_XUNG_DOT') from None
        except LoiNghiepVu as exc:
            # Không chuyển tiếp thông điệp tùy ý từ một port hỏng.
            ma = exc.ma
            if ma in {'MASK_AI_HO_SO', 'MASK_AI_MAP', 'MASK_AI_QUYEN', 'MASK_AI_XUNG_DOT'}:
                raise _loi(ma) from None
            raise _loi('MASK_AI_QUYEN') from None
        except Exception:
            raise _loi() from None
    return goi


def json_chuan(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def bam_bytes(v):
    return 'sha256:' + sha256(v).hexdigest()


@dataclass(frozen=True, slots=True)
class DoanAI:
    chi_so: int
    bat_dau: int
    ket_thuc: int
    bat_dau_chinh: int
    ket_thuc_chinh: int
    bam_doan: str


def _bien_doan(goc, i):
    if not la_bien_to_hop(goc, i):
        return False
    if 0 < i < len(goc):
        if la_ky_tu_vo_hinh(goc[i - 1]) or la_ky_tu_vo_hinh(goc[i]):
            return False
        def trong_tu(c):
            return c.isalnum() or c == '_' or unicodedata.category(c).startswith('M')
        if trong_tu(goc[i - 1]) and trong_tu(goc[i]):
            return False
    return True


@dataclass(frozen=True, slots=True, repr=False)
class HoSoAI:
    anh_xa: AnhXaAI
    ke_hoach: tuple[DoanAI, ...]
    phien_ban_engine: str
    phien_ban: int = PHIEN_BAN_HO_SO

    def kiem(self):
        kiem_anh_xa(self.anh_xa)
        if (type(self.phien_ban) is not int or self.phien_ban != PHIEN_BAN_HO_SO
                or type(self.phien_ban_engine) is not str
                or not re.fullmatch(r'e_mask [0-9]+\.[0-9]+\.[0-9]+', self.phien_ban_engine)
                or type(self.ke_hoach) is not tuple or not 1 <= len(self.ke_hoach) <= 128):
            raise _loi()
        goc, cuoi = self.anh_xa.goc, 0
        for i, d in enumerate(self.ke_hoach):
            if (type(d) is not DoanAI or any(type(v) is not int for v in
                    (d.chi_so, d.bat_dau, d.ket_thuc, d.bat_dau_chinh, d.ket_thuc_chinh))
                    or d.chi_so != i or d.bat_dau_chinh != cuoi
                    or not 0 <= d.bat_dau <= d.bat_dau_chinh < d.ket_thuc_chinh <= d.ket_thuc <= len(goc)
                    or d.ket_thuc - d.bat_dau > 8000
                    or d.bat_dau_chinh - d.bat_dau > 512 or d.ket_thuc - d.ket_thuc_chinh > 512
                    or any(not _bien_doan(goc, p) for p in
                           (d.bat_dau, d.ket_thuc, d.bat_dau_chinh, d.ket_thuc_chinh))
                    or d.bam_doan != bam_chu(goc[d.bat_dau:d.ket_thuc])):
                raise _loi()
            cuoi = d.ket_thuc_chinh
        if cuoi != len(goc):
            raise _loi()

    @_chan_loi
    def thanh_bytes(self):
        self.kiem()
        du_lieu = json_chuan(asdict(self))
        if len(du_lieu) > GIOI_HAN_HO_SO:
            raise _loi()
        return du_lieu


def _khong_trung(cac_cap):
    ket = {}
    for k, v in cac_cap:
        if k in ket:
            raise _loi()
        ket[k] = v
    return ket


def _khong_hang(_):
    raise _loi()


def _dung_khoa(v, lop):
    if type(v) is not dict or set(v) != {f.name for f in fields(lop)}:
        raise _loi()


@_chan_loi
def doc_bytes(du_lieu):
    if type(du_lieu) is not bytes or len(du_lieu) > GIOI_HAN_HO_SO:
        raise _loi()
    v = json.loads(du_lieu.decode('utf-8'), object_pairs_hook=_khong_trung,
                   parse_constant=_khong_hang)
    _dung_khoa(v, HoSoAI)
    m = v['anh_xa']
    _dung_khoa(m, AnhXaAI)
    for ten in ('goc_sach', 'sach_do', 'goc_che'):
        if type(m[ten]) is not list:
            raise _loi()
        phep = []
        for p in m[ten]:
            _dung_khoa(p, PhepSua)
            if type(p['goc']) is not list or type(p['dich']) is not list:
                raise _loi()
            phep.append(PhepSua(tuple(p['goc']), tuple(p['dich']), p['loai']))
        m[ten] = tuple(phep)
    if type(v['ke_hoach']) is not list:
        raise _loi()
    for d in v['ke_hoach']:
        _dung_khoa(d, DoanAI)
    ho_so = HoSoAI(AnhXaAI(**m), tuple(DoanAI(**d) for d in v['ke_hoach']),
                   v['phien_ban_engine'], v['phien_ban'])
    if ho_so.thanh_bytes() != du_lieu:
        raise _loi()
    return ho_so


@dataclass(frozen=True, slots=True, repr=False)
class ThamChieuHoSo:
    tep_id: str
    ten: str
    mime: str
    kich_thuoc: int

    def kiem(self):
        if (type(self.tep_id) is not str or not _MA_TEP.fullmatch(self.tep_id)
                or self.ten != 'mask-2c-ho-so.json' or self.mime != 'application/json'
                or type(self.kich_thuoc) is not int or not 0 < self.kich_thuoc <= GIOI_HAN_HO_SO):
            raise _loi()


@dataclass(frozen=True, slots=True, repr=False)
class DauHoSoAI:
    ho_so: ThamChieuHoSo
    bam_ho_so: str


class CongHoSoAI(Protocol):
    """Tên lịch sử chỉ để import tương thích; không còn cửa luu/doc."""
    def kiem_quyen(self, viec, ngu_canh, *, tham_chieu, thao_tac) -> bool: ...


class KhoHoSoAI:
    """Cửa snapshot cũ đã đóng, kể cả khi caller cấp ngăn/port giả."""
    def __init__(self, *, ngan=None, quyen=None, cong=None):
        pass

    def luu(self, *a, **kw):
        raise _loi('MASK_AI_QUYEN')

    def doc(self, *a, **kw):
        raise _loi('MASK_AI_QUYEN')


@dataclass(frozen=True, slots=True, repr=False)
class DauHoSoRAM:
    ma_ho_so_ram: str
    bam_ho_so: str

    def kiem(self):
        if (type(self.ma_ho_so_ram) is not str
                or re.fullmatch(r'[0-9a-f]{32}', self.ma_ho_so_ram) is None
                or type(self.bam_ho_so) is not str or not _BAM.fullmatch(self.bam_ho_so)):
            raise _loi()


def kiem_kho_ram(ram):
    from .kho_anh_xa_ram import KhoAnhXaRAM
    if type(ram) is not KhoAnhXaRAM:
        raise LoiNghiepVu('MASK_AI_CHUA_CO_CUA_CORE',
                         'Chưa có đủ cổng Core cho chuỗi AI cục bộ.')
    return ram


def _buoc_da_nhuong():
    from .quyen_yeu_cau import loi_ram
    raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')


def nhuong_luot(luot):
    """Bỏ việc SDK/handle khỏi lookup khi chờ, cấm dùng ngoài bước RAM."""
    if luot is not None:
        luot._kiem_huy = _buoc_da_nhuong
        luot._kho = None


def du_lieu_ram(buoc):
    """Chỉ dùng dưới quyền sở hữu R4; không lấy object từ payload/Core."""
    v = buoc.du_lieu
    s, dau = v.get('ho_so_ai'), v.get('dau_ho_so_ai')
    if type(s) is not dict or type(dau) is not DauHoSoRAM:
        from .quyen_yeu_cau import loi_ram
        raise loi_ram('MASK_ANH_XA_KHONG_CON')
    dau.kiem()
    if bam_bytes(json_chuan(s)) != dau.bam_ho_so:
        raise _loi()
    buoc.kiem()
    return s, dau
