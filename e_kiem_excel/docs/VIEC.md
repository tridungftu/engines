# VIỆC — danh sách việc duy nhất của project `e_kiem_excel`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng). Giờ là **ước tính của lead, chưa đo**.

| # | Việc | Lát | Trạng thái | Giờ (ước tính) | Ghi chú |
|---|---|---|---|---:|---|
| 0 | Phiếu engine, tạo thư mục, chép mã gốc tham chiếu, lập phiếu giao Codex | EX-P | Xong — 16/11/2026 | — | Lead Claude. Anh đồng ý tiến hành 16/11; Q1–Q3 áp đề xuất |
| 1 | Khung gói SDK 2.2.0, ghim thư viện, sinh DEMO có giá trị lưu, nhận diện tệp, trần giải nén/ô, đo bộ nhớ | EX-0 | Chờ Core — 18/11/2026 | 4 | Mã và phép đo đã thực hiện; chưa đạt điều kiện CLI do yêu cầu hàm tạm CHUA_LAM. PR: chờ lead mở. Chi tiết bên dưới |
| 2 | `SoDo` + hàm tham chiếu + K1–K6 nạp từ bytes; schema `tep_json` | EX-1 | Xong — 18/11/2026 (phần EX-1) | 6 | PR: chờ lead mở. 62 pytest đạt; CLI chung 2/3, còn CHUA_LAM của EX-4. Schema chờ lead duyệt; chi tiết bên dưới |
| 3 | K7 + `o_dich`, `nhan_o_dich_json`, `bo_nhom_json`; Phụ lục A làm fixture | EX-2 | Xong — 18/11/2026 | 4 | PR: chờ lead mở. CLI 3/3; pytest 163 passed; kiểm độc lập mã 0. Đã kiểm bằng Core giả (CoreGia); chi tiết bên dưới |
| 4 | Báo cáo Excel trong RAM; K8 sau công tắc `kiem_nguon_kl` | EX-3 | Xong — 19/11/2026 | 4 | PR: chờ lead mở. CLI 3/3; pytest 183 passed; kiểm độc lập mã 0. Đã kiểm bằng Core giả (CoreGia); chi tiết cuối sổ |
| 5 | `excel.doc_bang@1` khuôn `xay_dung_klgt` | EX-4 | Đang làm — 18/11/2026 | 4 | Mã EX-4 xong, chờ gộp các lát toàn vẹn để CLI chung đạt 3/3. PR: chờ lead mở |
| 6 | Khuôn `tong_quat` | EX-5 | Xong — 18/11/2026 | 4 | PR: chờ lead mở. CLI 5/5 ĐẠT; pytest 144 passed, 0 skipped; kiểm độc lập mã 0. Đã kiểm bằng Core giả (CoreGia) |
| 7 | Ghim nguồn, cài máy sạch, đo thời gian/bộ nhớ trên bản hoàn chỉnh, chốt `thoi_han_giay` | EX-6 | Xong — 19/11/2026 (mã + kiểm cục bộ) | 3 | PR: chờ lead mở. CLI 5/5; pytest 240 passed; độc lập mã 0; cài sạch offline đạt. CI Linux 3.11 và Windows CMD chờ chạy; chi tiết cuối sổ |
| 8 | Trình soạn ô đích, bộ nhóm và khuôn cột cho Cài đặt bước | TS-EX | Xong — 21/11/2026 (mã + kiểm CoreGia) | 4 | PR: chờ lead mở. CLI 5/5; pytest 241 passed, 0 skipped; độc lập mã 0; UI 12/12; 3 ảnh DEMO. Core nạp màn qua cửa D2 còn chờ; chi tiết cuối sổ |
| 9 | Chạy bằng SDK Core cấp, kiểm lock/wheels, bỏ phụ thuộc SDK nội bộ | SDK25 | Xong — 22/11/2026 (mã + kiểm CoreGia) | 2–4 | PR: chờ lead mở. CLI 5/5; pytest 263 passed, 0 skipped; độc lập mã 0; UI 12/12; cài sạch Windows offline đạt. MIME chờ Core; chi tiết SDK25 bên dưới |
| | **Tổng** | | | **35–37** | |

## SDK25 — thực hiện 22/11/2026, PR: chờ lead mở

**Kết luận: Đạt kiểm trên SDK 2.5.0. Đã kiểm bằng Core giả (CoreGia); chưa nối
Core thật.** Python 3.13.14 win_amd64; giữ gói 0.1.3 và toàn bộ lock/wheel lead
đã chuẩn bị. Không commit/push.

Đã làm:

- Dùng trực tiếp `Engine.tu_khai_bao`, bỏ lớp con ghi đè nhật ký/xử lý việc và
  đối tượng bọc đường truyền. Không gọi/kiểm chữ ký/monkeypatch nội bộ SDK.
  Test lỗi bất ngờ qua CoreGia xác nhận câu lỗi chuẩn, không lộ nội dung exception.
- Kiểm import AST và tiến trình cô lập lấy thư viện/bản ghim từ lock mới, không
  khóa cứng phiên bản SDK. Công cụ đo hiệu năng đọc phiên bản SDK thực được cài.
- Thêm 20 ca SDK25: lock ASCII, không BOM/coding/nối dòng/chú thích giữa dòng,
  không namespace Core/SDK hoặc tên trùng; đủ đúng một wheel/thư viện cùng bản
  và SHA-256, không wheel thừa/sdist/thư mục con; cho hash Linux cùng dòng.
- Script máy sạch dùng SDK 2.5.0 có đối chiếu SHA-256 và wheel đi kèm gói, cài
  offline với hash/binary/no-deps. CMD giữ ASCII/CRLF, ưu tiên Python `.venv`.
  Workflow Linux dùng wheel gói cho Python 3.11 và 3.13; không tải lại runtime.
- README, NGUON, CHANGELOG và ghi chú D2 cập nhật; dùng
  `tests/kiem_bam_goi.py --cap-nhat` sau các chỉnh sửa trong gói.

Kết quả kiểm thật (mọi mã thoát 0):

```text
.venv\Scripts\python -X utf8 -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
  5/5 [ĐẠT]; engine 0.1.3, mọi ví dụ chạy thử DEMO đều đạt.
.venv\Scripts\python -X utf8 -m pytest e_kiem_excel/tests -q
  263 passed in 43.70s; 0 skipped.
.venv\Scripts\python -X utf8 e_kiem_excel/tests/kiem_doc_lap.py
  [ĐẠT] AST, cây gói, import cô lập; CoreGia: 5/5 DEMO XONG.
node --test e_kiem_excel/tests/ui/tham_so.test.mjs
  12 pass, 0 fail, 0 skipped.
cmd.exe /d /c e_kiem_excel\tests\KIEM-MAY-SACH.cmd
  Cài mới SDK 2.5.0 + ba thư viện offline; băm 28/28; dependency/DEFUSEDXML đạt;
  CLI 5/5 DEMO; kiểm độc lập đạt.
sh -n e_kiem_excel/tests/kiem_may_sach.sh
  Không lỗi cú pháp. Chưa chạy CI Linux trên máy này.
```

`git grep` không còn ghim SDK cũ ở mã/công cụ đang chạy; các mục còn SDK cũ
trong docs là lịch sử. `tests/demo/so-do-hieu-nang-EX6.json` là tài liệu số đo
thực ngày 19/11/2026, giữ nguyên metadata SDK cũ, không gắn nhãn thành số đo
SDK25. Không còn tham chiếu nội bộ SDK trong mã gói; `git diff --check` đạt.

Thời gian thực tế: **18:29–19:01 ngày 22/11/2026, 32 phút (~0,53 giờ)**;
ước tính phiếu: **2–4 giờ**.

Lệch khỏi phiếu / quyết định tạm: không đổi xử lý nghiệp vụ, phiên bản thư
viện hoặc manifest lead đã chuẩn bị; không thêm thư viện/tải mạng. Chấp nhận
bộ kiểm MIME và câu lỗi chuẩn SDK như phiếu SDK25 cho phép. CI Linux đã cập
nhật, chờ lead chạy trên GitHub; lượt cài máy sạch Windows đã đạt tại đây.

Cần Core / Chờ Anh mới phát sinh: Core chuẩn hóa MIME `.xlsm` trước SDK hoặc
SDK nhận MIME không phân biệt hoa/thường. Chi tiết ở mục Cần Core; không có
câu chặn mới cần Anh trả lời.

## Chờ Anh
- Không có câu chặn. Q1–Q3 đã áp đề xuất (16/11/2026).
- Phụ lục A, hai chỗ lệch nhỏ so với mã gốc (nhóm 6 xét cả nhãn dòng; `dai|rong|cao` khớp chứa chuỗi): EX-2 báo kết quả đo, Anh duyệt nếu muốn chặt hơn.

## Cần Core
- **SDK25 (22/11/2026) — MIME, thay ghi nhận EX0-SDK-02:** SDK 2.5.0 vẫn
  từ chối MIME `.xlsm` chứa `macroEnabled.12` do CoreGia tự gán, trả
  `DAU_VAO_KHONG_HOP_LE`; dạng `macroenabled.12` được nhận. Đã kiểm bằng Core
  giả (CoreGia), cả đầu vào gửi kèm và tải riêng. Đã bỏ lớp bọc SDK nội bộ;
  cần Core chuẩn hóa MIME trước khi giao việc hoặc SDK nhận MIME không phân
  biệt hoa/thường. Chưa xác nhận thuật toán gán MIME trên Core thật.
