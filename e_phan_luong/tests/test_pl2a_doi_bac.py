"""Luật đổi bậc, nguồn mẫu và mô phỏng 12 tháng bằng dữ liệu DEMO."""
import random
import sys
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import doi_bac, thong_ke, ty_le
from e_phan_luong.kieu import (
    CHE_DO_BAC, CHE_DO_TOAN_BO, CHUA_PHAN_LOAI, KQ_DAT, KQ_KHONG_KIEM,
    KQ_SAI, MAU_BAT_BUOC, MAU_CHON, MAU_NGOAI, MUC_NHO, MUC_SAD, MUC_TE,
    NHAN_LOI_NGOAI_MAU, NHAN_RUI_RO_CAO,
)
from e_phan_luong.loi import loi


CS = ty_le.ChinhSach()
LUC = "2026-11-20T19:46:00+07:00"


def _moi():
    return ty_le.moi("kt_kiem", "thanh_toan_demo", CS)


def _cap(tt, ket_qua=KQ_DAT, nguon=MAU_CHON, muc=None, *, cs=CS, luc=LUC):
    return doi_bac.cap_nhat(tt, doi_bac.MotKetQua(nguon, ket_qua, muc), cs, luc=luc)


def test_loai_sach_xuong_dung_mau_30_60_100_va_khong_duoi_san():
    tt = ban_dau = _moi()
    tong_mau = 0
    for so_mau, bac_truoc, bac_sau in ((30, "0.30", "0.20"), (60, "0.20", "0.10"), (100, "0.10", "0.05")):
        for i in range(1, so_mau + 1):
            luc = f"2026-11-20T20:{(tong_mau + i) // 60:02d}:{(tong_mau + i) % 60:02d}+07:00"
            tt, da_doi = _cap(tt, luc=luc)
            if i < so_mau:
                assert tt.bac == Decimal(bac_truoc)
                assert tt.mau_tu_doi_bac == i and not da_doi
            else:
                assert tt.bac == Decimal(bac_sau) and da_doi
                assert tt.mau_tu_doi_bac == tt.loi_tu_doi_bac == 0
                assert tt.doi_bac_luc == luc
        tong_mau += so_mau
        assert tt.mau_12t == tong_mau
    for _ in range(200):
        tt, da_doi = _cap(tt)
        assert tt.bac == Decimal("0.05") and not da_doi
    assert tt.mau_12t == 390 and tt.loi_12t == 0
    assert tt.diem == thong_ke.can_tren(0, 390)
    assert ban_dau == _moi()


@pytest.mark.parametrize("truoc,sau", [("0.05", "0.10"), ("0.10", "0.20"), ("0.20", "0.30"), ("0.30", "0.30")])
def test_loi_nho_len_dung_mot_bac(truoc, sau):
    cu = replace(_moi(), bac=Decimal(truoc), mau_tu_doi_bac=12, mau_12t=40, doi_bac_luc="2026-11-01T00:00:00+07:00")
    tt, da_doi = _cap(cu, KQ_SAI, muc=MUC_NHO)
    assert tt.bac == Decimal(sau) and tt.che_do == CHE_DO_BAC
    assert da_doi == (truoc != sau)
    assert tt.mau_12t == 41 and tt.loi_12t == 1 and tt.loi_sad_12t == 0
    if da_doi:
        assert tt.mau_tu_doi_bac == tt.loi_tu_doi_bac == 0
        assert tt.doi_bac_luc == LUC
    else:
        assert tt.mau_tu_doi_bac == 13 and tt.loi_tu_doi_bac == 1
        assert tt.doi_bac_luc == cu.doi_bac_luc


