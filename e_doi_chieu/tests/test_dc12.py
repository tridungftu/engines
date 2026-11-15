"""DC-12: kiểm toàn chuỗi và đường khởi động HTTP; chỉ DEMO/CoreGia."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia, MayChuGia

from chay_demo_voi_core_gia import (dap_an, do_ca, nap_mau, nhan_va_so,
    local_va_xuat, chay_demo, kiem_loi_nguon)
from test_dc3 import chay, hs, GOI, kiem_loi
from test_dc6 import PARAMS, chuan_bi, hau_kiem, giao, chay_buoc, DieuPhoiDEMO
from test_dc8 import tao_mau, giao_quet
from test_dc9 import doc_kq, xuat


@pytest.mark.parametrize("ca", dap_an(), ids=lambda c: c["ma"])
def test_dap_an_doc_lap_qua_chuoi_va_bao_cao(ca):
    r = do_ca(ca)
    assert r["bat_du"] and not r["bi_an_thanh_nhieu"]


def test_harness_dem_mau_so_khong_tinh_thieu_do_la_dat():
    r = chay_demo()
    assert r["so_ca_chuoi"] == 10
    assert r["nghiem_trong_bat_du"] == r["nghiem_trong_da_cai"] == 5
    assert r["sua_that_bi_an_thanh_nhieu"] == 0 and r["sua_that_da_cai"] == 8
    assert r["do_chat_luong_may_that"] is None and r["ly_do_chua_do"]
    assert r["cloud_that"] == r["ocr_that"] == r["ai_that"] == 0


@pytest.mark.parametrize("sai", [False, True], ids=["du_bang_chung", "cau_bia"])
def test_tep_cap_den_truong_du_va_sai_bang_chung(sai):
    m = nap_mau(dap_an()[6])
    t, s, _, request, reply = local_va_xuat(m, nhan_va_so(m), nhan="can_xem", sai_trich=sai)
    assert request["loai"] == "yeu_cau_ai" and reply["loai"] == "tra_loi_ai"
    assert s["ai"]["ket_qua"]
    assert all(r["trich_dan_dat"] is (not sai) for r in s["ai"]["ket_qua"])
    assert s["kiem_tra"]["phan_loai_ai"] == ("khong_dat" if sai else "dat")
    assert t["ket_luan"] == "chua_doi_chieu_duoc" and t["de_nghi_chan"]
    assert all(d["muc"] == "can_xem" for d in s["diem_lech"])


def test_bon_loi_nguon_la_loi_nghiep_vu_truoc_khi_sdk_dong_goi(monkeypatch):
    exceptions = []
    for name in ("can_cau_hinh", "_nhan_cap"):
        original = getattr(chay, name)
        def theo_doi(*a, _ham=original, **kw):
            try:
                return _ham(*a, **kw)
            except LoiNghiepVu as exc:
                exceptions.append(exc)
                raise
        monkeypatch.setattr(chay, name, theo_doi)
    expected = kiem_loi_nguon()
    assert [e.ma for e in exceptions] == expected
    assert all(e.thong_diep and "DEMO-" not in e.thong_diep for e in exceptions)


@pytest.mark.parametrize("thieu", ["detector", "anh", "toa_do"])
def test_thieu_bang_chung_qua_cua_quet_khong_ket_luan_sach(thieu):
    m = tao_mau("gach")
    from test_dc6 import dat_tu_dien
    dat_tu_dien(m)
    if thieu == "detector":
        m.cau_hinh["phien_ban_detector"] = "DEMO-chua-co"
        m.dat_cau_hinh()
    pb = nhan_va_so(m)
    vid = giao_quet(m, pb, metadata=(thieu != "toa_do"))
    if thieu == "anh":
        m.core.cam.add(m.cap["anh_trang"][0]["tep"]["tep_id"])
    m.core.chay(chay.app)
    r = m.core.xem(vid)
    assert r["trang_thai"] == "LOI" and r["ket_qua"] is None
    assert r["loi"]["ma"] in {"DC_CHUA_CO_BO_PHAT_HIEN", "DC_THIEU_ANH", "DC_THIEU_NGUON"}
    assert not any(b.gia_tri["trang_thai"] == "da_xuat" for b in m.cac_luot())


@pytest.mark.parametrize("buoc", ["chuan_bi_ai", "phan_loai_diem_lech", "xuat_ket_qua"])
@pytest.mark.parametrize("loai", ["huy", "mat_lease"])
def test_dung_giua_chuoi_khong_nop_ket_qua(monkeypatch, buoc, loai):
    m = nap_mau(dap_an()[6])
    pb, params = nhan_va_so(m), PARAMS
    if buoc != "chuan_bi_ai":
        reply = DieuPhoiDEMO().hoi(m, chuan_bi(m, pb))
        pb, params = reply, {}
        if buoc == "xuat_ket_qua":
            r = hau_kiem(m, reply)
            assert r["trang_thai"] == "XONG", r
            pb = r["ket_qua"]
    vid = giao(m, buoc, pb, params)
    original = m.core._tien_do
    dem = []
    def dung(ma, v, pt, cau):
        if v == vid and not dem:
            dem.append(v)
            if loai == "huy":
                m.core.huy(v)
            else:
                # Thu hồi lease bằng trạng thái thời hạn tại Core giả, không vá SDK.
                with m.core._lock:
                    m.core._viec[v]["han_giu"] = "2000-01-01T00:00:00+00:00"
        return original(ma, v, pt, cau)
    monkeypatch.setattr(m.core, "_tien_do", dung)
    m.core.chay(chay.app)
    r = m.core.xem(vid)
    assert dem and r["ket_qua"] is None
    assert r["trang_thai"] == ("HUY" if loai == "huy" else "DANG_CHAY")
    if loai == "mat_lease":
        assert not any(k[1] in {"ket_qua", "ket_thuc"} and k[2] == vid for k in m.core._idem)


@pytest.mark.parametrize("mat", ["tep", "ngan", "ket_qua", "ket_thuc"])
def test_mat_ack_cas_va_gui_lai_toan_chuoi_khong_nhan_doi(mat):
    m = nap_mau(dap_an()[6])
    pb = nhan_va_so(m)
    m.core.gay_xung_dot_ngan("luot_doi_chieu")
    m.core.gay_mat_xac_nhan(mat)
    t, s, pb_hau, _, _ = local_va_xuat(m, pb, nhan="can_xem")
    dem_luot, dem_tep = len(m.cac_luot()), m.core.so_tai
    lap = xuat(m, pb_hau)
    t2, s2, _ = doc_kq(m, lap)
    assert t2 == t and s2 == s
    assert len(m.cac_luot()) == dem_luot and m.core.so_tai == dem_tep
    assert len([b for b in m.cac_luot() if b.gia_tri["trang_thai"] == "da_xuat"]) == 1


@pytest.mark.parametrize("sai", ["quyen", "phap_nhan", "tu_bam"])
def test_khong_tu_cap_quyen_hoac_bam_snapshot_xuyen_chuoi(sai):
    m = nap_mau(dap_an()[6])
    pb = nhan_va_so(m)
    request = chuan_bi(m, pb)
    reply = DieuPhoiDEMO().hoi(m, request)
    pin = reply["tra_loi_ai"]["chuyen_tiep"]["doi_chieu"]
    if sai == "quyen":
        m.core.cam.add(pin["ho_so"]["tep_id"])
    elif sai == "tu_bam":
        raw = m.core.doc_tep(pin["ho_so"]["tep_id"])
        snap = json.loads(raw)
        snap["diem_lech"][0]["muc"] = "nhieu_ocr"
        ref = m.luu("DEMO-tu-sua.json", hs.json_bytes(snap), "application/json")
        pin.update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
    r = chay_buoc(m, "phan_loai_diem_lech", reply,
                  **({"pn": "DEMO-P-khac"} if sai == "phap_nhan" else {}))
    assert r["trang_thai"] == "LOI" and r["ket_qua"] is None
    assert r["loi"]["ma"] in {"DC_THIEU_NGUON", "DC_SAI_NGUON"}


def test_app_chay_doc_dong_khoi_dong_http_loopback():
    core = CoreGia()
    raw = (GOI / "demo/DEMO-ban-chot.docx").read_bytes()
    tep = core.them_tep("DEMO-khoi-dong.docx", raw,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    vid = core.giao_viec("doi_chieu.doc_docx@1", {"loai": "tep", "tep": tep})
    # Khóa sinh mới trong RAM, không hằng số/tệp/log và không truyền qua argv/env.
    khoa = secrets.token_urlsafe(32)
    env = {k: v for k, v in os.environ.items() if not k.startswith("KTT_")}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    with MayChuGia(core, {chay.app.ma: khoa}) as may:
        proc = subprocess.Popen([sys.executable, "-B", "-c",
            "from e_doi_chieu.chay import app; app.chay(dung_khi_het_viec=True, cho_gui_lai_giay=0)"],
            cwd=GOI, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            out, err = proc.communicate((json.dumps({"core_url": may.url, "khoa": khoa,
                "instance": "DEMO-dc12-http"}) + "\n").encode(), timeout=20)
            assert proc.returncode == 0, err.decode("utf-8")
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=5)
        calls = may.cac_loi_goi
    assert khoa.encode() not in out + err
    r = core.xem(vid)
    assert r["trang_thai"] == "XONG", r
    vb = r["ket_qua"]["van_ban_tai_lieu"]
    assert vb["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()
    assert "Công ty DEMO Ánh Dương" in vb["van_ban"]
    assert all(c["co_bearer"] and c["instance"] == "DEMO-dc12-http" for c in calls)
    for suffix in ("san-sang", "viec/nhan", f"viec/{vid}/tep/{tep['tep_id']}",
                   f"viec/{vid}/ket-qua", f"viec/{vid}/ket-thuc"):
        assert any(c["duong"].endswith(suffix) for c in calls), suffix
    assert all(c["idempotency_key"] for c in calls if c["phuong_thuc"] == "PUT" or
               c["duong"].endswith("ket-thuc"))


def test_toan_chuoi_chi_ram_ngan_va_kho_tep_core(monkeypatch):
    import builtins
    import io
    import socket
    m = nap_mau(dap_an()[6])
    goc_open, goc_io = builtins.open, io.open
    def chi_doc(ham):
        def mo(file, mode="r", *a, **kw):
            assert not any(c in mode for c in "wax+"), "Runtime đã mở tệp để ghi"
            return ham(file, mode, *a, **kw)
        return mo
    def cam(*a, **kw):
        pytest.fail("Runtime đã gọi mạng/chương trình ngoài CoreGia")
    monkeypatch.setattr(builtins, "open", chi_doc(goc_open))
    monkeypatch.setattr(io, "open", chi_doc(goc_io))
    monkeypatch.setattr(socket, "create_connection", cam)
    monkeypatch.setattr(subprocess, "Popen", cam)
    t, s, _, request, _ = local_va_xuat(m, nhan_va_so(m), nhan="can_xem")
    assert request and s["diem_lech"] and t["tep_json"]["tep_id"] and t["tep_pdf"]["tep_id"]
    for row in m.cac_luot():
        raw = hs.json_bytes(row.gia_tri).decode()
        assert dap_an()[6]["word"] not in raw and dap_an()[6]["ban_ky"] not in raw


def cong_cu_sach():
    import runpy
    return runpy.run_path(str(GOI.parents[1] / "cong-cu/kiem_may_sach.py"))


def test_may_sach_thieu_wheel_khong_tao_venv_hoac_tai_mang(tmp_path, monkeypatch, capsys):
    tool = cong_cu_sach()
    import venv
    from pip._vendor.packaging import tags
    host_tags = list(tags.sys_tags())  # Windows có thể hỏi lệnh ver khi đọc nền tảng.
    monkeypatch.setattr(tags, "sys_tags", lambda: iter(host_tags))
    def cam(*a, **kw):
        pytest.fail("Thiếu wheel/hash vẫn tạo venv hoặc gọi pip")
    monkeypatch.setattr(venv.EnvBuilder, "create", cam)
    monkeypatch.setattr(subprocess, "run", cam)
    assert tool["main"](["--wheelhouse", str(tmp_path), "--venv", str(tmp_path / "DEMO"), "--cai"]) == 2
    out = capsys.readouterr().out
    assert "THIEU wheel dung hash/tag: Pillow==12.3.0" in out
    assert "THIEU hash wheel duoc duyet: pytest==9.1.1" in out
    assert "CHUA KIEM may sach" in out and not (tmp_path / "DEMO").exists()


def test_may_sach_kiem_hash_va_tag_truoc_cai(tmp_path):
    tool = cong_cu_sach()
    from pip._vendor.packaging.tags import sys_tags
    sdk = GOI.parents[2] / "docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
    row = {"ten": "kho_tri_thuc_sdk", "phien_ban": "2.2.0", "hash": [sha256(sdk.read_bytes()).hexdigest()]}
    p = tmp_path / sdk.name
    p.write_bytes(sdk.read_bytes())
    kiem = tool["kiem_wheel"]
    assert kiem(row, tmp_path, set(sys_tags())) == (p, None)
    # Hash đúng nhưng không có tag của máy đích vẫn bị từ chối.
    assert kiem(row, tmp_path, set())[0] is None
    p.write_bytes(b"DEMO-wheel-da-bi-thay")
    assert kiem(row, tmp_path, set(sys_tags()))[0] is None


def test_hai_wrapper_ascii_va_khong_goi_mang():
    for name in ("KIEM-MAY-SACH.cmd", "kiem-may-sach.sh"):
        raw = (GOI.parents[1] / "cong-cu" / name).read_bytes()
        text = raw.decode("ascii")
        assert "kiem_may_sach.py" in text and "PYTHONDONTWRITEBYTECODE" in text
        assert "curl" not in text and "wget" not in text and "pip install" not in text
