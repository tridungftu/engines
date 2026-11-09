7 câu đã chốt theo QUYET-DINH-CUOI-e_mask.md §5.4 (CD-101, 06/11/2026)

# Tóm tắt 8 mẫu trao đổi Mask

**Cập nhật MASK-PHIEU, 06/11/2026.** Áp dụng [quyết định gốc](QUYET-DINH-CUOI-e_mask.md) §3–§5 và [CD-101](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md); văn bản gốc thắng khi khác. Thay nội dung dự thảo MASK-TT trái quyết định; không xin duyệt lại bảy câu. Đây là tài liệu mục tiêu, **chưa xác nhận 8 contract đã đăng ký/kích hoạt hoặc Mask đã chạy thật**. Bốn mẫu trong `engines/e_mask/contract/du_thao.json` vẫn là hiện vật cũ, phải viết lại ở lát 3/8.

“Schema” là mẫu thông tin được gửi/nhận. Engine Mask dùng lõi che và che Word/Excel của Mask file v2 nội bộ; OCR do engine OCR thực hiện, Core điều phối. Bảng định danh–bí danh và cột bí danh tạm nằm trong khối riêng CSDL Core, giới hạn quyền đọc, không mã hóa cột; bí danh chung toàn tập đoàn. Mọi ví dụ dưới đây là **GIẢ — DEMO**. Câu thông báo là bản nháp giao diện, không phải bằng chứng đã triển khai.

## 1. Bảy câu đã chốt

| Câu trước đây chờ duyệt | Đã chốt theo quyết định §5.4 |
|---|---|
| 1. Duyệt bốn mẫu | **ĐÃ THAY:** 8 mẫu §5 quyết định gốc, chuyển thành contract Core có điều kiện. Mẫu 1–4 ở lát 3, mẫu 5–8 ở lát 8; chỉ đăng ký/kích hoạt sau khi đủ kiểm thử. |
| 2. Nhóm tên và phiên bản | **ĐÃ CHỐT CÁCH LÀM:** lead đối chiếu sổ hiện hành, dùng nhóm tên Core chính thức, bắt đầu bản 1, tái dùng contract phù hợp; trình 8 tên cụ thể trước đăng ký. Đề xuất tên ở mục 5 dưới đây. |
| 3. Nguồn đi kèm hay cài riêng | **ĐÃ ĐÓNG:** chép mã lõi Mask v2 nội bộ vào gói, giữ che Word/Excel, tách OCR; chỉ kiểm giấy phép thư viện bên thứ ba. Môi trường riêng bỏ có điều kiện, chỉ xét lại khi lát 1 thấy xung đột. |
| 4. Giới hạn kích thước | **ĐÃ CHỐT:** văn bản ≤500.000 ký tự; định danh đã biết ≤500 mục, giá trị ≤300, nhóm ≤20 ký tự. Trần dung lượng tệp/đầu ra lead trình sau thử DEMO. Vượt trần từ chối, không cắt ngầm. |
| 5. Chặn Cloud khi thiếu kiểm | **ĐÃ THAY ĐIỀU KIỆN:** engine sẵn sàng, không sót, tiền/ngày giữ nguyên đã kiểm thực tế, Mask không lỗi; thiếu một → chặn. Bỏ điều kiện danh mục đang mở. **Mốc này không nối Cloud**; gửi thật thuộc Hỏi AI bản 2. |
| 6. Giữ lượt bao lâu | **ĐÃ ĐÓNG:** bỏ lượt có hạn, thay mã yêu cầu đang xử lý/đã đóng và quy tắc dọn bí danh tạm. |
| 7. Bảo vệ kết quả/thông báo | **ĐÃ CHỐT:** chỉ công bố nội dung đã kiểm; cụm gốc, mã yêu cầu, bảng đối chiếu không ra ngoài phạm vi nội bộ được phép, không lên Cloud. Cụm gốc mới chỉ vào chờ trong CSDL, không phản hồi/nhật ký/contract. Lỗi tiếng Việt không chứa định danh; bỏ câu nhắc danh mục/lượt cũ. |

## 2. Các điểm trái trong MASK-TT đã thay

Các tên trường cũ dưới đây chỉ để đối chiếu lịch sử, **không phải yêu cầu đang áp dụng**.

