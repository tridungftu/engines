"""DC-11: lõi học có duyệt, chỉ kiểm qua adapter Core giả.

Không đăng ký thao tác SDK. `cong` phải do host tin cậy cấp, không nhận
từ payload/UI. Nguồn Q14 là danh sách chứng minh, không tự bật cho DC-7.
"""
from copy import deepcopy
from dataclasses import dataclass

from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganXungDot

from . import ho_so as hs
from . import xac_nhan as xn
from . import lech_dau as ld
from . import tu_dien as td
from . import quy_tac as qt
from .so_chu import bo_dau


def loi(ma="DC_KHONG_DU_CAN_CU"):
    raise LoiNghiepVu(ma, {
        "DC_CAP_DOI_NGHIA": "Cặp từ có thể đổi nghĩa hoặc thuộc vùng bảo vệ. Không được đưa vào bộ lỗi OCR thường gặp.",
        "DC_KHONG_DU_CAN_CU": "Chưa đủ xác nhận, căn cứ không đổi nghĩa hoặc ngưỡng đã đo và duyệt. Chưa thể duyệt cặp lỗi OCR.",
        "DC_XUNG_DOT": "Danh mục vừa thay đổi. Anh tải lại trước khi thực hiện.",
    }[ma], thu_lai_duoc=ma == "DC_XUNG_DOT")


@dataclass(frozen=True)
class BoQ14:
    """Đề nghị adapter C-DC-03/Q14, KHÔNG phải API/thuộc tính SDK.

    Host chứng thực bộ sạch có giấy phép, phê duyệt nguồn/bằng chứng và
    đã loại định danh. Kiểu dữ liệu hoặc băm không thay xác thực của host.
    """
    noi_dung: dict
    bam: str
    ma_phe_duyet: str
    vo_danh: bool


def _bo_q14(viec, cong):
    if not callable(getattr(cong, "cap_bo_q14", None)):
        loi()
    b = cong.cap_bo_q14(viec)
    if (type(b) is not BoQ14 or b.vo_danh is not True or
            type(b.ma_phe_duyet) is not str or not b.ma_phe_duyet.strip() or
            b.bam != hs.bam(hs.json_bytes(b.noi_dung))):
        loi()
    try:
        return td.TuDien(deepcopy(b.noi_dung), viec.kiem_huy), b.bam
    except LoiNghiepVu:
        loi()


def _nguong(cau_hinh):
    n = cau_hinh.get("hoc_loi_ocr")
    if (type(n) is not dict or set(n) != {"so_lan", "phien_ban", "nguon_do", "ma_phe_duyet"} or
            type(n["so_lan"]) is not int or n["so_lan"] < 1 or
            any(type(n[k]) is not str or not 1 <= len(n[k]) <= 1000 or not n[k].strip()
                for k in ("phien_ban", "nguon_do", "ma_phe_duyet"))):
        loi()
    return deepcopy(n)


def kiem_cap(s, ma_diem, tu_dien, kiem=lambda: None):
    """Hàm thuần: lấy token từ snapshot; không nhận cặp từ UI tự khai."""
    ds = [d for d in s["diem_lech"] if d["ma_diem"] == ma_diem]
    if len(ds) != 1:
        loi()
    d = ds[0]
    if d.get("vung_bao_ve") or d.get("quy_tac_trung") or d.get("muc_san") == "nghiem_trong":
        loi("DC_CAP_DOI_NGHIA")
    if d.get("nhom") != "chi_lech_dau":
        loi()
    tus = {k: td.CacTu(s["van_ban"][k]["van_ban_tai_lieu"]["van_ban"], kiem)
           for k in ("word", "ban_ky")}
    cum = ld._cum(d, tus)
    if cum is None or any(len(cum[k]["tu"]) != 1 for k in cum):
        loi()
    # Mở rộng ra toàn token trước khi kiểm vùng bảo vệ; diff có thể chỉ là dấu.
    q = qt.kiem_bo_cung(s["bo_quy_tac"]["noi_dung"])
    for ben, v in cum.items():
        ban = qt._Ban(s, ben, kiem)
        if any(a["bat_dau"] < v["ket_thuc"] and v["bat_dau"] < a["ket_thuc"]
               for a in qt._vung_bao_ve(ban, q)):
            loi("DC_CAP_DOI_NGHIA")
    w, o = (td.chuan(cum[k]["van_ban"]) for k in ("word", "ban_ky"))
    # Chỉ học một token chữ thường vô danh. Không học tên/mã/số/cụm định danh.
    if (any(t in td._CO_NGHIA for t in (w, o)) or
            tu_dien.tra(w, o)[0] == "ca_hai_co_nghia"):
        loi("DC_CAP_DOI_NGHIA")
    if (not all(t.isalpha() and len(t) <= 200 for t in (w, o)) or
            w == o or bo_dau(w) != bo_dau(o) or
            tu_dien.tra(w, o)[0] != "vo_nghia_co_can_cu"):
        loi()
    return {"word": w, "ocr": o, "bam_can_cu": hs.bam(hs.json_bytes(tu_dien.tra(w, o)[1]))}


