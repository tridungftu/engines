"""Ba nợ kiểm độc lập TC-2: nội dung bất hoạt, khóa thừa và luồng đọc ngắn."""

from copy import deepcopy
import io

import pytest
from kho_tri_thuc_sdk.engine import Viec

from e_tra_cuu.kiem_dau_vao import json_chuan
from ho_tro_tc_2 import BoDemo
from test_tc_2 import loi


@pytest.mark.parametrize("chu", ["ngày 01 / 02 / 2026", "Chi phí / doanh thu", "https://example.invalid/DEMO",
                                 "data: là nhãn dữ liệu DEMO", "A" * 80])
@pytest.mark.parametrize("truong", ["cau_hoi", "nguyen_van", "gia_tri"])
def test_khong_chan_noi_dung_hop_le_bang_regex(chu, truong):
    bo = BoDemo(van_ban="Công ty DEMO Ánh Dương\n" + chu)
    yc = bo.yeu_cau("xep_hang_lai" if truong == "nguyen_van" else "soan_tra_loi")
    if truong == "cau_hoi":
        yc["du_lieu"]["cau_hoi"] = chu
    elif truong == "gia_tri":
        yc["du_lieu"]["bang_chung"][0].update(kieu="van_ban", gia_tri=chu)
    assert bo.chay(yc)["trang_thai"] == "XONG"


@pytest.mark.parametrize("truong", ["tep_id", "ten", "ma"])
@pytest.mark.parametrize("chu", ["../DEMO.txt", "/tmp/DEMO.txt", "C:\\DEMO\\a", "https://example.invalid/a", "A" * 80])
def test_dinh_danh_tham_chieu_van_chan_traversal_va_kenh_ngoai(truong, chu):
    bo = BoDemo()
    yc = bo.yeu_cau()
    if truong == "ma":
        yc["ma_yeu_cau"] = chu
    else:
        yc["du_lieu"]["tai_lieu"]["goc"]["tep"][truong] = chu
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE")


@pytest.mark.parametrize("loai", ["metadata_core", "ung_vien", "bang_chung_1", "bang_chung_2", "nhom", "loai", "doi_tuong", "loai_hinh_phap_nhan"])
def test_cac_object_dong_tu_choi_khoa_thua(loai):
    bo = BoDemo()
    if loai == "metadata_core":
        yc = bo.yeu_cau()
        doi = yc["du_lieu"][loai]
    elif loai == "ung_vien":
        yc = bo.yeu_cau("xep_hang_lai")
        doi = yc["du_lieu"][loai][0]
    elif loai.startswith("bang_chung"):
        yc = bo.yeu_cau("soan_tra_loi")
        if loai.endswith("2"):
            yc["du_lieu"].update(tang=2, nguon=[bo.tai_lieu], bang_chung=[bo.doan()])
        doi = yc["du_lieu"]["bang_chung"][0]
    else:
        yc = bo.yeu_cau("phan_loai")
        dm = deepcopy(bo.danh_muc)
        dm[loai][0]["de_xuat_da_duyet"] = True
        yc["du_lieu"]["danh_muc"] = bo.tai("danh-muc-thua-DEMO.json", json_chuan(dm))
        doi = None
    if doi is not None:
        doi["de_xuat_da_duyet"] = True
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE")


@pytest.mark.parametrize("kich_thuoc", [1, 7, 97])
def test_doc_ngan_tiep_tuc_den_eof_thay_vi_sai_nguon(monkeypatch, kich_thuoc):
    goc = Viec.mo_tep
    dong = []

    class LuongNgan(io.BytesIO):
        def read(self, n=-1):
            return super().read(min(kich_thuoc, n) if n >= 0 else kich_thuoc)

        def close(self):
            dong.append(True)
            super().close()

    def mo_ngan(self, tep_id):
        with goc(self, tep_id) as f:
            return LuongNgan(f.read())

    monkeypatch.setattr(Viec, "mo_tep", mo_ngan)
    bo = BoDemo()
    assert bo.chay()["trang_thai"] == "XONG"
    assert len(dong) == 3
