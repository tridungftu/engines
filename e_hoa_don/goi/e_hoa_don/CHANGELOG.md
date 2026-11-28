## HD-9 — 15/11/2026

## 1.0.1 — LX-HD, đường cấu hình mặc định trên Linux, 28/11/2026

- Khi thiếu `PROGRAMDATA`, `_tep_mac_dinh()` dùng `/var/lib/KhoTriThuc/engines/e_hoa_don/cau_hinh.json` nếu không phải Windows; Windows vẫn dùng `C:/ProgramData`. Giữ ưu tiên `KTT_ENGINE_CAU_HINH` rồi `PROGRAMDATA`, cùng kiểm đường ngoài gói, trần byte, khóa lặp và schema.
- Thêm 8 ca giả lập Linux/Windows và ưu tiên biến môi trường; chỉ tính đường hoặc đọc tệp DEMO tạm, không ghi `/var/lib` thật. Nâng các chỗ ghim phiên bản và oracle hiện hành lên 1.0.1, sinh lại danh mục engine; không đổi lock hoặc thêm thư viện.
- Helper cấu hình vẫn ngoài đường chạy XML/ZIP/XLSX. Đã kiểm bằng Core giả (CoreGia); giả lập đường Linux không thay thế kiểm trên Ubuntu/WSL hoặc nghiệm thu Core thật.

Nâng yêu cầu SDK lên 2.2.0; engine không dùng ngăn hoặc cấu hình nên không cần migration. Hạ trần ZIP và JSON bảng kê đầu vào qua `mo_tep` xuống 20 MiB theo trần SDK; giữ trần XLSX và JSON đầu ra 32 MiB. Đúng 20 MiB được chấp nhận; vượt một byte bị từ chối bởi engine hoặc SDK. Đã kiểm bằng Core giả (CoreGia).

# CHANGELOG — e_hoa_don

- Kết quả Windows/Python 3.13.14/SDK 2.2.0: SDK 4/4 DEMO ĐẠT; pytest 662 passed in 189.49s, 0 skipped; kiểm độc lập ĐẠT, mọi mã thoát 0. Danh mục engine khớp; lock giữ nguyên. PR: chờ lead mở.

## HD-7 — Bảng kê XLSX exact trong RAM, 15/11/2026

- Đăng ký hoa_don.bang_ke_xlsx@1 nhận truong từ đọc XML/ZIP, trả 11 trường §2.5. Đúng 3/3 runtime chay.py/bang_ke.py/xlsx_toi_thieu.py; manifest/DEMO/AST handler XML/ZIP giữ nguyên. Không thêm dependency, không sửa Core/SDK/ma-nguon.
- Kiểm schema/phiên bản/băm/raw_ref/binding/đếm/ordinal/trùng từ JSON qua SDK, tái dựng DTO để dùng lại phép chiếu; không parse XML lại. OOXML zipfile RAM, hai sheet, inline string text @, style/width/freeze. Giữ exact money/currency/số 0 đầu, ngoài 18/6 kèm cảnh báo; sai/mơ hồ/thiếu currency để trống; không formula/SUM/hyperlink. Giữ mọi entry/thư mục/lỗi/trùng, không suy đủ kỳ hoặc ghi nhận nghiệp vụ.
- Chặn JSON 32 MiB, 1.000 dòng/entry, cell 16.000 ký tự, XLSX 32 MiB, 600 giây; kiểm hủy trong xử lý/trước upload/trả, không XONG khi mất lease/hủy/upload lỗi. Không ghi dữ liệu/cấu hình/sổ/cache/tệp tạm lên máy, chưa cần ngăn/màn riêng. Nguồn tĩnh CD-096 A1, SHA thực/LF và giải thích khác cột trong NGUON.md.
- Windows/Python 3.13.14/SDK 2.0.0: `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` → **4/4 DEMO ĐẠT** (3 XML + 1 ZIP); `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q --basetemp=.pytest-tmp` → **652 passed in 113.65s, 0 skipped**; `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` → **ĐẠT**; mọi mã thoát 0. Có 180 ca HD-7, oracle OOXML độc lập và CoreGia bộ nhớ/HTTP; biên 1.000, 32 MiB JSON, cell 16.000 và buffer XLSX kiểm thật; trần writer nhỏ/clock giả kiểm lỗi giới hạn. Lượt đầu 1 failed/648 passed do assertion HD-5 chỉ cho hai năng lực; sửa assertion theo phạm vi rồi chạy lại toàn bộ đạt.
- **Đã kiểm bằng Core giả (CoreGia)**. SDK chay_thu_demo chưa fixture tệp lồng trong truong: XLSX chỉ phủ qua pytest với CoreGia.them_tep/kết quả đọc thật; giữ Cần Core fixture/chuỗi chung, không ID giả hoặc sửa SDK. Chưa kiểm Core thật/quyền kho tệp/Excel app/Linux, cài sạch ZIP/XLSX tiếp HD-8.
- Thời gian thực tế: **08:37:00–08:59:29, 15/11/2026 UTC+07; 0.375 giờ**, so phiếu **5 giờ ước tính**. PR: **chờ lead mở**; không xóa/commit/push. Chi tiết lệnh và kết quả trong VIEC.md Bàn giao HD-7.

