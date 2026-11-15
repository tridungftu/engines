"""AI-6: Cloud giả hoàn toàn trong RAM; không gọi Cloud hoặc Local thật."""
import ast
import builtins
from copy import deepcopy
import io
import json
from pathlib import Path
import socket

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu, ViecDaHuy

from e_hoi_ai import nha_cung_cap as ncc
from e_hoi_ai.cloud import hoi_cloud
from e_hoi_ai.cong_ai import CongAI, NhaCungCapLocal
from e_hoi_ai.khuon_json import json_chuan

VAN_BAN = "DEMO: [[CT-0001]] ký hợp đồng [[HD-0001]]."
PHONG_BI = {"loai": "van_ban_da_che", "van_ban_da_che": {
    "phien_ban": 1, "van_ban": VAN_BAN, "ma_yeu_cau": "mask-DEMO-noi-bo",
    "con_sot": [], "kiem_tien_ngay": True,
    "chuyen_tiep": {"noi_bo": "DEMO không gửi", "long": {"danh_sach": [1, True, None]}}}}
TRA_LOI = {"truong": [{"gia_tri": "[[CT-0001]]", "trich_dan": VAN_BAN}]}
THAM_SO = {"model": "model-demo", "ma_prompt": "demo.hoi", "phien_ban_prompt": "1",
           "phien_ban_engine": "0.4.0"}
GUI_JSON_THAT = ncc._gui_json


class CloudGia:
    def __init__(self, loai):
        self.loai, self.luot = loai, []
        self.text = json.dumps(TRA_LOI, ensure_ascii=False)
        self.sua = {}

    def __call__(self, host, duong, headers, body, timeout):
        self.luot.append(deepcopy((host, duong, headers, body, timeout)))
        if self.loai == "anthropic":
            return {"content": [{"type": "text", "text": self.text}], "stop_reason": "end_turn", **self.sua}
        return {"choices": [{"message": {"content": self.text}, "finish_reason": "stop"}], **self.sua}


@pytest.fixture(autouse=True)
def cam_mang(monkeypatch):
    def cam(*args, **kwargs):
        raise AssertionError("AI-6 chỉ được kiểm bằng Cloud giả trong bộ nhớ.")
    monkeypatch.setattr(socket.socket, "connect", cam)
    monkeypatch.setattr(socket, "getaddrinfo", cam)
    monkeypatch.setattr(ncc, "_gui_json", cam)


def tao(loai="openai"):
    gia = CloudGia(loai)
    # Giá trị giả, không có khả năng xác thực; chỉ tồn tại trong RAM của test.
    provider = ncc.NhaCungCapCloud(loai, "DEMO-KHONG-LA-KHOA", gui_json=gia)
    return provider, gia


def test_co_tat_cung_va_khong_co_cloud_trong_cong_mac_dinh():
    assert ncc.BAT_CLOUD is False
    cay = ast.parse(Path(ncc.__file__).read_text(encoding="utf-8"))
    gan = [n for n in ast.walk(cay) if isinstance(n, ast.Assign)
           and any(isinstance(t, ast.Name) and t.id == "BAT_CLOUD" for t in n.targets)]
    assert len(gan) == 1 and isinstance(gan[0].value, ast.Constant) and gan[0].value.value is False
    cong = CongAI()
    assert set(cong.nha_cung_cap) == {"local"}
    assert isinstance(cong.nha_cung_cap["local"], NhaCungCapLocal)


@pytest.mark.parametrize("loai", ["anthropic", "openai"])
def test_khoa_chan_ca_ham_va_provider_khi_chua_bat(loai, monkeypatch):
    monkeypatch.setenv("BAT_CLOUD", "true")
    monkeypatch.setenv("KTT_ENGINE_CLOUD", "true")
    provider, gia = tao(loai)
    for goi in (lambda: hoi_cloud(PHONG_BI, nha_cung_cap=provider, **THAM_SO),
                lambda: provider.hoi(PHONG_BI, model="model-demo")):
        with pytest.raises(LoiNghiepVu) as loi:
            goi()
        assert loi.value.ma == "CLOUD_DANG_TAT"
    assert not gia.luot


