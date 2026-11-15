"""CoreGia + Ngăn RAM; seam bài đo, không giả API quản trị SDK 2.1."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay
from e_tra_cuu.ngan import NganBoNho, NganKhongHopLe
from e_tra_cuu.trang_thai import CHI_SO, lay_hoac_tao_dot, cap_nhat_cac_dot
from ho_tro_tc_2 import GOI


@pytest.fixture
def ngan():
    return NganBoNho(chay.KHAI_BAO["ngan_du_lieu"])


def du_lieu(core=None):
    core = core or CoreGia()
    noi_dung = b'{"DEMO":true,"tu_so":9,"mau_so":10}'
    return {"trang_thai": "da_do", "bam_bo": "sha256:" + sha256(b"Bo DEMO").hexdigest(),
            "bam_cau_hinh": "sha256:" + sha256(b"Cau hinh DEMO").hexdigest(),
            "phien_ban_engine": "e_tra_cuu 0.1.0",
            "chi_so": {ma: {"tu_so": 9, "mau_so": 10} for ma in CHI_SO},
            "bao_cao": core.them_tep("bao-cao-DEMO.json", noi_dung, "application/json"),
            "bam_bao_cao": "sha256:" + sha256(noi_dung).hexdigest()}


def khoa(ma="DEMO-1", p="DEMO-P"):
    return {"phap_nhan_id": p, "ma_dot": ma}


def test_cung_khoa_khong_nhan_so_dem_ke_ca_dong_thoi(ngan):
    data = du_lieu()
    with ThreadPoolExecutor(max_workers=8) as pool:
        ds = list(pool.map(lambda _: lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-1", data), range(16)))
    assert sum(kq.da_tao for kq in ds) == 1
    assert len({kq.row_version for kq in ds}) == 1
    assert ngan.doc("dot_kiem", khoa()).gia_tri["chi_so"]["tra_loi_dung"] == {"tu_so": 9, "mau_so": 10}
    # Gửi lại KHÔNG phải cập nhật; dù số đếm mới cũng không âm thầm ghi đè.
    data["chi_so"]["tra_loi_dung"] = {"tu_so": 10, "mau_so": 10}
    assert not lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-1", data).da_tao
    assert ngan.doc("dot_kiem", khoa()).gia_tri["chi_so"]["tra_loi_dung"]["tu_so"] == 9


def test_cas_lo_rollback_va_khong_thu_lai_am_tham(ngan):
    data = du_lieu()
    a = lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-1", data)
    b = lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-2", data)
    moi = deepcopy(data); moi["chi_so"]["tra_loi_dung"]["tu_so"] = 10
    cac_dot = [{"ma_dot": "DEMO-1", "gia_tri": moi, "row_version": a.row_version},
               {"ma_dot": "DEMO-2", "gia_tri": moi, "row_version": b.row_version + 1}]
    with pytest.raises(LoiNghiepVu) as exc:
        cap_nhat_cac_dot(ngan, "DEMO-P", cac_dot)
    assert exc.value.ma == "NGAN_XUNG_DOT" and exc.value.thu_lai_duoc
    assert "đọc lại" in exc.value.thong_diep
    assert ngan.doc("dot_kiem", khoa()).row_version == a.row_version
    assert ngan.doc("dot_kiem", khoa()).gia_tri == a.gia_tri
    cac_dot[1]["row_version"] = b.row_version
    kq = cap_nhat_cac_dot(ngan, "DEMO-P", cac_dot)
    assert all(k.gia_tri["chi_so"]["tra_loi_dung"]["tu_so"] == 10 for k in kq)
    with pytest.raises(LoiNghiepVu):
        cap_nhat_cac_dot(ngan, "DEMO-P", cac_dot)
    assert ngan.doc("dot_kiem", khoa()).gia_tri["chi_so"]["tra_loi_dung"]["tu_so"] == 10


def test_core_gia_goi_seam_thuan_ngan_uu_tien_va_phap_nhan_tung_lenh(ngan):
    phieu = deepcopy(chay.app.phieu)
    ma = "tra_cuu.xuat_ket_qua@1"
    phieu["nang_luc"] = [n for n in phieu["nang_luc"] if n["ma"] == ma]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=GOI); app.ngan = NganBoNho(chay.KHAI_BAO["ngan_du_lieu"])
    core = CoreGia(); data = du_lieu(core); luot = []

    class LoTheoDoi:
        def __enter__(self):
            self.lo = ngan.lo(); self.lo.__enter__(); return self

        def lay_hoac_tao(self, bang, khoa, gia_tri):
            luot.append((bang, deepcopy(khoa)))
            return self.lo.lay_hoac_tao(bang, khoa, gia_tri)

        def sua(self, bang, khoa, gia_tri, *, row_version):
            luot.append((bang, deepcopy(khoa)))
            return self.lo.sua(bang, khoa, gia_tri, row_version=row_version)

        def __exit__(self, *args):
            return self.lo.__exit__(*args)

    class NganTheoDoi:
        def lo(self):
            return LoTheoDoi()

    @app.nang_luc(ma)
    def seam_test(viec):
        # Chỉ test cấp ngăn qua dependency, không phải SDK 2.0 đã có viec.ngan.
        viec_gia = SimpleNamespace(ngu_canh=viec.ngu_canh, ngan=NganTheoDoi())
        a = chay.ghi_bai_do_demo(viec_gia, app, ma_dot="DEMO-1", gia_tri=data)
        chay.ghi_bai_do_demo(viec_gia, app, ma_dot="DEMO-1", gia_tri=data)
        chay.ghi_bai_do_demo(viec_gia, app, cac_dot=[{"ma_dot": "DEMO-1", "gia_tri": data, "row_version": a.row_version}])
        raise LoiNghiepVu("DEMO_DA_KIEM_SEAM", "Đã kiểm seam DEMO bằng Core giả.")

    viec_id = core.giao_viec(ma, {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": {}}, phap_nhan_id="DEMO-P")
    core.chay(app)
    kq = core.xem(viec_id)
    assert kq["loi"]["ma"] == "DEMO_DA_KIEM_SEAM"
    assert luot == [("dot_kiem", khoa())] * 3
    assert app.ngan.doc("dot_kiem", khoa()) is None  # Ưu tiên ngăn việc.
    assert ngan.doc("dot_kiem", khoa()).gia_tri["chi_so"]["tra_loi_dung"]["mau_so"] == 10


def test_fallback_ram_view_va_thieu_phap_nhan(ngan):
    app = SimpleNamespace(ngan=ngan); data = du_lieu()
    chay.ghi_bai_do_demo(SimpleNamespace(ngu_canh={"phap_nhan_id": "DEMO-P"}), app, ma_dot="DEMO-1", gia_tri=data)
    assert ngan.doc("dot_kiem", khoa()) is not None
    assert ngan.doc("dot_kiem", khoa(p="DEMO-Q")) is None
    with pytest.raises(LoiNghiepVu, match="Thiếu ngữ cảnh"):
        chay.ghi_bai_do_demo(SimpleNamespace(ngu_canh={}), app, ma_dot="DEMO-1", gia_tri=data)
    with pytest.raises(NganKhongHopLe):
        ngan.cho_phap_nhan("DEMO-P").doc("dot_kiem", khoa(p="DEMO-Q"))


def test_seam_khong_chuyen_view_sang_phap_nhan_khac(ngan):
    app = SimpleNamespace(ngan=ngan.cho_phap_nhan("DEMO-P"))
    with pytest.raises(LoiNghiepVu) as exc:
        chay.ghi_bai_do_demo(SimpleNamespace(ngu_canh={"phap_nhan_id": "DEMO-Q"}), app,
                           ma_dot="DEMO-1", gia_tri=du_lieu())
    assert exc.value.ma == "NGAN_KHONG_HOP_LE"
    assert ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}).danh_sach == []


def test_cursor_bang_loc_phap_nhan_khong_doi(ngan):
    data = du_lieu()
    for ma in ("DEMO-1", "DEMO-2"):
        lay_hoac_tao_dot(ngan, "DEMO-P", ma, data)
    trang = ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}, gioi_han=1)
    assert trang.tiep
    with pytest.raises(NganKhongHopLe):
        ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-Q"}, gioi_han=1, tiep=trang.tiep)
    with pytest.raises(NganKhongHopLe):
        ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P", "trang_thai": "da_do"}, gioi_han=1, tiep=trang.tiep)


@pytest.mark.parametrize("sua", [
    lambda v: v.update(cau_hoi="Nội dung DEMO không được lưu"),
    lambda v: v.update(nguyen_van="Nội dung DEMO không được lưu"),
    lambda v: v.update(phap_nhan_id="DEMO-Q"),
    lambda v: v.update(chi_so={"tra_loi_dung": {"phan_tram": 90}}),
    lambda v: v["chi_so"].update(tra_loi_dung={"tu_so": True, "mau_so": 10}),
    lambda v: v["chi_so"].update(tra_loi_dung={"tu_so": -1, "mau_so": 10}),
    lambda v: v["chi_so"].update(tra_loi_dung={"tu_so": 11, "mau_so": 10}),
    lambda v: v["chi_so"].update(tra_loi_dung={"tu_so": float("nan"), "mau_so": 10}),
    lambda v: v.update(chi_so={ma: None for ma in CHI_SO}),
    lambda v: v.update(bam_bo="DEMO-sai"),
    lambda v: v.update(bam_bao_cao=None),
    lambda v: v["bao_cao"].update(ten="ten-tai-lieu-DEMO.txt"),
    lambda v: v["bao_cao"].update(tep_id="DEMO/path"),
    lambda v: v.update(phien_ban_engine="<script>DEMO</script>"),
])
def test_khong_luu_noi_dung_sai_khuon_sai_so(ngan, sua):
    data = du_lieu(); sua(data)
    with pytest.raises(LoiNghiepVu) as exc:
        lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-1", data)
    assert exc.value.ma == "TC_BAI_DO_KHONG_HOP_LE"
    assert ngan.doc("dot_kiem", khoa()) is None
    assert "Nội dung DEMO" not in exc.value.thong_diep


def test_chua_do_chi_null_khong_tu_sinh_ty_le(ngan):
    data = du_lieu(); data.update(trang_thai="chua_do", chi_so={ma: None for ma in CHI_SO}, bao_cao=None, bam_bao_cao=None)
    kq = lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-1", data)
    assert kq.gia_tri["chi_so"] == {ma: None for ma in CHI_SO}
    data["chi_so"]["tra_loi_dung"] = {"tu_so": 0, "mau_so": 0}
    with pytest.raises(LoiNghiepVu):
        lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-2", data)


def test_tran_lo_khong_nhan_lenh_trung_va_cas_bat_buoc(ngan):
    data = du_lieu(); a = lay_hoac_tao_dot(ngan, "DEMO-P", "DEMO-1", data)
    muc = {"ma_dot": "DEMO-1", "gia_tri": data, "row_version": a.row_version}
    for cac_dot in ([], [muc] * 101, [muc, muc], [{**muc, "row_version": None}], [{**muc, "row_version": True}]):
        with pytest.raises(LoiNghiepVu):
            cap_nhat_cac_dot(ngan, "DEMO-P", cac_dot)
    assert ngan.doc("dot_kiem", khoa()).row_version == a.row_version
