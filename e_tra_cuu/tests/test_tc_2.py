"""Handler TC-2 thật trên CoreGia + adapter quyền/tệp con chỉ trong tests."""

from copy import deepcopy
import json
from pathlib import Path
import socket

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiDuongTruyen, kiem_phieu
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay
from e_tra_cuu.kiem_dau_vao import CAU_LOI, TAC_VU, bam, json_chuan
from ho_tro_tc_2 import BoDemo, CoreGiaTepCon, GOI, MA
from mo_hinh_contract_tc_1 import kiem_schema_moi

MIB = 1024**2
SCHEMA = json.loads((GOI / "contract/ho_so_tra_cuu.schema.json").read_text(encoding="utf-8"))


def loi(kq, ma):
    assert kq["trang_thai"] == "LOI", kq
    assert kq["loi"]["ma"] == ma, kq
    if ma in CAU_LOI:
        assert kq["loi"]["thong_diep"] == CAU_LOI[ma]
    assert kq["ket_qua"] is None


@pytest.mark.parametrize("tac_vu", sorted(TAC_VU))
def test_nam_tac_vu_hop_le_snapshot_that(tac_vu):
    bo = BoDemo()
    yc = bo.yeu_cau(tac_vu)
    kq = bo.chay(yc)
    assert kq["trang_thai"] == "XONG", kq
    pb = kq["ket_qua"]
    kiem_schema_moi(pb, SCHEMA, SCHEMA)
    h = pb["ho_so_tra_cuu"]
    s = bo.snapshot(kq)
    assert s["tac_vu"] == tac_vu and s["giai_doan"] == "da_nhan"
    assert s["ket_qua"] is None and s["ngu_canh_core"] == yc["ngu_canh_core"]
    assert h["bam_cau_hinh"] == bam(json_chuan(s["cau_hinh"]["gia_tri"]))
    assert s["cau_hinh"]["row_version"] == bo.app.ngan.doc("cau_hinh", {}).row_version
    assert h["tom_tat"]["trang_thai"] is None
    assert all(h["tom_tat"][k] is None for k in ("co_can_cu", "co_mau_thuan", "can_duyet", "nhan"))
    assert set(h) == set(SCHEMA["properties"]["ho_so_tra_cuu"]["required"])
    assert len(json_chuan(pb)) <= 65536
    assert bo.cau_hoi() not in json_chuan(pb).decode("utf-8")
    if "tai_lieu" in s["du_lieu"]:
        assert s["du_lieu"]["tai_lieu"]["van_ban_tai_lieu"] == bo.pb_vb
        assert s["du_lieu"]["tai_lieu"]["van_ban_tai_lieu"]["van_ban_tai_lieu"]["so_trang"] == 0
    if tac_vu == "phan_loai":
        assert s["du_lieu"]["danh_muc"] == bo.danh_muc
        assert h["bam_danh_muc"] == bam(json_chuan(bo.danh_muc))
    else:
        assert h["bam_danh_muc"] is None
    if tac_vu == "soan_tra_loi":
        # QĐ-4: tầng 1 không mở ngược tệp nguồn; nguồn do cửa Core xác thực.
        assert len(bo.core.luot_doc) == 1
        assert s["du_lieu"]["bang_chung"][0]["gia_tri"] == {"so": 1000000, "tien_te": "VND"}
    assert bo.core.so_lan_ghi["ket_qua"] == bo.core.so_lan_ghi["tep"] == 1


def test_manifest_tam_nang_luc_va_stub_khong_xong_gia():
    bo = BoDemo()
    assert kiem_phieu(bo.app.phieu, GOI) == []
    assert len(bo.app.phieu["nang_luc"]) == 8
    assert len(bo.app.phieu["chay_thu_demo"]) == 5
    assert len(bo.app.phieu["loai_du_lieu_rieng"]) == 4
    for n in bo.app.phieu["nang_luc"]:
        assert n["gioi_han"]["tep_toi_da_mib"] == 20 and n["huy_duoc"] is True
        if n["ma"] in {MA, "tra_cuu.cat_doan@1"}:
            continue
        loai = n["nhan"][0]
        ts = {} if "chuan_bi_ai" not in n["ma"] else {
            "tac_vu": "phan_loai", "ma_prompt": "DEMO", "phien_ban_prompt": "1", "prompt": "DEMO"}
        core = CoreGia()
        kq = core.chay_thu(bo.app, n["ma"], {"loai": loai, loai: {}}, ts)
        loi(kq, "CHUA_LAM")
        assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["tep"] == 0


