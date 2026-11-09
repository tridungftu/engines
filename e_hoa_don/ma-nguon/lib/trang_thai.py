"""G3-GOI-23: ánh xạ trạng thái/ngoại lệ THUẦN của engine hóa đơn E-HOADON/v1.

Chép nguyên từ ha_tang/engine_hoa_don.py (thân hàm/bảng không đổi). Enum
TrangThaiEngine lấy từ SDK (sdk_core.engine_legacy), cùng identity, không
định nghĩa enum thứ hai; module này không định nghĩa lớp nào nên không có
__module__ đi vào hash. Chỉ stdlib, SDK và reader cùng gói.
"""

from __future__ import annotations

from lzma import LZMAError
from types import MappingProxyType

from kho_tri_thuc.sdk_core.engine_legacy import TrangThaiEngine

from .hoa_don_xml import InvoiceReadResult, InvoiceZipReadResult


# Chỉ các lý do reader dùng để chặn định danh vì THIẾU context. Không biến
# RAW_REF_NOT_BOUND (không gate content), lỗi dòng hay context mâu thuẫn thành CHO.
_THIEU_CONTEXT = frozenset({
    "CONTEXT_ABSENT", "PROFILE_DOCUMENT_NOT_BOUND", "IDENTITY_PROFILE_ABSENT", "COMPANY_ABSENT",
})
_LOI_GOI = frozenset({"ZIP_MALFORMED", "ZIP_TOO_LARGE", "ZIP_TOO_MANY_ENTRIES"})
_DA_DOC = "Đã đọc hóa đơn bằng bộ đọc hiện có."
_CHO_CONTEXT = "Chờ ngữ cảnh đọc hóa đơn còn thiếu theo bộ đọc."
_KHONG_DOC_DUOC = "Bộ đọc không đọc được tệp hóa đơn trong phạm vi hỗ trợ."


# Rà toàn bộ hoa_don_xml và lời gọi primitives:
# - Đầu vào có thể raise: INPUT_NOT_BYTES (_bytes), INPUT_NAME_TYPE (_ten),
#   CONTEXT_FIELD_TYPE (_context/_tuple và kiểm DTO/context).
# - Nội bộ, phải nổi lên: FIELD_VALUE_INVARIANT, DECIMAL_INVARIANT,
#   RESULT_INVARIANT và ISSUE_SEVERITY (bộ đọc tự dựng issue/DTO).
# - CONTEXT_FORBIDDEN_FIELD/CONTEXT_UNKNOWN_FIELD chỉ ở tu_dict/_keys;
#   hai reader nhận DTO sẵn, không gọi các factory này nên không ánh xạ.
# - AMBIGUOUS_DATE/INVALID_DATE từ date_iso đã bị reader bắt thành issues.
# XML/ZIP hỏng, thiếu field/context, profile không hỗ trợ cũng trả DTO/issues,
# không raise DataError; giữ quyết định trạng thái của _trang_thai_xml/zip.
ANH_XA_MA_DATAERROR_HOA_DON = MappingProxyType({
    "INPUT_NOT_BYTES": (TrangThaiEngine.LOI, "INPUT_NOT_BYTES",
                        "Đầu vào bộ đọc hóa đơn chưa hợp lệ."),
    "INPUT_NAME_TYPE": (TrangThaiEngine.LOI, "INPUT_NAME_TYPE",
                        "Đầu vào bộ đọc hóa đơn chưa hợp lệ."),
    "CONTEXT_FIELD_TYPE": (TrangThaiEngine.LOI, "CONTEXT_FIELD_TYPE",
                           "Đầu vào bộ đọc hóa đơn chưa hợp lệ."),
})


# XML parse, ZIP hỏng/CRC, giải mã tên ZIP đã thành issues trong reader.
# ZIP dùng LZMA có thể để lọt LZMAError khi dữ liệu nén hỏng.
ANH_XA_NGOAI_LE_HOA_DON = MappingProxyType({
    LZMAError: (TrangThaiEngine.LOI, "HOADON_ZIP_LZMA_HONG",
                "Dữ liệu nén trong gói hóa đơn không hợp lệ."),
})


def _trang_thai_xml(result: InvoiceReadResult) -> tuple[TrangThaiEngine, str, str]:
    # shape phản ánh khả năng đọc cấu trúc; issues của dòng/tiền vẫn thuộc XONG.
    if result.shape != "SUPPORTED_SUBSET":
        ma = result.issues[0].code if result.issues else "XML_UNREADABLE"
        return TrangThaiEngine.LOI, ma, _KHONG_DOC_DUOC
    for ma in result.candidate_reasons:
        if ma in _THIEU_CONTEXT:
            return TrangThaiEngine.CHO, ma, _CHO_CONTEXT
    return TrangThaiEngine.XONG, "DA_DOC_HOA_DON", _DA_DOC


def _trang_thai_zip(result: InvoiceZipReadResult) -> tuple[TrangThaiEngine, str, str]:
    for issue in result.issues:
        if issue.code in _LOI_GOI:
            return TrangThaiEngine.LOI, issue.code, _KHONG_DOC_DUOC
    cho = None
    for entry in result.entries:
        if entry.state == "READ_ERROR":
            ma = entry.issues[0].code if entry.issues else "ZIP_MEMBER_READ_ERROR"
            return TrangThaiEngine.LOI, ma, _KHONG_DOC_DUOC
        if entry.result is not None:
            trang_thai = _trang_thai_xml(entry.result)
            if trang_thai[0] == TrangThaiEngine.LOI:
                return trang_thai
            if trang_thai[0] == TrangThaiEngine.CHO and cho is None:
                cho = trang_thai
    return cho or (TrangThaiEngine.XONG, "DA_DOC_HOA_DON", _DA_DOC)
