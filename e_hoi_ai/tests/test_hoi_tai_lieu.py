"""Đã kiểm bằng Core giả (CoreGia) và HTTP Local giả; không cần mạng ngoài."""
import ipaddress
import json
import socket
import threading

import pytest
from kho_tri_thuc_sdk.engine import Viec
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoi_ai import ai_cuc_bo, chay
from e_hoi_ai.nha_cung_cap import NhaCungCapCloud
from e_hoi_ai.cong_ai import CongAI, NhaCungCapLocal, danh_gia
from e_hoi_ai.dto import YeuCauAI
from local_gia import LocalGia, TAI_LIEU, TRA_LOI, TRICH_TIEN, TRICH_NGAY, ghi_cau_hinh

THAM_SO = {"ma_prompt": "demo.hoi", "phien_ban_prompt": "1",
           "prompt": "DEMO: Số tiền và ngày thanh toán là bao nhiêu?"}


class CloudGia:
    def __init__(self):
        self.so_luot = 0

    def hoi(self, *args, **kwargs):
        self.so_luot += 1
        raise AssertionError("Không được gọi provider Cloud trong bản 1.")


@pytest.fixture(autouse=True)
def khong_mang_ngoai_va_khong_cloud(monkeypatch):
    """Provider Cloud có mặt ở seam, được đếm ở mọi đường; chặn cả mạng ngoài/DNS."""
    cloud = CloudGia()
    cham_cloud = []

    def cam_provider_cloud(*args, **kwargs):
        cham_cloud.append(1)
        raise AssertionError("Hai năng lực bản 1 không được chạm NhaCungCapCloud.")

    monkeypatch.setattr(NhaCungCapCloud, "__init__", cam_provider_cloud)
    monkeypatch.setattr(NhaCungCapCloud, "hoi", cam_provider_cloud)
    cong = CongAI(nha_cung_cap={"local": NhaCungCapLocal(), "cloud": cloud})
    monkeypatch.setattr(chay.bo_hoi, "cong_ai", cong)
    ket_noi_goc = socket.socket.connect

    def ket_noi_chi_loopback(self, dia_chi):
        assert ipaddress.ip_address(dia_chi[0]).is_loopback, "Bộ test không được nối mạng ngoài."
        return ket_noi_goc(self, dia_chi)

    def cam_dns(*args, **kwargs):
        raise AssertionError("Local AI không được tra DNS.")

    monkeypatch.setattr(socket.socket, "connect", ket_noi_chi_loopback)
    monkeypatch.setattr(socket, "getaddrinfo", cam_dns)
    yield cloud
    assert cloud.so_luot == 0
    assert cham_cloud == []


@pytest.fixture
def local(tmp_path, monkeypatch):
    with LocalGia() as may:
        tep = ghi_cau_hinh(tmp_path, may.url)
        monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
        yield may


def hoi(*, core=None, tham_so=None, van_ban=TAI_LIEU, loai="van_ban"):
    du_lieu = van_ban if loai == "van_ban" else {"phien_ban": 1, "van_ban": van_ban}
    return (core or CoreGia()).chay_thu(
        chay.app, "ai.hoi_tai_lieu@1", {"loai": loai, loai: du_lieu},
        THAM_SO if tham_so is None else tham_so,
    )


@pytest.mark.parametrize("loai", ["van_ban", "van_ban_tai_lieu"])
def test_hoi_dung_tien_ngay_co_trich_dan_va_tien_do(local, loai):
    kq = hoi(loai=loai)
    assert kq["trang_thai"] == "XONG"
    truong = kq["ket_qua"]["truong"]
    assert truong == {"tra_loi": "1.000.000 VND\n30/10/2026", "co_can_cu": True,
                      "trich_dan": TRICH_TIEN + "\n" + TRICH_NGAY, "model": "model-demo",
                      "ly_do_chon_model": "quy_tac_ma_prompt"}
    assert [m[0] for m in kq["tien_do"]] == [10, 90]
    assert local.so_luot_hoi == 1
    request = local.yeu_cau[0]
    assert request["model"] == "model-demo" and request["temperature"] == 0
    assert request["stream"] is False
    khung = request["messages"][1]["content"]
    assert THAM_SO["prompt"] in khung and TAI_LIEU in khung
    assert "nguyên văn" in khung and "không thấy căn cứ" in khung and "Không bịa" in khung


