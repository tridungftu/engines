# VIỆC — danh sách việc duy nhất của project `e_kiem_excel`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng). Giờ là **ước tính của lead, chưa đo**.

| # | Việc | Lát | Trạng thái | Giờ (ước tính) | Ghi chú |
|---|---|---|---|---:|---|
| 0 | Phiếu engine, tạo thư mục, chép mã gốc tham chiếu, lập phiếu giao Codex | EX-P | Xong — 16/11/2026 | — | Lead Claude. Anh đồng ý tiến hành 16/11; Q1–Q3 áp đề xuất |
| 1 | Khung gói SDK 2.2.0, ghim thư viện, sinh DEMO có giá trị lưu, nhận diện tệp, trần giải nén/ô, đo bộ nhớ | EX-0 | Chờ Core — 18/11/2026 | 4 | Mã và phép đo đã thực hiện; chưa đạt điều kiện CLI do yêu cầu hàm tạm CHUA_LAM. PR: chờ lead mở. Chi tiết bên dưới |
| 2 | `SoDo` + hàm tham chiếu + K1–K6 nạp từ bytes; schema `tep_json` | EX-1 | Chờ làm | 6 | Sau EX-0 |
| 3 | K7 + `o_dich`, `nhan_o_dich_json`, `bo_nhom_json`; Phụ lục A làm fixture | EX-2 | Chờ làm | 4 | Sau EX-1 |
| 4 | Báo cáo Excel trong RAM; K8 sau công tắc `kiem_nguon_kl` | EX-3 | Chờ làm | 4 | Sau EX-2 |
| 5 | `excel.doc_bang@1` khuôn `xay_dung_klgt` | EX-4 | Đang làm — 18/11/2026 | 4 | Mã EX-4 xong, chờ gộp các lát toàn vẹn để CLI chung đạt 3/3. PR: chờ lead mở |
| 6 | Khuôn `tong_quat` | EX-5 | Chờ làm | 4 | Sau EX-4 |
| 7 | Ghim nguồn, cài máy sạch, đo thời gian/bộ nhớ trên bản hoàn chỉnh, chốt `thoi_han_giay` | EX-6 | Chờ làm | 3 | Cuối |
| | **Tổng** | | | **29** | |

## Chờ Anh
- Không có câu chặn. Q1–Q3 đã áp đề xuất (16/11/2026).
- Phụ lục A, hai chỗ lệch nhỏ so với mã gốc (nhóm 6 xét cả nhãn dòng; `dai|rong|cao` khớp chứa chuỗi): EX-2 báo kết quả đo, Anh duyệt nếu muốn chặt hơn.

## Cần Core
- Không có cửa mới cho engine.
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
