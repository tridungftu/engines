"""HD-5: ZIP DEMO trong RAM, oracle độc lập và đầu vào cố tình sai."""

import builtins
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import stat
import struct
import warnings
import zipfile

import pytest
from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.primitives import DataError

import e_hoa_don.hoa_don_xml as loi
import e_hoa_don.zip as cong

GOI = Path(__file__).resolve().parents[1] / "goi/e_hoa_don"
TEP = {"tep_id": "DEMO-zip", "ten": "goi-DEMO.zip", "mime": "application/zip", "kich_thuoc": 1}


def tao_zip(entries, method=zipfile.ZIP_STORED):
    buffer = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # tên trùng có chủ ý
        with zipfile.ZipFile(buffer, "w", compression=method) as z:
            for name, data in entries:
                info = name if isinstance(name, zipfile.ZipInfo) else zipfile.ZipInfo(name, (2026, 10, 30, 0, 0, 0))
                if isinstance(name, str):
                    info.filename = info.orig_filename = name  # giữ bytes tên backslash trên Windows
                info.compress_type = method
                z.writestr(info, data)
    return buffer.getvalue()


def doc(raw, **kwargs):
    t, data = cong.doc_zip(raw, tep_zip=TEP, **kwargs)
    return t, json.loads(data)


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def doi_central(raw, ordinal=1, **values):
    """Sửa bytes header độc lập với reader để dựng metadata giả DEMO."""
    raw = bytearray(raw)
    pos, found = 0, []
    while True:
        pos = raw.find(b"PK\x01\x02", pos)
        if pos < 0:
            break
        found.append(pos)
        name, extra, comment = struct.unpack_from("<HHH", raw, pos + 28)
        pos += 46 + name + extra + comment
    pos = found[ordinal - 1]
    for key, value in values.items():
        offset, fmt = {"flag": (8, "H"), "method": (10, "H"), "crc": (16, "I"),
                       "compressed": (20, "I"), "size": (24, "I"), "offset": (42, "I")}[key]
        struct.pack_into("<" + fmt, raw, pos + offset, value)
    return bytes(raw)


def vuot(raw, **kwargs):
    with pytest.raises(LoiNghiepVu) as exc:
        doc(raw, **kwargs)
    assert (exc.value.ma, exc.value.thong_diep) == (
        "HD_ZIP_VUOT_GIOI_HAN", "Gói ZIP vượt giới hạn xử lý. Anh hãy gửi gói nhỏ hơn.")


