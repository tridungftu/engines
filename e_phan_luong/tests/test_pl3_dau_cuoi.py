"""PL-2 + PL-3: đã kiểm bằng Core giả (CoreGia), Công ty DEMO Ánh Dương.

Một CoreGia giữ ngăn xuyên suốt chuỗi: 500 dòng -> ghi -> gửi trùng ->
nộp lại -> học 30 mẫu sạch -> phân luồng bằng bậc mới -> kiểm C4/C5.
Chỉ ghim nguồn sinh hạt giống để tái hiện; không giả chọn mẫu, ngăn hay
thuật toán đổi bậc, không gọi trực tiếp hàm nghiệp vụ trong gói.
"""
from collections import Counter
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong import chon_mau
from e_phan_luong.chay import app


DEMO = Path(__file__).resolve().parent / "demo"
KHAU = "ktt_duyet"
CONG_TY = "Công ty DEMO Ánh Dương"
LOAI_SACH = "sach_demo"
LOAI_SUA = "sua_loai_demo"


class ChuoiDemo:
    """Gửi tệp thật qua hai năng lực, giữ chứng cứ công khai để test độc lập."""

    def __init__(self):
        self.core = CoreGia()
        self.lo_goc = json.loads((DEMO / "lo-500-DEMO.json").read_bytes())
        danh_muc = json.loads((DEMO / "danh-muc-loai-DEMO.json").read_bytes())
        danh_muc.extend({"ma": ma, "ten": f"Loại DEMO {ma}", "mo_ta": CONG_TY}
                        for ma in (LOAI_SACH, LOAI_SUA))
        self.tham_so = {
            "khau": KHAU,
            "truong_phan_loai": "dien_giai",
            "danh_muc_loai_json": json.dumps(danh_muc, ensure_ascii=False),
            "bo_phan_loai_json": (DEMO / "bo-phan-loai-DEMO.json").read_text(encoding="utf-8"),
            # PL-4: tắt cờ DOI_TAC_MOI (khóa Admin) để giữ oracle tần suất của chuỗi PL-3;
            # hành vi mặc định của cờ đã kiểm ở test_pl2_phan_luong và test_pl4_*.
            "chinh_sach_json": json.dumps({"toi_thieu_ho_so_doi_tac_moi": 1000000}),
        }
        self.cac_dau_vao = []
        self.cac_truong_ra = []
        self.cac_tep_json = []

    def goi(self, nang_luc, noi_dung):
        raw = (noi_dung if isinstance(noi_dung, bytes)
               else json.dumps(noi_dung, ensure_ascii=False).encode("utf-8"))
        self.cac_dau_vao.append(json.loads(raw))
        tep = self.core.them_tep("du-lieu-DEMO.json", raw, "application/json")
        nl = next(n for n in app.phieu["nang_luc"] if n["ma"] == nang_luc)
        ma_tham_so = {t["ma"] for t in nl["tham_so"]}
        ts = {k: v for k, v in self.tham_so.items() if k in ma_tham_so}
        kq = self.core.chay_thu(app, nang_luc, {"loai": "tep", "tep": tep}, ts)
        assert kq["trang_thai"] == "XONG", kq.get("loi")
        assert kq["ket_qua"]["loai"] == "truong"
        truong = kq["ket_qua"]["truong"]
        self.cac_truong_ra.append((nang_luc, deepcopy(truong)))
        return truong

    def phan_luong(self, lo):
        truong = self.goi("audit.phan_luong@1", lo)
        tep = json.loads(self.core.doc_tep(truong["tep_json"]["tep_id"]))
        self.cac_tep_json.append(tep)
        return truong, tep

    def tep_ket_qua(self, tep, dong):
        return {"phien_ban": 1, "ma_module": tep["ma_module"],
                "nguong": deepcopy(self.lo_goc["nguong"]), "ket_qua": dong}

    def dong_ket_qua(self, tep, dong, **thay):
        return {"ma_luot": tep["ma_luot"], "ma": dong["ma"], "khau": tep["khau"],
                "ket_qua": "dat", "giai_thich": CONG_TY + ": cần đối chiếu chứng từ gốc.", **thay}

    def ghi(self, tep):
        return self.goi("audit.ghi_ket_qua@1", tep)

    def ty_le(self):
        return deepcopy(self.core.xem_ngan(app.ma, "ty_le"))

    def cap(self, loai):
        ds = [d for d in self.ty_le() if (d["khau"], d["loai"]) == (KHAU, loai)]
        assert len(ds) == 1, ds
        return ds[0]

    def lo_sach(self, lan, so_dong):
        # Tiền trong vùng SAD..TE, không số tròn, không cờ ngày/nhập tay;
        # mỗi đối tác một dòng để không tạo NGHI_CHIA_NHO.
        return {"phien_ban": 1, "ma_module": self.lo_goc["ma_module"], "ky": "2026-11",
                "nguong": deepcopy(self.lo_goc["nguong"]), "nghiep_vu": [
                    {"ma": f"PC-DEMO-SACH-{lan:03}-{i:04}", "loai": LOAI_SACH,
                     "ngay": "2026-11-16", "so_tien": {"so": "371234567.123456", "tien_te": "VND"},
                     "doi_tac": f"DEMO-NCC-SACH-{lan:03}-{i:04}",
                     "dien_giai": f"{CONG_TY} thanh toán sạch DEMO {lan}/{i}",
                     "tai_khoan_no": "331009876543210", "tai_khoan_co": "112100987654321",
                     "nhap_tay": False, "co_do_cung": False, "thuoc_tinh": {}}
                    for i in range(so_dong)]}


