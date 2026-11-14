"""OCR-MAY ca 2, 3, 4, 5, 7, 9: đã kiểm bằng Core giả (CoreGia).

ABBYY giả chỉ dùng thư mục DEMO tạm. Ca 1 chờ màn trạng thái Core; ca 6
chờ thiết kế trích vùng với e_doi_chieu; ca 8 chờ bí mật/cầu nối có khóa.
Số hàng chờ đọc từ CoreGia trong test, chưa là bằng chứng giao diện Core.
"""

import io
import json
from pathlib import Path
import threading
from types import SimpleNamespace
from xml.etree import ElementTree as ET
import zipfile

import pdfplumber
from PIL import Image
import pytest

from kho_tri_thuc_sdk.engine import LoiNghiepVu, Viec
from kho_tri_thuc_sdk.thu import CoreGia, nap_engine_tu_goi

from chay_demo import GOI, TesseractGia, chay_demo
from demo.tao_bo_demo import CONG_TY, TIEN, NGAY, tao_bo_demo
from e_ocr import tesseract
from e_ocr.chon_nguon import KHOA_HAN_MUC, SoHanMuc
from e_ocr.lop_chu import dem_trang
from e_ocr.xuat_word import MIME_DOCX, W
from test_ocr_1 import ABBYYGia, DOC, VAN_BAN, hot_folder, kiem_loi
from test_ocr_2 import cau_hinh_abbyy


WORD = "ocr.xuat_word@1"


@pytest.fixture(scope="module")
def bo_demo(tmp_path_factory):
    return tao_bo_demo(tmp_path_factory.mktemp("OCR-MAY-DEMO"))


def gui(tep, nang_luc=DOC, *, core=None, nguon="tu_dong"):
    core = core or CoreGia()
    mime = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg"}[tep.suffix]
    dau_vao = {"loai": "tep", "tep": core.them_tep(tep.name, tep.read_bytes(), mime)}
    return core, core.chay_thu(nap_engine_tu_goi(GOI), nang_luc, dau_vao, {"nguon": nguon})


def kiem_word(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None
        xml = archive.read("word/document.xml")
    assert b"<w:document" in xml and b"xmlns:w=" in xml
    assert b"ns0:" not in xml
    root = ET.fromstring(xml)
    text = "".join(n.text or "" for n in root.iter(W + "t"))
    assert all(chu in text for chu in (CONG_TY, TIEN, NGAY))
    tables = list(root.iter(W + "tbl"))
    assert len(tables) == 3
    for table in tables:
        assert len(table.findall(W + "tr")) == 4
        assert len(table.find(W + "tblGrid")) == 3
        assert len(list(table.iter(W + "tc"))) == 10
        span, = table.iter(W + "gridSpan")
        assert span.get(W + "val") == "3"
        assert sum(not list(c.iter(W + "t")) for c in table.iter(W + "tc")) == 1
        position = table.find(W + "tblPr/" + W + "tblpPr")
        assert int(position.get(W + "tblpX")) > 0
        assert int(position.get(W + "tblpY")) > 0


def test_bo_demo_la_anh_quet_that_va_word_dap_an(bo_demo):
    with pdfplumber.open(bo_demo.pdf_quet) as pdf:
        assert len(pdf.pages) == 3
        for page in pdf.pages:
            assert not page.chars and not page.lines
            assert len(page.images) == 1
            assert page.images[0]["srcsize"] == (1240, 1754)
    for tep, fmt in ((bo_demo.anh_png, "PNG"), (bo_demo.anh_jpeg, "JPEG")):
        with Image.open(tep) as anh:
            assert anh.format == fmt and anh.size == (1240, 1754)
            assert anh.getextrema()[0][0] == 0
    kiem_word(bo_demo.word_dap_an.read_bytes())
    dap_an = json.loads(bo_demo.dap_an.read_text(encoding="utf-8"))
    assert dap_an["truong"] == {"cong_ty": CONG_TY, "so_tien": {"so": 1000000, "tien_te": "VND"}, "ngay": "2026-10-30"}
    assert bo_demo.tep_qua_co.stat().st_size == 20 * 1024**2 + 1
    with pdfplumber.open(bo_demo.pdf_61_trang) as pdf:
        assert len(pdf.pages) == 61
    with pytest.raises(LoiNghiepVu) as loi:
        dem_trang(bo_demo.tep_hong.read_bytes(), "application/pdf")
    assert loi.value.ma == "TEP_HONG"
    assert not any((GOI / "demo" / tep.name).exists() for tep in (
        bo_demo.pdf_61_trang, bo_demo.tep_qua_co, bo_demo.tep_hong))
    with pytest.raises(FileExistsError):
        tao_bo_demo(bo_demo.thu_muc)


@pytest.mark.parametrize("nang_luc", [DOC, VAN_BAN, WORD])
def test_ca_2_pdf_quet_abbyy_vi_tri_word_tien_ngay(bo_demo, hot_folder, nang_luc):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, bo_demo.pdf_abbyy_gia.read_bytes()) as gia:
        core, kq = gui(bo_demo.pdf_quet, nang_luc)
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1 and gia.cac_tep[0][1] == bo_demo.pdf_quet.read_bytes()
    assert SoHanMuc().da_dung() == 3
    assert not list(ra.iterdir())
    if nang_luc == WORD:
        tep = kq["ket_qua"]["tep"]
        assert tep["mime"] == MIME_DOCX and tep["ten"] == "DEMO-quet-3-trang-OCR.docx"
        kiem_word(core.doc_tep(tep["tep_id"]))
        return
    data = kq["ket_qua"].get("van_ban_tai_lieu")
    text = data["van_ban"] if data else kq["ket_qua"]["van_ban"]
    assert len(text.split("\f")) == 3
    assert all(all(s in page for s in (CONG_TY, TIEN, NGAY)) for page in text.split("\f"))
    if data:
        assert data["nguon_doc"] == "abbyy" and data["so_trang"] == 3
        for n, page in enumerate(data["trang"], 1):
            assert page["so"] == n and page["don_vi"] == "pt"
            table, = [k for k in page["khoi"] if k["loai"] == "bang"]
            assert len(table["o"]) == 10
            assert table["o"][0]["gop_cot"] == 3
            assert sum(c["van_ban"] == "" for c in table["o"]) == 1
            assert all(len(k["hop"]) == 4 for k in page["khoi"])


