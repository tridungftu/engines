"""AI-3: đã kiểm bằng Core giả (CoreGia), chỉ Local HTTP DEMO trên loopback."""
import ipaddress
import socket

import pytest
from kho_tri_thuc_sdk.engine import ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoi_ai import chay, chon_model
from e_hoi_ai.cong_ai import CongAI, NhaCungCapLocal
from e_hoi_ai.dto import YeuCauAI
from local_gia import LocalGia, TAI_LIEU, ghi_cau_hinh


@pytest.fixture(autouse=True)
def cach_ly(monkeypatch):
    monkeypatch.setattr(chon_model, "bo_phat_hien", chon_model.BoPhatHienModel())
    luot_cloud = []

    class CloudGia:
        def hoi(self, *args, **kwargs):
            luot_cloud.append(1)
            pytest.fail("Không được gọi Cloud.")

    monkeypatch.setattr(chay.bo_hoi, "cong_ai", CongAI(nha_cung_cap={
        "local": NhaCungCapLocal(), "cloud": CloudGia(),
    }))
    ket_noi = socket.socket.connect

    def chi_loopback(self, dia_chi):
        assert ipaddress.ip_address(dia_chi[0]).is_loopback
        return ket_noi(self, dia_chi)

    monkeypatch.setattr(socket.socket, "connect", chi_loopback)
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **kw: pytest.fail("Không được tra DNS."))
    yield
    assert luot_cloud == []


def cau_hinh(may):
    return {"url": may.url, "timeout_giay": 1}


def hoi(may, tmp_path, monkeypatch, *, quy_tac=None, model=None, ma_prompt="m4.hoi"):
    tep = ghi_cau_hinh(tmp_path, may.url, quy_tac=quy_tac or [])
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    tham_so = {"ma_prompt": ma_prompt, "phien_ban_prompt": "1", "prompt": "Câu hỏi DEMO"}
    if model is not None:
        tham_so["model_uu_tien"] = model
    return CoreGia().chay_thu(chay.app, "ai.hoi_tai_lieu@1",
                             {"loai": "van_ban", "van_ban": TAI_LIEU}, tham_so)


@pytest.mark.parametrize("loai,api,truong,khoa", chon_model.CAC_API)
def test_phat_hien_tung_kieu_api_va_hoi_khong_can_v1_models(api, loai, truong, khoa,
                                                           tmp_path, monkeypatch):
    # Các ID tùy ý, không dùng tên thương mại để đoán phần mềm.
    with LocalGia() as may:
        may.models = []
        muc = {khoa: "model-demo-tu-nguon"}
        if api == "/api/tags":
            may.tags = [muc]
        elif api == "/api/v1/models":
            may.native_v1 = [{**muc, "type": "llm", "loaded_instances": [{"id": "demo"}]}]
        elif api == "/api/v0/models":
            may.native_v0 = [{**muc, "type": "llm", "state": "loaded"}]
        else:
            may.models = [muc]
        ds = chon_model.bo_phat_hien.phat_hien(cau_hinh(may))
        assert ds.loai == loai and ds.api[1] == api
        assert [m.ma for m in ds.models] == ["model-demo-tu-nguon"]
        kq = hoi(may, tmp_path, monkeypatch)
        assert kq["trang_thai"] == "XONG"
        assert kq["ket_qua"]["truong"]["model"] == "model-demo-tu-nguon"
        assert may.so_luot_hoi == 1
        if api != "/v1/models":
            assert ("GET", "/v1/models") not in may.luot


def test_cache_300_giay_va_doi_endpoint_khong_dung_chung():
    gio = [0]
    bo = chon_model.BoPhatHienModel(dong_ho=lambda: gio[0])
    with LocalGia() as may, LocalGia() as khac:
        ds = bo.phat_hien(cau_hinh(may))
        so_luot = len(may.luot)
        gio[0] = 299.999
        assert bo.phat_hien(cau_hinh(may)) is ds
        assert len(may.luot) == so_luot
        khac.tags = [{"name": "model-demo-khac"}]
        assert bo.phat_hien(cau_hinh(khac)).loai == "ollama"
        gio[0] = 300
        may.models = [{"id": "model-demo-moi"}]
        assert bo.phat_hien(cau_hinh(may)).models[0].ma == "model-demo-moi"
        assert len(may.luot) > so_luot


@pytest.mark.parametrize("raw", [b"not-json", b"\xff", b'{"models": {}}',
                                  b'{"models": [null]}', b"x" * 2_000_001,
                                  b"[" * 65 + b"]" * 65],
                         ids=["json_hong", "utf8_hong", "sai_kieu", "muc_hong", "qua_tran", "qua_sau"])
