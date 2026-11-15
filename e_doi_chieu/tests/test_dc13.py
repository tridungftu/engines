"""DC-13: chỉ chạy khô/CoreGia/adapter giả; không kết nối môi trường thật."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

CONG_CU = Path(__file__).resolve().parents[1] / "cong-cu"
spec = importlib.util.spec_from_file_location("thu_dc13", CONG_CU / "thu_doi_chieu_that.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def bo_demo():
    return {"phien_ban": 1, "nhan": "DEMO", "ma_bo": "DEMO-bo", "dap_an_day_du": True, "ca": [{
        "ma": "DEMO-tien", "word": {"tep_id": "DEMO-word", "bam": "sha256:" + "a"*64,
            "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        "scan": {"tep_id": "DEMO-scan", "bam": "sha256:" + "b"*64, "mime": "application/pdf"},
        "so_trang": 1, "so_vung_can_ocr": 1,
        "diem": [{"neo": {"bat_dau": 5, "ket_thuc": 14}, "nghiem_trong": True, "sua_that": True}],
        "vung_sua_tay": [{"trang": 1, "hop": [10, 10, 20, 20]}]}]}


def quan_sat():
    return {"trang_thai": "XONG", "cloud": 0, "so_trang": 1,
            "bam_cau_hinh": "sha256:" + "d"*64,
            "bam_word": "sha256:" + "a"*64, "bam_scan": "sha256:" + "b"*64,
            "diem_day_du": True, "diem": [{"neo": {"bat_dau": 5, "ket_thuc": 14},
                "muc": "nghiem_trong", "an_mac_dinh": False}],
            "tu_abbyy": [{"hop": [1, 2, 3, 4], "nghi_ngo": False}],
            "ocr_vung": [True], "tu_dien": {"bam": "sha256:" + "c"*64, "so_tu_kiem": 1, "so_tu_co_can_cu": 1},
            "detector_day_du": True, "vung_sua_tay": [{"trang": 1, "hop": [10, 10, 20, 20]}],
            "giay_xu_ly_core": 1.5, "ram_dinh_bytes": 1000000,
            "lech_dau_trang": [{"so_tu": 10, "so_tu_lech": 1}]}


class AdapterGia:
    """Đối tượng giả host Core; mọi cờ môi trường ở đây chỉ là dữ liệu test."""
    def __init__(self, r=None, loi_tai=None, ngoai_le=None, tre=False):
        self.r = quan_sat() if r is None else r
        self.calls = []
        self.loi_tai, self.ngoai_le, self.tre = loi_tai, ngoai_le, tre

    def trao_doi(self, req):
        self.calls.append(deepcopy(req))
        op = req["thao_tac"]
        if op == self.loi_tai:
            raise self.ngoai_le
        mtq = req["ma_tuong_quan"]
        if op == "kiem_moi_truong":
            return dict(ma_tuong_quan=mtq, core_that=True, ocr_that=True, local_that=True,
                        chi_local=True, bo_demo_da_xac_minh=True, bam_cau_hinh="sha256:" + "d"*64)
        if op == "luu_bao_cao":
            return {"ma_tuong_quan": mtq, "da_luu": True}
        if op == "gui_viec" and self.tre:
            return {"ma_tuong_quan": mtq, "trang_thai": "DA_NHAN"}
        return {"ma_tuong_quan": mtq, **self.r}


@pytest.fixture
def args(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "WORKSPACE", tmp_path)
    (tmp_path / "DEMO-bo.json").write_text(json.dumps(bo_demo()), encoding="utf-8")
    return t.tao_parser().parse_args(["--that", "--bo-demo", "DEMO-bo.json", "--ma-phien", "DEMO-phien",
        "--module", "demo", "--quy-trinh", "demo", "--cau-hinh-core", "demo", "--iou-ghep", "0.5"])


def test_chay_kho_khong_doc_khong_ghi_khong_handle(monkeypatch):
    def cam(*a, **k):
        pytest.fail("Chạy khô đã truy cập môi trường")
    monkeypatch.setattr(t, "duong_workspace", cam)
    monkeypatch.setattr(t, "CongHandle", cam)
    a = t.tao_parser().parse_args(["--bo-demo", ".env", "--bao-cao", "DEMO-khong-ghi.json"])
    bc = t.thuc_hien(a, cong=AdapterGia())
    assert bc["che_do"] == "CHAY_KHO" and bc["cong_chat_luong"] == bc["ket_luan_do"] == "CHUA_DO"
    assert all(v["gia_tri"] is None and v["ly_do"] for v in bc["so_do_chay_kho"].values())
    assert all(v["ket_qua"] is None for v in bc["trinh_duyet_core"].values())


@pytest.mark.parametrize("argv", [["--khoa", "DEMO-bi-mat"], ["--th"], ["--core-vao-fd", "x"],
    ["--han-giay", "nan"], ["--han-giay", "61"], ["--iou-ghep", "0"], ["--iou-ghep", "inf"]])
def test_parse_loi_khong_lo_tham_so(argv, capsys):
    assert t.main(argv) == 2
    err = capsys.readouterr().err
    assert "DC_THAM_SO_KHONG_HOP_LE" in err and "DEMO-bi-mat" not in err


def test_thieu_moi_truong_khong_gui(args):
    with pytest.raises(LoiNghiepVu, match="Chưa có đủ môi trường"):
        t.thuc_hien(args)
    assert t.main(["--that"]) == 2
    c = AdapterGia()
    c.trao_doi = lambda req: {"ma_tuong_quan": req["ma_tuong_quan"], "trang_thai": "LOI"}
    with pytest.raises(LoiNghiepVu) as e:
        t.thuc_hien(args, cong=c)
    assert e.value.ma == "DC_CHUA_CO_MOI_TRUONG_THU"


def test_chi_gui_nguon_khong_gui_dap_an(args):
    cong = AdapterGia(tre=True)
    bc = t.thuc_hien(args, cong=cong)
    assert bc["nghiem_trong"]["tu_so"] == bc["nghiem_trong"]["mau_so"] == 2
    assert bc["sua_that_bi_an"]["tu_so"] == 0 and bc["sua_that_bi_an"]["mau_so"] == 2
    assert bc["cong_chat_luong"] == "DAT_TREN_BO_DEMO" and bc["ket_luan_do"] == "CHO_ANH_DUYET_NGUONG"
    assert [r["thao_tac"] for r in cong.calls] == ["kiem_moi_truong", "gui_viec", "doc_viec", "luu_bao_cao"]
    sent = cong.calls[1]
    assert not {"diem", "dap_an", "iou_ghep", "vung_sua_tay"} & sent.keys()
    assert sent["chi_local"] is True and bc["ca"][0]["cloud"] == 0
    assert all(v["ket_qua"] is None for v in bc["trinh_duyet_core"].values())


@pytest.mark.parametrize("op", ["gui_viec", "doc_viec", "luu_bao_cao"])
@pytest.mark.parametrize("exc", [TimeoutError(), OSError("DEMO-secret-path"), KeyboardInterrupt()])
def test_mat_phan_hoi_khong_retry(args, op, exc):
    c = AdapterGia(loi_tai=op, ngoai_le=exc, tre=True)
    with pytest.raises(ChuaRo) as e:
        t.thuc_hien(args, cong=c)
    assert e.value.ma_tuong_quan == ("DEMO-phien" if op == "luu_bao_cao" else "DEMO-phien-1")
    assert len([r for r in c.calls if r["thao_tac"] == "gui_viec"]) == 1


@pytest.mark.parametrize("state,cls,ma", [("CHUA_RO", ChuaRo, None), ("HUY", LoiNghiepVu, "DC_HUY"),
    ("LOI", LoiNghiepVu, "DC_LOI_NGUON_THU"), ("DANG_CHAY", ChuaRo, None)])
def test_huy_loi_chua_ro(args, state, cls, ma):
    c = AdapterGia({"trang_thai": state})
    with pytest.raises(cls) as e:
        t.thuc_hien(args, cong=c)
    if ma:
        assert e.value.ma == ma
    assert not any(r["thao_tac"] == "luu_bao_cao" for r in c.calls)


def test_huy_truoc_gui(args):
    c = AdapterGia()
    def huy():
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        t.thuc_hien(args, cong=c, kiem_huy=huy)
    assert c.calls == []


@pytest.mark.parametrize("key", ["core_that", "ocr_that", "local_that", "chi_local", "bo_demo_da_xac_minh"])
def test_thieu_moi_truong_tu_choi(args, key):
    c = AdapterGia()
    original = c.trao_doi
    def doi(req):
        r = original(req)
        r[key] = False
        return r
    c.trao_doi = doi
    with pytest.raises(LoiNghiepVu) as e:
        t.thuc_hien(args, cong=c)
    assert e.value.ma == "DC_CHUA_CO_MOI_TRUONG_THU" and len(c.calls) == 1


@pytest.mark.parametrize("key,value", [("cloud", 1), ("cloud", False), ("bam_scan", "sha256:"+"c"*64),
    ("so_trang", 2), ("so_trang", True)])
def test_cloud_sai_nguon_phan_trang_tu_choi(args, key, value):
    r = quan_sat()
    r[key] = value
    with pytest.raises(LoiNghiepVu):
        t.thuc_hien(args, cong=AdapterGia(r))


@pytest.mark.parametrize("key", ["diem", "diem_day_du", "tu_abbyy", "ocr_vung", "tu_dien",
    "detector_day_du", "vung_sua_tay", "giay_xu_ly_core", "ram_dinh_bytes"])
def test_thieu_do_khong_thanh_dat(args, key):
    r = quan_sat()
    r.pop(key)
    bc = t.thuc_hien(args, cong=AdapterGia(r))
    assert bc["ket_luan_do"] == "CHUA_DO"
    if key.startswith("diem"):
        assert bc["cong_chat_luong"] == "CHUA_DO"


@pytest.mark.parametrize("change", ["ha_muc", "an", "nhieu", "bo_sot"])
def test_cong_that_bai_khong_duoc_che_bang_thieu_do(args, change):
    r = quan_sat()
    if change == "ha_muc":
        r["diem"][0]["muc"] = "can_xem"
    if change == "an":
        r["diem"][0]["an_mac_dinh"] = True
    if change == "nhieu":
        r["diem"][0]["muc"] = "nhieu_ocr"
    if change == "bo_sot":
        r["diem"] = []
    r.pop("tu_abbyy")
    bc = t.thuc_hien(args, cong=AdapterGia(r))
    assert bc["ket_luan_do"] == bc["cong_chat_luong"] == "KHONG_DAT"


def test_ghep_mo_ho_chua_do_va_them_chu_neo_rong():
    c, r = bo_demo()["ca"][0], quan_sat()
    r["diem"].append(deepcopy(r["diem"][0]))
    assert t.cham_ca(c, r, .5)["nghiem_trong"]["gia_tri"] is None
    c["diem"][0]["neo"]["ket_thuc"] = 5
    r["diem"] = r["diem"][:1]
    assert t.cham_ca(c, r, .5)["nghiem_trong"]["gia_tri"] == 1


def test_mau_so_0_khong_thanh_0_phan_tram():
    assert t.phep_do(0, 0)["gia_tri"] is None
    c, r = bo_demo()["ca"][0], quan_sat()
    r["tu_abbyy"] = []
    r["lech_dau_trang"] = [{"so_tu": 0, "so_tu_lech": 0}]
    row = t.cham_ca(c, r, .5)
    assert row["toa_do_tu_abbyy"]["gia_tri"] is None
    assert row["lech_dau_trang"][0]["gia_tri"] is None
    r["tu_abbyy"] = [{"hop": None, "nghi_ngo": False}]
    row = t.cham_ca(c, r, None)
    assert row["toa_do_tu_abbyy"]["gia_tri"] == 0
    assert row["co_nghi_ngo_abbyy"]["gia_tri"] == 1
    assert row["detector_recall"]["gia_tri"] is None
    r["giay_xu_ly_core"] = r["ram_dinh_bytes"] = 0
    row = t.cham_ca(c, r, .5)
    assert row["giay_xu_ly_core"]["gia_tri"] is None and row["ram_dinh_bytes"]["gia_tri"] is None
    assert row["trang_moi_giay"]["gia_tri"] is None and not t.so(10**400)


def test_lech_gia_va_detector_co_tu_mau_so():
    c, r = bo_demo()["ca"][0], quan_sat()
    r["diem"].append({"neo": {"bat_dau": 30, "ket_thuc": 31}, "muc": "can_xem", "an_mac_dinh": False})
    r["vung_sua_tay"].append({"trang": 1, "hop": [40, 40, 50, 50]})
    row = t.cham_ca(c, r, .5)
    assert row["lech_gia_moi_trang"]["tu_so"] == row["lech_gia_moi_trang"]["mau_so"] == 1
    assert row["detector_recall"]["gia_tri"] == 1
    assert row["detector_precision"]["tu_so"] == 1 and row["detector_precision"]["mau_so"] == 2


def test_vung_sua_tay_cung_la_nghiem_trong(args):
    r = quan_sat()
    r["vung_sua_tay"] = []
    bc = t.thuc_hien(args, cong=AdapterGia(r))
    assert bc["nghiem_trong"]["tu_so"] == 1 and bc["nghiem_trong"]["mau_so"] == 2
    assert bc["cong_chat_luong"] == "KHONG_DAT"
    assert bc["sua_that_bi_an"]["gia_tri"] is None


def test_chu_da_that_bai_khong_che_bang_detector_chua_do(args):
    r = quan_sat()
    r["diem"][0]["muc"] = "can_xem"
    r.pop("detector_day_du")
    bc = t.thuc_hien(args, cong=AdapterGia(r))
    assert bc["nghiem_trong"]["gia_tri"] is None
    assert bc["cong_chat_luong"] == bc["ket_luan_do"] == "KHONG_DAT"


@pytest.mark.parametrize("bad", [b'{"a":1,"a":2}', b'{"x":NaN}', b'{"x":Infinity}', b'\xff', b'{'])
def test_json_nghiem(bad):
    with pytest.raises(LoiNghiepVu):
        t.doc_json(bad)


@pytest.mark.parametrize("key,value", [("nhan", "THAT"), ("dap_an_day_du", False), ("phien_ban", True), ("ca", [])])
def test_bo_khong_demo_tu_choi(key, value):
    b = bo_demo()
    b[key] = value
    with pytest.raises(LoiNghiepVu):
        t.kiem_bo(b)


@pytest.mark.parametrize("name", ["../DEMO-x.json", "goi/DEMO-x.json", "var/DEMO-x.json", ".env",
    "cau_hinh.that.toml", "ma-nguon/DEMO-x.json", "x.json", "DEMO-x.json:ads"])
def test_bao_cao_cam_duong_may_va_goi(args, name):
    args.bao_cao = name
    c = AdapterGia()
    with pytest.raises(LoiNghiepVu):
        t.thuc_hien(args, cong=c)
    assert c.calls == []


def test_bao_cao_chi_mot_tep_khong_ghi_de_khong_lo_nguon(args, tmp_path):
    args.bao_cao = "DEMO-ket-qua.json"
    r = quan_sat()
    r["thong_diep"] = "DEMO-secret-path-key"
    r["tu_dien"]["duong_may"] = "DEMO-secret-path-key"
    bc = t.thuc_hien(args, cong=AdapterGia(r))
    raw = (tmp_path / args.bao_cao).read_text(encoding="utf-8")
    assert json.loads(raw) == bc and "DEMO-secret-path-key" not in raw
    assert "tep_id" not in raw and "DEMO-phien" not in raw and "cau_hinh_core" not in raw
    with pytest.raises(LoiNghiepVu):
        t.thuc_hien(args, cong=AdapterGia())


def test_core_gia_so_do_khong_bia_may_that(args):
    from chay_demo_voi_core_gia import nap_mau, dap_an, nhan_va_so
    m = nap_mau(dap_an()[0])
    pb = nhan_va_so(m)
    s = m.snapshot({"ket_qua": pb})
    # Adapter test chuyển nguyên offset từ CoreGia, không gọi runtime trực tiếp trong công cụ.
    r = quan_sat()
    r["diem"] = [{"neo": {"bat_dau": d["word"]["bat_dau"], "ket_thuc": d["word"]["ket_thuc"]},
                  "muc": d["muc"], "an_mac_dinh": d["muc"] == "nhieu_ocr"} for d in s["diem_lech"] if d["word"]]
    assert r["diem"][0]["muc"] == "nghiem_trong"
    r["diem_day_du"] = all(d["word"] is not None for d in s["diem_lech"])
    r.pop("tu_abbyy")  # CoreGia không chứng minh ABBYY có tọa độ/cờ thật.
    bc = t.thuc_hien(args, cong=AdapterGia(r))
    assert bc["nghiem_trong"]["gia_tri"] is None and bc["ket_luan_do"] == "CHUA_DO"
    assert bc["ca"][0]["toa_do_tu_abbyy"]["gia_tri"] is None


def test_cli_kho_va_cmd_ascii():
    raw = (CONG_CU / "THU-DOI-CHIEU-THAT.cmd").read_bytes().decode("ascii")
    assert "--that" not in raw and "Scripts\\python.exe" in raw and "%*" in raw
    r = subprocess.run([sys.executable, "-B", str(CONG_CU / "thu_doi_chieu_that.py")], capture_output=True,
                       encoding="utf-8", timeout=20)
    assert r.returncode == 0 and json.loads(r.stdout)["che_do"] == "CHAY_KHO"


def test_handle_tu_choi_file_va_fd_chuan(tmp_path):
    with pytest.raises(LoiNghiepVu):
        t.CongHandle(0, 1, 1)
    with (tmp_path / "DEMO-file").open("w+b") as f:
        with pytest.raises(LoiNghiepVu):
            t.CongHandle(f.fileno(), f.fileno() + 10000, 1)


def test_handle_pipe_gia_va_timeout_khong_gui_lai():
    import os
    import threading
    vao, host_ra = os.pipe()
    host_vao, ra = os.pipe()
    calls = []
    def host():
        with os.fdopen(host_vao, "rb", buffering=0) as nhan, os.fdopen(host_ra, "wb", buffering=0) as gui:
            req = json.loads(nhan.readline())
            calls.append(req)
            gui.write(json.dumps({"ma_tuong_quan": req["ma_tuong_quan"], "trang_thai": "XONG"}).encode() + b"\n")
    th = threading.Thread(target=host)
    th.start()
    try:
        c = t.CongHandle(vao, ra, 1)
        r = t.trao(c, "doc_viec", "DEMO-pipe", {}, co_the_da_nhan=True)
        assert r["trang_thai"] == "XONG" and len(calls) == 1
    finally:
        os.close(vao)
        os.close(ra)
        th.join(timeout=2)
    vao, host_ra = os.pipe()
    host_vao, ra = os.pipe()
    try:
        c = t.CongHandle(vao, ra, .01)
        with pytest.raises(ChuaRo):
            t.trao(c, "gui_viec", "DEMO-timeout", {}, co_the_da_nhan=True)
        assert c.hong
        with pytest.raises(OSError):
            c.trao_doi({})
    finally:
        # Đóng đầu host để worker daemon thoát with/finally; không giữ tệp tạm.
        for fd in (host_ra, host_vao, vao, ra):
            os.close(fd)
