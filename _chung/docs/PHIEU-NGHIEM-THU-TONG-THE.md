# Phiếu nghiệm thu tổng thể — Core, năm engine và luồng CRM

| BẢNG TÓM TẮT | Nội dung |
|---|---|
| Nguồn chuyển giao | **chuyển từ phiếu e_ocr theo CD-100**: các lát **4, 5, 7, 8, 10, 12** và bài test **60 phút qua CRM**. |
| Hai tầng nghiệm thu | [Engine OCR](PHIEU-ENGINE-e_ocr.md) chạy máy test độc lập trước; phiếu này thực hiện sau, **không chặn OCR xong**. Hoàn tất engine không đồng nghĩa đã nghiệm thu toàn hệ thống. |
| Khối lượng — ước tính | **6 việc chung: 22 giờ; bài CRM: 1 giờ (60 phút); tổng 23 giờ công còn lại — ước tính mới.** Không bao gồm các lát engine/CE/HC/CRM do phiếu khác quản lý, thời gian chờ hoặc sửa lỗi phát sinh. |
| Chủ trì và tính giờ | Lead điều phối; tái dùng AI-KENH, G3-GOI-34/13c/38/39/40 đã có trong [kế hoạch G3-GOI](KE-HOACH-G3-GOI.md). **Không giao lại hoặc cộng giờ trùng** với phần chung CD-098. |

Cập nhật **06/11/2026**. Căn cứ [CD-100](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md), [Quyết định cuối e_ocr](QUYET-DINH-CUOI-e_ocr.md) §2–§5 (**văn bản gốc thắng khi khác**) và G3-GOI §6.1–§6.7. Đã đọc CD-100 từ nhánh `hop-nhat-20261023` và văn bản gốc tại thư mục dự án chính vì worktree chưa có hai nguồn mới. **Mọi ước giờ cũ của phiếu OCR hết hiệu lực**; các số ở đây được ước lại theo phạm vi chuyển giao, chưa phải thời gian đã đo.

## 1. Sáu việc tiếp nhận, phụ thuộc và ước tính

**T** = test thuần nhanh + review chéo Codex; **N** = T + PG đầy đủ + Opus khi thay đổi nhạy cảm; **M** = lead thử thật trên giao diện DEMO/Windows được phép. Worker chỉ test thuần/mock, không chạy/dừng PostgreSQL hay server.

| Lát từ phiếu OCR | Việc nhận — chuyển từ phiếu e_ocr theo CD-100 | Phụ thuộc / điều kiện | Giờ còn lại — ước tính | Kiểm / mã dùng lại |
|---|---|---|---:|---|
| 4 | Kênh AI qua Core để engine trích gọi đúng quyền, phạm vi, nội dung | Dùng kết quả 1a đã xác minh theo CD-098; chỉ nối 1b khi thiếu, API/contract mới cần duyệt. Không tạo cổng/transport thứ hai | 3 | T; N khi đổi quyền/CSDL; AI-KENH 1a/1b |
| 5 | SDK cuối: tháo import lõi AI, kiểm kiểu dữ liệu/alias/identity và wheel độc lập | Sau phần kênh AI cần thiết; dùng khung/helper đã gộp; chốt bản phát hành riêng theo §6.3 | 4 | T; G3-GOI-34 |
| 7 | Rào chắn nạp gói thật, quyền kiểm kê mọi pháp nhân | Đủ bốn điều kiện G3-GOI §6.1: chặn bytecode, root đúng shim, chỉ đọc gói ghim, log lý do cố định; đối chiếu hash/pins, phần nợ §6.5 | 5 | N; G3-GOI-13c |
| 8 | Chứng minh năm gói cài độc lập, không đọc mã repo/engine/module khác | G3-GOI-09/20/26/30 đầy đủ/37; Mask có manifest/contract hợp lệ và nguồn/lock thực dùng, không dùng tài liệu thay nguồn thiếu; SDK phát hành phù hợp | 4 | T; G3-GOI-38 |
| 10 | Phát hiện → đăng ký → chạy đúng bản ghim → hiện đúng trên Quản lý engine | Sau 13c, 38 và đủ bằng chứng runtime/Windows từng engine, gồm OCR-WIN-NT; kiểm registry/pins, quyền và vòng đời | 4 | N + M; G3-GOI-39 |
| 12 | Hướng dẫn, ảnh thật, trạng thái và điều kiện còn chờ của nghiệm thu cuối | Sau 39 và bài cuối các engine/bài CRM; không ghi sẵn “đạt” | 2 | T; G3-GOI-40, phần cuối |
| | **Tổng sáu việc chung — ước tính** | Cùng việc chung CD-098, chỉ một lần thực hiện/tính giờ | **22** | |
| Bài CRM riêng | Bài qua giao diện ở mục 3, giữ đủ 60 phút theo quyết định chuyển giao | Sau các gate chung và tích hợp CE/HC/CRM; không phục hồi lát 11 vào phiếu OCR | 1 | T + M; bài nghiệm thu tổng thể |
| | **Tổng phiếu — ước tính** | Sáu việc chung + một bài CRM | **23** | |

