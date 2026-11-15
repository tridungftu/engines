# Thay đổi

## 0.2.0 — 15/11/2026, TX-1

- Đã nối ngăn chung NGAN-0 (PR #34), giữ nguyên `ngan.py`/`cau_hinh.py`;
  hai test so SHA-256 chuẩn hóa CRLF→LF chạy bắt buộc, không skip.
- RAM nhận khai báo bảng từ `KHAI-SDK-2.1.json/ngan_du_lieu`; cấu hình dùng
  khóa `{}`, dict trực tiếp, giữ snapshot và phiên bản từ cùng một lần đọc.
  Đổi ngoại lệ ngăn/cấu hình chung thành `LoiNghiepVu`, giữ cờ thử lại.
- Test dùng `KetQuaLenh`/`TrangNgan`, phạm vi pháp nhân trong khóa/bộ lọc
  hoặc view; kiểm schema DOCX bằng jsonschema có sẵn của SDK, chỉ trong test.
- Tạo gói SDK 2.0 độc lập, chỉ công bố `trich.doc_docx@1` và hai DOCX DEMO.
- Chuyển lõi Accept All/Numbering sang bytes trong RAM; giữ thứ tự khối,
  ô rỗng/gộp, vị trí Unicode, băm gốc; không tạo trang/hộp giả.
- Chặn vượt giới hạn tệp/ZIP/XML/nội dung, lỗi tiếng Việt, hỗ trợ hủy.
- Cổng ngăn RAM tạm có lô nguyên tử/CAS/duy nhất/pháp nhân; cấu hình chỉ
  qua ngăn, seam giữ snapshot; còn chờ API SDK 2.1 thật.
- Màn cấu hình qua KttCore, khai SDK 2.1 riêng, kiểm bằng Node/KttCore giả.
- Phạm vi kiểm: **đã kiểm bằng Core giả (CoreGia)** trên Windows;
  chưa chạy Linux hoặc nối Core thật. Không AI/OCR thật, 0 Cloud.
