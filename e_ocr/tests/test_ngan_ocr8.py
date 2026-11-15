"""Hợp đồng ngăn và lỗi cạnh tranh OCR-8; đã kiểm bằng Core giả (CoreGia)."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import threading
from types import SimpleNamespace

import pytest

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from e_ocr import chay, ngan as cong_ngan
from e_ocr.cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from e_ocr.luot_abbyy import NhatKyLuot
from e_ocr.ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan
from e_ocr.van_ban import SCHEMA
from ngan_demo import GOI, KHAI, SoHanMuc, dat_cau_hinh, ngan_demo, tao_ngan
from test_ocr_1 import ABBYYGia, hot_folder
from test_ocr_4 import PDF, chay_moi, nhat_ky


@pytest.mark.parametrize("ten", ["ngan.py", "cau_hinh.py"])
def test_so_bam_mau_chung(ten):
    chung = GOI.parents[2] / "_chung" / "mau-ma" / ten
    assert sha256(chung.read_bytes().replace(b"\r\n", b"\n")).digest() == sha256(
        (GOI / "e_ocr" / ten).read_bytes().replace(b"\r\n", b"\n")
    ).digest()


def test_ca_lo_rollback_khi_cas_lech():
    ngan = ngan_demo()
    with ngan.lo() as lo:
        lo.them("trang_thai_engine", {"ma": "DEMO"}, {"lan": 1})
    cu = ngan.doc("trang_thai_engine", {"ma": "DEMO"})
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("han_muc_ngay", {"ngay": "2026-11-15"}, {"da_nhan": {}, "dang_giu": {"DEMO": 1}})
            lo.sua("trang_thai_engine", {"ma": "DEMO"}, {"lan": 2}, row_version=cu.row_version + 1)
    assert ngan.tim("han_muc_ngay", loc={}).danh_sach == []
    assert ngan.doc("trang_thai_engine", {"ma": "DEMO"}).gia_tri["lan"] == 1


def test_lo_nem_loi_trong_with_khong_ghi():
    with pytest.raises(ValueError):
        with ngan_demo().lo() as lo:
            lo.them("trang_thai_engine", {"ma": "DEMO"}, {"lan": 1})
            raise ValueError("Lỗi DEMO.")
    assert ngan_demo().doc("trang_thai_engine", {"ma": "DEMO"}) is None


def test_lay_hoac_tao_hai_luong_chi_mot_ban():
    ngan = ngan_demo()
    bat_dau = threading.Barrier(2)

    def tao(ma):
        bat_dau.wait(5)
        with ngan.lo() as lo:
            ket_qua = lo.lay_hoac_tao("luot_abbyy", {"phap_nhan_id": "pn-DEMO", "bam_noi_dung": "DEMO"},
                           {"ma_tuong_quan": ma})
        return ket_qua.da_tao

    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_lan = [nhom.submit(tao, ma) for ma in ("DEMO-A", "DEMO-B")]
        assert sorted(k.result(timeout=10) for k in cac_lan) == [False, True]
    assert len(ngan.tim("luot_abbyy", loc={"phap_nhan_id": "pn-DEMO"}).danh_sach) == 1


def test_rang_buoc_duy_nhat_va_pham_vi():
    ngan = ngan_demo()
    a, b = ngan.cho_phap_nhan("pn-DEMO-A"), ngan.cho_phap_nhan("pn-DEMO-B")
    with a.lo() as lo:
        lo.them("luot_abbyy", {"ma_tuong_quan": "DEMO"}, {"bam_noi_dung": "DEMO"})
    assert b.doc("luot_abbyy", {"ma_tuong_quan": "DEMO"}) is None
    assert b.tim("luot_abbyy", loc={}).danh_sach == []
    with pytest.raises(NganKhongHopLe):
        b.doc("luot_abbyy", {"ma_tuong_quan": "DEMO", "phap_nhan_id": "pn-DEMO-A"})
    with pytest.raises(NganXungDot):
        with a.lo() as lo:
            lo.them("luot_abbyy", {"ma_tuong_quan": "DEMO-khac"}, {"bam_noi_dung": "DEMO"})
    with b.lo() as lo:
        lo.them("luot_abbyy", {"ma_tuong_quan": "DEMO"}, {"bam_noi_dung": "DEMO"})


def test_cas_khong_tai_su_dung_phien_sau_xoa():
    ngan = ngan_demo()
    with ngan.lo() as lo:
        lo.them("cau_hinh", {}, {})
    cu = ngan.doc("cau_hinh", {})
    with ngan.lo() as lo:
        lo.xoa("cau_hinh", {}, row_version=cu.row_version)
        lo.them("cau_hinh", {}, {})
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.sua("cau_hinh", {}, {}, row_version=cu.row_version)


def test_doc_la_ban_sao_va_tim_phan_trang():
    ngan = ngan_demo()
    with ngan.lo() as lo:
        for i in range(4):
            lo.them("trang_thai_engine", {"ma": str(i)}, {"lan": i})
    trang = ngan.tim("trang_thai_engine", loc={}, gioi_han=2)
    trang.danh_sach[0].gia_tri["lan"] = 99
    assert ngan.doc("trang_thai_engine", {"ma": "0"}).gia_tri["lan"] == 0
    tiep = ngan.tim("trang_thai_engine", loc={}, gioi_han=2, tiep=trang.tiep)
    assert [b.gia_tri["lan"] for b in tiep.danh_sach] == [2, 3] and tiep.tiep is None


def test_chon_ngan_that_hoac_ram_canh_bao_mot_lan(monkeypatch, capsys):
    monkeypatch.setattr(cong_ngan, "_DA_CANH_BAO", False)
    that = object()
    assert chon_ngan(SimpleNamespace(ngan=that)) is that
    app = SimpleNamespace(thu_muc_goi=GOI)
    a = chon_ngan(app)
    assert isinstance(a, NganBoNho) and chon_ngan(app) is a
    chon_ngan(SimpleNamespace(thu_muc_goi=GOI))
    assert capsys.readouterr().err.count("Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng") == 1


def test_cau_hinh_thieu_mac_dinh_va_khoi_dong_lai_mat_ram():
    assert doc_cau_hinh(ngan_demo(), SCHEMA) is None
    dat_cau_hinh({})
    cfg = doc_cau_hinh(ngan_demo(), SCHEMA)
    assert cfg["abbyy"]["han_muc_trang_30_ngay"] == 5000
    assert cfg["tesseract"] == {"duong_dan": "", "ngon_ngu": "vie+eng"}
    assert ngan_demo().doc("cau_hinh", {}).gia_tri == {}  # Không ghi default ngược ngăn.
    assert doc_cau_hinh(tao_ngan(), SCHEMA) is None


@pytest.mark.parametrize("gia_tri", [{"khoa": "DEMO"}, {"abbyy": {"bat": 1}},
    {"abbyy": {"han_muc_trang_30_ngay": 5001}}, {"abbyy": {"thoi_han_giay": 0}},
    {"tesseract": {"ngon_ngu": ""}}])
def test_cau_hinh_sai_schema_bi_tu_choi(gia_tri):
    dat_cau_hinh(gia_tri)
    with pytest.raises(CauHinhKhongHopLe):
        doc_cau_hinh(ngan_demo(), SCHEMA)


def test_thieu_cau_hinh_abbyy_bao_dung_cau():
    _, kq = chay_moi(nguon="chi_abbyy")
    assert kq["loi"]["ma"] == "CHUA_CAU_HINH"
    assert "Admin vào Quản lý engine › OCR › Cấu hình." in kq["loi"]["thong_diep"]


def test_cas_giu_trang_thu_lai_khong_tru_hai_lan(hot_folder, monkeypatch):
    ngan = ngan_demo()
    lo_goc = ngan.lo
    so_xung_dot = []

    @contextmanager
    def lo_canh_tranh():
        with lo_goc() as lo:
            yield lo
            if not so_xung_dot:
                so_xung_dot.append(True)
                # Ghi cạnh tranh qua API public, sau khi engine chụp sổ và xếp lệnh.
                with lo_goc() as khac:
                    khac.them("trang_thai_engine", {"ma": "han_muc"}, {"lan": 1})

    monkeypatch.setattr(ngan, "lo", lo_canh_tranh)
    with ABBYYGia(hot_folder[0], hot_folder[1], PDF) as gia:
        _, kq = chay_moi()
    assert kq["trang_thai"] == "XONG", kq
    assert so_xung_dot == [True] and len(gia.cac_tep) == 1
    assert SoHanMuc().da_dung() == 1 and SoHanMuc()._doc()[1]["dang_giu"] == {}
    assert len(ngan.tim("luot_abbyy", loc={"phap_nhan_id": "pn-demo"}).danh_sach) == 1


def test_ngan_ram_nhan_du_khai_bao_va_giu_ngan_sdk():
    ung_dung = SimpleNamespace()
    ngan = chay._ngan_ung_dung(ung_dung)
    assert chay._ngan_ung_dung(ung_dung) is ngan
    assert ngan.doc("cau_hinh", {}) is None
    so = SoHanMuc(ngan)
    nk = nhat_ky(so=so)
    nk.giu(1)
    assert nk.doc()["trang_thai"] == "dang_gui"
    assert so._doc()[1]["dang_giu"] == {nk.ma: 1}
    ngan_sdk = object()
    assert chay._ngan_ung_dung(SimpleNamespace(ngan=ngan_sdk)) is ngan_sdk


@pytest.mark.parametrize("loai_loi", [NganXungDot, NganKhongHopLe, CauHinhKhongHopLe])
def test_loi_ngan_chung_duoc_doi_tai_cong_sdk(monkeypatch, loai_loi):
    loi = loai_loi()

    def hong(*args, **kwargs):
        raise loi

    monkeypatch.setattr(chay, "trich_van_ban", hong)
    with pytest.raises(LoiNghiepVu) as bat:
        chay._doc(SimpleNamespace(ngan=ngan_demo()))
    assert (bat.value.ma, bat.value.thong_diep, bat.value.thu_lai_duoc) == (
        loi.ma, loi.thong_diep, loi.thu_lai_duoc)


def test_engine_dung_ngan_theo_viec_da_gan_phap_nhan(hot_folder, monkeypatch):
    # Mô phỏng SDK 2.1 cấp view theo việc; engine không cần API nội bộ RAM.
    that = ngan_demo()
    view = that.cho_phap_nhan("pn-demo")
    doc_goc = chay._doc

    def doc(viec):
        viec.ngan = view
        return doc_goc(viec)

    monkeypatch.setattr(chay, "_doc", doc)
    monkeypatch.setattr(chay.app, "ngan", object())  # Không được dùng ngăn app.
    with ABBYYGia(hot_folder[0], hot_folder[1], PDF) as gia:
        _, kq = chay_moi()
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1 and SoHanMuc(that).da_dung() == 1
    assert len(view.tim("luot_abbyy").danh_sach) == 1
    assert that.tim("luot_abbyy", loc={"phap_nhan_id": "pn-DEMO-khac"}).danh_sach == []


def test_hai_viec_hai_ben_nua_dem_van_chung_moc_cas_han_muc():
    bat_dau = threading.Barrier(2)
    luc = int(datetime(2026, 11, 15, 23, 59, 59, tzinfo=timezone.utc).timestamp())
    cac_so = [SoHanMuc(dong_ho=lambda: luc), SoHanMuc(dong_ho=lambda: luc + 1)]
    for so in cac_so:
        doc_goc = so._doc

        def mot_lan(so=so, doc_goc=doc_goc):
            anh = doc_goc()
            so._doc = doc_goc
            bat_dau.wait(5)
            return anh

        so._doc = mot_lan

    def giu(so):
        try:
            so.giu(1, 1)
            return "giu_duoc"
        except LoiNghiepVu as loi:
            return loi.ma

    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_lan = [nhom.submit(giu, so) for so in cac_so]
        assert sorted(k.result(timeout=10) for k in cac_lan) == ["ABBYY_HET_HAN_MUC", "giu_duoc"]
    assert sum(SoHanMuc()._doc()[1]["dang_giu"].values()) == 1


def test_nhieu_ngay_het_han_khong_lam_lo_vuot_100_lenh():
    ngan = ngan_demo()
    cac_ngay = [(date(2026, 1, 1) + timedelta(days=n)).isoformat() for n in range(120)]
    for dau in (0, 60):
        with ngan.lo() as lo:
            for ngay in cac_ngay[dau:dau + 60]:
                lo.them("han_muc_ngay", {"ngay": ngay}, {"da_nhan": {"0": 1}, "dang_giu": {}})
    so = SoHanMuc(dong_ho=lambda: datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp())
    ma = so.giu(1, 1)
    assert so.da_dung() == 0 and so._doc()[1]["dang_giu"] == {ma: 1}
    assert len(ngan.tim("han_muc_ngay", loc={}, gioi_han=500).danh_sach) == 121


def test_engine_chi_can_ba_ham_public_cua_ngan(hot_folder, monkeypatch):
    that = ngan_demo()

    class CongGia:
        def doc(self, *args, **kwargs):
            return that.doc(*args, **kwargs)

        def tim(self, *args, **kwargs):
            return that.tim(*args, **kwargs)

        def lo(self):
            return that.lo()

    monkeypatch.setattr(chay.app, "ngan", CongGia())
    with ABBYYGia(hot_folder[0], hot_folder[1], PDF):
        _, kq = chay_moi()
    assert kq["trang_thai"] == "XONG", kq
    assert SoHanMuc().da_dung() == 1


def test_doc_cu_khong_tao_the_he_moi_sau_luot_khac_vua_xong(hot_folder, monkeypatch):
    da_doc, tiep_tuc = threading.Event(), threading.Event()
    doc_goc = NhatKyLuot.doc
    chu = []

    def doc(nk):
        kq = doc_goc(nk)
        if not chu:
            chu.append(threading.get_ident())
            da_doc.set()
            assert tiep_tuc.wait(10)
        return kq

    monkeypatch.setattr(NhatKyLuot, "doc", doc)
    with ABBYYGia(hot_folder[0], hot_folder[1], PDF) as gia, ThreadPoolExecutor(max_workers=1) as nhom:
        tre = nhom.submit(chay_moi)
        assert da_doc.wait(5)
        _, xong = chay_moi()
        assert xong["trang_thai"] == "XONG", xong
        tiep_tuc.set()
        _, kq = tre.result(timeout=10)
    assert kq["trang_thai"] == "CHUA_RO", kq
    assert len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1


def test_quyen_xu_ly_cas_khong_nha_trang_hay_gui_lai_khi_het_han():
    luc = [1800000000]
    so = SoHanMuc(dong_ho=lambda: luc[0])
    a, b = nhat_ky(so=so), nhat_ky(so=so)
    a.giu(1)
    b.doc()
    viec = SimpleNamespace(kiem_huy=lambda: None)
    with a.xu_ly(viec):
        with pytest.raises(ChuaRo):
            with b.xu_ly(viec):
                pass
        luc[0] += 31
        with b.xu_ly(viec):
            with pytest.raises(ChuaRo):
                a.cap_nhat(nhan=True)
        assert so._doc()[1]["dang_giu"] == {a.ma: 1}
    assert so.da_dung() == 0


def test_trang_thai_ghi_vao_ngan_va_khong_chua_duong_dan(hot_folder):
    ngan = ngan_demo()
    chay.ghi_trang_thai(ngan)
    tt = ngan.doc("trang_thai_engine", {"ma": "abbyy"}).gia_tri
    assert tt["abbyy_bat"] is True and tt["ly_do"] == "bat" and tt["luc_kiem"]
    assert str(hot_folder[0]) not in json.dumps(tt)
    from test_ocr_2 import cau_hinh_abbyy
    cau_hinh_abbyy(bat=False)
    chay.ghi_trang_thai(ngan)
    assert ngan.doc("trang_thai_engine", {"ma": "abbyy"}).gia_tri["abbyy_bat"] is False


def test_trang_thai_chay_dinh_ky_va_dung_luong(monkeypatch):
    da_ghi = threading.Event()
    cac_lan = []

    def ghi(ngan):
        cac_lan.append(ngan)
        if len(cac_lan) >= 2:
            da_ghi.set()

    monkeypatch.setattr(chay, "ghi_trang_thai", ghi)
    app = SimpleNamespace(ngan=ngan_demo(), chay=lambda: da_ghi.wait(5))
    chay.chay_engine(ung_dung=app, khoang_giay=0.01)
    assert len(cac_lan) >= 2
    assert not any(t.name == "trang-thai-ocr" for t in threading.enumerate())


def test_khai_21_khong_chen_vao_manifest_20():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert not set(KHAI) & set(phieu)
    ds = {b["bang"]: b for b in KHAI["ngan_du_lieu"]}
    assert ds["luot_abbyy"]["duy_nhat"] == [["phap_nhan_id", "bam_noi_dung"]]
    assert "giu_toi_da_ngay" not in ds["luot_abbyy"]  # Không tự hết hạn lượt chưa rõ.
    assert ds["han_muc_ngay"]["pham_vi"] == "engine"
