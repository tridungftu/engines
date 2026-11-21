"""PL-10A/H1, Anh chốt 21/11/2026; đã kiểm bằng Core giả (CoreGia).

Chỉ hóa đơn DEMO. MST bán công khai được giữ nguyên trong mã hóa đơn;
ngoại lệ C4 chỉ áp cột ma ở dong_luot/ket_qua_kiem và tệp ra hóa đơn.
"""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
import re

import openpyxl
import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau, hoa_don
from e_phan_luong.chay import app
from test_pl7_phan_luong_hoa_don import chay, ket_qua, kiem_loi, tham_so, xml, zip_demo
from test_pl9b_c4_c5 import mst_trong_ma_hoa_don

MA = "1-C26TAA-00000123"
MST_A, MST_B = "0100000001", "0100000002"
TS = {"ma_module": "demo_thanh_toan", "loai_nghiep_vu": "hoa_don_dau_vao"}


def truong(mst=MST_A):
    t = xml()["truong"]
    t.update(so_hoa_don="00000123", ma_so_thue_ban=mst)
    return t


def bao_cao(*cac_truong):
    return json.dumps({
        "phien_ban": 1, "nguon_doc": "zip_xml_strict",
        "danh_sach_tep": [{"trang_thai_doc": "doc_duoc", "truong_hoa_don": t}
                          for t in cac_truong],
    }, ensure_ascii=False).encode("utf-8")


def phong_bi(core, nguon, *cac_truong):
    if nguon == "xml":
        t, = cac_truong
        return {"loai": "truong", "truong": t}
    return zip_demo(core, bao_cao(*cac_truong))[0]


@pytest.mark.parametrize("nguon", ["xml", "zip"])
@pytest.mark.parametrize("mst,duoi", [
    (MST_A, "-" + MST_A), ("  " + MST_A + "-001 \t", "-" + MST_A + "-001"),
    (None, ""), ("", ""), (" \t ", ""),
])
def test_ma_xml_va_doc_zip_cung_quy_tac_mst_nguyen_van(nguon, mst, duoi):
    t = truong(mst)
    goc = deepcopy(t)
    if nguon == "xml":
        lo = hoa_don.lo_tu_hoa_don(t, **TS)
    else:
        lo, bo = hoa_don.lo_tu_chi_tiet_zip(bao_cao(t), **TS)
        assert bo == 0
    nv, = lo.nghiep_vu
    assert nv.ma == MA + duoi
    assert nv.doi_tac == mst  # Không đổi xử lý đối tác hiện hành.
    assert t == goc


@pytest.mark.parametrize("nguon", ["xml", "zip"])
def test_thieu_khoa_mst_giu_ma_ba_phan(nguon):
    t = truong()
    del t["ma_so_thue_ban"]
    core = CoreGia()
    _, tep = ket_qua(core, chay(core, phong_bi(core, nguon, t)))
    assert tep["nghiep_vu"][0]["ma"] == MA


def test_cung_mau_ky_hieu_so_khac_nguoi_ban_nhan_ca_hai_trong_lo_zip():
    core = CoreGia()
    t, tep = ket_qua(core, chay(core, phong_bi(core, "zip", truong(), truong(MST_B))))
    assert t["so_nghiep_vu"] == 2
    assert [d["ma"] for d in tep["nghiep_vu"]] == [MA + "-" + MST_A, MA + "-" + MST_B]
    assert len(core.xem_ngan(app.ma, "dong_luot")) == 2


@pytest.mark.parametrize("mst_hai", [MST_A, "  " + MST_A + "  "])
def test_cung_mst_cung_hoa_don_van_tu_choi_ca_lo(mst_hai):
    core = CoreGia()
    pb = phong_bi(core, "zip", truong(), truong(mst_hai))
    kiem_loi(chay(core, pb), "DU_LIEU_KHONG_HOP_LE")
    for bang in ("luot", "dong_luot", "ho_so_hanh_vi"):
        assert core.xem_ngan(app.ma, bang) == []


@pytest.mark.parametrize("nguon", ["xml", "zip"])
@pytest.mark.parametrize("mst_hai,nop_lai", [(MST_B, False), (MST_A, True)])
def test_hai_luot_core_gia_chi_cung_nguoi_ban_moi_la_nop_lai(monkeypatch, nguon, mst_hai, nop_lai):
    core = CoreGia()
    a, b = truong(), truong(mst_hai)
    a["can_kiem_tra"] = b["can_kiem_tra"] = False
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *_: True)
    t1, tep1 = ket_qua(core, chay(core, phong_bi(core, nguon, a)))
    assert tep1["nghiep_vu"][0]["ly_do"] == ["CHON_MAU"]
    monkeypatch.setattr(chon_mau, "duoc_chon", lambda *_: False)
    t2, tep2 = ket_qua(core, chay(core, phong_bi(core, nguon, b)))
    assert t1["ma_luot"] != t2["ma_luot"]
    d, = tep2["nghiep_vu"]
    assert d["ma"] == MA + "-" + mst_hai
    assert ("NOP_LAI" in d["ly_do"]) is nop_lai
    assert d["luong"] == ("do" if nop_lai else "xanh")


