"""Kiểm runtime trong venv mới, chỉ stdlib + SDK; không giả là máy OS sạch."""
import argparse
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
GOC = Path(__file__).resolve().parents[2]
GOI = GOC / "e_trich_xuat/goi/e_trich_xuat"


def main(bo_demo=None):
    assert sys.prefix != sys.base_prefix, "Cần venv mới."
    cfg = Path(sys.prefix, "pyvenv.cfg").read_text(encoding="utf-8")
    assert "include-system-site-packages = false" in cfg.lower()
    assert version("kho_tri_thuc_sdk") == "2.0.0"
    for ten in ("pytest", "jsonschema"):
        try:
            version(ten)
        except PackageNotFoundError:
            pass
        else:
            raise AssertionError("Venv runtime không được dựa thư viện kiểm trên máy.")
    wheel = GOC / "docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == "a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892"
    for k in ("ngan.py", "cau_hinh.py"):
        assert (GOI / "e_trich_xuat" / k).read_bytes().replace(b"\r\n", b"\n") == (GOC / "_chung/mau-ma" / k).read_bytes().replace(b"\r\n", b"\n")
    for p in (GOI / "contract").glob("*.json"):
        assert p.read_bytes().replace(b"\r\n", b"\n") == (GOC / "_chung/contract" / p.name).read_bytes().replace(b"\r\n", b"\n")
    for script in ("kiem_doc_lap.py", "chay_demo_voi_ngan_gia.py"):
        subprocess.run([sys.executable, "-B", str(Path(__file__).parent / script)], check=True)
    for ten in ("do_suc_chua_model.py", "do_n1_mot_lan.py"):
        lenh = [sys.executable, "-B", str(GOC / "e_trich_xuat/cong-cu" / ten)]
        if ten == "do_n1_mot_lan.py" and bo_demo:
            lenh += ["--bo-demo", str(bo_demo)]
        subprocess.run(lenh, check=True)
    # Lệnh chuẩn vẫn được chạy và kiểm đúng lỗi đã biết; không biến exit 1 thành đạt.
    sdk = subprocess.run([sys.executable, "-B", "-m", "kho_tri_thuc_sdk.thu", str(GOI)],
                         capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert sdk.returncode == 1 and "Engine chưa được cấu hình." in sdk.stdout + sdk.stderr
    assert "DANG_CHAY" in sdk.stdout + sdk.stderr
    print("CLI SDK chuẩn: 3/5 ĐẠT, exit 1; C-TX-04/C-TX-06 vẫn mở.")
    print("[ĐẠT] Venv runtime mới: offline, không system-site-packages/pytest/jsonschema; DEMO ngăn 5/5.")
    print("đã kiểm bằng Core giả (CoreGia); chưa chứng nhận máy OS sạch, Linux/CI/Core thật.")
    return 0


def tao_venv(bo_demo=None):
    thu_muc = Path(tempfile.mkdtemp(prefix="tx6-sach-")) / "venv"
    subprocess.run([sys.executable, "-B", "-m", "venv", str(thu_muc)], check=True)
    py = thu_muc / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    wheel = GOC / "docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl"
    for them in ([str(wheel)], ["-r", str(GOI / "requirements.lock")]):
        subprocess.run([str(py), "-B", "-m", "pip", "install", "--no-compile", "--no-index", "--no-deps", *them], check=True)
    lenh = [str(py), "-B", str(Path(__file__).resolve())]
    if bo_demo:
        lenh += ["--bo-demo", str(Path(bo_demo).resolve())]
    return subprocess.run(lenh).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tao-venv", action="store_true")
    parser.add_argument("--bo-demo", type=Path)
    args = parser.parse_args()
    try:
        code = tao_venv(args.bo_demo) if args.tao_venv else main(args.bo_demo)
    except (AssertionError, OSError, subprocess.CalledProcessError):
        print("[LỖI] Kiểm venv mới chưa đạt; xem bước DEMO/nguồn đang thiếu, không chứng nhận máy sạch.", file=sys.stderr)
        code = 1
    raise SystemExit(code)
