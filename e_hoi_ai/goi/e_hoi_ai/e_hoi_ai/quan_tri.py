"""Thao tác Máy AI dự kiến; chưa đăng ký vào SDK 2.2.0.

Chỉ GET metadata qua bộ bảo vệ mạng hiện có, không gửi prompt/tài liệu.
Tự tìm trong các địa chỉ đã biết, không quét toàn bộ mạng hay phân giải DNS.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import math

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .ai_cuc_bo import kiem_url, LocalAIKhongSanSang
from .chon_model import BoPhatHienModel, _luu_catalog


def _cau_hinh(tac, url=None, timeout=None):
    du_lieu = tac.dau_vao
    if not isinstance(du_lieu, dict):
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Đầu vào kiểm máy AI phải là một đối tượng.")
    cu = tac.cau_hinh.get("local_ai", {})
    url = url if url is not None else du_lieu.get("url", cu.get("url"))
    giay = timeout if timeout is not None else du_lieu.get("timeout_giay", 2)
    try:
        if isinstance(giay, bool) or not isinstance(giay, (int, float)) or not math.isfinite(giay) or not 0 < giay <= 5:
            raise ValueError
        kiem_url(url)
    except (ValueError, LocalAIKhongSanSang):
        raise LoiNghiepVu("CAU_HINH_KHONG_HOP_LE", "Địa chỉ cần là IP nội bộ, loopback hoặc Tailscale với cổng 1–65535; thời hạn kiểm trên 0 đến 5 giây.") from None
    # Giữ đúng khóa URL cấu hình (kể cả /v1) cho catalog hiện có.
    return {"url": url, "timeout_giay": giay}


def _kiem(tac, cau_hinh, *, luu=True):
    kiem_huy = getattr(tac, "kiem_huy", lambda: None)
    kiem_huy()
    # Bộ phát hiện riêng không sửa cache của các việc đang xử lý.
    catalog = BoPhatHienModel().phat_hien(cau_hinh, kiem_huy=kiem_huy, lam_moi=True)
    kiem_huy()
    if luu:
        _luu_catalog(tac.ngan, cau_hinh["url"], catalog)
    return {"url": cau_hinh["url"], "ket_noi": catalog is not None,
            "models": [{"id_model": m.ma, "kha_dung": m.kha_dung} for m in catalog.models] if catalog else [],
            "kiem_luc": datetime.now(timezone.utc).isoformat(),
            "thong_diep": "Kết nối được" if catalog is not None else "Không kết nối được. Kiểm tra IP, cổng và dịch vụ Local AI."}


def kiem_ket_noi(tac):
    return _kiem(tac, _cau_hinh(tac))


def lay_danh_sach_model(tac):
    return _kiem(tac, _cau_hinh(tac))


def tim_may_ai(tac):
    """Tối đa 16 đích, 4 luồng; mỗi đích tối đa 4 GET × 1 giây.

    Không ghi catalog khi tìm: không chuyển model cùng ID sang máy khác trước
    khi người dùng chọn máy và kiểm kết nối. Lỗi ngăn không bị coi là mất mạng.
    """
    _cau_hinh(tac, "http://127.0.0.1:11434", 1)  # kiểm kiểu đầu vào trước đọc ngăn
    nhap = tac.dau_vao.get("danh_sach_url", [])
    if not isinstance(nhap, list) or len(nhap) > 16:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Danh sách tìm máy AI phải là mảng tối đa 16 địa chỉ.")
    urls = list(nhap)
    cu = tac.cau_hinh.get("local_ai", {}).get("url")
    if cu:
        urls.append(cu)
    tiep = None
    while True:
        trang = tac.ngan.tim("model_phat_hien", loc={}, gioi_han=500, tiep=tiep)
        urls.extend(b.gia_tri.get("url") for b in trang.danh_sach if b.gia_tri.get("url"))
        tiep = trang.tiep
        if tiep is None:
            break
    urls.extend(["http://127.0.0.1:11434", "http://127.0.0.1:1234"])
    cac_cau_hinh = {_cau_hinh(tac, u, 1)["url"]: _cau_hinh(tac, u, 1) for u in urls}
    if len(cac_cau_hinh) > 16:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Có hơn 16 địa chỉ máy AI đã biết. Thu hẹp danh sách trước khi tìm.")
    with ThreadPoolExecutor(max_workers=4) as nhom:
        ket_qua = list(nhom.map(lambda ch: _kiem(tac, ch, luu=False), cac_cau_hinh.values()))
    return {"danh_sach": [k for k in ket_qua if k["ket_noi"]], "so_da_kiem": len(ket_qua)}
