"""OCR-CHON: ABBYY PDF trước, mask_ocr/Tesseract dự phòng.

Core cấp SDK để kiểm–giữ lượt bền trước gửi; không có thao tác SDK thì giữ seam cũ.
Core tiêm backend san_sang()/doc_pdf(raw, duoi, huy=...) có timeout và
CongOCR đang giữ sổ chung. doc_pdf chỉ vận chuyển, KHÔNG tự tính trang;
không truyền BackendABBYY.ocr (đường DOCX cũ đã tự tính trang) vào seam này.
Không tạo cổng, sổ, kết nối, cấu hình hoặc bảng CSDL khác.
"""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import logging
import threading
import time
from uuid import UUID, uuid4

from ...sdk_core import kenh_khung
from ...sdk_core.ngu_canh import _xoa_loi
from ...sdk_core.primitives import DataError
from .abbyy import BackendKetNoiABBYY
from .ket_noi_abbyy import KetNoiABBYY, LoiKetNoiABBYY
from .lib.cong_ocr import CUA_SO_NGAY, HAN_MUC, CongOCR, _kiem_huy, _khoa_tep
from .lop_chu import MAX_BYTES, MAX_PAGES, MAX_TEXT, KetQuaLopChu, doc_lop_chu
from .van_ban import _nhap_parser_nguon


LY_DO = {
    'het_han_muc': 'Không đủ hạn mức ABBYY 5.000 trang trong 30 ngày gần nhất.',
    'khong_ket_noi': 'Không kết nối được máy ABBYY.',
    'qua_thoi_gian': 'ABBYY quá thời gian xử lý tài liệu.',
    'loi_nhan_dang': 'ABBYY không trả được đầy đủ kết quả đọc tài liệu.',
    'pdf_thieu_lop_chu': 'Kết quả ABBYY thiếu lớp chữ; cần nhận dạng từ tài liệu gốc.',
    'so_han_muc_can_kiem_tra': 'Chưa xác nhận được sổ hạn mức ABBYY; cần kiểm tra lại.',
    'chua_ro': 'Chưa rõ kết quả nhận dạng ABBYY; giữ hạn mức và chờ đối chiếu trước khi gửi lại.',
}
_MUI_GIO = timezone(timedelta(hours=7))
_LOG = logging.getLogger(__name__)
# Chỉ metadata trong RAM, dùng chung giữa các đối tượng cùng sổ/tiến trình.
# Seam cũ không tự quên việc chưa rõ; khi có SDK, Core giữ dấu bền.
_KHOA_LUOT = threading.Lock()
_LUOT_CHO = {}
_TOI_DA_LUOT_CHO = 1024
# Chỉ dấu đã xử lý, không giữ nội dung/kết quả tài liệu trong cache.
_LUOT_XONG = OrderedDict()
_TOI_DA_LUOT_XONG = 1000


@dataclass
class _LuotCho:
    ma: str
    so_trang: int
    trang_thai: str = 'đang chờ'
    phien_ban: int | None = None


def _cho_doi_chieu():
    loi = DataError('OCR_CHO_DOI_CHIEU', 'Tài liệu đang chờ đối chiếu kết quả nhận dạng.')
    loi.trang_thai_abbyy = 'chua_ro'
    return loi


def _loi_luot(luot):
    chua_ro = luot.trang_thai == 'chưa rõ'
    if luot.trang_thai == 'thành công':
        loi = DataError('OCR_DA_XU_LY', 'Tài liệu đã được nhận dạng; cần dùng kết quả đã có.')
    else:
        loi = DataError('OCR_CHUA_RO_KET_QUA' if chua_ro else 'OCR_DANG_XU_LY',
                       LY_DO['chua_ro'] if chua_ro else 'Tài liệu đang được nhận dạng; cần chờ kết quả.')
    # Nội bộ/chi tiết hỗ trợ; không ghép mã vào thông báo nghiệp vụ.
    loi.ma_tuong_quan = luot.ma
    loi.trang_thai_abbyy = 'chua_ro' if chua_ro else luot.trang_thai
    return loi


