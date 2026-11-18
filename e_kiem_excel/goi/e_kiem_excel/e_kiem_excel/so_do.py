"""Mô hình hai workbook trong RAM, không mở nguồn liên kết ngoài."""

from collections import Counter
from io import BytesIO
import re
import openpyxl
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from .chuan_hoa import nfc, bo_dau

class SoDo:
    def __init__(self, du_lieu):
        self.wb = self.wv = None
        try:
            self.wb = openpyxl.load_workbook(BytesIO(du_lieu), data_only=False, keep_vba=False)
            self.wv = openpyxl.load_workbook(BytesIO(du_lieu), data_only=True, keep_vba=False)
            if not self.wb.worksheets:
                raise ValueError("Không có sheet.")
            self.ngoai = {}
            for i, lk in enumerate(self.wb._external_links, 1):
                dich = str(lk.file_link.Target if lk.file_link else "?")
                self.ngoai[i] = re.split(r"[\\/]", dich.split("?")[0].split("#")[0])[-1] or "?"
            self._cot_ten, self._hdr, self._merged = {}, {}, {}
        except Exception:
            self.dong()
            raise LoiNghiepVu("TEP_HONG", "Không đọc được tệp Excel. Anh hãy kiểm tra và lưu lại tệp.") from None

    def dong(self):
        for wb in (self.wb, self.wv):
            if wb is not None:
                wb.close()

    # ---------------------------------------------------------- truy cập ô
    def f(self, sh, c, r):
        try:
            return self.wb[sh].cell(r, c).value
        except KeyError:
            return None

    def v(self, sh, c, r):
        try:
            return self.wv[sh].cell(r, c).value
        except KeyError:
            return None

    def an(self, sh):
        return sh in self.wb.sheetnames and self.wb[sh].sheet_state != "visible"

    # ---------------------------------------------------------- tên dòng, tên cột
    def cot_ten(self, sh):
        """Cột chứa tên hạng mục: cột (trong 10 cột đầu) có nhiều ô chữ dài nhất."""
        if sh not in self._cot_ten:
            ws = self.wv[sh]
            dem = Counter()
            for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 3000), max_col=min(ws.max_column, 10)):
                for c in row:
                    if isinstance(c.value, str) and len(c.value.strip()) >= 8 and re.search(r"[A-Za-zÀ-ỹ]{3}", c.value):
                        dem[c.column] += 1
            self._cot_ten[sh] = dem.most_common(1)[0][0] if dem else 2
        return self._cot_ten[sh]

    def nhan_dong(self, sh, r):
        if sh not in self.wv.sheetnames:
            return ""
        v = self.v(sh, self.cot_ten(sh), r)
        return re.sub(r"\s+", " ", nfc(v)).strip()[:120] if v not in (None, "") else ""

    def _gop(self, sh):
        if sh not in self._merged:
            m = {}
            for rg in self.wb[sh].merged_cells.ranges:
                if rg.min_row > 60:
                    continue
                for rr in range(rg.min_row, rg.max_row + 1):
                    for cc in range(rg.min_col, rg.max_col + 1):
                        m[(rr, cc)] = (rg.min_row, rg.min_col)
            self._merged[sh] = m
        return self._merged[sh]

    def tieu_de(self, sh, c):
        """Tên cột: dòng tiêu đề (dòng có nhiều ô chữ nhất trong 40 dòng đầu) + 2 dòng dưới, có xử lý ô gộp."""
        if sh not in self._hdr:
            ws = self.wv[sh]
            best, h = (0, 0), 1
            kw = re.compile(r"^(stt|tt\b|ten|noi dung|hang muc|dien giai|don vi|dvt|khoi luong|kl\b|don gia|thanh tien|"
                            r"gia tri|ghi chu|ma hieu|so luong|luy ke|k[iy] nay|k[iy] truoc)")
            for r in range(1, min(ws.max_row, 40) + 1):
                cells = [ws.cell(r, cc).value for cc in range(1, min(ws.max_column, 40) + 1)]
                txt = [bo_dau(v) for v in cells if isinstance(v, str) and len(v.strip()) >= 2]
                diem = (sum(1 for t in txt if kw.match(t)), len(txt))
                if diem > best:
                    best, h = diem, r
            self._hdr[sh] = h
        h, m = self._hdr[sh], self._gop(sh)
        ws = self.wv[sh]
        out = []
        for r in range(max(1, h - 3), h + 4):
            # bỏ dòng thông tin chung (1 ô chữ gộp ngang cả bảng)
            n_chu = sum(1 for cc_ in range(1, min(ws.max_column, 30) + 1)
                        if isinstance(ws.cell(r, cc_).value, str) and ws.cell(r, cc_).value.strip())
            if r != h and n_chu < 2:
                continue
            rr, cc = m.get((r, c), (r, c))
            v = self.v(sh, cc, rr)
            if isinstance(v, str) and v.strip() and not re.fullmatch(r"[\[\(]?\d+[\]\)]?", v.strip()):
                t = re.sub(r"\s+", " ", v).strip()
                if t not in out:
                    out.append(t)
        return " / ".join(out)[:100]


