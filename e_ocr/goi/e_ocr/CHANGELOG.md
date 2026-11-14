# Thay đổi

## 1.0.1 — 14/11/2026 — OCR-1

- Chuyển bốn mô-đun lõi từ `ma-nguon/`, bỏ phụ thuộc Core/cổng OCR cũ;
  hai action đọc dùng chung lõi SDK 2.0.
- Đọc lớp chữ PDF kể cả chữ ẩn ABBYY, giữ dấu/tiền/ngày và tọa độ trang,
  dòng, từ; đọc bảng có đường kẻ, giữ ô trống/ô gộp. Không OCR lại ảnh nền.
- Hot Folder cục bộ: công bố tệp nguyên tử, chờ đúng mã tương quan, có
  thời hạn/hủy/dọn tạm; đã nhận chưa trả thì `ChuaRo`, không báo thành công.
- Tự đếm trang trước gửi, từ chối hơn 60 trang/tệp hỏng; trả băm đầu vào,
  nguồn đọc, phiên bản và cảnh báo; lỗi tiếng Việt không chứa đường dẫn.
- Thêm hai DEMO lớp chữ 3 trang vào phiếu để kiểm chung ngay trong OCR-1;
  test ABBYY giả chạy bằng luồng nền và PDF DEMO thuần Python.
- Ghim lại dependency đã có trong lock cũ; chưa làm lock wheel/máy sạch
  OCR-6. **Đã kiểm bằng Core giả (CoreGia)** trên Windows, chưa kiểm Linux,
  ABBYY/Core thật. Tesseract, Word, sổ hạn mức và lượt bền thuộc các lát sau.

## 1.0.0 — 14/11/2026 — OCR-0

- Tạo gói độc lập, phiếu 2.0 và ba hàm tạm trả `CHUA_LAM`.
- Thêm cấu hình JSON ngoài gói, schema cấu hình và kho JSON cho dữ liệu tạm.
- Kho ghi nguyên tử, khóa tệp thật trên Windows/Linux; kiểm cạnh tranh hai
  tiến trình bằng `spawn`.
- Chép schema `van_ban_tai_lieu` dùng chung, test so SHA-256; mẫu DEMO chỉ
  minh họa schema, chưa có DEMO xử lý OCR trong phiếu.
- Cổng đã kiểm bằng Core giả (CoreGia); chưa nối nguồn OCR hoặc Core thật.
