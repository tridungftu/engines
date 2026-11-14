# VIỆC — danh sách việc duy nhất của project `e_ocr`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc tài liệu cổng và engine; nhận kế hoạch các lát theo `GIAO-CODEX-e_ocr.md` | — | Xong 14/11/2026 | Thực hiện OCR-0 theo phiếu Anh giao; ước tính 2 giờ |
| OCR-0 | Khung SDK 2.0, cấu hình máy, kho tạm, schema chung và kiểm độc lập | OCR-6 | Xong 14/11/2026 | PR: **chờ lead mở**. Đã đạt tiêu chí riêng của OCR-0; kết quả DEMO chung và giới hạn xem bên dưới |
| OCR-1 | Đọc lớp chữ PDF và ABBYY Hot Folder cục bộ; hai action đọc dùng chung lõi | OCR-2, 3, 4, 7, 15 | Xong 14/11/2026 | PR: **chờ lead mở**. SDK DEMO 2/2, pytest 119 passed, 0 skipped, kiểm độc lập đạt; đã kiểm bằng Core giả (CoreGia), chi tiết bên dưới |
| OCR-3 | Xuất Word từ cấu trúc tài liệu, giữ ô trống/ô gộp, vị trí bảng và thứ tự trang | OCR-4, 5 | Xong 14/11/2026 | PR: **chờ lead mở**. SDK DEMO 3/3, pytest 145 passed, 0 skipped, kiểm độc lập đạt; đã kiểm bằng Core giả (CoreGia), chi tiết bên dưới |
| 1 | Đóng gói độc lập theo cổng chung; thay hàm SDK riêng `ocr_*_luot` bằng lượt bền chung khi Core có | OCR-6, 13 | Đang làm 14/11/2026 | Có khung OCR-0; chuyển lõi ở OCR-1…OCR-4, không sửa `ma-nguon/` |
| 2 | Bổ sung dependency cho nguồn dự phòng mask_ocr | OCR-8 | Chờ làm |  |
| 3 | Màn hạn mức ABBYY / trạng thái máy (giao diện của engine) | OCR-8 | Chờ làm |  |
| 4 | Bài máy test ca 1, 3, 8 | OCR-11 | Chờ làm |  |
| 5 | Lát 9: ABBYY thật trên máy hiện tại bằng PDF DEMO (Anh đã cho phép mở kết nối tạm) | OCR-12 | Chờ làm | Không chép `in\ out\ jobs\ state\` |
| 6 | Ghép Core (K1–K6) → nghiệm thu tổng thể | — | Chờ Core |  |

## Cần Core (chuyển lead Core qua Anh)
- Theo SDK 2.0.0 và `GIAO-CODEX-THU-TU.md` §3: đưa cấu hình từ `san-sang` tới engine, kèm schema để Core dựng form. Tạm đọc JSON ngoài gói bằng `KTT_ENGINE_CAU_HINH`.
- Ngăn dữ liệu engine: ghi theo lô nguyên tử, CAS/`row_version`, ràng buộc duy nhất/lấy hoặc tạo. Tạm dùng `KTT_ENGINE_DU_LIEU`; `doc` và `ghi` là các thao tác riêng lẻ, không có giao dịch đọc–sửa nhiều lời gọi.
- Lượt bền chung #10 giữ/chốt/đọc (đợt 2): thay phần lưu lượt tạm ở OCR-4 khi Core có. Không dùng hàm `ocr_*_luot` cũ.
- Bí mật theo tên, nhật ký kỹ thuật và thẻ trạng thái chung để thay phần trạng thái/hạn mức ABBYY; đợt 1 không làm giao diện riêng hay cầu nối có khóa.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).
- OCR-3 không phát sinh thiếu hụt Core/SDK: tải DOCX ra bằng API chung `viec.tai_tep_ra`, không cần kênh ACK hoặc sổ bàn giao riêng.

## Bằng chứng OCR-0 — 14/11/2026

- Nhánh: `codex/e_ocr-ocr-0`; PR: **chờ lead mở**. Lead commit và mở PR.
- Thời gian thực tế: **14/11/2026, 22:18–22:38** (20 phút, khoảng **0,33 giờ**),
  so với **2 giờ ước tính** trong phiếu; giờ Việt Nam.
- Gói mới: `goi/e_ocr/`, bốn tệp mã Python; chỉ thư viện chuẩn + SDK 2.0.0.
  Không sửa mã cũ hoặc tài liệu SDK/Core. Hàm tạm của cả ba năng lực trả
  `LoiNghiepVu("CHUA_LAM", ...)`, không nộp kết quả giả.
- Schema `van_ban_tai_lieu` được tạo theo `LOAI-DU-LIEU-RIENG.md` §2.1 và
  chép nguyên tệp vào gói; test so SHA-256. Khi gộp với AI-0, lead chọn một
  bản chung và chép nguyên byte vào các gói trước khi chạy lại test so băm.
- Cấu hình máy và dữ liệu tạm đều ngoài gói, không chứa bí mật/nội dung tài
  liệu. Khóa thật bằng `msvcrt`/`fcntl`; test hai tiến trình `spawn` đồng thời,
  giữ khóa, hết hạn khóa, lỗi thay tệp, kho hỏng, khởi tạo lại và từ chối bytes.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows x64, Python 3.13.14.
  Chưa chạy Linux, Core thật hoặc nguồn OCR thật. Test không phụ thuộc Windows
  API ngoài nhánh khóa tệp chuẩn; dùng `spawn` trên cả hai nền tảng.
- SDK cài offline trong `.venv`, phiên bản `2.0.0`; băm wheel khớp
  `SHA256SUMS.txt`. `.venv` dùng `--system-site-packages` để dùng pytest có sẵn,
  không tải thêm thư viện; chưa phải bài cài máy sạch của OCR-6.

### Kết quả ba lệnh bắt buộc

Đầu ra thực tế lượt kiểm cuối; đã đặt `PYTHONDONTWRITEBYTECODE=1` và
`PYTHONUTF8=1`, không phát sinh bytecode trong gói:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát: 1; chưa có ví dụ (0/0), chưa đạt kiểm DEMO chung.

> .venv\Scripts\python -m pytest e_ocr/tests -q
........................................................................ [ 86%]
...........                                                              [100%]
83 passed in 5.88s
Mã thoát: 0; 0 skipped.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát: 0.
```

