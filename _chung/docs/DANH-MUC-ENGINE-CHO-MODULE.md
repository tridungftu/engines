# Danh mục engine cho lập trình module

*Tệp **sinh tự động** bằng `python _chung/cong-cu/sinh_danh_muc_engine.py` từ `engine.json` của mọi gói; không sửa tay. Muốn đổi ghi chú hay chuỗi mẫu: sửa `GHI_CHU`/`CHUOI` trong script rồi chạy lại. Kiểm tự động trên GitHub báo đỏ khi tệp chưa cập nhật theo `engine.json` hoặc một chuỗi mẫu nối sai.*

*Phiên bản gói lúc sinh: `e_ocr` 1.0.9, `e_hoi_ai` 0.12.0, `e_mask` 1.6.1, `e_trich_xuat` 0.5.0, `e_hoa_don` 1.0.0, `e_kiem_excel` 0.1.1, `e_phan_luong` 0.1.0, `e_doi_chieu` 0.9.0, `e_tra_cuu` 0.2.0.*

## 1. Kết luận

- **9 engine, 43 năng lực.** Tất cả mới **kiểm bằng Core giả (CoreGia)**, chưa nối Core thật, nên chưa engine nào "SẴN SÀNG". Module lập trình và test bằng dữ liệu DEMO.
- **Module không gọi engine.** Module khai **nút** trong phiếu module. Admin tạo **quy trình** (chuỗi bước engine) gắn vào nút trên Core. Kết quả bước cuối về **ngăn** của module.
- Tải gói: mục **Releases** của repo `tridungftu/engines`; chọn bản có tệp `<engine>-<phiên bản gói>.zip` khớp cột "Gói" dưới đây. Mỗi bản có `SHA256SUMS.txt`, `DANH-SACH-GOI.json`, `HUONG-DAN-CAI-NGHIEM-THU.md` và wheel SDK.

| Engine | Tên | Gói | Số năng lực | Dùng khi | Lưu ý cho module |
|---|---|---|---:|---|---|
| `e_ocr` | Nhận dạng văn bản | 1.0.9 | 3 | PDF scan, ảnh → chữ có vị trí, văn bản thuần, Word giữ bảng | ABBYY trước, Tesseract dự phòng; ABBYY thật chưa chạy thử |
| `e_hoi_ai` | Hỏi AI | 0.12.0 | 3 | Hỏi AI về tài liệu có trích dẫn; bước AI giữa chuỗi của engine khác | **Chỉ Local AI**; chưa có năng lực Cloud; prompt thuộc module |
| `e_mask` | Che định danh | 1.6.1 | 8 | Che/mở che tên, MST, địa chỉ… trước khi đưa ra ngoài | Kho bí danh tạm giữ trong bộ nhớ (mất khi khởi động lại); mở che cần `ma_yeu_cau` |
| `e_trich_xuat` | Trích thông tin hợp đồng | 0.5.0 | 4 | Trích tham số hợp đồng theo bộ tham số của module | Bộ tham số + mã băm truyền qua Cài đặt bước |
| `e_hoa_don` | Đọc XML hóa đơn | 1.0.0 | 3 | Đọc XML, ZIP hóa đơn điện tử; lập bảng kê XLSX | Chưa có PDF, chưa tải cổng thuế |
| `e_kiem_excel` | Kiểm và đọc file Excel | 0.1.1 | 2 | Kiểm toàn vẹn file Excel (K1–K8); đọc bảng nhiều tầng tiêu đề | Ô đích, bộ nhóm, khuôn cột do module truyền |
| `e_phan_luong` | Phân luồng kiểm tra | 0.1.0 | 5 | Phân luồng kiểm tra theo khâu, ngưỡng PM/TE/SAD và chọn mẫu | PL-2: `audit.phan_luong@1` nhận JSON, có DEMO; Excel/CSV, AI, hóa đơn và ghi kết quả chờ lát sau; danh sách Excel để trống tới PL-8 |
| `e_doi_chieu` | Đối chiếu bản ký | 0.9.0 | 7 | So bản Word chuẩn với bản đã ký | Bước đầu nhận **tệp JSON cặp** do module lập; chặn hiệu lực là việc của module |
| `e_tra_cuu` | Tra cứu tài liệu | 0.2.0 | 8 | Hỏi đáp 3 tầng trên kho tài liệu | Bước đầu nhận **tệp JSON yêu cầu**; cần Kho tài liệu của Core (chưa có) |

## 2. Quy tắc module phải theo

1. **Quy tắc nối bước** (API v1 b.2):
   - bước 1 nhận `tep`, là tệp người dùng tải ở nút;
   - bước *k* hợp lệ khi loại `tra` của bước *k−1* nằm trong `nhan` của bước *k*; Core tự kiểm khi khai quy trình.
2. **Bước cuối phải trả `truong`, `van_ban` hoặc `tep`** thì mới ghép được vào cột ngăn của module. Năng lực trả loại riêng (mục 4) **chỉ dùng ở giữa chuỗi**.
3. **Bước sau không nhận lại tệp gốc.** Cần hai kết quả khác nhau từ cùng một tệp thì làm **hai nút** (hai quy trình), người dùng tải tệp hai lần. Ví dụ: kiểm toàn vẹn Excel và đọc bảng Excel.
4. **Nhận kết quả:**
   - khi quy trình xong, Core gửi `quy_trinh.xong`; SDK module gọi hàm nhận với `tep_nut` và `ghep` (xem `docs/goi-gui-engine/sdk-2.2.0/HUONG-DAN-VIET-MODULE.md`);
   - trường kiểu `tep` (báo cáo Excel, JSON chi tiết, Word…) là tham chiếu tệp trong kho Core; module đọc nội dung bằng cổng đọc tệp của SDK module.
5. **Tiền** (kiểu `so_tien`):
   - dạng `{"so": "<chuỗi thập phân>", "tien_te": "VND"}`;
   - chưa rõ đơn vị thì **cả trường là `null`**, kèm cờ chưa rõ (nếu engine có);
   - module không tự gán VND.
   - Hiển thị: tiền có dấu chấm hàng nghìn kèm đơn vị; ngày dd/mm/yyyy.