## HD-5 — Lõi ZIP và kiểm kê từng entry, 15/11/2026

- Thêm zip.py và schema JSON kỹ thuật; tái dùng lõi ZIP/parser strict/DTO/phép chiếu XML. Chỉ sửa 2/4 runtime; manifest/hoa_don.doc_xml@2 không đổi, ZIP chưa đăng ký (HD-6). Giữ ordinal/tên gốc/entry lỗi và mọi bản trùng; trạng thái đọc tách khỏi dấu trùng; thư mục báo riêng.
- SHA-256 chỉ sau đọc hết/CRC đúng; băm và kích thước null khi đọc thiếu. Chặn tên nguy hiểm/symlink/ZIP lồng khỏi parser; non-XML đọc có trần để băm. Đối chiếu EOCD với central directory; không kế thừa COMPLETE hoặc suy đủ kỳ/thuế/ghi nhận. Giữ context=None, UNKNOWN/NOT_PERFORMED.
- Chặn metadata và byte thật: 64 MiB ZIP, 1.000 entry, 16 MiB/tệp, 128 MiB tổng, 1.000 HHDVu trước DTO, 32 MiB JSON; toàn việc lỗi khi vượt trần. Theo lead bổ sung trần nén 1.000:1 (chưa đo corpus). Chỉ STORED/DEFLATE, method khác báo chưa hỗ trợ. Hook bộ nhớ ZipExtFile chống file_size giả và đếm chunk lỗi CRC; kiểm lại khi nâng Python. Không giải nén đĩa/cấu hình/sổ/cache/ngăn/tệp tạm; giữ tệp/test cấu hình lịch sử ngoài đường chạy, chờ lưu trữ sau.
- 69 unit tests HD-5; hồi quy parser XML/DTO nguyên AST. Sửa nợ subprocess UTF-8 ở test_hd_2 và cập nhật danh mục gói trong test độc lập. Windows/Python 3.13.14/SDK 2.0.0: SDK **3/3 DEMO ĐẠT**, pytest **367 passed in 45.80s, 0 skipped**, kiểm độc lập **ĐẠT**, mọi mã thoát 0. **Đã kiểm bằng Core giả (CoreGia)**; ZIP mới kiểm unit, chưa nối Core thật/đăng ký SDK; chưa chạy Linux hoặc cài sạch ZIP.
- Thời gian thực tế: **07:51:00–08:15:19, 15/11/2026 UTC+07; 0.406 giờ**, phiếu **4 giờ ước tính**. PR: **chờ lead mở**. Không commit/push; không phát sinh Cần Core/Chờ Anh mới.

## HD-P2 — Phiếu ZIP + bảng kê XLSX, 15/11/2026 (chỉ tài liệu)

- Điều chỉnh theo lead: HD-7/HD-8 dùng Python stdlib, kiểm OOXML và đọc tĩnh nguồn đối chiếu. SDK 3/3 ĐẠT, pytest 298 passed (39.33s), kiểm độc lập ĐẠT; đã kiểm bằng Core giả (CoreGia), chưa triển khai ZIP/XLSX.

