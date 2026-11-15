"""Cổng DEMO AI-4: đã kiểm bằng Core giả (CoreGia) và Local HTTP giả."""
from copy import deepcopy
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
THU_MUC_TEST = Path(__file__).resolve().parent
sys.path.insert(0, str(THU_MUC_TEST.parent / "goi" / "e_hoi_ai"))

from kho_tri_thuc_sdk.thu import CoreGia
from e_hoi_ai.chay import app
from local_gia import LocalGia, TRA_LOI, ghi_cau_hinh

DU_LIEU_DEMO = {"so_tien": {"so": 1000000, "tien_te": "VND"}, "ngay": "2026-10-30"}


def chuan_bi_local_demo(local):
    """Ba phản hồi DEMO theo thứ tự phiếu; giữ nguyên các handler thật của engine."""
    local.tra_loi_tung_luot = deepcopy([
        TRA_LOI, {"truong": []}, {"du_lieu": DU_LIEU_DEMO, **TRA_LOI},
    ])


def main():
    cau_hinh_cu = os.environ.get("KTT_ENGINE_CAU_HINH")
    try:
        with TemporaryDirectory(prefix="ktt-ai-4-demo-", dir=THU_MUC_TEST) as thu_muc, LocalGia() as local:
            tep = ghi_cau_hinh(thu_muc, local.url)
            os.environ["KTT_ENGINE_CAU_HINH"] = str(tep)
            chuan_bi_local_demo(local)
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
        if cau_hinh_cu is None:
            os.environ.pop("KTT_ENGINE_CAU_HINH", None)
        else:
            os.environ["KTT_ENGINE_CAU_HINH"] = cau_hinh_cu


if __name__ == "__main__":
    raise SystemExit(main())
