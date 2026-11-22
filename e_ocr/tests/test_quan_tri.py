"""UI-OCR: đã kiểm bằng Core giả (CoreGia) và máy giả, chỉ DEMO."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_ocr import quan_tri, tesseract
from ngan_demo import GOI, KHAI


def chay_quan_tri(ma, dau_vao):
    # Adapter chỉ trong test: SDK 2.5.0 chưa có thao_tac_quan_tri.
    # Không thêm năng lực vào engine.json hoặc runtime xử lý việc OCR.
    phieu = deepcopy(KHAI)
    phieu["nang_luc"] = [{
        "ma": "thu.kiem_nguon@1", "ten": "Kiểm nguồn DEMO", "nhan": ["truong"],
        "tra": "truong", "gioi_han": {"thoi_han_giay": 15},
        "truong_ra": [{"ma": "dat", "ten": "Kiểm đạt", "kieu": "co_khong"},
                      {"ma": "ma", "ten": "Mã kết quả", "kieu": "van_ban"}],
    }]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=GOI)

    @app.nang_luc("thu.kiem_nguon@1")
    def kiem(viec):
        tac = SimpleNamespace(dau_vao=viec.dau_vao["truong"], kiem_huy=viec.kiem_huy,
                              ngan=viec.ngan, cau_hinh=viec.cau_hinh)
        return {"loai": "truong", "truong": quan_tri.THAO_TAC[ma](tac)}

    core = CoreGia(phieu, thu_muc_goi=GOI)
    kq = core.chay_thu(app, "thu.kiem_nguon@1", {"loai": "truong", "truong": dau_vao})
    assert all(not core.xem_ngan("e_ocr", bang["bang"]) for bang in KHAI["ngan_du_lieu"])
    return kq


def hot_folder(tmp_path):
    vao, ra = tmp_path / "DEMO-nhan", tmp_path / "DEMO-tra"
    vao.mkdir(); ra.mkdir()
    return {"thu_muc_vao": str(vao), "thu_muc_ra": str(ra)}


def test_hot_folder_chi_metadata_khong_mo_doc_ghi_ho_so(tmp_path, monkeypatch):
    cfg = hot_folder(tmp_path)
    goi = []

    def gia(cfg, **kw):
        assert cfg["bat"] is True  # Có thể kiểm bản nháp khi công tắc tắt.
        assert cfg["thoi_han_giay"] == 900
        return SimpleNamespace(_vao=Path(cfg["thu_muc_vao"]), _ra=Path(cfg["thu_muc_ra"]))

    monkeypatch.setattr(quan_tri, "BackendABBYY", gia)
    monkeypatch.setattr(quan_tri.os, "access", lambda p, quyen: goi.append((p, quyen)) or True)
    kq = chay_quan_tri("kiem_hot_folder", {"abbyy": {**cfg, "bat": False}})
    assert kq["trang_thai"] == "XONG"
    assert kq["ket_qua"]["truong"] == {"dat": True, "ma": "HOT_FOLDER_TRUY_CAP_DUOC"}
    assert len(goi) == 2
    assert list(tmp_path.rglob("*")) == [Path(cfg["thu_muc_vao"]), Path(cfg["thu_muc_ra"])]


@pytest.mark.parametrize("loi", ["thieu", "trung", "long", "tuong_doi", "khong_quyen"])
def test_hot_folder_that_bai_khong_ghi_han_muc(tmp_path, monkeypatch, loi):
    cfg = hot_folder(tmp_path)
    if loi == "thieu":
        cfg["thu_muc_ra"] = str(tmp_path / "DEMO-chua-co")
    elif loi == "trung":
        cfg["thu_muc_ra"] = cfg["thu_muc_vao"]
    elif loi == "long":
        con = Path(cfg["thu_muc_vao"]) / "DEMO-con"
        con.mkdir(); cfg["thu_muc_ra"] = str(con)
    elif loi == "tuong_doi":
        cfg["thu_muc_vao"] = "DEMO/nhan"
    else:
        monkeypatch.setattr(quan_tri.os, "access", lambda *a: False)
    kq = chay_quan_tri("kiem_hot_folder", {"abbyy": cfg})
    assert kq["ket_qua"]["truong"] == {"dat": False, "ma": "HOT_FOLDER_KHONG_TRUY_CAP"}
    assert cfg["thu_muc_ra"] not in json.dumps(kq)


@pytest.mark.parametrize("dau_vao", [{}, {"abbyy": None}, {"abbyy": {"thu_muc_vao": ""}},
                                   {"abbyy": {"thu_muc_vao": "x" * 4097}},
                                   {"abbyy": {}, "khoa": "DEMO-bi-mat"}])
def test_hot_folder_loi_nhap_tieng_viet(dau_vao):
    kq = chay_quan_tri("kiem_hot_folder", dau_vao)
    assert kq["trang_thai"] == "LOI"
    assert kq["loi"]["ma"] == "CAU_HINH_KHONG_HOP_LE"
    assert "DEMO-bi-mat" not in json.dumps(kq)


@pytest.mark.parametrize("ngon_ngu", ["vie", "eng", "vie+eng", "eng+vie"])
def test_tesseract_kiem_ngon_ngu_khong_ocr(monkeypatch, ngon_ngu):
    lenh = []
    monkeypatch.setattr(tesseract, "tim_tesseract", lambda cfg: "DEMO/tesseract.exe")

    def chay(lenh_vao, **kw):
        lenh.append(lenh_vao)
        assert kw["thoi_han"] == 10
        kw["viec"].kiem_huy()
        return b"List of available languages (2):\nvie\neng\n"

    monkeypatch.setattr(tesseract, "_chay", chay)
    kq = chay_quan_tri("kiem_tesseract", {"tesseract": {"duong_dan": "", "ngon_ngu": ngon_ngu}})
    assert kq["ket_qua"]["truong"] == {"dat": True, "ma": "TESSERACT_DU_NGON_NGU"}
    assert lenh == [["DEMO/tesseract.exe", "--list-langs"]]


@pytest.mark.parametrize("loi", ["thieu_ngon_ngu", "chua_cai", "qua_han", "thoat_loi"])
def test_tesseract_that_bai_khong_lo_stdout_stderr(monkeypatch, loi):
    monkeypatch.setattr(tesseract, "tim_tesseract", lambda cfg: "DEMO/tesseract.exe")

    class TienTrinhGia:
        stdout = SimpleNamespace(close=lambda: None)
        returncode = 1 if loi == "thoat_loi" else 0
        def communicate(self, timeout):
            if loi == "qua_han":
                raise subprocess.TimeoutExpired("DEMO-duong-dan-rieng", timeout)
            return b"DEMO-bi-mat\neng\n", None
        def poll(self):
            return None if loi == "qua_han" else self.returncode
        def kill(self):
            self.returncode = -1
        def wait(self, timeout):
            return self.returncode

    def khoi_chay(*args, **kw):
        assert kw["stderr"] == subprocess.DEVNULL
        if loi == "chua_cai":
            raise OSError("DEMO-duong-dan-rieng")
        return TienTrinhGia()

    monkeypatch.setattr(tesseract.subprocess, "Popen", khoi_chay)
    if loi == "qua_han":
        # Không chờ thật 10 giây trong test.
        dem = iter([0, 11])
        monkeypatch.setattr(tesseract, "time", SimpleNamespace(monotonic=lambda: next(dem, 11)))
    kq = chay_quan_tri("kiem_tesseract", {"tesseract": {"ngon_ngu": "vie+eng"}})
    assert kq["ket_qua"]["truong"] == {"dat": False, "ma": "TESSERACT_QUA_THOI_HAN" if loi == "qua_han" else "TESSERACT_CHUA_DUNG_DUOC"}
    assert "DEMO-bi-mat" not in json.dumps(kq) and "DEMO-duong-dan-rieng" not in json.dumps(kq)


@pytest.mark.parametrize("cfg", [{"ngon_ngu": "fra"}, {"duong_dan": "DEMO/powershell.exe"},
                                {"duong_dan": 12}, {"duong_dan": "x" * 4097}])
def test_tesseract_tu_choi_dau_vao_truoc_khi_goi_may(monkeypatch, cfg):
    def cam(*a, **kw):
        pytest.fail("Không được chạy chương trình khi đầu vào sai.")
    monkeypatch.setattr(tesseract, "tim_tesseract", cam)
    kq = chay_quan_tri("kiem_tesseract", {"tesseract": cfg})
    assert kq["loi"]["ma"] == "CAU_HINH_KHONG_HOP_LE"


def test_khai_du_kien_khong_mo_rong_engine_json():
    khai = json.loads((GOI / "KHAI-SDK-2.1.json").read_text(encoding="utf-8"))
    assert {t["ma"] for t in khai["thao_tac_quan_tri"]} == set(quan_tri.THAO_TAC)
    assert not {"thao_tac_quan_tri", "giao_dien_quan_tri"} & KHAI.keys()
    assert KHAI["bi_mat"] == []
