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

## DONG-GOI-1 — 15/11/2026

- Trạng thái: **đã làm xong công cụ/hướng dẫn phần chung; chưa đạt toàn bộ
  gate nghiệm thu 4 engine** vì CLI AI/TX còn lỗi; xem kết quả kiểm mới cuối mục.
  PR: **chờ lead mở**; nhánh `codex/_chung-dong-goi-1`.
- Chỉ sửa phần chung và `.gitignore`; không sửa mã/tài liệu/lock/kiểm kê của
  engine, không sửa Core/SDK, không chạy `git commit`/push trong worktree.
- Công cụ: [`../cong-cu/dong_goi.py`](../cong-cu/dong_goi.py), chỉ thư viện
  chuẩn; [`../cong-cu/tests/test_dong_goi.py`](../cong-cu/tests/test_dong_goi.py).
  Hướng dẫn: [`HUONG-DAN-CAI-NGHIEM-THU.md`](HUONG-DAN-CAI-NGHIEM-THU.md).
- Đọc tên/mode bằng `git ls-tree -rz`, lấy bytes bằng `git cat-file blob`
  (tương đương `git show <commit>:<path>`), chốt một commit duy nhất.
  Không đọc working tree để đóng gói hoặc kiểm kê; không chuẩn hóa CRLF.
- ZIP_STORED, tên sắp xếp, timestamp 01/01/1980, quyền 0644; mỗi ZIP chỉ
  một thư mục mã engine. Có allowlist, cấm tệp/thư mục nhạy cảm, bytecode,
  liên kết/submodule, kiểm kê sai/thiếu/thừa/trùng; kiểm hết trước khi ghi.
  Tạo wheel SDK đã kiểm SHA, SHA256SUMS và DANH-SACH-GOI có commit/năng lực/ngăn.
- Hướng dẫn có kiểm SDK, cài phụ thuộc OCR theo hash, Xem trước gói/Duyệt cài/Bật,
  trường cấu hình theo schema, bảng BẤM/ảnh của từng engine, kiểm restart,
  giới hạn Core/SDK và bước `.cmd` do lead thực hiện. Lead đã bấm thử luồng cài CĐ-36; chưa nghiệm thu đầy đủ Core thật.

### Bộ giao chạy thử và SHA-256 — lịch sử trước PR #94

Đã chạy đúng lệnh Anh giao, mã thoát **0**:

```powershell
python _chung/cong-cu/dong_goi.py --engine e_hoa_don --engine e_hoi_ai --engine e_ocr --engine e_trich_xuat --ra .dong-goi-thu --nhan thu
```

Python thực tế là `.venv\Scripts\python`, SDK **2.2.0**. Mốc nguồn
`12ed8dbfcb3a60cab02cbb7e1833997e23f27d77`; nhãn `thu`. Bộ artifact nằm
trong `.dong-goi-thu/`, được `.gitignore` bỏ qua, **không đưa vào commit**.
Manifest engine là nguồn phiên bản (README Hỏi AI còn tiêu đề lịch sử 0.11.0).

| Tệp | SHA-256 nguyên bytes |
|---|---|
| `e_hoa_don-1.0.0.zip` | `16de773cbf59b3a3fd6b506b52de9888100b564cddcf500da74851a90096ed99` |
| `e_hoi_ai-0.12.0.zip` | `e042d9968f1436959d8744ba0d8cbfa6a5aa50da7f6420b2903f977489a38761` |
| `e_ocr-1.0.9.zip` | `dcbc7dff42efe6a8d1342851353430843e12f7babad3825b7d45921ca247a586` |
| `e_trich_xuat-0.5.0.zip` | `f6815dbf9bb711dc367ebb6e5c021540f5e7029d694610358ffe9a6a39616730` |
| `kho_tri_thuc_sdk-2.2.0-py3-none-any.whl` | `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` |

Đóng bộ thật **hai lần** (lần hai ra thư mục DEMO tạm ngoài repo): cả bốn
ZIP, wheel, SHA256SUMS và DANH-SACH-GOI **trùng từng byte**. Đã mở lại
từng ZIP, kiểm CRC và đối chiếu **mọi tệp** với `git show` tại commit trên:
Hóa đơn **20**, Hỏi AI **28**, OCR **44**, Trích xuất **27** tệp, không thừa/thiếu.
Kiểm kê SQL Hỏi AI/OCR khớp toàn bộ bytes/SHA từ git trước đóng.

