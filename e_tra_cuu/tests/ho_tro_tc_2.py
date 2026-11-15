"""C-TC-02/03 giả CHỈ trong tests; quyền cấp ngoài JSON yêu cầu.

Không phải chứng nhận RLS thật. CoreGia 2.0 chỉ mở ID trực tiếp trong phong bì;
bản mở rộng này cấp danh sách tệp con cho từng việc, vẫn dùng Viec.mo_tep thật.
"""

from copy import deepcopy
from pathlib import Path

from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen
from kho_tri_thuc_sdk.thu import CoreGia

from e_tra_cuu import chay
from e_tra_cuu.kiem_dau_vao import bam, json_chuan


GOI = Path(__file__).resolve().parents[1] / "goi/e_tra_cuu"
MA = "tra_cuu.nhan_yeu_cau@1"
NGU_CANH = {"phap_nhan_id": "DEMO-P", "module": "M9", "nhom": ["02"],
            "nguoi_hoi_id": "DEMO-N", "ma_pham_vi": "DEMO-PV",
            "thoi_diem": "2026-11-15T12:51:00+07:00"}


class CuaNguonGia:
    def __init__(self):
        self.giay_cap = {}

    def doc_quyen(self, viec_id):
        return deepcopy(self.giay_cap.get(viec_id))


class CoreGiaTepCon(CoreGia):
    def __init__(self):
        super().__init__()
        self.cua = CuaNguonGia()
        self.tep_duoc_mo = {}
        self.luot_doc = []
        self.sau_doc = None

    def _mo_tep(self, ma, viec_id, tep_id, toi_da_byte):
        with self._lock:
            self._dang_giu(ma, viec_id)
            if tep_id not in self.tep_duoc_mo.get(viec_id, set()):
                raise LoiDuongTruyen("KHONG_DU_QUYEN", http_status=403)
            b = self.doc_tep(tep_id)
            if len(b) > toi_da_byte:
                raise LoiDuongTruyen("VUOT_GIOI_HAN_KICH_THUOC", http_status=413)
            self.luot_doc.append((viec_id, tep_id, len(b)))
            if self.sau_doc:
                self.sau_doc(viec_id, tep_id)
            return b


