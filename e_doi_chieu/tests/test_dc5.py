"""DC-5: ma trận DEMO; đã kiểm bằng Core giả (CoreGia), 0 Cloud."""
from copy import deepcopy
from decimal import Decimal
import importlib
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

from test_dc3 import Mau, PN, chay, hs, kiem_loi, quy_tac_demo
from test_dc4 import dat_cap, so, snapshot_so, giao_so

qt = importlib.import_module("e_doi_chieu.quy_tac")
tc = importlib.import_module("e_doi_chieu.tien_chu")
VN = {"nghin": ".", "thap_phan": ","}
US = {"nghin": ",", "thap_phan": "."}


def bo_demo():
    b = quy_tac_demo()
    b["quy_tac_cung"] = {"phien_ban": 1, "dinh_dang_so": [VN],
        "don_vi_tien": {"VND": "VND", "đồng": "VND", "USD": "USD", "đô la Mỹ": "USD"},
        "dinh_dang_ngay": ["YYYY-MM-DD"], "vung_bao_ve": []}
    return b


def dat_bo(m, bo):
    ref = m.luu("bo-dc5.json", hs.json_bytes(bo), "application/json", True)
    m.cap["bo_quy_tac"] = ref
    m.cau_hinh["bam_bo_chuan_hoa"] = ref["bam"]
    m.dat_cau_hinh()


@pytest.fixture
def mau(monkeypatch):
    m = Mau()
    monkeypatch.setattr(chay, "ngan", m.ngan)
    dat_bo(m, bo_demo())
    return m


def chay_cap(m, a, b=None, bo=None):
    dat_cap(m, a, b)
    if bo:
        dat_bo(m, bo)
    return snapshot_so(m, so(m))


# Mỗi dòng có ca dương và ca không lệch bằng cùng nội dung đầu; ca tiền
# nội bộ dùng bản chữ đúng riêng vì hai bản giống nhau vẫn có thể sai nội bộ.
MA_TRAN = [
    ("chu_so", "DEMO mã 12345", "DEMO mã 12346", "DC_CHU_SO"),
    ("tien", "DEMO 1.000.000 VND", "DEMO 1.100.000 VND", "DC_TIEN_TY_LE"),
    ("tien_te", "DEMO 1.000.000 VND", "DEMO 1.000.000 USD", "DC_TIEN_TY_LE"),
    ("ngay", "DEMO ngày 2026-10-30", "DEMO ngày 2026-10-31", "DC_NGAY_THOI_HAN"),
    ("thoi_han", "DEMO thời hạn ba ngày", "DEMO thời hạn bốn ngày", "DC_NGAY_THOI_HAN"),
    ("ty_le", "DEMO tỷ lệ 5%", "DEMO tỷ lệ 8%", "DC_TIEN_TY_LE"),
    ("tien_chu", "DEMO bằng chữ một triệu đồng", "DEMO bằng chữ hai triệu đồng", "DC_TIEN_TY_LE"),
    ("ben_ky", "Bên A: Công ty DEMO thuê", "Bên A: Công ty DEMO thuế", "DC_DINH_DANH"),
    ("dai_dien", "Đại diện: Ông DEMO Ánh", "Đại diện: Ông DEMO Anh", "DC_DINH_DANH"),
    ("chuc_vu", "Chức vụ: Giám đốc DEMO", "Chức vụ: Phó giám đốc DEMO", "DC_DINH_DANH"),
    ("mst_0_dau", "MST: 0012345678 DEMO", "MST: 012345678 DEMO", "DC_DINH_DANH"),
    ("stk", "STK: 000123456 DEMO", "STK: 000123457 DEMO", "DC_DINH_DANH"),
    ("dia_chi", "Địa chỉ: đường DEMO Ánh", "Địa chỉ: đường DEMO Anh", "DC_DINH_DANH"),
    ("so_hd", "Số hợp đồng: DEMO-001", "Số hợp đồng: DEMO-002", "DC_DINH_DANH"),
    ("khong", "DEMO đồng ý.", "DEMO không đồng ý.", "DC_PHU_DINH_BAT_BUOC"),
    ("chua", "DEMO thanh lý.", "DEMO chưa thanh lý.", "DC_PHU_DINH_BAT_BUOC"),
    ("phai", "DEMO giao hàng.", "DEMO phải giao hàng.", "DC_PHU_DINH_BAT_BUOC"),
    ("chi", "DEMO xem.", "DEMO chỉ xem.", "DC_PHU_DINH_BAT_BUOC"),
    ("tru", "DEMO điều này.", "DEMO trừ điều này.", "DC_PHU_DINH_BAT_BUOC"),
    ("ngoai_tru", "DEMO điều này.", "DEMO ngoại trừ điều này.", "DC_PHU_DINH_BAT_BUOC"),
    ("duoc", "DEMO nhận.", "DEMO được nhận.", "DC_PHU_DINH_BAT_BUOC"),
    ("co_the", "DEMO nhận.", "DEMO có thể nhận.", "DC_PHU_DINH_BAT_BUOC"),
    ("mat_dieu", "Điều 1. DEMO\nA\nĐiều 2. DEMO\nB", "Điều 1. DEMO\nA", "DC_CAU_TRUC"),
    ("thua_dieu", "Điều 1. DEMO\nA", "Điều 1. DEMO\nA\nĐiều 2. DEMO\nB", "DC_CAU_TRUC"),
    ("dao_dieu", "Điều 1. DEMO\nA\nĐiều 2. DEMO\nB", "Điều 2. DEMO\nB\nĐiều 1. DEMO\nA", "DC_CAU_TRUC"),
    ("ocr_0_o", "DEMO mã 1000", "DEMO mã 1O00", "DC_OCR_NHAM"),
    ("ocr_1_l", "DEMO mã 1111", "DEMO mã 11l1", "DC_OCR_NHAM"),
    ("ocr_5_s", "DEMO mã 5555", "DEMO mã 55S5", "DC_OCR_NHAM"),
    ("ocr_8_b", "DEMO mã 8888", "DEMO mã 88B8", "DC_OCR_NHAM"),
]


