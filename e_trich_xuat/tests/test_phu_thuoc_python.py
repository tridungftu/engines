"""Tự kiểm lock và wheel thật được Core cài, không tải mạng."""

import hashlib
from pathlib import Path
import zipfile

import pytest

from phu_thuoc_python import doc_lock, kiem_goi_phu_thuoc


GOI = Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"


def test_lock_va_wheels_cua_goi_khop_day_du():
    assert set(kiem_goi_phu_thuoc(GOI)) == set(doc_lock(GOI / "requirements.lock"))


def test_lock_chung_du_wheel_va_dung_so_bam_cho_hai_nen():
    ds = doc_lock(GOI / "requirements.lock")
    windows = kiem_goi_phu_thuoc(GOI)
    linux = kiem_goi_phu_thuoc(GOI, "linux")
    bien_dich = {"cryptography", "cffi", "rpds-py"}
    assert set(linux) == set(windows) == set(ds)
    assert {ten for ten, ghim in ds.items() if len(ghim["bam"]) == 2} == bien_dich
    for ten, ghim in ds.items():
        assert windows[ten].parent == GOI / "wheels"
        assert linux[ten].parent == (GOI.parents[1] / "wheels-linux" if ten in bien_dich else GOI / "wheels")
        assert {hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (windows[ten], linux[ten])} == ghim["bam"]


@pytest.mark.parametrize("tag,hop_le", [
    ("cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64", True),
    ("cp311-abi3-manylinux_2_34_x86_64", True),
    ("cp313-cp313-manylinux_2_40_x86_64", False),
    ("cp313-cp313-musllinux_1_2_x86_64", False),
    ("cp313-cp313-manylinux_2_34_aarch64", False),
    ("cp314-cp314-manylinux_2_34_x86_64", False),
    ("cp313-cp313-win_amd64", False),
])
def test_kho_linux_kiem_nen_va_abi_khi_lock_co_hai_bam(tmp_path, tag, hop_le):
    goi = tmp_path / "goi/e_demo"
    (goi / "wheels").mkdir(parents=True)
    kho = tmp_path / "wheels-linux"
    kho.mkdir()
    tep = kho / f"demo-1.0-{tag}.whl"
    with zipfile.ZipFile(tep, "w") as z:
        z.writestr("demo-1.0.dist-info/METADATA", "Metadata-Version: 2.1\nName: demo\nVersion: 1.0\n")
    bam = hashlib.sha256(tep.read_bytes()).hexdigest()
    (goi / "requirements.lock").write_text(
        f"demo==1.0 --hash=sha256:{'0' * 64} --hash=sha256:{bam}\n", encoding="ascii")
    if hop_le:
        assert kiem_goi_phu_thuoc(goi, "linux") == {"demo": tep}
    else:
        with pytest.raises(ValueError):
            kiem_goi_phu_thuoc(goi, "linux")


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
