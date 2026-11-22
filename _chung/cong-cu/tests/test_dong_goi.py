"""Kiểm đóng gói bằng kho git DEMO biệt lập, không commit vào repo làm việc."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import zipfile

import pytest


DUONG_DAN = Path(__file__).resolve().parents[1] / "dong_goi.py"
spec = importlib.util.spec_from_file_location("dong_goi", DUONG_DAN)
dg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dg)
MA = "e_hoi_ai"


def lenh_git(repo, *args, dau_vao=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="DEMO", GIT_AUTHOR_EMAIL="demo@example.invalid",
               GIT_COMMITTER_NAME="DEMO", GIT_COMMITTER_EMAIL="demo@example.invalid")
    return subprocess.check_output(["git", "-C", str(repo), *args], input=dau_vao, env=env)


def tao_moc(repo):
    # Tạo object git trong repo tạm của test; không dùng git commit/push.
    lenh_git(repo, "-c", "core.autocrlf=false", "add", ".")
    cay = lenh_git(repo, "write-tree").decode().strip()
    moc = lenh_git(repo, "commit-tree", cay, dau_vao=b"DEMO\n").decode().strip()
    lenh_git(repo, "update-ref", "HEAD", moc)
    return moc


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    lenh_git(r, "init", "-q")
    p = r / MA / "goi" / MA
    (p / MA).mkdir(parents=True)
    phieu = {"ma": MA, "ten": "Hỏi AI DEMO", "phien_ban": "1.0.0",
             "tuong_thich": {"sdk": ">=2.2.0 <3.0.0"}, "nang_luc": [{"ma": "demo.hoi@1"}]}
    (p / "engine.json").write_text(json.dumps(phieu), encoding="utf-8")
    (p / "README.md").write_bytes("DEMO — bytes LF\n".encode())
    (p / "NGUON.md").write_bytes(b"DEMO\n")
    (p / "requirements.lock").write_bytes(b"# DEMO\n")
    (p / MA / "chay.py").write_bytes(b"# DEMO\n")
    sdk = r / dg.THU_MUC_SDK
    sdk.mkdir(parents=True)
    (sdk / dg.WHEEL).write_bytes(b"DEMO wheel\r\n")
    (sdk / "SHA256SUMS.txt").write_bytes(
        f"{dg.sha256(b'DEMO wheel' + bytes([13, 10]))}  {dg.WHEEL}\n".encode())
    sdk25 = r / "docs/goi-gui-engine/sdk-2.5.0"
    sdk25.mkdir(parents=True)
    (sdk25 / W25).write_bytes(b"DEMO wheel 2.5")
    (sdk25 / "SHA256SUMS.txt").write_bytes(f"{dg.sha256(b'DEMO wheel 2.5')}  {W25}\n".encode())
    tao_moc(r)
    return r


W25 = "kho_tri_thuc_sdk-2.5.0-py3-none-any.whl"


def duong_goi(repo):
    return repo / MA / "goi" / MA


def xuat(repo, thu_muc, **kwargs):
    return dg.dong_goi(repo, [MA], thu_muc, "DEMO", **kwargs)


def them_sql(repo):
    p = duong_goi(repo)
    (p / "sql").mkdir()
    (p / "sql/001_tao_ngan.sql").write_bytes(b"-- DEMO\n")
    m = json.loads((p / "engine.json").read_bytes())
    m["ngan_du_lieu"] = [{"bang": "demo"}]
    m["du_lieu"] = {"goi_migration": {"thu_muc": "sql", "tep_kiem_ke": "sql/kiem_ke.json"}}
    (p / "engine.json").write_text(json.dumps(m), encoding="utf-8")
    tep = [{"duong_dan": f.relative_to(p).as_posix(), "bytes": len(f.read_bytes()),
            "sha256": dg.sha256(f.read_bytes())} for f in p.rglob("*") if f.is_file()]
    (p / "sql/kiem_ke.json").write_text(json.dumps({"phien_ban": "1.0.0", "tep": tep}), encoding="utf-8")
    tao_moc(repo)


def test_zip_tat_dinh_va_metadata(repo, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    ds = xuat(repo, a)
    xuat(repo, b)
    assert {p.name: p.read_bytes() for p in a.iterdir()} == {p.name: p.read_bytes() for p in b.iterdir()}
    with zipfile.ZipFile(a / ds[0]["tep_zip"]) as z:
        assert z.namelist() == sorted(z.namelist())
        assert all(n.startswith(MA + "/") for n in z.namelist())
        for info in z.infolist():
            assert info.date_time == dg.THOI_GIAN
            assert info.create_system == 3
            assert stat.S_IMODE(info.external_attr >> 16) == 0o644
            assert info.compress_type == zipfile.ZIP_STORED
    for dong in (a / "SHA256SUMS.txt").read_text().splitlines():
        bam, ten = dong.split("  ")
        assert hashlib.sha256((a / ten).read_bytes()).hexdigest() == bam
    bang = json.loads((a / "DANH-SACH-GOI.json").read_bytes())
    assert bang["goi"] == ds
    assert ds[0]["commit_git"] == lenh_git(repo, "rev-parse", "HEAD").decode().strip()


@pytest.mark.parametrize("ten", [
    ".venv/a.py", "__pycache__/a.py", ".pytest-tmp/a.json", ".pytest-tmp-1/a.json",
    "LUU-TRU/a.py", "e_hoi_ai/LUU-TRU/a.py", "e_hoi_ai/a.pyc", ".env",
    "demo/.env.demo", "demo/BI-MAT.json", "demo/Secret.txt", "demo/myToken.json",
    "demo/password.txt", "tep-la.exe", "demo/a.exe",
])
def test_tu_choi_tep_cam(repo, tmp_path, ten):
    p = duong_goi(repo) / ten
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"DEMO")
    tao_moc(repo)
    ra = tmp_path / "ra"
    with pytest.raises(dg.LoiDongGoi):
        xuat(repo, ra)
    assert not ra.exists()


@pytest.mark.parametrize("kieu", ["sha", "bytes", "thieu", "thua", "lap", "phien_ban"])
def test_kiem_ke_sai_dung_truoc_khi_ghi(repo, tmp_path, kieu):
    them_sql(repo)
    p = duong_goi(repo) / "sql/kiem_ke.json"
    kk = json.loads(p.read_bytes())
    if kieu == "sha": kk["tep"][0]["sha256"] = "0" * 64
    elif kieu == "bytes": kk["tep"][0]["bytes"] += 1
    elif kieu == "thieu": kk["tep"].pop()
    elif kieu == "thua": kk["tep"].append({"duong_dan": "khong_co"})
    elif kieu == "lap": kk["tep"].append(kk["tep"][0])
    else: kk["phien_ban"] = "9.9.9"
    p.write_text(json.dumps(kk), encoding="utf-8")
    tao_moc(repo)
    with pytest.raises(dg.LoiDongGoi, match="Kiểm kê"):
        xuat(repo, tmp_path / "ra")
    assert not (tmp_path / "ra").exists()


def test_kiem_ke_dung_va_bytes_git_khong_worktree(repo, tmp_path):
    them_sql(repo)
    p = duong_goi(repo)
    chuan = (p / "README.md").read_bytes()
    (p / "README.md").write_bytes(b"DEMO dirty CRLF\r\n")
    (p / "sql/kiem_ke.json").write_bytes(b"JSON hong trong worktree")
    # Tệp chưa ghi trong git không được đọc hoặc lọt vào gói.
    (p / "demo").mkdir()
    (p / "demo/ngoai_git.txt").write_bytes(b"DEMO")
    (repo / dg.THU_MUC_SDK / dg.WHEEL).write_bytes(b"DEMO dirty wheel")
    ds = xuat(repo, tmp_path / "ra")
    assert ds[0]["co_ngan"] and ds[0]["co_sql"]
    with zipfile.ZipFile(tmp_path / "ra" / ds[0]["tep_zip"]) as z:
        assert z.read(f"{MA}/README.md") == chuan
        assert not any("ngoai_git" in n for n in z.namelist())
    assert (tmp_path / "ra" / dg.WHEEL).read_bytes() == b"DEMO wheel\r\n"


def test_chon_ref_cu(repo, tmp_path):
    cu = lenh_git(repo, "rev-parse", "HEAD").decode().strip()
    (duong_goi(repo) / "README.md").write_bytes(b"DEMO ban moi\n")
    tao_moc(repo)
    ds = xuat(repo, tmp_path / "ra", ref=cu)
    assert ds[0]["commit_git"] == cu
    with zipfile.ZipFile(tmp_path / "ra" / ds[0]["tep_zip"]) as z:
        assert z.read(f"{MA}/README.md") == "DEMO — bytes LF\n".encode()


def test_wheel_sai_sha_dung(repo, tmp_path):
    (repo / dg.THU_MUC_SDK / dg.WHEEL).write_bytes(b"DEMO wheel sai")
    tao_moc(repo)
    with pytest.raises(dg.LoiDongGoi, match="Wheel"):
        xuat(repo, tmp_path / "ra")
    assert not (tmp_path / "ra").exists()


def test_thieu_kiem_ke_sql(repo, tmp_path):
    p = duong_goi(repo) / "sql"
    p.mkdir()
    (p / "001_tao_ngan.sql").write_bytes(b"-- DEMO\n")
    tao_moc(repo)
    with pytest.raises(dg.LoiDongGoi, match="Ngăn/SQL"):
        xuat(repo, tmp_path / "ra")


def test_cam_dau_ra_trong_repo_va_khong_ghi_de(repo, tmp_path):
    with pytest.raises(dg.LoiDongGoi, match="ngoài repo"):
        xuat(repo, repo / "ra")
    ra = tmp_path / "ra"
    xuat(repo, ra)
    with pytest.raises(dg.LoiDongGoi, match="mới hoặc rỗng"):
        xuat(repo, ra)


def test_khong_phat_hanh_mot_phan(repo, tmp_path):
    with pytest.raises(dg.LoiDongGoi):
        dg.dong_goi(repo, [MA, "e_ocr"], tmp_path / "ra", "DEMO")
    assert not (tmp_path / "ra").exists()


def test_tu_choi_symlink_git_khong_can_quyen_windows(repo, tmp_path):
    oid = lenh_git(repo, "hash-object", "-w", "--stdin", dau_vao=b"README.md").decode().strip()
    lenh_git(repo, "update-index", "--add", "--cacheinfo", "120000", oid,
             f"{MA}/goi/{MA}/demo/lien_ket.txt")
    cay = lenh_git(repo, "write-tree").decode().strip()
    moc = lenh_git(repo, "commit-tree", cay, dau_vao=b"DEMO symlink\n").decode().strip()
    lenh_git(repo, "update-ref", "HEAD", moc)
    with pytest.raises(dg.LoiDongGoi, match="liên kết"):
        xuat(repo, tmp_path / "ra")


def test_thu_muc_thu_duoc_cho_phep(repo):
    ds = xuat(repo, repo / ".dong-goi-thu")
    assert (repo / ".dong-goi-thu" / ds[0]["tep_zip"]).exists()


def test_ma_lap_khong_tao_hai_goi(repo, tmp_path):
    ds = dg.dong_goi(repo, [MA, MA], tmp_path / "ra", "DEMO")
    assert len(ds) == 1


def test_tham_so_sai_bao_tieng_viet(capsys):
    with pytest.raises(SystemExit) as loi:
        dg.main(["--engine", "khong_co"])
    assert loi.value.code == 2
    assert "Tham số chưa hợp lệ" in capsys.readouterr().err


def them_thu_vien(repo, lock=None, wheel=b"DEMO whl", khai=True):
    p = duong_goi(repo)
    (p / "wheels").mkdir(exist_ok=True)
    (p / "wheels/demo_lib-1.0.0-py3-none-any.whl").write_bytes(wheel)
    if lock is None:
        lock = f"# DEMO\ndemo-lib==1.0.0 --hash=sha256:{dg.sha256(b'DEMO whl')}\n".encode()
    (p / "requirements.lock").write_bytes(lock)
    m = json.loads((p / "engine.json").read_bytes())
    if khai:
        m["phu_thuoc_python"] = {"lock": "requirements.lock", "wheels": "wheels"}
        m["tuong_thich"]["sdk"] = ">=2.4.0 <3.0.0"
    (p / "engine.json").write_text(json.dumps(m), encoding="utf-8")
    tao_moc(repo)


def test_thu_vien_dung_vao_zip(repo, tmp_path):
    them_thu_vien(repo)
    xuat(repo, tmp_path / "ra", sdk="2.5.0")
    with zipfile.ZipFile(tmp_path / "ra" / f"{MA}-1.0.0.zip") as z:
        assert z.read(f"{MA}/wheels/demo_lib-1.0.0-py3-none-any.whl") == b"DEMO whl"
    assert (tmp_path / "ra" / W25).read_bytes() == b"DEMO wheel 2.5"
    assert not (tmp_path / "ra" / dg.WHEEL).exists()
    ds = json.loads((tmp_path / "ra" / "DANH-SACH-GOI.json").read_bytes())
    assert ds["sdk"] == "2.5.0" and ds["wheel_sdk"]["tep"] == W25


def test_goi_kem_thu_vien_khong_di_voi_sdk_22(repo, tmp_path):
    them_thu_vien(repo)
    with pytest.raises(dg.LoiDongGoi, match="--sdk 2.5.0"):
        xuat(repo, tmp_path / "ra")
    assert not (tmp_path / "ra").exists()


def test_sdk_la_bi_tu_choi(repo, tmp_path):
    with pytest.raises(dg.LoiDongGoi):
        xuat(repo, tmp_path / "ra", sdk="9.9.9")


@pytest.mark.parametrize("kieu", ["sai_bam", "thieu_khai", "co_sdk", "noi_dong", "thieu_wheel"])
def test_thu_vien_sai_dung_truoc_khi_ghi(repo, tmp_path, kieu):
    bam = dg.sha256(b"DEMO whl")
    tham = {
        "sai_bam": dict(wheel=b"khac"),
        "thieu_khai": dict(khai=False),
        "co_sdk": dict(lock=f"kho_tri_thuc_sdk==2.5.0 --hash=sha256:{bam}\ndemo-lib==1.0.0 --hash=sha256:{bam}\n".encode()),
        "noi_dong": dict(lock=f"demo-lib==1.0.0 \\\n    --hash=sha256:{bam}\n".encode()),
        "thieu_wheel": dict(lock=f"demo-lib==1.0.0 --hash=sha256:{bam}\nkhac==2.0 --hash=sha256:{bam}\n".encode()),
    }[kieu]
    them_thu_vien(repo, **tham)
    with pytest.raises(dg.LoiDongGoi):
        xuat(repo, tmp_path / "ra", sdk="2.5.0")
    assert not (tmp_path / "ra").exists()
