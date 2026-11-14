"""HD-1: đáp án literal DEMO, kiểm lõi thuần và đường trả qua CoreGia."""

from dataclasses import replace
from decimal import Decimal, localcontext
from hashlib import sha256
import io
import json
import re

import pytest
from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu, Viec, ViecDaHuy
from kho_tri_thuc_sdk.primitives import DataError
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoa_don.chay import app, doc_hoa_don
from e_hoa_don.doc import doc_xml
from e_hoa_don.hoa_don_xml import (
    CompanyFact, IDENTITY_PROFILE_REF, InvoiceReadContext, InvoiceMeasurementFacts,
    MAX_XML_BYTES, PROFILE_DOCUMENT_SHA256, PROFILE_REF, XmlRawRef, doc_hoa_don_xml,
)


def qua_core(raw, *, metadata=None):
    core = CoreGia()
    tep = core.them_tep("DEMO.xml", raw, "application/xml")
    tep.update(metadata or {})
    kq = core.chay_thu(app, "hoa_don.doc_xml@2", {"loai": "tep", "tep": tep})
    return core, kq


def thanh_cong(raw):
    core, kq = qua_core(raw)
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    report = json.loads(core.doc_tep(t["chi_tiet_nguon"]["tep_id"]))
    assert t["can_kiem_tra"] is True
    return t, report["chi_tiet_nguon"], report["van_de_phep_chieu"]


def thay(raw, tag, text):
    tag = tag.encode()
    value = b"" if text is None else b"<" + tag + b">" + text.encode() + b"</" + tag + b">"
    return re.sub(b"<" + tag + b">[^<]*</" + tag + b">", lambda _: value, raw)


@pytest.mark.parametrize(("lexeme", "state", "expected", "issue"), [
    (None, "ABSENT", None, "MONEY_ABSENT"),
    ("", "EMPTY", None, "MONEY_EMPTY"),
    ("0", "PRECISION_UNDECLARED", "0", None),
    ("0.000000", "PRECISION_UNDECLARED", "0.000000", None),
    ("1000000.123456", "PRECISION_UNDECLARED", "1000000.123456", None),
    ("1000000.120000", "PRECISION_UNDECLARED", "1000000.120000", None),
    ("-1000000.120000", "PRECISION_UNDECLARED", "-1000000.120000", None),
    ("1,000.00", "INVALID", None, "MONEY_LEXEME_INVALID"),
    ("1e6", "INVALID", None, "MONEY_LEXEME_INVALID"),
    ("+1", "INVALID", None, "MONEY_LEXEME_INVALID"),
    (" 1 ", "INVALID", None, "MONEY_LEXEME_INVALID"),
])
def test_tien_absent_empty_zero_exact_va_sai(xml_demo, lexeme, state, expected, issue):
    t, d, _ = thanh_cong(thay(xml_demo, "TgTCThue", lexeme))
    fact = d["money"]["net_amount"]
    assert fact["state"] == state
    assert fact["exact_value"] == expected
    assert t["tien_truoc_thue"] == (None if expected is None else {"so": expected, "tien_te": "VND"})
    f = next(f for f in d["money"]["fields"] if f["name"] == "TgTCThue")
    assert [(o["state"], o["lexeme"]) for o in f["occurrences"]] == [
        ("ABSENT" if lexeme is None else "EMPTY" if lexeme == "" else "TEXT", lexeme)
    ]
    if issue:
        assert issue in d["money"]["reasons"]