@pytest.mark.parametrize("ten,a,b,quy_tac", MA_TRAN, ids=[r[0] for r in MA_TRAN])
def test_ma_tran_duong_bat_du_diem_da_cai(mau, ten, a, b, quy_tac):
    s = chay_cap(mau, a, b)
    points = [d for d in s["diem_lech"] if d["phep"] != "kiem_noi_bo"]
    assert points and all(d["muc_san"] == d["muc"] == "nghiem_trong" for d in points)
    assert any(quy_tac in d["quy_tac_trung"] for d in points)
    assert qt.kiem_bat_bien(s)
    assert s["tom_tat"]["so_nghiem_trong"] >= len(points)
    assert not s["da_kiem_du"] and s["de_nghi_chan"] and s["ket_luan"] is None


@pytest.mark.parametrize("ten,a,b,quy_tac", MA_TRAN, ids=[r[0] for r in MA_TRAN])
def test_ma_tran_khong_lech_khong_tu_sinh_nghiem_trong(mau, ten, a, b, quy_tac):
    s = chay_cap(mau, a)
    assert not [d for d in s["diem_lech"] if d["muc"] == "nghiem_trong"]
    assert s["tom_tat"]["so_nghiem_trong"] == 0


@pytest.mark.parametrize("so,chu,gia_tri", [
    ("1.000.000 VND", "một triệu đồng", 1000000),
    ("1.100.000 VND", "một triệu một trăm nghìn đồng", 1100000),
    ("0 VND", "không đồng", 0),
    ("15 VND", "mười lăm đồng chẵn", 15),
    ("21 USD", "hai mươi mốt đô la Mỹ", 21),
    ("105 VND", "một trăm linh năm đồng", 105),
    ("1.000.005 VND", "một triệu không trăm lẻ năm đồng", 1000005),
    ("1.000.000.000 VND", "một tỷ đồng", 1000000000),
])
def test_tien_noi_bo_giong_nhau_khop_chi_khi_phan_tich_du(mau, so, chu, gia_tri):
    s = chay_cap(mau, f"DEMO số tiền {so} (Bằng chữ: {chu}).")
    x, = s["kiem_quy_tac"]["tien_bang_chu"]["danh_sach"]
    assert x["da_kiem_du"] and x["khop"] is True
    assert x["tien_bang_so"] == x["tien_bang_chu"] == {"so": gia_tri, "tien_te": "USD" if "USD" in so else "VND"}
    assert not s["diem_lech"]


