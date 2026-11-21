"""H2 — đã kiểm bằng Core giả (CoreGia), chỉ Công ty DEMO Ánh Dương.

PL-10B nhận DongKetQua đã đọc; PL-10C sở hữu bộ đọc JSON. Các ca cần
giải thích đặt dữ liệu tại ranh giới này để chạy độc lập khi chưa gộp
PL-10C; vẫn chạy năng lực, ngăn, CAS và tải tệp thật của CoreGia.
"""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import __version__, chot_ky, ket_qua, ngan_ket_qua, ty_le
from e_phan_luong.chay import app
from e_phan_luong.kieu import Tien
from test_pl3_ngan_ket_qua import (
    KHAU, LOAI, LOAI_DUNG, MA_LUOT, MA_MODULE, NGUONG,
    chay_ghi, dong_demo, dung_luot, kiem_loi, tep_demo, trang_thai, trong_viec, truong,
)
from test_pl9b_c4_c5 import cam_c5


GIAI_THICH = "Công ty DEMO Ánh Dương: cần đối chiếu chứng từ gốc trước khi kết luận."
SCHEMA = json.loads((Path(__file__).parent / "schema" / "tep_bai_hoc.schema.json").read_text(
    encoding="utf-8"))
KIEM_SCHEMA = Draft202012Validator(SCHEMA)


def _dong(i=0, *, kq="sai", so="1", loai_dung=None, giai_thich=GIAI_THICH,
          chi_so=None, ma_luot=MA_LUOT):
    return ket_qua.DongKetQua(
        i if chi_so is None else chi_so, ma_luot, dong_demo(i)["ma"], KHAU, kq,
        Tien(Decimal(so), "VND") if kq == "sai" else None, loai_dung,
        giai_thich=giai_thich,
    )


def _tep(ds):
    return ket_qua.KetQuaTep(MA_MODULE, deepcopy(NGUONG), tuple(ds), 0)


def _ghi(core, ds, monkeypatch):
    # Chỉ thay bộ đọc thuộc PL-10C; không thay mã ghi, tải tệp hoặc CoreGia.
    with monkeypatch.context() as m:
        m.setattr(ket_qua, "doc_ket_qua_json", lambda _: _tep(ds))
        return chay_ghi(core, tep_demo([]))


def _bai_hoc(core, dem):
    assert dem["tep_bai_hoc"]["mime"] == "application/json"
    raw = core.doc_tep(dem["tep_bai_hoc"]["tep_id"])
    assert raw.decode("utf-8").encode("utf-8") == raw
    assert "Ánh Dương".encode("utf-8") in raw
    noi_dung = json.loads(raw)
    KIEM_SCHEMA.validate(noi_dung)
    assert noi_dung["phien_ban"] == 1
    assert noi_dung["ma_module"] == MA_MODULE
    assert noi_dung["khau"] == KHAU
    assert noi_dung["phien_ban_engine"] == __version__
    assert len(noi_dung["dong"]) == dem["so_ai_sai"]
    return noi_dung


def _xem_ngan(core):
    return {b["bang"]: core.xem_ngan(app.ma, b["bang"])
            for b in app.phieu["ngan_du_lieu"]}


def _sua_dong(core, ds):
    def sua(viec):
        with viec.ngan.lo() as lo:
            for i, thay in ds:
                khoa = {"ma_luot": MA_LUOT, "ma": dong_demo(i)["ma"]}
                bg = viec.ngan.doc("dong_luot", khoa)
                lo.sua("dong_luot", khoa, thay, row_version=bg.row_version)
    trong_viec(core, sua)