Thứ tự: **4 (1a → 1b nếu thiếu) → 5**; việc **7** làm phần độc lập khi đủ điều kiện; **5 + 7 + năm gói đủ → 8 → 10 → bài CRM → 12**. Phụ thuộc chuỗi **CE-2, CE-3, CE-4a/4b, CE-5a/5b, CE-6/7, HC-1/2**, tích hợp **CR9a**, nghiệm thu **CE-8** giữ chủ trì ở phiếu tương ứng; lead kiểm trạng thái trước khi xếp lịch. Các điều kiện này **không chuyển ngược thành blocker của engine OCR**. CE-K/Cloud không là điều kiện đọc OCR bằng Local.

Sáu hàng này là một phần việc chung đã có ở G3-GOI §6.6 (CD-098), không thành sáu lát triển khai mới. **22 giờ là dự toán thay thế cho cùng phạm vi chung khi điều phối theo CD-100, không cộng thêm vào quỹ 19 giờ lịch sử ở §6.6**; bài CRM 1 giờ chỉ tính tại đây. Phần đã hoàn tất ở các mã chung phải trừ trước giao việc, không tính lại; khi ước lượng thay đổi, lead cập nhật cả phiếu này và tham chiếu §6.7.

## 2. Điều kiện trước khi chạy tổng thể

- Engine OCR đã có bài máy test riêng; các engine khác đủ bằng chứng cho năng lực đem nghiệm thu. Bảng Word giữ ô không tự đồng nghĩa đã có `ocr.trich_bang@1`.
- Mask thiếu nguồn/manifest/contract hoặc điều kiện bắt buộc thì chưa nghiệm thu đủ năm gói. **Wheel SDK 1.4.1 chỉ candidate theo G3-GOI §6.3**; không đổi/ghim SDK từ phiếu tài liệu này. Lát OCR-20 vẫn được làm theo khung đã gộp, không chờ SDK cuối.
- Lead chuẩn bị Core thử được cấp bằng dữ liệu DEMO, xác nhận trạng thái CRM và quyền Admin/pháp nhân. **8796** chỉ là cổng trong kế hoạch cũ; chỉ dùng **8790** khi phiên đã được lead xác nhận sẵn sàng. Phiếu không xác nhận cổng nào đang chạy; worker không khởi động/dừng dịch vụ.
- Nếu CRM còn lỗi Bật/mở màn thì ghi **chưa kiểm tổng thể**, không yêu cầu OCR chờ CRM. Trước báo sẵn sàng, lead tự bấm bằng trình duyệt thật theo CD-099: đăng nhập → Bật CRM → trang chủ → bấm ô Hợp đồng & bán hàng → mở Dự án/Báo giá → F5 → về trang chủ, lưu ảnh; gọi API không thay cho luồng này.

## 3. Bài test 60 phút qua CRM — chuyển từ phiếu e_ocr theo CD-100

