"""TRICH-3b: pipeline cổng chung TRICH-1b + vòng đời SDK/Core TRICH-3a.

Trong phạm vi hai file của lát, các thân hàm được chép nguyên từ nguồn
repo ghim dưới đây: không import tham_so/chay/quy_trinh vì còn dependency
review_goc.quy_trinh -> client riêng. Không nạp động hay sửa globals nguồn.
Giữ thuật toán TRICH-1b, mọi câu hỏi qua AIChung/CongAI; DOCX bằng XML.
Core nhận phản hồi nguồn trước ánh xạ tham_so.v1, giữ retry/ACK/drain.
Readiness contracts=[]; độ chính xác chờ TRICH-4b. Không dọn tệp.
"""

import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import threading
import tempfile
import time
from uuid import UUID
import zipfile

from . import ai_chung, docx
from .ai_chung import AIChung, AILoi, DaDung, CHI_DAN_TRICH, YeuCauAI
from .docx import kiem_docx, read_contract
from ...sdk_core import danh_muc_tham_so, xlsx_mini
from .vendor.review.cau_truc import build_structure, locate, nhan, save, than, vi_tri
from .vendor.review.kiem_tra import (
    check, compare, gan_dieu_khoan, giong_nhau, la_khong_co, la_ok,
    load_key, loose, norm, tim_dap_an,
)
from .vendor.review.logic import kiem_tra_logic
from ...sdk_core.bootstrap import Bootstrap, LoiBootstrap, PROTOCOL, gui_thong_diep
from ...sdk_core.engine import LoiEngine, SDKEngine
from ...sdk_core.ngu_canh import _xoa_loi

NGUON_CHEP = {
    'src/kho_tri_thuc/m4/review_goc/trich_xuat/danh_muc.py':
        'f0796984f7b18a4d0d3389b557a6324f3ad59ca488c29ad3284e11ca97ca2ff2',
    'engines/e_trich_xuat/quy_trinh.py':
        'aa743428b7bc2e28b39429f53787e727379d62b7532df70f9379fed0ebf46dc7',
    # G3-GOI-33: thân đổi nguồn import sang vendor/SDK, thuật toán không đổi
    # (anh_xa_tham_so vẫn được test so AST với bản chép).
    'engines/e_trich_xuat/tham_so.py':
        'b65e7e2159a686dcf16fa1816d10da15571e07d356c50a2ca8a4acfd69fe7e7f',
    'engines/e_trich_xuat/chay.py':
        'e7679e0c0b0e40b9092eca83ff001cb9f201c17ea6ef70f6b4354c015665e98c',
}

NGUON = "src/kho_tri_thuc/m4/review_goc/trich_xuat/quy_trinh.py"
NGUON_SHA256 = "a76e95a55cb7253cc7446ead9e7fd495fb9c3ea457c612259bd062aa27b26264"
PHIEN_BAN_NGUON = "2026-10-15a"

DANH_MUC_ID = "XD"
DANH_MUC_SHA256 = "05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd"
# LHD-E2 / QD-TAM-20261106-04: giữ đường catalog legacy của engine,
# không suy từ xlsx_mini.__file__ vì bộ đọc nay thuộc SDK.
DANH_MUC_THAM_SO = (Path(__file__).resolve().parents[2] / "src" / "kho_tri_thuc"
                    / "m4" / "review_goc" / "trich_xuat" / "DANH_MUC_THAM_SO.xlsx")


# Các hàm thuần dưới đây chép nguyên từ danh_muc.py, SHA trong NGUON_CHEP.
# Không import danh_muc/cau_hinh: Core loại biến home trước bootstrap/readiness.
def _split(s):
    return [x.strip().lower() for x in re.split(r"[;\n]", s or "") if x.strip()]


def _muc(v, ma=""):
    try:
        m = int(float(str(v).strip()))
        return min(3, max(0, m))
    except ValueError:
        return 0 if ma.startswith("TC-") else 2


def ten_ngan(mo_ta):
    return re.split(r"[(:;—]", mo_ta)[0].strip()[:60]


def to_param(ma, nhom, mo_ta, tk="", bk="", muc=None, bat_buoc="", loai_tru="", luon_cloud=False):
    """Một dòng danh mục → dict tham số dùng trong quy trình."""
    def kws(x):
        return _split(x) if isinstance(x, str) else [str(k).strip().lower() for k in (x or []) if str(k).strip()]
    ma = str(ma).strip()
    return {"ma": ma, "nhom": (nhom or "").strip() or "Khác", "mo_ta": str(mo_ta).strip(), "ten": ten_ngan(str(mo_ta)),
            "tieu_de_kws": kws(tk), "noi_dung_kws": kws(bk), "muc": _muc(muc if muc is not None else "", ma),
            "bat_buoc": kws(bat_buoc), "loai_tru": kws(loai_tru), "luon_cloud": bool(luon_cloud)}


# Thứ tự mã từ MAC_DINH và tập giá trị KHONG của cùng nguồn ghim ở trên.
_MA_DANH_MUC = (
    'TC-01', 'TC-02', 'TC-03', 'TC-04', 'TC-05', 'TC-06', 'TC-07', 'TC-08', 'TC-09',
    'TT-01', 'TT-02', 'TT-03', 'TT-04', 'TT-05', 'TT-10', 'TT-11', 'TT-12', 'TT-20',
    'TT-21', 'TT-22', 'TT-30', 'TT-31', 'TT-32', 'TT-33', 'TT-40', 'TT-41', 'TT-42',
    'TT-50', 'TT-51', 'TT-52', 'TT-53', 'TT-54', 'TT-55', 'TT-56', 'TT-60', 'TT-61',
    'TT-62',
)
KHONG = ("không", "khong", "no", "0", "x", "false")


def danh_muc_xd():
    """Chỉ đọc XLSX ghim đủ 10 cột; giữ chuyển đổi tham số thuần của nguồn."""
    path = DANH_MUC_THAM_SO
    if hashlib.sha256(path.read_bytes()).hexdigest() != DANH_MUC_SHA256:
        raise ValueError("TRICH_DANH_MUC_SAI_HASH")
    # Hash cố định cả header, số cột và dữ liệu; không tạo/ghi đè catalog.
    params, seen = [], set()
    for row in xlsx_mini.read_xlsx(path)[1:]:
        ma, nhom, mo_ta, tk, bk, dung, muc, bat_buoc, loai_tru, luon_cloud = (
            str(value).strip() for value in row)
        if not ma or not mo_ta or dung.lower() in KHONG or ma in seen:
            continue
        seen.add(ma)
        params.append(to_param(ma, nhom, mo_ta, tk, bk, muc, bat_buoc, loai_tru,
            luon_cloud.lower() in ("có", "co", "x", "1", "yes", "true")))
    if tuple(p["ma"] for p in params) != _MA_DANH_MUC or len(params) != 37:
        raise ValueError("TRICH_DANH_MUC_SAI_37_MA")
    return params


