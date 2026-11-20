"""PL-5A: DEMO thuần và đã kiểm bằng Core giả (CoreGia), không gọi mạng.

CoreGia không chứng nhận quyền/cùng việc của Core thật; kiểm thêm hình dạng
đối tượng tep_id theo test_pl0_can_core, không chấp nhận chuỗi trơn.
"""
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sys
import unicodedata

import pytest

TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / "goi" / "e_phan_luong"
sys.path.insert(0, str(GOI))

from e_phan_luong import chuoi_ai
from e_phan_luong.loi import CAU_LOI, loi


def doc_demo(ten):
    return json.loads((TESTS / "demo" / ten).read_text(encoding="utf-8"), parse_float=Decimal)


def json_bytes(gia_tri):
    return json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


@pytest.fixture
def danh_muc():
    return {m["ma"]: m for m in doc_demo("danh-muc-loai-DEMO.json")}


@pytest.fixture
def tham_so():
    yc = doc_demo("yeu-cau-ai-DEMO.json")["yeu_cau_ai"]
    return {k: yc[k] for k in ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien")}


def phong_bi():
    return doc_demo("tra-loi-ai-dung-enum.json")


def chuyen_tiep():
    return phong_bi()["tra_loi_ai"]["chuyen_tiep"]


def kiem_loi(ham, ma):
    with pytest.raises(type(loi(ma))) as bat:
        ham()
    assert bat.value.ma == ma
    assert bat.value.thong_diep == CAU_LOI[ma]


def muc(chi_so=0, loai="chi_phi_khac", tin_cay=Decimal("0.9")):
    return {"chi_so": chi_so, "loai": loai, "tin_cay": tin_cay}


def doc_ai(pb, danh_muc, so_tai_lieu=1, nguong=Decimal("0.7")):
    return chuoi_ai.doc_tra_loi_ai(pb, danh_muc=danh_muc, so_tai_lieu=so_tai_lieu,
                                  nguong_tin_cay=nguong)


def kiem_canh_bao(canh_bao):
    assert canh_bao and all(isinstance(cau, str) and cau for cau in canh_bao)
    noi_dung = " ".join(canh_bao).casefold()
    for cam in ("%", "tỷ lệ", "xác suất", "bậc", "0.9", "0.4", "NOI-DUNG-DEMO-BI-MAT".casefold()):
        assert cam not in noi_dung
    assert len(noi_dung) <= 500


def test_khu_trung_nfc_khoang_trang_giu_nguyen_lan_dau_va_chi_so_dong():
    goc = "  " + unicodedata.normalize("NFD", "Công ty DEMO Ánh Dương") + "\t"
    ds = [(7, goc), (2, "Công  ty\nDEMO Ánh\u00a0Dương"), (11, "Khác DEMO"), (20, goc)]
    cu = deepcopy(ds)
    tai_lieu, anh_xa = chuoi_ai.lap_tai_lieu(ds)
    assert tai_lieu == [{"chi_so": 0, "noi_dung": goc}, {"chi_so": 1, "noi_dung": "Khác DEMO"}]
    assert anh_xa == {0: [7, 2, 20], 1: [11]}
    assert ds == cu


def test_khu_trung_khong_bo_dau_hay_doi_chu_hoa():
    ds = list(enumerate(("Công DEMO", "công DEMO", "Cong DEMO")))
    assert len(chuoi_ai.lap_tai_lieu(ds)[0]) == 3
    assert chuoi_ai.lap_tai_lieu([]) == ([], {})


def test_bien_2000_ky_tu_bo_rieng_dong_dai_khong_cat_va_dem_duoc():
    dung = "Đ" * 2000
    dai = "Đ" * 2001
    ds = [(0, dai), (1, dung), (2, dung), (3, " " * 2001 + "DEMO"), (4, "DEMO")]
    tai_lieu, anh_xa = chuoi_ai.lap_tai_lieu(ds)
    assert tai_lieu == [{"chi_so": 0, "noi_dung": dung}, {"chi_so": 1, "noi_dung": "DEMO"}]
    assert anh_xa == {0: [1, 2], 1: [4]}
    assert len(ds) - sum(map(len, anh_xa.values())) == 2
    assert chuoi_ai.lap_tai_lieu([(0, dai)]) == ([], {})


def test_tran_5000_gia_tri_sau_khu_trung_khong_cat_ngam():
    ds = [(i, f"Nội dung DEMO {i}") for i in range(5000)]
    tai_lieu, anh_xa = chuoi_ai.lap_tai_lieu(ds)
    assert len(tai_lieu) == len(anh_xa) == 5000
    assert tai_lieu[-1] == {"chi_so": 4999, "noi_dung": "Nội dung DEMO 4999"}
    kiem_loi(lambda: chuoi_ai.lap_tai_lieu(ds + [(5000, "Nội dung DEMO khác")]), "VUOT_GIOI_HAN")
    # Một lô nhiều dòng vẫn chỉ gửi một giá trị nếu nội dung trùng nhau.
    assert chuoi_ai.lap_tai_lieu([(i, "DEMO") for i in range(5001)])[1] == {0: list(range(5001))}


@pytest.mark.parametrize("ds", [[(True, "DEMO")], [(-1, "DEMO")], [(0, None)]])
def test_tai_lieu_sai_kieu(ds):
    kiem_loi(lambda: chuoi_ai.lap_tai_lieu(ds), "DU_LIEU_KHONG_HOP_LE")


def test_khuon_draft_2020_12_va_phong_bi_demo_dung_schema(danh_muc, tham_so):
    jsonschema = pytest.importorskip("jsonschema", reason="Venv không có jsonschema; chỉ dùng trong test.")
    khuon = chuoi_ai.khuon_tra_loi(danh_muc)
    jsonschema.Draft202012Validator.check_schema(khuon)
    jsonschema.Draft202012Validator.check_schema(chuoi_ai.khuon_tra_loi({}))
    bo_kiem = jsonschema.Draft202012Validator(khuon)
    assert bo_kiem.is_valid(phong_bi()["tra_loi_ai"]["du_lieu"])
    assert bo_kiem.is_valid({"phan_loai": []})
    for sai in ({"phan_loai": [], "them": True}, {"phan_loai": [muc(loai="ngoai_DEMO")]},
                {"phan_loai": [muc(chi_so=True)]}, {"phan_loai": [muc(tin_cay=True)]},
                {"phan_loai": [muc(tin_cay=2)]}, {"phan_loai": [{**muc(), "them": 1}]}):
        assert not bo_kiem.is_valid(sai)
    for ten, loai in (("yeu-cau-ai-DEMO.json", "yeu_cau_ai"),
                      ("tra-loi-ai-dung-enum.json", "tra_loi_ai"),
                      ("tra-loi-ai-sai-enum.json", "tra_loi_ai"),
                      ("tra-loi-ai-tin-cay-thap.json", "tra_loi_ai"),
                      ("tra-loi-ai-cloud.json", "tra_loi_ai"),
                      ("tra-loi-ai-khong-thay-can-cu.json", "tra_loi_ai")):
        schema = json.loads((TESTS.parents[1] / "_chung" / "contract" / f"{loai}.schema.json")
                            .read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(doc_demo(ten))
        if loai == "yeu_cau_ai":
            tai_lieu, _ = chuoi_ai.lap_tai_lieu([(9, "Nội dung DEMO")])
            yc = chuoi_ai.lap_yeu_cau_ai(tai_lieu, danh_muc, tham_so, chuyen_tiep())
            jsonschema.Draft202012Validator(schema).validate(yc)
            ct = chuyen_tiep()
            ct["phan_luong"]["khong_can_ai"] = True
            jsonschema.Draft202012Validator(schema).validate(
                chuoi_ai.lap_yeu_cau_ai([], {}, tham_so, ct))
    # Các mã/điểm là metadata, không bị Hỏi AI bắt chép nguyên văn nội dung.
    for node in khuon["properties"]["phan_loai"]["items"]["properties"].values():
        assert node["$comment"] == "ktt:ai12:metadata"


def test_lap_yeu_cau_giu_prompt_module_model_va_json_tai_lieu(danh_muc, tham_so):
    tai_lieu, _ = chuoi_ai.lap_tai_lieu([(5, "Nội dung DEMO Ánh Dương")])
    ct = chuyen_tiep()
    cu = deepcopy((tai_lieu, tham_so, ct, danh_muc))
    yc = chuoi_ai.lap_yeu_cau_ai(tai_lieu, danh_muc, tham_so, ct)["yeu_cau_ai"]
    for k in ("ma_prompt", "phien_ban_prompt", "prompt", "model_uu_tien"):
        assert yc[k] == tham_so[k]
    assert json.loads(yc["tai_lieu"]) == tai_lieu
    assert "Ánh Dương" in yc["tai_lieu"]
    assert yc["bat_buoc_trich_dan"] is False
    assert yc["chuyen_tiep"] == ct
    assert set(yc) == {"phien_ban", "ma_prompt", "phien_ban_prompt", "prompt", "tai_lieu",
                       "khuon_tra_loi", "bat_buoc_trich_dan", "model_uu_tien", "chuyen_tiep"}
    assert (tai_lieu, tham_so, ct, danh_muc) == cu
    ct["phan_luong"]["tep_lo"]["ten"] = "Đã đổi DEMO"
    assert yc["chuyen_tiep"] == cu[2]


@pytest.mark.parametrize("gia_tri", [None, "", " \t\n", 1, True])
@pytest.mark.parametrize("khoa", ["ma_prompt", "phien_ban_prompt", "prompt"])
def test_thieu_prompt_hoac_sai_kieu_khong_tu_viet_prompt(khoa, gia_tri, danh_muc, tham_so):
    tham_so[khoa] = gia_tri
    kiem_loi(lambda: chuoi_ai.lap_yeu_cau_ai([], danh_muc, tham_so, chuyen_tiep()), "THAM_SO_KHONG_HOP_LE")
    del tham_so[khoa]
    kiem_loi(lambda: chuoi_ai.lap_yeu_cau_ai([], danh_muc, tham_so, chuyen_tiep()), "THAM_SO_KHONG_HOP_LE")


@pytest.mark.parametrize("model", [None, "", " \t", "DEMO-local-gia"])
def test_model_tuy_chon(model, danh_muc, tham_so):
    tham_so["model_uu_tien"] = model
    yc = chuoi_ai.lap_yeu_cau_ai([], danh_muc, tham_so, chuyen_tiep())["yeu_cau_ai"]
    assert yc["model_uu_tien"] == (model if model and model.strip() else None)
    del tham_so["model_uu_tien"]
    assert chuoi_ai.lap_yeu_cau_ai([], danh_muc, tham_so, chuyen_tiep())["yeu_cau_ai"]["model_uu_tien"] is None


def test_khong_can_ai_tai_lieu_rong_va_bo_qua_du_lieu_phan_loai(danh_muc, tham_so):
    ct = chuyen_tiep()
    ct["phan_luong"]["khong_can_ai"] = True
    yc = chuoi_ai.lap_yeu_cau_ai([{"chi_so": 0, "noi_dung": "DEMO"}], danh_muc, tham_so, ct)
    assert yc["yeu_cau_ai"]["tai_lieu"] == ""
    pb = phong_bi()
    pb["tra_loi_ai"].update(chuyen_tiep=ct, du_lieu=None)
    assert doc_ai(pb, danh_muc, 0) == ({}, [])


def test_lap_chuyen_tiep_giu_nguyen_doi_tuong_tep_khong_dung_chuoi_tron():
    pl = chuyen_tiep()["phan_luong"]
    tep = deepcopy(pl["tep_lo"])
    ct = chuoi_ai.lap_chuyen_tiep(tep, pl["bam_tep"], pl["khau"], False)
    assert ct == chuyen_tiep()
    tep["ten"] = "Đã đổi DEMO"
    assert ct["phan_luong"]["tep_lo"] == pl["tep_lo"]
    assert len(json_bytes(ct)) <= 4096
    pb = phong_bi()
    assert chuoi_ai.doc_chuyen_tiep(pb) == pl
    chuoi_ai.doc_chuyen_tiep(pb)["tep_lo"]["ten"] = "Bản sao DEMO"
    assert pb == phong_bi()


def test_bien_chuyen_tiep_4kib_tinh_theo_byte_utf8_khong_cat():
    pl = chuyen_tiep()["phan_luong"]
    ct = chuoi_ai.lap_chuyen_tiep(pl["tep_lo"], pl["bam_tep"], pl["khau"], False)
    con = 4096 - len(json_bytes(ct))
    tep = deepcopy(pl["tep_lo"])
    tep["ten"] += "Đ" * (con // 2) + "x" * (con % 2)
    ct = chuoi_ai.lap_chuyen_tiep(tep, pl["bam_tep"], pl["khau"], False)
    assert len(json_bytes(ct)) == 4096
    tep["ten"] += "x"
    kiem_loi(lambda: chuoi_ai.lap_chuyen_tiep(tep, pl["bam_tep"], pl["khau"], False), "VUOT_GIOI_HAN")
    ct["phan_luong"]["tep_lo"] = tep
    pb = phong_bi()
    pb["tra_loi_ai"]["chuyen_tiep"] = ct
    kiem_loi(lambda: chuoi_ai.doc_chuyen_tiep(pb), "CHUOI_KHONG_KHOP")


@pytest.mark.parametrize("khoa,gia_tri", [
    ("phien_ban", True), ("phien_ban", 2), ("tep_lo", "tep-DEMO-lo-chuyen-tiep"),
    ("tep_lo", {"tep_id": "tep-DEMO-lo-chuyen-tiep"}), ("bam_tep", "sha256:DEMO"),
    ("khau", ""), ("khau", "x" * 41), ("khong_can_ai", 0),
])
def test_doc_chuyen_tiep_sai_dang(khoa, gia_tri):
    pb = phong_bi()
    pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"][khoa] = gia_tri
    kiem_loi(lambda: chuoi_ai.doc_chuyen_tiep(pb), "CHUOI_KHONG_KHOP")


@pytest.mark.parametrize("khoa,gia_tri", [
    ("tep_id", None), ("tep_id", ""), ("ten", None), ("mime", []),
    ("kich_thuoc", True), ("kich_thuoc", -1), ("kich_thuoc", "12117"),
])
def test_doc_chuyen_tiep_metadata_tep_sai(khoa, gia_tri):
    pb = phong_bi()
    pb["tra_loi_ai"]["chuyen_tiep"]["phan_luong"]["tep_lo"][khoa] = gia_tri
    kiem_loi(lambda: chuoi_ai.doc_chuyen_tiep(pb), "CHUOI_KHONG_KHOP")


@pytest.mark.parametrize("tiep", [None, {}, [], "tep-DEMO", {"phan_luong": {}}])
def test_chuyen_tiep_thieu_la_loi_chuoi_ke_ca_ai_khong_thay_can_cu(tiep, danh_muc):
    pb = doc_demo("tra-loi-ai-khong-thay-can-cu.json")
    pb["tra_loi_ai"]["chuyen_tiep"] = tiep
    kiem_loi(lambda: chuoi_ai.doc_chuyen_tiep(pb), "CHUOI_KHONG_KHOP")
    kiem_loi(lambda: doc_ai(pb, danh_muc), "CHUOI_KHONG_KHOP")
    del pb["tra_loi_ai"]["chuyen_tiep"]
    kiem_loi(lambda: chuoi_ai.doc_chuyen_tiep(pb), "CHUOI_KHONG_KHOP")


@pytest.mark.parametrize("dau_vao", [
    None, {}, "tep-DEMO", {"tep_lo": "tep-DEMO"}, {"tep_id_khac": "tep-DEMO"},
    {"tep_id": None}, {"tep_id": 1}, {"tep_id": " \t"},
])
def test_hinh_dang_tham_chieu_nghiem_tu_choi_chuoi_tron_va_khoa_gan_dung(dau_vao):
    kiem_loi(lambda: chuoi_ai.kiem_tham_chieu_tep(dau_vao), "CHUOI_KHONG_KHOP")


@pytest.mark.parametrize("dau_vao", [
    {"tep_id": "tep-DEMO"}, {"chuyen_tiep": {"phan_luong": {"tep_lo": {"tep_id": "tep-DEMO"}}}},
    {"chuyen_tiep": [{"sau": [{"tep_id": "tep-DEMO"}]}]},
])
def test_hinh_dang_tham_chieu_nghiem_nhan_doi_tuong_long_trong_mang(dau_vao):
    assert chuoi_ai.kiem_tham_chieu_tep(dau_vao) is None


@pytest.mark.parametrize("ten,mong,co_canh_bao", [
    ("tra-loi-ai-dung-enum.json", {0: "chi_phi_khac"}, False),
    ("tra-loi-ai-sai-enum.json", {}, True),
    ("tra-loi-ai-tin-cay-thap.json", {}, True),
    ("tra-loi-ai-khong-thay-can-cu.json", {}, True),
])
def test_phong_bi_ai_gia_demo(ten, mong, co_canh_bao, danh_muc):
    pb = doc_demo(ten)
    cu = deepcopy(pb)
    ket_qua, canh_bao = doc_ai(pb, danh_muc)
    assert ket_qua == mong
    if co_canh_bao:
        kiem_canh_bao(canh_bao)
    else:
        assert canh_bao == []
    assert pb == cu


@pytest.mark.parametrize("nha_cung_cap", ["cloud", "LOCAL", "", None, 1])
def test_chi_nhan_local_ke_ca_khong_co_can_cu(nha_cung_cap, danh_muc):
    pb = doc_demo("tra-loi-ai-cloud.json")
    pb["tra_loi_ai"]["nha_cung_cap"] = nha_cung_cap
    kiem_loi(lambda: doc_ai(pb, danh_muc), "KHONG_PHAI_LOCAL")
    pb["tra_loi_ai"]["trang_thai"] = "khong_thay_can_cu"
    kiem_loi(lambda: doc_ai(pb, danh_muc), "KHONG_PHAI_LOCAL")


@pytest.mark.parametrize("du_lieu", [
    None, [], "DEMO", {}, {"phan_loai": {}}, {"phan_loai": [], "them": 1},
    {"phan_loai": [None]}, {"phan_loai": [muc(), {"chi_so": 1, "loai": "luong"}]},
    {"phan_loai": [{**muc(), "them": "DEMO"}]},
])
def test_sai_khuon_khong_loi_ca_luot_nhung_khong_nhan_mot_phan(du_lieu, danh_muc):
    pb = phong_bi()
    pb["tra_loi_ai"]["du_lieu"] = du_lieu
    ket_qua, canh_bao = doc_ai(pb, danh_muc)
    assert ket_qua == {}
    kiem_canh_bao(canh_bao)


@pytest.mark.parametrize("khoa,gia_tri", [
    ("chi_so", True), ("chi_so", "0"), ("chi_so", 0.0), ("loai", []),
    ("tin_cay", True), ("tin_cay", "0.9"), ("tin_cay", None), ("tin_cay", -0.1),
    ("tin_cay", 1.01), ("tin_cay", float("nan")), ("tin_cay", float("inf")),
    ("tin_cay", Decimal("NaN")), ("tin_cay", Decimal("sNaN")), ("tin_cay", Decimal("Infinity")),
])
def test_khuon_sai_kieu_bool_va_so_khong_huu_han(khoa, gia_tri, danh_muc):
    pb = phong_bi()
    sai = muc(1)
    sai[khoa] = gia_tri
    pb["tra_loi_ai"]["du_lieu"] = {"phan_loai": [muc(), sai]}
    ket_qua, canh_bao = doc_ai(pb, danh_muc, 2)
    assert ket_qua == {}
    kiem_canh_bao(canh_bao)


def test_bo_rieng_chi_so_enum_can_cu_va_giu_muc_dau_khi_trung(danh_muc):
    pb = phong_bi()
    pb["tra_loi_ai"]["du_lieu"] = {"phan_loai": [
        muc(0, tin_cay=0.7), muc(-1), muc(6), muc(1, "ngoai_DEMO"),
        muc(2, tin_cay=Decimal("0.6999999999999999999999999999")),
        muc(0, "luong"), muc(1, "luong"), muc(2, "luong"), muc(3, "tam_ung"),
    ]}
    ket_qua, canh_bao = doc_ai(pb, danh_muc, 4)
    assert ket_qua == {0: "chi_phi_khac", 3: "tam_ung"}
    assert len(canh_bao) == len(set(canh_bao)) == 4
    kiem_canh_bao(canh_bao)


@pytest.mark.parametrize("diem,nguong,mong", [
    (Decimal("0.7"), Decimal("0.7"), True), (0.7, Decimal("0.7"), True),
    (0.7, Decimal("0.7000000000000000000000000001"), False),
    (0, Decimal(0), True), (1, Decimal(1), True),
])
def test_bien_nguong_decimal_khong_mat_do_chinh_xac(diem, nguong, mong, danh_muc):
    pb = phong_bi()
    pb["tra_loi_ai"]["du_lieu"] = {"phan_loai": [muc(tin_cay=diem)]}
    ket_qua, canh_bao = doc_ai(pb, danh_muc, nguong=nguong)
    assert ket_qua == ({0: "chi_phi_khac"} if mong else {})
    assert bool(canh_bao) is not mong


def test_khong_chep_canh_bao_diem_hay_noi_dung_ai_ra_ngoai(danh_muc):
    pb = phong_bi()
    pb["tra_loi_ai"]["canh_bao"] = ["Tỷ lệ 99%, xác suất 0.9, bậc DEMO; NOI-DUNG-DEMO-BI-MAT"]
    pb["tra_loi_ai"]["tra_loi"] = "NOI-DUNG-DEMO-BI-MAT"
    pb["tra_loi_ai"]["du_lieu"] = {"phan_loai": [muc(0, "NOI-DUNG-DEMO-BI-MAT"),
                                                   *[muc(i, tin_cay=0.4) for i in range(1, 100)]]}
    ket_qua, canh_bao = doc_ai(pb, danh_muc, 100)
    assert ket_qua == {}
    assert len(canh_bao) == 2
    kiem_canh_bao(canh_bao)


def test_khu_trung_anh_xa_ket_qua_ai_ve_dung_cac_dong_goc(danh_muc):
    _, anh_xa = chuoi_ai.lap_tai_lieu([(8, "DEMO"), (1, " DEMO "), (4, "Khác DEMO")])
    pb = phong_bi()
    pb["tra_loi_ai"]["du_lieu"] = {"phan_loai": [muc(0), muc(1, "luong")]}
    ket_qua, _ = doc_ai(pb, danh_muc, 2)
    theo_dong = {dong: loai for chi_so, loai in ket_qua.items() for dong in anh_xa[chi_so]}
    assert theo_dong == {8: "chi_phi_khac", 1: "chi_phi_khac", 4: "luong"}


def test_chuyen_tiep_tep_thuc_qua_core_gia_mo_lai_duoc(danh_muc, tham_so):
    """Đã kiểm bằng Core giả (CoreGia); không chứng nhận quyền Core thật."""
    from kho_tri_thuc_sdk.engine import Engine
    from kho_tri_thuc_sdk.thu import CoreGia

    phieu = json.loads((GOI / "engine.json").read_text(encoding="utf-8"))
    phieu["nang_luc"] = [
        {"ma": "demo.chuan_bi@1", "ten": "Chuẩn bị yêu cầu DEMO",
         "nhan": ["tep"], "tra": "yeu_cau_ai",
         "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 300}},
        {"ma": "demo.ai_gia@1", "ten": "Trả phong bì AI giả DEMO",
         "nhan": ["yeu_cau_ai"], "tra": "tra_loi_ai", "gioi_han": {"thoi_han_giay": 300}},
        {"ma": "demo.mo_lai@1", "ten": "Mở lô DEMO sau AI giả",
         "nhan": ["tra_loi_ai"], "tra": "van_ban",
         "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 300}},
    ]
    thu = Engine(phieu)
    raw = (TESTS / "demo" / "lo-chuyen-tiep-DEMO.json").read_bytes()
    core = CoreGia()
    tep_da_gui = {}

    @thu.nang_luc("demo.chuan_bi@1")
    def chuan_bi(viec):
        with viec.mo_tep(viec.dau_vao["tep"]["tep_id"]) as f:
            assert f.read() == raw
        tep = viec.tai_tep_ra("lo-chuyen-tiep-DEMO.json", raw, "application/json")
        tep_da_gui.update(tep)
        ct = chuoi_ai.lap_chuyen_tiep(tep, "sha256:" + sha256(raw).hexdigest(), "ktt_duyet", False)
        tai_lieu, _ = chuoi_ai.lap_tai_lieu([(0, "Nội dung DEMO")])
        return chuoi_ai.lap_yeu_cau_ai(tai_lieu, danh_muc, tham_so, ct)

    @thu.nang_luc("demo.ai_gia@1")
    def ai_gia(viec):
        # Phong bì đi qua SDK phải tuần tự hóa được bằng JSON chuẩn.
        # Decimal chỉ dùng lúc kiểm nghiệp vụ, không phải kiểu số trên dây.
        pb = json.loads((TESTS / "demo" / "tra-loi-ai-dung-enum.json").read_text(encoding="utf-8"))
        yc = viec.dau_vao
        pb["tra_loi_ai"].update(chuyen_tiep=deepcopy(yc["yeu_cau_ai"]["chuyen_tiep"]),
                                bam_dau_vao="sha256:" + sha256(json_bytes(yc)).hexdigest())
        return pb

    @thu.nang_luc("demo.mo_lai@1")
    def mo_lai(viec):
        pl = chuoi_ai.doc_chuyen_tiep(viec.dau_vao)
        chuoi_ai.kiem_tham_chieu_tep(viec.dau_vao)
        assert pl["tep_lo"] == tep_da_gui
        with viec.mo_tep(pl["tep_lo"]["tep_id"]) as f:
            da_doc = f.read()
        assert da_doc == raw
        assert len(da_doc) == pl["tep_lo"]["kich_thuoc"]
        assert "sha256:" + sha256(da_doc).hexdigest() == pl["bam_tep"]
        assert doc_ai(viec.dau_vao, danh_muc) == ({0: "chi_phi_khac"}, [])
        return {"loai": "van_ban", "van_ban": "Đã mở lại lô DEMO."}

    tep_goc = core.them_tep("lo-DEMO.json", raw, "application/json")
    dau_vao = {"loai": "tep", "tep": tep_goc}
    for nang_luc in ("demo.chuan_bi@1", "demo.ai_gia@1", "demo.mo_lai@1"):
        ket_qua = core.chay_thu(thu, nang_luc, dau_vao)
        assert ket_qua["trang_thai"] == "XONG", ket_qua
        dau_vao = ket_qua["ket_qua"]
    assert ket_qua["ket_qua"]["van_ban"] == "Đã mở lại lô DEMO."