6. **AI:**
   - mọi bước gọi model đi qua `e_hoi_ai`, hiện **chỉ Local**;
   - Cloud chưa có; khi có (bản 2) chỉ nhận `van_ban_da_che`, tức phải có bước Mask đứng trước;
   - M9 và nhóm tài liệu 07-Nhân sự luôn chỉ Local.
7. **Lỗi:** engine trả mã lỗi kèm câu tiếng Việt. Module hiển thị câu đó, không tự diễn giải lại. Quá trần thì engine từ chối, không cắt ngầm.
8. **Dữ liệu thử:** chỉ dùng DEMO (ví dụ "Công ty DEMO Ánh Dương", 1.000.000 VND, 30/10/2026).
9. **Cài đặt bước thuộc module:** prompt, bộ tham số hợp đồng, bộ nhóm dữ liệu gốc, khuôn cột, bộ quy tắc đối chiếu… đặt trong Cài đặt bước của quy trình; engine không có mặc định chung cho các thứ này.

## 3. Chuỗi bước mẫu (quy trình)

Script đã kiểm mọi chuỗi dưới đây nối đúng `nhan`/`tra` trong `engine.json`. Tên trường ra chi tiết ở mục 5.

| # | Mục đích | Chuỗi bước | Cột ngăn nhận |
|---:|---|---|---|
| 1 | Phân luồng kiểm tra lô JSON theo khâu | `audit.phan_luong@1` | luồng, lý do, số đếm, tổng tiền Đỏ, tệp JSON, mã lượt và băm |
| 2 | Phân luồng kiểm tra có phân loại bằng Local AI | `audit.chuan_bi_phan_loai@1` → `ai.hoi_theo_yeu_cau@1` → `audit.phan_luong_sau_ai@1` | như phân luồng; dòng AI gán loại ghi nguồn loại ai |
| 3 | Lấy chữ từ PDF scan/ảnh | `ocr.doc_van_ban@1` | 1 trường văn bản |
| 4 | Chuyển PDF scan/ảnh sang Word | `ocr.xuat_word@1` | 1 trường tệp (DOCX) |
| 5 | Hỏi AI về PDF scan/ảnh | `ocr.doc_tai_lieu@1` → `ai.hoi_tai_lieu@1` | trả lời, có căn cứ, trích dẫn, model |
| 6 | Hỏi AI về hợp đồng Word | `trich.doc_docx@1` → `ai.hoi_tai_lieu@1` | như trên |
| 7 | Trích tham số hợp đồng Word | `trich.doc_docx@1` → `trich.chuan_bi@1` → `ai.hoi_theo_yeu_cau@1` → `trich.hau_kiem@1` → `trich.xuat_ket_qua@1` | tệp JSON, tệp Excel, số tham số, số ô cần soát, có căn cứ |
| 8 | Trích tham số hợp đồng PDF | `ocr.doc_tai_lieu@1` → `trich.chuan_bi@1` → `ai.hoi_theo_yeu_cau@1` → `trich.hau_kiem@1` → `trich.xuat_ket_qua@1` | như trên |
| 9 | Đọc một hóa đơn XML | `hoa_don.doc_xml@2` | các trường hóa đơn (số, ngày, MST, tiền…) |
| 10 | Đọc gói ZIP hóa đơn | `hoa_don.doc_zip@1` | số tệp, đọc được, lỗi, trùng… |
| 11 | Lập bảng kê XLSX | `hoa_don.doc_xml@2` / `hoa_don.doc_zip@1` → `hoa_don.bang_ke_xlsx@1` | tệp bảng kê + số đếm |
| 12 | Kiểm toàn vẹn file Excel | `excel.toan_ven@1` | số cờ Cao/Trung bình, ô đích, báo cáo Excel, JSON |
| 13 | Đọc bảng Excel (BOQ, hồ sơ đợt, báo giá…) | `excel.doc_bang@1` | sheet, số dòng, giá trị HĐ, giá trị đề nghị, JSON |
| 14 | Che tệp Word/Excel bằng Local AI, giữ định dạng | `mask.chuan_bi_tep_ai_cuc_bo@1` → `ai.hoi_mask_cuc_bo@1` → `mask.hau_kiem_tep_giu_dinh_dang@1` | tệp đã che, mã yêu cầu, phần còn sót, kiểm tiền/ngày |
| 15 | Đối chiếu bản ký | `doi_chieu.nhan_cap@1` → `doi_chieu.so_van_ban@1` → `doi_chieu.phat_hien_sua_tay@1` → `doi_chieu.chuan_bi_ai@1` → `ai.hoi_theo_yeu_cau@1` → `doi_chieu.phan_loai_diem_lech@1` → `doi_chieu.xuat_ket_qua@1` | kết luận, số điểm nghiêm trọng, đề nghị chặn, JSON, PDF |
| 16 | Tra cứu tài liệu | `tra_cuu.nhan_yeu_cau@1` → `tra_cuu.cat_doan@1` → `tra_cuu.chuan_bi_ai@1` → `ai.hoi_theo_yeu_cau@1` → `tra_cuu.phan_loai_tai_lieu@1` / `tra_cuu.phan_tich_cau_hoi@1` / `tra_cuu.xep_hang_lai@1` / `tra_cuu.soan_tra_loi@1` → `tra_cuu.xuat_ket_qua@1` | trả lời, nhãn, tầng, có căn cứ, có mâu thuẫn, cần duyệt, JSON |

**Lưu ý:**
- **Mask:**
  - `mask.che_van_ban@1` và `mask.hau_kiem_ai_cuc_bo@1` trả `van_ban_da_che`, hiện chưa có bước nào nhận tiếp. Bước Cloud thuộc bản 2.
  - Mở che (`mask.mo_che_tep@1`, `mask.mo_che_van_ban@1`) cần đúng `ma_yeu_cau` do Core cấp lúc che.
  - Hỏi lead Mask trước khi thiết kế luồng che/mở che trong module.
- **Đối chiếu, Tra cứu:** bước đầu nhận **tệp JSON** (cặp tài liệu, yêu cầu tra cứu) do module lập, không phải tệp người dùng tải. Thứ tự các bước giữa theo README của gói.
- **Tra cứu** cần Kho tài liệu và chỉ mục của Core. Core chưa có phần này.

