"""Chuyển có sửa hàm thuần build_structure/vi_tri từ vendor/review/cau_truc.

Giữ Điều/Khoản; dùng khoảng Unicode trong toàn văn thay bản cắt/strip hoặc
top-k. Vị trí OCR/DOCX gốc được giữ riêng nguyên vẹn trong hồ sơ hậu kiểm.
"""

from io import BytesIO
import json
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .tham_so import BAM, loi


KHOAN = re.compile(r"^(\d+(?:\.\d+)+)\.?\s+(.*)$")
DIEU = re.compile(r"^Điều\s+(\d+)\s*[.:]?\s*(.*)$", re.IGNORECASE)
TAI_LIEU_TOI_DA_BYTE = 20 * 1024 * 1024
TRANG_TOI_DA = 2_000
TRANG_TOI_DA_BYTE = 8 * 1024 * 1024
CANH_BAO_TOI_DA = 200
CANH_BAO_TOI_DA_BYTE = 64 * 1024


def json_bytes_co_tran(v, tran_byte):
    """JSON canonical trong RAM; dừng trước khi ghép phong bì quá trần."""
    encoder = json.JSONEncoder(ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False)
    with BytesIO() as bo_nho:
        for phan in encoder.iterencode(v):
            con = tran_byte - bo_nho.tell()
            if len(phan) > con:  # UTF-8 không thể ít byte hơn số ký tự.
                loi("VUOT_GIOI_HAN")
            raw = phan.encode("utf-8")
            if len(raw) > con:
                loi("VUOT_GIOI_HAN")
            bo_nho.write(raw)
        return bo_nho.getvalue()


def doc_tai_lieu(dau_vao):
    v = dau_vao.get("van_ban_tai_lieu")
    can = {"phien_ban", "van_ban", "trang", "nguon_doc", "ly_do_chuyen_nguon",
           "so_trang", "phien_ban_engine", "bam_dau_vao", "canh_bao"}
    if (not isinstance(v, dict) or not can <= v.keys()
            or type(v["phien_ban"]) is not int or v["phien_ban"] != 1
            or not isinstance(v["van_ban"], str)
            or not isinstance(v["trang"], list)
            or type(v["so_trang"]) is not int or v["so_trang"] < 0
            or v["nguon_doc"] not in ("abbyy", "tesseract", "lop_chu_san", "docx")
            or not isinstance(v["bam_dau_vao"], str) or not BAM.fullmatch(v["bam_dau_vao"])
            or not isinstance(v["phien_ban_engine"], str) or not v["phien_ban_engine"].strip()
            or not (v["ly_do_chuyen_nguon"] is None or isinstance(v["ly_do_chuyen_nguon"], str))
            or not isinstance(v["canh_bao"], list)
            or not all(isinstance(c, str) for c in v["canh_bao"])):
        raise LoiNghiepVu("DAU_VAO_KHONG_HOP_LE", "Văn bản tài liệu không đúng cấu trúc phiên bản 1.")
    if len(v["van_ban"]) > 500_000:
        loi("VUOT_GIOI_HAN")
    if len(v["trang"]) > TRANG_TOI_DA or len(v["canh_bao"]) > CANH_BAO_TOI_DA:
        loi("VUOT_GIOI_HAN")
    try:
        json_bytes_co_tran(v["trang"], TRANG_TOI_DA_BYTE)
        json_bytes_co_tran(v["canh_bao"], CANH_BAO_TOI_DA_BYTE)
        json_bytes_co_tran(v, TAI_LIEU_TOI_DA_BYTE)
    except (ValueError, TypeError, RecursionError, OverflowError, UnicodeError):
        raise LoiNghiepVu("DAU_VAO_KHONG_HOP_LE", "Văn bản tài liệu không đúng cấu trúc phiên bản 1.") from None
    return v


def vi_tri(dieu, khoan):
    if not dieu:
        return "Phần mở đầu"
    return "Điều " + dieu + (f" – Khoản {khoan}" if khoan else "")


def build_structure(van_ban, kiem_huy):
    """Chỉ lập chỉ mục; mọi ký tự vẫn thuộc đúng một khoảng, không bịa trang."""
    moc = [(0, "Phần mở đầu")]
    dieu = ""
    for dong in re.finditer(r"[^\n\f]+", van_ban):
        kiem_huy()
        text = dong.group().strip()
        d, k = DIEU.fullmatch(text), KHOAN.fullmatch(text)
        if d:
            dieu = d[1]
        elif not (k and dieu and k[1].split(".")[0] == dieu):
            continue
        nhan = vi_tri(dieu, "" if d else k[1])
        if dong.start() == 0:
            moc[0] = (0, nhan)
        else:
            moc.append((dong.start(), nhan))
    return [{"id": f"R{i + 1:03d}", "nhan": nhan, "bat_dau": dau,
             "ket_thuc": moc[i + 1][0] if i + 1 < len(moc) else len(van_ban)}
            for i, (dau, nhan) in enumerate(moc)]
