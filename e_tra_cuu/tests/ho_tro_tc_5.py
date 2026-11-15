"""Core điều phối TC-5, bộ quy tắc/ngưỡng chỉ DEMO; không model/mạng thật."""

from copy import deepcopy

from e_tra_cuu.kiem_dau_vao import bam, doc_json, json_chuan
from ho_tro_tc_2 import NGU_CANH
from ho_tro_tc_4 import BoAI, THAM_SO


PHAN_LOAI = "tra_cuu.phan_loai_tai_lieu@1"
AI_VERSION = "e_hoi_ai 0.5.0"
BEN_KY = "Bên ký: Công ty DEMO Ánh Dương (DEMO-P)."
DOI_TUONG = "Đối tượng DEMO-DT; Công trình DEMO-CT-01 tại địa điểm DEMO."
# Chỉ fixture được nghiệp vụ giả lập; không tự cài/kích hoạt trong runtime.
CAC_LOAI = {
    "phap_ly_du_an": ("01", "Giấy phép xây dựng DEMO", []),
    "vay": ("02", "Hợp đồng tín dụng DEMO", []),
    "mua_hang": ("03", "Mua dịch vụ văn phòng DEMO", []),
    "thue_may": ("03", "Thuê máy thi công DEMO", []),
    "cong_trinh": ("04", "Thi công có BOQ DEMO", []),
    "thiet_bi_lap_dat": ("04", "Thiết bị kèm lắp đặt DEMO", []),
    "vat_tu_cdt_cap": ("04", "Vật tư chủ đầu tư cấp DEMO", []),
    "sua_chua_bao_tri": ("04", "Sửa chữa bảo trì DEMO", []),
    "ban_nha": ("05", "Hợp đồng bán nhà DEMO", []),
    "kcn": ("05", "Điện năng gắn hợp đồng KCN DEMO", []),
    "ban_nhua": ("05", "Bán nhựa DEMO", []),
    "ban_dien_doc_lap": ("05", "Bán điện độc lập DEMO", []),
    "cp": ("06", "Đại hội đồng cổ đông DEMO", ["CP"]),
    "tnhh": ("06", "Hội đồng thành viên chủ sở hữu DEMO", ["TNHH"]),
    "quy_che_lao_dong": ("07", "Quy chế thưởng phạt người lao động DEMO", []),
    "nhan_su": ("07", "Hợp đồng lao động DEMO", []),
    "quy_che_khac": ("08", "Quy chế văn thư DEMO", []),
}