@pytest.mark.parametrize("nguon", [MAU_CHON, MAU_BAT_BUOC, MAU_NGOAI])
def test_loi_sad_moi_nguon_ve_bac_dau_va_rui_ro_cao(nguon):
    cu = replace(_moi(), bac=Decimal("0.05"), mau_tu_doi_bac=12, mau_12t=100)
    tt, da_doi = _cap(cu, KQ_SAI, nguon, MUC_SAD)
    assert da_doi and tt.bac == Decimal("0.30") and tt.che_do == CHE_DO_BAC
    assert tt.mau_tu_doi_bac == tt.loi_tu_doi_bac == 0
    assert tt.mau_12t == 100 + int(nguon == MAU_CHON)
    assert tt.loi_12t == int(nguon == MAU_CHON)
    assert tt.loi_sad_12t == 1 and NHAN_RUI_RO_CAO in tt.nhan
    assert (NHAN_LOI_NGOAI_MAU in tt.nhan) == (nguon == MAU_NGOAI)


@pytest.mark.parametrize("nguon", [MAU_CHON, MAU_BAT_BUOC, MAU_NGOAI])
def test_loi_te_vao_toan_bo_va_dung_30_mau_sach_ve_bac_dau(nguon):
    tt, da_doi = _cap(replace(_moi(), bac=Decimal("0.10")), KQ_SAI, nguon, MUC_TE)
    assert da_doi and tt.che_do == CHE_DO_TOAN_BO and tt.mau_sach_toan_bo == 0
    assert tt.loi_sad_12t == 1 and NHAN_RUI_RO_CAO in tt.nhan
    for i in range(1, 31):
        # Cả ba nguồn đều được tính vào chuỗi sạch của chế độ toàn bộ.
        tt, da_doi = _cap(tt, nguon=(MAU_BAT_BUOC, MAU_NGOAI, MAU_CHON)[i % 3])
        assert tt.mau_sach_toan_bo == i
        if i < 30:
            assert tt.che_do == CHE_DO_TOAN_BO and not da_doi
            assert ty_le.p_bac(tt, CS) == Decimal(1)
        else:
            assert tt.che_do == CHE_DO_BAC and tt.bac == Decimal("0.30") and da_doi
            assert tt.mau_tu_doi_bac == tt.loi_tu_doi_bac == 0
    assert NHAN_RUI_RO_CAO in tt.nhan


@pytest.mark.parametrize("muc", [MUC_NHO, MUC_SAD, MUC_TE])
@pytest.mark.parametrize("nguon", [MAU_CHON, MAU_NGOAI, MAU_BAT_BUOC])
def test_dang_toan_bo_chi_loi_te_dem_sach_lai(muc, nguon):
    cu = replace(_moi(), bac=Decimal("0.10"), che_do=CHE_DO_TOAN_BO,
                 mau_sach_toan_bo=20, mau_tu_doi_bac=20, mau_12t=100, doi_bac_luc=LUC)
    tt, da_doi = _cap(cu, KQ_SAI, nguon, muc, luc="2026-11-21T00:00:00+07:00")
    assert not da_doi and tt.che_do == CHE_DO_TOAN_BO and tt.bac == cu.bac
    assert tt.mau_sach_toan_bo == (0 if muc == MUC_TE else 20)
    assert tt.doi_bac_luc == LUC
    assert tt.mau_tu_doi_bac == 20 + int(nguon == MAU_CHON)
    assert (NHAN_RUI_RO_CAO in tt.nhan) == (muc in (MUC_SAD, MUC_TE))
    assert (NHAN_LOI_NGOAI_MAU in tt.nhan) == (nguon == MAU_NGOAI)
    so_con_lai = 30 if muc == MUC_TE else 10
    for _ in range(so_con_lai - 1):
        tt, da_doi = _cap(tt)
        assert not da_doi and tt.che_do == CHE_DO_TOAN_BO
    tt, da_doi = _cap(tt)
    assert da_doi and tt.bac == Decimal("0.30") and tt.che_do == CHE_DO_BAC


def test_loi_ngoai_mau_ve_bac_dau_nhan_rieng_khong_vao_uoc_luong():
    cu = replace(_moi(), bac=Decimal("0.05"), mau_tu_doi_bac=8, mau_12t=100)
    tt, da_doi = _cap(cu, KQ_SAI, MAU_NGOAI, MUC_NHO)
    assert da_doi and tt.bac == Decimal("0.30")
    assert tt.mau_12t == 100 and tt.loi_12t == 0 and tt.loi_sad_12t == 0
    assert tt.loi_ngoai_mau_12t == 1 and NHAN_LOI_NGOAI_MAU in tt.nhan
    assert NHAN_RUI_RO_CAO not in tt.nhan
    assert tt.diem == thong_ke.can_tren(0, 100)