@pytest.mark.parametrize("so,chu", [
    ("1.000.000 VND", "một triệu một trăm nghìn đồng"),
    ("1.100.000 VND", "một triệu đồng"),
    ("1.000.000 VND", "một triệu USD"),
    ("-100 VND", "một trăm đồng"),
])
def test_tien_noi_bo_giong_word_van_bat_trai_so(mau, so, chu):
    text = f"DEMO {so} (Bằng chữ: {chu})."
    s = chay_cap(mau, text)
    d, = s["diem_lech"]
    assert d["quy_tac_trung"] == ["DC_TIEN_CHU"] and d["muc_san"] == "nghiem_trong"
    assert s["tom_tat"]["so_nghiem_trong"] == 1
    x = d["can_cu"]["kiem_tien"]
    assert x["da_kiem_du"] and x["khop"] is False
    assert x["so"]["nguyen_van"] == so and x["chu"]["nguyen_van"] == chu
    assert d["ban_ky"]["nguyen_van"] == text


@pytest.mark.parametrize("text", [
    "DEMO 1.000 VND (Bằng chữ: một nghìn đồng).",
    "DEMO 1,000 VND (Bằng chữ: một nghìn đồng).",
    "DEMO 1.00.000 VND (Bằng chữ: một triệu đồng).",
    "DEMO 1000 VND (Bằng chữ: nghìn đồng).",
    "DEMO 1000 VND (Bằng chữ: một nghìn).",
    "DEMO 1000 VND (Bằng chữ: một ngìn đồng).",
    "DEMO 1000 VND (Bằng chữ: one thousand VND).",
    "DEMO 1000 VND (Bằng chữ: một nghìn đồng và hơn).",
    "DEMO 1000 VND và 2000 VND (Bằng chữ: một nghìn đồng).",
    "DEMO Bằng chữ: một triệu đồng.",
    "DEMO 1000 $ (Bằng chữ: một nghìn đồng).",
    "DEMO 1000 CHF (Bằng chữ: một nghìn đồng).",
    "DEMO 1000 VND.",
    "DEMO một triệu đồng.",
    "DEMO 1000VND (Bằng chữ: một nghìn đồng) và nội dung khác.",
])
def test_mo_ho_thieu_khong_doc_duoc_khong_tu_coi_khop(mau, text):
    b = bo_demo()
    if "1.000 VND" in text or "1,000 VND" in text:
        b["quy_tac_cung"]["dinh_dang_so"] = [VN, US]
    s = chay_cap(mau, text, bo=b)
    k = s["kiem_quy_tac"]["tien_bang_chu"]
    assert k["danh_sach"] and not k["da_kiem_du"]
    assert all(x["khop"] is None for x in k["danh_sach"])
    assert all(d["muc_san"] == "can_xem" for d in s["diem_lech"])


@pytest.mark.parametrize("chu,so", [
    ("mười", 10), ("mười một", 11), ("hai mươi tư", 24), ("hai mươi lăm", 25),
    ("một trăm mười", 110), ("chín trăm chín mươi chín", 999),
    ("một tỷ hai triệu ba nghìn bốn trăm linh năm", 1002003405),
    ("một ngàn", 1000), ("một tỉ", 1000000000),
    ("một trăm năm", None), ("mười mốt", None), ("một mươi", None),
    ("một triệu triệu", None), ("một nghìn một triệu", None), ("một tỷ triệu", None),
    ("triệu", None), ("một trăm linh", None), ("một trăm linh không", None),
    ("một phẩy năm", None), ("một nghìn tỷ", None),
])
def test_ngu_phap_chu_nghiem_khong_doan(chu, so):
    assert tc.doc_chu_so(chu) == so


