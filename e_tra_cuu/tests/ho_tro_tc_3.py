"""CoreGia cấp snapshot xuyên bước chỉ trong tests; chỉ có dữ liệu DEMO."""

from copy import deepcopy

from e_tra_cuu.kiem_dau_vao import bam, json_chuan
from ho_tro_tc_2 import BoDemo, NGU_CANH


CAT = "tra_cuu.cat_doan@1"


class BoCatDoan(BoDemo):
    def nguon_co_cau_truc(self, pb):
        self.pb_vb = deepcopy(pb)
        self.van_ban = pb["van_ban_tai_lieu"]["van_ban"]
        self.pb_vb["van_ban_tai_lieu"]["bam_dau_vao"] = self.goc["bam"]
        self.vb = self.tai("van-ban-co-cau-truc-DEMO.json", json_chuan(self.pb_vb))
        self.tai_lieu["van_ban"] = deepcopy(self.vb)
        self.nguon["bam_van_ban"] = bam(self.van_ban.encode("utf-8"))
        self.nguon_duoc_cap[self.nguon["ma_nguon"]] = deepcopy(self.nguon)

    def dat_cau_hinh(self, ban_va):
        self.cau_hinh.update(deepcopy(ban_va))
        self.core.dat_cau_hinh(self.app.ma, self.cau_hinh)

    def nhan(self, yc=None):
        kq = self.chay(self.yeu_cau("cat_doan") if yc is None else yc)
        assert kq["trang_thai"] == "XONG", kq
        self.kq_nhan = kq
        self.pb_nhan = deepcopy(kq["ket_qua"])
        self.s_nhan = self.snapshot(kq)
        return self.pb_nhan

    def giao_cat(self, pb=None, *, muc_tieu=200, cap=True, phap_nhan="DEMO-P"):
        pb = self.pb_nhan if pb is None else pb
        self.cat_id = self.core.giao_viec(CAT, deepcopy(pb),
            {} if muc_tieu is None else {"do_dai_muc_tieu": muc_tieu}, phap_nhan_id=phap_nhan)
        self.core.tep_duoc_mo[self.cat_id] = {r["tep"]["tep_id"] for r in self.refs} | {pb["ho_so_tra_cuu"]["ho_so"]["tep_id"]}
        if cap:
            ref = {"tep": deepcopy(pb["ho_so_tra_cuu"]["ho_so"]), "bam": pb["ho_so_tra_cuu"]["bam_ho_so"]}
            self.core.cua.giay_cap[self.cat_id] = {
                "ma_yeu_cau": pb["ho_so_tra_cuu"]["ma_yeu_cau"], "tac_vu": "cat_doan",
                "dau_vao": deepcopy(pb), "ngu_canh_core": deepcopy(NGU_CANH),
                "metadata_core": deepcopy(self.s_nhan["du_lieu"]["metadata_core"]),
                "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in [*self.refs, ref]},
                "nguon": deepcopy(self.nguon_duoc_cap),
            }
        return self.cat_id

    def cat(self, pb=None, **kwargs):
        self.giao_cat(pb, **kwargs)
        self.core.chay(self.app)
        return self.core.xem(self.cat_id)

    def doi_snapshot(self, sua):
        s = deepcopy(self.s_nhan)
        sua(s)
        ref = self.tai("snapshot-doi-DEMO.json", json_chuan(s))
        pb = deepcopy(self.pb_nhan)
        pb["ho_so_tra_cuu"].update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
        return pb


def phong_bi_trang(bo, cac_trang, cac_khoi=None):
    pb = deepcopy(bo.pb_vb)
    v = pb["van_ban_tai_lieu"]
    v.update(van_ban="\f".join(cac_trang), nguon_doc="lop_chu_san", so_trang=len(cac_trang), trang=[])
    for i, chu in enumerate(cac_trang, 1):
        khoi = [{"loai": "doan", "van_ban": chu, "hop": [10, 20, 500, 100]}] if chu else []
        v["trang"].append({"so": i, "rong": 595, "cao": 842, "don_vi": "pt",
                           "khoi": deepcopy(cac_khoi[i - 1] if cac_khoi is not None else khoi)})
    return pb


