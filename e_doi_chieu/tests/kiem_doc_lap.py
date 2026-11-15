"""Ki?m g?i ??c l?p; m? tho?t 0 khi ??t, 1 khi c? vi ph?m."""
import ast
from pathlib import Path
import sys

GOI = Path(__file__).resolve().parents[1] / "goi"

def kiem_tra(goc):
    loi = []
    if not goc.is_dir():
        return ["Thi?u th? m?c g?i"]
    for tep in goc.rglob("*"):
        if tep.is_symlink() or getattr(tep, "is_junction", lambda: False)():
            loi.append(f"Li?n k?t: {tep}")
            continue
        if tep.name == "__pycache__" or tep.suffix == ".pyc":
            loi.append(f"T?p ??m: {tep}")
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
                        loi.append(f"Import b? c?m: {tep}")
                    if isinstance(node, ast.Name) and node.id in {"Bootstrap", "SDKEngine", "kenh_engine"}:
                        loi.append(f"K?nh c?: {tep}")
                    if isinstance(node, ast.Attribute) and node.attr in {"Bootstrap", "SDKEngine", "kenh_engine"}:
                        loi.append(f"K?nh c?: {tep}")
            except (SyntaxError, UnicodeError) as exc:
                loi.append(f"Kh?ng ??c ???c m?: {tep}: {type(exc).__name__}")
    return loi

if __name__ == "__main__":
    loi = kiem_tra(GOI)
    for dong in loi:
        print(dong)
    print("CH?A ??T" if loi else "??T: ki?m ??c l?p")
    sys.exit(bool(loi))