def test_cung_chay_thu_demo_trong_harness():
    from chay_demo_voi_core_gia import chay_demo
    kq = chay_demo()
    assert len(kq) == 5 and all(k["trang_thai"] == "XONG" for k in kq)


def test_cli_sdk_thieu_ngan_dung_chua_cau_hinh():
    # Cổng SDK gốc, không adapter/cấu hình test. Không làm xanh giả.
    core = CoreGia()
    kq = core.chay_thu_demo(chay.app)
    assert len(kq) == 5
    for k in kq:
        loi(k, "CHUA_CAU_HINH")
    assert chay.app.ngan.doc("cau_hinh", {}) is None
    assert core.so_lan_ghi["ket_qua"] == core.so_lan_ghi["tep"] == 0


def test_bam_bytes_chinh_xac_khong_chua_bang_canonical():
    bo = BoDemo()
    yc = bo.yeu_cau()
    b = json_chuan(yc) + b"\n "
    assert bo.chay(yc, b=b)["trang_thai"] == "XONG"
    bo = BoDemo()
    loi(bo.chay(yc, b=b, bam_yeu_cau=bam(json_chuan(yc))), "TC_SAI_NGUON")


@pytest.mark.parametrize("b", [
    b'{"phien_ban":1,"phien_ban":1}', b'{"x":{"a":1,"a":2}}',
    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'{"x":1e999}',
    b'{"x":"\xff"}', b'{"x":"\\ud800"}', b'{"x":"\\udfff"}', b'{',
    b'[' * 1500 + b']' * 1500,
], ids=["khoa-trung", "khoa-trung-long", "nan", "infinity", "am-infinity", "so-overflow",
        "utf8-hong", "surrogate-cao", "surrogate-thap", "json-thieu", "long-qua-sau"])
def test_json_nghiem_truoc_xu_ly_khong_lo_noi_dung(b, capsys):
    bo = BoDemo()
    loi(bo.chay(b=b), "TC_DAU_VAO_KHONG_HOP_LE")
    assert len(bo.core.luot_doc) == 1
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("v", [
    "https://example.invalid/DEMO", "file:///DEMO", "data:text/plain;base64,REVNTw==",
    "C:\\DEMO\\nguon.json", "C:/DEMO/nguon.json", "\\\\DEMO\\nguon.json", "/tmp/DEMO.json", "../DEMO.json",
    "REVNTyBr aG9uZw==", "REVNTyBub2kgZHVuZyBuZ3Vvbg==",
])
def test_url_duong_may_base64_bi_tu_choi(v):
    bo = BoDemo()
    yc = bo.yeu_cau()
    yc["ma_yeu_cau"] = v
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE")
    assert len(bo.core.luot_doc) == 1


@pytest.mark.parametrize("k", ["url", "duong_dan", "base64", "noi_dung_base64", "sql", "code", "da_loc_quyen"])
def test_khong_nhan_kenh_du_lieu_ngoai_va_co_tu_khai(k):
    bo = BoDemo()
    yc = bo.yeu_cau()
    yc["du_lieu"][k] = True
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE")