## 4. Loại dữ liệu dùng chung giữa các bước

| Mã | Ý nghĩa | Năng lực tạo ra | Năng lực nhận |
|---|---|---|---|
| `van_ban_tai_lieu` | Văn bản có vị trí trang, bảng, nguồn đọc | `ocr.doc_tai_lieu@1`, `trich.doc_docx@1`, `doi_chieu.doc_docx@1` | `ai.hoi_tai_lieu@1`, `mask.chuan_bi_ai_cuc_bo@1`, `mask.che_van_ban@1`, `trich.chuan_bi@1` |
| `yeu_cau_ai` | Yêu cầu hỏi AI (prompt, tài liệu, khuôn trả lời) | `mask.chuan_bi_tep_ai_cuc_bo@1`, `mask.chuan_bi_ai_cuc_bo@1`, `trich.chuan_bi@1`, `audit.chuan_bi_phan_loai@1`, `doi_chieu.chuan_bi_ai@1`, `tra_cuu.chuan_bi_ai@1` | `ai.hoi_theo_yeu_cau@1`, `ai.hoi_mask_cuc_bo@1` |
| `tra_loi_ai` | Trả lời AI có trích dẫn, đã kiểm | `ai.hoi_theo_yeu_cau@1`, `ai.hoi_mask_cuc_bo@1` | `mask.hau_kiem_tep_van_ban@1`, `mask.hau_kiem_tep_giu_dinh_dang@1`, `mask.hau_kiem_ai_cuc_bo@1`, `mask.mo_che_van_ban@1`, `trich.hau_kiem@1`, `audit.phan_luong_sau_ai@1`, `doi_chieu.phan_loai_diem_lech@1`, `tra_cuu.phan_loai_tai_lieu@1`, `tra_cuu.phan_tich_cau_hoi@1`, `tra_cuu.xep_hang_lai@1`, `tra_cuu.soan_tra_loi@1` |
| `van_ban_da_che` | Văn bản đã che định danh | `mask.hau_kiem_tep_van_ban@1`, `mask.hau_kiem_ai_cuc_bo@1`, `mask.che_van_ban@1` | — (chưa có) |
| `bang_trich_xuat` | Bảng tham số đã trích | `trich.hau_kiem@1` | `trich.xuat_ket_qua@1` |
| `ho_so_doi_chieu` | Hồ sơ đối chiếu giữa các bước | `doi_chieu.nhan_cap@1`, `doi_chieu.so_van_ban@1`, `doi_chieu.phat_hien_sua_tay@1`, `doi_chieu.phan_loai_diem_lech@1` | `doi_chieu.so_van_ban@1`, `doi_chieu.phat_hien_sua_tay@1`, `doi_chieu.chuan_bi_ai@1`, `doi_chieu.xuat_ket_qua@1` |
| `ho_so_tra_cuu` | Hồ sơ tra cứu giữa các bước | `tra_cuu.nhan_yeu_cau@1`, `tra_cuu.cat_doan@1`, `tra_cuu.phan_loai_tai_lieu@1`, `tra_cuu.phan_tich_cau_hoi@1`, `tra_cuu.xep_hang_lai@1`, `tra_cuu.soan_tra_loi@1` | `tra_cuu.cat_doan@1`, `tra_cuu.chuan_bi_ai@1`, `tra_cuu.soan_tra_loi@1`, `tra_cuu.xuat_ket_qua@1` |

Module **không đọc** các loại này: chúng chỉ đi giữa các bước. Định nghĩa đầy đủ: `_chung/docs/LOAI-DU-LIEU-RIENG.md`.

## 5. Chi tiết từng năng lực (sinh từ `engine.json`)

### e_ocr — Nhận dạng văn bản (gói 1.0.9)

Loại dữ liệu riêng: `van_ban_tai_lieu`. Số việc đồng thời: 1.

#### `ocr.doc_tai_lieu@1` — Đọc tài liệu có vị trí

- **Nhận:** `tep` → **Trả:** `van_ban_tai_lieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 900 giây; loại tệp: `application/pdf`, `image/png`, `image/jpeg`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `nguon` | Nguồn đọc | chọn | không | `"tu_dong"` | `tu_dong` (Tự động), `chi_abbyy` (Chỉ ABBYY), `chi_tesseract` (Chỉ Tesseract) |


#### `ocr.doc_van_ban@1` — Đọc văn bản thuần

- **Nhận:** `tep` → **Trả:** `van_ban` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 900 giây; loại tệp: `application/pdf`, `image/png`, `image/jpeg`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `nguon` | Nguồn đọc | chọn | không | `"tu_dong"` | `tu_dong` (Tự động), `chi_abbyy` (Chỉ ABBYY), `chi_tesseract` (Chỉ Tesseract) |


#### `ocr.xuat_word@1` — Xuất Word giữ bảng

- **Nhận:** `tep` → **Trả:** `tep` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 900 giây; loại tệp: `application/pdf`, `image/png`, `image/jpeg`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `nguon` | Nguồn đọc | chọn | không | `"tu_dong"` | `tu_dong` (Tự động), `chi_abbyy` (Chỉ ABBYY), `chi_tesseract` (Chỉ Tesseract) |


### e_hoi_ai — Hỏi AI (gói 0.12.0)

Loại dữ liệu riêng: `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`. Số việc đồng thời: 1.

#### `ai.hoi_tai_lieu@1` — Hỏi tài liệu

- **Nhận:** `van_ban`, `van_ban_tai_lieu` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 600 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `ma_prompt` | Mã prompt của chức năng | văn bản | có | trống | — |
| `phien_ban_prompt` | Phiên bản prompt | văn bản | có | trống | — |
| `prompt` | Yêu cầu của chức năng | văn bản | có | trống | — |
| `model_uu_tien` | Model ưu tiên | văn bản | không | trống | — |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tra_loi` | Trả lời | văn bản |
| `co_can_cu` | Có căn cứ | có/không |
| `trich_dan` | Trích dẫn (mỗi câu một dòng) | văn bản |
| `model` | Model | văn bản |
| `ly_do_chon_model` | Lý do chọn model | văn bản |

