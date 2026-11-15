"""DC-10: đã kiểm bằng Core giả (CoreGia), RAM; không chứng minh nhật ký bền."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import io
import json
from pathlib import Path
import threading
from types import SimpleNamespace

import pytest
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, NganXungDot, ChuaRo, ViecDaHuy

from test_dc9 import mau_day_du, diem_demo, ghim_demo, xuat, chay, hs

import e_doi_chieu.xac_nhan as xn
from tham_chieu_ngan_0.ngan import NganBoNho, NganXungDot as XungDotRam

GOI = Path(__file__).resolve().parents[1] / "goi/e_doi_chieu"
PN, MODULE = "DEMO-P", "DEMO-module"


class CongDEMO:
    """Mock Core giữ danh tính/quyền/đồng hồ ngoài payload UI."""
    def __init__(self, luot, **kw):
        self.c = xn.NguCanhXacNhan(PN, MODULE, luot, "DEMO-NGUOI-1", "Người phụ trách DEMO",
            "2026-11-15T13:15:00+00:00", ("xem_doi_chieu", "xac_nhan_doi_chieu", "gui_yeu_cau_module"),
            ("DEMO-1", "DEMO-2", "DEMO-V1"))
        self.c = replace(self.c, **kw)
        self.gui = []

    def cap_ngu_canh(self, viec, ma_luot):
        return self.c

    def gui_yeu_cau_module(self, viec, yeu_cau):
        self.gui.append(deepcopy(yeu_cau))
        return {"da_nhan": True}


class NganRam:
    """Chuẩn hóa ngoại lệ RAM sang SDK ở phía test, không sửa mẫu NGAN-0."""
    def __init__(self, n):
        self.n = n

    def __getattr__(self, ten):
        return getattr(self.n, ten)

    @contextmanager
    def lo(self):
        class Lo:
            def __init__(self, goc):
                self.goc = goc

            def __getattr__(self, ten):
                return getattr(self.goc, ten)

            def them(self, bang, gia_tri):
                return self.goc.them(bang, {"ma_xac_nhan": gia_tri["ma_xac_nhan"]}, gia_tri)
        try:
            with self.n.lo() as lo:
                yield Lo(lo)
        except XungDotRam:
            raise NganXungDot() from None


def trong_viec(m, ham, pn=PN):
    phieu = deepcopy(m.app.phieu)
    phieu["nang_luc"] = [{"ma": "demo.xac_nhan@1", "ten": "Xác nhận DEMO", "nhan": ["van_ban"],
        "tra": "van_ban", "gioi_han": {"thoi_han_giay": 30}}]
    phieu["chay_thu_demo"] = []
    app = Engine(phieu, thu_muc_goi=m.app.thu_muc_goi)
    kq, loi = [], []

    @app.nang_luc("demo.xac_nhan@1")
    def xu_ly(viec):
        try:
            kq.append(ham(viec))
        except Exception as exc:
            loi.append(exc)
        return {"loai": "van_ban", "van_ban": "DEMO"}

    vid = m.core.giao_viec("demo.xac_nhan@1", {"loai": "van_ban", "van_ban": "DEMO"}, phap_nhan_id=pn)
    m.core.cap[vid] = set(m.refs)
    m.core.chay(app)
    assert m.core.xem(vid)["trang_thai"] == "XONG"
    if loi:
        raise loi[0]
    return kq[0]


class BoDEMO:
    def __init__(self, ban="sdk", *, thieu=False, vung=False):
        self.m, s = mau_day_du()
        s["diem_lech"] = [diem_demo(s, "nghiem_trong", 1), diem_demo(s, "can_xem", 2)]
        if thieu:
            s["kiem_tra"]["sua_tay"] = "chua_kiem"
        if vung:
            ref = s["anh_trang"][0]
            s["vung_sua_tay"] = [{"ma": "DEMO-V1", "muc": "nghiem_trong", "muc_san": "nghiem_trong",
                "so_trang": 1, "hop": [0, 0, 2, 2], "chu_tay": None, "anh_cat": ref["tep"], "bam_anh_cat": ref["bam"]}]
        r = xuat(self.m, ghim_demo(self.m, s))
        assert r["trang_thai"] == "XONG", r
        self.ban = ban
        self.cau_hinh = deepcopy(chay.app.cau_hinh)
        luot = next(r for r in self.m.core.xem_ngan(chay.app.ma, "luot_doi_chieu") if r["trang_thai"] == "da_xuat")
        self.ma = luot["ma_luot"]
        self.cong = CongDEMO(self.ma)
        if ban == "ram":
            goc = NganBoNho(chay.app.phieu["ngan_du_lieu"])
            n = goc.cho_phap_nhan(PN)
            for bang in chay.app.phieu["ngan_du_lieu"]:
                for row in self.m.core.xem_ngan(chay.app.ma, bang["bang"]):
                    vals = {k: v for k, v in row.items() if k in {t["ma"] for t in bang["truong"]}}
                    with n.lo() as lo:
                        lo.them(bang["bang"], {k: vals[k] for k in bang["khoa"]}, vals)
            self.ngan = NganRam(n)

    def viec_ram(self):
        def mo(tid):
            if tid in self.m.core.cam or self.m.core.chu_tep.get(tid) != (PN, MODULE):
                raise LoiNghiepVu("DC_SAI_NGUON", "Không được cấp nguồn DEMO.")
            return io.BytesIO(self.m.core.doc_tep(tid))
        return SimpleNamespace(ngan=self.ngan, cau_hinh=self.cau_hinh, ngu_canh={"phap_nhan_id": PN, "module": MODULE},
            kiem_huy=lambda: None, mo_tep=mo)

    def goi(self, ham, *a, **kw):
        if "cong" not in kw:
            kw["cong"] = self.cong
        if self.ban == "sdk":
            return trong_viec(self.m, lambda v: ham(v, *a, **kw))
        return ham(self.viec_ram(), *a, **kw)

    def view(self):
        return self.goi(chay.doc_ket_qua, self.ma)

    def yeu_cau(self, ma="DEMO-REQ-1", diem="DEMO-1", lua_chon="loi_ocr", **kw):
        return {"ma_luot": self.ma, "row_version": self.view()["row_version"], "ma_yeu_cau": ma, "ma_diem": diem,
                "lua_chon": lua_chon, "noi_dung_dung": "DEMO nội dung đúng" if lua_chon == "thay_doi_da_thong_nhat" else "",
                "ly_do": "DEMO lý do không ảnh hưởng" if lua_chon == "khong_anh_huong" else "", **kw}


@pytest.fixture(params=["sdk", "ram"])
def bo(request):
    return BoDEMO(request.param)


def bi_loi(ma, ham):
    with pytest.raises(LoiNghiepVu) as e:
        ham()
    assert e.value.ma == ma
    return e.value


def test_mau_ngan_0_nguyen_ban_lf_va_khai_man_khong_vao_manifest():
    for ten in ("ngan.py", "cau_hinh.py"):
        a = (GOI / "tham_chieu_ngan_0" / ten).read_bytes().replace(b"\r\n", b"\n")
        b = (GOI.parents[2] / "_chung/mau-ma" / ten).read_bytes().replace(b"\r\n", b"\n")
        assert sha256(a).digest() == sha256(b).digest()
    assert "giao_dien_quan_tri" not in chay.app.phieu
    assert not any("xac_nhan" in n["ma"] for n in chay.app.phieu["nang_luc"])


@pytest.mark.parametrize("lua_chon", xn.LUA_CHON)
def test_bon_lua_chon_nhat_ky_tin_cay_va_khong_doi_ket_qua_may(bo, lua_chon):
    truoc = bo.view()
    y = bo.yeu_cau(lua_chon=lua_chon)
    assert bo.goi(chay.xac_nhan, y)["da_luu"] is True
    sau = bo.view()
    assert sau["row_version"] != truoc["row_version"]
    assert sau["bao_cao"] == truoc["bao_cao"]
    row, = sau["xac_nhan"]
    assert (row["lua_chon"], row["nguoi_id"], row["luc"]) == (lua_chon, bo.cong.c.nguoi_id, bo.cong.c.luc)
    assert not bo.cong.gui


@pytest.mark.parametrize("thay", [
    {"lua_chon": "tu_mo_chan"}, {"lua_chon": "thay_doi_da_thong_nhat", "noi_dung_dung": " "},
    {"lua_chon": "khong_anh_huong", "ly_do": " "}, {"nguoi_id": "DEMO-Admin"},
    {"luc": "2026-11-15T00:00:00Z"}, {"quyen": ["admin_core"]}, {"row_version": True},
    {"ma_diem": "DEMO-khong-co"}, {"noi_dung_dung": "D"*4001},
])
def test_dau_vao_sai_khong_ghi(bo, thay):
    if thay.get("ma_diem"):
        bo.cong.c = replace(bo.cong.c, diem_duoc_xac_nhan=(*bo.cong.c.diem_duoc_xac_nhan, thay["ma_diem"]))
    bi_loi("DC_SAI_XAC_NHAN", lambda: bo.goi(chay.xac_nhan, bo.yeu_cau(**thay)))
    assert bo.view()["xac_nhan"] == []


def test_khong_co_cua_khong_co_quyen_khac_phap_nhan(bo):
    y = bo.yeu_cau()
    bi_loi("DC_CHUA_CO_CONG_XAC_NHAN", lambda: bo.goi(chay.xac_nhan, y, cong=None))
    for thay in ({"quyen": ("xem_doi_chieu",)}, {"phap_nhan_id": "DEMO-P2"},
                 {"module": "DEMO-module-khac"}, {"ma_luot": "DEMO-luot-khac"}, {"diem_duoc_xac_nhan": ()},
                 {"quyen": "khong_xac_nhan_doi_chieu"}, {"diem_duoc_xac_nhan": "DEMO-1"},
                 {"luc": "2026-11-15T13:15:00"}, {"luc": "khong-phai-gio"}):
        bi_loi("DC_KHONG_CO_QUYEN", lambda: bo.goi(chay.xac_nhan, y, cong=CongDEMO(bo.ma, **thay)))
    assert bo.view()["xac_nhan"] == []


def test_cas_xung_dot_rollback_ca_nhat_ky(bo):
    y = bo.yeu_cau()
    bo.goi(chay.xac_nhan, bo.yeu_cau(ma="DEMO-khac", diem="DEMO-2"))
    e = bi_loi("DC_XUNG_DOT", lambda: bo.goi(chay.xac_nhan, y))
    assert e.thu_lai_duoc is True and e.thong_diep == "Kết quả vừa thay đổi. Anh tải lại trước khi xác nhận."
    assert [r["ma_yeu_cau"] for r in bo.view()["xac_nhan"]] == ["DEMO-khac"]


def test_gui_lai_cung_ma_khong_nhan_doi_va_khong_dung_cho_nguoi_khac(bo):
    y = bo.yeu_cau()
    a = bo.goi(chay.xac_nhan, y)
    rv = bo.view()["row_version"]
    assert bo.goi(chay.xac_nhan, y) == a
    assert bo.view()["row_version"] == rv and len(bo.view()["xac_nhan"]) == 1
    bi_loi("DC_TRUNG_YEU_CAU", lambda: bo.goi(chay.xac_nhan, {**y, "lua_chon": "ban_ky_sai"}))
    bi_loi("DC_TRUNG_YEU_CAU", lambda: bo.goi(chay.xac_nhan, y, cong=CongDEMO(bo.ma, nguoi_id="DEMO-NGUOI-2")))


def test_hai_nguoi_duyet_khac_nguoi_dung_tham_quyen(bo):
    bo.goi(chay.xac_nhan, bo.yeu_cau(lua_chon="thay_doi_da_thong_nhat"))
    bo.goi(chay.xac_nhan, bo.yeu_cau(ma="DEMO-r2", diem="DEMO-2"))
    assert not bo.view()["dieu_kien_module"]["du_dieu_kien_de_nghi"]
    bi_loi("DC_DA_XAC_NHAN", lambda: bo.goi(chay.xac_nhan,
        bo.yeu_cau(ma="DEMO-r3", lua_chon="thay_doi_da_thong_nhat"),
        cong=CongDEMO(bo.ma, quyen=bo.cong.c.quyen + ("duyet_thay_doi_nghiem_trong",))))
    # Người thứ hai chưa có thẩm quyền: ghi lời xác nhận nhưng chưa đủ hai cấp.
    bo.goi(chay.xac_nhan, bo.yeu_cau(ma="DEMO-r4", lua_chon="thay_doi_da_thong_nhat"),
           cong=CongDEMO(bo.ma, nguoi_id="DEMO-NGUOI-2"))
    assert not bo.view()["dieu_kien_module"]["du_dieu_kien_de_nghi"]
    bo.goi(chay.xac_nhan, bo.yeu_cau(ma="DEMO-r5", lua_chon="thay_doi_da_thong_nhat"),
           cong=CongDEMO(bo.ma, nguoi_id="DEMO-NGUOI-3", quyen=bo.cong.c.quyen + ("duyet_thay_doi_nghiem_trong",)))
    assert bo.view()["dieu_kien_module"]["du_dieu_kien_de_nghi"]


@pytest.mark.parametrize("thieu,ban_sai,mau_thuan,vung", [(True, False, False, False), (False, True, False, False),
    (False, False, True, False), (False, False, False, True), (False, False, False, False)])
def test_dieu_kien_chan_va_gui_qua_module(thieu, ban_sai, mau_thuan, vung):
    b = BoDEMO(thieu=thieu, vung=vung)
    b.goi(chay.xac_nhan, b.yeu_cau(lua_chon="ban_ky_sai" if ban_sai else "loi_ocr"))
    b.goi(chay.xac_nhan, b.yeu_cau(ma="DEMO-r2", diem="DEMO-2"))
    if mau_thuan:
        b.goi(chay.xac_nhan, b.yeu_cau(ma="DEMO-r3", lua_chon="khong_anh_huong"),
              cong=CongDEMO(b.ma, nguoi_id="DEMO-NGUOI-2"))
    view = b.view()
    du = not any((thieu, ban_sai, mau_thuan, vung))
    assert view["dieu_kien_module"]["du_dieu_kien_de_nghi"] is du
    assert b.goi(chay.gui_yeu_cau_module, b.ma)["da_nhan"] is True
    assert b.cong.gui[-1]["nguoi_nhan"] == "nguoi_nop_va_nguoi_phu_trach"
    assert b.cong.gui[-1]["dieu_kien"]["du_dieu_kien_de_nghi"] is du
    assert "mo_chan" not in b.cong.gui[-1]
    # Bản ký sai vẫn giữ nguyên sau người khác xác nhận lỗi OCR.
    if ban_sai:
        b.goi(chay.xac_nhan, b.yeu_cau(ma="DEMO-r4"), cong=CongDEMO(b.ma, nguoi_id="DEMO-NGUOI-2"))
        assert not b.view()["dieu_kien_module"]["du_dieu_kien_de_nghi"]


@pytest.mark.parametrize("cung_ma", [False, True])
def test_hai_xac_nhan_thuc_su_dong_thoi_ram(cung_ma):
    b = BoDEMO("ram")
    y = b.yeu_cau()
    y2 = y if cung_ma else b.yeu_cau(ma="DEMO-r2")
    cong2 = b.cong if cung_ma else CongDEMO(b.ma, nguoi_id="DEMO-NGUOI-2")
    barrier = threading.Barrier(2)
    lo_goc = b.ngan.lo

    @contextmanager
    def tranh():
        barrier.wait(timeout=10)
        with lo_goc() as lo:
            yield lo

    b.ngan.lo = tranh
    def goi(args):
        y, gate = args
        try:
            return b.goi(chay.xac_nhan, y, cong=gate)
        except LoiNghiepVu as e:
            return e.ma
    with ThreadPoolExecutor(2) as pool:
        a, c = list(pool.map(goi, [(y, b.cong), (y2, cong2)]))
    rows = b.view()["xac_nhan"]
    assert len(rows) == 1
    if cung_ma:
        assert a == c and a["da_luu"]
    else:
        assert sorted(type(v).__name__ for v in (a, c)) == ["dict", "str"]
        assert "DC_XUNG_DOT" in (a, c)
        b.ngan.lo = lo_goc
        con_lai = cong2 if rows[0]["nguoi_id"] == b.cong.c.nguoi_id else b.cong
        b.goi(chay.xac_nhan, b.yeu_cau(ma="DEMO-r3"), cong=con_lai)
        assert len(b.view()["xac_nhan"]) == 2
        assert len({r["nguoi_id"] for r in b.view()["xac_nhan"]}) == 2


def test_ngan_sdk_xung_dot_tai_commit_khong_ghi_do_dang():
    b = BoDEMO()
    y = b.yeu_cau()
    b.m.core.gay_xung_dot_ngan("luot_doi_chieu")
    bi_loi("DC_XUNG_DOT", lambda: b.goi(chay.xac_nhan, y))
    assert b.view()["xac_nhan"] == []


def test_gui_lai_mat_ack_ngan_sdk_khong_nhan_doi():
    b = BoDEMO()
    y = b.yeu_cau()
    b.m.core.gay_mat_xac_nhan("ngan")
    assert b.goi(chay.xac_nhan, y)["da_luu"]
    assert len(b.view()["xac_nhan"]) == 1


def test_mat_quyen_bao_cao_cu_khong_duoc_gui_lai():
    b = BoDEMO()
    y = b.yeu_cau()
    b.goi(chay.xac_nhan, y)
    b.m.core.cam.add(b.view()["bao_cao"]["bao_cao_pdf"]["tep"]["tep_id"])
    with pytest.raises(LoiNghiepVu):
        b.goi(chay.xac_nhan, y)
    assert len(b.m.core.xem_ngan(chay.app.ma, "xac_nhan")) == 1


def test_cua_module_thieu_va_chua_ro_khong_bao_da_nhan():
    b = BoDEMO()
    bi_loi("DC_CHUA_CO_CONG_MODULE", lambda: b.goi(chay.gui_yeu_cau_module, b.ma, cong=None))
    b.cong.gui_yeu_cau_module = lambda *a: None
    with pytest.raises(ChuaRo):
        b.goi(chay.gui_yeu_cau_module, b.ma)


def test_khac_phap_nhan_doc_ngan_thuc_khong_thay_luot():
    b = BoDEMO()
    gate = CongDEMO(b.ma, phap_nhan_id="DEMO-P2")
    bi_loi("DC_SAI_NGUON", lambda: trong_viec(b.m, lambda v: chay.doc_ket_qua(v, b.ma, cong=gate), pn="DEMO-P2"))