@pytest.mark.parametrize("raw,formats,expected", [
    ("1.000.000", [VN], Decimal(1000000)), ("1,000,000", [US], Decimal(1000000)),
    ("1.000", [VN, US], None), ("1,000", [VN, US], None),
    ("1.000.000", [], None), ("001234", [], Decimal(1234)),
    ("1.00.000", [VN], None), ("1.000,25", [VN], Decimal("1000.25")),
    ("123456789012345678901234567890.01", [US], Decimal("123456789012345678901234567890.01")),
    ("NaN", [US], None), ("1e6", [US], None), ("1O00", [VN], None),
])
def test_phan_cach_decimal_khong_float(raw, formats, expected):
    result = tc.doc_so(raw, formats)
    assert result == expected and (result is None or type(result) is Decimal)


def test_chi_quy_uoc_da_khai_moi_cho_tuong_duong(mau):
    b = bo_demo()
    b["quy_tac_cung"]["dinh_dang_so"] = [VN, US]
    s = chay_cap(mau, "DEMO số 1.000.000", "DEMO số 1,000,000", b)
    assert s["diem_lech"] and all(d["muc_san"] == "hinh_thuc" for d in s["diem_lech"])
    b["quy_tac_cung"]["dinh_dang_so"] = []
    s = chay_cap(mau, "DEMO số 1.000.000", "DEMO số 1,000,000", b)
    assert all(d["muc_san"] == "nghiem_trong" for d in s["diem_lech"])


def test_giu_0_dau_khong_dung_decimal_de_gop_ma(mau):
    s = chay_cap(mau, "DEMO 000123", "DEMO 123")
    assert s["diem_lech"] and all(d["muc_san"] == "nghiem_trong" for d in s["diem_lech"])
    assert "000123" in s["van_ban"]["word"]["van_ban_tai_lieu"]["van_ban"]


@pytest.mark.parametrize("a,b", [
    ("Số hợp đồng: DEMO-001", "Số hợp đồng: DEMO–001"),
    ("Bên A: Công ty DEMO–Ánh", "Bên A: Công ty DEMO-Ánh"),
    ("MST: 001\u00a0234 DEMO", "MST: 001 234 DEMO"),
    ("DEMO –5", "DEMO -5"),
])
def test_chuan_hoa_khong_duoc_che_lech_cung(mau, a, b):
    s = chay_cap(mau, a, b)
    points = [d for d in s["diem_lech"] if d["nhom"] == "bao_ve_truoc_chuan_hoa"]
    assert points and all(d["muc_san"] == "nghiem_trong" for d in points)
    assert any(op["phep"] == "tuong_duong_chuan_hoa" for op in s["edit_script"])


def test_chuan_khoang_trang_so_phai_theo_bo_da_khai(mau):
    text = ("DEMO 1\u00a0000", "DEMO 1 000")
    b = bo_demo()
    s = chay_cap(mau, *text, b)
    assert s["diem_lech"] and all(d["muc_san"] == "nghiem_trong" for d in s["diem_lech"])
    b["quy_tac_cung"]["dinh_dang_so"] = [{"nghin": " ", "thap_phan": ","}]
    s = chay_cap(mau, *text, b)
    assert s["diem_lech"] and all(d["muc_san"] == "hinh_thuc" for d in s["diem_lech"])


def test_nfc_tuong_duong_va_khoang_trang_ngoai_vung_van_duoc_duyet(mau):
    s = chay_cap(mau, "Bên A: Công ty DEMO A\u0301nh", "Bên A: Công ty DEMO Ánh")
    assert not s["diem_lech"]
    s = chay_cap(mau, "DEMO\tA", "DEMO A")
    assert not s["diem_lech"]


@pytest.mark.parametrize("a,b", [
    ("DEMO có  thể nhận", "DEMO có thể nhận"),
    ("DEMO   1000 VND (Bằng chữ: một nghìn đồng).", "DEMO 1000 VND (Bằng chữ: một nghìn đồng)."),
    ("DEMO    ngày 2026-10-30", "DEMO ngày 2026-10-30"),
])
def test_khoang_trang_ngoai_token_khong_tu_tao_diem_cung(mau, a, b):
    s = chay_cap(mau, a, b)
    assert not s["diem_lech"]


def test_vung_khong_nhan_dien_van_quy_tac_toan_van(mau):
    s = chay_cap(mau, "DEMO mã 00123", "DEMO mã 0123")
    assert s["tom_tat"]["so_nghiem_trong"] > 0
    assert not s["kiem_quy_tac"]["vung_bao_ve"]["da_kiem_du"]
    assert s["kiem_tra"]["quy_tac_cung"] == "chua_kiem"


