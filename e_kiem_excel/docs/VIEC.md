# VIỆC — danh sách việc duy nhất của project `e_kiem_excel`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng). Giờ là **ước tính của lead, chưa đo**.

| # | Việc | Lát | Trạng thái | Giờ (ước tính) | Ghi chú |
|---|---|---|---|---:|---|
| 0 | Phiếu engine, tạo thư mục, chép mã gốc tham chiếu, lập phiếu giao Codex | EX-P | Xong — 16/11/2026 | — | Lead Claude. Anh đồng ý tiến hành 16/11; Q1–Q3 áp đề xuất |
| 1 | Khung gói SDK 2.2.0, ghim thư viện, sinh DEMO có giá trị lưu, nhận diện tệp, trần giải nén/ô, đo bộ nhớ | EX-0 | Chờ Core — 18/11/2026 | 4 | Mã và phép đo đã thực hiện; chưa đạt điều kiện CLI do yêu cầu hàm tạm CHUA_LAM. PR: chờ lead mở. Chi tiết bên dưới |
| 2 | `SoDo` + hàm tham chiếu + K1–K6 nạp từ bytes; schema `tep_json` | EX-1 | Xong — 18/11/2026 (phần EX-1) | 6 | PR: chờ lead mở. 62 pytest đạt; CLI chung 2/3, còn CHUA_LAM của EX-4. Schema chờ lead duyệt; chi tiết bên dưới |
| 3 | K7 + `o_dich`, `nhan_o_dich_json`, `bo_nhom_json`; Phụ lục A làm fixture | EX-2 | Chờ làm | 4 | Sau EX-1 |
| 4 | Báo cáo Excel trong RAM; K8 sau công tắc `kiem_nguon_kl` | EX-3 | Chờ làm | 4 | Sau EX-2 |
| 5 | `excel.doc_bang@1` khuôn `xay_dung_klgt` | EX-4 | Chờ làm | 4 | Sau EX-0; song song EX-1…EX-3 được |
| 6 | Khuôn `tong_quat` | EX-5 | Chờ làm | 4 | Sau EX-4 |
| 7 | Ghim nguồn, cài máy sạch, đo thời gian/bộ nhớ trên bản hoàn chỉnh, chốt `thoi_han_giay` | EX-6 | Chờ làm | 3 | Cuối |
| | **Tổng** | | | **29** | |

## Chờ Anh
- Không có câu chặn. Q1–Q3 đã áp đề xuất (16/11/2026).
- Phụ lục A, hai chỗ lệch nhỏ so với mã gốc (nhóm 6 xét cả nhãn dòng; `dai|rong|cao` khớp chứa chuỗi): EX-2 báo kết quả đo, Anh duyệt nếu muốn chặt hơn.

## Cần Core
- Không có cửa mới cho engine.
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
