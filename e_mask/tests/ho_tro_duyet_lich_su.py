"""Fixture RAM lịch sử MASK-6, chỉ phục vụ hồi quy; không thuộc gói chạy R7."""
from copy import deepcopy
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_mask.che_van_ban import _kiem_dinh_danh, chuan_hoa, chuan_bi_danh
from e_mask.kho_ngan import AnhNgan, CAC_TIEN_TO, bi_danh_moi
from e_mask.quyen_yeu_cau import loi_kho


def _khong_quyen():
    return LoiNghiepVu('MASK_KHONG_CO_QUYEN', 'Chỉ quản trị viên được thực hiện thao tác này.')


def kiem_ma_junsky(ma):
    if (not isinstance(ma, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', ma)
            or any(ma.upper().startswith(t) for t in CAC_TIEN_TO)):
        raise LoiNghiepVu('MASK_DAU_VAO', 'Mã đối tác chưa hợp lệ hoặc trùng tiền tố tự sinh.')
    return '[[' + ma + ']]'


def kiem_bi_danh(dl, bi_danh, cum):
    b = chuan_bi_danh(bi_danh)
    for bang in ('dinh_danh', 'cho_duyet', 'bi_danh_tam'):
        for muc in dl[bang].values():
            cac_ma = (muc['bi_danh'], muc.get('bi_danh_tam'))
            if any(m and chuan_bi_danh(m) == b for m in cac_ma) and chuan_hoa(muc['gia_tri']) != cum:
                raise loi_kho('MASK_XUNG_DOT')


class DuyetDinhDanh:
    def __init__(self, ngan, quyen):
        self.ngan, self.quyen = ngan, quyen

    def _kiem(self):
        try:
            vung = self.quyen.xac_minh_admin()
            if vung not in ('DEMO', 'THAT'):
                raise ValueError
            return vung
        except Exception:
            raise _khong_quyen() from None

    def danh_sach(self):
        anh = AnhNgan(self.ngan, self._kiem())
        return [{'gia_tri': deepcopy(m.gia_tri), 'row_version': m.row_version}
                for m in anh.cu['cho_duyet'].values()]

    def duyet(self, khoa, row_version, *, ma_junsky=None):
        vung = self._kiem()
        anh = AnhNgan(self.ngan, vung)
        muc = anh.cu['cho_duyet'].get(khoa)
        if muc is None or muc.row_version != row_version:
            raise loi_kho('MASK_XUNG_DOT')
        moi = deepcopy(muc.gia_tri)
        bi_danh = kiem_ma_junsky(ma_junsky) if ma_junsky is not None else bi_danh_moi(moi['nhom'])
        kiem_bi_danh(anh.moi, bi_danh, khoa)
        moi.update(bi_danh_tam=moi['bi_danh'], bi_danh=bi_danh, nguon='chinh_thuc')
        moi.pop('so_lan_gap', None)
        anh.dat('dinh_danh', khoa, moi)
        del anh.moi['cho_duyet'][khoa]
        self._kiem()
        anh.chot()
        return bi_danh

    def tu_choi(self, khoa, row_version):
        anh = AnhNgan(self.ngan, self._kiem())
        muc = anh.cu['cho_duyet'].get(khoa)
        if muc is None or muc.row_version != row_version:
            raise loi_kho('MASK_XUNG_DOT')
        del anh.moi['cho_duyet'][khoa]
        # Giữ tên/alias trong bi_danh_tam cho các yêu cầu còn xử lý.
        self._kiem()
        anh.chot()

    def don(self):
        anh = AnhNgan(self.ngan, self._kiem())
        dl = anh.moi
        dang_mo = {k for k, m in dl['ma_yeu_cau'].items() if m['trang_thai'] == 'DANG_XU_LY'}
        giu = {m['bi_danh'] for m in dl['dau_gap'].values()
               if m.get('loai_dau') == 'tham_chieu' and m['ma_yeu_cau'] in dang_mo}
        giu.update(chuan_bi_danh(m['bi_danh']) for m in dl['cho_duyet'].values())
        xoa = set(dl['bi_danh_tam']) - giu
        for b in xoa:
            del dl['bi_danh_tam'][b]
        for k, muc in list(dl['dinh_danh'].items()):
            if muc.get('bi_danh_tam') and chuan_bi_danh(muc['bi_danh_tam']) in xoa:
                moi = dict(muc)
                del moi['bi_danh_tam']
                anh.dat('dinh_danh', k, moi)
        self._kiem()
        anh.chot()
        return len(xoa)

    def dong(self, ma_yeu_cau):
        anh = AnhNgan(self.ngan, self._kiem())
        cu = anh.moi['ma_yeu_cau'].get(ma_yeu_cau)
        if cu is None:
            raise loi_kho('MASK_MA_YEU_CAU')
        anh.dat('ma_yeu_cau', ma_yeu_cau, dict(cu, trang_thai='DA_DONG'))
        self._kiem()
        anh.chot()

    def nhap_demo(self, danh_sach, *, thuc_hien=False):
        """Mặc định chạy khô. Không nhận đường dẫn hay mã danh mục cũ."""
        anh = AnhNgan(self.ngan, self._kiem())
        truoc, them = len(anh.moi['dinh_danh']), 0
        if not isinstance(danh_sach, list):
            raise LoiNghiepVu('MASK_DAU_VAO', 'Danh mục chưa hợp lệ.')
        for muc in danh_sach:
            try:
                if not isinstance(muc, dict) or set(muc) != {'gia_tri', 'nhom', 'ma_junsky'}:
                    raise ValueError
                _kiem_dinh_danh([muc], la_khai_bao=True)
                b = kiem_ma_junsky(muc['ma_junsky'])
                khoa = chuan_hoa(muc['gia_tri'])
                cu = anh.moi['dinh_danh'].get(khoa)
                if cu:
                    if cu['nhom'] != muc['nhom'] or chuan_bi_danh(cu['bi_danh']) != chuan_bi_danh(b):
                        raise loi_kho('MASK_XUNG_DOT')
                    continue
                if khoa in anh.moi['cho_duyet']:
                    raise loi_kho('MASK_XUNG_DOT')
                kiem_bi_danh(anh.moi, b, khoa)
                anh.dat('dinh_danh', khoa, {'gia_tri': muc['gia_tri'], 'nhom': muc['nhom'],
                                          'bi_danh': b, 'nguon': 'chinh_thuc'})
                them += 1
            except (ValueError, TypeError, KeyError):
                raise LoiNghiepVu('MASK_DAU_VAO', 'Danh mục có dòng chưa hợp lệ.') from None
        if thuc_hien:
            self._kiem()
            anh.chot()
        return {'so_dong_truoc': truoc, 'so_dong_them': them, 'so_dong_sau': truoc + them,
                'chay_kho': not thuc_hien}
