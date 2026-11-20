"""Các điểm lead cho phép sửa trong ty_le/chon_mau của PL-2 ghép."""
from decimal import Decimal
import inspect
import json

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_phan_luong import chon_mau, ty_le
from e_phan_luong.kieu import THU_TU_CO
from e_phan_luong.loi import CAU_LOI


@pytest.mark.parametrize("gia_tri", [0, -1, 0.5, 1.5, "1", True, None])
def test_don_vi_so_tron_phai_la_so_nguyen_duong(gia_tri):
    with pytest.raises(LoiNghiepVu) as exc:
        ty_le.doc_chinh_sach(json.dumps({"don_vi_so_tron": gia_tri}))
    assert exc.value.ma == "THAM_SO_KHONG_HOP_LE"


@pytest.mark.parametrize("gia_tri", [1, 10, 10000000])
def test_don_vi_so_tron_nguyen_duong_hop_le(gia_tri):
    assert ty_le.doc_chinh_sach(json.dumps({"don_vi_so_tron": gia_tri})).don_vi_so_tron == Decimal(gia_tri)


@pytest.mark.parametrize("co", THU_TU_CO)
@pytest.mark.parametrize("gia_tri", [0, -1, 0.999999, True, None, "2"])
def test_moi_he_so_khong_duoc_nho_hon_mot(co, gia_tri):
    with pytest.raises(LoiNghiepVu) as exc:
        ty_le.doc_chinh_sach(json.dumps({"he_so": {co: gia_tri}}))
    assert exc.value.ma == "THAM_SO_KHONG_HOP_LE"


@pytest.mark.parametrize("cot", ["san", "ty_le_duoi_sad", "don_vi_so_tron"])
@pytest.mark.parametrize("chu_so", ["NaN", "Infinity", "-Infinity", "1e999999999999999999999999999"])
def test_decimal_sai_khong_de_invalidoperation_lot_ra(cot, chu_so):
    with pytest.raises(LoiNghiepVu) as exc:
        ty_le.doc_chinh_sach('{"' + cot + '":' + chu_so + '}')
    assert exc.value.ma == "THAM_SO_KHONG_HOP_LE"
    assert exc.value.thong_diep == CAU_LOI[exc.value.ma]


@pytest.mark.parametrize("cot", ["san", "ty_le_duoi_sad"])
@pytest.mark.parametrize("p", [-0.000001, 1.000001])
def test_ty_le_ngoai_khoang_bi_tu_choi(cot, p):
    with pytest.raises(LoiNghiepVu) as exc:
        ty_le.doc_chinh_sach(json.dumps({cot: p}))
    assert exc.value.ma == "THAM_SO_KHONG_HOP_LE"


@pytest.mark.parametrize("p", [0, 1])
def test_hai_bien_ty_le_hop_le(p):
    cs = ty_le.doc_chinh_sach(json.dumps({"san": p, "ty_le_duoi_sad": p}))
    assert cs.san == cs.ty_le_duoi_sad == Decimal(p)


def test_q4_khong_con_tham_so_tat_nhan_he_so():
    assert list(inspect.signature(chon_mau.tinh_p).parameters) == ["p_co_so", "he_so", "san"]
    assert chon_mau.tinh_p(Decimal("0.02"), Decimal("20.25"), Decimal(0)) == Decimal("0.4050")
    assert "chờ quyết định" not in inspect.getdoc(chon_mau.tinh_p)


def test_hat_giong_khu_hoi_hex_bytes_cho_cung_ket_qua():
    hg = bytes(range(32))
    luu_ngan = hg.hex()
    doc_lai = bytes.fromhex(luu_ngan)
    assert len(luu_ngan) == 64 and doc_lai == hg
    assert chon_mau.bam_hat_giong(doc_lai) == chon_mau.bam_hat_giong(hg)
    for i in range(1000):
        args = ("demo_thanh_toan", "ktt_duyet", f"PC-DEMO-{i:04}", Decimal("0.20"))
        assert chon_mau.duoc_chon(doc_lai, *args) == chon_mau.duoc_chon(hg, *args)
