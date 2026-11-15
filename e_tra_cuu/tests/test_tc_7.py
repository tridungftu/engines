"""TC-7 chỉ DEMO, đã kiểm bằng Core giả (CoreGia); không chứng nhận RLS."""

import builtins
from copy import deepcopy
import re
import socket

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, LoiNghiepVu, Viec

from e_tra_cuu.kiem_dau_vao import bam, json_chuan
from ho_tro_tc_3 import phong_bi_trang
from ho_tro_tc_4 import dieu_phoi_hoi_ai
from ho_tro_tc_7 import BoTraLoi, TRUONG, VAN_BAN, chay_demo_tra_loi


def loi(kq, ma):
    assert kq["trang_thai"] == "LOI" and kq["ket_qua"] is None, kq
    assert kq["loi"]["ma"] == ma, kq


def ket_qua(bo, ra):
    assert ra["trang_thai"] == "XONG", ra
    h = ra["ket_qua"]["ho_so_tra_cuu"]
    s = bo.snapshot(ra)
    r = s["ket_qua"]
    assert h["giai_doan"] == s["giai_doan"] == "da_soan"
    for k in ("trang_thai", "tang", "co_can_cu", "co_mau_thuan", "can_duyet", "nhan"):
        assert h["tom_tat"][k] == r[k]
    assert s["du_lieu"] == bo.s_nhan["du_lieu"]
    assert r["phu_thuoc_cache"]["thuc_the"] == s["du_lieu"]["thuc_the"]
    return r


def khong_can_cu(bo, ra):
    r = ket_qua(bo, ra)
    assert r["trang_thai"] == "khong_thay_can_cu" and not r["co_can_cu"]
    assert r["nhan"] is None and r["khang_dinh"] == [] and r["ly_do"]
    assert not re.search(r"[0-9]", r["tra_loi"])
    return r


@pytest.fixture
def ai():
    bo = BoTraLoi()
    bo.nhan_soan(2)
    bo.chuan_bi_soan()
    bo.local_soan()
    return bo


@pytest.mark.parametrize("tang,ai", [(1, False), (1, True), (2, True), (3, True)])
def test_hai_duong_nhan_tien_ngay_dung_nguon_tung_ky_tu(tang, ai):
    bo = BoTraLoi()
    bo.nhan_soan(tang)
    if ai:
        bo.chuan_bi_soan()
        bo.local_soan()
    r = ket_qua(bo, bo.soan())
    assert r["tra_loi"] == "Giá trị (DEMO-VAY-A): 1.000.000 VND.\nNgày (DEMO-VAY-A): 2026-10-30."
    assert r["nhan"] == ("vang" if ai else "xanh") and r["tang"] == tang
    assert r["khang_dinh"][0]["gia_tri"] == {"so": 1000000, "tien_te": "VND"}
    assert r["khang_dinh"][1]["gia_tri"] == "2026-10-30"
    for k in r["khang_dinh"]:
        q = k["can_cu"][0]
        assert bo.van_ban[q["bat_dau"]:q["ket_thuc"]] == q["cau"]
        assert q["vi_tri"] == {"trang": None, "hop": None, "dieu": "Điều 1. Nghĩa vụ DEMO"}
        assert q["nguon"] == bo.nguon
    assert r["de_nghi_k5"]["du_lieu_moi"] is (tang > 1)
    assert not r["de_nghi_k5"]["da_duyet"] and not r["de_nghi_k5"]["da_tao_viec"]
    assert bo.so_luot_local == int(ai)
    if tang == 1:
        viec_ids = {bo.viec_id, bo.soan_id} | ({bo.ai_id} if ai else set())
        assert all(tep_id not in (bo.goc["tep"]["tep_id"], bo.vb["tep"]["tep_id"])
                   for viec_id, tep_id, _ in bo.core.luot_doc if viec_id in viec_ids)


@pytest.mark.parametrize("sai", ["quote-bia", "offset", "ngoai-context", "nhan-ky-thuat", "nguon", "doan",
                                    "thuc-the", "ma-gan-giong", "truong", "tien", "tien-te", "don-vi",
                                    "ngay", "thieu-khang-dinh", "them-khang-dinh", "trung-khang-dinh",
                                    "van-xuoi-bia", "so-mot-phan", "ngay-mot-phan", "menh-de-phu", "quote-phu"])
