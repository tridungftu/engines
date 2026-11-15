"""DC-4: DEMO, đã kiểm bằng Core giả (CoreGia); không chứng nhận OCR thật."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import importlib
import random
import struct
import threading
import time
import zlib

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy, ChuaRo

from test_dc1 import kiem_schema
from test_dc2 import p, tc, tao_goi, table_demo
from test_dc3 import Mau, CoreTepConDEMO, PN, MODULE, chay, docx, hs, ng, quy_tac_demo, kiem_loi

sc = importlib.import_module("e_doi_chieu.so_chu")
cc = importlib.import_module("e_doi_chieu.can_chinh")


class CorePhanTrangDEMO(CoreTepConDEMO):
    """C-DC-05 giả: chỉ Core gắn bằng chứng, không lấy từ JSON người gửi."""
    def __init__(self):
        super().__init__()
        self.phan_trang_do_core = {}

    def _nhan_viec(self, ma):
        data = super()._nhan_viec(ma)
        if data and data["id"] in self.phan_trang_do_core:
            data["ngu_canh"]["doi_chieu_phan_trang"] = deepcopy(self.phan_trang_do_core[data["id"]])
        return data


def dat_cap(m, trai, phai=None, *, body=None):
    """DOCX thật, kết quả OCR DEMO giữ đúng nguyên văn và cấu trúc đã chọn."""
    body = body if body is not None else "".join(p(s) for s in trai.split("\n"))
    raw = tao_goi(body)
    ref = m.luu("word-dc4.docx", raw, docx.MIME_DOCX, True)
    m.cap["nguon"]["word"] = ref
    word = docx.doc_bytes(raw, lambda: None, lambda *a: None, phien_ban_engine="e_doi_chieu 0.3.0")
    m.dat_vb(word, "word")
    if phai is None:
        phai = word["van_ban_tai_lieu"]["van_ban"]
    pages = phai.split("\f")
    ocr = m.vb()
    v = ocr["van_ban_tai_lieu"]
    v.update(van_ban=phai, so_trang=len(pages), trang=[{
        "so": i + 1, "rong": 2, "cao": 2, "don_vi": "px", "khoi": [
            {"loai": "doan", "van_ban": text, "hop": [0, 0, 2, 2]}]} for i, text in enumerate(pages)])
    m.cap["anh_trang"] = [{"so": i + 1, **m.luu(f"page-{i}.png", png(i), "image/png")} for i in range(len(pages))]
    m.dat_vb(ocr)
    return word, ocr


def png(pixel):
    def chunk(ten, data):
        return struct.pack(">I", len(data)) + ten + data + struct.pack(">I", zlib.crc32(ten + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(bytes([0, pixel, pixel]) * 2)) + chunk(b"IEND", b""))


def pdf_trang_demo(pixels):
    """PDF DEMO đủ xref, mỗi trang thật chứa một ảnh xám 2×2 tương ứng PNG.

    Đây là provider render/OCR giả để kiểm giao thức; không phải đo render Word.
    """
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b""]
    kids = []
    for pixel in pixels:
        at = len(objs) + 1
        kids.append(f"{at} 0 R")
        objs.extend([
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 2 2] /Resources << /XObject << /Im0 {at + 2} 0 R >> >> /Contents {at + 1} 0 R >>".encode(),
            b"<< /Length 27 >>\nstream\nq 2 0 0 2 0 0 cm /Im0 Do Q\n\nendstream",
            b"<< /Type /XObject /Subtype /Image /Width 2 /Height 2 /ColorSpace /DeviceGray /BitsPerComponent 8 /Length 4 >>\nstream\n" + bytes([pixel]) * 4 + b"\nendstream"])
    objs[1] = f"<< /Type /Pages /Count {len(pixels)} /Kids [{' '.join(kids)}] >>".encode()
    raw, offsets = b"%PDF-1.4\n% DEMO\n", [0]
    for i, o in enumerate(objs, 1):
        offsets.append(len(raw))
        raw += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(raw)
    raw += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    raw += b"".join(f"{v:010d} 00000 n \n".encode() for v in offsets[1:])
    return raw + f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


def dat_phan_trang(m, ky, word):
    ref = m.luu("signed-paged.pdf", pdf_trang_demo(ky), "application/pdf", True)
    m.cap["nguon"]["ban_ky"] = ref
    ocr = m.vb()
    ocr["van_ban_tai_lieu"]["bam_dau_vao"] = ref["bam"]
    m.dat_vb(ocr)
    m.cap["anh_trang"] = [{"so": i + 1, **m.luu(f"signed-{i}.png", png(v), "image/png")} for i, v in enumerate(ky)]
    m.cap["ban_chuan_phan_trang"] = m.luu("render-paged.pdf", pdf_trang_demo(word), "application/pdf", True)
    m.cap["anh_trang_word"] = [{"so": i + 1, **m.luu(f"render-{i}.png", png(v), "image/png")} for i, v in enumerate(word)]
    m.phan_trang_core = {"phien_ban": 1, "bam_word": m.cap["nguon"]["word"]["bam"],
        "phien_ban_word": m.cap["nguon"]["word"]["phien_ban"], "bam_pdf_chuan": m.cap["ban_chuan_phan_trang"]["bam"],
        "bam_ban_ky": ref["bam"], "anh_word": [p["bam"] for p in m.cap["anh_trang_word"]],
        "anh_ban_ky": [p["bam"] for p in m.cap["anh_trang"]]}


def giao_so(m, pb, *, tham_so=None, pn=PN, module=MODULE, quyen=True):
    raw = m.core.doc_tep(m.cap["bo_quy_tac"]["tep"]["tep_id"])
    tham_so = {"bo_quy_tac_json": raw.decode(), "bam_bo_quy_tac": hs.bam(raw)} if tham_so is None else tham_so
    vid = m.core.giao_viec("doi_chieu.so_van_ban@1", pb, tham_so, phap_nhan_id=pn)
    m.core.module_viec[vid] = module
    m.core.cap[vid] = set(m.refs) if quyen else set()
    if getattr(m, "phan_trang_core", None) is not None:
        m.core.phan_trang_do_core[vid] = deepcopy(m.phan_trang_core)
    return vid


def so(m, pb=None, **kw):
    if pb is None:
        r = m.chay()
        assert r["trang_thai"] == "XONG", r
        pb = r["ket_qua"]
    vid = giao_so(m, pb, **kw)
    m.core.chay(chay.app)
    return m.core.xem(vid)


@pytest.fixture
def mau(monkeypatch):
    m = Mau(CorePhanTrangDEMO())
    monkeypatch.setattr(chay, "ngan", m.ngan)
    return m


def snapshot_so(m, r):
    assert r["trang_thai"] == "XONG", r
    s = m.snapshot(r)
    kiem_schema(r["ket_qua"], hs._SCHEMA_HS)
    sc.kiem_tai_dung(s["edit_script"], s["chuan_hoa"])
    for k in ("word", "ban_ky"):
        assert "".join(op[k]["nguyen_van"] for op in s["edit_script"]) == s["van_ban"][k]["van_ban_tai_lieu"]["van_ban"]
        for d in s["diem_lech"]:
            if d[k] is not None:
                b = d[k]
                assert s["chuan_hoa"][k]["nguyen_van"][b["bat_dau"]:b["ket_thuc"]] == b["nguyen_van"]
                if b["vi_tri"] and k == "word":
                    assert b["vi_tri"]["so_trang"] is None and b["vi_tri"]["hop"] is None
    return s


def test_cap_giong_nhau_chua_ket_luan_sach(mau):
    r = so(mau)
    s = snapshot_so(mau, r)
    # DC-5 tiếp nối: nguyên văn giống nhau nhưng thiếu tiền bằng chữ,
    # phải có điểm cần xem nội bộ thay vì hiểu danh sách rỗng là sạch.
    assert s["giai_doan"] == "da_so"
    assert all(d["nhom"] == "tien_trong_ban_ky" and d["muc_san"] == "can_xem" for d in s["diem_lech"])
    assert s["tom_tat"]["so_diem"] == s["tom_tat"]["so_can_xem"] == 1
    assert s["tom_tat"]["so_nghiem_trong"] == s["tom_tat"]["so_hinh_thuc"] == s["tom_tat"]["so_nhieu_ocr"] == 0
    assert s["tom_tat"]["so_vung_sua_tay"] is None and s["tom_tat"]["so_trang_ocr_kem"] is None
    assert s["kiem_tra"]["so_van_ban"] == "dat" and s["kiem_tra"]["quy_tac_cung"] == "chua_kiem"
    assert s["kiem_tra"]["trang"] == "chua_kiem"
    assert s["ket_luan"] is None and not s["da_kiem_du"] and s["de_nghi_chan"]
    assert len(mau.cac_luot()) == 3  # Nhận cặp, so DC-5 và kiểm trang DC-7, mỗi bước một bản.
    row = [b.gia_tri for b in mau.cac_luot() if b.gia_tri["trang_thai"] == "da_so"][0]
    assert len(hs.json_bytes(row)) < 65536 and "Công ty" not in hs.json_bytes(row).decode()


@pytest.mark.parametrize("trai,phai,phep,can_cu", [
    ("Điều 1. DEMO\n1. Thuê DEMO.\n2. Thuế DEMO.\n3. Hết DEMO.", "Điều 1. DEMO\n1. Thuê DEMO.\n3. Hết DEMO.", "xoa", "thieu_khoan"),
    ("Điều 1. DEMO\n1. Thuê DEMO.\n3. Hết DEMO.", "Điều 1. DEMO\n1. Thuê DEMO.\n2. Thuế DEMO.\n3. Hết DEMO.", "chen", "thua_khoan"),
    ("Điều 1. DEMO A\nNội dung A.\nĐiều 2. DEMO B\nNội dung B.", "Điều 2. DEMO B\nNội dung B.\nĐiều 1. DEMO A\nNội dung A.", "dao", "dao_dieu"),
    ("Điều 1. DEMO\n1. A DEMO\n2. B DEMO", "Điều 1. DEMO\n2. B DEMO\n1. A DEMO", "dao", "dao_khoan"),
    ("Điều 1. DEMO\nA\nĐiều 2. DEMO\nB", "Điều 1. DEMO\nA", "xoa", "thieu_dieu"),
    ("Điều 1. DEMO\nA", "Điều 1. DEMO\nA\nĐiều 2. DEMO\nB", "chen", "thua_dieu"),
])
def test_cau_truc_khong_lam_mat_doan(mau, trai, phai, phep, can_cu):
    dat_cap(mau, trai, phai)
    s = snapshot_so(mau, so(mau))
    assert any(d["phep"] == phep and d["can_cu"]["phuong_phap"] == can_cu for d in s["diem_lech"])
    assert all(d["muc_san"] == d["muc"] == "nghiem_trong" for d in s["diem_lech"])
    assert any("DC_CAU_TRUC" in d["quy_tac_trung"] for d in s["diem_lech"])


@pytest.mark.parametrize("trai,phai", [
    ("DEMO lặp\nDEMO lặp\nDEMO cuối", "DEMO lặp\nDEMO thêm\nDEMO lặp\nDEMO cuối"),
    ("DEMO lặp\nDEMO lặp\nDEMO lặp", "DEMO lặp\nDEMO lặp"),
    ("DEMO A", "DEMO A\nĐoạn được thêm tận cuối."),
    ("DEMO A\nĐoạn cuối bị xóa.", "DEMO A"),
    ("DEMO a\nb", "DEMO a b"),
    ("DEMO 😀 A\u0301nh thuê", "DEMO 😀 Ánh thuế"),
    ("DEMO \u0344 thuê", "DEMO \u0308\u0301 thuế"),
    ("DEMO hợ\u00ad\np đồng thuê", "DEMO hợp đồng thuế"),
    ("DEMO một. DEMO một. DEMO hai.", "DEMO một. DEMO hai. DEMO một."),
    ("Điều 1. DEMO\n1. Lặp\n1. Lặp", "Điều 1. DEMO\n1. Lặp"),
])
def test_lap_duoi_ngat_dong_unicode_khong_mat_doan(mau, trai, phai):
    dat_cap(mau, trai, phai)
    s = snapshot_so(mau, so(mau))
    assert s["edit_script"] and s["diem_lech"]


@pytest.mark.parametrize("a,b", [("thuê", "thuế"), ("lãi", "lại"), ("phạt", "phát"), ("bán", "bàn"), ("không", "khống"), ("hạn", "hàn"), ("đ", "d")])
def test_lech_dau_chi_gan_nhom_khong_xoa(mau, a, b):
    dat_cap(mau, "DEMO " + a, "DEMO " + b)
    s = snapshot_so(mau, so(mau))
    points = [d for d in s["diem_lech"] if d["nhom"] == "chi_lech_dau"]
    assert points and all(d["muc"] == d["muc_san"] for d in points)
    if a == "không":
        assert all(d["muc"] == "nghiem_trong" and "DC_PHU_DINH_BAT_BUOC" in d["quy_tac_trung"] for d in points)
    else:
        assert all(d["cho_phan_loai"] and d["muc"] == "can_xem" for d in points)
    assert s["kiem_tra"]["lech_dau"] == "chua_kiem"


@pytest.mark.parametrize("a,b", [("1.000.000", "1.000.001"), ("1.000.000", "1,000,000"), ("10%", "1O%"),
    ("01/02", "02/01"), ("bảo hành", "bao hanh"), ("sẽ", "se"), ("không, đồng ý", "không đồng ý"),
    ("1 000", "1000"), ("A", "\u0410"), ("-5", "−5"), ("IV", "Ⅳ"), ("Nguyễn", "nguyễn"), ("001", "1"), ("1l", "11")])
def test_matrix_dc3_van_tao_diem(mau, a, b):
    dat_cap(mau, "DEMO " + a, "DEMO " + b)
    assert snapshot_so(mau, so(mau))["diem_lech"]


@pytest.mark.parametrize("a,b", [("1\u00a0000", "1 000"), ("DEMO\tA", "DEMO A"), ("DEMO   A", "DEMO A"),
    ("DEMO–A", "DEMO-A"), ("DEMO—A", "DEMO-A"), ("‘DEMO’", "'DEMO'"), ("“DEMO”", '"DEMO"')])
def test_tuong_duong_duoc_duyet_van_tai_dung_nguyen_van(mau, a, b):
    dat_cap(mau, a, b)
    s = snapshot_so(mau, so(mau))
    assert any(x["phep"] == "tuong_duong_chuan_hoa" for x in s["edit_script"])
    if "1" in a:
        # DC-5: bộ DC-3 cũ chưa khai quy ước phân cách số, không được ẩn.
        assert s["diem_lech"] and all(d["muc_san"] == "nghiem_trong" for d in s["diem_lech"])
    else:
        assert not s["diem_lech"]


def dat_ocr_bang(m, word):
    ocr = m.vb()
    blocks = deepcopy(word["van_ban_tai_lieu"]["khoi_docx"])
    for k in blocks:
        k["hop"] = [0, 0, 2, 2]
    ocr["van_ban_tai_lieu"]["trang"][0]["khoi"] = blocks
    m.dat_vb(ocr)


def test_bang_o_rong_gop_nhieu_dong_o_giu_day_du(mau):
    w, _ = dat_cap(mau, "", body=p("DEMO bảng") + table_demo() + p("DEMO cuối"))
    dat_ocr_bang(mau, w)
    s = snapshot_so(mau, so(mau))
    assert not [d for d in s["diem_lech"] if d["nhom"] != "tien_trong_ban_ky"]
    assert any(o["van_ban"] == "" for o in s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]["trang"][0]["khoi"][1]["o"])


def test_bang_thay_chu_o_cuoi_va_gop_khong_xoa_diem(mau):
    w, _ = dat_cap(mau, "", body=p("DEMO bảng") + table_demo())
    dat_ocr_bang(mau, w)
    v = mau.vb()
    tab = v["van_ban_tai_lieu"]["trang"][0]["khoi"][1]
    tab["o"][-1]["van_ban"] += " DEMO thêm"
    tab["van_ban"] += " DEMO thêm"
    tab["ket_thuc"] += len(" DEMO thêm")
    v["van_ban_tai_lieu"]["van_ban"] += " DEMO thêm"
    mau.dat_vb(v)
    s = snapshot_so(mau, so(mau))
    assert any("o" in d["can_cu"].get("cap_can", []) for d in s["diem_lech"])
    assert "DEMO thêm" in "".join(d["ban_ky"]["nguyen_van"] for d in s["diem_lech"] if d["ban_ky"])


def test_bang_thay_gop_khi_chu_khong_doi(mau):
    table = '<w:tbl><w:tr>' + tc("DEMO") + tc() + '</w:tr></w:tbl>'
    w, _ = dat_cap(mau, "", body=table)
    dat_ocr_bang(mau, w)
    v = mau.vb()
    tab = v["van_ban_tai_lieu"]["trang"][0]["khoi"][0]
    tab["o"] = [tab["o"][0]]
    tab["o"][0]["gop_cot"] = 2
    mau.dat_vb(v)
    s = snapshot_so(mau, so(mau))
    assert any(d["can_cu"]["phuong_phap"] == "doi_cau_truc_bang" for d in s["diem_lech"])


def test_bang_ocr_mo_ho_tu_choi_khong_doan(mau):
    w, _ = dat_cap(mau, "", body=table_demo() + table_demo())
    dat_ocr_bang(mau, w)
    v = mau.vb()
    for k in v["van_ban_tai_lieu"]["trang"][0]["khoi"]:
        k.pop("bat_dau", None)
        k.pop("ket_thuc", None)
    mau.dat_vb(v)
    kiem_loi(so(mau), "DC_KHONG_CAN_DUOC")


def test_bang_lap_co_offset_nguon_da_kiem_giu_ca_hai(mau):
    w, _ = dat_cap(mau, "", body=table_demo() + table_demo())
    dat_ocr_bang(mau, w)
    assert not [d for d in snapshot_so(mau, so(mau))["diem_lech"] if d["nhom"] != "tien_trong_ban_ky"]


def test_bang_long_can_tung_dong_o_va_khong_bo_duoi(mau):
    inner = '<w:tbl><w:tr>' + tc("DEMO thuê") + tc() + '</w:tr></w:tbl>'
    outer = '<w:tbl><w:tr><w:tc><w:tcPr/>' + p("DEMO đầu") + inner + p("DEMO đuôi") + '</w:tc>' + tc() + '</w:tr></w:tbl>'
    w, _ = dat_cap(mau, "", body=outer + p("DEMO cuối"))
    dat_ocr_bang(mau, w)
    v = mau.vb()
    def thay(ds):
        for k in ds:
            k["van_ban"] = k["van_ban"].replace("thuê", "thuế")
            for o in k.get("o", []):
                o["van_ban"] = o["van_ban"].replace("thuê", "thuế")
                thay(o.get("khoi", []))
    thay(v["van_ban_tai_lieu"]["trang"][0]["khoi"])
    v["van_ban_tai_lieu"]["van_ban"] = v["van_ban_tai_lieu"]["van_ban"].replace("thuê", "thuế")
    mau.dat_vb(v)
    s = snapshot_so(mau, so(mau))
    assert any(d["can_cu"].get("cap_can", []).count("bang") == 2 for d in s["diem_lech"])


def test_hai_van_ban_khong_co_neo_tu_choi_dung_cau(mau):
    dat_cap(mau, "ABCXYZ", "UVWOPQ")
    r = so(mau)
    kiem_loi(r, "DC_KHONG_CAN_DUOC")
    assert r["loi"]["thong_diep"] == "Chưa căn được cấu trúc hai bản. Anh kiểm tra bản chuẩn và bản nhận dạng."


def test_trang_khac_dan_trang_khong_tu_coi_thieu(mau):
    dat_cap(mau, "DEMO A\nDEMO B", "DEMO A\fDEMO B")
    dat_phan_trang(mau, [0, 1], [8])
    s = snapshot_so(mau, so(mau))
    assert s["kiem_tra"]["trang"] == "chua_kiem"
    assert not any(d["nhom"] == "trang" for d in s["diem_lech"])


@pytest.mark.parametrize("dao", [True, False])
def test_trang_thuc_anh_cung_bam_dung_hoac_bi_dao(mau, dao):
    dat_cap(mau, "DEMO A\nDEMO B", "DEMO B\fDEMO A" if dao else "DEMO A\fDEMO B")
    dat_phan_trang(mau, [1, 0] if dao else [0, 1], [0, 1])
    s = snapshot_so(mau, so(mau))
    assert s["kiem_tra"]["trang"] == ("khong_dat" if dao else "dat")
    assert bool([d for d in s["diem_lech"] if d["nhom"] == "trang" and d["phep"] == "dao"]) == dao


def test_anh_trung_bam_nhung_thieu_nguon_goc_core_van_chua_kiem(mau):
    dat_cap(mau, "DEMO A\nDEMO B", "DEMO B\fDEMO A")
    dat_phan_trang(mau, [1, 0], [0, 1])
    # Caller nhét cờ/tuyên bố vào snapshot không tạo nguồn tin cậy.
    claimed = mau.phan_trang_core
    mau.phan_trang_core = None
    pb = mau.chay()["ket_qua"]
    s = mau.snapshot({"ket_qua": pb})
    s["doi_chieu_phan_trang"] = claimed
    raw = hs.json_bytes(s)
    ref = mau.luu("claimed-pagination.json", raw, "application/json")
    pb = hs._phong_bi(s, ref["tep"], raw)
    s = snapshot_so(mau, so(mau, pb))
    assert s["kiem_tra"]["trang"] == "chua_kiem" and not any(d["nhom"] == "trang" for d in s["diem_lech"])


def test_nguon_goc_phan_trang_core_sai_bam_tu_choi(mau):
    dat_cap(mau, "DEMO A\nDEMO B", "DEMO B\fDEMO A")
    dat_phan_trang(mau, [1, 0], [0, 1])
    mau.phan_trang_core["bam_word"] = "sha256:" + "0" * 64
    kiem_loi(so(mau), "DC_SAI_NGUON")


def test_nguon_goc_phan_trang_thay_doi_khong_dung_cache_thieu_kiem(mau):
    dat_cap(mau, "DEMO A\nDEMO B", "DEMO B\fDEMO A")
    dat_phan_trang(mau, [1, 0], [0, 1])
    bc = mau.phan_trang_core
    mau.phan_trang_core = None
    pb = mau.chay()["ket_qua"]
    assert snapshot_so(mau, so(mau, pb))["kiem_tra"]["trang"] == "chua_kiem"
    mau.phan_trang_core = bc
    assert snapshot_so(mau, so(mau, pb))["kiem_tra"]["trang"] == "khong_dat"


def test_id_on_dinh_lap_lai_va_nguon_id_moi(mau):
    dat_cap(mau, "DEMO thuê", "DEMO thuế")
    pb = mau.chay()["ket_qua"]
    r1, r2 = so(mau, pb), so(mau, pb)
    a, b = snapshot_so(mau, r1), snapshot_so(mau, r2)
    assert r1["ket_qua"] == r2["ket_qua"] and a["diem_lech"] == b["diem_lech"]
    old = [d["ma_diem"] for d in a["diem_lech"]]
    # Một phiên Core khác có ID tệp mới vẫn cho cùng mã điểm nghiệp vụ.
    m = Mau()
    dat_cap(m, "DEMO thuê", "DEMO thuế")
    chay.ngan = m.ngan
    assert [d["ma_diem"] for d in snapshot_so(m, so(m))["diem_lech"]] == old


@pytest.mark.parametrize("thay", ["bam_ho_so", "bam_bo", "chuan_hoa", "nguyen_van", "bo", "nguon", "giai_doan"])
def test_snapshot_sai_ghim_tu_choi(mau, thay):
    pb = mau.chay()["ket_qua"]
    if thay == "bam_ho_so":
        pb["ho_so_doi_chieu"]["bam_ho_so"] = "sha256:" + "0" * 64
    elif thay == "bam_bo":
        pb["ho_so_doi_chieu"]["bam_bo_quy_tac"] = "sha256:" + "0" * 64
    elif thay == "giai_doan":
        pb["ho_so_doi_chieu"]["giai_doan"] = "da_tong_hop"
    else:
        s = mau.snapshot({"ket_qua": pb})
        if thay == "chuan_hoa":
            s["chuan_hoa"]["word"]["van_ban"] += " DEMO giả"
        elif thay == "nguyen_van":
            s["van_ban"]["ban_ky"]["van_ban_tai_lieu"]["van_ban"] += " DEMO giả"
        elif thay == "bo":
            s["bo_quy_tac"]["noi_dung"]["chuan_hoa"]["gach_noi"] = "giu_nguyen"
        else:
            s["nguon"]["word"]["bam"] = "sha256:" + "0" * 64
        ref = mau.luu("snapshot-gia.json", hs.json_bytes(s), "application/json")
        pb = hs._phong_bi(s, ref["tep"], hs.json_bytes(s))
    r = so(mau, pb)
    kiem_loi(r, "DC_SAI_DAU_VAO" if thay == "giai_doan" else "DC_SAI_NGUON")


def test_bo_json_khac_bytes_du_cung_noi_dung_bi_tu_choi(mau):
    pb = mau.chay()["ket_qua"]
    raw = hs.json_bytes(quy_tac_demo()) + b" "
    kiem_loi(so(mau, pb, tham_so={"bo_quy_tac_json": raw.decode(), "bam_bo_quy_tac": hs.bam(raw)}), "DC_SAI_NGUON")


@pytest.mark.parametrize("thu_hoi", ["snapshot", "word", "bo", "anh"])
def test_quyen_bi_thu_hoi_khong_lach_bang_bam(mau, thu_hoi):
    pb = mau.chay()["ket_qua"]
    tid = {"snapshot": pb["ho_so_doi_chieu"]["ho_so"]["tep_id"], "word": mau.cap["nguon"]["word"]["tep"]["tep_id"],
           "bo": mau.cap["bo_quy_tac"]["tep"]["tep_id"], "anh": mau.cap["anh_trang"][0]["tep"]["tep_id"]}[thu_hoi]
    mau.core.cam.add(tid)
    kiem_loi(so(mau, pb), "DC_THIEU_NGUON")


@pytest.mark.parametrize("pn,module", [("DEMO-khac", MODULE), (PN, "DEMO-khac")])
def test_khong_doc_cheo_phap_nhan_module(mau, pn, module):
    pb = mau.chay()["ket_qua"]
    kiem_loi(so(mau, pb, pn=pn, module=module), "DC_THIEU_NGUON")


def test_thieu_cau_hinh(mau, monkeypatch):
    pb = mau.chay()["ket_qua"]
    monkeypatch.setattr(chay, "ngan", ng.NganBoNho(chay._khai["ngan_du_lieu"]))
    kiem_loi(so(mau, pb), "CHUA_CAU_HINH")


def test_vuot_tran_diem_khong_cat_danh_sach(mau):
    dat_cap(mau, "DEMO a b c d e f", "DEMO x b y d z f")
    mau.cau_hinh["diem_lech_toi_da"] = 2
    mau.dat_cau_hinh()
    pb = mau.chay()["ket_qua"]
    count = mau.core.so_tai
    kiem_loi(so(mau, pb), "DC_QUA_GIOI_HAN")
    assert mau.core.so_tai == count


def test_vuot_tran_ky_tu_hien_tai_khong_dung_cache(mau):
    pb = mau.chay()["ket_qua"]
    mau.cau_hinh["ky_tu_moi_tai_lieu"] = 1
    mau.dat_cau_hinh()
    kiem_loi(so(mau, pb), "DC_QUA_GIOI_HAN")


def test_tran_snapshot_metadata_hai_muoi_mib_tra_dung_ma(mau):
    pb = mau.chay()["ket_qua"]
    pb["ho_so_doi_chieu"]["ho_so"]["kich_thuoc"] = 20 * hs.MIB + 1
    kiem_loi(so(mau, pb), "DC_QUA_GIOI_HAN")


def test_thoi_han_tu_kiem_bao_loi_gioi_han(mau, monkeypatch):
    pb = mau.chay()["ket_qua"]
    times = iter((0, 301))
    monkeypatch.setattr(sc.time, "perf_counter", lambda: next(times, 301))
    kiem_loi(so(mau, pb), "DC_QUA_GIOI_HAN")


def test_huy_giua_can_khong_nop_ho_so(mau, monkeypatch):
    dat_cap(mau, "DEMO thuê", "DEMO thuế")
    pb = mau.chay()["ket_qua"]
    def huy(*args, **kw):
        raise ViecDaHuy()
    monkeypatch.setattr(sc, "can_chinh", huy)
    r = so(mau, pb)
    assert r["trang_thai"] == "HUY" and r["ket_qua"] is None
    assert any(b.gia_tri["trang_thai"] == "can_thu_lai" for b in mau.cac_luot())


def test_huy_duoc_kiem_trong_cum_lap_dai():
    calls = 0
    def huy():
        nonlocal calls
        calls += 1
        if calls == 5:
            raise ViecDaHuy()
    with pytest.raises(ViecDaHuy):
        sc._so_lat("a" * 500000, "a" * 500000, 0, 500000, 0, 500000, lambda *a: None, huy, [])
    assert calls == 5


def test_tai_dung_phat_hien_hong_script(mau):
    s = snapshot_so(mau, so(mau))
    s["edit_script"][0]["word"]["nguyen_van"] += " DEMO giả"
    with pytest.raises(LoiNghiepVu, match="Chưa căn được"):
        sc.kiem_tai_dung(s["edit_script"], s["chuan_hoa"])


@pytest.mark.parametrize("a,b", [("\u0344", "\u0308"), ("\u0344", "\u0301"), ("\u1100\u1161\u11a8", "\u1100\u1161"),
                                     ("a\u0323\u0301", "a\u0323")])
def test_nfc_co_gian_khong_tach_mat_ky_tu_nguon(mau, a, b):
    dat_cap(mau, "DEMO " + a + " cuối", "DEMO " + b + " cuối")
    s = snapshot_so(mau, so(mau))
    assert s["diem_lech"]
    assert any(a in d["word"]["nguyen_van"] for d in s["diem_lech"] if d["word"])


def test_khoan_thieu_trong_dieu_bi_dao_van_duoc_kiem(mau):
    dat_cap(mau, "Điều 1. DEMO\n1. A DEMO\n2. B DEMO\nĐiều 2. DEMO\n1. C DEMO",
            "Điều 2. DEMO\n1. C DEMO\nĐiều 1. DEMO\n1. A DEMO")
    s = snapshot_so(mau, so(mau))
    assert {"dao_dieu", "thieu_khoan"} <= {d["can_cu"]["phuong_phap"] for d in s["diem_lech"]}


def test_nhan_dieu_nfd_va_khoan_co_ten_duoc_can(mau):
    import unicodedata
    dat_cap(mau, unicodedata.normalize("NFD", "Điều 1. DEMO\nKhoản 1. DEMO A\nKhoản 2. DEMO B"),
            "Điều 1. DEMO\nKhoản 1. DEMO A")
    s = snapshot_so(mau, so(mau))
    assert any(d["can_cu"]["phuong_phap"] == "thieu_khoan" for d in s["diem_lech"])


def test_tien_dau_dong_khong_tu_bien_thanh_khoan(mau):
    dat_cap(mau, "DEMO\n1.000.000 VND", "DEMO\n1.100.000 VND")
    s = snapshot_so(mau, so(mau))
    assert s["diem_lech"] and not any(d["nhom"] == "cau_truc" for d in s["diem_lech"])


@pytest.mark.parametrize("phep", ["chen", "xoa"])
def test_bang_hoac_dong_them_xoa_giu_o_cuoi(mau, phep):
    body = '<w:tbl><w:tr>' + tc("DEMO một") + tc() + '</w:tr><w:tr>' + tc("DEMO hai") + tc() + '</w:tr></w:tbl>'
    w, _ = dat_cap(mau, "", body=p("DEMO đầu") + body)
    dat_ocr_bang(mau, w)
    if phep == "chen":
        # Bản nhận dạng bổ sung cả một bảng ở cuối, có offset thật từ bộ đọc.
        raw = tao_goi(p("DEMO đầu") + body + table_demo())
    else:
        raw = tao_goi(p("DEMO đầu"))
    other = docx.doc_bytes(raw, lambda: None, lambda *a: None, phien_ban_engine="e_doi_chieu 0.4.0")
    v = mau.vb()
    v["van_ban_tai_lieu"]["van_ban"] = other["van_ban_tai_lieu"]["van_ban"]
    v["van_ban_tai_lieu"]["trang"][0]["khoi"] = deepcopy(other["van_ban_tai_lieu"]["khoi_docx"])
    for k in v["van_ban_tai_lieu"]["trang"][0]["khoi"]:
        k["hop"] = [0, 0, 2, 2]
    mau.dat_vb(v)
    s = snapshot_so(mau, so(mau))
    assert any(d["phep"] == phep for d in s["diem_lech"])
    assert any(d["can_cu"]["phuong_phap"] == ("thua_bang" if phep == "chen" else "thieu_bang") for d in s["diem_lech"])


@pytest.mark.parametrize("so_diem", [10000, 10001])
def test_bien_that_muoi_nghin_diem_khong_cat(mau, so_diem):
    dat_cap(mau, "DEMO " + "a0 b " * so_diem, "DEMO " + "c0 b " * so_diem)
    r = mau.chay()
    assert r["trang_thai"] == "XONG", r
    s = mau.snapshot(r)
    if so_diem == 10001:
        with pytest.raises(LoiNghiepVu) as exc:
            sc.so_hai_ban(s, lambda: None, 10000)
        assert exc.value.ma == "DC_QUA_GIOI_HAN"
    else:
        script, points, _ = sc.so_hai_ban(s, lambda: None, 10000)
        assert len(points) == 10000
        sc.kiem_tai_dung(script, s["chuan_hoa"])


def test_snapshot_ra_vuot_tran_khong_tai_ban_cat(mau):
    dat_cap(mau, "DEMO " + "a0 b " * 1200, "DEMO " + "c0 b " * 1200)
    mau.cau_hinh["ho_so_mib"] = 1
    mau.dat_cau_hinh()
    pb = mau.chay()["ket_qua"]
    count = mau.core.so_tai
    kiem_loi(so(mau, pb), "DC_QUA_GIOI_HAN")
    assert mau.core.so_tai == count


@pytest.mark.parametrize("so_lan", [1, 3])
def test_cas_so_xung_dot_khong_tai_lai_tep(mau, monkeypatch, so_lan):
    pb = mau.chay()["ket_qua"]
    original = mau.ngan._thuc_hien
    dem = 0
    def conflict(du_lieu, chi_muc, phien_ban, lenh):
        nonlocal dem
        if lenh[0] == "sua" and lenh[3].get("trang_thai") == "da_so" and dem < so_lan:
            dem += 1
            raise ng.NganXungDot()
        return original(du_lieu, chi_muc, phien_ban, lenh)
    monkeypatch.setattr(mau.ngan, "_thuc_hien", conflict)
    count = mau.core.so_tai
    r = so(mau, pb)
    if so_lan == 1:
        snapshot_so(mau, r)
    else:
        kiem_loi(r, "NGAN_XUNG_DOT")
        assert any(b.gia_tri["trang_thai"] == "can_thu_lai" for b in mau.cac_luot())
    assert mau.core.so_tai == count + (2 if so_lan == 1 else 1)


def test_cas_chu_cu_khong_chot_cleanup_de_chu_moi(mau, monkeypatch):
    pb = mau.chay()["ket_qua"]
    original = mau.ngan._thuc_hien
    chen = False
    def conflict(du_lieu, chi_muc, phien_ban, lenh):
        nonlocal chen
        if lenh[0] == "sua" and lenh[3].get("trang_thai") == "da_so" and not chen:
            chen = True
            # Thay chủ trước CAS chốt của worker cũ; thực hiện bằng API ngăn.
            with mau.ngan.lo() as lo:
                lo.sua("luot_doi_chieu", lenh[2], {"chu_so_huu": "DEMO-chu-moi"}, row_version=lenh[4])
            raise ng.NganXungDot()
        return original(du_lieu, chi_muc, phien_ban, lenh)
    monkeypatch.setattr(mau.ngan, "_thuc_hien", conflict)
    kiem_loi(so(mau, pb), "NGAN_XUNG_DOT")
    rows = [b.gia_tri for b in mau.cac_luot() if b.gia_tri["trang_thai"] == "dang_so"]
    assert len(rows) == 1 and rows[0]["chu_so_huu"] == "DEMO-chu-moi"


def test_hai_viec_so_dong_thoi_mot_luot_va_co_the_thu_lai(mau, monkeypatch):
    pb = mau.chay()["ket_qua"]
    ids = [giao_so(mau, pb) for _ in range(2)]
    original = sc.so_hai_ban
    bat_dau, tiep = threading.Event(), threading.Event()
    def cham(*a, **kw):
        bat_dau.set()
        assert tiep.wait(3)
        return original(*a, **kw)
    monkeypatch.setattr(sc, "so_hai_ban", cham)
    with ThreadPoolExecutor(max_workers=2) as pool:
        dau = pool.submit(mau.core.chay, chay.app)
        assert bat_dau.wait(3)
        sau = pool.submit(mau.core.chay, chay.app)
        sau.result(timeout=3)
        tiep.set()
        dau.result(timeout=3)
    rs = [mau.core.xem(v) for v in ids]
    assert sorted(r["trang_thai"] for r in rs) == ["LOI", "XONG"]
    kiem_loi(next(r for r in rs if r["trang_thai"] == "LOI"), "DC_DANG_XU_LY")
    assert so(mau, pb)["ket_qua"] == next(r for r in rs if r["trang_thai"] == "XONG")["ket_qua"]
    assert len([b for b in mau.cac_luot() if b.gia_tri["trang_thai"] == "da_so"]) == 2  # DC-5 và DC-7 không tạo trùng từng bước.


def test_cache_mat_tep_so_duoc_dung_lai(mau):
    pb = mau.chay()["ket_qua"]
    r = so(mau, pb)
    mau.core.cam.add(r["ket_qua"]["ho_so_doi_chieu"]["ho_so"]["tep_id"])
    new = so(mau, pb)
    snapshot_so(mau, new)
    assert new["ket_qua"]["ho_so_doi_chieu"]["ho_so"]["tep_id"] != r["ket_qua"]["ho_so_doi_chieu"]["ho_so"]["tep_id"]
    assert len([b for b in mau.cac_luot() if b.gia_tri["trang_thai"] == "da_so"]) == 2


def test_cache_sai_bam_khong_tu_bo_qua(mau):
    pb = mau.chay()["ket_qua"]
    so(mau, pb)
    ban = next(b for b in mau.cac_luot() if b.gia_tri["trang_thai"] == "da_so")
    value = ban.gia_tri
    value["phong_bi"]["ho_so_doi_chieu"]["bam_ho_so"] = "sha256:" + "0" * 64
    with mau.ngan.lo() as lo:
        lo.sua("luot_doi_chieu", {"phap_nhan_id": PN, "ma_luot": value["ma_luot"]}, value, row_version=ban.row_version)
    kiem_loi(so(mau, pb), "DC_SAI_NGUON")


@pytest.mark.parametrize("moc", [5, 25, 85, 100])
def test_huy_o_moc_tien_do_khong_nop_ket_qua(mau, monkeypatch, moc):
    pb = mau.chay()["ket_qua"]
    vid = giao_so(mau, pb)
    original = mau.core._tien_do
    def huy(ma, id_viec, pt, cau):
        if vid == id_viec and pt == moc:
            mau.core.huy(vid)
        return original(ma, id_viec, pt, cau)
    monkeypatch.setattr(mau.core, "_tien_do", huy)
    mau.core.chay(chay.app)
    r = mau.core.xem(vid)
    assert r["trang_thai"] == "HUY" and r["ket_qua"] is None
    snapshot_so(mau, so(mau, pb))


def test_mat_xac_nhan_tai_tep_ket_qua_khong_trung(mau):
    pb = mau.chay()["ket_qua"]
    for tac in ("tep", "ket_qua", "ket_thuc"):
        mau.core.gay_mat_xac_nhan(tac)
    snapshot_so(mau, so(mau, pb))
    assert mau.core.so_tai == 3  # Hai snapshot bất biến DC-5/DC-7, một kết quả SDK.
    assert len([b for b in mau.cac_luot() if b.gia_tri["trang_thai"] == "da_so"]) == 2


def test_loi_la_khong_lo_noi_dung_ngoai_le(mau, monkeypatch, capsys):
    pb = mau.chay()["ket_qua"]
    def loi_bi_mat(*a, **kw):
        raise RuntimeError("DEMO bí mật không được đưa vào lỗi hoặc log")
    monkeypatch.setattr(sc, "so_hai_ban", loi_bi_mat)
    r = so(mau, pb)
    kiem_loi(r, "DC_LOI_XU_LY")
    assert "bí mật" not in str(r) and "bí mật" not in capsys.readouterr().err


def test_tai_tep_chua_ro_khong_bao_thanh_cong(mau, monkeypatch):
    pb = mau.chay()["ket_qua"]
    def chua_ro(*a, **kw):
        raise ChuaRo("DEMO-tai-ho-so")
    monkeypatch.setattr(mau.core, "_tai_tep_ra", chua_ro)
    r = so(mau, pb)
    assert r["trang_thai"] == "CHUA_RO" and r["ket_qua"] is None and r["ma_tuong_quan"] == "DEMO-tai-ho-so"


def test_tien_do_khong_kem_nguyen_van(mau):
    dat_cap(mau, "DEMO thuê", "DEMO thuế")
    r = so(mau)
    assert r["trang_thai"] == "XONG", r
    assert all("DEMO" not in cau and "thuê" not in cau and "thuế" not in cau for _, cau in r["tien_do"])


def test_so_khong_truy_cap_dia_mang_engine_khac(mau, monkeypatch):
    import builtins
    from pathlib import Path
    import subprocess
    import urllib.request
    pb = mau.chay()["ket_qua"]
    def cam(*a, **kw):
        pytest.fail("Lượt so chỉ được dùng SDK/Core và RAM")
    with monkeypatch.context() as mp:
        mp.setattr(builtins, "open", cam)
        mp.setattr(Path, "open", cam)
        mp.setattr(subprocess, "Popen", cam)
        mp.setattr(urllib.request, "urlopen", cam)
        r = so(mau, pb)
    snapshot_so(mau, r)


def test_hieu_nang_van_ban_lap_gan_tran_va_nhieu_bang(mau):
    timings = []
    for body in (p("DEMO lặp. " * 45000), "".join('<w:tbl><w:tr>' + tc(f"DEMO bảng {i}") + tc() + tc() + '</w:tr></w:tbl>' for i in range(500))):
        w, _ = dat_cap(mau, "", body=body)
        if "<w:tbl>" in body:
            dat_ocr_bang(mau, w)
        r = mau.chay()
        assert r["trang_thai"] == "XONG", r
        s = mau.snapshot(r)
        start = time.perf_counter()
        script, points, _ = sc.so_hai_ban(s, lambda: None, 10000)
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        sc.kiem_tai_dung(script, s["chuan_hoa"])
        assert not points and elapsed < 5, (len(s["chuan_hoa"]["word"]["van_ban"]), elapsed)
    print("DC-4 DEMO hiệu năng: văn bản lặp 450.000 ký tự %.4fs; 500 bảng %.4fs" % tuple(timings))


def test_tai_dung_nhieu_cap_ngau_nhien_co_lap_unicode(mau):
    rng = random.Random(20261115)
    for _ in range(60):
        a = "DEMO " + "".join(rng.choice("ab thuêế😀 \n") for _ in range(45))
        b = "DEMO " + "".join(rng.choice("ab thuêế😀 \n") for _ in range(45))
        dat_cap(mau, a, b)
        snapshot_so(mau, so(mau))
