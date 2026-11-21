# VIỆC — danh sách việc duy nhất của project `e_ocr`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| UI-OCR | Ba thẻ ABBYY / Tesseract / Hạn mức, hai nút kiểm nguồn và mô tả schema | AGENTS §4.13–14, phiếu UI §4 | Xong 21/11/2026 trong phạm vi CoreGia/KttCore giả | PR: **chờ lead mở**, nhánh `codex/e_ocr-ui-ocr`; không commit/push. Bằng chứng và Cần Core tại mục UI-OCR bên dưới |
| 0 | Đọc tài liệu cổng và engine; nhận kế hoạch các lát theo `GIAO-CODEX-e_ocr.md` | — | Xong 14/11/2026 | Thực hiện OCR-0 theo phiếu Anh giao; ước tính 2 giờ |
| OCR-0 | Khung SDK 2.0, cấu hình máy, kho tạm, schema chung và kiểm độc lập | OCR-6 | Xong 14/11/2026 | PR: **chờ lead mở**. Đã đạt tiêu chí riêng của OCR-0; kết quả DEMO chung và giới hạn xem bên dưới |
| OCR-1 | Đọc lớp chữ PDF và ABBYY Hot Folder cục bộ; hai action đọc dùng chung lõi | OCR-2, 3, 4, 7, 15 | Xong 14/11/2026 | PR: **chờ lead mở**. SDK DEMO 2/2, pytest 119 passed, 0 skipped, kiểm độc lập đạt; đã kiểm bằng Core giả (CoreGia), chi tiết bên dưới |
| OCR-2 | Chọn nguồn, hạn mức 30 ngày và dự phòng Tesseract; vendor PDF/DOCX/bảng | OCR-8 | Xong 14/11/2026 | PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia), mock CI và Tesseract thật bằng DEMO; bằng chứng OCR-2 bên dưới |
| OCR-9 | Chuyển SDK 2.2.0: ngăn/cấu hình, migration SQL, CoreGia và kiểm kê gói | OCR-8, 13, 14 | Xong 15/11/2026 trong phạm vi CoreGia | PR: **chờ lead mở**, nhánh `codex/e_ocr-ocr-9`; không commit/push |
| OCR-3 | Xuất Word từ cấu trúc tài liệu, giữ ô trống/ô gộp, vị trí bảng và thứ tự trang | OCR-4, 5 | Xong 14/11/2026 | PR: **chờ lead mở**. SDK DEMO 3/3, pytest 145 passed, 0 skipped, kiểm độc lập đạt; đã kiểm bằng Core giả (CoreGia), chi tiết bên dưới |
| OCR-4 | Lượt chưa rõ theo phương án B, chống trùng bền và đối chiếu hạn mức sau khởi động lại | OCR-13, 14, 15 | Xong 15/11/2026 | Phiếu 14/11/2026; PR: **chờ lead mở**. SDK DEMO 3/3, pytest 218 passed, 0 skipped, kiểm độc lập mã 0; đã kiểm bằng Core giả (CoreGia) |
| OCR-5 | Bộ DEMO, sáu ví dụ chạy thử và OCR-MAY ca 2/3/4/5/7/9; sửa namespace Word | OCR-11, 15, 16 | Xong — phiếu 14/11/2026 | Thực hiện 15/11/2026; PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia); SDK 6/6, pytest 239 passed, 0 skipped; bằng chứng bên dưới |
| OCR-6 | Ghim thư viện, nguồn và kiểm máy sạch | OCR-6 | Chưa đạt — phiếu 14/11/2026 | PR: **chờ lead mở**; chờ kiểm cài sạch và SDK DEMO theo bằng chứng bên dưới |
| OCR-8 | Cấu hình, hạn mức và lượt ABBYY qua ngăn; màn quản trị; đóng nợ OCR-4 số 1 | OCR-8, 13, 14 | Xong 15/11/2026 trong phạm vi CoreGia/RAM | PR: **chờ lead mở**. Đã sửa kiểm độc lập của lead; đã kiểm bằng Core giả (CoreGia), 288 passed, 0 skipped, SDK DEMO 6/6, Node UI 12/12; ngăn thật/màn thật chờ SDK 2.1 |
| 1 | Đóng gói độc lập theo cổng chung; thay hàm SDK riêng `ocr_*_luot` bằng lượt bền chung khi Core có | OCR-6, 13 | Đang làm 14/11/2026 | Có khung OCR-0; chuyển lõi ở OCR-1…OCR-4, không sửa `ma-nguon/` |
| 2 | Bổ sung nguồn dự phòng mask_ocr/Tesseract | OCR-8 | Xong 14/11/2026 | OCR-2 dùng CLI và pypdfium2 đã ghim, không thêm dependency. Máy đích xem **Cần cài** |
| 3 | Màn hạn mức ABBYY / trạng thái máy (giao diện của engine) | OCR-8 | Xong 15/11/2026 với KttCore/DOM giả | Màn `ui/cau_hinh.js`; chờ SDK 2.1 nạp trong Core thật |
| 4 | Bài máy test còn lại ca 1, 6, 8 | OCR-11 | Chờ Core / thiết kế | Ca 3 đã kiểm bằng Core giả ở OCR-5; ca 1 chờ thẻ trạng thái, ca 6 chờ Đối chiếu, ca 8 chờ bí mật/cầu nối có khóa |
| 5 | Lát 9: ABBYY thật trên máy hiện tại bằng PDF DEMO (Anh đã cho phép mở kết nối tạm) | OCR-12 | Chờ làm | Không chép `in\ out\ jobs\ state\` |
| 6 | Ghép Core (K1–K6) → nghiệm thu tổng thể | — | Chờ Core |  |

## UI-OCR — 21/11/2026

PR: **chờ lead mở**, nhánh `codex/e_ocr-ui-ocr`. Bắt đầu **21:26 ngày
21/11/2026** theo lead; phiếu UI §4 ước tính **3 giờ**.

Đã làm: màn ba thẻ theo ảnh mẫu, hai cột/một cột; hướng dẫn và mẫu cho
từng trường, kiểm khi nhập và lỗi tại ô; giữ CAS, hạn mức 30 ngày và trạng
thái engine. Nút kiểm dùng bản nháp; chặn bấm trùng, bỏ kết quả đến muộn
nếu đã sửa cấu hình, không tự lưu hoặc ghi hạn mức. Hai hàm quản trị nằm
trong `e_ocr/quan_tri.py`, khai dự kiến vào `KHAI-SDK-2.1.json`.

Schema chỉ thêm `title`/`description`/`examples`, gồm cấu trúc và mẫu đầy
đủ tại gốc; đã so toàn bộ type/default/enum/trần với HEAD và khớp. Giữ
nguyên bytes `engine.json`, không đổi năng lực/hành vi xử lý việc, không
cần sinh lại danh mục. Kiểm kê SQL cập nhật bytes/SHA-256 mọi tệp gói.

Đã kiểm bằng Core giả (CoreGia), máy giả và KttCore giả; chưa nối
Core/ABBYY thật, chưa chạy Linux hoặc cài máy sạch. Môi trường `.venv`
trong worktree dùng các thư viện đã cài (system-site-packages), SDK 2.2.0
cài bằng wheel nội bộ `--no-index --no-deps`, SHA-256 khớp SHA256SUMS.
Không thêm dependency runtime, không dùng mạng. Chromium dùng
playwright-core có sẵn, chỉ là công cụ chụp/kiểm bên ngoài gói engine.

Ảnh DEMO để lead so với mẫu: [màn rộng](anh-ui-ocr/01-may-rong.png),
[lỗi nguồn](anh-ui-ocr/02-loi-nguon.png), [CAS](anh-ui-ocr/03-cas.png),
[màn hẹp](anh-ui-ocr/04-man-hep.png). Tái dựng bằng
`tests/ui/chup_man.mjs`, màn thật + KttCore giả, chặn mạng hoàn toàn.

Lệch khỏi phiếu / giới hạn: kiểm Hot Folder chỉ metadata/quyền theo hệ
điều hành, không tạo tệp thử để tránh kích hoạt OCR; không chứng minh
FineReader đang chạy hoặc quyền ghi ACL thực tế. Không có bí mật trong
UI-OCR (`bi_mat: []`), nên ca hiện bốn ký tự cuối không áp dụng; đã kiểm
màn không đọc két và không hiện/gửi trường bí mật ngoài schema.

### Cần Core — UI-OCR

- **Cửa D:** nạp `ui/cau_hinh.js` như màn module cho Admin, API cấu hình
  có CAS và đọc ngăn. Khi chưa nạp màn, ô JSON chung cần hiện mô tả/ví dụ
  schema kèm chèn mẫu, định dạng và lỗi tại trường theo phiếu UI §2.1/10.
- **Cửa E:** chuyển `.thao_tac(ma, dau_vao)` thành việc quản trị có quyền
  Admin và thời hạn tối đa 15 giây, nối tới hai hàm Python đã khai dự kiến.
  SDK 2.2.0 chưa có decorator/cổng này. Adapter CoreGia chỉ nằm trong test,
  không mở năng lực giả trong runtime. `diem_vao` trong bản khai dự kiến
  là gợi ý nối hàm, chưa coi là hợp đồng SDK. Khi chưa có cổng, màn báo
  chờ Core; không suy rằng đã kiểm thành công.

Kết quả cuối: SDK DEMO 6/6 ĐẠT; pytest 318 passed, 0 skipped; Node UI 22/22; kiểm độc lập mã 0. Thời gian thực tế 0.47 giờ (21:26:00–21:54:25), ước tính 3 giờ.

Không phát sinh câu Chờ Anh mới. Kết quả kiểm và giờ kết thúc được ghi
trong [báo cáo UI-OCR](anh-ui-ocr/KIEM-TRA.md).

## OCR-9 — chuyển SDK 2.2.0, 15/11/2026

PR: **chờ lead mở**, nhánh `codex/e_ocr-ocr-9`; chỉ sửa e_ocr trong worktree.
Bắt đầu **16:44 ngày 15/11/2026** theo lead; phiếu ước tính **4 giờ**.

Đã chuyển `engine.json`/lock lên SDK 2.2.0, khai ba bảng ngăn, schema cấu
hình và gói migration. Cấu hình từ `viec.cau_hinh`; phạm vi pháp nhân qua
`viec.ngan`, khóa/lọc không tự cấp pháp nhân. Bỏ bảng cấu hình và fallback
RAM. Lượt, hạn mức, tổng hợp chưa rõ vẫn cùng lô nguyên tử; xung đột đọc
lại, thử tối đa 12 lần. Thế hệ lượt mới sửa CAS giữ id, không xóa/tạo lại.
Giữ chỗ chuyển vào mốc CAS không TTL để bảo toàn khi ngừng quá 45 ngày.

`KHAI-SDK-2.1.json`, `ngan.py`, `cau_hinh.py` chuyển nguyên bản vào
`e_ocr/LUU-TRU/OCR-9/`; chỉ bỏ hai ca băm mẫu chung được yêu cầu. Các ca
hành vi cũ giữ, đổi cách dựng môi trường sang CoreGia 2.2.0; ca ghi sai
kiểu boolean bị CoreGia từ chối ngay khi ghi và kiểm rollback tại đó.
Các ca xóa/khởi động lại RAM đổi sang CAS trạng thái/giữ dữ liệu qua App
mới và kiểm SDK từ chối xóa. Không còn tự cài đặt ngữ nghĩa NganBoNho.

Lệch kỹ thuật đã kiểm: SDK không hỗ trợ kiểu ngăn `json` và khóa manifest
`giao_dien_quan_tri`; giải pháp/việc cần Core ở mục tương ứng. Numeric của
SDK trả chuỗi, đã chuyển có kiểm số nguyên. Màn đọc JSON text cùng mã.
Thay đổi đồng bộ **5 tệp Python runtime + 1 JS + 1 SQL**: vượt ngưỡng nhỏ
~5 tệp vì phải đổi biểu diễn ngăn/UI/migration trong cùng gói được giao,
tránh gói pha API cũ/mới. Không tự tách thành các gói không chạy độc lập.

Môi trường: venv mới, wheel SDK cài `--no-index --no-deps`, SHA khớp
`0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`.
Không có wheelhouse phụ thuộc, tải pip bị ngắt; cài offline tệp distribution
đúng pin sẵn có, kiểm hash `RECORD`, không dùng system-site-packages.
Chưa kiểm cài lại archive wheel phụ thuộc trên máy sạch. Không đổi pin
thư viện OCR; README/NGUON ghi đúng giới hạn môi trường này.

Kết luận: **Đạt OCR-9 trong phạm vi được giao — đã kiểm bằng Core giả (CoreGia)**.
Chưa kiểm Core/ABBYY thật, màn trình duyệt thật hoặc Linux.

Kết quả kiểm thực tế, Python 3.13.14/SDK 2.2.0:

```text
> .venv/Scripts/python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
6/6 [ĐẠT]. Engine e_ocr 1.0.9: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát 0; CoreGia + Tesseract thật vie+eng, cấu hình mặc định SDK.