def test_mau_bat_buoc_khong_gop_vao_dieu_kien_xuong_bac():
    tt = _moi()
    for _ in range(29):
        tt, _ = _cap(tt)
    for _ in range(200):
        tt, da_doi = _cap(tt, nguon=MAU_BAT_BUOC)
        assert not da_doi and tt.bac == Decimal("0.30")
        assert tt.mau_tu_doi_bac == tt.mau_12t == 29
    tt, da_doi = _cap(tt)
    assert da_doi and tt.bac == Decimal("0.20") and tt.mau_12t == 30


def test_chi_mau_bat_buoc_khong_co_diem_nhung_loi_van_len_bac():
    tt = replace(_moi(), bac=Decimal("0.10"))
    tt, da_doi = _cap(tt, KQ_SAI, MAU_BAT_BUOC, MUC_NHO)
    assert da_doi and tt.bac == Decimal("0.20")
    assert tt.mau_12t == tt.loi_12t == 0 and tt.diem is None
    tt, da_doi = _cap(tt, KQ_SAI, MAU_BAT_BUOC, MUC_SAD)
    assert da_doi and tt.bac == Decimal("0.30") and tt.diem is None
    assert NHAN_RUI_RO_CAO in tt.nhan


def test_khong_kiem_khong_doi_bat_ky_truong_nao():
    cu = replace(_moi(), bac=Decimal("0.20"), mau_tu_doi_bac=29, loi_tu_doi_bac=1,
                 mau_12t=50, loi_12t=2, diem=Decimal("0.12"), nhan=frozenset({NHAN_RUI_RO_CAO}))
    for nguon in (MAU_CHON, MAU_BAT_BUOC, MAU_NGOAI):
        tt, da_doi = _cap(cu, KQ_KHONG_KIEM, nguon, MUC_TE)
        assert tt is cu and not da_doi


def test_chua_phan_loai_co_dinh_ke_ca_loi_te_va_ngoai_mau():
    tt = replace(_moi(), loai=CHUA_PHAN_LOAI)
    for _ in range(200):
        tt, da_doi = _cap(tt)
        assert not da_doi and ty_le.p_bac(tt, CS) == Decimal("0.30")
    for nguon in (MAU_CHON, MAU_BAT_BUOC, MAU_NGOAI):
        for muc in (MUC_NHO, MUC_SAD, MUC_TE):
            tt, da_doi = _cap(tt, KQ_SAI, nguon, muc)
            assert not da_doi and tt.che_do == CHE_DO_BAC and tt.bac == Decimal("0.30")
    assert tt.mau_12t == 203 and tt.loi_12t == 3
    assert tt.loi_sad_12t == 6 and tt.loi_ngoai_mau_12t == 3
    assert tt.nhan == frozenset({NHAN_RUI_RO_CAO, NHAN_LOI_NGOAI_MAU})
    assert tt.doi_bac_luc is None


def test_diem_va_nhan_cap_nhat_dung_nguong_nghiem_ngat():
    cs = replace(CS, nguong_diem_rui_ro=Decimal("0.95"))
    tt, _ = _cap(_moi(), cs=cs)
    assert tt.diem == Decimal("0.950000") and NHAN_RUI_RO_CAO not in tt.nhan
    tt, _ = _cap(_moi())
    assert NHAN_RUI_RO_CAO in tt.nhan
    tt = replace(tt, nhan=tt.nhan | {"nhan_demo"})
    for _ in range(29):
        tt, _ = _cap(tt)
    assert tt.diem == thong_ke.can_tren(0, 30)
    assert tt.nhan == frozenset({"nhan_demo"})


