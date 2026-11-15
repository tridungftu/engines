# Sửa an toàn MASK-3b…6 — 15/11/2026

Kết luận: **Đạt phạm vi sửa an toàn, đã kiểm bằng Core giả (CoreGia); chưa đạt nghiệm thu chung qua CLI SDK chuẩn vì thiếu nguồn quyền Core.** PR: **chờ lead mở**. Không commit/push.

Đã làm: bỏ toàn bộ Unicode Cf và variation selector trước dò NFC, giữ ánh xạ về đoạn gốc; bỏ ký tự vô hình còn lại và chặn phong bì khi không an toàn. Che được các ví dụ lead nêu cùng tổ hợp NFD/NBSP/tab/xuống dòng, MST/STK. Bí danh tạm chỉ mở/ghi tham chiếu trong đúng yêu cầu sinh ra; mỗi yêu cầu có alias tạm riêng, hàng chờ vẫn gộp cụm và đếm đúng. Mã chính thức/Junsky giữ ổn định. Bọc cả lỗi lạ và lỗi đã mang kiểu LoiNghiepVu từ ngăn bằng câu cố định, không để tên gốc vào stdout/stderr hoặc thông điệp lỗi. Chặn chốt bản che không đạt.

Đã chuyển nguyên hai mô-đun lưu trên máy cùng schema cũ sang `e_mask/LUU-TRU/mask_truoc_ngan/`, SHA LF khớp blob gốc. Test lịch sử nạp riêng ngoài gói; kiểm độc lập chặn mã đọc biến cấu hình máy và import hiện vật. README, VIEC, CHANGELOG và NGUON đã cập nhật; SHA theo LF. Giữ nguyên `_chung/**`, hai mẫu `ngan.py/cau_hinh.py`, nguồn cũ và hợp đồng chung.

Kết quả kiểm:

| Lệnh (Python trong .venv) | Kết quả thật | Mã thoát |
|---|---|---:|
| `python -m pytest e_mask/tests -q --basetemp=.pytest-tmp` | **422 passed, 190 subtests passed, 0 skipped**, 31.39 giây | 0 |
| `python e_mask/tests/chay_demo.py` | **2/2 ĐẠT**, adapter có quyền/ngăn DEMO ngoài gói | 0 |
| `python e_mask/tests/kiem_doc_lap.py` | **ĐẠT**, không còn mã đọc biến lưu trữ máy trong gói | 0 |
| `node --test e_mask/tests/ui/duyet_dinh_danh.test.mjs` | **4/4 ĐẠT**, KttCore giả | 0 |
| `python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT**, chặn thiếu nguồn quyền tin cậy | 1 |
| `git diff --check` | Không lỗi khoảng trắng | 0 |

Toàn bộ 280 ca nền vẫn nằm trong bộ kiểm; thêm 142 ca, không skip. Có kiểm từng Cf trong bảng Unicode của Python và các selector, vị trí nguyên văn, từ chối khi không ánh xạ được, alias tạm khác yêu cầu trước/sau duyệt, giữ mã chính thức, CAS/retry/dọn và capsys/capfd. [Nhật ký thật](KET-QUA-KIEM-SUA-AN-TOAN-MASK-3b-6.txt). Môi trường Windows, Python 3.13.14, SDK 2.0.0 offline đã đối chiếu SHA. Chưa chạy Linux/Core thật hoặc Cloud.

Thời gian thực tế: **08:25:00–08:54:41 ngày 15/11/2026 (UTC+07), 0.49 giờ**. Phiếu MASK-3b ước tính **3 giờ**; MASK-3b…6 tổng **13 giờ**. Không có dự toán riêng cho vòng sửa an toàn này.

Lệch khỏi phiếu / quyết định tạm đã dùng: yêu cầu mới về phạm vi alias tạm thay quy tắc tra tạm toàn bảng trong tài liệu cũ. Chia nhóm review A (types/che/phong bì, 3 tệp), B (kho qua Core/ngăn/cổng, 3 tệp), C (3 hiện vật chuyển lưu trữ); test/tài liệu không tính vào trần mã. `git mv` bị sandbox từ chối vì Git index ngoài vùng được ghi; dùng Move-Item, giữ nguyên nội dung. **Lead cần stage các rename khi commit.** Không thay hợp đồng để làm CLI chuẩn vượt kiểm.

Cần Core / Chờ Anh mới phát sinh: nguồn quyền/mã yêu cầu tin cậy, ngăn thật, lease và các phụ thuộc cũ vẫn chờ Core. Khi nối port thật phải giữ ràng buộc alias tạm theo yêu cầu trong giao dịch và quyền server. Không thêm API/schema chung, không có câu hỏi mới cần Anh quyết định. SDK còn cần nhật ký an toàn cho lỗi ngoài handler.
