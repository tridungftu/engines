"""PL-7: đã kiểm bằng Core giả (CoreGia), chỉ dùng hóa đơn DEMO.

Kiểm nghiêm hình dạng tham chiếu khi mở tệp; quyền cùng việc/pháp nhân
vẫn phải kiểm trên Core thật. Không gọi e_hoa_don trong test/runtime.
"""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import Viec
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau, doc_lo, quy_trinh
from e_phan_luong.chay import app, phan_luong_hoa_don
from e_phan_luong.loi import CAU_LOI
from test_pl0_can_core import co_tham_chieu_tep

DEMO = Path(__file__).resolve().parent / "demo"
REPO = DEMO.parents[2]
NANG_LUC = "audit.phan_luong_hoa_don@1"


def doc_demo(ten):
    return json.loads((DEMO / ten).read_bytes())


def tham_so(**doi):
    return {
        "khau": "ktt_duyet", "ma_module": "demo_thanh_toan",
        "loai_nghiep_vu": "hoa_don_dau_vao",
        "nguong_json": (DEMO / "nguong-DEMO.json").read_text(encoding="utf-8"),
        "danh_muc_loai_json": json.dumps([{
            "ma": "hoa_don_dau_vao", "ten": "Hóa đơn đầu vào DEMO", "mo_ta": "DEMO",
        }], ensure_ascii=False),
        **doi,
    }


def xml():
    return doc_demo("hoa-don-xml-DEMO.json")


def zip_demo(core, raw=None):
    if raw is None:
        raw = (DEMO / "hoa-don-chi-tiet-zip-DEMO.json").read_bytes()
    pb = doc_demo("hoa-don-zip-DEMO.json")
    pb["truong"]["chi_tiet_nguon"] = core.them_tep(
        "chi-tiet-hoa-don-DEMO.json", raw, "application/json")
    return pb, raw


def chay(core, pb, ts=None):
    return core.chay_thu(app, NANG_LUC, pb, tham_so() if ts is None else ts)


def ket_qua(core, kq):
    assert kq["trang_thai"] == "XONG", kq
    truong = kq["ket_qua"]["truong"]
    tep = json.loads(core.doc_tep(truong["tep_json"]["tep_id"]))
    return truong, tep


def kiem_loi(kq, ma):
    assert kq["trang_thai"] == "LOI", kq
    assert kq["loi"] == {
        "ma": ma, "thong_diep": CAU_LOI[ma], "thu_lai_duoc": False,
    }


@pytest.fixture(autouse=True)
def core_nghiem(monkeypatch):
    """Bù khác biệt CoreGia: ID trơn không được coi là tham chiếu tệp."""
    mo_goc = Viec.mo_tep

    def mo(viec, tep_id):
        assert co_tham_chieu_tep(viec.dau_vao, tep_id)
        return mo_goc(viec, tep_id)

    monkeypatch.setattr(Viec, "mo_tep", mo)
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: bytes(range(32)))


@pytest.mark.parametrize("chi_tiet", ["giu_nguyen", None, "bo_khoa"])
def test_xml_mot_hoa_don_co_chi_tiet_xml_van_dung_truong(chi_tiet):
    core, pb = CoreGia(), xml()
    if chi_tiet is None:
        pb["truong"]["chi_tiet_nguon"] = None
    elif chi_tiet == "bo_khoa":
        del pb["truong"]["chi_tiet_nguon"]
    truong, tep = ket_qua(core, chay(core, pb))
    assert truong["so_nghiep_vu"] == truong["so_do_bat_buoc"] == 1
    assert truong["luong"] == "do" and truong["can_nguoi_kiem"] is True
    assert tep["nghiep_vu"] == [{
        "ma": "1-C26TAA-0000123", "luong": "do", "ly_do": ["CO_DO_CUNG"],
        "co": ["CUOI_KY"], "loai": "hoa_don_dau_vao", "nguon_loai": "module",
    }]
    assert truong["tong_tien_do"] == {"so": "1100000", "tien_te": "VND"}


