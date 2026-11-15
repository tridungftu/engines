"""Xử lý của module DEMO theo hợp đồng cổng phần (a), mục a.9–a.10 (bản 1.5).

- Hai hành động khai trong module.json (`hanh_dong.ma`) chỉ ĐỌC ngăn `ho_so` của chính module:
  `sdk.ngan(ma).doc(loc, gioi_han, con_tro)` trả `{danh_sach, con_tro_tiep}`, `loc` là `{cột: giá trị}` so bằng,
  SDK tự lọc theo pháp nhân của phiên. Hàm nhận `yeu_cau` gồm `duong_dan`, `truy_van`, `than`, `ngu_canh`.
- Sự kiện `quy_trinh.xong` (a.10 điểm 5): thêm một dòng vào ngăn `ho_so` bằng `sdk.ngan(ma).them(dong)` theo
  bảng `ghep` Core gửi kèm; tệp người dùng tải ở nút (`tep_nut`) ghi vào cột `tep_goc`, tên tệp vào `ten_ho_so`
  (Admin ghép tường minh cột nào thì giá trị ghép thắng). Chống xử lý trùng theo `id` sự kiện do bus của Core lo.
Lỗi nghiệp vụ trả bằng mã đã khai ở `ma_loi`; câu cho người dùng do Core tra trong phiếu. Chỉ thư viện chuẩn.
"""

from __future__ import annotations

import re

NGAN = "ho_so"
TOI_DA_DONG = 200
CO_TRANG = 200        # số dòng mỗi lần đọc
TOI_DA_TRANG = 50     # chặn vòng đọc vô hạn nếu con trỏ lỗi
COT_NGAN = ("ten_ho_so", "noi_dung", "so_tu", "so_dong", "tep_goc")
_RE_ID = re.compile(r"[A-Za-z0-9-]{1,64}")
_COT_DANH_SACH = ("id", "ten_ho_so", "so_tu", "so_dong", "tep_goc", "tao_luc")
_COT_CHI_TIET = ("id", "ten_ho_so", "noi_dung", "so_tu", "so_dong", "tep_goc", "tao_luc", "sua_luc")


class LoiNghiepVu(Exception):
    """Lỗi có mã khai trong `ma_loi` của module.json; không mang dữ liệu nghiệp vụ."""

    def __init__(self, ma: str):
        super().__init__(ma)
        self.ma = ma


def _chuoi(value):
    return None if value is None else str(value)


def _dong(row: dict, cot) -> dict:
    out = {k: row.get(k) for k in cot}
    for k in ("id", "tep_goc", "tao_luc", "sua_luc"):
        if k in out:
            out[k] = _chuoi(out[k])
    return out


def _doc_het(ngan, loc):
    dong, con_tro = [], None
    for _ in range(TOI_DA_TRANG):
        trang = ngan.doc(loc, gioi_han=CO_TRANG, con_tro=con_tro)
        dong.extend(trang.get("danh_sach") or [])
        con_tro = trang.get("con_tro_tiep")
        if not con_tro:
            break
    return dong


def danh_sach_ho_so(sdk, yeu_cau=None) -> dict:
    """GET /ho-so: hồ sơ chưa lưu trữ, mới nhất trước, tối đa 200 dòng, không kèm nội dung đầy đủ."""
    dong = [r for r in _doc_het(sdk.ngan(NGAN), {"da_luu_tru": False}) if not r.get("da_luu_tru")]
    dong.sort(key=lambda r: str(r.get("tao_luc") or ""), reverse=True)
    return {"danh_sach": [_dong(r, _COT_DANH_SACH) for r in dong[:TOI_DA_DONG]]}


def xem_ho_so(sdk, yeu_cau) -> dict:
    """GET /ho-so/{id}: một hồ sơ của pháp nhân đang làm việc."""
    ma = ((yeu_cau or {}).get("duong_dan") or {}).get("id")
    if not isinstance(ma, str) or not _RE_ID.fullmatch(ma):
        raise LoiNghiepVu("HO_SO_MA_KHONG_HOP_LE")
    trang = sdk.ngan(NGAN).doc({"id": ma}, gioi_han=1, con_tro=None)
    dong = [r for r in trang.get("danh_sach") or [] if str(r.get("id")) == ma and not r.get("da_luu_tru")]
    if not dong:
        raise LoiNghiepVu("HO_SO_KHONG_TIM_THAY")
    return _dong(dong[0], _COT_CHI_TIET)


def nhan_quy_trinh_xong(sdk, su_kien) -> dict:
    """quy_trinh.xong: một hồ sơ mới từ tệp người dùng tải ở nút và các trường quy trình trả về (đã ghép)."""
    tep = su_kien.get("tep_nut") or {}
    dong = {"ten_ho_so": tep.get("ten"), "tep_goc": _chuoi(tep.get("tep_id"))}
    for muc in su_kien.get("ghep") or []:
        if muc.get("ngan") == NGAN and muc.get("cot") in COT_NGAN:
            dong[muc["cot"]] = muc.get("gia_tri")
    return sdk.ngan(NGAN).them({k: v for k, v in dong.items() if v is not None})


def thu_ghi_cheo_core(sdk, yeu_cau):
    """Thử ghi phiếu của module khác qua Core; Core phải trả lỗi từ chối quyền."""
    return sdk.ngan_core.them('demo_bo_truong.phieu', {
        'ma_phieu': 'DEMO-GHI-CHEO', 'so_tien': 1000, 'ngay_lap': '2026-11-13'})


# Bảng xử lý theo `hanh_dong.ma`; khóa phải trùng đúng danh sách hành động trong module.json.
XU_LY = {"danh_sach_ho_so": danh_sach_ho_so, "xem_ho_so": xem_ho_so,
         "thu_ghi_cheo_core": thu_ghi_cheo_core}
# Sự kiện Core gửi cho module sở hữu nút (a.10 điểm 5); module không cần khai nhận trong phiếu.
SU_KIEN = {"quy_trinh.xong": nhan_quy_trinh_xong}