### Kết quả kiểm thật trước PR #94 — các lệnh §5

Môi trường Windows, Python **3.13.14**, venv `.venv` trong worktree với
`--system-site-packages` để dùng dependency/pytest đã có, không tải mạng.
SDK cài `pip install --no-index --no-deps` từ wheel repo; phiên bản in **2.2.0**,
SHA wheel trên đĩa và trong git khớp bảng phát hành. Không nhận đây là kiểm
máy sạch/venv hoàn toàn biệt lập. Các lệnh đặt `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONUTF8=1`. Không có bytecode trong các gói sau kiểm.

Chạy đủ ba nhóm lệnh cho **từng engine**, dùng đúng Python trong venv:

```powershell
python -m kho_tri_thuc_sdk.thu <engine>/goi/<ma>
python -m pytest <engine>/tests -q --basetemp=.pytest-tmp-<engine>
python <engine>/tests/kiem_doc_lap.py
```

| Engine | CLI gói nguồn | CLI ZIP giải nén | Pytest nguồn | Kiểm độc lập |
|---|---|---|---|---|
| Hóa đơn | **4/4 ĐẠT**, exit 0 | **4/4 ĐẠT**, exit 0 | **654 passed, 0 skipped**, 221,52 giây, exit 0 | ĐẠT, exit 0 |
| Hỏi AI | **0/3**, exit 1: `CHUA_CAU_HINH` | **0/3**, cùng lỗi, exit 1 | **637 passed, 0 skipped**, 380,60 giây, exit 0 | ĐẠT, exit 0 |
| OCR | **6/6 ĐẠT**, exit 0 | **6/6 ĐẠT**, exit 0 | Lượt đầu **293 passed, 1 failed, 0 skipped**, 154,49 giây; lượt lặp **293 passed, 1 failed, 0 skipped**, 105,12 giây; đều exit 1 | ĐẠT, exit 0 |
| Trích xuất | **4/5**, exit 1: C-TX-06 `DANG_CHAY` | **4/5**, cùng lỗi, exit 1 | **485 passed, 1 failed, 0 skipped**, 101,63 giây, exit 1 | ĐẠT, exit 0 |

CLI tổng **14/18 ĐẠT** trên gói nguồn và **14/18 ĐẠT** trên ZIP giải nén.
OCR dùng Tesseract đã có trên máy kiểm; không chạy ABBYY thật. Toàn bộ đường
Core trong bảng **đã kiểm bằng Core giả (CoreGia)**; chưa kiểm Core thật,
ngăn ghi bền/restart, trình duyệt, model Local thật hoặc Linux.

Test công cụ đóng gói:

```powershell
python -m pytest _chung/cong-cu/tests/test_dong_goi.py -q --basetemp=.pytest-tmp-dong-goi-2
# 31 passed, 0 skipped, 93,26 giây, exit 0 (trước khi thêm ca CLI tiếng Việt)
python -m pytest _chung/cong-cu/tests/test_dong_goi.py -q -k tham_so_sai --basetemp=.pytest-tmp-dong-goi-cli
# 1 passed, 31 deselected, 0,07 giây, exit 0
```

**32 ca đóng gói/CLI đã được kiểm**, không skip. Có ca git DEMO biệt lập
kiểm LF/CRLF, working tree bẩn, wheel bẩn, ref cũ, SHA wheel sai, kiểm kê
sai bytes/SHA/tập tệp/phiên bản, tệp cấm, symlink, đầu ra, không phát hành
một phần. Kho git fixture dùng `commit-tree`/`update-ref` chỉ trong thư mục
test tạm, không ghi lịch sử worktree. Quét AST công cụ: chỉ stdlib.
`git diff --check` không lỗi; diff bốn thư mục engine và Core/SDK rỗng.

### Lỗi lượt kiểm cũ và tình trạng xử lý

1. OCR lượt đầu:
   `test_ocr_2.py::test_abbyy_da_tra_thieu_chu_khong_chuyen` lỗi ở fixture
   `ABBYYGia.__exit__`, `PermissionError(13, 'Permission denied')`;
   riêng ca đó chạy lại **1 passed** trong 1,34 giây. Lượt toàn bộ thứ hai
   lại lỗi fixture này ở
   `test_ocr_4.py::test_app_moi_giao_lai_va_tra_muon_cung_ma_khong_gui_lai[ocr.doc_van_ban@1]`,
   đồng thời có `XONG` thay vì `CHUA_RO`. Có dấu hiệu nhạy thời điểm/khóa
   file trên Windows, **chưa kết luận nguyên nhân gốc**; không bỏ ca hoặc
   đổi thành đạt vì một lần chạy riêng xanh. Không chạy lặp để lựa kết quả.
