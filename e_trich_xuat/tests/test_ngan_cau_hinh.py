"""Hợp đồng ngăn tạm: nguyên tử/CAS/phạm vi và cấu hình chỉ qua ngăn."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import threading
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.cau_hinh import doc_cau_hinh
from e_trich_xuat.chay import CAU_CHUA_CAU_HINH, SCHEMA_CAU_HINH, ghim_cau_hinh, tao_app
from e_trich_xuat import ngan as mo_ngan
from e_trich_xuat.ngan import NganBoNho, NganXungDot, chon_ngan


KHOA = {"ma": "mac_dinh"}
KHAI = [{"bang": "demo", "pham_vi": "phap_nhan", "khoa": ["ma_tuong_quan"],
         "duy_nhat": [["phap_nhan_id", "bam_noi_dung"]]}]


def dat(ngan, v):
    with ngan.lo() as lo:
        lo.them("cau_hinh", KHOA, {"gia_tri": v})


def test_mac_dinh_chi_dien_cho_ban_ghi_da_co_khong_ghi_nguoc():
    ngan = NganBoNho()
    assert doc_cau_hinh(ngan, SCHEMA_CAU_HINH) is None
    assert ngan.tim("cau_hinh", loc={}, gioi_han=500) == {"danh_sach": [], "tiep": None}
    dat(ngan, {})
    truoc = ngan.doc("cau_hinh", KHOA)
    assert doc_cau_hinh(ngan, SCHEMA_CAU_HINH) == {"ngan_sach_token_vao_toi_da": 16000}
    assert ngan.doc("cau_hinh", KHOA) == truoc
    assert truoc.gia_tri["gia_tri"] == {}


@pytest.mark.parametrize("v", [{"ngan_sach_token_vao_toi_da": 1023}, {"ngan_sach_token_vao_toi_da": 100001},
    {"ngan_sach_token_vao_toi_da": True}, {"ngan_sach_token_vao_toi_da": 16000.5},
    {"ngan_sach_token_vao_toi_da": "16000"}, {"ngan_sach_token_vao_toi_da": 10 ** 1000},
    {"truong_la": "DEMO"}, [], None])
def test_cau_hinh_sai_bi_tu_choi(v):
    ngan = NganBoNho()
    dat(ngan, v)
    with pytest.raises(ValueError, match="Cấu hình không đúng"):
        doc_cau_hinh(ngan, SCHEMA_CAU_HINH)


def test_gioi_han_json_64k_khong_nhan_nan():
    ngan = NganBoNho()
    for v in [{"DEMO": "D" * 65536}, {"DEMO": float("nan")}]:
        with pytest.raises(ValueError):
            dat(ngan, v)
    assert ngan.doc("cau_hinh", KHOA) is None


def test_cas_sai_khong_ghi_lo_va_exception_trong_with_khong_ghi():
    ngan = NganBoNho()
    dat(ngan, {"ngan_sach_token_vao_toi_da": 16000})
    cu = ngan.doc("cau_hinh", KHOA)
    with pytest.raises(NganXungDot) as exc:
        with ngan.lo() as lo:
            lo.them("cau_hinh", {"ma": "DEMO-khac"}, {"gia_tri": {}})
            lo.sua("cau_hinh", KHOA, {"gia_tri": {}}, row_version=cu.row_version + 1)
    assert exc.value.thu_lai_duoc is True
    assert ngan.doc("cau_hinh", KHOA) == cu
    assert ngan.doc("cau_hinh", {"ma": "DEMO-khac"}) is None
    with pytest.raises(RuntimeError):
        with ngan.lo() as lo:
            lo.sua("cau_hinh", KHOA, {"gia_tri": {}}, row_version=cu.row_version)
            raise RuntimeError("DEMO lỗi giữa lô")
    assert ngan.doc("cau_hinh", KHOA) == cu


def test_sua_xoa_cung_lo_va_phien_ban_khong_aba():
    ngan = NganBoNho()
    dat(ngan, {})
    cu = ngan.doc("cau_hinh", KHOA)
    with ngan.lo() as lo:
        lo.sua("cau_hinh", KHOA, {"gia_tri": {"ngan_sach_token_vao_toi_da": 20000}}, row_version=cu.row_version)
    moi = ngan.doc("cau_hinh", KHOA)
    assert moi.row_version > cu.row_version
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.xoa("cau_hinh", KHOA, row_version=cu.row_version)
    with ngan.lo() as lo:
        lo.xoa("cau_hinh", KHOA, row_version=moi.row_version)
        lo.them("cau_hinh", KHOA, {"gia_tri": {}})
    assert ngan.doc("cau_hinh", KHOA).row_version > moi.row_version


def test_hai_luong_lay_hoac_tao_theo_duy_nhat_chi_tao_mot_ban():
    ngan = NganBoNho(KHAI)
    chan = threading.Barrier(2)

    def lam(i):
        chan.wait(timeout=5)
        with ngan.lo() as lo:
            lo.lay_hoac_tao("demo", {"phap_nhan_id": "pn-DEMO", "bam_noi_dung": "bam-DEMO"},
                           {"ma_tuong_quan": f"luot-DEMO-{i}"})
        return lo.ket_qua[0]

    with ThreadPoolExecutor(max_workers=2) as pool:
        kq = list(pool.map(lam, [1, 2]))
    assert sorted(k["da_tao"] for k in kq) == [False, True]
    assert kq[0]["ban_ghi"] == kq[1]["ban_ghi"]
    assert len(ngan.tim("demo", {"phap_nhan_id": "pn-DEMO"})["danh_sach"]) == 1


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
    assert len(ngan.tim("demo", {"phap_nhan_id": "pn-DEMO"})["danh_sach"]) == 2


def test_ngan_goc_bat_buoc_phap_nhan_trong_khoa_va_loc_khong_doc_cheo():
    ngan = NganBoNho(KHAI)
    for pn in ["pn-DEMO-A", "pn-DEMO-B"]:
        with ngan.lo() as lo:
            lo.them("demo", {"phap_nhan_id": pn, "ma_tuong_quan": "DEMO-1"}, {"bam_noi_dung": "DEMO"})
    assert ngan.doc("demo", {"phap_nhan_id": "pn-DEMO-A", "ma_tuong_quan": "DEMO-1"}).gia_tri["phap_nhan_id"] == "pn-DEMO-A"
    assert len(ngan.tim("demo", loc={"phap_nhan_id": "pn-DEMO-B"})["danh_sach"]) == 1
    with pytest.raises(ValueError):
        ngan.doc("demo", {"ma_tuong_quan": "DEMO-1"})
    with pytest.raises(ValueError):
        ngan.tim("demo", loc={})
    rieng = NganBoNho(KHAI, phap_nhan_id="pn-DEMO-A")
    with pytest.raises(ValueError):
        rieng.tim("demo", loc={"phap_nhan_id": "pn-DEMO-B"})


def test_tim_phan_trang_va_doc_khong_cho_sua_kho_ngam():
    ngan = NganBoNho()
    with ngan.lo() as lo:
        for ma in ["DEMO-1", "DEMO-2", "DEMO-3"]:
            lo.them("cau_hinh", {"ma": ma}, {"gia_tri": {}})
    ds = ngan.tim("cau_hinh", loc={}, gioi_han=2)
    assert len(ds["danh_sach"]) == 2 and ds["tiep"] is not None
    assert len(ngan.tim("cau_hinh", loc={}, gioi_han=2, tiep=ds["tiep"])["danh_sach"]) == 1
    row = ngan.doc("cau_hinh", {"ma": "DEMO-1"})
    row.gia_tri["gia_tri"]["DEMO"] = "khong luu"
    assert ngan.doc("cau_hinh", {"ma": "DEMO-1"}).gia_tri["gia_tri"] == {}
    for gioi_han in [0, 501, True]:
        with pytest.raises(ValueError):
            ngan.tim("cau_hinh", gioi_han=gioi_han)


def test_chon_ngan_uu_tien_sdk_canh_bao_mot_lan_va_ram_mat_khi_phien_moi(monkeypatch, capsys):
    monkeypatch.setattr(mo_ngan, "_da_canh_bao", False)
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
        lo.sua("cau_hinh", KHOA, {"gia_tri": {"ngan_sach_token_vao_toi_da": 20000}}, row_version=ban1["phien_ban_cau_hinh"])
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
