# Phiếu kế hoạch tổng thể — Trích thông tin hợp đồng theo bộ tham số của module

**Bản lập lại ngày 07/11/2026 theo CD-107, quyết định chốt lúc 20:42.** Bộ tham số thuộc module; Core chỉ điều phối xử lý và giữ tạm kết quả. Phần có hiệu lực là nội dung trước phụ lục; bản 06/11 được giữ nguyên ở cuối để đối chiếu.

**Bổ sung theo CD-111 mục 2/4 từ handoff DOC-CD111:** cập nhật chuỗi chuẩn bị / Hỏi AI / hậu kiểm và đánh giá hỏi lại trường thiếu tại mục 1. Bản chỉ đạo trong worktree chưa có CD-111. Phương án lặp dưới đây chỉ để lead trình Anh, chưa phải chức năng đã duyệt hoặc phần công đã tính trong 53 giờ; không thiết kế đường gọi AI riêng.

| BẢNG TÓM TẮT | Nội dung |
|---|---|
| Kết quả cần đạt | Trong CRM · Hợp đồng & bán hàng, chọn loại hợp đồng, tải Word hoặc bản quét DEMO, nhận bảng thông tin có trích dẫn và ô cần xem lại. Quản trị bộ tham số tại phần quản lý của module: nạp Excel, lịch sử, so sánh, chạy thử, kích hoạt. |
| Quyền sở hữu | Mỗi module giữ bản riêng, kể cả cùng loại hợp đồng; không còn kho bộ tham số ở Core. Admin module quản bộ của mình; Admin Core xem/sửa tất cả qua chức năng của module. Không tạo quyền Kích hoạt riêng ở Core. |
| Loại hợp đồng | Giữ xây dựng 37 tham số làm mặc định chuyển tiếp; loại thứ hai là **thuê đất kèm cơ sở hạ tầng (KCN)**, bộ tham số do **CRM** giữ. M3 dùng lại dữ liệu đã trích, không dùng chung bộ tham số. |
| Phạm vi / giờ còn lại | **16 lát / 53 giờ công ước tính**, gồm phần module, engine, chuyển tiếp và bài cuối. So bản 06/11: giảm 15 giờ trong phiếu do chuyển 24 giờ dùng chung về phiếu chủ trì và tăng ròng 9 giờ công việc trong cùng phạm vi. Chi tiết mục 3. |
| Việc chờ Anh | Chỉ quyết định riêng engine trích tại mục 4. Các quyết định về nơi giữ bộ, quyền quản trị và loại thứ hai đã chốt, không hỏi lại. |
| Nghiệm thu | Giữ E6 so từng byte và Word có Track Changes; N1 chỉ một lần kiểm nhanh. Chia bài cuối vào các buổi 17:00, mỗi buổi phần tham gia của Anh không quá 30 phút; AI/OCR chạy trước. |

Căn cứ: [CD-107](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md), văn bản gốc `docs/47-core/g3/QUYET-DINH-CUOI-e_trich_xuat.md` (đã đọc tại thư mục dự án chính; worktree này chưa có tệp), [phiếu chuỗi engine](PHIEU-ENGINE-chuoi.md), [kế hoạch đóng gói §6.3](KE-HOACH-G3-GOI.md). Mốc đối chiếu mã của worktree: `b5fcd090`. CD-107 và văn bản gốc thắng nội dung cũ khi khác nhau. Đây là phiếu kế hoạch và đánh giá chỉ đọc, chưa phải xác nhận chạy được luồng mới.

## 1. Hợp đồng việc và trách nhiệm

~~**Module gửi tệp + loại hợp đồng + bộ tham số → Core điều phối OCR nếu cần → engine trích → engine Hỏi AI Local → Core trả bảng kết quả về module.** Core điều phối chuỗi theo CD-080; engine trích không tự điều phối OCR hoặc tự tra kho danh mục.~~ **Thay theo CD-111:** module gửi tệp + loại hợp đồng + bộ tham số đã cố định → **Core điều phối OCR nếu cần → Trích chuẩn bị → Hỏi AI Local → Trích hậu kiểm → Core trả bảng kết quả về module**. Bộ điều phối chuỗi là dịch vụ lõi của Core theo CD-110; engine không gọi engine. Word đọc trực tiếp; bản quét đi qua OCR rồi mới trích. Mọi lượt AI qua cổng AI của phần mềm; bước Hỏi AI bản 1 ép Local, không giữ transaction CSDL khi chờ AI, mất kết nối/model lỗi không chuyển Cloud. Hàng 34 trong [kế hoạch đóng gói](KE-HOACH-G3-GOI.md) tách hai bước trích, không còn import `CongAI` trong engine trích.

**Đánh giá nhiều vòng hỏi–đáp AI (CD-111 mục 4):** chưa đủ bằng chứng để kết luận mọi hợp đồng cần nhiều vòng; trước hết hỏi đủ trường đã biết trong một lượt. Có thể cần hỏi lại khi hậu kiểm thấy trường thiếu nhưng nguồn còn căn cứ chưa được lấy. Đề xuất có điều kiện: **bước lặp có giới hạn số vòng do Core điều phối**, chạy Hỏi AI → Trích hậu kiểm cho các trường còn thiếu; engine trích chỉ trả kết quả/nhu cầu hỏi lại. Lead trình Anh giới hạn số vòng, tiêu chí hỏi lại/dừng và ước công; dừng khi đủ trường, không tiến triển hoặc hết số vòng. Thông tin không có trong nguồn phải báo thiếu, không lặp để ép AI bịa. Không tự mở lát mới của phiếu chuỗi khi chưa duyệt lại theo CD-110; không tạo đường gọi AI giữa chừng.

| Bên giữ trách nhiệm | Nội dung phải bảo đảm |
|---|---|
| Module | Giữ loại, nội dung bộ tham số, các bản nháp/bản đang dùng, lịch sử và phê duyệt nghiệp vụ. Gửi một bản đã cố định cho từng việc, kèm nhận diện module, loại, phiên bản và hash. Cập nhật bản đang dùng chỉ ảnh hưởng việc gửi sau đó. |
| Core | Xác minh module, phạm vi quyền và tham chiếu tệp; chuyển nguyên bộ đã gửi qua chuỗi, không tự chọn một bộ khác. Cấp luồng đọc qua SDK cho tệp hợp đồng và bộ tham số; không đưa đường dẫn kho vào việc. Có thể tiếp nhận bản tạm phục vụ việc, không biến bản tạm thành kho phiên bản của Core. |
| Engine trích | ~~Trích đúng bộ được gửi kèm, kiểm nội dung và hash trước khi gọi AI.~~ **Thay theo CD-111:** bước chuẩn bị kiểm nội dung/hash, lập các trường và đầu vào theo bộ được gửi kèm; bước hậu kiểm nhận kết quả Hỏi AI, kiểm trích dẫn/trường thiếu và trả bảng kết quả. Engine trích không gọi AI hoặc tự chạy vòng lặp. Không tự tra danh mục, không tự chọn bản đang dùng, không lấy bộ của module khác. Ngoại lệ duy nhất là bộ xây dựng mặc định chuyển tiếp nêu tại mục 2. |
| Kết quả trả về | Bảng thông tin, trích dẫn/vị trí nguồn, ô cần xem lại; metadata máy đọc ghi đủ **module, loại, phiên bản, hash** để truy vết đúng đầu vào. Việc thiếu bộ hoặc sai hash bị từ chối, không tự dùng bộ xây dựng thay thế. |
| Lưu và dọn | Module tự quyết khi nào ghi vào CSDL của mình. Core giữ tạm tới khi module xác nhận đã lưu hoặc đóng việc, rồi dọn theo cơ chế lưu giữ của phiếu chuỗi. Chưa có xác nhận thì không coi đã lưu; gửi lại xác nhận không gây dọn/lưu hai lần. Không để tham chiếu tệp hay kết quả đang cần trở thành mồ côi. |

Các module dùng cùng loại hợp đồng vẫn có bộ độc lập; không SQL sang schema module khác. Admin Core quản lý qua cửa chức năng có kiểm quyền của từng module, không mở quyền đọc/ghi trực tiếp các bảng module. Màn sử dụng nghiệp vụ không hiện phiên bản bộ tham số, hash, UUID hoặc mã kỹ thuật; lịch sử/so sánh nằm trong phần quản lý bộ tham số theo quyết định gốc. Nhãn tiếng Việt, ngày dd/mm/yyyy, tiền có đơn vị, không xưng hô trên giao diện. Đề xuất đổi nhãn “Import danh mục” thành “Nạp bộ tham số”.

