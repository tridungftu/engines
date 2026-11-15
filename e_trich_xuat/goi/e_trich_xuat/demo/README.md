# Dữ liệu DEMO

Hai tệp DOCX chỉ chứa dữ liệu giả có nhãn DEMO: Công ty DEMO Ánh Dương,
1.000.000 VND, ngày 2026-10-30. Không có giá trị giao dịch.
Tệp thứ nhất có số tự động, ô rỗng và ô gộp; tệp thứ hai có Track Changes.
Nguồn sinh xác định: `e_trich_xuat/tests/mau_docx.py`, nằm ngoài gói chạy.

Hai DEMO TX-3 đã đăng ký trong `engine.json`: hậu kiểm nhận phản hồi AI
giả đầy đủ, xuất nhận bảng thật từ lõi hậu kiểm. Dữ liệu chuyển từ
`e_trich_xuat/tests/mau_tx3.py`, qua chuẩn bị/hậu kiểm thật trên CoreGia.
`DEMO-ho-so-hau-kiem.json` chứa snapshot và văn bản giả có băm/kích thước
thực, không phải placeholder hoặc cấu hình của engine. Bản cấu hình đã
ghim trong hồ sơ chỉ là bằng chứng của lượt chuẩn bị DEMO trước đó.

Trước chạy mẫu, cổng kiểm gọi `e_trich_xuat.demo.nap_ho_so_demo(core, app)`:
tải bytes hồ sơ vào kho CoreGia qua API công khai, thay mã tham chiếu DEMO
bằng mã Core vừa cấp và tính lại băm toàn phong bì yêu cầu AI. Nội dung
snapshot, bộ, prompt, văn bản và băm hồ sơ giữ nguyên. Helper không tự tạo
cấu hình, không chạy từ handler, không giả phiếu đăng ký trong test.
Cổng `tests/chay_demo_voi_ngan_gia.py` nạp riêng cấu hình DEMO vào ngăn RAM
và chạy đủ **5/5 DEMO**, **đã kiểm bằng Core giả (CoreGia)**, 0 Cloud.

CLI SDK 2.0 chỉ tự nạp `tep_demo` ở đầu vào loại `tep`; chưa nạp hồ sơ
tham chiếu trong `tra_loi_ai` (C-TX-06). Vì vậy CLI chuẩn **3/5 ĐẠT**:
chuẩn bị thiếu cấu hình (C-TX-04), hậu kiểm thiếu hồ sơ ở kho (DANG_CHAY
sau lỗi 404 bị SDK coi là mất quyền giữ việc). Đây không phải kết quả
chạy xanh; cần Core/SDK bổ sung cổng DEMO tệp tham chiếu cho loại riêng.
