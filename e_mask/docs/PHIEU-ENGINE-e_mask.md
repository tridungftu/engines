# Phiếu kế hoạch tổng thể — Che định danh

**Cập nhật 06/11/2026 theo CD-101 và [QUYẾT ĐỊNH CUỐI — Engine Mask](QUYET-DINH-CUOI-e_mask.md). Văn bản gốc thắng khi khác.** Phạm vi và cách triển khai đã chốt; ước giờ, tiền tố bí danh và tên contract dưới đây là đề xuất để lead trình, không phải kết quả đã nghiệm thu.

| BẢNG TÓM TẮT | Nội dung |
|---|---|
| Khi xong, người dùng làm được | Module gửi văn bản/tệp qua API Core, nhận bản đã che kèm mã yêu cầu; mở che trả đúng module và người gửi. Admin thử DEMO và duyệt định danh mới. Tiền/ngày giữ nguyên. |
| Đầu ra | Mặc định văn bản; Word (.docx)/Excel (.xlsx) được chọn nhận tệp cùng định dạng khi che và mở che. PDF chỉ trả văn bản; scan/ảnh do Core điều phối OCR → Mask. |
| Tổng lát | **8 lát**, thứ tự **1 → 2 → 3 → 4 → 8 → 6 → 7**; lát **5 song song lát 3–4**. |
| Giờ công còn lại — ước tính | **46–54 giờ**, gồm test thuần, review, chuẩn bị DEMO và lần chạy bài tổng thể đầu tiên. Chưa gồm chờ, sửa lỗi chưa biết, phần Word/Excel chưa có phải trình thêm và các việc chung được tính ở phiếu chuỗi. |
| Mốc thực hiện | Song song Hỏi AI bản 1, sau ưu tiên CD-099 của lead; **không nối Cloud**, bước “AI sửa tệp” do lead giả lập. Cloud thật thuộc Hỏi AI bản 2. |
| Trạng thái | Phiếu đã sửa theo quyết định; chưa xác nhận lõi nguồn thật, chuyển danh mục, 8 contract hoặc bài DEMO đã hoàn tất. Không xin duyệt lại 7 câu đã chốt. |

## 1. Căn cứ, kiến trúc và phạm vi

Căn cứ: [CD-101](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md), quyết định gốc §1–§5, [bản tóm tắt 8 mẫu](TOM-TAT-SCHEMA-MASK-CHO-ANH.md) và [kế hoạch G3-GOI §6.3](KE-HOACH-G3-GOI.md). Khi khảo sát lát MASK-PHIEU, CD-101 và quyết định gốc chưa có trong worktree; đã đọc nguyên văn tại `docs/` của thư mục chính, không chép thêm tệp vào worktree.

Engine = **lõi Mask file v2 nội bộ + API**, tận dụng mã đã có, tách OCR sang `e_ocr`. Bảng định danh–bí danh, cột bí danh tạm và bảng mã yêu cầu nằm trong **khối dữ liệu riêng CSDL Core**, tên tiếng Việt không dấu, giới hạn quyền đọc, **không mã hóa cột**. Bí danh dùng chung toàn tập đoàn; bảng đối chiếu không còn nằm trong bộ nhớ Mask. Không dùng mô hình “mở/khóa danh mục tại máy chủ” để cấp quyền hoặc chặn xử lý.

Luồng thống nhất:

1. Core xác minh phiên, gắn module/người gửi/tài liệu và cấp mã yêu cầu khi che; module không tự khai danh tính. Đối tác có mã Junsky dùng `[[<mã Junsky>]]`, định danh khác dùng `[[<tiền tố>-NNNN]]`.
2. Định danh nghi ngờ được **che ngay bằng bí danh tạm**, đồng thời ghi vào danh sách chờ trong CSDL. Module chỉ nhận số cụm mới chờ duyệt, không nhận cụm gốc.
3. Admin duyệt → cấp bí danh chính thức mới (mã Junsky nếu có), bí danh tạm cũ sang cột tạm. Từ chối → bỏ mục khỏi danh sách chờ. Mở che tra bảng chung, gồm bí danh chính thức và cột tạm; mã yêu cầu kiểm quyền và giữ bí danh tạm, **không giới hạn bảng tra**.
4. Mở che bắt buộc đúng mã yêu cầu + module + người gửi. Mã có trạng thái **đang xử lý / đã đóng**, thay lượt có hạn. Chỉ dọn bí danh tạm khi không còn mã yêu cầu đang xử lý dùng nó. Tệp gửi ra AI tiếp tục đang xử lý đến khi mở che xong hoặc module đóng việc.

