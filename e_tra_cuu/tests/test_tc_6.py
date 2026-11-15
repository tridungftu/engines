"""TC-6 đã kiểm bằng Core giả (CoreGia); DEMO/Local giả, không chứng nhận RLS."""

import builtins
from copy import deepcopy
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, Viec, ViecDaHuy

from e_tra_cuu import cau_hoi, xep_hang
from e_tra_cuu.kiem_dau_vao import bam, json_chuan
from ho_tro_tc_2 import NGU_CANH
from ho_tro_tc_6 import BoHauKiem, THUC_THE, chay_demo_hau_kiem


def loi(kq, ma):
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None, kq
    assert kq["loi"]["ma"] in ({ma} if type(ma) is str else ma), kq


def dat(bo, kq):
    assert kq["trang_thai"] == "XONG", kq
    s = bo.snapshot(kq)
    assert s["nguon"] == bo.s_ai["nguon"] and s["du_lieu"] == bo.s_ai["du_lieu"]
    assert s["cau_hinh"] == bo.s_ai["cau_hinh"] and s["ai"] == bo.s_ai["ai"]
    assert s["ket_qua"]["phu_thuoc_cache"]["nguon"] == s["nguon"]
    assert s["ket_qua"]["phu_thuoc_cache"]["thuc_the"] == s["ket_qua"]["thuc_the"]
    assert kq["ket_qua"]["ho_so_tra_cuu"]["tom_tat"]["co_can_cu"] is None
    assert kq["ket_qua"]["ho_so_tra_cuu"]["tom_tat"]["nhan"] is None
    assert bo.so_luot_local == 1
    return s["ket_qua"]


@pytest.fixture
def cau():
    bo = BoHauKiem()
    bo.chuan_bi_hau()
    bo.local_gia()
    return bo


@pytest.fixture
def hang():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["ung_vien"].extend([
        {**bo.doan(), "ma_ung_vien": "DEMO-UV-2", "diem_tim_kiem": 0.6},
        {**bo.doan(), "ma_ung_vien": "DEMO-UV-3", "diem_tim_kiem": 0.4}])
    bo.chuan_bi_hau("xep_hang_lai", yc)
    bo.local_gia()
    return bo


@pytest.mark.parametrize("ma", ["DEMO-VAY-A", "DEMO-VAY-B", "0007", "007", "DEMO-VAY-AB"])
def test_tap_thuc_the_chinh_xac_khong_trung_theo_ngu_nghia_hoac_bo_so_0(ma):
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["cau_hoi"] = f"Giá trị khoản vay {ma} là bao nhiêu VND?"
    bo.chuan_bi_hau(yc=yc)
    bo.local_gia(bo.du_lieu_local(ma_thuc_the=ma))
    kq = dat(bo, bo.hau_kiem())
    assert kq["thuc_the"] == [{"loai": "khoan_vay", "ma": ma, "gia_tri": ma}]
    assert kq["ham_de_xuat"][0]["tham_so"] == {"ma_khoan_vay": ma}
    assert kq["can_lam_ro"] is False
    for can_cu in kq["can_cu_thuc_the"]:
        assert yc["du_lieu"]["cau_hoi"][can_cu["bat_dau"]:can_cu["ket_thuc"]] == can_cu["cau"] == ma


@pytest.mark.parametrize("sai", ["doi-ma", "gia-tri-khac", "thieu", "thua", "trung", "doi-loai"])
def test_ai_khong_duoc_doi_them_bot_tap_thuc_the(cau, sai):
    d = cau.pb_local["tra_loi_ai"]["du_lieu"]
    if sai == "doi-ma": d["thuc_the"][0].update(ma="DEMO-VAY-B", gia_tri="DEMO-VAY-B")
    elif sai == "gia-tri-khac": d["thuc_the"][0]["gia_tri"] = "DEMO-VAY-B"
    elif sai == "thieu": d["thuc_the"] = []
    elif sai == "thua": d["thuc_the"].append(deepcopy(THUC_THE[1]))
    elif sai == "trung": d["thuc_the"].append(deepcopy(d["thuc_the"][0]))
    else: d["thuc_the"][0]["loai"] = "hop_dong"
    loi(cau.hau_kiem(), "TC_AI_SAI_KHUON")


def test_so_0_dau_khong_duoc_chuyen_thanh_so_hoac_ma_ngan_hon():
    for thay in ("007", "7", 7):
        bo = BoHauKiem()
        yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
        yc["du_lieu"]["cau_hoi"] = "Giá trị khoản vay 0007?"
        bo.chuan_bi_hau(yc=yc)
        d = bo.du_lieu_local(ma_thuc_the="0007")
        d["thuc_the"][0]["ma"] = thay
        bo.local_gia(d)
        loi(bo.hau_kiem(), "TC_AI_SAI_KHUON")