def test_goi_hon_hop_oracle_thu_tu_bam_trung_va_tien(xml_demo):
    khac = xml_demo.replace(b"0000123", b"0000124")
    entries = [("z-DEMO.xml", xml_demo), ("thu-muc/", b""), ("a-hong.xml", b"<HDon"),
               ("DEMO.pdf", b"%PDF-DEMO"), ("trung.xml", xml_demo), ("trung.xml", khac),
               ("ban-sao.pdf", b"%PDF-DEMO"), ("ngoai.xml", b'<HDon xmlns="urn:DEMO"/>')]
    raw = tao_zip(entries)
    t, r = doc(raw)
    expected = [
        (1, "z-DEMO.xml", "doc_duoc", False, None, None),
        (3, "a-hong.xml", "loi", False, None, "HD_ZIP_XML_HONG"),
        (4, "DEMO.pdf", "khong_ho_tro", False, None, "HD_ZIP_KHONG_HO_TRO"),
        (5, "trung.xml", "doc_duoc", True, 1, None),
        (6, "trung.xml", "doc_duoc", True, None, None),
        (7, "ban-sao.pdf", "khong_ho_tro", False, 4, "HD_ZIP_KHONG_HO_TRO"),
        (8, "ngoai.xml", "khong_ho_tro", False, None, "HD_ZIP_XML_NGOAI_PROFILE"),
    ]
    ds = r["danh_sach_tep"]
    assert [tuple(e[k] for k in ("thu_tu", "ten", "trang_thai_doc", "trung_ten", "trung_noi_dung_voi", "ma_loi")) for e in ds] == expected
    assert r["danh_sach_thu_muc"] == [{"thu_tu": 2, "ten": "thu-muc/", "trung_ten": False, "canh_bao": []}]
    assert {k: t[k] for k in ("so_tep", "so_doc_duoc", "so_loi", "so_khong_ho_tro", "so_trung_noi_dung")} == {
        "so_tep": 7, "so_doc_duoc": 3, "so_loi": 1, "so_khong_ho_tro": 3, "so_trung_noi_dung": 2,
    }
    assert t["da_doc_het"] is r["da_doc_het"] is False
    assert t["can_kiem_tra"] is True and "đầy đủ" not in t["canh_bao"]
    assert t["tep_zip"] == r["tep_zip"] == TEP and t["chi_tiet_nguon"] is None
    assert r["bam_dau_vao"] == t["bam_dau_vao"] == bam(raw)
    for e in ds:
        content = entries[e["thu_tu"] - 1][1]
        assert (e["bam"], e["kich_thuoc"]) == (bam(content), len(content))
        assert e["can_kiem_tra"] is True
        if e["trang_thai_doc"] != "doc_duoc":
            assert e["truong_hoa_don"] is None
            continue
        fields, detail = e["truong_hoa_don"], e["chi_tiet_nguon"]
        assert fields["so_hoa_don"] == ("0000124" if e["thu_tu"] == 6 else "0000123")
        assert fields["ngay_lap"] == "2026-10-30" and fields["so_dong"] == 1
        assert fields["tien_truoc_thue"] == {"so": "1000000", "tien_te": "VND"}
        assert fields["tien_thue"] == {"so": "100000", "tien_te": "VND"}
        assert fields["tong_thanh_toan"] == {"so": "1100000", "tien_te": "VND"}
        assert "tep_xml" not in fields and "tep_id" not in fields
        assert fields["nguon"] == {"tep_zip": TEP, "bam_goi": bam(raw), "thu_tu": e["thu_tu"], "ten": e["ten"], "bam": e["bam"]}
        assert detail["raw_ref"] == {"native_sha256": sha256(content).hexdigest(), "byte_length": len(content),
                                     "media_type": "application/xml", "container_sha256": sha256(raw).hexdigest(),
                                     "entry_ordinal": e["thu_tu"], "entry_name": e["ten"]}
        assert detail["lines"][0]["source_ordinal"] == 1
        assert detail["lines"][0]["source_locator"] == "/HDon/DLHDon/NDHDon/DSHHDVu/HHDVu[1]"
        assert detail["lines"][0]["source_amount"]["exact_value"] == "1000000"
        assert detail["canonical_identity"] is detail["semantic_digest"] is detail["source_instance"] is None
        assert "CONTEXT_ABSENT" in detail["candidate_reasons"]
        assert detail["native_fiscal_status"] == r["native_fiscal_status"] == "UNKNOWN"
        assert detail["business_promotion"] == r["business_promotion"] == "NOT_PERFORMED"
    assert r["do_du_ky_tai"] == "UNKNOWN"


@pytest.mark.parametrize("entries,files,dirs", [([], 0, 0), ([("DEMO/", b"")], 0, 1),
    ([("z/", b""), ("a/", b"")], 0, 2), ([("DEMO.pdf", b"%PDF-DEMO")], 1, 0)])
def test_rong_thu_muc_khong_suy_doc_het(entries, files, dirs):
    t, r = doc(tao_zip(entries))
    assert t["da_doc_het"] is False and t["can_kiem_tra"] is True
    assert (t["so_tep"], t["so_doc_duoc"]) == (files, 0)
    assert len(r["danh_sach_thu_muc"]) == dirs
    assert "Gói không có tệp hóa đơn đọc được." in r["canh_bao"]


@pytest.mark.parametrize("method", [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])
def test_doc_het_chi_nghia_doc_tap_hien_tai_va_giu_trung(xml_demo, method):
    t, r = doc(tao_zip([("z.xml", xml_demo), ("a.xml", xml_demo)], method))
    assert (t["so_tep"], t["so_doc_duoc"], t["so_trung_noi_dung"]) == (2, 2, 1)
    assert t["da_doc_het"] is True and t["can_kiem_tra"] is True
    assert r["do_du_ky_tai"] == "UNKNOWN"
    assert [e["thu_tu"] for e in r["danh_sach_tep"]] == [1, 2]


