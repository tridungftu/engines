"""DC-9: đã kiểm bằng Core giả (CoreGia), chỉ DEMO, 0 Cloud.

ghim_demo mô phỏng đầu ra upstream đã đo/duyệt qua ngăn tin cậy, chỉ để
kiểm bảng quyết định. Các phép đo này KHÔNG là nghiệm thu detector/OCR thật.
Đường DC-5…8 thật được kiểm riêng, luôn giữ trạng thái thiếu kiểm hiện hành.
"""
from copy import deepcopy
from collections import Counter
import importlib
import json
from pathlib import Path
import re

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy, ChuaRo, LoiDuongTruyen

from test_dc3 import Mau, hs, chay, kiem_loi
from test_dc6 import (cap_da_so, dat_bo, bo_demo, dat_tu_dien, chay_buoc, giao,
                      DieuPhoiDEMO, chuan_bi, hau_kiem)
from test_dc8 import tao_mau, quet
from test_dc4 import so
from ngan_demo import trong_ngan

th = importlib.import_module("e_doi_chieu.tong_hop")
bc = importlib.import_module("e_doi_chieu.bao_cao")
qt = importlib.import_module("e_doi_chieu.quy_tac")


def mau_day_du(text="Công ty DEMO Ánh Dương: 1.000.000 VND, ngày 2026-10-30."):
    m = Mau()
    dat_bo(m, bo_demo())
    dat_tu_dien(m)
    pb = cap_da_so(m, text, text)
    s = m.snapshot({"ket_qua": pb})
    # Đáp án của upstream giả trong bảng quyết định: không có điểm lệch.
    s["diem_lech"] = []
    s["kiem_tra"] = {k: "dat" for k in hs._KIEM}
    s["kiem_trang"]["trang_thai"] = "dat"
    for row in s["kiem_quy_tac"].values():
        if isinstance(row, dict):
            row["da_kiem_du"] = True
    s["vung_sua_tay"] = []
    s["quet_anh"] = {"du_dieu_kien_ket_luan_sach": True, "so_do_chat_luong_ho_so": {"DEMO_gia": True},
        "trang": [{"so_trang": 1, "da_quet_toan_trang": True}]}
    s["trang_ocr_kem"] = []
    s["lech_dau"]["trang"] = [{"so": 1, "trang_thai": "khong_vuot_nguong"}]
    s["canh_bao"] = ["DEMO: bằng chứng đo và duyệt giả chỉ kiểm bảng quyết định DC-9."]
    return m, s


def diem_demo(s, muc, no=1):
    def v(ben):
        text = s["van_ban"][ben]["van_ban_tai_lieu"]["van_ban"]
        return {"nguyen_van": text, "bat_dau": 0, "ket_thuc": len(text),
                "vi_tri": {"so_trang": None, "hop": None, "so_doan": 1} if ben == "word" else
                          {"so_trang": 1, "hop": [0, 0, 2, 2], "don_vi": "px"}}
    return {"ma_diem": f"DEMO-{no}", "muc": muc, "muc_san": muc, "cho_phan_loai": False,
            "quy_tac_trung": [], "can_cu_quy_tac": [], "vung_bao_ve": [],
            "word": v("word"), "ban_ky": v("ban_ky"), "nhom": "DEMO_bang_quyet_dinh",
            "ly_do_ai": "DEMO: lý do có dấu, không phải kết quả model thật.", "can_cu": {"nguon": "DEMO"}}


def ghim_demo(m, s):
    """Mô phỏng upstream tin cậy, không mở cổng giả trong runtime."""
    s["nhat_ky_quy_tac"] = [qt._dau_diem(d) for d in s["diem_lech"]]
    s["bam_nhat_ky_quy_tac"] = hs.bam(hs.json_bytes(s["nhat_ky_quy_tac"]))
    dem = Counter(d["muc"] for d in s["diem_lech"])
    s["tom_tat"] = {"so_diem": len(s["diem_lech"]), **{"so_"+k: dem[k] for k in th.CAC_MUC},
                   "so_vung_sua_tay": len(s["vung_sua_tay"]) if s["vung_sua_tay"] is not None else None,
                   "so_trang_ocr_kem": len(s["trang_ocr_kem"]) if s["trang_ocr_kem"] is not None and
                       all(p["trang_thai"] != "chua_kiem" for p in s["lech_dau"]["trang"]) else None}
    raw = hs.json_bytes(s)
    ref = m.luu("ho-so-dc9-DEMO.json", raw, "application/json")
    pb = hs._phong_bi(s, ref["tep"], raw)
    def ghi(ngan):
        with ngan.lo() as lo:
            lo.them("luot_doi_chieu", {"ma_luot": "DEMO-DC9-"+hs.bam(raw)[7:23],
                "bam_cap": hs.bam(raw), "bam_bo": s["bo_quy_tac"]["bam"],
                "phien_ban_engine": s["phien_ban_engine"], "trang_thai": s["giai_doan"],
                "phong_bi": hs.dong_phong_bi(pb)})
    trong_ngan(m, ghi)
    return pb


