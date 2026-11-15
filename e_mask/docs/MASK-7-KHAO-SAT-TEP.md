# MASK-7 — Bằng chứng tệp và phương án trình Anh

Ngày 15/11/2026; nhánh `codex/e_mask-mask-7`; PR: **chờ lead mở**. Phạm vi: khảo sát nguồn trong repo, tạo fixture DEMO trong RAM ở `tests/`, đo và trình phương án. Không thêm năng lực/thuật toán, UI, dependency, không sửa nguồn cũ/Core/SDK, không mở kho dữ liệu nguồn ngoài; không commit/push.

**Kết luận: hoàn tất khảo sát MASK-7; chưa đủ cơ sở triển khai toàn bộ Word/Excel.** Nguồn Word chỉ dựng mới và xử lý lịch sử sửa; nguồn Excel che một phần XML nhưng có thể xuất nguyên định danh trong công thức/liên kết ngoài. Trần tệp/đầu ra/ZIP và phương án MASK-8…11 **chờ Anh/lead chốt** theo quyết định 15/11 câu 11. Chưa triển khai phần thiếu. Văn bản hiện có **đã kiểm bằng Core giả (CoreGia)**; khảo sát helper tệp là kiểm nguồn độc lập, không phải năng lực tệp đã nối CoreGia.

## 1. Phương pháp và khả năng tái lập

Đọc AGENTS.md, hợp đồng API v1 + hai hướng dẫn SDK 2.0.0, quyết định 15/11, phiếu đợt 2/thứ tự/SDK 2.1, sổ loại riêng, phiếu giao Mask, CLAUDE.md, hiện trạng, quyết định cuối §2.2/§3/§5.2, `ma-nguon/NGUON.md` §4, `ma-nguon/nguon/PHU-THUOC.md`. Mã nguồn dẫn dưới đây tương đối với `e_mask/ma-nguon/nguon/privacy/`, trừ nơi ghi khác. Không dùng thông tin trên mạng hoặc nguồn ngoài repo.

- `tests/ho_tro_khao_sat_tep.py` nạp nguyên `excel.py`, `excel_values.py`, `docx_revisions.py`, `types.py` từ repo dưới namespace test riêng. Chỉ lấy nguyên AST năm định nghĩa `CATEGORIES`, `TOKEN`, `key`, `literal_pattern`, `validate_rules` của core cũ; dùng `normalize`/`PrivacyError` nguyên bản. Không import crypto/python-docx chưa ghim, không thay bằng matcher mới. **Không chạy `make_docx`**; kết luận về hàm này dựa đọc mã/AST.
- Token thử Excel là `[KHAC_001]` đúng khuôn cũ, không giả đã chuyển sang `[[...]]`. Test không chạy detector cũ/không đọc tài nguyên bên ngoài. Từ điển sạch hiện có chỉ được handler văn bản dùng theo MASK-6.
- Word fixture là các phần XML tối giản có tên DEMO ở thân/đầu/chân/notes/comments/thuộc tính và ins/del. Nó đủ để thử helper, **không phải DOCX đã được Word xác nhận mở được**. Excel fixture là workbook do helper nguồn dựng, bổ sung từng phần tối giản để khảo sát parser; không phải nghiệm thu hiển thị Excel.
- `tests/test_mask_7.py`: kiểm kết quả XML/bytes thật của helper, kể cả các ca cố ý chứng minh chưa an toàn. Test xanh nghĩa là bằng chứng giới hạn được tái hiện, không có nghĩa che đủ mọi vùng.
- `tests/do_mask_7.py`: mỗi ca một tiến trình mới, một lần đo mỗi ca trong lượt ghi hoàn tất, seed 7. Bộ 1.000/100.000/500.000 ký tự dạng lặp và 500.000 dạng đa dạng (hex DEMO + Unicode + tiền/ngày). Chia ô bằng fixture, không cắt chuỗi; không ghi DOCX/XLSX xuống đĩa. JSON số đo chỉ có môi trường/băm/số đếm/thời gian, không tài liệu hoặc mapping.

## 2. Bảng bằng chứng từng vùng Word

