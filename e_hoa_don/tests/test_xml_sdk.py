"""Regression đường đọc XML thật → SDK/CoreGia; không gọi Node/Cloud/thuế."""

from hashlib import sha256
import io
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import LoiDuongTruyen, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoa_don.chay import app, doc_hoa_don
from e_hoa_don.doc import doc_xml
from e_hoa_don.hoa_don_xml import MAX_XML_BYTES, doc_hoa_don_xml, ra_json

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_hoa_don"
TRUONG = {
    "mau_so", "ky_hieu", "so_hoa_don", "ngay_lap", "ma_so_thue_ban", "ma_so_thue_mua",
    "don_vi_tien", "tien_truoc_thue", "tien_thue", "tong_thanh_toan", "so_dong",
    "can_kiem_tra", "canh_bao", "tep_xml", "chi_tiet_nguon", "nguon_doc", "phien_ban_engine",
    "bam_dau_vao",
}


def chay(raw, *, core=None, metadata=None):
    core = core or CoreGia()
    tep = core.them_tep("hoa-don-DEMO.xml", raw, "application/xml")
    if metadata:
        tep.update(metadata)
    kq = core.chay_thu(app, "hoa_don.doc_xml@2", {"loai": "tep", "tep": tep})
    return core, tep, kq


def doc_bao_cao(core, kq):
    return json.loads(core.doc_tep(kq["ket_qua"]["truong"]["chi_tiet_nguon"]["tep_id"]))


def test_demo_du_truong_va_chi_tiet_nguon(xml_demo):
    core, tep, kq = chay(xml_demo)
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    assert set(t) == TRUONG == {t["ma"] for t in app.phieu["nang_luc"][0]["truong_ra"]}
    assert t["so_hoa_don"] == "0000123"
    assert t["ngay_lap"] == "2026-10-30"
    assert t["ma_so_thue_ban"] == "0100000001"
    assert t["ma_so_thue_mua"] == "0100000002"
    for ma, so in (("tien_truoc_thue", "1000000"), ("tien_thue", "100000"), ("tong_thanh_toan", "1100000")):
        assert t[ma] == {"so": so, "tien_te": "VND"}
    assert t["so_dong"] == 1 and t["can_kiem_tra"] is True
    assert t["nguon_doc"] == "xml_strict" and t["phien_ban_engine"] == "e_hoa_don 1.0.0"
    assert t["tep_xml"] == tep  # tep-1 không phải UUID, không cấp hay upload XML mới.
    assert t["chi_tiet_nguon"]["tep_id"] != tep["tep_id"]
    assert t["chi_tiet_nguon"]["ten"] == "hoa-don-chi-tiet.json"
    assert t["chi_tiet_nguon"]["mime"] == "application/json"
    assert core.so_lan_ghi["tep"] == 1
    assert [n[0] for n in core.nhat_ky].index("tep") < [n[0] for n in core.nhat_ky].index("ket_qua")
    bao_cao = doc_bao_cao(core, kq)
    chi_tiet = bao_cao["chi_tiet_nguon"]
    assert chi_tiet == ra_json(doc_hoa_don_xml(xml_demo, context=None))
    assert chi_tiet["canonical_identity"] is None and chi_tiet["semantic_digest"] is None
    assert chi_tiet["semantic_envelope"] is None
    assert {"CONTEXT_ABSENT", "IDENTITY_UNRESOLVED"} <= set(chi_tiet["candidate_reasons"])
    assert chi_tiet["native_fiscal_status"] == "UNKNOWN"
    assert chi_tiet["business_promotion"] == "NOT_PERFORMED"
    assert "raw_xml" not in chi_tiet and "contract" not in bao_cao
    assert "chi_tiet_nguon" not in bao_cao["tep_xml"]  # không tự tham chiếu báo cáo.
    digest = sha256(xml_demo).hexdigest()
    assert bao_cao["bam_dau_vao"] == t["bam_dau_vao"] == "sha256:" + digest
    assert chi_tiet["raw_ref"]["native_sha256"] == digest
    assert chi_tiet["raw_ref"]["byte_length"] == len(xml_demo)
    assert chi_tiet["lines"][0]["source_locator"].endswith("HHDVu[1]")
    assert chi_tiet["lines"][0]["source_amount"]["exact_value"] == "1000000"
    assert "CONTEXT_ABSENT:" in t["canh_bao"]
    assert "0100000001" not in t["canh_bao"] and "1000000" not in t["canh_bao"]