def test_nhan_khong_thay_metadata_khong_tu_chung_nhan_du(mau):
    text = "\n".join(["Bên A: Công ty DEMO", "Đại diện: Ông DEMO", "Chức vụ: Giám đốc DEMO",
                      "MST: 00123", "STK: 000123", "Địa chỉ: đường DEMO", "Số hợp đồng: DEMO-01"])
    s = chay_cap(mau, text)
    k = s["kiem_quy_tac"]["vung_bao_ve"]
    assert set(k["da_nhan_dien"]["word"]) == set(qt.CAC_VUNG)
    assert not k["da_kiem_du"]


def dat_metadata(m, b, loai, a, z, ben):
    raw = m.vb(ben)["van_ban_tai_lieu"]["van_ban"]
    b["quy_tac_cung"]["vung_bao_ve"].append({"ben": ben, "loai": loai, "bat_dau": a, "ket_thuc": z,
        "nguyen_van": raw[a:z], "bam_van_ban": hs.bam(raw.encode())})


def test_metadata_gia_tri_khong_co_nhan_bao_ve_khong_can_ai(mau):
    dat_cap(mau, "DEMO công ty thuê", "DEMO công ty thuế")
    b = bo_demo()
    for ben in ("word", "ban_ky"):
        dat_metadata(mau, b, "ben_ky", 5, len(mau.vb(ben)["van_ban_tai_lieu"]["van_ban"]), ben)
    dat_bo(mau, b)
    s = snapshot_so(mau, so(mau))
    assert s["diem_lech"] and all("DC_DINH_DANH" in d["quy_tac_trung"] for d in s["diem_lech"])


@pytest.mark.parametrize("sai", ["bam", "nguyen_van", "vi_tri"])
def test_metadata_phai_khop_nguon_thuc(mau, sai):
    dat_cap(mau, "DEMO công ty thuê", "DEMO công ty thuế")
    b = bo_demo()
    dat_metadata(mau, b, "ben_ky", 5, 16, "word")
    v = b["quy_tac_cung"]["vung_bao_ve"][0]
    if sai == "bam":
        v["bam_van_ban"] = "sha256:" + "0" * 64
    elif sai == "nguyen_van":
        v["nguyen_van"] += " DEMO giả"
    else:
        v["bat_dau"] += 1
    dat_bo(mau, b)
    kiem_loi(so(mau), "DC_SAI_NGUON")


def test_nfd_ben_ky_va_phu_dinh_van_bat_du(mau):
    a = unicodedata.normalize("NFD", "Bên A: Công ty DEMO thuê\nDEMO đồng ý.")
    b = unicodedata.normalize("NFD", "Bên A: Công ty DEMO thuế\nDEMO không đồng ý.")
    s = chay_cap(mau, a, b)
    assert all(d["muc_san"] == "nghiem_trong" for d in s["diem_lech"] if d["phep"] != "kiem_noi_bo")


@pytest.mark.parametrize("thay", ["them_khoa", "tat_quy_tac", "phan_cach", "float", "ma_tien", "don_vi", "ngay"])
def test_bo_sai_khong_tu_roi_ve_mac_dinh(mau, thay):
    b = bo_demo()
    q = b["quy_tac_cung"]
    if thay == "them_khoa":
        q["tuy_y"] = "DEMO"
    elif thay == "tat_quy_tac":
        q["DC_CHU_SO"] = False
    elif thay == "phan_cach":
        q["dinh_dang_so"] = [{"nghin": ".", "thap_phan": "."}]
    elif thay == "float":
        q["phien_ban"] = 1.0
    elif thay == "ma_tien":
        q["don_vi_tien"]["VND"] = "USD"
    elif thay == "don_vi":
        q["don_vi_tien"]["đồng"] = "USD"
    else:
        q["dinh_dang_ngay"] = ["tu_doan"]
    dat_bo(mau, b)
    kiem_loi(so(mau), "DC_BO_QUY_TAC_KHONG_HOP_LE")


