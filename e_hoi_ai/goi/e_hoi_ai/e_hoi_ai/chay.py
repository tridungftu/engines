"""Đăng ký hai năng lực; AI-0 chưa thực hiện hỏi AI."""
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("ai.hoi_tai_lieu@1")
def hoi_tai_lieu(viec):
    raise LoiNghiepVu("CHUA_LAM", "Chức năng hỏi tài liệu chưa được triển khai.")


@app.nang_luc("ai.hoi_theo_yeu_cau@1")
def hoi_theo_yeu_cau(viec):
    raise LoiNghiepVu("CHUA_LAM", "Chức năng hỏi theo yêu cầu chưa được triển khai.")


if __name__ == "__main__":
    app.chay()
