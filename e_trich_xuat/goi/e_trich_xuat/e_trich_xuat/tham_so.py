"""TX-2: snapshot của từng việc; dùng lại bộ kiểm dòng E1 của SDK.

Chuyển có sửa phần kiểm hash/chọn danh mục trong ma-nguon/tham_so.py và
tich_hop.py. Không tra XLSX, không có bộ dự phòng hoặc adapter gọi AI.
"""

import hashlib
import json
import math
import re

from kho_tri_thuc_sdk import danh_muc_tham_so as e1
from kho_tri_thuc_sdk.engine import LoiNghiepVu


BO_TOI_DA_BYTE = 64 * 1024
DONG_DANG_DUNG_TOI_DA = 200
MA = re.compile(r"[A-Za-z0-9_.:-]{1,200}\Z")
BAM = re.compile(r"sha256:[0-9a-fA-F]{64}\Z")
CAU_LOI = {
    "THIEU_BO_THAM_SO": "Việc chưa có bộ tham số đã ghim.",
    "SAI_BAM_BO_THAM_SO": "Bộ tham số không khớp mã kiểm tra.",
    "BO_THAM_SO_KHONG_HOP_LE": "Bộ tham số không đúng cấu trúc hoặc có mã trùng.",
    "THIEU_PROMPT": "Module chưa cung cấp hướng dẫn trích thông tin.",
    "CAU_HOI_THEM_CHUA_DUYET": "Câu hỏi bổ sung chưa được bật.",
    "VUOT_GIOI_HAN": "Yêu cầu vượt giới hạn xử lý.",
    "VUOT_NGAN_SACH": "Tài liệu vượt ngân sách đầu vào đã cấu hình.",
}


def loi(ma):
    raise LoiNghiepVu(ma, CAU_LOI[ma]) from None


def bam_bytes(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def json_bytes(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _cac_cap(cap):
    out = {}
    for k, v in cap:
        if k in out:
            raise ValueError("JSON lặp khóa")
        out[k] = v
    return out


def _cam_hang_so(v):
    raise ValueError("JSON có số không hữu hạn")


def _so_thuc(v):
    so = float(v)
    if not math.isfinite(so):
        raise ValueError("JSON có số không hữu hạn")
    return so


def doc_json(chuoi):
    """Không chuẩn hóa chuỗi; từ chối cả khóa lặp lồng nhau và 1e9999."""
    v = json.loads(chuoi, object_pairs_hook=_cac_cap,
                   parse_constant=_cam_hang_so, parse_float=_so_thuc)
    json_bytes(v)  # Cả Unicode surrogate thoát trong JSON cũng phải là UTF-8.
    return v


def _dong_e1(dong):
    if not isinstance(dong, dict) or set(dong) != set(e1.KHOA):
        raise ValueError("Thiếu cột E1")
    if any(not isinstance(dong[k], str) for k in e1.KHOA
           if k not in ("dung", "luon_cloud", "muc")):
        raise ValueError("Sai kiểu cột E1")
    if (type(dong["dung"]) is not bool or type(dong["luon_cloud"]) is not bool
            or type(dong["muc"]) is not int):
        raise ValueError("Sai kiểu cột E1")
    return [
        ("Có" if dong[k] else "Không") if k in ("dung", "luon_cloud") else dong[k]
        for k in e1.KHOA]


def _quy_tac_e1(quy_tac):
    if not isinstance(quy_tac, list):
        raise ValueError("Sai quy tắc")
    rows = [e1.QUY_TAC_HEADER]
    for r in quy_tac:
        if (not isinstance(r, dict)
                or set(r) != {"kieu", "ma_tham_so", "dieu_kien", "doi_chieu"}
                or not isinstance(r["ma_tham_so"], list)
                or not all(isinstance(x, str) for x in r["ma_tham_so"])
                or not all(isinstance(r[k], str) for k in ("kieu", "dieu_kien", "doi_chieu"))):
            raise ValueError("Sai quy tắc")
        rows.append([r["kieu"], ";".join(r["ma_tham_so"]), r["dieu_kien"], r["doi_chieu"]])
    return rows


def doc_bo(tham_so):
    chuoi = tham_so.get("bo_tham_so_json")
    if chuoi is None or chuoi == "":
        loi("THIEU_BO_THAM_SO")
    if not isinstance(chuoi, str):
        loi("BO_THAM_SO_KHONG_HOP_LE")
    try:
        raw = chuoi.encode("utf-8")
    except UnicodeError:
        loi("BO_THAM_SO_KHONG_HOP_LE")
    if len(raw) > BO_TOI_DA_BYTE:
        loi("VUOT_GIOI_HAN")
    bam = bam_bytes(raw)
    # Băm đúng bytes trước parse, kể cả JSON sai hoặc không canonical.
    if tham_so.get("bam_bo_tham_so") != bam:
        loi("SAI_BAM_BO_THAM_SO")
    try:
        bo = doc_json(chuoi)
        can = {"phien_ban", "module", "loai_hop_dong", "phien_ban_bo", "quy_tac", "cac_dong"}
        if (not isinstance(bo, dict) or not can <= bo.keys()
                or bo.keys() - can - {"bam_tep_goc", "ma_bam_noi_dung"}
                or type(bo["phien_ban"]) is not int or bo["phien_ban"] != 1
                or not all(isinstance(bo[k], str) and MA.fullmatch(bo[k])
                           for k in ("module", "loai_hop_dong", "phien_ban_bo"))
                or not isinstance(bo["cac_dong"], list)):
            raise ValueError("Sai snapshot")
        if "bam_tep_goc" in bo and not (isinstance(bo["bam_tep_goc"], str)
                                        and BAM.fullmatch(bo["bam_tep_goc"])):
            raise ValueError("Sai băm tệp gốc")
        rows = [e1.HEADER] + [_dong_e1(r) for r in bo["cac_dong"]]
        danh_muc = e1.kiem_tra_danh_muc(rows, quy_tac=_quy_tac_e1(bo["quy_tac"]))
        if ([r["ma"] for r in danh_muc.cac_dong] != [r["ma"] for r in bo["cac_dong"]]
                or danh_muc.quy_tac != bo["quy_tac"]
                or ("ma_bam_noi_dung" in bo
                    and bo["ma_bam_noi_dung"] != danh_muc.ma_bam_noi_dung)):
            raise ValueError("Snapshot khác nội dung E1")
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError, UnicodeError):
        loi("BO_THAM_SO_KHONG_HOP_LE")
    if danh_muc.tom_tat["so_dang_dung"] > DONG_DANG_DUNG_TOI_DA:
        loi("VUOT_GIOI_HAN")
    return bo, danh_muc, bam


def chon_tham_so(tham_so, danh_muc):
    try:
        ds = doc_json(tham_so.get("ma_truong_can_trich_json", "[]"))
        if (not isinstance(ds, list) or not all(isinstance(ma, str) for ma in ds)
                or len(ds) != len(set(ds))):
            raise ValueError("Sai danh sách mã")
        theo_ma = {p["ma"]: p for p in danh_muc.tham_so}
        return [theo_ma[ma] for ma in ds] if ds else list(theo_ma.values())
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError, UnicodeError):
        loi("BO_THAM_SO_KHONG_HOP_LE")


def kiem_hoi_them(tham_so):
    try:
        if doc_json(tham_so.get("yeu_cau_them_json", "[]")) != []:
            loi("CAU_HOI_THEM_CHUA_DUYET")
    except (ValueError, TypeError, RecursionError, OverflowError, UnicodeError):
        loi("CAU_HOI_THEM_CHUA_DUYET")