Kiểm bổ sung: `tu_khai_bao: e_ocr 3`; kiểm schema draft 2020-12 và các mẫu
DEMO hợp lệ bằng công cụ `jsonschema` có sẵn trong môi trường (không là
dependency của engine). So băm nguồn gói theo `NGUON.md`; `git diff --check`
không báo lỗi. Mã schema chung:
`f3756741eea1e5c9c9451b8a8df8a5416817f04adffe4bf1b44c24b19c3e7f93`.

### Quyết định tạm và phần còn lại

- `chay_thu_demo` rỗng tới OCR-5. SDK 2.0.0 coi phiếu không có ví dụ là mã
  thoát 1; CLI chỉ chấp nhận ví dụ kết thúc `XONG`. Vì OCR-0 bắt buộc hàm tạm
  `CHUA_LAM`, **chưa đạt điều kiện DEMO chung AGENTS.md §5**. Tiêu chí riêng
  OCR-0 vẫn là `tu_khai_bao` không lỗi, pytest xanh, kiểm độc lập mã 0.
- Giới hạn lớp bọc tạm: cấu hình/giá trị kho 64 KiB, toàn kho 8 MiB; chuỗi mã
  ASCII tối đa 200 ký tự, độ sâu 16, vượt trần thì từ chối. Không CAS nhiều
  lời gọi; cần bổ sung giao dịch ở lát nghiệp vụ trước khi cộng hạn mức/giữ
  lượt có điều kiện. Mặc định ABBYY tắt, thời hạn cấu hình 900 giây.
