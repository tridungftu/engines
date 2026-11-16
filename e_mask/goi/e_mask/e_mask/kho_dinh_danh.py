"""Ghép protocol Kho với Ngan và nguồn quyền tin cậy cho handler văn bản.

Các port quyền chỉ được tiêm bởi bên tích hợp tin
cậy, không lấy callable/danh tính từ dữ liệu công việc. Không có vòng gửi lại
kết quả: phần đó thuộc SDK. KhoBoNho chỉ nằm ngoài gói, trong tests.
"""
from __future__ import annotations

from contextlib import ExitStack

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, NganEngine

from .che_van_ban import Kho
from .kho_qua_core import KhoNhanDienQuaCore, KhoQuaCore, bam_noi_dung


def _kiem_ket_qua(ket_qua, loai):
    if not isinstance(ket_qua, dict):
        raise LoiNghiepVu('MASK_DAU_VAO', 'Nội dung yêu cầu chưa hợp lệ.')
    if ket_qua.get('kiem_tien_ngay') is not True:
        raise LoiNghiepVu('MASK_TIEN_NGAY_THAY_DOI', 'Kiểm tra bảo toàn tiền và ngày chưa đạt.')
    if loai == 'che' and (ket_qua.get('gui_duoc') is not True or ket_qua.get('con_sot') != []):
        raise LoiNghiepVu('MASK_DINH_DANH_CHUA_DAT', 'Chưa kiểm tra hết định danh. Không thể trả kết quả che.')


