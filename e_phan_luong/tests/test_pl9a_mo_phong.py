"""PL-9A: đã kiểm bằng Core giả (CoreGia), Công ty DEMO Ánh Dương.

Chạy báo cáo: python -B -m pytest e_phan_luong/tests/test_pl9a_mo_phong.py -q -s
Chỉ ghim đồng hồ/hạt giống; không thay thuật toán chọn mẫu, đổi bậc hoặc ngăn.
Đáp án độc lập: Fraction + công thức CP 0 lỗi; CDF nhị thức chính xác
tại ngưỡng để xét CP có lỗi. Không gọi thong_ke/doi_bac để tính đáp án.
Ca lớn có tên riêng, chạy mặc định và không xfail.
"""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
from math import comb
from threading import Barrier, Event, Lock
from time import perf_counter

import json
import pytest
import socket
import kho_tri_thuc_sdk.engine as sdk_engine
import kho_tri_thuc_sdk.thu as sdk_thu
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from demo import mo_phong_12_thang as demo
from e_phan_luong import chon_mau, chot_ky, ngan_chung, ngan_ho_so, ngan_ket_qua
from e_phan_luong.chay import app


BAC = (Fraction(3, 10), Fraction(1, 5), Fraction(1, 10), Fraction(1, 20))
NGUONG_XUONG = (Fraction(1, 10), Fraction(1, 20), Fraction(3, 100))
MAU_TOI_THIEU = (30, 60, 100)


def tao_dong_ho(monkeypatch):
    """Ghim cả thời điểm tạo/hết hạn ngăn và lease SDK, không ghim perf_counter."""
    luc = [datetime(2026, 1, 15, 3, tzinfo=timezone.utc)]

    class NgayGioDemo(datetime):
        @classmethod
        def now(cls, tz=None):
            return luc[0].astimezone(tz) if tz else luc[0].replace(tzinfo=None)

        @classmethod
        def today(cls):
            return cls.now()

    for mo_dun in (sdk_engine, sdk_thu, chot_ky, ngan_ket_qua):
        monkeypatch.setattr(mo_dun, "datetime", NgayGioDemo)
    def ky(luc_bo_qua=None):
        return luc[0].strftime("%Y-%m")
    monkeypatch.setattr(chot_ky, "ky_hien_tai", ky)
    monkeypatch.setattr(ngan_ho_so, "ky_hien_tai", ky)
    monkeypatch.setattr(chon_mau, "sinh_hat_giong", lambda: demo.HAT_GIONG)
    return luc


@pytest.fixture
def dong_ho(monkeypatch):
    return tao_dong_ho(monkeypatch)


def chay_ca_tach_biet(ma):
    """Process riêng tránh xung đột các đồng hồ monkeypatch giữa ba ca nặng."""
    with pytest.MonkeyPatch.context() as mp:
        luc = tao_dong_ho(mp)

        def cam_mang(*args, **kwargs):
            raise AssertionError("Chỉ dùng Core giả (CoreGia) trong RAM; cấm mạng.")

        mp.setattr(socket.socket, "connect", cam_mang)
        mp.setattr(socket, "create_connection", cam_mang)
        if ma == "chinh":
            return mo_phong(luc)
        if ma == "lon":
            return mo_phong(luc, ca_lon=True)
        assert ma == "tan_suat"
        return kiem_tan_suat()


@pytest.fixture(scope="module")
def cac_ca_nang(request):
    """Chạy song song bằng thư viện chuẩn, không cần pytest-xdist.

    Mỗi ca có CoreGia nguyên bản và giữ ngăn riêng; không chia mô phỏng
    theo tháng, không sửa SDK hoặc thay ngăn bằng stub. Chỉ khởi chạy các
    ca được pytest chọn, nên -k vẫn chạy đúng phạm vi mong muốn.
    """
    ten_ca = {
        "test_mo_phong_12_thang_ba_loai_chot_ky_va_doi_bac": "chinh",
        "test_ca_lon_8_phan_tram_khoang_1000_mau_khong_ap_dat_bac_30": "lon",
        "test_tan_suat_10000_dong_bac_20_qua_cong_cong_khai": "tan_suat",
    }
    can = {ten_ca[item.originalname] for item in request.session.items
           if item.module is request.module and item.originalname in ten_ca}
    with ProcessPoolExecutor(max_workers=len(can)) as nhom:
        yield {ma: nhom.submit(chay_ca_tach_biet, ma) for ma in sorted(can)}


