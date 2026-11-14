"""Chuyển lõi ma-nguon/van_ban.py sang phong bì SDK 2.0, dùng chung hai action.

Bỏ tham chiếu/UUID, parser DOCX và cổng lib.cong_ocr cũ. PDF có chữ được
đọc trực tiếp; nguồn ABBYY chỉ trả PDF lớp chữ, không OCR lại ảnh nền.
"""

import hashlib

from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .abbyy import BackendABBYY
from .cau_hinh_may import doc_cau_hinh
from .lop_chu import MAX_BYTES, LoiLopChu, dem_trang, doc_lop_chu


MIME_DUOI = {"application/pdf": "pdf", "image/png": "png", "image/jpeg": "jpg"}


def trich_van_ban(viec, *, phien_ban_engine):
    tep = viec.dau_vao["tep"]
    viec.tien_do(5, "Đang đọc tệp tài liệu.")
    with viec.mo_tep(tep["tep_id"]) as f:
        raw = f.read(MAX_BYTES + 1)
    viec.tien_do(15, "Đang kiểm tra tệp và đếm trang.")
    so_trang = dem_trang(raw, tep["mime"], kiem_huy=viec.kiem_huy)
    bam = "sha256:" + hashlib.sha256(raw).hexdigest()
    ket_qua = None
    if tep["mime"] == "application/pdf":
        viec.tien_do(25, "Đang đọc lớp chữ có sẵn trong PDF.")
        try:
            ket_qua = doc_lop_chu(raw, kiem_huy=viec.kiem_huy)
        except LoiLopChu as exc:
            if exc.ma != "KHONG_CO_LOP_CHU":
                raise
    nguon_doc = "lop_chu_san"
    if ket_qua is None:
        if viec.tham_so.get("nguon") == "chi_tesseract":
            raise LoiNghiepVu("CHUA_LAM", "Nguồn Tesseract chưa được triển khai ở phiên bản này.")
        cau_hinh = doc_cau_hinh(bat_buoc=True)
        backend = BackendABBYY(cau_hinh["abbyy"])
        pdf = backend.doc_pdf(raw, MIME_DUOI[tep["mime"]], viec=viec)
        viec.tien_do(75, "Đã nhận kết quả ABBYY; đang đọc lớp chữ.")
        try:
            ket_qua = doc_lop_chu(pdf, kiem_huy=viec.kiem_huy)
        except LoiLopChu:
            raise LoiNghiepVu(
                "ABBYY_THIEU_LOP_CHU", "Kết quả ABBYY chưa có lớp chữ đầy đủ. Hãy kiểm tra cấu hình xuất PDF."
            ) from None
        if len(ket_qua.pages) != so_trang:
            raise LoiNghiepVu(
                "KET_QUA_KHONG_KHOP", "Số trang kết quả ABBYY không khớp tài liệu gốc. Hãy kiểm tra lại nguồn nhận dạng."
            )
        nguon_doc = "abbyy"
    viec.tien_do(95, "Đang hoàn tất văn bản và vị trí trang.")
    du_lieu = {
        "phien_ban": 1, "van_ban": ket_qua.text, "trang": ket_qua.pages,
        "nguon_doc": nguon_doc, "ly_do_chuyen_nguon": None, "so_trang": so_trang,
        "phien_ban_engine": phien_ban_engine, "bam_dau_vao": bam,
        "canh_bao": ket_qua.warnings,
    }
    viec.tien_do(100, "Đã đọc xong tài liệu.")
    return du_lieu
