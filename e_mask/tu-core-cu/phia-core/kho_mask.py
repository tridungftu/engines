"""Kho Mask nội bộ Core, dùng kết nối được tiêm và các cửa DEFINER 118/119.

MASK-3B chưa có snapshot/chốt lượt của lát D: mỗi gọi là một transaction
(hoặc savepoint nếu caller đã mở transaction). giao_dich chỉ giữ mã yêu cầu
trong một lượt xử lý; KHÔNG bảo đảm rollback toàn lượt che/mở che.
Không mở kết nối, không SQL trực tiếp tới bảng, không ghi log định danh.
"""
from __future__ import annotations

from contextlib import contextmanager
from uuid import UUID, uuid4

from .phien import MaBiMat


class LoiKhoMask(RuntimeError):
    """Lỗi cố định, không giữ lỗi driver chứa tham số hoặc định danh."""


class KhoMask:
    def __init__(self, ket_noi, *, ma: MaBiMat, module: str,
                 phap_nhan_id: UUID, hanh_dong: str, tai_lieu_id: UUID,
                 viec_id: UUID | None = None, the_he: int | None = None):
        if not isinstance(ma, MaBiMat):
            raise ValueError('Cần mã phiên được Core cấp.')
        self._ket_noi = ket_noi
        self._ma = ma
        self._module = module
        self._pn = UUID(str(phap_nhan_id))
        self._hd = hanh_dong
        self._tai_lieu = UUID(str(tai_lieu_id))
        self._viec = None if viec_id is None else UUID(str(viec_id))
        self._the_he = the_he
        self._yeu_cau = None
        self._dang_goi = False
        self._mo_che = False

    @contextmanager
    def giao_dich(self):
        """Phạm vi mã yêu cầu, chưa phải giao dịch trọn lượt (lát D)."""
        if self._dang_goi:
            raise LoiKhoMask('Lượt xử lý đang được sử dụng.')
        self._dang_goi = True
        self._yeu_cau = None
        self._mo_che = False
        try:
            yield self
        finally:
            self._yeu_cau = None
            self._dang_goi = False
            self._mo_che = False

    def _goi(self, ten, *du_lieu, cap_ma=False):
        # ten chỉ do các phương thức bên dưới cung cấp, không lấy từ đầu vào.
        tham_so = (self._ma.lay_de_truyen(), self._module, self._pn, self._hd)
        if cap_ma:
            tham_so += (self._tai_lieu, self._viec, self._the_he)
        else:
            if not self._dang_goi or self._yeu_cau is None:
                raise LoiKhoMask('Cần yêu cầu đã được xác minh trong lượt xử lý.')
            tham_so += (self._viec, self._the_he, self._yeu_cau, *du_lieu)
        try:
            with self._ket_noi.transaction():
                dong = self._ket_noi.execute(
                    'SELECT mask.' + ten + '(' + ','.join(['%s'] * len(tham_so)) + ')',
                    tham_so).fetchone()
                return dong[0]
        except Exception:
            pass
        # Raise ngoài except để không giữ driver trong context/cause.
        tham_so = du_lieu = dong = None
        raise LoiKhoMask('Không thể thực hiện thao tác kho định danh.')

    def tao_yeu_cau(self):
        if not self._dang_goi or self._yeu_cau is not None:
            raise LoiKhoMask('Lượt xử lý chưa hợp lệ.')
        ma = self._goi('cap_ma_yeu_cau', cap_ma=True)
        self._yeu_cau = UUID(str(ma))
        return str(self._yeu_cau)

    def doc_yeu_cau(self, ma_yeu_cau):
        if not self._dang_goi:
            raise LoiKhoMask('Cần mở lượt xử lý.')
        ma = UUID(str(ma_yeu_cau))
        if self._yeu_cau is not None and self._yeu_cau != ma:
            raise LoiKhoMask('Yêu cầu khác đang được xử lý.')
        self._yeu_cau = ma
        self._mo_che = True
        try:
            return self._goi('doc_yeu_cau')
        except Exception:
            self._yeu_cau = None
            self._mo_che = False
            raise

    def _dung_yeu_cau(self, ma):
        if self._yeu_cau is None or self._yeu_cau != UUID(str(ma)):
            raise LoiKhoMask('Yêu cầu không thuộc lượt xử lý.')

    def liet_ke_dinh_danh(self):
        # Port Kho dùng cùng phương thức cho hai luồng. tao_yeu_cau mở bước
        # che; doc_yeu_cau mở bước mở che, chỉ cần danh sách mã để dò mã hỏng.
        return self._goi('liet_ke_bi_danh' if self._mo_che else 'liet_ke_dinh_danh')

    def tra_bi_danh(self, gia_tri_chuan):
        return self._goi('tra_bi_danh', gia_tri_chuan)

    def cap_bi_danh_tam(self):
        return '[[MASKTAM-' + uuid4().hex + ']]'

    def ghi_cho_duyet(self, gia_tri, nhom, bi_danh, ma_yeu_cau):
        self._dung_yeu_cau(ma_yeu_cau)
        muc = self._goi('ghi_cho_duyet', gia_tri, nhom, bi_danh, False)
        moi = muc.pop('vua_them')
        return muc, moi

    def ghi_nhan_gap_lai(self, ma_yeu_cau, cum_chuan, nhom):
        self._dung_yeu_cau(ma_yeu_cau)
        # Cùng cửa đếm nguyên tử; cờ True chỉ nhận cụm đã có, không tạo cụm.
        self._goi('ghi_cho_duyet', cum_chuan, nhom, None, True)

    def ghi_bi_danh_da_dung(self, ma_yeu_cau, bi_danh):
        self._dung_yeu_cau(ma_yeu_cau)
        self._goi('ghi_bi_danh_da_dung', list(bi_danh))

    def tra_dinh_danh(self, bi_danh_chuan):
        return self._goi('tra_dinh_danh', bi_danh_chuan)

    def dong_yeu_cau(self, ma_yeu_cau):
        self._dung_yeu_cau(ma_yeu_cau)
        self._goi('dong_yeu_cau')
