"""PL-2 tích hợp: đã kiểm bằng Core giả (CoreGia), dữ liệu DEMO trong RAM."""
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, Viec
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau, co, phan_luong, ty_le
from e_phan_luong.chay import app
from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.kieu import CHON_MAU, KHONG_CHON, NOP_LAI, THU_TU_CO, Tien
from e_phan_luong.loi import CAU_LOI
from e_phan_luong.ngan_chung import ghi_lay_hoac_tao_nhieu
from e_phan_luong.xuat_json import canh_bao
from test_pl2_ngan_luot import chay_ngan

DEMO = Path(__file__).resolve().parent / "demo"
HG = bytes(range(32))
KHAU = "ktt_duyet"


def tham_so(**ghi_de):
    return {
        "khau": KHAU, "truong_phan_loai": "dien_giai",
        "danh_muc_loai_json": (DEMO / "danh-muc-loai-DEMO.json").read_text(encoding="utf-8"),
        "bo_phan_loai_json": (DEMO / "bo-phan-loai-DEMO.json").read_text(encoding="utf-8"),
        **ghi_de,
    }


def lo_mot(**doi_dong):
    lo = json.loads((DEMO / "lo-500-DEMO.json").read_text(encoding="utf-8"))
    lo["nghiep_vu"] = [{
        "ma": "PC-DEMO-001", "loai": "chi_phi_khac", "ngay": "2026-11-16",
        "so_tien": {"so": "300000001", "tien_te": "VND"}, "doi_tac": None,
        "dien_giai": "Nội dung DEMO chỉ dùng trong RAM", "nhap_tay": False,
        "co_do_cung": False, **doi_dong,
    }]
    return lo


def chay(core, lo, ts=None, *, ten="lo-DEMO.json", mime="application/json"):
    raw = lo if isinstance(lo, bytes) else json.dumps(lo, ensure_ascii=False).encode("utf-8")
    tep = core.them_tep(ten, raw, mime)
    return core.chay_thu(app, "audit.phan_luong@1", {"loai": "tep", "tep": tep},
                         tham_so() if ts is None else ts)


def lay_kq(core, ket_qua):
    assert ket_qua["trang_thai"] == "XONG", ket_qua
    truong = ket_qua["ket_qua"]["truong"]
    raw = core.doc_tep(truong["tep_json"]["tep_id"])
    return truong, json.loads(raw), raw


@pytest.fixture(autouse=True)
def ghim_hat_giong(monkeypatch):
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: HG)


def test_500_demo_khop_lop1_loai_chon_bam_doc_lap_va_du_truong_ra():
    core = CoreGia()
    raw = (DEMO / "lo-500-DEMO.json").read_bytes()
    truong, tep, _ = lay_kq(core, chay(core, raw))
    dap_an = json.loads((DEMO / "dap-an-lop1.json").read_text(encoding="utf-8"))["theo_ma"]
    lo = doc_lo_json(raw)
    assert [d["ma"] for d in tep["nghiep_vu"]] == [nv.ma for nv in lo.nghiep_vu]
    assert len(tep["nghiep_vu"]) == truong["so_nghiep_vu"] == 500
    for d, nv in zip(tep["nghiep_vu"], lo.nghiep_vu):
        mong = dap_an[d["ma"]]
        assert (d["loai"], d["nguon_loai"]) == (mong["loai"], mong["nguon_loai"])
        assert "SO_TIEN_BAT_THUONG" not in d["co"]  # hồ sơ trống: chưa đủ 50 nghiệp vụ
        # PL-4: mặc định (toi_thieu_ho_so_doi_tac_moi = 0) lượt đầu coi mọi đối tác là mới.
        assert ("DOI_TAC_MOI" in d["co"]) == (nv.doi_tac is not None)
        if mong["ly_do"]:
            assert d["luong"] == "do" and d["ly_do"] == mong["ly_do"]
        else:
            # Tính độc lập bằng Fraction và công thức SHA-256 của hợp đồng.
            tien = nv.so_tien_quy_doi or nv.so_tien
            p = Fraction(2, 100) if abs(tien.so) < 250000000 else Fraction(30, 100)
            for ma in d["co"]:
                p *= Fraction(2) if ma in THU_TU_CO[:2] else Fraction(3, 2)
            p = min(Fraction(1), p)
            h = int.from_bytes(sha256(b"\x1f".join((HG, lo.ma_module.encode(), KHAU.encode(), nv.ma.encode()))).digest(), "big")
            chon = Fraction(h, 1 << 256) < p
            assert (d["luong"], d["ly_do"]) == (("do", [CHON_MAU]) if chon else ("xanh", [KHONG_CHON]))
    nl = next(n for n in app.phieu["nang_luc"] if n["ma"] == "audit.phan_luong@1")
    assert set(truong) == {t["ma"] for t in nl["truong_ra"]}
    assert truong["so_do"] + truong["so_xanh"] == 500
    assert truong["so_do_bat_buoc"] + truong["so_do_chon_mau"] == truong["so_do"]
    assert truong["so_chua_phan_loai"] == sum(d["loai"] == "chua_phan_loai" for d in tep["nghiep_vu"])
    assert truong["luong"] == "do" and truong["can_nguoi_kiem"] is True
    assert truong["tong_tien_do"] is None  # Có ngoại tệ chưa quy đổi/thiếu tiền tệ.
    # PL-8: có dòng Đỏ thì có tệp Excel danh sách cần kiểm.
    assert truong["tep_ds_do"]["ten"] == "ds-can-kiem.xlsx"
    assert core.xem_ngan(app.ma, "ty_le") == []
    assert len(core.xem_ngan(app.ma, "dong_luot")) == 500
    assert len(core.xem_ngan(app.ma, "luot")) == 1


