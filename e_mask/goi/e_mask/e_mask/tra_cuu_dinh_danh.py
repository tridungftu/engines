"""MASK-R3: dò chính xác ứng viên từ đầu vào hiện tại, chỉ khảo sát RAM.

Không liệt kê kho, không khôi phục tên từ metadata, không cấp alias tạm.
Đối tượng này thuộc một chuỗi, phải dùng chung cho quy tắc và Local; R4/R5
chịu vòng đời và nguồn Local. Không tự cấp chứng cứ phát hành hoặc quyền.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from time import monotonic

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from .nguon.privacy.types import la_bien_to_hop


TRAN_UNG_VIEN = 2_000
TRAN_VI_TRI = 20_000
# Budget khảo sát cho các lượt định vị giá trị detector trên bản dò; không
# biến thành O(n²) bằng cách thử mọi chuỗi con. Chưa là SLA máy đích.
TRAN_KY_TU_DO = 8_000_000
_CAU = {
    'MASK_R3_CHUA_CHUNG_MINH': 'Chưa chứng minh đủ độ phủ và chi phí nhận diện. Không thể phát hành văn bản.',
    'MASK_UNG_VIEN_QUA_TRAN': 'Số ứng viên hoặc chi phí dò vượt giới hạn. Anh hãy chia nhỏ tài liệu.',
    'MASK_UNG_VIEN_QUA_HAN': 'Đã hết thời gian kiểm tra định danh. Anh hãy chạy lại toàn bộ chuỗi.',
    'MASK_UNG_VIEN_CHUA_DAT': 'Không xác minh được ứng viên định danh. Không thể phát hành văn bản.',
    'MASK_MO_CHE_KHONG_DAY_DU': 'Không thể mở che đầy đủ kết quả này. Anh hãy chạy lại toàn bộ chuỗi.',
}


def loi(ma='MASK_UNG_VIEN_CHUA_DAT'):
    return LoiNghiepVu(ma, _CAU[ma])


def chan_phat_hanh():
    """Cửa đóng cố định; không có cờ caller/cấu hình để bật khảo sát."""
    raise loi('MASK_R3_CHUA_CHUNG_MINH') from None


@dataclass(frozen=True, repr=False)
class UngVien:
    bat_dau: int
    ket_thuc: int
    nhom: str
    nguon: str


@dataclass(frozen=True, repr=False)
class KetQuaDo:
    """Chỉ RAM nội bộ; tuyệt đối không serialize vào kết quả/chuyen_tiep."""
    phep_thay: tuple
    alias_nguyen_van: dict = field(repr=False)
    so_ung_vien: int
    so_chua_co: int


class TraCuuDinhDanh:
    def __init__(self, goc, kho, *, han_monotonic, kiem_huy):
        from .che_van_ban import _kiem_van_ban
        _kiem_van_ban(goc)
        if (type(han_monotonic) not in (int, float) or not math.isfinite(han_monotonic)
                or not callable(kiem_huy) or not callable(getattr(kho, 'tim_ung_vien', None))):
            raise loi()
        self._goc, self._kho = goc, kho
        self._han, self._kiem_huy = han_monotonic, kiem_huy
        self._da_tim, self._alias, self._phep = {}, {}, {}
        self._vi_tri = set()
        self._ky_tu_do, self._hong = 0, False
        self.kiem_han()

    def __repr__(self):
        return 'TraCuuDinhDanh(<ẩn>)'

    def dong(self):
        """Bỏ tham chiếu; Python không bảo đảm ghi đè mọi bản sao RAM."""
        self._hong = True
        self._goc, self._kho = '', None
        self._kiem_huy = None
        self._da_tim.clear()
        self._alias.clear()
        self._phep.clear()
        self._vi_tri.clear()

    def kiem_han(self):
        if self._hong:
            raise loi()
        try:
            self._kiem_huy()
            if monotonic() >= self._han:
                raise loi('MASK_UNG_VIEN_QUA_HAN')
        except BaseException:
            self.dong()
            raise

    def tinh_chi_phi(self, so_ky_tu):
        self.kiem_han()
        if type(so_ky_tu) is not int or so_ky_tu < 0:
            self.dong()
            raise loi()
        self._ky_tu_do += so_ky_tu
        if self._ky_tu_do > TRAN_KY_TU_DO:
            self.dong()
            raise loi('MASK_UNG_VIEN_QUA_TRAN')

    def _metadata(self, muc, nhom):
        if muc is None:
            return None
        # Chỉ chiếu nhãn/alias; tên chỉ được lấy từ self._goc[a:b].
        if (type(muc) is not dict or muc.get('nhom') != nhom
                or muc.get('trang_thai') not in {'CHO_DUYET', 'CHINH_THUC', 'TU_CHOI'}
                or any(muc.get(k) is not None or muc.get(k + '_da_ma_hoa') is not True
                       for k in ('gia_tri_goc', 'gia_tri_chuan'))):
            raise loi()
        if muc['trang_thai'] != 'CHINH_THUC':
            return None
        alias = muc.get('bi_danh')
        if (muc.get('nguon') != 'chinh_thuc' or type(alias) is not str
                or re.fullmatch(r'\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]', alias) is None
                or alias[2:-2].upper().startswith('MASKTAM')):
            raise loi()
        return alias

    def them(self, ung_vien):
        """Một giá trị chuẩn hóa = một lần tìm chính xác, kể cả không thấy.

        Hai nhóm khác nhau cho cùng giá trị là xung đột; không dò lại theo
        nhiều nhóm để tìm một kết quả thuận lợi. Quá trần dừng trước RPC.
        """
        from .che_van_ban import _kiem_dinh_danh, chuan_hoa, chuan_bi_danh
        self.kiem_han()
        try:
            if not isinstance(ung_vien, UngVien):
                raise loi()
            a, b, nhom = ung_vien.bat_dau, ung_vien.ket_thuc, ung_vien.nhom
            if (type(a) is not int or type(b) is not int or not 0 <= a < b <= len(self._goc)
                    or ung_vien.nguon not in {'quy_tac', 'dau_vao', 'local', 'truong'}
                    or not la_bien_to_hop(self._goc, a) or not la_bien_to_hop(self._goc, b)):
                raise loi()
            nguyen_van = self._goc[a:b]
            _kiem_dinh_danh([dict(gia_tri=nguyen_van, nhom=nhom)])
            self._vi_tri.add((a, b))
            if len(self._vi_tri) > TRAN_VI_TRI:
                raise loi('MASK_UNG_VIEN_QUA_TRAN')
            khoa = chuan_hoa(nguyen_van)
            if khoa in self._da_tim:
                nhom_cu, alias = self._da_tim[khoa]
                if nhom_cu != nhom:
                    raise loi()
            else:
                if len(self._da_tim) >= TRAN_UNG_VIEN:
                    raise loi('MASK_UNG_VIEN_QUA_TRAN')
                alias = self._metadata(self._kho.tim_ung_vien(nguyen_van, nhom), nhom)
                self.kiem_han()  # Không nhận kết quả RPC trả về sau deadline/hủy.
                self._da_tim[khoa] = (nhom, alias)
            if alias is not None:
                chuan = chuan_bi_danh(alias)
                cu = self._alias.get(chuan)
                if cu is not None and cu != (alias, nguyen_van, nhom):
                    # Cùng giá trị chuẩn hóa nhưng NFD/Cf/hoa-thường khác nhau
                    # vẫn mơ hồ khi AI chỉ trả lại alias, không có vị trí nguồn.
                    raise loi('MASK_MO_CHE_KHONG_DAY_DU')
                if (a, b) in self._phep and self._phep[a, b] != alias:
                    raise loi('MASK_MO_CHE_KHONG_DAY_DU')
                self._alias[chuan] = (alias, nguyen_van, nhom)
                self._phep[a, b] = alias
        except (ChuaRo, ViecDaHuy, LoiNghiepVu):
            self.dong()
            raise
        except Exception:
            self.dong()
            raise loi() from None

    def ket_qua(self):
        from .nguon.privacy.core import Occupied
        self.kiem_han()
        # Các ứng viên lồng nhau chỉ là đề xuất detector. Chọn vùng dài
        # nhất đã tìm trúng; gold phải kiểm che đủ, kể cả che prefix.
        chon, chiem = [], Occupied()
        for (a, b), alias in sorted(self._phep.items(), key=lambda p: (-(p[0][1] - p[0][0]), p[0])):
            self.kiem_han()
            if not chiem.touches(a, b):
                chon.append((a, b, alias))
                chiem.update([(a, b)])
        da_dung = {alias for _, _, alias in chon}
        return KetQuaDo(tuple(sorted(chon)),
                        {alias: goc for alias, goc, _ in self._alias.values() if alias in da_dung},
                        len(self._da_tim), sum(alias is None for _, alias in self._da_tim.values()))
