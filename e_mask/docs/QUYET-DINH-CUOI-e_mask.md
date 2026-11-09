# QUYẾT ĐỊNH CUỐI — Engine Mask

*Ngày 06/11/2026. Bản hợp nhất: quyết định cuối 20:35 + bổ sung sửa 21:00 + rà soát schema MASK-TT lúc 21:05. Thay thế phương án trong "Phiếu kế hoạch tổng thể — Che định danh" (`PHIEU-ENGINE-e_mask.md`, mốc git `2f6a05a9`) và các điểm trái với quyết định này trong "Tóm tắt 4 schema Mask để Anh duyệt" (`TOM-TAT-SCHEMA-MASK-CHO-ANH.md`).*

## 1. Phạm vi đồng ý

- **Engine Mask = lõi Mask file v2 (phần mềm nội bộ) + API.** Tận dụng tối đa code đã viết. **Không lấy phần OCR** của Mask v2 — nhận dạng chữ thuộc engine OCR (e_ocr).
- **Luồng chuẩn:** module gửi văn bản/tệp qua API Core → Mask che theo bảng định danh – bí danh trong CSDL Core → định danh nghi ngờ thì **che luôn bằng bí danh tạm** và đưa vào danh sách chờ → trả kết quả đã che kèm **mã yêu cầu** về module → Admin duyệt danh sách chờ → mục duyệt ghi vào CSDL.
- **Luồng tệp tham khảo AI (mục đích chính của che giữ định dạng):** module gửi tệp Word/Excel → Mask che → tệp đã che ra AI để tham khảo/hiệu chỉnh → AI trả tệp đã sửa → module gửi tệp kèm mã yêu cầu → Mask **đổi ngược bí danh thành tên gốc** → trả tệp về **đúng module đã gửi**.
- **Dạng đầu ra:**
  - Mặc định: **văn bản đã che** cho mọi loại đầu vào (văn bản, tệp có lớp chữ, tệp scan).
  - Riêng **Word (.docx) và Excel (.xlsx)**: module được chọn nhận lại tệp cùng định dạng (che và mở che).
  - PDF (có lớp chữ hoặc scan): chỉ trả văn bản, không dựng lại tệp.
- **Tệp scan/ảnh:** Core tự điều phối OCR → Mask (văn bản do OCR trả đi theo mẫu che văn bản). Mask không tự nhận dạng chữ.
- **Có mở che:** tra ngược bảng chung (bí danh chính thức + cột tạm); **bắt buộc kèm mã yêu cầu**; chỉ trả cho đúng module và người gửi yêu cầu.
- **Thời điểm:** làm **song song** Hỏi AI bản 1. Mask chưa nối Cloud trong mốc này; bước "AI sửa tệp" do lead giả lập. Gửi thật ra Cloud thuộc Hỏi AI bản 2.

## 2. Các lát

### 2.1 Giữ / thêm — 8 lát, theo thứ tự ưu tiên

Thứ tự: **1 → 2 → 3 → 4 → 8 → 6 → 7**; lát 5 chạy song song lát 3–4.