def test_khang_dinh_hong_bi_loai_bo_khong_ha_vang(ai, sai):
    a = ai.pb_local["tra_loi_ai"]
    d, k = a["du_lieu"], a["du_lieu"]["khang_dinh"][0]
    q = k["can_cu"][0]
    if sai == "quote-bia": q["cau"] = "DEMO trích bịa 9.000.000 VND."
    elif sai == "offset": q["bat_dau"] += 1
    elif sai == "ngoai-context": q.update(bat_dau=999999, ket_thuc=1000000)
    elif sai == "nhan-ky-thuat":
        tl = ai.s_ai["ai"]["tai_lieu"]
        q.update(cau=tl[:10], bat_dau=0, ket_thuc=10)
    elif sai == "nguon": q["ma_nguon"] = "DEMO-NGUON-GIA"
    elif sai == "doan": q["ma_doan"] = "DEMO-DOAN-GIA"
    elif sai == "thuc-the": k["thuc_the"] = "DEMO-VAY-B"
    elif sai == "ma-gan-giong": k["thuc_the"] = "DEMO-VAY-AB"
    elif sai == "truong": k["truong"] = "lai_suat"
    elif sai == "tien": k["gia_tri"]["so"] = 100000
    elif sai == "tien-te": k["gia_tri"]["tien_te"] = "USD"
    elif sai == "don-vi": k["don_vi"] = "USD"
    elif sai == "ngay": d["khang_dinh"][1]["gia_tri"] = "2026-10-31"
    elif sai == "thieu-khang-dinh": d["khang_dinh"].pop()
    elif sai == "them-khang-dinh": d["khang_dinh"].append(deepcopy(k))
    elif sai == "trung-khang-dinh": d["khang_dinh"][1] = deepcopy(k)
    elif sai == "van-xuoi-bia": d["tra_loi"] = "Không phải trả nợ DEMO dù có hợp đồng."
    elif sai == "so-mot-phan": d["tra_loi"] = d["tra_loi"].replace("1.000.000", "1")
    elif sai == "ngay-mot-phan": d["tra_loi"] = d["tra_loi"].replace("2026-10-30", "2026")
    elif sai == "menh-de-phu": d["tra_loi"] += " Khoản vay đã được miễn trả."
    else: k["can_cu"].append(deepcopy(q))
    r = khong_can_cu(ai, ai.soan())
    assert "KHANG_DINH_AI_KHONG_DAT" in r["ly_do"]


@pytest.mark.parametrize("sai", ["quote", "offset", "khong-dat", "loi", "trang-thai", "rong", "null"])
def test_trich_dan_tang_ngoai_khong_tin_co_tu_khai(ai, sai):
    a = ai.pb_local["tra_loi_ai"]
    if sai == "quote": a["trich_dan"][0]["cau"] = "DEMO bịa."
    elif sai == "offset": a["trich_dan"][0]["ket_thuc"] -= 1
    elif sai == "khong-dat": a["kiem_trich_dan"]["dat"] = False
    elif sai == "loi": a["kiem_trich_dan"]["loi"] = ["DEMO lỗi trích dẫn"]
    elif sai == "trang-thai": a["trang_thai"] = "khong_thay_can_cu"
    elif sai == "rong": a["trich_dan"] = []
    else: a.update(trang_thai="khong_thay_can_cu", du_lieu=None, trich_dan=[])
    khong_can_cu(ai, ai.soan())


@pytest.mark.parametrize("sai", ["nhan", "duyet", "can-cu-sai-kieu", "gia-tri-tien-float", "tham-so-thua", "phien-ban"])
def test_sai_khuon_tra_loi_la_loi_nghiep_vu(ai, sai):
    a = ai.pb_local["tra_loi_ai"]
    if sai == "nhan": a["du_lieu"]["nhan"] = "xanh"
    elif sai == "duyet": a["du_lieu"]["khang_dinh"][0]["da_duyet"] = True
    elif sai == "can-cu-sai-kieu": a["du_lieu"]["khang_dinh"][0]["can_cu"] = "DEMO"
    elif sai == "gia-tri-tien-float": a["du_lieu"]["khang_dinh"][0]["gia_tri"]["so"] = 1000000.0
    elif sai == "tham-so-thua": a["metadata_tu_khai"] = True
    else: a["phien_ban"] = True
    if sai == "gia-tri-tien-float":
        khong_can_cu(ai, ai.soan())  # JSON Schema coi float nguyên là integer; nghiệp vụ từ chối.
    else:
        loi(ai.soan(), "TC_AI_SAI_KHUON")


@pytest.mark.parametrize("k,v,ma", [("nha_cung_cap", "cloud", "TC_CHI_LOCAL"), ("nha_cung_cap", "khac", "TC_SAI_NGUON"),
    ("ma_prompt", "DEMO-khac", "TC_SAI_NGUON"), ("phien_ban_prompt", "DEMO-2", "TC_SAI_NGUON"),
    ("bam_dau_vao", "sha256:" + "0" * 64, "TC_SAI_NGUON"), ("phien_ban_engine", "DEMO-gia", "TC_SAI_NGUON")])
def test_metadata_cloud_bam_prompt_khong_duoc_doi(ai, k, v, ma):
    ai.pb_local["tra_loi_ai"][k] = v
    loi(ai.soan(), ma)


@pytest.mark.parametrize("k,v", [("tac_vu", "phan_loai"), ("bam_ho_so", "sha256:" + "0" * 64),
    ("bam_cau_hinh", "sha256:" + "0" * 64), ("bam_ngu_canh_ai", "sha256:" + "0" * 64), ("ma_yeu_cau", "DEMO-YC-khac")])
