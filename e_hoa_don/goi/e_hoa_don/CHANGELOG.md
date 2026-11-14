# CHANGELOG — e_hoa_don

## HD-2 — mốc 14/11/2026, kiểm thực tế 15/11/2026

- Chỉ sửa runtime `chay.py` (1/2 tệp cho phép); giữ nguyên parser/phép chiếu/lỗi HD-1, `hoa_don.doc_xml@2` và phiên bản gói. Kiểm hủy trước đọc, sau parse, trước upload và trước return; bốn câu tiến độ cố định, không chứa định danh/dữ liệu tài liệu.
- Giữ mở theo `tep_id` qua SDK, nguyên tham chiếu XML/bytes/hash và bàn giao JSON trước khi trả trường. Không ID tự cấp, kho tạm/cache/dedupe, nhận nghiệp vụ, heartbeat/retry/server riêng. SDK quản lý lease và Idempotency-Key.
- Test canary chứng minh SDK 2.0.0 in traceback/nội dung exception; lớp bọc `CongHoaDon._ghi` chỉ in mã cố định `HD_SDK_THONG_BAO`, không đổi xử lý lỗi/hủy/lease. Ghi Cần Core/SDK: hook nhật ký an toàn và seam lease/giao lại công khai; không sửa SDK. Hủy sau upload không nộp kết quả, vòng đời tệp đã upload thuộc Core.
- Thêm **102 test HD-2** qua CoreGia trong bộ nhớ và MayChuGia loopback: đọc/upload, ID opaque, bytes/hash, metadata tên không mở đường dẫn, mất 1/3 ACK ở ba thao tác không ghi trùng, upload lỗi/thiếu ID, hủy bốn mốc, mất lease 409/404/410 và gia hạn SDK, giao lại thuần, hai pháp nhân cùng XML không cache, canary stderr/lỗi/tiến độ. Thêm hai ca tiến trình `app.chay`/module nhận một dòng JSON stdin, giữ stdin mở lúc việc đã bàn giao.
- Ba lệnh nghiệm thu Windows/Python 3.13.14/SDK 2.0.0 với `-B`: SDK **1/1 DEMO [ĐẠT]**; pytest **259 passed in 37.53s, 0 skipped**; kiểm độc lập **[ĐẠT]**; cả ba mã thoát 0. **Đã kiểm bằng Core giả (CoreGia)**; chưa kiểm quyền kho tệp/Core thật, Linux hoặc máy sạch HD-4. Chỉ DEMO, không thuế/Cloud/Node.
- Thời gian thực tế: **0.195 giờ** (01:55:00–02:06:41, 15/11/2026, UTC+07) (phiếu **3 giờ ước tính**). PR: **chờ lead mở**; bản nháp `docs/PR-HD-2.md`, chi tiết `docs/VIEC.md`. Không commit/push, không mở phần ZIP/bảng kê/tải.

## HD-1 — 15/11/2026

- Phân biệt XML hỏng và encoding/DOCTYPE/namespace/path ngoài profile bằng lỗi cố định; không phản chiếu nguồn hoặc bắt tràn DataError. Nhiều TToan không chiếu scalar mơ hồ; giữ exact text/occurrence, money/relations/thuế, issue ngoài envelope V1 và context=None.
- Lead Claude duyệt cặp runtime `doc.py` + `chay.py` (hai tệp, trong trần ≤5), không phải quyết định của Anh. Parser `hoa_don_xml.py` giữ nguyên. Sửa `HD_XML_QUA_LON`/`HD_KET_QUA_QUA_LON`; chỉ bọc đúng lỗi kích thước trong khối mở/đọc tệp, giữ lỗi khác/hủy/mất lease/invariant.
- Thêm trần vận hành 1.000 HHDVu/XML, XML parser tiền kiểm không dựng cây, dừng ở dòng 1.001 trước DTO/JSON bằng `HD_QUA_NHIEU_DONG_HANG`. Không cắt dòng/occurrence; comment/CDATA không bị đếm nhầm. README/VIEC ghi giá trị, lý do và giới hạn bằng chứng; trần JSON 32 MiB vẫn áp dụng trước upload.
- Thêm 20 test DEMO lượt bổ sung (HD-1 tổng 94 test mới trên nền HD-0 63 test). Năm ca đỏ lượt trước đã xanh. Ca 200.000 HHDVu chứng minh chặn trước parser lõi/JSON; đúng 1.000 dòng vẫn giữ đủ thứ tự/occurrence.
- Windows, Python 3.13.14, SDK 2.0.0, `PYTHONDONTWRITEBYTECODE=1`: SDK 1/1 DEMO [ĐẠT]; pytest `-q -p no:cacheprovider` **157 passed in 5.57s, 0 skipped**; kiểm độc lập [ĐẠT]; cả ba mã thoát 0. **Đã kiểm bằng Core giả (CoreGia)**, chưa nghiệm thu Core thật, chưa chạy Linux/máy sạch HD-4.
- Bàn giao và bản nháp PR cũ chuyển vào VIEC mục Bàn giao HD-1; giữ và cập nhật `docs/PR-HD-1.md` để lead dùng. Lượt bổ sung khoảng 0.2 giờ, tổng HD-1 khoảng 0.37 giờ gồm mốc trước 0.17 giờ; phiếu 3 giờ ước tính. Không git add/commit/push. PR: chờ lead mở. Không phát sinh Cần Core/Chờ Anh mới; giữ nợ SDK ánh xạ lỗi 413 đã được engine bọc hẹp.

