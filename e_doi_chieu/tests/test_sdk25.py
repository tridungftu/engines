"""SDK25: hợp đồng đóng gói và cài offline; chỉ dữ liệu DEMO."""
from hashlib import sha256
from pathlib import Path
import runpy
import shutil

import pytest

GOI = Path(__file__).resolve().parents[1] / "goi/e_doi_chieu"
TOOL = runpy.run_path(str(GOI.parents[1] / "cong-cu/kiem_may_sach.py"))


def test_lock_va_wheels_goi_core_tu_cai():
    rows = TOOL["kiem_goi_thu_vien"](GOI)
    assert rows and all(r["hash"] for r in rows)


@pytest.mark.parametrize("line", [
    "Pillow==12.3.0",  # Thiếu hash.
    "Pillow==12.3.0 --hash=sha256:{hash} # DEMO",
    "Pillow==12.3.0 {slash}\n --hash=sha256:{hash}",
    "Pillow>=12.3.0 --hash=sha256:{hash}",
    "Pillow==12.3.0; python_version >= '3' --hash=sha256:{hash}",
    "--find-links DEMO",
    "kho_tri_thuc_sdk==2.5.0 --hash=sha256:{hash}",
    "Kho.Tri-Thuc-demo==1.0.0 --hash=sha256:{hash}",
    "# coding: ascii\nPillow==12.3.0 --hash=sha256:{hash}",
    "Pillow==12.3.0 --hash=sha256:{hash}\npillow==12.3.0 --hash=sha256:{hash}",
    "\ufeffPillow==12.3.0 --hash=sha256:{hash}",
    "# chú thích không ASCII",
])
def test_lock_sai_bi_tu_choi(tmp_path, line):
    lock = tmp_path / "requirements.lock"
    lock.write_text(line.format(hash="0" * 64, slash=chr(92)), encoding="utf-8")
    with pytest.raises((ValueError, UnicodeError)):
        TOOL["doc_lock"](lock)


@pytest.mark.parametrize("sai", ["thieu", "thua", "bam", "sdist", "thu_muc", "phien_ban", "nen_tang"])
def test_goi_sai_wheel_bi_tu_choi(tmp_path, sai):
    shutil.copyfile(GOI / "requirements.lock", tmp_path / "requirements.lock")
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    source, = (GOI / "wheels").glob("*.whl")
    if sai != "thieu":
        shutil.copyfile(source, wheels / source.name)
    if sai == "thua":
        shutil.copyfile(source, wheels / source.name.replace("pillow-", "DEMO-"))
    elif sai == "bam":
        (wheels / source.name).write_bytes(b"DEMO wheel sai bam")
    elif sai == "sdist":
        (wheels / "DEMO.tar.gz").write_bytes(b"DEMO")
    elif sai == "thu_muc":
        (wheels / "DEMO").mkdir()
    elif sai in {"phien_ban", "nen_tang"}:
        # Giữ bytes/hash, thay tên: vẫn phải từ chối pin/tag sai.
        old = wheels / source.name
        name = source.name.replace("12.3.0", "0.0.0") if sai == "phien_ban" else source.name.replace("win_amd64", "manylinux_2_28_x86_64")
        old.rename(wheels / name)
    with pytest.raises(ValueError):
        TOOL["kiem_goi_thu_vien"](tmp_path)


def test_may_sach_mac_dinh_lay_wheels_cua_goi():
    selected, errors = TOOL["kiem_truoc"](GOI / "wheels", chi_runtime=True)
    import os
    if os.name == "nt":
        assert not errors
        assert selected[1:] == list((GOI / "wheels").glob("*.whl"))
    else:
        # Gói Core Windows; Linux cần kho offline riêng có hash Linux đã cấp.
        assert errors and all("THIEU wheel dung hash/tag:" in e for e in errors)
    sdk = selected[0]
    assert sha256(sdk.read_bytes()).hexdigest() in (sdk.parent / "SHA256SUMS.txt").read_text()


def test_runtime_chi_dung_cua_cong_khai_sdk():
    import ast
    for p in (GOI / "e_doi_chieu").glob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        roots = {"app", "viec", "ngan", "lo"}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                roots.update(a.asname or a.name.split(".")[0] for a in n.names
                             if a.name.startswith("kho_tri_thuc_sdk"))
            elif isinstance(n, ast.ImportFrom) and (n.module or "").startswith("kho_tri_thuc_sdk"):
                assert not any(part.startswith("_") for part in n.module.split(".")), p
                assert all(not a.name.startswith("_") for a in n.names), p
                roots.update(a.asname or a.name for a in n.names)
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr.startswith("_"):
                root = n.value
                while isinstance(root, ast.Attribute):
                    root = root.value
                assert not (isinstance(root, ast.Name) and root.id in roots), (p, n.lineno)
