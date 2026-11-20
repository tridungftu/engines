"""PL-9G/PL-9B: đã kiểm bằng Core giả (CoreGia), chưa đo trên Core thật.

Chạy: .venv/Scripts/python -B e_phan_luong/tests/do_hieu_nang.py
--pha core: giữ chế độ đếm CoreGia N=1.000/5.000/10.000.
--pha thuan (mặc định; may là bí danh): chỉ mục test, JSON/Excel
N=10.000/25.000/50.000; ghi kết quả N=1.000/5.000/10.000.
Engine thuần = tổng giây - hợp các khoảng SDK gọi Core giả, gồm SDK phía engine.
Mỗi ca có một lượt làm ấm riêng ngoài bộ mẫu; giải phóng Core giả ngoài đồng hồ.
--ho-so: cProfile lượt riêng, không dùng giây có profiler để ước tính.
Không có ca lớn trong pytest. Không sửa SDK/gói. MB = 10^6 byte.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fractions import Fraction
import cProfile
import gc
import hashlib
import inspect
from importlib.metadata import version
import json
from pathlib import Path
import platform
import pstats
import sys
import threading
import time
import tracemalloc
from unittest.mock import patch
from uuid import uuid4

import openpyxl

sys.dont_write_bytecode = True
TESTS = Path(__file__).resolve().parent
GOI = TESTS.parent / "goi/e_phan_luong"
sys.path[:0] = [str(GOI), str(TESTS)]
from kho_tri_thuc_sdk.thu import CoreGia, _DuongGia, _loi
from kho_tri_thuc_sdk import __version__ as PHIEN_BAN_SDK
from kho_tri_thuc_sdk.engine import NganXungDot
from e_phan_luong import chon_mau, chot_ky, ngan_luot, phan_luong
from e_phan_luong.chay import app
from e_phan_luong.doc_lo import TOI_DA_BYTE, TOI_DA_DONG
from demo.sinh_bang_demo import khuon_demo, sinh_xlsx, TIEU_DE

MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CAC_CA = ("json_trong", "json_nop_lai", "excel_trong", "excel_nop_lai",
          "ghi_ket_qua_trong", "ghi_ket_qua_nop_lai")
CACH_DEM = ("doc", "tim", "lo_ghi", "tai_tep_vao", "tai_tep_ra")
NGUONG = {k: {"so": str(v), "tien_te": "VND"} for k, v in
          (("pm", 5000000000), ("te", 3000000000), ("sad", 250000000))}


def cac_cong_core():
    """Đọc ranh giới SDK hiện cài; không bỏ sót cửa mới khi chạy lại."""
    cay = ast.parse(inspect.getsource(_DuongGia))
    return tuple(sorted({n.func.attr for n in ast.walk(cay)
                         if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                         and isinstance(n.func.value, ast.Attribute)
                         and isinstance(n.func.value.value, ast.Name)
                         and n.func.value.value.id == "self" and n.func.value.attr == "_core"}))


class DongHoCore:
    """Bọc instance test, không sửa SDK; đo cả lần gọi lỗi/gửi lại.

    Khóa bảo vệ bộ đếm và hợp khoảng wall time qua các luồng. Lời gọi nội bộ
    Core -> Core không đếm/trừ lại. Tổng từng cửa có thể chồng do gia hạn;
    chỉ HỢP khoảng được trừ khỏi tổng wall time. Chi phí wrapper nằm trong
    engine thuần, nên số đo hơi bảo thủ. Không đo CPU time.
    """
    def __init__(self, core, *, dong_ho=time.perf_counter):
        self.core, self.dong_ho = core, dong_ho
        self.khoa = threading.Lock()
        self.cuc_bo = threading.local()
        self.dem, self.giay_cua = Counter(), Counter()
        self.giay = 0.0
        self.dang_goi = 0
        self.cu = {}

    def boc(self, ten, ham):
        def goi(*args, **kw):
            if getattr(self.cuc_bo, "trong_core", False):
                return ham(*args, **kw)
            self.cuc_bo.trong_core = True
            with self.khoa:
                dau = self.dong_ho()
                if self.dang_goi == 0:
                    self.dau_hop = dau
                self.dang_goi += 1
                self.dem[ten] += 1
            try:
                return ham(*args, **kw)
            finally:
                with self.khoa:
                    cuoi = self.dong_ho()
                    self.giay_cua[ten] += cuoi - dau
                    self.dang_goi -= 1
                    if self.dang_goi == 0:
                        self.giay += cuoi - self.dau_hop
                self.cuc_bo.trong_core = False
        return goi

    def __enter__(self):
        for ten in cac_cong_core():
            self.cu[ten] = self.core.__dict__.get(ten, None)
            setattr(self.core, ten, self.boc(ten, getattr(self.core, ten)))
        return self

    def __exit__(self, *exc):
        for ten, cu in self.cu.items():
            if cu is None:
                delattr(self.core, ten)
            else:
                setattr(self.core, ten, cu)


def doc_ho_so(ho_so):
    """Self time chỉ xếp hàm Python engine; cumulative vẫn chứa Core bên dưới.

    SDK self time là cận dưới: không gồm stdlib/thư viện được SDK gọi.
    cProfile chỉ theo luồng chạy việc; gia hạn vẫn do đồng hồ Core đo đủ.
    """
    ds, sdk, duong_gia = [], 0.0, 0.0
    nguon, dong_dau = inspect.getsourcelines(_DuongGia)
    for (tep, dong, ten), (cc, nc, tt, ct, _) in pstats.Stats(ho_so).stats.items():
        duong = Path(tep)
        if duong.parent == GOI / "e_phan_luong":
            ds.append({"ham": f"{duong.name}:{dong}:{ten}", "so_goi": nc,
                       "self_giay": round(tt, 6), "cumulative_giay_gom_core": round(ct, 6)})
        if "kho_tri_thuc_sdk" in duong.parts and duong.name == "engine.py":
            sdk += tt
        if ("kho_tri_thuc_sdk" in duong.parts and duong.name == "thu.py"
                and dong_dau <= dong < dong_dau + len(nguon)):
            duong_gia += tt
    return {"top_5_engine_self": sorted(ds, key=lambda d: d["self_giay"], reverse=True)[:5],
            "sdk_engine_py_self_giay_can_duoi": round(sdk, 6),
            "sdk_duong_gia_self_giay_can_duoi": round(duong_gia, 6),
            "sdk_phia_engine_self_giay_can_duoi": round(sdk + duong_gia, 6),
            "ghi_chu": "Lượt riêng có cProfile; self time SDK là cận dưới, không dùng để ước tính Core thật."}


class CoreDem(CoreGia):
    """Chỉ đếm tại cổng Core; mọi hành vi vẫn là CoreGia nguyên bản."""
    def __init__(self):
        super().__init__()
        self.dem = Counter()
        self.trong_tra_nop_lai = False

    def _tang_dem(self, ten):
        self.dem[ten] += 1
        if self.trong_tra_nop_lai:
            self.dem["tra_nop_lai_" + ten] += 1

    def _ngan_doc(self, *args, **kw):
        self._tang_dem("doc")
        return super()._ngan_doc(*args, **kw)

    def _ngan_tim(self, *args, **kw):
        self._tang_dem("tim")
        return super()._ngan_tim(*args, **kw)

    def _ngan_ghi_lo(self, *args, **kw):
        self._tang_dem("lo_ghi")
        return super()._ngan_ghi_lo(*args, **kw)

    def _mo_tep(self, *args, **kw):
        self._tang_dem("tai_tep_vao")
        return super()._mo_tep(*args, **kw)

    def _tai_tep_ra(self, *args, **kw):
        self._tang_dem("tai_tep_ra")
        return super()._tai_tep_ra(*args, **kw)


class CoreChiMuc(CoreDem):
    """Ngăn dict CHỈ TRONG TEST, không phải bản mô phỏng Core thật về tốc độ.

    Lọc bằng chỉ mục theo tổ hợp khóa; helper CoreGia kiểm quyền/pháp nhân,
    kiểu dữ liệu, hết hạn, sort và cursor.
    Lô chỉ đưa các dòng có thể bị chạm/xung đột vào CoreGia để tránh deepcopy
    toàn ngăn. Chỉ công bố chúng vào kho dict sau khi CoreGia chấp nhận cả lô.
    Không hỗ trợ phép lọc khác dấu bằng (cổng SDK 2.2.0 cũng chưa có).
    """
    def __init__(self):
        super().__init__()
        self.kho = defaultdict(dict)
        self.chi_muc = {}

    @staticmethod
    def _gia_tri(kb, cot, dong):
        kieu = {t["ma"]: t["kieu"] for t in kb["truong"]}
        return tuple(Decimal(str(dong[c])) if dong.get(c) is not None
                     and kieu.get(c) in {"so", "so_tien"} else
                     datetime.fromisoformat(dong[c]) if dong.get(c) is not None
                     and kieu.get(c) == "thoi_diem" else dong.get(c) for c in cot)

    def _chon(self, ma, bang, kb, loc):
        cot = tuple(sorted(loc))
        cm = (ma, bang, cot)
        if cm not in self.chi_muc:
            idx = defaultdict(set)
            for id_, dong in self.kho[ma, bang].items():
                idx[self._gia_tri(kb, cot, dong)].add(id_)
            self.chi_muc[cm] = idx
        ids = self.chi_muc[cm].get(self._gia_tri(kb, cot, loc), ())
        return [self.kho[ma, bang][i] for i in ids]

    def _loc(self, ma, instance, bang, loc, viec_id, *, khoa=False):
        kb, pn = self._bang_ngan(ma, bang, viec_id, instance)
        loc = (self._khoa_ngan(kb, loc, pn) if khoa else
               self._gia_tri_ngan(kb, loc or {}, khoa=bool(loc)))
        if kb["pham_vi"] == "phap_nhan":
            loc["phap_nhan_id"] = pn
        return kb, self._chon(ma, bang, kb, loc)

    def _ngan_doc(self, ma, instance, bang, khoa, **kw):
        with self._lock:
            _, ds = self._loc(ma, instance, bang, khoa, kw.get("viec_id"), khoa=True)
            self._ngan = {(ma, bang): ds}
            try:
                return super()._ngan_doc(ma, instance, bang, khoa, **kw)
            finally:
                self._ngan = {}

    def _ngan_tim(self, ma, instance, bang, **kw):
        with self._lock:
            _, ds = self._loc(ma, instance, bang, kw.get("loc"), kw.get("viec_id"))
            self._ngan = {(ma, bang): ds}
            try:
                return super()._ngan_tim(ma, instance, bang, **kw)
            finally:
                self._ngan = {}

    def _cong_bo(self, tam):
        for b, ds in tam.items():
            kb = next(k for k in self._phieu[b[0]]["ngan_du_lieu"] if k["bang"] == b[1])
            for d in ds.values():
                cu = self.kho[b].get(d["id"])
                for (m, t, cot), idx in self.chi_muc.items():
                    if (m, t) == b:
                        if cu is not None:
                            gia = self._gia_tri(kb, cot, cu)
                            idx[gia].discard(d["id"])
                            if not idx[gia]:
                                del idx[gia]
                        idx[self._gia_tri(kb, cot, d)].add(d["id"])
                self.kho[b][d["id"]] = d

    def _ngan_ghi_lo(self, ma, instance, lenh, khoa, **kw):
        """Overlay ch? c?c d?ng b? s?a; commit c? l? sau m?i ki?m tra.

        Ki?u/kh?a/quy?n/h?t h?n d?ng helper CoreGia; unique, CAS, idem v?
        l? theo c?ng th? t? v?i CoreGia 2.2.0. Kh?ng sao ch?p to?n ng?n.
        """
        with self._lock:
            self._tang_dem("lo_ghi")
            if not isinstance(lenh, list) or not 1 <= len(lenh) <= 100:
                raise self._sai_ngan()
            if not isinstance(khoa, str) or not 8 <= len(khoa) <= 200:
                raise self._sai_ngan()
            for l in lenh:
                self._bang_ngan(ma, l.get("bang"), kw.get("viec_id"), instance)
            than = json.dumps(lenh, sort_keys=True, ensure_ascii=False, allow_nan=False)
            idem = (ma, khoa)
            self.nhat_ky.append(("ngan", ma, kw.get("viec_id"), khoa))
            if idem in self._idem_ngan:
                cu, kq = self._idem_ngan[idem]
                if cu != than:
                    raise _loi("KHOA_CHONG_TRUNG_KHAC_NOI_DUNG", "Kh?a ?? d?ng cho n?i dung kh?c.", 409)
                return deepcopy(kq)
            tam, ket_qua = defaultdict(dict), []
            chi_muc_tam = {}

            def chon(bang, kb, loc):
                # Ch? m?c overlay ???c c?p nh?t khi m?t d?ng trong l? ??i.
                cm = (bang, tuple(sorted(loc)))
                if cm not in chi_muc_tam:
                    idx = defaultdict(set)
                    for i, d in tam[ma, bang].items():
                        idx[self._gia_tri(kb, cm[1], d)].add(i)
                    chi_muc_tam[cm] = idx
                ids = chi_muc_tam[cm].get(self._gia_tri(kb, cm[1], loc), ())
                ds = [d for d in self._chon(ma, bang, kb, loc) if d["id"] not in tam[ma, bang]]
                return ds + [tam[ma, bang][i] for i in ids]

            for l in lenh:
                bang, tt = l["bang"], l["thao_tac"]
                kb, pn = self._bang_ngan(ma, bang, kw.get("viec_id"), instance)
                if tt not in ("them", "sua", "lay_hoac_tao"):
                    raise self._sai_ngan()
                if self._xung_dot_ngan[bang] > 0:
                    self._xung_dot_ngan[bang] -= 1
                    raise NganXungDot()
                gt = self._gia_tri_ngan(kb, l.get("gia_tri", {}))
                d = None
                if tt != "them":
                    loc = self._khoa_ngan(kb, l.get("khoa"), pn, lay_hoac_tao=tt == "lay_hoac_tao")
                    ds = chon(bang, kb, loc)
                    d = ds[0] if ds else None
                da_tao = d is None
                if tt == "sua":
                    if d is None:
                        raise _loi("NGAN_KHONG_THAY", "Kh?ng th?y b?n ghi c?n s?a.", 404)
                    if type(l.get("row_version")) is not int:
                        raise self._sai_ngan()
                    if l["row_version"] != d["row_version"]:
                        raise NganXungDot()
                if tt == "lay_hoac_tao" and d is not None:
                    ket_qua.append(dict(id=d["id"], row_version=d["row_version"], da_tao=False))
                    continue
                moi = deepcopy(d or {})
                if tt == "lay_hoac_tao":
                    moi.update(loc)
                moi.update(gt)
                moi["phap_nhan_id"] = pn if kb["pham_vi"] == "phap_nhan" else None
                self._gia_tri_ngan(kb, {k: v for k, v in moi.items() if k not in
                    {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}}, tao=True)
                for cot in kb.get("duy_nhat", []):
                    if all(moi.get(c) is not None for c in cot):
                        if any(d is None or cu["id"] != d["id"]
                               for cu in chon(bang, kb, {c: moi[c] for c in cot})):
                            raise NganXungDot()
                now = datetime.now(timezone(timedelta(hours=7)))
                moi.update(id=moi.get("id", str(uuid4())),
                           row_version=1 if da_tao else d["row_version"] + 1,
                           tao_luc=moi.get("tao_luc", now.isoformat()),
                           sua_luc=None if da_tao else now.isoformat(), viec_id=kw.get("viec_id"),
                           het_han_luc=(now + timedelta(days=kb["giu_toi_da_ngay"])).isoformat()
                           if kb.get("giu_toi_da_ngay") is not None else None)
                cu_tam = tam[ma, bang].get(moi["id"])
                for (t, cot), idx in chi_muc_tam.items():
                    if t == bang:
                        if cu_tam is not None:
                            idx[self._gia_tri(kb, cot, cu_tam)].discard(moi["id"])
                        idx[self._gia_tri(kb, cot, moi)].add(moi["id"])
                tam[ma, bang][moi["id"]] = moi
                ket_qua.append(dict(id=moi["id"], row_version=moi["row_version"], da_tao=da_tao))
            self._cong_bo(tam)
            result = {"ket_qua": ket_qua}
            self._idem_ngan[idem] = (than, deepcopy(result))
            self.so_lan_ghi["ngan"] += 1
            if self._mat_xac_nhan["ngan"] > 0:
                self._mat_xac_nhan["ngan"] -= 1
                raise _loi("MAT_PHAN_HOI", "M?t ph?n h?i (gi? l?p).", 503, True)
            return result

    def xem_ngan(self, ma_engine, bang):
        with self._lock:
            return deepcopy(list(self.kho[ma_engine, bang].values()))


def tao_lo(so_dong):
    if not 1 <= so_dong <= TOI_DA_DONG:
        raise ValueError("Số dòng DEMO phải nằm trong trần của engine.")
    return {"phien_ban": 1, "ma_module": "demo_thanh_toan", "ky": "2026-11",
            "nguong": deepcopy(NGUONG), "nghiep_vu": [
                {"ma": f"PC-DEMO-PERF-{i:05}", "ngay": "2026-11-16",
                 "loai": "chi_phi_khac", "so_tien": {"so": "371234567.123456", "tien_te": "VND"},
                 "dien_giai": "Công ty DEMO Ánh Dương chi phí DEMO"}
                for i in range(so_dong)]}


def ma_hoa(nut):
    return json.dumps(nut, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def tham_so():
    return {"khau": "ktt_duyet", "ma_module": "demo_thanh_toan",
            "nguong_json": json.dumps(NGUONG),
            "danh_muc_loai_json": json.dumps([{"ma": "chi_phi_khac", "ten": "Chi phí DEMO", "mo_ta": "DEMO"}]),
            "khuon_cot_json": json.dumps(khuon_demo(), ensure_ascii=False)}


@contextmanager
def tat_dinh(core):
    cu = ngan_luot.tra_nop_lai
    def tra(*args, **kw):
        core.trong_tra_nop_lai = True
        try:
            return cu(*args, **kw)
        finally:
            core.trong_tra_nop_lai = False
    with patch.object(chon_mau, "sinh_hat_giong", lambda: bytes(range(32))), \
         patch.object(chot_ky, "ky_hien_tai", lambda *a: "2026-11"), \
         patch.object(phan_luong, "tra_nop_lai", tra):
        yield


@contextmanager
def tach_core_gia():
    """Không giữ kho fake của mẫu trước qua transport/ngăn trên app dùng chung.

    SDK tự gán lại hai thuộc tính khi chay; chỉ dọn tham chiếu của test trước
    setup và sau khi SDK đã dừng luồng gia hạn. Tránh tính hủy kho fake cũ
    vào engine thuần của mẫu tiếp theo. Không sửa SDK hoặc dữ liệu ngăn.
    """
    app._dt = app.ngan = None
    try:
        yield
    finally:
        app._dt = app.ngan = None


def goi(core, nang_luc, pb):
    nl = next(n for n in app.phieu["nang_luc"] if n["ma"] == nang_luc)
    cho_phep = {t["ma"] for t in nl["tham_so"]}
    kq = core.chay_thu(app, nang_luc, pb,
                       {k: v for k, v in tham_so().items() if k in cho_phep})
    assert kq["trang_thai"] == "XONG", kq
    return kq["ket_qua"]


def nap(core, ca, so_dong):
    lo = tao_lo(so_dong)
    nl = "audit.phan_luong@1"
    if ca.startswith("ghi_ket_qua"):
        ref = core.them_tep("truoc-DEMO.json", ma_hoa(lo), "application/json")
        t = goi(core, nl, {"loai": "tep", "tep": ref})["truong"]
        raw = ma_hoa({"phien_ban": 1, "ma_module": lo["ma_module"], "ket_qua": [
            {"ma_luot": t["ma_luot"], "ma": d["ma"], "khau": "ktt_duyet", "ket_qua": "dat"}
            for d in lo["nghiep_vu"]]})
        nl = "audit.ghi_ket_qua@1"
    elif ca.startswith("excel"):
        hang = [TIEU_DE[:4]] + [[d["ma"], d["ngay"], d["so_tien"]["so"], "VND"]
                               for d in lo["nghiep_vu"]]
        raw = sinh_xlsx(hang, cong_thuc=False)  # 200.004 ô ở N=50.000 < 250.000.
    else:
        raw = ma_hoa(lo)
    assert len(raw) <= TOI_DA_BYTE
    ref = core.them_tep("tai-DEMO.xlsx" if ca.startswith("excel") else "tai-DEMO.json", raw,
                        MIME_XLSX if ca.startswith("excel") else "application/json")
    return nl, {"loai": "tep", "tep": ref}, hashlib.sha256(raw).hexdigest()


def do_mot(ca, so_dong, *, lop_core=CoreDem, bo_nho=False, ho_so=False):
    """Setup ngoài đồng hồ/bộ đếm; đo toàn lời gọi công khai của engine.

    Ca ghi_trong có sẵn lượt phân luồng bắt buộc, bảng kết quả kiểm trống.
    Ca ghi_nop_lai có cả lượt và kết quả dat trước đó; đo nộp trùng đúng Q5.
    Đo giây khi tắt tracemalloc; chạy riêng cùng dữ liệu/trạng thái để đo MB.
    Engine thuần vẫn gồm SDK phía engine; không phải thời gian Core thật.
    Giao việc/xem kết quả ở ngoài đồng hồ. Gia hạn dùng nhịp thật 20 giây
    thay vì nhịp 0,01 giây chỉ dành cho test của CoreGia.
    """
    assert ca in CAC_CA
    core = lop_core()
    with tat_dinh(core), tach_core_gia():
        nl, pb, bam = nap(core, ca, so_dong)
        if ca.endswith("nop_lai"):
            goi(core, nl, pb)
        core.dem.clear()
        nl_phieu = next(n for n in app.phieu["nang_luc"] if n["ma"] == nl)
        cho_phep = {t["ma"] for t in nl_phieu["tham_so"]}
        viec_id = core.giao_viec(nl, pb, {k: v for k, v in tham_so().items() if k in cho_phep})
        gc.collect()
        profiler = cProfile.Profile() if ho_so else None
        if bo_nho:
            tracemalloc.start()
        try:
            with DongHoCore(core) as dong_ho:
                bat_dau = time.perf_counter()
                if profiler:
                    profiler.enable()
                try:
                    core.chay(app, khoang_gia_han=20)
                finally:
                    if profiler:
                        profiler.disable()
                    giay = time.perf_counter() - bat_dau
            dinh = tracemalloc.get_traced_memory()[1] if bo_nho else None
        finally:
            if bo_nho:
                tracemalloc.stop()
        kq = core.xem(viec_id)
        assert kq["trang_thai"] == "XONG", kq
        ra = kq["ket_qua"]
    t = ra["truong"]
    assert (t["so_dong_nhan"] + t["so_trung"] if ca.startswith("ghi") else t["so_nghiep_vu"]) == so_dong
    han = next(n["gioi_han"]["thoi_han_giay"] for n in app.phieu["nang_luc"] if n["ma"] == nl)
    dem_kq = {k: v for k, v in t.items() if type(v) in {int, bool}}
    ket_qua = {"ca": ca, "so_dong": so_dong, "ngan": lop_core.__name__, "trang_thai": "XONG",
            "giay": round(giay, 6), "MB": None if dinh is None else round(dinh / 1000000, 3),
            "giay_core_gia": round(dong_ho.giay, 6),
            "giay_engine_thuan": round(giay - dong_ho.giay, 6),
            "giay_core_theo_cua": {k: round(v, 6) for k, v in dong_ho.giay_cua.items()},
            "dem_moi_cong_core": dict(dong_ho.dem), "tong_moi_cong_core": sum(dong_ho.dem.values()),
            "co_profiler": ho_so,
            "tracemalloc_dinh_byte": dinh, "thoi_han_giay": han,
            "dem": dict(core.dem), "tong_goi": sum(core.dem[k] for k in CACH_DEM),
            "ket_qua_dem": dem_kq, "sha256": bam}
    if bo_nho:
        # Lượt đo MB đã xong: không mang kho fake của nó sang lượt đo giây.
        del core, dong_ho
        gc.collect()
        rieng = do_mot(ca, so_dong, lop_core=lop_core, bo_nho=False, ho_so=ho_so)
        assert rieng["dem"] == ket_qua["dem"] and rieng["ket_qua_dem"] == dem_kq
        for k in ("giay", "giay_core_gia", "giay_engine_thuan", "giay_core_theo_cua",
                  "dem_moi_cong_core", "tong_moi_cong_core"):
            ket_qua[k] = rieng[k]
        ket_qua["giay_co_tracemalloc"] = round(giay, 6)
    if profiler:
        ket_qua["ho_so"] = doc_ho_so(profiler)
    return ket_qua


def uoc_tinh_dem(cac_mau, dich=50000):
    """Hồi quy tuyến tính số gọi theo N; làm tròn lên, giữ sai số mẫu.

    Không ngoại suy giây CoreGia (quét/copy tuyến tính làm nó gần bậc hai).
    Đếm phần dư/page/ceil lô được báo qua sai_so_toi_da, không giấu làm tròn.
    """
    xs = [m["so_dong"] for m in cac_mau]
    assert len(set(xs)) >= 2
    # Số gọi là số nguyên: dùng phân số để ceil không cộng thừa một lời
    # gọi vì sai số float (ví dụ 50005.00000000001).
    x_tb = Fraction(sum(xs), len(xs))
    duoi = sum((x - x_tb) ** 2 for x in xs)
    ket_qua = {}
    for k in CACH_DEM + ("tra_nop_lai_doc", "tra_nop_lai_tim"):
        ys = [m["dem"].get(k, 0) for m in cac_mau]
        y_tb = Fraction(sum(ys), len(ys))
        a = sum((x - x_tb) * (y - y_tb) for x, y in zip(xs, ys)) / duoi
        b = y_tb - a * x_tb
        sai_so = max(abs(y - (a * x + b)) for x, y in zip(xs, ys))
        from math import ceil
        ket_qua[k] = {"moi_dong": float(a), "co_dinh": float(b),
                      "uoc_tinh": max(0, ceil(a * dich + b + sai_so)),
                      "sai_so_toi_da": float(sai_so)}
    return ket_qua


def bang_uoc_tinh(mau_core, mau_may):
    bang = []
    for may in mau_may:
        ca, n = may["ca"], may["so_dong"]
        mau = [m for m in mau_core if m["ca"] == ca and not m.get("co_profiler")]
        if len(mau) < 2 or may.get("co_profiler"):
            continue
        # Dùng số gọi ĐO THẬT ở N đích, gồm cả giao thức; không mã cứng
        # calls/dòng, nên chạy lại được sau khi ghép PL-9F.
        tong = may["tong_moi_cong_core"]
        thuan = may["giay_engine_thuan"]
        cc6 = may["dem"].get("tra_nop_lai_tim", 0)
        tra = cc6 + may["dem"].get("tra_nop_lai_doc", 0)
        cac_n = sorted(mau, key=lambda m: m["so_dong"])
        khac = [m for m in cac_n if m["so_dong"] != n and "tong_moi_cong_core" in m]
        if not khac:
            continue
        # Hệ số calls bảo thủ: đường thẳng qua điểm đích và từng mẫu khác,
        # giữ intercept >= 0 và phần dư dương lớn nhất trên tất cả mẫu.
        a_goi = max(0, max((tong - m["tong_moi_cong_core"]) / (n - m["so_dong"]) for m in khac))
        b_goi = max(0, max(m["tong_moi_cong_core"] - a_goi * m["so_dong"] for m in mau))
        # Lấy giây/dòng cao nhất đã đo để không che tăng phi tuyến.
        giay_dong = max(m["giay_engine_thuan"] / m["so_dong"] for m in mau)
        for tre in (2, 5, 10):
            giay = thuan + tong * tre / 1000
            # Dư >=2 lần theo phiếu: chỉ dùng nửa ngân sách 300 giây.
            a = giay_dong + a_goi * tre / 1000
            b = b_goi * tre / 1000
            ngoai_suy = min(TOI_DA_DONG, max(0, int((may["thoi_han_giay"] / 2 - b) / a)))
            an_toan = min(n, ngoai_suy)
            bang.append({"nhan": "ước tính, chưa đo trên Core thật", "ca": ca, "so_dong": n,
                         "tre_ms": tre, "giay_uoc_tinh": round(giay, 3), "tong_goi_uoc_tinh": tong,
                         "giay_engine_thuan": thuan, "nguon_so_goi": "đo thật tại N đích, gồm giao thức",
                         "cc6_tim_phan_tram": round(100 * cc6 / tong, 2),
                         "tra_nop_lai_phan_tram": round(100 * tra / tong, 2),
                         "trong_300_giay": giay <= may["thoi_han_giay"],
                         "co_lo_an_toan_uoc_tinh_du_2_lan": an_toan,
                         "co_lo_ngoai_suy_du_2_lan": ngoai_suy,
                         "ghi_chu": "Giây/dòng lớn nhất đã đo + đường bao calls; cỡ an toàn chặn ở N lớn nhất đã đo. Cột ngoại suy có thể vượt miền đã đo, chưa kiểm Core thật."})
    return bang


def xu_huong(cac_mau):
    """Một lượt/mốc chỉ là dấu hiệu, không kết luận thống kê; ngưỡng 25%."""
    ds = sorted(cac_mau, key=lambda m: m["so_dong"])
    def ti_so(k):
        xs = [m[k] / m["so_dong"] for m in ds]
        return max(xs) / min(xs) if min(xs) > 0 else None
    he_so = ti_so("giay_engine_thuan")
    return {"ca": ds[0]["ca"], "co_mau": [m["so_dong"] for m in ds],
            "engine_giay_moi_1000_dong": [round(m["giay_engine_thuan"] * 1000 / m["so_dong"], 4) for m in ds],
            "ty_so_engine_moi_dong_max_min": he_so,
            "ty_so_core_gia_moi_dong_max_min": ti_so("giay_core_gia"),
            "gan_tuyen_tinh_trong_mau": he_so is not None and he_so <= 1.25,
            "ghi_chu": "Một lượt/mốc, sai khác <=25% coi gần tuyến tính trong mẫu; chưa phải bảo đảm SLA."}


def in_json(nut):
    print(json.dumps(nut, ensure_ascii=False), flush=True)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pha", choices=("core", "may", "thuan", "tat_ca"), default="thuan")
    ap.add_argument("--ca", choices=CAC_CA, action="append")
    ap.add_argument("--co-mau", type=int, action="append", help="Thay các cỡ mẫu mặc định của pha.")
    ap.add_argument("--bo-nho", action="store_true", help="Đo tracemalloc ở lượt riêng (chậm).")
    ap.add_argument("--ho-so", action="store_true", help="cProfile riêng mốc lớn nhất mỗi ca.")
    ap.add_argument("--khong-lam-am", action="store_true", help="Bỏ lượt làm ấm riêng trước mỗi ca.")
    args = ap.parse_args()
    in_json({"python": platform.python_version(), "he_dieu_hanh": platform.platform(),
             "bat_dau": datetime.now().astimezone().isoformat(), "sdk": PHIEN_BAN_SDK,
             "thu_vien": {ten: version(ten) for ten in ("openpyxl", "et_xmlfile", "defusedxml")},
             "openpyxl_dung_lxml": openpyxl.LXML,
             "phuong_phap": __doc__, "ngoai_tru": "Không đo HTTP/Core thật; không gồm setup. Có mọi cửa SDK/Core và gia hạn 20 giây.",
             "cac_cong_core_duoc_boc": cac_cong_core(),
             "bam_runtime": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((GOI / "e_phan_luong").glob("*.py"))}})
    mau_core, mau_may = [], []
    for pha in ("core", "may"):
        if args.pha not in (("may", "thuan", "tat_ca") if pha == "may" else ("core", "tat_ca")):
            continue
        for ca in args.ca or CAC_CA:
            ns = args.co_mau or ([1000, 5000, 10000] if pha == "core" or ca.startswith("ghi")
                                 else [10000, 25000, 50000])
            if pha == "may" and not args.khong_lam_am:
                in_json({"bat_dau_lam_am": ca, "N": ns[0]})
                in_json({"lam_am_ngoai_bo_mau": do_mot(ca, ns[0], lop_core=CoreChiMuc)})
            for n in ns:
                in_json({"bat_dau_ca": ca, "pha": pha, "N": n})
                dung = threading.Event()
                def bao():
                    while not dung.wait(30):
                        in_json({"dang_do": ca, "pha": pha, "N": n})
                thread = threading.Thread(target=bao, daemon=True)
                thread.start()
                try:
                    kq = do_mot(ca, n, lop_core=CoreDem if pha == "core" else CoreChiMuc,
                                bo_nho=args.bo_nho and pha == "may")
                    (mau_core if pha == "core" else mau_may).append(kq)
                    in_json(kq)
                finally:
                    dung.set()
                    thread.join()
    for ca in args.ca or CAC_CA:
        mau = [m for m in mau_core if m["ca"] == ca]
        if len({m["so_dong"] for m in mau}) >= 2:
            dem = uoc_tinh_dem(mau, 50000)
            in_json({"nhan": "ước tính, chưa đo trên Core thật", "ca": ca,
                     "co_mau_CoreGia": [m["so_dong"] for m in mau], "so_dong": 50000,
                     "dem_core_50000_uoc_tinh": dem,
                     "tong_goi_50000_uoc_tinh": sum(dem[k]["uoc_tinh"] for k in CACH_DEM)})
    for ca in args.ca or CAC_CA:
        mau = [m for m in mau_may if m["ca"] == ca]
        if mau:
            lon = max(mau, key=lambda m: m["so_dong"])
            huong = xu_huong(mau) if len(mau) >= 2 else None
        if len(mau) >= 2:
            in_json({"xu_huong": huong})
            for hang in bang_uoc_tinh(mau, [lon]):
                in_json(hang)
        if mau and (args.ho_so or huong is not None and not huong["gan_tuyen_tinh_trong_mau"]):
            in_json({"bat_dau_ho_so": ca, "N": lon["so_dong"]})
            in_json({"ho_so_luot_rieng": do_mot(ca, lon["so_dong"], lop_core=CoreChiMuc, ho_so=True)})
    in_json({"ket_thuc": datetime.now().astimezone().isoformat()})


if __name__ == "__main__":
    main()

