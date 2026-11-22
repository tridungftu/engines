"""TS-TX: thao tác thuần cho màn nhúng của module, chưa đăng ký SDK quản trị.

Chỉ nhận dữ liệu trong bộ nhớ; không lưu bộ, không gọi engine hay dịch vụ.
Core cần nối thao tác dự kiến soan_bo_tham_so tới ham_thao_tac.
"""

import base64
import binascii
import re

from kho_tri_thuc_sdk import danh_muc_tham_so as e1
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .tham_so import (BO_TOI_DA_BYTE, MA, _dong_e1, _quy_tac_e1,
                      bam_bytes, doc_bo, json_bytes)


def _loi(truong, thong_bao):
    return {"truong": truong, "thong_bao": thong_bao}


def _van_de(v):
    # Không trả câu E1 có chèn giá trị nhập; chỉ trả vị trí và cách sửa.
    cot = e1.HEADER.index(v.cot) if v.cot in e1.HEADER else None
    if cot is None and isinstance(v.cot, str) and re.fullmatch("[A-J]", v.cot):
        cot = ord(v.cot) - ord("A")
    truong = (f"cac_dong.{v.dong - 2}" if v.dong and v.dong >= 2 else "cac_dong")
    if cot is not None:
        truong += "." + e1.KHOA[cot]
    if v.ma.startswith("QUY_TAC") or v.ma == "SAI_QUY_TAC":
        truong = "quy_tac"
    cau = {
        "SAI_MA": "Mã gồm 2–3 chữ in hoa, dấu - và 2–3 chữ số; ví dụ TT-01.",
        "TRUNG_MA": "Mã trùng; đổi thành mã chưa có trong bảng.",
        "THIEU_MA": "Điền mã tham số, ví dụ TT-01.",
        "THIEU_NHOM": "Điền tên nhóm, ví dụ Thông tin chung.",
        "THIEU_MO_TA": "Điền mô tả cho AI.",
        "MO_TA_QUA_DAI": "Mô tả cho AI tối đa 1.000 ký tự.",
        "TU_KHOA_QUA_DAI": "Mỗi từ khóa tối đa 60 ký tự; ngăn cách bằng dấu ;.",
        "SAI_TU_KHOA": "Chỉ từ khóa tiêu đề được dùng @mo_dau; bỏ ký tự @ khác.",
        "SAI_CO_KHONG": "Chọn Có hoặc Không.",
        "SAI_MUC": "Chọn mức quan trọng từ 0 đến 3.",
        "KHONG_CO_THAM_SO_DUNG": "Bật Dùng cho ít nhất một tham số.",
        "O_CONG_THUC": "Thay công thức Excel bằng giá trị.",
        "O_GOP": "Tách ô gộp và ghi giá trị từng dòng trong Excel.",
        "SAI_QUY_TAC": "Chọn đúng kiểu, điều kiện và mã đối chiếu của quy tắc.",
        "QUY_TAC_MA_KHONG_CO": "Mã trong quy tắc phải có trong bảng tham số.",
        "THIEU_COT": "Excel phải có đủ 10 cột theo mẫu E1, đúng thứ tự.",
        "SAI_COT": "Sắp cột Excel theo đúng thứ tự mẫu E1.",
        "TEP_QUA_LON": "Excel tối đa 2 MiB, nội dung giải nén tối đa 16 MiB.",
        "TEP_CO_MACRO": "Lưu Excel thành .xlsx không macro.",
        "SAI_TEP": "Chọn tệp Excel .xlsx hợp lệ.",
        "KHONG_TU_KHOA": "Chưa có từ khóa; tìm theo mục lục có thể chậm hơn.",
        "NHIEU_THAM_SO": "Bộ có hơn 60 tham số đang dùng; cần kiểm ngân sách AI.",
    }.get(v.ma, "Kiểm tra giá trị và cấu trúc theo mẫu E1.")
    vi_tri = f"Dòng Excel {v.dong}: " if v.dong else ""
    return _loi(truong, vi_tri + cau)


