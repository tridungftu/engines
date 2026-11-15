"""Kho nhận diện bí mật SDK 2.2; phần RAM lịch sử không nhận ngăn SDK.

KhoNganBiMat chỉ trả metadata/null+cờ. Các lớp AnhNgan/DauNgan/PortNgan
cũ còn cho hồi quy RAM trước R3/R4/R5; tuyệt đối không dùng chúng với Core.
"""
from copy import deepcopy
from decimal import Decimal
from functools import wraps
from hashlib import sha256
import json
from re import fullmatch
from uuid import uuid4

from kho_tri_thuc_sdk.engine import (ChuaRo, LoiDuongTruyen, LoiNghiepVu,
                                   NganEngine, NganXungDot as XungDotSDK, ViecDaHuy)

from .che_van_ban import _kiem_dinh_danh, chuan_hoa, chuan_bi_danh
from .khoi_tao_ngan import PHIEN_BAN_CHUAN_HOA, can_bao_dam_core, ngan_cua_viec
from .ngan import CauHinhKhongHopLe, NganKhongHopLe, NganXungDot
from .nguon.privacy.core import CATEGORIES
from .quyen_yeu_cau import loi_kho, xac_minh


BANG = ('dinh_danh', 'bi_danh_tam', 'cho_duyet', 'ma_yeu_cau', 'dau_gap')
TIEN_TO = {'CONG_TY': 'MASKCT', 'CA_NHAN': 'MASKCN', 'DIA_CHI': 'MASKDC',
           'MA_SO_THUE': 'MASKMST', 'TAI_KHOAN': 'MASKTK'}
CAC_TIEN_TO = frozenset((*TIEN_TO.values(), 'MASKKHAC', 'MASKTAM'))
# Khai RAM lịch sử; khác hai bảng SDK đã khai bởi R1.
KHAI_NGAN = [dict(bang=bang, pham_vi='engine', khoa=['vung', 'khoa'],
                  duy_nhat=[['vung', 'bi_danh']] if bang in BANG[:3] else [])
             for bang in BANG]


def khoa_dau(*phan):
    return json.dumps(phan, ensure_ascii=True, separators=(',', ':'))


def khoa_muc(vung, khoa):
    return {'vung': vung, 'khoa': khoa}


def bi_danh_moi(nhom):
    return '[[' + TIEN_TO.get(nhom, 'MASKKHAC') + '-' + uuid4().hex + ']]'


def _kiem_id(ma):
    if not isinstance(ma, str) or fullmatch(r'(?:[0-9a-f]{32}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})', ma) is None:
        raise loi_kho()
    return ma


def _kiem_phien(phien):
    if type(phien) is not int or phien < 1:
        raise loi_kho('MASK_XUNG_DOT')


def bao_ve_sdk(ham):
    """Không chuyển thông điệp, bản ghi hay traceback nguồn ra khỏi kho."""
    @wraps(ham)
    def goi(*args, **kwargs):
        try:
            return ham(*args, **kwargs)
        except ChuaRo:
            raise ChuaRo(args[0]._tuong_quan) from None
        except ViecDaHuy:
            raise
        except XungDotSDK:
            raise loi_kho('MASK_XUNG_DOT') from None
        except LoiNghiepVu as exc:
            if exc.ma == 'MASK_KHO_CAN_CORE':
                can_bao_dam_core()
            if exc.ma == 'MASK_QUA_GIOI_HAN':
                raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Mỗi lô chỉ nhận tối đa 100 thay đổi.') from None
            raise loi_kho(exc.ma) from None
        except Exception:
            raise loi_kho() from None
    return goi


