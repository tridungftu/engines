"""Tiện ích ngăn đã kiểm bằng Core giả (CoreGia), không dùng Core thật."""

from copy import deepcopy

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong.chay import app
from e_phan_luong.loi import CAU_LOI
from e_phan_luong.ngan_chung import ghi_lay_hoac_tao_nhieu, ghi_lo_thu_lai, tim_tat_ca


def chay_ngan(core, ham):
    """App test có cùng khai báo ngăn; không thay hàm tạm của gói runtime."""
    phieu = deepcopy(app.phieu)
    nl = phieu["nang_luc"][0]
    nl.update(nhan=["van_ban"], tra="van_ban")
    nl.pop("truong_ra")
    phieu["nang_luc"] = [nl]
    thu = Engine(phieu)

    @thu.nang_luc(nl["ma"])
    def kiem(viec):
        ham(viec)
        return {"loai": "van_ban", "van_ban": "DEMO"}

    return core.chay_thu(thu, nl["ma"], {"loai": "van_ban", "van_ban": "DEMO"},
                         {"khau": "ktt_duyet"})


def ds_dong(n):
    return [({"ma_luot": "PL-DEMO", "ma": f"PC-DEMO-{i:06}"},
             {"ma_module": "demo_thanh_toan", "khau": "ktt_duyet", "ly_do": "KHONG_CHON"})
            for i in range(n)]


def test_dung_mot_lan_thu_lai_va_doc_lai_cas():
    core = CoreGia()
    khoa = {"khau": "ktt_duyet", "loai": "chi_phi_demo"}
    lan_doc = []
    so_thu_lai = []

    def ham(viec):
        ghi_lay_hoac_tao_nhieu(viec, "ty_le", [(khoa, {"mau_12t": 0})])
        core.gay_xung_dot_ngan("ty_le", so_lan=1)

        def lap(lo):
            ban_ghi = viec.ngan.doc("ty_le", khoa)
            lan_doc.append(ban_ghi.row_version)
            lo.sua("ty_le", khoa, {"mau_12t": int(ban_ghi.gia_tri["mau_12t"]) + 1},
                   row_version=ban_ghi.row_version)
            # Phải cùng lô CAS: xung đột không để lại dòng dở dang.
            lo.lay_hoac_tao("dong_luot", *ds_dong(1)[0])

        so_thu_lai.append(ghi_lo_thu_lai(viec, lap))

    kq = chay_ngan(core, ham)
    assert kq["trang_thai"] == "XONG", kq
    assert so_thu_lai == [1]
    assert len(lan_doc) == 2
    assert core.xem_ngan(app.ma, "ty_le")[0]["mau_12t"] == "1"
    assert len(core.xem_ngan(app.ma, "dong_luot")) == 1


def test_ngan_ban_sau_bon_lan_xung_dot_khong_ghi_do_dang():
    core = CoreGia()
    core.gay_xung_dot_ngan("dong_luot", so_lan=4)
    so_goi = []

    def ham(viec):
        def lap(lo):
            so_goi.append(1)
            lo.lay_hoac_tao("dong_luot", *ds_dong(1)[0])
        ghi_lo_thu_lai(viec, lap)

    kq = chay_ngan(core, ham)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"] == {"ma": "NGAN_BAN", "thong_diep": CAU_LOI["NGAN_BAN"], "thu_lai_duoc": True}
    assert len(so_goi) == 4
    assert core.xem_ngan(app.ma, "dong_luot") == []


def test_ba_lan_xung_dot_van_thanh_cong_lan_thu_tu():
    core = CoreGia()
    core.gay_xung_dot_ngan("dong_luot", so_lan=3)
    ds = []

    def ham(viec):
        ds.append(ghi_lo_thu_lai(viec, lambda lo: lo.lay_hoac_tao("dong_luot", *ds_dong(1)[0])))

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"
    assert ds == [3]


@pytest.mark.parametrize("n,so_lo", [(0, 0), (1, 1), (100, 1), (101, 2), (205, 3)])
def test_chia_lo_khong_qua_100_va_nop_lai_khong_trung(n, so_lo):
    core = CoreGia()
    ds = ds_dong(n)
    ban_sao = deepcopy(ds)

    def ham(viec):
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", ds)

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"
    assert len([l for l in core.nhat_ky if l[0] == "ngan"]) == so_lo
    assert chay_ngan(core, ham)["trang_thai"] == "XONG"
    assert len(core.xem_ngan(app.ma, "dong_luot")) == n
    assert ds == ban_sao


def test_phan_trang_loc_day_du_va_bien_tran():
    core = CoreGia()

    def ham(viec):
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", ds_dong(205))
        khoa, gia_tri = ds_dong(1)[0]
        khoa = dict(khoa, ma_luot="PL-DEMO-khac")
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", [(khoa, gia_tri)])
        loc = {"ma_luot": "PL-DEMO"}
        for gioi_han in (1, 100, 500):
            ds = tim_tat_ca(viec, "dong_luot", loc, gioi_han=gioi_han, toi_da=205)
            assert {d.gia_tri["ma"] for d in ds} == {k["ma"] for k, _ in ds_dong(205)}
        assert loc == {"ma_luot": "PL-DEMO"}
        assert tim_tat_ca(viec, "dong_luot", {"ma_luot": "PL-DEMO-rong"}, toi_da=0) == []
        with pytest.raises(LoiNghiepVu) as exc:
            tim_tat_ca(viec, "dong_luot", loc, gioi_han=100, toi_da=204)
        assert exc.value.ma == "VUOT_GIOI_HAN"

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"


def test_khong_thu_lai_loi_nghiep_vu_khac_va_huy_viec():
    core = CoreGia()
    so_goi = []

    def ham(viec):
        def lap(lo):
            so_goi.append(1)
            lo.lay_hoac_tao("dong_luot", *ds_dong(1)[0])
            raise LoiNghiepVu("DEMO", "Lỗi DEMO.")
        with pytest.raises(LoiNghiepVu, match="Lỗi DEMO"):
            ghi_lo_thu_lai(viec, lap)
        with pytest.raises(ViecDaHuy):
            def huy(lo):
                raise ViecDaHuy()
            ghi_lo_thu_lai(viec, huy)
        with pytest.raises(LoiNghiepVu):
            ghi_lo_thu_lai(viec, lap, so_lan_thu_lai=-1)
        with pytest.raises(LoiNghiepVu):
            tim_tat_ca(viec, "dong_luot", {}, gioi_han=501)

    assert chay_ngan(core, ham)["trang_thai"] == "XONG"
    assert len(so_goi) == 1
    assert core.xem_ngan(app.ma, "dong_luot") == []