def bang_demo(bo, *, docx=False, so_hang=7, gop=True):
    """Bảng DEMO có tiêu đề gộp ngang, thân gộp dọc, ô rỗng và map thật."""
    dau = "Công ty DEMO Ánh Dương\nĐiều 1. Bảng DEMO\n"
    than, cac_o = "", []

    def them(h, c, chu, gh=1, gc=1):
        nonlocal than
        a = len(dau) + len(than)
        cac_o.append({"hang": h, "cot": c, "gop_hang": gh, "gop_cot": gc,
                      "van_ban": chu, "bat_dau": a, "ket_thuc": a + len(chu)})
        than += chu

    them(0, 0, "BẢNG DEMO Giá trị và ngày", gc=2)
    than += "\n"
    for r in range(1, so_hang):
        if not (gop and r == 2):
            them(r, 0, f"Khoản DEMO {r} " + "Ánh Dương " * 5,
                 gh=2 if gop and r == 1 else 1)
            than += "\t"
        them(r, 1, "" if r == 2 else "1.000.000 VND / 2026-10-30")
        than += "\n"
    cuoi = "\nĐiều 2. Kết thúc DEMO, giữ đủ đuôi."
    a, z = len(dau), len(dau + than)
    bang = {"loai": "bang", "hop": None if docx else [10, 100, 500, 700],
            "bat_dau": a, "ket_thuc": z, "hang_tieu_de": [0], "o": cac_o}
    khoi = [{"loai": "doan", "van_ban": dau, "hop": None if docx else [10, 20, 500, 90]},
            bang, {"loai": "doan", "van_ban": cuoi, "hop": None if docx else [10, 710, 500, 790]}]
    if docx:
        pb = deepcopy(bo.pb_vb)
        pb["van_ban_tai_lieu"].update(van_ban=dau + than + cuoi, khoi=khoi)
    else:
        pb = phong_bi_trang(bo, [dau + than + cuoi], [khoi])
    return pb


def kiem_phu_nguon(bo, kq):
    assert kq["trang_thai"] == "XONG", kq
    s = bo.snapshot(kq)
    h = kq["ket_qua"]["ho_so_tra_cuu"]
    ds, vb = s["ket_qua"]["doan"], bo.van_ban
    assert h["tom_tat"]["so_doan"] == len(ds)
    assert h["giai_doan"] == s["giai_doan"] == h["tom_tat"]["trang_thai"] == "da_cat_doan"
    assert s["du_lieu"] == bo.s_nhan["du_lieu"]
    assert s["nguon"] == bo.s_nhan["nguon"]
    assert len({d["ma_doan"] for d in ds}) == len(ds)
    cac_phan, con_tro = [], 0
    for d in ds:
        assert "confidence" not in d and "do_tin_cay" not in d
        assert d["metadata_core"] == s["du_lieu"]["metadata_core"]
        assert all(d[k] == bo.nguon[k] for k in bo.nguon)
        dai_doan = 0
        for m in d["map_nguon"]:
            assert m["doan_bat_dau"] == dai_doan
            a, z = m["nguon_bat_dau"], m["nguon_ket_thuc"]
            assert d["nguyen_van"][m["doan_bat_dau"]:m["doan_ket_thuc"]] == vb[a:z]
            dai_doan = m["doan_ket_thuc"]
            if m["vai_tro"] == "noi_dung":
                assert a == con_tro
                con_tro = z
                cac_phan.append(vb[a:z])
        assert dai_doan == len(d["nguyen_van"])
        if d["bat_dau"] is not None:
            assert d["nguyen_van"] == vb[d["bat_dau"]:d["ket_thuc"]]
        else:
            assert d["ket_thuc"] is None and any(m["vai_tro"] == "ngu_canh_lap" for m in d["map_nguon"])
        if d["bang"]:
            for o in d["bang"]["o"]:
                assert o["van_ban"] == vb[o["bat_dau"]:o["ket_thuc"]]
                assert o["van_ban"] == d["nguyen_van"][o["doan_bat_dau"]:o["doan_ket_thuc"]]
    assert con_tro == len(vb) and "".join(cac_phan) == vb
    return s, ds
