"""Chuyển lõi ma-nguon/van_ban.py sang phong bì SDK 2.0, dùng chung hai action.

Bỏ tham chiếu/UUID, parser DOCX và cổng lib.cong_ocr cũ. PDF có chữ được
đọc trực tiếp; nguồn ABBYY chỉ trả PDF lớp chữ, không OCR lại ảnh nền.
"""

import hashlib

from .cau_hinh_may import doc_cau_hinh
from .chon_nguon import doc_theo_nguon
from .lop_chu import MAX_BYTES, LoiLopChu, dem_trang, doc_lop_chu


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
    ly_do = None
    if ket_qua is None:
        cau_hinh = doc_cau_hinh(bat_buoc=False) or {}
        chon = doc_theo_nguon(raw, tep["mime"], so_trang, viec=viec, cau_hinh=cau_hinh)
        ket_qua, nguon_doc, ly_do = chon.ket_qua, chon.nguon_doc, chon.ly_do_chuyen_nguon
    viec.tien_do(95, "Đang hoàn tất văn bản và vị trí trang.")
    du_lieu = {
        "phien_ban": 1, "van_ban": ket_qua.text, "trang": ket_qua.pages,
        "nguon_doc": nguon_doc, "ly_do_chuyen_nguon": ly_do, "so_trang": so_trang,
        "phien_ban_engine": phien_ban_engine, "bam_dau_vao": bam,
        "canh_bao": ket_qua.warnings,
    }
    viec.tien_do(100, "Đã đọc xong tài liệu.")
    return du_lieu
