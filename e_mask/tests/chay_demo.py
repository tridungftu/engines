"""Chạy ví dụ thật của gói bằng CoreGia + quyền/ngăn DEMO được tiêm ngoài gói."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'goi/e_mask'))
from kho_tri_thuc_sdk.thu import CoreGia
from e_mask.chay import tao_app
from ho_tro_duyet_lich_su import DuyetDinhDanh
from e_mask.kho_ngan import KHAI_NGAN
from e_mask.ngan import NganBoNho
from ho_tro_ngan import ADMIN, QuyenNganDemo, TEN


class CoreDemo(CoreGia):
    def __init__(self, quyen):
        super().__init__()
        self.quyen = quyen

    def giao_viec(self, nang_luc, dau_vao, tham_so=None, **kw):
        ma = super().giao_viec(nang_luc, dau_vao, tham_so, **kw)
        if nang_luc == 'mask.mo_che_van_ban@1':
            self.quyen.cap(ma, loai='mo_che', ma_yeu_cau=dau_vao['tra_loi_ai']['chuyen_tiep']['ma_yeu_cau'])
        else:
            self.quyen.cap(ma)
        return ma


def chay():
    ngan, quyen = NganBoNho(KHAI_NGAN), QuyenNganDemo()
    # Danh mục/mã yêu cầu DEMO cấp từ bên tin cậy, không có cờ DEMO trong engine.
    DuyetDinhDanh(ngan, ADMIN).nhap_demo([{'gia_tri': TEN, 'nhom':'CONG_TY', 'ma_junsky':'KH-DEMO-001'}], thuc_hien=True)
    with ngan.lo() as lo:
        lo.them('ma_yeu_cau', {'vung':'DEMO', 'khoa':'DEMO'},
                {'module':quyen.module, 'nguoi_gui':quyen.nguoi_gui, 'tai_lieu':quyen.tai_lieu,
                 'trang_thai':'DANG_XU_LY'})
    return CoreDemo(quyen).chay_thu_demo(tao_app(ngan=ngan, quyen=quyen))


if __name__ == '__main__':
    ds = chay()
    for kq in ds:
        print('[ĐẠT]' if kq['trang_thai'] == 'XONG' else '[LỖI]', kq['ten'], kq['trang_thai'],
              '' if not kq['loi'] else kq['loi']['ma'])
    print('Đã kiểm bằng Core giả (CoreGia).')
    raise SystemExit(0 if ds and all(k['trang_thai'] == 'XONG' for k in ds) else 1)
