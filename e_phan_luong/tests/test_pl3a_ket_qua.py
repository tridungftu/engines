"""Kiểm hợp đồng PL-3A bằng dữ liệu DEMO, không cần Core hay mô-đun khác."""
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))

from e_phan_luong import ket_qua, kieu, loi


def dong_demo(**thay):
    dong = {
        "ma_luot": "PL-DEMO-0001", "ma": "PC-DEMO-0001",
        "khau": "ktt_duyet", "ket_qua": "dat",
        "so_tien_sai": {"so": "0", "tien_te": "VND"}, "loai_dung": None,
    }
    dong.update(thay)
    return dong


def tep_demo(dong=None, **thay):
    tep = {
        "phien_ban": 1, "ma_module": "demo_thanh_toan",
        "ket_qua": [dong_demo()] if dong is None else dong,
    }
    tep.update(thay)
    return tep


def ma_hoa(tep):
    return json.dumps(tep, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def kiem_loi(ham, *args, ma="DU_LIEU_KHONG_HOP_LE"):
    with pytest.raises(loi.LoiNghiepVu) as bat:
        ham(*args)
    assert bat.value.ma == ma
    assert bat.value.thong_diep == loi.CAU_LOI[ma]
    assert bat.value.thu_lai_duoc is False
    assert "PC-DEMO" not in str(bat.value)


def nguong_demo():
    return kieu.Nguong(
        pm=kieu.Tien(Decimal("5000000"), "VND"),
        te=kieu.Tien(Decimal("3000000"), "VND"),
        sad=kieu.Tien(Decimal("250000"), "VND"),
    )


@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"])
def test_doc_du_ba_ket_qua_va_loai_dung(bom):
    ds = [dong_demo(), dong_demo(
        ma="PC-DEMO-0002", ket_qua="sai", loai_dung="thanh_toan_ncc",
        so_tien_sai={"so": "-1000000000000.123456", "tien_te": "VND"},
    ), dong_demo(ma="PC-DEMO-0003", ket_qua="khong_kiem", so_tien_sai=None)]
    kq = ket_qua.doc_ket_qua_json(bom + ma_hoa(tep_demo(ds)))
    assert isinstance(kq, ket_qua.KetQuaTep)
    assert kq.ma_module == "demo_thanh_toan"
    assert kq.nguong is None
    assert kq.so_trung_trong_tep == 0
    assert isinstance(kq.dong, tuple)
    assert [d.chi_so for d in kq.dong] == [0, 1, 2]
    assert [d.ket_qua for d in kq.dong] == ["dat", "sai", "khong_kiem"]
    assert kq.dong[0].ma_luot == "PL-DEMO-0001"
    assert kq.dong[0].khau == "ktt_duyet"
    assert kq.dong[1].so_tien_sai == kieu.Tien(Decimal("-1000000000000.123456"), "VND")
    assert kq.dong[1].loai_dung == "thanh_toan_ncc"
    assert kq.dong[2].so_tien_sai is None


def test_doc_so_json_bang_decimal_va_giu_nguyen_nguong():
    du_lieu = b'''{"phien_ban":1,"ma_module":"demo_thanh_toan",
      "nguong":{"pm":{"so":5000000.123456,"tien_te":"VND"}},
      "ket_qua":[{"ma_luot":"PL-DEMO-1","ma":"PC-DEMO-1","khau":"ktt_duyet",
        "ket_qua":"sai","so_tien_sai":{"so":1000000000000.123456,"tien_te":"USD"}}]}'''
    with localcontext() as ctx:
        ctx.prec = 6
        kq = ket_qua.doc_ket_qua_json(du_lieu)
    assert kq.dong[0].so_tien_sai == kieu.Tien(Decimal("1000000000000.123456"), "USD")
    assert kq.nguong == {"pm": {"so": Decimal("5000000.123456"), "tien_te": "VND"}}


def test_nguong_tuy_chon_chuyen_cho_phan_ghep_kiem():
    ng = {"pm": {"so": "5000000", "tien_te": "VND"},
          "te": {"so": "3000000", "tien_te": "VND"},
          "sad": {"so": "250000", "tien_te": "VND"}}
    assert ket_qua.doc_ket_qua_json(ma_hoa(tep_demo(nguong=ng))).nguong == ng
    # Bộ đọc chưa có Cài đặt bước; phần ghép mới kiểm thiếu cả hai nguồn ngưỡng.
    assert ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([
        dong_demo(ket_qua="sai"),
    ]))).nguong is None


@pytest.mark.parametrize("trang_thai", ["dat", "khong_kiem"])
def test_khong_sai_duoc_thieu_so_tien_sai_va_loai_dung(trang_thai):
    dong = dong_demo(ket_qua=trang_thai)
    del dong["so_tien_sai"]
    del dong["loai_dung"]
    kq = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong])))
    assert kq.dong[0].so_tien_sai is None
    assert kq.dong[0].loai_dung is None


def test_lo_rong_hop_le():
    assert ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([]))).dong == ()