## 2. Chuyển tiếp bộ xây dựng và bộ thuê đất KCN

**Xây dựng:** giữ nguyên bộ 37 tham số làm mặc định trong engine cho tới khi module nhận xong. E6 phải so từng byte giữa đường module gửi bộ và đường mặc định bằng cùng đầu vào/câu trả lời AI giả cố định: nội dung và thứ tự bộ tham số, câu hỏi, bảng kết quả và phản hồi tương ứng trùng; chỉ loại trường thời gian theo quy tắc đã định. Metadata mới về module/phiên bản kiểm riêng, không dùng để miễn sai khác nội dung. Có cả ca Word có Track Changes. Chỉ khi E6 đạt mới chuyển sang bộ module; sau chuyển đưa bộ mặc định vào LUU-TRU, không xóa. Chưa đạt thì giữ mặc định xây dựng, không mở ngoại lệ cho loại khác.

**Thuê đất kèm cơ sở hạ tầng (KCN):** CRM giữ bộ; M3 dùng lại dữ liệu đã trích qua lớp dữ liệu giao tiếp được duyệt. LHD-02b đổi mục tiêu sang soạn bộ tham số **nháp** và bộ hợp đồng DEMO giả kèm đáp án; đề xuất ba mẫu độc lập, có ô trống/điều khoản khác nhau để kiểm. Số tham số và nội dung phải do người nghiệp vụ duyệt trước kích hoạt; không mặc nhiên dùng 30 tham số dịch vụ hay áp quy tắc xây dựng. Lát hiện tại không soạn bộ này hoặc mở hợp đồng thật.

**Đề xuất lưu trữ:** bộ 30 tham số dịch vụ, ba hợp đồng dịch vụ DEMO và đáp án chuyên biệt hết vai trò loại thứ hai. Mục 6 liệt kê nơi tìm thấy và phụ thuộc cần xử lý trước khi lead chuyển LUU-TRU. Không đổi tên dịch vụ thành thuê đất để tái sử dụng nội dung nghiệp vụ; phần helper/test tổng quát vẫn tận dụng.

## 3. Danh sách lát, thứ tự và chênh lệch giờ

Các mã C1–C4 giữ để đối chiếu lịch sử, nhưng nội dung được lập lại theo mô hình module. **T** = test thuần/mock nhanh + review chéo; **N** = T + lead chạy PostgreSQL và review quyền/CSDL khi cần; **M** = lead thử trình duyệt DEMO có ảnh. Worker không chạy/dừng PostgreSQL, server hoặc AI thật. Giờ gồm sửa, tự kiểm và review, chưa gồm chờ AI/OCR hay sửa lỗi phát sinh; là **ước tính**, không phải giờ đã tiêu.

| Thứ tự | Lát / việc cần làm | Phụ thuộc và điều kiện nghiệm thu | Giờ mới | So 06/11 | Kiểm |
|---|---|---|---:|---:|---|
| 1 | LHD-00 — lấy nền đối chiếu, giữ bài Word có Track Changes | Tận dụng LHD-01/02 và số đo còn dùng được; lead giữ cách cấp mẫu được phép. Không dựng lại phép đo lớn TRICH-4b đã hủy. | 3 | 4 → 3, −1 | T + M |
| 2 | LHD-C1 — dữ liệu bộ tham số thuộc từng module | Dùng lại mẫu phiên bản bất biến, hash, chống ghi đè, nhật ký của 108; thiết kế lại khóa/phạm vi theo module. Không phát triển tiếp kho loại chung ở Core. Admin module quản mình, Admin Core quản mọi module qua cửa hợp lệ. | 6 | 3 → 6, +3 | N |
| 3 | LHD-C2 — cửa nạp/kiểm Excel, lịch sử/so sánh/chạy thử/kích hoạt của module | C1, dùng E1 hiện có; cố định bộ gửi theo việc. Phê duyệt nội dung KCN trước kích hoạt; không sinh quyền Kích hoạt riêng ở Core. | 5 | 4 → 5, +1 | N |
| 4 | LHD-02b — bộ tham số nháp + hợp đồng DEMO thuê đất kèm hạ tầng KCN | CRM giữ bộ; người nghiệp vụ duyệt nội dung/đáp án. Chỉ dữ liệu giả. Bản dịch vụ cũ đề xuất lưu trữ, không coi là đầu ra KCN. | 4 | 0 → 4, +4 | T + M |
| 5 | LHD-E2 — nhận bộ từ việc của module | Tận dụng đường đọc Excel qua SDK và kiểm hash đã gộp; thêm kiểm ngữ cảnh module, không tra danh mục ở Core. Giữ đường xây dựng mặc định tới E6. Nhánh đóng gói tiếp tục song song. | 3 | 4 → 3, −1 | T |
| 6 | LHD-E3 — kiểm logic đúng loại | E2, nội dung KCN và quy tắc nghiệp vụ được duyệt. Xây dựng giữ quy tắc cũ; không tự áp cho thuê đất. | 3 | 3 → 3, 0 | T |
| 7 | LHD-E4 — câu hỏi bổ sung của một việc | E2; lựa chọn riêng tại mục 4. Tách câu hỏi thêm khỏi bộ phiên bản, không làm đổi bộ trong module. | 2 | 2 → 2, 0 | T |
| 8 | LHD-E5 — hợp đồng đầu vào/kết quả theo module | C1, E2; trình duyệt phần nghiệp vụ trước đăng ký. Đầu vào tệp + loại + bộ; kết quả đủ module/loại/phiên bản/hash, có xác nhận lưu/đóng việc; giữ tương thích xây dựng chuyển tiếp. | 3 | 2 → 3, +1 | T |
| 9 | LHD-C3 — Core nhận và chuyển bộ cố định, trả kết quả, giữ tạm rồi dọn | C2, E5 và chuỗi CE; không đọc “bản đang dùng” từ kho Core. Kiểm quyền theo module/pháp nhân, không dọn trước xác nhận lưu/đóng; xử lý gửi lại/lỗi bàn giao. Dùng cơ chế chung, không tạo chuỗi riêng. | 4 | 3 → 4, +1 | N |
| 10 | LHD-C4 — nối ba màn đã có vào quản lý của module | C2/C3, bộ DEMO KCN; tận dụng U1a/U1b, thay dữ liệu mô phỏng bằng dữ liệu DEMO thật đã lưu. Có ảnh luồng quản lý và màn nhận kết quả; kiểm cả Admin module/Admin Core và màn người dùng ẩn thông tin kỹ thuật. | 4 | 3 → 4, +1 | T + M |
| 11 | LHD-E6 — cổng so từng byte xây dựng | LHD-00/02, E2–E5; cùng mẫu/cùng AI giả, Word có Track Changes. Chỉ sau cổng đạt mới chuyển bộ xây dựng sang module; không coi test AI giả là số đo chất lượng AI thật. | 4 | 4 → 4, 0 | T |
| 12 | G3-GOI-37 — ghim nguồn, thư viện và tài nguyên chuyển tiếp | G3-GOI-34/36, E6 cho phần chuyển bộ. Giữ bộ 37 mặc định cho tới cổng đạt rồi mới đề xuất lưu trữ; gói độc lập không tự tìm kho Core/repo cũ. Wheel 1.4.1 vẫn chỉ candidate theo §6.3, lát này không đổi SDK/version. | 2 | 2 → 2, 0 | T |
| 13 | LHD-C1-BU — migration bù vô hiệu hóa đường kho Core cũ (đề xuất) | Sau C1/C3/E5 và rà tham chiếu; lead chọn số migration mới khi giao. Giữ nguyên 108 và lịch sử; nội dung mục 6. Không viết/áp migration trong lát phiếu. | 2 | 0 → 2, +2 | N |
| 14 | LHD-N1 — **một lần** kiểm nhanh engine mới | E6, LHD-00 và đường Local đã sẵn. So với nền được chấp nhận; lệch thì ghi/báo, không lặp N1 để chọn kết quả tốt. | 2 | 4 → 2, −2 | T + M |
| 15 | TRICH-READY — bằng chứng đúng phiên bản đang nghiệm thu | N1, E6, G3-GOI-37; cập nhật tham chiếu phép kiểm nhanh thay TRICH-4b, giữ chặn khi thiếu bằng chứng. PG chỉ nếu diff chạm CSDL/quyền. | 2 | 2 → 2, 0 | T; N nếu cần |
| 16 | LHD-N2 — bài cuối chia buổi 17:00 | C4/E5/E6/N1/READY; đóng gói và OCR/Local/chuỗi đủ điều kiện. Lead chạy trước AI/OCR và các ca từ chối; mỗi buổi Anh tham gia ≤ 30 phút, mục 5. | 4 | 4 → 4, 0 | T + M |
| | **Tổng phạm vi phiếu mới** | **16 lát, không ấn định số worker song song** | **53** | | |

