"""Cổng SDK của engine Đối chiếu bản ký."""
import json
from functools import wraps
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, LoiDuongTruyen, ViecDaHuy, ChuaRo
from .ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan
from .cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from .doc_docx import doc_docx as _doc_docx
from .ho_so import nhan_cap as _nhan_cap
# DC-5 — khối nối riêng; không đổi đăng ký/cổng của lát ảnh DC-8.
from .quy_tac import so_van_ban as _so_van_ban
from .chuan_bi_ai import chuan_bi_ai as _chuan_bi_ai, kiem_prompt
from .hau_kiem_ai import phan_loai_diem_lech as _phan_loai_diem_lech

_GOI = Path(__file__).resolve().parent.parent
app = Engine.tu_khai_bao(str(_GOI / "engine.json"))
_khai = json.loads((_GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
_schema = json.loads((_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))
if getattr(app, "ngan", None) is None:
    app.ngan = NganBoNho(_khai["ngan_du_lieu"])
ngan = chon_ngan(app)


def can_cau_hinh(ngan_doc=None):
    """Dùng cho các việc cần cấu hình trong những lát tiếp theo."""
    try:
        cau_hinh = doc_cau_hinh(ngan if ngan_doc is None else ngan_doc, _schema)
    except CauHinhKhongHopLe as exc:
        raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None
    if cau_hinh is None:
        raise LoiNghiepVu("CHUA_CAU_HINH", "Engine chưa được cấu hình. Admin vào Quản lý engine › Đối chiếu bản ký › Cấu hình.")
    return cau_hinh


def _an_toan(ham):
    """SDK 2.0 ghi traceback lỗi lạ; chỉ đổi lỗi bên trong handler thành câu cố định."""
    @wraps(ham)
    def goi(*args, **kwargs):
        try:
            return ham(*args, **kwargs)
        except (LoiNghiepVu, LoiDuongTruyen, ViecDaHuy, ChuaRo):
            raise
        except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
            raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None
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
    ngan_viec = getattr(viec, "ngan", None)
    if ngan_viec is None:
        ngan_viec = ngan
    cau_hinh = can_cau_hinh(ngan_viec)
    thoi_han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"]
                   if n["ma"] == "doi_chieu.nhan_cap@1")
    return _nhan_cap(viec, ngan_viec, cau_hinh,
                     phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"], thoi_han_viec_giay=thoi_han)


@app.nang_luc("doi_chieu.so_van_ban@1")
@_an_toan
def so_van_ban(viec):
    ngan_viec = getattr(viec, "ngan", None)
    if ngan_viec is None:
        ngan_viec = ngan
    cau_hinh = can_cau_hinh(ngan_viec)
    thoi_han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"]
                   if n["ma"] == "doi_chieu.so_van_ban@1")
    return _so_van_ban(viec, ngan_viec, cau_hinh,
                       phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"], thoi_han_viec_giay=thoi_han)


# DC-8 — khối đăng ký riêng; DC-5 bổ sung độc lập ở phía trên.
from .sua_tay import phat_hien_sua_tay as _phat_hien_sua_tay


@app.nang_luc("doi_chieu.phat_hien_sua_tay@1")
@_an_toan
def phat_hien_sua_tay(viec):
    ngan_viec = getattr(viec, "ngan", None)
    ngan_doc = ngan if ngan_viec is None else ngan_viec
    ban = ngan_doc.doc("cau_hinh", {})
    if ban is not None and any(type(ban.gia_tri.get(k)) is not str or not ban.gia_tri[k].strip()
            for k in ("phuong_phap_detector", "phien_ban_detector")):
        raise LoiNghiepVu("DC_CHUA_CO_BO_PHAT_HIEN", "Chưa có bộ phát hiện sửa tay và dữ liệu hỗ trợ đã đo phù hợp. Hồ sơ vẫn cần kiểm tra.")
    cau_hinh = can_cau_hinh(ngan_doc)
    thoi_han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"]
                   if n["ma"] == "doi_chieu.phat_hien_sua_tay@1")
    return _phat_hien_sua_tay(viec, cau_hinh,
        phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"], thoi_han_viec_giay=thoi_han)


@app.nang_luc("doi_chieu.chuan_bi_ai@1")
@_an_toan
def chuan_bi_ai(viec):
    kiem_prompt(viec.tham_so)  # SDK 2.0 chưa cho handler đặt mã lỗi tham số bắt buộc.
    ngan_viec = getattr(viec, "ngan", None)
    ngan_doc = ngan if ngan_viec is None else ngan_viec
    return _chuan_bi_ai(viec, ngan_doc, can_cau_hinh(ngan_doc),
                       phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"])


@app.nang_luc("doi_chieu.phan_loai_diem_lech@1")
@_an_toan
def phan_loai_diem_lech(viec):
    ngan_viec = getattr(viec, "ngan", None)
    ngan_doc = ngan if ngan_viec is None else ngan_viec
    return _phan_loai_diem_lech(viec, ngan_doc, can_cau_hinh(ngan_doc),
                              phien_ban_engine="e_doi_chieu " + app.phieu["phien_ban"])


if __name__ == "__main__":
    app.chay()
