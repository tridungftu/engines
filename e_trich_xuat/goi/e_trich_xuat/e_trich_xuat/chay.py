"""Đăng ký năng lực bằng SDK 2.2.0; cấu hình là bản chụp của việc."""

from copy import deepcopy
from inspect import signature
from pathlib import Path

import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .tham_so import bam_bytes, json_bytes


GOC_GOI = Path(__file__).resolve().parents[1]
CAU_CHUA_CAU_HINH = (
    "Engine chưa được cấu hình. Admin vào Quản lý engine › "
    "Trích thông tin hợp đồng › Cấu hình."
)


def ghim_cau_hinh(viec):
    """SDK kiểm schema/điền mặc định; không đọc lại cấu hình hiện hành.

    SDK 2.2.0 chưa công bố phiên bản trên Viec. Ghi null và băm bản chụp,
    không lấy phiên bản nội bộ của app vì có thể đã đổi bởi việc khác.
    """
    gia_tri = deepcopy(viec.cau_hinh)
    if not isinstance(gia_tri, dict) or "ngan_sach_token_vao_toi_da" not in gia_tri:
        raise LoiNghiepVu("CHUA_CAU_HINH", CAU_CHUA_CAU_HINH)
    return {"gia_tri": gia_tri, "phien_ban_cau_hinh": None,
            "bam_cau_hinh": bam_bytes(json_bytes(gia_tri))}


class EngineTrichXuat(Engine):
    """Bọc hẹp lỗi kiểm đầu vào SDK 2.2, giữ nguyên vòng việc/lease/ACK.

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
        elif loi is not None and viec.nang_luc == "trich.chuan_bi@1" and loi.ma == "VUOT_GIOI_HAN":
            loi = LoiNghiepVu("VUOT_GIOI_HAN", "Yêu cầu vượt giới hạn xử lý.")
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
        dung = (kho_tri_thuc_sdk.__version__ == "2.2.0"
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

    @app.nang_luc("trich.doc_docx@1")
    def doc_word(viec):
        from .docx import doc_docx
        return doc_docx(viec, phien_ban_engine=f"{app.ma} {app.phien_ban}")

    @app.nang_luc("trich.chuan_bi@1")
    def chuan_bi_ai(viec):
        from .tich_hop import chuan_bi
        viec.kiem_huy()
        cau_hinh = ghim_cau_hinh(viec)
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
