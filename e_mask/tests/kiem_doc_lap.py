"""Kiểm gói độc lập; mã thoát 0 khi đạt, 1 khi không đạt."""
import ast
import os
from pathlib import Path
import re
import stat
import sys

CAM = re.compile(r"(?i)(?:kho_tri_thuc\.|kenh_engine|SDKEngine|Bootstrap|shim[_-]kho|\bsql\b|sqlite|psycopg|postgres|mysql|pymysql|pyodbc|sqlalchemy|https?://(?!json-schema\.org/)|urllib|requests|httpx|aiohttp|subprocess|socket)")

def kiem_tra(thu_muc):
    goc = Path(thu_muc).absolute()
    loi = []
    def quet(p):
        try:
            st = p.lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
                loi.append("Có liên kết trong gói."); return
            if p.name.casefold() == "__pycache__" or p.suffix.casefold() == ".pyc":
                loi.append("Có tệp hoặc thư mục biên dịch."); return
            if stat.S_ISDIR(st.st_mode):
                for con in p.iterdir(): quet(con)
            elif stat.S_ISREG(st.st_mode):
                noi_dung = p.read_text(encoding="utf-8")
                if CAM.search(noi_dung): loi.append(f"Có tham chiếu bị cấm: {p.relative_to(goc)}")
                if p.suffix == ".py":
                    cay = ast.parse(noi_dung)
                    for nut in ast.walk(cay):
                        if isinstance(nut, (ast.Import, ast.ImportFrom)):
                            ten = [a.name for a in nut.names] if isinstance(nut, ast.Import) else [nut.module or ""]
                            if any(CAM.search(t) or t == "kho_tri_thuc" for t in ten):
                                loi.append(f"Import bị cấm: {p.relative_to(goc)}")
            else: loi.append("Có mục không phải tệp thường.")
        except (OSError, UnicodeError, SyntaxError, ValueError):
            loi.append("Không kiểm được một mục trong gói.")
    quet(goc)
    return loi

def main():
    if len(sys.argv) > 2:
        print("Cách dùng: kiem_doc_lap.py [thư mục gói]"); return 1
    goc = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[1] / "goi"
    loi = kiem_tra(goc)
    for cau in loi: print("[LỖI]", cau)
    if loi: return 1
    print("[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
