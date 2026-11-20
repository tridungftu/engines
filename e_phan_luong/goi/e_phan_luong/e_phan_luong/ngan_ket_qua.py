"""Ghi kết quả kiểm và thống kê qua ngăn Core, theo Q1/Q2/Q6/Q7.

Mỗi lô nguyên tử gồm tối đa 99 kết quả và một sửa CAS bảng ty_le.
Tệp có nhiều lô có thể đã ghi các lô trước khi lô sau báo lỗi; gửi lại
an toàn nhờ khóa duy nhất của ket_qua_kiem. Không lưu chi tiết giao dịch.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re

from . import doi_bac, ket_qua, ngan_chung, nguong, ty_le
from .kieu import CHUA_PHAN_LOAI, KQ_SAI, MAU_NGOAI
from .loi import loi
from .phan_loai import doc_danh_muc_loai


@dataclass(frozen=True)
class _DongGhi:
    gia_tri: dict
    sua_loai: bool

    @property
    def khoa(self) -> dict:
        return {cot: self.gia_tri[cot] for cot in ("ma_luot", "ma", "khau")}


def _da_ghi(viec, dong: _DongGhi) -> bool:
    # Lượt giữ 400 ngày, kết quả 365 ngày: dòng đã ẩn vẫn là dấu chống trùng.
    return viec.ngan.doc("ket_qua_kiem", dong.khoa, gom_het_han=True) is not None


def _chuan_bi(viec, tep: ket_qua.KetQuaTep) -> dict[tuple[str, str], list[_DongGhi]]:
    """Kiểm toàn bộ tệp trước lệnh ghi đầu tiên, giữ thứ tự chi_so mỗi cặp."""
    ts = viec.tham_so
    khau = ts.get("khau")
    ma_module = ts.get("ma_module", "")
    if (not isinstance(khau, str)
            or re.fullmatch(r"[a-z][a-z0-9_]{0,39}", khau) is None
            or not isinstance(ma_module, str)
            or (ma_module and re.fullmatch(r"[a-z][a-z0-9_]{0,30}", ma_module) is None)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if ma_module and ma_module != tep.ma_module:
        raise loi("DU_LIEU_KHONG_HOP_LE")

    danh_muc = doc_danh_muc_loai(ts.get("danh_muc_loai_json"))
    ng = None
    if any(d.ket_qua == KQ_SAI for d in tep.dong):
        nguong_json = ts.get("nguong_json")
        if nguong_json is not None and not isinstance(nguong_json, str):
            raise loi("THAM_SO_KHONG_HOP_LE")
        ng = nguong.doc_nguong(tep.nguong, nguong_json)

    nhom = {}
    cac_luot = {}
    for dong in sorted(tep.dong, key=lambda d: d.chi_so):
        viec.kiem_huy()
        if dong.ma_luot not in cac_luot:
            cac_luot[dong.ma_luot] = viec.ngan.doc("luot", {"ma_luot": dong.ma_luot})
        luot = cac_luot[dong.ma_luot]
        if luot is None:
            raise loi("LUOT_KHONG_TON_TAI")
        if (dong.khau != khau or luot.gia_tri.get("khau") != dong.khau
                or luot.gia_tri.get("ma_module") != tep.ma_module):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        if (dong.loai_dung is not None and dong.loai_dung != CHUA_PHAN_LOAI
                and dong.loai_dung not in danh_muc):
            raise loi("DU_LIEU_KHONG_HOP_LE")

        ban_ghi = viec.ngan.doc("dong_luot", {"ma_luot": dong.ma_luot, "ma": dong.ma})
        dong_luot = {} if ban_ghi is None else ban_ghi.gia_tri
        if ban_ghi is not None and (dong_luot.get("ma_module") != tep.ma_module
                                   or dong_luot.get("khau") != dong.khau):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        loai_goc = dong_luot.get("loai")
        loai = dong.loai_dung or loai_goc or CHUA_PHAN_LOAI
        sua_loai = (ban_ghi is not None and dong.loai_dung is not None
                    and dong.loai_dung != loai_goc)
        muc_sai = ket_qua.muc_sai(dong.so_tien_sai, ng) if dong.ket_qua == KQ_SAI else None
        gia_tri = {
            "ma_luot": dong.ma_luot, "ma": dong.ma, "khau": dong.khau,
            "ma_module": tep.ma_module, "loai": loai, "ket_qua": dong.ket_qua,
            "muc_sai": muc_sai, "nguon_mau": ket_qua.nguon_mau(dong_luot.get("ly_do")),
            "nguon_loai_sai": dong_luot.get("nguon_loai") if sua_loai else None,
        }
        nhom.setdefault((dong.khau, loai), []).append(_DongGhi(gia_tri, sua_loai))
    return nhom


def _tao_cap_moi(viec, khoa: dict, dong: list[_DongGhi], cs: ty_le.ChinhSach) -> None:
    """Tạo nền bằng lay_hoac_tao; luôn đọc lại nền trước khi sửa CAS."""
    def lap_lenh(lo):
        if (viec.ngan.doc("ty_le", khoa) is None
                and any(not _da_ghi(viec, d) for d in dong)):
            lo.lay_hoac_tao("ty_le", khoa, ty_le.ve_ban_ghi(
                ty_le.moi(khoa["khau"], khoa["loai"], cs)))

    ngan_chung.ghi_lo_thu_lai(viec, lap_lenh)


def ghi_ket_qua(viec, tep: ket_qua.KetQuaTep) -> dict[str, int]:
    """Trả số đếm của các lô đã ghi; không trả tỷ lệ hay trạng thái bậc.

    Trong mỗi lần thử lại: đọc lại ty_le và dấu chống trùng, tính lại toàn
    bộ lô. Chỉ cộng số đếm sau khi lô được Core xác nhận thành công.
    """
    cs = ty_le.doc_chinh_sach(viec.tham_so.get("chinh_sach_json"))
    cac_nhom = _chuan_bi(viec, tep)
    tong = {"so_dong_nhan": 0, "so_trung": tep.so_trung_trong_tep,
            "so_ngoai_mau": 0, "so_sua_loai": 0}
    cap_da_doi = set()
    for cap, dong in cac_nhom.items():
        khoa = dict(zip(("khau", "loai"), cap))
        _tao_cap_moi(viec, khoa, dong, cs)
        for dau in range(0, len(dong), 99):
            nhom = dong[dau:dau + 99]
            dem = {}
            da_doi = False

            def lap_lenh(lo):
                nonlocal dem, da_doi
                dem = {cot: 0 for cot in tong}
                da_doi = False
                ban_ghi = viec.ngan.doc("ty_le", khoa)
                tt = None if ban_ghi is None else ty_le.tu_ban_ghi(ban_ghi.gia_tri)
                luc = datetime.now(timezone.utc).isoformat()
                for d in nhom:
                    viec.kiem_huy()
                    if _da_ghi(viec, d):
                        dem["so_trung"] += 1
                        continue
                    # Cặp mới đã tạo bằng lay_hoac_tao, không ghi đè nền cũ.
                    if tt is None:
                        raise loi("NGAN_BAN")
                    gt = d.gia_tri
                    tt, doi = doi_bac.cap_nhat(tt, doi_bac.MotKetQua(
                        gt["nguon_mau"], gt["ket_qua"], gt["muc_sai"]), cs, luc=luc)
                    da_doi = da_doi or doi
                    # them phải xung đột nếu việc khác vừa ghi cùng kết quả.
                    lo.them("ket_qua_kiem", gt)
                    dem["so_dong_nhan"] += 1
                    dem["so_ngoai_mau"] += int(gt["nguon_mau"] == MAU_NGOAI)
                    dem["so_sua_loai"] += int(d.sua_loai)
                if dem["so_dong_nhan"]:
                    lo.sua("ty_le", khoa, ty_le.ve_ban_ghi(tt), row_version=ban_ghi.row_version)

            ngan_chung.ghi_lo_thu_lai(viec, lap_lenh)
            for cot in tong:
                tong[cot] += dem[cot]
            if da_doi:
                cap_da_doi.add(cap)
    return {**tong, "so_cap_doi_bac": len(cap_da_doi)}
