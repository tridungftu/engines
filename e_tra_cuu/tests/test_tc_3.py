"""TC-3 thực thi bằng SDK/CoreGia, ngăn RAM và cửa quyền giả chỉ ở tests."""

from copy import deepcopy
import io
import unicodedata

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, Viec

from e_tra_cuu import chay
from e_tra_cuu.cat_doan import BAN_THUAT_TOAN
from e_tra_cuu.kiem_dau_vao import bam, json_chuan
from ho_tro_tc_3 import BoCatDoan, bang_demo, kiem_phu_nguon, phong_bi_trang
from mo_hinh_contract_tc_1 import kiem_schema_moi
from test_tc_2 import SCHEMA, loi


def test_docx_khong_trang_tien_ngay_va_nguyen_van():
    vb = "Công ty DEMO Ánh Dương\nĐiều 1. Giá trị\n1. Giá trị 1.000.000 VND, ngày 2026-10-30.\nĐiều 2. Đủ chữ cuối DEMO.\n  "
    bo = BoCatDoan(van_ban=vb, noi_dung_goc=b"DEMO-bytes-container")
    bo.nhan()
    kq = bo.cat()
    s, ds = kiem_phu_nguon(bo, kq)
    kiem_schema_moi(kq["ket_qua"], SCHEMA, SCHEMA)
    v = s["du_lieu"]["tai_lieu"]["van_ban_tai_lieu"]["van_ban_tai_lieu"]
    assert v["so_trang"] == 0 and v["trang"] == []
    assert all(d["so_trang"] is d["hop"] is None for d in ds)
    assert all(d["vi_tri"] == {"trang": None, "hop": None} for d in ds)
    assert s["nguon"][0]["bam_goc"] != s["nguon"][0]["bam_van_ban"]
    assert "1.000.000 VND" in "".join(d["nguyen_van"] for d in ds)
    assert "2026-10-30" in "".join(d["nguyen_van"] for d in ds)
    assert s["ket_qua"]["ban_thuat_toan"] == BAN_THUAT_TOAN
    assert all(d["metadata_core"]["trang_thai_duyet"] == "cho_duyet" for d in ds)


def test_dieu_khoan_xuyen_trang_va_trang_rong():
    cac_trang = ["Điều 1. Điều kiện DEMO\nKhoản 1. Bắt đầu nội dung DEMO",
                 " tiếp nối đúng Khoản 1, giữ dấu tiếng Việt và 1.000.000 VND.",
                 "", "Khoản 2. Ngày 2026-10-30.\nĐiều 2. Kết thúc DEMO\n"]
    bo = BoCatDoan(van_ban="\f".join(cac_trang))
    bo.nguon_co_cau_truc(phong_bi_trang(bo, cac_trang))
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat(muc_tieu=300))
    doan = next(d for d in ds if "Bắt đầu" in d["nguyen_van"])
    assert doan["dieu"] == "Điều 1"
    assert doan["vi_tri"] == {"trang": None, "hop": None}
    assert {r["so_trang"] for r in doan["vung_vi_tri"]} >= {1, 2}
    assert all(r["hop"] is None or r["hop"] == [10, 20, 500, 100] for r in doan["vung_vi_tri"])
    assert any(n["khoan"] == "Khoản 1" for n in doan["nhan_cau_truc"])


def test_tieu_de_trung_khong_find_nham_vi_tri():
    vb = "Tiêu đề DEMO\nNội dung một.\nTiêu đề DEMO\nNội dung hai."
    bo = BoCatDoan(van_ban=vb)
    cac_khoi = [[{"loai": "doan", "van_ban": c, "hop": [10, i * 100, 500, i * 100 + 50]}
                 for i, c in enumerate(["Tiêu đề DEMO", "Nội dung một.", "Tiêu đề DEMO", "Nội dung hai."], 1)]]
    bo.nguon_co_cau_truc(phong_bi_trang(bo, [vb], cac_khoi))
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat())
    vt = [v for d in ds for v in d["vung_vi_tri"] if v["hop"] in ([10, 100, 500, 150], [10, 300, 500, 350])]
    assert len(vt) == 2 and vt[0]["bat_dau"] != vt[1]["bat_dau"]
    assert ds[0]["hop"] is None  # Không tạo hộp bao từ nhiều khối.


