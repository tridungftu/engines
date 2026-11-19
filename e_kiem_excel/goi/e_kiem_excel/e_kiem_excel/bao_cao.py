"""Báo cáo chuyển từ toan_ven.py 764–866; chỉ ghi trong RAM."""

from collections import Counter
from copy import deepcopy
from decimal import Decimal
from functools import partial
from io import BytesIO
import re
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter, column_index_from_string
from .chuan_hoa import bo_dau, num
from .doc_bang import _tim_tien_te
from kho_tri_thuc_sdk.engine import LoiNghiepVu


def _du_lieu_bao_cao(kt):
    """Bản sao để định dạng tiền không làm đổi kết quả kiểm/JSON."""
    k, sd = deepcopy(kt.kq), kt.sd
    tien_te = {}

    def don_vi(sh):
        if sh not in tien_te:
            ws = sd.wv[sh]
            bang = dict(sheet=sh, hdr=min(ws.max_row, 40),
                        cols={f'gt_{c}': c for c in range(1, ws.max_column + 1)},
                        items=[dict(dvt=True, dong=r) for r in range(1, ws.max_row + 1)])
            tien_te[sh] = _tim_tien_te(sd.wv, bang, kt._kiem_huy)
        return tien_te[sh]

    def tien(v, ma):
        return f'{format(num(v), "f")} {ma}' if v is not None and ma else None

    def gia_tri(v, sh, o):
        if isinstance(v, bool) or not isinstance(v, (int, float, Decimal)):
            return v
        m = re.match(r'([A-Z]+)([0-9]+)', o)
        if not m or sh not in sd.wv.sheetnames:
            return None  # không đủ căn cứ về loại số/đơn vị
        c, r = column_index_from_string(m[1]), int(m[2])
        nhan = bo_dau(sd.tieu_de(sh, c)) + ' ' + bo_dau(sd.nhan_dong(sh, r))
        fmt = sd.wv[sh].cell(r, c).number_format
        if (re.search(r'gia tri|don gia|thanh tien|so tien|thanh toan', nhan)
                or re.search(r'\[\$[A-Z]{3}(?:-[0-9A-Fa-f]+)?\]|"[A-Z]{3}"', fmt)):
            return tien(v, don_vi(sh))
        return format(v, 'f') if isinstance(v, Decimal) else v

    for ten, cot_o, cot_gt in [('lech', 1, 6), ('tay', 1, 4), ('lien_ket', 1, 9)]:
        for row in k.get(ten, []):
            kt._kiem_huy()
            row[cot_gt] = gia_tri(row[cot_gt], row[0], row[cot_o])
    for row in k.get('an_khac', []):
        row[4] = gia_tri(row[4], row[0], row[2])
        row[5] = gia_tri(row[5], row[1], row[2])
    for row in k.get('cay', []):
        kt._kiem_huy()
        if '!' in row[2] and row[5] != 'Tham số gõ cứng':
            sh, o = row[2].rsplit('!', 1)
            row[4] = gia_tri(row[4], sh, o)
    ma = k.get('tien_te')
    for row in k.get('nguon', []):
        row[5], row[6] = tien(row[5], ma), tien(row[6], ma)
    for row in k.get('tang', []):
        row[2], row[3] = tien(row[2], ma), tien(row[3], ma)
    ph = deepcopy(kt.ph)
    for p in ph:
        if p['kt'] == 'K8':
            p['gia_tri'] = tien(p['gia_tri'], ma)
    return k, ph

HF = PatternFill("solid", fgColor="1F4A7A")
HFONT = Font(name="Arial", bold=True, color="FFFFFF", size=10)
BASE = Font(name="Arial", size=10)
NOTE = Font(name="Arial", size=9, italic=True, color="6B6B6B")
TO = {"Cao": PatternFill("solid", fgColor="F8D7D3"), "Trung bình": PatternFill("solid", fgColor="FFF2CC"),
      "Kiểm soát": PatternFill("solid", fgColor="E3EBF5")}


def _sheet(wb, ten, tieu_de, cot, rong, dong, ghi=(), fmt=None, to_cot=None, kiem_huy=lambda: None):
    ws = wb.create_sheet(ten)
    ws.cell(1, 1, tieu_de).font = Font(name="Arial", size=12, bold=True)
    r = 2
    for g in ghi:
        ws.cell(r, 1, g).font = NOTE
        r += 1
    r += 1
    for j, h in enumerate(cot, 1):
        c = ws.cell(r, j, h)
        c.font, c.fill = HFONT, HF
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = rong[j - 1]
    ws.freeze_panes = ws.cell(r + 1, 1)
    for d in dong:
        kiem_huy()
        r += 1
        for j, v in enumerate(d, 1):
            if isinstance(v, str) and len(v) > 32767:
                raise LoiNghiepVu("VUOT_GIOI_HAN", "Nội dung một ô báo cáo vượt giới hạn Excel.")
            c = ws.cell(r, j, v)
            if isinstance(v, str) and v.startswith("="):
                c.data_type = "s"
            c.font = BASE
            if fmt and j in fmt:
                c.number_format = fmt[j]
        if to_cot is not None and d[to_cot] in TO:
            for j in range(1, len(d) + 1):
                ws.cell(r, j).fill = TO[d[to_cot]]
    if not dong:
        ws.cell(r + 1, 1, "(không có)").font = NOTE
    return ws


