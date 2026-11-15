"""Contract DEMO, đã kiểm bằng Core giả (CoreGia); không có handler nghiệp vụ.

Bộ kiểm chỉ hỗ trợ từ khóa thực dùng, từ chối từ khóa lạ; không phải bộ
triển khai đầy đủ JSON Schema. Adapter quyền chỉ tồn tại trong tests này.
"""

from copy import deepcopy
from hashlib import sha256
import importlib
import io
import json
import math
from pathlib import Path
import re
import struct
import sys
import zipfile
import zlib

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

ROOT = Path(__file__).resolve().parents[2]
GOI = ROOT / "e_doi_chieu/goi/e_doi_chieu"
sys.path.insert(0, str(GOI))
chay = importlib.import_module("e_doi_chieu.chay")
TEN_SCHEMA = ("ho_so_doi_chieu", "van_ban_tai_lieu", "yeu_cau_ai", "tra_loi_ai")
SCHEMA = json.loads((GOI / "ho_so_doi_chieu.schema.json").read_text(encoding="utf-8"))
TU_KHOA = {
    "$schema", "$id", "$comment", "$defs", "$ref", "title", "description",
    "type", "const", "enum", "required", "properties", "additionalProperties",
    "items", "minItems", "maxItems", "minLength", "maxLength", "minimum",
    "maximum", "exclusiveMinimum", "exclusiveMaximum", "pattern", "oneOf",
}


def bam(raw):
    return "sha256:" + sha256(raw).hexdigest()


def json_bytes(data):
    return json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")


def kiem_schema(value, schema, root=None):
    """Kiểm tập con dùng ở 4 contract, không bỏ qua keyword không hỗ trợ."""
    root = schema if root is None else root
    assert set(schema) <= TU_KHOA, "Từ khóa schema chưa được bộ kiểm test hỗ trợ"
    if "$ref" in schema:
        assert schema["$ref"].startswith("#/$defs/")
        kiem_schema(value, root["$defs"][schema["$ref"].split("/")[-1]], root)
    if "oneOf" in schema:
        dat = 0
        for con in schema["oneOf"]:
            try:
                kiem_schema(value, con, root)
                dat += 1
            except AssertionError:
                pass
        assert dat == 1
    kinds = {
        "object": type(value) is dict, "array": type(value) is list,
        "string": type(value) is str, "integer": type(value) is int,
        "number": type(value) in (int, float), "boolean": type(value) is bool,
        "null": value is None,
    }
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        assert any(kinds[k] for k in types)
    if "const" in schema:
        assert json_bytes(value) == json_bytes(schema["const"])
    if "enum" in schema:
        assert any(json_bytes(value) == json_bytes(v) for v in schema["enum"])
    if type(value) is dict:
        assert set(schema.get("required", [])) <= value.keys()
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert value.keys() <= props.keys()
        for key, item in value.items():
            if key in props:
                kiem_schema(item, props[key], root)
    if type(value) in (str, list):
        low, high = ("minLength", "maxLength") if isinstance(value, str) else ("minItems", "maxItems")
        assert schema.get(low, 0) <= len(value) <= schema.get(high, math.inf)
        if type(value) is list and "items" in schema:
            for item in value:
                kiem_schema(item, schema["items"], root)
    if type(value) is str and "pattern" in schema:
        assert re.search(schema["pattern"], value)
    if type(value) in (int, float):
        assert math.isfinite(value)
        assert schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf)
        assert schema.get("exclusiveMinimum", -math.inf) < value < schema.get("exclusiveMaximum", math.inf)