| Thứ tự | Lát | Nội dung | Tiêu chí chính |
|---:|---:|---|---|
| 1 | 1 | Lấy lõi Mask v2 vào gói engine, **tách bỏ OCR**; giữ code che tệp Word/Excel; kiểm kê phụ thuộc (gồm cryptography) | Không còn code/chỗ gọi OCR; chỉ kiểm giấy phép thư viện bên thứ ba; báo rõ mức hỗ trợ Word/Excel hiện có — phần chưa có thì trình, không tự viết thay |
| 2 | 2 | **Bảng định danh – bí danh** trong khối dữ liệu riêng của CSDL Core, có cột bí danh tạm; **bảng mã yêu cầu**; công cụ chuyển danh mục từ Mask v2 | Tên tiếng Việt không dấu; giới hạn quyền đọc; quy tắc bí danh theo mục 3 (mã Junsky / mã tự sinh, không trùng tiền tố); đối chiếu số dòng trước/sau chuyển; xác nhận danh mục Mask v2 hiện có giữ mã Junsky đến đâu |
| 3 | 3 | **API che và mở che văn bản — mẫu 1–4** (mục 5), cho văn bản trực tiếp và văn bản đến từ OCR | Không sót định danh; tiền/ngày giữ nguyên; mở che thiếu/sai mã yêu cầu hoặc khác module → từ chối; lỗi báo tiếng Việt, không chứa định danh, không cắt ngầm |
| 4 | 4 | **Danh sách chờ + màn duyệt cho Admin** (lọc kiểu Excel); việc dọn bí danh tạm | Duyệt → cấp bí danh mới (mã Junsky nếu đối tác có), bí danh cũ sang cột tạm; từ chối → xóa khỏi danh sách; dọn bỏ qua mã yêu cầu còn "đang xử lý" |
| 5 | 8 | **Che và mở che tệp — mẫu 5–8** (mục 5), giữ định dạng Word/Excel; PDF có lớp chữ trả văn bản (phụ thuộc lát 2, 3) | Xem 2.2 |
| 6 | 6 | **Công bố Mask trong Core và đóng gói** (G3-GOI-28, phần còn nợ của 30); đăng ký 8 contract | Chỉ công bố năng lực đã kiểm; tên contract theo mục 5.4 |
| 7 | 7 | **Bài test tổng thể** (mục 4) | Ca scan ghi riêng nếu OCR chưa nối chuỗi |
| song song | 5 | **Màn thử che/mở che DEMO** (chỉ Admin), gồm thử văn bản và tệp | Dữ liệu DEMO có nhãn rõ |

### 2.2 Tiêu chí lát 8

- **Khi che:** không sót định danh ở mọi chỗ trong tệp —
  - Word: thân văn bản, đầu/chân trang, ghi chú, bình luận, lịch sử sửa, thuộc tính tệp.
  - Excel: tên sheet, sheet ẩn, ô ẩn, bình luận, nhãn biểu đồ, thuộc tính tệp.
- **Khi mở che tệp đã bị AI sửa:** khôi phục đúng tên gốc kể cả khi bí danh bị đổi hoa/thường, thêm dấu cách thừa, hoặc bị tách thành nhiều đoạn định dạng trong Word; giữ nguyên nội dung AI thêm mới. Bí danh không nhận ra được → **không đoán**, trả tệp kèm danh sách bí danh chưa mở được và vị trí (sheet/ô hoặc đoạn).
- **Chung:** tiền/ngày (kể cả ô số Excel) giữ nguyên; bố cục không vỡ; không còn tệp gốc trên đĩa; tệp chỉ trả về đúng module đã gửi.

### 2.3 Bỏ

Lý do chung: danh mục đã chuyển vào CSDL, không còn bí mật nằm trong bộ nhớ.

| Lát cũ | Xử lý |
|---|---|
| Khóa chỉ qua bộ nhớ (MASK-KHOA) | Bỏ — bảng không mã hóa cột, không còn khóa |
| Tài khoản Windows riêng (MASK-WIN) | Bỏ — tiêu chí "không còn tệp gốc trên đĩa" chuyển vào lát 3 và 8 |
| Phát hiện riêng (MASK-3-TK, MASK-3) | Bỏ — việc dò nằm trong bước che + danh sách chờ |
| Lượt có hạn (mã lượt, hết hạn, mất lượt khi khởi động lại) | Bỏ — thay bằng mã yêu cầu + quy tắc dọn bí danh tạm |
| Khảo sát che tệp (MASK-4-TK); che tệp (MASK-4) | Thay bằng lát 8, chỉ dựng lại Word/Excel |
| Môi trường Python riêng (MASK-MOI-TRUONG) | **Bỏ có điều kiện** — chỉ quay lại nếu kiểm kê lát 1 thấy xung đột thư viện với Core; khi đó dùng thư viện riêng cho tiến trình Mask, **không nâng thư viện chung của Core** |
| Bốn mẫu trao đổi dự thảo (MASK-HOP-DONG) | Viết lại thành **8 mẫu** (mục 5); mẫu 1–4 thuộc lát 3, mẫu 5–8 thuộc lát 8 |