def xuat(m, pb):
    return chay_buoc(m, "xuat_ket_qua", pb)


def doc_kq(m, r):
    assert r["trang_thai"] == "XONG", r
    t = r["ket_qua"]["truong"]
    raw = m.core.doc_tep(t["tep_json"]["tep_id"])
    pdf = m.core.doc_tep(t["tep_pdf"]["tep_id"])
    s = json.loads(raw)
    assert hs.json_bytes(s) == raw
    assert hs.bam(pdf) == s["bao_cao_pdf"]["bam"]
    meta = bytes.fromhex(re.search(rb"/Subject <([0-9a-f]+)>", pdf)[1].decode()).decode("utf-16")
    dem_pdf = json.loads(meta)
    for key in ("ket_luan", "da_kiem_du", "de_nghi_chan"):
        assert t[key] == s[key] == dem_pdf[key]
    for key in th.TRUONG_DEM:
        assert t[key] == s["tom_tat"][key] == dem_pdf[key]
    assert pdf.startswith(b"%PDF-1.4") and pdf.endswith(b"%%EOF\n")
    # Xref ghi đúng byte offset từng object, kể cả tiếng Việt metadata.
    xref = int(re.search(rb"startxref\n([0-9]+)", pdf)[1])
    assert pdf[xref:xref+4] == b"xref"
    return t, s, pdf


@pytest.mark.parametrize("muc,ket_luan,chan", [
    (None, "khop", False), ("hinh_thuc", "khop_co_thay_doi_hinh_thuc", False),
    ("nhieu_ocr", "khop_co_thay_doi_hinh_thuc", False), ("can_xem", "can_xem", False),
    ("nghiem_trong", "lech_nghiem_trong", True)])
def test_bang_ket_luan_core_gia(muc, ket_luan, chan):
    m, s = mau_day_du()
    if muc:
        s["diem_lech"] = [diem_demo(s, muc)]
    t, out, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert t["ket_luan"] == ket_luan and t["de_nghi_chan"] is chan and t["da_kiem_du"]
    assert out["tong_hop"]["phan_chua_kiem"] == []
    assert len(out["diem_lech"]) == (1 if muc else 0)


@pytest.mark.parametrize("kiem", list(hs._KIEM))
def test_thieu_tung_kiem_khong_thanh_khop(kiem):
    m, s = mau_day_du()
    s["kiem_tra"][kiem] = "chua_kiem"
    # Có Cần xem đã phân loại: không được tự bỏ qua AI.
    s["diem_lech"] = [diem_demo(s, "can_xem")]
    t, out, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert t["ket_luan"] == "chua_doi_chieu_duoc" and not t["da_kiem_du"] and t["de_nghi_chan"]
    assert kiem in out["tong_hop"]["phan_chua_kiem"]


@pytest.mark.parametrize("loai", ["ocr_loi", "thieu_trang", "khong_can_duoc", "detector", "nguong_ocr"])
def test_loi_nguon_va_do_thieu_khong_khop(loai):
    m, s = mau_day_du()
    if loai == "ocr_loi":
        s["kiem_dau_vao"]["ocr_day_du"] = False
        s["kiem_tra"]["doc_hai_ban"] = "khong_dat"
    elif loai == "thieu_trang":
        s["anh_trang"] = []
    elif loai == "khong_can_duoc":
        s["kiem_tra"]["so_van_ban"] = "khong_dat"
    elif loai == "detector":
        s["quet_anh"] = None
        s["vung_sua_tay"] = None
    else:
        s["lech_dau"]["trang"][0]["trang_thai"] = "chua_kiem"
    t, _, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert not t["da_kiem_du"] and t["de_nghi_chan"] and t["ket_luan"] == "chua_doi_chieu_duoc"
    if loai == "nguong_ocr":
        assert t["so_trang_ocr_kem"] is None
    if loai == "detector":
        assert t["so_vung_sua_tay"] is None