def test_ca_3_hai_anh_hang_cho_va_trung_luot_do(bo_demo, hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    core, app = CoreGia(), nap_engine_tu_goi(GOI)
    viec = []
    for tep in (bo_demo.anh_png, bo_demo.anh_jpeg, bo_demo.anh_png):
        mime = "image/png" if tep.suffix == ".png" else "image/jpeg"
        ref = core.them_tep(tep.name, tep.read_bytes(), mime)
        viec.append(core.giao_viec(DOC, {"loai": "tep", "tep": ref}))
    # CoreGia chưa có API đếm hàng chờ: quan sát trạng thái công khai từng việc.
    assert sum(core.xem(v)["trang_thai"] == "CHO" for v in viec) == 3
    tien_do_goc, so_dang_cho = Viec.tien_do, []

    def tien_do(v, phan_tram, cau=""):
        if phan_tram == 5:
            so_dang_cho.append(sum(core.xem(ma)["trang_thai"] == "CHO" for ma in viec))
        return tien_do_goc(v, phan_tram, cau)

    monkeypatch.setattr(Viec, "tien_do", tien_do)
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        core.chay(app)
    ket_qua = [core.xem(v) for v in viec]
    assert so_dang_cho == [2, 1, 0]
    assert all(k["trang_thai"] == "CHUA_RO" and k["ket_qua"] is None for k in ket_qua)
    assert ket_qua[0]["ma_tuong_quan"] == ket_qua[2]["ma_tuong_quan"]
    assert ket_qua[1]["ma_tuong_quan"] != ket_qua[0]["ma_tuong_quan"]
    assert [raw for _, raw in gia.cac_tep] == [bo_demo.anh_png.read_bytes(), bo_demo.anh_jpeg.read_bytes()]
    assert SoHanMuc().da_dung() == 2 and core.so_lan_ghi["ket_qua"] == 0
    # Giao lại cùng CoreGia, trả muộn theo đúng hai mã: không gửi lại ảnh.
    for ma in {k["ma_tuong_quan"] for k in ket_qua}:
        (ra / (ma + ".pdf")).write_bytes(bo_demo.pdf_abbyy_anh.read_bytes())
    for tep in (bo_demo.anh_png, bo_demo.anh_jpeg):
        _, kq = gui(tep, core=core)
        assert kq["trang_thai"] == "XONG", kq
        assert kq["ket_qua"]["van_ban_tai_lieu"]["nguon_doc"] == "abbyy"
    assert SoHanMuc().da_dung() == 2 and not list(vao.iterdir()) and not list(ra.iterdir())


def so_do(text):
    doi_chieu = [{"trang": n, "truong": ten, "dung": chu in page}
                for n, page in enumerate(text.split("\f"), 1)
                for ten, chu in (("cong_ty", CONG_TY), ("so_tien", TIEN), ("ngay", NGAY))]
    dung = sum(c["dung"] for c in doi_chieu)
    return {"dung": dung, "sai": len(doi_chieu) - dung, "tong": len(doi_chieu), "doi_chieu": doi_chieu}


@pytest.mark.parametrize("gia", [True, False], ids=["tesseract-gia", "tesseract-that-neu-co"])
def test_ca_4_het_han_muc_do_dung_sai(bo_demo, hot_folder, tmp_path, record_property, gia):
    vao, _, _ = hot_folder
    cau_hinh_abbyy(han_muc_trang_30_ngay=0)
    if not gia:
        try:
            tesseract._kiem_bo_doc({}, SimpleNamespace(kiem_huy=lambda: None))
        except LoiNghiepVu as loi:
            if loi.ma == "NGUON_DU_PHONG_CHUA_CAI":
                pytest.skip("Không có Tesseract thật hoặc đủ vie+eng; nguồn giả vẫn kiểm ở ca riêng.")
            raise
    from contextlib import nullcontext
    with TesseractGia() if gia else nullcontext():
        _, kq = gui(bo_demo.pdf_quet)
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert data["nguon_doc"] == "tesseract" and "hạn mức" in data["ly_do_chuyen_nguon"]
    assert not list(vao.iterdir()) and SoHanMuc().da_dung() == 0
    do = {"nguon": "tesseract_gia" if gia else "tesseract_that", **so_do(data["van_ban"])}
    (tmp_path / "DEMO-so-do.json").write_text(json.dumps(do, ensure_ascii=False, indent=2), encoding="utf-8")
    record_property("so_do_DEMO", json.dumps(do, ensure_ascii=False))
    assert do["tong"] == 9
    # Chỉ fixture giả có đáp án tất định; chưa áp ngưỡng cho nguồn thật.
    if gia:
        assert do["dung"] == 9 and do["sai"] == 0


def test_ca_5_abbyy_tat_tu_chuyen_co_ly_do(bo_demo, hot_folder):
    vao, _, _ = hot_folder
    cau_hinh_abbyy(bat=False)
    with TesseractGia() as gia:
        _, kq = gui(bo_demo.anh_jpeg)
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert data["nguon_doc"] == "tesseract"
    assert "đang tắt" in data["ly_do_chuyen_nguon"]
    assert gia.lenh and SoHanMuc().da_dung() == 0 and not list(vao.iterdir())


@pytest.mark.parametrize("ten,ma", [("tep_qua_co", "VUOT_GIOI_HAN"), ("pdf_61_trang", "QUA_SO_TRANG"), ("tep_hong", "TEP_HONG")])
def test_ca_7_tep_loi_khong_tru_han_muc(bo_demo, hot_folder, ten, ma):
    vao, _, tam = hot_folder
    core, kq = gui(getattr(bo_demo, ten))
    kiem_loi(core, kq, ma)
    assert not list(vao.iterdir()) and not tam
    assert SoHanMuc().da_dung() == 0
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC) is None
    assert str(bo_demo.thu_muc) not in kq["loi"]["thong_diep"]