def anh_xa_tham_so(phan_hoi, *, tep_id, phan_hoi_nguon_tep_id, van_ban,
                   loai_hop_dong, danh_muc_id, danh_muc_sha256, revision=1, params=None):
    """Ánh xạ phản hồi đã lưu, không sửa phản hồi và không tự đoán tiền/ngày.

    Chưa có kiểu nghiệp vụ được catalog quy định: giữ giá trị xác định dưới
    kiểu van_ban; thiếu giá trị/dẫn chứng kiểm được thành chua_ro. Không dùng
    vi_tri_do_duoc (vị trí ứng viên) thay dẫn chứng. Core kiểm quyền các ID.
    """
    if params is None:
        if (loai_hop_dong, danh_muc_id, danh_muc_sha256) != ("XD", DANH_MUC_ID, DANH_MUC_SHA256):
            raise ValueError("TRICH_DANH_MUC_KHONG_HO_TRO")
    tep_uuids = []
    for value in (tep_id, phan_hoi_nguon_tep_id):
        if not isinstance(value, str):
            raise ValueError("TRICH_TEP_ID_SAI")
        try:
            parsed = UUID(value)
        except ValueError as exc:
            raise ValueError("TRICH_TEP_ID_SAI") from exc
        if str(parsed) != value.lower():
            raise ValueError("TRICH_TEP_ID_SAI")
        tep_uuids.append(parsed)
    if tep_uuids[0] == tep_uuids[1]:
        raise ValueError("TRICH_PHAN_HOI_PHAI_LA_TEP_RIENG")
    if type(revision) is not int or revision < 1:
        raise ValueError("TRICH_REVISION_SAI")
    params = danh_muc_xd() if params is None else params
    allowed = {p["ma"] for p in params}
    by_ma = {}
    for row in phan_hoi["bang"]:
        ma = row["ma"]
        if ma not in allowed or ma in by_ma:
            raise ValueError("TRICH_MA_LA_HOAC_TRUNG")
        by_ma[ma] = row

    result = []
    for p in params:
        row = by_ma.get(p["ma"], {})
        value = row.get("gia_tri")
        if value is not None and not isinstance(value, str):
            raise ValueError("TRICH_GIA_TRI_NGUON_SAI_KIEU")
        quote = row.get("trich_dan") or ""
        locator = row.get("dieu_khoan") or row.get("row_id") or ""
        warnings = [f"{key}: {row[key]}" for key in
                    ("ghi_chu", "kiem_tra", "vi_tri_do_duoc") if row.get(key)]
        evidence = []
        if quote.strip() and locator.strip() and norm(quote) in norm(van_ban):
            evidence = [{"vi_tri": {"tep_id": tep_id, "dinh_vi": locator}, "trich_dan": quote}]
        reason = None
        if value is None or not value.strip() or la_khong_co(value):
            reason = "Chưa xác định" if not value else value
        elif not evidence:
            reason = "Chưa có dẫn chứng kiểm được"
        typed = {"kieu": "chua_ro", "ly_do": reason} if reason else {"kieu": "van_ban", "gia_tri": value}
        if reason:
            warnings.append(reason)
        result.append({"ma": p["ma"], "ten": p["ten"], "gia_tri": typed,
                       "nguyen_van": value, "dan_chung": evidence,
                       "can_soat": bool(reason) or not la_ok(row.get("kiem_tra", "")),
                       "canh_bao": warnings})
    return {"contract": "tham_so.v1", "phien_ban": "1.0.0", "revision": revision,
            "nguon_tep_ids": [tep_id], "loai_hop_dong": loai_hop_dong,
            "danh_muc_id": danh_muc_id, "danh_muc_sha256": danh_muc_sha256,
            "phan_hoi_nguon_tep_id": phan_hoi_nguon_tep_id, "tham_so": result}


GROUP_MAX = 8
MAX_CTX_CHARS = 14000
MAX_MUC_LUC_CHARS = 40000
BUOC = ["Đọc file", "Tách Điều/Khoản", "Dò vị trí tham số", "Hỏi Local AI", "Tự kiểm tra trích dẫn",
        "Rà lại ô vàng", "Kiểm tra logic", "Kiểm tra chéo cloud", "Xuất kết quả"]
TRANG_THAI = ("Chưa xác nhận", "Đã xác nhận", "Đã sửa tay")


def ten_an_toan(name, toi_da=60):
    """Tên thư mục/file ngắn, hợp lệ trên Windows (đường dẫn Windows tối đa 260 ký tự)."""
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    return (s[:toi_da].rstrip(" .") or "hop_dong")


def build_prompt(params, rows_by_id, row_ids, used=None, max_chars=MAX_CTX_CHARS):
    ds = "\n".join(f"- {p['ma']} | {p['mo_ta']}" for p in params)
    blocks, total = [], 0
    for rid in row_ids:
        r = rows_by_id[rid]
        b = f"[{nhan(r)}]\n{than(r)}"
        if total + len(b) > max_chars and blocks:
            continue
        if len(b) > max_chars:                      # một Khoản dài hơn giới hạn → cắt (đã cảnh báo ở phiếu đầu vào)
            b = b[:max_chars]
        blocks.append(b)
        total += len(b)
        if used is not None:
            used.append(r)
    names = tuple(name for p in params
                  for name in (p["ma"], p["ma"] + ".don_vi", p["ma"] + ".ghi_chu"))
    return YeuCauAI("BOC_TACH_HOP_DONG", "\n\n".join(blocks),
                    CHI_DAN_TRICH + "\nTHAM SỐ:\n" + ds, names)



def chia_doan(rows, max_chars=MAX_CTX_CHARS):
    """Chia TOÀN BỘ HĐ thành các đoạn ≤ max_chars ký tự → list danh sách ID."""
    chunks, cur, n = [], [], 0
    for r in rows:
        size = len(nhan(r)) + len(than(r)) + 4
        if cur and n + size > max_chars:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(r["id"])
        n += size
    if cur:
        chunks.append(cur)
    return chunks


def ghep_kiem_tra(ck, logic):
    """Kết quả tự kiểm + lỗi logic → nội dung cột Kiểm tra."""
    if not logic:
        return ck
    return ("KIỂM TRA: " + "; ".join(logic)) if la_ok(ck) else (ck + " | " + "; ".join(logic))


def _co_gia_tri(it):
    v = ((it or {}).get("gia_tri") or "").strip().lower()
    return bool(v) and not v.startswith(("không quy định", "không tìm thấy"))


