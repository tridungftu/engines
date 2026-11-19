# Kiểm và đọc Excel — EX-2

Khung SDK 2.2.0 cho `excel.toan_ven@1` và `excel.doc_bang@1`.
Kiểm đuôi, chữ ký, ZIP/XML, trần ô trước khi nạp workbook. `excel.toan_ven@1`
chạy K1–K6, tải JSON chi tiết qua Core; số trong JSON là chuỗi thập phân.
K7/K8 và báo cáo Excel chưa triển khai; kết quả ghi cảnh báo và để trống/null.
K6 liệt kê hằng số nhưng chưa phát cờ theo cây K7. `excel.doc_bang@1` đọc được
khuôn `xay_dung_klgt` (EX-4) và `tong_quat` (EX-5).

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

## Khuôn tổng quát (EX-5)

Chọn `khuon = tong_quat`, truyền `khuon_cot_json` phiên bản 1 theo phiếu §4.2.
Khuôn đóng: đúng ba khóa `phien_ban`, `cot`, `dong_dung`; mỗi cột đúng bốn khóa
`ma`, `tu_khoa`, `bat_buoc`, `kieu`. Mã cột duy nhất, chữ thường không dấu,
chữ đầu là a–z, sau đó chữ/số/gạch dưới, tối đa 64 ký tự. Có ít nhất một cột
bắt buộc. Trần 30 cột, tổng 200 từ khóa (gồm dòng dừng), 32 KiB UTF-8.
Sai cấu trúc, trùng khóa JSON hoặc vượt trần trả `THAM_SO_KHONG_HOP_LE`.

Từ khóa gọi trực tiếp `bo_nhom.khop_tu_khoa`: bỏ dấu/không phân biệt hoa thường,
chứa chuỗi; `=...` khớp nguyên từ/cụm từ; `#` khớp ít nhất một chữ số.
Ký tự regex khác hiểu nguyên văn. `dong_dung` xét ô có giá trị ngoài cùng bên trái
trong các cột đã nhận diện; có thể dùng `=tong cong` để tránh khớp một phần nhãn.

Dò tiêu đề bắt đầu trong 40 dòng đầu, ghép tối đa 4 tầng, trải nội dung ô gộp
chỉ trong vùng tiêu đề. Chọn bảng nhiều cột khớp nhất, rồi ít tầng nhất, rồi dòng
trên cùng; hòa giữa các sheet thì lấy sheet trước. Không lấy sheet ẩn. Từ khóa
khớp nhiều cột hoặc hai mã cùng trỏ một cột thì bỏ ứng viên đó; không thấy ứng viên
đủ cột bắt buộc trả `KHONG_TIM_THAY_BANG`. Cột tùy chọn không có trả null.

Tệp JSON giữ phần đầu như §5.2, `cot` ánh xạ mã → chữ cột. Mỗi phần tử `dong`
gồm `vi_tri`, `nhom`, `la_nhom`, `du_cot_bat_buoc`, `gia_tri` (mã cột → giá trị),
`canh_bao`. Dòng thiếu cột bắt buộc vẫn giữ để kiểm tra và có cảnh báo, không tính
vào `so_dong`; một ô chữ duy nhất thuộc cột văn bản khi thiếu cột bắt buộc được coi
là tiêu đề nhóm. Ô sai kiểu trả null và cảnh báo; dòng đủ giá trị nguồn ở các cột
bắt buộc vẫn tính vào `so_dong`. `tong_hop` rỗng, hai trường giá trị hợp đồng/đề nghị
luôn null vì chỉ áp dụng khuôn xây dựng.

Số dùng Decimal, JSON là chuỗi thập phân; số lưu dạng chữ có cảnh báo. Mã hàng
dạng chữ giữ số 0 đầu. Ngày Excel có định dạng ngày, chuỗi ISO hoặc dd/mm/yyyy
được xuất `YYYY-MM-DD`; không suy ngày từ số serial chưa có định dạng.
Tiền tệ lấy từ tham số hoặc đơn vị ghi rõ như EX-4; chưa rõ thì cờ bật, JSON giữ
số nguồn với `tien_te: null` theo §5.2. Không tự gán đơn vị.

Hai ví dụ trong `chay_thu_demo`: bảng giá thành tiêu đề gộp nhiều tầng, bảng báo giá
đổi vị trí cột và sheet. Nguồn sinh, khuôn và đáp án ngoài gói tại `tests/demo/`.
