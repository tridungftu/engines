"""Đăng ký bằng cửa công khai SDK do Core cấp; cấu hình là bản chụp của việc."""

from copy import deepcopy
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .tham_so import bam_bytes, json_bytes


GOC_GOI = Path(__file__).resolve().parents[1]
CAU_CHUA_CAU_HINH = (
    "Engine chưa được cấu hình. Admin vào Quản lý engine › "
    "Trích thông tin hợp đồng › Cấu hình."
)


def ghim_cau_hinh(viec):
    """SDK kiểm schema/điền mặc định; không đọc lại cấu hình hiện hành.

    SDK chưa công bố phiên bản trên Viec. Ghi null và băm bản chụp,
    không lấy phiên bản nội bộ của app vì có thể đã đổi bởi việc khác.
    """
    gia_tri = deepcopy(viec.cau_hinh)
    if not isinstance(gia_tri, dict) or "ngan_sach_token_vao_toi_da" not in gia_tri:
        raise LoiNghiepVu("CHUA_CAU_HINH", CAU_CHUA_CAU_HINH)
    return {"gia_tri": gia_tri, "phien_ban_cau_hinh": None,
            "bam_cau_hinh": bam_bytes(json_bytes(gia_tri))}


def tao_app():
    app = Engine.tu_khai_bao(GOC_GOI / "engine.json")

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
