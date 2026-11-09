"""Kho RAM chỉ cho DEMO/test, cùng port với kho Core tương lai.

Không nhận cờ la_demo từ bên gọi che/mở che. Mọi instance thuộc vùng DEMO cố
định. theo_phien chỉ để mô phỏng các phiên do test tin cậy cấp, KHÔNG phải
xác thực Core. Không dùng kho này cho dữ liệu vận hành hay làm bằng chứng RLS.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import re
from threading import RLock
from uuid import uuid4

from .che_van_ban import _kiem_dinh_danh, chuan_bi_danh, chuan_hoa


_TIEN_TO = {'CONG_TY': 'MASKCT', 'CA_NHAN': 'MASKCN', 'DIA_CHI': 'MASKDC',
            'MA_SO_THUE': 'MASKMST', 'TAI_KHOAN': 'MASKTK'}


class _DuLieuDemo:
    def __init__(self):
        self.khoa = RLock()
        self.danh_muc = {}
        self.cho_duyet = {}
        self.yeu_cau = {}
        self.so = 0


class KhoBoNho:
    def __init__(self, dinh_danh=(), *, module='demo_mask', nguoi_gui='nguoi_demo_a',
                 tai_lieu='tai_lieu_demo'):
        self._du_lieu = _DuLieuDemo()
        self._gan_phien(module, nguoi_gui, tai_lieu)
        for muc in dinh_danh:
            self.them_dinh_danh(**muc)

    def _gan_phien(self, module, nguoi_gui, tai_lieu):
        if any(not isinstance(v, str) or not v.strip() for v in (module, nguoi_gui, tai_lieu)):
            raise ValueError('Phiên DEMO chưa hợp lệ.')
        self._phien = (module, nguoi_gui)
        self._tai_lieu = tai_lieu

    def theo_phien(self, *, module, nguoi_gui, tai_lieu='tai_lieu_demo'):
        """Fixture phiên khác, chung bảng DEMO; chỉ bên dựng test/DEMO được dùng."""
        kho = object.__new__(type(self))
        kho._du_lieu = self._du_lieu
        kho._gan_phien(module, nguoi_gui, tai_lieu)
        return kho

    @contextmanager
    def giao_dich(self):
        dl = self._du_lieu
        with dl.khoa:
            truoc = deepcopy((dl.danh_muc, dl.cho_duyet, dl.yeu_cau, dl.so))
            try:
                yield self
            except BaseException:
                dl.danh_muc, dl.cho_duyet, dl.yeu_cau, dl.so = truoc
                raise

    def _muc_theo_bi_danh(self, bi_danh):
        khoa = chuan_bi_danh(bi_danh)
        if not khoa:
            return None
        for muc in [*self._du_lieu.danh_muc.values(), *self._du_lieu.cho_duyet.values()]:
            if any(chuan_bi_danh(b) == khoa for b in
                   (muc['bi_danh'], muc.get('bi_danh_tam') or '')):
                return muc
        return None

    def them_dinh_danh(self, gia_tri, nhom='KHAC', *, ma_junsky=None, bi_danh_tam=None):
        """Nạp danh mục DEMO ban đầu, không phải thao tác duyệt của lát 4."""
        _kiem_dinh_danh([{'gia_tri': gia_tri, 'nhom': nhom}])
        with self.giao_dich():
            if self.tra_bi_danh(chuan_hoa(gia_tri)) is not None:
                raise ValueError('Định danh DEMO bị trùng.')
            if ma_junsky is not None:
                if (not isinstance(ma_junsky, str)
                        or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', ma_junsky)
                        or ma_junsky.upper().startswith('MASK')):
                    raise ValueError('Mã đối tượng DEMO chưa hợp lệ.')
                bi_danh = '[[' + ma_junsky + ']]'
            else:
                self._du_lieu.so += 1
                bi_danh = f'[[{_TIEN_TO.get(nhom, "MASKKHAC")}-{self._du_lieu.so:04d}]]'
            if bi_danh_tam is not None and (
                    not isinstance(bi_danh_tam, str)
                    or not re.fullmatch(r'\[\[MASKTAM-[0-9a-f]{32}\]\]', bi_danh_tam)):
                raise ValueError('Bí danh tạm DEMO chưa hợp lệ.')
            if self._muc_theo_bi_danh(bi_danh) or (bi_danh_tam and self._muc_theo_bi_danh(bi_danh_tam)):
                raise ValueError('Bí danh DEMO bị trùng.')
            muc = {'gia_tri': gia_tri, 'nhom': nhom, 'bi_danh': bi_danh,
                   'bi_danh_tam': bi_danh_tam, 'nguon': 'chinh_thuc'}
            self._du_lieu.danh_muc[chuan_hoa(gia_tri)] = muc
            return deepcopy(muc)

    def liet_ke_dinh_danh(self):
        return deepcopy([*self._du_lieu.danh_muc.values(), *self._du_lieu.cho_duyet.values()])

    def tra_bi_danh(self, gia_tri_chuan):
        muc = (self._du_lieu.danh_muc.get(gia_tri_chuan)
               or self._du_lieu.cho_duyet.get(gia_tri_chuan))
        return deepcopy(muc)

    def cap_bi_danh_tam(self):
        while True:
            bi_danh = '[[MASKTAM-' + uuid4().hex + ']]'
            if self._muc_theo_bi_danh(bi_danh) is None:
                return bi_danh

    def tao_yeu_cau(self):
        ma = str(uuid4())
        self._du_lieu.yeu_cau[ma] = {
            'module': self._phien[0], 'nguoi_gui': self._phien[1],
            'tai_lieu': self._tai_lieu, 'trang_thai': 'DANG_XU_LY',
            'la_demo': True, 'bi_danh_tam_da_dung': set(), 'cum_da_gap': set()}
        return ma

    def doc_yeu_cau(self, ma_yeu_cau):
        muc = self._du_lieu.yeu_cau.get(ma_yeu_cau)
        if (muc is None or (muc['module'], muc['nguoi_gui']) != self._phien
                or muc['la_demo'] is not True or muc['trang_thai'] != 'DANG_XU_LY'):
            raise ValueError('Yêu cầu không thuộc phiên hiện tại hoặc đã đóng.')
        return deepcopy(muc)

    def ghi_cho_duyet(self, gia_tri, nhom, bi_danh, ma_yeu_cau):
        """Tạo cụm nếu thiếu; đếm bằng ghi_nhan_gap_lai trong cùng giao dịch."""
        self.doc_yeu_cau(ma_yeu_cau)
        _kiem_dinh_danh([{'gia_tri': gia_tri, 'nhom': nhom}])
        muc = self.tra_bi_danh(chuan_hoa(gia_tri))
        if muc is not None:
            return muc, False
        if (not isinstance(bi_danh, str)
                or not re.fullmatch(r'\[\[MASKTAM-[0-9a-f]{32}\]\]', bi_danh)
                or self._muc_theo_bi_danh(bi_danh)):
            raise ValueError('Bí danh tạm DEMO chưa hợp lệ.')
        muc = {'gia_tri': gia_tri, 'nhom': nhom, 'bi_danh': bi_danh,
               'nguon': 'tam', 'ma_yeu_cau': ma_yeu_cau, 'so_lan_gap': 0}
        self._du_lieu.cho_duyet[chuan_hoa(gia_tri)] = muc
        return deepcopy(muc), True

    def ghi_nhan_gap_lai(self, ma_yeu_cau, cum_chuan, nhom):
        """Ghi một lần cho mỗi yêu cầu + cụm; khóa cả kiểm trùng và tăng đếm."""
        dl = self._du_lieu
        with dl.khoa:
            self.doc_yeu_cau(ma_yeu_cau)
            cum_chuan = chuan_hoa(cum_chuan)
            muc = dl.danh_muc.get(cum_chuan) or dl.cho_duyet.get(cum_chuan)
            if muc is None or muc['nhom'] != nhom:
                raise ValueError('Không tìm được định danh đúng nhóm trong kho DEMO.')
            if muc['nguon'] == 'chinh_thuc':
                return
            da_gap = dl.yeu_cau[ma_yeu_cau]['cum_da_gap']
            if cum_chuan not in da_gap:
                muc['so_lan_gap'] += 1
                da_gap.add(cum_chuan)

    def ghi_bi_danh_da_dung(self, ma_yeu_cau, bi_danh):
        self.doc_yeu_cau(ma_yeu_cau)
        tap = self._du_lieu.yeu_cau[ma_yeu_cau]['bi_danh_tam_da_dung']
        for b in bi_danh:
            muc = self._muc_theo_bi_danh(b)
            if muc is None:
                raise ValueError('Không tìm được bí danh trong kho DEMO.')
            if muc['nguon'] == 'tam' or chuan_bi_danh(b) == chuan_bi_danh(muc.get('bi_danh_tam') or ''):
                tap.add(chuan_bi_danh(b))

    def tra_dinh_danh(self, bi_danh_chuan):
        muc = self._muc_theo_bi_danh(bi_danh_chuan)
        return muc['gia_tri'] if muc else None

    def dong_yeu_cau(self, ma_yeu_cau):
        self.doc_yeu_cau(ma_yeu_cau)
        self._du_lieu.yeu_cau[ma_yeu_cau]['trang_thai'] = 'DA_DONG'

    def so_cum_cho_duyet(self):
        """Chỉ số DEMO, không xuất cụm gốc qua kết quả che."""
        return len(self._du_lieu.cho_duyet)
