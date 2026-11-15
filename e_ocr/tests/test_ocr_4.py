"""OCR-4 đã kiểm bằng Core giả (CoreGia), ABBYY giả; chỉ dữ liệu DEMO.

OCR-8: mô phỏng gián đoạn bằng cùng ngăn RAM; cạnh tranh bằng hai luồng.
"""

from hashlib import sha256
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import os
from pathlib import Path

import pytest

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, Viec, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from demo.tao_pdf import DONG_DEMO, pdf_demo
from e_ocr import abbyy, chay as cong
from ngan_demo import SoHanMuc, ngan_demo, bo_cau_hinh, ghi_luot
from e_ocr.luot_abbyy import NhatKyLuot
from test_ocr_1 import ABBYYGia, DOC, GOI, VAN_BAN, hot_folder
from test_ocr_2 import cau_hinh_abbyy, tess_gia


RAW = pdf_demo(())
PDF = pdf_demo(DONG_DEMO)
WORD = "ocr.xuat_word@1"


def app_moi():
    app = Engine.tu_khai_bao(str(GOI / "engine.json"))
    for ma, ham in [(DOC, cong.doc_tai_lieu), (VAN_BAN, cong.doc_van_ban), (WORD, cong.xuat_word)]:
        app.nang_luc(ma)(ham)
    assert app is not cong.app
    return app


def chay_moi(*, pn="pn-demo", lan_thu=1, nang_luc=DOC, nguon="tu_dong"):
    core = CoreGia()
    tep = core.them_tep("DEMO.pdf", RAW, "application/pdf")
    ma = core.giao_viec(nang_luc, {"loai": "tep", "tep": tep}, {"nguon": nguon}, phap_nhan_id=pn)
    # CoreGia tự tăng lan_thu lúc lấy việc, giống Core thật giao lại sau mất lease.
    core._viec[ma]["lan_thu"] = lan_thu - 1
    core.chay(app_moi())
    return core, core.xem(ma)


def nhat_ky(pn="pn-demo", so=None):
    return NhatKyLuot(so or SoHanMuc(), pn, "sha256:" + sha256(RAW).hexdigest(), 1)


def kiem_chua_ro(core, kq, ma=None):
    assert kq["trang_thai"] == "CHUA_RO", kq
    assert kq["ma_tuong_quan"] and (ma is None or kq["ma_tuong_quan"] == ma)
    assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == 0


def bien_nhan_loi(ra, ma, **sua):
    data = {"ma_tuong_quan": ma, "trang_thai": "tu_choi", "da_tieu_trang": False}
    data.update(sua)
    tep = ra / f"{ma}.loi.json"
    tep.write_text(json.dumps(data), encoding="utf-8")
    return tep


