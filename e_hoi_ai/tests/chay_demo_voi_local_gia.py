"""Bật Local HTTP giả rồi chạy nguyên lệnh SDK thu; đã kiểm bằng Core giả (CoreGia)."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from local_gia import LocalGia, ghi_cau_hinh


def main():
    goc = Path(__file__).resolve().parents[2]
    with TemporaryDirectory(prefix="ktt-ai-1-demo-") as thu_muc, LocalGia() as local:
        tep = ghi_cau_hinh(thu_muc, local.url)
        moi_truong = {**os.environ, "KTT_ENGINE_CAU_HINH": str(tep),
                      "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
        lenh = [sys.executable, "-m", "kho_tri_thuc_sdk.thu", "e_hoi_ai/goi/e_hoi_ai"]
        print("Chạy: python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai", flush=True)
        ket_qua = subprocess.run(lenh, cwd=goc, env=moi_truong, timeout=30)
        if ket_qua.returncode:
            return ket_qua.returncode
        if local.so_luot_hoi != 1:
            print("[LỖI] DEMO phải thực sự gọi Local giả đúng một lượt.")
            return 1
        print("[ĐẠT] Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; 1 lượt Local.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
