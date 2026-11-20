"""PL-6: đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO."""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from demo.sinh_bang_demo import hang_demo, khuon_demo, lo_json_demo, sinh_csv, sinh_xlsx
from e_phan_luong import chon_mau, doc_bang, quy_trinh
from e_phan_luong.chay import app
from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.loi import CAU_LOI

DEMO = Path(__file__).resolve().parent / "demo"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
HAT_GIONG = bytes(range(32))


def tham_so(**ghi_de):
    return {
        "khau": "ktt_duyet", "ma_module": "demo_thanh_toan",
        "nguong_json": (DEMO / "nguong-DEMO.json").read_text(encoding="utf-8"),
        "khuon_cot_json": json.dumps(khuon_demo(), ensure_ascii=False),
        **ghi_de,
    }


def chay(raw, kieu, ts=None):
    core = CoreGia()
    mime = {"xlsx": MIME_XLSX, "csv": "text/csv", "json": "application/json",
            "xls": "application/vnd.ms-excel"}[kieu]
    tep = core.them_tep("lo-DEMO." + kieu, raw, mime)
    kq = core.chay_thu(app, "audit.phan_luong@1", {"loai": "tep", "tep": tep},
                       tham_so() if ts is None else ts)
    return core, kq


def ket_qua(core, kq):
    assert kq["trang_thai"] == "XONG", kq
    truong = kq["ket_qua"]["truong"]
    return truong, json.loads(core.doc_tep(truong["tep_json"]["tep_id"]))["nghiep_vu"]


def kiem_loi(core, kq, ma):
    assert kq["trang_thai"] == "LOI", kq
    assert kq["loi"]["ma"] == ma
    assert kq["loi"]["thong_diep"] == CAU_LOI[ma]
    assert core.xem_ngan(app.ma, "luot") == []
    assert core.xem_ngan(app.ma, "dong_luot") == []


@pytest.fixture(autouse=True)
def ghim_hat_giong(monkeypatch):
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HAT_GIONG)


