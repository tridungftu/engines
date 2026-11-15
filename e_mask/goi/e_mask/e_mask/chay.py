"""Năng lực SDK 2.2.0; cửa vòng đời RAM P4, nối nghiệp vụ ở R5/R6."""
from copy import deepcopy
from functools import wraps
from pathlib import Path

from kho_tri_thuc_sdk.engine import ChuaRo, Engine, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import che_van_ban as loi_che, phong_bi, tai_nguyen
from .kho_dinh_danh import KhoDinhDanh
from .kho_anh_xa_ram import KhoAnhXaRAM
from .kho_ngan import KHAI_NGAN
from .ngan import CauHinhKhongHopLe, NganBoNho, NganKhongHopLe, NganXungDot
from .quyen_yeu_cau import loi_kho


def _loi_cong(ham):
    @wraps(ham)
    def goi(viec):
        try:
            # SDK đã kiểm schema và điền TTL mặc định vào snapshot cấu hình.
            # Không chặn snapshot có trường mới trước kiểm ngữ cảnh/port của ham.
            return ham(viec)
        except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
            lop = type(exc)
            raise LoiNghiepVu(lop.ma, lop.thong_diep,
                             thu_lai_duoc=lop.thu_lai_duoc) from None
        except (ChuaRo, ViecDaHuy, LoiDuongTruyen, LoiNghiepVu):
            raise
        except Exception:
            raise loi_kho() from None
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


def tao_app(*, ngan=None, quyen=None, cong_chuan_bi_ai=None, cong_hau_kiem_ai=None):
    """Chỉ bên tích hợp truyền port; dữ liệu việc không thể cấp quyền này."""
    ung_dung = Engine.tu_khai_bao(str(Path(__file__).resolve().parents[1] / 'engine.json'))
    if ngan is None:
        from .chuan_bi_ai import KHAI_NGAN_CHUAN_BI_AI
        ngan = NganBoNho([*KHAI_NGAN, *KHAI_NGAN_CHUAN_BI_AI])
    # Không ghi đè app.ngan của SDK, không chọn viec.ngan cho kho bí danh.
    # Adapter nghiệp vụ cũ chờ R2/R5/R6; CĐ-36 không cho giải mã ngăn Core.
    # Handler thật còn bị chặn nếu thiếu cửa ghim/lifecycle P4 bên dưới.
    ung_dung.kho_bi_danh_ram = ngan
    ung_dung.kho_anh_xa_ram = ram = KhoAnhXaRAM(quyen=quyen)

    def bao_ve(ham):
        @wraps(ham)
        def goi(viec):
            # SDK 2.2.0 chưa cấp cổng ghim/lifecycle C-P4-01/02.
            # Không suy khả năng này từ so_viec_dong_thoi hoặc dữ liệu việc.
            ram.kiem_san_sang()
            return ham(viec)
        return _loi_cong(goi)

    def ngan_cua_viec(viec):
        return ngan

    @ung_dung.nang_luc('mask.hau_kiem_ai_cuc_bo@1')
    @bao_ve
    def hau_kiem_ai(viec):
        from .hau_kiem_ai import HauKiemAI
        return HauKiemAI(ngan=ngan_cua_viec(viec), quyen=quyen, cong=cong_hau_kiem_ai,
                         phien_ban_engine='e_mask ' + ung_dung.phieu['phien_ban']).hau_kiem(viec)

    @ung_dung.nang_luc('mask.chuan_bi_ai_cuc_bo@1')
    @bao_ve
    def chuan_bi_ai(viec):
        from .chuan_bi_ai import ChuanBiAI
        return ChuanBiAI(ngan=ngan_cua_viec(viec), quyen=quyen, cong=cong_chuan_bi_ai,
                         phien_ban_engine='e_mask ' + ung_dung.phieu['phien_ban']).chuan_bi(viec)

    @ung_dung.nang_luc('mask.che_van_ban@1')
    @bao_ve
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
    @bao_ve
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
