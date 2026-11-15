"""Khóa SDK 2.0.0 và kiểm log an toàn qua đầy đủ vòng CoreGia."""

from inspect import signature

import pytest
import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import tao_app


def test_chot_sdk_va_chu_ky_hai_hook_noi_bo():
    assert kho_tri_thuc_sdk.__version__ == "2.0.0"
    assert str(signature(Engine._ghi)) == "(self, cau)"
    assert str(signature(Engine._ket_thuc)) == (
        "(self, dt, viec, cfg, trang_thai, *, loi=None, ma_tuong_quan=None)")


@pytest.mark.parametrize("doi", ["phien_ban", "ghi", "ket_thuc"])
def test_sdk_doi_thi_khong_khoi_dong(monkeypatch, doi):
    if doi == "phien_ban":
        monkeypatch.setattr(kho_tri_thuc_sdk, "__version__", "2.0.1")
    else:
        monkeypatch.setattr(Engine, "_ghi" if doi == "ghi" else "_ket_thuc", lambda self: None)
    with pytest.raises(RuntimeError, match="SDK đã thay đổi"):
        tao_app()


def test_runtimeerror_bi_mat_demo_qua_coregia_khong_lo_stderr(capsys):
    app, core = tao_app(), CoreGia()
    bi_mat = "DEMO_BI_MAT_KHONG_DUOC_XUAT_HIEN"
    def handler(viec):
        raise RuntimeError(bi_mat)
    app._ham["trich.doc_docx@1"] = handler
    tep = core.them_tep("DEMO.docx", b"DEMO", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    capsys.readouterr()
    kq = core.chay_thu(app, "trich.doc_docx@1", {"loai": "tep", "tep": tep})
    err = capsys.readouterr().err
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "ENGINE_LOI_XU_LY"
    assert bi_mat not in err and "Traceback" not in err and "ENGINE_LOI_XU_LY" in err
    assert bi_mat not in str(kq)


def test_log_sdk_chi_co_ma_loi_van_giu_chan_doan(capsys):
    app = tao_app()
    capsys.readouterr()
    cau = "Lỗi trao đổi với Core khi làm việc viec-DEMO: MAT_PHAN_HOI."
    app._ghi(cau)
    assert capsys.readouterr().err == f"[engine e_trich_xuat] {cau}\n"