| Điểm cũ | Nội dung thay thế |
|---|---|
| Bốn mẫu chỉ che/mở văn bản, còn chờ duyệt | **8 mẫu đã chốt về nội dung**: 4 văn bản + 4 tệp; đăng ký/kích hoạt còn có điều kiện kiểm thử. |
| `ma_luot`, quyền đúng việc/pháp nhân | Mã yêu cầu do Core cấp, gắn module + người gửi + tài liệu; mở che kiểm đúng mã + module + người gửi. Không chia bí danh theo pháp nhân. |
| `danh_muc` đã mở/chưa có; mở/đóng danh mục trên máy chủ | **Bỏ** trường và điều kiện này; bảng nằm trong CSDL Core. |
| `het_han_sau_giay`, `luot_con_giu`, mất lượt khi khởi động lại | **Bỏ**; trạng thái mã yêu cầu đang xử lý/đã đóng. Không lấy ví dụ hạn 1.800 giây cũ làm quy tắc. |
| `ket_thuc_luot` | Đổi thành **đóng việc sau khi mở**; văn bản mặc định không đóng. |
| `cum_moi[].cum` và cụm gốc mới trong phản hồi | **Bỏ khỏi phản hồi**, chỉ ghi vào chờ trong CSDL; phản hồi chỉ có số cụm vừa thêm. |
| Bảng đối chiếu giữ trong bộ nhớ Mask, cần khóa/mật khẩu mở | **Bỏ**; khối riêng CSDL Core, giới hạn quyền đọc, không mã hóa cột. Không đưa khóa/mật khẩu vào mẫu trao đổi. |
| Người duyệt là Anh | **Admin** duyệt/từ chối; màn thử DEMO cũng chỉ Admin. |
| Nguồn bí danh: danh mục/đã biết/phát hiện mới | `bi_danh[].nguon` = **chính thức / tạm**. Giữ số chỗ thay, số chỗ mở, cảnh báo, kết luận cho phép gửi và kiểm còn sót; bí danh không rõ thêm vị trí. |
| Không nhận trực tiếp Word/PDF; che tệp là nhánh khảo sát ngoài mốc | Tệp đi mẫu 5–8. Word/Excel có lựa chọn văn bản hoặc tệp; PDF có chữ chỉ văn bản; scan/ảnh Core → OCR → mẫu 1. |
| Không nhận kết quả nếu còn bí danh không rõ | **Trả kết quả kèm danh sách và vị trí**, không đoán và không công bố là đã mở che đầy đủ. |
| Môi trường riêng mặc định, chờ tài khoản Windows/khóa | Bỏ MASK-KHOA/MASK-WIN; **MASK-MOI-TRUONG bỏ có điều kiện**, chỉ quay lại nếu lát 1 thấy xung đột. Khi đó thư viện riêng cho tiến trình Mask, **không nâng thư viện chung Core**. |

## 3. Quy tắc chung và ranh giới bảo mật

