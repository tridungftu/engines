# Lịch sử thay đổi

## 0.1.0 — 21/11/2026

- **TS-PL:** trình soạn dùng chung năm năng lực cho danh mục, quy tắc theo thứ tự, PM/TE/SAD chính xác, chính sách và khuôn cột; lỗi cạnh ô, trần UTF-8, nút kiểm, callback lưu/CAS dự kiến cửa D2. Bổ sung diễn giải/mẫu của năm tham số JSON; không đổi hàm xử lý việc. Đã kiểm bằng Core giả (CoreGia); chưa nối màn bước Core thật.

- **PL-0:** khung SDK 2.2.0, năm năng lực, sáu bảng ngăn theo pháp nhân, migration SQL và kiểm kê SHA-256; thử lại CAS, kiểm độc lập.
- **PL-0B:** bộ DEMO 500 nghiệp vụ, đáp án lớp 1 và phong bì AI giả, sinh lại tất định.
- **PL-1:** đọc JSON/Decimal, kiểm dữ liệu và ngưỡng PM/TE/SAD; phân loại module/quy tắc, chống chia nhỏ trong lô, xử lý thiếu tiền tệ.
- **PL-2:** nối phân luồng, Clopper-Pearson, bậc thang, cờ và chọn mẫu SHA-256; ngăn lượt, nộp lại Q5, kết quả JSON tái hiện được.
- **PL-3:** ghi kết quả kiểm, sửa loại, nguồn ngoài mẫu, chống trùng; cập nhật thống kê/bậc bằng CAS, Q1–Q7.
- **PL-4:** hồ sơ hành vi gộp, chia nhỏ qua lô, chốt kỳ tháng, trần 20.000 đối tác; cộng hồ sơ cùng lô với dấu lượt (phần dư trên 99 loại không nguyên tử), Q8–Q11.
- **PL-5:** chuẩn bị và hậu kiểm chuỗi Local AI, khử trùng nội dung, enum danh mục, kiểm băm/tham chiếu tệp; sai khuôn hoặc thiếu căn cứ chuyển chưa phân loại.
- **PL-6:** đọc Excel .xlsx/CSV UTF-8 theo khuôn cột; trần ZIP/XML/ô trước openpyxl, không tự gán tiền tệ.
- **PL-7:** nối sau Hóa đơn XML/ZIP, ánh xạ tổng thanh toán và cờ cần kiểm; đếm/cảnh báo nguồn không đọc được.
- **PL-8:** JSON và Excel danh sách Đỏ trong RAM, không lộ tỷ lệ/xác suất cho người duyệt; màn Admin chỉ đọc dừng an toàn khi thiếu cổng Core (CC-5).
- **PL-9:** hoàn thiện README/nguồn, rà lock, script kiểm máy sạch offline và test ZIP tất định/kiểm kê. Mô phỏng 12 tháng và đo C4/C5/hiệu năng thuộc PL-9A/PL-9B; lead ghép và ghi kết quả nghiệm thu chung.
- **PL-9D/PL-9E (sửa sau rà soát độc lập PL-4…PL-8):** xuất Excel tuyến tính theo số dòng Đỏ; lịch sử chia nhỏ chỉ khoản < TE, bỏ ngày tương lai; hồ sơ ghi tiền tệ ngưỡng (cột `tien_te`); cảnh báo trần 20.000 đối tác lên `canh_bao`; chốt kỳ đếm theo trang, lỗi một cặp không chặn cả việc; số quy đổi trong bảng phải có tiền tệ riêng; mã toàn khoảng trắng bị từ chối; làm tròn số float của Excel về 15 chữ số có nghĩa.
- **PL-9F–PL-9I (hiệu năng):** tra nộp lại và ghi kết quả bỏ đọc ngăn từng dòng: dò rỗng một lần, quét trang có ngân sách theo lượt, vượt ngân sách mới đọc từng mã; giữ nguyên ngữ nghĩa Q1–Q7 (đối chiếu bản cũ trên 240 trạng thái ngẫu nhiên mỗi phần). Bộ đo tách thời gian engine thuần khỏi Core giả. 50.000 dòng: ≤ 1.130 lần gọi Core, ước tính ≤ 31 giây ở 10 ms/lần gọi (chưa đo trên Core thật).
- **PL-10 (Anh chốt H1/H2 21/11/2026):** mã hóa đơn nối MST người bán nguyên văn (Q12); chỉ lỗi AI bỏ sót mới đổi bậc, dòng AI đã gắn cờ thì không (Q13–Q15); ô Giải thích bắt buộc khi AI sai trong JSON và Excel người kiểm (cột 10), mã lỗi `THIEU_GIAI_THICH`; `ghi_ket_qua` trả `so_ai_sai` và `tep_bai_hoc` cho Admin (Q16).

Đã kiểm bằng Core giả (CoreGia); chưa kiểm tích hợp Core thật. Bản ZIP phát hành từ git do lead đóng sau khi commit; ZIP thử worktree không đưa vào git. Các điểm CC còn mở được nêu trong README.
