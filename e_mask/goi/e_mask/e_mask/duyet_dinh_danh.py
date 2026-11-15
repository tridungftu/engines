"""MASK-R7: Admin chỉ metadata, bí mật không rời cửa Xem dữ liệu Core.

C-P4-06 chưa có trong SDK. Port quyền phải được host tin cậy cấp riêng,
không lấy từ payload/cấu hình. bien_nhan_duyet(...) là giao thức nội bộ
chờ Core nối: context manager kiểm quyền xem VÀ duyệt của phiên/vùng/ID,
biên nhận một lần đúng phiên bản và quyết định/alias; giữ quyền tới hết lô
CAS, không nuốt ngoại lệ. Chỉ yield {id_dinh_danh, row_version}, không tên.
Không có port này thì giữ chờ, không suy quyền từ cờ caller hoặc null+cờ.
"""
from functools import wraps
import re
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from .kho_ngan import CAC_TIEN_TO, KhoNganBiMat, bi_danh_moi, _kiem_id, _kiem_phien


_LOI = {
    'MASK_KHONG_CO_QUYEN': 'Không xác minh được quyền quản trị cho thao tác này.',
    'MASK_ADMIN_CAN_CORE': 'Chưa có cửa xem và xác minh biên nhận của Core. Mục này vẫn chờ duyệt.',
    'MASK_BIEN_NHAN_KHONG_HOP_LE': 'Biên nhận xem không còn hợp lệ. Anh hãy xem lại tại Core.',
    'MASK_XUNG_DOT': 'Danh sách vừa thay đổi. Anh hãy tải lại và xem lại tại Core.',
    'MASK_DAU_VAO': 'Thông tin duyệt chưa hợp lệ.',
    'MASK_KHO_LOI': 'Không thể hoàn tất xử lý kho định danh.',
    'MASK_NGAN_CHUA_CO': 'Chưa kết nối được ngăn dữ liệu của Core.',
}


def _loi(ma):
    ma = ma if isinstance(ma, str) and ma in _LOI else 'MASK_KHO_LOI'
    return LoiNghiepVu(ma, _LOI[ma], thu_lai_duoc=ma == 'MASK_XUNG_DOT')


def _an_loi(ham):
    @wraps(ham)
    def goi(self, *args, **kwargs):
        try:
            return ham(self, *args, **kwargs)
        except ViecDaHuy:
            raise
        except ChuaRo:
            self._chua_ro = True
            raise ChuaRo(self._tuong_quan) from None
        except LoiNghiepVu as exc:
            raise _loi(exc.ma) from None
        except Exception:
            raise _loi('MASK_KHO_LOI') from None
    return goi


def kiem_ma_junsky(ma):
    if (not isinstance(ma, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', ma)
            or any(ma.upper().startswith(t) for t in CAC_TIEN_TO)):
        raise _loi('MASK_DAU_VAO')
    return '[[' + ma + ']]'


class DuyetDinhDanh:
    def __init__(self, viec, quyen):
        self.viec, self.quyen = viec, quyen
        self._tuong_quan, self._chua_ro = 'mask-admin-' + uuid4().hex, False

    def __repr__(self):
        return 'DuyetDinhDanh(<ẩn>)'

    def _kiem(self):
        self.viec.kiem_huy()
        try:
            vung = self.quyen.xac_minh_admin()
            if vung not in ('DEMO', 'THAT'):
                raise ValueError
        except Exception:
            raise _loi('MASK_KHONG_CO_QUYEN') from None
        return vung

    @_an_loi
    def danh_sach(self, *, tiep=None):
        """Một trang metadata; không lọc hoặc nhận tên, không tải kho bản rõ."""
        vung = self._kiem()
        kho = KhoNganBiMat(self.viec, vung=vung)
        trang = self.viec.ngan.tim('dinh_danh', loc={
            'vung_du_lieu': vung, 'trang_thai': 'CHO_DUYET'}, gioi_han=100, tiep=tiep)
        ds = []
        for dong in trang.danh_sach:
            muc = kho._ket_qua(dong)
            ds.append({k: muc[k] for k in ('id_dinh_danh', 'row_version', 'bi_danh',
                                          'nhom', 'trang_thai', 'so_gap')})
        if self._kiem() != vung:
            raise _loi('MASK_KHONG_CO_QUYEN')
        return {'danh_sach': ds, 'tiep': trang.tiep}

    def _quyet_dinh(self, ma, phien, bien_nhan, *, ma_junsky, duyet):
        if self._chua_ro:
            raise ChuaRo(self._tuong_quan)
        vung = self._kiem()
        _kiem_id(ma)
        _kiem_phien(phien)
        # Chỉ tham chiếu opaque. da_xem=true hay object tự khai không là vé.
        if not isinstance(bien_nhan, str) or re.fullmatch(r'[0-9a-f]{32}', bien_nhan) is None:
            raise _loi('MASK_BIEN_NHAN_KHONG_HOP_LE')
        cua = getattr(self.quyen, 'bien_nhan_duyet', None)
        if not callable(cua):
            raise _loi('MASK_ADMIN_CAN_CORE')
        kho = KhoNganBiMat(self.viec, vung=vung)
        muc = kho.doc(ma)
        if muc is None or muc['row_version'] != phien or muc['trang_thai'] != 'CHO_DUYET':
            raise _loi('MASK_XUNG_DOT')
        alias = (kiem_ma_junsky(ma_junsky) if ma_junsky is not None
                 else bi_danh_moi(muc['nhom'])) if duyet else None
        # Quyền xem/duyệt, phiên/vùng, chống replay và thu hồi đồng thời thuộc
        # cửa Core chung; engine không tự ký vé hay giữ sổ biên nhận trên máy.
        da_ghi = False
        try:
            with cua(self.viec, bien_nhan=bien_nhan, id_dinh_danh=ma, row_version=phien,
                     vung=vung, quyet_dinh='DUYET' if duyet else 'TU_CHOI', bi_danh=alias) as ve:
                if (type(ve) is not dict or set(ve) != {'id_dinh_danh', 'row_version'}
                        or ve['id_dinh_danh'] != ma or type(ve['row_version']) is not int
                        or ve['row_version'] != phien):
                    raise _loi('MASK_BIEN_NHAN_KHONG_HOP_LE')
                if self._kiem() != vung:
                    raise _loi('MASK_KHONG_CO_QUYEN')
                if duyet:
                    kho.duyet_cung_id(ma, row_version=phien, bi_danh=alias)
                else:
                    kho.sua_metadata([{'id_dinh_danh': ma, 'row_version': phien,
                                       'gia_tri': {'trang_thai': 'TU_CHOI'}}])
                da_ghi = True
        except Exception:
            if da_ghi:
                raise ChuaRo(self._tuong_quan) from None
            raise
        if not da_ghi:
            raise _loi('MASK_KHO_LOI')
        return {'id_dinh_danh': ma, 'bi_danh': alias,
                'trang_thai': 'CHINH_THUC' if duyet else 'TU_CHOI'}

    @_an_loi
    def duyet(self, id_dinh_danh, row_version, *, bien_nhan=None, ma_junsky=None):
        return self._quyet_dinh(id_dinh_danh, row_version, bien_nhan,
                               ma_junsky=ma_junsky, duyet=True)

    @_an_loi
    def tu_choi(self, id_dinh_danh, row_version, *, bien_nhan=None):
        return self._quyet_dinh(id_dinh_danh, row_version, bien_nhan,
                               ma_junsky=None, duyet=False)