def test_chuyen_tiep_gan_dung_ho_so(ai, k, v):
    ai.pb_local["tra_loi_ai"]["chuyen_tiep"]["tra_cuu"][k] = v
    loi(ai.soan(), "TC_SAI_NGUON")


@pytest.mark.parametrize("sai,ly_do", [("chua-duyet", "CHUA_DUYET"), ("het-hieu-luc", "HET_HIEU_LUC"),
    ("chua-hieu-luc", "HET_HIEU_LUC"), ("moc-tuong-lai", "HET_HIEU_LUC"),
    ("tin-cay-thap", "DUOI_NGUONG_TIN_CAY"), ("thieu-nguong", "THIEU_NGUONG_DA_DO"),
    ("nguong-chua-do", "THIEU_NGUONG_DA_DO"), ("nguong-chua-duyet", "THIEU_NGUONG_DA_DO"),
    ("ngoai-truong", "THIEU_TRUONG_HOAC_THUC_THE")])
def test_tang_mot_chua_du_khong_co_so_doan(sai, ly_do):
    bo = BoTraLoi()
    bang = [bo.can_cu(), bo.can_cu(truong="ngay")]
    if sai == "chua-duyet": bang[0].update(trang_thai_duyet="cho_duyet", moc_duyet=None)
    elif sai == "het-hieu-luc": bang[0].update(con_hieu_luc=False, hieu_luc_den="2026-10-31")
    elif sai == "chua-hieu-luc": bang[0]["hieu_luc_tu"] = "2026-12-01"
    elif sai == "moc-tuong-lai": bang[0]["moc_cong_bo"] = "2026-12-01T00:00:00+07:00"
    elif sai == "tin-cay-thap": bang[0]["do_tin_cay"] = 0.1
    bo.nhan_soan(bang=bang)
    if sai == "thieu-nguong": bo.profile["nguong_tin_cay"] = None
    elif sai == "nguong-chua-do": bo.profile["nguong_tin_cay"]["trang_thai"] = "chua_do"
    elif sai == "nguong-chua-duyet": bo.profile["nguong_tin_cay"]["da_duyet"] = False
    elif sai == "ngoai-truong": bo.profile["truong_can_tra_loi"].append({"ma": "phi", "ten": "Phí", "kieu": "so", "don_vi": "VND"})
    r = khong_can_cu(bo, bo.soan())
    assert ly_do in r["ly_do"] and not r["de_nghi_k5"]["du_lieu_moi"]


@pytest.mark.parametrize("ai,tang", [(False, 1), (True, 1), (True, 2), (True, 3)])
def test_co_van_ban_moi_cho_duyet_luon_canh_bao_toi_da_vang(ai, tang):
    bo = BoTraLoi()
    bo.nhan_soan(tang, sua=lambda d: d.update(co_van_ban_moi_cho_duyet=True))
    if ai:
        bo.chuan_bi_soan()
        bo.local_soan()
    r = ket_qua(bo, bo.soan())
    assert r["nhan"] == "vang" and r["can_duyet"] and r["canh_bao"]
    assert r["phu_thuoc_cache"]["co_van_ban_moi_cho_duyet"]


@pytest.mark.parametrize("tang", [1, 2, 3])
def test_khong_bang_chung_duong_python_khong_ai_khong_so(tang):
    bo = BoTraLoi()
    bo.nhan_soan(tang, bang=[], sua=lambda d: d.update(bang_chung=[]))
    khong_can_cu(bo, bo.soan())
    assert bo.so_luot_local == 0


@pytest.mark.parametrize("tang", [2, 3])
def test_ho_so_co_doan_chua_ai_khong_cho_xin_xanh(tang):
    bo = BoTraLoi()
    bo.nhan_soan(tang)
    loi(bo.soan(), "TC_SAI_GIAI_DOAN")


def test_khong_cho_chen_van_ban_tu_do_vao_ho_so_de_xin_xanh():
    bo = BoTraLoi()
    bo.nhan_soan()
    pb = bo.doi_snapshot_soan(lambda s: s["du_lieu"].update(tra_loi="DEMO bịa 9.000.000 VND", nhan="xanh"))
    assert bo.soan(pb)["trang_thai"] == "LOI"


@pytest.mark.parametrize("sai", ["thuc-the", "truong", "don-vi", "gia-tri", "ngay", "quy-tac"])
def test_bang_chung_core_cung_phai_khop_truong_va_thuc_the(sai):
    bo = BoTraLoi()
    bo.nhan_soan()
    b = bo.profile["bang_chung"][0]
    if sai == "thuc-the": b["thuc_the"].update(ma="DEMO-VAY-B", gia_tri="DEMO-VAY-B")
    elif sai == "truong": b["truong"] = "phi"
    elif sai == "don-vi": b["don_vi"] = "USD"
    elif sai == "gia-tri": b["gia_tri"]["so"] = 100000
    elif sai == "ngay": bo.profile["bang_chung"][1]["gia_tri"] = "2026-10-31"
    else: b["quy_tac"] = "nhan_ty_gia_tu_suy"
    khong_can_cu(bo, bo.soan())


