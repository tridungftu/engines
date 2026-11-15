# [e_hoa_don] HD-3 — Bộ XML DEMO có đáp án và regression

Bản nháp cho lead; PR: **chờ lead mở**. Không commit/push.

### Bàn giao HD-3 — mốc 14/11/2026, kiểm thực tế 15/11/2026

Kết luận: **Đạt phạm vi HD-3 — đã kiểm bằng Core giả (CoreGia)**. PR: **chờ lead mở**; bản nháp `PR-HD-3.md`, tiêu đề `[e_hoa_don] HD-3 — Bộ XML DEMO có đáp án và regression`. Chưa nghiệm thu Core thật; không commit/push.

Đã làm:

- `engine.json` có đúng ba DEMO dương tính trong `demo/`: số 0000123/ngày 2026-10-30, 1000000 VND + 100000 VND = 1100000 VND; tiền lẻ 1000000.123456 VND + 100000.012345 VND = 1100000.135801 VND; mẫu thiếu KHHDon, MST mua rỗng và thiếu TgTTTBSo để kiểm null/ABSENT/EMPTY/cảnh báo/HOLD. Không thêm Ten ngoài allowlist; Công ty DEMO Ánh Dương là nhãn mô tả fixture. TToan ngoài semantic envelope V1 vẫn giữ issue, không nâng thành đầy đủ.
- Ba bản fixture độc lập ở `tests/demo/`, đáp án literal `dap-an.json` viết từ XML, pin SHA-256/số bytes `bam-fixture.json` tính độc lập với parser. `.gitattributes` giữ bytes XML UTF-8/LF trên Windows/Linux; chuẩn hóa bản checkout Windows về LF đã ghim của fixture tiền nguyên. Không nhận đã kiểm hash golden/overlay cũ khi thiếu bytes gốc. `tests/demo/README.md` đối chiếu ý đồ bốn test tham chiếu; không sửa/chạy nguyên trạng namespace Core hoặc thêm shim.
- Thêm **24 ca HD-3**: kiểm đủ 18 trường, từng header/dòng/occurrence/locator, bytes/hash và JSON qua CoreGia.doc_tep, Decimal trong context precision=2, tiền/thuế, context thiếu và identity/digest null; MIME sai chặn trước parser; lỗi cấu trúc đúng lớp LoiNghiepVu/mã/câu HD-1; DTO bất biến/snapshot bytes và Issue SDK. Hai ca XML 1.000/1.001 dòng sinh trong tmp_path/DEMO: 1.000 giữ đủ thứ tự/nguồn, 1.001 từ chối không upload/nộp kết quả. Ca thiếu TToan không tính tổng từ dòng.
- Chạy tiếp toàn bộ regression HD-0…HD-2: tiền/ngày sai, trùng/rỗng/thiếu/mixed, tiền vượt miền, tổng lệch, currency thiếu, bytes/JSON vượt trần, hủy, upload/retry/mất lease, canary. Không skip/xfail hoặc cắt dữ liệu. **0 tệp runtime thay đổi** (trần 2); không mở ZIP/bảng kê/tải/Cloud/Node. Cập nhật hiện trạng và README để phân biệt lịch sử @1 với gói @2, giữ HD-4 chờ làm.

Kết quả thật trên Windows, Python 3.13.14, SDK 2.0.0; wheel cài offline --no-index --no-deps và SHA-256 khớp SHA256SUMS.txt. Pytest 9.1.1 cùng phụ thuộc kiểm thử có sẵn được chép offline vào venv; không thêm dependency runtime.

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | **3/3 DEMO [ĐẠT]** | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q` | **283 passed in 38.65s, 0 skipped** | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | **[ĐẠT] AST/import, cây gói và tiến trình sạch** | 0 |

Thời gian thực tế: **0.208 giờ** (02:08:00–02:20:27, 15/11/2026, UTC+07); ước tính trong phiếu **3 giờ**. Mốc giờ bắt đầu theo lead.

Lệch khỏi phiếu / quyết định tạm đã dùng: **không mở rộng phạm vi**, giữ context=None, tiền exact, identity/digest null, trạng thái thuế UNKNOWN/ghi nhận NOT_PERFORMED. Oracle lượt đầu được sửa sau đối chiếu định nghĩa lõi: TToan có TOTAL_SECTION_UNSUPPORTED (không thêm UNSUPPORTED_ELEMENT), quan hệ không có là ABSENT; không sửa runtime hoặc thêm cảnh báo để né lỗi cấu trúc. Pin chỉ xác nhận ba fixture mới có bytes hiện hữu, không chứng minh tương thích corpus/golden cũ.

Cần Core / Chờ Anh mới phát sinh: **không có**. Giữ nợ context tin cậy, quyền tệp theo pháp nhân, hook log/seam lease SDK và corpus cũ tại mục Cần Core. XML **đã kiểm bằng Core giả (CoreGia)**; ZIP/bảng kê/tải và quyền/Core thật còn chờ Anh/Core theo phiếu; HD-4 ghim nguồn/cài sạch chưa làm. Chưa chạy Linux, máy sạch HD-4 hoặc bài Core thật 120 phút. Không dùng tài khoản/cổng thuế thật.