@pytest.mark.parametrize("ly_do", ["CO_DO_CUNG", "VUOT_TE,CO_DO_CUNG", "CO_DO_CUNG,CHON_MAU"])
@pytest.mark.parametrize("so", ["1", "250000", "3000000"])
@pytest.mark.parametrize("che_do", ["bac", "toan_bo"])
def test_ai_da_gan_co_khong_doi_bac_che_do_moc_dem(ly_do, so, che_do, monkeypatch):
    core = CoreGia()
    cs = ty_le.ChinhSach()
    cu = replace(ty_le.moi(KHAU, LOAI, cs), bac=Decimal("0.10"), che_do=che_do,
                 mau_tu_doi_bac=17, loi_tu_doi_bac=1, mau_12t=17, loi_12t=1,
                 mau_sach_toan_bo=19, doi_bac_luc="2026-10-30T00:00:00+07:00")
    dung_luot(core, ly_do=ly_do, tt=cu)
    dem = truong(_ghi(core, [_dong(so=so, giai_thich=None)], monkeypatch))
    moi = trang_thai(core)
    assert (moi.bac, moi.che_do, moi.doi_bac_luc, moi.mau_sach_toan_bo) == (
        cu.bac, cu.che_do, cu.doi_bac_luc, 19)
    chon = int("CHON_MAU" in ly_do)
    assert (moi.mau_tu_doi_bac, moi.loi_tu_doi_bac) == (17 + chon, 1 + chon)
    assert (moi.mau_12t, moi.loi_12t) == (17 + chon, 1 + chon)
    assert moi.loi_sad_12t == int(Decimal(so) >= 250000)
    assert "rui_ro_cao" in moi.nhan  # Rủi ro nghiệp vụ vẫn tính mọi lỗi.
    assert ty_le.p_bac(moi, cs) == ty_le.p_bac(cu, cs)  # Nhãn/điểm không tăng tỷ lệ.
    assert (dem["so_cap_doi_bac"], dem["so_ai_sai"], dem["tep_bai_hoc"]) == (0, 0, None)


@pytest.mark.parametrize("ly_do", ["CHON_MAU", "VUOT_TE", "KHONG_CHON", None, "DEMO_CO_DO_CUNG"])
@pytest.mark.parametrize("so", ["1", "250000", "3000000"])
@pytest.mark.parametrize("che_do", ["bac", "toan_bo"])
def test_ai_bo_sot_van_len_bac_va_giu_q6(ly_do, so, che_do, monkeypatch):
    core = CoreGia()
    cu = replace(ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()), bac=Decimal("0.10"),
                 che_do=che_do, mau_sach_toan_bo=19, mau_tu_doi_bac=17,
                 doi_bac_luc="2026-10-30T00:00:00+07:00")
    dung_luot(core, 0 if ly_do is None else 1, ly_do=ly_do, tt=cu)
    dem = truong(_ghi(core, [_dong(so=so, loai_dung=LOAI)], monkeypatch))
    moi = trang_thai(core)
    ngoai = ly_do in {None, "KHONG_CHON", "DEMO_CO_DO_CUNG"}
    if Decimal(so) >= 3000000 or che_do == "toan_bo":
        assert moi.che_do == "toan_bo"
        assert moi.mau_sach_toan_bo == (0 if Decimal(so) >= 3000000 else 19)
        assert moi.bac == cu.bac
    else:
        assert moi.che_do == "bac"
        assert moi.bac == Decimal("0.30" if ngoai or Decimal(so) >= 250000 else "0.20")
    assert moi.loi_ngoai_mau_12t == int(ngoai)
    assert ("loi_ngoai_mau" in moi.nhan) == ngoai
    assert moi.loi_sad_12t == int(Decimal(so) >= 250000)
    assert moi.loi_12t == moi.mau_12t == int(ly_do == "CHON_MAU")
    bh = _bai_hoc(core, dem)["dong"][0]
    assert (bh["ai_bo_sot"], bh["ai_sai_loai"], bh["da_ghi_truoc"]) == (True, False, False)