@pytest.fixture(scope="module")
def chuoi_demo():
    chuoi = ChuoiDemo()
    dem_hat = 0

    def hat_giong_demo():
        nonlocal dem_hat
        dem_hat += 1
        return (bytes(range(32)) if dem_hat == 1
                else sha256(f"PL-3 đầu-cuối DEMO {dem_hat}".encode("utf-8")).digest())

    with pytest.MonkeyPatch.context() as ghim:
        ghim.setattr(chon_mau, "sinh_hat_giong", hat_giong_demo)
        chuoi.truong1, chuoi.tep1 = chuoi.phan_luong((DEMO / "lo-500-DEMO.json").read_bytes())
        ds = chuoi.tep1["nghiep_vu"]
        chon = lambda loai: next(d for d in ds if d["loai"] == loai and d["ly_do"] == ["CHON_MAU"])
        chuoi.dong_nho = chon("thanh_toan_ncc")
        chuoi.dong_sad = chon("chi_phi_khac")
        chuoi.dong_te = chon("luong")
        chuoi.dong_sua = chon("tam_ung")
        chuoi.dong_xanh = next(d for d in ds if d["loai"] == "thu_tien" and d["luong"] == "xanh")
        chuoi.cac_loi = {d["ma"] for d in (chuoi.dong_nho, chuoi.dong_sad, chuoi.dong_te)}
        dong_dat = [chuoi.dong_ket_qua(chuoi.tep1, d,
                    **({"loai_dung": LOAI_SUA} if d == chuoi.dong_sua else {}))
                    for d in ds if d["luong"] == "do" and d["ma"] not in chuoi.cac_loi]
        ng = chuoi.lo_goc["nguong"]
        chuoi.nguong_loi = [
            (chuoi.dong_nho, str(Decimal(ng["sad"]["so"]) - 1)),
            (chuoi.dong_sad, ng["sad"]["so"]),
            (chuoi.dong_te, ng["te"]["so"]),
            (chuoi.dong_xanh, "1234567.654321"),
        ]
        # Lỗi ở cuối: hai cặp đủ 30 mẫu sạch hạ 20%, rồi SAD về 30% / TE lên 100%.
        dong_sai = [chuoi.dong_ket_qua(chuoi.tep1, d, ket_qua="sai",
                    so_tien_sai={"so": so, "tien_te": ng["sad"]["tien_te"]})
                    for d, so in chuoi.nguong_loi]
        chuoi.tep_ghi = chuoi.tep_ket_qua(chuoi.tep1, dong_dat + dong_sai)
        chuoi.dem_ghi = chuoi.ghi(chuoi.tep_ghi)
        chuoi.ty_le_sau_ghi = chuoi.ty_le()
        chuoi.ket_qua_sau_ghi = deepcopy(chuoi.core.xem_ngan(app.ma, "ket_qua_kiem"))
        chuoi.dem_trung = chuoi.ghi(chuoi.tep_ghi)  # Đúng nội dung, không sửa tệp gửi lại.
        chuoi.ty_le_sau_trung = chuoi.ty_le()
        chuoi.ket_qua_sau_trung = deepcopy(chuoi.core.xem_ngan(app.ma, "ket_qua_kiem"))

        chuoi.truong2, chuoi.tep2 = chuoi.phan_luong((DEMO / "lo-500-DEMO.json").read_bytes())
        # Mọi dòng Đỏ lượt 1 đã được kiểm. Tạo tình huống Q5 ở lượt 2:
        # chỉ kiểm một dòng, giữ dòng Đỏ khác chưa có kết quả lượt gần nhất.
        hai_do = [d for d in chuoi.tep2["nghiep_vu"]
                  if d["loai"] == "luong" and d["ly_do"] == ["CHON_MAU"]]
        assert len(hai_do) >= 2, "DEMO phải có hai dòng Đỏ để kiểm Q5."
        chuoi.da_kiem, chuoi.chua_kiem = hai_do[:2]
        chuoi.ghi(chuoi.tep_ket_qua(chuoi.tep2,
                  [chuoi.dong_ket_qua(chuoi.tep2, chuoi.da_kiem)]))
        chuoi.truong3, chuoi.tep3 = chuoi.phan_luong((DEMO / "lo-500-DEMO.json").read_bytes())

        chuoi.cac_mau_sach = []
        for lan in range(1, 121):
            if len(chuoi.cac_mau_sach) == 30:
                break
            _, tep = chuoi.phan_luong(chuoi.lo_sach(lan, 16))
            ds_chon = [d for d in tep["nghiep_vu"] if d["ly_do"] == ["CHON_MAU"]]
            if not ds_chon:
                continue
            dong = chuoi.dong_ket_qua(tep, ds_chon[0])
            dem = chuoi.ghi(chuoi.tep_ket_qua(tep, [dong]))
            chuoi.cac_mau_sach.append((tep["ma_luot"], ds_chon[0], dem, chuoi.cap(LOAI_SACH)))
        assert len(chuoi.cac_mau_sach) == 30, "DEMO chưa thu được đủ 30 mẫu ngẫu nhiên."
        chuoi.ty_le_truoc_luot20 = chuoi.ty_le()
        chuoi.lo20 = chuoi.lo_sach(999, 2000)
        chuoi.truong20, chuoi.tep20 = chuoi.phan_luong(chuoi.lo20)
        chuoi.ty_le_sau_luot20 = chuoi.ty_le()
    return chuoi


