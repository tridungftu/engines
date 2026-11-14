"""Chuyển quy tắc bảo toàn ô từ ma-nguon/bang.py sang schema SDK 2.0.

OCR-1 chỉ đọc đường kẻ và ký tự sẵn có trong PDF; không suy bảng từ text
hoặc OCR ảnh nền. Parser DOCX/xuất Word thuộc OCR-3, chưa chép vendor vào đây.
"""

from kho_tri_thuc_sdk.engine import LoiNghiepVu


def doc_bang_trang(page, *, chuyen_hop, huong, kiem_huy):
    """Giữ ô rỗng/ô gộp ở ô gốc; từ chối bảng quá trần hoặc không đầy đủ."""
    import pdfplumber

    ket_qua = []
    for bang in page.find_tables({"vertical_strategy": "lines", "horizontal_strategy": "lines"}):
        kiem_huy()
        xs = sorted({v for cell in bang.cells for v in (cell[0], cell[2])})
        ys = sorted({v for cell in bang.cells for v in (cell[1], cell[3])})
        rows, cols = len(ys) - 1, len(xs) - 1
        if not 1 <= rows <= 100 or not 1 <= cols <= 40:
            raise LoiNghiepVu("BANG_QUA_LON", "Bảng vượt 100 hàng hoặc 40 cột. Hãy chia nhỏ tài liệu.")
        cells, occupied = [], set()
        for cell in sorted(bang.cells, key=lambda c: (c[1], c[0])):
            kiem_huy()
            r, c = ys.index(cell[1]), xs.index(cell[0])
            rs, cs = ys.index(cell[3]) - r, xs.index(cell[2]) - c
            covered = {(y, x) for y in range(r, r + rs) for x in range(c, c + cs)}
            if not covered or occupied & covered:
                raise LoiNghiepVu("BANG_KHONG_DAY_DU", "Không đọc được đầy đủ cấu trúc bảng. Hãy kiểm tra bản gốc.")
            occupied.update(covered)
            chars = [ch for ch in page.chars if
                     cell[0] <= (ch["x0"] + ch["x1"]) / 2 < cell[2]
                     and cell[1] <= (ch["top"] + ch["bottom"]) / 2 < cell[3]]
            text = pdfplumber.utils.extract_text(chars, **huong) if chars else ""
            cells.append({"hang": r, "cot": c, "gop_hang": rs, "gop_cot": cs,
                          "van_ban": text, "hop": chuyen_hop(cell)})
        if len(occupied) != rows * cols:
            raise LoiNghiepVu("BANG_KHONG_DAY_DU", "Không đọc được đầy đủ cấu trúc bảng. Hãy kiểm tra bản gốc.")
        ket_qua.append({"loai": "bang", "hop": chuyen_hop(bang.bbox), "o": cells})
    return ket_qua
