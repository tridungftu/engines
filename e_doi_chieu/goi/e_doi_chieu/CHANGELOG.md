# Thay đổi

## DC-1 — 15/11/2026 · 0.1.0 chưa phát hành

- Thêm schema `ho_so_doi_chieu` theo DC-Q17 đã duyệt; chép nguyên ba schema
  chung `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, test so băm LF với
  `_chung/contract/`. Không sửa schema cấu hình DC-0 hoặc mẫu NGAN-0.
- Khai đúng tên bốn loại đã duyệt trong manifest; sửa nhãn tiếng Việt.
  Chỉ giữ khung Word `CHUA_LAM`, chưa thêm handler nhận cặp/đối chiếu.
- Đặc tả JSON cặp, snapshot/băm/giai đoạn và khảo sát nguồn tại
  `e_doi_chieu/docs/DC-1-KHAO-SAT.md`. Quyền tệp con/OCR vùng/ngưỡng detector
  vẫn cần Core/đo thật; không dùng đường máy để bù nguồn thiếu.
- Đã kiểm bằng Core giả (CoreGia): pytest 46 passed, 0 skipped; kiểm độc lập
  mã 0. `thu` giữ 0 demo nghiệp vụ, SDK 2.0 trả mã 1 do danh sách rỗng;
  chưa đạt điều kiện kiểm chung. Không mạng/Cloud hoặc lưu dữ liệu bền.

## 0.1.0 ? 15/11/2026

- DC-0: khung SDK 2.0, khai b?o d? ki?n SDK 2.1, ng?n RAM v? c?u h?nh; ??c Word tr? CHUA_LAM. ?? ki?m b?ng Core gi? (CoreGia); ch?a ki?m nghi?p v?.
