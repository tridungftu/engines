"""Đã kiểm bằng Core giả (CoreGia) + Local HTTP giả; không gọi máy thật.

SDK chưa có tác vụ quản trị: adapter CHỈ TRONG TEST gọi hàm với snapshot/ngăn
của một việc DEMO. Không đăng ký năng lực hoặc sửa manifest gói phát hành.
"""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, NganEngine
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoi_ai import quan_tri
from e_hoi_ai.chay import app
from e_hoi_ai.chon_model import DanhSachModel, ModelLocal, CAC_API
from local_gia import LocalGia


def chay_quan_tri(ham, dau_vao, cau_hinh=None, truoc=None):
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = phieu["nang_luc"][:1]
    phieu["chay_thu_demo"] = phieu["chay_thu_demo"][:1]
    ung_dung = Engine(phieu, thu_muc_goi=app.thu_muc_goi)
    core = CoreGia(ung_dung)
    if cau_hinh:
        core.dat_cau_hinh(app.ma, cau_hinh)
    if truoc:
        truoc(core, ung_dung)

    @ung_dung.nang_luc("ai.hoi_tai_lieu@1")
    def adapter(viec):
        kq = ham(SimpleNamespace(dau_vao=dau_vao, cau_hinh=viec.cau_hinh,
                                 ngan=viec.ngan, kiem_huy=viec.kiem_huy))
        return {"loai": "truong", "truong": {"tra_loi": json.dumps(kq), "co_can_cu": False,
                "trich_dan": "", "model": "DEMO", "ly_do_chon_model": "DEMO"}}

    vd = phieu["chay_thu_demo"][0]
    kq = core.chay_thu(ung_dung, vd["nang_luc"], vd["dau_vao"], vd["tham_so"])
    return kq, core


@pytest.mark.parametrize("ham", [quan_tri.kiem_ket_noi, quan_tri.lay_danh_sach_model])
@pytest.mark.parametrize("loai", ["ollama", "lm1", "lm0", "openai"])
def test_kiem_lay_model_coregia_va_may_gia(ham, loai):
    with LocalGia() as may:
        if loai == "ollama":
            may.tags = [{"name": "model-demo"}, {"name": "model-demo-cloud", "remote": True}]
        elif loai == "lm1":
            may.native_v1 = [{"key": "model-demo", "loaded_instances": [{}]}]
        elif loai == "lm0":
            may.native_v0 = [{"id": "model-demo", "state": "loaded"}]
        ch = {"local_ai": {"url": may.url + "/v1", "timeout_giay": 60}}
        kq, core = chay_quan_tri(ham, {}, ch)
        assert kq["trang_thai"] == "XONG", kq
        gt = json.loads(kq["ket_qua"]["truong"]["tra_loi"])
        assert gt["ket_noi"] and gt["url"] == may.url + "/v1"
        assert gt["models"][0] == {"id_model": "model-demo", "kha_dung": True}
        if loai == "ollama":
            assert gt["models"][1]["kha_dung"] is False
        ban = core.xem_ngan(app.ma, "model_phat_hien")
        assert any(b["id_model"] == "model-demo" for b in ban)
        assert all(method == "GET" for method, _ in may.luot)
        assert may.so_luot_hoi == 0


def test_model_rong_la_ket_noi_duoc():
    with LocalGia() as may:
        may.models = []
        kq, _ = chay_quan_tri(quan_tri.kiem_ket_noi, {"url": may.url})
        gt = json.loads(kq["ket_qua"]["truong"]["tra_loi"])
        assert gt["ket_noi"] and gt["models"] == []


def test_may_loi_khong_thanh_cong_gia_va_khong_lo_chi_tiet():
    with LocalGia() as may:
        for _, duong, *_ in CAC_API:
            may.phan_hoi_get[duong] = (500, b"DEMO-BI-MAT-KHONG-HIEN")
        kq, _ = chay_quan_tri(quan_tri.kiem_ket_noi, {"url": may.url})
        gt = json.loads(kq["ket_qua"]["truong"]["tra_loi"])
        assert gt["ket_noi"] is False and gt["models"] == []
        assert "DEMO-BI-MAT" not in str(gt)


@pytest.mark.parametrize("gt", [None, {"url": "https://127.0.0.1:11434"},
    {"url": "http://8.8.8.8:11434"}, {"url": "http://ai.example:11434"},
    {"url": "http://127.0.0.1:11434?key=DEMO"}, {"url": "http://127.0.0.1:65536"},
    {"url": "http://127.0.0.1:11434", "timeout_giay": True},
    {"url": "http://127.0.0.1:11434", "timeout_giay": float("nan")},
    {"url": "http://127.0.0.1:11434", "timeout_giay": 6}])
