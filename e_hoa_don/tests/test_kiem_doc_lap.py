"""Kiểm công cụ phát hiện cả import ẩn và tên legacy không có tác dụng shim."""

from pathlib import Path

import pytest

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
