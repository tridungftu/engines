"""MASK-2: nguồn whitelist và kiểm âm tính; mọi từ vựng đều là DEMO."""
from hashlib import sha256
from pathlib import Path
import sys
import unicodedata

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi/e_mask"))
from e_mask import che_van_ban as xu_ly, tai_nguyen
from e_mask.nguon.privacy import core, detectors, leftovers
from ho_tro_kho_demo import KhoBoNho

TU_VUNG_DEMO = {
    "vn_surnames.txt": ("Nguyễn *", "Trần *"),
    "vn_places.txt": ("Địa Danh DEMO",),
    "common_acronyms.txt": ("DEMO VND USD VAT GTGT",),
    "leftover_allowlist.txt": ("words: demo nội dung thanh toán ngày giá trị vnd usd",),
}
TEN = "Công ty DEMO Ánh Dương"


@pytest.fixture(autouse=True)
def don_cache(monkeypatch):
    monkeypatch.setattr(tai_nguyen, "_du_lieu", {})
    tai_nguyen.xoa_cache()
    yield
    tai_nguyen.xoa_cache()


@pytest.fixture
def demo_tu_vung(monkeypatch):
    def doc(ten):
        return TU_VUNG_DEMO[ten]
    monkeypatch.setattr(tai_nguyen, "doc_dong", doc)


def cau_hinh_demo(tmp_path):
    ket_qua = {}
    for ten, dong in TU_VUNG_DEMO.items():
        tep = tmp_path / ten
        du_lieu = ("# DEMO\n" + "\n".join(dong)).encode("utf-8")
        tep.write_bytes(du_lieu)
        ket_qua[ten] = {"duong_dan": str(tep), "sha256": sha256(du_lieu).hexdigest()}
    return {"tai_nguyen": ket_qua}


def test_mac_dinh_khong_co_nguon_khong_dung_tu_dien_demo():
    kho = KhoBoNho()
    with pytest.raises(tai_nguyen.ThieuTaiNguyen) as loi:
        xu_ly.che("nội dung", [], kho)
    assert loi.value.ma == "MASK_THIEU_TAI_NGUYEN"
    assert kho._du_lieu.yeu_cau == {}
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        core.verify("nội dung", [], known=[])


@pytest.mark.parametrize("thieu", sorted(TU_VUNG_DEMO))
def test_thieu_tung_tai_nguyen_chan_ke_ca_khong_khop_mau(monkeypatch, thieu):
    def doc(ten):
        if ten == thieu:
            raise tai_nguyen.ThieuTaiNguyen()
        return TU_VUNG_DEMO[ten]
    monkeypatch.setattr(tai_nguyen, "doc_dong", doc)
    kho = KhoBoNho()
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        xu_ly.che("nội dung", [], kho)
    assert kho._du_lieu.yeu_cau == {}


def test_whitelist_du_4_tep_dung_sha_va_thu_hoi_cache(tmp_path):
    cfg = cau_hinh_demo(tmp_path)
    tai_nguyen.nap_cau_hinh(cfg)
    assert detectors.surnames()[0] == frozenset({"Nguyễn", "Trần"})
    assert detectors._ascii_surnames() == frozenset({"Nguyen", "Tran"})
    assert "địa danh demo" in detectors.places()
    assert "DEMO" in detectors.acronyms()
    assert "nội" in leftovers.allowlist()[1]
    assert xu_ly.che("nội dung", [], KhoBoNho())["gui_duoc"] is True
    # Bản nạp là snapshot đã kiểm SHA, không âm thầm đọc lại nguồn vừa đổi.
    tep = Path(cfg["tai_nguyen"]["vn_surnames.txt"]["duong_dan"])
    tep.write_text("Họ DEMO khác", encoding="utf-8")
    assert "Nguyễn" in detectors.surnames()[0]
    with pytest.raises(tai_nguyen.ThieuTaiNguyen) as loi:
        tai_nguyen.nap_cau_hinh(cfg)
    assert str(tep) not in str(loi.value)
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        detectors.surnames()
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        detectors._ascii_surnames()
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        leftovers.allowlist()


