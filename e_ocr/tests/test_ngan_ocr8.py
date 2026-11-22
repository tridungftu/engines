"""Hợp đồng ngăn và lỗi cạnh tranh OCR-8; đã kiểm bằng Core giả (CoreGia)."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
import json
import threading
from types import SimpleNamespace

import pytest

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from e_ocr import chay
from kho_tri_thuc_sdk.engine import Engine, NganEngine, NganXungDot, LoiDuongTruyen
from kho_tri_thuc_sdk.thu import CoreGia
from e_ocr.luot_abbyy import doc_map, ghi_map, doc_so_nguyen
from e_ocr.luot_abbyy import NhatKyLuot
from ngan_demo import GOI, KHAI, SoHanMuc, dat_cau_hinh, ngan_demo, core_demo, cau_hinh_hien_tai
from test_ocr_1 import ABBYYGia, hot_folder
from test_ocr_4 import PDF, chay_moi, nhat_ky


def test_ca_lo_rollback_khi_cas_lech():
    ngan = ngan_demo()
    with ngan.lo() as lo:
        lo.them("trang_thai_engine", {"ma": "DEMO", "lan": 1})
    cu = ngan.doc("trang_thai_engine", {"ma": "DEMO"})
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.them("han_muc_ngay", {"ngay": "2026-11-15", "da_nhan": "{}"})
            lo.sua("trang_thai_engine", {"ma": "DEMO"}, {"lan": 2}, row_version=cu.row_version + 1)
    assert ngan.tim("han_muc_ngay", loc={}).danh_sach == []
    assert doc_so_nguyen(ngan.doc("trang_thai_engine", {"ma": "DEMO"}).gia_tri["lan"]) == 1


def test_lo_nem_loi_trong_with_khong_ghi():
    with pytest.raises(ValueError):
        with ngan_demo().lo() as lo:
            lo.them("trang_thai_engine", {"ma": "DEMO", "lan": 1})
            raise ValueError("Lỗi DEMO.")
    assert ngan_demo().doc("trang_thai_engine", {"ma": "DEMO"}) is None


def test_lay_hoac_tao_hai_luong_chi_mot_ban():
    ngan = ngan_demo()
    bat_dau = threading.Barrier(2)

    def tao(ma):
        bat_dau.wait(5)
        with ngan.lo() as lo:
            lo.lay_hoac_tao("luot_abbyy", {"bam_noi_dung": "DEMO"}, luot_demo(ma))
        return lo.ket_qua[0].da_tao

    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_lan = [nhom.submit(tao, ma) for ma in ("DEMO-A", "DEMO-B")]
        assert sorted(k.result(timeout=10) for k in cac_lan) == [False, True]
    assert len(core_demo().xem_ngan("e_ocr", "luot_abbyy")) == 1


def test_rang_buoc_duy_nhat_va_pham_vi():
    ngan = ngan_demo()
    a, b = ngan_demo("pn-DEMO-A"), ngan_demo("pn-DEMO-B")
    with a.lo() as lo:
        lo.them("luot_abbyy", luot_demo("DEMO"))
    assert b.doc("luot_abbyy", {"ma_tuong_quan": "DEMO"}) is None
    assert b.tim("luot_abbyy", loc={}).danh_sach == []
    with pytest.raises(NganXungDot):
        with a.lo() as lo:
            lo.them("luot_abbyy", luot_demo("DEMO-khac"))
    with b.lo() as lo:
        lo.them("luot_abbyy", luot_demo("DEMO"))
    assert len(core_demo().xem_ngan("e_ocr", "luot_abbyy")) == 2
    # Core không tin pháp nhân client tự khai, view B vẫn chỉ thấy B.
    assert b.doc("luot_abbyy", {"ma_tuong_quan": "DEMO", "phap_nhan_id": "pn-DEMO-A"}).gia_tri["phap_nhan_id"] == "pn-DEMO-B"


def test_cas_khong_tai_su_dung_phien_sau_doi_trang_thai():
    ngan = ngan_demo()
    with ngan.lo() as lo:
        lo.them("trang_thai_engine", {"ma": "DEMO", "lan": 1})
    cu = ngan.doc("trang_thai_engine", {"ma": "DEMO"})
    with ngan.lo() as lo:
        lo.sua("trang_thai_engine", {"ma": "DEMO"}, {"lan": 2}, row_version=cu.row_version)
    with pytest.raises(NganXungDot):
        with ngan.lo() as lo:
            lo.sua("trang_thai_engine", {"ma": "DEMO"}, {"lan": 3}, row_version=cu.row_version)
    with pytest.raises(LoiNghiepVu) as loi:
        with ngan.lo() as lo:
            lo.xoa("trang_thai_engine", {"ma": "DEMO"})
    assert loi.value.ma == "NGAN_KHONG_XOA"


def test_doc_la_ban_sao_va_tim_phan_trang():
    ngan = ngan_demo()
    with ngan.lo() as lo:
        for i in range(4):
            lo.them("trang_thai_engine", {"ma": str(i), "lan": i})
    trang = ngan.tim("trang_thai_engine", loc={}, gioi_han=2, sap_xep=[{"truong": "ma", "giam": False}])
    trang.danh_sach[0].gia_tri["lan"] = 99
    assert doc_so_nguyen(ngan.doc("trang_thai_engine", {"ma": "0"}).gia_tri["lan"]) == 0
    tiep = ngan.tim("trang_thai_engine", loc={}, gioi_han=2, tiep=trang.tiep,
                   sap_xep=[{"truong": "ma", "giam": False}])
    assert [doc_so_nguyen(b.gia_tri["lan"]) for b in tiep.danh_sach] == [2, 3] and tiep.tiep is None


def test_chi_dung_ngan_sdk_khong_tao_ram_khi_chua_ket_noi(capsys):
    app = Engine.tu_khai_bao(GOI / "engine.json")
    assert isinstance(app.ngan, NganEngine)
    with pytest.raises(LoiNghiepVu) as loi:
        app.ngan.doc("trang_thai_engine", {"ma": "abbyy"})
    assert loi.value.ma == "ENGINE_CHUA_SAN_SANG"
    assert capsys.readouterr().err == ""
    for ten in ("ngan.py", "cau_hinh.py"):
        assert not (GOI / "e_ocr" / ten).exists()
        assert (GOI.parents[1] / "LUU-TRU" / "OCR-9" / ten).is_file()


def test_cau_hinh_mac_dinh_va_giu_qua_app_moi():
    cfg = cau_hinh_hien_tai()
    assert cfg["abbyy"]["han_muc_trang_30_ngay"] == 5000
    assert cfg["tesseract"] == {"duong_dan": "", "ngon_ngu": "vie+eng"}
    dat_cau_hinh({"abbyy": {"han_muc_trang_30_ngay": 7}})
    app = Engine.tu_khai_bao(GOI / "engine.json")
    dt = core_demo().duong_truyen(app.ma)
    dt.chuan_bi(app.phieu, app.thu_muc_goi)
    assert dt.san_sang(app.phien_ban, [])["abbyy"]["han_muc_trang_30_ngay"] == 7
    assert cau_hinh_hien_tai()["abbyy"]["han_muc_trang_30_ngay"] == 7
    assert not core_demo().xem_ngan("e_ocr", "cau_hinh")
    khac = CoreGia(KHAI, thu_muc_goi=GOI)
    assert khac.duong_truyen("e_ocr").doc_cau_hinh()["cau_hinh"]["abbyy"]["han_muc_trang_30_ngay"] == 5000


@pytest.mark.parametrize("gia_tri", [{"khoa": "DEMO"}, {"abbyy": {"bat": 1}},
    {"abbyy": {"han_muc_trang_30_ngay": 5001}}, {"abbyy": {"thoi_han_giay": 0}},
    {"tesseract": {"ngon_ngu": ""}}])
def test_cau_hinh_sai_schema_bi_tu_choi(gia_tri):
    cu = cau_hinh_hien_tai()
    with pytest.raises(LoiDuongTruyen) as loi:
        dat_cau_hinh(gia_tri)
    assert loi.value.ma == "NGAN_DU_LIEU_SAI"
    assert cau_hinh_hien_tai() == cu


def test_thieu_cau_hinh_abbyy_bao_dung_cau():
    _, kq = chay_moi(nguon="chi_abbyy")
    assert kq["loi"]["ma"] == "CHUA_CAU_HINH"
    assert "Admin vào Quản lý engine › OCR › Cấu hình." in kq["loi"]["thong_diep"]


def test_cas_giu_trang_thu_lai_khong_tru_hai_lan(hot_folder):
    core_demo().gay_xung_dot_ngan("trang_thai_engine", so_lan=1)
    with ABBYYGia(hot_folder[0], hot_folder[1], PDF) as gia:
        _, kq = chay_moi()
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1
    assert SoHanMuc().da_dung() == 1 and SoHanMuc()._doc()[1]["dang_giu"] == {}
    assert len(core_demo().xem_ngan("e_ocr", "luot_abbyy")) == 1


def test_ngan_sdk_nhan_du_khai_bao_va_dung_view_theo_viec():
    ngan = ngan_demo()
    assert isinstance(ngan, NganEngine)
    so = SoHanMuc(ngan)
    nk = nhat_ky(so=so)
    nk.giu(1)
    assert nk.doc()["trang_thai"] == "dang_gui"
    assert so._doc()[1]["dang_giu"] == {nk.ma: 1}
    assert core_demo().xem_ngan("e_ocr", "luot_abbyy")[0]["phap_nhan_id"] == "pn-demo"


@pytest.mark.parametrize("loai_loi", ["NGAN_XUNG_DOT", "NGAN_DU_LIEU_SAI", "CAU_HINH_KHONG_HOP_LE"])
def test_loi_ngan_chung_duoc_giu_tai_cong_sdk(monkeypatch, loai_loi):
    loi = LoiNghiepVu(loai_loi, "Lỗi cấu hình hoặc dữ liệu DEMO.", thu_lai_duoc=loai_loi == "NGAN_XUNG_DOT")

    def hong(*args, **kwargs):
        raise loi

    monkeypatch.setattr(chay, "trich_van_ban", hong)
    with pytest.raises(LoiNghiepVu) as bat:
        chay._doc(SimpleNamespace(ngan=ngan_demo()))
    assert (bat.value.ma, bat.value.thong_diep, bat.value.thu_lai_duoc) == (
        loi.ma, loi.thong_diep, loi.thu_lai_duoc)


def test_engine_dung_ngan_theo_viec_da_gan_phap_nhan(hot_folder, monkeypatch):
    doc_goc = chay.trich_van_ban

    def doc(viec, **kw):
        assert kw["ngan"] is viec.ngan
        return doc_goc(viec, **kw)

    monkeypatch.setattr(chay, "trich_van_ban", doc)
    with ABBYYGia(hot_folder[0], hot_folder[1], PDF) as gia:
        _, kq = chay_moi()
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1
    assert len(ngan_demo().tim("luot_abbyy").danh_sach) == 1
    assert ngan_demo("pn-DEMO-khac").tim("luot_abbyy").danh_sach == []


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
                lo.them("han_muc_ngay", {"ngay": ngay, "da_nhan": ghi_map({"0": 1})})
    so = SoHanMuc(dong_ho=lambda: datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp())
    ma = so.giu(1, 1)
    assert so.da_dung() == 0 and so._doc()[1]["dang_giu"] == {ma: 1}
    for _ in range(2):
        so.bo_giu("DEMO-khong-co")
    # Dòng lịch sử do Core ẩn theo TTL, không bị ghi lại/gia hạn khi dọn.
    hang = core_demo().xem_ngan("e_ocr", "han_muc_ngay")
    assert len(hang) == 120 and all(b["row_version"] == 1 for b in hang)


def test_engine_chi_can_ba_ham_public_cua_ngan(hot_folder, monkeypatch):
    doc_goc = chay.trich_van_ban

    class CongGia:
        def __init__(self, ngan):
            self.ngan = ngan

        def doc(self, *args, **kwargs):
            return self.ngan.doc(*args, **kwargs)

        def tim(self, *args, **kwargs):
            return self.ngan.tim(*args, **kwargs)

        def lo(self):
            return self.ngan.lo()

    def doc(viec, **kw):
        return doc_goc(viec, **{**kw, "ngan": CongGia(viec.ngan)})

    monkeypatch.setattr(chay, "trich_van_ban", doc)
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
    chay.ghi_trang_thai(ngan, cau_hinh_hien_tai())
    tt = ngan.doc("trang_thai_engine", {"ma": "abbyy"}).gia_tri
    assert tt["abbyy_bat"] is True and tt["ly_do"] == "bat" and tt["luc_kiem"]
    assert str(hot_folder[0]) not in json.dumps(tt)
    from test_ocr_2 import cau_hinh_abbyy
    cau_hinh_abbyy(bat=False)
    chay.ghi_trang_thai(ngan, cau_hinh_hien_tai())
    assert ngan.doc("trang_thai_engine", {"ma": "abbyy"}).gia_tri["abbyy_bat"] is False


def test_trang_thai_chay_dinh_ky_va_dung_luong(monkeypatch):
    da_ghi = threading.Event()
    cac_lan = []

    def ghi(ngan, cau_hinh):
        cac_lan.append(ngan)
        if len(cac_lan) >= 2:
            da_ghi.set()

    monkeypatch.setattr(chay, "ghi_trang_thai", ghi)
    app = SimpleNamespace(ngan=ngan_demo(), cau_hinh={}, chay=lambda: da_ghi.wait(5))
    chay.chay_engine(ung_dung=app, khoang_giay=0.01)
    assert len(cac_lan) >= 2
    assert not any(t.name == "trang-thai-ocr" for t in threading.enumerate())


def test_khai_22_trong_manifest_va_luu_tru_cong_tam():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert phieu["tuong_thich"]["sdk"] == ">=2.4.0 <3.0.0"
    ds = {b["bang"]: b for b in phieu["ngan_du_lieu"]}
    assert "cau_hinh" not in ds
    assert ["phap_nhan_id", "bam_noi_dung"] in ds["luot_abbyy"]["duy_nhat"]
    assert "giu_toi_da_ngay" not in ds["luot_abbyy"]  # Không tự hết hạn lượt chưa rõ.
    assert ds["han_muc_ngay"]["pham_vi"] == "engine"
    assert ds["han_muc_ngay"]["giu_toi_da_ngay"] == 45
    assert "giu_toi_da_ngay" not in ds["trang_thai_engine"]
    assert phieu["cau_hinh"] == {"schema": "cau_hinh.schema.json"}
    assert (GOI.parents[1] / "LUU-TRU" / "OCR-9" / "KHAI-SDK-2.1.json").is_file()


@pytest.mark.parametrize("ngon_ngu", ["vie", "eng", "vie+eng", "eng+vie"])
def test_schema_chap_nhan_dung_bon_ngon_ngu(ngon_ngu):
    dat_cau_hinh({"tesseract": {"ngon_ngu": ngon_ngu}})
    assert cau_hinh_hien_tai()["tesseract"]["ngon_ngu"] == ngon_ngu


@pytest.mark.parametrize("ngon_ngu", ["fra", "vie+fra", "vie+eng+vie", " eng", "VIE"])
def test_schema_tu_choi_ngon_ngu_ngoai_danh_sach(ngon_ngu):
    with pytest.raises(LoiDuongTruyen):
        dat_cau_hinh({"tesseract": {"ngon_ngu": ngon_ngu}})


def doc_chua_ro(ngan):
    b = ngan.doc("trang_thai_engine", {"ma": "chua_ro"})
    return None if b is None else {"ma": "chua_ro", "so_luot": doc_so_nguyen(b.gia_tri["so_luot"]),
                                 "theo_ngay": doc_map(b.gia_tri["theo_ngay"])}


def test_tong_hop_chua_ro_chi_co_so_dem_va_ngay_khong_lo_phap_nhan():
    ngan = ngan_demo()
    luc = int(datetime(2026, 11, 14, 23, 59, 59, tzinfo=timezone.utc).timestamp())
    so = SoHanMuc(dong_ho=lambda: luc)
    a = NhatKyLuot(SoHanMuc(ngan_demo("pn-DEMO-A"), dong_ho=so.dong_ho), "pn-DEMO-A", "sha256:" + "a" * 64, 1)
    b = NhatKyLuot(SoHanMuc(ngan_demo("pn-DEMO-B"), dong_ho=so.dong_ho), "pn-DEMO-B", "sha256:" + "b" * 64, 2)
    a.giu(5000)
    assert doc_chua_ro(ngan) is None  # Đang gửi không phải chưa rõ.
    a.cap_nhat("chua_ro")
    a.cap_nhat("chua_ro")
    luc += 2
    b.giu(5000)
    b.cap_nhat("chua_ro", nhan=True)
    assert doc_chua_ro(ngan) == {"ma": "chua_ro", "so_luot": 2,
                                "theo_ngay": {"2026-11-14": 1, "2026-11-15": 1}}
    for nk in (a, b):
        for rieng in (nk.phap_nhan_id, nk.bam, nk.ma):
            assert rieng not in json.dumps(doc_chua_ro(ngan))
    a.cap_nhat("xong", nhan=True)
    a.cap_nhat("xong", nhan=True)
    assert doc_chua_ro(ngan)["theo_ngay"] == {"2026-11-15": 1}
    b.cap_nhat("tu_choi")
    assert doc_chua_ro(ngan) == {"ma": "chua_ro", "so_luot": 0, "theo_ngay": {}}
    assert so.da_dung() == 1


@pytest.mark.parametrize("ra_chua_ro", [False, True])
def test_tong_hop_luot_va_han_muc_cung_rollback_khi_lo_loi(monkeypatch, ra_chua_ro):
    so = SoHanMuc()
    nk = nhat_ky(so=so)
    nk.giu(5000)
    if ra_chua_ro:
        nk.cap_nhat("chua_ro")
    cu = (nk.doc(), doc_chua_ro(nk.ngan), so._doc()[1])
    ghi_goc = so._ghi

    def hong(*args):
        ghi_goc(*args)
        raise NganXungDot()

    monkeypatch.setattr(so, "_ghi", hong)
    with pytest.raises(LoiNghiepVu, match="Dữ liệu OCR vừa thay đổi"):
        nk.cap_nhat("xong" if ra_chua_ro else "chua_ro", nhan=True)
    assert (nk.doc(), doc_chua_ro(nk.ngan), so._doc()[1]) == cu
    monkeypatch.setattr(so, "_ghi", ghi_goc)
    nk.cap_nhat("xong" if ra_chua_ro else "chua_ro", nhan=True)
    assert doc_chua_ro(nk.ngan)["so_luot"] == (0 if ra_chua_ro else 1)
    assert so.da_dung() == 1


def test_hai_phap_nhan_cap_nhat_chua_ro_dong_thoi_khong_mat_dem(monkeypatch):
    ngan = ngan_demo()
    so = SoHanMuc(dong_ho=lambda: datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp())
    cac_nk = [NhatKyLuot(SoHanMuc(ngan_demo("pn-DEMO-" + c), dong_ho=so.dong_ho),
                       "pn-DEMO-" + c, "sha256:" + c * 64, 1) for c in ("a", "b")]
    for nk in cac_nk:
        nk.giu(5000)
    doc_goc = ngan.doc
    bat_dau = threading.Barrier(2)
    da_doc = set()

    def doc(bang, khoa):
        b = doc_goc(bang, khoa)
        ma = threading.get_ident()
        if bang == "trang_thai_engine" and khoa == {"ma": "chua_ro"} and ma not in da_doc:
            da_doc.add(ma)
            bat_dau.wait(5)
        return b

    monkeypatch.setattr(ngan, "doc", doc)
    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_lan = [nhom.submit(nk.cap_nhat, "chua_ro") for nk in cac_nk]
        for lan in cac_lan:
            lan.result(timeout=10)
    monkeypatch.setattr(ngan, "doc", doc_goc)
    assert doc_chua_ro(ngan) == {"ma": "chua_ro", "so_luot": 2, "theo_ngay": {"2026-11-15": 2}}


def test_don_ngay_cu_giu_dung_bien_30_ngay_va_khong_mat_cho_giu():
    ngan = ngan_demo()
    luc = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp())
    so = SoHanMuc(dong_ho=lambda: luc)
    ma_cu = so.giu(2, 5000)
    with ngan.lo() as lo:
        lo.them("han_muc_ngay", {"ngay": "2026-10-16", "da_nhan": ghi_map({"43200": 1, "43201": 3})})
    luc = int(datetime(2026, 11, 15, 12, tzinfo=timezone.utc).timestamp())
    ma_moi = so.giu(1, 5000)
    assert ngan.doc("han_muc_ngay", {"ngay": "2026-10-01"}) is None
    assert ngan.doc("han_muc_ngay", {"ngay": "2026-10-16"}) is not None
    assert so.da_dung() == 3
    assert so._doc()[1]["dang_giu"] == {ma_cu: 2, ma_moi: 1}
    assert doc_map(ngan.doc("trang_thai_engine", {"ma": "han_muc"}).gia_tri["dang_giu"]) == {ma_cu: 2, ma_moi: 1}


def test_don_ngay_cu_cung_lo_rollback_va_thu_lai_khong_mat_han_muc(monkeypatch):
    ngan = ngan_demo()
    with ngan.lo() as lo:
        lo.them("han_muc_ngay", {"ngay": "2026-01-01", "da_nhan": ghi_map({"0": 1})})
    so = SoHanMuc(dong_ho=lambda: datetime(2026, 11, 15, tzinfo=timezone.utc).timestamp())
    lo_goc = ngan.lo

    @contextmanager
    def hong():
        with lo_goc() as lo:
            yield lo
            raise NganXungDot()

    monkeypatch.setattr(ngan, "lo", hong)
    with pytest.raises(LoiNghiepVu):
        so.giu(1, 1)
    assert ngan.doc("han_muc_ngay", {"ngay": "2026-01-01"}) is not None
    assert so._doc()[1]["dang_giu"] == {}
    monkeypatch.setattr(ngan, "lo", lo_goc)
    ma = so.giu(1, 1)
    assert ngan.doc("han_muc_ngay", {"ngay": "2026-01-01"}) is not None  # Core ẩn theo TTL, không xóa.
    assert so._doc()[1]["dang_giu"] == {ma: 1}


def luot_demo(ma):
    return {"ma_tuong_quan": ma, "bam_noi_dung": "DEMO", "so_trang": 1,
            "lan_gui": 1, "trang_thai": "dang_gui", "da_nhan": False, "da_hoan": False,
            "luc_giu": 0, "luc_nhan": None, "chu_xu_ly": None, "han_xu_ly": 0}
