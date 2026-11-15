"""Đăng ký năng lực SDK 2.0; hỏi tài liệu và yêu cầu có khuôn chỉ qua Local AI."""
from functools import wraps

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .hoi import AdapterHoiAI
from .hoi_yeu_cau import goi_theo_yeu_cau
from .cau_hinh import CauHinhKhongHopLe
from .ngan import NganKhongHopLe, NganXungDot, chon_ngan
from .ngan_engine import tao_ngan_bo_nho

app = Engine.tu_khai_bao("engine.json")
if getattr(app, "ngan", None) is None:
    app.ngan = tao_ngan_bo_nho()
chon_ngan(app)
bo_hoi = AdapterHoiAI()


def loi_ngan_sdk(ham):
    @wraps(ham)
    def goi(viec):
        try:
            return ham(viec)
        except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
            raise LoiNghiepVu(exc.ma, exc.thong_diep,
                              thu_lai_duoc=exc.thu_lai_duoc) from None
    return goi


@app.nang_luc("ai.hoi_tai_lieu@1")
@loi_ngan_sdk
def hoi_tai_lieu(viec):
    return bo_hoi.goi(viec)


@app.nang_luc("ai.hoi_theo_yeu_cau@1")
@loi_ngan_sdk
def hoi_theo_yeu_cau(viec):
    return goi_theo_yeu_cau(viec, bo_hoi.cong_ai, phien_ban=app.phieu["phien_ban"])


if __name__ == "__main__":
    app.chay()