| Vùng | Mã nguồn thực đọc | Bằng chứng DEMO / kết luận |
|---|---|---|
| Thân, bảng, run | `core.py:548–595`, `make_docx(text)` gọi `Document()` không đầu vào DOCX; tạo Arial 11, đoạn/bảng tab; `export_document` chỉ kiểm lại đoạn/ô của tệp vừa dựng | AST xác nhận chỉ nhận `text`. `test_word_accept_khong_che_bat_ky_vung_nao` vẫn còn tên ở thân. **Chưa có che DOCX gốc/giữ bố cục/tên tách run** |
| Đầu/chân trang | `make_docx` không nhận gói gốc; `docx_revisions.py:107–146` duyệt `word/*.xml` chỉ khi có revision markup | Tên trong `header1.xml`, `footer1.xml` giữ nguyên sau helper. **Chưa có che** |
| Footnote/endnote | Cùng đường helper; không có reader/mask chuyên biệt trong closure repo | Tên trong `footnotes.xml`, `endnotes.xml` giữ nguyên. **Chưa có che** |
| Bình luận | Cùng helper lịch sử sửa; không có vòng che comment/tác giả của DOCX gốc | `comments.xml` còn tên. **Chưa có che** |
| Lịch sử sửa | `docx_revisions.py:50–89` xóa del/moveFrom/property changes, unwrap ins/moveTo; `:107–146` có thể trả `(data, 0)` | DEMO xóa hai dấu sửa nhưng giữ tên trong ins/thân. Bốn ca hỏng/ZIP path traversal/DTD-entity/trùng tên trả nguyên byte. **Accept không phải che, không được bỏ lịch sử rồi công bố đã quét đủ** |
| Thuộc tính | `core.py:550–551` làm rỗng bảy core properties trên tài liệu **mới**; helper revisions chỉ chọn `word/*.xml` | `docProps/core.xml` gốc còn tên. **Chưa có quét core/app/custom của DOCX gốc** |

Không có Word unmask file trong closure đã đọc; nhận bí danh mềm ở lõi văn bản không tự ghép và thay được run/notes/comment XML của Word. Không dùng `accept_tracked_changes` làm bước chứng nhận an toàn: không có revision hoặc không xử lý được đều có thể cùng trả đếm 0. Nó còn bỏ qua phần >15 MiB; `_safe` không kiểm đầy đủ ratio/symlink. Không đưa helper này lên đường vận hành trong MASK-7.

## 3. Bảng bằng chứng từng vùng Excel

| Vùng | Mã nguồn thực đọc | Bằng chứng DEMO / kết luận |
|---|---|---|
| Tên sheet | `excel.py:_read_cells` :582–712 giữ tên; `_audit` :1237–1279 kiểm attribute; `_ai_plan` :916–1013 dùng `safe_sheet_name` | Tên chứa cụm chọn → blockers, `output=None`. **Chưa che tại chỗ**; bản values đổi tên không thay giữ định dạng |
| Sheet ẩn/veryHidden | `_read_cells` không bỏ sheet theo state; `_mask` :1025–1187 thay XML giá trị | Ca `sheet_an` che tên trong ô và giữ `veryHidden`. Chỉ chứng minh string trong sheet ẩn tối giản, không mọi đối tượng ẩn |
| Ô/hàng/cột ẩn | `_read_cells` duyệt tất cả `c`, không bỏ hàng/cột hidden | Ca `o_an` che ô và giữ cả hai cờ hidden; ô số 1.000.000 và serial ngày 46325 giữ nguyên. Không kiểm rendering/locale Excel |
| Bình luận | `_read_metadata` :713–737 xử lý author và rich text comments | Comment legacy/tác giả DEMO được che. Threaded comments/persons là unsupported, **chưa đủ mọi loại bình luận** |
| Chart/nhãn | `ALLOWED_PART` :40–49 không có charts; `_describe_unsupported` :405–412; `_validate_drawing` :516–531 chỉ shape/text, không chart/ảnh | Thêm `xl/charts/chart1.xml` → blocker, không có output. **Chưa che nhãn chart**; shape text không đồng nghĩa chart |
| Thuộc tính | `_read_metadata` core/app/custom; `_audit` kiểm phần bất biến; printer binary chỉ disclosure :417–433 | Creator core DEMO được che. Một số app properties và custom chuỗi có code nhưng chưa thử mọi nhánh; binary/thumbnail/customXml chưa được chứng nhận. Không công bố đã che toàn metadata |
| Công thức/cache | `_mask` :1099–1143 giữ `<f>`, có sửa cache chữ, có bỏ cache nhất định và đặt fullCalcOnLoad/forceFullCalc; `_audit` :1271–1277 đưa `formula_sensitive` vào disclosures | Ca `cong_thuc`: **có output, công thức còn tên**, cache đã được xử lý; disclosures cũng chứa tên gốc. Vì vậy nhận định “mọi công thức có tên đều blocker” là sai. Tính lại có thể tái sinh tên; chưa đủ bảo toàn ngữ nghĩa |
| Liên kết ngoài | `_validate_relationships` :435–503 chỉ ghi target, không mở/fetch; `_read_external_links` :758–797; `_audit` dùng disclosures cho external | Ca `lien_ket_ngoai`: **có output và còn tên ở external sheetName/target**, disclosures nguyên văn. **Chưa che link/cache**; không có mạng trong harness |