@pytest.mark.parametrize("khoa", ["phien_ban", "ma_module", "ket_qua"])
def test_thieu_truong_tep(khoa):
    tep = tep_demo()
    del tep[khoa]
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep))


@pytest.mark.parametrize("khoa,gia_tri", [
    ("phien_ban", None), ("phien_ban", True), ("phien_ban", 1.0),
    ("phien_ban", "1"), ("phien_ban", 2),
    ("ma_module", None), ("ma_module", []), ("ma_module", ""),
    ("ma_module", "DEMO"), ("ma_module", "demo-module"),
    ("ma_module", "1demo"), ("ma_module", "d" * 32),
    ("ket_qua", None), ("ket_qua", {}), ("ket_qua", "dat"),
    ("nguong", []), ("nguong", "DEMO"),
])
def test_sai_truong_tep(khoa, gia_tri):
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo(**{khoa: gia_tri})))


@pytest.mark.parametrize("khoa", ["ma_luot", "ma", "khau", "ket_qua"])
def test_thieu_truong_dong(khoa):
    dong = dong_demo()
    del dong[khoa]
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([dong])))


@pytest.mark.parametrize("khoa,gia_tri", [
    ("ma_luot", None), ("ma_luot", ""), ("ma_luot", "PL-DEMO\n"),
    ("ma", True), ("ma", ""), ("ma", "PC-DEMO\x7f"), ("ma", "d" * 121),
    ("khau", None), ("khau", "  "), ("khau", "d" * 41),
    ("ket_qua", "la"), ("ket_qua", "DAT"), ("ket_qua", None),
    ("ket_qua", []), ("ket_qua", {}),
    ("loai_dung", ""), ("loai_dung", 3), ("loai_dung", "Loai-DEMO"),
    ("loai_dung", "d" * 41),
])
def test_sai_truong_dong(khoa, gia_tri):
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([dong_demo(**{khoa: gia_tri})])))


@pytest.mark.parametrize("dong", [None, [], 1, "DEMO"])
def test_dong_khong_phai_object(dong):
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([dong])))


def test_bien_do_dai_ma():
    kq = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([
        dong_demo(ma="d" * 120, khau="d" * 40, loai_dung="d" * 40),
    ], ma_module="d" * 31)))
    assert len(kq.dong) == 1


@pytest.mark.parametrize("thieu", [True, False])
def test_sai_bat_buoc_so_tien_sai(thieu):
    dong = dong_demo(ket_qua="sai", so_tien_sai=None)
    if thieu:
        del dong["so_tien_sai"]
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([dong])))


@pytest.mark.parametrize("tien", [
    {"so": "1"}, {"so": "1", "tien_te": None},
    {"so": "1", "tien_te": "vnd"}, {"so": "1", "tien_te": ""},
    {"so": "1", "tien_te": "VNDD"}, {"so": "1", "tien_te": 1},
    {"tien_te": "VND"}, {"so": None, "tien_te": "VND"},
    {"so": True, "tien_te": "VND"}, {"so": [], "tien_te": "VND"},
    {"so": "1e3", "tien_te": "VND"}, {"so": "NaN", "tien_te": "VND"},
    {"so": "Infinity", "tien_te": "VND"}, {"so": "1,000", "tien_te": "VND"},
    {"so": " 1 ", "tien_te": "VND"}, {"so": "0.0000001", "tien_te": "VND"},
    {"so": "1000000000000000000", "tien_te": "VND"}, 1000000, [],
])
def test_so_tien_sai_khong_hop_le(tien):
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([
        dong_demo(ket_qua="sai", so_tien_sai=tien),
    ])))


@pytest.mark.parametrize("so", [0, -1, 1000000000000, "0.000001", "-999999999999999999.999999"])
def test_so_tien_hop_le(so):
    kq = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([
        dong_demo(ket_qua="sai", so_tien_sai={"so": so, "tien_te": "USD"}),
    ])))
    assert kq.dong[0].so_tien_sai == kieu.Tien(Decimal(so), "USD")


@pytest.mark.parametrize("trang_thai", ["dat", "khong_kiem"])
def test_tien_da_gui_van_phai_hop_le_du_khong_sai(trang_thai):
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([
        dong_demo(ket_qua=trang_thai, so_tien_sai={"so": "0"}),
    ])))


@pytest.mark.parametrize("du_lieu", [
    b"", b"DEMO", b"\xff", b"{}", b"[]", b"null", b"true",
    b'{"phien_ban":1,"phien_ban":1}',
    b'{"phien_ban":1,"ma_module":"demo","ket_qua":[],"nguong":{"pm":1,"pm":2}}',
    b'{"phien_ban":1,"ma_module":"demo","ket_qua":[],"nguong":{"pm":NaN}}',
    b'{"phien_ban":1,"ma_module":"demo","ket_qua":[],"nguong":{"pm":Infinity}}',
    b'{"phien_ban":1,"ma_module":"demo","ket_qua":[],"nguong":{"pm":-Infinity}}',
    b'{"phien_ban":1,"ma_module":"demo","ket_qua":[],"nguong":{"pm":1e999999999999999999999}}',
])
def test_json_sai_khoa_trung_va_hang_so_khong_huu_han(du_lieu):
    kiem_loi(ket_qua.doc_ket_qua_json, du_lieu)


