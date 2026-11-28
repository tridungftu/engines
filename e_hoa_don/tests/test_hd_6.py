"""HD-6: đáp án dựng từ literal DEMO, không gọi parser để tạo expected."""

from copy import deepcopy
from hashlib import sha256
import builtins
import io
import json
import threading
import warnings
import zipfile

import pytest
from kho_tri_thuc_sdk.engine import LoiDuongTruyen, Viec
from kho_tri_thuc_sdk.thu import CoreGia

import e_hoa_don.chay as cong
import e_hoa_don.zip as zip_cong
from test_hd_2 import kenh  # Hai đường SDK: bộ nhớ và HTTP loopback.
from test_hd_5 import GOI, tao_zip, doi_central, kiem_schema

NL = "hoa_don.doc_zip@1"
DEMO = GOI / "demo/goi-hon-hop-DEMO.zip"
GOC = "/HDon/DLHDon/"
DONG = GOC + "NDHDon/DSHHDVu/HHDVu[1]"
TONG = GOC + "NDHDon/TToan"
CB = [
    "TOTAL_SECTION_UNSUPPORTED: Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.",
    "UNIT_UNPROVEN: Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.",
    "CONTEXT_ABSENT: Chưa có ngữ cảnh tin cậy để xác định hóa đơn.",
    "CONTENT_OUTSIDE_SUPPORTED_ENVELOPE: Dữ liệu nguồn còn cần kiểm tra; xem chi tiết kỹ thuật.",
    "IDENTITY_UNRESOLVED: Chưa xác định được định danh hóa đơn.",
]


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def giao(core, raw=None, metadata=None):
    tep = core.them_tep("goi-DEMO.zip", DEMO.read_bytes() if raw is None else raw, "application/zip")
    tep.update(metadata or {})
    vid = core.giao_viec(NL, {"loai": "tep", "tep": tep}, gui_kem_dau_vao=False)
    return vid, tep


def report(core, kq):
    return json.loads(core.doc_tep(kq["ket_qua"]["truong"]["chi_tiet_nguon"]["tep_id"]))


def occurrence(text, state="TEXT"):
    return dict(state=state, lexeme=text, lexeme_basis="XML_DECODED_CHARACTER_DATA_NO_TRIM")


def fields(pairs, path):
    return [dict(name=n, locator=path + "/" + n, occurrences=[occurrence(v)], mixed_content=False) for n, v in pairs]


def number(text, digits, state="PRECISION_UNDECLARED"):
    return dict(state=state, exact_value=text, exact_text=text, lexical_digits=digits, scale=0)


def issue(code, message, locator, severity="ERROR"):
    return dict(code=code, message=message, locator=locator, severity=severity)


