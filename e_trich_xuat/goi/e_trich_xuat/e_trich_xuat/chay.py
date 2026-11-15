"""Đăng ký năng lực thật bằng SDK 2.0; cấu hình chỉ qua ngăn."""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .cau_hinh import doc_cau_hinh
from .ngan import chon_ngan


GOC_GOI = Path(__file__).resolve().parents[1]
SCHEMA_CAU_HINH = json.loads((GOC_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))
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
    if hasattr(viec, "cau_hinh") and hasattr(viec, "phien_ban_cau_hinh"):
        v, phien_ban = viec.cau_hinh, viec.phien_ban_cau_hinh
        ban_ghi = (SimpleNamespace(gia_tri={"gia_tri": deepcopy(v)}, row_version=phien_ban)
                   if v is not None and phien_ban is not None else None)
    else:
        ngan = getattr(viec, "ngan", None)
        if ngan is None:
            ngan = chon_ngan(app)
        ban_ghi = ngan.doc("cau_hinh", {"ma": "mac_dinh"})
    try:
        gia_tri = doc_cau_hinh(_BanChup(ban_ghi), SCHEMA_CAU_HINH)
    except ValueError:
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE",
                          "Cấu hình engine không hợp lệ. Admin hãy kiểm tra lại mục Cấu hình.") from None
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
        # SDK 2.0 có thể đưa traceback vào cau. Không đưa nội dung đó ra log.
        super()._ghi("Có lỗi khi xử lý hoặc trao đổi với Core; hãy thử lại hoặc liên hệ hỗ trợ.")


def tao_app():
    app = EngineTrichXuat.tu_khai_bao(GOC_GOI / "engine.json")
    chon_ngan(app)

    @app.nang_luc("trich.doc_docx@1")
    def doc_word(viec):
        from .docx import doc_docx
        return doc_docx(viec, phien_ban_engine=f"{app.ma} {app.phien_ban}")

    return app


app = tao_app()


if __name__ == "__main__":
    app.chay()