`changes.before`, `summary.sheet_names/hidden_sheets`, warnings, blocker location/value và disclosures có thể chứa định danh. Test đã chứng minh tên sheet trong blockers, tên gốc trong disclosures. Lát sau phải chuyển sang mã vùng/chỉ số/câu cố định trước trả báo cáo, chặn nếu phần được giữ lại chưa che; không coi “có disclosure” là an toàn.

`excel_values.py:74–87` cắt cell text ở 32.767, bỏ ký tự cấm/chuẩn hóa/cắt tên sheet tới 31 và tránh trùng. `_ai_plan` có thể đổi tên, tạo sheet công thức/ghi chú; `build_values_workbook` dựng mới, bỏ metadata/link/chart… Test chứng minh chuỗi 35.000 thành 32.767 và `[[MASKCT-0001]]` thành `MASKCT-0001`. **Không dùng làm fallback giữ định dạng**. Không có Excel unmask trong nguồn này.

## 4. Số đo DEMO và giới hạn diễn giải

Số đo đầy đủ: [SO-DO-MASK-7.json](SO-DO-MASK-7.json), gồm SHA-256 LF nguồn, Python/OS/architecture/SDK/zlib/CPU logic. Môi trường đo: Windows 11 build 10.0.26200, AMD64, Python 3.13.14, SDK 2.0.0, zlib 1.3.1, 12 CPU logic; venv trong worktree, không có tải test chủ ý chạy song song. Các ứng dụng khác trên máy không được kiểm soát. Dấu phẩy trong bảng sau là phân cách hàng nghìn; MiB = 1.048.576 byte.

| Luồng / seed / kiểu | ZIP byte vào → ra | Giải nén byte vào → ra | Ký tự vào → ra | Giây | Python peak MiB | OS peak MiB |
|---|---:|---:|---:|---:|---:|---:|
| docx / 1,000 / lap | 1,807 → 1,814 | 7,939 → 7,900 | 7,028 → 7,014 | 0.004923 | 0.35 | 29.98 |
| docx / 100,000 / lap | 3,956 → 3,955 | 700,939 → 700,900 | 700,028 → 700,014 | 0.010481 | 1.11 | 30.39 |
| docx / 500,000 / lap | 12,091 → 12,090 | 3,500,939 → 3,500,900 | 3,500,028 → 3,500,014 | 0.038269 | 4.78 | 35.28 |
| docx / 500,000 / da_dang | 1,779,389 → 1,779,376 | 3,516,185 → 3,516,146 | 3,500,028 → 3,500,014 | 0.203801 | 6.35 | 38.19 |
| xlsx / 1,000 / lap | 2,223 → 2,223 | 4,460 → 4,376 | 1,033 → 949 | 0.031175 | 0.50 | 30.45 |
| xlsx / 100,000 / lap | 3,729 → 3,517 | 111,762 → 103,490 | 100,033 → 91,761 | 0.220701 | 1.59 | 31.79 |
| xlsx / 500,000 / lap | 9,423 → 7,950 | 546,162 → 504,826 | 500,033 → 458,697 | 1.347464 | 7.63 | 39.24 |
| xlsx / 500,000 / da_dang | 263,000 → 263,082 | 548,340 → 544,036 | 500,033 → 495,729 | 1.049567 | 9.80 | 42.35 |
| van_ban / 1,000 / lap | không là ZIP | không áp dụng | 1,000 → 1,861 | 0.058153 | 0.23 | 33.88 |
| van_ban / 100,000 / lap | không là ZIP | không áp dụng | 100,000 → 185,404 | 5.651850 | 7.86 | 59.94 |
| van_ban / 500,000 / lap | không là ZIP | không áp dụng | 500,000 → 927,097 | 41.689126 | 38.12 | 159.48 |
| van_ban / 500,000 / da_dang | — | — | đầu ra chưa đo | timeout tiến trình 60s | chưa đo | chưa đo |

