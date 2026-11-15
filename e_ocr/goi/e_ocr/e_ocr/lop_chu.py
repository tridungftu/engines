"""Chuyển OCR-NOI từ ma-nguon/lop_chu.py; chỉ đọc chữ PDF, không render/OCR.

Giữ phép kiểm hướng chữ và tọa độ của nguồn. Trang thiếu lớp chữ khiến cả
tài liệu chuyển sang ABBYY, không trả thành công với văn bản thiếu trang.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import io
import math
import warnings

from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

from .bang import doc_bang_trang


MAX_BYTES = 20 * 1024**2
MAX_PAGES = 60
MAX_TEXT = 500_000


@dataclass
class KetQuaLopChu:
    text: str
    warnings: list[str] = field(default_factory=list)
    ocr_pages: int = 0
    pages: list[dict] = field(default_factory=list)


class LoiLopChu(LoiNghiepVu):
    """Mã KHONG_CO_LOP_CHU chỉ báo cần nguồn nhận dạng, không phải tệp hỏng."""


def _khong_huy():
    pass


def _nap_pdfplumber():
    try:
        import pdfplumber
    except ImportError:
        raise LoiNghiepVu(
            "THIEU_THU_VIEN", "Chưa cài đủ thư viện đọc PDF. Hãy liên hệ quản trị viên."
        ) from None
    return pdfplumber


def _kiem_pdf(raw):
    if not raw or not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-1024:]:
        raise LoiNghiepVu("TEP_HONG", "Tệp PDF bị hỏng hoặc chưa ghi xong. Hãy kiểm tra lại tệp.")


def _kiem_so_trang(so_trang):
    if so_trang > MAX_PAGES:
        raise LoiNghiepVu("QUA_SO_TRANG", "Tài liệu vượt 60 trang. Hãy chia thành các tệp nhỏ hơn.")
    if so_trang < 1:
        raise LoiNghiepVu("TEP_HONG", "Tài liệu không có trang đọc được. Hãy kiểm tra lại tệp.")


def dem_trang(raw: bytes, mime: str, *, kiem_huy=_khong_huy) -> int:
    """Kiểm tệp thực và đếm trang trước mọi giao tiếp với Hot Folder."""
    kiem_huy()
    if not raw:
        raise LoiNghiepVu("TEP_HONG", "Tệp rỗng hoặc bị hỏng. Hãy kiểm tra lại tệp.")
    if len(raw) > MAX_BYTES:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Tệp vượt 20 MiB. Hãy chia thành các tệp nhỏ hơn.")
    try:
        if mime == "application/pdf":
            _kiem_pdf(raw)
            with _nap_pdfplumber().open(io.BytesIO(raw)) as pdf:
                so_trang = len(pdf.pages)
                _kiem_so_trang(so_trang)
                # Buộc đọc cấu trúc/luồng từng trang, kể cả khi trang đầu thiếu chữ.
                for trang in pdf.pages:
                    kiem_huy()
                    if not all(math.isfinite(v) and v > 0 for v in (trang.width, trang.height)):
                        raise ValueError
                    _ = trang.chars
                    trang.close()
        elif mime in ("image/png", "image/jpeg"):
            from PIL import Image

            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(raw)) as anh:
                    if anh.format != {"image/png": "PNG", "image/jpeg": "JPEG"}[mime]:
                        raise ValueError
                    so_trang = getattr(anh, "n_frames", 1)
                    _kiem_so_trang(so_trang)
                    if so_trang != 1:
                        raise LoiNghiepVu(
                            "DINH_DANG_KHONG_HO_TRO", "Hãy chuyển ảnh nhiều khung thành PDF trước khi đọc."
                        )
                    anh.verify()
                with Image.open(io.BytesIO(raw)) as anh:
                    anh.load()
        else:
            raise LoiNghiepVu("DINH_DANG_KHONG_HO_TRO", "Chỉ đọc được tệp PDF, PNG hoặc JPEG.")
    except (LoiNghiepVu, ViecDaHuy):
        raise
    except ImportError:
        raise LoiNghiepVu(
            "THIEU_THU_VIEN", "Chưa cài đủ thư viện kiểm tra tệp. Hãy liên hệ quản trị viên."
        ) from None
    except Exception:
        raise LoiNghiepVu(
            "TEP_HONG", "Tệp bị hỏng, có mật khẩu hoặc không đúng định dạng. Hãy kiểm tra lại tệp."
        ) from None
    kiem_huy()
    return so_trang


def _hop(box, origin, size):
    box = [float(box[0]) - origin[0], float(box[1]) - origin[1],
           float(box[2]) - origin[0], float(box[3]) - origin[1]]
    if (not all(math.isfinite(v) for v in (*box, *size))
            or not (0 <= box[0] < box[2] <= size[0] and 0 <= box[1] < box[3] <= size[1])):
        raise ValueError("Vị trí chữ không hợp lệ.")
    return box


def _bbox(item, origin, size):
    return _hop((item["x0"], item["top"], item["x1"], item["bottom"]), origin, size)


def _huong_chu_hop_le(char, rotation):
    """Hoàn tác phép xoay trang; không đoán thứ tự tiền/ngày khi chữ xiên."""
    try:
        a, b, c, d, e, f = map(float, char["matrix"])
        if (not all(math.isfinite(v) for v in (a, b, c, d, e, f))
                or char["upright"] is not (rotation in (0, 180))):
            return False
        x, y = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[rotation]
        a, b, c, d = x * a + y * b, -y * a + x * b, x * c + y * d, -y * c + x * d
        return a > 0 and d > 0 and abs(b) <= 1e-8 * a and abs(c) <= 1e-8 * d
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def _doc_trang(page, pdfplumber, kiem_huy):
    origin = page.bbox[:2]
    size = float(page.width), float(page.height)
    if any(not _huong_chu_hop_le(char, page.rotation) for char in page.chars):
        raise LoiLopChu("KHONG_CO_LOP_CHU", "Lớp chữ chưa đọc được chắc chắn; cần nhận dạng tài liệu.")
    line_dir, char_dir = {0: ("ttb", "ltr"), 90: ("rtl", "ttb"),
                          180: ("btt", "rtl"), 270: ("ltr", "btt")}[page.rotation]
    directions = dict(line_dir=line_dir, char_dir=char_dir,
                      line_dir_rotated=line_dir, char_dir_rotated=char_dir,
                      expand_ligatures=False)
    doan, texts = [], []
    # extract_text_lines/words chỉ đọc ký tự, kể cả chữ ẩn Tr=3 của ABBYY.
    for line in page.extract_text_lines(line_dir_render="ttb", char_dir_render="ltr", **directions):
        kiem_huy()
        if not line["text"].strip():
            continue
        box = _bbox(line, origin, size)
        words = pdfplumber.utils.extract_words(line["chars"], **directions)
        tu = [{"van_ban": w["text"], "hop": _bbox(w, origin, size)} for w in words]
        dong = {"van_ban": line["text"], "hop": box, "tu": tu}
        doan.append({"loai": "doan", "van_ban": line["text"], "hop": box, "dong": [dong]})
        texts.append(line["text"])
    if not texts:
        raise LoiLopChu("KHONG_CO_LOP_CHU", "Tài liệu có trang chưa có lớp chữ; cần nhận dạng tài liệu.")
    bang = doc_bang_trang(
        page, chuyen_hop=lambda box: _hop(box, origin, size),
        huong=directions, kiem_huy=kiem_huy,
    )
    # Toàn văn giữ thứ tự dòng gốc; cấu trúc không lặp đoạn nằm trọn trong bảng.
    doan = [d for d in doan if not any(
        b["hop"][0] <= d["hop"][0] <= d["hop"][2] <= b["hop"][2]
        and b["hop"][1] <= d["hop"][1] <= d["hop"][3] <= b["hop"][3] for b in bang
    )]
    khoi = sorted([*doan, *bang], key=lambda k: (k["hop"][1], k["hop"][0]))
    canh_bao = []
    if page.images and not bang:
        canh_bao.append("PDF có ảnh nền; chưa xác định cấu trúc bảng từ ảnh, cần đối chiếu bản gốc.")
    return ({"so": page.page_number, "rong": size[0], "cao": size[1],
             "don_vi": "pt", "khoi": khoi}, "\n".join(texts), canh_bao)


def doc_lop_chu(raw: bytes, *, kiem_huy=_khong_huy) -> KetQuaLopChu:
    """Giữ nguyên chữ, tiền/ngày; không chuẩn hóa dấu hay OCR lại ảnh nền."""
    kiem_huy()
    _kiem_pdf(raw)
    if len(raw) > MAX_BYTES:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "PDF vượt 20 MiB. Hãy chia thành các tệp nhỏ hơn.")
    pdfplumber = _nap_pdfplumber()
    try:
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            _kiem_so_trang(len(pdf.pages))
            pages, texts, canh_bao, total = [], [], [], 0
            for page in pdf.pages:
                kiem_huy()
                detail, text, warnings_page = _doc_trang(page, pdfplumber, kiem_huy)
                total += len(text) + bool(texts)
                if total > MAX_TEXT:
                    raise LoiNghiepVu("QUA_DO_DAI", "Nội dung vượt giới hạn đọc. Hãy chia nhỏ tài liệu.")
                pages.append(detail)
                texts.append(text)
                canh_bao.extend(warnings_page)
                page.close()
            kiem_huy()
            return KetQuaLopChu(text="\f".join(texts), pages=pages,
                               warnings=list(dict.fromkeys(canh_bao)))
    except (LoiNghiepVu, ViecDaHuy):
        raise
    except Exception:
        raise LoiNghiepVu(
            "TEP_HONG", "Không đọc được đầy đủ PDF; tệp có thể hỏng hoặc có mật khẩu. Hãy kiểm tra lại tệp."
        ) from None