@pytest.mark.parametrize("dang", ["NFC", "NFD"])
@pytest.mark.parametrize("muc_tieu", [200, 501, 2000, 8000])
def test_unicode_python_khong_bat_dau_theo_byte_utf16(dang, muc_tieu):
    chu = unicodedata.normalize(dang, "Điều 1. Công ty DEMO Ánh Dương 😀\nKhoản 1. ")
    vb = chu + ("Nội dung tiếng Việt vẫn nguyên văn, giá 1.000.000 VND. " * 50) + "\nĐủ đuôi 2026-10-30."
    bo = BoCatDoan(van_ban=vb)
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat(muc_tieu=muc_tieu))
    assert any(d["dieu"] and "Đi" in d["dieu"] for d in ds)
    assert len(ds) > 1 if muc_tieu < 2000 else len(ds) >= 1
    assert all(len(d["nguyen_van"]) <= 8000 for d in ds)


def test_khong_cat_tung_n_ky_tu_va_don_vi_dai_hon_muc_tieu():
    cau = "Công ty DEMO Ánh Dương " + "x" * 300 + ". "
    bo = BoCatDoan(van_ban=cau * 5 + "Kết thúc DEMO.")
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat(muc_tieu=200))
    assert len(ds[0]["nguyen_van"]) == len(cau) > 200
    assert all(d["nguyen_van"].endswith((". ", ".")) for d in ds)


@pytest.mark.parametrize("docx", [False, True], ids=["co-trang", "docx-khong-trang"])
def test_bang_gop_trong_tieu_de_lap_map_tung_o(docx):
    bo = BoCatDoan()
    bo.nguon_co_cau_truc(bang_demo(bo, docx=docx))
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat())
    bang = [d for d in ds if d["bang"]]
    assert len(bang) >= 2
    assert len({d["bang"]["ma_bang"] for d in bang}) == 1
    assert bang[0]["bat_dau"] is not None
    assert all(d["bat_dau"] is d["ket_thuc"] is None for d in bang[1:])
    assert all(d["map_nguon"][0]["vai_tro"] == "ngu_canh_lap" for d in bang[1:])
    cac_o = [o for d in bang for o in d["bang"]["o"] if o["vai_tro"] == "noi_dung"]
    assert any(o["van_ban"] == "" for o in cac_o)
    assert any(o["gop_cot"] == 2 for o in cac_o)
    assert any(o["gop_hang"] == 2 for o in cac_o)
    assert len({(o["hang"], o["cot"]) for o in cac_o}) == len(cac_o)
    assert all(d["bang"]["hang_tieu_de"] == [0] for d in bang)
    if docx:
        assert all(d["so_trang"] is d["hop"] is None for d in ds)
    else:
        assert all(d["so_trang"] == 1 and d["hop"] == [10, 100, 500, 700] for d in bang)
        assert all(o["hop"] is None for o in cac_o)  # Không mượn hộp bảng làm hộp ô.


def test_bang_khong_co_tieu_de_khong_tu_lay_hang_dau_lam_tieu_de():
    bo = BoCatDoan()
    pb = bang_demo(bo)
    pb["van_ban_tai_lieu"]["trang"][0]["khoi"][1].pop("hang_tieu_de")
    bo.nguon_co_cau_truc(pb)
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat())
    assert all(m["vai_tro"] == "noi_dung" for d in ds for m in d["map_nguon"])


