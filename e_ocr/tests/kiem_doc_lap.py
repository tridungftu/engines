"""Kiểm gói bằng AST và cây tệp, không nạp mã engine hay mã Core."""

from __future__ import annotations

import ast
from pathlib import Path
import re
import sys


THU_MUC_GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
_TEN_CAM = {"kenh_engine", "SDKEngine", "Bootstrap", "engine_legacy"}
_THU_VIEN_NGOAI = {"pdfplumber": "pdfplumber", "PIL": "Pillow"}


def _import_cam(ten):
    return ten.split(".")[0] == "kho_tri_thuc" or bool(set(ten.split(".")) & _TEN_CAM)


def kiem_doc_lap(thu_muc_goi=THU_MUC_GOI):
    goc = Path(thu_muc_goi)
    loi = []
    if not goc.is_dir() or goc.is_symlink():
        return ["Không tìm thấy thư mục gói độc lập hợp lệ."]
    lock = goc / "requirements.lock"
    cac_pin = set(re.findall(r"^([A-Za-z0-9_.-]+)==[^\s]+$", lock.read_text(encoding="utf-8"), re.M)) if lock.is_file() else set()
    duoc_import = sys.stdlib_module_names | {"e_ocr", "kho_tri_thuc_sdk"} | {
        ten for ten, goi in _THU_VIEN_NGOAI.items() if goi in cac_pin
    }
    for tep in sorted(goc.rglob("*")):
        ten = tep.relative_to(goc).as_posix()
        if tep.is_symlink():
            loi.append(f"{ten}: gói có liên kết tượng trưng.")
            continue
        if tep.name == "__pycache__" or tep.suffix in (".pyc", ".pyo"):
            loi.append(f"{ten}: gói có tệp hoặc thư mục biên dịch sẵn.")
        if not tep.is_file():
            continue
        if tep.stat().st_size > 20 * 1024 * 1024:
            loi.append(f"{ten}: tệp vượt giới hạn 20 MiB của gói.")
        if tep.suffix != ".py":
            continue
        try:
            cay = ast.parse(tep.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, SyntaxError):
            loi.append(f"{ten}: không phân tích được mã Python.")
            continue
        for nut in ast.walk(cay):
            cac_ten = []
            if isinstance(nut, ast.Import):
                cac_ten = [muc.name for muc in nut.names]
            elif isinstance(nut, ast.ImportFrom):
                cac_ten = [nut.module or ""] + [muc.name for muc in nut.names]
            elif isinstance(nut, ast.Call) and nut.args:
                ham = nut.func
                if (isinstance(ham, ast.Name) and ham.id == "__import__") or (
                    isinstance(ham, ast.Attribute) and ham.attr == "import_module"
                ):
                    if isinstance(nut.args[0], ast.Constant) and isinstance(nut.args[0].value, str):
                        cac_ten = [nut.args[0].value]
                    else:
                        loi.append(f"{ten}:{nut.lineno}: không kiểm được import động.")
            for muc in cac_ten:
                if _import_cam(muc):
                    loi.append(f"{ten}:{nut.lineno}: có import Core hoặc kênh SDK cũ.")
                elif isinstance(nut, ast.Import) or (
                    isinstance(nut, ast.ImportFrom) and nut.level == 0 and muc == nut.module
                ):
                    goc_import = muc.split(".")[0]
                    if goc_import not in duoc_import:
                        loi.append(f"{ten}:{nut.lineno}: có thư viện ngoài phạm vi đã ghim.")
    return loi


def main():
    loi = kiem_doc_lap()
    for muc in loi:
        print(f"[LỖI] {muc}")
    if not loi:
        print("[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.")
    return 1 if loi else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