def test_khong_co_dap_an_trong_tai_lieu(local):
    local.tra_loi = {"truong": []}
    kq = hoi(tham_so={**THAM_SO, "prompt": "DEMO: Ai là người bảo lãnh?"})
    assert kq["trang_thai"] == "XONG"
    assert kq["ket_qua"]["truong"]["co_can_cu"] is False
    assert kq["ket_qua"]["truong"]["tra_loi"] == "không thấy căn cứ"
    assert kq["ket_qua"]["truong"]["trich_dan"] == ""


@pytest.mark.parametrize("phan_hoi,canh_bao", [
    ({"truong": [{"gia_tri": "9.000.000 VND", "trich_dan": "DEMO trả 9.000.000 VND."}]}, "trích dẫn không xuất hiện"),
    ({"truong": [{"gia_tri": "Người bảo lãnh DEMO", "trich_dan": TRICH_TIEN}]}, "không nằm trong trích dẫn"),
    ({"truong": [{"gia_tri": "9.000.000 VND", "trich_dan": TRICH_TIEN}]}, "số liệu"),
    ({"truong": [{"gia_tri": "1.000.000 VND", "trich_dan": ""}]}, "thiếu trích dẫn"),
    ({"truong": [{"gia_tri": "1.000.000 VND", "trich_dan": TRICH_TIEN.replace(" là ", "  là ")}]}, "trích dẫn không xuất hiện"),
    ({"truong": [*TRA_LOI["truong"], {"gia_tri": "DEMO bịa", "trich_dan": "DEMO bịa"}]}, "trích dẫn không xuất hiện"),
    ({"truong": ["DEMO sai kiểu"]}, "không đúng định dạng"),
    ({"truong": [{"gia_tri": " ", "trich_dan": TRICH_TIEN}]}, "không đúng định dạng"),
    ({"truong": "DEMO sai kiểu"}, "không đúng định dạng"),
    ("DEMO trả lời tự do không có trích dẫn", "không đúng định dạng"),
])
def test_ha_ket_qua_sai_khong_phat_hanh_noi_dung_bia(local, phan_hoi, canh_bao):
    local.tra_loi = phan_hoi
    kq = hoi()
    assert kq["trang_thai"] == "XONG"
    truong = kq["ket_qua"]["truong"]
    assert truong["co_can_cu"] is False
    assert truong["tra_loi"].startswith("không thấy căn cứ\nCảnh báo:")
    assert canh_bao in truong["tra_loi"]
    assert "9.000.000" not in truong["tra_loi"]
    assert all(trich in TAI_LIEU for trich in truong["trich_dan"].splitlines())


def test_so_phai_la_token_day_du_trong_nguon():
    yc = YeuCauAI("DEMO có 1000 VND.", "Câu hỏi DEMO", "demo.hoi", "1")
    _, loi = danh_gia({"truong": [{"gia_tri": "100", "trich_dan": "DEMO có 1000 VND."}]}, yc)
    assert "SO_NGOAI_NGUON" in loi


@pytest.mark.parametrize("prompt", ["", " \t\n", None])
def test_prompt_rong_bi_tu_choi_truoc_goi_local(local, prompt):
    kq = hoi(tham_so={**THAM_SO, "prompt": prompt})
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "THIEU_PROMPT"
    assert kq["loi"]["thu_lai_duoc"] is False
    assert kq["ket_qua"] is None
    assert not local.luot


