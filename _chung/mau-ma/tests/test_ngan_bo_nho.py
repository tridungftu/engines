"""Giới hạn, lỗi đầu vào và lựa chọn bản RAM tạm thời."""

from types import SimpleNamespace
from datetime import date, timedelta

import pytest

import ngan as mau_ngan
from ngan import NganBoNho, NganKhongHopLe


@pytest.mark.parametrize("gioi_han", [0, -1, 501, True, 1.5, "10"])
def test_tu_choi_gioi_han_tim(ngan, gioi_han):
    with pytest.raises(NganKhongHopLe):
        ngan.tim("han_muc", gioi_han=gioi_han)


def test_tran_lo_100_khong_cat_ngam(ngan):
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            for i in range(101):
                lo.them("han_muc", {"ngay": (date(2026, 11, 15) + timedelta(days=i)).isoformat()}, {"so_trang": 1})
    assert ngan.tim("han_muc").danh_sach == []
    with ngan.lo() as lo:
        for i in range(100):
            lo.them("han_muc", {"ngay": (date(2026, 11, 15) + timedelta(days=i)).isoformat()}, {"so_trang": 1})
    assert len(ngan.tim("han_muc").danh_sach) == 100


def test_khong_the_nuot_loi_tran_de_ghi_mot_phan(ngan):
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            for i in range(100):
                lo.them("han_muc", {"ngay": (date(2026, 11, 15) + timedelta(days=i)).isoformat()}, {"so_trang": 1})
            with pytest.raises(NganKhongHopLe):
                lo.them("han_muc", {"ngay": "2027-12-31"}, {})
    assert ngan.tim("han_muc").danh_sach == []


@pytest.mark.parametrize("khoa", [{"ma": "DEMO"}, {"bam": "DEMO"}, {}])
def test_phap_nhan_thieu_ngu_canh_bi_tu_choi(ngan, khoa):
    with pytest.raises(NganKhongHopLe):
        ngan.doc("luot", khoa)
    with pytest.raises(NganKhongHopLe):
        ngan.tim("luot")


@pytest.mark.parametrize("thao_tac", ["doc", "tim", "them", "sua", "xoa", "lay_hoac_tao"])
def test_khong_gia_mao_phap_nhan_trong_lenh(ngan, thao_tac):
    a = ngan.cho_phap_nhan("DEMO-A")
    khoa = {"ma": "DEMO-1", "phap_nhan_id": "DEMO-B"}
    with pytest.raises(NganKhongHopLe):
        if thao_tac == "doc":
            a.doc("luot", khoa)
        elif thao_tac == "tim":
            a.tim("luot", {"phap_nhan_id": "DEMO-B"})
        else:
            with a.lo() as lo:
                if thao_tac == "xoa":
                    lo.xoa("luot", khoa, row_version=1)
                elif thao_tac == "sua":
                    lo.sua("luot", khoa, {}, row_version=1)
                else:
                    getattr(lo, thao_tac)("luot", khoa, {"bam": "DEMO"})
    assert a.tim("luot").danh_sach == []


def test_khong_gia_mao_phap_nhan_trong_gia_tri(ngan):
    with pytest.raises(NganKhongHopLe):
        with ngan.cho_phap_nhan("DEMO-A").lo() as lo:
            lo.them("luot", {"ma": "DEMO"}, {"bam": "DEMO", "phap_nhan_id": "DEMO-B"})


def test_con_tro_gan_voi_truy_van_va_phap_nhan(ngan):
    a, b = ngan.cho_phap_nhan("DEMO-A"), ngan.cho_phap_nhan("DEMO-B")
    with a.lo() as lo:
        for i in range(3):
            lo.them("luot", {"ma": f"DEMO-{i}"}, {"bam": f"DEMO-{i}"})
    trang = a.tim("luot", gioi_han=1)
    assert trang.tiep is not None
    for xem, bang, loc, tiep in [
        (b, "luot", {}, trang.tiep), (a, "luot", {"bam": "DEMO"}, trang.tiep),
        (a, "han_muc", {}, trang.tiep), (a, "luot", {}, "DEMO-sai"),
        (a, "luot", {}, trang.tiep[:-4] + "AAAA"),
    ]:
        with pytest.raises(NganKhongHopLe):
            xem.tim(bang, loc=loc, tiep=tiep)


