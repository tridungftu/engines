# Thay đổi

## 1.0.0 — 14/11/2026 — OCR-0

- Tạo gói độc lập, phiếu 2.0 và ba hàm tạm trả `CHUA_LAM`.
- Thêm cấu hình JSON ngoài gói, schema cấu hình và kho JSON cho dữ liệu tạm.
- Kho ghi nguyên tử, khóa tệp thật trên Windows/Linux; kiểm cạnh tranh hai
  tiến trình bằng `spawn`.
- Chép schema `van_ban_tai_lieu` dùng chung, test so SHA-256; mẫu DEMO chỉ
  minh họa schema, chưa có DEMO xử lý OCR trong phiếu.
- Cổng đã kiểm bằng Core giả (CoreGia); chưa nối nguồn OCR hoặc Core thật.
