# NGUỒN — e_mask

Ngày đối chiếu: 06/11/2026. Lát **MASK-1 / CD-101**, theo Quyết định cuối e_mask §2.1 lát 1 (bản 06/11/2026 trong thư mục dự án chính; worktree chưa có tệp này). Lõi nội bộ đã được chép vào gói; chỉ kiểm giấy phép thư viện bên thứ ba. Chưa công bố capability hoặc nghiệm thu engine.

## 1. Nguồn khung engine trong repo

| Đường gốc | Đích | Ghi chú |
|---|---|---|
| src/kho_tri_thuc/engines/e_mask/chay.py | engines/e_mask/chay.py | chuyển ở G3-GOI-27, không sửa trong MASK-1 |
| src/kho_tri_thuc/engines/e_mask/vong_doi.py | engines/e_mask/vong_doi.py | chuyển ở G3-GOI-27, không sửa trong MASK-1 |
| src/kho_tri_thuc/engines/e_mask/contract/du_thao.json | engines/e_mask/contract/du_thao.json | bản nháp, chưa công bố; không sửa |

Sau G3-GOI-29, khung dùng interface launcher từ SDK nhưng còn helper `kho_tri_thuc.nguon.trich6_host.env_con`. Khung cũ vẫn nhắm `run_privacy.py` nguồn ngoài; MASK-1 chưa đổi launcher, chưa nối lõi đã chép vào Core/API, chưa chạy server. Các quy tắc khóa/lượt/tài khoản cũ cần lead xử lý theo quyết định mới.

## 2. Bảng nguồn → đích và SHA-256

Gốc: `D:\GPT\Phan mem Mask file\Mask file v2`. Chỉ đọc mã `.py` thuộc closure cần xét; không import/chạy ứng dụng nguồn ngoài, không sửa/xóa nguồn. `privacy/__init__.py` khai **2.7.2**: phiên bản ứng dụng nguồn, **không phải SDK** hoặc revision bất biến. SHA nguồn giữ giá trị đã ghi từ byte gốc; SHA sau chỉnh tính từ byte đích hiện tại sau các điều chỉnh ở cột cuối. Tệp chỉ thay dòng CRLF → LF có thể có SHA khác dù nội dung giữ nguyên.

| Tệp gốc | Tệp đích (từ e_mask) | SHA nguồn | SHA sau chỉnh | Điều chỉnh |
|---|---|---|---|---|
| `privacy/__init__.py` | `nguon/privacy/__init__.py` | `089a17a5759e62cb2e7a4f160bb88ac248ea4a8e2a507f1c7aad323a123e6845` | `089a17a5759e62cb2e7a4f160bb88ac248ea4a8e2a507f1c7aad323a123e6845` | nội dung giữ nguyên; UTF-8/LF |
| `privacy/core.py` | `nguon/privacy/core.py` | `313629cdabf68ab8b431ab5ae52bdc368a0b6eae2a75e7e30cae647c3f48d865` | `287616e854e5c6a59be5a2531638dd5f68dda2df387b0ff778b770da4ff44075` | import nội bộ tương đối; bỏ tham chiếu nhận dạng trong chú thích; UTF-8/LF |
| `privacy/types.py` | `nguon/privacy/types.py` | `426f021ac87fe5c9d0f71ddc25ecc5ada62eef2ee3c329d041928f5a6260cd3c` | `59acab78646831909af6da5d54b292c0ad35929fbbff8b526084853bbf02c562` | bỏ trường đếm trang nhận dạng; UTF-8/LF |
| `privacy/detectors.py` | `nguon/privacy/detectors.py` | `7bc1d6a5ccb88eff5dc21018837ea4219e697f81df04afcc6231c3fa9fc4c77f` | `793419cc7e649947040dd0abd1be2d76a02a038f8f92580bf56fb44cf64f5039` | import nội bộ tương đối; đổi mô tả biến thể văn bản; đã chỉnh chú thích ví dụ số tài khoản thành số giả; UTF-8/LF |
| `privacy/company_names.py` | `nguon/privacy/company_names.py` | `b09c30eaaa6cbda23ad67066b371aef5fa4e37d88435464897a3dd204a08036e` | `56a6b584d2e78161182413df61c6391e21c9c6fa8f64d2c483e5f849fc3a2fb3` | bỏ tham chiếu nhận dạng trong docstring; UTF-8/LF |
| `privacy/person_names.py` | `nguon/privacy/person_names.py` | `e1b00921cdd1374876eaa13ce9baa3a79eef7cac7614d2b9854621f728054214` | `e1b00921cdd1374876eaa13ce9baa3a79eef7cac7614d2b9854621f728054214` | nội dung giữ nguyên; UTF-8/LF |
| `privacy/variants.py` | `nguon/privacy/variants.py` | `ec5ba8b6241204841e753480a4cfee526ab57c3c885a59ef431ceddcffa07dcb` | `d83763b71b9eb53cfb29a1c3a5f61660dcf6b1230af08f11307d8beb56a811d4` | import nội bộ tương đối; đổi câu báo lỗi biến thể văn bản; UTF-8/LF |
| `privacy/docx_revisions.py` | `nguon/privacy/docx_revisions.py` | `4ab82b50b0f9ed520fe277a7693023fb85ef80ad98812d6ce0f2a0731ca5fcdd` | `1ea7764c75a8f9b32b8a1c17f23ddcf346b2161eb64a81166c69dfbded1ea2f4` | bỏ mô tả phụ thuộc nhận dạng; giữ thuật toán lịch sử sửa; UTF-8/LF |
| `privacy/excel.py` | `nguon/privacy/excel.py` | `b837f86a9accaea662357b485fb0d835a6deef4ba4e9f8ccffb0bb9a1243fdc7` | `b837f86a9accaea662357b485fb0d835a6deef4ba4e9f8ccffb0bb9a1243fdc7` | nội dung giữ nguyên; UTF-8/LF |
| `privacy/excel_values.py` | `nguon/privacy/excel_values.py` | `6bbcb1c0e19923d13923ca935970199626aca668ec3f23d903ef3e512c22e901` | `6bbcb1c0e19923d13923ca935970199626aca668ec3f23d903ef3e512c22e901` | nội dung giữ nguyên; UTF-8/LF |
| `privacy/leftovers.py` | `nguon/privacy/leftovers.py` | `afc77d19a79b56d12592f123bb78d137fcb60c45e5e079e82be2c0e6ebb35b8c` | `978f8e4dcf0155e2ae1b6c3b3f9ef23085416239e4327ebdef7f48a76144a163` | import nội bộ tương đối; đã chỉnh chú thích ví dụ số tài khoản thành số giả; UTF-8/LF |

Gói import: `engines.e_mask.nguon.privacy`. Import nội bộ tương đối để không cần thêm nguồn ngoài vào `sys.path` hoặc tạo alias `privacy` toàn cục. Giữ thuật toán che, kiểm số và xử lý Word/Excel; không viết thay phần còn thiếu.

**Danh sách số giả/giá trị minh họa được phép:** test quét mọi tệp dưới `nguon/` để chặn chuỗi liền 9–16 chữ số ngoài danh sách theo từng tệp dưới đây. Đây là các ví dụ cố định trong chú thích/docstring, không phải dữ liệu thật; không cho phép thêm số ngoài danh sách hoặc dùng số ở tệp khác. Số tài khoản giả dùng thống nhất là `1912345678901`.

| Tệp (từ nguon) | Số giả/giá trị minh họa được phép | Mục đích |
|---|---|---|
| `privacy/core.py` | `001234567890` | ví dụ dấu phân cách của chuỗi số giả |
| `privacy/detectors.py` | `1250000000`, `1912345678901`, `5000000000` | số tiền minh họa và số tài khoản giả |
| `privacy/excel.py` | `1234567890` | ví dụ chuẩn hóa ô số bằng dãy chữ số tuần tự |
| `privacy/leftovers.py` | `1250000000`, `1912345678901` | số tiền minh họa và số tài khoản giả |