@pytest.mark.parametrize("eol", ["\n", "\r\n"], ids=["LF", "CRLF"])
@pytest.mark.parametrize("kieu", ["khong-map", "chi-map-bang", "chi-map-o", "thieu-mot-map"])
def test_bang_chieu_tab_newline_suy_map_chinh_xac_khong_sua_phong_bi(eol, kieu):
    bo = BoCatDoan()
    pb = bang_demo(bo)
    v = pb["van_ban_tai_lieu"]
    vb_cu = v["van_ban"]
    if eol != "\n":
        v["van_ban"] = vb_cu.replace("\n", eol)
        for k in v["trang"][0]["khoi"]:
            if "van_ban" in k:
                k["van_ban"] = k["van_ban"].replace("\n", eol)
            for muc in [k, *k.get("o", [])]:
                for ten in ("bat_dau", "ket_thuc"):
                    if ten in muc:
                        muc[ten] = len(vb_cu[:muc[ten]].replace("\n", eol))
    b = v["trang"][0]["khoi"][1]
    if kieu in {"khong-map", "chi-map-o"}:
        b.pop("bat_dau"); b.pop("ket_thuc")
    if kieu in {"khong-map", "chi-map-bang"}:
        for o in b["o"]:
            o.pop("bat_dau"); o.pop("ket_thuc")
    if kieu == "thieu-mot-map":
        b["o"][2].pop("bat_dau"); b["o"][2].pop("ket_thuc")
    truoc = deepcopy(pb)
    bo.nguon_co_cau_truc(pb); bo.nhan()
    s, ds = kiem_phu_nguon(bo, bo.cat())
    assert s["du_lieu"]["tai_lieu"]["van_ban_tai_lieu"] == truoc
    assert len([d for d in ds if d["bang"]]) >= 2


def test_bang_docx_khong_offset_co_chuoi_khoi_chieu_duoc():
    bo = BoCatDoan()
    pb = bang_demo(bo, docx=True)
    b = pb["van_ban_tai_lieu"]["khoi"][1]
    b["van_ban"] = pb["van_ban_tai_lieu"]["van_ban"][b["bat_dau"]:b["ket_thuc"]]
    b.pop("bat_dau"); b.pop("ket_thuc")
    for o in b["o"]:
        o.pop("bat_dau"); o.pop("ket_thuc")
    bo.nguon_co_cau_truc(pb); bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat())
    assert all(d["so_trang"] is d["hop"] is None for d in ds)


@pytest.mark.parametrize("sai", ["config-sai", "version-bool", "stage-snapshot", "phien-ban-engine", "thua-envelope", "thua-metadata", "danh-muc-thua", "cap-khac-envelope"])
def test_tu_choi_snapshot_va_phong_bi_sai_mien(sai):
    bo = BoCatDoan(); bo.nhan()
    pb = deepcopy(bo.pb_nhan)
    ma_loi = "TC_SAI_NGUON"
    if sai == "config-sai":
        pb = bo.doi_snapshot(lambda s: s["cau_hinh"]["gia_tri"].update(phien_ban=2))
    elif sai == "version-bool":
        pb = bo.doi_snapshot(lambda s: s["cau_hinh"].update(row_version=True))
    elif sai == "stage-snapshot":
        pb = bo.doi_snapshot(lambda s: s.update(giai_doan="da_cat_doan"))
    elif sai == "phien-ban-engine":
        pb["ho_so_tra_cuu"]["phien_ban_engine"] = "e_tra_cuu 9.9.9"
    elif sai == "thua-envelope":
        pb["ho_so_tra_cuu"]["confidence"] = 1
        ma_loi = "TC_DAU_VAO_KHONG_HOP_LE"
    elif sai == "thua-metadata":
        pb = bo.doi_snapshot(lambda s: s["du_lieu"]["metadata_core"].update(confidence=1))
        ma_loi = "TC_DAU_VAO_KHONG_HOP_LE"
    elif sai == "danh-muc-thua":
        pb = bo.doi_snapshot(lambda s: s["du_lieu"].update(danh_muc={**bo.danh_muc, "duyet": True}))
        ma_loi = "TC_DAU_VAO_KHONG_HOP_LE"
    bo.giao_cat(pb)
    if sai == "cap-khac-envelope":
        bo.core.cua.giay_cap[bo.cat_id]["dau_vao"]["ho_so_tra_cuu"]["ma_yeu_cau"] = "DEMO-KHAC"
    bo.core.chay(bo.app)
    loi(bo.core.xem(bo.cat_id), ma_loi)
    assert bo.core.so_lan_ghi["tep"] == 1