def test_probe_hong_du_phong_api_tiep_theo(raw):
    with LocalGia() as may:
        may.phan_hoi_get["/api/tags"] = (200, raw)
        ds = chon_model.bo_phat_hien.phat_hien(cau_hinh(may))
        assert ds.loai == "openai_compatible"


def test_phat_hien_loi_khong_cache_loi_va_phuc_hoi(tmp_path, monkeypatch):
    with LocalGia() as may:
        for _, duong, _, _ in chon_model.CAC_API:
            may.phan_hoi_get[duong] = (503, b"DEMO loi khong duoc lo")
        assert chon_model.bo_phat_hien.phat_hien(cau_hinh(may)) is None
        kq = hoi(may, tmp_path, monkeypatch)
        assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
        assert kq["loi"]["thu_lai_duoc"] and may.so_luot_hoi == 0
        assert "DEMO loi" not in str(kq)
        may.phan_hoi_get.clear()
        assert hoi(may, tmp_path, monkeypatch)["trang_thai"] == "XONG"


@pytest.mark.parametrize("url", ["http://8.8.8.8:12345", "http://demo.invalid:12345"])
def test_phat_hien_url_bi_chan_tra_none(url):
    assert chon_model.bo_phat_hien.phat_hien({"url": url, "timeout_giay": 1}) is None


QUY_TAC = [
    {"mau_ma_prompt": "m4.*", "uu_tien": "model-demo-b", "du_phong": ["model-demo-c", "model-demo-a"]},
    {"mau_ma_prompt": "*", "uu_tien": "model-demo-a", "du_phong": []},
]


@pytest.mark.parametrize("model,ma_prompt,quy_tac,co_mat,chon,ly_do", [
    ("model-demo-c", "m4.hoi", QUY_TAC, "abc", "c", "model_uu_tien"),
    ("model-demo-mat", "m4.hoi", QUY_TAC, "abc", "b", "quy_tac_ma_prompt"),
    (None, "m4.hoi", QUY_TAC, "ac", "c", "du_phong_quy_tac_ma_prompt"),
    (None, "m4.hoi", QUY_TAC, "a", "a", "du_phong_quy_tac_ma_prompt"),
    (None, "m5.hoi", QUY_TAC, "abc", "a", "quy_tac_ma_prompt"),
    (None, "m5.hoi", QUY_TAC[:1], "cab", "c", "model_dau_tien_kha_dung"),
    (None, "m4.hoi", QUY_TAC, "d", "d", "model_dau_tien_kha_dung"),
    (None, "m4.hoi", [QUY_TAC[1], QUY_TAC[0]], "abc", "a", "quy_tac_ma_prompt"),
])
def test_chon_dung_thu_tu_va_ghi_ly_do(model, ma_prompt, quy_tac, co_mat, chon, ly_do,
                                      tmp_path, monkeypatch):
    with LocalGia() as may:
        may.models = [{"id": "model-demo-" + ma} for ma in co_mat]
        kq = hoi(may, tmp_path, monkeypatch, quy_tac=quy_tac, model=model, ma_prompt=ma_prompt)
        assert kq["trang_thai"] == "XONG"
        truong = kq["ket_qua"]["truong"]
        assert (truong["model"], truong["ly_do_chon_model"]) == ("model-demo-" + chon, ly_do)
        assert may.yeu_cau[0]["model"] == truong["model"]


@pytest.mark.parametrize("nguon", ["ollama", "lm_studio", "openai_compatible"])
def test_model_bien_mat_giua_hai_luot_chon_du_phong_khong_cho_het_ttl(nguon, tmp_path, monkeypatch):
    with LocalGia() as may:
        if nguon == "ollama":
            may.tags = [{"name": "model-demo-b"}, {"name": "model-demo-c"}]
            cac_model = may.tags
        elif nguon == "lm_studio":
            may.native_v1 = [{"key": "model-demo-b"}, {"key": "model-demo-c"}]
            cac_model = may.native_v1
        else:
            may.models = [{"id": "model-demo-b"}, {"id": "model-demo-c"}]
            cac_model = may.models
        assert hoi(may, tmp_path, monkeypatch, quy_tac=QUY_TAC)["ket_qua"]["truong"]["model"] == "model-demo-b"
        cac_model.pop(0)
        kq = hoi(may, tmp_path, monkeypatch, quy_tac=QUY_TAC, model="model-demo-b")
        assert kq["ket_qua"]["truong"]["model"] == "model-demo-c"
        assert kq["ket_qua"]["truong"]["ly_do_chon_model"] == "du_phong_quy_tac_ma_prompt"
        cac_model.clear()
        kq = hoi(may, tmp_path, monkeypatch, quy_tac=QUY_TAC)
        assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
        assert may.so_luot_hoi == 2


