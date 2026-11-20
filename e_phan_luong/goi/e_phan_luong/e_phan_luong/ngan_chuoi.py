"""PL-5: tệp chuyển tiếp do Core cất; chỉ giữ dữ liệu của lượt trong RAM.

Không lưu ngăn riêng, không gọi AI. Core nối ba bước; Core thật chịu
trách nhiệm kiểm quyền/cùng việc ngoài kiểm hình dạng và băm tại đây.
"""
from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from io import BytesIO

from kho_tri_thuc_sdk.engine import LoiDuongTruyen

from . import chuoi_ai, quy_trinh
from .doc_lo import TOI_DA_BYTE
from .loi import loi


class _ViecDocLo:
    """Đọc bằng điểm nối PL-6 trên chính bytes đã kiểm để tránh đọc hai bản.

    Giữ tên/mime gốc cho bộ đọc JSON/Excel/CSV của quy_trinh.doc_tep_lo;
    mọi cổng còn lại lấy từ việc thật, không sửa dau_vao của việc đó.
    """

    def __init__(self, viec, tep_lo, du_lieu):
        self._viec, self._du_lieu = viec, du_lieu
        self.dau_vao = {"loai": "tep", "tep": tep_lo}

    def __getattr__(self, ten):
        return getattr(self._viec, ten)

    def mo_tep(self, tep_id):
        if tep_id != self.dau_vao["tep"]["tep_id"]:
            raise loi("CHUOI_KHONG_KHOP")
        self._viec.kiem_huy()
        return BytesIO(self._du_lieu)


def doc_lo_chuyen_tiep(viec, tep_lo, du_lieu):
    lo, _ = quy_trinh.doc_tep_lo(_ViecDocLo(viec, tep_lo, du_lieu))
    return lo


def chuan_bi(viec, lo, du_lieu, cd) -> dict:
    tai_lieu, _, _ = chuoi_ai.tai_lieu_cho_lo(lo, cd, viec.tham_so)
    # Kiểm prompt/khuôn trước khi tạo tệp chuyển tiếp trên Core.
    tep_goc = viec.dau_vao["tep"]
    ct = chuoi_ai.lap_chuyen_tiep(
        tep_goc, "sha256:" + sha256(du_lieu).hexdigest(),
        viec.tham_so["khau"], not tai_lieu)
    ct = chuoi_ai.them_bam_chuyen_tiep(ct, viec.tham_so, tai_lieu)
    yeu_cau = chuoi_ai.lap_yeu_cau_ai(tai_lieu, cd.danh_muc, viec.tham_so, ct)
    tep_lo = viec.tai_tep_ra(tep_goc["ten"], du_lieu, tep_goc["mime"])
    ct = chuoi_ai.lap_chuyen_tiep(
        tep_lo, ct["phan_luong"]["bam_tep"], viec.tham_so["khau"], not tai_lieu)
    yeu_cau["yeu_cau_ai"]["chuyen_tiep"] = chuoi_ai.them_bam_chuyen_tiep(
        ct, viec.tham_so, tai_lieu)
    return yeu_cau


def phan_luong_sau_ai(viec) -> dict:
    pl = chuoi_ai.doc_chuyen_tiep(viec.dau_vao)
    chuoi_ai.kiem_tham_chieu_tep(viec.dau_vao)
    tep_lo = pl["tep_lo"]
    try:
        with viec.mo_tep(tep_lo["tep_id"]) as tep:
            du_lieu = tep.read(TOI_DA_BYTE + 1)
    except LoiDuongTruyen as exc:
        if exc.http_status in (403, 404):
            raise loi("CHUOI_KHONG_KHOP") from None
        raise
    if (len(du_lieu) != tep_lo["kich_thuoc"]
            or "sha256:" + sha256(du_lieu).hexdigest() != pl["bam_tep"]):
        raise loi("CHUOI_KHONG_KHOP")
    if (pl["khau"] != viec.tham_so.get("khau")
            or pl.get("bam_cai_dat") != chuoi_ai.bam_cai_dat(viec.tham_so)):
        raise loi("CHUOI_KHONG_KHOP")
    lo = doc_lo_chuyen_tiep(viec, tep_lo, du_lieu)
    cd = quy_trinh.doc_cai_dat(viec.tham_so, lo)
    tai_lieu, anh_xa, canh_bao = chuoi_ai.tai_lieu_cho_lo(lo, cd, viec.tham_so)
    if (pl.get("bam_tai_lieu") != chuoi_ai.bam_tai_lieu(tai_lieu)
            or pl["khong_can_ai"] != (not tai_lieu)):
        raise loi("CHUOI_KHONG_KHOP")
    loai_ai = {}
    if not pl["khong_can_ai"]:
        diem = viec.tham_so.get("nguong_tin_cay", 0.7)
        if type(diem) not in (int, float, Decimal):
            raise loi("THAM_SO_KHONG_HOP_LE")
        theo_tai_lieu, canh_bao_ai = chuoi_ai.doc_tra_loi_ai(
            viec.dau_vao, danh_muc=cd.danh_muc, so_tai_lieu=len(tai_lieu),
            nguong_tin_cay=Decimal(str(diem)))
        canh_bao.extend(canh_bao_ai)
        theo_dong = {chi_so: loai for i, loai in theo_tai_lieu.items()
                     for chi_so in anh_xa[i]}
        loai_ai = {nv.ma: theo_dong[nv.chi_so] for nv in lo.nghiep_vu
                   if nv.chi_so in theo_dong}
    return quy_trinh.chay_phan_luong(viec, lo, du_lieu,
                                      loai_ai=loai_ai, canh_bao_them=canh_bao)
