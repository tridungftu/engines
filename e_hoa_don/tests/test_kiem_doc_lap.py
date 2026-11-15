"""Kiểm công cụ phát hiện cả import ẩn và tên legacy không có tác dụng shim."""

from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

import kiem_doc_lap as bo_kiem
from kiem_doc_lap import THU_MUC_GOI, TEP_TOI_DA_BYTE, kiem_doc_lap, kiem_tien_trinh_sach


def goi_demo(tmp_path, ma):
    goi = tmp_path / "goi-DEMO"
    goi.mkdir()
    (goi / "DEMO.py").write_text(ma, encoding="utf-8")
    return goi


def test_goi_that_ast_va_tien_trinh_sach():
    assert kiem_doc_lap() == []
    assert kiem_tien_trinh_sach() == []
    assert len(list((THU_MUC_GOI / "e_hoa_don").glob("*.py"))) == 5


@pytest.mark.parametrize("ma", [
    "import kho_tri_thuc.nguon.hoa_don_xml",
    "def lazy():\n    from kho_tri_thuc.sdk_core.primitives import DataError",
    "from kho_tri_thuc_sdk.engine import SDKEngine",
    "from kho_tri_thuc_sdk import Bootstrap",
    "import kenh_engine",
    "from kho_tri_thuc_sdk.engine_legacy import TrangThaiEngine",
    "from kho_tri_thuc_sdk.engine_legacy import *",
    "__import__('kho_tri_thuc' + '.nguon')",
    "f = __import__\nf('kho_tri_thuc')",
    "import importlib as il\nil.import_module('kho_' + 'tri_thuc')",
    "from importlib import import_module as nap\nnap('kho_tri_thuc.nguon')",
    "import builtins as b\ngetattr(b, '__import__')('kho_tri_thuc')",
    "import sys as s\ns.path.insert(0, 'shim-kho_tri_thuc')",
    "import sys\nsys.modules['kho_tri_thuc'] = None",
    "from sys import path as duong\nduong.insert(0, 'DEMO')",
    "import pickle",
    "import thu_vien_chua_ghim",
    "import importlib\nimportlib.import_module(ten_khong_biet)",
    "duong = '../tu-core-cu/src'",
    # Literal provenance không biến import Core kế tiếp thành hợp lệ.
    "Lop.__module__ = 'kho_tri_thuc.nguon.hoa_don_xml'\nimport kho_tri_thuc.nguon.hoa_don_xml",
])
def test_bat_import_cam_ke_ca_lazy_dynamic(tmp_path, ma):
    assert kiem_doc_lap(goi_demo(tmp_path, ma))


def test_cho_phep_dau_vet_va_lazy_issue_sdk(tmp_path):
    ma = "Lop.__module__ = 'kho_tri_thuc.nguon.hoa_don_xml'\ndef lazy():\n    from kho_tri_thuc_sdk.engine_legacy import Issue"
    assert kiem_doc_lap(goi_demo(tmp_path, ma)) == []


@pytest.mark.parametrize("duong", ["__pycache__", "DEMO.pyc", "DEMO.pyo"])
def test_cam_bytecode(tmp_path, duong):
    goi = goi_demo(tmp_path, "")
    if duong == "__pycache__":
        (goi / duong).mkdir()
    else:
        (goi / duong).write_bytes(b"DEMO")
    assert kiem_doc_lap(goi)


def test_cam_tep_lon_khong_commit_tep_lon(tmp_path):
    goi = goi_demo(tmp_path, "")
    with (goi / "lon-DEMO.bin").open("wb") as f:
        f.truncate(TEP_TOI_DA_BYTE + 1)
    assert any("20 MiB" in loi for loi in kiem_doc_lap(goi))


def test_cam_symlink_bang_mock_khong_can_quyen_windows(tmp_path, monkeypatch):
    goi = goi_demo(tmp_path, "")
    tep = goi / "lien-ket-DEMO"
    tep.write_bytes(b"DEMO")
    cu = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda p: p == tep or cu(p))
    assert any("liên kết" in loi for loi in kiem_doc_lap(goi))