- Tên, địa chỉ, MST, tài khoản và các định danh phải được che; tiền/ngày **giữ nguyên giá trị thực tế**, kể cả ô số Excel. MST/tài khoản không được hiểu nhầm là số tiền. Đối tác có mã Junsky dùng `[[<mã Junsky>]]`; định danh khác dùng `[[<tiền tố>-NNNN]]`, không trùng tiền tố Junsky.
- Định danh nghi ngờ vẫn che ngay bằng bí danh tạm và ghi vào danh sách chờ. **Cụm gốc mới chỉ ghi trong CSDL, không vào phản hồi cho module, nhật ký hay contract công bố**. Phản hồi chỉ báo số cụm mới chờ duyệt; không đưa cụm gốc vào cảnh báo/lỗi.
- **Core gắn module/người gửi từ phiên đăng nhập**, module không tự khai. Mã yêu cầu cấp khi trả kết quả che ở mẫu 2 hoặc 6, gắn module + người gửi + tài liệu, không gửi Cloud. Mã cấp từ che tệp nhận văn bản vẫn dùng mở văn bản bằng mẫu 3 được.
- Mở che bắt buộc đúng mã yêu cầu + module + người gửi; mã không tồn tại, thiếu hoặc sai danh tính → từ chối. Tra ngược **toàn bảng chung, gồm bí danh chính thức và cột tạm**; mã dùng kiểm quyền và giữ bí danh tạm, không giới hạn tập tra.
- Nhận diện mở che mềm: không phân biệt hoa/thường, bỏ dấu cách thừa, ghép bí danh bị tách đoạn định dạng Word. Không nhận ra → trả kết quả kèm danh sách và vị trí, không đoán, không báo đã mở đầy đủ. Giữ nội dung AI thêm mới.
- Admin duyệt → cấp bí danh chính thức mới, mã tạm cũ sang cột tạm; từ chối → bỏ khỏi danh sách chờ. Chỉ dọn bí danh tạm khi **không còn mã yêu cầu đang xử lý dùng nó**. Tệp đang ở ngoài AI giữ trạng thái đang xử lý đến mở che xong hoặc module đóng việc.
- Không còn tệp gốc trên đĩa sau xử lý; chỉ trả tệp/kết quả đúng module và người gửi. Bảng riêng hạn chế quyền đọc; người không phải Admin không xem bảng hoặc duyệt.
- **Không nối Cloud trong mốc này**, bước AI sửa tệp do lead giả lập. Khi mở ở Hỏi AI bản 2: chỉ nội dung đã che qua cổng AI chung, đủ các kiểm đã chốt ở mục 1; không kèm mã yêu cầu, cụm gốc, bảng đối chiếu. Local AI luôn theo cổng chung.

**Nguồn và dữ liệu — CD-101 mục 2–4:** chỉ chép **MÃ lõi che + che Word/Excel** từ Mask file v2, tách OCR. **KHÔNG chép/đọc/in/commit danh mục thật, bảng đối chiếu, tệp dữ liệu, khóa, cấu hình bí mật**. Lát tài liệu này không mở thư mục Mask file v2; nếu cần chỉ liệt kê tên `.py`. Chuyển danh mục chỉ thử DEMO, đối chiếu số dòng; chuyển thật làm riêng khi vận hành, Anh xác nhận số dòng trước/sau. Không xóa mã cũ; phần Word/Excel chưa có phải trình sau lát 1, không tự viết thay.

## 4. Nội dung 8 mẫu trao đổi đã chốt

Mẫu 1–4 thuộc **lát 3**, mẫu 5–8 thuộc **lát 8**. Bảng dưới mô tả nội dung nghiệp vụ, không tự công bố tên trường mới hoặc thay schema trong mã. Trần đầu ra và dung lượng tệp chưa có số được chốt; lead trình sau thử DEMO. Không dùng trần đầu vào làm trần đầu ra một cách mặc nhiên.

### Mẫu 1 — Gửi che văn bản

| Thông tin | Yêu cầu và ví dụ GIẢ — DEMO |
|---|---|
| Văn bản cần che | Bắt buộc, không rỗng, ≤500.000 ký tự. Ví dụ: “DEMO Công ty DEMO Ánh Dương thanh toán 1.000.000 VND ngày 30/10/2026”. |
| Định danh đã biết | Tùy chọn, ≤500 mục; giá trị ≤300 ký tự, nhóm ≤20 ký tự. Chưa có trong bảng thì coi là cụm mới và vào chờ, vẫn che ngay. |
| Nguồn văn bản | Trực tiếp / từ OCR, **Core gắn**. Scan/ảnh không để Mask tự nhận dạng. |

### Mẫu 2 — Kết quả che văn bản

| Thông tin | Ý nghĩa và điều kiện |
|---|---|
| Mã yêu cầu | Core cấp và quản lý; ví dụ giả `DEMO_YC_01`, không lên Cloud. Không kế thừa giới hạn 1–64 ký tự của mã lượt cũ nếu chưa chốt schema mới. |
| Văn bản đã che | Đối tác có mã Junsky DEMO, ví dụ `[[KH-DEMO-00123]]`; mã tự sinh ví dụ đề xuất `[[MASKCT-0001]]`. Tiền 1.000.000 VND và ngày 30/10/2026 giữ nguyên. |
| Còn sót và kiểm tiền/ngày | Kết quả đạt yêu cầu có còn sót **rỗng**, tiền/ngày đạt kiểm thực tế. Giữ kết luận cho phép gửi (`gui_duoc`) nhưng không dùng riêng trường này để cấp quyền gửi Cloud. |
| Số chỗ đã thay; bí danh đã dùng | Số chỗ không âm; mỗi bí danh gồm bí danh, nhóm, nguồn **chính thức / tạm**. Số chỗ bằng 0 không chứng minh không còn sót. |
| Số cụm vừa vào chờ; cảnh báo | Chỉ số lượng, không có cụm gốc. Cảnh báo không chứa định danh. Bỏ trạng thái danh mục, hạn lượt và cụm gốc mới khỏi phản hồi. |

