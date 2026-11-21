"""Kiểm PL-7A bằng DEMO; tệp mẫu sinh từ bộ đọc e_hoa_don hiện hành.

hoa-don-xml-DEMO.json: doc_xml(demo/hoa-don-DEMO.xml).
hoa-don-zip-DEMO.json và hoa-don-chi-tiet-zip-DEMO.json: doc_zip của
hai XML DEMO số 0000123/0000124, ở giữa có XML hỏng <HDon>DEMO.
Không gọi engine khác khi chạy test. Đã kiểm bằng Core giả (CoreGia),
chưa kiểm quyền kho tệp/cùng việc trên Core thật.
"""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import sys

import pytest
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import doc_lo, hoa_don, kieu, loi

DEMO = Path(__file__).resolve().parent / "demo"
REPO = DEMO.parents[2]
THAM_SO = {"ma_module": "demo_thanh_toan", "loai_nghiep_vu": "hoa_don_dau_vao"}


def _doc(ten):
    return json.loads((DEMO / ten).read_text(encoding="utf-8"), parse_float=Decimal)


def _truong():
    return _doc("hoa-don-xml-DEMO.json")["truong"]


def _bao_cao():
    return _doc("hoa-don-chi-tiet-zip-DEMO.json")


def _bytes(gia_tri):
    return json.dumps(gia_tri, ensure_ascii=False).encode("utf-8")


def _kiem_loi(ham, *args, ma="DU_LIEU_KHONG_HOP_LE", **kwargs):
    with pytest.raises(loi.LoiNghiepVu) as bat:
        ham(*args, **kwargs)
    assert bat.value.ma == ma
    assert bat.value.thong_diep == loi.CAU_LOI[ma]
    assert not bat.value.thu_lai_duoc


@pytest.mark.parametrize("ten,nang_luc", [
    ("hoa-don-xml-DEMO.json", "hoa_don.doc_xml@2"),
    ("hoa-don-zip-DEMO.json", "hoa_don.doc_zip@1"),
])
def test_phong_bi_demo_dung_truong_ra_e_hoa_don(ten, nang_luc):
    phieu = json.loads((REPO / "e_hoa_don/goi/e_hoa_don/engine.json").read_text(encoding="utf-8"))
    nl = next(n for n in phieu["nang_luc"] if n["ma"] == nang_luc)
    pb = _doc(ten)
    assert pb["loai"] == "truong"
    assert set(pb["truong"]) == {t["ma"] for t in nl["truong_ra"]}
    tep = hoa_don.lay_tep_chi_tiet(pb["truong"])
    assert set(tep) == {"tep_id", "ten", "mime", "kich_thuoc"}
    if nang_luc.endswith("doc_zip@1"):
        assert tep["kich_thuoc"] == (DEMO / tep["ten"]).stat().st_size


def test_anh_xa_du_truong_mot_hoa_don_mot_nghiep_vu_khong_sua_nguon():
    truong = _truong()
    ban_dau = deepcopy(truong)
    lo = hoa_don.lo_tu_hoa_don(truong, **THAM_SO)
    assert isinstance(lo, kieu.Lo)
    assert (lo.phien_ban, lo.ma_module, lo.ky, lo.nguong) == (1, "demo_thanh_toan", None, None)
    assert lo.nghiep_vu == (kieu.NghiepVu(
        chi_so=0, ma="1-C26TAA-0000123-0100000001", ngay=date(2026, 10, 30),
        so_tien=kieu.Tien(Decimal("1100000"), "VND"),
        doi_tac="0100000001", loai="hoa_don_dau_vao", co_do_cung=True,
    ),)
    assert truong == ban_dau


