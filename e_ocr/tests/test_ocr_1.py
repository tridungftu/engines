"""OCR-1 đã kiểm bằng Core giả (CoreGia), ABBYY giả dùng luồng nền.

Chỉ tạo thư mục/tệp DEMO trong tmp_path, dùng API filesystem Python trên
cả Windows/Linux. Không đọc cấu hình máy thật hoặc chạy ABBYY/Tesseract.
"""

from contextlib import AbstractContextManager
from hashlib import sha256
import io
import json
from pathlib import Path
import threading

import pytest
from PIL import Image
import pdfplumber

from kho_tri_thuc_sdk.engine import Viec, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia, nap_engine_tu_goi

from demo.tao_pdf import CONG_TY, TIEN, NGAY, DONG_DEMO, pdf_demo
from e_ocr import abbyy, lop_chu


GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
DOC = "ocr.doc_tai_lieu@1"
VAN_BAN = "ocr.doc_van_ban@1"


class ABBYYGia(AbstractContextManager):
    """Nhận đúng tệp DEMO của test, trả PDF lớp chữ cùng mã tương quan."""

    def __init__(self, vao, ra, pdf, *, nhan=True, tra=True, tung_phan=False):
        self.vao, self.ra, self.pdf = vao, ra, pdf
        self.nhan, self.tra, self.tung_phan = nhan, tra, tung_phan
        self.da_thay = threading.Event()
        self.da_nhan = threading.Event()
        self.da_ghi_phan = threading.Event()
        self.dung = threading.Event()
        self.tieptuc = threading.Event()
        self.cac_tep, self.loi = [], []
        self.luong = threading.Thread(target=self._chay, daemon=True)

    def _chay(self):
        seen = set()
        try:
            while not self.dung.wait(0.005):
                for tep in self.vao.iterdir():
                    if tep.suffix not in (".pdf", ".png", ".jpg") or tep.name in seen:
                        continue
                    seen.add(tep.name)
                    self.da_thay.set()
                    if not self.nhan:
                        continue
                    raw = tep.read_bytes()
                    self.cac_tep.append((tep.name, raw))
                    tep.unlink()
                    self.da_nhan.set()
                    if not self.tra:
                        continue
                    ket_qua = self.ra / (tep.stem + ".pdf")
                    if self.tung_phan:
                        with ket_qua.open("wb") as f:
                            f.write(self.pdf[:len(self.pdf) // 2])
                            f.flush()
                            self.da_ghi_phan.set()
                            assert self.tieptuc.wait(3), "Test chưa cho ABBYY giả ghi phần còn lại."
                            f.write(self.pdf[len(self.pdf) // 2:])
                    else:
                        ket_qua.write_bytes(self.pdf)
        except BaseException as exc:
            self.loi.append(exc)

    def __enter__(self):
        self.luong.start()
        return self

    def __exit__(self, *args):
        self.dung.set()
        self.tieptuc.set()
        self.luong.join(3)
        assert not self.luong.is_alive(), "ABBYY giả chưa dừng."
        assert not self.loi, self.loi


@pytest.fixture
def hot_folder(tmp_path, monkeypatch):
    vao, ra = tmp_path / "nhan-DEMO", tmp_path / "tra-DEMO"
    vao.mkdir()
    ra.mkdir()
    cau_hinh = tmp_path / "cau-hinh-DEMO.json"
    cau_hinh.write_text(json.dumps({"abbyy": {
        "bat": True, "thu_muc_vao": str(vao), "thu_muc_ra": str(ra), "thoi_han_giay": 1,
    }}), encoding="utf-8")
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(cau_hinh))
    monkeypatch.setattr(abbyy, "KHOANG_CHO_GIAY", 0.01)
    cac_thu_muc_tam = []
    tao_tam = abbyy.TemporaryDirectory

    def ghi_nhan_tam(*args, **kwargs):
        tam = tao_tam(*args, **kwargs)
        cac_thu_muc_tam.append(Path(tam.name))
        return tam

    monkeypatch.setattr(abbyy, "TemporaryDirectory", ghi_nhan_tam)
    yield vao, ra, cac_thu_muc_tam
    assert all(not d.exists() for d in cac_thu_muc_tam), "Còn thư mục tạm của việc."
    assert not list(vao.iterdir()), "Còn tệp vào của việc đã kết thúc."


def chay(raw, nang_luc=DOC, *, mime="application/pdf", tham_so=None, core=None):
    core = core or CoreGia()
    tep = core.them_tep("DEMO.pdf", raw, mime)
    ket_qua = core.chay_thu(nap_engine_tu_goi(GOI), nang_luc, {"loai": "tep", "tep": tep}, tham_so)
    return core, ket_qua


def kiem_loi(core, ket_qua, ma):
    assert ket_qua["trang_thai"] == "LOI", ket_qua
    assert ket_qua["loi"]["ma"] == ma
    assert ket_qua["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0
    assert "DEMO.pdf" not in ket_qua["loi"]["thong_diep"]
    assert ":\\" not in ket_qua["loi"]["thong_diep"]


def kiem_noi_dung(data, raw, nguon):
    assert data["phien_ban"] == 1
    assert data["so_trang"] == len(data["trang"]) == 3
    assert data["nguon_doc"] == nguon
    assert data["ly_do_chuyen_nguon"] is None
    assert data["phien_ban_engine"] == "e_ocr " + nap_engine_tu_goi(GOI).phieu["phien_ban"]
    assert data["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()
    assert data["van_ban"] == "\f".join(["\n".join(DONG_DEMO)] * 3)
    assert all(isinstance(w, str) for w in data["canh_bao"])
    for so, page in enumerate(data["trang"], 1):
        assert page["so"] == so
        assert page["don_vi"] == "pt"
        assert (page["rong"], page["cao"]) == (595, 842)
        assert [b["van_ban"] for b in page["khoi"]] == list(DONG_DEMO)
        for block in page["khoi"]:
            x0, y0, x1, y1 = block["hop"]
            assert 0 <= x0 < x1 <= page["rong"] and 0 <= y0 < y1 <= page["cao"]
            line, = block["dong"]
            assert " ".join(w["van_ban"] for w in line["tu"]) == block["van_ban"]
            for word in line["tu"]:
                a, b, c, d = word["hop"]
                assert x0 <= a < c <= x1 and y0 <= b < d <= y1
    json.dumps(data, ensure_ascii=False, allow_nan=False)


@pytest.mark.parametrize("nang_luc", [DOC, VAN_BAN])
def test_abbyy_pdf_3_trang_chu_viet_tien_ngay_vi_tri(hot_folder, nang_luc, monkeypatch):
    vao, ra, cac_tam = hot_folder
    raw = pdf_demo((), (), ())
    result = pdf_demo(DONG_DEMO, DONG_DEMO, DONG_DEMO)
    mo_tep_goc, da_mo = Viec.mo_tep, []

    def mo_tep(viec, ma):
        da_mo.append(ma)
        return mo_tep_goc(viec, ma)

    monkeypatch.setattr(Viec, "mo_tep", mo_tep)
    with ABBYYGia(vao, ra, result) as gia:
        core, kq = chay(raw, nang_luc)
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == len(da_mo) == len(cac_tam) == 1
    assert gia.cac_tep[0][1] == raw
    assert len(Path(gia.cac_tep[0][0]).stem) == 32
    assert not list(ra.iterdir())
    if nang_luc == DOC:
        kiem_noi_dung(kq["ket_qua"]["van_ban_tai_lieu"], raw, "abbyy")
    else:
        assert kq["ket_qua"] == {"loai": "van_ban", "van_ban": "\f".join(["\n".join(DONG_DEMO)] * 3)}
    assert core.so_lan_ghi["ket_qua"] == 1
    assert kq["tien_do"]
    cac_moc = [phan_tram for phan_tram, _ in kq["tien_do"]]
    assert cac_moc == sorted(cac_moc)
    assert {5, 15, 25, 35, 75, 95, 100} <= set(cac_moc)
    assert CONG_TY not in json.dumps(kq["tien_do"], ensure_ascii=False)


@pytest.mark.parametrize("nang_luc", [DOC, VAN_BAN])
@pytest.mark.parametrize("nguon", ["tu_dong", "chi_abbyy", "chi_tesseract"])
def test_pdf_co_chu_khong_gui_abbyy_hoac_ocr_lai(nang_luc, nguon, monkeypatch):
    def cam(*args, **kwargs):
        raise AssertionError("PDF có chữ không được đọc cấu hình/gửi ABBYY/render ảnh.")

    monkeypatch.setattr("e_ocr.van_ban.doc_cau_hinh", cam)
    monkeypatch.setattr(abbyy.BackendABBYY, "doc_pdf", cam)
    monkeypatch.setattr(pdfplumber.page.Page, "to_image", cam)
    raw = pdf_demo(DONG_DEMO, DONG_DEMO, DONG_DEMO)
    _, kq = chay(raw, nang_luc, tham_so={"nguon": nguon})
    assert kq["trang_thai"] == "XONG", kq
    if nang_luc == DOC:
        kiem_noi_dung(kq["ket_qua"]["van_ban_tai_lieu"], raw, "lop_chu_san")
    else:
        assert kq["ket_qua"]["van_ban"] == "\f".join(["\n".join(DONG_DEMO)] * 3)


@pytest.mark.parametrize("rotate", [0, 90, 180, 270])
def test_lop_chu_trang_xoay_giu_thu_tu_va_toa_do(rotate):
    _, kq = chay(pdf_demo(DONG_DEMO, rotate=rotate))
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert data["van_ban"] == "\n".join(DONG_DEMO)
    page, = data["trang"]
    assert (page["rong"], page["cao"]) == ((842, 595) if rotate in (90, 270) else (595, 842))
    for block in page["khoi"]:
        x0, y0, x1, y1 = block["hop"]
        assert 0 <= x0 < x1 <= page["rong"] and 0 <= y0 < y1 <= page["cao"]


def test_pdf_mot_trang_thieu_chu_khong_tra_ket_qua_mot_phan(hot_folder):
    vao, ra, _ = hot_folder
    raw = pdf_demo(DONG_DEMO, (), DONG_DEMO)
    with ABBYYGia(vao, ra, pdf_demo(DONG_DEMO, DONG_DEMO, DONG_DEMO)) as gia:
        _, kq = chay(raw)
    assert kq["trang_thai"] == "XONG", kq
    assert len(gia.cac_tep) == 1
    kiem_noi_dung(kq["ket_qua"]["van_ban_tai_lieu"], raw, "abbyy")


@pytest.mark.parametrize("co_chu", [False, True])
@pytest.mark.parametrize("nang_luc", [DOC, VAN_BAN])
def test_qua_60_trang_tu_choi_truoc_hot_folder(hot_folder, co_chu, nang_luc):
    vao, _, tam = hot_folder
    raw = pdf_demo(*([DONG_DEMO if co_chu else ()] * 61))
    core, kq = chay(raw, nang_luc)
    kiem_loi(core, kq, "QUA_SO_TRANG")
    assert not list(vao.iterdir()) and not tam


def test_dung_60_trang_van_duoc_doc():
    _, kq = chay(pdf_demo(*([DONG_DEMO] * 60)))
    assert kq["trang_thai"] == "XONG", kq
    assert kq["ket_qua"]["van_ban_tai_lieu"]["so_trang"] == 60


@pytest.mark.parametrize("raw,mime", [
    (b"", "application/pdf"), (b"DEMO hong", "application/pdf"),
    (b"%PDF-1.4\nDEMO\n%%EOF\n", "application/pdf"),
    (pdf_demo(())[:-20], "application/pdf"),
    (pdf_demo(), "application/pdf"),
    (b"\x89PNG\r\n\x1a\nDEMO hong", "image/png"),
    (b"\xff\xd8\xffDEMO hong", "image/jpeg"),
    (pdf_demo(DONG_DEMO), "image/png"),
])
def test_tep_hong_khong_gui_abbyy(hot_folder, raw, mime, capsys):
    vao, _, tam = hot_folder
    core, kq = chay(raw, mime=mime)
    kiem_loi(core, kq, "TEP_HONG")
    assert not list(vao.iterdir()) and not tam
    out = capsys.readouterr()
    assert str(vao) not in out.err + out.out


def test_tep_qua_20_mib_bi_tu_choi_truoc_gui(hot_folder):
    _, _, tam = hot_folder
    core, kq = chay(b"DEMO" + b"\0" * (20 * 1024**2))
    kiem_loi(core, kq, "VUOT_GIOI_HAN")
    assert not tam


@pytest.mark.parametrize("mime,fmt", [("image/png", "PNG"), ("image/jpeg", "JPEG")])
def test_anh_duoc_kiem_va_dem_truoc_gui_abbyy(hot_folder, mime, fmt):
    vao, ra, _ = hot_folder
    f = io.BytesIO()
    with Image.new("RGB", (23, 7), "white") as anh:
        anh.save(f, format=fmt)
    with ABBYYGia(vao, ra, pdf_demo(DONG_DEMO)) as gia:
        _, kq = chay(f.getvalue(), mime=mime)
    assert kq["trang_thai"] == "XONG", kq
    data = kq["ket_qua"]["van_ban_tai_lieu"]
    assert data["nguon_doc"] == "abbyy" and data["so_trang"] == 1
    assert data["bam_dau_vao"] == "sha256:" + sha256(f.getvalue()).hexdigest()
    assert gia.cac_tep[0][0].endswith(".png" if fmt == "PNG" else ".jpg")


@pytest.mark.parametrize("tra_ve,ma", [
    (pdf_demo(DONG_DEMO), "KET_QUA_KHONG_KHOP"),
    (pdf_demo((), (), ()), "ABBYY_THIEU_LOP_CHU"),
    (b"%PDF-1.4\nDEMO hong\n%%EOF\n", "TEP_HONG"),
])
def test_ket_qua_abbyy_khong_day_du_khong_bao_xong(hot_folder, tra_ve, ma):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, tra_ve):
        core, kq = chay(pdf_demo((), (), ()))
    kiem_loi(core, kq, ma)
    assert not list(ra.iterdir())


def test_abbyy_khong_nhan_qua_han_thi_rut_tep(hot_folder):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", nhan=False):
        core, kq = chay(pdf_demo(()), tham_so={"nguon": "chi_abbyy"})
    kiem_loi(core, kq, "ABBYY_QUA_THOI_HAN")
    assert kq["loi"]["thu_lai_duoc"] is True


def test_abbyy_da_nhan_qua_han_phai_chua_ro(hot_folder):
    vao, ra, _ = hot_folder
    with ABBYYGia(vao, ra, b"", tra=False) as gia:
        core, kq = chay(pdf_demo(()))
    assert kq["trang_thai"] == "CHUA_RO", kq
    assert kq["ma_tuong_quan"] == Path(gia.cac_tep[0][0]).stem
    assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("da_nhan", [False, True])
def test_huy_viec_dang_cho_va_don_tep_tam(hot_folder, da_nhan):
    vao, ra, cac_tam = hot_folder
    core = CoreGia()
    tep = core.them_tep("DEMO.pdf", pdf_demo(()), "application/pdf")
    ma = core.giao_viec(DOC, {"loai": "tep", "tep": tep})
    with ABBYYGia(vao, ra, b"", nhan=da_nhan, tra=False) as gia:
        luong = threading.Thread(target=core.chay, args=(nap_engine_tu_goi(GOI),))
        luong.start()
        try:
            assert (gia.da_nhan if da_nhan else gia.da_thay).wait(3)
            core.huy(ma)
        finally:
            luong.join(3)
        assert not luong.is_alive(), "Hủy phải kết thúc vòng chờ ABBYY."
    kq = core.xem(ma)
    assert kq["trang_thai"] == "HUY", kq
    assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == 0
    assert len(cac_tam) == 1
    from e_ocr.chon_nguon import SoHanMuc
    assert SoHanMuc().da_dung() == (1 if da_nhan else 0)


def test_khong_doc_pdf_abbyy_dang_ghi_do_va_khong_lay_nham_ma(hot_folder):
    vao, ra, _ = hot_folder
    khac = ra / "DEMO-ma-khac.pdf"
    khac.write_bytes(pdf_demo(("DEMO KHONG PHAI VIEC NAY",)))
    core = CoreGia()
    tep = core.them_tep("DEMO.pdf", pdf_demo(()), "application/pdf")
    ma = core.giao_viec(DOC, {"loai": "tep", "tep": tep})
    with ABBYYGia(vao, ra, pdf_demo(DONG_DEMO), tung_phan=True) as gia:
        luong = threading.Thread(target=core.chay, args=(nap_engine_tu_goi(GOI),))
        luong.start()
        try:
            assert gia.da_ghi_phan.wait(3)
            # Vẫn đứng yên qua nhiều chu kỳ poll, chưa có EOF nên không đọc thiếu.
            assert not threading.Event().wait(0.08)
            assert core.xem(ma)["trang_thai"] == "DANG_CHAY"
            assert core.so_lan_ghi["ket_qua"] == 0
        finally:
            gia.tieptuc.set()
            luong.join(3)
        assert not luong.is_alive()
    kq = core.xem(ma)
    assert kq["trang_thai"] == "XONG", kq
    assert kq["ket_qua"]["van_ban_tai_lieu"]["van_ban"] == "\n".join(DONG_DEMO)
    assert list(ra.iterdir()) == [khac]


def test_loi_gui_don_dem_va_khong_lo_duong_dan(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    thay_goc = abbyy.os.replace

    def loi(nguon, dich):
        if Path(dich).parent == vao:
            raise OSError(f"DEMO duong dan khong duoc lo: {vao}")
        return thay_goc(nguon, dich)

    monkeypatch.setattr(abbyy.os, "replace", loi)
    core, kq = chay(pdf_demo(()), tham_so={"nguon": "chi_abbyy"})
    kiem_loi(core, kq, "ABBYY_KHONG_TRUY_CAP_DUOC")
    assert str(vao) not in json.dumps(kq, ensure_ascii=False)
    assert not list(ra.iterdir())


def test_loi_don_ket_qua_khong_bao_thanh_cong_gia(hot_folder, monkeypatch):
    vao, ra, _ = hot_folder
    unlink_goc = Path.unlink

    def khong_xoa_ket_qua(tep, *args, **kwargs):
        if tep.parent == ra:
            raise PermissionError(f"DEMO loi quyen tai {ra}")
        return unlink_goc(tep, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", khong_xoa_ket_qua)
    with ABBYYGia(vao, ra, pdf_demo(DONG_DEMO)):
        core, kq = chay(pdf_demo(()))
    kiem_loi(core, kq, "KHONG_DON_DUOC_TEP_TAM")
    assert str(ra) not in json.dumps(kq, ensure_ascii=False)
    assert len(list(ra.iterdir())) == 1


def test_chi_abbyy_thieu_cau_hinh_khong_gui():
    core, kq = chay(pdf_demo(()), tham_so={"nguon": "chi_abbyy"})
    kiem_loi(core, kq, "CHUA_CAU_HINH")


def test_bang_pdf_giu_o_rong_va_o_gop_tu_duong_ke():
    _, kq = chay(pdf_demo(DONG_DEMO, bang=True))
    assert kq["trang_thai"] == "XONG", kq
    page, = kq["ket_qua"]["van_ban_tai_lieu"]["trang"]
    bang, = [k for k in page["khoi"] if k["loai"] == "bang"]
    assert bang["hop"] == [50, 192, 450, 282]
    assert len(bang["o"]) == 7
    o_gop = bang["o"][0]
    assert (o_gop["hang"], o_gop["cot"], o_gop["gop_hang"], o_gop["gop_cot"]) == (0, 0, 1, 3)
    assert o_gop["van_ban"] == "BANG DEMO"
    assert [(o["hang"], o["cot"]) for o in bang["o"] if o["van_ban"] == ""] == [(1, 2), (2, 2)]
    assert {TIEN, NGAY} <= {o["van_ban"] for o in bang["o"]}


def test_huy_trong_luc_doc_pdf_khong_doi_thanh_tep_hong():
    dem = 0

    def huy():
        nonlocal dem
        dem += 1
        if dem == 3:
            raise ViecDaHuy()

    with pytest.raises(ViecDaHuy):
        lop_chu.doc_lop_chu(pdf_demo(DONG_DEMO, DONG_DEMO), kiem_huy=huy)
