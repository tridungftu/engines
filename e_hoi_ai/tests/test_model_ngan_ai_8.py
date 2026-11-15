"""AI-8: model ngăn trên CoreGia và Local giả; 0 lượt Cloud."""
import pytest

from e_hoi_ai import chay, chon_model
from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganEngine
from local_gia import core_demo
from local_gia import LocalGia, nap_cau_hinh
from test_hoi_tai_lieu import hoi, khong_mang_ngoai_va_khong_cloud, local


def test_model_ghi_ngan_khong_trung_id_va_loai_bo_model_mat(local):
    local.models = [{"id": "model-demo"}, {"id": "model-demo-b"}]
    assert hoi()["trang_thai"] == "XONG"
    n = chay.app.ngan
    assert len(n.tim("model_phat_hien").danh_sach) == 2
    a = n.doc("model_phat_hien", {"id_model": "model-demo"})
    assert a.gia_tri["kha_dung"] and a.gia_tri["loai"] == "openai_compatible"
    assert a.gia_tri["kiem_luc"] and a.gia_tri["url"] == local.url
    local.models.pop(0)
    assert hoi()["ket_qua"]["truong"]["model"] == "model-demo-b"
    assert not n.doc("model_phat_hien", {"id_model": "model-demo"}).gia_tri["kha_dung"]
    assert len(n.tim("model_phat_hien").danh_sach) == 2


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
    core_demo().gay_xung_dot_ngan("model_phat_hien", so_loi)
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


def test_catalog_phan_trang_theo_ngan_chung():
    n = chay.app.ngan
    assert {b["bang"] for b in chay.app.phieu["ngan_du_lieu"]} == {"model_phat_hien"}
    models = tuple(chon_model.ModelLocal(f"model-demo-{i:04}", True) for i in range(501))
    catalog = chon_model.DanhSachModel("openai_compatible", chon_model.CAC_API[-1], models)
    url = "http://127.0.0.1:12345"
    chon_model._luu_catalog(n, url, catalog)
    ds = chon_model._doc_models(n, url)
    assert len(ds) == 501
    assert {b.gia_tri["id_model"] for b in ds} == {m.ma for m in models}
    assert all(b.gia_tri["kha_dung"] for b in ds)


def test_loi_ngan_model_khong_goi_local(local, monkeypatch, capsys):
    def tim_loi(*args, **kwargs):
        raise LoiNghiepVu("NGAN_DU_LIEU_SAI", "Dữ liệu ngăn chưa đúng khai báo.")

    monkeypatch.setattr(NganEngine, "tim", tim_loi)
    kq = hoi()
    assert kq["loi"]["ma"] == "NGAN_DU_LIEU_SAI"
    assert not kq["loi"]["thu_lai_duoc"]
    assert local.so_luot_hoi == 0
    assert "Traceback" not in capsys.readouterr().err


def test_thu_tu_model_so_khong_so_chuoi(local):
    local.models = [{"id": f"model-demo-{i}", "remote_model": "DEMO"} if i < 9
                    else {"id": f"model-demo-{i}"} for i in range(12)]
    assert hoi()["ket_qua"]["truong"]["model"] == "model-demo-9"
    assert len(core_demo().xem_ngan(chay.app.ma, "model_phat_hien")) == 12


def test_catalog_con_sau_khi_tao_lai_app(local):
    assert hoi()["trang_thai"] == "XONG"
    truoc = core_demo().xem_ngan(chay.app.ma, "model_phat_hien")
    # Tiến trình mới nối lại cùng Core: catalog thuộc Core, không thuộc RAM engine.
    from kho_tri_thuc_sdk.engine import Engine
    ung_dung = Engine.tu_khai_bao(chay.app.thu_muc_goi / "engine.json")
    core_demo().nap_engine(ung_dung)
    n = NganEngine(core_demo().duong_truyen(ung_dung.ma), ung_dung._cfg)
    assert n.doc("model_phat_hien", {"id_model": "model-demo"}).gia_tri["kha_dung"]
    assert core_demo().xem_ngan(ung_dung.ma, "model_phat_hien") == truoc