def detail(ordinal, name, digest, size, container, so="0000123", hong=False):
    """Literal DTO theo nguồn XML DEMO + hợp đồng; chỉ ghép binding động."""
    prefix = f"zip:{container}!{ordinal}:{name}#"
    absent = dict(state="ABSENT", exact_value=None, exact_text=None, lexical_digits=None, scale=None)
    r = dict(
        raw_ref=dict(native_sha256=digest, byte_length=size, media_type="application/xml",
                     container_sha256=container, entry_ordinal=ordinal, entry_name=name),
        artifact_name=name, shape="XML_MALFORMED" if hong else "SUPPORTED_SUBSET",
        source_instance=None, source_profile_ref=None, profile_document_sha256=None,
        profile_payload_sha256=None, header_fields=[],
        header_total_section=occurrence(None, "ABSENT") if hong else occurrence("", "EMPTY"),
        lines=[], canonical_identity=None, semantic_envelope=None, semantic_digest=None,
        issues=[], candidate_reasons=["CONTEXT_ABSENT", "XML_MALFORMED"] if hong else
        ["CONTEXT_ABSENT", "CONTENT_OUTSIDE_SUPPORTED_ENVELOPE", "IDENTITY_UNRESOLVED"],
        native_fiscal_status="UNKNOWN", business_promotion="NOT_PERFORMED", current_DB_basis_sha256=None,
        L11_eligibility="NOT_EVALUATED", request_digest="NOT_DEFINED_IN_THIS_SLICE", profile_payload_binding="NOT_BOUND",
        money=dict(state="HOLD", fields=[], currency=None, net_amount=deepcopy(absent), tax_amount=deepcopy(absent),
                   non_taxable_amount=deepcopy(absent), total_amount=deepcopy(absent), tax_components=[], issues=[], reasons=["INPUT_NOT_READ"]),
        relations=dict(state="HOLD" if hong else "ABSENT", items=[], issues=[], reasons=["INPUT_NOT_READ"] if hong else []),
    )
    if hong:
        r["issues"] = [issue("XML_MALFORMED", "XML không phân tích được; giữ nguyên bytes làm bằng chứng.", prefix + "/")]
        return r
    r["header_fields"] = fields([("PBan", "DEMO"), ("KHMSHDon", "1"), ("KHHDon", "C26TAA"),
                                 ("SHDon", so), ("NLap", "2026-10-30"), ("DVTTe", "VND")], GOC + "TTChung")
    r["header_fields"] += fields([("NBan/MST", "0100000001"), ("NMua/MST", "0100000002")], GOC + "NDHDon")
    unit = issue("UNIT_UNPROVEN", "Không có fact đơn vị khớp DVTinh — số lượng chuẩn hóa NULL (HOLD).", prefix + DONG + "/DVTinh", "WARNING")
    r["issues"] = [issue("TOTAL_SECTION_UNSUPPORTED", "Có mục tổng TToan — ngoài envelope DEMO hiện hỗ trợ.", prefix + TONG), unit]
    r["lines"] = [dict(source_ordinal=1, source_locator=DONG,
        fields=fields([("STT", "1"), ("TChat", "1"), ("MHHDVu", "DEMO-01"), ("THHDVu", "Hàng hóa DEMO Ánh Dương"),
                       ("DVTinh", "CAI"), ("SLuong", "1"), ("DGia", "1000000"), ("ThTien", "1000000"), ("TSuat", "10%")], DONG),
        nature="GOODS", quantity=number("1", 1, "EXACT"), unit_price=number("1000000", 7, "EXACT"),
        source_amount=number("1000000", 7), normalized_quantity_text=None, unit_definition_ref=None,
        logical_line_ref=None, crosswalk_ref=None, continuity_ref=None, issues=[unit], row_raw_sha256=None)]
    tc = TONG + "/THTTLTSuat/LTSuat[1]"
    r["money"] = dict(state="EXACT", fields=fields([("TgTCThue", "1000000"), ("TgTThue", "100000"),
        ("TgTTTBSo", "1100000"), ("TGTKCThue", "0")], TONG) + fields([("DVTTe", "VND")], GOC + "TTChung"),
        currency="VND", net_amount=number("1000000", 7), tax_amount=number("100000", 6), non_taxable_amount=number("0", 1),
        total_amount=number("1100000", 7), tax_components=[dict(source_locator=tc,
        fields=fields([("TSuat", "10%"), ("ThTien", "1000000"), ("TThue", "100000")], tc), rate="10%",
        net_amount=number("1000000", 7), tax_amount=number("100000", 6))], issues=[], reasons=[])
    r["van_de_phep_chieu"] = []
    return r