- **SDK25 — câu lỗi/log:** dùng nguyên câu lỗi chuẩn và log đã lọc của SDK
  2.5.0; không có cửa công khai trong hướng dẫn engine để đổi câu/định dạng log.
  Nếu cần tùy biến, đề nghị SDK cấp cửa công khai; engine không ghi đè nội bộ.
- **TS-EX (21/11/2026) — cửa D2:** nạp `ui/tham_so.js` theo khai dự kiến
  `KHAI-SDK-2.1.json` vào Cài đặt bước cho hai năng lực; Core cấp bản tham số,
  danh sách sheet từ tệp mẫu (nếu có), quyền và phiên bản bước. Callback
  đọc/lưu thuộc màn bước Core, kiểm CAS/kiểu/trần và trả phiên bản mới; đây
  **chưa là hợp đồng SDK đã phát hành**. Không dùng `.cau_hinh`/`.ngan` engine
  để cất tham số quy trình. Lỗi 409 giữ nội dung sửa và buộc tải lại. Đã kiểm
  bằng Core giả (CoreGia), chưa kiểm quyền/CAS trên Core thật.
- **TS-EX — hướng dẫn ô JSON chung:** SDK 2.2.0 giới hạn `mo_ta` 500 ký tự;
  đã đưa mô tả rút gọn + mẫu vào ba tham số, bảng từng trường/từng cấp và mẫu
  đầy đủ trong README gói. Cần Core hiển thị mô tả và cho mở hướng dẫn đầy đủ
  (cửa D2/D của phiếu UI) cho tới khi nạp được trình soạn. Không nới schema SDK.
- **EX-6 (19/11):** không phát sinh cửa mới. Đã kiểm bằng Core giả (CoreGia): CLI 5/5, pytest 240 passed, kiểm độc lập mã 0; cài sạch offline từ ZIP thử đạt. EX0-SDK-01 là lịch sử, không còn chặn. Giữ EX0-SDK-02/MIME Core thật. CI Linux 3.11, CMD Windows và gói phát hành từ commit chờ lead/Anh.
- Không có cửa mới cho engine.
- **EX-3 (19/11):** không phát sinh yêu cầu Core/SDK; báo cáo Excel và JSON qua `viec.tai_tep_ra`. Giữ EX0-SDK-02 về MIME/Core thật; chưa kiểm với Core thật.

- **EX-5 (18/11):** không phát sinh yêu cầu Core/SDK. Bản worktree đã có EX-1 + EX-4 + EX-5: CLI chuẩn **5/5 ĐẠT**, mã 0; vướng hàm tạm EX0-SDK-01 trong các báo cáo lịch sử dưới đây không còn chặn bản này. EX0-SDK-02/MIME Core thật vẫn giữ nguyên, không thuộc phạm vi EX-5.

- **EX-2 (18/11):** không phát sinh cửa Core/SDK mới. Gói hiện đã có EX-4 và K1–K7,
  CLI chuẩn **3/3 ĐẠT**, mã 0; EX0-SDK-01 không còn chặn bản hiện tại. Các ghi nhận
  CLI mã 1 trong báo cáo EX-0/EX-1/EX-4 bên dưới là lịch sử của từng lượt.
  EX0-SDK-02 về MIME/Core thật vẫn giữ nguyên.
- **EX-1 (18/11):** không phát sinh yêu cầu Core/SDK. Hai DEMO `excel.toan_ven@1` đã XONG qua CLI chuẩn; mục EX0-SDK-01 bên dưới hiện chỉ còn ví dụ `excel.doc_bang@1` của EX-4. Giữ nguyên ví dụ này, không thay kỳ vọng CLI thành đạt; lead chạy lại cả gói sau khi ghép EX-4. MIME vẫn theo EX0-SDK-02.
- **Cần Core xác nhận** MIME khi tải `.xlsx`/`.xlsm` lên Core thật. `API-ENGINE-v1.md` chỉ quy định trường `mime`, không cam kết thuật toán gán MIME. SDK `thu.py`, `CoreGia.them_tep` → `_mime` trả `.xlsx`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; `.xlsm`: `application/vnd.ms-excel.sheet.macroEnabled.12`. HTTP tải byte của `MayChuGia` dùng `application/octet-stream`, khác metadata trong phong bì. Chưa có bằng chứng Core thật; manifest tạm nhận thêm `application/octet-stream`, vẫn kiểm đuôi/chữ ký/ZIP/XML.
- **EX0-SDK-01 — CLI và hàm tạm mâu thuẫn:** SDK 2.2.0 `thu.main()` chỉ cho `[ĐẠT]` khi `trang_thai == "XONG"`, không có cách khai lỗi kỳ vọng trong `chay_thu_demo`. Yêu cầu EX-0 giữ `LoiNghiepVu("CHUA_LAM", …)` làm ba ví dụ đều kết thúc `LOI`. Giữ nguyên API/SDK và yêu cầu hàm tạm; không đổi lỗi thành thành công hay bỏ DEMO. Cần lead thống nhất nghiệm thu EX-0 theo test lỗi kỳ vọng, hoặc SDK bổ sung cơ chế kiểm lỗi kỳ vọng. CLI chuẩn vẫn mã 1 ở bản này; không tuyên bố đạt ba lệnh.
- **EX0-SDK-02 — lịch sử 18/11:** lớp bọc MIME đã bỏ trong SDK25; trạng thái
  hiện hành xem mục SDK25/MIME ở trên. Các kết quả cũ bên dưới chỉ ghi nhận
  lượt kiểm trước khi bỏ lớp bọc.

## EX-0 — thực hiện 18/11/2026, PR: chờ lead mở

Kết luận: **Chưa đạt điều kiện nghiệm thu chung** vì CLI chuẩn không chấp nhận hàm tạm `CHUA_LAM`; khung gói, kiểm an toàn, DEMO, ghim thư viện và phép đo đã hoàn thành. Đã kiểm bằng Core giả (CoreGia), chưa nối Core thật.

### Phần đã làm

- Ba tệp Python runtime: `__init__.py`, `chay.py`, `nhan_dien.py`; không vượt quy mô lát. Hai năng lực đủ 11 trường ra mỗi năng lực và toàn bộ tham số theo phiếu §4.1–4.3; `khuon` có hai lựa chọn, mọi tham số chữ có trần. `o_dich` tạm tối đa 512 ký tự; tệp 20 MiB, thời hạn Core 120 giây, hủy được.
- Bọc nhật ký bằng mã cố định theo mẫu Hóa đơn. Hai hàm kiểm an toàn đầu vào rồi báo `CHUA_LAM`; không gọi openpyxl, không có kết quả nghiệp vụ giả.
- Kiểm đuôi `.xlsx`/`.xlsm`, chữ ký ZIP/OLE; kiểm tổng giải nén, số entry, CRC/XML theo luồng 64 KiB; đếm thẻ `c` theo namespace, không nạp cây XML. DTD/thực thể kể cả UTF-16 bị từ chối `TEP_HONG`; vượt trần → `VUOT_GIOI_HAN`; `.xls` → `TEP_KHONG_HO_TRO`. Có kiểm vùng ô thưa/ô gộp lớn và worksheet đổi đường dẫn/đuôi qua relationships.
- Ghim wheel `openpyxl==3.1.5`, `et_xmlfile==2.0.0`, `defusedxml==0.7.1`, hash trong lock và nguồn/giấy phép trong `NGUON.md`. SDK 2.2.0 SHA khớp `SHA256SUMS.txt`. Wheel ngoài tải từ mirror Aliyun và xác minh bằng hash metadata PyPI; cài vào `.venv` hoàn toàn bằng `--no-index --require-hashes --no-deps`.
- DEMO tất định bằng ZIP/XML thư viện chuẩn: mỗi công thức có `<f>` và `<v>` tự tính; riêng tệp thiếu `<v>` cố ý. Có tệp đủ K1–K8, tệp sạch, bảng KL, XML thực thể lồng nhau, `.xls` OLE giả; đáp án và băm ngoài gói. Mã gốc xác nhận **đúng toàn bộ 11 phát hiện** (mức, mã, ô), sạch K1–K6 không có cờ; bảng KL đọc được 30 dòng và tổng 60.000.000 VND. Đây là kiểm fixture, chưa phải kiểm tương đương thuật toán engine ở EX-1…EX-4.
- `ma-nguon/` không sửa. Checkout Windows có CRLF: SHA raw `toan_ven.py` = `4cf78d3c1eb6d2612071088291d966a32d0aed484d4f871931725c27921f2dc4`, `master_hd.py` = `a1ef89edec9b5b03c0165caa5a9d9397e49ce26437347683ecc64d9242d4afa5`; chỉ chuẩn hóa CRLF → LF trong phép kiểm RAM thì khớp đúng hai SHA nguồn đã ghim. Không viết lại tệp nguồn.
- Có script kiểm máy sạch Linux/Windows nhận thư mục wheel offline. Tạo thêm venv sạch và chép riêng gói ra khỏi repo tham chiếu để kiểm cài offline trên Windows: cài thành công, kiểm độc lập mã 0; CLI vẫn mã 1 với ba lỗi `CHUA_LAM`. Chưa chạy Linux; `KIEM-MAY-SACH.cmd` để Anh/lead chạy theo phiếu EX-6.

### Đo bộ nhớ thực tế

