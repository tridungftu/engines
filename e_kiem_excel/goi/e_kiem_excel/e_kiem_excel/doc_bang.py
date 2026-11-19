"""Đọc KLGT từ master_hd.py 629–765; không tính lại công thức Excel."""

from decimal import Decimal, localcontext
from hashlib import sha256
from io import BytesIO
import json
import re

import openpyxl
from openpyxl.utils import get_column_letter
from kho_tri_thuc_sdk.engine import LoiNghiepVu

from .nhan_dien import CAU_VUOT_TRAN, TEP_TOI_DA_BYTE
from .chuan_hoa import nfc as _nfc, bo_dau as _bo_dau, num as _num


def _hdr_text(ws, rows, col):
    return " ".join(_bo_dau(ws.cell(r, col).value) for r in rows if ws.cell(r, col).value not in (None, ""))


def tim_bang_chi_tiet(wb_values, kiem_huy=lambda: None):
    """
    Tìm bảng xác định giá trị (KL x đơn giá) trong workbook bất kỳ, dựa vào tiêu đề cột:
    cột 'Tên công việc/tác', 'Đơn vị', 'Đơn giá'; cột bên trái đơn giá là khối lượng,
    bên phải là giá trị; phân biệt HĐ / kỳ trước / kỳ này / lũy kế theo chữ trong tiêu đề.
    """
    best = None
    for ws in wb_values.worksheets:
        kiem_huy()
        if ws.max_row < 5:
            continue
        for r in range(1, min(ws.max_row, 40) + 1):
            kiem_huy()
            cols = {}
            for c in range(1, min(ws.max_column, 40) + 1):
                t = _bo_dau(ws.cell(r, c).value)
                if re.search(r"^ten cong (viec|tac)|^noi dung cong viec|^ten (hang muc|cong viec)", t):
                    cols["ten"] = c
                elif re.search(r"^don gia", t):
                    cols["dg"] = c
            if "ten" not in cols or "dg" not in cols:
                continue
            hdr_rows = range(r, r + 4)
            m = {"ten": cols["ten"], "dg": cols["dg"]}
            for c in range(1, min(ws.max_column, 40) + 1):
                t = _hdr_text(ws, hdr_rows, c)
                # tiêu đề nhóm (vd 'Khối lượng' gộp ô) chỉ nằm ở ô đầu; ghép với ô dưới
                if not t:
                    continue
                if c < cols["ten"] and re.search(r"\bstt\b|\btt\b", t):
                    m.setdefault("stt", c)
                if re.search(r"^don vi|^d\.? ?vi|^dvt", t) and c != cols["ten"]:
                    m.setdefault("dvt", c)
                side = "kl" if c < cols["dg"] else ("gt" if c > cols["dg"] else None)
                if not side or c <= cols["ten"]:
                    continue
                if re.search(r"hop dong", t) and not re.search(r"ky truoc|ky nay", t):
                    m.setdefault(side + "_hd", c)
                elif re.search(r"ky truoc", t):
                    m.setdefault(side + "_kt", c)
                elif re.search(r"luy ke.*ky nay|het ky nay", t):
                    m.setdefault(side + "_lk", c)
                elif re.search(r"ky nay", t):
                    m.setdefault(side + "_kn", c)
            if "dvt" not in m or not any(k in m for k in ("kl_hd", "kl_lk")):
                continue
            # dòng dữ liệu: bắt đầu sau dòng đánh số cột, dừng ở dòng 'cộng'
            r0 = r + 1
            while r0 < r + 6 and not isinstance(_num(ws.cell(r0, m["dg"]).value), Decimal) \
                    and not str(ws.cell(r0, m["ten"]).value or "").strip()[:1].isalpha():
                r0 += 1
            items = []
            for rr in range(r0, ws.max_row + 1):
                kiem_huy()
                name = ws.cell(rr, m["ten"]).value
                nb = _bo_dau(name)
                dvt0 = ws.cell(rr, m["dvt"]).value
                low = _nfc(name).strip().lower()
                if dvt0 in (None, "", 0) and re.match(r"^(cộng|tổng cộng|thuế( gtgt| vat)?|tổng giá trị)(\s|\(|:|$)", low):
                    break  # dòng cộng / thuế cuối bảng (không nhầm với hạng mục 'Cống ...' vì có đơn vị)
                if not name or re.fullmatch(r"[\[\]\-\d\s]+", str(name)):
                    continue
                dvt = ws.cell(rr, m["dvt"]).value
                it = dict(dong=rr, stt=str(ws.cell(rr, m["stt"]).value or "").strip() if "stt" in m else "",
                          ten=_nfc(name).strip(), dvt=_nfc(dvt).strip() if dvt not in (None, 0) else "",
                          don_gia=_num(ws.cell(rr, m["dg"]).value))
                for k in ("kl_hd", "kl_kt", "kl_kn", "kl_lk", "gt_hd", "gt_kt", "gt_kn", "gt_lk"):
                    it[k] = _num(ws.cell(rr, m[k]).value) if k in m else None
                items.append(it)
            n_item = sum(1 for i in items if i["dvt"])
            score = n_item * 10 + len([k for k in m if k.startswith(("kl_", "gt_"))])
            if not best or score > best["score"]:
                best = dict(sheet=ws.title, hdr=r, cols=m, items=items, score=score)
            break
    if not best:
        raise LoiNghiepVu("KHONG_TIM_THAY_BANG", "Không tìm thấy bảng có đủ cột cần đọc trong tệp này.")
    # gán nhóm (dòng không có đơn vị là tiêu đề nhóm)
    grp = []
    for it in best["items"]:
        if not it["dvt"]:
            if re.match(r"^[A-Z]{1,3}\.?$|^[IVX]+\.?$", it["stt"] or "") or not grp:
                grp = [it["ten"]] if re.match(r"^[A-Z]\.?$", it["stt"] or "") or not grp else grp[:1] + [it["ten"]]
            else:
                grp = grp[:1] + [it["ten"]]
        it["nhom"] = " / ".join(grp)
    seen = {}
    for it in best["items"]:
        if it["dvt"]:
            base = khoa(it)
            seen[base] = seen.get(base, 0) + 1
            it["khoa"] = base if seen[base] == 1 else f"{base}#{seen[base]}"
    return best