@pytest.mark.parametrize("muc", ["can_xem", "hinh_thuc", "nhieu_ocr"])
def test_ai_ha_nghiem_trong_bi_chan(mau, muc):
    s = chay_cap(mau, "MST: 00123 DEMO", "MST: 00124 DEMO")
    goc = deepcopy(s)
    with pytest.raises(LoiNghiepVu) as e:
        qt.ap_muc_ai(s, [{"ma_diem": d["ma_diem"], "muc": muc, "ly_do": "DEMO AI đề nghị hạ"} for d in s["diem_lech"]])
    assert e.value.ma == "DC_HA_MUC_TRAI_QUY_TAC" and s == goc


@pytest.mark.parametrize("thay", ["muc_san", "quy_tac_trung", "can_cu_quy_tac", "vung_bao_ve", "xoa_diem", "tu_bam_lai"])
def test_khong_the_sua_san_nhat_ky_ke_ca_tu_bam_lai(mau, thay):
    goc = chay_cap(mau, "MST: 00123 DEMO", "MST: 00124 DEMO")
    s = deepcopy(goc)
    if thay == "xoa_diem":
        s["diem_lech"] = []
    elif thay == "tu_bam_lai":
        s["diem_lech"][0]["muc_san"] = s["diem_lech"][0]["muc"] = "nhieu_ocr"
        s["diem_lech"][0]["quy_tac_trung"] = []
        s["nhat_ky_quy_tac"] = [qt._dau_diem(d) for d in s["diem_lech"]]
        s["bam_nhat_ky_quy_tac"] = hs.bam(hs.json_bytes(s["nhat_ky_quy_tac"]))
    else:
        s["diem_lech"][0][thay] = "nhieu_ocr" if thay == "muc_san" else []
    with pytest.raises(LoiNghiepVu) as e:
        qt.kiem_bat_bien(s, goc)
    assert e.value.ma == "DC_SAI_NGUON"


def test_ai_chi_nang_muc_va_giu_nhat_ky(mau):
    s = chay_cap(mau, "DEMO thuê", "DEMO thuế")
    out = qt.ap_muc_ai(s, [{"ma_diem": d["ma_diem"], "muc": "nghiem_trong", "ly_do": "DEMO có căn cứ"} for d in s["diem_lech"]])
    assert out["nhat_ky_quy_tac"] == s["nhat_ky_quy_tac"]
    assert all(d["muc"] == "nghiem_trong" and d["muc_san"] == "can_xem" for d in out["diem_lech"])
    assert qt.kiem_bat_bien(out, s)


def test_ap_lai_khong_duoc_reset_muc_ai_da_nang(mau):
    s = chay_cap(mau, "DEMO thuê", "DEMO thuế")
    out = qt.ap_muc_ai(s, [{"ma_diem": d["ma_diem"], "muc": "nghiem_trong", "ly_do": "DEMO"} for d in s["diem_lech"]])
    assert qt.ap_quy_tac(out) == out
    lower = deepcopy(out)
    lower["diem_lech"][0]["muc"] = "can_xem"
    with pytest.raises(LoiNghiepVu) as e:
        qt.kiem_bat_bien(lower, out)
    assert e.value.ma == "DC_SAI_NGUON"


def test_cum_tien_khong_duoc_noi_cheo_o_hay_dong(mau):
    for sep in ("\n", "\t", " | "):
        s = chay_cap(mau, f"DEMO 1000 VND{sep}Bằng chữ: một nghìn đồng.")
        ds = s["kiem_quy_tac"]["tien_bang_chu"]["danh_sach"]
        assert ds and all(not x["da_kiem_du"] and x["khop"] is None for x in ds)


def test_tien_le_serialize_chinh_xac_va_so_lon_khong_float(mau):
    text = "DEMO 123456789012345678901234567890,01 USD (Bằng chữ: không phân tích được USD)."
    s = chay_cap(mau, text)
    ds = s["kiem_quy_tac"]["tien_bang_chu"]["danh_sach"]
    assert ds[0]["tien_bang_so"] == {"so": "123456789012345678901234567890.01", "tien_te": "USD"}
    assert ds[0]["tien_bang_chu"] is None and not ds[0]["da_kiem_du"]
    def khong_float(x):
        if isinstance(x, dict):
            for v in x.values():
                khong_float(v)
        elif isinstance(x, list):
            for v in x:
                khong_float(v)
        else:
            assert type(x) is not float
    khong_float(ds)


