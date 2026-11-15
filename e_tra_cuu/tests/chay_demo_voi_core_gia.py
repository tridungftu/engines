"""Cổng bổ sung §2.5: cùng chay_thu_demo, Ngan RAM và quyền/tệp con giả.

Chỉ tests được nạp DEMO. Không thay SDK/CLI, không chứng nhận quyền Core thật.
"""

from copy import deepcopy
from pathlib import Path
import socket
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi/e_tra_cuu"))

from e_tra_cuu.kiem_dau_vao import bam, doc_json
from ho_tro_tc_2 import BoDemo, GOI


def chay_demo():
    bo = BoDemo(thu_muc_demo=GOI / "demo")
    kq = []
    for vd in bo.app.phieu["chay_thu_demo"]:
        b = (GOI / vd["dau_vao"]["tep_demo"]).read_bytes()
        yc = doc_json(b)
        assert yc == bo.yeu_cau(yc["tac_vu"]), "DEMO phải khớp nguồn/tệp đã nạp thật."
        assert bam(b) == vd["tham_so"]["bam_yeu_cau"]
        ref = bo.tai(Path(vd["dau_vao"]["tep_demo"]).name, b)
        viec_id = bo.core.giao_viec(vd["nang_luc"], {"loai": "tep", "tep": ref["tep"]},
                                   deepcopy(vd["tham_so"]), phap_nhan_id="DEMO-P")
        bo.cap(viec_id, yc, ref)
        bo.core.chay(bo.app)
        ket_qua = bo.core.xem(viec_id)
        if ket_qua["trang_thai"] == "XONG":
            snapshot = bo.snapshot(ket_qua)
            assert snapshot["tac_vu"] == yc["tac_vu"] and snapshot["ket_qua"] is None
        kq.append({"ten": vd["ten"], **ket_qua})
    return kq


def main():
    dem_mang = 0

    def cam_mang(*args, **kwargs):
        nonlocal dem_mang
        dem_mang += 1
        raise AssertionError("DEMO không được gọi mạng.")

    with patch.object(socket.socket, "connect", cam_mang), patch.object(socket.socket, "connect_ex", cam_mang), \
            patch.object(socket, "create_connection", cam_mang), patch.object(socket, "getaddrinfo", cam_mang):
        kq = chay_demo()
    for k in kq:
        dat = k["trang_thai"] == "XONG"
        print(f'[{"ĐẠT" if dat else "LỖI"}] {k["ten"]}' + ("" if dat else ": " + str(k["loi"]["ma"])))
    dat = sum(k["trang_thai"] == "XONG" for k in kq)
    print(f"{dat}/{len(kq)} DEMO ĐẠT; mạng ngoài/Cloud={dem_mang}.")
    print("Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.")
    return 0 if kq and dat == len(kq) and dem_mang == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