@pytest.mark.parametrize("sai", ["thieu-map-bang", "thieu-map-o", "map-utf16", "text-o", "thieu-o-trong", "o-chong", "nhay-chu",
                                 "tieu-de-khong-dau", "tieu-de-cat-o-gop", "hop-ngoai-trang", "hop-o-ngoai-bang", "map-don"])
def test_bang_nguon_khong_nhat_quan_bi_tu_choi(sai):
    bo = BoCatDoan()
    pb = bang_demo(bo)
    b = pb["van_ban_tai_lieu"]["trang"][0]["khoi"][1]
    if sai == "thieu-map-bang":
        b.pop("bat_dau"); b.pop("ket_thuc")
        # Phép chiếu có delimiter riêng, không có vùng nguồn kiểm được.
        v = pb["van_ban_tai_lieu"]
        v["van_ban"] = v["van_ban"].replace("\t", "|")
    elif sai == "thieu-map-o":
        b["o"][2].pop("bat_dau"); b["o"][2].pop("ket_thuc")
        v = pb["van_ban_tai_lieu"]
        v["van_ban"] = v["van_ban"].replace("\t", "|")
    elif sai == "map-utf16":
        b["o"][0]["bat_dau"] += 1
        b["o"][0]["ket_thuc"] += 1
    elif sai == "text-o":
        b["o"][0]["van_ban"] = "DEMO sai chữ"
    elif sai == "thieu-o-trong":
        b["o"] = [o for o in b["o"] if o["van_ban"]]
    elif sai == "o-chong":
        b["o"][1]["gop_cot"] = 2
    elif sai == "nhay-chu":
        b["o"][0].update(bat_dau=b["o"][0]["bat_dau"] + 1,
                          van_ban=b["o"][0]["van_ban"][1:])
    elif sai == "tieu-de-khong-dau":
        b["hang_tieu_de"] = [1]
    elif sai == "tieu-de-cat-o-gop":
        b["hang_tieu_de"] = [0, 1]
    elif sai == "hop-ngoai-trang":
        b["hop"][2] = 600
    elif sai == "hop-o-ngoai-bang":
        b["o"][0]["hop"] = [0, 0, 20, 20]
    else:
        b["o"][0].pop("ket_thuc")
    bo.nguon_co_cau_truc(pb)
    bo.nhan()
    loi(bo.cat(), "TC_SAI_NGUON")
    assert bo.core.so_lan_ghi["tep"] == 1


@pytest.mark.parametrize("sai", ["text-khoi", "text-dong", "text-tu", "so-trang", "hop-docx", "map-bo-chu", "map-thua", "map-bool"])
def test_khoi_chu_khong_co_map_kiem_duoc_khong_bia_vi_tri(sai):
    bo = BoCatDoan(van_ban="Công ty DEMO Ánh Dương.")
    pb = phong_bi_trang(bo, [bo.van_ban])
    k = pb["van_ban_tai_lieu"]["trang"][0]["khoi"][0]
    if sai == "text-khoi":
        k["van_ban"] = "DEMO sai"
    elif sai in {"text-dong", "text-tu"}:
        k["dong"] = [{"van_ban": "DEMO sai" if sai == "text-dong" else bo.van_ban,
                      "hop": k["hop"], "tu": [{"van_ban": "DEMO sai", "hop": k["hop"]}]}]
    elif sai == "so-trang":
        pb["van_ban_tai_lieu"]["van_ban"] += "\f"
    elif sai == "hop-docx":
        pb = deepcopy(bo.pb_vb)
        pb["van_ban_tai_lieu"]["khoi"] = [k]
    elif sai == "map-bo-chu":
        k["van_ban"] = bo.van_ban[4:]
    elif sai == "map-thua":
        k["bat_dau"], k["ket_thuc"] = 0, len(bo.van_ban) + 1
    else:
        k["bat_dau"], k["ket_thuc"] = False, len(bo.van_ban)
    bo.nguon_co_cau_truc(pb)
    bo.nhan()
    loi(bo.cat(), "TC_SAI_NGUON")