## 3. Các câu đã chốt

| Câu hỏi | Chốt |
|---|---|
| Lưu dữ liệu mask | Chỉ dữ liệu cần mask (tên, địa chỉ, MST, dữ liệu khác) lưu trong CSDL Core, gắn sẵn bí danh. Bảng đối chiếu **không còn** nằm trong bộ nhớ Mask |
| Dạng bí danh | Dạng riêng bọc `[[...]]`, cho mọi đầu ra. **Đối tác có mã đối tượng Junsky → `[[<mã Junsky>]]`** (giữ quy tắc TL 48), ví dụ `[[KH-00123]]`; **định danh khác → mã tự sinh** theo loại, ví dụ `[[CT-0001]]`. Hai loại mã không được trùng tiền tố — lead đề xuất bộ tiền tố |
| Mã yêu cầu | Thay "mã lượt". Core cấp khi che; gắn module + người gửi + tài liệu; trạng thái **đang xử lý / đã đóng**. **Bắt buộc khi mở che**; khác module/người gửi hoặc mã không tồn tại → từ chối. Không gửi mã cho Cloud |
| Mở che | Có, tra ngược bảng chung (bí danh chính thức + cột tạm); mã yêu cầu dùng để kiểm quyền và giữ bí danh tạm, không giới hạn bảng tra |
| Nhận diện khi mở che | Mềm: không phân biệt hoa/thường, bỏ qua dấu cách thừa, ghép bí danh bị tách đoạn |
| Bí danh không mở được | Trả kết quả kèm danh sách và vị trí; không đoán; không công bố là đã mở che đầy đủ |
| Bí danh tạm khi được duyệt | Cấp bí danh mới; bí danh tạm cũ lưu ở cột tạm |
| Dọn bí danh tạm | Khi không còn mã yêu cầu nào ở trạng thái "đang xử lý" dùng nó. Tệp đã gửi ra AI giữ "đang xử lý" đến khi mở che xong hoặc module đóng việc |
| Phạm vi bí danh | Chung toàn tập đoàn |
| Người duyệt danh sách chờ | Admin |
| Cụm gốc mới phát hiện | Ghi thẳng vào danh sách chờ trong CSDL; **không trả trong phản hồi** cho module, không vào nhật ký, không vào contract công bố. Phản hồi chỉ báo số cụm chờ duyệt |
| Bảo vệ bảng định danh | Khối dữ liệu riêng, giới hạn quyền, không mã hóa cột |
| Tệp scan/ảnh | Core tự chuyển OCR → Mask (mẫu 1) |
| Dạng đầu ra | Văn bản đã che; Word/Excel được chọn nhận lại tệp; PDF chỉ văn bản |
| Số mẫu trao đổi | **8 mẫu**: 4 cho văn bản, 4 cho tệp (mục 5) |
| Điều kiện cho đi Cloud (khi bật ở bản 2) | Chỉ khi: engine sẵn sàng, không còn sót định danh, tiền/ngày giữ nguyên (đã kiểm thực tế), Mask không lỗi. Thiếu một điều kiện → chặn. Bỏ điều kiện "danh mục đang mở". Chỉ nội dung đã che đi Cloud; không kèm mã yêu cầu, cụm gốc, bảng đối chiếu |
| Giới hạn | Giữ trần đầu vào văn bản: 500.000 ký tự; định danh đã biết ≤500 mục, giá trị ≤300 ký tự, nhóm ≤20 ký tự. **Trần dung lượng tệp và trần đầu ra: lead trình sau thử DEMO**. Vượt trần → từ chối, không cắt ngầm |
| Danh mục thật | Bài test chỉ dùng DEMO; chuyển danh mục thật làm riêng khi vận hành, Anh xác nhận số dòng trước/sau |
| Giờ công | **Chưa có** — lead ước lại theo 8 lát và trình Anh |