@pytest.mark.parametrize("nguon", ["xml", "zip"])
@pytest.mark.parametrize("do_dai", [120, 121])
def test_tran_ma_120_ky_tu_khong_cat_ngam(nguon, do_dai):
    t = truong()
    t["so_hoa_don"] = "0" * (do_dai - len("1-C26TAA--" + MST_A))
    core = CoreGia()
    kq = chay(core, phong_bi(core, nguon, t))
    if do_dai == 121:
        kiem_loi(kq, "DU_LIEU_KHONG_HOP_LE")
        assert core.xem_ngan(app.ma, "dong_luot") == []
    else:
        _, tep = ket_qua(core, kq)
        assert len(tep["nghiep_vu"][0]["ma"]) == 120


@pytest.mark.parametrize("nguon", ["xml", "zip"])
def test_c4_mst_chi_o_ma_hoa_don_ho_so_hanh_vi_van_bam(nguon):
    core = CoreGia()
    mst = MST_A + "-001"
    t, tep = ket_qua(core, chay(core, phong_bi(core, nguon, truong(mst))))
    ma = MA + "-" + mst
    assert tep["nghiep_vu"][0]["ma"] == ma
    wb = openpyxl.load_workbook(BytesIO(core.doc_tep(t["tep_ds_do"]["tep_id"])), read_only=True)
    try:
        assert any(o.value == ma for ws in wb for hang in ws for o in hang)
    finally:
        wb.close()
    ghi = {"phien_ban": 1, "ma_module": TS["ma_module"], "ket_qua": [{
        "ma_luot": t["ma_luot"], "ma": ma, "khau": "ktt_duyet", "ket_qua": "dat",
    }]}
    ref = core.them_tep("ket-qua-hoa-don-DEMO.json", json.dumps(ghi).encode(), "application/json")
    ts = tham_so()
    del ts["loai_nghiep_vu"]
    kq = core.chay_thu(app, "audit.ghi_ket_qua@1", {"loai": "tep", "tep": ref}, ts)
    assert kq["trang_thai"] == "XONG", kq
    for bang in app.phieu["ngan_du_lieu"]:
        ten = bang["bang"]
        ds = core.xem_ngan(app.ma, ten)
        if ten in {"dong_luot", "ket_qua_kiem"}:
            assert ds and ds[0]["ma"] == ma
        for dong in ds:
            for cot, o in dong.items():
                if ten in {"dong_luot", "ket_qua_kiem"} and cot == "ma":
                    continue  # Ngoại lệ C4 Anh duyệt 21/11/2026, chỉ mã hóa đơn.
                assert MST_A not in str(o)
    hs = core.xem_ngan(app.ma, "ho_so_hanh_vi")
    assert hs
    bam = [h for d in hs for h in json.loads(d["bam_doi_tac"])]
    assert bam and all(re.fullmatch(r"[0-9a-f]{32}", h) for h in bam)
    assert set(bam) == {sha256(
        ("e_phan_luong|doi_tac|" + TS["ma_module"] + "|" + mst).encode("utf-8")
    ).hexdigest()[:32]}


@pytest.mark.parametrize("bang,duong,ma,cam,duoc", [
    ("dong_luot", "/ma", MA + "-" + MST_A, MST_A, True),
    ("ket_qua_kiem", "/ma", MA + "-" + MST_A, MST_A, True),
    ("ho_so_hanh_vi", "/ma", MA + "-" + MST_A, MST_A, False),
    ("luot", "/ma", MA + "-" + MST_A, MST_A, False),
    ("dong_luot", "/ly_do", MA + "-" + MST_A, MST_A, False),
    ("dong_luot", "/ma", "PC-DEMO-" + MST_A, MST_A, False),
    ("dong_luot", "/ma", MA + "-" + MST_B, MST_B, False),
])
def test_bo_quet_c4_chi_mien_dung_cot_ma_duong_hoa_don(bang, duong, ma, cam, duoc):
    class Vong:
        dau_vao = [{"loai": "truong", "truong": truong()}]
        ra = [("audit.phan_luong_hoa_don@1", {"truong": {"ma_luot": "PL-DEMO"}})]

    assert mst_trong_ma_hoa_don(Vong(), bang, duong, ma, cam, "PL-DEMO") is duoc
    assert not mst_trong_ma_hoa_don(Vong(), bang, duong, ma, cam, "PL-DEMO-JSON")
