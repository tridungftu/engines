"""Cập nhật thuần một kết quả kiểm theo luật GIAO-CODEX §2.3.

Số đếm 12 tháng ở đây được cộng dồn; PL-4 chịu trách nhiệm tính lại
cửa sổ khi chốt kỳ. Mẫu bắt buộc/ngoài mẫu không đi vào ước lượng.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .kieu import (
    CHE_DO_BAC, CHE_DO_TOAN_BO, CHUA_PHAN_LOAI, KQ_DAT, KQ_KHONG_KIEM,
    KQ_SAI, MAU_BAT_BUOC, MAU_CHON, MAU_NGOAI, MUC_NHO, MUC_SAD, MUC_TE,
    NHAN_LOI_NGOAI_MAU, NHAN_RUI_RO_CAO,
)
from .loi import loi
from .thong_ke import can_tren
from .ty_le import ChinhSach, TrangThai


@dataclass(frozen=True)
class MotKetQua:
    nguon_mau: str
    ket_qua: str
    muc_sai: str | None = None


def cap_nhat(
    tt: TrangThai, kq: MotKetQua, cs: ChinhSach, *, luc: str,
) -> tuple[TrangThai, bool]:
    """Trả trạng thái mới và cờ đổi bậc/chế độ; không sửa trạng thái đầu vào."""
    if kq.ket_qua == KQ_KHONG_KIEM:
        return tt, False
    if (kq.nguon_mau not in {MAU_CHON, MAU_BAT_BUOC, MAU_NGOAI}
            or kq.ket_qua not in {KQ_DAT, KQ_SAI}
            or (kq.ket_qua == KQ_SAI and kq.muc_sai not in {MUC_NHO, MUC_SAD, MUC_TE})):
        raise loi("DU_LIEU_KHONG_HOP_LE")

    sai = kq.ket_qua == KQ_SAI
    chon = kq.nguon_mau == MAU_CHON
    mau_tu_doi_bac = tt.mau_tu_doi_bac + int(chon)
    loi_tu_doi_bac = tt.loi_tu_doi_bac + int(chon and sai)
    mau_12t = tt.mau_12t + int(chon)
    loi_12t = tt.loi_12t + int(chon and sai)
    loi_sad_12t = tt.loi_sad_12t + int(sai and kq.muc_sai in {MUC_SAD, MUC_TE})
    loi_ngoai_mau_12t = tt.loi_ngoai_mau_12t + int(sai and kq.nguon_mau == MAU_NGOAI)
    bac, che_do, mau_sach = tt.bac, tt.che_do, tt.mau_sach_toan_bo

    if tt.loai != CHUA_PHAN_LOAI:
        if sai:
            if kq.muc_sai == MUC_TE:
                che_do, mau_sach = CHE_DO_TOAN_BO, 0
            elif che_do == CHE_DO_TOAN_BO:
                pass
            elif kq.muc_sai == MUC_SAD or kq.nguon_mau == MAU_NGOAI:
                bac = cs.bac[0]
            else:
                bac = cs.bac[max(0, cs.bac.index(bac) - 1)]
        elif che_do == CHE_DO_TOAN_BO:
            mau_sach += 1
            if mau_sach >= cs.mau_sach_toan_bo:
                bac, che_do = cs.bac[0], CHE_DO_BAC
        elif chon:
            i = cs.bac.index(bac)
            if (i < len(cs.bac) - 1 and mau_tu_doi_bac >= cs.mau_toi_thieu[i]
                    and can_tren(loi_tu_doi_bac, mau_tu_doi_bac, cs.do_tin_cay) <= cs.nguong_xuong[i]):
                bac = cs.bac[i + 1]

    da_doi = (bac, che_do) != (tt.bac, tt.che_do)
    diem = can_tren(loi_12t, mau_12t, cs.do_tin_cay) if mau_12t else None
    nhan = set(tt.nhan) - {NHAN_RUI_RO_CAO, NHAN_LOI_NGOAI_MAU}
    if loi_sad_12t > 0 or (diem is not None and diem > cs.nguong_diem_rui_ro):
        nhan.add(NHAN_RUI_RO_CAO)
    if loi_ngoai_mau_12t > 0:
        nhan.add(NHAN_LOI_NGOAI_MAU)
    return replace(
        tt, bac=bac, che_do=che_do,
        mau_tu_doi_bac=0 if da_doi else mau_tu_doi_bac,
        loi_tu_doi_bac=0 if da_doi else loi_tu_doi_bac,
        mau_sach_toan_bo=mau_sach, mau_12t=mau_12t, loi_12t=loi_12t,
        loi_sad_12t=loi_sad_12t, loi_ngoai_mau_12t=loi_ngoai_mau_12t,
        diem=diem, nhan=frozenset(nhan),
        doi_bac_luc=luc if da_doi else tt.doi_bac_luc,
    ), da_doi