def test_cung_hat_giong_dau_vao_va_trang_thai_ngan_cung_tep_tung_byte():
    ds = []
    for _ in range(2):
        core = CoreGia()
        ds.append(lay_kq(core, chay(core, (DEMO / "lo-500-DEMO.json").read_bytes())))
    assert ds[0] == ds[1]
    assert ds[0][2].endswith(b"\n") and b"\r\n" not in ds[0][2]


def test_c4_xem_ngan_moi_bang_khong_co_chi_tiet_giao_dich():
    core = CoreGia()
    raw = (DEMO / "lo-500-DEMO.json").read_bytes()
    lay_kq(core, chay(core, raw))
    lo = json.loads(raw)
    nguyen_van_cam = set()
    for nv in lo["nghiep_vu"]:
        nguyen_van_cam.update(v for v in (nv.get("doi_tac"), nv.get("dien_giai"), nv["ngay"], nv["so_tien"]["so"]) if v)
    he_thong = {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
    for bang in app.phieu["ngan_du_lieu"]:
        ds = core.xem_ngan(app.ma, bang["bang"])
        cho_phep = {t["ma"] for t in bang["truong"]} | he_thong
        for dong in ds:
            assert set(dong) <= cho_phep
            assert not set(dong) & {"so_tien", "ngay", "doi_tac", "dien_giai", "noi_dung", "tai_khoan_no", "tai_khoan_co", "thuoc_tinh"}
            assert not nguyen_van_cam & {v for v in dong.values() if isinstance(v, str)}


def test_c5_truong_ra_va_tep_json_chi_danh_sach_cot_cong_bo():
    core = CoreGia()
    truong, tep, raw = lay_kq(core, chay(core, (DEMO / "lo-500-DEMO.json").read_bytes()))
    assert set(tep) == {"phien_ban", "ma_luot", "bam_hat_giong", "bam_dau_vao", "phien_ban_engine", "khau", "ma_module", "nghiep_vu"}
    assert all(set(d) == {"ma", "luong", "ly_do", "co", "loai", "nguon_loai"} for d in tep["nghiep_vu"])
    for nut in [truong, tep, *tep["nghiep_vu"]]:
        assert not any("ty_le" in k or "xac_suat" in k or "bac" in k or k in {"p", "he_so", "san", "hat_giong"} for k in nut)
    assert HG.hex().encode() not in raw
    assert len(truong["canh_bao"]) <= 500
    assert not any(chu in truong["canh_bao"] for chu in ("%", "xác suất", "tỷ lệ", "bậc"))
    # Cảnh báo là tập câu lý do cố định: mã nghiệp vụ/nội dung không đi vào câu.
    assert "PC-DEMO" not in truong["canh_bao"]
    assert canh_bao(tuple()) == ""


def test_hat_giong_luu_hex_va_kiem_lai_bang_bytes_fromhex():
    core = CoreGia()
    _, tep, _ = lay_kq(core, chay(core, lo_mot()))
    luot, = core.xem_ngan(app.ma, "luot")
    assert len(luot["hat_giong"]) == 64
    hg = bytes.fromhex(luot["hat_giong"])
    assert hg == HG
    assert chon_mau.bam_hat_giong(hg) == tep["bam_hat_giong"]
    d, = tep["nghiep_vu"]
    assert chon_mau.duoc_chon(hg, tep["ma_module"], tep["khau"], d["ma"], Decimal("0.30")) == (d["luong"] == "do")


@pytest.mark.parametrize("kiem", ["dat", "sai", "khong_kiem"])
def test_nop_lai_toan_luong_roi_kiem_xet_lai_hat_giong_moi(monkeypatch, kiem):
    core = CoreGia()
    dem = iter(bytes([i]) * 32 for i in range(1, 8))
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: next(dem))
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: False)
    t1, tep1, _ = lay_kq(core, chay(core, lo_mot(co_do_cung=True)))
    t2, tep2, _ = lay_kq(core, chay(core, lo_mot()))
    assert tep1["nghiep_vu"][0]["ly_do"] == ["CO_DO_CUNG"]
    assert tep2["nghiep_vu"][0]["ly_do"] == [NOP_LAI]
    assert t2["so_do_bat_buoc"] == 1 and t2["so_do_chon_mau"] == 0
    assert t1["bam_hat_giong"] != t2["bam_hat_giong"]

    def ghi(viec):
        ghi_lay_hoac_tao_nhieu(viec, "ket_qua_kiem", [(
            {"ma_luot": t2["ma_luot"], "ma": "PC-DEMO-001", "khau": KHAU},
            {"ma_module": "demo_thanh_toan", "loai": "chi_phi_khac", "ket_qua": kiem})])

    assert chay_ngan(core, ghi)["trang_thai"] == "XONG"
    t3, tep3, _ = lay_kq(core, chay(core, lo_mot()))
    assert tep3["nghiep_vu"][0]["ly_do"] == ([NOP_LAI] if kiem == "khong_kiem" else [KHONG_CHON])
    assert t3["bam_hat_giong"] not in {t1["bam_hat_giong"], t2["bam_hat_giong"]}


