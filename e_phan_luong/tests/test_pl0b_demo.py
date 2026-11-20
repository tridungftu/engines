"""Kiểm fixture PL-0B độc lập engine; chưa phải test tích hợp CoreGia."""

import hashlib
import json
import re
import runpy
import subprocess
import sys
import unicodedata
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest


GOC_ENGINE = Path(__file__).resolve().parents[1]
GOC_REPO = GOC_ENGINE.parent
DEMO = GOC_ENGINE / "tests" / "demo"
SINH = runpy.run_path(str(DEMO / "sinh_demo.py"))
# PL-7A lấy từ đầu ra e_hoa_don với XML DEMO, không do sinh_demo.py sinh.
# Khóa bytes riêng, không đưa vào phép so tái sinh của bộ PL-0B.
BAM_HOA_DON_DEMO = {
    "tests/demo/hoa-don-xml-DEMO.json": "sha256:907aa867c39963aaad135f54d81d3d843a6fb9a5f41fdb00b016e535cdaf8e5f",
    "tests/demo/hoa-don-zip-DEMO.json": "sha256:b3a07740b90edde4537931f60eab8c23e9722e2ea07ba8988667869757c89811",
    "tests/demo/hoa-don-chi-tiet-zip-DEMO.json": "sha256:3815c23a5a5dd571b5ef258747dc8c01fe229ab80368714d01067c02ea71f5d8",
}


def doc(ten):
    return json.loads((DEMO / ten).read_text(encoding="utf-8"))


def sha(noi_dung):
    return "sha256:" + hashlib.sha256(noi_dung).hexdigest()


def kiem_schema_bang_tay(gia_tri, schema):
    """Fallback theo khóa bắt buộc, kiểu và enum có trong schema phong bì chung."""
    kieu = {"object": dict, "array": list, "string": str, "integer": int,
            "number": (int, float), "boolean": bool, "null": type(None)}
    if "type" in schema:
        cac_kieu = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        assert any(isinstance(gia_tri, kieu[k]) and
                   not (k in ("integer", "number") and isinstance(gia_tri, bool))
                   for k in cac_kieu)
    if "const" in schema:
        assert gia_tri == schema["const"]
    if "enum" in schema:
        assert gia_tri in schema["enum"]
    if isinstance(gia_tri, dict):
        assert set(schema.get("required", ())) <= gia_tri.keys()
        for khoa, schema_con in schema.get("properties", {}).items():
            if khoa in gia_tri:
                kiem_schema_bang_tay(gia_tri[khoa], schema_con)
    if isinstance(gia_tri, list) and "items" in schema:
        for muc in gia_tri:
            kiem_schema_bang_tay(muc, schema["items"])
    if isinstance(gia_tri, str):
        assert len(gia_tri) >= schema.get("minLength", 0)
        if "pattern" in schema:
            assert re.search(schema["pattern"], gia_tri)
    if type(gia_tri) in (int, float):
        assert gia_tri >= schema.get("minimum", float("-inf"))
        assert gia_tri <= schema.get("maximum", float("inf"))


def kiem_schema(gia_tri, schema):
    try:
        import jsonschema
    except ImportError:
        kiem_schema_bang_tay(gia_tri, schema)
    else:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(gia_tri)


