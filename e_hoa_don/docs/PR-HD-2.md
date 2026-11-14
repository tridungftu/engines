# [e_hoa_don] HD-2 — Bàn giao tệp, hủy và gửi lại qua SDK

PR: **chờ lead mở**. Bản nháp để lead commit/mở PR; Codex chưa commit/push.

Kết luận: **Đạt phạm vi HD-2 — đã kiểm bằng Core giả (CoreGia)** và MayChuGia loopback; chưa nghiệm thu quyền kho tệp/Core thật.

Đã làm:

- Chỉ sửa một tệp runtime `chay.py`, trong trần hai tệp được giao. Bổ sung kiểm hủy trước đọc, sau `doc_xml`, trước upload và trước return; bốn câu tiến độ cố định. Giữ nguyên parser, phép chiếu, lỗi/giới hạn HD-1 và `hoa_don.doc_xml@2`: `tep` XML → đủ 18 trường `truong`.
- Giữ nguyên đối tượng `tep_xml`; mở qua `viec.mo_tep(tep_id)`, tên chỉ là metadata. Upload `hoa-don-chi-tiet.json` qua `viec.tai_tep_ra`, chỉ trả trường sau khi có tham chiếu Core. Không ID tự cấp, raw bytes trong báo cáo, cache, kho tạm/dedupe, heartbeat/retry/server riêng hoặc ghi nhận nghiệp vụ; SDK quản lý gia hạn và gửi lại.
- Chứng minh lỗi rò stderr bằng test canary đỏ trước sửa. Lớp bọc `CongHoaDon` chỉ thay thông báo SDK thành `HD_SDK_THONG_BAO`, giữ nguyên việc SDK xử lý lỗi chung/hủy/lease; không bắt tràn exception trong handler. Giữ `context=None`, `can_kiem_tra=true`, identity/digest null và `NOT_PERFORMED`.
- Thêm **102 test HD-2** trên nền 157 test HD-1. Qua cả bộ nhớ và HTTP: bytes/hash, ID không UUID, đầu vào tải riêng, metadata đường dẫn không được mở, mất 1 hoặc 3 ACK ở tệp/kết quả/kết thúc vẫn đúng một lần ghi mỗi thao tác và cùng Idempotency-Key; upload lỗi hoặc thiếu ID không XONG; hủy bốn mốc không nộp; lease 409/404/410 ở đọc/tiến độ/upload và gia hạn SDK không nộp/kết thúc; giao lại cùng việc; hai pháp nhân DEMO cùng XML xử lý riêng; canary trong lỗi/tiến độ/stderr. Hai ca tiến trình kiểm `app.chay` và module entry point nhận đúng một dòng stdin, giữ stdin mở khi Core đã nhận kết quả.

Kết quả kiểm thực tế trên **Windows, Python 3.13.14, SDK 2.0.0**, dùng `-B`:

```text
.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -B -m pytest e_hoa_don/tests -q
→ 259 passed in 37.53s; 0 skipped; mã thoát 0
.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import, cây gói và tiến trình sạch; mã thoát 0
```

SDK cài offline từ wheel trong repo, SHA-256 khớp `SHA256SUMS.txt`: `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Pytest 9.1.1 và phụ thuộc kiểm thử chép offline từ bản có sẵn vào venv, không thêm dependency runtime. Test trong tiến trình pytest chỉ mở kết nối đúng cổng MayChuGia loopback đã đăng ký; tiến trình con chỉ được cấp địa chỉ MayChuGia. Không cổng thuế/Cloud/Node. Chưa chạy Linux hoặc cài máy sạch HD-4.

Thời gian thực tế: **0.195 giờ** (01:55:00–02:06:41, 15/11/2026, UTC+07) (ước tính trong phiếu: **3 giờ**).

Lệch khỏi phiếu / quyết định tạm đã dùng: lớp bọc nhật ký dựa trên `_ghi` nội bộ của SDK 2.0.0 đã ghim; không thay SDK. Ca giao lại dùng hàng việc nội bộ CoreGia vì chưa có seam công khai. Test double HD-1 được bổ sung `kiem_huy`; fixture chặn mạng chỉ mở ngoại lệ đúng MayChuGia cho HD-2. Không thay hợp đồng đầu vào/ra, phiên bản gói hoặc nghiệp vụ HD-1. Chỉ sửa trong `e_hoa_don/`; môi trường `.venv` theo hướng dẫn giao việc.

Cần Core / Chờ Anh mới phát sinh: SDK cần hook nhật ký an toàn và seam lỗi lease/giao lại công khai, đã ghi VIEC. Hủy sau upload có thể để lại tệp đã lưu mà không có kết quả; chưa chứng minh Core thật dọn tệp hoặc kiểm quyền theo pháp nhân. Không phát sinh câu cần Anh chốt để bàn giao HD-2. Giữ các nợ context tin cậy/kho tệp và phần ZIP/bảng kê/tải đang chờ. Không chạy bài Core thật 120 phút.