def test_xml_bam_json_chuan_hoa_utf8_khong_phu_thuoc_thu_tu_khoa():
    pb = xml()
    pb["truong"]["nhan_demo"] = "Công ty DEMO Ánh Dương"
    raw = json.dumps(pb["truong"], sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False).encode("utf-8")
    bam = "sha256:" + sha256(raw).hexdigest()
    pb_dao = {"loai": "truong", "truong": dict(reversed(list(pb["truong"].items())))}
    for nguon in (pb, pb_dao):
        core = CoreGia()
        truong, tep = ket_qua(core, chay(core, nguon))
        assert truong["bam_dau_vao"] == tep["bam_dau_vao"] == bam
        assert core.xem_ngan(app.ma, "luot")[0]["bam_dau_vao"] == bam


def test_zip_mo_doi_tuong_tep_id_phan_luong_tung_hoa_don_va_canh_bao_bo(monkeypatch):
    core = CoreGia()
    pb, raw = zip_demo(core)
    mo_goc, da_mo = Viec.mo_tep, []

    def mo(viec, tep_id):
        assert viec.dau_vao["truong"]["chi_tiet_nguon"]["tep_id"] == tep_id
        da_mo.append(tep_id)
        return mo_goc(viec, tep_id)

    monkeypatch.setattr(Viec, "mo_tep", mo)
    truong, tep = ket_qua(core, chay(core, pb))
    assert da_mo == [pb["truong"]["chi_tiet_nguon"]["tep_id"]]
    assert truong["so_nghiep_vu"] == truong["so_do_bat_buoc"] == 2
    assert [d["ma"] for d in tep["nghiep_vu"]] == ["1-C26TAA-0000123", "1-C26TAA-0000124"]
    assert all(d["luong"] == "do" and "CO_DO_CUNG" in d["ly_do"] for d in tep["nghiep_vu"])
    assert "Bỏ 1 hóa đơn không đọc được" in truong["canh_bao"]
    assert truong["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()
    assert tep["ma_module"] == "demo_thanh_toan"


def test_zip_khong_bo_thi_khong_them_canh_bao_bo():
    core = CoreGia()
    bao_cao = doc_demo("hoa-don-chi-tiet-zip-DEMO.json")
    bao_cao["danh_sach_tep"] = [d for d in bao_cao["danh_sach_tep"] if d["trang_thai_doc"] == "doc_duoc"]
    pb, _ = zip_demo(core, json.dumps(bao_cao).encode("utf-8"))
    truong, _ = ket_qua(core, chay(core, pb))
    assert "hóa đơn không đọc được" not in truong["canh_bao"]


@pytest.mark.parametrize("nguon", ["xml", "zip"])
def test_can_kiem_tra_thanh_co_do_cung_thieu_tien_te_thanh_do(nguon):
    core = CoreGia()
    if nguon == "xml":
        pb = xml()
        cac_truong = [pb["truong"]]
    else:
        bao_cao = doc_demo("hoa-don-chi-tiet-zip-DEMO.json")
        cac_truong = [d["truong_hoa_don"] for d in bao_cao["danh_sach_tep"] if d["trang_thai_doc"] == "doc_duoc"]
    for t in cac_truong:
        t["can_kiem_tra"] = True
        t["don_vi_tien"] = None
        t["tong_thanh_toan"]["tien_te"] = None
    if nguon == "zip":
        pb, _ = zip_demo(core, json.dumps(bao_cao).encode("utf-8"))
    truong, tep = ket_qua(core, chay(core, pb))
    assert truong["tong_tien_do"] is None
    for d in tep["nghiep_vu"]:
        assert d["luong"] == "do"
        assert set(d["ly_do"]) == {"CHUA_RO_TIEN_TE", "CO_DO_CUNG"}


@pytest.mark.parametrize("nguon", ["xml", "zip"])
def test_thieu_nguong_json_loi_khong_lay_nguong_tu_hoa_don(nguon):
    core = CoreGia()
    pb = xml() if nguon == "xml" else zip_demo(core)[0]
    pb["truong"]["nguong"] = doc_demo("nguong-DEMO.json")
    kiem_loi(chay(core, pb, tham_so(nguong_json="")), "THIEU_NGUONG")
    assert core.xem_ngan(app.ma, "luot") == []


def test_ma_module_loai_nghiep_vu_chi_lay_tu_cai_dat_buoc():
    core, pb = CoreGia(), xml()
    pb["truong"].update(ma_module="demo_khong_dung", loai_nghiep_vu="loai_khong_dung")
    _, tep = ket_qua(core, chay(core, pb))
    assert tep["ma_module"] == "demo_thanh_toan"
    assert tep["nghiep_vu"][0]["loai"] == "hoa_don_dau_vao"


def test_hoa_don_khong_gan_loai_van_phan_luong_duoc():
    core = CoreGia()
    truong, tep = ket_qua(core, chay(core, xml(), tham_so(loai_nghiep_vu="")))
    assert truong["so_chua_phan_loai"] == 1
    assert tep["nghiep_vu"][0]["loai"] == "chua_phan_loai"


def test_thieu_tien_te_khong_can_co_do_cung_van_do():
    core, pb = CoreGia(), xml()
    pb["truong"]["can_kiem_tra"] = False
    pb["truong"]["don_vi_tien"] = None
    del pb["truong"]["tong_thanh_toan"]["tien_te"]
    _, tep = ket_qua(core, chay(core, pb))
    assert tep["nghiep_vu"][0]["ly_do"] == ["CHUA_RO_TIEN_TE"]


def test_zip_co_do_cung_lay_tung_hoa_don_khong_ep_theo_bang_ke(monkeypatch):
    core = CoreGia()
    bao_cao = doc_demo("hoa-don-chi-tiet-zip-DEMO.json")
    for d in bao_cao["danh_sach_tep"]:
        if d["trang_thai_doc"] == "doc_duoc":
            d["truong_hoa_don"]["can_kiem_tra"] = False
    pb, _ = zip_demo(core, json.dumps(bao_cao).encode("utf-8"))
    assert pb["truong"]["can_kiem_tra"] is True
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *_: False)
    truong, tep = ket_qua(core, chay(core, pb))
    assert truong["so_xanh"] == 2
    assert all(d["ly_do"] == ["KHONG_CHON"] for d in tep["nghiep_vu"])


