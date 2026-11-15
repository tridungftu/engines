# TX-1 — Phân nhóm triển khai để lead review

Ngày 15/11/2026; nhánh `codex/e_trich_xuat-tx-1`; PR: **chờ lead mở**.
Theo lệnh giao, tổng **8 giờ công ước tính**, không mở TX-2/3.

| Nhóm | Tệp mã | Phạm vi |
|---|---|---|
| TX-1a | `__init__.py`, `chay.py`, `ngan.py`, `cau_hinh.py`, `ui/cau_hinh.js` | Khung SDK, cổng ngăn RAM tạm, cấu hình và màn quản trị |
| TX-1b | `docx.py` | Chuyển lõi Accept All/Numbering từ hai nguồn cũ, đọc DOCX trong RAM |

Đây là phân nhóm thay đổi theo hai phần lead yêu cầu trước khi viết mã;
lead quyết định tách commit/PR. Codex chỉ làm trong worktree đã giao,
không commit/push. `chay.py` của TX-1a nối hàm đã hoàn thành ở TX-1b;
phiếu bàn giao chỉ công bố `trich.doc_docx@1`, không có năng lực giả.

Đã nối ngăn chung NGAN-0 — 15/11/2026 (PR #34 đã gộp main): lead đã chép
hai tệp `ngan.py`, `cau_hinh.py` vào gói, Codex giữ nguyên. Sửa tích hợp trong
`chay.py` và khai báo SDK 2.1; cấu hình khóa `{}`, dict trực tiếp; test so
SHA-256 cả hai tệp sau chuẩn hóa CRLF→LF, không skip. Không sửa `_chung/**`.

DOCX độc lập với cấu hình ngân sách AI. Chỉ bước cần ngân sách (TX-2)
mới bắt buộc bản ghi cấu hình; không tự tạo bản ghi để làm xanh DEMO.
Vị trí DOCX theo khối/đoạn/Điều/Khoản và offset Unicode; không có trang/hộp giả.
Schema chung được chép nguyên byte. Không AI/OCR/mạng ngoài, 0 Cloud.
