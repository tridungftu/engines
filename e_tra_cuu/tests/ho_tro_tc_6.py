"""CoreGia điều phối Local giả theo protocol; 0 model/provider thật, chỉ DEMO.

Không dùng validator TC-6 để tự tạo đáp án. Từng phản hồi/giấy cấp là fixture
độc lập; seam bổ sung chưa phải C-TC-03 đã phát hành và không chứng nhận RLS.
"""

from copy import deepcopy

from kho_tri_thuc_sdk.engine import Engine

from e_tra_cuu.kiem_dau_vao import bam, json_chuan
from ho_tro_tc_2 import GOI, NGU_CANH
from ho_tro_tc_4 import BoAI


PHAN_TICH = "tra_cuu.phan_tich_cau_hoi@1"
XEP_HANG = "tra_cuu.xep_hang_lai@1"
THUC_THE = [{"loai": "khoan_vay", "ma": x, "gia_tri": x}
            for x in ("DEMO-VAY-A", "DEMO-VAY-B", "0007", "007", "DEMO-VAY-AB")]


class BoHauKiem(BoAI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.so_luot_local = 0
        self.ngu_canh = deepcopy(NGU_CANH)

    def chuan_bi_hau(self, tac_vu="phan_tich_cau_hoi", yc=None):
        self.tac_vu = tac_vu
        self.yc = deepcopy(self.yeu_cau_ai(tac_vu) if yc is None else yc)
        self.nhan_ai(tac_vu, self.yc)
        ra = self.chuan_bi()
        assert ra["trang_thai"] == "XONG", ra
        self.pb_ai = ra["ket_qua"]
        self.s_ai = self.snapshot_ai(ra)
        self.meta = {
            "bam_cau_hoi": bam(self.yc["du_lieu"]["cau_hoi"].encode("utf-8")),
            "thuc_the": deepcopy(THUC_THE), "can_lam_ro": False,
            "y_dinh": [{"ma": "gia_tri", "cum_tu": ["Giá trị", "Số tiền"], "phu_thuoc_thoi_diem": False},
                       {"ma": "lai_suat", "cum_tu": ["Lãi suất"], "phu_thuoc_thoi_diem": True}],
            "ham": {h["ten"]: {"phien_ban": h["phien_ban"], "trang_thai": "chua_chay", "moc_cong_bo": None,
                "y_dinh": ["gia_tri"],
                "rang_buoc": {"ma_khoan_vay": {"loai": "thuc_the", "loai_thuc_the": "khoan_vay", "truong": "ma"}}}
                for h in self.yc["du_lieu"].get("ham", [])},
        }
        return ra

    def du_lieu_local(self, *, ma_thuc_the="DEMO-VAY-A"):
        if self.tac_vu == "xep_hang_lai":
            return {"xep_hang": [{"ma_ung_vien": x["ma_ung_vien"], "diem": 0.5}
                                  for x in self.yc["du_lieu"]["ung_vien"]]}
        return {"y_dinh": "gia_tri", "thuc_the": [{"loai": "khoan_vay", "ma": ma_thuc_the, "gia_tri": ma_thuc_the}],
                "ham_de_xuat": [{"ten": "m9.gia_tri", "phien_ban": "1", "tham_so": {"ma_khoan_vay": ma_thuc_the}}],
                "phu_thuoc_thoi_diem": False, "thoi_diem": self.ngu_canh["thoi_diem"]}

    def local_gia(self, du_lieu=None):
        yc = self.pb_ai["yeu_cau_ai"]
        maps = [m for m in self.s_ai["ai"]["map_nguon"] if (m["duong_dan_snapshot"] == ["du_lieu", "cau_hoi"]
                if self.tac_vu == "phan_tich_cau_hoi" else m["ma_ung_vien"] is not None)]
        a = {"phien_ban": 1, "trang_thai": "co_can_cu", "tra_loi": "Kết quả DEMO Local giả do Core điều phối.",
             "du_lieu": deepcopy(self.du_lieu_local() if du_lieu is None else du_lieu),
             "trich_dan": [{"cau": yc["tai_lieu"][m["ai_bat_dau"]:m["ai_ket_thuc"]],
                            "bat_dau": m["ai_bat_dau"], "ket_thuc": m["ai_ket_thuc"]} for m in maps],
             "kiem_trich_dan": {"dat": True, "loi": []}, "nha_cung_cap": "local",
             "model": "DEMO-local-gia", "ly_do_chon_model": "DEMO do Core điều phối, không model thật.",
             "ma_prompt": yc["ma_prompt"], "phien_ban_prompt": yc["phien_ban_prompt"],
             "phien_ban_engine": "e_hoi_ai 0.1.0", "bam_dau_vao": bam(json_chuan(self.pb_ai)),
             "chuyen_tiep": deepcopy(yc["chuyen_tiep"]), "canh_bao": []}
        phieu = deepcopy(self.app.phieu)
        phieu.update(ma="e_demo_local_gia", chay_thu_demo=[], nang_luc=[{
            "ma": "demo.local_gia@1", "ten": "Local giả DEMO", "nhan": ["yeu_cau_ai"], "tra": "tra_loi_ai",
            "gioi_han": {"thoi_han_giay": 30}, "huy_duoc": True}])
        phieu.pop("ngan_du_lieu", None)
        phieu.pop("du_lieu", None)
        phieu.pop("cau_hinh", None)
        local = Engine(phieu, thu_muc_goi=GOI)

        @local.nang_luc("demo.local_gia@1")
        def hoi(viec):
            viec.kiem_huy()
            self.so_luot_local += 1
            return {"loai": "tra_loi_ai", "tra_loi_ai": deepcopy(a)}

        ra = self.core.chay_thu(local, "demo.local_gia@1", self.pb_ai)
        assert ra["trang_thai"] == "XONG", ra
        self.pb_local = ra["ket_qua"]
        return deepcopy(self.pb_local)

    def giao_hau(self, pb=None, *, cap=True, phap_nhan="DEMO-P"):
        pb = deepcopy(self.pb_local if pb is None else pb)
        nl = PHAN_TICH if self.tac_vu == "phan_tich_cau_hoi" else XEP_HANG
        self.hau_id = self.core.giao_viec(nl, pb, {}, phap_nhan_id=phap_nhan)
        c = pb["tra_loi_ai"]["chuyen_tiep"]["tra_cuu"]
        ref = {"tep": c["ho_so"], "bam": c["bam_ho_so"]}
        refs = [*self.refs, ref]
        self.core.tep_duoc_mo[self.hau_id] = {r["tep"]["tep_id"] for r in refs}
        if cap:
            self.core.cua.giay_cap[self.hau_id] = {
                "ma_yeu_cau": c["ma_yeu_cau"], "tac_vu": self.tac_vu, "dau_vao": deepcopy(pb),
                "ngu_canh_core": deepcopy(self.ngu_canh),
                "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in refs},
                "nguon": deepcopy(self.nguon_duoc_cap), "phan_giai_cau_hoi": deepcopy(self.meta),
                "phu_thuoc_thoi_diem": False,
            }
        return self.hau_id

    def hau_kiem(self, pb=None, **kwargs):
        self.giao_hau(pb, **kwargs)
        self.core.chay(self.app)
        return self.core.xem(self.hau_id)

    def doi_snapshot(self, sua):
        s = deepcopy(self.s_ai)
        sua(s)
        ref = self.tai("snapshot-hong-DEMO.json", json_chuan(s))
        pb = deepcopy(self.pb_local)
        c = pb["tra_loi_ai"]["chuyen_tiep"]["tra_cuu"]
        c.update(ho_so=ref["tep"], bam_ho_so=ref["bam"])
        yc = deepcopy(self.pb_ai)
        yc["yeu_cau_ai"]["chuyen_tiep"] = deepcopy(pb["tra_loi_ai"]["chuyen_tiep"])
        pb["tra_loi_ai"]["bam_dau_vao"] = bam(json_chuan(yc))
        return pb


def chay_demo_hau_kiem():
    kq = []
    for ten, ma in (("Câu hỏi VAY-A DEMO", "DEMO-VAY-A"), ("Câu hỏi VAY-B DEMO", "DEMO-VAY-B"),
                    ("Mã giữ 0 đầu DEMO", "0007")):
        bo = BoHauKiem()
        yc = bo.yeu_cau_ai("phan_tich_cau_hoi")
        yc["du_lieu"]["cau_hoi"] = f"Giá trị khoản vay {ma} là bao nhiêu VND?"
        bo.chuan_bi_hau(yc=yc)
        bo.local_gia(bo.du_lieu_local(ma_thuc_the=ma))
        kq.append({"ten": ten, **bo.hau_kiem()})
    bo = BoHauKiem()
    yc = bo.yeu_cau_ai("xep_hang_lai")
    yc["du_lieu"]["ung_vien"].append({**bo.doan(), "ma_ung_vien": "DEMO-UV-2", "diem_tim_kiem": 0.5})
    bo.chuan_bi_hau("xep_hang_lai", yc)
    d = bo.du_lieu_local()
    d["xep_hang"].reverse()
    bo.local_gia(d)
    kq.append({"ten": "Xếp hạng tie giữ toàn nguồn DEMO", **bo.hau_kiem()})
    return kq
