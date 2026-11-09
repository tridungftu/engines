"""XS-3d: E-HOADON/v1 bọc riêng nhánh đọc XML/ZIP có sẵn.

Không đọc/ghi bảng M2 hay module nào; không filesystem, mạng, cổng thuế,
thư viện hoặc kết nối mới. Chưa nối M2/M3, chưa bọc nhánh tải M2-00.
Caller cấp bytes/context đã được phép đọc. Tên tệp chỉ là metadata;
``dinh_dang`` tường minh, không đoán định dạng hay sửa dữ liệu nguồn.
Đầu ra là asdict của TOÀN BỘ DTO reader: giữ bytes, Decimal, tuple, mọi
trường hóa đơn, coverage, issues, locator và hash; không dùng ra_json vì
hàm đó bỏ raw bytes. Các kiểu thuần này được hash_du_lieu hỗ trợ sẵn.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from kho_tri_thuc.ha_tang.danh_ba_engine import DanhBaEngine
from kho_tri_thuc.ha_tang.engine import Engine, KhaiBaoEngine, KetQuaXuLy, TrangThaiEngine
from kho_tri_thuc.ha_tang.primitives import DataError
from kho_tri_thuc.nguon.hoa_don_xml import (
    InvoiceReadContext, InvoiceReadResult, InvoiceZipReadResult,
    doc_goi_hoa_don_zip, doc_hoa_don_xml,
)
# G3-GOI-23: ánh xạ trạng thái thuần nằm ở lib của gói engine; re-export cùng object.
from kho_tri_thuc.engines.e_hoa_don.lib.trang_thai import (  # noqa: F401
    ANH_XA_MA_DATAERROR_HOA_DON, ANH_XA_NGOAI_LE_HOA_DON,
    _CHO_CONTEXT, _DA_DOC, _KHONG_DOC_DUOC, _LOI_GOI, _THIEU_CONTEXT,
    _trang_thai_xml, _trang_thai_zip,
)


@dataclass(frozen=True)
class DauVaoHoaDon:
    """XML nhận một context/None; ZIP nhận tuple contexts/None (= tuple rỗng).

    Thiếu context được reader đánh giá; wrapper không tự dựng context.
    Chỉ nhận bytes theo hợp đồng engine, không đường dẫn hay file object.
    """

    raw: bytes
    context: InvoiceReadContext | tuple[InvoiceReadContext, ...] | None = None
    ten_tep: str | None = None
    dinh_dang: str = "XML"


class EngineHoaDon(Engine):
    """Một wrapper dùng chung, thuần; không đọc/ghi bảng hay nối module."""

    def __init__(self) -> None:
        super().__init__(KhaiBaoEngine("E-HOADON", "v1", DauVaoHoaDon, dict))

    def xu_ly(self, dau_vao: DauVaoHoaDon) -> KetQuaXuLy:
        if dau_vao.dinh_dang not in ("XML", "ZIP"):
            return KetQuaXuLy(TrangThaiEngine.LOI, "DINH_DANG_KHONG_HO_TRO",
                              "Định dạng đầu vào phải là XML hoặc ZIP.")
        try:
            if dau_vao.dinh_dang == "XML":
                result = doc_hoa_don_xml(dau_vao.raw, dau_vao.context, artifact_name=dau_vao.ten_tep)
            else:
                contexts = () if dau_vao.context is None else dau_vao.context
                result = doc_goi_hoa_don_zip(dau_vao.raw, contexts, archive_name=dau_vao.ten_tep)
        except DataError as exc:
            # Không suy loại từ tên mã: chỉ nhận đúng lớp và mã đầu vào đã rà.
            # Bare raise giữ nguyên exception, locator và traceback của lỗi nội bộ/lạ.
            if type(exc) is not DataError or exc.code not in ANH_XA_MA_DATAERROR_HOA_DON:
                raise
            trang_thai, ma, ly_do = ANH_XA_MA_DATAERROR_HOA_DON[exc.code]
            return KetQuaXuLy(trang_thai, ma, ly_do)
        except tuple(ANH_XA_NGOAI_LE_HOA_DON) as exc:
            # Chỉ ánh xạ đúng lớp đã công bố; lớp con chưa biết cũng nổi lên.
            if type(exc) not in ANH_XA_NGOAI_LE_HOA_DON:
                raise
            trang_thai, ma, ly_do = ANH_XA_NGOAI_LE_HOA_DON[type(exc)]
            return KetQuaXuLy(trang_thai, ma, ly_do)
        trang_thai, ma, ly_do = (_trang_thai_xml(result) if dau_vao.dinh_dang == "XML"
                                else _trang_thai_zip(result))
        return KetQuaXuLy(trang_thai, ma, ly_do, asdict(result))


def dang_ky_engine_hoa_don(danh_ba: DanhBaEngine) -> EngineHoaDon:
    """Đăng ký riêng lát XS-3d; danh bạ hiện có chịu trách nhiệm từ chối trùng."""
    engine = EngineHoaDon()
    danh_ba.dang_ky(engine)
    return engine
