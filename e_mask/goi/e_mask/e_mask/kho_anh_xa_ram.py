"""Kho một chuỗi trong RAM Mask; không có đường phục hồi hoặc xuất map.

R5/R6/B7 nối dữ liệu nghiệp vụ vào buoc(). Port Core còn thiếu phải được
bên tích hợp cấp riêng; adapter CoreGia chỉ nằm ngoài gói. Bỏ tham chiếu
không có nghĩa ghi đè vật lý mọi bản sao mà Python có thể đã tạo.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
from threading import Lock, RLock, Timer, get_ident
from time import monotonic
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo

from .khoi_tao_ngan import THOI_HAN_ANH_XA_TOI_DA, thoi_han_anh_xa_giay
from .quyen_yeu_cau import (
    GhimTienTrinh, SuKienRAM, kiem_ngu_canh_ram, loi_kho, loi_ram, xac_minh_ram,
)


def _hen_gio(giay, ham):
    hen = Timer(giay, ham)
    hen.daemon = True
    return hen


def _chu(ctx):
    q = ctx.quyen
    return (q.ma_yeu_cau, q.phien, q.module, q.nguoi_gui, q.tai_lieu,
            q.vung, ctx.phap_nhan_id, ctx.instance, ctx.phien_ram)


def _bam(viec, loai):
    try:
        return sha256(json.dumps(
            [loai, viec.dau_vao, viec.tham_so], ensure_ascii=False,
            sort_keys=True, separators=(',', ':'), allow_nan=False,
        ).encode('utf-8')).digest()
    except Exception:
        pass
    raise loi_ram('MASK_DAU_VAO_THAY_DOI') from None


def _bo_tham_chieu(du_lieu):
    cho, da_gap = [du_lieu], set()
    while cho:
        v = cho.pop()
        if id(v) in da_gap:
            continue
        da_gap.add(id(v))
        if type(v) is dict:
            cho.extend(v.values())
            v.clear()
        elif type(v) is list:
            cho.extend(v)
            v.clear()
        elif type(v) is tuple:
            cho.extend(v)
        elif type(v) is set:
            v.clear()
        # bytes/bytearray có thể còn memoryview của bước đang chạy. Chỉ bỏ
        # tham chiếu; không resize buffer đang xuất và làm timer lỗi.


class _BanGhi:
    def __init__(self, ctx, han):
        self.ctx, self.han = ctx, han
        self.trang_thai = 'DANG_CHE'
        self.du_lieu, self.bam_buoc = {}, {}
        self.so_huu = None
        self.hen = None


class _BuocRAM:
    """Handle nội bộ chỉ sống trong with; repr không có dữ liệu nghiệp vụ."""
    def __init__(self, kho, ban_ghi, viec, loai, thu_lai, ctx):
        self._kho, self._ban_ghi, self._viec = kho, ban_ghi, viec
        self._ctx = ctx
        self._loai, self._luong = loai, get_ident()
        self._cho_ai = False
        self.thu_lai = thu_lai

    def kiem(self):
        self._viec.kiem_huy()
        ctx = xac_minh_ram(self._kho._quyen, self._viec,
                           phien_ram=self._kho._phien_ram, loai=self._loai,
                           ma_yeu_cau=self._ctx.quyen.ma_yeu_cau)
        if ctx.instance != self._ctx.instance or ctx.phien_ram != self._ctx.phien_ram:
            raise loi_ram('MASK_ANH_XA_KHONG_CON')
        if (_chu(ctx) != _chu(self._ctx)
                or ctx.quyen.ma_luot != self._ctx.quyen.ma_luot):
            raise loi_kho('MASK_MA_YEU_CAU')
        with self._kho._khoa:
            self._kho._kiem_buoc(self)
            if ctx.han_monotonic is not None and ctx.han_monotonic < self._ban_ghi.han:
                self._ban_ghi.han = ctx.han_monotonic
                self._kho._dat_hen(self._ban_ghi)
                self._kho._kiem_buoc(self)

    @property
    def du_lieu(self):
        """Chỉ tham chiếu RAM nội bộ; không sao sang port/kết quả/chuyen_tiep.

        Mỗi vòng xử lý dài phải gọi kiem(). Timer có thể dọn dictionary này;
        kết thúc with còn kiểm lần cuối trước khi caller được trả kết quả.
        """
        self.kiem()
        return self._ban_ghi.du_lieu

    def cho_ai(self):
        self.kiem()
        if self._loai != 'che':
            raise loi_ram('MASK_VONG_DOI_KHONG_HOP_LE')
        self._cho_ai = True


class KhoAnhXaRAM:
    def __init__(self, *, quyen, dong_ho=monotonic, hen_gio=_hen_gio):
        self._quyen, self._dong_ho, self._hen_gio = quyen, dong_ho, hen_gio
        self._khoa = RLock()
        self._khoa_dang_ky = Lock()
        self._phien_ram = uuid4().hex
        self._ghim = None
        self._ban_ghi = None
        # Chỉ ID + hạn để chặn khởi tạo lại trong TTL; không cache bản rõ.
        # Sau hạn, Core vẫn phải từ chối duoc_tao cho mã đã dùng/restart.
        self._da_tao = {}
        self._da_ket_thuc = {}

    def kiem_san_sang(self):
        with self._khoa:
            if self._ghim is not None:
                return
        # Port có thể giao sự kiện từ luồng khác ngay khi đăng ký. Không
        # giữ khóa dữ liệu trong lúc chờ biên nhận của port.
        with self._khoa_dang_ky:
            with self._khoa:
                if self._ghim is not None:
                    return
            if self._quyen is None:
                raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
            try:
                ghim = self._quyen.dang_ky_vong_doi_ram(
                    self.nhan_su_kien, phien_ram=self._phien_ram)
                if (isinstance(ghim, GhimTienTrinh)
                        and isinstance(ghim.instance, str) and ghim.instance.strip()
                        and ghim.phien_ram == self._phien_ram
                        and ghim.ghim_cung_tien_trinh is True
                        and ghim.bao_vong_doi_khi_ranh is True
                        and callable(getattr(self._quyen, 'xac_minh_ram', None))):
                    with self._khoa:
                        self._ghim = ghim
                    return
            except Exception:
                pass
        raise loi_ram('MASK_CHUOI_CHUA_GHIM') from None

    def _don(self, bg):
        """Gọi dưới khóa; timer cũ không được dọn bản ghi chuỗi mới."""
        bg.trang_thai = 'KET_THUC'
        bg.so_huu = None
        if bg.hen is not None:
            bg.hen.cancel()
            bg.hen = None
        _bo_tham_chieu(bg.du_lieu)
        bg.bam_buoc.clear()
        if self._ban_ghi is bg:
            self._ban_ghi = None

    def _dat_hen(self, bg):
        if bg.hen is not None:
            bg.hen.cancel()
        bg.hen = self._hen_gio(max(0, bg.han - self._dong_ho()), lambda: self._het_han(bg))
        bg.hen.start()

    def _het_han(self, bg):
        with self._khoa:
            if self._ban_ghi is not bg:
                return
            if self._dong_ho() >= bg.han:
                self._don(bg)
            else:
                # Timer chạy sớm không được nới hạn tuyệt đối.
                try:
                    self._dat_hen(bg)
                except Exception:
                    # Không để ngoại lệ timer in traceback ra stderr.
                    self._don(bg)

    def nhan_su_kien(self, su_kien):
        """Chỉ port tin cậy gọi callback; sai chủ/phiên không dọn map khác."""
        if (not isinstance(su_kien, SuKienRAM) or not isinstance(su_kien.ket_thuc, str)
                or su_kien.ket_thuc not in {
            'HUY', 'LOI', 'KET_THUC', 'MAT_QUYEN', 'MAT_LEASE', 'HET_HAN',
        }):
            return
        try:
            ctx = kiem_ngu_canh_ram(su_kien.ngu_canh)
        except Exception:
            return
        with self._khoa:
            if (ctx.phien_ram != self._phien_ram
                    or (self._ghim is not None and ctx.instance != self._ghim.instance)):
                return
            luc = self._dong_ho()
            self._da_ket_thuc = {k: h for k, h in self._da_ket_thuc.items() if h > luc}
            self._da_ket_thuc[_chu(ctx)] = luc + THOI_HAN_ANH_XA_TOI_DA
            bg = self._ban_ghi
            if bg is not None and _chu(bg.ctx) == _chu(ctx):
                self._don(bg)

    def _kiem_buoc(self, buoc):
        bg = buoc._ban_ghi
        if (self._ban_ghi is not bg or bg.so_huu is not buoc
                or bg.trang_thai == 'KET_THUC' or buoc._luong != get_ident()):
            raise loi_ram('MASK_ANH_XA_KHONG_CON')
        if self._dong_ho() >= bg.han:
            self._don(bg)
            raise loi_ram('MASK_ANH_XA_KHONG_CON')

    def _nhan_buoc(self, viec, loai, ma):
        self.kiem_san_sang()
        # Đo trước xác minh: thời gian port xử lý không được cộng vào TTL.
        luc = self._dong_ho()
        ctx = xac_minh_ram(self._quyen, viec, phien_ram=self._phien_ram,
                           loai=loai, ma_yeu_cau=ma)
        if (ctx.instance != self._ghim.instance or ctx.phien_ram != self._phien_ram):
            raise loi_ram('MASK_ANH_XA_KHONG_CON')
        bam = _bam(viec, loai)
        with self._khoa:
            if _chu(ctx) in self._da_ket_thuc:
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            bg = self._ban_ghi
            if bg is not None and self._dong_ho() >= bg.han:
                self._don(bg)
                bg = None
            if bg is not None and bg.ctx.quyen.ma_yeu_cau == ctx.quyen.ma_yeu_cau:
                if _chu(bg.ctx) != _chu(ctx):
                    raise loi_kho('MASK_MA_YEU_CAU')
            elif bg is not None:
                raise loi_ram('MASK_CHUOI_DANG_XU_LY' if loai == 'che' else 'MASK_ANH_XA_KHONG_CON')
            if bg is None:
                if loai != 'che' or not ctx.duoc_tao or ctx.quyen.ma_yeu_cau in self._da_tao:
                    raise loi_ram('MASK_ANH_XA_KHONG_CON')
                han = luc + thoi_han_anh_xa_giay(viec)
                if ctx.han_monotonic is not None:
                    han = min(han, ctx.han_monotonic)
                if self._dong_ho() >= han:
                    raise loi_ram('MASK_ANH_XA_KHONG_CON')
                bg = _BanGhi(ctx, han)
                self._da_tao = {m: h for m, h in self._da_tao.items() if h > luc}
                self._da_tao[ctx.quyen.ma_yeu_cau] = han
                self._ban_ghi = bg
                try:
                    self._dat_hen(bg)
                except BaseException:
                    self._don(bg)
                    raise
            if self._ban_ghi is not bg:
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            if bg.so_huu is not None:
                raise loi_ram('MASK_BUOC_DANG_XU_LY')
            if ctx.han_monotonic is not None and ctx.han_monotonic < bg.han:
                bg.han = ctx.han_monotonic
                try:
                    self._dat_hen(bg)
                except BaseException:
                    self._don(bg)
                    raise
            if self._dong_ho() >= bg.han:
                self._don(bg)
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            khoa = (loai, ctx.quyen.ma_luot)
            thu_lai = khoa in bg.bam_buoc
            if thu_lai and bg.bam_buoc[khoa] != bam:
                self._don(bg)
                raise loi_ram('MASK_DAU_VAO_THAY_DOI')
            bg.bam_buoc[khoa] = bam
            bg.trang_thai = 'DANG_MO' if loai == 'mo_che' else 'DANG_CHE'
            buoc = _BuocRAM(self, bg, viec, loai, thu_lai, ctx)
            bg.so_huu = buoc
            return buoc

    @contextmanager
    def buoc(self, viec, *, loai='che', ma_yeu_cau=None):
        """Một bước sở hữu RAM, nhường handler bằng cho_ai() trước khi ra.

        Mở luôn tiêu thụ, kể cả lỗi/hủy/ChuaRo. ChuaRo chỉ giữ map nếu bước
        che đã báo chờ AI và chuỗi còn trong hạn. Không cache kết quả mở;
        Core xử lý ACK/kết quả cuối, không gọi mở lại để dựng lại bản rõ.
        """
        buoc = self._nhan_buoc(viec, loai, ma_yeu_cau)
        giu, chot = False, False
        try:
            buoc.kiem()
            yield buoc
            buoc.kiem()
            giu = buoc._cho_ai and loai == 'che'
            chot = True
        except ChuaRo:
            buoc.kiem()
            giu = buoc._cho_ai and loai == 'che'
            chot = True
            raise
        except BaseException:
            with self._khoa:
                bg = buoc._ban_ghi
                if self._ban_ghi is not bg or self._dong_ho() >= bg.han:
                    # Timer có thể vừa clear map giữa checkpoint và phép
                    # đọc của nghiệp vụ. Không lộ KeyError/đầu ra dở.
                    raise loi_ram('MASK_ANH_XA_KHONG_CON') from None
            raise
        finally:
            with self._khoa:
                bg = buoc._ban_ghi
                if chot:
                    # Điểm chốt nguyên tử với timer/hủy: mất map thì không
                    # cho caller rời with để phát hành kết quả đã tính.
                    self._kiem_buoc(buoc)
                if self._ban_ghi is bg and bg.so_huu is buoc:
                    if giu and self._dong_ho() < bg.han:
                        bg.trang_thai, bg.so_huu = 'CHO_AI', None
                    else:
                        self._don(bg)
