"""HD-3: fixture DEMO và oracle literal, không lấy expected từ parser."""

from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
import re

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.engine_legacy import Issue
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoa_don.chay import app
from e_hoa_don.doc import doc_xml
from e_hoa_don.hoa_don_xml import InvoiceIssue, doc_hoa_don_xml, ra_json

GOI = Path(__file__).resolve().parents[1] / "goi/e_hoa_don"
DEMO = Path(__file__).parent / "demo"
DAP_AN = json.loads((DEMO / "dap-an.json").read_text(encoding="utf-8"))
BAM = json.loads((DEMO / "bam-fixture.json").read_text(encoding="utf-8"))
CA = DAP_AN["ca"]
GOC_DONG = "/HDon/DLHDon/NDHDon/DSHHDVu/HHDVu"
GOC_TONG = "/HDon/DLHDon/NDHDon/TToan"


def chay(raw, *, mime="application/xml"):
    core = CoreGia()
    tep = core.them_tep("hoa-don-DEMO.xml", raw, mime)
    kq = core.chay_thu(app, "hoa_don.doc_xml@2", {"loai": "tep", "tep": tep})
    return core, tep, kq


def bao_cao(core, kq):
    return json.loads(core.doc_tep(kq["ket_qua"]["truong"]["chi_tiet_nguon"]["tep_id"]))


def kiem_fields(thuc, mong, goc):
    assert {f["name"] for f in thuc} == set(mong)
    for f in thuc:
        assert [[o["state"], o["lexeme"]] for o in f["occurrences"]] == mong[f["name"]]
        assert f["mixed_content"] is False
        assert f["locator"] == goc + "/" + f["name"]


@pytest.mark.parametrize("ca", CA, ids=lambda ca: ca["tep"])
def test_fixture_pin_va_du_18_truong_qua_coregia(ca):
    raw = (DEMO / ca["tep"]).read_bytes()
    assert raw == (GOI / "demo" / ca["tep"]).read_bytes()
    assert {"sha256": sha256(raw).hexdigest(), "bytes": len(raw)} == BAM[ca["tep"]]
    # Nhãn công ty nằm trong tài liệu, không thêm NBan/Ten ngoài allowlist.
    assert b"<Ten>" not in raw and b"\r" not in raw
    core, tep, kq = chay(raw)
    assert kq["trang_thai"] == "XONG", kq
    assert kq["ket_qua"]["loai"] == "truong"
    t = kq["ket_qua"]["truong"]
    assert len(t) == 18
    assert set(t) == {f["ma"] for f in app.phieu["nang_luc"][0]["truong_ra"]}
    mong = {**DAP_AN["chung"], **ca["truong"]}
    assert {k: t[k] for k in mong} == mong
    assert len(mong) == 14  # 4 trường còn lại kiểm độc lập bên dưới.
    assert t["tep_xml"] == tep and core.doc_tep(tep["tep_id"]) == raw
    assert t["bam_dau_vao"] == "sha256:" + BAM[ca["tep"]]["sha256"]
    ds = t["canh_bao"].splitlines()
    assert len(ds) == len(set(ds))
    assert {c.split(": ", 1)[0] for c in ds} == set(DAP_AN["canh_bao_chung"] + ca["canh_bao_them"])
    for c in ds:
        ma, cau = c.split(": ", 1)
        assert cau == {
            "CONTEXT_ABSENT": "Chưa có ngữ cảnh tin cậy để xác định hóa đơn.",
            "IDENTITY_UNRESOLVED": "Chưa xác định được định danh hóa đơn.",
            "HD_MONEY_HOLD": "Thông tin tiền nguồn còn cần kiểm tra.",
        }.get(ma, "Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.")
    ref = t["chi_tiet_nguon"]
    assert set(ref) == {"tep_id", "ten", "mime", "kich_thuoc"}
    assert ref["tep_id"] != tep["tep_id"]
    assert (ref["ten"], ref["mime"]) == ("hoa-don-chi-tiet.json", "application/json")
    assert ref["kich_thuoc"] == len(core.doc_tep(ref["tep_id"]))
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1