**60 phút là thời lượng bài được chuyển nguyên phạm vi; 1 giờ công là ước tính cho một lượt chạy**, không gồm thời gian dựng mẫu hay sửa lỗi. Bộ mẫu phối hợp với OCR-MAY, không làm bộ dữ liệu thật: PDF quét 3 trang, hai ảnh PNG/JPEG một trang, Word đáp án cùng bộ; “Công ty DEMO Ánh Dương”, **1.000.000 VND**, **30/10/2026**; bảng có ô trống/ô gộp; PDF 61 trang, tệp trên 20 MiB, tệp hỏng. Tất cả có nhãn **DEMO**, chỉ là bộ mẫu cần chuẩn bị, chưa khẳng định đã tồn tại.

| Bước qua giao diện | Thao tác trong DEMO | Điều phải thấy để đạt | Phút |
|---|---|---|---:|
| 1 | Đăng nhập Admin DEMO → Quản trị Core → Quản lý engine → OCR | Đúng phiên bản và lý do sẵn sàng/chờ; dữ liệu giả có nhãn; không hiện xanh khi Windows chưa kiểm | 5 |
| 2 | Từ trang chủ bấm Hợp đồng & bán hàng → màn tải hợp đồng; chọn PDF DEMO và gửi | Có thông báo nhận việc; Việc của tôi thấy một chuỗi, bước OCR và vị trí hàng chờ. Luồng đích cần nối CE/CRM, chưa khẳng định đang chạy | 10 |
| 3 | Gửi thêm hai ảnh DEMO; mở chi tiết việc đầu | Một chủ OCR, không xử lý trùng; việc sau chờ rõ; không trừ hạn mức hai lần; thứ tự theo chính sách đã duyệt | 10 |
| 4 | Mở kết quả OCR, đối chiếu PDF/Word đáp án giả; tải kết quả | Chữ có vị trí/nguồn; tiền/ngày nguyên; bảng không mất ô; Core nhận xong mới giải phóng kết quả; mở lại trang vẫn thấy kết quả | 10 |
| 5 | Gửi tệp quá cỡ, quá trang, hỏng; hủy một việc đang chờ | Lỗi dễ hiểu; không thành công giả, không tự gửi lại hoặc hoàn hạn mức khi chưa rõ; hủy theo quyền/quy tắc chuỗi | 10 |
| 6 | Lead thử tài khoản DEMO khác pháp nhân tải kết quả; mở lại chi tiết engine và nhật ký thời gian | Từ chối đúng quyền; không lộ đường dẫn/bí mật; ảnh, thời gian chờ/chạy, kết quả và phần chưa kiểm đầy đủ | 15 |
| | **Tổng** | | **60** |

Giao diện dùng tiếng Việt nghiệp vụ, không mã kỹ thuật, không xưng “Anh”/“bạn”; ngày **dd/mm/yyyy**, tiền có đơn vị. Chụp ảnh thao tác thật; nhật ký chỉ dùng DEMO và không lộ bí mật.

## 4. Điều kiện đạt và báo cáo

Sau khi đủ tiền đề, lead chạy bài tổng thể **hằng ngày và trước báo xong mốc**, ghi phút thực tế, ảnh màn và log từng ca; PG toàn bộ một lần/đêm. Đạt khi không thêm mã lỗi so [NEN-TEST.md](../../46-chuyen-doi-dieu-phoi/NEN-TEST.md), không tăng skip không giải thích, và tất cả ca đầu–cuối/Windows bắt buộc có bằng chứng. Không tự bỏ qua lỗi mới vì trùng tên lỗi cũ; phần chưa kiểm ghi rõ.

Việc chờ Anh của riêng OCR giữ ở [phiếu OCR mục 4](PHIEU-ENGINE-e_ocr.md): giấy phép FineReader Corporate trước chuyển máy chủ, cho phép kết nối tạm có khóa trước thử thật, Anh tự chuyển PDF/DOCX vào lưu trữ. Trích bảng, hóa đơn giấy, bảng kê và chuyển ABBYY lên máy chủ **để sau**, không thành điều kiện nghiệm thu OCR v1; khi chuyển máy phải chạy lại OCR-MAY **ca 2, 5, 8**.

**Phiếu này mới tiếp nhận kế hoạch; chưa chạy PG, ABBYY, trình duyệt hoặc bài CRM, chưa có kết luận nghiệm thu đạt.**
