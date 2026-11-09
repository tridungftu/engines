# VIỆC — danh sách việc duy nhất của project `e_ocr`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | Đóng gói độc lập theo cổng chung; thay hàm SDK riêng `ocr_*_luot` bằng lượt bền chung khi Core có | OCR-6, 13 | Chờ làm |  |
| 2 | Bổ sung dependency cho nguồn dự phòng mask_ocr | OCR-8 | Chờ làm |  |
| 3 | Màn hạn mức ABBYY / trạng thái máy (giao diện của engine) | OCR-8 | Chờ làm |  |
| 4 | Bài máy test ca 1, 3, 8 | OCR-11 | Chờ làm |  |
| 5 | Lát 9: ABBYY thật trên máy hiện tại bằng PDF DEMO (Anh đã cho phép mở kết nối tạm) | OCR-12 | Chờ làm | Không chép `in\ out\ jobs\ state\` |
| 6 | Ghép Core (K1–K6) → nghiệm thu tổng thể | — | Chờ Core |  |

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).
