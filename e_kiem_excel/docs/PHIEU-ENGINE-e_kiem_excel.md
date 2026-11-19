# Phiếu engine — `e_kiem_excel` (Kiểm và đọc file Excel)

*Lập 16/11/2026 theo yêu cầu của Anh Dũng, để lead Claude lập phiếu giao Codex trong repo `engines`. **Trạng thái: ĐÃ DUYỆT TIẾN HÀNH 16/11/2026.** Anh đồng ý triển khai; Q1–Q3 (§9) áp phương án đề xuất. Bản này đã có 9 chỉnh sửa của lead sau khi đối chiếu SDK 2.2.0 và mã gốc, liệt kê ở cuối phiếu (Phụ lục C).*

*Căn cứ đã đọc: `engines/AGENTS.md`; SDK 2.2.0 (`HUONG-DAN-VIET-ENGINE.md`, `MAU-PHIEU-ENGINE.md`, `API-CORE-v1.md`); `_chung/docs/LOAI-DU-LIEU-RIENG.md`; mã gốc `review_xaydung/toan_ven.py` (887 dòng) và `review_xaydung/master_hd.py` (phần đọc bảng); `review_xaydung/quy-trinh-review-ttkl.md` v2.5 mục 10–11; repo `phan_mem_core` (cửa Nhập Excel `core/nhap_excel.py`). Phiếu này thay tên `e_excel_ho_so` ghi trong bản thiết kế module Review TTKL.*

---

## 1. Kết luận

- **Engine mới `e_kiem_excel`, 2 năng lực, chỉ dùng loại gốc** (`tep` vào, `truong` ra). Không cần loại dữ liệu riêng, không cần ngăn, không SQL, không mạng:
  - `excel.toan_ven@1`: Lớp 1, kiểm tính toàn vẹn của một file Excel bất kỳ (K1–K8).
  - `excel.doc_bang@1`: đọc bảng nhiều tầng tiêu đề ra dữ liệu chuẩn.
- **Engine dùng chung cho mọi module, không gắn riêng xây dựng.** Hai chỗ đang viết cứng cho thanh toán khối lượng chuyển thành **Cài đặt bước** để module tự truyền:
  - ô đích và danh mục nhóm dữ liệu gốc của K7;
  - khuôn cột của `doc_bang`.
  - Bộ "7 nhóm dữ liệu gốc" của Review TTKL ở Phụ lục A thuộc **module**, không nằm trong engine (cùng nguyên tắc với bộ tham số của `e_trich_xuat`).
- **Tận dụng mã có sẵn, không viết lại:**
  - lõi `toan_ven.py` (lớp `SoDo`, `KiemTra`, các hàm tách tham chiếu, mẫu công thức, ghi báo cáo);
  - 6 hàm của `master_hd.py`: `nfc`, `bo_dau`, `num`, `tim_bang_chi_tiet`, `khoa`, `tim_so_tong_hop`.
  - Phần còn lại của `master_hd.py` (trích hợp đồng) và `hardcode_audit.py` **không chuyển**.
- **Cần thư viện `openpyxl`** (kèm `et_xmlfile`) và **`defusedxml`**:
  - `toan_ven.py` dựa trên `openpyxl` để đọc cả công thức lẫn giá trị đã lưu;
  - `openpyxl` chỉ chống được tấn công qua XML (thực thể lồng nhau nở to) khi có `defusedxml`; có thì nó tự dùng.
  - Ghim trong `requirements.lock`, ghi `NGUON.md`, giống cách `e_ocr` ghim `pdfplumber`. Q1 áp phương án (a).
- **Ba sửa bắt buộc khi chuyển mã:**
  - tiền dùng `Decimal` và luôn kèm đơn vị, thay `float` và định dạng `:,.0f`;
  - không ghi tệp ra đĩa, dùng tệp trong RAM rồi `viec.tai_tep_ra`;
  - câu lỗi tiếng Việt qua `LoiNghiepVu`, không lộ đường dẫn hay tên tệp.
- **Giờ công: 29 giờ, ƯỚC TÍNH của lead, chưa đo** (§8; lệnh giao từng lát ở `GIAO-CODEX-e_kiem_excel.md`).

## 2. Phạm vi

| Làm | Không làm |
|---|---|
| Đọc `.xlsx`, `.xlsm` (không chạy macro) | `.xls` cũ, `.ods`, `.csv`: từ chối bằng câu tiếng Việt, không chuyển đổi ngầm |
| Kiểm K1–K8, dựng cây truy vết, xếp ô nhập tay vào nhóm do module truyền | Đối chiếu với hợp đồng, BOQ, phụ lục (Lớp 2): module làm bằng dữ liệu trong CSDL của nó |
| Đọc bảng nhiều tầng tiêu đề, gộp ô, dòng nhóm, dừng ở dòng "Cộng" | Bảng sạch một dòng tiêu đề: đã có cửa Nhập Excel chung của Core (`nhap_excel.py`, ≤ 2 MiB, ≤ 10.000 dòng, ≤ 100 cột) |
| Trả số đếm, cờ, tệp báo cáo Excel và tệp JSON chi tiết | Tính lại bảng tổng hợp, sửa file, mở file ngoài được liên kết |
| Báo tiền tệ "chưa rõ" khi file không ghi đơn vị | Tự gán VND |

## 3. Nguồn mã và cách chuyển

Ba repo, ghim theo commit đã đọc ngày 16/11/2026. Số dòng tính theo đúng commit này; commit khác thì số dòng có thể lệch, Codex đối chiếu lại bằng tên hàm và SHA-256 tệp.

