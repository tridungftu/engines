"""SDK25: tự kiểm gói và các ca từ chối lock/wheel sai; không tải mạng."""

from hashlib import sha256
import ast
import re
from zipfile import ZipFile

import pytest

from kiem_doc_lap import kiem_doc_lap
from kiem_thu_vien import GOI, doc_lock, kiem_goi_thu_vien


def test_lock_va_wheels_cua_goi():
    assert len(kiem_goi_thu_vien()) == 8


def test_bam_nguon_du_tep_khop_quy_uoc_lf():
    nguon = (GOI / "NGUON.md").read_text(encoding="utf-8")
    bang = re.findall(r"^([0-9a-f]{64})  (.+)$", nguon, re.M)
    that = {p.relative_to(GOI).as_posix(): p for p in GOI.rglob("*")
            if p.is_file() and p.relative_to(GOI).as_posix() not in {"NGUON.md", "sql/kiem_ke.json"}}
    assert len(bang) == len(that) and {ten for _, ten in bang} == set(that)
    for bam, ten in bang:
        tep = that[ten]
        raw = tep.read_bytes()
        if tep.suffix in {".py", ".md", ".json", ".js", ".sql", ".lock"} or tep.name == ".gitattributes":
            raw = raw.replace(b"\r\n", b"\n")
        assert sha256(raw).hexdigest() == bam, ten


def test_runtime_chi_dung_cua_sdk_cong_khai():
    for tep in (GOI / "e_ocr").rglob("*.py"):
        cay = ast.parse(tep.read_text(encoding="utf-8-sig"))
        sdk = {"app", "viec", "ung_dung", "ngan"}
        for nut in ast.walk(cay):
            if isinstance(nut, ast.ImportFrom) and (nut.module or "").startswith("kho_tri_thuc_sdk"):
                assert not any(a.name.startswith("_") for a in nut.names), tep
                sdk.update(a.asname or a.name for a in nut.names)
            elif isinstance(nut, ast.Import):
                sdk.update(a.asname or a.name for a in nut.names if a.name.startswith("kho_tri_thuc_sdk"))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.Attribute) and isinstance(nut.value, ast.Name) and nut.value.id in sdk:
                assert not nut.attr.startswith("_"), (tep, nut.lineno)
            if isinstance(nut, ast.ClassDef) and any(isinstance(b, ast.Name) and b.id in sdk for b in nut.bases):
                assert not any(isinstance(h, (ast.FunctionDef, ast.AsyncFunctionDef)) and h.name.startswith("_")
                               for h in nut.body), tep


@pytest.mark.parametrize("dong", [
    b"Pillow>=12.3.0 --hash=sha256:" + b"a" * 64,
    b"Pillow==12.3.0 \\\n --hash=sha256:" + b"a" * 64,
    b"Pillow==12.3.0 --hash=sha256:" + b"a" * 64 + b" # DEMO",
    b"Pillow==12.3.0", b"\xef\xbb\xbf# DEMO", "# Chữ DEMO".encode(),
    b"# coding: ascii\nPillow==12.3.0 --hash=sha256:" + b"a" * 64,
    *[(ten + "==2.5.0 --hash=sha256:" + "a" * 64).encode()
      for ten in ["kho_tri_thuc_sdk", "kho-tri-thuc-sdk", "Kho.Tri.Thuc.sdk"]],
    ("Pillow==12.3.0 --hash=sha256:" + "a" * 64 + "\nPILLOW==12.3.0 --hash=sha256:" + "a" * 64).encode(),
])
def test_lock_sai_bi_tu_choi(tmp_path, dong):
    lock = tmp_path / "requirements.lock"
    lock.write_bytes(dong)
    with pytest.raises(ValueError):
        doc_lock(lock)


@pytest.mark.parametrize("thu_vien", ["Pillow", "PILLOW", "pdfminer.six", "pdfminer-six", "pypdfium2", "pdfplumber"])
def test_kiem_doc_lap_doc_ten_lock_moi(tmp_path, thu_vien):
    module = {"pillow": "PIL", "pdfminer.six": "pdfminer", "pdfminer-six": "pdfminer"}.get(thu_vien.lower(), thu_vien)
    (tmp_path / "requirements.lock").write_text(f"{thu_vien}==1.0 --hash=sha256:{'a' * 64}\n", encoding="ascii")
    (tmp_path / "DEMO.py").write_text(f"import {module}\n", encoding="ascii")
    assert kiem_doc_lap(tmp_path) == []


@pytest.fixture
def goi_demo(tmp_path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    wheel = wheels / "demo-1.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as zip:
        zip.writestr("demo-1.0.dist-info/METADATA", "Name: demo\nVersion: 1.0\n")
    (tmp_path / "requirements.lock").write_text(f"demo==1.0 --hash=sha256:{sha256(wheel.read_bytes()).hexdigest()}\n", encoding="ascii")
    assert kiem_goi_thu_vien(tmp_path)
    return tmp_path, wheel


@pytest.mark.parametrize("ca", ["bam", "thieu", "lap", "thua", "sdist", "thu_muc", "ban", "linux", "cp312"])
def test_wheel_sai_bi_tu_choi(goi_demo, ca):
    goi, wheel = goi_demo
    if ca == "bam":
        wheel.write_bytes(b"DEMO bi thay doi")
    elif ca == "thieu":
        (goi / "requirements.lock").write_text("thieu==1.0 --hash=sha256:" + "a" * 64, encoding="ascii")
    elif ca == "thu_muc":
        (goi / "wheels" / "con").mkdir()
    elif ca in {"lap", "thua", "sdist"}:
        ten = {"lap": "demo-1.0-py3-none-win_amd64.whl", "thua": "thua-1.0-py3-none-any.whl", "sdist": "demo-1.0.tar.gz"}[ca]
        (goi / "wheels" / ten).write_bytes(wheel.read_bytes())
    else:
        ten = {"ban": "demo-2.0-py3-none-any.whl", "linux": "demo-1.0-py3-none-manylinux_x86_64.whl", "cp312": "demo-1.0-cp312-cp312-win_amd64.whl"}[ca]
        wheel.rename(wheel.with_name(ten))
    with pytest.raises(ValueError):
        kiem_goi_thu_vien(goi)
