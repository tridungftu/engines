"""Engine DEMO: đọc tệp văn bản thuần (.txt UTF-8) thành văn bản.

Năng lực tep.doc_van_ban@1: nhận "tep", trả "van_ban". Chỉ dùng SDK.
"""
try:
    from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
except ImportError:  # chạy trong mã nguồn Core, chưa cài gói SDK
    from kho_tri_thuc.sdk_core.engine import Engine, LoiNghiepVu

app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("tep.doc_van_ban@1")
def doc_van_ban(viec):
    tep = viec.dau_vao["tep"]
    viec.tien_do(10, "Đang đọc tệp")
    with viec.mo_tep(tep["tep_id"]) as f:
        du_lieu = f.read()
    try:
        van_ban = du_lieu.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise LoiNghiepVu(
            "TEP_KHONG_PHAI_UTF8",
            "Tệp không phải văn bản UTF-8. Hãy lưu lại tệp dưới dạng .txt UTF-8 rồi tải lên lại.",
        ) from None
    viec.tien_do(100, "Đã đọc xong tệp")
    return {"loai": "van_ban", "van_ban": van_ban}


if __name__ == "__main__":
    app.chay()