#### `ai.hoi_theo_yeu_cau@1` — Hỏi theo yêu cầu

- **Nhận:** `yeu_cau_ai` → **Trả:** `tra_loi_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 600 giây; hủy được: có

#### `ai.hoi_mask_cuc_bo@1` — Nhận diện thực thể bằng Local AI

- **Nhận:** `yeu_cau_ai` → **Trả:** `tra_loi_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 600 giây; hủy được: có

### e_mask — Che định danh (gói 1.6.1)

Loại dữ liệu riêng: `yeu_cau_ai`, `van_ban_tai_lieu`, `tra_loi_ai`, `van_ban_da_che`. Số việc đồng thời: 1.

#### `mask.mo_che_tep@1` — Mở che tệp trong cùng chu kỳ

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 1 MiB; thời hạn 300 giây; loại tệp: `application/json`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `dong_viec` | Đóng việc sau khi mở | có/không | không | `false` | — |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tep_da_mo_che` | Tệp đã mở che | tệp |
| `so_cho_mo` | Số chỗ mở | số |
| `bi_danh_khong_ro_json` | Bí danh chưa mở JSON | văn bản |
| `mo_day_du` | Mở đầy đủ | có/không |
| `trang_thai_ma_yeu_cau` | Trạng thái yêu cầu | văn bản |

#### `mask.chuan_bi_tep_ai_cuc_bo@1` — Chuẩn bị tệp cho AI cục bộ

- **Nhận:** `tep` → **Trả:** `yeu_cau_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 1 MiB; thời hạn 300 giây; loại tệp: `application/json`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; hủy được: có

#### `mask.hau_kiem_tep_van_ban@1` — Hậu kiểm tệp và trả văn bản đã che

- **Nhận:** `tra_loi_ai` → **Trả:** `van_ban_da_che` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** ≤ 1.048.576 ký tự; thời hạn 300 giây; hủy được: có

#### `mask.hau_kiem_tep_giu_dinh_dang@1` — Hậu kiểm tệp và giữ định dạng

- **Nhận:** `tra_loi_ai` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** ≤ 1.048.576 ký tự; thời hạn 300 giây; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tep_da_che` | Tệp đã che | tệp |
| `ma_yeu_cau` | Mã yêu cầu | văn bản |
| `con_sot_json` | Còn sót JSON | văn bản |
| `kiem_tien_ngay` | Kiểm tiền ngày | có/không |
| `so_cho_thay` | Số chỗ thay | số |
| `bi_danh_json` | Bí danh JSON | văn bản |
| `so_cum_vua_them` | Số cụm vừa thêm | số |
| `vung_da_quet_json` | Vùng đã quét JSON | văn bản |
| `canh_bao_json` | Cảnh báo JSON | văn bản |

#### `mask.hau_kiem_ai_cuc_bo@1` — Hậu kiểm AI cục bộ và che bổ sung

- **Nhận:** `tra_loi_ai` → **Trả:** `van_ban_da_che` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 64 MiB; ≤ 1.048.576 ký tự; thời hạn 60 giây; loại tệp: `application/json`; hủy được: có

#### `mask.chuan_bi_ai_cuc_bo@1` — Chuẩn bị AI cục bộ nhận diện định danh

- **Nhận:** `van_ban`, `van_ban_tai_lieu`, `tep` → **Trả:** `yeu_cau_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 4 MiB; ≤ 500.000 ký tự; thời hạn 60 giây; loại tệp: `application/json`; hủy được: có

#### `mask.che_van_ban@1` — Che văn bản

- **Nhận:** `van_ban`, `van_ban_tai_lieu`, `tep` → **Trả:** `van_ban_da_che` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 60 giây; hủy được: có

#### `mask.mo_che_van_ban@1` — Mở che văn bản

- **Nhận:** `tra_loi_ai`, `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 60 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `dong_viec` | Đóng việc sau khi mở | có/không | không | `false` | — |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `van_ban_da_mo_che` | Văn bản đã mở che | văn bản |
| `so_cho_mo` | Số chỗ mở | số |
| `bi_danh_khong_ro_json` | Bí danh chưa mở JSON | văn bản |
| `mo_day_du` | Mở đầy đủ | có/không |
| `trang_thai_ma_yeu_cau` | Trạng thái yêu cầu | văn bản |
| `tra_loi_ai_da_mo_json` | Trả lời AI đã mở JSON | văn bản |

### e_trich_xuat — Trích thông tin hợp đồng (gói 0.5.0)

Loại dữ liệu riêng: `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, `bang_trich_xuat`. Số việc đồng thời: 1.

#### `trich.doc_docx@1` — Đọc hợp đồng Word

- **Nhận:** `tep` → **Trả:** `van_ban_tai_lieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; loại tệp: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`; hủy được: có

#### `trich.chuan_bi@1` — Chuẩn bị trích thông tin

- **Nhận:** `van_ban_tai_lieu` → **Trả:** `yeu_cau_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 120 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `bo_tham_so_json` | Bộ tham số đã ghim của việc (JSON) | văn bản | không | trống | — |
| `bam_bo_tham_so` | Mã kiểm tra snapshot bộ tham số | văn bản | không | trống | — |
| `ma_prompt` | Mã hướng dẫn của module | văn bản | không | trống | — |
| `phien_ban_prompt` | Phiên bản hướng dẫn đã ghim | văn bản | không | trống | — |
| `prompt` | Hướng dẫn trích thông tin của module | văn bản | không | trống | — |
| `model_uu_tien` | Model ưu tiên | văn bản | không | trống | — |
| `ma_truong_can_trich_json` | Danh sách mã cần trích (JSON) | văn bản | không | `"[]"` | — |
| `yeu_cau_them_json` | Câu hỏi bổ sung (chưa bật) | văn bản | không | `"[]"` | — |
| `ngan_sach_token_vao` | Ngân sách đầu vào (token ước lượng) | số | không | `16000` | — |


#### `trich.hau_kiem@1` — Hậu kiểm thông tin trích xuất

- **Nhận:** `tra_loi_ai` → **Trả:** `bang_trich_xuat` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; hủy được: có

#### `trich.xuat_ket_qua@1` — Xuất kết quả JSON và Excel

- **Nhận:** `bang_trich_xuat` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tep_json` | Tệp JSON | tệp |
| `tep_excel` | Tệp Excel | tệp |
| `so_tham_so` | Số tham số | số |
| `so_can_soat` | Số cần soát | số |
| `co_can_cu` | Có căn cứ | có/không |