class KhoNganBiMat:
    """Adapter nội bộ R2, chỉ lấy viec.ngan; không giữ ứng viên hay map.

    Duyệt/sửa metadata là primitive cho R7, nơi phải xác minh biên nhận Admin.
    Tạo tên/đếm gặp bị chặn C-P4-03, không mô phỏng bảo đảm còn thiếu bằng RAM.
    """
    def __init__(self, viec, *, vung):
        if vung not in {'DEMO', 'THAT'}:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
        self._ngan = ngan_cua_viec(viec)
        self._viec, self._vung = viec, vung
        self._tuong_quan, self._chua_ro = 'mask-ngan-' + uuid4().hex, False

    def __repr__(self):
        return 'KhoNganBiMat(<ẩn>)'

    def _kiem_chua_ro(self):
        if self._chua_ro:
            raise ChuaRo(self._tuong_quan) from None

    def _doc(self, ma):
        self._viec.kiem_huy()
        dong = self._ngan.doc('dinh_danh', {'id_dinh_danh': _kiem_id(ma)})
        if dong is not None and dong.gia_tri.get('vung_du_lieu') != self._vung:
            return None
        return dong

    def _metadata(self, dong):
        muc = dong.gia_tri
        _kiem_id(muc.get('id_dinh_danh'))
        _kiem_phien(dong.row_version)
        # SDK 2.2 trả cột so bằng chuỗi thập phân, không dùng mock trả int.
        so_gap = muc.get('so_gap')
        if type(so_gap) not in (int, str):
            raise loi_kho()
        so_gap = Decimal(str(so_gap))
        if (muc.get('vung_du_lieu') != self._vung
                or muc.get('phien_ban_chuan_hoa') != PHIEN_BAN_CHUAN_HOA
                or muc.get('nhom') not in CATEGORIES
                or muc.get('trang_thai') not in {'CHO_DUYET', 'CHINH_THUC', 'TU_CHOI'}
                or not so_gap.is_finite() or so_gap < 0 or so_gap != so_gap.to_integral_value()
                or any(muc.get(k) is not None or muc.get(k + '_da_ma_hoa') is not True
                       for k in ('gia_tri_goc', 'gia_tri_chuan'))):
            raise loi_kho()
        # Chỉ chiếu allowlist, không sao JSON/cột bổ sung hoặc khóa từ nguồn.
        return {k: muc[k] for k in ('id_dinh_danh', 'vung_du_lieu', 'phien_ban_chuan_hoa',
                'nhom', 'trang_thai', 'so_gap', 'gia_tri_goc', 'gia_tri_chuan',
                'gia_tri_goc_da_ma_hoa', 'gia_tri_chuan_da_ma_hoa')} | {
                    'row_version': dong.row_version, 'so_gap': int(so_gap)}

    def _ket_qua(self, dong):
        muc = self._metadata(dong)
        muc.update(bi_danh=None, id_bi_danh=None, nguon=None)
        if muc['trang_thai'] == 'CHINH_THUC':
            trang = self._ngan.tim('bi_danh', loc={
                'id_dinh_danh': muc['id_dinh_danh'], 'vung_du_lieu': self._vung,
                'trang_thai': 'CHINH_THUC'}, gioi_han=2)
            if len(trang.danh_sach) != 1 or trang.tiep is not None:
                raise loi_kho('MASK_XUNG_DOT')
            alias = trang.danh_sach[0].gia_tri
            _kiem_id(alias.get('id_bi_danh'))
            chu = alias.get('bi_danh')
            if (not isinstance(chu, str)
                    or fullmatch(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]', chu) is None
                    or chu[2:-2].upper().startswith('MASKTAM')
                    or alias.get('bi_danh_chuan') != chuan_bi_danh(chu)):
                raise loi_kho()
            muc.update(bi_danh=chu, id_bi_danh=alias['id_bi_danh'], nguon='chinh_thuc')
            cuoi = self._doc(muc['id_dinh_danh'])
            if cuoi is None or cuoi.row_version != dong.row_version:
                raise loi_kho('MASK_XUNG_DOT')
        return muc

    @bao_ve_sdk
    def doc(self, id_dinh_danh):
        dong = self._doc(id_dinh_danh)
        return None if dong is None else self._ket_qua(dong)

    @bao_ve_sdk
    def tim_ung_vien(self, gia_tri, nhom):
        _kiem_dinh_danh([{'gia_tri': gia_tri, 'nhom': nhom}])
        self._viec.kiem_huy()
        trang = self._ngan.tim('dinh_danh', loc={
            'gia_tri_chuan': chuan_hoa(gia_tri), 'vung_du_lieu': self._vung,
            'phien_ban_chuan_hoa': PHIEN_BAN_CHUAN_HOA}, gioi_han=2)
        # Không gom các giá trị null thành cùng thực thể, không lấy dòng đầu.
        if len(trang.danh_sach) > 1 or trang.tiep is not None:
            raise loi_kho('MASK_XUNG_DOT')
        if not trang.danh_sach:
            return None
        muc = self._ket_qua(trang.danh_sach[0])
        if muc['nhom'] != nhom:
            raise loi_kho('MASK_XUNG_DOT')
        return muc

    def _sua_lo(self, lenh):
        self._kiem_chua_ro()
        self._viec.kiem_huy()
        try:
            with self._ngan.lo() as lo:
                for thao_tac, bang, khoa, gia_tri, phien in lenh:
                    if thao_tac == 'them':
                        lo.them(bang, gia_tri)
                    else:
                        lo.sua(bang, khoa, gia_tri, row_version=phien)
                self._viec.kiem_huy()
        except (XungDotSDK, ViecDaHuy):
            raise
        except LoiNghiepVu as exc:
            # NganEngine đổi lỗi NGAN_* sau gửi lại thành LoiNghiepVu.
            # Cờ thử lại không xác nhận được rằng nguồn chưa ghi.
            if exc.ma in {'NGAN_DU_LIEU_SAI', 'NGAN_KHONG_THAY', 'NGAN_CAN_VIEC',
                          'NGAN_LO_QUA_LON', 'NGAN_KHONG_XOA', 'ENGINE_CHUA_SAN_SANG',
                          'KHOA_CHONG_TRUNG_KHAC_NOI_DUNG'} and not exc.thu_lai_duoc:
                raise
            self._chua_ro = True
            raise ChuaRo(self._tuong_quan) from None
        except LoiDuongTruyen as exc:
            if (exc.http_status is not None and 400 <= exc.http_status < 500
                    and exc.http_status not in {408, 429} and not exc.thu_lai_duoc):
                raise loi_kho() from None
            self._chua_ro = True
            raise ChuaRo(self._tuong_quan) from None
        except Exception:
            # Đã giao lô cho nguồn nhưng không có xác nhận xác định.
            self._chua_ro = True
            raise ChuaRo(self._tuong_quan) from None

    @bao_ve_sdk
    def sua_metadata(self, thay_doi):
        """Bản vá metadata, CAS từng ID trong một lô; không chia lô ngầm."""
        self._kiem_chua_ro()
        if not isinstance(thay_doi, (list, tuple)) or not thay_doi:
            raise loi_kho()
        if len(thay_doi) > 100:
            raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Mỗi lô chỉ nhận tối đa 100 thay đổi.')
        lenh, da_co = [], set()
        for doi in thay_doi:
            if not isinstance(doi, dict) or set(doi) != {'id_dinh_danh', 'row_version', 'gia_tri'}:
                raise loi_kho()
            ma, phien, va = doi['id_dinh_danh'], doi['row_version'], doi['gia_tri']
            _kiem_id(ma)
            _kiem_phien(phien)
            if (ma in da_co or not isinstance(va, dict) or not va
                    or set(va) - {'nhom', 'trang_thai'}
                    or ('nhom' in va and va['nhom'] not in CATEGORIES)
                    or ('trang_thai' in va and va['trang_thai'] not in {'CHO_DUYET', 'TU_CHOI'})):
                raise loi_kho()
            dong = self._doc(ma)
            if dong is None or dong.row_version != phien:
                raise loi_kho('MASK_XUNG_DOT')
            if self._metadata(dong)['trang_thai'] == 'CHINH_THUC' and 'trang_thai' in va:
                raise loi_kho('MASK_XUNG_DOT')
            da_co.add(ma)
            lenh.append(('sua', 'dinh_danh', {'id_dinh_danh': ma}, dict(va), phien))
        self._sua_lo(lenh)

    @bao_ve_sdk
    def duyet_cung_id(self, id_dinh_danh, *, row_version, bi_danh):
        """Primitive R7 sau xác minh Admin: đổi trạng thái, không chép bí mật."""
        self._kiem_chua_ro()
        _kiem_phien(row_version)
        dong = self._doc(id_dinh_danh)
        if dong is None or dong.row_version != row_version:
            raise loi_kho('MASK_XUNG_DOT')
        muc = self._metadata(dong)
        if muc['trang_thai'] != 'CHO_DUYET':
            raise loi_kho('MASK_XUNG_DOT')
        if (not isinstance(bi_danh, str)
                or fullmatch(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]', bi_danh) is None
                or bi_danh[2:-2].upper().startswith('MASKTAM')):
            raise loi_kho()
        alias = dict(id_bi_danh=uuid4().hex, id_dinh_danh=id_dinh_danh,
                     vung_du_lieu=self._vung, bi_danh=bi_danh,
                     bi_danh_chuan=chuan_bi_danh(bi_danh), trang_thai='CHINH_THUC')
        # them + duy nhất: lay_hoac_tao có thể trả alias thuộc ID khác.
        self._sua_lo([
            ('sua', 'dinh_danh', {'id_dinh_danh': id_dinh_danh}, {'trang_thai': 'CHINH_THUC'}, row_version),
            ('them', 'bi_danh', None, alias, None),
        ])

    def lay_hoac_tao(self, *args, **kwargs):
        can_bao_dam_core()

    def ghi_nhan_gap_lai(self, *args, **kwargs):
        can_bao_dam_core()