@pytest.mark.parametrize("giai_thich", [None, "", " \t\n"])
@pytest.mark.parametrize("loai_loi", ["bo_sot", "ngoai_mau", "sai_loai", "gan_co_sai_loai"])
def test_thieu_giai_thich_tu_choi_toan_tep_truoc_moi_lenh_ghi(loai_loi, giai_thich, monkeypatch):
    core = CoreGia()
    dung_luot(core, 101, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()), nguon_loai="ai")
    if loai_loi == "gan_co_sai_loai":
        _sua_dong(core, [(100, {"ly_do": "CO_DO_CUNG"})])
    # Ép có kỳ cần chốt: lỗi vẫn phải giữ nguyên cả chot_ky/ty_le/hồ sơ.
    monkeypatch.setattr(chot_ky, "ky_hien_tai", lambda *a: "2026-12")
    truoc = _xem_ngan(core)
    cac_lenh = []
    goc = core._ngan_ghi_lo

    def ghi(*args, **kw):
        cac_lenh.append(args)
        return goc(*args, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    ds = [_dong(i, kq="dat", giai_thich=None) for i in range(100)]
    if loai_loi in {"sai_loai", "gan_co_sai_loai"}:
        cuoi = _dong(100, kq="dat", loai_dung=LOAI_DUNG, giai_thich=giai_thich)
    else:
        cuoi = _dong(999 if loai_loi == "ngoai_mau" else 100, giai_thich=giai_thich)
    kiem_loi(_ghi(core, [*ds, cuoi], monkeypatch), "THIEU_GIAI_THICH")
    assert cac_lenh == []
    assert _xem_ngan(core) == truoc


@pytest.mark.parametrize("nguon", ["module", "quy_tac", "ai", "chua_phan_loai"])
@pytest.mark.parametrize("sua", [False, True])
def test_chi_ai_sai_loai_can_giai_thich(nguon, sua, monkeypatch):
    core = CoreGia()
    dung_luot(core, nguon_loai=nguon, ly_do="CO_DO_CUNG")
    d = _dong(kq="dat", loai_dung=LOAI_DUNG if sua else LOAI, giai_thich=None)
    kq = _ghi(core, [d], monkeypatch)
    if nguon == "ai" and sua:
        kiem_loi(kq, "THIEU_GIAI_THICH")
        assert core.xem_ngan(app.ma, "ket_qua_kiem") == []
    else:
        dem = truong(kq)
        assert (dem["so_ai_sai"], dem["tep_bai_hoc"]) == (0, None)
        assert dem["so_sua_loai"] == int(sua)


@pytest.mark.parametrize("kq", ["dat", "sai", "khong_kiem"])
def test_ai_sai_loai_co_bai_hoc_ke_ca_da_gan_co(kq, monkeypatch):
    core = CoreGia()
    dung_luot(core, nguon_loai="ai", ly_do="CO_DO_CUNG")
    dem = truong(_ghi(core, [_dong(kq=kq, loai_dung=LOAI_DUNG)], monkeypatch))
    bh = _bai_hoc(core, dem)["dong"][0]
    assert bh == {
        "ma_luot": MA_LUOT, "ma": dong_demo()["ma"], "loai": LOAI, "loai_dung": LOAI_DUNG,
        "nguon_loai": "ai", "nguon_mau": "bat_buoc", "ket_qua": kq,
        "muc_sai": "nho" if kq == "sai" else None, "ai_bo_sot": False,
        "ai_sai_loai": True, "da_ghi_truoc": False, "giai_thich": GIAI_THICH,
    }


def test_bai_hoc_schema_thu_tu_gui_lai_c4_c5(monkeypatch):
    core = CoreGia()
    dung_luot(core, 7)
    _sua_dong(core, [(1, {"nguon_loai": "ai"}), (2, {"nguon_loai": "ai"}),
                    (3, {"ly_do": "CO_DO_CUNG"}), (5, {"loai": LOAI_DUNG})])
    # Các cặp thống kê làm thay thứ tự duyệt, đầu vào đảo tuple để kiểm chi_so.
    ds = [_dong(0), _dong(1, kq="dat", loai_dung=LOAI_DUNG),
          _dong(2, loai_dung=LOAI_DUNG), _dong(3, giai_thich=None),
          _dong(4, kq="dat", giai_thich="DEMO tùy chọn không lưu"),
          _dong(5), _dong(99, loai_dung=LOAI_DUNG)]
    dem = truong(_ghi(core, list(reversed(ds)), monkeypatch))
    noi_dung = _bai_hoc(core, dem)
    bh = noi_dung["dong"]
    assert [d["ma"] for d in bh] == [dong_demo(i)["ma"] for i in (0, 1, 2, 5, 99)]
    assert [(d["ai_bo_sot"], d["ai_sai_loai"]) for d in bh] == [
        (True, False), (False, True), (True, True), (True, False), (True, False)]
    assert bh[-1]["loai"] is bh[-1]["nguon_loai"] is None
    assert not any(d["da_ghi_truoc"] for d in bh)
    assert len(bh) == dem["so_ai_sai"] == 5
    truoc = _xem_ngan(core)
    lap = truong(_ghi(core, ds, monkeypatch))
    assert (lap["so_dong_nhan"], lap["so_trung"], lap["so_ai_sai"]) == (0, 7, 5)
    bh_lap = _bai_hoc(core, lap)["dong"]
    assert bh_lap == [{**d, "da_ghi_truoc": True} for d in bh]
    assert _xem_ngan(core) == truoc
    chuoi_ngan = json.dumps(truoc, ensure_ascii=False)
    assert "giai_thich" not in chuoi_ngan
    assert GIAI_THICH not in chuoi_ngan
    assert "DEMO tùy chọn không lưu" not in chuoi_ngan
    hat_giong = {d["hat_giong"] for d in truoc["luot"]}
    assert cam_c5(dem, hat_giong, ["5", "10", "20", "30", "100"]) == []
    assert cam_c5(noi_dung, hat_giong, ["5", "10", "20", "30", "100"]) == []
    assert set(dem) == {t["ma"] for t in next(n for n in app.phieu["nang_luc"]
                                            if n["ma"] == "audit.ghi_ket_qua@1")["truong_ra"]}
    Draft202012Validator.check_schema(SCHEMA)
    for du_lieu in ({**noi_dung, "ty_le": 0.3},
                   {**noi_dung, "dong": [{**bh[0], "bac": 0.3}]},
                   {**noi_dung, "dong": [{**bh[0], "giai_thich": "   "}]}):
        with pytest.raises(ValidationError):
            KIEM_SCHEMA.validate(du_lieu)


def test_xung_dot_khong_lap_bai_hoc(monkeypatch):
    core = CoreGia()
    dung_luot(core, 2, tt=ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()))
    core.gay_xung_dot_ngan("ty_le", so_lan=1)
    dem = truong(_ghi(core, [_dong(0), _dong(1)], monkeypatch))
    assert (dem["so_ai_sai"], dem["so_dong_nhan"], dem["so_trung"]) == (2, 2, 0)
    assert len(_bai_hoc(core, dem)["dong"]) == 2
    assert trang_thai(core).loi_12t == 2