def khoa(it):
    """Khoá so khớp hạng mục giữa các file: nhóm + tên + đơn vị (bỏ dấu, bỏ khoảng trắng thừa)."""
    return f"{_bo_dau(it.get('nhom', ''))}|{_bo_dau(it['ten'])[:120]}|{_bo_dau(it['dvt'])}"


# ============================================================== tìm số tổng hợp (mọi mẫu)
LABELS = {
    "gt_hd": r"gia tri hop dong( goc| \+ bo sung| \+ plhd)?",
    "gt_lk_kt": r"luy ke thuc hien (den het|het) ky truoc",
    "gt_kn": r"gia tri (thuc hien|hoan thanh) (ky nay|dot nay)",
    "gt_lk": r"luy ke thuc hien (den het|het) ky nay",
    "giu_lai": r"giu lai",
    "thu_hoi_tu": r"hoan tra tam ung|thu hoi (gia tri )?(da )?tam ung",
    "tt_ky_nay": r"gia tri (thanh toan|de nghi thanh toan) ky nay",
}


def tim_so_tong_hop(wb_values, kiem_huy=lambda: None):
    """Quét các sheet tổng hợp tìm số theo nhãn; lấy số đầu tiên bên phải nhãn."""
    found = {}
    for ws in wb_values.worksheets:
        kiem_huy()
        if ws.sheet_state != "visible":
            continue
        for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 80), max_col=min(ws.max_column, 12)):
            kiem_huy()
            for cell in row:
                t = _bo_dau(cell.value) if isinstance(cell.value, str) else ""
                if not t or len(t) > 140:
                    continue
                for k, pat in LABELS.items():
                    if k in found or not re.search(pat, t):
                        continue
                    if k == "gt_hd" and "luy ke" in t:
                        continue
                    for c in range(cell.column + 1, min(ws.max_column, cell.column + 6) + 1):
                        v = ws.cell(cell.row, c).value
                        v = _num(v)
                        if v is not None:
                            found[k] = dict(gia_tri=v, o=f"{ws.title}!{ws.cell(cell.row, c).coordinate}",
                                            nhan=_nfc(cell.value)[:80])
                            break
    return found




