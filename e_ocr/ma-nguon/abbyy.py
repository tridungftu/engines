"""OCR-4b: ghép phiên ABBYY có màn hình vào cổng OCR dùng chung.

CD-038 3A cho phép phiên Windows riêng, không cho phép dùng SID Core/module.
Core khởi chạy/cấp Job và bootstrap G2-21; adapter không tạo tài khoản,
launcher, HotFolderClient hay sổ hạn mức khác. Dùng lại CongOCR.ocr, đang
được OCR-2/3/5a dùng, không mở đường convert riêng vượt cổng/sổ chung.

Cấu hình và các seam chỉ do hồ sơ tin cậy của Core tiêm sau bootstrap,
không nhận từ payload module. kiem_phien đọc token của chính engine và
tiến trình ABBYY đang Watching, không chỉ tên tài khoản. kiem_acl phải
kiểm từ engine: quyền tối thiểu thư mục in/out/đệm/sổ do Core cấp; cấm đọc
két/DPAPI, mở bộ nhớ/token/handle Core, debug/impersonate và thoát Job.
Chỉ trả True khi đủ bằng chứng, thiếu/chưa kiểm phải trả False.

Nếu launcher cần bí mật, seam của Core nhận trong RAM từ stdin/handle;
adapter không cần mật khẩu và không tự đọc config/khóa nguồn/env/args.
Cách ly/khởi chạy Windows thật: CHUA_KIEM cho tới khi G2-33b được kiểm.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .lib.cong_ocr import CongOCR, _docx_hop_le
from .ket_noi_abbyy import LoiKetNoiABBYY
from ...sdk_core.ngu_canh import _xoa_loi


class BackendKetNoiABBYY:
    """KN4: vận chuyển PDF qua client KN3 do bootstrap tin cậy tiêm.

    Không tự tạo client, đọc endpoint/khóa/cấu hình hay tính hạn mức.
    san_sang chỉ phản ánh cấu hình client, chưa xác nhận ABBYY thật.
    """

    def __init__(self, *, ket_noi=None):
        if ket_noi is not None and (
                not callable(getattr(ket_noi, 'san_sang', None))
                or not callable(getattr(ket_noi, 'doc_pdf', None))):
            raise TypeError('Cần kết nối nhận dạng do Core cấp.')
        self._ket_noi = ket_noi

    def __repr__(self):
        return 'BackendKetNoiABBYY(<an>)'

    def san_sang(self):
        return self._ket_noi is not None and self._ket_noi.san_sang() is True

    def doc_pdf(self, raw, duoi='pdf', *, huy=None, ma_yeu_cau=None):
        if not self.san_sang():
            raise LoiKetNoiABBYY('ABBYY_KHONG_KET_NOI', ma_yeu_cau=ma_yeu_cau)
        return self._ket_noi.doc_pdf(raw, duoi, huy=huy, ma_yeu_cau=ma_yeu_cau)


class LoiABBYY(RuntimeError):
    def __init__(self, ma):
        self.ma = ma
        super().__init__(ma)


@dataclass(frozen=True, slots=True, repr=False)
class CauHinhABBYY:
    """SID/phiên mong đợi do Core cấp, không chứa credential Windows."""

    sid_ocr: str
    sid_core: str
    sid_module: str
    sid_engine_khac: tuple[str, ...]
    phien_ocr: int
    phien_core: int

    def __repr__(self):
        return 'CauHinhABBYY(<an>)'


@dataclass(frozen=True, slots=True, repr=False)
class DanhTinhWindows:
    sid: str
    phien_id: int
    han_che: bool
    co_man_hinh: bool

    def __repr__(self):
        return 'DanhTinhWindows(<an>)'


class BackendABBYY:
    """Seam ocr(raw, duoi, huy=...) cho adapter văn bản/bảng hiện có.

    kiem_phien() -> (danh tính engine, danh tính ABBYY); phải lấy mới mỗi
    lần. kiem_acl(cong_ocr, engine, abbyy) -> bool; exception cũng từ chối.
    Không cache readiness: logout/đổi SID/ACL sau ready phải chặn việc mới.
    Không thử lại/hoàn hạn mức khi lỗi sau gửi; OCR-5a/Core đối chiếu.
    """

    def __init__(self, *, cau_hinh, cong_ocr, kiem_phien, kiem_acl):
        if not isinstance(cau_hinh, CauHinhABBYY):
            raise LoiABBYY('ABBYY_CAU_HINH_SAI')
        sids = (cau_hinh.sid_ocr, cau_hinh.sid_core, cau_hinh.sid_module)
        if (type(cau_hinh.sid_engine_khac) is not tuple
                or any(not isinstance(s, str)
                       or re.fullmatch(r'S-1-5-21-(?:\d+-){3}\d+', s) is None
                       for s in (*sids, *cau_hinh.sid_engine_khac))
                or len(set((*sids, *cau_hinh.sid_engine_khac)))
                    != len(sids) + len(cau_hinh.sid_engine_khac)
                or type(cau_hinh.phien_ocr) is not int or cau_hinh.phien_ocr <= 0
                or type(cau_hinh.phien_core) is not int or cau_hinh.phien_core < 0
                or cau_hinh.phien_ocr == cau_hinh.phien_core):
            raise LoiABBYY('ABBYY_CAU_HINH_SAI')
        if (not isinstance(cong_ocr, CongOCR)
                or not callable(kiem_phien) or not callable(kiem_acl)):
            raise LoiABBYY('ABBYY_THIEU_SEAM')
        self._cfg, self._cong = cau_hinh, cong_ocr
        self._kiem_phien, self._kiem_acl = kiem_phien, kiem_acl

    def __repr__(self):
        return 'BackendABBYY(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize phiên ABBYY')

    def _kiem_quyen(self):
        ma = 'ABBYY_PHIEN_KHONG_HOP_LE'
        try:
            engine, abbyy = self._kiem_phien()
            for danh_tinh in (engine, abbyy):
                if (not isinstance(danh_tinh, DanhTinhWindows)
                        or danh_tinh.sid != self._cfg.sid_ocr
                        or type(danh_tinh.phien_id) is not int
                        or danh_tinh.phien_id != self._cfg.phien_ocr
                        or danh_tinh.han_che is not True
                        or danh_tinh.co_man_hinh is not True):
                    raise LoiABBYY(ma)
            ma = 'ABBYY_ACL_CHUA_DAT'
            if self._kiem_acl(self._cong, engine, abbyy) is not True:
                raise LoiABBYY(ma)
            return
        except Exception as exc:
            _xoa_loi(exc)
        # Ngoài except: không giữ exception nguồn chứa bí mật trong context.
        raise LoiABBYY(ma) from None

    def san_sang(self):
        self._kiem_quyen()
        return True

    def doc_lop_chu(self, raw, *, huy=None):
        """Đọc PDF lớp chữ kết quả ABBYY do Core cấp, không gửi OCR lại.

        OCR-NOI/QD-TAM-20261106-12: giữ nguyên đường ocr trả DOCX. Lỗi
        LoiLopChu truyền về lớp chọn nguồn; không nuốt thành lỗi hạn mức
        và không tự gọi mask_ocr. Việc lưu PDF/provenance vẫn do Core làm.
        """
        self._kiem_quyen()
        from .lop_chu import doc_lop_chu
        return doc_lop_chu(raw, huy=huy)

    def ocr(self, raw, duoi, *, huy=None):
        self._kiem_quyen()
        ma = 'ABBYY_CAN_DOI_CHIEU'
        try:
            # Chuyển đúng một lần qua chủ/hạn mức đã được Core cấp.
            docx = self._cong.ocr(raw, duoi, huy=huy)
            if not isinstance(docx, bytes) or not _docx_hop_le(docx):
                ma = 'ABBYY_DOCX_KHONG_HOP_LE'
                raise LoiABBYY(ma)
            return docx
        except Exception as exc:
            _xoa_loi(exc)
        raise LoiABBYY(ma) from None