### Mẫu 3 — Gửi mở che văn bản

| Thông tin | Yêu cầu |
|---|---|
| Mã yêu cầu | **Bắt buộc**, kiểm đúng module và người gửi từ Core. |
| Văn bản có bí danh | ≤500.000 ký tự; có thể nhận từ luồng che văn bản hoặc che tệp trả văn bản. |
| Đóng việc sau khi mở | Có/không, **mặc định không**. Thay kết thúc lượt cũ; không tự đóng khi tệp/văn bản còn được xử lý. |

### Mẫu 4 — Kết quả mở che văn bản

| Thông tin | Yêu cầu |
|---|---|
| Văn bản đã mở; số chỗ đã mở | Khôi phục từ bảng chung, bảo toàn tiền/ngày. |
| Bí danh chưa mở được + vị trí | Ví dụ giả `[[DEMO_CHUA_RO]]` tại đoạn DEMO 2. Trả cùng kết quả, không đoán; có mục chưa mở thì không công bố đã mở đầy đủ. |
| Trạng thái mã yêu cầu | Đang xử lý / đã đóng; thay trạng thái lượt còn giữ. |

### Mẫu 5 — Gửi che tệp

| Thông tin | Yêu cầu |
|---|---|
| Tệp | `.docx`, `.xlsx`, PDF có lớp chữ; trần dung lượng trình sau thử DEMO. Scan/ảnh Core chuyển OCR → mẫu 1. |
| Dạng trả về | Văn bản / tệp; **tệp chỉ docx/xlsx**. ☑ Đề xuất với PDF chọn nhận tệp: từ chối rõ để chọn lại văn bản, không âm thầm đổi đầu ra. Đây là lựa chọn triển khai cần lead trình theo quyết định §5.2. |
| Định danh đã biết | Tùy chọn, cùng giới hạn mẫu 1. |

### Mẫu 6 — Kết quả che tệp

| Thông tin | Yêu cầu |
|---|---|
| Mã yêu cầu; tệp hoặc văn bản đã che | Tệp cùng định dạng docx/xlsx khi được chọn; PDF chỉ văn bản. Không còn tệp gốc trên đĩa sau xử lý. |
| Còn sót; kiểm tiền/ngày; số chỗ thay | Còn sót phải rỗng khi đạt; kiểm có vị trí sheet/ô, đoạn, phần ẩn; tiền/ngày và ô số Excel giữ nguyên. Không trả cụm gốc qua phản hồi/lỗi. |
| Bí danh đã dùng; số cụm mới chờ; cảnh báo | Như mẫu 2, không kèm bảng đối chiếu hoặc cụm gốc. |
| Các vùng đã quét | **Word:** thân, đầu/chân trang, ghi chú, bình luận, lịch sử sửa, thuộc tính. **Excel:** tên sheet, sheet ẩn, ô ẩn, bình luận, nhãn biểu đồ, thuộc tính. Chưa kiểm vùng nào thì không khẳng định đã che đủ. |

### Mẫu 7 — Gửi mở che tệp

| Thông tin | Yêu cầu |
|---|---|
| Mã yêu cầu | Bắt buộc; kiểm module + người gửi từ Core. |
| Tệp có bí danh | `.docx`/`.xlsx`, có thể đã bị AI sửa; bước AI chỉ giả lập trong mốc này. |
| Đóng việc sau khi mở | Có/không; không tự dọn bí danh của mã yêu cầu còn đang xử lý. |

### Mẫu 8 — Kết quả mở che tệp