def test_nhieu_khoan_vay_mo_ho_khong_chon_bua_ham():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["cau_hoi"] = "Giá trị khoản vay DEMO-VAY-A hay DEMO-VAY-B?"
    bo.chuan_bi_hau(yc=yc)
    d = bo.du_lieu_local()
    d["thuc_the"] = deepcopy(THUC_THE[:2])
    bo.local_gia(d)  # Model tự chọn A, hậu kiểm không chọn theo.
    kq = dat(bo, bo.hau_kiem())
    assert kq["can_lam_ro"] is True and kq["ham_de_xuat"] == []
    assert kq["tang_1"]["trang_thai"] == "can_lam_ro" and not kq["de_nghi_tang_2"]


@pytest.mark.parametrize("cau_hoi", ["Giá trị khoản vay đó?", "Giá trị DEMO-VAY-LA?", "Đề nghị DEMO-VAY-A?"])
def test_khong_ro_thuc_the_hoac_y_dinh_thi_can_lam_ro(cau_hoi):
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["cau_hoi"] = cau_hoi
    bo.chuan_bi_hau(yc=yc)
    d = bo.du_lieu_local()
    d["ham_de_xuat"] = []
    if "DEMO-VAY-A" not in cau_hoi:
        d["thuc_the"] = []
    if "Giá trị" not in cau_hoi:
        d["y_dinh"] = "can_lam_ro"
    bo.local_gia(d)
    assert dat(bo, bo.hau_kiem())["can_lam_ro"] is True


def test_core_bao_ngu_canh_chua_phan_giai_duoc(cau):
    cau.meta["can_lam_ro"] = True
    assert dat(cau, cau.hau_kiem())["ham_de_xuat"] == []


def test_cung_chu_nhieu_loai_thuc_the_phai_lam_ro(cau):
    x = {"loai": "hop_dong", "ma": "DEMO-HD-A", "gia_tri": "DEMO-VAY-A"}
    cau.meta["thuc_the"].append(x)
    cau.pb_local["tra_loi_ai"]["du_lieu"]["thuc_the"].append(x)
    assert dat(cau, cau.hau_kiem())["can_lam_ro"] is True


def test_thuc_the_lap_nhieu_lan_khong_nhan_ban_chung_cu():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["cau_hoi"] = "Giá trị " + "DEMO-VAY-A, " * 200
    bo.chuan_bi_hau(yc=yc)
    bo.local_gia()
    kq = dat(bo, bo.hau_kiem())
    assert len(kq["can_cu_thuc_the"]) == 1 and kq["can_lam_ro"] is False


@pytest.mark.parametrize("moc,tu_ngay,den_ngay", [
    ("2024-02-29T23:59:00-09:00", "2024-02-01", "2024-02-29"),
    ("2027-01-01T00:01:00+14:00", "2027-01-01", "2027-01-31")])
def test_thang_nay_dung_moc_core_khong_dung_gio_may_model(moc, tu_ngay, den_ngay, monkeypatch):
    monkeypatch.setitem(NGU_CANH, "thoi_diem", moc)
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["cau_hoi"] = "Giá trị khoản vay DEMO-VAY-A tháng này?"
    bo.chuan_bi_hau(yc=yc)
    d = bo.du_lieu_local()
    d["phu_thuoc_thoi_diem"] = True
    bo.local_gia(d)
    kq = dat(bo, bo.hau_kiem())
    assert kq["moc_thoi_diem"] == {"thoi_diem": moc, "tu_ngay": tu_ngay, "den_ngay": den_ngay}
    assert kq["phu_thuoc_cache"]["duoc_tai_dung_cache"] is False


def test_y_dinh_lai_suat_co_co_thoi_diem_do_core_cap():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["cau_hoi"] = "Lãi suất khoản vay DEMO-VAY-A?"
    bo.chuan_bi_hau(yc=yc)
    d = bo.du_lieu_local()
    d.update(y_dinh="lai_suat", phu_thuoc_thoi_diem=True, ham_de_xuat=[])
    bo.local_gia(d)
    assert dat(bo, bo.hau_kiem())["phu_thuoc_thoi_diem"] is True