def oracle(tep):
    """Không dùng output reader; thứ tự, số đếm, bytes và trạng thái chốt riêng."""
    raw = DEMO.read_bytes()
    xml = (GOI / "demo/hoa-don-DEMO.xml").read_bytes()
    assert bam(raw) == "sha256:91106609ac23affecdb2be9592f7a708a0b816700c5370eb234bbc913a5cedc8"
    assert bam(xml) == "sha256:06fe9986063ee65483c7d91880b948a1ab65856d05767508face98695c8d07fe"
    entries = [(1, "z-DEMO.xml", xml, "doc_duoc", False, None),
               (3, "loi-DEMO.xml", b"<HDon", "loi", False, None),
               (4, "DEMO.pdf", b"%PDF-DEMO", "khong_ho_tro", False, None),
               (5, "trung-DEMO.xml", xml, "doc_duoc", True, 1),
               (6, "trung-DEMO.xml", xml.replace(b"0000123", b"0000124"), "doc_duoc", True, None)]
    ds = []
    for ordinal, name, content, state, trung_ten, trung in entries:
        digest = bam(content)
        cb = CB.copy() if state == "doc_duoc" else ["Không đọc được cấu trúc XML hóa đơn." if state == "loi" else
                "Định dạng tệp chưa được hỗ trợ; chỉ kiểm kê và băm nội dung."]
        if trung_ten:
            cb.append("Tên entry trùng sau chuẩn hóa NFC/hoa thường; giữ riêng từng entry.")
        if trung:
            cb.append("Nội dung trùng với entry trước; giữ nguyên bản này.")
        f = None
        if state == "doc_duoc":
            f = dict(mau_so="1", ky_hieu="C26TAA", so_hoa_don="0000124" if ordinal == 6 else "0000123",
                ngay_lap="2026-10-30", don_vi_tien="VND", ma_so_thue_ban="0100000001", ma_so_thue_mua="0100000002",
                tien_truoc_thue=dict(so="1000000", tien_te="VND"), tien_thue=dict(so="100000", tien_te="VND"),
                tong_thanh_toan=dict(so="1100000", tien_te="VND"), so_dong=1, can_kiem_tra=True,
                canh_bao="\n".join(CB), chi_tiet_nguon=None, nguon_doc="xml_strict", phien_ban_engine="e_hoa_don 1.0.1",
                bam_dau_vao=digest, nguon=dict(tep_zip=tep, bam_goi=bam(raw), thu_tu=ordinal, ten=name, bam=digest))
        ds.append(dict(thu_tu=ordinal, ten=name, bam=digest, kich_thuoc=len(content), trang_thai_doc=state,
            trung_ten=trung_ten, trung_noi_dung_voi=trung, ma_loi={"doc_duoc": None, "loi": "HD_ZIP_XML_HONG",
            "khong_ho_tro": "HD_ZIP_KHONG_HO_TRO"}[state], canh_bao=cb, can_kiem_tra=True, truong_hoa_don=f,
            chi_tiet_nguon=None if state == "khong_ho_tro" else detail(ordinal, name, digest[7:], len(content),
            bam(raw)[7:], "0000124" if ordinal == 6 else "0000123", state == "loi")))
    return dict(phien_ban=1, nguon_doc="zip_xml_strict", phien_ban_engine="e_hoa_don 1.0.1", bam_dau_vao=bam(raw),
        tep_zip=tep, da_doc_het=False, so_tep=5, so_doc_duoc=3, so_loi=1, so_khong_ho_tro=1, so_trung_noi_dung=1,
        can_kiem_tra=True, do_du_ky_tai="UNKNOWN", native_fiscal_status="UNKNOWN", business_promotion="NOT_PERFORMED",
        danh_sach_tep=ds, danh_sach_thu_muc=[dict(thu_tu=2, ten="thu-muc-DEMO/", trung_ten=False, canh_bao=[])],
        canh_bao=["Đã đọc 3/5 tệp; kết quả cần kiểm tra.", "Có tệp lỗi/chưa hỗ trợ; xem kiểm kê từng tệp.",
                  "Chưa xác định độ đủ kỳ tải hoặc trạng thái thuế; chưa ghi nhận nghiệp vụ."])