@pytest.mark.parametrize("can_kiem_tra", [True, False])
def test_co_do_cung_va_loai_tuy_chon(can_kiem_tra):
    truong = _truong()
    truong["can_kiem_tra"] = can_kiem_tra
    truong["so_dong"] = 30  # Dòng hàng không làm tăng số nghiệp vụ.
    lo = hoa_don.lo_tu_hoa_don(truong, ma_module="demo_thanh_toan", loai_nghiep_vu=None)
    nv, = lo.nghiep_vu
    assert nv.co_do_cung is can_kiem_tra
    assert nv.loai is None


@pytest.mark.parametrize("don_vi", [None, "USD"])
@pytest.mark.parametrize("co_khoa_tien_te", [True, False])
def test_thieu_tien_te_khong_tu_gan_vnd_va_dung_don_vi_hoa_don(don_vi, co_khoa_tien_te):
    truong = _truong()
    truong["don_vi_tien"] = don_vi
    truong["tong_thanh_toan"] = {"so": "1000000.123456"}
    if co_khoa_tien_te:
        truong["tong_thanh_toan"]["tien_te"] = None
    nv, = hoa_don.lo_tu_hoa_don(truong, **THAM_SO).nghiep_vu
    assert nv.so_tien == kieu.Tien(Decimal("1000000.123456"), don_vi)


def test_tien_te_trong_tong_duoc_giu_khi_khong_co_don_vi_tien():
    truong = _truong()
    del truong["don_vi_tien"]
    truong["tong_thanh_toan"] = {"so": Decimal("-1000000.123456"), "tien_te": "EUR"}
    nv, = hoa_don.lo_tu_hoa_don(truong, **THAM_SO).nghiep_vu
    assert nv.so_tien == kieu.Tien(Decimal("-1000000.123456"), "EUR")


@pytest.mark.parametrize("khoa,gia_tri", [
    ("mau_so", None), ("mau_so", ""), ("ky_hieu", " "), ("so_hoa_don", 123),
    ("so_hoa_don", "DEMO\n"), ("so_hoa_don", "D" * 121),
    ("ngay_lap", "2026-02-29"), ("ngay_lap", None),
    ("tong_thanh_toan", None), ("tong_thanh_toan", "1100000"),
    ("tong_thanh_toan", {"so": 1.1}), ("tong_thanh_toan", {"so": "NaN"}),
    ("tong_thanh_toan", {"so": "1.1234567"}),
    ("tong_thanh_toan", {"so": "1", "tien_te": "USD"}),
    ("don_vi_tien", "vnd"), ("can_kiem_tra", 1), ("can_kiem_tra", "true"),
    ("ma_so_thue_ban", {}),
])
def test_du_lieu_hoa_don_sai_khong_suy_doan(khoa, gia_tri):
    truong = _truong()
    truong[khoa] = gia_tri
    _kiem_loi(hoa_don.lo_tu_hoa_don, truong, **THAM_SO)


@pytest.mark.parametrize("khoa", ["mau_so", "ky_hieu", "so_hoa_don", "ngay_lap", "tong_thanh_toan"])
def test_thieu_truong_bat_buoc(khoa):
    truong = _truong()
    del truong[khoa]
    _kiem_loi(hoa_don.lo_tu_hoa_don, truong, **THAM_SO)


@pytest.mark.parametrize("ma_module", [None, "", "Demo", "demo-module", "d" * 32])
def test_ma_module_dung_luat_doc_lo_ke_ca_zip_rong(ma_module):
    tham_so = {**THAM_SO, "ma_module": ma_module}
    _kiem_loi(hoa_don.lo_tu_hoa_don, _truong(), **tham_so)
    bao_cao = _bao_cao()
    bao_cao["danh_sach_tep"] = []
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, _bytes(bao_cao), **tham_so)