@pytest.mark.parametrize("sai", ["trang-gia", "hop-gia", "dieu-gia", "cau-gia", "offset-sai"])
def test_vi_tri_bang_chung_core_tang_hai_phai_map_ve_nguon_thuc(ai, sai):
    b = ai.profile["bang_chung"][0]
    if sai == "trang-gia": b["vi_tri"]["trang"] = 9
    elif sai == "hop-gia": b["vi_tri"]["hop"] = [0, 0, 1, 1]
    elif sai == "dieu-gia": b["vi_tri"]["dieu"] = "Điều 99. DEMO giả"
    elif sai == "cau-gia":
        b["cau"] = b["cau"].replace("Khoản vay", "Khoản mới")
        b["ket_thuc"] = b["bat_dau"] + len(b["cau"])
    else:
        b["bat_dau"] += 1
        b["ket_thuc"] += 1
        b["vi_tri_gia_tri"] = [x + 1 for x in b["vi_tri_gia_tri"]]
    if sai == "hop-gia":
        loi(ai.soan(), "TC_SAI_NGUON")  # Hộp không có trang là metadata sai khuôn.
    else:
        khong_can_cu(ai, ai.soan())


def test_so_dung_o_nguon_khac_khoan_vay_khong_dat():
    bo = BoTraLoi()
    b = bo.can_cu(cau="Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, ngày 2026-11-01.",
        thuc_the={"loai": "khoan_vay", "ma": "DEMO-VAY-B", "gia_tri": "DEMO-VAY-B"},
        gia_tri={"so": 2000000, "tien_te": "USD"}, hien_thi="2.000.000 USD")
    b["don_vi"] = "USD"
    bo.nhan_soan(2, bang=[b], fields=[TRUONG[0]])
    # Model đòi khoản A nhưng trích câu B có số có thật.
    bo.chuan_bi_soan()
    d = bo.du_lieu_soan()
    d["khang_dinh"][0]["thuc_the"] = "DEMO-VAY-A"
    bo.local_soan(d)
    khong_can_cu(bo, bo.soan())


@pytest.mark.parametrize("sai", ["tien-sang-ty-le", "ty-le-sang-tien", "tu-tinh-tong", "doi-don-vi"])
def test_tien_khong_duoc_thanh_ty_le_hoac_so_tu_suy(ai, sai):
    d = ai.pb_local["tra_loi_ai"]["du_lieu"]
    k = d["khang_dinh"][0]
    if sai == "tien-sang-ty-le": k.update(gia_tri=1000000, don_vi="%")
    elif sai == "ty-le-sang-tien": k.update(truong="lai_suat", gia_tri={"so": 5, "tien_te": "VND"})
    elif sai == "tu-tinh-tong": k["gia_tri"]["so"] = 3000000
    else: k["don_vi"] = "triệu VND"
    khong_can_cu(ai, ai.soan())


@pytest.mark.parametrize("ma_sai", ["007", "7", "00070"])
def test_ma_so_0_dau_phai_khop_ca_cum(ma_sai):
    vb = VAN_BAN.replace("DEMO-VAY-A", "0007")
    bo = BoTraLoi(van_ban=vb)
    e = {"loai": "khoan_vay", "ma": "0007", "gia_tri": "0007"}
    cau = "Khoản vay 0007 có giá trị 1.000.000 VND, ngày 2026-10-30."
    b = bo.can_cu(thuc_the=e, cau=cau)
    bo.nhan_soan(2, bang=[b], fields=[TRUONG[0]], sua=lambda d: d.update(
        thuc_the=[e], cau_hoi="Giá trị khoản vay 0007 là bao nhiêu VND?"))
    bo.chuan_bi_soan()
    d = bo.du_lieu_soan()
    bo.local_soan(d)
    assert ket_qua(bo, bo.soan())["khang_dinh"][0]["thuc_the"]["ma"] == "0007"
    bo.pb_local["tra_loi_ai"]["du_lieu"]["khang_dinh"][0]["thuc_the"] = ma_sai
    khong_can_cu(bo, bo.soan())


def test_snapshot_cau_hinh_da_ghim_khong_doc_lai_ngan_giua_chuoi():
    bo = BoTraLoi()
    bo.nhan_soan()
    cu = deepcopy(bo.s_nhan["cau_hinh"])
    bo.dat_cau_hinh({"cat_doan": {"do_dai_muc_tieu": 250}})
    ra = bo.soan()
    ket_qua(bo, ra)
    assert bo.snapshot(ra)["cau_hinh"] == cu


