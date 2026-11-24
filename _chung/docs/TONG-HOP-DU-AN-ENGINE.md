# TỔNG HỢP DỰ ÁN ENGINE — mục tiêu, kết quả, tên và năng lực chuẩn

*Lead (Claude) lập 24/11/2026 theo yêu cầu của Anh Dũng. Số liệu lấy từ `main` `2f01fa0` (PR #176), các bản phát hành `engines-20261115` → `engines-20261124` và `*/goi/*/engine.json`. Tệp này là **điểm vào duy nhất** để nắm toàn dự án; chi tiết nằm ở tài liệu được dẫn.*

**Kết luận nhanh**
- 9 engine, 44 năng lực đã có mã, test và gói phát hành (trừ Phân luồng chưa có bản phát hành trong repo này). **Tất cả mới kiểm bằng Core giả (CoreGia)**, chưa engine nào nối Core thật, nên chưa engine nào "SẴN SÀNG".
- Màn cấu hình đã làm xong cho mọi engine có cấu hình (11 lát UI, PR #156–#166), nhưng **chỉ hiện trong Core khi Core mở 4 cửa D, D2, E, F**. Đây là việc chặn lớn nhất, nằm phía Core.
- Tên hiển thị đang lệch nhau: chỗ ghi "Chuẩn bị…", chỗ "Hậu kiểm…", chỗ không nói bước AI. §5 đề xuất bộ tên chuẩn. **Đổi tên hiển thị không làm hỏng quy trình.** Mã năng lực là hợp đồng nên giữ nguyên.
- Còn 3 việc chờ Anh: duyệt bộ tên chuẩn (§5); duyệt SDK 2.5.0; chạy 4 tệp `.cmd` kiểm máy thật (§6).

---

## 1. Mục tiêu và nguyên tắc

**Mục tiêu:** tách các engine khỏi Core (từ 08/11/2026). Mỗi engine là một gói độc lập, gắn vào Core qua **một cổng chung** (API v1, SDK `kho_tri_thuc_sdk`, webhook). Module của Core chỉ cần ghép năng lực engine thành quy trình, không viết lại xử lý.

| Nguyên tắc | Nội dung | Nguồn |
|---|---|---|
| Cổng chung | Chỉ API v1 + `engine.json` 2.0 + SDK. Engine không gọi engine khác, không CSDL, không SQL lúc chạy | `docs/goi-gui-engine/API-ENGINE-v1.md`, `AGENTS.md` §4.1–2 |
| Nối chuỗi | Bước 1 nhận `tep`; bước k nhận đúng loại bước k−1 trả; bước cuối trả `truong`/`van_ban`/`tep` để ghép vào cột ngăn module | `DANH-MUC-ENGINE-CHO-MODULE.md` |
| Engine không lưu gì trên máy | Dữ liệu và cấu hình đi qua ngăn của Core (`viec.ngan`, `app.ngan`, `viec.cau_hinh`) | Quyết định 15/11 câu 1–2; `AGENTS.md` §4.12 |
| Cấu hình thuộc engine | Màn cấu hình ở `goi/<ma>/ui/`, nạp thẳng như màn module | Quyết định 15/11 câu 1, 13; `AGENTS.md` §4.13 |
| Cấu hình phải dễ dùng | Tốt nhất không nhập JSON thô; bắt buộc nhập thì có diễn giải cấu trúc, hướng dẫn, mẫu, báo lỗi đúng trường | Anh yêu cầu 21/11; `AGENTS.md` §4.14 |
| Cloud chỉ qua Mask | Cloud chỉ nhận `van_ban_da_che`; M9 và nhóm 07 luôn chỉ Local; Hỏi AI bản 1 chỉ Local | Quyết định 15/11 câu 4 |
| Prompt thuộc module | Engine Hỏi AI không có prompt sẵn; module gửi prompt | Anh chốt 24/11 (AI-13) |
| Dữ liệu | Chỉ DEMO; tiền luôn kèm mã tiền tệ; không tự gán VND | `AGENTS.md` §4.5, §4.8 |
| Cách làm | Codex viết mã theo lát (1 lát = 1 PR); lead lập phiếu, rà, gộp; trước khi nối Core thật chỉ ghi "đã kiểm bằng Core giả (CoreGia)" | `AGENTS.md` §5 |

## 2. Các mốc quyết định của Anh

| Ngày | Quyết định chính | Tài liệu |
|---|---|---|
| 08/11 | Tách engine khỏi Core, mỗi engine một project, chung một cổng | `README.md` |
| 14/11 | Giao Codex; thứ tự Hỏi AI + OCR → Trích xuất | `GIAO-CODEX-THU-TU.md` |
| 15/11 sáng | 13 câu: cấu hình ở engine, engine không lưu, 4 loại dữ liệu chung, Cloud chỉ qua Mask, phạm vi Hóa đơn (XML → ZIP + bảng kê), nạp màn engine như màn module… | `QUYET-DINH-ANH-20261115.md` |
| 15/11 chiều | Thêm AI cục bộ cho Mask trước Cloud; duyệt `bang_trich_xuat`, `ho_so_doi_chieu`, `ho_so_tra_cuu`; 17 câu Đối chiếu, 15 câu Tra cứu theo đề xuất (trừ TC-Q06); Mask tệp theo phương án B; mở che trong cùng chu kỳ, không lưu ánh xạ | `QUYET-DINH-ANH-20261115-CHIEU.md` |
| 16/11 | Duyệt tiến hành `e_kiem_excel` | `e_kiem_excel/docs/PHIEU-ENGINE-e_kiem_excel.md` |
| 20/11 | Duyệt phiếu `e_phan_luong` (Q1–Q7); yêu cầu danh mục engine cho module, tự sinh | `e_phan_luong/docs/GIAO-CODEX-e_phan_luong.md` §4 |
| 21/11 | Mọi cấu hình phải có màn dễ dùng (quy tắc 14); đóng gói lại kèm thư viện ngoại tuyến | `GIAO-CODEX-UI-CAU-HINH.md`; bản `engines-20261122b` |
| 24/11 | Prompt nằm trong module; thêm `ai.hoi_theo_prompt@1` | bản `engines-20261124` |

## 3. Đã làm được

- **176 PR** đã gộp (#1 ngày 14/11 → #176 ngày 24/11); không còn PR mở.
- **8 đợt phát hành** (nguồn: GitHub Releases của repo):

| Bản | Ngày | Nội dung |
|---|---|---|
| `engines-20261115` | 15/11 | Hóa đơn 1.0.0, Hỏi AI 0.12.0, OCR 1.0.9, Trích xuất 0.5.0 (SDK 2.2.0) |
| `engines-20261115b` | 15/11 | Đối chiếu 0.9.0, Tra cứu 0.2.0 |
| `engines-20261116` | 16/11 | Mask 1.6.0: che tệp **chưa đạt** (chặn nhầm 12/12 tệp hợp lệ) |
| `engines-20261117` | 16/11 | Mask 1.6.1: 19/19 tệp cần chặn bị chặn đúng; 12/12 tệp hợp lệ che và mở che đủ (bộ 31 tệp DEMO) |
| `engines-20261119` | 19/11 | Kiểm Excel 0.1.1 |
| `engines-20261122` | 22/11 | Màn cấu hình cho 7 engine (Hỏi AI 0.12.1, OCR 1.0.10, Trích xuất 0.5.1, Đối chiếu 0.9.1, Tra cứu 0.2.1, Mask 1.6.2, Kiểm Excel 0.1.2) |
| `engines-20261122b` | 22/11 | Đóng gói lại 4 engine kèm `wheels/` cho Core 2.5.x tự cài ngoại tuyến; chạy trên SDK 2.5.0 (OCR 1.0.11, Trích xuất 0.5.2, Đối chiếu 0.9.2, Kiểm Excel 0.1.3) |
| `engines-20261124` | 24/11 | Hỏi AI 0.13.0: `ai.hoi_theo_prompt@1` |

- **Hạ tầng chung:**
  - 7 loại dữ liệu riêng đã duyệt (`LOAI-DU-LIEU-RIENG.md`);
  - danh mục engine cho module tự sinh, có kiểm chuỗi trong CI (`_chung/cong-cu/sinh_danh_muc_engine.py`, workflow `danh muc engine cho module`);
  - `AGENTS.md` có 14 quy tắc cứng.
- **Màn cấu hình:** 11 lát UI xong (PR #156–#166). Có ảnh mẫu `_chung/docs/mau-ui/`.

### Hiện trạng từng engine

| Engine | Bản | SDK | Cấu hình / ngăn / màn | Hiện trạng | Còn lại chính |
|---|---|---|---|---|---|
| `e_hoi_ai` | 0.13.0 | ≥2.2 | Có / Có / Có | Local xong, kiểm bằng Core giả và Local giả; pytest 721 ca (bản 24/11) | Chưa thử model thật; Cloud bản 2 chưa mở; CLI SDK báo `CHUA_CAU_HINH` vì thiếu cửa nạp cấu hình DEMO |
| `e_ocr` | 1.0.11 | ≥2.4 | Có / Có / Có | ABBYY Hot Folder + Tesseract, kiểm bằng giả lập | Anh chạy `KIEM-TESSERACT.cmd`, `THU-ABBYY-THAT.cmd`; xác nhận giấy phép FineReader |
| `e_mask` | 1.6.2 | ≥2.2 | Có / Có / Có | Che văn bản và tệp Word/Excel; mở che trong cùng chu kỳ | Chưa kiểm với Office và AI cục bộ thật; 2 lát B5b, B6b chưa đạt full xanh; hiệu năng văn bản 500.000 ký tự vượt trần 5 giây |
| `e_trich_xuat` | 0.5.2 | ≥2.4 | Có / — / Có | Trích hợp đồng bằng Local AI, xuất JSON/Excel | Đo thật sức chứa model; `truong_ra` động (C-TX-03) |
| `e_hoa_don` | 1.0.0 | ≥2.2 | — / — / — | XML, ZIP, bảng kê Excel | PDF và tải cổng thuế để sau (quyết định 15/11) |
| `e_kiem_excel` | 0.1.3 | ≥2.4 | — / — / Có (trình soạn bước) | Xong 7 lát EX-0…EX-6; pytest 240 passed (EX-6) | Xác nhận MIME với Core thật |
| `e_doi_chieu` | 0.9.2 | ≥2.4 | Có / Có / Có | So bản ký, phát hiện sửa tay, phân loại bằng Local AI | OCR vùng (C-DC-05); quyền từng tệp con (C-DC-02) |
| `e_tra_cuu` | 0.2.1 | ≥2.2 | Có / Có / Có | Hỏi đáp 3 tầng trên tài liệu | Cần **Kho tài liệu** phía Core; bộ đo 38 ca chưa duyệt nghiệp vụ; TC-Q06 chưa chốt |
| `e_phan_luong` | 0.1.0 | ≥2.2 | — / Có / Có | 5 năng lực Đỏ/Xanh, kiểm bằng Core giả; 1.123 test (PL-3) | Chưa có bản phát hành trong repo này; màn tỷ lệ chờ cửa D (CC-5) |

*Nguồn: `engine.json`, `<engine>/docs/VIEC.md`, ghi chú phát hành. "SDK ≥2.4" là 4 engine đã chuyển sang khai `phu_thuoc_python` và chạy SDK 2.5.0.*

## 4. Quy ước đặt tên (chuẩn hóa)

**4.1. Mã — là hợp đồng, không đổi tùy tiện**
- **Mã engine:** `e_<linh_vuc>`, tiếng Việt không dấu. Ví dụ `e_hoa_don`.
- **Mã năng lực:** `<nhom>.<dong_tu>[_<doi_tuong>]@<n>`.
  - `nhom` là tên nhóm đã đăng ký ở bảng 4.3.
  - `@n` tăng khi đổi hợp đồng (đổi `nhan`, `tra` hay ý nghĩa tham số).
- **Đổi mã năng lực đã phát hành sẽ làm hỏng quy trình module đã ghép.** Muốn đổi thì:
  1. thêm mã mới;
  2. giữ mã cũ, ghi "(cũ, giữ để tương thích)" trong tên;
  3. bỏ mã cũ sau khi mọi quy trình đã chuyển.

**4.2. Động từ dùng cho năng lực mới**

| Động từ mã | Tên hiển thị bắt đầu bằng | Dùng khi | Vai trò thường gặp |
|---|---|---|---|
| `doc_<nguon>` | Đọc … | Tệp → văn bản / trường | Đầu, hoặc trọn một bước |
| `nhan_<doi_tuong>` | Nhận … | Tệp yêu cầu → hồ sơ nội bộ | Đầu |
| `chuan_bi_ai[_<viec>]` | Chuẩn bị AI — … | → `yeu_cau_ai` | Giữa |
| `hau_kiem[_<viec>]` | Hậu kiểm AI — … | `tra_loi_ai` → … | Giữa / Cuối |
| `xuat_<dang>` / `xuat_ket_qua` | Xuất … | → `truong` / `tep` | Cuối |
| `che_`, `mo_che_`, `hoi_`, `kiem_`, `lap_`, `phan_luong_` | Che…, Mở che…, Hỏi…, Kiểm…, Lập…, Phân luồng… | Việc đặc thù của engine | Tùy |

**4.3. Tên nhóm và tên hiển thị engine**

| Mã engine | Nhóm năng lực | Tên hiển thị hiện tại | Tên chuẩn đề xuất | Ghi chú |
|---|---|---|---|---|
| `e_hoi_ai` | `ai` | Hỏi AI | Hỏi AI | Giữ |
| `e_ocr` | `ocr` | Nhận dạng văn bản | Nhận dạng văn bản (OCR) | Thêm "OCR" để dễ tìm |
| `e_mask` | `mask` | Che định danh | Che định danh (Mask) | Thêm "Mask" vì tài liệu quen dùng tên này |
| `e_trich_xuat` | `trich` | Trích thông tin hợp đồng | Trích thông tin hợp đồng | Giữ. Nhóm `trich` lệch tên engine, giữ vì là hợp đồng |
| `e_hoa_don` | `hoa_don` | Đọc XML hóa đơn | **Hóa đơn điện tử** | Tên cũ thiếu ZIP và bảng kê |
| `e_kiem_excel` | `excel` | Kiểm và đọc file Excel | Kiểm và đọc Excel | Bỏ từ "file" cho gọn. Nhóm `excel` giữ |
| `e_doi_chieu` | `doi_chieu` | Đối chiếu bản ký | Đối chiếu bản ký | Giữ |
| `e_tra_cuu` | `tra_cuu` | Tra cứu tài liệu | Tra cứu tài liệu | Giữ |
| `e_phan_luong` | `audit` | Phân luồng kiểm tra | Phân luồng kiểm tra | **Nhóm `audit` là từ tiếng Anh duy nhất.** Xem lựa chọn ở §6 |

## 5. Bảng năng lực chuẩn (44 năng lực)

Vai trò:
- **Trọn**: nhận `tep`, trả kết quả dùng được ngay; dùng một bước.
- **Đầu**: bước mở chuỗi.
- **Giữa**: bước nối giữa chuỗi.
- **Cuối**: bước trả `truong`/`tep` cho module.

"Cũ" là năng lực giữ để tương thích, không dùng cho quy trình mới. Cột "Tên chuẩn" chỉ đổi tên hiển thị; **mã giữ nguyên**.

| # | Mã năng lực (giữ) | Vào → ra | Vai trò | Tên hiện tại | Tên chuẩn đề xuất |
|---|---|---|---|---|---|
| **Hỏi AI** | | | | | |
| 1 | `ai.hoi_theo_prompt@1` | yeu_cau_ai / van_ban / van_ban_tai_lieu → truong | Trọn / Cuối | Hỏi AI theo prompt của module | *giữ* (**dùng cho quy trình mới**) |
| 2 | `ai.hoi_theo_yeu_cau@1` | yeu_cau_ai → tra_loi_ai | Giữa | Hỏi theo yêu cầu (có khung trích dẫn…) | Hỏi AI — khung trích dẫn (bước giữa chuỗi) |
| 3 | `ai.hoi_mask_cuc_bo@1` | yeu_cau_ai → tra_loi_ai | Giữa | Nhận diện thực thể bằng Local AI | Hỏi Local AI — nhận diện định danh cho Mask |
| 4 | `ai.hoi_tai_lieu@1` | van_ban / van_ban_tai_lieu → truong | Cũ | Hỏi tài liệu (có khung trích dẫn…) | Hỏi tài liệu — khung trích dẫn (cũ, giữ để tương thích) |
| **OCR** | | | | | |
| 5 | `ocr.doc_tai_lieu@1` | tep → van_ban_tai_lieu | Đầu | Đọc tài liệu có vị trí | *giữ* |
| 6 | `ocr.doc_van_ban@1` | tep → van_ban | Trọn / Đầu | Đọc văn bản thuần | *giữ* |
| 7 | `ocr.xuat_word@1` | tep → tep | Trọn | Xuất Word giữ bảng | Chuyển sang Word giữ bảng |
| **Mask** | | | | | |
| 8 | `mask.che_van_ban@1` | van_ban / van_ban_tai_lieu / tep → van_ban_da_che | Đầu / Giữa | Che văn bản | Che văn bản theo quy tắc |
| 9 | `mask.chuan_bi_ai_cuc_bo@1` | van_ban / van_ban_tai_lieu / tep → yeu_cau_ai | Đầu | Chuẩn bị AI cục bộ nhận diện định danh | Chuẩn bị AI — nhận diện định danh trong văn bản |
| 10 | `mask.hau_kiem_ai_cuc_bo@1` | tra_loi_ai → van_ban_da_che | Giữa | Hậu kiểm AI cục bộ và che bổ sung | Hậu kiểm AI — che bổ sung văn bản |
| 11 | `mask.chuan_bi_tep_ai_cuc_bo@1` | tep → yeu_cau_ai | Đầu | Chuẩn bị tệp cho AI cục bộ | Chuẩn bị AI — nhận diện định danh trong tệp |
| 12 | `mask.hau_kiem_tep_van_ban@1` | tra_loi_ai → van_ban_da_che | Giữa | Hậu kiểm tệp và trả văn bản đã che | Hậu kiểm AI — che tệp, trả văn bản đã che |
| 13 | `mask.hau_kiem_tep_giu_dinh_dang@1` | tra_loi_ai → truong | Cuối | Hậu kiểm tệp và giữ định dạng | Hậu kiểm AI — che tệp, giữ định dạng |
| 14 | `mask.mo_che_van_ban@1` | tra_loi_ai / tep → truong | Cuối | Mở che văn bản | *giữ* |
| 15 | `mask.mo_che_tep@1` | tep → truong | Cuối | Mở che tệp trong cùng chu kỳ | Mở che tệp (trong cùng chu kỳ) |
| **Trích xuất** | | | | | |
| 16 | `trich.doc_docx@1` | tep → van_ban_tai_lieu | Đầu | Đọc hợp đồng Word | Đọc tệp Word |
| 17 | `trich.chuan_bi@1` | van_ban_tai_lieu → yeu_cau_ai | Giữa | Chuẩn bị trích thông tin | Chuẩn bị AI — trích thông tin hợp đồng |
| 18 | `trich.hau_kiem@1` | tra_loi_ai → bang_trich_xuat | Giữa | Hậu kiểm thông tin trích xuất | Hậu kiểm AI — trích thông tin hợp đồng |
| 19 | `trich.xuat_ket_qua@1` | bang_trich_xuat → truong | Cuối | Xuất kết quả JSON và Excel | Xuất kết quả — JSON và Excel |
| **Hóa đơn** | | | | | |
| 20 | `hoa_don.doc_xml@2` | tep → truong | Trọn / Đầu | Đọc XML hóa đơn | *giữ* |
| 21 | `hoa_don.doc_zip@1` | tep → truong | Trọn / Đầu | Đọc gói ZIP hóa đơn | *giữ* |
| 22 | `hoa_don.bang_ke_xlsx@1` | truong → truong | Cuối | Lập bảng kê hóa đơn XLSX | Lập bảng kê hóa đơn (Excel) |
| **Kiểm Excel** | | | | | |
| 23 | `excel.toan_ven@1` | tep → truong | Trọn | Kiểm tính toàn vẹn file Excel | Kiểm toàn vẹn tệp Excel |
| 24 | `excel.doc_bang@1` | tep → truong | Trọn | Đọc bảng Excel nhiều tầng tiêu đề | *giữ* |
| **Đối chiếu** | | | | | |
| 25 | `doi_chieu.nhan_cap@1` | tep → ho_so_doi_chieu | Đầu | Nhận cặp tài liệu đối chiếu | *giữ* |
| 26 | `doi_chieu.so_van_ban@1` | ho_so_doi_chieu → ho_so_doi_chieu | Giữa | So văn bản hai bên | *giữ* |
| 27 | `doi_chieu.phat_hien_sua_tay@1` | ho_so_doi_chieu → ho_so_doi_chieu | Giữa | Phát hiện vùng nghi sửa tay | *giữ* |
| 28 | `doi_chieu.chuan_bi_ai@1` | ho_so_doi_chieu → yeu_cau_ai | Giữa | Chuẩn bị phân loại bằng Local AI | Chuẩn bị AI — phân loại điểm lệch |
| 29 | `doi_chieu.phan_loai_diem_lech@1` | tra_loi_ai → ho_so_doi_chieu | Giữa | Hậu kiểm phân loại Local AI | Hậu kiểm AI — phân loại điểm lệch |
| 30 | `doi_chieu.xuat_ket_qua@1` | ho_so_doi_chieu → truong | Cuối | Xuất kết quả JSON và PDF | Xuất kết quả — JSON và PDF |
| 31 | `doi_chieu.doc_docx@1` | tep → van_ban_tai_lieu | Đầu | Đọc bản Word | Đọc tệp Word |
| **Tra cứu** | | | | | |
| 32 | `tra_cuu.nhan_yeu_cau@1` | tep → ho_so_tra_cuu | Đầu | Nhận yêu cầu tra cứu | *giữ* |
| 33 | `tra_cuu.cat_doan@1` | ho_so_tra_cuu → ho_so_tra_cuu | Giữa | Cắt đoạn tài liệu | *giữ* |
| 34 | `tra_cuu.chuan_bi_ai@1` | ho_so_tra_cuu → yeu_cau_ai | Giữa | Chuẩn bị yêu cầu AI | Chuẩn bị AI — tra cứu |
| 35 | `tra_cuu.phan_loai_tai_lieu@1` | tra_loi_ai → ho_so_tra_cuu | Giữa | Hậu kiểm phân loại | Hậu kiểm AI — phân loại tài liệu |
| 36 | `tra_cuu.phan_tich_cau_hoi@1` | tra_loi_ai → ho_so_tra_cuu | Giữa | Hậu kiểm phân tích câu hỏi | Hậu kiểm AI — phân tích câu hỏi |
| 37 | `tra_cuu.xep_hang_lai@1` | tra_loi_ai → ho_so_tra_cuu | Giữa | Hậu kiểm xếp hạng lại | Hậu kiểm AI — xếp hạng lại |
| 38 | `tra_cuu.soan_tra_loi@1` | tra_loi_ai / ho_so_tra_cuu → ho_so_tra_cuu | Giữa | Soạn và kiểm câu trả lời | Hậu kiểm AI — soạn và kiểm câu trả lời |
| 39 | `tra_cuu.xuat_ket_qua@1` | ho_so_tra_cuu → truong | Cuối | Xuất kết quả tra cứu | Xuất kết quả — tra cứu |
| **Phân luồng** | | | | | |
| 40 | `audit.phan_luong@1` | tep → truong | Trọn | Phân luồng kiểm tra | Phân luồng nghiệp vụ (Excel/CSV) |
| 41 | `audit.chuan_bi_phan_loai@1` | tep → yeu_cau_ai | Đầu | Chuẩn bị phân loại bằng Local AI | Chuẩn bị AI — phân loại nghiệp vụ |
| 42 | `audit.phan_luong_sau_ai@1` | tra_loi_ai → truong | Cuối | Phân luồng sau Local AI | Hậu kiểm AI — phân luồng |
| 43 | `audit.phan_luong_hoa_don@1` | truong → truong | Cuối | Phân luồng hóa đơn từ XML/ZIP | Phân luồng hóa đơn (sau Đọc XML/ZIP) |
| 44 | `audit.ghi_ket_qua@1` | tep → truong | Trọn | Ghi kết quả kiểm | *giữ* |

**Các chỗ lệch mã (ghi nhận, chưa đổi):**
- **Lệch nhóm:** nhóm `ai`, `excel`, `trich`, `audit` khác tên engine. Riêng `audit` là tiếng Anh.
- **Lệch động từ:** ba mã sau là bước hậu kiểm (nhận `tra_loi_ai`) nhưng không có chữ `hau_kiem`:
  - `doi_chieu.phan_loai_diem_lech`;
  - `tra_cuu.phan_loai_tai_lieu`, `phan_tich_cau_hoi`, `xep_hang_lai`, `soan_tra_loi`;
  - `audit.phan_luong_sau_ai`.
- **Lệch cách viết:**
  - Mask dùng `chuan_bi_ai_cuc_bo`, các engine khác dùng `chuan_bi_ai`;
  - `excel.toan_ven` thiếu động từ (đúng chuẩn là `kiem_toan_ven`);
  - Trích xuất dùng `chuan_bi`/`hau_kiem` không có đối tượng.
- **Trùng chức năng:** `trich.doc_docx@1` và `doi_chieu.doc_docx@1` cùng `tep → van_ban_tai_lieu`. Lead chưa rà hai bản có khác nhau không.
- **Cũ:** `ai.hoi_tai_lieu@1`, `ai.hoi_theo_yeu_cau@1` giữ để Tra cứu, Đối chiếu dùng. Quy trình mới dùng `ai.hoi_theo_prompt@1`.

**Đề xuất của lead:** đổi tên hiển thị ngay. Mỗi engine tăng bản vá; không đổi xử lý, không hỏng quy trình. Codex làm 1 lát, sinh lại danh mục. Lệch mã chỉ sửa khi engine đó có lý do ra `@n` mới.

## 6. Còn lại

**Chờ Anh**

| # | Việc | Lựa chọn |
|---|---|---|
| A1 | Duyệt bộ tên chuẩn §4.3 và §5 | Duyệt cả bộ / duyệt có sửa / chưa đổi |
| A2 | Nhóm `audit` của Phân luồng | (a) **Giữ** `audit`, ghi vào bảng nhóm (lead đề xuất: không tốn công, không rủi ro). (b) Thêm `phan_luong.*@1` song song, giữ `audit.*` là cũ |
| A3 | Duyệt SDK 2.5.0 (bản nháp 20/11, thêm `quy_trinh.loi`) | `docs/goi-gui-engine/sdk-2.5.0/` |
| A4 | Chạy trên máy thật: `KIEM-TESSERACT.cmd`, `THU-LOCAL-AI-THAT.cmd`, `THU-ABBYY-THAT.cmd`, `KIEM-MAY-SACH.cmd`; xác nhận giấy phép FineReader | — |
| A5 | Câu nghiệp vụ còn mở: TC-Q06 (Tra cứu, tự xóa hay không); bộ đo 38 ca Tra cứu; 2 chỗ lệch nhỏ Phụ lục A Kiểm Excel (duyệt nếu muốn chặt hơn) | Xem `VIEC.md` từng engine |
| A6 | Cloud AI bản 2 (qua Mask) | Chưa mở lát |

*Ghi chú: một số dòng "Chờ Anh" trong `VIEC.md` của Hóa đơn, Đối chiếu, Tra cứu, Trích xuất có từ trước 15/11. Nhiều khả năng các quyết định ngày 15/11 đã thay chúng. Lead sẽ rà và đánh dấu lịch sử, không xóa.*

**Cần Core** (không sửa được từ phía engine)

| Mã | Việc | Ảnh hưởng |
|---|---|---|
| D | Nạp màn engine (`giao_dien_quan_tri`) | Màn trong `ui/` của 8 engine (trừ Hóa đơn) chưa hiện |
| D2 | Trình soạn Cài đặt bước do engine cấp (`giao_dien_tham_so`) | Trình soạn Cài đặt bước (Kiểm Excel, Phân luồng và các bước có tham số JSON) chưa hiện |
| E | Thao tác quản trị (`thao_tac_quan_tri`) | Nút kiểm kết nối Local AI, Hot Folder, Tesseract |
| F | Két bí mật theo tên (`app.bi_mat`), chỉ hiện 4 ký tự cuối | Khóa Cloud AI, khóa ABBYY |
| — | Cửa nạp cấu hình DEMO cho CLI chạy thử | Hỏi AI, Trích xuất, Tra cứu báo `CHUA_CAU_HINH` khi chạy thử |
| — | Xác nhận MIME với Core thật, không phân biệt hoa thường | Kiểm Excel, Trích xuất |
| — | Kho tài liệu | Tra cứu |
| — | `truong_ra` động theo tham số (C-TX-03) | Trích xuất |
| — | Lượt bền, quyền từng tệp con, OCR vùng | Đối chiếu, Mask |

SDK 2.5.0 nháp **chưa có** cửa D, D2, E, F. Cần đưa vào bản SDK kế tiếp.

**Tài liệu liên quan**
- `_chung/docs/DANH-MUC-ENGINE-CHO-MODULE.md`: danh mục tự sinh, chuỗi mẫu cho module.
- `_chung/docs/GIAO-CODEX-UI-CAU-HINH.md`: nguyên tắc màn cấu hình.
- `_chung/docs/LOAI-DU-LIEU-RIENG.md`: loại dữ liệu chung.
- `<engine>/docs/VIEC.md`: việc chi tiết từng engine.