def _noi_dung(row):
    return hs.mo_phong_bi(row.gia_tri["noi_dung"])


def _dong(value):
    if len(hs.json_bytes(value)) > 65536:
        hs.loi("DC_QUA_GIOI_HAN")
    return hs.dong_phong_bi(value)


def _nguon(viec, ngan, cau_hinh, ma_luot, ma_xac_nhan, c):
    ban, s, bam = xn._doc(viec, ngan, cau_hinh, ma_luot)
    rows = xn._nhat_ky(viec, ngan, ma_luot, bam)
    ds = [r for r in rows if r["ma_xac_nhan"] == ma_xac_nhan and r["lua_chon"] == "loi_ocr"
          and r["module"] == c.module]
    if len(ds) != 1:
        loi()
    r = ds[0]
    # Xác nhận mâu thuẫn trên cùng điểm chưa đủ căn cứ để học.
    if any(a["ma_diem"] == r["ma_diem"] and a["lua_chon"] != "loi_ocr" for a in rows):
        loi()
    return ban, s, r, bam


def de_xuat(viec, ngan, cau_hinh, ma_luot, ma_xac_nhan, *, cong=None):
    """Lõi chưa nối SDK; chỉ test CoreGia/NganBoNho, không là handler."""
    c = xn._ngu_canh(viec, cong, ma_luot, "de_xuat_loi_ocr")
    if "xem_doi_chieu" not in c.quyen:
        xn.loi("DC_KHONG_CO_QUYEN")
    n = _nguong(cau_hinh)
    tu_dien, q14 = _bo_q14(viec, cong)
    ban, s, r, bam = _nguon(viec, ngan, cau_hinh, ma_luot, ma_xac_nhan, c)
    cap = kiem_cap(s, r["ma_diem"], tu_dien, viec.kiem_huy)
    khoa = {"bam_cap_tu": hs.bam(hs.json_bytes([cap, q14]))}
    cu = ngan.doc("loi_ocr_de_xuat", khoa)
    row = _noi_dung(cu) if cu else {**cap, "q14": q14, "lan_gap": [], "trang_thai": "cho_nguong"}
    if any(a["module"] != c.module for a in row["lan_gap"]):
        xn.loi("DC_KHONG_CO_QUYEN")
    # Đếm một vị trí nguồn một lần, kể cả hai người xác nhận hoặc mất ACK.
    ma_gap = hs.bam(hs.json_bytes([ma_luot, bam, r["ma_diem"]]))
    da_gap = any(a["ma_gap"] == ma_gap for a in row["lan_gap"])
    if da_gap and (row.get("nguong") == n or row["trang_thai"] == "da_duyet"):
        return {**khoa, "so_lan": len(row["lan_gap"]), "trang_thai": row["trang_thai"]}
    if not da_gap:
        row["lan_gap"].append({"ma_gap": ma_gap, "ma_xac_nhan": ma_xac_nhan,
            "ma_luot": ma_luot, "ma_diem": r["ma_diem"], "bam_ket_qua": bam, "module": c.module})
    row["nguong"] = n
    if row["trang_thai"] != "da_duyet":
        row["trang_thai"] = "cho_duyet" if len(row["lan_gap"]) >= n["so_lan"] else "cho_nguong"
    value = {"noi_dung": _dong(row)}
    viec.kiem_huy()
    try:
        with ngan.lo() as lo:
            if cu:
                lo.sua("loi_ocr_de_xuat", khoa, value, row_version=cu.row_version)
            else:
                lo.them("loi_ocr_de_xuat", {**khoa, **value})
            lo.sua("luot_doi_chieu", {"ma_luot": ma_luot}, {"trang_thai": "da_xuat"}, row_version=ban.row_version)
    except NganXungDot:
        loi("DC_XUNG_DOT")
    return {**khoa, "so_lan": len(row["lan_gap"]), "trang_thai": row["trang_thai"]}