def test_khong_gui_truong_prompt_cung_tra_thieu_prompt(local):
    kq = hoi(tham_so={k: v for k, v in THAM_SO.items() if k != "prompt"})
    assert kq["loi"]["ma"] == "THIEU_PROMPT"
    assert not local.luot


def test_local_tat_loi_thu_lai_duoc_khong_cloud(tmp_path, monkeypatch):
    with LocalGia() as may:
        tep = ghi_cau_hinh(tmp_path, may.url, thoi_han=0.2)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    kq = hoi()
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert kq["loi"]["thu_lai_duoc"] is True
    assert kq["ket_qua"] is None


@pytest.mark.parametrize("metadata", [[], [{"id": "model-demo", "remote_host": "cloud.demo.invalid"}],
                                      [{"id": "model-demo", "remote_model": "DEMO"}],
                                      [{"id": "model-demo", "state": "not-loaded"}]])
def test_model_chua_san_sang_khong_gui_noi_dung(local, metadata):
    local.models = metadata
    kq = hoi()
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"]
    assert local.so_luot_hoi == 0


def test_ollama_remote_bi_chan_du_v1_models_khong_khai(local):
    local.tags = [{"name": "model-demo", "remote_host": "cloud.demo.invalid"}]
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert local.so_luot_hoi == 0


@pytest.mark.parametrize("ma_http", [400, 404, 429, 500, 503])
def test_local_tu_choi_tra_loi_bao_thu_lai_khong_tu_gui_lai(local, ma_http):
    local.ma_http = ma_http
    local.tra_loi = "DEMO nội dung lỗi máy AI không được lộ"
    kq = hoi()
    assert kq["trang_thai"] == "LOI" and kq["loi"]["thu_lai_duoc"]
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG"
    assert "nội dung lỗi" not in str(kq["loi"])
    assert local.so_luot_hoi == 1


@pytest.mark.parametrize("raw", [b"not-json-demo", b'{"choices": []}', b"\xff", b"x" * 2_000_001,
                                  b"[" * 65 + b"]" * 65],
                         ids=["json_hong", "choices_trong", "utf8_hong", "qua_tran", "qua_sau"])
def test_phan_hoi_http_hong_hoac_vuot_tran(local, raw):
    local.phan_hoi_tho = raw
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"]
    assert kq["ket_qua"] is None


def test_timeout_theo_cau_hinh(local, tmp_path, monkeypatch):
    tep = ghi_cau_hinh(tmp_path, local.url, thoi_han=0.02)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    cho = threading.Event()
    local.khi_nhan = lambda phuong_thuc, duong: cho.wait(0.1) if phuong_thuc == "POST" else None
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"]


def test_huy_truoc_goi_ai_khong_gui_yeu_cau(local, monkeypatch):
    core = CoreGia()
    tien_do_goc = core._tien_do

    def huy_ngay_khi_gui_tien_do(ma, viec_id, phan_tram, cau):
        core.huy(viec_id)
        return tien_do_goc(ma, viec_id, phan_tram, cau)

    monkeypatch.setattr(core, "_tien_do", huy_ngay_khi_gui_tien_do)
    kq = hoi(core=core)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert not local.luot and core.so_lan_ghi["ket_qua"] == 0


def test_huy_giua_luot_local_khong_nop_ket_qua(local, monkeypatch):
    core = CoreGia()
    tien_do_goc = core._tien_do
    ma_viec = []

    def ghi_nhan_viec(ma, viec_id, phan_tram, cau):
        ma_viec.append(viec_id)
        return tien_do_goc(ma, viec_id, phan_tram, cau)

    monkeypatch.setattr(core, "_tien_do", ghi_nhan_viec)
    local.khi_nhan = lambda phuong_thuc, duong: core.huy(ma_viec[0]) if phuong_thuc == "POST" else None
    kq = hoi(core=core)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert local.so_luot_hoi == 1 and core.so_lan_ghi["ket_qua"] == 0


