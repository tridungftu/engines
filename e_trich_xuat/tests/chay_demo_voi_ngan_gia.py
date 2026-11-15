"""Cổng DEMO có ngăn, chờ CLI SDK hỗ trợ cấu hình; không dùng tệp/env cấu hình."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"))

from kho_tri_thuc_sdk.thu import CoreGia
from e_trich_xuat.chay import KHAI_BAO_NGAN, tao_app
from e_trich_xuat.ngan import NganBoNho


def chay_demo():
    app = tao_app()
    app.ngan = NganBoNho(KHAI_BAO_NGAN)
    with app.ngan.lo() as lo:
        lo.them("cau_hinh", {}, {"ngan_sach_token_vao_toi_da": 16000})
    return CoreGia().chay_thu_demo(app)


def main():
    ket_qua = chay_demo()
    for kq in ket_qua:
        dat = kq["trang_thai"] == "XONG"
        print(f"[{'ĐẠT' if dat else 'LỖI'}] {kq['ten']}" +
              ("" if dat else f" ({kq['loi']['ma']})"))
    print("Đã kiểm bằng Core giả (CoreGia); ngăn DEMO trong RAM, 0 Cloud.")
    return int(any(kq["trang_thai"] != "XONG" for kq in ket_qua))


if __name__ == "__main__":
    raise SystemExit(main())
