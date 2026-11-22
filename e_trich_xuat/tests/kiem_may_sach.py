"""Kiểm SDK Core cấp và thư viện cài offline trong venv mới; không chứng nhận OS sạch."""
import argparse
import hashlib
from importlib.metadata import version, PackageNotFoundError, distribution
from pathlib import Path
import subprocess
import sys
import tempfile

from phu_thuoc_python import doc_lock, kiem_goi_phu_thuoc

sys.dont_write_bytecode = True
GOC = Path(__file__).resolve().parents[2]
GOI = GOC / "e_trich_xuat/goi/e_trich_xuat"
THU_MUC_SDK = GOC / "docs/goi-gui-engine/sdk-2.5.0"
WHEEL_SDK = THU_MUC_SDK / "kho_tri_thuc_sdk-2.5.0-py3-none-any.whl"


def kiem_bam_sdk():
    dong = next(d for d in (THU_MUC_SDK / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
                if d.split()[-1].lstrip("*") == WHEEL_SDK.name)
    assert hashlib.sha256(WHEEL_SDK.read_bytes()).hexdigest() == dong.split()[0]


def lenh_script(tep, tham_so=(), thu_vien=None):
    # -I bỏ PYTHONPATH/user-site; chỉ thêm thư viện riêng và thư mục script.
    ma = ("import runpy,sys; from pathlib import Path; "
          "tep=Path(sys.argv[1]); sys.path.extend([sys.argv[2],str(tep.parent)]); "
          "sys.argv=[str(tep),*sys.argv[3:]]; runpy.run_path(str(tep),run_name='__main__')")
    return [sys.executable, "-I", "-B", "-X", "utf8", "-c", ma,
            str(tep), str(thu_vien or Path(sys.prefix) / "lib-khong-co"), *map(str, tham_so)]


def main(bo_demo=None, thu_vien=None):
    assert sys.prefix != sys.base_prefix, "Cần venv mới."
    cfg = Path(sys.prefix, "pyvenv.cfg").read_text(encoding="utf-8")
    assert "include-system-site-packages = false" in cfg.lower()
    assert version("kho_tri_thuc_sdk") == "2.5.0", "Venv kiểm cần wheel SDK 2.5.0 đã cấp."
    kiem_bam_sdk()
    kiem_goi_phu_thuoc(GOI)
    for ten, ghim in doc_lock(GOI / "requirements.lock").items():
        assert version(ten) == ghim["phien_ban"], "Thư viện chưa khớp lock."
        if thu_vien:
            assert Path(distribution(ten).locate_file("")).resolve() == thu_vien.resolve()
    for ten in ("pytest",):
        try:
            version(ten)
        except PackageNotFoundError:
            pass
        else:
            raise AssertionError("Venv runtime không được dựa thư viện kiểm trên máy.")
    for k in ("ngan.py", "cau_hinh.py"):
        assert not (GOI / "e_trich_xuat" / k).exists()
        assert (GOC / "e_trich_xuat/LUU-TRU/TX-7" / k).is_file()
    for p in (GOI / "contract").glob("*.json"):
        assert p.read_bytes().replace(b"\r\n", b"\n") == (GOC / "_chung/contract" / p.name).read_bytes().replace(b"\r\n", b"\n")
    for script in ("kiem_doc_lap.py",):
        subprocess.run(lenh_script(Path(__file__).parent / script, thu_vien=thu_vien), check=True)
    for ten in ("do_suc_chua_model.py", "do_n1_mot_lan.py"):
        tham_so = []
        if ten == "do_n1_mot_lan.py" and bo_demo:
            tham_so += ["--bo-demo", str(bo_demo)]
        subprocess.run(lenh_script(GOC / "e_trich_xuat/cong-cu" / ten, tham_so, thu_vien), check=True)
    # Chỉ CLI chuẩn quyết định đạt DEMO; không còn cổng thay thế.
    ma = ("import runpy,sys; sys.path.append(sys.argv.pop(1)); "
          "sys.argv=['kho_tri_thuc_sdk.thu',*sys.argv[1:]]; "
          "runpy.run_module('kho_tri_thuc_sdk.thu',run_name='__main__')")
    sdk = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", "-c", ma,
                          str(thu_vien or Path(sys.prefix) / "lib-khong-co"), str(GOI)],
                         capture_output=True, text=True, encoding="utf-8", timeout=30)
    print(sdk.stdout)
    if sdk.stderr:
        print(sdk.stderr, file=sys.stderr)
    if sdk.returncode:
        print("[CHƯA ĐẠT] CLI SDK chuẩn còn thiếu nạp tệp phụ DEMO (C-TX-06).")
        return sdk.returncode
    print("[ĐẠT] Venv mới: SDK 2.5.0, thư viện cài offline từ lock vào khu riêng; DEMO chuẩn đạt.")
    print("đã kiểm bằng Core giả (CoreGia); chưa chứng nhận máy OS sạch, Linux/CI/Core thật.")
    return 0


def tao_venv(bo_demo=None, kho_wheel=None):
    kiem_bam_sdk()
    kiem_goi_phu_thuoc(GOI)
    khu = Path(tempfile.mkdtemp(prefix="tx25-sach-", dir=GOC / ".venv"))
    thu_muc = khu / "venv"
    thu_vien = khu / "e_trich_xuat.thu-vien"
    subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", "-m", "venv", str(thu_muc)], check=True)
    py = thu_muc / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    pip = [str(py), "-I", "-X", "utf8", "-m", "pip", "install", "--isolated",
           "--no-index", "--only-binary", ":all:", "--no-deps", "--no-compile"]
    subprocess.run([*pip, str(WHEEL_SDK)], check=True)
    subprocess.run([*pip, "--find-links", str(kho_wheel or GOI / "wheels"), "--require-hashes",
                    "--target", str(thu_vien), "-r", str(GOI / "requirements.lock")], check=True)
    lenh = lenh_script(Path(__file__).resolve(), ["--thu-vien", str(thu_vien)], thu_vien)
    lenh[0] = str(py)
    if bo_demo:
        lenh += ["--bo-demo", str(Path(bo_demo).resolve())]
    return subprocess.run(lenh).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tao-venv", action="store_true")
    parser.add_argument("--bo-demo", type=Path)
    parser.add_argument("--kho-wheel", type=Path, help="Kho wheel phụ thuộc đã ghim, không dùng mạng.")
    parser.add_argument("--thu-vien", type=Path, help="Khu thư viện riêng vừa cài từ lock.")
    args = parser.parse_args()
    if args.thu_vien:
        sys.path.append(str(args.thu_vien.resolve()))
    try:
        code = tao_venv(args.bo_demo, args.kho_wheel) if args.tao_venv else main(args.bo_demo, args.thu_vien)
    except (AssertionError, ValueError, OSError, subprocess.CalledProcessError):
        print("[LỖI] Kiểm venv mới chưa đạt; xem bước DEMO/nguồn đang thiếu, không chứng nhận máy sạch.", file=sys.stderr)
        code = 1
    raise SystemExit(code)
