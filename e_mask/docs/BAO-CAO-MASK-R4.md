# Báo cáo MASK-R4 — 15/11/2026

Kết luận: Chưa đạt nghiệm thu chung — kho RAM/port vòng đời đã triển khai trong đúng ba runtime; thiếu cửa Core và kiểm kê gói chưa khớp.

Đã làm: kho `KhoAnhXaRAM` và quyền theo mã Core cấp, đủ module/người/tài liệu/pháp nhân/DEMO/instance/phiên RAM. TTL 600 giây, nguyên 60–900, snapshot đầu chuỗi và monotonic, deadline Core sớm hơn, retry không trượt. Một chuỗi sống/một bước sở hữu; nhường handler khi chờ AI; timer chủ động và finally dọn khi mở/hủy/lỗi/kết thúc/mất quyền/lease/hết hạn. Chống tái tạo/khác instance/double-open và đua hủy/timeout với khởi tạo/mở/chốt. Mất map trả lỗi cố định yêu cầu chạy lại, không cache kết quả mở hoặc output dở.

Kết quả kiểm: **đã kiểm bằng Core giả (CoreGia)**, Python 3.13.14, SDK 2.2.0 và jsonschema có sẵn; SDK wheel repo cài offline `--no-index --no-deps`, SHA-256 khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`. CLI chuẩn **0/2 ĐẠT, mã 1** (thiếu quyền tin cậy); pytest toàn bộ **2305 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed, 0 skipped, 147,49 giây, mã 1**. Kiểm riêng R4 **78 passed, 0 failed/skip/xfail, 1,12 giây, mã 0**. Kiểm độc lập gói gốc **mã 1** do kiểm kê, diff **mã 0**. Không gọi bộ kiểm toàn bộ là xanh; mọi ca hành vi/an toàn cũ giữ nguyên và qua, bốn xfail “giới hạn quy tắc, nợ CAO” không đổi.

Thời gian thực tế: **20:11:00–20:45:15 ngày 15/11/2026 (UTC+07), 0,57 giờ** tại mốc chốt kiểm và đối chiếu artifact; bắt đầu theo giờ lead giao. Phiếu **4–6 giờ ƯỚC TÍNH**, độ khó **kho**.

Lệch khỏi phiếu / quyết định tạm đã dùng: không nới phạm vi ba runtime, không sửa Core/SDK/dependency hoặc commit/push. Kiểm kê R1 bao cả gói đã lệch ở nền do checkout hai tệp; sau R4 cần cập nhật thêm bytes/SHA của runtime/CHANGELOG. Ngoại lệ cho tệp kiểm kê ngoài bảng §4 đang chờ phản hồi, chưa sửa. Không bỏ kiểm hoặc thay tiêu chí để làm xanh. Handler cũ còn được kiểm bằng fixture ngoài gói; chuyển map/snapshot/ngăn và nghiệp vụ mở sang API RAM thuộc R2/R5/R6/B7, chưa nhận luồng P4 tích hợp.

Cần Core / Chờ Anh mới phát sinh: C-P4-01/02 còn mở: ghim cùng tiến trình/instance/phiên RAM, quyền xuyên bước, quyền tạo một lần, thông báo vòng đời khi rảnh và đồng bộ kết quả cuối/ACK/deadline. Runtime từ chối khi thiếu; adapter giả chỉ ngoài gói. Không thêm câu hỏi nghiệp vụ. Chưa kiểm Core/Local/Office/Linux thật; Cloud giữ tắt.

Lệnh và trích dòng kết quả thật: [KET-QUA-KIEM-MASK-R4.txt](KET-QUA-KIEM-MASK-R4.txt). PR: **chờ lead mở**. Tệp kiểm kê đề nghị vẫn ngoài gói, chưa có phản hồi cho ngoại lệ thứ tư.

| Lệnh / phép kiểm | Kết quả thật |
|---|---|
| Kiểm nền full trước sửa | 2227 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed, 0 skipped; 181,60 giây, mã 1 |
| Full đầu sau sửa R4 | 2284 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed, 0 skipped; 132,32 giây, mã 1 |
| Full trung gian sau bổ sung ca đua | 2302 passed / 150,82 giây và 2304 passed / 149,80 giây; đều chỉ 1 failed kiểm kê, 4 xfailed/190 subtests, mã 1 |
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | 0/2 ĐẠT, mã 1; cả hai thiếu phiên/quyền `MASK_NGU_CANH_CHUA_XAC_MINH` |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | 2305 passed, 1 failed `test_mask_r1.py::test_kiem_ke_day_du_bytes_va_sha_tung_tep`, 4 xfailed cũ, 190 subtests passed, 0 skipped; 147,49 giây, mã 1 |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | Mã 1: “[LỖI] Không kiểm được một mục trong gói.” do kiểm kê gốc chưa cập nhật |
| `.venv/Scripts/python -B -m pytest e_mask/tests/test_mask_r4.py -q --tb=short` | 78 passed; 1,12 giây, mã 0 |
| `git diff --check` | Mã 0 |
| Bản sao đóng gói dùng kiểm kê đề nghị ngoài gói | Kiểm độc lập mã 0, đủ 51/51 tệp; không dùng kết quả này thay kiểm gói gốc |
| UTF-8/AST/khoảng trắng/bytecode | 5/5 tệp Python sửa/thêm đạt; không `__pycache__`/`.pyc` trong gói |

[Kiểm kê đề nghị](KIEM-KE-MASK-R4-DE-NGHI.json) chỉ là tài liệu ngoài gói: SHA-256 **31f7269fd61a99bda673430dd7b222c474588c4575040da3b9050d952c859054**, tính từ bytes checkout thực tế, không chuẩn hóa LF để nhận băm. Gói gốc `sql/kiem_ke.json` không sửa vì chưa có ngoại lệ giới hạn ba tệp trong MASK-P4 §4. Nếu lead gộp R2 hoặc đổi bytes gói phải tạo/kiểm lại, không chép nguyên bản đề nghị này sang gói đã đổi.

API nội bộ cho R5/R6/B7: `app.kho_anh_xa_ram.buoc(viec, loai='che'/'mo_che', ma_yeu_cau=...)` trả handle trong `with`. Dữ liệu riêng nằm ở `handle.du_lieu`; gọi `handle.kiem()` trong vòng xử lý dài. Bước che chờ AI gọi `handle.cho_ai()` trước ra `with`; không giữ tham chiếu dữ liệu để dùng ngoài quyền sở hữu. Mở luôn tiêu thụ khi ra, bất kể cờ đóng cũ. Dữ liệu cần giữ (map/gốc/span/Unicode/phiên bản/băm/kế hoạch/bytes) chỉ trong dictionary RAM này; không đưa sang port, kết quả che hoặc chuyen_tiep. Điểm chốt cuối dưới khóa chặn kết quả nếu timer/sự kiện đã hủy. Đồng bộ sau điểm này tới ACK thật cần Core C-P4-02/05; R4 không cam kết giao dịch qua mạng chỉ bằng khóa Python.
