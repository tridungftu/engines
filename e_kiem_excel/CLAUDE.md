# CLAUDE.md — Project engine `e_kiem_excel` · Kiểm và đọc file Excel

Người đặt yêu cầu: **Anh Dũng** (CFO).
- Trả lời bằng tiếng Việt, ngắn gọn, kết luận trước.
- Không bịa số liệu; giờ ước phải ghi "ước tính"; tiền luôn ghi đơn vị (VND, USD).

**Tóm tắt engine:** Engine dùng chung cho mọi module, 2 năng lực, chỉ loại gốc (`tep` vào, `truong` ra):
- `excel.toan_ven@1`: kiểm tính toàn vẹn file Excel, K1–K8, chuyển từ `toan_ven.py`;
- `excel.doc_bang@1`: đọc bảng nhiều tầng tiêu đề, chuyển từ `master_hd.py`.

Bộ nhóm dữ liệu gốc và khuôn cột do module truyền qua Cài đặt bước. Engine không ngăn, không cấu hình, không mạng, không lưu gì trên máy.

## 0. Đọc trước khi làm
1. `..\AGENTS.md`: quy tắc cứng, môi trường SDK 2.2.0, điều kiện đạt từng lát.
2. `docs\PHIEU-ENGINE-e_kiem_excel.md`: phiếu engine (đã duyệt tiến hành 16/11/2026).
3. `docs\GIAO-CODEX-e_kiem_excel.md`: lát và lệnh giao.
4. `docs\VIEC.md`: danh sách việc duy nhất.
5. `ma-nguon\NGUON.md`: mã gốc tham chiếu, chỉ đọc.

## 1. Ba yêu cầu bắt buộc
1. **Gắn vào Core chỉ qua cổng engine chung**, khai báo bằng `engine.json`. Thiếu cửa nào thì ghi vào `docs\VIEC.md` mục "Cần Core".
2. **Engine không gọi engine khác, không CSDL, không SQL, không mạng.**
3. **Gói độc lập:** chỉ import `kho_tri_thuc_sdk` và thư viện đã ghim (`openpyxl`, `et_xmlfile`, `defusedxml`); có `NGUON.md`; cài được trên máy sạch; test chạy với Core giả của SDK.

## 2. Thư mục
- `goi\e_kiem_excel\`: gói gửi Core (tạo ở lát EX-0).
- `tests\`: test, script sinh DEMO, đáp án (ngoài gói).
- `ma-nguon\`: `toan_ven.py`, `master_hd.py` gốc. Chỉ đọc, chỉ dùng trong test so tương đương.
- `docs\`: tài liệu.

## 3. Cách làm
- **Code bằng Codex** theo `..\AGENTS.md` và `docs\GIAO-CODEX-e_kiem_excel.md`; Claude điều phối và review.
- Tận dụng tối đa mã gốc (phiếu §3), không viết lại thuật toán.
- Trước khi nối Core thật, ghi "đã kiểm bằng Core giả (CoreGia)", không ghi "SẴN SÀNG".
- Lỗi bằng câu tiếng Việt dễ hiểu; không lộ đường dẫn, tên tệp trong máy.
- Không đứng chờ Anh: câu chờ ghi vào `docs\VIEC.md`, rồi làm việc khác.

## 4. Ràng buộc cứng
- Không xóa tệp. Không sửa `ma-nguon\`.
- **Chỉ dữ liệu DEMO**, sinh bằng script. Không dùng hồ sơ thanh toán thật.
- Tiền: `Decimal` trong tính toán; trả ra theo phiếu §4.3; không tự gán VND.
- Không chạy macro, không mở file ngoài được liên kết.
- Không push nhánh `main`. Không gửi email.
- **Không sửa mã Core trong project này.**