class BoPhanLoai(BoAI):
    def __init__(self, quy_tac="vay", *, van_ban=None, loai_hinh="CP", da_do=True,
                 trang_thai="hoat_dong", cong_trinh=True):
        self.quy_tac = quy_tac
        self.nc = deepcopy(NGU_CANH)
        self.nc["nhom"] = [f"{i:02}" for i in range(1, 9)]
        vb = van_ban if van_ban is not None else BEN_KY + "\n" + CAC_LOAI[quy_tac][1] + ".\n" + DOI_TUONG
        super().__init__(van_ban=vb)
        self.danh_muc["loai"] = [{"ma": "DEMO-" + q, "ten": ten,
            "nhom": n, "trang_thai": trang_thai if q == quy_tac else "hoat_dong"}
            for q, (n, ten, lh) in CAC_LOAI.items()]
        self.danh_muc["doi_tuong"] = [{"ma": "DEMO-DT", "ten": "Đối tượng DEMO"}]
        self.dm = self.tai("danh-muc-phan-loai-DEMO.json", json_chuan(self.danh_muc))
        self.bam_bo_do = bam(b"DEMO: bai do gia lap; khong phai accuracy thuc te")
        self.bo_quy_tac = {"phien_ban": 1, "quy_che_khac": ["Quy chế văn thư DEMO"],
            "phap_nhan": [{"ma": "DEMO-P", "loai_hinh": loai_hinh, "dau_hieu_ben_ky": [BEN_KY]},
                          {"ma": "DEMO-Q", "loai_hinh": "TNHH", "dau_hieu_ben_ky": ["Bên ký: Công ty DEMO Khác (DEMO-Q)."]}],
            "loai": [{"ma": "DEMO-" + q,
                      "quy_tac": "phap_ly_cong_ty" if q in {"cp", "tnhh"} else q,
                      "loai_hinh": lh, "dau_hieu": [ten]}
                     for q, (n, ten, lh) in CAC_LOAI.items()],
            "doi_tuong": [{"ma": "DEMO-DT", "nhom": self.nc["nhom"], "loai": [],
                           "dau_hieu": ["Công trình DEMO-CT-01 tại địa điểm DEMO" if cong_trinh else "Đối tượng DEMO-DT"],
                           "thong_tin_cong_trinh": cong_trinh}],
            "phep_do": {"bam_bo_do": self.bam_bo_do, "ma_prompt": THAM_SO["ma_prompt"],
                        "phien_ban_prompt": THAM_SO["phien_ban_prompt"], "model": "DEMO-model-local",
                        "phien_ban_engine_ai": AI_VERSION}}
        self.ghi_bo_quy_tac()
        if da_do:
            self.dat_cau_hinh({"phan_loai": {"trang_thai": "da_do", "nguong": 0.8, "bam_bo_do": self.bam_bo_do}})

    def ghi_bo_quy_tac(self):
        self.ref_quy_tac = self.tai("bo-quy-tac-DEMO.json", json_chuan(self.bo_quy_tac))
        self.dat_cau_hinh({"quy_tac_nhom": {"tep_id": self.ref_quy_tac["tep"]["tep_id"], "bam": self.ref_quy_tac["bam"]}})

    def cap(self, viec_id, yc, ref, *, cap=True):
        super().cap(viec_id, yc, ref, cap=cap)
        if cap:
            self.core.cua.giay_cap[viec_id]["ngu_canh_core"] = deepcopy(self.nc)

    def yeu_cau_ai(self, tac_vu):
        yc = super().yeu_cau_ai(tac_vu)
        yc["ngu_canh_core"] = deepcopy(self.nc)
        return yc

    def giao_ai(self, *args, **kwargs):
        i = super().giao_ai(*args, **kwargs)
        if i in self.core.cua.giay_cap:
            self.core.cua.giay_cap[i]["ngu_canh_core"] = deepcopy(self.nc)
        return i

    def chuan_bi_phan_loai(self, yc=None):
        self.nhan_ai(yc=yc)
        kq = self.chuan_bi()
        assert kq["trang_thai"] == "XONG", kq
        self.yc_ai = deepcopy(kq["ket_qua"])
        self.s_ai = self.snapshot_ai(kq)
        return self.yc_ai

    def can_cu(self, cau=None):
        ai = self.s_ai["ai"]
        m = next(x for x in ai["map_nguon"] if x["ma_nguon"] is not None)
        cau = self.van_ban if cau is None else cau
        a = ai["tai_lieu"].index(cau, m["ai_bat_dau"])
        return {"ma_nguon": m["ma_nguon"], "ma_doan": m["ma_doan"], "cau": cau,
                "bat_dau": a, "ket_thuc": a + len(cau)}

    def de_xuat(self):
        loai = "DEMO-" + self.quy_tac
        muc = next(x for x in self.danh_muc["loai"] if x["ma"] == loai)
        return {"nhom_de_xuat": CAC_LOAI[self.quy_tac][0],
                "loai_de_xuat": loai if muc["trang_thai"] == "hoat_dong" else None,
                "doi_tuong": "DEMO-DT", "diem": 0.95, "can_cu": [self.can_cu()],
                "ly_do_cho": [], "de_nghi_chuyen_bo": False}

    def phan_hoi(self, de_xuat=None):
        ai = self.yc_ai["yeu_cau_ai"]
        cc = self.can_cu()
        return {"loai": "tra_loi_ai", "tra_loi_ai": {
            "phien_ban": 1, "trang_thai": "co_can_cu", "tra_loi": "DEMO đề xuất chưa duyệt.",
            "du_lieu": self.de_xuat() if de_xuat is None else deepcopy(de_xuat),
            "trich_dan": [{k: cc[k] for k in ("cau", "bat_dau", "ket_thuc")}],
            "kiem_trich_dan": {"dat": True, "loi": []},
            "nha_cung_cap": "local", "model": "DEMO-model-local", "ly_do_chon_model": "DEMO",
            "ma_prompt": ai["ma_prompt"], "phien_ban_prompt": ai["phien_ban_prompt"],
            "phien_ban_engine": AI_VERSION, "bam_dau_vao": bam(json_chuan(self.yc_ai)),
            "chuyen_tiep": deepcopy(ai["chuyen_tiep"]), "canh_bao": []}}

    def giao_phan_loai(self, pb=None, *, cap=True, phap_nhan="DEMO-P"):
        self.pb_ai = deepcopy(self.phan_hoi() if pb is None else pb)
        self.pl_id = self.core.giao_viec(PHAN_LOAI, self.pb_ai, {}, phap_nhan_id=phap_nhan)
        ct = self.yc_ai["yeu_cau_ai"]["chuyen_tiep"]["tra_cuu"]
        ref = {"tep": ct["ho_so"], "bam": ct["bam_ho_so"]}
        refs = [*self.refs, ref]
        self.core.tep_duoc_mo[self.pl_id] = {r["tep"]["tep_id"] for r in refs}
        if cap:
            self.core.cua.giay_cap[self.pl_id] = {
                "ma_yeu_cau": ct["ma_yeu_cau"], "tac_vu": "phan_loai", "ngu_canh_core": deepcopy(self.nc),
                "yeu_cau_ai": deepcopy(self.yc_ai), "nguon_ai": {"nha_cung_cap": "local",
                    "model": "DEMO-model-local", "phien_ban_engine": AI_VERSION},
                "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in refs}, "nguon": deepcopy(self.nguon_duoc_cap)}
        return self.pl_id

    def phan_loai(self, pb=None, **kwargs):
        self.giao_phan_loai(pb, **kwargs)
        self.core.chay(self.app)
        return self.core.xem(self.pl_id)

    def doi_snapshot_ai(self, sua):
        s = deepcopy(self.s_ai)
        sua(s)
        ref = self.tai("snapshot-ai-doi-DEMO.json", json_chuan(s))
        # CoreGia mô phỏng nguồn mới có ref/băm đúng, nhưng quan hệ phải tự kiểm.
        self.yc_ai["yeu_cau_ai"]["chuyen_tiep"]["tra_cuu"].update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
        return s


def chay_demo_phan_loai():
    kq = []
    for q in ("phap_ly_du_an", "vay", "thue_may", "thiet_bi_lap_dat", "kcn", "cp", "quy_che_lao_dong", "quy_che_khac"):
        bo = BoPhanLoai(q)
        bo.chuan_bi_phan_loai()
        ra = bo.phan_loai()
        if ra["trang_thai"] == "XONG":
            s = bo.snapshot(ra)
            assert s["giai_doan"] == "da_phan_loai" and s["ket_qua"]["nhom_de_xuat"] == CAC_LOAI[q][0]
            assert s["ket_qua"]["kiem_tra"]["chi_la_de_xuat"] is True
        kq.append({"ten": "Phân loại DEMO — " + CAC_LOAI[q][0], **ra})
    for ten, kwargs in (("ngưỡng chưa đo", {"da_do": False}),
                        ("vật tư thiếu công trình", {"quy_tac": "vat_tu_cdt_cap", "cong_trinh": False}),
                        ("nhựa chưa bật", {"quy_tac": "ban_nhua", "trang_thai": "cho_kich_hoat"})):
        bo = BoPhanLoai(**kwargs)
        bo.chuan_bi_phan_loai()
        ra = bo.phan_loai()
        if ra["trang_thai"] == "XONG":
            s = bo.snapshot(ra)
            assert s["giai_doan"] == "cho_phan_loai" and s["ket_qua"]["ly_do_cho"]
        kq.append({"ten": "Hàng chờ DEMO — " + ten, **ra})
    return kq