def test_ma_tien_chua_khai_van_bao_lech_khong_doan(mau):
    s = chay_cap(mau, "DEMO 1000 CHF", "DEMO 1000 CAD")
    assert all(d["muc_san"] == "nghiem_trong" for d in s["diem_lech"] if d["phep"] != "kiem_noi_bo")
    assert all(x["tien_bang_so"] is None for x in s["kiem_quy_tac"]["tien_bang_chu"]["danh_sach"])


def test_ky_hieu_tien_chi_nhan_khi_duoc_khai_tuong_minh(mau):
    b = bo_demo()
    b["quy_tac_cung"]["don_vi_tien"]["$"] = "USD"
    s = chay_cap(mau, "DEMO 1000 $ (Bằng chữ: một nghìn đô la Mỹ).", bo=b)
    kt, = s["kiem_quy_tac"]["tien_bang_chu"]["danh_sach"]
    assert kt["khop"] is True and kt["tien_bang_so"] == {"so": 1000, "tien_te": "USD"}


def test_ngay_cau_truc_luu_iso_va_khong_doan(mau):
    s = chay_cap(mau, "DEMO ngày 2026-10-30", "DEMO ngày 2026-10-31")
    dates = [v["ngay"] for d in s["diem_lech"] for cc in d["can_cu_quy_tac"] for v in cc.get("ngay", [])]
    assert set(dates) == {"2026-10-30", "2026-10-31"}
    assert tc.doc_ngay("2026-02-30") is None
    assert tc.doc_ngay("10/11/2026", ["DD/MM/YYYY", "MM/DD/YYYY"]) is None
    assert tc.doc_ngay("30/10/2026", ["DD/MM/YYYY"]) == "2026-10-30"


@pytest.mark.parametrize("text", ["DEMO ngày 2026-02-30", "DEMO ngày 2026-1-2", "DEMO ngày 1/2/2026", "DEMO thời hạn ba ngày"])
def test_ngay_thieu_chuan_hoac_bang_loi_khong_tu_nhan_du(mau, text):
    s = chay_cap(mau, text)
    assert not s["kiem_quy_tac"]["so_va_ngay"]["da_kiem_du"]


def test_nhan_dien_du_metadata_va_tien_moi_dat_hang_muc(mau):
    lines = ["Bên A: Công ty DEMO", "Đại diện: Ông DEMO", "Chức vụ: Giám đốc DEMO",
             "MST: 00123", "STK: 000123", "Địa chỉ: đường DEMO", "Số hợp đồng: DEMO-01"]
    dat_cap(mau, "\n".join(lines + ["DEMO 1000 VND (Bằng chữ: một nghìn đồng).", "DEMO ngày 2026-10-30"]))
    b = bo_demo()
    for ben in ("word", "ban_ky"):
        raw = mau.vb(ben)["van_ban_tai_lieu"]["van_ban"]
        for loai, line in zip(qt.CAC_VUNG, lines):
            a = raw.index(line)
            dat_metadata(mau, b, loai, a, a + len(line), ben)
    dat_bo(mau, b)
    s = snapshot_so(mau, so(mau))
    assert s["kiem_tra"]["quy_tac_cung"] == "dat"
    assert all(s["kiem_quy_tac"][k]["da_kiem_du"] for k in ("vung_bao_ve", "so_va_ngay", "tien_bang_chu"))
    assert not s["da_kiem_du"] and s["ket_luan"] is None and s["de_nghi_chan"]


def test_tham_chieu_vung_quay_lai_nguyen_van_khong_nhan_ca_dong_vao_diem(mau):
    s = chay_cap(mau, "Bên A: Công ty DEMO thuê", "Bên A: Công ty DEMO thuế")
    for d in s["diem_lech"]:
        for v in d["vung_bao_ve"]:
            raw = s["van_ban"][v["ben"]]["van_ban_tai_lieu"]["van_ban"]
            assert "nguyen_van" not in v
            assert hs.bam(raw.encode()) == v["bam_van_ban"]
            assert hs.bam(raw[v["bat_dau"]:v["ket_thuc"]].encode()) == v["bam_vung"]