## 3. Phần đã tách và các mục bỏ qua

- Không chép `privacy/ocr_client.py`, `privacy/extract.py`, `privacy/offline.py`, `ocr_settings.py`: loại client, extraction shim, cấu hình và guard kết nối nhận dạng cũ. Mã đã chép không còn chuỗi/import/chỗ gọi OCR, Tesseract, VietOCR.
- Bỏ trường `Extracted.ocr_pages`; sửa chú thích/docstring/thông báo nhắc nhận dạng trong `core.py`, `company_names.py`, `detectors.py`, `variants.py`, `docx_revisions.py`. Giữ xử lý biến thể chữ thuần văn bản.
- Không chép server/API cũ (`privacy/server.py`, `privacy/auto_api.py`) và launcher (`run_privacy.py`, `start_all.py`, `initialize_api.py`): gắn client nhận dạng, kho cục bộ/khóa hoặc vòng đời cũ. Chỉ xem các dòng import/định nghĩa/liên kết Word/Excel trong hai tệp server/API để xác định closure; không import/chạy chúng. API Core mới thuộc lát sau.
- Không chép `privacy/local_ai.py`, `privacy/ai_apply.py`, `privacy/keeplist.py`, `privacy/pending.py`: AI/kho cục bộ/queue cũ ngoài lõi thuần cần giữ. Không tạo đường gọi AI khác.

**Tên nghi dữ liệu/bí mật đã thấy và bỏ qua để lead xét:** `config/`, `privacy/data/`, `privacy/catalog.py`, `tmp/`. Chỉ thấy tên ở cấp cha, **không đọc nội dung/đi vào các mục này**. Không thấy tên `mapping`, `key`, `secret`, `out`, `logs`, `.db`, `.sqlite` hoặc JSON cấu hình ở các cấp đã liệt kê; không dò sâu để tìm. Các thư mục `docs/`, `scripts/`, `tests/`, `privacy/static/`, `__pycache__/` và tệp ngoài `.py` cũng không được duyệt/chép. Không đọc lock/config của nguồn ngoài để kiểm phiên bản.

