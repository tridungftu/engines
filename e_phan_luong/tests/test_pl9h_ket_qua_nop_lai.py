"""PL-9H: giữ Q5 khi gộp kết quả; đã kiểm bằng Core giả (CoreGia).

Bản tham chiếu chép nguyên thân tra_nop_lai sau PL-9F, chỉ đổi tên.
Mọi trạng thái ngăn, mã và lịch sử trong tệp đều là DEMO.
"""
from collections.abc import Sequence
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from random import Random
from types import SimpleNamespace
import weakref

import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from e_phan_luong import ngan_luot
from e_phan_luong.chay import app
from e_phan_luong.kieu import CHON_MAU, KQ_DAT, KQ_SAI, LY_DO_BAT_BUOC, noi_ly_do, tach_ly_do
from e_phan_luong.ngan_chung import ghi_lay_hoac_tao_nhieu, tim_tat_ca
from e_phan_luong.ngan_luot import _quet_dong_nop_lai
from test_pl9f_tra_nop_lai import (KHAU, MODULE, _CoreDem, _dong, _lich_su_nhieu_dong,
                                  _luot, _trong_viec)


def tra_nop_lai_cu(viec, ma_module: str, khau: str, ds_ma: Sequence[str]) -> frozenset[str]:
    """Q5: chỉ giữ Đỏ của lượt hoàn tất gần nhất chưa có kết quả dat/sai.

    Dòng của lượt ghi dở không có dấu luot bị bỏ qua. So thời điểm có múi giờ,
    không so thứ tự ma_luot hoặc thời điểm riêng của dong_luot. Nếu hai lượt
    trùng thời điểm, dùng ma_luot làm khóa phụ ổn định. Bỏ qua chính lượt
    của việc Core hiện tại để giao lại không tự sinh lý do NOP_LAI.
    """
    cac_ma = dict.fromkeys(ds_ma)
    if not cac_ma:
        return frozenset()
    dong_theo_ma = _quet_dong_nop_lai(viec, ma_module, khau, cac_ma)
    if dong_theo_ma == {}:
        return frozenset()
    luot_da_doc = {}
    nop_lai = set()
    for ma in cac_ma:
        viec.kiem_huy()
        ds = (tim_tat_ca(viec, "dong_luot", {"ma_module": ma_module, "khau": khau, "ma": ma})
              if dong_theo_ma is None else dong_theo_ma.get(ma, ()))
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


class _CoreTheoDoi(_CoreDem):
    """Chỉ thêm bộ đếm; giữ nguyên doc/tim của CoreGia SDK 2.2.0."""

    def __init__(self):
        super().__init__()
        self.cac_doc = []

    def _ngan_doc(self, ma, instance, bang, khoa, **kw):
        self.cac_doc.append((bang, deepcopy(khoa), deepcopy(kw)))
        return super()._ngan_doc(ma, instance, bang, khoa, **kw)

    def dat_lai_dem(self):
        super().dat_lai_dem()
        self.cac_doc.clear()


def _kq(ma_luot, ma, ket_qua, khau=KHAU):
    return ({"ma_luot": ma_luot, "ma": ma, "khau": khau},
            {"ma_module": MODULE, "loai": "chi_phi_demo", "ket_qua": ket_qua})


def _them_ban_phu(core, viec, bang, ma_luot, n):
    """Gieo metadata qua SDK rồi nhân dòng DEMO; cổng đọc/tìm không bị thay."""
    if n <= 0:
        return
    ma = f"PC-DEMO-PHU-{ma_luot}-000000"
    dong = _dong(ma_luot, ma) if bang == "dong_luot" else _kq(ma_luot, ma, "dat")
    ghi_lay_hoac_tao_nhieu(viec, bang, [dong])
    cac_ban = core._ngan[app.ma, bang]
    mau = next(d for d in cac_ban if d["ma"] == ma)
    cac_ban.extend({**mau, "id": f"DEMO-{bang}-{ma_luot}-{i:06}",
                    "ma": f"PC-DEMO-PHU-{ma_luot}-{i:06}"} for i in range(1, n))


