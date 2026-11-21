"""PL-9F: giữ Q5, giảm lượt tìm; đã kiểm bằng Core giả (CoreGia).

Bản tham chiếu chép nguyên hàm trước PL-9F, chỉ đổi tên; không sinh từ mã mới.
Mọi trạng thái, mã và lịch sử trong tệp đều là DEMO.
"""
from collections import Counter
from collections.abc import Sequence
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from random import Random
import sys
from types import SimpleNamespace
import weakref

import pytest
from conftest import trang_thai_so_sanh
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "goi" / "e_phan_luong"))
from e_phan_luong import ngan_luot
from e_phan_luong.chay import app
from e_phan_luong.kieu import CHON_MAU, KQ_DAT, KQ_SAI, LY_DO_BAT_BUOC, noi_ly_do, tach_ly_do
from e_phan_luong.ngan_chung import ghi_lay_hoac_tao_nhieu, tim_tat_ca

MODULE = "demo_thanh_toan"
KHAU = "ktt_duyet"


def tra_nop_lai_cu(viec, ma_module: str, khau: str, ds_ma: Sequence[str]) -> frozenset[str]:
    """Q5: chỉ giữ Đỏ của lượt hoàn tất gần nhất chưa có kết quả dat/sai.

    Dòng của lượt ghi dở không có dấu luot bị bỏ qua. So thời điểm có múi giờ,
    không so thứ tự ma_luot hoặc thời điểm riêng của dong_luot. Nếu hai lượt
    trùng thời điểm, dùng ma_luot làm khóa phụ ổn định. Bỏ qua chính lượt
    của việc Core hiện tại để giao lại không tự sinh lý do NOP_LAI.
    """
    luot_da_doc = {}
    nop_lai = set()
    for ma in dict.fromkeys(ds_ma):
        ds = tim_tat_ca(viec, "dong_luot", {"ma_module": ma_module, "khau": khau, "ma": ma})
        gan_nhat = None
        for bg in ds:
            dong = bg.gia_tri
            ma_luot = dong["ma_luot"]
            if ma_luot == getattr(viec, "_ma_luot_phan_luong", None):
                continue
            if ma_luot not in luot_da_doc:
                luot_da_doc[ma_luot] = viec.ngan.doc("luot", {"ma_luot": ma_luot})
            luot = luot_da_doc[ma_luot]
            if luot is None:
                continue
            gia_tri = luot.gia_tri
            if gia_tri["ma_module"] != ma_module or gia_tri["khau"] != khau:
                continue
            khoa = (datetime.fromisoformat(gia_tri["tao_luc"]), ma_luot)
            if gan_nhat is None or khoa > gan_nhat[0]:
                gan_nhat = (khoa, dong)
        if gan_nhat is None:
            continue
        dong = gan_nhat[1]
        if not set(tach_ly_do(dong["ly_do"])) & (LY_DO_BAT_BUOC | {CHON_MAU}):
            continue
        kq = viec.ngan.doc("ket_qua_kiem", {"ma_luot": dong["ma_luot"], "ma": ma, "khau": khau},
                          gom_het_han=True)
        if kq is None or kq.gia_tri["ket_qua"] not in {KQ_DAT, KQ_SAI}:
            nop_lai.add(ma)
    return frozenset(nop_lai)



class _CoreDem(CoreGia):
    """Chỉ đếm ở cổng; đọc/tìm vẫn chạy nguyên bản CoreGia SDK 2.2.0."""

    def __init__(self):
        super().__init__()
        self.dem = Counter()
        self.cac_tim = []

    def _ngan_tim(self, ma, instance, bang, **kw):
        self.dem["tim"] += 1
        self.cac_tim.append((bang, deepcopy(kw)))
        return super()._ngan_tim(ma, instance, bang, **kw)

    def _ngan_doc(self, *a, **kw):
        self.dem["doc"] += 1
        return super()._ngan_doc(*a, **kw)

    def dat_lai_dem(self):
        self.dem.clear()
        self.cac_tim.clear()


