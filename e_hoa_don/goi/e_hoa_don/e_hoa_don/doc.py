"""Chiếu DTO strict sang trường SDK, không cấp định danh hay nhận nghiệp vụ."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET

from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.primitives import DataError, date_iso

from . import __version__
from .hoa_don_xml import (
    MAX_XML_BYTES, InvoiceField, InvoiceIssue, InvoiceReadResult, _identity_text,
    doc_hoa_don_xml, ra_json,
)

JSON_TOI_DA_BYTE = 32 * 1024 * 1024
SO_DONG_HANG_TOI_DA = 1000
PHIEN_BAN_ENGINE = f"e_hoa_don {__version__}"
_TIEN = re.compile(r"-?(0|[1-9][0-9]{0,17})(\.[0-9]{1,6})?")
_DAU = {
    "mau_so": "KHMSHDon", "ky_hieu": "KHHDon", "so_hoa_don": "SHDon",
    "ngay_lap": "NLap", "don_vi_tien": "DVTTe",
    "ma_so_thue_ban": "NBan/MST", "ma_so_thue_mua": "NMua/MST",
}
_CANH_BAO_CHIEU = {
    "HOADON_HEADER_INVALID": "Trường đầu hóa đơn không hợp lệ; hãy kiểm tra nguồn.",
    "HOADON_MONEY_OVER_DOMAIN": "Tiền nguồn vượt miền 18/6; giữ số chính xác trong chi tiết.",
    "CONTEXT_ABSENT": "Chưa có ngữ cảnh tin cậy để xác định hóa đơn.",
    "IDENTITY_UNRESOLVED": "Chưa xác định được định danh hóa đơn.",
    "HD_MONEY_HOLD": "Thông tin tiền nguồn còn cần kiểm tra.",
    "HD_RELATIONS_HOLD": "Quan hệ hóa đơn nguồn còn cần kiểm tra.",
}


def _text(field: InvoiceField | None) -> str | None:
    value = None if field is None else field.duy_nhat
    return value.lexeme if value is not None and value.state == "TEXT" else None


def chieu_truong(result: InvoiceReadResult, tep_xml: dict) -> tuple[dict, list]:
    """Giữ số nguồn, null nếu mơ hồ; không tính lại tổng hay mặc định tiền tệ."""
    issues = list(dict.fromkeys((
        *result.issues, *result.money.issues, *result.relations.issues,
        *(i for dong in result.lines for i in dong.issues),
    )))
    van_de_phep_chieu = []

    def issue(code, locator):
        value = InvoiceIssue(code, _CANH_BAO_CHIEU[code], locator, "ERROR")
        if value not in van_de_phep_chieu:
            van_de_phep_chieu.append(value)
        if value not in issues:
            issues.append(value)

    header = {f.name: f for f in result.header_fields}
    dau = {}
    for name, tag in _DAU.items():
        field = header.get(tag)
        text = _text(field)
        if field is not None and any(
            i.code == "STRUCTURE_DUPLICATE"
            and field.locator.startswith(i.locator.rsplit("#", 1)[-1] + "/")
            for i in result.issues
        ):
            text = None
        if text is not None:
            valid = True
            if name == "ngay_lap":
                try:
                    date_iso(text)
                except DataError:
                    valid = False
            elif name == "don_vi_tien":
                valid = re.fullmatch(r"[A-Z]{3}", text) is not None
            elif name == "so_hoa_don":
                valid = re.fullmatch(r"[0-9]+", text) is not None
            else:
                valid = _identity_text(field.duy_nhat) is not None
            if not valid:
                issue("HOADON_HEADER_INVALID", field.locator)
                text = None
        dau[name] = text

    def tien(fact, locator):
        if fact.exact_value is None or "MONEY_SECTION_AMBIGUOUS" in result.money.reasons:
            return None
        text = format(fact.exact_value, "f")
        if not _TIEN.fullmatch(text):
            issue("HOADON_MONEY_OVER_DOMAIN", locator)
            return None
        currency = dau["don_vi_tien"]
        return None if currency is None else {"so": text, "tien_te": currency}

    for name, tag, fact in (
        ("tien_truoc_thue", "TgTCThue", result.money.net_amount),
        ("tien_thue", "TgTThue", result.money.tax_amount),
        ("tong_thanh_toan", "TgTTTBSo", result.money.total_amount),
    ):
        dau[name] = tien(fact, f"/HDon/DLHDon/NDHDon/TToan/{tag}")

    # Câu cảnh báo không chép message/locator/lexeme từ nguồn. Mã do lõi sinh.
    codes = list(dict.fromkeys((
        *(i.code for i in issues), *result.candidate_reasons,
        *result.money.reasons, *result.relations.reasons,
    )))
    if result.money.state == "HOLD":
        codes.append("HD_MONEY_HOLD")
    if result.relations.state == "HOLD":
        codes.append("HD_RELATIONS_HOLD")
    codes = list(dict.fromkeys(codes))
    dau.update({
        "so_dong": len(result.lines), "can_kiem_tra": bool(codes),
        "canh_bao": "\n".join(
            f"{ma}: {_CANH_BAO_CHIEU.get(ma, 'Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.')}"
            for ma in codes
        ),
        "tep_xml": tep_xml, "chi_tiet_nguon": None, "nguon_doc": "xml_strict",
        "phien_ban_engine": PHIEN_BAN_ENGINE,
        "bam_dau_vao": f"sha256:{result.raw_ref.native_sha256}",
    })
    return dau, van_de_phep_chieu


def _kiem_tran_dong_hang(raw: bytes) -> None:
    """Đếm phần tử thật, không dựng cây/DTO; dừng ngay ở HHDVu thứ 1.001.

    Gate tài nguyên đếm mọi HHDVu không namespace, không diễn giải profile.
    Lỗi cú pháp/encoding vẫn do bộ đọc strict bên dưới phân loại.
    """
    class DemDongHang:
        so_dong = 0

        def start(self, ten, thuoc_tinh):
            if ten == "HHDVu":
                self.so_dong += 1
                if self.so_dong > SO_DONG_HANG_TOI_DA:
                    raise LoiNghiepVu(
                        "HD_QUA_NHIEU_DONG_HANG",
                        "Tệp XML vượt giới hạn 1.000 dòng hàng hóa. Anh hãy gửi tệp ít dòng hơn.",
                    )

        def doctype(self, ten, public_id, system_id):
            raise LoiNghiepVu(
                "HD_XML_NGOAI_PROFILE",
                "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ.",
            )

        def close(self):
            return None

    parser = ET.XMLParser(target=DemDongHang())
    try:
        parser.feed(raw)
        parser.close()
    except (ET.ParseError, ValueError, LookupError):
        # Không đổi hợp đồng lỗi nguồn của parser lõi.
        return


def doc_xml(raw: bytes, *, tep_xml: dict) -> tuple[dict, bytes]:
    if len(raw) > MAX_XML_BYTES:
        raise LoiNghiepVu(
            "HD_XML_QUA_LON",
            "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.",
        )
    # Profile chỉ nhận UTF-8; không phản chiếu byte lỗi hoặc exception.
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        raise LoiNghiepVu(
            "HD_XML_NGOAI_PROFILE",
            "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ.",
        ) from None
    _kiem_tran_dong_hang(raw)
    # SDK chưa có context được kiểm quyền: không lấy MST/profile từ ngu_canh.
    result = doc_hoa_don_xml(raw, context=None)
    # Tái dùng gate cấu trúc của trang_thai._trang_thai_xml. Thiếu context là
    # cảnh báo dữ liệu, không phải nguồn ngoài đã nhận việc nên không ChuaRo.
    if result.shape == "XML_MALFORMED":
        raise LoiNghiepVu(
            "HD_XML_KHONG_DOC_DUOC",
            "Không đọc được cấu trúc tệp XML hóa đơn.",
        )
    if result.shape in {
        "UNSUPPORTED_INPUT", "UNSUPPORTED_NAMESPACE", "UNSUPPORTED_PATH", "STRUCTURE_DUPLICATE",
    }:
        raise LoiNghiepVu(
            "HD_XML_NGOAI_PROFILE",
            "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ.",
        )
    if result.shape != "SUPPORTED_SUBSET":
        raise RuntimeError("Trạng thái bộ đọc XML ngoài invariant.")
    truong, van_de = chieu_truong(result, tep_xml)
    bao_cao = {
        "phien_ban": 1, "nguon_doc": "xml_strict",
        "phien_ban_engine": PHIEN_BAN_ENGINE,
        "bam_dau_vao": truong["bam_dau_vao"], "tep_xml": tep_xml,
        "chi_tiet_nguon": ra_json(result), "van_de_phep_chieu": ra_json(van_de),
    }
    return truong, json.dumps(
        bao_cao, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")