def tham_so():
    return {"khau": demo.KHAU, "danh_muc_loai_json": json.dumps([
        {"ma": ma, "ten": "Loại DEMO", "mo_ta": demo.CONG_TY}
        for ma in (demo.LOAI_SACH, demo.LOAI_LOI)], ensure_ascii=False)}


def giao(core, nang_luc, noi_dung):
    tep = core.them_tep("PL-9A-DEMO.json", demo.ma_hoa(noi_dung), "application/json")
    return core.giao_viec(nang_luc, {"loai": "tep", "tep": tep}, tham_so())


def truong(core, ma_viec):
    kq = core.xem(ma_viec)
    assert kq["trang_thai"] == "XONG", kq
    return kq["ket_qua"]["truong"]


def chay(core, nang_luc, noi_dung):
    ma_viec = giao(core, nang_luc, noi_dung)
    core.chay(app, khoang_gia_han=30)
    return truong(core, ma_viec)


def phan_luong(core, lo):
    ra = chay(core, "audit.phan_luong@1", lo)
    raw = core.doc_tep(ra["tep_json"]["tep_id"])
    return ra, json.loads(raw), raw


def trang_thai(core):
    """Chỉ test đọc bậc nội bộ; không thêm bậc vào đầu ra của engine."""
    return {d["loai"]: d for d in core.xem_ngan(app.ma, "ty_le")}


def ghi_bac_demo(core, bac=Fraction(1, 5)):
    """Ghi trạng thái DEMO qua viec.ngan, không chọc bộ nhớ riêng CoreGia."""
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = [{"ma": "demo.dung_ngan@1", "ten": "Dựng ngăn DEMO",
                          "nhan": ["van_ban"], "tra": "van_ban",
                          "gioi_han": {"thoi_han_giay": 300}}]
    phieu["chay_thu_demo"] = []
    thu = Engine(phieu)

    @thu.nang_luc("demo.dung_ngan@1")
    def dung(viec):
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("ty_le", {"khau": demo.KHAU, "loai": demo.LOAI_SACH}, {
                "bac": str(Decimal(bac.numerator) / bac.denominator), "che_do": "bac",
                **{cot: 0 for cot in ("mau_tu_doi_bac", "loi_tu_doi_bac", "mau_12t",
                    "loi_12t", "loi_sad_12t", "loi_ngoai_mau_12t", "mau_sach_toan_bo")},
                "diem": None, "nhan": "", "doi_bac_luc": None})
        return {"loai": "van_ban", "van_ban": demo.CONG_TY}

    kq = core.chay_thu(thu, "demo.dung_ngan@1", {"loai": "van_ban", "van_ban": demo.CONG_TY})
    assert kq["trang_thai"] == "XONG", kq


def duoc_chon_doc_lap(ma, p):
    raw = b"\x1f".join((demo.HAT_GIONG, demo.MA_MODULE.encode(), demo.KHAU.encode(), ma.encode()))
    return Fraction(int.from_bytes(sha256(raw).digest(), "big"), 2**256) < p


def du_cp(loi, n, nguong):
    """CP <= q tương đương P(X <= lỗi | n,q) <= 0,05, tính bằng Fraction."""
    if loi == 0:
        with localcontext() as ctx:
            ctx.prec = 60
            can_tren = 1 - Decimal("0.05") ** (Decimal(1) / n)
            q = Decimal(nguong.numerator) / nguong.denominator
            theo_cong_thuc = can_tren <= q
        theo_fraction = (1 - nguong)**n <= Fraction(1, 20)
        assert theo_cong_thuc == theo_fraction
        return theo_fraction
    a, b = nguong.numerator, nguong.denominator
    cdf = Fraction(sum(comb(n, k) * a**k * (b-a)**(n-k) for k in range(loi + 1)), b**n)
    return cdf <= Fraction(1, 20)


