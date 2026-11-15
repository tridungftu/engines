"""Kiểm hành vi cũ trên ngăn SDK/CoreGia 2.2.0, không ngăn RAM riêng."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, NganEngine, NganXungDot, kiem_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay
from ho_tro_sdk_22 import BoNganSDK
from kiem_doc_lap import GOI, kiem_goi

REPO = Path(__file__).resolve().parents[2]
MA = "tra_cuu.xuat_ket_qua@1"

@pytest.fixture
def bo_ngan():
    bo = BoNganSDK()
    yield bo
    bo.close()

@pytest.fixture
def ngan(bo_ngan):
    return bo_ngan.ngan()

def cau_hinh_demo():
    return {"phien_ban": 1, "quy_tac_nhom": {"tep_id": "tep-quy-tac-DEMO",
            "bam": "sha256:" + sha256(b"Quy tac DEMO").hexdigest()}}

def khoa(ma="DEMO-1"):
    return {"ma_dot": ma}

def them_dot(ngan, ma="DEMO-1"):
    with ngan.lo() as lo:
        lo.them("dot_kiem", {**khoa(ma), "trang_thai": "chua_do"})
    return lo.ket_qua[0]

def chay_cong_cau_hinh(gia_tri=None, *, hong=None):
    phieu = deepcopy(chay.app.phieu)
    phieu["nang_luc"] = [n for n in phieu["nang_luc"] if n["ma"] == MA]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=GOI)
    core = CoreGia(app)
    if gia_tri is not None:
        core.dat_cau_hinh(app.ma, gia_tri)
    if hong is not None:
        # Giả lập phản hồi Core hỏng ở biên; không nới bộ kiểm SDK để nạp cấu hình sai.
        doc_goc = core._doc_cau_hinh
        def doc_hong(ma):
            ban = doc_goc(ma)
            ban["cau_hinh"] = deepcopy(hong)
            return ban
        core._doc_cau_hinh = doc_hong
    @app.nang_luc(MA)
    def handler(viec):
        chay.yeu_cau_cau_hinh(viec)
        raise LoiNghiepVu("CHUA_LAM", "Chức năng tra cứu đang được hoàn thiện.")
    return core.chay_thu(app, MA, {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": {}})

def test_phieu_khung_va_khai_sdk_rieng():
    assert kiem_phieu(chay.app.phieu, GOI) == []
    assert len(chay.app.phieu["chay_thu_demo"]) == 5
    assert len(chay.app.phieu["loai_du_lieu_rieng"]) == 4
    assert len(chay.app.phieu["nang_luc"]) == 8
    assert chay.app.phieu["tuong_thich"]["sdk"] == ">=2.2.0 <3.0.0"
    assert [b["bang"] for b in chay.app.phieu["ngan_du_lieu"]] == ["dot_kiem"]
    assert chay.app.phieu["cau_hinh"]["schema"] == "cau_hinh.schema.json"
    assert not (GOI / "KHAI-SDK-2.1.json").exists()
    assert not (REPO / "e_tra_cuu/ma-nguon").exists()

def test_stub_core_gia_khong_thanh_cong_gia():
    core = CoreGia()
    kq = core.chay_thu(chay.app, MA, {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": {}})
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "TC_DAU_VAO_KHONG_HOP_LE"
    assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == 0

def test_khoi_tao_tai_su_dung_va_canh_bao_mot_lan(ngan, capsys):
    assert isinstance(ngan, NganEngine)
    them_dot(ngan)
    assert ngan.doc("dot_kiem", khoa()) is not None
    assert "Đang lưu tạm trong bộ nhớ" not in capsys.readouterr().err

def test_giu_ngan_sdk_khi_co(ngan, capsys):
    assert isinstance(ngan, NganEngine)
    assert not hasattr(chay, "khoi_tao_ngan")
    assert not hasattr(chay, "ngan")
    assert capsys.readouterr().err == ""

def test_thieu_cau_hinh_core_gia_khong_tao_default():
    kq = chay_cong_cau_hinh()
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "CHUA_CAU_HINH"
    assert kq["loi"]["thong_diep"] == "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
    assert kq["ket_qua"] is None

def test_default_tren_ban_sao_khong_ghi_nguoc():
    goc = cau_hinh_demo()
    viec = SimpleNamespace(cau_hinh=deepcopy(goc))
    doc = chay.yeu_cau_cau_hinh(viec)
    assert doc["phan_loai"] == {"trang_thai": "chua_do"}
    assert doc["cat_doan"]["do_dai_muc_tieu"] == 2000
    assert doc["ngan_sach"]["so_ung_vien_toi_da"] == 50
    doc["cat_doan"]["do_dai_muc_tieu"] = 300
    assert viec.cau_hinh == goc
    assert chay.yeu_cau_cau_hinh(viec)["cat_doan"]["do_dai_muc_tieu"] == 2000
    assert chay_cong_cau_hinh(goc)["loi"]["ma"] == "CHUA_LAM"

@pytest.mark.parametrize("ban_va", [
    {"phien_ban": 2}, {"phien_ban": True}, {"local_ai": {"url": "DEMO"}},
    {"phan_loai": {"nguong": 0.99}}, {"phan_loai": {"trang_thai": "da_do"}},
    {"phan_loai": {"trang_thai": "da_do", "nguong": 1.1, "bam_bo_do": "DEMO"}},
    {"cat_doan": {"do_dai_muc_tieu": 8001}},
    {"cat_doan": {"do_dai_muc_tieu": 2000, "ky_tu_don_vi_toi_da": 1000}},
    {"ngan_sach": {"so_ung_vien_toi_da": 51}}, {"ngan_sach": {"so_trang_toi_da": False}},
    {"quy_tac_nhom": {"tep_id": "DEMO", "bam": "sai-DEMO"}},
    {"quy_tac_nhom": {"tep_id": "DEMO/path", "bam": "sha256:" + "a" * 64}},
])
def test_sai_cau_hinh_core_gia(ban_va):
    cau_hinh = {**cau_hinh_demo(), **ban_va}
    kq = chay_cong_cau_hinh(cau_hinh_demo(), hong=cau_hinh)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "CAU_HINH_KHONG_HOP_LE" and kq["ket_qua"] is None

def test_nguong_da_do_can_gia_tri_va_bam():
    c = cau_hinh_demo()
    c["phan_loai"] = {"trang_thai": "da_do", "nguong": 0.5, "bam_bo_do": "sha256:" + sha256(b"Bo do DEMO").hexdigest()}
    assert chay.yeu_cau_cau_hinh(SimpleNamespace(cau_hinh=c))["phan_loai"] == c["phan_loai"]

def test_cas_rollback_ca_lo_va_ket_qua_chua_commit(ngan):
    ban = them_dot(ngan)
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("dot_kiem", {**khoa("DEMO-2"), "trang_thai": "chua_do"})
            assert lo.ket_qua == []  # Kết quả chỉ có sau khi cả lô thành công.
            lo.sua("dot_kiem", khoa(), {"trang_thai": "da_do"}, row_version=ban.row_version + 1)
    assert lo.ket_qua == [] and ngan.doc("dot_kiem", khoa("DEMO-2")) is None
    assert ngan.doc("dot_kiem", khoa()).row_version == ban.row_version
    with ngan.lo() as lo:
        lo.sua("dot_kiem", khoa(), {"trang_thai": "da_do"}, row_version=ban.row_version)
    assert lo.ket_qua[0].row_version != ban.row_version

def test_unique_rollback_va_lay_hoac_tao(ngan):
    them_dot(ngan)
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("dot_kiem", {**khoa("DEMO-2"), "trang_thai": "chua_do"})
            lo.them("dot_kiem", {**khoa(), "trang_thai": "da_do"})
    assert ngan.doc("dot_kiem", khoa("DEMO-2")) is None
    with ngan.lo() as lo:
        lo.lay_hoac_tao("dot_kiem", khoa(), {"trang_thai": "da_do"})
    assert not lo.ket_qua[0].da_tao
    assert ngan.doc("dot_kiem", khoa()).gia_tri["trang_thai"] == "chua_do"

def test_lay_hoac_tao_hai_luong_chi_mot_ban(ngan):
    def tao(_):
        with ngan.lo() as lo:
            lo.lay_hoac_tao("dot_kiem", khoa(), {"trang_thai": "chua_do"})
        return lo.ket_qua[0].da_tao
    with ThreadPoolExecutor(max_workers=2) as nhom:
        assert sorted(nhom.map(tao, range(2))) == [False, True]
    assert len(ngan.tim("dot_kiem").danh_sach) == 1

@pytest.mark.parametrize("lenh", ["doc", "tim", "them", "sua", "xoa", "lay_hoac_tao"])
@pytest.mark.parametrize("phap_nhan", [None, "", "  "])
def test_dot_kiem_bat_buoc_phap_nhan_tung_lenh(bo_ngan, lenh, phap_nhan):
    ngan = bo_ngan.ngan(None)  # Không có pháp nhân tin cậy của việc.
    k = {**khoa(), **({"phap_nhan_id": phap_nhan} if phap_nhan is not None else {})}
    with pytest.raises(LoiNghiepVu) as e:
        if lenh == "doc": ngan.doc("dot_kiem", k)
        elif lenh == "tim": ngan.tim("dot_kiem", loc=k)
        else:
            with ngan.lo() as lo:
                if lenh == "them": lo.them("dot_kiem", {"ma_dot": "DEMO-1"})
                elif lenh == "xoa": lo.xoa("dot_kiem", k, row_version=1)
                elif lenh == "sua": lo.sua("dot_kiem", k, {}, row_version=1)
                else: lo.lay_hoac_tao("dot_kiem", k, {})
    assert e.value.ma in ("NGAN_CAN_VIEC", "NGAN_KHONG_XOA")
    assert bo_ngan.core.xem_ngan("e_tra_cuu", "dot_kiem") == []

def test_lo_khong_ke_thua_phap_nhan_lenh_truoc(ngan):
    with pytest.raises(LoiNghiepVu):
        with ngan.lo() as lo:
            lo.them("dot_kiem", {"ma_dot": "DEMO-1"})
            lo.them("dot_kiem", {"ma_dot": "DEMO-2", "phap_nhan_id": "DEMO-Q"})
    assert ngan.doc("dot_kiem", khoa()) is None

@pytest.mark.parametrize("lenh", ["doc", "tim", "them", "sua", "xoa", "lay_hoac_tao"])
def test_view_tu_choi_phap_nhan_cheo(bo_ngan, ngan, lenh):
    them_dot(ngan)
    # SDK bỏ qua pháp nhân tự khai trong khóa; phạm vi chỉ lấy từ việc.
    k = {**khoa(), "phap_nhan_id": "DEMO-Q"}
    if lenh == "doc": assert ngan.doc("dot_kiem", k).gia_tri["phap_nhan_id"] == "DEMO-P"
    elif lenh == "tim": assert all(b.gia_tri["phap_nhan_id"] == "DEMO-P" for b in ngan.tim("dot_kiem", loc=k).danh_sach)
    elif lenh in ("them", "xoa"):
        with pytest.raises(LoiNghiepVu):
            with ngan.lo() as lo:
                if lenh == "xoa": lo.xoa("dot_kiem", k, row_version=1)
                else: lo.them("dot_kiem", k)
    else:
        with ngan.lo() as lo:
            if lenh == "sua": lo.sua("dot_kiem", k, {"trang_thai": "da_do"}, row_version=1)
            else: lo.lay_hoac_tao("dot_kiem", k, {})
    assert bo_ngan.ngan("DEMO-Q").doc("dot_kiem", khoa()) is None

def test_du_lieu_va_cursor_khong_doc_cheo(bo_ngan, ngan):
    for p in ("DEMO-P", "DEMO-Q"):
        for ma in ("DEMO-1", "DEMO-2"): them_dot(bo_ngan.ngan(p), ma)
    trang = ngan.tim("dot_kiem", gioi_han=1)
    assert trang.tiep is not None
    tiep = ngan.tim("dot_kiem", gioi_han=1, tiep=trang.tiep)
    assert tiep.danh_sach[0].id != trang.danh_sach[0].id
    assert all(b.gia_tri["phap_nhan_id"] == "DEMO-Q" for b in bo_ngan.ngan("DEMO-Q").tim("dot_kiem", gioi_han=1, tiep=trang.tiep).danh_sach)
    with pytest.raises(LoiNghiepVu): ngan.tim("dot_kiem", gioi_han=501)
    assert bo_ngan.ngan("DEMO-Q").doc("dot_kiem", khoa("DEMO-khong-co")) is None

def test_goi_doc_lap():
    assert kiem_goi(GOI) == []


@pytest.mark.parametrize("ma", [
    "import kho_tri_thuc.engine", "from kho_tri_thuc import sdk_core",
    "from e_hoi_ai.chay import app", "from kho_tri_thuc_sdk.engine import SDKEngine",
    "import socket", "import kenh_engine", "Bootstrap()", "__import__('e_ocr')",
])
def test_bo_quet_phat_hien_import_va_kenh_cam(tmp_path, ma):
    (tmp_path / "sai.py").write_text(ma, encoding="utf-8")
    assert kiem_goi(tmp_path)


def test_bo_quet_phat_hien_bytecode(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "sai.pyc").write_bytes(b"DEMO")
    assert len(kiem_goi(tmp_path)) == 2


@pytest.mark.parametrize("ma", [
    "from socket import create_connection", "from .e_hoi_ai import chay",
    "from kho_tri_thuc_sdk.bootstrap import Bootstrap", "from kho_tri_thuc_sdk.engine import KenhCore",
])
def test_bo_quet_bat_import_from_cam(tmp_path, ma):
    (tmp_path / "sai.py").write_text(ma, encoding="utf-8")
    assert kiem_goi(tmp_path)


def test_bo_quet_lien_ket_khong_di_theo(tmp_path, monkeypatch):
    # Giả lập cờ liên kết để test chạy cả Windows không có quyền tạo symlink.
    lien_ket = tmp_path / "lien-ket-DEMO"
    lien_ket.mkdir()
    ham_goc = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda p: p == lien_ket or ham_goc(p))
    assert any("không được có liên kết" in cau for cau in kiem_goi(tmp_path))


def test_ma_thoat_bo_quet(tmp_path, monkeypatch, capsys):
    import kiem_doc_lap
    monkeypatch.setattr(kiem_doc_lap, "GOI", tmp_path)
    assert kiem_doc_lap.main() == 0
    (tmp_path / "sai.pyc").write_bytes(b"DEMO")
    assert kiem_doc_lap.main() == 1
    assert "[LỖI]" in capsys.readouterr().out


@pytest.mark.parametrize("ngoai_le", [NganXungDot, LoiNghiepVu])
def test_loi_ngan_duoc_doi_sang_loi_nghiep_vu(ngan, bo_ngan, ngoai_le):
    if ngoai_le is NganXungDot:
        bo_ngan.core.gay_xung_dot_ngan("dot_kiem")
        with pytest.raises(NganXungDot) as e: them_dot(ngan)
        assert e.value.thu_lai_duoc
    else:
        with pytest.raises(LoiNghiepVu) as e: ngan.doc("cau_hinh", {})
        assert e.value.ma == "NGAN_KHONG_CO_BANG"

def test_xoa_cas_rollback_va_cach_ly_gia_tri(ngan):
    ban = them_dot(ngan)
    with pytest.raises(LoiNghiepVu) as e:
        with ngan.lo() as lo:
            lo.them("dot_kiem", {"ma_dot": "DEMO-2"})
            lo.xoa("dot_kiem", khoa(), row_version=ban.row_version)
    assert e.value.ma == "NGAN_KHONG_XOA"
    assert ngan.doc("dot_kiem", khoa("DEMO-2")) is None
    assert ngan.doc("dot_kiem", khoa()).row_version == ban.row_version
    with ngan.lo() as lo:
        lo.sua("dot_kiem", khoa(), {"trang_thai": "da_do"}, row_version=ban.row_version)
    assert ngan.doc("dot_kiem", khoa()).gia_tri["trang_thai"] == "da_do"

def test_ngan_moi_khong_giu_du_lieu_va_cursor_cu(ngan):
    them_dot(ngan); them_dot(ngan, "DEMO-2")
    trang = ngan.tim("dot_kiem", gioi_han=1)
    bo = BoNganSDK()
    try:
        moi = bo.ngan()
        assert moi.doc("dot_kiem", khoa()) is None
        assert moi.tim("dot_kiem", gioi_han=1, tiep=trang.tiep).danh_sach == []
        assert bo.core.xem_ngan("e_tra_cuu", "dot_kiem") == []
    finally: bo.close()

def test_diem_vao_chay_sdk_khong_ghi_ben(monkeypatch):
    import builtins
    import os
    tep = GOI / "e_tra_cuu/chay.py"
    ma = compile(tep.read_text(encoding="utf-8"), str(tep), "exec")
    mo_goc, os_mo_goc, da_chay = builtins.open, os.open, []
    def chi_doc(file, mode="r", *args, **kwargs):
        assert not any(c in mode for c in "wax+")
        return mo_goc(file, mode, *args, **kwargs)
    def os_chi_doc(path, flags, *args, **kwargs):
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        return os_mo_goc(path, flags, *args, **kwargs)
    def cam_ghi(*args, **kwargs): raise AssertionError("Runtime không được ghi tệp.")
    monkeypatch.setattr(builtins, "open", chi_doc)
    monkeypatch.setattr(os, "open", os_chi_doc)
    monkeypatch.setattr(Path, "write_text", cam_ghi)
    monkeypatch.setattr(Path, "write_bytes", cam_ghi)
    monkeypatch.setattr(Engine, "chay", lambda app: da_chay.append(app))
    bien = {"__name__": "__main__", "__package__": "e_tra_cuu", "__file__": str(tep)}
    exec(ma, bien)
    assert da_chay == [bien["app"]]
    assert isinstance(bien["app"].ngan, NganEngine)
    assert "ngan" not in bien