## 4. Bài test tổng thể cuối — 11 bước, ước 135 phút, chỉ dữ liệu DEMO

**Lead chuẩn bị:** Admin DEMO, người dùng DEMO A và DEMO B, hai module DEMO; danh mục DEMO đã chuyển vào CSDL, trong đó có một đối tác DEMO mang mã Junsky DEMO; tệp Word, Excel, PDF có lớp chữ, PDF scan — đều ghi "Dữ liệu giả — DEMO". Không gọi Cloud. Thời lượng là ước lượng xếp lịch, chưa phải số đo.

| # | Phút | Thao tác | Phải thấy |
|---:|---:|---|---|
| 1 | 10 | Quản trị Core → Quản lý engine → Che định danh | Engine sẵn sàng; lõi Mask v2 không kèm OCR; số dòng danh mục DEMO khớp; 8 mẫu trao đổi hiển thị đúng |
| 2 | 15 | Màn thử che (Admin): văn bản DEMO có đối tác mã Junsky DEMO, một công ty khác, MST, địa chỉ, 1.000.000 VND, 30/10/2026 | Đối tác Junsky thành `[[<mã Junsky DEMO>]]`, định danh khác thành mã tự sinh `[[...]]`; tiền/ngày giữ nguyên; có mã yêu cầu |
| 3 | 15 | Thêm một tên lạ chưa có trong bảng | Vẫn bị che bằng bí danh tạm, vào danh sách chờ; phản hồi chỉ báo số cụm chờ, không chứa cụm gốc |
| 4 | 15 | Module DEMO gửi tệp Word/PDF có lớp chữ (mẫu 5), chọn nhận văn bản | Văn bản đã che; không sót định danh; không còn tệp gốc trên đĩa |
| 4b | 15 | Module DEMO gửi Word và Excel DEMO (định danh ở đầu trang, bình luận, sheet ẩn, thuộc tính tệp), chọn nhận lại tệp. Lead giả lập AI sửa: thêm đoạn mới, đổi hoa/thường một bí danh, tách một bí danh, làm hỏng hẳn một bí danh; gửi tệp đã sửa kèm mã yêu cầu để mở che (mẫu 7) | Tệp che không sót ở chỗ ẩn. Tệp mở che khôi phục đúng tên gốc, giữ đoạn mới; bí danh hỏng nằm trong danh sách kèm vị trí sheet/ô hoặc đoạn. Tiền/ngày giữ, bố cục không vỡ, tệp về đúng module; bí danh tạm chưa bị dọn khi tệp ở ngoài |
| 5 | 10 | Module gửi PDF scan DEMO | Core chuyển OCR → Mask (mẫu 1), trả văn bản đã che. OCR chưa nối → ghi "chưa kiểm", không đánh dấu xong |
| 6 | 15 | Mở che (mẫu 3) câu trả lời có bí danh chính thức, bí danh tạm và một bí danh lạ, kèm đúng mã yêu cầu | Hai loại đầu khôi phục đúng; bí danh lạ báo chưa mở đủ kèm vị trí, không đoán |
| 7 | 15 | Admin duyệt một mục, từ chối một mục; mở che lại tài liệu đang xử lý | Mục duyệt có bí danh mới, bí danh cũ sang cột tạm, mở che vẫn đúng; mục từ chối biến mất |
| 8 | 10 | Đóng việc một mã yêu cầu, rồi chạy việc dọn bí danh tạm | Chỉ dọn bí danh tạm không còn mã "đang xử lý" dùng; bí danh của tệp đang ở ngoài được giữ |
| 9 | 10 | Đăng nhập người dùng DEMO B; module DEMO thứ hai gửi mở che bằng mã yêu cầu của A; gửi mở che không kèm mã | Đều bị từ chối; người không phải Admin không xem được bảng, không thấy nút duyệt |
| 10 | 5 | Gửi tệp hỏng, sai định dạng, vượt giới hạn; gửi PDF và yêu cầu nhận lại tệp | Báo lỗi tiếng Việt, không chứa định danh, không cắt ngầm; PDF chỉ trả văn bản |

