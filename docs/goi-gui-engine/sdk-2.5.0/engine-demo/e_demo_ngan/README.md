# Đếm lượt gọi theo ngày (DEMO)

Gói nghiệm thu lô 2, CĐ-35; đối chiếu G3/G5/G14, E1/E5/E9 và L2.1/L7.1.
Cần Core có ngăn engine (migration 191–192 và API lô 2), SDK **2.2.0**.
Không có thông tin đăng nhập PostgreSQL trong engine. Cài và thử theo
[HUONG-DAN-THU.md](HUONG-DAN-THU.md).

- `dem.goi@1` nhận văn bản, trả `{"loai":"truong","truong":{"so_lan":1}}`.
- `dem_goi` đếm riêng từng pháp nhân, từng ngày theo giờ Việt Nam (`+07:00`).
  Core điền pháp nhân từ việc, bộ đếm được tạo bằng `lay_hoac_tao`, tăng bằng
  `sua` kèm `row_version`. Một lượt đầu và tối đa **5 lượt thử lại** khi
  `NganXungDot`; hết lượt thì trả lỗi qua SDK. Đây là thử lại CAS trong một việc,
  không phải bảo đảm đếm một lần khi người dùng chủ động chạy lại cả việc.
- Văn bản bắt đầu bằng `DD:` ghi một dòng `dinh_danh` cùng lô CAS tăng đếm.
  Phần sau `DD:` là dữ liệu DEMO được Core mã hóa; bí danh dùng cấu hình
  `tien_to` (mặc định `DEMO`) và mã việc. Engine không ghi nhật ký bản rõ.
- Ngăn `dem_goi` giữ tối đa 90 ngày: hết hạn thì ẩn khi đọc mặc định,
  dữ liệu vẫn được giữ trong PostgreSQL; ngăn `dinh_danh` không khai hạn giữ.
- SQL 001 tạo hai bảng thường trong `eng_e_demo_ngan`; SQL 002 thêm
  `ghi_chu text` cho phép bỏ trống để thử đường nâng gói. Cột này chưa được
  năng lực sử dụng. Kiểm kê `sql/kiem_ke.json` chứa bytes và SHA256 của mọi tệp
  trong gói, trừ chính kiểm kê; phải tính lại sau mọi thay đổi.

Thử thuần khi đã có SDK 2.2.0: `python -m kho_tri_thuc_sdk.thu <thư-mục-gói>`.
`demo/mau.txt` chỉ chứa định danh giả; không đưa dữ liệu thật vào gói.
