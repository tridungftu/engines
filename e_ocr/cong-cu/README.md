# Công cụ e_ocr

1. Chạy `THU-ABBYY-THAT.cmd` để kiểm chạy khô; không gửi tài liệu.
2. Gói OCR cần `pdfplumber`, `Pillow` và `pypdfium2`, đã ghim trong `e_ocr/goi/e_ocr/requirements.lock`. Nếu chạy `--that` báo thiếu thư viện, Anh tự chạy `.venv\Scripts\python -m pip install --require-hashes -r e_ocr\goi\e_ocr\requirements.lock` từ thư mục gốc repo; lệnh này cần mạng.
3. Tạo ba thư mục DEMO riêng, tách biệt; cấu hình Hot Folder ABBYY theo hai thư mục vào/ra DEMO này, ngoài `abbyy-hotfolder` hiện có.
4. Chạy `THU-ABBYY-THAT.cmd --that --cau-hinh "<JSON cấu hình máy>" --ket-qua "<thư mục kết quả DEMO>"`; JSON dùng `abbyy.bat`, `thu_muc_vao`, `thu_muc_ra`, `thoi_han_giay`. `abbyy.bat` là cờ bật/tắt (`true`/`false`), không phải đường dẫn lệnh; thử thật cần đặt `true`.
5. Xem `ket-qua.json` và Word trong thư mục lượt DEMO; quá giờ là chưa rõ, không tự gửi lại; lượt thành công không xác nhận quy ước biên nhận lỗi.
