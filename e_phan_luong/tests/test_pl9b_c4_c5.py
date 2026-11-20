"""PL-9B: C4/C5 theo quyết định lead, đã kiểm bằng Core giả (CoreGia).

Ngoại lệ C4 chỉ ở tổng 7 ngày theo phiếu §4.1; ngoại lệ C5 chỉ là hai
tên trường của hợp đồng, tuyệt đối không miễn kiểm giá trị bên trong.
"""
from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
import json
from pathlib import Path
import re
import unicodedata

import openpyxl
import pytest
from kho_tri_thuc_sdk.thu import CoreGia

from demo.sinh_bang_demo import khuon_demo, lo_json_demo, sinh_csv, sinh_xlsx
from e_phan_luong import chon_mau, chot_ky
from e_phan_luong.chay import app

DEMO = Path(__file__).resolve().parent / "demo"
KHAU = "ktt_duyet"
NL = tuple(n["ma"] for n in app.phieu["nang_luc"])
COT_TY_LE = set("khau loai bac che_do mau_tu_doi_bac loi_tu_doi_bac mau_sach_toan_bo "
                 "mau_12t loi_12t loi_sad_12t loi_ngoai_mau_12t diem nhan doi_bac_luc".split())
COT = {
    "luot": set("ma_luot ma_module khau hat_giong bam_dau_vao".split()),
    "dong_luot": set("ma_luot ma ma_module khau ly_do loai nguon_loai".split()),
    "ket_qua_kiem": set("ma_luot ma khau ma_module loai ket_qua muc_sai nguon_mau nguon_loai_sai".split()),
    "ty_le": COT_TY_LE,
    "ho_so_hanh_vi": set("khau loai so_nghiep_vu bieu_do bam_doi_tac tong_7_ngay tien_te ky_lam_moi".split()),  # tien_te: PL-9D
    "chot_ky": COT_TY_LE | {"ky"},
}
HE_THONG = set("id phap_nhan_id row_version tao_luc sua_luc het_han_luc viec_id".split())
CAM_C5 = ("ty le", "xac suat", "bac", "hat giong", "he so")
# Phiếu §5.5: băm SHA-256 không phải hạt giống; số cặp không phải giá trị bậc.
# Chỉ cho phép KHÓA đúng tên này, không cho phép chuỗi giá trị hay tên mở rộng.
KHOA_CHO_PHEP_C5 = {
    "bam_hat_giong": "SHA-256 của hạt giống, không phải hạt giống.",
    "so_cap_doi_bac": "Số cặp đổi bậc, không tiết lộ bậc hay tỷ lệ.",
}


def doc(ten):
    return json.loads((DEMO / ten).read_bytes())


def ma_hoa(nut):
    return json.dumps(nut, ensure_ascii=False).encode("utf-8")


def bo_dau(chu):
    chu = "".join(c for c in unicodedata.normalize("NFD", str(chu))
                  if unicodedata.category(c) != "Mn").casefold().replace("đ", "d")
    return " ".join(re.sub(r"[_\W]+", " ", chu).split())


def cac_o(nut, duong=""):
    """Quét cả khóa và giá trị, kể cả JSON nằm trong ô text của ngăn/AI."""
    if isinstance(nut, dict):
        for k, v in nut.items():
            yield duong + "/<khoa:" + k + ">", k
            yield from cac_o(v, duong + "/" + k)
    elif isinstance(nut, (list, tuple)):
        for i, v in enumerate(nut):
            yield from cac_o(v, f"{duong}/{i}")
    else:
        yield duong, nut
        if isinstance(nut, str) and nut.lstrip().startswith(("{", "[")):
            try:
                ben_trong = json.loads(nut)
            except (ValueError, RecursionError):
                return
            yield from cac_o(ben_trong, duong + "/json")


