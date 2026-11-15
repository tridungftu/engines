"""OCR-4 đã kiểm bằng Core giả (CoreGia), ABBYY giả; chỉ dữ liệu DEMO.

Có tiến trình spawn chết thật sau công bố; không phụ thuộc fork/Windows API.
"""

from hashlib import sha256
import json
import multiprocessing
import os
from pathlib import Path

import pytest

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, Viec, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from demo.tao_pdf import DONG_DEMO, pdf_demo
from e_ocr import abbyy, chay as cong
from e_ocr.chon_nguon import KHOA_HAN_MUC, SoHanMuc
from e_ocr.kho_tam import KhoTam
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
            assert luot["bam"] == "sha256:" + sha256(RAW).hexdigest()
            assert luot["so_trang"] == luot["lan_gui"] == 1
            assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {luot["ma_tuong_quan"]: 1}
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
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}
    assert not list(ra.iterdir())
    if nang_luc == WORD:
        assert core.doc_tep(muon["ket_qua"]["tep"]["tep_id"]).startswith(b"PK")
    else:
        text = muon["ket_qua"].get("van_ban", muon["ket_qua"].get("van_ban_tai_lieu", {}).get("van_ban"))
        assert all(d in text for d in DONG_DEMO)
    noi_dung_kho = (KhoTam().thu_muc / "kho.json").read_text(encoding="utf-8")
    assert "DEMO.pdf" not in noi_dung_kho and "VND" not in noi_dung_kho and "Công ty" not in noi_dung_kho


def _chet(vao, kenh, truoc_gui=False):
    # os._exit mô phỏng chết đột ngột: không finally, không ghi nhận đã nhận.
    if truoc_gui:
        abbyy.BackendABBYY.doc_pdf = lambda *a, **k: os._exit(23)
    else:
        thay = abbyy.os.replace

        def cong_bo(nguon, dich):
            thay(nguon, dich)
            if Path(dich).parent == Path(vao):
                kenh.send(Path(dich).stem)
                os._exit(23)

        abbyy.os.replace = cong_bo
    chay_moi()


def _gui_dong_thoi(bat_dau, kenh, doc_do=None):
    if doc_do is not None:
        doc_goc = NhatKyLuot.doc

        def doc(nk):
            luot = doc_goc(nk)
            doc_do.wait(10)
            return luot

        NhatKyLuot.doc = doc
    try:
        assert bat_dau.wait(10)
        _, kq = chay_moi()
        kenh.send((kq["trang_thai"], kq["ma_tuong_quan"]))
    finally:
        kenh.close()


def dung_cac_tien_trinh(cac_tt):
    for tt in cac_tt:
        tt.join(10)
        if tt.is_alive():
            tt.terminate()
            tt.join(5)
        assert not tt.is_alive()


def test_chet_that_sau_cong_bo_khoi_dong_lai_chot_cho_giu(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    ctx = multiprocessing.get_context("spawn")
    cha, con = ctx.Pipe()
    tt = ctx.Process(target=_chet, args=(str(vao), con))
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        try:
            tt.start()
            con.close()
            assert cha.poll(15), "Tiến trình DEMO chưa công bố tệp."
            ma = cha.recv()
            assert gia.da_nhan.wait(5)
        finally:
            dung_cac_tien_trinh([tt])
            cha.close()
        assert tt.exitcode == 23
        assert nhat_ky().doc()["trang_thai"] == "dang_gui"
        assert SoHanMuc().da_dung() == 0
        assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {ma: 1}
        core, kq = chay_moi(lan_thu=2)
        kiem_chua_ro(core, kq, ma)
        # Không thấy tệp sau crash chưa đủ để biết chết trước/sau công bố.
        assert SoHanMuc().da_dung() == 0
        (ra / f"{ma}.pdf").write_bytes(PDF)
        _, kq = chay_moi(lan_thu=3)
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1 and not tess_gia
    assert SoHanMuc().da_dung() == 1 and nhat_ky().doc()["trang_thai"] == "xong"
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}


def test_chet_truoc_cong_bo_khong_tu_hoan_khoi_dong_lai_co_bang_chung_thi_nha(hot_folder):
    vao, ra, _ = hot_folder
    ctx = multiprocessing.get_context("spawn")
    cha, con = ctx.Pipe()
    tt = ctx.Process(target=_chet, args=(str(vao), con, True))
    try:
        tt.start()
        con.close()
    finally:
        dung_cac_tien_trinh([tt])
        cha.close()
    assert tt.exitcode == 23
    luot = nhat_ky().doc()
    ma = luot["ma_tuong_quan"]
    core, kq = chay_moi(lan_thu=2)
    kiem_chua_ro(core, kq, ma)
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {ma: 1}
    assert SoHanMuc().da_dung() == 0
    bien_nhan_loi(ra, ma)
    _, kq = chay_moi(lan_thu=3, nguon="chi_abbyy")
    assert kq["loi"]["ma"] == "ABBYY_TU_CHOI", kq
    assert nhat_ky().doc()["trang_thai"] == "tu_choi" and nhat_ky().doc()["da_hoan"]
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}
    assert not list(vao.iterdir()) and not list(ra.iterdir())


