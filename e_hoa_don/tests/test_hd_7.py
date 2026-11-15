"""HD-7: oracle OOXML đọc độc lập và chuỗi đọc thật → XLSX qua CoreGia."""

from copy import deepcopy
from hashlib import sha256
import builtins
import io
import json
from pathlib import Path
import posixpath
import re
import threading
from types import SimpleNamespace
import zipfile
import xml.etree.ElementTree as ET

import pytest
from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu, Viec
from kho_tri_thuc_sdk.thu import CoreGia

import e_hoa_don.bang_ke as bk
import e_hoa_don.chay as cong
import e_hoa_don.xlsx_toi_thieu as xlsx
from test_hd_1 import thay
from test_hd_2 import GOI, kenh
from test_hd_5 import tao_zip

NL = "hoa_don.bang_ke_xlsx@1"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
HEAD = ["STT", "Thứ tự entry", "Tên entry", "Băm tệp", "Mẫu số", "Ký hiệu", "Số hóa đơn",
        "Ngày lập", "MST bán", "MST mua", "Tiền trước thuế", "Tiền thuế", "Tổng thanh toán",
        "Mã tiền tệ", "Cần kiểm tra", "Cảnh báo", "Trùng với thứ tự"]
KIEM_KE = ["Thứ tự entry", "Tên entry", "Băm tệp", "Trạng thái đọc", "Trùng tên",
           "Trùng với thứ tự", "Mã lỗi", "Cảnh báo"]
CB = ["TOTAL_SECTION_UNSUPPORTED: Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.",
      "UNIT_UNPROVEN: Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.",
      "CONTEXT_ABSENT: Chưa có ngữ cảnh tin cậy để xác định hóa đơn.",
      "CONTENT_OUTSIDE_SUPPORTED_ENVELOPE: Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.",
      "IDENTITY_UNRESOLVED: Chưa xác định được định danh hóa đơn."]


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def nguon(core, raw=None, zip=False):
    raw = raw if raw is not None else (GOI / "demo" / ("goi-hon-hop-DEMO.zip" if zip else "hoa-don-DEMO.xml")).read_bytes()
    tep = core.them_tep("DEMO.zip" if zip else "DEMO.xml", raw, "application/zip" if zip else "application/xml")
    kq = core.chay_thu(cong.app, "hoa_don.doc_zip@1" if zip else "hoa_don.doc_xml@2", {"loai": "tep", "tep": tep})
    assert kq["trang_thai"] == "XONG", kq
    return kq["ket_qua"]


def giao(core, data):
    return core.giao_viec(NL, data, gui_kem_dau_vao=False)


def xuat(core, data):
    kq = core.chay_thu(cong.app, NL, data)
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    return t, core.doc_tep(t["bang_ke"]["tep_id"])