@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"])
def test_zip_hai_hoa_don_va_mot_hong_bo_va_dem(bom):
    raw = (DEMO / "hoa-don-chi-tiet-zip-DEMO.json").read_bytes()
    lo, so_bo = hoa_don.lo_tu_chi_tiet_zip(bom + raw, **THAM_SO)
    assert so_bo == 1
    assert [nv.ma for nv in lo.nghiep_vu] == ["1-C26TAA-0000123-0100000001", "1-C26TAA-0000124-0100000001"]
    assert [nv.chi_so for nv in lo.nghiep_vu] == [0, 1]
    assert all(nv.co_do_cung for nv in lo.nghiep_vu)
    assert lo.nghiep_vu[0] == hoa_don.lo_tu_hoa_don(_truong(), **THAM_SO).nghiep_vu[0]
    assert lo.ma_module == THAM_SO["ma_module"] and lo.ky is None and lo.nguong is None


def test_zip_khong_ho_tro_duoc_dem_thu_muc_khong_thanh_nghiep_vu():
    bao_cao = _bao_cao()
    bao_cao["danh_sach_tep"][1]["trang_thai_doc"] = "khong_ho_tro"
    bao_cao["danh_sach_thu_muc"] = [{"thu_tu": 4, "ten": "DEMO/", "trung_ten": False, "canh_bao": []}]
    lo, so_bo = hoa_don.lo_tu_chi_tiet_zip(_bytes(bao_cao), **THAM_SO)
    assert len(lo.nghiep_vu) == 2 and so_bo == 1


def test_zip_ma_trung_tu_choi_ca_lo_ke_ca_ban_trung_noi_dung():
    bao_cao = _bao_cao()
    bao_cao["danh_sach_tep"][2] = deepcopy(bao_cao["danh_sach_tep"][0])
    bao_cao["danh_sach_tep"][2]["thu_tu"] = 3
    bao_cao["danh_sach_tep"][2]["trung_noi_dung_voi"] = 1
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, _bytes(bao_cao), **THAM_SO)


@pytest.mark.parametrize("dong", [None, {}, {"trang_thai_doc": "DEMO"},
    {"trang_thai_doc": "doc_duoc", "truong_hoa_don": None}])
def test_zip_sai_cau_truc_khong_bi_bo_nhu_loi_doc(dong):
    bao_cao = _bao_cao()
    bao_cao["danh_sach_tep"].append(dong)
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, _bytes(bao_cao), **THAM_SO)


@pytest.mark.parametrize("khoa,gia_tri", [("phien_ban", True), ("phien_ban", 2),
    ("nguon_doc", "xml_strict"), ("danh_sach_tep", {})])
def test_zip_sai_phien_ban_nguon_danh_sach(khoa, gia_tri):
    bao_cao = _bao_cao()
    bao_cao[khoa] = gia_tri
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, _bytes(bao_cao), **THAM_SO)


@pytest.mark.parametrize("raw,ma", [
    (b"DEMO", "TEP_KHONG_HO_TRO"), (b"\xff", "TEP_KHONG_HO_TRO"),
    (b"{} {}", "TEP_KHONG_HO_TRO"), (b"[", "TEP_KHONG_HO_TRO"),
    (b"[]", "DU_LIEU_KHONG_HOP_LE"), (b"null", "DU_LIEU_KHONG_HOP_LE"),
    (b'{"phien_ban":1,"phien_ban":1}', "DU_LIEU_KHONG_HOP_LE"),
    (b'{"so":NaN}', "DU_LIEU_KHONG_HOP_LE"),
])
def test_zip_json_sai_khoa_trung_va_hang_so(raw, ma):
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, raw, ma=ma, **THAM_SO)


def test_zip_so_json_thap_phan_duoc_doc_decimal_khong_qua_float():
    bao_cao = _bao_cao()
    bao_cao["danh_sach_tep"][0]["truong_hoa_don"]["tong_thanh_toan"]["so"] = "1000000.123456"
    raw = _bytes(bao_cao).replace(b'"1000000.123456"', b'1000000.123456')
    lo, _ = hoa_don.lo_tu_chi_tiet_zip(raw, **THAM_SO)
    assert lo.nghiep_vu[0].so_tien.so == Decimal("1000000.123456")


