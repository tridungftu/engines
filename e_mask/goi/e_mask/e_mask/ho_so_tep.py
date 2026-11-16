"""Adapter B7 của kho RAM R4; không có snapshot hoặc kho phục hồi.

Các port là đề nghị C-P4-04/05, chưa có binding trong SDK 2.2.0.
Chỉ adapter ngoài gói được dùng khi kiểm CoreGia. Không có I/O lưu hồ sơ.
"""
from contextlib import contextmanager
from functools import wraps

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import chuan_bi_ai as cb, hau_kiem_ai as hk, phong_bi
from .ho_so_ai import bam_bytes, json_chuan, kiem_kho_ram
from .mo_che_ram import _don_ngoai_le
from .quyen_yeu_cau import loi_kho, loi_ram, xac_minh
from . import tep_word as word, tep_excel as excel

CHUAN_BI = 'mask.chuan_bi_tep_ai_cuc_bo@1'
VAN_BAN = 'mask.hau_kiem_tep_van_ban@1'
GIU_DINH_DANG = 'mask.hau_kiem_tep_giu_dinh_dang@1'
MIME = {'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
TRAN_TEP = 1048576
_CAU = {
    'MASK_TEP_RAM': 'Không xác minh được dữ liệu tệp trong chuỗi này. Anh hãy chạy lại toàn bộ chuỗi.',
    'MASK_TEP_CHUA_HO_TRO': 'Tệp có nội dung chưa được hỗ trợ xử lý đầy đủ.',
    'MASK_DINH_DANH_CHUA_DAT': 'Chưa kiểm tra hết định danh. Không thể trả kết quả che.',
    'MASK_THIEU_TAI_NGUYEN': 'Chưa có đủ tài nguyên nhận diện được phê duyệt.',
}


def loi(ma='MASK_TEP_RAM'):
    return LoiNghiepVu(ma, _CAU[ma])


def bao_ve(ham):
    """Không để lỗi port/parser giữ traceback có gốc hoặc in ra stderr."""
    @wraps(ham)
    def goi(*a, **kw):
        try:
            return ham(*a, **kw)
        except BaseException as exc:
            ma = getattr(exc, 'ma', None)
            if isinstance(exc, ChuaRo):
                ket = ChuaRo('mask-tep-' + bam_bytes(str(exc.ma_tuong_quan).encode('utf-8'))[7:])
            elif isinstance(exc, ViecDaHuy):
                ket = ViecDaHuy()
            elif isinstance(exc, LoiNghiepVu):
                if ma in _CAU:
                    ket = loi(ma)
                elif ma in cb._CAU_LOI:
                    ket = cb.loi(ma)
                elif ma in hk._CAU:
                    ket = hk.loi(ma)
                elif ma in word._LOI_RAM:
                    ket = loi_ram(ma)
                elif ma in word._LOI_UNG_VIEN:
                    ket = word.loi_ung_vien(ma)
                elif ma in {'MASK_DAU_VAO', 'MASK_QUA_GIOI_HAN', 'MASK_MA_YEU_CAU'}:
                    ket = phong_bi.loi(ma)
                else:
                    ket = loi_kho(ma)
            elif isinstance(exc, Exception):
                ket = loi()
            else:
                ket = KeyboardInterrupt() if isinstance(exc, KeyboardInterrupt) else SystemExit(1)
            _don_ngoai_le(exc)
        a = kw = ma = None
        raise ket from None
    return goi


class HoSoTepRAM:
    def __init__(self, *, ram, quyen, cong, phien_ban_engine):
        self.ram, self.quyen, self.cong = ram, quyen, cong
        self.phien_ban_engine = phien_ban_engine
        self.buoc = self.viec = self.ctx = None

    @contextmanager
    def so_huu(self, viec):
        with kiem_kho_ram(self.ram).buoc(viec, loai='che') as buoc:
            self.buoc, self.viec = buoc, viec
            try:
                self.ctx = xac_minh(self.quyen, viec, loai='che', thao_tac='tep_ai')
                self.bam_vao = bam_bytes(json_chuan([viec.dau_vao, viec.tham_so]))
                self.kiem()
                yield buoc
            finally:
                self.buoc = self.viec = self.ctx = None

    def kiem(self):
        self.buoc.kiem()
        if self.cong is None:
            raise cb.loi('MASK_AI_CHUA_CO_CUA_CORE')
        ctx = xac_minh(self.quyen, self.viec, loai='che', ma_yeu_cau=self.ctx.ma_yeu_cau,
                       thao_tac='tep_ai')
        if (ctx != self.ctx or self.viec.ngu_canh.get('phap_nhan_id') != self.buoc._ctx.phap_nhan_id
                or bam_bytes(json_chuan([self.viec.dau_vao, self.viec.tham_so])) != self.bam_vao):
            raise hk.loi('MASK_AI_NGUON')

    def goi(self, ten, **kw):
        self.kiem()
        ham = getattr(self.cong, ten, None)
        if not callable(ham):
            raise cb.loi('MASK_AI_CHUA_CO_CUA_CORE')
        try:
            k = ham(self.viec, self.ctx, **kw)
        except LoiDuongTruyen as exc:
            if ten in {'ban_giao', 'chot_metadata'} and (
                    exc.thu_lai_duoc or exc.http_status is None or exc.http_status >= 500):
                raise ChuaRo('mask-tep-' + self.bam_vao[7:]) from None
            raise
        except (TimeoutError, ConnectionError):
            if ten in {'ban_giao', 'chot_metadata'}:
                raise ChuaRo('mask-tep-' + self.bam_vao[7:]) from None
            raise
        self.kiem()
        return k

    def dung(self, ten, **kw):
        if self.goi(ten, **kw) is not True:
            raise hk.loi('MASK_AI_NGUON')

    def doc(self):
        self.kiem()
        du = self.buoc.du_lieu
        h = du.get('ho_so_tep')
        if type(h) is not dict or h.get('giai_doan') != 'CHO_LOCAL':
            raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
        s = (word if h['loai'] == 'docx' else excel)._doc_ram(self.buoc)
        if (s['bam_goc'] != h['bam_tep'] or s['bam_da_che'] != h['bam_quy_tac']
                or bam_bytes(json_chuan(h['mo_ta'])) != h['dau'].bam_ho_so):
            raise loi()
        return h, s

    def ghi(self, du, **gia_tri):
        # Cùng khóa với timer/hủy R4: không dựng lại map sau clear.
        self.kiem()
        with self.ram._khoa:
            self.ram._kiem_buoc(self.buoc)
            if self.buoc._ban_ghi.du_lieu.get('ho_so_tep') is not du:
                raise loi()
            du.update(gia_tri)