@pytest.mark.parametrize("truong,gia_tri", [("phu_thuoc_thoi_diem", True), ("thoi_diem", "2030-01-01T00:00:00+07:00"),
                                          ("y_dinh", "lai_suat"), ("y_dinh", "SELECT * FROM DEMO")])
def test_model_khong_duoc_tu_doi_y_dinh_va_co_moc_thoi_diem(cau, truong, gia_tri):
    cau.pb_local["tra_loi_ai"]["du_lieu"][truong] = gia_tri
    loi(cau.hau_kiem(), "TC_AI_SAI_KHUON")


@pytest.mark.parametrize("sua", [
    {"ten": "m9.ham_la"}, {"ten": "SELECT * FROM DEMO"}, {"ten": "https://demo.invalid"},
    {"phien_ban": "2"}, {"tham_so": {"ma_khoan_vay": 7}},
    {"tham_so": {"ma_khoan_vay": "DEMO-VAY-A", "thua": "DEMO"}},
    {"tham_so": {"sql": "SELECT * FROM DEMO"}}, {"tham_so": {"code": "DEMO"}},
    {"tham_so": {"ma_khoan_vay": "eval('DEMO')"}},
    {"tham_so": {"ma_khoan_vay": "https://demo.invalid"}},
    {"tham_so": {"ma_khoan_vay": "DEMO-VAY-B"}}, {"du_lieu_tang_1": 1000000}])
def test_ham_ten_phien_ban_sql_code_url_kieu_va_khoa_thua(cau, sua):
    cau.pb_local["tra_loi_ai"]["du_lieu"]["ham_de_xuat"][0].update(sua)
    loi(cau.hau_kiem(), {"TC_AI_SAI_KHUON", "TC_HAM_KHONG_DUOC_PHEP"})


def test_de_xuat_ham_trung_bi_tu_choi(cau):
    d = cau.pb_local["tra_loi_ai"]["du_lieu"]
    d["ham_de_xuat"] *= 2
    loi(cau.hau_kiem(), {"TC_AI_SAI_KHUON", "TC_HAM_KHONG_DUOC_PHEP"})


def test_khong_duoc_bo_tham_so_thuc_the_de_mo_rong_pham_vi(cau):
    cau.pb_local["tra_loi_ai"]["du_lieu"]["ham_de_xuat"][0]["tham_so"] = {}
    loi(cau.hau_kiem(), "TC_HAM_KHONG_DUOC_PHEP")


def test_ham_dung_allowlist_nhung_sai_y_dinh_van_tu_choi(cau):
    cau.meta["ham"]["m9.gia_tri"]["y_dinh"] = ["lai_suat"]
    loi(cau.hau_kiem(), "TC_HAM_KHONG_DUOC_PHEP")


def test_core_rang_buoc_tham_so_nguyen_dung_kieu_va_phap_nhan():
    for p in ("DEMO-P", "DEMO-P-KHAC"):
        bo = BoHauKiem()
        yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
        schema = yc["du_lieu"]["ham"][0]["schema_tham_so"]
        schema["properties"]["phap_nhan_id"] = {"type": "string"}
        bo.chuan_bi_hau(yc=yc)
        bo.meta["ham"]["m9.gia_tri"]["rang_buoc"]["phap_nhan_id"] = {"loai": "ngu_canh", "truong": "phap_nhan_id"}
        d = bo.du_lieu_local()
        d["ham_de_xuat"][0]["tham_so"]["phap_nhan_id"] = p
        bo.local_gia(d)
        if p == "DEMO-P": dat(bo, bo.hau_kiem())
        else: loi(bo.hau_kiem(), "TC_HAM_KHONG_DUOC_PHEP")


@pytest.mark.parametrize("quyen", [{"nhom": "07"}, {"phap_nhan_id": "DEMO-P-KHAC"},
                                  {"ma_pham_vi": "DEMO-PV-KHAC"}, {"module": "M4"}, {"admin": True}])
def test_ham_khong_duoc_vuot_pham_vi_core(quyen):
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["ham"][0]["quyen"] = quyen
    bo.chuan_bi_hau(yc=yc)
    bo.local_gia()
    loi(bo.hau_kiem(), "TC_HAM_KHONG_DUOC_PHEP")


@pytest.mark.parametrize("trang_thai,ket_thuc", [("chua_chay", "cho"), ("khong_kha_dung", "khong_kha_dung"),
                                              ("kha_dung", "chua_thuc_hien")])