def test_toan_json_literal_va_cong_sdk(kenh, monkeypatch):
    core, chay, _ = kenh
    vid, tep = giao(core, metadata={"kich_thuoc": 1})
    opened = []
    mo = Viec.mo_tep
    def doc(viec, tid):
        opened.append(tid)
        return mo(viec, tid)
    monkeypatch.setattr(Viec, "mo_tep", doc)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "XONG", kq
    r = report(core, kq)
    assert r == oracle(tep)  # So toàn bộ DTO, locator, occurrence, tiền, băm và thứ tự.
    schema = json.loads((GOI / "contract/bao_cao_zip.schema.json").read_text(encoding="utf-8"))
    kiem_schema(r, schema, schema)
    t = kq["ket_qua"]["truong"]
    assert set(t) == {f["ma"] for f in cong.app.phieu["nang_luc"][1]["truong_ra"]}
    assert {k: v for k, v in t.items() if k not in {"chi_tiet_nguon", "canh_bao"}} == {k: r[k] for k in t if k not in {"chi_tiet_nguon", "canh_bao"}}
    assert t["canh_bao"] == "\n".join(r["canh_bao"]) and "đầy đủ" not in t["canh_bao"]
    assert t["chi_tiet_nguon"]["ten"] == "hoa-don-goi-chi-tiet.json"
    assert t["chi_tiet_nguon"]["mime"] == "application/json"
    assert opened == [tep["tep_id"]] and len(core._tep) == 2
    calls = [n[0] for n in core.nhat_ky]
    assert calls.index("tep") < calls.index("ket_qua") < calls.index("ket_thuc")


@pytest.mark.parametrize("op", ["tep", "ket_qua", "ket_thuc"])
@pytest.mark.parametrize("n", [1, 3])
def test_ack_gui_lai_idempotency(kenh, op, n):
    core, chay, may = kenh
    vid, tep = giao(core)
    core.gay_mat_xac_nhan(op, n)
    chay()
    assert core.xem(vid)["trang_thai"] == "XONG"
    assert report(core, core.xem(vid)) == oracle(tep)
    for key in ("tep", "ket_qua", "ket_thuc"):
        calls = [x for x in core.nhat_ky if x[0] == key]
        assert core.so_lan_ghi[key] == 1 and len(calls) == (n + 1 if key == op else 1)
        assert len({x[3] for x in calls}) == 1 and calls[0][3]
    assert len(core._tep) == 2
    if may:
        suffix = {"tep": "/tep", "ket_qua": "/ket-qua", "ket_thuc": "/ket-thuc"}[op]
        assert len({x["idempotency_key"] for x in may.cac_loi_goi if x["duong"].endswith(suffix)}) == 1


@pytest.mark.parametrize("stage", [10, 60, 80, 100])
def test_huy_truoc_upload_tra(kenh, monkeypatch, stage):
    core, chay, _ = kenh
    vid, _ = giao(core)
    tien_do = core._tien_do
    def huy(ma, viec, percent, cau):
        if percent == stage:
            core.huy(viec)
        return tien_do(ma, viec, percent, cau)
    monkeypatch.setattr(core, "_tien_do", huy)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0 and core.so_lan_ghi["tep"] == (stage == 100)


@pytest.mark.parametrize("status", [404, 409, 410])
@pytest.mark.parametrize("stage", [10, 60, 80, 100, "doc", "upload"])
def test_mat_lease_khong_nop(kenh, monkeypatch, capsys, status, stage):
    core, chay, _ = kenh
    vid, _ = giao(core)
    def hong(*a, **k):
        raise LoiDuongTruyen("MAT_LEASE", "DEMO-CANARY-LEASE", http_status=status)
    if stage in {"doc", "upload"}:
        monkeypatch.setattr(core, "_mo_tep" if stage == "doc" else "_tai_tep_ra", hong)
    else:
        tien_do = core._tien_do
        def progress(ma, v, percent, cau):
            return hong() if percent == stage else tien_do(ma, v, percent, cau)
        monkeypatch.setattr(core, "_tien_do", progress)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "DANG_CHAY" and kq["ket_qua"] is None and kq["ma_tuong_quan"] is None
    assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 0
    assert "DEMO-CANARY" not in capsys.readouterr().err + json.dumps(kq)