class CoreCapQuyenDEMO(CoreGia):
    """Mô phỏng C-DC-02 bằng allowlist, không coi đây là ACL/RLS thật."""

    def __init__(self):
        super().__init__()
        self.cap_cho_viec = {}
        self.thu_hoi_cho_viec = {}

    def _mo_tep(self, ma, viec_id, tep_id, toi_da_byte):
        if tep_id in self.thu_hoi_cho_viec.get(viec_id, set()):
            self._dang_giu(ma, viec_id)
            raise LoiDuongTruyen("KHONG_TIM_THAY", "Không thấy tệp.", http_status=404)
        if tep_id in self.cap_cho_viec.get(viec_id, set()):
            self._dang_giu(ma, viec_id)
            raw = self.doc_tep(tep_id)
            if len(raw) <= toi_da_byte:
                return raw
        return super()._mo_tep(ma, viec_id, tep_id, toi_da_byte)


def png_demo():
    """Ảnh 2×2 DEMO thực; không tạo tọa độ chữ/confidence."""
    def chunk(ten, raw):
        return struct.pack(">I", len(raw)) + ten + raw + struct.pack(">I", zlib.crc32(ten + raw))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\xff" * 2)) + chunk(b"IEND", b""))


@pytest.fixture
def ho_so_demo():
    core = CoreCapQuyenDEMO()
    refs = {}

    def luu(ten, raw, mime):
        tep = core.them_tep("DEMO-" + ten, raw, mime)
        ref = {"tep": tep, "bam": bam(raw)}
        refs[tep["tep_id"]] = ref
        return deepcopy(ref)

    docx = io.BytesIO()
    with zipfile.ZipFile(docx, "w") as z:
        z.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>DEMO</w:t></w:r></w:p></w:body></w:document>')
    # Bytes nguồn chỉ để kiểm vận chuyển/băm; không đem qua bộ đọc DOCX/PDF.
    word = luu("word.docx", docx.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    pdf = luu("ban-ky.pdf", b"%PDF-1.4\n% DEMO transport fixture\n%%EOF\n", "application/pdf")
    for ref in (word, pdf):
        ref["phien_ban"] = "DEMO-1"
    van_ban = {}
    for ben, nguon in (("word", word), ("ban_ky", pdf)):
        vb = {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
            "phien_ban": 1, "van_ban": "DEMO", "trang": [],
            "nguon_doc": "docx" if ben == "word" else "lop_chu_san",
            "so_trang": 0 if ben == "word" else 1,
            "ly_do_chuyen_nguon": None, "phien_ban_engine": "DEMO",
            "bam_dau_vao": nguon["bam"], "canh_bao": ["DEMO giao thức; không phải kết quả đọc nguồn thật."]}}
        if ben == "ban_ky":
            vb["van_ban_tai_lieu"]["trang"] = [{"so": 1, "rong": 2, "cao": 2, "don_vi": "px", "khoi": []}]
        van_ban[ben] = luu(ben + ".json", json_bytes(vb), "application/json")
    anh = luu("trang-1.png", png_demo(), "image/png")
    bo = luu("bo.json", json_bytes({"nhan": "DEMO", "kiem_bat_buoc": ["sua_tay"]}), "application/json")
    bo["phien_ban"] = "DEMO-1"
    cap = {"phien_ban": 1, "ma_cap": "DEMO-cap-001", "nguon": {"word": word, "ban_ky": pdf},
           "van_ban": van_ban, "anh_trang": [{"so": 1, **anh}], "ban_chuan_phan_trang": None,
           "bo_quy_tac": bo, "kiem_dau_vao": {"word_da_chot": True, "ocr_day_du": True, "canh_bao": ["DEMO"]},
           "bang_chung_ocr_lai": []}
    payload = {"phien_ban": 1, "ma_cap": cap["ma_cap"], "giai_doan": "da_nhan",
               "nguon": {k: {"tep_id": v["tep"]["tep_id"], "phien_ban": v["phien_ban"], "bam": v["bam"]} for k, v in cap["nguon"].items()},
               "bam_bo_quy_tac": bo["bam"], "phien_ban_engine": "e_doi_chieu 0.1.0",
               "tom_tat": {k: None for k in ("so_diem", "so_nghiem_trong", "so_can_xem", "so_hinh_thuc", "so_nhieu_ocr", "so_vung_sua_tay", "so_trang_ocr_kem")},
               "kiem_tra": {k: "dat" if k == "doc_hai_ban" else "chua_kiem" for k in ("doc_hai_ban", "so_van_ban", "quy_tac_cung", "trang", "lech_dau", "sua_tay", "phan_loai_ai")},
               "da_kiem_du": False, "ket_luan": None, "de_nghi_chan": True,
               "canh_bao": ["DEMO; chưa so chữ, chưa phân trang Word và chưa quét ảnh."]}
    snapshot = {**deepcopy(cap), **deepcopy(payload), **{k: None for k in ("chuan_hoa", "edit_script", "diem_lech", "quet_anh", "vung_sua_tay", "trang_ocr_kem", "ai")}}
    snapshot["nguon"] = deepcopy(cap["nguon"])
    snap = luu("ho-so.json", json_bytes(snapshot), "application/json")
    payload.update(ho_so=snap["tep"], bam_ho_so=snap["bam"])
    return core, {"loai": "ho_so_doi_chieu", "ho_so_doi_chieu": payload}, cap, refs


