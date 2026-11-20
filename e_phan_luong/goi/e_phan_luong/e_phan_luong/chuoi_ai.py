"""PL-5A: lập yêu cầu Local và đọc kết quả phân loại, không gọi cổng AI.

Core nối chuan_bi_phan_loai -> ai.hoi_theo_yeu_cau@1 -> phan_luong_sau_ai.
Phong bì theo LOAI-DU-LIEU-RIENG §2.2–2.3; chuyển tiếp theo GIAO-CODEX §2.5.
Mô-đun chỉ xử lý dữ liệu trong RAM; bên ghép chịu trách nhiệm tải/mở tệp,
kiểm bytes/băm và áp kết quả về các dòng qua ánh xạ của lap_tai_lieu.
"""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from decimal import Decimal
import json
import re
import unicodedata

from .loi import loi

TOI_DA_GIA_TRI = 5000
TOI_DA_KY_TU = 2000
TOI_DA_BYTE_CHUYEN_TIEP = 4 * 1024
_BAM = re.compile(r"sha256:[0-9a-fA-F]{64}")
_KHOA_TEP = {"tep_id", "ten", "mime", "kich_thuoc"}
_KHOA_CHUYEN_TIEP = {"phien_ban", "tep_lo", "bam_tep", "khau", "khong_can_ai"}

_SAI_KHUON = "Kết quả AI chưa đúng khuôn; các dòng đang chờ được giữ là chưa phân loại."
_KHONG_CAN_CU = "AI chưa tìm thấy căn cứ phân loại; các dòng đang chờ được giữ là chưa phân loại."
_SAI_CHI_SO = "AI trả chỉ số tài liệu không hợp lệ; mục đó chưa được phân loại."
_SAI_LOAI = "AI trả loại ngoài danh mục; mục đó chưa được phân loại."
_CHUA_DU_CAN_CU = "Một số tài liệu chưa đủ căn cứ để phân loại."
_TRUNG_CHI_SO = "AI trả trùng chỉ số tài liệu; chỉ giữ mục đầu tiên."


def _chu(gia_tri) -> bool:
    return isinstance(gia_tri, str) and bool(gia_tri.strip())


