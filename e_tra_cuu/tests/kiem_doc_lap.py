"""Kiểm gói độc lập bằng phân tích tĩnh; mã thoát 0/1."""

import ast
import os
from pathlib import Path
import sys


GOI = Path(__file__).resolve().parents[1] / "goi" / "e_tra_cuu"
_CAM = {"kenh_engine", "Bootstrap", "SDKEngine", "socket", "sqlite3", "bootstrap", "KenhCore"}


def kiem_goi(goc):
    loi = []
    if not goc.is_dir() or goc.is_symlink():
        return ["Không có thư mục gói độc lập hợp lệ."]
    for thu_muc, thu_muc_con, tep_con in os.walk(goc, followlinks=False):
        for ten in thu_muc_con + tep_con:
            tep = Path(thu_muc) / ten
            nhan = tep.relative_to(goc).as_posix()
            if tep.is_symlink() or getattr(tep, "is_junction", lambda: False)():
                loi.append(f"{nhan}: không được có liên kết.")
                if ten in thu_muc_con:
                    thu_muc_con.remove(ten)
            elif ten == "__pycache__" or tep.suffix.lower() == ".pyc":
                loi.append(f"{nhan}: không được có bytecode.")
            elif tep.suffix == ".py" and tep.is_file():
                try:
                    cay = ast.parse(tep.read_text(encoding="utf-8-sig"))
                except (ValueError, SyntaxError):
                    loi.append(f"{nhan}: mã Python không hợp lệ.")
                    continue
                for nut in ast.walk(cay):
                    if isinstance(nut, ast.Import):
                        ds = [m.name for m in nut.names]
                    elif isinstance(nut, ast.ImportFrom):
                        if nut.level:
                            # Gói chỉ một cấp; không được thoát sang repo ngoài.
                            if nut.level > 1 or ((nut.module or "").split(".")[0] in _CAM
                                    or (nut.module or "").startswith("e_")):
                                loi.append(f"{nhan}:{nut.lineno}: import tương đối bị cấm.")
                            ds = []
                        else:
                            ds = [nut.module or ""]
                    else:
                        ds = []
                    for ma in ds:
                        goc_ma = ma.split(".")[0]
                        if (goc_ma not in sys.stdlib_module_names | {"e_tra_cuu", "kho_tri_thuc_sdk"}
                                or any(phan in _CAM for phan in ma.split("."))):
                            loi.append(f"{nhan}:{nut.lineno}: import ngoài SDK/thư viện chuẩn/gói.")
                    if ((isinstance(nut, ast.Name) and nut.id in _CAM)
                            or (isinstance(nut, ast.Attribute) and nut.attr in _CAM)
                            or (isinstance(nut, ast.alias) and any(x in _CAM for x in nut.name.split(".")))):
                        loi.append(f"{nhan}:{nut.lineno}: dùng kênh hoặc API bị cấm.")
                    if isinstance(nut, ast.Call):
                        ham = nut.func
                        if ((isinstance(ham, ast.Name) and ham.id in {"__import__", "eval", "exec"})
                                or (isinstance(ham, ast.Attribute) and ham.attr == "import_module")):
                            loi.append(f"{nhan}:{nut.lineno}: nạp mã động không được phép.")
    return loi


def main():
    loi = kiem_goi(GOI)
    for cau in loi:
        print(cau)
    print("[LỖI] Gói chưa độc lập." if loi else "[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.")
    return 1 if loi else 0


if __name__ == "__main__":
    raise SystemExit(main())