2. **Đã xử lý tại PR #94:** TX `test_nguon_tx6.py::test_cac_bam_trong_nguon_khop_tai_nguyen_thuc`
   dừng ở SHA tham chiếu `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/hoi_yeu_cau.py`:
   NGUON TX giữ `4130ccaf…`, mã hiện tại là `3162ba60…` (LF).
   Lead đã cập nhật băm nguồn; công cụ đóng gói không sửa nguồn hoặc bỏ kiểm tra này.
3. **Đã xử lý theo quyết định lead:** Hỏi AI, Trích xuất, Hóa đơn dùng SDK
   2.2.0 và dependency SDK đã có trong Python Core; chỉ kiểm phiên bản SDK.
   OCR có dependency riêng có hash, vẫn cài lock với `--require-hashes --no-deps`.

Bổ sung từ lead: test OCR “ABBYY giả Windows” trên worktree sạch **294 passed**;
lỗi kiểm kê ở checkout cũ do CRLF đã tồn tại trước `.gitattributes`, là vấn đề
môi trường checkout, không phải lỗi gói: công cụ đóng gói lấy bytes từ git.
TX đã được lead sửa băm và gộp PR #94. Kết quả cũ phía trên là lịch sử.


### Cần Core — DONG-GOI-1 hiện hành

Các mục NGAN-0 phía trên là lịch sử SDK 2.0.0; SDK 2.2.0 đã có ngăn và cấu
hình. Các điểm vẫn mở cho bộ giao này:

1. Cấp cấu hình/fixture nguồn ngoài cho CLI `chay_thu_demo`: Hỏi AI hiện
   nhận `CHUA_CAU_HINH`, không được thay CLI chuẩn bằng cổng giả khác.
2. C-TX-06: cấp tệp DEMO được tham chiếu lồng trong `tra_loi_ai` cho hậu
   kiểm TX; không sửa ID giả để ép xanh. DEMO XLSX Hóa đơn lồng `truong`
   cũng cần cổng fixture hoặc quy trình Core để nghiệm thu qua màn.
3. Kiểu ngăn `json`: hiện AI/OCR dùng JSON text `van_ban` ≤64 KiB theo
   giới hạn SDK; chưa tự đổi schema hoặc kiểu cột.
4. `giao_dien_quan_tri`: SDK chưa nhận khóa manifest. Lead Core cần
   review/nạp màn cấu hình ba engine qua `KttCore.engine(ma)`, quyền Admin,
   lifecycle UI và thống nhất dạng trả `cau_hinh.doc()` (AI đọc `cau_hinh`,
   OCR/TX đọc `gia_tri`). Không có màn thì ca cấu hình/restart còn chờ.
5. Lead/Anh nghiệm thu ngăn thật sau restart theo bảng ảnh trong hướng dẫn;
   kết quả CoreGia không chứng minh lưu bền/ACL hoặc nguồn ABBYY thật.

### Báo cáo §6 — lượt trước

Kết luận: **Chưa đạt** — công cụ/hướng dẫn phần chung đã kiểm đạt; bốn engine
chưa qua toàn bộ gate CLI/pytest hiện hữu, chưa nghiệm thu Core thật.
Đã làm: công cụ bytes git/ZIP tất định/kiểm kê/SHA/danh sách; hướng dẫn cài
và BẤM nghiệm thu; 32 ca test đã kiểm; đủ 4 ZIP bỏ qua gitignore.
Kết quả kiểm: SDK CLI nguồn và ZIP đều **14/18 ĐẠT**; pytest HD **654 passed**,
AI **637 passed**, OCR **293 passed/1 failed** (cả hai lượt), TX **485 passed/1 failed**;
**0 skipped**; bốn kiểm độc lập exit 0. Đã kiểm bằng Core giả (CoreGia).
Thời gian thực tế: **15/11/2026 17:43–18:03 (UTC+07)**, khoảng **0,34 giờ**;
phiếu giao DONG-GOI-1 **không nêu giờ ước tính riêng**.
Lệch khỏi phiếu / quyết định tạm: thêm `--ref` chọn mốc, mặc định HEAD;
`--nhan` giữ nhãn bộ giao. Cho riêng `.dong-goi-thu` trong repo để thực hiện
đúng lệnh Anh giao, mọi đầu ra khác phải ngoài repo. Không sửa engine để
che lỗi kiểm, không commit/push; venv dùng dependency có sẵn như đã nêu.
Cần Core / Chờ Anh mới phát sinh: các mục Core/lead phía trên; không có
quyết định nghiệp vụ mới cần Anh duyệt. Máy thật/ảnh/restart do lead và Anh
thực hiện theo hướng dẫn.

