"""Kiểm tĩnh hai tệp mẫu: chỉ thư viện chuẩn, không tệp biên dịch sẵn."""

import ast
from pathlib import Path
import sys


def kiem_doc_lap():
    goc = Path(__file__).resolve().parents[1]
    loi = []
    for ten in ("ngan.py", "cau_hinh.py"):
        tep = goc / ten
        if tep.is_symlink():
            loi.append("Mẫu có liên kết tượng trưng.")
        for nut in ast.walk(ast.parse(tep.read_text(encoding="utf-8"))):
            if isinstance(nut, ast.Import):
                cac_ten = [x.name for x in nut.names]
            elif isinstance(nut, ast.ImportFrom):
                cac_ten = [nut.module or ""]
                if nut.level:
                    loi.append("Mẫu có import tương đối ngoài thư viện chuẩn.")
            else:
                continue
            if any(t.split(".")[0] not in sys.stdlib_module_names for t in cac_ten):
                loi.append("Mẫu có import ngoài thư viện chuẩn.")
    if any(p.name == "__pycache__" or p.suffix in (".pyc", ".pyo") or p.is_symlink()
           for p in goc.rglob("*")):
        loi.append("Thư mục mẫu có tệp biên dịch sẵn hoặc liên kết tượng trưng.")
    return loi


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cac_loi = kiem_doc_lap()
    for loi in cac_loi:
        print("[LỖI] " + loi)
    if not cac_loi:
        print("[ĐẠT] Hai tệp mẫu chỉ dùng thư viện chuẩn; không có tệp biên dịch sẵn.")
    raise SystemExit(bool(cac_loi))