| Repo | Commit | Vai trò |
|---|---|---|
| [`tridungftu/review_xaydung`](https://github.com/tridungftu/review_xaydung) — bản trên máy Anh: `D:\Claude\Ho tro review ho so xay dung\review_xaydung` | `1bed645ed56a36a59995afe1617af9dec83b8d82` (05/10/2026) | **Nguồn mã chính** để chuyển vào engine |
| [`tridungftu/engines`](https://github.com/tridungftu/engines) | `0e759eff098979891720c8a057c6a5fd03b25ddb` (16/11/2026) | Nơi đặt engine mới; **mẫu khung gói, test, ghim nguồn** từ engine đã có |
| [`tridungftu/phan_mem_core`](https://github.com/tridungftu/phan_mem_core) (riêng tư) | `ed3bad4a4ce03098d950e9ed115cb88644f85309` (16/11/2026) | Chỉ tham khảo cách đọc .xlsx bằng thư viện chuẩn; **engine không được import** `kho_tri_thuc.*` (`AGENTS.md` §4.1) |

### 3.1 Từ `review_xaydung/toan_ven.py`

887 dòng, SHA-256 `a97396de2be4cecfb060cd52689f4eec648f7904a7fd132089e10e3c897f6023`.

| Dòng | Đoạn mã | Vào tệp của gói `goi/e_kiem_excel/e_kiem_excel/` | Sửa khi chuyển |
|---|---|---|---|
| 42–50 | Hằng `LOI`, `QREF`, `LREF`, `CHUOI`, `SO_NHUNG`, `MUC` | `tham_chieu.py` | Giữ nguyên |
| 54–142 | Lớp `SoDo`: `__init__` (55), `f` (65), `v` (71), `an` (77), `cot_ten` (81), `nhan_dong` (93), `_gop` (99), `tieu_de` (111) | `so_do.py` | `__init__` nạp từ bytes (`BytesIO`) thay đường dẫn; `self.ngoai` (dòng 59–61) chỉ giữ tên tệp, bỏ thư mục |
| 144–229 | Hàm `bo_chuoi` (144), `tach_tham_chieu` (148), `mau_cong_thuc` (167), `la_tong` (193), `hang_so_nhung` (197), `la_so` (213), `la_cong_thuc` (217), `giong` (221) | `tham_chieu.py` | Giữ nguyên |
| 231–260 | `nhom_goc`, `TAI_LIEU` (7 nhóm viết cứng) | **Không vào engine** | Thành dữ liệu module, Phụ lục A |
| 262–272 | `KiemTra.__init__`, `them` | `kiem_tra.py` | `__init__` nhận `SoDo` đã dựng + tham số bước |
| 273–330 | `k1_tong_quan` | `kiem_tra.py` | Giữ nguyên; thêm `viec.kiem_huy()` cuối hàm |
| 331–383 | `k2_ban_do_cong_thuc` | `kiem_tra.py` | Giữ nguyên |
| 384–424 | `k3_lien_ket_dong` | `kiem_tra.py` | Giữ nguyên |
| 425–463 | `k4_sheet_an` | `kiem_tra.py` | Giữ nguyên |
| 464–484 | `k5_so_dang_chu` | `kiem_tra.py` | Giữ nguyên |
| 485–515 | `k6_tham_so_nhung` | `kiem_tra.py` | Bỏ câu có chữ "HĐ" viết cứng trong `mo_ta`/`tai_lieu`, lấy tài liệu từ `bo_nhom_json` khi có |
| 516–604 | `k7_cay_truy_vet` | `kiem_tra.py` | Ô đích: `o_dich` → tự tìm theo `nhan_o_dich_json` (thay chỗ gọi `tim_so_tong_hop` dòng 520); phân nhóm lá: thay `nhom_goc` bằng bộ so từ khóa đọc `bo_nhom_json` (§4.1.1) |
| 605–736 | `k8_nguon_kl` (605), `_lech` (659), `_nguon` (664) | `kiem_tra.py` | Chỉ chạy khi `kiem_nguon_kl` = `true`; gọi `doc_bang.tim_bang_chi_tiet` mới |
| 737–762 | `chay`, `_xep_lai` | `kiem_tra.py` | `chay` gọi K8 có điều kiện; trả dict cho `tep_json` |
| 764–866 | Kiểu ô `HF`…`TO`, `_sheet` (772), `ghi` (803) | `bao_cao.py` | Ghi vào `BytesIO`; số tiền kèm đơn vị hoặc để trống khi chưa rõ |
| 867–887 | `main` (argparse) | Không chuyển | Thay bằng `chay.py` theo SDK |

Dòng 40 của tệp gốc `from master_hd import bo_dau, nfc, num, tim_bang_chi_tiet, tim_so_tong_hop` đổi thành import từ `chuan_hoa.py` và `doc_bang.py` trong gói. **Không chép nguyên `master_hd.py` vào gói**: tệp này import `urllib.request`, `subprocess` (dòng 30, 34) cho phần gọi AI và chuyển `.doc`, trái quy tắc engine không gọi mạng.

### 3.2 Từ `review_xaydung/master_hd.py`

1234 dòng, SHA-256 `7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124`. `app_kiem_tra_ho_so/master_hd.py` là bản trùng y hệt (cùng SHA); chỉ lấy một bản.

| Dòng | Đoạn mã | Vào tệp | Sửa khi chuyển |
|---|---|---|---|
| 43–72 | `nfc` (43), `bo_dau` (47), `so` (54), `num` (62) | `chuan_hoa.py` | `num` trả `Decimal`, không `float` |
| 629–728 | `_hdr_text` (629), `tim_bang_chi_tiet` (633), `khoa` (724) | `doc_bang.py` | Thành khuôn `xay_dung_klgt`; `RuntimeError` (dòng 705) đổi thành `LoiNghiepVu("KHONG_TIM_THAY_BANG", …)`; giữ nguyên công thức `khoa` |
| 730–765 | `LABELS` (730), `tim_so_tong_hop` (741) | `doc_bang.py` | Số dạng `Decimal`; không lọc `abs(v) > 1` bằng `float` |
| 74–627 | Đọc/trích hợp đồng, quy tắc, gọi AI, chấm điểm | **Không lấy** | Đã có `e_trich_xuat` + `e_hoi_ai` |
| 767–1132 | Ghi/đọc master, `nap_dot` (974), `doi_chieu` (1029) | **Không lấy cho engine** | Là logic Lớp 2: tham khảo khi viết hành động `kiem_dot` của module `review_ttkl` |
| 1134–1234 | `main` (CLI) | Không lấy | |

Không dùng `hardcode_audit.py` (cả bản gốc và bản trùng trong `app_kiem_tra_ho_so/`): quy trình v2.5 mục 10 đã ghi `toan_ven.py` thay thế.

### 3.3 Mẫu khung lấy từ repo `engines` (commit `0e759ef`)

| Tệp | Dùng để | Ghi chú |
|---|---|---|
| `docs/goi-gui-engine/sdk-2.2.0/engine-demo/e_demo_doc_tep/` (`chay.py` 31 dòng, `engine.json`) | Khung tối thiểu engine nhận `tep` | Điểm xuất phát của EX-0 |
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/chay.py` (115 dòng): lớp `CongHoaDon(Engine)` dòng 15–29, `doc_hoa_don` dòng 30–71 | Mẫu `tep` → `truong` + tải tệp JSON kết quả bằng `viec.tai_tep_ra`, bọc lỗi không lộ traceback | Gần nhất với `e_kiem_excel` |
| `e_hoa_don/goi/e_hoa_don/requirements.lock`, `NGUON.md` (181 dòng) | Mẫu ghim thư viện có băm và ghi nguồn | Ghim `openpyxl`, `et_xmlfile` theo cùng cách |
| `e_ocr/goi/e_ocr/requirements.lock` | Mẫu ghim thư viện ngoài (`pdfplumber`, `Pillow`…) | Cách engine đã được duyệt dùng thư viện ngoài |
| `e_hoa_don/tests/kiem_doc_lap.py` (221 dòng), `conftest.py` (42), `kiem_may_sach.sh`, `KIEM-MAY-SACH.cmd`, `tests/demo/bam-fixture.json` | Kiểm độc lập, kiểm máy sạch, ghi băm fixture DEMO | Dùng cho §7 và EX-6 |
| `_chung/cong-cu/dong_goi.py` (238 dòng) | Đóng gói gói engine từ bytes trong git | Dùng ở EX-6 |
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/xlsx_mini.py` (112 dòng), `e_hoa_don/goi/e_hoa_don/e_hoa_don/xlsx_toi_thieu.py` (93 dòng) | Ghi .xlsx trong RAM chỉ bằng thư viện chuẩn | Chỉ tham khảo. Lead đã kiểm: `kho_tri_thuc_sdk/xlsx_mini.write_xlsx` dùng `zipfile.ZipFile(path, "w")` nên nhận được `BytesIO`, nhưng chỉ có vài kiểu ô. **Báo cáo `tep_bao_cao` ghi bằng `openpyxl` vào `BytesIO`** để giữ nguyên định dạng của `toan_ven.ghi` (đã ghim `openpyxl`) |
| `AGENTS.md` | Quy tắc cứng, cách làm lát, báo cáo PR | Bắt buộc đọc trước |

### 3.4 Tham khảo trong `phan_mem_core` (commit `ed3bad4`, chỉ đọc)

| Tệp | Đoạn | Dùng để |
|---|---|---|
| `src/kho_tri_thuc/core/nhap_excel.py` (426 dòng) | Trần `GIOI_HAN_NHAP_*` (dòng 23–25), `_doc_xlsx_nhap` (132–208), `_gia_tri_o` (92–122), `_ngay_excel` (77–91), `_kiem_tep` (209–216) | Cách Core đọc .xlsx bằng thư viện chuẩn và chặn tệp hỏng/bom nén. **Chỉ đọc giá trị, không đọc công thức**, nên không thay được `openpyxl` cho K2/K7. Muốn dùng thì chép lại có ghi nguồn, không import |

Mã gốc giữ nguyên trong các repo trên, không sửa, không xóa. Nếu repo `engines` cần bản tham chiếu thì chép `toan_ven.py`, `master_hd.py` vào `e_kiem_excel/ma-nguon/` (chỉ đọc), ghi commit và SHA-256 như trên trong `NGUON.md`.

## 4. Năng lực

### 4.1 `excel.toan_ven@1` — Kiểm tính toàn vẹn file Excel

- **Nhận:** `tep`, mime `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` và `application/vnd.ms-excel.sheet.macroEnabled.12`.
- **Trả:** `truong`.
- **`huy_duoc`:** `true`. Gọi `viec.kiem_huy()` giữa các kiểm tra K1…K8.

**Tám kiểm tra (giữ nguyên ý nghĩa và mức cờ của `toan_ven.py`):**

| Mã | Kiểm | Mức khi có phát hiện | Dùng chung mọi module? |
|---|---|---|---|
| K1 | Sheet ẩn; liên kết file ngoài, tách loại công thức đang dùng và loại chỉ còn trong tên định nghĩa; ô lỗi (#REF!, #DIV/0!…); công thức chưa có giá trị lưu | Cao nếu file ngoài nằm trên đường tính ô đích; Trung bình nếu ở cột phụ | Có |
| K2 | Mẫu công thức chính từng cột (chuẩn hóa kiểu R1C1); ô lệch mẫu; **số gõ tay giữa cột công thức** | Cao (gõ tay), Trung bình (lệch mẫu) | Có |
| K3 | Công thức trỏ sang sheet khác có trỏ đúng dòng không (so tên dòng hai đầu; chỉ cặp sheet liên kết có hệ thống, bỏ dòng tổng) | Cao | Có, với bảng có cột tên dòng |
| K4 | Sheet ẩn bị sheet hiện tham chiếu bao nhiêu ô; khác gì sheet hiện cùng tên | Trung bình | Có |
| K5 | Số lưu dạng chữ | Trung bình | Có |
| K6 | Hằng số gõ cứng trong công thức (×1,08; ×60%…), chỉ báo khi nằm trên cột thuộc cây truy vết | Trung bình | Có |
| K7 | Cây truy vết: ô đích = dữ liệu nào × dữ liệu nào; mỗi ô nhập tay xếp vào một nhóm của danh mục; ô "Ngoài nhóm" là cờ | Cao | Có, khi module truyền ô đích + danh mục |
| K8 | Nguồn KL lũy kế / kỳ trước từng hạng mục: từ diễn giải, nhập tay, bằng KL HĐ, tỷ lệ × KL HĐ, link lệch dòng, trống, qua sheet ẩn | Cao / Trung bình | Không: riêng hồ sơ khối lượng, bật bằng tham số |

**Cài đặt bước (`tham_so`):**

| `ma` | `kieu` | Bắt buộc | Mặc định | Ý nghĩa |
|---|---|---|---|---|
| `o_dich` | `van_ban` | Không | trống | Ô đích của K7 dạng `Sheet!D38`. Trống thì engine tự tìm theo `nhan_o_dich_json` |
| `nhan_o_dich_json` | `van_ban` (`toi_da` 4096) | Không | trống | Danh sách cụm từ (bỏ dấu) để tự tìm ô đích, ví dụ `["gia tri de nghi thanh toan ky nay"]`. Cả hai trống → K7 báo mức "Kiểm soát": không có ô đích |
| `bo_nhom_json` | `van_ban` (`toi_da` 32768) | Không | trống | Danh mục nhóm dữ liệu gốc theo §4.1.1. Trống → K7 vẫn dựng cây, lá ghi "Chưa phân nhóm", không bật cờ "Ngoài nhóm" |
| `kiem_nguon_kl` | `co_khong` | Không | `false` | Bật K8 (cần bảng có cột KL, đơn giá; dùng khuôn `xay_dung_klgt` của §4.2) |

#### 4.1.1 Định dạng `bo_nhom_json`

Dùng **danh sách từ khóa**, không nhận biểu thức chính quy từ tham số (tránh biểu thức chạy treo). Xét theo thứ tự; nhóm đầu tiên khớp thì dừng.

```json
{"phien_ban": 1, "ten_bo": "…", "nhom": [
  {"ma": "…", "ten": "…", "tai_lieu": "Tài liệu gốc cần đối chiếu",
   "khi": [ {"vung": ["tieu_de_cot", "ten_sheet", "nhan_dong"],
             "tat_ca": [["tu khoa a", "=tu"], ["tu khoa b"]],
             "khong_co": ["tu khoa c"]} ]}
]}
```

- `khi`: danh sách điều kiện; nhóm khớp nếu **một** điều kiện khớp.
- `vung`: chữ dùng để so, đã bỏ dấu, viết thường, gộp khoảng trắng:
  - `tieu_de_cot`: tiêu đề cột của ô;
  - `ten_sheet`: tên sheet;
  - `nhan_dong`: tên dòng hoặc nhãn bên trái ô.
- `tat_ca`: mọi danh sách con đều phải có ít nhất một từ khóa xuất hiện. Từ khóa thường = **chứa chuỗi** (đúng như `nhom_goc` gốc). `=tu` = **khớp nguyên từ**. `#` trong từ khóa = một hoặc nhiều chữ số (ví dụ `dot #`).
- `khong_co`: không được chứa từ khóa nào trong danh sách.
- Trần đề xuất: ≤ 30 nhóm, ≤ 200 từ khóa, ≤ 32 KiB. Vượt trần hoặc sai cấu trúc → `THAM_SO_KHONG_HOP_LE`.

**`truong_ra`:**

| `ma` | `ten` | `kieu` | Ghi chú |
|---|---|---|---|
| `so_co_cao` | Số cờ mức Cao | `so` | |
| `so_co_trung_binh` | Số cờ mức Trung bình | `so` | |
| `so_kiem_soat` | Số mục cần kiểm soát | `so` | Ví dụ không tìm được ô đích |
| `so_ngoai_nhom` | Số ô nhập tay ngoài nhóm | `so` | `null` khi không có `bo_nhom_json` |
| `o_dich` | Ô đích đã dùng | `van_ban` | `null` khi không có |
| `da_tinh_lai` | File đã tính lại | `co_khong` | `false` khi có công thức chưa có giá trị lưu |
| `co_lien_ket_ngoai` | Có liên kết file ngoài đang dùng | `co_khong` | |
| `tep_bao_cao` | Báo cáo Lớp 1 (Excel) | `tep` | Các sheet "Phat hien", "K1 Tong quan" … "K8 Nguon ky truoc" như `toan_ven.py` |
| `tep_json` | Kết quả chi tiết (JSON) | `tep` | §5.1 |
| `bam_dau_vao` | Mã băm tệp vào | `van_ban` | `sha256:<64 hex>` của bytes tệp |
| `phien_ban_engine` | Phiên bản engine | `van_ban` | Ví dụ `e_kiem_excel 0.1.0` |

### 4.2 `excel.doc_bang@1` — Đọc bảng nhiều tầng tiêu đề

- **Nhận:** `tep` cùng mime như §4.1.
- **Trả:** `truong`.
- **`huy_duoc`:** `true`.

**Cài đặt bước:**

| `ma` | `kieu` | Bắt buộc | Mặc định | Ý nghĩa |
|---|---|---|---|---|
| `khuon` | `chon`, `lua_chon`: `xay_dung_klgt` (Bảng khối lượng xây dựng), `tong_quat` (Bảng theo khuôn cột) | Có | `xay_dung_klgt` | `xay_dung_klgt` = logic `tim_bang_chi_tiet` + `tim_so_tong_hop` hiện có (bảng KL × đơn giá: HĐ, kỳ trước, kỳ này, lũy kế; số tổng hợp: GT HĐ, lũy kế, giữ lại, thu hồi tạm ứng, đề nghị kỳ này). `tong_quat` = đọc theo `khuon_cot_json` |
| `khuon_cot_json` | `van_ban` (`toi_da` 32768) | Khi `khuon` = `tong_quat` | trống | `{"phien_ban":1,"cot":[{"ma":"…","tu_khoa":["…"],"bat_buoc":true,"kieu":"van_ban|so|so_tien|ngay"}],"dong_dung":["cong","tong cong"]}`. Cùng quy tắc từ khóa như §4.1.1 |
| `tien_te` | `van_ban` (`toi_da` 3) | Không | trống | Mã ISO 3 chữ in hoa (VND, USD…), sai dạng → `THAM_SO_KHONG_HOP_LE`. Do quy trình hoặc module truyền. Trống và file không ghi đơn vị → mọi số tiền trả `null`, `tien_te_chua_ro` = `true` |

Khuôn `xay_dung_klgt` là **kiến thức về mẫu bảng**, giống `e_hoa_don` biết cấu trúc XML. Engine không biết hợp đồng nào; khuôn chỉ quyết định cách đọc cột. Thêm khuôn mới cho mảng khác = thêm lựa chọn `chon`, tăng phiên bản gói, không đổi năng lực.

**`truong_ra`:**

| `ma` | `ten` | `kieu` | Ghi chú |
|---|---|---|---|
| `tep_json` | Bảng đã đọc (JSON) | `tep` | §5.2 |
| `sheet` | Sheet chứa bảng | `van_ban` | |
| `dong_tieu_de` | Dòng tiêu đề | `so` | |
| `so_dong` | Số dòng dữ liệu | `so` | Dòng có đơn vị tính (khuôn `xay_dung_klgt`) hoặc đủ cột bắt buộc (khuôn `tong_quat`) |
| `so_dong_nhom` | Số dòng tiêu đề nhóm | `so` | |
| `so_canh_bao` | Số cảnh báo | `so` | Ví dụ thành tiền ≠ KL × đơn giá, ô số dạng chữ, dòng trùng khóa |
| `gia_tri_hop_dong` | Giá trị hợp đồng | `so_tien` | Chỉ khuôn `xay_dung_klgt`; `null` khi không thấy hoặc chưa rõ tiền tệ |
| `gia_tri_de_nghi` | Giá trị đề nghị thanh toán kỳ này | `so_tien` | Như trên |
| `tien_te_chua_ro` | Tiền tệ chưa rõ | `co_khong` | |
| `bam_dau_vao` | Mã băm tệp vào | `van_ban` | |
| `phien_ban_engine` | Phiên bản engine | `van_ban` | |

### 4.3 Quy ước giá trị trường trả ra (bắt buộc theo SDK 2.2.0)

Lead đã kiểm trong mã SDK 2.2.0 (`engine.py`, hàm kiểm giá trị trường):

- **`so`:** chỉ nhận `int`/`float` hữu hạn, **không nhận `Decimal`**. Các trường đếm (`so_co_cao`, `so_dong`…) trả `int`.
- **`so_tien`:** đúng hai khóa `{"so", "tien_te"}`.
  - `tien_te` phải là 3 chữ in hoa, không nhận `null`. Chưa rõ đơn vị thì trả **cả trường = `null`**, kèm `tien_te_chua_ro = true`.
  - `so` là số hoặc chuỗi khớp `-?[0-9]+(\.[0-9]+)?`. Từ `Decimal` phải đổi bằng `format(d, "f")`; `str(d)` có thể ra `2.5E+9` và bị SDK từ chối. Không dấu phẩy, không dấu cách.
- **`tep`:** đối tượng do `viec.tai_tep_ra(ten, bytes, mime)` trả về, đặt nguyên vào trường.
- Test EX-1/EX-4 phải có ca `Decimal` lớn (≥ 10^9) và ca số âm, ca có phần lẻ.

## 5. Tệp JSON chi tiết

Quy ước chung cho mọi tệp JSON engine tải lên:

- Mã hóa UTF-8.
- Số dạng **chuỗi thập phân** (giữ đúng giá trị `Decimal`, không qua `float`).
- Tiền = `{"so": "…", "tien_te": "VND" | null}`.
- Vị trí ô dạng `"Sheet!D38"`.
- Không chép toàn bộ nội dung file vào JSON.
- Trần đề xuất 20 MiB. Vượt trần → `VUOT_GIOI_HAN`, không cắt ngầm.

### 5.1 Của `excel.toan_ven@1`

```json
{"phien_ban": 1, "phien_ban_engine": "e_kiem_excel 0.1.0", "bam_dau_vao": "sha256:…",
 "o_dich": "2. TH!D38", "bo_nhom": {"ten_bo": "…", "bam": "sha256:…"} ,
 "phat_hien": [{"muc": "Cao", "kiem": "K2", "o": "BTH!H45", "mo_ta": "…", "so_o": 1, "tai_lieu": "…"}],
 "k1_sheet": [...], "k1_lien_ket_ngoai": [{"stt": 1, "ten_tep": "…", "so_cong_thuc": 3}],
 "k2_mau_cot": [...], "k2_lech_mau": [...], "k2_go_tay": [...],
 "k3_lien_ket_dong": [...], "k4_sheet_an": [...], "k5_so_dang_chu": [...], "k6_hang_so": [...],
 "k7_cay": [{"cap": 0, "o": "…", "cong_thuc": "…", "gia_tri": "…", "la": false, "nhom": null}],
 "k8_nguon": [...], "canh_bao": []}
```

`k1_lien_ket_ngoai.ten_tep` chỉ ghi **tên tệp**, bỏ phần thư mục, vì đường dẫn có thể lộ cấu trúc máy nội bộ. Chi tiết từng mảng theo đúng các cột báo cáo của `toan_ven.py` (hàm `ghi`). Codex chốt schema ở lát EX-1, lead duyệt.

### 5.2 Của `excel.doc_bang@1`

```json
{"phien_ban": 1, "phien_ban_engine": "e_kiem_excel 0.1.0", "bam_dau_vao": "sha256:…",
 "khuon": "xay_dung_klgt", "sheet": "…", "dong_tieu_de": 8, "cot": {"ten": "C", "dvt": "D", "dg": "H"},
 "tien_te": null,
 "dong": [{"vi_tri": "BTH!12", "stt": "1", "nhom": "A / I", "ten": "…", "dvt": "m3",
           "khoa": "…", "kl_hd": "25", "kl_kt": "0", "kl_kn": "5", "kl_lk": "5",
           "don_gia": {"so": "100000000", "tien_te": null},
           "gt_hd": {"so": "2500000000", "tien_te": null}, "canh_bao": []}],
 "tong_hop": {"gt_hd": {"gia_tri": {"so": "…", "tien_te": null}, "o": "…", "nhan": "…"}},
 "canh_bao": []}
```

`khoa` giữ đúng công thức `khoa()` gốc (nhóm + tên + ĐVT, bỏ dấu, thêm `#n` khi trùng) để module khớp hạng mục giữa các đợt.

## 6. Giới hạn, an toàn, lỗi

- **Giới hạn đầu vào:** `tep_toi_da_mib: 20` (giống `e_ocr`).
- **`thoi_han_giay`: đề xuất cuối EX-6 = 120 giây cho cả hai năng lực**, giữ `tep_toi_da_mib = 20`; dựa trên số đo DEMO thật bên dưới. Không dùng số 25 giây hồ sơ thật của quy trình cũ làm bằng chứng cho gói.
- **Nhận diện tệp:** không chỉ dựa vào mime Core gửi (một số trình duyệt gửi `application/octet-stream`). Engine kiểm thêm đuôi `.xlsx`/`.xlsm` và chữ ký ZIP `PK\x03\x04` ở đầu tệp; `.xls` cũ (chữ ký OLE `D0 CF 11 E0`) → `TEP_KHONG_HO_TRO`. EX-0 ghi rõ Core gán mime gì khi tải `.xlsx` lên; nếu Core gán `application/octet-stream` thì thêm mime này vào `gioi_han.mime` và dựa vào kiểm chữ ký.
- **Trước khi nạp `openpyxl`:**
  - kiểm tổng dung lượng giải nén của gói ZIP .xlsx và số tệp bên trong để chặn "bom nén";
  - chặn số ô quá trần (đếm thẻ `<c` trong các sheet XML theo luồng, không nạp cả cây);
  - ghim `defusedxml` để `openpyxl` tự dùng bộ phân tích an toàn; test có một tệp DEMO chứa thực thể XML lồng nhau phải bị từ chối.
  - Trần cụ thể Codex đo và đề xuất **ở EX-0**.
- **Bộ nhớ:** `SoDo` nạp workbook đầy đủ hai lần. EX-6 đã đo toàn năng lực trên bản 0.1.1 ở 1/5/10/20 MiB và sát trần ô/vùng/giải nén, bảng dưới. Giữ trần 250.000 ô thực, 500.000 ô vùng, 128 MiB giải nén, 2.048 entry, một việc đồng thời.
- **Không chạy macro, không mở file ngoài:** nạp `.xlsm` với `keep_vba=False`; liên kết ngoài chỉ đọc tên.
- **Engine không lưu gì trên máy** (Anh chốt 15/11): tệp tạm của một việc nằm trong RAM; nếu buộc phải ghi đĩa thì xóa trong `finally`.
- **Mã lỗi** (câu tiếng Việt cho người dùng, mã để trong "Chi tiết hỗ trợ"):

| Mã | Khi nào | Câu gợi ý |
|---|---|---|
| `TEP_KHONG_HO_TRO` | Không phải .xlsx/.xlsm, hoặc .xls cũ | Chỉ nhận tệp Excel .xlsx hoặc .xlsm. Vui lòng lưu lại tệp theo định dạng này. |
| `TEP_HONG` | Không mở được | Không đọc được tệp Excel này. Vui lòng mở và lưu lại tệp rồi gửi lại. |
| `VUOT_GIOI_HAN` | Quá trần dung lượng, ô, giải nén, JSON | Tệp vượt giới hạn xử lý. Vui lòng tách tệp hoặc liên hệ quản trị. |
| `THAM_SO_KHONG_HOP_LE` | `bo_nhom_json`, `khuon_cot_json`, `o_dich`, `tien_te` sai | Cài đặt bước chưa đúng. Quản trị viên kiểm tra lại cài đặt của quy trình. |
| `KHONG_TIM_THAY_BANG` | `doc_bang` không thấy bảng theo khuôn | Không tìm thấy bảng có đủ cột cần đọc trong tệp này. |


### Số đo EX-6 — 19/11/2026 (bản 0.1.1)

**Đã kiểm bằng Core giả (CoreGia)** trên Windows x64/Python 3.13.14, SDK 2.2.0,
openpyxl 3.1.5; ba tiến trình riêng mỗi mẫu/năng lực, **36/36 XONG**. Đo
perf_counter quanh toàn bộ chay_thu, RSS đỉnh tiến trình, không tracemalloc;
không tính sinh DEMO/import module. Toàn vẹn bật K8, bộ nhóm và cây K7;
đọc bảng xay_dung_klgt kiểm đúng 30 dòng. Chi tiết phương pháp/SHA runtime và
input ở `tests/demo/so-do-hieu-nang-EX6.json`, diễn giải ở `docs/VIEC.md` EX-6.

| DEMO | Byte tệp / MiB giải nén / ô thực / ô vùng | Toàn vẹn: trung vị / lớn nhất (s) | Toàn vẹn: RSS đỉnh (MiB) | Đọc bảng: trung vị / lớn nhất (s) | Đọc bảng: RSS đỉnh (MiB) |
|---|---|---:|---:|---:|---:|
| 1 MiB | 1,049,804 / 2.057 / 9,325 / 9,512 | 0.667 / 0.708 | 54.10 | 0.269 / 0.394 | 45.53 |
| 5 MiB | 5,240,493 / 10.267 / 44,925 / 45,112 | 3.375 / 3.384 | 118.59 | 1.196 / 1.211 | 77.12 |
| 10 MiB | 10,477,707 / 20.543 / 89,405 / 89,592 | 6.504 / 6.976 | 192.79 | 2.483 / 3.067 | 115.03 |
| 20 MiB | 20,951,711 / 41.109 / 178,345 / 178,532 | 12.163 / 12.719 | 342.29 | 4.760 / 4.915 | 190.88 |
| Sát trần ô/vùng | 575,218 / 7.242 / 249,421 / 499,552 | 8.495 / 8.498 | 343.56 | 3.080 / 3.578 | 139.79 |
| Sát trần giải nén | 329,594 / 127.847 / 4,534 / 4,702 | 1.712 / 2.205 | 300.70 | 1.099 / 1.166 | 170.00 |

Chậm nhất **12.719 giây**, RSS lớn nhất **343.56 MiB**. Giữ
**20 MiB/120 giây**, hệ số dự phòng thời gian đo **9.43 lần**.
Mật độ/giải nén ảnh hưởng độc lập với dung lượng tệp; không bỏ các trần phụ.
Số đo không chứng minh worst case cây K7 hoặc bảng xuất cực lớn/mọi khuôn.
Chưa đo Linux/Python 3.11 hay Core thật; CI đã cấu hình, chờ lead chạy.
Báo cáo Excel ghi cả XML worksheet trong RAM, không dùng tệp tạm của openpyxl.

## 7. DEMO và tiêu chí đạt

- **Bộ Excel DEMO** do script trong `tests/` sinh ra, nhãn DEMO (ví dụ "Công ty DEMO Ánh Dương", số tiền giả). Mỗi kiểm tra K1–K8 có ít nhất một dấu hiệu cài sẵn, kèm `tests/demo/dap-an.json` ghi phát hiện kỳ vọng. Thêm một file "sạch" để kiểm không báo nhầm.
- **Sinh DEMO có sẵn giá trị lưu, không cần LibreOffice:**
  - Tệp do `openpyxl` ghi **không có giá trị lưu** của công thức, nên K1 sẽ báo "chưa tính lại" và K7/K8 không có giá trị.
  - Vì vậy script sinh DEMO **tự ghi XML của .xlsx bằng thư viện chuẩn** (`zipfile`), mỗi ô công thức có cả `<f>` (công thức) lẫn `<v>` (giá trị lưu, script tự tính).
  - Tệp ra tất định, ghi SHA-256 vào `tests/demo/bam-fixture.json`; Codex tự chạy trong test, Anh không phải chạy gì.
  - Một tệp DEMO cố ý **không có** `<v>` để kiểm K1 báo "chưa tính lại".
  - LibreOffice/Excel chỉ là cách đối chiếu phụ, không bắt buộc.
- **Tương đương mã gốc:** với cùng file DEMO và bộ 7 nhóm ở Phụ lục A, kết quả `excel.toan_ven@1` phải khớp kết quả `python toan_ven.py <file>` về danh sách phát hiện (mức, mã kiểm, ô) và cây K7. Chỗ lệch phải liệt kê và lead duyệt từng chỗ (ví dụ do đổi `float` sang `Decimal`).
- **`chay_thu_demo`:** ít nhất 3 ví dụ:
  - kiểm toàn vẹn có bộ nhóm;
  - kiểm toàn vẹn không có bộ nhóm;
  - đọc bảng khuôn `xay_dung_klgt`.
- **Điều kiện đạt chung mỗi lát** (theo `AGENTS.md` §5; ghi "đã kiểm bằng Core giả (CoreGia)", không ghi "SẴN SÀNG"):

```bash
python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel   # mọi ví dụ [ĐẠT], mã thoát 0
python -m pytest e_kiem_excel/tests -q                          # 0 lỗi; skip phải có lý do
python e_kiem_excel/tests/kiem_doc_lap.py                       # không import kho_tri_thuc.*, không __pycache__ trong goi/
```

## 8. Lát đề xuất

Mỗi lát một nhánh `codex/e_kiem_excel-<mã lát>`, tối đa khoảng 5 tệp mã. Giờ công **ước tính của lead, chưa đo**: EX-0 4, EX-1 6, EX-2 4, EX-3 4, EX-4 4, EX-5 4, EX-6 3 = **29 giờ**. Lệnh giao từng lát: `GIAO-CODEX-e_kiem_excel.md`.

| Lát | Nội dung | Xong khi |
|---|---|---|
| EX-0 | Khung gói SDK 2.2.0: `engine.json` 2 năng lực (chưa xử lý thật), `requirements.lock` ghim `openpyxl` (+ `et_xmlfile`, `defusedxml`), `NGUON.md`, script sinh DEMO có `<v>`, `kiem_doc_lap.py`, nhận diện tệp, kiểm trần giải nén/ô, **đo đỉnh bộ nhớ** | Ba lệnh §7 chạy; DEMO có SHA; bảng số đo bộ nhớ và trần đề xuất |
| EX-1 | Chuyển `SoDo`, hàm tham chiếu, K1–K6 nạp từ bytes; schema `tep_json` §5.1 | K1–K6 khớp đáp án DEMO và khớp `toan_ven.py` |
| EX-2 | K7 với `o_dich`, `nhan_o_dich_json`, `bo_nhom_json` (§4.1.1); Phụ lục A làm fixture | Cây K7 và phân nhóm khớp `toan_ven.py` trên DEMO |
| EX-3 | Báo cáo Excel `tep_bao_cao` trong RAM; K8 sau công tắc `kiem_nguon_kl` | Đủ các sheet như `toan_ven.py`; K8 khớp đáp án |
| EX-4 | `excel.doc_bang@1` khuôn `xay_dung_klgt` (`tim_bang_chi_tiet`, `khoa`, `tim_so_tong_hop`), `Decimal`, tham số `tien_te` | Bảng đọc ra khớp đáp án; `tien_te_chua_ro` đúng khi thiếu đơn vị |
| EX-5 | Khuôn `tong_quat` theo `khuon_cot_json` | Đọc được ít nhất 2 mẫu bảng DEMO khác nhau (ví dụ bảng giá thành, bảng báo giá) |
| EX-6 | Ghim nguồn, cài máy sạch offline, đo thời gian và đỉnh bộ nhớ trên file 20 MiB; đề xuất `thoi_han_giay` | Cài sạch đạt; số đo ghi trong `VIEC.md` |

Thứ tự đề xuất: EX-0 → EX-1 → EX-2 → EX-3 → EX-4. EX-5 làm khi có module thứ hai cần dùng; EX-6 làm cuối.

## 9. Chờ Anh / Cần Core

**Chờ Anh** (phương án đề xuất được dùng tạm nếu Anh chưa trả lời):

| # | Câu | Phương án | Đề xuất |
|---|---|---|---|
| Q1 | Dùng thư viện ngoài | (a) ghim `openpyxl` (+ `defusedxml`); (b) tự đọc XML của .xlsx bằng thư viện chuẩn | **Áp (a) — 16/11.** Mã gốc đã viết trên `openpyxl`; (b) phải viết lại phần đọc công thức dùng chung (shared formula), rủi ro cao |
| Q2 | Tách hay gộp | (a) 2 năng lực như phiếu này; (b) 1 năng lực trả cả hai | **Áp (a) — 16/11.** Mỗi năng lực dùng lại được riêng. Quy trình của Core chỉ chuyển kết quả bước trước sang bước sau, bước sau không nhận lại tệp gốc, nên hai năng lực gắn vào hai nút; người dùng Review TTKL tải cùng file hai lần |
| Q3 | Tên mã | `e_kiem_excel` / `e_excel_ho_so` | **Áp `e_kiem_excel` — 16/11.** Engine dùng chung, không riêng hồ sơ |

**Cần Core:** không có cửa mới riêng cho engine này. Hai việc liên quan nằm phía module, không chặn engine:

- module đọc `tep_json` qua `tep.mo_doc` (C-RV-01 của thiết kế module);
- ghi đơn vị tiền tệ vào cột tiền của ngăn module (C-RV-03).

## 10. Module sẽ dùng

| Module / mảng | Dùng năng lực nào | Module truyền gì |
|---|---|---|
| Review thanh toán khối lượng (`review_ttkl`) | Cả hai: nút "Kiểm toàn vẹn", "Đọc BOQ", "Đọc hồ sơ đợt" | Ô đích "giá trị đề nghị thanh toán kỳ này", bộ 7 nhóm (Phụ lục A), `kiem_nguon_kl = true`, khuôn `xay_dung_klgt` |
| Quyết toán / dự toán hạ tầng (BĐS nhà ở, KCN) | Cả hai | Như trên, ô đích là giá trị quyết toán |
| Thẩm định đầu tư (mô hình NPV/IRR) | `toan_ven` | Ô đích NPV/IRR; bộ nhóm "giả định đầu vào"; K6 bắt tỷ lệ gõ cứng |
| Báo cáo công ty con trước hợp nhất | `toan_ven` | Ô đích chỉ tiêu cần truy (ví dụ lợi nhuận trước thuế); bộ nhóm theo nguồn số liệu |
| Bảng giá / bảng hàng BĐS, giá thành sản xuất, so sánh báo giá | `toan_ven` và `doc_bang` khuôn `tong_quat` | Khuôn cột theo mẫu bảng; ô đích theo chỉ tiêu |

Các mảng ngoài Review TTKL **chưa có bộ DEMO và chưa đo**; danh sách trên là khả năng, không phải cam kết.

---

## Phụ lục A — Bộ 7 nhóm dữ liệu gốc của Review TTKL (thuộc module, dán vào `bo_nhom_json`)

Chuyển từ hàm `nhom_goc` và bảng `TAI_LIEU` trong `toan_ven.py`, giữ đúng thứ tự xét. Từ khóa có `=` là khớp nguyên từ (tương đương `\b` trong mã gốc), còn lại là chứa chuỗi như mã gốc. EX-2 phải chứng minh tương đương trên DEMO.

```json
{"phien_ban": 1, "ten_bo": "Review TTKL - 7 nhóm dữ liệu gốc", "nhom": [
 {"ma": "2", "ten": "2 Đơn giá", "tai_lieu": "A02 BOQ / A03 phụ lục",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet"], "tat_ca": [["don gia"]]}]},
 {"ma": "3-4", "ten": "3-4 Kỳ trước / lũy kế trước", "tai_lieu": "E01 hồ sơ đợt trước đã duyệt",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet", "nhan_dong"], "tat_ca": [["ky truoc", "ki truoc", "dot truoc", "luy ke truoc"]]}]},
 {"ma": "1", "ten": "1 KL hợp đồng", "tai_lieu": "A02 BOQ / A03 phụ lục",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet"], "tat_ca": [["hop dong", "=hd"], ["khoi luong", "=kl"]]}]},
 {"ma": "7", "ten": "7 Đã thanh toán / tạm ứng", "tai_lieu": "E01 hồ sơ đã duyệt, E02 UNC",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet", "nhan_dong"], "tat_ca": [["tam ung", "da thanh toan", "thanh toan dot", "dot #", "unc"]]}]},
 {"ma": "5", "ten": "5 KL kỳ này", "tai_lieu": "C01/C02 biên bản nghiệm thu",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet"], "tat_ca": [["ky nay", "ki nay", "thuc hien", "nghiem thu", "hoan thanh"]]}]},
 {"ma": "6", "ten": "6 Tham số HĐ", "tai_lieu": "A01 điều khoản hợp đồng",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet", "nhan_dong"], "tat_ca": [["%", "ty le", "thue suat", "he so", "giu lai"]]},
          {"vung": ["tieu_de_cot", "ten_sheet", "nhan_dong"], "tat_ca": [["=thue", "vat", "gtgt"]], "khong_co": ["gia tri"]}]},
 {"ma": "1-2", "ten": "1-2 Giá trị HĐ", "tai_lieu": "A01 hợp đồng / A03 phụ lục",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet", "nhan_dong"], "tat_ca": [["gia tri hop dong", "gia tri hd"]]}]},
 {"ma": "5b", "ten": "5 KL / diễn giải", "tai_lieu": "B01 bản vẽ / B03 hoàn công / diễn giải KL",
  "khi": [{"vung": ["tieu_de_cot", "ten_sheet"], "tat_ca": [["khoi luong", "=kl", "dien giai", "kich thuoc", "dai", "rong", "cao", "so luong"]]}]}
]}
```

Ô nhập tay không khớp nhóm nào → "Ngoài nhóm — cần giải thích", tài liệu "Yêu cầu nhà thầu giải trình nguồn".

**Hai chỗ lệch nhỏ so với mã gốc, EX-2 phải kiểm:**

1. Mã gốc xét `khong_co: "gia tri"` (nhóm 6, điều kiện 2) chỉ trên tiêu đề + tên sheet; định dạng trên xét cả nhãn dòng.
2. Mã gốc dùng `dai|rong|cao` dạng chứa chuỗi, nên cũng khớp chữ như "bao cao". Phụ lục giữ đúng hành vi đó; muốn chặt hơn thì đổi thành `=dai`, `=rong`, `=cao` sau khi Anh duyệt.

## Phụ lục B — Khung `engine.json`

Khung thiết kế, **chưa phải phiếu hoàn chỉnh**. EX-0 điền đủ `truong_ra`, `tham_so`, `chay_thu_demo` theo §4 và kiểm bằng `kho_tri_thuc_sdk.thu`.

```json
{
  "phien_ban_manifest": 2,
  "loai": "engine",
  "ma": "e_kiem_excel",
  "ten": "Kiểm và đọc file Excel",
  "phien_ban": "0.1.0",
  "tuong_thich": {"core": ">=2.0.0 <3.0.0", "api": "v1", "sdk": ">=2.2.0 <3.0.0"},
  "che_do_chay": "cuc_bo",
  "diem_vao": {"lenh": ["{python}", "-m", "e_kiem_excel.chay"], "thu_muc": "."},
  "nang_luc": [
    {"ma": "excel.toan_ven@1", "ten": "Kiểm tính toàn vẹn file Excel",
     "nhan": ["tep"], "tra": "truong", "truong_ra": ["… §4.1"],
     "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": "<đo ở EX-6>",
                  "mime": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           "application/vnd.ms-excel.sheet.macroEnabled.12"]},
     "huy_duoc": true, "tham_so": ["… §4.1"]},
    {"ma": "excel.doc_bang@1", "ten": "Đọc bảng Excel nhiều tầng tiêu đề",
     "nhan": ["tep"], "tra": "truong", "truong_ra": ["… §4.2"],
     "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": "<đo ở EX-6>", "mime": ["… như trên"]},
     "huy_duoc": true, "tham_so": ["… §4.2"]}
  ],
  "loai_du_lieu_rieng": [],
  "tai_nguyen": {"so_viec_dong_thoi": 1},
  "readiness": {"thoi_han_giay": 30},
  "chay_thu_demo": ["… §7"],
  "bi_mat": [],
  "webhook": null
}
```

Không khai `ngan_du_lieu`, `cau_hinh` hay `du_lieu.goi_migration`: engine không giữ dữ liệu giữa các việc và không có cấu hình máy.

## Phụ lục C — Chỉnh sửa của lead (16/11/2026)

Sau khi đối chiếu phiếu với mã gốc (`review_xaydung` commit `1bed645`, SHA khớp) và SDK 2.2.0:

| # | Chỉnh | Mục |
|---:|---|---|
| 1 | Quy ước giá trị `so` / `so_tien` theo đúng bộ kiểm của SDK 2.2.0; `format(d, "f")` cho `Decimal` | §4.3 |
| 2 | `khuon` có `lua_chon`; các tham số chữ có `toi_da` để Core chặn khi Admin nhập | §4.1, §4.2 |
| 3 | Đo đỉnh bộ nhớ ngay ở EX-0, không đợi EX-6 | §6, §8 |
| 4 | Ghim `defusedxml`; ca DEMO thực thể XML lồng nhau | §1, §6 |
| 5 | DEMO tự ghi `<f>` + `<v>`, bỏ phụ thuộc LibreOffice | §7 |
| 6 | Báo cáo Excel ghi bằng `openpyxl` vào `BytesIO`; `xlsx_mini` chỉ tham khảo | §3.3 |
| 7 | Nhận diện tệp bằng đuôi + chữ ký ZIP, không chỉ mime | §6 |
| 8 | Thêm lý do cho Q2 | §9 |
| 9 | Bản tham chiếu mã gốc chép vào `e_kiem_excel/ma-nguon/` (chỉ đọc) để test so tương đương; `master_hd.py` chỉ import trong test, không vào gói | §3, §7 |

Chưa kiểm được: các dẫn chiếu `phan_mem_core` (§3.4), vì repo riêng tư, phiên của lead không đọc được.