**11/12 ca có số đo hoàn tất; một ca vượt ngân sách tiến trình đo 60 giây.** Timeout gồm khởi động/import/dựng fixture và xử lý, không phải số đo thời gian handler chính xác, không là chứng cứ Core timeout đã hoạt động. Không có số RAM/ký tự ra đáng tin cho ca đó; không điền số giả. Lượt đầu công cụ dừng ở ca timeout cuối và chưa lưu JSON; lượt ghi trên đã chạy lại với cơ chế lưu từng ca và ghi riêng timeout. Mã thoát 0 của công cụ nghĩa là ghi đủ ca, không nghĩa là mọi ca xử lý thành công.

Văn bản lặp tăng 500.000 → 927.097 ký tự do thay bí danh; không thể dùng 500.000 làm trần đầu ra. Peak tiến trình 159,48 MiB ở ca này không phải budget đã duyệt. Excel đa dạng có ZIP ra lớn hơn vào (263.082 so với 263.000 byte), nên phải kiểm riêng chiều ra. Word seed 500.000 thực chứa 3.500.028 ký tự vì fixture có nhiều vùng: nó sẽ vượt trần tổng 500.000 nếu reader tệp tương lai áp dụng đề xuất, dù helper lịch sử sửa vẫn xử lý. Không suy mức hỗ trợ từ việc helper đo xong.

`byte_zip` là toàn container, `byte_nen_thanh_vien` là tổng payload nén (không header), `byte_giai_nen` là tổng file_size; không dùng chúng thay lẫn nhau. Ký tự XML là text/tail Unicode sau parse, không markup/attribute; Word có cùng chuỗi ở nhiều vùng nên tổng lớn hơn kích thước seed. Đây **không phải số ký tự văn bản đã che** của Word: helper không che. Ký tự CoreGia là chuỗi vào/ra thực; UTF-8 byte đo riêng.

Thời gian chỉ bao quanh xử lý, không gồm dựng fixture/import/đếm lại; có bật `tracemalloc` nên không là benchmark production. Tracemalloc peak là cấp phát Python trong lượt, không phải RAM toàn máy. OS peak working set/RSS trước/sau là high-water mark của toàn tiến trình, gồm import/dựng fixture và cấp phát native, không lấy hiệu hai đỉnh làm RAM riêng của thuật toán. Mỗi ca chạy riêng tránh đỉnh từ ca trước. Một lần đo không cho p95 hoặc cam kết tải đồng thời; không đặt ngưỡng test tốc độ mới.

Word đo accept revisions, Excel đo parse + mask + audit + dựng ZIP bằng rule cũ (cụm qua ranh giới hai ô không được ghép; không có detector/hậu kiểm toàn engine trong phép đo này), văn bản đo handler SDK với CoreGia/ngăn/quyền DEMO và từ điển sạch đang có. **Chưa đo che/mở che DOCX gốc, unmask XLSX, PDF, Core thật hoặc máy chủ đích** vì chưa có chức năng/nguồn đã chốt. Test tệp nguồn không được gộp thành “đã kiểm bằng Core giả (CoreGia)” cho tệp.

## 5. Trần trình lead/Anh — chưa áp dụng

Không có cơ sở suy 20 MiB nén chạy được chỉ vì chuỗi 500.000 chạy được. `MAX_BYTES=20 MiB`, `MAX_EXPANDED=80 MiB`, phần ≤32 MiB, 2.000 phần, 200 sheet/200.000 ô/500.000 node toàn workbook, 80 mức XML/400.000 node mỗi XML/ratio 1000 trên phần >1 MiB là **giới hạn kỹ thuật Excel cũ**. Word helper dùng 3.000 phần/80 MiB tổng/15 MiB mỗi phần, vượt phần thì bỏ qua. JSON adapter đang có 4 MiB là giới hạn kỹ thuật mẫu 1/3, không là phê duyệt tệp nghiệp vụ. Không đổi các số này hoặc manifest trong MASK-7.