Bốn mẫu nháp và khung vòng đời cũ đã có trong mã chỉ là nền tái sử dụng; các điều kiện trái quyết định phải sửa ở các lát tiếp theo. Tài liệu này không đổi mã, SDK hay đăng ký contract.

## 2. Kế hoạch đúng 8 lát

**Giờ đều là ước tính**, chưa phải số đo hoặc cam kết ngày xong. Lát 8 có khoảng giờ vì chưa kiểm kê mức hỗ trợ Word/Excel; sau lát 1 phải cập nhật ước tính, phần chưa có trình lại, không tự viết thay. Lead quyết số worker song song khi triển khai; từng handoff vẫn phải khóa danh sách tệp.

**Loại kiểm:** T = test thuần/mock bằng dữ liệu DEMO + review chéo. N = T và kiểm PostgreSQL/quyền liên quan do lead chạy, review theo cổng dự án. M = lead bấm trình duyệt thật, lưu ảnh và phút thực tế. Worker không khởi động/dừng PG hay server. Không chạy PG toàn bộ cho từng lát; bộ đầy đủ do lead xếp một lần/đêm.

| Thứ tự | Lát | Nội dung và tiêu chí chính | Phụ thuộc | Giờ — ước tính | Kiểm |
|---|---:|---|---|---:|---|
| 1 | 1 | Chỉ lấy **mã lõi che + che Word/Excel** từ Mask file v2 vào gói engine; **tách OCR**, không còn code/chỗ gọi OCR trong Mask. Kiểm kê phụ thuộc gồm cryptography; chỉ kiểm giấy phép thư viện bên thứ ba; báo đúng khả năng Word/Excel hiện có, thiếu thì trình. Không xóa mã cũ. | Mở sau phiếu; lead khóa tập mã sạch | 6 | T; kiểm nguồn/phụ thuộc, không chạy dịch vụ |
| 2 | 2 | Bảng định danh–bí danh + cột tạm + bảng mã yêu cầu trong khối riêng Core; quyền đọc hạn chế, không mã hóa cột. Quy tắc mã Junsky/mã tự sinh không trùng tiền tố; công cụ chuyển danh mục **chỉ DEMO**, đối chiếu số dòng trước/sau. Xác nhận khả năng giữ mã Junsky bằng mẫu DEMO. | 1; tiền tố cụ thể trình trước dùng | 6 | N — CSDL, quyền và định danh |
| 3 | 3 | API che/mở che văn bản, **mẫu 1–4** của quyết định §5; nhận văn bản trực tiếp hoặc do OCR trả. Không sót định danh, tiền/ngày giữ nguyên; sai/thiếu mã yêu cầu hoặc khác module/người gửi → từ chối. Lỗi tiếng Việt không chứa định danh, vượt trần không cắt ngầm; không còn tệp gốc trên đĩa nếu có trung gian. | 2 | 6 | N — quyền, dữ liệu nhạy cảm, tiền/ngày |
| 4 | 4 | Danh sách chờ + màn duyệt **chỉ Admin**, lọc kiểu Excel; duyệt/từ chối và dọn bí danh tạm. Duyệt cấp bí danh mới, giữ mã tạm cũ; việc dọn bỏ qua mọi mã yêu cầu còn đang xử lý dùng bí danh đó. | 3; giao diện làm cùng back end | 5 | N + M — quyền duyệt, vòng đời mã yêu cầu |
| 5 | 8 | API che/mở che tệp, **mẫu 5–8**; Word/Excel chọn nhận tệp hoặc văn bản, PDF có lớp chữ chỉ văn bản. Quét đủ vùng ẩn, giữ tiền/ngày và bố cục; mở che mềm sau AI sửa; bí danh không nhận ra trả danh sách + vị trí, không đoán. Xem tiêu chí dưới bảng. | 2, 3; triển khai sau 4 theo thứ tự đã chốt | 12–20 | N + M — tệp, quyền, định danh, số liệu |
| 6 | 6 | Công bố Mask và đóng gói: **G3-GOI-28 + phần còn nợ của 30**, đăng ký 8 contract sau khi tên được trình và đủ kiểm thử. Chỉ công bố năng lực đã kiểm; xử lý tương thích contract cũ trước kích hoạt. | 3, 4, 8; màn 5 sẵn sàng | 4 | N — contract/quyền; test gói độc lập |
| 7 | 7 | Bài tổng thể **11 bước, 135 phút ước tính** theo quyết định §4; trình duyệt thật, ảnh và phút thực tế từng bước. Ca scan chưa nối OCR ghi “chưa kiểm”. | 5, 6 và các lát áp dụng; scan phụ thuộc chuỗi OCR | 3 | N + M; gồm chuẩn bị/tổng hợp ngoài 135 phút bấm |
| Song song 3–4 | 5 | Màn thử che/mở che **DEMO, chỉ Admin**, gồm văn bản và tệp. Có bản dữ liệu giả ghi nhãn rõ cùng back end; nối văn bản sau 3, danh sách chờ sau 4, thử tệp thật sau 8. | Dựng màn mẫu cùng 3–4; không chờ 8 mới làm giao diện | 4 | T + M; kiểm quyền Admin phía máy chủ |
| | | **Tổng 8 lát — ước tính** | | **46–54** | |