Đường chính: C1 → C2 → C3 → C4 → N2; E2 → E3/E4/E5 → E6 → G3-GOI-37 → N1/READY → N2. LHD-02b chạy song song C1, phải có duyệt nghiệp vụ trước kích hoạt; nhánh đóng gói và E6 tiếp tục theo CD-107, không chờ câu hỏi chung. C1-BU chỉ đóng đường cũ sau kiểm phụ thuộc và không chặn việc chuẩn bị mẫu/kiểm thuần. Đây là phụ thuộc nghiệm thu; không suy ra các lát chưa có đã hoàn tất.

**Đối chiếu giờ với bản 06/11/2026:**

| Khoản đối chiếu | Giờ | Ý nghĩa |
|---|---:|---|
| Phạm vi chính cũ | 68 | 49 giờ riêng + 19 giờ dùng chung, 22 lát. |
| Sáu việc chung vốn đã có | −19 | AI-KENH, G3-GOI-34, 13c, 38, 39 và phần cuối 40 về kế hoạch đóng gói/phiếu chủ trì; không tính lặp. |
| Hai việc đóng gói trước tính trong phần riêng | −5 | G3-GOI-35: 3 giờ; G3-GOI-36: 2 giờ. Vẫn tiếp tục, giờ theo phiếu đóng gói hiện hành. |
| Tăng việc trong phiếu | +13 | C1 +3, C2 +1, C3 +1, C4 +1, E5 +1, LHD-02b KCN +4, migration bù +2. |
| Giảm nhờ tận dụng và thu gọn phép kiểm | −4 | LHD-00 −1, E2 −1, N1 −2. |
| **Phiếu mới** | **53** | **68 − 19 − 5 + 13 − 4 = 53; giảm 15 giờ trên phạm vi trình bày.** |

Để so **cùng phạm vi cũ**, nếu tạm giữ nguyên 24 giờ dự toán lịch sử đã chuyển, tổng tương đương **77 giờ, tăng 9 giờ so 68**. Đây không phải cập nhật dự toán của các phiếu chung; lead lấy số hiện hành từ phiếu chủ trì, không cộng lại 24 giờ lần nữa. Bốn lát trích bảng có điều kiện vẫn **+10 giờ** ngoài phạm vi chính, chưa được mở; không bị loại bỏ bởi việc chuyển bộ tham số sang module. Chi tiết cũ ở phụ lục, chỉ triển khai sau quyết định riêng.

## 4. Việc chờ Anh — chỉ quyết định riêng engine trích

| Quyết định riêng còn cần chốt | Đề xuất để xem xét | Giới hạn trước khi chốt |
|---|---|---|
| Duyệt phiếu lập lại và ước giờ | Triển khai theo mô hình module đã chốt; giao từng lát trong phạm vi được duyệt | Không coi việc lập phiếu là cấp phép viết code mới. Nhánh đã được phép tiếp tục theo CD-107 vẫn làm. |
| Quy tắc kiểm logic cho thuê đất KCN | Người nghiệp vụ duyệt bộ nháp và quy tắc của đúng loại; dùng lại bộ kiểm Excel E1 | Không áp logic xây dựng/dịch vụ để lấp chỗ thiếu; chưa duyệt thì chưa kích hoạt. |
| Mức tối thiểu mẫu chạy thử | Đề xuất ba hợp đồng KCN DEMO độc lập, kết quả hoàn tất và đã xem, trước kích hoạt | Mức ba mẫu là đề xuất giữ từ phiếu cũ, không phải quyết định mới của CD-107; duyệt nghiệp vụ vẫn bắt buộc. |
| Hợp đồng nghiệp vụ đầu vào/kết quả E5 | Duyệt cấu trúc nhận bộ từ module, truy vết module/loại/phiên bản/hash và bàn giao kết quả | Không tự đăng ký/kích hoạt cấu trúc nghiệp vụ mới trước duyệt. |
| Cách cấp mẫu cho kiểm nhanh LHD-00/N1 | Lead giữ phép kiểm tại máy đã được phép, worker chỉ dùng DEMO giả; không gọi Word COM | Giữ Word có Track Changes, N1 đúng một lần; thiếu bằng chứng ghi chưa kiểm, không suy là đạt. |
| Câu hỏi thêm của một việc | Đề xuất tối đa năm câu, không sửa bộ tham số đã ghim | Chưa coi giới hạn này là đã được duyệt. |
| Hỏi lại trường thiếu qua nhiều vòng AI (CD-111 mục 4) | Chỉ khi cần, dùng bước lặp có giới hạn số vòng do Core điều phối; lead trình giới hạn, tiêu chí hỏi lại/dừng và ước công | Đề xuất chưa duyệt; chưa cộng vào 53 giờ, không thiết kế operation gọi AI riêng hoặc để engine tự lặp. |
| Có mở nhánh trích bảng hay không | Giữ riêng bốn lát có điều kiện / 10 giờ, xem bằng chứng nguồn rồi duyệt | Không gộp vào 53 giờ hoặc tự mở nhánh. |

Không hỏi lại nơi giữ bộ, ai quản bộ, phạm vi kho chung hay loại thứ hai. Giấy phép OCR, kênh AI, SDK, quyền chuỗi và cổng đóng gói thuộc [phiếu OCR](PHIEU-ENGINE-e_ocr.md), [phiếu Hỏi AI](PHIEU-ENGINE-e_hoi_ai.md), [phiếu chuỗi](PHIEU-ENGINE-chuoi.md) và [kế hoạch đóng gói](KE-HOACH-G3-GOI.md); không giữ trong danh sách chờ của engine trích.

## 5. Bài test cuối — kết quả sẵn, quản lý bộ tham số tại module

**Ước 4 giờ công lead trong LHD-N2**, gồm chuẩn bị/chạy/đối chiếu/ảnh; thời gian chờ AI/OCR ghi riêng. Đề xuất ba buổi lúc **17:00**, ngày cụ thể do lead hẹn; mỗi buổi tối đa **25 phút** tham gia của Anh, luôn dưới trần 30 phút. Không đưa bước chờ xử lý vào thời gian buổi; chưa có kết quả thì lead hoàn tất trước khi mời xem.

Dữ liệu: năm biến thể xây dựng DEMO V0–V4, Word có Track Changes, bộ 37 mặc định và bộ module nhận; bộ tham số KCN nháp đã được người nghiệp vụ duyệt, đề xuất ba hợp đồng KCN DEMO kèm đáp án; Excel lỗi/đúng/bản sửa, Word và PDF cùng nội dung giả. Không dùng bộ dịch vụ làm nghiệm thu KCN. Có hai module giữ bản riêng của cùng loại, hai pháp nhân DEMO, Admin module/Admin Core và người dùng không có quyền quản lý.

| Buổi | Lead hoàn thành trước giờ hẹn | Phần Anh xem/bấm trên giao diện | Thời gian tối đa |
|---|---|---|---:|
| A, 17:00 | Tự chạy trọn đường đăng nhập → CRM → quản lý bộ tham số → về trang chủ; chuẩn bị Excel lỗi/đúng và lịch sử DEMO | Mở quản lý của CRM; nạp bản lỗi, xem dòng/cột/cách sửa; nạp bản đúng, lưu nháp, xem lịch sử/so sánh | 25 phút |
| B, 17:00 | Chạy OCR/Local AI cho bộ mẫu KCN theo bản nháp, có sẵn bảng chạy thử và trích dẫn; kiểm duyệt nội dung và quyền quản lý | Mở kết quả chạy thử sẵn, xem ô cần xem lại, kích hoạt bộ đã được duyệt trong quản lý CRM | 25 phút |
| C, 17:00 | Chạy sẵn xây dựng Word/PDF/Track Changes và KCN, hoàn tất E6/N1, đối chiếu metadata/bàn giao về module | Mở các bảng kết quả sẵn trong CRM, kiểm nội dung/trích dẫn và màn nghiệp vụ ẩn thông tin kỹ thuật | 25 phút |

**Lead tự chạy, không để Anh gánh các ca kiểm kỹ thuật:**