Đề xuất một bộ trần thử nghiệm bảo thủ để Anh/lead cân nhắc, **chưa là ngưỡng an toàn đã chứng minh**:

| Đại lượng | Đề xuất cho vòng DEMO tiếp sau duyệt | Điều kiện trước vận hành |
|---|---|---|
| DOCX/XLSX vào và ra | Mỗi chiều ≤1 MiB nén, kiểm chiều ra riêng trước upload; không tự lấy trần vào làm trần ra | Bổ sung DEMO đúng 1 MiB và +1 byte, entropy/format/nhiều node/alias dài; đo RAM trên máy đích. Những ca khảo sát lớn hơn chỉ là điểm đo, không phải quyền nhận tệp |
| Giải nén ZIP | Tổng ≤8 MiB, mỗi phần ≤2 MiB, ≤256 phần; tỷ lệ từng phần ≤200:1 (kể cả phần nhỏ) | Chạy biên và ZIP bomb nhỏ có giới hạn tài nguyên; từ chối cả gói, không bỏ phần. Tỷ lệ nén cao có thể là DEMO hợp lệ: chấp nhận đánh đổi từ chối nhầm |
| XML/tập đối tượng | Độ sâu ≤64; ≤100.000 node tổng; ≤50 sheet, ≤20.000 ô | Đây là đề xuất thấp hơn số cũ, **chưa benchmark biên**; đo riêng many-node/many-cell, không suy từ plain text |
| Nội dung vào | Giữ ≤500.000 ký tự đã chốt, tính tổng mọi vùng đọc; không dùng preview 500.000 của Excel để cắt dữ liệu | Đầu vào văn bản CoreGia 500.000 được thử; file text extraction cần đo sau có reader |
| Nội dung ra | Đề xuất ≤2.000.000 ký tự và ≤8 MiB UTF-8 cho văn bản, đồng thời; JSON báo cáo ≤256 KiB UTF-8 | Cần test alias/mở che khuếch đại, danh sách vị trí/báo cáo dài. Không bịa hệ số expansion tối đa; vượt thì lỗi, không cắt. Bước Hỏi AI vẫn kiểm trần của nó |
| Thời gian/RAM | Chưa trình số hard cap production từ một máy/lần đo; phiếu 60s văn bản/300s tệp chỉ là dự toán kỹ thuật | Lead/Core xác định budget tiến trình/job/concurrency, đo máy đích và hủy/timeout trước mở năng lực |

Bộ ZIP mới còn phải từ chối tên tuyệt đối/drive/UNC/backslash/`..`, trùng tên kể cả casefold, symlink, encrypted, phương thức nén lạ, DTD/entity/PI và thành phần không được hỗ trợ. Đối chiếu kích thước khai báo với bytes đọc thực, giới hạn trong lúc đọc, không extract ra đĩa; không tin MIME/đuôi. Đây là **thiết kế cần bổ sung**, không khẳng định mã cũ đã đạt. Chưa chốt trần → không mở năng lực và thiết kế `LoiNghiepVu("MASK_TEP_CHUA_CHOT_GIOI_HAN", "Chưa có giới hạn xử lý tệp được phê duyệt.")`; phần không hỗ trợ → `MASK_TEP_CHUA_HO_TRO`, “Tệp có nội dung chưa được hỗ trợ xử lý đầy đủ.” Không trả thành công rỗng.

## 6. Nguồn cần bổ sung và các phương án

| Phương án trình Anh | Ưu điểm | Hạn chế/điều kiện |
|---|---|---|
| A — Lead cung cấp nguồn sạch đầy đủ vùng Word/Excel và mở che | Tận dụng mã nội bộ, giảm viết mới | Chưa thấy nguồn đó trong repo. Lead chép closure **chỉ mã**, SHA/phiên bản/quyền nguồn/lock/artifact notices + DEMO; không dữ liệu/khóa/danh mục/launcher/OCR. Codex không mở kho nguồn ngoài. Phải đánh giá lại giờ sau đọc code, chưa thể cam kết |
| B — Bổ sung bằng ZIP/XML stdlib, phạm vi OOXML có kiểm và từ chối phần lạ (**đề xuất**) | Không thêm thư viện Word/Excel, kiểm trực tiếp phần được giữ, giữ bytes phần không đổi | Anh cần duyệt phát triển mới và giới hạn hỗ trợ. Run tách, công thức tham chiếu, chart/cache và lịch sử sửa cần xử lý riêng; không hứa mọi OOXML hoặc file do AI tùy ý |
| C — Tiếp tục chỉ văn bản; Core đưa OCR/văn bản vào Mask | Dùng năng lực đang có, không phát triển mới phần tệp khi chưa duyệt | Không đáp ứng nhận lại DOCX/XLSX giữ bố cục/mẫu 5–8. Giữ các lát tệp ở Chờ Anh, không ghi đã hoàn tất quyết định 06/11 |

