Anh, **đường ABBYY hiện có là Hot Folder cục bộ; chưa có HTTP trong năm tệp khảo sát.** Có thể chia phần kết nối thành các lát DEMO/mock, mặc định tắt.

1. **Hiện trạng**
   - `BackendABBYY.ocr()` → `CongOCR.ocr()` → ghi tệp vào `in`, chờ DOCX trong `out`: `engines/e_ocr/abbyy.py:137`, `engines/e_ocr/lib/cong_ocr.py:317`. `src/kho_tri_thuc/ha_tang/cong_ocr.py:9` chỉ là alias, không phải cầu nối mạng.
   - Luồng mới nhận backend `san_sang()` / `doc_pdf()` được Core tiêm; cần **PDF có lớp chữ**, backend chỉ vận chuyển, không tính trang: `engines/e_ocr/chon_nguon.py:3`, `:137`, `:176`.
   - Nguồn cầu nối được tài liệu chỉ tới **ngoài repo**, tại `D:\GPT\OCR\abbyy-hotfolder`: `docs/47-core/g3/QUYET-DINH-CUOI-e_ocr.md:10`. `engines/e_ocr/NGUON.md:27` chỉ liệt kê các tệp `mask_ocr` đã chép; `:209` xác nhận chưa nối cầu ABBYY thật. Chưa xác định giao thức của nguồn ngoài vì không đọc nguồn đó.

2. **Kiến trúc đề xuất**
   - Máy chủ Core → client HTTPS → dịch vụ nhỏ trên máy ABBYY → adapter Hot Folder dùng lại mã chung. Client triển khai đúng `san_sang`/`doc_pdf`; không mở chia sẻ thư mục cho Core.
   - Đặt dịch vụ và client trong `engines/e_ocr/`. Kiểm **đồng thời khóa và IP Core**, lấy IP từ socket thực, không tin `X-Forwarded-For`; firewall chỉ cho địa chỉ Core.
   - Core lấy khóa qua **két bí mật hiện có**, tiêm vào RAM qua bootstrap tin cậy; không ghi khóa vào cấu hình thường, URL, args hoặc env. Hướng tiêm RAM đã có tại `abbyy.py:15`; API két và điểm bootstrap cụ thể chưa được xác minh trong phạm vi này.
   - Log theo danh sách trường cho phép: mã tương quan ngẫu nhiên, kết quả, thời gian, số trang. Không ghi header, tên/đường dẫn tệp, nội dung tài liệu, exception gốc; tắt access log mặc định có thể lộ URL.

3. **Các lát đề xuất — mỗi lát ≤3 tệp**

   Các đường dẫn dưới đây tương đối với `engines/e_ocr/`, **chưa phải whitelist triển khai**.

   | Lát | Tệp đề xuất | Kiểm DEMO/mock |
   |---|---|---|
   | KN1 | `lib/cong_ocr.py`, `tests/test_hot_folder_pdf.py` mới, `NGUON.md` | Tách vận chuyển PDF, giữ đường DOCX; mock toàn bộ filesystem |
   | KN2 | `cau_noi_abbyy.py` mới, `tests/test_cau_noi_abbyy.py` mới | Thiếu/sai khóa; đúng khóa nhưng sai IP; không lộ bí mật qua log |
   | KN3 | `ket_noi_abbyy.py` mới, `tests/test_ket_noi_abbyy.py` mới | Mock HTTP: timeout, mất kết nối, phản hồi sai/quá cỡ, hủy |
   | KN4 | `abbyy.py`, `chon_nguon.py`, `tests/test_chon_nguon.py` | Tiêm backend, fallback, chống gửi trùng và đối chiếu hạn mức |

   Mọi lát mặc định **tắt**, không bind socket khi import; DEMO không tự công bố ABBYY thật sẵn sàng. **Lát 9** mới mở kết nối/firewall, cấp bí mật thật và thử ABBYY bằng PDF DEMO, sau khi Anh cho phép: `QUYET-DINH-CUOI-e_ocr.md:55`.

4. **Rủi ro cần chốt**
   - Khóa qua HTTP thuần có thể bị lấy lại; cần TLS xác minh chứng thư, chống replay/gửi trùng, giới hạn dung lượng, thời gian và hàng chờ.
   - Không nhận đường dẫn hay endpoint từ payload; bảo vệ thư mục bằng ACL, giữ cách ly Windows: `abbyy.py:8`.
   - **Timeout sau gửi có thể vẫn tiêu trang ABBYY:** lớp chọn nguồn hiện hoàn trang khi thất bại (`chon_nguon.py:190`), trong khi đường cũ giữ trang nếu ABBYY đã nhận (`lib/cong_ocr.py:385`). Cần chốt cách đánh dấu “đã nhận/chưa rõ” và đối chiếu trước khi nối thật.

**Tệp đổi: 0; không commit.** Test trước/sau: **chưa chạy**, ok/fail/error/skip = **—/—/—/—**; giữ giới hạn khảo sát không tạo tệp, không thực thi luồng OCR có ghi/dọn tệp. Git sạch đầu/cuối; không truy cập các thư mục bị cấm.

**Lead cần chốt:** whitelist từng lát, điểm cấp bí mật từ Core, chính sách hạn mức khi mất phản hồi. Không thay SDK; 1.4.1 vẫn là candidate (`KE-HOACH-G3-GOI.md:355`).