def test_01_lo_500_demo_so_dem_truong_ra_khop_tep_json(chuoi_demo):
    c = chuoi_demo
    truong, tep = c.truong1, c.tep1
    ds = tep["nghiep_vu"]
    assert [d["ma"] for d in ds] == [d["ma"] for d in c.lo_goc["nghiep_vu"]]
    assert truong["ma_luot"] == tep["ma_luot"]
    assert tep["khau"] == KHAU and tep["ma_module"] == c.lo_goc["ma_module"]
    assert truong["so_nghiep_vu"] == len(ds) == 500
    assert truong["so_do"] == sum(d["luong"] == "do" for d in ds)
    assert truong["so_xanh"] == sum(d["luong"] == "xanh" for d in ds)
    assert truong["so_do_chon_mau"] == sum("CHON_MAU" in d["ly_do"] for d in ds)
    assert truong["so_do_bat_buoc"] == sum(d["luong"] == "do" and "CHON_MAU" not in d["ly_do"] for d in ds)
    assert truong["so_chua_phan_loai"] == sum(d["loai"] == "chua_phan_loai" for d in ds)
    assert truong["so_do"] == truong["so_do_bat_buoc"] + truong["so_do_chon_mau"]
    assert truong["so_do"] + truong["so_xanh"] == 500
    assert truong["luong"] == "do" and truong["can_nguoi_kiem"] is True
    assert truong["tong_tien_do"] is None  # Có dòng chưa rõ tiền tệ/chưa quy đổi.
    for cot in ("bam_hat_giong", "bam_dau_vao", "phien_ban_engine"):
        assert truong[cot] == tep[cot]