def _kem_doi_chieu(ket_qua, luot):
    if luot.trang_thai == 'chưa rõ':
        ket_qua.trang_thai_abbyy = 'chua_ro'
        ket_qua.ma_tuong_quan = luot.ma
    return ket_qua


def _chac_chan_chua_nhan(exc):
    # Bằng chứng tiếp nhận/chưa rõ luôn thắng mã lỗi chưa nhận của seam cũ.
    if getattr(exc, 'chua_ro_da_nhan', None) is True:
        return False
    if isinstance(exc, LoiKetNoiABBYY):
        return exc.chua_ro_da_nhan is False
    return getattr(exc, 'code', None) in ('OCR_KHONG_NHAN', 'OCR_HET_HAN_MUC')


@dataclass(repr=False)
class KetQuaChonNguon(KetQuaLopChu):
    nguon_doc: str = 'ABBYY'
    ma_ly_do_chuyen: str | None = None
    ly_do_chuyen: str | None = None
    trang_thai_abbyy: str | None = None
    ma_tuong_quan: str | None = None

    def du_lieu(self):
        """Phản hồi nguồn nội bộ; không thay contract/provenance của Core."""
        return asdict(self)


def _ly_do_loi(exc):
    ma = getattr(exc, 'ma', getattr(exc, 'code', None))
    if ma == 'OCR_HUY':
        return 'huy'
    if ma == 'OCR_PDF_KHONG_LOP_CHU':
        return 'pdf_thieu_lop_chu'
    if isinstance(exc, TimeoutError) or ma == 'OCR_QUA_GIO':
        return 'qua_thoi_gian'
    if isinstance(exc, ConnectionError) or ma in ('OCR_KHONG_NHAN', 'ABBYY_KHONG_KET_NOI'):
        return 'khong_ket_noi'
    if ma == 'OCR_HET_HAN_MUC':
        return 'het_han_muc'
    return 'loi_nhan_dang'


def _dem_trang(raw, duoi):
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES:
        raise DataError('OCR_KICH_THUOC', 'Tài liệu phải có nội dung, tối đa 20 MiB.')
    if not isinstance(duoi, str) or duoi.lower().lstrip('.') not in ('pdf', 'png', 'jpg', 'jpeg'):
        raise DataError('OCR_DINH_DANG', 'Chỉ nhận tài liệu PDF, PNG hoặc JPEG.')
    duoi = duoi.lower().lstrip('.')
    loi = False
    try:
        if duoi == 'pdf':
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                so_trang = len(pdf.pages)
        else:
            from PIL import Image
            with Image.open(io.BytesIO(raw)) as image:
                if (image.format != ('PNG' if duoi == 'png' else 'JPEG')
                        or getattr(image, 'n_frames', 1) != 1
                        or image.width * image.height > 20_000_000):
                    raise ValueError
                image.verify()
            so_trang = 1
        if not 0 < so_trang <= MAX_PAGES:
            raise ValueError
    except Exception as exc:
        _xoa_loi(exc)
        loi = True
    if loi:
        raise DataError('OCR_TAI_LIEU', 'Không đọc được tài liệu hoặc tài liệu vượt 60 trang; cần kiểm tra nguồn.') from None
    return duoi, so_trang


def _ket_qua(result, so_trang, nguon, reason=None):
    if (not isinstance(result.text, str) or not result.text.strip() or len(result.text) > MAX_TEXT
            or not isinstance(result.warnings, list)
            or any(not isinstance(w, str) for w in result.warnings)
            or type(result.ocr_pages) is not int or not 0 <= result.ocr_pages <= so_trang
            or not isinstance(result.pages, list) or len(result.pages) != so_trang
            or any(not isinstance(p, dict) or p.get('number') != i
                   or not isinstance(p.get('text'), str) or not p['text'].strip()
                   for i, p in enumerate(result.pages, 1))):
        raise ValueError('Kết quả đọc tài liệu không đầy đủ.')
    return KetQuaChonNguon(result.text, deepcopy(result.warnings), result.ocr_pages,
                           deepcopy(result.pages), nguon, reason, LY_DO.get(reason))