- Mã cũ giữ nguyên để chuyển lõi ở lát sau. Vỏ `chay.py`, `lib/cong_ocr.py`
  cũ, shim và hàm SDK riêng không dùng trong gói mới; ghi nhận để chuyển
  `LUU-TRU/` sau, không xóa trong OCR-0.
- Không phát sinh câu hỏi mới cần Anh quyết định; giữ các mục chờ Anh trong
  phiếu giao (Q1/Q2/Q3 và các việc trước khi thử ABBYY thật).

## Bằng chứng OCR-1 — 14/11/2026

- Nhánh: `codex/e_ocr-ocr-1`; PR: **chờ lead mở**. Lead commit và mở PR.
  Tiêu đề đề xuất: `[e_ocr] OCR-1 — Lớp chữ PDF và ABBYY Hot Folder cục bộ`.
- Thời gian thực tế: **14/11/2026, 22:40–23:01** (21 phút, khoảng
  **0,35 giờ**), so với **5 giờ ước tính** trong phiếu; giờ Việt Nam.
- Chuyển thể `lop_chu.py`, `van_ban.py`, `bang.py`, `abbyy.py` từ nguồn cũ
  vào gói; `chay.py` nối hai action dùng chung lõi. Bỏ phụ thuộc Core cũ,
  không dùng `lib/cong_ocr.py`, không đổi mã `ma-nguon/` hoặc SDK/Core.
- Giữ thuật toán đọc chữ ẩn, dấu tiếng Việt, thứ tự tiền/ngày, kiểm ma trận
  xoay trang và tọa độ từ nguồn PDF. Toàn văn nối trang bằng `\f`; kết quả
  có vị trí khối/dòng/từ, SHA-256 tệp đầu vào, nguồn đọc, phiên bản và cảnh báo.
  Bảng có đường kẻ PDF giữ ô trống và ô gộp; không OCR lại ảnh nền.
- Đầu vào đọc bằng `viec.mo_tep`; tự kiểm định dạng/đếm trang trước gửi.
  Vượt 60 trang → `QUA_SO_TRANG`, tệp hỏng/mật khẩu → `TEP_HONG`; lỗi tiếng
  Việt không có đường dẫn. Kiểm cả trường hợp đúng 60 trang và quá 20 MiB.
- Hot Folder công bố tệp qua đổi tên nguyên tử trên cùng filesystem, chờ
  đúng mã tương quan, đọc kết quả ổn định/có EOF, kiểm đủ lớp chữ/số trang.
  Có tiến độ từng bước, kiểm hủy trong vòng chờ; rút tệp chưa được nhận và
  dọn thư mục tạm ở `finally`. Lỗi dọn kết quả không trả thành công giả.
- Quá hạn khi còn rút được tệp chờ → lỗi cho phép thử lại. Tệp đã được
  nhận mà chưa trả → `ChuaRo(ma_tuong_quan)`, không chuyển nguồn và không
  nộp kết quả giả. Hủy sau nhận vẫn kết thúc `HUY`, không ép dừng ABBYY.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows x64, Python 3.13.14;
  ABBYY giả là luồng nền theo dõi thư mục DEMO và ghi PDF lớp chữ cùng mã.
  Chưa chạy Linux: máy không có WSL/Linux; test dùng API Python đa nền tảng,
  không mock parser PDF thật. Chưa nối ABBYY, Tesseract hoặc Core thật.

### Kết quả ba lệnh bắt buộc OCR-1

