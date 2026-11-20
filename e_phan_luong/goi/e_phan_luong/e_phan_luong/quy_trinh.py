"""Đường chạy chung của các năng lực phân luồng (lead tách ở đầu PL-4, 20/11/2026).

Mỗi hàm là một ĐIỂM NỐI có chủ sở hữu riêng để các lát ghép song song không sửa chồng:
- bat_dau          → PL-4 (chốt kỳ tháng ở lượt đầu tiên của tháng mới, mọi năng lực)
- doc_tep_lo       → PL-6 (thêm Excel/CSV theo khuôn cột)
- doc_cai_dat      → chung (lead)
- chay_phan_luong  → PL-4 (hồ sơ hành vi: cờ, chia nhỏ qua lô, cập nhật hồ sơ);
                     PL-5/PL-7 chỉ GỌI hàm này (loai_ai, canh_bao_them), không sửa thân
- xuat_ket_qua     → PL-8 (tệp Excel danh sách Đỏ)
Không đổi hành vi so với PL-2/PL-3.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256

from . import __version__, chon_mau, ngan_luot
from .doc_lo import doc_lo_json
from .kieu import KetQuaDong, Lo, Nguong
from .loi import loi
from .nguong import doc_nguong
from .phan_loai import BoPhanLoai, doc_bo_phan_loai, doc_danh_muc_loai
from .phan_luong import xet_lop1_lo, xet_lop23_lo
from .ty_le import ChinhSach, doc_chinh_sach
from .xuat_json import tao_tep_json, tao_truong_ra


@dataclass(frozen=True)
class CaiDat:
    nguong: Nguong
    danh_muc: dict[str, dict]
    bo: BoPhanLoai
    cs: ChinhSach


def bat_dau(viec) -> int:
    """Gọi đầu MỌI năng lực. PL-4 nối chốt kỳ tháng tại đây; trả số cặp đã chốt."""
    return 0


def doc_tep_lo(viec) -> tuple[Lo, bytes]:
    """Đọc JSON hoặc bảng theo khuôn cột; giữ bytes gốc để băm kiểm toán."""
    from . import doc_bang

    tep = viec.dau_vao["tep"]
    with viec.mo_tep(tep["tep_id"]) as f:
        du_lieu = f.read(doc_bang.TOI_DA_BYTE + 1)
    kieu = doc_bang.nhan_dien(du_lieu, tep.get("ten"), tep.get("mime"))
    if kieu == "json":
        return doc_lo_json(du_lieu), du_lieu
    ts = viec.tham_so
    khuon, ma_module = ts.get("khuon_cot_json"), ts.get("ma_module")
    if (not isinstance(khuon, str) or not khuon.strip()
            or not isinstance(ma_module, str) or not ma_module.strip()):
        raise loi("THAM_SO_KHONG_HOP_LE")
    lo = doc_bang.doc_lo_bang(
        du_lieu, kieu, khuon_cot_json=khuon, ma_module=ma_module,
        tien_te=ts.get("tien_te") or None, ky=ts.get("ky") or None,
    )
    return lo, du_lieu


def _so_tham_so(gia_tri) -> Decimal | None:
    if gia_tri is None:
        return None
    # Cổng SDK trả số JSON bằng float; đổi qua chuỗi, không Decimal(float).
    if isinstance(gia_tri, bool) or not isinstance(gia_tri, (int, float, Decimal)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    return Decimal(str(gia_tri))


def doc_chinh_sach_buoc(tham_so: Mapping[str, object]) -> ChinhSach:
    return doc_chinh_sach(tham_so.get("chinh_sach_json"),
                          ty_le_duoi_sad=_so_tham_so(tham_so.get("ty_le_duoi_sad")))


def doc_cai_dat(tham_so: Mapping[str, object], lo: Lo) -> CaiDat:
    ng = doc_nguong(lo.nguong, tham_so.get("nguong_json"))
    danh_muc = doc_danh_muc_loai(tham_so.get("danh_muc_loai_json"))
    bo = doc_bo_phan_loai(tham_so.get("bo_phan_loai_json"), danh_muc)
    return CaiDat(ng, danh_muc, bo, doc_chinh_sach_buoc(tham_so))


def chay_phan_luong(viec, lo: Lo, du_lieu: bytes, *,
                    loai_ai: Mapping[str, str] | None = None,
                    canh_bao_them: Sequence[str] = ()) -> dict:
    """Lớp 1 → 2 → 3, tệp kết quả, ghi lượt (dong_luot trước, luot sau cùng).

    loai_ai: mã nghiệp vụ → loại do Local AI gán (PL-5); chỉ dùng cho dòng chưa có loại
    từ module/quy tắc. canh_bao_them: câu cảnh báo bổ sung (không chứa tỷ lệ, C5).
    """
    ts = viec.tham_so
    viec.tien_do(10, "Đang kiểm tra lô nghiệp vụ.")
    cd = doc_cai_dat(ts, lo)
    ds_lop1 = xet_lop1_lo(lo, ts, nguong=cd.nguong, danh_muc=cd.danh_muc, bo=cd.bo,
                          truong_phan_loai=ts.get("truong_phan_loai"), loai_ai=loai_ai)
    hat_giong = chon_mau.sinh_hat_giong()
    bam_dau_vao = "sha256:" + sha256(du_lieu).hexdigest()
    # Hạt giống mới tạo lượt mới; ghim hạt giống + đầu vào tái hiện cả mã lượt.
    ma_luot = "PL-" + sha256(b"\x1f".join((
        hat_giong, lo.ma_module.encode("utf-8"), ts["khau"].encode("utf-8"),
        bam_dau_vao.encode("ascii"),
    ))).hexdigest()
    thong_tin = {
        "ma_luot": ma_luot, "bam_hat_giong": chon_mau.bam_hat_giong(hat_giong),
        "bam_dau_vao": bam_dau_vao, "phien_ban_engine": __version__,
        "khau": ts["khau"], "ma_module": lo.ma_module,
    }
    viec.tien_do(50, "Đang chọn mẫu kiểm tra.")
    ds_dong = xet_lop23_lo(viec, lo, ds_lop1, khau=ts["khau"], cs=cd.cs, hat_giong=hat_giong)
    truong = xuat_ket_qua(viec, lo, cd.nguong, ds_dong, thong_tin=thong_tin,
                          canh_bao_them=canh_bao_them)
    viec.tien_do(90, "Đang ghi kết quả lượt phân luồng.")
    ngan_luot.ghi_luot(viec, {
        "ma_luot": ma_luot, "ma_module": lo.ma_module, "khau": ts["khau"],
        "hat_giong": hat_giong.hex(), "bam_dau_vao": bam_dau_vao,
    }, ds_dong)
    return truong


def xuat_ket_qua(viec, lo: Lo, ng: Nguong, ds_dong: Sequence[KetQuaDong], *,
                 thong_tin: dict, canh_bao_them: Sequence[str] = ()) -> dict:
    """Tải JSON và Excel dòng Đỏ lên Core; lô không có Đỏ trả tep_ds_do null."""
    noi_dung = tao_tep_json(ds_dong, thong_tin=thong_tin)
    tep_json = viec.tai_tep_ra("phan-luong.json", noi_dung, "application/json")
    truong = tao_truong_ra(lo, ng, ds_dong, thong_tin=thong_tin, tep_json=tep_json)
    if any(d.luong == "do" for d in ds_dong):
        # Nạp khi cần Excel; đường import khung không buộc nạp thư viện Excel.
        from . import xuat_excel

        du_lieu = xuat_excel.lap_ds_do(ds_dong, **{
            cot: thong_tin[cot]
            for cot in ("ma_luot", "ma_module", "khau", "phien_ban_engine")
        })
        truong["tep_ds_do"] = viec.tai_tep_ra(
            "ds-can-kiem.xlsx", du_lieu,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if canh_bao_them:
        them = "; ".join(c for c in canh_bao_them if c)
        cu = truong.get("canh_bao") or ""
        truong["canh_bao"] = ((cu + "; " if cu else "") + them)[:500]
    return truong
