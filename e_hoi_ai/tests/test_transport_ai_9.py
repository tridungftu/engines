"""Hồi quy cả ba handler: hoàn tất, mạng Local và trạng thái gửi POST."""
import threading

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo

from e_hoi_ai import ai_cuc_bo, chay
from e_hoi_ai.nha_cung_cap import NhaCungCapLocal
from local_gia import nap_cau_hinh
from mask_gia import phan_hoi_demo
from test_hoi_mask_ai_9 import hoi as hoi_mask
from test_hoi_tai_lieu import hoi as hoi_tai_lieu, khong_mang_ngoai_va_khong_cloud, local
from test_hoi_yeu_cau import hoi as hoi_yeu_cau, PHAN_HOI


def goi_handler(local, loai):
    if loai == "mask":
        local.tra_loi = phan_hoi_demo()
        return hoi_mask()
    if loai == "yeu_cau":
        local.tra_loi = PHAN_HOI
        return hoi_yeu_cau()
    return hoi_tai_lieu()


@pytest.mark.parametrize("loai", ["tai_lieu", "yeu_cau", "mask"])
@pytest.mark.parametrize("tinh_huong", ["timeout_sau_post", "202", "mat_ket_noi", "cat_than"])
def test_sau_post_chua_ro_khong_retry_fallback_hoac_rong(local, loai, tinh_huong):
    nap_cau_hinh(local.url, thoi_han=0.03)
    cho = threading.Event()
    if tinh_huong == "202":
        local.ma_http = 202
    elif tinh_huong == "mat_ket_noi":
        # Fixture đóng socket có chủ đích, không in traceback server.
        local.cat_sau_post = True
    elif tinh_huong == "cat_than":
        local.cat_than_sau_post = True
    else:
        local.khi_nhan = lambda m, p: cho.wait(0.1) if m == "POST" else None
    kq = goi_handler(local, loai)
    assert kq["trang_thai"] == "CHUA_RO" and kq["ket_qua"] is None, kq
    assert kq["ma_tuong_quan"].startswith("local-")
    assert "DEMO-mask" not in kq["ma_tuong_quan"] and local.so_luot_hoi == 1


@pytest.mark.parametrize("loai", ["tai_lieu", "yeu_cau", "mask"])
def test_timeout_metadata_truoc_post_la_loi_thu_lai_duoc(local, loai):
    nap_cau_hinh(local.url, thoi_han=0.01)
    cho = threading.Event()
    local.khi_nhan = lambda m, p: cho.wait(0.04) if m == "GET" else None
    kq = goi_handler(local, loai)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert kq["loi"]["thu_lai_duoc"] and local.so_luot_hoi == 0


@pytest.mark.parametrize("loai", ["tai_lieu", "yeu_cau", "mask"])
@pytest.mark.parametrize("raw", [
    b'{"choices":[{"message":{"content":"{}"}}]}',
    b'{"choices":[{"message":{"content":"{}"},"finish_reason":"length"}]}',
    b'{"choices":[{"message":{"content":"{}"},"finish_reason":"content_filter"}]}',
    b'{"choices":[{"message":{"content":"{}"},"finish_reason":null}]}',
    b'{"choices":[{"message":{"content":"{}"},"finish_reason":"stop"}],"nha_cung_cap":"cloud"}',
    b'{"choices":[{"message":{"content":"{}"},"finish_reason":"stop"}],"remote_host":"DEMO"}',
    b'{"choices":[],"choices":[{"message":{"content":"{}"},"finish_reason":"stop"}]}',
])
def test_thieu_hoan_tat_hoac_nguon_gia_la_loi_dong(local, loai, raw):
    local.phan_hoi_tho = raw
    kq = goi_handler(local, loai)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert local.so_luot_hoi == 1


@pytest.mark.parametrize("done,reason", [(False, "stop"), (1, "stop"), (True, "length"),
                                        (True, None), (None, "stop"), (True, "load")])
