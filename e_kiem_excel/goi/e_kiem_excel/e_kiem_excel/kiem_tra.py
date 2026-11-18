"""K1–K6 chuyển từ mã nguồn đã ghim; K7/K8 được bổ sung ở lát sau."""

from collections import Counter, defaultdict
from datetime import date, datetime, time
from decimal import Decimal
import json
import re
from openpyxl.utils import column_index_from_string, get_column_letter
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from .chuan_hoa import bo_dau, num
from .tham_chieu import (LOI, MUC, bo_chuoi, tach_tham_chieu, mau_cong_thuc,
                         la_tong, la_so, la_cong_thuc, giong, hang_so_nhung)

JSON_TOI_DA_BYTE = 20 * 1024 * 1024
CANH_BAO_EX1 = "EX-1 chỉ chạy K1–K6; K6 chưa phát cờ theo cây K7; K7, K8 và báo cáo Excel chưa được thực hiện."

# Tên trường theo từng bảng gốc; ô được ghép với tên sheet khi xuất.
BANG_JSON = {
    "k1_sheet": ("sheet", "sheet trang_thai so_dong so_cot so_cong_thuc so_go_tay so_ref_loi so_o_loi so_chua_tinh"),
    "k1_lien_ket_ngoai": ("ngoai", "stt ten_tep so_cong_thuc"),
    "k2_mau_cot": ("cot", "sheet cot tieu_de so_cong_thuc so_khong_tong so_theo_mau ty_le so_mau cong_thuc_mau"),
    "k2_lech_mau": ("lech", "sheet o tieu_de nhan_dong cong_thuc cong_thuc_mau gia_tri"),
    "k2_go_tay": ("tay", "sheet o tieu_de nhan_dong gia_tri cong_thuc_mau nhom"),
    "k3_lien_ket_dong": ("lien_ket", "sheet o tieu_de nhan_dong cong_thuc tro_toi nhan_dich do_giong ket_luan gia_tri"),
    "k4_sheet_an": ("an", "sheet trang_thai so_dong so_cong_thuc so_tham_chieu tu_sheet ban_hien so_o_khac"),
    "k4_khac_ban_hien": ("an_khac", "sheet_hien sheet_an o nhan_dong gia_tri_hien gia_tri_an"),
    "k5_so_dang_chu": ("chu", "sheet o tieu_de nhan_dong noi_dung"),
    "k6_hang_so": ("nhung", "hang_so loai so_cong_thuc so_trong_cay vi_du_o cong_thuc"),
}


def _gia_tri_json(v):
    if v is None or isinstance(v, (str, bool)):
        return v
    if isinstance(v, (int, float, Decimal)):
        d = num(v)
        if d is None:
            raise LoiNghiepVu("TEP_HONG", "Tệp Excel có giá trị số không hợp lệ.")
        return format(d, "f")
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    raise LoiNghiepVu("TEP_HONG", "Tệp Excel có kiểu ô chưa được hỗ trợ.")


def ma_hoa_json(du_lieu):
    """Chặn trần trong lúc mã hóa; không cắt bớt dữ liệu kết quả."""
    raw = bytearray()
    for khoi in json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":")).iterencode(du_lieu):
        khoi = khoi.encode("utf-8")
        if len(raw) + len(khoi) > JSON_TOI_DA_BYTE:
            raise LoiNghiepVu("VUOT_GIOI_HAN", "Kết quả JSON vượt giới hạn 20 MiB.")
        raw.extend(khoi)
    return bytes(raw)

