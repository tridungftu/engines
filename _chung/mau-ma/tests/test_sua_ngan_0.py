"""Hồi quy kiểm độc lập NGAN-0: phạm vi, chỉ mục, JSON và hiệu năng."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import perf_counter

import pytest

from kiem_doc_lap import kiem_doc_lap
from ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan


def test_kiem_doc_lap_duoc_pytest_thu_thap():
    assert kiem_doc_lap() == []


def test_ngan_goc_dung_dung_vi_du_dac_ta(tao_ngan):
    app_ngan = tao_ngan([{
        "bang": "luot_abbyy", "khoa": ["ma_tuong_quan"], "pham_vi": "phap_nhan",
        "duy_nhat": [["phap_nhan_id", "bam_noi_dung"]],
    }])
    for p in ("DEMO-P", "DEMO-Q"):
        with app_ngan.lo() as lo:
            kq = lo.lay_hoac_tao("luot_abbyy", {"phap_nhan_id": p, "bam_noi_dung": "DEMO-bam"},
                                 {"ma_tuong_quan": "DEMO-1", "so_trang": 1})
        assert kq.da_tao
        khoa = {"phap_nhan_id": p, "ma_tuong_quan": "DEMO-1"}
        assert app_ngan.doc("luot_abbyy", khoa).row_version == kq.row_version
        assert app_ngan.doc("luot_abbyy", {"phap_nhan_id": p, "bam_noi_dung": "DEMO-bam"})
        with app_ngan.lo() as lo:
            lo.sua("luot_abbyy", khoa, {"so_trang": 2}, row_version=kq.row_version)
        ds = app_ngan.tim("luot_abbyy", {"phap_nhan_id": p, "so_trang": 2}).danh_sach
        assert len(ds) == 1 and ds[0].gia_tri["phap_nhan_id"] == p
        with app_ngan.lo() as lo:
            cu = lo.lay_hoac_tao("luot_abbyy", {"phap_nhan_id": p, "bam_noi_dung": "DEMO-bam"},
                                {"ma_tuong_quan": "DEMO-2"})
        assert not cu.da_tao and cu.gia_tri["ma_tuong_quan"] == "DEMO-1"
    with app_ngan.lo() as lo:
        lo.xoa("luot_abbyy", {"phap_nhan_id": "DEMO-P", "ma_tuong_quan": "DEMO-1"},
               row_version=app_ngan.doc("luot_abbyy", {"phap_nhan_id": "DEMO-P", "ma_tuong_quan": "DEMO-1"}).row_version)
    assert app_ngan.tim("luot_abbyy", {"phap_nhan_id": "DEMO-P"}).danh_sach == []
    assert len(app_ngan.tim("luot_abbyy", {"phap_nhan_id": "DEMO-Q"}).danh_sach) == 1


@pytest.mark.parametrize("p", [None, "", "  ", 1, True, [], "\ud800"])
@pytest.mark.parametrize("lenh", ["doc", "tim", "them", "sua", "xoa", "lay_hoac_tao"])
def test_ngan_goc_thieu_hoac_sai_phap_nhan(ngan, p, lenh):
    khoa = {"phap_nhan_id": p, "ma": "DEMO"}
    with pytest.raises(NganKhongHopLe):
        if lenh == "doc":
            ngan.doc("luot", khoa)
        elif lenh == "tim":
            ngan.tim("luot", khoa)
        else:
            with ngan.lo() as lo:
                if lenh == "xoa":
                    lo.xoa("luot", khoa, row_version=1)
                elif lenh == "sua":
                    lo.sua("luot", khoa, {}, row_version=1)
                else:
                    getattr(lo, lenh)("luot", khoa, {"bam": "DEMO"})


def test_view_khong_doi_phap_nhan_va_gia_tri_cheo_bi_tu_choi(ngan):
    p = ngan.cho_phap_nhan("DEMO-P")
    assert p.cho_phap_nhan("DEMO-P").tim("luot").danh_sach == []
    with pytest.raises(NganKhongHopLe):
        p.cho_phap_nhan("DEMO-Q")
    for xem in (ngan, p):
        with pytest.raises(NganKhongHopLe):
            with xem.lo() as lo:
                lo.lay_hoac_tao("luot", {"phap_nhan_id": "DEMO-P", "bam": "DEMO"},
                                     {"ma": "DEMO", "phap_nhan_id": "DEMO-Q"})


def test_mot_lo_ngan_goc_nhieu_phap_nhan_va_bang_engine(ngan):
    with ngan.lo() as lo:
        for p in ("DEMO-P", "DEMO-Q"):
            lo.them("luot", {"phap_nhan_id": p, "ma": "DEMO-1"}, {"bam": "DEMO-chung"})
        lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 2})
    for p in ("DEMO-P", "DEMO-Q"):
        assert len(ngan.tim("luot", {"phap_nhan_id": p}).danh_sach) == 1
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}).gia_tri["so_trang"] == 2


@pytest.mark.parametrize("lenh", ["them", "sua", "xoa", "lay_hoac_tao"])
def test_phap_nhan_chi_trong_gia_tri_khong_du(ngan, lenh):
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            if lenh == "xoa":
                lo.xoa("luot", {"ma": "DEMO"}, row_version=1)
            elif lenh == "sua":
                lo.sua("luot", {"ma": "DEMO"}, {"phap_nhan_id": "DEMO-P"}, row_version=1)
            else:
                getattr(lo, lenh)("luot", {"ma": "DEMO"}, {"phap_nhan_id": "DEMO-P", "bam": "DEMO"})


@pytest.mark.parametrize("v", ["\ud800", "\udfff", {"\ud800": "DEMO"}, ["\ud800"]])
@pytest.mark.parametrize("lenh", ["them", "doc", "tim"])
def test_tu_choi_surrogate_le_bang_loi_ngan(ngan, v, lenh):
    with pytest.raises(NganKhongHopLe):
        if lenh == "them":
            with ngan.lo() as lo:
                lo.them("han_muc", {"ngay": "2026-11-15"}, {"chi_tiet": v})
        elif lenh == "doc":
            ngan.doc("han_muc", {"ngay": v})
        else:
            ngan.tim("han_muc", {"ngay": v})


@pytest.mark.parametrize("v", [None, 1, {"DEMO": [1, True, None]}])
def test_unique_json_none_so_bool_va_thu_tu_object(ngan, v):
    with ngan.lo() as lo:
        cu = lo.them("danh_muc", {"ma": "DEMO-1"}, {"bam": v, "bi_danh": "DEMO-1"})
    trung = 1.0 if v == 1 else v
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("danh_muc", {"ma": "DEMO-2"}, {"bam": trung, "bi_danh": "DEMO-2"})
    assert ngan.doc("danh_muc", {"bam": trung}).row_version == cu.row_version
    assert len(ngan.tim("danh_muc", {"bam": trung}).danh_sach) == 1
    khac = True if v == 1 else {"DEMO": [True, 1, None]}
    with ngan.lo() as lo:
        lo.them("danh_muc", {"ma": "DEMO-2"}, {"bam": khac, "bi_danh": "DEMO-2"})
    assert len(ngan.tim("danh_muc", {"bam": trung}).danh_sach) == 1


def test_khoa_chinh_so_bool_va_json_long_nhau(tao_ngan):
    ngan = tao_ngan([{"bang": "DEMO", "khoa": ["ma"]}])
    for v in (1, True, {"b": [1.0], "a": None}):
        with ngan.lo() as lo:
            lo.them("DEMO", {"ma": v}, {})
    for v in (1.0, True, {"a": None, "b": [1]}):
        assert ngan.doc("DEMO", {"ma": v}) is not None
        with pytest.raises(NganXungDot):
            with ngan.lo() as lo:
                lo.them("DEMO", {"ma": v}, {})
    assert len(ngan.tim("DEMO").danh_sach) == 3


def test_overlay_cap_nhat_xoa_tao_lai_va_rollback_chi_muc(ngan):
    with ngan.lo() as lo:
        cu = lo.them("danh_muc", {"ma": "DEMO-1"}, {"bam": "DEMO-cu", "bi_danh": "DEMO-1"})
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.sua("danh_muc", {"ma": "DEMO-1"}, {"bam": "DEMO-moi"}, row_version=cu.row_version)
            lo.them("danh_muc", {"ma": "DEMO-2"}, {"bam": "DEMO-moi", "bi_danh": "DEMO-2"})
    assert ngan.doc("danh_muc", {"bam": "DEMO-moi"}) is None
    assert ngan.doc("danh_muc", {"bam": "DEMO-cu"}).row_version == cu.row_version
    with ngan.lo() as lo:
        lo.xoa("danh_muc", {"bam": "DEMO-cu"}, row_version=cu.row_version)
        moi = lo.them("danh_muc", {"ma": "DEMO-1"}, {"bam": "DEMO-moi", "bi_danh": "DEMO-1"})
        lap = lo.lay_hoac_tao("danh_muc", {"bam": "DEMO-moi"}, {})
        lo.them("danh_muc", {"ma": "DEMO-2"}, {"bam": "DEMO-cu", "bi_danh": "DEMO-2"})
    assert moi.row_version == lap.row_version and not lap.da_tao
    with ngan.lo() as lo:
        sua = lo.sua("danh_muc", {"ma": "DEMO-1"}, {"bam": "DEMO-sua"}, row_version=moi.row_version)
    assert ngan.doc("danh_muc", {"bam": "DEMO-moi"}) is None
    assert ngan.doc("danh_muc", {"bam": "DEMO-sua"}).row_version == sua.row_version


def test_dong_thoi_tam_luong_nam_muoi_vong(ngan):
    hen = Barrier(8)
    def chay(so):
        ds = []
        for vong in range(50):
            with ngan.lo() as lo:
                kq = lo.lay_hoac_tao("luot", {"phap_nhan_id": "DEMO-P", "bam": "DEMO-chung"},
                                     {"ma": f"DEMO-{so}-{vong}"})
                hen.wait(timeout=10)
            ds.append(kq)
        return ds
    with ThreadPoolExecutor(max_workers=8) as nhom:
        ds = [k for nhom_kq in nhom.map(chay, range(8)) for k in nhom_kq]
    assert sum(k.da_tao for k in ds) == 1
    assert len({k.row_version for k in ds}) == 1
    assert all(k.gia_tri == ds[0].gia_tri for k in ds)
    assert len(ngan.tim("luot", {"phap_nhan_id": "DEMO-P"}).danh_sach) == 1


def test_hieu_nang_3000_them_va_200_lay_hoac_tao(ngan):
    bat_dau = perf_counter()
    for i in range(3000):
        with ngan.lo() as lo:
            lo.them("danh_muc", {"ma": f"DEMO-{i}"}, {"bam": f"DEMO-{i}", "bi_danh": f"DEMO-{i}"})
    for i in range(200):
        with ngan.lo() as lo:
            kq = lo.lay_hoac_tao("danh_muc", {"bam": f"DEMO-{i * 15}"}, {})
        assert not kq.da_tao
    thoi_gian = perf_counter() - bat_dau
    print(f"3000 them + 200 lay_hoac_tao: {thoi_gian:.3f} giây")
    assert thoi_gian < 2.0


def test_chon_ngan_app_slots_tra_ngan_khong_gan():
    class App:
        __slots__ = ()
    app = App()
    assert isinstance(chon_ngan(app), NganBoNho)
    assert not hasattr(app, "ngan")
