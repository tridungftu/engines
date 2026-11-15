"""DC-10: xác nhận chỉ thêm; adapter nội bộ, chưa có binding Core thật.

`cong` là đối tượng do host Core tin cậy cấp, KHÔNG dựng từ JSON/UI.
Không đăng ký năng lực/API giả, không dùng quyền Admin ngăn thay C-DC-03.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganXungDot, ChuaRo

from . import ho_so as hs
from . import chuan_bi_ai as cb
from . import tong_hop as th

LUA_CHON = ("loi_ocr", "thay_doi_da_thong_nhat", "ban_ky_sai", "khong_anh_huong")
_LOI = {
    "DC_CHUA_CO_CONG_XAC_NHAN": "Chưa có cổng xác nhận và phân quyền của Core. Anh chỉ có thể xem kết quả.",
    "DC_CHUA_CO_CONG_MODULE": "Chưa có cổng chuyển yêu cầu cho module. Trạng thái hiệu lực chưa được cập nhật.",
    "DC_KHONG_CO_QUYEN": "Anh chưa được giao quyền thực hiện thao tác này trên hồ sơ.",
    "DC_SAI_XAC_NHAN": "Xác nhận chưa hợp lệ. Anh kiểm tra lựa chọn, nội dung đúng hoặc lý do.",
    "DC_TRUNG_YEU_CAU": "Mã yêu cầu đã được dùng cho xác nhận khác. Anh tải lại trước khi xác nhận.",
    "DC_DA_XAC_NHAN": "Anh đã xác nhận điểm này. Nhật ký được giữ nguyên; người thứ hai phải là người khác.",
    "DC_XUNG_DOT": "Kết quả vừa thay đổi. Anh tải lại trước khi xác nhận.",
    "DC_SAI_NGUON": "Hồ sơ đối chiếu không khớp nguồn đã ghim. Anh kiểm tra lại cặp tài liệu và phiên bản.",
}


def loi(ma):
    raise LoiNghiepVu(ma, _LOI[ma], thu_lai_duoc=ma == "DC_XUNG_DOT")


@dataclass(frozen=True)
class NguCanhXacNhan:
    """Hợp đồng adapter đề nghị C-DC-03; chưa phải thuộc tính SDK."""
    phap_nhan_id: str
    module: str
    ma_luot: str
    nguoi_id: str
    ten_nguoi: str
    luc: str
    quyen: tuple[str, ...]
    diem_duoc_xac_nhan: tuple[str, ...] = ()


def _ngu_canh(viec, cong, ma_luot, quyen):
    if cong is None or not callable(getattr(cong, "cap_ngu_canh", None)):
        loi("DC_CHUA_CO_CONG_XAC_NHAN")
    c = cong.cap_ngu_canh(viec, ma_luot)
    if (type(c) is not NguCanhXacNhan or type(c.quyen) is not tuple or
            type(c.diem_duoc_xac_nhan) is not tuple or
            any(type(v) is not str or not v.strip() for v in (*c.quyen, *c.diem_duoc_xac_nhan))):
        loi("DC_KHONG_CO_QUYEN")
    scope = cb.pham_vi(viec)
    if (c.phap_nhan_id != scope["phap_nhan_id"] or c.module != scope["module"] or
            c.ma_luot != ma_luot or quyen not in c.quyen or
            any(type(v) is not str or not v.strip() for v in (c.nguoi_id, c.ten_nguoi, c.luc))):
        loi("DC_KHONG_CO_QUYEN")
    try:
        if datetime.fromisoformat(c.luc.replace("Z", "+00:00")).utcoffset() is None:
            loi("DC_KHONG_CO_QUYEN")
    except (ValueError, TypeError):
        loi("DC_KHONG_CO_QUYEN")
    return c


class _ViecNguon:
    def __init__(self, viec, pb):
        self._viec, self.dau_vao = viec, pb

    def __getattr__(self, ten):
        return getattr(self._viec, ten)


def _doc(viec, ngan, cau_hinh, ma_luot):
    """Mở lại nguồn và báo cáo qua quyền việc; JSON UI không phải kết quả tin cậy."""
    ban = ngan.doc("luot_doi_chieu", {"ma_luot": ma_luot})
    if ban is None or ban.gia_tri.get("trang_thai") != "da_xuat":
        loi("DC_SAI_NGUON")
    try:
        saved = hs.mo_phong_bi(ban.gia_tri["phong_bi"])
        t = saved["ket_qua"]["truong"]
        doc = hs._DocTep(viec, deepcopy(cau_hinh))
        raw = doc.doc({"tep": t["tep_json"], "bam": saved["bam_json"]}, cau_hinh["ho_so_mib"] * hs.MIB)
        s = hs.doc_json(raw, viec.kiem_huy)
        ref = s["tong_hop"]["ho_so_dau_vao"]
        src_raw = doc.doc(ref, cau_hinh["ho_so_mib"] * hs.MIB)
        src = hs.doc_json(src_raw, viec.kiem_huy)
        pb = hs._phong_bi(src, ref["tep"], src_raw)
        source, source_doc = th.doc_ho_so(_ViecNguon(viec, pb), ngan, cau_hinh)
        # Tổng ngân sách cả hai bộ đọc, kể cả bytes bị đọc lại.
        if doc.tong + source_doc.tong > min(doc.cau_hinh["tong_byte_tep_con"], source_doc.cau_hinh["tong_byte_tep_con"]):
            hs.loi("DC_QUA_GIOI_HAN")
        expected = th.tong_hop(source)
        expected["tong_hop"]["ho_so_dau_vao"] = ref
        if {k: v for k, v in s.items() if k != "bao_cao_pdf"} != expected:
            loi("DC_SAI_NGUON")
        if (any(t[k] != s[k] for k in ("ket_luan", "da_kiem_du", "de_nghi_chan")) or
                any(t[k] != s["tom_tat"][k] for k in th.TRUONG_DEM) or
                s["bao_cao_pdf"]["tep"] != t["tep_pdf"]):
            loi("DC_SAI_NGUON")
        pdf = doc.doc(s["bao_cao_pdf"], cau_hinh["tep_mib"] * hs.MIB)
        if not pdf.startswith(b"%PDF-"):
            loi("DC_SAI_NGUON")
        if doc.tong + source_doc.tong > source_doc.cau_hinh["tong_byte_tep_con"]:
            hs.loi("DC_QUA_GIOI_HAN")
        return ban, s, saved["bam_json"]
    except (KeyError, TypeError, ValueError):
        loi("DC_SAI_NGUON")


def _nhat_ky(viec, ngan, ma_luot, bam_ket_qua):
    out, tiep = [], None
    while True:
        viec.kiem_huy()
        trang = ngan.tim("xac_nhan", loc={"ma_luot": ma_luot}, gioi_han=500, tiep=tiep)
        for b in trang.danh_sach:
            row = hs.mo_phong_bi(b.gia_tri["noi_dung"])
            if row["bam_ket_qua"] != bam_ket_qua or row["ma_luot"] != ma_luot:
                loi("DC_SAI_NGUON")
            out.append(row)
        tiep = trang.tiep
        if tiep is None:
            return out


def _cac_diem(s):
    ds = {d["ma_diem"]: d["muc"] for d in s["diem_lech"]}
    for v in s.get("vung_sua_tay") or []:
        if v["ma"] in ds:
            loi("DC_SAI_NGUON")
        ds[v["ma"]] = "nghiem_trong"
    return ds


def dieu_kien_module(s, nhat_ky):
    """Chỉ lập bằng chứng đề nghị. Module/Core phải tự tính lại trước đổi hiệu lực."""
    diem = _cac_diem(s)
    bat_buoc = {k: v for k, v in diem.items() if v in ("nghiem_trong", "can_xem")}
    thieu, mau_thuan, ban_ky_sai = [], [], []
    for ma, muc in bat_buoc.items():
        rows = [r for r in nhat_ky if r["ma_diem"] == ma]
        if any(r["lua_chon"] == "ban_ky_sai" for r in rows):
            ban_ky_sai.append(ma)
        quyet_dinh = {(r["lua_chon"], r["noi_dung_dung"], r["ly_do"]) for r in rows}
        if len(quyet_dinh) > 1:
            mau_thuan.append(ma)
        hop_le = bool(rows) and len(quyet_dinh) == 1 and not any(r["lua_chon"] == "ban_ky_sai" for r in rows)
        if hop_le and muc == "nghiem_trong" and rows[0]["lua_chon"] == "thay_doi_da_thong_nhat":
            # Q03: một người phụ trách và người duyệt có thẩm quyền khác người.
            hop_le = any(a["nguoi_id"] != b["nguoi_id"] and b["duoc_duyet_cap_hai"]
                         for a in rows for b in rows)
        if not hop_le:
            thieu.append(ma)
    thieu_kiem = s["tong_hop"]["phan_chua_kiem"]
    return {"du_dieu_kien_de_nghi": s["da_kiem_du"] is True and not thieu_kiem and
                not thieu and not ban_ky_sai and not mau_thuan,
            "diem_chua_du_xac_nhan": thieu, "diem_ban_ky_sai": ban_ky_sai,
            "diem_mau_thuan": mau_thuan, "phan_chua_kiem": deepcopy(thieu_kiem)}


def doc_ket_qua(viec, ngan, cau_hinh, ma_luot, *, cong=None):
    c = _ngu_canh(viec, cong, ma_luot, "xem_doi_chieu")
    ban, s, bam = _doc(viec, ngan, cau_hinh, ma_luot)
    rows = _nhat_ky(viec, ngan, ma_luot, bam)
    # Nếu lượt đổi giữa lúc đọc báo cáo và nhật ký, không trả view trộn phiên bản.
    if ngan.doc("luot_doi_chieu", {"ma_luot": ma_luot}).row_version != ban.row_version:
        loi("DC_XUNG_DOT")
    return {"ma_luot": ma_luot, "row_version": ban.row_version, "bam_ket_qua": bam, "bao_cao": s, "xac_nhan": rows,
            "quyen": {"xac_nhan": "xac_nhan_doi_chieu" in c.quyen,
                      "gui_yeu_cau_module": "gui_yeu_cau_module" in c.quyen,
                      "diem_duoc_xac_nhan": list(c.diem_duoc_xac_nhan)},
            "dieu_kien_module": dieu_kien_module(s, rows)}


def _kiem_yeu_cau(y):
    khoa = {"ma_luot", "ma_diem", "ma_yeu_cau", "row_version", "lua_chon", "noi_dung_dung", "ly_do"}
    if type(y) is not dict or set(y) - khoa or not khoa - {"noi_dung_dung", "ly_do"} <= y.keys():
        loi("DC_SAI_XAC_NHAN")
    y = deepcopy(y)
    for k in ("ma_luot", "ma_diem", "ma_yeu_cau"):
        if type(y[k]) is not str or not y[k].strip() or len(y[k]) > 200:
            loi("DC_SAI_XAC_NHAN")
    if type(y["row_version"]) is not int or y["row_version"] < 1 or y["lua_chon"] not in LUA_CHON:
        loi("DC_SAI_XAC_NHAN")
    for k in ("noi_dung_dung", "ly_do"):
        v = y.get(k, "")
        if type(v) is not str or len(v) > 4000:
            loi("DC_SAI_XAC_NHAN")
        y[k] = v.strip()
    if (y["lua_chon"] == "thay_doi_da_thong_nhat" and not y["noi_dung_dung"] or
            y["lua_chon"] == "khong_anh_huong" and not y["ly_do"]):
        loi("DC_SAI_XAC_NHAN")
    return y


def _da_luu(ngan, y, c):
    ban = ngan.doc("xac_nhan", {"ma_yeu_cau": y["ma_yeu_cau"]})
    if ban is None:
        return None
    row = hs.mo_phong_bi(ban.gia_tri["noi_dung"])
    if row["yeu_cau"] != y or row["nguoi_id"] != c.nguoi_id or row["module"] != c.module:
        loi("DC_TRUNG_YEU_CAU")
    return {"da_luu": True, "ma_yeu_cau": y["ma_yeu_cau"], "ma_xac_nhan": row["ma_xac_nhan"]}


def xac_nhan(viec, ngan, cau_hinh, yeu_cau, *, cong=None):
    y = _kiem_yeu_cau(yeu_cau)
    c = _ngu_canh(viec, cong, y["ma_luot"], "xac_nhan_doi_chieu")
    if "xem_doi_chieu" not in c.quyen or y["ma_diem"] not in c.diem_duoc_xac_nhan:
        loi("DC_KHONG_CO_QUYEN")
    ban, s, bam = _doc(viec, ngan, cau_hinh, y["ma_luot"])
    cu = _da_luu(ngan, y, c)
    if cu is not None:
        return cu
    if ban.row_version != y["row_version"]:
        loi("DC_XUNG_DOT")
    if _cac_diem(s).get(y["ma_diem"]) not in ("nghiem_trong", "can_xem"):
        loi("DC_SAI_XAC_NHAN")
    rows = _nhat_ky(viec, ngan, y["ma_luot"], bam)
    if any(r["ma_diem"] == y["ma_diem"] and r["nguoi_id"] == c.nguoi_id for r in rows):
        loi("DC_DA_XAC_NHAN")
    ma = hs.bam(hs.json_bytes([c.phap_nhan_id, y["ma_yeu_cau"]]))
    row = {**y, "yeu_cau": y, "ma_xac_nhan": ma, "bam_ket_qua": bam,
           "nguoi_id": c.nguoi_id, "ten_nguoi": c.ten_nguoi, "luc": c.luc, "module": c.module,
           "duoc_duyet_cap_hai": "duyet_thay_doi_nghiem_trong" in c.quyen}
    viec.kiem_huy()
    try:
        with ngan.lo() as lo:
            lo.them("xac_nhan", {"ma_xac_nhan": ma, "ma_yeu_cau": y["ma_yeu_cau"],
                    "ma_luot": y["ma_luot"], "ma_diem": y["ma_diem"], "noi_dung": hs.dong_phong_bi(row)})
            # CAS cùng lô; giữ nguyên kết quả máy và trạng thái da_xuat.
            lo.sua("luot_doi_chieu", {"ma_luot": y["ma_luot"]},
                   {"trang_thai": "da_xuat"}, row_version=ban.row_version)
    except NganXungDot:
        cu = _da_luu(ngan, y, c)
        if cu is not None:
            return cu
        loi("DC_XUNG_DOT")
    return {"da_luu": True, "ma_yeu_cau": y["ma_yeu_cau"], "ma_xac_nhan": ma}


def gui_yeu_cau_module(viec, ngan, cau_hinh, ma_luot, *, cong=None):
    """C-DC-04 do host cấp; không event, không gọi engine, không tự mở chặn."""
    if cong is None or not callable(getattr(cong, "gui_yeu_cau_module", None)):
        loi("DC_CHUA_CO_CONG_MODULE")
    view = doc_ket_qua(viec, ngan, cau_hinh, ma_luot, cong=cong)
    c = _ngu_canh(viec, cong, ma_luot, "gui_yeu_cau_module")
    y = {"ma_luot": ma_luot, "row_version": view["row_version"],
         "bam_ket_qua": view["bam_ket_qua"], "phap_nhan_id": c.phap_nhan_id, "module": c.module,
         "dieu_kien": view["dieu_kien_module"], "nguoi_nhan": "nguoi_nop_va_nguoi_phu_trach"}
    y["ma_yeu_cau"] = hs.bam(hs.json_bytes(y))
    viec.kiem_huy()
    ack = cong.gui_yeu_cau_module(viec, deepcopy(y))
    if type(ack) is not dict or ack.get("da_nhan") is not True:
        raise ChuaRo(y["ma_yeu_cau"])
    return {"da_nhan": True, "ma_yeu_cau": y["ma_yeu_cau"]}
