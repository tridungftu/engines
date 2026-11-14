"""Port Kho: chuyển từ nguồn cũ, giữ snapshot/nhật ký/chốt trong RAM.

Chỉ tái dùng hai thao tác nội bộ snapshot_luot/chot_luot. Đây chưa phải API
ngăn hoặc transport SDK. Callable phải gắn phiên/lease tin cậy, kiểm quyền
trong cùng giao dịch phía kho, CAS và duy nhất trước trả chốt. Snapshot có
da_chot=False phải xác nhận không còn chốt đang chờ; nếu chưa biết, port ném
ChuaRo. Nhật ký chứa cụm gốc chỉ gửi vào kho được phép, không phải log.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import json
from re import fullmatch
from typing import Protocol
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo, ViecDaHuy

from .che_van_ban import _kiem_dinh_danh, chuan_bi_danh, chuan_hoa
from .kho_tam import KhoTam
from .nguon.privacy.core import CATEGORIES
from .quyen_yeu_cau import loi_kho, xac_minh


# Họ tiền tố chỉ cho DEMO, chờ xác nhận không trùng mã Junsky thật.
TIEN_TO_TU_SINH = 'MASK'


class PortKho(Protocol):
    def __call__(self, thao_tac: str, *, ma_yeu_cau: str, ma_luot: str,
                 loai: str, **payload) -> dict:
        """snapshot_luot hoặc chot_luot; không nhận danh tính tự khai.

        chot_luot với nhật ký None chỉ đọc lại lượt đã chốt sau kiểm quyền.
        CAS bao trùm alias/cụm/đếm/tham chiếu/yêu cầu/kết quả. Đã nhận chốt
        chưa trả phải ném ChuaRo; lỗi xác định phải đảm bảo chưa ghi gì.
        """
        ...


def bam_noi_dung(gia_tri):
    try:
        raw = json.dumps(gia_tri, ensure_ascii=True, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
        return sha256(raw).hexdigest()
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise loi_kho() from None


def _la_bi_danh(gia_tri):
    return isinstance(gia_tri, str) and fullmatch(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]', gia_tri)


def _kiem_snapshot(snap):
    try:
        if not isinstance(snap, dict) or type(snap.get('da_chot')) is not bool:
            raise ValueError
        if not {'phien_ban', 'yeu_cau'} <= snap.keys() or not isinstance(snap.get('danh_muc'), list):
            raise ValueError
        yc = snap.get('yeu_cau')
        if yc is not None and (not isinstance(yc, dict) or yc.get('trang_thai') not in {'DANG_XU_LY', 'DA_DONG'}):
            raise ValueError
        theo_cum, theo_bi_danh = set(), {}
        for muc in snap['danh_muc']:
            if (not isinstance(muc, dict) or not _la_bi_danh(muc.get('bi_danh'))
                    or muc.get('nguon') not in {'tam', 'chinh_thuc'}
                    or (muc.get('bi_danh_tam') is not None and not _la_bi_danh(muc['bi_danh_tam']))):
                raise ValueError
            _kiem_dinh_danh([{'gia_tri': muc['gia_tri'], 'nhom': muc['nhom']}])
            chuan = chuan_hoa(muc['gia_tri'])
            if chuan in theo_cum:
                raise ValueError
            theo_cum.add(chuan)
            for bi_danh in (muc['bi_danh'], muc.get('bi_danh_tam')):
                if bi_danh:
                    b = chuan_bi_danh(bi_danh)
                    if b in theo_bi_danh and theo_bi_danh[b] != chuan:
                        raise ValueError
                    theo_bi_danh[b] = chuan
        cum_cho = snap.get('cum_cho_toan_vung', {})
        if not isinstance(cum_cho, dict):
            raise ValueError
        for bam, muc in cum_cho.items():
            if (not isinstance(bam, str) or fullmatch(r'[0-9a-f]{64}', bam) is None
                    or not isinstance(muc, dict) or set(muc) != {'nhom', 'bi_danh', 'nguon'}
                    or not isinstance(muc['nhom'], str) or muc['nhom'] not in CATEGORIES
                    or not _la_bi_danh(muc['bi_danh']) or muc['nguon'] != 'tam'):
                raise ValueError
        bo_sung = snap.get('bi_danh_bo_sung', {})
        if (not isinstance(bo_sung, dict)
                or any(not _la_bi_danh(k) or not isinstance(v, str) or not v for k, v in bo_sung.items())):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise loi_kho() from None


class KhoQuaCore:
    def __init__(self, *, goi_kho=None, quyen=None, viec=None, loai='che',
                 ma_yeu_cau=None, bam_dau_vao, kho_tam=None):
        if not callable(goi_kho):
            raise loi_kho('MASK_KHO_CHUA_NOI')
        self._ngu_canh = xac_minh(quyen, viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        self._ma, self._luot = self._ngu_canh.ma_yeu_cau, self._ngu_canh.ma_luot
        self._loai, self._goi_kho = loai, goi_kho
        self._quyen, self._viec = quyen, viec
        self._kho_tam = kho_tam if kho_tam is not None else KhoTam()
        self._bam_dau_vao = bam_dau_vao
        self._bam_chot = None
        self._dau = self._ghi_dau(1)
        self._snapshot = deepcopy(self._goi('snapshot_luot'))
        _kiem_snapshot(self._snapshot)
        self.da_chot = self._snapshot['da_chot']
        if self._dau['trang_thai'] == 4 and not self.da_chot:
            raise loi_kho('MASK_XUNG_DOT')
        self._danh_muc = deepcopy(self._snapshot['danh_muc'])
        self._theo_cum = {chuan_hoa(m['gia_tri']): m for m in self._danh_muc}
        self._dang_goi = self._da_chay = self._hop_le = self._can_hoi_lai = False
        self._nhat_ky = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[], dong_yeu_cau=False,
                            cum_da_tra=[], bi_danh_da_tra=[])
        self._da_gap = set()

    def __repr__(self):
        return 'KhoQuaCore(<ẩn>)'

    def _ghi_dau(self, trang_thai):
        return self._kho_tam.ghi(vung=self._ngu_canh.vung, ma_luot=self._luot,
                                ma_yeu_cau=self._ma, bam_dau_vao=self._bam_dau_vao,
                                trang_thai=trang_thai, bam_chot=self._bam_chot)

    def _goi(self, thao_tac, **payload):
        ngu_canh = xac_minh(self._quyen, self._viec, loai=self._loai, ma_yeu_cau=self._ma,
                           thao_tac=('snapshot' if thao_tac == 'snapshot_luot'
                                     else 'doc_lai' if payload.get('nhat_ky') is None else 'chot'))
        if ngu_canh != self._ngu_canh:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
        try:
            return self._goi_kho(thao_tac, ma_yeu_cau=self._ma,
                                 ma_luot=self._luot, loai=self._loai, **payload)
        except ChuaRo:
            self._dau = self._ghi_dau(3)
            # Dùng mã từ khóa lượt đã băm, không chuyển câu/mã tùy ý của nguồn.
            raise ChuaRo('mask-' + self._dau['tuong_quan']) from None
        except ViecDaHuy:
            raise
        except Exception as exc:
            ma = getattr(exc, 'ma', None)
        raise loi_kho(ma) from None

    def chot(self, ket_qua=None):
        if self._can_hoi_lai and not self.da_chot:
            snap = self._goi('snapshot_luot')
            _kiem_snapshot(snap)
            self.da_chot = snap['da_chot']
        if self.da_chot:
            # Đọc lại từ port có kiểm quyền; không lấy kết quả từ JSON/snapshot.
            kq = self._goi('chot_luot', phien_ban=None, nhat_ky=None, ket_qua=None)
        else:
            nhat_ky = self.nhat_ky
            if not isinstance(ket_qua, dict):
                raise loi_kho()
            kq = deepcopy(ket_qua)
            kq.update(ma_yeu_cau=self._ma, ma_luot=self._luot)
            if self._loai == 'che' and not kq.get('gui_duoc'):
                nhat_ky['dong_yeu_cau'] = True
            self._bam_chot = bam_noi_dung([nhat_ky, kq])
            self._dau = self._ghi_dau(2)
            self._can_hoi_lai = True
            kq = self._goi('chot_luot', phien_ban=self._snapshot['phien_ban'],
                           nhat_ky=nhat_ky, ket_qua=kq)
        if (not isinstance(kq, dict) or kq.get('ma_yeu_cau') != self._ma
                or kq.get('ma_luot') != self._luot):
            raise loi_kho()
        self.da_chot = True
        self._ghi_dau(4)
        return deepcopy(kq)

    @contextmanager
    def giao_dich(self):
        if self.da_chot or self._dang_goi or self._da_chay:
            raise loi_kho()
        self._dang_goi = self._da_chay = True
        try:
            yield self
            self._hop_le = True
        finally:
            self._dang_goi = False
            if not self._hop_le:
                self._nhat_ky = None
                self._theo_cum.clear()
                self._danh_muc.clear()

    def _kiem(self, ma=None):
        if not self._dang_goi or (ma is not None and ma != self._ma):
            raise loi_kho('MASK_MA_YEU_CAU')

    @property
    def nhat_ky(self):
        if not self._hop_le or self._dang_goi:
            raise loi_kho()
        return deepcopy(self._nhat_ky)

    def tao_yeu_cau(self):
        self._kiem()
        if self._loai != 'che':
            raise loi_kho()
        return self._ma

    def doc_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        muc = self._snapshot['yeu_cau']
        if muc is None or muc['trang_thai'] != 'DANG_XU_LY':
            raise loi_kho('MASK_MA_YEU_CAU')
        return deepcopy(muc)

    def liet_ke_dinh_danh(self):
        self._kiem()
        return deepcopy(self._danh_muc)

    def tra_bi_danh(self, gia_tri_chuan):
        self._kiem()
        chuan = chuan_hoa(gia_tri_chuan)
        bam = sha256(chuan.encode('utf-8')).hexdigest()
        if bam not in self._nhat_ky['cum_da_tra']:
            self._nhat_ky['cum_da_tra'].append(bam)
        muc = self._theo_cum.get(chuan)
        if muc is None:
            da_co = self._snapshot.get('cum_cho_toan_vung', {}).get(bam)
            if da_co is not None:
                muc = dict(gia_tri=gia_tri_chuan, nhom=da_co['nhom'],
                           bi_danh=da_co['bi_danh'], nguon=da_co['nguon'])
                self._theo_cum[chuan] = muc
                self._danh_muc.append(muc)
        return None if muc is None else {k: deepcopy(v) for k, v in muc.items() if k != 'gia_tri'}

    def cap_bi_danh_tam(self):
        self._kiem()
        ma = '[[' + TIEN_TO_TU_SINH + 'TAM-' + uuid4().hex + ']]'
        if not _la_bi_danh(ma):
            raise loi_kho()
        self._nhat_ky['bi_danh_tam_moi'].append(ma)
        return ma

    def ghi_cho_duyet(self, gia_tri, nhom, bi_danh, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        _kiem_dinh_danh([{'gia_tri': gia_tri, 'nhom': nhom}])
        chuan = chuan_hoa(gia_tri)
        cu = self.tra_bi_danh(chuan)
        if cu is not None:
            if bi_danh != cu['bi_danh'] and bi_danh in self._nhat_ky['bi_danh_tam_moi']:
                self._nhat_ky['bi_danh_tam_moi'].remove(bi_danh)
            self.ghi_nhan_gap_lai(ma_yeu_cau, chuan, cu['nhom'])
            return cu, False
        if bi_danh not in self._nhat_ky['bi_danh_tam_moi']:
            raise loi_kho()
        muc = dict(gia_tri=gia_tri, nhom=nhom, bi_danh=bi_danh, nguon='tam', so_lan_gap=1)
        self._theo_cum[chuan] = muc
        self._danh_muc.append(muc)
        self._nhat_ky['cum'].append(dict(gia_tri=gia_tri, nhom=nhom,
                                       bi_danh=bi_danh, chi_gap_lai=False))
        self._da_gap.add(chuan)
        return self.tra_bi_danh(chuan), True

    def ghi_nhan_gap_lai(self, ma_yeu_cau, cum_chuan, nhom):
        self._kiem(ma_yeu_cau)
        chuan = chuan_hoa(cum_chuan)
        muc = self._theo_cum.get(chuan)
        if muc is None or muc['nhom'] != nhom:
            raise loi_kho()
        if chuan not in self._da_gap:
            self._nhat_ky['cum'].append(dict(gia_tri=muc['gia_tri'], nhom=nhom,
                                           bi_danh=muc['bi_danh'], chi_gap_lai=True))
            self._da_gap.add(chuan)

    def ghi_bi_danh_da_dung(self, ma_yeu_cau, bi_danh):
        self._kiem(ma_yeu_cau)
        if any(not _la_bi_danh(b) for b in bi_danh):
            raise loi_kho()
        self._nhat_ky['bi_danh_da_dung'] = sorted(set(self._nhat_ky['bi_danh_da_dung']) | set(bi_danh))

    def tra_dinh_danh(self, bi_danh_chuan):
        self._kiem()
        chuan = chuan_bi_danh(bi_danh_chuan)
        if chuan not in self._nhat_ky['bi_danh_da_tra']:
            self._nhat_ky['bi_danh_da_tra'].append(chuan)
        for muc in self._danh_muc:
            if any(b and chuan_bi_danh(b) == chuan
                   for b in (muc['bi_danh'], muc.get('bi_danh_tam'))):
                return muc['gia_tri']
        return self._snapshot.get('bi_danh_bo_sung', {}).get(chuan)

    def dong_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        self._nhat_ky['dong_yeu_cau'] = True
