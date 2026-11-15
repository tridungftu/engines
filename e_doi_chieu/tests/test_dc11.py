"""DC-11: đã kiểm bằng Core giả (CoreGia) + NganBoNho, chỉ DEMO, 0 Cloud."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

import pytest
from kho_tri_thuc_sdk.engine import NganXungDot, LoiNghiepVu, ViecDaHuy

from test_dc10 import BoDEMO, CongDEMO, NganRam, trong_viec, bi_loi, GOI, PN, MODULE
from test_dc7 import cap_so, phan_loai, Mau, CoreOCRVungDEMO, dat_tu_dien, DieuPhoiDEMO
from test_dc9 import xuat, chay, hs
from tham_chieu_ngan_0.ngan import NganBoNho, NganXungDot as XungDotRam
from ngan_demo import trong_ngan
from e_doi_chieu import loi_ocr as hoc, tu_dien as td


Q14 = json.loads((Path(__file__).parent/'fixtures/DEMO-tu-dien-dc7.json').read_text(encoding='utf-8'))
# 2 là ngưỡng GIẢ trong test, không phải số đo hoặc mặc định vận hành.
NGUONG = {"so_lan": 2, "phien_ban": "DEMO-do-1", "nguon_do": "DEMO-bang-do-gia", "ma_phe_duyet": "DEMO-duyet-gia"}


class CongHocDEMO(CongDEMO):
    def __init__(self, ma, **kw):
        super().__init__(ma, **kw)
        self.c = replace(self.c, quyen=self.c.quyen + ("de_xuat_loi_ocr", "duyet_loi_ocr", "admin_core"))
        self.q = hoc.BoQ14(deepcopy(Q14), hs.bam(hs.json_bytes(Q14)), "DEMO-Q14-gia", True)

    def cap_ngu_canh(self, viec, ma_luot):
        return replace(self.c, ma_luot=ma_luot)

    def cap_bo_q14(self, viec):
        return self.q


class NganHocRam(NganRam):
    @contextmanager
    def lo(self):
        class Lo:
            def __init__(self, goc): self.goc = goc
            def __getattr__(self, ten): return getattr(self.goc, ten)
            def them(self, bang, value):
                khoa = {"ma_xac_nhan": value["ma_xac_nhan"]} if bang == "xac_nhan" else {"bam_cap_tu": value["bam_cap_tu"]}
                return self.goc.them(bang, khoa, value)
        try:
            with self.n.lo() as lo:
                yield Lo(lo)
        except XungDotRam:
            raise NganXungDot() from None


class BoHocDEMO(BoDEMO):
    def __init__(self, ban="sdk", w="hợp", o="hơp"):
        self.m = Mau(CoreOCRVungDEMO())
        base = deepcopy(Q14)
        base["cap_vo_nghia_co_can_cu"] = []
        dat_tu_dien(self.m, value=base)
        self.m.provider = DieuPhoiDEMO()
        r, s = cap_so(self.m, "DEMO " + w + ".", "DEMO " + o + ".")
        if any(d["cho_phan_loai"] for d in s["diem_lech"]):
            r = phan_loai(self.m, r, s, nhan="khong_chac")
        r = xuat(self.m, r["ket_qua"])
        assert r["trang_thai"] == "XONG", r
        self.ban = ban
        self.cau_hinh = {**deepcopy(chay.app.cau_hinh), "hoc_loi_ocr": deepcopy(NGUONG)}
        self.ma = next(r["ma_luot"] for r in self.m.core.xem_ngan(chay.app.ma, "luot_doi_chieu") if r["trang_thai"] == "da_xuat")
        self.cong = CongHocDEMO(self.ma)
        self.cong.c = replace(self.cong.c, diem_duoc_xac_nhan=tuple(d["ma_diem"] for d in s["diem_lech"]))
        if ban == "ram":
            self.ngan = NganHocRam(NganBoNho(chay.app.phieu["ngan_du_lieu"]).cho_phap_nhan(PN))
            for b in chay.app.phieu["ngan_du_lieu"]:
                for row in self.m.core.xem_ngan(chay.app.ma, b["bang"]):
                    vals = {k: v for k, v in row.items() if k in {t["ma"] for t in b["truong"]}}
                    with self.ngan.n.lo() as lo:
                        lo.them(b["bang"], {k: vals[k] for k in b["khoa"]}, vals)
        self.xn = self.goi(chay.xac_nhan, self.yeu_cau(diem=self.cong.c.diem_duoc_xac_nhan[0]))["ma_xac_nhan"]

    def hoc(self, ham, *a, **kw):
        def goi(viec, *, cong=None):
            return ham(viec, viec.ngan, self.cau_hinh, *a, cong=cong, **kw)
        return self.goi(goi)

    def de_xuat(self):
        return self.hoc(hoc.de_xuat, self.ma, self.xn)

    def doc(self, bang, khoa):
        if self.ban == "ram": return self.ngan.doc(bang, khoa)
        return trong_ngan(self.m, lambda n: n.doc(bang, khoa))

    def ban_de_xuat(self, k):
        b = self.doc("loi_ocr_de_xuat", {"bam_cap_tu": k})
        return b, hoc._noi_dung(b)

    def duyet(self, k, rv=None, ma="DEMO-duyet-1"):
        b, _ = self.ban_de_xuat(k)
        return self.hoc(hoc.duyet, self.ma, k, b.row_version if rv is None else rv, ma)


@pytest.fixture(params=["sdk", "ram"])
def bo(request):
    return BoHocDEMO(request.param)


def test_dem_de_xuat_khong_tu_duyet_gui_lai_khong_dem_hai_lan(bo):
    truoc = bo.view()["bao_cao"]
    kq = bo.de_xuat()
    assert kq["so_lan"] == 1 and kq["trang_thai"] == "cho_nguong"
    b, row = bo.ban_de_xuat(kq["bam_cap_tu"])
    assert bo.de_xuat() == kq
    assert bo.ban_de_xuat(kq["bam_cap_tu"])[0].row_version == b.row_version
    assert bo.view()["bao_cao"] == truoc
    bi_loi("DC_KHONG_DU_CAN_CU", lambda: bo.duyet(kq["bam_cap_tu"]))
    assert not bo.doc("loi_ocr_da_duyet", {"bam_cap_tu": kq["bam_cap_tu"], "phien_ban": "DEMO"})
    # Hai người cùng xác nhận một vị trí vẫn chỉ có một lần gặp.
    bo.cong.c = replace(bo.cong.c, nguoi_id="DEMO-NGUOI-2")
    bo.xn = bo.goi(chay.xac_nhan, bo.yeu_cau(ma="DEMO-xn-2", diem=bo.cong.c.diem_duoc_xac_nhan[0]))["ma_xac_nhan"]
    assert bo.de_xuat() == kq
    assert bo.ban_de_xuat(kq["bam_cap_tu"])[1] == row


def cho_duyet(b):
    # Hạ về 1 CHỈ trong cấu hình DEMO được mock phê duyệt để kiểm luồng duyệt.
    b.cau_hinh["hoc_loi_ocr"]["so_lan"] = 1
    return b.de_xuat()["bam_cap_tu"]


def test_admin_duyet_nguyen_tu_nhat_ky_vo_danh_va_giu_snapshot(bo):
    truoc = bo.view()["bao_cao"]
    k = cho_duyet(bo)
    assert bo.view()["bao_cao"] == truoc
    b, row = bo.ban_de_xuat(k)
    assert row["trang_thai"] == "cho_duyet" and "duyet" not in row
    assert all(d["muc"] != "nhieu_ocr" for d in truoc["diem_lech"])
    res = bo.duyet(k)
    assert res["da_duyet"]
    sau, row = bo.ban_de_xuat(k)
    assert sau.row_version != b.row_version and row["trang_thai"] == "da_duyet"
    assert row["duyet"]["nguoi_id"] == bo.cong.c.nguoi_id and row["duyet"]["luc"] == bo.cong.c.luc
    approved = hoc._noi_dung(bo.doc("loi_ocr_da_duyet", {"bam_cap_tu": k, "phien_ban": res["phien_ban"]}))
    assert td.TuDien(approved, lambda: None).tra("hợp", "hơp")[0] == "vo_nghia_co_can_cu"
    raw = hs.json_bytes(approved).decode()
    for text in (bo.ma, bo.xn, PN, MODULE, bo.cong.c.nguoi_id, bo.cong.c.luc, "DEMO"):
        assert text not in raw
    assert bo.duyet(k, b.row_version) == res
    assert bo.ban_de_xuat(k)[0].row_version == sau.row_version
    assert bo.view()["bao_cao"] == truoc
    assert bo.m.provider.cloud == 0


@pytest.mark.parametrize("quyen", [("xem_doi_chieu", "admin_core"), ("xem_doi_chieu", "duyet_loi_ocr")])
def test_khong_tu_cap_quyen_admin(bo, quyen):
    k = cho_duyet(bo)
    bo.cong.c = replace(bo.cong.c, quyen=quyen)
    bi_loi("DC_KHONG_CO_QUYEN", lambda: bo.duyet(k))
    assert bo.ban_de_xuat(k)[1]["trang_thai"] == "cho_duyet"


@pytest.mark.parametrize("w,o", [cap for a,b in td.CAP_CO_NGHIA for cap in ((a,b),(b,a))])
def test_cap_doi_nghia_khong_duoc_hoc(w,o):
    b = BoHocDEMO(w=w,o=o)
    bi_loi("DC_CAP_DOI_NGHIA", b.de_xuat)
    assert not b.m.core.xem_ngan(chay.app.ma, "loi_ocr_de_xuat")


@pytest.mark.parametrize("thay", [None, {}, {**NGUONG,"so_lan":True}, {**NGUONG,"so_lan":0}, {**NGUONG,"nguon_do":""}, {**NGUONG,"ma_phe_duyet":""}])
def test_khong_bia_nguong(bo, thay):
    bo.cau_hinh["hoc_loi_ocr"] = thay
    bi_loi("DC_KHONG_DU_CAN_CU", bo.de_xuat)


@pytest.mark.parametrize("thay", [{"vo_danh":False}, {"ma_phe_duyet":""}, {"bam":"sha256:"+"0"*64}])
def test_q14_chua_duyet_hoac_khong_vo_danh_khong_hoc(bo, thay):
    bo.cong.q = replace(bo.cong.q, **thay)
    bi_loi("DC_KHONG_DU_CAN_CU", bo.de_xuat)


def test_thieu_cong_va_xac_nhan_tu_khai_khong_hoc(bo):
    cong = bo.cong
    bo.cong = None
    bi_loi("DC_CHUA_CO_CONG_XAC_NHAN", bo.de_xuat)
    bo.cong = cong
    bi_loi("DC_KHONG_DU_CAN_CU", lambda: bo.hoc(hoc.de_xuat, bo.ma, "DEMO-id-tu-khai"))


@pytest.mark.parametrize("truong", ["vung_bao_ve", "quy_tac_trung", "muc_san"])
def test_vung_bao_ve_cung_khong_duoc_hoc(bo, truong):
    s = bo.view()["bao_cao"]
    d = s["diem_lech"][0]
    d[truong] = "nghiem_trong" if truong == "muc_san" else ["DEMO-bao-ve"]
    bi_loi("DC_CAP_DOI_NGHIA", lambda: hoc.kiem_cap(s, d["ma_diem"], td.TuDien(Q14, lambda: None)))


def test_muc_tin_cay_khong_ro_thi_khong_cho_duyet(bo):
    q = deepcopy(Q14); q["cap_vo_nghia_co_can_cu"] = []
    bo.cong.q = replace(bo.cong.q, noi_dung=q, bam=hs.bam(hs.json_bytes(q)))
    bi_loi("DC_KHONG_DU_CAN_CU", bo.de_xuat)


def test_cas_de_xuat_cu_tu_choi(bo):
    k = cho_duyet(bo)
    e = bi_loi("DC_XUNG_DOT", lambda: bo.duyet(k, rv=999))
    assert e.thu_lai_duoc and "DEMO" not in e.thong_diep
    assert bo.ban_de_xuat(k)[1]["trang_thai"] == "cho_duyet"


@pytest.mark.parametrize("bang", ["loi_ocr_de_xuat", "luot_doi_chieu"])
def test_sdk_cas_rollback_trang_thai_bo_duyet_va_nhat_ky(bang):
    b = BoHocDEMO()
    k = cho_duyet(b)
    row, before = b.ban_de_xuat(k)
    b.m.core.gay_xung_dot_ngan(bang)
    bi_loi("DC_XUNG_DOT", lambda: b.duyet(k))
    assert b.ban_de_xuat(k)[1] == before
    assert b.ban_de_xuat(k)[0].row_version == row.row_version
    assert b.m.core.xem_ngan(chay.app.ma, "loi_ocr_da_duyet") == []


def test_mat_ack_sdk_gui_lai_khong_duyet_hai_lan():
    b = BoHocDEMO()
    k = cho_duyet(b)
    b.m.core.gay_mat_xac_nhan("ngan")
    r = b.duyet(k)
    assert b.duyet(k) == r
    assert len(b.m.core.xem_ngan(chay.app.ma, "loi_ocr_da_duyet")) == 1


def test_khac_phap_nhan_khong_doc_de_xuat_va_khong_duyet():
    b = BoHocDEMO()
    k = cho_duyet(b)
    assert trong_ngan(b.m, lambda n: n.doc("loi_ocr_de_xuat", {"bam_cap_tu":k}), "DEMO-P2") is None
    gate = CongHocDEMO(b.ma, phap_nhan_id="DEMO-P2")
    bi_loi("DC_KHONG_DU_CAN_CU", lambda: trong_viec(b.m, lambda v: hoc.duyet(v,v.ngan,b.cau_hinh,b.ma,k,1,"DEMO-y",cong=gate),pn="DEMO-P2"))


def test_mat_quyen_nguon_hoac_xac_nhan_mau_thuan_khong_duyet(bo):
    k = cho_duyet(bo)
    bo.cong.c = replace(bo.cong.c, nguoi_id="DEMO-NGUOI-2")
    bo.goi(chay.xac_nhan, bo.yeu_cau(ma="DEMO-mau-thuan",diem=bo.cong.c.diem_duoc_xac_nhan[0],lua_chon="ban_ky_sai"))
    bi_loi("DC_KHONG_DU_CAN_CU", lambda: bo.duyet(k))


def test_huy_khong_ghi():
    b = BoHocDEMO("ram")
    v = b.viec_ram()
    def huy(): raise ViecDaHuy()
    v.kiem_huy = huy
    with pytest.raises(ViecDaHuy): hoc.de_xuat(v,v.ngan,b.cau_hinh,b.ma,b.xn,cong=b.cong)
    assert not b.ngan.tim("loi_ocr_de_xuat").danh_sach


def test_khong_them_nang_luc_hay_decorator_sdk_gia():
    assert len(chay.app.phieu["nang_luc"]) == 7
    assert "thao_tac_quan_tri" not in chay.app.phieu
    assert not hasattr(chay.app, "thao_tac_quan_tri")
    assert "hoc_loi_ocr" not in chay.app.cau_hinh
    schema = json.loads((GOI/'cau_hinh.schema.json').read_text(encoding='utf-8'))
    assert "default" not in schema["properties"]["hoc_loi_ocr"]


@pytest.mark.parametrize("ban", ["sdk", "ram"])
def test_hai_lan_gap_doc_lap_dat_nguong_nhung_chua_duyet(ban):
    b = BoHocDEMO(ban, w="hợp và hợp", o="hơp và hơp")
    a = b.de_xuat()
    assert a["so_lan"] == 1 and a["trang_thai"] == "cho_nguong"
    diem = b.cong.c.diem_duoc_xac_nhan[1]
    b.xn = b.goi(chay.xac_nhan, b.yeu_cau(ma="DEMO-xn-vi-tri-2",diem=diem))["ma_xac_nhan"]
    c = b.de_xuat()
    assert c["bam_cap_tu"] == a["bam_cap_tu"] and c["so_lan"] == 2 and c["trang_thai"] == "cho_duyet"
    assert b.duyet(a["bam_cap_tu"])["da_duyet"]


def test_mat_quyen_nguon_truoc_duyet():
    b = BoHocDEMO()
    k = cho_duyet(b)
    tid = b.view()["bao_cao"]["nguon"]["ban_ky"]["tep"]["tep_id"]
    b.m.core.cam.add(tid)
    with pytest.raises(LoiNghiepVu): b.duyet(k)
    assert b.ban_de_xuat(k)[1]["trang_thai"] == "cho_duyet"
    assert not b.m.core.xem_ngan(chay.app.ma,"loi_ocr_da_duyet")


def test_thay_nguong_sau_de_xuat_phai_tinh_lai():
    b = BoHocDEMO()
    k = cho_duyet(b)
    b.cau_hinh["hoc_loi_ocr"]["phien_ban"] = "DEMO-do-2"
    bi_loi("DC_KHONG_DU_CAN_CU", lambda: b.duyet(k))
    assert b.de_xuat()["so_lan"] == 1
    assert b.ban_de_xuat(k)[1]["nguong"]["phien_ban"] == "DEMO-do-2"
    assert b.duyet(k)["da_duyet"]


def test_cas_ram_rollback_ca_lo_tai_commit():
    b = BoHocDEMO("ram")
    k = cho_duyet(b)
    before = b.ban_de_xuat(k)
    goc = b.ngan.lo
    @contextmanager
    def tranh():
        # Đối thủ đổi sau khi đã đọc, trước commit lô duyệt.
        with b.ngan.n.lo() as lo:
            lo.sua("loi_ocr_de_xuat", {"bam_cap_tu":k}, {"noi_dung":hs.dong_phong_bi(before[1])},row_version=before[0].row_version)
        with goc() as lo: yield lo
    b.ngan.lo = tranh
    bi_loi("DC_XUNG_DOT", lambda: b.duyet(k))
    assert b.ban_de_xuat(k)[1] == before[1]
    assert not b.ngan.tim("loi_ocr_da_duyet").danh_sach


def test_gioi_han_khong_cat_ngam():
    bi_loi("DC_QUA_GIOI_HAN", lambda: hoc._dong({"DEMO":"D"*65536}))


def test_bo_chung_doc_duoc_o_phap_nhan_khac_nhung_de_xuat_thi_khong():
    b = BoHocDEMO()
    k = cho_duyet(b)
    pb = b.duyet(k)["phien_ban"]
    assert trong_ngan(b.m, lambda n:n.doc("loi_ocr_de_xuat",{"bam_cap_tu":k}), "DEMO-P2") is None
    shared = trong_ngan(b.m, lambda n:n.doc("loi_ocr_da_duyet",{"bam_cap_tu":k,"phien_ban":pb}), "DEMO-P2")
    assert shared is not None and hoc._noi_dung(shared)["pham_vi"] == "engine"


@pytest.mark.parametrize("cung_ma", [False,True])
def test_hai_admin_duyet_dong_thoi_chi_mot_phien_ban(cung_ma):
    b = BoHocDEMO("ram")
    k = cho_duyet(b)
    rv = b.ban_de_xuat(k)[0].row_version
    cong2 = deepcopy(b.cong)
    if not cung_ma: cong2.c = replace(cong2.c,nguoi_id="DEMO-Admin-2")
    barrier = threading.Barrier(2)
    lo_goc = b.ngan.lo
    @contextmanager
    def tranh():
        barrier.wait(timeout=10)
        with lo_goc() as lo: yield lo
    b.ngan.lo = tranh
    def goi(args):
        gate,ma=args
        v=b.viec_ram()
        try: return hoc.duyet(v,v.ngan,b.cau_hinh,b.ma,k,rv,ma,cong=gate)
        except LoiNghiepVu as e: return e.ma
    with ThreadPoolExecutor(2) as pool:
        out=list(pool.map(goi,[(b.cong,"DEMO-y1"),(cong2,"DEMO-y1" if cung_ma else "DEMO-y2")]))
    assert sum(isinstance(v,dict) for v in out) == 1
    assert "DC_XUNG_DOT" in out
    assert len(b.ngan.tim("loi_ocr_da_duyet").danh_sach) == 1
    assert b.ban_de_xuat(k)[1]["trang_thai"] == "da_duyet"


def test_bo_da_co_khong_khop_khong_ghi_de():
    b = BoHocDEMO("ram")
    k = cho_duyet(b)
    row = b.ban_de_xuat(k)[1]
    cap = {t:row[t] for t in ("word","ocr","bam_can_cu")}
    pb = hoc.bo_moi(cap,row["q14"])["phien_ban_bo"]
    with b.ngan.n.lo() as lo:
        lo.them("loi_ocr_da_duyet",{"bam_cap_tu":k,"phien_ban":pb},{"noi_dung":hs.dong_phong_bi({"DEMO":"khong-khop"})})
    bi_loi("DC_XUNG_DOT",lambda:b.duyet(k))
    assert b.ban_de_xuat(k)[1]["trang_thai"] == "cho_duyet"
