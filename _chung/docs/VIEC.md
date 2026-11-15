# Việc phần chung

## NGAN-0 — 15/11/2026

- Trạng thái: **đã sửa V1–V4 theo kiểm độc lập của lead, đạt kiểm mẫu RAM và
  hợp đồng cục bộ ngày 15/11/2026; PR: chờ lead mở**.
- Nhánh: `codex/_chung-ngan-0`. Không sửa engine, không commit/push.
- Hai tệp mã: `../mau-ma/ngan.py`, `../mau-ma/cau_hinh.py`.
  Hướng dẫn chép, so băm và trạng thái: `../mau-ma/README.md`.
- Lượt sửa chỉ đổi runtime `ngan.py`, bổ sung `tests/test_sua_ngan_0.py` và tài liệu;
  giữ `cau_hinh.py` nguyên trạng. API cuối cùng liệt kê ở README, mục
  “API cuối cùng cho AI-8 / OCR-8 / MASK-3b”.
- Đã làm: giao diện `Ngan`/`LoNgan`, `NganBoNho` khóa luồng, chọn ngăn SDK/RAM,
  lô nguyên tử tối đa 100 lệnh, CAS, khóa duy nhất, lấy hoặc tạo đồng thời,
  phân trang tối đa 500 bản và view pháp nhân dùng cùng RAM. Cấu hình lấy từ ngăn,
  kiểm tập con JSON Schema, điền mặc định trên bản sao, thiếu bản ghi trả `None`.
- Lượt đầu theo giao việc: **15/11/2026 07:29**, hoàn tất kiểm và bàn giao **07:42**
  (UTC+07), khoảng **0,22 giờ**; ước tính lead trong phiếu: **2 giờ**.

### Sửa theo kiểm độc lập V1–V4 — 15/11/2026

- V1: bảng pháp nhân chạy trực tiếp trên ngăn gốc, lấy phạm vi từ `phap_nhan_id`
  trong `khoa/loc` của từng lệnh; thiếu/sai chuỗi thì `NganKhongHopLe`. Kiểm cả
  `lay_hoac_tao`, `doc`, `tim`, `sua`, `xoa` và một lô nhiều pháp nhân/bảng engine.
- V2: view P từ chối pháp nhân khác P trong khóa/bộ lọc/giá trị và từ chối tạo
  view Q; vẫn cho tạo view P. Giữ đường tắt không truyền lại pháp nhân.
- V3: chỉ mục primary và từng unique theo bảng/pháp nhân. Overlay dữ liệu và
  chỉ mục của lô chỉ được áp sau khi mọi lệnh đạt, dưới cùng RLock. Không
  deepcopy toàn kho; bản sao đầu vào/đầu ra và ngữ nghĩa CAS vẫn được giữ.
  Kiểm rollback chỉ mục, sửa unique, xóa/tạo lại trong cùng lô.
- V4: JSON và khóa chứa surrogate lẻ bị từ chối bằng `NganKhongHopLe`, kể cả tên
  thuộc tính lồng nhau. So sánh JSON thống nhất cho khóa/unique/lọc: `1 == 1.0`,
  bool khác số; `None` trong unique coi là trùng.
- README nêu đủ quy ước unique/JSON, app `__slots__`, schema gốc nên có
  `additionalProperties: false`, cách lấy `row_version` cấu hình khi cần CAS.
  Kiểm độc lập được gọi từ test để pytest thu thập, vẫn giữ script chạy riêng.
- Bắt đầu lượt sửa: **15/11/2026 07:47**; kết thúc **07:53** (UTC+07), khoảng
  **0,10 giờ**. Phiếu NGAN-0 ước tính **2 giờ**, không có ước tính riêng cho lượt sửa.

### Kết quả kiểm thật

Môi trường Windows, Python 3.13.14, `.venv` trong worktree. SDK cài bằng
`pip install --no-index --no-deps` từ wheel repo; phiên bản in ra `2.0.0`.
SHA-256 wheel:
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`,
khớp `SHA256SUMS.txt`. Pytest 9.1.1 có sẵn qua `--system-site-packages`;
không tải mạng, hai tệp runtime không có dependency ngoài thư viện chuẩn.

Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` cho các lệnh dưới.

