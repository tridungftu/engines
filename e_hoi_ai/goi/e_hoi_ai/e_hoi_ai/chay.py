"""Đăng ký năng lực SDK 2.2.0; chỉ dùng ngăn và cấu hình của Core."""
from kho_tri_thuc_sdk.engine import Engine

from .chon_model import bo_phat_hien
from .hoi import AdapterHoiAI
from .hoi_yeu_cau import goi_theo_yeu_cau
from .hoi_mask import goi_mask_cuc_bo

app = Engine.tu_khai_bao("engine.json")
bo_hoi = AdapterHoiAI()


@app.khi_doi_cau_hinh
def doi_cau_hinh(cau_hinh):
    # Discovery chỉ đệm RAM; đổi cấu hình buộc phát hiện lại ở lượt tiếp theo.
    bo_phat_hien._dem.clear()


@app.nang_luc("ai.hoi_tai_lieu@1")
def hoi_tai_lieu(viec):
    return bo_hoi.goi(viec)


@app.nang_luc("ai.hoi_theo_yeu_cau@1")
def hoi_theo_yeu_cau(viec):
    return goi_theo_yeu_cau(viec, bo_hoi.cong_ai, phien_ban=app.phieu["phien_ban"])


@app.nang_luc("ai.hoi_mask_cuc_bo@1")
def hoi_mask_cuc_bo(viec):
    return goi_mask_cuc_bo(viec, bo_hoi.cong_ai, phien_ban=app.phieu["phien_ban"])


if __name__ == "__main__":
    app.chay()