def _trong_viec(core, ham):
    phieu = deepcopy(app.phieu)
    phieu["chay_thu_demo"] = []
    nl = phieu["nang_luc"][0]
    nl.update(nhan=["van_ban"], tra="van_ban")
    nl.pop("truong_ra")
    phieu["nang_luc"] = [nl]
    thu = Engine(phieu)
    ket_qua = []

    @thu.nang_luc(nl["ma"])
    def kiem(viec):
        ket_qua.append(ham(viec))
        return {"loai": "van_ban", "van_ban": "DEMO"}

    kq = core.chay_thu(thu, nl["ma"], {"loai": "van_ban", "van_ban": "DEMO"}, {"khau": KHAU})
    assert kq["trang_thai"] == "XONG", kq
    return ket_qua[0]


def _luot(ma_luot, ma_module=MODULE, khau=KHAU):
    return ({"ma_luot": ma_luot}, {"ma_module": ma_module, "khau": khau,
            "hat_giong": bytes(range(32)).hex(), "bam_dau_vao": "sha256:" + "a" * 64})


def _dong(ma_luot, ma, ly_do=CHON_MAU, ma_module=MODULE, khau=KHAU):
    return ({"ma_luot": ma_luot, "ma": ma}, {"ma_module": ma_module, "khau": khau,
            "ly_do": ly_do, "loai": "chi_phi_demo", "nguon_loai": "module"})


def _lich_su_nhieu_dong(core, viec, n):
    """Gieo một dòng qua SDK rồi nhân metadata hợp lệ, chỉ để setup DEMO lớn.

    Không thay cổng đọc/tìm bằng chỉ mục hay giả kết quả để đo số lần gọi.
    Mọi dòng có id/khóa riêng, cùng pháp nhân, lượt và hạn giữ của dòng gốc.
    """
    ghi_lay_hoac_tao_nhieu(viec, "luot", [_luot("PL-DEMO-DEM")])
    ghi_lay_hoac_tao_nhieu(viec, "dong_luot", [_dong("PL-DEMO-DEM", "PC-DEMO-00000")])
    mau, = core._ngan[app.ma, "dong_luot"]
    core._ngan[app.ma, "dong_luot"] = [
        {**mau, "id": f"dong-DEMO-{i:06}", "ma": f"PC-DEMO-{i:05}"} for i in range(n)]
    return [f"PC-DEMO-{i:05}" for i in range(n)]


@pytest.mark.parametrize("chi_so", trang_thai_so_sanh())
def test_tuong_duong_240_trang_thai_ngau_nhien_demo(chi_so):
    """Hạt cố định; thứ tự mã/thời điểm, trạng thái hoàn tất và kết quả độc lập."""
    rng = Random(202611210349 + chi_so)
    core = CoreGia()

    def kiem(viec):
        cac_ma = [f"PC-DEMO-{i:02}" for i in range(rng.randint(5, 12))]
        cac_luot, cac_dong, cac_kq, thoi_diem, het_han = [], [], [], {}, set()
        for i in range(rng.randint(8, 16)):
            ml = f"PL-DEMO-{i:02}"
            # Có dòng trông đúng phạm vi nhưng dấu luot lại khác module/khâu.
            md = "demo_khac" if i % 7 == 2 else MODULE
            kh = "cfo_duyet" if i % 7 == 3 else KHAU
            if i % 7 != 1:  # Lượt ghi dở: không có dấu luot.
                cac_luot.append(_luot(ml, md, kh))
            # Hai lượt 00/05 trùng thời điểm thực, trình bày khác múi giờ.
            phut = 15 if i in (0, 5) else rng.randrange(30)
            gio = timezone(timedelta(hours=rng.choice((-5, 0, 7, 9))))
            thoi_diem[ml] = datetime(2026, 11, 20, 14, phut, tzinfo=timezone.utc).astimezone(gio).isoformat()
            for ma in rng.sample(cac_ma, rng.randint(1, len(cac_ma))):
                ly_do = rng.choice((CHON_MAU, "KHONG_CHON", "DEMO_KHAC", *sorted(LY_DO_BAT_BUOC),
                                    noi_ly_do((CHON_MAU, "CO_DO_CUNG"))))
                md_dong = "demo_khac" if rng.randrange(9) == 0 else MODULE
                kh_dong = "cfo_duyet" if rng.randrange(9) == 0 else KHAU
                cac_dong.append(_dong(ml, ma, ly_do, md_dong, kh_dong))
                kq = rng.choice((None, "dat", "sai", "khong_kiem", "DEMO_KHAC"))
                if kq is not None:
                    cac_kq.append(({"ma_luot": ml, "ma": ma, "khau": KHAU},
                                   {"ma_module": MODULE, "loai": "chi_phi_demo", "ket_qua": kq}))
                    if rng.choice((False, True)):
                        het_han.add((ml, ma))
        ghi_lay_hoac_tao_nhieu(viec, "luot", cac_luot)
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", cac_dong)
        ghi_lay_hoac_tao_nhieu(viec, "ket_qua_kiem", cac_kq)
        for luot in core._ngan[app.ma, "luot"]:
            luot["tao_luc"] = thoi_diem[luot["ma_luot"]]
        for kq in core._ngan.get((app.ma, "ket_qua_kiem"), []):
            if (kq["ma_luot"], kq["ma"]) in het_han:
                kq["het_han_luc"] = "2025-01-01T00:00:00+07:00"
        if chi_so % 3:
            viec._ma_luot_phan_luong = "PL-DEMO-04"
        ds_ma = [] if chi_so % 17 == 0 else rng.choices(cac_ma, k=len(cac_ma) * 2) + ["PC-DEMO-MOI"]
        truoc = deepcopy(core._ngan)
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        moi = ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma)
        assert moi == cu
        assert isinstance(moi, frozenset)
        assert core._ngan == truoc  # Cả hai cách tra đều chỉ đọc.

    _trong_viec(core, kiem)


