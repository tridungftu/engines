"""MASK-3E: port Kho của engine, snapshot/nhật ký theo MASK-3D.

goi_kho(operation, **payload) do Core tiêm và gắn với SDKEngine của việc.
Chỉ hai operation nội bộ: snapshot_luot và chot_luot. Callable phải kiểm
lease/quyền ở mỗi lần gọi và chỉ trả chốt sau commit. F/G nối transport;
không nhận callable, danh tính hoặc kết nối CSDL từ envelope.
Nhật ký thay đổi chứa cụm gốc, chỉ gửi về kho Core; không phải audit/log.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from re import fullmatch
from uuid import UUID, uuid4

from kho_tri_thuc.sdk_core.engine import LoiEngine
from kho_tri_thuc.sdk_core.ngu_canh import _xoa_loi
from .che_van_ban import chuan_bi_danh, chuan_hoa


class LoiKhoQuaCore(ValueError):
    """Lỗi cố định, không giữ cụm gốc hoặc ngoại lệ từ kênh."""

    def __init__(self, thong_bao, *, ma='MASK_XU_LY'):
        self.ma = ma
        super().__init__(thong_bao)


class KhoQuaCore:
    def __init__(self, *, goi_kho, ma_yeu_cau, ma_luot, loai):
        if not callable(goi_kho) or loai not in ('che', 'mo_che'):
            raise LoiKhoQuaCore('Chưa có kênh kho định danh hợp lệ.')
        # Các mã ổn định được Core cấp trong tệp riêng; không tự sinh khi retry.
        self._ma = str(UUID(ma_yeu_cau))
        self._luot = str(UUID(ma_luot))
        self._loai, self._goi_kho = loai, goi_kho
        self._snapshot = deepcopy(self._goi('snapshot_luot'))
        if (not isinstance(self._snapshot, dict)
                or type(self._snapshot.get('da_chot')) is not bool):
            raise LoiKhoQuaCore('Thông tin lượt xử lý chưa hợp lệ.')
        cum_cho = self._snapshot.get('cum_cho_toan_vung', {})
        if not isinstance(cum_cho, dict):
            raise LoiKhoQuaCore('Thông tin định danh chờ duyệt chưa hợp lệ.')
        # DTO mask_snapshot_ra_noi_bo.v1: kiểm toàn bộ trước khi dùng snapshot.
        for bam, muc in cum_cho.items():
            if (not isinstance(bam, str) or fullmatch(r'[0-9a-f]{64}', bam) is None
                    or not isinstance(muc, dict) or set(muc) != {'nhom', 'bi_danh', 'nguon'}
                    or any(not isinstance(muc[k], str) or not muc[k]
                           for k in ('nhom', 'bi_danh'))
                    or muc['nguon'] != 'tam'):
                raise LoiKhoQuaCore('Thông tin định danh chờ duyệt chưa hợp lệ.')
        self.da_chot = self._snapshot['da_chot']
        self._danh_muc = deepcopy(self._snapshot.get('danh_muc', []))
        self._theo_cum = {chuan_hoa(m['gia_tri']): m for m in self._danh_muc}
        self._dang_goi = self._da_chay = self._hop_le = False
        self._nhat_ky = dict(cum=[], bi_danh_tam_moi=[], bi_danh_da_dung=[], dong_yeu_cau=False,
                            cum_da_tra=[], bi_danh_da_tra=[])
        self._da_gap = set()

    def __repr__(self):
        return 'KhoQuaCore(<ẩn>)'

    def _goi(self, operation, **payload):
        ma_loi = 'MASK_XU_LY'
        try:
            return self._goi_kho(operation, ma_yeu_cau=self._ma,
                                 ma_luot=self._luot, loai=self._loai, **payload)
        except Exception as exc:
            ma = getattr(exc, 'ma', None)
            if ma in ('VIEC_MAT_LEASE', 'MASK_XUNG_DOT_LUOT'):
                ma_loi = ma
            elif getattr(exc, 'sqlstate', None) in ('40001', '40P01'):
                ma_loi = 'MASK_XUNG_DOT_LUOT'
            _xoa_loi(exc)
        if ma_loi == 'VIEC_MAT_LEASE':
            raise LoiEngine('VIEC_MAT_LEASE')
        raise LoiKhoQuaCore('Không thể hoàn tất lượt xử lý định danh.', ma=ma_loi)

    def chot(self, ket_qua=None):
        if self.da_chot:
            # Cửa chốt vẫn kiểm lại quyền, không đọc thẳng kết quả snapshot.
            return self._goi('chot_luot', phien_ban=None, nhat_ky=None, ket_qua=None)
        kq = deepcopy(ket_qua)
        kq.update(ma_yeu_cau=self._ma, ma_luot=self._luot)
        nhat_ky = self.nhat_ky
        if self._loai == 'che' and not kq['gui_duoc']:
            nhat_ky['dong_yeu_cau'] = True
        return self._goi('chot_luot', phien_ban=self._snapshot['phien_ban'],
                         nhat_ky=nhat_ky, ket_qua=kq)

    @contextmanager
    def giao_dich(self):
        if self.da_chot or self._dang_goi or self._da_chay:
            raise LoiKhoQuaCore('Lượt xử lý đã được sử dụng.')
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
        if not self._dang_goi or (ma is not None and str(ma) != self._ma):
            raise LoiKhoQuaCore('Yêu cầu không thuộc lượt xử lý.')

    @property
    def nhat_ky(self):
        if not self._hop_le or self._dang_goi:
            raise LoiKhoQuaCore('Lượt xử lý chưa hoàn tất.')
        return deepcopy(self._nhat_ky)

    def tao_yeu_cau(self):
        self._kiem()
        if self._loai != 'che':
            raise LoiKhoQuaCore('Lượt xử lý chưa hợp lệ.')
        return self._ma

    def doc_yeu_cau(self, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        muc = self._snapshot['yeu_cau']
        if muc is None or muc['trang_thai'] != 'DANG_XU_LY':
            raise LoiKhoQuaCore('Yêu cầu không còn hiệu lực.')
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
                # Chỉ nạp cụm vừa được tra; giữ nhóm/bí danh từ snapshot Core.
                muc = dict(gia_tri=gia_tri_chuan, nhom=da_co['nhom'],
                           bi_danh=da_co['bi_danh'], nguon=da_co['nguon'])
                self._theo_cum[chuan] = muc
                self._danh_muc.append(muc)
        return None if muc is None else {k: deepcopy(v) for k, v in muc.items() if k != 'gia_tri'}

    def cap_bi_danh_tam(self):
        self._kiem()
        ma = '[[MASKTAM-' + uuid4().hex + ']]'
        self._nhat_ky['bi_danh_tam_moi'].append(ma)
        return ma

    def ghi_cho_duyet(self, gia_tri, nhom, bi_danh, ma_yeu_cau):
        self._kiem(ma_yeu_cau)
        chuan = chuan_hoa(gia_tri)
        cu = self.tra_bi_danh(chuan)
        if cu is not None:
            if bi_danh != cu['bi_danh'] and bi_danh in self._nhat_ky['bi_danh_tam_moi']:
                self._nhat_ky['bi_danh_tam_moi'].remove(bi_danh)
            self.ghi_nhan_gap_lai(ma_yeu_cau, chuan, cu['nhom'])
            return cu, False
        if bi_danh not in self._nhat_ky['bi_danh_tam_moi']:
            raise LoiKhoQuaCore('Bí danh chưa được cấp trong lượt xử lý.')
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
            raise LoiKhoQuaCore('Cụm định danh chưa hợp lệ.')
        if chuan not in self._da_gap:
            self._nhat_ky['cum'].append(dict(gia_tri=muc['gia_tri'], nhom=nhom,
                                           bi_danh=muc['bi_danh'], chi_gap_lai=True))
            self._da_gap.add(chuan)

    def ghi_bi_danh_da_dung(self, ma_yeu_cau, bi_danh):
        self._kiem(ma_yeu_cau)
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
