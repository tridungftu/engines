"""Tiến trình app.chay thật đọc stdin, HTTP chỉ loopback MayChuGia."""
import json
import os
import secrets
import subprocess
import sys
import time

import pytest
from kho_tri_thuc_sdk.thu import CoreGia, MayChuGia
from e_trich_xuat.chay import GOC_GOI


@pytest.mark.parametrize("ca", ["mat_xac_nhan", "huy"])
def test_app_chay_stdin_http_loopback(ca, monkeypatch):
    core = CoreGia()
    tep = core.them_tep("DEMO.docx", (GOC_GOI / "demo/DEMO-hop-dong.docx").read_bytes(),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    viec = core.giao_viec("trich.doc_docx@1", {"loai": "tep", "tep": tep}, gui_kem_dau_vao=False)
    if ca == "mat_xac_nhan":
        core.gay_mat_xac_nhan("ket_qua")
        core.gay_mat_xac_nhan("ket_thuc")
    else:
        bao = core._tien_do
        def huy(ma, viec_id, pt, cau):
            core.huy(viec_id)
            return bao(ma, viec_id, pt, cau)
        monkeypatch.setattr(core, "_tien_do", huy)
    khoa = secrets.token_hex(24)  # Khóa giả mỗi phiên, không nằm trong mã/artifact.
    with MayChuGia(core, {"e_trich_xuat": khoa}) as may:
        env = {k: v for k, v in os.environ.items() if not k.startswith("KTT_")}
        env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.Popen([sys.executable, "-B", "-m", "e_trich_xuat.chay"], cwd=GOC_GOI,
                                env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            proc.stdin.write((json.dumps({"core_url": may.url, "khoa": khoa,
                                         "instance": "DEMO-tx6-stdin"}) + "\n").encode("utf-8"))
            proc.stdin.close()
            han = time.monotonic() + 12
            while time.monotonic() < han:
                kq = core.xem(viec)
                ack_du = ca != "mat_xac_nhan" or len([n for n in may.cac_loi_goi
                    if n["duong"].endswith("/ket-thuc")]) >= 2
                if kq["trang_thai"] in ("XONG", "HUY", "LOI") and ack_du:
                    break
                assert proc.poll() is None, "Tiến trình DEMO kết thúc sớm."
                time.sleep(0.02)
            assert kq["trang_thai"] == ("XONG" if ca == "mat_xac_nhan" else "HUY"), kq
            if ca == "mat_xac_nhan":
                assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1
                for duoi in ("ket-qua", "ket-thuc"):
                    ds = [n for n in may.cac_loi_goi if n["duong"].endswith("/" + duoi)]
                    assert len(ds) == 2 and len({n["idempotency_key"] for n in ds}) == 1
            else:
                assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == 0
            assert all(n["co_bearer"] and n["instance"] == "DEMO-tx6-stdin" for n in may.cac_loi_goi)
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=5)
            out, err = proc.stdout.read(), proc.stderr.read()
            proc.stdout.close()
            proc.stderr.close()
        assert khoa.encode() not in out + err and b"Traceback" not in err