def test_ghi_luot_va_giu_trang_nguyen_tu_truoc_cong_bo(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    thay = os.replace
    da_kiem = []

    def cong_bo(nguon, dich):
        if Path(dich).parent == vao:
            nk = nhat_ky()
            luot = nk.doc()
            assert luot["trang_thai"] == "dang_gui" and not luot["da_nhan"]
            assert luot["bam_noi_dung"] == "sha256:" + sha256(RAW).hexdigest()
            assert luot["so_trang"] == luot["lan_gui"] == 1
            assert SoHanMuc()._doc()[1]["dang_giu"] == {luot["ma_tuong_quan"]: 1}
            assert Path(dich).stem == luot["ma_tuong_quan"] == nk._ma_luot(1)
            da_kiem.append(True)
        return thay(nguon, dich)

    monkeypatch.setattr(os, "replace", cong_bo)
    with ABBYYGia(vao, ra, PDF):
        _, kq = chay_moi()
    assert kq["trang_thai"] == "XONG", kq
    assert da_kiem == [True] and nhat_ky().doc()["trang_thai"] == "xong"
    assert not list(ra.iterdir())


@pytest.mark.parametrize("nang_luc", [DOC, VAN_BAN, WORD])
def test_app_moi_giao_lai_va_tra_muon_cung_ma_khong_gui_lai(hot_folder, tess_gia, nang_luc, monkeypatch):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        core, dau = chay_moi(nang_luc=nang_luc)
        kiem_chua_ro(core, dau)
        ma = dau["ma_tuong_quan"]
        cac_lan = []
        khoi_tao = Viec.__init__

        def viec_moi(viec, *args, **kwargs):
            khoi_tao(viec, *args, **kwargs)
            cac_lan.append(viec.lan_thu)

        monkeypatch.setattr(Viec, "__init__", viec_moi)
        core, lap = chay_moi(lan_thu=2, nang_luc=nang_luc)
        kiem_chua_ro(core, lap, ma)
        assert cac_lan == [2]
        (ra / f"{ma}.pdf").write_bytes(PDF)
        core, muon = chay_moi(lan_thu=3, nang_luc=nang_luc)
    assert muon["trang_thai"] == "XONG", muon
    assert len(gia.cac_tep) == 1 and not tess_gia
    assert nhat_ky().doc()["trang_thai"] == "xong"
    assert nhat_ky().doc()["ma_tuong_quan"] == ma
    assert SoHanMuc().da_dung() == 1
    assert SoHanMuc()._doc()[1]["dang_giu"] == {}
    assert not list(ra.iterdir())
    if nang_luc == WORD:
        assert core.doc_tep(muon["ket_qua"]["tep"]["tep_id"]).startswith(b"PK")
    else:
        text = muon["ket_qua"].get("van_ban", muon["ket_qua"].get("van_ban_tai_lieu", {}).get("van_ban"))
        assert all(d in text for d in DONG_DEMO)
    noi_dung_kho = json.dumps([b.gia_tri for b in ngan_demo().tim("luot_abbyy", loc={})["danh_sach"]])
    assert "DEMO.pdf" not in noi_dung_kho and "VND" not in noi_dung_kho and "Công ty" not in noi_dung_kho


def test_gian_doan_sau_cong_bo_chot_cho_giu_cung_ngan(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    luot, _ = nhat_ky().giu(5000)
    ma = luot["ma_tuong_quan"]
    # Trạng thái tương ứng crash sau công bố, trước callback ghi nhận.
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        (vao / f"{ma}.pdf").write_bytes(RAW)
        assert gia.da_nhan.wait(5)
        assert nhat_ky().doc()["trang_thai"] == "dang_gui"
        assert SoHanMuc().da_dung() == 0
        core, kq = chay_moi(lan_thu=2)
        kiem_chua_ro(core, kq, ma)
        assert SoHanMuc().da_dung() == 0
        (ra / f"{ma}.pdf").write_bytes(PDF)
        _, kq = chay_moi(lan_thu=3)
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1 and not tess_gia
    assert SoHanMuc().da_dung() == 1 and nhat_ky().doc()["trang_thai"] == "xong"
    assert SoHanMuc()._doc()[1]["dang_giu"] == {}


def test_gian_doan_truoc_cong_bo_khong_tu_hoan(hot_folder):
    vao, ra, _ = hot_folder
    luot, _ = nhat_ky().giu(5000)
    ma = luot["ma_tuong_quan"]
    core, kq = chay_moi(lan_thu=2)
    kiem_chua_ro(core, kq, ma)
    assert SoHanMuc()._doc()[1]["dang_giu"] == {ma: 1}
    assert SoHanMuc().da_dung() == 0
    bien_nhan_loi(ra, ma)
    _, kq = chay_moi(lan_thu=3, nguon="chi_abbyy")
    assert kq["loi"]["ma"] == "ABBYY_TU_CHOI", kq
    assert nhat_ky().doc()["trang_thai"] == "tu_choi" and nhat_ky().doc()["da_hoan"]
    assert SoHanMuc()._doc()[1]["dang_giu"] == {}
    assert not list(vao.iterdir()) and not list(ra.iterdir())


def test_hai_luong_gui_tep_trung_chi_mot_luot_abbyy(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    bat_dau = threading.Barrier(2)
    doc_goc = NhatKyLuot.doc

    def doc(nk):
        kq = doc_goc(nk)
        bat_dau.wait(5)
        return kq

    monkeypatch.setattr(NhatKyLuot, "doc", doc)
    with ABBYYGia(vao, ra, b"", tra=False) as gia, ThreadPoolExecutor(max_workers=2) as nhom:
        cac_lan = [nhom.submit(chay_moi) for _ in range(2)]
        kq = [lan.result(timeout=10)[1] for lan in cac_lan]
    monkeypatch.setattr(NhatKyLuot, "doc", doc_goc)
    assert all(k["trang_thai"] == "CHUA_RO" for k in kq), kq
    assert kq[0]["ma_tuong_quan"] == kq[1]["ma_tuong_quan"] == nhat_ky().doc()["ma_tuong_quan"]
    assert len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1


def test_cung_bam_khac_phap_nhan_khong_chan_nhau(hot_folder):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        _, a = chay_moi(pn="pn-DEMO-A")
        _, b = chay_moi(pn="pn-DEMO-B")
    assert a["trang_thai"] == b["trang_thai"] == "CHUA_RO"
    assert a["ma_tuong_quan"] != b["ma_tuong_quan"]
    assert len(gia.cac_tep) == 2 and SoHanMuc().da_dung() == 2


@pytest.mark.parametrize("huy", [True, False])
def test_huy_hoac_loi_sau_abbyy_tra_pdf_phai_don_ke_ca_chua_doc(hot_folder, monkeypatch, huy):
    vao, ra, _ = hot_folder
    kiem_goc = Viec.kiem_huy
    da_dung = []

    def kiem(viec):
        if list(ra.glob("*.pdf")):
            da_dung.append(True)
            if huy:
                raise ViecDaHuy()
            raise LoiNghiepVu("DEMO_LOI", "Lỗi DEMO sau khi nguồn trả kết quả.")
        kiem_goc(viec)

    monkeypatch.setattr(Viec, "kiem_huy", kiem)
    with ABBYYGia(vao, ra, PDF, tra=True):
        core, kq = chay_moi()
    assert kq["trang_thai"] == ("HUY" if huy else "LOI"), kq
    assert da_dung and not list(ra.iterdir())
    assert core.so_lan_ghi["ket_qua"] == 0
    assert nhat_ky().doc()["trang_thai"] == ("huy" if huy else "loi")
    assert SoHanMuc().da_dung() == 1 and SoHanMuc()._doc()[1]["dang_giu"] == {}


def test_loi_chot_ben_giu_pdf_chua_ro_roi_khoi_dong_lai_chot_mot_lan(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    cap_nhat = NhatKyLuot.cap_nhat

    def hong(nk, trang_thai=None, **kwargs):
        if trang_thai == "xong":
            raise LoiNghiepVu("DEMO_LOI_GHI", "Lỗi ghi DEMO.")
        return cap_nhat(nk, trang_thai, **kwargs)

    with ABBYYGia(vao, ra, PDF) as gia:
        with monkeypatch.context() as tam:
            tam.setattr(NhatKyLuot, "cap_nhat", hong)
            core, kq = chay_moi()
        kiem_chua_ro(core, kq)
        ma = kq["ma_tuong_quan"]
        assert (ra / f"{ma}.pdf").read_bytes() == PDF
        _, kq = chay_moi(lan_thu=2)
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1 and not list(ra.iterdir())


def test_ghi_giu_loi_khong_co_luot_hoac_trang_mot_nua(hot_folder, monkeypatch):
    from e_ocr.ngan import NganXungDot
    vao, _, _ = hot_folder
    ngan = ngan_demo()

    def hong(*args, **kwargs):
        raise NganXungDot()

    with monkeypatch.context() as tam:
        tam.setattr(ngan, "_ghi_lo", hong)
        _, kq = chay_moi()
    assert kq["loi"]["ma"] == "NGAN_XUNG_DOT", kq
    assert nhat_ky().doc() is None and SoHanMuc()._doc()[1] == {"da_nhan": {}, "dang_giu": {}}
    assert not list(vao.iterdir())


def test_tu_choi_ro_hoan_dung_luot_mot_lan_sau_khoi_dong_lai(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False):
        _, a = chay_moi(pn="pn-DEMO-A")
        _, b = chay_moi(pn="pn-DEMO-B")
        bien_nhan_loi(ra, a["ma_tuong_quan"])
        _, kq = chay_moi(pn="pn-DEMO-A", lan_thu=2)
    assert kq["trang_thai"] == "XONG" and len(tess_gia) == 1, kq
    nk = nhat_ky("pn-DEMO-A")
    assert nk.doc()["trang_thai"] == "tu_choi"
    nk.cap_nhat("tu_choi")
    assert SoHanMuc().da_dung() == 1
    assert nhat_ky("pn-DEMO-B").doc()["ma_tuong_quan"] == b["ma_tuong_quan"]


@pytest.mark.parametrize("truong,gia_tri", [("ma_tuong_quan", "0" * 32), ("da_tieu_trang", True), ("trang_thai", "loi")])
def test_khong_tu_hoan_theo_bien_nhan_thieu_bang_chung(hot_folder, tess_gia, truong, gia_tri):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        core, kq = chay_moi()
        ma = kq["ma_tuong_quan"]
        tep = bien_nhan_loi(ra, ma, **{truong: gia_tri})
        core, lap = chay_moi(lan_thu=2)
    kiem_chua_ro(core, lap, ma)
    assert SoHanMuc().da_dung() == 1 and not tess_gia and len(gia.cac_tep) == 1
    assert tep.exists()


@pytest.mark.parametrize("co_ket_qua", [True, False])
def test_luot_do_van_tra_cuu_khi_abbyy_tat_khong_du_phong(hot_folder, tess_gia, co_ket_qua):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        _, dau = chay_moi()
        ma = dau["ma_tuong_quan"]
        cau_hinh_abbyy(bat=False)
        if co_ket_qua:
            (ra / f"{ma}.pdf").write_bytes(PDF)
        core, lap = chay_moi(lan_thu=2)
    if co_ket_qua:
        assert lap["trang_thai"] == "XONG", lap
    else:
        kiem_chua_ro(core, lap, ma)
    assert not tess_gia and len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1


def test_khong_tu_het_han_luot_do_va_ma_tat_dinh_theo_lan_gui(tmp_path):
    luc = [1800000000]
    so = SoHanMuc(ngan_demo(), dong_ho=lambda: luc[0])
    nk = nhat_ky(so=so)
    luot, moi = nk.giu(1)
    assert moi
    ma = luot["ma_tuong_quan"]
    luc[0] += 60 * 86400
    nk2 = nhat_ky(so=SoHanMuc(so.ngan, dong_ho=lambda: luc[0]))
    lap, moi = nk2.giu(1)
    assert not moi and lap == luot
    assert so._doc()[1]["dang_giu"] == {ma: 1}
    nk2.cap_nhat("tu_choi")
    tiep, moi = nk2.giu(1)
    assert moi and tiep["lan_gui"] == 2 and tiep["ma_tuong_quan"] != ma
    assert tiep["ma_tuong_quan"] == nk2._ma_luot(2)


@pytest.mark.parametrize("nguon", ["tu_dong", "chi_abbyy", "chi_tesseract"])
def test_thieu_cau_hinh_khi_giao_lai_van_chua_ro_khong_chuyen(hot_folder, tess_gia, monkeypatch, nguon):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        _, dau = chay_moi()
        bo_cau_hinh()
        core, lap = chay_moi(lan_thu=2, nguon=nguon)
    kiem_chua_ro(core, lap, dau["ma_tuong_quan"])
    assert not tess_gia and len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1


@pytest.mark.parametrize("co_ket_qua", [True, False])
def test_doi_chi_tesseract_khong_bo_qua_luot_abbyy_do(hot_folder, tess_gia, co_ket_qua):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        _, dau = chay_moi()
        ma = dau["ma_tuong_quan"]
        if co_ket_qua:
            (ra / f"{ma}.pdf").write_bytes(PDF)
        core, lap = chay_moi(lan_thu=2, nguon="chi_tesseract")
    if co_ket_qua:
        assert lap["trang_thai"] == "XONG" and lap["ket_qua"]["van_ban_tai_lieu"]["nguon_doc"] == "abbyy", lap
    else:
        kiem_chua_ro(core, lap, ma)
    assert not tess_gia and len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1


def test_loi_ghi_nhan_giu_trang_va_pdf_cho_doi_chieu_lan_sau(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    cap_nhat = NhatKyLuot.cap_nhat

    def hong(nk, trang_thai=None, **kwargs):
        if kwargs.get("nhan"):
            raise LoiNghiepVu("DEMO_LOI_GHI", "Lỗi ghi DEMO.")
        return cap_nhat(nk, trang_thai, **kwargs)

    with ABBYYGia(vao, ra, PDF) as gia:
        with monkeypatch.context() as tam:
            tam.setattr(NhatKyLuot, "cap_nhat", hong)
            core, dau = chay_moi()
        kiem_chua_ro(core, dau)
        assert SoHanMuc().da_dung() == 0
        assert SoHanMuc()._doc()[1]["dang_giu"] == {dau["ma_tuong_quan"]: 1}
        assert gia.da_nhan.wait(3)
        # ABBYY giả có thể vừa nhận nhưng chưa kịp ghi PDF khi lần đầu kết thúc.
        gia.luong.join(0.03)
        if not (ra / f"{dau['ma_tuong_quan']}.pdf").exists():
            (ra / f"{dau['ma_tuong_quan']}.pdf").write_bytes(PDF)
        _, lap = chay_moi(lan_thu=2)
    assert lap["trang_thai"] == "XONG", lap
    assert len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1 and not list(ra.iterdir())


def test_loi_chot_tu_choi_giu_bien_nhan_de_khoi_dong_lai_hoan(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False):
        _, dau = chay_moi()
    ma = dau["ma_tuong_quan"]
    tep = bien_nhan_loi(ra, ma)
    cap_nhat = NhatKyLuot.cap_nhat

    def hong(nk, trang_thai=None, **kwargs):
        if trang_thai == "tu_choi":
            raise LoiNghiepVu("DEMO_LOI_GHI", "Lỗi ghi DEMO.")
        return cap_nhat(nk, trang_thai, **kwargs)

    with monkeypatch.context() as tam:
        tam.setattr(NhatKyLuot, "cap_nhat", hong)
        core, lap = chay_moi(lan_thu=2)
    kiem_chua_ro(core, lap, ma)
    assert tep.exists() and SoHanMuc().da_dung() == 1
    _, lap = chay_moi(lan_thu=3, nguon="chi_abbyy")
    assert lap["loi"]["ma"] == "ABBYY_TU_CHOI", lap
    assert not tep.exists() and SoHanMuc().da_dung() == 0


def test_pdf_muon_ghi_do_giu_lai_den_khi_du(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        _, dau = chay_moi()
        ma = dau["ma_tuong_quan"]
        tep = ra / f"{ma}.pdf"
        tep.write_bytes(PDF[:len(PDF) // 2])
        core, lap = chay_moi(lan_thu=2)
        kiem_chua_ro(core, lap, ma)
        assert tep.exists()
        tep.write_bytes(PDF)
        _, lap = chay_moi(lan_thu=3)
    assert lap["trang_thai"] == "XONG", lap
    assert len(gia.cac_tep) == 1 and SoHanMuc().da_dung() == 1 and not tess_gia


@pytest.mark.parametrize("sua", [{"trang_thai": "khong_hop_le"}, {"lan_gui": 0}, {"da_nhan": "khong"}, {"ma_tuong_quan": "0" * 32}])
def test_nhat_ky_hong_khong_tu_dat_lai_va_gui_trung(hot_folder, tess_gia, sua):
    nk = nhat_ky()
    luot, _ = nk.giu(5000)
    luot.update(sua)
    ghi_luot(nk, luot)
    _, kq = chay_moi()
    assert kq["loi"]["ma"] == "NHAT_KY_LUOT_CAN_KIEM_TRA", kq
    assert not tess_gia and not list(hot_folder[0].iterdir())


def test_luot_moi_sau_xong_tang_lan_gui_khong_trung_ma(hot_folder):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, PDF) as gia:
        _, a = chay_moi()
        ma_a = nhat_ky().doc()["ma_tuong_quan"]
        _, b = chay_moi()
    assert a["trang_thai"] == b["trang_thai"] == "XONG"
    assert len(gia.cac_tep) == 2 and nhat_ky().doc()["lan_gui"] == 2
    assert ma_a != nhat_ky().doc()["ma_tuong_quan"] and SoHanMuc().da_dung() == 2


def test_hai_luong_cung_lay_pdf_muon_khong_gianh_doc_don(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False):
        _, dau = chay_moi()
    ma = dau["ma_tuong_quan"]
    (ra / f"{ma}.pdf").write_bytes(PDF)
    bat_dau = threading.Barrier(2)
    doc_goc = NhatKyLuot.doc

    def doc(nk):
        luot = doc_goc(nk)
        bat_dau.wait(5)
        return luot

    with monkeypatch.context() as tam:
        tam.setattr(NhatKyLuot, "doc", doc)
        with ThreadPoolExecutor(max_workers=2) as nhom:
            cac_lan = [nhom.submit(chay_moi) for _ in range(2)]
            kq = [lan.result(timeout=10)[1] for lan in cac_lan]
    assert sorted(k["trang_thai"] for k in kq) == ["CHUA_RO", "XONG"], kq
    assert nhat_ky().doc()["trang_thai"] == "xong" and nhat_ky().doc()["lan_gui"] == 1
    assert SoHanMuc().da_dung() == 1 and not list(ra.iterdir()) and not list(vao.iterdir())


@pytest.mark.parametrize("rut_duoc", [True, False])
def test_tu_choi_ro_rut_tep_vao_con_cho_truoc_khi_hoan(hot_folder, tess_gia, monkeypatch, rut_duoc):
    vao, ra, _ = hot_folder
    with monkeypatch.context() as tam:
        tam.setattr(abbyy, "_rut_tep", lambda tep: False)
        core, dau = chay_moi()
    kiem_chua_ro(core, dau)
    ma = dau["ma_tuong_quan"]
    tep_vao = vao / f"{ma}.pdf"
    assert tep_vao.exists()
    tep_loi = bien_nhan_loi(ra, ma)
    don_goc = abbyy._don_tep
    with monkeypatch.context() as tam:
        if not rut_duoc:
            tam.setattr(abbyy, "_don_tep", lambda tep: False if tep == tep_vao else don_goc(tep))
        core, lap = chay_moi(lan_thu=2, nguon="chi_abbyy")
    if not rut_duoc:
        kiem_chua_ro(core, lap, ma)
        assert tep_loi.exists() and tep_vao.exists()
        assert SoHanMuc()._doc()[1]["dang_giu"] == {ma: 1}
        _, lap = chay_moi(lan_thu=3, nguon="chi_abbyy")
    assert lap["loi"]["ma"] == "ABBYY_TU_CHOI", lap
    assert SoHanMuc()._doc()[1]["dang_giu"] == {}
    assert SoHanMuc().da_dung() == 0 and not tep_loi.exists() and not tep_vao.exists() and not tess_gia