@pytest.mark.parametrize("thoi_diem", [False, True])
def test_phu_thuoc_cache_giu_pham_vi_thuc_the_moc_cong_bo_va_duyet(ai, thoi_diem):
    ai.profile["phu_thuoc_thoi_diem"] = thoi_diem
    r = ket_qua(ai, ai.soan())
    p = r["phu_thuoc_cache"]
    assert p["nguon"] == ai.s_nhan["nguon"]
    assert p["ngu_canh_core"] == ai.ngu_canh
    assert p["phu_thuoc_thoi_diem"] is thoi_diem
    assert p["duoc_tai_dung_cache"] is (False if thoi_diem else None)
    assert all(x["moc_duyet"] and x["moc_cong_bo"] and x["nguon"]["phien_ban_nguon"] == "1" for x in p["moc_nguon"])


@pytest.mark.parametrize("sai", ["cap", "profile", "trang-thai-nguon", "nguon", "bam-du-lieu", "phap-nhan"])
def test_thieu_quyen_hoac_nguon_loi_khong_thanh_khong_du_lieu(ai, sai):
    ai.giao_soan(phap_nhan="DEMO-Q" if sai == "phap-nhan" else "DEMO-P")
    c = ai.core.cua.giay_cap[ai.soan_id]
    if sai == "cap": ai.core.cua.giay_cap.pop(ai.soan_id)
    elif sai == "profile": c.pop("kiem_chung_tra_loi")
    elif sai == "trang-thai-nguon": c["kiem_chung_tra_loi"]["trang_thai_nguon"] = "loi"
    elif sai == "nguon": c["nguon"] = {}
    elif sai == "bam-du-lieu": c["kiem_chung_tra_loi"]["bam_du_lieu"] = "sha256:" + "0" * 64
    ai.core.chay(ai.app)
    ra = ai.core.xem(ai.soan_id)
    assert ra["trang_thai"] == "LOI" and ra["ket_qua"] is None


def test_nguon_da_nhan_chua_tra_giu_chua_ro(ai, monkeypatch):
    def chua_ro(viec_id):
        raise ChuaRo("DEMO-tuong-quan")
    monkeypatch.setattr(ai.core.cua, "doc_quyen", chua_ro)
    ra = ai.soan()
    assert ra["trang_thai"] == "CHUA_RO" and ra["ket_qua"] is None


@pytest.mark.parametrize("luc", ["truoc-doc", "sau-doc", "sau-upload"])
def test_huy_khong_nop_cau_tra_loi(ai, luc, monkeypatch):
    ai.giao_soan()
    if luc == "truoc-doc": ai.core.huy(ai.soan_id)
    elif luc == "sau-doc": ai.core.sau_doc = lambda viec_id, tep_id: ai.core.huy(viec_id)
    else:
        tai = Viec.tai_tep_ra
        def tai_roi_huy(viec, *args, **kwargs):
            ra = tai(viec, *args, **kwargs)
            ai.core.huy(viec.id)
            return ra
        monkeypatch.setattr(Viec, "tai_tep_ra", tai_roi_huy)
    ai.core.chay(ai.app)
    ra = ai.core.xem(ai.soan_id)
    assert ra["trang_thai"] == "HUY" and ra["ket_qua"] is None


def test_runtime_khong_ghi_tep_va_khong_model_that_cloud(ai, monkeypatch):
    dem = {"mang": 0, "ghi": 0}
    def cam_mang(*args, **kwargs):
        dem["mang"] += 1
        raise AssertionError("Không gọi provider thật.")
    mo = builtins.open
    def cam_ghi(tep, mode="r", *args, **kwargs):
        if any(k in mode for k in "wax+"):
            dem["ghi"] += 1
            raise AssertionError("Không ghi đĩa.")
        return mo(tep, mode, *args, **kwargs)
    monkeypatch.setattr(socket.socket, "connect", cam_mang)
    monkeypatch.setattr(socket, "create_connection", cam_mang)
    monkeypatch.setattr(socket, "getaddrinfo", cam_mang)
    monkeypatch.setattr(builtins, "open", cam_ghi)
    assert ket_qua(ai, ai.soan())["co_can_cu"]
    assert dem == {"mang": 0, "ghi": 0} and ai.so_luot_local == 1


def test_harness_tc_7():
    assert all(x["trang_thai"] == "XONG" for x in chay_demo_tra_loi())


