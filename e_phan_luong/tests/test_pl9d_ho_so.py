"""PL-9D: hồ sơ hành vi; đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO."""
from copy import deepcopy
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import json
import logging

import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chot_ky, ho_so, ngan_ho_so, quy_trinh
from e_phan_luong.chay import app
from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.kieu import DOI_TAC_MOI, NGHI_CHIA_NHO, SO_TIEN_BAT_THUONG, Tien
from e_phan_luong.phan_luong import bam_doi_tac
from test_pl2_ngan_luot import chay_ngan
from test_pl2_phan_luong import KHAU, chay, lay_kq, lo_mot, tham_so


NGAY = date(2026, 11, 21)
GIO_VN = timezone(timedelta(hours=7))
LOAI = "chi_phi_khac"
DOI_TAC = "DEMO-NCC-HO-SO"
BAM = bam_doi_tac("demo_thanh_toan", DOI_TAC)


@pytest.fixture(autouse=True)
def ghim_gio(monkeypatch):
    class DongHo(datetime):
        @classmethod
        def now(cls, tz=None):
            luc = datetime(2026, 11, 20, 17, 30, tzinfo=timezone.utc)
            return luc.astimezone(tz) if tz is not None else luc.replace(tzinfo=None)

    monkeypatch.setattr(chot_ky, "datetime", DongHo)


def _dong(so="40", *, ngay=NGAY, bam=BAM, tien_te="VND"):
    return Tien(Decimal(so), tien_te), bam, ngay


def _lo(ma, so="40", tien_te="VND", **doi):
    lo = lo_mot(ma=ma, doi_tac=DOI_TAC, ngay=NGAY.isoformat(), **doi)
    lo["nguong"] = {k: {"so": v, "tien_te": tien_te}
                    for k, v in {"pm": "200", "te": "100", "sad": "10"}.items()}
    lo["nghiep_vu"][0]["so_tien"] = {"so": so, "tien_te": tien_te}
    return lo


def _hs(core):
    return ho_so.tu_ban_ghi(next(b for b in core.xem_ngan(app.ma, "ho_so_hanh_vi")
                               if b["khau"] == KHAU and b["loai"] == LOAI))


def _ghi(core, hs):
    def ghi(viec):
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("ho_so_hanh_vi", {"khau": hs.khau, "loai": hs.loai},
                           ho_so.ve_ban_ghi(hs))
    assert chay_ngan(core, ghi)["trang_thai"] == "XONG"


@pytest.mark.parametrize("so", ["100", "150", "-100"])
def test_khoan_dat_te_khong_vao_lich_su_chia_nho(so):
    cu = ho_so.moi(KHAU, LOAI)
    hs, bo = ho_so.cong(cu, [_dong(so)], ky="2026-11", te=Decimal(100))
    assert hs.so_nghiep_vu == 1 and hs.doi_tac == {BAM: "2026-11"}
    assert hs.tong_ngay == {} and bo == 0
    assert cu == ho_so.moi(KHAU, LOAI)


def test_luot_vuot_te_roi_khoan_nho_khong_nghi_chia_nho():
    core = CoreGia()
    _, tep1, _ = lay_kq(core, chay(core, _lo("PC-DEMO-LON", "100")))
    assert tep1["nghiep_vu"][0]["ly_do"] == ["VUOT_TE"]
    _, tep2, _ = lay_kq(core, chay(core, _lo("PC-DEMO-NHO")))
    assert NGHI_CHIA_NHO not in tep2["nghiep_vu"][0]["ly_do"]
    hs = _hs(core)
    assert hs.tong_ngay == {BAM: {NGAY.isoformat(): Decimal(40)}}
    assert hs.so_nghiep_vu == 2 and hs.tien_te == "VND"


@pytest.mark.parametrize("dao", [False, True])
def test_ngay_2062_khong_cat_mat_hom_nay_va_bien_cong_mot_ngay(dao):
    ds = [_dong("20", ngay=date(2062, 1, 1)), _dong("30"),
          _dong("1", ngay=NGAY + timedelta(days=1)),
          _dong("2", ngay=NGAY + timedelta(days=2))]
    hs, _ = ho_so.cong(ho_so.moi(KHAU, LOAI), reversed(ds) if dao else ds,
                       ky="2026-11", te=Decimal(100))
    assert hs.tong_ngay == {BAM: {"2026-11-21": Decimal(30), "2026-11-22": Decimal(1)}}
    assert hs.so_nghiep_vu == 4  # Chỉ loại khỏi tổng chia nhỏ, vẫn đếm biểu đồ.
    assert chot_ky.ngay_hien_tai() == NGAY and chot_ky.ky_hien_tai() == "2026-11"


def test_ho_so_cu_ngay_2062_duoc_lam_moi_truoc_khi_cat_cua_so():
    hs = ho_so.HoSo(KHAU, LOAI, {"2026-10": {0: 2}}, {BAM: "2026-10"},
                   {BAM: {"2062-01-01": Decimal(90), "2026-11-21": Decimal(30)}},
                   "2026-10", "VND")
    cu = deepcopy(hs)
    moi = ho_so.lam_moi(hs, "2026-11")
    assert moi.tong_ngay == {BAM: {"2026-11-21": Decimal(30)}}
    moi, _ = ho_so.cong(moi, [_dong("10")], ky="2026-11", te=Decimal(100))
    assert moi.tong_ngay[BAM] == {"2026-11-21": Decimal(40)}
    assert hs == cu and moi.tien_te == "VND"


