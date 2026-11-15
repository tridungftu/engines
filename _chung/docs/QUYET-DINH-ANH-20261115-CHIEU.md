# Quyết định của Anh — chiều 15/11/2026 (bảng chọn trong phiên lead)

*Ghi nhận: Claude (lead), 15/11/2026. Bổ sung cho `QUYET-DINH-ANH-20261115.md`. Khi khác với phiếu giao Codex cũ, văn bản này thắng.*

## 1. Kết luận

- **E6 (Trích xuất) chấm theo giá trị**, không so từng byte câu hỏi/bảng.
- **Duyệt ba loại dữ liệu mới:** `bang_trich_xuat`, `ho_so_doi_chieu`, `ho_so_tra_cuu`.
- **Duyệt theo đề xuất** toàn bộ câu chọn: 17 câu Đối chiếu, 15 câu Tra cứu (trừ TC-Q06), 5 câu TX0-06.
- **Lớp an toàn tên viết thường của Mask: thêm AI cục bộ** (chọn trước đó trong phiên). Thiết kế ở `e_mask/docs/GIAO-CODEX-e_mask.md` mục MASK-2c.
- **Tệp Word/Excel của Mask: Anh cần nhận lại tệp giữ định dạng** → phương án **B** của MASK-7 (tự viết ZIP/XML Python thư viện chuẩn, chỉ giữ phần đã kiểm, từ chối phần lạ). Trần: dùng bộ trần thử nghiệm MASK-7 §5 (lead quyết, đo lại tại biên rồi trình Anh nếu cần đổi).
- **Mở che của Mask (Anh chốt tối 15/11, sau MASK-P3):** che và mở che nằm trong **cùng một chu kỳ** (ví dụ Mask → Hỏi AI → mở che ngay khi có kết quả); **không lưu ánh xạ ở bất kỳ đâu** (không ngăn, không tệp, không hồ sơ Core) để tránh lộ dữ liệu. Ánh xạ chỉ nằm trong RAM của tiến trình Mask trong thời gian chuỗi chạy; mất RAM thì không mở che được, người dùng chạy lại chuỗi.
- **Chưa quyết:** TC-Q06 (thời hạn giữ nhật ký hỏi đáp) — Anh trả lời riêng.

## 2. Bảng quyết định

| # | Câu | Anh chốt | Hệ quả cho Codex / lead |
|---|---|---|---|
| 1 | Lớp an toàn tên viết thường trước khi bật Cloud | **Thêm AI cục bộ** | Lát MASK-2c-1…4 + AI-9; Cloud giữ tắt tới khi MASK-2c-4 đo thật đạt 0 lọt |
| 2 | Tiêu chí E6 | **So giá trị trích ra từng mã + dẫn chứng** trên bộ DEMO chuẩn; giữ trùng byte bộ tham số (E1) và văn bản đọc ra | Sửa công cụ E6 (TX-4) theo tiêu chí mới; lead lập bộ DEMO chuẩn + bản vàng giá trị; không làm lại luồng nhiều lượt |
| 3 | Loại `bang_trich_xuat` | **Duyệt** (§4 `LOAI-DU-LIEU-RIENG.md`, gồm bổ sung ở `e_trich_xuat/docs/TX-3-REVIEW.md`: `don_vi_offset`, cờ kiểu chưa chuyển, trường tạm E6, `phan_hoi_ai` chỉ kiểm toán) | Tạo schema chung, đăng ký `trich.hau_kiem@1`, `trich.xuat_ket_qua@1` |
| 4 | Loại `ho_so_doi_chieu` (DC-Q17) | **Duyệt** | Mở DC-1 |
| 5 | Loại `ho_so_tra_cuu` (TC-Q13) | **Duyệt** | Mở TC-1 |
| 6 | 17 câu Đối chiếu DC-Q01…Q17 | **Theo đề xuất** trong `e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md` §5 | Codex làm theo cột "lựa chọn đề xuất" |
| 7 | 15 câu Tra cứu TC-Q01…Q15 | **Theo đề xuất**, trừ TC-Q06 | TC-Q06 giữ "không tự xóa" tới khi Anh chọn |
| 8 | 5 câu TX0-06 | **Theo đề xuất**: tối đa 5 câu hỏi thêm; hoãn hỏi lại nhiều vòng; TT-21 chỉ tính khi bộ module khai công thức đã duyệt; 3 hợp đồng KCN DEMO; hoãn nhánh trích bảng | Không mở phạm vi mới trong TX-1…TX-6 |
| 9 | Phương án tệp Word/Excel Mask | **Cần tệp giữ định dạng → phương án B** (MASK-7 §6, 54–80 giờ ước tính) | Lập lại phiếu MASK-8…11 theo B (lát MASK-P2), rồi giao; trần thử nghiệm MASK-7 §5 |
| 10 | Mở che của Mask | **Cùng một chu kỳ, không lưu ánh xạ ở đâu** (chỉ RAM tiến trình Mask khi chuỗi chạy) | Lập lại phiếu mở che (MASK-P4) theo hướng này; MASK-P3 phương án A không dùng; kho bí danh chính thức chỉ giữ bí danh + băm |
