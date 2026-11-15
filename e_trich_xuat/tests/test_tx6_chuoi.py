"""TX-6: Core điều phối hai chuỗi DEMO; không chứng nhận quyền/TTL/ACK thật."""
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import socket
from zipfile import ZipFile

import pytest
from jsonschema import Draft202012Validator
from kho_tri_thuc_sdk.engine import Engine, ChuaRo
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import tao_app, GOC_GOI
from e_trich_xuat.tham_so import bam_bytes, json_bytes
from mau_tx3 import ai_demo
from test_xuat import doc_excel

GOC = Path(__file__).resolve().parents[2]
E6 = GOC / "e_trich_xuat/tham-chieu/e6"


def engine_gia(ma, nang_luc, nhan, tra):
    phieu = deepcopy(tao_app().phieu)
    phieu.update(ma=ma, nang_luc=[{"ma": nang_luc, "ten": "DEMO giả",
        "nhan": [nhan], "tra": tra, "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 30}}], chay_thu_demo=[])
    return Engine(phieu, thu_muc_goi=GOC_GOI)


def pdf_demo():
    # PDF một trang hợp lệ, nội dung giả. OCR dưới đây chỉ là nhà cung cấp giả.
    stream = b"BT /F1 14 Tf 30 70 Td (DEMO - Du lieu gia lap) Tj ET"
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    out, offsets = b"%PDF-1.4\n", [0]
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 6\n0000000000 65535 f \n" + b"".join(f"{n:010d} 00000 n \n".encode() for n in offsets[1:])
    return out + b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF\n"


def chay(core, app, ma, vao, ts=None):
    v = core.chay_thu(app, ma, vao, ts, cho_gui_lai_giay=0)
    assert v["trang_thai"] == "XONG", v
    return v["ket_qua"]


@pytest.mark.parametrize("nguon", ["docx", "pdf_ocr_gia"])
def test_hai_chuoi_schema_metadata_tien_ngay_tep_snapshot(nguon, monkeypatch):
    # Chặn mạng: CoreGia giao từng bước, không có engine gọi chéo.
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("Không mạng"))
    core, app = CoreGia(), tao_app()
    core.nap_engine(app)
    core.dat_cau_hinh(app.ma, {"ngan_sach_token_vao_toi_da": 100000})
    docx = (E6 / "DEMO-thuong.docx").read_bytes()
    t = core.them_tep("DEMO.docx", docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    tl = chay(core, app, "trich.doc_docx@1", {"loai": "tep", "tep": t})
    if nguon != "docx":
        pdf, ocr = pdf_demo(), engine_gia("e_ocr_demo", "ocr.doc_tai_lieu@1", "tep", "van_ban_tai_lieu")
        t = core.them_tep("DEMO.pdf", pdf, "application/pdf")
        @ocr.nang_luc("ocr.doc_tai_lieu@1")
        def doc_gia(viec):
            assert viec.mo_tep(viec.dau_vao["tep"]["tep_id"]).read() == pdf
            ra = deepcopy(tl)
            ra["van_ban_tai_lieu"].update(nguon_doc="abbyy", so_trang=1,
                bam_dau_vao=bam_bytes(pdf), phien_ban_engine="DEMO-OCR-gia 1",
                trang=[{"so": 1, "rong": 595, "cao": 842, "don_vi": "pt", "khoi": [
                    {"loai": "doan", "van_ban": tl["van_ban_tai_lieu"]["van_ban"], "hop": [10, 10, 585, 832]}]}])
            return ra
        tl = chay(core, ocr, "ocr.doc_tai_lieu@1", {"loai": "tep", "tep": t})
    schema = lambda ten, v: Draft202012Validator(json.loads((GOC_GOI / "contract" / (ten + ".schema.json")).read_text(encoding="utf-8"))).validate(v)
    schema("van_ban_tai_lieu", tl)
    ts = json.loads((E6 / "DEMO-thuong.tham-so.json").read_text(encoding="utf-8"))
    ts["model_uu_tien"] = "DEMO-model-gia"
    req = chay(core, app, "trich.chuan_bi@1", tl, ts)
    schema("yeu_cau_ai", req)
    r = req["yeu_cau_ai"]
    meta = r["chuyen_tiep"]["trich_xuat"]
    ho_so = core.doc_tep(meta["ho_so_hau_kiem"]["tep_id"])
    assert bam_bytes(ho_so) == meta["bam_ho_so_hau_kiem"]
    assert len(ho_so) == meta["ho_so_hau_kiem"]["kich_thuoc"]
    # Đổi bộ/cấu hình sau chuẩn bị: hồ sơ cũ và metadata đầu ra giữ nguyên.
    ts["prompt"] = "DEMO prompt mới"
    ts["bo_tham_so_json"] = "DEMO khác"
    core.dat_cau_hinh(app.ma, {"ngan_sach_token_vao_toi_da": 1024})
    assert json.loads(ho_so)["cau_hinh_da_ghim"]["gia_tri"]["ngan_sach_token_vao_toi_da"] == 100000
    vang = json.loads((E6 / "DEMO-thuong.vang.json").read_text(encoding="utf-8"))
    data = {}
    for ma in r["khuon_tra_loi"]["required"]:
        q, v = vang["can_cu"][ma], vang["gia_tri"][ma]
        i = r["tai_lieu"].index(q)
        data[ma] = {"gia_tri": v, "don_vi": None, "ghi_chu": None,
                    "trich_dan": [{"cau": q, "bat_dau": i, "ket_thuc": i + len(q)}]}
    ai = engine_gia("e_ai_demo", "ai.hoi_theo_yeu_cau@1", "yeu_cau_ai", "tra_loi_ai")
    @ai.nang_luc("ai.hoi_theo_yeu_cau@1")
    def hoi_gia(viec):
        assert viec.dau_vao == req
        return ai_demo(viec.dau_vao, data)
    ans = chay(core, ai, "ai.hoi_theo_yeu_cau@1", req)
    schema("tra_loi_ai", ans)
    b = chay(core, app, "trich.hau_kiem@1", ans)
    schema("bang_trich_xuat", b)
    bang = b["bang_trich_xuat"]
    assert bang["bam_bo_tham_so"] == meta["bam_bo_tham_so"]
    assert bang["nguon"]["bam_dau_vao"] == tl["van_ban_tai_lieu"]["bam_dau_vao"]
    assert [x["ma"] for x in bang["bang"]] == r["khuon_tra_loi"]["required"]
    assert {x["ma"]: x["gia_tri"] for x in bang["bang"]} == vang["gia_tri"]
    assert next(x for x in bang["bang"] if x["ma"] == "TT-02")["gia_tri"] == "1.100.000 VND"
    assert next(x for x in bang["bang"] if x["ma"] == "TC-02")["gia_tri"] == "2026-10-30"
    for row in bang["bang"]:
        for q in row["dan_chung"]:
            assert r["tai_lieu"][q["bat_dau"]:q["ket_thuc"]] == q["cau"]
            assert q["vi_tri"]["so_trang"] == (None if nguon == "docx" else 1)
    ra = chay(core, app, "trich.xuat_ket_qua@1", b)
    assert ra["loai"] == "truong" and ra["truong"]["so_tham_so"] == 37
    for k in ("tep_json", "tep_excel"):
        ref = ra["truong"][k]
        assert len(core.doc_tep(ref["tep_id"])) == ref["kich_thuoc"] > 0
    assert core.doc_tep(ra["truong"]["tep_json"]["tep_id"]) == json_bytes(b)
    excel = doc_excel(core.doc_tep(ra["truong"]["tep_excel"]["tep_id"]))
    assert len(excel) == 38 and any("1.100.000 VND" in row for row in excel)
    assert core.doc_tep(meta["ho_so_hau_kiem"]["tep_id"]) == ho_so


def test_chua_ro_khong_co_ket_qua_khong_gui_lai_mu():
    app, core = engine_gia("e_ai_demo", "ai.hoi_theo_yeu_cau@1", "yeu_cau_ai", "tra_loi_ai"), CoreGia()
    dem = []
    @app.nang_luc("ai.hoi_theo_yeu_cau@1")
    def nhan_chua_tra(viec):
        dem.append(1)
        raise ChuaRo("DEMO-tuong-quan-TX6")
    kq = core.chay_thu(app, "ai.hoi_theo_yeu_cau@1", {"loai": "yeu_cau_ai", "yeu_cau_ai": {}})
    assert dem == [1] and kq["trang_thai"] == "CHUA_RO"
    assert kq["ket_qua"] is None and kq["ma_tuong_quan"] == "DEMO-tuong-quan-TX6"
