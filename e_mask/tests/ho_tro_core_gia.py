"""Kho RAM chỉ cho DEMO/test, cùng port với kho Core tương lai.

Không nhận cờ la_demo từ bên gọi che/mở che. Mọi instance thuộc vùng DEMO cố
định. theo_phien chỉ để mô phỏng các phiên do test tin cậy cấp, KHÔNG phải
xác thực Core. Không dùng kho này cho dữ liệu vận hành hay làm bằng chứng RLS.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import re
from multiprocessing.managers import BaseManager
from threading import RLock
from types import SimpleNamespace
from uuid import uuid4

from e_mask.che_van_ban import _kiem_dinh_danh, chuan_bi_danh, chuan_hoa
from e_mask.kho_qua_core import TIEN_TO_TU_SINH
from e_mask.quyen_yeu_cau import NguCanhTinCay, loi_kho
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu


_TIEN_TO = {nhom: TIEN_TO_TU_SINH + duoi for nhom, duoi in
            {'CONG_TY': 'CT', 'CA_NHAN': 'CN', 'DIA_CHI': 'DC',
             'MA_SO_THUE': 'MST', 'TAI_KHOAN': 'TK'}.items()}


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
                        or ma_junsky.upper().startswith(TIEN_TO_TU_SINH)):
                    raise ValueError('Mã đối tượng DEMO chưa hợp lệ.')
                bi_danh = '[[' + ma_junsky + ']]'
            else:
                self._du_lieu.so += 1
                bi_danh = f'[[{_TIEN_TO.get(nhom, TIEN_TO_TU_SINH + "KHAC")}-{self._du_lieu.so:04d}]]'
            if bi_danh_tam is not None and (
                    not isinstance(bi_danh_tam, str)
                    or not re.fullmatch(r'\[\[' + TIEN_TO_TU_SINH + r'TAM-[0-9a-f]{32}\]\]', bi_danh_tam)):
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
            bi_danh = '[[' + TIEN_TO_TU_SINH + 'TAM-' + uuid4().hex + ']]'
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
                or muc['tai_lieu'] != self._tai_lieu
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
                or not re.fullmatch(r'\[\[' + TIEN_TO_TU_SINH + r'TAM-[0-9a-f]{32}\]\]', bi_danh)
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


class QuyenCoreGia:
    """Fixture quyền, do test cấp; không phải xác thực/transport thật."""

    def __init__(self, core, *, phien='phien-demo-a', module='module-demo-a',
                 nguoi_gui='nguoi-demo-a', tai_lieu='tai-lieu-demo-a', vung='DEMO'):
        self.core = core
        self.phien = (phien, module, nguoi_gui, tai_lieu, vung)
        self.thu_hoi = False
        self.ve = {}
        self.cac_kiem = []

    def cap(self, viec_id, *, buoc=1, loai='che', ma_yeu_cau=None,
            ma_luot=None):
        """Mã từ bộ cấp Core giả, tồn tại qua lần khởi tạo lại engine."""
        khoa = (viec_id, buoc, loai)
        with self.core.khoa:
            cu = self.core.ma_da_cap.get(khoa)
            if cu is None:
                if loai == 'che':
                    ma_yeu_cau = ma_yeu_cau or 'yeu-cau-demo-' + uuid4().hex
                cu = NguCanhTinCay(ma_yeu_cau, ma_luot or 'luot-demo-' + uuid4().hex, *self.phien)
                self.core.ma_da_cap[khoa] = cu
            self.ve[khoa] = cu
            return cu

    def kiem_ma(self, ma, luot, loai, thao_tac):
        with self.core.khoa:
            ctx = next((v for k, v in self.ve.items()
                        if k[2] == loai and v.ma_luot == luot and v.ma_yeu_cau == ma), None)
            if self.thu_hoi or ctx is None or (ctx.phien, ctx.module, ctx.nguoi_gui, ctx.tai_lieu, ctx.vung) != self.phien:
                raise loi_kho('MASK_MA_YEU_CAU')
            dl = self.core.bang[ctx.vung]
            yc = dl['yeu_cau'].get(ma)
            cu = dl['luot'].get(luot)
            if yc is not None and any(yc[k] != getattr(ctx, k) for k in ('module', 'nguoi_gui', 'tai_lieu')):
                raise loi_kho('MASK_MA_YEU_CAU')
            if loai == 'mo_che' and (yc is None or (yc['trang_thai'] != 'DANG_XU_LY' and cu is None)):
                raise loi_kho('MASK_MA_YEU_CAU')
            if loai == 'che' and yc is not None and yc['trang_thai'] != 'DANG_XU_LY' and cu is None:
                raise loi_kho('MASK_MA_YEU_CAU')
            self.cac_kiem.append(thao_tac)
            return ctx

    def xac_minh(self, viec, *, loai, ma_yeu_cau, thao_tac):
        ctx = self.ve.get((viec.id, viec.ngu_canh['buoc'], loai))
        if ctx is None:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
        if ma_yeu_cau is not None and ma_yeu_cau != ctx.ma_yeu_cau:
            raise loi_kho('MASK_MA_YEU_CAU')
        return self.kiem_ma(ctx.ma_yeu_cau, ctx.ma_luot, loai, thao_tac)


class KhoCoreGia:
    """Kho port giả có CAS/rollback dưới khóa; chỉ RAM, không chứng minh độ bền.

    Cả hai vùng đều dữ liệu giả; nhãn THAT chỉ kiểm tách vùng, không chứa hồ
    sơ thật. Mỗi vùng chung bảng giữa module/pháp nhân. Quyền cấp riêng.
    """

    def __init__(self):
        self.khoa = RLock()
        self.bang = {v: dict(danh_muc={}, cho_duyet={}, yeu_cau={}, luot={}, phien_ban=0)
                     for v in ('DEMO', 'THAT')}
        self.ma_da_cap = {}
        self.cac_goi = []
        self.so_chot = 0
        self.loi_sau = None
        self.mat_phan_hoi = False
        self.cho_chot = False
        self.dang_cho = {}

    def them_dinh_danh(self, *args, **kw):
        """Chỉ nạp danh mục DEMO, không phải chức năng quản trị sản phẩm."""
        kho = KhoBoNho()
        muc = kho.them_dinh_danh(*args, **kw)
        with self.khoa:
            self.bang['DEMO']['danh_muc'][chuan_hoa(muc['gia_tri'])] = muc
            self.bang['DEMO']['phien_ban'] += 1
        return muc

    def port(self, quyen):
        def goi(thao_tac, **p):
            with self.khoa:
                ctx = quyen.kiem_ma(p['ma_yeu_cau'], p['ma_luot'], p['loai'], thao_tac)
                self.cac_goi.append((thao_tac, deepcopy(p)))
                dl = self.bang[ctx.vung]
                if thao_tac == 'snapshot_luot':
                    if ctx.ma_luot in self.dang_cho:
                        raise ChuaRo('cho-demo')
                    yc = dl['yeu_cau'].get(ctx.ma_yeu_cau)
                    return deepcopy(dict(da_chot=ctx.ma_luot in dl['luot'], phien_ban=dl['phien_ban'],
                                         danh_muc=[*dl['danh_muc'].values(), *dl['cho_duyet'].values()],
                                         yeu_cau=None if yc is None else {'trang_thai': yc['trang_thai']},
                                         cum_cho_toan_vung={}, bi_danh_bo_sung={}))
                if thao_tac != 'chot_luot':
                    raise AssertionError('Thao tác port chưa được giao.')
                if ctx.ma_luot in dl['luot']:
                    return deepcopy(dl['luot'][ctx.ma_luot])
                if p['nhat_ky'] is None:
                    raise loi_kho()
                if self.cho_chot:
                    self.dang_cho[ctx.ma_luot] = (quyen, deepcopy(p))
                    raise ChuaRo('cho-demo')
                self._chot(ctx, p)
                if self.mat_phan_hoi:
                    self.mat_phan_hoi = False
                    raise ChuaRo('mat-phan-hoi-demo')
                return deepcopy(self.bang[ctx.vung]['luot'][ctx.ma_luot])
        return goi

    def hoan_tat(self, ma_luot):
        with self.khoa:
            quyen, p = self.dang_cho[ma_luot]
            ctx = quyen.kiem_ma(p['ma_yeu_cau'], p['ma_luot'], p['loai'], 'chot')
            self._chot(ctx, p)
            del self.dang_cho[ma_luot]

    def _chot(self, ctx, p):
        cu = self.bang[ctx.vung]
        if p['phien_ban'] != cu['phien_ban']:
            raise loi_kho('MASK_XUNG_DOT')
        # Dựng toàn bộ trạng thái kế tiếp; chỉ công bố một lần dưới khóa.
        dl = deepcopy(cu)
        def moc(ten):
            if self.loi_sau == ten:
                raise LoiNghiepVu('MASK_KHO_LOI', 'Lỗi DEMO giữa chốt.')
        ma = ctx.ma_yeu_cau
        yc = dl['yeu_cau'].get(ma)
        if yc is None:
            if p['loai'] != 'che':
                raise loi_kho('MASK_MA_YEU_CAU')
            yc = dict(module=ctx.module, nguoi_gui=ctx.nguoi_gui, tai_lieu=ctx.tai_lieu,
                      trang_thai='DANG_XU_LY', cum_da_gap=set(), bi_danh_tam_da_dung=set())
            dl['yeu_cau'][ma] = yc
        nk = p['nhat_ky']
        cac_bi_danh = {chuan_bi_danh(b) for muc in [*dl['danh_muc'].values(), *dl['cho_duyet'].values()]
                      for b in (muc['bi_danh'], muc.get('bi_danh_tam')) if b}
        for muc in nk['cum']:
            khoa = chuan_hoa(muc['gia_tri'])
            co = dl['danh_muc'].get(khoa) or dl['cho_duyet'].get(khoa)
            if co is None:
                if muc['chi_gap_lai'] or chuan_bi_danh(muc['bi_danh']) in cac_bi_danh:
                    raise loi_kho('MASK_XUNG_DOT')
                if muc['bi_danh'] not in nk['bi_danh_tam_moi']:
                    raise loi_kho()
                co = dict(gia_tri=muc['gia_tri'], nhom=muc['nhom'], bi_danh=muc['bi_danh'],
                          nguon='tam', so_lan_gap=0)
                dl['cho_duyet'][khoa] = co
                cac_bi_danh.add(chuan_bi_danh(co['bi_danh']))
            elif co['nhom'] != muc['nhom'] or co['bi_danh'] != muc['bi_danh']:
                raise loi_kho('MASK_XUNG_DOT')
            moc('alias')
            if co['nguon'] == 'tam' and khoa not in yc['cum_da_gap']:
                co['so_lan_gap'] += 1
                yc['cum_da_gap'].add(khoa)
            moc('dem')
        moc('hang_cho')
        for bi_danh in nk['bi_danh_da_dung']:
            if chuan_bi_danh(bi_danh) not in cac_bi_danh:
                raise loi_kho()
            for muc in [*dl['danh_muc'].values(), *dl['cho_duyet'].values()]:
                if ((muc['nguon'] == 'tam' and chuan_bi_danh(muc['bi_danh']) == chuan_bi_danh(bi_danh))
                        or (muc.get('bi_danh_tam') and chuan_bi_danh(muc['bi_danh_tam']) == chuan_bi_danh(bi_danh))):
                    yc['bi_danh_tam_da_dung'].add(chuan_bi_danh(bi_danh))
        moc('tham_chieu')
        if nk['dong_yeu_cau']:
            yc['trang_thai'] = 'DA_DONG'
        moc('yeu_cau')
        dl['luot'][ctx.ma_luot] = deepcopy(p['ket_qua'])
        dl['phien_ban'] += 1
        moc('luot')
        self.bang[ctx.vung] = dl
        self.so_chot += 1


class _MayKhoGia:
    """Giữ cùng một KhoCoreGia trong RAM cho hai tiến trình engine test."""

    def __init__(self):
        self.core = KhoCoreGia()
        self.quyen = {i: QuyenCoreGia(self.core) for i in range(2)}
        for i, quyen in self.quyen.items():
            quyen.cap(f'viec-demo-{i}')

    def xac_minh(self, hang, viec_id, buoc, **doi):
        viec = SimpleNamespace(id=viec_id, ngu_canh={'buoc': buoc})
        try:
            return True, self.quyen[hang].xac_minh(viec, **doi)
        except LoiNghiepVu as exc:
            return False, exc.ma

    def goi(self, hang, thao_tac, **p):
        try:
            return True, self.core.port(self.quyen[hang])(thao_tac, **p)
        except LoiNghiepVu as exc:
            # Ngoại lệ SDK cần hai đối số, không truyền pickle ngoại lệ đó.
            return False, exc.ma

    def xem(self):
        with self.core.khoa:
            return deepcopy(self.core.bang), self.core.so_chot


class MayKhoGia(BaseManager):
    pass


MayKhoGia.register('kho', _MayKhoGia)