def test_tran_20_mib_dung_thi_doc_vuot_thi_tu_choi_truoc_parse():
    raw = (DEMO / "hoa-don-chi-tiet-zip-DEMO.json").read_bytes()
    raw += b" " * (doc_lo.TOI_DA_BYTE - len(raw))
    assert len(hoa_don.lo_tu_chi_tiet_zip(raw, **THAM_SO)[0].nghiep_vu) == 2
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, raw + b" ", ma="VUOT_GIOI_HAN", **THAM_SO)


def test_tran_50000_tinh_ca_tep_loi_khong_cat_ngam():
    bao_cao = _bao_cao()
    bao_cao["danh_sach_tep"] = [{"trang_thai_doc": "loi"}] * doc_lo.TOI_DA_DONG
    lo, so_bo = hoa_don.lo_tu_chi_tiet_zip(_bytes(bao_cao), **THAM_SO)
    assert lo.nghiep_vu == () and so_bo == doc_lo.TOI_DA_DONG
    bao_cao["danh_sach_tep"].append({"trang_thai_doc": "loi"})
    _kiem_loi(hoa_don.lo_tu_chi_tiet_zip, _bytes(bao_cao), ma="VUOT_GIOI_HAN", **THAM_SO)


@pytest.mark.parametrize("truong", [None, {}, {"chi_tiet_nguon": None},
    {"chi_tiet_nguon": "tep-DEMO"}, {"chi_tiet_nguon": {}},
    {"chi_tiet_nguon": {"tep_id": ""}}, {"chi_tiet_nguon": {"tep_id": " "}},
    {"chi_tiet_nguon": {"tep_id": 1}}])
def test_tham_chieu_phai_la_doi_tuong_co_tep_id(truong):
    _kiem_loi(hoa_don.lay_tep_chi_tiet, truong)


def test_tham_chieu_giu_nguyen_metadata_va_mo_bang_core_gia():
    core = CoreGia()
    raw = (DEMO / "hoa-don-chi-tiet-zip-DEMO.json").read_bytes()
    ref = core.them_tep("hoa-don-chi-tiet-zip-DEMO.json", raw, "application/json")
    pb = _doc("hoa-don-zip-DEMO.json")
    pb["truong"]["chi_tiet_nguon"] = ref
    assert hoa_don.lay_tep_chi_tiet(pb["truong"]) is ref
    phieu = json.loads((REPO / "e_phan_luong/goi/e_phan_luong/engine.json").read_text(encoding="utf-8"))
    phieu["nang_luc"] = [{"ma": "demo.doc_hoa_don@1", "ten": "Đọc chi tiết DEMO",
        "nhan": ["truong"], "tra": "van_ban", "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 300}}]
    phieu["chay_thu_demo"] = [v for v in phieu.get("chay_thu_demo", [])
                              if v["nang_luc"] in {n["ma"] for n in phieu["nang_luc"]}]
    app = Engine(phieu)

    @app.nang_luc("demo.doc_hoa_don@1")
    def doc(viec):
        tep = hoa_don.lay_tep_chi_tiet(viec.dau_vao["truong"])
        # Điều kiện hình dạng Core thật: đối tượng có đúng khóa tep_id.
        assert viec.dau_vao["truong"]["chi_tiet_nguon"]["tep_id"] == tep["tep_id"]
        with viec.mo_tep(tep["tep_id"]) as luong:
            lo, so_bo = hoa_don.lo_tu_chi_tiet_zip(luong.read(), **THAM_SO)
        return {"loai": "van_ban", "van_ban": f"DEMO: {len(lo.nghiep_vu)} hóa đơn; bỏ {so_bo} tệp."}

    kq = core.chay_thu(app, "demo.doc_hoa_don@1", pb)
    assert kq["trang_thai"] == "XONG", kq
    assert kq["ket_qua"]["van_ban"] == "DEMO: 2 hóa đơn; bỏ 1 tệp."
