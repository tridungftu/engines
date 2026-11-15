"""Port danh tính tin cậy; chưa có transport tương ứng trong SDK 2.0.

Port do bên tích hợp tiêm, gắn với phiên Core và việc. Không dựng danh tính
từ payload, tham số, pháp nhân hoặc cấu hình máy. Mã yêu cầu/lượt là opaque,
do Core cấp ổn định theo việc/bước; không dùng số lần thử trong khóa.
"""
from __future__ import annotations

from dataclasses import dataclass
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


def xac_minh(quyen, viec, *, loai, ma_yeu_cau=None, thao_tac='snapshot'):
    if loai == 'mo_che' and (not isinstance(ma_yeu_cau, str) or not ma_yeu_cau):
        raise loi_kho('MASK_MA_YEU_CAU')
    if quyen is None:
        raise loi_kho('MASK_NGU_CANH_CHUA_XAC_MINH')
    try:
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