### e_hoa_don — Đọc XML hóa đơn (gói 1.0.0)

Loại dữ liệu riêng: không. Số việc đồng thời: 1.

#### `hoa_don.doc_xml@2` — Đọc XML hóa đơn

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 16 MiB; thời hạn 600 giây; loại tệp: `application/xml`, `text/xml`; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `mau_so` | Mẫu số | văn bản |
| `ky_hieu` | Ký hiệu | văn bản |
| `so_hoa_don` | Số hóa đơn | văn bản |
| `ngay_lap` | Ngày lập | ngày |
| `ma_so_thue_ban` | Mã số thuế bên bán | văn bản |
| `ma_so_thue_mua` | Mã số thuế bên mua | văn bản |
| `don_vi_tien` | Đơn vị tiền | văn bản |
| `tien_truoc_thue` | Tiền trước thuế | số tiền |
| `tien_thue` | Tiền thuế | số tiền |
| `tong_thanh_toan` | Tổng thanh toán | số tiền |
| `so_dong` | Số dòng nguồn | số |
| `can_kiem_tra` | Cần kiểm tra | có/không |
| `canh_bao` | Cảnh báo | văn bản |
| `tep_xml` | Tệp XML nguồn | tệp |
| `chi_tiet_nguon` | Chi tiết nguồn | tệp |
| `nguon_doc` | Nguồn đọc | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |
| `bam_dau_vao` | Băm đầu vào | văn bản |

