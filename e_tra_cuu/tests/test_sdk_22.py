"""TC-S22: kiểm chuyển SDK bằng CoreGia thật, chỉ DEMO và Local giả."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk import __version__
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, NganXungDot, kiem_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay
from ho_tro_sdk_22 import BoNganSDK, mo_viec_ngan
from ho_tro_tc_2 import GOI
from ho_tro_tc_4 import BoAI, TAC_VU, dieu_phoi_hoi_ai


def test_sdk_va_wheel_da_ghim():
    repo = GOI.parents[2]
    wheel = repo / "docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl"
    ma = sha256(wheel.read_bytes()).hexdigest()
    assert __version__ == "2.2.0"
    assert f"{ma}  {wheel.name}" in wheel.with_name("SHA256SUMS.txt").read_text()
    assert (GOI / "requirements.lock").read_text().strip() == f"kho_tri_thuc_sdk==2.2.0 --hash=sha256:{ma}"


def test_ngan_giu_du_lieu_khi_engine_khoi_dong_lai():
    core = CoreGia()
    with mo_viec_ngan(core) as viec:
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("dot_kiem", {"ma_dot": "DEMO-BEN"}, {"trang_thai": "chua_do"})
        id_cu = lo.ket_qua[0].id
    with mo_viec_ngan(core) as viec:
        ban = viec.ngan.doc("dot_kiem", {"ma_dot": "DEMO-BEN"})
        assert ban.id == id_cu and ban.row_version == 1
        assert "viec_id" not in ban.gia_tri
    ds = core.xem_ngan("e_tra_cuu", "dot_kiem")
    assert len(ds) == 1 and ds[0]["phap_nhan_id"] == "DEMO-P"
    assert ds[0]["viec_id"]


def test_xung_dot_sdk_rollback_va_doc_lai_thu_lai():
    bo = BoNganSDK()
    try:
        ngan = bo.ngan()
        bo.core.gay_xung_dot_ngan("dot_kiem")
        with pytest.raises(NganXungDot) as exc:
            with ngan.lo() as lo:
                lo.lay_hoac_tao("dot_kiem", {"ma_dot": "DEMO-CAS"}, {})
        assert exc.value.thu_lai_duoc
        assert bo.core.xem_ngan("e_tra_cuu", "dot_kiem") == []
        with ngan.lo() as lo:
            lo.lay_hoac_tao("dot_kiem", {"ma_dot": "DEMO-CAS"}, {})
        assert lo.ket_qua[0].da_tao and lo.ket_qua[0].row_version == 1
    finally:
        bo.close()


def test_cau_hinh_doi_chi_ap_dung_viec_tiep_theo():
    phieu = deepcopy(chay.app.phieu)
    phieu["nang_luc"] = [{"ma": "demo.cau_hinh@1", "ten": "Cấu hình DEMO",
                           "nhan": ["van_ban"], "tra": "van_ban",
                           "gioi_han": {"thoi_han_giay": 30}}]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=GOI)
    core = CoreGia(app)
    cu = {"phien_ban": 1, "quy_tac_nhom": {"tep_id": "DEMO", "bam": "sha256:" + "a" * 64}}
    moi = {**cu, "cat_doan": {"do_dai_muc_tieu": 300}}
    core.dat_cau_hinh(app.ma, cu)
    da_gap, su_kien = [], []

    @app.khi_doi_cau_hinh
    def doi(cau_hinh):
        su_kien.append(cau_hinh)

    @app.nang_luc("demo.cau_hinh@1")
    def xu_ly(viec):
        truoc = deepcopy(viec.cau_hinh)
        if not da_gap:
            core.dat_cau_hinh(app.ma, moi)
        assert viec.cau_hinh == truoc
        da_gap.append(viec.cau_hinh)
        return {"loai": "van_ban", "van_ban": "DEMO"}

    ids = [core.giao_viec("demo.cau_hinh@1", {"loai": "van_ban", "van_ban": "DEMO"}) for _ in range(2)]
    core.chay(app)
    assert all(core.xem(i)["trang_thai"] == "XONG" for i in ids)
    assert [c["cat_doan"]["do_dai_muc_tieu"] for c in da_gap] == [2000, 300]
    assert len(su_kien) == 1 and su_kien[0]["cat_doan"]["do_dai_muc_tieu"] == 300


@pytest.mark.parametrize("kieu", ["json", "tep"])
def test_gioi_han_kieu_ngan_sdk_22_duoc_ghi_ro(kieu):
    phieu = deepcopy(chay.app.phieu)
    phieu["ngan_du_lieu"][0]["truong"][1]["kieu"] = kieu
    assert kiem_phieu(phieu, GOI)


@pytest.mark.parametrize("tac_vu", TAC_VU)
def test_bon_khuon_co_vai_tro_va_consumer_ai12_khong_nhan_nham_metadata(tac_vu):
    bo = BoAI()
    bo.nhan_ai(tac_vu)
    ra = bo.chuan_bi()
    assert ra["trang_thai"] == "XONG", ra
    ai = ra["ket_qua"]["yeu_cau_ai"]
    props = ai["khuon_tra_loi"]["properties"]
    if tac_vu == "phan_loai":
        m = next(m for m in bo.snapshot_ai(ra)["ai"]["map_nguon"] if m["ma_nguon"])
        can = {"ma_nguon": m["ma_nguon"], "ma_doan": m["ma_doan"],
               "cau": ai["tai_lieu"][m["ai_bat_dau"]:m["ai_ket_thuc"]],
               "bat_dau": m["ai_bat_dau"], "ket_thuc": m["ai_ket_thuc"]}
        du_lieu = {"nhom_de_xuat": "02", "loai_de_xuat": "DEMO-LOAI", "doi_tuong": "DEMO-VAY-A",
                   "diem": 0.9, "can_cu": [can], "ly_do_cho": ["can_review"], "de_nghi_chuyen_bo": False}
        assert props["diem"]["$comment"] == "ktt:ai12:metadata"
        assert props["can_cu"]["items"]["$comment"] == "ktt:ai12:trich_dan"
    elif tac_vu == "phan_tich_cau_hoi":
        du_lieu = {"y_dinh": "tra_gia_tri", "thuc_the": [], "ham_de_xuat": [
            {"ten": "m9.gia_tri", "phien_ban": "1", "tham_so": {"ma_khoan_vay": "DEMO-VAY-A"}}],
            "phu_thuoc_thoi_diem": False, "thoi_diem": bo.s_nhan["ngu_canh_core"]["thoi_diem"]}
        assert props["thuc_the"]["items"]["properties"]["gia_tri"]["$comment"] == "ktt:ai12:trich_xuat"
        assert ai["khuon_tra_loi"]["$defs"]["ham_0"]["properties"]["ma_khoan_vay"]["$comment"] == "ktt:ai12:trich_xuat"
    elif tac_vu == "xep_hang_lai":
        du_lieu = {"xep_hang": [{"ma_ung_vien": "DEMO-UV-1", "diem": 0.83}]}
        assert props["xep_hang"]["items"]["properties"]["diem"]["$comment"] == "ktt:ai12:metadata"
    else:
        m = next(m for m in bo.snapshot_ai(ra)["ai"]["map_nguon"] if m["ma_nguon"])
        can = {"ma_nguon": m["ma_nguon"], "ma_doan": m["ma_doan"],
               "cau": ai["tai_lieu"][m["ai_bat_dau"]:m["ai_ket_thuc"]],
               "bat_dau": m["ai_bat_dau"], "ket_thuc": m["ai_ket_thuc"]}
        du_lieu = {"tra_loi": "Giá trị là 1.000.000 VND.", "khang_dinh": [{"thuc_the": "DEMO-VAY-A",
            "truong": "gia_tri", "gia_tri": {"so": 1000000, "tien_te": "VND"}, "don_vi": "VND", "can_cu": [can]}],
            "co_mau_thuan": False}
        assert props["tra_loi"]["$comment"] == "ktt:ai12:tong_hop"
        assert props["khang_dinh"]["items"]["properties"]["gia_tri"]["$comment"] == "ktt:ai12:trich_xuat"
    kq, local = dieu_phoi_hoi_ai(bo, ra["ket_qua"], du_lieu)
    assert local.so_luot == 1 and set(local.__dict__) >= {"prompts"}
    assert kq["trang_thai"] == "XONG", kq
    tra = kq["ket_qua"]["tra_loi_ai"]
    assert tra["kiem_trich_dan"]["dat"] is True, tra
    assert tra["chuyen_tiep"] == ai["chuyen_tiep"]
    assert tra["nha_cung_cap"] == "local"


def test_tham_so_ham_khong_duoc_mien_kiem_bang_annotation_metadata():
    bo = BoAI()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    goc = yc["du_lieu"]["ham"][0]["schema_tham_so"]
    goc["properties"]["ma_khoan_vay"]["$comment"] = "ktt:ai12:metadata"
    bo.nhan_ai("phan_tich_cau_hoi", yc)
    ra = bo.chuan_bi()
    assert ra["trang_thai"] == "XONG"
    du_lieu = {"y_dinh": "tra_gia_tri", "thuc_the": [], "ham_de_xuat": [
        {"ten": "m9.gia_tri", "phien_ban": "1", "tham_so": {"ma_khoan_vay": "DEMO-BIA-KHONG-TRONG-CAN-CU"}}],
        "phu_thuoc_thoi_diem": False, "thoi_diem": bo.s_nhan["ngu_canh_core"]["thoi_diem"]}
    kq, _ = dieu_phoi_hoi_ai(bo, ra["ket_qua"], du_lieu)
    assert kq["trang_thai"] == "XONG"
    assert kq["ket_qua"]["tra_loi_ai"]["kiem_trich_dan"]["dat"] is False
    assert goc["properties"]["ma_khoan_vay"]["$comment"] == "ktt:ai12:metadata"


@pytest.mark.parametrize("tang", [2, 3])
@pytest.mark.parametrize("sai", [None, "gia_tri", "offset"])
def test_chuoi_consumer_hoi_ai_den_hau_kiem_tc_giu_san_can_cu(monkeypatch, tang, sai):
    from ho_tro_tc_4 import LocalGia
    from ho_tro_tc_7 import BoTraLoi
    from e_tra_cuu.kiem_dau_vao import json_chuan

    bo = BoTraLoi()
    bo.nhan_soan(tang)
    bo.chuan_bi_soan()
    du_lieu = bo.du_lieu_soan()
    if sai == "gia_tri":
        du_lieu["khang_dinh"][0]["gia_tri"]["so"] = 987654321
    elif sai == "offset":
        du_lieu["khang_dinh"][0]["can_cu"][0]["bat_dau"] += 1

    def hoi(self, cau_hinh, model, prompt, *, kiem_huy, khuon):
        kiem_huy()
        self.so_luot += 1
        can = self.du_lieu["khang_dinh"][0]["can_cu"][0]["cau"]
        return json_chuan({"du_lieu": self.du_lieu, "truong": [
            {"ten": "DEMO", "gia_tri": "DEMO", "trich_dan": can}]}).decode("utf-8")

    monkeypatch.setattr(LocalGia, "hoi", hoi)
    ra, local = dieu_phoi_hoi_ai(bo, bo.pb_ai, du_lieu)
    assert ra["trang_thai"] == "XONG" and local.so_luot == 1
    a = ra["ket_qua"]["tra_loi_ai"]
    assert a["kiem_trich_dan"]["dat"] is (sai is None)
    kq = bo.soan(ra["ket_qua"])
    assert kq["trang_thai"] == "XONG", kq
    r = bo.snapshot(kq)["ket_qua"]
    if sai is None:
        assert r["co_can_cu"] and r["nhan"] == "vang"
    else:
        assert not r["co_can_cu"] and r["nhan"] is None
        assert r["khang_dinh"] == [] and "KHANG_DINH_AI_KHONG_DAT" in r["ly_do"]


def test_kiem_ke_sql_toan_goi_khop_bytes_va_bam():
    kiem_ke = json.loads((GOI / "sql/kiem_ke.json").read_bytes())
    thuc_te = {p.relative_to(GOI).as_posix(): p.read_bytes() for p in GOI.rglob("*")
               if p.is_file() and p != GOI / "sql/kiem_ke.json"}
    assert kiem_ke["phien_ban"] == chay.app.phien_ban
    assert {t["duong_dan"] for t in kiem_ke["tep"]} == set(thuc_te)
    for t in kiem_ke["tep"]:
        b = thuc_te[t["duong_dan"]]
        assert t["bytes"] == len(b) and t["sha256"] == sha256(b).hexdigest()


def test_sql_chi_tao_bang_ngan_dung_schema_va_cot():
    import re
    sql = (GOI / "sql/001_tao_dot_kiem.sql").read_text(encoding="utf-8")
    ma = re.sub(r"--[^\n]*", "", sql).strip()
    assert ma.startswith("CREATE TABLE eng_e_tra_cuu.dot_kiem (") and ma.count(";") == 1
    cot = set(re.findall(r"^    ([a-z_]+) (?:uuid|bigint|timestamptz|text)", ma, re.M))
    he_thong = {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
    assert cot == he_thong | {t["ma"] for t in chay.app.phieu["ngan_du_lieu"][0]["truong"]}
    assert "UNIQUE (phap_nhan_id, ma_dot)" in ma
    assert "giu_toi_da_ngay" not in chay.app.phieu["ngan_du_lieu"][0]