- Quyền: Admin module chỉ quản bộ của mình, Admin Core xem/sửa được mọi module qua cửa hợp lệ, người dùng không có quyền bị từ chối; không có quyền Kích hoạt riêng ở Core. Hai module cùng loại vẫn độc lập; không đọc kết quả khác module/pháp nhân.
- Đầu vào: Excel lỗi không lưu; thiếu bộ, sai loại/hash hoặc lấy tệp ngoài phạm vi bị từ chối trước AI. Bộ đang dùng đổi trong lúc chạy không đổi bản đã gửi. Nháp chưa duyệt nghiệp vụ hoặc chạy thử chưa đạt điều kiện không kích hoạt.
- Bảo toàn: E6 so từng byte hai đường bộ xây dựng; kiểm Word có Track Changes; N1 một lần đối chiếu nền, không lặp. Kết quả giả không thay bằng chứng AI thật.
- Điều phối/lưu giữ: Word bỏ qua OCR, PDF đi qua OCR; trích hỏi qua Hỏi AI Local, bảng về đúng module. Core giữ tạm khi chưa lưu/đóng; xác nhận lưu/đóng xong thì dọn đúng phạm vi, có kiểm gửi lại xác nhận, lỗi bàn giao và không để tệp/kết quả đang dùng mồ côi.
- Giao diện: đăng nhập → ô CRM → quản lý/kết quả → F5 → về trang chủ; kết quả/lịch sử vẫn đúng. Không lộ phiên bản bộ, hash, UUID/mã lỗi thô ở màn sử dụng; tiếng Việt đúng dấu, ngày dd/mm/yyyy, không xưng hô. Lỗi tiếng Việt và Chi tiết hỗ trợ thu gọn theo CD-102.

Lead gửi ảnh trình duyệt thật và biên bản từng ca, ghi phút thao tác/chờ AI/OCR, kết quả E6/N1 và phần chưa kiểm. Kiểm đầu–cuối hằng ngày/trước mốc; PostgreSQL toàn bộ do lead chạy một lần/đêm, chỉ tăng kiểm từng lát khi chạm rủi ro CSDL/quyền. Đạt khi không thêm lỗi so [nền hiện hành v6](../../46-chuyen-doi-dieu-phoi/NEN-TEST.md), không tăng skip không giải thích và đủ bằng chứng luồng mới. Phiếu này chưa chạy bài cuối, AI/OCR thật hay PostgreSQL.

## 6. Đánh giá phần đã gộp (07/11)

### Phạm vi và kết luận chỉ đọc

Đã tìm `danh_muc_trich`, `LHD-C1`, `lhd_c1` trong `src/tests/docs` (máy không có `rg`, dùng `git grep`), mở rộng tìm `trich_danh_muc_`, C2/U1/E1 và đường engine thực tế. Không đọc dữ liệu thật hoặc cấu hình kết nối; không chạy dịch vụ. Dẫn chiếu dưới đây là **tệp:dòng tại `b5fcd090`**, không suy tình trạng CSDL đang chạy từ sự tồn tại của mã.

C1 có migration 108 trong nhánh; nhật ký lead ghi đã gộp, nhưng lát này không kiểm việc áp trên CSDL. E1 và U1a/U1b có mã tận dụng được; ba màn vẫn là mô phỏng trong RAM. **Chưa tìm thấy `core/routes_danh_muc_trich.py`, `tests/test_lhd_c2_routes.py` hoặc nơi gọi các hàm `trich_danh_muc_*` ngoài migration/test C1**, nên chưa có bằng chứng C2 đã gộp trong nhánh này. Các đường trong `ung_dung.py` chỉ phục vụ JavaScript tĩnh, không phải API quản lý bộ thật. Không mở lại/gộp C2 theo hướng kho Core.

### Phần tận dụng được cho module

| Phần | Bằng chứng tệp:dòng | Tận dụng / điều chỉnh cần làm |
|---|---|---|
| E1: kiểm Excel, dòng/cột lỗi, giới hạn tệp, so sánh và mẫu | `src/kho_tri_thuc/sdk_core/danh_muc_tham_so.py:61`, `:116`, `:187`, `:264`, `:321`, `:340`; `tests/test_lhd_e1_danh_muc.py:58` | Giữ bộ kiểm thuần nhận bytes; module gọi để kiểm/nạp/so sánh. Có kiểm macro/ZIP/kiểu ô, hash nội dung và hash tệp. Giữ nguyên byte bộ xây dựng trong thời gian chuyển; nhãn cột cũ “Luôn hỏi Claude” không được dùng để tự mở Cloud hay gọi thẳng nhà cung cấp. |
| Logic phiên bản bất biến/chống trùng | `src/kho_tri_thuc/core/sql/108_danh_muc_trich.sql:127`, `:154`, `:163`, `:286`, `:346`, `:378` | Tận dụng thiết kế bản chỉ ghi thêm, khóa khi ghi, kiểm trùng hash/xung đột, thao tác lặp không tạo bản mới. **Không dùng nguyên bảng Core**: bảng chưa có khóa module, khóa duy nhất hiện chỉ theo engine/nhóm/loại/phiên bản; phải chuyển logic vào vùng dữ liệu module và kiểm quyền tương ứng. |
| Lịch sử/chạy thử/nhật ký | `src/kho_tri_thuc/core/sql/108_danh_muc_trich.sql:238`, `:383`, `:469`, `:553`, `:592`; `tests/test_lhd_c1_danh_muc.py:234` | Giữ nguyên tắc ghi cả từ chối, lịch sử con trỏ, đối chiếu kết quả với việc/engine/pháp nhân và đếm mẫu khác bytes. Đổi nguồn bộ và việc sang module; không bê điều kiện cũ `module='core'` hoặc quyền Core sang module. Mức ba mẫu chờ chốt tại mục 4. |
| U1a: loại + nạp Excel/lịch sử/so sánh | `src/kho_tri_thuc/core/ui/danh_muc_trich_mau.js:63`, `:102`, `:111`, `:152`, `:199` | Tận dụng dựng DOM bằng textContent, bảng lỗi, chọn tệp, xem tham số, lịch sử/so sánh. Đặt tại quản lý module; thay nguồn giả và thông điệp dùng chung toàn hệ thống; xác thực ở máy chủ, không dựa cờ client. |
| U1b: chạy thử + hộp kích hoạt | `src/kho_tri_thuc/core/ui/danh_muc_trich_mau.js:223`, `:267`, `:283`, `:310`; `tests/danh_muc_trich_mau.cjs:1` | Tận dụng bố cục tiến độ, ô cần xem/trích dẫn, xem khác biệt/lý do và hủy thao tác khi đóng màn. Thay tiến độ/kết quả mô phỏng bằng việc DEMO thật, dùng quyền Admin module/Admin Core, kiểm duyệt nghiệp vụ. Không dùng `quyen_kich_hoat` client làm quyền thực. |
| E2 đã nhận bộ Excel qua SDK | `engines/e_trich_xuat/tich_hop.py:698`, `:724`, `:872`, `:883`, `:921`; `tests/test_lhd_e2_loai.py:64` | Tận dụng bộ gửi kèm việc, đọc tệp theo tham chiếu, kiểm hash trước AI, truyền params. E5 bổ sung/kiểm đủ metadata module/phiên bản ở mọi đường trả về: đường nối hiện ánh xạ loại/hash tại dòng 921, chưa đủ để kết luận đã đạt hợp đồng mới. Không tự tra danh mục Core. |
| Bộ 37 và hồi quy DEMO | `engines/e_trich_xuat/tich_hop.py:103`, `:705`; `tests/test_lhd_e1_danh_muc.py:70`; `tests/test_lhd_e2_loai.py:40`; `tests/fixtures/trich_bien_the_xd.py:1` | Giữ mặc định tạm và nền câu hỏi/kết quả. Bằng chứng E2 cũ chưa thay cổng E6 của việc chuyển sang module, đặc biệt khi worktree đang thiếu tệp Excel ghim. |

### Phần không dùng theo hướng cũ — chỉ đề xuất LUU-TRU