- Cập nhật `docs/GIAO-CODEX-e_hoa_don.md` và `docs/VIEC.md` của engine theo quyết định Anh 15/11: Q1–Q3 đã chốt, XML mốc 1; thêm HD-5…HD-8 cho `hoa_don.doc_zip@1` và `hoa_don.bang_ke_xlsx@1`, tổng 14 giờ triển khai ước tính. Mỗi lát có lệnh giao và điều kiện đạt; PDF/tải cổng thuế để sau.
- Thiết kế giữ từng entry ZIP với thứ tự/tên/SHA/trạng thái đọc và dấu trùng; không gọi đầy đủ khi có lỗi. XLSX hai sheet giữ tiền cell string exact + currency, số hóa đơn có số 0 đầu. Lead quyết định dùng Python stdlib với OOXML tối thiểu, tham chiếu tĩnh cách chiếu cột/định dạng nguồn cũ theo quyền CD-096 A1; không thêm dependency. Không cấu hình/sổ/cache bền trên máy; khi cần giữ dữ liệu dùng Ngan, tạm RAM.
- Không sửa mã, manifest, dependency, DEMO hoặc kích hoạt ZIP/XLSX. Kiểm hồi quy Windows/Python 3.13.14/SDK 2.0.0: SDK 3/3 DEMO ĐẠT, pytest 298 passed in 39.00s/0 skipped, kiểm độc lập ĐẠT; đã kiểm bằng Core giả (CoreGia). Đây là bằng chứng XML hiện có, chưa kiểm ZIP/XLSX/Core thật. PR: chờ lead mở; không commit/push.

## Sửa HD-4 — CI Linux/Python 3.11, 15/11/2026

- Sửa audit hook trong công cụ kiểm ngoài gói: từ chối import bằng `ModuleNotFoundError` để phép dò Jython tùy chọn của `copy.py` CPython 3.11 bắt được `ImportError`. Hook cũ ném `RuntimeError` khiến tiến trình sạch thất bại; Python 3.13 đã bỏ phép dò này. Giữ allowlist, `-I -B -S`, SDK nạp theo tệp cụ thể và chặn mạng/tiến trình; không thêm Core/shim/site-packages. Runtime, SDK, API và dependency không đổi.
- Chẩn đoán lỗi chỉ in mã thoát/tên ngoại lệ đã giới hạn hoặc mã cố định cho lỗi lạ, thiếu xác nhận, khởi chạy/quá hạn; không phản chiếu nội dung hóa đơn, đường dẫn hay traceback. Thêm 14 test hồi quy gồm probe Jython, import cấm có tệp hiện hữu, sự kiện mạng/tiến trình và canary chẩn đoán.
- Windows/Python 3.13.14/SDK 2.0.0, `PYTHONDONTWRITEBYTECODE=1`: SDK **3/3 DEMO**, pytest **298 passed in 39.46s, 0 skipped**, kiểm độc lập và cài sạch Windows **[ĐẠT]**, mã thoát 0. Đã kiểm bằng Core giả (CoreGia). Nguyên mã copy.py CPython 3.11.18 chạy trong tiến trình cô lập trên 3.13: hook cũ mã 1/RuntimeError, hook mới mã 0/đủ DEMO. Chưa có interpreter 3.11/Linux tại máy, **chờ CI Linux xác nhận**, không coi mô phỏng là chạy Linux.
- Không git add/commit/push; mã PR chưa tra. Không có yêu cầu Core/Chờ Anh mới. Không đo mốc bắt đầu lượt sửa; phiếu HD-4 **2 giờ ước tính**.

## HD-4 — mốc 14/11/2026, kiểm thực tế 15/11/2026

