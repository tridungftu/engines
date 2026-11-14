"""Kho JSON tạm cho mã, băm, số đếm; không nhận nội dung tài liệu.

Mỗi ghi khóa cả chu kỳ đọc–sửa–thay tệp. cap_nhat cho phép cập nhật một
khóa trong cùng khóa tệp; không cung cấp giao dịch nhiều lời gọi.
"""

from __future__ import annotations

from contextlib import contextmanager
import errno
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .cau_hinh_may import THU_MUC_GOI, _khong_lap_khoa, _thu_muc_may, _tu_choi_hang_so

if os.name == "nt":
    import msvcrt
else:
    import fcntl


_MA = re.compile(r"[A-Za-z0-9_.:@+-]{1,200}\Z")
_TRUONG_NOI_DUNG = {
    "van_ban", "noi_dung", "noi_dung_tep", "du_lieu", "du_lieu_tep",
    "tai_lieu", "tep", "prompt", "tra_loi",
}
_GIA_TRI_TOI_DA_BYTE = 64 * 1024
_KHO_TOI_DA_BYTE = 8 * 1024 * 1024


def _kiem_ma(ma):
    if not isinstance(ma, str) or _MA.fullmatch(ma) is None:
        raise ValueError("Mã không hợp lệ.")


def _kiem_du_lieu(gia_tri, do_sau=0):
    if do_sau > 16:
        raise ValueError("Dữ liệu lồng quá sâu.")
    if gia_tri is None or type(gia_tri) is bool:
        return
    if type(gia_tri) is int and gia_tri >= 0:
        return
    if type(gia_tri) is str:
        _kiem_ma(gia_tri)
        return
    if type(gia_tri) is list:
        for muc in gia_tri:
            _kiem_du_lieu(muc, do_sau + 1)
        return
    if type(gia_tri) is dict:
        for ma, muc in gia_tri.items():
            _kiem_ma(ma)
            if ma.lower() in _TRUONG_NOI_DUNG:
                raise ValueError("Không được lưu nội dung tài liệu.")
            _kiem_du_lieu(muc, do_sau + 1)
        return
    raise ValueError("Kho chỉ nhận mã, băm, số đếm và cờ trạng thái.")


