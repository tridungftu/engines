"""Kiểm JSON bước đọc và chiếu bảng kê; không đọc lại XML hay chạy nguồn Node."""

from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from types import SimpleNamespace
import unicodedata

from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu
from kho_tri_thuc_sdk.primitives import DataError

from .doc import PHIEN_BAN_ENGINE, chieu_truong
from .hoa_don_xml import FieldValue, InvoiceField, InvoiceIssue
from .xlsx_toi_thieu import tao_xlsx, vuot_tran

JSON_TOI_DA = 32 * 1024 * 1024
DONG_TOI_DA = 1000
THOI_HAN = 600
MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
COT_HOA_DON = tuple(zip((
    "STT", "Thứ tự entry", "Tên entry", "Băm tệp", "Mẫu số", "Ký hiệu",
    "Số hóa đơn", "Ngày lập", "MST bán", "MST mua", "Tiền trước thuế", "Tiền thuế",
    "Tổng thanh toán", "Mã tiền tệ", "Cần kiểm tra", "Cảnh báo", "Trùng với thứ tự",
), (8, 14, 32, 72, 16, 16, 18, 16, 20, 20, 26, 26, 26, 16, 16, 64, 20)))
COT_KIEM_KE = tuple(zip(("Thứ tự entry", "Tên entry", "Băm tệp", "Trạng thái đọc",
    "Trùng tên", "Trùng với thứ tự", "Mã lỗi", "Cảnh báo"), (14, 32, 72, 20, 14, 20, 36, 64)))
GHI_CHU = "Không xác nhận đủ hóa đơn trong kỳ; chưa thực hiện ghi nhận nghiệp vụ"
_DECIMAL = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")


def dau_vao_sai():
    raise LoiNghiepVu("HD_BANG_KE_DAU_VAO",
                     "Cần kết quả đọc XML hoặc ZIP hóa đơn hợp lệ để lập bảng kê.")


def _can(dieu_kien):
    if not dieu_kien:
        dau_vao_sai()


def _schema(value, s, root, kiem_tra):
    """Bộ kiểm đúng tập từ khóa của hai schema nội bộ; không tải schema ngoài."""
    kiem_tra()
    if "$ref" in s:
        target = root
        for key in s["$ref"].removeprefix("#/").split("/"):
            target = target[key]
        return _schema(value, target, root, kiem_tra)
    if "anyOf" in s and not any(_schema(value, p, root, kiem_tra) for p in s["anyOf"]):
        return False
    if not all(_schema(value, p, root, kiem_tra) for p in s.get("allOf", [])):
        return False
    if "if" in s and _schema(value, s["if"], root, kiem_tra):
        if not _schema(value, s.get("then", {}), root, kiem_tra):
            return False
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "boolean": bool, "null": type(None)}
    if "type" in s:
        names = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not any(type(value) is types[n] for n in names):
            return False
    if "const" in s and (type(value) is not type(s["const"]) or value != s["const"]):
        return False
    if "enum" in s and not any(type(value) is type(v) and value == v for v in s["enum"]):
        return False
    if isinstance(value, dict):
        props = s.get("properties", {})
        if not set(s.get("required", [])) <= value.keys():
            return False
        if s.get("additionalProperties") is False and not value.keys() <= props.keys():
            return False
        if not all(_schema(v, props[k], root, kiem_tra) for k, v in value.items() if k in props):
            return False
    if isinstance(value, list):
        if len(value) < s.get("minItems", 0) or len(value) > s.get("maxItems", len(value)):
            return False
        if not all(_schema(v, s.get("items", {}), root, kiem_tra) for v in value):
            return False
    if isinstance(value, str):
        if len(value) < s.get("minLength", 0):
            return False
        if "pattern" in s and re.fullmatch(s["pattern"].removeprefix("^").removesuffix("$"), value) is None:
            return False
    if type(value) is int and not s.get("minimum", value) <= value <= s.get("maximum", value):
        return False
    return True


def _doi_tuong(pairs):
    d = {}
    for k, v in pairs:
        _can(k not in d)
        d[k] = v
    return d


