"""Ghép port Kho hiện có với nguồn quyền; chưa nối vào handler MASK-5.

Không có kho nội dung mặc định. Các port chỉ được tiêm bởi bên tích hợp tin
cậy, không lấy callable/danh tính từ dữ liệu công việc. Không có vòng gửi lại
kết quả: phần đó thuộc SDK. KhoBoNho chỉ nằm ngoài gói, trong tests.
"""
from __future__ import annotations

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .che_van_ban import Kho
from .kho_qua_core import KhoQuaCore, bam_noi_dung


def _kiem_ket_qua(ket_qua, loai):
    if not isinstance(ket_qua, dict):
        raise LoiNghiepVu('MASK_DAU_VAO', 'Nội dung yêu cầu chưa hợp lệ.')
    if ket_qua.get('kiem_tien_ngay') is not True:
        raise LoiNghiepVu('MASK_TIEN_NGAY_THAY_DOI', 'Kiểm tra bảo toàn tiền và ngày chưa đạt.')
    if loai == 'che' and (ket_qua.get('gui_duoc') is not True or ket_qua.get('con_sot') != []):
        raise LoiNghiepVu('MASK_DINH_DANH_CHUA_DAT', 'Chưa kiểm tra hết định danh. Không thể trả kết quả che.')


class KhoDinhDanh:
    def __init__(self, *, goi_kho=None, quyen=None, kho_tam=None):
        self._goi_kho, self._quyen, self._kho_tam = goi_kho, quyen, kho_tam

    def mo_luot(self, viec, *, loai='che', ma_yeu_cau=None) -> KhoQuaCore:
        bam = bam_noi_dung({'loai': loai, 'dau_vao': viec.dau_vao, 'tham_so': viec.tham_so})
        return KhoQuaCore(goi_kho=self._goi_kho, quyen=self._quyen, viec=viec,
                          loai=loai, ma_yeu_cau=ma_yeu_cau, bam_dau_vao=bam,
                          kho_tam=self._kho_tam)

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