@pytest.mark.parametrize("tag,field", [("TgTCThue", "tien_truoc_thue"), ("TgTThue", "tien_thue"), ("TgTTTBSo", "tong_thanh_toan")])
@pytest.mark.parametrize("value,project", [
    ("999999999999999999.999999", True),
    ("1000000000000000000", False), ("1.1234567", False),
])
def test_mien_18_6_khong_cat(xml_demo, tag, field, value, project):
    t, d, issues = thanh_cong(thay(xml_demo, tag, value))
    fact_name = {"TgTCThue": "net_amount", "TgTThue": "tax_amount", "TgTTTBSo": "total_amount"}[tag]
    assert d["money"][fact_name]["exact_text"] == value
    assert t[field] == ({"so": value, "tien_te": "VND"} if project else None)
    if not project:
        assert "HOADON_MONEY_OVER_DOMAIN" in {i["code"] for i in issues}


@pytest.mark.parametrize("tag,field,code", [("SLuong", "quantity", "QUANTITY"), ("DGia", "unit_price", "UNIT_PRICE")])
@pytest.mark.parametrize("value,state,suffix", [
    ("999999999999999.999999", "EXACT", None),
    ("9999999999999999.999999", "OVER_DOMAIN", "DIGITS_EXCEEDED"),
    ("1.1234567", "OVER_DOMAIN", "SCALE_EXCEEDED"),
    ("1e3", "INVALID", "LEXEME_INVALID"), ("1,5", "INVALID", "LEXEME_INVALID"),
])
def test_mien_so_luong_don_gia_21_6(xml_demo, tag, field, code, value, state, suffix):
    raw = thay(xml_demo, tag, value)
    line = doc_hoa_don_xml(raw).lines[0]
    fact = getattr(line, field)
    assert fact.state == state
    assert line.field(tag).duy_nhat.lexeme == value
    assert fact.exact_text == (value if state == "EXACT" else None)
    if suffix:
        assert code + "_" + suffix in {i.code for i in line.issues}
    _, d, _ = thanh_cong(raw)
    assert d["lines"][0][field]["state"] == state


@pytest.mark.parametrize("value", [None, "", "vnd", "VN", " VND "])
def test_currency_thieu_sai_khong_gia_tien(xml_demo, value):
    t, d, _ = thanh_cong(thay(xml_demo, "DVTTe", value))
    assert t["don_vi_tien"] is None
    assert [t[k] for k in ("tien_truoc_thue", "tien_thue", "tong_thanh_toan")] == [None, None, None]
    assert d["money"]["currency"] is None
    assert d["money"]["net_amount"]["exact_text"] == "1000000"


@pytest.mark.parametrize("value", [None, "", "2026-02-30", "30/10/2026", "20261030", "2026-10-30T00:00:00"])
def test_ngay_null_canh_bao_va_lexeme_goc(xml_demo, value):
    t, d, _ = thanh_cong(thay(xml_demo, "NLap", value))
    assert t["ngay_lap"] is None
    f = next(f for f in d["header_fields"] if f["name"] == "NLap")
    assert f["occurrences"][0]["lexeme"] == value
    assert any(i["code"].startswith("DATE_") for i in d["issues"])


@pytest.mark.parametrize("tag,field", [("SHDon", "so_hoa_don"), ("DVTTe", "don_vi_tien"), ("TgTCThue", "tien_truoc_thue")])
@pytest.mark.parametrize("mixed", [False, True])
def test_trung_mixed_khong_chon_scalar(xml_demo, tag, field, mixed):
    raw = re.sub(("<" + tag + ">([^<]*)</" + tag + ">").encode(),
                 lambda m: b"<" + tag.encode() + b">DEMO<x/>tail</" + tag.encode() + b">" if mixed else m[0] + m[0], xml_demo)
    t, d, _ = thanh_cong(raw)
    assert t[field] is None
    fields = d["money"]["fields"] if tag == "TgTCThue" else d["header_fields"]
    f = next(f for f in fields if f["name"] == tag)
    assert f["mixed_content"] is mixed
    assert len(f["occurrences"]) == (1 if mixed else 2)
    if field == "don_vi_tien":
        assert t["tien_truoc_thue"] is None