Lượt kiểm cuối đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`. Cả ba lệnh
có mã thoát **0** (chạy riêng và lấy mã thoát riêng):

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
[ĐẠT] Đọc PDF DEMO có lớp chữ và vị trí, 3 trang: {"loai": "van_ban_tai_lieu", "van_ban_tai_lieu": {"phien_ban": 1, "van_ban": "DEMO - HO SO GIA\nCông ty DEMO Ánh Dương\n1.000.000 VND\n30/10/2026\fDEMO - HO SO GIA\nCông ty DEMO Ánh Dương\n1.000.000 VND\n30/10/2026\fDEMO - HO SO GIA\nCông ty DEMO Ánh Dương\n1.000.000 VND\n30/10/2026", "trang": [{"so
[ĐẠT] Đọc văn bản thuần từ PDF DEMO có lớp chữ, 3 trang: {"loai": "van_ban", "van_ban": "DEMO - HO SO GIA\nCông ty DEMO Ánh Dương\n1.000.000 VND\n30/10/2026\fDEMO - HO SO GIA\nCông ty DEMO Ánh Dương\n1.000.000 VND\n30/10/2026\fDEMO - HO SO GIA\nCông ty DEMO Ánh Dương\n1.000.000 VND\n30/10/2026"}
Engine e_ocr 1.0.1: mọi ví dụ chạy thử DEMO đều đạt.
Kết quả: 2/2 ĐẠT; mã thoát 0.

> .venv\Scripts\python -m pytest e_ocr/tests -q
........................................................................ [ 60%]
...............................................                          [100%]
119 passed in 8.39s
Mã thoát: 0; 0 skipped.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát: 0.
```

Ca mới gồm hai action với PDF 3 trang qua ABBYY giả, đúng công ty/tiền/ngày
và tọa độ, PDF lớp chữ không gửi ABBYY, PDF trộn trang có/không chữ, bốn
góc xoay, 60/61 trang, tệp hỏng/quá cỡ, PNG/JPEG, kết quả thiếu chữ/sai số
trang, timeout trước/sau nhận, hủy trước/sau nhận, kết quả đang ghi dở,
mã tương quan khác, lỗi gửi/dọn tạm, bảng ô trống/ô gộp và hủy trong parser.

Kiểm bổ sung: kết quả PDF có bảng đạt JSON Schema draft 2020-12 chung;
metadata phiên bản khớp phiếu; mọi pin runtime khớp distribution đã cài.
`jsonschema` chỉ dùng kiểm bổ sung từ môi trường sẵn có, không là dependency
runtime hoặc điều kiện chạy pytest. Băm tệp gói cập nhật trong `NGUON.md`;
`git diff --check` không báo lỗi. Wheel SDK 2.0.0 cài offline, SHA-256 khớp
`SHA256SUMS.txt`. Không chạy commit/push.

### Quyết định tạm, lệch và phần còn lại OCR-1

- Dùng cấu hình JSON ngoài gói theo quyết định tạm đã có; thiếu cấu hình
  chỉ chặn việc cần ABBYY, không chặn PDF có lớp chữ. Không thêm bí mật.
- Thư mục đệm riêng của lượt nằm cạnh thư mục vào để `os.replace` không
  vượt filesystem; cần quyền tạo/dọn đệm ở thư mục cha. Không dùng thư
  mục dữ liệu thật của công cụ ABBYY. Kết quả trả muộn chưa có ở thời điểm
  timeout vẫn thuộc ABBYY; xử lý bền/chống gửi lại ở OCR-4.
- Quy ước tạm Hot Folder: rời/xóa tệp vào khi nhận, trả đúng tên
  `<ma_tuong_quan>.pdf`. Chưa có ACK nguồn riêng; cần kiểm quy ước này trên
  ABBYY thật ở OCR-7. Không diễn giải sự im lặng thành thành công.
- Thêm sớm hai ví dụ DEMO lớp chữ để đạt kiểm chung AGENTS.md §5 ngay ở
  OCR-1. Bộ DEMO đầy đủ cho Tesseract/Word vẫn thuộc OCR-5.
- Phần xử lý đúng **5 tệp mã** được giao; ngoài ra chỉ sửa metadata phiên
  bản trong `__init__.py` để đồng bộ `engine.json` 1.0.1. Không mở rộng thêm
  mô-đun nghiệp vụ; dòng metadata đi cùng phiên bản gói, không tách lát riêng.