**Nguồn lát 1 — ranh giới bắt buộc của CD-101 mục 2:** chỉ chép **MÃ** lõi che và che Word/Excel; tách OCR. **KHÔNG chép/đọc/in/commit danh mục thật, bảng đối chiếu, tệp dữ liệu, khóa, cấu hình bí mật** trong Mask file v2. Trong lát tài liệu này không mở thư mục Mask file v2; nếu cần kiểm kê chỉ được liệt kê tên tệp mã nguồn `.py`. Lát lấy nguồn tiếp theo phải có handoff riêng, chỉ định rõ tệp mã được phép; không coi phiếu là quyền mở dữ liệu. Không xóa mã cũ, không tự bổ sung thuật toán thay phần nguồn chưa hỗ trợ.

**Tiêu chí lát 8 theo quyết định §2.2:**

- Khi che Word: kiểm thân, đầu/chân trang, ghi chú, bình luận, lịch sử sửa, thuộc tính tệp. Khi che Excel: tên sheet, sheet ẩn, ô ẩn, bình luận, nhãn biểu đồ, thuộc tính tệp. Không sót định danh ở các vùng này.
- Khi mở che sau AI sửa: nhận bí danh đổi hoa/thường, có dấu cách thừa, bị tách thành nhiều đoạn định dạng Word; giữ nội dung AI thêm mới. Bí danh không nhận ra → trả kết quả kèm danh sách và vị trí sheet/ô hoặc đoạn, không đoán, không công bố là đã mở đầy đủ.
- Tiền/ngày, kể cả ô số Excel, giữ nguyên; bố cục không vỡ; không còn tệp gốc trên đĩa; kết quả chỉ về đúng module và người gửi.

**Phụ thuộc dùng chung, không cộng trùng vào 46–54 giờ:** cổng/SDK, kiểm gói chung G3-GOI-38, quản lý engine 39, tài liệu/ảnh chung 40 và cửa nạp gói thật 13c theo [phiếu chuỗi](PHIEU-ENGINE-chuoi.md). Phần riêng Mask của 28/30 đã tính tại lát 6. **Không đổi version SDK; wheel 1.4.1 chỉ candidate theo G3-GOI §6.3, không phát hành/ghim engine vào candidate.** Không buộc Mask mốc này chờ nối Cloud.

## 3. Các lát và điều kiện cũ đã bỏ/thay

| Nội dung cũ | Quyết định áp dụng; không còn là việc chờ duyệt |
|---|---|
| MASK-KHOA | **Bỏ**; bảng không mã hóa cột, không còn khóa danh mục cần chuyển qua bộ nhớ. |
| MASK-WIN | **Bỏ**; tiêu chí không còn tệp gốc trên đĩa nằm trong lát 3/8. |
| MASK-3-TK, MASK-3 — phát hiện riêng | **Bỏ**; dò định danh nằm trong bước che + danh sách chờ. |
| Lượt có hạn, mã lượt, hết hạn, mất lượt sau khởi động lại | **Bỏ**; thay bằng mã yêu cầu và quy tắc dọn bí danh tạm. |
| MASK-4-TK, MASK-4 | **Thay bằng lát 8**; chỉ dựng lại Word/Excel, PDF chỉ văn bản. |
| MASK-HOP-DONG — bốn mẫu dự thảo | **Viết lại thành 8 mẫu §5**: mẫu 1–4 tại lát 3, mẫu 5–8 tại lát 8. |
| MASK-MOI-TRUONG | **Bỏ có điều kiện**: chỉ quay lại nếu kiểm kê lát 1 thấy xung đột thư viện; khi đó thư viện riêng cho tiến trình Mask, **KHÔNG nâng thư viện chung Core**. Chưa cộng giờ phát sinh vì chưa xác minh xung đột. |

