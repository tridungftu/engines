"""Đã kiểm bằng Core giả (CoreGia); giữ các kiểm độc lập của AI-0."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoi_ai.chay import app

GOC = Path(__file__).resolve().parents[2]
GOI = GOC / "e_hoi_ai" / "goi" / "e_hoi_ai"


def test_doc_phieu_va_khai_bao_dung_hop_dong():
    engine = Engine.tu_khai_bao(GOI / "engine.json")
    assert engine.ma == "e_hoi_ai"
    assert engine.cac_nang_luc == ("ai.hoi_tai_lieu@1", "ai.hoi_theo_yeu_cau@1")
    tai_lieu, yeu_cau = engine.phieu["nang_luc"]
    assert tai_lieu["nhan"] == ["van_ban", "van_ban_tai_lieu"]
    assert tai_lieu["tra"] == "truong"
    assert {v["ma"]: v["kieu"] for v in tai_lieu["truong_ra"]} == {
        "tra_loi": "van_ban", "co_can_cu": "co_khong", "trich_dan": "van_ban", "model": "van_ban"}
    assert yeu_cau["nhan"] == ["yeu_cau_ai"]
    assert yeu_cau["tra"] == "tra_loi_ai"
    assert "truong_ra" not in yeu_cau
    assert engine.phieu["loai_du_lieu_rieng"] == [
        {"ma": "van_ban_tai_lieu", "ten": "Văn bản tài liệu có vị trí"},
        {"ma": "yeu_cau_ai", "ten": "Yêu cầu hỏi AI"},
        {"ma": "tra_loi_ai", "ten": "Trả lời AI có trích dẫn"}]
    tham_so = {v["ma"]: v for v in tai_lieu["tham_so"]}
    assert set(tham_so) == {"ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien"}
    assert all(tham_so[k]["bat_buoc"] for k in ("ma_prompt", "phien_ban_prompt", "prompt"))
    assert not tham_so["model_uu_tien"]["bat_buoc"]
    assert all("mac_dinh" not in tham_so[k] for k in ("ma_prompt", "phien_ban_prompt"))
    # Sentinel rỗng giúp engine trả THIEU_PROMPT thay lỗi kiểm tham số chung của SDK.
    assert tham_so["prompt"]["mac_dinh"] == ""
    assert all(nl["gioi_han"] == {"ky_tu_toi_da": 500000, "thoi_han_giay": 600}
               and nl["huy_duoc"] for nl in engine.phieu["nang_luc"])
    assert engine.phieu["tai_nguyen"]["so_viec_dong_thoi"] == 1
    assert engine.phieu["bi_mat"] == []
    assert len(engine.phieu["chay_thu_demo"]) == 1
    assert engine.phieu["chay_thu_demo"][0]["nang_luc"] == "ai.hoi_tai_lieu@1"


@pytest.mark.parametrize("ma", ["van_ban_tai_lieu", "yeu_cau_ai", "tra_loi_ai"])
def test_schema_trong_goi_trung_bam_nguon_chung(ma):
    nguon = (GOC / "_chung" / "contract" / f"{ma}.schema.json").read_bytes()
    ban_sao = (GOI / "contract" / f"{ma}.schema.json").read_bytes()
    assert sha256(nguon).digest() == sha256(ban_sao).digest()
    schema = json.loads(ban_sao)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["loai"]["const"] == ma
    assert set(schema["required"]) == {"loai", ma}
    assert schema["properties"][ma]["properties"]["phien_ban"]["const"] == 1


@pytest.mark.parametrize("loai", ["van_ban", "van_ban_tai_lieu", "yeu_cau_ai"])
def test_core_gia_thieu_cau_hinh_hoac_nang_luc_chua_lam_khong_co_ket_qua(loai, monkeypatch, tmp_path):
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "chua-co-demo.json"))
    if loai == "van_ban":
        du_lieu = "Công ty DEMO Ánh Dương, hợp đồng DEMO-001."
    elif loai == "van_ban_tai_lieu":
        du_lieu = {"phien_ban": 1, "van_ban": "Tài liệu DEMO", "trang": [],
                   "nguon_doc": "docx", "ly_do_chuyen_nguon": None, "so_trang": 0,
                   "phien_ban_engine": "e_ocr DEMO", "bam_dau_vao": "sha256:" + "0" * 64, "canh_bao": []}
    else:
        du_lieu = {"phien_ban": 1, "ma_prompt": "demo.hoi", "phien_ban_prompt": "1",
                   "prompt": "Câu hỏi DEMO", "tai_lieu": "Tài liệu DEMO", "khuon_tra_loi": None,
                   "bat_buoc_trich_dan": True, "model_uu_tien": None, "chuyen_tiep": {}}
    nang_luc = "ai.hoi_theo_yeu_cau@1" if loai == "yeu_cau_ai" else "ai.hoi_tai_lieu@1"
    ket_qua = CoreGia().chay_thu(app, nang_luc, {"loai": loai, loai: du_lieu},
                               {"ma_prompt": "demo.hoi", "phien_ban_prompt": "1", "prompt": "Câu hỏi DEMO"}
                               if loai != "yeu_cau_ai" else {})
    assert ket_qua["trang_thai"] == "LOI"
    assert ket_qua["loi"]["ma"] == ("CHUA_LAM" if loai == "yeu_cau_ai" else "CHUA_CAU_HINH")
    assert ket_qua["ket_qua"] is None
    assert not ket_qua["loi"]["thu_lai_duoc"]


def test_goi_chay_doc_lap_ngoai_repo_khi_thieu_cau_hinh(tmp_path):
    ban_sao = tmp_path / "goi-demo"
    shutil.copytree(GOI, ban_sao)
    tep_cau_hinh = tmp_path / "cau_hinh_DEMO.json"
    tep_cau_hinh.write_text(json.dumps({"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60}}), encoding="utf-8")
    thu_muc_sdk = Path(kho_tri_thuc_sdk.__file__).resolve().parent.parent
    ma_kiem = (
        "import os, sys; sys.path.insert(0, " + repr(str(thu_muc_sdk)) + "); "
        "sys.path.insert(0, " + repr(str(ban_sao)) + "); "
        "os.environ['KTT_ENGINE_CAU_HINH'] = " + repr(str(tmp_path / "chua-co-demo.json")) + "; "
        "from e_hoi_ai.chay import app; from e_hoi_ai.cau_hinh_may import doc_cau_hinh; "
        "assert app.ma == 'e_hoi_ai'; assert doc_cau_hinh() is None; "
        "os.environ['KTT_ENGINE_CAU_HINH'] = " + repr(str(tep_cau_hinh)) + "; "
        "assert doc_cau_hinh()['local_ai']['timeout_giay'] == 60"
    )
    ket_qua = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", ma_kiem], cwd=tmp_path,
                             capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert ket_qua.returncode == 0, ket_qua.stderr
    assert not list(ban_sao.rglob("__pycache__"))