@pytest.mark.parametrize("ten", ["../DEMO.xml", "a/../DEMO.xml", "/DEMO.xml", "C:/DEMO.xml", "C:DEMO.xml", "\\\\DEMO\\DEMO.xml", "..\\DEMO.xml"])
def test_ten_nguy_hiem_chi_metadata_khong_parse(xml_demo, monkeypatch, ten):
    raw = tao_zip([(ten, xml_demo)])
    monkeypatch.setattr(loi, "_doc", lambda *a: pytest.fail("Không được parse tên nguy hiểm."))
    t, r = doc(raw)
    e = r["danh_sach_tep"][0]
    assert (e["ten"], e["trang_thai_doc"], e["ma_loi"], e["bam"]) == (ten, "khong_ho_tro", "HD_ZIP_TEN_KHONG_AN_TOAN", bam(xml_demo))
    assert ten not in t["canh_bao"] and t["da_doc_het"] is False


def test_symlink_zip_long_va_non_xml_khong_parse(xml_demo, monkeypatch):
    info = zipfile.ZipInfo("lien-ket.xml")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    nested = tao_zip([("DEMO.xml", xml_demo)])
    raw = tao_zip([(info, xml_demo), ("long.xml", nested), ("DEMO.zip", nested), ("DEMO.pdf", b"%PDF-DEMO"), ("DEMO.txt", b"DEMO")])
    monkeypatch.setattr(loi, "_doc", lambda *a: pytest.fail("Không được parse non-XML, ZIP lồng hoặc symlink."))
    _, r = doc(raw)
    assert [e["ma_loi"] for e in r["danh_sach_tep"]] == ["HD_ZIP_SYMLINK", "HD_ZIP_LONG", "HD_ZIP_LONG", "HD_ZIP_KHONG_HO_TRO", "HD_ZIP_KHONG_HO_TRO"]
    assert all(e["bam"] is not None for e in r["danh_sach_tep"])


def test_trung_ten_nfc_casefold_khong_gop_khac_bytes(xml_demo):
    entries = [("DEMO-É.xml", xml_demo), ("demo-e\u0301.XML", xml_demo.replace(b"0000123", b"0000124")),
               ("DEMO-É.xml", xml_demo)]
    t, r = doc(tao_zip(entries))
    ds = r["danh_sach_tep"]
    assert [e["ten"] for e in ds] == [n for n, _ in entries]
    assert [e["trung_ten"] for e in ds] == [True, True, True]
    assert [e["trung_noi_dung_voi"] for e in ds] == [None, None, 1]
    assert [e["trang_thai_doc"] for e in ds] == ["doc_duoc"] * 3
    assert t["so_doc_duoc"] == 3 and t["so_trung_noi_dung"] == 1


@pytest.mark.parametrize("raw,code,state", [
    (b"<HDon", "HD_ZIP_XML_HONG", "loi"),
    (b"<x/>", "HD_ZIP_XML_NGOAI_PROFILE", "khong_ho_tro"),
    (b'<HDon xmlns="urn:DEMO"/>', "HD_ZIP_XML_NGOAI_PROFILE", "khong_ho_tro"),
    (b'<?xml version="1.0" encoding="ISO-8859-1"?><HDon/>', "HD_ZIP_XML_NGOAI_PROFILE", "khong_ho_tro"),
    ('<HDon/>'.encode('utf-16'), "HD_ZIP_XML_NGOAI_PROFILE", "khong_ho_tro"),
    (b'<HDon>\xff</HDon>', "HD_ZIP_XML_NGOAI_PROFILE", "khong_ho_tro"),
    (b'<!DOCTYPE HDon [<!ENTITY DEMO "DEMO">]><HDon>&DEMO;</HDon>', "HD_ZIP_XML_NGOAI_PROFILE", "khong_ho_tro"),
])
def test_xml_loi_ngoai_profile_van_co_bam(raw, code, state):
    t, r = doc(tao_zip([("DEMO.xml", raw)]))
    e = r["danh_sach_tep"][0]
    assert (e["trang_thai_doc"], e["ma_loi"], e["bam"], e["kich_thuoc"]) == (state, code, bam(raw), len(raw))
    assert e["truong_hoa_don"] is None and t["da_doc_het"] is False