def test_tien_le_exact_qua_sdk(xml_demo):
    raw = xml_demo.replace(b">1000000<", b">1000000.123456<").replace(
        b">100000<", b">100000.000001<").replace(b">1100000<", b">1100000.123457<")
    core, _, kq = chay(raw)
    assert kq["trang_thai"] == "XONG"
    t = kq["ket_qua"]["truong"]
    assert t["tien_truoc_thue"] == {"so": "1000000.123456", "tien_te": "VND"}
    assert t["tien_thue"] == {"so": "100000.000001", "tien_te": "VND"}
    assert t["tong_thanh_toan"] == {"so": "1100000.123457", "tien_te": "VND"}
    fact = doc_bao_cao(core, kq)["chi_tiet_nguon"]["money"]["net_amount"]
    assert fact["exact_text"] == fact["exact_value"] == "1000000.123456"


@pytest.mark.parametrize("raw", [b"<HDon>DEMO-khong-lo-nguon", b"<x/>", b'<HDon xmlns="urn:DEMO"/>'])
def test_xml_hong_va_ngoai_profile_loi_co_dinh(raw):
    core, _, kq = chay(raw)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "HD_XML_KHONG_DOC_DUOC"
    assert kq["loi"]["thong_diep"] == "Không đọc được tệp XML hóa đơn trong phạm vi hỗ trợ."
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    with pytest.raises(LoiNghiepVu, match="HD_XML_KHONG_DOC_DUOC"):
        doc_xml(raw, tep_xml={"tep_id": "DEMO-khong-uuid"})


@pytest.mark.parametrize("so", [b"1000000.1234567", b"1000000000000000000"])
def test_tien_vuot_mien_khong_lam_tron(xml_demo, so):
    raw = xml_demo.replace(b">1000000<", b">" + so + b"<")
    core, _, kq = chay(raw)
    assert kq["trang_thai"] == "XONG"
    t = kq["ket_qua"]["truong"]
    assert t["tien_truoc_thue"] is None and t["can_kiem_tra"] is True
    bao_cao = doc_bao_cao(core, kq)
    assert bao_cao["chi_tiet_nguon"]["money"]["net_amount"]["exact_value"] == so.decode()
    assert "HOADON_MONEY_OVER_DOMAIN" in {i["code"] for i in bao_cao["van_de_phep_chieu"]}


@pytest.mark.parametrize(("cu", "moi", "truong"), [
    (b"<NLap>2026-10-30</NLap>", b"<NLap>2026-02-30</NLap>", "ngay_lap"),
    (b"<DVTTe>VND</DVTTe>", b"<DVTTe>vnd</DVTTe>", "don_vi_tien"),
    (b"<DVTTe>VND</DVTTe>", b"", "don_vi_tien"),
    (b"<SHDon>0000123</SHDon>", b"<SHDon>0000123</SHDon><SHDon>DEMO</SHDon>", "so_hoa_don"),
    (b"<SHDon>0000123</SHDon>", b"<SHDon/>", "so_hoa_don"),
    (b"<SHDon>0000123</SHDon>", b"", "so_hoa_don"),
    (b"<SHDon>0000123</SHDon>", b"<SHDon>00<x/>00123</SHDon>", "so_hoa_don"),
])
def test_nguon_sai_thieu_mo_ho_null(xml_demo, cu, moi, truong):
    core, _, kq = chay(xml_demo.replace(cu, moi))
    assert kq["trang_thai"] == "XONG"
    t = kq["ket_qua"]["truong"]
    assert t[truong] is None and t["can_kiem_tra"] is True
    if truong == "don_vi_tien":
        assert all(t[ma] is None for ma in ("tien_truoc_thue", "tien_thue", "tong_thanh_toan"))
    assert doc_bao_cao(core, kq)["chi_tiet_nguon"]["raw_ref"]["native_sha256"] == t["bam_dau_vao"][7:]


def test_occurrence_giu_absent_empty_text_va_trung(xml_demo):
    raw = xml_demo.replace(b"<SHDon>0000123</SHDon>", b"<SHDon/><SHDon>0000123</SHDon>").replace(
        b"<KHHDon>C26TAA</KHHDon>", b"")
    core, _, kq = chay(raw)
    fields = {f["name"]: f for f in doc_bao_cao(core, kq)["chi_tiet_nguon"]["header_fields"]}
    assert [o["state"] for o in fields["SHDon"]["occurrences"]] == ["EMPTY", "TEXT"]
    assert fields["SHDon"]["occurrences"][1]["lexeme"] == "0000123"
    assert fields["KHHDon"]["occurrences"][0]["state"] == "ABSENT"


