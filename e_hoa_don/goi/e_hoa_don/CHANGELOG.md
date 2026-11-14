# CHANGELOG — e_hoa_don

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