@pytest.mark.parametrize("response", [None, {}, {"tep_id": ""}, {"tep_id": 12}, "loi", "loi_tam"])
def test_upload_loi_khong_xong(kenh, monkeypatch, capsys, response):
    core, chay, _ = kenh
    vid, _ = giao(core)
    calls = []
    def hong(ma, v, ten, raw, mime, khoa):
        calls.append(khoa)
        if response in ("loi", "loi_tam"):
            raise LoiDuongTruyen("DEMO_UPLOAD", "DEMO-CANARY-UPLOAD", http_status=503 if response == "loi_tam" else 403,
                                 thu_lai_duoc=response == "loi_tam")
        return response
    monkeypatch.setattr(core, "_tai_tep_ra", hong)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and kq["ma_tuong_quan"] is None
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    assert len(calls) == (4 if response == "loi_tam" else 1) and len(set(calls)) == 1
    assert "DEMO-CANARY" not in capsys.readouterr().err + json.dumps(kq)


@pytest.mark.parametrize("kind", ["hong", "bytes", "entry", "ratio", "json"])
def test_tu_choi_toan_viec_khong_upload(kenh, monkeypatch, kind):
    core, chay, _ = kenh
    raw = DEMO.read_bytes()
    if kind == "hong":
        raw = b"DEMO-CANARY-zip-hong"
    elif kind == "bytes":
        monkeypatch.setattr(cong, "ZIP_TOI_DA_BYTE", len(raw) - 1)
    elif kind == "entry":
        raw = doi_central(raw, size=16 * 1024 * 1024 + 1)
    elif kind == "ratio":
        raw = doi_central(raw, ordinal=4, size=1001, compressed=1)
    else:
        monkeypatch.setattr(zip_cong, "JSON_TOI_DA_BYTE", 1)
    vid, _ = giao(core, raw, {"kich_thuoc": 1})
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == ("HD_ZIP_KHONG_DOC_DUOC" if kind == "hong" else "HD_ZIP_VUOT_GIOI_HAN")
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("entries", [[], [("DEMO/", b"")]])
def test_goi_rong_canh_bao(kenh, entries):
    core, chay, _ = kenh
    vid, _ = giao(core, tao_zip(entries))
    chay()
    kq = core.xem(vid)
    r = report(core, kq)
    assert kq["trang_thai"] == "XONG" and r["so_tep"] == 0 and r["da_doc_het"] is False
    assert r["can_kiem_tra"] is True and "Gói không có tệp hóa đơn đọc được." in r["canh_bao"]


def test_overlap_canary_khong_stderr_giu_entry(kenh, monkeypatch, capsys, xml_demo):
    core, chay, _ = kenh
    name = "DEMO-CANARY-OVERLAP.xml"
    raw = tao_zip([(name, xml_demo), (name, xml_demo), ("tot-DEMO.xml", xml_demo)])
    raw = doi_central(raw, ordinal=2, offset=0)
    vid, _ = giao(core, raw)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        chay()
    kq = core.xem(vid)
    r = report(core, kq)
    assert not caught and name not in capsys.readouterr().err + json.dumps(kq["tien_do"]) + json.dumps(kq["loi"])
    assert [(e["thu_tu"], e["trang_thai_doc"]) for e in r["danh_sach_tep"]] == [(1, "loi"), (2, "doc_duoc"), (3, "doc_duoc")]
    assert r["danh_sach_tep"][0]["bam"] is None and r["da_doc_het"] is False


