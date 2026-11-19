# Kiểm và đọc Excel — EX-2

Khung SDK 2.2.0 cho `excel.toan_ven@1` và `excel.doc_bang@1`.
Kiểm đuôi, chữ ký, ZIP/XML, trần ô trước khi nạp workbook. `excel.toan_ven@1`
chạy K1–K7, tải JSON chi tiết qua Core; số trong JSON là chuỗi thập phân.
K7 dựng cây trước K6, phân nhóm bằng bộ module truyền. K8 và báo cáo Excel
thuộc EX-3; kết quả ghi cảnh báo. `excel.doc_bang@1` đã đọc khuôn KLGT ở EX-4.

Ô đích nhận `Sheet!A1` (có thể có dấu `$` và tên sheet đặt trong nháy đơn),
phải thuộc workbook và giới hạn Excel. Nếu trống, tìm theo `nhan_o_dich_json`:
danh sách từ khóa, 80 dòng đầu/12 cột đầu của sheet hiện, số đầu trong sáu ô
bên phải nhãn. Không tìm được hoặc cả hai trống: một mục Kiểm soát K7.

`bo_nhom_json`: tối đa 30 nhóm, 200 từ khóa, 32 KiB UTF-8; xét nhóm theo thứ tự.
Từ khóa chứa chuỗi, `=tu` khớp nguyên từ, `#` khớp một hoặc nhiều chữ số;
các ký tự regex được hiểu nguyên văn. Không bộ nhóm: lá Chưa phân nhóm,
`so_ngoai_nhom = null`. Bộ Review TTKL thuộc module, chỉ ở fixture ngoài gói.
Mã dùng chung cho EX-5: `bo_nhom.kiem_tu_khoa(tu)`,
`bo_nhom.khop_tu_khoa(tu, van_ban)`; tự bỏ dấu/viết thường/gộp khoảng trắng.

Không mạng ngoài Core, không CSDL, không ngăn/cấu hình, không lưu dữ liệu trên máy.
DEMO hoàn toàn giả: Công ty DEMO Ánh Dương. Script sinh ở `tests/demo/sinh_demo.py`
ngoài gói. Cài thư viện bằng `requirements.lock` với `--require-hashes --no-deps`;
SDK cài riêng từ wheel 2.2.0 trong repo. Bật `PYTHONDONTWRITEBYTECODE=1` khi kiểm.

Trần tạm: tệp 20 MiB; giải nén 128 MiB; 2.048 entry; 250.000 ô thực,
500.000 ô trong tổng hình chữ nhật các sheet; thời hạn Core 120 giây.
Số đo và giới hạn phép kiểm ghi trong `docs/VIEC.md` ngoài gói.
K7 giữ trần 14 tầng/12 mẫu mỗi dải của nguồn nhưng từ chối khi vượt,
không cắt ngầm; thêm trần 100.000 nút, 250.000 ô/dải, 500.000 lượt đọc ô.

SDK 2.2.0 kiểm MIME bằng chữ thường trong khi CoreGia trả MIME `.xlsm` có chữ
hoa. Cổng tạm chuẩn hóa MIME trước bộ kiểm, cho cả đầu vào gửi kèm và tải riêng;
không sửa phong bì gốc. Đợi Core/SDK sửa để bỏ lớp bọc này.

Đã kiểm bằng Core giả (CoreGia); chưa nối Core thật.
