# Phiếu kế hoạch engine — Đọc văn bản từ bản quét (OCR)

| BẢNG TÓM TẮT | Nội dung |
|---|---|
| Kết quả v1 | Admin thử engine độc lập: PDF/ảnh → văn bản có vị trí trang, bản Word giữ ô trống/ô gộp; trích vùng trả chữ và cờ nghi ngờ. ABBYY được ưu tiên, tự chuyển sang Tesseract khi cần. |
| Phạm vi đã chốt | **10 lát riêng OCR: 3 đã gộp, 7 còn lại.** Máy test engine trước; nghiệm thu tổng thể ở phiếu riêng làm sau, không chặn OCR xong. |
| Giờ công còn lại — ước tính | **22 giờ**, gồm chuẩn bị DEMO và lần chạy OCR-MAY đầu; không tính lại 17/18/19 đã gộp. Chưa gồm chờ cấp phép/kết nối, sửa lỗi phát sinh hoặc các lần chạy hằng ngày tiếp theo. |
| Việc chờ Anh | Giấy phép FineReader Corporate trước khi chuyển lên máy chủ; cho phép kết nối tạm có khóa trước lát 9; Anh tự chuyển PDF/DOCX nguồn vào lưu trữ. Các việc này không chặn phần code/kiểm giả lập được phép. |
| Cách triển khai | Tận dụng mã hiện có, ưu tiên abbyy-hotfolder; mask_ocr chỉ nhánh Tesseract. Lead quyết số lát song song lúc triển khai; không chờ duyệt lại phạm vi đã chốt. |

Cập nhật **06/11/2026** theo [CD-100](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md) và [Quyết định cuối e_ocr](QUYET-DINH-CUOI-e_ocr.md) §1–§5; **văn bản gốc thắng khi có khác biệt**. Worktree OCR-PHIEU chưa có hai nguồn mới: đã đọc CD-100 từ `hop-nhat-20261023` và quyết định gốc tại thư mục dự án chính, chỉ đọc. **Mọi ước giờ cũ hết hiệu lực**; các số dưới đây là **ước tính mới**, chưa phải thời gian đã đo hay cam kết nghiệm thu đạt.

## 1. Hiện trạng và phạm vi v1

Đã đối chiếu `git log hop-nhat-20261023` ngày **06/11/2026**:

