"""OCR-2 đã kiểm bằng Core giả (CoreGia); chỉ dữ liệu và thư mục DEMO."""

from datetime import datetime, timezone
import io
import json
import multiprocessing
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw, ImageFont

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

from demo.tao_pdf import DONG_DEMO, pdf_demo
from e_ocr import abbyy, chon_nguon, tesseract
from e_ocr.chon_nguon import KHOA_HAN_MUC, SoHanMuc
from e_ocr.kho_tam import KhoTam
from e_ocr.lop_chu import doc_lop_chu
from test_ocr_1 import ABBYYGia, DOC, VAN_BAN, chay, hot_folder, kiem_loi


@pytest.fixture
def tess_gia(monkeypatch):
    calls = []

    def doc(raw, mime, cau_hinh, *, viec):
        viec.kiem_huy()
        calls.append((raw, mime, cau_hinh))
        from e_ocr.lop_chu import dem_trang
        n = dem_trang(raw, mime)
        return doc_lop_chu(pdf_demo(*([DONG_DEMO] * n)))

    monkeypatch.setattr(tesseract, "doc_tesseract", doc)
    return calls


def cau_hinh_abbyy(**phan_abbyy):
    from e_ocr.cau_hinh_may import doc_cau_hinh
    import os
    cau_hinh = doc_cau_hinh(bat_buoc=True)
    cau_hinh["abbyy"].update(phan_abbyy)
    Path(os.environ["KTT_ENGINE_CAU_HINH"]).write_text(json.dumps(cau_hinh), encoding="utf-8")


def kiem_chuyen(kq, ly_do):
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert data["nguon_doc"] == "tesseract"
    assert data["ly_do_chuyen_nguon"] == chon_nguon.LY_DO[ly_do]
    assert all(d in data["van_ban"] for d in DONG_DEMO)


def test_het_han_muc_chuyen_truoc_gui(hot_folder, tess_gia):
    vao, _, tam = hot_folder
    so = SoHanMuc()
    # DEMO: nhận 4.999 trang bằng nhiều lượt hợp lệ, không chứa nội dung.
    luc = int(so.dong_ho())
    ngay = datetime.fromtimestamp(luc, timezone.utc).date().isoformat()
    so.kho.ghi(KHOA_HAN_MUC, {"da_nhan": {ngay: {str(luc % 86400): 4999}}, "dang_giu": {}})
    _, kq = chay(pdf_demo((), (), ()))
    kiem_chuyen(kq, "het_han_muc")
    assert len(tess_gia) == 1 and not tam and not list(vao.iterdir())
    assert so.da_dung() == 4999
    assert so.kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}


