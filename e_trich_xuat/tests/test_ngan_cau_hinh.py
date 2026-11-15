"""Hành vi cấu hình/ngăn đã có, chuyển sang CoreGia SDK 2.2.0.

Bảng demo chỉ thuộc phiếu test; gói TX không còn bảng ngăn sau bỏ cấu hình.
Các ca xóa/RAM cũ kiểm quy tắc không xóa và vòng đời do Core giữ tương ứng.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import threading
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, LoiDuongTruyen, NganXungDot, NganEngine
from kho_tri_thuc_sdk.thu import CoreGia
from e_trich_xuat.chay import CAU_CHUA_CAU_HINH, GOC_GOI, ghim_cau_hinh, tao_app
from e_trich_xuat.tham_so import bam_bytes, json_bytes

KHAI = [{"bang": "demo", "ten": "Ngăn DEMO", "pham_vi": "phap_nhan",
         "khoa": ["ma_tuong_quan"], "duy_nhat": [["phap_nhan_id", "bam_noi_dung"]],
         "truong": [{"ma": "ma_tuong_quan", "kieu": "van_ban", "bat_buoc": True},
                    {"ma": "bam_noi_dung", "kieu": "van_ban", "bat_buoc": True},
                    {"ma": "trang_thai", "kieu": "van_ban"}], "giu_toi_da_ngay": 90}]


def moi():
    core, app = CoreGia(), tao_app()
    core.nap_engine(app)
    return core, app


def trong_viec(ham, *, core=None, pn="pn-DEMO-A", khai=None):
    core = core or CoreGia()
    phieu = deepcopy(tao_app().phieu)
    phieu.pop("cau_hinh")
    phieu.update(ngan_du_lieu=deepcopy(khai or KHAI), chay_thu_demo=[],
        du_lieu={"goi_migration": {"ma": "e_trich_xuat", "thu_muc": "sql",
            "tep_kiem_ke": "sql/kiem_ke.json", "phien_ban_du_lieu": 1}},
        nang_luc=[{"ma": "demo.ngan@1", "ten": "Kiểm ngăn DEMO", "nhan": ["van_ban"],
                   "tra": "van_ban", "gioi_han": {"thoi_han_giay": 10}}])
    app = Engine(phieu)
    ket_qua = []
    @app.nang_luc("demo.ngan@1")
    def lam(viec):
        ket_qua.append(ham(viec.ngan, app, viec))
        return {"loai": "van_ban", "van_ban": "DEMO"}
    vid = core.giao_viec("demo.ngan@1", {"loai": "van_ban", "van_ban": "DEMO"}, phap_nhan_id=pn)
    core.chay(app, cho_gui_lai_giay=0)
    assert core.xem(vid)["trang_thai"] == "XONG", core.xem(vid)
    return ket_qua[0], core


def them(ngan, ma="DEMO-1", bam="a"):
    with ngan.lo() as lo:
        lo.them("demo", {"ma_tuong_quan": ma, "bam_noi_dung": bam})
    return ngan.doc("demo", {"ma_tuong_quan": ma})


def test_mac_dinh_chi_dien_cho_ban_ghi_da_co_khong_ghi_nguoc():
    core, app = moi()
    assert app.cau_hinh == {}
    def lam(viec):
        assert viec.cau_hinh == {"ngan_sach_token_vao_toi_da": 16000}
        return {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {}}
    app._ham["trich.doc_docx@1"] = lam
    tep = core.them_tep("DEMO.docx", b"DEMO", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert core.chay_thu(app, "trich.doc_docx@1", {"loai": "tep", "tep": tep})["trang_thai"] == "XONG"
    assert core.xem_ngan(app.ma, "cau_hinh") == []


@pytest.mark.parametrize("v", [{"ngan_sach_token_vao_toi_da": 1023}, {"ngan_sach_token_vao_toi_da": 100001},
    {"ngan_sach_token_vao_toi_da": True}, {"ngan_sach_token_vao_toi_da": 16000.5},
    {"ngan_sach_token_vao_toi_da": "16000"}, {"ngan_sach_token_vao_toi_da": 10 ** 1000},
    {"truong_la": "DEMO"}, {"gia_tri": {}}, {"ma": "mac_dinh"}])
def test_cau_hinh_sai_bi_tu_choi(v):
    core, app = moi()
    with pytest.raises(LoiDuongTruyen) as e:
        core.dat_cau_hinh(app.ma, v)
    assert e.value.ma == "NGAN_DU_LIEU_SAI"
    assert core.xem_ngan(app.ma, "cau_hinh") == []


def test_cau_hinh_khong_phai_dict_hoac_nan_bi_ngan_tu_choi():
    core, app = moi()
    for v in [[], None, {"ngan_sach_token_vao_toi_da": float("nan")}]:
        with pytest.raises(LoiDuongTruyen):
            core.dat_cau_hinh(app.ma, v)
    assert core.xem_ngan(app.ma, "cau_hinh") == []


def test_cas_sai_khong_ghi_lo_va_exception_trong_with_khong_ghi():
    def lam(n, a, v):
        cu = them(n)
        with pytest.raises(NganXungDot) as e:
            with n.lo() as lo:
                lo.them("demo", {"ma_tuong_quan": "DEMO-2", "bam_noi_dung": "b"})
                lo.sua("demo", {"ma_tuong_quan": "DEMO-1"}, {"trang_thai": "moi"}, row_version=cu.row_version+1)
        assert e.value.thu_lai_duoc
        assert n.doc("demo", {"ma_tuong_quan": "DEMO-1"}) == cu
        assert n.doc("demo", {"ma_tuong_quan": "DEMO-2"}) is None
        with pytest.raises(RuntimeError):
            with n.lo() as lo:
                lo.sua("demo", {"ma_tuong_quan": "DEMO-1"}, {"trang_thai": "moi"}, row_version=cu.row_version)
                raise RuntimeError("DEMO")
        assert n.doc("demo", {"ma_tuong_quan": "DEMO-1"}) == cu
    trong_viec(lam)


def test_sua_xoa_cung_lo_va_phien_ban_khong_aba():
    # SDK 2.2 cấm xóa: trạng thái thay cho xóa/tạo lại, CAS tăng đơn điệu.
    def lam(n, a, v):
        cu = them(n)
        with pytest.raises(LoiNghiepVu) as e:
            with n.lo() as lo:
                lo.xoa("demo", {"ma_tuong_quan": "DEMO-1"}, row_version=cu.row_version)
        assert e.value.ma == "NGAN_KHONG_XOA"
        with n.lo() as lo:
            lo.sua("demo", {"ma_tuong_quan": "DEMO-1"}, {"trang_thai": "luu_tru"}, row_version=cu.row_version)
        moi = n.doc("demo", {"ma_tuong_quan": "DEMO-1"})
        assert moi.row_version > cu.row_version
        with pytest.raises(NganXungDot):
            with n.lo() as lo:
                lo.sua("demo", {"ma_tuong_quan": "DEMO-1"}, {"trang_thai": "cu"}, row_version=cu.row_version)
        assert n.doc("demo", {"ma_tuong_quan": "DEMO-1"}) == moi
    trong_viec(lam)


def test_hai_luong_lay_hoac_tao_theo_duy_nhat_chi_tao_mot_ban():
    def lam(n, a, v):
        chan = threading.Barrier(2)
        def ghi(i):
            chan.wait(timeout=5)
            with n.lo() as lo:
                lo.lay_hoac_tao("demo", {"bam_noi_dung": "a"}, {"ma_tuong_quan": f"DEMO-{i}"})
            return lo.ket_qua[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            kq = list(pool.map(ghi, [1,2]))
        assert sorted(k.da_tao for k in kq) == [False, True]
        assert kq[0].id == kq[1].id
        assert len(n.tim("demo", loc={}).danh_sach) == 1
    trong_viec(lam)


def test_duy_nhat_va_thay_chi_muc_trong_lo():
    def lam(n,a,v):
        cu = them(n)
        with pytest.raises(NganXungDot):
            them(n, "DEMO-2", "a")
        with n.lo() as lo:
            lo.sua("demo", {"ma_tuong_quan": "DEMO-1"}, {"bam_noi_dung": "b"}, row_version=cu.row_version)
            lo.them("demo", {"ma_tuong_quan": "DEMO-2", "bam_noi_dung": "a"})
        assert len(n.tim("demo").danh_sach) == 2
    trong_viec(lam)


def test_ngan_goc_bat_buoc_phap_nhan_trong_khoa_va_loc_khong_doc_cheo():
    def ghi(n,a,v):
        with pytest.raises(LoiNghiepVu) as e:
            a.ngan.doc("demo", {"ma_tuong_quan": "DEMO-1"})
        assert e.value.ma == "NGAN_CAN_VIEC"
        assert n.tim("demo", loc={}).danh_sach == []
        row = them(n)
        assert row.gia_tri["phap_nhan_id"] == v.ngu_canh["phap_nhan_id"]
        assert len(n.tim("demo", loc={}).danh_sach) == 1
    _, core = trong_viec(ghi)
    trong_viec(ghi, core=core, pn="pn-DEMO-B")
    assert len(core.xem_ngan("e_trich_xuat", "demo")) == 2


def test_tim_phan_trang_va_doc_khong_cho_sua_kho_ngam():
    def lam(n,a,v):
        for ma in ["DEMO-1","DEMO-2","DEMO-3"]:
            them(n, ma, ma)
        ds = n.tim("demo", loc={}, gioi_han=2)
        assert len(ds.danh_sach) == 2 and ds.tiep is not None
        assert len(n.tim("demo", loc={}, gioi_han=2, tiep=ds.tiep).danh_sach) == 1
        row = n.doc("demo", {"ma_tuong_quan":"DEMO-1"})
        row.gia_tri["trang_thai"] = "khong luu"
        assert n.doc("demo", {"ma_tuong_quan":"DEMO-1"}).gia_tri["trang_thai"] is None
        for gh in [0,501,True]:
            with pytest.raises(LoiNghiepVu):
                n.tim("demo", gioi_han=gh)
    trong_viec(lam)


def test_chon_ngan_uu_tien_sdk_canh_bao_mot_lan_va_ram_mat_khi_phien_moi(capsys):
    # Không còn fallback/cảnh báo RAM; Core giữ dữ liệu qua hai app mới.
    _, core = trong_viec(lambda n,a,v: them(n))
    def doc(n,a,v):
        assert isinstance(a.ngan, NganEngine)
        assert n.doc("demo", {"ma_tuong_quan":"DEMO-1"}) is not None
    trong_viec(doc, core=core)
    assert "Đang lưu tạm" not in capsys.readouterr().err
    assert CoreGia().xem_ngan("e_trich_xuat", "demo") == []


def test_ghim_cau_hinh_doc_mot_lan_va_thay_doi_khong_sua_snapshot():
    viec = SimpleNamespace(cau_hinh={"ngan_sach_token_vao_toi_da":16000})
    cu = ghim_cau_hinh(viec)
    viec.cau_hinh = {"ngan_sach_token_vao_toi_da":20000}
    moi = ghim_cau_hinh(viec)
    assert cu["gia_tri"]["ngan_sach_token_vao_toi_da"] == 16000
    assert moi["gia_tri"]["ngan_sach_token_vao_toi_da"] == 20000
    assert cu["bam_cau_hinh"] != moi["bam_cau_hinh"]
    assert cu["phien_ban_cau_hinh"] is None  # SDK chưa công bố trên việc.


def test_snapshot_chi_doc_mot_ban_va_ngan_cua_viec_duoc_uu_tien():
    class Viec:
        so_doc = 0
        @property
        def cau_hinh(self):
            self.so_doc += 1
            return {"ngan_sach_token_vao_toi_da":16000}
        @property
        def ngan(self):
            pytest.fail("Cấu hình không đọc từ ngăn")
    v = Viec()
    assert ghim_cau_hinh(v)["gia_tri"] == {"ngan_sach_token_vao_toi_da":16000}
    assert v.so_doc == 1


def test_tao_app_khai_bao_ngan_chung_va_giu_ngan_sdk():
    app = tao_app()
    assert isinstance(app.ngan, NganEngine)
    assert "ngan_du_lieu" not in app.phieu
    assert app.cau_hinh == {}  # Không cấu hình engine khi tạo app.
    with pytest.raises(LoiNghiepVu) as e:
        app.ngan.doc("cau_hinh", {"ma":"mac_dinh"})
    assert e.value.ma == "ENGINE_CHUA_SAN_SANG"
    trong_viec(lambda n,a,v: pytest.raises(LoiNghiepVu, n.doc, "bang_chua_khai", {"ma_tuong_quan":"DEMO"}))


@pytest.mark.parametrize("loi", ["NGAN_XUNG_DOT", "NGAN_DU_LIEU_SAI", "NGAN_KHONG_CO_BANG"])
def test_loi_cong_chung_duoc_doi_sang_loi_nghiep_vu(loi):
    core = CoreGia()
    def lam(n,a,v):
        if loi == "NGAN_XUNG_DOT":
            core.gay_xung_dot_ngan("demo")
        with pytest.raises(LoiNghiepVu) as e:
            if loi == "NGAN_KHONG_CO_BANG":
                n.doc("chua_khai", {"ma_tuong_quan":"DEMO"})
            elif loi == "NGAN_DU_LIEU_SAI":
                them(n, bam=True)
            else:
                them(n)
        assert e.value.ma == loi
        assert e.value.thu_lai_duoc == (loi == "NGAN_XUNG_DOT")
    trong_viec(lam, core=core)
    assert core.xem_ngan("e_trich_xuat", "demo") == []


def test_snapshot_sdk_duoc_sao_chep_va_kiem_schema():
    core, app = moi()
    core.dat_cau_hinh(app.ma, {})  # SDK điền mặc định trước giao việc.
    viec = SimpleNamespace(cau_hinh={"ngan_sach_token_vao_toi_da":16000})
    ban = ghim_cau_hinh(viec)
    assert ban["bam_cau_hinh"] == bam_bytes(json_bytes(viec.cau_hinh))
    ban["gia_tri"]["ngan_sach_token_vao_toi_da"] = 20000
    assert viec.cau_hinh["ngan_sach_token_vao_toi_da"] == 16000
    with pytest.raises(LoiDuongTruyen):
        core.dat_cau_hinh(app.ma, {"ngan_sach_token_vao_toi_da":True})
    for thieu in [{}, None]:
        with pytest.raises(LoiNghiepVu) as e:
            ghim_cau_hinh(SimpleNamespace(cau_hinh=thieu))
        assert e.value.ma == "CHUA_CAU_HINH"


def test_buoc_can_cau_hinh_tra_loi_nghiep_vu_bang_core_gia():
    core, app = moi()
    ham = app._ham["trich.chuan_bi@1"]
    def lam(viec):
        viec.cau_hinh = {}  # Mô phỏng snapshot bị thiếu; không bỏ kiểm Core.
        return ham(viec)
    app._ham["trich.chuan_bi@1"] = lam
    vd = next(v for v in app.phieu["chay_thu_demo"] if v["nang_luc"] == "trich.chuan_bi@1")
    kq = core.chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
    assert kq["loi"]["ma"] == "CHUA_CAU_HINH" and kq["loi"]["thong_diep"] == CAU_CHUA_CAU_HINH
    app._ham[vd["nang_luc"]] = ham
    core.dat_cau_hinh(app.ma, {"ngan_sach_token_vao_toi_da":16000})
    assert core.chay_thu(app, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])["trang_thai"] == "XONG"
    with pytest.raises(LoiDuongTruyen):
        core.dat_cau_hinh(app.ma, {"ngan_sach_token_vao_toi_da":True})
