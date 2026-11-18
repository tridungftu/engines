"""Cổng SDK kiểm an toàn tệp; EX-1 thực hiện kiểm toàn vẹn K1–K6."""

from copy import deepcopy
from hashlib import sha256

from kho_tri_thuc_sdk.engine import Engine, LoiDuongTruyen, LoiNghiepVu

from .nhan_dien import CAU_VUOT_TRAN, TEP_TOI_DA_BYTE, kiem_tep
from .so_do import SoDo
from .kiem_tra import KiemTra, ma_hoa_json


if not all(callable(getattr(Engine, ten, None)) for ten in ("_ghi", "_lam")):
    raise RuntimeError("SDK không có hook nhật ký cần thiết; không thể khởi động an toàn.")


def _chuan_mime(dau_vao):
    """MIME không phân biệt hoa/thường; SDK 2.2.0 hiện chỉ nhận chữ thường."""
    pb = deepcopy(dau_vao)
    if isinstance(pb, dict) and pb.get('loai') == 'tep' and isinstance(pb.get('tep'), dict):
        mime = pb['tep'].get('mime')
        if isinstance(mime, str):
            pb['tep']['mime'] = mime.lower()
    return pb


class _DuongChuanMime:
    """Chỉ bọc đầu vào tải riêng; các lệnh lease/nộp/kết thúc giữ nguyên."""

    def __init__(self, duong):
        self._duong = duong

    def __getattr__(self, ten):
        return getattr(self._duong, ten)

    def doc_dau_vao(self, viec_id):
        return _chuan_mime(self._duong.doc_dau_vao(viec_id))


class CongKiemExcel(Engine):
    """Theo CongHoaDon: chỉ ghi mã cố định, tránh traceback/nội dung exception."""

    def _ghi(self, cau):
        super()._ghi("EX_SDK_THONG_BAO")

    def _lam(self, dt, viec, du_lieu, cfg):
        du_lieu = dict(du_lieu)
        if du_lieu.get('dau_vao') is not None:
            du_lieu['dau_vao'] = _chuan_mime(du_lieu['dau_vao'])
        return super()._lam(_DuongChuanMime(dt), viec, du_lieu, cfg)


app = CongKiemExcel.tu_khai_bao("engine.json")


def _doc_va_kiem(viec):
    tep = viec.dau_vao["tep"]
    viec.kiem_huy()
    try:
        with viec.mo_tep(tep["tep_id"]) as luong:
            raw = bytearray()
            while len(raw) <= TEP_TOI_DA_BYTE:
                viec.kiem_huy()
                khoi = luong.read(min(64 * 1024, TEP_TOI_DA_BYTE + 1 - len(raw)))
                if not khoi:
                    break
                raw.extend(khoi)
    except LoiDuongTruyen as loi:
        if loi.ma != "VUOT_GIOI_HAN_KICH_THUOC":
            raise
        raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_VUOT_TRAN) from None
    kiem_tep(raw, tep["ten"], kiem_huy=viec.kiem_huy)
    viec.kiem_huy()
    return bytes(raw)


@app.nang_luc("excel.toan_ven@1")
def kiem_toan_ven(viec):
    raw = _doc_va_kiem(viec)
    sd = SoDo(raw)
    try:
        kt = KiemTra(sd, viec.tham_so).chay(viec)
        bam = "sha256:" + sha256(raw).hexdigest()
        phien_ban = "e_kiem_excel " + app.phieu["phien_ban"]
        chi_tiet = kt.ket_qua_json(bam, phien_ban)
        viec.kiem_huy()
        tep_json = viec.tai_tep_ra("toan-ven.json", ma_hoa_json(chi_tiet), "application/json")
        return {"loai": "truong", "truong": {
            "so_co_cao": sum(p["muc"] == "Cao" for p in kt.ph),
            "so_co_trung_binh": sum(p["muc"] == "Trung bình" for p in kt.ph),
            "so_kiem_soat": sum(p["muc"] == "Kiểm soát" for p in kt.ph),
            "so_ngoai_nhom": None, "o_dich": None, "tep_bao_cao": None,
            "da_tinh_lai": not any(d[8] for d in kt.kq["sheet"]),
            "co_lien_ket_ngoai": bool(kt._ngoai_o),
            "tep_json": tep_json, "bam_dau_vao": bam, "phien_ban_engine": phien_ban}}
    finally:
        sd.dong()


@app.nang_luc("excel.doc_bang@1")
def doc_bang(viec):
    _doc_va_kiem(viec)
    raise LoiNghiepVu("CHUA_LAM", "Chức năng đọc bảng Excel chưa được triển khai ở lát EX-0.")


if __name__ == "__main__":
    app.chay()
