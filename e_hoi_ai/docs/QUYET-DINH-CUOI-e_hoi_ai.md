# QUYẾT ĐỊNH CUỐI — Engine hỏi AI (`e_hoi_ai`)

Ngày chốt: 06/11/2026 · Căn cứ: phiếu `docs/47-core/g3/PHIEU-ENGINE-e_hoi_ai.md` (mốc git `4f180f92`) và thảo luận với Anh trên claude.ai ngày 06/11/2026.
Giờ ghi trong tài liệu này là giờ ước của phiếu, **chưa đo**.

## 1. Phạm vi đồng ý

- **Bản 1 chỉ dùng Local AI.** Cloud để sang bản 2.
- **Engine bản 1 chỉ làm phần lõi:**
  1. Nhận từ module: prompt của function, tài liệu, mã module và mã function.
  2. Ghép phần khung chung: bắt buộc trả lời kèm trích dẫn; tài liệu không có thông tin thì nói "không thấy căn cứ".
  3. Gửi sang Local AI qua cổng chung. Máy Local AI là máy riêng, có GPU, kết nối theo TL 48 §1.2.
  4. Python kiểm trích dẫn.
  5. Trả kết quả về module và ghi nhật ký: module, function, phiên bản prompt, thời gian, kết quả kiểm.
- **Lượt gửi thiếu prompt:** engine từ chối và báo rõ lý do. Không có prompt mặc định chung.
- **Local lỗi** (mất kết nối, model chưa sẵn sàng): báo rõ, cho thử lại. Bản 1 không có Cloud.
- **Prompt thuộc module, không thuộc engine:**
  - Mỗi function có một prompt riêng, khai báo trong gói module, có mã và phiên bản.
  - Module gửi lượt nào thì kéo đúng prompt của function đó.
  - Việc xem và sửa prompt làm trong module: Admin module sửa prompt của module mình; Admin Core sửa được tất cả.
- **Ngoài phạm vi phiếu này:**
  - tạo vector `ai.nhung_vector@1` → phiếu `e_tra_cuu`;
  - hàng chờ và thông báo hàng chờ → chuỗi CE/HC;
  - đóng gói chung → phiếu G3-GOI.
- **Quy tắc khi bật Cloud ở bản 2** (giữ theo TL 48 §1.5–1.6, quyết định ngày 25/10):
  - Có công tắc Cloud riêng cho từng module, mặc định tắt. M9 luôn chỉ dùng Local.
  - Module đã bật Cloud thì tự chuyển sang Cloud khi Local không chạy, khi Local không chắc, và ở các lượt kiểm xác suất.
  - Đo độ chính xác Local theo từng function. Lịch kiểm xác suất: 20% → 10% → 5%, không về 0; tụt dưới 90% thì quay lại 20%.
  - Mọi lượt Cloud phải đi qua Mask.

## 2. Các lát: giữ / bỏ / chuyển / thêm

| Lát | Nội dung | Quyết định |
|---|---|---|
| 1 | AI-KENH — kiểm kênh AI | **Chuyển sang G3-GOI** (là phụ thuộc). Tách **1a** xác minh và **1b** nối thêm (chỉ làm khi 1a thấy thiếu). Mức kiểm N chỉ áp khi 1b đổi quyền hoặc CSDL |
| 2 | G3-GOI-34 — engine trích gọi AI qua SDK | **Chuyển sang G3-GOI** (là phụ thuộc), giữ nội dung |
| 3 | G3-GOI-09 — khóa phiên bản, cài trên máy sạch | **Giữ** |
| 4 | G3 AI-3 — nối Mask | **Sang bản 2** |
| 5 + 9 | Kiểm các ca Mask lỗi bằng Cloud giả | **Gộp làm một lát, sang bản 2** |
| 6 | Tài khoản Windows và khóa API | **Sang bản 2**; cách giữ khóa quyết khi làm bản 2 |
| 7 | Lịch sử/thống kê sau khởi động lại | **Gộp vào bài test cuối** |
| 8 | Thử Local thật | **Giữ.** Chờ Anh kê khai model. Sửa nội dung: Local lỗi thì báo rõ và cho thử lại |
| 10 | Màn Chạy thử DEMO | **Giữ, làm đầu tiên**, làm cùng lúc với back end. Chỉ Admin vào được |
| 11, 12, 13, 15 | Đóng gói và nghiệm thu chung | **Chuyển sang G3-GOI** |
| 14 | Anh thử hỏi–đáp–xem lại qua màn nghiệp vụ | **Giữ**, theo bài test cuối ở mục 5 |
| Thêm | AI-DINH-TUYEN — định tuyến Cloud, đo độ chính xác, kiểm xác suất | **Thêm vào bản 2**, theo A1/A2 |
| Bỏ | AI-PROMPT — quản lý prompt trong engine | **Bỏ**; việc này thuộc module |

## 3. Thứ tự ưu tiên

**Bản 1** (giờ ước theo phiếu: lát 10 = 3 giờ, lát 3 = 2 giờ, lát 8 = 2 giờ, lát 14 = 1 giờ; tổng **8 giờ**, chưa gồm phụ thuộc G3-GOI):
1. Lát 10 — màn Chạy thử DEMO, làm giao diện mẫu song song với các bước 2–3.
2. Phụ thuộc ở G3-GOI: 1a → 1b (nếu cần) → 34.
3. Lát 3 (G3-GOI-09), làm sau 34.
4. Lát 8, khi Anh đã kê khai model.
5. Lát 14 — bài test cuối.

