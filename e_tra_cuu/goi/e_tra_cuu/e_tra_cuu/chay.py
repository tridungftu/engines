"""Điểm vào SDK 2.0; cấu hình và dữ liệu chỉ qua ngăn."""

import json
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from .ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan


_GOI = Path(__file__).resolve().parent.parent
# Chỉ đọc metadata/schema đóng gói, không đọc giá trị cấu hình trên đĩa.
KHAI_BAO = json.loads((_GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((_GOI / "cau_hinh.schema.json").read_text(encoding="utf-8"))


def khoi_tao_ngan(ung_dung):
    """Gắn đúng một ngăn RAM khi SDK chưa cấp ngăn."""
    if getattr(ung_dung, "ngan", None) is None:
        ung_dung.ngan = NganBoNho(KHAI_BAO["ngan_du_lieu"])
    return chon_ngan(ung_dung)


def yeu_cau_cau_hinh(ngan):
    """Cổng cho việc cần cấu hình; stub TC-0 chưa dùng cấu hình."""
    try:
        cau_hinh = doc_cau_hinh(ngan, SCHEMA)
        if cau_hinh is None:
            raise LoiNghiepVu(
                "CHUA_CAU_HINH",
                "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình.",
            )
        # Các quan hệ không diễn đạt bằng tập từ khóa schema tối thiểu.
        phan_loai = cau_hinh["phan_loai"]
        da_do = phan_loai["trang_thai"] == "da_do"
        if (da_do and not {"nguong", "bam_bo_do"} <= phan_loai.keys()) or (
            not da_do and {"nguong", "bam_bo_do"} & phan_loai.keys()
        ):
            raise CauHinhKhongHopLe()
        if cau_hinh["cat_doan"]["do_dai_muc_tieu"] > cau_hinh["cat_doan"]["ky_tu_don_vi_toi_da"]:
            raise CauHinhKhongHopLe()
        return cau_hinh
    except (CauHinhKhongHopLe, NganKhongHopLe, NganXungDot) as exc:
        raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None


app = Engine.tu_khai_bao("engine.json")
ngan = khoi_tao_ngan(app)


@app.nang_luc("tra_cuu.kiem_khung@1")
def kiem_khung(viec):
    raise LoiNghiepVu("CHUA_LAM", "Chức năng tra cứu đang được hoàn thiện.")


if __name__ == "__main__":
    app.chay()
