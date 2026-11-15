# Mẫu biên bản TX-6 — phân biệt đo thật và chưa đo

Ngày/giờ, người chạy, người review: **chưa ghi**. Phạm vi: **DEMO**.
Chế độ: **chạy khô / máy thật** (chọn rõ). Băm artifact công cụ: **chưa có**.
CoreGia chỉ là mô phỏng; chưa chứng nhận quyền/lưu giữ/ACK Core thật.

| Bằng chứng | Băm / số đo | Trạng thái |
|---|---|---|
| Wheel SDK, schema, ngăn/cấu hình chung | Điền SHA-256, quy ước văn bản CRLF→LF; wheel bytes | Chưa kiểm |
| Bộ DEMO/đáp án, E6 và biên bản lead | Điền băm bytes artifact, không nội dung hồ sơ | Chưa kiểm |
| Nền N1 được lead chấp nhận | Băm nền/biên bản; model và băm cấu hình | Chưa kiểm |
| Venv mới Windows / Linux / CI | Ghi từng môi trường và exit thực; không gộp | Chưa kiểm |
| CLI SDK chuẩn | Số DEMO đạt/tổng, exit và lỗi thật | Chưa kiểm |
| DEMO CoreGia có ngăn/hồ sơ, UI, stdin/HTTP giả | Số ca/exit thực | Chưa kiểm |

Mỗi dòng T3 phải có băm bộ/prompt/tài liệu/khuôn/body thực; giữ riêng băm
Phụ lục A, không lấy token ký tự/4 làm số thực. Một dòng cho mỗi ID model ×
DEMO-1/20/60; Gemma ghi ID phát hiện nguyên vẹn, không đoán biến thể.

| ID / tải / băm cấu hình | Runtime / quantization / context hiệu dụng | Token vào sau bọc / ra / reasoning | Giây | Ô trả / 37 | Căn cứ hợp lệ / 37 | Cần soát | Từ chối / tràn / cắt | Kết luận |
|---|---|---|---|---|---|---|---|---|
| Chưa đo | Chưa đo / chưa đo / `null` | `null` / `null` / `null` | `null` | `null` / 37 | `null` / 37 | `null` | `null` / `null` / `null` | T3 chưa đo |

N1 chỉ ghi **một lần**: băm dữ liệu/đáp án/prompt/khuôn/bộ/model/cấu hình
phải khớp nền. `da_do`, `dat`, `ty_le`: **null/chưa đo** tới khi có số thật.
Ghi tập mã/mẫu số nền và mới, không chỉ tỷ lệ. Không thấp hơn nền và đủ mã
đo mới nhận đạt. Dấu `.da-nhan.json` được giữ cả khi lỗi/chưa rõ; không chạy
lại để chọn kết quả tốt. Chưa có nền/biên bản: **N1 chưa kiểm**.

Số 0 chỉ ghi khi đã quan sát 0 thật. Thiếu số → `null`/“chưa đo”, không ghi
0 giây/0 token/0% thay phần chưa đo. Lượt Local giả ghi riêng, 0 lượt Local
thật và 0 Cloud; số chấm giả không là độ chính xác máy thật.

Kết luận: **Chưa kiểm** (thay sau khi review artifact thật). Chỉ kết luận
một lượt cho tải/cấu hình đã đo, đủ ô/căn cứ, qua hậu kiểm và E6/N1. Không
có biên bản thì chưa chuyển bộ mặc định/lưu trữ. Nếu thất bại, trình b/c và
giờ riêng trong README công cụ; chưa mở batch/nhiều vòng.