def test_lan_truoc_xanh_lan_sau_chon_binh_thuong(monkeypatch):
    core = CoreGia()
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: False)
    _, kq1, _ = lay_kq(core, chay(core, lo_mot()))
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: bytes(reversed(HG)))
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: True)
    _, kq2, _ = lay_kq(core, chay(core, lo_mot()))
    assert kq1["nghiep_vu"][0]["ly_do"] == [KHONG_CHON]
    assert kq2["nghiep_vu"][0]["ly_do"] == [CHON_MAU]


@pytest.mark.parametrize("bac,che_do,chua_loai,p_mong", [
    ("0.20", "bac", False, "0.20"), ("0.05", "bac", False, "0.05"),
    ("0.05", "toan_bo", False, "1"), ("0.05", "bac", True, "0.30"),
])
def test_doc_p_bac_ngan_hieu_luc_ngay(monkeypatch, bac, che_do, chua_loai, p_mong):
    core = CoreGia()
    loai = "chua_phan_loai" if chua_loai else "chi_phi_khac"
    tt = replace(ty_le.moi(KHAU, loai, ty_le.ChinhSach()), bac=Decimal(bac), che_do=che_do)
    assert chay_ngan(core, lambda v: ghi_lay_hoac_tao_nhieu(v, "ty_le", [(
        {"khau": KHAU, "loai": loai}, ty_le.ve_ban_ghi(tt))]))["trang_thai"] == "XONG"
    cac_p = []
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: cac_p.append(a[-1]) or False)
    lay_kq(core, chay(core, lo_mot(loai=None if chua_loai else loai)))
    assert cac_p == [Decimal(p_mong)]


def test_q4_duoi_sad_nhan_he_so_khong_kep_san_va_tien_am_da_tuyet_doi(monkeypatch):
    core = CoreGia()
    cac_co, cac_p, bam_chia_nho = [], [], []
    tinh_co_goc, tim_chia_nho_goc = co.tinh_co, phan_luong.tim_chia_nho

    def tinh_co(nv, tien_ss, ho_so, bam_dt, cs):
        cac_co.append((tien_ss, ho_so, bam_dt))
        return tinh_co_goc(nv, tien_ss, ho_so, bam_dt, cs)

    def tim_chia_nho(*args, **kw):
        bam_chia_nho.append(kw["bam"]("DEMO-NCC-01"))
        return tim_chia_nho_goc(*args, **kw)

    monkeypatch.setattr(co, "tinh_co", tinh_co)
    monkeypatch.setattr(phan_luong, "tim_chia_nho", tim_chia_nho)
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *a: cac_p.append(a[-1]) or False)
    _, tep, _ = lay_kq(core, chay(core, lo_mot(
        so_tien={"so": "-10000000", "tien_te": "VND"}, nhap_tay=True, doi_tac="DEMO-NCC-01"),
        tham_so(chinh_sach_json='{"san":0.9,"toi_thieu_ho_so_doi_tac_moi":1}')))
    # Khóa PL-4 = 1 với hồ sơ trống → không bật DOI_TAC_MOI; còn SO_TRON × NHAP_TAY.
    assert cac_p == [Decimal("0.045")]
    assert [(t, b) for t, _, b in cac_co] == [(Tien(Decimal("10000000"), "VND"), bam_chia_nho[0])]
    assert cac_co[0][1].so_nghiep_vu == 0  # PL-4: ảnh chụp hồ sơ rỗng, không phải None
    assert bam_chia_nho == [phan_luong.bam_doi_tac("demo_thanh_toan", "DEMO-NCC-01")]
    assert tep["nghiep_vu"][0]["co"] == ["SO_TRON", "NHAP_TAY"]