def _json(gia_tri) -> str:
    return json.dumps(gia_tri, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def lap_tai_lieu(ds: Sequence[tuple[int, str]]) -> tuple[list[dict], dict[int, list[int]]]:
    """Khử trùng bằng NFC/khoảng trắng, giữ nguyên nội dung đầu tiên.

    Trần áp cho 5.000 giá trị khác nhau gửi AI, không cắt bớt danh sách.
    Dòng có nội dung gốc quá dài không có trong ánh xạ, kể cả khi chuẩn hóa
    làm nó ngắn lại. Bên ghép đếm số dòng bỏ bằng len(ds) trừ tổng độ dài
    các danh sách trong ánh xạ và giữ các dòng đó là chua_phan_loai.
    """
    tai_lieu, anh_xa, da_gap = [], {}, {}
    for chi_so_dong, noi_dung in ds:
        if type(chi_so_dong) is not int or chi_so_dong < 0 or not isinstance(noi_dung, str):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        if len(noi_dung) > TOI_DA_KY_TU:
            continue
        khoa = " ".join(unicodedata.normalize("NFC", noi_dung).split())
        if khoa not in da_gap:
            if len(tai_lieu) >= TOI_DA_GIA_TRI:
                raise loi("VUOT_GIOI_HAN")
            chi_so = len(tai_lieu)
            da_gap[khoa] = chi_so
            tai_lieu.append({"chi_so": chi_so, "noi_dung": noi_dung})
            anh_xa[chi_so] = []
        anh_xa[da_gap[khoa]].append(chi_so_dong)
    return tai_lieu, anh_xa


def khuon_tra_loi(danh_muc) -> dict:
    """Khuôn đóng; annotation AI-12 xác định các giá trị metadata của AI."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object", "additionalProperties": False,
        "required": ["phan_loai"],
        "properties": {"phan_loai": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["chi_so", "loai", "tin_cay"],
            "properties": {
                "chi_so": {"type": "integer", "minimum": 0,
                           "$comment": "ktt:ai12:metadata"},
                "loai": {"type": "string", "enum": list(danh_muc),
                         "$comment": "ktt:ai12:metadata"},
                "tin_cay": {"type": "number", "minimum": 0, "maximum": 1,
                            "$comment": "ktt:ai12:metadata"},
            },
        }}},
    }


def _kiem_chuyen_tiep(chuyen_tiep, *, ma_qua_tran="CHUOI_KHONG_KHOP") -> dict:
    if not isinstance(chuyen_tiep, dict):
        raise loi("CHUOI_KHONG_KHOP")
    pl = chuyen_tiep.get("phan_luong")
    if not isinstance(pl, dict) or set(pl) != _KHOA_CHUYEN_TIEP:
        raise loi("CHUOI_KHONG_KHOP")
    tep = pl["tep_lo"]
    if (type(pl["phien_ban"]) is not int or pl["phien_ban"] != 1
            or not isinstance(tep, dict) or set(tep) != _KHOA_TEP
            or not all(_chu(tep[k]) for k in ("tep_id", "ten", "mime"))
            or type(tep["kich_thuoc"]) is not int or tep["kich_thuoc"] < 0
            or not isinstance(pl["bam_tep"], str) or not _BAM.fullmatch(pl["bam_tep"])
            or not _chu(pl["khau"]) or len(pl["khau"]) > 40
            or type(pl["khong_can_ai"]) is not bool):
        raise loi("CHUOI_KHONG_KHOP")
    try:
        so_byte = len(_json(chuyen_tiep).encode("utf-8"))
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise loi("CHUOI_KHONG_KHOP") from None
    if so_byte > TOI_DA_BYTE_CHUYEN_TIEP:
        raise loi(ma_qua_tran)
    return pl


def lap_chuyen_tiep(tep_lo: dict, bam_tep: str, khau: str, khong_can_ai: bool) -> dict:
    """Giữ nguyên bốn trường tệp Core trả về; không thay bằng chuỗi tep_id."""
    ct = {"phan_luong": {"phien_ban": 1, "tep_lo": tep_lo, "bam_tep": bam_tep,
                         "khau": khau, "khong_can_ai": khong_can_ai}}
    _kiem_chuyen_tiep(ct, ma_qua_tran="VUOT_GIOI_HAN")
    return deepcopy(ct)


def lap_yeu_cau_ai(tai_lieu, danh_muc, tham_so, chuyen_tiep) -> dict:
    """Lập phong bì cho ai.hoi_theo_yeu_cau@1 (Local), giữ prompt của module."""
    if (not isinstance(tham_so, dict)
            or not all(_chu(tham_so.get(k)) for k in ("ma_prompt", "phien_ban_prompt", "prompt"))):
        raise loi("THAM_SO_KHONG_HOP_LE")
    model = tham_so.get("model_uu_tien")
    if isinstance(model, str) and not model.strip():
        model = None
    if model is not None and not _chu(model):
        raise loi("THAM_SO_KHONG_HOP_LE")
    pl = _kiem_chuyen_tiep(chuyen_tiep, ma_qua_tran="VUOT_GIOI_HAN")
    if pl["khong_can_ai"]:
        van_ban = ""
    else:
        if not isinstance(tai_lieu, list):
            raise loi("DU_LIEU_KHONG_HOP_LE")
        if len(tai_lieu) > TOI_DA_GIA_TRI:
            raise loi("VUOT_GIOI_HAN")
        for i, muc in enumerate(tai_lieu):
            if (not isinstance(muc, dict) or set(muc) != {"chi_so", "noi_dung"}
                    or type(muc["chi_so"]) is not int or muc["chi_so"] != i
                    or not isinstance(muc["noi_dung"], str)
                    or len(muc["noi_dung"]) > TOI_DA_KY_TU):
                raise loi("DU_LIEU_KHONG_HOP_LE")
        van_ban = _json(tai_lieu)
    return {"loai": "yeu_cau_ai", "yeu_cau_ai": {
        "phien_ban": 1,
        **{k: tham_so[k] for k in ("ma_prompt", "phien_ban_prompt", "prompt")},
        "tai_lieu": van_ban, "khuon_tra_loi": khuon_tra_loi(danh_muc),
        "bat_buoc_trich_dan": False, "model_uu_tien": model,
        "chuyen_tiep": deepcopy(chuyen_tiep),
    }}


def kiem_tham_chieu_tep(dau_vao) -> None:
    """Kiểm hình dạng nghiêm như test_pl0_can_core.co_tham_chieu_tep.

    Chỉ nhận đối tượng có khóa tep_id là chuỗi không rỗng, ở bất kỳ độ sâu
    nào, kể cả trong mảng. Không chứng nhận tệp tồn tại/cùng việc/pháp nhân;
    Core phải kiểm các quyền đó khi mo_tep.
    """
    cho, da_gap = [dau_vao], set()
    while cho:
        nut = cho.pop()
        if isinstance(nut, (dict, list)):
            if id(nut) in da_gap:
                continue
            da_gap.add(id(nut))
        if isinstance(nut, dict):
            if _chu(nut.get("tep_id")):
                return
            cho.extend(nut.values())
        elif isinstance(nut, list):
            cho.extend(nut)
    raise loi("CHUOI_KHONG_KHOP")


def doc_chuyen_tiep(phong_bi_tra_loi) -> dict:
    """Đọc khối phan_luong (không phải cả chuyen_tiep) sau khi kiểm hình dạng."""
    if (not isinstance(phong_bi_tra_loi, dict)
            or phong_bi_tra_loi.get("loai") != "tra_loi_ai"
            or not isinstance(phong_bi_tra_loi.get("tra_loi_ai"), dict)):
        raise loi("CHUOI_KHONG_KHOP")
    pl = _kiem_chuyen_tiep(phong_bi_tra_loi["tra_loi_ai"].get("chuyen_tiep"))
    kiem_tham_chieu_tep(phong_bi_tra_loi)
    return deepcopy(pl)


def _diem(gia_tri) -> Decimal | None:
    if type(gia_tri) not in (int, float, Decimal):
        return None
    so = Decimal(str(gia_tri)) if type(gia_tri) is float else Decimal(gia_tri)
    if not so.is_finite() or not 0 <= so <= 1:
        return None
    return so


def doc_tra_loi_ai(phong_bi, *, danh_muc, so_tai_lieu,
                   nguong_tin_cay: Decimal) -> tuple[dict[int, str], list[str]]:
    """Sai chuỗi/nguồn là lỗi; sai khuôn/căn cứ để lại các dòng chưa phân loại.

    Chỉ số trùng giữ mục đầu, kể cả khi mục đầu bị bỏ do enum hoặc căn cứ.
    Cảnh báo là câu cố định; không chép điểm, dữ liệu hay cảnh báo của AI.
    """
    pl = doc_chuyen_tiep(phong_bi)
    ai = phong_bi["tra_loi_ai"]
    if ai.get("nha_cung_cap") != "local":
        raise loi("KHONG_PHAI_LOCAL")
    if (type(so_tai_lieu) is not int or not 0 <= so_tai_lieu <= TOI_DA_GIA_TRI
            or not isinstance(nguong_tin_cay, Decimal)
            or not nguong_tin_cay.is_finite() or not 0 <= nguong_tin_cay <= 1):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if pl["khong_can_ai"]:
        return {}, []
    if ai.get("trang_thai") == "khong_thay_can_cu":
        return {}, [_KHONG_CAN_CU]
    du_lieu = ai.get("du_lieu")
    if (type(ai.get("phien_ban")) is not int or ai["phien_ban"] != 1
            or ai.get("trang_thai") != "co_can_cu"
            or not isinstance(du_lieu, dict) or set(du_lieu) != {"phan_loai"}
            or not isinstance(du_lieu["phan_loai"], list)):
        return {}, [_SAI_KHUON]
    # Kiểm đủ khuôn trước khi nhận mục nào; enum/chỉ số ngoài tập được bỏ
    # riêng theo phiếu. Không coi bool là số nguyên hoặc điểm hợp lệ.
    cac_muc = []
    for muc in du_lieu["phan_loai"]:
        if (not isinstance(muc, dict) or set(muc) != {"chi_so", "loai", "tin_cay"}
                or type(muc["chi_so"]) is not int or not isinstance(muc["loai"], str)
                or (diem := _diem(muc["tin_cay"])) is None):
            return {}, [_SAI_KHUON]
        cac_muc.append((muc["chi_so"], muc["loai"], diem))
    ket_qua, canh_bao, da_gap = {}, [], set()
    for chi_so, loai, diem in cac_muc:
        if chi_so in da_gap:
            cau = _TRUNG_CHI_SO
        else:
            da_gap.add(chi_so)
            if not 0 <= chi_so < so_tai_lieu:
                cau = _SAI_CHI_SO
            elif loai not in danh_muc:
                cau = _SAI_LOAI
            elif diem < nguong_tin_cay:
                cau = _CHUA_DU_CAN_CU
            else:
                ket_qua[chi_so] = loai
                continue
        if cau not in canh_bao:
            canh_bao.append(cau)
    return ket_qua, canh_bao