@pytest.mark.parametrize("sai", ["tham_so_bam", "bam_con", "noi_dung_con", "metadata", "mime", "phien_ban_nguon", "phien_ban_ocr", "bam_goc_ocr"])
def test_sai_bam_metadata_phien_ban_nguon(sai):
    bo = BoDemo()
    yc = bo.yeu_cau()
    ts = {}
    if sai == "tham_so_bam":
        ts["bam_yeu_cau"] = "sha256:" + "0" * 64
    elif sai == "bam_con":
        yc["du_lieu"]["tai_lieu"]["goc"]["bam"] = "sha256:" + "0" * 64
    elif sai == "noi_dung_con":
        ten, mime, b = bo.core._tep[bo.goc["tep"]["tep_id"]]
        bo.core._tep[bo.goc["tep"]["tep_id"]] = (ten, mime, b + b"DEMO")
    elif sai in {"metadata", "mime"}:
        yc["du_lieu"]["tai_lieu"]["goc"]["tep"]["ten" if sai == "metadata" else "mime"] = "doi-DEMO.txt" if sai == "metadata" else "application/pdf"
    elif sai == "phien_ban_nguon":
        yc["du_lieu"]["tai_lieu"]["phien_ban_nguon"] = "2"
    else:
        vb = deepcopy(bo.pb_vb)
        vb["van_ban_tai_lieu"]["phien_ban" if sai == "phien_ban_ocr" else "bam_dau_vao"] = (
            2 if sai == "phien_ban_ocr" else "sha256:" + "0" * 64)
        yc["du_lieu"]["tai_lieu"]["van_ban"] = bo.tai("van-ban-sai-DEMO.json", json_chuan(vb))
    loi(bo.chay(yc, **ts), "TC_SAI_NGUON")
    assert bo.core.so_lan_ghi["tep"] == bo.core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("p", [None, "", "  "])
def test_thieu_phap_nhan_ngu_canh_sdk(p):
    bo = BoDemo()
    loi(bo.chay(phap_nhan=p), "TC_THIEU_NGU_CANH")


@pytest.mark.parametrize("kieu", ["khong_cua", "khong_giay_cap", "co_true", "phap_nhan", "module", "nhom", "nguoi_hoi_id", "ma_pham_vi", "thoi_diem", "tep_con", "quyen_tep_core"])
def test_quyen_va_pham_vi_khong_tin_caller(kieu):
    bo = BoDemo()
    yc = bo.yeu_cau()
    bo.giao(yc)
    cap = bo.core.cua.giay_cap[bo.viec_id]
    if kieu == "khong_cua":
        bo.app.cua_nguon = None
    elif kieu == "khong_giay_cap":
        del bo.core.cua.giay_cap[bo.viec_id]
    elif kieu == "co_true":
        bo.core.cua.giay_cap[bo.viec_id] = True
    elif kieu == "tep_con":
        del cap["tep"][bo.goc["tep"]["tep_id"]]
    elif kieu == "quyen_tep_core":
        bo.core.tep_duoc_mo[bo.viec_id].remove(bo.goc["tep"]["tep_id"])
    else:
        truong = "phap_nhan_id" if kieu == "phap_nhan" else kieu
        cap["ngu_canh_core"][truong] = ["07"] if truong == "nhom" else "DEMO-ngoai-pham-vi"
    bo.core.chay(bo.app)
    loi(bo.core.xem(bo.viec_id), "TC_CHUA_CO_CUA_CORE")
    assert bo.core.so_lan_ghi["tep"] == bo.core.so_lan_ghi["ket_qua"] == 0


def test_json_phap_nhan_khac_ngu_canh_bi_tu_choi():
    bo = BoDemo()
    yc = bo.yeu_cau()
    yc["ngu_canh_core"]["phap_nhan_id"] = "DEMO-Q"
    loi(bo.chay(yc), "TC_CHUA_CO_CUA_CORE")


@pytest.mark.parametrize("truong", ["phap_nhan_id", "module", "nhom", "nguoi_hoi_id", "ma_pham_vi", "thoi_diem"])
def test_thieu_ngu_canh_trong_yeu_cau(truong):
    bo = BoDemo()
    yc = bo.yeu_cau()
    del yc["ngu_canh_core"][truong]
    loi(bo.chay(yc), "TC_THIEU_NGU_CANH")