@pytest.mark.parametrize("ca", CA, ids=lambda ca: ca["tep"])
def test_json_nguon_co_dap_an_literal(ca):
    raw = (DEMO / ca["tep"]).read_bytes()
    with localcontext() as ctx:
        ctx.prec = 2
        core, tep, kq = chay(raw)
    assert kq["trang_thai"] == "XONG", kq
    b = bao_cao(core, kq)
    assert set(b) == {"phien_ban", "nguon_doc", "phien_ban_engine", "bam_dau_vao", "tep_xml", "chi_tiet_nguon", "van_de_phep_chieu"}
    assert b["phien_ban"] == 1 and b["tep_xml"] == tep
    assert b["nguon_doc"] == "xml_strict" and b["phien_ban_engine"] == "e_hoa_don 1.0.0"
    assert b["bam_dau_vao"] == "sha256:" + BAM[ca["tep"]]["sha256"]
    assert b["van_de_phep_chieu"] == []
    d = b["chi_tiet_nguon"]
    assert d["shape"] == "SUPPORTED_SUBSET"
    assert d["raw_ref"] == {
        "native_sha256": BAM[ca["tep"]]["sha256"], "byte_length": BAM[ca["tep"]]["bytes"],
        "media_type": "application/xml", "container_sha256": None, "entry_ordinal": None, "entry_name": None,
    }
    for cle in ("canonical_identity", "semantic_digest", "semantic_envelope"):
        assert d[cle] is None
    assert set(d["candidate_reasons"]) == {"CONTEXT_ABSENT", "CONTENT_OUTSIDE_SUPPORTED_ENVELOPE", "IDENTITY_UNRESOLVED"}
    assert d["native_fiscal_status"] == "UNKNOWN" and d["business_promotion"] == "NOT_PERFORMED"
    assert d["L11_eligibility"] == "NOT_EVALUATED"
    assert "raw_xml" not in d and "contract" not in b
    header = {**DAP_AN["header"], **ca["header"]}
    assert {f["name"] for f in d["header_fields"]} == set(header)
    for f in d["header_fields"]:
        goc = "/HDon/DLHDon/NDHDon" if "/MST" in f["name"] else "/HDon/DLHDon/TTChung"
        kiem_fields([f], {f["name"]: header[f["name"]]}, goc)
    assert len(d["lines"]) == 1
    dong = d["lines"][0]
    assert (dong["source_ordinal"], dong["source_locator"], dong["nature"]) == (1, GOC_DONG + "[1]", "GOODS")
    assert dong["logical_line_ref"] is dong["normalized_quantity_text"] is dong["unit_definition_ref"] is None
    assert dong["row_raw_sha256"] is None
    kiem_fields(dong["fields"], {**DAP_AN["dong"], "DGia": [["TEXT", ca["net"]]], "ThTien": [["TEXT", ca["net"]]]}, GOC_DONG + "[1]")
    for cle, so in (("quantity", "1"), ("unit_price", ca["net"]), ("source_amount", ca["net"])):
        assert dong[cle]["exact_value"] == dong[cle]["exact_text"] == so
    m = d["money"]
    assert m["state"] == ca["money_state"] and m["currency"] == "VND"
    for cle, so, state in (("net_amount", ca["net"], "PRECISION_UNDECLARED"), ("tax_amount", ca["thue"], "PRECISION_UNDECLARED"), ("total_amount", ca["tong"], ca["tong_state"]), ("non_taxable_amount", "0", "PRECISION_UNDECLARED")):
        assert (m[cle]["exact_value"], m[cle]["exact_text"], m[cle]["state"]) == (so, so, state)
    assert set(m["reasons"]) == ({"MONEY_ABSENT"} if ca["tong"] is None else set())
    mong = {"TgTCThue": [["TEXT", ca["net"]]], "TgTThue": [["TEXT", ca["thue"]]],
            "TgTTTBSo": [["ABSENT", None]] if ca["tong"] is None else [["TEXT", ca["tong"]]],
            "TGTKCThue": [["TEXT", "0"]], "DVTTe": [["TEXT", "VND"]]}
    assert {f["name"] for f in m["fields"]} == set(mong)
    for f in m["fields"]:
        kiem_fields([f], {f["name"]: mong[f["name"]]}, "/HDon/DLHDon/TTChung" if f["name"] == "DVTTe" else GOC_TONG)
    assert len(m["tax_components"]) == 1
    thue = m["tax_components"][0]
    assert thue["rate"] == "10%" and thue["source_locator"] == GOC_TONG + "/THTTLTSuat/LTSuat[1]"
    assert thue["net_amount"]["exact_value"] == ca["net"] and thue["tax_amount"]["exact_value"] == ca["thue"]
    kiem_fields(thue["fields"], {"TSuat": [["TEXT", "10%"]], "ThTien": [["TEXT", ca["net"]]], "TThue": [["TEXT", ca["thue"]]]}, GOC_TONG + "/THTTLTSuat/LTSuat[1]")
    assert d["relations"]["items"] == [] and d["relations"]["state"] == "ABSENT"


