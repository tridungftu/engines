# VIỆC — danh sách việc duy nhất của project `e_tra_cuu`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | TC-0: khảo sát pgvector/unaccent/pg_trgm trên PostgreSQL; chọn và đo model vector | — | Chờ làm | Chỉ đọc, DEMO |
| 2 | TC-2 (phần engine): `phan_loai_tai_lieu@1`, `cat_doan@1` | §1.2 | Chờ làm |  |
| 3 | TC-3/TC-4 (phần engine): `phan_tich_cau_hoi@1`, `xep_hang_lai@1`, `soan_tra_loi@1` | §1.2 | Chờ làm |  |
| 4 | Bộ câu hỏi mẫu nhóm 02 và bài đo chất lượng | §1.3 | Chờ làm |  |
| 5 | Kho tài liệu, `loi_tra_cuu`, quy trình nạp/hỏi | TC-1 | Chờ Core |  |
| 6 | 9 câu trả lời sau (đặc tả §15) | — | Chờ Anh |  |

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).
