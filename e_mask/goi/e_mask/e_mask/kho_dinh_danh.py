"""Ghép protocol Kho với Ngan và nguồn quyền tin cậy cho handler văn bản.

Các port quyền chỉ được tiêm bởi bên tích hợp tin
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
    def __init__(self, *, goi_kho=None, quyen=None, kho_tam=None, ngan=None):
        self._goi_kho, self._quyen, self._kho_tam = goi_kho, quyen, kho_tam
        self._ngan = ngan

    def mo_luot(self, viec, *, loai='che', ma_yeu_cau=None) -> KhoQuaCore:
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
        """Map chỉ ở RAM/snapshot Core; không chép vào kết quả chốt ngăn.

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