@pytest.mark.parametrize("bad", ["crc", "encrypted", "method", "offset", "truncated", "size_short", "size_long"])
def test_entry_doc_thieu_bam_null_giu_entry_va_tiep_tuc(xml_demo, bad):
    raw = tao_zip([("hong.xml", xml_demo), ("tot.xml", xml_demo)])
    if bad == "crc":
        raw = doi_central(raw, crc=0)
    elif bad == "encrypted":
        raw = doi_central(raw, flag=1)
    elif bad == "method":
        raw = doi_central(raw, method=99)
    elif bad == "offset":
        raw = doi_central(raw, offset=5)
    elif bad == "truncated":
        raw = doi_central(raw, compressed=len(xml_demo) - 5)
    elif bad == "size_short":
        # CRC vẫn đúng toàn bộ nội dung: phải phát hiện file_size giả.
        raw = doi_central(raw, size=5)
    else:
        raw = doi_central(raw, size=len(xml_demo) + 1)
    t, r = doc(raw)
    a, b = r["danh_sach_tep"]
    assert a["bam"] is a["kich_thuoc"] is a["trung_noi_dung_voi"] is None
    assert a["canh_bao"] and a["can_kiem_tra"] is True
    assert a["trang_thai_doc"] == ("khong_ho_tro" if bad == "method" else "loi")
    assert b["trang_thai_doc"] == "doc_duoc" and b["bam"] == bam(xml_demo)
    assert b["trung_noi_dung_voi"] is None  # không băm phần đầu để gọi trùng
    assert t["da_doc_het"] is False and t["so_tep"] == 2


@pytest.mark.parametrize("raw", [b"", b"DEMO", b"PK\x03\x04DEMO", b"PK\x05\x06DEMO"])
def test_zip_khong_kiem_ke_duoc_loi_toan_viec_co_dinh(raw):
    with pytest.raises(LoiNghiepVu) as exc:
        doc(raw)
    assert (exc.value.ma, exc.value.thong_diep) == (
        "HD_ZIP_KHONG_DOC_DUOC", "Không kiểm kê được gói ZIP. Anh hãy kiểm tra lại tệp.")


def test_central_directory_hong_khong_bia_danh_sach(xml_demo):
    raw = bytearray(tao_zip([("DEMO.xml", xml_demo)]))
    pos = raw.index(b"PK\x01\x02")
    raw[pos:pos + 4] = b"DEMO"
    with pytest.raises(LoiNghiepVu) as exc:
        doc(bytes(raw))
    assert exc.value.ma == "HD_ZIP_KHONG_DOC_DUOC"


@pytest.mark.parametrize("offset,value", [(8, 1), (10, 1), (4, 1), (6, 1)])
def test_eocd_gia_khong_bia_goi_rong_da_kiem(offset, value):
    raw = bytearray(tao_zip([]))
    struct.pack_into("<H", raw, offset, value)
    with pytest.raises(LoiNghiepVu) as exc:
        doc(bytes(raw))
    assert exc.value.ma == "HD_ZIP_KHONG_DOC_DUOC"


def test_eocd_khai_1001_entry_tu_choi_toan_viec():
    raw = bytearray(tao_zip([]))
    struct.pack_into("<H", raw, 10, 1001)
    vuot(bytes(raw))


def test_khong_ke_thua_complete_cua_loi(monkeypatch):
    from dataclasses import replace
    raw = tao_zip([("DEMO.pdf", b"%PDF-DEMO")])
    core_result = replace(loi.doc_goi_hoa_don_zip(raw), artifact_coverage="COMPLETE")
    monkeypatch.setattr(cong, "doc_goi_hoa_don_zip", lambda *a, **k: core_result)
    t, r = doc(raw)
    assert t["da_doc_het"] is False and t["so_khong_ho_tro"] == 1
    assert r["do_du_ky_tai"] == "UNKNOWN"


def test_khong_mo_duong_may_khong_ghi_cau_hinh_noi_dung(xml_demo, monkeypatch, capsys):
    raw = tao_zip([("../DEMO.xml", xml_demo), ("DEMO.xml", xml_demo), ("DEMO.pdf", b"%PDF-DEMO")])
    def cam(*a, **k):
        pytest.fail("Đã chạm filesystem hoặc giải nén đĩa.")
    monkeypatch.setattr(builtins, "open", cam)
    monkeypatch.setattr(io, "open", cam)
    monkeypatch.setattr(zipfile.ZipFile, "extract", cam)
    monkeypatch.setattr(zipfile.ZipFile, "extractall", cam)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", "DEMO-khong-duoc-doc.json")
    monkeypatch.setenv("KTT_ENGINE_DU_LIEU", "DEMO-khong-duoc-ghi")
    _, r = doc(raw)
    assert len(r["danh_sach_tep"]) == 3
    assert capsys.readouterr() == ("", "")