def test_ca_7_huy_dang_cho_khong_tru_han_muc(bo_demo, hot_folder, capsys):
    vao, ra, _ = hot_folder
    core = CoreGia()
    ref = core.them_tep(bo_demo.pdf_quet.name, bo_demo.pdf_quet.read_bytes(), "application/pdf")
    ma = core.giao_viec(DOC, {"loai": "tep", "tep": ref})
    with ABBYYGia(vao, ra, b"", nhan=False) as gia:
        luong = threading.Thread(target=core.chay, args=(nap_engine_tu_goi(GOI),))
        luong.start()
        try:
            assert gia.da_thay.wait(5)
            core.huy(ma)
        finally:
            luong.join(5)
        assert not luong.is_alive()
    kq = core.xem(ma)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0 and SoHanMuc().da_dung() == 0
    assert SoHanMuc().kho.doc(KHOA_HAN_MUC)["dang_giu"] == {}
    log = json.loads(capsys.readouterr().err)
    assert log["trang_thai"] == "HUY" and log["nguon_doc"] == "abbyy"
    assert log["cho_nguon_giay"] > 0


@pytest.mark.parametrize("nguon,nang_luc", [("abbyy", DOC), ("abbyy", WORD), ("tesseract", VAN_BAN), ("lop_chu_san", DOC), ("chua_ro", DOC), ("hong", WORD)])
def test_ca_9_stderr_thoi_gian_nguon_khong_noi_dung_duong_dan(bo_demo, hot_folder, capsys, nguon, nang_luc):
    vao, ra, _ = hot_folder
    tep = bo_demo.tep_hong if nguon == "hong" else bo_demo.pdf_quet
    if nguon == "lop_chu_san":
        tep = bo_demo.pdf_abbyy_gia
    if nguon == "tesseract":
        with TesseractGia():
            _, kq = gui(tep, nang_luc, nguon="chi_tesseract")
    else:
        with ABBYYGia(vao, ra, bo_demo.pdf_abbyy_gia.read_bytes(), tra=nguon != "chua_ro"):
            _, kq = gui(tep, nang_luc)
    out = capsys.readouterr()
    assert not out.out
    lines = out.err.splitlines()
    assert len(lines) == 1
    log = json.loads(lines[0])
    assert set(log) == {"su_kien", "nang_luc", "trang_thai", "nguon_doc", "cho_nguon_giay", "chay_giay", "tong_giay"}
    assert log["nang_luc"] == nang_luc and log["trang_thai"] == kq["trang_thai"]
    assert log["nguon_doc"] == {"chua_ro": "abbyy", "hong": "chua_xac_dinh"}.get(nguon, nguon)
    assert all(log[k] >= 0 for k in ("cho_nguon_giay", "chay_giay", "tong_giay"))
    assert log["chay_giay"] + log["cho_nguon_giay"] == pytest.approx(log["tong_giay"], abs=0.000002)
    if nguon in ("abbyy", "chua_ro"):
        assert log["cho_nguon_giay"] > 0
    else:
        assert log["cho_nguon_giay"] == 0
    for cam in (CONG_TY, TIEN, NGAY, tep.name, str(tep), str(vao), str(ra), "\\", "/", "tep_id"):
        assert cam not in out.err


