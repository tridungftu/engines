"""Kiểm AST toàn gói và import/chạy DEMO trong tiến trình sạch chỉ SDK/stdlib."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

THU_MUC_GOI = Path(__file__).resolve().parents[1] / "goi" / "e_hoa_don"
TEP_TOI_DA_BYTE = 20 * 1024 * 1024
_TEN_CAM = {"SDKEngine", "Bootstrap", "kenh_engine"}
# Fail-closed: gói XML không cần dynamic loader, thực thi mã hoặc pickle.
_DONG_CAM = {"__import__", "import_module", "exec", "eval", "compile", "__builtins__"}
_MODULE_CAM = {"pickle", "_pickle", "importlib", "builtins", "runpy", "sys", "site"}
_DAU_VET = "kho_tri_thuc.nguon.hoa_don_xml"
_DUONG_CAM = re.compile(
    r"kho_tri_thuc(?:[./\\]|$)|shim[-_]kho_tri_thuc|ma-nguon|tu-core-cu|tests-tu-core|"
    r"tham-chieu-cong-hien-tai|(?:^|[/\\])core(?:[/\\]|$)", re.I,
)


def _import_cam(ten):
    return ten.split(".")[0] == "kho_tri_thuc" or bool(set(ten.split(".")) & _TEN_CAM)


def kiem_doc_lap(thu_muc_goi=THU_MUC_GOI):
    goc = Path(thu_muc_goi)
    loi = []
    if not goc.is_dir() or goc.is_symlink():
        return ["Không tìm thấy thư mục gói độc lập hợp lệ."]
    duoc_import = sys.stdlib_module_names | {"e_hoa_don", "kho_tri_thuc_sdk"}
    for tep in sorted(goc.rglob("*")):
        ten = tep.relative_to(goc).as_posix()
        if tep.is_symlink() or (hasattr(tep, "is_junction") and tep.is_junction()):
            loi.append(f"{ten}: gói có liên kết tượng trưng hoặc junction.")
            continue
        if tep.name == "__pycache__" or tep.suffix.lower() in (".pyc", ".pyo"):
            loi.append(f"{ten}: gói có bytecode.")
        if not tep.is_file():
            continue
        if tep.stat().st_size > TEP_TOI_DA_BYTE:
            loi.append(f"{ten}: tệp vượt trần đóng gói 20 MiB.")
        if tep.suffix != ".py":
            continue
        try:
            cay = ast.parse(tep.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, SyntaxError):
            loi.append(f"{ten}: không phân tích được mã Python.")
            continue
        # Chỉ bỏ qua đúng literal GÁN __module__; không miễn import từ Core.
        dau_vet = {
            id(nut.value) for nut in ast.walk(cay)
            if isinstance(nut, ast.Assign)
            and isinstance(nut.value, ast.Constant) and nut.value.value == _DAU_VET
            and all(isinstance(t, ast.Attribute) and t.attr == "__module__" for t in nut.targets)
        }
        for nut in ast.walk(cay):
            def bao(cau):
                loi.append(f"{ten}:{getattr(nut, 'lineno', 0)}: {cau}")

            if isinstance(nut, (ast.Import, ast.ImportFrom)):
                if isinstance(nut, ast.Import):
                    modules = [m.name for m in nut.names]
                    symbols = []
                else:
                    modules = [nut.module or ""] if nut.level == 0 else []
                    symbols = [m.name for m in nut.names]
                for muc in modules:
                    if _import_cam(muc) or muc.split(".")[0] in _MODULE_CAM:
                        bao("import Core, loader động hoặc thư viện bị cấm.")
                    elif muc.split(".")[0] not in duoc_import:
                        bao("import thư viện ngoài SDK/stdlib.")
                    if "engine_legacy" in muc.split(".") and not (
                        isinstance(nut, ast.ImportFrom)
                        and muc == "kho_tri_thuc_sdk.engine_legacy" and symbols == ["Issue"]
                    ):
                        bao("engine_legacy chỉ được lấy Issue.")
                if any(m in _TEN_CAM | _DONG_CAM or m == "*" for m in symbols):
                    bao("import symbol cấm hoặc wildcard.")
            if isinstance(nut, ast.Name) and nut.id in _TEN_CAM | _DONG_CAM:
                bao("tham chiếu kênh cũ hoặc cơ chế thực thi/import động.")
            if isinstance(nut, ast.Attribute):
                if nut.attr in _TEN_CAM | (_DONG_CAM - {"compile"}):
                    bao("truy cập kênh cũ hoặc import động, kể cả qua alias.")
                if nut.attr in {"path", "modules", "meta_path"} and isinstance(nut.value, ast.Name):
                    # Chặn cả alias của sys khi sửa đường import/shim; XML không cần các cửa này.
                    aliases = {"sys"} | {
                        m.asname for n in ast.walk(cay) if isinstance(n, ast.Import)
                        for m in n.names if m.name == "sys" and m.asname
                    }
                    if nut.value.id in aliases:
                        bao("phụ thuộc/sửa đường import hoặc registry module.")
            if isinstance(nut, ast.Constant) and isinstance(nut.value, str):
                if nut.value in _TEN_CAM | _DONG_CAM:
                    bao("tên kênh cũ hoặc import động dưới dạng chuỗi.")
                if id(nut) not in dau_vet and _DUONG_CAM.search(nut.value):
                    bao("phụ thuộc tên/đường Core hoặc mã tham chiếu cũ.")
    return loi


def kiem_tien_trinh_sach(thu_muc_goi=THU_MUC_GOI):
    spec = importlib.util.find_spec("kho_tri_thuc_sdk")
    if spec is None or spec.origin is None:
        return ["Chưa cài SDK 2.0.0 để kiểm độc lập."]
    # -I -S loại cwd, PYTHONPATH, site-packages và .pth. SDK nạp bằng đường
    # package chính xác, không thêm cả site-packages vào đường tìm module.
    ma = r"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid
os.environ['KTT_ENGINE_CAU_HINH'] = str(Path(tempfile.gettempdir()) / ('thieu-DEMO-' + uuid.uuid4().hex))
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
cho_phep = sys.stdlib_module_names | {'e_hoa_don', 'kho_tri_thuc_sdk'}
def audit(su_kien, args):
    if su_kien == 'import' and args[0].split('.')[0] not in cho_phep:
        raise RuntimeError('Import ngoài SDK/stdlib/gói XML.')
    if su_kien in {'socket.connect', 'socket.bind', 'subprocess.Popen', 'os.system'}:
        raise RuntimeError('Gói XML không được gọi mạng hay tiến trình ngoài.')
sys.addaudithook(audit)
spec = importlib.util.spec_from_file_location('kho_tri_thuc_sdk', sys.argv[2],
    submodule_search_locations=[str(Path(sys.argv[2]).parent)])
sdk = importlib.util.module_from_spec(spec)
sys.modules['kho_tri_thuc_sdk'] = sdk
spec.loader.exec_module(sdk)
assert sdk.__version__ == '2.0.0'
from e_hoa_don.chay import app
from e_hoa_don import cau_hinh_may
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from e_hoa_don.hoa_don_xml import InvoiceIssue
from kho_tri_thuc_sdk.engine_legacy import Issue
from kho_tri_thuc_sdk.thu import CoreGia
assert cau_hinh_may.doc_cau_hinh() is None
try:
    cau_hinh_may.doc_cau_hinh(bat_buoc=True)
except LoiNghiepVu as loi:
    assert loi.ma == 'CHUA_CAU_HINH'
else:
    raise AssertionError('Thieu cau hinh phai tu choi')
assert type(InvoiceIssue('DEMO', 'Vấn đề DEMO.', '$', 'WARNING').as_issue()) is Issue
ket_qua = CoreGia().chay_thu_demo(app, sys.argv[1])
assert ket_qua and all(k['trang_thai'] == 'XONG' for k in ket_qua)
assert not any(n == 'kho_tri_thuc' or n.startswith('kho_tri_thuc.') for n in sys.modules)
print('DA_KIEM_DOC_LAP')
"""
    try:
        kq = subprocess.run(
            [sys.executable, "-I", "-B", "-S", "-c", ma,
             str(Path(thu_muc_goi).resolve()), str(Path(spec.origin).resolve())],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
            cwd=Path(thu_muc_goi).resolve(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return ["Không chạy được phép kiểm trong tiến trình sạch."]
    if kq.returncode != 0 or "DA_KIEM_DOC_LAP" not in kq.stdout:
        return ["Import/DEMO trong tiến trình sạch không đạt; không dùng Core/shim để bù."]
    return []


def main():
    loi = kiem_doc_lap()
    if not loi:
        loi += kiem_tien_trinh_sach()
    for muc in loi:
        print(f"[LỖI] {muc}")
    if not loi:
        print("[ĐẠT] AST/import (kể cả lazy/dynamic), cây gói và tiến trình sạch; đã kiểm bằng Core giả (CoreGia).")
    return 1 if loi else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