def test_thieu_kiem_van_giu_nghiem_trong():
    m, s = mau_day_du()
    s["diem_lech"] = [diem_demo(s, "nghiem_trong")]
    s["kiem_tra"]["sua_tay"] = "chua_kiem"
    t, out, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert t["ket_luan"] == "chua_doi_chieu_duoc" and t["so_nghiem_trong"] == 1
    assert out["diem_lech"] == s["diem_lech"] and t["de_nghi_chan"]


def test_trang_ocr_kem_can_xem_khong_tu_chan():
    m, s = mau_day_du()
    s["trang_ocr_kem"] = [{"so": 1, "trang_thai": "ocr_kem"}]
    s["lech_dau"]["trang"] = deepcopy(s["trang_ocr_kem"])
    t, _, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert t["ket_luan"] == "can_xem" and not t["de_nghi_chan"] and t["so_trang_ocr_kem"] == 1


def test_vung_sua_tay_chan_nhu_nghiem_trong_khi_kiem_du():
    m, s = mau_day_du()
    ref = s["anh_trang"][0]
    s["vung_sua_tay"] = [{"ma": "DEMO-V1", "muc": "nghiem_trong", "muc_san": "nghiem_trong",
        "so_trang": 1, "hop": [0, 0, 2, 2], "chu_tay": None,
        "anh_cat": ref["tep"], "bam_anh_cat": ref["bam"]}]
    t, _, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert t["ket_luan"] == "lech_nghiem_trong" and t["de_nghi_chan"] and t["da_kiem_du"]
    assert t["so_nghiem_trong"] == 0 and t["so_vung_sua_tay"] == 1


def test_sai_so_dem_snapshot_tu_choi():
    m, s = mau_day_du()
    ghim_demo(m, s)
    s["tom_tat"]["so_can_xem"] = 99
    with pytest.raises(LoiNghiepVu) as exc:
        th._kiem_diem(s)
    assert exc.value.ma == "DC_SAI_NGUON"


def test_hinh_thuc_va_nhieu_deu_giu_trong_pdf(monkeypatch):
    m, s = mau_day_du()
    s["diem_lech"] = [diem_demo(s, "hinh_thuc", 1), diem_demo(s, "nhieu_ocr", 2)]
    lines = []
    goc = bc._PDF._ve_dong
    def ve(p, text, color):
        lines.append(text)
        return goc(p, text, color)
    monkeypatch.setattr(bc._PDF, "_ve_dong", ve)
    t, out, _ = doc_kq(m, xuat(m, ghim_demo(m, s)))
    assert t["ket_luan"] == "khop_co_thay_doi_hinh_thuc"
    text = "\n".join(lines)
    assert "PHỤ LỤC - TOÀN BỘ NHIỄU OCR" in text and "Điểm DEMO-1" in text and "Điểm DEMO-2" in text
    assert "Hình thức: 1" in text and "Nhiễu OCR: 1" in text
    assert out["diem_lech"] == s["diem_lech"]
    assert "Chưa có dữ liệu xác nhận tin cậy từ Core." in text


def test_dang_cho_ai_va_diem_chua_phan_loai_tu_choi():
    m, s = mau_day_du()
    s["diem_lech"] = [diem_demo(s, "can_xem")]
    s["diem_lech"][0]["cho_phan_loai"] = True
    pb = ghim_demo(m, s)
    kiem_loi(xuat(m, pb), "DC_HO_SO_CHUA_DU")
    pb["ho_so_doi_chieu"]["giai_doan"] = "cho_ai"
    kiem_loi(xuat(m, pb), "DC_HO_SO_CHUA_DU")


@pytest.mark.parametrize("sai", ["bam", "schema", "tu_bam_lai", "mat_quyen", "khac_phap_nhan"])
def test_sai_nguon_tu_choi(sai):
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    if sai == "bam":
        pb["ho_so_doi_chieu"]["bam_ho_so"] = "sha256:"+"0"*64
    elif sai == "schema":
        pb["ho_so_doi_chieu"]["truong_la"] = "DEMO"
    elif sai == "tu_bam_lai":
        s["canh_bao"].append("DEMO-sua-khong-qua-ngan")
        raw = hs.json_bytes(s)
        pb = hs._phong_bi(s, m.luu("khong-ghim.json", raw, "application/json")["tep"], raw)
    elif sai == "mat_quyen":
        m.core.cam.add(s["nguon"]["word"]["tep"]["tep_id"])
    if sai == "khac_phap_nhan":
        r = chay_buoc(m, "xuat_ket_qua", pb, pn="DEMO-P2")
    else:
        r = xuat(m, pb)
    kiem_loi(r, "DC_SAI_NGUON")