def _bam_ket_qua(kq):
    return sha256(json.dumps(kq, sort_keys=True, ensure_ascii=True,
                             allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def bao_ve_loi_ngan(ham):
    """Chặn thông điệp ngoại lệ của ngăn trước khi SDK có thể in traceback."""
    @wraps(ham)
    def goi(*args, **kwargs):
        try:
            return ham(*args, **kwargs)
        except (ChuaRo, ViecDaHuy, LoiDuongTruyen):
            raise
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None
        except (NganKhongHopLe, CauHinhKhongHopLe) as exc:
            lop = type(exc)
            raise LoiNghiepVu(lop.ma, lop.thong_diep, thu_lai_duoc=lop.thu_lai_duoc) from None
        except LoiNghiepVu as exc:
            # Ngăn tương lai có thể ném ngay LoiNghiepVu. Không coi câu của
            # bên ngoài là an toàn chỉ vì ngoại lệ đã mang kiểu nghiệp vụ.
            if exc.ma == 'MASK_QUA_GIOI_HAN':
                raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Số thay đổi vượt giới hạn một giao dịch. Cần chia nhỏ yêu cầu.') from None
            raise loi_kho(exc.ma) from None
        except Exception:
            raise loi_kho() from None
    return goi


def doc_het(ngan, bang, vung):
    if isinstance(ngan, NganEngine):
        can_bao_dam_core()
    ds, tiep = {}, None
    while True:
        trang = ngan.tim(bang, loc={'vung': vung}, gioi_han=500, tiep=tiep)
        for muc in trang.danh_sach:
            ds[muc.gia_tri['khoa']] = muc
        tiep = trang.tiep
        if tiep is None:
            return ds


class AnhNgan:
    """Đọc trước CAS chung; nếu snapshot đổi thì lô chốt bị từ chối toàn bộ."""
    @bao_ve_loi_ngan
    def __init__(self, ngan, vung):
        if isinstance(ngan, NganEngine):
            can_bao_dam_core()
        self.ngan, self.vung = ngan, vung
        khoa = khoa_muc(vung, 'phien')
        if ngan.doc('dau_gap', khoa) is None:
            with ngan.lo() as lo:
                lo.lay_hoac_tao('dau_gap', khoa, {'so': 0})
        self.phien = ngan.doc('dau_gap', khoa)
        self.cu = {b: doc_het(ngan, b, vung) for b in BANG}
        self.moi = {b: {k: deepcopy(m.gia_tri) for k, m in ds.items()} for b, ds in self.cu.items()}

    def dat(self, bang, khoa, gia_tri):
        self.moi[bang][khoa] = dict(deepcopy(gia_tri), **khoa_muc(self.vung, khoa))

    @bao_ve_loi_ngan
    def chot(self):
        lenh = []
        for b in BANG:
            for k in self.cu[b].keys() | self.moi[b].keys():
                if b == 'dau_gap' and k == 'phien':
                    continue
                cu, moi = self.cu[b].get(k), self.moi[b].get(k)
                if cu is not None and cu.gia_tri == moi:
                    continue
                lenh.append((b, k, cu, moi))
        # sua là bản vá: bỏ trường phải xóa/tạo lại trong cùng lô có CAS.
        so_lenh = sum(2 if cu is not None and moi is not None
                      and cu.gia_tri.keys() - moi.keys() else 1
                      for _, _, cu, moi in lenh)
        if so_lenh + 1 > 100:
            raise LoiNghiepVu('MASK_QUA_GIOI_HAN', 'Số thay đổi vượt giới hạn một giao dịch. Cần chia nhỏ yêu cầu.')
        try:
            with self.ngan.lo() as lo:
                lo.sua('dau_gap', khoa_muc(self.vung, 'phien'),
                       {'so': self.phien.gia_tri['so'] + 1}, row_version=self.phien.row_version)
                for b, k, cu, moi in lenh:
                    khoa = khoa_muc(self.vung, k)
                    if cu is None:
                        lo.them(b, khoa, moi)
                    elif moi is None:
                        lo.xoa(b, khoa, row_version=cu.row_version)
                    elif cu.gia_tri.keys() - moi.keys():
                        lo.xoa(b, khoa, row_version=cu.row_version)
                        lo.them(b, khoa, moi)
                    else:
                        lo.sua(b, khoa, moi, row_version=cu.row_version)
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None


class DauNgan:
    """Dấu phục hồi của port MASK-3, cùng ngăn; không chứa tên/tài liệu."""
    def __init__(self, ngan):
        if isinstance(ngan, NganEngine):
            can_bao_dam_core()
        self.ngan = ngan

    @bao_ve_loi_ngan
    def ghi(self, *, vung, ma_luot, ma_yeu_cau, bam_dau_vao, trang_thai=1, bam_chot=None):
        tuong_quan = sha256(json.dumps([vung, ma_luot], ensure_ascii=True).encode()).hexdigest()
        khoa = khoa_muc(vung, khoa_dau('phuc_hoi', tuong_quan))
        cu = self.ngan.doc('dau_gap', khoa)
        moi = dict(yeu_cau=sha256(ma_yeu_cau.encode()).hexdigest(), dau_vao=bam_dau_vao,
                   chot=bam_chot or '0' * 64, tuong_quan=tuong_quan, trang_thai=trang_thai)
        if cu:
            if any(cu.gia_tri[k] != moi[k] for k in ('yeu_cau', 'dau_vao')):
                raise loi_kho('MASK_XUNG_DOT')
            if trang_thai == 1 or cu.gia_tri['trang_thai'] == 4:
                return deepcopy(cu.gia_tri)
            if bam_chot is None:
                moi['chot'] = cu.gia_tri['chot']
        try:
            with self.ngan.lo() as lo:
                if cu:
                    lo.sua('dau_gap', khoa, moi, row_version=cu.row_version)
                else:
                    lo.them('dau_gap', khoa, moi)
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None
        return deepcopy(moi)


class PortNgan:
    """Adapter snapshot/chốt cho lõi MASK-3, chỉ dùng API Ngan công bố."""
    def __init__(self, ngan, quyen, viec, *, loai, ma_yeu_cau, bam_dau_vao):
        if isinstance(ngan, NganEngine):
            can_bao_dam_core()
        self.ngan, self.quyen, self.viec = ngan, quyen, viec
        self.loai, self.ma, self.bam = loai, ma_yeu_cau, bam_dau_vao
        self.ctx = xac_minh(quyen, viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        self.anh = None

    def _kiem(self, thao_tac):
        ctx = xac_minh(self.quyen, self.viec, loai=self.loai, ma_yeu_cau=self.ctx.ma_yeu_cau,
                       thao_tac=thao_tac)
        if ctx != self.ctx:
            raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
        return ctx

    def __call__(self, thao_tac, *, ma_yeu_cau, ma_luot, loai, **p):
        try:
            return self._goi(thao_tac, ma_yeu_cau, ma_luot, loai, p)
        except NganXungDot:
            raise loi_kho('MASK_XUNG_DOT') from None

    def _goi(self, thao_tac, ma, luot, loai, p):
        ctx = self._kiem('snapshot' if thao_tac == 'snapshot_luot' else 'chot')
        if (ma, luot, loai) != (ctx.ma_yeu_cau, ctx.ma_luot, self.loai):
            raise loi_kho('MASK_MA_YEU_CAU')
        if thao_tac == 'snapshot_luot':
            self.anh = AnhNgan(self.ngan, ctx.vung)
        anh, yc_khoa = self.anh, ma
        dl = anh.moi
        yc = dl['ma_yeu_cau'].get(yc_khoa)
        da_chot = dl['dau_gap'].get(khoa_dau('luot', luot))
        if yc and any(yc[k] != getattr(ctx, k) for k in ('module', 'nguoi_gui', 'tai_lieu')):
            raise loi_kho('MASK_MA_YEU_CAU')
        if da_chot and (da_chot['bam'] != self.bam or da_chot['ma_yeu_cau'] != ma or da_chot['loai'] != loai):
            raise loi_kho('MASK_XUNG_DOT')
        if (loai == 'mo_che' and yc is None) or (yc and yc['trang_thai'] != 'DANG_XU_LY' and not da_chot):
            raise loi_kho('MASK_MA_YEU_CAU')
        if thao_tac == 'snapshot_luot':
            danh_muc = list(dl['dinh_danh'].values()) + list(dl['cho_duyet'].values())
            tam_duoc_dung = {m['bi_danh'] for m in dl['dau_gap'].values()
                            if m.get('loai_dau') == 'tham_chieu' and m.get('ma_yeu_cau') == ma}
            bo_sung = {k: m['gia_tri'] for k, m in dl['bi_danh_tam'].items() if k in tam_duoc_dung}
            tam_theo_cum = {chuan_hoa(m['gia_tri']): m for b, m in dl['bi_danh_tam'].items() if b in tam_duoc_dung}
            # Một cụm chờ có thể đã được che trong nhiều yêu cầu bằng các mã
            # tạm khác nhau. Chỉ chọn lại mã đã sinh cho yêu cầu hiện tại.
            for i, muc in enumerate(danh_muc):
                if muc['nguon'] == 'tam':
                    rieng = tam_theo_cum.get(chuan_hoa(muc['gia_tri']))
                    if rieng:
                        danh_muc[i] = dict(muc, bi_danh=rieng['bi_danh'])
            # Giao lại dùng đúng lựa chọn đã chốt; duyệt/dọn không đổi kết quả cũ.
            if da_chot:
                chon = [m for m in dl['dau_gap'].values() if m.get('loai_dau') == 'lua_chon' and m.get('ma_luot') == luot]
                danh_muc = [dict(m['dinh_danh']) for m in chon if m.get('de_che')]
                bo_sung = {chuan_bi_danh(m['dinh_danh']['bi_danh']): m['dinh_danh']['gia_tri']
                           for m in chon if chuan_bi_danh(m['dinh_danh']['bi_danh']) in tam_duoc_dung}
                if loai == 'mo_che':
                    danh_muc = list(dl['dinh_danh'].values())
            if yc and da_chot:
                yc = dict(yc, trang_thai='DANG_XU_LY')
            return dict(da_chot=False, phien_ban=anh.phien.row_version, yeu_cau=deepcopy(yc),
                        danh_muc=deepcopy(danh_muc), bi_danh_bo_sung=bo_sung,
                        bi_danh_tam_duoc_dung=sorted(tam_duoc_dung),
                        cum_cho_toan_vung={}, da_phuc_hoi=bool(da_chot))
        if thao_tac != 'chot_luot' or p.get('nhat_ky') is None or p.get('phien_ban') != anh.phien.row_version:
            raise loi_kho('MASK_XUNG_DOT')
        nk, kq = p['nhat_ky'], deepcopy(p['ket_qua'])
        if da_chot:
            if loai == 'che':
                kq['cho_duyet'] = {'so_cum_vua_them': da_chot['so_moi']}
            if _bam_ket_qua(kq) != da_chot['bam_ket_qua']:
                # Thay tài nguyên/logic không được âm thầm đổi kết quả đã chốt.
                raise loi_kho('MASK_XUNG_DOT')
            anh.chot()  # CAS bảo vệ cả lần đọc lại với quyền mới kiểm.
            return kq
        for muc in nk['cum']:
            khoa = chuan_hoa(muc['gia_tri'])
            hien = dl['dinh_danh'].get(khoa) or dl['cho_duyet'].get(khoa)
            b = chuan_bi_danh(muc['bi_danh'])
            if not muc['chi_gap_lai']:
                if muc['bi_danh'] not in nk['bi_danh_tam_moi'] or b in dl['bi_danh_tam']:
                    raise loi_kho('MASK_XUNG_DOT')
                for bang in ('dinh_danh', 'cho_duyet', 'bi_danh_tam'):
                    if any(b in {chuan_bi_danh(m['bi_danh']), chuan_bi_danh(m.get('bi_danh_tam') or '')}
                           for m in dl[bang].values()):
                        raise loi_kho('MASK_XUNG_DOT')
                tam = dict(gia_tri=muc['gia_tri'], nhom=muc['nhom'], bi_danh=muc['bi_danh'], nguon='tam')
                anh.dat('bi_danh_tam', b, tam)
            if hien is None:
                hien = dict(gia_tri=muc['gia_tri'], nhom=muc['nhom'], bi_danh=muc['bi_danh'],
                            nguon='tam', so_lan_gap=0)
                anh.dat('cho_duyet', khoa, hien)
            if hien['nhom'] != muc['nhom'] or (hien['nguon'] == 'chinh_thuc' and hien['bi_danh'] != muc['bi_danh']):
                raise loi_kho('MASK_XUNG_DOT')
            dau = khoa_dau('gap', ma, khoa)
            if hien['nguon'] == 'tam' and dau not in dl['dau_gap']:
                hien = dict(hien, so_lan_gap=hien['so_lan_gap'] + 1)
                anh.dat('cho_duyet', khoa, hien)
                anh.dat('dau_gap', dau, {'ma_yeu_cau': ma, 'cum': khoa})
        for bi_danh in set(nk['bi_danh_da_dung'] + nk['bi_danh_da_tra']):
            b = chuan_bi_danh(bi_danh)
            muc = next((m for bang in ('bi_danh_tam', 'dinh_danh', 'cho_duyet') for m in dl[bang].values()
                        if b in {chuan_bi_danh(m['bi_danh']), chuan_bi_danh(m.get('bi_danh_tam') or '')}), None)
            if muc is None:
                continue  # Bí danh lạ được báo bởi lõi, không đoán/ghi tham chiếu.
            if b in dl['bi_danh_tam']:
                ref = khoa_dau('tham_chieu', ma, b)
                moi = any(chuan_bi_danh(m) == b for m in nk['bi_danh_tam_moi'])
                if ref not in dl['dau_gap'] and not (loai == 'che' and moi):
                    if bi_danh not in nk['bi_danh_da_dung']:
                        continue  # Tra hụt bí danh tạm khác yêu cầu: không nhận tham chiếu.
                    raise loi_kho('MASK_MA_YEU_CAU')
                anh.dat('dau_gap', khoa_dau('tham_chieu', ma, b),
                        {'loai_dau': 'tham_chieu', 'ma_yeu_cau': ma, 'bi_danh': b})
            chon = {k: deepcopy(muc[k]) for k in ('gia_tri', 'nhom', 'bi_danh', 'nguon')}
            if loai == 'mo_che':
                chon['bi_danh'] = bi_danh
            anh.dat('dau_gap', khoa_dau('lua_chon', luot, b),
                    {'loai_dau': 'lua_chon', 'ma_luot': luot, 'de_che': loai == 'che', 'dinh_danh': chon})
        yc = deepcopy(yc) if yc else {k: getattr(ctx, k) for k in ('module', 'nguoi_gui', 'tai_lieu')}
        yc['trang_thai'] = 'DA_DONG' if nk['dong_yeu_cau'] else 'DANG_XU_LY'
        anh.dat('ma_yeu_cau', ma, yc)
        anh.dat('dau_gap', khoa_dau('luot', luot),
                {'bam': self.bam, 'ma_yeu_cau': ma, 'loai': loai,
                 'bam_ket_qua': _bam_ket_qua(kq),
                 'so_moi': kq.get('cho_duyet', {}).get('so_cum_vua_them', 0)})
        self.viec.kiem_huy()
        self._kiem('chot')
        anh.chot()
        return kq
