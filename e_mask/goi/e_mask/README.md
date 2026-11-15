# e_mask — DEMO

MASK-0 có khung SDK; MASK-1 thêm matcher; MASK-2 thêm detector và hậu kiểm lõi văn bản. Hai năng lực cổng vẫn trả `CHUA_LAM`, chưa kích hoạt vận hành. Đã kiểm bằng Core giả (CoreGia).

Lõi nhận văn bản/danh sách định danh đã biết và kho do bên tin cậy tiêm; kết quả nội bộ che/mở kèm kiểm không phải phong bì phát hành. Kho DEMO và từ vựng mock chỉ nằm ngoài gói trong tests. Không tự cấp quyền, nối kho vận hành, OCR hoặc Cloud.

Bốn tài nguyên chưa được lead cấp sạch. `tai_nguyen.nap_cau_hinh` chỉ nhận whitelist nội bộ tin cậy gồm đường tuyệt đối ngoài gói và SHA-256 của đúng bốn tệp. Chưa cấu hình đủ → `MASK_THIEU_TAI_NGUYEN`, không có fallback. Kênh cấu hình máy/schema MASK-0 vẫn giữ nguyên tới lát nối adapter và khi có whitelist được duyệt; nội dung công việc không được cấp cấu hình này.

Trần giữ nguyên 500.000/500/300/20; detector không bị cắt ở 500 cụm. Còn sót, lỗi detector, chuỗi chưa quét hết hoặc sai tiền/ngày đều chặn văn bản. Adapter sau phải đổi thành `LoiNghiepVu` với mã/câu cố định, không dùng ngoại lệ gốc. Không có mã hóa bảng hoặc xuất Word mới trong lõi.

Heuristic còn bỏ lọt tên người viết thường không nhãn. Test DEMO đạt chưa chứng minh đủ điều kiện Cloud. Xem `NGUON.md` về đường nguồn, SHA, cấu hình whitelist và giới hạn. Chỉ dùng thư viện chuẩn và SDK 2.0.0.
