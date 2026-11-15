"""Tiện ích test OCR trên một ngăn RAM DEMO dùng chung, không có kho đĩa."""

import json
from pathlib import Path

from e_ocr.chon_nguon import SoHanMuc as SoHanMucGoc
from e_ocr.cau_hinh import doc_cau_hinh
from e_ocr.ngan import NganBoNho
from e_ocr.van_ban import SCHEMA

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_ocr"
KHAI = json.loads((GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
_ngan = None


def tao_ngan():
    return NganBoNho(KHAI["ngan_du_lieu"])


def ngan_demo():
    assert _ngan is not None, "Test cần fixture ngăn DEMO."
    return _ngan


def dat_cau_hinh(gia_tri):
    ngan = ngan_demo()
    cu = ngan.doc("cau_hinh", {})
    with ngan.lo() as lo:
        if cu is None:
            lo.them("cau_hinh", {}, gia_tri)
        else:
            lo.sua("cau_hinh", {}, gia_tri, row_version=cu.row_version)


def bo_cau_hinh():
    ngan = ngan_demo()
    cu = ngan.doc("cau_hinh", {})
    with ngan.lo() as lo:
        lo.xoa("cau_hinh", {}, row_version=cu.row_version)


def cau_hinh_hien_tai():
    return doc_cau_hinh(ngan_demo(), SCHEMA)


class SoHanMuc(SoHanMucGoc):
    def __init__(self, ngan=None, *, dong_ho=None):
        super().__init__(ngan if ngan is not None else ngan_demo(), dong_ho=dong_ho)


def ghi_so(so, gia_tri):
    anh, _ = so._doc()
    with so.ngan.lo() as lo:
        so._ghi(lo, anh, gia_tri)


def ghi_luot(nk, gia_tri):
    cu = nk.ngan.doc("luot_abbyy", nk._khoa())
    # Sửa bản ghi hỏng có thể đổi khóa: xóa/tạo để mô phỏng dữ liệu cần kiểm tra.
    with nk.ngan.lo() as lo:
        lo.xoa("luot_abbyy", nk._khoa(), row_version=cu.row_version)
        lo.them("luot_abbyy", {"phap_nhan_id": nk.phap_nhan_id,
                               "ma_tuong_quan": gia_tri["ma_tuong_quan"]}, gia_tri)