def test_cau_truc_ben_ban_trung_khong_chon_mst_dau(xml_demo):
    raw = xml_demo.replace(b"</NBan>", b"</NBan><NBan/>")
    t, d, _ = thanh_cong(raw)
    assert t["ma_so_thue_ban"] is None
    f = next(f for f in d["header_fields"] if f["name"] == "NBan/MST")
    assert f["occurrences"][0]["lexeme"] == "0100000001"
    assert "STRUCTURE_DUPLICATE" in {i["code"] for i in d["issues"]}


def test_namespace_long_khong_ghep_the_cung_localname(xml_demo):
    raw = xml_demo.replace(b"<SHDon>0000123</SHDon>", b'<SHDon xmlns="urn:DEMO">0000123</SHDon>')
    _, kq = qua_core(raw)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "HD_XML_NGOAI_PROFILE"


def test_ttoan_trung_khong_chieu_scalar_tu_nhieu_section(xml_demo):
    raw = xml_demo.replace(b"</TToan>", b"</TToan><TToan/>")
    t, d, _ = thanh_cong(raw)
    assert [t[k] for k in ("tien_truoc_thue", "tien_thue", "tong_thanh_toan")] == [None, None, None]
    assert "MONEY_SECTION_AMBIGUOUS" in d["money"]["reasons"]
    assert d["money"]["net_amount"]["exact_text"] == "1000000"


def test_so_chuoi_va_khong_suy_identity_dong(xml_demo):
    raw = thay(xml_demo, "MHHDVu", "0000456")
    row = re.search(b"<HHDVu>.*?</HHDVu>", raw, re.S)[0]
    raw = raw.replace(row, row + row)
    t, d, _ = thanh_cong(raw)
    assert (t["so_hoa_don"], t["ma_so_thue_ban"], t["ma_so_thue_mua"]) == ("0000123", "0100000001", "0100000002")
    assert t["so_dong"] == 2
    assert [line["source_ordinal"] for line in d["lines"]] == [1, 2]
    assert [line["logical_line_ref"] for line in d["lines"]] == [None, None]
    for line in d["lines"]:
        assert next(f for f in line["fields"] if f["name"] == "MHHDVu")["occurrences"][0]["lexeme"] == "0000456"
        assert "STT_DUPLICATE" in {i["code"] for i in line["issues"]}


def context_demo(raw):
    return InvoiceReadContext(
        source_instance="nguon-DEMO", source_profile_ref=PROFILE_REF,
        profile_document_sha256=PROFILE_DOCUMENT_SHA256, identity_profile_ref=IDENTITY_PROFILE_REF,
        company=CompanyFact("0100000002", "PN-DEMO", "map-DEMO", 1, "scope-DEMO"),
        expected_raw_ref=XmlRawRef(sha256(raw).hexdigest(), len(raw)),
        resolved_invoice_measurement_facts=InvoiceMeasurementFacts(
            "decimal-DEMO", "unit-DEMO", PROFILE_DOCUMENT_SHA256, "CAI", "CAI", "1", "1", 21, 6),
    )


def test_context_du_chi_ham_thuan_va_ngoai_envelope(xml_demo):
    # Fixture LF độc lập với kiểu checkout; không bỏ issue để ép tạo digest.
    raw = xml_demo.replace(b"\r\n", b"\n")
    result = doc_hoa_don_xml(raw, context_demo(raw))
    assert result.canonical_identity == ("PN-DEMO", "MUA_VAO", "0100000001", "1", "C26TAA", "123")
    assert result.semantic_digest is None and result.semantic_envelope is None
    assert "TOTAL_SECTION_UNSUPPORTED" in {i.code for i in result.issues}
    assert "CONTENT_OUTSIDE_SUPPORTED_ENVELOPE" in result.candidate_reasons
    assert result.lines[0].normalized_quantity_text == "1"
    assert result.lines[0].logical_line_ref is None
    assert result.money.net_amount.exact_value == Decimal("1000000")
    assert result.money.non_taxable_amount.exact_value == Decimal("0")


