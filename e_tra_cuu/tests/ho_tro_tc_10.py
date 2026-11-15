"""Chuỗi DEMO TC-10 do CoreGia điều phối; không nằm trong runtime.

Fixture Local và đáp án tách biệt. Hỏi AI dùng handler AI-12 trong repo,
chỉ provider được thay bằng Local giả; TC không gọi engine/provider.
"""

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from e_tra_cuu.kiem_dau_vao import bam, doc_json, json_chuan
from ho_tro_tc_2 import GOI
from ho_tro_tc_3 import BoCatDoan, kiem_phu_nguon
from ho_tro_tc_4 import LocalGia, dieu_phoi_hoi_ai
from ho_tro_tc_5 import BoPhanLoai
from ho_tro_tc_6 import BoHauKiem
from ho_tro_tc_7 import BoTraLoi, TRUONG


DEMO = GOI / "demo/tc-10"
CHI_SO = ("tra_loi_dung", "trich_dan_dung", "tu_choi_dung", "phan_loai_dung")


def nap_bo():
    pin = doc_json((DEMO / "bam-DEMO.json").read_bytes())
    for ten, checksum in pin.items():
        assert Path(ten).name == ten and bam((DEMO / ten).read_bytes()) == checksum, "Sai băm fixture DEMO."
    bo = doc_json((DEMO / "bo-ca-DEMO.json").read_bytes())
    vang = doc_json((DEMO / "dap-an-DEMO.json").read_bytes())
    assert not bo["da_duyet_nghiep_vu"] and not vang["da_duyet_nghiep_vu"]
    assert bo["nhom_duoc_kich_hoat"] == vang["nhom_duoc_kich_hoat"] == []
    assert {x["ma"] for x in bo["kich_ban"]} == set(vang["dap_an"])
    for n in bo["nguon"].values():
        raw = (DEMO / n["tep"]).read_bytes()
        assert len(raw) == n["bytes"] and bam(raw) == n["bam"]
    return bo, vang["dap_an"]


def doc_nguon(bo, ma):
    return (DEMO / bo["nguon"][ma]["tep"]).read_bytes().decode("utf-8")


def hoi_local(bo, pb, du_lieu, quotes, *, chua_ro=False):
    """Đi qua consumer thật; không sửa phong bì sau AI để làm xanh kiểm chứng."""
    def hoi(self, cau_hinh, model, prompt, *, kiem_huy, khuon):
        kiem_huy()
        self.so_luot += 1
        self.prompts.append(prompt)
        if chua_ro:
            from kho_tri_thuc_sdk.engine import ChuaRo
            raise ChuaRo("DEMO-TC10-local-chua-tra")
        return json_chuan({"du_lieu": self.du_lieu, "truong": [
            {"ten": "DEMO", "gia_tri": "DEMO", "trich_dan": q} for q in dict.fromkeys(quotes)
        ]}).decode("utf-8")

    with patch.object(LocalGia, "hoi", hoi):
        ra, local = dieu_phoi_hoi_ai(bo, pb, deepcopy(du_lieu))
    if not chua_ro:
        assert ra["trang_thai"] == "XONG", ra
        assert local.so_luot == 1 and ra["ket_qua"]["tra_loi_ai"]["nha_cung_cap"] == "local"
        assert ra["ket_qua"]["tra_loi_ai"]["chuyen_tiep"] == pb["yeu_cau_ai"]["chuyen_tiep"]
    return ra, local