| Lệnh (Python = `.venv/Scripts/python`) | Kết quả |
|---|---|
| `python -m pytest _chung/mau-ma/tests -q --basetemp=.pytest-tmp` | **182 passed, 0 skipped** trong 0,82 giây, mã thoát 0 |
| `python -m pytest _chung/mau-ma/tests -q -k dong_thoi --basetemp=.pytest-dong-thoi` | **20/20 lượt liên tiếp đạt**, mỗi lượt **3 passed**; 60 lần chạy ca, 0 lỗi. Gồm ca 8 luồng × 50 vòng cùng khóa, chỉ tạo 1 bản |
| `python -m pytest _chung/mau-ma/tests/test_sua_ngan_0.py -q -s -k hieu_nang --basetemp=.pytest-hieu-nang` | **1 passed**, 69 deselected; 3000 `them` đơn lẻ + 200 `lay_hoac_tao` tại 3000 hàng: **0,311 giây < 2 giây**. Ca cũng chạy mặc định trong bộ 182 test |
| `python _chung/mau-ma/tests/kiem_doc_lap.py` | **[ĐẠT]** chỉ thư viện chuẩn; không `__pycache__`, `.pyc`, symlink; mã thoát 0 |
| `python -m kho_tri_thuc_sdk.thu docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_doc_tep` | **1/1 ĐẠT**, mã thoát 0 |
| `python -m kho_tri_thuc_sdk.thu docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_chu_hoa` | **1/1 ĐẠT**, mã thoát 0 |
| `python -m kho_tri_thuc_sdk.thu docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_dem_tu` | **2/2 ĐẠT**, mã thoát 0 |
| `git diff --check` | Không lỗi khoảng trắng |

SDK DEMO **đã kiểm bằng Core giả (CoreGia)**. Hợp đồng ngăn được kiểm trực tiếp
trên `NganBoNho`; CoreGia/MayChuGia SDK 2.0 chưa có API ngăn. Chưa kiểm ngăn Core
thật hoặc chạy thực tế trên Linux; test chỉ dùng API Python đa nền tảng.

### Lệch khỏi phiếu / quy ước tạm

- Lát chung không có `goi/<ma>` hay manifest engine; nhóm kiểm §5 được áp dụng
  bằng pytest và kiểm độc lập của mẫu chung, cùng ba engine DEMO có sẵn của SDK
  để kiểm nền SDK. Không tạo engine hay sửa các engine khác trong lát này.
- Giữ API `doc/tim/lo` theo đề nghị; các chi tiết chưa được đề nghị chốt
  (constructor, view pháp nhân, kiểu trang/kết quả, khóa cấu hình) được ghi rõ
  trong README, cần đối chiếu SDK 2.1 trước khi dùng ngăn thật.

## Cần Core

1. SDK 2.1 cung cấp `app.ngan`/`viec.ngan`, lô nguyên tử, CAS, unique, idempotency,
   ràng buộc pháp nhân từ ngữ cảnh tin cậy và ngoại lệ `NganXungDot` theo đề nghị.
   Bản RAM không thay kiểm quyền của Core, không có dữ liệu lưu bền.
2. Chốt constructor/khai báo bảng, kiểu kết quả `tim` và kết quả từng lệnh trong
   `lo()`. Bản tạm dùng `TrangNgan(danh_sach, tiep)` và kết quả chờ commit, có
   `ban_ghi/gia_tri/row_version/da_tao`; `sua` là bản vá. Chốt ảnh trả khi xóa.
3. Chốt bản ghi cấu hình hệ thống: hiện dùng bảng `cau_hinh`, khóa `{}`, giá trị
   trực tiếp. Cần nối cấu hình từ `san-sang`, snapshot theo việc, phiên bản CAS
   và sự kiện `engine.cau_hinh_doi`; không giả các chức năng này ở bản RAM.
4. CoreGia/MayChuGia thêm ngăn, móc gây xung đột và xem ngăn để đưa factory vào
   cùng bộ test hợp đồng. Hiện chỉ factory `NganBoNho` được chạy, chưa có adapter
   hoặc HTTP ngăn SDK 2.1 để kiểm tương thích thực tế.
5. TTL/retention, giới hạn kiểu cột JSON 64 KiB, migration, sao lưu, kiểm toán,
   giao thức HTTP và ghi bền thuộc Core/SDK, chưa thực hiện trong mẫu NGAN-0.
6. Đối chiếu SDK 2.1 với API cuối trong README: nhận `phap_nhan_id` theo từng
   `khoa/loc` trên ngăn gốc, view không cho đổi pháp nhân, cùng quy ước JSON/NULL
   của unique. Đây là chi tiết tương thích cần chốt; Core vẫn phải ràng buộc
   pháp nhân theo ngữ cảnh tin cậy, không coi ID do engine gửi là phân quyền.

Không phát sinh câu hỏi chờ Anh ngoài các điểm SDK/Core đã nêu.
