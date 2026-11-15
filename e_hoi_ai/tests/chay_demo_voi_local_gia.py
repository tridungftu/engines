"""Cổng DEMO AI-4: đã kiểm bằng Core giả (CoreGia) và Local HTTP giả."""
from copy import deepcopy
from pathlib import Path
import sys

sys.dont_write_bytecode = True
THU_MUC_TEST = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC_TEST.parent / "goi" / "e_hoi_ai"))

from kho_tri_thuc_sdk.thu import CoreGia
from e_hoi_ai.chay import app
from local_gia import LocalGia, TRA_LOI, nap_cau_hinh

DU_LIEU_DEMO = {"so_tien": {"so": 1000000, "tien_te": "VND"}, "ngay": "2026-10-30"}


def chuan_bi_local_demo(local):
    """Ba phản hồi DEMO theo thứ tự phiếu; giữ nguyên các handler thật của engine."""
    local.tra_loi_tung_luot = deepcopy([
        TRA_LOI, {"truong": []}, {"du_lieu": DU_LIEU_DEMO, **TRA_LOI},
    ])


def main(*, sdk_thu=False):
    from e_hoi_ai.ngan import NganBoNho
    import kho_tri_thuc_sdk.thu as thu
    co_ngan = hasattr(app, "ngan")
    ngan_cu = getattr(app, "ngan", None)
    try:
        app.ngan = NganBoNho()
        with LocalGia() as local:
            nap_cau_hinh(local.url)
            chuan_bi_local_demo(local)
            if sdk_thu:
                return thu.main([str(app.thu_muc_goi)])
            ket_qua = CoreGia().chay_thu_demo(app)
            dat = bool(ket_qua) and len(ket_qua) == len(app.phieu["chay_thu_demo"])
            for kq in ket_qua:
                xong = kq["trang_thai"] == "XONG"
                print(f"[{'ĐẠT' if xong else 'LỖI'}] {kq['ten']}")
                dat = dat and xong
            if local.so_luot_hoi != len(ket_qua) or local.tra_loi_tung_luot:
                print("[LỖI] Số lượt Local giả không khớp bộ ví dụ DEMO.")
                dat = False
            if dat:
                print(f"[ĐẠT] Đã kiểm bằng Core giả (CoreGia); {len(ket_qua)}/{len(ket_qua)} DEMO, "
                      f"{local.so_luot_hoi} lượt Local HTTP giả.")
            return 0 if dat else 1
    finally:
        if co_ngan:
            app.ngan = ngan_cu
        else:
            del app.ngan


if __name__ == "__main__":
    raise SystemExit(main(sdk_thu="--sdk-thu" in sys.argv))
