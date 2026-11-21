"""Đọc kết quả kiểm và phân mức sai theo GIAO-CODEX §2.3 (PL-3A).

Chỉ kiểm dữ liệu trong bộ nhớ. Phần ghép kiểm lượt, danh mục loại và đọc
ngưỡng dự phòng từ Cài đặt bước; khối ngưỡng ở đây giữ nguyên để chuyển tiếp.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import re
import unicodedata

from .kieu import (
    CHON_MAU, KQ_DAT, KQ_KHONG_KIEM, KQ_SAI, LY_DO_BAT_BUOC,
    MAU_BAT_BUOC, MAU_CHON, MAU_NGOAI, MUC_NHO, MUC_SAD, MUC_TE,
    Nguong, Tien, tach_ly_do,
)
from .loi import loi
from .tien import doc_so_thap_phan


TOI_DA_BYTE = 20 * 1048576
TOI_DA_DONG = 50000


@dataclass(frozen=True)
class DongKetQua:
    """Một dòng hợp lệ; chi_so là vị trí gốc trong tệp, đếm từ 0."""

    chi_so: int
    ma_luot: str
    ma: str
    khau: str
    ket_qua: str
    so_tien_sai: Tien | None
    loai_dung: str | None
    # PL-10 (H2, Anh chốt 21/11/2026): giải thích của người kiểm khi AI sai; chỉ đi qua RAM
    # sang tệp bài học, không ghi ngăn (C4). PL-10C đọc từ JSON/Excel, PL-10B bắt buộc khi AI sai.
    giai_thich: str | None = None


@dataclass(frozen=True)
class KetQuaTep:
    """Kết quả đã bỏ trùng theo (ma_luot, ma, khau), giữ thứ tự gốc."""

    ma_module: str
    nguong: dict | None
    dong: tuple[DongKetQua, ...]
    so_trung_trong_tep: int


def _tu_cap(cap: list[tuple[str, object]]) -> dict:
    ket_qua = {}
    for khoa, gia_tri in cap:
        if khoa in ket_qua:
            raise loi("DU_LIEU_KHONG_HOP_LE")
        ket_qua[khoa] = gia_tri
    return ket_qua


def _hang_so_cam(chuoi: str) -> None:
    raise loi("DU_LIEU_KHONG_HOP_LE")


def _ma_hop_le(gia_tri: object, toi_da: int | None = None) -> bool:
    return (
        isinstance(gia_tri, str)
        and bool(gia_tri.strip())
        and (toi_da is None or len(gia_tri) <= toi_da)
        and not any(unicodedata.category(ky_tu) == "Cc" for ky_tu in gia_tri)
    )


def _doc_tien(gia_tri: object) -> Tien:
    """Tiền kết quả luôn có tiền tệ; dùng chung luật đọc số của mô-đun tien."""
    if not isinstance(gia_tri, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    tien_te = gia_tri.get("tien_te")
    if not isinstance(tien_te, str) or not re.fullmatch(r"[A-Z]{3}", tien_te):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return Tien(doc_so_thap_phan(gia_tri.get("so")), tien_te)


def _doc_giai_thich(gia_tri: object) -> str | None:
    """Chuẩn hóa giải thích người kiểm; chỉ kiểm định dạng, chưa bắt buộc điền."""
    if gia_tri is None:
        return None
    if not isinstance(gia_tri, str):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    gia_tri = unicodedata.normalize("NFC", gia_tri)
    # Xuống dòng Windows (CRLF) hoặc CR đơn → LF: văn bản dán từ Windows; openpyxl
    # không lxml (đúng requirements.lock) cũng đọc CR trong ô thành LF.
    gia_tri = gia_tri.replace("\r\n", "\n").replace("\r", "\n")
    # Kiểm trước strip để ký tự điều khiển ở hai đầu cũng không bị bỏ ngầm.
    if any(unicodedata.category(c) == "Cc" and c not in "\n\t" for c in gia_tri):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    gia_tri = gia_tri.strip()
    if len(gia_tri) > 2000:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return gia_tri or None


def doc_ket_qua_json(du_lieu: bytes) -> KetQuaTep:
    """Đọc UTF-8 có/không BOM; kiểm mọi dòng trước khi bỏ trùng.

    Trần dòng tính cả dòng trùng, không cắt dữ liệu. Thiếu ngưỡng được giữ
    là None vì phần ghép còn có thể lấy nguong_json của Cài đặt bước.
    """
    if not isinstance(du_lieu, bytes):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(du_lieu) > TOI_DA_BYTE:
        raise loi("VUOT_GIOI_HAN")
    try:
        du_lieu_doc = json.loads(
            du_lieu.decode("utf-8-sig"), parse_float=Decimal,
            parse_constant=_hang_so_cam, object_pairs_hook=_tu_cap,
        )
    except (UnicodeDecodeError, ValueError, RecursionError, InvalidOperation):
        raise loi("DU_LIEU_KHONG_HOP_LE") from None
    if not isinstance(du_lieu_doc, dict):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    phien_ban = du_lieu_doc.get("phien_ban")
    ma_module = du_lieu_doc.get("ma_module")
    nguong = du_lieu_doc.get("nguong")
    ds = du_lieu_doc.get("ket_qua")
    if (type(phien_ban) is not int or phien_ban != 1
            or not isinstance(ma_module, str)
            or not re.fullmatch(r"[a-z][a-z0-9_]{0,30}", ma_module)
            or (nguong is not None and not isinstance(nguong, dict))
            or not isinstance(ds, list)):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(ds) > TOI_DA_DONG:
        raise loi("VUOT_GIOI_HAN")

    dong = []
    da_gap = set()
    so_trung = 0
    for chi_so, muc in enumerate(ds):
        if not isinstance(muc, dict):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        ma_luot, ma, khau = (muc.get(k) for k in ("ma_luot", "ma", "khau"))
        ket_qua = muc.get("ket_qua")
        loai_dung = muc.get("loai_dung")
        if (not _ma_hop_le(ma_luot) or not _ma_hop_le(ma, 120)
                or not _ma_hop_le(khau, 40)
                or ket_qua not in (KQ_DAT, KQ_SAI, KQ_KHONG_KIEM)
                or (loai_dung is not None and (
                    not isinstance(loai_dung, str)
                    or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", loai_dung)))):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        so_tien_sai = muc.get("so_tien_sai")
        if so_tien_sai is None:
            if ket_qua == KQ_SAI:
                raise loi("DU_LIEU_KHONG_HOP_LE")
        else:
            so_tien_sai = _doc_tien(so_tien_sai)
        giai_thich = _doc_giai_thich(muc.get("giai_thich"))
        khoa = (ma_luot, ma, khau)
        if khoa in da_gap:
            so_trung += 1
            continue
        da_gap.add(khoa)
        dong.append(DongKetQua(
            chi_so, ma_luot, ma, khau, ket_qua, so_tien_sai, loai_dung, giai_thich,
        ))
    return KetQuaTep(ma_module, nguong, tuple(dong), so_trung)


def muc_sai(so_tien_sai: Tien, ng: Nguong) -> str:
    """So giá trị tuyệt đối; module phải gửi tiền đã quy đổi sang tiền ngưỡng."""
    if (so_tien_sai.tien_te is None or so_tien_sai.tien_te != ng.tien_te
            or not so_tien_sai.so.is_finite()):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    gia_tri = so_tien_sai.so.copy_abs()
    if gia_tri < ng.sad.so:
        return MUC_NHO
    if gia_tri < ng.te.so:
        return MUC_SAD
    return MUC_TE


def nguon_mau(ly_do: str | None) -> str:
    """Tách mã đúng ranh giới dấu phẩy; CHON_MAU có ưu tiên theo hợp đồng."""
    tap = set(tach_ly_do(ly_do))
    if CHON_MAU in tap:
        return MAU_CHON
    if tap & LY_DO_BAT_BUOC:
        return MAU_BAT_BUOC
    return MAU_NGOAI