def test_manifest_chay_dung_ba_fixture_khong_cau_hinh():
    demo = app.phieu["chay_thu_demo"]
    assert len(demo) == 3
    assert {c["dau_vao"]["tep_demo"] for c in demo} == {"demo/" + c["tep"] for c in CA}
    assert all(c["nang_luc"] == "hoa_don.doc_xml@2" and c["tham_so"] == {} for c in demo)
    assert not app.phieu["bi_mat"]
    assert all(c["trang_thai"] == "XONG" for c in CoreGia().chay_thu_demo(app, GOI))


@pytest.mark.parametrize("mime", ["application/pdf", "text/plain", "application/zip", "application/octet-stream"])
def test_mime_sai_sdk_tu_choi_truoc_parser(mime, monkeypatch):
    import e_hoa_don.chay as cong
    def cam_parse(*args, **kwargs):
        raise AssertionError("Không được đọc sai MIME.")
    monkeypatch.setattr(cong, "doc_xml", cam_parse)
    core, _, kq = chay((DEMO / CA[0]["tep"]).read_bytes(), mime=mime)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert (kq["loi"]["ma"], kq["loi"]["thong_diep"]) == (
        "LOAI_TEP_KHONG_NHAN", "Loại tệp này không được bước này nhận (chỉ nhận: application/xml, text/xml).")
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("so_dong", [1000, 1001])
def test_bien_dong_fixture_sinh_trong_demo_tam(tmp_path, so_dong):
    raw = (DEMO / CA[0]["tep"]).read_bytes()
    dong = re.search(rb"<HHDVu>.*?</HHDVu>", raw, re.S)[0]
    raw = raw.replace(dong, dong * so_dong)
    thu_muc = tmp_path / "DEMO"
    thu_muc.mkdir()
    tep = thu_muc / "hoa-don-nhieu-dong-DEMO.xml"
    tep.write_bytes(raw)
    core, _, kq = chay(tep.read_bytes())
    if so_dong == 1001:
        assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
        assert (kq["loi"]["ma"], kq["loi"]["thong_diep"]) == (
            "HD_QUA_NHIEU_DONG_HANG", "Tệp XML vượt giới hạn 1.000 dòng hàng hóa. Anh hãy gửi tệp ít dòng hơn.")
        assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
        with pytest.raises(LoiNghiepVu) as exc:
            doc_xml(raw, tep_xml={})
        assert (exc.value.ma, exc.value.thong_diep) == (kq["loi"]["ma"], kq["loi"]["thong_diep"])
    else:
        assert kq["trang_thai"] == "XONG" and kq["ket_qua"]["truong"]["so_dong"] == 1000
        ds = bao_cao(core, kq)["chi_tiet_nguon"]["lines"]
        assert len(ds) == 1000
        for i, d in enumerate(ds, 1):
            assert (d["source_ordinal"], d["source_locator"], d["logical_line_ref"]) == (i, GOC_DONG + f"[{i}]", None)
            assert d["source_amount"]["exact_value"] == "1000000"


