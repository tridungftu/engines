"""Công cụ TX-6 chỉ kiểm bằng Local giả/transport giả, không chạy --that."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import socket
import sys
import unicodedata
import re

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cong-cu"))
import ho_tro_do as h
import do_n1_mot_lan as n1
import do_suc_chua_model as t3


@pytest.fixture
def bo_demo_lf(tmp_path):
    """Staging đúng bytes nguồn đã ghim, không sửa fixture chỉ đọc trong checkout.

    Git Windows có thể đổi LF->CRLF; staging test tách khỏi kiểm E6 nguồn thật.
    Nếu nội dung khác ngoài xuống dòng, băm vẫn thất bại. Không dùng trong runtime.
    """
    goc = h.ENGINE / "tham-chieu/e6"
    m = json.loads((goc / "chap-nhan.json").read_text(encoding="utf-8"))
    for c in m["cac_ca"]:
        for k in ("docx", "vang", "tham_so", "ai"):
            spec = c[k]
            raw = (goc / spec["tep"]).read_bytes()
            if spec["tep"].endswith(".json"):
                raw = raw.replace(b"\r\n", b"\n")
            assert h.bam(raw) == spec["bam"]
            (tmp_path / spec["tep"]).write_bytes(raw)
    tep = tmp_path / "chap-nhan.json"
    tep.write_bytes((goc / "chap-nhan.json").read_bytes().replace(b"\r\n", b"\n"))
    return tep


def test_t3_chay_kho_9_tai_bam_phu_luc_va_null_runtime(monkeypatch, tmp_path):
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("Không mạng"))
    monkeypatch.setattr(h.ai_cuc_bo, "_gui_post", lambda *a, **k: pytest.fail("Không POST"))
    monkeypatch.setattr(t3, "LocalThat", lambda *a, **k: pytest.fail("Không dựng Local thật"))
    tep = tmp_path / "T3.json"
    assert t3.main(["--url", "http://127.0.0.1:9", "--dau-ra", str(tep)]) == 0
    v, _ = h.doc_artifact(tep)
    assert v["trang_thai"] == "chay_kho" and v["so_luot_local_that"] == v["so_luot_cloud"] == 0
    assert len(v["cac_ca"]) == 9
    assert {r["mau"] for r in v["cac_ca"]} == {"DEMO-1", "DEMO-20", "DEMO-60"}
    for r in v["cac_ca"]:
        assert r["so_o_tra"] == r["mau_so"] == 37 and r["qua_hau_kiem"]
        assert all(r[k] is None for k in ("token_vao", "token_ra", "token_reasoning", "thoi_gian_giay"))
        assert r["bam_prompt_phu_luc_a"] == "sha256:290bb3c5a0264e289bdf8b2de0b29d226f6db464d7581b7ed312449a3f3f6ba5"
        assert r["bam_khuon_phu_luc_a"] == "sha256:0e55030f86901fafc93d0a292c63f08deabbb35ee1aec92cfc54628131c99de8"
        assert r["token_uoc_luong_phu_luc_a"] in (1967, 20971, 60981)
        assert r["bam_prompt"] != r["bam_prompt_phu_luc_a"]  # Giao thức TX-2 được băm riêng.
    assert "Công ty" not in tep.read_text(encoding="utf-8")
    _, _, _, docs = h.corpus_t3()
    assert [len(s) for s in docs.values()] == [2227, 78246, 238286]
    assert h.bam(docs[1].encode()) == "sha256:b6b511f069739ab4b6012ca161882244482b1a8da6da62eee50b6498f1f9e209"


def test_n1_kho_nguon_ghim_cham_khong_tieu_thu_luot(monkeypatch, bo_demo_lf, tmp_path):
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("Không mạng"))
    monkeypatch.setattr(n1, "LocalThat", lambda *a, **k: pytest.fail("Không dựng Local thật"))
    tep = tmp_path / "N1-kho.json"
    assert n1.main(["--bo-demo", str(bo_demo_lf), "--dau-ra", str(tep)]) == 0
    v, _ = h.doc_artifact(tep)
    assert v["trang_thai"] == "chay_kho" and v["bam_nen"] is None and v["so_lan_n1"] == 0
    assert not list(tmp_path.glob("*.da-nhan.json"))
    assert len(v["cac_ca"]) == 2 and all(c["cham"]["da_do"] == 37 for c in v["cac_ca"])
    assert all(c["so_do"]["token_vao"] is None for c in v["cac_ca"])
    assert "Công ty" not in tep.read_text(encoding="utf-8") and "duong_dan" not in tep.read_text(encoding="utf-8")


@pytest.mark.parametrize("thieu", ["context_hieu_dung", "token_ra_toi_da", "du_phong_boc", "runtime", "quantization", "bam_bien_ban_runtime"])
def test_thieu_cau_hinh_so_do_khong_tu_gan_0(thieu):
    cfg = h.cfg_gia("gemma")
    cfg[thieu] = None
    with pytest.raises(h.LoiDo):
        h.cau_hinh_model(cfg)


@pytest.mark.parametrize("id_model,vai_tro,hop_le", [
    ("qwen3:8b", "qwen3_8b", True), ("qwen3:4b", "qwen3_8b", False),
    ("gpt-oss:20b", "gpt_oss_20b", True), ("gpt-oss:120b", "gpt_oss_20b", False),
    ("gemma-ID-da-phat-hien", "gemma", True), ("khong-ro", "gemma", False)])
def test_khong_doan_model_bien_the_context(id_model, vai_tro, hop_le):
    cfg = h.cfg_gia(vai_tro)
    cfg["id"] = id_model
    if hop_le:
        h.kiem_id_model(cfg)
    else:
        with pytest.raises(h.LoiDo):
            h.kiem_id_model(cfg)


def test_preflight_chan_truoc_gui_khong_cat_du_lieu():
    core, app, req, _ = h.tao_yeu_cau_t3(1, "DEMO-qwen3_8b")
    cu = deepcopy(req)
    cfg = h.cfg_gia("qwen3_8b")
    cfg["context_hieu_dung"] = 1024
    local = h.LocalGia([cfg])
    so, b = h.do_mot_ca(core, app, req, cfg, local)
    assert local.so_gui == 0 and b is None and so["tran"] is None and so["tu_choi"] is True
    assert so["vuot_tran_ngan_sach"] and so["tu_choi_truoc_gui"] and so["nguon_tu_choi"] == "cong_cu"
    assert so["token_vao"] is so["thoi_gian_giay"] is None and req == cu


def test_tokenizer_ghim_dung_body_ke_ca_phan_boc():
    _, _, req, _ = h.tao_yeu_cau_t3(1, "DEMO-qwen3_8b")
    cfg = h.cfg_gia("qwen3_8b")
    body = h.dong_goi(req, cfg["id"], "openai_compatible", cfg["token_ra_toi_da"])
    cfg["token_vao_da_kiem"] = {h.bam(body): {"so": 1000, "bam_bien_ban": h.bam(b"DEMO-tokenizer")}}
    so = h.kiem_context(body, cfg)
    assert so["token_vao_truoc_gui_da_dem"] == 1000
    assert so["tran_token_vao_truoc_gui"] == 1000 + cfg["du_phong_boc"]
    body["messages"][1]["content"] += "DEMO đổi phần bọc"
    assert h.kiem_context(body, cfg)["token_vao_truoc_gui_da_dem"] is None
    assert "chuyen_tiep" not in body and req["yeu_cau_ai"]["tai_lieu"] in json.loads(
        body["messages"][1]["content"].split("Yêu cầu của module và tài liệu (JSON):\n")[1].split("\nThay đối tượng JSON mẫu")[0])["tai_lieu"]


def local_transport_gia(monkeypatch, raw):
    cfg = h.cfg_gia("qwen3_8b")
    cfg["id"] = "qwen3:8b"
    local = h.LocalThat("http://127.0.0.1:9", [cfg])
    local.loai = "openai_compatible"
    monkeypatch.setattr(local, "phat_hien", lambda: [cfg["id"]])
    monkeypatch.setattr(h.ai_cuc_bo, "_gui_post", lambda *a, **k: raw)
    return local, cfg


def test_transport_gia_giu_so_runtime_thieu_reasoning_la_null(monkeypatch):
    core, app, req, _ = h.tao_yeu_cau_t3(1, "qwen3:8b")
    data = h.du_lieu_gia(req)
    raw = {"model": "qwen3:8b", "usage": {"prompt_tokens": 6000, "completion_tokens": 50},
           "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"du_lieu": data})}}]}
    local, cfg = local_transport_gia(monkeypatch, raw)
    so, b = h.do_mot_ca(core, app, req, cfg, local)
    assert so["token_vao"] == 6000 and so["token_ra"] == 50 and so["token_reasoning"] is None
    assert so["thoi_gian_giay"] >= 0 and b and local.so_gui == 1


@pytest.mark.parametrize("cat,refusal", [(True, None), (False, "DEMO từ chối")])
def test_cat_tu_choi_khong_thanh_cong_khong_hoi_lai(monkeypatch, cat, refusal):
    core, app, req, _ = h.tao_yeu_cau_t3(1, "qwen3:8b")
    raw = {"model": "qwen3:8b", "usage": {"prompt_tokens": 80, "completion_tokens": 12},
           "choices": [{"finish_reason": "length" if cat else "stop",
                        "message": {"content": "{}", "refusal": refusal}}]}
    local, cfg = local_transport_gia(monkeypatch, raw)
    so, b = h.do_mot_ca(core, app, req, cfg, local)
    assert b is None and not so["qua_hau_kiem"] and local.so_gui == 1
    assert so["cat"] == cat and so["tu_choi"] == bool(refusal) and so["token_ra"] == 12


def test_model_sai_khong_fallback_khong_gui(monkeypatch):
    _, _, req, _ = h.tao_yeu_cau_t3(1, "qwen3:8b")
    local, cfg = local_transport_gia(monkeypatch, {})
    monkeypatch.setattr(local, "phat_hien", lambda: ["qwen3:4b"])
    with pytest.raises(h.LoiDo):
        local.hoi(req, cfg)
    assert local.so_gui == 0


def test_chua_ro_dung_t3_khong_gui_luot_sau():
    configs = [h.cfg_gia(v) for v in h.VAI_TRO]
    class DaNhan(h.LocalGia):
        def hoi(self, *a, **k):
            self.so_gui += 1
            raise h.ChuaRo("DEMO-tx6-cho-nguon")
    local = DaNhan(configs)
    v, code = t3.chay(configs, local)
    assert code == 2 and local.so_gui == 1 and v["trang_thai"] == "chua_ro"
    assert v["ma_tuong_quan"] == "DEMO-tx6-cho-nguon"
    assert v["cac_ca"][0]["token_vao"] is None


def test_cham_n1_giu_compare_nguon_va_mau_so():
    text = (h.ENGINE / "ma-nguon/vendor/review/kiem_tra.py").read_text(encoding="utf-8")
    cay = ast.parse(text)
    ham = ast.Module(body=[n for n in cay.body if isinstance(n, ast.FunctionDef)
                           and n.name in ("norm", "_ngay", "compare")], type_ignores=[])
    ns = {"re": re, "unicodedata": unicodedata}
    exec(compile(ham, "DEMO-compare-chuan", "exec"), ns)
    for g, a in [("100", "1000"), ("30 tháng 10 năm 2026", "30/10/2026"), ("DEMO", "khác"), ("kí", "ký")]:
        assert h.compare(g, a) == ns["compare"](g, a)
    vang = {"gia_tri": {r[0]: None for r in h.ma_37()}}
    vang["gia_tri"].update({"TC-01": "DEMO-001", "TC-02": "2026-10-30"})
    v = h.cham_n1(vang, [{"ma": "TC-01", "gia_tri": "DEMO-001"}])
    assert (v["da_do"], v["dat"], v["ty_le"]) == (1, 1, 1.0)
    assert next(x for x in v["tham_so"] if x["ma"] == "TC-02")["dat"] is None
    v = h.cham_n1(vang, None)
    assert v["da_do"] == 0 and v["dat"] is v["ty_le"] is None


def nen_gia(cac_ca, b, cfg):
    ds = []
    for c in cac_ca:
        core, _, req = h.yeu_cau_n1(c, cfg)
        ds.append({"ma": c["ma"], "bam_nguon": deepcopy(c["bam"]), "ghim": n1.ghim_yeu_cau(req, core),
                   "cham": h.cham_n1(c["vang"], [{"ma": k, "gia_tri": v} for k, v in c["vang"]["gia_tri"].items()])})
    return {"nhan": "DEMO", "chap_nhan_lead": "đã duyệt", "bien_ban_lead": "DEMO-test-giả",
            "bam_nguon_cham": "sha256:" + h.BAM_NGUON_CHAM,
            "cach_cham": h.CACH_CHAM, "model": cfg["id"], "bam_cau_hinh": h.bam_cau_hinh(cfg),
            "bam_bo_demo": b, "cac_ca": ds}


@pytest.mark.parametrize("doi", ["thieu", "bam", "model", "cau_hinh", "dap_an", "mau_so", "chuaky"])
def test_n1_tu_choi_nen_thieu_khac_ghim(bo_demo_lf, tmp_path, doi):
    ds, b = h.doc_bo_demo(bo_demo_lf)
    cfg = h.cfg_gia("qwen3_8b")
    v = nen_gia(ds, b, cfg)
    if doi == "thieu": v = {}
    if doi == "model": v["model"] = "DEMO-khac"
    if doi == "cau_hinh": v["bam_cau_hinh"] = h.bam(b"DEMO-khac")
    if doi == "dap_an": v["cac_ca"][0]["bam_nguon"]["vang"] = h.bam(b"DEMO-khac")
    if doi == "mau_so": v["cac_ca"][0]["cham"]["da_do"] = 0
    if doi == "chuaky": v["bien_ban_lead"] = None
    tep = tmp_path / "nen-gia.json"
    h.ghi_artifact(tep, v)
    with pytest.raises(h.LoiDo):
        n1.kiem_nen(tep, h.bam(b"DEMO-sai") if doi == "bam" else h.bam(tep.read_bytes()), cfg, ds, b)


def test_dau_n1_doc_lap_ten_bien_ban_khong_xoa_sau_loi(tmp_path):
    nen = tmp_path / "nen-gia.json"
    nen.write_text("DEMO", encoding="utf-8")
    b = h.bam(nen.read_bytes())
    dau = n1.giu_luot_n1(nen, b)
    assert dau.exists()
    with pytest.raises(h.LoiDo):
        n1.giu_luot_n1(nen, b)
    assert dau.exists()  # Chưa rõ/lỗi không cấp lại lượt N1 tự động.


def test_nen_du_so_va_giu_dung_mau_so_cham(bo_demo_lf, tmp_path):
    ds, b = h.doc_bo_demo(bo_demo_lf)
    cfg = h.cfg_gia("qwen3_8b")
    v = nen_gia(ds, b, cfg)
    tep = tmp_path / "nen-du-so-gia.json"
    h.ghi_artifact(tep, v)
    assert n1.kiem_nen(tep, h.bam(tep.read_bytes()), cfg, ds, b)[0] == v


@pytest.mark.parametrize("thieu", ["token_vao", "token_ra", "token_reasoning", "thoi_gian_giay"])
def test_thieu_so_runtime_khong_du_dieu_kien_nghiem_thu(thieu):
    so = {"token_vao": 100, "token_ra": 20, "token_reasoning": 0, "thoi_gian_giay": 1.5}
    assert h.co_du_so_runtime(so)  # 0 reasoning có đo thực được giữ nguyên.
    so[thieu] = None
    assert not h.co_du_so_runtime(so)


def test_model_spec_ascii_va_thieu_so_thoat_khac_0(monkeypatch):
    cfg = h.doc_model_spec("qwen3_8b,qwen3:8b,32768,8192,2048,DEMO-runtime,DEMO-quant," + h.bam(b"DEMO"))
    assert cfg["id"] == "qwen3:8b" and cfg["context_hieu_dung"] == 32768
    monkeypatch.setattr(t3, "LocalThat", lambda *a, **k: pytest.fail("Không mạng"))
    assert t3.main(["--model-spec", "gemma,DEMO,CHUA_DO,8192,2048,DEMO,DEMO," + h.bam(b"DEMO")]) == 2


def test_tran_cau_hinh_trich_gim_tu_dong_lenh_khong_tu_nang(monkeypatch):
    configs = [h.cfg_gia(v) for v in h.VAI_TRO]
    h.dat_ngan_sach_trich(configs, 1024)
    local = h.LocalGia(configs)
    v, code = t3.chay(configs, local)
    assert code == 1 and local.so_gui == 0
    assert len(v["cac_ca"]) == 9 and all(c["nguon_tu_choi"] == "chuan_bi" for c in v["cac_ca"])
    with pytest.raises(h.LoiDo):
        h.dat_ngan_sach_trich(configs, 100001)


def test_schema_ngan_nguon_sha_va_cmd_ascii():
    goi = h.ENGINE / "goi/e_trich_xuat"
    for p in (goi / "contract").glob("*.json"):
        assert p.read_bytes().replace(b"\r\n", b"\n") == (h.GOC / "_chung/contract" / p.name).read_bytes().replace(b"\r\n", b"\n")
    for k in ("ngan.py", "cau_hinh.py"):
        assert (goi / "e_trich_xuat" / k).read_bytes().replace(b"\r\n", b"\n") == (h.GOC / "_chung/mau-ma" / k).read_bytes().replace(b"\r\n", b"\n")
    for p in (h.ENGINE / "cong-cu").glob("*.cmd"):
        p.read_bytes().decode("ascii")
    (h.ENGINE / "tests/kiem_may_sach.cmd").read_bytes().decode("ascii")
    assert "--no-index --no-deps" in (h.ENGINE / "tests/kiem_may_sach.cmd").read_text(encoding="ascii")