class TrichXuat:
    def __init__(self, *, cong_ai, out_dir, ra_lai=True, cloud=None,
                 tien_do=None, ghi_log=None, dung=None, thu_muc_dap_an=None, rng=None,
                 params=None, loai_hop_dong="XD", ten_loai="Hợp đồng xây dựng"):
        if cloud is not None:
            raise ValueError("TRICH_CLOUD_BI_CHAN")
        self.params = danh_muc_xd() if params is None else params
        self.ai = AIChung(cong_ai, cloud=None, dung=dung,
                          loai_hop_dong=loai_hop_dong, ten_loai=ten_loai)
        self.out_dir = os.fspath(out_dir)
        self.ra_lai_bat = ra_lai
        self.cloud = None
        self._tien_do = tien_do or (lambda *a: None)
        self.ghi_log = ghi_log or (lambda m: None)
        self.dung = dung
        self.thu_muc_dap_an = thu_muc_dap_an
        self.rng = rng
        self.ung_vien = {}

    def ocr_pdf(self, *args, **kwargs):
        raise ValueError("TRICH_OCR_BI_CHAN: PDF phải qua e_ocr")

    def tien_do(self, buoc, mo_ta, pct):
        if self.dung is not None and self.dung.is_set():
            raise DaDung()
        self._tien_do(buoc, mo_ta, pct)

    def ai_tim_vi_tri(self, params, rows):
        """Giữ chia mục lục của nguồn, thay schema riêng bằng DTO cổng chung."""
        dong = [(r["id"], f"{r['id']} | {nhan(r)} | "
                 + r["noi_dung"][:120].replace(chr(10), " ")) for r in rows]
        phan, cur, n = [], [], 0
        for rid, d in dong:
            if cur and n + len(d) > MAX_MUC_LUC_CHARS:
                phan.append(cur)
                cur, n = [], 0
            cur.append((rid, d))
            n += len(d) + 1
        if cur:
            phan.append(cur)
        found = {}
        for ph in phan:
            data = self.ai.tim_vi_tri(params, "\n".join(d for _, d in ph),
                                      {rid for rid, _ in ph})
            for ma, ids in data.items():
                found.setdefault(ma, [])
                found[ma] += [rid for rid in ids if rid not in found[ma]]
        return {ma: ids[:3] for ma, ids in found.items()}

    # ---------------------------------------------------------------- bước 6: rà lại toàn HĐ
    def ra_lai(self, rows, rows_by_id, loc_by, results, sent, full_norm, full_loose):
        """Tham số chưa chắc sau lượt 1 → quét TOÀN BỘ HĐ theo đoạn, chỉ hỏi các tham số đó. Không 'thấy là bỏ':
        giữ mọi ứng viên qua được kiểm tra nguyên văn; lượt 1 đã có giá trị → lượt 2 chỉ XÁC NHẬN.
        ≥2 giá trị khác nhau cùng hợp lệ → vàng, liệt kê. Trả số lỗi AI."""
        def chac(it, ma):
            if not it or (it.get("gia_tri") or "") in ("", "Không tìm thấy trong HĐ"):
                return False
            return la_ok(check(it, full_norm, full_loose, sent.get(ma)))
        can = [p for p in self.params if not chac(results.get(p["ma"]), p["ma"])]
        if not can:
            self.ghi_log("  rà lại: không có ô vàng")
            return 0
        chunks = chia_doan(rows)
        batches = [can[i:i + GROUP_MAX] for i in range(0, len(can), GROUP_MAX)]
        total, k, n_err, t1 = len(chunks) * len(batches), 0, 0, time.time()
        cands = {p["ma"]: [] for p in can}
        self.ghi_log(f"  rà lại {len(can)} tham số × {len(chunks)} đoạn: {', '.join(p['ma'] for p in can)}")
        for ci, ids in enumerate(chunks):
            for b in batches:
                self.tien_do(5, f"Rà lại toàn HĐ: {len(can)} ô vàng — đoạn {ci + 1}/{len(chunks)}",
                             0.70 + 0.15 * k / max(1, total))
                k += 1
                used = []
                prompt = build_prompt(b, rows_by_id, ids, used)
                try:
                    items, _, _ = self.ai.hoi_trich(prompt, f"rà lại đoạn {ci + 1}")
                except AILoi as e:
                    n_err += 1
                    self.ghi_log(f"  LỖI rà lại đoạn {ci + 1}: {e}")
                    continue
                for it in items:
                    ma = (it.get("ma") or "").strip()
                    v = (it.get("gia_tri") or "").strip()
                    if ma not in cands or not v or la_khong_co(v):
                        continue
                    gan_dieu_khoan(it, used)
                    cands[ma].append((it, used, la_ok(check(it, full_norm, full_loose, used))))
                    if it.get("_row") and it["_row"] not in self.ung_vien.setdefault(ma, []):
                        self.ung_vien[ma].append(it["_row"])      # đoạn ứng viên → gửi kèm khi kiểm tra chéo cloud
        for p in can:
            ma = p["ma"]
            old = results.get(ma) or {"ma": ma, "gia_tri": ""}
            oks = [c for c in cands[ma] if c[2]]
            khac = []
            for it, _, _ in oks:
                if all(not giong_nhau(it["gia_tri"], x) for x in khac):
                    khac.append(it["gia_tri"])
            pref = set(loc_by[ma]["row_ids"])

            def tot(cs):
                return next((c for c in cs if c[0].get("_row") in pref), cs[0])

            def note(it, x):
                return "; ".join(y for y in ((it.get("ghi_chu") or "").strip(), x) if y)
            if _co_gia_tri(old):
                giong = [c for c in oks if giong_nhau(old["gia_tri"], c[0]["gia_tri"])]
                if giong:
                    best = tot(giong)
                    it = dict(best[0])
                    it["ghi_chu"] = note(it, "rà lại toàn HĐ: xác nhận")
                    results[ma], sent[ma] = it, best[1]
                else:
                    it = dict(old)
                    if oks:
                        it["_nhieu"] = " | ".join([old["gia_tri"]] + khac[:3])
                    it["ghi_chu"] = note(it, "đã rà toàn HĐ: không xác nhận được giá trị lượt 1")
                    results[ma] = it
            elif oks:
                best = tot(oks)
                it = dict(best[0])
                it["ghi_chu"] = note(it, "rà lại toàn HĐ")
                if len(khac) > 1:
                    it["_nhieu"] = " | ".join(khac[:4])
                elif best[0].get("_row") not in pref:
                    it["_xac_nhan"] = it.get("dieu_khoan", "")
                results[ma], sent[ma] = it, best[1]
            else:
                it = dict(old)
                it["ghi_chu"] = note(it, "đã rà toàn HĐ: không thấy giá trị chắc chắn")
                results[ma] = it
        n_fix = sum(1 for p in can if chac(results.get(p["ma"]), p["ma"]))
        self.ghi_log(f"  rà lại xong: {n_fix}/{len(can)} chắc chắn | {total} lần gọi | {time.time() - t1:.1f}s")
        return n_err

    # ---------------------------------------------------------------- một hợp đồng
    def xu_ly(self, path):
        path = kiem_docx(path)
        if self.cloud is not None or self.ai.la_cloud is not False:
            raise ValueError("TRICH_CLOUD_BI_CHAN")
        if not isinstance(self.ai, AIChung):
            raise TypeError("TRICH_CAN_AI_CHUNG")
        phan_hoi0 = len(self.ai.phan_hoi)
        t0 = time.time()
        file = os.path.basename(path)
        name = os.path.splitext(file)[0]
        ten = ten_an_toan(name)
        out = os.path.join(self.out_dir, ten)
        os.makedirs(out, exist_ok=True)
        dung_ai = self.ai is not None
        la_cloud = bool(getattr(self.ai, "la_cloud", False))     # Claude thay Local AI: che định danh, không gửi mở đầu
        ten_ai = getattr(self.ai, "ten", "Local AI") if dung_ai else "Local AI"
        n_err = 0
        self.ghi_log(f"HĐ {file}")
        self.ung_vien = {}

        # 1. đọc file
        self.tien_do(0, "Đọc DOCX bằng XML Python", 0.01)
        info = read_contract(path)
        rep = info["report"]
        self.ghi_log(f"  đọc: {rep['words']:,} từ | {rep['articles']} Điều | {len(rep['warnings'])} cảnh báo")

        # 2. tách Điều/Khoản
        self.tien_do(1, f"Tách Điều/Khoản: {rep['words']:,} từ, {rep['articles']} Điều", 0.04)
        rows = build_structure(info)
        rows_by_id = {r["id"]: r for r in rows}
        # 3. dò vị trí
        self.tien_do(2, f"Dò vị trí {len(self.params)} tham số theo từ khoá", 0.06)
        loc = locate(rows, self.params)
        loc_by = {x["ma"]: x for x in loc}
        missing = [p for p in self.params if not loc_by[p["ma"]]["row_ids"]]
        if missing and dung_ai:
            self.tien_do(2, f"{ten_ai} tìm vị trí {len(missing)} tham số không khớp từ khoá (qua mục lục)", 0.08)
            try:
                found = self.ai_tim_vi_tri(missing, [r for r in rows if r.get("dieu") != "0"] if la_cloud else rows)
            except AILoi as e:
                n_err += 1
                self.ghi_log(f"  LỖI tìm vị trí: {e}")
                found = {}
            for p in missing:
                ids = found.get(p["ma"], [])
                loc_by[p["ma"]]["row_ids"] = ids
                loc_by[p["ma"]]["vi_tri"] = [vi_tri(rows_by_id[i]) for i in ids]
                loc_by[p["ma"]]["tu_khoa"] += " | vị trí do AI tìm qua mục lục"
        save(os.path.join(out, ten), info, rows, loc)
        full_norm, full_loose = norm(info["text"]), loose(info["text"])

        # 4. hỏi AI theo nhóm
        groups = []
        for p in self.params:
            if not groups or groups[-1][0] != p["nhom"] or len(groups[-1][1]) >= GROUP_MAX:
                groups.append((p["nhom"], []))
            groups[-1][1].append(p)
        results, sent = {}, {}
        for gi, (grp, ps) in enumerate(groups):
            ids = []
            for rank in range(3):
                for p in ps:
                    r = loc_by[p["ma"]]["row_ids"]
                    if len(r) > rank and r[rank] not in ids:
                        ids.append(r[rank])
            co_vi_tri = lambda p: bool(loc_by[p["ma"]]["row_ids"])
            todo = [p for p in ps if co_vi_tri(p)]
            for p in ps:
                if not loc_by[p["ma"]]["row_ids"]:
                    results[p["ma"]] = {"ma": p["ma"], "gia_tri": "Không tìm thấy trong HĐ" if dung_ai else "",
                                        "ghi_chu": "Không xác định được vị trí"}
            if not todo:
                continue
            used = []
            prompt = build_prompt(todo, rows_by_id, ids, used)
            for p in todo:
                sent[p["ma"]] = used
            if not dung_ai:
                for p in todo:
                    results[p["ma"]] = {"ma": p["ma"], "gia_tri": "", "ghi_chu": "Chưa chạy AI — xem sheet Doan_lien_quan"}
                continue
            t1 = time.time()
            self.tien_do(3, f"Hỏi {ten_ai}: nhóm «{grp}» ({gi + 1}/{len(groups)}) — {len(todo)} tham số, {len(used)} đoạn",
                         0.10 + 0.55 * gi / len(groups))
            try:
                items, pi, po = self.ai.hoi_trich(prompt, f"nhóm {grp}")
            except AILoi as e:
                n_err += 1
                self.ghi_log(f"  LỖI nhóm {grp}: {e}")
                items, pi, po = [], 0, 0
            self.ghi_log(f"  nhóm {grp} | {len(todo)} tham số | {len(used)} đoạn | token {pi:,}/{po:,} | "
                         f"{time.time() - t1:.1f}s")
            got = {str(it.get("ma", "")).strip(): it for it in items}
            for p in todo:
                results[p["ma"]] = got.get(p["ma"], {"ma": p["ma"], "gia_tri": "", "ghi_chu": "AI không trả về"})

        # 5. tự kiểm: Điều/Khoản suy từ trích dẫn
        self.tien_do(4, "Tự kiểm tra trích dẫn và số liệu", 0.66)
        if dung_ai:
            for ma, it in results.items():
                gan_dieu_khoan(it, sent.get(ma))

        # 6. rà lại
        if dung_ai and self.ra_lai_bat and not la_cloud:     # rà lại = đọc cả HĐ → không làm khi dùng Claude
            n_err += self.ra_lai(rows, rows_by_id, loc_by, results, sent, full_norm, full_loose)

        # 7. logic
        self.tien_do(6, "Kiểm tra logic L1–L5", 0.86)
        logic = kiem_tra_logic(results, self.params, rows_by_id) if dung_ai else {}

        bang = []
        for p in self.params:
            it = results.get(p["ma"], {}) or {}
            if not dung_ai:
                ck = "CHƯA CHẠY AI" if loc_by[p["ma"]]["row_ids"] else "CHƯA CHẠY AI — chưa có vị trí"
            elif it.get("gia_tri") == "Không tìm thấy trong HĐ":
                ck = "KIỂM TRA: không tìm thấy vị trí"
            else:
                ck = check(it, full_norm, full_loose, sent.get(p["ma"]))
                if it.get("_nhieu"):
                    ck = "KIỂM TRA: nhiều giá trị khác nhau trong HĐ: " + it["_nhieu"]
                elif la_ok(ck) and it.get("_xac_nhan") is not None:
                    ck = f"KIỂM TRA: chỉ tìm thấy khi rà lại toàn HĐ ({it['_xac_nhan']}) — cần xác nhận"
            lg = logic.get(p["ma"], [])
            bang.append({"ma": p["ma"], "nhom": p["nhom"], "tham_so": p["ten"], "mo_ta": p["mo_ta"], "muc": p["muc"],
                         "gia_tri": it.get("gia_tri", ""), "don_vi": it.get("don_vi", ""),
                         "dieu_khoan": it.get("dieu_khoan", ""), "trich_dan": it.get("trich_dan", ""),
                         "ghi_chu": it.get("ghi_chu", ""), "kiem_tra": ghep_kiem_tra(ck, lg), "kiem_tra_tu": ck,
                         "logic": lg, "nguon": "Local", "trang_thai": TRANG_THAI[0], "row_id": it.get("_row", ""),
                         "vi_tri_do_duoc": "; ".join(loc_by[p["ma"]]["vi_tri"]), "lich_su": []})

        # 8. Cloud luôn tắt ở lát này, không gọi bộ kiểm chéo nguồn.
        tom_cloud = {"bat": False}

        for d in bang:                       # giá trị máy trích (sau cloud) — luôn giữ lại khi người soát sửa
            d.update(gia_tri_ai=d["gia_tri"], da_xac_nhan=False, da_sua=False)

        # so đáp án (nếu có)
        key = load_key(tim_dap_an(name, self.thu_muc_dap_an)) if dung_ai else None
        n_key = n_keyed = 0
        if key:
            for d in bang:
                if d["ma"] in key:
                    n_keyed += 1
                    d["dap_an"] = key[d["ma"]]
                    d["so_voi_dap_an"] = compare(key[d["ma"]], d["gia_tri"])
                    n_key += d["so_voi_dap_an"] == "ĐÚNG"

        # 9. xuất
        self.tien_do(8, "Ghi Excel / JSON", 0.97)
        doan = {}
        if not dung_ai:
            for p in self.params:
                for rid in loc_by[p["ma"]]["row_ids"]:
                    r = rows_by_id[rid]
                    doan.setdefault(p["ma"], []).append({"vi_tri": vi_tri(r), "noi_dung": than(r)[:3000]})
        n_ok = sum(1 for d in bang if la_ok(d["kiem_tra"]))
        dt = time.time() - t0
        kq = {
            "hop_dong": file, "ten": ten, "che_do": "AI" if dung_ai else "chua_chay_AI",
            "model": self.ai.model if dung_ai else None, "may_ai": self.ai.url if dung_ai else None,
            "tao_luc": datetime.datetime.now().isoformat(timespec="seconds"),
            "tuy_chon": {"ra_lai": bool(self.ra_lai_bat and dung_ai and not la_cloud),
                         "cloud": bool(self.cloud and dung_ai and not la_cloud), "nguon_ai": ten_ai if dung_ai else "",
                         "gui_ra_ngoai": getattr(self.ai, "nhat_ky", "") if la_cloud else ""},
            "tom_tat": {"so_tham_so": len(bang), "so_ok": n_ok, "so_vang": len(bang) - n_ok,
                        "dung_dap_an": f"{n_key}/{n_keyed}" if key else "",
                        # Số 0 tương thích bộ xuất nguồn, không phải phép đo token.
                        "token_vao": 0, "token_ra": 0, "token_da_do": False,
                        "thoi_gian_giay": round(dt), "loi_ai": n_err, "cloud": tom_cloud},
            "phieu_kiem_tra": rep, "bang": bang, "doan_lien_quan": doan,
            "phan_hoi_ai": self.ai.phan_hoi[phan_hoi0:],
        }
        from .vendor.review.xuat import ghi_ket_qua_hd
        kq["tom_tat"]["so_can_xem"] = sum(1 for d in bang if not la_ok(d["kiem_tra"]))
        kq["tom_tat"]["so_da_xac_nhan"] = 0
        ghi_ket_qua_hd(kq, out)
        self.ghi_log(f"  xong {file} | {n_ok}/{len(bang)} OK" + (f" | đáp án {n_key}/{n_keyed}" if key else "")
                     + f" | {dt:.0f}s | lỗi AI: {n_err}")
        return kq


