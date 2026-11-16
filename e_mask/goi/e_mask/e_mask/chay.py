"""Năng lực SDK 2.2.0; bản rõ/map chỉ trong RAM của chuỗi P4."""
from functools import wraps
from pathlib import Path

from kho_tri_thuc_sdk.engine import ChuaRo, Engine, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy

from . import phong_bi
from .kho_anh_xa_ram import KhoAnhXaRAM
from .ngan import CauHinhKhongHopLe, NganKhongHopLe, NganXungDot
from .quyen_yeu_cau import loi_kho
from .mo_che_ram import MoCheRAM


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


def tao_app(*, ngan=None, quyen=None, cong_chuan_bi_ai=None, cong_hau_kiem_ai=None,
            cong_mo_che=None, cong_chuan_bi_tep=None, cong_hau_kiem_tep=None,
            cong_mo_tep=None):
    """Chỉ bên tích hợp truyền port; dữ liệu việc không thể cấp quyền này."""
    ung_dung = Engine.tu_khai_bao(str(Path(__file__).resolve().parents[1] / 'engine.json'))
    # ngan chỉ giữ tương thích chữ ký, không dựng kho ánh xạ/ngăn dự phòng.
    # Các consumer R5/R6 dùng đúng kho của app, không giữ một kho thứ hai.
    ung_dung.kho_anh_xa_ram = KhoAnhXaRAM(quyen=quyen)

    def bao_ve(ham):
        @wraps(ham)
        def goi(viec):
            # SDK 2.2.0 chưa cấp cổng ghim/lifecycle C-P4-01/02.
            # Không suy khả năng này từ so_viec_dong_thoi hoặc dữ liệu việc.
            ung_dung.kho_anh_xa_ram.kiem_san_sang()
            return ham(viec)
        return _loi_cong(goi)

    @ung_dung.nang_luc('mask.chuan_bi_tep_ai_cuc_bo@1')
    @bao_ve
    def chuan_bi_tep(viec):
        from .chuan_bi_tep import ChuanBiTep
        with phong_bi.viec_chuan_bi_tep(viec) as tep:
            return ChuanBiTep(ram=ung_dung.kho_anh_xa_ram, quyen=quyen,
                cong=cong_chuan_bi_tep,
                phien_ban_engine='e_mask ' + ung_dung.phieu['phien_ban']).chuan_bi(tep)

    def hau_kiem_tep(viec, nang_luc):
        from .hau_kiem_tep import HauKiemTep
        from .ho_so_tep import bao_ve as bao_ve_loi_tep
        from .kho_qua_core import CongHauKiemTepSDK

        @bao_ve_loi_tep
        def xu_ly():
            with CongHauKiemTepSDK(cong=cong_hau_kiem_tep, quyen=quyen,
                                   ram=ung_dung.kho_anh_xa_ram) as cong:
                return HauKiemTep(ram=ung_dung.kho_anh_xa_ram, quyen=quyen,
                    cong=cong, phien_ban_engine='e_mask ' + ung_dung.phieu['phien_ban']).hau_kiem(viec, nang_luc=nang_luc)
        return xu_ly()

    @ung_dung.nang_luc('mask.hau_kiem_tep_van_ban@1')
    @bao_ve
    def hau_kiem_tep_van_ban(viec):
        return hau_kiem_tep(viec, 'mask.hau_kiem_tep_van_ban@1')

    @ung_dung.nang_luc('mask.hau_kiem_tep_giu_dinh_dang@1')
    @bao_ve
    def hau_kiem_tep_giu_dinh_dang(viec):
        return hau_kiem_tep(viec, 'mask.hau_kiem_tep_giu_dinh_dang@1')

    @ung_dung.nang_luc('mask.mo_che_tep@1')
    @bao_ve
    def mo_tep(viec):
        from .kho_dinh_danh import MoTepSDK
        return MoTepSDK(ram=ung_dung.kho_anh_xa_ram, quyen=quyen,
                        cong=cong_mo_tep).mo(viec)

    @ung_dung.nang_luc('mask.hau_kiem_ai_cuc_bo@1')
    @bao_ve
    def hau_kiem_ai(viec):
        from .hau_kiem_ai import HauKiemAI
        return HauKiemAI(ngan=None, quyen=quyen, cong=cong_hau_kiem_ai,
                         ram=ung_dung.kho_anh_xa_ram,
                         phien_ban_engine='e_mask ' + ung_dung.phieu['phien_ban']).hau_kiem(viec)

    @ung_dung.nang_luc('mask.chuan_bi_ai_cuc_bo@1')
    @bao_ve
    def chuan_bi_ai(viec):
        from .chuan_bi_ai import ChuanBiAI
        return ChuanBiAI(ngan=None, quyen=quyen, cong=cong_chuan_bi_ai,
                         ram=ung_dung.kho_anh_xa_ram,
                         phien_ban_engine='e_mask ' + ung_dung.phieu['phien_ban']).chuan_bi(viec)

    @ung_dung.nang_luc('mask.che_van_ban@1')
    @bao_ve
    def che(viec):
        # Lớp quy tắc riêng chưa có bằng chứng chất lượng R3; không dùng
        # kho lịch sử để phát hành hoặc lưu map. Chuỗi Local đi qua R5.
        from .tra_cuu_dinh_danh import chan_phat_hanh
        with ung_dung.kho_anh_xa_ram.buoc(viec):
            phong_bi.doc_che(viec)
            chan_phat_hanh()

    @ung_dung.nang_luc('mask.mo_che_van_ban@1')
    @bao_ve
    def mo(viec):
        return MoCheRAM(ram=ung_dung.kho_anh_xa_ram, quyen=quyen,
                        cong=cong_mo_che).mo(viec)

    return ung_dung


app = tao_app()

if __name__ == '__main__':
    app.chay()
