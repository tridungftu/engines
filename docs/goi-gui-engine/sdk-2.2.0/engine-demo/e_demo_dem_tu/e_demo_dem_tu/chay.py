"""Engine DEMO: đếm số từ và số dòng của văn bản.

Năng lực van_ban.dem_tu@1: nhận "van_ban", trả "truong" (so_tu, so_dong).
Cài đặt bước "bo_dong_trong": bỏ dòng chỉ có khoảng trắng khi đếm dòng. Chỉ dùng SDK.
"""
try:
    from kho_tri_thuc_sdk.engine import Engine
except ImportError:  # chạy trong mã nguồn Core, chưa cài gói SDK
    from kho_tri_thuc.sdk_core.engine import Engine

app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("van_ban.dem_tu@1")
def dem_tu(viec):
    dong = viec.dau_vao["van_ban"].splitlines()
    if viec.tham_so["bo_dong_trong"]:
        dong = [d for d in dong if d.strip()]
    viec.tien_do(50, "Đang đếm từ")
    return {"loai": "truong",
            "truong": {"so_tu": sum(len(d.split()) for d in dong), "so_dong": len(dong)}}


if __name__ == "__main__":
    app.chay()
