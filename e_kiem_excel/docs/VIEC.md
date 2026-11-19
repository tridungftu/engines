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
| 6 | Khuôn `tong_quat` | EX-5 | Chờ làm | 4 | Sau EX-4 |
| 7 | Ghim nguồn, cài máy sạch, đo thời gian/bộ nhớ trên bản hoàn chỉnh, chốt `thoi_han_giay` | EX-6 | Chờ làm | 3 | Cuối |
| | **Tổng** | | | **29** | |

## Chờ Anh
- Không có câu chặn. Q1–Q3 đã áp đề xuất (16/11/2026).
- Phụ lục A, hai chỗ lệch nhỏ so với mã gốc (nhóm 6 xét cả nhãn dòng; `dai|rong|cao` khớp chứa chuỗi): EX-2 báo kết quả đo, Anh duyệt nếu muốn chặt hơn.

## Cần Core
- Không có cửa mới cho engine.
- **EX-3 (19/11):** không phát sinh yêu cầu Core/SDK; báo cáo Excel và JSON qua `viec.tai_tep_ra`. Giữ EX0-SDK-02 về MIME/Core thật; chưa kiểm với Core thật.
- **EX-2 (18/11):** không phát sinh cửa Core/SDK mới. Gói hiện đã có EX-4 và K1–K7,
  CLI chuẩn **3/3 ĐẠT**, mã 0; EX0-SDK-01 không còn chặn bản hiện tại. Các ghi nhận
  CLI mã 1 trong báo cáo EX-0/EX-1/EX-4 bên dưới là lịch sử của từng lượt.
  EX0-SDK-02 về MIME/Core thật vẫn giữ nguyên.
- **EX-1 (18/11):** không phát sinh yêu cầu Core/SDK. Hai DEMO `excel.toan_ven@1` đã XONG qua CLI chuẩn; mục EX0-SDK-01 bên dưới hiện chỉ còn ví dụ `excel.doc_bang@1` của EX-4. Giữ nguyên ví dụ này, không thay kỳ vọng CLI thành đạt; lead chạy lại cả gói sau khi ghép EX-4. MIME vẫn theo EX0-SDK-02.
- **Cần Core xác nhận** MIME khi tải `.xlsx`/`.xlsm` lên Core thật. `API-ENGINE-v1.md` chỉ quy định trường `mime`, không cam kết thuật toán gán MIME. SDK `thu.py`, `CoreGia.them_tep` → `_mime` trả `.xlsx`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; `.xlsm`: `application/vnd.ms-excel.sheet.macroEnabled.12`. HTTP tải byte của `MayChuGia` dùng `application/octet-stream`, khác metadata trong phong bì. Chưa có bằng chứng Core thật; manifest tạm nhận thêm `application/octet-stream`, vẫn kiểm đuôi/chữ ký/ZIP/XML.
- **EX0-SDK-01 — CLI và hàm tạm mâu thuẫn:** SDK 2.2.0 `thu.main()` chỉ cho `[ĐẠT]` khi `trang_thai == "XONG"`, không có cách khai lỗi kỳ vọng trong `chay_thu_demo`. Yêu cầu EX-0 giữ `LoiNghiepVu("CHUA_LAM", …)` làm ba ví dụ đều kết thúc `LOI`. Giữ nguyên API/SDK và yêu cầu hàm tạm; không đổi lỗi thành thành công hay bỏ DEMO. Cần lead thống nhất nghiệm thu EX-0 theo test lỗi kỳ vọng, hoặc SDK bổ sung cơ chế kiểm lỗi kỳ vọng. CLI chuẩn vẫn mã 1 ở bản này; không tuyên bố đạt ba lệnh.
- **EX0-SDK-02 — chữ hoa/thường MIME:** manifest và bộ kiểm phong bì của SDK 2.2.0 chỉ nhận MIME viết thường, nhưng CoreGia tự trả `.xlsm` có `macroEnabled.12`; phong bì này bị lỗi `DAU_VAO_KHONG_HOP_LE` trước khi tới engine. Manifest dùng `macroenabled.12`; lớp bọc tạm `CongKiemExcel._lam` chuẩn hóa bản sao MIME của đầu vào gửi kèm/tải riêng, giữ nguyên các kiểm tra và vòng lease/nộp/kết thúc của SDK. Hai ca CoreGia đã kiểm lớp bọc. Cần Core/SDK xử lý MIME không phân biệt hoa/thường để bỏ lớp bọc.

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
