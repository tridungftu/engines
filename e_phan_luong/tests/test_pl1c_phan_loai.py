"""Kiểm hợp đồng phân loại PL-1C bằng dữ liệu DEMO, không cần Core."""
from dataclasses import replace
from datetime import date
from decimal import Decimal
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import phan_loai
from e_phan_luong.kieu import NghiepVu, Tien
from e_phan_luong.loi import CAU_LOI, loi


def json_chu(d):
    return json.dumps(d, ensure_ascii=False)


def muc(ma="thanh_toan"):
    return {"ma": ma, "ten": "Thanh toán DEMO", "mo_ta": ""}


def danh_muc():
    return phan_loai.doc_danh_muc_loai(json_chu([muc(), muc("tam_ung")]))


def dk(tu="DEMO"):
    return {"tat_ca": [[tu]]}


def qt(loai="thanh_toan", khi=None):
    return {"loai": loai, "khi": [dk()] if khi is None else khi}


def bo(quy_tac=None):
    return {"phien_ban": 1, "quy_tac": [qt()] if quy_tac is None else quy_tac}


def nv():
    return NghiepVu(0, "PC-DEMO-0001", date(2026, 10, 30),
                   Tien(Decimal("1000000"), "VND"),
                   noi_dung={"dien_giai": "DEMO thanh toán đợt 12",
                             "tai_khoan_no": "331", "tai_khoan_co": "1121",
                             "thuoc_tinh.nhom": "DEMO tạm ứng",
                             "thuoc_tinh.Đơn vị": "Công ty DEMO Ánh Dương"})


def kiem_loi(ham, ma="THAM_SO_KHONG_HOP_LE"):
    with pytest.raises(type(loi(ma))) as bat:
        ham()
    assert bat.value.ma == ma
    assert bat.value.thong_diep == CAU_LOI[ma]


@pytest.mark.parametrize("chuoi", [None, "", "[]"])
def test_danh_muc_trong(chuoi):
    assert phan_loai.doc_danh_muc_loai(chuoi) == {}


def test_danh_muc_giu_thong_tin_va_bien_100():
    ds = [muc(f"demo_{i}") for i in range(100)]
    assert phan_loai.doc_danh_muc_loai(json_chu(ds)) == {m["ma"]: m for m in ds}
    kiem_loi(lambda: phan_loai.doc_danh_muc_loai(json_chu(ds + [muc("demo_100")])))
    assert "a" * 40 in phan_loai.doc_danh_muc_loai(json_chu([muc("a" * 40)]))


@pytest.mark.parametrize("ma", ["chua_phan_loai", "", "1demo", "Demo", "DEMO",
                                   "đemo", "demo-x", "demo x", "a" * 41, [], None])
def test_ma_loai_sai(ma):
    kiem_loi(lambda: phan_loai.doc_danh_muc_loai(json_chu([muc(ma)])))


@pytest.mark.parametrize("ds", [
    [muc(), muc()], {}, [None], [{"ma": "demo", "ten": "DEMO"}],
    [{**muc(), "ten": " "}], [{**muc(), "mo_ta": None}], [{**muc(), "them": 1}],
])
def test_danh_muc_sai_cau_truc_hoac_trung(ds):
    kiem_loi(lambda: phan_loai.doc_danh_muc_loai(json_chu(ds)))


def test_danh_muc_tran_16kib():
    chu = json_chu([muc()])
    chu += " " * (16384 - len(chu.encode("utf-8")))
    assert phan_loai.doc_danh_muc_loai(chu) == {"thanh_toan": muc()}
    kiem_loi(lambda: phan_loai.doc_danh_muc_loai(chu + " "))


@pytest.mark.parametrize("chu", [None, "", json_chu(bo([]))])
def test_bo_trong(chu):
    b = phan_loai.doc_bo_phan_loai(chu, danh_muc())
    assert b.tim("DEMO") is None
    assert phan_loai.gan_loai(nv(), danh_muc(), b, "dien_giai") == (None, None)


def test_quy_tac_dau_tien_thang_va_or_trong_khi():
    b = phan_loai.doc_bo_phan_loai(json_chu(bo([
        qt("tam_ung", [dk("không tồn tại DEMO"), dk("thanh toán")]),
        qt("thanh_toan"),
    ])), danh_muc())
    assert phan_loai.gan_loai(nv(), danh_muc(), b, "dien_giai") == ("tam_ung", "quy_tac")


def test_quy_tac_khong_co_va_khong_khop():
    dieu_kien = {"tat_ca": [["thanh toán", "tạm ứng"], ["đợt #"]], "khong_co": ["hủy"]}
    b = phan_loai.doc_bo_phan_loai(json_chu(bo([qt(khi=[dieu_kien])])), danh_muc())
    assert phan_loai.gan_loai(nv(), danh_muc(), b, "dien_giai") == ("thanh_toan", "quy_tac")
    n = replace(nv(), noi_dung={"dien_giai": "DEMO HỦY thanh toán đợt 12"})
    ket_qua = phan_loai.gan_loai(n, danh_muc(), b, "dien_giai")
    assert ket_qua == (None, None)
    assert phan_loai.chot_loai(ket_qua) == ("chua_phan_loai", "chua_phan_loai")