def _thap_phan(d):
    if d is None:
        return None
    # Chặn trước format để chuỗi số có số mũ lớn không cấp phát vô hạn.
    if len(d.as_tuple().digits) + abs(d.as_tuple().exponent) > TEP_TOI_DA_BYTE:
        raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_VUOT_TRAN)
    return format(d, "f")


def _tien(d, tien_te):
    return None if d is None else {"so": _thap_phan(d), "tien_te": tien_te}


def _tim_tien_te(wb, bang, kiem_huy):
    """Chỉ nhận mã ghi rõ ở phần đầu bảng hoặc định dạng ô tiền của bảng."""
    ws = wb[bang["sheet"]]
    ma = set()
    for row in ws.iter_rows(max_row=bang["hdr"], max_col=min(ws.max_column, 40)):
        kiem_huy()
        for cell in row:
            t = _nfc(cell.value).strip()
            if t in {"VND", "USD", "EUR", "GBP", "JPY", "CNY", "CHF", "AUD", "CAD",
                     "SGD", "HKD", "KRW", "THB", "TWD", "MYR", "IDR", "INR"}:
                ma.add(t)
            for m in re.finditer(r"(?:đơn vị(?: tiền(?: tệ)?)?|tiền tệ|đvt|currency)\s*[:(\-]?\s*([A-Z]{3})\b", t, re.IGNORECASE):
                code = m.group(1)
                if re.fullmatch(r"[A-Z]{3}", code):
                    ma.add(code)
    for it in bang["items"]:
        kiem_huy()
        if not it["dvt"]:
            continue
        for k, c in bang["cols"].items():
            if k == "dg" or k.startswith("gt_"):
                fmt = ws.cell(it["dong"], c).number_format
                ma.update(re.findall(r"\[\$([A-Z]{3})(?:-[0-9A-Fa-f]+)?\]", fmt))
                ma.update(re.findall(r'"([A-Z]{3})"', fmt))
    # Nhiều mã khác nhau: không tự chọn một đơn vị.
    return next(iter(ma)) if len(ma) == 1 else None


def _dong_json(ws, it, cot, tien_te, seen):
    vi_tri = f"{ws.title}!{it['dong']}"
    canh_bao = []

    def bao(ma, o, cau):
        canh_bao.append({"ma": ma, "o": o, "mo_ta": cau})

    if it["dvt"]:
        base = khoa(it)
        if base in seen:
            bao("TRUNG_KHOA", vi_tri, "Dòng có cùng khóa với một dòng trước đó; đã thêm hậu tố để phân biệt.")
        seen.add(base)
        for k, c in cot.items():
            if k == "dg" or k.startswith(("kl_", "gt_")):
                cell = ws.cell(it["dong"], c)
                if isinstance(cell.value, str) and _num(cell.value) is not None:
                    bao("SO_DANG_CHU", f"{ws.title}!{cell.coordinate}", "Ô số đang được lưu dưới dạng chữ.")
        for ky in ("hd", "kt", "kn", "lk"):
            kl, dg, gt = it["kl_" + ky], it["don_gia"], it["gt_" + ky]
            if kl is None or dg is None or gt is None:
                continue
            with localcontext() as ctx:
                ctx.prec = max(28, len(kl.as_tuple().digits) + len(dg.as_tuple().digits))
                tich = kl * dg
            if gt != tich:
                o = f"{ws.title}!{get_column_letter(cot['gt_' + ky])}{it['dong']}"
                bao("THANH_TIEN_LECH", o, "Thành tiền khác khối lượng nhân đơn giá.")
    dong = {k: it[k] for k in ("stt", "nhom", "ten", "dvt")}
    dong.update(vi_tri=vi_tri, khoa=it.get("khoa"), canh_bao=canh_bao)
    for k in ("kl_hd", "kl_kt", "kl_kn", "kl_lk"):
        dong[k] = _thap_phan(it[k])
    for k in ("don_gia", "gt_hd", "gt_kt", "gt_kn", "gt_lk"):
        dong[k] = _tien(it[k], tien_te)
    return dong


