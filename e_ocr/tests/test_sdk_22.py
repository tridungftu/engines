"""OCR-9: hợp đồng SDK 2.5.0, ngăn bền và gói migration; chỉ DEMO."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk import thu

from e_ocr import van_ban
from ngan_demo import GOI, SoHanMuc, core_demo, dat_cau_hinh, ngan_demo, cau_hinh_hien_tai, ghi_so
from test_ocr_1 import chay
from test_ocr_2 import tess_gia
from test_ocr_4 import nhat_ky, RAW


def test_kiem_ke_sql_du_tung_tep_va_dung_bam_bytes():
    kk = json.loads((GOI / "sql/kiem_ke.json").read_text(encoding="utf-8"))
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert kk["phien_ban"] == phieu["phien_ban"]
    tep = {t["duong_dan"]: t for t in kk["tep"]}
    that = {p.relative_to(GOI).as_posix(): p for p in GOI.rglob("*")
            if p.is_file() and p != GOI / "sql/kiem_ke.json"}
    assert set(tep) == set(that) and len(tep) == len(kk["tep"])
    for ten, p in that.items():
        raw = p.read_bytes()
        assert tep[ten] == {"duong_dan": ten, "bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def test_sql_chi_tao_ba_bang_dung_truong_va_cot_he_thong():
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert phieu["du_lieu"]["goi_migration"] == {
        "ma": "e_ocr", "thu_muc": "sql", "tep_kiem_ke": "sql/kiem_ke.json", "phien_ban_du_lieu": 1}
    raw = (GOI / "sql/001_tao_ngan.sql").read_text(encoding="utf-8")
    raw = re.sub(r"--[^\n]*", "", raw)
    mau = r"CREATE TABLE eng_e_ocr\.([a-z_]+)\s*\((.*?)\);"
    bang = dict(re.findall(mau, raw, re.S))
    assert not re.sub(mau, "", raw, flags=re.S).strip()
    assert set(bang) == {b["bang"] for b in phieu["ngan_du_lieu"]}
    kieu = {"van_ban": "text", "so": "numeric", "ngay": "date", "co_khong": "boolean"}
    he_thong = {"id": "uuid", "phap_nhan_id": "uuid", "row_version": "bigint",
                "tao_luc": "timestamptz", "sua_luc": "timestamptz", "het_han_luc": "timestamptz", "viec_id": "uuid"}
    for b in phieu["ngan_du_lieu"]:
        sql = bang[b["bang"]]
        cot = dict(re.findall(r"^\s*([a-z_]+)\s+([a-z]+)", sql, re.M))
        assert cot == {**he_thong, **{t["ma"]: kieu[t["kieu"]] for t in b["truong"]}}
        for t in b["truong"]:
            if t.get("bat_buoc"):
                assert re.search(rf"\b{t['ma']} {kieu[t['kieu']]} NOT NULL\b", sql)
        if b["pham_vi"] == "phap_nhan":
            assert "phap_nhan_id uuid NOT NULL" in sql
        for unique in b.get("duy_nhat", []):
            assert "UNIQUE (" + ", ".join(unique) + ")" in sql


def test_ttl_chi_an_hang_ngay_khong_mat_cho_giu_luot_do(monkeypatch):
    ngan = ngan_demo()
    so = SoHanMuc(ngan)
    nk = nhat_ky(so=so)
    nk.giu(5000)
    nk.cap_nhat("chua_ro")
    qua_khu = datetime.now(timezone.utc) - timedelta(days=46)

    class DongHoCu(datetime):
        @classmethod
        def now(cls, tz=None):
            return qua_khu.astimezone(tz) if tz else qua_khu.replace(tzinfo=None)

    # Ghi qua ngăn SDK dưới đồng hồ Core giả; không sửa kho nội bộ.
    with monkeypatch.context() as tam:
        tam.setattr(thu, "datetime", DongHoCu)
        with ngan.lo() as lo:
            lo.them("han_muc_ngay", {"ngay": qua_khu.date().isoformat(), "da_nhan": '{"0":1}'})
    khoa = {"ngay": qua_khu.date().isoformat()}
    assert ngan.doc("han_muc_ngay", khoa) is None
    assert ngan.tim("han_muc_ngay").danh_sach == []
    assert ngan.doc("han_muc_ngay", khoa, gom_het_han=True) is not None
    assert len(ngan.tim("han_muc_ngay", gom_het_han=True).danh_sach) == 1
    assert so._doc()[1]["dang_giu"] == {nk.ma: 1}
    assert nk.doc()["trang_thai"] == "chua_ro"
    assert all(b["het_han_luc"] is None for b in core_demo().xem_ngan("e_ocr", "luot_abbyy"))


def test_the_he_luot_moi_giu_id_va_tang_cas_khong_xoa():
    nk = nhat_ky()
    nk.giu(5000)
    cu = nk.ngan.doc("luot_abbyy", nk._khoa())
    nk.cap_nhat("tu_choi")
    moi, da_tao = nk.giu(5000)
    ban = nk.ngan.doc("luot_abbyy", nk._khoa())
    assert da_tao and moi["lan_gui"] == 2
    assert ban.id == cu.id and ban.row_version > cu.row_version
    assert len(core_demo().xem_ngan("e_ocr", "luot_abbyy")) == 1


@pytest.mark.parametrize("bo", ["thu_muc_vao", "thu_muc_ra"])
def test_thieu_truong_bat_buoc_abbyy_bao_chua_cau_hinh(bo):
    cfg = {"bat": True, "thu_muc_vao": "DEMO/nhan", "thu_muc_ra": "DEMO/tra"}
    cfg.pop(bo)
    dat_cau_hinh({"abbyy": cfg})
    _, kq = chay(RAW, tham_so={"nguon": "chi_abbyy"})
    assert kq["loi"]["ma"] == "CHUA_CAU_HINH"
    assert not core_demo().xem_ngan("e_ocr", "luot_abbyy")


def test_cau_hinh_la_ban_chup_khi_nhan_viec(monkeypatch, tess_gia):
    dat_cau_hinh({"tesseract": {"ngon_ngu": "eng"}})
    doc_goc, cac_lan = van_ban.doc_theo_nguon, []

    def doc(*args, **kw):
        cfg = kw["cau_hinh"]
        cac_lan.append(cfg["tesseract"]["ngon_ngu"])
        dat_cau_hinh({"tesseract": {"ngon_ngu": "vie"}})
        assert cfg is kw["viec"].cau_hinh
        assert cfg["tesseract"]["ngon_ngu"] == cac_lan[-1]
        return doc_goc(*args, **kw)

    monkeypatch.setattr(van_ban, "doc_theo_nguon", doc)
    for _ in range(2):
        _, kq = chay(RAW, tham_so={"nguon": "chi_tesseract"})
        assert kq["trang_thai"] == "XONG", kq
    assert cac_lan == ["eng", "vie"]
    assert cau_hinh_hien_tai()["tesseract"]["ngon_ngu"] == "vie"


def test_vuot_tran_map_khong_ghi_mot_nua():
    so = SoHanMuc()
    cu = so._doc()[1]
    with pytest.raises(LoiNghiepVu) as loi:
        ghi_so(so, {"da_nhan": {}, "dang_giu": {f"{n:032x}": 1 for n in range(3000)}})
    assert loi.value.ma == "NGAN_DU_LIEU_QUA_LON"
    assert so._doc()[1] == cu