#### `hoa_don.doc_zip@1` — Đọc gói ZIP hóa đơn

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 600 giây; loại tệp: `application/zip`, `application/x-zip-compressed`; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tep_zip` | Tệp ZIP nguồn | tệp |
| `chi_tiet_nguon` | Báo cáo kiểm kê | tệp |
| `so_tep` | Số tệp | số |
| `so_doc_duoc` | Số tệp đọc được | số |
| `so_loi` | Số tệp lỗi | số |
| `so_khong_ho_tro` | Số tệp chưa hỗ trợ | số |
| `so_trung_noi_dung` | Số tệp trùng nội dung | số |
| `da_doc_het` | Đã đọc hết tệp trong gói | có/không |
| `can_kiem_tra` | Cần kiểm tra | có/không |
| `canh_bao` | Cảnh báo | văn bản |
| `bam_dau_vao` | Băm đầu vào | văn bản |
| `nguon_doc` | Nguồn đọc | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

#### `hoa_don.bang_ke_xlsx@1` — Lập bảng kê hóa đơn XLSX

- **Nhận:** `truong` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 600 giây; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `bang_ke` | Bảng kê | tệp |
| `chi_tiet_nguon` | Chi tiết nguồn | tệp |
| `so_hoa_don` | Số hóa đơn | số |
| `so_loi` | Số lỗi | số |
| `so_khong_ho_tro` | Số tệp chưa hỗ trợ | số |
| `so_trung_noi_dung` | Số tệp trùng nội dung | số |
| `da_doc_het` | Đã đọc hết | có/không |
| `can_kiem_tra` | Cần kiểm tra | có/không |
| `canh_bao` | Cảnh báo | văn bản |
| `bam_dau_vao` | Băm JSON đầu vào | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

### e_kiem_excel — Kiểm và đọc file Excel (gói 0.1.1)

Loại dữ liệu riêng: không. Số việc đồng thời: 1.

#### `excel.toan_ven@1` — Kiểm tính toàn vẹn file Excel

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; loại tệp: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/vnd.ms-excel.sheet.macroenabled.12`, `application/octet-stream`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `o_dich` | Ô đích cần truy vết | văn bản | không | trống | ≤ 512 ký tự |
| `nhan_o_dich_json` | Nhãn tự tìm ô đích (JSON) | văn bản | không | trống | ≤ 4096 ký tự |
| `bo_nhom_json` | Bộ nhóm dữ liệu gốc (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `kiem_nguon_kl` | Kiểm nguồn khối lượng (K8) | có/không | không | `false` | — |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `so_co_cao` | Số cờ mức Cao | số |
| `so_co_trung_binh` | Số cờ mức Trung bình | số |
| `so_kiem_soat` | Số mục cần kiểm soát | số |
| `so_ngoai_nhom` | Số ô nhập tay ngoài nhóm | số |
| `o_dich` | Ô đích đã dùng | văn bản |
| `da_tinh_lai` | File đã tính lại | có/không |
| `co_lien_ket_ngoai` | Có liên kết file ngoài đang dùng | có/không |
| `tep_bao_cao` | Báo cáo Lớp 1 (Excel) | tệp |
| `tep_json` | Kết quả chi tiết (JSON) | tệp |
| `bam_dau_vao` | Mã băm tệp vào | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

#### `excel.doc_bang@1` — Đọc bảng Excel nhiều tầng tiêu đề

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; loại tệp: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/vnd.ms-excel.sheet.macroenabled.12`, `application/octet-stream`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `khuon` | Khuôn đọc bảng | chọn | có | `"xay_dung_klgt"` | `xay_dung_klgt` (Bảng khối lượng xây dựng), `tong_quat` (Bảng theo khuôn cột) |
| `khuon_cot_json` | Khuôn cột (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `tien_te` | Mã tiền tệ ISO | văn bản | không | trống | ≤ 3 ký tự |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tep_json` | Bảng đã đọc (JSON) | tệp |
| `sheet` | Sheet chứa bảng | văn bản |
| `dong_tieu_de` | Dòng tiêu đề | số |
| `so_dong` | Số dòng dữ liệu | số |
| `so_dong_nhom` | Số dòng tiêu đề nhóm | số |
| `so_canh_bao` | Số cảnh báo | số |
| `gia_tri_hop_dong` | Giá trị hợp đồng | số tiền |
| `gia_tri_de_nghi` | Giá trị đề nghị thanh toán kỳ này | số tiền |
| `tien_te_chua_ro` | Tiền tệ chưa rõ | có/không |
| `bam_dau_vao` | Mã băm tệp vào | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

### e_phan_luong — Phân luồng kiểm tra (gói 0.1.0)

Loại dữ liệu riêng: `yeu_cau_ai`, `tra_loi_ai`. Số việc đồng thời: 1.

#### `audit.phan_luong@1` — Phân luồng kiểm tra

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 300 giây; loại tệp: `application/json`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `text/csv`, `application/vnd.ms-excel`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `khau` | Mã khâu duyệt | văn bản | có | trống | ≥ 1 · ≤ 40 ký tự |
| `ma_module` | Mã module | văn bản | không | trống | ≤ 31 ký tự |
| `nguong_json` | Ngưỡng PM/TE/SAD (JSON) | văn bản | không | trống | ≤ 4096 ký tự |
| `danh_muc_loai_json` | Danh mục loại nghiệp vụ (JSON) | văn bản | không | trống | ≤ 16384 ký tự |
| `truong_phan_loai` | Trường nội dung để phân loại | văn bản | không | trống | ≤ 60 ký tự |
| `bo_phan_loai_json` | Bộ quy tắc phân loại (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `chinh_sach_json` | Chính sách kiểm tra (JSON) | văn bản | không | trống | ≤ 8192 ký tự |
| `ty_le_duoi_sad` | Tỷ lệ kiểm dưới SAD | số | không | `0.02` | ≥ 0 · ≤ 1 |
| `cua_so_chia_nho_ngay` | Cửa sổ chống chia nhỏ (ngày) | số | không | `7` | ≥ 1 |
| `khuon_cot_json` | Khuôn cột Excel/CSV (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `tien_te` | Mã tiền tệ | văn bản | không | trống | ≤ 3 ký tự |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `ma_luot` | Mã lượt phân luồng | văn bản |
| `luong` | Luồng | văn bản |
| `can_nguoi_kiem` | Cần người kiểm | có/không |
| `canh_bao` | Cảnh báo | văn bản |
| `so_nghiep_vu` | Số nghiệp vụ | số |
| `so_do` | Số dòng Đỏ | số |
| `so_do_bat_buoc` | Số dòng Đỏ bắt buộc | số |
| `so_do_chon_mau` | Số dòng Đỏ chọn mẫu | số |
| `so_xanh` | Số dòng Xanh | số |
| `so_chua_phan_loai` | Số dòng chưa phân loại | số |
| `tong_tien_do` | Tổng tiền luồng Đỏ | số tiền |
| `tep_json` | Kết quả chi tiết | tệp |
| `tep_ds_do` | Danh sách cần kiểm (Excel) | tệp |
| `bam_hat_giong` | Băm hạt giống | văn bản |
| `bam_dau_vao` | Băm đầu vào | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

#### `audit.chuan_bi_phan_loai@1` — Chuẩn bị phân loại bằng Local AI

- **Nhận:** `tep` → **Trả:** `yeu_cau_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 300 giây; loại tệp: `application/json`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `text/csv`, `application/vnd.ms-excel`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `khau` | Mã khâu duyệt | văn bản | có | trống | ≥ 1 · ≤ 40 ký tự |
| `ma_module` | Mã module | văn bản | không | trống | ≤ 31 ký tự |
| `nguong_json` | Ngưỡng PM/TE/SAD (JSON) | văn bản | không | trống | ≤ 4096 ký tự |
| `danh_muc_loai_json` | Danh mục loại nghiệp vụ (JSON) | văn bản | không | trống | ≤ 16384 ký tự |
| `truong_phan_loai` | Trường nội dung để phân loại | văn bản | không | trống | ≤ 60 ký tự |
| `bo_phan_loai_json` | Bộ quy tắc phân loại (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `chinh_sach_json` | Chính sách kiểm tra (JSON) | văn bản | không | trống | ≤ 8192 ký tự |
| `ty_le_duoi_sad` | Tỷ lệ kiểm dưới SAD | số | không | `0.02` | ≥ 0 · ≤ 1 |
| `cua_so_chia_nho_ngay` | Cửa sổ chống chia nhỏ (ngày) | số | không | `7` | ≥ 1 |
| `khuon_cot_json` | Khuôn cột Excel/CSV (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `tien_te` | Mã tiền tệ | văn bản | không | trống | ≤ 3 ký tự |
| `ma_prompt` | Mã hướng dẫn của module | văn bản | không | trống | — |
| `phien_ban_prompt` | Phiên bản hướng dẫn | văn bản | không | trống | — |
| `prompt` | Hướng dẫn phân loại của module | văn bản | không | trống | — |
| `model_uu_tien` | Model ưu tiên | văn bản | không | trống | — |


#### `audit.phan_luong_sau_ai@1` — Phân luồng sau Local AI

- **Nhận:** `tra_loi_ai` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 300 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `khau` | Mã khâu duyệt | văn bản | có | trống | ≥ 1 · ≤ 40 ký tự |
| `ma_module` | Mã module | văn bản | không | trống | ≤ 31 ký tự |
| `nguong_json` | Ngưỡng PM/TE/SAD (JSON) | văn bản | không | trống | ≤ 4096 ký tự |
| `danh_muc_loai_json` | Danh mục loại nghiệp vụ (JSON) | văn bản | không | trống | ≤ 16384 ký tự |
| `truong_phan_loai` | Trường nội dung để phân loại | văn bản | không | trống | ≤ 60 ký tự |
| `bo_phan_loai_json` | Bộ quy tắc phân loại (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `chinh_sach_json` | Chính sách kiểm tra (JSON) | văn bản | không | trống | ≤ 8192 ký tự |
| `ty_le_duoi_sad` | Tỷ lệ kiểm dưới SAD | số | không | `0.02` | ≥ 0 · ≤ 1 |
| `cua_so_chia_nho_ngay` | Cửa sổ chống chia nhỏ (ngày) | số | không | `7` | ≥ 1 |
| `nguong_tin_cay` | Ngưỡng tin cậy phân loại AI | số | không | `0.7` | ≥ 0 · ≤ 1 |
| `khuon_cot_json` | Khuôn cột Excel/CSV (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `tien_te` | Mã tiền tệ | văn bản | không | trống | ≤ 3 ký tự |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `ma_luot` | Mã lượt phân luồng | văn bản |
| `luong` | Luồng | văn bản |
| `can_nguoi_kiem` | Cần người kiểm | có/không |
| `canh_bao` | Cảnh báo | văn bản |
| `so_nghiep_vu` | Số nghiệp vụ | số |
| `so_do` | Số dòng Đỏ | số |
| `so_do_bat_buoc` | Số dòng Đỏ bắt buộc | số |
| `so_do_chon_mau` | Số dòng Đỏ chọn mẫu | số |
| `so_xanh` | Số dòng Xanh | số |
| `so_chua_phan_loai` | Số dòng chưa phân loại | số |
| `tong_tien_do` | Tổng tiền luồng Đỏ | số tiền |
| `tep_json` | Kết quả chi tiết | tệp |
| `tep_ds_do` | Danh sách cần kiểm (Excel) | tệp |
| `bam_hat_giong` | Băm hạt giống | văn bản |
| `bam_dau_vao` | Băm đầu vào | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

#### `audit.phan_luong_hoa_don@1` — Phân luồng hóa đơn

- **Nhận:** `truong` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 300 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `khau` | Mã khâu duyệt | văn bản | có | trống | ≥ 1 · ≤ 40 ký tự |
| `ma_module` | Mã module | văn bản | không | trống | ≤ 31 ký tự |
| `nguong_json` | Ngưỡng PM/TE/SAD (JSON) | văn bản | không | trống | ≤ 4096 ký tự |
| `danh_muc_loai_json` | Danh mục loại nghiệp vụ (JSON) | văn bản | không | trống | ≤ 16384 ký tự |
| `truong_phan_loai` | Trường nội dung để phân loại | văn bản | không | trống | ≤ 60 ký tự |
| `bo_phan_loai_json` | Bộ quy tắc phân loại (JSON) | văn bản | không | trống | ≤ 32768 ký tự |
| `chinh_sach_json` | Chính sách kiểm tra (JSON) | văn bản | không | trống | ≤ 8192 ký tự |
| `ty_le_duoi_sad` | Tỷ lệ kiểm dưới SAD | số | không | `0.02` | ≥ 0 · ≤ 1 |
| `cua_so_chia_nho_ngay` | Cửa sổ chống chia nhỏ (ngày) | số | không | `7` | ≥ 1 |
| `loai_nghiep_vu` | Loại nghiệp vụ hóa đơn | văn bản | không | trống | — |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `ma_luot` | Mã lượt phân luồng | văn bản |
| `luong` | Luồng | văn bản |
| `can_nguoi_kiem` | Cần người kiểm | có/không |
| `canh_bao` | Cảnh báo | văn bản |
| `so_nghiep_vu` | Số nghiệp vụ | số |
| `so_do` | Số dòng Đỏ | số |
| `so_do_bat_buoc` | Số dòng Đỏ bắt buộc | số |
| `so_do_chon_mau` | Số dòng Đỏ chọn mẫu | số |
| `so_xanh` | Số dòng Xanh | số |
| `so_chua_phan_loai` | Số dòng chưa phân loại | số |
| `tong_tien_do` | Tổng tiền luồng Đỏ | số tiền |
| `tep_json` | Kết quả chi tiết | tệp |
| `tep_ds_do` | Danh sách cần kiểm (Excel) | tệp |
| `bam_hat_giong` | Băm hạt giống | văn bản |
| `bam_dau_vao` | Băm đầu vào | văn bản |
| `phien_ban_engine` | Phiên bản engine | văn bản |

#### `audit.ghi_ket_qua@1` — Ghi kết quả kiểm

- **Nhận:** `tep` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 300 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `khau` | Mã khâu duyệt | văn bản | có | trống | ≥ 1 · ≤ 40 ký tự |
| `ma_module` | Mã module | văn bản | không | trống | ≤ 31 ký tự |
| `nguong_json` | Ngưỡng PM/TE/SAD (JSON) | văn bản | không | trống | ≤ 4096 ký tự |
| `danh_muc_loai_json` | Danh mục loại nghiệp vụ (JSON) | văn bản | không | trống | ≤ 16384 ký tự |
| `chinh_sach_json` | Chính sách kiểm tra (JSON) | văn bản | không | trống | ≤ 8192 ký tự |

- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `so_dong_nhan` | Số dòng nhận | số |
| `so_trung` | Số dòng trùng | số |
| `so_ngoai_mau` | Số dòng ngoài mẫu | số |
| `so_cap_doi_bac` | Số cặp đổi bậc | số |
| `so_sua_loai` | Số lần sửa loại | số |
| `phien_ban_engine` | Phiên bản engine | văn bản |

### e_doi_chieu — Đối chiếu bản ký (gói 0.9.0)

Loại dữ liệu riêng: `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, `ho_so_doi_chieu`. Số việc đồng thời: 1.

#### `doi_chieu.doc_docx@1` — Đọc bản Word

- **Nhận:** `tep` → **Trả:** `van_ban_tai_lieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; loại tệp: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`; hủy được: có

#### `doi_chieu.nhan_cap@1` — Nhận cặp tài liệu đối chiếu

- **Nhận:** `tep` → **Trả:** `ho_so_doi_chieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; loại tệp: `application/json`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `bam_yeu_cau` | Băm yêu cầu đã ghim | văn bản | có | trống | ≤ 71 ký tự |


#### `doi_chieu.so_van_ban@1` — So văn bản hai bên

- **Nhận:** `ho_so_doi_chieu` → **Trả:** `ho_so_doi_chieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 300 giây; loại tệp: `application/json`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `bo_quy_tac_json` | Bộ quy tắc đã ghim | văn bản | có | trống | ≤ 65536 ký tự |
| `bam_bo_quy_tac` | Băm bộ quy tắc | văn bản | có | trống | ≤ 71 ký tự |


#### `doi_chieu.phat_hien_sua_tay@1` — Phát hiện vùng nghi sửa tay

- **Nhận:** `ho_so_doi_chieu` → **Trả:** `ho_so_doi_chieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 900 giây; loại tệp: `application/json`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `che_do` | Phạm vi quét | chọn | không | `"day_du"` | `day_du` (Quét đủ ảnh trang) |


#### `doi_chieu.chuan_bi_ai@1` — Chuẩn bị phân loại bằng Local AI

- **Nhận:** `ho_so_doi_chieu` → **Trả:** `yeu_cau_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 300 giây; loại tệp: `application/json`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `module` | Module cung cấp prompt (bắt buộc) | văn bản | không | trống | — |
| `ma_prompt` | Mã prompt (bắt buộc) | văn bản | không | trống | — |
| `phien_ban_prompt` | Phiên bản prompt (bắt buộc) | văn bản | không | trống | — |
| `prompt` | Nội dung prompt (bắt buộc) | văn bản | không | trống | — |
| `model_uu_tien` | Model Local ưu tiên | văn bản | không | trống | — |


#### `doi_chieu.phan_loai_diem_lech@1` — Hậu kiểm phân loại Local AI

- **Nhận:** `tra_loi_ai` → **Trả:** `ho_so_doi_chieu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 300 giây; loại tệp: `application/json`; hủy được: có

#### `doi_chieu.xuat_ket_qua@1` — Xuất kết quả JSON và PDF

- **Nhận:** `ho_so_doi_chieu` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** ≤ 500.000 ký tự; thời hạn 180 giây; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `ket_luan` | Kết luận | văn bản |
| `so_nghiem_trong` | Số điểm Nghiêm trọng | số |
| `so_can_xem` | Số điểm Cần xem | số |
| `so_hinh_thuc` | Số điểm hình thức | số |
| `so_nhieu_ocr` | Số điểm nhiễu OCR | số |
| `so_vung_sua_tay` | Số vùng sửa tay | số |
| `so_trang_ocr_kem` | Số trang OCR kém | số |
| `da_kiem_du` | Đã kiểm đủ | có/không |
| `de_nghi_chan` | Đề nghị chặn | có/không |
| `tep_json` | Báo cáo JSON | tệp |
| `tep_pdf` | Báo cáo PDF | tệp |

### e_tra_cuu — Tra cứu tài liệu (gói 0.2.0)

Loại dữ liệu riêng: `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, `ho_so_tra_cuu`. Số việc đồng thời: 1.

#### `tra_cuu.nhan_yeu_cau@1` — Nhận yêu cầu tra cứu

- **Nhận:** `tep` → **Trả:** `ho_so_tra_cuu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; thời hạn 120 giây; loại tệp: `application/json`; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `bam_yeu_cau` | Băm tệp yêu cầu | văn bản | có | trống | ≤ 71 ký tự |


#### `tra_cuu.cat_doan@1` — Cắt đoạn tài liệu

- **Nhận:** `ho_so_tra_cuu` → **Trả:** `ho_so_tra_cuu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 120 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `do_dai_muc_tieu` | Độ dài mục tiêu | số | không | `2000` | ≥ 200 · ≤ 8000 |


#### `tra_cuu.chuan_bi_ai@1` — Chuẩn bị yêu cầu AI

- **Nhận:** `ho_so_tra_cuu` → **Trả:** `yeu_cau_ai` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 180 giây; hủy được: có
- **Cài đặt bước:**

| Mã | Tên | Kiểu | Bắt buộc | Mặc định | Lựa chọn / trần |
|---|---|---|---|---|---|
| `tac_vu` | Tác vụ | chọn | có | trống | `phan_loai` (Phân loại), `phan_tich_cau_hoi` (Phân tích câu hỏi), `xep_hang_lai` (Xếp hạng lại), `soan_tra_loi` (Soạn trả lời) |
| `ma_prompt` | Mã prompt | văn bản | có | trống | ≤ 200 ký tự |
| `phien_ban_prompt` | Phiên bản prompt | văn bản | có | trống | ≤ 100 ký tự |
| `prompt` | Prompt của module | văn bản | có | trống | ≤ 16000 ký tự |
| `model_uu_tien` | Model ưu tiên | văn bản | không | trống | ≤ 200 ký tự |


#### `tra_cuu.phan_loai_tai_lieu@1` — Hậu kiểm phân loại

- **Nhận:** `tra_loi_ai` → **Trả:** `ho_so_tra_cuu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 180 giây; hủy được: có

#### `tra_cuu.phan_tich_cau_hoi@1` — Hậu kiểm phân tích câu hỏi

- **Nhận:** `tra_loi_ai` → **Trả:** `ho_so_tra_cuu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 180 giây; hủy được: có

#### `tra_cuu.xep_hang_lai@1` — Hậu kiểm xếp hạng lại

- **Nhận:** `tra_loi_ai` → **Trả:** `ho_so_tra_cuu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 180 giây; hủy được: có

#### `tra_cuu.soan_tra_loi@1` — Soạn và kiểm câu trả lời

- **Nhận:** `tra_loi_ai`, `ho_so_tra_cuu` → **Trả:** `ho_so_tra_cuu` (chỉ dùng ở giữa chuỗi)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 180 giây; hủy được: có

#### `tra_cuu.xuat_ket_qua@1` — Xuất kết quả tra cứu

- **Nhận:** `ho_so_tra_cuu` → **Trả:** `truong` (ghép được vào cột ngăn)
- **Giới hạn:** tệp ≤ 20 MiB; ≤ 500.000 ký tự; thời hạn 120 giây; hủy được: có
- **Trường trả ra (ghép vào cột ngăn của module):**

| Mã | Tên | Kiểu |
|---|---|---|
| `tac_vu` | Tác vụ | văn bản |
| `trang_thai` | Trạng thái | văn bản |
| `tra_loi` | Trả lời | văn bản |
| `nhan` | Nhãn | văn bản |
| `nhom_de_xuat` | Nhóm đề xuất | văn bản |
| `loai_de_xuat` | Loại đề xuất | văn bản |
| `tang` | Tầng | số |
| `so_doan` | Số đoạn | số |
| `so_ung_vien` | Số ứng viên | số |
| `co_can_cu` | Có căn cứ | có/không |
| `co_mau_thuan` | Có mâu thuẫn | có/không |
| `can_duyet` | Cần duyệt | có/không |
| `tep_json` | Tệp JSON | tệp |