def test_trang_thai_module_khong_gia_thanh_du_lieu_tang_1(cau, trang_thai, ket_thuc):
    cau.meta["ham"]["m9.gia_tri"]["trang_thai"] = trang_thai
    kq = dat(cau, cau.hau_kiem())
    assert kq["tang_1"]["trang_thai"] == ket_thuc
    assert set(kq["tang_1"]) == {"trang_thai", "ly_do"}
    assert kq["de_nghi_tang_2"] is (trang_thai != "kha_dung")


@pytest.mark.parametrize("gia_tri", [0, 13, True, "2", 2.5])
def test_rang_buoc_schema_tham_so_so_nguyen(gia_tri):
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    schema = yc["du_lieu"]["ham"][0]["schema_tham_so"]
    schema["properties"]["so_thang"] = {"type": "integer", "minimum": 1, "maximum": 12}
    schema["required"] = ["ma_khoan_vay", "so_thang"]
    bo.chuan_bi_hau(yc=yc)
    bo.meta["ham"]["m9.gia_tri"]["rang_buoc"]["so_thang"] = {"loai": "gia_tri", "cho_phep": [1, 2, 3]}
    d = bo.du_lieu_local()
    d["ham_de_xuat"][0]["tham_so"]["so_thang"] = gia_tri
    bo.local_gia(d)
    loi(bo.hau_kiem(), "TC_AI_SAI_KHUON")


def test_schema_ref_noi_bo_nested_va_tham_so_ngu_canh():
    for thua in (False, True):
        bo = BoHauKiem()
        yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
        schema = yc["du_lieu"]["ham"][0]["schema_tham_so"]
        schema.update({"$defs": {"loc": {"type": "object", "required": ["phap_nhan_id"],
            "properties": {"phap_nhan_id": {"type": "string"}}}}})
        schema["properties"]["loc"] = {"$ref": "#/$defs/loc"}
        bo.chuan_bi_hau(yc=yc)
        bo.meta["ham"]["m9.gia_tri"]["rang_buoc"]["loc"] = {"loai": "gia_tri", "cho_phep": [{"phap_nhan_id": "DEMO-P"}]}
        d = bo.du_lieu_local()
        d["ham_de_xuat"][0]["tham_so"]["loc"] = {"phap_nhan_id": "DEMO-P", **({"thua": "DEMO"} if thua else {})}
        bo.local_gia(d)
        if thua: loi(bo.hau_kiem(), "TC_AI_SAI_KHUON")
        else: dat(bo, bo.hau_kiem())


@pytest.mark.parametrize("schema_con", [{"type": ["object", "null"]}, True, {}])
def test_schema_mo_khong_duoc_dung_de_gui_khoa_thua(schema_con):
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["ham"][0]["schema_tham_so"]["properties"]["loc"] = schema_con
    bo.chuan_bi_hau(yc=yc)
    # Dù Core giới hạn nguyên giá trị, khóa không khai ở schema vẫn bị từ chối.
    bo.meta["ham"]["m9.gia_tri"]["rang_buoc"]["loc"] = {"loai": "gia_tri", "cho_phep": [{"thua": "DEMO"}]}
    d = bo.du_lieu_local()
    d["ham_de_xuat"][0]["tham_so"]["loc"] = {"thua": "DEMO"}
    bo.local_gia(d)
    loi(bo.hau_kiem(), "TC_AI_SAI_KHUON")


@pytest.mark.parametrize("ten_schema,v,dat_du_kien", [
    ({"type": "number", "multipleOf": 0.1}, 0.3, True),
    ({"type": "number", "multipleOf": 0.1}, 0.35, False),
    ({"enum": [1]}, True, False), ({"const": "0007"}, "007", False),
    ({"allOf": [{"minimum": 1}, {"exclusiveMaximum": 3}]}, 3, False),
    ({"anyOf": [{"type": "null"}, {"type": "string", "minLength": 2}]}, "DEMO", True),
    ({"oneOf": [{"type": "number"}, {"type": "integer"}]}, 1, False),
    ({"type": "array", "uniqueItems": True, "items": {"type": "string"}}, ["DEMO", "DEMO"], False),
    ({"type": "array", "prefixItems": [{"const": "0007"}], "items": False}, ["0007"], True),
    ({"type": "array", "prefixItems": [{"const": "0007"}], "items": False}, ["0007", "DEMO"], False),
    ({"not": {"type": "null"}}, None, False), ({"format": "uri"}, "DEMO", False),
    ({"$ref": "https://demo.invalid/schema"}, "DEMO", False),
])
def test_bo_kiem_khuon_tu_choi_tu_khoa_la_khong_bo_qua_rang_buoc(ten_schema, v, dat_du_kien):
    assert cau_hoi.khop_khuon(v, ten_schema) is dat_du_kien


