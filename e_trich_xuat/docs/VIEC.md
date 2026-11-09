# VIỆC — danh sách việc duy nhất của project `e_trich_xuat`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | Tách năng lực thành **chuẩn bị** và **hậu kiểm**; bỏ gọi AI trực tiếp (`ai_chung.py`) | TX-3 | Chờ làm | Theo CD-111 |
| 2 | E2/E5: nhận bộ từ việc của module, đủ metadata module/loại/phiên bản/hash | TX-2, 4, 5 | Chờ làm |  |
| 3 | E6: so từng byte bộ 37 xây dựng (cần tệp ghim `DANH_MUC_THAM_SO.xlsx`) | TX-7 | Chờ làm | Thiếu tệp ghim |
| 4 | Cung cấp E1 (kiểm Excel) + U1a/U1b cho module dùng lại; module tự đặt màn quản lý bộ tham số | TX-8, 14 | Chờ làm | C1/C2/C4 là việc của module |
| 5 | LHD-02b: bộ nháp thuê đất KCN + 3 hợp đồng DEMO (CRM giữ bộ) | TX-10 | Chờ Anh | Người nghiệp vụ duyệt |
| 6 | G3-GOI-37, N1 (một lần), TRICH-READY, N2 (buổi 17:00 ≤ 30 phút) | TX-12, 13 | Chờ làm |  |

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).