def test_tran_byte_tinh_ca_nhat_ky_khong_cat_diem(mau):
    s = chay_cap(mau, "MST: 00123 DEMO", "MST: 00124 DEMO")
    for k in ("thuat_toan_quy_tac", "nhat_ky_quy_tac", "bam_nhat_ky_quy_tac"):
        s.pop(k)
    s["diem_lech"] = [d for d in s["diem_lech"] if d["phep"] != "kiem_noi_bo"]
    with pytest.raises(LoiNghiepVu) as e:
        qt.ap_quy_tac(s, toi_da_byte=100)
    assert e.value.ma == "DC_QUA_GIOI_HAN"


def test_loi_la_dc5_khong_lo_noi_dung_ra_log(mau, monkeypatch, capsys):
    dat_cap(mau, "DEMO số 001234", "DEMO số 001235")
    pb = mau.chay()["ket_qua"]
    def loi_co_noi_dung(*a, **kw):
        raise RuntimeError("DEMO Công ty Ánh: 001234 VND")
    monkeypatch.setattr(qt, "doc_so", loi_co_noi_dung)
    kiem_loi(so(mau, pb), "DC_LOI_XU_LY")
    log = capsys.readouterr()
    assert all(t not in log.out + log.err for t in ("Công ty Ánh", "001234", "RuntimeError"))


@pytest.mark.parametrize("x", [None, {}, {"diem_lech": []}])
def test_nhat_ky_thieu_sai_tra_loi_nguon(x):
    with pytest.raises(LoiNghiepVu) as e:
        qt.kiem_bat_bien(x)
    assert e.value.ma == "DC_SAI_NGUON"


def test_quy_tac_cung_null_khong_coi_nhu_bo_cu(mau):
    b = bo_demo()
    b["quy_tac_cung"] = None
    dat_bo(mau, b)
    kiem_loi(so(mau), "DC_BO_QUY_TAC_KHONG_HOP_LE")


def test_khong_log_noi_dung_khong_ghi_dia_khong_goi_mang(mau, monkeypatch, capsys):
    dat_cap(mau, "MST: 00123 DEMO Ánh", "MST: 00124 DEMO Anh")
    pb = mau.chay()["ket_qua"]
    import builtins
    import socket
    def cam(*a, **kw):
        pytest.fail("Không được ghi đĩa hoặc gọi mạng trong DC-5")
    old_open = builtins.open
    def chi_doc(file, mode="r", *args, **kwargs):
        if any(k in mode for k in "wax+"):
            cam()
        return old_open(file, mode, *args, **kwargs)
    with monkeypatch.context() as mp:
        mp.setattr(builtins, "open", chi_doc)
        mp.setattr(socket, "create_connection", cam)
        r = so(mau, pb)
    s = snapshot_so(mau, r)
    assert s["tom_tat"]["so_nghiem_trong"] > 0
    log = capsys.readouterr()
    assert all(x not in log.out + log.err for x in ("00123", "00124", "Ánh", "MST:"))


def test_huy_trong_quy_tac_khong_tai_snapshot(mau, monkeypatch):
    pb = mau.chay()["ket_qua"]
    tai = mau.core.so_tai
    def huy(*a, **kw):
        raise ViecDaHuy()
    monkeypatch.setattr(qt, "ap_quy_tac", huy)
    r = so(mau, pb)
    assert r["trang_thai"] == "HUY" and r["ket_qua"] is None
    assert mau.core.so_tai == tai
    assert any(x.gia_tri["trang_thai"] == "can_thu_lai" for x in mau.cac_luot())


def test_vuot_tran_tinh_ca_diem_kiem_noi_bo(mau):
    dat_cap(mau, "DEMO 1000 VND (Bằng chữ: hai nghìn đồng).\nDEMO 2000 VND (Bằng chữ: ba nghìn đồng).")
    mau.cau_hinh["diem_lech_toi_da"] = 1
    mau.dat_cau_hinh()
    kiem_loi(so(mau), "DC_QUA_GIOI_HAN")
