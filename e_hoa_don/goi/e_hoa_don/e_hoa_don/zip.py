"""Kiểm kê ZIP trong RAM, bàn giao báo cáo qua cổng SDK."""

from __future__ import annotations

import json
import warnings as canh_bao_python
import zipfile

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.primitives import DataError

from .doc import PHIEN_BAN_ENGINE, _kiem_tran_dong_hang, chieu_truong
from .hoa_don_xml import MAX_ZIP_BYTES, doc_goi_hoa_don_zip, ra_json

ZIP_TOI_DA_BYTE = MAX_ZIP_BYTES
JSON_TOI_DA_BYTE = 32 * 1024 * 1024
CAU_VUOT_TRAN = "Gói ZIP vượt giới hạn xử lý. Anh hãy gửi gói nhỏ hơn."
CAU_KHONG_DOC = "Không kiểm kê được gói ZIP. Anh hãy kiểm tra lại tệp."
_LY_DO = {
    "HD_ZIP_ENTRY_KHONG_DOC_DUOC": "Không đọc đủ tệp hoặc không xác nhận được CRC; chưa có băm và kích thước thực.",
    "HD_ZIP_XML_HONG": "Không đọc được cấu trúc XML hóa đơn.",
    "HD_ZIP_XML_NGOAI_PROFILE": "XML chưa thuộc phạm vi bộ đọc đang hỗ trợ.",
    "HD_ZIP_TEN_KHONG_AN_TOAN": "Tên tệp không an toàn; không đưa nội dung vào bộ đọc XML.",
    "HD_ZIP_SYMLINK": "Liên kết tượng trưng chưa được hỗ trợ.",
    "HD_ZIP_LONG": "Gói ZIP lồng chưa được hỗ trợ.",
    "HD_ZIP_KHONG_HO_TRO": "Định dạng tệp chưa được hỗ trợ; chỉ kiểm kê và băm nội dung.",
}
_BO_QUA = {
    "ZIP_ENTRY_UNSAFE_NAME": "HD_ZIP_TEN_KHONG_AN_TOAN",
    "ZIP_ENTRY_SYMLINK": "HD_ZIP_SYMLINK",
    "ZIP_ENTRY_NESTED_ZIP": "HD_ZIP_LONG",
    "ZIP_ENTRY_IGNORED_NON_XML": "HD_ZIP_KHONG_HO_TRO",
    "ZIP_MEMBER_METHOD_UNSUPPORTED": "HD_ZIP_KHONG_HO_TRO",
}


def _canh_bao_zip_hong(*args, **kwargs):
    # zipfile ở một số bản Python cảnh báo thay vì từ chối overlap.
    # Lõi bắt BadZipFile tại thao tác mở/đọc và giữ entry lỗi, không lộ tên.
    raise zipfile.BadZipFile("Entry ZIP không đọc được.")


def _kiem_xml(raw):
    try:
        _kiem_tran_dong_hang(raw)
    except LoiNghiepVu as loi:
        if loi.ma == "HD_QUA_NHIEU_DONG_HANG":
            raise LoiNghiepVu("HD_ZIP_VUOT_GIOI_HAN", CAU_VUOT_TRAN) from None
        if loi.ma != "HD_XML_NGOAI_PROFILE":
            raise
        # DOCTYPE do bộ đọc strict phân loại; không dựng DTO hóa đơn.