@pytest.mark.parametrize("status", [None, 409])
def test_huy_mat_lease_giua_entry_qua_gia_han(kenh, monkeypatch, status):
    core, chay, _ = kenh
    vid, _ = giao(core)
    stop = threading.Event()
    real_doc = zip_cong.doc_goi_hoa_don_zip
    checks = []
    def gia_han(ma, v, giay):
        stop.set()
        if status:
            raise LoiDuongTruyen("MAT_LEASE", "DEMO-CANARY-GIA-HAN", http_status=status)
        return {"huy": True}
    def doc(*a, kiem_huy, **kw):
        def check():
            checks.append(1)
            if len(checks) == 4:
                assert stop.wait(3)
                # Gia hạn đã chạy, chờ chính cờ SDK thay vì race với thread.
                viec = kiem_huy.__self__
                assert viec._huy.wait(3)
            kiem_huy()
        return real_doc(*a, kiem_huy=check, **kw)
    monkeypatch.setattr(core, "_gia_han", gia_han)
    monkeypatch.setattr(zip_cong, "doc_goi_hoa_don_zip", doc)
    chay(khoang_gia_han=0.01)
    kq = core.xem(vid)
    assert kq["trang_thai"] == ("DANG_CHAY" if status else "HUY")
    assert kq["ket_qua"] is None and core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("method", [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])
def test_chot_api_rieng_zipfile_va_crc(method):
    raw = tao_zip([("DEMO.txt", b"DEMO" * 100)], method)
    end = zipfile._EndRecData(io.BytesIO(raw))
    assert [end[getattr(zipfile, key)] for key in ("_ECD_DISK_NUMBER", "_ECD_DISK_START", "_ECD_ENTRIES_TOTAL", "_ECD_ENTRIES_THIS_DISK")] == [0, 0, 1, 1]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        with z.open(z.infolist()[0]) as f:
            assert all(hasattr(f, k) for k in ("_left", "_update_crc", "_eof", "_compress_left", "_decompressor"))
            assert callable(f._update_crc) and f._left == 400 and not f._eof
            f._left = 401
            crc = f._update_crc
            seen = []
            def count(chunk):
                seen.append(chunk)
                crc(chunk)
            f._update_crc = count
            assert f.read() == b"DEMO" * 100 and b"".join(seen) == b"DEMO" * 100
            assert f._eof and f._compress_left == 0
            if method == zipfile.ZIP_DEFLATED:
                assert f._decompressor.eof
    bad = doi_central(raw, crc=0)
    with zipfile.ZipFile(io.BytesIO(bad)) as z:
        with z.open(z.infolist()[0]) as f, pytest.raises(zipfile.BadZipFile):
            f.read()


def test_khong_luu_gi_tren_may(monkeypatch):
    raw = DEMO.read_bytes()
    core = CoreGia()
    vid, _ = giao(core, raw)
    def cam(*a, **kw):
        pytest.fail("Engine không được chạm filesystem hoặc giải nén đĩa.")
    monkeypatch.setattr(builtins, "open", cam)
    monkeypatch.setattr(io, "open", cam)
    monkeypatch.setattr(zipfile.ZipFile, "extract", cam)
    monkeypatch.setattr(zipfile.ZipFile, "extractall", cam)
    core.chay(cong.app)
    assert core.xem(vid)["trang_thai"] == "XONG"


def test_manifest_zip_va_xml_giu_nguyen():
    p = cong.app.phieu
    cap = p["nang_luc"][1]
    assert cap["ma"] == NL and cap["nhan"] == ["tep"] and cap["tra"] == "truong"
    assert cap["gioi_han"] == dict(tep_toi_da_mib=20, mime=["application/zip", "application/x-zip-compressed"], thoi_han_giay=600)
    assert cap["huy_duoc"] is True and cap["tham_so"] == p["loai_du_lieu_rieng"] == []
    assert p["nang_luc"][0]["ma"] == "hoa_don.doc_xml@2"
    assert len(p["nang_luc"][0]["truong_ra"]) == 18
    assert len(p["chay_thu_demo"]) == 4


