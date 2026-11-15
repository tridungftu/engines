"""Kiểm khung bằng CoreGia; hợp đồng ngăn kiểm trực tiếp trên RAM."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, kiem_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay
from e_tra_cuu.cau_hinh import doc_cau_hinh
from e_tra_cuu.ngan import NganBoNho, NganKhongHopLe, NganXungDot
import e_tra_cuu.ngan as mau_ngan
from kiem_doc_lap import GOI, kiem_goi

REPO = Path(__file__).resolve().parents[2]
MA = "tra_cuu.xuat_ket_qua@1"  # TC-3 đã có cắt đoạn; năng lực này vẫn chờ TC-8.


@pytest.fixture
def ngan():
    return NganBoNho(chay.KHAI_BAO["ngan_du_lieu"])


def cau_hinh_demo():
    return {
        "phien_ban": 1,
        "quy_tac_nhom": {"tep_id": "tep-quy-tac-DEMO", "bam": "sha256:" + sha256(b"Quy tac DEMO").hexdigest()},
    }


def luu_cau_hinh(ngan, gia_tri):
    with ngan.lo() as lo:
        lo.them("cau_hinh", {}, gia_tri)


def khoa(p="DEMO-P", ma="DEMO-1"):
    return {"phap_nhan_id": p, "ma_dot": ma}


def them_dot(ngan, p="DEMO-P", ma="DEMO-1"):
    with ngan.lo() as lo:
        kq = lo.them("dot_kiem", khoa(p, ma), {"trang_thai": "chua_do"})
    return kq


def chay_cong_cau_hinh(ngan):
    # Handler chỉ có trong test: kiểm lỗi cấu hình qua biên SDK thật.
    phieu = deepcopy(chay.app.phieu)
    phieu["nang_luc"] = [n for n in phieu["nang_luc"] if n["ma"] == MA]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=GOI)
    chay.khoi_tao_ngan(app)
    app.ngan = ngan

    @app.nang_luc(MA)
    def viec_can_cau_hinh(viec):
        chay.yeu_cau_cau_hinh(app.ngan)
        raise LoiNghiepVu("CHUA_LAM", "Chức năng tra cứu đang được hoàn thiện.")

    core = CoreGia()
    return core.chay_thu(app, MA, {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": {}})


@pytest.mark.parametrize("ten", ["ngan.py", "cau_hinh.py"])
def test_bam_hai_mau_nguyen_trang(ten):
    def bam(tep):
        return sha256(tep.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    assert bam(GOI / "e_tra_cuu" / ten) == bam(REPO / "_chung" / "mau-ma" / ten)


def test_phieu_khung_va_khai_sdk_rieng():
    assert kiem_phieu(chay.app.phieu, GOI) == []
    assert len(chay.app.phieu["chay_thu_demo"]) >= 1
    assert len(chay.app.phieu["loai_du_lieu_rieng"]) == 4
    assert len(chay.app.phieu["nang_luc"]) == 8
    assert "tra_cuu.kiem_khung@1" not in {n["ma"] for n in chay.app.phieu["nang_luc"]}
    assert not {"ngan_du_lieu", "cau_hinh", "giao_dien_quan_tri"} & chay.app.phieu.keys()
    assert [b["bang"] for b in chay.KHAI_BAO["ngan_du_lieu"]] == ["cau_hinh", "dot_kiem"]
    assert len(chay.KHAI_BAO["giao_dien_quan_tri"]) == 2
    assert not (REPO / "e_tra_cuu" / "ma-nguon").exists()


def test_stub_core_gia_khong_thanh_cong_gia():
    assert chay.ngan.doc("cau_hinh", {}) is None
    core = CoreGia()
    kq = core.chay_thu(chay.app, MA, {"loai": "ho_so_tra_cuu", "ho_so_tra_cuu": {}})
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "CHUA_LAM"
    assert kq["loi"]["thong_diep"] == "Chức năng tra cứu đang được hoàn thiện."
    assert kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0


def test_khoi_tao_tai_su_dung_va_canh_bao_mot_lan(monkeypatch, capsys):
    monkeypatch.setattr(mau_ngan, "_DA_CANH_BAO", False)
    app = SimpleNamespace()
    ngan = chay.khoi_tao_ngan(app)
    assert chay.khoi_tao_ngan(app) is ngan is app.ngan
    # Ngăn có đầy đủ khai báo, không phải RAM rỗng mới mỗi lần gọi.
    them_dot(ngan)
    assert chay.khoi_tao_ngan(app).doc("dot_kiem", khoa()) is not None
    assert capsys.readouterr().err.splitlines() == [
        "Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng"
    ]


def test_giu_ngan_sdk_khi_co(capsys):
    ngan_sdk = object()
    app = SimpleNamespace(ngan=ngan_sdk)
    assert chay.khoi_tao_ngan(app) is ngan_sdk
    assert app.ngan is ngan_sdk
    assert capsys.readouterr().err == ""


def test_thieu_cau_hinh_core_gia_khong_tao_default(ngan):
    assert doc_cau_hinh(ngan, chay.SCHEMA) is None
    kq = chay_cong_cau_hinh(ngan)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "CHUA_CAU_HINH"
    assert kq["loi"]["thong_diep"] == (
        "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
    )
    assert kq["ket_qua"] is None
    assert ngan.doc("cau_hinh", {}) is None


def test_default_tren_ban_sao_khong_ghi_nguoc(ngan):
    goc = cau_hinh_demo()
    luu_cau_hinh(ngan, goc)
    truoc = ngan.doc("cau_hinh", {})
    doc = chay.yeu_cau_cau_hinh(ngan)
    assert doc["phan_loai"] == {"trang_thai": "chua_do"}
    assert doc["cat_doan"]["do_dai_muc_tieu"] == 2000
    assert doc["ngan_sach"]["so_ung_vien_toi_da"] == 50
    doc["cat_doan"]["do_dai_muc_tieu"] = 300
    sau = ngan.doc("cau_hinh", {})
    assert sau.gia_tri == truoc.gia_tri == goc
    assert sau.row_version == truoc.row_version
    assert chay.yeu_cau_cau_hinh(ngan)["cat_doan"]["do_dai_muc_tieu"] == 2000
    assert chay_cong_cau_hinh(ngan)["loi"]["ma"] == "CHUA_LAM"


@pytest.mark.parametrize("ban_va", [
    {"phien_ban": 2}, {"phien_ban": True}, {"local_ai": {"url": "DEMO"}},
    {"phan_loai": {"nguong": 0.99}}, {"phan_loai": {"trang_thai": "da_do"}},
    {"phan_loai": {"trang_thai": "da_do", "nguong": 1.1, "bam_bo_do": "DEMO"}},
    {"cat_doan": {"do_dai_muc_tieu": 8001}},
    {"cat_doan": {"do_dai_muc_tieu": 2000, "ky_tu_don_vi_toi_da": 1000}},
    {"ngan_sach": {"so_ung_vien_toi_da": 51}},
    {"ngan_sach": {"so_trang_toi_da": False}},
    {"quy_tac_nhom": {"tep_id": "DEMO", "bam": "sai-DEMO"}},
    {"quy_tac_nhom": {"tep_id": "DEMO/path", "bam": "sha256:" + "a" * 64}},
])
def test_sai_cau_hinh_core_gia(ngan, ban_va):
    cau_hinh = cau_hinh_demo()
    cau_hinh.update(ban_va)
    luu_cau_hinh(ngan, cau_hinh)
    kq = chay_cong_cau_hinh(ngan)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "CAU_HINH_KHONG_HOP_LE"
    assert kq["ket_qua"] is None
    assert ngan.doc("cau_hinh", {}).gia_tri == cau_hinh


def test_nguong_da_do_can_gia_tri_va_bam(ngan):
    cau_hinh = cau_hinh_demo()
    cau_hinh["phan_loai"] = {"trang_thai": "da_do", "nguong": 0.5,
                              "bam_bo_do": "sha256:" + sha256(b"Bo do DEMO").hexdigest()}
    luu_cau_hinh(ngan, cau_hinh)
    assert chay.yeu_cau_cau_hinh(ngan)["phan_loai"] == cau_hinh["phan_loai"]


def test_cas_rollback_ca_lo_va_ket_qua_chua_commit(ngan):
    luu_cau_hinh(ngan, cau_hinh_demo())
    ban = ngan.doc("cau_hinh", {})
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            ket_qua = lo.them("dot_kiem", khoa(), {"trang_thai": "chua_do"})
            with pytest.raises(NganKhongHopLe):
                _ = ket_qua.da_tao
            lo.sua("cau_hinh", {}, {"phien_ban": 1}, row_version=ban.row_version + 1)
    assert ngan.doc("dot_kiem", khoa()) is None
    assert ngan.doc("cau_hinh", {}).row_version == ban.row_version
    with pytest.raises(NganKhongHopLe):
        _ = ket_qua.row_version
    with ngan.lo() as lo:
        kq = lo.sua("cau_hinh", {}, {"phien_ban": 1}, row_version=ban.row_version)
    assert kq.row_version != ban.row_version


def test_unique_rollback_va_lay_hoac_tao(ngan):
    them_dot(ngan)
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("dot_kiem", khoa(ma="DEMO-2"), {"trang_thai": "chua_do"})
            lo.them("dot_kiem", khoa(), {"trang_thai": "da_do"})
    assert ngan.doc("dot_kiem", khoa(ma="DEMO-2")) is None
    with ngan.lo() as lo:
        kq = lo.lay_hoac_tao("dot_kiem", khoa(), {"trang_thai": "da_do"})
    assert kq.da_tao is False
    assert kq.gia_tri["trang_thai"] == "chua_do"


def test_lay_hoac_tao_hai_luong_chi_mot_ban(ngan):
    def tao(_):
        with ngan.lo() as lo:
            kq = lo.lay_hoac_tao("dot_kiem", khoa(), {"trang_thai": "chua_do"})
        return kq.da_tao
    with ThreadPoolExecutor(max_workers=2) as nhom:
        assert sorted(nhom.map(tao, range(2))) == [False, True]
    assert len(ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}).danh_sach) == 1


@pytest.mark.parametrize("lenh", ["doc", "tim", "them", "sua", "xoa", "lay_hoac_tao"])
@pytest.mark.parametrize("phap_nhan", [None, "", "  "])
def test_dot_kiem_bat_buoc_phap_nhan_tung_lenh(ngan, lenh, phap_nhan):
    k = {"ma_dot": "DEMO-1"}
    if phap_nhan is not None:
        k["phap_nhan_id"] = phap_nhan
    with pytest.raises(NganKhongHopLe):
        if lenh == "doc":
            ngan.doc("dot_kiem", k)
        elif lenh == "tim":
            ngan.tim("dot_kiem", loc=k)
        else:
            with ngan.lo() as lo:
                ham = getattr(lo, lenh)
                if lenh == "xoa":
                    ham("dot_kiem", k, row_version=1)
                elif lenh == "sua":
                    ham("dot_kiem", k, {"phap_nhan_id": "DEMO-P"}, row_version=1)
                else:
                    ham("dot_kiem", k, {"phap_nhan_id": "DEMO-P"})
    assert ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}).danh_sach == []


def test_lo_khong_ke_thua_phap_nhan_lenh_truoc(ngan):
    with pytest.raises(NganKhongHopLe):
        with ngan.lo() as lo:
            lo.them("dot_kiem", khoa(), {})
            lo.them("dot_kiem", {"ma_dot": "DEMO-2"}, {"phap_nhan_id": "DEMO-P"})
    assert ngan.doc("dot_kiem", khoa()) is None


@pytest.mark.parametrize("lenh", ["doc", "tim", "them", "sua", "xoa", "lay_hoac_tao"])
def test_view_tu_choi_phap_nhan_cheo(ngan, lenh):
    them_dot(ngan)
    view = ngan.cho_phap_nhan("DEMO-P")
    k = khoa("DEMO-Q")
    with pytest.raises(NganKhongHopLe):
        if lenh == "doc":
            view.doc("dot_kiem", k)
        elif lenh == "tim":
            view.tim("dot_kiem", loc=k)
        else:
            with view.lo() as lo:
                ham = getattr(lo, lenh)
                if lenh == "xoa":
                    ham("dot_kiem", k, row_version=1)
                elif lenh == "sua":
                    ham("dot_kiem", k, {}, row_version=1)
                else:
                    ham("dot_kiem", k, {})
    assert view.doc("dot_kiem", khoa()).gia_tri["phap_nhan_id"] == "DEMO-P"


def test_du_lieu_va_cursor_khong_doc_cheo(ngan):
    for p in ("DEMO-P", "DEMO-Q"):
        for ma in ("DEMO-1", "DEMO-2"):
            them_dot(ngan, p, ma)
    trang = ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}, gioi_han=1)
    assert trang.tiep is not None
    assert all(b.gia_tri["phap_nhan_id"] == "DEMO-P" for b in trang.danh_sach)
    tiep = ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}, gioi_han=1, tiep=trang.tiep)
    assert tiep.danh_sach[0].gia_tri["ma_dot"] != trang.danh_sach[0].gia_tri["ma_dot"]
    for loc in ({"phap_nhan_id": "DEMO-Q"}, {"phap_nhan_id": "DEMO-P", "trang_thai": "chua_do"}):
        with pytest.raises(NganKhongHopLe):
            ngan.tim("dot_kiem", loc=loc, gioi_han=1, tiep=trang.tiep)
    with pytest.raises(NganKhongHopLe):
        ngan.cho_phap_nhan("DEMO-P").cho_phap_nhan("DEMO-Q")
    with pytest.raises(NganKhongHopLe):
        ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}, gioi_han=501)
    assert ngan.cho_phap_nhan("DEMO-Q").doc("dot_kiem", khoa("DEMO-Q", "DEMO-khong-co")) is None


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


@pytest.mark.parametrize("ngoai_le", [NganXungDot, NganKhongHopLe])
def test_loi_ngan_duoc_doi_sang_loi_nghiep_vu(ngoai_le):
    class NganLoi:
        def doc(self, bang, khoa):
            assert (bang, khoa) == ("cau_hinh", {})
            raise ngoai_le()
    with pytest.raises(LoiNghiepVu) as loi:
        chay.yeu_cau_cau_hinh(NganLoi())
    assert loi.value.ma == ngoai_le.ma
    assert loi.value.thu_lai_duoc == ngoai_le.thu_lai_duoc


def test_xoa_cas_rollback_va_cach_ly_gia_tri(ngan):
    ban = them_dot(ngan)
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("dot_kiem", khoa(ma="DEMO-2"), {})
            lo.xoa("dot_kiem", khoa(), row_version=ban.row_version + 1)
    assert ngan.doc("dot_kiem", khoa(ma="DEMO-2")) is None
    assert ngan.doc("dot_kiem", khoa()).row_version == ban.row_version
    with pytest.raises(NganKhongHopLe):
        with ngan.cho_phap_nhan("DEMO-P").lo() as lo:
            lo.sua("dot_kiem", khoa(), {"phap_nhan_id": "DEMO-Q"}, row_version=ban.row_version)
    with ngan.lo() as lo:
        lo.xoa("dot_kiem", khoa(), row_version=ban.row_version)
    assert ngan.doc("dot_kiem", khoa()) is None


def test_ngan_moi_khong_giu_du_lieu_va_cursor_cu(ngan):
    them_dot(ngan)
    them_dot(ngan, ma="DEMO-2")
    trang = ngan.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}, gioi_han=1)
    moi = NganBoNho(chay.KHAI_BAO["ngan_du_lieu"])
    assert moi.doc("dot_kiem", khoa()) is None
    assert moi.doc("cau_hinh", {}) is None
    with pytest.raises(NganKhongHopLe):
        moi.tim("dot_kiem", loc={"phap_nhan_id": "DEMO-P"}, gioi_han=1, tiep=trang.tiep)
    for p in ("DEMO-P", "DEMO-Q"):
        if p == "DEMO-Q":
            them_dot(ngan, p)
        ds = ngan.cho_phap_nhan(p).tim("dot_kiem", loc={"phap_nhan_id": p}).danh_sach
        assert ds and all(b.gia_tri["phap_nhan_id"] == p for b in ds)


def test_diem_vao_chay_sdk_khong_ghi_ben(monkeypatch):
    import builtins
    import os

    tep = GOI / "e_tra_cuu" / "chay.py"
    ma = compile(tep.read_text(encoding="utf-8"), str(tep), "exec")
    mo_goc = builtins.open
    os_mo_goc = os.open
    da_chay = []

    def chi_doc(file, mode="r", *args, **kwargs):
        assert not any(c in mode for c in "wax+"), "Runtime không được ghi tệp."
        return mo_goc(file, mode, *args, **kwargs)

    def os_chi_doc(path, flags, *args, **kwargs):
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        return os_mo_goc(path, flags, *args, **kwargs)

    def cam_ghi(*args, **kwargs):
        raise AssertionError("Runtime không được ghi tệp.")

    monkeypatch.setattr(builtins, "open", chi_doc)
    monkeypatch.setattr(os, "open", os_chi_doc)
    monkeypatch.setattr(Path, "write_text", cam_ghi)
    monkeypatch.setattr(Path, "write_bytes", cam_ghi)
    monkeypatch.setattr(Engine, "chay", lambda app: da_chay.append(app))
    bien = {"__name__": "__main__", "__package__": "e_tra_cuu", "__file__": str(tep)}
    exec(ma, bien)
    assert da_chay == [bien["app"]]
    assert bien["app"].ngan is bien["ngan"]
    assert bien["ngan"].doc("cau_hinh", {}) is None
