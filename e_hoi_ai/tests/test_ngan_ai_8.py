"""Hợp đồng RAM AI-8; dữ liệu DEMO, không mạng hay lưu bền."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoi_ai.chay import app
from e_hoi_ai.cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from e_hoi_ai.hoi import yeu_cau_cau_hinh
from e_hoi_ai.ngan import Ngan, NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan
from local_gia import nap_cau_hinh

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"
SCHEMA = json.loads((GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))
KHAI = [{"bang": "demo", "khoa": ["id"], "duy_nhat": [["ten"]], "pham_vi": "phap_nhan"}]
KHAI_ENGINE = [{"bang": "demo", "khoa": ["id"], "pham_vi": "engine"}]


def test_lo_nguyen_tu_cas_va_rollback():
    n = NganBoNho(KHAI_ENGINE)
    assert isinstance(n, Ngan)
    with n.lo() as lo:
        lo.them("demo", {"id": "DEMO-1"}, {"dem": 1})
        lo.them("demo", {"id": "DEMO-2"}, {"dem": 2})
    cu = n.doc("demo", {"id": "DEMO-1"})
    with pytest.raises(NganXungDot) as loi:
        with n.lo() as lo:
            lo.sua("demo", {"id": "DEMO-1"}, {"dem": 3}, row_version=cu.row_version)
            lo.xoa("demo", {"id": "DEMO-2"}, row_version=cu.row_version)
    assert loi.value.thu_lai_duoc
    assert n.doc("demo", {"id": "DEMO-1"}) == cu
    assert n.doc("demo", {"id": "DEMO-2"}) is not None
    with pytest.raises(RuntimeError):
        with n.lo() as lo:
            lo.xoa("demo", {"id": "DEMO-1"}, row_version=cu.row_version)
            raise RuntimeError("DEMO")
    assert n.doc("demo", {"id": "DEMO-1"}) == cu
    with n.lo() as lo:
        lo.xoa("demo", {"id": "DEMO-1"}, row_version=cu.row_version)
    with n.lo() as lo:
        lo.them("demo", {"id": "DEMO-1"}, {"dem": 4})
    with pytest.raises(NganXungDot):
        with n.lo() as lo:
            lo.sua("demo", {"id": "DEMO-1"}, {"dem": 5}, row_version=cu.row_version)


def test_lay_hoac_tao_hai_luong_chi_tao_mot():
    n = NganBoNho(KHAI_ENGINE)
    def tao(_):
        with n.lo() as lo:
            kq = lo.lay_hoac_tao("demo", {"id": "DEMO"}, {"ten": "DEMO"})
        assert kq.ban_ghi.gia_tri == kq.gia_tri
        assert kq.ban_ghi.row_version == kq.row_version
        return kq.da_tao
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(tao, range(2))) == [False, True]
    assert len(n.tim("demo").danh_sach) == 1


def test_duy_nhat_phap_nhan_khong_doc_cheo():
    n = NganBoNho(KHAI)
    a, b = n.cho_phap_nhan("DEMO-A"), n.cho_phap_nhan("DEMO-B")
    with a.lo() as lo:
        lo.them("demo", {"id": "DEMO-1"}, {"ten": "DEMO"})
    assert b.doc("demo", {"id": "DEMO-1"}) is None
    assert b.tim("demo").danh_sach == []
    with b.lo() as lo:
        lo.them("demo", {"id": "DEMO-1"}, {"ten": "DEMO"})
    with pytest.raises(NganXungDot):
        with a.lo() as lo:
            lo.them("demo", {"id": "DEMO-2"}, {"ten": "DEMO"})
    with a.lo() as lo:
        kq = lo.lay_hoac_tao("demo", {"ten": "DEMO"}, {"id": "DEMO-2"})
    assert kq.da_tao is False
    assert a.doc("demo", {"id": "DEMO-2"}) is None
    with pytest.raises(NganKhongHopLe):
        a.doc("demo", {"phap_nhan_id": "DEMO-B"})
    with pytest.raises(NganKhongHopLe):
        with a.lo() as lo:
            lo.them("demo", {"id": "DEMO-2"}, {"phap_nhan_id": "DEMO-B"})


def test_ban_sao_phan_trang_va_tran_lo():
    n = NganBoNho(KHAI_ENGINE)
    with n.lo() as lo:
        for i in range(3):
            lo.them("demo", {"id": i}, {"nhan": ["DEMO"]})
    trang = n.tim("demo", gioi_han=2)
    assert len(trang.danh_sach) == 2 and trang.tiep
    assert len(n.tim("demo", gioi_han=2, tiep=trang.tiep).danh_sach) == 1
    trang.danh_sach[0].gia_tri["nhan"].append("KHAC")
    assert n.doc("demo", {"id": 0}).gia_tri["nhan"] == ["DEMO"]
    with pytest.raises(NganKhongHopLe):
        with n.lo() as lo:
            for i in range(101):
                lo.them("demo", {"id": i + 10}, {})
    assert len(n.tim("demo").danh_sach) == 3


def test_chon_ngan_that_va_canh_bao_mot_lan(capsys, monkeypatch):
    from e_hoi_ai import ngan
    monkeypatch.setattr(ngan, "_DA_CANH_BAO", False)
    a = SimpleNamespace()
    assert chon_ngan(a) is chon_ngan(a)
    assert capsys.readouterr().err.count("Đang lưu tạm trong bộ nhớ") == 1
    that = SimpleNamespace(ngan=object())
    assert chon_ngan(that) is that.ngan
    assert not capsys.readouterr().err


def test_doc_cau_hinh_dien_mac_dinh_khong_ghi_nguoc_va_nap_lai():
    n = app.ngan
    assert doc_cau_hinh(n, SCHEMA) is None
    with n.lo() as lo:
        lo.them("cau_hinh", {}, {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 1}})
    ch = doc_cau_hinh(n, SCHEMA)
    assert ch["quy_tac_model"] == []
    assert "quy_tac_model" not in n.doc("cau_hinh", {}).gia_tri
    nap_cau_hinh("http://127.0.0.1:12346", thoi_han=2)
    assert yeu_cau_cau_hinh(SimpleNamespace())["local_ai"]["timeout_giay"] == 2


def test_uu_tien_ngan_cua_viec_theo_sdk_21():
    n = NganBoNho()
    with n.lo() as lo:
        lo.them("cau_hinh", {}, {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 5}})
    assert app.ngan.doc("cau_hinh", {}) is None
    assert yeu_cau_cau_hinh(SimpleNamespace(ngan=n))["local_ai"]["timeout_giay"] == 5


@pytest.mark.parametrize("timeout", [True, 0, -1, float("inf"), 601])
def test_cau_hinh_sai_khong_lo_noi_dung(timeout):
    # Ngăn thật từ chối số không hữu hạn trước; ngăn giả này kiểm thêm lớp đọc cấu hình.
    n = SimpleNamespace(doc=lambda *a: SimpleNamespace(gia_tri={
        "local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": timeout}}))
    with pytest.raises(LoiNghiepVu) as loi:
        yeu_cau_cau_hinh(SimpleNamespace(ngan=n))
    assert loi.value.ma == "CAU_HINH_KHONG_HOP_LE"


@pytest.mark.parametrize("loai_loi", [NganXungDot, NganKhongHopLe, CauHinhKhongHopLe])
@pytest.mark.parametrize("chi_so_demo", [0, 2])
def test_loi_ngan_tai_bien_sdk_khong_lo_chi_tiet(monkeypatch, capsys, loai_loi, chi_so_demo):
    def doc_loi(*args):
        raise loai_loi()

    monkeypatch.setattr(app.ngan, "doc", doc_loi)
    vd = app.phieu["chay_thu_demo"][chi_so_demo]
    kq = CoreGia().chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"] == {"ma": loai_loi.ma, "thong_diep": loai_loi.thong_diep,
                         "thu_lai_duoc": loai_loi.thu_lai_duoc}
    assert "Traceback" not in capsys.readouterr().err


def test_khong_doc_cau_hinh_may_ke_ca_bien_tro_tep_demo(monkeypatch, tmp_path):
    from e_hoi_ai import cau_hinh_may
    monkeypatch.setattr(cau_hinh_may, "doc_cau_hinh", lambda: pytest.fail("Không đọc tệp cấu hình."))
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tmp_path / "DEMO.json"))
    for vd in app.phieu["chay_thu_demo"]:
        kq = CoreGia().chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
        assert kq["loi"]["ma"] == "CHUA_CAU_HINH"


@pytest.mark.parametrize("ten", ["ngan.py", "cau_hinh.py"])
def test_bam_mau_chung_ngan_0(ten):
    goc = Path(__file__).resolve().parents[2]
    lf = lambda p: p.read_bytes().replace(b"\r\n", b"\n")
    assert sha256(lf(goc / "_chung" / "mau-ma" / ten)).digest() == sha256(lf(GOI / "e_hoi_ai" / ten)).digest()