class DapAn:
    """Sổ test độc lập, reset mẫu chỉ khi bậc thực sự đổi theo §4.3."""
    def __init__(self):
        self.i = self.n = self.loi = self.tong = self.tong_loi = self.sad = 0
        self.doi = []

    @property
    def bac(self):
        return BAC[self.i]

    def kiem(self, dong, kq, thang):
        chon = "CHON_MAU" in dong["ly_do"]
        sai = kq["ket_qua"] == "sai"
        self.n += int(chon)
        self.loi += int(chon and sai)
        self.tong += int(chon)
        self.tong_loi += int(chon and sai)
        sad = sai and int(kq["so_tien_sai"]["so"]) >= 250_000_000
        self.sad += int(sad)
        cu = self.i
        if dong["loai"] != demo.CHUA_PHAN_LOAI:
            if sai and "CO_DO_CUNG" not in dong["ly_do"]:
                self.i = 0 if sad else max(0, self.i - 1)
            elif not sai and chon and self.i < 3 and self.n >= MAU_TOI_THIEU[self.i]:
                if du_cp(self.loi, self.n, NGUONG_XUONG[self.i]):
                    self.i += 1
        if self.i != cu:
            self.doi.append((thang, self.tong, self.n, BAC[cu], self.bac))
            self.n = self.loi = 0


