"""Danh sách Đỏ và kết quả kiểm §5.3; toàn bộ đọc/ghi trong RAM.

Lớp ghi XML sheet chép-sửa từ e_kiem_excel/bao_cao.py (_GhiExcelBoNho).
Phụ thuộc API nội bộ của openpyxl 3.1.5 đã ghim trong requirements.lock.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from io import BytesIO
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import openpyxl
from openpyxl.drawing.spreadsheet_drawing import SpreadsheetDrawing
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet._writer import WorksheetWriter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.writer.excel import ExcelWriter

from . import kieu
from .kieu import KetQuaDong
from .loi import loi
from .tien import doc_tien, tien_ra


TEN_LY_DO = {
    kieu.VUOT_PM: "Vượt ngưỡng PM",
    kieu.VUOT_TE: "Vượt ngưỡng TE",
    kieu.CHUA_QUY_DOI: "Chưa quy đổi tiền tệ",
    kieu.CHUA_RO_TIEN_TE: "Chưa rõ tiền tệ",
    kieu.NGHI_CHIA_NHO: "Nghi chia nhỏ nghiệp vụ",
    kieu.CO_DO_CUNG: "Cảnh báo từ module",
    kieu.NOP_LAI: "Nộp lại nghiệp vụ cần kiểm",
    kieu.CHON_MAU: "Được chọn kiểm tra",
    kieu.KHONG_CHON: "Không được chọn kiểm tra",
}
TEN_CO = {
    kieu.SO_TIEN_BAT_THUONG: "Số tiền bất thường",
    kieu.DOI_TAC_MOI: "Đối tác mới",
    kieu.SO_TRON: "Số tròn",
    kieu.NGAY_NGHI: "Ngày nghỉ",
    kieu.CUOI_KY: "Cuối kỳ",
    kieu.NHAP_TAY: "Nhập tay",
}
_COT = ("Mã", "Lý do", "Cờ", "Loại", "Nguồn loại", "Kết quả",
        "Số tiền sai", "Tiền tệ", "Loại đúng")
_NHAN = ("ma_luot", "khau", "ma_module", "phien_ban_engine")
_MOC = datetime(2000, 1, 1)
_NGAY_ZIP = (2000, 1, 1, 0, 0, 0)
_TOI_DA_DONG = 50_000
_TOI_DA_BYTE = 20 * 1048576
_KET_QUA = (kieu.KQ_DAT, kieu.KQ_SAI, kieu.KQ_KHONG_KIEM)


class _ZipCoDinh(ZipFile):
    def writestr(self, zinfo_or_arcname, data, compress_type=None, compresslevel=None):
        ten = (zinfo_or_arcname.filename if isinstance(zinfo_or_arcname, ZipInfo)
               else zinfo_or_arcname)
        thong_tin = ZipInfo(ten, _NGAY_ZIP)
        thong_tin.create_system = 0
        return super().writestr(thong_tin, data, compress_type=ZIP_DEFLATED)


class _GhiExcelBoNho(ExcelWriter):
    def write_worksheet(self, ws):
        ws._drawing = SpreadsheetDrawing()
        ws._drawing.charts = ws._charts
        ws._drawing.images = ws._images
        with BytesIO() as out:
            writer = WorksheetWriter(ws, out=out)
            try:
                writer.write()
                ws._rels = writer._rels
                self._archive.writestr(ws.path[1:], writer.read())
                self.manifest.append(ws)
            finally:
                writer.close()


def _chu(gia_tri, toi_da=120):
    if (not isinstance(gia_tri, str) or not gia_tri.strip()
            or len(gia_tri) > toi_da
            or any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in gia_tri)):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    return gia_tri


def _kiem_metadata(ma_luot, khau, ma_module, phien_ban_engine):
    _chu(ma_luot)
    _chu(khau, 40)
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,30}", _chu(ma_module, 31)):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    _chu(phien_ban_engine)


def _ghi_chu(ws, dong, cot, gia_tri):
    """Giữ mã nguyên văn, kể cả mã bắt đầu bằng dấu bằng."""
    o = ws.cell(dong, cot, gia_tri)
    o.data_type = "s"
    o.alignment = Alignment(vertical="top", wrap_text=True)
    return o


def lap_ds_do(ds: Sequence[KetQuaDong], *, ma_luot, ma_module, khau,
              phien_ban_engine) -> bytes:
    """Dòng 1 là metadata theo cặp nhãn/giá trị; dòng 2 là tiêu đề cố định."""
    _kiem_metadata(ma_luot, khau, ma_module, phien_ban_engine)
    if len(ds) > _TOI_DA_DONG:
        raise loi("VUOT_GIOI_HAN")
    wb = openpyxl.Workbook()
    try:
        wb.properties.created = wb.properties.modified = _MOC
        wb.properties.creator = "e_phan_luong"
        ws = wb.active
        ws.title = "Can kiem"
        for cot, (nhan, gia_tri) in enumerate(zip(
                _NHAN, (ma_luot, khau, ma_module, phien_ban_engine)), 1):
            _ghi_chu(ws, 1, 2 * cot - 1, nhan)
            _ghi_chu(ws, 1, 2 * cot, gia_tri)
        for cot, ten in enumerate(_COT, 1):
            o = _ghi_chu(ws, 2, cot, ten)
            o.font = Font(bold=True, color="FFFFFF")
            o.fill = PatternFill("solid", fgColor="9C3030")
        dong = 2
        for nv in ds:
            if nv.luong != "do":
                continue
            _chu(nv.ma)
            try:
                ly_do = "; ".join(TEN_LY_DO[m] for m in nv.ly_do)
                co = "; ".join(TEN_CO[m] for m in nv.co)
            except KeyError:
                raise loi("DU_LIEU_KHONG_HOP_LE") from None
            dong += 1
            for cot, gia_tri in enumerate((nv.ma, ly_do, co, nv.loai, nv.nguon_loai), 1):
                _ghi_chu(ws, dong, cot, _chu(gia_tri, 32767) if gia_tri else "")
            for cot in range(6, 10):
                ws.cell(dong, cot).number_format = "@"
        dv = DataValidation(type="list", formula1='"dat,sai,khong_kiem"',
                            allow_blank=True)
        dv.showErrorMessage = True
        dv.errorStyle = "stop"
        dv.errorTitle = "Kết quả chưa đúng"
        dv.error = "Chọn dat, sai hoặc khong_kiem."
        ws.add_data_validation(dv)
        if dong >= 3:
            dv.add(f"F3:F{dong}")
        ws.freeze_panes = "F3"
        ws.auto_filter.ref = f"A2:I{dong}"
        for cot, rong in enumerate((25, 48, 40, 25, 22, 18, 25, 12, 25), 1):
            ws.column_dimensions[get_column_letter(cot)].width = rong
        hd = wb.create_sheet("Huong dan")
        for dong, noi_dung in enumerate((
                "HƯỚNG DẪN GHI KẾT QUẢ KIỂM",
                "Giữ nguyên dòng đầu, tiêu đề và các cột từ Mã đến Nguồn loại.",
                "Kết quả: dat = đạt; sai = có sai sót; khong_kiem = chưa kiểm.",
                "Để trống Kết quả nếu chưa gửi; dòng đó sẽ được bỏ qua khi đọc lại.",
                "Khi ghi sai, điền Số tiền sai và Tiền tệ (mã ba chữ hoa).",
                "Nhập tiền bằng chuỗi thập phân, dấu chấm phần lẻ, không phân nhóm.",
                "Cột Số tiền sai có dạng văn bản để giữ chính xác số đã nhập.",
                "Loại đúng: điền mã loại trong danh mục nếu cần sửa; còn lại để trống.",
                "Module đọc lại tệp để lập JSON kết quả kiểm và gửi kèm ngưỡng phù hợp.",
        ), 1):
            _ghi_chu(hd, dong, 1, noi_dung)
        hd.column_dimensions["A"].width = 105
        out = BytesIO()
        with _ZipCoDinh(out, "w", ZIP_DEFLATED) as archive:
            _GhiExcelBoNho(wb, archive).write_data()
        du_lieu = out.getvalue()
        if len(du_lieu) > _TOI_DA_BYTE:
            raise loi("VUOT_GIOI_HAN")
        return du_lieu
    finally:
        wb.close()


def _doc_mau(wb):
    if wb.sheetnames != ["Can kiem", "Huong dan"]:
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ws = wb["Can kiem"]
    if ws.max_row > _TOI_DA_DONG + 2:
        raise loi("VUOT_GIOI_HAN")
    if (ws.max_column != 9 or tuple(o.value for o in ws[2]) != _COT
            or tuple(ws.cell(1, c).value for c in (1, 3, 5, 7)) != _NHAN
            or ws.cell(1, 9).value is not None):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    ma_luot, khau, ma_module, phien_ban = (ws.cell(1, c).value for c in (2, 4, 6, 8))
    if any(o.data_type == "f" for o in ws[1]):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    _kiem_metadata(ma_luot, khau, ma_module, phien_ban)
    ket_qua = []
    for hang in ws.iter_rows(min_row=3):
        ma, _, _, _, _, kq, so, tien_te, loai_dung = (o.value for o in hang)
        if kq is None or kq == "":
            continue
        if kq not in _KET_QUA or any(o.data_type in ("f", "e") for o in hang):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        _chu(ma)
        if loai_dung == "":
            loai_dung = None
        if loai_dung is not None and not re.fullmatch(
                r"[a-z][a-z0-9_]{0,39}", _chu(loai_dung, 40)):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        tien = None
        co_so = so is not None and so != ""
        co_tien_te = tien_te is not None and tien_te != ""
        if co_so or co_tien_te or kq == kieu.KQ_SAI:
            if not co_so or not co_tien_te:
                raise loi("DU_LIEU_KHONG_HOP_LE")
            # Biên Excel: số đã lưu tối đa khoảng 15 chữ số; văn bản giữ đủ độ chính xác.
            if isinstance(so, float):
                so = Decimal(repr(so))
            tien = tien_ra(doc_tien({"so": so, "tien_te": tien_te}))
        ket_qua.append({"ma_luot": ma_luot, "ma": ma, "khau": khau,
                        "ket_qua": kq, "so_tien_sai": tien, "loai_dung": loai_dung})
    return {"phien_ban": 1, "ma_module": ma_module, "ket_qua": ket_qua}


def doc_ds_do_da_ghi(du_lieu: bytes) -> dict:
    """Đọc mẫu của lap_ds_do; không tính công thức, không tự gán tiền tệ."""
    if not isinstance(du_lieu, bytes):
        raise loi("DU_LIEU_KHONG_HOP_LE")
    if len(du_lieu) > _TOI_DA_BYTE:
        raise loi("VUOT_GIOI_HAN")
    try:
        with ZipFile(BytesIO(du_lieu)) as archive:
            ds = archive.infolist()
            if len(ds) > 2000 or sum(t.file_size for t in ds) > 100 * 1048576:
                raise loi("VUOT_GIOI_HAN")
        wb = openpyxl.load_workbook(BytesIO(du_lieu), read_only=True,
                                    data_only=False, keep_links=False)
    except Exception as exc:
        # Lỗi thư viện chỉ được đổi thành câu cố định; không lộ nội dung tệp.
        # Lỗi giới hạn ở bước kiểm ZIP phải giữ nguyên mã.
        if getattr(exc, "ma", None) == "VUOT_GIOI_HAN":
            raise
        raise loi("DU_LIEU_KHONG_HOP_LE") from None
    try:
        return _doc_mau(wb)
    except Exception as exc:
        if getattr(exc, "ma", None) in ("DU_LIEU_KHONG_HOP_LE", "VUOT_GIOI_HAN"):
            raise
        raise loi("DU_LIEU_KHONG_HOP_LE") from None
    finally:
        wb.close()