def test_ho_so_cu_chua_co_tien_te_nhan_don_vi_luot_dau():
    hs = ho_so.HoSo(KHAU, LOAI, {"2026-11": {0: 50}}, {BAM: "2026-11"},
                   {BAM: {NGAY.isoformat(): Decimal(2)}})
    ban = ho_so.ve_ban_ghi(hs)
    ban.pop("tien_te")
    cu = ho_so.tu_ban_ghi(ban)
    assert cu.tien_te is None
    assert ho_so.anh_chup(cu, tien_te_nguong="USD").so_nghiep_vu == 50
    moi, _ = ho_so.cong(cu, [_dong("3", tien_te="USD")], ky="2026-11",
                       te=Decimal(100), tien_te_nguong="USD")
    assert moi.tien_te == "USD" and moi.so_nghiep_vu == 51
    assert moi.tong_ngay[BAM][NGAY.isoformat()] == 5
    assert ho_so.tu_ban_ghi(ho_so.ve_ban_ghi(moi)) == moi


def test_vnd_sang_usd_bo_tong_bieu_do_phan_vi_giu_doi_tac_va_canh_bao():
    core = CoreGia()
    lo = _lo("PC-DEMO-VND", "1")
    lo["nghiep_vu"] = [{**lo["nghiep_vu"][0], "ma": f"PC-DEMO-VND-{i}"} for i in range(50)]
    lay_kq(core, chay(core, lo))
    cu = _hs(core)
    assert cu.so_nghiep_vu == 50
    anh = ho_so.anh_chup(cu, tien_te_nguong="USD")
    assert anh.so_nghiep_vu == 0 and anh.phan_vi_95 is None
    assert anh.bam_doi_tac == frozenset({BAM})
    truong, tep, _ = lay_kq(core, chay(core, _lo("PC-DEMO-USD", "60", "USD")))
    dong = tep["nghiep_vu"][0]
    assert NGHI_CHIA_NHO not in dong["ly_do"]
    assert DOI_TAC_MOI not in dong["co"] and SO_TIEN_BAT_THUONG not in dong["co"]
    assert "Tiền tệ ngưỡng đã đổi" in truong["canh_bao"]
    assert "%" not in truong["canh_bao"]
    moi = _hs(core)
    assert moi.tien_te == "USD" and moi.so_nghiep_vu == 1
    assert moi.tong_ngay == {BAM: {NGAY.isoformat(): Decimal(60)}}
    # VND ở loại khác cũng không được cộng vào tổng chia nhỏ theo khâu.
    _, tep, _ = lay_kq(core, chay(core, _lo("PC-DEMO-USD-LOAI-KHAC", "40", "USD", loai="tam_ung")))
    assert NGHI_CHIA_NHO in tep["nghiep_vu"][0]["ly_do"]


def test_tien_te_khac_o_loai_khac_khong_gom_chia_nho():
    core = CoreGia()
    lay_kq(core, chay(core, _lo("PC-DEMO-VND-CU", "60")))
    _, tep, _ = lay_kq(core, chay(core, _lo("PC-DEMO-USD-MOI", "40", "USD", loai="tam_ung")))
    assert NGHI_CHIA_NHO not in tep["nghiep_vu"][0]["ly_do"]


def test_q9_canh_bao_truoc_xuat_khong_ghi_va_log_sau_cas(monkeypatch, caplog):
    core = CoreGia()
    hs = ho_so.HoSo(KHAU, LOAI, {"2026-11": {0: 1}},
                   {f"{i:032x}": "2026-10" for i in range(20000)}, {}, "2026-11", "VND")
    _ghi(core, hs)
    cu = deepcopy(core.xem_ngan(app.ma, "ho_so_hanh_vi"))
    xuat_goc = quy_trinh.xuat_ket_qua
    da_xuat = []

    def xuat(*args, **kw):
        assert core.xem_ngan(app.ma, "ho_so_hanh_vi") == cu
        assert any("20.000 đối tác" in c for c in kw["canh_bao_them"])
        da_xuat.append(True)
        return xuat_goc(*args, **kw)

    monkeypatch.setattr(quy_trinh, "xuat_ket_qua", xuat)
    core.gay_xung_dot_ngan("ho_so_hanh_vi", so_lan=1)
    with caplog.at_level(logging.WARNING, logger=quy_trinh.__name__):
        truong, _, _ = lay_kq(core, chay(core, _lo("PC-DEMO-TRAN")))
    assert da_xuat == [True] and "20.000 đối tác" in truong["canh_bao"]
    assert len(_hs(core).doi_tac) == 20000 and _hs(core).so_nghiep_vu == 2
    logs = [r for r in caplog.records if r.name == quy_trinh.__name__]
    assert len(logs) == 1 and logs[0].args == (1,)
    assert DOI_TAC not in truong["canh_bao"] and BAM not in truong["canh_bao"]


@pytest.mark.parametrize("tien_te", ["VNDD", "usd", "", 123])
def test_ho_so_tien_te_khong_hop_le_bi_bo(tien_te):
    hs = ho_so.moi(KHAU, LOAI)
    assert ho_so.tu_ban_ghi({**ho_so.ve_ban_ghi(hs), "tien_te": tien_te}) == hs
