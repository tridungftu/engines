# Công cụ e_ocr

1. Chạy `THU-ABBYY-THAT.cmd` để kiểm chạy khô; không gửi tài liệu.
2. Cài dependency của gói e_ocr theo hướng dẫn cài máy sạch trước khi thử thật.
3. Tạo ba thư mục DEMO riêng, tách biệt; cấu hình Hot Folder ABBYY theo hai thư mục vào/ra DEMO này, ngoài `abbyy-hotfolder` hiện có.
4. Chạy `THU-ABBYY-THAT.cmd --that --cau-hinh "<JSON cấu hình máy>" --ket-qua "<thư mục kết quả DEMO>"`; JSON dùng `abbyy.bat`, `thu_muc_vao`, `thu_muc_ra`, `thoi_han_giay`.
5. Xem `ket-qua.json` và Word trong thư mục lượt DEMO; quá giờ là chưa rõ, không tự gửi lại; lượt thành công không xác nhận quy ước biên nhận lỗi.