def mo_phong(dong_ho, *, ca_lon=False):
    bat_dau = perf_counter()
    core = CoreGia()  # Cùng một CoreGia giữ toàn bộ ngăn trong 12 tháng.
    kich_ban = json.loads(demo.sinh_kich_ban(ca_lon=ca_lon))
    cac_loai = (demo.LOAI_LOI,) if ca_lon else demo.CAC_LOAI
    dap_an = {loai: DapAn() for loai in cac_loai}
    bao_cao = []
    for thang, lo in enumerate(kich_ban["lo"], 1):
        dong_ho[0] = datetime(2026, thang, 15, 3, tzinfo=timezone.utc)
        ra, tep, _ = phan_luong(core, lo)
        # Cổng đầu tiên tháng mới phải tự chốt, chưa ghi kết quả tháng này.
        cac_chot = core.xem_ngan(app.ma, "chot_ky")
        assert len(cac_chot) == (thang - 1) * len(cac_loai)
        assert {(d["ky"], d["loai"]) for d in cac_chot} == {
            (f"2026-{m:02d}", l) for m in range(1, thang) for l in cac_loai}
        if thang > 1:
            for d in trang_thai(core).values():
                a = dap_an[d["loai"]]
                assert (int(d["mau_12t"]), int(d["loi_12t"]),
                        int(d["mau_tu_doi_bac"]), int(d["loi_tu_doi_bac"])) == (
                            a.tong, a.tong_loi, a.n, a.loi)
        ds = []
        dem = {loai: [0, 0, 0] for loai in cac_loai}  # mẫu ngẫu nhiên, lỗi ngẫu nhiên, lỗi SAD
        for dong in tep["nghiep_vu"]:
            co_mong = (["DOI_TAC_MOI", "NHAP_TAY"] if ca_lon else
                       ["NHAP_TAY"] if dong["loai"] == demo.LOAI_SACH else [])
            assert dong["co"] == co_mong
            if dong["ma"].endswith("-SAD"):
                assert dong["luong"] == "do" and "CO_DO_CUNG" in dong["ly_do"]
            else:
                he_so = Fraction(3) if ca_lon else Fraction(3, 2) if co_mong else Fraction(1)
                p = min(Fraction(1), dap_an[dong["loai"]].bac * he_so)
                chon = duoc_chon_doc_lap(dong["ma"], p)
                assert (dong["luong"], dong["ly_do"]) == (
                    ("do", ["CHON_MAU"]) if chon else ("xanh", ["KHONG_CHON"]))
            if dong["luong"] == "do":
                ds.append({"ma_luot": ra["ma_luot"], **demo.ket_qua_nguoi_kiem(dong),
                           "giai_thich": "Công ty DEMO Ánh Dương: cần đối chiếu chứng từ gốc."})
        # Tất cả dòng trong lượt dùng bậc TRƯỚC ghi; sau đó người kiểm mới trả kết quả.
        theo_ma = {dong["ma"]: dong for dong in tep["nghiep_vu"]}
        for kq in ds:
            dong = theo_ma[kq["ma"]]
            chon, sai = "CHON_MAU" in dong["ly_do"], kq["ket_qua"] == "sai"
            dem[dong["loai"]][0] += int(chon)
            dem[dong["loai"]][1] += int(chon and sai)
            dem[dong["loai"]][2] += int(sai and dong["ma"].endswith("-SAD"))
            dap_an[dong["loai"]].kiem(dong, kq, thang)
        ghi = chay(core, "audit.ghi_ket_qua@1", {
            "phien_ban": 1, "ma_module": demo.MA_MODULE,
            "nguong": demo.NGUONG, "ket_qua": ds})
        assert (ghi["so_dong_nhan"], ghi["so_trung"], ghi["so_ngoai_mau"]) == (len(ds), 0, 0)
        tt = trang_thai(core)
        assert set(tt) == set(cac_loai)
        for loai, a in dap_an.items():
            d = tt[loai]
            assert Fraction(d["bac"]) == a.bac
            assert d["che_do"] == "bac"
            assert tuple(int(d[c]) for c in ("mau_tu_doi_bac", "loi_tu_doi_bac",
                         "mau_12t", "loi_12t", "loi_sad_12t")) == (a.n, a.loi, a.tong, a.tong_loi, a.sad)
            if a.sad:
                assert "rui_ro_cao" in d["nhan"].split(",")
        bao_cao.append((thang, {l: (*dem[l], dap_an[l].bac) for l in cac_loai}))
        print(f"DEMO {'lớn' if ca_lon else 'chính'} tháng {thang:02d}: "
              f"{perf_counter()-bat_dau:.3f} giây lũy kế", flush=True)
    assert len(core.xem_ngan(app.ma, "ket_qua_kiem")) == sum(a.tong + a.sad for a in dap_an.values())
    giay = perf_counter() - bat_dau
    print("\nPL-9A", "CA LỚN" if ca_lon else "CHÍNH", "— đã kiểm bằng Core giả (CoreGia)")
    print("Tháng | " + " | ".join(cac_loai) + " (mẫu/lỗi ngẫu nhiên + lỗi SAD; bậc cuối tháng)")
    for thang, ds in bao_cao:
        print(f"{thang:02d} | " + " | ".join(
            f"{ds[l][0]}/{ds[l][1]}+{ds[l][2]}; {float(ds[l][3]):.0%}" for l in cac_loai))
    for loai, a in dap_an.items():
        print(loai, "đổi bậc (tháng, tổng mẫu, mẫu từ lần đổi, bậc trước/sau):", a.doi)
    print(f"Thời gian mô phỏng: {giay:.3f} giây")
    return dap_an, bao_cao


def test_script_demo_cung_hat_giong_cung_bytes():
    for ca_lon in (False, True):
        raw = demo.sinh_kich_ban(ca_lon=ca_lon)
        assert raw == demo.sinh_kich_ban(ca_lon=ca_lon)
        kich_ban = json.loads(raw)
        assert kich_ban["cong_ty"] == demo.CONG_TY
        assert len(kich_ban["lo"]) == 12
        assert len({d["ma"] for lo in kich_ban["lo"] for d in lo["nghiep_vu"]}) == sum(
            len(lo["nghiep_vu"]) for lo in kich_ban["lo"])
        for lo in kich_ban["lo"]:
            for dong in lo["nghiep_vu"]:
                assert dong["dien_giai"] == demo.CONG_TY
                assert dong["so_tien"]["tien_te"] == "VND"
    # Đáp án 0 lỗi phải dùng đúng hai điều kiện: CP và số mẫu tối thiểu.
    for n, q in zip(MAU_TOI_THIEU, NGUONG_XUONG):
        assert du_cp(0, n, q)