| Thông tin | Yêu cầu |
|---|---|
| Tệp đã mở, cùng định dạng; số chỗ mở | Khôi phục mềm theo mục 3; giữ phần AI thêm mới, tiền/ngày và bố cục. Chỉ trả đúng module/người gửi. |
| Bí danh chưa mở + vị trí | Sheet/ô hoặc đoạn; trả tệp kèm danh sách, không đoán, không công bố đã mở đầy đủ. |
| Trạng thái mã yêu cầu | Đang xử lý / đã đóng, dùng cho việc dọn bí danh tạm. |

### Thông báo giao diện dự thảo đã sửa

| Tình huống | Thông báo đề xuất |
|---|---|
| Thiếu/sai mẫu hoặc vượt trần | “Nội dung hoặc tệp chưa hợp lệ hoặc vượt giới hạn cho phép. Vui lòng kiểm tra lại.” Không cắt ngầm. |
| Thiếu/sai mã yêu cầu hoặc khác module/người gửi | “Không xác minh được quyền mở che cho yêu cầu này.” Không đưa định danh, mã kỹ thuật vào lỗi. |
| Engine lỗi, còn sót hoặc tiền/ngày chưa đạt | “Kết quả che chưa đạt kiểm tra an toàn. Cần kiểm tra lại trước khi sử dụng.” |
| Còn bí danh không mở được | “Kết quả còn bí danh chưa mở được. Xem danh sách và vị trí để kiểm tra.” Vẫn trả kết quả đúng quyền, không tự đoán. |
| PDF chọn nhận tệp | ☑ “PDF chỉ hỗ trợ trả văn bản. Vui lòng chọn nhận văn bản.” |

Giao diện dùng tiếng Việt nghiệp vụ, ngày **dd/mm/yyyy**, không xưng hô trong thông báo. Không dùng lại câu lỗi nhắc danh mục mở/khóa, hạn lượt hoặc yêu cầu nhập khóa. Mở che thành công không xác nhận nội dung do AI tạo đúng nghiệp vụ.

## 5. Lead trình Anh sau

**☑ chỉ là đề xuất**, không biểu thị đã được duyệt, đã đăng ký hoặc đã kiểm vận hành. Bảy câu ở mục 1 đã đóng; các đầu việc dưới đây là chi tiết cần trình tiếp.

### Bộ tiền tố bí danh tự sinh

☑ Dành họ **`MASKCT`, `MASKCN`, `MASKDC`, `MASKMST`, `MASKTK`, `MASKKHAC`** lần lượt cho công ty, cá nhân, địa chỉ, MST, tài khoản và định danh khác; dạng `[[<tiền tố>-NNNN]]`, ví dụ giả `[[MASKCT-0001]]`. Đối tác có mã Junsky giữ nguyên mã, chỉ bọc `[[...]]`.

**Chưa xác minh không trùng tiền tố Junsky.** Mã hiện hành khai `tien_to text` theo danh mục động (`src/kho_tri_thuc/ha_tang/pg_migrations.py`, bảng `master.doi_tac_ma_junsky`), không có tập tiền tố cố định để suy từ mã. Lead đối chiếu bộ tiền tố Junsky trước trình/chốt/dùng, phát hiện trùng thì đổi bộ đề xuất; không đổi mã Junsky và không đọc danh mục thật trong lát tài liệu này.

### Tên 8 contract — đề xuất theo sổ hiện hành

Đã đối chiếu **khai báo sổ** `loi.dang_ky_contract` trong `src/kho_tri_thuc/core/sql/005_dang_ky.sql` (mã, phiên bản, trạng thái, bằng chứng duyệt), quy tắc tên ở `core/contract/manifest.json`, contract chung ở `core/contract/ky_thuat.json` và ví dụ `modules/crm/contract/bao_gia.schema.json`. Đây là khảo sát mã tĩnh, **không truy vấn sổ CSDL chạy thực**. Chưa thấy tám tên đề xuất trong các tệp mã/schema đã khảo sát dưới `src/kho_tri_thuc`.

