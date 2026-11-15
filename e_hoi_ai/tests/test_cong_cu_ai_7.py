"""Kiểm công cụ AI-7 bằng Core giả và Local HTTP giả, không gọi máy thật."""
import importlib.util
from pathlib import Path

import chay_demo_voi_local_gia as demo
from test_hoi_tai_lieu import khong_mang_ngoai_va_khong_cloud, local

spec = importlib.util.spec_from_file_location("cong_cu_ai_7", Path(__file__).resolve().parents[1] / "cong-cu" / "thu_local_ai_that.py")
cong_cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cong_cu)


def test_thu_ba_ca_manifest_qua_local_gia(local):
    demo.chuan_bi_local_demo(local)
    bao_cao = cong_cu.thuc_hien(local.url)
    rows = bao_cao["ket_qua"]
    assert [r["ca_demo"] for r in rows] == [vd["ten"] for vd in cong_cu.doc_demo()]
    assert len(rows) == 3 and all(r["dung"] for r in rows)
    assert [r["co_trich_dan"] for r in rows] == [True, False, True]
    assert bao_cao["local_tat_gia_lap"]["khong_san_sang"]
    assert bao_cao["so_luot_cloud"] == 0
