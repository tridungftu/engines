"""Hai năng lực văn bản SDK; kho qua ngăn, quyền từ bên tích hợp tin cậy."""
from copy import deepcopy
from functools import wraps
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from . import che_van_ban as loi_che, phong_bi, tai_nguyen
from .kho_dinh_danh import KhoDinhDanh
from .cau_hinh import CauHinhKhongHopLe
from .kho_ngan import KHAI_NGAN
from .ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan


def _loi_cong(ham):
    @wraps(ham)
    def goi(viec):
        try:
            return ham(viec)
        except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
            raise LoiNghiepVu(exc.ma, exc.thong_diep,
                             thu_lai_duoc=exc.thu_lai_duoc) from None
    return goi


def _mo_ai(chu, ma, dong, ai, kho, viec):
    """Một giao dịch cho toàn bộ chuỗi AI, không đóng sau riêng tra_loi."""
    with kho.giao_dich():
        kho.doc_yeu_cau(ma)
        cac_kq = []
        def mo(chu, duong):
            viec.kiem_huy()
            kq = loi_che._mo_che(chu, ma, kho, False)
            for muc in kq['bi_danh_khong_ro']:
                muc['duong_truong'] = list(duong)
            cac_kq.append(kq)
            return kq['van_ban_da_mo_che']
        moi = deepcopy(ai)
        moi['tra_loi'] = mo(chu, ('tra_loi',))
        def de_quy(v, duong):
            if isinstance(v, str):
                return mo(v, duong)
            if isinstance(v, dict):
                return {k: de_quy(m, duong + (k,)) for k, m in v.items()}
            if isinstance(v, list):
                return [de_quy(m, duong + (i,)) for i, m in enumerate(v)]
            return v
        moi['du_lieu'] = de_quy(moi['du_lieu'], ('du_lieu',))
        doi_trich = False
        for i, muc in enumerate(moi['trich_dan']):
            cu = muc['cau']
            muc['cau'] = mo(cu, ('trich_dan', i, 'cau'))
            if cu != muc['cau']:
                doi_trich = True
                muc['can_kiem_lai'] = True
        if doi_trich:
            moi['kiem_trich_dan'] = {'dat': False, 'loi': ['Câu trích đã mở che; cần kiểm tra lại với tài liệu gốc.']}
            moi['trang_thai'] = 'khong_thay_can_cu'
        du = all(k['mo_day_du'] for k in cac_kq)
        tien_ngay = all(k['kiem_tien_ngay'] for k in cac_kq)
        if dong and du and tien_ngay:
            kho.dong_yeu_cau(ma)
        return dict(van_ban_da_mo_che=moi['tra_loi'], so_cho_mo=sum(k['so_cho_mo'] for k in cac_kq),
                    bi_danh_khong_ro=[m for k in cac_kq for m in k['bi_danh_khong_ro']],
                    mo_day_du=du, kiem_tien_ngay=tien_ngay,
                    trang_thai_ma_yeu_cau='DA_DONG' if dong and du and tien_ngay else 'DANG_XU_LY',
                    tra_loi_ai=moi)


def tao_app(*, ngan=None, quyen=None):
    """Chỉ bên tích hợp truyền port; dữ liệu việc không thể cấp quyền này."""
    ung_dung = Engine.tu_khai_bao(str(Path(__file__).resolve().parents[1] / 'engine.json'))
    if ngan is not None:
        ung_dung.ngan = ngan
    elif getattr(ung_dung, 'ngan', None) is None:
        ung_dung.ngan = NganBoNho(KHAI_NGAN)
    ngan = chon_ngan(ung_dung)

    def ngan_cua_viec(viec):
        ngan_viec = getattr(viec, 'ngan', None)
        return ngan if ngan_viec is None else ngan_viec

    @ung_dung.nang_luc('mask.che_van_ban@1')
    @_loi_cong
    def che(viec):
        chu, ds = phong_bi.doc_che(viec)
        viec.tien_do(10, 'Đang kiểm tra văn bản.')
        kho = KhoDinhDanh(ngan=ngan_cua_viec(viec), quyen=quyen)
        def xu_ly(kho):
            try:
                tai_nguyen.nap_tu_goi()
                kq = loi_che.che(chu, ds, kho)
            except tai_nguyen.ThieuTaiNguyen:
                raise LoiNghiepVu('MASK_THIEU_TAI_NGUYEN', 'Chưa có đủ tài nguyên nhận diện được phê duyệt.') from None
            except loi_che.LoiCheVanBan:
                raise LoiNghiepVu('MASK_DINH_DANH_CHUA_DAT', 'Chưa kiểm tra hết định danh. Không thể trả kết quả che.') from None
            if kq.get('gui_duoc'):
                phong_bi.ket_qua_che(kq, chu)
            return kq
        kq = kho.xu_ly(viec, xu_ly)
        viec.tien_do(100, 'Đã hoàn tất che văn bản.')
        return phong_bi.ket_qua_che(kq, chu)

    @ung_dung.nang_luc('mask.mo_che_van_ban@1')
    @_loi_cong
    def mo(viec):
        chu, ma, dong, ai = phong_bi.doc_mo(viec)
        viec.tien_do(10, 'Đang kiểm tra quyền mở che.')
        kho = KhoDinhDanh(ngan=ngan_cua_viec(viec), quyen=quyen)
        def xu_ly(kho):
            try:
                if ai is not None:
                    return _mo_ai(chu, ma, dong, ai, kho, viec)
                return loi_che.mo_che(chu, ma, kho, dong_viec=dong)
            except loi_che.LoiCheVanBan:
                raise phong_bi.loi('MASK_MA_YEU_CAU') from None
        kq = kho.xu_ly(viec, xu_ly, loai='mo_che', ma_yeu_cau=ma)
        viec.tien_do(100, 'Đã hoàn tất mở che văn bản.')
        return phong_bi.ket_qua_mo(kq, kq.get('tra_loi_ai'))

    return ung_dung


app = tao_app()

if __name__ == '__main__':
    app.chay()
