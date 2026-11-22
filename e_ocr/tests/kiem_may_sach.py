"""Cài SDK và thư viện vào môi trường sạch, không truy cập mạng."""

from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from kiem_thu_vien import GOI, kiem_goi_thu_vien


ROOT = Path(__file__).resolve().parents[2]
SDK = ROOT / "docs/goi-gui-engine/sdk-2.5.0"


def main():
    kiem_goi_thu_vien()
    wheel_sdk = SDK / "kho_tri_thuc_sdk-2.5.0-py3-none-any.whl"
    bang_bam = dict(dong.split(maxsplit=1)[::-1]
                   for dong in (SDK / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines() if dong)
    if sha256(wheel_sdk.read_bytes()).hexdigest() != bang_bam[wheel_sdk.name]:
        raise ValueError("Băm wheel SDK khác SHA256SUMS.txt.")
    # Windows dùng đúng wheel kèm gói. Linux CI chuẩn bị wheelhouse riêng theo
    # hash Linux trong cùng lock; công cụ này luôn cài ngoại tuyến.
    if sys.platform == "win32":
        wheelhouse = GOI / "wheels"
    else:
        if not os.environ.get("WHEELHOUSE"):
            raise ValueError("Linux cần WHEELHOUSE chứa wheel đúng hash Linux trong lock.")
        wheelhouse = Path(os.environ["WHEELHOUSE"]).resolve(strict=True)
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    env.pop("PYTHONPATH", None)
    with TemporaryDirectory(prefix="e-ocr-clean-") as tam:
        khu = Path(tam)
        subprocess.run([sys.executable, "-I", "-X", "utf8", "-m", "venv", str(khu / "venv")], check=True, env=env)
        python = khu / "venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        pip = [str(python), "-I", "-X", "utf8", "-m", "pip", "install", "--isolated", "--no-index", "--no-deps"]
        subprocess.run([*pip, str(wheel_sdk)], check=True, env=env)
        thu_vien = khu / "e_ocr.thu-vien"
        subprocess.run([*pip, "--find-links", str(wheelhouse), "--require-hashes", "--only-binary", ":all:",
                        "--target", str(thu_vien), "-r", str(GOI / "requirements.lock")], check=True, env=env)
        env["PYTHONPATH"] = str(thu_vien)
        for script, args in [("kiem_thu_vien.py", []), ("kiem_doc_lap.py", []), ("chay_demo.py", ["--gia"])]:
            subprocess.run([str(python), "-B", "-X", "utf8", str(Path(__file__).parent / script), *args],
                           check=True, env=env, cwd=ROOT)
    print("[ĐẠT] Máy sạch: SDK 2.5.0, thư viện riêng, 6/6 DEMO bằng Core giả (CoreGia) và Tesseract giả.")


if __name__ == "__main__":
    raise SystemExit(main())
