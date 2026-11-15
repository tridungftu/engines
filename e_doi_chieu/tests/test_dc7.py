"""DC-7: đã kiểm bằng Core giả (CoreGia), chỉ DEMO, không OCR/AI/mạng thật."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import socket
import time
from types import SimpleNamespace
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu, ViecDaHuy

from test_dc3 import Mau, hs, chay, kiem_loi, PN, MODULE
from test_dc4 import so
from test_dc5 import bo_demo, dat_bo, qt
from test_dc6 import DieuPhoiDEMO, chuan_bi, giao
from demo_lech_dau import CoreOCRVungDEMO, dat_cap_co_tu, dat_tu_dien, manifest_ocr

ld = importlib.import_module("e_doi_chieu.lech_dau")
td = importlib.import_module("e_doi_chieu.tu_dien")


@pytest.fixture
def mau(monkeypatch):
    m = Mau(CoreOCRVungDEMO())
    monkeypatch.setattr(chay, "ngan", m.ngan)
    dat_tu_dien(m)
    m.provider = DieuPhoiDEMO()
    yield m
    assert m.provider.cloud == 0


def cap_so(m, w="DEMO thuê.", o="DEMO thuế.", *, bo=None):
    dat_cap_co_tu(m, w, o)
    if bo is not None:
        dat_bo(m, bo)
    r = so(m)
    assert r["trang_thai"] == "XONG", r
    return r, m.snapshot(r)


def phan_loai(m, r, s, *, nhan="nhieu_ocr", manifest=None, reply_sua=None):
    req = chuan_bi(m, r["ket_qua"])
    reply = m.provider.hoi(m, req, nhan)
    if reply_sua:
        reply_sua(reply)
    vid = giao(m, "phan_loai_diem_lech", reply)
    if manifest is not None:
        m.core.ocr_vung_viec[vid] = deepcopy(manifest)
    m.core.chay(chay.app)
    return m.core.xem(vid)


def doi_bang_chung(m, manifest, sua):
    for i, ref in enumerate(manifest["ket_qua"]):
        e = json.loads(m.core.doc_tep(ref["tep"]["tep_id"]))
        sua(e)
        new = m.luu(f"DEMO-ocr-doi-{i}.json", hs.json_bytes(e), "application/json")
        manifest["ket_qua"][i] = {**new, **{k: ref[k] for k in ("nguon_doc", "phien_ban_nguon", "nang_luc", "ma_ket_qua")}}
    return manifest


@pytest.mark.parametrize("w,o", [cap for a, b in td.CAP_CO_NGHIA for cap in ((a, b), (b, a))])
@pytest.mark.parametrize("co_ocr", [False, True])
def test_ma_tran_cap_co_nghia_khong_tu_bo_qua(mau, w, o, co_ocr):
    r, s = cap_so(mau, "DEMO " + w + ".", "DEMO " + o + ".")
    assert s["diem_lech"] and all(d["nhom"] == "chi_lech_dau" for d in s["diem_lech"])
    assert all(d["muc"] != "nhieu_ocr" for d in s["diem_lech"])
    if not any(d["cho_phan_loai"] for d in s["diem_lech"]):
        assert all(d["muc"] == "nghiem_trong" for d in s["diem_lech"])  # không/khống: phủ định là quy tắc cứng.
        return
    out = phan_loai(mau, r, s, manifest=manifest_ocr(mau, s) if co_ocr else None)
    assert out["trang_thai"] == "XONG", out
    final = mau.snapshot(out)
    assert all(d["muc"] == ("nhieu_ocr" if co_ocr else "can_xem") for d in final["diem_lech"])
    assert final["nhat_ky_quy_tac"] == s["nhat_ky_quy_tac"]
    assert final["edit_script"] == s["edit_script"]
    assert all(d["muc_san"] == "can_xem" for d in final["diem_lech"])
    assert final["tom_tat"]["so_nhieu_ocr"] == (len(s["diem_lech"]) if co_ocr else 0)


def test_tu_vo_nghia_demo_co_chung_nhan_chi_python_moi_phan_loai(mau):
    r, s = cap_so(mau, "DEMO hợp.", "DEMO hơp.")
    out = phan_loai(mau, r, s, nhan="khong_chac")
    assert out["trang_thai"] == "XONG", out
    final = mau.snapshot(out)
    assert all(d["muc"] == "nhieu_ocr" for d in final["diem_lech"])
    assert all(r["tu_dien"] == "vo_nghia_co_can_cu" and r["can_cu_vo_nghia"] for r in final["lech_dau"]["ket_qua"])
    assert final["lech_dau"]["tu_dien"]["pham_vi"] == "DEMO"
    assert final["lech_dau"]["tu_dien"]["bam"] == mau.cau_hinh["bam_tu_dien"]
    assert any("DC-Q14" in c for c in final["canh_bao"])
    assert final["ket_luan"] is None and not final["da_kiem_du"]


@pytest.mark.parametrize("co_ocr", [False, True])
def test_tu_la_ngoai_tu_dien_huu_han_khong_tu_thanh_vo_nghia(mau, co_ocr):
    r, s = cap_so(mau, "DEMO zạ.", "DEMO zả.")
    out = phan_loai(mau, r, s, manifest=manifest_ocr(mau, s) if co_ocr else None)
    assert out["trang_thai"] == "XONG", out
    final = mau.snapshot(out)
    assert all(d["muc"] == "can_xem" for d in final["diem_lech"])
    assert all(r["tu_dien"] == "chua_biet" for r in final["lech_dau"]["ket_qua"])


@pytest.mark.parametrize("nhan", ["khong_chac", "can_xem", "hinh_thuc", "nghiem_trong"])
def test_ocr_dong_y_ai_khong_xac_nhan_loi_ocr_giu_can_xem_hoac_da_nang(mau, nhan):
    r, s = cap_so(mau)
    out = phan_loai(mau, r, s, nhan=nhan, manifest=manifest_ocr(mau, s))
    assert out["trang_thai"] == "XONG", out
    assert all(d["muc"] == ("nghiem_trong" if nhan == "nghiem_trong" else "can_xem") for d in mau.snapshot(out)["diem_lech"])


@pytest.mark.parametrize("text", ["", " \n", "thuế", "thuê thêm chữ", "DEMO thuê"])
def test_ai_dong_y_ocr_lai_rong_hoac_khac_khong_thanh_nhieu_giu_anh_cat(mau, text):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s, text=text, anh_cat=True)
    out = phan_loai(mau, r, s, manifest=ev)
    assert out["trang_thai"] == "XONG", out
    final = mau.snapshot(out)
    assert all(d["muc"] == "can_xem" for d in final["diem_lech"])
    for row in final["lech_dau"]["ket_qua"]:
        assert not row["ocr_lai_dat"] and row["anh_cat"]
        cut = row["anh_cat"]
        assert hs.bam(mau.core.doc_tep(cut["tep"]["tep_id"])) == cut["bam"]


@pytest.mark.parametrize("key,value", [("bam_ban_ky", "sha256:" + "0"*64), ("phien_ban_ban_ky", "DEMO-khac"),
    ("ma_cap", "DEMO-cap-khac"), ("ma_diem", "DEMO-diem-khac"), ("trang", 2), ("trang", True),
    ("hop", [1, 10, 35, 30]), ("don_vi", "pt"), ("bat_dau", 0), ("ket_thuc", 1),
    ("bam_anh_trang", "sha256:"+"1"*64), ("nguon_doc", "abbyy"), ("phien_ban_nguon", "DEMO-sai")])
def test_bang_chung_sai_nguon_trang_vung_diem_phien_ban_bi_tu_choi(mau, key, value):
    r, s = cap_so(mau)
    ev = doi_bang_chung(mau, manifest_ocr(mau, s), lambda e: e.update({key: value}))
    kiem_loi(phan_loai(mau, r, s, manifest=ev), "DC_SAI_NGUON")


def test_thieu_phien_ban_nguon_khong_tu_nhan_dat(mau):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    ev["ket_qua"][0]["phien_ban_nguon"] = ""
    doi_bang_chung(mau, ev, lambda e: e.update(phien_ban_nguon=""))
    out = phan_loai(mau, r, s, manifest=ev)
    assert out["trang_thai"] == "XONG", out
    assert all(d["muc"] == "can_xem" for d in mau.snapshot(out)["diem_lech"])


@pytest.mark.parametrize("w,o", [("Bên A: Công ty DEMO thuê.", "Bên A: Công ty DEMO thuế."),
    ("DEMO bằng chữ một triệu đồng.", "DEMO bằng chữ môt triệu đồng.")])
def test_vung_ben_ky_va_tien_chu_khong_bao_gio_thanh_nhieu(mau, w, o):
    # Thêm ứng viên độc lập để Core có nhánh AI dù điểm cứng không giao cho AI.
    r, s = cap_so(mau, w + "\nDEMO phạt.", o + "\nDEMO phát.")
    out = phan_loai(mau, r, s, manifest=manifest_ocr(mau, s))
    assert out["trang_thai"] == "XONG", out
    final = mau.snapshot(out)
    for cu, d in zip(s["diem_lech"], final["diem_lech"]):
        if cu["quy_tac_trung"]:
            assert d == cu and d["muc"] == "nghiem_trong"
    assert any(d["muc"] == "nghiem_trong" for d in final["diem_lech"])


def test_co_abbyy_va_caller_tu_khai_khong_thay_ocr_tin_cay(mau):
    # Caller đặt dữ liệu giống hệt bằng chứng đúng, nhưng Core không chứng thực nguồn.
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    mau.cap["bang_chung_ocr_lai"] = [{k: v for k, v in ref.items() if k in ("tep", "bam")} for ref in ev["ket_qua"]]
    r = so(mau)
    assert r["trang_thai"] == "XONG", r
    s = mau.snapshot(r)
    out = phan_loai(mau, r, s)
    assert out["trang_thai"] == "XONG", out
    assert all(d["muc"] == "can_xem" for d in mau.snapshot(out)["diem_lech"])
    assert mau.snapshot(out)["lech_dau"]["contract_ocr_vung"] == "chua_co_contract_ocr_vung"


@pytest.mark.parametrize("loai", ["thieu", "bam", "ma", "phien_ban", "nguon", "giay_phep", "cap_co_nghia"])
def test_tu_dien_thieu_sai_ghim_nguon_khong_duoc_suy_dien(mau, loai):
    value = json.loads((Path(__file__).parent/"fixtures/DEMO-tu-dien-dc7.json").read_bytes())
    if loai in ("nguon", "giay_phep"):
        value[loai] = ""
    if loai == "cap_co_nghia":
        value["cap_vo_nghia_co_can_cu"].append({"word": "thuê", "ocr": "thuế", "can_cu": "DEMO tự khai"})
    bo = dat_tu_dien(mau, value=value)
    if loai == "thieu":
        bo.pop("lech_dau")
    elif loai == "bam":
        bo["lech_dau"]["tu_dien"]["bam"] = "sha256:" + "a"*64
    elif loai == "phien_ban":
        bo["lech_dau"]["tu_dien"]["phien_ban"] = "DEMO-sai"
    elif loai == "ma":
        mau.cau_hinh["ma_tu_dien"] = "DEMO-ma-khac"
    r, s = cap_so(mau, bo=bo)
    result = phan_loai(mau, r, s)
    kiem_loi(result, "DC_THIEU_TU_DIEN" if loai == "thieu" else "DC_SAI_NGUON")


def test_khong_can_tu_dien_neu_chi_co_diem_cung(mau):
    r, s = cap_so(mau, "Bên A: DEMO thuê.", "Bên A: DEMO thuế.", bo=bo_demo())
    assert all(d["muc"] == "nghiem_trong" for d in s["diem_lech"])
    assert s["lech_dau"]["tu_dien"] is None


def test_trang_chua_co_nguong_khong_duoc_coi_la_trang_tot(mau):
    _, s = cap_so(mau, "DEMO thuê.", "DEMO thuế.")
    page = s["lech_dau"]["trang"][0]
    assert page["so_tu_ocr"] == 2 and page["so_tu_lech_dau"] == 1
    assert page["phan_so"] == {"tu_so": 1, "mau_so": 2} and page["ty_le"] == .5
    assert page["trang_thai"] == "chua_kiem" and page["nguong"] is None
    assert s["tom_tat"]["so_trang_ocr_kem"] is None and s["kiem_tra"]["lech_dau"] == "chua_kiem"


def test_khong_tu_khong_phai_khong_phan_tram_loi(mau):
    _, s = cap_so(mau, "...", "...")
    row = s["lech_dau"]["trang"][0]
    assert row["so_tu_ocr"] == 0 and row["ty_le"] is None and row["trang_thai"] == "chua_kiem"
    assert not s["da_kiem_du"]


def test_tu_so_dem_token_phan_biet_khong_dem_so_edit_script(mau):
    _, s = cap_so(mau, "DEMO ábá.", "DEMO àbà.")
    page = s["lech_dau"]["trang"][0]
    assert len(s["diem_lech"]) >= 2
    assert page["so_tu_lech_dau"] == 1 and page["so_tu_ocr"] == 2


@pytest.mark.parametrize("threshold,status", [(.49, "ocr_kem"), (.5, "khong_vuot_nguong"), (.51, "khong_vuot_nguong")])
def test_nguong_demo_ghim_va_bien_vuot_nghiem_ngat(mau, threshold, status):
    bo = dat_tu_dien(mau)
    bo["lech_dau"]["nguong_ocr_kem"] = {"ty_le": threshold, "phien_ban": "DEMO-do-1", "nguon_do": "Fixture DEMO, không là ngưỡng vận hành"}
    _, s = cap_so(mau, bo=bo)
    assert s["lech_dau"]["trang"][0]["trang_thai"] == status
    assert s["tom_tat"]["so_trang_ocr_kem"] == int(status == "ocr_kem")


def test_trang_ocr_kem_gom_nhieu_giu_moi_diem_va_rieng_nghiem_trong(mau):
    bo = dat_tu_dien(mau)
    bo["lech_dau"]["nguong_ocr_kem"] = {"ty_le": 0, "phien_ban": "DEMO-do-1", "nguon_do": "DEMO"}
    r, s = cap_so(mau, "Bên A: DEMO thuê.\nDEMO phạt.", "Bên A: DEMO thuế.\nDEMO phát.", bo=bo)
    out = phan_loai(mau, r, s, manifest=manifest_ocr(mau, s))
    assert out["trang_thai"] == "XONG", out
    final = mau.snapshot(out)
    assert final["tom_tat"]["so_trang_ocr_kem"] == 1 and final["trang_ocr_kem"][0]["anh_trang"]
    row = final["trang_ocr_kem"][0]
    assert row["ma_nhieu_ocr"] and row["ma_nghiem_trong"]
    assert len(final["diem_lech"]) == len(s["diem_lech"]) and final["edit_script"] == s["edit_script"]
    assert set(row["ma_diem"]) == {d["ma_diem"] for d in final["diem_lech"]}
    for d, old in zip(final["diem_lech"], s["diem_lech"]):
        if old["muc"] == "nghiem_trong":
            assert d == old and d["ma_diem"] in row["ma_nghiem_trong"]


def test_hai_nguon_ocr_mau_thuan_khong_chon_ket_qua_thuan_loi(mau):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    ev["ket_qua"] += manifest_ocr(mau, s, text="thuế")["ket_qua"]
    out = phan_loai(mau, r, s, manifest=ev)
    assert out["trang_thai"] == "XONG", out
    assert all(d["muc"] == "can_xem" for d in mau.snapshot(out)["diem_lech"])


def test_muc_ai_da_nang_khong_bi_tu_dien_ha_xuong(mau):
    r, s = cap_so(mau, "DEMO hợp.", "DEMO hơp.")
    out = phan_loai(mau, r, s, nhan="nghiem_trong")
    assert out["trang_thai"] == "XONG", out
    assert all(d["muc"] == "nghiem_trong" for d in mau.snapshot(out)["diem_lech"])


def test_mat_ack_giao_lai_mot_ket_qua_va_khong_tao_lai_snapshot(mau):
    r, s = cap_so(mau)
    req = chuan_bi(mau, r["ket_qua"])
    reply, ev = mau.provider.hoi(mau, req, "nhieu_ocr"), manifest_ocr(mau, s)
    for op in ("tep", "ket_qua", "ket_thuc"):
        mau.core.gay_mat_xac_nhan(op)
    refs, results = [], []
    for _ in range(2):
        vid = giao(mau, "phan_loai_diem_lech", reply)
        mau.core.ocr_vung_viec[vid] = ev
        mau.core.chay(chay.app)
        result = mau.core.xem(vid)
        assert result["trang_thai"] == "XONG", result
        assert len([k for k in mau.core._idem if k[1:3] == ("ket_qua", vid)]) == 1
        refs.append(mau.core.so_tai)
        results.append(result["ket_qua"])
    assert refs[0] == refs[1] and results[0] == results[1]


def test_co_tu_khai_chung_nhan_nhieu_ocr_khong_qua_kiem_bat_bien(mau):
    _, s = cap_so(mau)
    fake = deepcopy(s)
    d = fake["diem_lech"][0]
    d["muc"] = "nhieu_ocr"
    fake["lech_dau"]["ket_qua"][0].update(muc="nhieu_ocr", tu_dien="ca_hai_co_nghia", ai_dat=True, ocr_lai_dat=True)
    with pytest.raises(LoiNghiepVu) as exc:
        ld.kiem_bat_bien(fake, s)
    assert exc.value.ma == "DC_SAI_NGUON"


def test_nguon_khong_quyen_ocr_vung_bi_chan(mau):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    mau.core.cam.add(ev["ket_qua"][0]["tep"]["tep_id"])
    result = phan_loai(mau, r, s, manifest=ev)
    assert result["trang_thai"] == "XONG", result
    final = mau.snapshot(result)
    assert all(d["muc"] == "can_xem" for d in final["diem_lech"])
    assert final["lech_dau"]["contract_ocr_vung"] == "thieu_ket_qua_ocr_vung"


def test_nfd_va_offset_unicode_dung_cum(mau):
    w, o = (unicodedata.normalize("NFD", t) for t in ("DEMO thuê.", "DEMO thuế."))
    r, s = cap_so(mau, w, o)
    out = phan_loai(mau, r, s, manifest=manifest_ocr(mau, s))
    assert out["trang_thai"] == "XONG", out
    assert all(d["muc"] == "nhieu_ocr" for d in mau.snapshot(out)["diem_lech"])


def test_quet_tuyen_tinh_va_huy_giua_token_dai():
    raw = ("DEMO thuê 1.000.000 VND. "*25000)[:500000]
    start = time.perf_counter()
    tokens = td.CacTu(raw)
    elapsed = time.perf_counter() - start
    assert tokens.tu and elapsed < 2
    assert "1.000.000" in {t["van_ban"] for t in tokens.tu}
    calls = [0]
    def huy():
        calls[0] += 1
        if calls[0] == 3:
            raise ViecDaHuy()
    with pytest.raises(ViecDaHuy):
        td.CacTu("a"*500000, huy)
    assert calls[0] == 3


def test_huy_dc7_truoc_tai_snapshot_va_giao_lai_duoc(mau, monkeypatch):
    r, s = cap_so(mau)
    ev, req = manifest_ocr(mau, s), chuan_bi(mau, r["ket_qua"])
    reply = mau.provider.hoi(mau, req, "nhieu_ocr")
    vid = giao(mau, "phan_loai_diem_lech", reply)
    mau.core.ocr_vung_viec[vid] = ev
    original = mau.core._tien_do
    def huy(ma, viec_id, pt, cau):
        if viec_id == vid and pt == 90:
            mau.core.huy(vid)
        return original(ma, viec_id, pt, cau)
    monkeypatch.setattr(mau.core, "_tien_do", huy)
    mau.core.chay(chay.app)
    out = mau.core.xem(vid)
    assert out["trang_thai"] == "HUY" and out["ket_qua"] is None
    retried = phan_loai(mau, r, s, manifest=ev)
    assert retried["trang_thai"] == "XONG", retried


@pytest.mark.parametrize("field,value", [("nang_luc", "ocr.doc_tai_lieu@1"), ("ma_ket_qua", "")])
def test_manifest_core_phai_lien_ket_dung_nang_luc_va_ket_qua_nguon(mau, field, value):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    ev["ket_qua"][0][field] = value
    kiem_loi(phan_loai(mau, r, s, manifest=ev), "DC_SAI_NGUON")


def test_bam_tep_ocr_vung_sai_bi_tu_choi(mau):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    ev["ket_qua"][0]["bam"] = "sha256:" + "a"*64
    kiem_loi(phan_loai(mau, r, s, manifest=ev), "DC_SAI_NGUON")


def test_tu_dien_mat_quyen_tra_ma_thieu_tu_dien(mau):
    r, s = cap_so(mau)
    ref = s["bo_quy_tac"]["noi_dung"]["lech_dau"]["tu_dien"]
    mau.core.cam.add(ref["tep"]["tep_id"])
    kiem_loi(phan_loai(mau, r, s), "DC_THIEU_TU_DIEN")


def test_mau_so_tach_tung_trang_khong_tron_voi_toan_tai_lieu(mau):
    _, s = cap_so(mau, "DEMO thuê.\nDEMO giao đồ.", "DEMO thuế.\fDEMO giao đồ.")
    a, b = s["lech_dau"]["trang"]
    assert a["phan_so"] == {"tu_so": 1, "mau_so": 2}
    assert b["phan_so"] == {"tu_so": 0, "mau_so": 3}


@pytest.mark.parametrize("x", [True, -0.01, 1.01])
def test_nguong_sai_khong_duoc_dung_de_ket_luan_trang(mau, x):
    bo = dat_tu_dien(mau)
    bo["lech_dau"]["nguong_ocr_kem"] = {"ty_le": x, "phien_ban": "DEMO-1", "nguon_do": "DEMO"}
    dat_cap_co_tu(mau, "DEMO thuê.", "DEMO thuế.")
    dat_bo(mau, bo)
    kiem_loi(so(mau), "DC_SAI_NGUON")


def test_runtime_khong_mang_ghi_ben_hoac_goi_ocr_cloud(mau, monkeypatch):
    r, s = cap_so(mau)
    ev = manifest_ocr(mau, s)
    def cam(*args, **kwargs):
        raise AssertionError("DEMO: cấm gọi mạng hoặc ghi đĩa")
    monkeypatch.setattr(socket, "create_connection", cam)
    monkeypatch.setattr(Path, "write_text", cam)
    monkeypatch.setattr(Path, "write_bytes", cam)
    out = phan_loai(mau, r, s, manifest=ev)
    assert out["trang_thai"] == "XONG", out
    assert mau.provider.cloud == 0