def bo_moi(cap, q14):
    """Hàm thuần tạo bộ một cặp vô danh; Core ghép/ghim cho việc MỚI."""
    phien_ban = hs.bam(hs.json_bytes([cap, q14]))
    return {"phien_ban": 1, "ma": "loi_ocr_da_duyet", "phien_ban_bo": phien_ban,
        "nguon": "Bộ cặp vô danh theo DC-Q14; " + q14,
        "giay_phep": "Theo giấy phép nguồn DC-Q14 đã được phê duyệt.", "pham_vi": "engine",
        "am_tiet_co_nghia": [cap["word"]], "tu_co_nghia": [],
        "cap_vo_nghia_co_can_cu": [{"word": cap["word"], "ocr": cap["ocr"],
            "can_cu": "Cặp vô danh đã duyệt; " + cap["bam_can_cu"]}]}


def duyet(viec, ngan, cau_hinh, ma_luot, bam_cap_tu, row_version, ma_yeu_cau, *, cong=None):
    """Admin qua adapter chung; trạng thái + bộ mới cùng một Ngan.lo."""
    c = xn._ngu_canh(viec, cong, ma_luot, "duyet_loi_ocr")
    if "admin_core" not in c.quyen or "xem_doi_chieu" not in c.quyen:
        xn.loi("DC_KHONG_CO_QUYEN")
    if (type(row_version) is not int or row_version < 1 or type(ma_yeu_cau) is not str or
            not 1 <= len(ma_yeu_cau) <= 200 or not ma_yeu_cau.strip()):
        loi()
    n = _nguong(cau_hinh)
    tu_dien, q14 = _bo_q14(viec, cong)
    khoa = {"bam_cap_tu": bam_cap_tu}
    ban = ngan.doc("loi_ocr_de_xuat", khoa)
    if ban is None:
        loi()
    row = _noi_dung(ban)
    if row["q14"] != q14 or row.get("nguong") != n or len(row["lan_gap"]) < n["so_lan"]:
        loi()
    # Kiểm lại mọi xác nhận/nguồn/quyền; không duyệt chỉ dựa vào bộ đếm.
    luot = {}
    cap = {k: row[k] for k in ("word", "ocr", "bam_can_cu")}
    for gap in row["lan_gap"]:
        if gap["module"] != c.module:
            xn.loi("DC_KHONG_CO_QUYEN")
        xn._ngu_canh(viec, cong, gap["ma_luot"], "duyet_loi_ocr")
        b, s, r, bam = _nguon(viec, ngan, cau_hinh, gap["ma_luot"], gap["ma_xac_nhan"], c)
        if (r["ma_diem"] != gap["ma_diem"] or bam != gap["bam_ket_qua"] or
                kiem_cap(s, r["ma_diem"], tu_dien, viec.kiem_huy) != cap):
            loi()
        luot[gap["ma_luot"]] = b
    if ma_luot not in luot or len(luot) > 98:
        loi()
    if row["trang_thai"] == "da_duyet":
        a = row["duyet"]
        if a["ma_yeu_cau"] == ma_yeu_cau and a["nguoi_id"] == c.nguoi_id:
            return {"da_duyet": True, "phien_ban": row["phien_ban"]}
        loi("DC_XUNG_DOT")
    if ban.row_version != row_version or row["trang_thai"] != "cho_duyet":
        loi("DC_XUNG_DOT")
    bo = bo_moi(cap, q14)
    td.TuDien(bo, viec.kiem_huy)
    pb = bo["phien_ban_bo"]
    da_co = ngan.doc("loi_ocr_da_duyet", {**khoa, "phien_ban": pb})
    if da_co is not None and _noi_dung(da_co) != bo:
        loi("DC_XUNG_DOT")
    row.update(trang_thai="da_duyet", phien_ban=pb,
        duyet={"ma_yeu_cau": ma_yeu_cau, "nguoi_id": c.nguoi_id, "luc": c.luc, "module": c.module,
               "row_version_truoc": row_version})
    viec.kiem_huy()
    try:
        with ngan.lo() as lo:
            lo.sua("loi_ocr_de_xuat", khoa, {"noi_dung": _dong(row)}, row_version=ban.row_version)
            # Chỉ tạo, không sửa phiên bản đã có. Không đưa người/hồ sơ/pháp nhân vào bộ chung.
            lo.lay_hoac_tao("loi_ocr_da_duyet", {**khoa, "phien_ban": pb}, {"noi_dung": _dong(bo)})
            for ma, b in luot.items():
                lo.sua("luot_doi_chieu", {"ma_luot": ma}, {"trang_thai": "da_xuat"}, row_version=b.row_version)
    except NganXungDot:
        loi("DC_XUNG_DOT")
    return {"da_duyet": True, "phien_ban": pb}