Với A: cần reader DOCX tất cả story parts + tables/runs/fields/textboxes/notes/comments/revision text/properties; patch giữ format và mở mềm qua nhiều run; Excel cần đổi tên sheet có cập nhật tham chiếu đã kiểm hoặc chặn, chart text/cache/formula và link/cache/metadata an toàn, inverse file walker. Kèm fixture cấu trúc sạch cho unsupported/tiền-ngày/AI sửa. Không đưa crypto/helper bảng đối chiếu cũ/COM vào closure. Bốn từ điển sạch đã có, **không yêu cầu cấp lại từ điển**. PDF cần closure đọc lớp chữ và bộ wheel/hash/giấy phép offline (phiếu cho phép tham khảo nguồn PDF của OCR ở lát sau), hiện chưa thử/cài.

Ước tính mới cho **B**, gồm code/test/review DEMO engine; không gồm chờ duyệt, công Core/SDK, chuẩn bị nguồn ngoài, vận hành thật. Mỗi lát ≤5 tệp mã; mọi đường dưới là dự kiến dưới `goi/e_mask/` trừ test/tài liệu. Các lát con phải được lead cập nhật phiếu trước giao, **chưa code**:

| Lát dự kiến | Tập tệp mã (tối đa 5) | Giờ công **ước tính mới, chưa đo** |
|---|---|---:|
| MASK-8a ZIP/MIME/trần + reader Word toàn vùng | `e_mask/{doc_tep,doc_word}.py`; test/tài liệu ngoài tập | 6–8 |
| MASK-8b reader PDF chữ + SDK văn bản | `e_mask/{doc_pdf,chay}.py`, `engine.json`, `requirements.lock` | 4–6 |
| MASK-9a chuyển Excel + chặn formula/link/metadata chưa che | `e_mask/nguon/privacy/{excel,excel_values}.py`, `e_mask/tep_excel.py`, `e_mask/chay.py`, `engine.json`; không dùng values fallback | 6–8 |
| MASK-9b sheet/metadata và chart trong whitelist đã duyệt | `e_mask/{tep_excel,xml_excel}.py`, `e_mask/nguon/privacy/excel.py` | 8–12 |
| MASK-10a che Word story parts/run/properties | `e_mask/{tep_word,doc_word,xml_word}.py` | 8–12 |
| MASK-10b Word history/comment/notes + hậu kiểm/SDK | `e_mask/{tep_word,doc_word,chay}.py`, `e_mask/nguon/privacy/docx_revisions.py`, `engine.json` | 6–10 |
| MASK-11a mở mềm Word, giữ nội dung AI thêm, vị trí lạ | `e_mask/{mo_tep_word,xml_word,phong_bi}.py` | 8–12 |
| MASK-11b mở Excel + quyền/chốt/SDK cả hai tệp | `e_mask/{mo_tep_excel,tep_excel,phong_bi,chay}.py`, `engine.json` | 8–12 |
| **Tổng MASK-8…11 theo B** | Thay dự toán có điều kiện cũ **21–31 giờ** | **54–80 giờ** |

Giữ các lát khác như phiếu, tổng triển khai cũ 52–62 giờ thành **85–111 giờ ước tính** nếu chọn đủ B (cộng phần ngoài MASK-8…11 là 31 giờ; MASK-7 vẫn 2 giờ ước tính). Đây là ước lượng lập kế hoạch, không phải thời gian đã dùng hoặc cam kết đủ mọi vùng OOXML. Chart/link/formula có cấu trúc ngoài whitelist tiếp tục từ chối; muốn hỗ trợ rộng hơn phải ước riêng sau có DEMO/nguồn. C chưa có giờ phát triển tệp; A chưa có nguồn để ước lại có trách nhiệm.

