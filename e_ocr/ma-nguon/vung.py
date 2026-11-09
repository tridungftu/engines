"""OCR-VUNG: cắt bốn điểm bằng Pillow, đọc qua mask_ocr trong gói.

Chuyển thể crop_quad từ mask_ocr/image_layout.py:73; xem NGUON.md.
Không sắp xếp lại điểm, không bù biên hoặc trả ảnh cắt giả khi vùng sai.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import math
import re

from ...sdk_core.primitives import DataError
from .van_ban import MAX_BYTES, _TRUONG_TEP, _id, _nhap_parser_nguon


CAPABILITY = 'ocr.trich_vung@1'
MAX_PIXELS = 20_000_000
MIME_ANH = {'image/png': 'PNG', 'image/jpeg': 'JPEG'}


def crop_quad(image, polygon):
    """Ảnh Pillow; điểm pixel: trên trái, trên phải, dưới phải, dưới trái.

    Kích thước đích giữ phép float32/int của gốc. QUAD nhận thứ tự trên
    trái, dưới trái, dưới phải, trên phải; dùng nội suy BICUBIC của Pillow.
    """
    import numpy as np
    from PIL import Image

    if not isinstance(image, Image.Image) or not 0 < image.width * image.height <= MAX_PIXELS:
        raise DataError('OCR_VUNG_ANH', 'Cần ảnh hợp lệ, tối đa 20 triệu điểm ảnh.')
    try:
        original = np.asarray(polygon)
        if original.shape != (4, 2) or original.dtype.kind not in 'iuf':
            raise ValueError
        if not np.isfinite(original).all():
            raise ValueError
        if (np.any(original < 0) or np.any(original[:, 0] > image.width - 1)
                or np.any(original[:, 1] > image.height - 1)):
            raise DataError('OCR_VUNG_NGOAI_ANH', 'Vùng chọn nằm ngoài ảnh; cần chọn lại trong ảnh.')
        points = original.astype(np.float32)
        # Bốn góc phải tạo tứ giác lồi, không trùng/thẳng hàng/tự cắt.
        edges = np.roll(points, -1, axis=0) - points
        cross = edges[:, 0] * np.roll(edges[:, 1], -1) - edges[:, 1] * np.roll(edges[:, 0], -1)
        if not (np.all(cross > 0) or np.all(cross < 0)):
            raise ValueError
        area = abs(sum(float(points[i, 0]) * float(points[(i + 1) % 4, 1])
                       - float(points[(i + 1) % 4, 0]) * float(points[i, 1]) for i in range(4))) / 2
        if area == 0:
            raise ValueError
        width = max(int(np.linalg.norm(points[0] - points[1])),
                    int(np.linalg.norm(points[2] - points[3])), 2)
        height = max(int(np.linalg.norm(points[0] - points[3])),
                     int(np.linalg.norm(points[1] - points[2])), 2)
        if width * height > MAX_PIXELS:
            raise DataError('OCR_VUNG_QUA_LON', 'Vùng chọn vượt 20 triệu điểm ảnh; cần chọn vùng nhỏ hơn.')
    except DataError:
        raise
    except (ValueError, TypeError, OverflowError):
        raise DataError('OCR_VUNG_DIEM', 'Cần bốn điểm hữu hạn tạo vùng không tự cắt, không suy biến.') from None
    quad = [float(value) for point in points[[0, 3, 2, 1]] for value in point]
    return image.convert('RGB').transform((width, height), Image.Transform.QUAD, quad,
                                          resample=Image.Resampling.BICUBIC)


def kiem_yeu_cau(yeu_cau):
    """Kiểm hình dạng trước khi xin Core mở tệp; không nhận đường dẫn."""
    if (not isinstance(yeu_cau, dict)
            or set(yeu_cau) != {'contract', 'phien_ban', 'tham_chieu_tep', 'bon_diem'}
            or yeu_cau['contract'] != 'vung_anh.v1' or yeu_cau['phien_ban'] != '1.0.0'):
        raise DataError('OCR_VUNG_YEU_CAU', 'Yêu cầu đọc vùng ảnh không hợp lệ.')
    points = yeu_cau['bon_diem']
    if (not isinstance(points, list) or len(points) != 4
            or any(not isinstance(point, list) or len(point) != 2 for point in points)):
        raise DataError('OCR_VUNG_DIEM', 'Cần chọn đúng bốn điểm của vùng ảnh.')
    try:
        if any(type(value) not in (int, float) or not math.isfinite(value)
               for point in points for value in point):
            raise ValueError
    except (ValueError, OverflowError):
        raise DataError('OCR_VUNG_DIEM', 'Tọa độ vùng ảnh phải là số hữu hạn.') from None
    ref = yeu_cau['tham_chieu_tep']
    if (not isinstance(ref, dict) or set(ref) != _TRUONG_TEP
            or ref['contract'] != 'tham_chieu_tep.v1' or ref['phien_ban'] != '1.0.0'):
        raise DataError('OCR_VUNG_NGUON', 'Tham chiếu ảnh không hợp lệ.')
    try:
        _id(ref['tep_id'])
    except DataError:
        raise DataError('OCR_VUNG_NGUON', 'Thông tin nguồn ảnh không hợp lệ.') from None
    if not isinstance(ref['mime'], str) or ref['mime'] not in MIME_ANH:
        raise DataError('OCR_VUNG_DINH_DANG', 'Chỉ đọc vùng trên ảnh PNG hoặc JPEG.')
    ten = ref['ten_tep']
    if (not isinstance(ten, str) or not 1 <= len(ten) <= 255
            or any(c in ten for c in '/\\') or any(ord(c) < 32 for c in ten)):
        raise DataError('OCR_VUNG_NGUON', 'Tên ảnh không hợp lệ.')
    if type(ref['kich_thuoc']) is not int or not 0 < ref['kich_thuoc'] <= MAX_BYTES:
        raise DataError('OCR_VUNG_NGUON', 'Ảnh phải có dung lượng lớn hơn không, tối đa 20 MiB.')
    if not isinstance(ref['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', ref['sha256']):
        raise DataError('OCR_VUNG_NGUON', 'Thông tin xác minh ảnh không hợp lệ.')
    if ref['het_han_luc'] is not None:
        try:
            if not isinstance(ref['het_han_luc'], str) or not re.fullmatch(
                    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', ref['het_han_luc']):
                raise ValueError
            moc = datetime.fromisoformat(ref['het_han_luc'].replace('Z', '+00:00'))
        except ValueError:
            raise DataError('OCR_VUNG_NGUON', 'Thời hạn sử dụng ảnh không hợp lệ.') from None
        if moc <= datetime.now(timezone.utc):
            raise DataError('OCR_VUNG_HET_HAN', 'Tham chiếu ảnh đã hết hạn sử dụng.')


def trich_vung(raw: bytes, yeu_cau: dict, *, revision: int = 1, image_text=None) -> dict:
    """Bytes ảnh do Core cấp; seam image_text là đúng hàm mask_ocr nguồn.

    Hàm nguồn chỉ trả str, chưa có confidence. Luôn cần soát khi chưa có
    độ tin cậy; ảnh không có chữ trả cờ vùng rỗng, không được coi là lỗi OCR.
    """
    from PIL import Image

    request = deepcopy(yeu_cau)
    kiem_yeu_cau(request)
    ref = request['tham_chieu_tep']
    if type(revision) is not int or revision < 1:
        raise DataError('OCR_VUNG_LAN_SUA', 'Lần sửa kết quả phải là số nguyên dương.')
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES:
        raise DataError('OCR_VUNG_ANH', 'Cần nội dung ảnh không rỗng, tối đa 20 MiB.')
    if len(raw) != ref['kich_thuoc'] or hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise DataError('OCR_VUNG_NGUON', 'Nội dung ảnh không khớp nguồn được cấp.')
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != MIME_ANH[ref['mime']] or getattr(image, 'n_frames', 1) != 1:
                raise DataError('OCR_VUNG_DINH_DANG', 'Nội dung ảnh không khớp định dạng hoặc có nhiều khung hình.')
            if image.width * image.height > MAX_PIXELS:
                raise DataError('OCR_VUNG_ANH', 'Ảnh vượt 20 triệu điểm ảnh; cần giảm kích thước ảnh.')
            # Kiểm vùng trước chuyển màu/giải nén toàn ảnh và trước OCR.
            crop = crop_quad(image, request['bon_diem'])
            with io.BytesIO() as stream:
                crop.convert('RGB').save(stream, format='PNG')
                png = stream.getvalue()
    except DataError:
        raise
    except (OSError, ValueError, Image.DecompressionBombError):
        raise DataError('OCR_VUNG_ANH', 'Không đọc được ảnh; cần kiểm tra hoặc xuất lại ảnh PNG, JPEG.') from None
    if image_text is None:
        try:
            extraction, _ = _nhap_parser_nguon()
            image_text = extraction.image_text
        except ImportError:
            raise DataError('OCR_VUNG_CHUA_SAN_SANG', 'Bộ nhận dạng ảnh chưa sẵn sàng; cần kiểm tra môi trường xử lý.') from None
    if not callable(image_text):
        raise TypeError('Cần hàm đọc ảnh nguồn trong gói.')
    try:
        text = image_text(png)
        if not isinstance(text, str) or len(text) > 500_000:
            raise ValueError
    except Exception:
        raise DataError('OCR_VUNG_KHONG_DOC_DUOC', 'Không nhận dạng được vùng ảnh; cần kiểm tra bộ nhận dạng và ảnh nguồn.') from None
    rong = not text.strip()
    reasons = ['chua_co_do_tin_cay'] + (['vung_rong'] if rong else [])
    return {
        'contract': 'van_ban_vung.v1', 'phien_ban': '1.0.0', 'revision': revision,
        'nguon_tep_ids': [ref['tep_id']], 'van_ban': text,
        'bon_diem': deepcopy(request['bon_diem']),
        'kich_thuoc_vung': {'rong': crop.width, 'cao': crop.height},
        'nguon_doc': 'mask_ocr_tesseract', 'do_tin_cay': None,
        'nghi_ngo': True, 'vung_rong': rong, 'ly_do_nghi_ngo': reasons,
        'canh_bao': ['Chưa có độ tin cậy nhận dạng; cần kiểm tra nội dung đọc được.']
                    + (['Vùng chọn không đọc được chữ; cần kiểm tra lại ảnh và vùng chọn.'] if rong else []),
    }