**Tiêu chí đạt chung:** không sót định danh; tiền/ngày giữ nguyên; không còn tệp gốc trên đĩa; mở che chỉ đúng mã yêu cầu, module và người gửi; tệp về đúng module; ca scan ghi riêng nếu chờ OCR. Lead lưu ảnh chụp và số phút thực tế từng bước.

## 5. Schema — 8 mẫu trao đổi (thay bốn mẫu dự thảo MASK-TT)

Mẫu 1–4 làm ở lát 3, mẫu 5–8 làm ở lát 8. Người gửi và module gửi do Core gắn từ phiên đăng nhập, module không tự khai. Mã yêu cầu cấp ở mẫu 2 hoặc 6 dùng được cho mở che ở mẫu 3 hoặc 7 (ví dụ tệp che xong nhận văn bản thì mở che bằng mẫu 3).

### 5.1 Văn bản

| Mẫu | Thông tin chính | Ghi chú |
|---|---|---|
| **1. Gửi che văn bản** | Văn bản cần che (bắt buộc, không rỗng, ≤500.000 ký tự); định danh đã biết (tùy chọn: giá trị ≤300, nhóm ≤20, ≤500 mục); nguồn văn bản (trực tiếp / từ OCR — Core gắn) | Định danh đã biết chưa có trong bảng → coi là cụm mới, vào danh sách chờ |
| **2. Kết quả che văn bản** | Mã yêu cầu; văn bản đã che; còn sót (phải rỗng); kiểm tiền/ngày giữ nguyên (đạt/không); số chỗ đã thay; bí danh đã dùng (bí danh, nhóm, nguồn: chính thức / tạm); số cụm vừa vào chờ duyệt; cảnh báo (không chứa định danh) | Bỏ: trạng thái danh mục, hạn lượt, cụm gốc mới |
| **3. Gửi mở che văn bản** | Mã yêu cầu (bắt buộc); văn bản có bí danh (≤500.000 ký tự); đóng việc sau khi mở (có/không, mặc định không) | Thay `ket_thuc_luot` bằng "đóng việc" |
| **4. Kết quả mở che văn bản** | Văn bản đã mở che; số chỗ đã mở; bí danh chưa mở được kèm vị trí; trạng thái mã yêu cầu (đang xử lý / đã đóng) | Còn bí danh chưa mở → không công bố là mở đầy đủ |

### 5.2 Tệp

| Mẫu | Thông tin chính | Ghi chú |
|---|---|---|
| **5. Gửi che tệp** | Tệp (docx / xlsx / pdf có lớp chữ; trần dung lượng do lead trình); dạng trả về (văn bản / tệp — tệp chỉ docx, xlsx); định danh đã biết (tùy chọn, như mẫu 1) | PDF chọn "tệp" → báo lỗi rõ hoặc trả văn bản theo cách lead trình; tệp scan/ảnh không đi mẫu này mà Core chuyển OCR → mẫu 1 |
| **6. Kết quả che tệp** | Mã yêu cầu; tệp đã che (cùng định dạng) hoặc văn bản đã che; còn sót (phải rỗng, có vị trí sheet/ô, đoạn, phần ẩn); kiểm tiền/ngày; số chỗ đã thay; bí danh đã dùng; các vùng đã quét (thân, đầu/chân trang, bình luận, lịch sử sửa, thuộc tính, sheet/ô ẩn, nhãn biểu đồ); số cụm vừa vào chờ duyệt; cảnh báo | Không còn tệp gốc trên đĩa sau xử lý |
| **7. Gửi mở che tệp** | Mã yêu cầu (bắt buộc); tệp docx/xlsx có bí danh (có thể đã bị AI sửa); đóng việc sau khi mở (có/không) | |
| **8. Kết quả mở che tệp** | Tệp đã mở che (cùng định dạng); số chỗ đã mở; bí danh chưa mở được kèm vị trí (sheet/ô hoặc đoạn); trạng thái mã yêu cầu | Chỉ trả về đúng module và người gửi |

