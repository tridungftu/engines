"""DC-3: đã kiểm bằng Core giả (CoreGia), ngăn RAM và quyền tệp DEMO.

Adapter dưới đây chỉ mô phỏng C-DC-02, không được đưa vào gói runtime.
Văn bản/hình học OCR là giả để kiểm giao thức, không phải số đo OCR thật.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import importlib
import io
import json
from pathlib import Path
import struct
import sys
import threading
import zlib

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy, ChuaRo
from kho_tri_thuc_sdk.thu import CoreGia

from test_dc1 import kiem_schema as kiem_schema_test, png_demo
from test_dc2 import tao_goi, p, table_demo

GOI = Path(__file__).resolve().parents[1] / "goi/e_doi_chieu"
sys.path.insert(0, str(GOI))
chay = importlib.import_module("e_doi_chieu.chay")
hs = importlib.import_module("e_doi_chieu.ho_so")
ch = importlib.import_module("e_doi_chieu.chuan_hoa")
vt = importlib.import_module("e_doi_chieu.vi_tri")
docx = importlib.import_module("e_doi_chieu.doc_docx")
ng = importlib.import_module("e_doi_chieu.ngan")
PB_ENGINE = "e_doi_chieu " + chay.app.phieu["phien_ban"]
PN, MODULE = "DEMO-P", "DEMO-module"


class CoreTepConDEMO(CoreGia):
    def __init__(self):
        super().__init__()
        self.cap = {}
        self.chu_tep = {}
        self.module_viec = {}
        self.tep_ra = set()
        self.cam = set()
        self.doc_ids = []
        self.so_tai = 0

    def _nhan_viec(self, ma):
        data = super()._nhan_viec(ma)
        if data:
            data["ngu_canh"]["module"] = self.module_viec.get(data["id"], MODULE)
        return data

    def _mo_tep(self, ma, viec_id, tep_id, toi_da_byte):
        with self._lock:
            viec = self._dang_giu(ma, viec_id)
            scope = viec["phap_nhan_id"], self.module_viec.get(viec_id, MODULE)
            self.doc_ids.append((viec_id, tep_id))
            if tep_id in self.cam or self.chu_tep.get(tep_id) != scope:
                raise LoiDuongTruyen("KHONG_CO_QUYEN", "Không có quyền đọc tệp DEMO.", http_status=403)
            if tep_id in self.cap.get(viec_id, set()) or tep_id in self.tep_ra:
                raw = self.doc_tep(tep_id)
                if len(raw) > toi_da_byte:
                    raise LoiDuongTruyen("VUOT_GIOI_HAN_KICH_THUOC", "Tệp DEMO quá lớn.", http_status=413)
                return raw
            return super()._mo_tep(ma, viec_id, tep_id, toi_da_byte)

    def _tai_tep_ra(self, ma, viec_id, ten, du_lieu, mime, khoa):
        out = super()._tai_tep_ra(ma, viec_id, ten, du_lieu, mime, khoa)
        with self._lock:
            tid = out["tep_id"]
            if tid not in self.tep_ra:
                self.so_tai += 1
            self.tep_ra.add(tid)
            self.chu_tep[tid] = self._viec[viec_id]["phap_nhan_id"], self.module_viec.get(viec_id, MODULE)
        return out


def quy_tac_demo():
    return {"phien_ban": 1, "phien_ban_bo": "DEMO-1", "ma_bo_chuan_hoa": "DEMO-NFC-1",
            "chuan_hoa": {"unicode": "NFC", "khoang_trang": "gop", "dau_nhay": "thang",
                          "gach_noi": "thong_nhat", "ngat_dong": "noi_trong_doan",
                          "ngat_tu_cuoi_dong": "chi_gach_noi_mem", "dau_chan_trang": [], "bo_so_trang": False}}


def pdf_demo():
    """PDF một trang thực, byte offset/xref được tính, chỉ chữ DEMO."""
    stream = b"BT /F1 12 Tf 10 30 Td (DEMO) Tj ET"
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = b"%PDF-1.4\n", [0]
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 6\n0000000000 65535 f \n"
    out += b"".join(f"{x:010d} 00000 n \n".encode() for x in offsets[1:])
    out += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF\n"
    return out


class Mau:
    def __init__(self, core=None):
        self.core = core or CoreTepConDEMO()
        self.refs = {}
        self.ngan = ng.NganBoNho(chay._khai["ngan_du_lieu"])
        word = self.luu("ban-chot.docx", tao_goi(p("Công ty DEMO Ánh Dương") + p("1.000.000 VND ngày 2026-10-30")), docx.MIME_DOCX, True)
        ban_ky = self.luu("ban-ky.pdf", pdf_demo(), "application/pdf", True)
        word_vb = docx.doc_bytes(self.core.doc_tep(word["tep"]["tep_id"]), lambda: None, lambda *a: None,
                                  phien_ban_engine=PB_ENGINE)
        ocr = {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
            "phien_ban": 1, "van_ban": word_vb["van_ban_tai_lieu"]["van_ban"],
            "trang": [{"so": 1, "rong": 2, "cao": 2, "don_vi": "px", "khoi": [
                {"loai": "doan", "van_ban": word_vb["van_ban_tai_lieu"]["van_ban"], "hop": [0, 0, 2, 2]}]}],
            "nguon_doc": "tesseract", "ly_do_chuyen_nguon": None, "so_trang": 1,
            "phien_ban_engine": "e_ocr DEMO-1", "bam_dau_vao": ban_ky["bam"], "canh_bao": ["DEMO OCR giả kiểm giao thức."]}}
        bo = self.luu("bo.json", hs.json_bytes(quy_tac_demo()), "application/json", True)
        self.cap = {"phien_ban": 1, "ma_cap": "DEMO-cap-001", "nguon": {"word": word, "ban_ky": ban_ky},
                    "van_ban": {"word": self.luu("word.json", hs.json_bytes(word_vb), "application/json"),
                                "ban_ky": self.luu("ocr.json", hs.json_bytes(ocr), "application/json")},
                    "anh_trang": [{"so": 1, **self.luu("trang.png", png_demo(), "image/png")}],
                    "ban_chuan_phan_trang": None, "bo_quy_tac": bo,
                    "kiem_dau_vao": {"word_da_chot": True, "ocr_day_du": True, "canh_bao": ["DEMO"]},
                    "bang_chung_ocr_lai": []}
        self.cau_hinh = {"phien_ban_cau_hinh": "DEMO-1", "ma_bo_chuan_hoa": "DEMO-NFC-1", "bam_bo_chuan_hoa": bo["bam"],
                         "ma_tu_dien": "DEMO-chua-dung", "bam_tu_dien": "DEMO-chua-dung", "phuong_phap_detector": "DEMO-chua-dung",
                         "phien_ban_detector": "DEMO-chua-do"}
        self.dat_cau_hinh()

    def luu(self, name, raw, mime, version=False):
        tep = self.core.them_tep("DEMO-" + name, raw, mime)
        if isinstance(self.core, CoreTepConDEMO):
            self.core.chu_tep[tep["tep_id"]] = PN, MODULE
        ref = {"tep": tep, "bam": hs.bam(raw)}
        self.refs[tep["tep_id"]] = deepcopy(ref)
        if version:
            ref["phien_ban"] = "DEMO-1"
        return ref

    def dat_cau_hinh(self):
        ban = self.ngan.doc("cau_hinh", {})
        with self.ngan.lo() as lo:
            if ban:
                lo.sua("cau_hinh", {}, self.cau_hinh, row_version=ban.row_version)
            else:
                lo.them("cau_hinh", {}, self.cau_hinh)

    def vb(self, ben="ban_ky"):
        return json.loads(self.core.doc_tep(self.cap["van_ban"][ben]["tep"]["tep_id"]))

    def dat_vb(self, vb, ben="ban_ky"):
        self.cap["van_ban"][ben] = self.luu(ben + ".json", hs.json_bytes(vb), "application/json")

    def giao(self, *, cap=None, raw=None, bam=None, pn=PN, module=MODULE, quyen=True):
        cap = self.cap if cap is None else cap
        raw = hs.json_bytes(cap) if raw is None else raw
        ref = self.luu("yeu-cau.json", raw, "application/json")
        vid = self.core.giao_viec("doi_chieu.nhan_cap@1", {"loai": "tep", "tep": ref["tep"]},
                                  {"bam_yeu_cau": bam or hs.bam(raw)}, phap_nhan_id=pn)
        if isinstance(self.core, CoreTepConDEMO):
            self.core.module_viec[vid] = module
            self.core.chu_tep[ref["tep"]["tep_id"]] = pn, module
            self.core.cap[vid] = set(self.refs) if quyen else set()
        return vid

    def chay(self, **kw):
        vid = self.giao(**kw)
        self.core.chay(chay.app)
        return self.core.xem(vid)

    def snapshot(self, result):
        p = result["ket_qua"]["ho_so_doi_chieu"]
        raw = self.core.doc_tep(p["ho_so"]["tep_id"])
        assert hs.bam(raw) == p["bam_ho_so"] and len(raw) == p["ho_so"]["kich_thuoc"]
        return json.loads(raw)

    def cac_luot(self, pn=PN):
        return self.ngan.tim("luot_doi_chieu", {"phap_nhan_id": pn}).danh_sach


@pytest.fixture
def mau(monkeypatch):
    m = Mau()
    monkeypatch.setattr(chay, "ngan", m.ngan)
    return m


def kiem_loi(result, ma):
    assert result["trang_thai"] == "LOI", result
    assert result["ket_qua"] is None and result["loi"]["ma"] == ma, result


def test_cap_demo_snapshot_day_du_bam_schema_ngan_nho(mau):
    result = mau.chay()
    assert result["trang_thai"] == "XONG", result
    pb = result["ket_qua"]
    kiem_schema_test(pb, hs._SCHEMA_HS)
    p = pb["ho_so_doi_chieu"]
    assert p["giai_doan"] == "da_nhan" and p["ket_luan"] is None
    assert p["de_nghi_chan"] and not p["da_kiem_du"]
    assert p["kiem_tra"]["doc_hai_ban"] == "dat" and set(p["tom_tat"].values()) == {None}
    assert "van_ban" not in p and len(hs.json_bytes(pb)) < 4096
    snap = mau.snapshot(result)
    assert "bam_ho_so" not in snap and snap["nguon"] == mau.cap["nguon"]
    assert snap["van_ban"]["word"] == mau.vb("word")
    assert snap["chuan_hoa"]["word"]["nguyen_van"] == mau.vb("word")["van_ban_tai_lieu"]["van_ban"]
    assert snap["chuan_hoa"]["word"]["van_ban"].endswith("2026-10-30")
    assert snap["van_ban"]["word"]["van_ban_tai_lieu"]["trang"] == []
    assert snap["kiem_anh"]["anh_trang"] == [{"so": 1, "rong": 2, "cao": 2, "da_giai_ma": True}]
    assert all(snap[k] is None for k in ("edit_script", "diem_lech", "quet_anh", "vung_sua_tay", "ai"))
    luot = mau.cac_luot()
    assert len(luot) == 1 and luot[0].gia_tri["trang_thai"] == "da_nhan"
    assert "Công ty" not in hs.json_bytes(luot[0].gia_tri).decode()
    assert len(hs.json_bytes(luot[0].gia_tri)) < 65536


def test_bam_yeu_cau_truoc_parse(mau, monkeypatch):
    def cam_parse(*a, **kw):
        pytest.fail("Đã parse trước khi kiểm băm yêu cầu")
    monkeypatch.setattr(hs, "doc_json", cam_parse)
    kiem_loi(mau.chay(raw=b"{DEMO hong", bam="sha256:" + "0" * 64), "DC_SAI_NGUON")
    assert not mau.cac_luot()


@pytest.mark.parametrize("raw,ma", [
    (b'{"phien_ban":1,"phien_ban":1}', "DC_SAI_DAU_VAO"),
    (b'{"a":NaN}', "DC_SAI_DAU_VAO"), (b'{"a":Infinity}', "DC_SAI_DAU_VAO"),
    (b'{"a":1e999}', "DC_SAI_DAU_VAO"), (b'{"a":"\\ud800"}', "DC_SAI_DAU_VAO"),
    (b'{"a":"\\udfff"}', "DC_SAI_DAU_VAO"), (b'\xff', "DC_SAI_DAU_VAO"),
    (b'{}DEMO', "DC_SAI_DAU_VAO"), (b'[' * 65 + b']' * 65, "DC_QUA_GIOI_HAN"),
])
def test_json_nghiem(mau, raw, ma):
    kiem_loi(mau.chay(raw=raw), ma)


@pytest.mark.parametrize("key", ["phap_nhan_id", "module", "quyen", "duong_dan", "url", "base64"])
def test_khong_tin_danh_tinh_tu_khai(mau, key):
    mau.cap[key] = "DEMO-tu-khai"
    kiem_loi(mau.chay(), "DC_SAI_DAU_VAO")


@pytest.mark.parametrize("phap_nhan,module", [("DEMO-khac-P", MODULE), (PN, "DEMO-khac-module")])
def test_core_tu_choi_khac_phap_nhan_module(mau, phap_nhan, module):
    kiem_loi(mau.chay(pn=phap_nhan, module=module), "DC_THIEU_NGUON")
    assert not mau.cac_luot() and mau.core.so_tai == 0


def test_thieu_cua_core_that_khong_adapter(monkeypatch):
    m = Mau(CoreGia())
    monkeypatch.setattr(chay, "ngan", m.ngan)
    kiem_loi(m.chay(), "DC_THIEU_NGUON")
    assert not m.cac_luot()


def test_khong_quyen_va_thu_hoi_ke_ca_co_bam(mau):
    kiem_loi(mau.chay(quyen=False), "DC_THIEU_NGUON")
    mau.core.cam.add(mau.cap["van_ban"]["ban_ky"]["tep"]["tep_id"])
    kiem_loi(mau.chay(), "DC_THIEU_NGUON")


@pytest.mark.parametrize("path", [("nguon", "word"), ("nguon", "ban_ky"), ("van_ban", "word"), ("van_ban", "ban_ky"), ("bo_quy_tac",)])
def test_sai_bam_tung_nguon(mau, path):
    obj = mau.cap
    for k in path:
        obj = obj[k]
    obj["bam"] = "sha256:" + "0" * 64
    kiem_loi(mau.chay(), "DC_SAI_NGUON")


@pytest.mark.parametrize("key", ["bam_dau_vao", "van_ban", "trang_thai", "loi", "so_trang"])
def test_ocr_rong_loi_sai_nguon_khong_thanh_khop(mau, key):
    vb = mau.vb()
    v = vb["van_ban_tai_lieu"]
    v[key] = {"bam_dau_vao": "sha256:" + "0" * 64, "van_ban": " \n\t", "trang_thai": "LOI", "loi": {"ma": "DEMO"}, "so_trang": 2}[key]
    mau.dat_vb(vb)
    kiem_loi(mau.chay(), "DC_SAI_NGUON" if key in ("bam_dau_vao", "so_trang") else "DC_OCR_KHONG_DOC_DUOC")
    assert not mau.cac_luot()


@pytest.mark.parametrize("key,value", [("word_da_chot", False), ("ocr_day_du", False)])
def test_co_bao_nguon_loi_tu_choi(mau, key, value):
    mau.cap["kiem_dau_vao"][key] = value
    kiem_loi(mau.chay(), "DC_OCR_KHONG_DOC_DUOC")


def test_khong_tin_word_da_chot_va_van_ban_word_gia(mau):
    vb = mau.vb("word")
    vb["van_ban_tai_lieu"]["van_ban"] = "DEMO Word giả"
    mau.dat_vb(vb, "word")
    kiem_loi(mau.chay(), "DC_SAI_NGUON")
    raw = tao_goi('<w:ins>' + p("DEMO") + '</w:ins>')
    mau.cap["nguon"]["word"] = mau.luu("sua-doi.docx", raw, docx.MIME_DOCX, True)
    kiem_loi(mau.chay(), "DC_WORD_CHUA_CHOT")


@pytest.mark.parametrize("path", [("nguon", "word"), ("van_ban", "word"), ("anh_trang", 0)])
def test_metadata_kich_thuoc_khong_tin(mau, path):
    obj = mau.cap
    for k in path:
        obj = obj[k]
    obj["tep"]["kich_thuoc"] += 1
    kiem_loi(mau.chay(), "DC_SAI_NGUON")


def test_anh_sai_bam_thieu_trang_va_hop_ngoai_bien(mau):
    anh = deepcopy(mau.cap["anh_trang"])
    mau.cap["anh_trang"] = []
    kiem_loi(mau.chay(), "DC_THIEU_NGUON")
    mau.cap["anh_trang"] = anh
    mau.cap["anh_trang"][0]["bam"] = "sha256:" + "0" * 64
    kiem_loi(mau.chay(), "DC_SAI_NGUON")
    mau.cap["anh_trang"] = anh = deepcopy(anh)
    anh[0]["bam"] = hs.bam(mau.core.doc_tep(anh[0]["tep"]["tep_id"]))
    vb = mau.vb()
    vb["van_ban_tai_lieu"]["trang"][0]["khoi"][0]["hop"] = [0, 0, 3, 2]
    mau.dat_vb(vb)
    kiem_loi(mau.chay(), "DC_SAI_NGUON")


def test_thieu_cau_hinh(mau, monkeypatch):
    monkeypatch.setattr(chay, "ngan", ng.NganBoNho(chay._khai["ngan_du_lieu"]))
    kiem_loi(mau.chay(), "CHUA_CAU_HINH")


def test_sai_bo_da_duyet(mau):
    mau.cau_hinh["bam_bo_chuan_hoa"] = "sha256:" + "0" * 64
    mau.dat_cau_hinh()
    kiem_loi(mau.chay(), "DC_SAI_NGUON")


def test_hai_viec_dong_thoi_chi_mot_snapshot_mot_luot(mau, monkeypatch):
    gap = threading.Barrier(2)
    original = hs._doc_hai_ban
    def cung_doc(*a, **kw):
        out = original(*a, **kw)
        gap.wait(timeout=5)
        return out
    monkeypatch.setattr(hs, "_doc_hai_ban", cung_doc)
    ids = [mau.giao(), mau.giao()]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda _: mau.core.chay(chay.app), ids))
    a, b = [mau.core.xem(i) for i in ids]
    assert a["trang_thai"] == b["trang_thai"] == "XONG", (a, b)
    assert a["ket_qua"] == b["ket_qua"]
    assert len(mau.cac_luot()) == mau.core.so_tai == 1


def test_lap_lai_kiem_quyen_snapshot_va_khong_tai_lai(mau):
    a = mau.chay()
    assert a["trang_thai"] == "XONG", a
    b = mau.chay()
    assert b["ket_qua"] == a["ket_qua"] and mau.core.so_tai == 1
    mau.core.cam.add(a["ket_qua"]["ho_so_doi_chieu"]["ho_so"]["tep_id"])
    kiem_loi(mau.chay(), "DC_THIEU_NGUON")


@pytest.mark.parametrize("so_lan", [1, 5])
def test_cas_xung_dot_khong_de_ket_qua_cu_khong_nhan_doi_tai(mau, monkeypatch, so_lan):
    original = mau.ngan._thuc_hien
    dem = [0]
    def xung_dot(du_lieu, chi_muc, phien_ban, lenh):
        if lenh[0] == "sua" and lenh[3].get("trang_thai") == "da_nhan" and dem[0] < so_lan:
            dem[0] += 1
            raise ng.NganXungDot()
        return original(du_lieu, chi_muc, phien_ban, lenh)
    monkeypatch.setattr(mau.ngan, "_thuc_hien", xung_dot)
    result = mau.chay()
    if so_lan == 1:
        assert result["trang_thai"] == "XONG", result
        assert mau.cac_luot()[0].gia_tri["trang_thai"] == "da_nhan"
    else:
        kiem_loi(result, "NGAN_XUNG_DOT")
        assert result["loi"]["thu_lai_duoc"]
        assert mau.cac_luot()[0].gia_tri["trang_thai"] == "can_thu_lai"
    assert mau.core.so_tai == 1 and len(mau.cac_luot()) == 1


def test_cas_mat_quyen_so_huu_khong_ghi_de(mau, monkeypatch):
    original = mau.ngan.lo
    dem = [0]
    class LoChen:
        def __enter__(self):
            self.lo = original()
            self.lo.__enter__()
            return self
        def __exit__(self, *exc):
            return self.lo.__exit__(*exc)
        def __getattr__(self, ten):
            return getattr(self.lo, ten)
        def sua(self, bang, khoa, gia_tri, *, row_version):
            if gia_tri.get("trang_thai") == "da_nhan" and dem[0] == 0:
                dem[0] += 1
                with original() as khac:
                    khac.sua(bang, khoa, {"chu_so_huu": "DEMO-chu-khac"}, row_version=row_version)
            return self.lo.sua(bang, khoa, gia_tri, row_version=row_version)
    monkeypatch.setattr(mau.ngan, "lo", LoChen)
    kiem_loi(mau.chay(), "NGAN_XUNG_DOT")
    ban = mau.cac_luot()[0].gia_tri
    assert ban["chu_so_huu"] == "DEMO-chu-khac" and ban["trang_thai"] == "dang_nhan"


@pytest.mark.parametrize("moc", [25, 80, 100])
def test_huy_khong_nop_ket_qua_va_lan_sau_thu_lai(mau, monkeypatch, moc):
    vid = mau.giao()
    original = mau.core._tien_do
    def huy(ma, id_viec, pt, cau):
        if id_viec == vid and pt == moc:
            mau.core.huy(vid)
        return original(ma, id_viec, pt, cau)
    monkeypatch.setattr(mau.core, "_tien_do", huy)
    mau.core.chay(chay.app)
    result = mau.core.xem(vid)
    assert result["trang_thai"] == "HUY" and result["ket_qua"] is None, result
    assert mau.chay()["trang_thai"] == "XONG"
    assert len(mau.cac_luot()) == 1


def test_mat_xac_nhan_tep_ket_qua_ket_thuc_khong_trung(mau):
    for thao_tac in ("tep", "ket_qua", "ket_thuc"):
        mau.core.gay_mat_xac_nhan(thao_tac)
    result = mau.chay()
    assert result["trang_thai"] == "XONG", result
    assert len(mau.cac_luot()) == mau.core.so_tai == 1


@pytest.mark.parametrize("key,value", [("ky_tu_moi_tai_lieu", 10), ("ky_tu_hai_tai_lieu", 10),
                                      ("pixel_anh", 3), ("tong_byte_tep_con", 1), ("docx_so_muc", 1)])
def test_tran_cau_hinh_truoc_xu_ly_khong_cat(mau, key, value):
    mau.cau_hinh[key] = value
    mau.dat_cau_hinh()
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")
    assert not mau.cac_luot()


def test_tran_yeu_cau_mot_mib_va_nguon_metadata(mau):
    kiem_loi(mau.chay(raw=b" " * (hs.MIB + 1)), "DC_QUA_GIOI_HAN")
    mau.cap["nguon"]["word"]["tep"]["kich_thuoc"] = 20 * hs.MIB + 1
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")


def test_tran_byte_that_khi_sdk_413_va_nhan_anh_hong(mau):
    mau.cap["anh_trang"][0].update(mau.luu("lon.png", b"X" * (20 * hs.MIB + 1), "image/png"))
    mau.cap["anh_trang"][0]["tep"]["kich_thuoc"] = 1
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")
    mau.cap["anh_trang"][0].update(mau.luu("hong.png", png_demo()[:-1], "image/png"))
    kiem_loi(mau.chay(), "DC_SAI_NGUON")


def word_chuan(text):
    # XML chuẩn hóa CRLF của literal; entity giữ đúng CR trong fixture offset.
    return docx.doc_bytes(tao_goi(p(text).replace("\r", "&#13;")), lambda: None, lambda *a: None,
                         phien_ban_engine=PB_ENGINE)["van_ban_tai_lieu"]


def test_anh_xa_nfc_khoang_trang_ngat_dong_dau_cau():
    goc = "DEMO 😀 A\u0301nh\t \u00a0Dương\r\n‘thuê’ – 1.000.000 VND"
    out = ch.chuan_hoa(word_chuan(goc), quy_tac_demo()["chuan_hoa"])
    assert out["nguyen_van"] == goc
    assert out["van_ban"] == "DEMO 😀 Ánh Dương 'thuê' - 1.000.000 VND"
    for text, nguon in [("Á", "A\u0301"), (" ", "\t \u00a0"), ("'thuê'", "‘thuê’"), ("-", "–")]:
        a = out["van_ban"].find("Ánh") + 3 if nguon == "\t \u00a0" else out["van_ban"].index(text)
        result = vt.ve_nguon(out, a, a + len(text))
        assert "".join(x["van_ban"] for x in result["lat_nguon"]) == nguon, result
        assert any(x.get("so_doan") == 1 for x in result["vi_tri"])
    a = out["van_ban"].index(" 'thuê'")
    assert vt.ve_nguon(out, a, a + 1)["lat_nguon"][0]["van_ban"] == "\r\n"
    # Tất cả offset có nguồn, cả emoji và dấu tiếng Việt; map phủ kín, không đứt.
    assert out["anh_xa"][0][0] == 0 and out["anh_xa"][-1][1] == len(out["van_ban"])
    assert all(a[1] == b[0] for a, b in zip(out["anh_xa"], out["anh_xa"][1:]))
    for i in range(len(out["van_ban"])):
        assert vt.ve_nguon(out, i, i + 1)["lat_nguon"][0]["van_ban"]
    assert "thuê" in out["van_ban"] and "thue" not in out["van_ban"]


def test_hangul_nfc_va_map_cuoi_chuoi_rong():
    out = ch.chuan_hoa(word_chuan("DEMO \u1100\u1161\u11a8"), quy_tac_demo()["chuan_hoa"])
    assert out["van_ban"] == "DEMO 각"
    assert vt.ve_nguon(out, 5, 6)["lat_nguon"][0]["van_ban"] == "\u1100\u1161\u11a8"
    assert vt.ve_nguon(out, 6, 6)["lat_nguon"][0]["bat_dau"] == 8


def test_ngat_tu_mem_khong_xoa_gach_noi_so_hop_dong():
    v = word_chuan("DEMO hợ\u00ad\np đồng số DEMO-\n001")
    out = ch.chuan_hoa(v, quy_tac_demo()["chuan_hoa"])
    assert out["van_ban"] == "DEMO hợp đồng số DEMO- 001"
    a = out["van_ban"].index("hợp")
    assert [x["van_ban"] for x in vt.ve_nguon(out, a, a + 3)["lat_nguon"]] == ["hợ", "p"]
    assert out["da_bo"][0]["ly_do"] == "ngat_tu_mem_trong_doan"


def test_bien_doan_va_bang_o_rong_gop_duoc_giu():
    v = docx.doc_bytes(tao_goi(p("Đầu DEMO") + table_demo() + p("Cuối DEMO")), lambda: None, lambda *a: None,
                       phien_ban_engine=PB_ENGINE)["van_ban_tai_lieu"]
    out = ch.chuan_hoa(v, quy_tac_demo()["chuan_hoa"])
    assert "Đầu DEMO\nÔ gộp DEMO" in out["van_ban"] and out["van_ban"].endswith("\nCuối DEMO")
    o = [x for x in out["vi_tri"] if x.get("gop_cot") == 2]
    assert o and o[0]["gop_hang"] == 2
    assert any(x["loai"] == "o" and x["bat_dau"] == x["ket_thuc"] for x in out["vi_tri"])
    a = out["van_ban"].index("1.000.000 VND")
    r = vt.ve_nguon(out, a, a + 13)
    assert any(x.get("hang") == 1 and x.get("cot") == 2 for x in r["vi_tri"])


def test_header_tien_ma_noi_dung_giong_header_van_giu():
    texts = ["DEMO đầu trang", "1.000.000 VND", "Hợp đồng DEMO-001"]
    raw = tao_goi(p("DEMO đầu trang"), phu={"word/header1.xml": '<w:hdr xmlns:w="' + docx.W_NS + '">' + ''.join(p(s) for s in texts) + '</w:hdr>'})
    v = docx.doc_bytes(raw, lambda: None, lambda *a: None, phien_ban_engine=PB_ENGINE)["van_ban_tai_lieu"]
    q = quy_tac_demo()["chuan_hoa"]
    q["dau_chan_trang"] = texts
    out = ch.chuan_hoa(v, q)
    assert out["van_ban"].count("DEMO đầu trang") == 1  # Chỉ story header, thân còn nguyên.
    assert "1.000.000 VND" in out["van_ban"] and "Hợp đồng DEMO-001" in out["van_ban"]
    assert len(out["da_bo"]) == 1
    a, b = out["da_bo"][0]["bat_dau"], out["da_bo"][0]["ket_thuc"]
    assert v["van_ban"][a:b] == "DEMO đầu trang"


@pytest.mark.parametrize("nang_luc,ten_ham", [("doi_chieu.doc_docx@1", "_doc_docx"), ("doi_chieu.nhan_cap@1", "_nhan_cap")])
def test_loi_la_bi_mat_demo_khong_lo_stderr_e2e(mau, monkeypatch, capsys, nang_luc, ten_ham):
    secret = "DEMO_BI_MAT_KHONG_DUOC_LO"
    def hong(*a, **kw):
        raise RuntimeError(secret)
    monkeypatch.setattr(chay, ten_ham, hong)
    if nang_luc == "doi_chieu.doc_docx@1":
        r = mau.core.chay_thu(chay.app, nang_luc, {"loai": "tep", "tep": mau.cap["nguon"]["word"]["tep"]})
    else:
        r = mau.chay()
    kiem_loi(r, "DC_LOI_XU_LY")
    printed = capsys.readouterr()
    assert secret not in printed.out + printed.err + repr(r)


def test_khong_truy_cap_dia_mang_ngoai_trong_handler(mau, monkeypatch):
    def cam(*a, **kw):
        raise AssertionError("DEMO: không được truy cập đĩa/mạng")
    monkeypatch.setattr("builtins.open", cam)
    monkeypatch.setattr("urllib.request.urlopen", cam)
    monkeypatch.setattr("subprocess.Popen", cam)
    result = mau.chay()
    assert result["trang_thai"] == "XONG", result


def test_tai_lai_cung_bytes_khong_nhan_doi_luot(mau):
    a = mau.chay()
    assert a["trang_thai"] == "XONG", a
    # Cùng bytes/phiên bản nhưng Core cấp ID mới: băm cặp không phụ thuộc ID/tên.
    for key in ("word", "ban_ky"):
        old = mau.cap["nguon"][key]
        mau.cap["nguon"][key] = mau.luu("tai-lai-" + key, mau.core.doc_tep(old["tep"]["tep_id"]), old["tep"]["mime"], True)
    mau.cap["ma_cap"] = "DEMO-ma-moi"
    b = mau.chay()
    assert b["ket_qua"] == a["ket_qua"] and len(mau.cac_luot()) == mau.core.so_tai == 1
    # Quyền nguồn cũ của snapshot vẫn phải còn, không dùng quyền tới ID mới để lách.
    mau.core.cam.add(a["ket_qua"]["ho_so_doi_chieu"]["nguon"]["word"]["tep_id"])
    kiem_loi(mau.chay(), "DC_THIEU_NGUON")


@pytest.mark.parametrize("thay", ["phien_ban_word", "phien_ban_bo", "ket_qua_ocr"])
def test_doi_phien_ban_hoac_bang_chung_khong_dung_lai_snapshot(mau, thay):
    assert mau.chay()["trang_thai"] == "XONG"
    if thay == "phien_ban_word":
        mau.cap["nguon"]["word"]["phien_ban"] = "DEMO-2"
    elif thay == "phien_ban_bo":
        bo = quy_tac_demo()
        bo["phien_ban_bo"] = "DEMO-2"
        ref = mau.luu("bo-2.json", hs.json_bytes(bo), "application/json", True)
        ref["phien_ban"] = "DEMO-2"
        mau.cap["bo_quy_tac"] = ref
        mau.cau_hinh["bam_bo_chuan_hoa"] = ref["bam"]
        mau.dat_cau_hinh()
    else:
        vb = mau.vb()
        vb["van_ban_tai_lieu"]["phien_ban_engine"] = "e_ocr DEMO-2"
        mau.dat_vb(vb)
    assert mau.chay()["trang_thai"] == "XONG"
    assert len(mau.cac_luot()) == mau.core.so_tai == 2


def test_khong_doc_them_tu_mot_ref_dung_lap(mau):
    result = mau.chay()
    assert result["trang_thai"] == "XONG"
    ids = [tid for _, tid in mau.core.doc_ids]
    assert len(ids) == len(set(ids))


def test_snapshot_vuot_tran_khong_tai_ho_so_cat(mau, monkeypatch):
    original = hs.chuan_hoa
    def phinh(*a, **kw):
        value = original(*a, **kw)
        value["DEMO-thu-tran"] = "X" * (11 * hs.MIB)
        return value
    monkeypatch.setattr(hs, "chuan_hoa", phinh)
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")
    assert mau.core.so_tai == 0 and mau.cac_luot()[0].gia_tri["trang_thai"] == "can_thu_lai"


def test_tran_giai_nen_theo_cau_hinh_truoc_doc_word(mau, monkeypatch):
    mau.cau_hinh["docx_giai_nen_mib"] = 1
    mau.dat_cau_hinh()
    raw = tao_goi(p("DEMO"), sua={"DEMO-padding.data": b"X" * (hs.MIB + 1)})
    mau.cap["nguon"]["word"] = mau.luu("giai-nen.docx", raw, docx.MIME_DOCX, True)
    def cam(*a, **kw):
        pytest.fail("Đã đọc Word trước kiểm trần giải nén")
    monkeypatch.setattr(hs, "doc_bytes", cam)
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")


def test_tong_byte_tinh_tat_ca_tep_con(mau):
    # Đủ byte yêu cầu và Word, không đủ tổng cả PDF/text/ảnh/bộ.
    mau.cau_hinh["tong_byte_tep_con"] = len(hs.json_bytes(mau.cap)) + mau.cap["nguon"]["word"]["tep"]["kich_thuoc"] + 1
    mau.dat_cau_hinh()
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")


def test_tran_ky_tu_thuc_te_500001(mau):
    vb = mau.vb()
    vb["van_ban_tai_lieu"]["van_ban"] = "D" * 500001
    mau.dat_vb(vb)
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")


def test_tran_so_trang_61_va_thieu_mot_trang_ocr(mau):
    vb = mau.vb()
    vb["van_ban_tai_lieu"]["so_trang"] = 61
    mau.dat_vb(vb)
    kiem_loi(mau.chay(), "DC_QUA_GIOI_HAN")
    vb["van_ban_tai_lieu"]["so_trang"] = 1
    vb["van_ban_tai_lieu"]["trang"] = []
    mau.dat_vb(vb)
    kiem_loi(mau.chay(), "DC_SAI_NGUON")


def test_tai_tep_loi_va_chua_ro_khong_bao_thanh_cong(mau, monkeypatch):
    def chua_ro(*a, **kw):
        raise ChuaRo("DEMO-tuong-quan")
    monkeypatch.setattr(mau.core, "_tai_tep_ra", chua_ro)
    result = mau.chay()
    assert result["trang_thai"] == "CHUA_RO" and result["ket_qua"] is None
    assert result["ma_tuong_quan"] == "DEMO-tuong-quan"
    assert mau.cac_luot()[0].gia_tri["trang_thai"] == "can_thu_lai"


def test_ocr_trang_rong_va_word_khong_bia_trang(mau):
    vb = mau.vb()
    vb["van_ban_tai_lieu"]["van_ban"] += "\f \n"
    vb["van_ban_tai_lieu"]["so_trang"] = 2
    page = deepcopy(vb["van_ban_tai_lieu"]["trang"][0])
    page["so"] = 2
    vb["van_ban_tai_lieu"]["trang"].append(page)
    mau.cap["anh_trang"].append({"so": 2, **mau.luu("trang-2.png", png_demo(), "image/png")})
    mau.dat_vb(vb)
    kiem_loi(mau.chay(), "DC_OCR_KHONG_DOC_DUOC")


def test_offset_sai_khong_doan_nguon_va_ocr_lap_khong_doan_hop():
    v = word_chuan("DEMO")
    v["khoi_docx"][0]["bat_dau"] = 1
    with pytest.raises(LoiNghiepVu) as exc:
        ch.chuan_hoa(v, quy_tac_demo()["chuan_hoa"])
    assert exc.value.ma == "DC_SAI_NGUON"
    v = {"nguon_doc": "tesseract", "van_ban": "DEMO\nDEMO", "so_trang": 1,
         "trang": [{"so": 1, "rong": 100, "cao": 100, "don_vi": "pt", "khoi": [
             {"loai": "doan", "van_ban": "DEMO", "hop": [0, 20, 90, 30]}]}]}
    out = ch.chuan_hoa(v, quy_tac_demo()["chuan_hoa"])
    assert out["chua_neo_cau_truc"] == ["/trang/0/khoi/0"]
    assert not any("hop" in x for x in vt.ve_nguon(out, 0, 4)["vi_tri"])
    assert any(x.get("so_trang") == 1 for x in vt.ve_nguon(out, 0, 4)["vi_tri"])


def test_so_trang_ocr_chi_bo_khi_dung_vung_so_thuc():
    v = {"nguon_doc": "tesseract", "van_ban": "Trang 1\nDEMO 1.000.000 VND", "so_trang": 1,
         "trang": [{"so": 1, "rong": 100, "cao": 100, "don_vi": "pt", "khoi": [
             {"loai": "doan", "van_ban": "Trang 1", "hop": [0, 1, 90, 5]},
             {"loai": "doan", "van_ban": "DEMO 1.000.000 VND", "hop": [0, 20, 90, 30]}]}]}
    q = quy_tac_demo()["chuan_hoa"]
    q["bo_so_trang"] = True
    out = ch.chuan_hoa(v, q)
    assert "Trang 1" not in out["van_ban"] and "1.000.000 VND" in out["van_ban"]
    assert out["da_bo"][0]["ly_do"] == "so_trang_da_xac_minh"
    v["trang"][0]["khoi"][0]["hop"] = [0, 20, 90, 30]
    assert "Trang 1" in ch.chuan_hoa(v, q)["van_ban"]
    v["trang"][0]["khoi"][0]["hop"] = [0, 1, 90, 5]
    v["van_ban"] = v["van_ban"].replace("Trang 1", "Trang 9")
    v["trang"][0]["khoi"][0]["van_ban"] = "Trang 9"
    assert "Trang 9" in ch.chuan_hoa(v, q)["van_ban"]


def test_nfc_tien_to_khong_mat_dau_va_tuyen_tinh_cum_dai():
    goc = "DEMO " + "A" + "\u0301" * 20000
    out = ch.chuan_hoa(word_chuan(goc), quy_tac_demo()["chuan_hoa"])
    import unicodedata
    assert out["van_ban"] == unicodedata.normalize("NFC", goc)
    assert vt.ve_nguon(out, 5, 6)["lat_nguon"][0]["van_ban"] == goc[5:]


def test_png_crc_giai_nen_day_du_va_pixel_kiem_truoc():
    assert vt.kiem_anh(png_demo(), "image/png", 4)["rong"] == 2
    with pytest.raises(LoiNghiepVu):
        vt.kiem_anh(png_demo().replace(b"IDAT", b"IdAT"), "image/png", 4)
    raw = bytearray(png_demo())
    struct.pack_into(">II", raw, 16, 20000, 20000)
    struct.pack_into(">I", raw, 29, zlib.crc32(raw[12:29]))
    with pytest.raises(LoiNghiepVu) as exc:
        vt.kiem_anh(bytes(raw), "image/png", 20000000)
    assert exc.value.ma == "DC_QUA_GIOI_HAN"


def test_anh_jpeg_png_demo_repo_khong_nhan_giai_ma_jpeg():
    for ten, mime in [("DEMO-1-trang.jpg", "image/jpeg"), ("DEMO-1-trang.png", "image/png")]:
        raw = (GOI.parents[2] / "e_ocr/goi/e_ocr/demo" / ten).read_bytes()
        info = vt.kiem_anh(raw, mime, 20000000)
        assert info["rong"] > 0 and info["cao"] > 0
        assert info["da_giai_ma"] is (mime == "image/png")
        with pytest.raises(LoiNghiepVu):
            vt.kiem_anh(raw[:-2], mime, 20000000)
        with pytest.raises(LoiNghiepVu) as exc:
            vt.kiem_anh(raw, mime, 1)
        assert exc.value.ma == "DC_QUA_GIOI_HAN"


def test_cac_truong_ngan_da_khai_du_de_sdk_21_tao_bang(mau):
    assert mau.chay()["trang_thai"] == "XONG"
    bang = next(x for x in chay._khai["ngan_du_lieu"] if x["bang"] == "luot_doi_chieu")
    assert mau.cac_luot()[0].gia_tri.keys() <= {x["ma"] for x in bang["truong"]}


def test_bam_hex_hoa_hop_dong_chung(mau):
    def hoa(value):
        return "sha256:" + value[7:].upper()
    vb = mau.vb("word")
    vb["van_ban_tai_lieu"]["bam_dau_vao"] = hoa(vb["van_ban_tai_lieu"]["bam_dau_vao"])
    mau.dat_vb(vb, "word")
    for ref in [*mau.cap["nguon"].values(), *mau.cap["van_ban"].values(), *mau.cap["anh_trang"], mau.cap["bo_quy_tac"]]:
        ref["bam"] = hoa(ref["bam"])
    assert mau.chay()["trang_thai"] == "XONG"


def test_schema_so_huu_han_va_khong_bo_qua_tu_khoa_la():
    for schema, value in [({"type": "number"}, 10 ** 400), ({"type": "number"}, float("inf")),
                          ({"type": "string", "format": "email"}, "DEMO")]:
        with pytest.raises(LoiNghiepVu) as exc:
            hs.kiem_schema(value, schema)
        assert exc.value.ma == "DC_SAI_NGUON"