@pytest.mark.parametrize("duong,gia_tri", [
    (("phien_ban",), True), (("tac_vu",), []), (("du_lieu",), []),
    (("du_lieu", "metadata_core", "con_hieu_luc"), 1),
    (("du_lieu", "tai_lieu", "goc", "tep", "kich_thuoc"), True),
])
def test_sai_kieu_khong_traceback_du_lieu(duong, gia_tri, capsys):
    bo = BoDemo()
    yc = bo.yeu_cau()
    doi = yc
    for k in duong[:-1]:
        doi = doi[k]
    doi[duong[-1]] = gia_tri
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE")
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("ban_va", [
    {"phien_ban": 2}, {"ngan_sach": {"so_ham_toi_da": 101}},
    {"quy_tac_nhom": {"tep_id": "DEMO", "bam": "\ud800"}},
])
def test_cau_hinh_sai_qua_handler_that_khong_lo_log(ban_va, capsys):
    bo = BoDemo()
    # Surrogate không thể vào NganBoNho: mô phỏng phản hồi Core hỏng riêng.
    if "quy_tac_nhom" in ban_va:
        from types import SimpleNamespace

        class NganHong:
            def doc(self, bang, khoa):
                return SimpleNamespace(gia_tri={**bo.cau_hinh, **ban_va}, row_version=1)

        bo.app.ngan = NganHong()
    else:
        ban = bo.app.ngan.doc("cau_hinh", {})
        with bo.app.ngan.lo() as lo:
            lo.sua("cau_hinh", {}, ban_va, row_version=ban.row_version)
    loi(bo.chay(), "CAU_HINH_KHONG_HOP_LE")
    assert bo.core.luot_doc == [] and capsys.readouterr().err == ""


def test_bam_hex_hoa_duoc_chap_nhan():
    bo = BoDemo()
    yc = bo.yeu_cau()
    yc["du_lieu"]["tai_lieu"]["goc"]["bam"] = "sha256:" + bo.goc["bam"][7:].upper()
    yc["du_lieu"]["tai_lieu"]["van_ban"]["bam"] = "sha256:" + bo.vb["bam"][7:].upper()
    b = json_chuan(yc)
    assert bo.chay(yc, b=b, bam_yeu_cau="sha256:" + bam(b)[7:].upper())["trang_thai"] == "XONG"


def test_nguon_cap_khac_phien_ban_bi_tu_choi():
    bo = BoDemo()
    bo.nguon_duoc_cap[bo.nguon["ma_nguon"]]["phien_ban_nguon"] = "2"
    loi(bo.chay(), "TC_SAI_NGUON")


def test_khong_cap_nguon_thi_khong_mo_tep_con():
    bo = BoDemo()
    bo.nguon_duoc_cap = {}
    loi(bo.chay(), "TC_CHUA_CO_CUA_CORE")
    assert len(bo.core.luot_doc) == 1


@pytest.mark.parametrize("kieu", ["khoa-trung", "utf8-hong", "nan"])
def test_json_con_cung_bi_kiem_nghiem(kieu):
    bo = BoDemo()
    yc = bo.yeu_cau("phan_loai")
    b = {"khoa-trung": b'{"nhom":[],"nhom":[]}', "utf8-hong": b'{"DEMO":"\xff"}', "nan": b'{"DEMO":NaN}'}[kieu]
    yc["du_lieu"]["danh_muc"] = bo.tai("danh-muc-hong-DEMO.json", b)
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE")


@pytest.mark.parametrize("tang", [2, 3])
def test_soan_nhan_bang_chung_doan_tang_hai_ba(tang):
    bo = BoDemo()
    yc = bo.yeu_cau("soan_tra_loi")
    yc["du_lieu"].update(tang=tang, nguon=[bo.tai_lieu], bang_chung=[bo.doan()])
    kq = bo.chay(yc)
    assert kq["trang_thai"] == "XONG"
    assert bo.snapshot(kq)["du_lieu"]["tang"] == tang
    assert kq["ket_qua"]["ho_so_tra_cuu"]["tom_tat"]["tang"] == tang


def test_tang_mot_nguon_descriptor_khong_doc_nguoc():
    bo = BoDemo()
    yc = bo.yeu_cau("soan_tra_loi")
    yc["du_lieu"]["nguon"] = [bo.nguon]
    assert bo.chay(yc)["trang_thai"] == "XONG"
    assert len(bo.core.luot_doc) == 1


