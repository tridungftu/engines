"""AI-11: ngữ nghĩa SDK chính thức, kiểm kê raw bytes và thiếu cấu hình."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from e_hoi_ai import chay, chon_model
from e_hoi_ai.hoi import yeu_cau_cau_hinh
from local_gia import core_demo, nap_cau_hinh

GOI = Path(__file__).resolve().parents[1] / "goi" / "e_hoi_ai"


def test_cau_hinh_snapshot_va_hook_khi_doi_giua_hai_viec(monkeypatch):
    core = core_demo()
    nap_cau_hinh("http://127.0.0.1:12345", thoi_han=5)
    monkeypatch.setattr(chon_model.bo_phat_hien, "_dem", {})
    da_doc = []
    def xu_ly(viec):
        ch = yeu_cau_cau_hinh(viec)
        da_doc.append(deepcopy(ch))
        if len(da_doc) == 1:
            chon_model.bo_phat_hien._dem["DEMO"] = "DEMO"
            nap_cau_hinh("http://127.0.0.1:12346", thoi_han=6)
            assert yeu_cau_cau_hinh(viec)["local_ai"]["timeout_giay"] == 5
        else:
            assert not chon_model.bo_phat_hien._dem
        viec.cau_hinh["quy_tac_model"] = []
        return {"loai": "truong", "truong": {"tra_loi": "DEMO", "co_can_cu": False,
            "trich_dan": "", "model": "DEMO", "ly_do_chon_model": "DEMO"}}
    monkeypatch.setattr(chay.bo_hoi, "goi", xu_ly)
    vd = chay.app.phieu["chay_thu_demo"][0]
    ids = [core.giao_viec(vd["nang_luc"], vd["dau_vao"], vd["tham_so"]) for _ in range(2)]
    core.chay(chay.app)
    assert all(core.xem(ma)["trang_thai"] == "XONG" for ma in ids)
    assert [c["local_ai"]["timeout_giay"] for c in da_doc] == [5, 6]
    assert core.duong_truyen(chay.app.ma).doc_cau_hinh()["cau_hinh"]["quy_tac_model"]


@pytest.mark.parametrize("local", [None, {}, {"url": "http://127.0.0.1:12345"}, {"timeout_giay": 2}])
def test_thieu_truong_bat_buoc_tra_chua_cau_hinh(local):
    with pytest.raises(LoiNghiepVu) as loi:
        yeu_cau_cau_hinh(SimpleNamespace(cau_hinh={} if local is None else {"local_ai": local}))
    assert loi.value.ma == "CHUA_CAU_HINH"


def test_kiem_ke_sql_khop_moi_tep_va_sql_dung_khai_bao():
    kk = json.loads((GOI / "sql/kiem_ke.json").read_text(encoding="utf-8"))
    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    assert kk["phien_ban"] == phieu["phien_ban"]
    tep = {p.relative_to(GOI).as_posix(): p.read_bytes() for p in GOI.rglob("*")
           if p.is_file() and p.relative_to(GOI).as_posix() != "sql/kiem_ke.json"}
    assert len(kk["tep"]) == len(tep)
    assert {m["duong_dan"] for m in kk["tep"]} == set(tep)
    for m in kk["tep"]:
        raw = tep[m["duong_dan"]]
        assert len(raw) == m["bytes"]
        assert hashlib.sha256(raw).hexdigest() == m["sha256"]
        assert b"\r" not in raw
    sql = (GOI / "sql/001_tao_model_phat_hien.sql").read_text(encoding="utf-8")
    cau = re.sub(r"--[^\n]*", "", sql).strip().rstrip(";")
    assert len(cau.split(";")) == 1 and cau.startswith("CREATE TABLE eng_e_hoi_ai.model_phat_hien (")
    cot = {m[0]: m[1] for m in re.findall(r"^    ([a-z_]+) ([a-z]+)", cau, re.MULTILINE)}
    he_thong = {"id": "uuid", "phap_nhan_id": "uuid", "row_version": "bigint", "tao_luc": "timestamptz",
                "sua_luc": "timestamptz", "het_han_luc": "timestamptz", "viec_id": "uuid"}
    kieu = {"van_ban": "text", "so": "numeric", "co_khong": "boolean"}
    bang = phieu["ngan_du_lieu"][0]
    assert cot == {**he_thong, **{t["ma"]: kieu[t["kieu"]] for t in bang["truong"]}}
    assert "UNIQUE (id_model)" in sql and "id_model text NOT NULL" in sql
    assert {b["bang"] for b in phieu["ngan_du_lieu"]} == {"model_phat_hien"}
    assert phieu["tuong_thich"]["sdk"] == ">=2.2.0 <3.0.0"