@pytest.mark.parametrize("dau,bom", [(",", False), (";", False), (",", True), (";", True)])
def test_json_excel_csv_cung_danh_sach_luong(dau, bom):
    # Thêm nhiều dòng ở vùng chọn mẫu để kiểm cả Đỏ và Xanh với hạt giống cố định.
    lo = json.loads(lo_json_demo())
    hang = hang_demo()[:5]
    for i in range(3, 63):
        ma, so = f"PC-DEMO-{i:04d}", str(300000000 + i)
        lo["nghiep_vu"].append({"ma": ma, "ngay": "2026-11-16",
                                "so_tien": {"so": so, "tien_te": "VND"}})
        hang.append([ma, "2026-11-16", so, "VND"])
    cac_tep = [(json.dumps(lo).encode(), "json"),
               (sinh_xlsx(hang, cong_thuc=False), "xlsx"),
               (sinh_csv(hang, dau=dau, bom=bom), "csv")]
    ds = []
    for raw, kieu in cac_tep:
        truong, dong = ket_qua(*chay(raw, kieu))
        assert truong["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()
        assert truong["bam_hat_giong"] == chon_mau.bam_hat_giong(HAT_GIONG)
        ds.append(dong)
    assert ds[0] == ds[1] == ds[2]
    assert {d["luong"] for d in ds[0][2:]} == {"do", "xanh"}


@pytest.mark.parametrize("kieu", ["xlsx", "csv"])
@pytest.mark.parametrize("tien_te", [None, "", "EUR"])
def test_thieu_cot_tien_te_khong_tu_gan_vnd(kieu, tien_te):
    hang = [["Mã", "Ngày", "Số tiền"], ["PC-DEMO-0001", "2026-11-16", "1000000"]]
    raw = sinh_xlsx(hang, cong_thuc=False) if kieu == "xlsx" else sinh_csv(hang)
    truong, ds = ket_qua(*chay(raw, kieu, tham_so(tien_te=tien_te)))
    assert ds[0]["luong"] == "do"
    assert ds[0]["ly_do"] == (["CHUA_QUY_DOI"] if tien_te else ["CHUA_RO_TIEN_TE"])
    assert truong["tong_tien_do"] is None


@pytest.mark.parametrize("kieu", ["xlsx", "csv"])
def test_tien_te_cai_dat_chi_dung_khi_khong_co_cot(kieu):
    hang = [["Mã", "Ngày", "Số tiền"], ["PC-DEMO-0001", "2026-11-16", "3000000000"]]
    raw = sinh_xlsx(hang, cong_thuc=False) if kieu == "xlsx" else sinh_csv(hang)
    truong, ds = ket_qua(*chay(raw, kieu, tham_so(tien_te="VND")))
    assert ds[0]["ly_do"] == ["VUOT_TE"]
    assert truong["tong_tien_do"] == {"so": "3000000000", "tien_te": "VND"}


@pytest.mark.parametrize("kieu,raw", [("xlsx", sinh_xlsx()), ("csv", sinh_csv())])
@pytest.mark.parametrize("ma,gia_tri", [("khuon_cot_json", None), ("khuon_cot_json", ""),
                                       ("khuon_cot_json", "   "), ("ma_module", None),
                                       ("ma_module", ""), ("ma_module", "   ")])
def test_thieu_khuon_hoac_module(kieu, raw, ma, gia_tri):
    ts = tham_so(**{ma: gia_tri})
    if gia_tri is None:
        ts.pop(ma)
    kiem_loi(*chay(raw, kieu, ts), "THAM_SO_KHONG_HOP_LE")


@pytest.mark.parametrize("kieu,raw", [("xlsx", sinh_xlsx()), ("csv", sinh_csv())])
def test_thieu_nguong_do_doc_cai_dat_bao(kieu, raw):
    ts = tham_so()
    ts.pop("nguong_json")
    kiem_loi(*chay(raw, kieu, ts), "THIEU_NGUONG")


@pytest.mark.parametrize("raw", [doc_bang.OLE + b"DEMO", b"DEMO", lo_json_demo(), sinh_csv(), sinh_xlsx()])
def test_xls_luon_tu_choi(raw):
    kiem_loi(*chay(raw, "xls"), "TEP_KHONG_HO_TRO")


def test_json_khong_can_khuon_module_va_nguong_trong_tep_thang():
    lo = json.loads(lo_json_demo())
    lo["nguong"] = json.loads(tham_so()["nguong_json"])
    truong, ds = ket_qua(*chay(json.dumps(lo).encode(), "json", {
        "khau": "ktt_duyet", "nguong_json": "khong dung DEMO",
    }))
    assert truong["so_nghiep_vu"] == len(ds) == 2


@pytest.mark.parametrize("kieu,raw", [("json", lo_json_demo()), ("xlsx", sinh_xlsx()), ("csv", sinh_csv())])
def test_doc_tep_lo_giu_nguyen_bytes_va_chuyen_cai_dat(kieu, raw):
    viec = SimpleNamespace(dau_vao={"tep": {"tep_id": "tep-DEMO", "ten": "DEMO." + kieu}},
                           tham_so=tham_so(ky="2026-11"), mo_tep=lambda _: BytesIO(raw))
    lo, goc = quy_trinh.doc_tep_lo(viec)
    assert goc == raw
    assert lo == doc_lo_json(lo_json_demo())


def test_doc_tep_lo_chan_tran_khong_cat_ngam(monkeypatch):
    # Tệp lớn hơn trần dù nội dung chỉ là JSON hợp lệ theo sau bởi khoảng trắng.
    raw = lo_json_demo() + b" " * 100
    monkeypatch.setattr(doc_bang, "TOI_DA_BYTE", len(raw) - 1)
    viec = SimpleNamespace(dau_vao={"tep": {"tep_id": "tep-DEMO", "ten": "DEMO.json"}},
                           tham_so=tham_so(), mo_tep=lambda _: BytesIO(raw))
    with pytest.raises(LoiNghiepVu) as bat:
        quy_trinh.doc_tep_lo(viec)
    assert bat.value.ma == "VUOT_GIOI_HAN"


def test_phieu_mime_va_demo_excel_tai_hien_tu_script():
    phieu = deepcopy(app.phieu)
    for nl in phieu["nang_luc"]:
        if nl["ma"] in {"audit.phan_luong@1", "audit.chuan_bi_phan_loai@1"}:
            # MIME cũ đi tới bộ đọc để .xls nhận đúng lỗi TEP_KHONG_HO_TRO.
            assert set(nl["gioi_han"]["mime"]) == {
                "application/json", MIME_XLSX, "text/csv", "application/vnd.ms-excel"}
        else:
            assert "mime" not in nl["gioi_han"]
    vd, = [v for v in phieu["chay_thu_demo"] if v["dau_vao"].get("tep_demo", "").endswith(".xlsx")]
    raw = BytesIO(sinh_xlsx())
    with ZipFile(raw, "a") as goi:
        goi.comment = b"DEMO - Cong ty DEMO Anh Duong"
    assert (app.thu_muc_goi / vd["dau_vao"]["tep_demo"]).read_bytes() == raw.getvalue()
    ds = CoreGia().chay_thu_demo(app)
    # Nhánh sau có thể thêm ví dụ của năng lực khác; PL-6 chỉ khẳng định đủ 2 ví dụ phân luồng.
    assert len(ds) == len(phieu["chay_thu_demo"])
    assert sum(v["nang_luc"] == "audit.phan_luong@1" for v in phieu["chay_thu_demo"]) == 2
    assert all(k["trang_thai"] == "XONG" for k in ds), ds
