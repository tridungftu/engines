"""Đọc trạng thái và ghi dấu hoàn tất lượt qua ngăn Core (PL-2)."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from hashlib import sha256

from .kieu import CHON_MAU, KQ_DAT, KQ_SAI, LY_DO_BAT_BUOC, KetQuaDong, noi_ly_do, tach_ly_do
from .ngan_chung import ghi_lay_hoac_tao_nhieu, ghi_lo_thu_lai, tim_tat_ca
from .ty_le import ChinhSach, TrangThai, moi, tu_ban_ghi


def ma_luot_cua_viec(viec, bam_dau_vao: str) -> str:
    """Mã lượt theo việc Core và đầu vào, độc lập với hạt giống chọn mẫu."""
    chuoi = "e_phan_luong|luot|" + viec.id + "|" + bam_dau_vao
    return "PL-" + sha256(chuoi.encode("utf-8")).hexdigest()


def doc_ty_le(viec, khau: str, loai: str, cs: ChinhSach) -> TrangThai:
    """Cặp mới dùng chính sách khởi đầu trong RAM, không tạo bản ghi ngăn."""
    bg = viec.ngan.doc("ty_le", {"khau": khau, "loai": loai})
    return moi(khau, loai, cs) if bg is None else tu_ban_ghi(bg.gia_tri)


def tra_nop_lai(viec, ma_module: str, khau: str, ds_ma: Sequence[str]) -> frozenset[str]:
    """Q5: chỉ giữ Đỏ của lượt hoàn tất gần nhất chưa có kết quả dat/sai.

    Dòng của lượt ghi dở không có dấu luot bị bỏ qua. So thời điểm có múi giờ,
    không so thứ tự ma_luot hoặc thời điểm riêng của dong_luot. Nếu hai lượt
    trùng thời điểm, dùng ma_luot làm khóa phụ ổn định. Bỏ qua chính lượt
    của việc Core hiện tại để giao lại không tự sinh lý do NOP_LAI.
    """
    cac_ma = dict.fromkeys(ds_ma)
    if not cac_ma:
        return frozenset()
    dong_theo_ma = _quet_dong_nop_lai(viec, ma_module, khau, cac_ma)
    if dong_theo_ma == {}:
        return frozenset()
    luot_da_doc = {}
    ung_vien_theo_luot = {}
    for ma in cac_ma:
        viec.kiem_huy()
        ds = (tim_tat_ca(viec, "dong_luot", {"ma_module": ma_module, "khau": khau, "ma": ma})
              if dong_theo_ma is None else dong_theo_ma.get(ma, ()))
        gan_nhat = None
        for bg in ds:
            dong = bg.gia_tri
            ma_luot = dong["ma_luot"]
            if ma_luot == getattr(viec, "_ma_luot_phan_luong", None):
                continue
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
        ung_vien_theo_luot.setdefault(dong["ma_luot"], {})[ma] = None
    nop_lai = set()
    for ma_luot, cac_ma_luot in ung_vien_theo_luot.items():
        ket_qua_theo_ma = _quet_ket_qua_nop_lai(viec, ma_luot, khau, cac_ma_luot)
        for ma in cac_ma_luot:
            viec.kiem_huy()
            kq = (viec.ngan.doc("ket_qua_kiem", {"ma_luot": ma_luot, "ma": ma, "khau": khau},
                               gom_het_han=True)
                  if ket_qua_theo_ma is None else ket_qua_theo_ma.get(ma))
            if kq is None or kq.gia_tri["ket_qua"] not in {KQ_DAT, KQ_SAI}:
                nop_lai.add(ma)
    return frozenset(nop_lai)


def _quet_ket_qua_nop_lai(viec, ma_luot, khau, cac_ma):
    """Quét kết quả của một lượt, chỉ giữ mã ứng viên, kể cả đã hết hạn.

    Hết trong max(1, ceil(số ứng viên / 10)) trang 500 dòng thì dùng kết quả.
    Vượt ngân sách trả None, bỏ kết quả dở để đọc lại từng mã như trước PL-9H.
    """
    from .loi import loi

    loc = {"ma_luot": ma_luot, "khau": khau}
    sap_xep = [{"truong": cot, "giam": False} for cot in ("ma_luot", "ma", "khau")]
    ket_qua_theo_ma = {}
    tiep = None
    da_gap = set()
    for _ in range(max(1, (len(cac_ma) + 9) // 10)):
        viec.kiem_huy()
        trang = viec.ngan.tim("ket_qua_kiem", loc=loc, sap_xep=sap_xep,
                             gioi_han=500, tiep=tiep, gom_het_han=True)
        for bg in trang.danh_sach:
            viec.kiem_huy()
            ma = bg.gia_tri["ma"]
            if ma in cac_ma:
                ket_qua_theo_ma[ma] = bg
        tiep = trang.tiep
        if tiep is None:
            return ket_qua_theo_ma
        if tiep in da_gap:
            raise loi("NGAN_BAN")
        da_gap.add(tiep)
    return None


def _quet_dong_nop_lai(viec, ma_module, khau, cac_ma):
    """Chỉ giữ dòng thuộc mã cần tra; None nghĩa là quay về tìm từng mã.

    Dò rỗng một lần, rồi quét tối đa ceil(số mã / 10) trang 500 dòng.
    Chưa hết lịch sử thì bỏ toàn bộ kết quả quét trước khi quay về đường cũ.
    Phụ phí tìm tối đa 1 + ceil(số mã / 10), kể cả khi số mã không chia hết 10.
    Trần mỗi mã giống tim_tat_ca, không áp trần lên toàn lịch sử module/khâu.
    """
    from .loi import loi

    loc = {"ma_module": ma_module, "khau": khau}
    sap_xep = [{"truong": cot, "giam": False} for cot in ("ma_luot", "ma")]
    viec.kiem_huy()
    if not viec.ngan.tim("dong_luot", loc=loc, gioi_han=1).danh_sach:
        return {}

    dong_theo_ma = {}
    tiep = None
    da_gap = set()
    for _ in range(max(1, (len(cac_ma) + 9) // 10)):
        viec.kiem_huy()
        trang = viec.ngan.tim("dong_luot", loc=loc, sap_xep=sap_xep,
                             gioi_han=500, tiep=tiep)
        for bg in trang.danh_sach:
            viec.kiem_huy()
            ma = bg.gia_tri["ma"]
            if ma in cac_ma:
                ds = dong_theo_ma.setdefault(ma, [])
                ds.append(bg)
                if len(ds) > 200000:
                    raise loi("VUOT_GIOI_HAN")
        tiep = trang.tiep
        if tiep is None:
            return dong_theo_ma
        if tiep in da_gap:
            raise loi("NGAN_BAN")
        da_gap.add(tiep)
    return None


def ghi_luot(viec, luot: dict, ds_dong: Sequence[KetQuaDong], *,
             lenh_cuoi: Callable[[object], None] | None = None) -> None:
    """Ghi dòng trước (≤100/lô), dấu luot sau cùng; gửi lại không tạo trùng.

    lenh_cuoi(lo) (PL-4): thêm tối đa 99 lệnh vào CÙNG lô với dấu luot, chạy lại
    khi lô xung đột (phải tự đọc lại CAS). Lượt đã có dấu luot thì bỏ qua cả lô.

    Chỉ lấy danh sách cột cho phép, không chuyển toàn bộ nghiệp vụ vào ngăn.
    Các lô dòng đã ghi trước một lỗi chưa trở thành lịch sử lượt hoàn tất.
    Khi chưa có dấu luot, sửa CAS dòng còn lại từ lần chạy dở để không lẫn
    quyết định dùng hạt giống cũ. Lượt đã hoàn tất giữ nguyên các dòng.
    """
    ma_luot = luot["ma_luot"]
    ngu_canh = {cot: luot[cot] for cot in ("ma_module", "khau")}
    ds = [
        ({"ma_luot": ma_luot, "ma": dong.ma}, {
            **ngu_canh, "ly_do": noi_ly_do(dong.ly_do),
            "loai": dong.loai, "nguon_loai": dong.nguon_loai,
        }) for dong in ds_dong
    ]
    if viec.ngan.doc("luot", {"ma_luot": ma_luot}) is not None:
        return  # Lượt đã hoàn tất: giữ nguyên dòng và dấu luot.
    # Hiệu năng (PL-4 lead): đọc MỘT lần các dòng còn lại của lần chạy dở bằng tim
    # (≤500/trang) thay vì đọc từng dòng; lần đầu thường rỗng. Lô xung đột thì lần
    # thử lại đọc từng dòng của lô đó để có row_version mới.
    da_co = {bg.gia_tri["ma"]: bg for bg in tim_tat_ca(viec, "dong_luot", {"ma_luot": ma_luot})}
    for dau in range(0, len(ds), 100):
        nhom = ds[dau:dau + 100]
        lan = [0]

        def lap_lenh(lo):
            for khoa, gia_tri in nhom:
                cu = da_co.get(khoa["ma"]) if lan[0] == 0 else viec.ngan.doc("dong_luot", khoa)
                if cu is None:
                    lo.lay_hoac_tao("dong_luot", khoa, gia_tri)
                else:
                    lo.sua("dong_luot", khoa, gia_tri, row_version=cu.row_version)
            lan[0] += 1

        ghi_lo_thu_lai(viec, lap_lenh)
    gia_tri = {**ngu_canh, **{cot: luot[cot] for cot in ("hat_giong", "bam_dau_vao")}}
    if lenh_cuoi is None:
        ghi_lay_hoac_tao_nhieu(viec, "luot", [({"ma_luot": ma_luot}, gia_tri)])
        return

    def lap_cuoi(lo):
        if viec.ngan.doc("luot", {"ma_luot": ma_luot}) is not None:
            return
        lenh_cuoi(lo)
        lo.lay_hoac_tao("luot", {"ma_luot": ma_luot}, gia_tri)

    ghi_lo_thu_lai(viec, lap_cuoi)