@pytest.mark.parametrize("ten,mime,raw,ma_loi", [
    # PL-6: Excel/CSV đã được nhận; tệp hỏng hoặc thiếu khuôn cột bị từ chối đúng mã.
    ("lo-DEMO.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b"PK-DEMO",
     "TEP_KHONG_HO_TRO"),
    ("lo-DEMO.csv", "text/csv", b"ma,so_tien\nPC-DEMO,1000000", "THAM_SO_KHONG_HOP_LE"),
    ("lo-DEMO.json", "application/json", b"khong phai JSON DEMO", "TEP_KHONG_HO_TRO"),
    # SDK chặn mime không khai trước khi tới engine.
    ("lo-DEMO.pdf", "application/pdf", b"%PDF-DEMO", "LOAI_TEP_KHONG_NHAN"),
])
def test_tep_chua_ho_tro_tu_choi_khong_ghi_ngan(ten, mime, raw, ma_loi):
    core = CoreGia()
    kq = chay(core, raw, ten=ten, mime=mime)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == ma_loi
    if ma_loi in CAU_LOI:
        assert kq["loi"]["thong_diep"] == CAU_LOI[ma_loi]
    assert all(core.xem_ngan(app.ma, b["bang"]) == [] for b in app.phieu["ngan_du_lieu"])


@pytest.mark.parametrize("khau", ["kt\x1fkiem", "kt-kiem", "KT_KIEM"])
def test_khau_sai_dang_tu_choi_truoc_khi_ghi(khau):
    core = CoreGia()
    kq = chay(core, lo_mot(), tham_so(khau=khau))
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "THAM_SO_KHONG_HOP_LE"
    assert core.xem_ngan(app.ma, "luot") == []


def test_upload_loi_khong_ghi_dau_hoan_tat(monkeypatch):
    def hong(*a, **kw):
        raise LoiNghiepVu("DEMO", "Lỗi tải tệp DEMO.")

    monkeypatch.setattr(Viec, "tai_tep_ra", hong)
    core = CoreGia()
    kq = chay(core, lo_mot())
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "DEMO"
    assert core.xem_ngan(app.ma, "dong_luot") == core.xem_ngan(app.ma, "luot") == []


def test_ghi_luot_la_thao_tac_ngan_sau_cung_va_tep_da_tai(monkeypatch):
    core = CoreGia()
    cac_lo = []
    ghi_goc = core._ngan_ghi_lo

    def ghi(ma, instance, lenh, khoa, **kw):
        cac_lo.append([c["bang"] for c in lenh])
        # SDK đã tải tệp trước lô đầu tiên; kiểm qua nhật ký công khai của CoreGia.
        assert any(d[0] == "tep" for d in core.nhat_ky)
        return ghi_goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    lay_kq(core, chay(core, lo_mot()))
    # PL-4: hồ sơ rỗng tạo trước; hồ sơ cộng CÙNG lô nguyên tử với dấu luot (luot sau cùng).
    assert cac_lo == [["ho_so_hanh_vi"], ["dong_luot"], ["ho_so_hanh_vi", "luot"]]


def test_lo_rong_tra_du_truong_dem_khong_va_tong_co_tien_te():
    core = CoreGia()
    lo = lo_mot()
    lo["nghiep_vu"] = []
    truong, tep, _ = lay_kq(core, chay(core, lo))
    assert tep["nghiep_vu"] == []
    assert truong["luong"] == "xanh" and truong["can_nguoi_kiem"] is False
    assert truong["so_nghiep_vu"] == truong["so_do"] == truong["so_xanh"] == 0
    assert truong["tong_tien_do"] == {"so": "0", "tien_te": "VND"}


def test_tong_tien_do_quy_doi_va_so_am_khong_bu_tru():
    core = CoreGia()
    lo = lo_mot()
    lo["nghiep_vu"] = [
        {**lo["nghiep_vu"][0], "ma": "PC-DEMO-QUY-DOI", "so_tien": {"so": "100", "tien_te": "USD"},
         "so_tien_quy_doi": {"so": "-3200000000.123456", "tien_te": "VND"}},
        {**lo["nghiep_vu"][0], "ma": "PC-DEMO-AM", "so_tien": {"so": "-5100000000.000001", "tien_te": "VND"}},
    ]
    truong, tep, _ = lay_kq(core, chay(core, lo))
    assert truong["tong_tien_do"] == {"so": "8300000000.123457", "tien_te": "VND"}
    assert truong["so_do_bat_buoc"] == 2
    assert [d["ly_do"] for d in tep["nghiep_vu"]] == [["VUOT_TE"], ["VUOT_PM"]]
