# [e_hoa_don] HD-4 — Ghim nguồn và cài máy sạch

Kết luận: Đạt phạm vi XML, đã kiểm bằng Core giả (CoreGia); chưa kiểm Linux/Core thật. PR: **chờ lead mở**.

Đã làm: đối chiếu SDK và SHA nguồn/gói; hai kịch bản cài sạch; fail-closed khi SDK thiếu hook `_ghi`; kiểm thiếu cấu hình. Không thêm nghiệp vụ, không sửa nguồn cũ/Core/SDK, không commit/push.

Kết quả kiểm Windows/Python 3.13.14: `kho_tri_thuc_sdk.thu` 3/3 ĐẠT; pytest 284 passed, 0 skipped; `kiem_doc_lap.py` ĐẠT; cài sạch Windows 3/3 DEMO và kiểm độc lập ĐẠT. Các mã thoát 0. Linux chưa chạy.

Thời gian thực tế: khoảng 0,12 giờ (02:22–02:29, 15/11/2026 UTC+07; ước tính 2 giờ).

Lệch khỏi phiếu / quyết định tạm: thêm chốt fail-closed và test theo yêu cầu lead; venv chính dùng pytest sẵn có, venv cài sạch chỉ cài SDK offline.

Cần Core / Chờ Anh mới phát sinh: hook nhật ký công khai không in traceback ra stderr; tiếp tục chờ context tin cậy, quyền tệp và chuyển @1 sang @2 do lead/Core. ZIP/bảng kê/tải chờ Anh, cần phiếu riêng cho tải.