@pytest.mark.parametrize("loai", ["anthropic", "openai"])
def test_chi_gui_noi_dung_da_che_va_chuyen_ma_ve_noi_bo(loai, monkeypatch, capsys):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)  # Chỉ trong test, transport giả trong RAM.
    provider, gia = tao(loai)
    vao = deepcopy(PHONG_BI)
    vao["van_ban_da_che"]["chuyen_tiep"]["ma_yeu_cau"] = "DEMO-ma-cu"
    truoc = json_chuan(vao)
    ra = hoi_cloud(vao, nha_cung_cap=provider, **THAM_SO)["tra_loi_ai"]
    assert json_chuan(vao) == truoc
    assert ra["nha_cung_cap"] == "cloud" and ra["trang_thai"] == "co_can_cu"
    assert ra["tra_loi"] == "[[CT-0001]]" and ra["kiem_trich_dan"]["dat"]
    assert ra["chuyen_tiep"] == {**vao["van_ban_da_che"]["chuyen_tiep"], "ma_yeu_cau": "mask-DEMO-noi-bo"}
    ra["chuyen_tiep"]["long"]["danh_sach"].append("DEMO")
    assert json_chuan(vao) == truoc
    assert len(gia.luot) == 1
    host, duong, headers, body, timeout = gia.luot[0]
    assert body["messages"][-1] == {"role": "user", "content": VAN_BAN}
    serialized = json.dumps(gia.luot, ensure_ascii=False)
    for rieng in ("mask-DEMO-noi-bo", "DEMO-ma-cu", "DEMO không gửi", "chuyen_tiep", "ma_yeu_cau", "demo.hoi"):
        assert rieng not in serialized
    if loai == "anthropic":
        assert (host, duong) == ("api.anthropic.com", "/v1/messages")
        assert headers["x-api-key"] == "DEMO-KHONG-LA-KHOA"
        assert body["max_tokens"] == 4096 and body["system"] == ncc.HE_THONG
    else:
        assert (host, duong) == ("api.openai.com", "/v1/chat/completions")
        assert headers["Authorization"] == "Bearer DEMO-KHONG-LA-KHOA"
        assert body["max_completion_tokens"] == 4096
    assert timeout == 60
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("dau_vao", [None, "DEMO chưa che", {}, {"loai": "van_ban", "van_ban": VAN_BAN},
                                     {"loai": "van_ban_da_che", "van_ban_da_che": VAN_BAN}])
