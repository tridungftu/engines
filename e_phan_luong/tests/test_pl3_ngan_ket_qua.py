"""PL-3 đã kiểm bằng Core giả (CoreGia), chỉ dữ liệu DEMO trong RAM.

CLI SDK 2.2.0 chạy từng chay_thu_demo độc lập, không nối mã lượt động.
PL-2 ghép chưa có trên nhánh này: fixture ghi đủ luot/dong_luot qua
viec.ngan, không giả một ví dụ ghi_ket_qua trong engine.json.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
import json
from threading import Barrier, Event, Lock, local

import pytest
from kho_tri_thuc_sdk.engine import Engine as EngineSDK
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import __version__, doi_bac, ket_qua, ngan_chung, ngan_ket_qua, ty_le
from e_phan_luong.chay import Engine, app, ghi_ket_qua
from e_phan_luong.kieu import CHUA_PHAN_LOAI
from e_phan_luong.loi import CAU_LOI

MA_MODULE = "demo_thanh_toan"
KHAU = "ktt_duyet"
MA_LUOT = "PL-DEMO-0001"
LOAI = "chi_phi_demo"
LOAI_DUNG = "thanh_toan_demo"
NGUONG = {ten: {"so": str(so), "tien_te": "VND"}
          for ten, so in (("pm", 5000000), ("te", 3000000), ("sad", 250000))}
THAM_SO = {
    "khau": KHAU,
    "danh_muc_loai_json": json.dumps([
        {"ma": m, "ten": "Loại DEMO", "mo_ta": "Dữ liệu DEMO"}
        for m in (LOAI, LOAI_DUNG)
    ]),
}


def ma_hoa(gia_tri):
    return json.dumps(gia_tri, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def dong_demo(i=0, **thay):
    return {"ma_luot": MA_LUOT, "ma": f"PC-DEMO-{i:04}", "khau": KHAU,
            "ket_qua": "dat", **thay}


def tep_demo(dong, **thay):
    return {"phien_ban": 1, "ma_module": MA_MODULE, "nguong": NGUONG,
            "ket_qua": dong, **thay}


def trong_viec(core, ham, *, phap_nhan_id="pn-demo"):
    """Dựng dữ liệu/người đọc DEMO qua API công khai của SDK."""
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = [{
        "ma": "demo.ngan@1", "ten": "Ngăn DEMO", "nhan": ["van_ban"],
        "tra": "van_ban", "gioi_han": {"thoi_han_giay": 300},
    }]
    thu = EngineSDK(phieu)
    ket_qua_ham = []

    @thu.nang_luc("demo.ngan@1")
    def xu_ly(viec):
        ket_qua_ham.append(ham(viec))
        return {"loai": "van_ban", "van_ban": "DEMO"}

    ma_viec = core.giao_viec("demo.ngan@1", {"loai": "van_ban", "van_ban": "DEMO"},
                            phap_nhan_id=phap_nhan_id)
    core.chay(thu)
    kq = core.xem(ma_viec)
    assert kq["trang_thai"] == "XONG", kq
    return ket_qua_ham[0]


def dung_luot(core, n=1, *, ly_do="CHON_MAU", loai=LOAI, nguon_loai="quy_tac",
              tt=None, ma_luot=MA_LUOT, ma_module=MA_MODULE, khau=KHAU,
              thay_dong=None, phap_nhan_id="pn-demo"):
    def dung(viec):
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("luot", {"ma_luot": ma_luot}, {
                "ma_module": ma_module, "khau": khau, "hat_giong": "ab" * 32,
                "bam_dau_vao": "sha256:" + "12" * 32,
            })
        for dau in range(0, n, 100):
            with viec.ngan.lo() as lo:
                for i in range(dau, min(n, dau + 100)):
                    lo.lay_hoac_tao("dong_luot", {"ma_luot": ma_luot, "ma": dong_demo(i)["ma"]}, {
                        "ma_module": ma_module, "khau": khau, "ly_do": ly_do,
                        "loai": loai, "nguon_loai": nguon_loai, **(thay_dong or {}),
                    })
        if tt is not None:
            with viec.ngan.lo() as lo:
                lo.lay_hoac_tao("ty_le", {"khau": tt.khau, "loai": tt.loai}, ty_le.ve_ban_ghi(tt))

    trong_viec(core, dung, phap_nhan_id=phap_nhan_id)


def giao_ghi(core, tep, *, ts=None, phap_nhan_id="pn-demo"):
    du_lieu = tep if isinstance(tep, bytes) else ma_hoa(tep)
    dau_vao = {"loai": "tep", "tep": core.them_tep("ket-qua-DEMO.json", du_lieu, "application/json")}
    return core.giao_viec("audit.ghi_ket_qua@1", dau_vao, {**THAM_SO, **(ts or {})},
                         phap_nhan_id=phap_nhan_id)


def chay_ghi(core, tep, *, ts=None, thu=app, phap_nhan_id="pn-demo"):
    ma_viec = giao_ghi(core, tep, ts=ts, phap_nhan_id=phap_nhan_id)
    core.chay(thu)
    return core.xem(ma_viec)


def truong(kq):
    assert kq["trang_thai"] == "XONG", kq
    return kq["ket_qua"]["truong"]


def kiem_loi(kq, ma):
    assert kq["trang_thai"] == "LOI", kq
    assert kq["loi"] == {"ma": ma, "thong_diep": CAU_LOI[ma], "thu_lai_duoc": ma == "NGAN_BAN"}


def trang_thai(core, loai=LOAI):
    dong = next(d for d in core.xem_ngan(app.ma, "ty_le") if d["loai"] == loai)
    return ty_le.tu_ban_ghi(dong)


def theo_doi_thu_lai(monkeypatch):
    goc = ngan_chung.ghi_lo_thu_lai
    ds = []

    def ghi(*args, **kw):
        lan = goc(*args, **kw)
        ds.append(lan)
        return lan

    monkeypatch.setattr(ngan_chung, "ghi_lo_thu_lai", ghi)
    return ds


def app_ghi_rieng():
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = [n for n in phieu["nang_luc"] if n["ma"] == "audit.ghi_ket_qua@1"]
    thu = Engine(phieu)
    thu.nang_luc("audit.ghi_ket_qua@1")(ghi_ket_qua)
    return thu


def chay_hai(core, cac_tep, *, khi_xong=None):
    """Hai instance cùng nhận hàng chờ; đọc kết quả sau khi cả hai đã dừng."""
    ma_viec = [giao_ghi(core, tep) for tep in cac_tep]

    def chay(thu):
        try:
            core.chay(thu)
        finally:
            if khi_xong is not None:
                khi_xong()

    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_viec = [nhom.submit(chay, app_ghi_rieng()) for _ in range(2)]
        for v in cac_viec:
            v.result(timeout=20)
    return [truong(core.xem(ma)) for ma in ma_viec]


def test_ghi_demo_dung_loai_q2_va_khong_lo_ty_le_c5():
    core = CoreGia()
    dung_luot(core)
    kq = chay_ghi(core, tep_demo([dong_demo()]))
    assert truong(kq) == {
        "so_dong_nhan": 1, "so_trung": 0, "so_ngoai_mau": 0,
        "so_cap_doi_bac": 0, "so_sua_loai": 0, "phien_ban_engine": __version__,
    }
    da_ghi = core.xem_ngan(app.ma, "ket_qua_kiem")[0]
    assert da_ghi["loai"] == LOAI
    assert da_ghi["nguon_mau"] == "chon_mau"
    assert da_ghi["nguon_loai_sai"] is None
    assert trang_thai(core).mau_12t == 1
    assert set(kq["ket_qua"]) == {"loai", "truong"}
    assert not {"ty_le", "xac_suat", "bac", "diem", "hat_giong", "che_do"} & set(truong(kq))


def test_trung_trong_tep_va_trung_da_ghi_khong_cong_hai_lan():
    core = CoreGia()
    dung_luot(core, 3)
    tep = tep_demo([dong_demo(0), dong_demo(0), dong_demo(1), dong_demo(2), dong_demo(1)])
    assert truong(chay_ghi(core, tep))["so_trung"] == 2
    ban_dau = core.xem_ngan(app.ma, "ty_le")
    assert truong(chay_ghi(core, tep)) == {
        "so_dong_nhan": 0, "so_trung": 5, "so_ngoai_mau": 0,
        "so_cap_doi_bac": 0, "so_sua_loai": 0, "phien_ban_engine": __version__,
    }
    assert core.xem_ngan(app.ma, "ty_le") == ban_dau
    assert trang_thai(core).mau_12t == 3
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 3


def test_ket_qua_da_het_han_van_la_dau_chong_trung(monkeypatch):
    core = CoreGia()
    dung_luot(core)
    tep = tep_demo([dong_demo()])
    assert truong(chay_ghi(core, tep))["so_dong_nhan"] == 1
    cu = core.xem_ngan(app.ma, "ty_le")
    # Giả thời điểm kết quả bị ẩn sau 365 ngày nhưng lượt chưa hết 400 ngày.
    monkeypatch.setattr(core, "_con_han", lambda d: "ket_qua" not in d)
    dem = truong(chay_ghi(core, tep))
    assert (dem["so_dong_nhan"], dem["so_trung"]) == (0, 1)
    assert core.xem_ngan(app.ma, "ty_le") == cu


def test_tep_rong_khong_tao_thong_ke():
    core = CoreGia()
    dem = truong(chay_ghi(core, tep_demo([], nguong=None)))
    assert all(v == 0 for k, v in dem.items() if k != "phien_ban_engine")
    assert core.xem_ngan(app.ma, "ty_le") == []
    assert core.xem_ngan(app.ma, "ket_qua_kiem") == []


@pytest.mark.parametrize("truong_hop", ["khong_co", "phap_nhan_khac", "dong_sau_khong_co"])
def test_luot_khong_ton_tai_kiem_het_truoc_khi_ghi(truong_hop):
    core = CoreGia()
    dung_luot(core)
    ds = [dong_demo(ma_luot="PL-DEMO-khong-co")]
    if truong_hop == "dong_sau_khong_co":
        ds.insert(0, dong_demo())
    elif truong_hop == "phap_nhan_khac":
        ds = [dong_demo()]
    kq = chay_ghi(core, tep_demo(ds),
                 phap_nhan_id="pn-demo-khac" if truong_hop == "phap_nhan_khac" else "pn-demo")
    kiem_loi(kq, "LUOT_KHONG_TON_TAI")
    assert core.xem_ngan(app.ma, "ket_qua_kiem") == []
    assert core.xem_ngan(app.ma, "ty_le") == []


@pytest.mark.parametrize("thay_luot,thay_dong,thay_tep,ts", [
    ({"ma_module": "demo_khac"}, None, {}, {}),
    ({"khau": "cfo_duyet"}, None, {}, {}),
    ({}, {"ma_module": "demo_khac"}, {}, {}),
    ({}, {"khau": "cfo_duyet"}, {}, {}),
    ({}, None, {"ma_module": "demo_khac"}, {}),
    ({}, None, {}, {"ma_module": "demo_khac"}),
    ({}, None, {}, {"khau": "cfo_duyet"}),
])
def test_tu_choi_module_khau_khong_khop(thay_luot, thay_dong, thay_tep, ts):
    core = CoreGia()
    dung_luot(core, thay_dong=thay_dong, **thay_luot)
    kiem_loi(chay_ghi(core, tep_demo([dong_demo()], **thay_tep), ts=ts), "DU_LIEU_KHONG_HOP_LE")
    assert core.xem_ngan(app.ma, "ket_qua_kiem") == []


@pytest.mark.parametrize("nguon_loai", ["module", "quy_tac", "ai", "chua_phan_loai"])
def test_sua_loai_dung_va_nguon_loai_sai_q2(nguon_loai):
    core = CoreGia()
    dung_luot(core, nguon_loai=nguon_loai)
    tep = tep_demo([dong_demo(loai_dung=LOAI_DUNG)])
    assert truong(chay_ghi(core, tep))["so_sua_loai"] == 1
    ghi = core.xem_ngan(app.ma, "ket_qua_kiem")[0]
    assert (ghi["loai"], ghi["nguon_loai_sai"]) == (LOAI_DUNG, nguon_loai)
    assert trang_thai(core, LOAI_DUNG).mau_12t == 1
    assert not any(d["loai"] == LOAI for d in core.xem_ngan(app.ma, "ty_le"))
    assert truong(chay_ghi(core, tep))["so_sua_loai"] == 0


def test_loai_dung_giong_goc_khong_dem_sua_va_ngoai_danh_muc_bi_tu_choi():
    core = CoreGia()
    dung_luot(core, 2)
    kq = chay_ghi(core, tep_demo([dong_demo(loai_dung=LOAI)]))
    assert truong(kq)["so_sua_loai"] == 0
    kiem_loi(chay_ghi(core, tep_demo([dong_demo(1, loai_dung="loai_demo_la")])), "DU_LIEU_KHONG_HOP_LE")
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 1


@pytest.mark.parametrize("thuoc_luot", [True, False])
def test_loi_ngoai_mau_quay_ve_bac_dau_khong_di_vao_uoc_luong(thuoc_luot):
    core = CoreGia()
    tt = replace(ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()), bac=Decimal("0.10"))
    dung_luot(core, ly_do="KHONG_CHON", tt=tt)
    d = dong_demo(0 if thuoc_luot else 99, ket_qua="sai",
                  so_tien_sai={"so": "1", "tien_te": "VND"}, loai_dung=LOAI)
    dem = truong(chay_ghi(core, tep_demo([d])))
    assert (dem["so_ngoai_mau"], dem["so_cap_doi_bac"], dem["so_sua_loai"]) == (1, 1, 0)
    tt = trang_thai(core)
    assert tt.bac == Decimal("0.30")
    assert tt.mau_12t == tt.loi_12t == 0
    assert tt.loi_ngoai_mau_12t == 1
    assert "loi_ngoai_mau" in tt.nhan


@pytest.mark.parametrize("loai_dung,loai_mong", [(None, CHUA_PHAN_LOAI), (LOAI_DUNG, LOAI_DUNG)])
def test_dong_ngoai_luot_lay_loai_dung_hoac_chua_phan_loai(loai_dung, loai_mong):
    core = CoreGia()
    dung_luot(core, 0)
    kq = chay_ghi(core, tep_demo([dong_demo(99, loai_dung=loai_dung)]))
    assert truong(kq)["so_ngoai_mau"] == 1
    assert truong(kq)["so_sua_loai"] == 0
    ghi = core.xem_ngan(app.ma, "ket_qua_kiem")[0]
    assert (ghi["loai"], ghi["nguon_loai_sai"]) == (loai_mong, None)


@pytest.mark.parametrize("nguon,kq,mau", [("CHON_MAU", "dat", 1), ("VUOT_TE", "dat", 0),
                                         ("KHONG_CHON", "dat", 0), ("CHON_MAU", "khong_kiem", 0)])
def test_chi_mau_ngau_nhien_da_kiem_duoc_cong(nguon, kq, mau):
    core = CoreGia()
    dung_luot(core, ly_do=nguon)
    assert truong(chay_ghi(core, tep_demo([dong_demo(ket_qua=kq)])))["so_dong_nhan"] == 1
    assert trang_thai(core).mau_12t == mau


@pytest.mark.parametrize("co_nguong_tep,co_nguong_tham_so", [(True, False), (False, True), (True, True)])
def test_nguong_q1_uu_tien_tep_truoc_cai_dat(co_nguong_tep, co_nguong_tham_so):
    core = CoreGia()
    dung_luot(core)
    nguong_khac = {ten: {"so": str(so), "tien_te": "VND"}
                  for ten, so in (("pm", 500), ("te", 300), ("sad", 25))}
    d = dong_demo(ket_qua="sai", so_tien_sai={"so": "250000", "tien_te": "VND"})
    tep = tep_demo([d], nguong=NGUONG if co_nguong_tep else None)
    ts = {"nguong_json": json.dumps(nguong_khac)} if co_nguong_tham_so else {}
    assert truong(chay_ghi(core, tep, ts=ts))["so_dong_nhan"] == 1
    assert core.xem_ngan(app.ma, "ket_qua_kiem")[0]["muc_sai"] == ("sad" if co_nguong_tep else "te")


def test_thieu_nguong_chi_can_khi_co_dong_sai_va_q7_tu_choi_tien_te_khac():
    core = CoreGia()
    dung_luot(core, 3)
    assert truong(chay_ghi(core, tep_demo([dong_demo()], nguong=None)))["so_dong_nhan"] == 1
    d = dong_demo(1, ket_qua="sai", so_tien_sai={"so": "1000000", "tien_te": "VND"})
    kiem_loi(chay_ghi(core, tep_demo([d], nguong=None)), "THIEU_NGUONG")
    d["so_tien_sai"]["tien_te"] = "USD"
    kiem_loi(chay_ghi(core, tep_demo([dong_demo(2), d])), "DU_LIEU_KHONG_HOP_LE")
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 1
    assert trang_thai(core).mau_12t == 1


def test_thu_tu_chi_so_va_dem_moi_cap_mot_lan_du_co_hai_lan_doi():
    core = CoreGia()
    dung_luot(core, 31)
    ds = [dong_demo(0, ket_qua="sai", so_tien_sai={"so": "-3000000", "tien_te": "VND"})]
    ds.extend(dong_demo(i) for i in range(1, 31))
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo(ds)))
    tep = replace(tep, dong=tuple(reversed(tep.dong)))

    def ghi(viec):
        viec.tham_so = deepcopy(THAM_SO)
        return ngan_ket_qua.ghi_ket_qua(viec, tep)

    dem = trong_viec(core, ghi)
    assert dem["so_cap_doi_bac"] == 1  # bac -> toan_bo -> bac, cùng một cặp.
    assert dem["so_dong_nhan"] == 31
    tt = trang_thai(core)
    assert (tt.che_do, tt.bac, tt.mau_sach_toan_bo) == ("bac", Decimal("0.30"), 30)
    assert datetime.fromisoformat(tt.doi_bac_luc).utcoffset() == timedelta(0)


def test_loi_nho_khi_dang_toan_bo_giu_dem_mau_sach_q6():
    core = CoreGia()
    tt = replace(ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()), che_do="toan_bo", mau_sach_toan_bo=29)
    dung_luot(core, 2, tt=tt)
    ds = [dong_demo(0, ket_qua="sai", so_tien_sai={"so": "1", "tien_te": "VND"}), dong_demo(1)]
    assert truong(chay_ghi(core, tep_demo(ds)))["so_cap_doi_bac"] == 1
    assert trang_thai(core).che_do == "bac"
    assert trang_thai(core).mau_sach_toan_bo == 30


@pytest.mark.parametrize("n", [99, 100, 199])
def test_chia_lo_99_ket_qua_va_mot_ty_le_cas(n, monkeypatch):
    core = CoreGia()
    dung_luot(core, n)
    cac_lo = []
    goc = core._ngan_ghi_lo

    def ghi(ma, instance, lenh, khoa, **kw):
        cac_lo.append(deepcopy(lenh))
        return goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    assert truong(chay_ghi(core, tep_demo([dong_demo(i) for i in range(n)])))["so_dong_nhan"] == n
    assert len(cac_lo) == 1 + (n + 98) // 99
    assert [(l["bang"], l["thao_tac"]) for l in cac_lo[0]] == [("ty_le", "lay_hoac_tao")]
    for lo in cac_lo[1:]:
        assert 2 <= len(lo) <= 100
        assert all(l["bang"] == "ket_qua_kiem" and l["thao_tac"] == "them" for l in lo[:-1])
        assert (lo[-1]["bang"], lo[-1]["thao_tac"]) == ("ty_le", "sua")
        assert type(lo[-1]["row_version"]) is int
    assert trang_thai(core).mau_12t == n


@pytest.mark.parametrize("so_xung_dot", [1, 3, 4])
def test_cas_doc_lai_khong_dem_lech_va_ngan_ban_sau_ba_lan_thu_lai(so_xung_dot, monkeypatch):
    core = CoreGia()
    dung_luot(core, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()))
    cu = core.xem_ngan(app.ma, "ty_le")
    core.gay_xung_dot_ngan("ty_le", so_lan=so_xung_dot)
    so_lo_cu = len([d for d in core.nhat_ky if d[0] == "ngan"])
    thu_lai = theo_doi_thu_lai(monkeypatch)
    kq = chay_ghi(core, tep_demo([dong_demo()]))
    if so_xung_dot == 4:
        kiem_loi(kq, "NGAN_BAN")
        assert core.xem_ngan(app.ma, "ket_qua_kiem") == []
        assert core.xem_ngan(app.ma, "ty_le") == cu
    else:
        assert truong(kq)["so_dong_nhan"] == 1
        assert truong(kq)["so_trung"] == 0
        assert sum(thu_lai) == so_xung_dot
        assert trang_thai(core).mau_12t == 1
        assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 1
    so_lo_moi = len([d for d in core.nhat_ky if d[0] == "ngan"]) - so_lo_cu
    assert so_lo_moi == min(so_xung_dot + 1, 4)


@pytest.mark.parametrize("gui_trung", [False, True])
def test_hai_ghi_thuc_su_tranh_cas_dung_mot_lan_thu_lai(gui_trung, monkeypatch):
    core = CoreGia()
    dung_luot(core, 2, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()))
    thu_lai = theo_doi_thu_lai(monkeypatch)
    hen = Barrier(2, timeout=10)
    cuc_bo = local()
    cap_nhat_goc = doi_bac.cap_nhat

    def cap_nhat(*args, **kw):
        if not getattr(cuc_bo, "da_hen", False):
            cuc_bo.da_hen = True
            hen.wait()  # Cả hai đã đọc cùng row_version và chưa thấy kết quả.
        return cap_nhat_goc(*args, **kw)

    monkeypatch.setattr(doi_bac, "cap_nhat", cap_nhat)
    cac_dem = chay_hai(core, [tep_demo([dong_demo(i)]) for i in (0, 0 if gui_trung else 1)])
    assert sum(thu_lai) == 1
    assert sum(d["so_dong_nhan"] for d in cac_dem) == (1 if gui_trung else 2)
    assert sum(d["so_trung"] for d in cac_dem) == int(gui_trung)
    assert trang_thai(core).mau_12t == (1 if gui_trung else 2)
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == (1 if gui_trung else 2)


def test_hai_ghi_dong_thoi_gay_xung_dot_ngan_mot_lan(monkeypatch):
    core = CoreGia()
    dung_luot(core, 2, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()))
    core.gay_xung_dot_ngan("ty_le", so_lan=1)
    thu_lai = theo_doi_thu_lai(monkeypatch)
    hen, xong = Barrier(2, timeout=10), Event()
    khoa = Lock()
    stt = []
    tao_goc = ngan_ket_qua._tao_cap_moi

    def tao(*args):
        tao_goc(*args)
        with khoa:
            i = len(stt)
            stt.append(i)
        hen.wait()
        if i == 1:
            assert xong.wait(10)  # Ép riêng xung đột giả, không thêm một CAS đua.

    monkeypatch.setattr(ngan_ket_qua, "_tao_cap_moi", tao)

    cac_dem = chay_hai(core, [tep_demo([dong_demo(i)]) for i in range(2)], khi_xong=xong.set)
    assert sum(thu_lai) == 1
    assert sum(d["so_dong_nhan"] for d in cac_dem) == 2
    assert sum(d["so_trung"] for d in cac_dem) == 0
    assert trang_thai(core).mau_12t == 2


def test_hai_ghi_cung_tao_cap_moi_lay_hoac_tao_roi_sua_cas(monkeypatch):
    core = CoreGia()
    dung_luot(core, 2)
    thu_lai = theo_doi_thu_lai(monkeypatch)
    hen_tao, hen_sua = Barrier(2, timeout=10), Barrier(2, timeout=10)
    cuc_bo = local()
    moi_goc, cap_nhat_goc = ty_le.moi, doi_bac.cap_nhat

    def moi(*args):
        hen_tao.wait()  # Cả hai cùng thấy cặp chưa tồn tại.
        return moi_goc(*args)

    def cap_nhat(*args, **kw):
        if not getattr(cuc_bo, "da_hen", False):
            cuc_bo.da_hen = True
            hen_sua.wait()
        return cap_nhat_goc(*args, **kw)

    monkeypatch.setattr(ty_le, "moi", moi)
    monkeypatch.setattr(doi_bac, "cap_nhat", cap_nhat)
    cac_dem = chay_hai(core, [tep_demo([dong_demo(i)]) for i in range(2)])
    assert sum(thu_lai) == 1
    assert sum(d["so_dong_nhan"] for d in cac_dem) == 2
    assert len(core.xem_ngan(app.ma, "ty_le")) == 1
    assert trang_thai(core).mau_12t == 2


def test_cung_ket_qua_nhung_sua_sang_hai_loai_chi_cong_mot_cap(monkeypatch):
    core = CoreGia()
    dung_luot(core, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()))
    thu_lai = theo_doi_thu_lai(monkeypatch)
    hen, cuc_bo = Barrier(2, timeout=10), local()
    goc = doi_bac.cap_nhat

    def cap_nhat(*args, **kw):
        if not getattr(cuc_bo, "da_hen", False):
            cuc_bo.da_hen = True
            hen.wait()
        return goc(*args, **kw)

    monkeypatch.setattr(doi_bac, "cap_nhat", cap_nhat)
    cac_dem = chay_hai(core, [tep_demo([dong_demo(loai_dung=l)]) for l in (LOAI, LOAI_DUNG)])
    assert sum(thu_lai) == 1
    assert sum(d["so_dong_nhan"] for d in cac_dem) == 1
    assert sum(d["so_trung"] for d in cac_dem) == 1
    assert sum(int(d["mau_12t"]) for d in core.xem_ngan(app.ma, "ty_le")) == 1
    da_ghi = core.xem_ngan(app.ma, "ket_qua_kiem")
    assert len(da_ghi) == 1
    assert sum(d["so_sua_loai"] for d in cac_dem) == int(da_ghi[0]["loai"] == LOAI_DUNG)


def test_lo_sau_ban_gui_lai_khong_cong_lai_lo_truoc(monkeypatch):
    core = CoreGia()
    dung_luot(core, 100)
    tep = tep_demo([dong_demo(i) for i in range(100)])
    goc = core._ngan_ghi_lo
    da_gay = False

    def ghi(ma, instance, lenh, khoa, **kw):
        nonlocal da_gay
        if not da_gay and any(l.get("gia_tri", {}).get("ma") == dong_demo(99)["ma"] for l in lenh):
            da_gay = True
            core.gay_xung_dot_ngan("ty_le", so_lan=4)
        return goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    kiem_loi(chay_ghi(core, tep), "NGAN_BAN")
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 99
    assert trang_thai(core).mau_12t == 99
    dem = truong(chay_ghi(core, tep))
    assert (dem["so_dong_nhan"], dem["so_trung"]) == (1, 99)
    assert trang_thai(core).mau_12t == 100
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 100


def test_mat_xac_nhan_ngan_khong_ghi_ket_qua_hai_lan():
    core = CoreGia()
    dung_luot(core, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()))
    core.gay_mat_xac_nhan("ngan", so_lan=1)
    dem = truong(chay_ghi(core, tep_demo([dong_demo()])))
    assert dem["so_dong_nhan"] == 1
    assert dem["so_trung"] == 0
    assert trang_thai(core).mau_12t == 1
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 1


def test_luot_ke_tiep_doc_ngay_bac_moi_qua_ngan_coregia():
    """Kiểm hợp đồng người đọc PL-2; chưa là test năng lực PL-2 đang ghép."""
    core = CoreGia()
    dung_luot(core, 30)
    assert truong(chay_ghi(core, tep_demo([dong_demo(i) for i in range(30)])))["so_cap_doi_bac"] == 1

    def doc_luot_ke(viec):
        bg = viec.ngan.doc("ty_le", {"khau": KHAU, "loai": LOAI})
        return ty_le.p_bac(ty_le.tu_ban_ghi(bg.gia_tri), ty_le.ChinhSach())

    assert trong_viec(core, doc_luot_ke) == Decimal("0.20")


def test_cai_dat_chinh_sach_dung_khi_ghi_ket_qua():
    core = CoreGia()
    dung_luot(core)
    cs = {"mau_toi_thieu": [1, 2, 3], "nguong_xuong": [0.99, 0.98, 0.97]}
    dem = truong(chay_ghi(core, tep_demo([dong_demo()]), ts={"chinh_sach_json": json.dumps(cs)}))
    assert dem["so_cap_doi_bac"] == 1
    assert trang_thai(core).bac == Decimal("0.20")


def test_xem_ngan_c4_khong_luu_chi_tiet_giao_dich():
    core = CoreGia()
    dung_luot(core)
    d = dong_demo(ket_qua="sai", loai_dung=LOAI_DUNG,
                  so_tien_sai={"so": "1234567.123456", "tien_te": "VND"},
                  ngay="2026-10-30", doi_tac="DEMO-NCC-KHONG-LUU",
                  dien_giai="NOI-DUNG-DEMO-KHONG-LUU", nguoi_kiem="DEMO-NGUOI-KIEM",
                  ghi_chu="DEMO-GHI-CHU-KHONG-LUU")
    assert truong(chay_ghi(core, tep_demo([d])))["so_sua_loai"] == 1
    cot_he_thong = {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
    noi_dung = []
    for b in app.phieu["ngan_du_lieu"]:
        for dong in core.xem_ngan(app.ma, b["bang"]):
            assert set(dong) <= cot_he_thong | {t["ma"] for t in b["truong"]}
            assert not set(dong) & {"so_tien", "so_tien_sai", "tien_te", "ngay", "doi_tac",
                                    "noi_dung", "dien_giai", "nguoi_kiem", "ghi_chu"}
            noi_dung.append(dong)
    chuoi = json.dumps(noi_dung, ensure_ascii=False)
    for cam in ("1234567.123456", "2026-10-30", "DEMO-NCC-KHONG-LUU",
                "NOI-DUNG-DEMO-KHONG-LUU", "DEMO-NGUOI-KIEM", "DEMO-GHI-CHU-KHONG-LUU"):
        assert cam not in chuoi
