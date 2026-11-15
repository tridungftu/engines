"""Máy sạch TC-10: venv tạm chỉ SDK wheel repo, offline, không bytecode.

Mã thoát giữ kết quả CLI chuẩn, kể cả lỗi cấu hình đã biết. Không tự tiêm
DEMO/cấu hình để làm CLI xanh. Pytest/harness có dependency test chạy riêng.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


REPO = Path(__file__).resolve().parents[2]
GOI = REPO / "e_tra_cuu/goi/e_tra_cuu"
SDK = REPO / "docs/goi-gui-engine/sdk-2.2.0"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bao-cao", type=Path, help="Artifact DEMO ngoài runtime engine.")
    args = p.parse_args(argv)
    wheel = SDK / "kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
    checksum = sha256(wheel.read_bytes()).hexdigest()
    assert f"{checksum}  {wheel.name}" in (SDK / "SHA256SUMS.txt").read_text(encoding="ascii")
    env = {k: v for k, v in os.environ.items() if k not in {
        "PYTHONPATH", "KTT_CORE_URL", "KTT_ENGINE_KHOA", "KTT_ENGINE_INSTANCE"}}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1")

    def chay(cmd, cwd):
        return subprocess.run(cmd, cwd=cwd, env=env, text=True, encoding="utf-8",
                              errors="replace", capture_output=True, timeout=120)

    report = {"nhan": "DEMO", "he_dieu_hanh": platform.system(), "python": platform.python_version(),
        "sdk": "2.2.0", "bam_wheel": checksum, "offline": True, "moi_truong_tach_biet": True,
        "harness_may_sach": {"trang_thai": "chua_kiem", "ly_do": "Máy sạch chỉ cài SDK. Harness/pytest dùng dependency test đã ghim và được chạy riêng."},
        "core_that": "chua_kiem", "linux": "chua_kiem" if platform.system() != "Linux" else "da_chay"}
    # Thư mục do công cụ tạo trong workspace; TemporaryDirectory dọn trong finally.
    # Không xóa/move bất kỳ tệp nguồn hoặc venv sẵn có nào của người dùng.
    with TemporaryDirectory(prefix=".tc10-may-sach-", dir=REPO) as tam:
        goc_tam = Path(tam).resolve()
        assert goc_tam.is_relative_to(REPO.resolve()) and goc_tam.name.startswith(".tc10-may-sach-")
        venv = goc_tam / "venv"
        tao = chay([sys.executable, "-B", "-m", "venv", str(venv)], REPO)
        if tao.returncode:
            print("[LỖI] Chưa tạo được môi trường kiểm độc lập.")
            return 2
        py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        cai = chay([str(py), "-B", "-m", "pip", "install", "--no-index", "--no-deps", "--no-compile",
                    "--require-hashes", "--find-links", str(SDK), "-r", str(GOI / "requirements.lock")], REPO)
        if cai.returncode:
            print("[LỖI] Chưa cài được SDK offline theo lock và băm.")
            return 2
        staging = goc_tam / "goi"
        shutil.copytree(GOI, staging)
        nhap = chay([str(py), "-I", "-B", "-c", '''
import importlib.metadata as m
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from e_tra_cuu.chay import app
import kho_tri_thuc_sdk
assert kho_tri_thuc_sdk.__version__ == '2.2.0'
assert {d.metadata['Name'].lower().replace('-', '_') for d in m.distributions()} <= {'pip', 'setuptools', 'kho_tri_thuc_sdk'}
assert len(app.phieu['nang_luc']) == 8 and len(app.phieu['chay_thu_demo']) == 12
print('Da kiem import doc lap; SDK 2.2.0; 8 nang luc; 12 DEMO.')
'''], staging)
        cli = chay([str(py), "-B", "-m", "kho_tri_thuc_sdk.thu", str(staging)], goc_tam)
        bytecode = [f for f in staging.rglob("*") if f.name == "__pycache__" or f.suffix == ".pyc"]
        report.update(cai_sdk_ma_thoat=cai.returncode, import_ma_thoat=nhap.returncode,
            so_bytecode_trong_goi=len(bytecode), cli_chuan={"ma_thoat": cli.returncode,
                "tu_so": cli.stdout.count("[ĐẠT]"), "mau_so": 12,
                "so_loi_chua_cau_hinh": (cli.stdout + cli.stderr).count("Engine chưa được cấu hình."),
                "so_loi_chua_co_cua_core": (cli.stdout + cli.stderr).count("Core chưa cấp đủ cửa nguồn và quyền tra cứu."),
                "can_cu_ma_loi": "Đếm thông điệp CLI; test CoreGia/HTTP đối chiếu mã CHUA_CAU_HINH và TC_CHUA_CO_CUA_CORE."})
        nhan = "ĐẠT" if nhap.returncode == 0 and not bytecode else "LỖI"
        print(f'[{nhan}] Cài SDK offline theo băm; import độc lập={nhap.returncode}; bytecode trong gói={len(bytecode)}.')
        print(f'CLI chuẩn: {report["cli_chuan"]["tu_so"]}/12; mã {cli.returncode}; '
              f'CHUA_CAU_HINH={report["cli_chuan"]["so_loi_chua_cau_hinh"]}; '
              f'TC_CHUA_CO_CUA_CORE={report["cli_chuan"]["so_loi_chua_co_cua_core"]}.')
        code = cli.returncode if nhap.returncode == 0 and not bytecode else 2
    # Đã dọn staging/venv trước khi xuất artifact bên ngoài gói.
    report["da_don_tam"] = not goc_tam.exists()
    if args.bao_cao:
        args.bao_cao.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print("Đã kiểm bằng Core giả (CoreGia); CLI chưa đạt khi thiếu cấu hình/cửa nguồn. Không kích hoạt nhóm.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
