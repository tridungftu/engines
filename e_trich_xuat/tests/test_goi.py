"""Kiểm phiếu thật, SHA nguồn chung, quét độc lập và chạy UI bằng Node."""

import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from kho_tri_thuc_sdk.engine import kiem_phieu

from kiem_doc_lap import kiem_tra


GOC = Path(__file__).resolve().parents[2]
GOI = GOC / "e_trich_xuat/goi/e_trich_xuat"


def test_phieu_20_va_khai_21_tach_rieng():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert kiem_phieu(phieu, GOI) == []
    assert len(phieu["nang_luc"]) == 1
    assert phieu["nang_luc"][0]["ma"] == "trich.doc_docx@1"
    for k in ["ngan_du_lieu", "cau_hinh", "giao_dien_quan_tri"]:
        assert k not in phieu
    khai = json.loads((GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
    assert set(khai) == {"ngan_du_lieu", "cau_hinh", "giao_dien_quan_tri"}
    assert khai["ngan_du_lieu"][0]["pham_vi"] == "engine"
    assert "giu_toi_da_ngay" not in khai["ngan_du_lieu"][0]


def test_schema_chung_khop_tung_byte_va_sha():
    ten = "van_ban_tai_lieu.schema.json"
    a = (GOC / "_chung/contract" / ten).read_bytes()
    b = (GOI / "contract" / ten).read_bytes()
    assert a == b and hashlib.sha256(a).digest() == hashlib.sha256(b).digest()


@pytest.mark.parametrize("ten", ["ngan.py", "cau_hinh.py"])
def test_sha_mau_ngan_0(ten):
    mau = GOC / "_chung/mau-ma" / ten
    a = mau.read_bytes().replace(b"\r\n", b"\n")
    b = (GOI / "e_trich_xuat" / ten).read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(a).digest() == hashlib.sha256(b).digest()


def test_goi_doc_lap_va_import_chi_sdk_thu_vien_chuan():
    assert kiem_tra(GOI.parent) == []
    for p in (GOI / "e_trich_xuat").glob("*.py"):
        cay = ast.parse(p.read_text(encoding="utf-8"))
        for n in ast.walk(cay):
            if isinstance(n, ast.Import):
                ten = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and not n.level:
                ten = [n.module.split(".")[0]]
            else:
                continue
            assert all(t in sys.stdlib_module_names or t == "kho_tri_thuc_sdk" for t in ten)


def test_quet_phat_hien_core_kenh_cu_bytecode_va_symlink(tmp_path):
    for du_lieu in [b"from kho_tri_thuc.loi import X", b"SDKEngine", b"Bootstrap", b"kenh_engine"]:
        (tmp_path / "DEMO.py").write_bytes(du_lieu)
        assert kiem_tra(tmp_path)
    (tmp_path / "DEMO.py").write_text("# DEMO", encoding="utf-8")
    (tmp_path / "DEMO.pyc").write_bytes(b"DEMO")
    assert kiem_tra(tmp_path)
    # Không cần tạo symlink Windows đòi quyền; kiểm cả reparse point bằng metadata.
    from kiem_doc_lap import _lien_ket
    from types import SimpleNamespace
    import stat
    assert _lien_ket(SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0))
    assert _lien_ket(SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400))


def test_ui_node():
    node = shutil.which("node")
    assert node, "Cần Node để kiểm màn bằng KttCore giả."
    kq = subprocess.run([node, "--test", str(Path(__file__).parent / "ui/cau_hinh.test.mjs")],
                        capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert kq.returncode == 0, kq.stdout + kq.stderr
