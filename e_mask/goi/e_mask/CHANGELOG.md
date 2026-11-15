# Thay đổi

## 1.0.0 — 15/11/2026, MASK-3b → MASK-6

- Thay kho tệp trên đường chạy bằng cổng ngăn; RAM tạm khi chưa có SDK 2.1. CAS bảo vệ toàn bộ alias, hàng chờ, đếm gặp, tham chiếu và dấu lượt.
- Chốt bộ tiền tố MASKCT/MASKCN/MASKDC/MASKMST/MASKTK/MASKKHAC/MASKTAM; giữ mã Junsky hợp lệ, chặn mã trùng tiền tố.
- Thêm schema và handler che/mở văn bản, mở chuỗi trong dữ liệu/trích dẫn AI; trích dẫn đổi chữ phải kiểm lại.
- Chép bốn từ điển sạch của lead, kiểm SHA; không ghi tài liệu xuống đĩa.
- Thêm duyệt/từ chối, đóng/dọn, chuyển danh mục DEMO và màn quản trị qua KttCore.
- Giữ tín hiệu ChuaRo cả khi ghi dấu lỗi; giao lại không tăng đếm, không thay kết quả đã chốt.

Đã kiểm bằng Core giả (CoreGia). Còn chờ SDK/ngăn thật, nguồn danh tính tin cậy, mẫu NGAN-0 và tích hợp màn vào Core. CLI SDK chuẩn không tiêm nguồn quyền, hai ví dụ bị chặn. Chưa kiểm Core thật hoặc Cloud.