def test_tai_sinh_cung_byte_va_bam_co_dinh(tmp_path):
    bo = SINH["sinh_bo_demo"]()
    assert bo == SINH["sinh_bo_demo"]()
    danh_sach_bam = doc("bam-demo.json")["tep"]
    assert set(bo) == set(danh_sach_bam) | {"tests/demo/bam-demo.json"}
    for ten, noi_dung in bo.items():
        assert (GOC_ENGINE / ten).read_bytes() == noi_dung, ten
        if ten in danh_sach_bam:
            assert sha(noi_dung) == danh_sach_bam[ten], ten
        assert b"\r" not in noi_dung and not noi_dung.startswith(b"\xef\xbb\xbf")

    # Thực thi CLI hai lần ở cây tạm, ngoài cwd repo, khác PYTHONHASHSEED.
    script = tmp_path / "tests" / "demo" / "sinh_demo.py"
    script.parent.mkdir(parents=True)
    script.write_bytes((DEMO / "sinh_demo.py").read_bytes())
    import os
    for hat in ("1", "8675309"):
        tien_trinh = subprocess.run([sys.executable, "-B", str(script)], cwd=tmp_path,
                                   env={**os.environ, "PYTHONHASHSEED": hat},
                                   capture_output=True, timeout=30)
        assert tien_trinh.returncode == 0, tien_trinh.stderr.decode("utf-8", errors="replace")
        assert {ten: (tmp_path / ten).read_bytes() for ten in bo} == bo


def test_moi_json_doc_duoc_va_dung_danh_sach():
    tep_thuc = {"tests/demo/" + p.name for p in DEMO.glob("*.json")}
    tep_thuc |= {"goi/e_phan_luong/demo/" + p.name
                 for p in (GOC_ENGINE / "goi/e_phan_luong/demo").glob("*.json")}
    assert tep_thuc == set(SINH["sinh_bo_demo"]()) | set(BAM_HOA_DON_DEMO)
    for ten in tep_thuc:
        noi_dung = (GOC_ENGINE / ten).read_bytes()
        if ten in BAM_HOA_DON_DEMO:
            assert sha(noi_dung) == BAM_HOA_DON_DEMO[ten], ten
            assert b"DEMO" in noi_dung, ten
        du_lieu = json.loads(noi_dung.decode("utf-8"),
                            parse_constant=lambda _: pytest.fail("JSON có hằng số ngoài chuẩn."))
        assert isinstance(du_lieu, (dict, list)), ten


def test_lo_500_va_lo_nho_du_ca():
    lo = doc("lo-500-DEMO.json")
    lo_nho = json.loads((GOC_ENGINE / "goi/e_phan_luong/demo/lo-nho-DEMO.json").read_bytes())
    assert lo["ten"] == "Công ty DEMO Ánh Dương"
    assert lo["ma_module"] == "demo_thanh_toan" and lo["ky"] == "2026-11"
    assert lo["phien_ban"] == 1
    assert len(lo["nghiep_vu"]) == 500
    assert len({d["ma"] for d in lo["nghiep_vu"]}) == 500
    assert lo_nho == {**lo, "nghiep_vu": lo["nghiep_vu"][:20]}
    ca = {d["thuoc_tinh"]["ca_demo"] for d in lo_nho["nghiep_vu"]}
    assert ca == {"vuot_te", "vuot_pm", "chia_nho", "doi_tac_moi", "so_tron",
                  "ngay_nghi", "cuoi_ky", "nhap_tay", "co_do_cung", "usd_chua_quy_doi",
                  "usd_co_quy_doi", "thieu_tien_te", "module_da_gan", "chi_quy_tac_phan_loai",
                  "khong_khop", "tam_ung", "chi_phi_khac", "thu_tien"}
    for dong in lo["nghiep_vu"]:
        ngay = date.fromisoformat(dong["ngay"])
        assert date(2026, 10, 1) <= ngay <= date(2026, 11, 30)
        assert type(dong["nhap_tay"]) is type(dong["co_do_cung"]) is bool
        for khoa in ("so_tien", "so_tien_quy_doi"):
            if dong[khoa] is not None:
                assert isinstance(dong[khoa]["so"], str)
                assert Decimal(dong[khoa]["so"]).is_finite()
                if dong["thuoc_tinh"].get("ca_demo") != "thieu_tien_te":
                    assert dong[khoa]["tien_te"] in {"VND", "USD"}