def test_goi_kiem_huy_ngay_truoc_goi_ai(local, monkeypatch):
    kiem_goc = Viec.kiem_huy
    so_lan = []

    def kiem(viec):
        so_lan.append(len(local.luot))
        return kiem_goc(viec)

    monkeypatch.setattr(Viec, "kiem_huy", kiem)
    assert hoi()["trang_thai"] == "XONG"
    # Có kiểm trước mạng và sau metadata, trước POST chứa tài liệu.
    assert 0 in so_lan and len(local.luot) - 1 in so_lan


def test_mat_xac_nhan_ket_qua_khong_goi_lai_ai_khong_nop_trung(local):
    core = CoreGia()
    core.gay_mat_xac_nhan("ket_qua")
    kq = hoi(core=core)
    assert kq["trang_thai"] == "XONG"
    assert local.so_luot_hoi == 1
    assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1
    cac_luot = [luot for luot in core.nhat_ky if luot[0] == "ket_qua"]
    assert len(cac_luot) == 2 and len({luot[3] for luot in cac_luot}) == 1


def test_nhat_ky_chi_metadata_khong_noi_dung(local, capsys):
    assert hoi()["trang_thai"] == "XONG"
    out = capsys.readouterr()
    assert out.out == ""
    ban_ghi = json.loads(out.err)
    assert set(ban_ghi) == {"ma_prompt", "phien_ban_prompt", "model", "ly_do_chon", "thoi_gian_ms", "ket_qua_kiem"}
    assert ban_ghi["ma_prompt"] == "demo.hoi" and ban_ghi["phien_ban_prompt"] == "1"
    assert ban_ghi["model"] == "model-demo" and ban_ghi["ly_do_chon"] == "quy_tac_ma_prompt"
    assert ban_ghi["ket_qua_kiem"] == "DAT" and ban_ghi["thoi_gian_ms"] >= 0
    assert all(v not in out.err for v in (THAM_SO["prompt"], TAI_LIEU, "1.000.000", "30/10/2026", local.url))


def test_nhat_ky_ket_qua_kiem_khong_dat(local, capsys):
    local.tra_loi = {"truong": [{"gia_tri": "DEMO bịa", "trich_dan": "DEMO bịa"}]}
    hoi()
    assert json.loads(capsys.readouterr().err)["ket_qua_kiem"] == "KHONG_DAT"


def test_nhat_ky_thieu_prompt_van_co_ma_va_phien_ban(local, capsys):
    hoi(tham_so={**THAM_SO, "prompt": ""})
    ban_ghi = json.loads(capsys.readouterr().err)
    assert ban_ghi["ma_prompt"] == "demo.hoi" and ban_ghi["phien_ban_prompt"] == "1"
    assert ban_ghi["ket_qua_kiem"] == "THIEU_PROMPT"


@pytest.mark.parametrize("model", ["", " \t"])
def test_model_uu_tien_rong_dung_quy_tac(local, model):
    kq = hoi(tham_so={**THAM_SO, "model_uu_tien": model})
    assert kq["ket_qua"]["truong"]["model"] == "model-demo"


def test_model_uu_tien_tham_so_thang_quy_tac(local):
    local.models.append({"id": "model-demo-uu-tien"})
    kq = hoi(tham_so={**THAM_SO, "model_uu_tien": "model-demo-uu-tien"})
    assert kq["ket_qua"]["truong"]["model"] == "model-demo-uu-tien"


def test_khong_co_quy_tac_chon_model_dau_tien_kha_dung(local, tmp_path, monkeypatch):
    tep = ghi_cau_hinh(tmp_path, local.url, quy_tac=[])
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    kq = hoi()
    assert kq["ket_qua"]["truong"]["model"] == "model-demo"
    assert kq["ket_qua"]["truong"]["ly_do_chon_model"] == "model_dau_tien_kha_dung"


