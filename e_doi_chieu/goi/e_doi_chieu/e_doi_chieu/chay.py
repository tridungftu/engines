"""Cổng SDK của engine Đối chiếu bản ký."""
from functools import wraps
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, LoiDuongTruyen, ViecDaHuy, ChuaRo
from .doc_docx import doc_docx as _doc_docx
from .ho_so import nhan_cap as _nhan_cap
# DC-5 — khối nối riêng; không đổi đăng ký/cổng của lát ảnh DC-8.
from .quy_tac import so_van_ban as _so_van_ban
from .chuan_bi_ai import chuan_bi_ai as _chuan_bi_ai, kiem_prompt
from .hau_kiem_ai import phan_loai_diem_lech as _phan_loai_diem_lech
from .lech_dau import xu_ly_ho_so as _kiem_lech_dau

_GOI = Path(__file__).resolve().parent.parent
app = Engine.tu_khai_bao(str(_GOI / "engine.json"))
_BAT_BUOC = ("phien_ban_cau_hinh", "ma_bo_chuan_hoa", "bam_bo_chuan_hoa",
             "ma_tu_dien", "bam_tu_dien", "phuong_phap_detector", "phien_ban_detector")


def can_cau_hinh(viec):
    """SDK kiểm schema/điền mặc định; chỉ đọc bản chụp của việc hiện tại."""
    cau_hinh = viec.cau_hinh
    if any(type(cau_hinh.get(k)) is not str or not cau_hinh[k].strip() for k in _BAT_BUOC):
        raise LoiNghiepVu("CHUA_CAU_HINH", "Engine chưa được cấu hình. Admin vào Quản lý engine › Đối chiếu bản ký › Cấu hình.")
    return cau_hinh


def _an_toan(ham):
    """Đổi lỗi lạ bên trong handler thành câu cố định, giữ nguyên lỗi SDK."""
    @wraps(ham)
    def goi(*args, **kwargs):
        try:
            return ham(*args, **kwargs)
        except (LoiNghiepVu, LoiDuongTruyen, ViecDaHuy, ChuaRo):
            raise
        except Exception:
            raise LoiNghiepVu("DC_LOI_XU_LY", "Chưa xử lý được hồ sơ đối chiếu. Anh thử lại hoặc liên hệ quản trị viên.") from None
    return goi


@app.nang_luc("doi_chieu.doc_docx@1")
@_an_toan
def doc_docx(viec):
    return _doc_docx(viec, phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"])


@app.nang_luc("doi_chieu.nhan_cap@1")
@_an_toan
def nhan_cap(viec):
    cau_hinh = can_cau_hinh(viec)
    thoi_han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"]
                   if n["ma"] == "doi_chieu.nhan_cap@1")
    return _nhan_cap(viec, viec.ngan, cau_hinh,
                     phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"], thoi_han_viec_giay=thoi_han)


@app.nang_luc("doi_chieu.so_van_ban@1")
@_an_toan
def so_van_ban(viec):
    cau_hinh = can_cau_hinh(viec)
    thoi_han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"]
                   if n["ma"] == "doi_chieu.so_van_ban@1")
    pb = _so_van_ban(viec, viec.ngan, cau_hinh,
                    phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"], thoi_han_viec_giay=thoi_han)
    return _kiem_lech_dau(viec, viec.ngan, cau_hinh, pb)


# DC-8 — khối đăng ký riêng; DC-5 bổ sung độc lập ở phía trên.
from .sua_tay import phat_hien_sua_tay as _phat_hien_sua_tay


@app.nang_luc("doi_chieu.phat_hien_sua_tay@1")
@_an_toan
def phat_hien_sua_tay(viec):
    if any(k in viec.cau_hinh for k in _BAT_BUOC) and any(
            type(viec.cau_hinh.get(k)) is not str or not viec.cau_hinh[k].strip()
            for k in ("phuong_phap_detector", "phien_ban_detector")):
        raise LoiNghiepVu("DC_CHUA_CO_BO_PHAT_HIEN", "Chưa có bộ phát hiện sửa tay và dữ liệu hỗ trợ đã đo phù hợp. Hồ sơ vẫn cần kiểm tra.")
    cau_hinh = can_cau_hinh(viec)
    thoi_han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"]
                   if n["ma"] == "doi_chieu.phat_hien_sua_tay@1")
    return _phat_hien_sua_tay(viec, cau_hinh,
        phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"], thoi_han_viec_giay=thoi_han)


@app.nang_luc("doi_chieu.chuan_bi_ai@1")
@_an_toan
def chuan_bi_ai(viec):
    kiem_prompt(viec.tham_so)  # SDK 2.0 chưa cho handler đặt mã lỗi tham số bắt buộc.
    return _chuan_bi_ai(viec, viec.ngan, can_cau_hinh(viec),
                       phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"])


@app.nang_luc("doi_chieu.phan_loai_diem_lech@1")
@_an_toan
def phan_loai_diem_lech(viec):
    cau_hinh = can_cau_hinh(viec)
    pb = _phan_loai_diem_lech(viec, viec.ngan, cau_hinh,
                            phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"])
    return _kiem_lech_dau(viec, viec.ngan, cau_hinh, pb, hau_kiem=True)


if __name__ == "__main__":
    app.chay()