def test_ma_doan_on_dinh_qua_viec_khac_va_doi_khi_doi_nguon_phien_ban(monkeypatch):
    bo = BoCatDoan()
    bo.nhan()
    _, mot = kiem_phu_nguon(bo, bo.cat())
    _, hai = kiem_phu_nguon(bo, bo.cat())
    assert [d["ma_doan"] for d in mot] == [d["ma_doan"] for d in hai]
    import e_tra_cuu.cat_doan as modul
    monkeypatch.setattr(modul, "BAN_THUAT_TOAN", "DEMO-thuat-toan-2")
    _, ba = kiem_phu_nguon(bo, bo.cat())
    assert [d["ma_doan"] for d in mot] != [d["ma_doan"] for d in ba]
    bo2 = BoCatDoan(van_ban=bo.van_ban)
    bo2.tai_lieu["phien_ban_nguon"] = "2"
    bo2.nguon["phien_ban_nguon"] = "2"
    bo2.nguon_duoc_cap[bo2.nguon["ma_nguon"]] = deepcopy(bo2.nguon)
    bo2.nhan()
    _, bon = kiem_phu_nguon(bo2, bo2.cat())
    assert [d["ma_doan"] for d in ba] != [d["ma_doan"] for d in bon]


@pytest.mark.parametrize("do_dai,dat", [(8000, True), (8001, False)])
def test_don_vi_khong_chia_an_toan_bien_tam_nghin(do_dai, dat):
    bo = BoCatDoan(van_ban="DEMO " + "x" * (do_dai - 5))
    bo.nhan()
    kq = bo.cat()
    if dat:
        _, ds = kiem_phu_nguon(bo, kq)
        assert len(ds) == 1 and len(ds[0]["nguyen_van"]) == 8000
    else:
        loi(kq, "TC_KHONG_CAT_DUOC")
        assert bo.core.so_lan_ghi["tep"] == 1


def test_dieu_dai_chia_duoc_theo_cau_khong_tu_choi_ca_dieu():
    bo = BoCatDoan(van_ban="Điều 1. DEMO\nKhoản 1. " + "Nội dung DEMO hợp lệ. " * 1000)
    bo.nhan()
    _, ds = kiem_phu_nguon(bo, bo.cat(muc_tieu=2000))
    assert len(ds) > 10 and all(len(d["nguyen_van"]) <= 2000 for d in ds)


@pytest.mark.parametrize("gioi_han,so_dieu", [(2, 3), (5000, 5001)])
def test_vuot_so_doan_khong_upload_ban_cat_cuoi(gioi_han, so_dieu):
    bo = BoCatDoan(van_ban="".join(f"Điều {i}. DEMO\n" for i in range(1, so_dieu + 1)))
    bo.dat_cau_hinh({"cat_doan": {"so_doan_toi_da": gioi_han}})
    bo.nhan()
    loi(bo.cat(), "TC_QUA_GIOI_HAN")
    assert bo.core.so_lan_ghi["tep"] == 1