def bo_mau_thuan(tang):
    bo = BoTraLoi()
    chu2 = VAN_BAN.replace("1.000.000 VND", "2.000.000 VND")
    goc2 = bo.tai("nguon-thu-hai-DEMO.txt", chu2.encode("utf-8"), "text/plain")
    vb2 = deepcopy(bo.pb_vb)
    vb2["van_ban_tai_lieu"].update(van_ban=chu2, bam_dau_vao=goc2["bam"])
    ref2 = bo.tai("van-ban-thu-hai-DEMO.json", json_chuan(vb2))
    n2 = {"ma_nguon": "DEMO-NGUON-2", "phien_ban_nguon": "2", "tep_id": goc2["tep"]["tep_id"],
          "bam_goc": goc2["bam"], "bam_van_ban": bam(chu2.encode("utf-8"))}
    tl2 = {"ma_nguon": n2["ma_nguon"], "phien_ban_nguon": "2", "goc": goc2, "van_ban": ref2}
    bo.nguon_duoc_cap[n2["ma_nguon"]] = n2
    b1 = bo.can_cu()
    cu = bo.van_ban
    bo.van_ban = chu2
    b2 = bo.can_cu(cau="Khoản vay DEMO-VAY-A có giá trị 2.000.000 VND, ngày 2026-10-30.",
                  gia_tri={"so": 2000000, "tien_te": "VND"}, hien_thi="2.000.000 VND", nguon=n2)
    bo.van_ban = cu
    def them(d):
        if tang != 1:
            d["nguon"].append(tl2)
            d["bang_chung"].append({**{k: n2[k] for k in ("ma_nguon", "phien_ban_nguon", "bam_goc", "bam_van_ban")},
                "nguyen_van": chu2, "bat_dau": 0, "ket_thuc": len(chu2), "vi_tri": {"trang": None, "hop": None}})
    bo.nhan_soan(tang, bang=[b1, b2], fields=[TRUONG[0]], sua=them)
    return bo


@pytest.mark.parametrize("tang,ai", [(1, False), (1, True), (2, True), (3, True)])
def test_hai_nguon_mau_thuan_tra_ca_hai_khong_tu_chon(tang, ai):
    bo = bo_mau_thuan(tang)
    if ai:
        bo.chuan_bi_soan()
        d = bo.du_lieu_soan()
        d["co_mau_thuan"] = True
        d["tra_loi"] = "Có mâu thuẫn trong bằng chứng; Anh cần duyệt các giá trị sau.\n" + d["tra_loi"]
        bo.local_soan(d)
    r = ket_qua(bo, bo.soan())
    assert r["co_can_cu"] and r["co_mau_thuan"] and r["can_duyet"] and r["nhan"] == "vang"
    assert [k["gia_tri"]["so"] for k in r["khang_dinh"]] == [1000000, 2000000]
    assert {k["can_cu"][0]["nguon"]["ma_nguon"] for k in r["khang_dinh"]} == {"DEMO-NGUON-1", "DEMO-NGUON-2"}
    assert len(r["phu_thuoc_cache"]["moc_nguon"]) == 2 and len(r["mau_thuan"]) == 2
    assert r["de_nghi_k5"]["co_mau_thuan"] and not r["de_nghi_k5"]["da_tao_viec"]


def test_ai_khong_duoc_giau_mau_thuan_core_da_cap():
    bo = bo_mau_thuan(2)
    bo.chuan_bi_soan()
    d = bo.du_lieu_soan()
    d["khang_dinh"] = d["khang_dinh"][:1]
    d["tra_loi"] = "Giá trị (DEMO-VAY-A): 1.000.000 VND."
    bo.local_soan(d)
    r = khong_can_cu(bo, bo.soan())
    assert r["co_mau_thuan"] and r["can_duyet"] and len(r["mau_thuan"]) == 2


def test_ban_het_hieu_luc_khong_duoc_coi_la_mau_thuan_hien_hanh():
    bo = bo_mau_thuan(2)
    bo.profile["bang_chung"][1].update(con_hieu_luc=False, hieu_luc_den="2026-10-31")
    bo.chuan_bi_soan()
    bo.local_soan()
    r = khong_can_cu(bo, bo.soan())
    assert "HET_HIEU_LUC" in r["ly_do"] and not r["co_mau_thuan"] and r["mau_thuan"] == []


@pytest.mark.parametrize("sai", [False, True])
def test_trang_thuc_map_chinh_xac_khong_chi_kiem_trang_nam_trong_tai_lieu(sai):
    bo = BoTraLoi()
    chu = VAN_BAN.split("\n", 2)
    pages = ["\n".join(chu[:2]), chu[2]]
    bo.nguon_co_cau_truc(phong_bi_trang(bo, pages))
    bang = [bo.can_cu(), bo.can_cu(truong="ngay")]
    for b in bang:
        b["vi_tri"].update(trang=2, hop=[10, 20, 500, 100])
    bo.nhan_soan(2, bang=bang)
    bo.chuan_bi_soan()
    bo.local_soan()
    if sai:
        bo.profile["bang_chung"][0]["vi_tri"]["trang"] = 1  # trang có thật nhưng sai đoạn.
        khong_can_cu(bo, bo.soan())
    else:
        r = ket_qua(bo, bo.soan())
        assert r["co_can_cu"] and all(k["can_cu"][0]["vi_tri"]["trang"] == 2 for k in r["khang_dinh"])


@pytest.mark.parametrize("so,hien", [(9007199254740993, "9.007.199.254.740.993 VND"),
                                    ("1000000.10", "1.000.000,10 VND")])
