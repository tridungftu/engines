"""TC-11: chỉ CoreGia/adapter giả; cấm mạng bởi conftest, không --that thật."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil

import pytest
from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from ho_tro_tc_2 import GOI
from ho_tro_tc_10 import chay_bo_do

CONG_CU = GOI.parents[1] / "cong-cu"
spec = importlib.util.spec_from_file_location("thu_tra_cuu_that_tc11", CONG_CU / "thu_tra_cuu_that.py")
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)


def ghim():
    pin = {"phien_ban": "DEMO-1", "bam": tc.bam(b"DEMO")}
    return {"nhan": "DEMO", "phien_ban": 1, "engine": deepcopy(pin), "danh_muc": deepcopy(pin),
            "cau_hinh": deepcopy(pin), "prompt": {k: {**pin, "ma": "DEMO-" + k} for k in tc.TAC_VU if k != "cat_doan"}}


@pytest.fixture(scope="module")
def bo():
    return tc.nap_bo()


@pytest.fixture(scope="module")
def quan_sat_core_gia():
    report, qs = chay_bo_do()
    assert report["so_ca_dat"] == 38
    return {k: deepcopy(v["xuat"]) for k, v in qs.items()}


class AdapterGia:
    la_gia = True

    def __init__(self, outputs):
        self.outputs = outputs
        self.gui = []
        self.nhan = []
        self.reports = []
        h = tc.bam(b"DEMO-kiem")
        self.env = {k: {"co_that": True, "bam_kiem": h} for k in ("core", "ai", "ocr", "tx", "embedding")}
        self.env.update(ghim=ghim(), chi_local=True, models=[{"vai_tro": k, "id": "DEMO-ID-" + str(i),
            "runtime": "DEMO-runtime", "phien_ban": "DEMO-v1", "context_hieu_dung": 8192,
            "bam_phat_hien": h, "local": True} for i, k in enumerate(tc.VAI_TRO)])
        self.env["embedding"].update(id="DEMO-khong-doan-tu-ten", runtime="DEMO-runtime",
            phien_ban="DEMO-v1", context_hieu_dung=4096, bam_phat_hien=h, local=True,
            lead_chon=True, ho_tro_nhung=True, bam_kiem_tieng_viet=h)

    def kiem_moi_truong(self, pin):
        return deepcopy(self.env)

    def chuan_bi(self, ca, model, pin):
        return {"nguon_dem": "tokenizer_runtime", "day_du_khung": True, "model_id": model["id"],
                "token_vao": 100, "token_ra_du_phong": 200, "bam_noi_dung_gui": tc.bam(b"DEMO-prompt"),
                "ma_tuong_quan": "DEMO-viec-" + str(len(self.gui)), "goi_ai": ca.get("ai", ca["tac_vu"] != "cat_doan")}

    def gui_viec(self, ca, model, plan):
        assert "local" not in ca and "dap_an" not in ca
        self.gui.append((deepcopy(ca), deepcopy(model), deepcopy(plan)))
        return {"ma_tuong_quan": plan["ma_tuong_quan"], "http": 200, "trang_thai": "DA_NHAN"}

    def nhan_ket_qua(self, ticket):
        self.nhan.append(deepcopy(ticket))
        ca, m, p = self.gui[-1]
        return {"trang_thai": "XONG", "model_id": m["id"], "local": True,
                "model_phien_ban": m["phien_ban"], "runtime": m["runtime"], "ghim": ghim(),
                "bam_noi_dung_gui": p["bam_noi_dung_gui"], "cat_ngam": False, "batch": False,
                "dau_ra": deepcopy(self.outputs[ca["ma"]]), "so_do": {}}

    def bien_ban_core(self):
        return {}

    def giu_bao_cao(self, report):
        self.reports.append(deepcopy(report))


def test_chay_kho_kiem_bam_khong_adapter_khong_ghi(bo, monkeypatch, capsys):
    def cam(*a, **kw):
        raise AssertionError("Không tạo adapter hoặc ghi tệp mặc định.")
    monkeypatch.setattr(tc, "CoreThat", cam)
    monkeypatch.setattr(tc, "ghi_bao_cao", cam)
    assert tc.main([]) == 0
    assert "CHẠY KHÔ" in capsys.readouterr().out
    r, code = tc.chay(bo)
    assert code == 0 and r["trang_thai"] == "chay_kho"
    assert r["so_viec_gui"] == r["so_luot_cloud"] == 0
    assert r["model_duoc_chot"] is r["nguong_duoc_chot"] is r["accuracy_model_that"] is None
    for v in r["chi_so"].values():
        assert v["tu_so"] == v["mau_so"] == 0 and v["ty_le"] is None and v["ly_do"]
    assert r["chi_so"]["tra_loi_dung"]["chua_do"] == 12
    assert r["chi_so"]["phan_loai_dung"]["chua_do"] == 20
    assert "local" not in bo["corpus"]["kich_ban"][0]


@pytest.mark.parametrize("args", [["--that"], ["--that", "--core", "https://core.invalid"],
    ["--bo-demo", "DEMO"], ["--ghim", "DEMO"], ["--key", "DEMO-BI-MAT"],
    ["--khoa=DEMO-BI-MAT"], ["--tha"], ["--bao-cao", "DEMO.json"]])
def test_parse_thieu_loi_an_toan(args, capsys):
    assert tc.main(args) == 2
    text = capsys.readouterr()
    assert "DEMO-BI-MAT" not in text.err and "Traceback" not in text.err


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e999}',
    b'{"x":"\\ud800"}', b'\xff', b'{"x":'])
def test_json_nghiem(raw):
    with pytest.raises(LoiNghiepVu):
        tc.json_nghiem(raw)


def test_ghim_chi_nhan_bam_phien_ban_khong_gia_tri_cau_hinh(tmp_path):
    path = tmp_path / "ghim-DEMO.json"
    raw = tc.json_bytes(ghim())
    path.write_bytes(raw)
    assert tc.nap_ghim(path, tc.bam(raw)) == ghim()
    with pytest.raises(LoiNghiepVu):
        tc.nap_ghim(path, tc.bam(b"khac"))
    value = ghim()
    value["cau_hinh"]["url"] = "https://khong-duoc-doc.invalid"
    raw = tc.json_bytes(value)
    path.write_bytes(raw)
    with pytest.raises(LoiNghiepVu):
        tc.nap_ghim(path, tc.bam(raw))


def test_pin_nguon_dap_an_khong_tu_chap_nhan_sua(tmp_path):
    root = tmp_path / "DEMO"
    shutil.copytree(tc.DEMO, root)
    tc.nap_bo(root, tc.BAM_BO_MAC_DINH)
    (root / "vay-DEMO.txt").write_text("DEMO thay đổi", encoding="utf-8")
    with pytest.raises(LoiNghiepVu) as exc:
        tc.nap_bo(root, tc.BAM_BO_MAC_DINH)
    assert exc.value.ma == "TC_SAI_NGUON"
    with pytest.raises(LoiNghiepVu):
        tc.nap_bo(root, tc.bam(b"sai-pin"))


@pytest.mark.parametrize("ten", ["../ngoai-DEMO.txt", "C:/ngoai-DEMO.txt", ".env", "cau_hinh.that.toml"])
def test_ten_nguon_khong_thoat_pham_vi(tmp_path, ten):
    (tmp_path / "bam-DEMO.json").write_bytes(tc.json_bytes({ten: tc.bam(b"DEMO"), "khac-DEMO.txt": tc.bam(b"DEMO")}))
    checksum = tc.bam((tmp_path / "bam-DEMO.json").read_bytes())
    with pytest.raises(LoiNghiepVu):
        tc.nap_bo(tmp_path, checksum)


@pytest.mark.parametrize("url", ["https://core.invalid", "http://127.0.0.1:8000", "http://[::1]:8000", "http://localhost"])
def test_url_hop_le_khong_noi_mang(url):
    assert tc.kiem_url(url)


@pytest.mark.parametrize("url", ["http://core.invalid", "https://key@core.invalid", "https://core.invalid/?k=DEMO",
    "file:///DEMO", "https://core.invalid:xx", "https://core.invalid/api", "https://core.invalid/#key", "https://core.invalid\n"])
def test_url_sai(url):
    with pytest.raises(LoiNghiepVu):
        tc.kiem_url(url)


def test_core_that_thieu_cua_khong_nhap_khoa_khong_mang(bo):
    # Gọi seam chốt thiếu cửa, KHÔNG chạy CLI --that hoặc hệ thống thật.
    with pytest.raises(LoiNghiepVu) as ex:
        tc.chay(bo, ghim(), tc.CoreThat("https://core.invalid"))
    assert ex.value.ma == "TC_CHUA_CO_MOI_TRUONG_THU"
    assert ex.value.thong_diep == tc.CAU_MOI_TRUONG
    assert ex.value.bao_cao["so_viec_gui"] == 0


@pytest.mark.parametrize("dich_vu", ["core", "ai", "ocr", "tx", "embedding"])
def test_thieu_dich_vu_chan_truoc_gui(bo, dich_vu):
    a = AdapterGia({})
    a.env[dich_vu]["co_that"] = False
    with pytest.raises(LoiNghiepVu) as e:
        tc.chay(bo, ghim(), a)
    assert e.value.ma == "TC_CHUA_CO_MOI_TRUONG_THU" and not a.gui


@pytest.mark.parametrize("sua", ["embedding_ten", "embedding_chua_chon", "embedding_chua_kiem_viet", "runtime_thieu",
    "id_trung", "context_thieu", "ghim_khac", "cloud", "catalog_thieu", "version_thieu"])
def test_khong_doan_model_tu_ten_va_khong_nhan_model_tu_khai(bo, sua):
    a = AdapterGia({})
    if sua == "embedding_ten":
        a.env["embedding"].update(id="Vietnamese-embedding", ho_tro_nhung=False)
    elif sua == "embedding_chua_chon": a.env["embedding"]["lead_chon"] = False
    elif sua == "embedding_chua_kiem_viet": a.env["embedding"]["bam_kiem_tieng_viet"] = None
    elif sua == "runtime_thieu": a.env["models"][0]["runtime"] = None
    elif sua == "id_trung": a.env["models"][0]["id"] = a.env["models"][1]["id"]
    elif sua == "context_thieu": a.env["models"][0]["context_hieu_dung"] = None
    elif sua == "ghim_khac": a.env["ghim"] = None
    elif sua == "cloud": a.env["chi_local"] = False
    elif sua == "version_thieu": a.env["models"][0]["phien_ban"] = None
    else: a.env["models"] = []
    with pytest.raises(LoiNghiepVu):
        tc.chay(bo, ghim(), a)
    assert not a.gui


def test_do_bon_ty_le_bang_ket_qua_core_gia_thieu_so_khong_thanh_0(bo, quan_sat_core_gia):
    a = AdapterGia(quan_sat_core_gia)
    r, code = tc.chay(bo, ghim(), a)
    assert code == 2 and len(a.gui) == 38 * 3 and len(a.reports) == 1
    assert r["chi_so"] is r["chi_tiet"] is None
    for m in r["models"]:
        assert {k: (v["tu_so"], v["mau_so"]) for k, v in m["chi_so"].items()} == {
            "tra_loi_dung": (12, 12), "trich_dan_dung": (12, 12), "tu_choi_dung": (6, 6), "phan_loai_dung": (20, 20)}
        assert m["chi_tiet"]["cat_doan_vi_tri"]["ty_le"] is None
        assert m["chi_tiet"]["tien"]["tu_so"] > 0
    for row in r["cac_ca"]:
        assert row["token_vao"] is row["token_ra"] is row["thoi_gian_runtime_giay"] is None
        assert row["ly_do_thieu"]["token_vao"] and row["nguon_so_do"] == "adapter_gia"
        assert row["thoi_gian_cong_cu_giay"] >= 0
    assert all(v["trang_thai"] == "chua_kiem" for v in r["kiem_core"].values())
    assert r["core_that"] == "chua_kiem" and r["accuracy_model_that"] is None
    assert r["so_luot_cloud"] == 0 and r["ket_luan_phep_do_that"] == "CHỜ ANH TỰ CHẠY"


@pytest.mark.parametrize("thay", ["gia_tri", "thuc_the", "tien_te", "ngay", "offset", "nguon", "version"])
def test_cham_sai_khong_bao_dat(bo, quan_sat_core_gia, thay):
    g = bo["dap_an"]["TL-Python-A"]
    out = deepcopy(quan_sat_core_gia["TL-Python-A"])
    k = out["ket_qua"]["khang_dinh"][0]
    if thay == "gia_tri": k["gia_tri"]["so"] = 99
    elif thay == "thuc_the": k["thuc_the"]["ma"] = "DEMO-VAY-B"
    elif thay == "tien_te": k["gia_tri"]["tien_te"] = "USD"
    elif thay == "ngay": out["ket_qua"]["khang_dinh"][1]["gia_tri"] = "2026-10-31"
    elif thay == "offset": k["can_cu"][0]["bat_dau"] += 1
    elif thay == "nguon": k["can_cu"][0]["nguon"]["ma_nguon"] = "DEMO-khac"
    else: k["can_cu"][0]["nguon"]["phien_ban_nguon"] = "DEMO-2"
    c = tc.cham(g, out)
    assert not c["trich_dan_dung" if thay in {"offset", "nguon", "version"} else "tra_loi_dung"]


@pytest.mark.parametrize("tac,chi", [("cat_doan", "cat_doan_vi_tri"), ("phan_tich_cau_hoi", "cau_hoi_ham"), ("xep_hang_lai", "xep_hang")])
def test_cham_ba_tac_vu_gim_gia_tri_vi_tri_ham_hoan_vi(tac, chi):
    # Không có đáp án supplement thì chưa đo; không mặc định đúng.
    assert tc.cham_chi_tiet({}, {}, tac) == {}
    gold = {"du_lieu": {"doan": [{"a": 0, "b": 12}], "ham": {"ma": "DEMO-doc", "tham_so": {"vay": "DEMO-A"}}, "thu_tu": ["DEMO-1", "DEMO-2"]}}
    assert tc.cham_chi_tiet(gold, {"ket_qua": gold["du_lieu"]}, tac) == {chi: True}
    wrong = deepcopy(gold["du_lieu"])
    wrong["ham"]["tham_so"]["vay"] = "DEMO-B"
    assert tc.cham_chi_tiet(gold, {"ket_qua": wrong}, tac) == {chi: False}


def test_context_qua_tran_khong_gui_khong_cat_khong_batch(bo):
    bo = deepcopy(bo)
    bo["corpus"]["kich_ban"] = [c for c in bo["corpus"]["kich_ban"] if c.get("ai", True)]
    bo["dap_an"] = {c["ma"]: bo["dap_an"][c["ma"]] for c in bo["corpus"]["kich_ban"]}
    a = AdapterGia({})
    prepare = a.chuan_bi
    def qua(c, m, g):
        return {**prepare(c, m, g), "token_vao": m["context_hieu_dung"]}
    a.chuan_bi = qua
    r, code = tc.chay(bo, ghim(), a)
    assert code == 2 and not a.gui and r["so_viec_gui"] == 0
    assert all(v["trang_thai"] == "tu_choi_context" for v in r["cac_ca"])
    assert r["models"][0]["chi_so"]["tra_loi_dung"]["ty_le"] is None


@pytest.mark.parametrize("patch", [{"nguon_dem": "ky_tu_chia_4"}, {"day_du_khung": False}, {"model_id": "DEMO-khac"},
    {"token_vao": None}, {"token_vao": True}, {"token_ra_du_phong": 0}])
def test_khong_dung_uoc_luong_ky_tu_4_de_cho_gui(bo, patch):
    a = AdapterGia({})
    prepare = a.chuan_bi
    a.chuan_bi = lambda c, m, g: {**prepare(c, m, g), **patch}
    with pytest.raises(LoiNghiepVu):
        tc.chay(bo, ghim(), a)
    assert not a.gui


@pytest.mark.parametrize("luc", ["gui_timeout", "nhan_timeout", "202", "chua_ro", "ticket_hong"])
def test_chua_ro_khong_gui_lai_mu(bo, luc):
    a = AdapterGia({})
    gui = a.gui_viec
    def do_gui(c, m, p):
        t = gui(c, m, p)
        if luc == "gui_timeout": raise TimeoutError("DEMO-khoa-khong-log")
        if luc == "202": t["http"] = 202
        if luc == "ticket_hong": return {}
        return t
    def nhan(t):
        if luc == "nhan_timeout": raise TimeoutError("DEMO-khoa-khong-log")
        return {"trang_thai": "CHUA_RO"}
    a.gui_viec, a.nhan_ket_qua = do_gui, nhan
    with pytest.raises(ChuaRo) as ex:
        tc.chay(bo, ghim(), a)
    assert ex.value.ma_tuong_quan == "DEMO-viec-0" and len(a.gui) == 1
    r = ex.value.bao_cao
    assert r["trang_thai"] == "chua_ro" and r["so_viec_gui"] == 1
    assert "ma_tuong_quan" not in r and r["bam_ma_tuong_quan"] == tc.bam(b"DEMO-viec-0")
    assert r["models"][0]["chi_so"]["phan_loai_dung"]["tu_so"] == 0


@pytest.mark.parametrize("luc", ["truoc", "sau_gui"])
def test_huy_khong_gui_tiep(bo, luc):
    a = AdapterGia({})
    def huy():
        if luc == "truoc" or a.gui: raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt) as ex:
        tc.chay(bo, ghim(), a, kiem_huy=huy)
    assert ex.value.bao_cao["trang_thai"] == "huy" and len(a.gui) == int(luc == "sau_gui")


@pytest.mark.parametrize("val", [None, False, -1, float("nan"), float("inf"), "100", 10**30])
def test_so_do_thieu_sai_la_null_co_ly_do(val):
    r = tc.so_do_runtime({k: val for k in tc.SO_DO})
    assert all(r[k] is None and r["ly_do_thieu"][k] for k in tc.SO_DO)


def test_runtime_token_so_dem_0_la_so_do_khong_null():
    r = tc.so_do_runtime({"nguon": "runtime_qua_core", **{k: 8192 if k == "context_hieu_dung" else 0 for k in tc.SO_DO}})
    assert not r["ly_do_thieu"] and r["token_vao"] == r["token_ra"] == 0


def test_so_uoc_luong_khong_bien_thanh_token_runtime():
    r = tc.so_do_runtime({"nguon": "ky_tu_chia_4", "token_vao": 123, "token_ra": 456})
    assert r["token_vao"] is r["token_ra"] is None


@pytest.mark.parametrize("sai", ["model_id", "model_phien_ban", "runtime", "local", "ghim", "bam_noi_dung_gui", "cat_ngam", "batch"])
def test_ket_qua_khac_model_ghim_cloud_cat_batch_bi_chan(bo, quan_sat_core_gia, sai):
    a = AdapterGia(quan_sat_core_gia)
    nhan = a.nhan_ket_qua
    def sua(t):
        return {**nhan(t), sai: "DEMO-sai"}
    a.nhan_ket_qua = sua
    with pytest.raises(LoiNghiepVu) as ex:
        tc.chay(bo, ghim(), a)
    assert ex.value.ma == "TC_CHUA_CO_MOI_TRUONG_THU" and len(a.gui) == 1


def test_loi_adapter_khong_phan_chieu_thong_diep_bi_mat(bo):
    a = AdapterGia({})
    def loi_ngoai(_):
        raise LoiNghiepVu("DEMO", "DEMO-BI-MAT")
    a.kiem_moi_truong = loi_ngoai
    with pytest.raises(LoiNghiepVu) as ex:
        tc.chay(bo, ghim(), a)
    assert "DEMO-BI-MAT" not in ex.value.thong_diep


def test_bien_ban_core_thieu_cua_tai_rieng_khong_tinh_dat(bo):
    r = tc.bao_cao_moi(bo)
    pin = tc.bam(b"DEMO-bien-ban")
    tc.nhan_bien_ban_core(r, {"postgresql": {"trang_thai": "dat", "bam_bien_ban": pin},
        "pgvector": {"trang_thai": "dat"}, "tai_20_dong_thoi": {"trang_thai": "dat", "bam_bien_ban": pin}}, gia=False)
    assert r["kiem_core"]["postgresql"]["trang_thai"] == "dat"
    assert r["kiem_core"]["pgvector"]["trang_thai"] == "chua_kiem"
    assert r["kiem_core"]["tai_20_dong_thoi"]["trang_thai"] == "chua_kiem"
    tc.nhan_bien_ban_core(r, {"tai_20_dong_thoi": {"trang_thai": "dat", "bam_bien_ban": pin,
        "bai_tai_rieng": True, "so_nguoi": 150, "dong_thoi": 20}}, gia=True)
    assert r["kiem_core"]["tai_20_dong_thoi"]["trang_thai"] == "da_kiem_gia"


def test_bao_cao_allowlist_khong_khoa_duong_noi_dung_ngoai_y_muon(bo, quan_sat_core_gia, tmp_path):
    a = AdapterGia(quan_sat_core_gia)
    nhan = a.nhan_ket_qua
    def nhan_them(t):
        return {**nhan(t), "khoa": "DEMO-BI-MAT", "duong_may": "DEMO-DUONG-MAY",
                "noi_dung": "DEMO-HO-SO-THAT", "loi": "DEMO-BI-MAT"}
    a.nhan_ket_qua = nhan_them
    r, _ = tc.chay(bo, ghim(), a)
    path = tc.duong_bao_cao(tmp_path / "bao-cao-DEMO.json", tmp_path)
    tc.ghi_bao_cao(path, r)
    text = path.read_text(encoding="utf-8")
    assert all(x not in text for x in ("DEMO-BI-MAT", "DEMO-DUONG-MAY", "DEMO-HO-SO-THAT", "1.000.000 VND", "DEMO-VAY-A"))
    with pytest.raises(LoiNghiepVu): tc.ghi_bao_cao(path, r)


@pytest.mark.parametrize("dir_name", ["goi", ".git", "ma-nguon", "jobs"])
def test_bao_cao_cam_goi_ngoai_workspace_ghi_de(tmp_path, dir_name):
    d = tmp_path / dir_name
    d.mkdir()
    with pytest.raises(LoiNghiepVu): tc.duong_bao_cao(d / "DEMO.json", tmp_path)
    with pytest.raises(LoiNghiepVu): tc.duong_bao_cao(tmp_path.parent / "DEMO.json", tmp_path)
    with pytest.raises(LoiNghiepVu): tc.duong_bao_cao(tmp_path / "DEMO.json", None)


def test_export_duoc_chon_mot_artifact_khong_sinh_cau_hinh(tmp_path):
    path = tmp_path / "TC11-DEMO.json"
    assert tc.main(["--bao-cao", str(path), "--workspace", str(tmp_path)]) == 0
    assert len(list(tmp_path.iterdir())) == 1
    r = json.loads(path.read_bytes())
    assert r["trang_thai"] == "chay_kho" and r["token_vao"] is None
    assert tc.main(["--bao-cao", str(path), "--workspace", str(tmp_path)]) == 2


def test_cmd_ascii_khong_tu_them_that_khong_cai_he_thong():
    text = (CONG_CU / "THU-TRA-CUU-THAT.cmd").read_bytes().decode("ascii")
    assert "thu_tra_cuu_that.py" in text and "%*" in text
    assert "--that" not in text and "pip install" not in text and "setx" not in text
