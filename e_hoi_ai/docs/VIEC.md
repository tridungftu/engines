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
| AI-0 | Khung SDK 2.0, phiếu 2 năng lực, schema chung, cấu hình máy và kiểm độc lập | AI-13 (phần khung) | Xong — 14/11/2026 (tiêu chí riêng AI-0) | Đã kiểm bằng Core giả (CoreGia); pytest 57 passed, 0 skipped; kiểm độc lập mã 0. Tại mốc AI-0 cổng DEMO chưa đạt; đã bổ sung ở AI-1. PR: **chờ lead mở** |
| AI-1 | Hỏi tài liệu chỉ Local, khung trích dẫn, hậu kiểm Python, lỗi/thử lại, hủy và chống nộp trùng | AI-1…5, 7, 8 | Xong — 14/11/2026 | Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; SDK thu 1/1 ĐẠT; pytest 141 passed, 0 skipped; kiểm độc lập mã 0; provider Cloud 0 lượt. Chưa chạy thực tế trên Linux/Core thật/model thật. PR: **chờ lead mở** |

## Cần Core (chuyển lead Core qua Anh)

- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

- AI-0 (14/11/2026): vẫn cần kênh `cau_hinh` từ `san-sang` tới hàm năng lực và form cấu hình từ schema theo `_chung/docs/GIAO-CODEX-THU-TU.md` §3. Chưa sửa phiếu/API/SDK đã khóa; tạm đọc JSON ngoài gói bằng `KTT_ENGINE_CAU_HINH`. Không phát sinh điểm chặn Core/SDK mới.
- AI-1 (14/11/2026): vẫn cần cấu hình và nhật ký kỹ thuật chung từ Core. Ghi nợ SDK chung: cho phép engine xác định mã lỗi khi thiếu tham số bắt buộc; áp trần nội dung văn bản bên trong loại riêng. Tạm giữ `prompt.bat_buoc=true` với sentinel `mac_dinh=""` để engine tự trả `THIEU_PROMPT`, và tự kiểm trần 500.000 ký tự cho `van_ban_tai_lieu.van_ban` cùng prompt. Không sửa hợp đồng SDK/API hoặc mã Core; không có điểm chặn mới.

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

## Bàn giao AI-1 — 14/11/2026

**Kết luận:** Đạt lát AI-1 và ba cổng kiểm trên môi trường Windows hiện có. **Đã kiểm bằng Core giả (CoreGia)** và máy Local HTTP giả trên loopback; chưa xác nhận thực tế trên Linux, Core thật hoặc model thật.

**PR:** chờ lead mở. Nhánh: `codex/e_hoi_ai-ai-1`. Tiêu đề đề nghị: `[e_hoi_ai] AI-1 — Hỏi tài liệu, chỉ Local`. Không chạy git commit/push.

### Đã làm

- Dùng lại khung AI-0. Chuyển phần lõi cần dùng từ `ma-nguon/lib/cong_ai.py`, `lib/ai_cuc_bo.py`, `dto.py`, `hoi.py` sang gói độc lập. Đúng 5 tệp Python chạy được thêm/sửa: `chay.py`, `cong_ai.py`, `ai_cuc_bo.py`, `dto.py`, `hoi.py`; không vượt cỡ lát. Gói phiên bản `0.2.0`.
- `ai.hoi_tai_lieu@1` nhận hai loại đầu vào đã khai; prompt thuộc module. Ghép khung bắt buộc trích nguyên văn, lấy câu trả lời từ trích dẫn; không có thông tin thì trả `không thấy căn cứ`.
- Kiểm Python: trích dẫn nằm đúng từng ký tự trong tài liệu, giá trị thuộc trích dẫn tương ứng, token số đầy đủ thuộc nguồn. Một mục không đạt thì hạ toàn bộ `co_can_cu=false`, trả cảnh báo cố định và không đưa câu trả lời bịa vào kết quả. Cảnh báo nằm trong `tra_loi` để giữ nguyên bốn trường đầu ra tĩnh; chỉ giữ câu trích đã kiểm hợp lệ.
- Local HTTP dùng IP trực tiếp, không DNS/proxy/redirect/HTTPS; chỉ loopback/RFC1918/Tailscale. Đích Tailscale phải có nguồn Tailscale và socket được ghim nguồn. Kiểm `/v1/models` cùng metadata Ollama `/api/tags` nếu có trước khi gửi nội dung; từ chối model từ xa/Cloud.
- Lấy URL và timeout từ `cau_hinh_may`; chọn model từ tham số ưu tiên hoặc quy tắc đầu tiên khớp mã prompt. Model thiếu/không sẵn sàng, lỗi mạng/HTTP, timeout, phản hồi hỏng hoặc vượt trần đều trả `LOCAL_AI_KHONG_SAN_SANG`, có thể thử lại. Chưa làm discovery/dự phòng thuộc AI-3.
- Báo tiến độ trước/sau Local, kiểm hủy trước mạng và giữa các lần đọc metadata. Lượt hủy không nộp kết quả. SDK xử lý mất xác nhận kết quả bằng cùng Idempotency-Key, không gọi AI lại, Core chỉ ghi một lần.
- Mỗi lượt ghi stderr đúng sáu metadata: mã/phiên bản prompt, model, lý do chọn, ms, kết quả kiểm; không ghi prompt, tài liệu, câu trả lời, URL hoặc nội dung lỗi nguồn.
- Test dùng Local HTTP giả trên `127.0.0.1`, CoreGia, provider Cloud giả có bộ đếm và hàng rào mạng: cấm DNS và mọi kết nối ngoài loopback. Các đường thành công, thiếu căn cứ, bịa dẫn chứng/số liệu, thiếu prompt, Local tắt/lỗi/model thiếu, hủy, gửi lại xác nhận đều có **0 lượt Cloud**.
- Ghi nguồn cũ → mới và SHA-256 trong `NGUON.md`; cập nhật README, CHANGELOG và phiếu DEMO tối thiểu. Chỉ SDK và thư viện chuẩn, không thêm dependency.

