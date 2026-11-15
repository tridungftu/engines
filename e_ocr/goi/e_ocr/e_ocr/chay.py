"""Cổng SDK 2.0: ba action đọc/xuất Word dùng chung lõi nhận dạng."""

from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Event, Thread

from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

from .abbyy import BackendABBYY, LoiABBYYChuaNhan
from .ban_giao import ban_giao_word
from .cau_hinh import CauHinhKhongHopLe, doc_cau_hinh
from .ngan import NganBoNho, NganKhongHopLe, NganXungDot, chon_ngan
from .nhat_ky import do_luot, ghi_nguon
from .van_ban import SCHEMA, trich_van_ban


app = Engine.tu_khai_bao("engine.json")
KHAI_NGAN = json.loads((Path(__file__).resolve().parents[1] / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))["ngan_du_lieu"]


def _ngan_ung_dung(ung_dung):
    if getattr(ung_dung, "ngan", None) is None:
        ung_dung.ngan = NganBoNho(KHAI_NGAN)
    return chon_ngan(ung_dung)


_ngan_ung_dung(app)


def _doc(viec):
    ngan = getattr(viec, "ngan", None)
    if ngan is None:
        ngan = _ngan_ung_dung(app)
    try:
        du_lieu = trich_van_ban(viec, phien_ban_engine=f"{app.ma} {app.phieu['phien_ban']}", ngan=ngan)
    except (NganXungDot, NganKhongHopLe, CauHinhKhongHopLe) as exc:
        raise LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc) from None
    ghi_nguon(du_lieu.get("nguon_doc"))
    return du_lieu


@app.nang_luc("ocr.doc_tai_lieu@1")
@do_luot
def doc_tai_lieu(viec):
    du_lieu = _doc(viec)
    return {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": du_lieu}


@app.nang_luc("ocr.doc_van_ban@1")
@do_luot
def doc_van_ban(viec):
    du_lieu = _doc(viec)
    return {"loai": "van_ban", "van_ban": du_lieu["van_ban"]}


@app.nang_luc("ocr.xuat_word@1")
@do_luot
def xuat_word(viec):
    du_lieu = _doc(viec)
    return ban_giao_word(viec, du_lieu)


def ghi_trang_thai(ngan):
    """Chỉ kiểm đường vào/ra đã cấu hình; không đọc hồ sơ hay gửi việc thử."""
    bat, ly_do = False, "chua_cau_hinh"
    try:
        cau_hinh = doc_cau_hinh(ngan, SCHEMA)
        if cau_hinh is not None:
            if cau_hinh["abbyy"]["bat"]:
                BackendABBYY(cau_hinh["abbyy"])
                bat, ly_do = True, "bat"
            else:
                ly_do = "dang_tat"
    except LoiABBYYChuaNhan:
        ly_do = "khong_ket_noi"
    except (ValueError, TypeError, OverflowError, RecursionError):
        ly_do = "cau_hinh_loi"
    gia_tri = {"abbyy_bat": bat, "ly_do": ly_do,
               "luc_kiem": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    for _ in range(12):
        cu = ngan.doc("trang_thai_engine", {"ma": "abbyy"})
        try:
            with ngan.lo() as lo:
                if cu is None:
                    lo.them("trang_thai_engine", {"ma": "abbyy"}, gia_tri)
                else:
                    lo.sua("trang_thai_engine", {"ma": "abbyy"}, gia_tri, row_version=cu.row_version)
            return
        except NganXungDot:
            continue
    raise LoiNghiepVu("NGAN_XUNG_DOT", "Trạng thái OCR vừa thay đổi. Hãy thử lại.", thu_lai_duoc=True)


def chay_engine(*, ung_dung=None, khoang_giay=30):
    ung_dung = app if ung_dung is None else ung_dung
    dung = Event()

    def cap_nhat():
        while not dung.is_set():
            try:
                ghi_trang_thai(_ngan_ung_dung(ung_dung))
            except Exception:
                # Giữ bản ghi cũ; màn hiển thị hết hạn, không bịa trạng thái mới.
                pass
            dung.wait(khoang_giay)

    luong = Thread(target=cap_nhat, name="trang-thai-ocr", daemon=True)
    luong.start()
    try:
        ung_dung.chay()
    finally:
        dung.set()
        luong.join()


if __name__ == "__main__":
    chay_engine()