@pytest.mark.parametrize("change,reason", [
    ({"company": None}, "COMPANY_ABSENT"),
    ({"source_profile_ref": "profile-DEMO-sai"}, "PROFILE_REF_MISMATCH"),
    ({"profile_document_sha256": "0" * 64}, "PROFILE_DOCUMENT_MISMATCH"),
    ({"expected_raw_ref": XmlRawRef("0" * 64, 1)}, "RAW_REF_MISMATCH"),
    ({"profile_payload_sha256": PROFILE_DOCUMENT_SHA256}, "PROFILE_PAYLOAD_CONFUSED"),
])
def test_context_thieu_mau_thuan_khong_identity_digest_gia(xml_demo, change, reason):
    result = doc_hoa_don_xml(xml_demo, replace(context_demo(xml_demo), **change))
    assert result.canonical_identity is result.semantic_digest is result.semantic_envelope is None
    assert reason in result.candidate_reasons
    if reason != "COMPANY_ABSENT":
        assert result.lines[0].normalized_quantity_text is None


def test_tthdlquan_giu_chi_tiet_va_khong_digest(xml_demo):
    relation = (b"<TTHDLQuan><TCHDon>2</TCHDon><KHMSHDCLQuan>1</KHMSHDCLQuan>"
                b"<KHHDCLQuan>C26TAA</KHHDCLQuan><SHDCLQuan>0000011</SHDCLQuan>"
                b"<NLHDCLQuan>2026-02-30</NLHDCLQuan></TTHDLQuan>")
    raw = xml_demo.replace(b"</TTChung>", relation + relation + b"</TTChung>")
    t, d, _ = thanh_cong(raw)
    assert d["semantic_digest"] is None
    assert "CONTENT_OUTSIDE_SUPPORTED_ENVELOPE" in d["candidate_reasons"]
    assert "TOTAL_SECTION_UNSUPPORTED" in {i["code"] for i in d["issues"]}
    assert len(d["relations"]["items"]) == 2
    for item in d["relations"]["items"]:
        assert (item["relation_type"], item["original_number"], item["original_date"]) == ("DIEU_CHINH", "0000011", None)
        assert next(f for f in item["fields"] if f["name"] == "NLHDCLQuan")["occurrences"][0]["lexeme"] == "2026-02-30"
    assert "RELATION_DATE_INVALID:" in t["canh_bao"]
    assert d["money"]["tax_components"][0]["rate"] == "10%"
    assert d["money"]["tax_components"][0]["tax_amount"]["exact_text"] == "100000"


@pytest.mark.parametrize("raw,ma,message", [
    (b"<HDon>DEMO-CANARY", "HD_XML_KHONG_DOC_DUOC", "Không đọc được cấu trúc tệp XML hóa đơn."),
    (b'<HDon xmlns="urn:DEMO-CANARY"/>', "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<wrapper><HDon/></wrapper>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<!DOCTYPE HDon SYSTEM 'file:///DEMO-CANARY'><HDon/>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b'<?xml version="1.0" encoding="latin-1"?><HDon/>', "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"\xff\xfe<\x00H\x00", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<HDon>\xffDEMO-CANARY</HDon>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
])
def test_loi_nguon_co_dinh_khong_phan_chieu(raw, ma, message, capsys):
    core, kq = qua_core(raw)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert (kq["loi"]["ma"], kq["loi"]["thong_diep"]) == (ma, message)
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    output = capsys.readouterr()
    assert "DEMO-CANARY" not in output.out + output.err + json.dumps(kq["loi"])


def test_invariant_dataerror_khong_boc_loi_nguon(xml_demo, monkeypatch):
    import e_hoa_don.doc as doc
    def loi_noi_bo(*args, **kwargs):
        raise DataError("FIELD_VALUE_INVARIANT", "Bất biến nội bộ DEMO.")
    monkeypatch.setattr(doc, "doc_hoa_don_xml", loi_noi_bo)
    with pytest.raises(DataError):
        doc_xml(xml_demo, tep_xml={})
    _, kq = qua_core(xml_demo)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] not in {"HD_XML_NGOAI_PROFILE", "HD_XML_KHONG_DOC_DUOC"}