def test_tu_choi_truoc_mang_va_loi_tieng_viet(gt, monkeypatch):
    def cam(*args, **kw):
        pytest.fail("Không được gọi mạng với đầu vào sai")
    monkeypatch.setattr(quan_tri.BoPhatHienModel, "phat_hien", cam)
    kq, _ = chay_quan_tri(quan_tri.kiem_ket_noi, gt)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "CAU_HINH_KHONG_HOP_LE"
    assert "DEMO" not in kq["loi"]["thong_diep"]


def test_tim_tu_config_ngan_loopback_khong_ghi_catalog(monkeypatch):
    da_kiem = []
    def phat_hien(self, ch, **kw):
        da_kiem.append(ch.copy())
        return DanhSachModel("ollama", CAC_API[0], (ModelLocal("model-demo", True),)) if ch["url"].endswith(":12345") else None
    monkeypatch.setattr(quan_tri.BoPhatHienModel, "phat_hien", phat_hien)
    def nap(core, ung_dung):
        ngan = NganEngine(core.duong_truyen(app.ma), ung_dung._cfg)
        with ngan.lo() as lo:
            lo.them("model_phat_hien", {"id_model": "model-demo", "url": "http://127.0.0.1:12345", "kha_dung": True})
    kq, core = chay_quan_tri(quan_tri.tim_may_ai, {}, {"local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60}}, nap)
    assert kq["trang_thai"] == "XONG", kq
    gt = json.loads(kq["ket_qua"]["truong"]["tra_loi"])
    assert gt["so_da_kiem"] == 3 and len(gt["danh_sach"]) == 1
    assert all(ch["timeout_giay"] == 1 for ch in da_kiem)
    assert core.xem_ngan(app.ma, "model_phat_hien")[0]["row_version"] == 1


@pytest.mark.parametrize("dau_vao", [{"danh_sach_url": "DEMO"}, {"danh_sach_url": ["http://127.0.0.1:11434"] * 17},
    {"danh_sach_url": [f"http://127.0.0.1:{i+20000}" for i in range(16)]}])
def test_tim_vuot_tran_tu_choi_khong_cat_ngam(dau_vao, monkeypatch):
    monkeypatch.setattr(quan_tri.BoPhatHienModel, "phat_hien", lambda *a, **k: pytest.fail("Vượt trần không được gọi mạng"))
    kq, _ = chay_quan_tri(quan_tri.tim_may_ai, dau_vao)
    assert kq["loi"]["ma"] == "VUOT_GIOI_HAN"


def test_tim_khong_tim_duoc(monkeypatch):
    monkeypatch.setattr(quan_tri.BoPhatHienModel, "phat_hien", lambda *a, **k: None)
    kq, _ = chay_quan_tri(quan_tri.tim_may_ai, {})
    assert json.loads(kq["ket_qua"]["truong"]["tra_loi"]) == {"danh_sach": [], "so_da_kiem": 2}


def test_loi_ngan_khong_bi_doi_thanh_mat_ket_noi(monkeypatch):
    monkeypatch.setattr(quan_tri.BoPhatHienModel, "phat_hien", lambda *a, **k: None)
    def loi(*a):
        raise LoiNghiepVu("NGAN_XUNG_DOT", "Danh sách model vừa thay đổi. Hãy thử lại.", thu_lai_duoc=True)
    monkeypatch.setattr(quan_tri, "_luu_catalog", loi)
    kq, _ = chay_quan_tri(quan_tri.kiem_ket_noi, {"url": "http://127.0.0.1:11434"})
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "NGAN_XUNG_DOT"


def test_schema_moi_cap_co_nhan_dien_giai_va_mau():
    goi = Path(app.thu_muc_goi)
    schema = json.loads((goi / "cau_hinh.schema.json").read_text(encoding="utf-8"))
    def kiem(s):
        assert all(s.get(k) for k in ("title", "description", "examples"))
        for con in s.get("properties", {}).values():
            kiem(con)
        if "items" in s:
            kiem(s["items"])
    kiem(schema)
    assert "Mẫu đầy đủ:" in schema["description"] and "https?" not in schema["properties"]["local_ai"]["properties"]["url"]["pattern"]
    khai = json.loads((goi / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
    assert {k["ma"] for k in khai["thao_tac_quan_tri"]} == {"kiem_ket_noi", "lay_danh_sach_model", "tim_may_ai"}
    assert "thao_tac_quan_tri" not in app.phieu