- Đối chiếu SDK 2.0.0 và SHA wheel; xác minh bytes nguồn, lập danh mục SHA gói; chỉ SDK + stdlib. Hai kịch bản cài sạch sao chép gói tách khỏi source, kiểm thiếu cấu hình và nhập độc lập; chưa chạy Linux.
- Chặn khởi động nếu `Engine._ghi` không callable; test ghim SDK và thiếu hook. Cần SDK hook nhật ký công khai, không in traceback ra stderr.
- Windows/Python 3.13.14: SDK **3/3 DEMO [ĐẠT]**, pytest **284 passed, 0 skipped**, kiểm độc lập **[ĐẠT]**; cài sạch Windows **3/3 DEMO và kiểm độc lập [ĐẠT]**, các mã thoát 0. Đã kiểm bằng Core giả (CoreGia), chưa kiểm Linux/Core thật.
- Thời gian thực tế: 02:22–02:29 ngày 15/11/2026 UTC+07, khoảng **0,12 giờ**; phiếu **2 giờ ước tính**. PR: **chờ lead mở**. ZIP/bảng kê/tải chờ Anh; cần Core context tin cậy, quyền tệp và chuyển quy trình @1 → @2, giữ bản cũ.

## HD-3 — mốc 14/11/2026, kiểm thực tế 15/11/2026

- Ba chay_thu_demo dương tính: tiền nguyên 1000000 VND + 100000 VND = 1100000 VND; tiền lẻ exact 1000000.123456 VND + 100000.012345 VND = 1100000.135801 VND; nguồn thiếu/rỗng/tổng vắng → null/ABSENT/EMPTY/HOLD. Công ty DEMO Ánh Dương chỉ là nhãn mô tả, không thêm Ten ngoài allowlist. Context=None, can_kiem_tra=true, identity/digest null; TToan ngoài envelope V1 vẫn giữ issue.
- Thêm ba fixture XML nhỏ + oracle literal và pin bytes/SHA-256 độc lập trong tests/demo; pytest đối chiếu đủ 18 trường, báo cáo qua CoreGia.doc_tep, header/dòng/occurrence/locator, Decimal/tiền/thuế, bytes/hash và trạng thái nguồn. Không lấy output parser làm expected hoặc nhận golden cũ đã kiểm khi thiếu bytes gốc. Giữ XML UTF-8/LF bằng .gitattributes; bản checkout fixture tiền nguyên khớp LF đã ghim HD-0.
- Thêm **24 test HD-3**, gồm MIME sai, lỗi đúng LoiNghiepVu/mã/câu HD-1, DTO bất biến/Issue SDK, thiếu TToan và biên 1.000 dòng (qua)/1.001 dòng (từ chối). Tệp nhiều dòng chỉ sinh trong DEMO tạm. Chạy tiếp regression âm HD-1/HD-2: dữ liệu sai/thiếu/mơ hồ, giới hạn, hủy, upload/retry/lease và canary. Không skip/xfail, không cắt ngầm. 0 tệp runtime sửa, không đổi phiên bản/hợp đồng.
- Kiểm thật Windows/Python 3.13.14/SDK 2.0.0, đúng ba lệnh -B: SDK **3/3 DEMO [ĐẠT]**; pytest **283 passed in 38.65s, 0 skipped**; kiem_doc_lap **[ĐẠT]**, cả ba mã thoát 0. SDK wheel cài/đối chiếu SHA offline; pytest có sẵn chép offline. **Đã kiểm bằng Core giả (CoreGia)**; chưa chạy Linux, máy sạch HD-4, quyền kho tệp/Core thật hoặc bài Core thật 120 phút.
- Thời gian thực tế: **0.208 giờ** (02:08:00–02:20:27, 15/11/2026, UTC+07); phiếu **3 giờ ước tính**. Không mở rộng phạm vi hoặc phát sinh Cần Core/Chờ Anh mới; giữ context tin cậy/quyền tệp/hook log/seam lease/corpus cũ. ZIP/bảng kê/tải/Cloud/Node còn ngoài phạm vi và chờ Anh/Core. PR: **chờ lead mở**; bản nháp docs/PR-HD-3.md. Không commit/push.

## HD-2 — mốc 14/11/2026, kiểm thực tế 15/11/2026

