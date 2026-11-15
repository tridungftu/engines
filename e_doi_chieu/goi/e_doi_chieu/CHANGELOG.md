# Thay đổi

## DC-3 — 15/11/2026 · 0.3.0 chưa phát hành

Sửa theo kiểm độc lập lead, cùng phạm vi DC-3:

- Thêm hạn chiếm lượt trong ngăn, cấu hình thời hạn riêng hoặc mặc định
  thời hạn bước + 60 giây; CAS chiếm lại lượt quá hạn, mã chủ riêng ngăn
  worker cũ chốt/cleanup đè chủ mới. Chưa quá hạn trả `DC_DANG_XU_LY`.
- Hồ sơ Core cũ không đọc được chuyển `can_thu_lai` bằng CAS rồi dựng lại
  từ nguồn hiện tại đã kiểm quyền/băm/trần; sai băm vẫn từ chối.
- Khóa chống trùng ghim mã cặp, cảnh báo và băm cấu hình (gồm trần).
- Dựng chỉ mục văn bản → tập trang một lần, kiểm hủy trong vòng dài;
  12.000 nút OCR lề lặp đo riêng **0,1190 giây**, test `< 2 giây` đạt.
- Soft hyphen chỉ gom khoảng trắng liền kề, map không qua vùng đã bỏ.
  Bảng test 14 cặp vẫn phân biệt, 7 cặp bằng nhau theo bộ ghim và kiểm
  tắt từng quy tắc; thêm ca phục hồi, tranh lượt, chủ cũ quay lại và hủy.
- Đã kiểm bằng Core giả (CoreGia): pytest **297 passed, 0 skipped**
  (144 ca DC-3); DEMO Word **1/1 ĐẠT**; kiểm độc lập mã 0. Chưa kiểm
  Core thật/Linux; ngăn RAM/quyền tệp/đồng hồ/lease thật còn theo VIEC.
  SHA-256 LF hiện hành tại NGUON; PR: **chờ lead mở**, không commit/push.

Bản bàn giao trước kiểm độc lập:

- Thêm `doi_chieu.nhan_cap@1`: băm bytes yêu cầu trước parse JSON nghiêm,
  kiểm nguồn/tham chiếu/phiên bản/quyền qua SDK, đọc lại Word bằng DC-2,
  từ chối OCR rỗng/lỗi, thiếu tệp/quyền, sai băm và vượt trần.
- Snapshot đầy đủ tải Core, phong bì schema chỉ tham chiếu/băm/trạng thái;
  mới `da_nhan`, các số chưa đo null, không kết luận Khớp. Cấu hình/bộ đã
  ghim qua ngăn, thiếu cấu hình trả `CHUA_CAU_HINH`.
- NFC/khoảng trắng/nháy/gạch/ngắt dòng có map Unicode về nguyên văn/cấu
  trúc, giữ dấu/ô rỗng/gộp, không bịa trang Word; đầu/chân/số trang chỉ bỏ
  có căn cứ/whitelist, tiền/mã và nội dung thân giống header vẫn giữ.
- Ngăn chống trùng `lay_hoac_tao`, CAS chốt/nhường thử lại không đè chủ
  khác; cùng bytes với ID mới vẫn một lượt nhưng tái dùng phải có quyền
  tới snapshot và mọi tham chiếu cũ. Không lưu sổ đĩa/Cloud/engine khác.
- PNG kiểm CRC/DEFLATE/dòng/pixel; JPEG kiểm khung/kích thước, chưa giải mã
  DCT/quét. Giới hạn, nguồn gốc tệp và phục hồi chủ lượt theo lease còn
  cần Core/DC-8; chi tiết README/VIEC, không sửa API/SDK/schema chung.
- Khép test nợ DC-2: handler ném lỗi lạ chứa bí mật DEMO không lộ stderr
  khi chạy end-to-end CoreGia; ghi nợ field/AlternateContent từ chối toàn
  tài liệu, không nới trong lát này.
- Đã kiểm bằng Core giả (CoreGia): SDK DEMO Word 1/1 ĐẠT; pytest
  **237 passed, 0 skipped** (84 ca DC-3); kiểm độc lập mã 0. Chưa kiểm
  Core thật/Linux; PR: **chờ lead mở**; không commit/push.

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