Lệnh: `.venv/Scripts/python -B e_kiem_excel/tests/do_bo_nho.py --ra e_kiem_excel/tests/demo/so-do-bo-nho.json`.
Windows x64, Python 3.13.14, openpyxl 3.1.5, defusedxml 0.7.1. Mỗi cỡ chạy trong tiến trình riêng; `read_only=False`, `data_only=False` rồi `True`, giữ đồng thời hai workbook; `keep_vba=False`, `keep_links=False`. RSS đỉnh lấy `PeakWorkingSetSize` của Windows; script dùng `resource.ru_maxrss` trên Linux. `tracemalloc` bật trong lúc nạp hai workbook; RSS gồm Python, input bytes, thư viện và overhead của tracemalloc. Thời gian là lúc có tracemalloc, **chỉ nạp workbook**, chưa chạy K1–K8.

| Cỡ DEMO danh nghĩa | Byte tệp (MiB thực) | Giải nén (MiB) | Ô thực | Thời gian (giây) | tracemalloc đỉnh (MiB) | RSS nền (MiB) | RSS đỉnh (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5 MiB | 5.237.078 (4,994) | 10,247 | 44.481 | 3,931 | 51,80 | 40,95 | 159,88 |
| 10 MiB | 10.474.292 (9,989) | 20,524 | 88.961 | 8,032 | 103,63 | 46,07 | 279,70 |
| 20 MiB | 20.948.296 (19,978) | 41,090 | 177.901 | 16,425 | 207,26 | 55,79 | 539,30 |
| Mẫu ô ngắn, gần 250.000 ô | 897.056 (0,855) | 8,850 | 249.981 | 12,662 | 181,78 | 37,19 | 548,73 |

Mẫu 5/10/20 MiB dùng ZIP_DEFLATED thật, không đệm tệp giả: 20 cột, 15 chuỗi DEMO hex khó nén + 5 công thức/row; dung lượng thực sai dưới 0,2% và luôn dưới mốc danh nghĩa. Mẫu mật độ dùng ô số/công thức ngắn. Tệp đo chỉ ở thư mục tạm, tự dọn sau; JSON số đo có SHA-256 từng đầu vào để tái lập. Cả bốn mẫu được bộ chặn chấp nhận.

**Đề xuất tạm:** giữ `tep_toi_da_mib = 20`, thêm trần **250.000 ô thực**, **128 MiB giải nén**, **2.048 entry**, tổng hình chữ nhật các sheet **500.000 ô**; vùng gộp có kiểm trần bổ sung. Mẫu 0,855 MiB vẫn tốn RSS hơn mẫu 20 MiB nên trần byte đơn lẻ không đủ. Trần giải nén 128 MiB là mức thử nghiệm khoảng 3 lần mẫu lớn nhất đã đo, chưa phải kết quả đo tại biên. Chưa chứng minh đỉnh bộ nhớ cho mọi workbook hoặc khi K1–K8 tạo cây/báo cáo; EX-6 phải đo lại mật độ/vùng ô/giải nén ở biên và thời gian toàn năng lực trước khi chốt 120 giây.

### Kết quả ba lệnh nghiệm thu

Chạy bằng `.venv/Scripts/python`, đặt `PYTHONDONTWRITEBYTECODE=1` và UTF-8; đã kiểm bằng Core giả (CoreGia).

```text
python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 0/3 ĐẠT; 3/3 LOI với mã CHUA_LAM; mã thoát 1.
python -m pytest e_kiem_excel/tests -q
→ 38 passed, 0 skipped; mã thoát 0.
python e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập; 3/3 CHUA_LAM đúng EX-0; mã thoát 0.
```

Kiểm độc lập chạy tiến trình `-I -B -S`, chỉ cho stdlib/SDK/ba thư viện đã ghim/gói Excel; chặn mạng/tiến trình ngoài, không có `kho_tri_thuc.*`, không bytecode/symlink/tệp lớn trong gói.

Thời gian thực tế: **0,37 giờ**, từ **18/11/2026 20:15 đến 20:37** (giờ Việt Nam; ước tính trong phiếu: **4 giờ**). Kiểm cuối: pytest **38 passed in 1.27s**, không skip; CLI mã **1**; kiểm độc lập mã **0**; cài sạch offline và kiểm độc lập bản chép riêng mã **0**. `git diff --check` mã **0**; không có thay đổi `ma-nguon/`, bytecode hoặc symlink trong gói. Không commit/push; lead nhận worktree để commit và mở PR.

## EX-4 — thực hiện 18/11/2026, PR: chờ lead mở

Kết luận: **Mã phạm vi EX-4 hoàn tất, chưa đạt điều kiện nghiệm thu chung** vì
hai DEMO `excel.toan_ven@1` vẫn `CHUA_LAM` từ EX-0 trong worktree này.
Đã kiểm bằng Core giả (CoreGia), chưa nối Core thật. Không sửa các tệp EX-1
(`chuan_hoa.py`, `so_do.py`, `tham_chieu.py`, `kiem_tra.py`), không sửa mã nguồn
tham chiếu, không commit/push.

### Đã làm

- `doc_bang.py` chuyển `_hdr_text`, `tim_bang_chi_tiet`, `khoa`, `LABELS`,
  `tim_so_tong_hop` từ `master_hd.py` đúng vùng phiếu §3.2. Giữ tìm cột, chọn bảng
  theo điểm, dòng nhóm, khóa nhóm/tên/ĐVT (tên cắt 120 ký tự), hậu tố `#2`, `#3`.
  Dừng ở dòng Cộng không có ĐVT; hạng mục Cống có ĐVT vẫn đọc. Không thấy bảng
  trả `KHONG_TIM_THAY_BANG`; workbook lỗi trả `TEP_HONG` bằng câu tiếng Việt.
- `_nfc`, `_bo_dau`, `_num` là helper riêng tư trong `doc_bang.py`; có ghi chú
  **lead gộp vào chuan_hoa.py sau EX-1**. Decimal trong đọc/tính; phép nhân đặt
  precision đủ số chữ số hai toán hạng; xuất `format(d, "f")`, không đổi qua float.
- Nối riêng `excel.doc_bang@1`, trả đủ 11 trường §4.2 và tệp JSON UTF-8 §5.2
  qua `viec.tai_tep_ra`, trần 20 MiB, không cắt ngầm. Chỉ dùng RAM, đóng workbook
  trong `finally`, `keep_vba=False`, `keep_links=False`, kiểm hủy giữa các vòng đọc.
- Tham số tiền tệ kiểm đúng dạng ba chữ in hoa. Nếu trống, chỉ nhận đơn vị ghi rõ
  ở phần đầu bảng hoặc định dạng cột tiền; mã phổ biến đứng riêng như VND/USD
  cũng được nhận, không coi tiêu đề STT là tiền tệ. Ký hiệu mơ hồ như `$` không
  được suy ra USD. Nhiều đơn vị mâu thuẫn thì để chưa rõ; tham số quy trình có
  ưu tiên. Chưa rõ: hai trường `gia_tri_* = null`, `tien_te_chua_ro = true`;
  JSON giữ số thập phân với `tien_te: null` theo §5.2. Không mặc định VND.
- Cảnh báo có mã/ô/mô tả: `THANH_TIEN_LECH`, `SO_DANG_CHU`, `TRUNG_KHOA`,
  nằm tại từng dòng và danh sách chung; đếm đúng số cảnh báo. Khóa trùng vẫn
  giữ công thức khóa/hậu tố gốc.
- `engine.json` chỉ đổi tên ví dụ thứ ba; hai ví dụ toàn vẹn giữ nguyên.
  `chay.py` thêm một dòng trả bytes đã kiểm trong `_doc_va_kiem` để tái dùng
  bộ chặn EX-0, không đổi hành vi toàn vẹn; phần còn lại chỉ nối doc_bang.
- Điều chỉnh các assertion EX-0/kiểm cô lập về trạng thái thật: hai hàm toàn vẹn
  chưa làm, đọc bảng đã thành công. Không bỏ qua lỗi đầu vào hay bỏ DEMO.
  Không thêm dependency. SDK 2.2.0 SHA khớp, cài offline vào `.venv` trong worktree;
  ba thư viện runtime cài bằng lock có hash từ wheel sẵn có (chỉ đọc kho wheel).

### Đối chiếu và lệch số đã đo

- Hai tệp `bang-kl-DEMO.xlsx`, `K1-K8-DEMO.xlsx`: **khớp toàn bộ dict**
  `tim_bang_chi_tiet` và `tim_so_tong_hop` với hàm nguồn trích nguyên tại RAM,
  chỉ chuyển float → Decimal và bỏ ngưỡng theo yêu cầu. Test kiểm SHA-256 nguồn
  LF trước khi chạy; LABELS lấy từ nguồn gốc. **Không có lệch giá trị/làm tròn trên
  hai DEMO chuẩn**. Đáp án JSON kiểm đủ 30 dòng, nhóm, cột, khóa, bốn kỳ KL/GT,
  đơn giá và tổng 60.000.000 VND; 1 dòng nhóm, 0 cảnh báo với bản sạch.
- Những thay đổi có chủ đích so với bản float chưa chuyển:

| Ca DEMO bổ sung | Gốc | EX-4 |
|---|---|---|
| Số nguyên 9007199254740993 | float thành 9007199254740992.0 | Giữ 9007199254740993 trong cả chi tiết và tổng hợp |
| Tổng 0, 0.5, -1, các tổng 0.125…0.875 | Bị bỏ do `abs(v) > 1` | Giữ đúng số, vị trí và nhãn |
| Số tổng hợp lưu dạng chữ `1,234.25` | Bỏ qua vì chỉ nhận int/float | Đọc 1234.25 và cảnh báo `SO_DANG_CHU` |
| bool hoặc NaN/Infinity | Có thể bị coi là số/float | Không coi là giá trị số hợp lệ |

- Ca âm `-1000000000.25`, số lớn/lẻ `2500000000.125`, số ≥ 10^9 và đơn vị
  USD/VND đi qua CoreGia đúng quy ước SDK; phép nhân 0.1 × 0.2 = 0.02 không
  tạo cảnh báo sai do sai số nhị phân. Không tự làm tròn thành tiền.
- Giới hạn vốn có: đọc giá trị công thức đã lưu của Excel, không tính lại.
  openpyxl có thể đã đổi số thập phân OOXML sang float khi nạp; `_num` lấy
  `Decimal(str(v))`, không khôi phục được độ chính xác đã mất ở parser. Ca số
  nguyên vượt 2^53 dùng XML số nguyên trực tiếp để kiểm giữ chính xác.

### Kết quả ba lệnh nghiệm thu

Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; chạy bằng `.venv/Scripts/python`.
**Đã kiểm bằng Core giả (CoreGia).**

```text
python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 1/3 ĐẠT: DEMO đọc bảng EX-4 XONG.
→ 2/3 LỖI: DEMO toàn vẹn CHUA_LAM giữ nguyên từ EX-0; mã thoát 1.
python -m pytest e_kiem_excel/tests -q
→ 64 passed in 4.87s, 0 skipped; mã thoát 0.
python e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập; EX-4 XONG, 2 DEMO toàn vẹn CHUA_LAM;
  mã thoát 0.
```

Không có bytecode/symlink trong gói. `git diff --check` mã 0. Hai tệp Python
runtime sửa/thêm và một manifest, trong giới hạn lát ~5 tệp mã.

### Cần Core / chờ lead

- **Không phát sinh cửa Core/SDK mới.** EX0-SDK-01 hiện còn 2 DEMO chưa đạt,
  giảm từ 3 xuống 2; chờ các lát toàn vẹn được gộp rồi chạy lại CLI chung.
  Không đổi hàm toàn vẹn sang thành công giả để đạt 3/3.
- Lead gộp helper chuẩn hóa sau EX-1 và mở PR; mã PR: **chờ lead mở**.
- `tong_quat` giữ `CHUA_LAM`, thuộc EX-5; không mở thêm phạm vi.

Thời gian thực tế: **0.17 giờ**, từ **18/11/2026 20:47 đến 20:57:10** (giờ Việt Nam); ước tính trong phiếu **4 giờ**.

## EX-1 — thực hiện 18/11/2026, PR: chờ lead mở

Kết luận: **Hoàn tất phần mã EX-1; chưa đạt điều kiện nghiệm thu chung cả gói**:
CLI còn DEMO đọc bảng `CHUA_LAM`, thuộc EX-4 đang làm trong worktree khác.
Đã kiểm bằng Core giả (CoreGia); chưa nối Core thật. Schema chờ lead duyệt trong PR.

### Đã làm

- Đúng 5 tệp mã runtime sửa/thêm: `chay.py`, `tham_chieu.py`, `so_do.py`,
  `chuan_hoa.py`, `kiem_tra.py`. Chép lõi từ các đoạn nguồn trong phiếu §3.1;
  không viết lại thuật toán. Bảng nguồn→đích ghi trong `goi/e_kiem_excel/NGUON.md`.
- SoDo nạp hai workbook từ BytesIO, không có `self.path`, không chạy macro,
  không mở tệp liên kết; `self.ngoai` chỉ giữ tên tệp. Đóng workbook trong `finally`,
  kể cả khi hủy việc. Lỗi parser sau lớp chặn ZIP/XML trả `TEP_HONG` với câu cố định.
- `nfc/bo_dau` giữ quy tắc nguồn; `so/num` dùng Decimal, `num` từ chối số không hữu hạn.
  K2/K3 cộng giá trị bằng Decimal; không đổi qua float khi tạo JSON hoặc tiền.
  `so_tien` dùng `format(d, "f")`, kèm mã tiền tệ; chưa rõ đơn vị trả null toàn trường.
- K1–K6 nhận SoDo/tham số bước; kiểm hủy trước/sau từng kiểm. K6 bỏ câu/tài liệu
  hợp đồng viết cứng. K2 tạm ghi "Chưa phân nhóm", tài liệu nhóm để trống, chờ EX-2.
- `excel.toan_ven@1` trả đủ 11 trường theo manifest. K7/K8, bộ nhóm và báo cáo
  chưa chạy nên trường tương ứng rỗng/null, có cảnh báo rõ trong JSON. K6 vẫn liệt kê
  hằng số nhưng chưa phát cờ theo cây K7. `da_tinh_lai` kiểm tất cả ô thiếu giá trị lưu,
  không suy từ việc K1 có bật cờ trên ngưỡng 50% hay không.
- JSON UTF-8 tải qua `viec.tai_tep_ra`, không ghi kết quả runtime xuống máy;
  số nghiệp vụ/số đếm dạng chuỗi thập phân, giữ `phien_ban = 1` theo cấu trúc §5.1.
  Trần 20 MiB theo byte; vượt thì từ chối, không cắt bớt.
- `tests/schema/toan_ven.schema.json` và README khóa tên/kiểu từng cột EX-1;
  bổ sung `k1_so_ten_loi`, `k4_khac_ban_hien` để giữ thông tin nguồn. `gia_tri`
  giữ số/nội dung ô, không tự suy đơn vị tiền. EX-2/EX-3 mở phần K7/K8 và trình lead
  duyệt cùng lát tương ứng. Không đổi API/SDK.
- Cập nhật kỳ vọng test EX-0 khi năng lực toàn vẹn đã chạy. Bộ kiểm độc lập cho
  `re.compile` của regex cố định trong mã gốc, vẫn chặn `compile/eval/exec` chạy mã.
  Kiểm tiến trình cô lập dùng `-I -B -S`, không Core/shim, không mạng/tiến trình ngoài.
- Không tạo/sửa `doc_bang.py`. Kiểm bằng AST xác nhận hàm `doc_bang` giữ nguyên;
  hai khai báo năng lực và DEMO đọc bảng trong `engine.json` giữ nguyên. Chỉ đổi nhãn
  hai DEMO toàn vẹn. Hàm đọc chung thêm giá trị trả bytes để dùng ở EX-1.

### Tương đương và sai khác cần lead xem trong PR

`tests/test_tuong_duong.py` kiểm SHA-256 cả hai `ma-nguon/*.py`, chuẩn hóa
CRLF→LF **chỉ trong RAM**, rồi import đúng mã gốc trong test. Không sửa nguồn.

| Phép so | Kết quả thật |
|---|---|
| Cùng phạm vi K1–K6, tệp `K1-K8-DEMO.xlsx` | Khớp toàn bộ **7** phát hiện về mức/mã/ô: 3 Cao, 4 Trung bình, 0 Kiểm soát |
| Cùng phạm vi K1–K6, `sach-DEMO.xlsx` | Khớp: 0 phát hiện |
| Cùng phạm vi K1–K6, `thieu-v-DEMO.xlsx` | Khớp: 1 Kiểm soát K1 ở DEMO; `da_tinh_lai = false` |
| Cùng phạm vi K1–K6, `bang-kl-DEMO.xlsx` | Khớp: 0 phát hiện |
| So với `KiemTra.chay()` gốc chạy đủ K1–K8 trên `K1-K8-DEMO.xlsx`, lọc K1–K6 | **Lệch đúng 1**: EX-1 thiếu `Trung bình / K6 / BTH!J21`, do chưa chạy K7 để xác định cột thuộc cây. Không sửa cho khớp |
| Cấp cùng cây K7 của mã gốc **chỉ trong test** rồi chạy K6 | Bảng hằng số và phát hiện K6 khớp; mô tả/tài liệu đã bỏ nghiệp vụ viết cứng theo phiếu |
| Sáu biểu thức DEMO có tham chiếu tuyệt đối/tương đối, range, sheet có dấu/nháy, chuỗi, file ngoài, tỷ lệ | Các hàm tham chiếu/mẫu/hằng số khớp mã gốc |

Hai khác biệt dữ liệu bổ sung đúng phạm vi chuyển: tên liên kết ngoài bỏ thư mục;
K2 chưa gắn nhóm/tài liệu nguồn tới EX-2. Tổng giá trị dùng Decimal thay float theo phiếu.
Mã gốc có thể hạ mức liên kết ngoài sau K7; EX-1 chưa xếp lại theo cây, nên liên kết
đang dùng giữ mức K1 gốc trước K7. Bộ DEMO hiện không có sai khác mức từ nhánh này.

### Kết quả kiểm cuối

Chạy bằng `.venv/Scripts/python` của worktree, `PYTHONDONTWRITEBYTECODE=1`, UTF-8.
SDK 2.2.0 cài từ wheel trong repo, SHA-256 khớp bản phát hành. Ba thư viện runtime
cài offline từ wheel EX-0 bằng lock có hash; không tải mạng, không đổi lock.

```text
python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 2/3 ĐẠT: hai DEMO excel.toan_ven@1 XONG.
→ 1/3 LỖI: DEMO excel.doc_bang@1 trả CHUA_LAM (EX-4); mã thoát 1.

python -m pytest e_kiem_excel/tests -q
→ 62 passed in 2.61s, 0 skipped; mã thoát 0.

python e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập;
  CoreGia: 2/2 DEMO toàn vẹn XONG, đọc bảng CHUA_LAM (EX-4); mã thoát 0.
```

Test thêm đạt: Decimal `2.5E+9`, `-1234567890.125`, `0.00125` qua bộ kiểm
`so_tien` của SDK/CoreGia; số không hữu hạn; lỗi workbook đúng `TEP_HONG`, không
traceback/chi tiết lỗi; hủy sau K1 không chạy K2 và đóng workbook; liên kết ngoài
đang dùng/không dùng, không lộ thư mục; trần JSON ở đúng byte và vượt 1 byte.

Kiểm thêm JSON Schema bằng **jsonschema 4.26.0 đã có trên máy, chỉ dùng công cụ kiểm**:
`Draft202012Validator.check_schema` đạt; 4/4 kết quả DEMO thật hợp schema.
Không thêm thư viện này vào runtime hoặc dependency của pytest. Pytest dùng bộ kiểm
stdlib cho tập từ khóa schema đã khai, có ca dữ liệu sai phải bị từ chối.

`git diff --check` mã 0; không sửa `ma-nguon/`, SDK, `_chung/`, mã Core hoặc năng lực
EX-4; không bytecode/symlink trong gói. Test viết tương thích Linux, **chưa chạy Linux**
trong phiên Windows này. Không commit/push; lead nhận worktree để commit/mở PR.

Không phát sinh "Cần Core / Chờ Anh" mới. Phần cần lead: duyệt schema và sai khác
đã liệt kê; ghép EX-4 rồi chạy lại CLI toàn gói.

Thời gian thực tế EX-1: **0,24 giờ**, từ **18/11/2026 20:47 đến 21:01:10** (giờ Việt Nam); ước tính trong phiếu: **6 giờ**. PR: **chờ lead mở**.

## EX-5 — thực hiện 18/11/2026, PR: chờ lead mở

Kết luận: **Đạt phạm vi EX-5 và ba lệnh nghiệm thu chung trên worktree này.**
Đã kiểm bằng Core giả (CoreGia), chưa nối Core thật. Không commit/push.

### Đã làm

- `doc_tong_quat.py` đọc khuôn `{phien_ban, cot[{ma, tu_khoa, bat_buoc, kieu}], dong_dung}`;
  bốn kiểu `van_ban/so/so_tien/ngay`, cột bắt buộc/tùy chọn, tiêu đề nhiều tầng/ô gộp,
  dòng nhóm/dòng dừng. Dòng thiếu cột bắt buộc giữ trong JSON với cảnh báo, không
  tính vào số dòng dữ liệu. Sai kiểu ô trả null và cảnh báo; không cắt dữ liệu ngầm.
- Khuôn sai cấu trúc, phiên bản/kiểu/khóa lạ, khóa JSON trùng, mã cột trùng,
  từ khóa không hợp lệ, vượt trần → `THAM_SO_KHONG_HOP_LE`. Dùng nguyên
  `bo_nhom.doc_json`, `kiem_tu_khoa`, `khop_tu_khoa(tu, van_ban)` của EX-2,
  không tạo thuật toán từ khóa thứ hai. Tệp chung nhận từ worktree EX-2, SHA-256
  `319f034694ab3dacf4c8ea6f628ddecb80a5e67ffdb67d681c804d3b50488255`.
- Chỉ phần `excel.doc_bang@1` trong `chay.py` được nối thêm nhánh; manifest chỉ thêm
  hai DEMO thuộc năng lực đọc bảng. Không sửa `kiem_tra.py`, `so_do.py`,
  `tham_chieu.py` hoặc năng lực `excel.toan_ven@1` đang thuộc EX-2.
- Ba helper EX-4 `_nfc/_bo_dau/_num` nay là import trực tiếp từ `chuan_hoa.py` của
  EX-1. Không thêm/sửa hàm nào trong `chuan_hoa.py`. Toàn bộ test EX-1/EX-4 xanh;
  chỉ đổi ca cũ chờ EX-5 từ `CHUA_LAM` thành lỗi thiếu khuôn đúng nghiệp vụ.
- Hai DEMO OOXML/ZIP tất định, có `<f>` và `<v>` cho công thức; script sinh ngoài gói,
  đáp án độc lập trong `dap-an.json`, SHA-256 trong `bam-fixture.json`:

| Mẫu | Kết quả đối chiếu đáp án |
|---|---|
| Bảng giá thành DEMO | 2 dòng dữ liệu, 1 dòng nhóm, 0 cảnh báo; tiêu đề 2 tầng có ô gộp, cột tùy chọn vắng; Decimal số âm/số 0, đơn vị VND, ngày ISO |
| Bảng báo giá DEMO | 2 dòng dữ liệu, 0 dòng nhóm, 1 cảnh báo số lưu dạng chữ; cột rời/đổi sheet, từ khóa `#` và `=`, mã `0001`/`0002`, số nguyên 9007199254740993 và tiền 2500000000.125 USD giữ đúng |

- Giữ tiền/ngày theo §4.3/§5.2: Decimal → chuỗi thập phân, tiền kèm đơn vị, chưa rõ
  thì JSON giữ số nguồn với `tien_te: null` như EX-4; hai trường giá trị hợp đồng/đề nghị
  của khuôn tổng quát luôn null. Ngày Excel hoặc chuỗi ISO/dd/mm/yyyy xuất ISO.
- Chỉ RAM, đóng workbook trong `finally`, kiểm hủy giữa các vòng, trần JSON đầu ra
  20 MiB; không thêm dependency. SDK 2.2.0 cài từ wheel repo, SHA-256 khớp
  `SHA256SUMS.txt`; ba thư viện runtime cài offline từ wheel sẵn có bằng lock có hash.
- Cập nhật README, CHANGELOG, NGUON; chi tiết JSON động và quy tắc chọn bảng ghi
  trong README. Bốn tệp Python runtime sửa/thêm (gồm tệp chung `bo_nhom.py`) và
  một manifest, trong giới hạn lát. Không sửa mã nguồn tham chiếu, SDK/Core, `_chung/`.
- Cố định JSON fixture về LF trong script sinh và `.gitattributes`, chuẩn hóa xuống dòng
  của bản sao bộ nhóm fixture trước khi băm; tránh hash khác giữa Windows/Linux.

### Kết quả ba lệnh nghiệm thu

Chạy bằng `.venv/Scripts/python`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.
**Đã kiểm bằng Core giả (CoreGia).**

```text
python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 5/5 ĐẠT (2 toàn vẹn EX-1, 1 bảng KLGT EX-4, 2 bảng tổng quát EX-5); mã thoát 0.
python -m pytest e_kiem_excel/tests -q
→ 144 passed in 2.74s, 0 skipped; mã thoát 0.
python e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập; 5/5 DEMO XONG; mã thoát 0.
```

55 ca EX-5 bổ sung: hai đáp án; cấu trúc sai; biên đúng/vượt 30 cột, 200 từ khóa,
32 KiB theo byte UTF-8; JSON trùng khóa/không chuẩn/lồng sâu; matcher dùng cùng hàm;
tiêu đề mơ hồ; thiếu giá trị/sai kiểu; tiền tệ thiếu/tham số/định dạng ô; ngày không hợp
lệ/ngày Excel; hủy hoặc lỗi đóng workbook; biên đúng/vượt trần JSON; lỗi không lộ đầu vào.
Kiểm độc lập không có `kho_tri_thuc.*`, bytecode/symlink; `git diff --check` mã 0.
Phiên này chạy Windows; test viết tương thích Linux, chưa chạy Linux.

### Lệch khỏi phiếu / chi tiết triển khai chốt trong EX-5

- §4.2 chỉ nêu trần JSON 32 KiB; áp thêm **30 cột, tổng 200 từ khóa kể cả dòng dừng**
  theo mức cùng bộ nhóm §4.1.1. Yêu cầu ít nhất một cột bắt buộc, mã cột duy nhất
  dạng `[a-z][a-z0-9_]{0,63}`. Không đổi API/SDK hay trường ra đã khóa.
- Dò tiêu đề bắt đầu trong 40 dòng đầu, ghép tối đa 4 tầng. Chọn nhiều cột khớp nhất,
  rồi ít tầng nhất, rồi dòng trên cùng; hòa giữa sheet thì sheet trước. Không tự chọn
  khi từ khóa khớp nhiều cột. JSON động để giá trị theo mã trong `dong[].gia_tri`.
- `dong_dung` xét ô có giá trị ngoài cùng bên trái của các cột đã nhận diện. Một ô chữ
  duy nhất ở cột văn bản, khi thiếu cột bắt buộc, được coi là dòng nhóm; quy ước này
  là heuristic và đã ghi README để module chọn khuôn phù hợp.

### Cần Core / Chờ Anh mới phát sinh

- Không có cửa Core/SDK hoặc câu chặn mới. Vấn đề MIME Core thật có từ EX-0 giữ nguyên.
- Lead gộp EX-2/EX-5 cần giữ **một** `bo_nhom.py` chung với giao diện trên;
  snapshot EX-5 trùng bytes EX-2 lúc nhận. Không lấy toàn bộ `chay.py`/`engine.json`
  của nhánh này đè phần năng lực toàn vẹn EX-2.
- PR: **chờ lead mở**; đề xuất tiêu đề `[e_kiem_excel] EX-5 — Đọc bảng theo khuôn tổng quát`.

Thời gian thực tế EX-5: **0.20 giờ**, từ **18/11/2026 21:48 đến 21:59:58** (giờ Việt Nam); ước tính trong phiếu: **4 giờ**. PR: **chờ lead mở**.


## EX-2 — thực hiện 18/11/2026, PR: chờ lead mở

Kết luận: **Đạt phạm vi EX-2 và ba lệnh nghiệm thu chung**. Đã kiểm bằng Core giả
(CoreGia); chưa nối Core thật. K8/báo cáo Excel thuộc EX-3; khuôn tong_quat thuộc
EX-5 đang làm ở worktree khác. Không commit/push.

### Đã làm

- Ba tệp Python runtime: sửa `kiem_tra.py`, phần toàn vẹn trong `chay.py`,
  thêm `bo_nhom.py`; manifest chỉ đổi hai DEMO toàn vẹn, trong giới hạn ~5 tệp mã.
  Chuyển K7 và `_xep_lai` từ nguồn đã ghim; thứ tự K7 → K6 → xếp lại mức cờ.
- Ô đích kiểm fullmatch, tên sheet tồn tại, giới hạn XFD/1048576, hỗ trợ `$` và
  nháy đơn Excel. Sai → THAM_SO_KHONG_HOP_LE. Ưu tiên ô đích; nếu trống, tìm
  theo nhãn module trên sheet hiện (80 dòng đầu, 12 cột đầu; số đầu trong sáu ô
  bên phải). Số 0, âm, lẻ đều giữ; không có đích → đúng một mục Kiểm soát K7.
- LABELS/tim_so_tong_hop Decimal đã có từ EX-4: **không sửa doc_bang.py**.
  `_tim_o_dich` chuyển cùng thuật toán quét với nhãn tùy biến và num Decimal
  của EX-1; không sao chép LABELS nghiệp vụ vào K7. Năng lực/hàm/DEMO đọc bảng
  trong chay.py và engine.json so AST/JSON với HEAD giữ nguyên.
- Bộ nhóm kiểm chặt kiểu/cấu trúc/khóa trùng/phien_ban, vùng, nhóm trùng,
  danh sách điều kiện, từ khóa; đúng trần 30 nhóm/200 từ khóa/32768 byte UTF-8
  nhận được, vượt một đơn vị → THAM_SO_KHONG_HOP_LE. JSON NaN/Infinity bị từ chối.
- Từ khóa chứa chuỗi, `=tu` nguyên từ Unicode, `#` một hoặc nhiều chữ số;
  bỏ dấu/viết thường/gộp khoảng trắng. Các ký tự regex là chữ nguyên văn;
  không thực thi regex đầu vào. `#` dùng bảng trạng thái, không backtracking.
  API dùng chung cho EX-5: kiem_tu_khoa(tu), khop_tu_khoa(tu, van_ban).
- Không bộ nhóm: lá Chưa phân nhóm, so_ngoai_nhom null, không cờ Ngoài nhóm.
  Có bộ: nhóm đầu khớp, tài liệu theo nhóm; K2/K6 cũng lấy tài liệu từ bộ.
  Băm bộ nhóm là SHA-256 JSON UTF-8 chuẩn hóa; không lưu bộ lên máy/ngăn.
- Fixture tests/demo/bo_nhom_review_ttkl.json đã có từ EX-0: tái dùng, test so
  đúng nguyên object Phụ lục A, đủ tám mã (7 nhóm nghiệp vụ có nhánh 5b).
  Không chép fixture vào goi/.
- JSON K7 giữ đủ cột nguồn và boolean la; số chuỗi thập phân, tổng dải Decimal,
  đặt precision theo toán hạng. Schema mở cho K7, chờ lead duyệt trong PR.
  Đã cập nhật CHANGELOG, README, NGUON và schema README.

### Kết quả tương đương và các lệch đo riêng

Test kiểm SHA-256 hai mã nguồn (CRLF→LF chỉ trong RAM) trước khi import bản gốc.
So **mọi cột cây và nhóm/tài liệu từng lá**, số theo giá trị Decimal; phát hiện
so mức/mã/ô với KiemTra.chay() gốc đầy đủ rồi lọc K8 khỏi phạm vi EX-2.

| DEMO / ô đích | Nút K7 | Lá nhập tay/nhóm nhập tay | Ngoài nhóm | Phát hiện K1–K7 |
|---|---:|---:|---:|---|
| K1-K8-DEMO.xlsx / BTH!J39 | 13 | 6 | 1 | 4 Cao, 5 Trung bình, 0 Kiểm soát; khớp gốc |
| bang-kl-DEMO.xlsx / BTH!J39 | 6 | 2 | 0 | Không cờ; khớp gốc |
| sach-DEMO.xlsx / DEMO!B3 | 2 | 1 | 1 | 1 Cao K7; khớp gốc khi truyền bộ nhóm |
| thieu-v-DEMO.xlsx / DEMO!B3 | 1 | 0 | 0 | 1 Kiểm soát K1; khớp gốc |

Tổng **22 nút, 9 lá**, không lệch cấu trúc/giá trị/nhóm trên bốn DEMO này sau
chuẩn hóa tên Ngoài nhóm. Cờ **Trung bình / K6 / BTH!J21** từng thiếu ở EX-1
nay khớp, so_trong_cay = "1"; không còn lệch K1–K7 về mức/mã/ô trên bộ chuẩn.
Hai cờ K8 của tệp lỗi vẫn thuộc EX-3, chưa chạy trong engine.

| Chỗ Phụ lục A yêu cầu đo riêng | Kết quả |
|---|---|
| Nhóm 6 xét cả nhãn dòng trong khong_co gia tri | Trên bộ bốn DEMO chuẩn: 0 lệch. Ba ca bổ sung (thuế/VAT/GTGT, nhãn có Giá trị): gốc 3/3 vào nhóm 6; Phụ lục A 3/3 ra Ngoài nhóm. Có kiểm lá K7 thật cho VAT + nhãn Giá trị DEMO |
| dai/rong/cao chứa chuỗi | Báo cáo DEMO / Trong DEMO / Đại diện DEMO: cả gốc và EX-2 đều 3/3 vào 5 KL / diễn giải, 0 lệch. Có kiểm lá K7 thật cho Báo cáo DEMO. Chưa đổi thành =dai/=rong/=cao |

Lệch có chủ đích và quyết định tạm:

- Tên Ngoài 7 nhóm - cần giải thích → Ngoài nhóm — cần giải thích theo phiếu.
  Không coi đổi nhãn này là lệch phân loại. Không bộ nhóm thì dùng hành vi mới
  Chưa phân nhóm; ô đích không còn tự tìm nhãn thanh toán nếu module không truyền.
- Tổng dải 2.000.000 nguồn float ghi 2000000.0; EX-2 Decimal ghi 2000000,
  **chênh giá trị = 0**. Ca 0.1 + 0.2 - 1000000000.125 giữ -999999999.825;
  ca 10^30 + 1 - 10^30 giữ 1, không mất chữ số do precision mặc định.
- Giữ trần cây nguồn 14 tầng/12 mẫu mỗi dải nhưng **từ chối VUOT_GIOI_HAN thay
  vì cắt ngầm** theo AGENTS.md §4.6. Trần tạm bổ sung 100.000 nút,
  250.000 ô/dải, 500.000 lượt đọc ô; EX-6 đo lại sức chứa/thời gian trên bản đủ.
- Cây vẫn gom dải theo mẫu, chọn một ô đại diện/mẫu và gom ô nhập tay như nguồn;
  so_ngoai_nhom đếm **nút nhập tay** ngoài nhóm, đúng cách phát cờ nguồn,
  không phải kiểm kê từng ô trong một nút dải.

### Kết quả ba lệnh nghiệm thu

Dùng .venv/Scripts/python trong worktree, PYTHONUTF8=1 và
PYTHONDONTWRITEBYTECODE=1. SDK 2.2.0 cài offline từ wheel repo, SHA-256
0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984 khớp SHA256SUMS.
Ba dependency runtime cài offline bằng lock có hash từ wheel EX-0 (chỉ đọc).
Không tải mạng, không thêm dependency. **Đã kiểm bằng Core giả (CoreGia).**

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 3/3 ĐẠT; mọi ví dụ chạy thử DEMO đều đạt; mã thoát 0.
.venv/Scripts/python -m pytest e_kiem_excel/tests -q
→ 163 passed in 2.83s, 0 skipped; mã thoát 0.
.venv/Scripts/python e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập;
  đã kiểm bằng Core giả (CoreGia): 3/3 DEMO XONG (K1–K7, đọc bảng EX-4);
  mã thoát 0.
```

Có kiểm ca hủy trong K7, chu trình, sheet thiếu, trống/chữ, dải và nhiều mẫu,
liên kết ngoài thuộc cây/hạ mức cột phụ (khớp gốc), không lộ thư mục, giới hạn
độ sâu/dải/mẫu, tham số sai qua CoreGia. Kiểm độc lập không bytecode/symlink,
không import Core, không mạng/tiến trình ngoài. Test tương thích Linux;
**chưa chạy Linux** trong phiên Windows này. git diff --check mã 0.

### Cần Core / Chờ Anh mới phát sinh

Không có. EX0-SDK-01 không còn chặn CLI bản hiện tại; EX0-SDK-02 MIME/Core thật
vẫn giữ. Lead duyệt schema và các lệch đã nêu, ghép EX-5 dùng chung matcher,
commit và mở PR. Không sửa doc_bang.py, ma-nguon/, SDK, _chung/ hoặc mã Core.

Thời gian thực tế: **0.23 giờ**, từ **18/11/2026 21:47:00 đến 22:01:03** (giờ Việt Nam); ước tính trong phiếu **4 giờ**. PR: **chờ lead mở**.


## EX-3 — K8 và báo cáo Excel trong RAM — Xong 19/11/2026

PR: **chờ lead mở**. Nhánh `codex/e_kiem_excel-ex-3`; không commit/push.
**Đã kiểm bằng Core giả (CoreGia)**, chưa nối Core thật.

### Đã làm và phạm vi

- Chuyển K8, `_lech`, `_nguon` từ `toan_ven.py` 605–736; dùng trực tiếp
  `doc_bang.tim_bang_chi_tiet` đã có của EX-4. K8 chỉ chạy khi công tắc là true.
  Giữ xếp lại mức cờ sau K8; không bắt nuốt hủy/lỗi giới hạn.
- `bao_cao.py` chuyển kiểu ô/`_sheet`/`ghi` từ nguồn 764–866, giữ độ rộng, màu,
  freeze panes và cột. Bật K8: đủ 15 sheet; tắt: 12 sheet, không tạo ba sheet K8.
  Công thức nguồn là chuỗi hiển thị. Báo cáo chỉ ghi vào BytesIO, tải bằng
  `viec.tai_tep_ra`, đóng workbook trong finally kể cả khi hủy.
- Hoàn tất 11 trường ra §4.1, có `tep_bao_cao`; cập nhật hai DEMO toàn vẹn
  có/không bộ nhóm. Giữ nguyên DEMO và năng lực `excel.doc_bang@1`.
- Tiền báo cáo là chuỗi số chính xác kèm đơn vị đã xác định; thiếu/mâu thuẫn
  đơn vị thì để trống ô tiền. Dùng lại `_tim_tien_te` của EX-4. JSON K8 giữ
  số thập phân + mã tiền hoặc null; mở schema ngoài gói, chờ lead review.
- Chỉ sửa 3 tệp Python runtime (`kiem_tra.py`, `bao_cao.py`, `chay.py`) và
  phần DEMO toàn vẹn trong manifest; không sửa `doc_bang.py`, `bo_nhom.py`,
  mã nguồn tham chiếu, SDK, `_chung/` hay mã Core. Không thêm dependency.

### Kết quả kiểm và tương đương

- So mọi cột `nguon`, `tang`, `tang_kt`, sheet/cột KL và mức/mã/ô K8 với
  mã gốc đã kiểm SHA-256: hai DEMO chuẩn × 30 dòng và một bảng bổ sung 11 dòng,
  tổng **71 dòng**, khớp giá trị/phân loại/đường đi/cờ. K8 trên tệp cài lỗi
  khớp đáp án: Cao tại BTH!E và BTH!G.
- Bộ bổ sung kiểm Nhập tay, Bằng KL HĐ, Tỷ lệ × KL HĐ, diễn giải/công thức,
  Nguồn trống, Link lệch dòng, IF chặn vượt HĐ, qua sheet ẩn, File ngoài,
  hệ số × ô khác; có GT tính dự phòng khi thiếu cột giá trị.
- Báo cáo tải qua CoreGia mở lại bằng openpyxl, đúng tên/thứ tự sheet,
  freeze panes/màu, không có ô công thức thực thi; đủ trường ra và schema.
  Kiểm bốn tổ hợp bật/tắt K8 × có/không bộ nhóm; công tắc tắt không gọi bộ đọc K8.
- Kiểm VND/USD, thiếu hoặc xung đột đơn vị; số lớn 10^30+1, số âm/lẻ,
  hủy K8, hủy lúc dựng báo cáo, ô báo cáo quá dài và đường truy nguồn quá sâu.

Môi trường: Python 3.13.14, .venv riêng (`include-system-site-packages = false`),
SDK 2.2.0 từ wheel repo, SHA-256
`0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`
khớp SHA256SUMS. Dependency runtime cài offline bằng lock có hash từ wheel
EX-0 chỉ đọc: openpyxl 3.1.5, et_xmlfile 2.0.0, defusedxml 0.7.1.
Không tải mạng. Chạy với PYTHONUTF8=1 và PYTHONDONTWRITEBYTECODE=1.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 3/3 ĐẠT; mọi ví dụ chạy thử DEMO đều đạt; mã thoát 0.
.venv/Scripts/python -m pytest e_kiem_excel/tests -q
→ 183 passed in 11.20s; 0 skipped; mã thoát 0 (20 ca EX-3 mới).
.venv/Scripts/python e_kiem_excel/tests/kiem_doc_lap.py
→ [ĐẠT] AST, cây gói, import cô lập; đã kiểm bằng Core giả (CoreGia):
  3/3 DEMO XONG (toàn vẹn K1–K8, đọc bảng EX-4); mã thoát 0.
```

`git diff --check` mã 0. Không có bytecode trong gói. Chưa chạy Linux trong
phiên Windows này; test không dùng API Windows. Đo sức chứa/thời gian bản đủ
và kiểm máy sạch đa nền tảng tiếp tục ở EX-6 theo phiếu.

### Lệch nguồn / quyết định tạm

- Giữ `round` từng dòng K8 như nguồn; thay phép toán/tổng float bằng Decimal.
  71 dòng DEMO đối chiếu không lệch giá trị. Ca 10^30+1 giữ chính xác chữ số
  mà float không biểu diễn được. Mô tả tiền thêm đơn vị hoặc bỏ số khi chưa rõ.
- Hàm nhận diện số riêng cho K8 nhận Decimal; không đổi `la_so` dùng chung
  của các lát trước. Ngưỡng 1e-6/1e-9 giữ nguyên ý nghĩa dưới dạng Decimal.
- Thiếu bảng/cột KL: một mục Kiểm soát K8 bằng câu cố định, không lộ exception;
  không tuyên bố đã kiểm đủ nguồn. Lỗi khác/hủy/giới hạn được truyền lên SDK.
- Theo AGENTS.md §4.6, truy nguồn vượt 8 bước từ chối VUOT_GIOI_HAN thay cho
  nguồn trả Khác khi dừng; ô Excel vượt 32.767 ký tự từ chối thay vì cắt ngầm.
- Báo cáo bỏ tên tệp/đường dẫn khỏi tiêu đề, ghi theo bộ nhóm module thay
  câu cố định 7 nhóm. Giữ số phiên bản 0.1.0 theo các lát đang ghép; lead chốt
  phiên bản phát hành tại EX-6.

### Cần Core / Chờ Anh mới phát sinh

Không có. Giữ ghi nhận EX0-SDK-02 về MIME/Core thật. Lead review schema K8,
ngưỡng dừng truy nguồn và ghép EX-5 theo phạm vi đã phân công; commit/mở PR.

Thời gian thực tế theo mốc lead giao: **1.41 giờ**, từ **19/11/2026 08:06:00 đến 09:30:35** (giờ Việt Nam); ước tính trong phiếu **4 giờ**. PR: **chờ lead mở**.

## EX-6 — thực hiện 19/11/2026, PR: chờ lead mở

Kết luận: **Đạt ba lệnh kiểm và cài sạch cục bộ** trên Windows/Python 3.13.14;
đã chuẩn bị CI Linux/Python 3.11, chưa có kết quả CI vì không commit/push.
**Đã kiểm bằng Core giả (CoreGia)**, chưa nối Core thật. Bản gói **0.1.1**.

### Đã làm

- Lock chỉ giữ openpyxl 3.1.5, et_xmlfile 2.0.0, defusedxml 0.7.1: cả ba đều dùng.
  Không thêm dependency runtime. Cài wheel SDK 2.2.0 offline, SHA khớp bộ phát hành.
  Kiểm phiên bản/cờ DEFUSEDXML; pip check chỉ được thiếu đúng hai dependency
  phần module SDK (cryptography/jsonschema), theo hướng dẫn SDK --no-deps.
- NGUON.md tổng hợp đủ đường/dòng toan_ven/master_hd → tệp đích, phần không lấy,
  nguồn/giấy phép thư viện và mã mới. SHA bytes nguyên trạng **21/21 tệp gói**;
  NGUON.md liệt kê 20 tệp khác, SHA của chính nó nằm ngoài gói tại
  `tests/demo/bam-goi.json`, tránh tự tham chiếu. Test phát hiện bytes bị sửa.
- ZIP thử bằng `kiem_ten/doc_json/kiem_ke_sql/tao_zip` của chính
  `_chung/cong-cu/dong_goi.py`; kiểm tên, đọc ZIP so từng byte với worktree.
  Artifact: `.dong-goi-thu/e_kiem_excel-0.1.1-EX6-worktree.zip`, SHA-256
  `04b01cf47629dba57e71265466cd06e25a9ce6854557d3997c3bfd4dc08d200b`.
  Kiểm kê rời `.dong-goi-thu/KIEM-KE-EX6.json`. Đây là bản thử chưa commit.
- Cài venv mới tại `.venv/kiem-sach-EX6`, wheel offline có hash, trích riêng gói
  từ chính ZIP thử, không mang mã tham chiếu/shim vào cây kiểm. SHA 21/21,
  CLI 5/5, kiểm độc lập mã 0. **Không chạy KIEM-MAY-SACH.cmd.**
- `kiem_may_sach.sh`: Python 3.11, wheel offline, chuẩn hóa đường wheel tương đối,
  kiểm SHA/phiên bản, copy riêng gói, CLI 5/5 và kiểm độc lập; dọn môi trường tạm.
  Workflow `.github/workflows/ex-6-may-sach.yml` chạy ubuntu-latest/Python 3.11,
  tải wheel theo lock có hash rồi cài offline, chạy đủ ba lệnh. Đã kiểm cú pháp
  shell bằng `bash -n`; **chưa chạy trên Linux** do máy này chưa cài WSL.
- Sửa một tệp Python runtime `bao_cao.py`: openpyxl.save(BytesIO) vẫn ghi XML
  worksheet tạm trên đĩa; dùng WorksheetWriter(out=BytesIO) và ExcelWriter
  để toàn bộ báo cáo ở RAM, đóng XML trong finally. Test chặn tạo tệp tạm,
  mở lại đủ 15 sheet, K8/JSON vẫn đúng. Dùng API nội bộ của openpyxl **đã ghim 3.1.5**;
  khi nâng thư viện phải kiểm lại lớp ghi. Tăng manifest lên 0.1.1, không đổi API v1.

### Số đo thật trên runtime cuối

Lệnh: `.venv/Scripts/python -B e_kiem_excel/tests/do_hieu_nang.py --ra e_kiem_excel/tests/demo/so-do-hieu-nang-EX6.json`.
Máy: Windows-11-10.0.26200-SP0; Python 3.13.14; Intel64 Family 6 Model 154 Stepping 4, GenuineIntel; 12 CPU logic;
SDK 2.2.0/openpyxl 3.1.5/defusedxml 0.7.1, không lxml. Phiên đo từ
`2026-11-19T15:01:56.425639+07:00` đến `2026-11-19T15:05:17.261646+07:00`; raw JSON chứa SHA từng input và
SHA mọi tệp runtime để chứng minh phép đo trên mã cuối.

Mỗi mẫu/năng lực chạy **3 tiến trình riêng**, tổng **36/36 XONG**. Thời gian
perf_counter bao trọn CoreGia.chay_thu: kiểm ZIP/XML, nạp workbook, xử lý,
JSON/báo cáo và nộp tệp vào CoreGia. RSS đỉnh là PeakWorkingSetSize gồm cả
Python/SDK/input/output; không tracemalloc. Sinh DEMO/import module và kiểm
đáp án sau chạy nằm ngoài đồng hồ. Không chủ động chạy pytest/cài venv đồng
thời trong lượt đo cuối; thời gian vẫn chịu tải chung của máy.

| DEMO | Byte tệp / MiB giải nén / ô thực / ô vùng | Toàn vẹn: trung vị / lớn nhất (s) | Toàn vẹn: RSS đỉnh (MiB) | Đọc bảng: trung vị / lớn nhất (s) | Đọc bảng: RSS đỉnh (MiB) |
|---|---|---:|---:|---:|---:|
| 1 MiB | 1,049,804 / 2.057 / 9,325 / 9,512 | 0.667 / 0.708 | 54.10 | 0.269 / 0.394 | 45.53 |
| 5 MiB | 5,240,493 / 10.267 / 44,925 / 45,112 | 3.375 / 3.384 | 118.59 | 1.196 / 1.211 | 77.12 |
| 10 MiB | 10,477,707 / 20.543 / 89,405 / 89,592 | 6.504 / 6.976 | 192.79 | 2.483 / 3.067 | 115.03 |
| 20 MiB | 20,951,711 / 41.109 / 178,345 / 178,532 | 12.163 / 12.719 | 342.29 | 4.760 / 4.915 | 190.88 |
| Sát trần ô/vùng | 575,218 / 7.242 / 249,421 / 499,552 | 8.495 / 8.498 | 343.56 | 3.080 / 3.578 | 139.79 |
| Sát trần giải nén | 329,594 / 127.847 / 4,534 / 4,702 | 1.712 / 2.205 | 300.70 | 1.099 / 1.166 | 170.00 |

Mẫu 1/5/10/20 MiB có dung lượng thực lệch dưới 0,2% so mốc; 1 MiB thực hơi
lớn hơn mốc do ghép bảng KL. Không đệm ZIP bằng tệp lạ: sheet tải có 15 chuỗi
DEMO hex khó nén và 5 công thức có giá trị lưu mỗi dòng, cộng bảng KL/Nguon
DEMO 30 hạng mục. Toàn vẹn bật K8, ô đích BTH!J39 và bộ nhóm Phụ lục A, có
assert K7/K8 thực sự chạy; đọc bảng dùng xay_dung_klgt, VND, assert đủ 30 dòng.
Mẫu mật độ có 249.421 ô thực và 499.552 ô vùng; mẫu giải nén có XML ô chứa
chuỗi DEMO dưới 32.767 ký tự, 127,847 MiB giải nén. Hai mẫu đều qua bộ chặn.

**Đề xuất cuối:** giữ **tep_toi_da_mib=20**, **thoi_han_giay=120** cho cả hai
năng lực như manifest; giữ **250.000 ô thực, 500.000 ô vùng, 128 MiB giải nén,
2.048 entry, một việc đồng thời**. Lượt chậm nhất đo được **12.719 giây**,
RSS đỉnh lớn nhất **343.56 MiB**; 120 giây có hệ số dự phòng
**9.43 lần** thời gian đã đo. Đây là đề xuất từ các mẫu trên,
không phải chứng minh worst case cho mọi tổ hợp ở trần. Bảng đọc chỉ 30 dòng;
chưa đo bảng xuất 250.000 ô, cây K7 phức tạp tới 100.000 nút hay mọi khuôn.
Không suy số đo này sang Linux 3.11/Core thật; giữ các test từ chối vượt trần,
không nới trần. Chưa có số đo hiệu năng Core thật/Windows Python 3.11.

### Ba lệnh nghiệm thu

Chạy `.venv/Scripts/python`, PYTHONDONTWRITEBYTECODE=1, UTF-8; đã kiểm bằng Core giả (CoreGia).

```text
python -m kho_tri_thuc_sdk.thu e_kiem_excel/goi/e_kiem_excel
→ 5/5 ĐẠT; mã thoát 0.
python -m pytest e_kiem_excel/tests -q
→ 240 passed in 7.43s, 0 skipped; mã thoát 0.
python e_kiem_excel/tests/kiem_doc_lap.py
→ AST, cây gói, import cô lập, 5/5 DEMO XONG; mã thoát 0.
```

`git diff --check` mã 0; không sửa ma-nguon/SDK/Core; không commit/push.

### Lệch khỏi phiếu / quyết định tạm

- Máy có Python 3.13.14, chưa có Linux/WSL: số đo/cài sạch cục bộ là Windows
  3.13.14; CI 3.11 đã soạn và chờ lead chạy. Windows CMD chỉ soạn để Anh chạy.
- Công cụ đóng gói CLI chỉ đọc commit git, không đọc worktree. Theo lệnh
  không commit/push, Codex đóng **bản thử** bằng đúng hàm của công cụ; lead
  đóng phát hành sau commit bằng `python _chung/cong-cu/dong_goi.py --engine
  e_kiem_excel --ref HEAD --nhan EX-6 --ra <thu_muc_moi_ngoai_repo>`.
- Băm NGUON.md ở kiểm kê ngoài gói thay vì tự nhúng băm của chính nội dung.
- Bổ sung sửa đường ghi XML tạm của thư viện để đáp ứng quy tắc không lưu trên
  máy. Một tệp runtime thay đổi; không viết lại thuật toán K1–K8/đọc bảng.

### Cần Core / Chờ Anh mới phát sinh

Không phát sinh yêu cầu Core/SDK mới. Giữ EX0-SDK-02 về MIME và xác nhận MIME
Core thật. Lead commit/mở PR (**chờ lead mở**), chạy CI Linux 3.11 và đóng gói
phát hành từ commit; Anh chạy `e_kiem_excel/tests/KIEM-MAY-SACH.cmd`.

Thời gian thực tế: **0.31 giờ**, từ **19/11/2026 14:48:00 đến 15:06:39**
(giờ Việt Nam); ước tính trong phiếu **3 giờ**. PR: **chờ lead mở**.

## TS-EX — nghiệm thu 21/11/2026, PR: chờ lead mở

Kết luận: **Đạt phần mã và kiểm TS-EX**; đã kiểm bằng Core giả (CoreGia).
Core nạp màn và lưu/CAS bước thật qua cửa D2 còn chờ, không phải kết quả
đã nối Core thật. Không sửa mã Python xử lý việc.

- CLI chuẩn: **5/5 ĐẠT**, mã 0.
- Pytest toàn engine: **241 passed in 74.31s**, **0 skipped**, mã 0;
  gồm Node UI và 6 bộ tham số UI xuất chạy qua parser gốc/CoreGia đều XONG.
- Kiểm độc lập: AST, cây gói, import cô lập, **5/5 DEMO XONG**, mã 0.
- Node UI riêng: **12/12 pass**, 0 fail/skip; đọc/lưu/lỗi nhập, kiểm đạt/lỗi,
  tranh chấp hai màn, giữ bản sửa, chống gửi hai lần, round-trip và an toàn.
- SHA-256 nguyên trạng **25/25** tệp gói khớp; không bytecode trong gói.
- Ba ảnh DEMO desktop/mobile đã dựng bằng KttCore giả và xem lại; kiểm DOM
  thật, không tràn ngang tại 1180/390 px. [Ảnh và lệnh tái lập](anh-TS-EX/README.md).
- Đã chạy công cụ sinh danh mục; nội dung danh mục không đổi do chỉ thêm
  mô tả tham số. git diff --check mã 0. Không commit/push.

Chỉ 5 tệp mã/khai báo runtime: 3 JS UI, KHAI-SDK-2.1.json và engine.json
(chỉ bổ sung mo_ta). Không có schema cấu hình, API key, dịch vụ ngoài
hoặc thao tác quản trị mới; các đường kiểm tương ứng không áp dụng.
Lệch/tạm: mo_ta bị SDK giới hạn 500 ký tự nên bảng cấu trúc đầy đủ ở README;
callback D2 là đề xuất chưa phải SDK phát hành. Mục Cần Core đã ghi hai cửa.
Chưa chạy Linux trong lượt này.

[Báo cáo theo mẫu và kết quả lệnh thật](BAO-CAO-TS-EX.md).

Thời gian thực tế: **0.68 giờ, từ 21/11/2026 21:40:00 đến 21/11/2026 22:21:02 (UTC+7); ước tính trong phiếu: 4 giờ**. PR: **chờ lead mở**.