def ghi(kt):
    k, ph = _du_lieu_bao_cao(kt)
    tao_sheet = partial(_sheet, kiem_huy=kt._kiem_huy)
    wb = openpyxl.Workbook()
    try:
        wb.remove(wb.active)
        dem = Counter(x["muc"] for x in kt.ph)
        tao_sheet(wb, "Phat hien", "LỚP 1 - TÍNH TOÀN VẸN FILE EXCEL",
               ["#", "Mức", "Kiểm tra", "Vị trí", "Mô tả", "Số ô", "Giá trị liên quan", "Tài liệu / việc cần làm"],
               [4, 11, 8, 30, 90, 8, 18, 40],
               [[i + 1, x["muc"], x["kt"], x["o"], x["mo_ta"], x["so_o"], x["gia_tri"], x["tai_lieu"]] for i, x in enumerate(ph)],
               ghi=[f"Cao {dem['Cao']} · Trung bình {dem['Trung bình']} · Kiểm soát {dem['Kiểm soát']}.  "
                    "Cao = có thể làm sai số tiền; Trung bình = sai logic / thiếu căn cứ; Kiểm soát = lỗi cấu trúc file.",
                    "Chỉ đọc file, không tính lại bảng tổng hợp. Lớp 2 (đối chiếu hợp đồng, BOQ, phụ lục) và Lớp 3 (chứng từ) làm ở module khác."],
               fmt={7: "#,##0"}, to_cot=1)
        tao_sheet(wb, "K1 Tong quan", "K1 - Tổng quan workbook",
               ["Sheet", "Trạng thái", "Số dòng", "Số cột", "Công thức", "Số gõ tay", "Công thức #REF!", "Ô đang lỗi", "Công thức chưa có giá trị lưu"],
               [30, 11, 9, 8, 11, 11, 12, 10, 14], k.get("sheet", []),
               ghi=[f"Liên kết file ngoài: {len(k.get('ngoai', []))} (được công thức dùng: {sum(1 for x in k.get('ngoai', []) if x[2])}); "
                    f"tên định nghĩa lỗi #REF!: {k.get('ten_loi', 0)}"])
        tao_sheet(wb, "K1 File ngoai", "K1 - Liên kết file ngoài", ["#", "File", "Số công thức đang dùng"], [5, 120, 14], k.get("ngoai", []))
        tao_sheet(wb, "K2 Mau cot", "K2 - Mẫu công thức chính của từng cột",
               ["Sheet", "Cột", "Tiêu đề", "Công thức", "Không tính tổng", "Ô theo mẫu chính", "Tỷ lệ", "Số mẫu khác nhau", "Mẫu chính (ví dụ)"],
               [26, 6, 36, 10, 10, 10, 8, 10, 60], k.get("cot", []), fmt={7: "0%"},
               ghi=["Cột có mẫu chính (≥ 10 ô, ≥ 70%) mới xét lệch mẫu. Dòng tổng (SUM/SUBTOTAL) không xét."])
        tao_sheet(wb, "K2 Lech mau", "K2 - Ô công thức lệch mẫu chính của cột",
               ["Sheet", "Ô", "Tiêu đề cột", "Hạng mục", "Công thức ô này", "Công thức mẫu chính", "Giá trị"],
               [24, 8, 30, 44, 50, 50, 14], k.get("lech", []), fmt={7: "#,##0.###"})
        tao_sheet(wb, "K2 Go tay", "K2 - Số gõ tay nằm giữa cột công thức",
               ["Sheet", "Ô", "Tiêu đề cột", "Hạng mục", "Giá trị gõ tay", "Công thức mẫu của cột", "Nhóm dữ liệu gốc"],
               [24, 8, 30, 44, 14, 50, 26], k.get("tay", []), fmt={5: "#,##0.###"})
        tao_sheet(wb, "K3 Lien ket dong", "K3 - Liên kết sang sheet khác trỏ sai hạng mục",
               ["Sheet", "Ô", "Tiêu đề cột", "Hạng mục (dòng này)", "Công thức", "Trỏ tới", "Hạng mục (dòng đích)", "Độ giống", "Kết luận", "Giá trị"],
               [22, 8, 26, 40, 30, 22, 40, 8, 28, 14], k.get("lien_ket", []), fmt={10: "#,##0.###"},
               ghi=["So tên hạng mục ở dòng có công thức với tên ở dòng được trỏ tới (bỏ dấu). Độ giống < 0,6 hoặc dòng đích không có tên thì liệt kê."])
        tao_sheet(wb, "K4 Sheet an", "K4 - Sheet ẩn",
               ["Sheet ẩn", "Trạng thái", "Số dòng", "Công thức", "Bị sheet hiện tham chiếu (ô)", "Từ sheet", "Bản hiện cùng tên", "Số ô khác bản hiện"],
               [26, 11, 9, 10, 14, 40, 22, 12], k.get("an", []))
        tao_sheet(wb, "K4 Khac ban hien", "K4 - Khác biệt giữa sheet ẩn và sheet hiện cùng tên (tối đa 300 ô / cặp)",
               ["Sheet hiện", "Sheet ẩn", "Ô", "Hạng mục", "Giá trị bản hiện", "Giá trị bản ẩn"], [22, 22, 8, 50, 18, 18], k.get("an_khac", []))
        tao_sheet(wb, "K5 So dang chu", "K5 - Số lưu dạng chữ", ["Sheet", "Ô", "Tiêu đề cột", "Hạng mục", "Nội dung"], [24, 8, 30, 50, 14],
               k.get("chu", []))
        tao_sheet(wb, "K6 Hang so", "K6 - Hằng số gõ cứng trong công thức (nhân / chia)",
               ["Hằng số", "Loại", "Số công thức", "Trong cột thuộc cây truy vết", "Ví dụ ô", "Công thức ví dụ"], [10, 22, 12, 14, 70, 60],
               k.get("nhung", []),
               ghi=["Hằng số kiểu thuế suất, tỷ lệ nằm trên đường tính ra số đề nghị thanh toán phải khớp điều khoản hợp đồng (Lớp 2) "
                    "và nên nằm ở ô tham số riêng. Hằng số kích thước trong diễn giải KL chỉ liệt kê."])
        tao_sheet(wb, "K7 Cay truy vet", f"K7 - Cây truy vết từ {k.get('dich') or '(không có ô đích)'}",
               ["Cấp", "Thành phần", "Ô", "Công thức", "Giá trị", "Loại nút", "Nhóm dữ liệu gốc", "Tài liệu chứng minh", "Ghi chú"],
               [5, 70, 26, 50, 16, 14, 26, 34, 18], k.get("cay", []), fmt={5: "#,##0.###"},
               ghi=["Số đề nghị thanh toán = dữ liệu nào x dữ liệu nào. Dải nhiều ô: phân rã một ô đại diện cho mỗi mẫu công thức.",
                    "Có bộ nhóm: lá nhập tay được phân theo bộ đã truyền; không có bộ nhóm: Chưa phân nhóm."])
        if kt.tham_so.get('kiem_nguon_kl', False):
            tao_sheet(wb, "K8 Nguon KL", f"K8 - Nguồn KL lũy kế từng hạng mục (bảng {k.get('bang_sh', '?')}, cột {k.get('cot_kl', '?')})",
                        ["Nhóm nguồn", "Số hạng mục", "GT kỳ này", "GT lũy kế"], [34, 12, 18, 18], k.get("tang", []), fmt={3: "#,##0", 4: "#,##0"},
                        ghi=["Dùng cho chọn mẫu (bước 5): nhóm 'Nhập tay', 'Bằng KL HĐ', 'Nguồn trống', 'Link lệch dòng' rủi ro cao."])
            tao_sheet(wb, "K8 Tung dong", "K8 - Nguồn KL từng hạng mục",
                   ["Dòng", "Hạng mục", "ĐVT", "KL HĐ", "KL lũy kế", "GT kỳ này", "GT lũy kế", "Nguồn KL lũy kế", "Lưu ý", "Đường đi",
                    "KL kỳ trước", "Nguồn KL kỳ trước"],
                   [7, 50, 8, 12, 12, 16, 16, 26, 26, 70, 12, 26], k.get("nguon", []),
                   fmt={4: "#,##0.###", 5: "#,##0.###", 6: "#,##0", 7: "#,##0", 11: "#,##0.###"})
            tao_sheet(wb, "K8 Nguon ky truoc", "K8 - Nguồn KL kỳ trước (số hạng mục có KL kỳ trước)", ["Nguồn", "Số hạng mục"], [40, 12],
                   k.get("tang_kt", []))
        kt._kiem_huy()
        out = BytesIO()
        wb.save(out)
        kt._kiem_huy()
        return out.getvalue()
    finally:
        wb.close()