### Kết quả kiểm thật

Môi trường: Windows x64, Python 3.13.14, `.venv` trong worktree; SDK **2.0.0** cài bằng `--no-index --no-deps` từ wheel trong repo. SHA-256 wheel trùng `SHA256SUMS.txt`: `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Venv dùng `--system-site-packages` để dùng pytest 9.1.1 sẵn có; không tải mạng.

Đã đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
Chạy: python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
Engine e_hoi_ai 0.2.0: mọi ví dụ chạy thử DEMO đều đạt.
[ĐẠT] Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; 1 lượt Local.
Mã thoát: 0; SDK thu 1/1 ĐẠT.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
........................................................................ [ 51%]
.....................................................................    [100%]
141 passed in 5.11s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

Lệnh SDK được gọi thật trong tiến trình con với cấu hình DEMO ngoài gói và Local HTTP giả đang chạy; không đổi handler engine thành hàm giả. Các test hủy xác nhận `HUY` và không có kết quả; test `gay_mat_xac_nhan("ket_qua")` xác nhận hai lần gửi cùng khóa, **một lần ghi kết quả**, **một lần gọi Local**.

Giới hạn môi trường: không có WSL/Linux, Docker hoặc Podman; Git Bash không phải Linux. Bộ test không dùng API chỉ dành riêng Windows ở đường Local, nhưng **chưa chạy thực tế trên Linux**. Không chạy model/Local thật hoặc Core thật.

### Lệch khỏi phiếu / quyết định tạm đã dùng

- Đưa lên trước từ AI-4 **một ví dụ DEMO và bộ chạy Local giả tối thiểu** để cổng SDK thu có ca thật chạy và mã thoát 0 ngay ở AI-1. AI-4 vẫn làm bộ DEMO đầy đủ, HTTP Core giả và các phần còn lại theo phiếu.
- `prompt` có sentinel mặc định rỗng để SDK không chặn trường hợp thiếu bằng mã lỗi chung. Engine vẫn bắt buộc có nội dung prompt; không có prompt nghiệp vụ mặc định.
- Giữ và siết phép kiểm giá trị thuộc câu trích của mã cũ: không chấp nhận diễn giải ngoài nguyên văn. Đây là kiểm bằng quy tắc bảo thủ, chưa chứng minh suy luận ngữ nghĩa; câu đúng nhưng diễn đạt lại có thể bị hạ.
- Hủy giữa HTTP không cưỡng bức cắt socket đang chờ; SDK tiếp tục gia hạn/nhận cờ hủy, engine bỏ kết quả khi HTTP trả về hoặc hết timeout. Không chuyển Cloud.
- `ai.hoi_theo_yeu_cau@1` vẫn `CHUA_LAM`, đúng phạm vi AI-2. Chọn dự phòng/tự phát hiện model thuộc AI-3.
- Mã cũ `ma-nguon/chay.py`, `bi_mat.py`, phần Mask/Cloud/cấu hình Core cũ và chức năng chọn đối tác không đưa sang AI-1; giữ nguyên để lead quyết định chuyển `LUU-TRU/` sau các lát liên quan. Không sửa/xóa mã nguồn cũ, schema chung, tài liệu SDK hoặc mã Core.
- Cần Core/SDK đã ghi ở mục trên; không có câu Chờ Anh mới phát sinh. PR: **chờ lead mở**.

### Thời gian thực tế

Bắt đầu **14/11/2026 22:34** (theo lead); kết thúc kiểm và ghi bàn giao **14/11/2026 22:53:49 +07:00**: **0.33 giờ** (thời gian đồng hồ, gồm đọc tài liệu, chuyển lõi, test và bàn giao). Ước tính trong phiếu AI-1: **5 giờ**.
