"""Kiểm cổng độc lập bằng gói DEMO tạm, chạy được trên Windows và Linux."""
from pathlib import Path
import stat
import subprocess
import sys
from types import SimpleNamespace

import pytest

import kiem_doc_lap as kiem


@pytest.mark.parametrize("tep, noi_dung", [
    ("ma.py", b"from kho_tri_thuc.loi import x"),
    ("contract/demo.json", b'{"ma": "kho_tri_thuc.demo"}'),
    ("cache/ma.pyc", b"DEMO"),
    ("__pycache__/ma.txt", b"DEMO"),
])
def test_tu_choi_tung_loai_vi_pham(tmp_path, tep, noi_dung):
    tep_demo = tmp_path / tep
    tep_demo.parent.mkdir(parents=True, exist_ok=True)
    tep_demo.write_bytes(noi_dung)
    assert kiem.kiem_tra(tmp_path)


@pytest.mark.parametrize("che_do, thuoc_tinh", [(stat.S_IFLNK, 0), (stat.S_IFDIR, 0x400)])
def test_nhan_dien_symlink_linux_va_junction_windows(che_do, thuoc_tinh):
    assert kiem._la_lien_ket(SimpleNamespace(st_mode=che_do, st_file_attributes=thuoc_tinh))


def test_khong_doc_hoac_di_theo_lien_ket(tmp_path, monkeypatch):
    (tmp_path / "lien-ket-demo").mkdir()
    (tmp_path / "lien-ket-demo" / "tep-demo.txt").write_text("DEMO", encoding="utf-8")
    lan_kiem = 0
    def gia_lien_ket(thong_tin):
        nonlocal lan_kiem
        lan_kiem += 1
        return lan_kiem == 2  # Lần 1 là gốc, lần 2 là mục liên kết cần từ chối.
    monkeypatch.setattr(kiem, "_la_lien_ket", gia_lien_ket)
    loi = kiem.kiem_tra(tmp_path)
    assert len(loi) == 1 and "liên kết" in loi[0]
    assert lan_kiem == 2


def test_ma_thoat_cli_dat_va_loi(tmp_path):
    tep = tmp_path / "ma_demo.py"
    tep.write_text("from kho_tri_thuc_sdk.engine import Engine", encoding="utf-8")
    lenh = [sys.executable, "-X", "utf8", "-B", str(Path(kiem.__file__)), str(tmp_path)]
    ket_qua = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert ket_qua.returncode == 0
    assert "[ĐẠT]" in ket_qua.stdout
    tep.write_text("import kho_tri_thuc.loi", encoding="utf-8")
    ket_qua = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert ket_qua.returncode == 1
    assert "[LỖI]" in ket_qua.stdout


def test_thu_muc_khong_ton_tai_la_loi(tmp_path):
    assert kiem.main([str(tmp_path / "chua-co-DEMO")]) == 1


def test_goi_hien_tai_sach():
    assert kiem.kiem_tra(Path(__file__).resolve().parents[1] / "goi") == []
