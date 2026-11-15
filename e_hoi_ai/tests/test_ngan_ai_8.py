"""Hợp đồng ngăn/cấu hình AI-8 chuyển sang CoreGia SDK 2.2.0; chỉ DEMO."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, NganEngine, NganXungDot
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoi_ai.chay import app
from e_hoi_ai.hoi import yeu_cau_cau_hinh
from local_gia import core_demo, nap_cau_hinh


def tao_ngan(pham_vi="engine"):
    phieu = deepcopy(app.phieu)
    phieu.pop("cau_hinh")
    phieu["nang_luc"] = phieu["nang_luc"][:1]
    phieu["chay_thu_demo"] = phieu["chay_thu_demo"][:1]
    phieu["ngan_du_lieu"] = [{"bang": "demo", "ten": "Ngăn DEMO", "pham_vi": pham_vi,
        "khoa": ["ma"], "duy_nhat": [["phap_nhan_id", "ten"]] if pham_vi == "phap_nhan" else [["ten"]],
        "truong": [{"ma": "ma", "kieu": "van_ban"}, {"ma": "ten", "kieu": "van_ban"},
                   {"ma": "dem", "kieu": "so"}, {"ma": "nhan", "kieu": "van_ban"}]}]
    ung_dung = Engine(phieu, thu_muc_goi=app.thu_muc_goi)
    core = CoreGia(ung_dung)
    return core, ung_dung, NganEngine(core.duong_truyen(app.ma), ung_dung._cfg)


def test_lo_nguyen_tu_cas_va_rollback():
    core, _, n = tao_ngan()
    with n.lo() as lo:
        lo.them("demo", {"ma": "DEMO-1", "ten": "DEMO-A", "dem": 1})
        lo.them("demo", {"ma": "DEMO-2", "ten": "DEMO-B", "dem": 2})
    cu = n.doc("demo", {"ma": "DEMO-1"})
    with pytest.raises(NganXungDot) as loi:
        with n.lo() as lo:
            lo.sua("demo", {"ma": "DEMO-1"}, {"dem": 3}, row_version=cu.row_version)
            lo.sua("demo", {"ma": "DEMO-2"}, {"dem": 4}, row_version=0)
    assert loi.value.thu_lai_duoc
    assert n.doc("demo", {"ma": "DEMO-1"}) == cu
    assert n.doc("demo", {"ma": "DEMO-2"}).gia_tri["dem"] == "2"
    with pytest.raises(RuntimeError):
        with n.lo() as lo:
            lo.sua("demo", {"ma": "DEMO-1"}, {"dem": 5}, row_version=cu.row_version)
            raise RuntimeError("DEMO")
    assert n.doc("demo", {"ma": "DEMO-1"}) == cu
    with n.lo() as lo:
        lo.sua("demo", {"ma": "DEMO-1"}, {"dem": 4}, row_version=cu.row_version)
    with pytest.raises(NganXungDot):
        with n.lo() as lo:
            lo.sua("demo", {"ma": "DEMO-1"}, {"dem": 5}, row_version=cu.row_version)
    assert len(core.xem_ngan(app.ma, "demo")) == 2


def test_lay_hoac_tao_hai_luong_chi_tao_mot():
    _, _, n = tao_ngan()
    def tao(_):
        with n.lo() as lo:
            lo.lay_hoac_tao("demo", {"ma": "DEMO"}, {"ten": "DEMO"})
        kq = lo.ket_qua[0]
        ban = n.doc("demo", {"ma": "DEMO"})
        assert kq.id == ban.id and kq.row_version == ban.row_version
        return kq.da_tao
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(tao, range(2))) == [False, True]
    assert len(n.tim("demo").danh_sach) == 1


def test_duy_nhat_phap_nhan_khong_doc_cheo():
    core, ung_dung, n = tao_ngan("phap_nhan")
    with pytest.raises(LoiNghiepVu, match="Cần nhận việc"):
        n.tim("demo")
    @ung_dung.nang_luc("ai.hoi_tai_lieu@1")
    def xu_ly(viec):
        a = viec.ngan
        if viec.ngu_canh["phap_nhan_id"] == "DEMO-B":
            assert a.doc("demo", {"ma": "DEMO-1"}) is None
            assert a.tim("demo").danh_sach == []
        with a.lo() as lo:
            lo.them("demo", {"ma": "DEMO-1", "ten": "DEMO"})
        with pytest.raises(NganXungDot):
            with a.lo() as lo:
                lo.them("demo", {"ma": "DEMO-2", "ten": "DEMO"})
        with a.lo() as lo:
            lo.lay_hoac_tao("demo", {"ten": "DEMO"}, {"ma": "DEMO-2"})
        assert not lo.ket_qua[0].da_tao
        assert a.doc("demo", {"ma": "DEMO-2"}) is None
        with pytest.raises(LoiNghiepVu):
            with a.lo() as lo:
                lo.them("demo", {"ma": "DEMO-3", "phap_nhan_id": "DEMO-KHAC"})
        return {"loai": "truong", "truong": {"tra_loi": "DEMO", "co_can_cu": False,
            "trich_dan": "", "model": "DEMO", "ly_do_chon_model": "DEMO"}}
    for pn in ["DEMO-A", "DEMO-B"]:
        ma = core.giao_viec("ai.hoi_tai_lieu@1", {"loai": "van_ban", "van_ban": "DEMO"},
                           {"ma_prompt": "demo.hoi", "phien_ban_prompt": "1"}, phap_nhan_id=pn)
        core.chay(ung_dung)
        assert core.xem(ma)["trang_thai"] == "XONG"
    assert {d["phap_nhan_id"] for d in core.xem_ngan(app.ma, "demo")} == {"DEMO-A", "DEMO-B"}


def test_ban_sao_phan_trang_va_tran_lo():
    _, _, n = tao_ngan()
    with n.lo() as lo:
        for i in range(3):
            lo.them("demo", {"ma": str(i), "ten": f"DEMO-{i}", "nhan": "DEMO"})
    trang = n.tim("demo", gioi_han=2)
    assert len(trang.danh_sach) == 2 and trang.tiep
    assert len(n.tim("demo", gioi_han=2, tiep=trang.tiep).danh_sach) == 1
    trang.danh_sach[0].gia_tri["nhan"] = "KHAC"
    assert n.doc("demo", {"ma": trang.danh_sach[0].gia_tri["ma"]}).gia_tri["nhan"] == "DEMO"
    with pytest.raises(LoiNghiepVu) as loi:
        with n.lo() as lo:
            for i in range(101):
                lo.them("demo", {"ma": str(i + 10), "ten": f"DEMO-{i + 10}"})
    assert loi.value.ma == "NGAN_LO_QUA_LON"
    assert len(n.tim("demo").danh_sach) == 3


def test_khong_con_ngan_thay_the_hay_canh_bao_ram(capsys):
    ung_dung = Engine.tu_khai_bao(app.thu_muc_goi / "engine.json")
    assert isinstance(ung_dung.ngan, NganEngine)
    with pytest.raises(LoiNghiepVu) as loi:
        ung_dung.ngan.tim("model_phat_hien")
    assert loi.value.ma == "ENGINE_CHUA_SAN_SANG"
    assert not capsys.readouterr().err


def test_doc_cau_hinh_dien_mac_dinh_khong_ghi_nguoc_va_nap_lai():
    core = core_demo()
    assert core._doc_cau_hinh(app.ma)["cau_hinh"] == {"quy_tac_model": []}
    gia_tri = {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 1}}
    core.dat_cau_hinh(app.ma, gia_tri)
    ch = core._doc_cau_hinh(app.ma)["cau_hinh"]
    assert ch["quy_tac_model"] == [] and "quy_tac_model" not in gia_tri
    nap_cau_hinh("http://127.0.0.1:12346", thoi_han=2)
    assert core._doc_cau_hinh(app.ma)["cau_hinh"]["local_ai"]["timeout_giay"] == 2


def test_uu_tien_ban_chup_cau_hinh_cua_viec():
    viec = SimpleNamespace(cau_hinh={"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 5}})
    nap_cau_hinh("http://127.0.0.1:12346", thoi_han=2)
    assert yeu_cau_cau_hinh(viec)["local_ai"]["timeout_giay"] == 5


@pytest.mark.parametrize("timeout", [True, 0, -1, float("inf"), 601])
def test_cau_hinh_sai_khong_lo_noi_dung(timeout):
    with pytest.raises(LoiNghiepVu) as loi:
        yeu_cau_cau_hinh(SimpleNamespace(cau_hinh={
            "local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": timeout}}))
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"


@pytest.mark.parametrize("ma", ["NGAN_XUNG_DOT", "NGAN_DU_LIEU_SAI", "NGAN_KHONG_CO_BANG"])
@pytest.mark.parametrize("chi_so_demo", [0, 2])
def test_loi_ngan_tai_bien_sdk_khong_lo_chi_tiet(monkeypatch, capsys, ma, chi_so_demo):
    from local_gia import LocalGia
    def tim_loi(*args, **kwargs):
        raise LoiNghiepVu(ma, "Dữ liệu ngăn DEMO không hợp lệ.", thu_lai_duoc=ma == "NGAN_XUNG_DOT")
    monkeypatch.setattr(NganEngine, "tim", tim_loi)
    with LocalGia() as may:
        nap_cau_hinh(may.url)
        vd = app.phieu["chay_thu_demo"][chi_so_demo]
        kq = core_demo().chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"] == {"ma": ma, "thong_diep": "Dữ liệu ngăn DEMO không hợp lệ.",
                         "thu_lai_duoc": ma == "NGAN_XUNG_DOT"}
    assert "Traceback" not in capsys.readouterr().err


def test_khong_doc_cau_hinh_may_ke_ca_bien_tro_tep_demo(monkeypatch, tmp_path):
    from e_hoi_ai import cau_hinh_may
    monkeypatch.setattr(cau_hinh_may, "doc_cau_hinh", lambda: pytest.fail("Không đọc tệp cấu hình."))
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "DEMO.json"))
    for vd in app.phieu["chay_thu_demo"]:
        kq = core_demo().chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
        assert kq["loi"]["ma"] == "CHUA_CAU_HINH"