def test_bang_hang_qua_dai_khong_cat_giua_o():
    bo = BoCatDoan()
    pb = bang_demo(bo, docx=True, so_hang=2, gop=False)
    b = pb["van_ban_tai_lieu"]["khoi"][1]
    o = b["o"][-1]
    cu = pb["van_ban_tai_lieu"]["van_ban"]
    chen = " DEMO " + "x" * 8100
    pb["van_ban_tai_lieu"]["van_ban"] = cu[:o["ket_thuc"]] + chen + cu[o["ket_thuc"]:]
    o["ket_thuc"] += len(chen); o["van_ban"] += chen
    b["ket_thuc"] += len(chen)
    bo.nguon_co_cau_truc(pb)
    bo.nhan()
    loi(bo.cat(), "TC_KHONG_CAT_DUOC")


@pytest.mark.parametrize("sai", ["khong-cua", "khong-giay", "true", "khong-dau-vao", "scope", "module", "nguoi", "metadata", "quyen-snapshot", "quyen-goc", "quyen-ocr", "nguon"])
def test_cat_kiem_quyen_song_tung_tep_va_ngu_canh(sai):
    bo = BoCatDoan()
    bo.nhan(); bo.giao_cat()
    cap = bo.core.cua.giay_cap[bo.cat_id]
    if sai == "khong-cua":
        bo.app.cua_nguon = None
    elif sai == "khong-giay":
        del bo.core.cua.giay_cap[bo.cat_id]
    elif sai == "true":
        bo.core.cua.giay_cap[bo.cat_id] = True
    elif sai == "khong-dau-vao":
        cap.pop("dau_vao")
    elif sai in {"scope", "module", "nguoi"}:
        cap["ngu_canh_core"][{"scope": "ma_pham_vi", "module": "module", "nguoi": "nguoi_hoi_id"}[sai]] = "DEMO-sai"
    elif sai == "metadata":
        cap["metadata_core"]["trang_thai_duyet"] = "da_duyet"
    elif sai == "nguon":
        cap["nguon"] = {}
    else:
        tep = {"quyen-snapshot": bo.pb_nhan["ho_so_tra_cuu"]["ho_so"]["tep_id"],
               "quyen-goc": bo.goc["tep"]["tep_id"], "quyen-ocr": bo.vb["tep"]["tep_id"]}[sai]
        bo.core.tep_duoc_mo[bo.cat_id].remove(tep)
    bo.core.chay(bo.app)
    loi(bo.core.xem(bo.cat_id), "TC_SAI_NGUON" if sai == "metadata" else "TC_CHUA_CO_CUA_CORE")
    assert bo.core.so_lan_ghi["tep"] == 1


@pytest.mark.parametrize("sai", ["bam-snapshot", "bytes-snapshot", "bam-goc", "phien-ban", "bam-toan-van", "bam-cau-hinh", "bam-danh-muc", "summary", "pb-ocr", "nguon-snapshot"])
def test_snapshot_hoac_nguon_bi_thay_khong_tin_caller(sai):
    bo = BoCatDoan()
    bo.nhan()
    pb = deepcopy(bo.pb_nhan)
    if sai == "bam-snapshot":
        pb["ho_so_tra_cuu"]["bam_ho_so"] = "sha256:" + "0" * 64
    elif sai == "bytes-snapshot":
        tid = pb["ho_so_tra_cuu"]["ho_so"]["tep_id"]
        ten, mime, b = bo.core._tep[tid]
        bo.core._tep[tid] = (ten, mime, b + b"DEMO")
    elif sai in {"bam-cau-hinh", "bam-danh-muc"}:
        pb["ho_so_tra_cuu"][sai.replace("-", "_")] = "sha256:" + "0" * 64
    elif sai == "summary":
        pb["ho_so_tra_cuu"]["tom_tat"]["so_doan"] = 1
    elif sai == "pb-ocr":
        pb = bo.doi_snapshot(lambda s: s["du_lieu"]["tai_lieu"]["van_ban_tai_lieu"]["van_ban_tai_lieu"].update(van_ban="DEMO doi"))
    elif sai == "nguon-snapshot":
        pb = bo.doi_snapshot(lambda s: s["nguon"][0].update(phien_ban_nguon="DEMO-2"))
    else:
        bo.nguon_duoc_cap[bo.nguon["ma_nguon"]][{"bam-goc": "bam_goc", "phien-ban": "phien_ban_nguon", "bam-toan-van": "bam_van_ban"}[sai]] = (
            "DEMO-2" if sai == "phien-ban" else "sha256:" + "0" * 64)
    loi(bo.cat(pb), "TC_SAI_NGUON")
    assert bo.core.so_lan_ghi["tep"] == 1


