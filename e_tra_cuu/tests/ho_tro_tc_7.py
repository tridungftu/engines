"""Quan hệ bằng chứng DEMO độc lập, CoreGia điều phối; không provider thật."""

from copy import deepcopy

from e_tra_cuu.kiem_dau_vao import bam, json_chuan
from ho_tro_tc_2 import NGU_CANH
from ho_tro_tc_6 import BoHauKiem


SOAN = "tra_cuu.soan_tra_loi@1"
VAN_BAN = ("Công ty DEMO Ánh Dương\nĐiều 1. Nghĩa vụ DEMO\n"
           "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND, ngày 2026-10-30.\n"
           "Khoản vay DEMO-VAY-B có giá trị 2.000.000 USD, ngày 2026-11-01.\n"
           "Mã khoản vay 0007.")
TRUONG = [{"ma": "gia_tri", "ten": "Giá trị", "kieu": "so_tien", "don_vi": "VND"},
          {"ma": "ngay", "ten": "Ngày", "kieu": "ngay", "don_vi": None}]


class BoTraLoi(BoHauKiem):
    def __init__(self, **kwargs):
        super().__init__(van_ban=kwargs.pop("van_ban", VAN_BAN), **kwargs)
        self.profile = None

    def can_cu(self, *, truong="gia_tri", thuc_the=None, cau=None, gia_tri=None, hien_thi=None, nguon=None):
        e = thuc_the or self.thuc_the()[0]
        cau = cau or "Khoản vay DEMO-VAY-A có giá trị 1.000.000 VND, ngày 2026-10-30."
        a = self.van_ban.index(cau)
        tien = truong == "gia_tri"
        hien_thi = hien_thi or ("1.000.000 VND" if tien else "2026-10-30")
        x = a + cau.index(hien_thi)
        return {"nguon": deepcopy(nguon or self.nguon), "thuc_the": deepcopy(e), "truong": truong,
                "kieu": "so_tien" if tien else "ngay", "gia_tri": deepcopy(gia_tri if gia_tri is not None
                    else {"so": 1000000, "tien_te": "VND"} if tien else "2026-10-30"),
                "don_vi": "VND" if tien else None, "quy_tac": "tien_nhom_ba" if tien else "ngay_iso",
                "hien_thi": hien_thi, "cau": cau, "bat_dau": a, "ket_thuc": a + len(cau),
                "vi_tri_gia_tri": [x, x + len(hien_thi)], "vi_tri": {"trang": None, "hop": None, "dieu": "Điều 1. Nghĩa vụ DEMO"},
                "trang_thai_duyet": "da_duyet", "con_hieu_luc": True, "do_tin_cay": 0.95,
                "moc_cong_bo": NGU_CANH["thoi_diem"], "moc_duyet": NGU_CANH["thoi_diem"],
                "hieu_luc_tu": "2026-10-30", "hieu_luc_den": None}

    def nhan_soan(self, tang=1, *, bang=None, fields=None, sua=None):
        self.tac_vu = "soan_tra_loi"
        bang = deepcopy([self.can_cu(), self.can_cu(truong="ngay")] if bang is None else bang)
        yc = self.yeu_cau("soan_tra_loi") if tang == 1 else self.yeu_cau_ai("soan_tra_loi")
        d = yc["du_lieu"]
        d["tang"] = tang
        if tang == 1:
            d["bang_chung"] = [{k: b[k] for k in ("nguon", "thuc_the", "truong", "kieu", "gia_tri", "don_vi",
                 "trang_thai_duyet", "con_hieu_luc", "do_tin_cay", "moc_cong_bo")} for b in bang]
        if sua:
            sua(d)
        self.yc = deepcopy(yc)
        self.nhan_ai("soan_tra_loi", yc)
        self.profile = {"phien_ban": 1, "trang_thai_nguon": "da_tra", "bam_du_lieu": bam(json_chuan(self.s_nhan["du_lieu"])),
            "truong_can_tra_loi": deepcopy(TRUONG if fields is None else fields),
            "nguong_tin_cay": {"trang_thai": "da_do", "gia_tri": 0.9, "bam_bo_do": bam(b"DEMO-bo-do"), "da_duyet": True},
            "phu_thuoc_thoi_diem": False, "bang_chung": bang}
        return self.pb_nhan

    def chuan_bi_soan(self):
        self.giao_ai()
        self.core.cua.giay_cap[self.ai_id]["kiem_chung_tra_loi"] = deepcopy(self.profile)
        self.core.chay(self.app)
        ra = self.core.xem(self.ai_id)
        assert ra["trang_thai"] == "XONG", ra
        self.pb_ai = ra["ket_qua"]
        self.s_ai = self.snapshot_ai(ra)
        return ra

    def du_lieu_soan(self):
        cac_cau, khang_dinh = [], []
        for b in self.profile["bang_chung"]:
            ten = next(f["ten"] for f in self.profile["truong_can_tra_loi"] if f["ma"] == b["truong"])
            cac_cau.append(f'{ten} ({b["thuc_the"]["gia_tri"]}): {b["hien_thi"]}.')
            m = next(m for m in self.s_ai["ai"]["map_nguon"] if m["ma_nguon"] == b["nguon"]["ma_nguon"]
                and m["nguon_bat_dau"] <= b["bat_dau"] < b["ket_thuc"] <= m["nguon_ket_thuc"])
            x = m["ai_bat_dau"] + b["bat_dau"] - m["nguon_bat_dau"]
            khang_dinh.append({"thuc_the": b["thuc_the"]["ma"], "truong": b["truong"], "gia_tri": deepcopy(b["gia_tri"]),
                "don_vi": b["don_vi"], "can_cu": [{"ma_nguon": b["nguon"]["ma_nguon"], "ma_doan": m["ma_doan"],
                 "cau": b["cau"], "bat_dau": x, "ket_thuc": x + len(b["cau"])}]})
        return {"tra_loi": "\n".join(cac_cau), "khang_dinh": khang_dinh, "co_mau_thuan": False}

    def local_soan(self, du_lieu=None):
        pb = self.local_gia(self.du_lieu_soan() if du_lieu is None else du_lieu)
        ai = self.s_ai["ai"]
        pb["tra_loi_ai"]["trich_dan"] = [{"cau": ai["tai_lieu"][m["ai_bat_dau"]:m["ai_ket_thuc"]],
            "bat_dau": m["ai_bat_dau"], "ket_thuc": m["ai_ket_thuc"]} for m in ai["map_nguon"] if m["ma_nguon"] is not None]
        self.pb_local = deepcopy(pb)
        return pb

    def giao_soan(self, pb=None, *, cap=True, phap_nhan="DEMO-P"):
        pb = deepcopy((self.pb_local if hasattr(self, "pb_local") else self.pb_nhan) if pb is None else pb)
        self.soan_id = self.core.giao_viec(SOAN, pb, {}, phap_nhan_id=phap_nhan)
        c = pb["tra_loi_ai"]["chuyen_tiep"]["tra_cuu"] if pb["loai"] == "tra_loi_ai" else pb["ho_so_tra_cuu"]
        ref = {"tep": c["ho_so"], "bam": c["bam_ho_so"]}
        refs = [*self.refs, ref]
        self.core.tep_duoc_mo[self.soan_id] = {r["tep"]["tep_id"] for r in refs}
        if cap:
            self.core.cua.giay_cap[self.soan_id] = {"ma_yeu_cau": c["ma_yeu_cau"], "tac_vu": "soan_tra_loi",
                "dau_vao": deepcopy(pb), "ngu_canh_core": deepcopy(self.ngu_canh),
                "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in refs}, "nguon": deepcopy(self.nguon_duoc_cap),
                "kiem_chung_tra_loi": deepcopy(self.profile)}
        return self.soan_id

    def soan(self, pb=None, **kwargs):
        self.giao_soan(pb, **kwargs)
        self.core.chay(self.app)
        return self.core.xem(self.soan_id)

    def doi_snapshot_soan(self, sua):
        if hasattr(self, "pb_local"):
            return self.doi_snapshot(sua)
        s = deepcopy(self.s_nhan)
        sua(s)
        ref = self.tai("snapshot-doi-DEMO.json", json_chuan(s))
        pb = deepcopy(self.pb_nhan)
        pb["ho_so_tra_cuu"].update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
        return pb