def test_chay_py_van_chi_xml_khong_nap_cau_hinh():
    import ast
    import e_hoa_don.chay as chay
    tree = ast.parse((GOI / "e_hoa_don/chay.py").read_text(encoding="utf-8"))
    assert not any(isinstance(n, ast.ImportFrom) and n.module == "cau_hinh_may" for n in ast.walk(tree))
    assert [n["ma"] for n in chay.app.phieu["nang_luc"]] == ["hoa_don.doc_xml@2"]


def test_huy_khong_boc_thanh_loi_entry(xml_demo):
    calls = []
    def huy():
        calls.append(1)
        if len(calls) == 3:
            raise ViecDaHuy()
    with pytest.raises(ViecDaHuy):
        doc(tao_zip([("DEMO.xml", xml_demo)]), kiem_huy=huy)
    assert len(calls) == 3


def test_mat_lease_khi_doc_chunk_khong_bao_cao_thanh_cong(xml_demo):
    calls = []
    error = LoiDuongTruyen("MAT_LEASE", "DEMO-CANARY-LEASE", http_status=409)
    def kiem():
        calls.append(1)
        if len(calls) == 2:
            raise error
    with pytest.raises(LoiDuongTruyen) as exc:
        doc(tao_zip([("DEMO.xml", xml_demo)]), kiem_huy=kiem)
    assert exc.value is error and len(calls) == 2


def test_loi_bat_bien_khong_che_thanh_entry(xml_demo, monkeypatch):
    def hong(*a, **k):
        raise DataError("DEMO_INVARIANT", "DEMO")
    monkeypatch.setattr(loi, "_doc", hong)
    with pytest.raises(DataError) as exc:
        doc(tao_zip([("DEMO.xml", xml_demo)]))
    assert exc.value.code == "DEMO_INVARIANT"


def test_bien_1000_entry_va_tu_choi_1001_ca_thu_muc():
    raw = tao_zip([(f"DEMO-{i}/", b"") for i in range(1000)])
    _, r = doc(raw)
    assert len(r["danh_sach_thu_muc"]) == 1000 and r["so_tep"] == 0
    vuot(tao_zip([(f"DEMO-{i}/", b"") for i in range(1001)]))


@pytest.mark.parametrize("kind", ["zip", "file", "total", "ratio"])
def test_metadata_vuot_tran_tu_choi_truoc_mo_entry(monkeypatch, kind):
    if kind == "zip":
        monkeypatch.setattr(loi, "MAX_ZIP_BYTES", 64)
        raw = tao_zip([("DEMO.txt", b"DEMO")])
    elif kind == "file":
        raw = doi_central(tao_zip([("DEMO.txt", b"DEMO")]), size=16 * 1024 * 1024 + 1)
    elif kind == "total":
        raw = tao_zip([(f"DEMO-{i}.txt", b"x") for i in range(9)])
        for i in range(1, 10):
            raw = doi_central(raw, i, size=16 * 1024 * 1024, compressed=16 * 1024 * 1024)
    else:
        raw = doi_central(tao_zip([("DEMO.txt", b"DEMO")]), size=1001, compressed=1)
    monkeypatch.setattr(zipfile.ZipFile, "open", lambda *a: pytest.fail("Metadata vượt trần vẫn mở entry."))
    vuot(raw)


def test_bien_zip_bytes_thuc(monkeypatch):
    raw = tao_zip([])
    monkeypatch.setattr(loi, "MAX_ZIP_BYTES", len(raw))
    assert doc(raw)[0]["so_tep"] == 0
    vuot(raw + b"D")


def test_bien_zip_64mib_thuc():
    empty = tao_zip([])
    raw = b"D" * (64 * 1024 * 1024 - len(empty)) + empty
    assert doc(raw)[0]["so_tep"] == 0
    vuot(raw + b"D")


@pytest.mark.parametrize("suffix", ["xml", "pdf"])
def test_bien_16mib_thuc_va_vuot_1_byte(suffix):
    raw = b"D" * (16 * 1024 * 1024)
    t, r = doc(tao_zip([("DEMO." + suffix, raw)]))
    assert r["danh_sach_tep"][0]["bam"] == bam(raw)
    assert r["danh_sach_tep"][0]["kich_thuoc"] == len(raw)
    vuot(tao_zip([("DEMO." + suffix, raw + b"D")]))