def mo_ref_demo(viec, ref):
    try:
        with viec.mo_tep(ref["tep"]["tep_id"]) as f:
            raw = f.read()
    except LoiDuongTruyen as exc:
        if exc.http_status in (403, 404, 410):
            raise LoiNghiepVu("DC_THIEU_NGUON", "Chưa đủ nguồn hoặc quyền đọc tài liệu để đối chiếu. Anh kiểm tra lại hồ sơ được cấp.") from None
        raise
    if bam(raw) != ref["bam"] or len(raw) != ref["tep"]["kich_thuoc"]:
        raise LoiNghiepVu("DC_SAI_BAM", "Nguồn đối chiếu đã thay đổi hoặc chưa khớp bản được ghim. Anh chọn lại hồ sơ.")
    return raw


def app_kiem_demo():
    """Năng lực chỉ ở test; KHÔNG đăng ký nhan_cap hoặc thay app thật."""
    phieu = deepcopy(chay.app.phieu)
    phieu["chay_thu_demo"] = []  # App test chỉ có năng lực kiểm contract.
    phieu["nang_luc"] = [{"ma": "demo.kiem_contract@1", "ten": "Kiểm phong bì DEMO",
                          "nhan": ["ho_so_doi_chieu"], "tra": "ho_so_doi_chieu",
                          "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 120}}]
    app = Engine(phieu, thu_muc_goi=GOI)

    @app.nang_luc("demo.kiem_contract@1")
    def kiem_fixture(viec):
        try:
            kiem_schema(viec.dau_vao, SCHEMA)
        except AssertionError:
            raise LoiNghiepVu("DC_SAI_DAU_VAO", "Dữ liệu đối chiếu chưa đúng định dạng. Anh kiểm tra lại hồ sơ.") from None
        p = viec.dau_vao["ho_so_doi_chieu"]
        raw = mo_ref_demo(viec, {"tep": p["ho_so"], "bam": p["bam_ho_so"]})
        snap = json.loads(raw)
        for k in ("ma_cap", "giai_doan", "tom_tat", "kiem_tra", "da_kiem_du", "ket_luan", "de_nghi_chan", "bam_bo_quy_tac", "phien_ban_engine", "canh_bao"):
            if snap[k] != p[k]:
                raise LoiNghiepVu("DC_SAI_DAU_VAO", "Tóm tắt chưa khớp hồ sơ được ghim.")
        for ben in ("word", "ban_ky"):
            nguon = snap["nguon"][ben]
            if p["nguon"][ben] != {"tep_id": nguon["tep"]["tep_id"], "bam": nguon["bam"], "phien_ban": nguon["phien_ban"]}:
                raise LoiNghiepVu("DC_SAI_BAM", "Nguồn chưa khớp hồ sơ được ghim.")
            mo_ref_demo(viec, nguon)
            vb = json.loads(mo_ref_demo(viec, snap["van_ban"][ben]))
            schema_vb = json.loads((GOI / "van_ban_tai_lieu.schema.json").read_text(encoding="utf-8"))
            kiem_schema(vb, schema_vb)
            assert vb["van_ban_tai_lieu"]["bam_dau_vao"] == nguon["bam"]
        pages = json.loads(mo_ref_demo(viec, snap["van_ban"]["ban_ky"]))["van_ban_tai_lieu"]["so_trang"]
        if sorted(a["so"] for a in snap["anh_trang"]) != list(range(1, pages + 1)):
            raise LoiNghiepVu("DC_THIEU_NGUON", "Chưa đủ nguồn hoặc quyền đọc tài liệu để đối chiếu. Anh kiểm tra lại hồ sơ được cấp.")
        for a in snap["anh_trang"]:
            mo_ref_demo(viec, a)
        mo_ref_demo(viec, snap["bo_quy_tac"])
        return viec.dau_vao

    return app


def chay_fixture(core, pb, refs, *, cap_quyen=True, het_quyen=None):
    viec_id = core.giao_viec("demo.kiem_contract@1", pb)
    core.thu_hoi_cho_viec[viec_id] = {het_quyen} if het_quyen else set()
    if cap_quyen:
        core.cap_cho_viec[viec_id] = set(refs) - {het_quyen}
    core.chay(app_kiem_demo())
    return core.xem(viec_id)


def test_bam_schema_va_mau_ngan_lf():
    for ten in TEN_SCHEMA:
        src = ROOT / "_chung/contract" / (ten + ".schema.json")
        assert bam(src.read_bytes().replace(b"\r\n", b"\n")) == bam((GOI / src.name).read_bytes().replace(b"\r\n", b"\n"))
    assert {p.name for p in GOI.glob("*.schema.json")} == {"cau_hinh.schema.json", *(n + ".schema.json" for n in TEN_SCHEMA)}


def test_manifest_core_gia_giu_khung():
    assert chay.app.phieu["loai_du_lieu_rieng"] == [
        {"ma": "van_ban_tai_lieu", "ten": "Văn bản tài liệu có vị trí"},
        {"ma": "yeu_cau_ai", "ten": "Yêu cầu hỏi AI"},
        {"ma": "tra_loi_ai", "ten": "Trả lời AI có trích dẫn"},
        {"ma": "ho_so_doi_chieu", "ten": "Hồ sơ đối chiếu bản ký"}]
    core = CoreGia()
    core.chay(chay.app)
    demo = core.chay_thu_demo(chay.app, GOI)
    assert demo and all(kq["trang_thai"] == "XONG" for kq in demo)
    assert [n["ma"] for n in chay.app.phieu["nang_luc"]] == ["doi_chieu.doc_docx@1", "doi_chieu.nhan_cap@1", "doi_chieu.so_van_ban@1", "doi_chieu.phat_hien_sua_tay@1", "doi_chieu.chuan_bi_ai@1", "doi_chieu.phan_loai_diem_lech@1"]


def test_phong_bi_demo_hop_le_core_gia(ho_so_demo):
    core, pb, cap, refs = ho_so_demo
    kiem_schema(pb, SCHEMA)
    assert len(json_bytes(pb)) < 65536
    # Tệp cặp cũng là đúng một phong bì tep; băm đo từ bytes thật.
    raw = json_bytes(cap)
    tep = core.them_tep("DEMO-cap.json", raw, "application/json")
    assert bam(core.doc_tep(tep["tep_id"])) == bam(raw)
    kq = chay_fixture(core, pb, refs)
    assert kq["trang_thai"] == "XONG"
    assert kq["ket_qua"] == pb
    assert kq["ket_qua"]["ho_so_doi_chieu"]["tom_tat"]["so_vung_sua_tay"] is None


@pytest.mark.parametrize("key", SCHEMA["properties"]["ho_so_doi_chieu"]["required"])
def test_required_payload(ho_so_demo, key):
    _, pb, _, _ = ho_so_demo
    del pb["ho_so_doi_chieu"][key]
    with pytest.raises(AssertionError):
        kiem_schema(pb, SCHEMA)


@pytest.mark.parametrize("key,value", [
    ("phien_ban", True), ("giai_doan", "da_xac_nhan"), ("ma_cap", ""),
    ("bam_ho_so", "sha256:DEMO"), ("ket_luan", "tu_do"),
    ("da_kiem_du", 1), ("de_nghi_chan", "true"), ("noi_dung", "DEMO"),
])
def test_sai_hinh_dang(ho_so_demo, key, value):
    _, pb, _, _ = ho_so_demo
    pb["ho_so_doi_chieu"][key] = value
    with pytest.raises(AssertionError):
        kiem_schema(pb, SCHEMA)


@pytest.mark.parametrize("key,value", [("so_diem", -1), ("so_diem", 10001), ("so_diem", 1.5), ("so_trang_ocr_kem", 61), ("so_vung_sua_tay", True)])
def test_tran_so_dem(ho_so_demo, key, value):
    _, pb, _, _ = ho_so_demo
    pb["ho_so_doi_chieu"]["tom_tat"][key] = value
    with pytest.raises(AssertionError):
        kiem_schema(pb, SCHEMA)


@pytest.mark.parametrize("loai_loi", ["sai_loai", "sai_bam", "het_quyen", "chua_co_cua", "thieu_anh", "sai_tom_tat"])
def test_tu_choi_bao_thu_core_gia(ho_so_demo, loai_loi):
    core, pb, _, refs = ho_so_demo
    p = pb["ho_so_doi_chieu"]
    het_quyen = None
    if loai_loi == "sai_loai":
        pb["loai"] = "tra_loi_ai"
    elif loai_loi == "sai_bam":
        p["bam_ho_so"] = "sha256:" + "0" * 64  # Đúng hình dạng, sai bytes.
    elif loai_loi == "het_quyen":
        het_quyen = p["nguon"]["word"]["tep_id"]
    elif loai_loi == "thieu_anh":
        snap = json.loads(core.doc_tep(p["ho_so"]["tep_id"]))
        snap["anh_trang"] = []
        raw = json_bytes(snap)
        p["ho_so"] = core.them_tep("DEMO-thieu-anh.json", raw, "application/json")
        p["bam_ho_so"] = bam(raw)
        refs[p["ho_so"]["tep_id"]] = {"tep": p["ho_so"], "bam": p["bam_ho_so"]}
    elif loai_loi == "sai_tom_tat":
        p["tom_tat"]["so_nghiem_trong"] = 1
    kq = chay_fixture(core, pb, refs, cap_quyen=loai_loi != "chua_co_cua", het_quyen=het_quyen)
    assert kq["trang_thai"] == "LOI"
    assert kq["ket_qua"] is None
    if loai_loi in ("het_quyen", "chua_co_cua", "thieu_anh"):
        assert kq["loi"]["ma"] == "DC_THIEU_NGUON"
    elif loai_loi == "sai_bam":
        assert kq["loi"]["ma"] == "DC_SAI_BAM"
    elif loai_loi == "sai_tom_tat":
        assert kq["loi"]["ma"] == "DC_SAI_DAU_VAO"
    assert "DEMO" not in kq["loi"]["thong_diep"]


def test_schema_khong_nhan_tu_khoa_la():
    with pytest.raises(AssertionError, match="Từ khóa"):
        kiem_schema({}, {"mot_tu_khoa_chua_ho_tro": True})


@pytest.mark.parametrize("key,value", [("kich_thuoc", 20971521), ("kich_thuoc", 0), ("mime", "image/png"), ("duong_dan", "DEMO")])
def test_metadata_snapshot(ho_so_demo, key, value):
    _, pb, _, _ = ho_so_demo
    pb["ho_so_doi_chieu"]["ho_so"][key] = value
    with pytest.raises(AssertionError):
        kiem_schema(pb, SCHEMA)
