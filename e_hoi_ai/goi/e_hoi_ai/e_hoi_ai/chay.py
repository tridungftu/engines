"""Đăng ký năng lực SDK 2.0; AI-1 hỏi tài liệu chỉ qua Local AI."""
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .hoi import AdapterHoiAI

app = Engine.tu_khai_bao("engine.json")
bo_hoi = AdapterHoiAI()


@app.nang_luc("ai.hoi_tai_lieu@1")
def hoi_tai_lieu(viec):
    return bo_hoi.goi(viec)


@app.nang_luc("ai.hoi_theo_yeu_cau@1")
def hoi_theo_yeu_cau(viec):
    raise LoiNghiepVu("CHUA_LAM", "Chức năng hỏi theo yêu cầu chưa được triển khai.")


if __name__ == "__main__":
    app.chay()