def test_hai_tien_trinh_gui_tep_trung_chi_mot_luot_abbyy(hot_folder):
    vao, ra, _ = hot_folder
    ctx = multiprocessing.get_context("spawn")
    bat_dau = ctx.Event()
    cac_tt, cac_kenh = [], []
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        try:
            for _ in range(2):
                cha, con = ctx.Pipe()
                tt = ctx.Process(target=_gui_dong_thoi, args=(bat_dau, con))
                tt.start()
                con.close()
                cac_tt.append(tt)
                cac_kenh.append(cha)
            bat_dau.set()
            for kenh in cac_kenh:
                assert kenh.poll(15), "Tiến trình DEMO chưa trả trạng thái."
            kq = [kenh.recv() for kenh in cac_kenh]
        finally:
            dung_cac_tien_trinh(cac_tt)
            for kenh in cac_kenh:
                kenh.close()
    assert all(tt.exitcode == 0 for tt in cac_tt)
    assert kq[0] == kq[1] == ("CHUA_RO", nhat_ky().doc()["ma_tuong_quan"])
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
    assert SoHanMuc().da_dung() == 1 and SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}


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
    vao, _, _ = hot_folder
    thay = os.replace

    def hong(nguon, dich):
        if Path(dich).name == "kho.json":
            raise PermissionError("Lỗi ghi DEMO.")
        return thay(nguon, dich)

    with monkeypatch.context() as tam:
        tam.setattr(os, "replace", hong)
        _, kq = chay_moi()
    assert kq["loi"]["ma"] == "KHO_TAM_KHONG_TRUY_CAP", kq
    assert nhat_ky().doc() is None and KhoTam().doc(KHOA_HAN_MUC) is None
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
    so = SoHanMuc(KhoTam(tmp_path / "so-DEMO"), dong_ho=lambda: luc[0])
    nk = nhat_ky(so=so)
    luot, moi = nk.giu(1)
    assert moi
    ma = luot["ma_tuong_quan"]
    luc[0] += 60 * 86400
    nk2 = nhat_ky(so=SoHanMuc(KhoTam(so.kho.thu_muc), dong_ho=lambda: luc[0]))
    lap, moi = nk2.giu(1)
    assert not moi and lap == luot
    assert so.kho.doc(KHOA_HAN_MUC)["dang_giu"] == {ma: 1}
    nk2.cap_nhat("tu_choi")
    tiep, moi = nk2.giu(1)
    assert moi and tiep["lan_gui"] == 2 and tiep["ma_tuong_quan"] != ma
    assert tiep["ma_tuong_quan"] == nk2._ma_luot(2)


@pytest.mark.parametrize("nguon", ["tu_dong", "chi_abbyy", "chi_tesseract"])
def test_thieu_cau_hinh_khi_giao_lai_van_chua_ro_khong_chuyen(hot_folder, tess_gia, monkeypatch, nguon):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        _, dau = chay_moi()
        monkeypatch.delenv("KTT_ENGINE_CAU_HINH")
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
        assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {dau["ma_tuong_quan"]: 1}
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
    nk.kho.ghi(nk.khoa, luot)
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


def test_hai_tien_trinh_cung_lay_pdf_muon_khong_gianh_doc_don(hot_folder):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False):
        _, dau = chay_moi()
    ma = dau["ma_tuong_quan"]
    (ra / f"{ma}.pdf").write_bytes(PDF)
    ctx = multiprocessing.get_context("spawn")
    bat_dau, doc_do = ctx.Event(), ctx.Barrier(2)
    cac_tt, cac_kenh = [], []
    try:
        for _ in range(2):
            cha, con = ctx.Pipe()
            tt = ctx.Process(target=_gui_dong_thoi, args=(bat_dau, con, doc_do))
            tt.start()
            con.close()
            cac_tt.append(tt)
            cac_kenh.append(cha)
        bat_dau.set()
        for kenh in cac_kenh:
            assert kenh.poll(15), "Tiến trình DEMO chưa trả trạng thái."
        kq = [kenh.recv() for kenh in cac_kenh]
    finally:
        dung_cac_tien_trinh(cac_tt)
        for kenh in cac_kenh:
            kenh.close()
    assert all(tt.exitcode == 0 for tt in cac_tt)
    assert sorted(trang_thai for trang_thai, _ in kq) == ["CHUA_RO", "XONG"]
    assert ("CHUA_RO", ma) in kq
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
        assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {ma: 1}
        _, lap = chay_moi(lan_thu=3, nguon="chi_abbyy")
    assert lap["loi"]["ma"] == "ABBYY_TU_CHOI", lap
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}
    assert SoHanMuc().da_dung() == 0 and not tep_loi.exists() and not tep_vao.exists() and not tess_gia
