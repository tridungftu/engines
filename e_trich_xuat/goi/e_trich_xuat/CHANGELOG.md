# Thay đổi

## 0.2.0 — 15/11/2026, TX-1

- Tạo gói SDK 2.0 độc lập, chỉ công bố `trich.doc_docx@1` và hai DOCX DEMO.
- Chuyển lõi Accept All/Numbering sang bytes trong RAM; giữ thứ tự khối,
  ô rỗng/gộp, vị trí Unicode, băm gốc; không tạo trang/hộp giả.
- Chặn vượt giới hạn tệp/ZIP/XML/nội dung, lỗi tiếng Việt, hỗ trợ hủy.
- Cổng ngăn RAM tạm có lô nguyên tử/CAS/duy nhất/pháp nhân; cấu hình chỉ
  qua ngăn, seam giữ snapshot; chờ NGAN-0 và API SDK 2.1 thật.
- Màn cấu hình qua KttCore, khai SDK 2.1 riêng, kiểm bằng Node/KttCore giả.
- Phạm vi kiểm: **đã kiểm bằng Core giả (CoreGia)** trên Windows;
  chưa chạy Linux hoặc nối Core thật. Không AI/OCR thật, 0 Cloud.
