"""Chốt tháng qua ngăn Core; gọi ở đầu mỗi năng lực.

Bản chụp được giữ trước khi tính lại cửa sổ 365 ngày do Core lọc hạn.
SDK chỉ trả da_tao sau khi ghi lô: tạo bản chốt và cập nhật CAS là hai
lô riêng. Lô cập nhật gộp tỷ lệ và hồ sơ hành vi, đọc lại khi xung đột.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import re

from . import ngan_chung
from .kieu import (
    KQ_DAT, KQ_SAI, MAU_CHON, MAU_NGOAI, MUC_SAD, MUC_TE,
    NHAN_LOI_NGOAI_MAU, NHAN_RUI_RO_CAO,
)
from .loi import loi
from .thong_ke import can_tren
from .ty_le import ChinhSach, TrangThai, tu_ban_ghi, ve_ban_ghi


_GIO_VN = timezone(timedelta(hours=7))


def ky_hien_tai(luc: datetime | None = None) -> str:
    """Kỳ theo UTC+7; datetime không có múi giờ được hiểu là giờ Việt Nam."""
    if luc is None:
        luc = datetime.now(_GIO_VN)
    elif not isinstance(luc, datetime):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if luc.tzinfo is None or luc.utcoffset() is None:
        luc = luc.replace(tzinfo=_GIO_VN)
    luc = luc.astimezone(_GIO_VN)
    return f"{luc.year:04d}-{luc.month:02d}"


def ky_truoc(ky: str) -> str:
    """Trả tháng liền trước, kể cả khi chuyển sang năm trước."""
    if not isinstance(ky, str) or not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", ky):
        raise loi("THAM_SO_KHONG_HOP_LE")
    nam, thang = map(int, ky.split("-"))
    if nam == 0 or (nam == 1 and thang == 1):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if thang == 1:
        nam, thang = nam - 1, 12
    else:
        thang -= 1
    return f"{nam:04d}-{thang:02d}"


def _tinh_lai(viec, tt: TrangThai, cs: ChinhSach) -> TrangThai:
    """Chỉ tính số liệu 12 tháng; giữ bậc và bộ đếm từ lần đổi bậc.

    Không truyền gom_het_han: ngăn Core áp dụng giu_toi_da_ngay=365.
    Cận trên dùng chung thong_ke; điều kiện nhãn như doi_bac.cap_nhat.
    """
    mau = loi_mau = loi_sad = loi_ngoai = 0
    ds = ngan_chung.tim_tat_ca(viec, "ket_qua_kiem", {"khau": tt.khau, "loai": tt.loai})
    for ban in ds:
        viec.kiem_huy()
        kq = ban.gia_tri
        if kq.get("ket_qua") not in {KQ_DAT, KQ_SAI}:
            continue
        sai = kq["ket_qua"] == KQ_SAI
        if kq.get("nguon_mau") == MAU_CHON:
            mau += 1
            loi_mau += int(sai)
        loi_sad += int(sai and kq.get("muc_sai") in {MUC_SAD, MUC_TE})
        loi_ngoai += int(sai and kq.get("nguon_mau") == MAU_NGOAI)

    diem = can_tren(loi_mau, mau, cs.do_tin_cay) if mau else None
    nhan = set(tt.nhan) - {NHAN_RUI_RO_CAO, NHAN_LOI_NGOAI_MAU}
    if loi_sad > 0 or (diem is not None and diem > cs.nguong_diem_rui_ro):
        nhan.add(NHAN_RUI_RO_CAO)
    if loi_ngoai > 0:
        nhan.add(NHAN_LOI_NGOAI_MAU)
    return replace(tt, mau_12t=mau, loi_12t=loi_mau, loi_sad_12t=loi_sad,
                   loi_ngoai_mau_12t=loi_ngoai, diem=diem, nhan=frozenset(nhan))


def _chot_mot(viec, cs, khoa, kt, ky_moi, lam_moi_ho_so) -> bool:
    lo_chot = None

    def tao_chot(lo):
        nonlocal lo_chot
        # Không gửi cột hệ thống hoặc chi tiết giao dịch vào bản chụp C4.
        ban = viec.ngan.doc("ty_le", khoa)
        if ban is None:
            raise loi("NGAN_BAN")
        lo.lay_hoac_tao("chot_ky", {"ky": kt, **khoa}, ve_ban_ghi(tu_ban_ghi(ban.gia_tri)))
        lo_chot = lo

    ngan_chung.ghi_lo_thu_lai(viec, tao_chot)
    if not lo_chot.ket_qua[0].da_tao:
        return False

    def cap_nhat(lo):
        # Mọi lần thử lại đều đọc lại dữ liệu và row_version của cả hai bảng.
        ban = viec.ngan.doc("ty_le", khoa)
        if ban is None:
            raise loi("NGAN_BAN")
        tt = _tinh_lai(viec, tu_ban_ghi(ban.gia_tri), cs)
        lo.sua("ty_le", khoa, ve_ban_ghi(tt), row_version=ban.row_version)
        if lam_moi_ho_so is not None:
            ho_so = viec.ngan.doc("ho_so_hanh_vi", khoa)
            if ho_so is not None:
                gia_tri = lam_moi_ho_so(ho_so.gia_tri, ky_moi)
                lo.sua("ho_so_hanh_vi", khoa, gia_tri, row_version=ho_so.row_version)

    ngan_chung.ghi_lo_thu_lai(viec, cap_nhat)
    return True


def chot_neu_can(
    viec,
    cs: ChinhSach,
    *,
    luc: datetime | None = None,
    lam_moi_ho_so: Callable[[dict, str], dict] | None = None,
) -> int:
    """Chốt tháng trước cho các cặp chưa chốt; trả số cặp vừa tạo bản chốt.

    Chỉ bên nhận da_tao=True mới cập nhật số liệu/hồ sơ. Callback làm mới
    cần thuần vì có thể được gọi lại khi CAS xung đột. Nếu lô cập nhật
    thất bại sau khi tạo bản chốt, bản chốt vẫn còn (giới hạn SDK 2.2.0).
    """
    ky_moi = ky_hien_tai(luc)
    kt = ky_truoc(ky_moi)
    cac_ty_le = ngan_chung.tim_tat_ca(viec, "ty_le", {})
    da_chot = {
        (ban.gia_tri["khau"], ban.gia_tri["loai"])
        for ban in ngan_chung.tim_tat_ca(viec, "chot_ky", {"ky": kt})
    }
    so_chot = 0
    for ban in cac_ty_le:
        viec.kiem_huy()
        khoa = {"khau": ban.gia_tri["khau"], "loai": ban.gia_tri["loai"]}
        cap = (khoa["khau"], khoa["loai"])
        if cap not in da_chot and _chot_mot(viec, cs, khoa, kt, ky_moi, lam_moi_ho_so):
            so_chot += 1
            da_chot.add(cap)
    return so_chot
