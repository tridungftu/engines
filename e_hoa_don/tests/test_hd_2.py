"""HD-2: bàn giao thuần qua SDK, chỉ CoreGia/MayChuGia và dữ liệu DEMO."""

from hashlib import sha256
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener

import pytest
from kho_tri_thuc_sdk.engine import LoiDuongTruyen, Viec, ViecDaHuy
from kho_tri_thuc_sdk.engine_http import DuongHttp
from kho_tri_thuc_sdk.primitives import DataError
from kho_tri_thuc_sdk.thu import CoreGia, MayChuGia

import e_hoa_don.chay as cong

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_hoa_don"
NANG_LUC = "hoa_don.doc_xml@2"
TIEN_DO = [
    (10, "Đang đọc XML hóa đơn."),
    (60, "Đã đọc cấu trúc XML hóa đơn."),
    (80, "Đang lưu chi tiết nguồn hóa đơn."),
    (100, "Đã đọc XML hóa đơn; cần kiểm tra kết quả nguồn."),
]


@pytest.fixture(params=["bo_nho", "http"])
def kenh(request, cach_ly_demo):
    core = CoreGia()
    if request.param == "bo_nho":
        def chay(**tuy_chon):
            tuy_chon.setdefault("khoang_gia_han", 60)
            core.chay(cong.app, **tuy_chon)

        yield core, chay, None
        return
    # Khóa giả sinh lúc test, không có credential thật trong mã/kết quả/log.
    khoa = "DEMO-" + os.urandom(16).hex()
    with MayChuGia(core, {cong.app.ma: khoa}) as may:
        cach_ly_demo.add(("127.0.0.1", urlsplit(may.url).port))
        dt = DuongHttp(may.url, cong.app.ma, khoa, "HD-2-DEMO",
                       mo=build_opener(ProxyHandler({})))

        def chay(**tuy_chon):
            tuy_chon.setdefault("khoang_gia_han", 60)
            cong.app.chay(dt, dung_khi_het_viec=True, cho_gui_lai_giay=0, **tuy_chon)

        yield core, chay, may


def giao(core, raw, *, phap_nhan="phap-nhan-DEMO-A", gui_kem=True, ten="DEMO.xml"):
    tep = core.them_tep(ten, raw, "application/xml")
    viec_id = core.giao_viec(NANG_LUC, {"loai": "tep", "tep": tep},
                             phap_nhan_id=phap_nhan, gui_kem_dau_vao=gui_kem)
    return viec_id, tep


def bao_cao(core, kq):
    return json.loads(core.doc_tep(kq["ket_qua"]["truong"]["chi_tiet_nguon"]["tep_id"]))