def test_tien_lon_va_thap_phan_khong_mat_chinh_xac(so, hien):
    chu = VAN_BAN.replace("1.000.000 VND", hien)
    bo = BoTraLoi(van_ban=chu)
    cau = chu.splitlines()[2]
    b = bo.can_cu(cau=cau, gia_tri={"so": so, "tien_te": "VND"}, hien_thi=hien)
    bo.nhan_soan(bang=[b], fields=[TRUONG[0]])
    r = ket_qua(bo, bo.soan())
    assert r["co_can_cu"] and r["nhan"] == "xanh"
    assert r["khang_dinh"][0]["gia_tri"] == {"so": so, "tien_te": "VND"}
    assert hien in r["tra_loi"]


def test_chuyen_dinh_dang_ngay_chi_khi_khai_quy_tac_ro_rang():
    bo = BoTraLoi(van_ban=VAN_BAN.replace("2026-10-30", "30/10/2026"))
    b = bo.can_cu(truong="ngay", cau=bo.van_ban.splitlines()[2], hien_thi="30/10/2026")
    b["quy_tac"] = "ngay_viet"
    bo.nhan_soan(bang=[b], fields=[TRUONG[1]])
    r = ket_qua(bo, bo.soan())
    assert r["co_can_cu"] and r["khang_dinh"][0]["gia_tri"] == "2026-10-30"
    assert r["tra_loi"] == "Ngày (DEMO-VAY-A): 30/10/2026."
    bo.profile["bang_chung"][0]["quy_tac"] = "ngay_iso"
    khong_can_cu(bo, bo.soan())


@pytest.mark.parametrize("sai", ["chua_ro", "mat_lease", "sai_ack"])
def test_upload_chua_ro_lease_ack_khong_xong_gia(ai, sai, monkeypatch):
    goc = Viec.tai_tep_ra
    def tai(viec, *args):
        tep = goc(viec, *args)
        if sai == "chua_ro": raise ChuaRo("DEMO-upload-TC7")
        if sai == "mat_lease": raise LoiDuongTruyen("MAT_LEASE", http_status=409)
        return {**tep, "kich_thuoc": tep["kich_thuoc"] + 1}
    monkeypatch.setattr(Viec, "tai_tep_ra", tai)
    ra = ai.soan()
    assert ra["trang_thai"] != "XONG" and ra["ket_qua"] is None
    if sai == "chua_ro": assert ra["trang_thai"] == "CHUA_RO"
    elif sai == "sai_ack": loi(ra, "TC_SAI_NGUON")


@pytest.mark.parametrize("k", ["prompt", "khuon_tra_loi", "map_nguon", "tai_lieu", "ngan_sach", "doan"])
def test_snapshot_ai_tu_sua_kem_bam_moi_van_bi_tu_choi(ai, k):
    def sua(s):
        if k in ("prompt", "tai_lieu"): s["ai"][k] += " DEMO thay đổi"
        elif k == "khuon_tra_loi": s["ai"][k]["properties"]["nhan"] = {"const": "xanh"}
        elif k == "map_nguon": s["ai"][k][0]["ai_bat_dau"] += 1
        elif k == "ngan_sach": s["ai"][k]["so_ky_tu"] += 1
        else: s["ai"][k][0]["bat_dau"] += 1
    pb = ai.doi_snapshot_soan(sua)
    loi(ai.soan(pb), "TC_SAI_NGUON")


def test_profile_gan_sai_khoan_vay_du_so_dung_van_bi_tu_choi():
    bo = BoTraLoi()
    b = bo.can_cu(cau="Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, ngày 2026-11-01.",
                  gia_tri={"so": 2000000, "tien_te": "USD"}, hien_thi="2.000.000 USD")
    b["don_vi"] = "USD"  # Profile cố gắn câu B cho A, số/tiền tệ đều có thật.
    bo.nhan_soan(bang=[b], fields=[{**TRUONG[0], "don_vi": "USD"}])
    khong_can_cu(bo, bo.soan())


@pytest.mark.parametrize("tang", [1, 2])
def test_khong_nhan_so_nam_trong_mot_phan_cum_tien_o_nguon(tang):
    chu = VAN_BAN.replace("1.000.000 VND", "5.000.000 VND")
    bo = BoTraLoi(van_ban=chu)
    b = bo.can_cu(cau=chu.splitlines()[2], hien_thi="5")
    b.update(kieu="so", gia_tri=5, don_vi=None, quy_tac="so_chuan")
    bo.nhan_soan(tang, bang=[b], fields=[{"ma": "gia_tri", "ten": "Giá trị", "kieu": "so", "don_vi": None}])
    if tang == 2:
        bo.chuan_bi_soan()
        bo.local_soan()
    khong_can_cu(bo, bo.soan())


