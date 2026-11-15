"""Xuất TX-3: round trip JSON/OOXML, giới hạn, hủy, lỗi và ACK."""

from copy import deepcopy
from io import BytesIO
import builtins
import json
from pathlib import Path
import re
import socket
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat import hau_kiem as hk
from e_trich_xuat import xuat
from e_trich_xuat.tham_so import json_bytes
from e_trich_xuat.xlsx_mini import _cell, write_xlsx
from mau_tx3 import (GOC_GOI, PHIEU, VD, ai_demo, app_tx3, bang_demo,
                     chay_demo_tx3, chuan_bi_demo, o_ai, ts_demo)


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def doc_excel(raw, index=1):
    with ZipFile(BytesIO(raw)) as z:
        root = ET.fromstring(z.read(f"xl/worksheets/sheet{index}.xml"))
    out = []
    # OOXML decode một lần để không biến literal _x000D_ thành ký tự CR.
    for r in root.iter(NS + "row"):
        row = []
        for c in r.findall(NS + "c"):
            assert c.find(NS + "f") is None
            t = "".join(x.text or "" for x in c.iter(NS + "t"))
            if c.get("t") != "inlineStr":
                t = c.findtext(NS + "v") or ""
            t = re.sub(r"_x([0-9A-Fa-f]{4})_", lambda m: chr(int(m[1], 16)), t)
            row.append(t)
        out.append(row)
    return out


def xuat_demo(pb=None, core=None, app=None):
    if core is None:
        core, app, goc = bang_demo()
        pb = goc if pb is None else pb
    return core.chay_thu(app, "trich.xuat_ket_qua@1", pb), core


def loi(kq, ma):
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None, kq
    assert kq["loi"] == {"ma": ma, "thong_diep": hk.CAU_LOI[ma], "thu_lai_duoc": False}


def test_xuat_tai_lai_json_excel_du_thu_tu_unicode_va_nguyen_van():
    core, app, pb = bang_demo()
    b = pb["bang_trich_xuat"]
    # Bảng đề xuất có kiểu rõ, không suy kiểu từ Excel.
    b["bang"][0].update(kieu="so_tien", kieu_da_chuyen=True, gia_tri={"so": 10000000000000001, "tien_te": "VND"},
                        nguyen_van="10.000.000.000.000.001 VND")
    b["bang"][1].update(kieu="ngay", kieu_da_chuyen=True, gia_tri="2026-10-30", nguyen_van="30/10/2026 😀 e\u0301")
    b["tom_tat"] = hk.tom_tat(b["bang"])
    truoc = deepcopy(pb)
    kq, _ = xuat_demo(pb, core, app)
    assert kq["trang_thai"] == "XONG", kq
    t = kq["ket_qua"]["truong"]
    assert set(t) == {"tep_json", "tep_excel", "so_tham_so", "so_can_soat", "co_can_cu"}
    raw = core.doc_tep(t["tep_json"]["tep_id"])
    assert raw == json_bytes(pb) and json.loads(raw) == truoc == pb
    assert "😀".encode() in raw and t["tep_json"]["kich_thuoc"] == len(raw)
    xlsx = core.doc_tep(t["tep_excel"]["tep_id"])
    rows = doc_excel(xlsx)
    assert [r[0] for r in rows[1:]] == ["TT-01", "TT-02"]
    assert json.loads(rows[1][3]) == {"so": 10000000000000001, "tien_te": "VND"}
    assert rows[2][3] == "2026-10-30" and rows[2][4] == "30/10/2026 😀 e\u0301"
    assert rows[1][-1] == rows[2][-1] == "true"
    assert doc_excel(xlsx, 2)[1][1] == b["bang"][0]["dan_chung"][0]["cau"]
    assert any(r[0] == "nguon.bam_dau_vao" for r in doc_excel(xlsx, 3))
    assert any(r[0] == "TT-01.gia_tri" for r in doc_excel(xlsx, 4))


@pytest.mark.parametrize("text", ["=1+1", "+SUM(A1)", "-2+3", "@SUM(A1)", "000001", "<&>\r\x01_x000D_😀"])
def test_chuoi_khong_thanh_cong_thuc_hoac_mat_ky_tu(text):
    bo_nho = BytesIO()
    write_xlsx(bo_nho, {"DEMO": {"rows": [["DEMO"], [text]]}})
    assert doc_excel(bo_nho.getvalue())[1][0] == text
    with ZipFile(BytesIO(bo_nho.getvalue())) as z:
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        c = list(root.iter(NS + "c"))[1]
        assert c.get("t") == "inlineStr" and c.find(NS + "f") is None