def test_chinh_sach_do_tin_cay_thuc_su_dung_cho_xuong_bac_va_diem():
    cs = replace(CS, do_tin_cay=Decimal("0.90"), mau_toi_thieu=(Decimal(1), Decimal(60), Decimal(100)))
    tt = _moi()
    for _ in range(21):
        tt, da_doi = _cap(tt, cs=cs)
        assert not da_doi
    tt, da_doi = _cap(tt, cs=cs)
    assert da_doi and tt.bac == Decimal("0.20")
    assert tt.diem == thong_ke.can_tren(0, 22, Decimal("0.90"))


def test_du_mau_nhung_can_tren_chua_dat_thi_khong_xuong():
    tt, _ = _cap(_moi(), KQ_SAI, muc=MUC_NHO)
    for _ in range(29):
        tt, da_doi = _cap(tt)
        assert not da_doi
    assert tt.mau_tu_doi_bac == 30 and tt.loi_tu_doi_bac == 1
    assert tt.bac == Decimal("0.30")


def test_mo_phong_12_thang_25_mau_moi_thang_hat_giong_co_dinh():
    """300 mẫu/loại, đúng 24 lỗi nhỏ (8%); chưa thực hiện chốt kỳ PL-4.

    Quy mô là một điều kiện của mô phỏng: luật ngưỡng 10% không bảo đảm
    mọi chuỗi 8% ở cỡ mẫu lớn đều giữ bậc đầu (xem test giới hạn bên dưới).
    """
    ngau_nhien = random.Random(20261120)
    sach, co_loi = _moi(), _moi()
    chua = replace(_moi(), loai=CHUA_PHAN_LOAI)
    lan_xuong = []
    for thang in range(1, 13):
        chi_so_loi = set(ngau_nhien.sample(range(25), 2))
        for i in range(25):
            luc = f"2026-{thang:02d}-{i + 1:02d}T12:00:00+07:00"
            sach, da_doi = _cap(sach, luc=luc)
            if da_doi:
                lan_xuong.append((thang - 1) * 25 + i + 1)
            kq = KQ_SAI if i in chi_so_loi else KQ_DAT
            muc = MUC_NHO if kq == KQ_SAI else None
            co_loi, _ = _cap(co_loi, kq, muc=muc, luc=luc)
            chua, da_doi = _cap(chua, kq, muc=muc, luc=luc)
            assert co_loi.bac == Decimal("0.30") and co_loi.che_do == CHE_DO_BAC
            assert ty_le.p_bac(chua, CS) == Decimal("0.30") and not da_doi
        assert NHAN_RUI_RO_CAO in co_loi.nhan
    assert lan_xuong == [30, 90, 190]
    assert sach.bac == Decimal("0.05") and sach.mau_12t == 300
    assert co_loi.mau_12t == 300 and co_loi.loi_12t == 24
    assert co_loi.diem == thong_ke.can_tren(24, 300)


def test_gioi_han_luat_8_phan_tram_khong_bao_dam_giu_bac_voi_mau_lon():
    # 80/1.000 có cận trên < 10%: ghi nhận đúng luật, không thêm điều kiện giữ bậc.
    tt = replace(_moi(), mau_tu_doi_bac=999, loi_tu_doi_bac=80, mau_12t=999, loi_12t=80)
    tt, da_doi = _cap(tt)
    assert tt.diem == Decimal("0.095552")
    assert da_doi and tt.bac == Decimal("0.20")


@pytest.mark.parametrize("kq", [
    doi_bac.MotKetQua("nguon_la", KQ_DAT),
    doi_bac.MotKetQua(MAU_CHON, "ket_qua_la"),
    doi_bac.MotKetQua(MAU_CHON, KQ_SAI),
    doi_bac.MotKetQua(MAU_CHON, KQ_SAI, "muc_la"),
])
def test_ket_qua_sai_khong_bi_tinh_nham(kq):
    with pytest.raises(type(loi("DU_LIEU_KHONG_HOP_LE"))) as bat:
        doi_bac.cap_nhat(_moi(), kq, CS, luc=LUC)
    assert bat.value.ma == "DU_LIEU_KHONG_HOP_LE"