| Mẫu | Tên contract Core đề xuất — ☑ | Lát viết mẫu |
|---|---|---:|
| 1. Gửi che văn bản | ☑ `mask_che_van_ban_vao.v1` | 3 |
| 2. Kết quả che văn bản | ☑ `mask_che_van_ban_ra.v1` | 3 |
| 3. Gửi mở che văn bản | ☑ `mask_mo_che_van_ban_vao.v1` | 3 |
| 4. Kết quả mở che văn bản | ☑ `mask_mo_che_van_ban_ra.v1` | 3 |
| 5. Gửi che tệp | ☑ `mask_che_tep_vao.v1` | 8 |
| 6. Kết quả che tệp | ☑ `mask_che_tep_ra.v1` | 8 |
| 7. Gửi mở che tệp | ☑ `mask_mo_che_tep_vao.v1` | 8 |
| 8. Kết quả mở che tệp | ☑ `mask_mo_che_tep_ra.v1` | 8 |

☑ Bắt đầu **bản 1**, giá trị phiên bản đề xuất `1.0.0`, `$id` dạng `urn:ktt:contract:<tên ở bảng>`. Lead kiểm tên trùng và khả năng tái dùng trong sổ hiện hành, trình Anh tên cụ thể **trước đăng ký**; chỉ đăng ký/kích hoạt ở lát 6 sau khi đủ kiểm thử. Không coi tên dự thảo `urn:ktt:du-thao:e_mask:...` là tên Core đã công bố.

**Điểm trái còn trong mã cần lead xử lý ở lát 6:** `noi_dung_da_che.v1` trong `core/contract/ky_thuat.json` vẫn bắt buộc `luot_che_id`, `het_han_mo_che_luc`, `kiem_tra.danh_muc`. Vì CD-101 bỏ các nghĩa này, không thể tái dùng nguyên trạng hoặc âm thầm đổi nghĩa v1; lead trình cách tương thích/phiên bản. Chỉ tái dùng các phần chung thật sự phù hợp; tài liệu không tự sửa contract, đăng ký hay SDK.

### Trần dung lượng, mức hỗ trợ và giờ công

| Nội dung | ☑ Đề xuất / thời điểm trình |
|---|---|
| Trần dung lượng tệp và đầu ra | ☑ **Sau thử DEMO**: trình số đo kích thước/bộ nhớ/thời gian rồi chốt trần; chưa tự đặt số. Giữ trần đầu vào văn bản/định danh đã chốt; vượt trần từ chối, không cắt ngầm. |
| Mức hỗ trợ Word/Excel | ☑ **Sau lát 1**, kiểm kê từng vùng che và ca mở che mềm theo quyết định §2.2. Phần chưa có trình riêng, không tự viết thay; chưa có bằng chứng thì ghi chưa kiểm/chưa hỗ trợ. |
| Giờ theo 8 lát | ☑ **46–54 giờ công — ước tính**, theo [phiếu engine mục 2](PHIEU-ENGINE-e_mask.md#2-kế-hoạch-đúng-8-lát), cập nhật sau kiểm kê lát 1. |

## 6. Căn cứ và mức kiểm chứng

- [Quyết định cuối e_mask](QUYET-DINH-CUOI-e_mask.md): §2 (8 lát, phần bỏ), §3 (quy tắc), §4 (11 bước/135 phút ước tính), §5 (8 mẫu và 7 câu đã chốt). Đã đọc bản gốc ở thư mục chính vì chưa có trong worktree.
- [CD-101](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md): đã đọc nguyên văn tại thư mục chính; ràng buộc nguồn, bảo mật, trình tên/trần, không nối Cloud.
- [Kế hoạch G3-GOI §6.3](KE-HOACH-G3-GOI.md): **không đổi version SDK**, wheel 1.4.1 chỉ candidate, không phát hành/ghim engine trong lát này.
- [Phiếu 8 lát](PHIEU-ENGINE-e_mask.md): thứ tự 1 → 2 → 3 → 4 → 8 → 6 → 7, lát 5 song song 3–4; bài tổng thể 11 bước qua trình duyệt thật, ảnh + phút thực tế. Scan chưa nối OCR ghi “chưa kiểm”.

Lát MASK-PHIEU chỉ sửa hai tài liệu; không mở thư mục Mask file v2, không đọc dữ liệu/danh mục/khóa/cấu hình thật, không chạy Mask/AI/PG/server, không đăng ký contract và không commit. Kiểm tra thuần trước/sau không thay bằng chứng chạy DEMO của lead.
