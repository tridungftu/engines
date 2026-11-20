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
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.chuan_bi_phan_loai@1")
def chuan_bi_phan_loai(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.phan_luong_sau_ai@1")
def phan_luong_sau_ai(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.phan_luong_hoa_don@1")
def phan_luong_hoa_don(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


@app.nang_luc("audit.ghi_ket_qua@1")
def ghi_ket_qua(viec):
    raise LoiNghiepVu("CHUA_LAM", "Năng lực đang được xây dựng.")


if __name__ == "__main__":
    app.chay()