def test_module_uu_tien_va_chot_giu_nguyen_nguon():
    b = phan_loai.doc_bo_phan_loai(json_chu(bo()), danh_muc())
    n = replace(nv(), loai="tam_ung")
    kq = phan_loai.gan_loai(n, danh_muc(), b, "dien_giai")
    assert kq == ("tam_ung", "module")
    assert phan_loai.chot_loai(kq) == kq
    for nguon in ("quy_tac", "ai"):
        assert phan_loai.chot_loai(("thanh_toan", nguon)) == ("thanh_toan", nguon)


@pytest.mark.parametrize("loai", ["ngoai_demo", "chua_phan_loai", "", []])
def test_module_gan_ngoai_danh_muc(loai):
    kiem_loi(lambda: phan_loai.gan_loai(replace(nv(), loai=loai), danh_muc(),
                                     phan_loai.BoPhanLoai(), None), "DU_LIEU_KHONG_HOP_LE")


@pytest.mark.parametrize("truong,noi_dung", [
    ("dien_giai", "DEMO thanh toán đợt 12"), ("tai_khoan_no", "331"),
    ("tai_khoan_co", "1121"), ("thuoc_tinh.nhom", "DEMO tạm ứng"),
    ("thuoc_tinh.Đơn vị", "Công ty DEMO Ánh Dương"),
    ("thuoc_tinh.khong_co", None), (None, None), ("", None),
])
def test_lay_noi_dung(truong, noi_dung):
    assert phan_loai.lay_noi_dung(nv(), truong) == noi_dung


def test_phan_loai_chi_so_truong_da_chon():
    b = phan_loai.doc_bo_phan_loai(json_chu(bo([qt(khi=[dk("tạm ứng")])])), danh_muc())
    assert phan_loai.gan_loai(nv(), danh_muc(), b, "dien_giai") == (None, None)
    assert phan_loai.gan_loai(nv(), danh_muc(), b, "thuoc_tinh.nhom") == ("thanh_toan", "quy_tac")
    for truong in (None, "", "thuoc_tinh.khong_co"):
        assert phan_loai.gan_loai(nv(), danh_muc(), b, truong) == (None, None)


@pytest.mark.parametrize("truong", ["loai", "noi_dung", "nhom", "thuoc_tinh.", 1, [],
                                       "thuoc_tinh." + "a" * 50])
def test_truong_khong_hop_le(truong):
    kiem_loi(lambda: phan_loai.lay_noi_dung(nv(), truong))


@pytest.mark.parametrize("d", [
    None, [], {}, {**bo(), "phien_ban": True}, {**bo(), "phien_ban": 2},
    {**bo(), "quy_tac": {}}, {**bo(), "them": "DEMO"},
    bo([None]), bo([qt("ngoai_demo")]), bo([qt([])]), bo([qt(khi=[])]),
    bo([{**qt(), "vung": "dien_giai"}]),
    bo([qt(khi=[{"tat_ca": [["DEMO"]], "vung": ["dien_giai"]}])]),
    bo([qt(khi=[{"tat_ca": ["DEMO"]}])]),
    bo([qt(khi=[{"tat_ca": [["DEMO"]], "khong_co": [1]}])]),
])
def test_bo_sai_cau_truc(d):
    kiem_loi(lambda: phan_loai.doc_bo_phan_loai(json_chu(d), danh_muc()))


def test_tran_200_tu_tinh_ca_khong_co_va_cac_dieu_kien():
    dieu_kien = {"tat_ca": [["DEMO"] * 199], "khong_co": ["hủy"]}
    du_lieu = bo([qt(khi=[dieu_kien])])
    assert phan_loai.doc_bo_phan_loai(json_chu(du_lieu), danh_muc()).tim("DEMO") == "thanh_toan"
    dieu_kien["khong_co"].append("chưa")
    kiem_loi(lambda: phan_loai.doc_bo_phan_loai(json_chu(du_lieu), danh_muc()))
    dieu_kien["khong_co"].pop()
    du_lieu["quy_tac"][0]["khi"].append(dk())
    kiem_loi(lambda: phan_loai.doc_bo_phan_loai(json_chu(du_lieu), danh_muc()))


def test_200_tu_moi_quy_tac():
    d = bo([qt(khi=[{"tat_ca": [["DEMO"] * 200]}]),
            qt("tam_ung", [{"tat_ca": [["DEMO"] * 200]}])])
    assert phan_loai.doc_bo_phan_loai(json_chu(d), danh_muc()).tim("DEMO") == "thanh_toan"


def test_bo_tran_32kib_va_regex_chi_la_chu():
    chu = json_chu(bo([qt(khi=[dk(".*[Đ]+")])]))
    chu += " " * (32768 - len(chu.encode("utf-8")))
    b = phan_loai.doc_bo_phan_loai(chu, danh_muc())
    assert b.tim("DEMO đđđ") is None
    assert b.tim("DEMO .*[đ]+") == "thanh_toan"
    kiem_loi(lambda: phan_loai.doc_bo_phan_loai(chu + " ", danh_muc()))


@pytest.mark.parametrize("chuoi", ['{"phien_ban":1,"phien_ban":1,"quy_tac":[]}',
                                      '{"phien_ban":NaN,"quy_tac":[]}', "{",
                                      pytest.param("[" * 2000 + "]" * 2000, id="long_sau")])
def test_bo_json_loi(chuoi):
    kiem_loi(lambda: phan_loai.doc_bo_phan_loai(chuoi, danh_muc()))
