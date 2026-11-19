"""Đọc bảng theo khuôn cột của module; chỉ dùng RAM và giá trị Excel đã lưu."""

from datetime import date, datetime
from hashlib import sha256
from io import BytesIO
import json
import re

import openpyxl
from openpyxl.utils import get_column_letter
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .chuan_hoa import nfc, num
from .bo_nhom import doc_json, kiem_tu_khoa, khop_tu_khoa
from .doc_bang import _thap_phan, _tien, _tim_tien_te
from .nhan_dien import CAU_VUOT_TRAN, TEP_TOI_DA_BYTE

TRAN_KHUON_BYTE = 32768
TRAN_COT = 30
TRAN_TU_KHOA = 200
CAU_THAM_SO = "Cài đặt khuôn cột chưa đúng hoặc vượt giới hạn. Quản trị viên kiểm tra lại cài đặt của quy trình."


def _sai():
    raise LoiNghiepVu("THAM_SO_KHONG_HOP_LE", CAU_THAM_SO)


def doc_khuon(raw):
    """Khuôn đóng v1; trần 30 cột, tổng 200 từ khóa (kể cả dòng dừng), 32 KiB."""
    if not isinstance(raw, str) or not raw or len(raw) > TRAN_KHUON_BYTE:
        _sai()
    k = doc_json(raw, TRAN_KHUON_BYTE)
    if not isinstance(k, dict) or set(k) != {"phien_ban", "cot", "dong_dung"}:
        _sai()
    if type(k["phien_ban"]) is not int or k["phien_ban"] != 1:
        _sai()
    if not isinstance(k["cot"], list) or not 1 <= len(k["cot"]) <= TRAN_COT:
        _sai()
    ma = set()
    cac_tu = []
    for c in k["cot"]:
        if not isinstance(c, dict) or set(c) != {"ma", "tu_khoa", "bat_buoc", "kieu"}:
            _sai()
        if not isinstance(c["ma"], str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", c["ma"]) or c["ma"] in ma:
            _sai()
        ma.add(c["ma"])
        if type(c["bat_buoc"]) is not bool or c["kieu"] not in ("van_ban", "so", "so_tien", "ngay"):
            _sai()
        if not isinstance(c["tu_khoa"], list) or not c["tu_khoa"]:
            _sai()
        cac_tu.extend(c["tu_khoa"])
    if not any(c["bat_buoc"] for c in k["cot"]) or not isinstance(k["dong_dung"], list):
        _sai()
    cac_tu.extend(k["dong_dung"])
    if len(cac_tu) > TRAN_TU_KHOA:
        _sai()
    # Matcher của bộ nhóm là nơi duy nhất diễn giải cú pháp từ khóa.
    for t in cac_tu:
        if not isinstance(t, str) or not t.strip() or t.strip() == "=":
            _sai()
        kiem_tu_khoa(t)
    return k


def _co(v):
    return v is not None and (not isinstance(v, str) or bool(v.strip()))


def _tim_bang(wb, khuon, kiem_huy):
    best = None
    for ws in wb.worksheets:
        kiem_huy()
        if ws.sheet_state != "visible":
            continue
        # Chỉ trải ô gộp trong vùng dò tiêu đề; không lấp dữ liệu theo chiều ngang.
        gop = {}
        for vung in ws.merged_cells.ranges:
            if vung.min_row > 43:
                continue
            v = ws.cell(vung.min_row, vung.min_col).value
            for r in range(vung.min_row, min(vung.max_row, 43) + 1):
                for c in range(vung.min_col, vung.max_col + 1):
                    gop[r, c] = v
        for r in range(1, min(40, ws.max_row) + 1):
            for cao in range(1, min(4, ws.max_row - r + 1) + 1):
                kiem_huy()
                hdr = {c: " ".join(nfc(gop.get((rr, c), ws.cell(rr, c).value))
                                    for rr in range(r, r + cao)) for c in range(1, ws.max_column + 1)}
                cot = {}
                for c in khuon["cot"]:
                    trung = [i for i, t in hdr.items() if t.strip() and any(khop_tu_khoa(tu, t) for tu in c["tu_khoa"])]
                    if len(trung) > 1 or c["bat_buoc"] and not trung:
                        break
                    if trung:
                        cot[c["ma"]] = trung[0]
                else:
                    if len(set(cot.values())) != len(cot):
                        continue
                    diem = (len(cot), -cao, -r)
                    if best is None or diem > best[0]:
                        best = (diem, ws, r, cao, cot)
    if best is None:
        raise LoiNghiepVu("KHONG_TIM_THAY_BANG", "Không tìm thấy bảng có đủ cột cần đọc trong tệp này.")
    return best[1:]


def _gia_tri(cell, kieu, tien_te, bao):
    v = cell.value
    if not _co(v):
        return None
    if cell.data_type == "e":
        bao("GIA_TRI_SAI_KIEU", cell.coordinate, "Ô đang chứa lỗi Excel; cần kiểm tra lại.")
        return None
    if kieu == "van_ban":
        return nfc(str(v)).strip()
    if kieu in ("so", "so_tien"):
        d = num(v)
        if d is not None:
            if isinstance(v, str):
                bao("SO_DANG_CHU", cell.coordinate, "Ô số đang được lưu dưới dạng chữ.")
            return _thap_phan(d) if kieu == "so" else _tien(d, tien_te)
    elif kieu == "ngay":
        if isinstance(v, datetime):
            return v.date().isoformat()
        if isinstance(v, date):
            return v.isoformat()
        if isinstance(v, str):
            for mau in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(v.strip(), mau).date().isoformat()
                except ValueError:
                    pass
    bao("GIA_TRI_SAI_KIEU", cell.coordinate, "Giá trị ô không đúng kiểu của khuôn cột; cần kiểm tra lại.")
    return None


def doc_tong_quat(raw, tham_so, phien_ban_engine, kiem_huy=lambda: None):
    khuon = doc_khuon(tham_so.get("khuon_cot_json"))
    tien_te = tham_so.get("tien_te", "")
    if not isinstance(tien_te, str) or tien_te and not re.fullmatch(r"[A-Z]{3}", tien_te):
        _sai()
    kiem_huy()
    try:
        wb = openpyxl.load_workbook(BytesIO(raw), data_only=True, keep_vba=False, keep_links=False)
    except Exception:
        raise LoiNghiepVu("TEP_HONG", "Không đọc được tệp Excel này. Vui lòng mở và lưu lại tệp rồi gửi lại.") from None
    try:
        ws, hdr, cao, cot = _tim_bang(wb, khuon, kiem_huy)
        # Tái dùng nhận diện tiền tệ EX-4; ánh xạ các cột tiền sang vai trò gt_*.
        tien_te = tien_te or _tim_tien_te(wb, {
            "sheet": ws.title, "hdr": hdr + cao - 1,
            "cols": {"gt_" + c["ma"]: cot[c["ma"]] for c in khuon["cot"]
                     if c["kieu"] == "so_tien" and c["ma"] in cot},
            "items": ({"dvt": True, "dong": r} for r in range(hdr + cao, ws.max_row + 1)),
        }, kiem_huy)
        dong, canh_bao = [], []
        nhom = ""
        so_nhom = 0
        so_dong = 0
        for r in range(hdr + cao, ws.max_row + 1):
            kiem_huy()
            cells = {k: ws.cell(r, c) for k, c in cot.items()}
            co = {k: c for k, c in cells.items() if _co(c.value)}
            if not co:
                continue
            dau = min(co.values(), key=lambda c: c.column).value
            if isinstance(dau, str) and any(khop_tu_khoa(tu, dau) for tu in khuon["dong_dung"]):
                break
            cb = []

            def bao(ma, o, cau):
                cb.append({"ma": ma, "o": f"{ws.title}!{o}", "mo_ta": cau})

            thieu = any(c["bat_buoc"] and c["ma"] not in co for c in khuon["cot"])
            la_nhom = (thieu and len(co) == 1 and isinstance(dau, str)
                       and any(c["ma"] in co and c["kieu"] == "van_ban" for c in khuon["cot"]))
            if la_nhom:
                nhom = nfc(dau).strip()
                so_nhom += 1
            elif thieu:
                bao("DONG_THIEU_COT_BAT_BUOC", str(r), "Dòng thiếu giá trị ở cột bắt buộc; chưa tính là dòng dữ liệu.")
            else:
                so_dong += 1
            gia_tri = {c["ma"]: _gia_tri(cells[c["ma"]], c["kieu"], tien_te, bao)
                       if c["ma"] in cells and not la_nhom else None for c in khuon["cot"]}
            dong.append({"vi_tri": f"{ws.title}!{r}", "nhom": nhom, "la_nhom": la_nhom,
                         "du_cot_bat_buoc": not thieu, "gia_tri": gia_tri, "canh_bao": cb})
            canh_bao.extend(cb)
        bam = "sha256:" + sha256(raw).hexdigest()
        chi_tiet = {"phien_ban": 1, "phien_ban_engine": phien_ban_engine, "bam_dau_vao": bam,
                    "khuon": "tong_quat", "sheet": ws.title, "dong_tieu_de": hdr,
                    "cot": {k: get_column_letter(c) for k, c in cot.items()},
                    "tien_te": tien_te, "dong": dong, "tong_hop": {}, "canh_bao": canh_bao}
        noi_dung = json.dumps(chi_tiet, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(noi_dung) > TEP_TOI_DA_BYTE:
            raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_VUOT_TRAN)
        truong = {"sheet": ws.title, "dong_tieu_de": hdr, "so_dong": so_dong,
                  "so_dong_nhom": so_nhom, "so_canh_bao": len(canh_bao),
                  "gia_tri_hop_dong": None, "gia_tri_de_nghi": None,
                  "tien_te_chua_ro": tien_te is None, "bam_dau_vao": bam,
                  "phien_ban_engine": phien_ban_engine}
        kiem_huy()
        return truong, noi_dung
    finally:
        wb.close()
