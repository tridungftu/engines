"""Snapshot Local nội bộ bất biến; Core giữ tệp, Ngan chỉ giữ chỉ mục.

Chưa có transport SDK: bên tích hợp phải cấp cả quyền và port kho tệp có
ACL/lease. Không lấy port từ đầu vào, không dùng đường tệp máy hoặc bộ đệm
bền. Kế hoạch do Core cấp; thuật toán chia đoạn thuộc MASK-2c-2.
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
# Khai báo nội bộ cho adapter, chưa thêm trường vào phiếu SDK 2.0.
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
    """Port được bên tích hợp tiêm, KHÔNG phải API/transport SDK đã có.

    Core phải kiểm ACL, pháp nhân và lease ngay trong từng luu/doc; không
    dùng riêng kiểm_quyen trước thao tác để thay kiểm quyền nguyên tử.
    Kho giữ snapshot bất biến, dọn tệp chưa có chỉ mục/khi đóng yêu cầu.
    """
    def kiem_quyen(self, viec, ngu_canh, *, tham_chieu, thao_tac) -> bool: ...
    def luu(self, viec, ngu_canh, du_lieu: bytes) -> ThamChieuHoSo: ...
    def doc(self, viec, ngu_canh, tham_chieu: ThamChieuHoSo) -> bytes: ...


class KhoHoSoAI:
    def __init__(self, *, ngan, quyen=None, cong=None):
        self._ngan, self._quyen, self._cong = ngan, quyen, cong

    def _xac_minh(self, viec, ma, thao_tac, tham_chieu=None):
        if type(ma) is not str or not ma.strip() or self._cong is None:
            raise _loi('MASK_AI_QUYEN')
        ngu_canh = xac_minh(self._quyen, viec, loai='che', ma_yeu_cau=ma, thao_tac=thao_tac)
        pn = viec.ngu_canh.get('phap_nhan_id')
        if (type(pn) is not str or not pn.strip() or self._cong.kiem_quyen(
                viec, ngu_canh, tham_chieu=tham_chieu, thao_tac=thao_tac) is not True):
            raise _loi('MASK_AI_QUYEN')
        # Không dùng ma_luot/viec_id: cùng yêu cầu đi qua nhiều bước.
        khoa = {'ma': ma, 'phien': ngu_canh.phien, 'module': ngu_canh.module,
                'nguoi_gui': ngu_canh.nguoi_gui, 'tai_lieu': ngu_canh.tai_lieu,
                'vung': ngu_canh.vung, 'phap_nhan_id': pn}
        return ngu_canh, {'bam_yeu_cau': bam_bytes(json_chuan(khoa))}

    def _doc(self, viec, ma, chi_muc, khoa):
        v = chi_muc.gia_tri
        _dung_khoa(v['ho_so'], ThamChieuHoSo)
        ref = ThamChieuHoSo(**v['ho_so'])
        ref.kiem()
        ctx, khoa_moi = self._xac_minh(viec, ma, 'doc_ho_so_ai', ref)
        if khoa_moi != khoa:
            raise _loi('MASK_AI_QUYEN')
        raw = self._cong.doc(viec, ctx, ref)
        if type(raw) is not bytes or len(raw) != ref.kich_thuoc or bam_bytes(raw) != v['bam_ho_so']:
            raise _loi()
        ho_so = doc_bytes(raw)
        if (v['bam_goc'] != ho_so.anh_xa.bam_goc or v['bam_da_che_quy_tac'] != ho_so.anh_xa.bam_da_che
                or type(v['phien_ban_map']) is not int or v['phien_ban_map'] != ho_so.anh_xa.phien_ban
                or type(v['phien_ban_ho_so']) is not int or v['phien_ban_ho_so'] != ho_so.phien_ban
                or self._xac_minh(viec, ma, 'doc_ho_so_ai', ref)[1] != khoa):
            raise _loi()
        return ho_so

    @_chan_loi
    def luu(self, viec, ma_yeu_cau, ho_so):
        ctx, khoa = self._xac_minh(viec, ma_yeu_cau, 'luu_ho_so_ai')
        if type(ho_so) is not HoSoAI:
            raise _loi()
        raw = ho_so.thanh_bytes()
        bam = bam_bytes(raw)
        cu = self._ngan.doc('ho_so_ai', khoa)
        if cu is not None:
            if cu.gia_tri['bam_ho_so'] != bam:
                raise _loi('MASK_AI_XUNG_DOT')
            self._doc(viec, ma_yeu_cau, cu, khoa)
            return DauHoSoAI(ThamChieuHoSo(**cu.gia_tri['ho_so']), bam)
        ref = self._cong.luu(viec, ctx, raw)
        if type(ref) is not ThamChieuHoSo:
            raise _loi()
        ref.kiem()
        # Đọc lại bằng chính port có quyền: không tin metadata tự khai.
        ctx, khoa_moi = self._xac_minh(viec, ma_yeu_cau, 'doc_ho_so_ai', ref)
        if khoa_moi != khoa or self._cong.doc(viec, ctx, ref) != raw:
            raise _loi()
        chi_muc = {**khoa, 'ho_so': asdict(ref), 'bam_ho_so': bam,
                   'bam_goc': ho_so.anh_xa.bam_goc, 'bam_da_che_quy_tac': ho_so.anh_xa.bam_da_che,
                   'phien_ban_map': ho_so.anh_xa.phien_ban, 'phien_ban_ho_so': ho_so.phien_ban}
        if self._xac_minh(viec, ma_yeu_cau, 'chot_ho_so_ai', ref)[1] != khoa:
            raise _loi('MASK_AI_QUYEN')
        with self._ngan.lo() as lo:
            ket = lo.lay_hoac_tao('ho_so_ai', khoa, chi_muc)
        if ket.gia_tri != chi_muc:
            raise _loi('MASK_AI_XUNG_DOT')
        # Thu hồi quyền hoặc mất tệp trong lúc chốt: không phát hành tham chiếu.
        self._doc(viec, ma_yeu_cau, ket.ban_ghi, khoa)
        return DauHoSoAI(ref, bam)

    @_chan_loi
    def doc(self, viec, ma_yeu_cau, dau):
        if (type(dau) is not DauHoSoAI or type(dau.ho_so) is not ThamChieuHoSo
                or type(dau.bam_ho_so) is not str or not _BAM.fullmatch(dau.bam_ho_so)):
            raise _loi()
        dau.ho_so.kiem()
        _, khoa = self._xac_minh(viec, ma_yeu_cau, 'doc_ho_so_ai', dau.ho_so)
        ban = self._ngan.doc('ho_so_ai', khoa)
        if (ban is None or ban.gia_tri['ho_so'] != asdict(dau.ho_so)
                or ban.gia_tri['bam_ho_so'] != dau.bam_ho_so):
            raise _loi()
        return self._doc(viec, ma_yeu_cau, ban, khoa)