## 4. Bảo mật bắt buộc — CD-101 mục 4

- Cụm gốc mới phát hiện chỉ ghi vào danh sách chờ trong CSDL; **không vào phản hồi, nhật ký, contract công bố**. Phản hồi chỉ báo số cụm mới chờ duyệt.
- Mở che bắt buộc mã yêu cầu hợp lệ + đúng module + đúng người gửi, do Core xác minh; biết mã không thay quyền. Không gửi mã yêu cầu hoặc bảng đối chiếu cho Cloud. Bảng riêng Core hạn chế quyền đọc; người không phải Admin không xem bảng/duyệt.
- Thông báo lỗi bằng tiếng Việt nghiệp vụ, không chứa định danh hoặc mã kỹ thuật; ngày hiển thị dd/mm/yyyy, không xưng hô trong thông báo. Vượt trần → từ chối, **không cắt ngầm**.
- Không còn tệp gốc trên đĩa sau xử lý. Không dùng hồ sơ thật, kho thật, danh mục thật, khóa hoặc cấu hình bí mật làm fixture/test. Chuyển danh mục thật là việc riêng khi vận hành, Anh xác nhận số dòng trước/sau; công cụ của lát 2 chỉ chạy DEMO trong đợt này.
- **Mốc này không nối Cloud**, kể cả khi che thành công; lead giả lập bước AI sửa tệp. Khi Hỏi AI bản 2 mở Cloud: chỉ nội dung đã che đi qua cổng AI chung, engine sẵn sàng, không còn sót, tiền/ngày đã kiểm thực tế giữ nguyên, Mask không lỗi. Thiếu một điều kiện → chặn; bỏ điều kiện “danh mục đang mở”. Đường Local AI vẫn theo cổng chung.

## 5. Lead trình Anh sau

Dấu **☑ là đề xuất**, chưa phải đã duyệt/đăng ký. Bảy câu schema đã chốt, không đưa lại thành câu hỏi mở.