def test_mo_phong_12_thang_ba_loai_chot_ky_va_doi_bac(cac_ca_nang):
    dap_an, bang = cac_ca_nang["chinh"].result(timeout=120)
    sach = dap_an[demo.LOAI_SACH]
    assert [d[2] for d in sach.doi] == list(MAU_TOI_THIEU)
    assert sach.bac == Fraction(1, 20)
    assert all(d[demo.LOAI_LOI][3] == Fraction(3, 10) for _, d in bang)
    assert all(d[demo.CHUA_PHAN_LOAI][3] == Fraction(3, 10) for _, d in bang)
    assert dap_an[demo.LOAI_LOI].sad == 3


def test_ca_lon_8_phan_tram_khoang_1000_mau_khong_ap_dat_bac_30(cac_ca_nang):
    """CA QUY MÔ LỚN: quy tắc CP hiện hành; lead đang hỏi Anh về xuống 20%."""
    dap_an, _ = cac_ca_nang["lon"].result(timeout=120)
    a = dap_an[demo.LOAI_LOI]
    assert 850 <= a.tong <= 1200
    assert Fraction(5, 100) <= Fraction(a.tong_loi, a.tong) <= Fraction(11, 100)
    assert a.sad == 0
    # Mỗi lần xuống đã đối chiếu CP và mẫu từ lần đổi; lỗi nhỏ lên một bậc.
    assert a.bac in BAC
    print(f"Ca lớn quan sát: {a.tong} mẫu, {a.tong_loi} lỗi, bậc cuối {float(a.bac):.0%}.")