def test_bai_hoc_da_het_han_van_gui_lai_va_van_can_giai_thich(monkeypatch):
    core = CoreGia()
    dung_luot(core)
    assert truong(_ghi(core, [_dong()], monkeypatch))["so_dong_nhan"] == 1
    truoc = _xem_ngan(core)
    # Kết quả 365 ngày đã ẩn, lượt 400 ngày vẫn còn; chống trùng phải đọc cả hết hạn.
    monkeypatch.setattr(core, "_con_han", lambda d: "ket_qua" not in d)
    dem = truong(_ghi(core, [_dong()], monkeypatch))
    assert (dem["so_ai_sai"], dem["so_dong_nhan"], dem["so_trung"]) == (1, 0, 1)
    assert _bai_hoc(core, dem)["dong"][0]["da_ghi_truoc"] is True
    kiem_loi(_ghi(core, [_dong(giai_thich=None)], monkeypatch), "THIEU_GIAI_THICH")
    assert _xem_ngan(core) == truoc


def test_lo_sau_loi_gui_lai_van_du_bai_hoc_va_khong_cong_lai(monkeypatch):
    core = CoreGia()
    dung_luot(core, 102)
    ds = [_dong(i) for i in range(102)]
    goc = core._ngan_ghi_lo
    da_gay = False

    def ghi(ma, instance, lenh, khoa, **kw):
        nonlocal da_gay
        if not da_gay and any(l.get("gia_tri", {}).get("ma") == dong_demo(99)["ma"] for l in lenh):
            da_gay = True
            core.gay_xung_dot_ngan("ty_le", so_lan=4)
        return goc(ma, instance, lenh, khoa, **kw)

    monkeypatch.setattr(core, "_ngan_ghi_lo", ghi)
    kiem_loi(_ghi(core, ds, monkeypatch), "NGAN_BAN")
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == trang_thai(core).loi_12t == 99
    dem = truong(_ghi(core, ds, monkeypatch))
    bh = _bai_hoc(core, dem)["dong"]
    assert (dem["so_dong_nhan"], dem["so_trung"], dem["so_ai_sai"]) == (3, 99, 102)
    assert [d["da_ghi_truoc"] for d in bh] == [True] * 99 + [False] * 3
    assert trang_thai(core).loi_12t == trang_thai(core).mau_12t == 102