def test_tong_exact_khong_phu_thuoc_decimal_context(xml_demo):
    raw = thay(thay(thay(xml_demo, "TgTCThue", "1000000.123456"), "TgTThue", "100000.012345"), "TgTTTBSo", "1100000.135801")
    raw = thay(thay(raw, "ThTien", "1000000.123456"), "TThue", "100000.012345")
    with localcontext() as ctx:
        ctx.prec = 2
        t, d, _ = thanh_cong(raw)
    assert t["tong_thanh_toan"] == {"so": "1100000.135801", "tien_te": "VND"}
    assert "MONEY_TOTAL_CONFLICT" not in d["money"]["reasons"]


def test_net_bao_gom_kct_khong_doi_nhan_thue(xml_demo):
    raw = thay(thay(xml_demo, "TgTThue", "90000"), "TgTTTBSo", "1090000")
    raw = thay(raw, "TGTKCThue", "100000")
    raw = re.sub(b"<THTTLTSuat>.*?</THTTLTSuat>",
        b"<THTTLTSuat><LTSuat><TSuat>10%</TSuat><ThTien>900000</ThTien><TThue>90000</TThue></LTSuat>"
        b"<LTSuat><TSuat>KCT</TSuat><ThTien>100000</ThTien><TThue>0</TThue></LTSuat></THTTLTSuat>", raw, flags=re.S)
    t, d, _ = thanh_cong(raw)
    assert t["tien_truoc_thue"] == {"so": "1000000", "tien_te": "VND"}
    assert d["money"]["non_taxable_amount"]["exact_text"] == "100000"
    assert [(c["rate"], c["net_amount"]["exact_text"], c["tax_amount"]["exact_text"])
            for c in d["money"]["tax_components"]] == [("10%", "900000", "90000"), ("KCT", "100000", "0")]
    assert "MONEY_TOTAL_CONFLICT" not in d["money"]["reasons"]


def test_bao_cao_giu_het_occurrence_khong_cat(xml_demo):
    raw = xml_demo.replace(b"<SHDon>0000123</SHDon>", b"<SHDon>0000123</SHDon>" * 1001)
    t, d, _ = thanh_cong(raw)
    f = next(f for f in d["header_fields"] if f["name"] == "SHDon")
    assert len(f["occurrences"]) == 1001
    assert all(o["state"] == "TEXT" and o["lexeme"] == "0000123" for o in f["occurrences"])
    assert t["so_hoa_don"] is None


def test_doc_thuan_vuot_tran_16_mib():
    with pytest.raises(LoiNghiepVu) as exc:
        doc_xml(b" " * (MAX_XML_BYTES + 1), tep_xml={})
    assert (exc.value.ma, exc.value.thong_diep) == (
        "HD_XML_QUA_LON", "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.")


def test_bytes_thuc_vuot_tran_core_metadata_nho():
    core, kq = qua_core(b" " * (MAX_XML_BYTES + 2), metadata={"kich_thuoc": 1})
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "HD_XML_QUA_LON"
    assert kq["loi"]["thong_diep"] == "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn."
    assert core.so_lan_ghi["tep"] == 0


def test_gioi_han_read_16_mib_cong_1(monkeypatch):
    sizes = []
    class Luong(io.BytesIO):
        def read(self, n=-1):
            sizes.append(n)
            return super().read(n)
    # Seam luồng thực: SDK 2.0 bình thường tải bytes và chặn trần trước handler.
    monkeypatch.setattr(Viec, "mo_tep", lambda self, tep_id: Luong(b" " * (MAX_XML_BYTES + 2)))
    core, kq = qua_core(b"DEMO", metadata={"kich_thuoc": 1})
    assert sizes == [MAX_XML_BYTES + 1]
    assert kq["loi"]["ma"] == "HD_XML_QUA_LON" and core.so_lan_ghi["tep"] == 0


