# Kết quả theo đợt DEMO

Chứng minh C-RV-01/C-RV-02 (KQ-NUT mục 3), G5/G6/G14, M1/M4, E5/E9,
W3/W6 và lát L4.1–L4.3/L7.1. Chỉ dùng dữ liệu DEMO, không sửa Core.

Ba khóa đợt mẫu: `DEMO-01`, `DEMO-02`, `DEMO-03`. Người dùng chọn đợt và
tệp `.txt` UTF-8, bấm nút do module tự vẽ (`tu_ve: true`). Mỗi lần gửi tạo
một dòng mới trong ngăn bảng thường `ket_qua`, giữ cả lịch sử của cùng đợt.
Core tự tạo cột chuẩn `id`, `phap_nhan_id`, `nguoi_tao`, `tao_luc`, `sua_luc`,
`ban_ghi_goc_id`, `da_luu_tru` theo khuôn module; không có migration Core mới.

Route `POST /dot-demo/viec` lưu đợt và `viec_id` nhận từ `sdk.nut.chay`.
Hàm `quy_trinh.xong` tra ngăn theo việc, gọi `sdk.ket_qua.ds_tep` và
`sdk.ket_qua.doc_tep`, kiểm JSON rồi ghi `XONG` hoặc `LOI` với câu tiếng Việt.
Chỉ nhận đúng một `ket-qua.json` có MIME `application/json`; số dòng/từ phải
là số nguyên không âm, dòng đầu không quá 1.000.000 ký tự (giới hạn SDK ngăn).
Route lưu việc cũng kiểm kết quả đã hoàn tất để xử lý sự kiện đến trước liên kết.
Nếu việc chưa xong, giữ `DA_GUI`; không ghép sự kiện lạ vào đợt bất kỳ.
Màn chỉ vẽ form và nút gửi sau khi danh sách `/nut` cho phép `xuat_thong_ke`;
thiếu quyền, chưa gắn quy trình hoặc lỗi tra quyền đều ẩn form và nút.
Màn tự cập nhật tối đa 2 phút khi còn việc chờ, sau đó hướng tới Việc của tôi;
vẫn có nút cập nhật thủ công; mã lỗi chỉ trong
“Chi tiết hỗ trợ”. Nếu lưu liên kết lỗi, nút thử lưu dùng lại cùng việc/khóa,
không gửi tệp lần nữa. Giữ màn đang mở cho tới khi báo đã lưu liên kết.

## Giới hạn SDK 2.3.0 và lỗi tạm

Chưa xác minh được `viec_id` do trình duyệt gửi khi việc còn chạy: handler module
trong `sdk_core/chay_module.py` chỉ có `sdk.ket_qua.ds_tep/doc_tep`, không có
`sdk.viec.lay`. Cửa kênh `viec.lay` có tồn tại nhưng chỉ trả module/pháp nhân và
trạng thái, không trả nút sở hữu; không đủ để xác nhận việc thuộc `xuat_thong_ke`.
`quy_trinh.ket_qua` và các cửa tệp kết quả chỉ cho đọc việc đã `XONG`, trả cùng mã
`KHONG_TIM_THAY` cho việc chưa xong và việc không được đọc. Vì vậy `ghi_viec`
hiện chỉ kiểm UUID và liên kết đợt, chưa ngăn được việc gắn UUID bất kỳ hoặc việc
của nút khác. Không dùng việc đọc kết quả thay cho kiểm quyền lúc đang chạy.
Theo phiếu K142, giữ giới hạn này để lead xử lý cửa chung; không vá Core.

Lỗi `KHONG_TIM_THAY` khi nhận sự kiện xong, thiếu tệp, JSON sai hoặc sai khuôn
mới ghi `LOI`; lỗi kênh, `CHUA_SAN_SANG`, 429 và lỗi đọc tạm khác được ném lại
để Core giao lại sự kiện. Khi vừa lưu liên kết, `KHONG_TIM_THAY` vẫn giữ `DA_GUI`
vì việc có thể chưa xong. Engine chỉ trả tối đa 200 ký tự của dòng đầu.
Core chưa chuyển `quy_trinh.loi` tới hàm nhận của nút; màn dừng hỏi sau 2 phút
và hiện “Chưa có kết quả. Xem chi tiết ở mục Việc của tôi.”, không vá khoảng trống này.

## Lead nghiệm thu và phát hành

**Lead cài lên Core thử (CSDL ở 199), dựng quy trình gắn nút, bấm thử trên trình duyệt.**
Core/SDK phải chứa CK-1 + CK-2 (mốc `da565ee`); dùng SDK 2.3.0 khi phát hành.
Cài và bật engine `e_demo_xuat_tep`, cài/bật module; cấp quyền Xem và Lập.
Tạo quy trình một bước `tep.xuat_thong_ke@1`, gắn nút `xuat_thong_ke`,
không cần ghép cột vì module tự đọc tệp. Gửi `demo/mau.txt` của engine:
mong đợi 2 dòng, 8 từ, dòng đầu “Đợt DEMO một”. Thử hai đợt và gửi lại một
đợt: kết quả phải nằm đúng đợt, còn đủ lịch sử. Kiểm pgAdmin và ảnh từng bước.
Test PostgreSQL thật: lead chạy PG. Phiếu này chưa nghiệm thu trình duyệt.

Lead cập nhật `tools/dong_goi_sdk.py` khi phát hành:
- thêm `e_demo_xuat_tep` vào `ENGINE_DEMO`;
- công cụ hiện chỉ đóng module `demo_ho_so`: bổ sung sao chép gói
  `demo_ket_qua_nut` (gồm kiểm kê) vào phần module DEMO và bảng băm phát hành.

Kiểm kê: chạy `python -B -X utf8 goi-demo/module/tao_kiem_ke.py
goi-demo/module/demo_ket_qua_nut` từ gốc repo (ghép hai dòng thành một lệnh).
Chạy Python với `-B` để không tạo bytecode trong gói.
