"""Port danh tính tin cậy; chưa có transport tương ứng trong SDK 2.0.

Port do bên tích hợp tiêm, gắn với phiên Core và việc. Không dựng danh tính
từ payload, tham số, pháp nhân hoặc cấu hình máy. Mã yêu cầu/lượt là opaque,
do Core cấp ổn định theo việc/bước; không dùng số lần thử trong khóa.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Protocol

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy


@dataclass(frozen=True, repr=False)
class NguCanhTinCay:
    ma_yeu_cau: str
    ma_luot: str
    phien: str
    module: str
    nguoi_gui: str
    tai_lieu: str
    vung: str


class QuyenYeuCau(Protocol):
    def xac_minh(self, viec, *, loai: str, ma_yeu_cau: str | None,
                 thao_tac: str) -> NguCanhTinCay:
        """Kiểm phiên/lease/module/người/tài liệu/vùng và trạng thái yêu cầu.

        snapshot, chot, doc_lai đều phải kiểm. Chỉ cho đọc lại yêu cầu đã
        đóng nếu đúng lượt đã chốt; không cho mở một lượt mới trên mã đã đóng.
        """
        ...


_CAU_LOI = {
    'MASK_KHO_CHUA_NOI': 'Chưa kết nối kho định danh. Hãy nhờ quản trị viên thiết lập.',
    'MASK_NGU_CANH_CHUA_XAC_MINH': 'Chưa xác minh được phiên và quyền xử lý yêu cầu.',
    'MASK_MA_YEU_CAU': 'Không xác minh được quyền mở che cho yêu cầu này.',
    'MASK_XUNG_DOT': 'Dữ liệu định danh vừa thay đổi. Hãy thử lại yêu cầu.',
    'MASK_KHO_LOI': 'Không thể hoàn tất xử lý kho định danh.',
}


def loi_kho(ma='MASK_KHO_LOI'):
    """Chỉ phát thông điệp cố định, không chuyển tiếp lỗi của port."""
    ma = ma if isinstance(ma, str) and ma in _CAU_LOI else 'MASK_KHO_LOI'
    return LoiNghiepVu(ma, _CAU_LOI[ma], thu_lai_duoc=ma == 'MASK_XUNG_DOT')


def xac_minh(quyen, viec, *, loai, ma_yeu_cau=None, thao_tac='snapshot', kiem_huy=True):
    if loai == 'mo_che' and (not isinstance(ma_yeu_cau, str) or not ma_yeu_cau):
        raise loi_kho('MASK_MA_YEU_CAU')
    if quyen is None:
        raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
    try:
        if kiem_huy:
            viec.kiem_huy()
        ngu_canh = quyen.xac_minh(viec, loai=loai, ma_yeu_cau=ma_yeu_cau,
                                  thao_tac=thao_tac)
        if (not isinstance(ngu_canh, NguCanhTinCay)
                or any(not isinstance(v, str) or not v.strip()
                       for v in vars(ngu_canh).values())
                or ngu_canh.vung not in {'DEMO', 'THAT'}
                or loai not in {'che', 'mo_che'}
                or (ma_yeu_cau is not None and ngu_canh.ma_yeu_cau != ma_yeu_cau)
                or (loai == 'mo_che' and not ma_yeu_cau)):
            raise ValueError
        return ngu_canh
    except ViecDaHuy:
        raise
    except Exception as exc:
        ma = getattr(exc, 'ma', None)
    raise loi_kho(ma if isinstance(ma, str) and ma in {'MASK_MA_YEU_CAU', 'MASK_XUNG_DOT'}
                  else 'MASK_NGU_CANH_CHUA_XAC_MINH') from None


@dataclass(frozen=True, repr=False)
class GhimTienTrinh:
    """Biên nhận từ port Core đã xác thực, không nhận từ phong bì/cấu hình."""
    instance: str
    phien_ram: str
    ghim_cung_tien_trinh: bool
    bao_vong_doi_khi_ranh: bool


@dataclass(frozen=True, repr=False)
class NguCanhRAM:
    quyen: NguCanhTinCay
    phap_nhan_id: str
    instance: str
    phien_ram: str
    # Port chiếu deadline Core sang đồng hồ monotonic của tiến trình Mask.
    # None chỉ khi Core xác nhận chuỗi không có deadline ngắn hơn TTL.
    han_monotonic: float | None
    # Quyền khởi tạo chỉ cấp một lần; retry/restart không cấp lại quyền này.
    duoc_tao: bool = False


@dataclass(frozen=True, repr=False)
class SuKienRAM:
    ngu_canh: NguCanhRAM
    ket_thuc: str


class QuyenVongDoiRAM(Protocol):
    """Cửa chung còn thiếu ở SDK 2.2.0 (C-P4-01/02).

    Core giữ ghim instance + phien_ram qua mọi bước và lần giao lại. Không
    gắn lại chuỗi cũ vào phiên RAM mới. Đăng ký và xác minh không mang map,
    gốc hoặc kết quả mở. Callback nhận sự kiện đã xác thực cả khi Mask rảnh.
    duoc_tao phải được cấp nguyên tử một lần, chỉ cho bước đầu chuỗi mới.
    """
    def dang_ky_vong_doi_ram(self, ham, *, phien_ram: str) -> GhimTienTrinh: ...

    def xac_minh_ram(self, viec, *, ngu_canh: NguCanhTinCay,
                    phien_ram: str, thao_tac: str) -> NguCanhRAM: ...


def loi_ram(ma):
    cau = {
        'MASK_ANH_XA_KHONG_CON': 'Không còn dữ liệu mở che của chuỗi này. Anh hãy chạy lại toàn bộ chuỗi che và hỏi AI.',
        'MASK_CHUOI_CHUA_GHIM': 'Chưa xác minh được việc ghim tiến trình và thông báo vòng đời của Core. Anh hãy thử lại sau.',
        'MASK_CHUOI_DANG_XU_LY': 'Mask đang giữ dữ liệu của một chuỗi khác. Anh hãy chờ chuỗi đó kết thúc.',
        'MASK_BUOC_DANG_XU_LY': 'Một bước khác đang xử lý chuỗi này. Anh hãy chờ bước đó kết thúc.',
        'MASK_DAU_VAO_THAY_DOI': 'Đầu vào của lần thử lại đã thay đổi. Anh hãy chạy lại toàn bộ chuỗi.',
        'MASK_VONG_DOI_KHONG_HOP_LE': 'Không thể tiếp tục chuỗi xử lý này. Anh hãy chạy lại toàn bộ chuỗi.',
    }
    if ma not in cau:
        return loi_kho()
    return LoiNghiepVu(ma, cau[ma])


def _chuoi_ro(v):
    return isinstance(v, str) and bool(v.strip())


def kiem_ngu_canh_ram(ctx):
    if (not isinstance(ctx, NguCanhRAM)
            or not isinstance(ctx.quyen, NguCanhTinCay)
            or any(not _chuoi_ro(v) for v in vars(ctx.quyen).values())
            or ctx.quyen.vung not in {'DEMO', 'THAT'}
            or not all(_chuoi_ro(v) for v in (ctx.phap_nhan_id, ctx.instance, ctx.phien_ram))
            or type(ctx.duoc_tao) is not bool
            or (ctx.han_monotonic is not None and
                (type(ctx.han_monotonic) not in (int, float) or not isfinite(ctx.han_monotonic)))):
        raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
    return ctx


def xac_minh_ram(quyen, viec, *, phien_ram, loai, ma_yeu_cau=None):
    """Đối chiếu quyền xuyên bước; dữ liệu việc không tự cấp quyền RAM."""
    # Kiểm quyền trước để một việc đã hủy vẫn dọn được đúng map của nó.
    # Kho kiểm huy ngay trong try/finally sau khi nhận quyền sở hữu bản ghi.
    ctx = xac_minh(quyen, viec, loai=loai, ma_yeu_cau=ma_yeu_cau,
                   thao_tac='ram', kiem_huy=False)
    try:
        ram = kiem_ngu_canh_ram(quyen.xac_minh_ram(
            viec, ngu_canh=ctx, phien_ram=phien_ram, thao_tac='ram'))
        if ram.quyen != ctx:
            raise ValueError
        return ram
    except ViecDaHuy:
        raise
    except Exception:
        pass
    raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH') from None
