"""AI-4 đã kiểm bằng Core giả (CoreGia), Local giả và HTTP loopback thật."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

import pytest
from kho_tri_thuc_sdk.thu import CoreGia, MayChuGia

import chay_demo_voi_local_gia as bo_demo
from e_hoi_ai.chay import app
from local_gia import TAI_LIEU, TRICH_TIEN, TRICH_NGAY
from test_hoi_tai_lieu import khong_mang_ngoai_va_khong_cloud, local


def kiem_ket_qua_demo(ket_qua):
    assert len(ket_qua) == 3
    assert all(kq["trang_thai"] == "XONG" and kq["loi"] is None for kq in ket_qua)
    tien_ngay, khong_dap_an, co_khuon = [kq["ket_qua"] for kq in ket_qua]
    assert tien_ngay["truong"] == {
        "tra_loi": "1.000.000 VND\n30/10/2026", "co_can_cu": True,
        "trich_dan": TRICH_TIEN + "\n" + TRICH_NGAY, "model": "model-demo",
        "ly_do_chon_model": "quy_tac_ma_prompt",
    }
    assert khong_dap_an["truong"]["co_can_cu"] is False
    assert khong_dap_an["truong"]["tra_loi"] == "không thấy căn cứ"
    assert khong_dap_an["truong"]["trich_dan"] == ""
    ra = co_khuon["tra_loi_ai"]
    assert ra["du_lieu"] == {
        "so_tien": {"so": 1000000, "tien_te": "VND"}, "ngay": "2026-10-30",
    }
    assert ra["trang_thai"] == "co_can_cu" and ra["nha_cung_cap"] == "local"
    assert ra["kiem_trich_dan"] == {"dat": True, "loi": []}
    assert ra["chuyen_tiep"] == {"nhan": "DEMO", "ma_hop_dong": "DEMO-001"}
    assert [trich["cau"] for trich in ra["trich_dan"]] == [TRICH_TIEN, TRICH_NGAY]
    for trich in ra["trich_dan"]:
        assert TAI_LIEU[trich["bat_dau"]:trich["ket_thuc"]] == trich["cau"]


def test_toan_bo_demo_dung_dap_an_va_khuon(local):
    for vd in app.phieu["chay_thu_demo"]:
        assert "DEMO" in vd["ten"]
        dau_vao = vd["dau_vao"]
        tai_lieu = dau_vao.get("van_ban") or dau_vao["yeu_cau_ai"]["tai_lieu"]
        assert tai_lieu == TAI_LIEU
    bo_demo.chuan_bi_local_demo(local)
    kiem_ket_qua_demo(CoreGia().chay_thu_demo(app))
    assert local.so_luot_hoi == 3 and not local.tra_loi_tung_luot
    assert local.yeu_cau[2]["response_format"]["type"] == "json_schema"


@pytest.mark.parametrize("thanh_cong", [True, False, None], ids=["dat", "loi", "rong"])
def test_cong_demo_ma_thoat_va_cau_hinh_trong_tests(monkeypatch, thanh_cong):
    chay_goc = CoreGia.chay_thu_demo
    cau_hinh_da_dung = []

    def chay_demo(core, ung_dung):
        tep = Path(os.environ["KTT_ENGINE_CAU_HINH"])
        assert tep.is_relative_to(bo_demo.THU_MUC_TEST) and tep.is_file()
        cau_hinh_da_dung.append(tep)
        ket_qua = chay_goc(core, ung_dung)
        if thanh_cong is None:
            return []
        if not thanh_cong:
            ket_qua[-1]["trang_thai"] = "LOI"
        return ket_qua

    # Biến ban đầu có thể trỏ máy thật: bộ chạy phải thay trước khi đọc cấu hình.
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", "cau-hinh-DEMO-ban-dau.json")
    monkeypatch.setattr(CoreGia, "chay_thu_demo", chay_demo)
    assert bo_demo.main() == (0 if thanh_cong else 1)
    assert os.environ["KTT_ENGINE_CAU_HINH"] == "cau-hinh-DEMO-ban-dau.json"
    assert cau_hinh_da_dung and not cau_hinh_da_dung[0].exists()


def test_app_chay_doc_stdin_qua_may_chu_gia_http(local):
    core = CoreGia()
    cac_ma = [core.giao_viec(vd["nang_luc"], vd["dau_vao"], vd["tham_so"],
                             gui_kem_dau_vao=False) for vd in app.phieu["chay_thu_demo"]]
    bo_demo.chuan_bi_local_demo(local)
    khoa_demo = secrets.token_urlsafe(32)
    instance = "demo-ai-4-stdin"
    moi_truong = {k: v for k, v in os.environ.items()
                 if k not in {"KTT_CORE_URL", "KTT_ENGINE_KHOA", "KTT_ENGINE_INSTANCE"}}
    moi_truong.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    # Chạy tiến trình thật, stdin là pipe; không truyền DuongTruyen vào app.chay().
    ma_chay = '''
import ipaddress
import socket
from e_hoi_ai import chay
from e_hoi_ai.cong_ai import CongAI, NhaCungCapLocal

ket_noi_goc = socket.socket.connect
def chi_loopback(self, dia_chi):
    assert ipaddress.ip_address(dia_chi[0]).is_loopback, "Chỉ dùng loopback DEMO."
    return ket_noi_goc(self, dia_chi)
socket.socket.connect = chi_loopback

class CloudGia:
    so_luot = 0
    def hoi(self, *args, **kwargs):
        self.so_luot += 1
        raise AssertionError("Bản 1 không gọi Cloud.")
cloud = CloudGia()
chay.bo_hoi.cong_ai = CongAI(nha_cung_cap={"local": NhaCungCapLocal(), "cloud": cloud})
chay.app.chay(dung_khi_het_viec=True)
assert cloud.so_luot == 0, "Có lượt Cloud ngoài phạm vi."
'''
    with MayChuGia(core, {app.ma: khoa_demo}) as may:
        dong = json.dumps({"core_url": may.url, "khoa": khoa_demo, "instance": instance}) + "\n"
        tien_trinh = subprocess.run(
            [sys.executable, "-B", "-c", ma_chay], cwd=app.thu_muc_goi,
            input=dong, env=moi_truong, capture_output=True, text=True, encoding="utf-8", timeout=20,
        )
        assert tien_trinh.returncode == 0, tien_trinh.stderr
        assert khoa_demo not in tien_trinh.stdout + tien_trinh.stderr
        loi_goi = list(may.cac_loi_goi)
    kiem_ket_qua_demo([core.xem(ma) for ma in cac_ma])
    assert local.so_luot_hoi == 3
    assert all(goi["ma_engine"] == app.ma and goi["instance"] == instance and goi["co_bearer"]
               for goi in loi_goi)
    assert loi_goi[0]["duong"] == f"/api/v1/engine/{app.ma}/san-sang"
    for ma in cac_ma:
        duong = f"/api/v1/engine/viec/{ma}/"
        assert any(goi["phuong_thuc"] == "GET" and goi["duong"] == duong + "dau-vao"
                   for goi in loi_goi)
        ghi = [goi for goi in loi_goi if goi["duong"] in {duong + "ket-qua", duong + "ket-thuc"}]
        assert [(goi["phuong_thuc"], goi["duong"]) for goi in ghi] == [
            ("PUT", duong + "ket-qua"), ("POST", duong + "ket-thuc"),
        ]
        assert all(goi["idempotency_key"] for goi in ghi)