def test_02_ghi_ket_qua_q1_q2_muc_sai_ngoai_mau_va_doi_bac(chuoi_demo):
    c = chuoi_demo
    assert "nguong_json" not in c.tham_so  # Thực sự lấy ngưỡng trong tệp (Q1).
    ds = c.tep_ghi["ket_qua"]
    assert {d["ma"] for d in ds} == {d["ma"] for d in c.tep1["nghiep_vu"] if d["luong"] == "do"} | {c.dong_xanh["ma"]}
    assert c.dem_ghi == {"so_dong_nhan": len(ds), "so_trung": 0, "so_ngoai_mau": 1,
                         "so_sua_loai": 1, "so_cap_doi_bac": 2,
                         "so_ai_sai": 4, "tep_bai_hoc": c.dem_ghi["tep_bai_hoc"],
                         "phien_ban_engine": c.truong1["phien_ban_engine"]}
    bh = json.loads(c.core.doc_tep(c.dem_ghi["tep_bai_hoc"]["tep_id"]))["dong"]
    assert {d["ma"] for d in bh} == {d["ma"] for d in (c.dong_nho, c.dong_sad, c.dong_te, c.dong_xanh)}
    assert all(d["ai_bo_sot"] and not d["da_ghi_truoc"] for d in bh)
    # Oracle độc lập: 34 và 39 mẫu sạch rồi lỗi, chỉ hai cặp này đổi bậc.
    so_chon = Counter(d["loai"] for d in c.tep1["nghiep_vu"] if d["ly_do"] == ["CHON_MAU"])
    assert 30 <= so_chon["luong"] - 1 < 90
    assert 30 <= so_chon["chi_phi_khac"] - 1 < 90
    da_ghi = {d["ma"]: d for d in c.ket_qua_sau_ghi}
    assert len(da_ghi) == len(ds)
    for dong, muc in ((c.dong_nho, "nho"), (c.dong_sad, "sad"), (c.dong_te, "te")):
        assert da_ghi[dong["ma"]]["muc_sai"] == muc
        assert da_ghi[dong["ma"]]["nguon_mau"] == "chon_mau"
    ngoai = da_ghi[c.dong_xanh["ma"]]
    assert (ngoai["ket_qua"], ngoai["nguon_mau"], ngoai["loai"]) == ("sai", "ngoai_mau", "thu_tien")
    sua = da_ghi[c.dong_sua["ma"]]
    assert sua["loai"] == LOAI_SUA != c.dong_sua["loai"]
    assert sua["nguon_loai_sai"] == c.dong_sua["nguon_loai"]
    for dong in c.tep1["nghiep_vu"]:
        if dong["luong"] == "do" and "CHON_MAU" not in dong["ly_do"]:
            assert da_ghi[dong["ma"]]["nguon_mau"] == "bat_buoc"
    cap = {d["loai"]: d for d in c.ty_le_sau_ghi}
    assert int(cap["thu_tien"]["loi_ngoai_mau_12t"]) == 1
    assert "loi_ngoai_mau" in cap["thu_tien"]["nhan"].split(",")
    assert int(cap[LOAI_SUA]["mau_12t"]) == 1
    assert int(cap["tam_ung"]["mau_12t"]) == so_chon["tam_ung"] - 1
    assert int(cap["thanh_toan_ncc"]["mau_12t"]) == so_chon["thanh_toan_ncc"]