@pytest.mark.parametrize("kieu", ["ma-trung", "phien-ban", "offset", "bam", "diem-bool"])
def test_ung_vien_sai_quan_he_nguon(kieu):
    bo = BoDemo()
    yc = bo.yeu_cau("xep_hang_lai")
    u = yc["du_lieu"]["ung_vien"][0]
    if kieu == "ma-trung":
        yc["du_lieu"]["ung_vien"].append(deepcopy(u))
    elif kieu == "phien-ban":
        u["phien_ban_nguon"] = "2"
    elif kieu == "offset":
        u["ket_thuc"] -= 1
    elif kieu == "bam":
        u["bam_van_ban"] = "sha256:" + "0" * 64
    else:
        u["diem_tim_kiem"] = True
    loi(bo.chay(yc), "TC_DAU_VAO_KHONG_HOP_LE" if kieu == "diem-bool" else "TC_SAI_NGUON")


@pytest.mark.parametrize("ten,tran", [("ho_so_toi_da_byte", 100), ("tep_toi_da_byte", 1500)])
def test_tran_dau_ra_khong_upload_roi_bao_thanh_cong(ten, tran):
    bo = BoDemo()
    ban = bo.app.ngan.doc("cau_hinh", {})
    with bo.app.ngan.lo() as lo:
        lo.sua("cau_hinh", {}, {"ngan_sach": {ten: tran}}, row_version=ban.row_version)
    loi(bo.chay(), "TC_QUA_GIOI_HAN")
    assert bo.core.so_lan_ghi["tep"] == bo.core.so_lan_ghi["ket_qua"] == 0


def test_loi_bat_ngo_cua_core_khong_lo_du_lieu_vao_traceback(monkeypatch, capsys):
    bo = BoDemo()

    def loi_core(viec_id):
        raise RuntimeError(bo.cau_hoi() + " " + bo.van_ban)

    monkeypatch.setattr(bo.core.cua, "doc_quyen", loi_core)
    loi(bo.chay(), "ENGINE_LOI_XU_LY")
    assert capsys.readouterr().err == ""
    assert bo.core.so_lan_ghi["ket_qua"] == 0


def test_chua_ro_tu_cua_nguon_khong_doi_thanh_xong(monkeypatch):
    bo = BoDemo()

    def chua_ro(viec_id):
        raise ChuaRo("DEMO-tuong-quan-1")

    monkeypatch.setattr(bo.core.cua, "doc_quyen", chua_ro)
    kq = bo.chay()
    assert kq["trang_thai"] == "CHUA_RO" and kq["ma_tuong_quan"] == "DEMO-tuong-quan-1"
    assert kq["ket_qua"] is None and bo.core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("so_byte,dat", [(MIB, True), (MIB + 1, False)])
def test_json_chinh_bien_mot_mib_truoc_parse(monkeypatch, so_byte, dat):
    bo = BoDemo()
    yc = bo.yeu_cau()
    b = json_chuan(yc)
    b += b" " * (so_byte - len(b))
    if not dat:
        import e_tra_cuu.kiem_dau_vao as kiem
        monkeypatch.setattr(kiem, "doc_json", lambda b: pytest.fail("Quá trần phải từ chối trước parse."))
    kq = bo.chay(yc, b=b)
    if dat:
        assert kq["trang_thai"] == "XONG"
    else:
        loi(kq, "TC_QUA_GIOI_HAN")


@pytest.mark.parametrize("so_byte", [MIB + 1, 20 * MIB])
def test_tep_con_lon_hon_mot_mib_den_hai_muoi_mib(so_byte):
    bo = BoDemo(noi_dung_goc=b"DEMO" + b"x" * (so_byte - 4))
    kq = bo.chay()
    assert kq["trang_thai"] == "XONG", kq
    assert any(n == so_byte for _, _, n in bo.core.luot_doc)


def test_json_ocr_con_hon_mot_mib_khong_bi_tran_chinh():
    bo = BoDemo(van_ban="DEMO " + "ự" * 400000)
    assert MIB < bo.vb["tep"]["kich_thuoc"] <= 20 * MIB
    assert bo.chay()["trang_thai"] == "XONG"


def test_tep_con_qua_hai_muoi_mib_khong_cat():
    bo = BoDemo(noi_dung_goc=b"DEMO" + b"x" * (20 * MIB - 3))
    loi(bo.chay(), "TC_QUA_GIOI_HAN")
    assert not any(t == bo.goc["tep"]["tep_id"] for _, t, _ in bo.core.luot_doc)


