"""Điều phối CoreGia giữa nhận → chuẩn bị → Hỏi AI, chỉ DEMO."""

from copy import deepcopy
from pathlib import Path
import sys

from kho_tri_thuc_sdk.engine import ChuaRo, Engine

from e_tra_cuu.kiem_dau_vao import bam, doc_json, json_chuan
from ho_tro_tc_2 import GOI, NGU_CANH
from ho_tro_tc_3 import BoCatDoan


CHUAN_BI = "tra_cuu.chuan_bi_ai@1"
TAC_VU = ("phan_loai", "phan_tich_cau_hoi", "xep_hang_lai", "soan_tra_loi")
THAM_SO = {"ma_prompt": "demo.tra_cuu", "phien_ban_prompt": "DEMO-1",
           "prompt": "DEMO: Đề xuất theo tác vụ và khuôn, dẫn chứng nguyên văn; thiếu thì để trống.",
           "model_uu_tien": "DEMO-model-local"}


class BoAI(BoCatDoan):
    def yeu_cau_ai(self, tac_vu):
        yc = self.yeu_cau(tac_vu)
        if tac_vu == "soan_tra_loi":
            # Tầng 1 dùng Python; DEMO AI có nguồn/đoạn thật cho tầng 2.
            yc["du_lieu"].update(tang=2, bang_chung=[self.doan()], nguon=[self.tai_lieu])
        return yc

    def nhan_ai(self, tac_vu="phan_loai", yc=None):
        self.tac_vu = tac_vu
        return self.nhan(self.yeu_cau_ai(tac_vu) if yc is None else yc)

    def giao_ai(self, pb=None, *, ts=None, cap=True, phap_nhan="DEMO-P"):
        pb = deepcopy(self.pb_nhan if pb is None else pb)
        ts = {**THAM_SO, "tac_vu": self.tac_vu} if ts is None else ts
        self.ai_id = self.core.giao_viec(CHUAN_BI, pb, deepcopy(ts), phap_nhan_id=phap_nhan)
        h = pb["ho_so_tra_cuu"]
        ref = {"tep": h["ho_so"], "bam": h["bam_ho_so"]}
        self.core.tep_duoc_mo[self.ai_id] = {r["tep"]["tep_id"] for r in [*self.refs, ref]}
        if cap:
            self.core.cua.giay_cap[self.ai_id] = {
                "ma_yeu_cau": h["ma_yeu_cau"], "tac_vu": h["tac_vu"], "dau_vao": deepcopy(pb),
                "ngu_canh_core": deepcopy(NGU_CANH),
                "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in [*self.refs, ref]},
                "nguon": deepcopy(self.nguon_duoc_cap),
            }
        return self.ai_id

    def chuan_bi(self, pb=None, **kwargs):
        self.giao_ai(pb, **kwargs)
        self.core.chay(self.app)
        return self.core.xem(self.ai_id)

    def snapshot_ai(self, kq):
        ai = kq["ket_qua"]["yeu_cau_ai"]
        ct = ai["chuyen_tiep"]["tra_cuu"]
        b = self.core.doc_tep(ct["ho_so"]["tep_id"])
        assert len(b) == ct["ho_so"]["kich_thuoc"] and bam(b) == ct["bam_ho_so"]
        return doc_json(b)


def nap_hoi_ai():
    """Chỉ test thêm gói consumer có thật; engine TC không import engine khác."""
    goi_ai = GOI.parents[2] / "e_hoi_ai/goi/e_hoi_ai"
    if str(goi_ai) not in sys.path:
        sys.path.insert(0, str(goi_ai))
    from e_hoi_ai.hoi_yeu_cau import goi_theo_yeu_cau
    from e_hoi_ai.khuon_json import khop, kiem_khuon
    from e_hoi_ai.ngan import NganBoNho
    return goi_ai, goi_theo_yeu_cau, khop, kiem_khuon, NganBoNho


class LocalGia:
    def __init__(self, du_lieu, *, chua_ro=False):
        self.du_lieu = du_lieu
        self.chua_ro = chua_ro
        self.so_luot = 0
        self.prompts = []

    def hoi(self, cau_hinh, model, prompt, *, kiem_huy, khuon):
        kiem_huy()
        self.so_luot += 1
        self.prompts.append(prompt)
        if self.chua_ro:
            raise ChuaRo("DEMO-tuong-quan-local")
        # Quote rộng chỉ để kiểm dây chuyển tiếp AI-2; TC hậu kiểm vẫn phải
        # loại nhãn kỹ thuật. Không lấy XONG AI-2 làm chứng nhận nghiệp vụ TC.
        return json_chuan({"du_lieu": self.du_lieu,
                           "truong": [{"ten": "DEMO", "gia_tri": "DEMO", "trich_dan": self.tai_lieu}]}).decode("utf-8")


def dieu_phoi_hoi_ai(bo, pb, du_lieu, *, chua_ro=False):
    goi_ai, goi, _, _, NganBoNho = nap_hoi_ai()
    phieu = doc_json((goi_ai / "engine.json").read_bytes())
    # App kiểm riêng năng lực AI-2 nguyên khai báo; không đăng ký thành công giả
    # cho các năng lực Hỏi AI ngoài phạm vi chuỗi này.
    phieu["nang_luc"] = [n for n in phieu["nang_luc"] if n["ma"] == "ai.hoi_theo_yeu_cau@1"]
    phieu["chay_thu_demo"] = []
    app_ai = Engine(phieu, thu_muc_goi=goi_ai)
    ngan = NganBoNho()
    with ngan.lo() as lo:
        lo.them("cau_hinh", {}, {"local_ai": {"url": "http://127.0.0.1:1", "timeout_giay": 2},
                                 "quy_tac_model": []})
    local = LocalGia(du_lieu, chua_ro=chua_ro)
    local.tai_lieu = pb["yeu_cau_ai"]["tai_lieu"]

    class CongGia:
        nha_cung_cap = {"local": local}  # Không tạo provider Cloud.
        def chon_model(self, yc, cau_hinh, **kwargs):
            kwargs["kiem_huy"]()
            return "DEMO-model-local", "DEMO-do-Core-dieu-phoi"

    @app_ai.nang_luc("ai.hoi_theo_yeu_cau@1")
    def hoi(viec):
        viec.ngan = ngan
        return goi(viec, CongGia(), phien_ban=app_ai.phien_ban)

    kq = bo.core.chay_thu(app_ai, "ai.hoi_theo_yeu_cau@1", deepcopy(pb))
    return kq, local


def chay_demo_ai():
    kq = []
    for tac_vu in TAC_VU:
        bo = BoAI(thu_muc_demo=GOI / "demo")
        bo.nhan_ai(tac_vu)
        ra = bo.chuan_bi()
        if ra["trang_thai"] == "XONG":
            s = bo.snapshot_ai(ra)
            assert s["giai_doan"] == "cho_ai"
            assert s["ai"]["ngan_sach"]["token_thuc"] is None
        kq.append({"ten": "Chuẩn bị AI DEMO — " + tac_vu, **ra})
    return kq
