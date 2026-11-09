# e_doi_chieu — Đối chiếu bản ký: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- Đặc tả `DAC-TA-e_doi_chieu.md`, là bản chép TL 57 (31/10/2026); Anh đã chốt 5 câu.
- TL 41 (CRM-G5).
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

## 0. Kết luận
- **Engine mới chưa có mã.** Hiện chỉ có đặc tả đã chốt hướng. Thế hệ cũ K2 có bản G5-B thủ công: `crm_doi_chieu.py` ở `D:\Claude\CRM\tu-core-cu\`.
- Engine so **bản Word chuẩn** (bản gửi ký) với **bản đã ký** (PDF scan qua OCR) và báo **mọi** điểm khác nhau.
- **So theo 2 lớp:**
  - Lớp 1: Python so từng chữ, áp quy tắc cứng; không bỏ sót điểm nào.
  - Lớp 2: Local AI lọc phần còn lại; **chỉ được nâng mức, không được hạ**.
- **Khi có lệch Nghiêm trọng hoặc vùng sửa tay:** gửi báo cáo cho người dùng và **chặn hiệu lực hợp đồng** tới khi người dùng xác nhận từng điểm. **Chỉ dùng Local AI.**

## 1. Yêu cầu

### 1.1 Anh đã chốt (31/10)
| # | Quyết định |
|---|---|
| 1 | Engine trong Core kèm icon "Đối chiếu bản ký". CRM-G5, M2, M4, M9 cùng gọi |
| 2 | Python so chữ + Local AI lọc; **xử lý OCR thiếu dấu hoặc sai dấu** |
| 3 | Sửa tay, gạch xóa, ký nháy: **đánh dấu vùng, cắt ảnh để người xem**; máy không tự đọc chữ tay |
| 4 | Lệch Nghiêm trọng → báo cáo, gửi người dùng; **chặn hiệu lực** tới khi xác nhận |
| 5 | Chỉ Local AI |

### 1.2 Yêu cầu chi tiết
| Mã | Yêu cầu |
|---|---|
| DC-a | Kiểm bản Word: còn track changes hoặc comment thì dừng và hỏi người dùng. Có nhiều bản thì mặc định lấy bản "chờ ký" mới nhất |
| DC-b | Lấy chữ bản ký: PDF có lớp chữ thì lấy thẳng; PDF scan thì gọi `e_ocr`, giữ tọa độ từ và cờ nghi ngờ. **OCR lỗi → "Chưa đối chiếu được", không bao giờ coi là khớp** |
| DC-c | Kiểm trang: thiếu, thừa, đảo trang; thứ tự Điều và Khoản |
| DC-d | Chuẩn hóa: NFC, khoảng trắng, ngắt dòng, dấu nháy, gạch nối; bỏ đầu trang, chân trang, số trang; chuẩn kiểu đánh số |
| DC-e | Căn đoạn theo cấu trúc (Điều → Khoản → câu; bảng → dòng → ô); so hai lượt, **có dấu** và **bỏ dấu** |
| DC-f | **Lệch dấu, 5 bước** (§4 đặc tả): (1) tách nhóm chỉ lệch dấu; (2) tra từ điển: từ OCR vô nghĩa thì là Nhiễu OCR; (3) **cặp đổi nghĩa** (thuê/thuế, lãi/lại, phạt/phát, bán/bàn, không/khống, hạn/hàn) xét ngữ cảnh bằng Local AI + cờ ABBYY + **OCR lại vùng** (`ocr.trich_vung@1`); chỉ xếp Nhiễu khi **cả AI và lần OCR lại** cùng kết luận lỗi OCR; (4) không áp dụng cho vùng quy tắc cứng; (5) trang có quá nhiều lệch dấu → đánh dấu cả trang "OCR kém" |
| DC-g | **Quy tắc cứng → Nghiêm trọng:** mọi chữ số khác nhau; ngày tháng, thời hạn; số tiền (bằng số và bằng chữ), đơn vị tiền tệ, tỷ lệ %; **số tiền bằng số không khớp bằng chữ** ngay trong bản ký; tên bên ký, người đại diện, chức vụ, MST, STK, địa chỉ, số hợp đồng; thiếu/thừa/đảo trang hoặc Điều/Khoản; thêm hoặc bớt từ phủ định (không, chưa, chỉ, trừ…) và từ bắt buộc (phải, được, có thể); vùng sửa tay |
| DC-h | Local AI xếp phần còn lại: Cần xem / Thay đổi hình thức / Nhiễu OCR. Mọi kết luận có lý do và câu nguyên văn của hai bản; Python kiểm câu trích |
| DC-i | **Kết luận một lượt:** Khớp / Khớp – có thay đổi hình thức / Cần xem / Lệch nghiêm trọng / Chưa đối chiếu được |
| DC-j | **Phát hiện vùng sửa tay**: loại trừ khối chữ ký và con dấu; trả trang, tọa độ, ảnh cắt. Cách làm chọn sau khi đo ở DC-0 |
| DC-k | **Màn kết quả** hai cột: Word bên trái, ảnh cắt bản scan bên phải. Người dùng xác nhận từng điểm bằng 1 trong 4 lựa chọn: Lỗi OCR / Thay đổi đã thống nhất / Bản ký sai / Không ảnh hưởng (bắt buộc ghi lý do). Nhật ký chỉ ghi thêm, có `row_version`. Xuất báo cáo PDF |
| DC-l | **Chặn hiệu lực:** Core phát `doi_chieu.co_lech_nghiem_trong`; module đặt trạng thái "Chờ xác nhận đối chiếu" (khóa nút Hiệu lực ở CRM-G6; tham số trích từ bản ký không lên tầng 1). Mở chặn khi mọi điểm đã xác nhận và không còn "Bản ký sai" |
| DC-m | Học dần có duyệt: danh mục `loi_ocr_thuong_gap` chỉ chứa cặp **không đổi nghĩa**; Admin duyệt |
| DC-n | **Đo trước khi bật:** bắt đủ **100%** điểm Nghiêm trọng đã cài; tỷ lệ Nhiễu OCR xếp sai (sửa thật mà bị ẩn) **bằng 0** |

### 1.3 Năng lực của engine (đặc tả §9)
- `doi_chieu.doc_docx@1`
- `doi_chieu.so_van_ban@1`
- `doi_chieu.phan_loai_diem_lech@1` (qua `e_hoi_ai`, chỉ Local; Core điều phối, engine không gọi thẳng)
- `doi_chieu.phat_hien_sua_tay@1`
- Năng lực bổ sung cho `e_ocr`: `ocr.trich_vung@1` (✅ đã có mock)
- Contract mới: `diem_lech.v1`, `ket_qua_doi_chieu.v1`

### 1.4 Phần thuộc Core / module
- **Core:** schema `loi_doi_chieu` (6 bảng), quy trình `doi_chieu_ban_ky`, các route `/api/v1/doi-chieu/*`, sự kiện, màn `ManDoiChieu` và `NutDoiChieu` (SDK JS).
- **Lưu ý G14:** những phần này phải là cửa chung hoặc giao diện của engine. Chặn hiệu lực là việc của **module**, kích hoạt bằng sự kiện.

## 2. Hiện trạng
| Phần | Trạng thái |
|---|---|
| Engine `e_doi_chieu` | ❌ chưa có mã |
| `ocr.trich_vung@1` | ✅ mock (ở `e_ocr`) |
| Bản K2 G5-B thủ công | 🔁 `D:\Claude\CRM\tu-core-cu\...\k2\crm_doi_chieu.py`, `sql_crm_doi_chieu.py` |
| Khảo sát DC-0 (ABBYY có xuất tọa độ và cờ nghi ngờ không; từ điển tiếng Việt; cách phát hiện sửa tay; bộ mẫu) | ❌ |

## 3. Lát (đặc tả §12; chưa có giờ vì chưa đo)
- Thứ tự: DC-0 khảo sát → DC-1 đọc DOCX + so chữ + quy tắc cứng → DC-2 lệch dấu + phân loại Local → DC-3 sửa tay → DC-4 (Core) schema, quy trình, API, sự kiện → DC-5 màn kết quả, nhúng CRM-G4/G5, đo chất lượng → DC-6 danh mục lỗi OCR.
- **Project engine làm:** DC-1, DC-2, DC-3 và bộ đo.

## 4. Chờ Anh (trả lời sau, đặc tả §13)
1. Người xác nhận là ai? Có cần người thứ hai duyệt khi chọn "Thay đổi đã thống nhất" cho điểm Nghiêm trọng không?
2. Vùng sửa tay có chặn hiệu lực không? Đề xuất: có.
3. Nhóm hợp đồng nào bắt buộc đối chiếu 100%?
4. Có kiểm ký nháy và dấu giáp lai từng trang không?
5. Có tự gợi ý đối chiếu khi bản ký vào kho không?
6. Có hợp đồng song ngữ không?
7. Vị trí thư mục `ocr-dual-release`.
8. Máy Local AI có model thị giác không.