> .venv/Scripts/python -m pytest e_ocr/tests -q --basetemp=.pytest-tmp
294 passed in 79.89s (0:01:19)
Mã thoát 0; 0 skipped. Bao gồm kiểm TTL/schema/kiểm kê SQL và Node UI.
288 ca trước OCR-9 - 2 ca băm cổng tạm + 8 ca SDK 2.2.0 = 294 ca.

> .venv/Scripts/python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát 0.

> node --test e_ocr/tests/ui/test_cau_hinh.mjs
tests 12; pass 12; fail 0; skipped 0. Mã thoát 0.

> .venv/Scripts/python -m pip check
No broken requirements found. Mã thoát 0.

Kiểm kê SQL: 43/43 tệp khớp bytes/SHA-256, chỉ bỏ chính kiểm kê.
NGUON: đủ 44 tệp, một dòng/tệp; SHA nguồn LF khớp.
Ba tệp lưu trữ: nội dung khớp bản trước OCR-9 sau chuẩn hóa LF.
git diff --check: mã thoát 0.
```

Thời gian thực tế: **0.61 giờ**, **16:44:00–17:20:34 ngày
15/11/2026** (giờ Việt Nam), so với **4 giờ ước tính** trong phiếu chuyển SDK.
Bàn giao cho lead: PR **chờ lead mở**; không chạy commit/push.

Cần Core / Chờ Anh mới phát sinh: kiểu ngăn `json` và khai màn quản trị
chưa được SDK 2.2.0 chấp nhận; đã có giải pháp tương thích nêu trên. Nghiệm
thu lưu bền/migration/quyền/màn thật do Core tiếp tục. Không có câu chờ Anh mới.

## Sửa kiểm độc lập OCR-8 — 15/11/2026

Kết luận: **Đạt trong phạm vi được giao — đã kiểm bằng Core giả (CoreGia)**,
ngăn RAM và KttCore/DOM giả; chưa kiểm Core/ABBYY thật hoặc Linux.
PR: **chờ lead mở**, nhánh `codex/e_ocr-ocr-8`; không commit/push.

Đã làm: tách lỗi ba truy vấn UI; thay đọc lượt xuyên pháp nhân bằng bản
`trang_thai_engine/chua_ro` chỉ chứa `so_luot`, `theo_ngay` và khóa `ma`.
Vào/ra chưa rõ cập nhật tổng hợp cùng lô với lượt/hạn mức, CAS bảo vệ cạnh
tranh. Không tăng/giảm lại khi gọi lặp. UI chỉ hiện số đếm, ngày và “Lượt N”.
KttCore giả từ chối truy vấn bảng pháp nhân thiếu `phap_nhan_id` hợp lệ.

Dọn tối đa 50 hàng ngày hết cửa sổ mỗi lần ghi, trong cùng lô; chuyển chỗ
giữ còn dở sang ngày hiện tại trước khi xóa hàng cũ. Test 120 ngày tồn đọng
được dọn qua ba lần ghi, không vượt 100 lệnh/lô. Khai lưu 45 ngày. Schema
và ô chọn Tesseract chỉ nhận `vie`, `eng`, `vie+eng`, `eng+vie`.
README ghi cấm chạy thật trên RAM, quyền ghi thư mục cha Hot Folder vào,
dọn tạm `.e-ocr-…`; NGUON ghi công cụ OCR-7 đọc JSON qua `--cau-hinh`
do Anh tự chạy, nằm ngoài runtime engine. Đã cập nhật CHANGELOG và SHA theo LF.

Kết quả kiểm thực tế (`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`,
Python 3.13.14, SDK 2.0.0, wheel khớp SHA256SUMS.txt):

```text
> .venv/Scripts/python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
Engine e_ocr 1.0.8: mọi ví dụ chạy thử DEMO đều đạt.
6/6 ĐẠT, mã thoát 0. CoreGia + Tesseract thật vie+eng, chỉ DEMO.

> .venv/Scripts/python -m pytest e_ocr/tests -q --basetemp=.pytest-tmp
288 passed in 58.39s
Mã thoát 0; 0 skipped. ABBYY giả, có ca Tesseract thật.

> .venv/Scripts/python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát 0.