def test_xep_hang_diem_giam_dan_tie_theo_thu_tu_core(hang):
    ds = hang.pb_local["tra_loi_ai"]["du_lieu"]["xep_hang"]
    ds.reverse()
    ds[0]["diem"] = 0.9
    kq = dat(hang, hang.hau_kiem())
    assert [x["ma_ung_vien"] for x in kq["xep_hang"]] == ["DEMO-UV-3", "DEMO-UV-1", "DEMO-UV-2"]
    for x in kq["xep_hang"]:
        goc = next(u for u in hang.s_ai["du_lieu"]["ung_vien"] if u["ma_ung_vien"] == x["ma_ung_vien"])
        assert {k: v for k, v in x.items() if k != "diem_xep_hang"} == goc
    assert kq["diem_chi_de_sap_xep"] is True and "do_tin_cay" not in kq


@pytest.mark.parametrize("sai", ["doi", "trung", "thieu", "them", "nguon", "noi_dung", "phien_ban"])
def test_xep_hang_khong_them_bot_doi_ung_vien_nguon(hang, sai):
    ds = hang.pb_local["tra_loi_ai"]["du_lieu"]["xep_hang"]
    if sai == "doi": ds[0]["ma_ung_vien"] = "DEMO-UV-LA"
    elif sai == "trung": ds[0]["ma_ung_vien"] = ds[1]["ma_ung_vien"]
    elif sai == "thieu": ds.pop()
    elif sai == "them": ds.append({"ma_ung_vien": "DEMO-UV-LA", "diem": 0.8})
    elif sai == "nguon": ds[0]["ma_nguon"] = "DEMO-NGUON-KHAC"
    elif sai == "noi_dung": ds[0]["nguyen_van"] = "DEMO đổi nội dung"
    else: ds[0]["phien_ban_nguon"] = "2"
    loi(hang.hau_kiem(), "TC_AI_SAI_KHUON")


@pytest.mark.parametrize("diem", [float("nan"), float("inf"), -float("inf"), -0.01, 1.01, True, "0.8", None])
def test_diem_phai_huu_han_dung_thang(hang, diem):
    hang.pb_local["tra_loi_ai"]["du_lieu"]["xep_hang"][0]["diem"] = diem
    loi(hang.hau_kiem(), "TC_AI_SAI_KHUON")


def test_thang_diem_khong_mac_dinh_0_1():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["thang_diem"] = {"toi_thieu": -10, "toi_da": 10}
    bo.chuan_bi_hau("xep_hang_lai", yc)
    bo.local_gia({"xep_hang": [{"ma_ung_vien": "DEMO-UV-1", "diem": 10}]})
    assert dat(bo, bo.hau_kiem())["xep_hang"][0]["diem_xep_hang"] == 10


def test_xep_hang_giu_nguyen_hai_nguon_va_tu_choi_nguon_bi_thu_quyen():
    bo = BoHauKiem()
    chu = "Phụ lục DEMO cho khoản vay DEMO-VAY-B, 2026-10-30."
    goc = bo.tai("nguon-2-DEMO.txt", chu.encode("utf-8"), "text/plain")
    pb = deepcopy(bo.pb_vb)
    pb["van_ban_tai_lieu"].update(van_ban=chu, bam_dau_vao=goc["bam"])
    vb = bo.tai("van-ban-2-DEMO.json", json_chuan(pb))
    n = {"ma_nguon": "DEMO-NGUON-2", "tep_id": goc["tep"]["tep_id"], "phien_ban_nguon": "2",
         "bam_goc": goc["bam"], "bam_van_ban": bam(chu.encode("utf-8"))}
    bo.nguon_duoc_cap[n["ma_nguon"]] = n
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["nguon"].append({"ma_nguon": n["ma_nguon"], "phien_ban_nguon": "2", "goc": goc, "van_ban": vb})
    yc["du_lieu"]["ung_vien"].append({**{k: v for k, v in n.items() if k != "tep_id"},
        "nguyen_van": chu, "bat_dau": 0, "ket_thuc": len(chu), "vi_tri": {"trang": None, "hop": None},
        "ma_ung_vien": "DEMO-UV-2", "diem_tim_kiem": 0.4})
    bo.chuan_bi_hau("xep_hang_lai", yc)
    bo.local_gia()
    kq = dat(bo, bo.hau_kiem())
    assert len(kq["phu_thuoc_cache"]["nguon"]) == 2
    assert {k: kq["phu_thuoc_cache"]["nguon"][1][k] for k in n} == n
    bo.giao_hau()
    bo.core.cua.giay_cap[bo.hau_id]["nguon"].pop(n["ma_nguon"])
    bo.core.chay(bo.app)
    loi(bo.core.xem(bo.hau_id), "TC_CHUA_CO_CUA_CORE")