class KiemTra:
    def __init__(self, so_do, tham_so):
        self.sd = so_do
        self.tham_so = dict(tham_so)
        self.o_dich = self.tham_so.get("o_dich") or None
        self.ph = []          # phát hiện
        self.kq = {}          # bảng kết quả theo kiểm tra

    def them(self, muc, kt, o, mo_ta, so_o=1, gia_tri=None, tai_lieu=""):
        self.ph.append(dict(muc=muc, kt=kt, o=o, mo_ta=mo_ta, so_o=so_o, gia_tri=gia_tri, tai_lieu=tai_lieu))

    def chay(self, viec):
        for kiem in (self.k1_tong_quan, self.k2_ban_do_cong_thuc, self.k3_lien_ket_dong,
                     self.k4_sheet_an, self.k5_so_dang_chu, self.k6_tham_so_nhung):
            viec.kiem_huy()
            kiem()
            viec.kiem_huy()
        self.ph.sort(key=lambda x: (MUC[x["muc"]], x["kt"]))
        return self

    def ket_qua_json(self, bam, phien_ban):
        kq = {"phien_ban": 1, "phien_ban_engine": phien_ban, "bam_dau_vao": bam,
              "o_dich": None, "bo_nhom": None, "phat_hien": [],
              "k1_so_ten_loi": str(self.kq["ten_loi"]),
              "k7_cay": [], "k8_nguon": [], "canh_bao": [CANH_BAO_EX1]}
        for p in self.ph:
            kq["phat_hien"].append({
                "muc": p["muc"], "kiem": p["kt"], "o": p["o"], "mo_ta": p["mo_ta"],
                "so_o": str(p["so_o"]), "gia_tri": _gia_tri_json(p["gia_tri"]), "tai_lieu": p["tai_lieu"]})
        for ten, (nguon, cot) in BANG_JSON.items():
            ds = []
            for dong in self.kq[nguon]:
                row = {k: _gia_tri_json(v) for k, v in zip(cot.split(), dong, strict=True)}
                if "o" in row:
                    row["o"] = f"{row.get('sheet', row.get('sheet_hien'))}!{row['o']}"
                ds.append(row)
            kq[ten] = ds
        return kq

    # ---------------------------------------------------------- K1
    def k1_tong_quan(self):
        sd = self.sd
        dong, ngoai_dung = [], Counter()
        self._ct, self._ngoai_o = {}, {}         # (sh, r, c) -> công thức
        for ws in sd.wb.worksheets:
            n_ct = n_so = n_chua_tinh = 0
            loi_gt, loi_ct = [], 0
            wsv = sd.wv[ws.title]
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if la_cong_thuc(v):
                        n_ct += 1
                        self._ct[(ws.title, c.row, c.column)] = v
                        if "#REF!" in v:
                            loi_ct += 1
                        for m in re.finditer(r"\[(\d+)\]", bo_chuoi(v)):
                            ngoai_dung[int(m.group(1))] += 1
                            self._ngoai_o.setdefault(int(m.group(1)), set()).add((ws.title, c.column_letter))
                        gv = wsv.cell(c.row, c.column).value
                        if gv is None:
                            n_chua_tinh += 1
                        elif isinstance(gv, str) and gv.strip() in LOI:
                            loi_gt.append(c.coordinate)
                    elif la_so(v):
                        n_so += 1
            dong.append([ws.title, ws.sheet_state, ws.max_row, ws.max_column, n_ct, n_so, loi_ct, len(loi_gt), n_chua_tinh])
            if loi_ct:
                self.them("Trung bình" if ws.sheet_state == "visible" else "Kiểm soát", "K1", ws.title,
                          f"{loi_ct} công thức chứa #REF! (mất tham chiếu)", loi_ct, tai_lieu="Giải trình / sửa file")
            if loi_gt:
                self.them("Cao" if ws.sheet_state == "visible" else "Kiểm soát", "K1", f"{ws.title}!{loi_gt[0]}",
                          f"{len(loi_gt)} ô công thức đang ra lỗi (#REF!, #DIV/0!, #N/A...): " + ", ".join(loi_gt[:8]), len(loi_gt))
            if n_ct and n_chua_tinh > 0.5 * n_ct:
                self.them("Kiểm soát", "K1", ws.title, f"{n_chua_tinh}/{n_ct} công thức không có giá trị lưu: file chưa được Excel tính lại, "
                                                       "giá trị đọc được có thể không đúng", n_chua_tinh)
        self.kq["sheet"] = dong
        # liên kết file ngoài
        lk = []
        for i, tgt in sd.ngoai.items():
            lk.append([i, tgt, ngoai_dung.get(i, 0)])
            if ngoai_dung.get(i):
                cot = ", ".join(f"{a}!{b}" for a, b in sorted(self._ngoai_o.get(i, ())))
                self.them("Cao", "K1", f"[{i}]", f"{ngoai_dung[i]} công thức (cột {cot}) lấy số từ file ngoài: {tgt}", ngoai_dung[i],
                          tai_lieu="File Excel đang được liên kết (bản gốc)")
                self.ph[-1]["_ngoai"] = i
        rac = sum(1 for x in lk if not x[2])
        if rac:
            self.them("Kiểm soát", "K1", "Workbook", f"{rac} liên kết file ngoài chỉ còn trong tên định nghĩa (rác từ file mẫu khác), "
                                                     "không công thức nào dùng", rac)
        self.kq["ngoai"] = lk
        # tên định nghĩa lỗi
        ten_loi = [n for n, d in sd.wb.defined_names.items() if "#REF!" in str(d.attr_text)]
        self.kq["ten_loi"] = len(ten_loi)
        if ten_loi:
            self.them("Kiểm soát", "K1", "Workbook", f"{len(ten_loi)} tên định nghĩa (Name) bị #REF!", len(ten_loi))

    # ---------------------------------------------------------- K2
    def k2_ban_do_cong_thuc(self):
        sd = self.sd
        theo_cot = defaultdict(list)                # (sh, c) -> [(r, mẫu, f)]
        for (sh, r, c), f in self._ct.items():
            if sd.an(sh):
                continue
            theo_cot[(sh, c)].append((r, mau_cong_thuc(f, r, c), f))
        tom, lech, tay = [], [], []
        for (sh, c), ds in sorted(theo_cot.items()):
            ds_ = [x for x in ds if not la_tong(x[2])]
            if len(ds_) < 10:
                continue
            dem = Counter(m for _, m, _ in ds_)
            mau, n = dem.most_common(1)[0]
            ty = n / len(ds_)
            hdr = sd.tieu_de(sh, c)
            tom.append([sh, get_column_letter(c), hdr, len(ds), len(ds_), n, round(ty, 3), len(dem), ds_[0][2] if False else
                        next(f for _, m_, f in ds_ if m_ == mau)[:80]])
            if n < 10 or ty < 0.7:
                continue                                # cột không có mẫu chính rõ ràng
            dong_mau = sorted(r for r, m, _ in ds_ if m == mau)
            lo, hi = dong_mau[0], dong_mau[-1]
            for r, m, f in ds_:
                if m != mau and dem[m] <= 2 and lo <= r <= hi:
                    lech.append([sh, f"{get_column_letter(c)}{r}", hdr, sd.nhan_dong(sh, r), f[:100],
                                 next(ff for rr, mm, ff in ds_ if mm == mau)[:100], sd.v(sh, c, r)])
            # số gõ tay nằm giữa cột công thức
            co_ct = {r for r, _, _ in ds}
            for r in range(lo, hi + 1):
                if r in co_ct:
                    continue
                v = sd.f(sh, c, r)
                if la_so(v) and v != 0:
                    du_lieu = any(la_cong_thuc(sd.f(sh, cc, r)) for cc in range(1, sd.wb[sh].max_column + 1) if cc != c) \
                              or sd.nhan_dong(sh, r)
                    if du_lieu:
                        tay.append([sh, f"{get_column_letter(c)}{r}", hdr, sd.nhan_dong(sh, r), v,
                                    next(ff for rr, mm, ff in ds_ if mm == mau)[:80], "Chưa phân nhóm"])
        self.kq.update(cot=tom, lech=lech, tay=tay)
        by = Counter(x[0] for x in lech)
        for sh, n in by.items():
            vd = [x[1] for x in lech if x[0] == sh][:6]
            self.them("Trung bình", "K2", f"{sh}!{vd[0]}", f"{n} ô công thức lệch mẫu chung của cột ({', '.join(vd)}...)", n,
                      tai_lieu="Giải trình vì sao công thức khác")
        by = defaultdict(list)
        for x in tay:
            by[(x[0], x[1].rstrip("0123456789"))].append(x)
        for (sh, col), xs in by.items():
            self.them("Cao", "K2", f"{sh}!{xs[0][1]}",
                      f"{len(xs)} số gõ tay nằm giữa cột công thức '{xs[0][2][:40]}' ({', '.join(x[1] for x in xs[:6])}...)",
                      len(xs), sum((num(x[4]) for x in xs), Decimal(0)), "")

    # ---------------------------------------------------------- K3
    def k3_lien_ket_dong(self):
        sd = self.sd
        out = []
        cap = Counter()
        for (sh, r, c), f in self._ct.items():
            for x in tach_tham_chieu(f, sh):
                if x["sh"] != sh and x["ngoai"] is None and x["r1"] == x["r2"]:
                    cap[(sh, x["sh"])] += 1
        for (sh, r, c), f in self._ct.items():
            if sd.an(sh):
                continue
            refs = [x for x in tach_tham_chieu(f, sh) if x["sh"] != sh and x["ngoai"] is None
                    and x["c1"] == x["c2"] and x["r1"] == x["r2"] and x["sh"] in sd.wb.sheetnames]
            if not refs or len({(x["sh"], x["r1"]) for x in refs}) != 1:
                continue
            x = refs[0]
            if cap[(sh, x["sh"])] < 20:
                continue                                # bảng tổng hợp, giấy đề nghị: không phải liên kết theo từng hạng mục
            if la_cong_thuc(sd.f(x["sh"], x["c1"], x["r1"])) and la_tong(sd.f(x["sh"], x["c1"], x["r1"])):
                continue                                # trỏ vào dòng tổng: liên kết tổng hợp, không so tên
            a, b = sd.nhan_dong(sh, r), sd.nhan_dong(x["sh"], x["r1"])
            if not a or len(a) < 6 or re.match(r"(tong|cong|thue|vat|gia tri)", bo_dau(b)):
                continue
            g = giong(a, b)
            if g is None:
                kl = "Trỏ tới dòng không có tên hạng mục"
            elif g < 0.6:
                kl = "Lệch dòng: tên hai đầu khác nhau"
            else:
                continue
            out.append([sh, f"{get_column_letter(c)}{r}", sd.tieu_de(sh, c), a, f[:80],
                        f"{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}", b, round(g or 0, 2), kl, sd.v(sh, c, r)])
        self.kq["lien_ket"] = out
        by = defaultdict(list)
        for x in out:
            by[(x[0], x[1].rstrip("0123456789"), x[8])].append(x)
        for (sh, col, kl), xs in by.items():
            self.them("Cao", "K3", f"{sh}!{xs[0][1]}", f"{len(xs)} ô: {kl} ({', '.join(x[1] for x in xs[:6])} -> {xs[0][5]}...)",
                      len(xs), sum((num(x[9]) for x in xs if la_so(x[9])), Decimal(0)), "Sửa liên kết; xác định nguồn đúng của hạng mục")

    # ---------------------------------------------------------- K4
    def k4_sheet_an(self):
        sd = self.sd
        an = [ws.title for ws in sd.wb.worksheets if ws.sheet_state != "visible"]
        tro = Counter()
        for (sh, r, c), f in self._ct.items():
            if sd.an(sh):
                continue
            for x in tach_tham_chieu(f, sh):
                if x["sh"] in an:
                    tro[(sh, x["sh"])] += 1
        dong, so_sanh = [], []
        for h in an:
            ws = sd.wb[h]
            ten_goc = re.sub(r"\s*\(\d+\)\s*$", "", h).strip()
            twin = next((w.title for w in sd.wb.worksheets if w.sheet_state == "visible" and w.title != h and
                         bo_dau(w.title) == bo_dau(ten_goc)), None)
            n_tro = sum(n for (a, b), n in tro.items() if b == h)
            khac = []
            if twin:
                a, b = sd.wv[twin], sd.wv[h]
                for r in range(1, max(a.max_row, b.max_row) + 1):
                    for c in range(1, max(a.max_column, b.max_column) + 1):
                        va, vb = a.cell(r, c).value, b.cell(r, c).value
                        if va != vb and not (la_so(va) and la_so(vb) and abs(va - vb) < 1e-9):
                            khac.append((r, c, va, vb))
                for r, c, va, vb in khac[:300]:
                    so_sanh.append([twin, h, f"{get_column_letter(c)}{r}", sd.nhan_dong(twin, r), va, vb])
            dong.append([h, ws.sheet_state, ws.max_row, sum(1 for k in self._ct if k[0] == h), n_tro,
                         ", ".join(f"{a} ({n})" for (a, b), n in tro.items() if b == h), twin or "", len(khac) if twin else None])
            mo_ta = f"Sheet ẩn '{h}'"
            if n_tro:
                mo_ta += f" được {n_tro} công thức ở sheet hiện tham chiếu"
            if twin:
                mo_ta += f"; là bản khác của '{twin}', khác {len(khac)} ô"
            self.them("Trung bình" if (n_tro or (twin and khac)) else "Kiểm soát", "K4", h, mo_ta, n_tro or 1,
                      tai_lieu="Giải trình sheet ẩn; xác nhận bản nào là bản đã ký")
        self.kq.update(an=dong, an_khac=so_sanh)

    # ---------------------------------------------------------- K5
    def k5_so_dang_chu(self):
        sd = self.sd
        out = []
        for ws in sd.wb.worksheets:
            if ws.sheet_state != "visible":
                continue
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if isinstance(v, str) and not v.startswith("="):
                        t = v.strip().replace(" ", "")
                        if t and re.fullmatch(r"[-+]?\d+([.,]\d+)?%?", t) and not re.fullmatch(r"\d{1,2}", t):
                            out.append([ws.title, c.coordinate, sd.tieu_de(ws.title, c.column), sd.nhan_dong(ws.title, c.row), v])
        # bỏ cột STT, số hiệu (nhiều ô chữ số liên tiếp ở cột trái tên)
        out = [x for x in out if column_index_from_string(re.match(r"[A-Z]+", x[1]).group(0)) > sd.cot_ten(x[0])]
        self.kq["chu"] = out
        if out:
            self.them("Trung bình", "K5", f"{out[0][0]}!{out[0][1]}", f"{len(out)} ô số đang lưu dạng chữ, Excel không cộng vào tổng "
                                                                     f"({', '.join(x[0] + '!' + x[1] for x in out[:5])}...)", len(out))

    # ---------------------------------------------------------- K6
    def k6_tham_so_nhung(self):
        sd = self.sd
        cot_cay = set()
        for row in self.kq.get("cay", []):
            m = re.match(r"(.+)!([A-Z]+)\d+", str(row[2] or ""))
            if m:
                cot_cay.add((m.group(1), m.group(2)))
        dem = defaultdict(list)
        for (sh, r, c), f in self._ct.items():
            if sd.an(sh):
                continue
            for s in hang_so_nhung(f):
                dem[s].append(f"{sh}!{get_column_letter(c)}{r}")
        out = []
        for s, cells in sorted(dem.items(), key=lambda x: -len(x[1])):
            sh0 = cells[0].split("!")[0]
            r0 = int(re.search(r"(\d+)$", cells[0]).group(1))
            c0 = column_index_from_string(re.search(r"!([A-Z]+)", cells[0]).group(1))
            loai = "Thuế suất?" if s in ("1.08", "1.1", "1.05", "1.1", "0.08", "8%", "10%") else \
                   ("Tỷ lệ %" if s.endswith("%") or re.fullmatch(r"0\.\d{1,2}", s) else "Hằng số khác (kích thước, hệ số kỹ thuật...)")
            trong_cay = [x for x in cells if (x.split("!")[0], re.search(r"!([A-Z]+)", x).group(1)) in cot_cay]
            out.append([s, loai, len(cells), len(trong_cay), ", ".join((trong_cay or cells)[:8]),
                        self._ct.get((sh0, r0, c0), "")[:100]])
        self.kq["nhung"] = out
        for s, loai, n, n_cay, vd, f in out:
            if not loai.startswith("Hằng số khác") and n_cay:
                n = n_cay
                self.them("Trung bình", "K6", vd.split(",")[0], f"Hằng số {s} ({loai}) gõ thẳng trong {n} công thức: cần đối chiếu tài liệu nguồn "
                                                               "và nên đặt thành ô tham số", n, tai_lieu="")