class BoDemo:
    def __init__(self, *, noi_dung_goc=None, van_ban=None, core=None, thu_muc_demo=None):
        self.core = core or CoreGiaTepCon()
        self.refs = []
        self.thu_muc_demo = thu_muc_demo
        self.van_ban = van_ban if van_ban is not None else (
            "Công ty DEMO Ánh Dương\nHợp đồng DEMO-VAY-A.\n"
            "Giá trị 1.000.000 VND, ngày 2026-10-30."
        )
        self.goc = self.tai("nguon-DEMO.txt", noi_dung_goc if noi_dung_goc is not None
                            else self.van_ban.encode("utf-8"), "text/plain")
        self.pb_vb = {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {
            "phien_ban": 1, "van_ban": self.van_ban, "so_trang": 0, "trang": [],
            "nguon_doc": "docx", "ly_do_chuyen_nguon": None,
            "phien_ban_engine": "e_ocr 0.1.0", "bam_dau_vao": self.goc["bam"], "canh_bao": [],
        }}
        self.vb = self.tai("van-ban-DEMO.json", json_chuan(self.pb_vb))
        self.danh_muc = {
            "nhom": [{"ma": f"{i:02}", "ten": "Nhóm DEMO " + str(i)} for i in range(1, 9)],
            "loai": [{"ma": "DEMO-LOAI", "ten": "Loại DEMO", "nhom": "02", "trang_thai": "hoat_dong"}],
            "loai_hinh_phap_nhan": [{"ma": "CP", "ten": "Cổ phần DEMO"}, {"ma": "TNHH", "ten": "TNHH DEMO"}],
            "doi_tuong": [{"ma": "DEMO-VAY-A", "ten": "Khoản vay DEMO A"}],
        }
        self.dm = self.tai("danh-muc-DEMO.json", json_chuan(self.danh_muc))
        self.tai_lieu = {"ma_nguon": "DEMO-NGUON-1", "phien_ban_nguon": "1", "goc": self.goc, "van_ban": self.vb}
        self.nguon = {"ma_nguon": "DEMO-NGUON-1", "phien_ban_nguon": "1", "tep_id": self.goc["tep"]["tep_id"],
                      "bam_goc": self.goc["bam"], "bam_van_ban": bam(self.van_ban.encode("utf-8"))}
        self.nguon_duoc_cap = {self.nguon["ma_nguon"]: deepcopy(self.nguon)}
        self.cau_hinh = {"phien_ban": 1, "quy_tac_nhom": {"tep_id": self.dm["tep"]["tep_id"], "bam": self.dm["bam"]}}
        self.app = Engine(deepcopy(chay.app.phieu), thu_muc_goi=GOI)
        self.core.nap_engine(self.app)
        self.core.dat_cau_hinh(self.app.ma, self.cau_hinh)
        self.app.cua_nguon = self.core.cua
        chay.dang_ky_nang_luc(self.app)
        self.viec_id = None

    def tai(self, ten, b, mime="application/json"):
        if self.thu_muc_demo is not None and (self.thu_muc_demo / ten).is_file():
            b_demo = (self.thu_muc_demo / ten).read_bytes()
            assert b_demo == b, "Tệp DEMO và nguồn fixture không khớp."
            b = b_demo
        tep = self.core.them_tep(ten, b, mime)
        ref = {"tep": tep, "bam": bam(b)}
        self.refs.append(ref)
        return deepcopy(ref)

    def cau_hoi(self):
        return "Giá trị hợp đồng DEMO-VAY-A là bao nhiêu VND?"

    def thuc_the(self):
        return [{"loai": "khoan_vay", "ma": "DEMO-VAY-A", "gia_tri": "DEMO-VAY-A"}]

    def doan(self):
        return {"ma_nguon": self.nguon["ma_nguon"], "phien_ban_nguon": "1",
                "bam_goc": self.nguon["bam_goc"], "bam_van_ban": self.nguon["bam_van_ban"],
                "nguyen_van": self.van_ban, "bat_dau": 0, "ket_thuc": len(self.van_ban),
                "vi_tri": {"trang": None, "hop": None}}

    def yeu_cau(self, tac_vu="cat_doan"):
        if tac_vu == "phan_loai":
            d = {"tai_lieu": self.tai_lieu, "danh_muc": self.dm,
                 "phan_loai_cu": None, "quan_he_phu_luc": None}
        elif tac_vu == "cat_doan":
            d = {"tai_lieu": self.tai_lieu, "metadata_core": {"nhom": "02", "loai": "DEMO-LOAI",
                 "trang_thai_duyet": "cho_duyet", "con_hieu_luc": True}}
        elif tac_vu == "phan_tich_cau_hoi":
            d = {"cau_hoi": self.cau_hoi(), "ham": [{"ten": "m9.gia_tri", "phien_ban": "1",
                "mo_ta": "Lấy giá trị khoản vay DEMO chỉ đọc.",
                "schema_tham_so": {"type": "object", "properties": {"ma_khoan_vay": {"type": "string"}}},
                "schema_dau_ra": {"type": "object"}, "gioi_han": {"so_dong": 1}, "quyen": {"nhom": "02"}}]}
        elif tac_vu == "xep_hang_lai":
            d = {"cau_hoi": self.cau_hoi(), "thuc_the": self.thuc_the(), "nguon": [self.tai_lieu],
                 "ung_vien": [{**self.doan(), "ma_ung_vien": "DEMO-UV-1", "diem_tim_kiem": 0.8}],
                 "thang_diem": {"toi_thieu": 0, "toi_da": 1}}
        else:
            d = {"cau_hoi": self.cau_hoi(), "thuc_the": self.thuc_the(), "tang": 1,
                "bang_chung": [{"nguon": self.nguon, "thuc_the": self.thuc_the()[0], "truong": "gia_tri",
                    "kieu": "so_tien", "gia_tri": {"so": 1000000, "tien_te": "VND"}, "don_vi": "VND",
                    "trang_thai_duyet": "da_duyet", "con_hieu_luc": True, "do_tin_cay": 0.95,
                    "moc_cong_bo": NGU_CANH["thoi_diem"]}],
                "co_van_ban_moi_cho_duyet": False, "phu_thuoc_cache": [{"nguon": self.nguon,
                    "thuc_the": self.thuc_the()[0], "trang_thai_duyet": "da_duyet", "moc_cong_bo": NGU_CANH["thoi_diem"],
                    "ma_pham_vi": "DEMO-PV", "phu_thuoc_thoi_diem": False}]}
        return deepcopy({"phien_ban": 1, "ma_yeu_cau": "DEMO-YC-" + tac_vu,
                         "tac_vu": tac_vu, "ngu_canh_core": NGU_CANH, "du_lieu": d})

    def giao(self, yc=None, *, b=None, bam_yeu_cau=None, phap_nhan="DEMO-P", cap=True):
        yc = self.yeu_cau() if yc is None else yc
        ref = self.tai("yeu-cau-DEMO.json", json_chuan(yc) if b is None else b)
        self.viec_id = self.core.giao_viec(MA, {"loai": "tep", "tep": ref["tep"]},
            {"bam_yeu_cau": bam_yeu_cau or ref["bam"]}, phap_nhan_id=phap_nhan)
        self.cap(self.viec_id, yc, ref, cap=cap)
        return self.viec_id

    def cap(self, viec_id, yc, ref, *, cap=True):
        self.core.tep_duoc_mo[viec_id] = {r["tep"]["tep_id"] for r in self.refs}
        if cap:
            self.core.cua.giay_cap[viec_id] = {
                "ma_yeu_cau": yc["ma_yeu_cau"], "tac_vu": yc["tac_vu"], "bam_yeu_cau": ref["bam"],
                "ngu_canh_core": deepcopy(NGU_CANH),
                "tep": {r["tep"]["tep_id"]: deepcopy(r) for r in self.refs},
                "nguon": deepcopy(self.nguon_duoc_cap),
            }

    def chay(self, *args, **kwargs):
        self.giao(*args, **kwargs)
        self.core.chay(self.app)
        return self.core.xem(self.viec_id)

    def snapshot(self, kq):
        import json
        h = kq["ket_qua"]["ho_so_tra_cuu"]
        b = self.core.doc_tep(h["ho_so"]["tep_id"])
        assert len(b) == h["ho_so"]["kich_thuoc"] and bam(b) == h["bam_ho_so"]
        return json.loads(b)
