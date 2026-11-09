# QUYẾT ĐỊNH CUỐI — Engine OCR (e_ocr) — chốt 06/11/2026 21:00

Căn cứ: PHIEU-ENGINE-e_ocr.md (docs\47-core\g3\), thảo luận với Anh ngày 06/11/2026.
Mọi ước giờ trong phiếu cũ hết hiệu lực; lead ước lại theo danh sách lát dưới đây, ghi rõ là ước tính.

## 1. Phạm vi đồng ý
- e_ocr là ENGINE RIÊNG; nghiệm thu hai tầng: máy test engine trước (phiếu này),
  nghiệm thu tổng thể sau (phiếu chung riêng).
- Tận dụng tối đa mã có sẵn, là phần mềm nội bộ của Anh, được chép vào gói để dùng nội bộ:
  - D:\GPT\OCR\abbyy-hotfolder: cầu nối ABBYY FineReader Hot Folder (nguồn ưu tiên).
  - D:\GPT\OCR\mask_ocr: CHỈ nhánh Tesseract (vie+eng), đọc PDF có chữ sẵn, DOCX,
    giữ bảng, xuất Word, hàng chờ/chống trùng (nguồn dự phòng).
- Năng lực v1: đọc văn bản (có vị trí trang, bản Word, giữ ô trống/ô gộp của bảng)
  + trích vùng `ocr.trich_vung@1` (cho Đối chiếu bản ký, TL 57).
- KHÔNG có trong v1: VietOCR, chế độ dual, màn duyệt điểm khác nhau,
  `ocr.trich_bang@1`, hóa đơn giấy, bảng kê.

## 2. Các lát
GIỮ (riêng OCR):
- 1 / G3-GOI-17: đưa mã abbyy-hotfolder + mask_ocr (Tesseract) vào gói; ghi giấy phép
  "phần mềm nội bộ, dùng nội bộ tập đoàn". KHÔNG chép in\, out\, jobs\, state\
  (có khóa API) của abbyy-hotfolder; không chép VietOCR, mô hình chỉ phục vụ VietOCR,
  review dual. Mã cũ không xóa.
- 2 / G3-GOI-18: nối đọc văn bản và bàn giao vào nguồn trong gói. Kiểm: T.
- 3 / G3-GOI-19: giữ ô trống, ô gộp, vị trí bảng trong kết quả Word. Kiểm: T.
- 6 / G3-GOI-20: ghim phiên bản thư viện + nguồn; hướng dẫn cài môi trường sạch;
  ghim theo khung SDK ĐÃ GỘP, không chờ SDK cuối. Kiểm: T.
- 9 / OCR-WIN-NT: thử ABBYY thật trên MÁY HIỆN TẠI (tạm), PDF DEMO. Kiểm: N + M.
THÊM:
- OCR-NOI: lớp chữ PDF ("text under image") của ABBYY → cấu trúc kết quả chung
  của mask_ocr; không OCR lại ảnh nền. Kiểm: T.
- OCR-CHON: ABBYY trước; tự chuyển mask_ocr khi (a) hết hạn mức 5.000 trang/30 ngày,
  (b) máy ABBYY tắt, (c) ABBYY lỗi/quá giờ. Kết quả ghi rõ nguồn đọc. Màn quản lý engine
  hiện hạn mức đã dùng/còn lại và trạng thái máy ABBYY. Kiểm: T + M.
- OCR-KETNOI: mở cầu nối ABBYY cho máy chủ Core gọi tới máy hiện tại, có khóa, chỉ cho
  địa chỉ máy chủ Core; log không lộ khóa/đường dẫn. Kiểm: N.
- OCR-VUNG: `ocr.trich_vung@1` (dùng lại crop_quad), trả chữ + cờ nghi ngờ. Kiểm: T.
- OCR-MAY: bộ DEMO giả + bài máy test engine độc lập (mục 5). Thay lát 11. Kiểm: T + M.
BỎ khỏi phiếu OCR:
- Lát 11 (thử qua CRM): thay bằng OCR-MAY.
- VietOCR / dual / màn duyệt điểm khác nhau.
CHUYỂN sang phiếu nghiệm thu tổng thể (làm sau, không chặn OCR xong):
- Lát 4 (kênh AI), 5 (SDK cuối), 7 (rào chắn nạp gói thật), 8 (5 gói độc lập),
  10 (phát hiện → đăng ký gói), 12 (tài liệu nghiệm thu cuối),
  bài test 60 phút qua CRM của phiếu cũ.