@pytest.mark.parametrize("method", [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])
def test_size_header_gia_khong_cat_tien_to_de_qua_tran(monkeypatch, method):
    raw = tao_zip([("DEMO.pdf", b"D" * 65)], method)
    raw = doi_central(raw, size=1)
    monkeypatch.setattr(loi, "MAX_XML_BYTES", 64)
    vuot(raw)


def test_tong_giai_nen_dem_thuc_ca_non_xml_va_trung(monkeypatch):
    # Metadata khai 1 byte, CRC đúng cả nội dung. Ba entry đều phải được đọc;
    # hai entry đầu lỗi kích thước vẫn phải tính byte đã giải nén vào tổng.
    raw = tao_zip([("DEMO.pdf", b"D" * 8)] * 3)
    for i in (1, 2, 3):
        raw = doi_central(raw, i, size=1)
    monkeypatch.setattr(loi, "MAX_ZIP_TOTAL_BYTES", 23)
    vuot(raw)
    monkeypatch.setattr(loi, "MAX_ZIP_TOTAL_BYTES", 24)
    t, r = doc(raw)
    assert t["so_loi"] == 3 and t["so_tep"] == 3
    assert all(e["bam"] is None for e in r["danh_sach_tep"])


def test_chunk_loi_crc_van_tinh_vao_tong(monkeypatch):
    raw = tao_zip([("DEMO.pdf", b"D" * 8)] * 3)
    for i in (1, 2, 3):
        raw = doi_central(raw, i, size=1, crc=0)
    monkeypatch.setattr(loi, "MAX_ZIP_TOTAL_BYTES", 23)
    vuot(raw)


def test_tong_giai_nen_bien_128mib_khong_tin_complete():
    import random
    # Khối DEMO tái lập, đủ entropy để không chạm trần tỉ lệ 1.000:1.
    content = random.Random(20261030).randbytes(8192) * 2048
    entries = [(f"DEMO-{i}.pdf", content) for i in range(8)]
    t, r = doc(tao_zip(entries, zipfile.ZIP_DEFLATED))
    assert t["so_tep"] == 8 and t["so_trung_noi_dung"] == 7
    assert sum(e["kich_thuoc"] for e in r["danh_sach_tep"]) == 128 * 1024 * 1024
    assert all(e["bam"] == bam(content) for e in r["danh_sach_tep"])
    raw = tao_zip(entries + [("vuot.pdf", b"D")], zipfile.ZIP_DEFLATED)
    # Metadata khai 0 để buộc nhánh đếm byte THẬT xử lý 128 MiB + 1.
    vuot(doi_central(raw, 9, size=0))


def test_tong_thuc_bien_va_vuot_khong_loai_trung(monkeypatch):
    raw = tao_zip([("a.pdf", b"D" * 8), ("b.pdf", b"D" * 8), ("b.pdf", b"D" * 8)])
    monkeypatch.setattr(loi, "MAX_ZIP_TOTAL_BYTES", 24)
    t, _ = doc(raw)
    assert t["so_tep"] == 3 and t["so_trung_noi_dung"] == 2
    monkeypatch.setattr(loi, "MAX_ZIP_TOTAL_BYTES", 23)
    vuot(raw)


def test_ty_le_nen_dem_thuc_metadata_gia(monkeypatch):
    raw = doi_central(tao_zip([("DEMO.pdf", b"D" * 200)], zipfile.ZIP_DEFLATED), size=1)
    monkeypatch.setattr(loi, "MAX_ZIP_RATIO", 10)
    vuot(raw)


@pytest.mark.parametrize("n", [1000, 1001])
def test_gate_hhdvu_truoc_dto(xml_demo, monkeypatch, n):
    raw_xml = re.sub(rb"<HHDVu>.*?</HHDVu>", b"<HHDVu/>" * n, xml_demo, flags=re.S)
    raw = tao_zip([("DEMO.xml", raw_xml)])
    if n == 1000:
        t, r = doc(raw)
        assert t["so_doc_duoc"] == 1 and r["danh_sach_tep"][0]["truong_hoa_don"]["so_dong"] == 1000
    else:
        monkeypatch.setattr(loi, "_doc", lambda *a: pytest.fail("1.001 HHDVu đã vào DTO."))
        vuot(raw)


