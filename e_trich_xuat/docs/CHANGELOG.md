# CHANGELOG tài liệu và công cụ kiểm

## 0.5.0 — 15/11/2026, TX-7; PR: chờ lead mở

- Chuyển SDK 2.2.0, khai schema cấu hình trong manifest; bỏ bảng cấu hình
  và các cổng tạm khỏi đường chạy, lưu nguyên bản ở `LUU-TRU/TX-7`.
- Đọc `viec.cau_hinh` đã kiểm/default. SDK chưa cấp phiên bản công khai
  trên việc: hồ sơ mới dùng phiên bản null + SHA-256 bản chụp; hậu kiểm
  kiểm băm, vẫn nhận hồ sơ cũ có phiên bản dương. Ghi C-TX-07.
- Không có bảng ngăn TX sau bỏ cấu hình; không cần SQL/migration/kiểm kê SQL.
- Giữ hành vi và các ca kiểm cũ, chuyển môi trường sang CoreGia 2.2.0;
  bỏ test so SHA mẫu ngăn, bỏ cổng DEMO thay thế. Ghim đủ phụ thuộc SDK.
- CLI chuẩn 4/5 ĐẠT, exit 1: C-TX-06 vẫn thiếu nạp tệp phụ cho DEMO hậu kiểm.
  C-TX-04 phần ngăn/cấu hình đã có; C-TX-05 hook lỗi, C-TX-08 nạp màn còn mở.
  **đã kiểm bằng Core giả (CoreGia)**, chưa đạt nghiệm thu TX-7.


## 15/11/2026 — TX-4b, PR: chờ lead mở

- E6 giữ so bytes bộ E1/tham số/văn bản; chấm giá trị từng mã sau hậu kiểm
  TX-3 bằng strip đầu/cuối và dẫn chứng đúng offset Unicode/nguyên văn.
  Câu hỏi/bảng/phản hồi thô chỉ tham khảo, không làm lại luồng nhiều lượt.
- Báo đủ bốn loại khớp/khác/cũ có-mới null/cũ null-mới có kèm lý do;
  đối chiếu cả hai bên với vàng độc lập, không đổi vàng để làm khớp.
- Bộ chuẩn có hai DOCX DEMO (thường/Track Changes), băng AI hai giao thức,
  snapshot hai module và bản vàng 37 mã tự soạn từ chính câu hợp đồng.
  Manifest SHA-256 giữ `chap_nhan_lead: "chờ lead"`; đo đạt vẫn exit 2.
- Công cụ soạn nguồn tái lập bytes, từ chối ghi đè nguồn khác nội dung;
  regression kiểm E6 không ghi lại fixture. Không thêm dependency.
- Phép đo thật: **74/74 mã khớp vàng, 74/74 dẫn chứng hợp lệ**, byte bắt
  buộc trùng trên 2/2 ca; **đã kiểm bằng Core giả (CoreGia)**.
  Pytest **412 passed, 0 skipped**; độc lập đạt; DEMO có ngăn **5/5 ĐẠT**.
  CLI SDK **2/3 ĐẠT, exit 1**, giữ C-TX-04; E6 **exit 2**, chờ lead.
- DOCX chưa được kiểm bố cục PNG: renderer thiếu `pdf2image`; đã kiểm
  ZIP/XML, styles và Accept All/toàn văn. Không thêm dependency/mạng.
- CHANGELOG này thay cho sửa CHANGELOG trong `goi/**` vì TX-4b chỉ được
  sửa tests/tham-chieu/e6/docs. Không đổi phiên bản gói hoặc đăng ký năng lực;
  không sửa Core/SDK/nguồn cũ, không commit/push. Linux/T3/N1/Core thật chưa kiểm.
