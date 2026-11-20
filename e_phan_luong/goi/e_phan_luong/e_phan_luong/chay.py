"""Cổng SDK PL-0; các năng lực chưa triển khai đều từ chối rõ ràng."""

from kho_tri_thuc_sdk.engine import Engine as EngineSDK, LoiNghiepVu


if not callable(getattr(EngineSDK, "_ghi", None)):
    raise RuntimeError("SDK thiếu cổng nhật ký cần thiết để khởi động an toàn.")


class Engine(EngineSDK):
    """Theo mẫu e_kiem_excel: nhật ký SDK chỉ chứa mã cố định."""

    def _ghi(self, cau):
        super()._ghi("PL_SDK_THONG_BAO")


app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("audit.phan_luong@1")
def phan_luong(viec):
    """Lô JSON (PL-6 thêm Excel/CSV): lớp 1/2/3, tệp kết quả, dấu hoàn tất trong Core."""
    from . import quy_trinh

    quy_trinh.bat_dau(viec)
    lo, du_lieu = quy_trinh.doc_tep_lo(viec)
    return {"loai": "truong", "truong": quy_trinh.chay_phan_luong(viec, lo, du_lieu)}


@app.nang_luc("audit.chuan_bi_phan_loai@1")
def chuan_bi_phan_loai(viec):
    from . import ngan_chuoi, quy_trinh

    quy_trinh.bat_dau(viec)
    lo, du_lieu = quy_trinh.doc_tep_lo(viec)
    cd = quy_trinh.doc_cai_dat(viec.tham_so, lo)
    return ngan_chuoi.chuan_bi(viec, lo, du_lieu, cd)


@app.nang_luc("audit.phan_luong_sau_ai@1")
def phan_luong_sau_ai(viec):
    from . import ngan_chuoi, quy_trinh

    quy_trinh.bat_dau(viec)
    return {"loai": "truong", "truong": ngan_chuoi.phan_luong_sau_ai(viec)}


@app.nang_luc("audit.phan_luong_hoa_don@1")
def phan_luong_hoa_don(viec):
    from . import quy_trinh

    quy_trinh.bat_dau(viec)
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.ghi_ket_qua@1")
def ghi_ket_qua(viec):
    from . import __version__, ket_qua, ngan_ket_qua, quy_trinh

    quy_trinh.bat_dau(viec)
    viec.tien_do(5, "Đang đọc kết quả kiểm.")
    with viec.mo_tep(viec.dau_vao["tep"]["tep_id"]) as tep:
        du_lieu = tep.read(ket_qua.TOI_DA_BYTE + 1)
    noi_dung = ket_qua.doc_ket_qua_json(du_lieu)
    dem = ngan_ket_qua.ghi_ket_qua(viec, noi_dung)
    return {"loai": "truong", "truong": {**dem, "phien_ban_engine": __version__}}


if __name__ == "__main__":
    app.chay()