PHIEN_BAN = "0.1.0-demo.1"

def _ban_giao(sdk, value, *, ten, metadata):
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
    with io.BytesIO(raw) as luong:
        while True:
            luong.seek(0)
            try:
                return sdk.ghi_ket_qua(luong=luong, ten=ten,
                    du_lieu=metadata['du_lieu_ket_qua'],
                    revision_tep_truoc=metadata['revision_tep_truoc'])
            except LoiEngine as exc:
                # Core có thể đã đọc hết trước khi mất ACK; không trích lại.
                _xoa_loi(exc)
            time.sleep(0.1)


def xu_ly_viec(sdk, *, backend):
    if not isinstance(sdk, SDKEngine):
        raise TypeError('Cần SDKEngine do Core cấp')
    dau_vao = sdk.doc_dau_vao()
    phan_hoi, van_ban = backend.xu_ly(dau_vao)
    ack = _ban_giao(sdk, phan_hoi, ten='phan-hoi-nguon.json',
                    metadata=dau_vao['phan_hoi'])
    ket_qua = anh_xa_tham_so(phan_hoi, tep_id=dau_vao['tep_id'],
        phan_hoi_nguon_tep_id=ack['tep_id'], van_ban=van_ban,
        loai_hop_dong=dau_vao['loai_hop_dong'],
        danh_muc_id=dau_vao['danh_muc_id'],
        danh_muc_sha256=dau_vao['danh_muc_sha256'])
    return _ban_giao(sdk, ket_qua, ten='tham-so.json', metadata=dau_vao['tham_so'])


