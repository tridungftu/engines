"""Adapter B7 của kho RAM R4; không có snapshot hoặc kho phục hồi.

Các port là đề nghị C-P4-04/05, chưa có binding trong SDK 2.2.0.
Chỉ adapter ngoài gói được dùng khi kiểm CoreGia. Không có I/O lưu hồ sơ.
"""
from contextlib import contextmanager
from contextlib import ExitStack
from dataclasses import dataclass, field
from functools import wraps

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import chuan_bi_ai as cb, hau_kiem_ai as hk, phong_bi
from .ho_so_ai import bam_bytes, json_chuan, kiem_kho_ram
from .mo_che_ram import _don_ngoai_le
from .quyen_yeu_cau import NguCanhTinCay, loi_kho, loi_ram, xac_minh
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
    'MASK_MO_CHE_KHONG_DAY_DU': 'Không thể mở che đầy đủ kết quả này. Anh hãy chạy lại toàn bộ chuỗi.',
    'MASK_MO_CHE_CHUA_CO_CUA_CORE': 'Chưa xác minh được quyền bàn giao kết quả mở che. Anh hãy thử lại sau.',
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


@dataclass(frozen=True, slots=True, repr=False)
class TepDaMoRAM:
    """Chỉ kết quả cuối nội bộ; không chứa map hoặc bản gốc dự phòng."""
    du_lieu: bytes = field(repr=False)
    bam_dau_vao: str
    bam_ket_qua: str
    so_cho_mo: int
    nguyen_bytes: bool


class MoTepRAM:
    """B8 nội bộ; B9 mới đọc mẫu 7 và đăng ký năng lực SDK.

    C-P4-05: cong.kiem_tep_mo(viec, ctx, loai, bam_tep, ngan_sach)
    xác minh quyền tệp thuộc đầu vào việc và budget toàn chuỗi; chỉ nhận
    băm/số đếm. ban_giao_cuoi theo R6 cách ly bytes kết quả tới khi R4
    tiêu thụ và quyền/hạn vẫn hợp lệ. Đây là protocol đề nghị, không phải
    binding SDK. Không upload, đọc gốc từ Core hoặc tự cấp quyền.
    """
    def __init__(self, *, ram, quyen, cong):
        self.ram, self.quyen, self.cong = ram, quyen, cong

    @bao_ve
    def mo(self, viec, du_lieu, *, loai, ma_yeu_cau=None, dong_viec=True):
        from .kho_anh_xa_ram import KhoAnhXaRAM, TRAN_ALIAS_MO, _bam
        from .mo_che_ram import CHUYEN_QUY_TRINH
        from .mo_tep_word import mo_word
        from .mo_tep_excel import mo_excel
        from .zip_an_toan import TONG_GIAI_NEN_TOI_DA, kiem_kich_thuoc_tep

        ket = buoc = nhan = ham = ctx = None
        da_gui = False
        try:
            if (type(self.ram) is not KhoAnhXaRAM or self.quyen is None
                    or self.ram._quyen is not self.quyen):
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            # Lấy mã từ nguồn tin cậy trước; mã caller chỉ để đối chiếu.
            ctx = self.quyen.xac_minh(viec, loai='mo_che', ma_yeu_cau=None, thao_tac='ram')
            if type(ctx) is not NguCanhTinCay:
                raise loi_kho('MASK_MA_YEU_CAU')
            ctx = xac_minh(self.quyen, viec, loai='mo_che',
                ma_yeu_cau=ctx.ma_yeu_cau, thao_tac='ram', kiem_huy=False)
            xong = False
            # Cửa bàn giao thoát SAU kho RAM, kể cả mất ACK không giữ bản rõ.
            with ExitStack() as giao:
                with self.ram.buoc(viec, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau) as buoc:
                    if ma_yeu_cau is not None and ma_yeu_cau != ctx.ma_yeu_cau:
                        raise loi_kho('MASK_MA_YEU_CAU')
                    if type(loai) is not str or loai not in MIME or type(dong_viec) is not bool:
                        raise loi('MASK_TEP_CHUA_HO_TRO')
                    kiem_kich_thuoc_tep(du_lieu)
                    dau = _bam(viec, 'mo_che')
                    bam_tep = bam_bytes(du_lieu)
                    bam_vao = bam_bytes(json_chuan([viec.dau_vao, viec.tham_so, loai, bam_tep]))
                    ham = getattr(self.cong, 'kiem_tep_mo', None)
                    if not callable(ham):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    with self.ram._khoa:
                        self.ram._kiem_buoc(buoc)
                        s = buoc._ban_ghi.du_lieu.get('tep_word' if loai == 'docx' else 'tep_excel')
                        if type(s) is not dict:
                            raise loi_ram('MASK_ANH_XA_KHONG_CON')
                        byte_goc = len(s['goc']) if type(s.get('goc')) is bytes else 0
                        byte_che = len(s['da_che']) if type(s.get('da_che')) is bytes else 0
                    ngan_sach = dict(giai_doan='truoc', byte_vao=len(du_lieu),
                        byte_goc_ram=byte_goc, byte_che_ram=byte_che,
                        tran_tep=TRAN_TEP, tran_giai_nen=TONG_GIAI_NEN_TOI_DA,
                        tran_alias=TRAN_ALIAS_MO, tran_nut_do=word.che.TRAN_NUT_DO_MANH)
                    if ham(viec, buoc._ctx, loai=loai, bam_tep=bam_tep, ngan_sach=ngan_sach) is not True:
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    buoc.kiem()
                    if _bam(viec, 'mo_che') != dau:
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                    if not dong_viec:
                        viec.tien_do(10, CHUYEN_QUY_TRINH)
                    ket = (mo_word if loai == 'docx' else mo_excel)(du_lieu, buoc=buoc)
                    ngan_sach.update(giai_doan='sau', byte_ra=len(ket.du_lieu),
                                     so_cho_mo=ket.so_cho_mo)
                    if ham(viec, buoc._ctx, loai=loai, bam_tep=bam_tep, ngan_sach=ngan_sach) is not True:
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    buoc.kiem()
                    ham = getattr(self.cong, 'ban_giao_cuoi', None)
                    if not callable(ham):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    nhan = giao.enter_context(ham(viec, buoc._ctx,
                        bam_dau_vao=bam_vao, han_monotonic=buoc._ban_ghi.han))
                    if not callable(nhan):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    buoc.kiem()
                    if _bam(viec, 'mo_che') != dau:
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                    try:
                        da_gui = True
                        if nhan(ket.du_lieu) is not True:
                            raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    except (LoiDuongTruyen, TimeoutError, ConnectionError):
                        raise ChuaRo('mask-mo-tep-' + bam_vao[7:]) from None
                    buoc.kiem()
                    if _bam(viec, 'mo_che') != dau:
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                xong = True
            if not xong:  # Không chấp nhận port nuốt lỗi/hủy của R4.
                raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
            return ket
        except (LoiDuongTruyen, TimeoutError, ConnectionError):
            if da_gui:
                raise ChuaRo('mask-mo-tep-' + bam_vao[7:]) from None
            raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE') from None
        except LoiNghiepVu as exc:
            if exc.ma == 'MASK_BUOC_DANG_XU_LY':
                raise loi_ram('MASK_ANH_XA_KHONG_CON') from None
            raise
        finally:
            ket = du_lieu = buoc = nhan = ham = ctx = ngan_sach = s = None
