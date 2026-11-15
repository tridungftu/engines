"""Mở che tra ngược lịch sử chỉ dùng hồi quy ngoài gói, không P4."""
from __future__ import annotations
import re
from e_mask.che_van_ban import (LoiCheVanBan, _kiem_van_ban, _VUNG_BI_DANH,
    _BI_DANH, chuan_bi_danh, _vi_tri, _manh_bi_danh_con_lai, _kiem_tien_ngay)

def mo_che(van_ban_co_bi_danh: str, ma_yeu_cau: str, kho: Kho,
           *, dong_viec: bool = False) -> dict:
    """Mẫu 3–4: tra toàn bảng sau kiểm quyền; không đoán bí danh hỏng.

    Vị trí trong đầu vào: offset ký tự [bat_dau, ket_thuc), dòng/cột từ 1.
    Chỉ đóng việc theo yêu cầu rõ ràng và khi không còn bí danh chưa mở.
    """
    _kiem_van_ban(van_ban_co_bi_danh, cho_rong=True)
    if not isinstance(ma_yeu_cau, str) or not ma_yeu_cau or type(dong_viec) is not bool:
        raise LoiCheVanBan('Yêu cầu mở che chưa hợp lệ.')
    try:
        with kho.giao_dich():
            yeu_cau = kho.doc_yeu_cau(ma_yeu_cau)
            if yeu_cau['trang_thai'] != 'DANG_XU_LY':
                raise ValueError('Yêu cầu đã đóng.')
            return _mo_che(van_ban_co_bi_danh, ma_yeu_cau, kho, dong_viec)
    except Exception:
        raise LoiCheVanBan('Không thể mở che. Yêu cầu không hợp lệ hoặc không thuộc phiên hiện tại.') from None


def _mo_che(van_ban, ma, kho, dong_viec):
    chua_mo, da_dung = [], []
    so_cho, cuoi = 0, 0
    phan, da_xet = [], []
    xuong_dong = [i for i, ky_tu in enumerate(van_ban) if ky_tu == '\n']
    for m in _VUNG_BI_DANH.finditer(van_ban) if '[' in van_ban or ']' in van_ban else ():
        da_xet.append(m.span())
        bi_danh = chuan_bi_danh(m.group())
        goc = kho.tra_dinh_danh(bi_danh) if _BI_DANH.fullmatch(bi_danh) else None
        phan.append(van_ban[cuoi:m.start()])
        if goc is None:
            phan.append(m.group())
            chua_mo.append({'bi_danh': m.group(), 'vi_tri': _vi_tri(m.start(), m.end(), xuong_dong)})
        else:
            phan.append(goc)
            da_dung.append(bi_danh)
            so_cho += 1
        cuoi = m.end()
    phan.append(van_ban[cuoi:])
    cac_ma = [b for muc in kho.liet_ke_dinh_danh()
              for b in (muc['bi_danh'], muc.get('bi_danh_tam')) if b]
    for a, b in _manh_bi_danh_con_lai(van_ban, cac_ma, da_xet):
        chua_mo.append({'bi_danh': van_ban[a:b], 'vi_tri': _vi_tri(a, b, xuong_dong)})
    chua_mo.sort(key=lambda m: m['vi_tri']['bat_dau'])
    da_mo = ''.join(phan)
    kiem_tien_ngay = _kiem_tien_ngay(van_ban, da_mo)
    kho.ghi_bi_danh_da_dung(ma, da_dung)
    if dong_viec and not chua_mo and kiem_tien_ngay:
        kho.dong_yeu_cau(ma)
    return {'van_ban_da_mo_che': da_mo if kiem_tien_ngay else None, 'so_cho_mo': so_cho,
            'bi_danh_khong_ro': chua_mo, 'mo_day_du': not chua_mo and kiem_tien_ngay,
            'kiem_tien_ngay': kiem_tien_ngay,
            'trang_thai_ma_yeu_cau': 'DA_DONG' if dong_viec and not chua_mo and kiem_tien_ngay else 'DANG_XU_LY'}