def _thanh_json(gia_tri):
    return json.dumps(
        gia_tri, ensure_ascii=True, allow_nan=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


class KhoTam:
    """Đọc/ghi theo khóa; tệp dữ liệu và tệp khóa luôn ở ngoài gói.

    Chuỗi chỉ được là mã máy tối đa 200 ký tự, không khoảng trắng hay đường
    dẫn; không truyền bytes, văn bản tự do hoặc nội dung mã hóa vào kho.
    """

    def __init__(self, thu_muc=None, *, thoi_han_khoa_giay=10.0):
        try:
            if thu_muc is None:
                thu_muc = os.environ.get("KTT_ENGINE_DU_LIEU")
                if thu_muc is not None and not thu_muc.strip():
                    raise ValueError("Chưa chọn thư mục dữ liệu.")
                if thu_muc is None:
                    thu_muc = _thu_muc_may() / "du-lieu"
            self.thu_muc = Path(thu_muc).resolve()
            if self.thu_muc.is_relative_to(THU_MUC_GOI):
                raise ValueError("Dữ liệu phải ở ngoài gói.")
            if (
                type(thoi_han_khoa_giay) not in (int, float)
                or not math.isfinite(thoi_han_khoa_giay)
                or thoi_han_khoa_giay <= 0
            ):
                raise ValueError("Thời hạn khóa không hợp lệ.")
            self.thoi_han_khoa_giay = thoi_han_khoa_giay
        except (OSError, ValueError, TypeError):
            raise LoiNghiepVu(
                "KHO_TAM_CHUA_CAU_HINH", "Chưa cấu hình đúng nơi lưu dữ liệu tạm của OCR."
            ) from None

    @contextmanager
    def _khoa_tep(self):
        try:
            self.thu_muc.mkdir(parents=True, exist_ok=True)
            tep_khoa = self.thu_muc / "kho.khoa"
            tep_du_lieu = self.thu_muc / "kho.json"
            if tep_khoa.is_symlink() or tep_du_lieu.is_symlink():
                raise OSError("Không dùng liên kết tượng trưng trong kho.")
            # Tệp khóa cố định, tuyệt đối không đổi tên cùng tệp dữ liệu.
            with tep_khoa.open("a+b") as luong:
                if os.fstat(luong.fileno()).st_size == 0:
                    luong.write(b"\0")
                    luong.flush()
                han = time.monotonic() + self.thoi_han_khoa_giay
                while True:
                    try:
                        luong.seek(0)
                        if os.name == "nt":
                            msvcrt.locking(luong.fileno(), msvcrt.LK_NBLCK, 1)
                        else:
                            fcntl.flock(luong.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except OSError as loi:
                        if loi.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                            raise
                        if time.monotonic() >= han:
                            raise LoiNghiepVu(
                                "KHO_TAM_DANG_BAN", "Dữ liệu tạm đang được sử dụng. Hãy thử lại.",
                                thu_lai_duoc=True,
                            ) from None
                        time.sleep(0.01)
                try:
                    yield
                finally:
                    luong.seek(0)
                    if os.name == "nt":
                        msvcrt.locking(luong.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(luong.fileno(), fcntl.LOCK_UN)
        except OSError:
            raise LoiNghiepVu(
                "KHO_TAM_KHONG_TRUY_CAP", "Không truy cập được dữ liệu tạm của OCR. Hãy kiểm tra quyền lưu trữ."
            ) from None

    def _doc_toan_bo(self):
        try:
            try:
                with (self.thu_muc / "kho.json").open("rb") as luong:
                    noi_dung = luong.read(_KHO_TOI_DA_BYTE + 1)
            except FileNotFoundError:
                return {}
            if len(noi_dung) > _KHO_TOI_DA_BYTE:
                raise ValueError("Kho quá lớn.")
            du_lieu = json.loads(
                noi_dung.decode("utf-8"), object_pairs_hook=_khong_lap_khoa,
                parse_constant=_tu_choi_hang_so,
            )
            if type(du_lieu) is not dict:
                raise ValueError("Kho không đúng cấu trúc.")
            _kiem_du_lieu(du_lieu)
            return du_lieu
        except (ValueError, UnicodeError, RecursionError):
            raise LoiNghiepVu(
                "KHO_TAM_HONG", "Dữ liệu tạm của OCR không hợp lệ. Hãy liên hệ quản trị viên để kiểm tra."
            ) from None

    def doc(self, khoa, mac_dinh=None):
        try:
            _kiem_ma(khoa)
        except ValueError:
            raise LoiNghiepVu("KHO_TAM_KHOA_SAI", "Mã tra cứu dữ liệu tạm không hợp lệ.") from None
        with self._khoa_tep():
            return self._doc_toan_bo().get(khoa, mac_dinh)

    def ghi(self, khoa, gia_tri):
        # Kiểm trước khi mở kho để giữ hành vi từ chối dữ liệu không hợp lệ.
        self._kiem_gia_tri(khoa, gia_tri)
        self.cap_nhat(khoa, lambda cu: gia_tri)

    @staticmethod
    def _kiem_gia_tri(khoa, gia_tri):
        try:
            _kiem_ma(khoa)
            _kiem_du_lieu(gia_tri)
            if len(_thanh_json(gia_tri)) > _GIA_TRI_TOI_DA_BYTE:
                raise ValueError("Giá trị quá lớn.")
        except (ValueError, TypeError, RecursionError):
            raise LoiNghiepVu(
                "KHO_TAM_DU_LIEU_SAI", "Kho tạm chỉ nhận mã, băm và số đếm; không nhận nội dung tài liệu."
            ) from None

    def cap_nhat(self, khoa, sua):
        """Đọc–sửa–ghi một khóa nguyên tử; callback chỉ xử lý metadata.

        Callback không được gọi lại kho hay thực hiện I/O. Ngoại lệ của
        callback giữ nguyên bản cũ và nhả khóa. Trả giá trị đã ghi.
        """
        try:
            _kiem_ma(khoa)
        except ValueError:
            raise LoiNghiepVu("KHO_TAM_KHOA_SAI", "Mã tra cứu dữ liệu tạm không hợp lệ.") from None
        with self._khoa_tep():
            du_lieu = self._doc_toan_bo()
            gia_tri = sua(du_lieu.get(khoa))
            self._kiem_gia_tri(khoa, gia_tri)
            du_lieu[khoa] = gia_tri
            noi_dung = _thanh_json(du_lieu)
            if len(noi_dung) > _KHO_TOI_DA_BYTE:
                raise LoiNghiepVu("KHO_TAM_QUA_LON", "Kho dữ liệu tạm đã vượt giới hạn lưu trữ.")
            tep_tam = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb", dir=self.thu_muc, prefix=".kho-", suffix=".tmp", delete=False
                ) as luong:
                    tep_tam = Path(luong.name)
                    luong.write(noi_dung)
                    luong.flush()
                    os.fsync(luong.fileno())
                os.replace(tep_tam, self.thu_muc / "kho.json")
                if os.name != "nt":
                    thu_muc_fd = os.open(self.thu_muc, os.O_RDONLY | os.O_DIRECTORY)
                    try:
                        os.fsync(thu_muc_fd)
                    finally:
                        os.close(thu_muc_fd)
            finally:
                # Chỉ dọn tệp tạm do chính lượt ghi này vừa tạo.
                if tep_tam is not None:
                    tep_tam.unlink(missing_ok=True)
            return gia_tri