@pytest.mark.parametrize("version", [None, True, 0, -1, "1", 1.5])
def test_cas_bat_buoc_phien_ban_hop_le(ngan, version):
    with ngan.lo() as lo:
        lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 1})
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            lo.sua("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 2}, row_version=version)
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}).gia_tri["so_trang"] == 1


def test_khong_sua_khoa_chinh_qua_khoa_duy_nhat(ngan):
    with ngan.lo() as lo:
        cu = lo.them("danh_muc", {"ma": "DEMO"}, {"bam": "DEMO", "bi_danh": "DEMO"})
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            lo.sua("danh_muc", {"bam": "DEMO"}, {"ma": "DEMO-moi"}, row_version=cu.row_version)
    assert ngan.doc("danh_muc", {"ma": "DEMO"}) is not None


@pytest.mark.parametrize("gia_tri", [{"so": float("nan")}, {"so": float("inf")}, {1: "DEMO"}, {"DEMO": object()}])
def test_tu_choi_du_lieu_khong_phai_json(ngan, gia_tri):
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            lo.them("han_muc", {"ngay": "2026-11-15"}, gia_tri)
    assert ngan.tim("han_muc").danh_sach == []


def test_ket_qua_chua_commit_va_lo_that_bai_khong_bao_thanh_cong(ngan):
    with pytest.raises(RuntimeError):
        with ngan.lo() as lo:
            kq = lo.them("han_muc", {"ngay": "2026-11-15"}, {})
            with pytest.raises(NganKhongHopLe):
                _ = kq.da_tao
            raise RuntimeError("DEMO")
    with pytest.raises(NganKhongHopLe):
        _ = kq.row_version


def test_lenh_sai_khi_commit_huy_cac_lenh_truoc(ngan):
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            kq = lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 1})
            # Thiếu các trường trong ràng buộc duy nhất đã khai.
            lo.them("danh_muc", {"ma": "DEMO"}, {})
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}) is None
    with pytest.raises(NganKhongHopLe):
        _ = kq.da_tao


def test_lo_khong_tai_su_dung_va_khong_ghi_ngoai_with(ngan):
    lo = ngan.lo()
    with pytest.raises(NganKhongHopLe):
        lo.them("han_muc", {"ngay": "2026-11-15"}, {})
    with ngan.lo() as xong:
        pass
    with pytest.raises(NganKhongHopLe):
        with xong:
            pass
    with pytest.raises(NganKhongHopLe):
        xong.__exit__(None, None, None)


def test_khai_bao_config_va_ngan_khac_nhau_doc_lap():
    a = NganBoNho([{"bang": "cau_hinh", "khoa": [], "pham_vi": "engine"}])
    b = NganBoNho()
    with a.lo() as lo:
        lo.them("cau_hinh", {}, {"DEMO": True})
    assert b.doc("cau_hinh", {}) is None


def test_chon_ngan_sdk_that_ke_ca_doi_tuong_falsy(monkeypatch, capsys):
    class NganSDKGia:
        def __bool__(self):
            return False
    that = NganSDKGia()
    monkeypatch.setattr(mau_ngan, "_DA_CANH_BAO", False)
    assert mau_ngan.chon_ngan(SimpleNamespace(ngan=that)) is that
    assert capsys.readouterr().err == ""


def test_chon_ngan_ram_mot_lan_canh_bao_giu_cung_ngan(monkeypatch, capsys):
    monkeypatch.setattr(mau_ngan, "_DA_CANH_BAO", False)
    app = SimpleNamespace(phieu={"ngan_du_lieu": [{"bang": "han_muc", "khoa": ["ngay"]}]})
    a = mau_ngan.chon_ngan(app)
    assert mau_ngan.chon_ngan(app) is a
    assert mau_ngan.chon_ngan(SimpleNamespace()) is not a
    assert capsys.readouterr().err.count("Đang lưu tạm trong bộ nhớ") == 1