def test_chuoi_that_dc5_dc8_bao_do_giu_vung(monkeypatch):
    m = tao_mau("gach")
    dat_bo(m, bo_demo())
    dat_tu_dien(m)
    r = so(m)
    assert r["trang_thai"] == "XONG", r
    r = quet(m, monkeypatch, r["ket_qua"])
    assert r["trang_thai"] == "XONG", r
    provider = DieuPhoiDEMO()
    s = m.snapshot(r)
    pb = r["ket_qua"]
    if any(d["cho_phan_loai"] for d in s["diem_lech"]):
        r = hau_kiem(m, provider.hoi(m, chuan_bi(m, pb)))
        assert r["trang_thai"] == "XONG", r
        pb = r["ket_qua"]
    t, out, _ = doc_kq(m, xuat(m, pb))
    assert t["ket_luan"] == "chua_doi_chieu_duoc" and not t["da_kiem_du"]
    assert t["de_nghi_chan"] and t["so_vung_sua_tay"] > 0
    assert out["vung_sua_tay"] and provider.cloud == 0


@pytest.mark.parametrize("loai", ["vo_nghia", "doi_nghia_du_nguon", "doi_nghia_thieu_manifest"])
def test_nhieu_thuc_te_dc7_phai_kiem_lai_bang_validator(loai):
    from test_dc7 import cap_so, phan_loai
    from demo_lech_dau import CoreOCRVungDEMO, manifest_ocr
    m = Mau(CoreOCRVungDEMO())
    dat_tu_dien(m)
    m.provider = DieuPhoiDEMO()
    w, o = ("DEMO hợp.", "DEMO hơp.") if loai == "vo_nghia" else ("DEMO thuê.", "DEMO thuế.")
    r, s = cap_so(m, w, o)
    manifest = manifest_ocr(m, s) if loai != "vo_nghia" else None
    r = phan_loai(m, r, s, manifest=manifest)
    assert r["trang_thai"] == "XONG", r
    assert m.snapshot(r)["tom_tat"]["so_nhieu_ocr"] > 0
    vid = giao(m, "xuat_ket_qua", r["ket_qua"])
    if loai == "doi_nghia_du_nguon":
        m.core.ocr_vung_viec[vid] = manifest
    m.core.chay(chay.app)
    out = m.core.xem(vid)
    if loai == "doi_nghia_thieu_manifest":
        kiem_loi(out, "DC_SAI_NGUON")
    else:
        t, snap, _ = doc_kq(m, out)
        assert t["so_nhieu_ocr"] > 0 and t["ket_luan"] == "chua_doi_chieu_duoc"
        assert all(d["muc"] == "nhieu_ocr" for d in snap["diem_lech"])
    assert m.provider.cloud == 0


def test_font_thieu_hoac_sai_khong_co_json_thanh_cong(monkeypatch, tmp_path):
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    before = m.core.so_tai
    monkeypatch.setattr(bc, "FONT", tmp_path/"khong-co.ttf")
    kiem_loi(xuat(m, pb), "DC_THIEU_TAI_NGUYEN")
    assert m.core.so_tai == before
    p = tmp_path/"font-hong.ttf"
    p.write_bytes(b"DEMO-font-hong")
    monkeypatch.setattr(bc, "FONT", p)
    kiem_loi(xuat(m, pb), "DC_THIEU_TAI_NGUYEN")


@pytest.mark.parametrize("mime", ["application/pdf", "application/json"])
def test_tai_tep_loi_khong_xong_va_khong_nhan_doi_luot(monkeypatch, mime):
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    original = m.core._tai_tep_ra
    def tai(ma, vid, ten, raw, loai, khoa):
        if loai == mime:
            raise LoiDuongTruyen("DEMO", "DEMO", http_status=400)
        return original(ma, vid, ten, raw, loai, khoa)
    monkeypatch.setattr(m.core, "_tai_tep_ra", tai)
    kiem_loi(xuat(m, pb), "DC_KHONG_XUAT_DUOC")
    rows = [r for r in m.cac_luot() if r.gia_tri["trang_thai"] == "can_thu_lai"]
    assert len(rows) == 1
    no = rows[0].id
    monkeypatch.setattr(m.core, "_tai_tep_ra", original)
    doc_kq(m, xuat(m, pb))
    rows = [r for r in m.cac_luot() if r.gia_tri["trang_thai"] == "da_xuat"]
    assert len(rows) == 1 and rows[0].id == no


