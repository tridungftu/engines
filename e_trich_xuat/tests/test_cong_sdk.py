"""Kiểm cửa công khai và log an toàn qua đầy đủ vòng CoreGia."""

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import GOC_GOI, tao_app


def test_khoi_dong_bang_engine_cong_khai():
    app = tao_app()
    assert type(app) is Engine
    core = CoreGia()
    tep = core.them_tep("DEMO.docx", (GOC_GOI / "demo/DEMO-hop-dong.docx").read_bytes(),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert core.chay_thu(app, "trich.doc_docx@1", {"loai": "tep", "tep": tep})["trang_thai"] == "XONG"


def app_loi(ham):
    phieu = tao_app().phieu
    phieu.update(nang_luc=[{"ma": "demo.loi@1", "ten": "Lỗi DEMO",
        "nhan": ["van_ban"], "tra": "van_ban", "gioi_han": {"thoi_han_giay": 10}}],
        chay_thu_demo=[])
    app = Engine(phieu, thu_muc_goi=GOC_GOI)
    app.nang_luc("demo.loi@1")(ham)
    return app


@pytest.mark.parametrize("loai_loi", [RuntimeError, ValueError, OSError])
def test_loi_bat_ngo_demo_qua_coregia_khong_lo_stderr(capsys, loai_loi):
    core = CoreGia()
    bi_mat = "DEMO_BI_MAT_KHONG_DUOC_XUAT_HIEN"
    def handler(viec):
        raise loai_loi(bi_mat)
    app = app_loi(handler)
    capsys.readouterr()
    kq = core.chay_thu(app, "demo.loi@1", {"loai": "van_ban", "van_ban": "DEMO"})
    err = capsys.readouterr().err
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "ENGINE_LOI_XU_LY"
    assert bi_mat not in err and "Traceback" not in err and loai_loi.__name__ in err
    assert bi_mat not in str(kq)


def test_loi_nghiep_vu_giu_ma_va_cau_cong_khai():
    def handler(viec):
        raise LoiNghiepVu("DEMO_TU_CHOI", "Tệp DEMO không hợp lệ.")
    kq = CoreGia().chay_thu(app_loi(handler), "demo.loi@1", {"loai": "van_ban", "van_ban": "DEMO"})
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"] == {"ma": "DEMO_TU_CHOI", "thong_diep": "Tệp DEMO không hợp lệ.", "thu_lai_duoc": False}
