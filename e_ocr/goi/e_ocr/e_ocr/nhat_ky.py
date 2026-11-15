"""Nhật ký kỹ thuật stderr: chỉ số đo và mã cố định, không nội dung tệp.

Thời gian chờ là thời gian đợi nguồn ABBYY trong action; SDK 2.0 chưa
cấp mốc vào hàng chờ Core. ContextVar cách ly các việc chạy đồng thời.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
import sys
import time

from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy


_LUOT = ContextVar("nhat_ky_ocr", default=None)


def ghi_nguon(nguon):
    luot = _LUOT.get()
    if luot is not None and nguon in ("abbyy", "tesseract", "lop_chu_san"):
        luot["nguon_doc"] = nguon


def het_cho():
    luot = _LUOT.get()
    if luot is not None and luot["bat_dau_cho"] is not None:
        luot["cho"] += time.monotonic() - luot["bat_dau_cho"]
        luot["bat_dau_cho"] = None


@contextmanager
def cho_nguon():
    luot = _LUOT.get()
    if luot is not None:
        luot["bat_dau_cho"] = time.monotonic()
    try:
        yield
    finally:
        het_cho()


def do_luot(ham):
    @wraps(ham)
    def chay(viec):
        luc = time.monotonic()
        luot = {"nguon_doc": "chua_xac_dinh", "cho": 0.0, "bat_dau_cho": None}
        dau = _LUOT.set(luot)
        trang_thai = "LOI"
        try:
            ket_qua = ham(viec)
            trang_thai = "XONG"
            return ket_qua
        except ChuaRo:
            trang_thai = "CHUA_RO"
            raise
        except ViecDaHuy:
            trang_thai = "HUY"
            raise
        except (LoiNghiepVu, LoiDuongTruyen):
            raise
        except Exception:
            # SDK 2.0 in traceback cho ngoại lệ chưa xử lý. Đổi lỗi bất ngờ
            # ngay tại cổng để traceback/nội dung nguồn không lọt stderr.
            raise LoiNghiepVu("ENGINE_LOI_XU_LY", "Engine gặp lỗi khi xử lý việc này.") from None
        finally:
            het_cho()
            tong = time.monotonic() - luc
            ban_ghi = {
                "su_kien": "ocr.ket_thuc", "nang_luc": "ocr." + ham.__name__ + "@1",
                "trang_thai": trang_thai, "nguon_doc": luot["nguon_doc"],
                "cho_nguon_giay": round(luot["cho"], 6),
                "chay_giay": round(max(0, tong - luot["cho"]), 6),
                "tong_giay": round(tong, 6),
            }
            _LUOT.reset(dau)
            try:
                print(json.dumps(ban_ghi, ensure_ascii=False), file=sys.stderr)
            except OSError:
                pass  # Lỗi đích nhật ký không đổi trạng thái nghiệp vụ.
    return chay
