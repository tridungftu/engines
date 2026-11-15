"""Tích hợp NGAN-0 và hành vi cấu hình/snapshot riêng của engine."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import threading
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from e_trich_xuat.chay import (
    CAU_CHUA_CAU_HINH, KHAI_BAO_NGAN, SCHEMA_CAU_HINH, EngineTrichXuat,
    ghim_cau_hinh, tao_app,
)
from e_trich_xuat import ngan as mo_ngan
from e_trich_xuat.ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan


KHOA = {}
KHAI = [{"bang": "demo", "pham_vi": "phap_nhan", "khoa": ["ma_tuong_quan"],
         "duy_nhat": [["phap_nhan_id", "bam_noi_dung"]]}]


def dat(ngan, v):
    with ngan.lo() as lo:
        kq = lo.them("cau_hinh", KHOA, v)
    return kq


def test_mac_dinh_chi_dien_cho_ban_ghi_da_co_khong_ghi_nguoc():
    ngan = NganBoNho()
    assert doc_cau_hinh(ngan, SCHEMA_CAU_HINH) is None
    trang = ngan.tim("cau_hinh", loc={}, gioi_han=500)
    assert trang.danh_sach == [] and trang.tiep is None
    kq = dat(ngan, {})
    truoc = ngan.doc("cau_hinh", KHOA)
    assert doc_cau_hinh(ngan, SCHEMA_CAU_HINH) == {"ngan_sach_token_vao_toi_da": 16000}
    assert ngan.doc("cau_hinh", KHOA) == truoc
    assert truoc.gia_tri == kq.gia_tri == {}
    assert kq.ban_ghi == truoc and kq.row_version == truoc.row_version and kq.da_tao


@pytest.mark.parametrize("v", [{"ngan_sach_token_vao_toi_da": 1023}, {"ngan_sach_token_vao_toi_da": 100001},
    {"ngan_sach_token_vao_toi_da": True}, {"ngan_sach_token_vao_toi_da": 16000.5},
    {"ngan_sach_token_vao_toi_da": "16000"}, {"ngan_sach_token_vao_toi_da": 10 ** 1000},
    {"truong_la": "DEMO"}, {"gia_tri": {}}, {"ma": "mac_dinh"}])
def test_cau_hinh_sai_bi_tu_choi(v):
    ngan = NganBoNho()
    dat(ngan, v)
    with pytest.raises(CauHinhKhongHopLe):
        doc_cau_hinh(ngan, SCHEMA_CAU_HINH)


def test_cau_hinh_khong_phai_dict_hoac_nan_bi_ngan_tu_choi():
    ngan = NganBoNho()
    for v in [[], None, {"DEMO": float("nan")}]:
        with pytest.raises(NganKhongHopLe):
            dat(ngan, v)
    assert ngan.doc("cau_hinh", KHOA) is None


def test_cas_sai_khong_ghi_lo_va_exception_trong_with_khong_ghi():
    ngan = NganBoNho(KHAI)
    dat(ngan, {"ngan_sach_token_vao_toi_da": 16000})
    cu = ngan.doc("cau_hinh", KHOA)
    with pytest.raises(NganXungDot) as exc:
        with ngan.lo() as lo:
            lo.them("demo", {"phap_nhan_id": "pn-DEMO", "ma_tuong_quan": "DEMO-khac"},
                    {"bam_noi_dung": "bam-DEMO"})
            lo.sua("cau_hinh", KHOA, {"ngan_sach_token_vao_toi_da": 20000}, row_version=cu.row_version + 1)
    assert exc.value.thu_lai_duoc is True
    assert ngan.doc("cau_hinh", KHOA) == cu
    assert ngan.doc("demo", {"phap_nhan_id": "pn-DEMO", "ma_tuong_quan": "DEMO-khac"}) is None
    with pytest.raises(RuntimeError):
        with ngan.lo() as lo:
            lo.sua("cau_hinh", KHOA, {"ngan_sach_token_vao_toi_da": 20000}, row_version=cu.row_version)
            raise RuntimeError("DEMO lỗi giữa lô")
    assert ngan.doc("cau_hinh", KHOA) == cu


def test_sua_xoa_cung_lo_va_phien_ban_khong_aba():
    ngan = NganBoNho()
    dat(ngan, {})
    cu = ngan.doc("cau_hinh", KHOA)
    with ngan.lo() as lo:
        lo.sua("cau_hinh", KHOA, {"ngan_sach_token_vao_toi_da": 20000}, row_version=cu.row_version)
    moi = ngan.doc("cau_hinh", KHOA)
    assert moi.row_version > cu.row_version
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.xoa("cau_hinh", KHOA, row_version=cu.row_version)
    with ngan.lo() as lo:
        lo.xoa("cau_hinh", KHOA, row_version=moi.row_version)
        lo.them("cau_hinh", KHOA, {})
    assert ngan.doc("cau_hinh", KHOA).row_version > moi.row_version


def test_hai_luong_lay_hoac_tao_theo_duy_nhat_chi_tao_mot_ban():
    ngan = NganBoNho(KHAI)
    chan = threading.Barrier(2)

    def lam(i):
        chan.wait(timeout=5)
        with ngan.lo() as lo:
            kq = lo.lay_hoac_tao("demo", {"phap_nhan_id": "pn-DEMO", "bam_noi_dung": "bam-DEMO"},
                                {"ma_tuong_quan": f"luot-DEMO-{i}"})
        return kq

    with ThreadPoolExecutor(max_workers=2) as pool:
        kq = list(pool.map(lam, [1, 2]))
    assert sorted(k.da_tao for k in kq) == [False, True]
    assert kq[0].ban_ghi == kq[1].ban_ghi
    assert len(ngan.tim("demo", {"phap_nhan_id": "pn-DEMO"}).danh_sach) == 1


def test_duy_nhat_va_thay_chi_muc_trong_lo():
    ngan = NganBoNho(KHAI)
    with ngan.lo() as lo:
        lo.them("demo", {"phap_nhan_id": "pn-DEMO", "ma_tuong_quan": "DEMO-1"}, {"bam_noi_dung": "a"})
    khoa = {"phap_nhan_id": "pn-DEMO", "ma_tuong_quan": "DEMO-1"}
    cu = ngan.doc("demo", khoa)
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("demo", {"phap_nhan_id": "pn-DEMO", "ma_tuong_quan": "DEMO-2"}, {"bam_noi_dung": "a"})
    with ngan.lo() as lo:
        lo.sua("demo", khoa, {"bam_noi_dung": "b"}, row_version=cu.row_version)
        lo.them("demo", {"phap_nhan_id": "pn-DEMO", "ma_tuong_quan": "DEMO-2"}, {"bam_noi_dung": "a"})
    assert len(ngan.tim("demo", {"phap_nhan_id": "pn-DEMO"}).danh_sach) == 2


def test_ngan_goc_bat_buoc_phap_nhan_trong_khoa_va_loc_khong_doc_cheo():
    ngan = NganBoNho(KHAI)
    for pn in ["pn-DEMO-A", "pn-DEMO-B"]:
        with ngan.lo() as lo:
            lo.them("demo", {"phap_nhan_id": pn, "ma_tuong_quan": "DEMO-1"}, {"bam_noi_dung": "DEMO"})
    assert ngan.doc("demo", {"phap_nhan_id": "pn-DEMO-A", "ma_tuong_quan": "DEMO-1"}).gia_tri["phap_nhan_id"] == "pn-DEMO-A"
    assert len(ngan.tim("demo", loc={"phap_nhan_id": "pn-DEMO-B"}).danh_sach) == 1
    with pytest.raises(NganKhongHopLe):
        ngan.doc("demo", {"ma_tuong_quan": "DEMO-1"})
    with pytest.raises(NganKhongHopLe):
        ngan.tim("demo", loc={})
    rieng = ngan.cho_phap_nhan("pn-DEMO-A")
    assert rieng.doc("demo", {"ma_tuong_quan": "DEMO-1"}).gia_tri["phap_nhan_id"] == "pn-DEMO-A"
    with pytest.raises(NganKhongHopLe):
        rieng.tim("demo", loc={"phap_nhan_id": "pn-DEMO-B"})


def test_tim_phan_trang_va_doc_khong_cho_sua_kho_ngam():
    ngan = NganBoNho(KHAI, phap_nhan_id="pn-DEMO")
    with ngan.lo() as lo:
        for ma in ["DEMO-1", "DEMO-2", "DEMO-3"]:
            lo.them("demo", {"ma_tuong_quan": ma}, {"bam_noi_dung": ma, "chi_tiet": {}})
    ds = ngan.tim("demo", loc={}, gioi_han=2)
    assert len(ds.danh_sach) == 2 and ds.tiep is not None
    assert len(ngan.tim("demo", loc={}, gioi_han=2, tiep=ds.tiep).danh_sach) == 1
    row = ngan.doc("demo", {"ma_tuong_quan": "DEMO-1"})
    row.gia_tri["chi_tiet"]["DEMO"] = "khong luu"
    assert ngan.doc("demo", {"ma_tuong_quan": "DEMO-1"}).gia_tri["chi_tiet"] == {}
    for gioi_han in [0, 501, True]:
        with pytest.raises(NganKhongHopLe):
            ngan.tim("demo", gioi_han=gioi_han)


def test_chon_ngan_uu_tien_sdk_canh_bao_mot_lan_va_ram_mat_khi_phien_moi(monkeypatch, capsys):
    monkeypatch.setattr(mo_ngan, "_DA_CANH_BAO", False)
    sdk = object()
    assert chon_ngan(SimpleNamespace(ngan=sdk)) is sdk
    assert capsys.readouterr().err == ""
    app = SimpleNamespace()
    ngan = chon_ngan(app)
    dat(ngan, {})
    assert chon_ngan(app) is ngan
    app_moi = SimpleNamespace()
    assert chon_ngan(app_moi).doc("cau_hinh", KHOA) is None
    assert capsys.readouterr().err == "Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng\n"
    app.ngan = sdk
    assert chon_ngan(app) is sdk


def test_ghim_cau_hinh_doc_mot_lan_va_thay_doi_khong_sua_snapshot():
    app = tao_app()
    app.ngan = NganBoNho()
    with pytest.raises(LoiNghiepVu) as exc:
        ghim_cau_hinh(SimpleNamespace(), app)
    assert (exc.value.ma, exc.value.thong_diep) == ("CHUA_CAU_HINH", CAU_CHUA_CAU_HINH)
    dat(app.ngan, {})
    ban1 = ghim_cau_hinh(SimpleNamespace(), app)
    with app.ngan.lo() as lo:
        lo.sua("cau_hinh", KHOA, {"ngan_sach_token_vao_toi_da": 20000}, row_version=ban1["phien_ban_cau_hinh"])
    ban2 = ghim_cau_hinh(SimpleNamespace(), app)
    assert ban1["gia_tri"]["ngan_sach_token_vao_toi_da"] == 16000
    assert ban2["gia_tri"]["ngan_sach_token_vao_toi_da"] == 20000
    assert ban1["phien_ban_cau_hinh"] < ban2["phien_ban_cau_hinh"]
    # SDK 2.1 cung cấp bản chụp gắn với việc: không đọc cấu hình mới từ ngăn.
    viec = SimpleNamespace(cau_hinh=ban1["gia_tri"], phien_ban_cau_hinh=ban1["phien_ban_cau_hinh"])
    assert ghim_cau_hinh(viec, app) == ban1


def test_snapshot_chi_doc_mot_ban_va_ngan_cua_viec_duoc_uu_tien():
    ngan = NganBoNho()
    dat(ngan, {})
    dem = []

    class Cong:
        def doc(self, bang, khoa):
            dem.append((bang, khoa))
            return ngan.doc(bang, khoa)

    kq = ghim_cau_hinh(SimpleNamespace(ngan=Cong()), SimpleNamespace(ngan=object()))
    assert kq["gia_tri"]["ngan_sach_token_vao_toi_da"] == 16000
    assert dem == [("cau_hinh", KHOA)]


def test_tao_app_khai_bao_ngan_chung_va_giu_ngan_sdk(monkeypatch):
    app = tao_app()
    assert KHAI_BAO_NGAN[0]["khoa"] == []
    assert isinstance(app.ngan, NganBoNho)
    kq = dat(app.ngan, {})
    assert kq.da_tao and app.ngan.doc("cau_hinh", {}).gia_tri == {}
    with pytest.raises(NganKhongHopLe):
        app.ngan.doc("cau_hinh", {"ma": "mac_dinh"})
    with pytest.raises(NganKhongHopLe):
        app.ngan.doc("bang_chua_khai_DEMO", {})

    # App SDK đã có ngăn phải được giữ nguyên, không ghi cấu hình mặc định.
    sdk = object()
    app = EngineTrichXuat(deepcopy(app.phieu))
    app.ngan = sdk
    monkeypatch.setattr(EngineTrichXuat, "tu_khai_bao", lambda *a: app)
    assert tao_app().ngan is sdk


@pytest.mark.parametrize("loi", [NganXungDot, NganKhongHopLe, CauHinhKhongHopLe])
def test_loi_cong_chung_duoc_doi_sang_loi_nghiep_vu(loi):
    class CongLoi:
        def doc(self, bang, khoa):
            raise loi()

    with pytest.raises(LoiNghiepVu) as exc:
        ghim_cau_hinh(SimpleNamespace(ngan=CongLoi()), SimpleNamespace())
    assert (exc.value.ma, exc.value.thong_diep, exc.value.thu_lai_duoc) == (
        loi.ma, loi.thong_diep, loi.thu_lai_duoc)
    assert exc.value.__suppress_context__


def test_snapshot_sdk_duoc_sao_chep_va_kiem_schema():
    app = SimpleNamespace(ngan=object())  # Không được đọc ngăn nếu SDK đã ghim.
    viec = SimpleNamespace(cau_hinh={}, phien_ban_cau_hinh=7)
    ban = ghim_cau_hinh(viec, app)
    assert ban == {"gia_tri": {"ngan_sach_token_vao_toi_da": 16000}, "phien_ban_cau_hinh": 7}
    assert viec.cau_hinh == {}
    ban["gia_tri"]["ngan_sach_token_vao_toi_da"] = 20000
    assert ghim_cau_hinh(viec, app)["gia_tri"]["ngan_sach_token_vao_toi_da"] == 16000
    viec.cau_hinh = {"ngan_sach_token_vao_toi_da": True}
    with pytest.raises(LoiNghiepVu) as exc:
        ghim_cau_hinh(viec, app)
    assert exc.value.ma == CauHinhKhongHopLe.ma
    viec.cau_hinh = None
    with pytest.raises(LoiNghiepVu) as exc:
        ghim_cau_hinh(viec, app)
    assert exc.value.ma == "CHUA_CAU_HINH"


def test_buoc_can_cau_hinh_tra_loi_nghiep_vu_bang_core_gia():
    # Năng lực kiểm chỉ thuộc test, không được khai hoặc đăng ký vào gói thật.
    phieu = deepcopy(tao_app().phieu)
    phieu["nang_luc"] = [{"ma": "demo.cau_hinh@1", "ten": "Kiểm cấu hình DEMO", "nhan": ["van_ban"],
                           "tra": "van_ban", "gioi_han": {"thoi_han_giay": 10}}]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu)
    app.ngan = NganBoNho()

    @app.nang_luc("demo.cau_hinh@1")
    def lam(viec):
        return {"loai": "van_ban", "van_ban": str(ghim_cau_hinh(viec, app)["gia_tri"]["ngan_sach_token_vao_toi_da"])}

    kq = CoreGia().chay_thu(app, "demo.cau_hinh@1", {"loai": "van_ban", "van_ban": "DEMO"})
    assert kq["loi"]["ma"] == "CHUA_CAU_HINH" and kq["loi"]["thong_diep"] == CAU_CHUA_CAU_HINH
    dat(app.ngan, {})
    kq = CoreGia().chay_thu(app, "demo.cau_hinh@1", {"loai": "van_ban", "van_ban": "DEMO"})
    assert kq["trang_thai"] == "XONG" and kq["ket_qua"]["van_ban"] == "16000"
    cu = app.ngan.doc("cau_hinh", KHOA)
    with app.ngan.lo() as lo:
        lo.sua("cau_hinh", KHOA, {"ngan_sach_token_vao_toi_da": True}, row_version=cu.row_version)
    kq = CoreGia().chay_thu(app, "demo.cau_hinh@1", {"loai": "van_ban", "van_ban": "DEMO"})
    assert kq["loi"] == {"ma": CauHinhKhongHopLe.ma,
                         "thong_diep": CauHinhKhongHopLe.thong_diep, "thu_lai_duoc": False}
