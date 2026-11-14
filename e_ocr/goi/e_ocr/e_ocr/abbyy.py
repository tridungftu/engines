"""Hot Folder cục bộ: gửi một lần, lấy lại đúng mã; giữ PDF chỉ khi ChuaRo."""

import json
from pathlib import Path
import os
import re
from tempfile import TemporaryDirectory
import time
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from .cau_hinh_may import _khong_lap_khoa
from .lop_chu import MAX_BYTES


KHOANG_CHO_GIAY = 0.1


class LoiABBYYChuaNhan(LoiNghiepVu):
    """Bằng chứng nguồn chưa nhận: chưa gửi hoặc đã rút được tệp vào."""


class LoiABBYYTuChoi(LoiNghiepVu):
    """Nguồn xác nhận đúng mã: từ chối và không tiêu trang."""


def _rut_tep(tep):
    try:
        tep.unlink()
        return True
    except OSError:
        return False


def _don_tep(tep):
    try:
        tep.unlink(missing_ok=True)
        return True
    except OSError:
        return False


class BackendABBYY:
    """Trả <ma>.pdf; biên nhận từ chối rõ dùng <ma>.loi.json (xem README).

    Chỉ thao tác tệp đúng mã. Lần đọc lại không công bố hay rút tệp đang chờ.
    Callback xử lý/chốt kết quả chạy trước khi dọn PDF.
    """

    def __init__(self, cau_hinh, *, chi_doc=False):
        if not chi_doc and not cau_hinh["bat"]:
            raise LoiABBYYChuaNhan("ABBYY_DANG_TAT", "Nguồn ABBYY đang tắt. Hãy liên hệ quản trị viên.")
        try:
            vao, ra = (Path(cau_hinh[k]) for k in ("thu_muc_vao", "thu_muc_ra"))
            if not vao.is_absolute() or not ra.is_absolute():
                raise ValueError
            vao, ra = vao.resolve(strict=not chi_doc), ra.resolve(strict=True)
            if ((not chi_doc and not vao.is_dir()) or not ra.is_dir() or vao == ra
                    or vao.is_relative_to(ra) or ra.is_relative_to(vao)):
                raise ValueError
        except (OSError, ValueError, KeyError):
            raise LoiABBYYChuaNhan(
                "ABBYY_CHUA_CAU_HINH", "Chưa truy cập được thư mục nhận và trả của ABBYY. Hãy kiểm tra cấu hình."
            ) from None
        self._vao, self._ra = vao, ra
        self._thoi_han = cau_hinh["thoi_han_giay"]

    def _kiem_tu_choi(self, ma):
        tep = self._ra / f"{ma}.loi.json"
        try:
            if tep.is_symlink():
                raise ChuaRo(ma)
            with tep.open("rb") as f:
                raw = f.read(2049)
        except FileNotFoundError:
            return
        try:
            if len(raw) > 2048 or (self._ra / f"{ma}.pdf").exists():
                raise ValueError
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=_khong_lap_khoa)
            if data != {"ma_tuong_quan": ma, "trang_thai": "tu_choi", "da_tieu_trang": False} or data.get("da_tieu_trang") is not False:
                raise ValueError
        except (ValueError, UnicodeError, AttributeError, RecursionError):
            # Một tệp lỗi tùy ý/khác mã không là bằng chứng hoàn trang.
            raise ChuaRo(ma) from None
        raise LoiABBYYTuChoi("ABBYY_TU_CHOI", "ABBYY đã từ chối lượt này và xác nhận không tiêu trang.", thu_lai_duoc=True)

    def doc_pdf(self, raw, duoi, *, viec, khi_da_nhan=None, khi_chua_ro=None,
                ma_tuong_quan=None, doc_lai=False, xu_ly_ket_qua=None, khi_ket_thuc=None):
        ma = uuid4().hex if ma_tuong_quan is None else ma_tuong_quan
        if not isinstance(ma, str) or re.fullmatch(r"[a-f0-9]{32}", ma) is None or duoi not in {"pdf", "png", "jpg"}:
            raise LoiABBYYChuaNhan("MA_LUOT_KHONG_HOP_LE", "Mã lượt nhận dạng không hợp lệ.")
        vao, ra = self._vao / f"{ma}.{duoi}", self._ra / f"{ma}.pdf"
        tep_loi = self._ra / f"{ma}.loi.json"
        da_gui = da_nhan = da_doc = giu_ket_qua = False
        thu_muc_tam, ket_thuc = None, None

        def xac_nhan():
            nonlocal da_nhan
            if not da_nhan:
                da_nhan = True
                if khi_da_nhan is not None:
                    try:
                        khi_da_nhan()
                    except LoiNghiepVu:
                        raise ChuaRo(ma) from None

        def cho_doi_chieu():
            # Chỉ suy đã nhận từ tệp biến mất trong chính lần vừa công bố.
            # Sau crash, không có tệp cũng có thể là chết trước khi công bố.
            if da_gui and not da_nhan:
                try:
                    vao.stat()
                except FileNotFoundError:
                    xac_nhan()
                except OSError:
                    pass
            if khi_chua_ro is not None:
                khi_chua_ro()

        def chot(trang_thai):
            if khi_ket_thuc is not None:
                khi_ket_thuc(trang_thai)

        try:
            viec.kiem_huy()
            if not doc_lai:
                thu_muc_tam = TemporaryDirectory(prefix=".e-ocr-", dir=self._vao.parent)
                tam = Path(thu_muc_tam.name) / f"{ma}.{duoi}"
                with tam.open("xb") as f:
                    f.write(raw)
                    f.flush()
                    os.fsync(f.fileno())
                viec.kiem_huy()
                os.replace(tam, vao)
                da_gui = True
                viec.tien_do(35, "Đã gửi tài liệu; đang chờ ABBYY nhận dạng.")
            han = time.monotonic() + self._thoi_han
            lan_tien_do, dau_truoc = 0.0, None
            while True:
                viec.kiem_huy()
                if da_gui:
                    try:
                        vao.stat()
                    except FileNotFoundError:
                        xac_nhan()
                self._kiem_tu_choi(ma)
                try:
                    if ra.is_symlink():
                        raise LoiNghiepVu("KET_QUA_ABBYY_KHONG_HOP_LE", "Kết quả ABBYY không hợp lệ. Hãy liên hệ quản trị viên.")
                    stat = ra.stat()
                    if stat.st_size > MAX_BYTES:
                        raise LoiNghiepVu("VUOT_GIOI_HAN", "PDF kết quả vượt 20 MiB. Hãy chia nhỏ tài liệu.")
                    dau = stat.st_size, stat.st_mtime_ns
                    if dau == dau_truoc and stat.st_size:
                        with ra.open("rb") as f:
                            pdf = f.read(MAX_BYTES + 1)
                        sau = ra.stat()
                        if (len(pdf) == stat.st_size <= MAX_BYTES
                                and dau == (sau.st_size, sau.st_mtime_ns) and b"%%EOF" in pdf[-1024:]):
                            da_doc = True
                            xac_nhan()
                            viec.kiem_huy()
                            ket_qua = pdf if xu_ly_ket_qua is None else xu_ly_ket_qua(pdf)
                            try:
                                chot("xong")
                            except LoiNghiepVu:
                                # Chưa chốt bền: giữ PDF để khởi động lại đối chiếu.
                                raise ChuaRo(ma) from None
                            ket_thuc = "xong"
                            return ket_qua
                    dau_truoc = dau
                except FileNotFoundError:
                    dau_truoc = None
                    if doc_lai:
                        raise ChuaRo(ma) from None
                except OSError:
                    dau_truoc = None
                con_lai = han - time.monotonic()
                if con_lai <= 0:
                    if doc_lai or da_nhan or not _rut_tep(vao):
                        raise ChuaRo(ma)
                    da_gui = False
                    ket_thuc = "chua_gui"
                    raise LoiABBYYChuaNhan(
                        "ABBYY_QUA_THOI_HAN", "ABBYY chưa nhận tài liệu trong thời hạn; đã rút tệp đang chờ. Hãy thử lại sau.",
                        thu_lai_duoc=True,
                    )
                if time.monotonic() - lan_tien_do >= 1:
                    viec.tien_do(45, "Đang chờ kết quả nhận dạng từ ABBYY.")
                    lan_tien_do = time.monotonic()
                time.sleep(min(KHOANG_CHO_GIAY, con_lai))
        except OSError:
            if doc_lai or (da_gui and (da_nhan or not _rut_tep(vao))):
                giu_ket_qua = True
                try:
                    cho_doi_chieu()
                except LoiNghiepVu:
                    pass
                raise ChuaRo(ma) from None
            da_gui = False
            ket_thuc = "chua_gui"
            raise LoiABBYYChuaNhan(
                "ABBYY_KHONG_TRUY_CAP_DUOC", "Không gửi được tài liệu tới ABBYY. Hãy kiểm tra nguồn nhận dạng.",
                thu_lai_duoc=True,
            ) from None
        except ChuaRo:
            giu_ket_qua = True
            try:
                cho_doi_chieu()
            except LoiNghiepVu:
                pass  # Dấu dang_gui và chỗ giữ trước gửi vẫn bền; không được gửi lại.
            raise
        except LoiABBYYTuChoi:
            # Không để tệp còn chờ được nhận sau lúc đã hoàn hạn mức.
            if not _don_tep(vao):
                giu_ket_qua = True
                raise ChuaRo(ma) from None
            try:
                chot("tu_choi")
            except LoiNghiepVu:
                giu_ket_qua = True
                raise ChuaRo(ma) from None
            ket_thuc = "tu_choi"
            raise
        except BaseException as loi:
            ket_thuc = "huy" if isinstance(loi, ViecDaHuy) else "loi"
            raise
        finally:
            da_don, rut_duoc = True, False
            try:
                if not giu_ket_qua:
                    co_ket_qua = da_doc or ra.exists()
                    if co_ket_qua:
                        xac_nhan()
                        da_don = _don_tep(vao)
                    elif da_gui and not doc_lai:
                        rut_duoc = _rut_tep(vao)
                    if ket_thuc != "xong":
                        if ket_thuc == "tu_choi":
                            chot("tu_choi")
                        elif co_ket_qua:
                            chot(ket_thuc or "loi")
                        elif rut_duoc or (not da_gui and not doc_lai):
                            chot("chua_gui")
                        else:
                            cho_doi_chieu()
            except ChuaRo:
                giu_ket_qua = True
                raise
            finally:
                # Hủy/lỗi sau khi PDF đã về cũng phải dọn, kể cả chưa đọc bytes.
                if not giu_ket_qua:
                    da_don = _don_tep(ra) and _don_tep(tep_loi) and da_don
                if thu_muc_tam is not None:
                    try:
                        thu_muc_tam.cleanup()
                    except OSError:
                        da_don = False
                if not da_don:
                    raise LoiNghiepVu(
                        "KHONG_DON_DUOC_TEP_TAM", "Không dọn được tệp tạm của việc. Hãy liên hệ quản trị viên."
                    ) from None
