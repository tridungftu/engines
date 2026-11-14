"""Đăng ký năng lực SDK 2.0; hỏi tài liệu và yêu cầu có khuôn chỉ qua Local AI."""
from kho_tri_thuc_sdk.engine import Engine

from .hoi import AdapterHoiAI
from .hoi_yeu_cau import goi_theo_yeu_cau

app = Engine.tu_khai_bao("engine.json")
bo_hoi = AdapterHoiAI()


@app.nang_luc("ai.hoi_tai_lieu@1")
def hoi_tai_lieu(viec):
    return bo_hoi.goi(viec)


@app.nang_luc("ai.hoi_theo_yeu_cau@1")
def hoi_theo_yeu_cau(viec):
    return goi_theo_yeu_cau(viec, bo_hoi.cong_ai, phien_ban=app.phieu["phien_ban"])


if __name__ == "__main__":
    app.chay()