@pytest.mark.parametrize("loai", ["van_ban", "van_ban_tai_lieu"])
def test_vuot_tran_tai_lieu_tu_choi_khong_cat_ngam(local, loai):
    kq = hoi(van_ban="D" * 500_001, loai=loai)
    assert kq["loi"]["ma"] == "VUOT_GIOI_HAN" and not local.luot


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:12345", "http://localhost:12345/v1", "http://[::1]:12345/v1/chat/completions",
    "http://10.0.0.1:12345", "http://172.16.0.1:12345", "http://192.168.0.1:12345",
    "http://100.64.0.1:12345", "http://[fd7a:115c:a1e0::1]:12345",
])
def test_chi_chap_nhan_loopback_lan_tailscale(url):
    assert ai_cuc_bo.kiem_url(url).path == "/v1/chat/completions"


@pytest.mark.parametrize("url", [
    "http://ai.demo.invalid:12345", "http://127.0.0.1.demo.invalid:12345", "https://127.0.0.1:12345",
    "http://8.8.8.8:12345", "http://169.254.169.254:12345", "http://[fe80::1]:12345",
    "http://[::ffff:127.0.0.1]:12345", "http://127.0.0.1", "http://127.0.0.1:0",
    "http://demo:demo@127.0.0.1:12345", "http://127.0.0.1:12345/?demo=1",
    "http://127.0.0.1:12345/#demo", "http://127.0.0.1:12345/v1/other",
    "http://127.0.0.1:12345/\n", "http://[::1%25demo]:12345",
])
def test_dia_chi_khong_an_toan_bi_chan_truoc_ket_noi(url):
    with pytest.raises(ai_cuc_bo.LocalAIKhongSanSang):
        ai_cuc_bo.kiem_url(url)


def test_proxy_moi_truong_khong_duoc_su_dung(local, monkeypatch):
    for ten in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
        monkeypatch.setenv(ten, "http://proxy.demo.invalid:12345")
    for ten in ("no_proxy", "NO_PROXY"):
        monkeypatch.setenv(ten, "")
    assert hoi()["trang_thai"] == "XONG" and local.so_luot_hoi == 1


@pytest.mark.parametrize("ma_http", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("duong", ["/v1/models", "/v1/chat/completions"])
def test_khong_theo_redirect_ke_ca_post(local, ma_http, duong):
    local.chuyen_huong = duong, ma_http
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"]
    assert local.so_luot_hoi == (1 if duong.endswith("completions") else 0)
    assert all(p in ("/v1/models", "/api/tags", "/api/v1/models", "/api/v0/models",
                     "/v1/chat/completions") for _, p in local.luot)


def test_dich_tailscale_phai_co_nguon_tailscale(monkeypatch):
    monkeypatch.setattr(ai_cuc_bo, "ip_nguon", lambda host, port: "192.168.0.10")
    with pytest.raises(ai_cuc_bo.LocalAIKhongSanSang):
        ai_cuc_bo.nguon_tailscale("100.64.0.1", 12345)
    monkeypatch.setattr(ai_cuc_bo, "ip_nguon", lambda host, port: "100.64.0.2")
    assert ai_cuc_bo.nguon_tailscale("100.64.0.1", 12345) == "100.64.0.2"


def test_socket_ghim_nguon_tailscale_khong_dns(monkeypatch):
    thao_tac = []

    class SocketGia:
        def settimeout(self, gia_tri):
            thao_tac.append(("timeout", gia_tri))

        def bind(self, dia_chi):
            thao_tac.append(("bind", dia_chi))

        def connect(self, dia_chi):
            thao_tac.append(("connect", dia_chi))

        def close(self):
            pass

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: SocketGia())
    ket_noi = ai_cuc_bo._KetNoiIP("100.64.0.1:12345", nguon="100.64.0.2", timeout=2)
    ket_noi.connect()
    assert thao_tac == [("timeout", 2), ("bind", ("100.64.0.2", 0)), ("connect", ("100.64.0.1", 12345))]
