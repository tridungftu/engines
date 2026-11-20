"""Chốt tháng qua ngăn Core; gọi ở đầu mỗi năng lực.

Bản chụp trước tính lại, tỷ lệ mới và hồ sơ được ghi trong cùng một lô
nguyên tử. Tranh khóa bản chốt hoặc CAS đều đọc lại trước khi thử lại.
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
    khoa_chot = {"ky": kt, **khoa}
    da_chot = False

    def cap_nhat(lo):
        nonlocal da_chot
        da_chot = False
        # them tranh khóa duy nhất: bên thua đọc lại và dừng, không tính lại.
        if viec.ngan.doc("chot_ky", khoa_chot) is not None:
            return
        ban = viec.ngan.doc("ty_le", khoa)
        if ban is None:
            raise loi("NGAN_BAN")
        cu = tu_ban_ghi(ban.gia_tri)
        lo.them("chot_ky", {**khoa_chot, **ve_ban_ghi(cu)})
        tt = _tinh_lai(viec, cu, cs)
        lo.sua("ty_le", khoa, ve_ban_ghi(tt), row_version=ban.row_version)
        if lam_moi_ho_so is not None:
            ho_so = viec.ngan.doc("ho_so_hanh_vi", khoa)
            if ho_so is not None and ho_so.gia_tri.get("ky_lam_moi") != ky_moi:
                gia_tri = lam_moi_ho_so(ho_so.gia_tri, ky_moi)
                lo.sua("ho_so_hanh_vi", khoa, gia_tri, row_version=ho_so.row_version)
        da_chot = True

    ngan_chung.ghi_lo_thu_lai(viec, cap_nhat)
    return da_chot


def _lam_moi_mot(viec, khoa, ky_moi, lam_moi_ho_so):
    """Hồ sơ có thể tồn tại trước kết quả kiểm đầu tiên (chưa có ty_le)."""
    def cap_nhat(lo):
        ban = viec.ngan.doc("ho_so_hanh_vi", khoa)
        if ban is not None and ban.gia_tri.get("ky_lam_moi") != ky_moi:
            gia_tri = lam_moi_ho_so(ban.gia_tri, ky_moi)
            lo.sua("ho_so_hanh_vi", khoa, gia_tri, row_version=ban.row_version)

    ngan_chung.ghi_lo_thu_lai(viec, cap_nhat)


def _tao_tu_ky(ban_ty_le, ky_moi: str) -> bool:
    """Không chốt tháng trước cho cặp vừa tạo trong tháng hiện tại.

    Dùng thời điểm hệ thống do Core cấp, không dùng ngày nghiệp vụ hoặc
    thời điểm đổi bậc. Cặp này sẽ được chốt ở tháng sau.
    """
    tao_luc = ban_ty_le.gia_tri.get("tao_luc")
    if tao_luc is None:
        return False
    luc = datetime.fromisoformat(tao_luc)
    if luc.tzinfo is None:
        luc = luc.replace(tzinfo=_GIO_VN)
    luc = luc.astimezone(_GIO_VN)
    return f"{luc.year:04d}-{luc.month:02d}" >= ky_moi


def chot_neu_can(
    viec,
    cs: ChinhSach,
    *,
    luc: datetime | None = None,
    lam_moi_ho_so: Callable[[dict, str], dict] | None = None,
) -> int:
    """Chốt tháng trước cho các cặp chưa chốt; trả số cặp vừa tạo bản chốt.

    Bản chốt và cập nhật CAS cùng thành công hoặc cùng không ghi. Callback
    làm mới cần thuần vì có thể được gọi lại khi CAS/tranh khóa xung đột.
    Hồ sơ chưa có tỷ lệ cũng được làm mới; không tính vào số cặp chốt.
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
        if _tao_tu_ky(ban, ky_moi):
            continue
        khoa = {"khau": ban.gia_tri["khau"], "loai": ban.gia_tri["loai"]}
        cap = (khoa["khau"], khoa["loai"])
        if cap not in da_chot and _chot_mot(viec, cs, khoa, kt, ky_moi, lam_moi_ho_so):
            so_chot += 1
            da_chot.add(cap)
    if lam_moi_ho_so is not None:
        for ban in ngan_chung.tim_tat_ca(viec, "ho_so_hanh_vi", {}):
            if ban.gia_tri.get("ky_lam_moi") != ky_moi:
                khoa = {"khau": ban.gia_tri["khau"], "loai": ban.gia_tri["loai"]}
                _lam_moi_mot(viec, khoa, ky_moi, lam_moi_ho_so)
    return so_chot