def _nap_dto(d):
    """Tái dựng phần DTO cho phép chiếu sẵn có, không parse XML."""
    def doi(v):
        if isinstance(v, list):
            values = tuple(doi(x) for x in v)
            if values and isinstance(values[0], InvoiceField):
                _can(len({x.name for x in values}) == len(values))
            return values
        if not isinstance(v, dict):
            return v
        if set(v) == {"state", "lexeme", "lexeme_basis"}:
            _can((v["state"] == "ABSENT" and v["lexeme"] is None)
                 or (v["state"] == "EMPTY" and v["lexeme"] == "")
                 or (v["state"] == "TEXT" and isinstance(v["lexeme"], str) and v["lexeme"] != ""))
            return FieldValue(**v)
        if "occurrences" in v:
            _can(bool(v["occurrences"]))
            return InvoiceField(**{k: doi(x) for k, x in v.items()})
        if set(v) == {"code", "message", "locator", "severity"}:
            return InvoiceIssue(**v)
        if "exact_value" in v:
            exact = v["state"] in {"EXACT", "PRECISION_UNDECLARED"}
            _can(exact == (isinstance(v["exact_value"], str) and isinstance(v["exact_text"], str)))
            if exact:
                _can(_DECIMAL.fullmatch(v["exact_text"]) is not None)
                _can(v["exact_value"] == v["exact_text"])
            else:
                _can(v["exact_value"] is None and v["exact_text"] is None)
            return SimpleNamespace(**{**v, "exact_value": Decimal(v["exact_value"]) if exact else None})
        return SimpleNamespace(**{k: doi(x) for k, x in v.items()})
    try:
        return doi(d)
    except DataError:
        dau_vao_sai()


def _kiem_dto(d, bam, size, container=None, ordinal=None, name=None):
    _can(isinstance(bam, str) and type(size) is int and size >= 0)
    ref = d["raw_ref"]
    _can(ref == dict(native_sha256=bam.removeprefix("sha256:"), byte_length=size,
                     media_type="application/xml", container_sha256=container,
                     entry_ordinal=ordinal, entry_name=name))
    _can(d["native_fiscal_status"] == "UNKNOWN" and d["business_promotion"] == "NOT_PERFORMED")
    if len(d["lines"]) > DONG_TOI_DA:
        vuot_tran()
    _can([x["source_ordinal"] for x in d["lines"]] == list(range(1, len(d["lines"]) + 1)))
    dto = _nap_dto(d)
    return dto


def _chieu(d, fields, tep, bam, size, container=None, ordinal=None, name=None):
    dto = _kiem_dto(d, bam, size, container, ordinal, name)
    _can(d["shape"] == "SUPPORTED_SUBSET")
    expected, _ = chieu_truong(dto, tep)
    for k, v in expected.items():
        if k in {"tep_xml", "chi_tiet_nguon"}:
            continue
        _can(k in fields and type(fields[k]) is type(v) and fields[k] == v)
    return dto


def _dong_hoa_don(e, stt, dto):
    f, d = e["truong_hoa_don"], e["chi_tiet_nguon"]
    warnings = list(e["canh_bao"])
    currency = f["don_vi_tien"]
    currency_ok = (isinstance(currency, str) and re.fullmatch(r"[A-Z]{3}", currency)
                   and currency == d["money"]["currency"])
    if not currency_ok:
        warnings.append("HD_BANG_KE_CURRENCY: Thiếu hoặc mơ hồ mã tiền tệ; để trống tiền.")
    amounts = []
    for key, tag in (("net_amount", "TgTCThue"), ("tax_amount", "TgTThue"), ("total_amount", "TgTTTBSo")):
        fact = d["money"][key]
        occurrences = [x for x in dto.money.fields if x.name == tag]
        val = occurrences[0].duy_nhat if len(occurrences) == 1 else None
        text = fact["exact_text"]
        valid = (currency_ok and fact["state"] in {"EXACT", "PRECISION_UNDECLARED"}
                 and "MONEY_SECTION_AMBIGUOUS" not in dto.money.reasons
                 and val is not None and val.state == "TEXT"
                 and _DECIMAL.fullmatch(val.lexeme) is not None
                 and Decimal(val.lexeme) == Decimal(text))
        amounts.append(text if valid else None)
        if not valid:
            warnings.append("HD_BANG_KE_TIEN: Tiền thiếu, sai hoặc mơ hồ; để trống ô tương ứng.")
    warnings = list(dict.fromkeys(warnings))
    ngay = date.fromisoformat(f["ngay_lap"]) if f["ngay_lap"] else None
    return [stt, e["thu_tu"], e["ten"], e["bam"], f["mau_so"], f["ky_hieu"], f["so_hoa_don"],
            f"{ngay.day:02d}/{ngay.month:02d}/{ngay.year:04d}" if ngay else None,
            f["ma_so_thue_ban"], f["ma_so_thue_mua"], *amounts, currency if currency_ok else None,
            "Có" if f["can_kiem_tra"] or warnings else "Không", "\n".join(warnings), e["trung_noi_dung_voi"]]


