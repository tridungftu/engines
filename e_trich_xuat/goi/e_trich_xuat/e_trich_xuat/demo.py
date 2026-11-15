"""Nạp hồ sơ DEMO vào Core giả bằng API công khai, chỉ gọi từ cổng kiểm.

SDK 2.0 CLI chưa hỗ trợ tệp tham chiếu trong loại riêng (C-TX-04).
Không được gọi helper này từ handler hoặc tự tạo cấu hình cho engine.
"""

from copy import deepcopy
import json
from pathlib import Path

from .tham_so import bam_bytes, json_bytes


def nap_ho_so_demo(core, app):
    """Chỉ đổi tham chiếu tệp và băm request khi Core cấp tep_id mới.

    Mẫu đầu vào đầy đủ nằm trong manifest; không dựng phiếu/handlers thay thế.
    Hồ sơ trong gói có bytes/băm/kích thước thật, chỉ chứa dữ liệu DEMO.
    """
    phieu = deepcopy(app.phieu)
    mau = next(v for v in phieu["chay_thu_demo"] if v["nang_luc"] == "trich.hau_kiem@1")
    ai = mau["dau_vao"]["tra_loi_ai"]
    meta = ai["chuyen_tiep"]["trich_xuat"]
    raw = (Path(app.thu_muc_goi) / "demo/DEMO-ho-so-hau-kiem.json").read_bytes()
    if len(raw) != meta["ho_so_hau_kiem"]["kich_thuoc"] or bam_bytes(raw) != meta["bam_ho_so_hau_kiem"]:
        raise ValueError("Hồ sơ DEMO không khớp mã kiểm tra.")
    hs = json.loads(raw)
    tep = core.them_tep(meta["ho_so_hau_kiem"]["ten"], raw, "application/json")
    meta["ho_so_hau_kiem"] = tep
    req = {"tai_lieu": hs["tai_lieu"]["van_ban"], **hs["yeu_cau_ai"],
           "chuyen_tiep": ai["chuyen_tiep"]}
    ai["bam_dau_vao"] = bam_bytes(json_bytes({"loai": "yeu_cau_ai", "yeu_cau_ai": req}))
    for vd in phieu["chay_thu_demo"]:
        if vd["nang_luc"] == "trich.xuat_ket_qua@1":
            b = vd["dau_vao"]["bang_trich_xuat"]
            b["nguon"]["ho_so_hau_kiem"] = deepcopy(tep)
            b["ai"]["bam_dau_vao"] = ai["bam_dau_vao"]
    app.phieu = phieu