### Cập nhật DONG-GOI-1 theo CĐ-36 — 15/11/2026

Trạng thái: đã cập nhật hướng dẫn; nghiệm thu toàn bộ còn phụ thuộc kết quả kiểm
và Core thật. PR: **chờ lead mở**. Core main `0ebd632` đã được lead bấm thử:
Xem trước gói → Duyệt cài → tự cài ngăn C4 → tải lại màn → Bật. Lead soạn
và chạy `.cmd` khóa `tien_trinh_cai.thu_muc_engine` trước lần đầu cài engine
có ngăn trên Core tổng. Nợ Core: tải lại màn mới thấy nút Bật.

Bộ ZIP mới đóng từ `origin/main` tại commit `312e24589de9977ff8f6e4eeff5eda96b5ec795b`:

| ZIP | SHA-256 |
|---|---|
| `e_hoa_don-1.0.0.zip` | `16de773cbf59b3a3fd6b506b52de9888100b564cddcf500da74851a90096ed99` |
| `e_hoi_ai-0.12.0.zip` | `e042d9968f1436959d8744ba0d8cbfa6a5aa50da7f6420b2903f977489a38761` |
| `e_ocr-1.0.9.zip` | `dcbc7dff42efe6a8d1342851353430843e12f7babad3825b7d45921ca247a586` |
| `e_trich_xuat-0.5.0.zip` | `cbd8117ce5690bc7cf7d061f694ce89e1089dc051516b376cfaca083488d40bb` |


Kiểm lại ngày 15/11/2026, Python `.venv\Scripts\python` (SDK 2.2.0),
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; pytest dùng `--basetemp` riêng.
Bộ giao ở thư mục tạm `dong-goi-20261115-1814`, không đưa vào git.

| Engine | SDK CLI nguồn | SDK CLI ZIP giải nén | pytest | Kiểm độc lập |
|---|---|---|---|---|
| Hóa đơn | 4/4 ĐẠT, exit 0 | 4/4 ĐẠT, exit 0 | 654 passed, 0 skipped, exit 0 | ĐẠT, exit 0 |
| Hỏi AI | 0/3, exit 1: `CHUA_CAU_HINH` | 0/3, cùng lỗi, exit 1 | 637 passed, 0 skipped, exit 0 | ĐẠT, exit 0 |
| OCR | 6/6 ĐẠT, exit 0 | 6/6 ĐẠT, exit 0 | 294 passed, 0 skipped, exit 0 | ĐẠT, exit 0 |
| Trích xuất | 4/5, exit 1: C-TX-06 `DANG_CHAY` | 4/5, cùng lỗi, exit 1 | 486 passed, 0 skipped, exit 0 | ĐẠT, exit 0 |

SDK CLI tổng 14/18 ĐẠT ở cả nguồn và ZIP. **Đã kiểm bằng Core giả (CoreGia)**;
chưa nghiệm thu toàn bộ trên Core thật. OCR không chạy ABBYY thật. `git diff
--check` đạt. Cần Core vẫn là fixture/cấu hình CLI AI và fixture lồng C-TX-06
nêu ở trên, cùng lỗi giao diện phải tải lại để thấy nút Bật.

Báo cáo §6: **Chưa đạt** toàn bộ gate do CLI AI/TX; đã cập nhật luồng cài,
phụ thuộc, ghi nhận kiểm tra OCR của lead và đóng lại 4 ZIP từ `origin/main`.
Thời gian lượt này: **18:14–18:20 ngày 15/11/2026 (UTC+07), khoảng 0,10 giờ**;
phiếu không nêu ước tính riêng. Không sửa engine/Core/SDK, không commit/push;
không phát sinh quyết định nghiệp vụ chờ Anh.
