"""Kiểm gói độc lập; mã thoát 0 khi đạt, 1 khi có vi phạm."""
import ast
from pathlib import Path
import sys

GOI = Path(__file__).resolve().parents[1] / "goi"

def kiem_tra(goc):
    loi = []
    if not goc.is_dir():
        return ["Thiếu thư mục gói"]
    for tep in goc.rglob("*"):
        if tep.is_symlink() or getattr(tep, "is_junction", lambda: False)():
            loi.append(f"Liên kết: {tep}")
            continue
        if tep.name == "__pycache__" or tep.suffix == ".pyc":
            loi.append(f"Tệp đệm: {tep}")
        if tep.is_file() and tep.suffix == ".py":
            try:
                cay = ast.parse(tep.read_text(encoding="utf-8"))
                for node in ast.walk(cay):
                    ten = []
                    if isinstance(node, ast.Import):
                        ten = [x.name for x in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        ten = [node.module or ""]
                    if any(x == "kho_tri_thuc" or x.startswith("kho_tri_thuc.") or x == "socket" or "kenh_engine" in x for x in ten):
                        loi.append(f"Import bị cấm: {tep}")
                    if isinstance(node, ast.Name) and node.id in {"Bootstrap", "SDKEngine", "kenh_engine"}:
                        loi.append(f"Kênh cũ: {tep}")
                    if isinstance(node, ast.Attribute) and node.attr in {"Bootstrap", "SDKEngine", "kenh_engine"}:
                        loi.append(f"Kênh cũ: {tep}")
            except (SyntaxError, UnicodeError) as exc:
                loi.append(f"Không đọc được mã: {tep}: {type(exc).__name__}")
    return loi

if __name__ == "__main__":
    loi = kiem_tra(GOI)
    for dong in loi:
        print(dong)
    print("CHƯA ĐẠT" if loi else "ĐẠT: kiểm độc lập")
    sys.exit(bool(loi))