def test_metadata_vuot_tran_sdk_tu_choi():
    _, kq = qua_core(b"<HDon/>", metadata={"kich_thuoc": MAX_XML_BYTES + 1})
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "VUOT_GIOI_HAN"


def test_bao_cao_thuc_vuot_32_mib_khong_upload(xml_demo):
    # <10 MiB source sinh trong RAM → >32 MiB occurrence JSON, không cắt.
    raw = xml_demo.replace(b"<SHDon>0000123</SHDon>", b"<SHDon>0000123</SHDon>" * 400000)
    assert len(raw) < MAX_XML_BYTES
    core, kq = qua_core(raw)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "HD_KET_QUA_QUA_LON"
    assert kq["loi"]["thong_diep"] == "Kết quả đọc hóa đơn vượt giới hạn. Anh hãy chia nhỏ dữ liệu đầu vào."
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("loi", [
    LoiDuongTruyen("VUOT_GIOI_HAN_KICH_THUOC", "DEMO-CANARY", http_status=413),
    LoiNghiepVu("VUOT_GIOI_HAN", "DEMO-CANARY"),
])
@pytest.mark.parametrize("luc_doc", [False, True])
def test_boc_dung_loi_kich_thuoc_mo_doc_tep(loi, luc_doc, xml_demo, monkeypatch):
    class Luong(io.BytesIO):
        def read(self, n=-1):
            raise loi

    def mo(self, tep_id):
        if luc_doc:
            return Luong(xml_demo)
        raise loi

    monkeypatch.setattr(Viec, "mo_tep", mo)
    core, kq = qua_core(xml_demo)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert (kq["loi"]["ma"], kq["loi"]["thong_diep"]) == (
        "HD_XML_QUA_LON", "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.")
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("loi", [
    LoiDuongTruyen("DEMO_KHONG_CO_QUYEN", http_status=403),
    LoiDuongTruyen("DEMO_MAT_LEASE", http_status=409),
    LoiDuongTruyen("DEMO_KHONG_CON_VIEC", http_status=404),
    LoiDuongTruyen("DEMO_HET_HAN", http_status=410),
    LoiDuongTruyen("VUOT_GIOI_HAN", http_status=413),
    LoiNghiepVu("VUOT_GIOI_HAN_KICH_THUOC", "Lỗi DEMO khác kiểu."),
    LoiNghiepVu("DEMO_KHONG_DOC_DUOC", "Không đọc được tệp DEMO."),
    ViecDaHuy(),
    DataError("DEMO_INVARIANT", "Bất biến DEMO."),
])
def test_loi_mo_tep_khac_giu_nguyen(loi):
    class ViecDemo:
        dau_vao = {"tep": {"tep_id": "DEMO"}}

        def tien_do(self, *args):
            pass

        def mo_tep(self, tep_id):
            raise loi

    with pytest.raises(type(loi)) as exc:
        doc_hoa_don(ViecDemo())
    assert exc.value is loi


def test_bytes_dung_tran_16_mib_duoc_doc(xml_demo):
    raw = xml_demo + b" " * (MAX_XML_BYTES - len(xml_demo))
    core, kq = qua_core(raw)
    assert kq["trang_thai"] == "XONG", kq
    assert core.so_lan_ghi["tep"] == 1