class _VongNhan:
    """Một worker tuần tự; drain chờ xử lý và cả hai ACK của Core."""

    def __init__(self, bootstrap, nhan_viec, backend):
        self.bootstrap, self.nhan_viec, self.backend = bootstrap, nhan_viec, backend
        self.khoa = threading.Lock()
        self.dung = self.loi = False
        self._giu_khi_loi = threading.Event()
        self.worker = threading.Thread(target=self._chay, name='trich-demo')

    def bat_dau(self):
        self.bootstrap.socket.settimeout(0.1)
        self.worker.start()

    def _chay(self):
        try:
            while True:
                with self.khoa:
                    if self.dung:
                        return
                try:
                    conn, _ = self.bootstrap.accept()
                except socket.timeout:
                    continue
                except LoiBootstrap as exc:
                    if exc.ma == 'CHUA_CO_QUYEN_ACCEPT':
                        return
                    raise
                with conn:
                    with self.khoa:
                        if self.dung:
                            return
                        # Việc đăng ký trước ngừng nhận phải được drain chờ.
                    conn.settimeout(None)
                    try:
                        sdk = self.nhan_viec(conn, self.bootstrap.bo_doc)
                        xu_ly_viec(sdk, backend=self.backend)
                    except Exception as exc:
                        _xoa_loi(exc)
                        self.loi = True
                        self.ngung_accept()
                        self._giu_khi_loi.wait()
                        return
        except Exception as exc:
            _xoa_loi(exc)
            self.loi = True

    def ngung_accept(self):
        with self.khoa:
            self.dung = True

    def drain(self):
        self.worker.join(0.1)
        if self.loi:
            self._giu_khi_loi.wait(0.1)
        return not self.worker.is_alive() and not self.loi