| Nội dung cần trình | ☑ Đề xuất và thời điểm |
|---|---|
| Bộ tiền tố bí danh tự sinh, không trùng tiền tố Junsky | ☑ Dành họ `MASKCT` (công ty), `MASKCN` (cá nhân), `MASKDC` (địa chỉ), `MASKMST` (mã số thuế), `MASKTK` (tài khoản), `MASKKHAC` (khác); ví dụ DEMO `[[MASKCT-0001]]`. Giữ nguyên mã Junsky cho đối tác có mã. **Chỉ đề xuất, chưa xác minh không trùng**: mã nguồn lưu tiền tố theo danh mục động, không có tập tiền tố cố định. Lead đối chiếu trước chốt/dùng; trùng thì đổi bộ đề xuất, không đổi mã Junsky. Không đọc danh mục thật trong lát này. |
| Tên 8 contract | ☑ Dùng nhóm `mask_...v1`, bản `1.0.0`, theo bảng 8 tên cụ thể trong [tóm tắt schema, mục 5](TOM-TAT-SCHEMA-MASK-CHO-ANH.md#5-lead-trình-anh-sau). Đã khảo sát `loi.dang_ky_contract` và contract trong `src/kho_tri_thuc/**/contract`; mới là đối chiếu mã tĩnh, lead trình tên và kiểm sổ chạy thực trước đăng ký. |
| Trần dung lượng tệp và đầu ra | ☑ Trình **sau thử DEMO**, có số đo bộ nhớ/thời gian và kích thước; chưa tự đặt số. Trước đó giữ trần văn bản 500.000 ký tự, định danh ≤500 mục, giá trị ≤300 ký tự, nhóm ≤20 ký tự; vượt trần từ chối. |
| Mức hỗ trợ Word/Excel | ☑ Trình **sau lát 1**, theo từng vùng nêu ở §2.2 quyết định gốc. Chưa có bằng chứng thì ghi chưa kiểm/chưa hỗ trợ; phần chưa có không tự viết thay. |
| Giờ theo 8 lát | ☑ **46–54 giờ công — ước tính**, chi tiết mục 2; cập nhật sau kiểm kê lát 1, không coi là lịch cam kết. |

**Điểm tương thích cần lead chốt ở lát 6:** `src/kho_tri_thuc/core/contract/ky_thuat.json` hiện vẫn yêu cầu `luot_che_id`, `het_han_mo_che_luc`, `kiem_tra.danh_muc` trong `noi_dung_da_che.v1`. Không thể tái dùng nguyên trạng cho CD-101; không âm thầm sửa nghĩa bản đã công bố hoặc tạo dữ liệu giả về hạn lượt để vượt bộ kiểm. Lead trình cách tương thích/phiên bản trước đăng ký; lát tài liệu này chỉ ghi nhận, không sửa contract/Core.

## 6. Bài test tổng thể cuối — 11 bước, ước tính 135 phút, chưa chạy

Theo **quyết định gốc §4**; giữ số bước gốc **1, 2, 3, 4, 4b, 5, 6, 7, 8, 9, 10** (tổng 11). Lead chuẩn bị Admin DEMO, người dùng DEMO A/B, hai module DEMO, danh mục DEMO đã chuyển vào CSDL, một đối tác có mã Junsky DEMO, Word/Excel/PDF có chữ/PDF scan đều ghi “Dữ liệu giả — DEMO”. Không kết nối Junsky/Cloud thật. Lead chạy bằng **trình duyệt thật**, ảnh và phút thực tế từng bước; worker không chạy PG/server.

| Bước | Phút — ước tính | Thao tác | Kết quả phải thấy |
|---|---:|---|---|
| 1 | 10 | Quản trị Core → Quản lý engine → Che định danh | Engine sẵn sàng, lõi không kèm OCR, số dòng danh mục DEMO khớp, đúng 8 mẫu. |
| 2 | 15 | Admin thử văn bản DEMO có đối tác mã Junsky DEMO, công ty khác, MST, địa chỉ, 1.000.000 VND và 30/10/2026 | Mã Junsky bọc `[[...]]`, mã tự sinh cho định danh khác; tiền/ngày giữ nguyên, có mã yêu cầu. |
| 3 | 15 | Thêm tên lạ chưa có trong bảng | Che bằng bí danh tạm và vào chờ; phản hồi chỉ có số cụm chờ, không cụm gốc. |
| 4 | 15 | Module gửi Word/PDF có chữ, mẫu 5, chọn văn bản | Văn bản đã che không sót, không còn tệp gốc trên đĩa. |
| 4b | 15 | Word/Excel có định danh ở đầu trang, bình luận, sheet ẩn, thuộc tính; chọn tệp. Lead giả lập AI thêm đoạn, đổi hoa/thường, tách bí danh và làm hỏng một bí danh; mở bằng mẫu 7 | Che đủ vùng; mở đúng tên, giữ nội dung mới; bí danh hỏng kèm vị trí, không đoán. Tiền/ngày và bố cục giữ; trả đúng module/người; chưa dọn bí danh tạm khi tệp còn ở ngoài. |
| 5 | 10 | Module gửi PDF scan DEMO | Core điều phối OCR → mẫu 1 → văn bản đã che; OCR chưa nối thì ghi **“chưa kiểm”**, không đánh dấu xong ca scan. |
| 6 | 15 | Mẫu 3 với bí danh chính thức, tạm và lạ, đúng mã yêu cầu | Hai loại đầu khôi phục; loại lạ báo chưa mở đủ và vị trí. |
| 7 | 15 | Admin duyệt một mục, từ chối một mục; mở lại tài liệu đang xử lý | Cấp bí danh mới, giữ bí danh cũ ở cột tạm, mở vẫn đúng; mục từ chối không còn trong chờ. |
| 8 | 10 | Đóng một mã yêu cầu, chạy dọn bí danh tạm | Chỉ dọn khi không còn mã đang xử lý dùng; giữ bí danh của tệp đang ở ngoài. |
| 9 | 10 | DEMO B hoặc module thứ hai dùng mã của A; thử thiếu mã | Đều từ chối. Người không phải Admin không xem bảng/không thấy nút duyệt. |
| 10 | 5 | Tệp hỏng, sai định dạng, vượt trần; PDF chọn đầu ra tệp | Lỗi tiếng Việt không chứa định danh, không cắt ngầm; PDF chỉ hỗ trợ đầu ra văn bản. |
| | **135** | **Tổng 11 bước — ước tính** | Chỉ DEMO; lưu ảnh và phút thực tế. |

Chỉ báo hoàn tất các năng lực có bằng chứng đạt; scan chưa nối chuỗi ghi riêng. Lát MASK-PHIEU chỉ sửa hai tài liệu, không thực hiện bài vận hành này, không mở Mask file v2 hoặc dữ liệu thật, không đổi SDK, không commit.