def test_loai_bo_remote_embedding_chua_tai_va_khong_doan_tu_ten(tmp_path, monkeypatch):
    with LocalGia() as may:
        may.native_v1 = [
            {"key": "model-demo-remote", "remote_host": "demo.invalid"},
            {"key": "model-demo-embed", "type": "embedding"},
            {"key": "model-demo-unloaded", "loaded_instances": []},
            {"key": "model-demo-cu", "state": "not-loaded"},
            {"key": "ollama/demo-khac", "loaded_instances": [{"id": "demo"}]},
        ]
        kq = hoi(may, tmp_path, monkeypatch, model="model-demo-remote")
        assert kq["ket_qua"]["truong"]["model"] == "ollama/demo-khac"
        assert chon_model.bo_phat_hien.phat_hien(cau_hinh(may)).loai == "lm_studio"


def test_huy_discovery_khong_bi_nuot():
    def huy():
        raise ViecDaHuy()

    with LocalGia() as may:
        with pytest.raises(ViecDaHuy):
            chon_model.bo_phat_hien.phat_hien(cau_hinh(may), kiem_huy=huy)
        assert not may.luot


def test_hai_ma_prompt_khong_doi_cau_hinh_chung():
    with LocalGia() as may:
        may.models = [{"id": "model-demo-a"}, {"id": "model-demo-b"}]
        ch = {"local_ai": cau_hinh(may), "quy_tac_model": QUY_TAC}
        for ma, model in [("m4.hoi", "model-demo-b"), ("m5.hoi", "model-demo-a"), ("m4.hoi", "model-demo-b")]:
            yc = YeuCauAI("DEMO", "DEMO", ma, "1")
            assert chon_model.chon_model(yc, ch)[0] == model
        assert ch["quy_tac_model"] == QUY_TAC
        assert "model" not in ch["local_ai"]


def test_model_mat_sau_chon_truoc_post_khong_gui_noi_dung(tmp_path, monkeypatch):
    with LocalGia() as may:
        so_get = []

        def bien_mat(phuong_thuc, duong):
            if phuong_thuc == "GET" and duong == "/v1/models":
                so_get.append(1)
                if len(so_get) == 3:  # Discovery, kiểm để chọn, rồi kiểm ngay trước POST.
                    may.models.clear()

        may.khi_nhan = bien_mat
        kq = hoi(may, tmp_path, monkeypatch)
        assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
        assert may.so_luot_hoi == 0


def test_doi_loai_api_truoc_ttl_va_khong_gia_han_cache_khi_kiem_trang_thai():
    gio = [0]
    bo = chon_model.BoPhatHienModel(dong_ho=lambda: gio[0])
    with LocalGia() as may:
        may.tags = [{"name": "model-demo-cu"}]
        assert bo.phat_hien(cau_hinh(may)).loai == "ollama"
        gio[0] = 200
        bo.kha_dung_hien_tai(cau_hinh(may))
        assert bo._dem[may.url][0] == 0
        may.tags = None
        may.native_v0 = [{"id": "model-demo-moi", "type": "llm", "state": "loaded"}]
        moi = bo.kha_dung_hien_tai(cau_hinh(may))
        assert moi.loai == "lm_studio" and moi.models[0].ma == "model-demo-moi"


def test_native_rong_khong_quay_sang_compatible_co_remote(tmp_path, monkeypatch):
    with LocalGia() as may:
        may.tags = []
        kq = hoi(may, tmp_path, monkeypatch)
        assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
        assert all(duong == "/api/tags" for _, duong in may.luot)
        assert may.so_luot_hoi == 0


def test_model_trung_metadata_remote_khong_duoc_bo_qua(tmp_path, monkeypatch):
    with LocalGia() as may:
        may.models = [{"id": "model-demo"}, {"id": "model-demo", "remote_model": "demo"}]
        kq = hoi(may, tmp_path, monkeypatch)
        assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
        assert may.so_luot_hoi == 0


@pytest.mark.parametrize("duong", ["/api/tags", "/api/v1/models", "/api/v0/models"])
def test_probe_native_khong_theo_redirect(duong, tmp_path, monkeypatch):
    with LocalGia() as may:
        may.chuyen_huong = (duong, 302)
        # Các probe tiếp theo dùng cùng IP/cổng, không chuyển sang đích redirect.
        assert hoi(may, tmp_path, monkeypatch)["trang_thai"] == "XONG"
        assert all(p in {api[1] for api in chon_model.CAC_API} | {"/v1/chat/completions"}
                   for _, p in may.luot)