def _chay_khung(*, kiem_chu_ky, nhan_viec, backend):
    """Readiness contracts=[]: mock không chứng minh AI thật/độ chính xác."""
    if not callable(kiem_chu_ky) or not callable(nhan_viec):
        raise TypeError('Cần bộ kiểm chữ ký và seam nhận việc của Core')
    bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky)
    vong = _VongNhan(bootstrap, nhan_viec, backend)
    bat_dau = False
    try:
        bootstrap.bao_san_sang(phien_ban=PHIEN_BAN, contracts=[],
                               kiem_san_sang=backend.san_sang)
        vong.bat_dau()
        bat_dau = True
        try:
            bootstrap.cho_thu_hoi(ngung_accept=vong.ngung_accept, drain=vong.drain)
        except LoiBootstrap as exc:
            if exc.ma != 'DRAIN_CHUA_XONG':
                raise
            _xoa_loi(exc)
            gui_thong_diep(bootstrap._ra,
                {'protocol': PROTOCOL, 'kieu': 'drain_chua_xong'})
            while not vong.drain():
                pass
            bootstrap.socket.close()
            gui_thong_diep(bootstrap._ra,
                {'protocol': PROTOCOL, 'kieu': 'da_thu_hoi'})
    finally:
        if bat_dau:
            vong.ngung_accept()
            while not vong.drain():
                pass
        bootstrap.socket.close()


class ChuaKiem(ValueError):
    ma = "CHUA_KIEM"

    def __init__(self):
        super().__init__("CHUA_KIEM: PDF cần OCR-5b; chỉ nhận DOCX")


def _danh_muc_dau_vao(dau_vao):
    """LHD-E2: bytes do SDK cấp, loại/tên/phiên bản/SHA do Core ghim.

    Seam cũ chỉ nhận đúng XD đã ghim. Không có phiên bản của loại khác
    thì từ chối; tuyệt đối không mượn danh mục XD.
    """
    loai = dau_vao.get('loai_hop_dong')
    if not {'danh_muc', 'danh_muc_bytes', 'ten_loai', 'so_phien_ban'} & set(dau_vao):
        if (loai, dau_vao.get('danh_muc_id'), dau_vao.get('danh_muc_sha256')) != (
                'XD', DANH_MUC_ID, DANH_MUC_SHA256):
            raise ValueError('TRICH_DANH_MUC_KHONG_HO_TRO')
        return danh_muc_xd(), loai, 'Hợp đồng xây dựng', 1, DANH_MUC_SHA256
    ref = dau_vao.get('danh_muc')
    ten = dau_vao.get('ten_loai')
    version = dau_vao.get('so_phien_ban')
    if (not isinstance(ref, dict) or set(ref) != {'tep_id', 'sha256'}
            or not isinstance(loai, str) or re.fullmatch(r'[A-Z][A-Z0-9_]{1,31}', loai) is None
            or not isinstance(ten, str) or not ten.strip()
            or type(version) is not int or version < 1
            or dau_vao.get('danh_muc_id', loai) != loai):
        raise ValueError('TRICH_DANH_MUC_KHONG_HO_TRO')
    _uuid_noi(ref.get('tep_id'))
    sha = ref.get('sha256')
    if (not isinstance(sha, str) or re.fullmatch('[0-9a-f]{64}', sha) is None
            or dau_vao.get('danh_muc_sha256', sha) != sha):
        raise ValueError('TRICH_DANH_MUC_SAI_HASH')
    raw = dau_vao.get('danh_muc_bytes')
    if not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('TRICH_DANH_MUC_SAI_HASH')
    params = danh_muc_tham_so.doc_danh_muc(raw).tham_so
    return params, loai, ten.strip(), version, sha