## 1.0.0 — HD-0, 15/11/2026

- Tạo gói SDK 2.0 với đúng một năng lực `hoa_don.doc_xml@2`, `tep` → `truong`, đủ 18 trường phiếu §2.2; 16 MiB/XML/600 giây, cho phép hủy.
- Chuyển nguyên thuật toán strict/Decimal/DTO của `ma-nguon/lib/hoa_don_xml.py`, chỉ đổi hai import sang SDK 2.0.0 (kể cả lazy `Issue`). Giữ `__module__` legacy làm dấu vết; không shim, pickle hoặc kênh cũ. Nhánh ZIP nội bộ chưa kích hoạt.
- Lớp chiếu bảo toàn số 0 đầu, Decimal exact kèm currency, hash bytes, locator, occurrence, tiền/quan hệ nguồn; null khi thiếu/sai/mơ hồ/vượt miền. JSON kỹ thuật dùng `ra_json`, không raw bytes, thêm `van_de_phep_chieu` để lưu issue của phép chiếu.
- Handler dùng `viec.mo_tep`, đọc thực tối đa 16 MiB + 1; luôn `context=None`; upload JSON thành công qua `viec.tai_tep_ra` trước khi trả trường. JSON vượt 32 MiB từ chối, không cắt. `can_kiem_tra=true`, định danh/semantic digest null khi thiếu context; giữ `UNKNOWN`/`NOT_PERFORMED`.
- Thêm hai JSON Schema, cấu hình ngoài gói (không đọc ở khởi động/XML), README, DEMO giả, pin SDK và hồ sơ nguồn. Không tạo kho dữ liệu bền hoặc đọc bí mật.
- Kiểm AST/lazy/dynamic, cây gói và tiến trình sạch `-I -B -S` chỉ SDK/stdlib/gói XML; không bytecode/symlink/tệp vượt trần 20 MiB.

Kết quả thật trên Windows, Python 3.13.14, SDK 2.0.0 (wheel SHA-256 khớp bản phát hành), `-B`/`PYTHONDONTWRITEBYTECODE=1`:

```text
.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -B -m pytest e_hoa_don/tests -q
→ 63 passed in 0.82s; 0 skipped; mã thoát 0
.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import (kể cả lazy/dynamic), cây gói và tiến trình sạch; mã thoát 0
```

QA thêm: JSON Schema Draft 2020-12 hợp lệ và khớp báo cáo thật qua CoreGia, dùng công cụ `jsonschema` có sẵn trên máy để kiểm offline; không thêm dependency runtime. Pytest 9.1.1 và các phụ thuộc kiểm thử được chép từ bản cài sẵn vào venv, không truy cập mạng.

**Đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật.** Chưa chạy Linux hoặc bài máy sạch HD-4; test dùng pathlib/stdlib và mock I/O nên giữ khả năng chạy Windows/Linux, chưa coi đây là bằng chứng đã chạy Linux. Không chạy Node/Cloud/cổng thuế. Không thực hiện bài Core thật 120 phút.

Thời gian thực tế: 0.243 giờ (00:55:00–01:09:33, 15/11/2026, UTC+07; ước tính trong phiếu: 4 giờ). Mốc cập nhật VIEC theo giao việc: 14/11/2026; kiểm thực tế ngày 15/11/2026. PR: **chờ lead mở**; không commit/push. XML HD-1…HD-4 giữ theo phiếu, ZIP/bảng kê/tải còn chờ Anh chốt. Cần Core đã có: cửa context tin cậy/quyền tệp và kênh cấu hình máy; không phát sinh yêu cầu mới.
