"""TX-2: DEMO, CoreGia + NganBoNho; kiểm bất biến, giới hạn và bàn giao."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import builtins
import hashlib
import json
import math
from pathlib import Path
import socket
import threading
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from kho_tri_thuc_sdk import danh_muc_tham_so as e1
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_trich_xuat.chay import CAU_CHUA_CAU_HINH, tao_app
from e_trich_xuat.ngan import NganBoNho
from e_trich_xuat import tich_hop
from chay_demo_voi_ngan_gia import chay_demo


GOI = Path(__file__).resolve().parents[1] / "goi/e_trich_xuat"
PHIEU = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
VD = next(v for v in PHIEU["chay_thu_demo"] if v["nang_luc"] == "trich.chuan_bi@1")
SCHEMA = json.loads((GOI / "contract/yeu_cau_ai.schema.json").read_text(encoding="utf-8"))
CAU = {
    "THIEU_BO_THAM_SO": "Việc chưa có bộ tham số đã ghim.",
    "SAI_BAM_BO_THAM_SO": "Bộ tham số không khớp mã kiểm tra.",
    "BO_THAM_SO_KHONG_HOP_LE": "Bộ tham số không đúng cấu trúc hoặc có mã trùng.",
    "THIEU_PROMPT": "Module chưa cung cấp hướng dẫn trích thông tin.",
    "CAU_HOI_THEM_CHUA_DUYET": "Câu hỏi bổ sung chưa được bật.",
    "VUOT_GIOI_HAN": "Yêu cầu vượt giới hạn xử lý.",
    "VUOT_NGAN_SACH": "Tài liệu vượt ngân sách đầu vào đã cấu hình.",
    "CHUA_CAU_HINH": CAU_CHUA_CAU_HINH,
}


def bam(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def json_chuan(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def tham_so(*, bo=None, raw=None, **doi):
    ts = deepcopy(VD["tham_so"])
    if raw is None and bo is not None:
        raw = json_chuan(bo)
    if raw is not None:
        ts.update(bo_tham_so_json=raw, bam_bo_tham_so=bam(raw.encode("utf-8")))
    ts.update(doi)
    return ts


def bo_demo():
    return json.loads(VD["tham_so"]["bo_tham_so_json"])


def app_demo(tran=16000):
    app = tao_app()
    app.ngan = NganBoNho()
    if tran is not None:
        with app.ngan.lo() as lo:
            lo.them("cau_hinh", {}, {"ngan_sach_token_vao_toi_da": tran})
    return app


def chay(ts=None, *, dv=None, app=None, core=None):
    app = app if app is not None else app_demo()
    core = core if core is not None else CoreGia()
    kq = core.chay_thu(app, "trich.chuan_bi@1", deepcopy(dv or VD["dau_vao"]),
                      ts if ts is not None else tham_so())
    return kq, core


def ho_so(core, kq):
    assert kq["trang_thai"] == "XONG", kq
    req = kq["ket_qua"]["yeu_cau_ai"]
    ct = req["chuyen_tiep"]["trich_xuat"]
    raw = core.doc_tep(ct["ho_so_hau_kiem"]["tep_id"])
    assert ct["bam_ho_so_hau_kiem"] == bam(raw)
    assert ct["ho_so_hau_kiem"]["kich_thuoc"] == len(raw)
    return req, json.loads(raw)


def tu_choi(kq, core, ma):
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None, kq
    assert kq["loi"] == {"ma": ma, "thong_diep": CAU[ma], "thu_lai_duoc": False}
    assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["tep"] == 0


def test_yeu_cau_du_truong_hash_ho_so_va_ba_bam_rieng(monkeypatch):
    bo = bo_demo()
    bo["bam_tep_goc"] = bam(b"DEMO-XLSX-rieng")
    dem = []
    kiem_e1 = e1.kiem_tra_danh_muc

    def kiem(rows, **kw):
        dem.append(deepcopy((rows, kw)))
        return kiem_e1(rows, **kw)

    monkeypatch.setattr(e1, "kiem_tra_danh_muc", kiem)
    ts = tham_so(bo=bo)
    truoc = deepcopy(ts)
    kq, core = chay(ts)
    req, hs = ho_so(core, kq)
    Draft202012Validator(SCHEMA).validate(kq["ket_qua"])
    Draft202012Validator.check_schema(req["khuon_tra_loi"])
    assert len(dem) == 1 and len(dem[0][0]) == 4
    assert dem[0][0][0] == e1.HEADER and dem[0][0][-1][5] == "Không"
    dm = kiem_e1(dem[0][0], **dem[0][1])
    assert hs["ma_bam_noi_dung"] == dm.ma_bam_noi_dung
    assert hs["bam_bo_tham_so"] == bam(ts["bo_tham_so_json"].encode("utf-8"))
    assert hs["bam_tep_goc"] == bo["bam_tep_goc"]
    assert len({hs["ma_bam_noi_dung"], hs["bam_bo_tham_so"], hs["bam_tep_goc"]}) == 3
    assert hs["bo_tham_so"] == bo and hs["bo_tham_so_json"] == ts["bo_tham_so_json"]
    assert hs["cac_dong_e1"][-1]["dung"] is False
    assert hs["quy_tac"] == bo["quy_tac"]
    assert hs["tham_so_viec"]["bo_tham_so_json"] == ts["bo_tham_so_json"] and ts == truoc
    assert hs["tai_lieu"] == VD["dau_vao"]["van_ban_tai_lieu"]
    assert req["tai_lieu"] == hs["tai_lieu"]["van_ban"]
    assert req["prompt"].startswith(ts["prompt"])
    assert hs["yeu_cau_ai"] == {k: v for k, v in req.items() if k != "chuyen_tiep"}
    assert hs["bam_yeu_cau_ai"] == bam(json_chuan(hs["yeu_cau_ai"]).encode("utf-8"))
    assert hs["cau_hinh_da_ghim"]["gia_tri"] == {"ngan_sach_token_vao_toi_da": 16000}
    assert hs["ngu_canh"]["phap_nhan_id"] == "pn-demo"
    assert hs["sang_loc_ngan_sach"]["token_vao_uoc_luong"] == math.ceil((len(req["prompt"])
        + len(req["tai_lieu"]) + len(json_chuan(req["khuon_tra_loi"]))) / 4)
    ct = req["chuyen_tiep"]
    assert len(json_chuan(ct).encode("utf-8")) <= 4096
    assert "bo_tham_so" not in ct["trich_xuat"] and "tai_lieu" not in ct["trich_xuat"]
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 1


def test_hash_truoc_parse_va_giu_nguyen_whitespace_unicode(monkeypatch):
    raw = " \n" + json.dumps(bo_demo(), ensure_ascii=False, indent=2) + "\n "
    req, hs = ho_so(*reversed(chay(tham_so(raw=raw))))
    assert hs["bo_tham_so_json"] == raw
    assert req["chuyen_tiep"]["trich_xuat"]["bam_bo_tham_so"] == bam(raw.encode("utf-8"))
    # JSON sai nhưng hash sai phải dừng ở hash, trước khi gọi E1.
    monkeypatch.setattr(e1, "kiem_tra_danh_muc", lambda *a, **k: pytest.fail("Không được parse E1"))
    kq, core = chay(tham_so(raw="{JSON DEMO sai", bam_bo_tham_so=bam(b"DEMO-khac")))
    tu_choi(kq, core, "SAI_BAM_BO_THAM_SO")


@pytest.mark.parametrize("raw", [
    '{"module":"crm_demo","module":"crm_demo"}',
    '{"a":{"ma":"TT-01","ma":"TT-02"}}',
    '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1e9999}',
    '{"a":"\\ud800"}', '[]', 'null', '{DEMO sai', "\ufeff{}",
])
def test_json_nghiem_khong_lo_du_lieu(raw):
    kq, core = chay(tham_so(raw=raw))
    tu_choi(kq, core, "BO_THAM_SO_KHONG_HOP_LE")


@pytest.mark.parametrize("doi", [
    lambda b: b.pop("module"), lambda b: b.pop("loai_hop_dong"), lambda b: b.pop("quy_tac"),
    lambda b: b.update(phien_ban=True), lambda b: b.update(phien_ban_bo=""),
    lambda b: b.update(cac_dong=[]), lambda b: b.update(quy_tac={}),
    lambda b: b["cac_dong"].append(deepcopy(b["cac_dong"][0])),
    lambda b: b["cac_dong"][2].update(ma="TT-01"),
    lambda b: b["cac_dong"][0].pop("luon_cloud"),
    lambda b: b["cac_dong"][0].update(ma="Y-01"),
    lambda b: b["cac_dong"][0].update(muc=True),
    lambda b: b["cac_dong"][0].update(dung="Có"),
    lambda b: b["cac_dong"][0].update(mo_ta="D" * 1001),
    lambda b: b["cac_dong"][0].update(tk="D" * 61),
    lambda b: b.update(bam_tep_goc="DEMO-bam-sai"),
    lambda b: b.update(ma_bam_noi_dung="0" * 64),
    lambda b: b["quy_tac"][0].update(doi_chieu="TT-99"),
    lambda b: b["quy_tac"][0].update(ma_tham_so=["TT-01;TT-02"]),
])
def test_snapshot_sai_thieu_trung_hoac_e1_tu_choi(doi):
    b = bo_demo()
    doi(b)
    kq, core = chay(tham_so(bo=b))
    tu_choi(kq, core, "BO_THAM_SO_KHONG_HOP_LE")


@pytest.mark.parametrize("truong", ["bo_tham_so_json", "bam_bo_tham_so"])
def test_thieu_bo_hoac_thieu_bam_khong_fallback_xd(truong):
    ts = tham_so()
    ts.pop(truong)
    kq, core = chay(ts)
    tu_choi(kq, core, "THIEU_BO_THAM_SO" if truong == "bo_tham_so_json" else "SAI_BAM_BO_THAM_SO")


@pytest.mark.parametrize("ds, mong", [([], ["TT-01", "TT-02"]), (["TT-02"], ["TT-02"]),
                                       (["TT-02", "TT-01"], ["TT-02", "TT-01"])])
def test_danh_sach_con_dung_thu_tu_va_rong_la_toan_bo(ds, mong):
    kq, core = chay(tham_so(ma_truong_can_trich_json=json_chuan(ds)))
    req, hs = ho_so(core, kq)
    assert hs["ma_truong_can_trich"] == req["khuon_tra_loi"]["required"] == mong
    assert list(req["khuon_tra_loi"]["properties"]) == mong
    assert "TT-03" not in req["prompt"]
    assert hs["bo_tham_so"] == bo_demo()


@pytest.mark.parametrize("raw", ['["TT-02","TT-02"]', '["TT-99"]', '["TT-03"]',
                                    '[1]', 'null', '{}', '["tt-01"]', '[NaN]'])
def test_danh_sach_la_trung_ngung_dung_bi_tu_choi(raw):
    kq, core = chay(tham_so(ma_truong_can_trich_json=raw))
    tu_choi(kq, core, "BO_THAM_SO_KHONG_HOP_LE")


@pytest.mark.parametrize("raw", ['["Câu hỏi DEMO"]', '[{"ma":"Y-01"}]', '{}', 'null', '[NaN]', 'DEMO'])
def test_cau_hoi_them_chua_duyet(raw):
    kq, core = chay(tham_so(yeu_cau_them_json=raw))
    tu_choi(kq, core, "CAU_HOI_THEM_CHUA_DUYET")


@pytest.mark.parametrize("doi", [{"prompt": ""}, {"prompt": "  \n"}, {"ma_prompt": ""},
                                     {"phien_ban_prompt": ""}])
def test_prompt_thuoc_module_khong_co_mac_dinh(doi):
    kq, core = chay(tham_so(**doi))
    tu_choi(kq, core, "THIEU_PROMPT")


def test_thieu_cau_hinh_khong_tu_tao_ban_ghi():
    app = app_demo(None)
    kq, core = chay(app=app)
    tu_choi(kq, core, "CHUA_CAU_HINH")
    assert app.ngan.doc("cau_hinh", {}) is None


@pytest.mark.parametrize("vuot", [False, True])
def test_snapshot_tran_64_kib_tinh_bytes_utf8_khong_strip(vuot):
    # Chuỗi UTF-8 nhỏ hơn 65.536 ký tự vẫn có thể vượt trần byte.
    b = bo_demo()
    b["cac_dong"][0]["nhom"] = "Đ" * 18000
    raw = json_chuan(b)
    raw += " " * (65536 + int(vuot) - len(raw.encode("utf-8")))
    assert len(raw) < 65536 and len(raw.encode("utf-8")) == 65536 + int(vuot)
    kq, core = chay(tham_so(raw=raw))
    if vuot:
        tu_choi(kq, core, "VUOT_GIOI_HAN")
    else:
        _, hs = ho_so(core, kq)
        assert hs["bo_tham_so_json"] == raw


@pytest.mark.parametrize("n", [200, 201])
def test_tran_dong_dang_dung_ke_ca_chon_mot_ma(n):
    b = bo_demo()
    b["cac_dong"] = [dict(b["cac_dong"][0], ma=f"TT-{i:03d}", mo_ta="Trường DEMO")
                     for i in range(1, n + 1)]
    b["quy_tac"] = []
    kq, core = chay(tham_so(bo=b, ma_truong_can_trich_json='["TT-001"]'))
    if n == 201:
        tu_choi(kq, core, "VUOT_GIOI_HAN")
    else:
        assert ho_so(core, kq)[1]["ma_truong_can_trich"] == ["TT-001"]


def test_200_ma_du_mot_yeu_cau_khong_mat_khoa():
    b = bo_demo()
    b["cac_dong"] = [dict(b["cac_dong"][0], ma=f"TT-{i:03d}", mo_ta="Trường DEMO")
                     for i in range(1, 201)]
    b["quy_tac"] = []
    req, hs = ho_so(*reversed(chay(tham_so(bo=b))))
    assert len(req["khuon_tra_loi"]["required"]) == len(hs["ma_truong_can_trich"]) == 200
    assert set(req["khuon_tra_loi"]["properties"]) == set(req["khuon_tra_loi"]["required"])
    assert len(json_chuan(req["khuon_tra_loi"]).encode("utf-8")) <= 32768


def test_bam_e1_da_cap_va_doi_metadata_khong_doi_bam_10_cot():
    _, hs1 = ho_so(*reversed(chay()))
    b = bo_demo()
    b.update(module="module_demo_khac", phien_ban_bo="DEMO-2", ma_bam_noi_dung=hs1["ma_bam_noi_dung"])
    _, hs2 = ho_so(*reversed(chay(tham_so(bo=b))))
    assert hs1["ma_bam_noi_dung"] == hs2["ma_bam_noi_dung"]
    assert hs1["bam_bo_tham_so"] != hs2["bam_bo_tham_so"]
    # Đây chỉ kiểm toàn vẹn; hash không phải bằng chứng quyền module (C-TX-01).


@pytest.mark.parametrize("vuot", [False, True])
def test_tran_prompt_tinh_ca_phan_boc(vuot):
    kq, core = chay()
    req, _ = ho_so(core, kq)
    do_dai_phan_boc = len(req["prompt"]) - len(VD["tham_so"]["prompt"])
    prompt = "D" * (20000 + int(vuot) - do_dai_phan_boc)
    kq, core = chay(tham_so(prompt=prompt))
    if vuot:
        tu_choi(kq, core, "VUOT_GIOI_HAN")
    else:
        assert len(ho_so(core, kq)[0]["prompt"]) == 20000


@pytest.mark.parametrize("n, ma", [(500001, "VUOT_GIOI_HAN"), (500000, "VUOT_NGAN_SACH")])
def test_toan_van_vuot_tran_hoac_ngan_sach_khong_bo_trang(n, ma):
    dv = deepcopy(VD["dau_vao"])
    dv["van_ban_tai_lieu"]["van_ban"] = "D" * n
    kq, core = chay(dv=dv)
    tu_choi(kq, core, ma)


@pytest.mark.parametrize("vuot", [False, True])
def test_tran_khuon_32_kib_la_bytes_utf8(monkeypatch, vuot):
    tao = tich_hop.tao_khuon
    def khuon(params):
        k = tao(params)
        k["description"] = "Đ" * 9000
        k["description"] += "D" * (32768 + int(vuot) - len(json_chuan(k).encode("utf-8")))
        return k
    monkeypatch.setattr(tich_hop, "tao_khuon", khuon)
    kq, core = chay()
    if vuot:
        tu_choi(kq, core, "VUOT_GIOI_HAN")
    else:
        assert len(json_chuan(ho_so(core, kq)[0]["khuon_tra_loi"]).encode("utf-8")) == 32768


@pytest.mark.parametrize("ngan_sach", [0, -1, 16001, 16000.5])
def test_ngan_sach_buoc_khong_vuot_tran_cau_hinh(ngan_sach):
    kq, core = chay(tham_so(ngan_sach_token_vao=ngan_sach))
    tu_choi(kq, core, "VUOT_NGAN_SACH")


def test_ngan_sach_uoc_luong_cham_nguong_va_tran_cau_hinh_thap():
    dv = deepcopy(VD["dau_vao"])
    dv["van_ban_tai_lieu"]["van_ban"] = "Đ" * 10000
    _, hs = ho_so(*reversed(chay(dv=dv)))
    uoc = hs["sang_loc_ngan_sach"]["token_vao_uoc_luong"]
    kq, core = chay(tham_so(ngan_sach_token_vao=uoc), dv=dv)
    assert kq["trang_thai"] == "XONG"
    kq, core = chay(tham_so(ngan_sach_token_vao=uoc - 1), dv=dv)
    tu_choi(kq, core, "VUOT_NGAN_SACH")
    kq, core = chay(app=app_demo(1024))  # Mặc định bước 16.000 không được hạ ngầm.
    tu_choi(kq, core, "VUOT_NGAN_SACH")


@pytest.mark.parametrize("nguon", ["docx", "tesseract"])
def test_vi_tri_unicode_va_noi_dung_goc_docx_ocr_khong_cat(nguon):
    dv = deepcopy(VD["dau_vao"])
    vb = "DEMO 😀 a\u0301\nĐiều 1. Giá trị\n1.1. Giá: 1.000.000 VND.\fĐiều 2. Hồ sơ DEMO\n"
    dv["van_ban_tai_lieu"]["van_ban"] = vb
    dv["van_ban_tai_lieu"]["khoi_docx"] = [{"van_ban": vb, "bat_dau": 0, "ket_thuc": len(vb)}]
    if nguon == "tesseract":
        dv["van_ban_tai_lieu"].pop("khoi_docx")
        dv["van_ban_tai_lieu"].update(nguon_doc=nguon, so_trang=2, trang=[
            {"so": i, "rong": 595, "cao": 842, "don_vi": "pt", "khoi": [
                {"loai": "doan", "van_ban": text, "hop": [0, 0, 500, 800]}]}
            for i, text in enumerate(vb.split("\f"), 1)])
    schema_vao = json.loads((GOI / "contract/van_ban_tai_lieu.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema_vao).validate(dv)
    req, hs = ho_so(*reversed(chay(dv=dv)))
    assert req["tai_lieu"] == vb and hs["bam_van_ban"] == bam(vb.encode("utf-8"))
    assert hs["tai_lieu"] == dv["van_ban_tai_lieu"]
    assert "".join(vb[r["bat_dau"]:r["ket_thuc"]] for r in hs["cau_truc"]) == vb
    assert [r["nhan"] for r in hs["cau_truc"]] == ["Phần mở đầu", "Điều 1", "Điều 1 – Khoản 1.1", "Điều 2"]
    cau = "1.000.000 VND"
    o = {"gia_tri": cau, "don_vi": "VND", "ghi_chu": None,
         "trich_dan": [{"cau": cau, "bat_dau": vb.index(cau), "ket_thuc": vb.index(cau) + len(cau)}]}
    tra = {ma: deepcopy(o) for ma in req["khuon_tra_loi"]["required"]}
    Draft202012Validator(req["khuon_tra_loi"]).validate(tra)
    assert vb[o["trich_dan"][0]["bat_dau"]:o["trich_dan"][0]["ket_thuc"]] == cau
    assert "Unicode" in req["prompt"] and "UTF-16" in req["prompt"]
    for sai in ({}, {**tra, "TT-99": o}, {**tra, "TT-01": {"gia_tri": cau}}):
        assert list(Draft202012Validator(req["khuon_tra_loi"]).iter_errors(sai))


def test_hai_module_dong_thoi_khong_lan_bo_prompt_ho_so(monkeypatch):
    # Hai handler thật dùng chung app/ngăn; CoreGia riêng để cấp đúng việc.
    app, rao = app_demo(), threading.Barrier(2)
    ham = tich_hop.build_prompt
    def doi(*a):
        rao.wait(timeout=10)
        return ham(*a)
    monkeypatch.setattr(tich_hop, "build_prompt", doi)
    def lam(i):
        core = CoreGia()
        b = bo_demo()
        b.update(module=f"module_demo_{i}", loai_hop_dong=f"HD_DEMO_{i}")
        ts = tham_so(bo=b, ma_prompt=f"module_demo_{i}.trich", prompt=f"DEMO chỉ dẫn module {i}")
        kq, core = chay(ts, app=app, core=core)
        return ho_so(core, kq)
    with ThreadPoolExecutor(max_workers=2) as pool:
        ds = list(pool.map(lam, [1, 2]))
    for i, (req, hs) in enumerate(ds, 1):
        assert hs["bo_tham_so"]["module"] == f"module_demo_{i}"
        assert req["prompt"].startswith(f"DEMO chỉ dẫn module {i}")
        assert req["chuyen_tiep"]["trich_xuat"]["loai_hop_dong"] == f"HD_DEMO_{i}"
    assert ds[0][1]["bam_bo_tham_so"] != ds[1][1]["bam_bo_tham_so"]


def test_doi_bo_cau_hinh_giua_chuoi_khong_sua_snapshot_cu(monkeypatch):
    app, core = app_demo(), CoreGia()
    ban_cu = app.ngan.doc("cau_hinh", {})
    ts = tham_so()
    bao = core._tien_do
    def doi(ma, viec, phan_tram, cau):
        if phan_tram == 15:
            with app.ngan.lo() as lo:
                lo.sua("cau_hinh", {}, {"ngan_sach_token_vao_toi_da": 20000}, row_version=ban_cu.row_version)
            ts.update(tham_so(bo=dict(bo_demo(), phien_ban_bo="DEMO-2"), prompt="DEMO prompt mới"))
        return bao(ma, viec, phan_tram, cau)
    monkeypatch.setattr(core, "_tien_do", doi)
    req1, hs1 = ho_so(*reversed(chay(ts, app=app, core=core)))
    assert hs1["bo_tham_so"]["phien_ban_bo"] == "DEMO-1"
    assert hs1["cau_hinh_da_ghim"] == {"gia_tri": ban_cu.gia_tri, "phien_ban_cau_hinh": ban_cu.row_version}
    tep_id = req1["chuyen_tiep"]["trich_xuat"]["ho_so_hau_kiem"]["tep_id"]
    raw_cu = core.doc_tep(tep_id)
    monkeypatch.setattr(core, "_tien_do", bao)
    req2, hs2 = ho_so(*reversed(chay(ts, app=app, core=core)))
    assert hs2["bo_tham_so"]["phien_ban_bo"] == "DEMO-2"
    assert hs2["cau_hinh_da_ghim"]["gia_tri"]["ngan_sach_token_vao_toi_da"] == 20000
    assert hs2["cau_hinh_da_ghim"]["phien_ban_cau_hinh"] > ban_cu.row_version
    # Bước AI giả qua CoreGia: model chỉ nhận prompt/tài liệu/khuôn, chuyển tiếp trả nguyên.
    p = deepcopy(app.phieu)
    p.update(ma="e_ai_demo", nang_luc=[{"ma": "ai.hoi_theo_yeu_cau@1", "ten": "AI giả DEMO",
        "nhan": ["yeu_cau_ai"], "tra": "tra_loi_ai", "gioi_han": {"thoi_han_giay": 30}}],
        loai_du_lieu_rieng=p["loai_du_lieu_rieng"] + [{"ma": "tra_loi_ai", "ten": "Trả lời AI có trích dẫn"}],
        chay_thu_demo=[])
    ai = Engine(p)
    model_da_nhan = []
    @ai.nang_luc("ai.hoi_theo_yeu_cau@1")
    def ai_gia(viec):
        r = viec.dau_vao["yeu_cau_ai"]
        model_da_nhan.append({k: r[k] for k in ("prompt", "tai_lieu", "khuon_tra_loi")})
        return {"loai": "tra_loi_ai", "tra_loi_ai": {
            "phien_ban": 1, "trang_thai": "khong_thay_can_cu", "tra_loi": "không thấy căn cứ",
            "du_lieu": {ma: {"gia_tri": None, "don_vi": None, "ghi_chu": None, "trich_dan": []}
                        for ma in r["khuon_tra_loi"]["required"]},
            "trich_dan": [], "kiem_trich_dan": {"dat": True, "loi": []},
            "nha_cung_cap": "local", "model": "DEMO-gia", "ly_do_chon_model": "DEMO giả",
            "ma_prompt": r["ma_prompt"], "phien_ban_prompt": r["phien_ban_prompt"],
            "phien_ban_engine": "DEMO-ai-gia 1", "bam_dau_vao": bam(json_chuan(r).encode("utf-8")),
            "chuyen_tiep": deepcopy(r["chuyen_tiep"]), "canh_bao": [],
        }}
    kq = core.chay_thu(ai, "ai.hoi_theo_yeu_cau@1", {"loai": "yeu_cau_ai", "yeu_cau_ai": req1})
    assert kq["trang_thai"] == "XONG"
    assert kq["ket_qua"]["tra_loi_ai"]["chuyen_tiep"] == req1["chuyen_tiep"]
    assert "chuyen_tiep" not in model_da_nhan[0] and core.doc_tep(tep_id) == raw_cu
    assert req1["prompt"] != req2["prompt"]
    # Bước sau đọc lại bằng mo_tep của SDK; không thay bằng đọc kho ngoài cổng.
    p["ma"] = "e_hau_kiem_demo"
    p["nang_luc"] = [{"ma": "demo.doc_ho_so@1", "ten": "Đọc hồ sơ DEMO",
        "nhan": ["tra_loi_ai"], "tra": "van_ban", "gioi_han": {"thoi_han_giay": 30}}]
    sau = Engine(p)
    @sau.nang_luc("demo.doc_ho_so@1")
    def doc_ho_so(viec):
        meta = viec.dau_vao["tra_loi_ai"]["chuyen_tiep"]["trich_xuat"]
        with viec.mo_tep(meta["ho_so_hau_kiem"]["tep_id"]) as f:
            raw = f.read()
        assert bam(raw) == meta["bam_ho_so_hau_kiem"]
        assert json.loads(raw)["bo_tham_so"]["phien_ban_bo"] == "DEMO-1"
        return {"loai": "van_ban", "van_ban": "Đã đọc đúng hồ sơ DEMO cũ."}
    assert core.chay_thu(sau, "demo.doc_ho_so@1", kq["ket_qua"])["trang_thai"] == "XONG"
    # CoreGia dò tham chiếu trong đầu vào; không mô phỏng đầy đủ ACL/TTL/lưu-đóng.


@pytest.mark.parametrize("moc", [15, 70, 100])
def test_huy_khong_nop_ket_qua_khong_goi_ai(monkeypatch, moc):
    core = CoreGia()
    bao = core._tien_do
    def huy(ma, viec, phan_tram, cau):
        if phan_tram == moc:
            core.huy(viec)
        return bao(ma, viec, phan_tram, cau)
    monkeypatch.setattr(core, "_tien_do", huy)
    kq, core = chay(core=core)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert core.so_lan_ghi["ket_qua"] == 0
    assert core.so_lan_ghi["tep"] == (1 if moc == 100 else 0)


def test_mat_ack_tep_ket_qua_khong_nop_trung_va_khong_ghi_dia_mang(monkeypatch):
    app, core = app_demo(), CoreGia()
    for thao_tac in ("tep", "ket_qua", "ket_thuc"):
        core.gay_mat_xac_nhan(thao_tac)
    mo = builtins.open
    def mo_an_toan(file, mode="r", *a, **kw):
        assert not any(c in mode for c in "wax+"), "Engine không được ghi tệp"
        return mo(file, mode, *a, **kw)
    monkeypatch.setattr(builtins, "open", mo_an_toan)
    monkeypatch.setattr(Path, "write_bytes", lambda *a, **k: pytest.fail("Không ghi đĩa"))
    monkeypatch.setattr(Path, "write_text", lambda *a, **k: pytest.fail("Không ghi đĩa"))
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("Không gọi mạng"))
    kq, core = chay(app=app, core=core)
    ho_so(core, kq)
    assert all(core.so_lan_ghi[t] == 1 for t in ("tep", "ket_qua", "ket_thuc"))
    for t in ("tep", "ket_qua", "ket_thuc"):
        ds = [n for n in core.nhat_ky if n[0] == t]
        assert len(ds) == 2 and len({n[3] for n in ds}) == 1


def test_chuyen_tiep_64_kib_tu_choi_khong_cat_tham_chieu(monkeypatch):
    core = CoreGia()
    tai = core._tai_tep_ra
    def tham_chieu_lon(*a, **kw):
        kq = tai(*a, **kw)
        return {**kq, "tep_id": "D" * 65536}
    monkeypatch.setattr(core, "_tai_tep_ra", tham_chieu_lon)
    kq, core = chay(core=core)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "VUOT_GIOI_HAN"
    assert core.so_lan_ghi["ket_qua"] == 0  # Tệp đã lên Core, chờ vòng đời C-TX-02.


def test_cong_demo_ngan_thay_the_co_du_cau_hinh():
    ds = chay_demo()
    assert len(ds) == 3 and all(kq["trang_thai"] == "XONG" for kq in ds)


def test_ai_2_nhan_duoc_request_va_khuon_defs_khong_goi_model(monkeypatch):
    # Chỉ test consumer đã gộp; runtime Trích xuất không import engine khác.
    monkeypatch.syspath_prepend(str(GOI.parents[2] / "e_hoi_ai/goi/e_hoi_ai"))
    from e_hoi_ai.hoi_yeu_cau import _doc_yeu_cau
    kq, _ = chay()
    yeu_cau, raw, _ = _doc_yeu_cau(SimpleNamespace(dau_vao=kq["ket_qua"]))
    assert yeu_cau.van_ban == raw["tai_lieu"]
    assert raw["khuon_tra_loi"]["required"] == ["TT-01", "TT-02"]