def doc_zip(raw: bytes, *, tep_zip: dict, kiem_huy=None) -> tuple[dict, bytes]:
    """Trả trường tổng hợp + JSON kỹ thuật; tên entry chỉ nằm trong metadata.

    Không dùng artifact_coverage của lõi để suy số tệp đã đọc hoặc đủ kỳ.
    Callback hủy được truyền xuyên suốt; ngoại lệ hủy/lease không bị bọc.
    """
    try:
        with canh_bao_python.catch_warnings():
            canh_bao_python.simplefilter("always", UserWarning)
            canh_bao_python.showwarning = _canh_bao_zip_hong
            goi = doc_goi_hoa_don_zip(raw, contexts=(), kiem_xml=_kiem_xml, kiem_huy=kiem_huy)
    except DataError as loi:
        if loi.code != "ZIP_LIMIT":
            raise
        raise LoiNghiepVu("HD_ZIP_VUOT_GIOI_HAN", CAU_VUOT_TRAN) from None
    if any(i.code == "ZIP_MALFORMED" for i in goi.issues):
        raise LoiNghiepVu("HD_ZIP_KHONG_DOC_DUOC", CAU_KHONG_DOC)
    bam_goi = f"sha256:{goi.container_sha256}"
    files, dirs, da_gap = [], [], {}
    for entry in goi.entries:
        if kiem_huy is not None:
            kiem_huy()
        codes = {i.code for i in entry.issues}
        if "ZIP_ENTRY_DIRECTORY" in codes:
            warnings = [_LY_DO[_BO_QUA[c]] for c in _BO_QUA if c in codes]
            if entry.state == "READ_ERROR":
                warnings.append(_LY_DO["HD_ZIP_ENTRY_KHONG_DOC_DUOC"])
            if "ZIP_DIRECTORY_HAS_DATA" in codes:
                warnings.append("Thư mục có dữ liệu; cần kiểm tra nguồn.")
            if "ZIP_DUPLICATE_ENTRY_NAME" in codes:
                warnings.append("Tên entry trùng sau chuẩn hóa NFC/hoa thường; giữ riêng từng entry.")
            dirs.append({
                "thu_tu": entry.entry_ordinal, "ten": entry.entry_name,
                "trung_ten": "ZIP_DUPLICATE_ENTRY_NAME" in codes,
                "canh_bao": warnings,
            })
            continue
        digest = None if entry.raw_sha256 is None else f"sha256:{entry.raw_sha256}"
        trung = None if digest is None else da_gap.get(digest)
        if digest is not None:
            da_gap.setdefault(digest, entry.entry_ordinal)
        fields, detail, ma = None, None, None
        warnings = []
        if entry.state == "READ_ERROR":
            state, ma = "loi", "HD_ZIP_ENTRY_KHONG_DOC_DUOC"
        elif entry.result is None:
            state = "khong_ho_tro"
            ma = next((_BO_QUA[c] for c in _BO_QUA if c in codes), "HD_ZIP_KHONG_HO_TRO")
        else:
            result = entry.result
            detail = ra_json(result)
            if result.shape == "XML_MALFORMED":
                state, ma = "loi", "HD_ZIP_XML_HONG"
                try:
                    result.raw_xml.decode("utf-8")
                except UnicodeDecodeError:
                    state, ma = "khong_ho_tro", "HD_ZIP_XML_NGOAI_PROFILE"
            elif result.shape != "SUPPORTED_SUBSET":
                state, ma = "khong_ho_tro", "HD_ZIP_XML_NGOAI_PROFILE"
            else:
                state = "doc_duoc"
                fields, van_de = chieu_truong(result, {})
                # Không tạo tep_id của entry. Dùng binding container + ordinal.
                fields.pop("tep_xml")
                fields["nguon"] = {
                    "tep_zip": tep_zip, "bam_goi": bam_goi,
                    "thu_tu": entry.entry_ordinal, "ten": entry.entry_name, "bam": digest,
                }
                detail["van_de_phep_chieu"] = ra_json(van_de)
                warnings.extend(fields["canh_bao"].splitlines())
        if ma is not None:
            warnings.append(_LY_DO[ma])
        if digest is None and ma != "HD_ZIP_ENTRY_KHONG_DOC_DUOC":
            warnings.append(_LY_DO["HD_ZIP_ENTRY_KHONG_DOC_DUOC"])
        if "ZIP_DUPLICATE_ENTRY_NAME" in codes:
            warnings.append("Tên entry trùng sau chuẩn hóa NFC/hoa thường; giữ riêng từng entry.")
        if trung is not None:
            warnings.append("Nội dung trùng với entry trước; giữ nguyên bản này.")
        files.append({
            "thu_tu": entry.entry_ordinal, "ten": entry.entry_name,
            "bam": digest, "kich_thuoc": entry.byte_length,
            "trang_thai_doc": state, "trung_ten": "ZIP_DUPLICATE_ENTRY_NAME" in codes,
            "trung_noi_dung_voi": trung, "ma_loi": ma,
            "canh_bao": warnings, "can_kiem_tra": bool(warnings),
            "truong_hoa_don": fields, "chi_tiet_nguon": detail,
        })
    counts = {"so_tep": len(files)}
    for state, key in (("doc_duoc", "so_doc_duoc"), ("loi", "so_loi"), ("khong_ho_tro", "so_khong_ho_tro")):
        counts[key] = sum(e["trang_thai_doc"] == state for e in files)
    counts["so_trung_noi_dung"] = sum(e["trung_noi_dung_voi"] is not None for e in files)
    doc_het = (bool(files) and counts["so_doc_duoc"] == len(files) and all(e["bam"] for e in files)
               and not any(d["canh_bao"] for d in dirs))
    warnings = [f"Đã đọc {counts['so_doc_duoc']}/{counts['so_tep']} tệp; kết quả cần kiểm tra."]
    if not counts["so_doc_duoc"]:
        warnings.append("Gói không có tệp hóa đơn đọc được.")
    if counts["so_loi"] or counts["so_khong_ho_tro"]:
        warnings.append("Có tệp lỗi/chưa hỗ trợ; xem kiểm kê từng tệp.")
    warnings.append("Chưa xác định độ đủ kỳ tải hoặc trạng thái thuế; chưa ghi nhận nghiệp vụ.")
    report = {
        "phien_ban": 1, "nguon_doc": "zip_xml_strict", "phien_ban_engine": PHIEN_BAN_ENGINE,
        "bam_dau_vao": bam_goi, "tep_zip": tep_zip, "da_doc_het": doc_het,
        **counts, "can_kiem_tra": True, "do_du_ky_tai": "UNKNOWN",
        "native_fiscal_status": "UNKNOWN", "business_promotion": "NOT_PERFORMED",
        "danh_sach_tep": files, "danh_sach_thu_muc": dirs, "canh_bao": warnings,
    }
    # iterencode để dừng ở trần bytes thực, không dựng một chuỗi JSON quá lớn.
    buffer = bytearray()
    encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    for chunk in encoder.iterencode(report):
        data = chunk.encode("utf-8")
        if len(buffer) + len(data) > JSON_TOI_DA_BYTE:
            raise LoiNghiepVu("HD_ZIP_VUOT_GIOI_HAN", CAU_VUOT_TRAN)
        buffer.extend(data)
    if kiem_huy is not None:
        kiem_huy()
    fields = {k: v for k, v in report.items() if k in {
        *counts, "tep_zip", "da_doc_het", "can_kiem_tra", "bam_dau_vao", "nguon_doc", "phien_ban_engine",
    }}
    fields.update(chi_tiet_nguon=None, canh_bao="\n".join(warnings))
    return fields, bytes(buffer)
