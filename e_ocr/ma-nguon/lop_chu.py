"""OCR-NOI: đọc PDF lớp chữ ABBYY, không nhận dạng lại ảnh nền.

QD-TAM-20261106-12: pdfplumber đã có, import lười. Kết quả cùng cấu trúc
Extracted và layout mask_ocr: pages → blocks/unit_ids → units → parts.
Tọa độ là point, gốc trái trên MediaBox hiển thị, đã tính phép xoay PDF.
Nguồn ABBYY chỉ là nguồn đọc; không tự cấp provenance/ACK của Core.
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass, field



MAX_BYTES = 20 * 1024**2
MAX_PAGES = 60
MAX_TEXT = 500_000


@dataclass
class KetQuaLopChu:
    """Cùng bốn trường Extracted; không import package vendor nạp pymupdf."""

    text: str
    warnings: list[str] = field(default_factory=list)
    ocr_pages: int = 0
    pages: list[dict] = field(default_factory=list)


class LoiLopChu(ValueError):
    """ma dành cho lớp chọn nguồn; thông báo dành cho người dùng."""

    def __init__(self, ma, thong_bao):
        self.ma = ma
        super().__init__(thong_bao)


def _kiem_huy(huy):
    if huy is not None and huy.is_set():
        raise LoiLopChu('OCR_HUY', 'Đã hủy đọc lớp chữ tài liệu.')


def _bbox(item, origin, size):
    box = [float(item['x0']) - origin[0], float(item['top']) - origin[1],
           float(item['x1']) - origin[0], float(item['bottom']) - origin[1]]
    if (not all(math.isfinite(v) for v in (*box, *size))
            or not (0 <= box[0] < box[2] <= size[0] and 0 <= box[1] < box[3] <= size[1])):
        raise ValueError('Vị trí chữ không hợp lệ.')
    return box


def _huong_chu_hop_le(char, rotation):
    """Chỉ nhận chữ thẳng sau khi hoàn tác phép xoay trang.

    upright vẫn True với chữ xoay 180 độ; phải kiểm cả ma trận từng ký tự.
    Ma trận không đủ tin cậy cũng chuyển nguồn, không đoán thứ tự tiền/ngày.
    """
    try:
        a, b, c, d, e, f = map(float, char['matrix'])
        if (not all(math.isfinite(v) for v in (a, b, c, d, e, f))
                or char['upright'] is not (rotation in (0, 180))):
            return False
        x, y = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[rotation]
        a, b, c, d = x * a + y * b, -y * a + x * b, x * c + y * d, -y * c + x * d
        return (a > 0 and d > 0 and abs(b) <= 1e-8 * a and abs(c) <= 1e-8 * d)
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def _doc_trang(page, pdfplumber):
    number = page.page_number
    origin = page.bbox[:2]
    size = (float(page.width), float(page.height))
    if any(not _huong_chu_hop_le(char, page.rotation) for char in page.chars):
        raise LoiLopChu('OCR_PDF_KHONG_LOP_CHU',
                       f'Trang {number} có hướng chữ chưa đọc được chắc chắn; cần chuyển nguồn nhận dạng.')
    result = dict(number=number, width=size[0], height=size[1],
                  mode='native', source='ABBYY', text='', units=[], blocks=[],
                  issues=[], warnings=[], margins=dict(left=0, right=0, top=0, bottom=0))
    line_dir, char_dir = {0: ('ttb', 'ltr'), 90: ('rtl', 'ttb'),
                          180: ('btt', 'rtl'), 270: ('ltr', 'btt')}[page.rotation]
    directions = dict(line_dir=line_dir, char_dir=char_dir,
                      line_dir_rotated=line_dir, char_dir_rotated=char_dir,
                      expand_ligatures=False)
    # Chỉ đọc ký tự PDF. Không render, gọi extract_pdf legacy hoặc worker OCR.
    # Không chuẩn hóa dấu, tiền/ngày hay tự mở rộng các ký tự ligature.
    # Hướng nhóm chữ theo phép xoay, chuỗi xuất vẫn theo thứ tự đọc ban đầu.
    for line in page.extract_text_lines(line_dir_render='ttb', char_dir_render='ltr', **directions):
        if not line['text'].strip():
            continue
        uid = f'p{number}-u{len(result["units"])}'
        box = _bbox(line, origin, size)
        words = pdfplumber.utils.extract_words(line['chars'], **directions)
        parts = [dict(id=f'{uid}-w{i}', text=word['text'], bbox=_bbox(word, origin, size), source='ABBYY')
                 for i, word in enumerate(words)]
        char = line['chars'][0]
        font = char.get('fontname', '').lower()
        style = dict(size=float(char['size']), bold='bold' in font,
                     italic='italic' in font or 'oblique' in font)
        result['units'].append(dict(id=uid, bbox=box, text=line['text'], parts=parts,
                                    runs=[dict(text=line['text'], **style)],
                                    style=dict(align='left', **style), source='ABBYY'))
        result['blocks'].append(dict(type='paragraph', bbox=list(box), unit_ids=[uid], source='ABBYY'))
    result['text'] = '\n'.join(unit['text'] for unit in result['units'])
    return result


def doc_lop_chu(raw: bytes, *, huy=None) -> KetQuaLopChu:
    """Đọc bytes PDF kết quả ABBYY do Core cấp; mọi thao tác trong RAM.

    Không gọi ABBYY hoặc OCR dự phòng. Bất kỳ trang nào thiếu lớp chữ đều
    báo OCR_PDF_KHONG_LOP_CHU để lớp chọn nguồn chuyển mask_ocr; không trả
    thành công với tài liệu chỉ đọc được một phần. Không thử lại hay thay
    đổi sổ hạn mức. Giới hạn giữ cùng mức với parser mask_ocr.
    """
    if not isinstance(raw, bytes) or not raw:
        raise LoiLopChu('OCR_PDF_DAU_VAO', 'Cần nội dung PDF không rỗng để đọc lớp chữ.')
    if len(raw) > MAX_BYTES:
        raise LoiLopChu('OCR_PDF_GIOI_HAN', 'PDF vượt giới hạn dung lượng; cần chia nhỏ tài liệu.')
    _kiem_huy(huy)
    pdfplumber = None
    try:
        import pdfplumber
    except ImportError:
        pass
    if pdfplumber is None:
        raise LoiLopChu('OCR_LOP_CHU_THIEU_THU_VIEN',
                       'Chưa thể đọc lớp chữ PDF; cần kiểm tra môi trường xử lý.')
    try:
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            if not 0 < len(pdf.pages) <= MAX_PAGES:
                raise LoiLopChu('OCR_PDF_GIOI_HAN',
                               'PDF không có trang hoặc vượt giới hạn số trang; cần chia nhỏ tài liệu.')
            pages, texts, total = [], [], 0
            for page in pdf.pages:
                _kiem_huy(huy)
                detail = _doc_trang(page, pdfplumber)
                _kiem_huy(huy)
                if not detail['units']:
                    raise LoiLopChu('OCR_PDF_KHONG_LOP_CHU',
                                   f'Trang {page.page_number} không có lớp chữ đọc được; cần chuyển nguồn nhận dạng.')
                text = f'[Trang {page.page_number}]\n{detail["text"]}'
                total += len(text) + (2 if texts else 0)
                if total > MAX_TEXT:
                    raise LoiLopChu('OCR_PDF_GIOI_HAN', 'Nội dung quá dài; cần chia nhỏ tài liệu.')
                pages.append(detail)
                texts.append(text)
                page.close()
            return KetQuaLopChu(text='\n\n'.join(texts), warnings=[], ocr_pages=0, pages=pages)
    except LoiLopChu:
        raise
    except Exception:
        pass
    # Ngoài except để không giữ exception parser chứa nội dung/đường dẫn nguồn.
    raise LoiLopChu('OCR_PDF_KHONG_HOP_LE',
                   'Không đọc được PDF; tệp có thể hỏng hoặc có mật khẩu. Cần kiểm tra tài liệu.')
