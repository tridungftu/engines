"""Thay lớp vận chuyển ma-nguon/abbyy.py bằng Hot Folder cục bộ, SDK 2.0.

Không dùng cổng, SID/ACL hoặc hàm SDK riêng của Core cũ. Mỗi lượt có tên
ngẫu nhiên; chỉ thao tác đúng tệp của lượt, không quét nội dung thư mục.
"""

from pathlib import Path
import os
import re
from tempfile import TemporaryDirectory
import time
from uuid import uuid4

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from .lop_chu import MAX_BYTES


KHOANG_CHO_GIAY = 0.1


class LoiABBYYChuaNhan(LoiNghiepVu):
    """Bằng chứng nguồn chưa nhận: chưa gửi hoặc đã rút được tệp vào."""


def _rut_tep(tep):
    """True khi rút được tệp còn chờ; False khi nguồn có thể đã nhận."""
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
    """Hot Folder trả <ma_tuong_quan>.pdf, xóa/rời tệp vào khi nhận.

    PDF đầu ra phải giữ nguyên số trang, có lớp chữ đầy đủ. ABBYY được
    cấu hình theo dõi chỉ PDF/PNG/JPEG; thư mục đệm riêng nằm cạnh thư mục
    vào để đổi tên nguyên tử trên cùng filesystem, rồi dọn trong finally.
    """

    def __init__(self, cau_hinh):
        if not cau_hinh["bat"]:
            raise LoiABBYYChuaNhan("ABBYY_DANG_TAT", "Nguồn ABBYY đang tắt. Hãy liên hệ quản trị viên.")
        try:
            vao, ra = (Path(cau_hinh[k]) for k in ("thu_muc_vao", "thu_muc_ra"))
            if not vao.is_absolute() or not ra.is_absolute():
                raise ValueError
            vao, ra = vao.resolve(strict=True), ra.resolve(strict=True)
            if (not vao.is_dir() or not ra.is_dir() or vao == ra
                    or vao.is_relative_to(ra) or ra.is_relative_to(vao)):
                raise ValueError
        except (OSError, ValueError):
            raise LoiABBYYChuaNhan(
                "ABBYY_CHUA_CAU_HINH", "Chưa truy cập được thư mục nhận và trả của ABBYY. Hãy kiểm tra cấu hình."
            ) from None
        self._vao, self._ra = vao, ra
        self._thoi_han = cau_hinh["thoi_han_giay"]

    def doc_pdf(self, raw, duoi, *, viec, khi_da_nhan=None, khi_chua_ro=None, ma_tuong_quan=None):
        ma_tuong_quan = uuid4().hex if ma_tuong_quan is None else ma_tuong_quan
        if not isinstance(ma_tuong_quan, str) or re.fullmatch(r"[a-f0-9]{32}", ma_tuong_quan) is None:
            raise LoiABBYYChuaNhan("MA_LUOT_KHONG_HOP_LE", "Mã lượt nhận dạng không hợp lệ.")
        vao = self._vao / f"{ma_tuong_quan}.{duoi}"
        ra = self._ra / f"{ma_tuong_quan}.pdf"
        da_gui, da_nhan, da_doc = False, False, False
        thu_muc_tam = None

        def xac_nhan():
            nonlocal da_nhan
            if not da_nhan:
                da_nhan = True
                if khi_da_nhan is not None:
                    khi_da_nhan()

        def cho_doi_chieu():
            # Không rút được do lỗi quyền chưa chứng minh là nguồn đã nhận.
            # Giữ chỗ nhưng chỉ ghi trang đã dùng khi thấy tệp thực sự biến mất.
            if not da_nhan:
                try:
                    vao.stat()
                except FileNotFoundError:
                    xac_nhan()
                except OSError:
                    pass
            if not da_nhan and khi_chua_ro is not None:
                khi_chua_ro()

        try:
            viec.kiem_huy()
            # Không chép dở vào nơi ABBYY đang Watching. Chỉ công bố sau fsync.
            thu_muc_tam = TemporaryDirectory(prefix=".e-ocr-", dir=self._vao.parent)
            tam = Path(thu_muc_tam.name) / f"{ma_tuong_quan}.{duoi}"
            with tam.open("xb") as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
            viec.kiem_huy()
            os.replace(tam, vao)
            da_gui = True
            han = time.monotonic() + self._thoi_han
            lan_tien_do = 0.0
            dau_truoc = None
            viec.tien_do(35, "Đã gửi tài liệu; đang chờ ABBYY nhận dạng.")
            while True:
                viec.kiem_huy()
                try:
                    vao.stat()
                except FileNotFoundError:
                    xac_nhan()
                # Chỉ đọc đúng mã tương quan. Hai lượt ổn định + EOF + stat sau đọc
                # tránh PDF đang ghi dở; lỗi sharing Windows được chờ tới hạn.
                try:
                    if ra.is_symlink():
                        raise LoiNghiepVu("KET_QUA_ABBYY_KHONG_HOP_LE", "Kết quả ABBYY không hợp lệ. Hãy liên hệ quản trị viên.")
                    stat = ra.stat()
                    if stat.st_size > MAX_BYTES:
                        raise LoiNghiepVu("VUOT_GIOI_HAN", "PDF kết quả vượt 20 MiB. Hãy chia nhỏ tài liệu.")
                    dau = stat.st_size, stat.st_mtime_ns
                    if dau == dau_truoc and stat.st_size:
                        with ra.open("rb") as f:
                            ket_qua = f.read(MAX_BYTES + 1)
                        sau = ra.stat()
                        if (len(ket_qua) == stat.st_size <= MAX_BYTES
                                and dau == (sau.st_size, sau.st_mtime_ns)
                                and b"%%EOF" in ket_qua[-1024:]):
                            viec.kiem_huy()
                            # Có kết quả đúng mã cũng là bằng chứng nguồn đã nhận.
                            xac_nhan()
                            da_doc = True
                            return ket_qua
                    dau_truoc = dau
                except OSError:
                    dau_truoc = None
                con_lai = han - time.monotonic()
                if con_lai <= 0:
                    if da_nhan or not _rut_tep(vao):
                        cho_doi_chieu()
                        raise ChuaRo(ma_tuong_quan)
                    da_gui = False
                    raise LoiABBYYChuaNhan(
                        "ABBYY_QUA_THOI_HAN", "ABBYY chưa nhận tài liệu trong thời hạn; đã rút tệp đang chờ. Hãy thử lại sau.",
                        thu_lai_duoc=True,
                    )
                if time.monotonic() - lan_tien_do >= 1:
                    viec.tien_do(45, "Đang chờ kết quả nhận dạng từ ABBYY.")
                    lan_tien_do = time.monotonic()
                time.sleep(min(KHOANG_CHO_GIAY, con_lai))
        except OSError:
            if da_gui and (da_nhan or not _rut_tep(vao)):
                cho_doi_chieu()
                raise ChuaRo(ma_tuong_quan) from None
            da_gui = False
            raise LoiABBYYChuaNhan(
                "ABBYY_KHONG_TRUY_CAP_DUOC", "Không gửi được tài liệu tới ABBYY. Hãy kiểm tra nguồn nhận dạng.",
                thu_lai_duoc=True,
            ) from None
        finally:
            da_don = True
            if da_gui:
                if da_doc:
                    da_don = _don_tep(vao)
                else:
                    # Hủy/lỗi có thể xảy ra ngay sau khi nguồn nhận, trước poll.
                    if not _rut_tep(vao):
                        cho_doi_chieu()
            if da_doc:
                da_don = _don_tep(ra) and da_don
            if thu_muc_tam is not None:
                try:
                    thu_muc_tam.cleanup()
                except OSError:
                    da_don = False
            if not da_don:
                raise LoiNghiepVu(
                    "KHONG_DON_DUOC_TEP_TAM", "Không dọn được tệp tạm của việc. Hãy liên hệ quản trị viên."
                ) from None
