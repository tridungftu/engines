"""PL-5 tích hợp: đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO.

Phong bì AI dựng tay, giữ nguyên chuyển tiếp của bước chuẩn bị. Kiểm
riêng hình dạng Core thật; CoreGia chưa chứng nhận quyền/cùng việc.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import runpy
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import Viec
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chuoi_ai, ngan_chuoi, quy_trinh
from e_phan_luong.chay import app
from e_phan_luong.doc_lo import doc_lo_json
from e_phan_luong.loi import CAU_LOI

TESTS = Path(__file__).resolve().parent
REPO = TESTS.parents[1]
DEMO = TESTS / "demo"


def doc_demo(ten):
    return json.loads((DEMO / ten).read_text(encoding="utf-8"))


def tham_so(**doi):
    yc = doc_demo("yeu-cau-ai-DEMO.json")["yeu_cau_ai"]
    return {
        "khau": "ktt_duyet", "truong_phan_loai": "dien_giai",
        "danh_muc_loai_json": (DEMO / "danh-muc-loai-DEMO.json").read_text(encoding="utf-8"),
        "bo_phan_loai_json": (DEMO / "bo-phan-loai-DEMO.json").read_text(encoding="utf-8"),
        **{k: yc[k] for k in ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien")},
        **doi,
    }


def lo_demo(noi_dung=None):
    lo = {"phien_ban": 1, "ma_module": "demo_thanh_toan", "ky": "2026-11",
          "nguong": doc_demo("nguong-DEMO.json"), "nghiep_vu": []}
    if noi_dung is None:
        noi_dung = ["Nội dung ZZZ DEMO chưa xác định"]
    for i, chu in enumerate(noi_dung):
        lo["nghiep_vu"].append({
            "ma": f"PC-DEMO-{i:05}", "ngay": "2026-11-16", "loai": None,
            "so_tien": {"so": "1000000", "tien_te": "VND"}, "dien_giai": chu,
        })
    return lo


def bytes_lo(lo):
    return lo if isinstance(lo, bytes) else json.dumps(lo, ensure_ascii=False).encode("utf-8")


def chuan_bi(core, lo=None, ts=None, *, ten="lo-DEMO.json", mime="application/json"):
    raw = bytes_lo(lo_demo() if lo is None else lo)
    tep = core.them_tep(ten, raw, mime)
    kq = core.chay_thu(app, "audit.chuan_bi_phan_loai@1", {"loai": "tep", "tep": tep},
                       tham_so() if ts is None else ts)
    return kq, raw, tep


def yeu_cau(core, lo=None, ts=None, **kw):
    kq, raw, tep = chuan_bi(core, lo, ts, **kw)
    assert kq["trang_thai"] == "XONG", kq
    return kq["ket_qua"], raw, tep


def ai_gia(yc, ten="tra-loi-ai-dung-enum.json"):
    pb = doc_demo(ten)
    pb["tra_loi_ai"]["chuyen_tiep"] = deepcopy(yc["yeu_cau_ai"]["chuyen_tiep"])
    return pb


def chay_sau(core, pb, ts=None):
    cac_o = {o["ma"] for n in app.phieu["nang_luc"] if n["ma"] == "audit.phan_luong_sau_ai@1"
             for o in n["tham_so"]}
    ts = tham_so() if ts is None else ts
    return core.chay_thu(app, "audit.phan_luong_sau_ai@1", pb,
                         {k: v for k, v in ts.items() if k in cac_o})


def ket_qua(core, kq):
    assert kq["trang_thai"] == "XONG", kq
    truong = kq["ket_qua"]["truong"]
    tep = json.loads(core.doc_tep(truong["tep_json"]["tep_id"]))
    return truong, tep


def kiem_loi(core, kq, ma="CHUOI_KHONG_KHOP"):
    assert kq["trang_thai"] == "LOI", kq
    assert kq["loi"] == {"ma": ma, "thong_diep": CAU_LOI[ma], "thu_lai_duoc": False}
    assert core.xem_ngan(app.ma, "luot") == []
    assert core.xem_ngan(app.ma, "dong_luot") == []


def kiem_c5(truong, tep):
    def quet(nut):
        if isinstance(nut, dict):
            for khoa, gia_tri in nut.items():
                assert not any(chu in khoa for chu in ("ty_le", "xac_suat", "tin_cay", "bac"))
                assert khoa not in {"p", "hat_giong", "he_so", "san"}
                quet(gia_tri)
        elif isinstance(nut, list):
            for gia_tri in nut:
                quet(gia_tri)
    quet(truong)
    quet(tep)
    assert len(truong["canh_bao"]) <= 500
    assert not any(chu in truong["canh_bao"].casefold() for chu in
                   ("%", "tỷ lệ", "xác suất", "bậc", "tin cậy", "0.9", "0.4"))


def co_dung_tham_chieu(nut, tep_id):
    if isinstance(nut, dict):
        return nut.get("tep_id") == tep_id or any(
            co_dung_tham_chieu(v, tep_id) for v in nut.values())
    if isinstance(nut, list):
        return any(co_dung_tham_chieu(v, tep_id) for v in nut)
    return False


def test_chuan_bi_giu_nguyen_bytes_ten_mime_bam_va_khong_ghi_ngan(monkeypatch):
    core = CoreGia()
    cac_tep = []
    tai_goc = Viec.tai_tep_ra

    def tai(viec, ten, raw, mime):
        tep = tai_goc(viec, ten, raw, mime)
        cac_tep.append((ten, raw, mime, tep))
        return tep

    monkeypatch.setattr(Viec, "tai_tep_ra", tai)
    # BOM, khoảng trắng và CRLF phải giữ nguyên từng byte, không chuẩn hóa lô.
    raw = b"\xef\xbb\xbf \r\n" + bytes_lo(lo_demo()) + b"\r\n"
    yc, _, tep_vao = yeu_cau(core, raw, ten="Lo-Goc-DEMO.JSON", mime="application/json")
    ct = yc["yeu_cau_ai"]["chuyen_tiep"]
    pl = ct["phan_luong"]
    assert len(cac_tep) == 1
    assert cac_tep[0][:3] == ("Lo-Goc-DEMO.JSON", raw, "application/json")
    assert pl["tep_lo"] == cac_tep[0][3] and pl["tep_lo"] != tep_vao
    assert core.doc_tep(pl["tep_lo"]["tep_id"]) == raw
    assert len(json.dumps(ct, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()) <= 4096
    assert pl["bam_tep"] == "sha256:" + sha256(raw).hexdigest()
    assert pl["bam_tai_lieu"] == "sha256:" + sha256(yc["yeu_cau_ai"]["tai_lieu"].encode()).hexdigest()
    assert pl["bam_cai_dat"] == chuoi_ai.bam_cai_dat(tham_so())
    assert all(core.xem_ngan(app.ma, b["bang"]) == [] for b in app.phieu["ngan_du_lieu"])
    # Kiểm envelope theo schema nguồn, không chỉ theo tên loại của SDK.
    jsonschema = pytest.importorskip(
        "jsonschema", reason="Kiểm schema nguồn cần jsonschema (chỉ dùng trong test, không thuộc gói).")
    schema = json.loads((REPO / "_chung/contract/yeu_cau_ai.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(yc)


@pytest.mark.parametrize("ten,la_ai,loi", [
    ("tra-loi-ai-dung-enum.json", True, None),
    ("tra-loi-ai-sai-enum.json", False, None),
    ("tra-loi-ai-tin-cay-thap.json", False, None),
    ("tra-loi-ai-cloud.json", False, "KHONG_PHAI_LOCAL"),
    ("tra-loi-ai-khong-thay-can-cu.json", False, None),
])
def test_noi_hai_buoc_voi_nam_phong_bi_ai_demo(monkeypatch, ten, la_ai, loi):
    core = CoreGia()
    mo_goc = core._mo_tep

    def mo_nghiem(ma, viec_id, tep_id, toi_da):
        # CoreGia mặc định chỉ so chuỗi con; bổ sung điều kiện hình dạng Core thật.
        assert co_dung_tham_chieu(core._dang_giu(ma, viec_id)["dau_vao"], tep_id)
        return mo_goc(ma, viec_id, tep_id, toi_da)

    monkeypatch.setattr(core, "_mo_tep", mo_nghiem)
    goc = "Nội dung ZZZ DEMO chưa xác định"
    lo = lo_demo(["DEMO đã có loại", "Thanh toán DEMO", goc,
                  "  " + unicodedata.normalize("NFD", goc) + "\t", "  "])
    lo["nghiep_vu"][0]["loai"] = "luong"
    yc, raw, _ = yeu_cau(core, lo)
    tai_lieu = json.loads(yc["yeu_cau_ai"]["tai_lieu"])
    assert tai_lieu == [{"chi_so": 0, "noi_dung": goc}]
    pb = ai_gia(yc, ten)
    ct_cu = deepcopy(pb["tra_loi_ai"]["chuyen_tiep"])
    kq = chay_sau(core, pb)
    assert pb["tra_loi_ai"]["chuyen_tiep"] == ct_cu
    if loi:
        kiem_loi(core, kq, loi)
        return
    truong, tep = ket_qua(core, kq)
    dong = tep["nghiep_vu"]
    assert [(d["loai"], d["nguon_loai"]) for d in dong[:2]] == [
        ("luong", "module"), ("thanh_toan_ncc", "quy_tac")]
    mong = ("chi_phi_khac", "ai") if la_ai else ("chua_phan_loai", "chua_phan_loai")
    assert [(d["loai"], d["nguon_loai"]) for d in dong[2:4]] == [mong, mong]
    assert dong[4]["loai"] == "chua_phan_loai"
    assert truong["so_chua_phan_loai"] == (1 if la_ai else 3)
    if not la_ai:
        assert truong["canh_bao"]
    assert truong["bam_dau_vao"] == "sha256:" + sha256(raw).hexdigest()
    assert len(core.xem_ngan(app.ma, "luot")) == 1
    assert len(core.xem_ngan(app.ma, "dong_luot")) == 5
    kiem_c5(truong, tep)


@pytest.mark.parametrize("du_lieu", [None, {}, {"phan_loai": "DEMO"},
    {"phan_loai": [{"chi_so": 0, "loai": "chi_phi_khac", "tin_cay": True}]}])
def test_ai_sai_khuon_chi_canh_bao_khong_loi_luot(du_lieu):
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    pb = ai_gia(yc)
    pb["tra_loi_ai"]["du_lieu"] = du_lieu
    truong, tep = ket_qua(core, chay_sau(core, pb))
    assert truong["so_chua_phan_loai"] == 1 and truong["canh_bao"]
    kiem_c5(truong, tep)


def test_doi_mot_byte_tu_choi_truoc_khi_doc_lai_lo(monkeypatch):
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    tep_id = yc["yeu_cau_ai"]["chuyen_tiep"]["phan_luong"]["tep_lo"]["tep_id"]
    mo_goc = core._mo_tep

    def mo(*a):
        raw = mo_goc(*a)
        return bytes([raw[0] ^ 1]) + raw[1:] if a[2] == tep_id else raw

    monkeypatch.setattr(core, "_mo_tep", mo)
    monkeypatch.setattr(ngan_chuoi, "doc_lo_chuyen_tiep", lambda *a: pytest.fail("Không đọc lô sai băm."))
    kiem_loi(core, chay_sau(core, ai_gia(yc)))


@pytest.mark.parametrize("khoa,gia_tri", [
    ("danh_muc_loai_json", "[]"), ("bo_phan_loai_json", "{DEMO sai JSON}"),
    ("truong_phan_loai", "tai_khoan_no"), ("khuon_cot_json", "{}"), ("khau", "cfo_duyet"),
])
def test_doi_cai_dat_giua_hai_buoc_tu_choi_chuoi(khoa, gia_tri):
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    kiem_loi(core, chay_sau(core, ai_gia(yc), tham_so(**{khoa: gia_tri})))


@pytest.mark.parametrize("khoa,gia_tri", [
    ("bam_tai_lieu", "sha256:" + "1" * 64), ("bam_cai_dat", "sha256:" + "2" * 64),
    ("bam_tep", "sha256:" + "3" * 64), ("khong_can_ai", True),
])
def test_doi_bam_hoac_co_khong_can_ai_tu_choi(khoa, gia_tri):
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    pb = ai_gia(yc)
    pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"][khoa] = gia_tri
    kiem_loi(core, chay_sau(core, pb))


def test_thieu_ca_hai_bam_phan_ghep_khong_chap_nhan():
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    pb = ai_gia(yc)
    pl = pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"]
    for k in ("bam_cai_dat", "bam_tai_lieu"):
        del pl[k]
    kiem_loi(core, chay_sau(core, pb))


def test_chuyen_tiep_chuoi_tep_id_tu_choi_truoc_mo_tep(monkeypatch):
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    pb = ai_gia(yc)
    pl = pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"]
    pl["tep_lo"] = pl["tep_lo"]["tep_id"]
    monkeypatch.setattr(Viec, "mo_tep", lambda *a: pytest.fail("Phải kiểm hình dạng trước khi mở."))
    kiem_loi(core, chay_sau(core, pb))


def test_tep_chuyen_tiep_mat_tra_ma_loi_chuoi():
    core = CoreGia()
    yc, _, _ = yeu_cau(core)
    pl = yc["yeu_cau_ai"]["chuyen_tiep"]["phan_luong"]
    core._tep.pop(pl["tep_lo"]["tep_id"])
    kiem_loi(core, chay_sau(core, ai_gia(yc)))


@pytest.mark.parametrize("noi_dung", [[], ["  "], ["Thanh toán DEMO"], ["Đ" * 2001]])
def test_khong_dong_nao_can_ai_van_kiem_chuoi_va_bo_qua_ai(monkeypatch, noi_dung):
    core = CoreGia()
    yc, _, _ = yeu_cau(core, lo_demo(noi_dung))
    assert yc["yeu_cau_ai"]["tai_lieu"] == ""
    assert yc["yeu_cau_ai"]["chuyen_tiep"]["phan_luong"]["khong_can_ai"] is True
    monkeypatch.setattr(chuoi_ai, "doc_tra_loi_ai", lambda *a, **kw: pytest.fail("Không cần AI."))
    pb = ai_gia(yc, "tra-loi-ai-cloud.json")
    pb["tra_loi_ai"]["du_lieu"] = None
    truong, tep = ket_qua(core, chay_sau(core, pb))
    assert truong["so_nghiep_vu"] == len(noi_dung)
    if noi_dung and len(noi_dung[0]) > 2000:
        assert "1 dòng" in truong["canh_bao"]
    kiem_c5(truong, tep)


def test_khong_can_ai_nhung_tep_sai_bam_van_tu_choi():
    core = CoreGia()
    yc, _, _ = yeu_cau(core, lo_demo([]))
    pb = ai_gia(yc)
    pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"]["bam_tep"] = "sha256:" + "0" * 64
    kiem_loi(core, chay_sau(core, pb))


def test_tran_tong_500000_ky_tu_dem_dong_bo_khong_cat_noi_dung():
    core = CoreGia()
    # Dấu nháy/backslash làm chuỗi JSON dài hơn tổng nội dung thô.
    noi_dung = [f"DEMO-{i:04} " + '\\"Đ' * 500 for i in range(400)]
    noi_dung.extend([noi_dung[-1], "Đ" * 2001])
    yc, _, _ = yeu_cau(core, lo_demo(noi_dung))
    van_ban = yc["yeu_cau_ai"]["tai_lieu"]
    assert len(van_ban) <= 500000
    ds = json.loads(van_ban)
    assert 0 < len(ds) < 400
    assert [m["noi_dung"] for m in ds] == noi_dung[:len(ds)]
    # Thêm đúng tài liệu kế tiếp thì vượt trần: không cắt nội dung để nhét.
    them = ds + [{"chi_so": len(ds), "noi_dung": noi_dung[len(ds)]}]
    assert len(chuoi_ai.van_ban_tai_lieu(them)) > 500000
    pb = ai_gia(yc)
    pb["tra_loi_ai"]["du_lieu"]["phan_loai"] = [
        {"chi_so": m["chi_so"], "loai": "chi_phi_khac", "tin_cay": 0.9} for m in ds]
    truong, tep = ket_qua(core, chay_sau(core, pb))
    so_bo = len(noi_dung) - len(ds)
    assert truong["so_chua_phan_loai"] == so_bo
    assert f"{so_bo} dòng" in truong["canh_bao"]
    assert all(d["nguon_loai"] == "ai" for d in tep["nghiep_vu"][:len(ds)])
    kiem_c5(truong, tep)


def test_doc_lo_chuyen_tiep_dung_diem_noi_pl6_va_bytes_da_kiem(monkeypatch):
    core = CoreGia()
    yc, raw, _ = yeu_cau(core)
    pb = ai_gia(yc)
    pl = pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"]
    # Cổng PL-6 được thử riêng: lựa chọn bộ đọc phụ thuộc metadata gốc.
    pl["tep_lo"].update(ten="bang-DEMO.csv", mime="text/csv")
    da_goi = []

    def doc(viec):
        assert viec.dau_vao == {"loai": "tep", "tep": pl["tep_lo"]}
        assert viec.tham_so["khau"] == "ktt_duyet"
        with viec.mo_tep(pl["tep_lo"]["tep_id"]) as tep:
            assert tep.read() == raw
        da_goi.append(True)
        return doc_lo_json(raw), raw

    monkeypatch.setattr(quy_trinh, "doc_tep_lo", doc)
    ket_qua(core, chay_sau(core, pb))
    assert da_goi == [True]


def test_bat_dau_o_dau_ca_hai_nang_luc(monkeypatch):
    core, da_goi = CoreGia(), []
    monkeypatch.setattr(quy_trinh, "bat_dau", lambda v: da_goi.append(True))
    yc, _, _ = yeu_cau(core)
    ket_qua(core, chay_sau(core, ai_gia(yc)))
    assert da_goi == [True, True]


def test_thieu_prompt_tu_choi_truoc_tai_tep(monkeypatch):
    core = CoreGia()
    monkeypatch.setattr(Viec, "tai_tep_ra", lambda *a: pytest.fail("Chưa đủ prompt."))
    kq, _, _ = chuan_bi(core, ts=tham_so(prompt=""))
    kiem_loi(core, kq, "THAM_SO_KHONG_HOP_LE")


def test_chuoi_mau_dung_ham_kiem_cua_script_danh_muc():
    ma = runpy.run_path(str(REPO / "_chung/cong-cu/sinh_danh_muc_engine.py"))
    kiem = ma["kiem_chuoi"]
    # Chỉ kiểm chuỗi PL-5 trong test; lead thêm CHUOI ở script chung khi gộp.
    cu = kiem.__globals__["CHUOI"]
    try:
        kiem.__globals__["CHUOI"] = [("Phân luồng có Local AI DEMO", [
            "audit.chuan_bi_phan_loai@1", "ai.hoi_theo_yeu_cau@1", "audit.phan_luong_sau_ai@1"],
            "luồng, lý do, số đếm và tệp kết quả")]
        assert kiem(ma["doc_engine"]()) == []
    finally:
        kiem.__globals__["CHUOI"] = cu