def doc_mask_ocr(raw, duoi, *, huy=None):
    """Dùng đúng image_text trong gói (Tesseract); không dựng pool/worker.

    Vendor chưa đóng gói page_worker.py của extract_pdf. PDF được render
    trong RAM, cùng khóa MuPDF của vendor, rồi gọi image_text từng trang.
    Hàm nguồn chỉ trả chữ; không tự đặt confidence hoặc vị trí chữ.
    """
    _kiem_huy(huy)
    extraction, _ = _nhap_parser_nguon()
    pages = []
    with extraction.PDF_LOCK:
        if duoi == 'pdf':
            with extraction.pymupdf.open(stream=raw, filetype='pdf') as pdf:
                if pdf.needs_pass or not 0 < len(pdf) <= MAX_PAGES:
                    raise ValueError('Không đọc được tài liệu PDF.')
                for number, page in enumerate(pdf, 1):
                    _kiem_huy(huy)
                    if page.rect.width * page.rect.height * (150 / 72) ** 2 > 20_000_000:
                        raise ValueError('Trang quá lớn để nhận dạng.')
                    png = page.get_pixmap(dpi=150, alpha=False).tobytes('png')
                    text = extraction.image_text(png)
                    pages.append(dict(number=number, text=text, mode='full', source='mask_ocr'))
        else:
            pages.append(dict(number=1, text=extraction.image_text(raw), mode='full', source='mask_ocr'))
    _kiem_huy(huy)
    return KetQuaLopChu('\n\n'.join(f'[Trang {p["number"]}]\n{p["text"]}' for p in pages),
                         ['Cần đối chiếu nội dung nhận dạng với tài liệu gốc.'], len(pages), pages)