@pytest.mark.parametrize("sua", ["task", "stage"])
def test_cat_chi_nhan_dung_tac_vu_giai_doan(sua):
    bo = BoCatDoan(); bo.nhan()
    pb = deepcopy(bo.pb_nhan)
    pb["ho_so_tra_cuu"]["tac_vu" if sua == "task" else "giai_doan"] = "phan_loai" if sua == "task" else "da_cat_doan"
    loi(bo.cat(pb), "TC_SAI_GIAI_DOAN")


def test_chi_dung_cau_hinh_ghim_tu_ngan_khong_doc_lai_giua_chuoi():
    bo = BoCatDoan(van_ban="Điều 1. DEMO\n" + "Nội dung DEMO có dấu. " * 100)
    bo.nhan()
    bo.dat_cau_hinh({"cat_doan": {"ky_tu_don_vi_toi_da": 200, "do_dai_muc_tieu": 200, "so_doan_toi_da": 1}})
    s, ds = kiem_phu_nguon(bo, bo.cat())
    assert len(ds) > 1 and s["cau_hinh"] == bo.s_nhan["cau_hinh"]
    assert s["cau_hinh"]["row_version"] != bo.app.ngan.doc("cau_hinh", {}).row_version


@pytest.mark.parametrize("p", [None, "", "DEMO-Q"])
def test_phap_nhan_khong_du_hoac_khac_ngu_canh(p):
    bo = BoCatDoan(); bo.nhan()
    loi(bo.cat(phap_nhan=p), "TC_THIEU_NGU_CANH" if not p else "TC_CHUA_CO_CUA_CORE")


def test_tran_snapshot_ket_qua_tu_choi_truoc_upload():
    bo = BoCatDoan(van_ban="".join(f"Điều {i}. DEMO\n" for i in range(100)))
    bo.dat_cau_hinh({"ngan_sach": {"tep_toi_da_byte": 20000}})
    bo.nhan()
    loi(bo.cat(), "TC_QUA_GIOI_HAN")
    assert bo.core.so_lan_ghi["tep"] == 1


@pytest.mark.parametrize("moc", ["snapshot", "goc", "ocr", "cat"])
def test_huy_khi_doc_va_cat_theo_cum_khong_upload(moc, monkeypatch):
    bo = BoCatDoan(van_ban="".join(f"Điều {i}. DEMO\n" for i in range(100)))
    bo.nhan(); bo.giao_cat()
    if moc == "cat":
        goc = bo.core._tien_do

        def huy_cum(ma, viec_id, phan_tram, cau):
            if viec_id == bo.cat_id and 20 < phan_tram < 90:
                bo.core.huy(viec_id)
            return goc(ma, viec_id, phan_tram, cau)

        monkeypatch.setattr(bo.core, "_tien_do", huy_cum)
    else:
        tid = {"snapshot": bo.pb_nhan["ho_so_tra_cuu"]["ho_so"]["tep_id"],
               "goc": bo.goc["tep"]["tep_id"], "ocr": bo.vb["tep"]["tep_id"]}[moc]
        bo.core.sau_doc = lambda viec_id, tep: bo.core.huy(viec_id) if tep == tid else None
    bo.core.chay(bo.app)
    assert bo.core.xem(bo.cat_id)["trang_thai"] == "HUY"
    assert bo.core.so_lan_ghi["tep"] == bo.core.so_lan_ghi["ket_qua"] == 1


