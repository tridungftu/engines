"""Ngưỡng tiền, lớp 1 và phát hiện chia nhỏ theo GIAO-CODEX §2.3.

Chỉ tính trong bộ nhớ; lịch sử gộp và cách băm do bên gọi cung cấp.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Callable, Sequence
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext

from .kieu import (
    CHUA_QUY_DOI, CHUA_RO_TIEN_TE, CO_DO_CUNG, VUOT_PM, VUOT_TE,
    VUNG_BAT_BUOC, VUNG_CHON_MAU, VUNG_DUOI_SAD, NghiepVu, Nguong, Tien,
)
from .loi import loi


def _doc_tien_nguong(gia_tri: object) -> Tien:
    """Tự kiểm tiền ngưỡng, không phụ thuộc mô-đun đọc tiền của PL-1A."""
    if not isinstance(gia_tri, dict):
        raise loi("THIEU_NGUONG")
    so = gia_tri.get("so")
    tien_te = gia_tri.get("tien_te")
    if (isinstance(so, bool) or not isinstance(so, (str, int, Decimal))
            or not isinstance(tien_te, str)
            or re.fullmatch(r"[A-Z]{3}", tien_te) is None):
        raise loi("THIEU_NGUONG")
    try:
        so = Decimal(so)
    except InvalidOperation:
        raise loi("THIEU_NGUONG") from None
    if (not so.is_finite() or so <= 0 or so.adjusted() >= 18
            or so.as_tuple().exponent < -6):
        raise loi("THIEU_NGUONG")
    return Tien(so, tien_te)


def _hang_so_json_khong_hop_le(chuoi: str) -> None:
    raise ValueError


def doc_nguong(tu_tep: dict | None, tu_tham_so: str | None) -> Nguong:
    """Khối trong tệp thắng tham số, kể cả khi khối đó không hợp lệ."""
    khoi = tu_tep
    if khoi is None:
        if tu_tham_so is None or tu_tham_so.strip() == "":
            raise loi("THIEU_NGUONG")
        try:
            khoi = json.loads(tu_tham_so, parse_float=Decimal,
                              parse_constant=_hang_so_json_khong_hop_le)
        except (ValueError, TypeError, RecursionError):
            raise loi("THAM_SO_KHONG_HOP_LE") from None
        if not isinstance(khoi, dict):
            raise loi("THAM_SO_KHONG_HOP_LE")
    if not isinstance(khoi, dict):
        raise loi("THIEU_NGUONG")
    pm, te, sad = (_doc_tien_nguong(khoi.get(ten)) for ten in ("pm", "te", "sad"))
    if not (pm.tien_te == te.tien_te == sad.tien_te and sad.so < te.so <= pm.so):
        raise loi("THIEU_NGUONG")
    return Nguong(pm, te, sad)


def _gia_tri_so(t: Tien) -> Decimal:
    """Quy ước tạm §2.3: so số âm theo trị tuyệt đối, đổi tại một chỗ.

    copy_abs giữ chính xác số tiền ngay cả khi Decimal context của bên gọi thấp.
    """
    return t.so.copy_abs()


def tien_so_sanh(nv: NghiepVu, ng: Nguong) -> tuple[Tien | None, str | None]:
    if nv.so_tien_quy_doi is not None and nv.so_tien_quy_doi.tien_te == ng.tien_te:
        return Tien(_gia_tri_so(nv.so_tien_quy_doi), ng.tien_te), None
    if nv.so_tien.tien_te == ng.tien_te:
        return Tien(_gia_tri_so(nv.so_tien), ng.tien_te), None
    if nv.so_tien.tien_te is None:
        return None, CHUA_RO_TIEN_TE
    return None, CHUA_QUY_DOI


def xet_lop1(nv: NghiepVu, ng: Nguong) -> tuple[str, tuple[str, ...]]:
    tien, ly_do_tien = tien_so_sanh(nv, ng)
    ly_do = []
    if ly_do_tien is not None:
        ly_do.append(ly_do_tien)
    elif tien.so >= ng.pm.so:
        ly_do.append(VUOT_PM)
    elif tien.so >= ng.te.so:
        ly_do.append(VUOT_TE)
    if nv.co_do_cung:
        ly_do.append(CO_DO_CUNG)
    if ly_do:
        return VUNG_BAT_BUOC, tuple(ly_do)
    return (VUNG_CHON_MAU if tien.so >= ng.sad.so else VUNG_DUOI_SAD), ()


def tim_chia_nho(
    ds: Sequence[NghiepVu], ng: Nguong, *, cua_so_ngay: int = 7,
    tong_truoc: Callable[[str, date], Decimal] | None = None,
    bam: Callable[[str], str],
) -> frozenset[str]:
    """Gắn mọi dòng thuộc bất kỳ cửa sổ đủ TE, không phụ thuộc thứ tự lô.

    Chỉ cộng tiền đã đưa về tiền tệ ngưỡng. tong_truoc phải trả tổng ngày
    cùng tiền tệ ngưỡng, không chứa lại các dòng của ds (hợp đồng §2.3).
    Dùng cửa sổ trượt và đánh dấu khoảng để tránh duyệt lại mọi dòng mỗi lần
    tổng vượt ngưỡng. Có lịch sử: xét cả ngày cuối cửa sổ không có dòng mới.
    """
    if isinstance(cua_so_ngay, bool) or not isinstance(cua_so_ngay, int) or cua_so_ngay < 1:
        raise loi("THAM_SO_KHONG_HOP_LE")
    nhom = defaultdict(list)
    for nv in ds:
        if not nv.doi_tac:
            continue
        tien, _ = tien_so_sanh(nv, ng)
        if tien is not None and tien.so < ng.te.so:
            nhom[bam(nv.doi_tac)].append((nv.ngay.toordinal(), nv.ma, tien.so))

    bi_gan = set()
    # 18 chữ số nguyên + 6 số lẻ, tối đa 50.000 dòng: 40 chữ số đủ cộng chính xác.
    with localcontext() as ctx:
        ctx.prec = max(ctx.prec, 40)
        for khoa, dong in nhom.items():
            dong.sort(key=lambda muc: muc[0])
            ngay_cuoi = {muc[0] for muc in dong}
            if tong_truoc is not None:
                ngay_cuoi = {
                    d for ngay in ngay_cuoi
                    for d in range(ngay, min(date.max.toordinal(), ngay + cua_so_ngay - 1) + 1)
                }
            trai = phai = 0
            tong = Decimal(0)
            danh_dau = [0] * (len(dong) + 1)
            lich_su = {}
            for cuoi in sorted(ngay_cuoi):
                dau = max(1, cuoi - cua_so_ngay + 1)
                while phai < len(dong) and dong[phai][0] <= cuoi:
                    tong += dong[phai][2]
                    phai += 1
                while trai < phai and dong[trai][0] < dau:
                    tong -= dong[trai][2]
                    trai += 1
                tong_cua_so = tong
                if tong_truoc is not None:
                    for ngay in range(dau, cuoi + 1):
                        if ngay not in lich_su:
                            lich_su[ngay] = tong_truoc(khoa, date.fromordinal(ngay))
                        tong_cua_so += lich_su[ngay]
                if trai < phai and tong_cua_so >= ng.te.so:
                    danh_dau[trai] += 1
                    danh_dau[phai] -= 1
            so_cua_so = 0
            for i, (_, ma, _) in enumerate(dong):
                so_cua_so += danh_dau[i]
                if so_cua_so:
                    bi_gan.add(ma)
    return frozenset(bi_gan)
