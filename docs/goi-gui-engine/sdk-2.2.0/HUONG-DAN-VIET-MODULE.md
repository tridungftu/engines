# Hướng dẫn viết module cho Core

SDK 2.1.1 dùng chung cho module và engine. Bắt đầu từ `module-demo/demo_ho_so/` trong bộ phát hành: `module.json` là phiếu khai báo; `backend/` xử lý; `frontend/` hiển thị; `schema/` và `contract/` mô tả dữ liệu. Xem `API-CORE-v1.md` để tra API chung.

## Khai báo gói

Trong `module.json`, đặt `phien_ban_manifest: 2`, `loai: "module"`, `ma`, `ten`, `phien_ban`, `nha_phat_trien`, `tuong_thich`, `goi`, `backend`, `tien_trinh`, `giao_dien`, `quyen`, `hanh_dong`, `ma_loi`, `du_lieu`, `contract`, `nut`. Mã module gồm 3–31 ký tự, bắt đầu bằng chữ thường; các ký tự sau là chữ thường, số hoặc dấu gạch dưới. `goi` khai `tep_kiem_ke`, thuật toán băm và `phu_thuoc_module` (có thể rỗng). `backend.diem_vao` trỏ tới điểm vào Python; `tien_trinh` khai cả `nhan_listener` và `che_do_mac_dinh`. `giao_dien.tai_nguyen` phải chứa `diem_vao`.

Mỗi quyền có mã `<tai_nguyen>.<dong_tu>` và tên hiển thị. Động từ chỉ được là `xem`, `xem_du`, `lap`, `sua`, `kiem`, `duyet`, `huy`; nút tạo bản ghi dùng `lap`, sửa bản ghi dùng `sua`. Core gắn mã module vào quyền khi cài. Xem các quyền `ho_so.xem`, `ho_so.lap` trong mẫu.

Mỗi phần tử `hanh_dong` khai `ma`, `ten`, `phuong_thuc`, `duong_dan`, `quyen`, schema `dau_vao`/`dau_ra` khi cần, `kieu` (`dong_bo` hoặc `nen`) và `chong_trung`. Bộ chạy SDK hiện chưa hỗ trợ hành động `nen`; mẫu dùng `dong_bo`. Core tạo route `/api/v1/module/{ma}{duong_dan}`, kiểm phiên, quyền và schema trước khi chuyển yêu cầu cho module. Đường dẫn có thể chứa biến như `{id}`. Với `chong_trung: true`, bên gọi gửi `Idempotency-Key`. Xem hai hành động đọc trong mẫu.

Khai `ma_loi` gồm `ma`, mã `http`, `thong_diep` tiếng Việt dễ hiểu; backend trả mã lỗi nghiệp vụ đã khai. Phong bì API dạng phẳng gồm `ma`, `thong_diep`, `request_id`, `thu_lai_duoc`, và có thể có `chi_tiet`. Màn hiển thị `thong_diep`; mã và `request_id` đặt trong “Chi tiết hỗ trợ” thu gọn. Không đưa dữ liệu nghiệp vụ hoặc bí mật vào câu lỗi.

`du_lieu.ngan` khai từng ngăn và các cột `ma`, `ten`, `kieu`; Core tạo khối và cột chuẩn, phân tách dữ liệu theo pháp nhân. Các kiểu gồm `van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`, `khoa_noi` (khai thêm `ngan_dich`). Mẫu khai ngăn `ho_so`, trong đó `tep_goc` tham chiếu tệp. `contract.cong_bo` khai dữ liệu công bố: mã, phiên bản, module sở hữu, tệp mô tả, schema, ví dụ, quyền đọc và ngăn nguồn; xem các tệp tương ứng trong `contract/` của mẫu.

`nut` khai mã, tên, phần hiển thị, thao tác đầu, loại và giới hạn tệp nhận, ngăn kết quả, quyền và `sdk_dung`. Khai đúng các thao tác SDK cần dùng trong `hanh_dong[].sdk_dung` hoặc `nut[].sdk_dung`, chẳng hạn `quy_trinh.ket_qua`, `ngan.doc`, `ngan.them`, `ngan.sua`. Admin gắn quy trình và ghép trường kết quả với cột ngăn trên Core; gói không ấn định quy trình.

## Viết backend và giao diện

Trong `backend/xu_ly.py`, viết hàm `(sdk, yeu_cau)` và bảng `XU_LY` theo `hanh_dong.ma`. `yeu_cau` gồm `duong_dan`, `truy_van`, `than`, `ngu_canh`; kết quả phải khớp schema đầu ra. `backend/chay.py` chuyển bảng xử lý, bảng sự kiện và lớp lỗi cho `module_runtime.chay_theo_khai_bao`. SDK nhận ngữ cảnh do Core cấp và kiểm quyền; không tự chọn pháp nhân hay kết nối riêng từ yêu cầu.

`sdk.ngan(ma).doc(loc, gioi_han, con_tro)` trả `danh_sach` và `con_tro_tiep`; `loc` lọc bằng theo cột. Dùng `sdk.ngan(ma).them(dong)` hoặc `sdk.ngan(ma).sua(id, dong)` để ghi ngăn thuộc module, với thao tác được khai tương ứng. Mẫu đọc ngăn trong `danh_sach_ho_so` và `xem_ho_so`.

Khi quy trình gắn với nút hoàn tất, Core gửi `quy_trinh.xong` qua route nội bộ của nút; module không phải khai sự kiện nhận trong phiếu. SDK đọc tham chiếu kết quả rồi gọi hàm nhận với `tep_nut` và `ghep`. Xem `SU_KIEN` và `nhan_quy_trinh_xong` trong mẫu: hàm tự chọn cột tệp và ghi các giá trị được ghép vào ngăn bằng `ngan.them`. Không coi tham chiếu trên bus là toàn bộ nội dung kết quả.

Trong `frontend/chinh.js`, đánh dấu phần tử bằng `data-ktt-nut="doc_tep"` và gọi `sdk.nut.dat('doc_tep', phan_tu)` như mẫu. Core chỉ vẽ nút khi quy trình đã áp dụng và người dùng có quyền; nếu không đánh dấu vị trí, Core đặt nút ở thanh thao tác của phần.

## Đóng gói và cài

Hoàn thiện các tệp được phiếu tham chiếu, cập nhật `KIEM-KE.json` với mã băm đúng cho gói. Không đưa mật khẩu, khóa, địa chỉ hay đường dẫn cố định của máy vào gói. Trong Quản trị Core, chọn thêm module, đưa gói lên, xem quyền và thay đổi dữ liệu, duyệt cài rồi bật module. Sau đó Admin gắn quy trình đã áp dụng vào nút và ghép kết quả với ngăn. Kiểm thử với dữ liệu DEMO trước khi đưa vào sử dụng.
