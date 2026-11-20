"""So từ khóa thuần, chép-sửa từ e_kiem_excel, không import engine nguồn.

Nguồn: e_kiem_excel/goi/e_kiem_excel/e_kiem_excel/bo_nhom.py:
dòng 20–47 (đọc JSON, kiểm từ khóa), 50–93 (so từ khóa),
107–108 (AND/OR và loại trừ), 134–149 (kiểm điều kiện, đếm từ khóa).
Chuẩn hóa từ chuan_hoa.py cùng thư mục, dòng 8–16.
Đổi bo_dau thành chuan, dùng bảng lỗi PL; bỏ vung, kiểm trần từ khóa
theo từng quy tắc như GIAO-CODEX-e_phan_luong §2.3.
"""
from __future__ import annotations

import json
import re
import unicodedata

from .loi import loi

TOI_DA_BYTE = 32 * 1024
TOI_DA_TU_KHOA = 200


def chuan(chu) -> str:
    """NFC, bỏ dấu (kể cả Đ/đ), viết thường và gộp khoảng trắng."""
    chu = unicodedata.normalize("NFC", str(chu or ""))
    chu = chu.replace("đ", "d").replace("Đ", "D")
    chu = unicodedata.normalize("NFD", chu)
    chu = "".join(c for c in chu if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", chu.lower()).strip()


def _khong_trung(cap):
    d = {}
    for k, v in cap:
        if k in d:
            raise loi("THAM_SO_KHONG_HOP_LE")
        d[k] = v
    return d


def _sai_hang(_):
    raise loi("THAM_SO_KHONG_HOP_LE")


def doc_json(chuoi, tran=TOI_DA_BYTE):
    """Đọc cấu hình có trần byte UTF-8; không nhận khóa trùng, NaN/Inf."""
    if not isinstance(chuoi, str):
        raise loi("THAM_SO_KHONG_HOP_LE")
    try:
        if len(chuoi.encode("utf-8")) > tran:
            raise loi("THAM_SO_KHONG_HOP_LE")
        return json.loads(chuoi, object_pairs_hook=_khong_trung,
                          parse_constant=_sai_hang)
    except (ValueError, UnicodeError, RecursionError):
        raise loi("THAM_SO_KHONG_HOP_LE") from None


def kiem_tu_khoa(tu):
    if not isinstance(tu, str):
        raise loi("THAM_SO_KHONG_HOP_LE")
    tu = tu.strip()
    if not tu or not chuan(tu[1:] if tu.startswith("=") else tu):
        raise loi("THAM_SO_KHONG_HOP_LE")
    return tu


def khop_tu_khoa(tu, van_ban) -> bool:
    """Chứa chuỗi; = nguyên từ Unicode; # là >=1 chữ số thập phân.

    Ký tự regex giữ nguyên văn. Bảng trạng thái cho # không backtracking,
    chép-sửa bo_nhom.py dòng 50–93.
    """
    tu = kiem_tu_khoa(tu)
    nguyen_tu = tu.startswith("=")
    tu = chuan(tu[1:] if nguyen_tu else tu)
    van_ban = chuan(van_ban)

    def la_tu(ch):
        return ch.isalnum() or ch == "_"

    if "#" not in tu:
        if not nguyen_tu:
            return tu in van_ban
        i = van_ban.find(tu)
        while i >= 0:
            j = i + len(tu)
            if ((i == 0 or not la_tu(van_ban[i - 1]))
                    and (j == len(van_ban) or not la_tu(van_ban[j]))):
                return True
            i = van_ban.find(tu, i + 1)
        return False
    n = len(van_ban)
    trang_thai = [not nguyen_tu or i == 0 or not la_tu(van_ban[i - 1])
                  for i in range(n + 1)]
    for phan in re.split(r"(#)", tu):
        if not phan:
            continue
        tiep = [False] * (n + 1)
        if phan == "#":
            for i, ch in enumerate(van_ban):
                tiep[i + 1] = ch.isdecimal() and (trang_thai[i] or tiep[i])
        else:
            for i in range(n - len(phan) + 1):
                if trang_thai[i] and van_ban.startswith(phan, i):
                    tiep[i + len(phan)] = True
        trang_thai = tiep
        if not any(trang_thai):
            return False
    return any(dat and (not nguyen_tu or i == n or not la_tu(van_ban[i]))
               for i, dat in enumerate(trang_thai))


def kiem_dieu_kien(dk) -> int:
    """Kiểm cấu trúc một điều kiện; trả số từ khóa để cộng trong quy tắc."""
    if (not isinstance(dk, dict) or "tat_ca" not in dk
            or set(dk) - {"tat_ca", "khong_co"}
            or not isinstance(dk["tat_ca"], list) or not dk["tat_ca"]
            or not isinstance(dk.get("khong_co", []), list)):
        raise loi("THAM_SO_KHONG_HOP_LE")
    if any(not isinstance(ds, list) or not ds for ds in dk["tat_ca"]):
        raise loi("THAM_SO_KHONG_HOP_LE")
    so_tu = 0
    for ds in dk["tat_ca"] + [dk.get("khong_co", [])]:
        for tu in ds:
            kiem_tu_khoa(tu)
            so_tu += 1
    return so_tu


def khop_dieu_kien(dk, van_ban) -> bool:
    """Mọi nhóm tat_ca có một từ khớp và không từ khong_co nào khớp."""
    return (all(any(khop_tu_khoa(tu, van_ban) for tu in ds)
                for ds in dk["tat_ca"])
            and not any(khop_tu_khoa(tu, van_ban)
                        for tu in dk.get("khong_co", [])))