- Chỉ sửa runtime `chay.py` (1/2 tệp cho phép); giữ nguyên parser/phép chiếu/lỗi HD-1, `hoa_don.doc_xml@2` và phiên bản gói. Kiểm hủy trước đọc, sau parse, trước upload và trước return; bốn câu tiến độ cố định, không chứa định danh/dữ liệu tài liệu.
- Giữ mở theo `tep_id` qua SDK, nguyên tham chiếu XML/bytes/hash và bàn giao JSON trước khi trả trường. Không ID tự cấp, kho tạm/cache/dedupe, nhận nghiệp vụ, heartbeat/retry/server riêng. SDK quản lý lease và Idempotency-Key.
- Test canary chứng minh SDK 2.0.0 in traceback/nội dung exception; lớp bọc `CongHoaDon._ghi` chỉ in mã cố định `HD_SDK_THONG_BAO`, không đổi xử lý lỗi/hủy/lease. Ghi Cần Core/SDK: hook nhật ký an toàn và seam lease/giao lại công khai; không sửa SDK. Hủy sau upload không nộp kết quả, vòng đời tệp đã upload thuộc Core.
- Thêm **102 test HD-2** qua CoreGia trong bộ nhớ và MayChuGia loopback: đọc/upload, ID opaque, bytes/hash, metadata tên không mở đường dẫn, mất 1/3 ACK ở ba thao tác không ghi trùng, upload lỗi/thiếu ID, hủy bốn mốc, mất lease 409/404/410 và gia hạn SDK, giao lại thuần, hai pháp nhân cùng XML không cache, canary stderr/lỗi/tiến độ. Thêm hai ca tiến trình `app.chay`/module nhận một dòng JSON stdin, giữ stdin mở lúc việc đã bàn giao.
- Ba lệnh nghiệm thu Windows/Python 3.13.14/SDK 2.0.0 với `-B`: SDK **1/1 DEMO [ĐẠT]**; pytest **259 passed in 37.53s, 0 skipped**; kiểm độc lập **[ĐẠT]**; cả ba mã thoát 0. **Đã kiểm bằng Core giả (CoreGia)**; chưa kiểm quyền kho tệp/Core thật, Linux hoặc máy sạch HD-4. Chỉ DEMO, không thuế/Cloud/Node.
- Thời gian thực tế: **0.195 giờ** (01:55:00–02:06:41, 15/11/2026, UTC+07) (phiếu **3 giờ ước tính**). PR: **chờ lead mở**; bản nháp `docs/PR-HD-2.md`, chi tiết `docs/VIEC.md`. Không commit/push, không mở phần ZIP/bảng kê/tải.

## HD-1 — 15/11/2026

- Phân biệt XML hỏng và encoding/DOCTYPE/namespace/path ngoài profile bằng lỗi cố định; không phản chiếu nguồn hoặc bắt tràn DataError. Nhiều TToan không chiếu scalar mơ hồ; giữ exact text/occurrence, money/relations/thuế, issue ngoài envelope V1 và context=None.
- Lead Claude duyệt cặp runtime `doc.py` + `chay.py` (hai tệp, trong trần ≤5), không phải quyết định của Anh. Parser `hoa_don_xml.py` giữ nguyên. Sửa `HD_XML_QUA_LON`/`HD_KET_QUA_QUA_LON`; chỉ bọc đúng lỗi kích thước trong khối mở/đọc tệp, giữ lỗi khác/hủy/mất lease/invariant.
- Thêm trần vận hành 1.000 HHDVu/XML, XML parser tiền kiểm không dựng cây, dừng ở dòng 1.001 trước DTO/JSON bằng `HD_QUA_NHIEU_DONG_HANG`. Không cắt dòng/occurrence; comment/CDATA không bị đếm nhầm. README/VIEC ghi giá trị, lý do và giới hạn bằng chứng; trần JSON 32 MiB vẫn áp dụng trước upload.
- Thêm 20 test DEMO lượt bổ sung (HD-1 tổng 94 test mới trên nền HD-0 63 test). Năm ca đỏ lượt trước đã xanh. Ca 200.000 HHDVu chứng minh chặn trước parser lõi/JSON; đúng 1.000 dòng vẫn giữ đủ thứ tự/occurrence.
- Windows, Python 3.13.14, SDK 2.0.0, `PYTHONDONTWRITEBYTECODE=1`: SDK 1/1 DEMO [ĐẠT]; pytest `-q -p no:cacheprovider` **157 passed in 5.57s, 0 skipped**; kiểm độc lập [ĐẠT]; cả ba mã thoát 0. **Đã kiểm bằng Core giả (CoreGia)**, chưa nghiệm thu Core thật, chưa chạy Linux/máy sạch HD-4.
- Bàn giao và bản nháp PR cũ chuyển vào VIEC mục Bàn giao HD-1; giữ và cập nhật `docs/PR-HD-1.md` để lead dùng. Lượt bổ sung khoảng 0.2 giờ, tổng HD-1 khoảng 0.37 giờ gồm mốc trước 0.17 giờ; phiếu 3 giờ ước tính. Không git add/commit/push. PR: chờ lead mở. Không phát sinh Cần Core/Chờ Anh mới; giữ nợ SDK ánh xạ lỗi 413 đã được engine bọc hẹp.