def test_tai_tep_loi_than_thien_gui_lai_du_bai_hoc(monkeypatch):
    core = CoreGia()
    dung_luot(core, 2)
    ds = [_dong(0), _dong(1)]
    with monkeypatch.context() as m:
        def hong(*args, **kw):
            raise RuntimeError("CHI-TIET-DEMO-KHONG-LO")
        m.setattr(core, "_tai_tep_ra", hong)
        loi = _ghi(core, ds, m)
    assert loi["trang_thai"] == "LOI"
    assert "CHI-TIET-DEMO-KHONG-LO" not in json.dumps(loi["loi"])
    assert GIAI_THICH not in json.dumps(loi["loi"], ensure_ascii=False)
    truoc = _xem_ngan(core)
    dem = truong(_ghi(core, ds, monkeypatch))
    assert (dem["so_dong_nhan"], dem["so_trung"], dem["so_ai_sai"]) == (0, 2, 2)
    assert all(d["da_ghi_truoc"] for d in _bai_hoc(core, dem)["dong"])
    assert _xem_ngan(core) == truoc


def test_mat_xac_nhan_tai_tep_khong_cong_hai_lan(monkeypatch):
    core = CoreGia()
    dung_luot(core)
    core.gay_mat_xac_nhan("tep", so_lan=1)
    dem = truong(_ghi(core, [_dong()], monkeypatch))
    assert (dem["so_ai_sai"], dem["so_dong_nhan"]) == (1, 1)
    assert _bai_hoc(core, dem)["dong"][0]["da_ghi_truoc"] is False
    assert trang_thai(core).loi_12t == 1


def test_loi_da_gan_co_khong_dat_lai_moc_ha_bac_clopper_pearson(monkeypatch):
    core = CoreGia()
    cu = replace(ty_le.moi(KHAU, LOAI, ty_le.ChinhSach()), bac=Decimal("0.20"),
                 mau_tu_doi_bac=59, mau_12t=59, doi_bac_luc="2026-10-30T00:00:00+07:00")
    dung_luot(core, 2, tt=cu)
    _sua_dong(core, [(0, {"ly_do": "CO_DO_CUNG"})])
    assert truong(_ghi(core, [_dong(0, so="3000000", giai_thich=None)], monkeypatch))["so_cap_doi_bac"] == 0
    sau_loi = trang_thai(core)
    assert sau_loi.mau_tu_doi_bac == 59 and sau_loi.doi_bac_luc == cu.doi_bac_luc
    assert "rui_ro_cao" in sau_loi.nhan
    assert truong(_ghi(core, [_dong(1, kq="dat", giai_thich=None)], monkeypatch))["so_cap_doi_bac"] == 1
    assert trang_thai(core).bac == Decimal("0.10")


def test_tran_30_phan_tram_loi_nho_va_chua_phan_loai_giu_nguyen(monkeypatch):
    for loai in (LOAI, "chua_phan_loai"):
        core = CoreGia()
        dung_luot(core, loai=loai, tt=ty_le.moi(KHAU, loai, ty_le.ChinhSach()))
        dem = truong(_ghi(core, [_dong(so="1")], monkeypatch))
        tt = trang_thai(core, loai)
        assert tt.bac == Decimal("0.30") and tt.che_do == "bac"
        assert dem["so_cap_doi_bac"] == 0


def test_json_khong_co_ai_sai_khong_tao_tep_bai_hoc():
    # Đường đọc JSON hiện tại chạy trực tiếp, không cần phần PL-10C.
    core = CoreGia()
    dung_luot(core, ly_do="CO_DO_CUNG")
    dem = truong(chay_ghi(core, tep_demo([dong_demo(ket_qua="sai",
                 so_tien_sai={"so": "3000000", "tien_te": "VND"})])))
    assert (dem["so_ai_sai"], dem["tep_bai_hoc"], dem["so_cap_doi_bac"]) == (0, None, 0)
