"""Tự kiểm lock và wheel thật được Core cài, không tải mạng."""

import hashlib
from pathlib import Path
import zipfile

import pytest

from phu_thuoc_python import doc_lock, kiem_goi_phu_thuoc


GOI = Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"


def test_lock_va_wheels_cua_goi_khop_day_du():
    assert set(kiem_goi_phu_thuoc(GOI)) == set(doc_lock(GOI / "requirements.lock"))


@pytest.mark.parametrize("dong", [
    b"# Khong ASCII: \xc4\x90", b"\xef\xbb\xbf# BOM", b"# coding: ascii",
    b"demo==1.0 \\", b"demo==1.0 # giua dong", b"demo==1.0",
    b"demo==1.0 --hash=sha256:" + b"A" * 64,
    b"demo==1.0 --hash=sha256:" + b"0" * 64 + b" --no-deps",
    b"demo==1.0; python_version > '3' --hash=sha256:" + b"0" * 64,
    b"kho.tri_thuc_sdk==2.5.0 --hash=sha256:" + b"0" * 64,
    (b"demo==1.0 --hash=sha256:" + b"0" * 64 + b"\n") * 2,
])
def test_lock_tu_choi_khuon_cu_va_dong_khong_an_toan(tmp_path, dong):
    tep = tmp_path / "requirements.lock"
    tep.write_bytes(dong)
    with pytest.raises(ValueError):
        doc_lock(tep)


@pytest.mark.parametrize("loai", ["dung", "sai_bam", "thieu", "lap", "thua", "sdist", "thu_muc"])
def test_kho_wheel_khong_duoc_thua_thieu_hoac_sai_bam(tmp_path, loai):
    kho = tmp_path / "wheels"
    kho.mkdir()
    tep = kho / "demo-1.0-py3-none-any.whl"
    with zipfile.ZipFile(tep, "w") as z:
        z.writestr("demo-1.0.dist-info/METADATA", "Metadata-Version: 2.1\nName: demo\nVersion: 1.0\n")
    bam = hashlib.sha256(tep.read_bytes()).hexdigest()
    (tmp_path / "requirements.lock").write_text(
        f"demo==1.0 --hash=sha256:{bam}\n", encoding="ascii")
    if loai == "sai_bam":
        tep.write_bytes(b"DEMO sai bam")
    elif loai == "thieu":
        tep.rename(tmp_path / "DEMO-wheel-luu.whl")
    elif loai == "lap":
        (kho / "demo-1.0-1-py3-none-any.whl").write_bytes(tep.read_bytes())
    elif loai == "thua":
        (kho / "khac-1.0-py3-none-any.whl").write_bytes(tep.read_bytes())
    elif loai == "sdist":
        (kho / "demo-1.0.tar.gz").write_bytes(b"DEMO")
    elif loai == "thu_muc":
        (kho / "DEMO").mkdir()
    if loai == "dung":
        assert len(kiem_goi_phu_thuoc(tmp_path)) == 1
    else:
        with pytest.raises(ValueError):
            kiem_goi_phu_thuoc(tmp_path)