## 1.0.0 — HD-0, 15/11/2026

- Tạo gói SDK 2.0 với đúng một năng lực `hoa_don.doc_xml@2`, `tep` → `truong`, đủ 18 trường phiếu §2.2; 16 MiB/XML/600 giây, cho phép hủy.
- Chuyển nguyên thuật toán strict/Decimal/DTO của `ma-nguon/lib/hoa_don_xml.py`, chỉ đổi hai import sang SDK 2.0.0 (kể cả lazy `Issue`). Giữ `__module__` legacy làm dấu vết; không shim, pickle hoặc kênh cũ. Nhánh ZIP nội bộ chưa kích hoạt.
- Lớp chiếu bảo toàn số 0 đầu, Decimal exact kèm currency, hash bytes, locator, occurrence, tiền/quan hệ nguồn; null khi thiếu/sai/mơ hồ/vượt miền. JSON kỹ thuật dùng `ra_json`, không raw bytes, thêm `van_de_phep_chieu` để lưu issue của phép chiếu.
- Handler dùng `viec.mo_tep`, đọc thực tối đa 16 MiB + 1; luôn `context=None`; upload JSON thành công qua `viec.tai_tep_ra` trước khi trả trường. JSON vượt 32 MiB từ chối, không cắt. `can_kiem_tra=true`, định danh/semantic digest null khi thiếu context; giữ `UNKNOWN`/`NOT_PERFORMED`.
- Thêm hai JSON Schema, cấu hình ngoài gói (không đọc ở khởi động/XML), README, DEMO giả, pin SDK và hồ sơ nguồn. Không tạo kho dữ liệu bền hoặc đọc bí mật.
- Kiểm AST/lazy/dynamic, cây gói và tiến trình sạch `-I -B -S` chỉ SDK/stdlib/gói XML; không bytecode/symlink/tệp vượt trần 20 MiB.

Kết quả thật trên Windows, Python 3.13.14, SDK 2.0.0 (wheel SHA-256 khớp bản phát hành), `-B`/`PYTHONDONTWRITEBYTECODE=1`:

```text
.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -B -m pytest e_hoa_don/tests -q
→ 63 passed in 0.82s; 0 skipped; mã thoát 0
.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import (kể cả lazy/dynamic), cây gói và tiến trình sạch; mã thoát 0
```

QA thêm: JSON Schema Draft 2020-12 hợp lệ và khớp báo cáo thật qua CoreGia, dùng công cụ `jsonschema` có sẵn trên máy để kiểm offline; không thêm dependency runtime. Pytest 9.1.1 và các phụ thuộc kiểm thử được chép từ bản cài sẵn vào venv, không truy cập mạng.

**Đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật.** Chưa chạy Linux hoặc bài máy sạch HD-4; test dùng pathlib/stdlib và mock I/O nên giữ khả năng chạy Windows/Linux, chưa coi đây là bằng chứng đã chạy Linux. Không chạy Node/Cloud/cổng thuế. Không thực hiện bài Core thật 120 phút.