def chen_ma_sau_audit(monkeypatch, ma):
    """Chạy tiến trình thật, thêm tình huống DEMO ngay sau khi bật audit hook."""
    chay = subprocess.run

    def chay_demo(lenh, **tham_so):
        lenh = list(lenh)
        assert lenh[1:5] == ["-I", "-B", "-S", "-c"]
        lenh[5] = lenh[5].replace(
            "sys.addaudithook(audit)", "sys.addaudithook(audit)\n" + ma, 1,
        )
        return chay(lenh, **tham_so)

    monkeypatch.setattr(bo_kiem.subprocess, "run", chay_demo)


def test_do_jython_cua_copy_python_311_van_chay_demo(monkeypatch):
    # Phép dò trong Lib/copy.py CPython 3.11.18; 3.13 đã bỏ nhánh Jython.
    # Không thêm org vào allowlist hoặc nạp trước copy để né kiểm import.
    chen_ma_sau_audit(monkeypatch, """
try:
    from org.python.core import PyStringMap
except ImportError:
    PyStringMap = None
assert PyStringMap is None
assert not any(n == 'org' or n.startswith('org.') for n in sys.modules)
""")
    assert kiem_tien_trinh_sach() == []


@pytest.mark.parametrize("ten", ["org", "kho_tri_thuc", "thu_vien_chua_ghim"])
def test_audit_van_chan_module_ngoai_du_co_tep(tmp_path, monkeypatch, ten):
    goi = goi_demo(tmp_path, "")
    (goi / (ten + ".py")).write_text("DEMO = True\n", encoding="utf-8")
    chen_ma_sau_audit(monkeypatch, f"import {ten}\nraise AssertionError('Da lot import cam')")
    loi = kiem_tien_trinh_sach(goi)
    assert len(loi) == 1 and "ModuleNotFoundError" in loi[0]
    assert "mã thoát 1" in loi[0]


@pytest.mark.parametrize("su_kien", [
    "socket.connect", "socket.bind", "subprocess.Popen", "os.system",
])
def test_audit_van_chan_mang_va_tien_trinh(monkeypatch, su_kien):
    # Phát sự kiện kiểm chính sách, không thực sự gọi mạng/tiến trình ngoài.
    chen_ma_sau_audit(monkeypatch, f"sys.audit('{su_kien}')")
    assert "RuntimeError" in kiem_tien_trinh_sach()[0]


@pytest.mark.parametrize(("ma_thoat", "stderr", "ly_do"), [
    (1, 'File "/DEMO/hoa-don.xml"\nSyntaxError: CANARY_HOA_DON_DEMO', "SyntaxError"),
    (1, r'ValueError: C:\DEMO\hoa-don.xml CANARY_HOA_DON_DEMO', "ValueError"),
    (1, "CANARY_HOA_DON_DEMO: /DEMO/hoa-don.xml", "HD_SACH_KHONG_RO_LOI"),
    (0, "", "HD_SACH_THIEU_XAC_NHAN"),
])
def test_chan_doan_khong_lo_noi_dung_hoac_duong_dan(monkeypatch, ma_thoat, stderr, ly_do):
    monkeypatch.setattr(bo_kiem.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=ma_thoat, stdout="CANARY_HOA_DON_DEMO", stderr=stderr,
    ))
    loi = kiem_tien_trinh_sach()
    assert len(loi) == 1 and ly_do in loi[0]
    assert f"mã thoát {ma_thoat}" in loi[0]
    assert all(c not in loi[0] for c in ("CANARY_HOA_DON_DEMO", "/DEMO/hoa-don.xml", "C:\\DEMO"))


@pytest.mark.parametrize(("loi_chay", "ly_do"), [
    (OSError("/DEMO/CANARY_HOA_DON_DEMO"), "HD_SACH_KHONG_CHAY_DUOC; OSError"),
    (subprocess.TimeoutExpired("CANARY_HOA_DON_DEMO", 30), "HD_SACH_QUA_HAN; TimeoutExpired"),
])
def test_chan_doan_loi_khoi_chay_va_qua_han(monkeypatch, loi_chay, ly_do):
    def khong_chay(*args, **kwargs):
        raise loi_chay

    monkeypatch.setattr(bo_kiem.subprocess, "run", khong_chay)
    loi = kiem_tien_trinh_sach()
    assert len(loi) == 1 and ly_do in loi[0]
    assert "CANARY_HOA_DON_DEMO" not in loi[0] and "/DEMO" not in loi[0]
