# e_demo_doc_tep — Đọc tệp thành văn bản (DEMO)

Engine DEMO tối giản, đặt ngoài Core: năng lực `tep.doc_van_ban@1` nhận một tệp văn bản thuần `.txt` UTF-8 (loại `tep`, tối đa 5 MiB, `text/plain`) và trả nội dung thành `van_ban`; tệp không phải UTF-8 thì báo lỗi tiếng Việt. Thường đứng ở bước 1 của quy trình (nhận tệp người dùng tải ở nút). Chỉ dùng SDK (`kho_tri_thuc_sdk`); chạy thử không cần Core: `python -m kho_tri_thuc_sdk.thu <thư mục này>` (ví dụ ở `chay_thu_demo`, tệp `demo/mau.txt`). Chỉ dữ liệu DEMO.