@pytest.mark.parametrize("so_ma,so_dong", [(10, 500), (10, 501), (20, 1000), (20, 1001)])
def test_dung_va_vuot_ngan_sach_khong_dung_ket_qua_quet_do_dang(so_ma, so_dong):
    core = _CoreDem()

    def kiem(viec):
        ds_lich_su = _lich_su_nhieu_dong(core, viec, so_dong)
        # Một mã ở đầu, một mã ở cuối: quét dở không được bỏ mất mã cuối.
        ds_ma = [ds_lich_su[0], ds_lich_su[-1]] + [f"PC-DEMO-MOI-{i:02}" for i in range(so_ma - 2)]
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        assert cu == frozenset((ds_lich_su[0], ds_lich_su[-1]))
        core.dat_lai_dem()
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma + ds_ma) == cu
        ngan_sach = (so_ma + 9) // 10
        vuot = so_dong > ngan_sach * 500
        # PL-9H thêm một lượt tìm ket_qua_kiem cho hai ứng viên cùng lượt.
        assert core.dem["tim"] == 2 + ngan_sach + (so_ma if vuot else 0)
        cac_tim_dong = [kw for bang, kw in core.cac_tim if bang == "dong_luot"]
        cac_loc = [kw["loc"] for kw in cac_tim_dong]
        assert all(loc == {"ma_module": MODULE, "khau": KHAU} for loc in cac_loc[:1 + ngan_sach])
        if vuot:
            assert [loc["ma"] for loc in cac_loc[1 + ngan_sach:]] == ds_ma
        assert all(kw["sap_xep"] == [{"truong": c, "giam": False} for c in ("ma_luot", "ma")]
                   for kw in cac_tim_dong[1:])
        assert core.cac_tim[0][1]["gioi_han"] == 1

    _trong_viec(core, kiem)

