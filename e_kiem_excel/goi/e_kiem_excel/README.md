# Kiểm và đọc Excel — EX-0

Khung SDK 2.2.0 cho `excel.toan_ven@1` và `excel.doc_bang@1`.
Kiểm đuôi, chữ ký, ZIP/XML, trần ô trước khi nạp workbook. Hai năng lực hiện
trả lỗi `CHUA_LAM`; chưa thực hiện kiểm K1–K8 hoặc đọc bảng nghiệp vụ.

Không mạng ngoài Core, không CSDL, không ngăn/cấu hình, không lưu dữ liệu trên máy.
DEMO hoàn toàn giả: Công ty DEMO Ánh Dương. Script sinh ở `tests/demo/sinh_demo.py`
ngoài gói. Cài thư viện bằng `requirements.lock` với `--require-hashes --no-deps`;
SDK cài riêng từ wheel 2.2.0 trong repo. Bật `PYTHONDONTWRITEBYTECODE=1` khi kiểm.

Trần tạm: tệp 20 MiB; giải nén 128 MiB; 2.048 entry; 250.000 ô thực,
500.000 ô trong tổng hình chữ nhật các sheet; thời hạn Core 120 giây.
Số đo và giới hạn phép kiểm ghi trong `docs/VIEC.md` ngoài gói.

SDK 2.2.0 kiểm MIME bằng chữ thường trong khi CoreGia trả MIME `.xlsm` có chữ
hoa. Cổng tạm chuẩn hóa MIME trước bộ kiểm, cho cả đầu vào gửi kèm và tải riêng;
không sửa phong bì gốc. Đợi Core/SDK sửa để bỏ lớp bọc này.

Đã kiểm bằng Core giả (CoreGia); chưa nối Core thật.