| Nội dung / tệp:dòng | Đề xuất cho lead, chưa thực hiện |
|---|---|
| Kho Core và quyền riêng: `src/kho_tri_thuc/core/sql/108_danh_muc_trich.sql:127`, `:176`, `:193`, `:431`, `:623`; kiểm tương ứng `tests/test_lhd_c1_danh_muc.py:76`, `:217` | Ngừng dùng bảng kho chung, ba hành động `CORE:DANH_MUC_TRICH:*`, ràng buộc chỉ Core và seed/con trỏ XD ở Core làm nguồn bộ. Lưu thiết kế/kiểm cũ vào LUU-TRU khi thay xong; tách các mẫu kiểm còn hữu ích. **Riêng tệp SQL 108 phải giữ nguyên tại chuỗi migration**; chỉ lưu thêm bản tư liệu, không chuyển bản duy nhất ra ngoài. |
| Điểm mở màn kho Core: `src/kho_tri_thuc/core/ui/quan_tri.js:30`, `:50`; `src/kho_tri_thuc/core/ui/index.html:106`; `src/kho_tri_thuc/core/ung_dung.py:84` | Sau khi màn quản lý module thay thế, đề xuất lưu trữ đoạn gắn ô Danh mục trích xuất tại Core và các ánh xạ/script chuyên màn cũ. Không chuyển cả `quan_tri.js`, `index.html` hoặc `ung_dung.py` vì còn phục vụ chức năng khác. |
| Dữ liệu/quyền mô phỏng cũ: `src/kho_tri_thuc/core/ui/danh_muc_trich_mau.js:14`, `:22`, `:30`, `:48`, `:59`, `:217`, `:288`; kỳ vọng cũ `tests/danh_muc_trich_mau.cjs:43` | Lưu bộ dữ liệu giả dịch vụ, phiên bản/kết quả tạo sẵn, cờ quyền kích hoạt riêng và kỳ vọng kho toàn hệ thống sau khi tách phần dựng màn tái sử dụng. Không chuyển nguyên UI/test vì còn helper và các ca chống lỗi cần giữ. |
| Bộ 30 dịch vụ + ba hợp đồng DEMO: `tests/fixtures/trich_mau_dv_demo.py:18`, `:113`, `:250`, `:277`; `tests/test_trich_mau_dv_demo.py:28`; `src/kho_tri_thuc/core/ui/danh_muc_trich_mau.js:17`, `:51`; nội dung nháp `docs/47-core/g3/KE-HOACH-LOAI-HOP-DONG.md:348` | Đề xuất chuyển fixture/đáp án và phần tài liệu dịch vụ chuyên biệt sang LUU-TRU, thay nghiệm thu bằng KCN đã duyệt. Chưa tìm thấy một tệp Excel bộ 30 riêng trong danh sách tệp được git theo dõi; không giả định đã có để chuyển. Giữ phần thiết kế chung của kế hoạch loại hợp đồng. |
| Phụ thuộc fixture dịch vụ: `tests/test_lhd_e2_loai.py:28`, `:70`, `:80` | Trước khi chuyển fixture, tách helper tổng quát và thay ca dịch vụ chuyên biệt bằng KCN tương ứng; không làm hỏng import/test. Dữ liệu DV giả trong test bộ kiểm E1 không mặc nhiên là bộ 30 cần bỏ. |
| Khớp tìm kiếm không thuộc lát LHD: `tests/test_e1_mua_trich_phien_ban.py:38` | Đây là test danh mục của luồng mua cũ, không phải route LHD-C2 hay kho 108. Không đề xuất lưu trữ chỉ vì tên hàm có `danh_muc_trich`; tránh làm hỏng chức năng đang chạy. |

Tất cả chuyển LUU-TRU ở đây là **đề xuất**. Lát này không chuyển, không xóa, không sửa mã/test/tài liệu khác. Dừng gộp C1/C2 theo hướng cũ không có nghĩa hoàn tác commit đã gộp hoặc di chuyển migration lịch sử.

### Có cần migration bù không?

**Đề xuất có**, để vô hiệu hóa đường quản lý kho Core cũ và giữ lịch sử trên CSDL đã áp 108; không phải để lấp một số migration bị thiếu. Cần lead chốt sau khi kiểm CSDL DEMO và rà phụ thuộc. Căn cứ:

- `src/kho_tri_thuc/core/doi_cau_truc.py:114`, `:174`, `:178` kiểm thứ tự và mọi checksum lịch sử. Khoảng trống số được phép; chuyển 108 ra ngoài khi đã ghi lịch sử gây `MIGRATION_ORDER`, sửa nội dung 108 gây `MIGRATION_CHANGED`. Không đổi số/đổi hash 108, không chèn số cũ, không sửa sổ để giả như chưa áp.
- `108_danh_muc_trich.sql:137`, `:139`, `:141` có tham chiếu tự thân/người tạo/kiểm toán; `:136` giữ tep_id không có khóa ngoại sang kho tệp; `:163` chặn sửa/xóa dữ liệu. Thu hồi chức năng phải giữ chuỗi lịch sử, tệp liên quan và căn cứ chạy thử, không dọn tệp chỉ vì đã bỏ màn.
- `108_danh_muc_trich.sql:537`, `:617` cấp EXECUTE cho login Core/owner Core; bỏ ô trên màn không tự vô hiệu hóa các hàm SQL. `src/kho_tri_thuc/core/routes_mtq.py:46` và `tests/test_mtq_doc_api.py:96` còn nhãn hiển thị quyền cũ, cần xử lý trong lát chuyển đổi có phạm vi được giao.

**Nội dung đề xuất giao LHD-C1-BU, không viết SQL ở đây:**

1. Lead cấp số mới lớn hơn số cao nhất của nhánh tích hợp tại lúc giao (worktree khảo sát đang tới 125); giữ 108 nguyên byte trong chuỗi. Đọc trạng thái schema/ACL/tham chiếu trên DEMO được phép, không mặc định seed XD là dữ liệu duy nhất.
2. Khi C1/C3/E5 mới đã kiểm đạt, thu hồi đường EXECUTE kho trích cũ khỏi các vai đăng nhập/gọi vận hành, kể cả quyền kế thừa; cô lập cầu nối cũ nếu không còn người dùng hợp lệ. Giữ quyền cần cho việc áp lịch sử 108 và kiểm toán. Chặn các hàm ghi/kích hoạt cũ trong migration mới nếu còn đường gọi; không chỉ ẩn màn.
3. Đánh dấu ngừng dùng ở lớp đăng ký/quyền có sẵn hoặc bằng thay đổi bổ sung phù hợp (lead chốt cách làm); không tạo thêm kho tham số Core. Không xóa dòng MTQ/kiểm toán, không cập nhật cưỡng bức bảng chỉ ghi thêm, không phá các tham chiếu cũ. Bảng/seed 108 giữ như lịch sử bất hoạt, không còn làm nguồn bộ cho việc mới.
4. Lập ánh xạ đầu vào/kết quả/tep_id còn cần sang module chủ sở hữu qua cơ chế công bố và bàn giao hợp lệ. Không tự gán bộ toàn hệ thống cho một module khi chưa rõ chủ, không chép dữ liệu thật vào DEMO. Module chỉ giữ bản riêng; metadata và hash phải kiểm lại; dọn tạm theo xác nhận lưu/đóng, giữ tài liệu lịch sử còn tham chiếu.
5. Lead chạy kiểm migration trên hai trạng thái DEMO: dựng sạch qua toàn chuỗi và nâng bản đã áp 108 (có lịch sử/phiên bản/tham chiếu giả); chạy lại không thay lịch sử, checksum 108 còn nguyên, đường cũ bị chặn, đường module mới hoạt động, không mồ côi tệp hoặc sai quyền. Chưa có bằng chứng này thì chưa coi chuyển đổi xong.

### Kiểm tra đã dùng cho đánh giá

Trước và sau sửa tài liệu, kết quả không đổi: `tests.test_lhd_e1_danh_muc` + `tests.test_lhd_c1_danh_muc.MigrationTinhTests` chạy bằng Python được chỉ định: **48 ca = 46 ok / 0 fail / 1 error / 1 skip**. Error là `test_xd_dung_sha_va_bang_dung_danh_muc_xd` thiếu `src/kho_tri_thuc/m4/review_goc/trich_xuat/DANH_MUC_THAM_SO.xlsx`; skip C1 cũng do thiếu tệp ghim này. Node `tests/danh_muc_trich_mau.cjs`: **16 ok / 0 fail / 0 error / 0 skip**. Đây là kiểm hiện trạng mã cũ, không chứng minh luồng module mới đã có. Không chép thêm fixture ngoài phạm vi; lead cấp lại tệp ghim khi nghiệm thu E6. Không thêm lỗi/skip so lần chạy trước trong worktree; error và skip thiếu tệp ghim là hạn chế môi trường cần ghi riêng khi so nền v6. UTF-8 nghiêm ngặt, không BOM, NFC và `git diff --check` đạt; phụ lục khớp nguyên 21.557 byte bản trước sửa.

## Phụ lục — bản 06/11 (hết hiệu lực theo CD-107)