@pytest.mark.parametrize("n,co_lich_su", [
    pytest.param(n, co, marks=pytest.mark.sau if co and n == 10000 else (),
                 id=f"{'nop_lai' if co else 'trong'}-{n}")
    for co in (False, True) for n in (1000, 5000, 10000)
])
def test_so_lan_goi_coregia(n, co_lich_su):
    core = _CoreDem()

    def kiem(viec):
        ds_ma = (_lich_su_nhieu_dong(core, viec, n) if co_lich_su else
                 [f"PC-DEMO-{i:05}" for i in range(n)])
        core.dat_lai_dem()
        moi = ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma)
        assert moi == (frozenset(ds_ma) if co_lich_su else frozenset())
        # PL-9H đọc kết quả bằng một trang rỗng, chỉ còn doc dấu luot.
        assert core.dem["tim"] == (2 + (n + 499) // 500 if co_lich_su else 1)
        assert core.dem.get("doc", 0) == (1 if co_lich_su else 0)
        if n == 10000:
            if co_lich_su:
                assert core.dem["tim"] <= 25
            else:
                assert core.dem["tim"] == 1
        print(f"DEMO N={n} {'nop_lai' if co_lich_su else 'trong'}: "
              f"tim={core.dem['tim']}; doc={core.dem.get('doc', 0)}")

    _trong_viec(core, kiem)


@pytest.mark.parametrize("n", [1, 9, 10, 11, 20])
def test_can_roi_rac_khi_lam_tron_ngan_sach(n):
    core = _CoreDem()

    def kiem(viec):
        ngan_sach = (n + 9) // 10
        _lich_su_nhieu_dong(core, viec, ngan_sach * 500 + 1)
        ds_ma = [f"PC-DEMO-MOI-{i:02}" for i in range(n)]
        core.dat_lai_dem()
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        so_cu = core.dem["tim"]
        core.dat_lai_dem()
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma) == cu == frozenset()
        assert core.dem["tim"] == so_cu + ngan_sach + 1
        if n % 10 == 0:
            assert core.dem["tim"] * 10 <= 11 * so_cu + 10

    _trong_viec(core, kiem)


def test_ds_ma_rong_khong_goi_core():
    core = _CoreDem()

    def kiem(viec):
        core.dat_lai_dem()
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, []) == tra_nop_lai_cu(viec, MODULE, KHAU, [])
        assert core.dem == {}

    _trong_viec(core, kiem)


@pytest.mark.parametrize("cac_tiep", [("DEMO-A", "DEMO-A"), ("DEMO-A", "DEMO-B", "DEMO-A")])
def test_chong_vong_tiep_trong_quet(monkeypatch, cac_tiep):
    core = CoreGia()

    def kiem(viec):
        cac_goi = []
        ban = SimpleNamespace(gia_tri={"ma": "PC-DEMO-KHAC"})

        def tim(bang, **kw):
            cac_goi.append(kw)
            assert bang == "dong_luot"
            if kw["gioi_han"] == 1:
                return SimpleNamespace(danh_sach=[ban], tiep="DEMO-DO")
            assert len(cac_goi) <= len(cac_tiep) + 1
            return SimpleNamespace(danh_sach=[ban], tiep=cac_tiep[len(cac_goi) - 2])

        monkeypatch.setattr(viec.ngan, "tim", tim)
        with pytest.raises(LoiNghiepVu) as exc:
            ngan_luot.tra_nop_lai(viec, MODULE, KHAU, [f"PC-DEMO-{i}" for i in range(40)])
        assert exc.value.ma == "NGAN_BAN"
        assert len(cac_goi) == 1 + len(cac_tiep)

    _trong_viec(core, kiem)


def test_chong_vong_tiep_khi_quay_ve_tim_tung_ma(monkeypatch):
    core = CoreGia()

    def kiem(viec):
        ban = SimpleNamespace(gia_tri={"ma": "PC-DEMO-KHAC"})
        cac_goi = []

        def tim(bang, **kw):
            cac_goi.append(kw)
            assert len(cac_goi) <= 4
            return SimpleNamespace(danh_sach=[ban], tiep="DEMO-LAP")

        monkeypatch.setattr(viec.ngan, "tim", tim)
        with pytest.raises(LoiNghiepVu) as exc:
            ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ["PC-DEMO"])
        assert exc.value.ma == "NGAN_BAN"
        assert len(cac_goi) == 4  # Dò, quét một trang, hai trang đường cũ.
        assert all(kw["loc"]["ma"] == "PC-DEMO" for kw in cac_goi[2:])

    _trong_viec(core, kiem)