class ChonNguonOCR:
    def __init__(self, *, abbyy=None, cong_ocr, mask_ocr=None, phap_nhan_id=None, ben_goi=None,
                 sdk=None):
        """Core cấp pháp nhân và bên gọi ổn định từ ngữ cảnh đã kiểm quyền.

        Bỏ trống cả hai giữ phạm vi sổ cũ cho seam tương thích; không lấy
        danh tính từ tài liệu, đuôi tệp hoặc UUID của từng lượt nhận dạng.
        Chống trùng theo pháp nhân, dùng chung giữa các module gọi.
        SDK của chính việc do Core tiêm; danh tính/lease không lấy từ payload.
        SDK cũ chưa có đủ ba thao tác giữ nguyên đường mock/DEMO hiện có.
        """
        if abbyy is None:
            abbyy = BackendKetNoiABBYY()
        if (not isinstance(cong_ocr, CongOCR) or not callable(getattr(abbyy, 'san_sang', None))
                or not callable(getattr(abbyy, 'doc_pdf', None))
                or (mask_ocr is not None and not callable(mask_ocr))):
            raise TypeError('Cần sổ chung và bộ đọc PDF do Core cấp.')
        if phap_nhan_id is not None or ben_goi is not None:
            try:
                phap_nhan_id = str(UUID(str(phap_nhan_id)))
                if (not isinstance(ben_goi, str) or not 0 < len(ben_goi) <= 200
                        or ben_goi != ben_goi.strip()):
                    raise ValueError
            except (ValueError, TypeError, AttributeError):
                raise TypeError('Cần đầy đủ pháp nhân và bên gọi hợp lệ do Core cấp.') from None
        self._abbyy, self._cong = abbyy, cong_ocr
        self._sdk = sdk if all(callable(getattr(sdk, ten, None)) for ten in (
            'ocr_doc_luot', 'ocr_giu_luot', 'ocr_chot_luot')) else None
        self._pham_vi = (cong_ocr.tep_so_trang, phap_nhan_id)
        self._mask = doc_mask_ocr if mask_ocr is None else mask_ocr
        self._loi_gan_nhat = None

    def _kiem_may(self):
        reason = None
        try:
            if self._abbyy.san_sang() is not True:
                reason = 'khong_ket_noi'
        except Exception as exc:
            reason = _ly_do_loi(exc)
            _xoa_loi(exc)
        return reason

    def _giu_trang(self, so_trang, ma, *, huy=None):
        """Dùng khóa, mã giữ chỗ và xác nhận sau ghi của cổng chung."""
        if self._sdk is None:
            self._cong._giu_trang(so_trang, ma, huy=huy)
        else:
            self._cong._giu_trang(so_trang, ma, huy=huy, ma_ben=ma)

    def _kiem_luot_ben(self, raw):
        if self._sdk is None:
            return
        trang_thai = None
        try:
            data = self._sdk.ocr_doc_luot(bam_noi_dung=hashlib.sha256(raw).hexdigest())
            trang_thai = kenh_khung.kiem_dto_ocr('ocr.doc_luot', data, phan_hoi=True)['trang_thai']
        except Exception as exc:
            _xoa_loi(exc)
        if trang_thai in ('khong_co', 'hoan_trang'):
            return
        if trang_thai == 'da_tieu':
            raise DataError('OCR_DA_XU_LY', 'Tài liệu đã được nhận dạng; cần dùng kết quả đã có.') from None
        self._loi_gan_nhat = 'chua_ro'
        raise _cho_doi_chieu() from None

    def _giu_luot_ben(self, raw, so_trang, luot):
        if self._sdk is None:
            return
        data = None
        try:
            data = kenh_khung.kiem_dto_ocr('ocr.giu_luot', self._sdk.ocr_giu_luot(
                bam_noi_dung=hashlib.sha256(raw).hexdigest(), so_trang=so_trang), phan_hoi=True)
        except Exception as exc:
            _xoa_loi(exc)
        if data is None:
            # Bao gồm bị chặn do đua, mất phản hồi sau commit và DTO không hợp lệ.
            # Không đọc rồi tự suy quyền gửi, không retry hoặc hoàn lượt chưa biết.
            self._loi_gan_nhat = 'chua_ro'
            raise _cho_doi_chieu() from None
        luot.ma, luot.phien_ban = data['ma_tuong_quan'], data['phien_ban']

    def _chot_luot_ben(self, luot, ket_qua):
        if self._sdk is None:
            return
        data = kenh_khung.kiem_dto_ocr('ocr.chot_luot', self._sdk.ocr_chot_luot(
            ma_tuong_quan=luot.ma, ket_qua=ket_qua, phien_ban=luot.phien_ban), phan_hoi=True)
        if data['trang_thai'] != ket_qua:
            raise ValueError('Chưa xác nhận được đối chiếu lượt nhận dạng.')

    def _dang_ky(self, raw, duoi, so_trang, ma_yeu_cau):
        ma_hop_le = True
        if ma_yeu_cau is not None:
            try:
                if not isinstance(ma_yeu_cau, str):
                    raise ValueError
                ma_yeu_cau = str(UUID(ma_yeu_cau))
            except (ValueError, AttributeError):
                ma_hop_le = False
        if not ma_hop_le:
            raise DataError('OCR_MA_YEU_CAU', 'Thông tin yêu cầu nhận dạng không hợp lệ.') from None
        ma = ma_yeu_cau or str(uuid4())
        keys = [(self._pham_vi, 'tai_lieu', hashlib.sha256(raw).digest()),
                (self._pham_vi, 'yeu_cau', ma)]
        with _KHOA_LUOT:
            for key in keys:
                if key in _LUOT_CHO:
                    raise _loi_luot(_LUOT_CHO[key])
            khoa_xong = keys[0]
            if khoa_xong not in _LUOT_XONG and ma_yeu_cau is not None:
                khoa_xong = next((key for key, old in _LUOT_XONG.items()
                                  if key[0] == self._pham_vi and old.ma == ma), None)
            if khoa_xong in _LUOT_XONG:
                _LUOT_XONG.move_to_end(khoa_xong)
                raise _loi_luot(_LUOT_XONG[khoa_xong])
            if len(_LUOT_CHO) >= 2 * _TOI_DA_LUOT_CHO:
                raise DataError('OCR_CHO_DOI_CHIEU', 'Cần đối chiếu các lượt nhận dạng trước khi nhận thêm.')
            luot = _LuotCho(ma, so_trang)
            for key in keys:
                _LUOT_CHO[key] = luot
        return luot, keys

    def doc(self, raw, duoi, *, huy=None, ma_yeu_cau=None):
        _kiem_huy(huy)
        duoi, so_trang = _dem_trang(raw, duoi)
        _kiem_huy(huy)
        luot, keys = self._dang_ky(raw, duoi, so_trang, ma_yeu_cau)
        bat_dau = time.monotonic()
        try:
            self._kiem_luot_ben(raw)
            return _kem_doi_chieu(self._doc(raw, duoi, so_trang, luot, huy=huy), luot)
        except BaseException as exc:
            # Bao phủ cả hủy trước/trong/sau fallback và thoát bất thường.
            _kem_doi_chieu(exc, luot)
            raise
        finally:
            with _KHOA_LUOT:
                if self._sdk is None and luot.trang_thai == 'thành công' and keys:
                    # Chuyển sang dấu đã xử lý và bỏ khóa chờ trong cùng khóa.
                    _LUOT_XONG[keys[0]] = luot
                    while len(_LUOT_XONG) > _TOI_DA_LUOT_XONG:
                        _LUOT_XONG.popitem(last=False)
                if self._sdk is not None or luot.trang_thai != 'chưa rõ':
                    for key in keys:
                        _LUOT_CHO.pop(key, None)
            try:
                _LOG.info('%s', json.dumps(dict(ma_tuong_quan=luot.ma, ket_qua=luot.trang_thai,
                          thoi_gian=round(time.monotonic() - bat_dau, 6), so_trang=so_trang), ensure_ascii=False))
            except Exception as exc:
                _xoa_loi(exc)

    def _doc(self, raw, duoi, so_trang, luot, *, huy=None):
        reason = self._kiem_may()
        if reason == 'huy':
            raise DataError('OCR_HUY', 'Đã hủy nhận dạng tài liệu.')
        if reason is not None:
            self._loi_gan_nhat = reason
        if reason is None:
            # Chỉ phản hồi giữ lượt sau commit của Core cấp quyền gửi.
            # Đặt ngoài nhánh fallback: bị chặn/mất phản hồi trả lỗi hữu hạn.
            self._giu_luot_ben(raw, so_trang, luot)
        ma = luot.ma
        if reason is None:
            dang_giu, thanh_cong = True, False
            da_goi, hoan_duoc = False, True
            try:
                self._giu_trang(so_trang, ma, huy=huy)
                dang_giu = False
                _kiem_huy(huy)
                # Lỗi lấy backend/chuẩn bị tham số vẫn xảy ra trước gửi.
                doc_pdf = self._abbyy.doc_pdf
                tham_so = dict(huy=huy)
                if isinstance(self._abbyy, (BackendKetNoiABBYY, KetNoiABBYY)):
                    tham_so['ma_yeu_cau'] = ma
                # Trần đọc do adapter Hot Folder/KN3 giữ, không đổi seam cũ.
                da_goi, hoan_duoc = True, False
                pdf = doc_pdf(raw, duoi, **tham_so)
                _kiem_huy(huy)
                result = _ket_qua(doc_lop_chu(pdf, huy=huy), so_trang, 'ABBYY')
                _kiem_huy(huy)
                self._chot_luot_ben(luot, 'da_tieu')
                # Thành công mới giữ trang; chỉ bỏ con trỏ giữ chỗ trong RAM.
                self._cong._giu_cho.pop(ma, None)
                self._loi_gan_nhat = None
                luot.trang_thai = 'thành công'
                thanh_cong = True
                return result
            except Exception as exc:
                reason = _ly_do_loi(exc)
                hoan_duoc = (not da_goi or _chac_chan_chua_nhan(exc)
                             or (self._sdk is not None
                                 and getattr(exc, 'chua_ro_da_nhan', None) is False))
                if not hoan_duoc:
                    luot.trang_thai = 'chưa rõ'
                    if reason != 'huy':
                        reason = 'chua_ro'
                if dang_giu and reason not in ('het_han_muc', 'huy'):
                    reason = 'so_han_muc_can_kiem_tra'
                _xoa_loi(exc)
            finally:
                if not thanh_cong and not hoan_duoc:
                    # Kể cả hủy/thoát bất thường sau gọi: không chứng minh
                    # chưa nhận thì giữ trang và chặn lần gửi tiếp theo.
                    luot.trang_thai = 'chưa rõ'
                    self._loi_gan_nhat = 'chua_ro'
                if not thanh_cong and hoan_duoc:
                    try:
                        self._cong._hoan_trang(ma)
                        self._chot_luot_ben(luot, 'hoan_trang')
                    except Exception as exc:
                        _xoa_loi(exc)
                        # Không khẳng định đã hoàn khi không ghi được sổ.
                        if self._sdk is not None:
                            luot.trang_thai = 'chưa rõ'
                            self._loi_gan_nhat = 'chua_ro'
                        if reason != 'huy':
                            reason = 'chua_ro' if self._sdk is not None else 'so_han_muc_can_kiem_tra'
                    if reason not in (None, 'huy'):
                        self._loi_gan_nhat = reason
        if reason == 'huy':
            raise DataError('OCR_HUY', 'Đã hủy nhận dạng tài liệu.') from None
        _kiem_huy(huy)
        loi = None
        try:
            result = self._mask(raw, duoi, huy=huy)
            _kiem_huy(huy)
            result = _ket_qua(result, so_trang, 'mask_ocr', reason)
            if luot.trang_thai != 'chưa rõ':
                luot.trang_thai = 'chuyển nguồn'
            return result
        except Exception as exc:
            loi = _ly_do_loi(exc)
            _xoa_loi(exc)
        if loi == 'huy':
            raise DataError('OCR_HUY', 'Đã hủy nhận dạng tài liệu.') from None
        if luot.trang_thai == 'chưa rõ':
            raise _loi_luot(luot) from None
        raise DataError('OCR_KHONG_DOC_DUOC', 'Các nguồn đọc chưa xử lý được tài liệu; cần kiểm tra và thử lại.') from None

    def trang_thai(self):
        """Cửa sổ trượt 30 ngày theo giờ Việt Nam; không lộ đường dẫn/lỗi gốc.

        Sổ chứa cả trang tạm giữ của việc đang chạy. Lỗi sổ trả null thay
        cho 0. Lỗi máy gần nhất chỉ giữ trong phiên engine, không phải log.
        """
        used, loi_so = None, None
        try:
            with _khoa_tep(self._cong.tep_so_trang.with_suffix('.lock'), self._cong.nghi):
                used = sum(x[1] for x in self._cong._doc_so())
        except Exception as exc:
            _xoa_loi(exc)
            loi_so = LY_DO['so_han_muc_can_kiem_tra']
        reason = self._kiem_may()
        with _KHOA_LUOT:
            chua_ro = {x.ma: dict(ma_tuong_quan=x.ma, so_trang=x.so_trang)
                       for key, x in _LUOT_CHO.items()
                       if key[0] == self._pham_vi and x.trang_thai == 'chưa rõ'}
        state = 'sẵn sàng'
        if chua_ro:
            state = 'chưa rõ'
            reason = 'chua_ro'
        elif reason == 'khong_ket_noi':
            state = 'không kết nối'
        elif reason is not None or self._loi_gan_nhat not in (None, 'khong_ket_noi'):
            state = 'lỗi gần nhất'
        return dict(han_muc=HAN_MUC, so_ngay=CUA_SO_NGAY, han_muc_da_dung=used,
                    han_muc_con_lai=None if used is None else max(0, HAN_MUC - used),
                    ngay_bat_dau_ky=datetime.fromtimestamp(
                        time.time() - CUA_SO_NGAY * 86400, _MUI_GIO).strftime('%d/%m/%Y'),
                    trang_thai_may_abbyy=state, loi_gan_nhat=LY_DO.get(reason or self._loi_gan_nhat),
                    luot_chua_ro=list(chua_ro.values()),
                    loi_han_muc=loi_so)
