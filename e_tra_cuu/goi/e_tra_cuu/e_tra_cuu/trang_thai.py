"""Seam thuần ghi bài đo DEMO; chưa có thao tác quản trị SDK 2.1.

Caller tin cậy cấp ngăn và pháp nhân. Mã/băm không xác thực người dùng;
Core phải kiểm quyền trước khi gọi seam này. Không cộng dồn khi gửi lại.
"""

from copy import deepcopy
import json
import re

from kho_tri_thuc_sdk.engine import LoiNghiepVu, NganXungDot


CHI_SO = ("tra_loi_dung", "trich_dan_dung", "tu_choi_dung", "phan_loai_dung")
_BAM = re.compile(r"sha256:[0-9a-f]{64}")
_MA = re.compile(r"[A-Za-z0-9_.-]{1,200}")


def _loi():
    raise LoiNghiepVu("TC_BAI_DO_KHONG_HOP_LE", "Bài đo DEMO không hợp lệ. Anh kiểm tra lại báo cáo.")


def _khoa(ma_dot):
    if (not isinstance(ma_dot, str) or not _MA.fullmatch(ma_dot)
            or not ma_dot.startswith("DEMO-")):
        _loi()
    return {"ma_dot": ma_dot}


def _kiem(gia_tri, khoa):
    """Chỉ metadata đóng; không nhận nguyên văn/câu hỏi/tài liệu hay tỷ lệ tự khai."""
    if not isinstance(gia_tri, dict) or set(gia_tri) != {
        "trang_thai", "bam_bo", "bam_cau_hinh", "phien_ban_engine",
        "chi_so", "bao_cao", "bam_bao_cao",
    }:
        _loi()
    try:
        if len(json.dumps(gia_tri, ensure_ascii=False, allow_nan=False).encode("utf-8")) > 65536:
            _loi()
    except (ValueError, TypeError, UnicodeError, RecursionError):
        _loi()
    for ten in ("bam_bo", "bam_cau_hinh"):
        if not isinstance(gia_tri[ten], str) or not _BAM.fullmatch(gia_tri[ten]):
            _loi()
    if (not isinstance(gia_tri["phien_ban_engine"], str)
            or not re.fullmatch(r"e_tra_cuu [0-9]+\.[0-9]+\.[0-9]+", gia_tri["phien_ban_engine"])):
        _loi()
    chi_so = gia_tri["chi_so"]
    if not isinstance(chi_so, dict) or set(chi_so) != set(CHI_SO):
        _loi()
    for so in chi_so.values():
        if so is None:
            continue
        if (not isinstance(so, dict) or set(so) != {"tu_so", "mau_so"}
                or any(type(n) is not int or n < 0 or n > 9007199254740991 for n in so.values())
                or so["tu_so"] > so["mau_so"]):
            _loi()
    trang_thai = gia_tri["trang_thai"]
    if trang_thai not in ("chua_do", "dang_do", "da_do", "loi"):
        _loi()
    if trang_thai == "chua_do" and any(so is not None for so in chi_so.values()):
        _loi()
    if trang_thai == "da_do" and not any(so and so["mau_so"] > 0 for so in chi_so.values()):
        _loi()
    tep, bam = gia_tri["bao_cao"], gia_tri["bam_bao_cao"]
    if tep is None:
        if bam is not None or trang_thai == "da_do":
            _loi()
    elif (not isinstance(tep, dict) or set(tep) != {"tep_id", "ten", "mime", "kich_thuoc"}
          or not isinstance(tep["tep_id"], str) or not _MA.fullmatch(tep["tep_id"])
          or tep["ten"] != "bao-cao-DEMO.json" or tep["mime"] != "application/json"
          or type(tep["kich_thuoc"]) is not int or not 0 < tep["kich_thuoc"] <= 20971520
          or not isinstance(bam, str) or not _BAM.fullmatch(bam)):
        _loi()
    kq = {**deepcopy(gia_tri), **khoa}
    # SDK 2.2.0 chỉ có kiểu vô hướng trong ngăn. Hai cấu trúc nhỏ đã kiểm
    # được mã hóa JSON vào text; không chứa câu hỏi/nguyên văn, không là kho thứ hai.
    for ten in ("chi_so", "bao_cao"):
        kq[ten] = json.dumps(kq[ten], ensure_ascii=False, allow_nan=False,
                             sort_keys=True, separators=(",", ":")) if kq[ten] is not None else None
    return kq


def lay_hoac_tao_dot(ngan, ma_dot, gia_tri):
    """Gửi lại cùng khóa trả bản cũ, không cộng số đếm hoặc đổi phiên bản."""
    khoa = _khoa(ma_dot)
    gia_tri = _kiem(gia_tri, khoa)
    with ngan.lo() as lo:
        lo.lay_hoac_tao("dot_kiem", khoa, gia_tri)
    return lo.ket_qua[0]


def cap_nhat_cac_dot(ngan, cac_dot):
    """Thay ảnh số đo tuyệt đối bằng CAS trong MỘT lô; lệch bất kỳ → rollback.

    Mỗi mục: {ma_dot, gia_tri, row_version}. Không tự đọc lại/ghi đè hoặc retry.
    """
    if not isinstance(cac_dot, list) or not 1 <= len(cac_dot) <= 100:
        _loi()
    lenh = []
    da_gap = set()
    for muc in cac_dot:
        if not isinstance(muc, dict) or set(muc) != {"ma_dot", "gia_tri", "row_version"}:
            _loi()
        khoa = _khoa(muc["ma_dot"])
        if muc["ma_dot"] in da_gap or type(muc["row_version"]) is not int or muc["row_version"] < 1:
            _loi()
        da_gap.add(muc["ma_dot"])
        lenh.append((khoa, _kiem(muc["gia_tri"], khoa), muc["row_version"]))
    try:
        with ngan.lo() as lo:
            for khoa, gia_tri, phien in lenh:
                lo.sua("dot_kiem", khoa, gia_tri, row_version=phien)
        return lo.ket_qua
    except NganXungDot:
        raise LoiNghiepVu("NGAN_XUNG_DOT", "Bài đo đã thay đổi. Anh đọc lại và thử lại.",
                         thu_lai_duoc=True) from None