@pytest.mark.parametrize("sai", ["thieu_tep", "thieu_whitelist", "sai_sha", "duong_tuong_doi", "ten_la", "tep_rong"])
def test_cau_hinh_chi_nhan_nguon_whitelist_du_va_dung(tmp_path, sai):
    cfg = cau_hinh_demo(tmp_path)
    muc = cfg["tai_nguyen"]["vn_places.txt"]
    if sai == "thieu_tep":
        muc["duong_dan"] = str(tmp_path / "khong-co-demo.txt")
    elif sai == "thieu_whitelist":
        del cfg["tai_nguyen"]["vn_places.txt"]
    elif sai == "sai_sha":
        muc["sha256"] = "0" * 64
    elif sai == "duong_tuong_doi":
        muc["duong_dan"] = "vn_places.txt"
    elif sai == "ten_la":
        cfg["tai_nguyen"]["khac.txt"] = muc
    else:
        Path(muc["duong_dan"]).write_bytes(b"")
        muc["sha256"] = sha256(b"").hexdigest()
    with pytest.raises(tai_nguyen.ThieuTaiNguyen) as loi:
        tai_nguyen.nap_cau_hinh(cfg)
    assert loi.value.ma == "MASK_THIEU_TAI_NGUYEN"
    assert str(tmp_path) not in str(loi.value)
    with pytest.raises(tai_nguyen.ThieuTaiNguyen):
        xu_ly.che("nội dung", [], KhoBoNho())


@pytest.mark.parametrize("dang", ["NFC", "NFD"])
def test_bi_danh_hong_khong_an_dau_vet_ten_va_tien_ngay(demo_tu_vung, dang):
    chu = unicodedata.normalize(dang, "[[KH-DEMO-00?; Họ và tên:\nnguyễn văn demo; 1.000.000 VND; 30/10/2026")
    assert xu_ly._an_bi_danh(chu) == chu
    con_sot, het = xu_ly._kiem_con_sot(chu, [])
    assert het is True
    muc = next(m for m in con_sot if m.get("nhom") == "CA_NHAN")
    vi_tri = muc["vi_tri"]
    assert chu[vi_tri["bat_dau"]:vi_tri["ket_thuc"]] == unicodedata.normalize(dang, "nguyễn văn demo")
    assert vi_tri["dong"] == 2 and vi_tri["cot"] == 1
    assert not xu_ly._kiem_tien_ngay(chu, chu.replace("1.000.000 VND", ""))
    assert not xu_ly._kiem_tien_ngay(chu, chu + "; 30/10/2026")
    kq = xu_ly.che(chu, [], KhoBoNho())
    assert kq["gui_duoc"] is False and kq["van_ban_da_che"] is None
    assert "nguyễn văn demo" not in repr(kq)


@pytest.mark.parametrize("ma", ["kh.demo_Ab-001", "kh-demo.002"])
def test_ma_chu_thuong_cham_gach_khong_bat_nham_van_xuoi(demo_tu_vung, ma):
    kho = KhoBoNho([{"gia_tri": TEN, "nhom": "CONG_TY", "ma_junsky": ma}])
    kq = xu_ly.che(TEN, [], kho)
    assert kq["van_ban_da_che"] == "[[" + ma + "]]"
    chu = "[[ " + ma.upper() + " ]] ; x" + ma + "y"
    mo = xu_ly.mo_che(chu, kq["ma_yeu_cau"], kho)
    assert mo["so_cho_mo"] == 1
    assert mo["mo_day_du"] is True
    assert mo["van_ban_da_mo_che"] == TEN + " ; x" + ma + "y"


def test_so_tien_thay_doi_khi_mo_khong_tra_van_ban_khong_dong(demo_tu_vung, monkeypatch):
    kho = KhoBoNho([{"gia_tri": TEN, "nhom": "CONG_TY", "ma_junsky": "KH-DEMO-001"}])
    kq = xu_ly.che(TEN, [], kho)
    monkeypatch.setattr(kho, "tra_dinh_danh", lambda _: "1.000.000 VND")
    mo = xu_ly.mo_che(kq["van_ban_da_che"], kq["ma_yeu_cau"], kho, dong_viec=True)
    assert mo["van_ban_da_mo_che"] is None
    assert mo["kiem_tien_ngay"] is False
    assert mo["mo_day_du"] is False
    assert mo["trang_thai_ma_yeu_cau"] == "DANG_XU_LY"
    assert kho.doc_yeu_cau(kq["ma_yeu_cau"])["trang_thai"] == "DANG_XU_LY"


def test_gioi_han_heuristic_ten_thuong_khong_nhan(demo_tu_vung):
    # Ca này chứng minh giới hạn, không phải chứng nhận văn bản an toàn Cloud.
    chu = "nguyễn văn demo đang làm việc"
    assert not detectors.people(chu)
    assert not list(xu_ly._vung_nhan(chu))


def test_numeric_review_giu_ranh_gioi_so_canh_bi_danh():
    assert core.numeric_review("12[[kh.demo-1]]34", "1234", [])["changed"] is True