def test_03_gui_lai_dung_tep_khong_cong_lai_thong_ke(chuoi_demo):
    c = chuoi_demo
    assert c.dem_trung == {"so_dong_nhan": 0, "so_trung": len(c.tep_ghi["ket_qua"]),
                           "so_ngoai_mau": 0, "so_sua_loai": 0, "so_cap_doi_bac": 0,
                           "so_ai_sai": 4, "tep_bai_hoc": c.dem_trung["tep_bai_hoc"],
                           "phien_ban_engine": c.truong1["phien_ban_engine"]}
    bh = json.loads(c.core.doc_tep(c.dem_trung["tep_bai_hoc"]["tep_id"]))["dong"]
    assert len(bh) == 4 and all(d["da_ghi_truoc"] for d in bh)
    # So cả row_version và dấu thời gian: gửi trùng không có lần sửa ngăn nào.
    assert c.ty_le_sau_trung == c.ty_le_sau_ghi
    assert c.ket_qua_sau_trung == c.ket_qua_sau_ghi


def test_04_nop_lai_q5_theo_ket_qua_luot_gan_nhat(chuoi_demo):
    c = chuoi_demo
    assert len({c.tep1["ma_luot"], c.tep2["ma_luot"], c.tep3["ma_luot"]}) == 3
    assert c.tep1["bam_hat_giong"] != c.tep2["bam_hat_giong"] != c.tep3["bam_hat_giong"]
    assert all("NOP_LAI" not in d["ly_do"] for d in c.tep2["nghiep_vu"])
    theo_ma = {d["ma"]: d for d in c.tep3["nghiep_vu"]}
    assert "NOP_LAI" not in theo_ma[c.da_kiem["ma"]]["ly_do"]
    chua = theo_ma[c.chua_kiem["ma"]]
    assert chua["luong"] == "do" and "NOP_LAI" in chua["ly_do"]
    da_kiem = {(d["ma_luot"], d["ma"]) for d in c.core.xem_ngan(app.ma, "ket_qua_kiem")}
    for dong in c.tep2["nghiep_vu"]:
        if dong["luong"] == "do" and (c.tep2["ma_luot"], dong["ma"]) not in da_kiem:
            assert "NOP_LAI" in theo_ma[dong["ma"]]["ly_do"]


def test_05_loi_te_kiem_100_phan_tram_sad_ve_30_rui_ro_cao(chuoi_demo):
    c = chuoi_demo
    cap = {d["loai"]: d for d in c.ty_le_sau_ghi}
    assert cap["luong"]["che_do"] == "toan_bo"
    assert cap["chi_phi_khac"]["che_do"] == "bac"
    assert Decimal(str(cap["chi_phi_khac"]["bac"])) == Decimal("0.30")
    assert "rui_ro_cao" in cap["chi_phi_khac"]["nhan"].split(",")
    assert "rui_ro_cao" in cap["luong"]["nhan"].split(",")
    theo_ma = {d["ma"]: d for d in c.tep2["nghiep_vu"]}
    dong_goc = {d["ma"]: d for d in c.lo_goc["nghiep_vu"]}
    ng = c.lo_goc["nguong"]
    vung = []
    for dong in c.tep1["nghiep_vu"]:
        tien = dong_goc[dong["ma"]].get("so_tien_quy_doi") or dong_goc[dong["ma"]]["so_tien"]
        if (dong["loai"] == "luong" and dong["ly_do"] in (["CHON_MAU"], ["KHONG_CHON"])
                and tien["tien_te"] == ng["sad"]["tien_te"]
                and Decimal(ng["sad"]["so"]) <= abs(Decimal(tien["so"])) < Decimal(ng["te"]["so"])):
            vung.append(theo_ma[dong["ma"]])
    assert len(vung) >= 30
    # Kiểm 100%: không dòng nào Xanh. PL-4 + Anh chốt Q8: nộp lại cùng lô cộng trùng
    # tổng chia nhỏ qua hồ sơ nên một số dòng thành Đỏ bắt buộc NGHI_CHIA_NHO.
    assert all(d["luong"] == "do" for d in vung)
    assert all(d["ly_do"] == ["CHON_MAU"] or "NGHI_CHIA_NHO" in d["ly_do"] for d in vung)
    assert any(d["ly_do"] == ["CHON_MAU"] for d in vung)