def test_core_gia_loc_truoc_ngu_canh_khong_chung_nhan_rls_that():
    bo = BoHauKiem()
    # Adapter Core lọc trước khi ghép, không giao nguồn ngoài quyền cho engine.
    nguon_gia = [{"phap_nhan": "DEMO-P", "nhom": "02", "ung_vien": {**bo.doan(),
        "ma_ung_vien": "DEMO-UV-1", "diem_tim_kiem": 0.8}},
        {"phap_nhan": "DEMO-Q", "nhom": "07", "ung_vien": {"nguyen_van": "DEMO-NGOAI-QUYEN"}}]
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["ung_vien"] = [x["ung_vien"] for x in nguon_gia
                                  if x["phap_nhan"] == "DEMO-P" and x["nhom"] in NGU_CANH["nhom"]]
    bo.chuan_bi_hau("xep_hang_lai", yc)
    assert "DEMO-NGOAI-QUYEN" not in bo.pb_ai["yeu_cau_ai"]["tai_lieu"]
    bo.local_gia()
    assert len(dat(bo, bo.hau_kiem())["xep_hang"]) == 1


def test_xep_hang_cau_thoi_diem_khong_cho_cache_du_core_chua_gan_co():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["cau_hoi"] += " tháng này"
    bo.chuan_bi_hau("xep_hang_lai", yc)
    bo.local_gia()
    assert dat(bo, bo.hau_kiem())["phu_thuoc_cache"]["duoc_tai_dung_cache"] is False


def test_0_ung_vien_core_re_nhanh_khong_ai():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"].update(ung_vien=[], nguon=[])
    bo.nhan_ai("xep_hang_lai", yc)
    assert bo.pb_nhan["ho_so_tra_cuu"]["tom_tat"]["so_ung_vien"] == 0
    loi(bo.chuan_bi(), "TC_SAI_GIAI_DOAN")
    assert bo.so_luot_local == 0


@pytest.mark.parametrize("so_luong,ma_loi", [(50, None), (51, "TC_QUA_GIOI_HAN")])
def test_tran_ung_vien_khong_cat_top_k(so_luong, ma_loi):
    bo = BoHauKiem(van_ban="DEMO ngắn.")
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["ung_vien"] = [{**bo.doan(), "ma_ung_vien": f"DEMO-UV-{i:02}", "diem_tim_kiem": 0.5}
                                 for i in range(so_luong)]
    if ma_loi:
        loi(bo.chay(yc), ma_loi)
    else:
        bo.chuan_bi_hau("xep_hang_lai", yc)
        bo.local_gia()
        assert len(dat(bo, bo.hau_kiem())["xep_hang"]) == 50


def test_ngan_sach_da_ghim_tu_choi_khong_top_k(hang):
    def sua(s):
        s["cau_hinh"]["gia_tri"]["ngan_sach"]["so_ung_vien_toi_da"] = 2
    pb = hang.doi_snapshot(sua)
    c = pb["tra_loi_ai"]["chuyen_tiep"]["tra_cuu"]
    s = hang.core.doc_tep(c["ho_so"]["tep_id"])
    from e_tra_cuu.kiem_dau_vao import doc_json
    c["bam_cau_hinh"] = bam(json_chuan(doc_json(s)["cau_hinh"]["gia_tri"]))
    loi(hang.hau_kiem(pb), "TC_QUA_NGAN_SACH_AI")


@pytest.mark.parametrize("sai", ["prompt", "phien_ban_prompt", "bam", "task", "chuyen_tiep", "phap_nhan", "cloud", "provider"])
def test_giu_dung_nguon_prompt_tac_vu_va_local(cau, sai):
    pb = deepcopy(cau.pb_local)
    a = pb["tra_loi_ai"]
    if sai == "prompt": a["ma_prompt"] = "demo.khac"
    elif sai == "phien_ban_prompt": a["phien_ban_prompt"] = "2"
    elif sai == "bam": a["bam_dau_vao"] = bam(b"DEMO sai")
    elif sai == "task": a["chuyen_tiep"]["tra_cuu"]["tac_vu"] = "xep_hang_lai"
    elif sai == "chuyen_tiep": a["chuyen_tiep"]["tra_cuu"]["ma_yeu_cau"] = "DEMO-YC-KHAC"
    elif sai in {"cloud", "provider"}: a["nha_cung_cap"] = "cloud" if sai == "cloud" else "DEMO-la"
    kq = cau.hau_kiem(pb, phap_nhan="DEMO-P-KHAC" if sai == "phap_nhan" else "DEMO-P")
    loi(kq, "TC_CHI_LOCAL" if sai == "cloud" else "TC_SAI_NGUON")