def test_tang_hai_chua_duyet_chi_de_nghi_k5_khong_thanh_tang_mot():
    bo = BoTraLoi()
    bang = [bo.can_cu(), bo.can_cu(truong="ngay")]
    for b in bang:
        b.update(trang_thai_duyet="cho_duyet", moc_duyet=None, do_tin_cay=0.1)
    bo.nhan_soan(2, bang=bang)
    bo.profile["nguong_tin_cay"] = None
    bo.chuan_bi_soan()
    bo.local_soan()
    r = ket_qua(bo, bo.soan())
    assert r["co_can_cu"] and r["nhan"] == "vang" and r["can_duyet"]
    assert r["de_nghi_k5"]["du_lieu_moi"] and not r["de_nghi_k5"]["da_duyet"]


@pytest.mark.parametrize("prefix", ["😀 DEMO\n", "DEMO A\u0301nh Du\u031bo\u031bng\n"])
def test_offset_unicode_code_point_khong_tinh_byte_hoac_utf16(prefix):
    bo = BoTraLoi(van_ban=prefix + VAN_BAN)
    bo.nhan_soan(2)
    bo.chuan_bi_soan()
    bo.local_soan()
    r = ket_qua(bo, bo.soan())
    assert r["co_can_cu"]
    for k in r["khang_dinh"]:
        q = k["can_cu"][0]
        assert bo.van_ban[q["bat_dau"]:q["ket_thuc"]] == q["cau"]


@pytest.mark.parametrize("thao_tac", ["tep", "ket_qua", "ket_thuc"])
def test_mat_xac_nhan_sdk_gui_lai_khong_ghi_hai_lan(ai, thao_tac):
    truoc = dict(ai.core.so_lan_ghi)
    ai.core.gay_mat_xac_nhan(thao_tac, 1)
    r = ket_qua(ai, ai.soan())
    assert r["co_can_cu"]
    for k in ("tep", "ket_qua", "ket_thuc"):
        assert ai.core.so_lan_ghi[k] == truoc[k] + 1


@pytest.mark.parametrize("diem", ["_tien_do", "_tai_tep_ra", "_nop_ket_qua"])
def test_mat_lease_khong_nop_ket_thuc_gia(ai, diem, monkeypatch):
    ai.giao_soan()
    truoc = dict(ai.core.so_lan_ghi)
    def mat_lease(ma, viec_id, *args, **kwargs):
        ai.core._viec[viec_id]["trang_thai"] = "CHO"
        raise LoiDuongTruyen("MAT_LEASE", http_status=409)
    monkeypatch.setattr(ai.core, diem, mat_lease)
    ai.core.chay(ai.app)
    ra = ai.core.xem(ai.soan_id)
    assert ra["trang_thai"] == "CHO" and ra["ket_qua"] is None
    for k in ("ket_qua", "ket_thuc"):
        assert ai.core.so_lan_ghi[k] == truoc[k]


def test_ngoai_le_adapter_khong_lo_noi_dung_nguon_trong_loi_log(ai, monkeypatch, capsys):
    def hong(*args):
        raise RuntimeError("DEMO-noi-dung-rieng-khong-duoc-lo")
    monkeypatch.setattr(ai.core.cua, "doc_quyen", hong)
    ra = ai.soan()
    loi(ra, "ENGINE_LOI_XU_LY")
    assert "DEMO-noi-dung-rieng-khong-duoc-lo" not in repr(ra) + capsys.readouterr().err


def test_qua_tran_tu_choi_khong_cat_ai_tra_loi(ai):
    ai.pb_local["tra_loi_ai"]["tra_loi"] = "D" * 500001
    ra = ai.soan()
    assert ra["trang_thai"] == "LOI" and ra["ket_qua"] is None
    assert ra["loi"]["ma"] in ("VUOT_GIOI_HAN", "TC_QUA_GIOI_HAN")


def test_tap_thuc_the_dung_nguon_nhung_sai_cau_hoi_khong_duoc_tra_loi():
    bo = BoTraLoi()
    bo.nhan_soan(sua=lambda d: d.update(cau_hoi="Giá trị khoản vay DEMO-VAY-B là bao nhiêu?"))
    r = khong_can_cu(bo, bo.soan())
    assert "THUC_THE_KHONG_KHOP_CAU_HOI" in r["ly_do"]


def test_consumer_hoi_ai_hien_co_voi_local_gia_khong_duoc_lam_xanh():
    bo = BoTraLoi()
    bo.nhan_soan(2)
    bo.chuan_bi_soan()
    ra, local = dieu_phoi_hoi_ai(bo, bo.pb_ai, bo.du_lieu_soan())
    assert ra["trang_thai"] == "XONG" and local.so_luot == 1, ra
    a = ra["ket_qua"]["tra_loi_ai"]
    assert a["trang_thai"] == "co_can_cu" and a["kiem_trich_dan"]["dat"]
    # LocalGia trả thêm quote toàn ngữ cảnh, chứa vùng ngoài map nguồn. Hỏi AI
    # chấp nhận vai trò/schema nhưng TC vẫn từ chối chứng cứ rộng không hợp lệ.
    r = khong_can_cu(bo, bo.soan(ra["ket_qua"]))
    assert "KHANG_DINH_AI_KHONG_DAT" in r["ly_do"]