def test_tai_hien_tep_json_tung_byte_hai_core_doc_lap(dong_ho):
    cac_core = [CoreGia(), CoreGia()]
    cac_raw, cac_nen = [], []
    for core in cac_core:
        ghi_bac_demo(core)
        he_thong = {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
        cac_nen.append({k: v for k, v in trang_thai(core)[demo.LOAI_SACH].items()
                        if k not in he_thong})
        _, _, raw = phan_luong(core, demo.sinh_lo(1, cac_loai=(demo.LOAI_SACH,)))
        cac_raw.append(raw)
    assert cac_nen[0] == cac_nen[1]
    assert cac_raw[0] == cac_raw[1]
    print("Tái hiện tep_json SHA-256:", sha256(cac_raw[0]).hexdigest())


def kiem_tan_suat():
    """200 lô x 50 mã riêng: mỗi CoreGia có cùng nền 20%, tổng 10.000 dòng.

    Đây là phép đo tần suất độc lập cùng p, không phải đo hiệu năng lô 10.000
    (PL-9B đo hiệu năng). Chia lô tránh chi phí quét tuyến tính của CoreGia;
    không thay hoặc bỏ qua bất kỳ đường đọc/ghi ngăn nào.
    """
    bat_dau = perf_counter()
    lo_day_du = demo.sinh_lo(1, so_moi_loai=10_000, cac_loai=(demo.LOAI_SACH,))
    n = tong = 0
    for dau in range(0, 10_000, 50):
        core = CoreGia()
        ghi_bac_demo(core)
        ra, tep, _ = phan_luong(core, {**lo_day_du,
            "nghiep_vu": lo_day_du["nghiep_vu"][dau:dau+50]})
        for dong in tep["nghiep_vu"]:
            assert dong["co"] == []
            assert (dong["luong"] == "do") == duoc_chon_doc_lap(dong["ma"], Fraction(1, 5))
        assert ra["so_nghiep_vu"] == 50 and ra["so_do_bat_buoc"] == 0
        n += ra["so_do_chon_mau"]
        tong += ra["so_nghiep_vu"]
        assert Fraction(trang_thai(core)[demo.LOAI_SACH]["bac"]) == Fraction(1, 5)
    assert tong == 10_000
    assert 1900 <= n <= 2100
    print(f"Tần suất: {n}/10.000 = {n/100:.2f}%; {perf_counter()-bat_dau:.3f} giây.")
    return n


def test_tan_suat_10000_dong_bac_20_qua_cong_cong_khai(cac_ca_nang):
    assert 1900 <= cac_ca_nang["tan_suat"].result(timeout=120) <= 2100


@pytest.mark.parametrize("gui_trung", [False, True], ids=["khac_ket_qua", "trung_ket_qua"])
def test_hai_ghi_dong_thoi_mot_xung_dot_khong_lech_khong_trung(dong_ho, monkeypatch, gui_trung):
    core = CoreGia()
    ghi_bac_demo(core, Fraction(3, 10))
    ra, tep, _ = phan_luong(core, demo.sinh_lo(1, cac_loai=(demo.LOAI_SACH,)))
    do = [d for d in tep["nghiep_vu"] if d["luong"] == "do"]
    assert len(do) >= 2
    payload = lambda d: {"phien_ban": 1, "ma_module": demo.MA_MODULE,
        "nguong": demo.NGUONG, "ket_qua": [{"ma_luot": ra["ma_luot"], **demo.ket_qua_nguoi_kiem(d)}]}
    cac_viec = [giao(core, "audit.ghi_ket_qua@1", payload(do[i])) for i in (0, 0 if gui_trung else 1)]
    core.gay_xung_dot_ngan("ty_le", so_lan=1)
    hen, xong, khoa = Barrier(2, timeout=10), Event(), Lock()
    thu_tu, so_thu_lai = [], []
    tao_goc, ghi_goc = ngan_ket_qua._tao_cap_moi, ngan_chung.ghi_lo_thu_lai

    def tao(*args):
        tao_goc(*args)
        with khoa:
            i = len(thu_tu)
            thu_tu.append(i)
        hen.wait()
        if i == 1:
            assert xong.wait(10)

    def ghi(viec, lap_lenh, **kw):
        n = ghi_goc(viec, lap_lenh, **kw)
        with khoa:
            so_thu_lai.append(n)
        return n

    monkeypatch.setattr(ngan_ket_qua, "_tao_cap_moi", tao)
    monkeypatch.setattr(ngan_chung, "ghi_lo_thu_lai", ghi)
    # Hai Engine SDK độc lập tránh chia sẻ _dt/_cfg của app; dùng nguyên handler thật.
    def chay_mot():
        phieu = deepcopy(app.phieu)
        phieu["nang_luc"] = [n for n in phieu["nang_luc"] if n["ma"] == "audit.ghi_ket_qua@1"]
        phieu["chay_thu_demo"] = []
        thu = Engine(phieu)
        from e_phan_luong.chay import ghi_ket_qua
        thu.nang_luc("audit.ghi_ket_qua@1")(ghi_ket_qua)
        try:
            core.chay(thu, khoang_gia_han=30)
        finally:
            xong.set()

    with ThreadPoolExecutor(max_workers=2) as nhom:
        cac_lan = [nhom.submit(chay_mot) for _ in range(2)]
        for lan in cac_lan:
            lan.result(timeout=20)
    dem = [truong(core, v) for v in cac_viec]
    n = 1 if gui_trung else 2
    # PL-9I: một xung đột giả; cùng khóa còn có một xung đột unique vì
    # việc thứ hai dùng bản đọc trước cũ ở lần thử đầu, rồi đọc lại khóa.
    assert sum(so_thu_lai) == 1 + int(gui_trung)
    assert sum(d["so_dong_nhan"] for d in dem) == n
    assert sum(d["so_trung"] for d in dem) == int(gui_trung)
    ds = core.xem_ngan(app.ma, "ket_qua_kiem")
    assert len(ds) == len({(d["ma_luot"], d["ma"], d["khau"]) for d in ds}) == n
    tt = trang_thai(core)[demo.LOAI_SACH]
    assert int(tt["mau_12t"]) == int(tt["mau_tu_doi_bac"]) == n
    assert int(tt["loi_12t"]) == int(tt["loi_tu_doi_bac"]) == 0
