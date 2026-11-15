"""Đăng ký năng lực thật bằng SDK 2.0; cấu hình chỉ qua ngăn."""

from copy import deepcopy
from inspect import signature
import json
from pathlib import Path
from types import SimpleNamespace

import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from .ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan


GOC_GOI = Path(__file__).resolve().parents[1]
SCHEMA_CAU_HINH = json.loads((GOC_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))
KHAI_BAO_NGAN = json.loads((GOC_GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))["ngan_du_lieu"]
CAU_CHUA_CAU_HINH = (
    "Engine chưa được cấu hình. Admin vào Quản lý engine › "
    "Trích thông tin hợp đồng › Cấu hình."
)


class _BanChup:
    def __init__(self, ban_ghi):
        self._ban_ghi = ban_ghi

    def doc(self, bang, khoa):
        return self._ban_ghi


def ghim_cau_hinh(viec, app):
    """Seam TX-2: đọc đúng một bản, ưu tiên snapshot của SDK 2.1 nếu có.

    SDK lo engine.cau_hinh_doi; mỗi việc tiếp tục giữ bản chụp cũ.
    Không tự tạo bản ghi khi thiếu và không lưu giá trị vào tài nguyên gói.
    """
    try:
        if hasattr(viec, "cau_hinh") and hasattr(viec, "phien_ban_cau_hinh"):
            v, phien_ban = viec.cau_hinh, viec.phien_ban_cau_hinh
            ban_ghi = (SimpleNamespace(gia_tri=deepcopy(v), row_version=phien_ban)
                       if v is not None and phien_ban is not None else None)
        else:
            ngan = getattr(viec, "ngan", None)
            if ngan is None:
                ngan = chon_ngan(app)
            ban_ghi = ngan.doc("cau_hinh", {})
        gia_tri = doc_cau_hinh(_BanChup(ban_ghi), SCHEMA_CAU_HINH)
    except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
        raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None
    if gia_tri is None:
        raise LoiNghiepVu("CHUA_CAU_HINH", CAU_CHUA_CAU_HINH)
    return {"gia_tri": gia_tri, "phien_ban_cau_hinh": ban_ghi.row_version}


class EngineTrichXuat(Engine):
    """Bọc hẹp lỗi kiểm đầu vào SDK 2.0, giữ nguyên vòng việc/lease/ACK.

    SDK chặn MIME/kích thước trước handler. Chỉ dịch lỗi khi kết thúc;
    không nới khai báo hoặc sửa SDK. Cần Core C-TX-05 để có hook công khai.
    """
    def _ket_thuc(self, dt, viec, cfg, trang_thai, *, loi=None, ma_tuong_quan=None):
        if loi is not None and viec.nang_luc == "trich.doc_docx@1":
            if loi.ma == "LOAI_TEP_KHONG_NHAN":
                loi = LoiNghiepVu("TEP_KHONG_HO_TRO", "Chỉ nhận tệp Word định dạng DOCX.")
            elif loi.ma == "VUOT_GIOI_HAN":
                loi = LoiNghiepVu("VUOT_GIOI_HAN",
                                  "Tài liệu vượt giới hạn xử lý; hãy chia tài liệu trước khi gửi.")
        return super()._ket_thuc(dt, viec, cfg, trang_thai,
                                loi=loi, ma_tuong_quan=ma_tuong_quan)

    def _ghi(self, cau):
        # Chỉ chặn dòng SDK chứa lỗi nội dung việc/traceback; giữ mã lỗi vận hành.
        if cau.startswith("Lỗi khi xử lý việc ") or "Traceback (most recent call last):" in cau:
            cau = "Engine gặp lỗi khi xử lý việc này (ENGINE_LOI_XU_LY)."
        super()._ghi(cau)


def _kiem_sdk():
    """Hai hook nội bộ chỉ được kiểm với đúng SDK này; đổi SDK thì dừng kín."""
    try:
        dung = (kho_tri_thuc_sdk.__version__ == "2.0.0"
                and str(signature(Engine._ghi)) == "(self, cau)"
                and str(signature(Engine._ket_thuc)) == (
                    "(self, dt, viec, cfg, trang_thai, *, loi=None, ma_tuong_quan=None)"))
    except (AttributeError, TypeError, ValueError):
        dung = False
    if not dung:
        raise RuntimeError("SDK đã thay đổi; cần kiểm lại cổng lỗi và nhật ký trước khi chạy.")


def tao_app():
    _kiem_sdk()
    app = EngineTrichXuat.tu_khai_bao(GOC_GOI / "engine.json")
    if getattr(app, "ngan", None) is None:
        app.ngan = NganBoNho(KHAI_BAO_NGAN)
    chon_ngan(app)

    @app.nang_luc("trich.doc_docx@1")
    def doc_word(viec):
        from .docx import doc_docx
        return doc_docx(viec, phien_ban_engine=f"{app.ma} {app.phien_ban}")

    @app.nang_luc("trich.chuan_bi@1")
    def chuan_bi_ai(viec):
        from .tich_hop import chuan_bi
        viec.kiem_huy()
        cau_hinh = ghim_cau_hinh(viec, app)
        return chuan_bi(viec, cau_hinh, phien_ban_engine=f"{app.ma} {app.phien_ban}")

    @app.nang_luc("trich.hau_kiem@1")
    def hau_kiem_ai(viec):
        from .hau_kiem import hau_kiem
        return hau_kiem(viec, phien_ban_engine=f"{app.ma} {app.phien_ban}")

    @app.nang_luc("trich.xuat_ket_qua@1")
    def xuat_bang(viec):
        from .xuat import xuat_ket_qua
        return xuat_ket_qua(viec)

    return app


app = tao_app()


if __name__ == "__main__":
    app.chay()
