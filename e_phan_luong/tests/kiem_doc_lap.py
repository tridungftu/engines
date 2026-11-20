"""Kiểm cây gói, import AST, chuỗi mặc định tiền và import trong tiến trình sạch."""

import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"
CHO_PHEP = {"e_phan_luong", "kho_tri_thuc_sdk", "openpyxl", "et_xmlfile", "defusedxml"}
MODULE_CAM = {"kho_tri_thuc", "socket", "subprocess", "sqlite", "sqlite3", "psycopg",
              "psycopg2", "requests", "httpx", "urllib", "http", "ftplib", "smtplib",
              "importlib", "pickle", "builtins", "runpy", "site", "ctypes"}
TEN_CAM = {"kenh_engine", "SDKEngine", "Bootstrap", "__import__", "eval", "exec",
           "compile", "import_module", "system", "popen", "Popen", "spawnl", "spawnv"}
# Ngoại lệ grep chỉ dành cho mô tả/ví dụ, không miễn trừ mã runtime.
# tests/ nằm ngoài gói; README.md có câu minh họa về việc không tự gán tiền tệ.
NGOAI_LE_VND = ("README.md", "tests/")
MAU_VND = re.compile(r"(['\"])VND\1")


def kiem_doc_lap(goi=GOI):
    goi = Path(goi)
    ds_loi = []
    for tep in goi.rglob("*"):
        ten = tep.relative_to(goi).as_posix()
        if tep.is_symlink() or (hasattr(tep, "is_junction") and tep.is_junction()):
            ds_loi.append(f"{ten}: gói có liên kết.")
            continue
        if tep.name == "__pycache__" or tep.suffix.lower() in {".pyc", ".pyo"}:
            ds_loi.append(f"{ten}: gói có bytecode.")
        if not tep.is_file():
            continue
        if tep.stat().st_size > 20 * 1048576:
            ds_loi.append(f"{ten}: tệp quá lớn.")
        if tep.suffix != ".py":
            continue
        try:
            chu = tep.read_text(encoding="utf-8")
            cay = ast.parse(chu)
        except (SyntaxError, UnicodeError):
            ds_loi.append(f"{ten}: Python không hợp lệ.")
            continue
        # Grep literal VND trong mã gói, không chỉ một tên biến cụ thể.
        if ten not in NGOAI_LE_VND and not ten.startswith("tests/"):
            for so, dong in enumerate(chu.splitlines(), 1):
                if MAU_VND.search(dong) and not dong.lstrip().startswith("#"):
                    ds_loi.append(f"{ten}:{so}: có literal tiền tệ mặc định.")
        for nut in ast.walk(cay):
            imports = []
            if isinstance(nut, ast.Import):
                imports = [t.name for t in nut.names]
            elif isinstance(nut, ast.ImportFrom) and not nut.level:
                imports = [nut.module or ""]
            for module in imports:
                goc = module.split(".")[0]
                if goc in MODULE_CAM or goc not in sys.stdlib_module_names | CHO_PHEP:
                    ds_loi.append(f"{ten}:{nut.lineno}: import bị cấm hoặc chưa ghim.")
            if ((isinstance(nut, ast.Name) and nut.id in TEN_CAM)
                    or (isinstance(nut, ast.Attribute) and nut.attr in TEN_CAM
                        and not (nut.attr == "compile" and isinstance(nut.value, ast.Name)
                                 and nut.value.id == "re"))):
                ds_loi.append(f"{ten}:{nut.lineno}: cơ chế động hoặc kênh cũ bị cấm.")
            if isinstance(nut, ast.Constant) and isinstance(nut.value, str):
                if any(t in nut.value for t in ("kho_tri_thuc.", "ma-nguon", "shim-kho_tri_thuc", "tu-core-cu")):
                    ds_loi.append(f"{ten}:{nut.lineno}: phụ thuộc Core hoặc nguồn tham chiếu.")
    return ds_loi


def kiem_demo(goi=GOI):
    """Mỗi ví dụ phải trỏ tới tệp trong demo/ và có nhãn DEMO trong nội dung."""
    goi = Path(goi)
    try:
        phieu = json.loads((goi / "engine.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return ["Không đọc được phiếu để kiểm tệp DEMO."]
    ds_loi = []
    for so, vd in enumerate(phieu["chay_thu_demo"], 1):
        ten = vd["dau_vao"].get("tep_demo")
        if not isinstance(ten, str) or not ten.startswith("demo/"):
            ds_loi.append(f"DEMO thứ {so}: phải trỏ tới tệp trong demo/.")
            continue
        tep = (goi / ten).resolve()
        if not tep.is_relative_to((goi / "demo").resolve()) or not tep.is_file():
            ds_loi.append(f"DEMO thứ {so}: tệp không tồn tại trong demo/.")
            continue
        try:
            co_nhan = b"DEMO" in tep.read_bytes()
        except OSError:
            ds_loi.append(f"DEMO thứ {so}: không đọc được tệp.")
            continue
        if not co_nhan:
            ds_loi.append(f"DEMO thứ {so}: nội dung tệp thiếu nhãn DEMO.")
    return ds_loi


def kiem_tien_trinh_sach(goi=GOI):
    loi_demo = kiem_demo(goi)
    if loi_demo:
        return loi_demo
    spec = importlib.util.find_spec("kho_tri_thuc_sdk")
    if not spec or not spec.origin:
        return ["Thiếu SDK để kiểm import độc lập."]
    code = r'''
import sys
sys.dont_write_bytecode = True
sys.path[:0] = sys.argv[1:]
cho_phep = sys.stdlib_module_names | {'e_phan_luong', 'kho_tri_thuc_sdk'}
def kiem(event, args):
    if event == 'import' and args[0].split('.')[0] not in cho_phep:
        raise ModuleNotFoundError('Import ngoài SDK và thư viện chuẩn.')
    if event in {'socket.connect', 'socket.bind', 'subprocess.Popen', 'os.system'}:
        raise RuntimeError('Cấm mạng và tiến trình ngoài trong engine.')
sys.addaudithook(kiem)
import kho_tri_thuc_sdk
assert kho_tri_thuc_sdk.__version__ == '2.2.0'
from e_phan_luong.chay import app
from e_phan_luong import kieu, loi, ngan_chung
assert len(app.cac_nang_luc) == 5
assert not any(n == 'kho_tri_thuc' or n.startswith('kho_tri_thuc.') for n in sys.modules)
print('PL_DOC_LAP_DAT')
'''
    try:
        kq = subprocess.run([sys.executable, "-I", "-B", "-S", "-c", code,
                             str(Path(goi).resolve()), str(Path(spec.origin).parent.parent)],
                            cwd=goi, capture_output=True, text=True, encoding="utf-8", timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return ["Không chạy được tiến trình kiểm import độc lập."]
    if kq.returncode or "PL_DOC_LAP_DAT" not in kq.stdout:
        return [f"Import cô lập chưa đạt (mã thoát {kq.returncode})."]
    return []


def main():
    ds_loi = kiem_doc_lap()
    if not ds_loi:
        ds_loi += kiem_tien_trinh_sach()
    for cau in ds_loi:
        print("[LỖI] " + cau)
    if not ds_loi:
        print("[ĐẠT] Cây gói, AST, grep tiền tệ, import cô lập và tệp có nhãn DEMO.")
    return int(bool(ds_loi))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