def test_khoa_trung_trong_dong_bi_tu_choi():
    du_lieu = ma_hoa(tep_demo()).replace(b'"ket_qua":"dat"', b'"ket_qua":"dat","ket_qua":"sai"')
    kiem_loi(ket_qua.doc_ket_qua_json, du_lieu)


def test_json_long_qua_sau_van_tra_cau_loi_chuan():
    kiem_loi(ket_qua.doc_ket_qua_json, b"[" * 2000 + b"0" + b"]" * 2000)


def test_trung_giu_dong_dau_dem_va_giu_chi_so_goc():
    dau = dong_demo(ket_qua="sai", so_tien_sai={"so": "10", "tien_te": "VND"}, loai_dung="tam_ung")
    ds = [dau, dong_demo(), dong_demo(ma="PC-DEMO-0002"), dau,
          dong_demo(ma_luot="PL-DEMO-0002"), dong_demo(khau="cfo_duyet")]
    kq = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo(ds)))
    assert kq.so_trung_trong_tep == 2
    assert [d.chi_so for d in kq.dong] == [0, 2, 4, 5]
    assert kq.dong[0].ket_qua == "sai"
    assert kq.dong[0].so_tien_sai == kieu.Tien(Decimal("10"), "VND")
    assert kq.dong[0].loai_dung == "tam_ung"


def test_dong_trung_van_kiem_cau_truc():
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([
        dong_demo(), dong_demo(ket_qua="sai", so_tien_sai=None),
    ])))


def test_bien_tran_byte_that():
    du_lieu = ma_hoa(tep_demo([]))
    du_lieu += b" " * (ket_qua.TOI_DA_BYTE - len(du_lieu))
    assert len(du_lieu) == 20 * 1048576
    assert ket_qua.doc_ket_qua_json(du_lieu).dong == ()
    kiem_loi(ket_qua.doc_ket_qua_json, du_lieu + b" ", ma="VUOT_GIOI_HAN")


def test_bien_tran_dong_that_tinh_ca_dong_trung():
    dong = dong_demo()
    kq = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong] * 50000)))
    assert len(kq.dong) == 1
    assert kq.so_trung_trong_tep == 49999
    kiem_loi(ket_qua.doc_ket_qua_json, ma_hoa(tep_demo([dong] * 50001)), ma="VUOT_GIOI_HAN")


@pytest.mark.parametrize("so,muc", [
    ("0", "nho"), ("249999.999999", "nho"), ("250000", "sad"),
    ("250000.000001", "sad"), ("2999999.999999", "sad"),
    ("3000000", "te"), ("3000000.000001", "te"), ("5000000", "te"),
])
@pytest.mark.parametrize("dau", ["", "-"])
def test_muc_sai_bien_sad_te_va_so_am(so, muc, dau):
    assert ket_qua.muc_sai(kieu.Tien(Decimal(dau + so), "VND"), nguong_demo()) == muc


@pytest.mark.parametrize("tien_te", ["USD", None])
def test_muc_sai_tu_choi_tien_te_khac_hoac_thieu(tien_te):
    kiem_loi(ket_qua.muc_sai, kieu.Tien(Decimal("1000000"), tien_te), nguong_demo())


def test_muc_sai_khong_bi_lam_tron_theo_decimal_context():
    with localcontext() as ctx:
        ctx.prec = 3
        assert ket_qua.muc_sai(kieu.Tien(Decimal("-249999.999999"), "VND"), nguong_demo()) == "nho"


@pytest.mark.parametrize("ly_do,nguon", [
    ("CHON_MAU", "chon_mau"), ("VUOT_TE", "bat_buoc"),
    ("KHONG_CHON", "ngoai_mau"), (None, "ngoai_mau"),
])
def test_nguon_mau_du_bon_truong_hop(ly_do, nguon):
    assert ket_qua.nguon_mau(ly_do) == nguon


@pytest.mark.parametrize("ly_do", sorted(kieu.LY_DO_BAT_BUOC))
def test_nguon_mau_moi_ma_bat_buoc(ly_do):
    assert ket_qua.nguon_mau(ly_do) == "bat_buoc"


@pytest.mark.parametrize("ly_do,nguon", [
    ("VUOT_TE,CO_DO_CUNG", "bat_buoc"),
    ("VUOT_TE,CHON_MAU", "chon_mau"),
    ("CHON_MAU,KHONG_CHON", "chon_mau"),
    ("", "ngoai_mau"), ("KHONG_CHON_MAU", "ngoai_mau"),
    ("DEMO_VUOT_TE", "ngoai_mau"),
])
def test_nguon_mau_tach_ma_chinh_xac_va_uu_tien(ly_do, nguon):
    assert ket_qua.nguon_mau(ly_do) == nguon
