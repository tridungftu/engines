"""K1–K8 chuyển từ mã nguồn đã ghim; xử lý trong RAM."""

from collections import Counter, defaultdict
from datetime import date, datetime, time
from decimal import Decimal, localcontext
import json
import re
from openpyxl.utils import column_index_from_string, get_column_letter
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from .chuan_hoa import bo_dau, num
from .bo_nhom import (doc_bo_nhom, doc_json, khop_tu_khoa, kiem_tu_khoa,
                      sai_tham_so, CHUA_PHAN_NHOM, NGOAI_NHOM, TAI_LIEU_NGOAI)
from .doc_bang import tim_bang_chi_tiet, _tim_tien_te
from .tham_chieu import (LOI, MUC, QREF, LREF, bo_chuoi, tach_tham_chieu, mau_cong_thuc,
                         la_tong, la_so, la_cong_thuc, giong, hang_so_nhung)

JSON_TOI_DA_BYTE = 20 * 1024 * 1024

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


def _la_so_kl(v):
    return (isinstance(v, Decimal) and v.is_finite()) or la_so(v)


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
        if type(self.tham_so.get('kiem_nguon_kl', False)) is not bool:
            sai_tham_so()
        self.bo_nhom = doc_bo_nhom(self.tham_so.get("bo_nhom_json", ""))
        self.o_dich = self._doc_o_dich(self.tham_so.get("o_dich", ""))
        nhan = self.tham_so.get("nhan_o_dich_json", "")
        self.nhan_o_dich = [] if nhan == "" else doc_json(nhan, 4096)
        if (not isinstance(self.nhan_o_dich, list)
                or (nhan != "" and not self.nhan_o_dich)):
            sai_tham_so()
        for tu in self.nhan_o_dich:
            kiem_tu_khoa(tu)
        self.so_ngoai_nhom = None if self.bo_nhom is None else 0
        self._kiem_huy = lambda: None
        self.ph = []          # phát hiện
        self.kq = {}          # bảng kết quả theo kiểm tra

    def _doc_o_dich(self, dich):
        if dich == "":
            return None
        if not isinstance(dich, str) or len(dich) > 512:
            sai_tham_so()
        m = re.fullmatch(r"(?P<sh>'(?:[^']|'')+'|[^'!]+)!\$?(?P<c>[A-Za-z]{1,3})\$?(?P<r>[1-9][0-9]{0,6})", dich)
        if not m:
            sai_tham_so()
        sh = m['sh']
        if sh.startswith("'"):
            sh = sh[1:-1].replace("''", "'")
        c, r = m['c'].upper(), int(m['r'])
        if sh not in self.sd.wb.sheetnames or column_index_from_string(c) > 16384 or r > 1048576:
            sai_tham_so()
        return f"{sh}!{c}{r}"

    def _nhom_goc(self, tieu_de, nhan="", sh=""):
        if self.bo_nhom is None:
            return CHUA_PHAN_NHOM
        n = self.bo_nhom.tim(tieu_de, nhan, sh)
        return n['ten'] if n else NGOAI_NHOM

    def _tai_lieu(self, nhom):
        if nhom == NGOAI_NHOM:
            return TAI_LIEU_NGOAI
        return self.bo_nhom.tai_lieu(nhom) if self.bo_nhom else ""

    def _tim_o_dich(self):
        """master_hd.tim_so_tong_hop: 80 dòng, 12 cột, số đầu trong 6 ô bên phải.

        LABELS/tim_so_tong_hop Decimal đã chuyển ở EX-4 trong doc_bang.py;
        bản K7 thay LABELS bằng nhãn module, không sửa tệp EX-5 sở hữu.
        """
        if not self.nhan_o_dich:
            return None
        for ws in self.sd.wv.worksheets:
            if ws.sheet_state != "visible":
                continue
            for row in ws.iter_rows(max_row=min(ws.max_row, 80), max_col=min(ws.max_column, 12)):
                self._kiem_huy()
                for cell in row:
                    t = bo_dau(cell.value) if isinstance(cell.value, str) else ""
                    if not t or len(t) > 140 or not any(khop_tu_khoa(tu, t) for tu in self.nhan_o_dich):
                        continue
                    for c in range(cell.column + 1, min(ws.max_column, cell.column + 6) + 1):
                        o = f"{ws.title}!{get_column_letter(c)}{cell.row}"
                        if num(ws.cell(cell.row, c).value) is not None:
                            return o
        return None

    def them(self, muc, kt, o, mo_ta, so_o=1, gia_tri=None, tai_lieu=""):
        self.ph.append(dict(muc=muc, kt=kt, o=o, mo_ta=mo_ta, so_o=so_o, gia_tri=gia_tri, tai_lieu=tai_lieu))

    def chay(self, viec):
        self._kiem_huy = viec.kiem_huy
        for kiem in (self.k1_tong_quan, self.k2_ban_do_cong_thuc, self.k3_lien_ket_dong,
                     self.k4_sheet_an, self.k5_so_dang_chu, self.k7_cay_truy_vet, self.k6_tham_so_nhung):
            viec.kiem_huy()
            kiem()
            viec.kiem_huy()
        if self.tham_so.get('kiem_nguon_kl', False):
            viec.kiem_huy()
            self.k8_nguon_kl()
            viec.kiem_huy()
        self._xep_lai()
        self.ph.sort(key=lambda x: (MUC[x["muc"]], x["kt"]))
        return self

    def ket_qua_json(self, bam, phien_ban):
        kq = {"phien_ban": 1, "phien_ban_engine": phien_ban, "bam_dau_vao": bam,
              "o_dich": self.kq['dich'], "bo_nhom": self.bo_nhom.tham_chieu if self.bo_nhom else None, "phat_hien": [],
              "k1_so_ten_loi": str(self.kq["ten_loi"]),
              "k7_cay": [], "k8_nguon": [], "canh_bao": []}
        for row in self.kq['cay']:
            cap, ten, o, f, v, loai, nhom, tai_lieu, ghi = row
            kq['k7_cay'].append(dict(cap=str(cap), ten=ten, o=o, cong_thuc=f, gia_tri=_gia_tri_json(v),
                                     la=loai in ('Nhập tay', 'Nhóm nhập tay'), loai=loai,
                                     nhom=nhom or None, tai_lieu=tai_lieu, ghi_chu=ghi))
        for row in self.kq.get('nguon', []):
            dong, ten, dvt, hd, lk, gkn, glk, nguon, co, duong, kt, nkt = row
            kq['k8_nguon'].append(dict(
                o=f"{self.kq['bang_sh']}!{self.kq['cot_kl']}{dong}", dong=str(dong), ten=ten, dvt=dvt,
                kl_hd=_gia_tri_json(hd), kl_luy_ke=_gia_tri_json(lk),
                gia_tri_ky_nay={"so": _gia_tri_json(gkn), "tien_te": self.kq.get('tien_te')},
                gia_tri_luy_ke={"so": _gia_tri_json(glk), "tien_te": self.kq.get('tien_te')},
                nguon=nguon, luu_y=co, duong_di=duong, kl_ky_truoc=_gia_tri_json(kt), nguon_ky_truoc=nkt))
        for p in self.ph:
            kq["phat_hien"].append({
                "muc": p["muc"], "kiem": p["kt"], "o": p["o"], "mo_ta": p["mo_ta"],
                "so_o": str(p["so_o"]), "gia_tri": (
                    {"so": _gia_tri_json(p["gia_tri"]), "tien_te": self.kq.get('tien_te')}
                    if p["kt"] == "K8" and p["gia_tri"] is not None else _gia_tri_json(p["gia_tri"])), "tai_lieu": p["tai_lieu"]})
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
                                    next(ff for rr, mm, ff in ds_ if mm == mau)[:80], self._nhom_goc(hdr, sd.nhan_dong(sh, r), sh)])
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
                      len(xs), sum((num(x[4]) for x in xs), Decimal(0)), self._tai_lieu(xs[0][6]))

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
                                                               "và nên đặt thành ô tham số", n, tai_lieu=self._tai_lieu(self._nhom_goc("Tỷ lệ %")))


    def k7_cay_truy_vet(self, max_sau=14):
        sd = self.sd
        dich = self.o_dich
        if not dich:
            dich = self._tim_o_dich()
        rows = []
        so_o_da_doc = 0
        if not dich or "!" not in dich:
            self.kq["cay"], self.kq["dich"] = rows, None
            self.them("Kiểm soát", "K7", "-", "Không có ô đích để truy vết. Quản trị viên kiểm tra ô đích hoặc danh sách nhãn trong cài đặt bước.")
            return
        sh0, cd0 = dich.rsplit("!", 1)
        m = re.match(r"([A-Z]+)(\d+)", cd0.replace("$", ""))
        da = {}

        def them_dong(cap, ten, o, f, v, loai, nhom="", ghi=""):
            self._kiem_huy()
            if len(rows) >= 100000:
                raise LoiNghiepVu("VUOT_GIOI_HAN", "Cây truy vết vượt giới hạn 100.000 nút.")
            rows.append([cap, ("    " * cap) + ten, o, f, v, loai, nhom, self._tai_lieu(nhom) if loai in ("Nhập tay", "Nhóm nhập tay") else "", ghi])

        def tham(sh, c, r, cap):
            nonlocal so_o_da_doc
            self._kiem_huy()
            key = (sh, c, r)
            o = f"{sh}!{get_column_letter(c)}{r}"
            ten = (sd.nhan_dong(sh, r) or "") + (f"  [{sd.tieu_de(sh, c)}]" if sd.tieu_de(sh, c) else "")
            if key in da:
                them_dong(cap, ten, o, "", sd.v(sh, c, r), "Đã phân rã", ghi=f"xem dòng {da[key]}")
                return
            f = sd.f(sh, c, r)
            if not la_cong_thuc(f):
                loai = "Nhập tay" if la_so(f) else ("Trống" if f in (None, "") else "Chữ")
                da[key] = len(rows) + 2
                them_dong(cap, ten, o, "", f, loai, self._nhom_goc(sd.tieu_de(sh, c), sd.nhan_dong(sh, r), sh) if loai == "Nhập tay" else "")
                return
            da[key] = len(rows) + 2
            them_dong(cap, ten, o, f[:150], sd.v(sh, c, r), "Công thức", ghi="sheet ẩn" if sd.an(sh) else "")
            if cap >= max_sau:
                raise LoiNghiepVu("VUOT_GIOI_HAN", "Cây truy vết vượt giới hạn 14 tầng.")
            for s in hang_so_nhung(f):
                them_dong(cap + 1, f"Hằng số trong công thức: {s}", o, "", s, "Tham số gõ cứng", self._nhom_goc("Tỷ lệ %"))
            for x in tach_tham_chieu(f, sh):
                if x["ngoai"] is not None:
                    them_dong(cap + 1, f"File ngoài: {sd.ngoai.get(x['ngoai'], '?')[:80]}",
                              f"[{x['ngoai']}]{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}", "", None, "File ngoài",
                              ghi="File Excel đang được liên kết")
                    continue
                if x["sh"] not in sd.wb.sheetnames:
                    them_dong(cap + 1, f"Sheet không tồn tại: {x['sh']}", "", "", None, "Lỗi tham chiếu")
                    continue
                n_o = (x["c2"] - x["c1"] + 1) * (x["r2"] - x["r1"] + 1)
                if n_o > 250000:
                    raise LoiNghiepVu("VUOT_GIOI_HAN", "Dải truy vết vượt giới hạn 250.000 ô.")
                so_o_da_doc += n_o
                if so_o_da_doc > 500000:
                    raise LoiNghiepVu("VUOT_GIOI_HAN", "Tổng lượt đọc ô truy vết vượt giới hạn 500.000.")
                if n_o == 1:
                    tham(x["sh"], x["c1"], x["r1"], cap + 1)
                    continue
                # dải: gom theo mẫu công thức, phân rã 1 ô đại diện cho mỗi mẫu; ô nhập tay gom thành 1 nút
                mau, tay, tong_tay = defaultdict(list), [], Decimal(0)
                for rr in range(x["r1"], x["r2"] + 1):
                    self._kiem_huy()
                    for cc in range(x["c1"], x["c2"] + 1):
                        ff = sd.f(x["sh"], cc, rr)
                        if la_cong_thuc(ff):
                            mau[mau_cong_thuc(ff, rr, cc)].append((cc, rr))
                        elif la_so(ff):
                            tay.append((cc, rr))
                            v = num(ff)
                            if v is None:
                                raise LoiNghiepVu("TEP_HONG", "Tệp Excel có giá trị số không hợp lệ.")
                            with localcontext() as ctx:
                                ctx.prec = max(tong_tay.adjusted(), v.adjusted()) - min(
                                    tong_tay.as_tuple().exponent, v.as_tuple().exponent) + 2
                                tong_tay += v
                rg = f"{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}:{get_column_letter(x['c2'])}{x['r2']}"
                them_dong(cap + 1, f"Dải {n_o} ô: {sum(len(v) for v in mau.values())} công thức ({len(mau)} mẫu), {len(tay)} ô nhập tay",
                          rg, "", None, "Dải")
                if tay:
                    hd = sd.tieu_de(x["sh"], tay[0][0])
                    them_dong(cap + 2, f"{len(tay)} ô nhập tay trong dải  [{hd}]", rg, "", tong_tay, "Nhóm nhập tay",
                              self._nhom_goc(hd, "", x["sh"]))
                if len(mau) > 12:
                    raise LoiNghiepVu("VUOT_GIOI_HAN", "Dải truy vết vượt giới hạn 12 mẫu công thức.")
                for mm, cells in sorted(mau.items(), key=lambda kv: -len(kv[1])):
                    # đại diện: ô có giá trị lớn nhất (tránh dòng tiêu đề nhóm bằng 0)
                    cc, rr = max(cells, key=lambda o: abs(sd.v(x["sh"], o[0], o[1])) if la_so(sd.v(x["sh"], o[0], o[1])) else -1)
                    them_dong(cap + 2, f"Mẫu công thức áp dụng cho {len(cells)} ô, đại diện:", "", "", None, "Mẫu")
                    tham(x["sh"], cc, rr, cap + 3)

        tham(sh0, column_index_from_string(m.group(1)), int(m.group(2)), 0)
        self.kq["cay"], self.kq["dich"] = rows, dich
        la = [r for r in rows if r[5] in ("Nhập tay", "Nhóm nhập tay")]
        ngoai7 = [r for r in la if r[6] == NGOAI_NHOM]
        self.so_ngoai_nhom = len(ngoai7) if self.bo_nhom else None
        if ngoai7:
            self.them("Cao", "K7", ngoai7[0][2], f"Ô đích phụ thuộc {len(ngoai7)} nút nhập tay không thuộc bộ nhóm dữ liệu gốc "
                                                f"({', '.join(r[2] for r in ngoai7[:5])}...)", len(ngoai7),
                      tai_lieu="Yêu cầu nhà thầu giải trình nguồn")
        fn = [r for r in rows if r[5] == "File ngoài"]
        if fn:
            self.them("Cao", "K7", fn[0][2], f"Ô đích phụ thuộc {len(fn)} tham chiếu file ngoài", len(fn),
                      tai_lieu="File Excel đang được liên kết")


    def k8_nguon_kl(self):
        # Tránh mất chữ số khi nhân/cộng Decimal lớn; vẫn giữ round của nguồn.
        with localcontext() as ctx:
            do_dai = 28
            for ws in self.sd.wv.worksheets:
                for row in ws.iter_rows():
                    self._kiem_huy()
                    for c in row:
                        if la_so(c.value):
                            d = num(c.value)
                            do_dai = max(do_dai, len(d.as_tuple().digits) + abs(d.as_tuple().exponent))
            ctx.prec = do_dai * 2 + 16
            self._k8_nguon_kl()

    def _mo_ta_tien(self, ky_nay, luy_ke):
        ma = self.kq.get('tien_te')
        if not ma:
            return ": chưa rõ đơn vị tiền tệ."
        cau = f": GT lũy kế {luy_ke:,.0f} {ma}"
        return cau + (f", kỳ này {ky_nay:,.0f} {ma}" if ky_nay is not None else "")

    def _k8_nguon_kl(self):
        sd = self.sd
        try:
            bang = tim_bang_chi_tiet(sd.wv, self._kiem_huy)
        except LoiNghiepVu as loi:
            if loi.ma != "KHONG_TIM_THAY_BANG":
                raise
            self.kq["nguon"] = []
            self.them("Kiểm soát", "K8", "-", "Không nhận được bảng chi tiết KL × đơn giá.")
            return
        sh, cols = bang["sheet"], bang["cols"]
        cot_kl = cols.get("kl_lk") or cols.get("kl_kn")
        if not cot_kl:
            self.kq["nguon"] = []
            self.them("Kiểm soát", "K8", "-", "Bảng chưa có cột KL lũy kế hoặc kỳ này để kiểm nguồn.")
            return
        self.kq['tien_te'] = _tim_tien_te(sd.wv, bang, self._kiem_huy)
        out = []
        for it in bang["items"]:
            self._kiem_huy()
            if not it["dvt"]:
                continue
            nguon, duong, co = self._nguon(sh, cot_kl, it["dong"], it.get("kl_hd"))
            if cols.get("kl_kt") and (it.get("kl_kt") or 0):
                n_kt, d_kt, co_kt = self._nguon(sh, cols["kl_kt"], it["dong"], it.get("kl_hd"))
                n_kt = n_kt + (" (qua sheet ẩn)" if "qua sheet ẩn" in co_kt else "")
            else:
                n_kt = "0 / không có"
            dg = it.get("don_gia") or 0
            gt_kn = it.get("gt_kn") if it.get("gt_kn") is not None else (it.get("kl_kn") or 0) * dg
            gt_lk = it.get("gt_lk") if it.get("gt_lk") is not None else (it.get("kl_lk") or 0) * dg
            out.append([it["dong"], it["ten"][:80], it["dvt"], it.get("kl_hd"), it.get("kl_lk"), round(gt_kn or 0), round(gt_lk or 0),
                        nguon, "; ".join(co), " -> ".join(duong), it.get("kl_kt"), n_kt])
        self.kq.update(nguon=out, bang_sh=sh, cot_kl=get_column_letter(cot_kl) if cot_kl else "")
        tang = defaultdict(lambda: [0, Decimal(0), Decimal(0)])
        for x in out:
            self._kiem_huy()
            t = tang[x[7]]
            t[0] += 1
            t[1] += x[5]
            t[2] += x[6]
        self.kq["tang"] = sorted(([k] + v for k, v in tang.items()), key=lambda r: -r[3])
        chan = [x for x in out if "đang bị chặn" in x[8]]
        if chan:
            self.them("Trung bình", "K8", f"{sh}!{self.kq['cot_kl']}{chan[0][0]}",
                      f"{len(chan)} hạng mục có KL diễn giải vượt KL HĐ, đang bị công thức chặn về KL HĐ: phát sinh chưa xử lý, "
                      "BOQ sai hay diễn giải thổi phồng?", len(chan), tai_lieu="A04 hồ sơ phát sinh / B04 thay đổi thiết kế")
        kt_dem = Counter(x[11] for x in out if not x[11].startswith("0 /"))
        self.kq["tang_kt"] = [[k, n] for k, n in kt_dem.most_common()]
        for k, n in kt_dem.items():
            if k.startswith(("Nhập tay", "Tỷ lệ")) or "sheet ẩn" in k:
                self.them("Cao" if "Nhập tay" in k or "sheet ẩn" in k else "Trung bình", "K8", f"{sh}!{get_column_letter(cols['kl_kt'])}",
                          f"{n} hạng mục có KL kỳ trước nguồn '{k}'", n, tai_lieu="E01 hồ sơ đợt trước đã duyệt (đối chiếu từng hạng mục)")
        for k, n, gkn, glk in self.kq["tang"]:
            if k in ("Nhập tay", "Bằng KL HĐ", "Nguồn trống", "Link lệch dòng", "File ngoài") and n:
                self.them("Cao", "K8", f"{sh}!{self.kq['cot_kl']}", f"{n} hạng mục có KL lũy kế nguồn '{k}'" + self._mo_ta_tien(gkn, glk),
                          n, glk, {"Nhập tay": "Diễn giải KL, bản vẽ / hoàn công", "Bằng KL HĐ": "Hoàn công + BB nghiệm thu (không chấp nhận 'bằng KL HĐ')",
                                   "Nguồn trống": "Sửa liên kết, xác định nguồn", "Link lệch dòng": "Sửa liên kết, xác định nguồn",
                                   "File ngoài": "File Excel đang liên kết"}[k])
            elif k == "Tỷ lệ × KL HĐ" and n:
                self.them("Trung bình", "K8", f"{sh}!{self.kq['cot_kl']}", f"{n} hạng mục KL lũy kế = tỷ lệ % × KL HĐ (ước tính tiến độ)" + self._mo_ta_tien(None, glk),
                          n, glk, "Xác nhận % tiến độ của tư vấn giám sát")

    def _lech(self, sh, r, x):
        a, b = self.sd.nhan_dong(sh, r), self.sd.nhan_dong(x["sh"], x["r1"])
        g = giong(a, b)
        return bool(a) and len(a) >= 6 and (g is None or g < 0.6)

    def _nguon(self, sh, c, r, kl_hd, sau=0, duong=None, co=None):
        """Lần theo ô KL qua các tham chiếu 1 ô cho tới khi gặp công thức tính, số gõ tay, hoặc ô trống."""
        self._kiem_huy()
        sd = self.sd
        duong = (duong or []) + [f"{sh}!{get_column_letter(c)}{r}"]
        co = co or []
        if sd.an(sh) and "qua sheet ẩn" not in co:
            co.append("qua sheet ẩn")
        f = sd.f(sh, c, r)
        v = sd.v(sh, c, r)
        v = num(v) if _la_so_kl(v) else v
        bang_hd = lambda x: _la_so_kl(x) and _la_so_kl(kl_hd) and kl_hd and abs(num(x) - kl_hd) <= Decimal("0.000001") * max(1, abs(kl_hd))
        if f in (None, ""):
            return "Nguồn trống", duong, co
        if _la_so_kl(f):
            if bang_hd(f) and sau > 0:
                co.append("số gõ tay đúng bằng KL HĐ")
            return "Nhập tay", duong, co
        if not la_cong_thuc(f) or sau > 8:
            if la_cong_thuc(f) and sau > 8:
                raise LoiNghiepVu("VUOT_GIOI_HAN", "Đường truy nguồn KL vượt giới hạn 8 tầng.")
            return "Khác", duong, co
        refs = tach_tham_chieu(f, sh)
        if any(x["ngoai"] is not None for x in refs):
            return "File ngoài", duong, co
        don = [x for x in refs if x["c1"] == x["c2"] and x["r1"] == x["r2"]]
        body = bo_chuoi(f)
        chi_1_ref = len(refs) == 1 and len(don) == 1 and re.fullmatch(r"=\s*\+?\s*(?:'[^']+'|[^!=]+)?!?\$?[A-Z]{1,3}\$?\d+\s*", body)
        if chi_1_ref:
            x = don[0]
            if bang_hd(v) and x["sh"] in sd.wb.sheetnames and re.search(r"hop dong|\bhd\b", bo_dau(sd.tieu_de(x["sh"], x["c1"]))):
                return "Bằng KL HĐ", duong + [f"{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}"], co
            if x["sh"] != sh and self._lech(sh, r, x):
                return "Link lệch dòng", duong + [f"{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}"], co
            if x["sh"] in sd.wb.sheetnames:
                return self._nguon(x["sh"], x["c1"], x["r1"], kl_hd, sau + 1, duong, co)
            return "Nguồn trống", duong, co
        # tham chiếu 1 ô nhân hằng số: tỷ lệ x KL HĐ ?
        if len(don) == 1 and len(refs) == 1 and hang_so_nhung(f):
            if _la_so_kl(v) and _la_so_kl(kl_hd) and kl_hd and 0 < v / kl_hd < 1:
                return "Tỷ lệ × KL HĐ", duong, co
            return "Hệ số × ô khác", duong, co
        cong_tru = re.fullmatch(r"=\s*[+\-]?\s*X(\s*[+\-]\s*X)+\s*", LREF.sub("X", QREF.sub("X", body)))
        if cong_tru and len(don) == len(refs) >= 2:
            # lũy kế = kỳ trước + kỳ này, kỳ này = lũy kế - kỳ trước ...: đi theo thành phần 'lũy kế', rồi 'kỳ này'
            def uu_tien(x):
                t = bo_dau(sd.tieu_de(x["sh"], x["c1"])) if x["sh"] in sd.wb.sheetnames else ""
                return (0 if "luy ke" in t and "truoc" not in t else 1 if re.search(r"k[iy] nay", t) else 2)
            x = sorted(don, key=uu_tien)[0]
            co.append("cộng/trừ nhiều ô")
            if x["sh"] != sh and self._lech(sh, r, x):
                return "Link lệch dòng", duong + [f"{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}"], co
            return self._nguon(x["sh"], x["c1"], x["r1"], kl_hd, sau + 1, duong, co)
        if re.match(r"^=\s*(IF|MIN|MAX)\(", f, re.I):
            co.append("có IF/MIN/MAX")
            # đi theo nhánh thực sự cho ra giá trị (so giá trị đã lưu); ưu tiên tham chiếu sang sheet khác (nguồn diễn giải)
            ung = [x for x in don if x["sh"] in sd.wb.sheetnames]
            gia = lambda x: num(sd.v(x["sh"], x["c1"], x["r1"]))
            khop = [x for x in ung if _la_so_kl(gia(x)) and _la_so_kl(v) and abs(gia(x) - v) <= Decimal("0.000000001") * max(1, abs(v))]
            khop.sort(key=lambda x: x["sh"] == sh)
            dg = next((x for x in ung if x["sh"] != sh), None)
            if dg and self._lech(sh, r, dg):
                return "Link lệch dòng", duong + [f"{dg['sh']}!{get_column_letter(dg['c1'])}{dg['r1']}"], co
            if dg and _la_so_kl(gia(dg)) and _la_so_kl(kl_hd) and gia(dg) > kl_hd + Decimal("0.000000001") and bang_hd(v):
                co.append(f"diễn giải {gia(dg):g} > KL HĐ {kl_hd:g}, đang bị chặn về KL HĐ")
                x = dg
            else:
                x = (khop or ([dg] if dg else []) or ung or [None])[0]
            if x:
                if x["sh"] != sh and self._lech(sh, r, x):
                    return "Link lệch dòng", duong + [f"{x['sh']}!{get_column_letter(x['c1'])}{x['r1']}"], co
                return self._nguon(x["sh"], x["c1"], x["r1"], kl_hd, sau + 1, duong, co)
        if bang_hd(v) and len(refs) == 1:
            return "Bằng KL HĐ", duong, co
        return "Tính từ diễn giải / công thức", duong, co


    def _xep_lai(self):
        """File ngoài chỉ dùng ở cột phụ (không nằm trên cây truy vết số đề nghị) -> hạ mức."""
        cot_cay = set()
        for row in self.kq.get("cay", []):
            m = re.match(r"(.+)!([A-Z]+)\d+", str(row[2] or ""))
            if m:
                cot_cay.add((m.group(1), m.group(2)))
        if not cot_cay:
            return
        for x in self.ph:
            if x.get("_ngoai") and not (self._ngoai_o.get(x["_ngoai"], set()) & cot_cay):
                x["muc"] = "Trung bình"
                x["mo_ta"] += " | không nằm trên đường tính ra ô đích (cột phụ / kiểm tra)"