@pytest.mark.parametrize("sau_so_tim", [0, 1, 2, 3])
def test_kiem_huy_truoc_do_trong_quet_va_trong_fallback(monkeypatch, sau_so_tim):
    core = _CoreDem()

    class HuyDemo(Exception):
        pass

    def kiem(viec):
        _lich_su_nhieu_dong(core, viec, 501)
        core.dat_lai_dem()

        def kiem_huy():
            if core.dem["tim"] == sau_so_tim:
                raise HuyDemo

        with monkeypatch.context() as tam:
            tam.setattr(viec, "kiem_huy", kiem_huy)
            with pytest.raises(HuyDemo):
                ngan_luot.tra_nop_lai(viec, MODULE, KHAU, [f"PC-DEMO-MOI-{i}" for i in range(10)])
        assert core.dem["tim"] == sau_so_tim

    _trong_viec(core, kiem)


def test_khong_gom_toan_bo_lich_su_vao_bo_nho(monkeypatch):
    core = CoreGia()

    class BanDemo:
        def __init__(self, ma):
            self.gia_tri = {"ma": ma}

    def kiem(viec):
        dang_song = weakref.WeakSet()
        so_trang = 0

        def tim(bang, **kw):
            nonlocal so_trang
            # Một trang cũ và một dòng ứng viên được giữ; không giữ các trang cũ hơn.
            assert len(dang_song) <= 501
            if kw["gioi_han"] == 1:
                return SimpleNamespace(danh_sach=[BanDemo("PC-DEMO-KHAC")], tiep="1")
            so_trang += 1
            ds = [BanDemo(f"PC-DEMO-KHAC-{so_trang}-{i}") for i in range(500)]
            if so_trang == 1:
                ds[0] = BanDemo("PC-DEMO-0")
            dang_song.update(ds)
            return SimpleNamespace(danh_sach=ds, tiep=str(so_trang) if so_trang < 8 else None)

        monkeypatch.setattr(viec.ngan, "tim", tim)
        ds = ngan_luot._quet_dong_nop_lai(viec, MODULE, KHAU, dict.fromkeys(f"PC-DEMO-{i}" for i in range(100)))
        assert so_trang == 8
        assert list(ds) == ["PC-DEMO-0"] and len(ds["PC-DEMO-0"]) == 1
        assert len(dang_song) == 1

    _trong_viec(core, kiem)