**Bản 2:** AI-3 (sau khi MASK-2 xong) → lát 5+9 → lát 6 → AI-DINH-TUYEN.

Số lát chạy song song do lead quyết khi triển khai. Lead không đứng chờ: lát nào chờ Anh thì chuyển sang làm lát khác.

## 4. Các câu đã chốt

| # | Câu | Anh chốt |
|---|---|---|
| A1 | Có tự chuyển sang Cloud khi Local lỗi không | **Phương án A**: giữ TL 48, thêm công tắc Cloud theo module, mặc định tắt (áp dụng từ bản 2) |
| A2 | Có thêm lát đo độ chính xác Local và kiểm xác suất không | **Có** (bản 2) |
| A3 | Tạo vector để ở phiếu nào | **Để ở `e_tra_cuu`**. Máy Local AI **có GPU** |
| B | Sắp lại cơ cấu lát | **Đồng ý**: đưa lát 10 lên đầu, chuyển 6 lát chung sang G3-GOI, gộp lát 5+9, đưa lát 7 vào bài test cuối |
| L1–3 | Lát 1–3 | **Đồng ý**: tách lát 1 thành 1a/1b; giữ lát 2 và 3 |
| P | Phạm vi bản 1 | **P1**: chỉ Local; Cloud sang bản 2 |
| PR | Cơ chế prompt | **(b)**: module khai báo prompt có mã và phiên bản; **mỗi function một prompt**; engine kéo đúng prompt khi module gửi |
| PR2 | Ai sửa prompt | Admin module sửa prompt của module mình; Admin Core sửa tất cả. **Việc này làm ở module, không ở engine** |
| LM | Máy Local AI | **Máy riêng, có GPU.** Model: Anh kê khai sau |
| DM | Màn Chạy thử DEMO | **Chỉ Admin** |
| TC | Bài test cuối | **Sửa theo P1** (mục 5) |

**Chưa chốt ở phiếu này:** bảy câu về schema Mask (`TOM-TAT-SCHEMA-MASK-CHO-ANH.md`). Các câu này thuộc phiếu Mask.
**Còn chờ Anh:** kê khai model Local AI (cần cho lát 8).

## 5. Bài test tổng thể cuối — khoảng 40 phút (tính lại từ phiếu §4, chưa đo)

**Dữ liệu dùng:** chỉ dữ liệu giả có nhãn DEMO.
- Một function DEMO có khai báo prompt.
- Đoạn hợp đồng GIẢ DEMO: "Công ty DEMO Ánh Dương", hợp đồng "DEMO-001", số tiền **1.000.000 VND**, ngày **30/10/2026**.
- Một câu hỏi mà tài liệu không có đáp án.
- Một function DEMO chưa khai báo prompt.
- Hai pháp nhân DEMO.

**Đường vào:** Quản trị Core → Quản lý engine → Hỏi AI → Chạy thử DEMO (vai Admin).

| Bước | Thao tác | Kết quả cần thấy | Phút |
|---|---|---|---:|
| 1 | Chọn function DEMO, dán đoạn tài liệu giả, hỏi "số tiền và ngày thanh toán là bao nhiêu", bấm Gửi | Trả lời đúng 1.000.000 VND và 30/10/2026, có trích dẫn. Engine dùng đúng prompt của function đó. Nhật ký ghi module, function, phiên bản prompt. **0 lượt Cloud** | 10 |
| 2 | Gửi hai câu liên tiếp, xem Việc của tôi. Hỏi câu tài liệu không có đáp án. Gửi lượt từ function chưa khai báo prompt | Thấy vị trí trong hàng chờ và thời gian ước. Mỗi việc chỉ ghi một lượt. Câu không có đáp án trả "không thấy căn cứ", không bịa. Lượt thiếu prompt bị từ chối, có báo lý do | 10 |
| 3 | Lead tạm tắt Local bằng cấu hình thử; Anh gửi câu hỏi | Báo rõ "không sẵn sàng / thử lại"; **0 lượt Cloud**. Bật lại Local thì gửi lại được | 5 |
| 4 | Mở Lịch sử và thống kê. Lead khởi động lại tiến trình DEMO, Anh tải lại trang. Thử bằng vai thuộc pháp nhân khác | Lịch sử và thống kê vẫn còn. Vai khác pháp nhân không xem được nội dung không thuộc quyền. Nhật ký không lưu nội dung nhạy cảm ngoài quy định | 10 |
| 5 | Ghi kết quả từng ca, ảnh chụp, số phút chờ và chạy | Phân biệt rõ dữ liệu DEMO với phần vận hành thật chưa kiểm | 5 |
| | **Tổng** | | **40** |

**Điều kiện đạt:**
- Không có lỗi mới so với `NEN-TEST.md`; không tăng số bài bỏ qua mà không giải thích.
- Chạy bài test hằng ngày và trước mỗi mốc; ghi riêng số phút test từng lát và số phút test tổng thể.
- PostgreSQL toàn bộ chỉ chạy một lần mỗi đêm.
- Không dùng dữ liệu thật; bản 1 không có lượt Cloud nào.