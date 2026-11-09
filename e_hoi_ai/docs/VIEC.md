# VIỆC — danh sách việc duy nhất của project `e_hoi_ai`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | Đóng gói độc lập theo cổng chung: bỏ shim, chỉ import SDK, build/cài wheel trên máy sạch | AI-13 | Chờ làm |  |
| 2 | Màn Chạy thử DEMO, Cổng Local AI, Cổng Cloud AI (tắt ở bản 1) thành **giao diện của engine** (không đặt trong Core) | AI-10, 11, 12 | Chờ làm | Bản cũ trong `tu-core-cu\phia-core\` |
| 3 | Tự phát hiện model trên máy AI qua Tailscale, chọn theo module/function | AI-10 | Chờ làm |  |
| 4 | Lát 8: thử thật gpt-oss 20B, Qwen3 8B, Gemma; Local lỗi phải báo rõ, 0 Cloud | AI-14, AI-8 | Chờ làm | Công cụ ở `tu-core-cu\tools\` |
| 5 | Ghép Core khi có cổng chung K1–K5 → bài test cuối 40 phút | AI-18 | Chờ Core |  |
| 6 | Bản 2: công tắc Cloud theo module, qua Mask, đo độ chính xác, kiểm xác suất | AI-21…26 | Chờ (bản 2) |  |

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).