def test_zip_khong_ho_tro_cung_duoc_dem_trong_canh_bao():
    core = CoreGia()
    bao_cao = doc_demo("hoa-don-chi-tiet-zip-DEMO.json")
    bao_cao["danh_sach_tep"].append({"trang_thai_doc": "khong_ho_tro"})
    pb, _ = zip_demo(core, json.dumps(bao_cao).encode("utf-8"))
    truong, _ = ket_qua(core, chay(core, pb))
    assert "Bỏ 2 hóa đơn không đọc được" in truong["canh_bao"]


def test_xml_chua_khai_nguon_doc_khong_co_chi_tiet():
    core, pb = CoreGia(), xml()
    del pb["truong"]["nguon_doc"]
    del pb["truong"]["chi_tiet_nguon"]
    truong, _ = ket_qua(core, chay(core, pb))
    assert truong["so_nghiep_vu"] == 1


def test_zip_co_tham_chieu_khong_khai_nguon_doc_van_doc_chi_tiet():
    core = CoreGia()
    pb, raw = zip_demo(core)
    del pb["truong"]["nguon_doc"]
    truong, _ = ket_qua(core, chay(core, pb))
    assert truong["so_nghiep_vu"] == 2
    assert truong["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()


@pytest.mark.parametrize("nguon", ["xml", "zip"])
def test_c4_mst_ban_va_chi_tiet_khong_xuat_hien_trong_xem_ngan(nguon):
    core = CoreGia()
    pb = xml() if nguon == "xml" else zip_demo(core)[0]
    ket_qua(core, chay(core, pb))
    for bang in app.phieu["ngan_du_lieu"]:
        ds = core.xem_ngan(app.ma, bang["bang"])
        chu = json.dumps(ds, ensure_ascii=False)
        assert "0100000001" not in chu and "0100000002" not in chu
        for dong in ds:
            assert not set(dong) & {"so_tien", "ngay", "doi_tac", "dien_giai", "noi_dung", "ma_so_thue_ban"}


def test_c5_truong_va_tep_khong_lo_ty_le_xac_suat_hat_giong():
    core = CoreGia()
    truong, tep = ket_qua(core, chay(core, xml()))
    for nut in [truong, tep, *tep["nghiep_vu"]]:
        assert not any(c in k for k in nut for c in ("ty_le", "xac_suat", "bac"))
        assert "hat_giong" not in nut
    assert not any(c in truong["canh_bao"] for c in ("%", "tỷ lệ", "xác suất", "bậc"))


@pytest.mark.parametrize("tham_chieu", [None, "tep-DEMO", {}, {"tep_id": ""}, {"tep_id": 1}])
def test_zip_tham_chieu_hong_khong_fallback_sang_mot_hoa_don(tham_chieu):
    pb = doc_demo("hoa-don-zip-DEMO.json")
    pb["truong"].update(xml()["truong"])
    pb["truong"]["nguon_doc"] = "zip_xml_strict"
    pb["truong"]["chi_tiet_nguon"] = tham_chieu
    kiem_loi(chay(CoreGia(), pb), "DU_LIEU_KHONG_HOP_LE")


def test_zip_doc_toi_da_tran_cong_mot_va_dong_luong_ke_ca_loi(monkeypatch):
    core = CoreGia()
    pb, _ = zip_demo(core)
    monkeypatch.setattr(doc_lo, "TOI_DA_BYTE", 64)

    class Luong(BytesIO):
        def read(self, so=-1):
            assert so == 65
            return super().read(so)

    luong = Luong(b" " * 66)
    monkeypatch.setattr(Viec, "mo_tep", lambda *_: luong)
    kiem_loi(chay(core, pb), "VUOT_GIOI_HAN")
    assert luong.closed
    assert core.xem_ngan(app.ma, "luot") == []


def test_xml_truong_chuan_hoa_vuot_tran_bi_tu_choi(monkeypatch):
    core = CoreGia()
    monkeypatch.setattr(doc_lo, "TOI_DA_BYTE", 128)
    # Không làm tràn phần lô rỗng dùng kiểm ma_module; trần áp cả bộ trường.
    kiem_loi(chay(core, xml()), "VUOT_GIOI_HAN")
    assert core.xem_ngan(app.ma, "luot") == []


def test_bat_dau_truoc_doc_va_giu_diem_noi_chung(monkeypatch):
    cac_buoc = []

    class ViecThu:
        dau_vao = xml()
        tham_so = tham_so()

    def bat_dau(viec):
        cac_buoc.append("bat_dau")

    def chay_chung(viec, lo, du_lieu, *, canh_bao_them):
        assert cac_buoc == ["bat_dau"]
        assert lo.nguong is None and len(lo.nghiep_vu) == 1
        assert json.loads(du_lieu) == viec.dau_vao["truong"]
        assert canh_bao_them == []
        return {"nhan": "DEMO"}

    monkeypatch.setattr(quy_trinh, "bat_dau", bat_dau)
    monkeypatch.setattr(quy_trinh, "chay_phan_luong", chay_chung)
    assert phan_luong_hoa_don(ViecThu()) == {"loai": "truong", "truong": {"nhan": "DEMO"}}


def test_nhan_tra_noi_duoc_xml_va_zip_theo_phieu():
    phieu = json.loads((REPO / "e_hoa_don/goi/e_hoa_don/engine.json").read_bytes())
    nhan = next(n["nhan"] for n in app.phieu["nang_luc"] if n["ma"] == NANG_LUC)
    for ma in ("hoa_don.doc_xml@2", "hoa_don.doc_zip@1"):
        nl = next(n for n in phieu["nang_luc"] if n["ma"] == ma)
        assert nl["tra"] in nhan == ["truong"]


def test_demo_mot_hoa_don_dung_bo_truong_xml_va_chay_duoc():
    vd, = [v for v in app.phieu["chay_thu_demo"] if v["nang_luc"] == NANG_LUC]
    phieu = json.loads((REPO / "e_hoa_don/goi/e_hoa_don/engine.json").read_bytes())
    nl = next(n for n in phieu["nang_luc"] if n["ma"] == "hoa_don.doc_xml@2")
    assert set(vd["dau_vao"]["truong"]) == {t["ma"] for t in nl["truong_ra"]}
    assert "DEMO" in json.dumps(vd["dau_vao"])
    core = CoreGia()
    truong, _ = ket_qua(core, chay(core, vd["dau_vao"], vd["tham_so"]))
    assert truong["so_nghiep_vu"] == 1