def test_json_dung_tran_duoc_upload(xml_demo, monkeypatch):
    import e_hoa_don.chay as chay_module
    _, bao_cao = doc_xml(xml_demo, tep_xml={})
    monkeypatch.setattr(chay_module, "doc_xml", lambda *args, **kwargs: ({}, bao_cao))
    monkeypatch.setattr(chay_module, "JSON_TOI_DA_BYTE", len(bao_cao))

    class ViecDemo:
        dau_vao = {"tep": {"tep_id": "DEMO"}}

        def tien_do(self, *args):
            pass

        def mo_tep(self, tep_id):
            return io.BytesIO(xml_demo)

        def kiem_huy(self):
            pass

        def tai_tep_ra(self, ten, du_lieu, mime):
            assert du_lieu == bao_cao
            return {"tep_id": "DEMO-BAO-CAO"}

    kq = doc_hoa_don(ViecDemo())
    assert kq["truong"]["chi_tiet_nguon"] == {"tep_id": "DEMO-BAO-CAO"}


@pytest.mark.parametrize("so_dong", [1001, 200000])
def test_vuot_tran_dong_hang_chan_truoc_dto_json(xml_demo, monkeypatch, so_dong, capsys):
    import e_hoa_don.doc as doc
    raw = re.sub(
        b"<DSHHDVu>.*?</DSHHDVu>",
        b"<DSHHDVu>" + b"<HHDVu/>" * so_dong + b"</DSHHDVu>",
        xml_demo, flags=re.S,
    )
    assert len(raw) < MAX_XML_BYTES

    def cam_dung_dto(*args, **kwargs):
        raise AssertionError("Phải chặn trước parser lõi và trước dựng JSON.")

    monkeypatch.setattr(doc, "doc_hoa_don_xml", cam_dung_dto)
    core, kq = qua_core(raw)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert (kq["loi"]["ma"], kq["loi"]["thong_diep"]) == (
        "HD_QUA_NHIEU_DONG_HANG",
        "Tệp XML vượt giới hạn 1.000 dòng hàng hóa. Anh hãy gửi tệp ít dòng hơn.",
    )
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    output = capsys.readouterr()
    assert "0100000001" not in output.out + output.err + json.dumps(kq["loi"])


def test_dung_tran_1000_dong_giu_du_thu_tu_va_occurrence(xml_demo):
    raw = re.sub(
        b"<DSHHDVu>.*?</DSHHDVu>",
        b"<DSHHDVu>" + b"<HHDVu><STT>0001</STT><MHHDVu>DEMO</MHHDVu></HHDVu>" * 1000 + b"</DSHHDVu>",
        xml_demo, flags=re.S,
    )
    t, d, _ = thanh_cong(raw)
    assert t["so_dong"] == len(d["lines"]) == 1000
    assert d["lines"][0]["source_locator"].endswith("HHDVu[1]")
    assert d["lines"][-1]["source_locator"].endswith("HHDVu[1000]")
    for dong in d["lines"]:
        stt = next(f for f in dong["fields"] if f["name"] == "STT")
        assert stt["occurrences"][0]["lexeme"] == "0001"


def test_tien_kiem_khong_dem_hhdvu_trong_comment_cdata(xml_demo):
    raw = xml_demo.replace(
        b"</DSHHDVu>", b"<!--" + b"<HHDVu/>" * 1001 + b"--></DSHHDVu>"
    )
    raw = re.sub(
        b"<THHDVu>.*?</THHDVu>",
        b"<THHDVu><![CDATA[DEMO " + b"<HHDVu/>" * 1001 + b"]]></THHDVu>", raw, flags=re.S,
    )
    t, d, _ = thanh_cong(raw)
    assert t["so_dong"] == len(d["lines"]) == 1


def test_tien_kiem_dung_ngay_o_dong_1001_truoc_duoi_xml_hong():
    raw = b"<HDon>" + b"<HHDVu/>" * 1001 + b"<DEMO-DUOI-HONG"
    with pytest.raises(LoiNghiepVu) as exc:
        doc_xml(raw, tep_xml={})
    assert exc.value.ma == "HD_QUA_NHIEU_DONG_HANG"
