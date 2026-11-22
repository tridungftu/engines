"""Kiểm DOCX DEMO bằng lõi thật và CoreGia; không AI/OCR hoặc mạng."""

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import struct
from types import SimpleNamespace
import zipfile

import pytest
from jsonschema import Draft202012Validator
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat import docx
from e_trich_xuat.chay import tao_app
from cong_sdk_cong_khai import duong_truyen_thu
from mau_docx import CT, NUM, REL, W_NS, bang_demo, goi_docx, mau_thuong, mau_track, o, p, so


GOI = Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"
SCHEMA = json.loads((GOI / "contract/van_ban_tai_lieu.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
BO_KIEM_SCHEMA = Draft202012Validator(SCHEMA)


def chay(raw, *, mime=docx.MIME_DOCX, sua_tep=None, core=None):
    core = CoreGia() if core is None else core
    app = tao_app()
    tep = core.them_tep("DEMO.docx", raw, mime)
    tep.update(sua_tep or {})
    kq = core.chay_thu(app, "trich.doc_docx@1", {"loai": "tep", "tep": tep})
    return kq, core


def doc(raw):
    kq, _ = chay(raw)
    assert kq["trang_thai"] == "XONG", kq
    BO_KIEM_SCHEMA.validate(kq["ket_qua"])
    return kq["ket_qua"]["van_ban_tai_lieu"]


def test_demo_sdk_phan_bo_dung_schema_va_khong_tu_cau_hinh():
    app, core = tao_app(), CoreGia()
    assert app.cac_nang_luc == ("trich.doc_docx@1", "trich.chuan_bi@1",
                              "trich.hau_kiem@1", "trich.xuat_ket_qua@1")
    assert core.xem_ngan(app.ma, "cau_hinh") == []
    from e_trich_xuat.demo import nap_ho_so_demo
    nap_ho_so_demo(core, app)
    ds = core.chay_thu_demo(app)
    assert len(ds) == 5
    for kq in ds[:2]:
        assert kq["trang_thai"] == "XONG"
        BO_KIEM_SCHEMA.validate(kq["ket_qua"])
    assert ds[2]["trang_thai"] == "XONG"  # Default do SDK điền, không ghi ngăn.
    assert all(kq["trang_thai"] == "XONG" for kq in ds[3:])
    assert core.xem_ngan(app.ma, "cau_hinh") == []
    assert core.xem_ngan(app.ma, "cau_hinh") == []
    assert (GOI / "demo/DEMO-hop-dong.docx").read_bytes() == mau_thuong()
    assert (GOI / "demo/DEMO-track-changes.docx").read_bytes() == mau_track()


def test_giu_thu_tu_o_rong_gop_va_so_tu_dong():
    raw = mau_thuong()
    kq = doc(raw)
    assert kq["nguon_doc"] == "docx"
    assert kq["so_trang"] == 0 and kq["trang"] == []
    assert kq["bam_dau_vao"] == "sha256:" + hashlib.sha256(raw).hexdigest()
    assert "Điều 1. Giá trị hợp đồng DEMO\n1.1. Giá trị là 1.000.000 VND" in kq["van_ban"]
    assert kq["van_ban"].endswith("Điều 2. Thanh toán DEMO\nKết thúc DEMO.")
    khoi = kq["khoi_docx"]
    assert [k["loai"] for k in khoi] == ["doan", "doan", "doan", "doan", "bang", "doan", "doan"]
    bang = khoi[4]
    assert bang["so_hang"] == bang["so_cot"] == 3
    assert len(bang["o"]) == 6
    assert bang["o"][1]["van_ban"] == ""
    gop = next(o for o in bang["o"] if o["hang"] == 1 and o["cot"] == 0)
    assert (gop["gop_hang"], gop["gop_cot"], gop["van_ban"]) == (2, 2, "Ô gộp DEMO")
    assert bang["van_ban"] == "Hạng mục DEMO |  | 1.000.000 VND\nÔ gộp DEMO |  | 2026-10-30\n |  | "
    assert khoi[3]["dieu"] == 1 and khoi[3]["khoan"] == "1.1."
    assert any("đoạn/Điều/Khoản" in c for c in kq["canh_bao"])

    def kiem(ds):
        for k in ds:
            assert kq["van_ban"][k["bat_dau"]:k["ket_thuc"]] == k["van_ban"]
            assert "hop" not in k and "so_trang" not in k
            if k["loai"] == "bang":
                for cell in k["o"]:
                    assert kq["van_ban"][cell["bat_dau"]:cell["ket_thuc"]] == cell["van_ban"]
                    kiem(cell["khoi"])
    kiem(khoi)


def test_track_changes_alias_namespace_accept_all_va_bam_goc():
    raw = mau_track()
    kq = doc(raw)
    assert "cũ" not in kq["van_ban"]
    assert "Giá trị DEMO mới: 1.000.000 VND." in kq["van_ban"]
    assert kq["so_sua_doi_da_chap_nhan"] == 2
    assert kq["bam_dau_vao"] == "sha256:" + hashlib.sha256(raw).hexdigest()
    assert raw == mau_track()


def test_accept_all_noi_nhieu_dau_doan_xoa_giu_noi_dung_chen_di_chuyen_va_xoa_dong():
    xoa_pr = '<w:pPr><w:rPr><w:del/></w:rPr></w:pPr>'
    noi = (p("DEMO A", xoa_pr) + p(" DEMO B", xoa_pr) + p(" DEMO C")
           + '<w:p><w:moveFrom><w:r><w:t>DEMO cũ</w:t></w:r></w:moveFrom>'
           + '<w:moveTo><w:r><w:t>DEMO mới</w:t></w:r></w:moveTo></w:p>'
           + '<w:tbl><w:tr><w:trPr><w:del/></w:trPr>' + o("DEMO dòng xóa") + "</w:tr>"
           + "<w:tr>" + o("DEMO dòng giữ") + "</w:tr></w:tbl>")
    kq = doc(goi_docx(noi))
    assert kq["van_ban"] == "DEMO A DEMO B DEMO C\nDEMO mới\nDEMO dòng giữ"


def test_o_xoa_va_dinh_dang_cu_khong_chen_noi_dung_cu():
    pr = '<w:pPr><w:pPrChange><w:pPr><w:numPr><w:numId w:val="99"/></w:numPr></w:pPr></w:pPrChange></w:pPr>'
    raw = goi_docx(p("DEMO còn", pr) + "<w:tbl><w:tr>" + o("DEMO bỏ", "<w:cellDel/>")
                   + o("DEMO giữ") + "</w:tr></w:tbl>")
    assert doc(raw)["van_ban"] == "DEMO còn\nDEMO giữ"


def test_noi_dau_doan_xoa_qua_bien_chen_va_content_control_trong_bang():
    pr = '<w:pPr><w:rPr><w:del/></w:rPr></w:pPr>'
    noi = '<w:ins>' + p("DEMO trước", pr) + '</w:ins>' + p(" DEMO sau")
    bang = ('<w:tbl><w:sdt><w:sdtContent><w:tr><w:sdt><w:sdtContent>'
            + o("DEMO ô có content control") + '</w:sdtContent></w:sdt></w:tr></w:sdtContent></w:sdt></w:tbl>')
    assert doc(goi_docx(noi + bang))["van_ban"] == "DEMO trước DEMO sau\nDEMO ô có content control"


def test_nhieu_dau_doan_xoa_khong_cat_ngam_noi_dung():
    pr = '<w:pPr><w:rPr><w:del/></w:rPr></w:pPr>'
    raw = goi_docx(p("D", pr) * 500 + p("DEMO cuối"), nen=zipfile.ZIP_STORED)
    assert doc(raw)["van_ban"] == "D" * 500 + "DEMO cuối"


def test_toan_bo_dong_bang_bi_xoa_khong_con_noi_dung_cu():
    raw = goi_docx(p("DEMO trước") + '<w:tbl><w:tr><w:trPr><w:del/></w:trPr>'
                   + o("DEMO dòng xóa") + '</w:tr></w:tbl>' + p("DEMO sau"))
    kq = doc(raw)
    assert "dòng xóa" not in kq["van_ban"]
    assert kq["khoi_docx"][1]["so_hang"] == 0


def test_danh_sach_rieng_style_va_start_override():
    styles = f'<w:styles xmlns:w="{W_NS}"><w:style w:styleId="S"><w:pPr><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr></w:style><w:style w:styleId="T"><w:basedOn w:val="S"/></w:style></w:styles>'
    num = NUM.replace('<w:num w:numId="2"><w:abstractNumId w:val="0"/></w:num>',
                      '<w:num w:numId="2"><w:abstractNumId w:val="0"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="5"/></w:lvlOverride></w:num>')
    raw = goi_docx(so("DEMO A", nid=1) + so("DEMO B", nid=2)
                   + p("DEMO C", '<w:pPr><w:pStyle w:val="T"/></w:pPr>')
                   + so("DEMO D", muc=1) + so("DEMO E") + so("DEMO F", muc=1),
                   numbering=num, styles=styles)
    assert doc(raw)["van_ban"].splitlines() == ["Điều 1. DEMO A", "Điều 5. DEMO B", "Điều 2. DEMO C",
                                               "2.1. DEMO D", "Điều 3. DEMO E", "3.1. DEMO F"]


@pytest.mark.parametrize("fmt,nhan", [("upperRoman", "I"), ("lowerLetter", "a"), ("decimalZero", "01")])
def test_dinh_dang_so(fmt, nhan):
    num = NUM.replace('w:val="decimal"', f'w:val="{fmt}"').replace("Điều %1.", "%1.")
    assert doc(goi_docx(so("DEMO"), numbering=num))["van_ban"] == nhan + ". DEMO"


def test_o_gop_ngang_cu_bang_long_va_khoi_sdt_giu_unicode_khoang_trang():
    bang = '<w:tbl><w:tr>' + o("DEMO A", '<w:hMerge w:val="restart"/>') + o("DEMO B", '<w:hMerge/>') + '</w:tr></w:tbl>'
    long = '<w:tbl><w:tr><w:tc>' + p("DEMO trước") + bang + p("DEMO sau") + '</w:tc></w:tr></w:tbl>'
    raw = goi_docx('<w:sdt><w:sdtContent>' + p("  DEMO 😀 a\u0301  ") + '</w:sdtContent></w:sdt>' + long + p())
    kq = doc(raw)
    assert kq["van_ban"].startswith("  DEMO 😀 a\u0301  \nDEMO trước\nDEMO A\nDEMO B | ")
    assert kq["van_ban"].endswith("DEMO sau\n")
    assert kq["khoi_docx"][1]["o"][0]["khoi"][1]["o"][0]["gop_cot"] == 2


@pytest.mark.parametrize("raw", [b"DEMO khong phai ZIP", goi_docx(raw_xml="<DEMO>"),
    goi_docx(them={"[Content_Types].xml": CT.replace("document.main+xml", "template.main+xml")}),
    goi_docx(them={"_rels/.rels": REL.replace('Target="word/document.xml"', 'Target="https://demo.invalid/a" TargetMode="External"')}),
    goi_docx(so("DEMO")), goi_docx(them={"../DEMO.txt": b"DEMO"})])
def test_hong_sai_cau_truc_va_path_tra_loi_an_toan(raw):
    kq, _ = chay(raw)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "DOCX_KHONG_HOP_LE"
    assert kq["loi"]["thong_diep"] == docx.CAU_DOCX_LOI
    assert kq["ket_qua"] is None


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
def test_dtd_va_entity_bi_chan(encoding):
    raw_xml = (f'<?xml version="1.0" encoding="{encoding}"?>'
               '<!DOCTYPE x [<!ENTITY demo "DEMO KHONG DUOC MO RONG">]>'
               f'<w:document xmlns:w="{W_NS}"><w:body><w:p><w:r><w:t>&demo;</w:t></w:r></w:p></w:body></w:document>')
    kq, _ = chay(goi_docx(raw_xml=raw_xml.encode(encoding)))
    assert kq["loi"]["ma"] == "DOCX_KHONG_HOP_LE"


def test_sai_mime_va_sai_duoi_khong_duoc_doc_nham():
    kq, _ = chay(mau_thuong(), mime="application/pdf")
    assert kq["loi"] == {"ma": "LOAI_TEP_KHONG_NHAN", "thong_diep":
        "Loại tệp này không được bước này nhận (chỉ nhận: " + docx.MIME_DOCX + ").", "thu_lai_duoc": False}
    # MIME là nguồn quyết định, tên tệp không được dùng để suy đoán dữ liệu.
    assert chay(mau_thuong(), sua_tep={"ten": "DEMO.pdf"})[0]["trang_thai"] == "XONG"


@pytest.mark.parametrize("loai", ["khai_bao", "bytes_that", "khai_bao_thieu"])
def test_tran_20_mib_va_kich_thuoc_thuc(loai):
    if loai == "khai_bao":
        raw, sua = mau_thuong(), {"kich_thuoc": docx.TEP_TOI_DA + 1}
    elif loai == "bytes_that":
        raw, sua = b"D" * (docx.TEP_TOI_DA + 1), {"kich_thuoc": 10}
    else:
        raw, sua = mau_thuong(), {"kich_thuoc": 1}
    kq, _ = chay(raw, sua_tep=sua)
    ma = "DOCX_KHONG_HOP_LE" if loai == "khai_bao_thieu" else "VUOT_GIOI_HAN"
    assert kq["loi"]["ma"] == ma
    cau = ("Tệp lớn hơn 20 MiB, bước này không nhận." if loai == "khai_bao"
           else docx.CAU_DOCX_LOI if ma == "DOCX_KHONG_HOP_LE" else "Tệp lớn hơn giới hạn bước này nhận.")
    assert kq["loi"]["thong_diep"] == cau


def test_xml_zip_vuot_tran_bi_tu_choi_truoc_mo_xml(monkeypatch):
    raw = bytearray(goi_docx())
    pos = raw.find(b"PK\x01\x02")
    struct.pack_into("<I", raw, pos + 24, docx.XML_TOI_DA + 1)
    monkeypatch.setattr(zipfile.ZipFile, "open", lambda *a, **k: pytest.fail("Không được giải nén trước kiểm trần"))
    with pytest.raises(LoiNghiepVu) as exc:
        docx.doc_bytes(bytes(raw), lambda: None, lambda *a: None, phien_ban_engine="DEMO")
    assert exc.value.ma == "VUOT_GIOI_HAN"


@pytest.mark.parametrize("gioi_han,gia_tri", [("GIAI_NEN_TOI_DA", 100), ("SO_MUC_ZIP_TOI_DA", 2),
    ("TY_LE_NEN_TOI_DA", 1), ("SO_NUT_XML_TOI_DA", 4), ("DO_SAU_XML_TOI_DA", 3),
    ("KY_TU_TOI_DA", 2), ("SO_COT_TOI_DA", 2), ("SO_O_TOI_DA", 2), ("JSON_TOI_DA", 100)])
def test_moi_tran_deu_tu_choi_khong_cat_ngam(monkeypatch, gioi_han, gia_tri):
    monkeypatch.setattr(docx, gioi_han, gia_tri)
    kq, _ = chay(mau_thuong())
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "VUOT_GIOI_HAN"


def test_huy_giua_doc_xml_va_cac_chang_khong_nop_ket_qua(monkeypatch):
    for moc in [5, 25, 45, 65, 100]:
        core = CoreGia()
        dt = duong_truyen_thu(core, monkeypatch)
        goc = dt.tien_do

        def bao(viec, phan_tram, cau):
            if phan_tram == moc:
                core.huy(viec)
            return goc(viec, phan_tram, cau)

        monkeypatch.setattr(dt, "tien_do", bao)
        kq, _ = chay(mau_thuong(), core=core)
        assert kq["trang_thai"] == "HUY"
        assert core.so_lan_ghi["ket_qua"] == 0
    dem = 0

    def kiem():
        nonlocal dem
        dem += 1
        if dem == 20:
            raise ViecDaHuy()

    with pytest.raises(ViecDaHuy):
        docx.doc_bytes(goi_docx(p("DEMO") * 400, nen=zipfile.ZIP_STORED), kiem,
                       lambda *a: None, phien_ban_engine="DEMO")


def test_mat_ack_khong_nop_trung_khong_ghi_tep(monkeypatch):
    core = CoreGia()
    core.gay_mat_xac_nhan("ket_qua")
    core.gay_mat_xac_nhan("ket_thuc")
    app = tao_app()
    tep = core.them_tep("DEMO.docx", mau_thuong(), docx.MIME_DOCX)
    monkeypatch.setattr(Path, "write_bytes", lambda *a, **k: pytest.fail("Runtime không được ghi tệp"))
    monkeypatch.setattr(Path, "write_text", lambda *a, **k: pytest.fail("Runtime không được ghi tệp"))
    import builtins
    import socket
    monkeypatch.setattr(builtins, "open", lambda *a, **k: pytest.fail("Runtime không được mở tệp đĩa"))
    monkeypatch.setattr(socket, "socket", lambda *a, **k: pytest.fail("Không được gọi mạng"))
    kq = core.chay_thu(app, "trich.doc_docx@1", {"loai": "tep", "tep": tep})
    assert kq["trang_thai"] == "XONG"
    assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1
    assert core.so_lan_ghi["tep"] == 0


def test_docx_khong_luu_ban_goc_sau_khi_loi_hoac_huy():
    raw = mau_track()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        truoc = z.read("word/document.xml")
    doc(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.read("word/document.xml") == truoc


def test_canh_bao_vung_khong_doc_va_khong_gia_ocr():
    raw = goi_docx(p("DEMO") + '<w:p><w:r><w:drawing/></w:r></w:p><w:altChunk/>',
                   them={"word/header1.xml": b"DEMO", "word/footnotes.xml": b"DEMO"})
    kq = doc(raw)
    assert len(kq["canh_bao"]) == 4
    assert kq["trang"] == []


def test_log_sdk_khong_lo_traceback_noi_dung_ho_so(monkeypatch, capsys):
    bi_mat = "DEMO nội dung tài liệu không được ghi log"
    def hong(*a, **k):
        raise RuntimeError(bi_mat)
    monkeypatch.setattr(docx, "doc_docx", hong)
    capsys.readouterr()
    kq, _ = chay(mau_thuong())
    err = capsys.readouterr().err
    assert bi_mat not in err + str(kq) and "Traceback" not in err
    assert kq["loi"]["ma"] == "ENGINE_LOI_XU_LY" and "RuntimeError" in err