def test_06_mau_sach_thu_30_xuong_20_luot_ke_tiep_doc_bac_moi(chuoi_demo):
    c = chuoi_demo
    assert len({ma_luot for ma_luot, _, _, _ in c.cac_mau_sach}) == 30
    for so, (_, dong, dem, cap) in enumerate(c.cac_mau_sach, 1):
        assert dong["ly_do"] == ["CHON_MAU"]
        assert dem["so_dong_nhan"] == 1 and dem["so_trung"] == 0
        assert dem["so_ngoai_mau"] == 0 and dem["so_sua_loai"] == 0
        assert dem["so_cap_doi_bac"] == (1 if so == 30 else 0)
        assert cap["che_do"] == "bac"
        assert Decimal(str(cap["bac"])) == (Decimal("0.30") if so < 30 else Decimal("0.20"))
        assert int(cap["mau_12t"]) == so and int(cap["loi_12t"]) == 0
        assert int(cap["mau_tu_doi_bac"]) == (so if so < 30 else 0)
    assert c.ty_le_truoc_luot20 == c.ty_le_sau_luot20
    ds = c.tep20["nghiep_vu"]
    assert len(ds) == 2000
    assert all(d["loai"] == LOAI_SACH and not d["co"] for d in ds)
    assert all(d["ly_do"] in (["CHON_MAU"], ["KHONG_CHON"]) for d in ds)
    so_chon = sum(d["ly_do"] == ["CHON_MAU"] for d in ds)
    assert Decimal("0.17") <= Decimal(so_chon) / len(ds) <= Decimal("0.23")
    # Khẳng định bậc bằng xem_ngan; số đếm đầu ra không chứng minh bậc 20%.
    assert Decimal(str(c.cap(LOAI_SACH)["bac"])) == Decimal("0.20")


def _cac_gia_tri(gia_tri):
    if isinstance(gia_tri, dict):
        for con in gia_tri.values():
            yield from _cac_gia_tri(con)
    elif isinstance(gia_tri, list):
        for con in gia_tri:
            yield from _cac_gia_tri(con)
    elif gia_tri is not None:
        yield str(gia_tri)