# Phiếu kế hoạch tổng thể — Trích thông tin hợp đồng, gồm quản lý loại hợp đồng

| BẢNG TÓM TẮT | Nội dung trình Anh |
|---|---|
| Khi xong, Anh thấy và làm được gì | Chọn loại hợp đồng; tải Word hoặc bản quét DEMO; nhận tham số kèm trích dẫn, vị trí và ô cần xem lại. Tự nạp bộ tham số Excel thành phiên bản nháp, chạy thử rồi kích hoạt; biết mỗi kết quả dùng bộ tham số nào. |
| Tổng số lát còn lại | **22 lát cho phạm vi chính**: 16 riêng trích/loại hợp đồng, 6 dùng chung; trong đó LHD-C1/C2/E2 đã được báo đang làm. **4 lát có điều kiện** cho trích bảng, hiện vẫn chờ, chưa đưa vào triển khai chính. |
| Tổng giờ ước còn lại | **68 giờ công phạm vi chính** = 49 giờ riêng + 19 giờ chung; nếu Anh mở thêm trích bảng: **+10 giờ / 4 lát**, tổng **78 giờ / 26 lát**. Đã gồm kiểm và bài cuối; chưa gồm chờ, sửa lỗi phát sinh hoặc công việc của engine khác. |
| Việc chờ Anh | Duyệt phiếu; xác nhận 9 lựa chọn loại hợp đồng; duyệt mẫu trao đổi loại/phiên bản; cách cấp danh mục gốc; phép kiểm trên máy do lead giữ; quyết định tạm về lưu danh mục và quy tắc chuỗi. |
| Cách triển khai | Giữ lõi trích đang chạy; hoàn thiện màn đã có song song phần xử lý. Xây dựng vẫn phải giữ kết quả cũ. Số lát giao đồng thời chốt khi triển khai. |

Ngày đối chiếu **06/11/2026**, mốc git **`4f180f92`**. Căn cứ: [CD-091, gồm sửa 10:02](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md); `CLAUDE.md` mục 0b bản điều phối trong thư mục dự án chính (bản worktree chưa có mục này); [đóng gói §5.2, §6.1–6.5](KE-HOACH-G3-GOI.md); [kế hoạch loại hợp đồng, đặc biệt §6–9](KE-HOACH-LOAI-HOP-DONG.md). Số giờ trong phiếu là **ước tính mới cho phần còn lại**, không quy đổi máy móc số ngày cũ thành giờ đã làm.

## 1. Hiện trạng — phần đã gộp và phần còn thiếu

Đã đối chiếu thực tế bằng `git log --oneline hop-nhat-20261023 --regexp-ignore-case --grep='gộp'`, tương đương lọc chữ “gộp” Anh yêu cầu. Không coi thông điệp “commit” hoặc tài liệu dự kiến là đã gộp. Trạng thái đang làm lấy từ CD-091 cập nhật 10:25 và nhật ký điều phối 10:00; chưa có commit gộp thì vẫn tính phần nghiệm thu còn lại.

| Trạng thái | Nội dung dễ hiểu | Cột phụ: mã / bằng chứng |
|---|---|---|
| Đã gộp | Đọc Word, ánh xạ 37 tham số xây dựng, hỏi qua cổng AI, khung và tích hợp Core | TRICH-1a `3b9ea358`, 4a `75a10106`, 1b `b589bac1`, 3a `34df3076`, 3b `98390d18`, G3-TRICH-NOI `55a42683`. Chưa suy thành sẵn sàng chạy thật. |
| Đã gộp | Gói trích riêng, nguồn Review nội bộ, chuyển bộ đọc sang nguồn đó | G3-GOI-31 `75585712`, 32 `51aab416`, 33 `97846a95`. Mã thuần DEMO trước/sau đã khớp; **đo lại Track Changes vẫn còn nợ** (§6.2). |
| Đã gộp | Công cụ so/chấm chỉ in số; 5 biến thể xây dựng giả; 3 hợp đồng dịch vụ giả | LHD-01 `0a1d7f1a`, 02 `c3604ddd`, 02b `be93c82d`. Chưa phải số đo AI thật. |
| Đã gộp | Đọc/kiểm Excel danh mục và 3 màn góp ý bằng dữ liệu giả | LHD-E1 `90839d31`; LHD-U1a/U1b `20d0e39a`. Màn có nút không chứng minh đã lưu/kích hoạt thật. |
| Đang làm, chưa thấy gộp | Kho phiên bản danh mục, các thao tác quản trị, engine nhận loại/phiên bản | LHD-C1 (108), LHD-C2, LHD-E2. C1 được báo đang review; C2 phải theo thay đổi C1; E2 làm trước 34 nên cần kiểm lại sau khi 34 gộp. |
| Chưa thấy gộp / còn bước đo | Phần loại hợp đồng còn lại | LHD-00, C3/C4, E3–E6, N1/N2; C1/C2/E2 còn phải hoàn tất. Không giao lại 01/02/02b/E1/U1a/U1b. |
| Chưa thấy gộp | Tháo phụ thuộc cổng AI cũ, khung độc lập, hồi quy, khóa phiên bản | G3-GOI-34–37; cổng sẵn sàng TRICH-READY còn phải đối chiếu CD-071. |
| Chưa làm theo phạm vi mới, đang chờ | Trích tham số dạng bảng | TRICH-2a. **TRICH-2b được thay bằng kế hoạch LHD**, không tính thêm lần nữa. |

Đối chiếu đủ 40 lát đóng gói: có gộp **01–08, 10–16, 21–24, 27, 29–33, 40**; **30/40 mới xong phần tài liệu/hiện trạng**. Chưa thấy gộp **09, 17–20, 25–26, 28, 34–39**. Đường kiểm kê 13/13b **đã gộp `df35defc`**, dù tài liệu G3-GOI-40 còn ghi chờ; bật thư mục thật nằm ở **13c/39**, không được coi 13 đã làm xong việc đó.

Chuỗi dùng chung: CE-0 `02cec4bc`, CE-1 `78add174`, CE-9 `a47242fe` đã gộp; **CE-2 vừa gộp `4f180f92`**, cập nhật mới hơn trạng thái đang làm trong CD-091. HC-1/HC-2 chưa thấy gộp. Phiếu này phụ thuộc chúng, không giao lại. Có phép kiểm nhanh trước đây ghi trong chỉ đạo, nhưng chưa có đủ báo cáo theo toàn bộ cách đo LHD-00; vì vậy không tự đánh dấu LHD-00 hoàn tất.

**Phương pháp giữ kết quả cũ:** CD-071 hủy phép đo lớn TRICH-4b, thay bằng kiểm nhanh 2–3 hợp đồng. Cổng ready/tên manifest cũ còn nói “chờ TRICH-4b”; phải cập nhật bằng bằng chứng kiểm nhanh đúng thẩm quyền, không bỏ cổng hoặc dựng lại dự án đo lớn. Tệp `.doc` không đọc trong engine; việc chuyển một lần ngoài engine do lead/Anh giữ, worker không gọi Word COM. Danh mục gốc đang cấp ngoài gói theo quyết định tạm 04 nên chưa thể kết luận gói tự đủ.

## 2. Danh sách đủ mọi lát còn lại

**T** = test thuần nhanh + review chéo Codex. **N** = T + PG đầy đủ + Opus vì sửa CSDL/quyền/tiền/bí mật/xóa. **M** = lead thử giao diện DEMO/máy được phép. Không chạy PG đầy đủ/Opus cho mọi lát thuần chỉ vì kế hoạch cũ từng ghi vậy; diff chạm rủi ro mới nâng N. Kiểm đọc đúng giá trị tiền có sẵn bằng test thuần không đồng nghĩa sửa thuật toán tiền. Tổng thể chạy hằng ngày/trước mốc; PG toàn bộ mỗi đêm một lần.