def test_tu_choi_moi_loai_chua_che(dau_vao, monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao()
    with pytest.raises(LoiNghiepVu) as loi:
        hoi_cloud(dau_vao, nha_cung_cap=provider, **THAM_SO)
    assert loi.value.ma == "VAN_BAN_DA_CHE_KHONG_HOP_LE"
    assert not gia.luot


@pytest.mark.parametrize("truong,gia_tri,ma", [
    ("con_sot", ["DEMO còn sót"], "MASK_CHUA_AN_TOAN"),
    ("con_sot", None, "MASK_CHUA_AN_TOAN"), ("con_sot", {}, "MASK_CHUA_AN_TOAN"),
    ("con_sot", "", "MASK_CHUA_AN_TOAN"), ("con_sot", False, "MASK_CHUA_AN_TOAN"),
    ("kiem_tien_ngay", False, "MASK_CHUA_AN_TOAN"), ("kiem_tien_ngay", 1, "MASK_CHUA_AN_TOAN"),
    ("kiem_tien_ngay", "true", "MASK_CHUA_AN_TOAN"), ("kiem_tien_ngay", None, "MASK_CHUA_AN_TOAN"),
    ("phien_ban", True, "VAN_BAN_DA_CHE_KHONG_HOP_LE"),
    ("phien_ban", 2, "VAN_BAN_DA_CHE_KHONG_HOP_LE"),
    ("van_ban", " ", "VAN_BAN_DA_CHE_KHONG_HOP_LE"),
    ("van_ban", "DEMO mask-DEMO-noi-bo", "MA_YEU_CAU_TRONG_NOI_DUNG"),
    ("van_ban", "x" * 500001, "VUOT_GIOI_HAN"),
    ("ma_yeu_cau", "", "VAN_BAN_DA_CHE_KHONG_HOP_LE"),
    ("chuyen_tiep", [], "VAN_BAN_DA_CHE_KHONG_HOP_LE"),
    ("chuyen_tiep", {"DEMO": "ấ" * 22000}, "VUOT_GIOI_HAN"),
], ids=["con-sot-co-muc", "con-sot-null", "con-sot-object", "con-sot-chuoi", "con-sot-bool",
        "kiem-false", "kiem-so", "kiem-chuoi", "kiem-null", "phien-ban-bool", "phien-ban-khac",
        "van-ban-rong", "ma-trong-noi-dung", "qua-tran-van-ban", "ma-rong", "chuyen-sai-kieu", "qua-tran-byte"])
def test_chan_fail_closed_truoc_provider(truong, gia_tri, ma, monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao()
    vao = deepcopy(PHONG_BI)
    vao["van_ban_da_che"][truong] = gia_tri
    for goi in (lambda: hoi_cloud(vao, nha_cung_cap=provider, **THAM_SO),
                lambda: provider.hoi(vao, model="model-demo")):
        with pytest.raises(LoiNghiepVu) as loi:
            goi()
        assert loi.value.ma == ma
    assert not gia.luot


@pytest.mark.parametrize("truong", list(PHONG_BI["van_ban_da_che"]))
def test_thieu_truong_bat_buoc_bi_chan(truong, monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao()
    vao = deepcopy(PHONG_BI)
    del vao["van_ban_da_che"][truong]
    with pytest.raises(LoiNghiepVu):
        hoi_cloud(vao, nha_cung_cap=provider, **THAM_SO)
    assert not gia.luot


def test_khong_doc_env_tep_hoac_dia_khi_khoi_tao_va_goi(monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    def cam(*args, **kwargs):
        raise AssertionError("Provider không được đọc env/tệp/đĩa.")
    import os
    with monkeypatch.context() as m:
        m.setattr(os, "getenv", cam)
        m.setattr(os, "environ", None)
        m.setattr(builtins, "open", cam)
        m.setattr(io, "open", cam)
        for loai in ("anthropic", "openai"):
            provider, gia = tao(loai)
            assert hoi_cloud(PHONG_BI, nha_cung_cap=provider, **THAM_SO)["loai"] == "tra_loi_ai"
            assert len(gia.luot) == 1


@pytest.mark.parametrize("loai", ["anthropic", "openai"])
@pytest.mark.parametrize("text", ["DEMO không có JSON", '{"truong": []}',
    '{"truong": [{"gia_tri":"DEMO bịa", "trich_dan":"DEMO bịa"}]}'])
def test_hau_kiem_cloud_khong_bao_co_can_cu_gia(loai, text, monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao(loai)
    gia.text = text
    ra = hoi_cloud(PHONG_BI, nha_cung_cap=provider, **THAM_SO)["tra_loi_ai"]
    assert ra["trang_thai"] == "khong_thay_can_cu"
    assert ra["tra_loi"] == "không thấy căn cứ"


@pytest.mark.parametrize("loai,sua", [("anthropic", {"stop_reason": "max_tokens"}),
    ("anthropic", {"stop_reason": "refusal"}), ("anthropic", {"content": []}),
    ("openai", {"choices": []}),
    ("openai", {"choices": [{"message": {"content": "DEMO"}, "finish_reason": "length"}]})])
def test_phan_hoi_thieu_bi_tu_choi_khong_cat_ngam(loai, sua, monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao(loai)
    gia.sua = sua
    with pytest.raises(LoiNghiepVu) as loi:
        hoi_cloud(PHONG_BI, nha_cung_cap=provider, **THAM_SO)
    assert loi.value.ma == "CLOUD_PHAN_HOI_LOI"


def test_nguon_chua_tra_phai_chua_ro_va_khong_retry(monkeypatch, capsys):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    luot = []
    def mat_phan_hoi(*args):
        luot.append(1)
        raise TimeoutError("DEMO lỗi transport chứa nội dung không được phản chiếu")
    provider = ncc.NhaCungCapCloud("openai", "DEMO-KHONG-LA-KHOA", gui_json=mat_phan_hoi)
    with pytest.raises(ChuaRo) as loi:
        hoi_cloud(PHONG_BI, nha_cung_cap=provider, **THAM_SO)
    assert len(luot) == 1
    assert "DEMO" not in str(loi.value)
    assert capsys.readouterr() == ("", "")


def test_huy_truoc_goi_khong_cham_cloud(monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao()
    def huy():
        raise ViecDaHuy()
    with pytest.raises(ViecDaHuy):
        hoi_cloud(PHONG_BI, nha_cung_cap=provider, kiem_huy=huy, **THAM_SO)
    assert not gia.luot


@pytest.mark.parametrize("loi,ma", [("ket-noi", "CLOUD_KHONG_SAN_SANG"),
    ("mat-phan-hoi", "CHUA_RO"), ("da-nhan", "CHUA_RO"),
    ("redirect", "CLOUD_TU_CHOI"), ("http", "CLOUD_TU_CHOI"),
    ("json", "CLOUD_PHAN_HOI_LOI"), ("qua-tran", "VUOT_GIOI_HAN"), ("khong-loi", None)])
def test_transport_https_chi_bang_doi_tuong_gia_trong_ram(loi, ma, monkeypatch):
    class KetNoiGia:
        def __init__(self, host, timeout):
            self.dong, self.luot = False, []
            assert host == "api.openai.com" and timeout == 60

        def connect(self):
            if loi == "ket-noi":
                raise OSError("DEMO")

        def request(self, method, duong, **kwargs):
            self.luot.append((method, duong))
            assert method == "POST" and duong == "/v1/chat/completions"

        def getresponse(self):
            if loi == "mat-phan-hoi":
                raise TimeoutError("DEMO")
            return self

        @property
        def status(self):
            return {"redirect": 302, "http": 500, "da-nhan": 202}.get(loi, 200)

        def read(self, tran):
            if loi == "qua-tran":
                return b"x" * tran
            return b"DEMO" if loi == "json" else b'{"DEMO": true}'

        def close(self):
            self.dong = True

    ket_noi = KetNoiGia("api.openai.com", 60)
    monkeypatch.setattr(ncc.http.client, "HTTPSConnection", lambda *a, **k: ket_noi)
    goi = lambda: GUI_JSON_THAT("api.openai.com", "/v1/chat/completions", {}, {"DEMO": True}, 60)
    if ma == "CHUA_RO":
        with pytest.raises(ChuaRo):
            goi()
    elif ma:
        with pytest.raises(LoiNghiepVu) as exc:
            goi()
        assert exc.value.ma == ma
    else:
        assert goi() == {"DEMO": True}
    assert ket_noi.dong
    assert len(ket_noi.luot) == (0 if loi == "ket-noi" else 1)


def test_tran_chuyen_tiep_tinh_ca_ma_mo_che_va_khong_cat(monkeypatch):
    monkeypatch.setattr(ncc, "BAT_CLOUD", True)
    provider, gia = tao()
    vao = deepcopy(PHONG_BI)
    data = vao["van_ban_da_che"]
    chuyen = {"DEMO": "", "ma_yeu_cau": data["ma_yeu_cau"]}
    chuyen["DEMO"] = "x" * (65536 - len(json_chuan(chuyen)))
    data["chuyen_tiep"] = chuyen
    ra = hoi_cloud(vao, nha_cung_cap=provider, **THAM_SO)["tra_loi_ai"]
    assert len(json_chuan(ra["chuyen_tiep"])) == 65536
    data["chuyen_tiep"]["DEMO"] += "x"
    with pytest.raises(LoiNghiepVu) as exc:
        hoi_cloud(vao, nha_cung_cap=provider, **THAM_SO)
    assert exc.value.ma == "VUOT_GIOI_HAN" and len(gia.luot) == 1