**Tài nguyên chưa mang theo:** mã `detectors.py` tham chiếu `data/vn_surnames.txt`, `data/vn_places.txt`, `data/common_acronyms.txt`; `leftovers.py` tham chiếu `data/leftover_allowlist.txt`. Các tên lấy từ mã, **chưa kiểm sự tồn tại/nội dung trong data/**. Không tạo từ điển thay thế. Import không đọc tài nguyên; gọi nhánh cần từ điển hiện báo thiếu tệp. Chưa thể công bố tự phát hiện/kiểm hết định danh hoặc cho gửi Cloud. Lead cần cấp whitelist tài nguyên sạch hoặc nguồn từ Core ở lát sau.

## 4. Mức hỗ trợ Word/Excel hiện có

| Phần | Có trong lõi đã chép | Chưa có/giới hạn — trình lead/lát sau |
|---|---|---|
| Word | `core.make_docx` dựng DOCX mới từ văn bản đã che, đoạn + bảng phân cột bằng tab, bỏ một số thuộc tính tác giả; `export_document`/`export_bundle` kiểm văn bản rồi xuất TXT/DOCX/ZIP. `docx_revisions.accept_tracked_changes` chấp nhận lịch sử sửa trên bản RAM. | Không có che DOCX gốc giữ bố cục, đọc Word độc lập với engine nhận dạng, che toàn bộ đầu/chân trang/ghi chú/bình luận/thuộc tính tệp gốc; không có mở che Word sau AI sửa/tách run. Helper lịch sử sửa trả nguyên đầu vào nếu không an toàn, cần bộ kiểm trước khi dùng. Dựng DOCX mới không chứng minh giữ bố cục gốc. |
| Excel giữ cấu trúc | `excel.ExcelWorkbook.mask` sửa XML trong XLSX, giữ phần không đổi/định dạng/ô gộp, kiểm sheet/ô ẩn; xử lý chuỗi shared/inline/rich text, bình luận, đầu/chân trang, một số thuộc tính/drawing. Giữ công thức, không tính lại. | Tên sheet/công thức chứa định danh có thể chặn xuất thay vì được che tại chỗ. Chart/ảnh/pivot và thành phần opaque ngoài tập hỗ trợ có thể chặn. Liên kết ngoài được giữ và đưa vào disclosures, chưa bảo đảm không sót. Chưa có mở che tệp. Không nhận XLS/XLSM/XLSB. |
| Excel bản giá trị | `excel_values.build_values_workbook` dựng XLSX mới từ kế hoạch che, đổi tên sheet đã che, giữ một phần số/ngày, ô gộp/độ rộng/trạng thái ẩn; `verify_values_workbook` rà lại. | Không giữ trọn bố cục/công thức/biểu đồ/ảnh/metadata. Mã cũ có cắt chuỗi ô tới 32.767 ký tự và chuẩn hóa tên sheet; lát sau cần rà theo yêu cầu không cắt ngầm. Tạo bản này không gọi AI. |
| Tiền/ngày và bí danh | Có `numeric_review`, bảo vệ ô số tài chính/ngày; bí danh nguồn dạng `[CONG_TY_001]`. | Chưa chuyển sang `[[...]]`, CSDL Core, mã yêu cầu/đúng module-người gửi, mở che mềm, vị trí chưa mở, bảo đảm không còn tệp gốc trên đĩa: thuộc các lát 2–4/8. |

Helper `encrypt_mapping`/`decrypt_mapping` là mã thuần đã giữ để tận dụng lõi; không kèm bảng đối chiếu/khóa và không kích hoạt kho cũ. Quyết định mới lưu bảng ở Core không mã hóa cột; lead xử lý helper khi tích hợp.

## 5. Kiểm và điểm cần lead chốt

Test thuần/mock tại `tests/test_nguon_mask.py`: import mọi module trong tiến trình Python sạch (cấm mạng/tiến trình dịch vụ/ghi tệp/đọc tài nguyên), allowlist chính xác mã và tài liệu (không dữ liệu/khóa/cache), quét chuỗi nhận dạng và chuỗi 9–16 chữ số theo danh sách số giả ở §2, so đúng cột SHA sau chỉnh, che văn bản giữ tiền/ngày, DOCX dựng mới/lịch sử sửa, XLSX thường/ẩn/bản giá trị. Kiểm định dạng dùng workbook DEMO hợp lệ do openpyxl sẵn có tạo trong RAM: cùng byte phải đi qua với `.xlsx`, bị từ chối đúng lý do với `.xls/.xlsm/.xlsb`; tệp hỏng được kiểm riêng. Không server, PostgreSQL, Word COM hoặc dịch vụ ngoài. Test không chứng nhận các khoảng thiếu nêu trên.

Kết quả ngày 06/11/2026 (thứ tự **ok / fail / error / skip**):

| Lần đo | Kết quả | Ghi chú |
|---|---|---|
| Trước sửa lõi: ba module hồi quy hiện có | **23 / 0 / 0 / 0** | `tests.test_g3_mask_1`, `tests.test_g3_goi_mask_move`, `engines.e_mask.tests.test_doc_lap` |
| Test mới trước khi chép nguồn | **0 / 3 / 8 / 0** | 11 ca đỏ đúng lý do chưa có nguồn/bảng SHA; đây là kiểm âm trước triển khai, không phải lỗi nền |
| Sau: ba module hồi quy + test mới | **34 / 0 / 0 / 0** | 23 ca giữ nguyên + 11 ca mới; không thêm lỗi so nền trong phạm vi đã chạy |

Vòng 2 ngày 07/11/2026, cùng bốn module trên; đếm theo phương thức test (hai failure của unittest ở lượt trước là hai subtest trong một phương thức SHA):

| Lần đo | ok / fail / error / skip | Ghi chú |
|---|---|---|
| Trước sửa vòng 2 | **33 / 1 / 0 / 0** | 34 phương thức; test SHA lỗi ở hai subtest `detectors.py` và `leftovers.py` sau khi lead chỉnh chú thích |
| Sau sửa vòng 2 | **37 / 0 / 0 / 0** | thêm quét số; tách tệp hỏng, đuôi chưa hỗ trợ và XLSX hợp lệ; không thêm lỗi trong phạm vi đã chạy |

Dùng đúng Python/PYTHONPATH handoff, `-X utf8 -B -m unittest`, không chạy `tests.test_v3`/`tests.test_v7`. Không đo lại toàn bộ nền v4 hoặc PostgreSQL.

**Giữ byte khi gộp:** `.gitattributes` đã có quy tắc `/engines/e_mask/nguon/privacy/*.py -text`, giữ nguyên byte khi Git checkout/đóng gói, không chuyển LF/CRLF. SHA sau chỉnh ở bảng tính trên byte UTF-8/LF hiện tại; nếu tệp bị đổi byte thì test SHA sẽ báo đỏ. Vòng 2 chỉ đối chiếu quy tắc hiện có, không sửa `.gitattributes`.

Lead chốt: tài nguyên detector sạch; lệch pin thư viện trước đóng gói; phần Word giữ bố cục/che-mở tệp còn thiếu cho lát 8; launcher/contract theo quyết định mới. Xem [nguon/PHU-THUOC.md](nguon/PHU-THUOC.md) để phân biệt phụ thuộc thực import, bản đã cài và pin lịch sử. SDK cuối còn chờ lát 34; không đổi SDK, capability, lock hoặc bộ cài trong MASK-1.

## 6. MASK-2 — bảng riêng và chuyển danh mục

Migration mới: `src/kho_tri_thuc/core/sql/113_mask_dinh_danh.sql`, không phụ thuộc hai số migration đang làm ở lát khác. Chỉ lead áp trên Core DEMO/test PostgreSQL 16+; worker chưa chạy PostgreSQL. Schema `mask` chưa có trong các migration đã khảo sát trước lát này.

Guard đầu migration kiểm `lower('Ô')='ô' AND lower('Đ')='đ'` trước khi thay đổi CSDL. Nếu locale không hạ được chữ Việt hoa (ví dụ LC_CTYPE `C`), migration dừng với `MASK_LC_CTYPE_KHONG_HO_TRO_TIENG_VIET` và hướng dẫn rõ; không tự chọn collation hoặc yêu cầu ICU. Lead cần dùng CSDL DEMO/test có LC_CTYPE phù hợp. Chuẩn hóa SQL/Python cùng dùng NFC, lower và tập khoảng trắng tường minh Unicode White_Space cộng U+001C–U+001F; gộp thành một dấu cách rồi bỏ dấu cách hai đầu, không dùng lớp `[:space:]` phụ thuộc locale.

| Bảng | Nội dung |
|---|---|
| `mask.dinh_danh` | Giá trị gốc, giá trị chuẩn NFC/không phân biệt hoa thường/gộp khoảng trắng, nhóm, mã Junsky nếu có, bí danh chính thức, cột bí danh tạm cũ, nguồn. Duy nhất theo giá trị chuẩn trong cùng vùng DEMO/thật, không chia theo pháp nhân. Bí danh chính thức và tạm cũng duy nhất trong vùng để mở che không nhập nhằng. |
| `mask.yeu_cau` | Mã UUID do CSDL Core cấp, module, người gửi, tài liệu, trạng thái đang xử lý/đã đóng, thời điểm tạo/đóng; mảng bí danh tạm đã dùng dành cho quy tắc dọn ở lát 4. |
| `mask.cho_duyet` | Cụm gốc mới, nhóm, bí danh tạm `[[MASKTAM-<UUID không gạch>]]`, nguồn và mã yêu cầu. Chỉ tạo nền dữ liệu; chưa có màn duyệt hay thao tác duyệt/dọn. |

Không mã hóa cột. Hai role `vai_doi_cau_truc_mask`/`vai_chay_mask` theo tiền tố test của Core đều NOLOGIN, không SUPERUSER/BYPASSRLS, không membership; không cấp cho login module hoặc login Core. Chỉ role engine đọc/ghi bảng. Login Core có USAGE schema và EXECUTE `mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)`, không có SELECT trực tiếp; hàm SECURITY DEFINER kiểm đúng session login Core. Core phải truyền danh tính/tài liệu đã xác minh; kiểm phiên và quyền mở che đầy đủ thuộc lát 3. Không dùng cửa cấp mã này như API nhận danh tính tự khai từ module.

**Rào DEMO và lý do không đăng ký xuất:** bí danh chung tập đoàn nên ba bảng không có `phap_nhan_id`, không thuộc tập bảng theo pháp nhân của helper DEMO 023/047 hoặc sổ xuất 048. Cố ý **không gọi `loi.xuat_dang_ky_bang`** vì sẽ cấp quyền đọc cho vai xuất, trái yêu cầu bảo vệ định danh/cụm gốc. Cả ba bảng có `la_demo` bắt buộc, FORCE RLS đối chiếu `ktt.mask_la_demo`; thiếu context không đọc/ghi được, FK chờ duyệt ghép `(yeu_cau_id,la_demo)` chặn liên kết chéo. Chỉ tách DEMO/thật, không tách danh mục theo công ty. Dọn dữ liệu thử của khối này phải qua role engine trong context DEMO; không suy từ công cụ dọn từng pháp nhân. Test PG riêng kiểm rào này; chưa khẳng định toàn bộ gate PG `test_g2_30`/`test_dm_1` đã đạt.

**Tiền tố triển khai để lead trình/chốt:** `MASKCT`, `MASKCN`, `MASKDC`, `MASKMST`, `MASKTK`, `MASKKHAC`; năm nhóm đầu tương ứng công ty/cá nhân/địa chỉ/MST/tài khoản, nhóm còn lại của lõi dùng `MASKKHAC`. Số thứ tự do sequence CSDL cấp, tối thiểu bốn chữ số và không cắt số lớn. Mã Junsky được giữ nguyên và bọc `[[...]]`; SQL lẫn công cụ từ chối mã bắt đầu bằng `MASK` (không phân biệt hoa thường), kể cả mã không có dấu gạch. Đây là ràng buộc ngăn trùng, **không phải xác nhận danh mục Junsky thật không dùng họ tiền tố đó**. Không đổi mã Junsky khi gặp trùng; báo lỗi để lead chốt trước vận hành.

### Công cụ chuyển

`tools/chuyen_danh_muc_mask.py` chỉ đọc **một tệp người vận hành chỉ định**; không dò thư mục, không tự mở cấu hình, không tự nối CSDL. Đầu vào được hỗ trợ là bản xuất JSON UTF-8 (có thể có BOM): list quy tắc hoặc object có `rules` là list; mỗi mục dùng `source`, `category`, tùy chọn `enabled`, `canonical`, `token`. Nếu có mã Junsky đã được đối chiếu riêng, người vận hành bổ sung rõ trường `ma_junsky`; **không lấy mã từ `token`**.

Gọi qua Python: `chuyen_danh_muc(duong_dan, ket_noi, la_demo=True, chay_thu=True)`. Kết nối do Core truyền vào, có quyền engine/provisioning. Chạy thử chỉ SELECT, không đổi GUC/cấp số/ghi bảng; nếu có kết nối, caller đặt sẵn `ktt.mask_la_demo` đúng vùng. Chạy ghi phải chọn `chay_thu=False`, công cụ đặt GUC cục bộ rồi phục hồi; từng dòng lỗi có savepoint, không ghi đè dòng đã có và không tự commit transaction ngoài của caller. Có thể dùng `main(argv, ket_noi=...)` trong lệnh vận hành do Core bọc. CLI độc lập: `python tools/chuyen_danh_muc_mask.py <tệp DEMO> --chay-thu`. Không có kết nối thì số trước/sau là 0/0, chỉ xác nhận kiểm tệp, **không phải số dòng CSDL đã đo**; các mục hợp lệ được đếm là **chưa đối chiếu**, không đoán sẽ thêm hay đã có. `--ghi` thiếu kết nối báo lỗi. Mặc định vùng DEMO; `--van-hanh` chỉ dành vận hành thật được xác nhận riêng, chưa chạy trong lát này.

Đầu ra chỉ số dòng trước/sau, số lỗi theo loại và khi chạy thử có số **sẽ thêm**, **sẽ bỏ qua (đã có)**, **sẽ vào danh sách chờ**, **chưa đối chiếu**, gồm tổng và số theo nhóm định danh với nhãn nghiệp vụ tiếng Việt; không in giá trị, tên tệp, đường dẫn, mã đối tượng hay lỗi driver. Mục sẽ thêm phải mới và không xung đột sau đối chiếu CSDL; mục bỏ qua phải đã có cùng giá trị chuẩn/nhóm/mã. Mục tên khác hoặc nhiều tên chung token được đếm vào danh sách chờ dự kiến và vẫn báo lỗi `ten_khac`; đây là số cần xử lý ở lát sau, **công cụ chưa ghi `mask.cho_duyet`**. Mục tắt, sai định dạng, trùng trong tệp hoặc xung đột được báo lỗi riêng, không tính là sẽ thêm. Thiếu quyền/lỗi đối chiếu không công bố dự kiến đã xác nhận cho các mục chưa kiểm được. Không tự tách hoặc làm mất quan hệ tên khác. Chạy lại cùng giá trị/nhóm/mã không thêm dòng; khác nhóm/mã báo xung đột. Bí danh đơn ngoặc cũ không chuyển sang cột tạm mới: cột này dành cho bí danh tạm mới đã được duyệt theo CD-101.

### NỢ — bàn giao lát 3/4/6

- **Lát 3 — rào DEMO:** RLS hiện dựa vào GUC `ktt.mask_la_demo`, chưa phải bằng chứng phiên đã xác minh. Lát 3 phải đặt GUC bên trong hàm SECURITY DEFINER, suy từ phiên đã được Core xác minh; không tin giá trị do caller tự đặt.
- **Lát 3 — cấp mã yêu cầu:** `cap_ma_yeu_cau` hiện nhận `p_la_demo` do người gọi khai. Lát 3 phải suy vùng DEMO/thật từ pháp nhân/phiên đã xác minh, cùng kiểm module, người gửi và tài liệu.
- **Lát 4/6 — CD-044:** chưa có công cụ xóa sạch DEMO cho cả ba bảng `mask.dinh_danh`, `mask.yeu_cau`, `mask.cho_duyet`. Cần xử lý quan hệ tham chiếu và rào DEMO của danh mục chung; không mặc nhiên dùng công cụ dọn theo pháp nhân.
- **Lát 4 — duyệt cụm gốc:** `cho_duyet.cum_goc` hiện cho phép `[`/`]` trong khi `dinh_danh.gia_tri` cấm; phải xử lý nhất quán khi duyệt, không để lỗi chuyển cụm sang danh mục.
- **Lát 3/4 — mã Junsky:** một mã Junsky chỉ có một tên chuẩn trong cùng vùng DEMO/thật (bí danh không phân biệt hoa/thường là duy nhất). Tên khác dùng chung mã/token phải chờ quy tắc chọn tên chuẩn và quan hệ tên khác; không tự cấp lại mã hoặc tạo thêm tên chuẩn.

### Mã Junsky trong nguồn hiện có

Đối chiếu **chỉ mã trong `nguon/privacy/`**: `core.validate_rules` trả `source`, `token`, `category`, `enabled`, tùy chọn `canonical`; `TOKEN` nhận dạng `[CONG_TY_001]` và `suggest`/`next_token` cấp số theo nhóm. Không thấy trường hay xử lý `junsky` trong tập mã này. `privacy/catalog.py` không có trong gói nguồn đã chép, chưa đọc vì ngoài tập mã sạch được mang theo. Vì vậy **chưa đủ căn cứ xác nhận định dạng lưu danh mục gốc hoặc danh mục Mask v2 giữ mã Junsky đến đâu**; không suy luận từ dữ liệu thật. Công cụ hiện nhận bản xuất quy tắc nêu trên, chưa được chứng nhận đọc trực tiếp tệp kho danh mục gốc chưa biết cấu trúc. Lead cần cấp mã lưu/xuất danh mục đã kiểm sạch hoặc đặc tả bản xuất để xác nhận trước chuyển thật; không cấp danh mục thật cho test.

Test `tests.test_mask_2`: thuần/mock với tệp DEMO tự sinh; các ca PostgreSQL có nhãn `CHUA_KIEM`, chỉ lead chạy khi cung cấp `KHO_PG_DSN_TEST`. Không đổi SDK, contract, launcher hoặc capability trong MASK-2.

Kết quả worker ngày 07/11/2026 (thứ tự **ok / fail / error / skip**, đúng Python/PYTHONPATH handoff):

| Phạm vi | Trước | Sau |
|---|---|---|
| `tests.test_cd060_vong_doi` + `tests.test_noi_quan_tri` | **62 / 0 / 0 / 4** | Giữ nguyên; chạy cùng test mới ở hàng dưới |
| Hai module trên + `tests.test_mask_2` | Test mới trước triển khai: **0 / 0 / 1 / 0**, lỗi import vì chưa có công cụ | **88 / 0 / 0 / 12**; riêng test mới **26 / 0 / 0 / 8** |
| Kiểm thêm `tests.test_g2_30` + `tests.test_dm_1`, chỉ thuần | Không đo lại trước | **58 / 0 / 0 / 30** |

Không có lỗi mới trong phạm vi đã chạy; không kết luận toàn bộ nền v4 hoặc các ca PG đã đạt. Chưa chạy/dừng PostgreSQL, server hoặc chuyển danh mục thật. Kiểm UTF-8 hợp lệ cả bốn tệp và `git diff --check`; không commit. Lead cần chạy 8 ca PG mới, đối chiếu gate PG rào DEMO/xuất; chốt họ tiền tố và bản xuất danh mục/mã Junsky trước vận hành.

Vòng 2 ngày 07/11/2026, riêng `tests.test_mask_2`, đúng Python/PYTHONPATH handoff, không đặt `KHO_PG_DSN_TEST`:

| Lần đo | ok / fail / error / skip | Ghi chú |
|---|---|---|
| Trước sửa vòng 2 | **26 / 0 / 0 / 8** | 34 ca; chỉ thuần/mock |
| Lượt đầu sau sửa | **33 / 1 / 0 / 9** | Assertion cũ cấm nhãn nhóm chung “Công ty”; đã sửa để kiểm tên DEMO đầy đủ |
| Sau sửa vòng 2 | **34 / 0 / 0 / 9** | 43 ca; thêm tám ca thuần và một ca PG |

Không có lỗi mới trong phạm vi thuần/mock đã chạy. Chín ca PG vẫn **CHƯA KIỂM**: lead chạy để xác minh locale/regex SQL, các vai có sẵn, login Core không đọc trực tiếp bảng, module không gọi cửa cấp mã và công cụ ghi dưới `vai_chay_mask` có rào DEMO. Chưa kiểm một CSDL LC_CTYPE `C` thực tế; guard phải từ chối trước khi áp. Không đổi SDK/thư viện, không chạy dịch vụ, không commit. Các nợ lát sau được ghi rõ ở mục **NỢ** bên trên.

## 7. MASK-3a — lõi che/mở che văn bản, chưa nối Core

Ngày 07/11/2026, CD-101, Quyết định cuối §2.1 lát 3 + §3 + §5.1 mẫu 1–4. Chỉ thêm `che_van_ban.py`, `kho_bo_nho.py`, `tests/test_che_van_ban.py` và cập nhật tài liệu này. Không đổi nguồn privacy/SHA, migration, SDK, launcher hoặc contract; không công bố capability và không gọi AI.

### Xử lý và giao diện kho nội bộ

- `che(van_ban, dinh_danh_da_biet, kho)`: định danh tùy chọn là list `{gia_tri, nhom}` hoặc `None`. Kiểm trần trên đầu vào gốc trước xử lý: văn bản không rỗng, tối đa 500.000 ký tự; tối đa 500 định danh, giá trị 2–300 ký tự, nhóm thuộc nhóm hiện có của privacy và tối đa 20 ký tự. Sai/vượt thì từ chối bằng thông báo cố định tiếng Việt, không đính kèm định danh. Không cắt đầu vào.
- Dùng `KnownText`, `company_spans`, `person_names`, các lớp `detectors` và `leftovers` của privacy; không dùng `suggest` vì hàm nguồn tự giới hạn 500 dòng. Danh mục kho và định danh đã biết đều được dò; tên dài ưu tiên trước để tránh che một phần. Dò qua NFC có bản đồ tọa độ, giữ nguyên các ký tự không thay trong văn bản gốc. Tiền/ngày được bảo vệ trước thay; đối chiếu thêm tập giá trị và số lần xuất hiện từ **văn bản gốc đầy đủ** với bản che, bên cạnh `numeric_review` cho các số ngoài vùng che.
- Kết quả có `ma_yeu_cau`, `van_ban_da_che`, `con_sot`, `kiem_tien_ngay` (boolean), `gui_duoc`, `so_cho_thay`, `bi_danh` (`bi_danh`, `nhom`, `nguon=chinh_thuc/tam`), `cho_duyet.so_cum_vua_them`, `canh_bao`. Cụm mới chỉ ghi vào kho, không trả trong kết quả, thông báo hoặc nhật ký. Còn sót trả `nhom` và `vi_tri` (offset ký tự `[bat_dau, ket_thuc)`, dòng/cột từ 1) trong **văn bản sau che**, ánh xạ đúng cả chữ Việt NFD; thiếu tài nguyên trả lý do chung. Không trả cụm gốc. Khi không đủ điều kiện gửi, `gui_duoc=False` và **`van_ban_da_che=None`**, không công bố văn bản chưa kiểm đạt. Đây là lựa chọn nội bộ cần đối chiếu khi làm contract ở lát sau.
- `mo_che(van_ban_co_bi_danh, ma_yeu_cau, kho, *, dong_viec=False)`: kho kiểm mã/phiên trước mọi tra ngược. Không phân biệt hoa/thường, bỏ khoảng trắng (kể cả xuống dòng) bên trong bí danh và dấu ngoặc bị tách. Tra toàn bảng chính thức/tạm, không giới hạn ở bí danh đã dùng trong một yêu cầu. Không sửa nội dung AI thêm. Bí danh lạ/hỏng vẫn giữ nguyên, trả `bi_danh_khong_ro` kèm offset ký tự `[bat_dau, ket_thuc)` trong đầu vào, dòng/cột bắt đầu từ 1; `mo_day_du=False`. Dạng thiếu một ngoặc cũng báo chưa mở. Chỉ đóng theo yêu cầu rõ ràng khi không còn bí danh chưa mở; còn mục chưa mở thì giữ `DANG_XU_LY` để bảo vệ bí danh tạm. Không suy đoán nếu nội dung đã mất hoàn toàn dấu hiệu bí danh.

`Kho` (Protocol trong `che_van_ban.py`) là port được tiêm, không SQL/driver hoặc import Core:

| Thao tác | Trách nhiệm |
|---|---|
| `giao_dich` | Bao trọn một lần che/mở; lỗi phải rollback mã yêu cầu, hàng chờ, tham chiếu, số lần gặp và dấu chống đếm lặp |
| `liet_ke_dinh_danh`, `tra_bi_danh(gia_tri_chuan)` | Đọc danh mục chính thức và cụm tạm trong đúng vùng; chuẩn hóa NFC/lower/gộp khoảng trắng khớp migration 113 |
| `cap_bi_danh_tam`, `ghi_cho_duyet` | Cấp `[[MASKTAM-<UUID không gạch>]]`, ghi cụm mới; trả bản ghi có thẩm quyền + cờ vừa thêm cho `so_cum_vua_them`; chưa tăng `so_lan_gap` |
| `ghi_nhan_gap_lai(ma_yeu_cau, cum_chuan, nhom)` | MASK-3c: tính cả lần đầu của cụm tạm; tăng nguyên tử, mỗi mã yêu cầu + cụm chuẩn chỉ tính một lần; cụm chính thức không tăng |
| `tao_yeu_cau`, `doc_yeu_cau`, `dong_yeu_cau` | Kho gắn module/người gửi/tài liệu từ phiên tin cậy; đọc từ chối mã sai, sai phiên/vùng hoặc đã đóng |
| `ghi_bi_danh_da_dung` | Giữ tham chiếu bí danh tạm, kể cả khi mở bí danh của yêu cầu khác trong bảng chung |
| `tra_dinh_danh(bi_danh_chuan)` | Tra chính thức, cột tạm cũ và hàng chờ; không trả bảng đối chiếu trong kết quả che |

`KhoBoNho` chỉ là DEMO/test, vùng DEMO cố định; `theo_phien` là fixture mô phỏng phiên khác dùng chung bảng, không phải xác thực. Có khóa RAM/giao dịch rollback; chỉ giữ danh mục/cụm chờ/thông tin yêu cầu, không ghi tệp hay lưu toàn văn đầu vào. Nạp danh mục DEMO dùng mã Junsky tường minh hoặc tiền tố MASK-2; từ chối trùng và không cắt số thứ tự lớn. Không có API vận hành hay màn duyệt trong lát này.

### Nợ và điểm lead cần chốt

1. **Nợ rào DEMO/cấp mã MASK-2 vẫn còn ở tích hợp Core:** hàm che/mở không nhận hoặc tin cờ DEMO caller. Kho RAM tự quyết DEMO; kho PostgreSQL ở lát sau phải suy vùng từ phiên/pháp nhân đã được Core xác minh, kiểm module/người gửi/tài liệu, đặt GUC bên trong hàm SECURITY DEFINER. Kết quả mock **không chứng minh** đã khép nợ RLS/GUC hay cửa cấp mã hiện có của migration 113.
2. **Tài nguyên detector sạch chưa được cấp:** thiếu một từ điển hoặc lỗi một lớp dò → còn sót báo chưa kiểm đủ và chặn gửi. Các ca thành công dùng mock từ vựng DEMO tường minh, dọn cache sau từng ca. Không thêm từ điển thay thế hoặc khẳng định tự nhận diện hết định danh ngoài khả năng heuristic của nguồn. Lead cấp whitelist tài nguyên trước kiểm tích hợp.
3. **Rào regex nguồn:** đã gặp lượt test bị chậm ở một khối 500.000 ký tự liền nhau; dừng riêng tiến trình test bằng ngắt bàn phím, không tác động dịch vụ. Lớp bọc đánh dấu chưa kiểm cho khối không có khoảng trắng dài hơn 1.024 ký tự (thay bằng NUL cùng chiều dài chỉ trong bản dò), luôn chặn gửi và không công bố văn bản. Không cắt đầu vào, không sửa lõi nguồn. Trần 500.000 vẫn được kiểm bằng văn bản thông thường đúng trần; có ca riêng cho khối liền rất dài. Lead cần đánh giá rào hiệu năng này khi chốt contract/DEMO.
4. Hành vi giữ yêu cầu đang xử lý khi còn bí danh chưa mở và `van_ban_da_che=None` khi bị chặn cần được giữ/đối chiếu ở lát route và contract; chưa đăng ký mẫu trao đổi công bố. Không gửi mã yêu cầu, bảng đối chiếu hoặc cả object kết quả này ra Cloud; lát cổng AI chỉ lấy văn bản đã che sau kiểm điều kiện.

### Kiểm thuần/mock

Dùng đúng Python/PYTHONPATH handoff, `-X utf8 -B -m unittest`, `PYTHONDONTWRITEBYTECODE=1`, không đặt DSN PG; không chạy `tests.test_v3`/`tests.test_v7`, không mở/đóng PostgreSQL hoặc server. Test mới gồm khứ hồi chính thức/tạm, AI sửa bí danh, chưa mở kèm vị trí, kiểm quyền/mã đóng, số tiền/ngày, thiếu tài nguyên/lỗi detector, rollback/lỗi kho không lộ nội dung, chuẩn hóa chữ Việt, đúng/vượt trần và 501 cụm do detector tìm được không bị cắt theo trần định danh đã biết.

Thứ tự số: **ok / fail / error / skip**. Kết quả trước lấy trên nhánh `lat/mask-3a` sạch; số skip PG theo test thực tế hiện có (khác số lịch sử MASK-2 ở trên).

| Phạm vi | Trước | Sau |
|---|---|---|
| Cả thư mục `engines/e_mask/tests` | **20 / 0 / 0 / 0** | **57 / 0 / 0 / 0** |
| `tests.test_mask_2` | **36 / 0 / 0 / 10** | **36 / 0 / 0 / 10** |
| Tổng | **56 / 0 / 0 / 10** | **93 / 0 / 0 / 10** |

Không thêm lỗi trong phạm vi đã chạy; 10 ca PG vẫn **CHƯA KIỂM**, không kết luận toàn bộ nền v4 hoặc tích hợp Core. Kiểm UTF-8 đúng dấu và diff đúng bốn tệp handoff; không commit, lead giữ việc commit/gộp.

### MASK-3a vòng 2 — khép ba lỗi chặn từ review chéo

Ngày 07/11/2026; chỉ sửa `che_van_ban.py`, `tests/test_che_van_ban.py` và tài liệu này. Không sửa nguồn privacy/SHA, SDK, thư viện hoặc kho.

- Hậu kiểm vẫn chạy `detectors`/`leftovers`, bổ sung luật không phân biệt hoa/thường cho “công ty …”, nhãn Họ và tên/Họ tên/Ông/Bà/Địa chỉ/MST/Mã số thuế/CCCD/CMND/Số tài khoản/STK/Điện thoại và MST 10/13 chữ số liền hoặc phân cách bằng chấm, gạch, khoảng trắng. Phần chưa che vào `con_sot` chỉ có loại/vị trí và chặn gửi. Mẫu MST mơ hồ không có ngữ cảnh tiền rõ cũng bị chặn; có thể chặn nhầm theo nguyên tắc ưu tiên không lọt. Không che riêng tiền tố công ty khi còn tên nối tiếp; trường địa chỉ đã được lõi nhận một phần được xét che trọn trường.
- Từ chối định danh đã biết chứa dạng tiền/ngày, kể cả `0.00`, `0,00`, `0.000`, hoặc trùng số tiền/ngày phát hiện trong đầu vào, bằng lỗi tiếng Việt cố định trước cấp mã yêu cầu. `kiem_tien_ngay` so `Counter` loại/giá trị/số lần từ bản gốc và bản sau che; mất, đổi hoặc thêm tiền/ngày đều không đạt. Giá trị số ngay trong trường có nhãn định danh không tự coi là tiền; không đưa giá trị so sánh vào đầu ra.
- Mảnh bí danh có một ngoặc mở/đóng, thiếu ngoặc cuối hoặc khoảng trắng chen cũng vào `bi_danh_khong_ro` kèm vị trí. Không suy đoán giá trị gốc. `dong_viec=True` vẫn giữ yêu cầu đang xử lý nếu còn mảnh chưa mở.

Lệnh: đúng Python/PYTHONPATH handoff, `-X utf8 -B -m unittest discover -s engines\e_mask\tests`; không dùng `-t .` vì thư mục test không có `__init__.py`. Không chạy PG/server hoặc hai module test bị cấm.

| Lần đo | ok / fail / error / skip | Ghi chú |
|---|---|---|
| Nền trước sửa | **57 / 0 / 0 / 0** | Toàn bộ thư mục test engine |
| Test tái hiện trước sửa code | **— / 41 / 6 / 0** | 66 phương thức; fail/error ở hàng này tính cả subtest, không suy số ok bằng phép trừ; error do chưa có hàm so tập và chưa có vị trí còn sót |
| Lượt đầu sau sửa | **64 / 1 / 1 / 0** | Hậu kiểm bắt phần địa chỉ chỉ được che một phần; fixture giả lập kho cũ cần mock để bỏ qua kiểm đầu vào mới |
| Sau hoàn tất vòng 2 | **67 / 0 / 0 / 0** | Thêm 10 phương thức so với nền; cả ba lỗi đã có test đỏ trước sửa và xanh sau sửa |

Không thêm lỗi trong phạm vi engine đã chạy. Các ca PG/nợ tích hợp Core và tài nguyên detector sạch nêu trên vẫn chưa kiểm trong lát này. Lead giữ commit/gộp; cần giữ cấu trúc vị trí còn sót và quy tắc chặn khi nối route/contract. Không commit.

### MASK-3a vòng 3 — phạm vi bản 1 theo QD-TAM-20261107-03

Ngày 07/11/2026; chỉ sửa `che_van_ban.py`, `tests/test_che_van_ban.py` và tài liệu này.

- Hậu kiểm trường có nhãn lấy giá trị ở dòng sau và nhiều dòng tới dòng trống, nhãn kế hoặc dấu phân cột; giữ tọa độ trên bản sau che, kể cả CRLF/NFD. Bổ sung nhãn email/điện thoại/tài khoản và dò độc lập với detector cho CCCD/CMND 9/12 chữ số, điện thoại Việt Nam, email; STK 6–19 chữ số được kiểm trong trường có nhãn. Giá trị còn sót chặn gửi, không công bố văn bản. Mẫu số không có ngữ cảnh tiền rõ có thể bị chặn thừa.
- **Giới hạn đã biết theo QD-TAM-20261107-03:** tên người không nhãn, viết thường, chưa có trong bảng định danh có thể không được nhận diện. Đây là phạm vi bản 1 đã chốt, không phải cam kết không sót mọi tên người. Bản 1 chưa gửi Cloud. Trước khi bật Cloud ở bản 2, cần bổ sung dò bằng Local AI qua cổng AI chung hoặc bắt buộc đối tác có trong bảng định danh; lát này không triển khai hai phương án đó.
- Danh sách định danh khai cho `che` bị từ chối trước giao dịch nếu chỉ gồm số/dấu phân cách hoặc có dạng tiền/ngày, kể cả `$`, `₫`, `đ`, `VND`, `USD`, ngày viết chữ như “ngày 30 tháng 10 năm 2026” và “30 tháng 10”. Số định danh do detector tìm hoặc có sẵn trong bảng kho vẫn được xử lý theo ngữ cảnh; không dùng khai số trực tiếp để che mất tiền/ngày. Kiểm trước–sau dùng `Counter` loại/giá trị/số lần, gồm ký hiệu tiền, ngày số và ngày viết chữ; lệch thì `kiem_tien_ngay=False`, chặn gửi. Loại tiền còn sau bí danh tài khoản không bị coi là định danh còn sót.
- Mở che vẫn chỉ tra mã đầy đủ hợp lệ. Mảnh còn lại được dò trên bản bỏ khoảng trắng có bản đồ tọa độ gốc: chấp nhận `?` để nhận ra dấu vết mã hỏng, không dùng `?` để tra giá trị gốc. Ngoặc lẻ cạnh tiền tố bí danh hoặc mã trần khớp mã đã cấp đều trả `bi_danh_khong_ro`, `mo_day_du=False`, giữ yêu cầu `DANG_XU_LY` dù yêu cầu đóng. Kho RAM chưa lưu mã chính thức theo từng yêu cầu, nên dò bảo thủ cả mã chính thức/tạm trong bảng cùng vùng đã xác minh; có thể chặn thừa nếu AI nhắc mã đó như văn bản thông thường. Không thêm trạng thái hay thay port kho trong lát này.
- Hiệu năng: mẫu số/bí danh dùng lớp ký tự với độ dài hữu hạn, không lượng từ lồng; bỏ quét bí danh khi không có ngoặc; phần kiểm ngữ cảnh tiền chỉ đọc cửa sổ 180 ký tự trước số thay vì quét lại cả đầu dòng. Test ba chuỗi 500.000 ký tự (`1; `, `1, `, `1 ` lặp) đo toàn bộ `che` với detector thật/từ vựng DEMO mock, ngưỡng xử lý 10 giây mỗi chuỗi. Tiến trình test con có timeout 12 giây gồm khởi tạo, chỉ giới hạn test, không thao tác PG/server.

Kiểm toàn bộ `engines/e_mask/tests` bằng đúng Python/PYTHONPATH handoff, `-X utf8 -B -m unittest discover -s engines\e_mask\tests`:

| Lần đo | ok / fail / error / skip | Ghi chú |
|---|---|---|
| Nền trước sửa | **67 / 0 / 0 / 0** | 28,471 giây |
| Test tái hiện trên mã nền | **68 / 45 / 1 / 0** | 77 phương thức; 68 phương thức đạt, fail/error đếm theo subtest nên không cộng thành tổng phương thức; cả ba lỗi chức năng đều đỏ, hai chuỗi hiệu năng timeout |
| Sau sửa lần 1 | **74 / 2 / 1 / 0** | 77 phương thức; còn hiệu năng, hậu tố loại tiền tài khoản và fixture khai số trực tiếp cũ |
| Sau sửa lần 2 | **76 / 2 / 0 / 0** | 78 phương thức; còn hiệu năng và một assertion mới thay chuỗi không làm đổi dữ liệu |
| Cuối, sau sửa assertion | **77 / 1 / 0 / 0** | 78 phương thức, 44,232 giây; ba lỗi chức năng xanh, còn một lỗi hiệu năng mới |

**Chưa đạt nghiệm thu hiệu năng:** lần cuối `1; ` đạt **7,027 giây**, `1, ` đạt **6,179 giây**, nhưng `1 ` vẫn timeout **12 giây**. Đã dừng tối ưu sau hai lượt sửa theo quy tắc AGENTS.md; giữ test đỏ để lead xử lý tiếp, không nới ngưỡng. Có **một lỗi mới so với nền engine** là test hiệu năng này; không kết luận toàn bộ nền v4. Lượt đo đầu chưa đặt timeout đã phải ngắt riêng tiến trình test, không tác động dịch vụ.

Chỉ thay đúng ba tệp được phép, UTF-8 hợp lệ và `git diff --check` đạt. Không commit, đổi SDK/thư viện, gọi dịch vụ hay chạy/dừng PG/server. Lead cần xử lý tiếp hiệu năng trước nghiệm thu và đối chiếu việc dò mã trần bảo thủ trên cả bảng khi thiết kế kho Core; các nợ PG/tài nguyên detector sạch/tích hợp Core nêu trên vẫn chưa kiểm.

## 8. MASK-3c — đếm gặp lại cụm tạm, chống đếm lặp khi retry

Ngày 07/11/2026; lát C trong `docs/47-core/g3/KS-MASK-3B-NOI-CORE.md`. Chỉ sửa `che_van_ban.py`, `kho_bo_nho.py`, `tests/test_che_van_ban.py` và tài liệu này; không sửa Core/CSDL, SDK hay đầu ra mẫu 1–4.

**Chọn thêm port `ghi_nhan_gap_lai(ma_yeu_cau, cum_chuan, nhom) -> None`.** Sau khi có bí danh hợp lệ, engine gọi port này cho mọi vị trí được che bằng bí danh tạm, kể cả cụm vừa tạo và cụm tạm đã có. Cụm chính thức không ghi nhận. `nhom` lấy từ bản ghi kho có thẩm quyền; không tạo lại bí danh khi gặp cụm tạm.

- `ghi_cho_duyet` chỉ tạo cụm nếu thiếu và trả cờ vừa thêm; bản ghi RAM mới bắt đầu `so_lan_gap=0`. `ghi_nhan_gap_lai` tính cả lần đầu thành 1 trong cùng `giao_dich`. Kho PostgreSQL nối sau phải giữ cách tách này, không vừa tự tăng trong `ghi_cho_duyet` vừa tăng lại ở port mới.
- Khóa chống lặp là **mã yêu cầu + cụm chuẩn hóa**, không gồm nhóm và không phải từng vị trí xuất hiện. RAM giữ `cum_da_gap` trong từng yêu cầu; chuẩn hóa NFC/lower/gộp khoảng trắng như tra danh mục. Cùng yêu cầu gặp cụm nhiều lần hoặc phát lại vẫn chỉ tính 1; hai yêu cầu khác gặp cùng cụm tính 2. Không lưu toàn văn đầu vào.
- Kho kiểm yêu cầu đang xử lý và đúng phiên trước khi đếm. Cả kiểm dấu trùng, tăng `so_lan_gap` và ghi dấu đều nằm trong khóa RAM dùng chung giữa các phiên. Giao dịch ngoài rollback cả bộ đếm và dấu chống lặp nếu bước sau lỗi, nên lượt thử lại sau rollback vẫn được tính đúng.
- `cho_duyet.so_cum_vua_them` tiếp tục chỉ đếm cụm mới thêm, không đếm số lượt gặp. Số lần gặp và dấu chống lặp chỉ nằm trong kho; không thêm vào kết quả che. Cụm gốc không xuất hiện trong kết quả/cảnh báo/thông báo lỗi.

**Lưu ý khi nối Core:** `che` giữ nguyên chữ ký; mỗi lần gọi thông thường vẫn nhờ kho cấp mã yêu cầu. Test retry mô phỏng kho/adapter tin cậy trả lại cùng mã bằng mock `tao_yeu_cau`, không nhận mã từ văn bản/caller. Lead cần bảo đảm adapter tái dùng đúng mã khi phát lại, giữ cả tạo cụm, ghi nhận, tham chiếu và kết quả trong giao dịch chốt nguyên tử. Khóa RAM không phải bằng chứng PostgreSQL; phía kho Core phải bảo đảm duy nhất theo cặp yêu cầu/cụm và tăng nguyên tử trong giao dịch đã xác minh phiên/vùng. Lát này không triển khai phần đó.

Kiểm thuần/mock bằng đúng Python/PYTHONPATH handoff, `PYTHONDONTWRITEBYTECODE=1`, `-X utf8 -B -m unittest discover -s engines\e_mask\tests` và `-m unittest tests.test_mask5_seam`. Thứ tự: **ok / fail / error / skip**.

| Phạm vi | Trước sửa | Sau sửa |
|---|---|---|
| Toàn bộ `engines/e_mask/tests` | **88 / 0 / 0 / 0** | **96 / 0 / 0 / 0** |
| `tests.test_mask5_seam` | **1 / 0 / 0 / 0** | **1 / 0 / 0 / 0** |
| Tổng | **89 / 0 / 0 / 0** | **97 / 0 / 0 / 0** |

Nhóm 9 ca liên quan trên mã nền: **1 / 1 / 7 / 0**; sau sửa: **9 / 0 / 0 / 0**. Bổ sung 8 phương thức test và mở rộng một ca sẵn có: gặp lại, nhiều vị trí, retry, hai cụm cùng yêu cầu, chuẩn hóa, cụm chính thức, sai phiên/mã đóng, lỗi kho và rollback. Ca đồng thời dùng 8 luồng, 16 mã mới được gọi 4 lần/mã; chỉ tăng thêm 16 so với một lần gặp ban đầu, không dựa khóa giao dịch ngoài.

Không thêm lỗi trong phạm vi đã chạy; seam xác nhận giữ nguyên tập khóa đầu ra mẫu 1–4. Chưa kiểm PostgreSQL hoặc tích hợp Core; không kết luận toàn bộ nền v4. Không chạy `tests.test_v3`/`tests.test_v7`, dịch vụ, dữ liệu thật, không đổi SDK/thêm thư viện và không commit; lead giữ commit/gộp.

## 9. MASK-3E vòng 3 — đồng bộ adapter với nhật ký chốt vòng 2

Ngày 07/11/2026. Đối chiếu bằng `git show lat/mask-3d:src/kho_tri_thuc/core/mask.py`, nhánh tham chiếu tại `f5a4201ad3f11047794ce23593c2bb5d5a86fa00`, cùng hợp đồng snapshot/chốt của migration 120. `kho_qua_core.py` giữ cài đặt độc lập trong gói engine, chỉ dùng SDK; không import `core.mask` hay mã Core để tái sử dụng `KhoLuot`. Test engine bỏ đối chiếu trực tiếp bằng import `KhoLuot`, kiểm chữ ký theo port `Kho` và kiểm hành vi bằng dữ liệu vector.

- Nhật ký đủ sáu trường: `cum`, `bi_danh_tam_moi`, `bi_danh_da_dung`, `dong_yeu_cau`, `cum_da_tra`, `bi_danh_da_tra`. Mọi lần `tra_bi_danh` đều ghi SHA-256 của cụm đã chuẩn hóa, cả trúng/hụt; `tra_dinh_danh` ghi bí danh đã chuẩn hóa, kể cả tra danh mục, bí danh tạm cũ, bổ sung và tra hụt. Mỗi khóa chỉ ghi một lần theo thứ tự tra đầu tiên. Không đưa cụm gốc vào hai trường khóa tra.
- `cum_cho_toan_vung` hiện là map SHA-256(cụm chuẩn) → chuỗi bí danh. Khi tìm thấy, bỏ mã vừa cấp khỏi `bi_danh_tam_moi`, dùng bí danh sẵn có, ghi `chi_gap_lai=True`, trả cờ vừa thêm bằng `False`; cùng cụm trong một lượt chỉ ghi nhận một lần. Snapshot che không mang cụm gốc của yêu cầu khác.
- Chốt lượt che có `gui_duoc=False` đặt `dong_yeu_cau=True` trên bản sao nhật ký gửi Core, gồm cả còn sót định danh và kiểm tiền/ngày không đạt. Lượt che đạt và lượt mở che giữ quy tắc đóng hiện có; phát lại lượt đã chốt vẫn gọi Core kiểm quyền với ba trường dữ liệu bằng `None`.

**Bộ vector dùng chung:** `engines/e_mask/tests/vector_kho_luot.json`, `phien_ban_vector=1`, 10 ca DEMO. `HopDongKhoTests.test_vector_kho_luot_dung_chung` thực thi toàn bộ: ghép `snapshot_mac_dinh` với snapshot từng ca; cố định `uuid_cap` khi cấp bí danh; chạy các port `thao_tac` trong một `giao_dich`; so kết quả từng port và toàn bộ sáu trường `nhat_ky`. So thêm `ket_qua_chot`/`nhat_ky_chot` cho bước điều phối sau giao dịch. Có ca Unicode NFD/hoa thường/khoảng trắng, tra trúng/hụt chống trùng, cụm mới, gặp lại, tái dùng toàn vùng, cụm khác không tái dùng, mở bằng chính thức/tạm/bổ sung/lạ, đóng rõ ràng và che bị chặn. Test còn kiểm bản sao chống sửa, không RPC từng port, giữ nguyên đầu vào và snapshot.

**Yêu cầu cho lát Core tiếp theo:** Core `mask.py` phải qua chính bộ vector JSON này. Test phía Core cần chạy phần port với `KhoLuot`, đồng thời kiểm `nhat_ky_chot` ở bước điều phối `Mask` (quy tắc che bị chặn nằm ngoài `KhoLuot`). Lát này chưa thêm test phía Core và chưa xác nhận PostgreSQL.

**Phụ thuộc Core cần lead chốt trước F/G:**

1. `cum_cho_toan_vung` hiện chưa mang nhóm có thẩm quyền; adapter theo `KhoLuot` tại commit tham chiếu, giữ nhóm đầu vào khi tái dùng bí danh. Nếu khác nhóm đã lưu, cửa ghi của migration 119 từ chối bằng `22023`. Không suy đoán cấu trúc mới. Khi vòng 3 bổ sung nhóm cụm chờ, cần đồng bộ cách đọc trường này, nhật ký `cum[].nhom`, giá trị trả từ `ghi_cho_duyet` và vector cả phía engine/Core.
2. `phien_ban` theo migration 120 là chuỗi JSON chứa phiên bản các khóa `cum`, `bi_danh` và `yeu_cau`, không phải hash toàn vùng. Adapter chuyển nguyên xi về chốt, không parse/tái băm hay tự kiểm xung đột; Core kiểm lại các khóa đã tra/ghi. Mock đã bỏ giả định hash 64 ký tự. Nếu vòng 3 đổi cấu trúc phiên bản, Core/transport F/G phải bảo toàn giá trị này; các trường `cum_da_tra`/`bi_danh_da_tra` trong nhật ký cần được đối chiếu lại cùng migration mới.

Kiểm bằng đúng Python/PYTHONPATH handoff, `PYTHONDONTWRITEBYTECODE=1`, `-X utf8 -B -m unittest discover -s engines\e_mask\tests`. Nền vòng này: 119 phương thức, **117 ok / 3 fail / 0 error / 0 skip**, 38,508 giây; 3 failure gồm hai subtest hiệu năng trong cùng một phương thức (`1; `: 5,325 giây; `1 `: 5,108 giây, ngưỡng 5 giây) và một phương thức nhật ký adapter lệch Core. Không sửa/nới ngưỡng hiệu năng vì ngoài phạm vi bốn tệp.

Sau sửa: **122 ok / 0 fail / 0 error / 0 skip**, 22,011 giây, gồm cả 26 phương thức `test_noi_core` và 10 vector trong một phương thức. Lỗi nhật ký nền đã hết, hai điều kiện chặn gửi đều kiểm được yêu cầu đóng, tái dùng cụm chờ được thử qua luồng che thật với kho mock. Hiệu năng lần này lần lượt **1,923 / 1,933 / 3,319 giây** cho `1; ` / `1, ` / `1 `; không thay mã hiệu năng nên không kết luận đã sửa nguyên nhân dao động theo tải. Lượt kiểm riêng ban đầu có ba lỗi fixture vector mở che vì mock chưa được cấp mã mở; đã bổ sung mã tin cậy cho mock trước lượt chạy toàn bộ đạt nêu trên.

Không thêm lỗi so nền đo trực tiếp trong phạm vi engine; chưa chạy toàn bộ nền v4, PostgreSQL hoặc transport F/G. Chỉ đổi đúng bốn tệp handoff, UTF-8/NFC không BOM; không commit, đổi SDK, thêm thư viện, xóa tệp hoặc thao tác dịch vụ/dữ liệu thật.