### 5.3 Thay đổi so với dự thảo MASK-TT

| Dự thảo | Xử lý |
|---|---|
| `ma_luot` | Thay bằng mã yêu cầu do Core cấp và quản lý |
| `danh_muc` (đã mở / chưa có) | Bỏ |
| `het_han_sau_giay`, `luot_con_giu` | Bỏ; thay bằng trạng thái mã yêu cầu |
| `ket_thuc_luot` | Đổi thành "đóng việc sau khi mở" |
| `cum_moi[].cum` (cụm gốc trong phản hồi) | Bỏ khỏi phản hồi; ghi thẳng vào danh sách chờ trong CSDL |
| `cho_duyet.so_cum_vua_them`, `gui_duoc`, `con_sot`, `so_cho_thay`, `bi_danh`, `canh_bao`, `so_cho_mo`, `bi_danh_khong_ro` | Giữ; `bi_danh_khong_ro` thêm vị trí; `bi_danh[].nguon` đổi thành chính thức / tạm |
| Quyền "đúng việc/pháp nhân" | Đổi thành đúng mã yêu cầu + module + người gửi (Core không chia pháp nhân, bí danh chung tập đoàn) |
| "Bảng đối chiếu do Mask giữ trong bộ nhớ" | Bỏ; bảng nằm trong khối riêng CSDL Core |
| "Anh mở/đóng danh mục tại máy chủ", người duyệt là Anh | Bỏ việc mở/đóng; người duyệt là Admin |
| "Không nhận tệp Word/PDF trực tiếp" | Bỏ; tệp đi mẫu 5–8 |

### 5.4 Bảy câu chốt trong tài liệu MASK-TT

| Câu cũ | Trạng thái |
|---|---|
| 1. Duyệt bốn mẫu | Thay bằng 8 mẫu ở mục 5; chuyển sang contract Core có điều kiện — chỉ đăng ký/kích hoạt sau khi đủ kiểm thử |
| 2. Nhóm tên và phiên bản contract | Theo đề xuất trong tài liệu MASK-TT: lead đối chiếu sổ hiện hành, dùng nhóm tên contract Core chính thức, bắt đầu bản 1 cho 8 mẫu, tái dùng contract Core đã có nếu phù hợp — lead trình tên cụ thể trước khi đăng ký |
| 3. Nguồn đi kèm hay cài riêng | Đóng — lõi Mask v2 nội bộ chép vào gói engine; môi trường riêng bỏ có điều kiện |
| 4. Giới hạn kích thước | Theo mục 3, dòng "Giới hạn" |
| 5. Chặn Cloud khi thiếu kiểm | Chốt theo mục 3, dòng "Điều kiện cho đi Cloud" |
| 6. Giữ lượt bao lâu | Đóng — thay bằng mã yêu cầu và quy tắc dọn bí danh tạm |
| 7. Bảo vệ kết quả và câu thông báo | Chốt: chỉ công bố nội dung đã kiểm; cụm gốc, mã yêu cầu, bảng đối chiếu không ra ngoài; thông báo tiếng Việt không chứa định danh. Các câu thông báo trong MASK-TT dùng làm bản nháp, bỏ những câu nhắc danh mục/lượt |