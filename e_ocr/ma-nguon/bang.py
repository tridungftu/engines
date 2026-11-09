"""OCR-3: bọc bảng DOCX nguồn thành du_lieu_bang.v1, không suy bảng từ text.

CD-036: dùng nguyên extract_docx / word_layout của local-mask-ocr 2.1.0
đã ghim trong vendor.mask_ocr của chính gói; nguồn và SHA tại NGUON.md.
Không đọc thư mục công cụ cũ hoặc đổi trạng thái import toàn cục.

Đầu vào là DOCX do Core cấp (có thể là kết quả OCR-2), không gọi HotFolder
lần nữa. Core lưu phan_hoi_nguon vào ID riêng trước công bố/ACK. Tọa độ
dàn dòng/trang logic của nguồn chỉ giữ trong phản hồi, không giả trang vật lý.
Giữ giới hạn nguồn 100 hàng/40 cột; lỗi thì từ chối, không cắt bảng.
Từ chối cấu trúc ô bọc ngoài paragraph và gridAfter khác 0 mà parser
nguồn chưa bảo toàn; không công bố bảng thiếu như kết quả thành công.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib
import io
import re
from uuid import UUID
import zipfile

from ...sdk_core.primitives import DataError


MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
CANH_BAO_VI_TRI = "DOCX chỉ có định vị logic; không xác định trang hoặc tọa độ vật lý."
_TRUONG_TEP = {"contract", "phien_ban", "tep_id", "ten_tep", "mime",
               "kich_thuoc", "sha256", "het_han_luc"}


@dataclass(frozen=True, repr=False)
class KetQuaBang:
    bang: dict
    phan_hoi_nguon: dict


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", value,
    ):
        raise DataError("OCR_ID_INVALID", "Cần UUID tệp do Core cấp.")
    return UUID(value)


def _nhap_parser_nguon():
    """Chỉ nạp parser đã ghim trong gói; thiếu nguồn/dependency thì báo lỗi."""
    return (importlib.import_module(".vendor.mask_ocr.extraction", __package__).extract_docx,
            importlib.import_module(".vendor.mask_ocr.layout", __package__).word_layout)


def _kiem_cau_truc_chua_ho_tro(raw):
    """Chỉ chặn hình dạng nguồn chưa đọc đủ, không tự phân tích/bù bảng.

    Chạy sau extract_docx đã kiểm giới hạn ZIP/XML; dùng cùng defusedxml
    có sẵn trong runtime OCR. Kiểm cả phần phụ mà word_layout đọc.
    """
    from defusedxml import ElementTree as ET

    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for name in archive.namelist():
            if name != "word/document.xml" and not re.fullmatch(
                r"word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml", name,
            ):
                continue
            root = ET.fromstring(archive.read(name))
            for cell in root.iter(w + "tc"):
                # word_layout chỉ đọc paragraph trực tiếp trong ô. Wrapper
                # (như sdt) có thể chứa toàn bộ hoặc một phần giá trị bị mất.
                if any(child.tag not in {w + "tcPr", w + "p"} for child in cell):
                    raise ValueError("Parser nguồn chưa hỗ trợ cấu trúc trong ô.")
            for after in root.findall(".//" + w + "trPr/" + w + "gridAfter"):
                if int(after.get(w + "val", "0")) != 0:
                    raise ValueError("Parser nguồn chưa bảo toàn gridAfter.")


def trich_bang(
    raw: bytes, tham_chieu_tep: dict, *, phan_hoi_nguon_tep_id: str,
    revision: int = 1, nguon_tep_ids=(), extract_docx=None, word_layout=None,
) -> KetQuaBang:
    """Đọc DOCX đã được Core kiểm quyền; không OCR ảnh nhúng/hiệu đính.

    nguon_tep_ids có thể chứa ID PDF/ảnh gốc từ OCR-2. Không suy kiểu dữ
    liệu, đơn vị hay tiêu đề từ hàng đầu: giữ tất cả hàng như nguồn.
    Hai seam tùy chọn dành cho hàm parser nguồn trong test/đóng gói.
    """
    ref = deepcopy(tham_chieu_tep)
    if type(revision) is not int or revision < 1:
        raise DataError("OCR_REVISION_INVALID", "Revision phải là số nguyên dương.")
    if not isinstance(ref, dict) or set(ref) != _TRUONG_TEP or (
        ref["contract"] != "tham_chieu_tep.v1" or ref["phien_ban"] != "1.0.0"
        or ref["mime"] != MIME_DOCX
    ):
        raise DataError("OCR_THAM_CHIEU_INVALID", "Cần tham chiếu tệp DOCX đúng contract.")
    tep_id, detail_id = _id(ref["tep_id"]), _id(phan_hoi_nguon_tep_id)
    if not isinstance(nguon_tep_ids, (list, tuple)):
        raise DataError("OCR_ID_INVALID", "Cần danh sách ID nguồn.")
    ids = list(nguon_tep_ids)
    parsed = [_id(value) for value in ids]
    if tep_id == detail_id or detail_id in parsed:
        raise DataError("OCR_FILE_REF_CONFLICT", "DOCX/nguồn và phản hồi cần tệp riêng.")
    ten = ref["ten_tep"]
    if not isinstance(ten, str) or not 1 <= len(ten) <= 255 or (
        any(c in ten for c in "/\\") or any(ord(c) < 32 for c in ten)
    ):
        raise DataError("OCR_TEN_TEP_INVALID", "Tên tệp không hợp lệ.")
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 20 * 1024**2:
        raise DataError("OCR_KICH_THUOC", "Cần bytes DOCX không rỗng, tối đa 20 MiB.")
    if type(ref["kich_thuoc"]) is not int or ref["kich_thuoc"] != len(raw) or (
        ref["sha256"] != hashlib.sha256(raw).hexdigest()
    ):
        raise DataError("OCR_NGUON_KHONG_KHOP", "Hash hoặc kích thước không khớp nguồn.")
    if ref["het_han_luc"] is not None:
        try:
            value = ref["het_han_luc"]
            if not isinstance(value, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value,
            ):
                raise ValueError
            moc = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise DataError("OCR_HET_HAN_INVALID", "Thời hạn tham chiếu không hợp lệ.") from None
        if moc <= datetime.now(timezone.utc):
            raise DataError("OCR_THAM_CHIEU_HET_HAN", "Tham chiếu tệp đã hết hạn.")
    if extract_docx is None or word_layout is None:
        extraction, layout = _nhap_parser_nguon()
        extract_docx = extraction if extract_docx is None else extract_docx
        word_layout = layout if word_layout is None else word_layout
    if not callable(extract_docx) or not callable(word_layout):
        raise TypeError("Cần hai hàm parser DOCX nguồn.")
    try:
        legacy = extract_docx(raw, image_reader=lambda _data: "")
        _kiem_cau_truc_chua_ho_tro(raw)
        layout = word_layout(raw, legacy, embedded_pages=[])
        warnings = list(layout["warnings"])
        if any(not isinstance(w, str) or not w for w in warnings):
            raise ValueError
        warnings = list(dict.fromkeys([*warnings, CANH_BAO_VI_TRI]))
        if legacy.ocr_pages:
            warnings.append("Ảnh nhúng DOCX chưa được nhận dạng; cần đối chiếu ảnh gốc.")
        units = {}
        for unit in layout["units"]:
            uid = unit["id"]
            if not isinstance(uid, str) or not uid or uid in units or not isinstance(unit["text"], str):
                raise ValueError
            units[uid] = unit["text"]
        tables = []
        for index, block in enumerate(layout["blocks"]):
            if block["type"] != "table":
                continue
            rows, cols = block["rows"], block["cols"]
            if type(rows) is not int or not 0 <= rows <= 100 or (
                type(cols) is not int or not 1 <= cols <= 40
            ):
                raise ValueError
            locator = f"word_layout/blocks/{index}"
            cells, occupied = [], set()
            for cell in block["cells"]:
                r, c, rs, cs = (cell[k] for k in ("row", "col", "rowspan", "colspan"))
                if any(type(v) is not int for v in (r, c, rs, cs)) or (
                    min(r, c) < 0 or min(rs, cs) < 1 or r + rs > rows or c + cs > cols
                ):
                    raise ValueError
                covered = {(y, x) for y in range(r, r + rs) for x in range(c, c + cs)}
                if occupied & covered:
                    raise ValueError
                occupied.update(covered)
                uids = cell["unit_ids"]
                if not isinstance(uids, list) or len(set(uids)) != len(uids):
                    raise ValueError
                cells.append({
                    "dong": r, "cot": c, "gop_dong": rs, "gop_cot": cs,
                    "gia_tri": {"kieu": "van_ban", "gia_tri": "\n".join(units[u] for u in uids)},
                    "vi_tri": {"tep_id": ref["tep_id"], "dinh_vi": f"{locator}/row/{r}/col/{c}"},
                    "ma_vung_nguon": list(uids),
                })
            tables.append({
                "ma": f"bang_{len(tables)}",
                "cot": [{"ma": f"cot_{c}", "ten": f"Cột {c + 1}", "kieu": "van_ban", "don_vi": None}
                        for c in range(cols)],
                "so_dong": rows, "o": cells,
                "vi_tri": {"tep_id": ref["tep_id"], "dinh_vi": locator},
                "can_soat": True, "canh_bao": list(warnings),
            })
    except Exception:
        raise DataError("OCR_BANG_DOCX_INVALID", "Không đọc được đầy đủ bảng DOCX; cần kiểm tra cấu trúc/giới hạn nguồn.") from None
    # Không đổi biểu diễn ID Core cấp; chống trùng theo giá trị UUID.
    sources, seen = [], set()
    for value in [*ids, ref["tep_id"]]:
        parsed_id = _id(value)
        if parsed_id not in seen:
            sources.append(value)
            seen.add(parsed_id)
    return KetQuaBang(
        bang={"contract": "du_lieu_bang.v1", "phien_ban": "1.0.0", "revision": revision,
              "nguon_tep_ids": sources, "bang": tables,
              "phan_hoi_nguon_tep_id": phan_hoi_nguon_tep_id},
        phan_hoi_nguon={"tham_chieu_tep": ref, "revision": revision,
                        "layout": deepcopy(layout), "canh_bao": warnings},
    )
