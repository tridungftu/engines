"""Hồi quy kiểm độc lập TC-7; chỉ DEMO, đã kiểm bằng Core giả (CoreGia)."""

from copy import deepcopy

import pytest

from ho_tro_tc_7 import BoTraLoi, TRUONG
from test_tc_7 import bo_mau_thuan, ket_qua, khong_can_cu


DAU = "Công ty DEMO Ánh Dương\nĐiều 1. Nghĩa vụ DEMO\n"
THUC_THE = {x: {"loai": "khoan_vay", "ma": "DEMO-VAY-" + x, "gia_tri": "DEMO-VAY-" + x}
            for x in ("A", "B")}


def bo_quan_he(cau, *, hien_thi, truong=None, thuc_the="A", gia_tri=None, bang=False,
               don_vi=None, kieu="so_tien", cac_o=None):
    """Dựng nguồn thật/offset thật độc lập validator; profile có thể gán sai quan hệ."""
    bo = BoTraLoi(van_ban=DAU + cau)
    if bang:
        o = []
        con_tro = len(DAU)
        for cot, chu in enumerate(cac_o or [cau]):
            a = bo.van_ban.index(chu, con_tro)
            o.append({"hang": 0, "cot": cot, "gop_hang": 1, "gop_cot": 1, "van_ban": chu,
                      "bat_dau": a, "ket_thuc": a + len(chu)})
            con_tro = a + len(chu)
        pb = deepcopy(bo.pb_vb)
        pb["van_ban_tai_lieu"]["khoi"] = [
            {"loai": "doan", "van_ban": DAU, "hop": None},
            {"loai": "bang", "bat_dau": len(DAU), "ket_thuc": len(bo.van_ban),
             "hop": None, "hang_tieu_de": [], "o": o}]
        bo.nguon_co_cau_truc(pb)
    f = deepcopy(truong or TRUONG[0])
    if kieu == "so_tien":
        dv = don_vi or hien_thi.rsplit(" ", 1)[-1]
        v = gia_tri if gia_tri is not None else {"so": int(hien_thi.split(" ", 1)[0].replace(".", "")), "tien_te": dv}
        q = "tien_nhom_ba"
    else:
        dv, v = don_vi, gia_tri if gia_tri is not None else hien_thi
        q = "ngay_iso" if kieu == "ngay" else "so_chuan"
    b = bo.can_cu(cau=cau, thuc_the=THUC_THE[thuc_the], hien_thi=hien_thi)
    b.update(truong=f["ma"], kieu=kieu, gia_tri=v, don_vi=dv, quy_tac=q)
    return bo, b, f


def tra_loi(bo, b, f, tang):
    e = b["thuc_the"]
    bo.nhan_soan(tang, bang=[b], fields=[f], sua=lambda d: d.update(
        thuc_the=[deepcopy(e)], cau_hoi=f'{f["ten"]} khoản vay {e["gia_tri"]} là bao nhiêu?'))
    if tang > 1:
        bo.chuan_bi_soan()
        bo.local_soan()
    return bo.soan()


