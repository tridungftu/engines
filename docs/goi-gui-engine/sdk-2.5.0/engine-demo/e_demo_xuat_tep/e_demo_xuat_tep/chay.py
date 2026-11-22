"""Nhận văn bản UTF-8, nộp thống kê JSON bằng cửa tệp ra của SDK."""
import json

try:
    from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
except ImportError:
    from kho_tri_thuc.sdk_core.engine import Engine, LoiNghiepVu

app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("tep.xuat_thong_ke@1")
def xuat_thong_ke(viec):
    viec.tien_do(10, "Đang đọc tệp văn bản")
    with viec.mo_tep(viec.dau_vao["tep"]["tep_id"]) as tep:
        du_lieu = tep.read()
    try:
        van_ban = du_lieu.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise LoiNghiepVu(
            "TEP_KHONG_PHAI_UTF8",
            "Tệp không phải văn bản UTF-8. Hãy lưu lại dưới dạng .txt UTF-8 rồi gửi lại.",
        ) from None
    dong = van_ban.splitlines()
    if dong and dong[0].strip() == "LOI-DEMO":
        raise LoiNghiepVu(
            "TEP_DEMO_GAY_LOI",
            "Tệp DEMO yêu cầu báo lỗi để kiểm thử. Hãy gửi tệp văn bản khác.",
        )
    ket_qua = {"so_dong": len(dong), "so_tu": len(van_ban.split()),
               "dong_dau": dong[0][:200] if dong else ""}
    noi_dung = (json.dumps(ket_qua, ensure_ascii=False) + "\n").encode("utf-8")
    tep_ra = viec.tai_tep_ra("ket-qua.json", noi_dung, "application/json")
    viec.tien_do(100, "Đã tạo tệp kết quả")
    return {"loai": "tep", "tep": tep_ra}


if __name__ == "__main__":
    app.chay()
