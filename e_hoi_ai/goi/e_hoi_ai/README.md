# e_hoi_ai — Hỏi AI (AI-0)

Khung gói SDK 2.0.0, phiên bản 0.1.0. Tạo từ mẫu `engine-demo/e_demo_dem_tu` của SDK 2.0.0 rồi đổi tên gói, phiếu và hàm xử lý. Chỉ dùng thư viện chuẩn Python (Python ≥ 3.11) và `kho_tri_thuc_sdk` 2.0.0; chưa gọi Local hoặc Cloud.

- `ai.hoi_tai_lieu@1`: nhận `van_ban` hoặc `van_ban_tai_lieu`, trả bộ trường `tra_loi`, `co_can_cu`, `trich_dan`, `model`.
- `ai.hoi_theo_yeu_cau@1`: nhận `yeu_cau_ai`, trả `tra_loi_ai`.
- Cả hai hàm hiện trả lỗi nghiệp vụ `CHUA_LAM`. Chưa thực hiện hỏi AI, kiểm trích dẫn hoặc chọn model. Không có prompt mặc định chung.

## Cấu hình máy

`e_hoi_ai.cau_hinh_may.doc_cau_hinh()` đọc JSON ngoài gói theo biến `KTT_ENGINE_CAU_HINH`. Khi biến chưa đặt, dùng `%PROGRAMDATA%\KhoTriThuc\engines\e_hoi_ai\cau_hinh.json`. Khi không có `PROGRAMDATA` (ví dụ Linux), không tự tìm tệp khác.

Thiếu tệp: trả `None`, không làm engine dừng khởi động. Khi xử lý việc cần Local AI, gọi `yeu_cau_cau_hinh()` để nhận lỗi nghiệp vụ `CHUA_CAU_HINH`. Các hàm tạm AI-0 vẫn trả `CHUA_LAM` theo phiếu giao. Đọc lại tệp ở mỗi lần gọi, không ghi tệp hoặc nhật ký nội dung cấu hình.

Schema ở `contract/cau_hinh_may.schema.json`. `local_ai.url` và `local_ai.timeout_giay` là bắt buộc; thời hạn phải là số dương. `quy_tac_model` tùy chọn, mỗi mục phải có đủ mẫu prompt, model ưu tiên và danh sách dự phòng. Các trường lạ, JSON lỗi hoặc trùng khóa bị từ chối bằng thông báo tiếng Việt không chứa dữ liệu đầu vào. Không chứa bí mật; URL không được có thông tin đăng nhập, query hoặc fragment. Kiểm địa chỉ mạng nội bộ thuộc AI-1.

Ví dụ dưới đây chỉ là cấu hình DEMO; chép vào tệp **ngoài gói** nếu cần kiểm bộ đọc:

```json
{
  "local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60},
  "quy_tac_model": [
    {"mau_ma_prompt": "demo.*", "uu_tien": "model-demo", "du_phong": []}
  ]
}
```

## Contract

Ba schema `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai` trong `contract/` là bản sao nguyên byte từ `_chung/contract/` trong repo. Pytest kiểm SHA-256 từng cặp; gói chạy độc lập không truy cập thư mục `_chung/`.

Các schema dùng Draft 2020-12, cho phép thêm trường tùy chọn để giữ tương thích phiên bản 1. `dong`, `tu`, `nghi_ngo` không bắt buộc; ô bảng trống và ô gộp được giữ lại. JSON Schema không biểu diễn được giới hạn dung lượng JSON UTF-8 của `khuon_tra_loi` (32 KiB) và `chuyen_tiep` (64 KiB); AI-2 sẽ kiểm khi xử lý. AI-0 chưa kiểm kết quả AI với khuôn trả lời.

## Kiểm AI-0

Chạy trong worktree, đặt `PYTHONDONTWRITEBYTECODE=1` để không sinh bytecode trong gói. Với PowerShell:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
.venv/Scripts/python -m pytest e_hoi_ai/tests -q
.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
```

**Giới hạn nghiệm thu:** AI-0 chưa có ví dụ `chay_thu_demo` (danh sách rỗng). Lệnh SDK hiện in `Phiếu chưa có ví dụ chay_thu_demo.` và trả mã **1**. Không coi đây là DEMO đạt; cổng DEMO chung ở AGENTS.md §5 còn chưa đạt. Các ví dụ hỏi AI và bộ chạy với Local giả thuộc AI-4. Bộ test AI-0 dùng CoreGia để xác nhận cả hai năng lực báo `CHUA_LAM`, không nộp kết quả thành công giả.

Tiêu chí riêng AI-0: `Engine.tu_khai_bao` đọc phiếu hợp lệ, pytest xanh và `kiem_doc_lap.py` mã 0. **Đã kiểm bằng Core giả (CoreGia)**; chưa kiểm Core thật, chưa thử model thật.