def test_json_bien_bytes_utf8_va_vuot(xml_demo, monkeypatch):
    raw = tao_zip([("ĐEMO.xml", xml_demo)])
    _, report = cong.doc_zip(raw, tep_zip=TEP)
    monkeypatch.setattr(cong, "JSON_TOI_DA_BYTE", len(report))
    assert cong.doc_zip(raw, tep_zip=TEP)[1] == report
    monkeypatch.setattr(cong, "JSON_TOI_DA_BYTE", len(report) - 1)
    vuot(raw)


def test_json_vuot_32mib_thuc_khong_cat_entry():
    # Chỉ metadata DEMO trong RAM, input <64 MiB, 1.000 entry, JSON >32 MiB.
    raw = tao_zip([("D" * 33196 + ".pdf", b"D")] * 1000)
    assert len(raw) < 64 * 1024 * 1024
    vuot(raw)


@pytest.mark.parametrize("directory", ["../DEMO/", "DEMO/"])
def test_loi_thu_muc_khong_suy_doc_het(xml_demo, directory):
    raw = tao_zip([("DEMO.xml", xml_demo), (directory, b"DEMO")])
    t, r = doc(raw)
    assert t["so_tep"] == t["so_doc_duoc"] == 1
    assert t["da_doc_het"] is False and r["danh_sach_thu_muc"][0]["canh_bao"]


def kiem_schema(value, schema, root):
    """Bộ kiểm test stdlib cho đúng tập từ khóa schema đang dùng; không runtime."""
    if "$ref" in schema:
        target = root
        for key in schema["$ref"][2:].split("/"):
            target = target[key]
        return kiem_schema(value, target, root)
    if "anyOf" in schema:
        errors = []
        for choice in schema["anyOf"]:
            try:
                kiem_schema(value, choice, root)
                return
            except AssertionError as error:
                errors.append(str(error))
        raise AssertionError(f"Không khớp anyOf: {errors}")
    if "type" in schema:
        types = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool, "null": type(None)}
        kinds = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        assert any(isinstance(value, types[k]) and not (k in {"integer", "number"} and isinstance(value, bool)) for k in kinds)
    if "const" in schema:
        assert value == schema["const"] and type(value) is type(schema["const"])
    if "enum" in schema:
        assert value in schema["enum"]
    if isinstance(value, dict):
        assert set(schema.get("required", [])) <= set(value)
        if schema.get("additionalProperties") is False:
            assert set(value) <= set(schema.get("properties", {}))
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                try:
                    kiem_schema(value[key], sub, root)
                except AssertionError as error:
                    raise AssertionError(f"{key}: {error}") from error
    if isinstance(value, list):
        assert len(value) <= schema.get("maxItems", len(value)) and len(value) >= schema.get("minItems", 0)
        for item in value:
            kiem_schema(item, schema.get("items", {}), root)
    if isinstance(value, str):
        assert len(value) >= schema.get("minLength", 0)
        if "pattern" in schema:
            assert re.search(schema["pattern"], value)
    if isinstance(value, int) and not isinstance(value, bool):
        assert schema.get("minimum", value) <= value <= schema.get("maximum", value)
    for sub in schema.get("allOf", []):
        try:
            kiem_schema(value, sub.get("if", {}), root)
        except AssertionError:
            continue
        kiem_schema(value, sub.get("then", {}), root)


def test_schema_json_ky_thuat_doc_duoc_loi_khong_ho_tro(xml_demo):
    schema = json.loads((GOI / "contract/bao_cao_zip.schema.json").read_text(encoding="utf-8"))
    raw = tao_zip([("z.xml", xml_demo), ("a.xml", b"<HDon"), ("DEMO.pdf", b"%PDF-DEMO"), ("DEMO/", b""),
                   ("namespace.xml", b'<HDon xmlns="urn:DEMO"/>'), ("profile.xml", b'<x/>'),
                   ("utf16.xml", '<HDon/>'.encode('utf-16'))])
    _, r = doc(raw)
    kiem_schema(r, schema, schema)
    raw = doi_central(raw, crc=0)
    _, r = doc(raw)
    kiem_schema(r, schema, schema)
    assert schema["properties"]["phien_ban"] == {"const": 1}
    assert schema["$defs"]["entry"]["additionalProperties"] is False
    assert "tep_xml" not in schema["$defs"]["truong_hoa_don"]["properties"]