@pytest.mark.parametrize("mime", ["application/zip", "application/x-zip-compressed"])
def test_mime_zip_duong(mime):
    core = CoreGia()
    vid, _ = giao(core, metadata={"mime": mime})
    core.chay(cong.app)
    assert core.xem(vid)["trang_thai"] == "XONG"


def test_zip_20mib_bien_qua_core_gia():
    empty = tao_zip([])
    raw = b"D" * (20 * 1024 * 1024 - len(empty)) + empty
    core = CoreGia()
    vid, _ = giao(core, raw)
    core.chay(cong.app)
    assert core.xem(vid)["trang_thai"] == "XONG"


def test_bytes_thuc_20mib_cong_1_metadata_gia_khong_upload():
    core = CoreGia()
    vid, _ = giao(core, b"D" * (20 * 1024 * 1024 + 1), {"kich_thuoc": 1})
    core.chay(cong.app)
    kq = core.xem(vid)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "HD_ZIP_VUOT_GIOI_HAN"
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


def test_luong_khoi_ngan_van_doc_het_va_chan_byte_thua(monkeypatch):
    raw = DEMO.read_bytes()
    core = CoreGia()
    vid, tep = giao(core, raw)
    class Ngan(io.BytesIO):
        def read(self, n=-1):
            return super().read(min(n, 7))
    monkeypatch.setattr(Viec, "mo_tep", lambda *a: Ngan(raw))
    core.chay(cong.app)
    assert report(core, core.xem(vid)) == oracle(tep)
    monkeypatch.setattr(cong, "ZIP_TOI_DA_BYTE", len(raw) - 1)
    vid, _ = giao(core, raw)
    core.chay(cong.app)
    assert core.xem(vid)["loi"]["ma"] == "HD_ZIP_VUOT_GIOI_HAN"
    assert core.so_lan_ghi["tep"] == 1  # Chỉ upload của việc trước.


def test_canh_bao_mo_entry_thanh_loi_cuc_bo_moi_python(monkeypatch, xml_demo, capsys):
    core = CoreGia()
    name = "DEMO-CANARY-WARNING.xml"
    vid, _ = giao(core, tao_zip([(name, xml_demo), ("tot-DEMO.xml", xml_demo)]))
    real_open = zipfile.ZipFile.open
    showwarning = warnings.showwarning
    filters = warnings.filters[:]
    def mo(z, info, *a, **kw):
        if info.filename == name:
            warnings.warn("Overlapped entries: " + name, UserWarning)
        return real_open(z, info, *a, **kw)
    monkeypatch.setattr(zipfile.ZipFile, "open", mo)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error")
        core.chay(cong.app)
    r = report(core, core.xem(vid))
    assert [e["trang_thai_doc"] for e in r["danh_sach_tep"]] == ["loi", "doc_duoc"]
    assert r["danh_sach_tep"][0]["bam"] is r["danh_sach_tep"][0]["kich_thuoc"] is None
    assert not caught and name not in capsys.readouterr().err
    assert warnings.showwarning is showwarning and warnings.filters == filters


@pytest.mark.parametrize("stage", ["doc", "parse", "upload"])
def test_loi_cuc_bo_khong_chuaro_khong_lo_canary(kenh, monkeypatch, capsys, stage):
    core, chay, _ = kenh
    vid, _ = giao(core)
    def hong(*a, **kw):
        raise OSError("DEMO-CANARY-LOCAL /DEMO/bi-mat.xml")
    if stage == "parse":
        monkeypatch.setattr(cong, "doc_zip", hong)
    else:
        monkeypatch.setattr(core, "_mo_tep" if stage == "doc" else "_tai_tep_ra", hong)
    chay()
    kq = core.xem(vid)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and kq["ma_tuong_quan"] is None
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    assert "DEMO-CANARY" not in capsys.readouterr().err + json.dumps(kq["tien_do"]) + json.dumps(kq["loi"])