def test_thieu_ttoan_khong_suy_tong_tu_dong():
    raw = re.sub(rb"<TToan>.*?</TToan>", b"", (DEMO / CA[0]["tep"]).read_bytes(), flags=re.S)
    core, _, kq = chay(raw)
    assert kq["trang_thai"] == "XONG"
    t = kq["ket_qua"]["truong"]
    assert t["can_kiem_tra"] is True
    assert [t[k] for k in ("tien_truoc_thue", "tien_thue", "tong_thanh_toan")] == [None, None, None]
    d = bao_cao(core, kq)["chi_tiet_nguon"]
    assert d["money"]["state"] == "HOLD" and "MONEY_SECTION_ABSENT" in d["money"]["reasons"]
    assert d["semantic_digest"] is None


def test_dto_bat_bien_decimal_snapshot_va_issue_sdk():
    raw = (DEMO / "hoa-don-le-DEMO.xml").read_bytes()
    mutable = bytearray(raw)
    d = doc_hoa_don_xml(mutable)
    mutable[0] = 0
    assert d.raw_xml == raw and type(d.raw_xml) is bytes
    assert type(d.lines[0].unit_price.exact_value) is Decimal
    assert d.lines[0].unit_price.exact_value.as_tuple() == Decimal("1000000.123456").as_tuple()
    with pytest.raises(FrozenInstanceError):
        d.shape = "DEMO"
    copie = ra_json(d)
    copie["lines"][0]["fields"].clear()
    assert len(d.lines[0].fields) == 9
    source = InvoiceIssue("DEMO", "Dữ liệu giả.", "/DEMO", "WARNING")
    a, b = source.as_issue(), source.as_issue()
    assert type(a) is type(b) is Issue and a is not b
    a.message = "Đã sửa bản sao."
    assert b.message == source.message == "Dữ liệu giả."


@pytest.mark.parametrize("raw,ma,cau", [
    (b"<HDon>DEMO-CANARY", "HD_XML_KHONG_DOC_DUOC", "Không đọc được cấu trúc tệp XML hóa đơn."),
    (b"<HDon><TTChung/><NDHDon/></HDon>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<DEMO><HDon><DLHDon><TTChung/><NDHDon/></DLHDon></HDon></DEMO>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b'<HDon xmlns="urn:DEMO-CANARY"/>', "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<!DOCTYPE HDon SYSTEM 'file:///DEMO-CANARY'><HDon/>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b'<?xml version="1.0" encoding="latin-1"?><HDon/>', "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<HDon><DLHDon/><DLHDon/></HDon>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<HDon><DLHDon><TTChung/><TTChung/><NDHDon/></DLHDon></HDon>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
    (b"<HDon><DLHDon><TTChung/><NDHDon><DSHHDVu/><DSHHDVu/></NDHDon></DLHDon></HDon>", "HD_XML_NGOAI_PROFILE", "Tệp XML chưa thuộc phạm vi bộ đọc đang hỗ trợ."),
])
def test_loi_nghiep_vu_dung_lop_ma_cau_hd_1(raw, ma, cau, capsys):
    with pytest.raises(LoiNghiepVu) as exc:
        doc_xml(raw, tep_xml={"tep_id": "DEMO-opaque"})
    assert (exc.value.ma, exc.value.thong_diep) == (ma, cau)
    core, _, kq = chay(raw)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert (kq["loi"]["ma"], kq["loi"]["thong_diep"]) == (ma, cau)
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    output = capsys.readouterr()
    assert "DEMO-CANARY" not in output.out + output.err + json.dumps(kq["loi"])