def doc_xlsx(raw):
    """Không dùng hằng/helper writer; đọc XML, giải ST_Xstring trong một lượt."""
    def text(s):
        return re.sub(r"_x([0-9A-Fa-f]{4})_", lambda m: chr(int(m[1], 16)), s)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert len(z.namelist()) == len(set(z.namelist())) == 7
        trees = {n: ET.fromstring(z.read(n)) for n in z.namelist()}
        assert z.testzip() is None
    relns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    for path in ("_rels/.rels", "xl/_rels/workbook.xml.rels"):
        base = "" if path == "_rels/.rels" else "xl"
        ids = []
        for rel in trees[path].findall(relns + "Relationship"):
            ids.append(rel.attrib["Id"])
            assert "TargetMode" not in rel.attrib
            target = posixpath.normpath(posixpath.join(base, rel.attrib["Target"]))
            assert target in trees
        assert len(ids) == len(set(ids))
    assert {n.attrib["Id"]: (n.attrib["Type"], n.attrib["Target"])
            for n in trees["xl/_rels/workbook.xml.rels"]} == {
        "rId1": (R + "/worksheet", "worksheets/sheet1.xml"),
        "rId2": (R + "/worksheet", "worksheets/sheet2.xml"),
        "rId3": (R + "/styles", "styles.xml")}
    wb = trees["xl/workbook.xml"].findall("s:sheets/s:sheet", NS)
    assert [(s.attrib["name"], s.attrib["sheetId"], s.attrib[f"{{{R}}}id"]) for s in wb] == [
        ("Hoa don", "1", "rId1"), ("Kiem ke tep", "2", "rId2")]
    ct = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    overrides = {n.attrib["PartName"]: n.attrib["ContentType"] for n in trees["[Content_Types].xml"].findall(ct + "Override")}
    assert set(overrides) == {"/xl/workbook.xml", "/xl/styles.xml", "/xl/worksheets/sheet1.xml", "/xl/worksheets/sheet2.xml"}
    assert overrides["/xl/workbook.xml"].endswith("spreadsheetml.sheet.main+xml")
    formats = trees["xl/styles.xml"].findall("s:cellXfs/s:xf", NS)
    assert len(formats) >= 2 and all(f.attrib["numFmtId"] == "49" and f.attrib["applyNumberFormat"] == "1" for f in formats)
    assert formats[1].attrib["fontId"] != formats[0].attrib["fontId"]
    sheets = []
    for n, width, header in ((1, 17, 1), (2, 8, 14)):
        tree = trees[f"xl/worksheets/sheet{n}.xml"]
        pane = tree.find("s:sheetViews/s:sheetView/s:pane", NS)
        assert pane.attrib == dict(ySplit=str(header), topLeftCell=f"A{header + 1}", activePane="bottomLeft", state="frozen")
        cols = tree.findall("s:cols/s:col", NS)
        assert len(cols) == width
        assert [int(c.attrib["min"]) for c in cols] == list(range(1, width + 1))
        assert all(c.attrib["min"] == c.attrib["max"] and int(c.attrib["width"]) > 0 and c.attrib["customWidth"] == "1" for c in cols)
        assert [int(c.attrib["width"]) for c in cols] == ([8, 14, 32, 72, 16, 16, 18, 16, 20, 20, 26, 26, 26, 16, 16, 64, 20]
            if n == 1 else [14, 32, 72, 20, 14, 20, 36, 64])
        rows = []
        for row in tree.findall("s:sheetData/s:row", NS):
            values = []
            for i, c in enumerate(row, 1):
                assert c.attrib["t"] == "inlineStr"
                assert int(c.attrib["s"]) == (1 if int(row.attrib["r"]) == header else 0)
                assert c.find("s:f", NS) is None and c.find("s:v", NS) is None
                elem = c.find("s:is/s:t", NS)
                assert elem.attrib["{http://www.w3.org/XML/1998/namespace}space"] == "preserve"
                values.append(text(elem.text or ""))
            rows.append(values)
        assert tree.find("s:hyperlinks", NS) is None
        sheets.append(rows)
    assert sheets[0][0] == HEAD and sheets[1][13] == KIEM_KE
    return sheets, trees