def doc_klgt(raw, tham_so, phien_ban_engine, kiem_huy=lambda: None):
    """Trả trường và JSON trong RAM; cổng SDK chịu trách nhiệm tải tệp ra."""
    khuon = tham_so.get("khuon", "xay_dung_klgt")
    if khuon != "xay_dung_klgt":
        raise LoiNghiepVu("CHUA_LAM", "Khuôn đọc bảng tổng quát chưa được triển khai ở lát EX-4.")
    tien_te = tham_so.get("tien_te", "")
    if not isinstance(tien_te, str) or tien_te and not re.fullmatch(r"[A-Z]{3}", tien_te):
        raise LoiNghiepVu("THAM_SO_KHONG_HOP_LE", "Cài đặt mã tiền tệ phải gồm ba chữ cái in hoa.")
    kiem_huy()
    try:
        wb = openpyxl.load_workbook(BytesIO(raw), data_only=True, keep_vba=False, keep_links=False)
    except Exception:
        raise LoiNghiepVu("TEP_HONG", "Không đọc được tệp Excel này. Vui lòng mở và lưu lại tệp rồi gửi lại.") from None
    try:
        bang = tim_bang_chi_tiet(wb, kiem_huy)
        tong = tim_so_tong_hop(wb, kiem_huy)
        tien_te = tien_te or _tim_tien_te(wb, bang, kiem_huy)
        dong, seen = [], set()
        for it in bang["items"]:
            kiem_huy()
            dong.append(_dong_json(wb[bang["sheet"]], it, bang["cols"], tien_te, seen))
        canh_bao = [cb for d in dong for cb in d["canh_bao"]]
        for v in tong.values():
            sheet, toa_do = v["o"].rsplit("!", 1)
            if isinstance(wb[sheet][toa_do].value, str):
                canh_bao.append({"ma": "SO_DANG_CHU", "o": v["o"], "mo_ta": "Ô số tổng hợp đang được lưu dưới dạng chữ."})
        bam = "sha256:" + sha256(raw).hexdigest()
        chi_tiet = {
            "phien_ban": 1, "phien_ban_engine": phien_ban_engine, "bam_dau_vao": bam,
            "khuon": khuon, "sheet": bang["sheet"], "dong_tieu_de": bang["hdr"],
            "cot": {k: get_column_letter(c) for k, c in bang["cols"].items()},
            "tien_te": tien_te, "dong": dong,
            "tong_hop": {k: {**v, "gia_tri": _tien(v["gia_tri"], tien_te)} for k, v in tong.items()},
            "canh_bao": canh_bao,
        }
        noi_dung = json.dumps(chi_tiet, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(noi_dung) > TEP_TOI_DA_BYTE:
            raise LoiNghiepVu("VUOT_GIOI_HAN", CAU_VUOT_TRAN)
        truong = {
            "sheet": bang["sheet"], "dong_tieu_de": bang["hdr"],
            "so_dong": sum(bool(it["dvt"]) for it in bang["items"]),
            "so_dong_nhom": sum(not it["dvt"] for it in bang["items"]),
            "so_canh_bao": len(canh_bao), "tien_te_chua_ro": tien_te is None,
            "bam_dau_vao": bam, "phien_ban_engine": phien_ban_engine,
        }
        for ten, k in (("gia_tri_hop_dong", "gt_hd"), ("gia_tri_de_nghi", "tt_ky_nay")):
            truong[ten] = _tien(tong[k]["gia_tri"], tien_te) if tien_te and k in tong else None
        kiem_huy()
        return truong, noi_dung
    finally:
        wb.close()
