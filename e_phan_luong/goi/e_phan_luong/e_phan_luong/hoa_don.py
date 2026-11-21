"""Chuyển kết quả e_hoa_don thành lô trong RAM (phiếu §5.4).

Bảng ánh xạ theo e_hoa_don/engine.json, hoa_don.doc_xml@2:

    Trường nguồn                         Trường NghiepVu
    mau_so, ky_hieu, so_hoa_don,          ma = "mau_so-ky_hieu-so_hoa_don-MST"
    ma_so_thue_ban                        MST nguyên văn sau strip, giữ hậu tố chi nhánh
    ngay_lap                             ngay
    tong_thanh_toan                       so_tien (giữ số nguồn, Decimal)
    tong_thanh_toan.tien_te, don_vi_tien   so_tien.tien_te (không mặc định VND)
    ma_so_thue_ban                        doi_tac (thô, chỉ trong RAM)
    can_kiem_tra                          co_do_cung (bool)
    Cài đặt bước loai_nghiep_vu           loai

Không lấy tiền trước thuế/tiền thuế làm tổng, không tách dòng hàng thành
nghiệp vụ. Tiền tệ trong tổng được ưu tiên; thiếu thì dùng don_vi_tien,
thiếu cả hai thì None; hai mã khác nhau bị từ chối. Tổng null bị từ chối
vì không có số để tạo Tien; không suy số tiền từ DTO kỹ thuật.

hoa_don.doc_zip@1: JSON chi_tiet_nguon phiên bản 1, nguon_doc
zip_xml_strict, danh_sach_tep[].truong_hoa_don dùng cùng ánh xạ trên.
Chỉ bỏ/đếm trạng thái loi hoặc khong_ho_tro; dòng doc_duoc sai dữ liệu
và mã trùng làm lỗi cả lô. Thiếu/rỗng MST giữ mã ba phần, không bịa MST.
Mã vẫn chịu trần 120 ký tự của doc_lo. Anh duyệt 21/11/2026 (PL-10A):
MST được giữ trong mã hóa đơn ở dong_luot, ket_qua_kiem và tệp ra;
đối tác trong hồ sơ hành vi vẫn chỉ giữ băm theo GIAO-CODEX §2.4.
Không gọi e_hoa_don, Core hay đọc/ghi tệp tại đây.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal, InvalidOperation
import json

from . import doc_lo
from .kieu import Lo, NghiepVu
from .loi import loi


def _lo_rong(ma_module: str) -> Lo:
    # Tái dùng kiểm ma_module/phien_ban của bộ đọc JSON chuẩn.
    if not isinstance(ma_module, str):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return doc_lo.doc_lo_json(json.dumps({
        "phien_ban": 1, "ma_module": ma_module, "nghiep_vu": [],
    }).encode("utf-8"))


def _nghiep_vu(truong: dict, chi_so: int, loai_nghiep_vu: str | None) -> NghiepVu:
    if not isinstance(truong, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    cac_phan = [truong.get(k) for k in ("mau_so", "ky_hieu", "so_hoa_don")]
    if any(not isinstance(p, str) or not p.strip() for p in cac_phan):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    mst_ban = truong.get("ma_so_thue_ban")
    if isinstance(mst_ban, str) and mst_ban.strip():
        cac_phan.append(mst_ban.strip())
    tong = truong.get("tong_thanh_toan")
    if not isinstance(tong, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    tien_te = tong.get("tien_te")
    don_vi = truong.get("don_vi_tien")
    if tien_te is not None and don_vi is not None and tien_te != don_vi:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    # doc_lo dùng doc_tien để kiểm miền số, mã tiền tệ và từ chối float.
    return doc_lo._doc_dong({
        "ma": "-".join(cac_phan),
        "ngay": truong.get("ngay_lap"),
        "so_tien": {**tong, "tien_te": tien_te if tien_te is not None else don_vi},
        "doi_tac": truong.get("ma_so_thue_ban"),
        "co_do_cung": truong.get("can_kiem_tra", False),
        "loai": loai_nghiep_vu,
    }, chi_so)


def lo_tu_hoa_don(
    truong: dict, *, ma_module: str, loai_nghiep_vu: str | None,
) -> Lo:
    """Một bộ trường XML → một nghiệp vụ; mã nối ba phần và MST nếu có.

    Nhận phần ``phong_bi['truong']``, không nhận cả phong bì.
    ky và nguong để None, bước ghép lấy ngưỡng từ Cài đặt bước.
    """
    lo = _lo_rong(ma_module)
    return replace(lo, nghiep_vu=(_nghiep_vu(truong, 0, loai_nghiep_vu),))


def lo_tu_chi_tiet_zip(
    du_lieu: bytes, *, ma_module: str, loai_nghiep_vu: str | None,
) -> tuple[Lo, int]:
    """Đọc JSON kiểm kê ZIP, trả (lô, số tệp lỗi/chưa hỗ trợ đã bỏ).

    UTF-8 có/không BOM; cùng trần 20 MiB/50.000 dòng với doc_lo.
    Trần dòng tính cả tệp bỏ, kiểm trước ánh xạ; không cắt ngầm.
    chi_so đếm liên tục trong lô sau khi bỏ. Thư mục không là hóa đơn.
    """
    if not isinstance(du_lieu, bytes):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(du_lieu) > doc_lo.TOI_DA_BYTE:
        raise loi("VUOT_GIOI_HAN")
    try:
        bao_cao = json.loads(
            du_lieu.decode("utf-8-sig"), parse_float=Decimal,
            parse_constant=doc_lo._hang_so_khong_hop_le,
            object_pairs_hook=doc_lo._doi_tuong,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        raise loi("TEP_KHONG_HO_TRO") from None
    except (ValueError, InvalidOperation):
        raise loi("DU_LIEU_KHONG_HOP_LE") from None
    if (not isinstance(bao_cao, dict)
            or type(bao_cao.get("phien_ban")) is not int
            or bao_cao["phien_ban"] != 1
            or bao_cao.get("nguon_doc") != "zip_xml_strict"
            or not isinstance(bao_cao.get("danh_sach_tep"), list)):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ds = bao_cao["danh_sach_tep"]
    if len(ds) > doc_lo.TOI_DA_DONG:
        raise loi("VUOT_GIOI_HAN")
    lo = _lo_rong(ma_module)
    if loai_nghiep_vu is not None and not isinstance(loai_nghiep_vu, str):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    nghiep_vu, cac_ma, so_bo = [], set(), 0
    for tep in ds:
        if not isinstance(tep, dict):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        trang_thai = tep.get("trang_thai_doc")
        if trang_thai in ("loi", "khong_ho_tro"):
            so_bo += 1
            continue
        if trang_thai != "doc_duoc":
            raise loi("DU_LIEU_KHONG_HOP_LE")
        nv = _nghiep_vu(tep.get("truong_hoa_don"), len(nghiep_vu), loai_nghiep_vu)
        if nv.ma in cac_ma:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        cac_ma.add(nv.ma)
        nghiep_vu.append(nv)
    return replace(lo, nghiep_vu=tuple(nghiep_vu)), so_bo


def lay_tep_chi_tiet(truong: dict) -> dict:
    """Giữ nguyên đối tượng chi_tiet_nguon, gồm tep_id và metadata.

    Bước ghép giữ đối tượng này trong đầu vào và gọi
    ``with viec.mo_tep(tep['tep_id']) as luong``. Chuỗi ID trơn không
    đáp ứng điều kiện tham chiếu của Core thật (GIAO-CODEX §4).
    """
    tep = truong.get("chi_tiet_nguon") if isinstance(truong, dict) else None
    if (not isinstance(tep, dict) or not isinstance(tep.get("tep_id"), str)
            or not tep["tep_id"].strip()):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return tep