@pytest.mark.parametrize("so_dong_phu", [0, 1001], ids=["quet_het", "fallback"])
def test_q5_ro_tung_truong_hop_o_ca_hai_duong(so_dong_phu):
    core = CoreGia()

    def kiem(viec):
        cac_luot = [_luot("PL-DEMO-A"), _luot("PL-DEMO-Z"), _luot("PL-DEMO-MUI-GIO"),
                    _luot("PL-DEMO-SAI-MODULE", "demo_khac"),
                    _luot("PL-DEMO-SAI-KHAU", khau="cfo_duyet"), _luot("PL-DEMO-HIEN-TAI")]
        ma_co_do = ("PC-DEMO-GIO", "PC-DEMO-DANG", "PC-DEMO-SAI-MODULE", "PC-DEMO-SAI-KHAU",
                    "PC-DEMO-KHONG-CO", "PC-DEMO-KHONG-KIEM", "PC-DEMO-KHAC", "PC-DEMO-HET-KHONG-KIEM")
        cac_ma = [*ma_co_do, "PC-DEMO-HOA", "PC-DEMO-HIEN-TAI", "PC-DEMO-DAT", "PC-DEMO-SAI",
                  "PC-DEMO-HET-DAT", "PC-DEMO-HET-SAI"]
        cac_dong = [_dong("PL-DEMO-A", ma) for ma in cac_ma]
        # Hòa thời gian thực: ma_luot Z thắng, dù chuỗi thời điểm A lớn hơn.
        cac_dong.append(_dong("PL-DEMO-Z", "PC-DEMO-HOA", "KHONG_CHON"))
        # Lượt mã cao hơn nhưng thời điểm thực cũ hơn không được thắng.
        cac_dong.append(_dong("PL-DEMO-MUI-GIO", "PC-DEMO-GIO", "KHONG_CHON"))
        cac_dong.extend((_dong("PL-DEMO-DO-DANG", "PC-DEMO-DANG", "KHONG_CHON"),
                        _dong("PL-DEMO-SAI-MODULE", "PC-DEMO-SAI-MODULE", "KHONG_CHON"),
                        _dong("PL-DEMO-SAI-KHAU", "PC-DEMO-SAI-KHAU", "KHONG_CHON")))
        cac_dong = [(k, {**g, "ly_do": "KHONG_CHON"}) if k["ma"] == "PC-DEMO-HIEN-TAI" else (k, g)
                    for k, g in cac_dong]
        cac_dong.append(_dong("PL-DEMO-HIEN-TAI", "PC-DEMO-HIEN-TAI"))
        cac_dong.extend(_dong("PL-DEMO-A", f"PC-DEMO-PHU-{i:04}") for i in range(so_dong_phu))
        cac_kq = []
        for hau_to, kq in (("DAT", "dat"), ("SAI", "sai"), ("KHONG-KIEM", "khong_kiem"),
                           ("KHAC", "DEMO_KHAC"), ("HET-DAT", "dat"), ("HET-SAI", "sai"),
                           ("HET-KHONG-KIEM", "khong_kiem")):
            cac_kq.append(({"ma_luot": "PL-DEMO-A", "ma": "PC-DEMO-" + hau_to, "khau": KHAU},
                           {"ma_module": MODULE, "loai": "chi_phi_demo", "ket_qua": kq}))
        for bang, ds in (("luot", cac_luot), ("dong_luot", cac_dong), ("ket_qua_kiem", cac_kq)):
            ghi_lay_hoac_tao_nhieu(viec, bang, ds)
        for luot in core._ngan[app.ma, "luot"]:
            luot["tao_luc"] = {"PL-DEMO-A": "2026-11-20T21:00:00+07:00",
                               "PL-DEMO-Z": "2026-11-20T14:00:00+00:00",
                               "PL-DEMO-MUI-GIO": "2026-11-20T13:59:00+00:00"}.get(
                                   luot["ma_luot"], "2026-11-20T15:00:00+00:00")
        for kq in core._ngan[app.ma, "ket_qua_kiem"]:
            if kq["ma"].startswith("PC-DEMO-HET-"):
                kq["het_han_luc"] = "2025-01-01T00:00:00+07:00"
        viec._ma_luot_phan_luong = "PL-DEMO-HIEN-TAI"
        assert tra_nop_lai_cu(viec, MODULE, KHAU, cac_ma) == frozenset(ma_co_do)
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, cac_ma * 2) == frozenset(ma_co_do)

    _trong_viec(core, kiem)


@pytest.mark.parametrize("so_dong", [200000, 200001])
def test_giu_tran_200000_dong_moi_ma_nhu_duong_cu(so_dong):
    """Mô phỏng ngăn toàn lượt ghi dở; trần tính riêng mã, không tính mã ngoài lô."""
    def tim(bang, *, loc, gioi_han, tiep=None, **kw):
        if "ma" in loc and loc["ma"] != "PC-DEMO-TRAN":
            return SimpleNamespace(danh_sach=[], tiep=None)
        dau = int(tiep or 0)
        cuoi = min(so_dong, dau + gioi_han)
        ds = [SimpleNamespace(gia_tri={"ma": "PC-DEMO-TRAN", "ma_luot": f"PL-DEMO-{i:06}"})
              for i in range(dau, cuoi)]
        return SimpleNamespace(danh_sach=ds, tiep=str(cuoi) if cuoi < so_dong else None)

    viec = SimpleNamespace(kiem_huy=lambda: None, ngan=SimpleNamespace(tim=tim, doc=lambda *a, **kw: None))
    cac_ma = ["PC-DEMO-TRAN", *(f"PC-DEMO-MOI-{i}" for i in range(4010))]
    for ham in (tra_nop_lai_cu, ngan_luot.tra_nop_lai):
        if so_dong == 200001:
            with pytest.raises(LoiNghiepVu) as exc:
                ham(viec, MODULE, KHAU, cac_ma)
            assert exc.value.ma == "VUOT_GIOI_HAN"
        else:
            assert ham(viec, MODULE, KHAU, cac_ma) == frozenset()