def test_tong_tep_that_qua_sau_muoi_tu_mib():
    bo = BoDemo(noi_dung_goc=b"DEMO" + b"x" * (17 * MIB - 4))
    yc = bo.yeu_cau("xep_hang_lai")
    nguon = [yc["du_lieu"]["nguon"][0]]
    for i in range(2, 5):
        goc = bo.tai(f"nguon-{i}-DEMO.txt", bo.core.doc_tep(bo.goc["tep"]["tep_id"]), "text/plain")
        n = {"ma_nguon": f"DEMO-NGUON-{i}", "phien_ban_nguon": "1", "goc": goc, "van_ban": bo.vb}
        nguon.append(n)
        bo.nguon_duoc_cap[n["ma_nguon"]] = {**bo.nguon, "ma_nguon": n["ma_nguon"], "tep_id": goc["tep"]["tep_id"]}
    yc["du_lieu"]["nguon"] = nguon
    assert sum(n["goc"]["tep"]["kich_thuoc"] for n in nguon) > 64 * MIB
    loi(bo.chay(yc), "TC_QUA_GIOI_HAN")
    assert bo.core.so_lan_ghi["tep"] == bo.core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("van_ban,ma_loi", [("", "TC_SAI_NGUON"), (" \n", "TC_SAI_NGUON"), ("DEMO " + "x" * 500000, "TC_QUA_GIOI_HAN")],
                         ids=["rong", "chi-khoang-trang", "qua-tran"])
def test_ocr_rong_va_van_ban_qua_tran(van_ban, ma_loi):
    bo = BoDemo(van_ban=van_ban)
    loi(bo.chay(), ma_loi)


def test_qua_sau_muoi_trang():
    bo = BoDemo()
    vb = deepcopy(bo.pb_vb)
    vb["van_ban_tai_lieu"]["so_trang"] = 61
    yc = bo.yeu_cau()
    yc["du_lieu"]["tai_lieu"]["van_ban"] = bo.tai("61-trang-DEMO.json", json_chuan(vb))
    loi(bo.chay(yc), "TC_QUA_GIOI_HAN")


@pytest.mark.parametrize("kieu", ["cau_hoi", "ham", "danh_muc", "ung_vien"])
def test_tran_cau_hoi_ham_danh_muc_ung_vien(kieu):
    bo = BoDemo()
    if kieu in {"cau_hoi", "ham"}:
        yc = bo.yeu_cau("phan_tich_cau_hoi")
        if kieu == "cau_hoi":
            yc["du_lieu"]["cau_hoi"] = "DEMO " + "x" * 4000
        else:
            yc["du_lieu"]["ham"] *= 101
    elif kieu == "danh_muc":
        yc = bo.yeu_cau("phan_loai")
        dm = deepcopy(bo.danh_muc)
        dm["doi_tuong"] = [{"ma": "DEMO-" + str(i), "ten": "DEMO"} for i in range(1001)]
        yc["du_lieu"]["danh_muc"] = bo.tai("danh-muc-lon-DEMO.json", json_chuan(dm))
    else:
        yc = bo.yeu_cau("xep_hang_lai")
        yc["du_lieu"]["ung_vien"] *= 51
    loi(bo.chay(yc), "TC_QUA_GIOI_HAN")


def test_chup_config_va_version_chi_mot_lan_doc():
    bo = BoDemo()
    ngan = bo.app.ngan
    truoc = ngan.doc("cau_hinh", {})
    cau_hinh_cu = chay.yeu_cau_cau_hinh(ngan)

    class DoiCauHinhSauDoc:
        dem = 0

        def doc(self, bang, khoa):
            self.dem += 1
            ban = ngan.doc(bang, khoa)
            with ngan.lo() as lo:
                lo.sua(bang, khoa, {"cat_doan": {"do_dai_muc_tieu": 300}}, row_version=ban.row_version)
            return ban

    bo.app.ngan = DoiCauHinhSauDoc()
    kq = bo.chay()
    assert kq["trang_thai"] == "XONG"
    s = bo.snapshot(kq)
    assert bo.app.ngan.dem == 1
    assert s["cau_hinh"] == {"gia_tri": cau_hinh_cu, "row_version": truoc.row_version}
    assert ngan.doc("cau_hinh", {}).row_version != truoc.row_version