class BackendTrichXuat:
    """CongAI do Core tiêm, mọi lượt gọi qua AIChung, luôn cloud=None."""

    def __init__(self, *, cong_ai, cloud=None, ra_lai=True):
        ai_chung.AIChung(cong_ai, cloud=cloud)
        self.cong_ai = cong_ai
        self.ra_lai = ra_lai

    def san_sang(self):
        ai_chung.AIChung(self.cong_ai, cloud=None)
        return len(danh_muc_xd()) == 37

    def xu_ly(self, dau_vao):
        params, loai, ten_loai, so_phien_ban, ma_bam = _danh_muc_dau_vao(dau_vao)
        tep_id = dau_vao['tep_id']
        if not isinstance(tep_id, str):
            raise ValueError('TRICH_TEP_ID_SAI')
        try:
            if str(UUID(tep_id)) != tep_id.lower():
                raise ValueError()
        except ValueError:
            raise ValueError('TRICH_TEP_ID_SAI') from None
        path = Path(dau_vao['docx'])
        if path.suffix.lower() == '.pdf':
            raise ChuaKiem()
        docx.kiem_docx(path)
        tx = TrichXuat(cong_ai=self.cong_ai, cloud=None,
            out_dir=dau_vao['out_dir'], ra_lai=self.ra_lai, params=params,
            loai_hop_dong=loai, ten_loai=ten_loai)
        sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        van_ban = docx.read_contract(path)['text']
        phan_hoi = tx.xu_ly(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
            raise ValueError('TRICH_TEP_NGUON_DA_DOI')
        # Bổ sung provenance vào phản hồi đầy đủ, không rút gọn bảng/dẫn chứng
        # hoặc KetQuaAI (kể cả các trường bị loại và mã yêu cầu của cổng).
        phan_hoi['nguon'] = dict(
            tep_id=tep_id, sha256=sha256, loai_hop_dong=loai,
            danh_muc_id=loai, danh_muc_sha256=ma_bam,
            phien_ban_nguon=PHIEN_BAN_NGUON,
            quy_trinh=dict(duong_dan=NGUON, sha256=NGUON_SHA256),
            ai_chung=dict(duong_dan=ai_chung.NGUON, sha256=ai_chung.NGUON_SHA256),
            docx=dict(sha256=docx.NGUON_SHA256),
        )
        # XD v1 có SHA ghim xác định duy nhất phiên bản; giữ phản hồi nguyên
        # byte cho gate LHD-E2. Loại/phiên bản khác ghi số để truy vết.
        if (loai, so_phien_ban, ma_bam) != ('XD', 1, DANH_MUC_SHA256):
            phan_hoi['nguon']['so_phien_ban'] = so_phien_ban
        return phan_hoi, van_ban


def chay(*, kiem_chu_ky, nhan_viec, cong_ai, cloud=None, ra_lai=True):
    """Bootstrap/lease/ACK/drain do khung hiện có quản lý; chưa ready capability."""
    return _chay_khung(kiem_chu_ky=kiem_chu_ky, nhan_viec=nhan_viec,
        backend=BackendTrichXuat(cong_ai=cong_ai, cloud=cloud, ra_lai=ra_lai))


# G3-TRICH-NOI giữ nguyên seam 3b ở trên cho consumer cũ. Entrypoint mới chỉ
# nhận tham chiếu qua SDKEngine/E1; không nhận đường dẫn kho hay tự mở kho.
LY_DO_CHUA_SAN_SANG = 'Chưa có phép đo TRICH-4b đạt; chưa công bố capability/contract.'
MIME_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
GIOI_HAN_DOCX = 20 * 1024 * 1024


def _uuid_noi(value):
    if not isinstance(value, str) or str(UUID(value)) != value.lower():
        raise ValueError('TRICH_THAM_CHIEU_SAI')
    return value


def _tham_chieu_noi(ref):
    """Vỏ tham_chieu_tep.v1 hiện có, metadata do provider Core cấp."""
    if not isinstance(ref, dict) or set(ref) != {
            'contract', 'phien_ban', 'tep_id', 'ten_tep', 'mime',
            'kich_thuoc', 'sha256', 'het_han_luc'}:
        raise ValueError('TRICH_THAM_CHIEU_SAI')
    _uuid_noi(ref['tep_id'])
    if (ref['contract'] != 'tham_chieu_tep.v1' or ref['phien_ban'] != '1.0.0'
            or not isinstance(ref['ten_tep'], str) or not ref['ten_tep']
            or type(ref['kich_thuoc']) is not int or ref['kich_thuoc'] <= 0
            or not isinstance(ref['sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', ref['sha256']) is None):
        raise ValueError('TRICH_THAM_CHIEU_SAI')
    if ref['het_han_luc'] is not None:
        han = datetime.datetime.fromisoformat(ref['het_han_luc'])
        if han.tzinfo is None or han <= datetime.datetime.now(datetime.timezone.utc):
            raise ValueError('TRICH_THAM_CHIEU_HET_HAN')
    return ref


def _ban_giao_noi(sdk, value, *, ten, metadata):
    """Một lần gửi; E1 kiểm hash/lease và ACK sau commit + đọc lại hash.

    Mất ACK giữ bản làm việc để Core đối chiếu, không lặp vô hạn trên kênh
    đã đóng và không trích/AI lại. Không bổ sung trường vào contract kết quả.
    """
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
    with io.BytesIO(raw) as stream:
        ack = sdk.ghi_ket_qua(luong=stream, ten=ten,
            du_lieu=metadata['du_lieu_ket_qua'],
            revision_tep_truoc=metadata['revision_tep_truoc'])
    if not isinstance(ack, dict) or ack.get('da_ban_giao') is not True:
        raise ValueError('TRICH_CHUA_XAC_NHAN')
    _uuid_noi(ack.get('ket_qua_id'))
    return ack, hashlib.sha256(raw).hexdigest()


def xu_ly_viec_noi(sdk, *, backend, thu_muc_lam_viec):
    """DOCX gốc hoặc DOCX OCR đã được Core commit/xác minh, cùng đường E1.

    Provider DauVaoEngine.du_lieu cấp tham_chieu_tep + metadata 3b. Nếu từ
    OCR, cấp ocr={ket_qua_id, nguon, docx, da_ban_giao}; mọi tham chiếu theo
    tham_chieu_tep.v1, không sửa contract nghiệp vụ. ACK E1 trả tham chiếu
    tệp phản hồi nguồn từ kết quả đã commit và đọc lại hash; không suy
    ket_qua_id là tep_id hay cần provider cập nhật dữ liệu đầu vào.
    """
    if not isinstance(sdk, SDKEngine):
        raise TypeError('Cần SDKEngine do Core cấp')
    dau_vao = sdk.doc_dau_vao()
    if not isinstance(dau_vao, dict) or {'docx', 'out_dir', 'danh_muc_bytes'} & set(dau_vao):
        raise ValueError('TRICH_KHONG_NHAN_DUONG_DAN_KHO')
    ref = _tham_chieu_noi(dau_vao['tham_chieu_tep'])
    if (ref['mime'] != MIME_DOCX
            or Path(ref['ten_tep']).suffix.lower() != '.docx'):
        raise ChuaKiem()
    if ref['kich_thuoc'] > GIOI_HAN_DOCX:
        raise ValueError('TRICH_TEP_QUA_LON')
    ocr = dau_vao.get('ocr')
    if ocr is not None:
        if (not isinstance(ocr, dict) or ocr.get('da_ban_giao') is not True
                or ocr.get('docx') != ref):
            raise ValueError('TRICH_OCR_CHUA_XAC_NHAN')
        _uuid_noi(ocr.get('ket_qua_id'))
        _tham_chieu_noi(ocr['nguon'])
        if ocr['nguon']['tep_id'] == ref['tep_id']:
            raise ValueError('TRICH_OCR_NGUON_SAI')
    # SDK chưa có accessor công khai; cùng cách adapter OCR đọc lease.
    giu = getattr(sdk, '_SDKEngine__giu')
    # Lease bao trùm thời hạn trích 600s và bàn giao; Core vẫn kiểm từng call.
    sdk.heartbeat(lease_giay=900)
    catalog = {}
    if 'danh_muc' in dau_vao:
        dm_ref = dau_vao['danh_muc']
        if not isinstance(dm_ref, dict):
            raise ValueError('TRICH_DANH_MUC_KHONG_HO_TRO')
        catalog_id = _uuid_noi(dm_ref.get('tep_id'))
        with sdk.mo_doc(catalog_id) as stream:
            raw = stream.read(danh_muc_tham_so.GIOI_HAN_TEP + 1)
        if len(raw) > danh_muc_tham_so.GIOI_HAN_TEP:
            raise ValueError('TRICH_DANH_MUC_QUA_LON')
        catalog['danh_muc_bytes'] = raw
    # Từ chối danh mục sai trước backend/AI hay ghi kết quả.
    params, loai, _, _, catalog_sha = _danh_muc_dau_vao({**dau_vao, **catalog})
    root = Path(thu_muc_lam_viec).resolve()
    root.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f'{giu.viec_id}-{giu.lan_thu_id}-{giu.the_he}-',
                                 dir=root))
    path = work / 'dau-vao.docx'
    bam, size = hashlib.sha256(), 0
    with sdk.mo_doc(ref['tep_id']) as src, path.open('xb') as dest:
        while True:
            chunk = src.read(min(64 * 1024, GIOI_HAN_DOCX - size + 1))
            if not chunk:
                break
            size += len(chunk)
            if size > GIOI_HAN_DOCX or size > ref['kich_thuoc']:
                raise ValueError('TRICH_TEP_QUA_LON')
            bam.update(chunk)
            dest.write(chunk)
    if (size, bam.hexdigest()) != (ref['kich_thuoc'], ref['sha256']):
        raise ValueError('TRICH_TEP_SAI_HASH')
    # Chặn PDF giả đuôi DOCX trước backend/cổng AI.
    with zipfile.ZipFile(path) as archive:
        archive.getinfo('word/document.xml')
    local = {**dau_vao, **catalog, 'tep_id': ref['tep_id'], 'docx': path,
             'out_dir': work / 'ket-qua', 'danh_muc_id': loai, 'danh_muc_sha256': catalog_sha}
    phan_hoi, van_ban = backend.xu_ly(local)
    if hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
        raise ValueError('TRICH_TEP_NGUON_DA_DOI')
    phan_hoi.setdefault('nguon', {}).update(tham_chieu_tep=dict(ref))
    if ocr is not None:
        phan_hoi['nguon']['ocr'] = ocr
    sdk.heartbeat()
    ack, sha = _ban_giao_noi(sdk, phan_hoi, ten='phan-hoi-nguon.json',
                            metadata=dau_vao['phan_hoi'])
    da_ghi = ack.get('tep')
    if (not isinstance(da_ghi, dict) or not da_ghi.get('tep_id')
            or da_ghi.get('sha256') != sha):
        raise ValueError('TRICH_THIEU_THAM_CHIEU_PHAN_HOI_CORE')
    tep_nguon = _uuid_noi(da_ghi.get('tep_id'))
    ket_qua = anh_xa_tham_so(phan_hoi, tep_id=ref['tep_id'],
        phan_hoi_nguon_tep_id=tep_nguon, van_ban=van_ban,
        loai_hop_dong=dau_vao['loai_hop_dong'],
        danh_muc_id=loai, danh_muc_sha256=catalog_sha, params=params)
    result, _ = _ban_giao_noi(sdk, ket_qua, ten='tham-so.json', metadata=dau_vao['tham_so'])
    return result


