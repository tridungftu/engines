"""SDK app.chay đọc stdin qua MayChuGia loopback; không chèn adapter runtime."""

import json
import os
import secrets
import socket
import subprocess
import sys

import pytest
from kho_tri_thuc_sdk.thu import CoreGia, MayChuGia

from e_tra_cuu.chay import app
from ho_tro_tc_2 import GOI
from e_tra_cuu.kiem_dau_vao import bam


@pytest.mark.parametrize("co_cau_hinh,ma_loi", [(False, "CHUA_CAU_HINH"), (True, "TC_CHUA_CO_CUA_CORE")])
def test_app_chay_bootstrap_stdin_http_that_loopback(monkeypatch, co_cau_hinh, ma_loi):
    core = CoreGia(app)
    vd = app.phieu["chay_thu_demo"][0]
    raw = (GOI / vd["dau_vao"]["tep_demo"]).read_bytes()
    tep = core.them_tep("yeu-cau-DEMO.json", raw, "application/json")
    if co_cau_hinh:
        b = (GOI / "demo/danh-muc-DEMO.json").read_bytes()
        dm = core.them_tep("danh-muc-DEMO.json", b, "application/json")
        core.dat_cau_hinh(app.ma, {"phien_ban": 1, "quy_tac_nhom": {"tep_id": dm["tep_id"], "bam": bam(b)}})
    i = core.giao_viec(vd["nang_luc"], {"loai": "tep", "tep": tep}, vd["tham_so"],
                       phap_nhan_id="DEMO-P", gui_kem_dau_vao=False)
    khoa_demo = secrets.token_urlsafe(32)
    instance = "DEMO-tc10-stdin"
    env = {k: v for k, v in os.environ.items()
           if k not in {"KTT_CORE_URL", "KTT_ENGINE_KHOA", "KTT_ENGINE_INSTANCE", "PYTHONPATH"}}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", NO_PROXY="127.0.0.1,localhost,::1")
    # HTTPServer không cần DNS ngoài. Parent vẫn giữ các lệnh connect bị chặn.
    monkeypatch.setattr(socket, "getfqdn", lambda name="": "localhost")
    code = '''
import ipaddress
import socket
from e_tra_cuu.chay import app
connect = socket.socket.connect
connect_ex = socket.socket.connect_ex
def chi_loopback(self, address):
    assert ipaddress.ip_address(address[0]).is_loopback, "Chỉ cho phép loopback DEMO."
    return connect(self, address)
def chi_loopback_ex(self, address):
    assert ipaddress.ip_address(address[0]).is_loopback, "Chỉ cho phép loopback DEMO."
    return connect_ex(self, address)
socket.socket.connect = chi_loopback
socket.socket.connect_ex = chi_loopback_ex
app.chay(dung_khi_het_viec=True)
'''
    with MayChuGia(core, {app.ma: khoa_demo}) as may:
        stdin = json.dumps({"core_url": may.url, "khoa": khoa_demo, "instance": instance}) + "\n"
        p = subprocess.run([sys.executable, "-B", "-c", code], cwd=GOI, input=stdin,
            env=env, text=True, encoding="utf-8", capture_output=True, timeout=25)
        assert p.returncode == 0, p.stderr
        assert khoa_demo not in p.stdout + p.stderr
        calls = list(may.cac_loi_goi)
    q = core.xem(i)
    assert q["trang_thai"] == "LOI" and q["loi"]["ma"] == ma_loi and q["ket_qua"] is None
    assert calls and all(c["ma_engine"] == app.ma and c["instance"] == instance and c["co_bearer"] for c in calls)
    assert calls[0]["duong"] == f"/api/v1/engine/{app.ma}/san-sang"
    assert any(c["duong"] == f"/api/v1/engine/viec/{i}/dau-vao" for c in calls)
    assert not any(c["duong"].endswith("/ket-qua") for c in calls)
    assert core.so_lan_ghi["ket_qua"] == 0 and core.so_lan_ghi["ket_thuc"] == 1
    end = [c for c in calls if c["duong"].endswith("/ket-thuc")]
    assert len(end) == 1 and end[0]["idempotency_key"]
    assert "C:\\" not in q["loi"]["thong_diep"] and "D:\\" not in q["loi"]["thong_diep"]
