# VIỆC — danh sách việc duy nhất của project `e_phan_luong`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng). Giờ là **ước tính của lead, chưa đo**. Lead (Claude) cập nhật tệp này khi gộp; Codex làm việc con không sửa tệp này (GIAO-CODEX §2.1).

| # | Việc | Lát | Trạng thái | Người làm | Chờ Anh? | Giờ (ước tính) | Ghi chú |
|---|---|---|---|---|---|---:|---|
| 0 | Phiếu engine (Anh duyệt 20/11), phiếu giao Codex, `kieu.py`, `loi.py`, kiểm 2 điểm Cần Core bằng đọc mã | PL-P | Xong — 20/11/2026 | Lead | Không | — | Kết quả kiểm: GIAO-CODEX §4 |
| 1 | Khung gói, `engine.json`, SQL 6 bảng + kiểm kê, `ngan_chung.py`, kiểm độc lập, test Cần Core bằng CoreGia | PL-0 | Đang làm — 20/11/2026 | Codex | Không (Q1, Q2 đã chốt) | 3 | |
| 2 | Bộ DEMO 500 nghiệp vụ, đáp án lớp 1, AI giả `tra_loi_ai` | PL-0B (PR PL-0) | Đang làm — 20/11/2026 | Codex | Không | 1 | |
| 3 | `tien.py`, `doc_lo.py` | PL-1A (PR PL-1) | Đang làm — 20/11/2026 | Codex | Không | 2 | |
| 4 | `nguong.py`: ngưỡng, lớp 1, chia nhỏ trong lô | PL-1B (PR PL-1) | Đang làm — 20/11/2026 | Codex | Không (Q3 đã chốt) | 2 | |
| 5 | `tu_khoa.py`, `phan_loai.py` | PL-1C (PR PL-1) | Đang làm — 20/11/2026 | Codex | Không | 2 | |
| 6 | `thong_ke.py` (Clopper-Pearson), `ty_le.py`, `doi_bac.py` | PL-2A (PR PL-2, `doi_bac` vào PR PL-3) | Đang làm — 20/11/2026 | Codex | Không | 3 | |
| 7 | `co.py`, `chon_mau.py` (SHA-256) | PL-2B (PR PL-2) | Đang làm — 20/11/2026 | Codex | Không (Q4 đã chốt) | 2 | |
| 8 | `ket_qua.py`: JSON kết quả kiểm, mức sai, nguồn mẫu | PL-3A (PR PL-3) | Đang làm — 20/11/2026 | Codex | Không (Q1, Q2, Q7 đã chốt) | 2 | |
| 9 | Ghép lớp 1 + phân loại (`phan_luong.py`) | PL-1 | Chờ làm | Codex | Không | 1 | Sau PL-0, PL-1A/B/C |
| 10 | Ghép lớp 2 + 3, năng lực `audit.phan_luong@1`, ngăn lượt, `tep_json` | PL-2 | Chờ làm | Codex | Không (Q4, Q5 đã chốt) | 2 | Sau PL-1 |
| 11 | Năng lực `audit.ghi_ket_qua@1`, CAS thử lại | PL-3 | Chờ làm | Codex | Không (Q1, Q2, Q6 đã chốt) | 2 | Sau PL-1; song song PL-2 ghép |
| 12 | **Dừng, báo Anh bản dùng được với JSON** | — | Chờ làm | Lead | Có | — | Trước PL-4 |
| 13 | Hồ sơ hành vi, chốt kỳ tháng, chia nhỏ qua lô | PL-4 | Chờ làm | Codex | Sau báo cáo PL-3 | 4 | |
| 14 | Chuỗi Local AI: `chuan_bi_phan_loai`, `phan_luong_sau_ai` | PL-5 | Chờ làm | Codex | Sau báo cáo PL-3 | 6 | Theo GIAO-CODEX §2.5 |
| 15 | Excel/CSV theo khuôn cột | PL-6 | Chờ làm | Codex | Sau báo cáo PL-3 | 4 | |
| 16 | `phan_luong_hoa_don` | PL-7 | Chờ làm | Codex | Sau báo cáo PL-3 | 4 | |
| 17 | Tệp JSON, Excel danh sách Đỏ, màn `ui/bang_ty_le.js` | PL-8 | Chờ làm | Codex | Sau báo cáo PL-3 | 5 | |
| 18 | Mô phỏng 12 tháng, test C4/C5, đo hiệu năng, kiểm độc lập, đóng gói, danh mục | PL-9 | Chờ làm | Codex | Sau báo cáo PL-3 | 3 | |
| | **Cộng** | | | | | **48** | Giờ phiếu §9; việc con chia lại trong cùng tổng |

## Chờ Anh
- Q1–Q7: **Anh đã chốt 20/11/2026** (bảng GIAO-CODEX §4): Q1 module gửi kèm ngưỡng trong JSON kết quả; Q2 thêm `loai`, `nguon_loai` vào `dong_luot`; Q3 số âm so giá trị tuyệt đối; Q4 dưới SAD nhân hệ số cờ; Q5 Đỏ chưa có kết quả kiểm thì giữ `NOP_LAI`; Q6 đang 100% chỉ lỗi ≥ TE mới đếm lại; Q7 `so_tien_sai` khác tiền tệ ngưỡng thì từ chối.
- Không còn câu chặn.

## Cần Core
- **CC-1 (PL-0, 20/11):** SDK 2.2.0 chưa có hàm JS `nut.chay` để module chạy nút bằng tệp tự lập; module dùng tạm `api.goi({tep: File})`. Cần Core phát hành hàm này trong SDK cho module, và chạy thật một lần trên Core tập. Kết luận cơ chế: **được** (đọc mã Core, chưa chạy thật).
- **CC-2 (PL-0, 20/11):** `mo_tep` tệp do bước trước tải lên: Core thật chỉ cho khi đầu vào bước có **đối tượng có khóa `tep_id`** và tệp cùng việc; CoreGia so chuỗi con, kho tệp toàn cục → **không cùng ngữ nghĩa**. Cần Core: sửa CoreGia cho khớp Core thật; chạy thật chuỗi 3 bước trên Core tập. Engine làm theo GIAO-CODEX §2.5.
- **CC-3 (PL-0, 20/11):** `hat_giong` để trường thường (phiếu §6); nếu muốn mã hóa sau thì cần đường giải mã cho màn engine (Admin).
