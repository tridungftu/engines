# Trích thông tin hợp đồng — TX-1, bản 0.2.0

TX-1 chỉ công bố **`trich.doc_docx@1`**: nhận phong bì `tep` có MIME DOCX,
đọc bytes bằng `viec.mo_tep`, trả phong bì `van_ban_tai_lieu`.
Các bước chuẩn bị AI, hậu kiểm và xuất Excel thuộc TX-2/3, chưa đăng ký.
Phần đã chạy test: **đã kiểm bằng Core giả (CoreGia)**; chưa nối Core thật.

DOCX được Accept All bằng XML trong RAM. Tệp gốc không đổi;
`bam_dau_vao` là SHA-256 bytes gốc. Văn bản giữ thứ tự đoạn/bảng, ô rỗng,
ô gộp, số tự động. Không có dữ liệu phân trang thật nên `so_trang=0`,
`trang=[]`, có cảnh báo vị trí theo đoạn/Điều/Khoản. Trường tùy chọn
`khoi_docx` chứa cây đoạn/bảng/ô, gộp hàng/cột và offset Unicode nửa mở
`[bat_dau, ket_thuc)` trong đúng `van_ban`; không có trang/hộp giả.
Ô gộp chỉ có ô gốc trong danh sách `o`; biểu diễn văn bản để trống các
vị trí tiếp tục gộp, không lặp nội dung ô gốc. Ô rỗng thực sự vẫn có mặt.
Đầu/chân trang, chú thích và hình ảnh/đối tượng nhúng có cảnh báo khi gặp;
không nhận dạng chữ trong ảnh. Schema chung được chép nguyên byte vào `contract/`.

Giới hạn đều từ chối bằng lỗi, không cắt nội dung:

| Giới hạn | Giá trị |
|---|---:|
| Bytes DOCX / thời hạn bước tại Core | 20 MiB / 120 giây |
| Tổng dung lượng giải nén khai báo / một XML | 64 MiB / 16 MiB |
| Số thành phần ZIP / tỷ lệ giải nén | 2.048 / 200 lần |
| Số nút / độ sâu một cây XML | 200.000 / 128 |
| Toàn văn / phong bì kết quả JSON UTF-8 | 500.000 ký tự / 20 MiB |
| Ô / cột bảng / bảng lồng | 50.000 / 256 / 16 mức |

DTD/entity, ZIP có đường không hợp lệ, thành phần trùng, liên kết, mã hóa
hoặc phương pháp nén chưa hỗ trợ bị từ chối. Không chuyển `.doc`, không
dùng Word, không OCR/AI hoặc gọi engine khác. Số lượt Cloud: **0**.

`cau_hinh.schema.json` chỉ là tài nguyên khai cấu trúc. Giá trị nằm trong
bảng `cau_hinh`, phạm vi `engine`, duy nhất bản hệ thống `ma=mac_dinh`,
trường JSON `gia_tri` ≤64 KiB, không hết hạn; cập nhật bằng CAS `row_version`.
Màn `ui/cau_hinh.js` dùng `KttCore.engine("e_trich_xuat").cau_hinh.doc/luu`;
đầu vào/đầu ra cổng màn là `{gia_tri, phien_ban_cau_hinh}`. Export `nap`
(đồng thời default) nhận `{goc, KttCore}` và trả hàm tháo màn. Cần lead Core
review adapter nạp màn trước cài. UI chỉ có trần ngân sách và nút Lưu;
model/IP thuộc Hỏi AI, bộ tham số thuộc module.

Thiếu bản ghi không làm engine chết. DOCX độc lập với ngân sách AI nên hai
DEMO không cần cấu hình. Hàm `ghim_cau_hinh(viec, app)` dành cho bước cần cấu
hình sẽ trả `CHUA_CAU_HINH` nếu thiếu; chỉ điền mặc định 16.000 vào bản đã có.
Hàm đọc một bản và giữ phiên bản; ưu tiên snapshot SDK 2.1 trên việc nếu có.
SDK 2.1 sẽ tự xử lý `engine.cau_hinh_doi`; thay đổi cấu hình không sửa bản
chụp của việc cũ. Chưa có API/sự kiện này trong SDK 2.0.0.

Khai ngăn/cấu hình/màn dự kiến nằm riêng ở `KHAI-SDK-2.1.json`, không thêm
khóa vào phiếu 2.0. `chon_ngan(app)` ưu tiên `app.ngan`; tạm dùng RAM và cảnh
báo stderr một lần. Khởi động lại sẽ mất cấu hình. Hai tệp ngăn/cấu hình
là bản tạm theo chỉ dẫn lead vì NGAN-0 chưa gộp; test SHA đang chờ NGAN-0,
lead phải đối chiếu và thay bằng mẫu chung. Không lưu cấu hình/bộ/log/kết quả
trên máy. Đường DOCX không tạo tệp tạm.

SDK 2.0 kiểm MIME/kích thước trước handler với câu lỗi khác phiếu TX-1.
`EngineTrichXuat` kế thừa `Engine.tu_khai_bao`, chỉ bọc `_ket_thuc` để dịch
hai lỗi đó sang lỗi TX-1 và `_ghi` để tránh traceback lộ dữ liệu. Vòng việc,
gia hạn, hủy và ACK vẫn do SDK thực hiện. Cần Core cung cấp hook công khai
(C-TX-05); khi nâng SDK phải kiểm lại hai seam này, không sửa SDK/wheel.

Từ gốc repo, dùng `.venv/Scripts/python -B` trên Windows hoặc
`.venv/bin/python -B` trên Linux:

```text
python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat
python -B -m pytest e_trich_xuat/tests -q
python -B e_trich_xuat/tests/kiem_doc_lap.py
node --test e_trich_xuat/tests/ui/cau_hinh.test.mjs
```

Luôn chạy `-B` hoặc `PYTHONDONTWRITEBYTECODE=1` để giữ gói sạch bytecode.
Test chỉ dùng DEMO, CoreGia, NganBoNho và KttCore giả; không cần mạng.
Máy kiểm phiên này là Windows; Linux chưa chạy thực tế vì không có runtime.
