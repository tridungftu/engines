# VIỆC — danh sách việc duy nhất của project `e_hoa_don`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | Xin Anh **quyết định cuối** cho phiếu (9 lát, 29 giờ công ước tính) | — | Chờ Anh |  |
| 2 | G3-GOI-25: nguồn Node bảng kê trong gói | HD-2 | Chờ Anh | Quyền chép nguồn |
| 3 | HD-CONG-BO: mẫu ZIP/bảng kê | HD-5 | Chờ Anh |  |
| 4 | HD-NOI-PHIEN, HD-WIN: phiên Windows/Chromium thật | HD-3, 4 | Chờ Anh | Tài khoản Windows |
| 5 | HD-NOI-CORE, HD-GIAO-DIEN, HD-SO-TIEN, G3-GOI-26, HD-TONG | HD-6…10 | Chờ làm |  |

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).
