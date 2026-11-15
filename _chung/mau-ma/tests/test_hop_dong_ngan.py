"""Hợp đồng chung; không truy cập trạng thái nội bộ của bản ngăn."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from ngan import NganXungDot


def them(ngan, ma="DEMO-1", bam="bam-DEMO-1", bi_danh="DEMO-A"):
    with ngan.lo() as lo:
        kq = lo.them("danh_muc", {"ma": ma}, {"bam": bam, "bi_danh": bi_danh, "dem": 1})
    return kq


def test_lo_thanh_cong_nhieu_bang_va_chi_ghi_khi_thoat(ngan):
    with ngan.lo() as lo:
        a = lo.them("danh_muc", {"ma": "DEMO-1"}, {"bam": "DEMO", "bi_danh": "DEMO"})
        b = lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 10})
        assert ngan.doc("danh_muc", {"ma": "DEMO-1"}) is None
        assert ngan.doc("han_muc", {"ngay": "2026-11-15"}) is None
    assert a.da_tao and b.da_tao
    assert ngan.doc("danh_muc", {"ma": "DEMO-1"}).row_version == a.row_version
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}).gia_tri["so_trang"] == 10


def test_ngoai_le_trong_with_huy_toan_lo(ngan):
    with pytest.raises(RuntimeError, match="DEMO"):
        with ngan.lo() as lo:
            lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 10})
            raise RuntimeError("DEMO")
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}) is None


@pytest.mark.parametrize("thao_tac", ["sua", "xoa"])
def test_cas_lech_rollback_them_sua_xoa_nhieu_bang(ngan, thao_tac):
    cu = them(ngan)
    with ngan.lo() as lo:
        h = lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 10})
    with pytest.raises(NganXungDot) as loi:
        with ngan.lo() as lo:
            lo.sua("danh_muc", {"ma": "DEMO-1"}, {"dem": 9}, row_version=cu.row_version)
            lo.xoa("han_muc", {"ngay": "2026-11-15"}, row_version=h.row_version)
            lo.them("han_muc", {"ngay": "2026-11-16"}, {"so_trang": 20})
            if thao_tac == "sua":
                lo.sua("danh_muc", {"ma": "DEMO-1"}, {"dem": 8}, row_version=cu.row_version)
            else:
                lo.xoa("danh_muc", {"ma": "DEMO-1"}, row_version=cu.row_version)
    assert loi.value.ma == "NGAN_XUNG_DOT" and loi.value.thu_lai_duoc
    assert ngan.doc("danh_muc", {"ma": "DEMO-1"}).gia_tri["dem"] == 1
    assert ngan.doc("danh_muc", {"ma": "DEMO-1"}).row_version == cu.row_version
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}).row_version == h.row_version
    assert ngan.doc("han_muc", {"ngay": "2026-11-16"}) is None


def test_sua_la_ban_va_xoa_cas_dung(ngan):
    cu = them(ngan)
    with ngan.lo() as lo:
        moi = lo.sua("danh_muc", {"ma": "DEMO-1"}, {"dem": 2}, row_version=cu.row_version)
    assert moi.row_version != cu.row_version
    assert not moi.da_tao and moi.gia_tri["bam"] == "bam-DEMO-1"
    with ngan.lo() as lo:
        xoa = lo.xoa("danh_muc", {"ma": "DEMO-1"}, row_version=moi.row_version)
    assert not xoa.da_tao
    assert ngan.doc("danh_muc", {"ma": "DEMO-1"}) is None


def test_cas_cu_khong_dung_lai_sau_xoa_tao_lai(ngan):
    cu = them(ngan)
    with ngan.lo() as lo:
        lo.xoa("danh_muc", {"ma": "DEMO-1"}, row_version=cu.row_version)
    moi = them(ngan)
    assert moi.row_version != cu.row_version
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.sua("danh_muc", {"ma": "DEMO-1"}, {"dem": 99}, row_version=cu.row_version)


@pytest.mark.parametrize("thao_tac", ["sua", "xoa"])
def test_cas_ban_ghi_khong_con(ngan, thao_tac):
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            if thao_tac == "sua":
                lo.sua("danh_muc", {"ma": "DEMO-mat"}, {"dem": 99}, row_version=1)
            else:
                lo.xoa("danh_muc", {"ma": "DEMO-mat"}, row_version=1)


@pytest.mark.parametrize("truong", ["ma", "bam", "bi_danh"])
def test_them_trung_bat_ky_rang_buoc_nao_huy_ca_lo(ngan, truong):
    cu = them(ngan)
    v = {"ma": "DEMO-2", "bam": "bam-DEMO-2", "bi_danh": "DEMO-B"}
    v[truong] = cu.gia_tri[truong]
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("han_muc", {"ngay": "2026-11-15"}, {"so_trang": 10})
            lo.them("danh_muc", {"ma": v["ma"]}, {k: x for k, x in v.items() if k != "ma"})
    assert ngan.doc("han_muc", {"ngay": "2026-11-15"}) is None
    assert len(ngan.tim("danh_muc").danh_sach) == 1


def test_sua_trung_duy_nhat_huy_ca_lo(ngan):
    them(ngan)
    hai = them(ngan, "DEMO-2", "bam-DEMO-2", "DEMO-B")
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.sua("danh_muc", {"ma": "DEMO-2"}, {"bam": "bam-DEMO-1"}, row_version=hai.row_version)
    assert ngan.doc("danh_muc", {"ma": "DEMO-2"}).row_version == hai.row_version


@pytest.mark.parametrize("khoa", [{"bam": "bam-DEMO-1"}, {"bi_danh": "DEMO-A"}])
def test_lay_hoac_tao_theo_duy_nhat_tra_ban_cu_khong_ghi_de(ngan, khoa):
    cu = them(ngan)
    with ngan.lo() as lo:
        kq = lo.lay_hoac_tao("danh_muc", khoa,
                             {"ma": "DEMO-2", "bi_danh": "DEMO-B", "dem": 99})
    assert not kq.da_tao
    assert kq.row_version == cu.row_version and kq.gia_tri == cu.gia_tri


def test_lay_hoac_tao_lap_trong_cung_lo(ngan):
    with ngan.lo() as lo:
        a = lo.lay_hoac_tao("danh_muc", {"bam": "DEMO"}, {"ma": "DEMO-1", "bi_danh": "DEMO"})
        b = lo.lay_hoac_tao("danh_muc", {"bam": "DEMO"}, {"ma": "DEMO-2", "bi_danh": "DEMO-2"})
    assert a.da_tao and not b.da_tao
    assert a.gia_tri == b.gia_tri and a.row_version == b.row_version


def test_dong_thoi_lay_hoac_tao_chi_mot_ban(ngan):
    hen = Barrier(2)
    def chay(so):
        with ngan.lo() as lo:
            kq = lo.lay_hoac_tao("danh_muc", {"bam": "bam-DEMO-chung"},
                                 {"ma": f"DEMO-{so}", "bi_danh": f"DEMO-{so}"})
            hen.wait(timeout=5)
        return kq
    with ThreadPoolExecutor(max_workers=2) as nhom:
        ds = list(nhom.map(chay, [1, 2]))
    assert sum(k.da_tao for k in ds) == 1
    assert ds[0].gia_tri == ds[1].gia_tri and ds[0].row_version == ds[1].row_version
    assert len(ngan.tim("danh_muc").danh_sach) == 1


def test_dong_thoi_cas_chi_mot_lo_thanh_cong(ngan):
    cu = them(ngan)
    hen = Barrier(2)
    def chay(so):
        try:
            with ngan.lo() as lo:
                lo.sua("danh_muc", {"ma": "DEMO-1"}, {"dem": so}, row_version=cu.row_version)
                lo.them("han_muc", {"ngay": f"2026-11-{so:02}"}, {"so_trang": so})
                hen.wait(timeout=5)
            return True
        except NganXungDot:
            return False
    with ThreadPoolExecutor(max_workers=2) as nhom:
        ds = list(nhom.map(chay, [15, 16]))
    assert sum(ds) == 1
    assert len(ngan.tim("han_muc").danh_sach) == 1


def test_phap_nhan_khong_doc_cheo_cung_khoa_va_cung_bam(ngan):
    a, b = ngan.cho_phap_nhan("DEMO-A"), ngan.cho_phap_nhan("DEMO-B")
    with a.lo() as lo:
        lo.them("luot", {"ma": "DEMO-1"}, {"bam": "DEMO-chung"})
        lo.them("luot", {"ma": "DEMO-2"}, {"bam": "DEMO-rieng"})
    assert b.doc("luot", {"ma": "DEMO-1"}) is None
    assert b.tim("luot").danh_sach == []
    with b.lo() as lo:
        kq = lo.lay_hoac_tao("luot", {"phap_nhan_id": "DEMO-B", "bam": "DEMO-chung"}, {"ma": "DEMO-1"})
    assert kq.da_tao
    assert len(a.tim("luot").danh_sach) == 2
    assert len(b.tim("luot").danh_sach) == 1
    assert a.doc("luot", {"ma": "DEMO-1"}).gia_tri["phap_nhan_id"] == "DEMO-A"
    with pytest.raises(NganXungDot):
        with b.lo() as lo:
            lo.xoa("luot", {"ma": "DEMO-2"}, row_version=a.doc("luot", {"ma": "DEMO-2"}).row_version)


def test_bang_engine_dung_chung_giua_cac_view(ngan):
    a, b = ngan.cho_phap_nhan("DEMO-A"), ngan.cho_phap_nhan("DEMO-B")
    them(a)
    assert b.doc("danh_muc", {"ma": "DEMO-1"}) is not None


def test_duy_nhat_tu_gioi_han_theo_phap_nhan(tao_ngan):
    goc = tao_ngan([{"bang": "luot", "khoa": ["ma"], "pham_vi": "phap_nhan",
                     "duy_nhat": [["bam"]]}])
    for p in ("DEMO-A", "DEMO-B"):
        with goc.cho_phap_nhan(p).lo() as lo:
            lo.them("luot", {"ma": "DEMO-chung"}, {"bam": "DEMO-chung"})
    for p in ("DEMO-A", "DEMO-B"):
        ds = goc.cho_phap_nhan(p).tim("luot").danh_sach
        assert len(ds) == 1 and ds[0].gia_tri["phap_nhan_id"] == p


def test_trung_duy_nhat_giua_hai_lenh_moi_huy_ca_lo(ngan):
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("danh_muc", {"ma": "DEMO-1"}, {"bam": "DEMO-chung", "bi_danh": "DEMO-1"})
            lo.them("danh_muc", {"ma": "DEMO-2"}, {"bam": "DEMO-chung", "bi_danh": "DEMO-2"})
    assert ngan.tim("danh_muc").danh_sach == []


def test_tim_loc_va_phan_trang_khong_lap(ngan):
    for i in range(5):
        them(ngan, f"DEMO-{i}", f"bam-DEMO-{i}", f"DEMO-{i}")
    ds, tiep = [], None
    for _ in range(3):
        trang = ngan.tim("danh_muc", {"dem": 1}, gioi_han=2, tiep=tiep)
        ds.extend(x.gia_tri["ma"] for x in trang.danh_sach)
        tiep = trang.tiep
    assert len(ds) == len(set(ds)) == 5 and tiep is None
    assert ngan.tim("danh_muc", {"dem": 99}).danh_sach == []


def test_ban_sao_dau_vao_dau_ra_khong_sua_ngam_ngan(ngan):
    v = {"so_trang": 1, "chi_tiet": {"DEMO": [1]}}
    with ngan.lo() as lo:
        kq = lo.them("han_muc", {"ngay": "2026-11-15"}, v)
        v["chi_tiet"]["DEMO"].append(2)
    kq.gia_tri["chi_tiet"]["DEMO"].append(3)
    doc = ngan.doc("han_muc", {"ngay": "2026-11-15"})
    doc.gia_tri["chi_tiet"]["DEMO"].append(4)
    ngan.tim("han_muc").danh_sach[0].gia_tri["so_trang"] = 999
    that = ngan.doc("han_muc", {"ngay": "2026-11-15"}).gia_tri
    assert that["chi_tiet"] == {"DEMO": [1]} and that["so_trang"] == 1