@pytest.mark.parametrize("mat", ["tep", "ngan", "ket_qua", "ket_thuc"])
def test_mat_xac_nhan_va_goi_lai_khong_nhan_doi(mat):
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    before = m.core.so_tai
    m.core.gay_mat_xac_nhan(mat)
    r = xuat(m, pb)
    doc_kq(m, r)
    assert m.core.so_tai == before+2
    r2 = xuat(m, pb)
    assert r2["ket_qua"] == r["ket_qua"] and m.core.so_tai == before+2
    assert len([r for r in m.cac_luot() if r.gia_tri["trang_thai"] == "da_xuat"]) == 1


def test_huy_giua_tai_json_khong_thanh_cong(monkeypatch):
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    original = m.core._tai_tep_ra
    def tai(ma, vid, ten, raw, mime, khoa):
        if mime == "application/json":
            m.core.huy(vid)
            raise ViecDaHuy()
        return original(ma, vid, ten, raw, mime, khoa)
    monkeypatch.setattr(m.core, "_tai_tep_ra", tai)
    r = xuat(m, pb)
    assert r["trang_thai"] == "HUY" and r["ket_qua"] is None
    assert not [r for r in m.cac_luot() if r.gia_tri["trang_thai"] == "da_xuat"]


def test_tai_da_nhan_nhung_chua_ro_khong_xong(monkeypatch):
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    def tai(*a, **kw):
        raise ChuaRo("DEMO-tai-chua-ro")
    monkeypatch.setattr(m.core, "_tai_tep_ra", tai)
    r = xuat(m, pb)
    assert r["trang_thai"] == "CHUA_RO" and r["ket_qua"] is None
    assert len([r for r in m.cac_luot() if r.gia_tri["trang_thai"] == "can_thu_lai"]) == 1


def test_tai_lai_khi_pdf_cu_mat_quyen_khong_tra_thanh_cong():
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    t, _, _ = doc_kq(m, xuat(m, pb))
    before = m.core.so_tai
    m.core.cam.add(t["tep_pdf"]["tep_id"])
    kiem_loi(xuat(m, pb), "DC_KHONG_XUAT_DUOC")
    assert m.core.so_tai == before


def test_pdf_nhieu_diem_dai_khong_mat_dong_va_dau(monkeypatch):
    text = ("Đối chiếu bản ký DEMO Ánh Dương: 1.000.000 VND ngày 2026-10-30; thuế, thuê, lãi, lại. " * 18).strip()
    m, s = mau_day_du(text)
    s["diem_lech"] = [diem_demo(s, "hinh_thuc", i) for i in range(1, 13)]
    lines = []
    goc = bc._PDF._ve_dong
    def ve(p, text, color):
        assert p.draw.textbbox((0, 0), text, font=p.font)[2] <= p.W-2*p.LE
        lines.append(text)
        return goc(p, text, color)
    monkeypatch.setattr(bc._PDF, "_ve_dong", ve)
    _, _, pdf = doc_kq(m, xuat(m, ghim_demo(m, s)))
    count = int(re.search(rb"/Type /Pages /Kids \[.*?\] /Count ([0-9]+)", pdf)[1])
    assert count > 5
    joined = "".join(lines)
    assert "[U+" not in joined
    assert joined.count(text) == 24
    assert all(f"Điểm DEMO-{i}" in joined for i in range(1, 13))


def test_engine_xuat_chi_ram_khong_mang(monkeypatch):
    import socket
    import tempfile
    m, s = mau_day_du()
    pb = ghim_demo(m, s)
    def cam(*a, **kw):
        raise AssertionError("DEMO: không được ghi đĩa hoặc gọi mạng")
    monkeypatch.setattr(Path, "write_bytes", cam)
    monkeypatch.setattr(Path, "write_text", cam)
    monkeypatch.setattr(tempfile, "NamedTemporaryFile", cam)
    monkeypatch.setattr(socket, "create_connection", cam)
    doc_kq(m, xuat(m, pb))
