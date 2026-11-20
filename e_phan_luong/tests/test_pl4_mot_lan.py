"""PL-4 lead: hồ sơ hành vi cộng đúng một lần khi Core giao lại việc.

Đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO. Hồ sơ được cộng trong
CÙNG lô nguyên tử với dấu luot: lô cuối lỗi thì cả hai chưa ghi; lượt đã có
dấu luot thì giao lại không cộng thêm.
"""
from copy import copy

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau
from e_phan_luong.chay import app
from test_pl2_ngan_luot import chay_ngan
from test_pl2_phan_luong import HG, lo_mot
from test_pl3_ngan_ket_qua import ma_hoa
from test_pl4_sua_ra import _chay_trong_viec


def so_nghiep_vu(core):
    return {(b["khau"], b["loai"]): int(b["so_nghiep_vu"]) for b in core.xem_ngan(app.ma, "ho_so_hanh_vi")}


@pytest.fixture(autouse=True)
def ghim(monkeypatch):
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HG)


def test_giao_lai_sau_khi_xong_khong_cong_ho_so_lan_hai():
    core = CoreGia()
    raw = ma_hoa(lo_mot(doi_tac="DEMO-NCC-01"))

    def kiem(viec):
        _chay_trong_viec(core, viec, raw)
        sau_lan_1 = so_nghiep_vu(core)
        assert list(sau_lan_1.values()) == [1]
        giao_lai = copy(viec)
        giao_lai.lan_thu += 1
        _chay_trong_viec(core, giao_lai, raw)
        assert so_nghiep_vu(core) == sau_lan_1

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    assert len(core.xem_ngan(app.ma, "luot")) == 1


def test_lo_cuoi_loi_thi_chua_co_luot_va_chua_cong_roi_giao_lai_cong_mot_lan():
    core = CoreGia()
    raw = ma_hoa(lo_mot(doi_tac="DEMO-NCC-01"))

    def kiem(viec):
        # Mọi lô chạm bảng luot xung đột 4 lần → NGAN_BAN; lô cuối nguyên tử.
        core.gay_xung_dot_ngan("luot", so_lan=4)
        with pytest.raises(LoiNghiepVu) as loi:
            _chay_trong_viec(core, viec, raw)
        assert loi.value.ma == "NGAN_BAN"
        assert core.xem_ngan(app.ma, "luot") == []
        assert list(so_nghiep_vu(core).values()) == [0]  # chỉ có hồ sơ rỗng tạo trước
        giao_lai = copy(viec)
        giao_lai.lan_thu += 1
        _chay_trong_viec(core, giao_lai, raw)
        assert list(so_nghiep_vu(core).values()) == [1]
        assert len(core.xem_ngan(app.ma, "luot")) == 1

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"


def test_ho_so_xung_dot_o_lo_cuoi_thi_doc_lai_va_cong_dung_mot_lan():
    core = CoreGia()
    raw = ma_hoa(lo_mot(doi_tac="DEMO-NCC-01"))

    def kiem(viec):
        _chay_trong_viec(core, viec, raw)

    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    # Việc thứ hai, cùng tệp: một xung đột hồ sơ ở lô cuối → đọc lại, vẫn cộng một lần.
    core.gay_xung_dot_ngan("ho_so_hanh_vi", so_lan=1)
    assert chay_ngan(core, kiem)["trang_thai"] == "XONG"
    assert list(so_nghiep_vu(core).values()) == [2]
    assert len(core.xem_ngan(app.ma, "luot")) == 2