| Thứ tự | Việc bằng lời dễ hiểu | Phụ thuộc / điều kiện | Giờ còn lại | Kiểm | Cột phụ: mã / phạm vi |
|---|---|---|---:|---|---|
| 1 | Lấy số so sánh gốc và engine; kiểm cả Word có sửa đổi được theo dõi | LHD-01/02 đã gộp; lead cùng model/cấu hình; cách cấp mẫu được Anh xác nhận | 4 | T + M | LHD-00; gồm nợ đo lại §6.2 sau G3-GOI-33; báo số, không chép hồ sơ vào DEMO |
| 2, đang làm | Hoàn thành kho loại, phiên bản và quyền kích hoạt; không mất phiên bản khi nâng engine | LHD-E1 đã gộp; xác nhận lựa chọn Q2/Q4/Q5 và quyết định tạm 07 | 3 | N | LHD-C1, 108; giờ hoàn tất/review còn lại |
| 3, đang làm | Hoàn thành màn gọi chức năng thật: nạp Excel, lịch sử, so sánh, chạy thử, kích hoạt | C1; đồng bộ phương án lưu mới, không dựa vào bản C1 cũ | 4 | N | LHD-C2; kiểm route đã đăng ký và quyền từng thao tác |
| 4, chung | Nối đường AI qua Core nếu kênh chuẩn hiện có chưa đủ | Lead đối chiếu wire; Anh duyệt phần API thiếu nếu có; không tạo cổng riêng | 4 | N | AI-KENH — đề xuất chung, đúng khoảng trống §6 G3-GOI |
| 5, chung | Tháo import cổng AI cũ; chốt SDK cuối có kiểu dữ liệu và cầu nối tương thích | AI-KENH; G3-GOI-05/07/22/33 đã gộp | 4 | T | G3-GOI-34; kiểm wheel/alias, không phát hành candidate 1.4.1 |
| 6 | Nối khung chạy trích vào SDK/OCR đúng nguồn, nhận kết quả rồi mới xác nhận | G3-GOI-18 và 34; kênh AI đã nối | 3 | T | G3-GOI-35 |
| 7, đang làm | Engine nhận đúng loại và phiên bản Excel; xây dựng giữ nguyên câu hỏi cũ | LHD-E1, G3-GOI-31–37 theo kế hoạch gốc; E2 đã làm trước nên hoàn tất nháp rồi kiểm lại sau 35–37 | 4 | T | LHD-E2; chưa kích hoạt thật trước các cổng |
| 8 | Kiểm hồi quy engine và nguồn độc lập, không miễn lỗi bằng cách tắt test | 33–35; phối hợp E2 nếu đã đổi cùng tệp | 2 | T | G3-GOI-36 |
| 9 | Ghim nguồn, thư viện, danh mục xây dựng để gói chạy độc lập | 36, 34; giải quyết cấp catalog đúng SHA và đường @1 không phụ thuộc repo cũ | 2 | T | G3-GOI-37; cập nhật README đã cũ; quyết định tạm 04/05 |
| 10 | Core ghim loại và phiên bản đang dùng; chạy thử được dùng nháp theo quyền | C1, CE-2 và kênh chuỗi liên quan; không tự fallback loại xây dựng | 3 | N | LHD-C3 |
| 11 | Nối ba màn đã góp ý sang dữ liệu thật của DEMO; giữ quyền và thông báo rõ | U1a/U1b đã gộp, C2/C3 | 3 | T + M | LHD-C4; nhãn DEMO vẫn giữ, bỏ nguồn dữ liệu giả trong màn đã nối |
| 12 | Kiểm logic theo đúng loại: xây dựng dùng quy tắc cũ; dịch vụ dùng quy tắc đã chọn | E2, Q3 | 3 | T | LHD-E3; không tự áp quy tắc xây dựng cho mọi loại |
| 13 | Cho thêm tối đa số câu hỏi một lượt đã được Anh chọn, phân biệt với danh mục chính | E2, Q9 | 2 | T | LHD-E4, các tham số Y-xx |
| 14 | Công bố đầu vào có loại và phiên bản; giữ bản cũ cho xây dựng | E2; Anh duyệt mẫu trao đổi C3-4/Q7 | 2 | T | LHD-E5, @2 và yeu_cau_trich.v1; đề xuất chưa được đăng ký trước duyệt |
| 15 | So tự động xây dựng trước/sau bằng cùng câu trả lời AI giả cố định | E2–E4, LHD-02; lead cung cấp bản vàng DEMO ở commit nền | 4 | T | LHD-E6; câu hỏi và kết quả trùng từng byte, bỏ trường thời gian |
| 16 | Lặp kiểm nhanh engine mới; không được giảm chất lượng so nền trước LHD | E6 và LHD-00 | 4 | T + M | LHD-N1; lead chỉ báo số; AI lệch thì lặp một lần, còn lệch dừng báo Anh |
| 17 | Cấp bằng chứng sẵn sàng đúng phiên bản, thay tham chiếu phép đo lớn đã hủy | LHD-00/N1; CD-071; đúng hash/version, giữ chặn khi thiếu bằng chứng | 2 | N | TRICH-READY — hoàn tất cổng còn nợ, không xóa kiểm an toàn |
| 18, chung | Hoàn tất các rào chắn nạp thư mục gói thật và quyền kiểm kê | G3-GOI-11/13/13b đã gộp; bốn điều kiện §6.1, phần nợ §6.5 | 4 | N | G3-GOI-13c; không bật sớm |
| 19, chung | Kiểm năm gói cài độc lập, không đọc repo hoặc engine khác | G3-GOI-09/20/26/30 **đầy đủ**/37 | 3 | T | G3-GOI-38 |
| 20, chung | Nghiệm thu gói, bản ghim, quyền, hiển thị và phiên chạy thực | 13c, 38; các bằng chứng Windows/ready từng engine | 3 | N + M | G3-GOI-39 |
| 21 | Thử trọn: xây dựng như cũ; nạp bộ dịch vụ, chạy ba mẫu, kích hoạt và dùng | C4, E5/E6, N1, READY, 39; LHD-02b; CE/CRM và OCR sẵn sàng | 4 | T + M | LHD-N2; bài cuối mục 4, gồm ảnh và đối chiếu kết quả |
| 22, chung | Chốt hướng dẫn và ảnh thật cuối; sửa trạng thái tài liệu cũ | 39 và các bài nghiệm thu | 1 | T | G3-GOI-40, chỉ phần còn thiếu |
| | **Tổng 22 lát phạm vi chính** | **16 riêng = 49 giờ; 6 chung = 19 giờ** | **68** | | |

E2 đã được giao trước CD-091, được làm nốt; đường làm trước G3-GOI-34–37 **không thay phụ thuộc nghiệm thu**. Không tạo vòng: 36/37 kiểm đường xây dựng đang có; E2 hoàn tất tích hợp sau đó. Nhánh Core 2→3→10→11 chạy song song nhánh đóng gói 4→5→6→8→9. E3/E4/E5 làm sau E2; E6→N1→READY trước nghiệm thu. Chưa mở bất kỳ lát engine mới nào ở bảng này trước khi Anh đồng ý phiếu.

**Phần có điều kiện: đủ bốn lát cho trích bảng, chưa được coi đã duyệt.** Không gộp với đọc bảng Word nội bộ của OCR hoặc tính trùng TRICH-2b.

| Thứ tự sau phạm vi chính | Việc bằng lời dễ hiểu | Phụ thuộc | Giờ | Kiểm | Cột phụ: mã đề xuất |
|---|---|---|---:|---|---|
| B1 | Khóa nguồn có quyền dùng, bộ mẫu giả và mẫu thông tin bảng cần lấy | Anh chọn có làm TRICH-2a; đủ nguồn/test bảo toàn bảng | 3 | T | TRICH-2a-NGUON; nếu không đủ nguồn thì dừng riêng nhánh |
| B2 | Bọc đúng cách trích bảng đã có, giữ ô/hàng/cột/nguồn | B1, OCR giữ cấu trúc; không tự viết thuật toán thay nguồn thiếu | 4 | T | TRICH-2a-BOC |
| B3 | Nối màn xem/so bảng và chỉ công bố năng lực khi mẫu trao đổi được duyệt | B2; Anh duyệt contract mới | 2 | T + M | TRICH-2a-MAN |
| B4 | Thử bảng DEMO đầu–cuối, ô gộp/ô rỗng/số tiền không biến dạng | B3 | 1 | T + M | TRICH-2a-NT |
| | **4 lát có điều kiện** | Chưa tính vào 68 giờ chính | **10** | | |

**Chi phí dùng chung 19 giờ chỉ tính một lần giữa các phiếu**: AI-KENH, G3-GOI-34, 13c, 38, 39, phần cuối 40 là **6 mã**; G3-GOI-34 gồm cùng phần SDK/AI trong cả ba phiếu. Phụ thuộc ngoài phiếu: OCR G3-GOI-17–20 và thử Windows; AI G3-GOI-09 và đường Local; Mask G3-GOI-28/phần nguồn 30; hóa đơn 25–26; chuỗi CE-2/3/4a/4b/5a/5b/6/7, HC-1/2; CRM CR9a; CE-8 là bài phối hợp dùng chung. Giờ của chúng nằm ở phiếu chủ trì, không nằm trong 68 giờ này.