def test_dung_han_muc_van_uu_tien_abbyy(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    cau_hinh_abbyy(han_muc_trang_30_ngay=3)
    with ABBYYGia(vao, ra, pdf_demo(DONG_DEMO, DONG_DEMO, DONG_DEMO)):
        _, kq = chay(pdf_demo((), (), ()))
    assert kq["trang_thai"] == "XONG", kq
    assert kq["ket_qua"]["van_ban_tai_lieu"]["nguon_doc"] == "abbyy"
    assert kq["ket_qua"]["van_ban_tai_lieu"]["ly_do_chuyen_nguon"] is None
    assert SoHanMuc().da_dung() == 3 and not tess_gia


@pytest.mark.parametrize("tat", ["bat", "duong_dan"])
def test_abbyy_tat_hoac_mat_thu_muc(hot_folder, tess_gia, tat):
    vao, _, tam = hot_folder
    if tat == "bat":
        cau_hinh_abbyy(bat=False)
    else:
        cau_hinh_abbyy(thu_muc_vao=str(vao / "khong-co-DEMO"))
    _, kq = chay(pdf_demo(()))
    kiem_chuyen(kq, "khong_ket_noi")
    assert not tam and len(tess_gia) == 1
    assert SoHanMuc().da_dung() == 0


def test_chua_cau_hinh_tu_dong_dung_du_phong(tess_gia):
    _, kq = chay(pdf_demo(()))
    kiem_chuyen(kq, "khong_ket_noi")
    assert len(tess_gia) == 1


def test_timeout_truoc_nhan_rut_roi_chuyen(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", nhan=False):
        _, kq = chay(pdf_demo(()))
    kiem_chuyen(kq, "qua_thoi_gian")
    assert len(tess_gia) == 1 and SoHanMuc().da_dung() == 0
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}


def test_loi_gui_chac_chan_chua_nhan_duoc_chuyen(hot_folder, tess_gia, monkeypatch):
    vao, _, _ = hot_folder
    thay_goc = abbyy.os.replace

    def loi(nguon, dich):
        if Path(dich).parent == vao:
            raise PermissionError("DEMO loi gui")
        return thay_goc(nguon, dich)

    monkeypatch.setattr(abbyy.os, "replace", loi)
    _, kq = chay(pdf_demo(()))
    kiem_chuyen(kq, "loi_nhan_dang")
    assert len(tess_gia) == 1 and SoHanMuc().da_dung() == 0


@pytest.mark.parametrize("nguon", ["tu_dong", "chi_abbyy"])
def test_da_nhan_chua_tra_khong_chuyen_va_khong_hoan(hot_folder, tess_gia, nguon):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False):
        core, kq = chay(pdf_demo(()), tham_so={"nguon": nguon})
    assert kq["trang_thai"] == "CHUA_RO", kq
    assert kq["ma_tuong_quan"] and not tess_gia
    assert core.so_lan_ghi["ket_qua"] == 0
    assert SoHanMuc().da_dung() == 1


def test_khong_rut_duoc_chua_chac_da_nhan_giu_cho_khong_tru(hot_folder, tess_gia, monkeypatch):
    vao, _, _ = hot_folder
    with monkeypatch.context() as tam:
        tam.setattr(abbyy, "_rut_tep", lambda tep: False)
        _, kq = chay(pdf_demo(()))
    assert kq["trang_thai"] == "CHUA_RO", kq
    assert SoHanMuc().da_dung() == 0 and not tess_gia
    assert sum(SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"].values()) == 1
    assert kq["ma_tuong_quan"] in SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"]
    # Chỉ dọn đúng tệp DEMO vừa được ca này tạo, sau khi đã kiểm metadata.
    for tep in vao.iterdir():
        tep.unlink()


def test_abbyy_da_tra_thieu_chu_khong_chuyen(hot_folder, tess_gia):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, pdf_demo(())):
        core, kq = chay(pdf_demo(()))
    kiem_loi(core, kq, "ABBYY_THIEU_LOP_CHU")
    assert not tess_gia and SoHanMuc().da_dung() == 1


@pytest.mark.parametrize("ly_do,ma", [
    ("tat", "ABBYY_DANG_TAT"), ("han_muc", "ABBYY_HET_HAN_MUC"),
    ("timeout", "ABBYY_QUA_THOI_HAN"),
])
def test_chi_abbyy_khong_chuyen(hot_folder, tess_gia, ly_do, ma):
    vao, ra, _ = hot_folder
    if ly_do == "tat":
        cau_hinh_abbyy(bat=False)
    if ly_do == "han_muc":
        cau_hinh_abbyy(han_muc_trang_30_ngay=0)
    with ABBYYGia(vao, ra, b"", nhan=False):
        core, kq = chay(pdf_demo(()), tham_so={"nguon": "chi_abbyy"})
    kiem_loi(core, kq, ma)
    assert not tess_gia and SoHanMuc().da_dung() == 0