def test_dap_an_lop1_khop_du_lieu_va_nhom_chia_nho():
    lo = doc("lo-500-DEMO.json")
    dap_an = doc("dap-an-lop1.json")["theo_ma"]
    assert set(dap_an) == {d["ma"] for d in lo["nghiep_vu"]}
    assert lo["nguong"] == doc("nguong-DEMO.json") == {
        "pm": {"so": "5000000000", "tien_te": "VND"},
        "te": {"so": "3000000000", "tien_te": "VND"},
        "sad": {"so": "250000000", "tien_te": "VND"},
    }
    nhom, ly_do = defaultdict(list), {}
    for d in lo["nghiep_vu"]:
        tien_goc, quy_doi = d["so_tien"], d["so_tien_quy_doi"]
        so = None
        ma_ly_do = set()
        if quy_doi and quy_doi.get("tien_te") == "VND":
            so = Decimal(quy_doi["so"])
        elif tien_goc.get("tien_te") == "VND":
            so = Decimal(tien_goc["so"])
        else:
            ma_ly_do.add("CHUA_RO_TIEN_TE" if not tien_goc.get("tien_te") else "CHUA_QUY_DOI")
        if so is not None:
            if so >= 5_000_000_000:
                ma_ly_do.add("VUOT_PM")
            elif so >= 3_000_000_000:
                ma_ly_do.add("VUOT_TE")
            else:
                nhom[d["doi_tac"]].append((date.fromisoformat(d["ngay"]), so, d["ma"]))
        if d["co_do_cung"]:
            ma_ly_do.add("CO_DO_CUNG")
        ly_do[d["ma"]] = ma_ly_do
    for cac_dong in nhom.values():
        for ngay, _, _ in cac_dong:
            cua_so = [d for d in cac_dong if ngay - timedelta(days=6) <= d[0] <= ngay]
            if sum(d[1] for d in cua_so) >= 3_000_000_000:
                assert len(cua_so) >= 3
                for _, _, ma in cua_so:
                    ly_do[ma].add("NGHI_CHIA_NHO")
    for ma, ky_vong in dap_an.items():
        assert set(ky_vong["ly_do"]) == ly_do[ma], ma
    assert {ma for ma, l in ly_do.items() if "NGHI_CHIA_NHO" in l} == {
        "PC-DEMO-0003", "PC-DEMO-0004", "PC-DEMO-0005"}


def test_danh_muc_quy_tac_va_nguon_loai():
    danh_muc = doc("danh-muc-loai-DEMO.json")
    cac_ma = {d["ma"] for d in danh_muc}
    assert cac_ma == {"thanh_toan_ncc", "tam_ung", "luong", "chi_phi_khac", "thu_tien"}
    bo = doc("bo-phan-loai-DEMO.json")
    assert bo["phien_ban"] == 1
    assert {q["loai"] for q in bo["quy_tac"]} == cac_ma
    for q in bo["quy_tac"]:
        assert set(q) == {"loai", "khi"}
        assert all(set(k) == {"tat_ca", "khong_co"} for k in q["khi"])

    def chuan(chu):
        return "".join(c for c in unicodedata.normalize("NFD", chu.lower().replace("đ", "d"))
                       if not unicodedata.combining(c))

    dap_an = doc("dap-an-lop1.json")["theo_ma"]
    for d in doc("lo-500-DEMO.json")["nghiep_vu"]:
        loai, nguon = d["loai"], "module"
        if loai is None:
            nguon = "quy_tac"
            loai = next((q["loai"] for q in bo["quy_tac"]
                         if any(all(chuan(t[0]) in chuan(d["dien_giai"]) for t in k["tat_ca"])
                                for k in q["khi"])), None)
        if loai is None:
            loai, nguon = "chua_phan_loai", "chua_phan_loai"
        assert (loai, nguon) == (dap_an[d["ma"]]["loai"], dap_an[d["ma"]]["nguon_loai"])
    assert dap_an["PC-DEMO-0015"] == {"ly_do": [], "loai": "luong", "nguon_loai": "module"}