Thời gian thực tế: 0.243 giờ (00:55:00–01:09:33, 15/11/2026, UTC+07; ước tính trong phiếu: 4 giờ). Mốc cập nhật VIEC theo giao việc: 14/11/2026; kiểm thực tế ngày 15/11/2026. PR: **chờ lead mở**; không commit/push. XML HD-1…HD-4 giữ theo phiếu, ZIP/bảng kê/tải còn chờ Anh chốt. Cần Core đã có: cửa context tin cậy/quyền tệp và kênh cấu hình máy; không phát sinh yêu cầu mới.


## HD-6 — 15/11/2026 — PR: chờ lead mở

- Đăng ký `hoa_don.doc_zip@1`: nhận tep, trả đủ 13 trường tĩnh và báo cáo `hoa-don-goi-chi-tiet.json` upload qua SDK; MIME ZIP, 64 MiB, 600 giây, hủy được. Giữ nguyên hợp đồng/handler `doc_xml@2`; chỉ 2 runtime `chay.py`/`zip.py` đổi. Giữ phiên bản 1.0.0 hiện có, ghim phát hành ZIP/XLSX ở HD-8/lead.
- Đọc qua `viec.mo_tep`, kiểm bytes thật/khối ngắn, hủy xuyên entry/chunk, trước upload/trả; lỗi/hủy/mất lease/upload lỗi không XONG, không dùng ChuaRo che lỗi cục bộ. Giữ tep_zip/băm bytes gốc; không tạo tep_id entry, không gọi engine khác hoặc ghi nhận nghiệp vụ, RAM thuần.
- Thêm ZIP DEMO hỗn hợp: 5 tệp/1 thư mục; 3 đọc được, 1 lỗi, 1 PDF chưa hỗ trợ, 1 trùng bytes, tên trùng khác bytes. XONG chỉ đã trả báo cáo; da_doc_het=false/can_kiem_tra=true; UNKNOWN/NOT_PERFORMED/context=None giữ nguyên.
- Đóng nợ HD-5: chặn UserWarning overlap, đổi thành lỗi entry an toàn/giữ bản ghi; chốt API riêng zipfile (EOCD/CRC/EOF/STORED/DEFLATE), lưu ý nâng Python tại NGUON; README ghi non-XML vượt 1.000:1 từ chối cả việc.
- 105 ca HD-6 đối chiếu toàn JSON với oracle literal, không sinh expected từ reader; từng băm/ordinal/đếm, SDK bộ nhớ + HTTP loopback, ACK/Idempotency-Key, hủy/gia hạn/mất lease/upload lỗi, canary và không filesystem. Điều chỉnh ba assertion chỉ-XML theo năng lực mới; không bỏ test hồi quy.
- Ba lệnh AGENTS.md §5 bằng `.venv\Scripts\python -B`: SDK **4/4 DEMO ĐẠT**, pytest `e_hoa_don/tests -q --basetemp=.pytest-tmp` **472 passed in 79.93s, 0 skipped**, kiểm độc lập **ĐẠT**, đều mã 0. Windows/Python 3.13.14/SDK 2.0.0 offline đúng SHA; đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật/quyền kho tệp, chưa chạy Linux/Excel app. Chi tiết lệnh và lần kiểm ban đầu được sửa tại VIEC.md.
- Thời gian thực tế **0.230 giờ** (08:21:00–08:34:48, UTC+07), phiếu 3 giờ ước tính. Không Cần Core/Chờ Anh mới; giữ nợ hook nhật ký/context/quyền tệp thật. Không sửa Core/SDK/ma-nguon, không dependency runtime mới, không xóa/commit/push; PR chờ lead mở.

## HD-8 ? 15/11/2026

M? r?ng ki?m ??c l?p v? c?i s?ch b?n sao g?i cho chu?i ZIP ? XLSX; th?m oracle VND/USD, entry l?i v? ki?m kh?ng ghi ??a. Kh?ng ??i runtime/dependency. ?? ki?m b?ng Core gi? (CoreGia); Linux, Core th?t, quy?n kho t?p v? Excel app ch?a ki?m. SDK ch?a c? fixture t?p l?ng trong `truong` cho Ch?y th? XLSX.

Windows/Python 3.13.14: SDK 4/4 ??T; pytest 653 passed, 0 skipped; ki?m ??c l?p v? c?i s?ch ??t. PR: ch? lead m?.