- Tái dùng pin pdfplumber/Pillow và dependency từ lock cũ; không thêm
  PyMuPDF/defusedxml/numpy. `requirements.lock` hiện ghim phiên bản, băm
  wheel SDK ghi ở comment để tránh bật nhầm `--require-hashes` khi dependency
  chưa có hash. Lock wheel đa nền tảng và máy sạch vẫn thuộc OCR-6.
- Tesseract/chọn nguồn/sổ hạn mức thuộc OCR-2; xuất Word thuộc OCR-3;
  nhật ký lượt bền/chống trùng/đọc kết quả trả muộn thuộc OCR-4. Bảng chỉ
  trong ảnh nền chưa được tái tạo; có cảnh báo để không hiểu là đã giữ bảng.
- Cần Core: tiếp tục các mục cấu hình/ngăn/lượt bền #10 ở trên; OCR-1
  không phát sinh yêu cầu Core hoặc câu hỏi mới cần Anh quyết định.
- Vỏ/cổng OCR cũ không dùng trong gói mới; vẫn giữ nguyên để chuyển
  `LUU-TRU/` sau theo kế hoạch, không xóa.

## Bằng chứng OCR-3 — 14/11/2026

- Nhánh: `codex/e_ocr-ocr-3`; PR: **chờ lead mở**. Không chạy commit/push.
  Tiêu đề đề xuất: `[e_ocr] OCR-3 — Xuất Word giữ bảng, ô trống và ô gộp`.
- Thời gian thực tế: **14/11/2026, 23:02–23:14** (12 phút, khoảng
  **0,20 giờ**), so với **3 giờ ước tính** trong phiếu; giờ Việt Nam.
- `ocr.xuat_word@1` nhận `tep`, gọi `trich_van_ban` như hai action đọc,
  rồi dựng DOCX từ `van_ban_tai_lieu`; trả phong bì `tep` bằng
  `viec.tai_tep_ra(ten, bytes, mime)`, tên `<tên gốc không phần mở rộng>-OCR.docx`.
  Không đọc lại/OCR lại nguồn để xuất Word; không giữ nội dung trên đĩa.
- Logic tách trong `xuat_word.py` và `ban_giao.py`; `chay.py` sửa tối thiểu,
  giữ điểm nối chung cho OCR-2. Tổng cộng **4 tệp mã** thêm/sửa, gồm
  `__init__.py` đồng bộ phiên bản 1.0.2; không sửa `van_ban.py`, `bang.py`
  hoặc mã nguồn cũ. Khi gộp OCR-2, lead hợp nhất phiên bản/DEMO trong phiếu.
- Giữ ô trống và ô gộp ngang/dọc bằng `gridSpan`/`vMerge`, kể cả ô gộp
  hai chiều và ô gộp rỗng; nội dung ô gốc chỉ xuất một lần. Kiểm lưới đủ
  và không chồng ô; thiếu ô thì từ chối, không tự thêm ô trống.
- Ghi tọa độ bảng `pt` bằng `tblpPr` neo theo trang, độ rộng cột từ tọa độ
  ô nếu có; không có tọa độ từng ô thì chia đều khoảng chưa có mốc. Giữ
  khổ trang, hướng ngang/dọc, thứ tự trang theo `so` và thứ tự khối; mỗi
  trang nguồn thành một section. Có đoạn ngăn giữa hai bảng liên tiếp.
- Không chuẩn hóa tiền/ngày; giữ nguyên dấu tiếng Việt, dấu XML, khoảng
  trắng, tab và xuống dòng. Từ chối dữ liệu không hợp lệ, bảng quá trần,
  quá trang/ký tự và tên tệp ra quá dài; hủy/chưa rõ không nộp kết quả giả.