class _VongNhanNoi(_VongNhan):
    """Kéo việc qua KenhCore/WorkerEngine; không mở kênh/DB riêng."""
    def __init__(self, bootstrap, nhan_viec, backend, thu_muc_lam_viec):
        super().__init__(bootstrap, nhan_viec, backend)
        self.thu_muc_lam_viec = thu_muc_lam_viec

    def _chay(self):
        try:
            while True:
                with self.khoa:
                    if self.dung:
                        return
                try:
                    conn, _ = self.bootstrap.accept()
                except socket.timeout:
                    continue
                except LoiBootstrap as exc:
                    if exc.ma == 'CHUA_CO_QUYEN_ACCEPT':
                        return
                    raise
                with conn:
                    conn.settimeout(None)
                    # Composition root tiêm KenhCore đã xác thực BM-KENH.
                    kenh = self.nhan_viec(conn, self.bootstrap.bo_doc)
                    while True:
                        with self.khoa:
                            if self.dung:
                                return
                        try:
                            sdk = kenh.cap_sdk()
                        except LoiEngine as exc:
                            if (exc.ma != 'CHUA_SAN_SANG'
                                    or not getattr(exc, 'thu_lai_duoc', False)):
                                raise
                            # E2 chưa ready: chờ trên cùng kênh, không đổi engine.
                            time.sleep(0.1)
                            continue
                        if sdk is None:
                            time.sleep(0.1)
                            continue
                        ack = xu_ly_viec_noi(sdk, backend=self.backend,
                            thu_muc_lam_viec=self.thu_muc_lam_viec)
                        kenh.ket_thuc(getattr(sdk, '_SDKEngine__giu'),
                            ket_qua_id=ack['ket_qua_id'])
        except Exception as exc:
            _xoa_loi(exc)
            self.loi = True
            self.ngung_accept()
            # Không báo drain xong khi ACK/lease cần Core đối chiếu.


def chay_noi(*, kiem_chu_ky, nhan_viec, cong_ai, thu_muc_lam_viec,
             cloud=None, ra_lai=True):
    """Entrypoint 3b trên kênh chung; capability chưa sẵn sàng vì TRICH-4b.

    nhan_viec dựng đầu KenhCore từ socket/credential bootstrap do P1 cấp.
    Không dựng provider/kho/DB ở engine. contracts=[] giữ gate E2 đóng.
    """
    if not callable(kiem_chu_ky) or not callable(nhan_viec):
        raise TypeError('Cần bộ kiểm chữ ký và kênh Core đã xác thực')
    backend = BackendTrichXuat(cong_ai=cong_ai, cloud=cloud, ra_lai=ra_lai)
    bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky)
    vong = _VongNhanNoi(bootstrap, nhan_viec, backend, thu_muc_lam_viec)
    started = False
    try:
        bootstrap.bao_san_sang(phien_ban=PHIEN_BAN, contracts=[],
                               kiem_san_sang=backend.san_sang)
        vong.bat_dau()
        started = True
        try:
            bootstrap.cho_thu_hoi(ngung_accept=vong.ngung_accept, drain=vong.drain)
        except LoiBootstrap as exc:
            if exc.ma != 'DRAIN_CHUA_XONG':
                raise
            _xoa_loi(exc)
            gui_thong_diep(bootstrap._ra,
                {'protocol': PROTOCOL, 'kieu': 'drain_chua_xong'})
            while not vong.drain():
                time.sleep(0.1)
            bootstrap.bi_mat.thu_hoi()
            bootstrap.socket.close()
            gui_thong_diep(bootstrap._ra,
                {'protocol': PROTOCOL, 'kieu': 'da_thu_hoi'})
    finally:
        if started:
            vong.ngung_accept()
            while not vong.drain():
                time.sleep(0.1)
        bootstrap.socket.close()