@pytest.mark.parametrize("loai", ["yeu_cau", "mask"])
def test_ollama_chi_nhan_done_true_va_stop(local, loai, done, reason):
    local.tags = [{"name": "model-demo"}]
    local.sua_phong_bi = {"done": done, "done_reason": reason}
    kq = goi_handler(local, loai)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and local.so_luot_hoi == 1


@pytest.mark.parametrize("metadata", [{"id": "model-demo", "provider": "cloud"},
    {"id": "model-demo", "nha_cung_cap": "remote"}, {"id": "model-demo", "local": False},
    {"id": "model-demo", "is_cloud": True}, {"id": "model-demo", "remote_model": "DEMO"}])
def test_metadata_remote_cloud_khong_gui_goc(local, metadata):
    local.models = [metadata]
    kq = goi_handler(local, "mask")
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and local.so_luot_hoi == 0


@pytest.mark.parametrize("context", [None, 8192, True, 0, 1.0, "65536"])
def test_thieu_hoac_vuot_suc_chua_khong_gui_goc(local, context):
    local.models = [{"id": "model-demo", "context_length": context}]
    kq = goi_handler(local, "mask")
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and local.so_luot_hoi == 0
    assert kq["loi"]["ma"] in {"LOCAL_AI_KHONG_SAN_SANG", "VUOT_GIOI_HAN"}