@pytest.mark.parametrize("sua", [
    lambda s: s["ai"].update(prompt="DEMO đổi prompt"),
    lambda s: s["ai"]["khuon_tra_loi"].update(additionalProperties=True),
    lambda s: s["ai"]["map_nguon"][0].update(ai_bat_dau=0),
    lambda s: s["ai"]["ngan_sach"].update(token_thuc=0, trang_thai_token="da_do"),
    lambda s: s["nguon"][0].update(phien_ban_nguon="2"),
    lambda s: s["du_lieu"]["ung_vien"][0].update(nguyen_van="DEMO nội dung đổi"),
])
def test_snapshot_bam_dung_cung_phai_doi_chieu_nguon_va_khuon(hang, sua):
    loi(hang.hau_kiem(hang.doi_snapshot(sua)), "TC_SAI_NGUON")


@pytest.mark.parametrize("sai", ["nguyen_van", "offset", "nhan_ky_thuat", "kiem_false", "trang_thai", "rong"])
def test_khong_tin_co_trich_dan_tu_khai(cau, sai):
    a = cau.pb_local["tra_loi_ai"]
    if sai == "nguyen_van": a["trich_dan"][0]["cau"] = "DEMO bịa"
    elif sai == "offset": a["trich_dan"][0]["bat_dau"] += 1
    elif sai == "nhan_ky_thuat":
        a["trich_dan"] = [{"cau": cau.s_ai["ai"]["tai_lieu"][:5], "bat_dau": 0, "ket_thuc": 5}]
    elif sai == "kiem_false": a["kiem_trich_dan"]["dat"] = False
    elif sai == "trang_thai": a["trang_thai"] = "khong_thay_can_cu"
    else: a["trich_dan"] = []
    loi(cau.hau_kiem(), "TC_AI_SAI_KHUON")


@pytest.mark.parametrize("sai", ["thieu-cua", "thieu-cap", "thieu-phan-giai", "sai-bam-cau-hoi", "sai-nhom"])
def test_core_chua_co_cua_hoac_sai_scope_tu_choi(cau, sai):
    cau.giao_hau(cap=sai != "thieu-cap")
    if sai == "thieu-cua": cau.app.cua_nguon = None
    elif sai == "thieu-phan-giai": cau.core.cua.giay_cap[cau.hau_id].pop("phan_giai_cau_hoi")
    elif sai == "sai-bam-cau-hoi": cau.core.cua.giay_cap[cau.hau_id]["phan_giai_cau_hoi"]["bam_cau_hoi"] = bam(b"DEMO")
    elif sai == "sai-nhom": cau.core.cua.giay_cap[cau.hau_id]["ngu_canh_core"]["nhom"] = ["07"]
    cau.core.chay(cau.app)
    loi(cau.core.xem(cau.hau_id), "TC_SAI_NGUON" if sai in {"sai-bam-cau-hoi", "sai-nhom"} else "TC_CHUA_CO_CUA_CORE")


def test_xep_hang_ngu_canh_khac_phap_nhan_tu_choi(hang):
    loi(hang.hau_kiem(phap_nhan="DEMO-Q"), "TC_SAI_NGUON")


@pytest.mark.parametrize("du_lieu", [None, {}, {"xep_hang": []}, {"xep_hang": [], "nhan": "xanh"}])
def test_ai_rong_sai_khuon_khong_xong_rong(hang, du_lieu):
    hang.pb_local["tra_loi_ai"]["du_lieu"] = du_lieu
    loi(hang.hau_kiem(), "TC_AI_SAI_KHUON")


def test_unicode_code_point_nfd_giu_nguyen_cau_hoi():
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    q = "😀 a\u0301. Giá trị khoản vay DEMO-VAY-A?"
    yc["du_lieu"]["cau_hoi"] = q
    bo.chuan_bi_hau(yc=yc)
    bo.local_gia()
    kq = dat(bo, bo.hau_kiem())
    assert kq["can_cu_thuc_the"][0]["bat_dau"] == q.index("DEMO-VAY-A")
    assert q[kq["can_cu_y_dinh"][0]["bat_dau"]:kq["can_cu_y_dinh"][0]["ket_thuc"]] == "Giá trị"


