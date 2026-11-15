# Thay đổi

## 0.3.0 — 15/11/2026, TX-2

- Thêm `trich.chuan_bi@1`: nhận snapshot theo việc, SHA-256 đúng bytes UTF-8
  trước parse; JSON nghiêm, kiểm đủ 10 cột/quy tắc qua E1 SDK, giữ dòng ngừng
  dùng/thứ tự; không tra bộ hoặc mặc định XD.
- Danh sách con giữ thứ tự, rỗng lấy mọi mã đang dùng; chỉ nhận hỏi thêm `[]`.
  Prompt bắt buộc của module; một request v1 đủ mã, khuôn 2020-12 `$defs`,
  nguyên văn và offset Unicode, không đổi loại chung thành batch.
- Chặn snapshot 64 KiB/200 dòng đang dùng, prompt 20.000 ký tự, toàn văn
  500.000 ký tự, khuôn 32 KiB; ngân sách mặc định 16.000 không vượt trần
  cấu hình ngăn, giữ phiên bản. Không cắt ngầm; token vẫn chỉ là ước lượng.
- Hồ sơ JSON trong RAM tải lên Core, gồm snapshot/vị trí/yêu cầu/cấu hình
  đã ghim; chuyển tiếp gọn chỉ metadata/tham chiếu/băm, trần 64 KiB.
- Sửa lọc log TX-1: chỉ che nội dung lỗi việc/traceback, giữ mã lỗi SDK;
  chặn khởi động khi SDK khác 2.0.0 hoặc chữ ký hai hook thay đổi.
- Thêm schema chung nguyên byte, DEMO TX-2, cổng DEMO có NganBoNho;
  **đã kiểm bằng Core giả (CoreGia)**: pytest **164 passed, 0 skipped**,
  độc lập **exit 0**, DEMO có ngăn **3/3 ĐẠT**. CLI SDK chuẩn **2/3 ĐẠT,
  exit 1**, TX-2 `CHUA_CAU_HINH`; ghi C-TX-04, không tự tạo cấu hình.
- Đóng nợ mô tả DOCX từ chối cả tài liệu với vMerge continue có chữ,
  dòng không ô hoặc lệch gridSpan; trần tỷ lệ giải nén **200:1**.
- Chưa kiểm Linux/Core thật, ACL/vòng đời tệp hoặc context model thật;
  giữ C-TX-01/02/04 và A-TX-01. Không sửa Core/SDK/nguồn cũ; **0 Cloud**.

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