def test_co_rui_ro_da_cai_san():
    ds = {d["ma"]: d for d in doc("lo-500-DEMO.json")["nghiep_vu"]}
    da = doc("dap-an-lop1.json")
    moi = ds["PC-DEMO-0006"]
    for da_gap in da["ho_so_demo"]["doi_tac_da_gap_theo_loai"].values():
        assert moi["doi_tac"] not in da_gap
    assert Decimal(ds["PC-DEMO-0007"]["so_tien"]["so"]) % 10_000_000 == 0
    assert date.fromisoformat(ds["PC-DEMO-0008"]["ngay"]).weekday() >= 5
    assert ds["PC-DEMO-0009"]["ngay"] == "2026-11-30"
    assert ds["PC-DEMO-0010"]["nhap_tay"] is True
    assert set(da["co_ky_vong_theo_ma"]) == {f"PC-DEMO-{stt:04d}" for stt in range(6, 11)}


def test_ket_qua_kiem_du_ba_khau_va_sua_loai():
    ket_qua = doc("ket-qua-kiem-mau-DEMO.json")
    ds = ket_qua["ket_qua"]
    assert ket_qua["phien_ban"] == 1 and ket_qua["ma_module"] == "demo_thanh_toan"
    assert {d["khau"] for d in ds} == set(doc("dap-an-lop1.json")["khau"]) == {
        "kt_kiem", "ktt_duyet", "cfo_duyet"}
    assert len(ds) == len({(d["ma_luot"], d["ma"], d["khau"]) for d in ds}) == 60
    assert {d["ket_qua"] for d in ds} == {"dat", "sai", "khong_kiem"}
    assert {d["so_tien_sai"]["so"] for d in ds if d["ket_qua"] == "sai"} == {
        "0", "1000000", "250000000", "3000000000"}
    for d in ds:
        assert d["ma_luot"].startswith("PL-DEMO-") and d["ma"].startswith("PC-DEMO-")
        assert d["so_tien_sai"]["tien_te"] == "VND"
    assert any(d["loai_dung"] == "chi_phi_khac" for d in ds)


@pytest.mark.parametrize("ten_schema,mau", [
    ("yeu_cau_ai", "yeu-cau-ai-*.json"), ("tra_loi_ai", "tra-loi-ai-*.json")])
def test_phong_bi_ai_hop_schema_chung(ten_schema, mau):
    schema = json.loads((GOC_REPO / "_chung/contract" / f"{ten_schema}.schema.json").read_bytes())
    for tep in DEMO.glob(mau):
        phong_bi = json.loads(tep.read_bytes())
        kiem_schema(phong_bi, schema)
        kiem_schema_bang_tay(phong_bi, schema)
        phong_bi[ten_schema].pop("chuyen_tiep")
        with pytest.raises(AssertionError):
            kiem_schema_bang_tay(phong_bi, schema)


