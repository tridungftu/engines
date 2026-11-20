"""Đọc trạng thái và ghi dấu hoàn tất lượt qua ngăn Core (PL-2)."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from .kieu import CHON_MAU, KQ_DAT, KQ_SAI, LY_DO_BAT_BUOC, KetQuaDong, noi_ly_do, tach_ly_do
from .ngan_chung import ghi_lay_hoac_tao_nhieu, tim_tat_ca
from .ty_le import ChinhSach, TrangThai, moi, tu_ban_ghi


def doc_ty_le(viec, khau: str, loai: str, cs: ChinhSach) -> TrangThai:
    """Cặp mới dùng chính sách khởi đầu trong RAM, không tạo bản ghi ngăn."""
    bg = viec.ngan.doc("ty_le", {"khau": khau, "loai": loai})
    return moi(khau, loai, cs) if bg is None else tu_ban_ghi(bg.gia_tri)


def tra_nop_lai(viec, ma_module: str, khau: str, ds_ma: Sequence[str]) -> frozenset[str]:
    """Q5: chỉ giữ Đỏ của lượt hoàn tất gần nhất chưa có kết quả dat/sai.

    Dòng của lượt ghi dở không có dấu luot bị bỏ qua. So thời điểm có múi giờ,
    không so thứ tự ma_luot hoặc thời điểm riêng của dong_luot. Nếu hai lượt
    trùng thời điểm, dùng ma_luot làm khóa phụ ổn định.
    """
    luot_da_doc = {}
    nop_lai = set()
    for ma in dict.fromkeys(ds_ma):
        ds = tim_tat_ca(viec, "dong_luot", {"ma_module": ma_module, "khau": khau, "ma": ma})
        gan_nhat = None
        for bg in ds:
            dong = bg.gia_tri
            ma_luot = dong["ma_luot"]
            if ma_luot not in luot_da_doc:
                luot_da_doc[ma_luot] = viec.ngan.doc("luot", {"ma_luot": ma_luot})
            luot = luot_da_doc[ma_luot]
            if luot is None:
                continue
            gia_tri = luot.gia_tri
            if gia_tri["ma_module"] != ma_module or gia_tri["khau"] != khau:
                continue
            khoa = (datetime.fromisoformat(gia_tri["tao_luc"]), ma_luot)
            if gan_nhat is None or khoa > gan_nhat[0]:
                gan_nhat = (khoa, dong)
        if gan_nhat is None:
            continue
        dong = gan_nhat[1]
        if not set(tach_ly_do(dong["ly_do"])) & (LY_DO_BAT_BUOC | {CHON_MAU}):
            continue
        kq = viec.ngan.doc("ket_qua_kiem", {"ma_luot": dong["ma_luot"], "ma": ma, "khau": khau})
        if kq is None or kq.gia_tri["ket_qua"] not in {KQ_DAT, KQ_SAI}:
            nop_lai.add(ma)
    return frozenset(nop_lai)


def ghi_luot(viec, luot: dict, ds_dong: Sequence[KetQuaDong]) -> None:
    """Ghi dòng trước (≤100/lô), dấu luot sau cùng; gửi lại không tạo trùng.

    Chỉ lấy danh sách cột cho phép, không chuyển toàn bộ nghiệp vụ vào ngăn.
    Các lô dòng đã ghi trước một lỗi chưa trở thành lịch sử lượt hoàn tất.
    """
    ma_luot = luot["ma_luot"]
    ngu_canh = {cot: luot[cot] for cot in ("ma_module", "khau")}
    ds = [
        ({"ma_luot": ma_luot, "ma": dong.ma}, {
            **ngu_canh, "ly_do": noi_ly_do(dong.ly_do),
            "loai": dong.loai, "nguon_loai": dong.nguon_loai,
        }) for dong in ds_dong
    ]
    ghi_lay_hoac_tao_nhieu(viec, "dong_luot", ds)
    gia_tri = {**ngu_canh, **{cot: luot[cot] for cot in ("hat_giong", "bam_dau_vao")}}
    ghi_lay_hoac_tao_nhieu(viec, "luot", [({"ma_luot": ma_luot}, gia_tri)])
