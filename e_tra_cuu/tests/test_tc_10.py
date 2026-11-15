"""TC-10: đo cơ chế DEMO và adapter hợp đồng Core; không accuracy thật."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen

from e_tra_cuu import chay
from core_hop_dong_tc_10 import CacheHopDongGia, DieuPhoiBaTangGia, loc_nguon_truoc_ai
from ho_tro_tc_2 import GOI, NGU_CANH
from ho_tro_tc_10 import (BoTraLoiTC10, CHI_SO, DEMO, cham, chay_bo_do, chay_ca,
                         chay_nam_tac_vu, doc_nguon, ghi_dot_kiem_core_gia, hoi_local, nap_bo, tong_hop)


@pytest.fixture(scope="module")
def bo_do():
    return chay_bo_do()


def lay_ca(ma):
    bo, _ = nap_bo()
    return bo, deepcopy(next(c for c in bo["kich_ban"] if c["ma"] == ma))


def test_bon_chi_so_demo_co_tu_mau_rieng_khong_co_accuracy_that(bo_do):
    report, q = bo_do
    assert report["so_ca"] == report["so_ca_dat"] == 38
    assert {k: (v["tu_so"], v["mau_so"]) for k, v in report["chi_so"].items()} == {
        "tra_loi_dung": (12, 12), "trich_dan_dung": (12, 12), "tu_choi_dung": (6, 6), "phan_loai_dung": (20, 20)}
    assert all(v["skip"] == v["chua_do"] == v["loi_chay"] == 0 for v in report["chi_so"].values())
    assert report["accuracy_model_that"] is report["nguong_tin_cay_that"] is None
    assert report["nhom_duoc_kich_hoat"] == [] and report["da_duyet_nghiep_vu"] is False
    assert report["core_that"] == "chua_kiem" and report["so_luot_cloud"] == 0
    assert set(report["theo_nhom"]) == {f"{n:02}" for n in range(1, 9)}
    assert len([x for x in q.values() if x["xuat"]["tac_vu"] == "soan_tra_loi"]) == 18
    for c in q.values():
        if c["so_luot_local_gia"]:
            assert c["so_luot_local_gia"] == 1 and c["prompts"]


def test_fixture_co_nguon_dap_an_gim_bam_offset_nguyen_van():
    bo, vang = nap_bo()
    for ca in bo["kich_ban"]:
        for k in vang[ca["ma"]].get("khang_dinh", []):
            for c in k["can_cu"]:
                index = int(c["ma_nguon"].rsplit("-", 1)[1]) - 1
                ma = ca["nguon"][index]
                text = doc_nguon(bo, ma)
                assert text[c["bat_dau"]:c["ket_thuc"]] == c["cau"]
                assert c["bam_goc"] == bo["nguon"][ma]["bam"]
                assert c["phien_ban_nguon"] == bo["nguon"][ma]["phien_ban"]


@pytest.mark.parametrize("sai,chi_so", [("gia_tri", "tra_loi_dung"), ("entity", "tra_loi_dung"),
    ("tien_te", "tra_loi_dung"), ("ngay", "tra_loi_dung"), ("offset", "trich_dan_dung"),
    ("phien_ban", "trich_dan_dung"), ("nguon", "trich_dan_dung"), ("bam", "trich_dan_dung")])
def test_bo_cham_khong_tu_xanh_khi_dap_an_nguon_sai(bo_do, sai, chi_so):
    _, vang = nap_bo()
    q = deepcopy({k: v for k, v in bo_do[1]["TL-Python-A"].items() if k not in {"bo"}})
    k = q["xuat"]["ket_qua"]["khang_dinh"][0]
    if sai == "gia_tri": k["gia_tri"]["so"] = 42
    elif sai == "entity": k["thuc_the"]["ma"] = "DEMO-VAY-B"
    elif sai == "tien_te": k["gia_tri"]["tien_te"] = "USD"
    elif sai == "ngay": q["xuat"]["ket_qua"]["khang_dinh"][1]["gia_tri"] = "2026-10-31"
    elif sai == "offset": k["can_cu"][0]["bat_dau"] += 1
    elif sai == "phien_ban": k["can_cu"][0]["nguon"]["phien_ban_nguon"] = "2"
    elif sai == "nguon": k["can_cu"][0]["nguon"]["ma_nguon"] = "DEMO-NGUON-2"
    else: k["can_cu"][0]["nguon"]["bam_goc"] = "sha256:" + "0" * 64
    assert not cham(vang["TL-Python-A"], q)[chi_so]


def test_bo_cham_bat_phan_loai_sai_va_tu_choi_giu_so_bia(bo_do):
    _, vang = nap_bo()
    for ma, sua, chi in [("PL-thiet_bi_lap_dat", lambda k: k.update(nhom_de_xuat="03", diem=1), "phan_loai_dung"),
                         ("TL-khong-dap-an", lambda k: k.update(tra_loi="DEMO 999 VND"), "tu_choi_dung")]:
        q = {"xuat": deepcopy(bo_do[1][ma]["xuat"])}
        sua(q["xuat"]["ket_qua"])
        assert not cham(vang[ma], q)[chi]


def test_skip_chua_do_va_loi_chay_khong_thanh_dat(bo_do):
    _, vang = nap_bo()
    q = dict(bo_do[1])
    q["TL-Python-A"] = {"trang_thai_do": "skip", "ly_do": "DEMO kiểm riêng phép tính mẫu số."}
    q.pop("TL-Python-B")
    q["TL-Local-A"] = {"trang_thai_do": "loi", "ly_do": "DEMO nguồn chưa trả."}
    r = tong_hop(vang, q)["tra_loi_dung"]
    assert r == {"tu_so": 9, "mau_so": 10, "so_ca_du_kien": 12,
                 "chua_do": 1, "skip": 1, "loi_chay": 1, "ty_le": 0.9}
    empty = tong_hop(vang, {})
    assert all(c["tu_so"] == c["mau_so"] == 0 and c["ty_le"] is None for c in empty.values())
    assert empty["phan_loai_dung"]["chua_do"] == 20
    q["TL-Python-A"].pop("ly_do")
    with pytest.raises(AssertionError):
        tong_hop(vang, q)


def test_du_nam_tac_vu_dung_loai_cho_noi_va_xuat():
    kq = chay_nam_tac_vu()
    assert {r["tac_vu"] for r in kq} == {"cat_doan", "phan_loai", "phan_tich_cau_hoi", "xep_hang_lai", "soan_tra_loi"}
    assert all(k["trang_thai"] == "XONG" for k in kq)
    caps = {n["ma"]: n for n in chay.app.phieu["nang_luc"]}
    assert caps["tra_cuu.nhan_yeu_cau@1"]["tra"] in caps["tra_cuu.chuan_bi_ai@1"]["nhan"]
    for hau in ("phan_loai_tai_lieu", "phan_tich_cau_hoi", "xep_hang_lai", "soan_tra_loi"):
        assert "tra_loi_ai" in caps["tra_cuu." + hau + "@1"]["nhan"]
        assert caps["tra_cuu." + hau + "@1"]["tra"] in caps["tra_cuu.xuat_ket_qua@1"]["nhan"]
    assert "yeu_cau_ai" not in caps["tra_cuu.xuat_ket_qua@1"]["nhan"]


def tao_tang_mot(corpus, ca, ly_do):
    c = deepcopy(ca)
    c.update(tang=1, ai=False)
    if ly_do == "THIEU_TRUONG_HOAC_THUC_THE": c["local"]["bang_chung"] = []
    elif ly_do == "CHUA_DUYET": c["trang_thai_bang"] = {"trang_thai_duyet": "cho_duyet", "moc_duyet": None}
    elif ly_do == "HET_HIEU_LUC": c["trang_thai_bang"] = {"con_hieu_luc": False, "hieu_luc_den": "2026-10-31"}
    elif ly_do == "DUOI_NGUONG_TIN_CAY": c["trang_thai_bang"] = {"do_tin_cay": 0.1}
    elif ly_do == "NGOAI_TRUONG": c["truong_bo_sung"] = [{"ma": "phi", "ten": "Phí", "kieu": "so", "don_vi": "VND"}]
    elif ly_do == "THIEU_NGUONG_DA_DO": c["thieu_nguong"] = True
    return chay_ca(c, corpus)


@pytest.mark.parametrize("ma", ["TL-Local-A", "TL-nhan-su-Local"])
@pytest.mark.parametrize("ly_do", [None, "THIEU_TRUONG_HOAC_THUC_THE", "CHUA_DUYET", "HET_HIEU_LUC",
                                   "DUOI_NGUONG_TIN_CAY", "NGOAI_TRUONG", "THIEU_NGUONG_DA_DO"])
def test_tang_mot_chi_thieu_dieu_kien_moi_di_tang_hai_local(ma, ly_do):
    corpus, ca = lay_ca(ma)
    q1 = tao_tang_mot(corpus, ca, ly_do)
    if ly_do:
        assert not q1["xuat"]["ket_qua"]["co_can_cu"]
        expected = "THIEU_TRUONG_HOAC_THUC_THE" if ly_do == "NGOAI_TRUONG" else ly_do
        assert expected in q1["xuat"]["ket_qua"]["ly_do"]
    else:
        assert q1["xuat"]["ket_qua"]["co_can_cu"]
        assert q1["so_luot_local_gia"] == 0
    q2 = []
    def tang_hai():
        q2.append(chay_ca(ca, corpus))
        return q2[-1]
    def cam_tang_ba():
        raise AssertionError("Tầng 2 đủ thì không chạy tầng 3.")
    core = DieuPhoiBaTangGia(lambda: q1, tang_hai, cam_tang_ba)
    out = core.hoi()
    assert out["http"] == 200 and out["ket_qua"]["co_can_cu"]
    assert core.da_chay == ([1, 2] if ly_do else [1]) and not core.viec_nen
    assert len(q2) == int(bool(ly_do))
    if q2:
        assert q2[0]["so_luot_local_gia"] == 1 and q2[0]["so_luot_cloud"] == 0


@pytest.mark.parametrize("ma", ["TL-Local-A", "TL-nhan-su-Local"])
def test_tang_ba_cho_202_chay_nen_local_k5_chi_de_nghi(ma):
    corpus, ca = lay_ca(ma)
    rong = deepcopy(ca)
    rong.update(ai=False, tang=2)
    rong["local"]["bang_chung"] = []
    ba = {**deepcopy(ca), "tang": 3}
    core = DieuPhoiBaTangGia(lambda: tao_tang_mot(corpus, ca, "CHUA_DUYET"),
                            lambda: chay_ca(rong, corpus), lambda: chay_ca(ba, corpus))
    pending = core.hoi()
    assert pending["http"] == 202 and pending["ket_qua"] is None and pending["trang_thai"] == "CHO"
    assert core.da_chay == [1, 2]
    ra = core.chay_nen()
    assert core.da_chay == [1, 2, 3] and ra["ket_qua"]["tang"] == 3
    assert ra["ket_qua"]["ai"]["nha_cung_cap"] == "local"
    assert ra["ket_qua"]["de_nghi_k5"] == {"du_lieu_moi": True, "co_mau_thuan": False,
                                           "da_duyet": False, "da_tao_viec": False}


def test_chua_ro_o_tang_so_huu_khong_doi_thanh_rong_hay_xong():
    corpus, ca = lay_ca("TL-Local-A")
    bo = BoTraLoiTC10(ca, corpus)
    bo.nhan_ca()
    bo.chuan_bi_soan()
    ra, local = hoi_local(bo, bo.pb_ai, bo.du_lieu_soan(), [bo.profile["bang_chung"][0]["cau"]], chua_ro=True)
    assert local.so_luot == 1 and ra["trang_thai"] == "CHUA_RO" and ra["ket_qua"] is None
    assert ra["ma_tuong_quan"] == "DEMO-TC10-local-chua-tra"
    def chua_tra():
        raise ChuaRo("DEMO-Core-tang-3")
    core = DieuPhoiBaTangGia(chua_tra, lambda: None, lambda: None)
    with pytest.raises(ChuaRo): core.hoi()
    assert core.da_chay == [1] and core.viec_nen == []


def tao_cache(q):
    p = q["xuat"]["ket_qua"]["phu_thuoc_cache"]
    nc, entities = p["ngu_canh_core"], p["thuc_the"]
    current = {n["ma_nguon"]: {"nguon": n, "nhom": nc["nhom"], "duyet": "DEMO-moc-1",
                "cong_bo": "DEMO-cong-bo-1", "con_hieu_luc": True} for n in p["nguon"]}
    ref = q["ra_xuat"]["ket_qua"]["truong"]["tep_json"]
    cache = CacheHopDongGia()
    cache.luu(nc, "DEMO-cung-ngu-nghia", entities, ref, p, current)
    return cache, nc, entities, current, ref


def test_cache_dung_thuc_the_phap_nhan_scope_va_bo_qua_cache(bo_do):
    cache, nc, entities, current, ref = tao_cache(bo_do[1]["TL-mau-thuan-Python"])
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", entities, set(current), current) == ref
    for k, v in [("phap_nhan_id", "DEMO-Q"), ("module", "M4"), ("nhom", ["07"]), ("ma_pham_vi", "DEMO-khac")]:
        assert cache.doc({**nc, k: v}, "DEMO-cung-ngu-nghia", entities, set(current), current) is None
    b = [{**entities[0], "ma": "DEMO-VAY-B", "gia_tri": "DEMO-VAY-B"}]
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", b, set(current), current) is None
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", entities, set(current), current, bo_qua_cache=True) is None
    assert "bo_qua_cache" in cache.nhat_ky
    text = json.dumps(cache.ban, default=str) if not cache.ban else json.dumps(list(cache.ban.values()), ensure_ascii=False)
    assert "1.000.000 VND" not in text and "prompt" not in text and "cau_hoi" not in text


@pytest.mark.parametrize("su_kien", ["tai_lieu.phien_ban_moi", "tai_lieu.doi_nhom", "ket_qua.da_duyet",
    "cong_bo.m9.cap_nhat", "quyen.thu_hoi", "tai_lieu.het_hieu_luc"])
@pytest.mark.parametrize("chi_so_nguon", [0, 1])
def test_cache_het_hieu_luc_khi_moi_nguon_phu_thuoc_doi(bo_do, su_kien, chi_so_nguon):
    cache, nc, entities, current, ref = tao_cache(bo_do[1]["TL-mau-thuan-Python"])
    ma = list(current)[chi_so_nguon]
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", entities, set(current) - {ma}, current) is None
    cache.su_kien(su_kien, ma)
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", entities, set(current), current) is None


@pytest.mark.parametrize("truong", ["nguon", "nhom", "duyet", "cong_bo", "con_hieu_luc"])
def test_cache_kiem_lai_metadata_khi_mat_su_kien(bo_do, truong):
    cache, nc, entities, current, _ = tao_cache(bo_do[1]["TL-mau-thuan-Python"])
    current = deepcopy(current)
    current["DEMO-NGUON-2"][truong] = "DEMO-da-doi"
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", entities, set(current), current) is None


def test_cau_phu_thuoc_thoi_diem_khong_tai_dung_cache(bo_do):
    q = bo_do[1]["TL-phu-thuoc-thoi-diem"]
    cache, nc, e, current, ref = tao_cache(q)
    assert not cache.ban and q["xuat"]["ket_qua"]["phu_thuoc_cache"]["duoc_tai_dung_cache"] is False
    assert cache.doc(nc, "DEMO-cung-ngu-nghia", e, set(current), current) is None


@pytest.mark.parametrize("ma", ["TL-Local-A", "TL-nhan-su-Local"])
def test_nguon_ngoai_quyen_khong_duoc_doc_hoac_vao_ngu_canh_ai(ma):
    corpus, ca = lay_ca(ma)
    nc = {**NGU_CANH, "nhom": [ca["nhom"]]}
    sources = [{"ma_nguon": "DEMO-cho-phep", "ma_fixture": ca["nguon"][0], "phap_nhan_id": "DEMO-P", "nhom": ca["nhom"], "con_hieu_luc": True},
               {"ma_nguon": "DEMO-khac-quyen", "phap_nhan_id": "DEMO-P", "nhom": ca["nhom"], "con_hieu_luc": True},
               {"ma_nguon": "DEMO-khac-phap-nhan", "phap_nhan_id": "DEMO-Q", "nhom": ca["nhom"], "con_hieu_luc": True},
               {"ma_nguon": "DEMO-khac-nhom", "phap_nhan_id": "DEMO-P", "nhom": "08", "con_hieu_luc": True},
               {"ma_nguon": "DEMO-het-han", "phap_nhan_id": "DEMO-P", "nhom": ca["nhom"], "con_hieu_luc": False}]
    da_doc = []
    def doc(n):
        da_doc.append(n["ma_nguon"])
        assert n["ma_nguon"] == "DEMO-cho-phep"
        return n["ma_fixture"]
    permitted = loc_nguon_truoc_ai(sources, nc, {"DEMO-cho-phep", "DEMO-khac-phap-nhan", "DEMO-khac-nhom", "DEMO-het-han"}, doc)
    assert da_doc == ["DEMO-cho-phep"] and permitted == ca["nguon"]
    # Chính kết quả lọc quyết định tập nguồn đưa cho chuỗi TC/AI kế tiếp.
    ca["nguon"] = permitted
    q = chay_ca(ca, corpus)
    prompt = "\n".join(q["prompts"])
    text = doc_nguon(corpus, permitted[0])
    assert text in prompt or json.dumps(text, ensure_ascii=False)[1:-1] in prompt
    assert list(q["bo"].cac_nguon) == permitted
    assert all(n["ma_nguon"] not in prompt for n in sources[1:])
    assert q["xuat"]["ket_qua"]["ai"]["nha_cung_cap"] == "local"


@pytest.mark.parametrize("luc", ["huy", "lease", "ack-het-luot"])
def test_loi_giua_chuoi_khong_nop_xong_gia(monkeypatch, luc):
    corpus, ca = lay_ca("TL-Local-A")
    bo = BoTraLoiTC10(ca, corpus)
    bo.nhan_ca()
    bo.local_ca()
    bo.giao_soan()
    truoc = deepcopy(bo.core.so_lan_ghi)
    if luc == "huy":
        bo.core.sau_doc = lambda i, t: bo.core.huy(i)
    elif luc == "lease":
        def mat_lease(ma, i, *args, **kwargs):
            bo.core._viec[i]["trang_thai"] = "CHO"
            raise LoiDuongTruyen("MAT_LEASE", http_status=409)
        monkeypatch.setattr(bo.core, "_tien_do", mat_lease)
    else:
        bo.core.gay_mat_xac_nhan("tep", 4)
    bo.core.chay(bo.app)
    ra = bo.core.xem(bo.soan_id)
    assert ra["trang_thai"] != "XONG" and ra["ket_qua"] is None
    assert bo.core.so_lan_ghi["ket_qua"] == truoc["ket_qua"]
    if luc == "lease": assert bo.core.so_lan_ghi["ket_thuc"] == truoc["ket_thuc"]


@pytest.mark.parametrize("thao_tac", ["tep", "ket_qua", "ket_thuc"])
def test_ack_gui_lai_cung_khoa_khong_nhan_ket_qua_hai_lan(thao_tac):
    corpus, ca = lay_ca("TL-Python-A")
    bo = BoTraLoiTC10(ca, corpus)
    bo.nhan_ca()
    truoc = deepcopy(bo.core.so_lan_ghi)
    start = len(bo.core.nhat_ky)
    bo.core.gay_mat_xac_nhan(thao_tac, 3)
    ra = bo.soan()
    assert ra["trang_thai"] == "XONG"
    assert all(bo.core.so_lan_ghi[t] - truoc[t] == 1 for t in ("tep", "ket_qua", "ket_thuc"))
    keys = [v[-1] for v in bo.core.nhat_ky[start:] if v[0] == thao_tac]
    assert len(keys) == 4 and len(set(keys)) == 1


def test_hai_mau_ngan_lich_su_va_bon_schema_khop_sha_lf():
    repo = GOI.parents[2]
    # SDK 2.2 không đưa cổng tạm trở lại runtime. Bản lưu trữ vẫn chép nguyên.
    for ten in ("ngan.py", "cau_hinh.py"):
        raw = (repo / "_chung/mau-ma" / ten).read_bytes().replace(b"\r\n", b"\n")
        copy = (repo / "e_tra_cuu/LUU-TRU/TC-S22" / ten).read_bytes().replace(b"\r\n", b"\n")
        assert sha256(raw).digest() == sha256(copy).digest()
        assert not (GOI / "e_tra_cuu" / ten).exists()
    for ma in ("van_ban_tai_lieu", "yeu_cau_ai", "tra_loi_ai", "ho_so_tra_cuu"):
        ten = ma + ".schema.json"
        assert sha256((repo / "_chung/contract" / ten).read_bytes().replace(b"\r\n", b"\n")).digest() == sha256(
            (GOI / "contract" / ten).read_bytes().replace(b"\r\n", b"\n")).digest()


def test_dot_kiem_ghi_so_do_thuc_demo_khong_diem_model_tu_khai(bo_do):
    rows, data = ghi_dot_kiem_core_gia(bo_do[0])
    assert len(rows) == 1 and rows[0]["phap_nhan_id"] == "DEMO-P"
    assert data["chi_so"]["phan_loai_dung"] == {"tu_so": 20, "mau_so": 20}
    assert set(data) == {"trang_thai", "bam_bo", "bam_cau_hinh", "phien_ban_engine", "chi_so", "bao_cao", "bam_bao_cao"}


def test_wrapper_may_sach_ascii_va_lock_khong_them_dependency():
    tests = Path(__file__).resolve().parent
    for ten in ("KIEM-MAY-SACH.cmd", "kiem_may_sach.sh"):
        raw = (tests / ten).read_bytes()
        assert raw.decode("ascii") and b"kiem_may_sach.py" in raw
    lock = (GOI / "requirements.lock").read_text(encoding="utf-8")
    assert len(lock.splitlines()) == 1 and lock.startswith("kho_tri_thuc_sdk==2.2.0 --hash=sha256:")