def test_xml_oracle_doc_lai_tep_va_nguon(kenh):
    core, chay, _ = kenh
    data = nguon(core)
    ref = data["truong"]["chi_tiet_nguon"]
    raw_json = core.doc_tep(ref["tep_id"])
    vid = giao(core, data)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    assert set(t) == {"bang_ke", "chi_tiet_nguon", "so_hoa_don", "so_loi", "so_khong_ho_tro", "so_trung_noi_dung",
                      "da_doc_het", "can_kiem_tra", "canh_bao", "bam_dau_vao", "phien_ban_engine"}
    assert t["chi_tiet_nguon"] == ref and t["bam_dau_vao"] == bam(raw_json)
    assert [t[k] for k in ("so_hoa_don", "so_loi", "so_khong_ho_tro", "so_trung_noi_dung", "da_doc_het", "can_kiem_tra")] == [1, 0, 0, 0, True, True]
    assert t["bang_ke"]["ten"] == "hoa-don-bang-ke.xlsx" and t["bang_ke"]["mime"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    sheets, _ = doc_xlsx(core.doc_tep(t["bang_ke"]["tep_id"]))
    assert sheets[0][1] == ["1", "1", "DEMO.xml", "sha256:06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe",
        "1", "C26TAA", "0000123", "30/10/2026", "0100000001", "0100000002", "1000000", "100000", "1100000", "VND", "Có", "\n".join(CB), ""]
    assert sheets[1][14] == ["1", "DEMO.xml", sheets[0][1][3], "doc_duoc", "Không", "", "", "\n".join(CB)]
    assert sheets[1][0] == ["Không xác nhận đủ hóa đơn trong kỳ; chưa thực hiện ghi nhận nghiệp vụ"]
    assert sheets[1][4] == ["Băm JSON", bam(raw_json)]
    assert sheets[1][5] == ["Băm XML/ZIP", "sha256:06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe"]


@pytest.mark.parametrize("tag,column", [("TgTCThue", 10), ("TgTThue", 11), ("TgTTTBSo", 12)])
@pytest.mark.parametrize("lexeme,expected", [
    ("1000000.123456", "1000000.123456"), ("1000000.120000", "1000000.120000"),
    ("-1000000.120000", "-1000000.120000"), ("0", "0"), ("0.000000", "0.000000"),
    ("9007199254740993", "9007199254740993"), ("1000000000000000000.1234567", "1000000000000000000.1234567"),
    ("999999999999999999.999999", "999999999999999999.999999"), ("1.1234567", "1.1234567"),
    (None, ""), ("", ""), ("1,000", ""), ("1e6", ""), ("+1", ""), (" 1 ", ""),
])
def test_tien_exact_khong_float_round_null_empty(xml_demo, tag, column, lexeme, expected):
    core = CoreGia()
    data = nguon(core, thay(xml_demo, tag, lexeme))
    t, raw = xuat(core, data)
    sheets, _ = doc_xlsx(raw)
    assert sheets[0][1][column] == expected and sheets[0][1][13] == "VND"
    if expected == "":
        assert "HD_BANG_KE_TIEN" in t["canh_bao"]
    if lexeme in {"1000000000000000000.1234567", "1.1234567"}:
        assert "HOADON_MONEY_OVER_DOMAIN" in sheets[0][1][15]


@pytest.mark.parametrize("currency,expected", [(None, ""), ("", ""), ("vnd", ""), ("USD", "USD"), ("VND", "VND")])
def test_currency_khong_mac_dinh(xml_demo, currency, expected):
    core = CoreGia()
    t, raw = xuat(core, nguon(core, thay(xml_demo, "DVTTe", currency)))
    sheets, _ = doc_xlsx(raw)
    row = sheets[0][1]
    assert row[13] == expected and row[10:13] == (["1000000", "100000", "1100000"] if expected else ["", "", ""])
    if not expected:
        assert "HD_BANG_KE_CURRENCY" in t["canh_bao"]


def test_tong_lech_mo_ho_khong_tinh_lai(xml_demo):
    core = CoreGia()
    t, raw = xuat(core, nguon(core, thay(xml_demo, "TgTTTBSo", "9.120000")))
    sheets, _ = doc_xlsx(raw)
    assert sheets[0][1][10:13] == ["1000000", "100000", "9.120000"]
    assert "MONEY_TOTAL_CONFLICT" in t["canh_bao"] and t["can_kiem_tra"]
    raw_xml = xml_demo.replace(b"<TgTCThue>1000000</TgTCThue>", b"<TgTCThue>1</TgTCThue><TgTCThue>2</TgTCThue>")
    t, raw = xuat(core, nguon(core, raw_xml))
    assert doc_xlsx(raw)[0][0][1][10] == "" and "MONEY_AMBIGUOUS" in t["canh_bao"]


def test_zip_oracle_giu_loi_trung_thu_muc(kenh):
    core, chay, _ = kenh
    data = nguon(core, zip=True)
    vid = giao(core, data)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    sheets, _ = doc_xlsx(core.doc_tep(t["bang_ke"]["tep_id"]))
    assert [t[k] for k in ("so_hoa_don", "so_loi", "so_khong_ho_tro", "so_trung_noi_dung", "da_doc_het")] == [3, 1, 1, 1, False]
    assert [(r[0], r[1], r[2], r[6], r[16]) for r in sheets[0][1:]] == [
        ("1", "1", "z-DEMO.xml", "0000123", ""), ("2", "5", "trung-DEMO.xml", "0000123", "1"),
        ("3", "6", "trung-DEMO.xml", "0000124", "")]
    assert [(r[0], r[1], r[3], r[4], r[5], r[6]) for r in sheets[1][14:]] == [
        ("1", "z-DEMO.xml", "doc_duoc", "Không", "", ""), ("2", "thu-muc-DEMO/", "thu_muc", "Không", "", ""),
        ("3", "loi-DEMO.xml", "loi", "Không", "", "HD_ZIP_XML_HONG"),
        ("4", "DEMO.pdf", "khong_ho_tro", "Không", "", "HD_ZIP_KHONG_HO_TRO"),
        ("5", "trung-DEMO.xml", "doc_duoc", "Có", "1", ""), ("6", "trung-DEMO.xml", "doc_duoc", "Có", "", "")]
    xml = (GOI / "demo/hoa-don-DEMO.xml").read_bytes()
    assert [r[2] for r in sheets[1][14:]] == [bam(xml), "", bam(b"<HDon"), bam(b"%PDF-DEMO"), bam(xml), bam(xml.replace(b"0000123", b"0000124"))]
    assert "Có tệp lỗi/chưa hỗ trợ" in t["canh_bao"]


@pytest.mark.parametrize("entries", [[], [("DEMO/", b"")], [("DEMO.pdf", b"%PDF-DEMO")]])
def test_zip_khong_hoa_don_van_co_bao_cao(entries):
    core = CoreGia()
    t, raw = xuat(core, nguon(core, tao_zip(entries), zip=True))
    sheets, _ = doc_xlsx(raw)
    assert len(sheets[0]) == 1 and len(sheets[1]) == 14 + len(entries)
    assert t["so_hoa_don"] == 0 and t["da_doc_het"] is False


@pytest.mark.parametrize("start", ["=1+1", "+SUM(A1)", "-2+3", "@DEMO", "https://demo.invalid"])
def test_text_giong_formula_va_hyperlink_la_literal(xml_demo, start):
    core = CoreGia()
    raw_xml = thay(xml_demo, "KHHDon", start)
    t, raw = xuat(core, nguon(core, tao_zip([(start + ".xml", raw_xml)]), zip=True))
    sheets, _ = doc_xlsx(raw)
    # URL có // chỉ là metadata, ZIP không xem là đường máy; XML số và MST vẫn string.
    assert sheets[0][1][2] == start + ".xml" and sheets[0][1][5] == start


def doi_report(core, data, sua=None, raw=None):
    data = deepcopy(data)
    report = json.loads(core.doc_tep(data["truong"]["chi_tiet_nguon"]["tep_id"]))
    if sua:
        sua(report, data["truong"])
    raw = raw if raw is not None else json.dumps(report, ensure_ascii=False).encode()
    data["truong"]["chi_tiet_nguon"] = core.them_tep("DEMO.json", raw, "application/json")
    return data


@pytest.mark.parametrize("kind", ["version", "source", "hash", "binding", "shape", "header", "money", "ordinal", "state", "schema", "bool_version", "json_duplicate", "json_nan", "json_hong", "mixed"])
def test_sai_schema_tron_nguon_khong_xong(kind):
    core = CoreGia()
    data = nguon(core)
    def sua(r, t):
        if kind == "version": r["phien_ban"] = 2
        elif kind == "bool_version": r["phien_ban"] = True
        elif kind == "source": r["nguon_doc"] = "zip_xml_strict"
        elif kind == "hash": r["chi_tiet_nguon"]["raw_ref"]["native_sha256"] = "a" * 64
        elif kind == "binding": r["tep_xml"]["tep_id"] = "DEMO-sai"
        elif kind == "shape": r["chi_tiet_nguon"]["shape"] = "XML_MALFORMED"
        elif kind == "header": t["so_hoa_don"] = "0000999"
        elif kind == "money": r["chi_tiet_nguon"]["money"]["net_amount"]["exact_text"] = "2.0"
        elif kind == "ordinal": r["chi_tiet_nguon"]["lines"][0]["source_ordinal"] = 2
        elif kind == "state": r["chi_tiet_nguon"]["header_fields"][0]["occurrences"][0]["state"] = "EMPTY"
        elif kind == "schema": del r["chi_tiet_nguon"]["money"]["fields"]
        elif kind == "mixed": t["tep_zip"] = t["tep_xml"]
    raw = {"json_duplicate": b'{"phien_ban":1,"phien_ban":1}', "json_nan": b'{"x":NaN}', "json_hong": b'CANARY-DEMO-hong'}.get(kind)
    data = doi_report(core, data, sua, raw)
    before = core.so_lan_ghi["tep"]
    kq = core.chay_thu(cong.app, NL, data)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "HD_BANG_KE_DAU_VAO", kq
    assert kq["ket_qua"] is None and core.so_lan_ghi["tep"] == before


@pytest.mark.parametrize("kind", ["count", "outer_count", "ordinal", "binding", "entry_hash", "duplicate", "duplicate_name", "da_doc_het", "detail_null"])
def test_zip_sai_dem_binding_trung_khong_xong(kind):
    core = CoreGia()
    data = nguon(core, zip=True)
    def sua(r, t):
        if kind == "count": r["so_tep"] = 4
        elif kind == "outer_count": t["so_loi"] = 0
        elif kind == "ordinal": r["danh_sach_tep"][1]["thu_tu"] = 2
        elif kind == "binding": r["danh_sach_tep"][0]["truong_hoa_don"]["nguon"]["thu_tu"] = 3
        elif kind == "entry_hash": r["danh_sach_tep"][0]["bam"] = "sha256:" + "a" * 64
        elif kind == "duplicate": r["danh_sach_tep"][3]["trung_noi_dung_voi"] = 3
        elif kind == "duplicate_name": r["danh_sach_tep"][3]["trung_ten"] = False
        elif kind == "da_doc_het": r["da_doc_het"] = t["da_doc_het"] = True
        elif kind == "detail_null": r["danh_sach_tep"][0]["chi_tiet_nguon"] = None
    kq = core.chay_thu(cong.app, NL, doi_report(core, data, sua))
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "HD_BANG_KE_DAU_VAO", kq


@pytest.mark.parametrize("stage", [10, 60, 80, 100])
def test_huy_khong_xong(kenh, monkeypatch, stage):
    core, chay, _ = kenh
    data = nguon(core)
    before = core.so_lan_ghi["tep"]
    vid = giao(core, data)
    tien_do = core._tien_do
    def huy(ma, v, percent, cau):
        if percent == stage: core.huy(v)
        return tien_do(ma, v, percent, cau)
    monkeypatch.setattr(core, "_tien_do", huy)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert core.so_lan_ghi["tep"] == before + (stage == 100)


@pytest.mark.parametrize("status", [404, 409, 410])
@pytest.mark.parametrize("stage", [10, 60, 80, 100, "doc", "upload"])
def test_mat_lease_khong_nop(kenh, monkeypatch, status, stage):
    core, chay, _ = kenh
    vid = giao(core, nguon(core))
    before = core.so_lan_ghi["ket_qua"], core.so_lan_ghi["ket_thuc"]
    def hong(*a, **kw): raise LoiDuongTruyen("MAT_LEASE", "CANARY-DEMO", http_status=status)
    if stage in {"doc", "upload"}:
        monkeypatch.setattr(core, "_mo_tep" if stage == "doc" else "_tai_tep_ra", hong)
    else:
        real = core._tien_do
        monkeypatch.setattr(core, "_tien_do", lambda m, v, p, c: hong() if p == stage else real(m, v, p, c))
    chay()
    assert core.xem(vid)["trang_thai"] == "DANG_CHAY" and core.xem(vid)["ket_qua"] is None
    assert before == (core.so_lan_ghi["ket_qua"], core.so_lan_ghi["ket_thuc"])


@pytest.mark.parametrize("response", [None, {}, {"tep_id": ""}, {"tep_id": 1}, "loi"])
def test_upload_loi_thieu_tham_chieu_khong_xong(kenh, monkeypatch, response, capsys):
    core, chay, _ = kenh
    vid = giao(core, nguon(core))
    def hong(*a):
        if response == "loi": raise LoiDuongTruyen("UPLOAD_DEMO", "CANARY-DEMO", http_status=403)
        return response
    monkeypatch.setattr(core, "_tai_tep_ra", hong)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert "CANARY-DEMO" not in capsys.readouterr().err + json.dumps(kq["tien_do"]) + json.dumps(kq["loi"])


@pytest.mark.parametrize("op", ["tep", "ket_qua", "ket_thuc"])
def test_mat_ack_khong_upload_trung(kenh, op):
    core, chay, _ = kenh
    vid = giao(core, nguon(core))
    before = dict(core.so_lan_ghi)
    core.gay_mat_xac_nhan(op)
    chay()
    assert core.xem(vid)["trang_thai"] == "XONG"
    assert all(core.so_lan_ghi[k] == before[k] + 1 for k in ("tep", "ket_qua", "ket_thuc"))


@pytest.mark.parametrize("kind", ["json_metadata", "json_bytes", "entry", "rows", "cell", "xlsx", "timeout"])
def test_vuot_tran_khong_upload(kind, monkeypatch):
    core = CoreGia()
    data = nguon(core, zip=kind in {"entry", "rows"})
    if kind == "json_metadata": data["truong"]["chi_tiet_nguon"]["kich_thuoc"] = 32 * 1024 * 1024 + 1
    elif kind == "json_bytes":
        data = doi_report(core, data, raw=b" " * (32 * 1024 * 1024 + 1))
        data["truong"]["chi_tiet_nguon"]["kich_thuoc"] = 1
    elif kind in {"entry", "rows"}:
        data = doi_report(core, data, lambda r, t: r.update(danh_sach_tep=[r["danh_sach_tep"][0]] * 1001))
    elif kind == "cell":
        data["truong"]["tep_xml"]["ten"] = "D" * 16001
        data = doi_report(core, data, lambda r, t: r["tep_xml"].update(ten=t["tep_xml"]["ten"]))
    elif kind == "xlsx": monkeypatch.setattr(xlsx, "XLSX_TOI_DA", 1024)
    elif kind == "timeout": monkeypatch.setattr(bk, "THOI_HAN", -1)
    before = core.so_lan_ghi["tep"]
    kq = core.chay_thu(cong.app, NL, data)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "HD_BANG_KE_VUOT_GIOI_HAN", kq
    assert kq["ket_qua"] is None and core.so_lan_ghi["tep"] == before


def test_1000_entry_va_1000_dong_bien(xml_demo):
    core = CoreGia()
    raw_zip = tao_zip([(f"DEMO-{i}.xml", xml_demo) for i in range(1000)])
    t, raw = xuat(core, nguon(core, raw_zip, zip=True))
    sheets, _ = doc_xlsx(raw)
    assert t["so_hoa_don"] == 1000 and t["so_trung_noi_dung"] == 999
    assert len(sheets[0]) == 1001 and len(sheets[1]) == 1014
    assert sheets[0][-1][0:3] == ["1000", "1000", "DEMO-999.xml"]


def test_json_32mib_va_cell_16000_bien():
    core = CoreGia()
    data = nguon(core)
    data["truong"]["tep_xml"]["ten"] = "D" * 16000
    data = doi_report(core, data, lambda r, t: r["tep_xml"].update(ten=t["tep_xml"]["ten"]))
    source = core.doc_tep(data["truong"]["chi_tiet_nguon"]["tep_id"])
    raw = source + b" " * (32 * 1024 * 1024 - len(source))
    data = doi_report(core, data, raw=raw)
    t, out = xuat(core, data)
    assert t["bam_dau_vao"] == bam(raw) and len(doc_xlsx(out)[0][0][1][2]) == 16000


def test_xlsx_tran_bytes_thuc():
    buf = xlsx._BoDem()
    assert buf.write(b"D" * (32 * 1024 * 1024)) == 32 * 1024 * 1024
    with pytest.raises(LoiNghiepVu) as exc: buf.write(b"D")
    assert exc.value.ma == "HD_BANG_KE_VUOT_GIOI_HAN"


def test_escape_xml_control_va_escape_literal(xml_demo):
    core = CoreGia()
    name = '=DEMO<&"\x01\x0b\ufffe_x0001_\r\n.xml'
    t, raw = xuat(core, nguon(core, tao_zip([(name, xml_demo)]), zip=True))
    sheets, _ = doc_xlsx(raw)
    assert sheets[0][1][2] == sheets[1][14][1] == name


def test_khong_ghi_dia_khong_doc_xml_lai(monkeypatch):
    core = CoreGia()
    data = nguon(core)
    real_open = builtins.open
    def mo(file, mode="r", *a, **kw):
        assert not set(mode) & set("wax+"), "Không ghi tệp trong engine."
        return real_open(file, mode, *a, **kw)
    def cam(*a, **kw): raise AssertionError("Không được parse XML lại.")
    monkeypatch.setattr(builtins, "open", mo)
    monkeypatch.setattr(io, "open", mo)
    monkeypatch.setattr(cong, "doc_xml", cam)
    monkeypatch.setattr(cong, "doc_zip", cam)
    xuat(core, data)


def test_doi_chieu_tinh_cot_nguon_va_thiet_ke():
    root = Path(__file__).resolve().parents[1]
    cjs = (root / "ma-nguon/bang_ke.cjs").read_text("utf-8")
    config = (root / "ma-nguon/vendor/config.js").read_text("utf-8")
    # Cắt cả khối bằng marker tiếp theo, không chạy Node/require.
    keys = re.findall(r"\['([^']+)', '[^']+'\]", config.split("EXCEL_COLUMNS: [", 1)[1].split("// Cac truong", 1)[0])
    assert keys == ["_stt", "khmshdon", "khhdon", "shdon", "tdlap", "nbmst", "nbten", "nmmst", "nmten", "nmcccd", "tgtcthue", "tgtthue", "tgtttbso", "dvtte", "tthai"]
    dau = cjs.split("const DAU = {", 1)[1].split("};", 1)[0]
    assert re.findall(r"([a-z]+): '([^']+)'", dau) == [
        ("khmshdon", "mau_so"), ("khhdon", "ky_hieu"), ("shdon", "so_hoa_don"), ("tdlap", "ngay_lap"),
        ("nbmst", "ma_so_thue_ban"), ("nmmst", "ma_so_thue_mua"), ("dvtte", "don_vi_tien")]
    assert "const TONG = { tgtcthue: 'truoc_thue', tgtthue: 'thue', tgtttbso: 'thanh_toan' };" in cjs
    assert [x[0] for x in bk.COT_HOA_DON] == HEAD and [x[0] for x in bk.COT_KIEM_KE] == KIEM_KE
    # Cột chung giữ thứ tự tương đối; bỏ tên/CCCD/trạng thái thuế vì không có nguồn strict.
    retained = [k for k in keys if k not in {"nbten", "nmten", "nmcccd", "tthai"}]
    assert retained == ["_stt", "khmshdon", "khhdon", "shdon", "tdlap", "nbmst", "nmmst", "tgtcthue", "tgtthue", "tgtttbso", "dvtte"]
    docs = (root / "goi/e_hoa_don/NGUON.md").read_text("utf-8")
    for word in ("HD-7", "CD-096 A1", "nbten", "nmten", "nmcccd", "tthai", "Thứ tự entry", "Kiem ke tep"):
        assert word in docs


def test_manifest_khong_gia_fixture_truong():
    cap = cong.app.phieu["nang_luc"][2]
    assert cap["ma"] == NL and cap["nhan"] == ["truong"] and cap["tra"] == "truong"
    assert cap["gioi_han"] == dict(tep_toi_da_mib=32, mime=[], thoi_han_giay=600)
    assert cap["tham_so"] == [] and cap["huy_duoc"] is True
    assert not any(c["nang_luc"] == NL for c in cong.app.phieu["chay_thu_demo"])
    assert len(cong.app.phieu["chay_thu_demo"]) == 4


@pytest.mark.parametrize("stage", ["schema", "writer"])
@pytest.mark.parametrize("status", [None, 409])
def test_huy_mat_lease_trong_xu_ly_qua_gia_han(kenh, monkeypatch, stage, status):
    core, chay, _ = kenh
    vid = giao(core, nguon(core))
    before = dict(core.so_lan_ghi)
    event = threading.Event()
    def gia_han(*a):
        event.set()
        if status:
            raise LoiDuongTruyen("MAT_LEASE", "CANARY-DEMO", http_status=status)
        return {"huy": True}
    real_schema, real_writer = bk._schema, bk.tao_xlsx
    waited = []
    def cho(kiem):
        if not waited:
            waited.append(1)
            assert event.wait(3)
            # Closure kiem_tra giữ Viec; lấy trực tiếp qua closure thay sleep/race.
            viec = next(c.cell_contents for c in kiem.__closure__ if isinstance(c.cell_contents, Viec))
            assert viec._huy.wait(3)
        kiem()
    def schema(value, s, root, kiem):
        cho(kiem)
        return real_schema(value, s, root, kiem)
    def writer(*args):
        cho(args[-1])
        return real_writer(*args)
    monkeypatch.setattr(core, "_gia_han", gia_han)
    monkeypatch.setattr(bk, "_schema" if stage == "schema" else "tao_xlsx", schema if stage == "schema" else writer)
    chay(khoang_gia_han=0.01)
    kq = core.xem(vid)
    assert kq["trang_thai"] == ("DANG_CHAY" if status else "HUY") and kq["ket_qua"] is None
    assert core.so_lan_ghi["tep"] == before["tep"] and core.so_lan_ghi["ket_qua"] == before["ket_qua"]


def test_600_giay_dung_bien(monkeypatch):
    core = CoreGia()
    data = nguon(core)
    calls = []
    def now():
        calls.append(1)
        return 0 if len(calls) == 1 else 600
    monkeypatch.setattr(bk, "time", SimpleNamespace(monotonic=now))
    xuat(core, data)


@pytest.mark.parametrize("value", [None, [], {}, 1])
def test_nguon_doc_sai_kieu_tra_loi_nghiep_vu(value):
    core = CoreGia()
    data = nguon(core)
    data["truong"]["nguon_doc"] = value
    kq = core.chay_thu(cong.app, NL, data)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "HD_BANG_KE_DAU_VAO"


def test_bam_nguon_tham_chieu_bytes_thuc_co_trong_ho_so():
    root = GOI.parents[1]
    docs = (GOI / "NGUON.md").read_text("utf-8")
    for name in ("bang_ke.cjs", "vendor/config.js", "vendor/build.js", "NGUON.md"):
        raw = (root / "ma-nguon" / name).read_bytes()
        assert sha256(raw).hexdigest() in docs
        assert sha256(raw.replace(b"\r\n", b"\n")).hexdigest() in docs


def test_mst_formula_va_currency_mo_ho(xml_demo):
    core = CoreGia()
    raw_xml = thay(xml_demo, "MST", "=DEMO")
    _, raw = xuat(core, nguon(core, raw_xml))
    assert doc_xlsx(raw)[0][0][1][8:10] == ["=DEMO", "=DEMO"]
    raw_xml = xml_demo.replace(b"<DVTTe>VND</DVTTe>", b"<DVTTe>VND</DVTTe><DVTTe>USD</DVTTe>")
    t, raw = xuat(core, nguon(core, raw_xml))
    assert doc_xlsx(raw)[0][0][1][10:14] == ["", "", "", ""]
    assert "HD_BANG_KE_CURRENCY" in t["canh_bao"]


def test_bam_null_giu_ly_do_khong_bia(xml_demo):
    # Entry mã hóa là báo lỗi không đọc được, ordinal và lý do vẫn được xuất.
    from test_hd_5 import doi_central
    core = CoreGia()
    raw_zip = doi_central(tao_zip([("DEMO.xml", xml_demo)]), flag=1)
    t, raw = xuat(core, nguon(core, raw_zip, zip=True))
    sheets, _ = doc_xlsx(raw)
    assert len(sheets[0]) == 1 and t["so_loi"] == 1
    row = sheets[1][14]
    assert row[0:4] == ["1", "DEMO.xml", "", "loi"]
    assert row[6] == "HD_ZIP_ENTRY_KHONG_DOC_DUOC" and row[7]


@pytest.mark.parametrize("iso,expected", [("0001-01-02", "02/01/0001"), ("2026-02-30", ""), ("", "")])
def test_ngay_hien_thi_doc_lap_locale(xml_demo, iso, expected):
    core = CoreGia()
    _, raw = xuat(core, nguon(core, thay(xml_demo, "NLap", iso)))
    assert doc_xlsx(raw)[0][0][1][7] == expected
