# Thay đổi

## DC-2 — 15/11/2026 · 0.2.0 chưa phát hành

- Triển khai đọc DOCX trong RAM qua SDK, SHA-256 bytes thật, giữ nguyên văn,
  bảng lồng/ô trống/gộp ngang dọc và offset Unicode. Đọc cả thân, đầu/chân
  trang và chú thích; `so_trang=0`, `trang=[]`, không render/trang/hộp giả.
- Chặn sửa đổi/comment ở mọi phần XML Word bằng `DC_WORD_CHUA_CHOT`;
  không Accept All. Vùng chưa hỗ trợ/hỏng trả `DC_WORD_KHONG_DOC_DUOC`.
- Bảo vệ ZIP/XML/quan hệ ngoài, trần trước giải nén và bytes/EOF/CRC thật;
  không tin kích thước tự khai để bỏ đuôi. Không OCR/AI/Cloud/nhúng/mạng.
- Thêm DEMO DOCX sạch thực vào manifest; đúng ba tệp runtime của lát.
  Nguồn/băm TX-1 tại NGUON.md; phạm vi và quy ước nguyên văn tại README.
- Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest 153 passed,
  0 skipped; kiểm độc lập mã 0. Khép nợ DEMO rỗng của DC-0/DC-1.
  Chưa kiểm Core thật/Linux; không commit/push.

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
