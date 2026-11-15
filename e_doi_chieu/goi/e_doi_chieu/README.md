# Đối chiếu bản ký — khung DC-0 và contract DC-1

Chưa triển khai đọc Word hay nghiệp vụ đối chiếu; năng lực Word trả
`CHUA_LAM`. Bốn schema dữ liệu đã kèm gói theo quyết định 15/11/2026,
không có handler nhận cặp. Không có ví dụ chạy nghiệp vụ thành công.

SDK 2.0 dùng ngăn RAM, mất khi dừng; ngăn bền và màn quản trị chờ Core/SDK
2.1. Các màn trong bản khai là dự kiến, chưa có tệp UI. Cấu hình và dữ liệu
cần giữ chỉ qua Ngan; snapshot/ảnh do kho Core giữ, không lưu bền trên engine.

Đã kiểm bằng Core giả (CoreGia). Pytest 46 passed, 0 skipped; kiểm độc lập
mã 0. Lệnh `kho_tri_thuc_sdk.thu` trả mã 1 vì `chay_thu_demo=[]` (0 demo
nghiệp vụ); chưa đạt điều kiện kiểm chung. Khảo sát/đặc tả và Cần Core tại
`e_doi_chieu/docs/DC-1-KHAO-SAT.md`, `VIEC.md`; nguồn tại `NGUON.md`.