def lap_bang_ke(viec):
    bat_dau = time.monotonic()

    def kiem_tra():
        viec.kiem_huy()
        if time.monotonic() - bat_dau > THOI_HAN:
            vuot_tran()

    kiem_tra()
    t = viec.dau_vao.get("truong")
    _can(viec.dau_vao.get("loai") == "truong" and isinstance(t, dict))
    source = t.get("nguon_doc")
    _can(isinstance(source, str) and source in {"xml_strict", "zip_xml_strict"})
    xml = source == "xml_strict"
    key = "tep_xml" if xml else "tep_zip"
    _can(key in t and ("tep_zip" if xml else "tep_xml") not in t)
    ref = t.get("chi_tiet_nguon")
    _can(isinstance(ref, dict) and isinstance(ref.get("tep_id"), str) and bool(ref["tep_id"]))
    _can(ref.get("mime") == "application/json")
    if type(ref.get("kich_thuoc")) is int and ref["kich_thuoc"] > JSON_TOI_DA:
        vuot_tran()
    viec.tien_do(10, "Đang đọc chi tiết nguồn để lập bảng kê.")
    raw = bytearray()
    try:
        with viec.mo_tep(ref["tep_id"]) as stream:
            while len(raw) <= JSON_TOI_DA:
                kiem_tra()
                chunk = stream.read(min(65536, JSON_TOI_DA + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
    except (LoiDuongTruyen, LoiNghiepVu) as loi:
        if loi.ma in {"VUOT_GIOI_HAN_KICH_THUOC", "VUOT_GIOI_HAN"}:
            vuot_tran()
        raise
    if len(raw) > JSON_TOI_DA:
        vuot_tran()
    _can("kich_thuoc" not in ref or type(ref["kich_thuoc"]) is int and ref["kich_thuoc"] == len(raw))
    try:
        report = json.loads(raw.decode("utf-8"), object_pairs_hook=_doi_tuong,
                            parse_constant=lambda _: dau_vao_sai())
    except (ValueError, UnicodeError, RecursionError):
        dau_vao_sai()
    _can(isinstance(report, dict))
    for k in ("danh_sach_tep", "danh_sach_thu_muc"):
        if isinstance(report.get(k), list) and len(report[k]) > DONG_TOI_DA:
            vuot_tran()
    schema_path = Path(__file__).resolve().parent.parent / "contract" / f"bao_cao_{'xml' if xml else 'zip'}.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    _can(_schema(report, schema, schema, kiem_tra))
    for k in ("nguon_doc", "phien_ban_engine", "bam_dau_vao", key):
        _can(report[k] == t.get(k))
    _can(re.fullmatch(r"e_hoa_don [0-9]+\.[0-9]+\.[0-9]+", report["phien_ban_engine"]) is not None)
    if xml:
        d = report["chi_tiet_nguon"]
        dto = _chieu(d, t, report[key], report["bam_dau_vao"], d["raw_ref"]["byte_length"])
        if "kich_thuoc" in report[key]:
            _can(report[key]["kich_thuoc"] == d["raw_ref"]["byte_length"])
        files = [dict(thu_tu=1, ten=report[key].get("ten", ""), bam=report["bam_dau_vao"],
            trang_thai_doc="doc_duoc", trung_ten=False, trung_noi_dung_voi=None, ma_loi=None,
            canh_bao=t["canh_bao"].splitlines(), truong_hoa_don=t, chi_tiet_nguon=d)]
        dirs, dtos = [], {1: dto}
        counts = dict(so_tep=1, so_doc_duoc=1, so_loi=0, so_khong_ho_tro=0, so_trung_noi_dung=0)
        doc_het, warnings = True, t["canh_bao"].splitlines()
    else:
        files, dirs, dtos = report["danh_sach_tep"], report["danh_sach_thu_muc"], {}
        if len(files) + len(dirs) > DONG_TOI_DA:
            vuot_tran()
        all_entries = sorted([*files, *dirs], key=lambda e: e["thu_tu"])
        _can([e["thu_tu"] for e in all_entries] == list(range(1, len(all_entries) + 1)))
        names = [unicodedata.normalize("NFC", e["ten"]).casefold() for e in all_entries]
        for e, normalized in zip(all_entries, names):
            _can(e["trung_ten"] == (names.count(normalized) > 1))
        _can([e["thu_tu"] for e in files] == sorted(e["thu_tu"] for e in files))
        _can([e["thu_tu"] for e in dirs] == sorted(e["thu_tu"] for e in dirs))
        seen = {}
        for e in files:
            kiem_tra()
            _can(e["trung_noi_dung_voi"] == (seen.get(e["bam"]) if e["bam"] else None))
            if e["bam"]:
                seen.setdefault(e["bam"], e["thu_tu"])
            if e["chi_tiet_nguon"] is not None:
                _kiem_dto(e["chi_tiet_nguon"], e["bam"], e["kich_thuoc"],
                          report["bam_dau_vao"][7:], e["thu_tu"], e["ten"])
            if e["trang_thai_doc"] == "doc_duoc":
                f = e["truong_hoa_don"]
                _can(f["nguon"] == dict(tep_zip=report[key], bam_goi=report["bam_dau_vao"],
                    thu_tu=e["thu_tu"], ten=e["ten"], bam=e["bam"]))
                _can(f["phien_ban_engine"] == report["phien_ban_engine"])
                dtos[e["thu_tu"]] = _chieu(e["chi_tiet_nguon"], f, {}, e["bam"], e["kich_thuoc"],
                                          report["bam_dau_vao"][7:], e["thu_tu"], e["ten"])
        counts = dict(so_tep=len(files), so_doc_duoc=len(dtos),
            so_loi=sum(e["trang_thai_doc"] == "loi" for e in files),
            so_khong_ho_tro=sum(e["trang_thai_doc"] == "khong_ho_tro" for e in files),
            so_trung_noi_dung=sum(e["trung_noi_dung_voi"] is not None for e in files))
        doc_het = (bool(files) and len(dtos) == len(files) and all(e["bam"] for e in files)
                   and not any(d["canh_bao"] for d in dirs))
        for k, v in {**counts, "da_doc_het": doc_het, "can_kiem_tra": True}.items():
            _can(type(report[k]) is type(v) and report[k] == v)
            _can(type(t.get(k)) is type(v) and t[k] == v)
        _can(t.get("canh_bao") == "\n".join(report["canh_bao"]))
        warnings = report["canh_bao"]
    if len(dtos) > DONG_TOI_DA:
        vuot_tran()
    hoa_don, inventory = [], []
    for e in files:
        kiem_tra()
        if e["trang_thai_doc"] == "doc_duoc":
            hoa_don.append(_dong_hoa_don(e, len(hoa_don) + 1, dtos[e["thu_tu"]]))
        inventory.append([e["thu_tu"], e["ten"], e["bam"], e["trang_thai_doc"],
                          "Có" if e["trung_ten"] else "Không", e["trung_noi_dung_voi"],
                          e["ma_loi"], "\n".join(e["canh_bao"])])
    inventory.extend([d["thu_tu"], d["ten"], None, "thu_muc", "Có" if d["trung_ten"] else "Không",
                      None, None, "\n".join(d["canh_bao"])] for d in dirs)
    inventory.sort(key=lambda row: row[0])
    digest = "sha256:" + sha256(raw).hexdigest()
    warning = "\n".join(dict.fromkeys([*warnings,
        *(line for row in hoa_don for line in row[15].splitlines()), GHI_CHU]))
    info = [[GHI_CHU], ["Nguồn đọc", source], ["Phiên bản nguồn", report["phien_ban_engine"]],
            ["Phiên bản bảng kê", PHIEN_BAN_ENGINE], ["Băm JSON", digest], ["Băm XML/ZIP", report["bam_dau_vao"]],
            *[[k, v] for k, v in counts.items()], ["da_doc_het", "Có" if doc_het else "Không"],
            ["Cảnh báo", "\n".join(warnings)]]
    viec.tien_do(60, "Đang tạo bảng kê hóa đơn và kiểm kê tệp.")
    data = tao_xlsx(hoa_don, inventory, info, COT_HOA_DON, COT_KIEM_KE, kiem_tra)
    kiem_tra()
    viec.tien_do(80, "Đang lưu bảng kê hóa đơn.")
    kiem_tra()
    output = viec.tai_tep_ra("hoa-don-bang-ke.xlsx", data, MIME)
    _can(isinstance(output, dict) and isinstance(output.get("tep_id"), str) and bool(output["tep_id"]))
    viec.tien_do(100, "Đã trả bảng kê; cần kiểm tra kết quả nguồn.")
    kiem_tra()
    return {"loai": "truong", "truong": dict(bang_ke=output, chi_tiet_nguon=ref,
        so_hoa_don=counts["so_doc_duoc"], so_loi=counts["so_loi"], so_khong_ho_tro=counts["so_khong_ho_tro"],
        so_trung_noi_dung=counts["so_trung_noi_dung"], da_doc_het=doc_het, can_kiem_tra=True,
        canh_bao=warning, bam_dau_vao=digest, phien_ban_engine=PHIEN_BAN_ENGINE)}
