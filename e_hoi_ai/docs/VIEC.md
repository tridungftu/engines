# VIỆC — danh sách việc duy nhất của project `e_hoi_ai`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc tài liệu bắt buộc; đối chiếu kế hoạch lát AI-0 đã giao | — | Xong — 14/11/2026 | Phạm vi, kiến trúc và cách triển khai theo `GIAO-CODEX-e_hoi_ai.md` và lệnh giao của Anh |
| 1 | Đóng gói độc lập theo cổng chung: bỏ shim, chỉ import SDK, build/cài wheel trên máy sạch | AI-13 | Đang làm — 14/11/2026 | Khung AI-0 xong; ghim đầy đủ và kiểm máy sạch thuộc AI-5 |
| 2 | Màn Chạy thử DEMO, Cổng Local AI, Cổng Cloud AI (tắt ở bản 1) thành **giao diện của engine** (không đặt trong Core) | AI-10, 11, 12 | Chờ làm | Bản cũ trong `tu-core-cu\phia-core\` |
| 3 | Tự phát hiện model trên máy AI qua Tailscale, chọn theo module/function | AI-10 | Chờ làm |  |
| 4 | Lát 8: thử thật gpt-oss 20B, Qwen3 8B, Gemma; Local lỗi phải báo rõ, 0 Cloud | AI-14, AI-8 | Chờ làm | Công cụ ở `tu-core-cu\tools\` |
| 5 | Ghép Core khi có cổng chung K1–K5 → bài test cuối 40 phút | AI-18 | Chờ Core |  |
| 6 | Bản 2: công tắc Cloud theo module, qua Mask, đo độ chính xác, kiểm xác suất | AI-21…26 | Chờ (bản 2) |  |
| AI-0 | Khung SDK 2.0, phiếu 2 năng lực, schema chung, cấu hình máy và kiểm độc lập | AI-13 (phần khung) | Xong — 14/11/2026 (tiêu chí riêng AI-0) | Đã kiểm bằng Core giả (CoreGia); pytest 57 passed, 0 skipped; kiểm độc lập mã 0. Cổng DEMO chung chưa đạt. PR: **chờ lead mở** |

## Cần Core (chuyển lead Core qua Anh)

- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

- AI-0 (14/11/2026): vẫn cần kênh `cau_hinh` từ `san-sang` tới hàm năng lực và form cấu hình từ schema theo `_chung/docs/GIAO-CODEX-THU-TU.md` §3. Chưa sửa phiếu/API/SDK đã khóa; tạm đọc JSON ngoài gói bằng `KTT_ENGINE_CAU_HINH`. Không phát sinh điểm chặn Core/SDK mới.

## Bàn giao AI-0 — 14/11/2026

**Kết luận:** Đạt ba tiêu chí riêng AI-0 (phiếu hợp lệ, pytest xanh, kiểm độc lập mã 0). **Cổng DEMO chung theo AGENTS.md §5 chưa đạt** vì hai năng lực còn tạm trả `CHUA_LAM`; không công bố hỏi AI thành công.

**PR:** chờ lead mở. Nhánh: `codex/e_hoi_ai-ai-0`. Không commit/push.

### Đã làm

- Chép khung SDK từ `engine-demo/e_demo_dem_tu` vào `goi/e_hoi_ai/`; thay tên và bỏ nhánh import Core của mẫu. Chỉ 3 tệp Python chạy trong gói (`__init__.py`, `chay.py`, `cau_hinh_may.py`). Phiếu 2.0 phiên bản khung `0.1.0`: đúng hai năng lực, tham số prompt thuộc module, giới hạn 500.000 ký tự/600 giây, 1 việc đồng thời, không khai Cloud.
- Tạo ba schema Draft 2020-12 ở `_chung/contract/`, chép nguyên byte vào gói. Test so SHA-256 từng cặp. Có mô tả `dong`/`tu`/`nghi_ngo` tùy chọn, ô trống/ô gộp, schema trả lời và chuyển tiếp. Kiểm dung lượng UTF-8 32/64 KiB và quan hệ nghiệp vụ thuộc AI-2/các lát kiểm trích dẫn.
- Bộ đọc cấu hình ngoài gói có schema, chấp nhận UTF-8/BOM, không ghi lại cấu hình, thiếu tệp không làm engine chết; cấu hình sai/không đọc được chuyển thành lỗi nghiệp vụ an toàn. Từ chối tệp trong gói, trường lạ, số không hữu hạn, URL chứa thông tin đăng nhập/query/fragment.
- Bộ kiểm độc lập quét toàn bộ `goi/`, từ chối chuỗi Core bị cấm, bytecode, symlink/junction và mục không kiểm được; trả mã 0/1.
- Test sao gói ra ngoài repo, chạy Python `-I -S -B` chỉ thêm đường dẫn SDK cài trong venv và gói sao chép: đọc phiếu, thiếu cấu hình vẫn khởi động, sau đó đọc được cấu hình hợp lệ bằng schema trong gói.
- Không sửa `ma-nguon/`, gói SDK tham chiếu hoặc mã Core. Không chuyển/xóa tệp cũ. Không gọi mạng hay AI thật.

### Kết quả kiểm thật

Môi trường: Windows, Python 3.13.14, `.venv` trong worktree. SDK 2.0.0 cài từ wheel với `--no-index --no-deps`; SHA-256 trùng bản phát hành (`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`). Venv dùng `--system-site-packages` để chạy pytest 9.1.1 đã có sẵn, không tải mạng. Gói chạy chỉ dùng SDK và thư viện chuẩn; test cách ly `-S` không nạp thư viện từ Python hệ thống. Chưa chạy bộ test trên Linux; các phần phụ thuộc symlink/junction được giả lập để test chạy đa nền tảng.

Đã đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; riêng pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát: 1; 0 ví dụ (không có ví dụ [ĐẠT]).

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
.........................................................                [100%]
57 passed in 0.84s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

`Engine.tu_khai_bao` đọc phiếu không lỗi (test riêng). CoreGia kiểm 3 dạng đầu vào của hai năng lực, cả 3 trả `LOI/CHUA_LAM`, không có kết quả. **Đã kiểm bằng Core giả (CoreGia)**; chưa kiểm Core thật hoặc model thật.

QA bổ sung bằng bộ kiểm `jsonschema` có sẵn trên máy phát triển: cả 4 schema hợp lệ Draft 2020-12; ba phong bì DEMO hợp lệ, ca sai phiên bản/loại bị bác. Thư viện này không phải phụ thuộc của gói/bộ pytest lưu trong repo.

### Lệch khỏi phiếu / quyết định tạm

- Theo phạm vi AI-0, giữ hai hàm tạm `CHUA_LAM`; `chay_thu_demo=[]`, nên SDK thu mã 1. Không tạo năng lực phụ hoặc giả kết quả thành công để làm xanh cổng chung. Các ví dụ hỏi AI và bộ chạy Local giả thuộc AI-4 theo phiếu giao.
- Dùng cấu hình JSON ngoài gói theo quyết định tạm của lead; chưa thêm trường cấu hình vào manifest 2.0 đã khóa. Phiên bản khung là `0.1.0`; chưa phát hành bản nghiệp vụ 1.0.0.
- Không có câu Chờ Anh mới phát sinh.

### Thời gian thực tế

Bắt đầu **14/11/2026 22:18** (theo lead); kết thúc kiểm và ghi bàn giao **14/11/2026 22:33:22 +07:00**: **0.26 giờ** (thời gian đồng hồ, gồm đọc tài liệu, dựng gói và kiểm). Ước tính trong phiếu AI-0: **2 giờ**.