def test_demo_du_sau_vi_du_va_nguon_gia_di_qua_tsv(capsys):
    with TesseractGia() as gia:
        ket_qua = CoreGia().chay_thu_demo(nap_engine_tu_goi(GOI), GOI)
    assert len(ket_qua) == 6 and all(k["trang_thai"] == "XONG" for k in ket_qua)
    assert sum("--list-langs" not in lenh for lenh in gia.lenh) == 12
    for vd in nap_engine_tu_goi(GOI).phieu["chay_thu_demo"]:
        assert vd["tham_so"] == {"nguon": "chi_tesseract"}
    assert len(capsys.readouterr().err.splitlines()) == 6


def test_ca_9_ngoai_le_khong_lo_noi_dung_duong_dan(bo_demo, hot_folder, monkeypatch, capsys):
    def loi(*args, **kwargs):
        raise RuntimeError(CONG_TY + TIEN + NGAY + str(bo_demo.anh_png))
    monkeypatch.setattr(tesseract, "doc_tesseract", loi)
    core, kq = gui(bo_demo.anh_png, nguon="chi_tesseract")
    assert kq["trang_thai"] == "LOI" and core.so_lan_ghi["ket_qua"] == 0
    out = capsys.readouterr()
    log = json.loads(out.err)
    assert log["nguon_doc"] == "tesseract" and log["trang_thai"] == "LOI"
    assert all(s not in out.err + out.out for s in (CONG_TY, TIEN, NGAY, str(bo_demo.anh_png)))


def test_chay_demo_thieu_tesseract_tu_dong_dung_gia(monkeypatch, capsys):
    def thieu(_):
        raise LoiNghiepVu("NGUON_DU_PHONG_CHUA_CAI", "Chưa có Tesseract DEMO.")
    monkeypatch.setattr(tesseract, "tim_tesseract", thieu)
    kq = chay_demo()
    assert len(kq) == 6 and all(k["trang_thai"] == "XONG" for k in kq)
    assert "Tesseract giả; không đo độ chính xác" in capsys.readouterr().out