@pytest.mark.parametrize("s", ["&" * 32767, "😀" * 16383 + "a"], ids=["escape-sat-tran", "utf16-sat-tran"])
def test_o_sat_tran_truoc_escape_va_utf16_giu_day_du(s):
    b = BytesIO()
    write_xlsx(b, {"DEMO": {"rows": [["DEMO"], [s]]}})
    assert doc_excel(b.getvalue())[1][0] == s


@pytest.mark.parametrize("s", ["a" * 32768, "😀" * 16384], ids=["ascii-vuot", "utf16-vuot"])
def test_o_vuot_tran_khong_cat(s):
    with pytest.raises(LoiNghiepVu) as exc:
        _cell("A1", s, 2)
    assert exc.value.ma == "O_EXCEL_QUA_DAI"
    assert exc.value.thong_diep == hk.CAU_LOI["O_EXCEL_QUA_DAI"]


def test_xuat_o_sat_tran_khong_tang_do_dai_do_json_va_vuot_khong_tai_tep():
    core, app, pb = bang_demo()
    r = pb["bang_trich_xuat"]["bang"][0]
    r["nguyen_van"] = "&" * 32767
    r["phan_hoi_ai"]["gia_tri"] = r["nguyen_van"]
    kq, _ = xuat_demo(pb, core, app)
    assert kq["trang_thai"] == "XONG", kq
    assert doc_excel(core.doc_tep(kq["ket_qua"]["truong"]["tep_excel"]["tep_id"]))[1][4] == "&" * 32767
    truoc = core.so_lan_ghi["tep"]
    r["nguyen_van"] += "&"
    kq, _ = xuat_demo(pb, core, app)
    loi(kq, "O_EXCEL_QUA_DAI")
    assert core.so_lan_ghi["tep"] == truoc  # Phải tạo đủ cả hai trước khi tải.


@pytest.mark.parametrize("doi", [
    lambda b: b["tom_tat"].update(so_tham_so=3),
    lambda b: b["tom_tat"].update(so_can_soat=1),
    lambda b: b["tom_tat"].update(co_can_cu=False),
    lambda b: b["tom_tat"].update(so_can_soat=True),
    lambda b: b["bang"].reverse(),
    lambda b: b["bang"].pop(),
    lambda b: b["bang"][1].update(ma="TT-01"),
    lambda b: b["bang"][1].update(ma="TT-99"),
    lambda b: b["bang"][1].update(kieu="so_tien", gia_tri={"so": 1000000}),
    lambda b: b["bang"][1].update(kieu="ngay", gia_tri="30/10/2026"),
    lambda b: b["bang"][1].update(kieu="ngay", gia_tri="2026-02-30"),
    lambda b: b["bang"][1].update(kieu="so", gia_tri=True),
    lambda b: b["bang"][1].update(gia_tri=None),
    lambda b: b["bang"][1]["dan_chung"][0]["vi_tri"].update(so_trang=1),
    lambda b: b["nguon"].update(bam_dau_vao="DEMO"),
    lambda b: b.pop("ma_prompt"),
    lambda b: b.pop("don_vi_offset"),
    lambda b: b.update(don_vi_offset="utf16"),
    lambda b: b["bang"][0].pop("kieu_da_chuyen"),
    lambda b: b["bang"][0].update(kieu_da_chuyen=0),
    lambda b: b["bang"][0].update(kieu="so", gia_tri=100, kieu_da_chuyen=False),
])
def test_bang_sai_tu_choi_truoc_tai(doi):
    core, app, pb = bang_demo()
    doi(pb["bang_trich_xuat"])
    truoc = core.so_lan_ghi["tep"]
    kq, _ = xuat_demo(pb, core, app)
    loi(kq, "KET_QUA_KHONG_HOP_LE")
    assert core.so_lan_ghi["tep"] == truoc