def test_nhom_07_chi_local_du_core_da_cap_nhom(monkeypatch):
    monkeypatch.setitem(NGU_CANH, "nhom", ["07"])
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
    yc["du_lieu"]["ham"][0]["quyen"] = {"nhom": "07"}
    bo.chuan_bi_hau(yc=yc)
    bo.local_gia()
    dat(bo, bo.hau_kiem())
    bo.pb_local["tra_loi_ai"]["nha_cung_cap"] = "cloud"
    loi(bo.hau_kiem(), "TC_CHI_LOCAL")


@pytest.mark.parametrize("moc", ["doc", "khuon", "thuc_the", "ham", "truoc_tai", "sau_tai"])
def test_huy_tung_cum_khong_xong_gia(cau, moc, monkeypatch):
    cau.giao_hau()
    truoc = cau.core.so_lan_ghi["ket_qua"]
    if moc == "doc": cau.core.sau_doc = lambda *args: cau.core.huy(cau.hau_id)
    elif moc in {"khuon", "thuc_the", "ham"}:
        ten = {"khuon": "khop_khuon", "thuc_the": "_phan_giai", "ham": "_kiem_ham"}[moc]
        goc = getattr(cau_hoi, ten)
        def huy(*args, **kwargs):
            cau.core.huy(cau.hau_id)
            return goc(*args, **kwargs)
        monkeypatch.setattr(cau_hoi, ten, huy)
    elif moc == "truoc_tai":
        def td(*args): raise ViecDaHuy()
        monkeypatch.setattr(Viec, "tien_do", td)
    else:
        goc = Viec.tai_tep_ra
        def tai(viec, *args):
            goc(viec, *args)
            raise ViecDaHuy()
        monkeypatch.setattr(Viec, "tai_tep_ra", tai)
    cau.core.chay(cau.app)
    kq = cau.core.xem(cau.hau_id)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert cau.core.so_lan_ghi["ket_qua"] == truoc


def test_huy_tung_ung_vien_khi_xep_hang(hang, monkeypatch):
    hang.giao_hau()
    goc = xep_hang.deepcopy
    dem = 0
    def copy(v):
        nonlocal dem
        dem += 1
        if dem == 2: hang.core.huy(hang.hau_id)
        return goc(v)
    monkeypatch.setattr(xep_hang, "deepcopy", copy)
    hang.core.chay(hang.app)
    kq = hang.core.xem(hang.hau_id)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None


@pytest.mark.parametrize("sai", ["chua_ro", "mat_lease", "sai_ack"])
def test_upload_chua_ro_mat_lease_ack_sai_khong_xong_gia(cau, sai, monkeypatch):
    goc = Viec.tai_tep_ra
    def tai(viec, *args):
        tep = goc(viec, *args)
        if sai == "chua_ro": raise ChuaRo("DEMO-upload-TC6")
        if sai == "mat_lease": raise LoiDuongTruyen("MAT_LEASE", http_status=409)
        return {**tep, "kich_thuoc": tep["kich_thuoc"] + 1}
    monkeypatch.setattr(Viec, "tai_tep_ra", tai)
    kq = cau.hau_kiem()
    assert kq["trang_thai"] != "XONG" and kq["ket_qua"] is None
    if sai == "chua_ro": assert kq["trang_thai"] == "CHUA_RO" and kq["ma_tuong_quan"] == "DEMO-upload-TC6"
    elif sai == "sai_ack": loi(kq, "TC_SAI_NGUON")


def test_khong_ghi_tep_cau_hinh_cache_nhat_ky_cuc_bo(cau, hang, monkeypatch):
    goc = builtins.open
    def mo(tep, mode="r", *args, **kwargs):
        if any(x in mode for x in "wax+"): pytest.fail("Engine không ghi đĩa.")
        return goc(tep, mode, *args, **kwargs)
    monkeypatch.setattr(builtins, "open", mo)
    monkeypatch.setattr(Path, "write_text", lambda *args, **kwargs: pytest.fail("Không ghi đĩa."))
    monkeypatch.setattr(Path, "write_bytes", lambda *args, **kwargs: pytest.fail("Không ghi đĩa."))
    dat(cau, cau.hau_kiem())
    dat(hang, hang.hau_kiem())


def test_harness_hau_kiem_local_gia():
    kq = chay_demo_hau_kiem()
    assert len(kq) == 4 and all(x["trang_thai"] == "XONG" for x in kq), kq