@pytest.mark.parametrize("tang", [1, 2, 3])
@pytest.mark.parametrize("bang,cau,thuc_the,hien,dat", [
    (False, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND.\nKhoản vay DEMO-VAY-B có giá trị 2.000.000 USD.", "B", "1.000.000 VND", False),
    (False, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND.\nKhoản vay DEMO-VAY-B có giá trị 2.000.000 USD.", "A", "2.000.000 USD", False),
    (False, "Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD.\nKhoản vay DEMO-VAY-A có giá trị 1.000.000 VND.", "B", "1.000.000 VND", False),
    (True, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND, khoản vay DEMO-VAY-B có giá trị 2.000.000 USD.", "A", "2.000.000 USD", False),
    (True, "Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, khoản vay DEMO-VAY-A có giá trị 1.000.000 VND.", "B", "1.000.000 VND", False),
    (False, "Giá trị 1.000.000 VND của khoản vay DEMO-VAY-A.", "A", "1.000.000 VND", False),
    (False, "Khoản vay DEMO-VAY-A\nGiá trị 1.000.000 VND.", "A", "1.000.000 VND", False),
    (False, "Khoản vay DEMO-VAY-A; Giá trị 1.000.000 VND.", "A", "1.000.000 VND", False),
    (False, "Khoản vay DEMO-VAY-A. Giá trị 1.000.000 VND.", "A", "1.000.000 VND", False),
    (False, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND, khoản vay DEMO-VAY-B 2.000.000 USD.", "B", "2.000.000 USD", False),
    (False, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND.\nKhoản vay DEMO-VAY-B có giá trị 2.000.000 USD.", "A", "1.000.000 VND", True),
    (False, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND.\nKhoản vay DEMO-VAY-B có giá trị 2.000.000 USD.", "B", "2.000.000 USD", True),
    (True, "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND, khoản vay DEMO-VAY-B có giá trị 2.000.000 USD.", "B", "2.000.000 USD", True),
    (True, "Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, khoản vay DEMO-VAY-A có giá trị 1.000.000 VND.", "A", "1.000.000 VND", True),
    (False, "Giá trị khoản vay DEMO-VAY-A: 1.000.000 VND.", "A", "1.000.000 VND", True),
])
def test_gia_tri_phai_thuoc_thuc_the_gan_nhat_truoc_no(tang, bang, cau, thuc_the, hien, dat):
    f = {**TRUONG[0], "don_vi": hien.rsplit(" ", 1)[-1]}
    bo, b, f = bo_quan_he(cau, hien_thi=hien, truong=f, thuc_the=thuc_the, bang=bang)
    ra = tra_loi(bo, b, f, tang)
    if dat:
        r = ket_qua(bo, ra)
        assert r["co_can_cu"] and r["nhan"] == ("xanh" if tang == 1 else "vang")
        assert r["khang_dinh"][0]["thuc_the"] == THUC_THE[thuc_the]
    else:
        assert "QUAN_HE_GIA_TRI_KHONG_DAT" in khong_can_cu(bo, ra)["ly_do"]


@pytest.mark.parametrize("tang", [2, 3])
@pytest.mark.parametrize("noi", ["\t", " | ", " "])
@pytest.mark.parametrize("cung_o", [False, True])
def test_ranh_gioi_o_bang_thuc_khong_ke_thua_thuc_the_tu_o_truoc(tang, noi, cung_o):
    o1 = "Khoản vay DEMO-VAY-A"
    o2 = ("Khoản vay DEMO-VAY-A " if cung_o else "") + "có giá trị 1.000.000 VND."
    cau = o1 + noi + o2
    bo, b, f = bo_quan_he(cau, hien_thi="1.000.000 VND", bang=True, cac_o=[o1, o2])
    ra = tra_loi(bo, b, f, tang)
    if cung_o:
        assert ket_qua(bo, ra)["nhan"] == "vang"
    else:
        khong_can_cu(bo, ra)


NGAY = [("ngay_ky", "Ngày ký", "2026-10-30"),
        ("ngay_hieu_luc", "Ngày hiệu lực", "2026-11-01"),
        ("han_tra", "Hạn trả", "2027-10-30")]


@pytest.mark.parametrize("tang", [1, 2, 3])
@pytest.mark.parametrize("truong", NGAY)
@pytest.mark.parametrize("hien", [x[2] for x in NGAY])
def test_ba_ngay_trong_mot_cau_khong_duoc_gan_sai_truong(tang, truong, hien):
    ma, ten, ngay_dung = truong
    cau = "Khoản vay DEMO-VAY-A ký ngày 2026-10-30, hiệu lực ngày 2026-11-01, hạn trả ngày 2027-10-30."
    f = {"ma": ma, "ten": ten, "kieu": "ngay", "don_vi": None}
    bo, b, f = bo_quan_he(cau, hien_thi=hien, truong=f, kieu="ngay")
    ra = tra_loi(bo, b, f, tang)
    if hien == ngay_dung:
        assert ket_qua(bo, ra)["nhan"] == ("xanh" if tang == 1 else "vang")
    else:
        assert "QUAN_HE_GIA_TRI_KHONG_DAT" in khong_can_cu(bo, ra)["ly_do"]


@pytest.mark.parametrize("tang", [1, 2, 3])
@pytest.mark.parametrize("cau", [
    "Khoản vay DEMO-VAY-A ký ngày 2026-10-30, hạn trả ngày 2027-10-30.",
    "Khoản vay DEMO-VAY-A: 2026-10-30; hạn trả ngày 2027-10-30.",
    "Khoản vay DEMO-VAY-A: 2026-10-30, hạn trả ngày 2027-10-30.",
])
def test_nhan_truong_dung_phai_dung_truoc_gia_tri(tang, cau):
    f = {"ma": "han_tra", "ten": "Hạn trả", "kieu": "ngay", "don_vi": None}
    bo, b, f = bo_quan_he(cau, hien_thi="2026-10-30", truong=f, kieu="ngay")
    khong_can_cu(bo, tra_loi(bo, b, f, tang))


@pytest.mark.parametrize("tang", [1, 2, 3])
@pytest.mark.parametrize("nguon,so", [
    ("10%", 10), ("10 %", 10), ("10‰", 10), ("10 ‰", 10),
    ("5 triệu VND", 5), ("5 triệu đồng", 5), ("5 nghìn", 5), ("5 ngàn", 5),
    ("5 tỷ VND", 5), ("5 tỉ", 5), ("5 đồng", 5), ("5 VND", 5),
    ("5 USD", 5), ("5 EUR", 5), ("5m2", 5), ("5 m3", 5),
    ("5 m²", 5), ("5 m³", 5), ("5 tấn", 5), ("5 kg", 5), ("5\u00a0kg", 5),
    ("5 kWh", 5), ("5 lượt", 5), ("5 (triệu VND)", 5), ("5 phần trăm", 5),
])
def test_so_tran_khong_duoc_bo_don_vi_hoac_quy_mo(tang, nguon, so):
    cau = f"Khoản vay DEMO-VAY-A có giá trị {nguon}."
    f = {"ma": "gia_tri", "ten": "Giá trị", "kieu": "so", "don_vi": None}
    bo, b, f = bo_quan_he(cau, hien_thi=str(so), truong=f, gia_tri=so, kieu="so")
    assert "QUAN_HE_GIA_TRI_KHONG_DAT" in khong_can_cu(bo, tra_loi(bo, b, f, tang))["ly_do"]


@pytest.mark.parametrize("tang", [1, 2, 3])
@pytest.mark.parametrize("don_vi,cach", [("%", ""), ("%", " "), ("‰", ""), ("‰", " "),
    ("triệu VND", " "), ("nghìn", " "), ("tỷ VND", " "), ("VND", " "),
    ("USD", " "), ("EUR", " "), ("m2", ""), ("m3", " "), ("kg", " "), (None, "")])
def test_so_giu_day_du_don_vi_khai_tuong_minh_con_nhan_dung(tang, don_vi, cach):
    hien = "10" + cach + (don_vi or "")
    cau = f"Khoản vay DEMO-VAY-A có giá trị {hien}."
    f = {"ma": "gia_tri", "ten": "Giá trị", "kieu": "so", "don_vi": don_vi}
    bo, b, f = bo_quan_he(cau, hien_thi=hien, truong=f, gia_tri=10, don_vi=don_vi, kieu="so")
    r = ket_qua(bo, tra_loi(bo, b, f, tang))
    assert r["co_can_cu"] and r["nhan"] == ("xanh" if tang == 1 else "vang")
    assert r["khang_dinh"][0]["don_vi"] == don_vi and hien in r["tra_loi"]


@pytest.mark.parametrize("tang", [1, 2, 3])
def test_khong_duoc_giu_quy_mo_nhung_bo_tien_te(tang):
    f = {"ma": "gia_tri", "ten": "Giá trị", "kieu": "so", "don_vi": "triệu"}
    bo, b, f = bo_quan_he("Khoản vay DEMO-VAY-A có giá trị 5 triệu VND.",
                          hien_thi="5 triệu", truong=f, gia_tri=5, don_vi="triệu", kieu="so")
    khong_can_cu(bo, tra_loi(bo, b, f, tang))


@pytest.mark.parametrize("tang", [2, 3])
@pytest.mark.parametrize("trang_thai,moc,diem,nguong,ly_do", [
    ("tu_choi", None, 0.95, "da_do", "BANG_CHUNG_BI_TU_CHOI"),
    ("cho_duyet", None, 0.95, "da_do", "CHUA_DUYET"),
    ("da_duyet", "2026-12-01T00:00:00+07:00", 0.95, "da_do", "CHUA_DUYET"),
    ("da_duyet", "2026-10-30T00:00:00+07:00", 0.1, "da_do", "DUOI_NGUONG_TIN_CAY"),
    ("da_duyet", "2026-10-30T00:00:00+07:00", 0.95, None, "THIEU_NGUONG_DA_DO"),
    ("da_duyet", "2026-10-30T00:00:00+07:00", 0.95, "chua_do", "THIEU_NGUONG_DA_DO"),
    ("da_duyet", "2026-10-30T00:00:00+07:00", 0.95, "chua_duyet", "THIEU_NGUONG_DA_DO"),
])
def test_tang_hai_ba_phai_xet_duyet_do_tin_cay_va_nguong(tang, trang_thai, moc, diem, nguong, ly_do):
    bo = BoTraLoi()
    b = bo.can_cu()
    b.update(trang_thai_duyet=trang_thai, moc_duyet=moc, do_tin_cay=diem)
    bo.nhan_soan(tang, bang=[b], fields=[TRUONG[0]])
    if nguong is None:
        bo.profile["nguong_tin_cay"] = None
    elif nguong == "chua_duyet":
        bo.profile["nguong_tin_cay"]["da_duyet"] = False
    else:
        bo.profile["nguong_tin_cay"]["trang_thai"] = nguong
    bo.chuan_bi_soan()
    bo.local_soan()
    ra = bo.soan()
    r = khong_can_cu(bo, ra) if trang_thai == "tu_choi" else ket_qua(bo, ra)
    assert ly_do in r["ly_do"]
    if trang_thai != "tu_choi":
        assert r["co_can_cu"] and r["nhan"] == "vang" and r["can_duyet"]
        assert r["canh_bao"] and not r["de_nghi_k5"]["da_duyet"]
    else:
        assert not r["de_nghi_k5"]["du_lieu_moi"] and not r["co_mau_thuan"]


def test_tang_mot_tu_choi_khong_co_can_cu():
    bo = BoTraLoi()
    b = bo.can_cu()
    b.update(trang_thai_duyet="tu_choi", moc_duyet=None)
    bo.nhan_soan(bang=[b], fields=[TRUONG[0]])
    assert "BANG_CHUNG_BI_TU_CHOI" in khong_can_cu(bo, bo.soan())["ly_do"]


@pytest.mark.parametrize("tang", [1, 2, 3])
@pytest.mark.parametrize("giu_khoang_trang", [False, True])
@pytest.mark.parametrize("nguon,hien,dv", [("10%", "10", None),
    ("5 triệu VND", "5", None), ("5 triệu VND", "5 triệu", "triệu")])
def test_quote_cat_truoc_don_vi_khong_duoc_lach_kiem_so_nguyen_cum(tang, giu_khoang_trang, nguon, hien, dv):
    cau = f"Khoản vay DEMO-VAY-A có giá trị {nguon}."
    f = {"ma": "gia_tri", "ten": "Giá trị", "kieu": "so", "don_vi": dv}
    bo, b, f = bo_quan_he(cau, hien_thi=hien, truong=f, gia_tri=int(hien.split()[0]), don_vi=dv, kieu="so")
    b["ket_thuc"] = b["vi_tri_gia_tri"][1]
    if giu_khoang_trang and bo.van_ban[b["ket_thuc"]].isspace():
        b["ket_thuc"] += 1
    b["cau"] = b["cau"][:b["ket_thuc"] - b["bat_dau"]]
    khong_can_cu(bo, tra_loi(bo, b, f, tang))


@pytest.mark.parametrize("tang", [1, 2, 3])
def test_khong_suy_tu_la_la_tu_noi_giua_nhan_truong_va_gia_tri(tang):
    cau = "Khoản vay DEMO-VAY-A có giá trị, phí bảo lãnh 1.000.000 VND."
    bo, b, f = bo_quan_he(cau, hien_thi="1.000.000 VND")
    khong_can_cu(bo, tra_loi(bo, b, f, tang))


@pytest.mark.parametrize("tang", [1, 2, 3])
def test_hai_truong_cung_nhan_khong_duoc_chon_theo_thu_tu_mang(tang):
    bo = BoTraLoi()
    b1 = bo.can_cu(truong="ngay")
    b2 = deepcopy(b1)
    b2["truong"] = "han_tra"
    fields = [{"ma": ma, "ten": "Ngày", "kieu": "ngay", "don_vi": None} for ma in ("ngay", "han_tra")]
    bo.nhan_soan(tang, bang=[b1, b2], fields=fields)
    if tang > 1:
        bo.chuan_bi_soan()
        bo.local_soan()
    khong_can_cu(bo, bo.soan())


@pytest.mark.parametrize("tang", [1, 2, 3])
def test_do_tin_cay_bang_nguong_van_du_dieu_kien(tang):
    bo = BoTraLoi()
    b = bo.can_cu()
    b["do_tin_cay"] = 0.9
    bo.nhan_soan(tang, bang=[b], fields=[TRUONG[0]])
    if tang > 1:
        bo.chuan_bi_soan()
        bo.local_soan()
    r = ket_qua(bo, bo.soan())
    assert r["co_can_cu"] and r["ly_do"] == [] and not r["canh_bao"]
    assert r["nhan"] == ("xanh" if tang == 1 else "vang")


@pytest.mark.parametrize("tang", [1, 2, 3])
def test_bang_chung_tu_choi_khong_duoc_giu_lam_mot_phia_mau_thuan(tang):
    bo = bo_mau_thuan(tang)
    bo.profile["bang_chung"][1].update(trang_thai_duyet="tu_choi", moc_duyet=None)
    # Tầng 1 có kiểm quan hệ riêng với dữ liệu đã nhận, vẫn từ chối kết quả.
    if tang > 1:
        bo.chuan_bi_soan()
        bo.local_soan()
    r = khong_can_cu(bo, bo.soan())
    assert not r["co_mau_thuan"] and r["mau_thuan"] == []
