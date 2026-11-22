"""Engine DEMO: đổi văn bản thành chữ hoa.

Năng lực van_ban.chu_hoa@1: nhận "van_ban", trả "van_ban". Chỉ dùng SDK.
"""
try:
    from kho_tri_thuc_sdk.engine import Engine
except ImportError:  # chạy trong mã nguồn Core, chưa cài gói SDK
    from kho_tri_thuc.sdk_core.engine import Engine

app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("van_ban.chu_hoa@1")
def chu_hoa(viec):
    viec.tien_do(50, "Đang đổi chữ hoa")
    return {"loai": "van_ban", "van_ban": viec.dau_vao["van_ban"].upper()}


if __name__ == "__main__":
    app.chay()
