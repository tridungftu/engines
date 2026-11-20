"""Kiểu dữ liệu và mã dùng chung của e_phan_luong.

Tệp này là HỢP ĐỒNG giữa các mô-đun do nhiều Codex viết song song (GIAO-CODEX §2).
Lead giữ tệp; Codex KHÔNG sửa. Thấy thiếu thì ghi vào báo cáo, lead bổ sung.
Chỉ dùng thư viện chuẩn. Tiền luôn là Decimal kèm mã tiền tệ; không tự gán VND.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

# ---------------------------------------------------------------- tiền

@dataclass(frozen=True)
class Tien:
    """Một số tiền. `tien_te` là mã ISO 4217 ba chữ hoa; None = chưa rõ tiền tệ."""
    so: Decimal
    tien_te: str | None


# ---------------------------------------------------------------- nghiệp vụ

@dataclass(frozen=True)
class NghiepVu:
    """Một dòng của lô (§5.1). `doi_tac` và `noi_dung` chỉ dùng trong lúc chạy, KHÔNG lưu ngăn."""
    chi_so: int                          # thứ tự dòng trong lô, đếm từ 0
    ma: str                              # mã giao dịch do module đặt (≤ 120 ký tự, không ký tự điều khiển)
    ngay: date
    so_tien: Tien
    so_tien_quy_doi: Tien | None = None
    loai: str | None = None              # loại module đã gán (doc_lo chưa kiểm danh mục)
    doi_tac: str | None = None           # mã đối tác thô
    noi_dung: dict[str, str] = field(default_factory=dict)
    # khóa của noi_dung: "dien_giai", "tai_khoan_no", "tai_khoan_co", "thuoc_tinh.<khóa>"
    nhap_tay: bool = False
    co_do_cung: bool = False


@dataclass(frozen=True)
class Lo:
    """Một lô nghiệp vụ đã kiểm cấu trúc (§5.1)."""
    phien_ban: int
    ma_module: str
    ky: str | None                       # "YYYY-MM" hoặc None
    nguong: dict | None                  # khối "nguong" thô trong tệp; nguong.py kiểm
    nghiep_vu: tuple[NghiepVu, ...]


@dataclass(frozen=True)
class Nguong:
    """Ngưỡng PM/TE/SAD đã kiểm: cùng tiền tệ, SAD < TE <= PM."""
    pm: Tien
    te: Tien
    sad: Tien

    @property
    def tien_te(self) -> str:
        return self.te.tien_te  # type: ignore[return-value]


# ---------------------------------------------------------------- mã lý do (ly_do)
# Mã ổn định: ghi trong tep_json, tep_ds_do và cột dong_luot.ly_do (nối bằng dấu phẩy, theo THU_TU_LY_DO).

VUOT_PM = "VUOT_PM"                  # số tiền >= PM
VUOT_TE = "VUOT_TE"                  # TE <= số tiền < PM
CHUA_QUY_DOI = "CHUA_QUY_DOI"        # khác tiền tệ ngưỡng, không có so_tien_quy_doi cùng tiền tệ ngưỡng
CHUA_RO_TIEN_TE = "CHUA_RO_TIEN_TE"  # không biết tiền tệ của số tiền
NGHI_CHIA_NHO = "NGHI_CHIA_NHO"      # nhóm (đối tác, khâu, cửa sổ ngày) tổng >= TE
CO_DO_CUNG = "CO_DO_CUNG"            # module truyền co_do_cung = true
NOP_LAI = "NOP_LAI"                  # lần trước cùng (ma_module, khau, ma) ra Đỏ
CHON_MAU = "CHON_MAU"                # Đỏ do chọn ngẫu nhiên (lớp 3)
KHONG_CHON = "KHONG_CHON"            # Xanh: không bị chọn

THU_TU_LY_DO = (VUOT_PM, VUOT_TE, CHUA_QUY_DOI, CHUA_RO_TIEN_TE, NGHI_CHIA_NHO,
                CO_DO_CUNG, NOP_LAI, CHON_MAU, KHONG_CHON)
LY_DO_BAT_BUOC = frozenset({VUOT_PM, VUOT_TE, CHUA_QUY_DOI, CHUA_RO_TIEN_TE,
                            NGHI_CHIA_NHO, CO_DO_CUNG, NOP_LAI})

# ---------------------------------------------------------------- cờ (lớp 3, §4.4)

SO_TIEN_BAT_THUONG = "SO_TIEN_BAT_THUONG"
DOI_TAC_MOI = "DOI_TAC_MOI"
SO_TRON = "SO_TRON"
NGAY_NGHI = "NGAY_NGHI"
CUOI_KY = "CUOI_KY"
NHAP_TAY = "NHAP_TAY"
THU_TU_CO = (SO_TIEN_BAT_THUONG, DOI_TAC_MOI, SO_TRON, NGAY_NGHI, CUOI_KY, NHAP_TAY)

# ---------------------------------------------------------------- loại, nguồn loại

CHUA_PHAN_LOAI = "chua_phan_loai"     # mã loại dành riêng; không được có trong danh_muc_loai_json
NGUON_MODULE = "module"
NGUON_QUY_TAC = "quy_tac"
NGUON_AI = "ai"
NGUON_CHUA = "chua_phan_loai"
CAC_NGUON_LOAI = (NGUON_MODULE, NGUON_QUY_TAC, NGUON_AI, NGUON_CHUA)

# ---------------------------------------------------------------- vùng lớp 1

VUNG_BAT_BUOC = "bat_buoc"   # Đỏ không cần chọn (có ít nhất một mã trong LY_DO_BAT_BUOC)
VUNG_CHON_MAU = "chon_mau"   # SAD <= số tiền < TE
VUNG_DUOI_SAD = "duoi_sad"   # số tiền < SAD

# ---------------------------------------------------------------- kết quả kiểm (§5.3)

KQ_DAT, KQ_SAI, KQ_KHONG_KIEM = "dat", "sai", "khong_kiem"
MUC_NHO, MUC_SAD, MUC_TE = "nho", "sad", "te"
MAU_CHON, MAU_BAT_BUOC, MAU_NGOAI = "chon_mau", "bat_buoc", "ngoai_mau"

# ---------------------------------------------------------------- nhãn bảng tỷ lệ

NHAN_RUI_RO_CAO = "rui_ro_cao"
NHAN_LOI_NGOAI_MAU = "loi_ngoai_mau"
CHE_DO_BAC = "bac"            # đang theo bậc thang
CHE_DO_TOAN_BO = "toan_bo"    # 100% sau lỗi >= TE


@dataclass(frozen=True)
class KetQuaDong:
    """Quyết định cuối cho một dòng. KHÔNG chứa xác suất, tỷ lệ, bậc (C5)."""
    ma: str
    luong: str                     # "do" | "xanh"
    ly_do: tuple[str, ...]         # >= 1 mã theo THU_TU_LY_DO; Xanh chỉ có (KHONG_CHON,)
    co: tuple[str, ...]            # cờ đã bật, theo THU_TU_CO (không kèm hệ số)
    loai: str
    nguon_loai: str


def noi_ly_do(ly_do) -> str:
    """Chuỗi lưu cột dong_luot.ly_do: các mã theo THU_TU_LY_DO, nối bằng dấu phẩy."""
    tap = set(ly_do)
    return ",".join(m for m in THU_TU_LY_DO if m in tap)


def tach_ly_do(chuoi: str) -> tuple[str, ...]:
    return tuple(m for m in (chuoi or "").split(",") if m)
