"""TRICH-1b: chép có sửa pipeline review v3/2026-10-15a.

Nguồn: src/kho_tri_thuc/m4/review_goc/trich_xuat/quy_trinh.py, chỉ đọc.
SHA256: a76e95a55cb7253cc7446ead9e7fd495fb9c3ea457c612259bd062aa27b26264.
Giữ nhóm 8, chia đoạn, tự kiểm trích dẫn, rà lại, kiểm logic và xuất nguồn.
Đổi build_prompt/ai_tim_vi_tri sang YeuCauAI, mọi lượt qua AIChung/CongAI.goi;
danh sách từng câu đổi và lý do ở ai_chung.CAU_HOI_DOI.
Chỉ DOCX/XML, danh mục XD 37 mã ghim từ TRICH-1a; cloud=None.
Chưa nối BackendTrichXuat (TRICH-3b), chưa đo trước/sau (TRICH-4b).
"""

NGUON = "src/kho_tri_thuc/m4/review_goc/trich_xuat/quy_trinh.py"
NGUON_SHA256 = "a76e95a55cb7253cc7446ead9e7fd495fb9c3ea457c612259bd062aa27b26264"
PHIEN_BAN_NGUON = "2026-10-15a"

import datetime
import os
import re
import time

from .ai_chung import AIChung, AILoi, DaDung, CHI_DAN_TRICH, YeuCauAI
from .docx import kiem_docx, read_contract
from .tham_so import danh_muc_xd
from ...m4.review_goc.trich_xuat.cau_truc import build_structure, locate, nhan, save, than, vi_tri
from ...m4.review_goc.trich_xuat.kiem_tra import (check, compare, gan_dieu_khoan, giong_nhau, la_khong_co, la_ok, load_key, loose, norm,
                       tim_dap_an)
from ...m4.review_goc.trich_xuat.logic import kiem_tra_logic

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
                 tien_do=None, ghi_log=None, dung=None, thu_muc_dap_an=None, rng=None):
        if cloud is not None:
            raise ValueError("TRICH_CLOUD_BI_CHAN")
        self.params = danh_muc_xd()
        self.ai = AIChung(cong_ai, cloud=None, dung=dung)
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
        from ...m4.review_goc.trich_xuat.xuat import ghi_ket_qua_hd
        kq["tom_tat"]["so_can_xem"] = sum(1 for d in bang if not la_ok(d["kiem_tra"]))
        kq["tom_tat"]["so_da_xac_nhan"] = 0
        ghi_ket_qua_hd(kq, out)
        self.ghi_log(f"  xong {file} | {n_ok}/{len(bang)} OK" + (f" | đáp án {n_key}/{n_keyed}" if key else "")
                     + f" | {dt:.0f}s | lỗi AI: {n_err}")
        return kq