| Phần | Trạng thái có căn cứ |
|---|---|
| Nền đọc văn bản, giữ bảng Word, khung chạy, bàn giao | Đã gộp OCR-2 `292ef532`, OCR-3 `9ef5e412`, OCR-4a `9ceee54f`, OCR-4b `b8ba1e7b`, OCR-5a `11b0ae30`, OCR-5b/5c `0d021dc7`; Windows/ABBYY thật còn phải kiểm. |
| Gói riêng và một cổng OCR | Đã gộp G3-GOI-15 `11d86468`, G3-GOI-16 `331c5620`. |
| Lát 1 / G3-GOI-17 | **ĐÃ GỘP hôm nay 06/11/2026**: mã `270f2af0`, lead ghi gộp `72e8c390` lúc 14:40. Nền parser mask_ocr đã có; nguồn ưu tiên abbyy-hotfolder theo CD-100 phải được đối chiếu trong các lát bổ sung, không coi đã tích hợp toàn bộ. |
| Lát 2 / G3-GOI-18 | **ĐÃ GỘP hôm nay 06/11/2026**: mã `cb51ae4e`, lead ghi gộp `15ebff47` lúc 15:25. |
| Lát 3 / G3-GOI-19 | **ĐÃ GỘP hôm nay 06/11/2026**: mã `406eddce`, lead ghi gộp `66dfdd61` lúc 16:12. |
| Lát 6 / G3-GOI-20 | Có thể làm theo **khung SDK đã gộp, không chờ SDK cuối**. Không đổi version SDK; wheel 1.4.1 chỉ candidate theo [kế hoạch §6.3](KE-HOACH-G3-GOI.md#63-điều-kiện-từ-lát-04-opus-review-05112026). |

Năng lực v1: đọc văn bản có vị trí trang, bản Word và bảo toàn ô trống/ô gộp/vị trí bảng; thêm **`ocr.trich_vung@1`** cho Đối chiếu bản ký (TL 57). Giới hạn đầu vào đang công bố: **PDF/PNG/JPEG; 20 MiB, 60 trang, 900 giây; một việc đồng thời**. Nhánh nguồn dự phòng còn có đọc PDF có chữ sẵn, DOCX, giữ bảng, xuất Word, hàng chờ/chống trùng; việc có mã nguồn không tự mở rộng đầu vào công bố hoặc chứng minh năng lực mới đã đạt.

Nguồn mã được phép dùng nội bộ:

- **Ưu tiên `D:\GPT\OCR\abbyy-hotfolder`**: cầu nối ABBYY FineReader Hot Folder. **TUYỆT ĐỐI KHÔNG chép `in\`, `out\`, `jobs\`, `state\` của abbyy-hotfolder**: có khóa API; không đọc, không in, không commit các thư mục này. Chỉ lấy mã sạch cần thiết theo whitelist của lát triển khai.
- **`D:\GPT\OCR\mask_ocr` chỉ nhánh Tesseract (vie+eng)**, cùng các phần đọc/giữ bảng/xuất Word/hàng chờ nêu trên. Không chép VietOCR, mô hình chỉ phục vụ VietOCR hoặc review dual; không xóa mã cũ.
- Giấy phép mã nguồn đã chốt: **“phần mềm nội bộ, dùng nội bộ tập đoàn”**; 17–20 đã mở chặn giấy phép nguồn. Đây là quyết định về mã nội bộ, còn giấy phép FineReader Corporate phục vụ nhiều người qua máy chủ ở mục 4.

## 2. Danh sách lát sau CD-100 và ước tính

**T** = test thuần nhanh + review chéo Codex; **N** = T + PostgreSQL đầy đủ + Opus cho thay đổi CSDL/quyền/tiền/bí mật/xóa; **M** = lead thử qua giao diện DEMO/máy được phép. Worker chỉ chạy thuần/mock; PG, server, ABBYY thật và thay đổi Windows do lead trong phạm vi đã được phép. Giao diện làm song song back end theo CD-058: tiếng Việt nghiệp vụ, không mã kỹ thuật, không xưng “Anh”/“bạn”, ngày **dd/mm/yyyy**.

| Lát / mã | Nội dung giữ hoặc thêm | Phụ thuộc / điều kiện | Giờ còn lại — ước tính | Kiểm |
|---|---|---|---:|---|
| 1 / G3-GOI-17 — GIỮ | Mã nguồn nội bộ trong gói, ưu tiên abbyy-hotfolder + mask_ocr chỉ Tesseract, đúng giới hạn nguồn mục 1 | **ĐÃ GỘP** nền nguồn; đối chiếu phần cầu nối ở OCR-NOI/OCR-KETNOI, không giao lại nguyên trạng | 0 | T |
| 2 / G3-GOI-18 — GIỮ | Nối đọc văn bản và bàn giao vào nguồn trong gói | Sau 1; **ĐÃ GỘP** | 0 | T |
| 3 / G3-GOI-19 — GIỮ | Giữ ô trống, ô gộp và vị trí bảng trong kết quả Word | Sau 2; **ĐÃ GỘP**; chưa công bố trích bảng riêng | 0 | T |
| OCR-NOI — THÊM | Đưa lớp chữ PDF ABBYY (“text under image”) về cấu trúc kết quả chung của mask_ocr; **không OCR lại ảnh nền** | Sau 1; dùng lại parser/adapter hiện có | 3 | T |
| OCR-KETNOI — THÊM | Cầu nối để máy chủ Core gọi ABBYY trên máy hiện tại, **có khóa, chỉ cho địa chỉ máy chủ Core**; log không lộ khóa/đường dẫn | Sau 1; code/mock trước. Khóa lưu két bí mật, không git/log/chat; không tự đọc/ghi két hay mở mạng | 4 | N |
| OCR-VUNG — THÊM | `ocr.trich_vung@1`: dùng lại `crop_quad`, trả chữ + cờ nghi ngờ | Sau 1; bộ vùng cắt DEMO và contract đúng chuẩn | 3 | T |
| OCR-CHON — THÊM | ABBYY trước; tự chuyển mask_ocr khi hết **5.000 trang/30 ngày**, máy ABBYY tắt, ABBYY lỗi/quá giờ. Kết quả ghi nguồn; Quản lý engine hiện đã dùng/còn lại và trạng thái máy ABBYY | Sau OCR-NOI; kiểm ca chuyển bằng mock, màn làm song song | 3 | T + M |
| 6 / G3-GOI-20 — GIỮ | Ghim thư viện + nguồn, hướng dẫn cài môi trường sạch theo khung SDK đã gộp | Sau nền 1→2→3 và các thay đổi OCR trên; **không chờ SDK cuối/G3-GOI-34, không ghim wheel 1.4.1 candidate** | 2 | T |
| 9 / OCR-WIN-NT — GIỮ | Thử ABBYY thật **trên máy hiện tại (tạm)** với PDF DEMO; kiểm cách ly và bàn giao | Sau 6; cầu nối đã kiểm. **Chờ Anh cho phép kết nối tạm có khóa**; chuẩn bị `.cmd` ASCII + hướng dẫn theo CD-065/087, không tự đổi tường lửa/mạng | 3 | N + M |
| OCR-MAY — THÊM | Bộ DEMO giả và bài test engine độc lập đúng 9 ca ở mục 5, thay lát 11 | Kết quả các lát trên đủ để chạy thật; chuẩn bị bộ mẫu/màn thử sớm. Chạy hằng ngày và trước báo xong | 4 | T + M |
| **Tổng 10 lát: 3 đã gộp, 7 còn lại** | Chỉ phần engine OCR, không cộng phần tổng thể | Bao gồm lần chạy OCR-MAY đầu | **22** | |

**BỎ** lát 11 (thử qua CRM), thay bằng OCR-MAY; bỏ VietOCR / dual / màn duyệt điểm khác nhau khỏi v1. **CHUYỂN** lát **4, 5, 7, 8, 10, 12** và bài **60 phút qua CRM** sang [Phiếu nghiệm thu tổng thể](PHIEU-NGHIEM-THU-TONG-THE.md), ghi “chuyển từ phiếu e_ocr theo CD-100”. Các việc này làm sau, **không chặn OCR xong**, không cộng giờ trùng với việc chung CD-098.

**ĐỂ SAU khi xong engine:** `ocr.trich_bang@1`, OCR hóa đơn giấy, OCR bảng kê và chuyển ABBYY lên máy chủ. Khi chuyển máy phải chạy lại **ca 2, 5, 8** của OCR-MAY. Giữ cấu trúc bảng trong Word ở v1 không đồng nghĩa công bố `ocr.trich_bang@1`.

## 3. Thứ tự ưu tiên và triển khai

1. **1 → 2 → 3**: nền gói đã gộp, không giao lại.
2. **Song song sau 1:** OCR-NOI, OCR-KETNOI, OCR-VUNG; làm phần code/mock và giao diện được phép.
3. **OCR-CHON sau OCR-NOI.**
4. **Lát 6:** ghim theo khung SDK đã gộp; không chờ SDK cuối.
5. **Lát 9:** ABBYY thật trên máy hiện tại, chỉ sau khi Anh cho phép kết nối tạm có khóa. Chuẩn bị sẵn `.cmd` ASCII + hướng dẫn trong lát triển khai được whitelist; lát tài liệu này không tạo/chạy `.cmd`.
6. **OCR-MAY:** chạy bài cuối đúng mục 5, **hằng ngày và trước khi báo xong**; ghi phút thực tế mỗi lần.

Lead quyết số lát giao song song khi bắt đầu triển khai. Phạm vi đã chốt theo CD-100, không đứng chờ duyệt lại; phần chưa được phép mở kết nối hoặc thay đổi hệ thống giữ riêng, tiếp tục việc khác. SDK cuối, năm gói độc lập, chuỗi CE/HC và CRM thuộc phiếu tổng thể, không là điều kiện mở các lát OCR trên.

## 4. Việc chờ Anh — không chặn phần code được phép

| Việc chờ Anh | ☑ Đề xuất | Mốc cần quyết định |
|---|---|---|
| Giấy phép FineReader Corporate cho tự động phục vụ nhiều người qua máy chủ | ☑ Xác nhận quyền dùng phù hợp trước khi đưa ABBYY lên máy chủ | Trước chuyển máy chủ; chưa chặn code/mock hoặc nền nguồn nội bộ |
| Cho phép mở kết nối tạm có khóa trên máy hiện tại | ☑ Chỉ cho địa chỉ máy chủ Core, có khóa lưu két; lead chuẩn bị `.cmd` ASCII và hướng dẫn theo CD-065/087 | Trước lát 9/kết nối thật; không tự đổi tường lửa, mạng hay két bí mật |
| Hợp đồng PDF ở `abbyy-hotfolder\in\` và DOCX ở `out\` cần lưu trữ | ☑ **Anh tự chuyển** sang thư mục lưu trữ | Worker/lead không mở, đọc, in hoặc chép các thư mục nguồn bị cấm |

Ngưỡng đúng/sai của nhánh Tesseract: **Anh chốt sau lần đo đầu** ở ca 4; trước đó chỉ ghi số đo, không tự đặt ngưỡng để báo đạt.

## 5. Bài test cuối engine độc lập — OCR-MAY

Bộ DEMO **hoàn toàn giả**, có nhãn DEMO: PDF quét 3 trang có bảng ô trống/ô gộp; 2 ảnh PNG/JPEG một trang; Word đáp án cùng bộ, “Công ty DEMO Ánh Dương”, **1.000.000 VND**, ngày **30/10/2026**; một ảnh vùng cắt; PDF **61 trang**, tệp **> 20 MiB**, tệp hỏng. Bộ mẫu là việc cần chuẩn bị trong OCR-MAY, chưa tuyên bố đã có. Không dùng hồ sơ thật.

Admin DEMO thao tác qua **Chạy thử DEMO / Quản lý engine**, chỉ Admin. Kiểm bằng **trình duyệt thật** theo CD-099: đăng nhập → mở màn → thao tác chính → F5 → về trang chủ, lưu ảnh; gọi API có header không thay bằng chứng thao tác qua màn. Không cần đi qua CRM để nghiệm thu engine.

| Ca | Thao tác | Phải thấy để đạt |
|---|---|---|
| 1 | Mở Quản lý engine → OCR | Đúng phiên bản; ABBYY sẵn sàng; hạn mức đã dùng/còn lại |
| 2 | Gửi PDF DEMO (ABBYY bật) | Nguồn = ABBYY; chữ có vị trí trang; Word tải được; tiền/ngày khớp đáp án; bảng còn đủ ô trống/ô gộp |
| 3 | Gửi 2 ảnh liên tiếp + gửi trùng 1 tệp | Báo số việc đang chờ; không xử lý trùng; thứ tự rõ ràng |
| 4 | Giả lập hết hạn mức, gửi lại PDF DEMO | Tự chuyển mask_ocr (Tesseract); nguồn = mask_ocr; ghi số đo đúng/sai so đáp án; **ngưỡng đạt Anh chốt sau lần đo đầu** |
| 5 | Tắt cầu nối ABBYY, gửi ảnh DEMO | Tự chuyển mask_ocr, không treo; ghi lý do chuyển |
| 6 | Gửi vùng cắt | Trích vùng trả chữ + cờ nghi ngờ |
| 7 | Gửi tệp quá cỡ, quá trang, hỏng; hủy 1 việc đang chờ | Lỗi dễ hiểu; không báo thành công giả; không trừ hạn mức sai |
| 8 | Gọi cầu nối từ máy khác không khóa / từ máy chủ Core có khóa | Không khóa → bị chặn; có khóa từ đúng máy chủ Core → được; log không lộ khóa/đường dẫn. Ca âm địa chỉ ngoài danh sách cho phép thuộc OCR-KETNOI |
| 9 | Xem nhật ký | Thời gian chờ/chạy từng ca; nguồn đọc từng ca |

**Đạt** khi mọi ca có **ảnh màn + log**, không thêm mã lỗi so [NEN-TEST.md](../../46-chuyen-doi-dieu-phoi/NEN-TEST.md), không tăng skip không giải thích, và các điều kiện cần chốt có kết quả rõ. Phần chưa kiểm ghi rõ, không báo đạt thay; lead ghi phút thực tế từng lần chạy. Thực hiện **hằng ngày và trước báo xong**; PG toàn bộ do lead chạy một lần/đêm. **Lát OCR-PHIEU chỉ sửa tài liệu, chưa chạy ABBYY, PG, trình duyệt hay nghiệm thu engine.**