def test_ban_giao_bytes_hash_va_tep_id_opaque(kenh, xml_demo, monkeypatch):
    core, chay, may = kenh
    raw = xml_demo + b"<!-- DEMO bytes goc -->\r\n"
    viec_id, tep = giao(core, raw, gui_kem=False)
    da_doc = []
    mo = Viec.mo_tep
    ham = cong.doc_hoa_don

    def doc(viec, tep_id):
        da_doc.append(tep_id)
        return mo(viec, tep_id)

    def giu_doi_tuong(viec):
        kq = ham(viec)
        assert kq["truong"]["tep_xml"] is viec.dau_vao["tep"]
        return kq

    monkeypatch.setattr(Viec, "mo_tep", doc)
    monkeypatch.setitem(cong.app._ham, NANG_LUC, giu_doi_tuong)
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "XONG" and kq["loi"] is None
    t = kq["ket_qua"]["truong"]
    assert da_doc == [tep["tep_id"]] and tep["tep_id"].startswith("tep-")
    assert t["tep_xml"] == tep
    assert core.doc_tep(tep["tep_id"]) == raw
    assert t["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()
    report = bao_cao(core, kq)
    assert report["tep_xml"] == tep
    assert report["bam_dau_vao"] == t["bam_dau_vao"]
    assert report["chi_tiet_nguon"]["raw_ref"]["native_sha256"] == sha256(raw).hexdigest()
    assert report["chi_tiet_nguon"]["raw_ref"]["byte_length"] == len(raw)
    assert "raw_xml" not in report["chi_tiet_nguon"]
    assert t["chi_tiet_nguon"]["tep_id"] not in json.dumps(report)
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1
    assert kq["tien_do"] == TIEN_DO
    if may:
        assert any(x["duong"].endswith("/dau-vao") for x in may.cac_loi_goi)
        assert all(x["co_bearer"] and x["instance"] == "HD-2-DEMO" for x in may.cac_loi_goi)


@pytest.mark.parametrize("thao_tac", ["tep", "ket_qua", "ket_thuc"])
@pytest.mark.parametrize("so_lan", [1, 3])
def test_mat_xac_nhan_sdk_gui_lai_cung_khoa_khong_trung(kenh, xml_demo, thao_tac, so_lan):
    core, chay, may = kenh
    viec_id, tep = giao(core, xml_demo)
    core.gay_mat_xac_nhan(thao_tac, so_lan)
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "XONG" and kq["ket_qua"] is not None
    assert core.doc_tep(tep["tep_id"]) == xml_demo
    for op in ("tep", "ket_qua", "ket_thuc"):
        assert core.so_lan_ghi[op] == 1
        calls = [n for n in core.nhat_ky if n[0] == op]
        assert len(calls) == (so_lan + 1 if op == thao_tac else 1)
        assert len({n[3] for n in calls}) == 1
    assert len(core._tep) == 2  # Một XML vào + một JSON ra, kể cả mất ACK.
    assert bao_cao(core, kq)["chi_tiet_nguon"]["business_promotion"] == "NOT_PERFORMED"
    if may:
        duoi = {"tep": "/tep", "ket_qua": "/ket-qua", "ket_thuc": "/ket-thuc"}[thao_tac]
        calls = [x for x in may.cac_loi_goi if x["duong"].endswith(duoi)]
        assert len(calls) == so_lan + 1
        assert len({x["idempotency_key"] for x in calls}) == 1
        assert all(x["idempotency_key"] for x in calls)


@pytest.mark.parametrize("loi_tam", [False, True])
def test_upload_that_bai_khong_id_thay_khong_xong(kenh, xml_demo, monkeypatch, loi_tam, capsys):
    core, chay, _ = kenh
    viec_id, _ = giao(core, xml_demo)
    calls = []

    def hong(ma, viec, ten, raw, mime, khoa):
        calls.append(khoa)
        raise LoiDuongTruyen("DEMO_UPLOAD_LOI", "DEMO-CANARY-UPLOAD /DEMO/secret",
                             http_status=503 if loi_tam else 403, thu_lai_duoc=loi_tam)

    monkeypatch.setattr(core, "_tai_tep_ra", hong)
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"]["ma"] == "KHONG_TRAO_DOI_DUOC_CORE"
    assert kq["ma_tuong_quan"] is None
    assert len(calls) == (4 if loi_tam else 1) and len(set(calls)) == 1
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    assert core.so_lan_ghi["ket_thuc"] == 1 and len(core._tep) == 1
    assert "DEMO-CANARY" not in capsys.readouterr().err + json.dumps(kq["loi"])


@pytest.mark.parametrize("phan_hoi", [None, {}, {"tep_id": ""}, {"tep_id": 12}])
def test_upload_thieu_tham_chieu_core_khong_cap_id(kenh, xml_demo, monkeypatch, phan_hoi):
    core, chay, _ = kenh
    viec_id, _ = giao(core, xml_demo)
    monkeypatch.setattr(core, "_tai_tep_ra", lambda *a, **kw: phan_hoi)
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["ma_tuong_quan"] is None and core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("moc", [10, 60, 80, 100])
def test_huy_o_bon_moc_khong_nop(kenh, xml_demo, monkeypatch, moc):
    core, chay, _ = kenh
    viec_id, _ = giao(core, xml_demo)
    tien_do = core._tien_do
    mo = core._mo_tep
    da_doc = []

    def doc(*args):
        da_doc.append(True)
        return mo(*args)

    def huy(ma, viec, phan_tram, cau):
        if phan_tram == moc:
            core.huy(viec)
        return tien_do(ma, viec, phan_tram, cau)

    monkeypatch.setattr(core, "_mo_tep", doc)
    monkeypatch.setattr(core, "_tien_do", huy)
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None and kq["loi"] is None
    assert kq["tien_do"] == [x for x in TIEN_DO if x[0] <= moc]
    assert bool(da_doc) is (moc != 10)
    assert core.so_lan_ghi["tep"] == (1 if moc == 100 else 0)
    assert core.so_lan_ghi["ket_qua"] == 0 and core.so_lan_ghi["ket_thuc"] == 1


@pytest.mark.parametrize("status", [409, 404, 410])
@pytest.mark.parametrize("moc", [10, 60, 80, 100, "doc", "upload"])
def test_mat_lease_dung_khong_nop_khong_ket_thuc(kenh, xml_demo, monkeypatch, status, moc):
    core, chay, _ = kenh
    viec_id, _ = giao(core, xml_demo)
    calls = []

    def mat_lease():
        calls.append(True)
        raise LoiDuongTruyen("MAT_LEASE", "DEMO-CANARY-LEASE", http_status=status)

    if moc == "doc":
        monkeypatch.setattr(core, "_mo_tep", lambda *a: mat_lease())
    elif moc == "upload":
        monkeypatch.setattr(core, "_tai_tep_ra", lambda *a, **kw: mat_lease())
    else:
        tien_do = core._tien_do

        def loi(ma, viec, phan_tram, cau):
            if phan_tram == moc:
                return mat_lease()
            return tien_do(ma, viec, phan_tram, cau)

        monkeypatch.setattr(core, "_tien_do", loi)
    chay()
    kq = core.xem(viec_id)
    assert calls == [True]  # Không retry lỗi lease.
    assert kq["trang_thai"] == "DANG_CHAY" and kq["ket_qua"] is None
    assert kq["loi"] is None and kq["ma_tuong_quan"] is None
    assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 0
    assert core.so_lan_ghi["tep"] == (1 if moc == 100 else 0)


def test_ten_chi_metadata_khong_mo_duong_dan(kenh, xml_demo, tmp_path):
    core, chay, _ = kenh
    ngoai_kho = tmp_path / "DEMO-ngoai-kho.xml"
    ngoai_kho.write_bytes(b"DEMO-CANARY-KHONG-DUOC-DOC")
    viec_id, tep = giao(core, xml_demo, ten=str(ngoai_kho))
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "XONG"
    assert kq["ket_qua"]["truong"]["tep_xml"] == tep
    assert kq["ket_qua"]["truong"]["bam_dau_vao"] == "sha256:" + sha256(xml_demo).hexdigest()
    assert ngoai_kho.read_bytes() == b"DEMO-CANARY-KHONG-DUOC-DOC"


def test_tep_id_khong_ton_tai_khong_doc_theo_ten(kenh, xml_demo, tmp_path):
    core, chay, _ = kenh
    ngoai_kho = tmp_path / "DEMO.xml"
    ngoai_kho.write_bytes(xml_demo)
    tep = {"tep_id": "DEMO-khong-trong-kho", "ten": str(ngoai_kho),
           "mime": "application/xml", "kich_thuoc": len(xml_demo)}
    viec_id = core.giao_viec(NANG_LUC, {"loai": "tep", "tep": tep})
    chay()
    kq = core.xem(viec_id)
    assert kq["ket_qua"] is None and kq["trang_thai"] == "DANG_CHAY"
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 0


def test_hai_phap_nhan_cung_xml_khong_cache_khong_nhan_nghiep_vu(kenh, xml_demo, monkeypatch, tmp_path):
    core, chay, _ = kenh
    monkeypatch.setenv("KTT_ENGINE_DU_LIEU", str(tmp_path / "kho-DEMO-khong-duoc-tao"))
    doc_xml = cong.doc_xml
    calls = []

    def doc(raw, **kwargs):
        calls.append(raw)
        return doc_xml(raw, **kwargs)

    monkeypatch.setattr(cong, "doc_xml", doc)
    a, tep_a = giao(core, xml_demo, phap_nhan="phap-nhan-DEMO-A")
    b, tep_b = giao(core, xml_demo, phap_nhan="phap-nhan-DEMO-B")
    chay()
    ka, kb = core.xem(a), core.xem(b)
    assert ka["trang_thai"] == kb["trang_thai"] == "XONG" and calls == [xml_demo, xml_demo]
    ta, tb = ka["ket_qua"]["truong"], kb["ket_qua"]["truong"]
    assert ta["tep_xml"] == tep_a and tb["tep_xml"] == tep_b
    assert ta["chi_tiet_nguon"]["tep_id"] != tb["chi_tiet_nguon"]["tep_id"]
    assert ta["bam_dau_vao"] == tb["bam_dau_vao"]
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 2
    for kq in (ka, kb):
        detail = bao_cao(core, kq)["chi_tiet_nguon"]
        assert detail["native_fiscal_status"] == "UNKNOWN"
        assert detail["business_promotion"] == "NOT_PERFORMED"
        assert detail["canonical_identity"] is detail["semantic_digest"] is None
    assert not (tmp_path / "kho-DEMO-khong-duoc-tao").exists()


@pytest.mark.parametrize("status", [None, 409, 404, 410])
def test_sdk_gia_han_bao_huy_mat_lease_trong_luc_parse(kenh, xml_demo, monkeypatch, status):
    core, chay, _ = kenh
    viec_id, _ = giao(core, xml_demo)
    da_gia_han = threading.Event()
    doc_xml = cong.doc_xml
    viec_dang_chay = []

    def xu_ly(viec):
        viec_dang_chay.append(viec)
        return cong.doc_hoa_don(viec)

    def gia_han(ma, viec, giay):
        da_gia_han.set()
        if status is not None:
            raise LoiDuongTruyen("MAT_LEASE", "Mất lease DEMO.", http_status=status)
        core.huy(viec)
        return {"huy": True, "han_giu": core._han(60)}

    def doc(*args, **kwargs):
        assert da_gia_han.wait(5), "SDK phải gia hạn trong lúc hàm đang xử lý."
        assert viec_dang_chay[0]._huy.wait(5), "Đợi SDK nhận tín hiệu, không dựa thời gian ngủ."
        return doc_xml(*args, **kwargs)

    monkeypatch.setitem(cong.app._ham, NANG_LUC, xu_ly)
    monkeypatch.setattr(core, "_gia_han", gia_han)
    monkeypatch.setattr(cong, "doc_xml", doc)
    chay(khoang_gia_han=0.01)
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == ("HUY" if status is None else "DANG_CHAY")
    assert kq["ket_qua"] is None and kq["loi"] is None
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0
    assert core.so_lan_ghi["ket_thuc"] == (1 if status is None else 0)


def test_giao_lai_cung_viec_chay_thuan_khong_ghi_nhan(kenh, xml_demo, monkeypatch):
    core, chay, _ = kenh
    viec_id, tep = giao(core, xml_demo)
    tien_do = core._tien_do

    def mat_lease(ma, viec, phan_tram, cau):
        if phan_tram == 60:
            raise LoiDuongTruyen("MAT_LEASE", http_status=409)
        return tien_do(ma, viec, phan_tram, cau)

    monkeypatch.setattr(core, "_tien_do", mat_lease)
    chay()
    assert core.xem(viec_id)["lan_thu"] == 1
    assert core.xem(viec_id)["ket_qua"] is None
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_thuc"] == 0
    # CoreGia 2.0.0 chưa có API giả lập hết lease/giao lại công khai.
    # Chỉ seam test sửa hàng việc giả; engine không chạm ngăn hay lease.
    with core._lock:
        core._viec[viec_id].update(trang_thai="CHO", ma_engine=None)
        core._hang.append(viec_id)
    monkeypatch.setattr(core, "_tien_do", tien_do)
    chay()
    kq = core.xem(viec_id)
    assert kq["lan_thu"] == 2 and kq["trang_thai"] == "XONG"
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1
    assert core.doc_tep(tep["tep_id"]) == xml_demo
    detail = bao_cao(core, kq)["chi_tiet_nguon"]
    assert detail["business_promotion"] == "NOT_PERFORMED"
    assert detail["canonical_identity"] is detail["semantic_digest"] is None


@pytest.mark.parametrize("loai", ["hong", "namespace", "doctype", "invariant", "upload"])
def test_canary_demo_khong_lo_stderr_loi_tien_do(kenh, xml_demo, monkeypatch, capsys, loai):
    core, chay, _ = kenh
    canary = "DEMO-CANARY-NOI-DUNG"
    if loai == "hong":
        raw = b"<HDon>DEMO-CANARY-NOI-DUNG"
    elif loai == "namespace":
        raw = b'<HDon xmlns="urn:DEMO-CANARY-NOI-DUNG"/>'
    elif loai == "doctype":
        raw = b'<!DOCTYPE HDon SYSTEM "file:///DEMO-CANARY-NOI-DUNG"><HDon/>'
    else:
        raw = xml_demo.replace(b"0000123", b"000099999123").replace(
            b"0100000001", b"0109999999").replace(b"1000000", b"987654321")

    def invariant(*args, **kwargs):
        raise DataError("DEMO_INVARIANT", canary + " /DEMO/secret")

    def upload(*args, **kwargs):
        raise LoiDuongTruyen("DEMO_UPLOAD_LOI", canary + " /DEMO/secret", http_status=403)

    if loai == "invariant":
        monkeypatch.setattr(cong, "doc_xml", invariant)
    elif loai == "upload":
        monkeypatch.setattr(core, "_tai_tep_ra", upload)
    viec_id, _ = giao(core, raw, ten="DEMO-CANARY-NOI-DUNG.xml")
    chay()
    kq = core.xem(viec_id)
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["ma_tuong_quan"] is None
    dau_ra = capsys.readouterr()
    xem_duoc = dau_ra.err + dau_ra.out + json.dumps([kq["loi"], kq["tien_do"]])
    for cam in (canary, "000099999123", "0109999999", "987654321", "/DEMO/secret", "Traceback", "chay.py"):
        assert cam not in xem_duoc
    assert set(dau_ra.err.splitlines()) <= {"[engine e_hoa_don] HD_SDK_THONG_BAO"}
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("luc", ["doc", "parse", "upload"])
def test_handler_khong_bat_mat_tin_hieu_huy(xml_demo, monkeypatch, luc):
    tin_hieu = ViecDaHuy()

    def huy(*args, **kwargs):
        raise tin_hieu

    class ViecDemo:
        dau_vao = {"tep": {"tep_id": "DEMO-khong-uuid"}}

        def kiem_huy(self):
            pass

        def tien_do(self, *args):
            pass

        def mo_tep(self, *args):
            return huy() if luc == "doc" else io.BytesIO(xml_demo)

        def tai_tep_ra(self, *args):
            return huy()

    if luc == "parse":
        monkeypatch.setattr(cong, "doc_xml", huy)
    with pytest.raises(ViecDaHuy) as exc:
        cong.doc_hoa_don(ViecDemo())
    assert exc.value is tin_hieu


@pytest.mark.parametrize("diem_vao", ["app", "module"])
def test_app_chay_mot_dong_stdin_qua_may_chu_gia(xml_demo, diem_vao):
    core = CoreGia()
    viec_id, tep = giao(core, xml_demo, gui_kem=False)
    da_ket_thuc = threading.Event()
    ket_thuc = core._ket_thuc

    def ghi_ket_thuc(*args, **kwargs):
        kq = ket_thuc(*args, **kwargs)
        da_ket_thuc.set()
        return kq

    core._ket_thuc = ghi_ket_thuc
    khoa = "DEMO-" + os.urandom(16).hex()
    with MayChuGia(core, {cong.app.ma: khoa}) as may:
        env = {k: v for k, v in os.environ.items()
               if not k.startswith("KTT_") and k not in {"PYTHONPATH", "PYTHONHOME"}}
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", NO_PROXY="127.0.0.1")
        lenh = [sys.executable, "-B"]
        if diem_vao == "app":
            lenh += ["-c", "from e_hoa_don.chay import app; app.chay(dung_khi_het_viec=True)"]
        else:
            lenh += ["-m", "e_hoa_don.chay"]
        proc = subprocess.Popen(lenh, cwd=GOI, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            dong = json.dumps({"core_url": may.url, "khoa": khoa, "instance": "HD-2-STDIN-DEMO"}) + "\n"
            proc.stdin.write(dong.encode("utf-8"))
            proc.stdin.flush()
            # Giữ stdin mở: SDK phải bắt đầu sau đúng một dòng, không đợi EOF.
            assert da_ket_thuc.wait(10), "app.chay phải đọc một dòng stdin rồi xử lý việc."
            if diem_vao == "app":
                proc.wait(timeout=10)
                assert proc.returncode == 0
            else:
                # Entry point thật chạy liên tục; dừng tiến trình DEMO sau bàn giao.
                proc.terminate()
                proc.wait(timeout=10)
            out, err = proc.communicate(timeout=5)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=5)
        kq = core.xem(viec_id)
        assert kq["trang_thai"] == "XONG" and kq["ket_qua"]["truong"]["tep_xml"] == tep
        assert core.doc_tep(tep["tep_id"]) == xml_demo
        assert bao_cao(core, kq)["chi_tiet_nguon"]["business_promotion"] == "NOT_PERFORMED"
        assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["ket_thuc"] == 1
        assert out == err == b"" and khoa.encode() not in out + err
        assert all(x["co_bearer"] and x["instance"] == "HD-2-STDIN-DEMO" for x in may.cac_loi_goi)


def test_stderr_loi_invariant_khong_lo_canary(xml_demo, monkeypatch, capsys):
    def hong(*args, **kwargs):
        raise RuntimeError("DEMO-CANARY-NOI-DUNG /DEMO-CANARY-DUONG-DAN")

    monkeypatch.setattr(cong, "doc_xml", hong)
    core = CoreGia()
    tep = core.them_tep("DEMO-CANARY-TEN.xml", xml_demo, "application/xml")
    kq = core.chay_thu(cong.app, "hoa_don.doc_xml@2", {"loai": "tep", "tep": tep})
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None
    assert kq["loi"] == {
        "ma": "ENGINE_LOI_XU_LY", "thong_diep": "Engine gặp lỗi khi xử lý việc này.",
        "thu_lai_duoc": False,
    }
    dau_ra = capsys.readouterr()
    assert "DEMO-CANARY" not in dau_ra.err + dau_ra.out + json.dumps(kq["loi"])
    assert "Traceback" not in dau_ra.err and "chay.py" not in dau_ra.err
    assert core.so_lan_ghi["tep"] == core.so_lan_ghi["ket_qua"] == 0


def test_sdk_ghim_va_thieu_hook_khong_khoi_dong():
    import kho_tri_thuc_sdk
    assert kho_tri_thuc_sdk.__version__ == "2.0.0"
    ma = "from kho_tri_thuc_sdk.engine import Engine; del Engine._ghi; import e_hoa_don.chay"
    kq = subprocess.run([sys.executable, "-B", "-c", ma], cwd=GOI,
                        capture_output=True, text=True, encoding="utf-8")
    assert kq.returncode != 0
    assert "SDK không có hook nhật ký" in kq.stderr