def test_khong_lay_max_context_lam_suc_chua_thuc(local):
    local.models = [{"id": "model-demo", "max_context_length": 1_000_000}]
    assert goi_handler(local, "mask")["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert local.so_luot_hoi == 0


@pytest.mark.parametrize("sua", [{"remote_host": "cloud.demo.invalid"}, {"type": "embedding"},
                               {"state": "not-loaded"}, {"loaded_instances": []}])
def test_metadata_doi_trong_luot_kiem_budget_khong_gui_goc(local, sua):
    dem = []
    def doi(m, p):
        if m == "GET" and p == "/v1/models":
            dem.append(1)
            if len(dem) == 4:
                local.models[0].update(sua)
    local.khi_nhan = doi
    assert goi_handler(local, "mask")["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert len(dem) == 4 and local.so_luot_hoi == 0


@pytest.mark.parametrize("api", ["native_v1", "native_v0"])
def test_ai_9_lm_studio_dung_catalog_va_context(local, api):
    setattr(local, api, [{"key" if api == "native_v1" else "id": "model-demo", "context_length": 65536}])
    assert goi_handler(local, "mask")["trang_thai"] == "XONG"
    assert local.luot[-1] == ("POST", "/v1/chat/completions")


def test_ollama_chua_tai_context_thi_tu_choi(local):
    local.tags = [{"name": "model-demo"}]
    local.dang_chay = []
    assert goi_handler(local, "mask")["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert local.so_luot_hoi == 0


def test_budget_byte_prompt_khong_cat_ngam(local):
    from mask_gia import bam, yeu_cau_demo
    yc = yeu_cau_demo()
    yc["prompt"] = "D" * 65536
    yc["chuyen_tiep"]["mask_2c"]["bam_prompt"] = bam(yc["prompt"].encode())
    kq = hoi_mask(yc)
    assert kq["loi"]["ma"] == "VUOT_GIOI_HAN" and local.so_luot_hoi == 0


def test_context_overflow_da_tra_loi_khong_fallback(local):
    local.ma_http = 400
    local.phan_hoi_tho = b'{"error":"DEMO context overflow"}'
    kq = goi_handler(local, "mask")
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and local.so_luot_hoi == 1


@pytest.mark.parametrize("url", ["http://cloud.demo.invalid:12345", "http://8.8.8.8:12345",
    "https://127.0.0.1:12345", "http://127.0.0.1:12345/v1?proxy=DEMO"])
def test_url_dns_public_va_proxy_tu_choi_truoc_post(local, url):
    nap_cau_hinh(url)
    kq = goi_handler(local, "mask")
    assert kq["trang_thai"] == "LOI" and local.so_luot_hoi == 0


@pytest.mark.parametrize("duong", ["/api/tags", "/v1/chat/completions"])
def test_redirect_khong_the_gui_lai_goc(local, duong):
    local.chuyen_huong = (duong, 307)
    if duong == "/api/tags":
        # Discovery có thể tìm API khác, nhưng không được follow URL trong Location.
        local.models = []
    kq = goi_handler(local, "mask")
    assert kq["trang_thai"] == "LOI" and local.so_luot_hoi <= 1


def test_proxy_env_khong_tac_dong_transport(local, monkeypatch):
    for ten in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        monkeypatch.setenv(ten, "http://cloud.demo.invalid:12345")
    monkeypatch.setenv("NO_PROXY", "")
    assert goi_handler(local, "mask")["trang_thai"] == "XONG"


def test_connect_timeout_chac_chan_chua_gui_la_local_khong_san_sang(local, monkeypatch):
    def timeout(self):
        raise TimeoutError("DEMO chi tiet khong duoc lo")
    monkeypatch.setattr(ai_cuc_bo._KetNoiIP, "connect", timeout)
    with pytest.raises(ai_cuc_bo.LocalAIKhongSanSang):
        ai_cuc_bo._gui_post(local.url + "/v1/chat/completions", None, 1, b'{}', lambda: None)
    assert local.so_luot_hoi == 0


def test_khong_biet_request_da_gui_bao_nhieu_thi_chua_ro(local, monkeypatch):
    def request(self, *args, **kwargs):
        raise ConnectionResetError("DEMO khong biet byte da gui")
    monkeypatch.setattr(ai_cuc_bo._KetNoiIP, "request", request)
    with pytest.raises(ChuaRo) as exc:
        ai_cuc_bo._gui_post(local.url + "/v1/chat/completions", None, 1, b'{}', lambda: None)
    assert exc.value.ma_tuong_quan.startswith("local-") and local.so_luot_hoi == 0


def test_loi_don_socket_khong_che_mat_chua_ro(local, monkeypatch):
    def request(self, *args, **kwargs):
        raise ConnectionResetError("DEMO")
    dong = ai_cuc_bo._KetNoiIP.close
    def close(self):
        dong(self)
        raise OSError("DEMO lỗi dọn socket")
    monkeypatch.setattr(ai_cuc_bo._KetNoiIP, "request", request)
    monkeypatch.setattr(ai_cuc_bo._KetNoiIP, "close", close)
    with pytest.raises(ChuaRo):
        ai_cuc_bo._gui_post(local.url + "/v1/chat/completions", None, 1, b'{}', lambda: None)


def test_provider_local_truyen_nguyen_chua_ro(monkeypatch):
    exc = ChuaRo("DEMO-tuong-quan-local")
    def chua_ro(*args, **kwargs):
        raise exc
    monkeypatch.setattr(ai_cuc_bo, "hoi_local", chua_ro)
    with pytest.raises(ChuaRo) as kq:
        NhaCungCapLocal().hoi({}, "DEMO", "DEMO", kiem_huy=lambda: None)
    assert kq.value is exc


def test_response_vuot_byte_khong_cat_lay_json_dau(local):
    local.phan_hoi_tho = b'{"choices":[]}' + b' ' * 2_000_001
    kq = goi_handler(local, "mask")
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None and local.so_luot_hoi == 1


@pytest.mark.parametrize("phan_tram", [10, 90])
def test_mat_lease_khong_nop_hoac_ket_thuc(local, monkeypatch, phan_tram):
    from kho_tri_thuc_sdk.engine import LoiDuongTruyen
    from kho_tri_thuc_sdk.thu import CoreGia
    core = CoreGia()
    goc = core._tien_do
    def mat_lease(ma, viec_id, pt, cau):
        if pt == phan_tram:
            raise LoiDuongTruyen("MAT_LEASE", http_status=409)
        return goc(ma, viec_id, pt, cau)
    monkeypatch.setattr(core, "_tien_do", mat_lease)
    local.tra_loi = phan_hoi_demo()
    kq = hoi_mask(core=core)
    assert kq["ket_qua"] is None and core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 0
    assert local.so_luot_hoi == (1 if phan_tram == 90 else 0)
