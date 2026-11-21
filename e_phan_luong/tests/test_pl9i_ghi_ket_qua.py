"""PL-9I: bản tham chiếu PL-9G chép nguyên trước tối ưu; chỉ DEMO/CoreGia.

Các hàm _chuan_bi/_da_ghi/_tao_cap_moi/ghi_ket_qua bên dưới cố định theo
nhánh lúc bắt đầu PL-9I; không gọi lại thuật toán đọc trước của mã mới.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re

from e_phan_luong import doi_bac, ket_qua, ngan_chung, nguong, ty_le
from e_phan_luong.kieu import CHUA_PHAN_LOAI, KQ_SAI, MAU_NGOAI
from e_phan_luong.loi import loi
from e_phan_luong.phan_loai import doc_danh_muc_loai


@dataclass(frozen=True)
class _DongGhi:
    gia_tri: dict
    sua_loai: bool

    @property
    def khoa(self) -> dict:
        return {cot: self.gia_tri[cot] for cot in ("ma_luot", "ma", "khau")}


def _da_ghi(viec, dong: _DongGhi) -> bool:
    # Lượt giữ 400 ngày, kết quả 365 ngày: dòng đã ẩn vẫn là dấu chống trùng.
    return viec.ngan.doc("ket_qua_kiem", dong.khoa, gom_het_han=True) is not None


def _chuan_bi(viec, tep: ket_qua.KetQuaTep) -> dict[tuple[str, str], list[_DongGhi]]:
    """Kiểm toàn bộ tệp trước lệnh ghi đầu tiên, giữ thứ tự chi_so mỗi cặp."""
    ts = viec.tham_so
    khau = ts.get("khau")
    ma_module = ts.get("ma_module", "")
    if (not isinstance(khau, str)
            or re.fullmatch(r"[a-z][a-z0-9_]{0,39}", khau) is None
            or not isinstance(ma_module, str)
            or (ma_module and re.fullmatch(r"[a-z][a-z0-9_]{0,30}", ma_module) is None)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if ma_module and ma_module != tep.ma_module:
        raise loi("DU_LIEU_KHONG_HOP_LE")

    danh_muc = doc_danh_muc_loai(ts.get("danh_muc_loai_json"))
    ng = None
    if any(d.ket_qua == KQ_SAI for d in tep.dong):
        nguong_json = ts.get("nguong_json")
        if nguong_json is not None and not isinstance(nguong_json, str):
            raise loi("THAM_SO_KHONG_HOP_LE")
        ng = nguong.doc_nguong(tep.nguong, nguong_json)

    nhom = {}
    cac_luot = {}
    for dong in sorted(tep.dong, key=lambda d: d.chi_so):
        viec.kiem_huy()
        if dong.ma_luot not in cac_luot:
            cac_luot[dong.ma_luot] = viec.ngan.doc("luot", {"ma_luot": dong.ma_luot})
        luot = cac_luot[dong.ma_luot]
        if luot is None:
            raise loi("LUOT_KHONG_TON_TAI")
        if (dong.khau != khau or luot.gia_tri.get("khau") != dong.khau
                or luot.gia_tri.get("ma_module") != tep.ma_module):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        if (dong.loai_dung is not None and dong.loai_dung != CHUA_PHAN_LOAI
                and dong.loai_dung not in danh_muc):
            raise loi("DU_LIEU_KHONG_HOP_LE")

        ban_ghi = viec.ngan.doc("dong_luot", {"ma_luot": dong.ma_luot, "ma": dong.ma})
        dong_luot = {} if ban_ghi is None else ban_ghi.gia_tri
        if ban_ghi is not None and (dong_luot.get("ma_module") != tep.ma_module
                                   or dong_luot.get("khau") != dong.khau):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        loai_goc = dong_luot.get("loai")
        loai = dong.loai_dung or loai_goc or CHUA_PHAN_LOAI
        sua_loai = (ban_ghi is not None and dong.loai_dung is not None
                    and dong.loai_dung != loai_goc)
        muc_sai = ket_qua.muc_sai(dong.so_tien_sai, ng) if dong.ket_qua == KQ_SAI else None
        gia_tri = {
            "ma_luot": dong.ma_luot, "ma": dong.ma, "khau": dong.khau,
            "ma_module": tep.ma_module, "loai": loai, "ket_qua": dong.ket_qua,
            "muc_sai": muc_sai, "nguon_mau": ket_qua.nguon_mau(dong_luot.get("ly_do")),
            "nguon_loai_sai": dong_luot.get("nguon_loai") if sua_loai else None,
        }
        nhom.setdefault((dong.khau, loai), []).append(_DongGhi(gia_tri, sua_loai))
    return nhom


def _tao_cap_moi(viec, khoa: dict, dong: list[_DongGhi], cs: ty_le.ChinhSach) -> None:
    """Tạo nền bằng lay_hoac_tao; luôn đọc lại nền trước khi sửa CAS."""
    def lap_lenh(lo):
        if (viec.ngan.doc("ty_le", khoa) is None
                and any(not _da_ghi(viec, d) for d in dong)):
            lo.lay_hoac_tao("ty_le", khoa, ty_le.ve_ban_ghi(
                ty_le.moi(khoa["khau"], khoa["loai"], cs)))

    ngan_chung.ghi_lo_thu_lai(viec, lap_lenh)


def ghi_ket_qua(viec, tep: ket_qua.KetQuaTep) -> dict[str, int]:
    """Trả số đếm của các lô đã ghi; không trả tỷ lệ hay trạng thái bậc.

    Trong mỗi lần thử lại: đọc lại ty_le và dấu chống trùng, tính lại toàn
    bộ lô. Chỉ cộng số đếm sau khi lô được Core xác nhận thành công.
    """
    cs = ty_le.doc_chinh_sach(viec.tham_so.get("chinh_sach_json"))
    cac_nhom = _chuan_bi(viec, tep)
    tong = {"so_dong_nhan": 0, "so_trung": tep.so_trung_trong_tep,
            "so_ngoai_mau": 0, "so_sua_loai": 0}
    cap_da_doi = set()
    for cap, dong in cac_nhom.items():
        khoa = dict(zip(("khau", "loai"), cap))
        _tao_cap_moi(viec, khoa, dong, cs)
        for dau in range(0, len(dong), 99):
            nhom = dong[dau:dau + 99]
            dem = {}
            da_doi = False

            def lap_lenh(lo):
                nonlocal dem, da_doi
                dem = {cot: 0 for cot in tong}
                da_doi = False
                ban_ghi = viec.ngan.doc("ty_le", khoa)
                tt = None if ban_ghi is None else ty_le.tu_ban_ghi(ban_ghi.gia_tri)
                luc = datetime.now(timezone.utc).isoformat()
                for d in nhom:
                    viec.kiem_huy()
                    if _da_ghi(viec, d):
                        dem["so_trung"] += 1
                        continue
                    # Cặp mới đã tạo bằng lay_hoac_tao, không ghi đè nền cũ.
                    if tt is None:
                        raise loi("NGAN_BAN")
                    gt = d.gia_tri
                    tt, doi = doi_bac.cap_nhat(tt, doi_bac.MotKetQua(
                        gt["nguon_mau"], gt["ket_qua"], gt["muc_sai"]), cs, luc=luc)
                    da_doi = da_doi or doi
                    # them phải xung đột nếu việc khác vừa ghi cùng kết quả.
                    lo.them("ket_qua_kiem", gt)
                    dem["so_dong_nhan"] += 1
                    dem["so_ngoai_mau"] += int(gt["nguon_mau"] == MAU_NGOAI)
                    dem["so_sua_loai"] += int(d.sua_loai)
                if dem["so_dong_nhan"]:
                    lo.sua("ty_le", khoa, ty_le.ve_ban_ghi(tt), row_version=ban_ghi.row_version)

            ngan_chung.ghi_lo_thu_lai(viec, lap_lenh)
            for cot in tong:
                tong[cot] += dem[cot]
            if da_doi:
                cap_da_doi.add(cap)
    return {**tong, "so_cap_doi_bac": len(cap_da_doi)}


# Hết bản tham chiếu PL-9G. Test phía dưới gọi riêng mã cũ và mã mới.
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
import json
import random
import sys

import pytest
from conftest import trang_thai_so_sanh
from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganXungDot, ViecDaHuy
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import ngan_ket_qua
from e_phan_luong.chay import app
from test_pl3_ngan_ket_qua import (
    KHAU, LOAI, LOAI_DUNG, MA_LUOT, MA_MODULE, NGUONG, THAM_SO,
    dong_demo, dung_luot, ma_hoa, tep_demo, trong_viec,
)


class _GioDemo(datetime):
    @classmethod
    def now(cls, tz=None):
        luc = cls(2026, 11, 21, 4, 38, tzinfo=timezone.utc)
        return luc.astimezone(tz) if tz is not None else luc.replace(tzinfo=None)


@pytest.fixture(autouse=True)
def gio_doi_bac_demo(monkeypatch):
    # So cả doi_bac_luc; chỉ ID/thời điểm do Core tự cấp được chuẩn hóa.
    monkeypatch.setattr(sys.modules[__name__], "datetime", _GioDemo)
    monkeypatch.setattr(ngan_ket_qua, "datetime", _GioDemo)


class _CoreDem(CoreGia):
    """CoreGia nguyên bản; chỉ ghi lại tên cửa, bảng và đối số."""
    def __init__(self):
        super().__init__()
        self.doc = []
        self.tim = []

    def _ngan_doc(self, ma, instance, bang, khoa, **kw):
        self.doc.append((bang, deepcopy(khoa), kw.get("gom_het_han", False)))
        return super()._ngan_doc(ma, instance, bang, khoa, **kw)

    def _ngan_tim(self, ma, instance, bang, **kw):
        self.tim.append((bang, deepcopy(kw)))
        return super()._ngan_tim(ma, instance, bang, **kw)


def _chay(core, ham, tep, ts=THAM_SO):
    def xu_ly(viec):
        viec.tham_so = deepcopy(ts)
        try:
            return {"dem": ham(viec, tep)}
        except LoiNghiepVu as exc:
            return {"loi": exc.ma}
    return trong_viec(core, xu_ly)


def _anh_ngan(core):
    # Giữ TOÀN BỘ cột nghiệp vụ, pháp nhân và row_version của cả bảng,
    # kể cả kết quả hết hạn. ID, giờ lưu/hết hạn, viec_id là metadata Core.
    cot_tu_sinh = {"id", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
    return {
        bang: sorted(({k: v for k, v in d.items() if k not in cot_tu_sinh}
                      for d in core.xem_ngan(app.ma, bang)),
                     key=lambda d: tuple(d.get(k, "") for k in ("ma_luot", "ma", "khau", "loai")))
        for bang in ("ket_qua_kiem", "ty_le")
    }


def _nap(core, cac_bang, het_han=()):
    def nap(viec):
        for bang, ds in cac_bang.items():
            for dau in range(0, len(ds), 100):
                with viec.ngan.lo() as lo:
                    for gt in ds[dau:dau + 100]:
                        lo.them(bang, gt)
    trong_viec(core, nap)
    # Đổi riêng metadata của fake để mô phỏng 365 ngày, không sửa dữ liệu.
    for d in core._ngan.get((app.ma, "ket_qua_kiem"), []):
        if (d["ma_luot"], d["ma"], d["khau"]) in het_han:
            d["het_han_luc"] = "2025-10-30T00:00:00+07:00"


def _trang_thai_ngau_nhien(hat):
    rng = random.Random(202611210900 + hat)
    ds = {b: [] for b in ("luot", "dong_luot", "ket_qua_kiem", "ty_le")}
    dong_tep, het_han = [], set()
    for i in range(rng.randint(1, 4)):
        ma_luot = f"PL-DEMO-9I-{hat:03}-{i}"
        ds["luot"].append({"ma_luot": ma_luot, "ma_module": MA_MODULE, "khau": KHAU,
                           "hat_giong": "ab" * 32, "bam_dau_vao": "sha256:" + "12" * 32})
        for j in range(10 if hat % 24 == 12 and i == 0 else rng.randint(3, 28)):
            ma = f"PC-DEMO-9I-{i}-{j:04}"
            loai_goc = rng.choice((LOAI, LOAI_DUNG, CHUA_PHAN_LOAI))
            ly_do = rng.choice(("CHON_MAU", "KHONG_CHON", "VUOT_TE", "CHON_MAU,NOP_LAI"))
            if rng.random() < 0.8:
                ds["dong_luot"].append({
                    "ma_luot": ma_luot, "ma": ma, "ma_module": MA_MODULE, "khau": KHAU,
                    "ly_do": ly_do, "loai": loai_goc,
                    "nguon_loai": rng.choice(("module", "quy_tac", "ai", "chua_phan_loai")),
                })
            kq = rng.choice(("dat", "dat", "sai", "khong_kiem"))
            d = {"ma_luot": ma_luot, "ma": ma, "khau": KHAU, "ket_qua": kq,
                 "loai_dung": rng.choice((None, loai_goc, LOAI_DUNG, CHUA_PHAN_LOAI))}
            if kq == "sai":
                d["so_tien_sai"] = {"so": rng.choice(("-1", "250000", "2999999", "-3000000")),
                                     "tien_te": "VND"}
            dong_tep.append(d)
            if rng.random() < 0.3:
                ds["ket_qua_kiem"].append({
                    "ma_luot": ma_luot, "ma": ma, "khau": KHAU, "ma_module": MA_MODULE,
                    "loai": loai_goc, "ket_qua": rng.choice(("dat", "sai", "khong_kiem")),
                    "muc_sai": "nho", "nguon_mau": ket_qua.nguon_mau(ly_do),
                    "nguon_loai_sai": None,
                })
                if rng.random() < 0.5:
                    het_han.add((ma_luot, ma, KHAU))
        # Lịch sử lớn so với tệp: quét vượt ngân sách rồi quay về doc.
        if hat % 24 == 12 and i == 0:
            ds["dong_luot"].extend({
                "ma_luot": ma_luot, "ma": f"PC-DEMO-LICHSU-{j:04}", "ma_module": MA_MODULE,
                "khau": KHAU, "ly_do": "KHONG_CHON", "loai": LOAI, "nguon_loai": "module",
            } for j in range(501))
    cs = ty_le.ChinhSach()
    for loai in (LOAI, LOAI_DUNG, CHUA_PHAN_LOAI):
        if rng.random() < 0.75:
            tt = replace(ty_le.moi(KHAU, loai, cs), bac=rng.choice(cs.bac),
                         che_do=rng.choice(("bac", "toan_bo")),
                         mau_sach_toan_bo=rng.choice((0, 10, 29)))
            ds["ty_le"].append(ty_le.ve_ban_ghi(tt))
    rng.shuffle(dong_tep)
    if hat % 3 == 0:
        dong_tep.extend(deepcopy(rng.choices(dong_tep, k=3)))
    ts = deepcopy(THAM_SO)
    co_nguong_tep = rng.choice((True, False))
    # Q1: ngưỡng tệp thắng ngưỡng cài đặt khác; đôi lúc chỉ có cài đặt.
    ts["nguong_json"] = json.dumps(NGUONG if not co_nguong_tep else {
        ten: {"so": str(so), "tien_te": "VND"}
        for ten, so in (("pm", 500), ("te", 300), ("sad", 25))})
    tep = tep_demo(dong_tep, nguong=NGUONG if co_nguong_tep else None)
    loi_ca = hat % 24
    if loi_ca == 0:
        ds["luot"].pop()
    elif loi_ca in (1, 2):
        ds["luot"][0]["ma_module" if loi_ca == 1 else "khau"] = "demo_khac"
    elif loi_ca in (3, 4):
        ds["dong_luot"][0]["ma_module" if loi_ca == 3 else "khau"] = "demo_khac"
    elif loi_ca == 5:
        dong_tep[0]["loai_dung"] = "loai_demo_ngoai_danh_muc"
    elif loi_ca == 6:
        dong_tep[0].update(ket_qua="sai", so_tien_sai={"so": "1", "tien_te": "USD"})
    elif loi_ca == 7:
        tep["nguong"] = None
        ts.pop("nguong_json")
        dong_tep[0].update(ket_qua="sai", so_tien_sai={"so": "1", "tien_te": "VND"})
    elif loi_ca == 8:
        ts["khau"] = "DEMO-sai"
    elif loi_ca == 9:
        ts["ma_module"] = "demo_khac"
    elif loi_ca == 10:
        ts["ma_module"] = "DEMO-sai"
    elif loi_ca == 11:
        ts["danh_muc_loai_json"] = "{}"
    da_doc = ket_qua.doc_ket_qua_json(ma_hoa(tep))
    # Đảo vị trí trong tuple để kiểm việc khôi phục đúng thứ tự chi_so.
    # PL-10B: ranh giới DongKetQua phải có giải thích cho các ca AI sai.
    # Oracle đọc ngăn PL-9G và 240 trạng thái/ngân sách trang giữ nguyên.
    da_doc = replace(da_doc, dong=tuple(replace(d,
        giai_thich="Công ty DEMO Ánh Dương: cần đối chiếu chứng từ gốc.")
        for d in reversed(da_doc.dong)))
    return ds, het_han, da_doc, ts


@pytest.mark.parametrize("hat", trang_thai_so_sanh())
def test_tuong_duong_240_trang_thai_demo_va_gui_lai_ca_tep(hat):
    ds, het_han, tep, ts = _trang_thai_ngau_nhien(hat)
    cu, moi = CoreGia(), CoreGia()
    for core in (cu, moi):
        _nap(core, ds, het_han)
    truoc = _anh_ngan(cu)
    kq_cu = _chay(cu, ghi_ket_qua, tep, ts)
    kq_moi = _chay(moi, ngan_ket_qua.ghi_ket_qua, tep, ts)
    assert kq_cu == kq_moi
    assert _anh_ngan(cu) == _anh_ngan(moi)
    if "loi" in kq_cu:
        assert _anh_ngan(cu) == truoc  # Kiểm hết tệp trước lệnh ghi đầu.
    else:
        sau_lan_dau = _anh_ngan(cu)
        assert _chay(cu, ghi_ket_qua, tep, ts) == _chay(moi, ngan_ket_qua.ghi_ket_qua, tep, ts)
        assert _anh_ngan(cu) == _anh_ngan(moi) == sau_lan_dau



# Lead: biên 2 trang (11 mã, 1.000/1.001 dòng) lặp lại biên 1 trang ở quy mô lớn hơn
# (~36 giây trên CoreGia) → kiểm sâu; kiểm nhanh giữ biên 1 trang 500/501 dòng.
@pytest.mark.parametrize("k,n", [(10, 500), (10, 501),
                                 pytest.param(11, 1000, marks=pytest.mark.sau),
                                 pytest.param(11, 1001, marks=pytest.mark.sau)])
@pytest.mark.parametrize("bang", ["dong_luot", "ket_qua_kiem"])
def test_ngan_sach_vua_du_va_vuot_khong_dung_ban_quet_do(k, n, bang):
    cores = [_CoreDem(), _CoreDem()]
    # Chỉ k mã trong tệp, ở đầu và cuối lịch sử; fallback phải đọc lại
    # TẤT CẢ k mã, kể cả mã đã tìm thấy trong bản quét dở.
    chi_so = [0, *range(n - k + 1, n)]
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo(i) for i in chi_so])))
    for core in cores:
        dung_luot(core, n if bang == "dong_luot" else k)
        if bang == "ket_qua_kiem":
            da_co = [{"ma_luot": MA_LUOT, "ma": dong_demo(i)["ma"], "khau": KHAU,
                      "ma_module": MA_MODULE, "loai": LOAI, "ket_qua": "dat",
                      "nguon_mau": "chon_mau", "muc_sai": None, "nguon_loai_sai": None}
                     for i in range(n)]
            _nap(core, {"ket_qua_kiem": da_co}, {(MA_LUOT, dong_demo(0)["ma"], KHAU)})
        core.doc.clear()
        core.tim.clear()
    assert _chay(cores[0], ghi_ket_qua, tep) == _chay(cores[1], ngan_ket_qua.ghi_ket_qua, tep)
    assert _anh_ngan(cores[0]) == _anh_ngan(cores[1])
    trang = [kw for b, kw in cores[1].tim if b == bang]
    assert len(trang) == (k + 9) // 10
    assert all(kw["gioi_han"] == 500 for kw in trang)
    assert all(kw.get("gom_het_han", False) == (bang == "ket_qua_kiem") for kw in trang)
    assert [sx["truong"] for sx in trang[0]["sap_xep"]] == (
        ["ma_luot", "ma"] if bang == "dong_luot" else ["ma_luot", "ma", "khau"])
    so_doc = sum(b == bang for b, _, _ in cores[1].doc)
    if n % 500 == 0:
        assert so_doc == 0
    else:
        assert so_doc >= k


@pytest.mark.parametrize("bang", ["dong_luot", "ket_qua_kiem"])
def test_chan_vong_tiep_truoc_khi_ghi(bang, monkeypatch):
    core = _CoreDem()
    dung_luot(core, 20)
    goc = core._ngan_tim

    def tim(ma, instance, ten, **kw):
        if ten == bang:
            kw["tiep"] = None
        ra = goc(ma, instance, ten, **kw)
        if ten == bang:
            ra["tiep"] = "0"
        return ra

    monkeypatch.setattr(core, "_ngan_tim", tim)
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo(i) for i in range(20)])))
    assert _chay(core, ngan_ket_qua.ghi_ket_qua, tep) == {"loi": "NGAN_BAN"}
    assert _anh_ngan(core) == {"ket_qua_kiem": [], "ty_le": []}


@pytest.mark.parametrize("bang", ["dong_luot", "ket_qua_kiem"])
def test_kiem_huy_trong_luc_duyet_trang(bang, monkeypatch):
    core = CoreGia()
    dung_luot(core, 20)
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo(i) for i in range(20)])))
    da_tim = [False]
    goc = core._ngan_tim

    def tim(ma, instance, ten, **kw):
        ra = goc(ma, instance, ten, **kw)
        if ten == bang:
            da_tim[0] = True
        return ra

    monkeypatch.setattr(core, "_ngan_tim", tim)

    def xu_ly(viec):
        viec.tham_so = deepcopy(THAM_SO)

        def kiem_huy():
            if da_tim[0]:
                raise ViecDaHuy()

        kiem_goc = viec.kiem_huy
        viec.kiem_huy = kiem_huy
        try:
            with pytest.raises(ViecDaHuy):
                ngan_ket_qua.ghi_ket_qua(viec, tep)
        finally:
            viec.kiem_huy = kiem_goc

    trong_viec(core, xu_ly)
    assert _anh_ngan(core) == {"ket_qua_kiem": [], "ty_le": []}



def _du_lieu_200_dong():
    return {
        "luot": [{"ma_luot": MA_LUOT, "ma_module": MA_MODULE, "khau": KHAU,
                  "hat_giong": "ab" * 32, "bam_dau_vao": "sha256:" + "12" * 32}],
        "dong_luot": [{"ma_luot": MA_LUOT, "ma": dong_demo(i)["ma"], "ma_module": MA_MODULE,
                       "khau": KHAU, "ly_do": "CHON_MAU", "loai": LOAI if i < 99 else LOAI_DUNG,
                       "nguon_loai": "module"} for i in range(200)],
        "ty_le": [ty_le.ve_ban_ghi(ty_le.moi(KHAU, loai, ty_le.ChinhSach()))
                  for loai in (LOAI, LOAI_DUNG)],
    }


def _chen_ket_qua(core, ghi_goc, ma, instance, kw):
    """Việc khác ghi ma=99 vào LOAI; tệp hiện tại đang ghi vào LOAI_DUNG.

    CAS của LOAI_DUNG không đổi: chỉ ràng buộc unique của lo.them mới
    chặn được ghi trùng ở lô đang giữ bản đọc trước cũ.
    """
    khoa = {"khau": KHAU, "loai": LOAI}
    bg = core._ngan_doc(ma, instance, "ty_le", khoa, viec_id=kw["viec_id"])
    tt, _ = doi_bac.cap_nhat(ty_le.tu_ban_ghi(bg["ban_ghi"]),
                            doi_bac.MotKetQua("chon_mau", "dat", None),
                            ty_le.ChinhSach(), luc=_GioDemo.now(timezone.utc).isoformat())
    gt = {"ma_luot": MA_LUOT, "ma": dong_demo(99)["ma"], "khau": KHAU,
          "ma_module": MA_MODULE, "loai": LOAI, "ket_qua": "dat", "muc_sai": None,
          "nguon_mau": "chon_mau", "nguon_loai_sai": None}
    ghi_goc(ma, instance, [
        {"bang": "ket_qua_kiem", "thao_tac": "them", "gia_tri": gt},
        {"bang": "ty_le", "thao_tac": "sua", "khoa": khoa,
         "gia_tri": ty_le.ve_ban_ghi(tt), "row_version": bg["row_version"]},
    ], "PL-DEMO-9I-chen-mot-ket-qua", **kw)


@pytest.mark.parametrize("lich", ["xung_dot", "het_lan", "chen_sau_lo_dau", "chen_truoc_ghi"])
def test_xung_dot_giua_chung_tuong_duong_khong_cong_hai_lan(lich, monkeypatch):
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo(i) for i in range(200)])))
    cores = [_CoreDem(), _CoreDem()]
    cac_dem = []
    cac_xung_dot = []
    for core, ham in zip(cores, (ghi_ket_qua, ngan_ket_qua.ghi_ket_qua)):
        _nap(core, _du_lieu_200_dong())
        goc = core._ngan_ghi_lo
        da_chen = [False]
        xung_dot = [0]

        def ghi(ma, instance, lenh, khoa, **kw):
            lo_dau = any(l.get("gia_tri", {}).get("ma") == dong_demo(0)["ma"] for l in lenh)
            lo_sau = any(l.get("gia_tri", {}).get("ma") == dong_demo(99)["ma"] for l in lenh)
            if not da_chen[0] and lo_sau:
                if lich in ("xung_dot", "het_lan"):
                    core.gay_xung_dot_ngan("ket_qua_kiem", 4 if lich == "het_lan" else 1)
                    da_chen[0] = True
                elif lich == "chen_truoc_ghi":
                    _chen_ket_qua(core, goc, ma, instance, kw)
                    da_chen[0] = True
            try:
                ra = goc(ma, instance, lenh, khoa, **kw)
            except NganXungDot:
                xung_dot[0] += 1
                raise
            if lich == "chen_sau_lo_dau" and lo_dau and not da_chen[0]:
                _chen_ket_qua(core, goc, ma, instance, kw)
                da_chen[0] = True
            return ra

        with monkeypatch.context() as m:
            m.setattr(core, "_ngan_ghi_lo", ghi)
            dem = _chay(core, ham, tep)
            if lich == "het_lan":
                assert dem == {"loi": "NGAN_BAN"}
                assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 99
                dem = _chay(core, ham, tep)
                assert (dem["dem"]["so_dong_nhan"], dem["dem"]["so_trung"]) == (101, 99)
            elif lich.startswith("chen"):
                assert (dem["dem"]["so_dong_nhan"], dem["dem"]["so_trung"]) == (199, 1)
            else:
                assert (dem["dem"]["so_dong_nhan"], dem["dem"]["so_trung"]) == (200, 0)
            cac_dem.append(dem)
        cac_xung_dot.append(xung_dot[0])
        assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == 200
        assert sum(int(d["mau_12t"]) for d in core.xem_ngan(app.ma, "ty_le")) == 200
    assert cac_dem[0] == cac_dem[1]
    assert _anh_ngan(cores[0]) == _anh_ngan(cores[1])
    if lich == "chen_sau_lo_dau":
        assert cac_xung_dot == [0, 1]  # Bản đọc trước cũ đã bị lo.them chặn.
    elif lich == "het_lan":
        assert cac_xung_dot == [4, 4]
    else:
        assert cac_xung_dot == [1, 1]


@pytest.mark.parametrize("so_lan", [1, 3, 4])
def test_tao_cap_moi_chi_doc_truoc_lan_dau_doc_tung_khoa_khi_thu_lai(so_lan):
    cores = [_CoreDem(), _CoreDem()]
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo()])))
    cac_dem = []
    for core, ham in zip(cores, (ghi_ket_qua, ngan_ket_qua.ghi_ket_qua)):
        dung_luot(core)
        core.doc.clear()
        core.tim.clear()
        core.gay_xung_dot_ngan("ty_le", so_lan)
        cac_dem.append(_chay(core, ham, tep))
    assert cac_dem[0] == cac_dem[1]
    assert _anh_ngan(cores[0]) == _anh_ngan(cores[1])
    cac_doc = [(k, gom) for b, k, gom in cores[1].doc if b == "ket_qua_kiem"]
    assert len(cac_doc) == min(so_lan, 3)
    assert all(gom for _, gom in cac_doc)



def _dem_lan_goi(core, ham, tep, monkeypatch):
    """Đếm riêng ngoài lap_lenh và tổng doc+tim, không bỏ đọc CAS."""
    doc_goc, tim_goc = core._ngan_doc, core._ngan_tim
    ghi_goc = ngan_chung.ghi_lo_thu_lai
    trong_lo = [False]
    dem, ngoai_lo = Counter(), Counter()

    def doc(*args, **kw):
        dem["doc"] += 1
        if not trong_lo[0]:
            ngoai_lo["doc"] += 1
        return doc_goc(*args, **kw)

    def tim(*args, **kw):
        dem["tim"] += 1
        if not trong_lo[0]:
            ngoai_lo["tim"] += 1
        return tim_goc(*args, **kw)

    def ghi(*args, **kw):
        trong_lo[0] = True
        try:
            return ghi_goc(*args, **kw)
        finally:
            trong_lo[0] = False

    with monkeypatch.context() as m:
        m.setattr(core, "_ngan_doc", doc)
        m.setattr(core, "_ngan_tim", tim)
        m.setattr(ngan_chung, "ghi_lo_thu_lai", ghi)
        kq = _chay(core, ham, tep)
    return kq, {"doc": dem["doc"], "tim": dem["tim"],
                "tong_doc_tim": sum(dem.values()), "ngoai_lo": sum(ngoai_lo.values())}


def _nhan_ban_fixture(core, bang, n):
    """Nhân fixture DEMO từ một dòng đã được chính CoreGia kiểm hợp lệ.

    Chỉ giảm chi phí dựng dữ liệu của fake; đọc, phân trang, ghi, CAS,
    unique, rollback trong phép đo vẫn dùng CoreGia nguyên bản.
    """
    mau = core._ngan[app.ma, bang][0]
    core._ngan[app.ma, bang] = [
        {**mau, "ma": dong_demo(i)["ma"], "id": f"00000000-0000-4000-8000-{i:012d}"}
        for i in range(n)
    ]


@pytest.mark.parametrize("n,toi_da_goi", [
    (501, 12),
    pytest.param(10000, 120, marks=pytest.mark.sau),
])
def test_so_lan_goi_coregia_doc_tim_ngoai_lo(n, toi_da_goi, monkeypatch):
    # Ca nhanh vẫn qua hai trang, ghi mới và gửi trùng; giữ ca 10.000 ở kiểm sâu.
    core = CoreGia()  # Không chỉ mục thay thế; đo đúng backend SDK.
    dung_luot(core)
    _nhan_ban_fixture(core, "dong_luot", n)
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo(i) for i in range(n)])))
    moi, dem_moi = _dem_lan_goi(core, ngan_ket_qua.ghi_ket_qua, tep, monkeypatch)
    assert moi["dem"]["so_dong_nhan"] == n
    assert dem_moi["ngoai_lo"] <= toi_da_goi
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == n
    truoc = _anh_ngan(core)
    trung, dem_trung = _dem_lan_goi(core, ngan_ket_qua.ghi_ket_qua, tep, monkeypatch)
    assert (trung["dem"]["so_dong_nhan"], trung["dem"]["so_trung"]) == (0, n)
    assert dem_trung["ngoai_lo"] <= toi_da_goi
    assert _anh_ngan(core) == truoc
    # Báo cả tổng có đọc CAS để ngưỡng "ngoài lô ghi" không che số gọi.
    print(json.dumps({"N": n, "CoreGia_ghi_moi": dem_moi,
                      "CoreGia_ghi_trung": dem_trung}, ensure_ascii=False))


@pytest.mark.parametrize("k,so_dong", [
    (1, 501), (10, 501), (11, 1001), (20, 1001),
    *[pytest.param(k, 10001, marks=pytest.mark.sau) for k in (1, 10, 11, 20, 100)],
])
def test_luot_lon_so_voi_tep_dem_ca_phu_phi_lam_tron_ngan_sach(k, so_dong, monkeypatch):
    core = CoreGia()
    dung_luot(core)
    tep1 = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo()])))
    assert _chay(core, ghi_ket_qua, tep1)["dem"]["so_dong_nhan"] == 1
    for bang in ("dong_luot", "ket_qua_kiem"):
        _nhan_ban_fixture(core, bang, so_dong)
    tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([dong_demo(i) for i in range(so_dong-k, so_dong)])))
    truoc = _anh_ngan(core)
    cu, dem_cu = _dem_lan_goi(core, ghi_ket_qua, tep, monkeypatch)
    moi, dem_moi = _dem_lan_goi(core, ngan_ket_qua.ghi_ket_qua, tep, monkeypatch)
    assert cu == moi
    assert _anh_ngan(core) == truoc
    assert dem_moi["tong_doc_tim"] <= dem_cu["tong_doc_tim"] + 2 * max(1, (k + 9)//10)
    if k in (1, 11):
        # Sai biệt tiêu chí đã báo lead: hai ceil không luôn vừa cận +1/lượt.
        assert dem_moi["tong_doc_tim"] > 1.1 * dem_cu["tong_doc_tim"] + 1
        assert dem_moi["tong_doc_tim"] <= 1.1 * dem_cu["tong_doc_tim"] + 2
    else:
        assert dem_moi["tong_doc_tim"] <= 1.1 * dem_cu["tong_doc_tim"] + 1



def test_doc_truoc_tach_luot_khau_va_phap_nhan():
    cores = [_CoreDem(), _CoreDem()]
    cac_dem = []
    for core, ham in zip(cores, (ghi_ket_qua, ngan_ket_qua.ghi_ket_qua)):
        for ma_luot in (MA_LUOT, "PL-DEMO-9I-khac"):
            dung_luot(core, ma_luot=ma_luot)
        gt = {"ma_luot": MA_LUOT, "ma": dong_demo()["ma"], "khau": KHAU,
              "ma_module": MA_MODULE, "loai": LOAI, "ket_qua": "dat", "muc_sai": None,
              "nguon_mau": "chon_mau", "nguon_loai_sai": None}
        # A đã ghi; B chỉ có kết quả ở khâu khác và pháp nhân khác.
        _nap(core, {"ket_qua_kiem": [gt, {**gt, "ma_luot": "PL-DEMO-9I-khac", "khau": "cfo_duyet"}]})

        def phap_nhan_khac(viec):
            with viec.ngan.lo() as lo:
                lo.them("ket_qua_kiem", {**gt, "ma_luot": "PL-DEMO-9I-khac"})

        trong_viec(core, phap_nhan_khac, phap_nhan_id="pn-demo-khac")
        core.doc.clear()
        core.tim.clear()
        tep = ket_qua.doc_ket_qua_json(ma_hoa(tep_demo([
            dong_demo(), dong_demo(ma_luot="PL-DEMO-9I-khac")])))
        cac_dem.append(_chay(core, ham, tep))
    assert cac_dem[0] == cac_dem[1]
    assert (cac_dem[1]["dem"]["so_dong_nhan"], cac_dem[1]["dem"]["so_trung"]) == (1, 1)
    assert _anh_ngan(cores[0]) == _anh_ngan(cores[1])
    assert Counter(b for b, _, _ in cores[1].doc)["luot"] == 2
    assert not any(b in ("dong_luot", "ket_qua_kiem") for b, _, _ in cores[1].doc)
    assert all(kw["loc"]["khau"] == KHAU for b, kw in cores[1].tim if b == "ket_qua_kiem")