def cam_c5(nut, hat_giong, phan_tram):
    loi = []
    for duong, o in cac_o(nut):
        chu = bo_dau(o)
        for cam in CAM_C5:
            khoa_duoc_phep = (isinstance(o, str) and o in KHOA_CHO_PHEP_C5
                             and duong.endswith("/<khoa:" + o + ">"))
            if not khoa_duoc_phep and re.search(r"(?:^| )" + re.escape(cam) + r"(?: |$)", chu):
                loi.append(f"{duong}: có chữ/khóa {cam}")
        if isinstance(o, str):
            if any(h in o.casefold() for h in hat_giong):
                loi.append(f"{duong}: lộ hạt giống hex")
            for p in phan_tram:
                if re.search(r"(?<![\d.])" + re.escape(p) + r"(?:[.,]0+)?\s*%", o):
                    loi.append(f"{duong}: lộ phần trăm {p}%")
    return loi


def kiem_tong_7_ngay(chuoi):
    """Ngoại lệ Anh duyệt §4.1: chỉ băm → ngày → tổng tiền không âm."""
    def khong_trung(ds):
        assert len(dict(ds)) == len(ds), "JSON tổng 7 ngày có khóa trùng."
        return dict(ds)

    assert isinstance(chuoi, str)
    tong = json.loads(chuoi, object_pairs_hook=khong_trung)
    assert isinstance(tong, dict)
    for bam, ngay_tien in tong.items():
        assert re.fullmatch(r"[0-9a-fA-F]{32}", bam)
        assert isinstance(ngay_tien, dict) and len(ngay_tien) <= 7
        for ngay, tien in ngay_tien.items():
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", ngay)
            assert date.fromisoformat(ngay).isoformat() == ngay
            assert isinstance(tien, str) and re.fullmatch(r"\d+(?:\.\d+)?", tien)
            assert Decimal(tien).is_finite() and Decimal(tien) >= 0


class VongDemo:
    def __init__(self):
        self.core = CoreGia()
        self.ra = []
        self.dau_vao = []
        self.ts = {"khau": KHAU, "ma_module": "demo_thanh_toan",
                   "nguong_json": json.dumps(doc("nguong-DEMO.json")),
                   "danh_muc_loai_json": json.dumps(doc("danh-muc-loai-DEMO.json")),
                   "bo_phan_loai_json": json.dumps(doc("bo-phan-loai-DEMO.json")),
                   "truong_phan_loai": "dien_giai", "khuon_cot_json": json.dumps(khuon_demo()),
                   "ma_prompt": "demo_thanh_toan.phan_loai_DEMO", "phien_ban_prompt": "DEMO-1",
                   "prompt": "DEMO: chỉ chọn loại trong danh mục."}

    def goi(self, nl, pb, **doi):
        n = next(n for n in app.phieu["nang_luc"] if n["ma"] == nl)
        cot = {t["ma"] for t in n["tham_so"]}
        ts = {k: v for k, v in {**self.ts, **doi}.items() if k in cot}
        kq = self.core.chay_thu(app, nl, pb, ts)
        assert kq["trang_thai"] == "XONG", kq
        self.ra.append((nl, deepcopy(kq["ket_qua"])))
        return kq["ket_qua"]

    def tep(self, nl, nut, *, ten="lo-DEMO.json", mime="application/json", **doi):
        raw = nut if isinstance(nut, bytes) else ma_hoa(nut)
        if not isinstance(nut, bytes):
            self.dau_vao.append(deepcopy(nut))
        ref = self.core.them_tep(ten, raw, mime)
        return self.goi(nl, {"loai": "tep", "tep": ref}, **doi)


