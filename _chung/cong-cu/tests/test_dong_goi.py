"""Kiểm đóng gói bằng kho git DEMO biệt lập, không commit vào repo làm việc."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
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


@pytest.mark.parametrize("nen", ["windows", "linux"])
@pytest.mark.parametrize("kieu", ["sha", "bytes", "thieu", "thua", "lap", "phien_ban"])
def test_kiem_ke_sai_dung_truoc_khi_ghi(repo, tmp_path, kieu, nen):
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
        xuat(repo, tmp_path / "ra", nen=nen)
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


WHEEL_WIN = "demo_native-1.0.0-cp313-cp313-win_amd64.whl"
WHEEL_LINUX = "demo_native-1.0.0-cp313-cp313-manylinux_2_39_x86_64.whl"
WHEEL_THUAN = "demo_lib-1.0.0-py3-none-any.whl"


def them_wheel_linux(repo, tag="cp313-cp313-manylinux_2_39_x86_64", co_linux=True):
    them_thu_vien(repo)
    p = duong_goi(repo)
    (p / "wheels" / WHEEL_WIN).write_bytes(b"DEMO Windows\r\n")
    lock = (p / "requirements.lock").read_bytes()
    lock += (f"demo-native==1.0.0 --hash=sha256:{dg.sha256(b'DEMO Windows' + bytes([13, 10]))}"
             f" --hash=sha256:{dg.sha256(b'DEMO Linux' + bytes([10]))}\n").encode()
    (p / "requirements.lock").write_bytes(lock)
    if co_linux:
        thu_muc = repo / MA / "wheels-linux"
        thu_muc.mkdir(exist_ok=True)
        (thu_muc / f"demo_native-1.0.0-{tag}.whl").write_bytes(b"DEMO Linux\n")
    return tao_moc(repo)


def doc_zip(thu_muc, ds):
    with zipfile.ZipFile(thu_muc / ds[0]["tep_zip"]) as z:
        return {ten[len(MA) + 1:]: z.read(ten) for ten in z.namelist()}


def kiem_kiem_ke_core(cac_tep, ten_tep, phien_ban):
    """Chép quy tắc _kiem_kiem_ke_tep của Core; dùng assert, không phụ thuộc mã Core."""
    kk = json.loads(cac_tep[ten_tep])
    assert isinstance(kk, dict) and kk["phien_ban"] == phien_ban
    assert isinstance(kk["tep"], list)
    da_gap = set()
    for muc in kk["tep"]:
        assert isinstance(muc, dict)
        ten = muc["duong_dan"]
        assert isinstance(ten, str) and ten and not PurePosixPath(ten).is_absolute()
        assert "\\" not in ten and ":" not in ten and not {"", ".", ".."} & set(ten.split("/"))
        for phan in ten.split("/"):
            assert not phan.endswith((" ", ".")) and not re.search(r'[\x00-\x1f<>"|?*]', phan)
            assert not re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", phan)
        so, bam = muc.get("bytes"), muc.get("sha256")
        assert ten != ten_tep and ten not in da_gap and ten in cac_tep
        assert type(so) is int and so >= 0
        assert isinstance(bam, str) and re.fullmatch(r"[0-9a-f]{64}", bam)
        da_gap.add(ten)
        assert so == len(cac_tep[ten])
        assert bam == hashlib.sha256(cac_tep[ten]).hexdigest()
    assert da_gap == set(cac_tep) - {ten_tep}


@pytest.mark.parametrize("co_thu_vien, bam_truoc", [
    (False, "aadd8c2fcb2ba24d55b2a60cb603cc858294a701b4d201a6c22db801b52aef5f"),
    (True, "7d40ec77642215d306465615bf399816cd6c0557819f05f804a75ebed9aac6ba"),
])
def test_windows_giu_nguyen_byte_zip_truoc_lx_dg(repo, tmp_path, co_thu_vien, bam_truoc):
    # SHA ZIP DEMO đo bằng dong_goi.py trước LX-DG; không lấy kết quả mới làm chuẩn.
    if co_thu_vien:
        them_thu_vien(repo)
    sdk = "2.5.0" if co_thu_vien else dg.SDK
    for nen, thu_muc in [(None, tmp_path / "mac_dinh"), ("windows", tmp_path / "windows")]:
        ds = xuat(repo, thu_muc, sdk=sdk, **({"nen": nen} if nen else {}))
        assert ds[0]["tep_zip"] == f"{MA}-1.0.0.zip"
        assert hashlib.sha256((thu_muc / ds[0]["tep_zip"]).read_bytes()).hexdigest() == bam_truoc


def test_linux_thay_wheel_tu_git_va_tat_dinh(repo, tmp_path):
    cu = them_wheel_linux(repo)
    thu_muc = repo / MA / "wheels-linux"
    (thu_muc / WHEEL_LINUX).write_bytes(b"DEMO dirty wheel\r\n")
    (thu_muc / "khac-1.0.0-py3-none-any.whl").write_bytes(b"DEMO ngoai moc")
    tao_moc(repo)
    a, b = tmp_path / "linux_a", tmp_path / "linux_b"
    ds = xuat(repo, a, ref=cu, sdk="2.5.0", nen="linux")
    xuat(repo, b, ref=cu, sdk="2.5.0", nen="linux")
    assert {p.name: p.read_bytes() for p in a.iterdir()} == {p.name: p.read_bytes() for p in b.iterdir()}
    assert ds[0]["tep_zip"] == f"{MA}-1.0.0-linux_x86_64.zip"
    tep = doc_zip(a, ds)
    assert {ten for ten in tep if ten.startswith("wheels/")} == {"wheels/" + WHEEL_LINUX, "wheels/" + WHEEL_THUAN}
    assert tep["wheels/" + WHEEL_LINUX] == b"DEMO Linux\n"
    assert tep["wheels/" + WHEEL_THUAN] == b"DEMO whl"
    assert tep["requirements.lock"] == lenh_git(repo, "show", f"{cu}:{MA}/goi/{MA}/requirements.lock")
    bang = json.loads((a / "DANH-SACH-GOI.json").read_bytes())
    assert bang["nen"] == "linux" and bang["goi"] == ds and bang["commit_git"] == cu
    sums = dict(dong.split("  ")[::-1] for dong in (a / "SHA256SUMS.txt").read_text().splitlines())
    assert set(sums) == {W25, ds[0]["tep_zip"]}
    assert all(hashlib.sha256((a / ten).read_bytes()).hexdigest() == bam for ten, bam in sums.items())


def test_linux_nhan_wheel_thuan_py2_py3(repo, tmp_path):
    # openpyxl/defusedxml mang tag py2.py3-none-any: wheel thuần, dùng chung hai nền.
    them_wheel_linux(repo)
    p = duong_goi(repo)
    ten = "demo_cu-2.0.0-py2.py3-none-any.whl"
    (p / "wheels" / ten).write_bytes(b"DEMO py2py3")
    lock = (p / "requirements.lock").read_bytes() + f"demo-cu==2.0.0 --hash=sha256:{dg.sha256(b'DEMO py2py3')}\n".encode()
    (p / "requirements.lock").write_bytes(lock)
    tao_moc(repo)
    ds = xuat(repo, tmp_path / "ra", sdk="2.5.0", nen="linux")
    assert doc_zip(tmp_path / "ra", ds)["wheels/" + ten] == b"DEMO py2py3"


def test_linux_uu_tien_wheel_thuan_trong_wheels_linux(repo, tmp_path):
    them_wheel_linux(repo)
    p = duong_goi(repo) / "requirements.lock"
    raw = b"DEMO pure Linux"
    p.write_bytes(p.read_bytes().replace(b"demo-lib==1.0.0 ",
                  f"demo-lib==1.0.0 --hash=sha256:{dg.sha256(raw)} ".encode()))
    (repo / MA / "wheels-linux" / WHEEL_THUAN).write_bytes(raw)
    tao_moc(repo)
    ds = xuat(repo, tmp_path / "ra", sdk="2.5.0", nen="linux")
    assert doc_zip(tmp_path / "ra", ds)["wheels/" + WHEEL_THUAN] == raw


def test_linux_sinh_lai_kiem_ke_toan_goi_theo_core(repo, tmp_path):
    them_wheel_linux(repo)
    them_sql(repo)
    kk_goc = lenh_git(repo, "show", f"HEAD:{MA}/goi/{MA}/sql/kiem_ke.json")
    linux, win = tmp_path / "linux", tmp_path / "windows"
    ds = xuat(repo, linux, sdk="2.5.0", nen="linux")
    ds_win = xuat(repo, win, sdk="2.5.0")
    tep, tep_win = doc_zip(linux, ds), doc_zip(win, ds_win)
    assert tep_win["sql/kiem_ke.json"] == kk_goc
    assert tep["sql/kiem_ke.json"] != kk_goc
    kiem_kiem_ke_core(tep, "sql/kiem_ke.json", "1.0.0")
    kiem_kiem_ke_core(tep_win, "sql/kiem_ke.json", "1.0.0")
    assert {t: b for t, b in tep.items() if not t.startswith("wheels/") and t != "sql/kiem_ke.json"} == {
        t: b for t, b in tep_win.items() if not t.startswith("wheels/") and t != "sql/kiem_ke.json"}
    # Công cụ không sửa kiểm kê trong worktree.
    assert (duong_goi(repo) / "sql/kiem_ke.json").read_bytes() == kk_goc


@pytest.mark.parametrize("co_sql", [False, True])
def test_linux_khong_wheel_giu_nguyen_zip_windows(repo, tmp_path, co_sql):
    if co_sql:
        them_sql(repo)
    ds_win = xuat(repo, tmp_path / "win")
    ds_linux = xuat(repo, tmp_path / "linux", nen="linux")
    assert (tmp_path / "win" / ds_win[0]["tep_zip"]).read_bytes() == (
        tmp_path / "linux" / ds_linux[0]["tep_zip"]).read_bytes()


def test_linux_thieu_wheel_dung_truoc_khi_ghi(repo, tmp_path):
    them_wheel_linux(repo, co_linux=False)
    with pytest.raises(dg.LoiDongGoi, match="Thiếu wheel.*demo-native"):
        xuat(repo, tmp_path / "ra", sdk="2.5.0", nen="linux")
    assert not (tmp_path / "ra").exists()


@pytest.mark.parametrize("tag", [
    "cp313-cp313-musllinux_1_2_x86_64", "cp313-cp313-manylinux_2_40_x86_64",
    "cp313-cp313-win_amd64", "cp313-cp313-macosx_11_0_x86_64",
    "cp313-cp313-manylinux_2_39_aarch64", "cp313-cp313-linux_x86_64",
    "cp313-cp313-manylinux_2_39_x86_64.manylinux_2_40_x86_64",
])
def test_linux_tu_choi_tag_sai(repo, tmp_path, tag):
    them_wheel_linux(repo, tag)
    with pytest.raises(dg.LoiDongGoi, match="không đúng nền linux"):
        xuat(repo, tmp_path / "ra", sdk="2.5.0", nen="linux")
    assert not (tmp_path / "ra").exists()


@pytest.mark.parametrize("tag", [
    "cp313-cp313-manylinux2014_x86_64", "cp313-cp313-manylinux1_x86_64",
    "cp313-cp313-manylinux2010_x86_64", "cp311-abi3-manylinux_2_34_x86_64",
    "py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64",
])
def test_linux_nhan_tag_hop_le(repo, tmp_path, tag):
    them_wheel_linux(repo, tag)
    ds = xuat(repo, tmp_path / "ra", sdk="2.5.0", nen="linux")
    assert f"wheels/demo_native-1.0.0-{tag}.whl" in doc_zip(tmp_path / "ra", ds)


@pytest.mark.parametrize("tag", ["cp313-cp313-manylinux_2_39_x86_64", "cp313-cp313-win32", "py3-none-macosx_11_0_x86_64"])
def test_windows_tu_choi_wheel_sai_nen(repo, tmp_path, tag):
    them_thu_vien(repo)
    (duong_goi(repo) / "wheels" / WHEEL_THUAN).rename(
        duong_goi(repo) / "wheels" / f"demo_lib-1.0.0-{tag}.whl")
    tao_moc(repo)
    with pytest.raises(dg.LoiDongGoi, match="không đúng nền windows"):
        xuat(repo, tmp_path / "ra", sdk="2.5.0")
    assert not (tmp_path / "ra").exists()


@pytest.mark.parametrize("kieu", ["sai_bam", "thua", "trung", "sai_ban"])
def test_linux_lock_va_wheel_sai_dung_truoc_khi_ghi(repo, tmp_path, kieu):
    them_wheel_linux(repo)
    thu_muc = repo / MA / "wheels-linux"
    if kieu == "sai_bam":
        (thu_muc / WHEEL_LINUX).write_bytes(b"DEMO bam sai")
    elif kieu == "thua":
        (thu_muc / "thua-1.0.0-py3-none-any.whl").write_bytes(b"DEMO Linux\n")
    elif kieu == "trung":
        (thu_muc / WHEEL_LINUX.replace("1.0.0-", "1.0.0-1-")).write_bytes(b"DEMO Linux\n")
    else:
        (thu_muc / WHEEL_LINUX).rename(thu_muc / WHEEL_LINUX.replace("1.0.0-", "2.0.0-"))
    tao_moc(repo)
    with pytest.raises(dg.LoiDongGoi, match="Wheel thừa, trùng, sai phiên bản hoặc sai băm"):
        xuat(repo, tmp_path / "ra", sdk="2.5.0", nen="linux")
    assert not (tmp_path / "ra").exists()


def test_tham_so_nen_linux_duoc_truyen_vao_dong_goi(repo, tmp_path, monkeypatch, capsys):
    dong_goi_goc = dg.dong_goi
    monkeypatch.setattr(dg, "dong_goi", lambda _repo, *args: dong_goi_goc(repo, *args))
    assert dg.main(["--engine", MA, "--ra", str(tmp_path / "ra"), "--nhan", "DEMO", "--nen", "linux"]) == 0
    assert f"{MA}-1.0.0-linux_x86_64.zip" in capsys.readouterr().out