ĐỂ SAU (function bổ sung, sau khi xong engine):
- `ocr.trich_bang@1`; OCR hóa đơn giấy; OCR bảng kê; chuyển ABBYY lên máy chủ
  (khi đó chạy lại ca 2, 5, 8 của bài test mục 5).

## 3. Thứ tự ưu tiên
1. Lát 1 → 2 → 3 (nền gói).
2. Song song sau lát 1: OCR-NOI, OCR-KETNOI, OCR-VUNG.
3. OCR-CHON (sau OCR-NOI).
4. Lát 6 (ghim).
5. Lát 9 (ABBYY thật, cần Anh cho phép mở kết nối tạm trên máy này).
6. OCR-MAY: chạy bài test cuối; ngày nào cũng chạy và trước khi báo xong.
Số lát giao song song: lead quyết khi bắt đầu triển khai. Không đứng chờ Anh duyệt.

## 4. Các câu đã chốt
- OCR là engine riêng; máy test trước, nghiệm thu tổng thể sau.
- Tận dụng tối đa mask_ocr; giấy phép nội bộ đã rõ (lát 17–20 mở chặn).
- Ưu tiên ABBYY; hết hạn mức HOẶC máy ABBYY tắt/lỗi → tự chuyển mask_ocr.
- ABBYY cài ở máy chủ; tạm thời dùng máy hiện tại.
- Bỏ VietOCR (không hiệu quả); mask_ocr chỉ chạy Tesseract.
- Thêm trích vùng vào v1.
- Trích bảng, hóa đơn giấy, bảng kê: làm sau; xong engine trước.
Việc chờ Anh (không chặn code):
- Xác nhận giấy phép FineReader Corporate cho dùng tự động phục vụ nhiều người
  qua máy chủ (trước khi chuyển ABBYY lên máy chủ).
- Cho phép mở kết nối tạm có khóa trên máy hiện tại (trước lát 9).
- Chuyển hợp đồng PDF ở abbyy-hotfolder\in\ và DOCX ở out\ vào thư mục lưu trữ.

## 5. Bài test tổng thể cuối của engine (OCR-MAY)
Bộ DEMO hoàn toàn giả, có nhãn DEMO: PDF quét 3 trang có bảng (ô trống, ô gộp),
2 ảnh PNG/JPEG 1 trang, Word đáp án cùng bộ, "Công ty DEMO Ánh Dương",
1.000.000 VND, ngày 30/10/2026; 1 ảnh vùng cắt cho trích vùng;
PDF 61 trang, tệp > 20 MiB, tệp hỏng. Không dùng hồ sơ thật.
Admin DEMO thao tác qua màn Chạy thử DEMO / Quản lý engine (chỉ Admin).

| Ca | Thao tác | Phải thấy để đạt |
|---|---|---|
| 1 | Mở Quản lý engine → OCR | Đúng phiên bản; ABBYY sẵn sàng; hạn mức đã dùng/còn lại |
| 2 | Gửi PDF DEMO (ABBYY bật) | Nguồn = ABBYY; chữ có vị trí trang; Word tải được; tiền/ngày khớp đáp án; bảng còn đủ ô trống/ô gộp |
| 3 | Gửi 2 ảnh liên tiếp + gửi trùng 1 tệp | Báo số việc đang chờ; không xử lý trùng; thứ tự rõ ràng |
| 4 | Giả lập hết hạn mức, gửi lại PDF DEMO | Tự chuyển mask_ocr; nguồn = mask_ocr; ghi số đo đúng/sai so đáp án (ngưỡng đạt Anh chốt sau lần đo đầu) |
| 5 | Tắt cầu nối ABBYY, gửi ảnh DEMO | Tự chuyển mask_ocr, không treo; ghi lý do chuyển |
| 6 | Gửi vùng cắt | Trích vùng trả chữ + cờ nghi ngờ |
| 7 | Gửi tệp quá cỡ, quá trang, hỏng; hủy 1 việc đang chờ | Lỗi dễ hiểu; không báo thành công giả; không trừ hạn mức sai |
| 8 | Gọi cầu nối từ máy khác không khóa / từ máy chủ Core có khóa | Không khóa → bị chặn; có khóa → được; log không lộ khóa/đường dẫn |
| 9 | Xem nhật ký | Thời gian chờ/chạy từng ca; nguồn đọc từng ca |

Đạt = mọi ca có bằng chứng (ảnh màn, log); không thêm mã lỗi so NEN-TEST.md;
phần chưa kiểm ghi rõ, không báo đạt thay. Lead ghi phút thực tế mỗi lần chạy.