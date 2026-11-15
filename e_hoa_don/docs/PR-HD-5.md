# [e_hoa_don] HD-5 — Lõi ZIP và kiểm kê từng tệp

Kết luận: **Đạt phạm vi HD-5** — lõi kiểm kê ZIP và hồi quy XML đã kiểm bằng Core giả (CoreGia); chưa nối Core thật.

Đã làm: thêm `zip.py` và `contract/bao_cao_zip.schema.json`; sửa đúng cổng `doc_goi_hoa_don_zip` trong `hoa_don_xml.py` (2/4 tệp runtime). Giữ nguyên parser XML/DTO/phép chiếu XML và `hoa_don.doc_xml@2`; không đổi manifest, `doc.py`, `chay.py`, dependency hoặc nguồn tham chiếu. Tên entry giữ gốc, ordinal 1-based và mở bằng ZipInfo; giữ mọi entry/trùng tên/trùng bytes, thư mục riêng. SHA-256 chỉ khi đọc hết và CRC đúng; đọc thiếu giữ băm/kích thước null với lý do. PDF/non-XML đọc có trần để băm; tên nguy hiểm/symlink/ZIP lồng không vào parser.

Kiểm metadata và byte thật: ZIP 64 MiB, 1.000 entry, 16 MiB/tệp, tổng giải nén 128 MiB, gate 1.000 HHDVu trước DTO, JSON UTF-8 32 MiB. Đối chiếu EOCD/central directory, kể cả ZIP nhiều đĩa và số entry giả. Vượt trần từ chối toàn việc; CRC/mã hóa/entry không mở được báo cục bộ. Không dùng COMPLETE của lõi để kết luận đã đọc hết; giữ UNKNOWN/NOT_PERFORMED/context=None, không suy đủ kỳ hoặc gộp trùng. Tất cả trong RAM; không tệp tạm, cấu hình, sổ, cache bền, ngăn hoặc gọi mạng.

Bổ sung 69 ca HD-5 với oracle độc lập: gói hỗn hợp, thứ tự khác từ điển, PDF/XML hỏng/ngoài profile, CRC/mã hóa/method, tên trùng khác bytes/NFC/casefold, tên gốc backslash, symlink/ZIP lồng, rỗng/chỉ thư mục, băm null và đọc tiếp sau lỗi, metadata giả/EOCD, biên thật 64/16/128 MiB và JSON vượt 32 MiB, 1.000/1.001 HHDVu trước DTO, hủy/mất lease và chặn filesystem. Điều chỉnh hai test lịch sử để thêm đúng zip.py và chỉ miễn phần cổng ZIP trong so sánh AST nguồn; toàn bộ parser XML/DTO còn lại phải nguyên AST. Nợ UTF-8 ở test_hd_2: giữ encoding=utf-8, thêm PYTHONUTF8=1/PYTHONIOENCODING=utf-8 cho subprocess.

Kết quả kiểm Windows/Python 3.13.14, SDK 2.0.0 (wheel offline, SHA-256 khớp SHA256SUMS), pytest 9.1.1 có sẵn qua venv system-site-packages; không thêm dependency runtime:

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | **3/3 DEMO ĐẠT** | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q --basetemp=.pytest-tmp` | **367 passed in 45.80s, 0 skipped** | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | **ĐẠT AST/import, cây gói, tiến trình sạch** | 0 |

Mọi kết quả qua cổng engine là **đã kiểm bằng Core giả (CoreGia)**. Kiểm ZIP HD-5 là unit tests thuần, chưa có handler/DEMO ZIP đăng ký; không gán kết quả unit thành nghiệm thu Core thật. Chưa chạy Linux/CPython 3.11 hoặc cài sạch ZIP (HD-8).

Thời gian thực tế: **07:51:00–08:15:19, 15/11/2026 UTC+07; 0.406 giờ** (mốc bắt đầu theo lead); phiếu **4 giờ ước tính**. PR: **chờ lead mở**. Không git add/commit/push.

Lệch khỏi phiếu / quyết định tạm đã dùng: theo ghi chú lead bổ sung trần tỉ lệ nén **1.000:1**, lựa chọn kỹ thuật chưa đo corpus; chỉ đọc STORED/DEFLATE có trần, method khác báo chưa hỗ trợ/băm null. Dùng hook ZipExtFile `_left`/`_update_crc` để không cắt theo file_size giả và đếm cả chunk lỗi CRC; `_EndRecData` để đối chiếu metadata. Các hook stdlib phải kiểm lại khi nâng Python; chưa thay đổi API/SDK đã khóa. Không viết parser XML thứ hai: tái dùng nguyên gate HD-1 và parser strict hiện có.

Cần Core / Chờ Anh mới phát sinh: **không**; giữ các nợ context tin cậy/quyền tệp/hook nhật ký/fixture đã có. `cau_hinh_may.py`, schema và test cấu hình lịch sử vẫn nguyên, ngoài đường chạy chay.py; ghi việc chuyển `LUU-TRU/` sau ở mục Cần Core, không xóa/di chuyển. Chưa đăng ký `hoa_don.doc_zip@1`; phần nối cổng thuộc HD-6. Không suy đã kiểm Core thật, Excel app hoặc bài nghiệp vụ 120 phút.
