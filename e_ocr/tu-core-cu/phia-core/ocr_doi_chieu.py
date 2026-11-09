"""Ba cửa OCR của SQL 126, chỉ dùng nội bộ Core, không phải operation SDK.

Caller xác minh quyền, nguồn băm và lease trước khi cấp ngữ cảnh. SQL 126
không kiểm lease/thế hệ; đối chiếu sau việc XONG vẫn cần quyền Core phù hợp.
Chỉ kết quả giữ lượt đã commit mới cho phép caller gửi ABBYY. Đọc trạng thái
không cấp quyền gửi và không tự thử lại khi chưa biết kết quả commit.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import re
from threading import Lock
from uuid import UUID

from ..sdk_core.ngu_canh import _xoa_loi
from .viec import GiuViec


_LOI = {
    'OCR_LUOT_DANG_BI_CHAN': (409, 'P0001', 'Lượt nhận dạng đang xử lý hoặc cần đối chiếu. Chưa thể gửi lại.'),
    'OCR_LUOT_XUNG_DOT': (409, '40001', 'Trạng thái lượt nhận dạng đã thay đổi. Cần kiểm tra lại.'),
    '42501': (403, '42501', 'Không có quyền xử lý lượt nhận dạng.'),
    'OCR_LUOT_DAU_VAO': (400, '22023', 'Thông tin lượt nhận dạng không hợp lệ.'),
    'OCR_LUOT_GIAO_DICH': (409, '25000', 'Chưa thể xử lý lượt nhận dạng trong giao dịch hiện tại.'),
    'OCR_LUOT_THAT_BAI': (500, None, 'Không thể xác nhận lượt nhận dạng. Cần kiểm tra trước khi gửi lại.'),
}


class LoiOCRDoiChieu(RuntimeError):
    """Mã hữu hạn, không giữ thông điệp/metadata từ driver."""

    def __init__(self, ma):
        self.ma = ma if ma in _LOI else 'OCR_LUOT_THAT_BAI'
        self.http_status, self.sqlstate, thong_diep = _LOI[self.ma]
        self.thu_lai_duoc = False  # Không tự gửi lại khi lỗi/commit chưa rõ.
        super().__init__(thong_diep)


def _can(dung):
    if not dung:
        raise LoiOCRDoiChieu('OCR_LUOT_DAU_VAO')


@dataclass(frozen=True, slots=True, repr=False)
class NguCanhOCR:
    """Danh tính từ caller Core đã xác minh; không dựng từ payload engine.

    tu_lease chỉ chép handle, không thay cho việc kiểm lease/quyền của caller.
    Không kiểm hạn lease ở đây để Core có thể đối chiếu sau khi việc đã xong.
    """

    phap_nhan_id: UUID
    module: str
    viec_id: UUID
    the_he: int

    def __post_init__(self):
        _can(isinstance(self.phap_nhan_id, UUID) and isinstance(self.viec_id, UUID)
             and isinstance(self.module, str) and bool(self.module)
             and type(self.the_he) is int and 1 <= self.the_he <= 2**63 - 1)

    @classmethod
    def tu_lease(cls, lease: GiuViec) -> NguCanhOCR:
        _can(isinstance(lease, GiuViec))
        return cls(lease.phap_nhan_id, lease.module, lease.viec_id, lease.the_he)


class TrangThaiLuotOCR(str, Enum):
    GIU = 'GIU'
    CHUA_RO = 'CHUA_RO'
    DA_TIEU_TRANG = 'DA_TIEU_TRANG'
    HOAN_TRANG = 'HOAN_TRANG'


@dataclass(frozen=True, slots=True, repr=False)
class KetQuaLuotOCR:
    giu_trang_id: UUID
    viec_id: UUID
    ma_tuong_quan: str
    so_trang: int
    trang_thai: TrangThaiLuotOCR
    phien_ban: int

    @property
    def dang_chan_gui(self) -> bool:
        return self.trang_thai in (TrangThaiLuotOCR.GIU, TrangThaiLuotOCR.CHUA_RO)


def _doc_ket_qua(raw) -> KetQuaLuotOCR:
    # Contract đóng: không chuyển tiếp băm, tên tệp hoặc chi tiết lạ từ SQL.
    if (not isinstance(raw, Mapping) or set(raw) != {
            'giu_trang_id', 'viec_id', 'ma_tuong_quan', 'so_trang', 'trang_thai', 'phien_ban'}
            or type(raw['so_trang']) is not int or not 1 <= raw['so_trang'] <= 2**31 - 1
            or type(raw['phien_ban']) is not int or not 1 <= raw['phien_ban'] <= 2**63 - 1
            or not isinstance(raw['ma_tuong_quan'], str)
            or re.fullmatch(r'[A-Za-z0-9_:-]{1,128}', raw['ma_tuong_quan']) is None):
        raise LoiOCRDoiChieu('OCR_LUOT_THAT_BAI')
    return KetQuaLuotOCR(UUID(str(raw['giu_trang_id'])), UUID(str(raw['viec_id'])),
        raw['ma_tuong_quan'], raw['so_trang'], TrangThaiLuotOCR(raw['trang_thai']), raw['phien_ban'])


class OCRDoiChieu:
    """Một kết nối dành riêng; sở hữu transaction tới khi commit hoàn tất.

    Ba câu SQL cố định. Pháp nhân/việc lấy từ ngữ cảnh; module/người tạo khi
    giữ lượt do SQL suy ra từ việc. Không nhận tên/đường dẫn/nội dung tệp.
    """

    def __init__(self, ket_noi, *, ngu_canh: NguCanhOCR):
        _can(isinstance(ngu_canh, NguCanhOCR))
        self._ket_noi, self._ctx = ket_noi, ngu_canh
        self._khoa = Lock()

    def __repr__(self):
        return 'OCRDoiChieu(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize dịch vụ đối chiếu nhận dạng')

    def _goi(self, sql, args, *, cho_rong=False, doi_chieu=None):
        ma = 'OCR_LUOT_THAT_BAI'
        row = raw = ket_qua = None
        try:
            with self._khoa:
                if self._ket_noi.info.transaction_status != 0:
                    raise LoiOCRDoiChieu('OCR_LUOT_GIAO_DICH')
                with self._ket_noi.transaction():
                    self._ket_noi.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED')
                    row = self._ket_noi.execute(sql, args).fetchone()
                    raw = row['r'] if isinstance(row, Mapping) else row[0]
                    if raw is None:
                        if not cho_rong:
                            raise LoiOCRDoiChieu('OCR_LUOT_THAT_BAI')
                    else:
                        ket_qua = _doc_ket_qua(raw)
                        if doi_chieu and any(getattr(ket_qua, k) != v for k, v in doi_chieu.items()):
                            raise LoiOCRDoiChieu('OCR_LUOT_THAT_BAI')
            return ket_qua  # Ngoài transaction: lỗi commit không công bố kết quả.
        except Exception as exc:
            if isinstance(exc, LoiOCRDoiChieu):
                ma = exc.ma
            else:
                ma = {'P0001': 'OCR_LUOT_DANG_BI_CHAN', '55P03': 'OCR_LUOT_DANG_BI_CHAN',
                      '40001': 'OCR_LUOT_XUNG_DOT', '40P01': 'OCR_LUOT_XUNG_DOT',
                      '42501': '42501', '22023': 'OCR_LUOT_DAU_VAO',
                      '25000': 'OCR_LUOT_GIAO_DICH'}.get(getattr(exc, 'sqlstate', None), ma)
            _xoa_loi(exc)
        # Raise ngoài except; không giữ args/kết quả/driver ở context hoặc cause.
        args = row = raw = ket_qua = doi_chieu = None
        raise LoiOCRDoiChieu(ma) from None

    @staticmethod
    def _kiem_bam(ma_bam):
        _can(isinstance(ma_bam, str) and re.fullmatch(r'[0-9a-f]{64}', ma_bam) is not None)

    def giu_luot(self, *, ma_bam: str, ma_tuong_quan: str, so_trang: int,
                 giu_trang_id: UUID) -> KetQuaLuotOCR:
        """Kiểm–giữ nguyên tử, commit trước khi cho caller gửi ra ngoài."""
        self._kiem_bam(ma_bam)
        _can(isinstance(giu_trang_id, UUID) and type(so_trang) is int and 1 <= so_trang <= 2**31 - 1
             and isinstance(ma_tuong_quan, str)
             and re.fullmatch(r'[A-Za-z0-9_:-]{1,128}', ma_tuong_quan) is not None)
        return self._goi('SELECT loi_tai_lieu.ocr_giu_luot(%s,%s,%s,%s,%s,%s) AS r',
            (self._ctx.phap_nhan_id, ma_bam, self._ctx.viec_id, ma_tuong_quan, so_trang, giu_trang_id),
            doi_chieu=dict(giu_trang_id=giu_trang_id, viec_id=self._ctx.viec_id,
                ma_tuong_quan=ma_tuong_quan, so_trang=so_trang,
                trang_thai=TrangThaiLuotOCR.GIU, phien_ban=1))

    def chot_luot(self, *, ma_bam: str, giu_trang_id: UUID, phien_ban: int,
                  trang_thai_cu: TrangThaiLuotOCR, trang_thai_moi: TrangThaiLuotOCR) -> KetQuaLuotOCR:
        self._kiem_bam(ma_bam)
        _can(isinstance(giu_trang_id, UUID) and type(phien_ban) is int and 1 <= phien_ban < 2**63 - 1)
        if (trang_thai_cu not in (TrangThaiLuotOCR.GIU, TrangThaiLuotOCR.CHUA_RO)
                or trang_thai_moi not in (TrangThaiLuotOCR.CHUA_RO, TrangThaiLuotOCR.DA_TIEU_TRANG,
                                         TrangThaiLuotOCR.HOAN_TRANG)
                or trang_thai_cu == trang_thai_moi):
            raise LoiOCRDoiChieu('OCR_LUOT_XUNG_DOT')
        return self._goi('SELECT loi_tai_lieu.ocr_chot_luot(%s,%s,%s,%s,%s,%s) AS r',
            (self._ctx.phap_nhan_id, ma_bam, giu_trang_id, phien_ban,
             TrangThaiLuotOCR(trang_thai_cu).value, TrangThaiLuotOCR(trang_thai_moi).value),
            doi_chieu=dict(giu_trang_id=giu_trang_id, phien_ban=phien_ban + 1,
                          trang_thai=TrangThaiLuotOCR(trang_thai_moi)))

    def doc_trang_thai(self, *, ma_bam: str) -> KetQuaLuotOCR | None:
        """Snapshot đối chiếu trong pháp nhân, kể cả lượt thuộc module khác."""
        self._kiem_bam(ma_bam)
        return self._goi('SELECT loi_tai_lieu.ocr_doc_trang_thai(%s,%s) AS r',
                         (self._ctx.phap_nhan_id, ma_bam), cho_rong=True)
