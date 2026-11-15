"""DC-S22: đã kiểm bằng Core giả (CoreGia), không chứng nhận Core thật."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

import pytest
import kho_tri_thuc_sdk
from kho_tri_thuc_sdk.engine import LoiNghiepVu, LoiDuongTruyen, NganXungDot

from ngan_demo import trong_ngan
from test_dc3 import Mau, chay, hs


GOI = Path(__file__).resolve().parents[1] / "goi/e_doi_chieu"


def test_sdk_va_wheel_dung_ban():
    assert kho_tri_thuc_sdk.__version__ == "2.2.0"
    sdk = GOI.parents[2] / "docs/goi-gui-engine/sdk-2.2.0"
    wheel = sdk / "kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
    expected = next(l.split()[0] for l in (sdk / "SHA256SUMS.txt").read_text().splitlines()
                    if l.endswith(wheel.name))
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == expected
    assert "kho_tri_thuc_sdk==2.2.0" in (GOI / "requirements.lock").read_text()


def test_sql_khai_bao_va_cot_he_thong_khop():
    sql = (GOI / "sql/001_tao_ngan.sql").read_text(encoding="utf-8")
    statements = [s.strip() for s in re.sub(r"--[^\n]*", "", sql).split(";") if s.strip()]
    them_cot = "\n".join(p.read_text(encoding="utf-8") for p in sorted((GOI / "sql").glob("*.sql")))
    assert len(statements) == len(chay.app.phieu["ngan_du_lieu"]) == 4
    for statement, bang in zip(statements, chay.app.phieu["ngan_du_lieu"]):
        assert statement.startswith("CREATE TABLE eng_e_doi_chieu." + bang["bang"] + " (")
        for cot in ("id uuid PRIMARY KEY", "row_version bigint NOT NULL DEFAULT 1", "tao_luc timestamptz",
                    "sua_luc timestamptz", "het_han_luc timestamptz", "viec_id uuid"):
            assert cot in statement
        assert ("phap_nhan_id uuid NOT NULL" in statement) == (bang["pham_vi"] == "phap_nhan")
        for truong in bang["truong"]:
            kieu = {"van_ban": "text", "so": "numeric"}[truong["kieu"]]
            assert (re.search(r"\b" + truong["ma"] + " " + kieu + r"\b", statement) or
                    ("ALTER TABLE eng_e_doi_chieu." + bang["bang"] + " ADD COLUMN " + truong["ma"] + " " + kieu + ";") in them_cot)
        for unique in bang.get("duy_nhat", []):
            assert "UNIQUE (" + ", ".join(unique) + ")" in statement
        assert "phap_nhan_id" not in bang["khoa"]
        assert "phap_nhan_id" not in {t["ma"] for t in bang["truong"]}


def test_kiem_ke_sql_du_tat_ca_bytes_va_sha():
    kiem_ke = json.loads((GOI / "sql/kiem_ke.json").read_text(encoding="utf-8"))
    assert kiem_ke["phien_ban"] == chay.app.phieu["phien_ban"]
    expected = {p.relative_to(GOI).as_posix(): p for p in GOI.rglob("*")
                if p.is_file() and p != GOI / "sql/kiem_ke.json"}
    actual = {r["duong_dan"]: r for r in kiem_ke["tep"]}
    assert len(actual) == len(kiem_ke["tep"]) and actual.keys() == expected.keys()
    for name, p in expected.items():
        raw = p.read_bytes()
        assert len(raw) == actual[name]["bytes"], name
        assert hashlib.sha256(raw).hexdigest() == actual[name]["sha256"], name
        if p.suffix in {".py", ".md", ".json", ".sql", ".lock"}:
            assert b"\r\n" not in raw, name


def test_khuon_dc6_vai_tro_ai12_va_bam():
    from e_doi_chieu.chuan_bi_ai import khuon_tra_loi

    khuon = khuon_tra_loi(["DEMO-1"])
    fields = khuon["properties"]["diem"]["items"]["properties"]
    for k in ("ma_diem", "nhan", "ly_do"):
        assert fields[k]["$comment"] == "ktt:ai12:metadata"
    for k in ("trai", "phai"):
        assert fields[k]["$comment"] == "ktt:ai12:trich_dan"
    root = GOI.parents[2]
    with pytest.MonkeyPatch.context() as mp:
        mp.syspath_prepend(str(root / "e_hoi_ai/goi/e_hoi_ai"))
        from e_hoi_ai.vai_tro_khuon import khuon_hau_kiem
        cu = hs.bam(hs.json_bytes(khuon))
        assert khuon_hau_kiem(khuon, {"doi_chieu": {"phien_ban": 1}}) == khuon
        assert hs.bam(hs.json_bytes(khuon)) == cu


def test_cau_hinh_dang_xu_ly_giu_ban_chup(monkeypatch):
    mau = Mau()
    original = hs.chuan_hoa
    da_doi = False

    def doi_giua_viec(*a, **kw):
        nonlocal da_doi
        if not da_doi:
            da_doi = True
            mau.cau_hinh["phien_ban_cau_hinh"] = "DEMO-2"
            mau.dat_cau_hinh()
        return original(*a, **kw)

    monkeypatch.setattr(hs, "chuan_hoa", doi_giua_viec)
    assert mau.snapshot(mau.chay())["cau_hinh"]["phien_ban_cau_hinh"] == "DEMO-1"
    assert mau.snapshot(mau.chay())["cau_hinh"]["phien_ban_cau_hinh"] == "DEMO-2"
    assert len(mau.cac_luot()) == 2


@pytest.mark.parametrize("thieu", chay._BAT_BUOC)
def test_thieu_tung_truong_bat_buoc_khong_thanh_cong(thieu):
    mau = Mau()
    mau.cau_hinh.pop(thieu)
    mau.dat_cau_hinh()
    kq = mau.chay()
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "CHUA_CAU_HINH"
    assert not mau.cac_luot()


def test_ngan_phap_nhan_cung_khoa_khong_doc_cheo():
    mau = Mau()

    def ghi(ngan):
        with ngan.lo() as lo:
            lo.lay_hoac_tao("loi_ocr_de_xuat", {"bam_cap_tu": "DEMO"}, {})
        return ngan.doc("loi_ocr_de_xuat", {"bam_cap_tu": "DEMO"})

    a = trong_ngan(mau, ghi, "DEMO-P1")
    b = trong_ngan(mau, lambda n: n.doc("loi_ocr_de_xuat", {"bam_cap_tu": "DEMO"}), "DEMO-P2")
    assert a.gia_tri["phap_nhan_id"] == "DEMO-P1" and b is None
    c = trong_ngan(mau, ghi, "DEMO-P2")
    assert a.id != c.id
    assert len(mau.core.xem_ngan(mau.app.ma, "loi_ocr_de_xuat")) == 2


def test_lo_nguyen_tu_khi_cas_sai_khong_ghi_do_dang():
    mau = Mau()
    assert mau.chay()["trang_thai"] == "XONG"
    ban = mau.cac_luot()[0]

    def lo_sai(ngan):
        with ngan.lo() as lo:
            lo.them("loi_ocr_de_xuat", {"bam_cap_tu": "DEMO-chua-ghi"})
            lo.sua("luot_doi_chieu", {"ma_luot": ban.gia_tri["ma_luot"]},
                   {"trang_thai": "DEMO-khong-ghi"}, row_version=ban.row_version - 1)

    with pytest.raises(NganXungDot):
        trong_ngan(mau, lo_sai)
    assert not mau.core.xem_ngan(mau.app.ma, "loi_ocr_de_xuat")
    assert mau.cac_luot() == [ban]


def test_mat_phan_hoi_ngan_khong_nhan_doi_luot():
    mau = Mau()
    mau.core.gay_mat_xac_nhan("ngan")
    kq = mau.chay()
    assert kq["trang_thai"] == "XONG", kq
    assert len(mau.cac_luot()) == 1 and mau.core.so_tai == 1


def test_cum_tien_lap_giu_tung_vi_tri_va_gia_tri_rieng():
    from test_dc5 import qt, bo_demo, BanQuetDemo

    line = "DEMO 1000 VND (một nghìn đồng)."
    ds = qt._kiem_tien_noi_bo(BanQuetDemo(line + "\n" + line), bo_demo()["quy_tac_cung"], lambda: None)
    assert len(ds) == 2 and all(d["khop"] is True for d in ds)
    assert ds[0]["nguyen_van"]["bat_dau"] == 0
    assert ds[1]["nguyen_van"]["bat_dau"] == len(line) + 1
    ds[0]["tien_bang_so"]["so"] = 999
    assert ds[1]["tien_bang_so"]["so"] == 1000
    ds[0]["tien_bang_chu"]["tien_te"] = "DEMO"
    assert ds[1]["tien_bang_chu"]["tien_te"] == "VND"


def test_khong_con_cong_tam_xoa_hoac_cau_hinh_trong_ngan():
    assert "cau_hinh" not in {b["bang"] for b in chay.app.phieu["ngan_du_lieu"]}
    for p in (GOI / "e_doi_chieu").glob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert node.module not in {"ngan", "cau_hinh"}
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr != "xoa"