class KhoDinhDanh:
    def __init__(self, *, goi_kho=None, quyen=None, kho_tam=None, ngan=None):
        self._goi_kho, self._quyen, self._kho_tam = goi_kho, quyen, kho_tam
        self._ngan = ngan

    def mo_kho_nhan_dien(self, viec, *, loai='che', ma_yeu_cau=None):
        """R2/R3: viec.ngan thật, không dùng callback trả tên hay snapshot."""
        return KhoNhanDienQuaCore(viec=viec, quyen=self._quyen, loai=loai,
                                 ma_yeu_cau=ma_yeu_cau)

    def mo_luot(self, viec, *, loai='che', ma_yeu_cau=None) -> KhoQuaCore | KhoNhanDienQuaCore:
        if (isinstance(self._ngan, NganEngine)
                or (self._ngan is None and self._goi_kho is None
                    and isinstance(getattr(viec, 'ngan', None), NganEngine))):
            # Chọn đường SDK trước mọi băm/snapshot của protocol cũ.
            return self.mo_kho_nhan_dien(viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        bam = bam_noi_dung({'loai': loai, 'dau_vao': viec.dau_vao, 'tham_so': viec.tham_so})
        goi_kho, kho_tam = self._goi_kho, self._kho_tam
        if self._ngan is not None:
            from .kho_ngan import DauNgan, PortNgan
            goi_kho = PortNgan(self._ngan, self._quyen, viec, loai=loai,
                              ma_yeu_cau=ma_yeu_cau, bam_dau_vao=bam)
            kho_tam = DauNgan(self._ngan)
        return KhoQuaCore(goi_kho=goi_kho, quyen=self._quyen, viec=viec,
                          loai=loai, ma_yeu_cau=ma_yeu_cau, bam_dau_vao=bam,
                          kho_tam=kho_tam)

    def xu_ly(self, viec, ham, *, loai='che', ma_yeu_cau=None):
        """ham nhận protocol Kho và hoàn tất giao_dich trước chot.

        Giao lại luôn hỏi snapshot trước; lượt đã chốt chỉ đọc qua port kiểm
        quyền, không chạy ham/cấp bí danh/tăng đếm lần nữa.
        """
        kho: Kho = self.mo_luot(viec, loai=loai, ma_yeu_cau=ma_yeu_cau)
        if kho.da_chot:
            ket_qua = kho.chot()
            _kiem_ket_qua(ket_qua, loai)
            return ket_qua
        ket_qua = ham(kho)
        _kiem_ket_qua(ket_qua, loai)
        viec.kiem_huy()
        ket_qua = kho.chot(ket_qua)
        _kiem_ket_qua(ket_qua, loai)
        return ket_qua

    def xu_ly_co_anh_xa(self, viec, ham):
        """Đường RAM lịch sử cho tới R5; không dùng snapshot với ngăn SDK.

        PortNgan phục hồi cùng lựa chọn alias và tính lại map từ gốc bất
        biến; không cấp alias/đếm gặp lần nữa. Port cũ chỉ có kết quả đã
        chốt mà không map thì từ chối, không suy map từ chênh chiều dài.
        """
        kho = self.mo_luot(viec)
        if kho.da_chot:
            raise LoiNghiepVu('MASK_AI_HO_SO', 'Không xác minh được hồ sơ nội bộ. Cần thực hiện lại yêu cầu.')
        ket_qua, anh_xa = ham(kho)
        _kiem_ket_qua(ket_qua, 'che')
        viec.kiem_huy()
        ket_qua = kho.chot(ket_qua)
        _kiem_ket_qua(ket_qua, 'che')
        if ket_qua['van_ban_da_che'] != anh_xa.da_che:
            raise LoiNghiepVu('MASK_AI_HO_SO', 'Không xác minh được hồ sơ nội bộ. Cần thực hiện lại yêu cầu.')
        return ket_qua, anh_xa

    def xu_ly_hau_kiem_ai(self, viec, ham, *, ma_yeu_cau, kiem_chot):
        """Dùng nguyên kho/CAS/chống lặp; kiểm lại nguồn trước và sau chốt.

        PortNgan tái tạo cùng lựa chọn alias khi mất ACK, so băm kết quả và
        không tăng đếm gặp lại. Không chia lô khi vượt 100 lệnh.
        """
        kiem_chot()
        kho = self.mo_luot(viec, ma_yeu_cau=ma_yeu_cau)
        ket_qua = kho.chot() if kho.da_chot else ham(kho)
        _kiem_ket_qua(ket_qua, 'che')
        kiem_chot()
        viec.kiem_huy()
        if not kho.da_chot:
            ket_qua = kho.chot(ket_qua)
        _kiem_ket_qua(ket_qua, 'che')
        kiem_chot()
        return ket_qua



class MoTepSDK:
    """B9: mẫu 7 → bộ T, reader/writer mở B8 dưới cùng handle RAM R4.

    C-P4-05 chưa có binding SDK: kiem_tep_mo phải xác minh cả tham chiếu
    con thuộc JSON/băm/quyền và budget; ban_giao_cuoi cách ly upload từ
    trước tai_tep_ra tới sau tiêu thụ RAM, không nuốt lỗi, không mở lại.
    """
    def __init__(self, *, ram, quyen, cong):
        self.ram, self.quyen, self.cong = ram, quyen, cong

    def mo(self, viec):
        from .ho_so_tep import bao_ve
        return bao_ve(self._mo)(viec)

    def _mo(self, viec):
        from . import phong_bi
        from .ho_so_ai import bam_bytes, json_chuan
        from .ho_so_tep import MIME, loi
        from .kho_anh_xa_ram import KhoAnhXaRAM, TRAN_ALIAS_MO, _bam, _chu
        from .mo_che_ram import CHUYEN_QUY_TRINH
        from .mo_tep_word import mo_word
        from .mo_tep_excel import mo_excel
        from .quyen_yeu_cau import NguCanhTinCay, loi_kho, loi_ram, xac_minh, xac_minh_ram
        from .zip_an_toan import TONG_GIAI_NEN_TOI_DA, kiem_kich_thuoc_tep

        raw = ref = ket = ket_qua = buoc = nhan = ctx = bg = None
        da_gui, xong = False, False
        bam_vao = None
        try:
            if (type(self.ram) is not KhoAnhXaRAM or self.quyen is None
                    or self.ram._quyen is not self.quyen):
                raise loi_ram('MASK_ANH_XA_KHONG_CON')
            # Quyền Core đi trước mã caller và parse. Lỗi mẫu 7 dọn đúng
            # map chủ việc; yêu cầu sai scope không lấy được handle này.
            ctx = self.quyen.xac_minh(viec, loai='mo_che', ma_yeu_cau=None, thao_tac='ram')
            if type(ctx) is not NguCanhTinCay:
                raise loi_kho('MASK_MA_YEU_CAU')
            ctx = xac_minh(self.quyen, viec, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau,
                           thao_tac='ram', kiem_huy=False)
            with ExitStack() as giao:
                with self.ram.buoc(viec, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau) as buoc:
                    bg, dau = buoc._ban_ghi, _bam(viec, 'mo_che')
                    han = bg.han
                    raw, loai, dong, ref = phong_bi.doc_mo_tep(viec, ma_tin_cay=ctx.ma_yeu_cau)
                    bam_tep = bam_bytes(raw)
                    bam_vao = bam_bytes(json_chuan([viec.dau_vao, viec.tham_so, loai, bam_tep]))
                    kiem_tep = getattr(self.cong, 'kiem_tep_mo', None)
                    ban_giao = getattr(self.cong, 'ban_giao_cuoi', None)
                    if not callable(kiem_tep) or not callable(ban_giao):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')

                    def kiem():
                        buoc.kiem()
                        if _bam(viec, 'mo_che') != dau:
                            raise loi_ram('MASK_DAU_VAO_THAY_DOI')

                    with self.ram._khoa:
                        self.ram._kiem_buoc(buoc)
                        s = bg.du_lieu.get('tep_word' if loai == 'docx' else 'tep_excel')
                        if type(s) is not dict:
                            raise loi_ram('MASK_ANH_XA_KHONG_CON')
                        byte_goc, byte_che = len(s['goc']), len(s['da_che'])
                    ngan_sach = dict(giai_doan='truoc', byte_vao=len(raw), byte_goc_ram=byte_goc,
                        byte_che_ram=byte_che, tran_tep=phong_bi.TRAN_TEP_B,
                        tran_giai_nen=TONG_GIAI_NEN_TOI_DA, tran_alias=TRAN_ALIAS_MO)
                    if kiem_tep(viec, buoc._ctx, tham_chieu=ref.copy(), loai=loai,
                                bam_tep=bam_tep, ngan_sach=ngan_sach.copy()) is not True:
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    kiem()
                    if not dong:
                        viec.tien_do(10, CHUYEN_QUY_TRINH)
                    ket = (mo_word if loai == 'docx' else mo_excel)(raw, buoc=buoc)
                    kiem_kich_thuoc_tep(ket.du_lieu)
                    ngan_sach.update(giai_doan='sau', byte_ra=len(ket.du_lieu), so_cho_mo=ket.so_cho_mo)
                    if kiem_tep(viec, buoc._ctx, tham_chieu=ref.copy(), loai=loai,
                                bam_tep=bam_tep, ngan_sach=ngan_sach.copy()) is not True:
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    kiem()
                    # Context ở ngoài buoc(): phát hành sau điểm tiêu thụ,
                    # nhưng cách ly bắt đầu TRƯỚC upload bản rõ hoàn chỉnh.
                    nhan = giao.enter_context(ban_giao(viec, buoc._ctx,
                        bam_dau_vao=bam_vao, han_monotonic=han))
                    if not callable(nhan):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    kiem()
                    if phong_bi.doc_mo_tep(viec, ma_tin_cay=ctx.ma_yeu_cau) != (raw, loai, dong, ref):
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                    ten = 'mask-da-mo-che.' + loai
                    da_gui = True
                    tep_ra = viec.tai_tep_ra(ten, ket.du_lieu, MIME[loai])
                    kiem()
                    phong_bi.kiem_tham_chieu_tep(tep_ra)
                    if (tep_ra['ten'] != ten or tep_ra['mime'] != MIME[loai]
                            or tep_ra['kich_thuoc'] != len(ket.du_lieu)):
                        raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                    if phong_bi.doc_mo_tep(viec, ma_tin_cay=ctx.ma_yeu_cau) != (raw, loai, dong, ref):
                        raise loi_ram('MASK_DAU_VAO_THAY_DOI')
                    ket_qua = dict(loai='truong', truong=dict(tep_da_mo_che=tep_ra,
                        so_cho_mo=ket.so_cho_mo, bi_danh_khong_ro_json='[]', mo_day_du=True,
                        trang_thai_ma_yeu_cau='DA_DONG'))
                    if nhan(json_chuan(ket_qua)) is not True:
                        raise ChuaRo('mask-mo-tep-' + bam_vao[7:])
                    kiem()
                    viec.tien_do(100, 'Đã kiểm tra đầy đủ tệp mở che.')
                    kiem()
                # R4 đã tiêu thụ RAM nhưng Core còn cách ly. Mọi kiểm cuối
                # phải ném lỗi TRƯỚC __exit__ bàn giao để Core hủy kết quả.
                viec.kiem_huy()
                cuoi = xac_minh_ram(self.quyen, viec, phien_ram=self.ram._phien_ram,
                                    loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau)
                if (xac_minh(self.quyen, viec, loai='mo_che', ma_yeu_cau=ctx.ma_yeu_cau,
                             thao_tac='ram') != ctx or self.ram._dong_ho() >= han
                        or _chu(cuoi) != _chu(bg.ctx) or _chu(cuoi) in self.ram._da_ket_thuc
                        or (cuoi.han_monotonic is not None and self.ram._dong_ho() >= cuoi.han_monotonic)
                        or viec.ngu_canh.get('phap_nhan_id') != cuoi.phap_nhan_id
                        or bg.du_lieu or _bam(viec, 'mo_che') != dau):
                    raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
                xong = True
            if not xong:  # Context Core không được nuốt lỗi kiểm cuối/R4.
                raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE')
            return ket_qua
        except (LoiDuongTruyen, TimeoutError, ConnectionError):
            if da_gui:
                raise ChuaRo('mask-mo-tep-' + bam_vao[7:]) from None
            raise loi('MASK_MO_CHE_CHUA_CO_CUA_CORE') from None
        finally:
            # Không để frame lỗi/callback giữ bản rõ hoặc handle sau mở.
            raw = ref = ket = ket_qua = buoc = nhan = ctx = bg = s = None
            kiem = kiem_tep = ban_giao = ngan_sach = None