def test_07_c4_moi_bang_sau_toan_bo_chuoi_khong_lo_chi_tiet_demo(chuoi_demo):
    c = chuoi_demo
    cam_cot = {"so_tien", "so_tien_sai", "so_tien_quy_doi", "ngay", "doi_tac", "dien_giai",
               "tai_khoan_no", "tai_khoan_co", "noi_dung", "thuoc_tinh"}
    nhan_biet = {CONG_TY}
    for lo in c.cac_dau_vao:
        for dong in lo.get("nghiep_vu", []):
            nhan_biet.update(str(dong[k]) for k in ("ngay", "doi_tac", "dien_giai", "tai_khoan_no", "tai_khoan_co") if dong.get(k))
            for k in ("so_tien", "so_tien_quy_doi"):
                if dong.get(k):
                    nhan_biet.add(str(dong[k]["so"]))
        for dong in lo.get("ket_qua", []):
            if dong.get("so_tien_sai"):
                nhan_biet.add(str(dong["so_tien_sai"]["so"]))
    nhan_biet_dai = {chu for chu in nhan_biet if len(chu) >= 8}
    he_thong = {"id", "phap_nhan_id", "row_version", "tao_luc", "sua_luc", "het_han_luc", "viec_id"}
    cac_bang = {b["bang"] for b in app.phieu["ngan_du_lieu"]}
    assert cac_bang == {"luot", "dong_luot", "ket_qua_kiem", "ty_le", "ho_so_hanh_vi", "chot_ky"}
    for bang in app.phieu["ngan_du_lieu"]:
        cho_phep = he_thong | {t["ma"] for t in bang["truong"]}
        gia_tri_bang = []
        for dong in c.core.xem_ngan(app.ma, bang["bang"]):
            assert set(dong) <= cho_phep
            assert not cam_cot & set(dong)
            # Ngày giao dịch DEMO có thể trùng ngày chạy test. Timestamp do
            # Core tạo không phải ngày giao dịch bị lưu; vẫn kiểm tên mọi cột.
            noi_dung = {k: v for k, v in dong.items()
                        if k not in {"tao_luc", "sua_luc", "het_han_luc", "doi_bac_luc"}}
            if bang["bang"] == "ho_so_hanh_vi":
                # Ngoại lệ Anh duyệt ở phiếu §4.1: tổng tiền theo (băm đối tác, ngày) 7 ngày
                # gần nhất để chống chia nhỏ qua lô; không có mã giao dịch hay đối tác thô.
                tong = json.loads(noi_dung.pop("tong_7_ngay"))
                for bam, theo_ngay in tong.items():
                    assert len(bam) == 32 and int(bam, 16) >= 0
                    ngay = sorted(theo_ngay)
                    assert len(ngay) <= 7
                    assert all(len(n) == 10 and n[4] == n[7] == "-" for n in ngay)
                    assert all(Decimal(v) >= 0 for v in theo_ngay.values())
            for gia_tri in _cac_gia_tri(noi_dung):
                assert gia_tri not in nhan_biet, (bang["bang"], gia_tri)
                gia_tri_bang.append(gia_tri)
        # Dò cả chuỗi con, kể cả chi tiết bị nhét vào một cột text/JSON.
        # str.find trên toàn bảng tránh regex hàng nghìn nhánh ở từng ô.
        van_ban = "\0".join(gia_tri_bang)
        for dau in nhan_biet_dai:
            assert dau not in van_ban, (bang["bang"], dau)
    # Các bảng có dữ liệu để phép dò không chỉ đúng với ngăn rỗng.
    for bang in ("luot", "dong_luot", "ket_qua_kiem", "ty_le"):
        assert c.core.xem_ngan(app.ma, bang)


def test_08_c5_moi_truong_ra_tep_json_khong_lo_ty_le_bac_hat_giong(chuoi_demo):
    c = chuoi_demo
    cam = {"ty_le", "xac_suat", "bac", "hat_giong", "p", "p_bac", "p_co_so", "he_so", "san", "diem", "che_do"}

    def kiem(nut):
        if isinstance(nut, dict):
            for khoa, con in nut.items():
                assert khoa not in cam
                assert not any(tu in khoa for tu in ("ty_le", "xac_suat", "hat_giong_tho"))
                kiem(con)
        elif isinstance(nut, list):
            for con in nut:
                kiem(con)

    for nang_luc, truong in c.cac_truong_ra:
        cong_bo = next(n for n in app.phieu["nang_luc"] if n["ma"] == nang_luc)
        assert set(truong) == {t["ma"] for t in cong_bo["truong_ra"]}
        kiem(truong)
        if "canh_bao" in truong:
            assert len(truong["canh_bao"]) <= 500
            assert not any(tu in truong["canh_bao"].lower() for tu in ("%", "tỷ lệ", "xác suất", "bậc"))
    for tep in c.cac_tep_json:
        kiem(tep)
        assert set(tep) == {"phien_ban", "ma_luot", "khau", "ma_module", "nghiep_vu",
                            "bam_hat_giong", "bam_dau_vao", "phien_ban_engine"}
        assert all(set(d) == {"ma", "luong", "ly_do", "co", "loai", "nguon_loai"} for d in tep["nghiep_vu"])
    ngoai = json.dumps([c.cac_truong_ra, c.cac_tep_json], ensure_ascii=False)
    for luot in c.core.xem_ngan(app.ma, "luot"):
        assert len(luot["hat_giong"]) == 64
        assert luot["hat_giong"] not in ngoai