@pytest.fixture(scope="module")
def vong():
    v = VongDemo()
    with pytest.MonkeyPatch.context() as ghim:
        ghim.setattr(chon_mau, "sinh_hat_giong", lambda: bytes(range(32)))
        ghim.setattr(chot_ky, "ky_hien_tai", lambda *a: "2026-11")
        # TẤT CẢ ví dụ dùng cùng một CoreGia với vòng bổ sung bên dưới.
        ds = v.core.chay_thu_demo(app)
        assert len(ds) == len(app.phieu["chay_thu_demo"])
        for vd, kq in zip(app.phieu["chay_thu_demo"], ds):
            assert kq["trang_thai"] == "XONG", kq
            v.ra.append((vd["nang_luc"], deepcopy(kq["ket_qua"])))
            pb = vd["dau_vao"]
            if pb.get("tep_demo", "").endswith(".json"):
                v.dau_vao.append(json.loads((app.thu_muc_goi / pb["tep_demo"]).read_bytes()))
            elif pb.get("loai") == "truong":
                v.dau_vao.append(deepcopy(pb))
        v.dau_vao.append(json.loads(lo_json_demo()))  # Cùng ô nguồn Excel DEMO.

        lo = {"phien_ban": 1, "ma_module": "demo_thanh_toan", "ky": "2026-11",
              "nguong": doc("nguong-DEMO.json"), "nghiep_vu": [
                  {"ma": f"PC-DEMO-C4-{i:03}", "ngay": "2026-11-16",
                   "so_tien": {"so": "371234567.123456", "tien_te": "VND"},
                   "doi_tac": f"DEMO-NCC-C4-{i:03}", "dien_giai": "Thanh toán DEMO nội dung riêng C4",
                   "thuoc_tinh": {"ma_so_thue": "DEMO-MST-C4-987654321",
                                   "ten_doi_tac": "Công ty DEMO Nhà cung cấp C4"},
                   "co_do_cung": i == 0} for i in range(12)]}
        ra = v.tep("audit.phan_luong@1", lo)
        t = ra["truong"]
        chi_tiet = json.loads(v.core.doc_tep(t["tep_json"]["tep_id"]))
        do = next(d for d in chi_tiet["nghiep_vu"] if d["luong"] == "do")
        xanh = next(d for d in chi_tiet["nghiep_vu"] if d["luong"] == "xanh")
        ghi = {"phien_ban": 1, "ma_module": lo["ma_module"], "nguong": lo["nguong"], "ket_qua": [
            {"ma_luot": t["ma_luot"], "ma": do["ma"], "khau": KHAU, "ket_qua": "dat", "loai_dung": "tam_ung"},
            {"ma_luot": t["ma_luot"], "ma": xanh["ma"], "khau": KHAU, "ket_qua": "sai",
             "so_tien_sai": {"so": "1234567.654321", "tien_te": "VND"}},
        ]}
        kq_ghi = v.tep("audit.ghi_ket_qua@1", ghi)["truong"]
        assert kq_ghi["so_sua_loai"] == 1 and kq_ghi["so_ngoai_mau"] == 1
        for kieu, raw, mime in (("xlsx", sinh_xlsx(cong_thuc=False),
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                               ("csv", sinh_csv(), "text/csv")):
            v.tep("audit.phan_luong@1", raw, ten="lo-DEMO." + kieu, mime=mime)

        ai_lo = deepcopy(lo)
        ai_lo["nghiep_vu"] = [dict(lo["nghiep_vu"][0], ma="PC-DEMO-C4-AI", dien_giai="ZZZ DEMO chờ phân loại nội bộ")]
        yc = v.tep("audit.chuan_bi_phan_loai@1", ai_lo)
        assert yc["yeu_cau_ai"]["tai_lieu"]
        ai = doc("tra-loi-ai-dung-enum.json")
        ai["tra_loi_ai"]["chuyen_tiep"] = deepcopy(yc["yeu_cau_ai"]["chuyen_tiep"])
        v.goi("audit.phan_luong_sau_ai@1", ai)
        hd = doc("hoa-don-xml-DEMO.json")
        v.dau_vao.append(deepcopy(hd))
        v.goi("audit.phan_luong_hoa_don@1", hd, loai_nghiep_vu="chi_phi_khac")
        # Đảm bảo chot_ky có bản chụp thật; không kiểm C4 trên bảng rỗng.
        ghim.setattr(chot_ky, "ky_hien_tai", lambda *a: "2026-12")
        lo_chot = deepcopy(lo)
        lo_chot["nghiep_vu"] = []
        v.tep("audit.phan_luong@1", lo_chot)
    assert set(n for n, _ in v.ra) == set(NL)
    assert all(v.core.xem_ngan(app.ma, b) for b in COT)
    assert any(json.loads(d["tong_7_ngay"]) for d in v.core.xem_ngan(app.ma, "ho_so_hanh_vi"))
    return v


@pytest.mark.parametrize("bang", COT)
def test_c4_cot_khop_chinh_xac_hop_dong_2_4(vong, bang):
    khai = next(b for b in app.phieu["ngan_du_lieu"] if b["bang"] == bang)
    assert {c["ma"] for c in khai["truong"]} == COT[bang]
    for dong in vong.core.xem_ngan(app.ma, bang):
        assert set(dong) == COT[bang] | HE_THONG
        if bang == "ho_so_hanh_vi":
            assert all(re.fullmatch(r"[0-9a-f]{32}", h) for h in json.loads(dong["bam_doi_tac"]))


def dau_cam(vong):
    tien, chu = set(), set()
    for nut in vong.dau_vao:
        for duong, o in cac_o(nut):
            if duong.endswith("/so") and o is not None:
                so = Decimal(str(o))
                tien.update((so, abs(so)))
            elif any(duong.endswith("/" + k) for k in
                     ("ngay", "ngay_lap", "doi_tac", "ten_doi_tac", "dien_giai", "noi_dung",
                      "ma_so_thue", "ma_so_thue_ban", "ma_so_thue_mua")):
                if isinstance(o, str) and o:
                    chu.add(o)
    return tien, chu


@pytest.mark.parametrize("bang", COT)
def test_c4_khong_o_nao_chua_chi_tiet_nghiep_vu(vong, bang):
    tien, chu = dau_cam(vong)
    loi = set()
    for i, dong in enumerate(vong.core.xem_ngan(app.ma, bang)):
        if bang == "ho_so_hanh_vi":
            kiem_tong_7_ngay(dong["tong_7_ngay"])
            # Không giữ mã giao dịch ở cột tổng; các bảng khác được giữ mã.
            for nut in vong.dau_vao:
                for duong, o in cac_o(nut):
                    if duong.endswith("/ma") and isinstance(o, str) and o:
                        assert o not in dong["tong_7_ngay"]
        for duong, o in cac_o(dong):
            if o is None or isinstance(o, bool):
                continue
            van_ban = str(o)
            for cam in chu:
                # Timestamp kỹ thuật được §2.4 cho phép và có thể trùng
                # ngày DEMO; mọi ô nghiệp vụ khác vẫn kiểm cả chuỗi con.
                la_ngay = re.fullmatch(r"\d{4}-\d{2}-\d{2}", cam)
                tong_7_ngay = bang == "ho_so_hanh_vi" and duong.startswith("/tong_7_ngay")
                thoi_diem = (duong.rsplit("/", 1)[-1] in
                              {"tao_luc", "sua_luc", "het_han_luc", "doi_bac_luc"}
                              and re.fullmatch(r"\d{4}-\d{2}-\d{2}T.+", van_ban))
                if cam in van_ban and not (la_ngay and (thoi_diem or tong_7_ngay)):
                    loi.add(f"{bang}[{i}]{duong}: chứa {cam}")
            if bang == "ho_so_hanh_vi" and duong.startswith("/tong_7_ngay"):
                continue  # Chỉ miễn dò tiền/ngày; đối tác và nội dung vẫn dò ở trên.
            # So giá trị số chuẩn hóa: bắt cả chuỗi thập phân, JSON số, số có .0.
            cac_so = re.findall(r"(?<![\w.\-])[+-]?\d+(?:\.\d+)?(?![\w.\-])", van_ban)
            for token in cac_so:
                try:
                    so = Decimal(token)
                except InvalidOperation:
                    continue
                if so in tien:
                    loi.add(f"{bang}[{i}]{duong}: chứa số tiền DEMO {token}")
    assert not loi, "\n".join(sorted(loi)[:30])


@pytest.mark.parametrize("nl", NL)
@pytest.mark.parametrize("be_mat", ["phong_bi", "tep_json", "tep_ds_do"])
def test_c5_moi_be_mat_moi_nang_luc(vong, nl, be_mat):
    hat = {d["hat_giong"] for d in vong.core.xem_ngan(app.ma, "luot")}
    phan_tram = {format((Decimal(d["bac"]) * 100).normalize(), "f")
                 for d in vong.core.xem_ngan(app.ma, "ty_le")}
    loi = []
    for ma, ra in vong.ra:
        if ma != nl:
            continue
        if be_mat == "phong_bi":
            loi.extend(cam_c5(ra, hat, phan_tram))
            continue
        ref = ra.get("truong", {}).get(be_mat)
        if ref is None:
            continue  # Năng lực không sinh tệp này, không phải skip ca kiểm.
        raw = vong.core.doc_tep(ref["tep_id"])
        if be_mat == "tep_json":
            loi.extend(cam_c5(json.loads(raw), hat, phan_tram))
        else:
            wb = openpyxl.load_workbook(BytesIO(raw), read_only=True, data_only=False)
            try:
                for ws in wb:
                    for hang in ws:
                        for o in hang:
                            loi.extend(f"{ws.title}!{o.coordinate}: {s}" for s in cam_c5(o.value, hat, phan_tram))
            finally:
                wb.close()
    assert not loi, "\n".join(sorted(set(loi)))


@pytest.mark.parametrize("chu", ["TỶ LỆ", "xÁc_sUẤt", "BẬC", "hạt_giống", "HỆ SỐ", "30%", "30,0 %"])
def test_bo_quet_c5_bat_ca_khoa_va_chu(chu):
    assert cam_c5({chu: chu}, {"ab" * 32}, {"30"})


def test_bo_quet_c5_bat_hex_nhung_cho_phep_ma_binh_thuong():
    assert cam_c5({"ghi_chu": "ab" * 32}, {"ab" * 32}, {"30"})
    assert not cam_c5({"ma": "PC-DEMO-30", "luong": "do"}, {"ab" * 32}, {"30"})


@pytest.mark.parametrize("khoa", KHOA_CHO_PHEP_C5)
def test_c5_chi_mien_ten_khoa_dung_hop_dong(khoa):
    assert not cam_c5({khoa: "an_toan"}, {"ab" * 32}, {"30"})
    assert cam_c5({khoa: "ab" * 32}, {"ab" * 32}, {"30"})
    assert cam_c5({khoa: "30%"}, {"ab" * 32}, {"30"})
    assert cam_c5({khoa: "bậc"}, {"ab" * 32}, {"30"})
    assert cam_c5({"ghi_chu": khoa}, {"ab" * 32}, {"30"})
    assert cam_c5({khoa + "_them": 1}, {"ab" * 32}, {"30"})


@pytest.mark.parametrize("nut", [[], {"DEMO-NCC": {}}, {"ab" * 16: []},
    {"ab" * 16: {"2026-11-31": "0"}}, {"ab" * 16: {"2026-11-01": -1}},
    {"ab" * 16: {"2026-11-01": "-1"}}, {"ab" * 16: {"2026-11-01": "NaN"}},
    {"ab" * 16: {f"2026-11-{i:02}": "0" for i in range(1, 9)}}])
def test_c4_tong_7_ngay_tu_choi_cau_truc_sai(nut):
    with pytest.raises((AssertionError, ValueError)):
        kiem_tong_7_ngay(json.dumps(nut))


def test_c4_tong_7_ngay_hop_le():
    kiem_tong_7_ngay(json.dumps({"ab" * 16: {"2026-11-16": "371234567.123456"}}))
    kiem_tong_7_ngay("{}")