@pytest.mark.parametrize("nang_luc", [DOC, VAN_BAN])
def test_chi_tesseract_bo_abbyy_va_so(hot_folder, tess_gia, monkeypatch, nang_luc):
    def cam(*args, **kwargs):
        raise AssertionError("Chỉ Tesseract không được chạm ABBYY/sổ.")

    monkeypatch.setattr(chon_nguon, "BackendABBYY", cam)
    monkeypatch.setattr(chon_nguon, "SoHanMuc", cam)
    _, kq = chay(pdf_demo(()), nang_luc, tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    assert len(tess_gia) == 1
    if nang_luc == DOC:
        data = kq["ket_qua"]["van_ban_tai_lieu"]
        assert data["nguon_doc"] == "tesseract" and data["ly_do_chuyen_nguon"] is None
    else:
        assert all(d in kq["ket_qua"]["van_ban"] for d in DONG_DEMO)


@pytest.mark.parametrize("nguon", ["tu_dong", "chi_tesseract"])
def test_thieu_tesseract_bao_ma_ro_khi_can_dung(monkeypatch, nguon):
    def chua_cai(cau_hinh):
        raise LoiNghiepVu("NGUON_DU_PHONG_CHUA_CAI", "Chưa cài nguồn Tesseract dự phòng.")

    monkeypatch.setattr(tesseract, "tim_tesseract", chua_cai)
    core, kq = chay(pdf_demo(()), tham_so={"nguon": nguon})
    kiem_loi(core, kq, "NGUON_DU_PHONG_CHUA_CAI")


def test_loi_kho_khong_duoc_gia_la_het_han_muc_va_chuyen(hot_folder, tess_gia):
    SoHanMuc().kho.ghi(KHOA_HAN_MUC, {"DEMO": 1})
    core, kq = chay(pdf_demo(()))
    kiem_loi(core, kq, "SO_HAN_MUC_CAN_KIEM_TRA")
    assert not tess_gia


def test_cua_so_truot_30_ngay_chinh_xac_va_qua_thang(tmp_path):
    luc = [int(datetime(2026, 10, 31, 23, 59, 59, tzinfo=timezone.utc).timestamp())]
    so = SoHanMuc(KhoTam(tmp_path / "so-DEMO"), dong_ho=lambda: luc[0])
    ma = so.giu(3, 5000)
    assert so.da_dung() == 0
    so.ghi_nhan(ma)
    luc[0] += 1
    assert so.da_dung() == 3  # Qua đầu tháng vẫn tính.
    luc[0] += 30 * 86400 - 2
    assert so.da_dung() == 3  # Còn đúng một giây trong cửa sổ.
    luc[0] += 1
    assert so.da_dung() == 0  # Đúng biên 30 ngày thì hết hạn.
    ma = so.giu(1, 1)
    so.bo_giu(ma)
    assert so.kho.doc(KHOA_HAN_MUC) == {"da_nhan": {}, "dang_giu": {}}


def _giu_dong_thoi(thu_muc, bat_dau, kenh):
    bat_dau.wait(10)
    try:
        SoHanMuc(KhoTam(thu_muc)).giu(1, 1)
        kenh.send("giu_duoc")
    except LoiNghiepVu as loi:
        kenh.send(loi.ma)
    finally:
        kenh.close()


def test_hai_tien_trinh_khong_cung_vuot_han_muc(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    bat_dau = ctx.Event()
    tt, kenh = [], []
    for _ in range(2):
        cha, con = ctx.Pipe()
        p = ctx.Process(target=_giu_dong_thoi, args=(str(tmp_path / "so-DEMO"), bat_dau, con))
        p.start()
        con.close()
        tt.append(p)
        kenh.append(cha)
    try:
        bat_dau.set()
        for k in kenh:
            assert k.poll(15), "Tiến trình DEMO chưa phản hồi."
        assert sorted(k.recv() for k in kenh) == ["ABBYY_HET_HAN_MUC", "giu_duoc"]
    finally:
        for p in tt:
            p.join(10)
            if p.is_alive():
                p.terminate()
                p.join(5)
            assert p.exitcode == 0
        for k in kenh:
            k.close()
    assert SoHanMuc(KhoTam(tmp_path / "so-DEMO")).da_dung() == 0


@pytest.fixture
def cli_gia(monkeypatch):
    calls = []
    monkeypatch.setattr(tesseract, "tim_tesseract", lambda cfg: "tesseract-DEMO")

    def run(lenh, *, viec, thoi_han, ma_loi, doc_stdout=False):
        viec.kiem_huy()
        calls.append(lenh)
        if "--list-langs" in lenh:
            return b"List of available languages (2):\neng\nvie\n"
        with Image.open(lenh[1]) as anh:
            assert anh.width > 20 and anh.height > 20
        text = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        for i, s in enumerate(DONG_DEMO, 1):
            text += f"5\t1\t1\t1\t{i}\t1\t10\t{20*i}\t200\t15\t95\t{s}\n"
        Path(lenh[2]).with_suffix(".tsv").write_text(text, encoding="utf-8")
        return b""

    monkeypatch.setattr(tesseract, "_chay", run)
    return calls


@pytest.mark.parametrize("mime,fmt", [("image/png", "PNG"), ("image/jpeg", "JPEG")])
def test_cli_mock_anh_tra_toa_do_va_don_tam(cli_gia, mime, fmt):
    raw = io.BytesIO()
    with Image.new("RGB", (600, 200), "white") as anh:
        anh.save(raw, format=fmt)
    _, kq = chay(raw.getvalue(), mime=mime, tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert data["nguon_doc"] == "tesseract"
    assert data["van_ban"] == "\n".join(DONG_DEMO)
    for khoi in data["trang"][0]["khoi"]:
        assert khoi["dong"][0]["tu"][0]["hop"] == khoi["hop"]
    assert len(cli_gia) == 2 and not Path(cli_gia[1][1]).parent.exists()


def test_cli_mock_pdf_tron_khong_ocr_lai_trang_co_chu(cli_gia):
    _, kq = chay(pdf_demo(DONG_DEMO, (), DONG_DEMO), tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    assert kq["ket_qua"]["van_ban_tai_lieu"]["van_ban"] == "\f".join(["\n".join(DONG_DEMO)] * 3)
    assert len(cli_gia) == 2 and "trang-2.png" in cli_gia[1][1]
    assert not Path(cli_gia[1][1]).parent.exists()


def test_cli_mock_giu_bang_vector_o_rong_o_gop(cli_gia, monkeypatch):
    chay_goc = tesseract._chay

    def run(lenh, **kwargs):
        out = chay_goc(lenh, **kwargs)
        if "--list-langs" not in lenh:
            tep = Path(lenh[2]).with_suffix(".tsv")
            with tep.open("a", encoding="utf-8") as f:
                for i, (x, y, text) in enumerate([
                    (60, 200, "BANG DEMO"), (60, 230, "DEMO"), (190, 230, "1.000.000 VND"),
                    (60, 260, "DEMO"), (190, 260, "30/10/2026"),
                ], 10):
                    f.write(f"5\t1\t2\t1\t{i}\t1\t{int(x*150/72)}\t{int(y*150/72)}\t160\t15\t95\t{text}\n")
                # Cùng dòng OCR với ô đầu hàng 1, nhưng nằm bên trái bảng.
                f.write(f"5\t1\t2\t1\t11\t2\t10\t{int(230*150/72)}\t50\t15\t95\tGHI CHU DEMO\n")
        return out

    monkeypatch.setattr(tesseract, "_chay", run)
    _, kq = chay(pdf_demo((), bang=True, chu_bang=False), tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    bang, = [b for b in kq["ket_qua"]["van_ban_tai_lieu"]["trang"][0]["khoi"] if b["loai"] == "bang"]
    assert len(bang["o"]) == 7 and bang["o"][0]["gop_cot"] == 3
    assert [o["van_ban"] for o in bang["o"]] == ["BANG DEMO", "DEMO", "1.000.000 VND", "", "DEMO", "30/10/2026", ""]
    assert any(b.get("van_ban") == "GHI CHU DEMO" for b in kq["ket_qua"]["van_ban_tai_lieu"]["trang"][0]["khoi"])


def test_tesseract_tsv_hong_khong_tra_thanh_cong():
    with pytest.raises(LoiNghiepVu) as loi:
        tesseract._doc_tsv(b"DEMO TSV hong", so=1, rong=100, cao=100, pixel=(100, 100))
    assert loi.value.ma == "TESSERACT_KHONG_DOC_DUOC"


def test_thieu_model_ngon_ngu_bao_chua_cai(cli_gia, monkeypatch):
    monkeypatch.setattr(tesseract, "_chay", lambda *a, **k: b"eng\n")
    core, kq = chay(pdf_demo(()), tham_so={"nguon": "chi_tesseract"})
    kiem_loi(core, kq, "NGUON_DU_PHONG_CHUA_CAI")


def test_huy_tesseract_dung_tien_trinh_va_khong_lo_lenh(monkeypatch):
    da_kill = []
    process = SimpleNamespace(returncode=None, stdout=None)
    process.communicate = lambda **k: (_ for _ in ()).throw(tesseract.subprocess.TimeoutExpired("DEMO", 1))
    process.poll = lambda: process.returncode
    process.kill = lambda: (da_kill.append(True), setattr(process, "returncode", -9))
    process.wait = lambda **k: None
    monkeypatch.setattr(tesseract.subprocess, "Popen", lambda *a, **k: process)
    calls = []

    def huy():
        calls.append(True)
        if len(calls) == 3:
            raise ViecDaHuy()

    with pytest.raises(ViecDaHuy):
        tesseract._chay(["DEMO"], viec=SimpleNamespace(kiem_huy=huy), thoi_han=10, ma_loi="DEMO")
    assert da_kill == [True]


def test_tesseract_that_neu_co_tren_may():
    try:
        tesseract._kiem_bo_doc({}, SimpleNamespace(kiem_huy=lambda: None))
    except LoiNghiepVu as loi:
        if loi.ma == "NGUON_DU_PHONG_CHUA_CAI":
            pytest.skip(f"Không có Tesseract thật hoặc đủ vie+eng: {loi.ma}.")
        raise
    raw = io.BytesIO()
    with Image.new("RGB", (1600, 350), "white") as anh:
        ve = ImageDraw.Draw(anh)
        font = ImageFont.load_default(size=46)
        for y, text in zip((35, 130, 225), ("CONG TY DEMO ANH DUONG", "1.000.000 VND", "30/10/2026")):
            ve.text((50, y), text, font=font, fill="black")
        anh.save(raw, format="PNG")
    _, kq = chay(raw.getvalue(), mime="image/png", tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert "DEMO" in data["van_ban"] and "1.000.000 VND" in data["van_ban"]
    assert "30/10/2026" in data["van_ban"]
    assert data["nguon_doc"] == "tesseract" and data["trang"][0]["khoi"]


def test_xuat_word_chon_tesseract(hot_folder, tess_gia):
    vao, _, _ = hot_folder
    core, kq = chay(pdf_demo(()), nang_luc="ocr.xuat_word@1", tham_so={"nguon": "chi_tesseract"})
    assert kq["trang_thai"] == "XONG", kq
    assert len(tess_gia) == 1 and not list(vao.iterdir())
    assert core.doc_tep(kq["ket_qua"]["tep"]["tep_id"]).startswith(b"PK")


def test_xuat_word_chi_abbyy_khong_du_phong(tess_gia):
    core, kq = chay(pdf_demo(()), nang_luc="ocr.xuat_word@1", tham_so={"nguon": "chi_abbyy"})
    assert kq["trang_thai"] == "LOI", kq
    assert not tess_gia and core.so_lan_ghi["ket_qua"] == 0