> node --test e_ocr/tests/ui/test_cau_hinh.mjs
tests 12; pass 12; fail 0; skipped 0
Mã thoát 0.
```

Thời gian thực tế: **0.20 giờ**, ngày **15/11/2026,
08:27:00–08:38:50** (giờ Việt Nam); phiếu OCR-8 **5 giờ ước tính**,
không có ước tính riêng cho lượt sửa kiểm độc lập.

Lệch khỏi phiếu / quyết định tạm: dọn dần 50 hàng/lô để tuân trần 100 lệnh;
giữ RAM theo quyết định 15/11 chỉ để kiểm DEMO. Sửa đúng năm tệp mã/khai báo
(hai Python, JS, schema, khai SDK 2.1), không sửa `_chung/**`, `ngan.py`,
`cau_hinh.py`, mã cũ, SDK/Core hoặc manifest đã khóa; không thêm dependency.

Cần Core / Chờ Anh mới phát sinh: xác nhận quyền Admin đọc xuyên pháp nhân
và bảo toàn chỗ giữ khi áp dụng lưu tối đa 45 ngày; chi tiết ngay bên dưới.
Không có câu chờ Anh mới.

## Cần Core (chuyển lead Core qua Anh)

Cập nhật OCR-9, 15/11/2026; các mục OCR-8 cần ngăn/cấu hình đã được SDK
2.2.0 giải quyết. Các phần bằng chứng cũ bên dưới giữ làm lịch sử.

- **SDK 2.2.0 chưa nhận kiểu `json` trong `ngan_du_lieu.truong`.** OCR-9 dùng
  `van_ban` chứa JSON ≤64 KiB cho `da_nhan`, `dang_giu`, `theo_ngay`, kiểm
  cấu trúc/số đếm; SQL dùng `text`, UI giải mã cùng biểu diễn. Khi thêm kiểu
  `json` cần thống nhất migration tiếp theo, không tự đổi hợp đồng SDK.
- **SDK 2.2.0 chưa nhận `giao_dien_quan_tri` trong manifest.** Màn hiện có
  `ui/cau_hinh.js` vẫn dùng `KttCore.engine("e_ocr").cau_hinh` với CAS, chỉ
  đọc bảng phạm vi engine. Cần Core nạp màn, cấp `admin_core`, gọi `destroy`
  khi đóng và kiểm trên trình duyệt thật; chưa tuyên bố màn đã nối.
- Cần lead/Core cài gói migration ba bảng `eng_e_ocr`, kiểm quyền pháp nhân,
  nâng gói và khởi động lại Core DEMO để xác nhận lưu bền. Đã kiểm bằng
  Core giả (CoreGia), không thay nghiệm thu PostgreSQL/Core thật.
- **Đã xử lý trong OCR-9:** `dang_giu` chuyển sang `trang_thai_engine/han_muc`
  không TTL; không còn chờ Core bảo toàn giữ chỗ trong hàng ngày có TTL.
  `luot_abbyy` không TTL; chỉ `han_muc_ngay` ẩn sau 45 ngày. Ngăn SDK đọc lại
  hàng hết hạn bằng `gom_het_han=True`; engine không dùng xóa.
- `app.hang_cho()` của SDK 2.2.0 đã có số việc chờ/đang chạy. Mốc vào hàng
  chờ và nhận việc để đo thời gian chờ Core chưa có; nhật ký hiện chỉ đo
  chờ ABBYY/chạy action. Không mở rộng yêu cầu OCR-9 sang đo hàng chờ.
- Bí mật theo tên, nhật ký tập trung, cầu nối ABBYY có khóa và gỡ mã riêng
  trong Core vẫn theo các lát trước. Không dùng `ocr_*_luot`, không đòi
  API riêng cho OCR. Trạng thái ABBYY chỉ phản ánh cấu hình/truy cập thư mục,
  chưa chứng minh FineReader đang chạy. Không có câu chờ Anh mới.

## Nợ OCR-4 — cập nhật OCR-8 ngày 15/11/2026

OCR-8 đóng nợ số 1; số 2 và số 3 tiếp tục ngoài phạm vi lát:

1. **Đã đóng trong OCR-8:** giữ trang + `lay_hoac_tao` trong một lô CAS,
   không tạo thế hệ gửi mới từ lần đọc đã cũ; quyền đọc/dọn có CAS riêng.
   Có test cùng tệp đồng thời, việc chậm qua lúc việc kia vừa xong và
   xung đột khi giữ trang. Đã kiểm bằng Core giả (CoreGia).
2. Lượt treo nếu tiến trình chết giữa `giu()` và thả tệp; chưa có bằng
   chứng phân biệt trước/sau công bố thì không tự nhả hạn mức.
3. PDF mồ côi sau biên nhận `.loi.json`; cần xử lý ở lát riêng.

## Cần cài — nguồn Tesseract trên máy đích (14/11/2026)

- Cần Tesseract Windows x64 và ngôn ngữ `vie`, `eng` để dùng dự phòng;
  executable/traineddata không nằm trong gói. Máy làm OCR-2 **đã có** và đã
  chạy test thật bằng DEMO, không cài/nâng cấp phần mềm trong lượt này.
- Anh tự chạy từ thư mục repo: `e_ocr\cong-cu\KIEM-TESSERACT.cmd`.
  Nếu dùng chỗ cài khác, truyền đường dẫn tới executable làm đối số thứ
  nhất, có dấu ngoặc kép khi có khoảng trắng. Công cụ ASCII chỉ kiểm;
  mã 0 = đủ bộ đọc và `vie+eng`, mã 1 = cần cài, mã 2 = thiếu ngôn ngữ.
- Nếu thiếu, Anh tự cài bộ Tesseract Windows x64 offline đã được duyệt,
  chọn cả tiếng Việt/Anh (hoặc bổ sung `vie.traineddata`, `eng.traineddata`
  từ bộ cài). Chạy lại `.cmd`, đặt `tesseract.duong_dan` ở màn Cấu hình OCR
  nếu không dùng PATH/vị trí mặc định; `ngon_ngu` là `vie+eng`.
- Thiếu khi cần dùng → `LoiNghiepVu("NGUON_DU_PHONG_CHUA_CAI", ...)`.
  Không chặn khởi động engine, PDF có lớp chữ hoặc việc ABBYY đọc được.

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

## Bằng chứng OCR-2 — 14/11/2026

- Nhánh: `codex/e_ocr-ocr-2`; PR: **chờ lead mở**. Lead commit/mở PR;
  Codex không commit/push. Tiêu đề đề xuất:
  `[e_ocr] OCR-2 — Tesseract dự phòng, chọn nguồn và hạn mức 30 ngày`.
- Thời gian thực tế: **14/11/2026, 23:02–23:30** (28 phút, khoảng
  **0,48 giờ**), so với **5 giờ ước tính** trong phiếu; giờ Việt Nam.
- Bộ chọn nguồn và Tesseract ở `chon_nguon.py`, `tesseract.py`, `vendor/`;
  `van_ban.py` chỉ nối bộ chọn và metadata kết quả. **Không sửa `chay.py`**
  để thuận tiện ghép nhánh OCR-3. Phiên bản gói tăng 1.0.2, API/MIME giữ
  theo phiếu đã khóa; DOCX chỉ có trong lõi vendor, chưa thêm MIME mới.
- Tách phần thực hiện vì tổng vượt khoảng 5 tệp mã: **OCR-2A** gồm bốn
  tệp vendor và công cụ `.cmd`; **OCR-2B** gồm năm tệp nghiệp vụ
  (`chon_nguon.py`, `tesseract.py`, `abbyy.py`, `kho_tam.py`, `van_ban.py`).
  Ngoài ra chỉ đổi dòng metadata phiên bản trong `__init__.py`; test,
  phiếu, lock và tài liệu đi cùng gói. Bàn giao chung lát OCR-2 trên nhánh
  lead chỉ định, không tạo thêm nhánh/PR hoặc mở rộng OCR-3/OCR-4.
- Chuyển từ `ma-nguon/chon_nguon.py`: giữ ABBYY trước, lý do chuyển và
  bằng chứng chắc chắn chưa nhận; bỏ cổng/lượt bền cũ. `chi_abbyy` trả lỗi
  ABBYY/hạn mức, `chi_tesseract` bỏ ABBYY và sổ. Lớp chữ sẵn được đọc trực
  tiếp ở mọi chế độ. Kết quả tài liệu ghi `nguon_doc`, `ly_do_chuyen_nguon`;
  kết quả văn bản thuần vẫn đúng hợp đồng chỉ trả chuỗi.
- Sổ `han_muc_abbyy` trong `KhoTam`: cửa sổ trượt **30 × 86.400 giây**,
  nhóm ngày UTC/giây, không reset đầu tháng. `cap_nhat` giữ khóa xuyên
  đọc–sửa–ghi để hai tiến trình không cùng vượt hạn mức. Chỗ giữ dùng cùng
  mã tương quan với ABBYY; chỉ ghi `da_nhan` khi thấy tệp biến mất hoặc
  có kết quả đúng mã. Không trừ khi bị từ chối/rút tệp trước khi nhận.
- Đã nhận mà chưa trả → `ChuaRo`, không chuyển/hoàn trang. Không rút được
  do lỗi quyền nhưng chưa chắc đã nhận → giữ chỗ, chưa ghi trang đã dùng.
  Hủy trước nhận bỏ giữ; hủy sau nhận vẫn tính trang đã nhận. Kết quả thiếu
  chữ/sai trang hoặc lỗi dọn sau nhận không kích hoạt fallback.
- Chuyển vendor phần PDF chữ sẵn, DOCX và giữ bảng; giấy phép **phần mềm
  nội bộ, dùng nội bộ tập đoàn** trong `NGUON.md`/`LICENSE`. Không chép
  runtime dual, VietOCR/model, worker hoặc dữ liệu ABBYY; nguồn cũ giữ nguyên.
- Tesseract CLI dùng pypdfium2/Pillow đã ghim, không thêm dependency/mạng.
  Giữ nguyên trang đã có lớp chữ trong PDF trộn; render trang thiếu chữ,
  TSV trả tọa độ từ, bảng vector được điền chữ mà giữ ô trống/ô gộp.
  PNG/TSV ở thư mục tạm riêng, có hủy/quá hạn và dọn tệp; stderr chương
  trình ngoài không được in. Thiếu executable/ngôn ngữ trả đúng
  `NGUON_DU_PHONG_CHUA_CAI`; hướng dẫn ở mục **Cần cài** phía trên.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows x64, Python 3.13.14.
  Mock Tesseract cho CI; test thật trên máy có đủ `vie+eng` nhận đúng
  `1.000.000 VND`, `30/10/2026` và chữ DEMO. Không đọc hồ sơ/cấu hình
  thật, không chạy ABBYY/Core thật. Chưa có bằng chứng chạy Linux hoặc
  cài máy sạch; test dùng filesystem/khóa chuẩn và `spawn` cho cả hai OS.

### Kết quả ba lệnh bắt buộc — OCR-2

Trích các dòng tổng kết thật của lượt kiểm cuối, dùng `-B` để không sinh
bytecode. SDK có đủ hai dòng `[ĐẠT]` cho hai ví dụ lớp chữ DEMO của OCR-1:

```text
> .venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
Engine e_ocr 1.0.2: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát: 0; 2/2 ĐẠT.

> .venv\Scripts\python -B -m pytest e_ocr/tests -q -rs
153 passed in 16.07s
Mã thoát: 0; 0 skipped, có test Tesseract thật.

> .venv\Scripts\python -B e_ocr/tests/kiem_doc_lap.py
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

34 ca mới kiểm hết hạn mức/trần bằng đúng, ABBYY tắt/mất thư mục, lỗi gửi,
timeout trước/sau nhận, quyền rút tệp chưa rõ, chỉ ABBYY/chỉ Tesseract,
thiếu executable/ngôn ngữ, kho hỏng, cửa sổ qua đầu tháng/biên 30 ngày,
hai tiến trình cùng giành trang cuối, CLI mock ảnh/PDF trộn, bảng vector,
TSV hỏng, chữ chú thích cạnh bảng trên cùng dòng OCR, hủy tiến trình,
DOCX ô trống/gridSpan/vMerge, XML DTD/entity,
giấy phép/cây vendor và một ca nhận dạng thật. Cập nhật ba ca OCR-1 theo
chế độ chỉ ABBYY; bổ sung kiểm hạn mức khi hủy trước/sau nhận.

Kiểm bổ sung: `.cmd` chạy trên máy → `[DAT] Da co Tesseract va du ngon
ngu vie+eng.`, mã 0; truyền executable DEMO không tồn tại → hướng dẫn
`[CAN CAI]`, mã 1. Tệp `.cmd` là ASCII. SHA-256 24 tệp gói cập nhật ở
`NGUON.md`; wheel SDK khớp `SHA256SUMS.txt`. Không thay pin dependency,
không có thay đổi ở `ma-nguon/`, SDK hoặc `_chung/`. `git diff --check`
không báo lỗi.

### Quyết định tạm và phần còn lại OCR-2

- Thay vận chuyển OCR MuPDF/worker của vendor cũ bằng Tesseract CLI và
  pypdfium2 đã ghim để chạy offline với môi trường có sẵn; không cài
  PyMuPDF/defusedxml hoặc mang runtime dual vào gói. DOCX dùng XML chuẩn,
  từ chối DTD/entity và XML khác UTF-8 trước parse. Nguồn/tệp đã chuyển
  thể được ghi trong `NGUON.md`, mã gốc giữ nguyên để lưu trữ sau.
- Giữ quyết định tạm cấu hình JSON/kho tạm ngoài gói của lead. Giữ chỗ
  trước gửi là cơ chế cạnh tranh, **không phải trang đã dùng**; sau crash
  không tự bỏ chỗ giữ hoặc gửi lại. Lượt bền/chống trùng/đọc trả muộn và
  đối chiếu chỗ giữ thuộc OCR-4, rồi thay bằng ngăn/lượt bền chung của Core.
- Quy ước rời/xóa tệp vào khi nhận vẫn kế thừa OCR-1, cần kiểm trên ABBYY
  thật ở OCR-7. Không suy việc đã nhận chỉ từ lỗi quyền hoặc sự im lặng.
- Giữ được bảng DOCX và bảng có đường kẻ vector; bảng chỉ có trong ảnh
  chưa được suy cấu trúc, có cảnh báo. Chưa đo độ chính xác tiếng Việt,
  chưa chốt ngưỡng đạt và chưa xuất Word (OCR-3).
- Không phát sinh yêu cầu Core/câu hỏi mới cho Anh. Giữ các mục **Cần Core**
  hiện có; máy đích cài/kiểm Tesseract theo mục **Cần cài**. Bộ DEMO chung
  cho scan/Word vẫn thuộc OCR-5, khóa hash wheel/máy sạch thuộc OCR-6.
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


## Bằng chứng OCR-4 — phiếu 14/11/2026, hoàn tất 15/11/2026

- Nhánh: `codex/e_ocr-ocr-4`; PR: **chờ lead mở**. Không chạy commit/push.
  Tiêu đề đề xuất: `[e_ocr] OCR-4 — Lượt chưa rõ và chống trùng bền`.
- Thời gian thực tế: **23:37 ngày 14/11/2026 – 00:08 ngày 15/11/2026**
  (31 phút, khoảng **0,52 giờ**), so với **4 giờ ước tính** trong phiếu;
  giờ Việt Nam. Ngày lát/phiếu giữ 14/11/2026, ghi đúng ngày kết thúc sau nửa đêm.
- `luot_abbyy.py` lưu metadata theo pháp nhân + băm; mã tương quan UUID5
  tất định theo hai giá trị đó và lần gửi bền. `viec_id`, `lan_thu`, năng
  lực đọc/xuất Word không tạo lượt ABBYY thứ hai khi còn lượt dở.
- `KhoTam.cap_nhat_nhieu` ghi sổ hạn mức và lượt `dang_gui` cùng commit,
  trước khi công bố tệp. Không lưu tên/đường dẫn hoặc nội dung tài liệu.
  Khóa hệ điều hành riêng theo mã lượt ngăn tranh đọc/dọn cùng PDF; khi
  tiến trình chết chỉ khóa được nhả, dấu bền vẫn còn.
- Lượt `dang_gui`/`chua_ro` tra thư mục ra đúng mã trước. Có PDF hợp lệ:
  chốt trang đã nhận đúng một lần, kiểm lớp chữ/số trang, chốt `xong` bền
  rồi dọn. Chưa có: `ChuaRo`, không gửi lại, không chuyển Tesseract, không
  hoàn. Lựa chọn nguồn mới, ABBYY tắt hoặc mất cấu hình không bỏ qua lượt dở.
- Nợ OCR-1 đã xử lý: hủy/lỗi sau khi ABBYY trả PDF cũng dọn tệp kết quả,
  kể cả chưa đọc bytes; test dùng `tra=True`. Chỉ `ChuaRo` giữ kết quả.
- Nợ OCR-2 đã xử lý: sau chết tiến trình, nhật ký đối chiếu `dang_giu` với
  kết quả/biên nhận để chốt hoặc nhả nguyên tử, không tính/hoàn hai lần.
  Không thấy tệp sau crash chưa đủ chứng minh chết trước hay sau công bố;
  tiếp tục giữ chỗ khi chưa có bằng chứng. Không tự hết hạn theo lease/tuổi lượt.
- Chỉ nhả khi chưa gửi/rút được tệp, hoặc nguồn xác nhận từ chối không
  tiêu trang; rút/dọn tệp vào còn chờ trước khi hoàn để tránh nhận muộn
  sau hoàn. Không rút được thì `ChuaRo`, giữ biên nhận và chỗ giữ. Có test
  giao lại cho cả nhánh rút được/không rút được. PDF lỗi, thiếu lớp chữ/sai
  số trang và sự im lặng không hoàn.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows x64, Python 3.13.14;
  ABBYY giả, dữ liệu DEMO. Test gồm App mới, `lan_thu` 2/3, tiến trình
  `spawn` chết thật ngay trước/sau công bố (`os._exit`, không finally), hai
  tiến trình gửi trùng và cùng lấy PDF muộn, cách ly pháp nhân, hủy/lỗi,
  ghi kho lỗi, PDF ghi dở, biên nhận sai và giữ lượt qua 60 ngày giả lập.
  Chưa chạy Linux, ABBYY/Core thật; test dùng API Python đa nền tảng,
  `msvcrt`/`fcntl` và `spawn`, không phụ thuộc fork.

### Kết quả ba lệnh bắt buộc OCR-4

Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`. Đầu ra SDK dưới đây chỉ
lược payload hai DEMO đọc; cả ba lệnh thực chạy riêng, mã thoát **0**:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
[ĐẠT] Đọc PDF DEMO có lớp chữ và vị trí, 3 trang: …
[ĐẠT] Đọc văn bản thuần từ PDF DEMO có lớp chữ, 3 trang: …
[ĐẠT] Xuất Word giữ bảng từ PDF DEMO có lớp chữ, 3 trang: {"loai": "tep", "tep": {"tep_id": "tep-7", "ten": "DEMO-bang-3-trang-OCR.docx", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "kich_thuoc": 1598}}
Engine e_ocr 1.0.4: mọi ví dụ chạy thử DEMO đều đạt.
Kết quả: 3/3 ĐẠT; mã thoát 0.

> .venv\Scripts\python -m pytest e_ocr/tests -q
........................................................................ [ 33%]
........................................................................ [ 66%]
........................................................................ [ 99%]
..                                                                       [100%]
218 passed in 53.00s
Mã thoát 0; 0 skipped.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát 0.
```

### Quyết định tạm, lệch và phần còn lại OCR-4

- Giữ lớp bọc tạm `kho_tam` theo phương án B; khi Core có #10 `luot-ben`
  phải thay phần lượt. Các mục cấu hình/ngăn/CAS của Core vẫn như trên.
  Không thêm dependency, không đổi API/SDK, không sửa mã cũ hoặc Core.
- Quy ước tạm biên nhận lỗi rõ: `<ma>.loi.json`, tối đa 2 KiB, đúng ba
  trường `ma_tuong_quan`, `trang_thai="tu_choi"`, `da_tieu_trang=false`.
  Chỉ nguồn xác nhận không tiêu trang mới được tạo biên nhận; không lấy
  lỗi parser/log hoặc tệp khác mã làm bằng chứng hoàn. Chốt lỗi giữ biên
  nhận bằng `ChuaRo` để lần sau đối chiếu. Quy ước được mô tả trong README;
  chưa kiểm nguồn ABBYY thật, xác nhận tiếp ở OCR-7. Không có bằng chứng
  thì giữ hạn mức. Đây không phải thay đổi hợp đồng API Core đã khóa.
- Lượt đã chốt `xong` không là cache nội dung. Việc mới sau lượt đã chốt
  tạo lần gửi tiếp; lát này chặn gửi trùng các lượt còn dở.
- Phạm vi: **5 tệp mã nghiệp vụ** (`abbyy`, `chon_nguon`, `kho_tam`,
  `luot_abbyy`, một dòng gọi cấu hình ở `van_ban`); thêm dòng metadata
  `__init__.py` và `engine.json` để đồng bộ phiên bản 1.0.4. `chay.py`,
  parser PDF, Tesseract/vendor và xuất Word không đổi so với nền OCR-2/3.
- SDK 2.0.0 cài offline trong `.venv --system-site-packages`, SHA-256 wheel
  khớp `SHA256SUMS.txt`. Dependency/pytest dùng bản có sẵn; chưa là cài
  máy sạch OCR-6. Đã cập nhật README/CHANGELOG/NGUON và băm tệp gói.
- Lịch sử trước giải gộp: nhánh dựng trên `5b987fd` (chưa có OCR-2),
  lần triển khai trước tự lấy nền qua archive do không ghi được metadata Git.
  Việc đồng bộ nền chính thức được xử lý ở mục giải gộp bên dưới; số liệu
  kiểm 218 test phía trên thuộc lần triển khai trước.
- Cần Core / Chờ Anh mới: **không phát sinh**. Giữ các mục chờ Anh có sẵn.


## Giải xung đột gộp OCR-4 — 15/11/2026

- Đã đối chiếu `5b987fd...HEAD` và `origin/main`: giữ nền OCR-2/OCR-3
  chính thức (1.0.3), áp riêng phần OCR-4; phiên bản kết quả **1.0.4**.
  Giữ cổng `ocr.xuat_word@1` qua `trich_van_ban`/bộ chọn nguồn và hai test
  Word `chi_tesseract`/`chi_abbyy`. Không thay Tesseract/vendor, parser PDF,
  cổng SDK hoặc bộ ghi Word của main.
- Giữ nguyên toàn bộ **181 test của main** (so nội dung từng tệp; riêng
  `test_kho_tam.py` chỉ nối thêm); bổ sung **37 test OCR-4**: 35 ca nhật ký/
  ABBYY và 2 ca cập nhật nhiều khóa. Tổng **218 test**, không bỏ/đổi test main.
- Đã bỏ dấu xung đột trong 10 tệp; `NGUON.md` có một hàng nguồn mỗi tệp,
  28 SHA-256 tính lại trên bytes cuối cùng (trừ chính `NGUON.md`).
- **Đã kiểm bằng Core giả (CoreGia)**, ABBYY giả và dữ liệu DEMO trên Windows;
  đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` cho cả ba lệnh:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
3/3 ĐẠT; Engine e_ocr 1.0.4; mã thoát 0.
> .venv\Scripts\python -m pytest e_ocr/tests -q -p no:cacheprovider
218 passed in 53.66s; 0 skipped; mã thoát 0.
> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát 0.
```

- Thời gian giải gộp thực tế: khoảng **4 phút (0,07 giờ)**; tách khỏi 31 phút
  triển khai OCR-4 đã ghi phía trên (phiếu OCR-4 ước tính 4 giờ).
- PR: **lead xử lý**. Không `git add`, commit hoặc push; index còn các mục
  unmerged để lead đánh dấu đã giải và hoàn tất merge. Các tệp ngoài OCR
  do merge tự động không bị chỉnh sửa trong lượt giải gộp này.
- Lệch mới / Cần Core / Chờ Anh mới: **không phát sinh**. Giữ lớp bọc tạm
  và quy ước biên nhận đã ghi; chưa kiểm Linux, ABBYY thật hoặc Core thật.


## Bằng chứng OCR-5 — phiếu 14/11/2026, thực hiện 15/11/2026

- Kết luận: **Đạt trong phạm vi OCR-5 — đã kiểm bằng Core giả (CoreGia)**.
  Gói **1.0.5**, nhánh `codex/e_ocr-ocr-5`; PR: **chờ lead mở**.
  Không commit/push. Tiêu đề đề xuất:
  `[e_ocr] OCR-5 — Bộ DEMO và bài OCR-MAY trên Core giả`.
- Thời gian thực tế: **15/11/2026, 00:17:00–00:33:50**, khoảng
  **0.28 giờ**, so với **4 giờ ước tính** trong phiếu; giờ Việt Nam.
- Đã chuyển bộ sinh từ `ma-nguon/tests/demo/tao_bo_demo.py` sang
  `tests/demo/tao_bo_demo.py`. Không sửa mã cũ. PDF quét 3 trang chỉ có
  ảnh bảng, PNG/JPEG 1 trang, Word/JSON đáp án có nhãn DEMO; bản ABBYY
  giả riêng có lớp chữ và hình học bảng. Giữ tệp DEMO cũ làm tham chiếu.
  Chỉ tệp nhỏ vào gói; PDF 61 trang, >20 MiB, tệp hỏng sinh ở tmp_path.
  Tệp lớn nhất trong gói **366.400 bytes**; không thêm dependency.
- Word đáp án luôn sinh bằng bộ ghi OOXML của gói, bỏ phụ thuộc tùy chọn
  python-docx của mã cũ; không coi đáp án là kết quả nhận dạng. Đã mở lại
  ZIP/XML để kiểm tên công ty/tiền/ngày, 3 bảng 4×3, mỗi bảng 10 ô gốc,
  một ô trống và ô đầu gộp 3 cột; bản Word từ ABBYY giả kiểm tương tự.
  Đã xem ảnh render trang PDF thật để xác nhận nhãn/chữ/bảng không cắt.
- Sáu ví dụ SDK: PDF quét/PNG × ba năng lực, `nguon=chi_tesseract`.
  `tests/chay_demo.py` gọi `CoreGia().chay_thu_demo`, cách ly cấu hình/kho
  bằng thư mục DEMO tạm, tự dùng Tesseract giả nếu thiếu executable hoặc
  vie+eng; `--gia` ép mock. Nguồn giả ở ngoài gói, không đổi engine thật.
- `tests/test_ocr_may.py`: ca 2, 3, 4, 5, 7, 9 đã kiểm bằng Core giả.
  Ca 3 thấy số chờ 3→2→1→0, PNG/JPEG đúng thứ tự; ảnh trùng nhận lại mã
  lượt dở, chỉ gửi hai lần/tính hai trang; giao lại lấy đúng PDF trả muộn.
  Chưa kiểm màn hình hàng chờ Core thật. Ca 1/6/8 ngoài đợt này: lần lượt
  chờ thẻ trạng thái Core, thiết kế trích vùng cùng Đối chiếu, bí mật và
  cầu nối có khóa; ghi rõ trong bài kiểm và YEU-CAU-VA-HIEN-TRANG.md.
- Ca 4: Tesseract thật có đủ vie+eng, **9 đúng/0 sai/9 phép đối chiếu**
  tên công ty/tiền/ngày trên 3 trang. Test lưu JSON số đo trong tmp_path,
  có property trong JUnit. Nguồn giả 9/9 chỉ kiểm luồng, không đo OCR.
  Không suy độ chính xác toàn văn/bảng ảnh hoặc áp ngưỡng Anh chưa chốt.
- Ca 9: log JSON stderr có năng lực, trạng thái, nguồn và thời gian
  chờ nguồn/chạy/tổng; kiểm thành công, Word, văn bản thuần, lớp chữ sẵn,
  lỗi/hủy/CHUA_RO. Ca ngoại lệ bất ngờ có chứa nội dung/đường dẫn DEMO
  vẫn không lộ: cổng đổi sang lỗi cố định trước khi SDK in traceback.
  Giữ ngoại lệ transport/hủy/chưa rõ. Chờ là chờ ABBYY, không giả mốc
  hàng chờ Core; action đã trả chưa bao gồm nộp kết quả/kết thúc SDK.
- Sửa nợ OCR-3: đăng ký namespace `w`/`xml`; test kiểm document.xml dùng
  `w:document`, có `xmlns:w`, không có `ns0:`. Ba nợ OCR-4 đã ghi ở mục
  **Nợ**, không vá. Chỉ **5 tệp mã gói** thêm/sửa: chay, chon_nguon,
  nhat_ky, xuat_word và metadata __init__; engine.json là phiếu.
- Môi trường Windows x64, Python 3.13.14; `.venv --system-site-packages`,
  SDK 2.0.0 cài offline từ wheel, SHA-256 khớp SHA256SUMS.txt. Dùng thư
  viện đã ghim/sẵn có; chưa là cài máy sạch OCR-6. Chưa chạy Linux,
  ABBYY hoặc Core thật. Không đọc hồ sơ thật hoặc Hot Folder thật.

### Kết quả ba lệnh bắt buộc OCR-5

Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`. CLI SDK dùng cấu hình
không tồn tại ở `.venv/khong-co-cau-hinh-DEMO.json` và dữ liệu tạm ở
`.venv/kiem-ocr5-du-lieu-DEMO` qua hai biến KTT_ENGINE_*; không đọc cấu
hình máy. Lượt CLI đầu dùng đích mặc định bị chặn quyền sandbox; đã chạy
lại với đích DEMO trong worktree. Không thay mã để bỏ kiểm quyền.

Đầu ra cuối thực tế, chỉ lược payload sáu dòng SDK cho ngắn:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
[ĐẠT] Đọc tài liệu có vị trí — PDF quét 3 trang DEMO, chỉ Tesseract: …
[ĐẠT] Đọc tài liệu có vị trí — ảnh PNG 1 trang DEMO, chỉ Tesseract: …
[ĐẠT] Đọc văn bản thuần — PDF quét 3 trang DEMO, chỉ Tesseract: …
[ĐẠT] Đọc văn bản thuần — ảnh PNG 1 trang DEMO, chỉ Tesseract: …
[ĐẠT] Xuất Word giữ bảng — PDF quét 3 trang DEMO, chỉ Tesseract: …
[ĐẠT] Xuất Word giữ bảng — ảnh PNG 1 trang DEMO, chỉ Tesseract: …
Engine e_ocr 1.0.5: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát 0; 6/6 ĐẠT, dùng Tesseract thật.

> .venv\Scripts\python -m pytest e_ocr/tests -q -p no:cacheprovider -o junit_family=legacy --junitxml=.venv/kiem-ocr5-tat-ca.xml
239 passed in 61.97s (0:01:01)
Mã thoát 0; 0 skipped, có test Tesseract thật.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát 0.
```

Kiểm bổ sung: `tests/chay_demo.py --gia` → **6/6 ĐẠT**, thông báo rõ
“Đã kiểm bằng Core giả (CoreGia) + Tesseract giả; không đo độ chính xác
OCR.” Test tự chuyển khi thiếu executable/ngôn ngữ cũng đạt. `NGUON.md`
có **38 SHA-256 khớp**, trừ chính NGUON.md; `git diff --check` không lỗi.
Đầu ra đầy đủ/JUnit/ảnh kiểm nằm trong `.venv/kiem-ocr5-*`, không đưa vào
gói hoặc git. Toàn bộ 218 test nền còn nguyên, thêm 21 test OCR-5.

### Lệch / quyết định tạm / Cần Core / Chờ Anh

- Không đổi API/SDK, không thêm dependency hoặc import Core. Giữ cấu hình
  JSON/kho tạm theo quyết định của lead; nhật ký stderr theo phiếu chung.
  Ngoài bộ DEMO/bài kiểm, bổ sung số đo tại cổng/chọn nguồn để đáp ứng
  ca 9; sửa namespace Word theo nợ lead giao. Không mở giao diện riêng.
- Cần Core mới: mốc/đếm hàng chờ chung và nhật ký SDK an toàn cho lỗi
  ngoài action; đã ghi mục Cần Core phía trên. Tệp quá cỡ bị SDK chặn
  trước action nên không có log action, không tạo bản ghi thời gian giả.
- Chờ Anh mới: **không phát sinh**. Giữ các mục giấy phép/hồ sơ thật/ngưỡng
  Tesseract đã có; ba nợ OCR-4 giữ nguyên để làm lát riêng.


## Bằng chứng OCR-7 — phiếu 14/11/2026

- PR: **chờ lead mở**. Công cụ mặc định chạy khô; chỉ `--that` mới gửi PDF quét DEMO vào các thư mục riêng do cấu hình chỉ định. Không truy cập Hot Folder thật trong lượt triển khai.
- ABBYY giả: đã kiểm luồng PDF, so tiền/ngày từng trang, xuất và kiểm cấu trúc Word; JSON ghi biên nhận chưa kiểm chứng khi không có từ chối. Thời gian JSON tính từ đầu sinh DEMO đến kết thúc xử lý, gồm cả thời gian chờ.
- ABBYY thật và việc ABBYY/script tích hợp có sinh `<ma>.loi.json` đúng OCR-4 **chưa được kiểm**. Một lượt thành công hoặc quá hạn không chứng minh nguồn hỗ trợ biên nhận; cần lượt từ chối thực tế để kiểm. Quá hạn giữ trạng thái chưa rõ, không tự gửi lại.
- Kết quả lượt kiểm trước: SDK DEMO 6/6 ĐẠT, pytest 241 passed, 0 skipped, kiểm độc lập mã 0; đã kiểm bằng Core giả (CoreGia), ABBYY giả. Chưa kiểm Linux, Core thật hay ABBYY thật.
- Không phát sinh yêu cầu Core/SDK mới. Các dependency của gói cần có sẵn theo hướng dẫn cài máy sạch; `.cmd` cài SDK offline và mặc định chạy khô. Ngày 15/11/2026: sửa mã hóa và làm rõ hướng dẫn cài dependency; PR chờ lead mở.
## Bằng chứng OCR-6 — phiếu 14/11/2026

- Nhánh `codex/e_ocr-ocr-6`; PR: **chờ lead mở**. Không commit/push.
- Thời gian thực tế: 00:37–00:43 ngày 15/11/2026, khoảng 0,10 giờ; phiếu ước tính 2 giờ.
- Ghim SDK và các wheel PyPI Windows x64 CPython 3.13/Linux x86_64 bằng SHA-256. Pillow dùng trực tiếp; PyMuPDF và defusedxml không dùng. SDK wheel khớp SHA256SUMS.txt. `NGUON.md` cập nhật nguồn, giấy phép và hash tệp gói; không tự băm.
- Đã kiểm bằng Core giả (CoreGia): `tests/chay_demo.py --gia` đạt 6/6 với Tesseract giả, không đo độ chính xác OCR.
- Windows máy sạch: venv mới cài SDK thành công, tải pdfplumber thất bại do kết nối `files.pythonhosted.org` bị reset; chưa kiểm được cài lock/DEMO máy sạch. Script cho phép cấu hình pip wheelhouse, SDK cài offline. Linux: chưa chạy vì máy không có WSL; đã thêm workflow CI, chưa có kết quả CI.
- SDK CLI trực tiếp: 0/6, lỗi không truy cập dữ liệu tạm OCR trong môi trường hiện tại; không suy diễn thành lỗi nghiệp vụ. Pytest: 239 passed, 0 skipped; kiểm độc lập: đạt.
- `vendor/mask_ocr/extraction.py` và `layout.py` được import gián tiếp qua `__init__.py`, có test vendor, nhưng parser DOCX/layout không được action hiện tại gọi; OCR-3 chuyển thể quy tắc sang `xuat_word.py`, không gọi parser. Giữ nguyên để tránh phá import/test; rà tách phần không dùng và chuyển `LUU-TRU/` sau, không xóa.
- Cần Core: không phát sinh; giữ các mục hiện có.

## Bằng chứng OCR-8 — 15/11/2026

Phần dưới ghi lịch sử lượt OCR-8 trước NGAN-0; kết quả nối mẫu chung và
báo cáo mới nhất ở cuối tài liệu thay các ghi chú chờ/skip NGAN-0 cũ.

- Nhánh `codex/e_ocr-ocr-8`; PR: **chờ lead mở**. Chỉ sửa trong worktree
  được giao; không commit/push, không sửa mẫu chung, SDK, Core hoặc mã cũ.
- **Đã kiểm bằng Core giả (CoreGia)**, ngăn RAM `NganBoNho`, ABBYY giả và
  KttCore/DOM giả của Node. CLI DEMO dùng Tesseract thật với `vie+eng`.
  Chưa kiểm Linux, Core/ABBYY thật hoặc UI trong trình duyệt thật.
- SDK 2.0.0 cài offline từ wheel, SHA-256 khớp
  `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
  `.venv --system-site-packages` dùng thư viện sẵn có, tất cả phiên bản
  khớp `requirements.lock`; không dùng mạng, không thêm dependency.
- Bốn bảng: `cau_hinh`, `han_muc_ngay`, `luot_abbyy`, `trang_thai_engine`.
  Bảng lượt có khóa `ma_tuong_quan`, phạm vi `phap_nhan` và duy nhất
  `[phap_nhan_id, bam_noi_dung]`; sổ ngày và cấu hình dùng phạm vi engine.
  Không đặt hạn tự xóa cho lượt chưa rõ hoặc bản mốc CAS của hạn mức.
- Giữ trang + lấy hoặc tạo lượt cùng một lô nguyên tử. Mọi thay đổi sổ
  tăng bản `trang_thai_engine/han_muc` bằng CAS để bảo vệ tổng 30 ngày,
  kể cả hai việc ở hai bên nửa đêm. CAS lệch thử lại tối đa 12 lần,
  không cộng lại trang từ giao dịch thất bại. Đọc trạng thái đã cũ không
  được tạo thế hệ gửi mới: đóng nợ OCR-4 số 1.
- Quyền xử lý lượt có CAS, 30 giây, gia hạn khi còn 10 giây. Worker mất
  quyền không được chốt/hoàn/dọn thay worker mới; quyền hết hạn chỉ cho
  đọc lại cùng mã. Dấu lượt và trang đang giữ không tự hết hạn theo quyền.
- Giữ phương án B: đã nhận/chưa rõ thì không chuyển nguồn, không gửi
  lại, không tự hoàn. Kết quả muộn chốt đúng mã; từ chối rõ chỉ hoàn một
  lần, sau khi rút/dọn được tệp vào. Nợ OCR-4 số 2 và 3 vẫn còn.
- Màn cấu hình dùng `KttCore.engine("e_ocr")`: đầy đủ trường ABBYY và
  Tesseract, lưu cấu hình bằng CAS, hạn mức 30 ngày trừ cả trang đang giữ,
  trạng thái cập nhật định kỳ và danh sách chờ đối chiếu đọc hết phân trang.
  Bản trạng thái quá 90 giây hiện chưa có cập nhật; không lấy công tắc
  cấu hình thay cho trạng thái engine. Không lộ mã, dùng `textContent`.
- Giữ nguyên `kho_tam.py`, `cau_hinh_may.py` và schema cấu hình máy cũ
  trong gói, chờ lead chuyển `LUU-TRU/`; không còn nạp chúng từ cổng chạy.
  Các test riêng của mã cũ vẫn giữ để kiểm hồi quy, chỉ dùng thư mục DEMO.
- `engine.json` vẫn đúng SDK 2.0, phiên bản engine 1.0.8. Phần ngăn/schema/
  màn quản trị khai riêng trong `KHAI-SDK-2.1.json`.

### Các phần review trong lát OCR-8

Phiếu này vượt mốc khoảng 5 tệp mã, chia thành ba phần review cùng worktree
theo lệnh lead (lead tự commit/mở PR): OCR-8a gồm hai mẫu `ngan.py` và
`cau_hinh.py`; OCR-8b gồm năm mô-đun nối runtime `abbyy`, `chay`,
`chon_nguon`, `luot_abbyy`, `van_ban`; OCR-8c gồm màn JS và đồng bộ phiên
bản `__init__`. Lý do: cổng ngăn, giao dịch và màn cấu hình cần cùng có để
kiểm trọn hành vi OCR-8; không thêm tính năng ngoài phiếu.

### API Ngan đã dùng — để lead đối chiếu NGAN-0

Mã engine chỉ dùng các hàm public dưới đây, không gọi thành phần nội bộ
của `NganBoNho`:

```python
chon_ngan(app)                         # ưu tiên app.ngan; trong việc ưu tiên viec.ngan
ngan.doc(bang, khoa)                   # None hoặc BanGhi.gia_tri, .row_version
ngan.tim(bang, loc=..., gioi_han=..., tiep=...)
# -> {"danh_sach": [BanGhi, ...], "tiep": str | None}
with ngan.lo() as lo:
    lo.them(bang, khoa, gia_tri)
    lo.sua(bang, khoa, gia_tri, row_version=...)
    lo.xoa(bang, khoa, row_version=...)
    lo.lay_hoac_tao(bang, khoa_duy_nhat, gia_tri)
# Gửi khi ra with; mọi lệnh cùng thành công hoặc rollback; NganXungDot -> thử lại.
doc_cau_hinh(ngan, schema)              # None nếu thiếu; dict đã kiểm/điền mặc định
```

- `khoa_duy_nhat` của lượt là `{phap_nhan_id, bam_noi_dung}`; khóa sửa/xóa
  lượt là `{phap_nhan_id, ma_tuong_quan}`. Mọi truy vấn lượt đều kèm pháp
  nhân. Khóa cấu hình là `{"ma": "cau_hinh"}`; giá trị có `abbyy`, `tesseract`.
- Bản tạm chỉ dùng thư viện chuẩn. API phụ để **test bản RAM**, không
  được mã nghiệp vụ gọi: `NganBoNho(khai_bao, phap_nhan_id=None)`;
  `doc/tim/lo(..., phap_nhan_id=...)`; `lo.ket_qua` gồm bản ghi có
  `.da_tao`. Test lỗi có chèn xung đột tại bản RAM, không đòi API phụ này
  từ SDK thật. Test qua cổng giả chỉ có `doc/tim/lo` vẫn xử lý OCR được.
- Trình duyệt tạm dùng `.cau_hinh.doc()` trả
  `{gia_tri, phien_ban_cau_hinh}`, `.cau_hinh.luu(gia_tri, phien)` trả
  `{phien_ban_cau_hinh}`; `.ngan.doc(bang, khoa)`,
  `.ngan.tim(bang, {loc, gioi_han, tiep})`. Bản ghi có `.gia_tri`.
  Đây là hình dạng kết quả mà KttCore giả kiểm; cần Core đối chiếu khi nối.

### Lệch khỏi phiếu / quyết định tạm

- NGAN-0 đang làm song song, chưa có trong worktree: viết hai bản tạm
  trong gói theo đúng các tên API được giao, không tạo/sửa `_chung/mau-ma`.
  Hai test so băm viết sẵn, skip đúng lý do **"chờ NGAN-0 gộp"**; lead
  thay mẫu rồi bật lại test. Không coi đây là đã kiểm băm mẫu chung.
- Các ca OCR-4/OCR-5 chạy lại với ngăn RAM. Ca cạnh tranh đa tiến trình
  của sổ/lượt được chuyển thành hai luồng cùng `NganBoNho`; ca chết thật
  được đổi sang trạng thái gián đoạn trước/sau công bố rồi dùng lại cùng
  ngăn. RAM không chia sẻ giữa tiến trình, không lưu qua khởi động lại;
  không báo những ca này là kiểm độ bền đa tiến trình của Core thật.
- Giữ cách chọn nguồn cũ: thiếu cấu hình ABBYY thì `chi_abbyy` báo
  `CHUA_CAU_HINH`; chế độ tự động/chỉ Tesseract vẫn dùng mặc định executable
  và `vie+eng`. Lượt ABBYY dở vẫn phải đối chiếu, kể cả khi cấu hình bị mất.

### Kết quả ba lệnh bắt buộc — lượt kiểm cuối OCR-8

Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`. Đã kiểm bằng Core giả
(CoreGia); dưới đây trích trạng thái/kết luận từ đầu ra thực tế:

```text
> .venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
[ĐẠT] Đọc tài liệu có vị trí — PDF quét 3 trang DEMO, chỉ Tesseract
[ĐẠT] Đọc tài liệu có vị trí — ảnh PNG 1 trang DEMO, chỉ Tesseract
[ĐẠT] Đọc văn bản thuần — PDF quét 3 trang DEMO, chỉ Tesseract
[ĐẠT] Đọc văn bản thuần — ảnh PNG 1 trang DEMO, chỉ Tesseract
[ĐẠT] Xuất Word giữ bảng — PDF quét 3 trang DEMO, chỉ Tesseract
[ĐẠT] Xuất Word giữ bảng — ảnh PNG 1 trang DEMO, chỉ Tesseract
Engine e_ocr 1.0.8: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát: 0; 6/6 ĐẠT.

> .venv\Scripts\python -m pytest e_ocr/tests -q -rs
SKIPPED [2] e_ocr\tests\test_ngan_ocr8.py:25: chờ NGAN-0 gộp
266 passed, 2 skipped in 55.95s
Mã thoát: 0.

> .venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
[ĐẠT] Gói e_ocr độc lập; không import Core/kênh cũ, không có tệp biên dịch sẵn.
Mã thoát: 0.
```

- Node UI: **7/7 passed, 0 skipped**, chạy bằng `node --test`; pytest có
  một ca gọi lại trọn bộ Node này. Kiểm lưu/CAS, phân trang, biên 30 ngày,
  trang đang giữ, trạng thái hết hạn, lỗi an toàn, dừng chu kỳ khi đóng.
- Kiểm bổ sung: **43/43** SHA-256 nguồn gói khớp `NGUON.md`;
  `git diff --check` sạch. Cổng engine trong tiến trình Python mới không
  nạp `kho_tam`/`cau_hinh_may`. Tài liệu SDK, mẫu chung, mã cũ và hai
  mô-đun lưu đĩa cũ không đổi; không có tệp Git bị xóa.

### Báo cáo bàn giao OCR-8

Kết luận: **Đạt trong phạm vi được giao** — đã kiểm bằng Core giả (CoreGia)
và NganBoNho; ngăn thật/màn thật chờ Core/SDK 2.1.

Đã làm: chuyển cấu hình/sổ/lượt sang ngăn, lô nguyên tử/CAS và chống trùng,
đóng nợ OCR-4 số 1, giữ phương án B, thêm màn cấu hình/trạng thái và khai SDK 2.1.

Kết quả kiểm: SDK DEMO **6/6 ĐẠT**; pytest **266 passed, 2 skipped**
(chờ NGAN-0 gộp); kiểm độc lập mã **0**; Node UI **7/7**.

Thời gian thực tế: **0,56 giờ**, ngày **15/11/2026, 07:38:00–08:11:25**
(giờ Việt Nam); so với **5 giờ ước tính** trong phiếu.

Lệch khỏi phiếu / quyết định tạm: hai mẫu trong gói đang là bản tạm chờ
NGAN-0; test băm skip theo lệnh lead. Ca đa tiến trình/crash cũ được kiểm
lại bằng hai luồng/trạng thái gián đoạn trên cùng ngăn RAM như mô tả trên.

Cần Core / Chờ Anh mới phát sinh: gộp NGAN-0, đối chiếu hình dạng kết quả
API và cấp ngăn/màn quản trị SDK 2.1 theo mục Cần Core; **không có câu chờ
Anh mới**. PR: **chờ lead mở**; không commit/push.


## N?i ng?n chung NGAN-0 ? OCR-8, 15/11/2026

K?t lu?n: **??t** trong ph?m vi ???c giao ? **?? n?i ng?n chung NGAN-0**
(PR #34), ?? ki?m b?ng Core gi? (CoreGia). PR: **ch? lead m?**.
M?c n?y thay k?t lu?n ch? NGAN-0 v? skip trong b?o c?o OCR-8 tr??c ??.

?? l?m:
- Gi? nguy?n `ngan.py`, `cau_hinh.py` trong g?i v? to?n b? `_chung/**`;
  hai test so SHA-256 ch?y sau chu?n h?a CRLF?LF, kh?ng skip.
- Kh?i t?o RAM b?ng `KHAI-SDK-2.1.json/ngan_du_lieu`; b?ng `cau_hinh`
  c? `khoa: []`, ??c/ghi b?ng kh?a `{}`, gi? tr? ch?nh l? dict c?u h?nh.
  `doc_cau_hinh` tr? dict/None; default ch? ?i?n tr?n b?n sao.
- ??c `TrangNgan.danh_sach/tiep`; nh?n `KetQuaLenh` t? l?nh l?, ch? ??c
  `gia_tri/da_tao` sau commit. Ph?p nh?n n?m trong kh?a/b? l?c, h? tr?
  `viec.ngan` ?? g?n ph?p nh?n, ?u ti?n ng?n SDK khi ???c c?p.
- Chuy?n `NganXungDot`, `NganKhongHopLe`, `CauHinhKhongHopLe` sang
  `LoiNghiepVu` t?i bi?n SDK, gi? `ma/thong_diep/thu_lai_duoc`.
- Gi? ph??ng ?n B c?a OCR-4: kh?ng g?i ABBYY l?n hai khi l??t c?n d?,
  kh?ng t? ho?n trang/h?t h?n l??t; trang v? l??t v?n c?ng l? nguy?n t?
  c? m?c CAS. Test l?i gi? l? v? xung ??t d?ng API public, kh?ng m?c
  `_ghi_lo` c?a b?n t?m. Gi? to?n b? test h?nh vi OCR-4/OCR-MAY.
- B? sung n?m ca ki?m kh?i t?o b?ng/gi? ng?n SDK, ba ngo?i l? chung v?
  ng?n theo vi?c ?? g?n ph?p nh?n. C?p nh?t README, CHANGELOG, NGUON.md;
  43/43 SHA-256 kh?p theo quy ??c LF, t?p nh? ph?n b?m nguy?n byte.

K?t qu? ba l?nh b?t bu?c (??u ra th?c t?; `PYTHONUTF8=1`,
`PYTHONDONTWRITEBYTECODE=1`, Python 3.13.14, SDK 2.0.0 trong `.venv`):

```text
> .venv/Scripts/python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
[??T] ??c t?i li?u c? v? tr? ? PDF qu?t 3 trang DEMO, ch? Tesseract
[??T] ??c t?i li?u c? v? tr? ? ?nh PNG 1 trang DEMO, ch? Tesseract
[??T] ??c v?n b?n thu?n ? PDF qu?t 3 trang DEMO, ch? Tesseract
[??T] ??c v?n b?n thu?n ? ?nh PNG 1 trang DEMO, ch? Tesseract
[??T] Xu?t Word gi? b?ng ? PDF qu?t 3 trang DEMO, ch? Tesseract
[??T] Xu?t Word gi? b?ng ? ?nh PNG 1 trang DEMO, ch? Tesseract
Engine e_ocr 1.0.8: m?i v? d? ch?y th? DEMO ??u ??t.
M? tho?t: 0. Payload DEMO ???c l??c trong b?n ghi n?y.

> .venv/Scripts/python -m pytest e_ocr/tests -q --basetemp=.pytest-tmp
273 passed in 56.93s
M? tho?t: 0; 0 skipped.

> .venv/Scripts/python e_ocr/tests/kiem_doc_lap.py
[??T] G?i e_ocr ??c l?p; kh?ng import Core/k?nh c?, kh?ng c? t?p bi?n d?ch s?n.
M? tho?t: 0.
```

SDK DEMO d?ng **CoreGia v? Tesseract th?t (vie+eng)** v?i d? li?u DEMO,
kh?ng c?n c?ng thay th? ho?c c?u h?nh ABBYY. Test ABBYY d?ng ngu?n gi?;
UI v?n ki?m qua KttCore/DOM gi? trong b? pytest. Kh?ng ch?y ABBYY/Core
th?t, m?y s?ch ho?c Linux trong l??t n?y. B?m wheel SDK kh?p
`SHA256SUMS.txt`; kh?ng th?m dependency hay d?ng m?ng.

Th?i gian th?c t? n?i NGAN-0: **0.16 gi?**, ng?y **15/11/2026,
08:12:00?08:21:53** (gi? Vi?t Nam); phi?u OCR-8 **5 gi? ??c t?nh**,
kh?ng c? ??c t?nh ri?ng cho l??t n?i n?y. Th?i gian OCR-8 tr??c ?? ???c
b?o ri?ng ? ph?n l?ch s?.

L?ch kh?i phi?u / quy?t ??nh t?m ?? d?ng: kh?ng ph?t sinh; ch? s?a b?n
m?-?un runtime v? khai b?o b?ng, kh?ng ??i manifest/API SDK ?? kh?a.
RAM t?m theo quy?t ??nh Anh 15/11; m?t d? li?u khi kh?i ??ng l?i.

C?n Core / Ch? Anh m?i ph?t sinh: **kh?ng**. C?n c?c vi?c ?? ghi ? m?c
C?n Core: ng?n b?n SDK 2.1, quy?n/ph?m vi th?t v? m?n qu?n tr? trong Core;
kh?ng c?n ch? NGAN-0. N? OCR-4 s? 2, 3 gi? nguy?n ngo?i ph?m vi.
Kh?ng commit/push; lead th?c hi?n commit v? m? PR.

## Giới hạn đã biết sau OCR-9 (kiểm độc lập 15/11/2026)

- `luot_abbyy` không có hạn giữ và SDK 2.2.0 không có lệnh xóa: mỗi (pháp nhân, tài liệu) giữ 1 hàng vĩnh viễn. Cần Core: hạn giữ riêng cho lượt đã chốt.

- Chỗ giữ `dang_giu` nằm trong một map ≤ 64 KiB; chỗ giữ bỏ dở không tự giải phóng; đầy thì mọi lượt mới báo NGAN_DU_LIEU_QUA_LON — Admin đối chiếu thủ công.