## 3. Việc chờ Anh và đề xuất có thể chọn

| Anh cần chốt | ☑ Đề xuất | Nếu chưa chốt |
|---|---|---|
| Đồng ý phiếu, gồm tách phần trích bảng | ☑ Làm phạm vi chính; giữ trích bảng chờ bằng chứng nguồn và duyệt riêng | Làm nốt lát đã giao; không mở lát engine mới. |
| Q1 — loại sau xây dựng | ☑ Dịch vụ bản gọn, 30 tham số nháp đã có | Chỉ mẫu giả; chưa tự biến bản nháp thành chuẩn nghiệp vụ. |
| Q2 — ai kích hoạt | ☑ Người có quyền Kích hoạt được làm, kể cả người đã nạp; luôn ghi nhật ký | Không tự cấp quyền thật. |
| Q3 — logic loại mới | ☑ Sheet quy tắc tùy chọn, ba kiểu đơn giản trong kế hoạch LHD | Không tự chép quy tắc mua sang dịch vụ. |
| Q4 và Q5 — phạm vi sổ loại / nơi phân quyền | ☑ Dùng chung toàn hệ thống, quản lý ở Quản trị Core → Danh mục trích xuất | Tiếp tục ghi rõ là lựa chọn tạm theo QD-TAM-20261106-02. |
| Q6 — tối thiểu mẫu chạy thử | ☑ Ba hợp đồng hoàn tất hợp lệ trước Kích hoạt | Nút bị chặn khi chưa đủ; không dùng ảnh màn giả làm bằng chứng chạy thử. |
| Q7 / C3-4 — cách engine nhận loại | ☑ Duyệt đầu vào gồm tệp + loại + phiên bản; giữ đường xây dựng cũ trong thời gian chuyển | Contract mới chỉ là đề xuất, chưa đăng ký/kích hoạt trước duyệt. |
| Q8 — cách kiểm nhanh | ☑ Lead kiểm hai hợp đồng có đáp án tại máy và một mẫu giả; chuyển `.doc` một lần ngoài engine theo quy trình đã phép | Worker không mở hợp đồng thật, không gọi Word COM; DEMO chỉ có mẫu giả. Bài này không chép nội dung thật vào phiếu. |
| Q9 — câu hỏi thêm một lượt | ☑ Tối đa năm dòng, người gửi việc thêm; ghi rõ ngoài danh mục | Không làm thay đổi phiên bản danh mục gốc. |
| Cấp danh mục xây dựng, quyết định tạm 04/05 | ☑ Cấp đúng bản gốc đã ghim và có quyền dùng, đóng tài nguyên sạch vào gói hoặc nhận qua SDK/Core; kiểm hash bắt buộc | Không suy đường catalog ngoài repo hiện nay là gói độc lập; lead khóa cách cấp trước 37/38. Việc giữ hai bản helper SDK/vendor cần ghi rõ nguồn, không thêm bản thứ ba. |
| Lưu loại và bản đang dùng, quyết định tạm 07 | ☑ Lưu thành các dòng trong kho phiên bản 108, không để nâng hồ sơ engine làm mất con trỏ | C1/C2 đồng bộ với nhau; quyền kích hoạt vẫn kiểm ở máy chủ. |
| Quy tắc chuỗi tạm 01/06 và màn kiểm kê tạm 03 | ☑ Một dòng chuỗi mở ra bước; lỗi hết lượt thử mới dừng; chạy lại từ bước lỗi; dùng màn kiểm kê theo đường riêng | Chưa coi là đã duyệt chính thức; thay phương án thì lead điều chỉnh phần chung. |
| Giấy phép OCR, phiên Windows, schema Mask | ☑ Xử lý theo phiếu chủ trì; Local AI vẫn là đường bắt buộc, Cloud mặc định tắt | Không chặn thử Word + Local độc lập; chặn nhánh PDF hoặc nghiệm thu đủ năm gói tương ứng. |

Các đề xuất trên xác nhận lại QD-TAM-20261106-01…07 trong [sổ quyết định](../../QUYET-DINH.md), không trình bày lựa chọn tạm thành quyết định Anh đã duyệt.

## 4. Bài test tổng thể cuối qua giao diện DEMO

**Ước 4 giờ** gồm chuẩn bị, chạy và ghi ảnh, nằm trong LHD-N2; có thể dài hơn nếu phải chờ Local AI. Lead mở Core thử được cấp (kế hoạch trước dùng 8796), chỉ chuyển sang 8790 khi đã xử lý vướng Bật CRM và xác nhận sẵn sàng. Các đường bấm sau là **luồng đích cần nghiệm thu**, chưa tuyên bố đang dùng được.

Dữ liệu: dùng **5 biến thể xây dựng DEMO V0–V4** của LHD-02, **3 hợp đồng dịch vụ DEMO** của LHD-02b; bộ Excel dịch vụ 30 tham số **nháp**, bản có lỗi dòng, bản sửa thành phiên bản 2; PDF DEMO tạo từ chính hợp đồng giả để so với Word; một loại chưa có danh mục; hai vai có/không quyền kích hoạt và hai pháp nhân DEMO. Tiền/ngày, tên và mọi đáp án đều giả, có nhãn DEMO. Chạy DEMO không chứng minh danh mục dịch vụ chính xác trên hợp đồng thật.

| Bước | Anh bấm / lead chuẩn bị trên màn | Kết quả cần thấy | Phút |
|---|---|---|---:|
| 1 | Đăng nhập quản trị DEMO → Quản trị Core → Danh mục trích xuất → Loại hợp đồng | Xây dựng giữ 37 tham số; dịch vụ hiển thị nháp/chưa đo thực; lịch sử và bản đang dùng rõ ràng | 15 |
| 2 | Chọn dịch vụ → Tải mẫu → chọn Excel lỗi → Kiểm tra; tiếp tục chọn Excel đúng → Lưu phiên bản nháp | Lỗi chỉ rõ dòng/cột/cách sửa, không cho lưu sai; bản đúng có tóm tắt và khác biệt, chưa đổi bản đang dùng | 25 |
| 3 | Chạy thử nháp với ba hợp đồng dịch vụ DEMO → mở Việc của tôi → mở từng kết quả | Có vị trí chờ, bước đang chạy; bảng tham số theo hợp đồng; ô cần xem có lý do và trích dẫn; chạy chưa đủ thì Kích hoạt chưa dùng được | 60 |
| 4 | Bấm Kích hoạt, đọc khác biệt và nhập lý do; đổi sang vai không có quyền thử lại; nạp phiên bản 2 | Chỉ vai được quyền kích hoạt; có nhật ký; việc đã gửi giữ bản cũ, việc mới dùng bản mới; không ghi đè lịch sử | 30 |
| 5 | Mở CRM · Hợp đồng & bán hàng → tải Word xây dựng DEMO, chọn xây dựng và gửi; chạy thêm PDF cùng nội dung | Word bỏ qua OCR, PDF qua OCR rồi trích; đều dùng cổng AI Local; kết quả có đủ loại/phiên bản/nguồn, ô vàng và trích dẫn; số xây dựng không thấp hơn cổng đo đã được chấp nhận | 45 |
| 6 | Chọn loại chưa có danh mục, thêm năm câu hỏi, thử câu thứ sáu; lead thử sai hash và tài khoản khác pháp nhân | Từ chối đúng lý do; không mượn danh mục xây dựng; chỉ nhận đúng câu hỏi thêm đã khai; không đọc được kết quả khác quyền | 25 |
| 7 | Tải lại trang và mở kết quả cũ; đối chiếu phiên bản, ảnh ba màn và hàng việc; xem Quản lý engine | Kết quả còn truy vết sau tải lại; trạng thái không giả sẵn sàng; có biên bản từng ca, phút chờ/chạy và phần chưa kiểm | 40 |
| | **Tổng** | | **240** |

Bài trọng tâm xây dựng giữ kết quả cũ có E6 kiểm tự động và N1 đo trên máy riêng; không dùng kết quả AI giả thay số đo. Mỗi ngày/trước báo xong chạy bài đầu–cuối trên DEMO và ghi phút; PG toàn bộ chạy ban đêm một lần. Đạt khi không thêm mã lỗi so [nền test](../../46-chuyen-doi-dieu-phoi/NEN-TEST.md), không tăng skip không giải thích, đủ bằng chứng quyền/ready và các ca giao diện trên. **Phiếu này chưa chạy bài cuối, PG, AI hay đọc nội dung hợp đồng thật.**