@pytest.mark.parametrize("sau_tep", ["chinh", "goc", "ocr"])
def test_huy_trong_khi_doc_khong_upload_khong_nop(sau_tep):
    bo = BoDemo()
    bo.giao()
    tep_id = {"chinh": bo.refs[-1]["tep"]["tep_id"], "goc": bo.goc["tep"]["tep_id"], "ocr": bo.vb["tep"]["tep_id"]}[sau_tep]
    bo.core.sau_doc = lambda viec_id, tep: bo.core.huy(viec_id) if tep == tep_id else None
    bo.core.chay(bo.app)
    assert bo.core.xem(bo.viec_id)["trang_thai"] == "HUY"
    assert bo.core.so_lan_ghi["tep"] == bo.core.so_lan_ghi["ket_qua"] == 0


@pytest.mark.parametrize("cua", ["_tien_do", "_tai_tep_ra", "_nop_ket_qua"])
def test_mat_lease_khong_ket_thuc_khong_xong_gia(cua, monkeypatch):
    bo = BoDemo()
    bo.giao()

    def mat_lease(ma, viec_id, *args, **kwargs):
        bo.core._viec[viec_id]["trang_thai"] = "CHO"
        raise LoiDuongTruyen("MAT_LEASE", http_status=409)

    monkeypatch.setattr(bo.core, cua, mat_lease)
    bo.core.chay(bo.app)
    assert bo.core.xem(bo.viec_id)["trang_thai"] == "CHO"
    assert bo.core.so_lan_ghi["ket_qua"] == bo.core.so_lan_ghi["ket_thuc"] == 0


@pytest.mark.parametrize("thao_tac", ["tep", "ket_qua", "ket_thuc"])
@pytest.mark.parametrize("so_lan", [1, 3])
def test_mat_ack_gui_lai_cung_khoa_chi_ghi_mot(thao_tac, so_lan):
    bo = BoDemo()
    bo.core.gay_mat_xac_nhan(thao_tac, so_lan)
    kq = bo.chay()
    assert kq["trang_thai"] == "XONG"
    for ten in ("tep", "ket_qua", "ket_thuc"):
        assert bo.core.so_lan_ghi[ten] == 1
    keys = [k[-1] for k in bo.core.nhat_ky if k[0] == thao_tac]
    assert len(keys) == so_lan + 1 and len(set(keys)) == 1


@pytest.mark.parametrize("thao_tac", ["tep", "ket_qua"])
def test_mat_ack_het_so_lan_khong_tu_bao_xong(thao_tac):
    bo = BoDemo()
    bo.core.gay_mat_xac_nhan(thao_tac, 4)
    kq = bo.chay()
    assert kq["trang_thai"] != "XONG"
    assert bo.core.so_lan_ghi[thao_tac] == 1
    if thao_tac == "tep":
        assert bo.core.so_lan_ghi["ket_qua"] == 0


def test_khong_ghi_noi_dung_vao_log_va_khong_ghi_tep(monkeypatch, capsys):
    bo = BoDemo()
    bo.giao(bo.yeu_cau("soan_tra_loi"))
    dem_mang = 0

    def cam_mang(*args, **kwargs):
        nonlocal dem_mang
        dem_mang += 1
        raise AssertionError("Không được gọi mạng.")

    def cam_ghi(*args, **kwargs):
        raise AssertionError("Runtime không được ghi tệp.")

    monkeypatch.setattr(socket.socket, "connect", cam_mang)
    monkeypatch.setattr(socket, "create_connection", cam_mang)
    monkeypatch.setattr(Path, "write_bytes", cam_ghi)
    monkeypatch.setattr(Path, "write_text", cam_ghi)
    bo.core.chay(bo.app)
    assert bo.core.xem(bo.viec_id)["trang_thai"] == "XONG"
    assert dem_mang == 0
    log = capsys.readouterr()
    assert bo.cau_hoi() not in log.err + log.out and bo.van_ban not in log.err + log.out
    assert all(bo.cau_hoi() not in cau for _, cau in bo.core.xem(bo.viec_id)["tien_do"])
