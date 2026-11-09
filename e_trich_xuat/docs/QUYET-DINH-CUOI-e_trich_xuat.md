# QUYẾT ĐỊNH CUỐI — Engine trích xuất (`e_trich_xuat`): bộ tham số ở module

*Anh chốt 07/11/2026, gửi phiên điều phối 20:42. Văn bản gốc; phiếu `PHIEU-ENGINE-e_trich_xuat.md` (mốc 06/11) phải lập lại theo đây.*

## 1. Quyết định
- Bộ tham số theo loại hợp đồng nằm ở **module**, không ở Core.
- Mỗi module giữ **bản riêng**, kể cả khi hai module cùng dùng một loại hợp đồng (không dùng chung).
- Module gửi việc gồm **tệp + loại + bộ tham số**. Core điều phối: cần OCR thì qua engine OCR, rồi engine trích hỏi Local AI qua engine Hỏi AI, trả bảng kết quả về module.
- Engine **không tự tra danh mục**; chỉ trích theo bộ tham số được gửi kèm. Kết quả ghi rõ module, loại, phiên bản, hash.
- Kết quả trả về module; module tự quyết khi nào lưu vào CSDL. Core giữ tạm kết quả tới khi module lưu hoặc đóng việc, sau đó dọn.
- Bộ 37 tham số xây dựng: engine giữ tạm làm bộ mặc định cho tới khi module nhận xong. Chỉ chuyển khi **E6 so từng byte** giữa bộ module gửi và bộ mặc định cho kết quả trùng. Sau khi chuyển, bộ mặc định đưa vào lưu trữ, không xóa.

## 2. Quản lý bộ tham số
- Màn nạp Excel, lịch sử, so sánh, chạy thử, kích hoạt nằm trong **phần quản lý của từng module**, theo mô hình prompt Hỏi AI: Admin module quản lý của mình, Admin Core xem/sửa được tất cả. Không tạo quyền "Kích hoạt" riêng ở Core.
- Màn người dùng không hiện phiên bản bộ tham số.

## 3. Loại hợp đồng thứ hai: thuê đất kèm cơ sở hạ tầng (KCN)
- Module giữ bộ tham số: **CRM**. M3 dùng lại dữ liệu đã trích.
- Lead soạn bộ tham số nháp và bộ hợp đồng DEMO thuê đất; người nghiệp vụ duyệt nội dung trước khi kích hoạt.
- Bộ 30 tham số dịch vụ và 3 hợp đồng dịch vụ DEMO chuyển lưu trữ, không xóa.

## 4. Đo kết quả và test
- Giữ E6 và bài kiểm Word có Track Changes; N1 chỉ một lần kiểm nhanh, không lặp.
- Bài test cuối chia vào các buổi 17:00. Lead chạy trước các bước chờ AI/OCR; Anh chỉ mở kết quả có sẵn và tự bấm phần quản lý bộ tham số (nạp Excel có bản lỗi, xem chạy thử, kích hoạt). Phần Anh tham gia mỗi buổi không quá 30 phút. Lead chạy các ca từ chối, tải lại trang, đối chiếu, gửi ảnh và biên bản.

## 5. Việc lead làm ngay
- Dừng gộp LHD-C1/C2 theo hướng kho ở Core.
- Tận dụng tối đa code đã viết (kiểm Excel E1, logic phiên bản, 3 màn U1a/U1b) cho mô hình module; phần không dùng chuyển lưu trữ, không xóa.
- Lập lại phiếu: các lát C1–C4, E2, E5, G3-GOI-37, LHD-02b, N1, bài test cuối; bỏ Q2/Q4/Q5. Mục "Việc chờ Anh" chỉ giữ quyết định riêng của engine trích, phần chung chuyển về phiếu chủ trì.
- Ghi rõ giờ tăng/giảm so bản 06/11.
- Không đứng chờ: nhánh đóng gói (AI-KENH, G3-GOI-34, 35, 36) và E6 chạy tiếp vì không bị ảnh hưởng.