def test_tran_200_dong_va_201_tu_choi():
    core, app, pb = bang_demo()
    b = pb["bang_trich_xuat"]
    mau = b["bang"][0]
    b["bang"] = [dict(deepcopy(mau), ma=f"TT-{i:03}") for i in range(200)]
    b["ma_truong_can_trich"] = [r["ma"] for r in b["bang"]]
    b["tom_tat"] = hk.tom_tat(b["bang"])
    kq, _ = xuat_demo(pb, core, app)
    assert kq["trang_thai"] == "XONG", kq
    assert len(doc_excel(core.doc_tep(kq["ket_qua"]["truong"]["tep_excel"]["tep_id"]))) == 201
    b["bang"].append(dict(deepcopy(mau), ma="TT-201"))
    b["ma_truong_can_trich"].append("TT-201")
    b["tom_tat"] = hk.tom_tat(b["bang"])
    loi(xuat_demo(pb, core, app)[0], "VUOT_GIOI_HAN")


def test_phong_bi_dung_20_mib_va_vuot_mot_byte():
    _, _, pb = bang_demo()
    b = pb["bang_trich_xuat"]
    b["canh_bao"] = [""]
    con = hk.JSON_TOI_DA - len(json_bytes(pb))
    b["canh_bao"] = ["é" * (con // 2) + "a" * (con % 2)]
    assert len(hk.kiem_bang(pb)) == 20 * 1024 * 1024
    b["canh_bao"][0] += "a"
    with pytest.raises(LoiNghiepVu) as exc:
        hk.kiem_bang(pb)
    assert exc.value.ma == "VUOT_GIOI_HAN"


@pytest.mark.parametrize("moc", [15, 55, 75, 100])
def test_xuat_huy_khong_xong_thieu_tep_va_ram_dong(monkeypatch, moc):
    core, app, pb = bang_demo()
    bo_nho = []
    class BoNho(BytesIO):
        def __init__(self):
            super().__init__()
            bo_nho.append(self)
    monkeypatch.setattr(xuat, "BytesIO", BoNho)
    bao = core._tien_do
    def huy(ma, viec, pt, cau):
        if pt == moc:
            core.huy(viec)
        return bao(ma, viec, pt, cau)
    monkeypatch.setattr(core, "_tien_do", huy)
    truoc = core.so_lan_ghi["ket_qua"]
    kq, _ = xuat_demo(pb, core, app)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == truoc
    assert all(b.closed for b in bo_nho)


@pytest.mark.parametrize("lan_loi", [1, 2])
def test_loi_tai_mot_trong_hai_tep_khong_xong_khong_lo_du_lieu(monkeypatch, capsys, lan_loi):
    core, app, pb = bang_demo()
    tai = core._tai_tep_ra
    da_goi = []
    def hong(*a, **k):
        da_goi.append(1)
        if len(da_goi) == lan_loi:
            raise RuntimeError("DEMO-BI-MAT và đường máy DEMO")
        return tai(*a, **k)
    monkeypatch.setattr(core, "_tai_tep_ra", hong)
    kq, _ = xuat_demo(pb, core, app)
    loi(kq, "XUAT_KET_QUA_LOI")
    assert "DEMO-BI-MAT" not in capsys.readouterr().err + str(kq)


def test_writer_hong_khong_tai_bat_ky_tep_va_bo_nho_dong(monkeypatch):
    core, app, pb = bang_demo()
    ds = []
    class BoNho(BytesIO):
        def __init__(self):
            super().__init__()
            ds.append(self)
    monkeypatch.setattr(xuat, "BytesIO", BoNho)
    def hong(*a, **k):
        raise ValueError("DEMO lỗi writer")
    monkeypatch.setattr(xuat, "write_xlsx", hong)
    truoc = core.so_lan_ghi["tep"]
    loi(xuat_demo(pb, core, app)[0], "XUAT_KET_QUA_LOI")
    assert core.so_lan_ghi["tep"] == truoc and ds[0].closed


def test_mat_ack_tep_ket_qua_ket_thuc_chi_ghi_mot_lan_va_khong_ghi_dia_mang(monkeypatch):
    core, app, pb = bang_demo()
    truoc = dict(core.so_lan_ghi)
    for t in ("tep", "ket_qua", "ket_thuc"):
        core.gay_mat_xac_nhan(t)
    mo = builtins.open
    def mo_an_toan(file, mode="r", *a, **k):
        assert not any(c in mode for c in "wax+"), "Không ghi tệp"
        return mo(file, mode, *a, **k)
    monkeypatch.setattr(builtins, "open", mo_an_toan)
    monkeypatch.setattr(Path, "write_bytes", lambda *a, **k: pytest.fail("Không ghi đĩa"))
    monkeypatch.setattr(Path, "write_text", lambda *a, **k: pytest.fail("Không ghi đĩa"))
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("Không gọi mạng"))
    kq, _ = xuat_demo(pb, core, app)
    assert kq["trang_thai"] == "XONG", kq
    assert core.so_lan_ghi["tep"] == truoc["tep"] + 2
    assert core.so_lan_ghi["ket_qua"] == truoc["ket_qua"] + 1
    assert core.so_lan_ghi["ket_thuc"] == truoc["ket_thuc"] + 1
    for t in ("tep", "ket_qua", "ket_thuc"):
        nhat_ky = [n for n in core.nhat_ky if n[0] == t and n[2] == kq["id"]]
        assert len(nhat_ky) >= 2


@pytest.mark.parametrize("nguon", ["docx", "abbyy"])
def test_chuoi_docx_hoac_ocr_gia_chuan_bi_ai_gia_hau_kiem_xuat(nguon):
    core = CoreGia()
    app = app_tx3(core)
    if nguon == "docx":
        tep = core.them_tep("DEMO.docx", (GOC_GOI / "demo/DEMO-hop-dong.docx").read_bytes(),
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        kq = core.chay_thu(app, "trich.doc_docx@1", {"loai": "tep", "tep": tep})
        assert kq["trang_thai"] == "XONG"
        dv = kq["ket_qua"]
    else:
        dv = deepcopy(VD["dau_vao"])
        tl = dv["van_ban_tai_lieu"]
        text = "DEMO-001. 1.000.000 VND"
        tl.update(van_ban=text + "\f" + text, nguon_doc="abbyy", so_trang=2,
                  trang=[{"so": i, "rong": 100, "cao": 200, "don_vi": "pt",
                          "khoi": [{"loai": "doan", "van_ban": text, "hop": [i, 10, 90, 30]}]}
                         for i in (1, 2)])
    core, app, req = chuan_bi_demo(core, app, dau_vao=dv)
    p = deepcopy(PHIEU)
    p.update(ma="e_ai_demo", nang_luc=[{"ma": "ai.hoi_theo_yeu_cau@1", "ten": "AI giả DEMO",
        "nhan": ["yeu_cau_ai"], "tra": "tra_loi_ai", "gioi_han": {"thoi_han_giay": 30}}],
        loai_du_lieu_rieng=app.phieu["loai_du_lieu_rieng"], chay_thu_demo=[])
    ai = Engine(p, thu_muc_goi=GOC_GOI)
    @ai.nang_luc("ai.hoi_theo_yeu_cau@1")
    def hoi_gia(viec):
        r = viec.dau_vao["yeu_cau_ai"]
        # Nhà cung cấp giả chỉ nhận prompt/tài liệu/khuôn, không chuyen_tiep.
        model_nhan = {k: r[k] for k in ("prompt", "tai_lieu", "khuon_tra_loi")}
        assert "chuyen_tiep" not in model_nhan
        kq = ai_demo(viec.dau_vao)
        if nguon != "docx":
            q = kq["tra_loi_ai"]["du_lieu"]["TT-02"]["trich_dan"][0]
            q["bat_dau"] += len(text) + 1
            q["ket_thuc"] += len(text) + 1
        return kq
    kq = core.chay_thu(ai, "ai.hoi_theo_yeu_cau@1", req)
    assert kq["trang_thai"] == "XONG"
    kq = core.chay_thu(app, "trich.hau_kiem@1", kq["ket_qua"])
    assert kq["trang_thai"] == "XONG", kq
    if nguon != "docx":
        vt = kq["ket_qua"]["bang_trich_xuat"]["bang"][1]["dan_chung"][0]["vi_tri"]
        assert vt["so_trang"] == 2 and vt["hop"] == [2, 10, 90, 30]
    kq, _ = xuat_demo(kq["ket_qua"], core, app)
    assert kq["trang_thai"] == "XONG" and kq["ket_qua"]["loai"] == "truong"


def test_hai_demo_da_dang_ky_chay_du():
    ds = chay_demo_tx3()
    assert len(ds) == 2 and all(x["trang_thai"] == "XONG" for x in ds)


def test_mat_ack_hai_tap_dung_khoa_rieng_nhung_retry_cung_khoa():
    core, app, pb = bang_demo()
    for t in ("tep", "ket_qua", "ket_thuc"):
        core.gay_mat_xac_nhan(t)
    kq, _ = xuat_demo(pb, core, app)
    assert kq["trang_thai"] == "XONG"
    for t, so_khoa, so_goi in (("tep", 2, 3), ("ket_qua", 1, 2), ("ket_thuc", 1, 2)):
        ds = [n for n in core.nhat_ky if n[0] == t and n[2] == kq["id"]]
        assert len(ds) == so_goi and len({n[3] for n in ds}) == so_khoa


def test_xuat_huy_giua_writer_dong_ram_va_khong_tai(monkeypatch):
    from types import SimpleNamespace
    _, _, pb = bang_demo()
    bo_nho = []
    class BoNho(BytesIO):
        def __init__(self):
            super().__init__()
            bo_nho.append(self)
    monkeypatch.setattr(xuat, "BytesIO", BoNho)
    dem = []
    def kiem_huy():
        dem.append(1)
        if len(dem) == 6:
            raise ViecDaHuy()
    viec = SimpleNamespace(dau_vao=pb, kiem_huy=kiem_huy, tien_do=lambda *a: None,
                           tai_tep_ra=lambda *a: pytest.fail("Chưa được tải tệp"))
    with pytest.raises(ViecDaHuy):
        xuat.xuat_ket_qua(viec)
    assert bo_nho[0].closed


def test_xuat_core_khong_tra_du_metadata_khong_xong(monkeypatch):
    core, app, pb = bang_demo()
    tai = core._tai_tep_ra
    def sai(*a, **k):
        tai(*a, **k)
        return {}
    monkeypatch.setattr(core, "_tai_tep_ra", sai)
    loi(xuat_demo(pb, core, app)[0], "XUAT_KET_QUA_LOI")


def test_xuat_tien_thieu_ma_tien_te_va_so_khong_huu_han():
    _, _, pb = bang_demo()
    for v in ({"so": 100, "tien_te": ""}, {"so": True, "tien_te": "VND"},
              {"so": float("inf"), "tien_te": "VND"}):
        p = deepcopy(pb)
        p["bang_trich_xuat"]["bang"][0].update(kieu="so_tien", gia_tri=v)
        with pytest.raises(LoiNghiepVu) as exc:
            hk.kiem_bang(p)
        assert exc.value.ma == "KET_QUA_KHONG_HOP_LE"


@pytest.mark.parametrize("so, dung", [
    (1000000, True), (0, True), (-100, True), (10000000000000001, True),
    ("1000000.50", True), ("-0.05", True), ("0", True),
    (1000000.5, False), (1.0, False), (True, False),
    ("1.000.000", False), ("1,5", False), ("1e6", False),
    ("NaN", False), ("Infinity", False), (" 100", False), ("", False),
])
def test_so_tien_chi_nhan_int_hoac_chuoi_thap_phan_chinh_xac(so, dung):
    core, app, pb = bang_demo()
    pb["bang_trich_xuat"]["bang"][0].update(
        kieu="so_tien", kieu_da_chuyen=True, gia_tri={"so": so, "tien_te": "VND"})
    truoc = core.so_lan_ghi["tep"]
    kq, _ = xuat_demo(pb, core, app)
    if not dung:
        loi(kq, "KET_QUA_KHONG_HOP_LE")
        assert core.so_lan_ghi["tep"] == truoc
    else:
        assert kq["trang_thai"] == "XONG", kq
        t = kq["ket_qua"]["truong"]
        bang = json.loads(core.doc_tep(t["tep_json"]["tep_id"]))["bang_trich_xuat"]["bang"]
        assert type(bang[0]["gia_tri"]["so"]) is type(so) and bang[0]["gia_tri"]["so"] == so
        excel = doc_excel(core.doc_tep(t["tep_excel"]["tep_id"]))
        assert json.loads(excel[1][3]) == {"so": so, "tien_te": "VND"}