@pytest.mark.parametrize("thao_tac", ["tep", "ket_qua", "ket_thuc"])
def test_cat_mat_ack_van_mot_ket_qua(thao_tac):
    bo = BoCatDoan(); bo.nhan()
    bo.core.gay_mat_xac_nhan(thao_tac, 3)
    kiem_phu_nguon(bo, bo.cat())
    assert all(bo.core.so_lan_ghi[k] == 2 for k in ("tep", "ket_qua", "ket_thuc"))


@pytest.mark.parametrize("cua", ["_tien_do", "_tai_tep_ra", "_nop_ket_qua"])
def test_cat_mat_lease_khong_nop_xong(cua, monkeypatch):
    bo = BoCatDoan(); bo.nhan(); bo.giao_cat()

    def mat_lease(ma, viec_id, *args, **kwargs):
        bo.core._viec[viec_id]["trang_thai"] = "CHO"
        raise LoiDuongTruyen("MAT_LEASE", http_status=409)

    monkeypatch.setattr(bo.core, cua, mat_lease)
    bo.core.chay(bo.app)
    assert bo.core.xem(bo.cat_id)["trang_thai"] == "CHO"
    assert bo.core.so_lan_ghi["ket_qua"] == bo.core.so_lan_ghi["ket_thuc"] == 1


def test_chua_ro_tu_cua_core_khong_doi_thanh_xong(monkeypatch):
    bo = BoCatDoan(); bo.nhan()

    def chua_ro(viec_id):
        raise ChuaRo("DEMO-TC3-tuong-quan")

    monkeypatch.setattr(bo.core.cua, "doc_quyen", chua_ro)
    assert bo.cat()["trang_thai"] == "CHUA_RO"
    assert bo.core.so_lan_ghi["ket_qua"] == 1


def test_cat_khong_ai_khong_index_khong_ghi_tep_ben_va_log_khong_noi_dung(monkeypatch, capsys):
    bo = BoCatDoan(); bo.nhan()
    dem = {"AI": 0, "Cloud": 0, "tim_kiem": 0, "ghi_dia": 0}

    def cam(ten):
        def dung(*args, **kwargs):
            dem[ten] += 1
            raise AssertionError("DEMO đã gọi cửa ngoài phạm vi.")
        return dung

    for ten in ("nhung_vector", "hoi_ai", "goi_engine"):
        monkeypatch.setattr(bo.app, ten, cam("AI"), raising=False)
    monkeypatch.setattr(bo.app, "cloud", cam("Cloud"), raising=False)
    monkeypatch.setattr(bo.app, "tim_kiem", cam("tim_kiem"), raising=False)
    monkeypatch.setattr("builtins.open", cam("ghi_dia"))
    kiem_phu_nguon(bo, bo.cat())
    assert dem == {"AI": 0, "Cloud": 0, "tim_kiem": 0, "ghi_dia": 0}
    for su_kien in bo.core.nhat_ky:
        if su_kien[0] == "tien_do":
            assert "Ánh Dương" not in str(su_kien) and "1.000.000" not in str(su_kien)
    assert capsys.readouterr().err == ""


def test_cat_doc_luong_ngan_van_kiem_du_bytes(monkeypatch):
    goc = Viec.mo_tep

    class Ngan(io.BytesIO):
        def read(self, n=-1):
            return super().read(min(n, 11))

    def mo(self, tep_id):
        with goc(self, tep_id) as f:
            return Ngan(f.read())

    bo = BoCatDoan(); bo.nhan()
    monkeypatch.setattr(Viec, "mo_tep", mo)
    kiem_phu_nguon(bo, bo.cat())