- Thêm PDF DEMO có bảng 3 trang từ bộ sinh sẵn có và ví dụ chạy thử Word
  trong phiếu. Test mở lại ZIP/XML để đếm đủ lưới 4×4, 11 `tc`, 5 `gridSpan`,
  `vMerge restart/continue`, 4 ô gốc rỗng; kiểm cả bảng từ parser PDF thật,
  tiền/ngày nguyên văn, tọa độ, thứ tự trang và tên/MIME/tệp tải từ CoreGia.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows x64, Python 3.13.14;
  không chạy ABBYY/Core/Word thật hoặc Linux. Test dùng thư viện chuẩn và
  seam nguồn đọc, không phụ thuộc Windows. Kiểm thêm bằng `python-docx`
  sẵn có: mở được DOCX, 2 section, bảng 4×4, nhận đúng ô gộp 2×2 và ô rỗng;
  công cụ này không là dependency runtime hoặc điều kiện chạy pytest.

### Kết quả ba lệnh bắt buộc OCR-3

Lượt kiểm cuối đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; cả ba lệnh
có mã thoát **0**. Đầu ra SDK dưới đây chỉ lược phần payload hai DEMO đọc
đã có ở OCR-1; dòng Word và tổng kết giữ nguyên:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
[ĐẠT] Đọc PDF DEMO có lớp chữ và vị trí, 3 trang: …
[ĐẠT] Đọc văn bản thuần từ PDF DEMO có lớp chữ, 3 trang: …
[ĐẠT] Xuất Word giữ bảng từ PDF DEMO có lớp chữ, 3 trang: {"loai": "tep", "tep": {"tep_id": "tep-7", "ten": "DEMO-bang-3-trang-OCR.docx", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "kich_thuoc": 1598}}
Engine e_ocr 1.0.2: mọi ví dụ chạy thử DEMO đều đạt.
Kết quả: 3/3 ĐẠT; mã thoát 0.

> .venv\Scripts\python -m pytest e_ocr/tests -q
........................................................................ [ 49%]
........................................................................ [ 99%]
.                                                                        [100%]
145 passed in 8.43s
Mã thoát: 0; 0 skipped.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát: 0.
```

### Lệch, quyết định tạm và giới hạn OCR-3

- Bản `ma-nguon/vendor/mask_ocr` trong repo chỉ chứa parser/layout, không
  có bộ ghi Word để chép nguyên. Chuyển thể quy tắc ô gộp từ `bang.py` và
  `word_layout` sang chiều xuất; dựng ZIP/XML bằng thư viện chuẩn. Không
  thêm thư viện hoặc chép import PyMuPDF/defusedxml chưa được ghim.
- `ban_giao.py` cũ phụ thuộc `CongOCR`/SDK/ACK cũ: chỉ chuyển vai trò bàn
  giao sang SDK 2.0 như phiếu yêu cầu. Không mang sổ ACK/lease/nội dung cũ
  vào gói. Phần cũ giữ nguyên để chuyển `LUU-TRU/` sau, không xóa.
- Tọa độ hỗ trợ `pt` như đầu ra OCR-1. Đơn vị khác bị từ chối, không đoán
  DPI. Row height dùng `atLeast` để tránh cắt chữ; Word có thể dàn lại theo
  font máy. Đã kiểm tọa độ trong XML, chưa kiểm hình thức bằng Word thật;
  không cam kết khớp từng pixel với bản gốc hoặc nhận ra bảng chỉ có trong ảnh.
- SDK wheel 2.0.0 cài offline trong `.venv --system-site-packages`, SHA-256
  khớp `SHA256SUMS.txt`; dùng dependency/pytest sẵn có, chưa là kiểm máy sạch
  OCR-6. Đã cập nhật README/CHANGELOG/NGUON và băm mọi tệp gói.
- Cần Core / Chờ Anh mới: **không phát sinh**. Không thay đổi các mục chờ
  có sẵn; không tự mở kết nối ABBYY hoặc cài phần mềm hệ thống.
