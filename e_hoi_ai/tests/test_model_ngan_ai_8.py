"""AI-8: model ngăn trên CoreGia và Local giả; 0 lượt Cloud."""
import pytest

from e_hoi_ai import chay, chon_model
from e_hoi_ai.ngan import NganBoNho, NganXungDot
from local_gia import LocalGia, nap_cau_hinh
from test_hoi_tai_lieu import hoi, khong_mang_ngoai_va_khong_cloud, local


def test_model_ghi_ngan_khong_trung_id_va_loai_bo_model_mat(local):
    local.models = [{"id": "model-demo"}, {"id": "model-demo-b"}]
    assert hoi()["trang_thai"] == "XONG"
    n = chay.app.ngan
    assert len(n.tim("model_phat_hien")["danh_sach"]) == 2
    a = n.doc("model_phat_hien", {"id_model": "model-demo"})
    assert a.gia_tri["kha_dung"] and a.gia_tri["loai"] == "openai_compatible"
    assert a.gia_tri["kiem_luc"] and a.gia_tri["url"] == local.url
    local.models.pop(0)
    assert hoi()["ket_qua"]["truong"]["model"] == "model-demo-b"
    assert not n.doc("model_phat_hien", {"id_model": "model-demo"}).gia_tri["kha_dung"]
    assert len(n.tim("model_phat_hien")["danh_sach"]) == 2


def test_doi_cau_hinh_local_cung_id_khong_dung_catalog_cu(local):
    assert hoi()["trang_thai"] == "XONG"
    with LocalGia() as moi:
        moi.tags = [{"name": "model-demo"}]
        nap_cau_hinh(moi.url)
        assert hoi()["trang_thai"] == "XONG"
        ban = chay.app.ngan.doc("model_phat_hien", {"id_model": "model-demo"})
        assert ban.gia_tri["url"] == moi.url
        assert ban.gia_tri["loai"] == "ollama"
        assert local.so_luot_hoi == moi.so_luot_hoi == 1


@pytest.mark.parametrize("so_loi", [1, 3])
def test_cas_model_thu_lai_co_gioi_han_khong_goi_cloud(local, monkeypatch, so_loi):
    n = chay.app.ngan
    lo_goc = n.lo
    con = [so_loi]
    def lo_moi():
        lo = lo_goc()
        sua_goc = lo.sua
        def sua(*a, **kw):
            if con[0]:
                con[0] -= 1
                raise NganXungDot()
            sua_goc(*a, **kw)
        lo.sua = sua
        return lo
    monkeypatch.setattr(n, "lo", lo_moi)
    kq = hoi()
    if so_loi == 1:
        assert kq["trang_thai"] == "XONG"
        assert local.so_luot_hoi == 1
    else:
        assert kq["loi"]["ma"] == "NGAN_XUNG_DOT" and kq["loi"]["thu_lai_duoc"]
        assert local.so_luot_hoi == 0


def test_loi_discovery_khong_tai_su_dung_model_cu(local):
    assert hoi()["trang_thai"] == "XONG"
    for _, duong, _, _ in chon_model.CAC_API:
        local.phan_hoi_get[duong] = (503, b"DEMO")
    assert hoi()["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    ban = chay.app.ngan.doc("model_phat_hien", {"id_model": "model-demo"})
    assert ban.gia_tri["kha_dung"] is False and ban.gia_tri["phat_hien_dat"] is False
    assert local.so_luot_hoi == 1