@pytest.mark.parametrize("chi_so", range(240))
def test_tuong_duong_240_trang_thai_ngau_nhien_demo(chi_so):
    rng = Random(202611210438 + chi_so)
    core = _CoreTheoDoi()

    def kiem(viec):
        cac_ma = [f"PC-DEMO-{i:02}" for i in range(rng.randint(8, 20))]
        cac_luot, cac_dong, cac_kq, thoi_diem, het_han = [], [], [], {}, set()
        for i in range(rng.randint(8, 16)):
            ml = f"PL-DEMO-{i:02}"
            md = "demo_khac" if i % 7 == 2 else MODULE
            kh = "cfo_duyet" if i % 7 == 3 else KHAU
            if i % 7 != 1:
                cac_luot.append(_luot(ml, md, kh))
            phut = 15 if i in (0, 5) else rng.randrange(30)
            mui = timezone(timedelta(hours=rng.choice((-5, 0, 7, 9))))
            thoi_diem[ml] = datetime(2026, 11, 20, 14, phut, tzinfo=timezone.utc).astimezone(mui).isoformat()
            for ma in rng.sample(cac_ma, rng.randint(1, len(cac_ma))):
                ly_do = rng.choice((CHON_MAU, "KHONG_CHON", "DEMO_KHAC", *sorted(LY_DO_BAT_BUOC),
                                    noi_ly_do((CHON_MAU, "CO_DO_CUNG"))))
                cac_dong.append(_dong(ml, ma, ly_do,
                                      "demo_khac" if rng.randrange(11) == 0 else MODULE,
                                      "cfo_duyet" if rng.randrange(11) == 0 else KHAU))
                kq = rng.choice((None, "dat", "sai", "khong_kiem", "DEMO_KHAC"))
                if kq is not None:
                    cac_kq.append(_kq(ml, ma, kq))
                    if rng.choice((False, True)):
                        het_han.add((ml, ma, KHAU))
                if rng.randrange(3) == 0:
                    cac_kq.append(_kq(ml, ma, rng.choice(("dat", "sai")), "cfo_duyet"))
        # 40 trạng thái có một nhóm ứng viên ở biên ngân sách 1 hoặc 2 trang.
        ml_bien = "PL-DEMO-BIEN"
        if chi_so % 6 == 0:
            k = rng.choice((10, 20))
            cac_luot.append(_luot(ml_bien))
            thoi_diem[ml_bien] = "2026-11-20T23:00:00+07:00"
            for i in range(k):
                ma = f"PC-DEMO-Z-{i:02}"
                cac_ma.append(ma)
                cac_dong.append(_dong(ml_bien, ma, rng.choice((CHON_MAU, *sorted(LY_DO_BAT_BUOC)))))
                kq = rng.choice((None, "dat", "sai", "khong_kiem", "DEMO_KHAC"))
                if kq is not None:
                    cac_kq.append(_kq(ml_bien, ma, kq))
                    if rng.choice((False, True)):
                        het_han.add((ml_bien, ma, KHAU))
                cac_kq.append(_kq(ml_bien, ma, "dat", "cfo_duyet"))
        for bang, ds in (("luot", cac_luot), ("dong_luot", cac_dong), ("ket_qua_kiem", cac_kq)):
            ghi_lay_hoac_tao_nhieu(viec, bang, ds)
        if chi_so % 6 == 0:
            da_co = sum(d["ma_luot"] == ml_bien and d["khau"] == KHAU
                        for d in core._ngan.get((app.ma, "ket_qua_kiem"), []))
            tong = ((k + 9) // 10) * 500 + (chi_so // 6 % 2)
            _them_ban_phu(core, viec, "ket_qua_kiem", ml_bien, tong - da_co)
        if chi_so % 7 == 1:
            _them_ban_phu(core, viec, "dong_luot", "PL-DEMO-DO-DANG",
                          ((len(cac_ma) + 10) // 10) * 500 + 1)
        for luot in core._ngan[app.ma, "luot"]:
            luot["tao_luc"] = thoi_diem[luot["ma_luot"]]
        for kq in core._ngan.get((app.ma, "ket_qua_kiem"), []):
            if (kq["ma_luot"], kq["ma"], kq["khau"]) in het_han:
                kq["het_han_luc"] = "2025-01-01T00:00:00+07:00"
        if chi_so % 3:
            viec._ma_luot_phan_luong = "PL-DEMO-04"
        rng.shuffle(cac_ma)
        ds_ma = [] if chi_so % 17 == 0 else cac_ma + rng.choices(cac_ma, k=10) + ["PC-DEMO-MOI"]
        truoc = deepcopy(core._ngan)
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        core.dat_lai_dem()
        moi = ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma)
        assert moi == cu
        assert isinstance(moi, frozenset)
        assert core._ngan == truoc
        if chi_so % 6 == 0 and ds_ma:
            tim_bien = [kw for bang, kw in core.cac_tim
                        if bang == "ket_qua_kiem" and kw["loc"]["ma_luot"] == ml_bien]
            doc_bien = [kw for bang, kw, _ in core.cac_doc
                        if bang == "ket_qua_kiem" and kw["ma_luot"] == ml_bien]
            assert len(tim_bien) == (k + 9) // 10
            assert len(doc_bien) == (k if chi_so // 6 % 2 else 0)

    _trong_viec(core, kiem)


@pytest.mark.parametrize("n", [1000, 5000, 10000])
@pytest.mark.parametrize("co_lich_su", [False, True], ids=["trong", "nop_lai"])
def test_so_lan_goi_truoc_sau_coregia(n, co_lich_su):
    core = _CoreTheoDoi()

    def kiem(viec):
        ds_ma = (_lich_su_nhieu_dong(core, viec, n) if co_lich_su else
                 [f"PC-DEMO-{i:05}" for i in range(n)])
        core.dat_lai_dem()
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        dem_cu = core.dem.copy()
        core.dat_lai_dem()
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma) == cu
        assert cu == (frozenset(ds_ma) if co_lich_su else frozenset())
        assert core.dem["doc"] == (1 if co_lich_su else 0)
        assert core.dem["tim"] == (2 + (n + 499) // 500 if co_lich_su else 1)
        if n == 10000:
            assert sum(core.dem.values()) <= 60
        print(f"DEMO N={n} {'nop_lai' if co_lich_su else 'trong'}: "
              f"truoc doc={dem_cu['doc']}, tim={dem_cu['tim']}, tong={sum(dem_cu.values())}; "
              f"sau doc={core.dem['doc']}, tim={core.dem['tim']}, tong={sum(core.dem.values())}")

    _trong_viec(core, kiem)


@pytest.mark.parametrize("k,so_dong", [(10, 500), (10, 501), (20, 1000), (20, 1001)])
def test_bien_ngan_sach_bo_ket_qua_do_dang_va_khong_lan_nhom(k, so_dong):
    core = _CoreTheoDoi()

    def kiem(viec):
        ml = "PL-DEMO-LON"
        ds_ma = [f"PC-DEMO-Z-{i:02}" for i in range(k)]
        ghi_lay_hoac_tao_nhieu(viec, "luot", [_luot(ml), _luot("PL-DEMO-NHO")])
        ghi_lay_hoac_tao_nhieu(viec, "dong_luot", [_dong(ml, ma) for ma in ds_ma]
                              + [_dong("PL-DEMO-NHO", "PC-DEMO-NHO")])
        # Ứng viên đầu nằm trong trang quét dở, ứng viên cuối nằm ở trang vượt.
        cac_kq = [_kq(ml, ds_ma[0], "sai"), _kq(ml, ds_ma[-1], "dat"),
                  *(_kq(ml, ma, "dat", "cfo_duyet") for ma in ds_ma),
                  _kq("PL-DEMO-NHO", "PC-DEMO-NHO", "dat")]
        ghi_lay_hoac_tao_nhieu(viec, "ket_qua_kiem", cac_kq)
        _them_ban_phu(core, viec, "ket_qua_kiem", ml, so_dong - 2)
        # Đặt ứng viên đầu trước các dòng phụ, để phát hiện tái dùng quét dở.
        ds_ma[0] = "PC-DEMO-A"
        for bang in ("dong_luot", "ket_qua_kiem"):
            for d in core._ngan[app.ma, bang]:
                if d["ma"] == "PC-DEMO-Z-00":
                    d["ma"] = ds_ma[0]
        for d in core._ngan[app.ma, "ket_qua_kiem"]:
            d["het_han_luc"] = "2025-01-01T00:00:00+07:00"
        ds_ma.append("PC-DEMO-NHO")
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        assert cu == frozenset(ds_ma[1:-2])
        core.dat_lai_dem()
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma * 2) == cu
        vuot = so_dong > ((k + 9) // 10) * 500
        cac_doc = [(khoa, kw) for bang, khoa, kw in core.cac_doc if bang == "ket_qua_kiem"]
        assert [khoa["ma"] for khoa, _ in cac_doc] == (ds_ma[:-1] if vuot else [])
        assert all(kw["gom_het_han"] for _, kw in cac_doc)
        cac_tim = [kw for bang, kw in core.cac_tim if bang == "ket_qua_kiem"]
        assert len(cac_tim) == (k + 9) // 10 + 1
        assert {tuple(sorted(kw["loc"].items())) for kw in cac_tim} == {
            tuple(sorted({"ma_luot": m, "khau": KHAU}.items())) for m in (ml, "PL-DEMO-NHO")}
        for kw in cac_tim:
            assert kw["sap_xep"] == [{"truong": c, "giam": False} for c in ("ma_luot", "ma", "khau")]
            assert kw["gioi_han"] == 500 and kw["gom_het_han"]

    _trong_viec(core, kiem)


@pytest.mark.parametrize("k", [1, 9, 10, 11, 20])
def test_luot_cu_rat_lon_so_voi_ung_vien_giu_can_phu_phi(k):
    core = _CoreTheoDoi()

    def kiem(viec):
        cac_ma = _lich_su_nhieu_dong(core, viec, 10001)
        _them_ban_phu(core, viec, "ket_qua_kiem", "PL-DEMO-DEM", 10001)
        ds_ma = cac_ma[:k]
        core.dat_lai_dem()
        cu = tra_nop_lai_cu(viec, MODULE, KHAU, ds_ma)
        so_cu = sum(core.dem.values())
        core.dat_lai_dem()
        assert ngan_luot.tra_nop_lai(viec, MODULE, KHAU, ds_ma) == cu == frozenset(ds_ma)
        assert sum(core.dem.values()) == so_cu + (k + 9) // 10
        assert sum(core.dem.values()) * 10 <= 11 * so_cu + 10  # Một ma_luot.

    _trong_viec(core, kiem)


@pytest.mark.parametrize("cac_tiep", [("DEMO-A", "DEMO-A"), ("DEMO-A", "DEMO-B", "DEMO-A")])
def test_chong_vong_tiep_ket_qua(monkeypatch, cac_tiep):
    cac_goi = []

    def tim(bang, **kw):
        assert bang == "ket_qua_kiem"
        cac_goi.append(kw)
        assert len(cac_goi) <= len(cac_tiep)
        return SimpleNamespace(danh_sach=[], tiep=cac_tiep[len(cac_goi) - 1])

    viec = SimpleNamespace(kiem_huy=lambda: None, ngan=SimpleNamespace(tim=tim))
    with pytest.raises(LoiNghiepVu) as exc:
        ngan_luot._quet_ket_qua_nop_lai(viec, "PL-DEMO", KHAU, dict.fromkeys(range(40)))
    assert exc.value.ma == "NGAN_BAN"
    assert [kw["tiep"] for kw in cac_goi] == [None, *cac_tiep[:-1]]


@pytest.mark.parametrize("diem_huy", ["truoc_trang", "trong_trang", "giua_trang", "truoc_doc", "giua_doc"])
def test_kiem_huy_khi_quet_va_fallback(monkeypatch, diem_huy):
    core = _CoreTheoDoi()

    class HuyDemo(Exception):
        pass

    def kiem(viec):
        ds_ma = _lich_su_nhieu_dong(core, viec, 20)
        so_dong = 501 if diem_huy in {"truoc_doc", "giua_doc"} else 1000
        _them_ban_phu(core, viec, "ket_qua_kiem", "PL-DEMO-DEM", so_dong)
        core.dat_lai_dem()
        tim_goc = viec.ngan.tim
        so_tim, so_doc, trong_trang, dang_quet = 0, 0, False, False
        quet_goc = ngan_luot._quet_ket_qua_nop_lai

        def quet(*args):
            nonlocal dang_quet
            dang_quet = True
            return quet_goc(*args)

        def tim(bang, **kw):
            nonlocal so_tim, trong_trang
            if bang == "ket_qua_kiem":
                trong_trang = True
                so_tim += 1
            return tim_goc(bang, **kw)

        doc_goc = viec.ngan.doc

        def doc(bang, khoa, **kw):
            nonlocal so_doc
            if bang == "ket_qua_kiem":
                so_doc += 1
            return doc_goc(bang, khoa, **kw)

        def kiem_huy():
            if (diem_huy == "truoc_trang" and dang_quet and so_tim == 0
                    or diem_huy == "trong_trang" and trong_trang
                    or diem_huy == "giua_trang" and so_tim == 1
                    or diem_huy == "truoc_doc" and so_tim == 1
                    or diem_huy == "giua_doc" and so_doc == 1):
                # Các ca giữa trang/trước doc phải đi qua hết vòng duyệt trang.
                if diem_huy in {"giua_trang", "truoc_doc"} and trong_trang:
                    return
                raise HuyDemo

        def tim_co_trang(bang, **kw):
            nonlocal trong_trang
            trang = tim(bang, **kw)
            if bang == "ket_qua_kiem":
                class CacBan:
                    def __iter__(self):
                        nonlocal trong_trang
                        yield from trang.danh_sach
                        trong_trang = False
                return SimpleNamespace(danh_sach=CacBan(), tiep=trang.tiep)
            return trang

        with monkeypatch.context() as tam:
            tam.setattr(ngan_luot, "_quet_ket_qua_nop_lai", quet)
            tam.setattr(viec.ngan, "tim", tim_co_trang)
            tam.setattr(viec.ngan, "doc", doc)
            tam.setattr(viec, "kiem_huy", kiem_huy)
            with pytest.raises(HuyDemo):
                ngan_luot.tra_nop_lai(viec, MODULE, KHAU,
                                      ds_ma[:10] if diem_huy in {"truoc_doc", "giua_doc"} else ds_ma)
        assert so_doc == (1 if diem_huy == "giua_doc" else 0)
        assert so_tim == (0 if diem_huy == "truoc_trang" else 1)

    _trong_viec(core, kiem)


def test_chi_giu_ket_qua_ung_vien_trong_bo_nho():
    dang_song = weakref.WeakSet()
    so_trang = 0

    class BanDemo:
        def __init__(self, ma):
            self.gia_tri = {"ma": ma, "ket_qua": "dat"}

    def tim(bang, **kw):
        nonlocal so_trang
        assert bang == "ket_qua_kiem"
        assert len(dang_song) <= 501
        so_trang += 1
        ds = [BanDemo(f"PC-DEMO-PHU-{so_trang}-{i}") for i in range(500)]
        if so_trang == 1:
            ds[0] = BanDemo("PC-DEMO-0")
        dang_song.update(ds)
        return SimpleNamespace(danh_sach=ds, tiep=str(so_trang) if so_trang < 8 else None)

    viec = SimpleNamespace(kiem_huy=lambda: None, ngan=SimpleNamespace(tim=tim))
    ds = ngan_luot._quet_ket_qua_nop_lai(viec, "PL-DEMO", KHAU,
                                        dict.fromkeys(f"PC-DEMO-{i}" for i in range(100)))
    assert so_trang == 8
    assert list(ds) == ["PC-DEMO-0"]
    assert len(dang_song) == 1