def test_nam_ca_ai_va_chuyen_tiep():
    yeu_cau_byte = (DEMO / "yeu-cau-ai-DEMO.json").read_bytes()
    yc = json.loads(yeu_cau_byte)["yeu_cau_ai"]
    ct = yc["chuyen_tiep"]
    assert len(json.dumps(ct, ensure_ascii=False).encode("utf-8")) <= 4096
    pl = ct["phan_luong"]
    assert set(pl) == {"phien_ban", "tep_lo", "bam_tep", "khau", "khong_can_ai"}
    assert pl["phien_ban"] == 1 and pl["khong_can_ai"] is False
    assert pl["khau"] == "ktt_duyet"
    tep = pl["tep_lo"]
    assert set(tep) == {"tep_id", "ten", "mime", "kich_thuoc"}
    assert tep["tep_id"].startswith("tep-DEMO-") and tep["mime"] == "application/json"
    snapshot = (DEMO / tep["ten"]).read_bytes()
    assert tep["kich_thuoc"] == len(snapshot) and pl["bam_tep"] == sha(snapshot)
    assert json.loads(snapshot)["cho_ai"] == [{
        "chi_so": 0, "ma": ["PC-DEMO-0017"], "noi_dung": "Nội dung ZZZ DEMO chưa xác định"}]
    khuon = yc["khuon_tra_loi"]
    assert set(khuon["properties"]["phan_loai"]["items"]["properties"]["loai"]["enum"]) == {
        d["ma"] for d in doc("danh-muc-loai-DEMO.json")}
    assert len(list(DEMO.glob("tra-loi-ai-*.json"))) == 5
    for ca in ("dung-enum", "sai-enum", "tin-cay-thap", "cloud", "khong-thay-can-cu"):
        tl = doc(f"tra-loi-ai-{ca}.json")["tra_loi_ai"]
        assert tl["chuyen_tiep"] == ct and tl["bam_dau_vao"] == sha(yeu_cau_byte)
        assert tl["nha_cung_cap"] == ("cloud" if ca == "cloud" else "local")
        if ca == "khong-thay-can-cu":
            assert tl["trang_thai"] == "khong_thay_can_cu" and tl["du_lieu"] is None
            assert tl["kiem_trich_dan"]["dat"] is False
        elif ca == "sai-enum":
            assert tl["du_lieu"]["phan_loai"][0]["loai"] not in {
                d["ma"] for d in doc("danh-muc-loai-DEMO.json")}
            with pytest.raises(AssertionError):
                kiem_schema_bang_tay(tl["du_lieu"], khuon)
        else:
            kiem_schema(tl["du_lieu"], khuon)
            assert tl["du_lieu"]["phan_loai"][0]["tin_cay"] == (0.4 if ca == "tin-cay-thap" else 0.9)


def test_chi_du_lieu_demo_khong_dinh_danh_nhay_cam():
    # Không sinh MST/số tài khoản ngân hàng; 331/1121 chỉ là tài khoản hạch toán.
    khoa_cam = {"mst", "ma_so_thue", "so_tai_khoan", "tai_khoan_ngan_hang", "iban"}

    def duyet(gia_tri, khoa="", *, hoa_don_demo=False):
        if isinstance(gia_tri, dict):
            assert not (set(gia_tri) & khoa_cam)
            for k, v in gia_tri.items():
                duyet(v, k, hoa_don_demo=hoa_don_demo)
        elif isinstance(gia_tri, list):
            for v in gia_tri:
                duyet(v, khoa, hoa_don_demo=hoa_don_demo)
        elif isinstance(gia_tri, str):
            assert "thật" not in gia_tri.casefold()
            if khoa in {"ten", "mo_ta", "dien_giai", "noi_dung", "doi_tac"}:
                assert "demo" in gia_tri.casefold()
            if khoa != "so":
                # Chỉ hai MST giả trong XML DEMO gốc của e_hoa_don;
                # lexeme là bản giữ nguyên MST đó trong chi tiết nguồn.
                mst_demo = (hoa_don_demo
                            and khoa in {"ma_so_thue_ban", "ma_so_thue_mua", "lexeme"}
                            and gia_tri in {"0100000001", "0100000002"})
                assert mst_demo or not re.fullmatch(r"\d{10,}", gia_tri)
            if khoa in {"tai_khoan_no", "tai_khoan_co"}:
                assert gia_tri in {"331", "1121"}

    for ten, noi_dung in SINH["sinh_bo_demo"]().items():
        duyet(json.loads(noi_dung))
    for ten, bam in BAM_HOA_DON_DEMO.items():
        noi_dung = (GOC_ENGINE / ten).read_bytes()
        assert sha(noi_dung) == bam, ten
        assert b"DEMO" in noi_dung, ten
        duyet(json.loads(noi_dung), hoa_don_demo=True)