def _ket_qua(bo, dm):
    bo = {**bo, "cac_dong": dm.cac_dong, "quy_tac": dm.quy_tac,
          "ma_bam_noi_dung": dm.ma_bam_noi_dung}
    raw = json_bytes(bo)
    if len(raw) > BO_TOI_DA_BYTE:
        return {"dat": False, "loi": [_loi("cac_dong", "Bộ tham số vượt 64 KiB; giảm nội dung trước khi xuất.")]}
    tham_so = {"bo_tham_so_json": raw.decode("utf-8"), "bam_bo_tham_so": bam_bytes(raw)}
    doc_bo(tham_so)  # Đúng cùng cửa nhận việc, gồm trần 200 tham số đang dùng.
    return {"dat": True, "bo": bo, "tham_so": tham_so, "loi": [],
            "canh_bao": [_van_de(v) for v in dm.canh_bao]}


def ham_thao_tac(tac):
    """tac.dau_vao: lenh doc_bo | nhap_excel | kiem_bo (xem README)."""
    vao = tac.dau_vao
    if not isinstance(vao, dict):
        raise LoiNghiepVu("TX_SOAN_SAI_DAU_VAO", "Dữ liệu trình soạn không hợp lệ.")
    try:
        lenh = vao.get("lenh")
        if lenh == "doc_bo":
            bo, dm, _ = doc_bo(vao.get("tham_so", {}))
            return _ket_qua(bo, dm)
        if lenh not in ("nhap_excel", "kiem_bo"):
            raise ValueError()
        bo = vao.get("bo")
        if not isinstance(bo, dict):
            raise ValueError()
        loi = [_loi(k, "Điền mã gồm chữ, số, dấu gạch dưới, chấm, hai chấm hoặc gạch ngang; tối đa 200 ký tự.")
               for k in ("module", "loai_hop_dong", "phien_ban_bo")
               if not isinstance(bo.get(k), str) or not MA.fullmatch(bo[k])]
        if loi:
            return {"dat": False, "loi": loi}
        if lenh == "nhap_excel":
            chuoi = vao.get("tep_base64")
            if not isinstance(chuoi, str) or len(chuoi) > ((e1.GIOI_HAN_TEP + 2) // 3) * 4:
                return {"dat": False, "loi": [_loi("tep", "Chọn Excel .xlsx tối đa 2 MiB.")]}
            dm = e1.doc_danh_muc(base64.b64decode(chuoi, validate=True))
            bam_goc = "sha256:" + dm.ma_bam
        else:
            if set(bo) - {"phien_ban", "module", "loai_hop_dong", "phien_ban_bo", "cac_dong", "quy_tac", "ma_bam_noi_dung", "bam_tep_goc"}:
                raise ValueError()
            if len(json_bytes(bo)) > BO_TOI_DA_BYTE:
                return {"dat": False, "loi": [_loi("cac_dong", "Bộ tham số vượt 64 KiB; giảm nội dung trước khi xuất.")]}
            dm = e1.kiem_tra_danh_muc([e1.HEADER] + [_dong_e1(r) for r in bo["cac_dong"]],
                                    quy_tac=_quy_tac_e1(bo["quy_tac"]))
            bam_goc = bo.get("bam_tep_goc")
        if dm.tom_tat["so_dang_dung"] > 200:
            return {"dat": False, "loi": [_loi("cac_dong", "Tối đa 200 tham số đang dùng; tắt hoặc tách bộ trước khi xuất.")]}
        out = {"phien_ban": 1, **{k: bo[k] for k in ("module", "loai_hop_dong", "phien_ban_bo")}}
        if bam_goc is not None:
            out["bam_tep_goc"] = bam_goc
        return _ket_qua(out, dm)
    except e1.LoiDanhMuc as exc:
        return {"dat": False, "loi": [_van_de(v) for v in exc.loi]}
    except LoiNghiepVu:
        return {"dat": False, "loi": [_loi("bo", "Bộ tham số hoặc băm không hợp lệ; tải lại bộ đã ghim và kiểm tra giới hạn.")]}
    except (ValueError, TypeError, KeyError, AttributeError, binascii.Error, UnicodeError, RecursionError):
        return {"dat": False, "loi": [_loi("bo", "Dữ liệu không đúng cấu trúc E1; tải lại bộ hoặc chọn Excel hợp lệ.")]}