PDF chọn trả tệp: thống nhất **từ chối rõ** `LoiNghiepVu("MASK_PDF_CHI_VAN_BAN", "PDF chỉ hỗ trợ trả văn bản đã che.")`, không tự đổi lựa chọn của module. Scan/ảnh hoặc PDF lẫn trang thiếu lớp chữ: `MASK_PDF_CAN_OCR`, “Tài liệu cần nhận dạng chữ trước khi che. Hãy dùng quy trình OCR của Core.” Core điều phối OCR → văn bản → Mask; Mask không gọi OCR. Trong MASK-7 đây là thiết kế, không handler đã có.

## 7. Cần Core và phần chưa kiểm

- Ngăn thật/quyền/module/người/tài liệu/mã yêu cầu ổn định và đối soát bàn giao vẫn là phụ thuộc MASK-6, không giả hoàn tất bằng fixture. Core xác minh tệp tham chiếu con trong JSON thuộc cùng việc và quyền download/upload/kết quả; bảo đảm không lọt file chưa hậu kiểm trước chốt.
- SDK `mo_tep` đọc trọn trong RAM, giới hạn phía engine sau đọc không đủ bảo vệ tải trước đó. Cần trần input/output chung và upload, đếm byte thực/luồng có hủy, budget thời gian/RAM của job, ánh xạ lỗi 413 đúng; không sửa SDK trong lát này.
- Chưa kiểm Word/Excel mở thật, bố cục/format/ô gộp phong phú, notes/comment đầy đủ chuẩn, chart/cache, external refresh/recalc, mở che tệp sau AI, ZIP biên/bomb/symlink và mọi trường hợp OOXML lạ. Không có máy Linux thực chạy trong phiên này; test/harness có nhánh Linux nhưng không nhận đã kiểm Linux.
- Chưa kiểm PDF/lẫn scan, chuỗi Core OCR → Mask, Core thật/browser/phân quyền thật/độ bền ngăn, Cloud/AI thật/Junsky thật/danh mục thật. **0 lượt Cloud, 0 lời gọi engine khác.**
- CLI SDK chuẩn hiện không cấp nguồn quyền nên hai DEMO bị chặn. Adapter DEMO ngoài gói tiêm quyền/ngăn rồi chạy CoreGia thật. Không sửa handler để làm xanh CLI bằng quyền tự khai.

## 8. Kiểm và bàn giao

Lệnh, mã thoát và kết quả thật tại [KET-QUA-KIEM-MASK-7.txt](KET-QUA-KIEM-MASK-7.txt). Ba lệnh AGENTS.md §5 đều được chạy, kèm adapter DEMO, test khảo sát và đo. UTF-8/JSON/khối lệnh phiếu/diff được kiểm. Không có tệp DEMO lớn/binary hoặc bytecode mới trong `goi/`.

Việc nhỏ: sửa mô tả NGUON về `kho_tam.py`/`cau_hinh_may.py` đã chuyển `LUU-TRU/mask_truoc_ngan/`. Nhánh chết `dong_yeu_cau` trong `KhoQuaCore.chot` **đã được lát sửa an toàn trước loại bỏ**: hiện che không đạt bị raise, không sửa mã chạy trong MASK-7.

Thời gian thực tế và kết quả tổng hợp được chốt trong `VIEC.md`; bắt đầu theo handoff **08:59 ngày 15/11/2026 (UTC+07)**; phiếu MASK-7 **2 giờ ước tính**. Lead commit/mở PR; chưa được duyệt thì không tiến sang code MASK-8…11.

Kết quả cuối: CLI SDK chuẩn **0/2, mã 1** (thiếu nguồn quyền); adapter CoreGia **2/2, mã 0**; pytest **438 passed, 190 subtests passed, 0 skipped, 32.52s**; khảo sát riêng **16 passed, 0.28s**; kiểm độc lập **ĐẠT, mã 0**. UTF-8 9/9, khối lệnh 14/14, AST 3/3, SHA nguồn LF 5/5, diff mã 0.

Thời gian thực tế: **08:59:00–09:16:54 ngày 15/11/2026 (UTC+07), 0.30 giờ thực tế; phiếu MASK-7 2 giờ ước tính**. Không commit/push; PR chờ lead mở.