def chay_demo_tra_loi():
    kq = []
    for ten, tang, ai in (("Python tầng một DEMO", 1, False), ("AI tầng một tối đa Vàng DEMO", 1, True),
                          ("Đoạn tầng hai DEMO", 2, True), ("Adapter tầng ba DEMO", 3, True)):
        bo = BoTraLoi()
        bo.nhan_soan(tang)
        if ai:
            bo.chuan_bi_soan()
            bo.local_soan()
        ra = bo.soan()
        if ra["trang_thai"] == "XONG":
            r = bo.snapshot(ra)["ket_qua"]
            assert r["trang_thai"] == "co_can_cu" and r["nhan"] == ("vang" if ai else "xanh"), r
        kq.append({"ten": ten, **ra})
    bo = BoTraLoi()
    bo.nhan_soan(bang=[])
    ra = bo.soan()
    if ra["trang_thai"] == "XONG":
        assert bo.snapshot(ra)["ket_qua"]["trang_thai"] == "khong_thay_can_cu"
    kq.append({"ten": "Không căn cứ DEMO không số", **ra})
    for ten in ("Quote bịa DEMO bị loại", "Văn bản mới DEMO hạ Vàng", "Thiếu ngưỡng DEMO không số"):
        bo = BoTraLoi()
        bo.nhan_soan(2 if ten.startswith("Quote") else 1,
                      sua=(lambda d: d.update(co_van_ban_moi_cho_duyet=True)) if ten.startswith("Văn") else None)
        if ten.startswith("Quote"):
            bo.chuan_bi_soan()
            bo.local_soan()
            bo.pb_local["tra_loi_ai"]["du_lieu"]["khang_dinh"][0]["can_cu"][0]["cau"] = "DEMO bịa 9.000.000 VND."
        elif ten.startswith("Thiếu"):
            bo.profile["nguong_tin_cay"] = None
        ra = bo.soan()
        if ra["trang_thai"] == "XONG":
            r = bo.snapshot(ra)["ket_qua"]
            if ten.startswith("Văn"):
                assert r["co_can_cu"] and r["nhan"] == "vang" and r["canh_bao"]
            else:
                assert not r["co_can_cu"] and r["nhan"] is None and r["khang_dinh"] == []
        kq.append({"ten": ten, **ra})
    return kq