def test_tong_mau_thuan_giu_so_nguon(xml_demo):
    core, _, kq = chay(xml_demo.replace(b">1100000<", b">1100001<"))
    t = kq["ket_qua"]["truong"]
    assert t["tong_thanh_toan"]["so"] == "1100001" and t["can_kiem_tra"] is True
    assert "MONEY_TOTAL_CONFLICT:" in t["canh_bao"]
    assert doc_bao_cao(core, kq)["chi_tiet_nguon"]["money"]["state"] == "HOLD"


class ViecDemo:
    """Seam I/O để kiểm đọc bytes thực và gate trước upload, không giả parser."""
    def __init__(self, raw):
        self.raw = raw
        self.dau_vao = {"tep": {"tep_id": "DEMO", "ten": "DEMO.xml", "kich_thuoc": 1}}
        self.da_tai = False

    def mo_tep(self, tep_id):
        assert tep_id == "DEMO"
        self.luong = io.BytesIO(self.raw)
        return self.luong

    def kiem_huy(self):
        pass

    def tien_do(self, *args):
        pass

    def tai_tep_ra(self, *args):
        self.da_tai = True
        raise AssertionError("Không được upload khi vượt giới hạn.")


def test_vuot_16_mib_kiem_bytes_thuc_metadata_khai_thieu():
    viec = ViecDemo(b" " * (MAX_XML_BYTES + 2))
    with pytest.raises(LoiNghiepVu) as exc:
        doc_hoa_don(viec)
    assert exc.value.ma == "HD_XML_VUOT_GIOI_HAN" and not viec.da_tai


def test_json_vuot_tran_tu_choi_truoc_upload(xml_demo, monkeypatch):
    import e_hoa_don.chay as chay_module
    monkeypatch.setattr(chay_module, "JSON_TOI_DA_BYTE", 1)
    viec = ViecDemo(xml_demo)
    with pytest.raises(LoiNghiepVu) as exc:
        doc_hoa_don(viec)
    assert exc.value.ma == "HD_JSON_VUOT_GIOI_HAN" and not viec.da_tai


def test_upload_that_bai_khong_xong(xml_demo, monkeypatch):
    core = CoreGia()
    def hong(*args, **kwargs):
        raise LoiDuongTruyen("DEMO_TAI_LOI", "Không lưu được tệp DEMO.", thu_lai_duoc=False)
    monkeypatch.setattr(core, "_tai_tep_ra", hong)
    _, _, kq = chay(xml_demo, core=core)
    assert kq["trang_thai"] != "XONG" and kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0


def test_manifest_chi_xml_va_demo_that():
    assert len(app.phieu["nang_luc"]) == 1
    nl = app.phieu["nang_luc"][0]
    assert nl["ma"] == "hoa_don.doc_xml@2" and nl["nhan"] == ["tep"] and nl["tra"] == "truong"
    assert nl["tham_so"] == app.phieu["loai_du_lieu_rieng"] == []
    assert nl["gioi_han"] == {"tep_toi_da_mib": 16, "mime": ["application/xml", "text/xml"], "thoi_han_giay": 600}
    assert nl["huy_duoc"] is True
    assert app.phieu["diem_vao"]["lenh"] == ["{python}", "-m", "e_hoa_don.chay"]
    kq = CoreGia().chay_thu_demo(app, GOI)
    assert len(kq) >= 1 and all(k["trang_thai"] == "XONG" for k in kq)


def test_loi_parser_khong_doi_thuat_toan():
    nguon = (GOI.parents[1] / "ma-nguon/lib/hoa_don_xml.py").read_text(encoding="utf-8")
    mong_doi = nguon.replace("from kho_tri_thuc.sdk_core.primitives import", "from kho_tri_thuc_sdk.primitives import").replace(
        "from kho_tri_thuc.sdk_core.engine_legacy import Issue", "from kho_tri_thuc_sdk.engine_legacy import Issue")
    assert (GOI / "e_hoa_don/hoa_don_xml.py").read_text(encoding="utf-8") == mong_doi