def xuat_day_du(bo, truoc):
    assert truoc["trang_thai"] == "XONG", truoc
    s = bo.snapshot(truoc)
    pb = deepcopy(truoc["ket_qua"])
    h = pb["ho_so_tra_cuu"]
    ref = {"tep": h["ho_so"], "bam": h["bam_ho_so"]}
    i = bo.core.giao_viec("tra_cuu.xuat_ket_qua@1", pb, {}, phap_nhan_id=s["ngu_canh_core"]["phap_nhan_id"])
    bo.core.tep_duoc_mo[i] = {h["ho_so"]["tep_id"]}
    bo.core.cua.giay_cap[i] = {"ma_yeu_cau": h["ma_yeu_cau"], "tac_vu": h["tac_vu"],
        "dau_vao": deepcopy(pb), "ngu_canh_core": deepcopy(s["ngu_canh_core"]),
        "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in [*bo.refs, ref]}, "nguon": deepcopy(bo.nguon_duoc_cap)}
    bo.core.chay(bo.app)
    ra = bo.core.xem(i)
    assert ra["trang_thai"] == "XONG", ra
    assert ra["ket_qua"]["loai"] == "truong"
    tep = ra["ket_qua"]["truong"]["tep_json"]
    raw = bo.core.doc_tep(tep["tep_id"])
    assert len(raw) == tep["kich_thuoc"]
    out = doc_json(raw)
    assert out["ket_qua"] == s["ket_qua"] and out["nguon"] == s["nguon"]
    assert out["bam_cau_hinh"] == h["bam_cau_hinh"] and out["bam_ho_so"] == h["bam_ho_so"]
    return out, ra


class BoTraLoiTC10(BoTraLoi):
    def __init__(self, ca, corpus):
        self.ca, self.corpus = deepcopy(ca), corpus
        super().__init__(van_ban=doc_nguon(corpus, ca["nguon"][0]))
        self.ngu_canh.update(nhom=[ca["nhom"]], module=ca.get("module", "M9"))
        self.cac_nguon = {}
        for j, ma in enumerate(ca["nguon"], 1):
            text = doc_nguon(corpus, ma)
            phien = corpus["nguon"][ma]["phien_ban"]
            if j == 1:
                self.nguon["phien_ban_nguon"] = self.tai_lieu["phien_ban_nguon"] = phien
                n, tl = self.nguon, self.tai_lieu
            else:
                goc = self.tai(f"nguon-{j}-DEMO.txt", text.encode("utf-8"), "text/plain")
                vb = deepcopy(self.pb_vb)
                vb["van_ban_tai_lieu"].update(van_ban=text, bam_dau_vao=goc["bam"])
                ref = self.tai(f"van-ban-{j}-DEMO.json", json_chuan(vb))
                n = {"ma_nguon": f"DEMO-NGUON-{j}", "phien_ban_nguon": phien,
                     "tep_id": goc["tep"]["tep_id"], "bam_goc": goc["bam"], "bam_van_ban": bam(text.encode("utf-8"))}
                tl = {"ma_nguon": n["ma_nguon"], "phien_ban_nguon": phien, "goc": goc, "van_ban": ref}
            self.cac_nguon[ma] = {"text": text, "nguon": deepcopy(n), "tai_lieu": deepcopy(tl)}
        self.nguon_duoc_cap = {v["nguon"]["ma_nguon"]: deepcopy(v["nguon"]) for v in self.cac_nguon.values()}

    def yeu_cau(self, *args, **kwargs):
        yc = super().yeu_cau(*args, **kwargs)
        yc["ngu_canh_core"] = deepcopy(self.ngu_canh)
        return yc

    def cap(self, *args, **kwargs):
        super().cap(*args, **kwargs)
        i = args[0]
        if i in self.core.cua.giay_cap:
            self.core.cua.giay_cap[i]["ngu_canh_core"] = deepcopy(self.ngu_canh)

    def giao_ai(self, *args, **kwargs):
        i = super().giao_ai(*args, **kwargs)
        if i in self.core.cua.giay_cap:
            self.core.cua.giay_cap[i]["ngu_canh_core"] = deepcopy(self.ngu_canh)
        return i

    def doan(self):
        d = super().doan()
        d["phien_ban_nguon"] = self.nguon["phien_ban_nguon"]
        return d

    def nhan_ca(self):
        ca, bang, cu = self.ca, [], self.van_ban
        for v in ca["local"]["bang_chung"]:
            src = self.cac_nguon[v["nguon"]]
            self.van_ban = src["text"]
            b = self.can_cu(truong=v["truong"], thuc_the=v["thuc_the"], cau=v["cau"],
                           gia_tri=v["gia_tri"], hien_thi=v["hien_thi"], nguon=src["nguon"])
            b["don_vi"] = v["don_vi"]
            b.update(deepcopy(ca.get("trang_thai_bang", {})))
            bang.append(b)
        self.van_ban = cu
        fields = deepcopy(TRUONG) + deepcopy(ca.get("truong_bo_sung", []))
        if len(bang) == 2 and all(b["truong"] == "gia_tri" for b in bang):
            fields = fields[:1]
        for f in fields:
            if f["ma"] == "gia_tri" and bang:
                f["don_vi"] = bang[0]["don_vi"]

        def sua(d):
            d.update(cau_hoi=ca["cau_hoi"], thuc_the=[deepcopy(ca["thuc_the"])],
                     co_van_ban_moi_cho_duyet=ca.get("co_van_ban_moi_cho_duyet", False))
            for p in d["phu_thuoc_cache"]:
                p.update(thuc_the=deepcopy(ca["thuc_the"]), nguon=deepcopy(self.nguon),
                         phu_thuoc_thoi_diem=ca.get("phu_thuoc_thoi_diem", False))
            if ca["tang"] > 1:
                d["nguon"] = [deepcopy(n["tai_lieu"]) for n in self.cac_nguon.values()]
                d["bang_chung"] = [] if not bang else [{
                    **{k: n["nguon"][k] for k in ("ma_nguon", "phien_ban_nguon", "bam_goc", "bam_van_ban")},
                    "nguyen_van": n["text"], "bat_dau": 0, "ket_thuc": len(n["text"]),
                    "vi_tri": {"trang": None, "hop": None}} for n in self.cac_nguon.values()]

        self.nhan_soan(ca["tang"], bang=bang, fields=fields, sua=sua)
        self.profile["phu_thuoc_thoi_diem"] = ca.get("phu_thuoc_thoi_diem", False)
        if ca.get("thieu_nguong"):
            self.profile["nguong_tin_cay"] = None
        return self.pb_nhan

    def local_ca(self):
        self.chuan_bi_soan()
        d = self.du_lieu_soan()
        if self.ca.get("mau_thuan"):
            d["co_mau_thuan"] = True
            d["tra_loi"] = "Có mâu thuẫn trong bằng chứng; Anh cần duyệt các giá trị sau.\n" + d["tra_loi"]
        sai = self.ca.get("sai_local")
        if sai == "gia_tri":
            d["khang_dinh"][0]["gia_tri"]["so"] = 999999999
        elif sai == "ngay":
            d["khang_dinh"][1]["gia_tri"] = "2026-10-31"
        elif sai == "offset":
            d["khang_dinh"][0]["can_cu"][0]["bat_dau"] += 1
        elif sai == "quote":
            d["khang_dinh"][0]["can_cu"][0]["cau"] = "DEMO bịa 9.000.000 VND."
        quotes = [b["cau"] for b in self.profile["bang_chung"]]
        ra, local = hoi_local(self, self.pb_ai, d, quotes)
        self.so_luot_local += local.so_luot
        self.pb_local = ra["ket_qua"]
        return local


def chay_ca(ca, corpus):
    local = None
    if ca["tac_vu"] == "phan_loai":
        bo = BoPhanLoai(ca["quy_tac"], van_ban=doc_nguon(corpus, ca["nguon"][0]),
            loai_hinh=ca.get("loai_hinh", "CP"), da_do=ca.get("da_do", True),
            trang_thai=ca.get("trang_thai_loai", "hoat_dong"), cong_trinh=ca.get("cong_trinh", True))
        bo.chuan_bi_phan_loai()
        du_lieu = {**deepcopy(ca["local"]), "can_cu": [bo.can_cu()]}
        ai, local = hoi_local(bo, bo.yc_ai, du_lieu, [bo.van_ban])
        ra = bo.phan_loai(ai["ket_qua"])
    else:
        bo = BoTraLoiTC10(ca, corpus)
        bo.nhan_ca()
        if ca["ai"]:
            local = bo.local_ca()
        ra = bo.soan()
    out, xuat = xuat_day_du(bo, ra)
    return {"ma": ca["ma"], "trang_thai_do": "da_do", "xuat": out,
            "so_luot_local_gia": local.so_luot if local else 0,
            "so_luot_cloud": 0, "bo": bo, "ra": ra, "ra_xuat": xuat,
            "prompts": local.prompts if local else []}


def rut_khang_dinh(kq, *, trich_dan=False):
    ds = []
    for k in kq.get("khang_dinh", []):
        v = {"thuc_the": k["thuc_the"]["ma"], "truong": k["truong"],
             "gia_tri": k["gia_tri"], "don_vi": k["don_vi"]}
        if trich_dan:
            v["can_cu"] = [{"ma_nguon": c["nguon"]["ma_nguon"],
                "phien_ban_nguon": c["nguon"]["phien_ban_nguon"], "bam_goc": c["nguon"]["bam_goc"],
                **{t: c[t] for t in ("cau", "bat_dau", "ket_thuc")}} for c in k["can_cu"]]
        ds.append(v)
    return ds


def cham(vang, quan_sat):
    out = quan_sat["xuat"]
    kq = out["ket_qua"]
    expected = vang.get("khang_dinh", [])
    values = [{k: v for k, v in b.items() if k != "can_cu"} for b in expected]
    dung = {}
    if "tra_loi_dung" in vang["chi_so"]:
        dung["tra_loi_dung"] = (kq.get("co_can_cu") is True and json_chuan(rut_khang_dinh(kq)) == json_chuan(values)
            and kq.get("tra_loi") == vang["tra_loi"] and kq.get("co_mau_thuan") is vang["co_mau_thuan"]
            and kq.get("nhan") == vang["nhan"])
    if "trich_dan_dung" in vang["chi_so"]:
        # Đáp án ghim cả nguồn/phiên bản/bytes/offset, không chỉ xét có quote.
        dung["trich_dan_dung"] = bool(expected) and json_chuan(rut_khang_dinh(kq, trich_dan=True)) == json_chuan(expected)
    if "tu_choi_dung" in vang["chi_so"]:
        dung["tu_choi_dung"] = (kq.get("trang_thai") == "khong_thay_can_cu" and kq.get("co_can_cu") is False
            and kq.get("khang_dinh") == [] and kq.get("nhan") is None
            and bool(kq.get("tra_loi")) and not any(c.isdigit() for c in kq["tra_loi"]))
    if "phan_loai_dung" in vang["chi_so"]:
        dung["phan_loai_dung"] = (out["giai_doan"] == vang["giai_doan"]
            and all(kq.get(k) == vang[k] for k in ("nhom_de_xuat", "loai_de_xuat"))
            and set(vang["ly_do"]) <= set(kq["kiem_tra"]["ma_ly_do"])
            and kq["kiem_tra"]["chi_la_de_xuat"] is True
            and kq["kiem_tra"]["diem_la_xac_suat"] is False)
    return dung


def tong_hop(vang, quan_sat):
    ket_qua = {}
    for chi_so in CHI_SO:
        items = [(ma, v) for ma, v in vang.items() if chi_so in v["chi_so"]]
        tu, mau, chua, skip, loi = 0, 0, 0, 0, 0
        for ma, v in items:
            q = quan_sat.get(ma)
            tt = q.get("trang_thai_do") if q else "chua_do"
            if tt == "skip":
                assert q.get("ly_do"), "Ca skip phải có lý do."
                skip += 1
            elif tt == "chua_do":
                chua += 1
            else:
                mau += 1
                if tt == "loi":
                    loi += 1
                else:
                    assert tt == "da_do"
                    tu += int(cham(v, q)[chi_so])
        ket_qua[chi_so] = {"tu_so": tu, "mau_so": mau, "so_ca_du_kien": len(items),
            "chua_do": chua, "skip": skip, "loi_chay": loi, "ty_le": tu / mau if mau else None}
    return ket_qua


def chay_bo_do():
    corpus, vang = nap_bo()
    quan_sat = {}
    for ca in corpus["kich_ban"]:
        quan_sat[ca["ma"]] = chay_ca(ca, corpus)
    cau_hinh_dot = {m: q["xuat"]["bam_cau_hinh"] for m, q in quan_sat.items()}
    report = {"phien_ban": 1, "nhan": "DEMO", "moi_truong": "CoreGia SDK 2.2.0 / Local giả",
        "da_duyet_nghiep_vu": False, "nhom_duoc_kich_hoat": [], "accuracy_model_that": None,
        "nguong_tin_cay_that": None, "core_that": "chua_kiem", "ly_do_chua_do_that": "Chưa có phép đo Core/model thật và bộ câu hỏi nghiệp vụ được duyệt.",
        "bam_bo_ca": bam((DEMO / "bo-ca-DEMO.json").read_bytes()),
        "bam_dap_an": bam((DEMO / "dap-an-DEMO.json").read_bytes()),
        "cau_hinh_da_ghim": cau_hinh_dot, "bam_cau_hinh_toan_dot": bam(json_chuan(cau_hinh_dot)),
        "chi_so": tong_hop(vang, quan_sat),
        "theo_nhom": {nhom: tong_hop({k: v for k, v in vang.items() if v["nhom"] == nhom}, quan_sat)
                      for nhom in sorted({v["nhom"] for v in vang.values()})},
        "cac_ca": [{"ma": ma, "trang_thai_do": q["trang_thai_do"], "chi_so": cham(vang[ma], q),
                    "so_luot_local_gia": q["so_luot_local_gia"]} for ma, q in quan_sat.items()],
        "so_luot_local_gia": sum(q["so_luot_local_gia"] for q in quan_sat.values()), "so_luot_cloud": 0,
        "so_ca": len(quan_sat), "so_ca_dat": sum(all(cham(vang[m], q).values()) for m, q in quan_sat.items())}
    return report, quan_sat


def ghi_dot_kiem_core_gia(report):
    """Ghi cặp tử/mẫu thực của bài DEMO vào ngăn SDK, không ngưỡng thật."""
    from kho_tri_thuc_sdk.thu import CoreGia
    from e_tra_cuu import chay
    from ho_tro_sdk_22 import mo_viec_ngan

    core = CoreGia()
    raw = json_chuan(report)
    ref = core.them_tep("bao-cao-DEMO.json", raw, "application/json")
    data = {"trang_thai": "da_do", "bam_bo": report["bam_bo_ca"],
            "bam_cau_hinh": report["bam_cau_hinh_toan_dot"], "phien_ban_engine": "e_tra_cuu " + chay.app.phien_ban,
            "chi_so": {k: {t: c[t] for t in ("tu_so", "mau_so")} for k, c in report["chi_so"].items()},
            "bao_cao": ref, "bam_bao_cao": bam(raw)}
    with mo_viec_ngan(core) as viec:
        a = chay.ghi_bai_do_demo(viec, chay.app, ma_dot="DEMO-TC10", gia_tri=data)
        b = chay.ghi_bai_do_demo(viec, chay.app, ma_dot="DEMO-TC10", gia_tri=data)
        assert a.da_tao and not b.da_tao and a.id == b.id
        row = viec.ngan.doc("dot_kiem", {"ma_dot": "DEMO-TC10"})
        assert doc_json(row.gia_tri["chi_so"].encode("utf-8")) == data["chi_so"]
        assert row.gia_tri["bam_bao_cao"] == bam(core.doc_tep(ref["tep_id"]))
    return core.xem_ngan(chay.app.ma, "dot_kiem"), data


def chay_nam_tac_vu():
    """Ba nhánh còn lại + hai nhánh trong bộ chấm; xuất qua loại hợp lệ."""
    corpus, _ = nap_bo()
    kq = []
    bo = BoCatDoan(thu_muc_demo=GOI / "demo")
    bo.nhan()
    ra = bo.cat()
    kiem_phu_nguon(bo, ra)
    out, _ = xuat_day_du(bo, ra)
    kq.append({"ten": "TC10 cắt Python → xuất", "tac_vu": out["tac_vu"], "trang_thai": "XONG"})
    for tac in ("phan_tich_cau_hoi", "xep_hang_lai"):
        bo = BoHauKiem()
        bo.chuan_bi_hau(tac)
        du_lieu = bo.du_lieu_local()
        quote = bo.yc["du_lieu"]["cau_hoi"] if tac == "phan_tich_cau_hoi" else bo.van_ban
        ai, local = hoi_local(bo, bo.pb_ai, du_lieu, [quote])
        out, _ = xuat_day_du(bo, bo.hau_kiem(ai["ket_qua"]))
        kq.append({"ten": "TC10 Local → hậu kiểm → xuất " + tac, "tac_vu": out["tac_vu"], "trang_thai": "XONG"})
    for tac in ("phan_loai", "soan_tra_loi"):
        ca = next(c for c in corpus["kich_ban"] if c["tac_vu"] == tac)
        q = chay_ca(ca, corpus)
        kq.append({"ten": "TC10 nhận → hậu kiểm → xuất " + tac, "tac_vu": q["xuat"]["tac_vu"], "trang_thai": "XONG"})
    return kq
