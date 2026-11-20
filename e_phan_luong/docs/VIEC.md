# VIỆC — danh sách việc duy nhất của project `e_phan_luong`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng). Giờ là **ước tính của lead, chưa đo**. Lead (Claude) cập nhật tệp này khi gộp; Codex làm việc con không sửa tệp này (GIAO-CODEX §2.1).

| # | Việc | Lát | Trạng thái | Người làm | Chờ Anh? | Giờ (ước tính) | Ghi chú |
|---|---|---|---|---|---|---:|---|
| 0 | Phiếu engine (Anh duyệt 20/11), phiếu giao Codex, `kieu.py`, `loi.py`, kiểm 2 điểm Cần Core bằng đọc mã | PL-P | Xong — 20/11/2026 | Lead | Không | — | Kết quả kiểm: GIAO-CODEX §4 |
| 1 | Khung gói, `engine.json`, SQL 6 bảng + kiểm kê, `ngan_chung.py`, kiểm độc lập, test Cần Core bằng CoreGia | PL-0 | Chờ Core — 20/11/2026 | Codex | Không (Q1, Q2 đã chốt) | 3 | Khung xong; đã kiểm bằng Core giả (CoreGia): pytest 33 passed, 0 skipped; kiểm độc lập mã 0; thu mã 1 do chưa có ví dụ thật (CC-4). PR: chờ lead mở. Giữ nguyên kieu.py/loi.py; không tạo demo PL-0B. |
| 2 | Bộ DEMO 500 nghiệp vụ, đáp án lớp 1, AI giả `tra_loi_ai` | PL-0B (PR PL-0) | Xong — 20/11/2026 | Codex | Không | 1 | Gộp vào PR PL-0 (#142). 11 test; sinh lại cùng byte |
| 3 | `tien.py`, `doc_lo.py` | PL-1A (PR PL-1) | Xong — 20/11/2026 | Codex | Không | 2 | PR PL-1. Sửa sau rà: loai rỗng = chưa gán; bộ đọc số chung; 0 thừa |
| 4 | `nguong.py`: ngưỡng, lớp 1, chia nhỏ trong lô | PL-1B (PR PL-1) | Xong — 20/11/2026 | Codex | Không (Q3 đã chốt) | 2 | PR PL-1. Số âm trị tuyệt đối (Q3); ngưỡng {} dùng nguong_json; đọc số chung |
| 5 | `tu_khoa.py`, `phan_loai.py` | PL-1C (PR PL-1) | Xong — 20/11/2026 | Codex | Không | 2 | PR PL-1. Chép cách so từ khóa e_kiem_excel §4.1.1 |
| 6 | `thong_ke.py` (Clopper-Pearson), `ty_le.py`, `doi_bac.py` | PL-2A (PR PL-2, `doi_bac` vào PR PL-3) | Xong — 20/11/2026 | Codex | Không | 3 | PR PL-2 (doi_bac.py cũng vào PR này). Q6 đã sửa; 158 test |
| 7 | `co.py`, `chon_mau.py` (SHA-256) | PL-2B (PR PL-2) | Xong — 20/11/2026 | Codex | Không (Q4 đã chốt) | 2 | PR PL-2. Bỏ tham số tắt hệ số dưới SAD (Q4) |
| 8 | `ket_qua.py`: JSON kết quả kiểm, mức sai, nguồn mẫu | PL-3A (PR PL-3) | Xong — 20/11/2026 | Codex | Không (Q1, Q2, Q7 đã chốt) | 2 | PR PL-3. Q1, Q7; 138 test |
| 9 | Ghép lớp 1 + phân loại (`phan_luong.py`) | PL-1 | Xong — 20/11/2026 | Codex | Không | 1 | PR PL-1. 570 test; thu mã 1 (chưa có ví dụ, CC-4); kiểm độc lập 0. Rà độc lập Sonnet: 0 lỗi cao, 5 điểm đã sửa |
| 10 | Ghép lớp 2 + 3, năng lực `audit.phan_luong@1`, ngăn lượt, `tep_json` | PL-2 | Xong — 20/11/2026 | Codex | Không (Q4, Q5 đã chốt) | 2 | PR PL-2. thu 1/1 ĐẠT mã 0; 929 test; kiểm độc lập 0; tái hiện từng byte; C4/C5; luot ghi sau cùng |
| 11 | Năng lực `audit.ghi_ket_qua@1`, CAS thử lại | PL-3 | Xong — 20/11/2026 | Codex | Không (Q1, Q2, Q6 đã chốt) | 2 | PR PL-3. 1123 test (8 test đầu-cuối); thu 1/1; kiểm độc lập 0. Rà Sonnet: 0 lỗi cao; M1, M3, T1–T5 sửa ở đầu nhánh PL-4 |
| 12 | **Dừng, báo Anh bản dùng được với JSON** | — | Xong — 20/11/2026 | Lead | Có | — | Báo cáo mốc PL-3 gửi Anh trong phiên; Anh yêu cầu làm tối đa nên PL-4…PL-8 chạy song song, chưa gộp main |
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
- **CC-1 (PL-0, 20/11):** SDK 2.2.0 chưa có hàm JS `nut.chay` để module chạy nút bằng tệp tự lập; module dùng tạm `api.goi({tep: File})` theo README gói. Test `test_pl0_can_core.py` nhận byte JSON tự lập rồi mở được bằng CoreGia; **không kiểm multipart/nút JS**. Cần Core phát hành hàm này trong SDK cho module, và chạy thật một lần trên Core tập. Đã kiểm bằng Core giả (CoreGia); chưa chạy Core thật.
- **CC-2 (PL-0, 20/11):** `mo_tep` tệp do bước trước tải lên: test `test_pl0_can_core.py` tải tệp bằng `tai_tep_ra`, truyền nguyên đối tượng trong `tra_loi_ai.chuyen_tiep.phan_luong.tep_lo`, bước sau mở được và kiểm đúng byte/băm. Hàm `co_tham_chieu_tep` để PL-5 dùng lại kiểm hình dạng `$.** ? (@.tep_id == $t)`; test âm chứng minh CoreGia cho chuỗi trơn nhưng hàm nghiêm từ chối. CoreGia có kho tệp toàn cục và mỗi giao việc tạo việc độc lập, nên **chưa chứng minh điều kiện cùng việc/pháp nhân của Core thật**. Cần Core sửa CoreGia cho khớp Core thật và chạy thật chuỗi 3 bước trên Core tập. Đã kiểm bằng Core giả (CoreGia); engine theo GIAO-CODEX §2.5.
- **CC-5 (PL-8B, 20/11):** SDK 2.2.0 (wheel) chưa có `KttCore.engine(ma)` cho màn engine; `ui/bang_ty_le.js` dừng an toàn khi thiếu. Các engine khác (`e_ocr`, `e_mask`, `e_doi_chieu`…) cũng đang dùng cổng này. Cần Core phát hành trong SDK.
- **CC-6 (rà PL-2/PL-3, 20/11):** `viec.ngan.tim` chỉ lọc bằng (=), không lọc theo danh sách giá trị. Xét nộp lại cho lô 50.000 dòng phải gọi `tim` từng mã → có thể vượt `thoi_han_giay`. Cần Core: lọc `ma IN [...]` (hoặc tương đương). PL-9 đo thật trên CoreGia và ghi số.
- **Anh chốt thêm 20/11:** Q8 (không khử trùng riêng khi nộp lại), Q9 (trần 20.000 đối tác/loại), Q10 (dưới SAD khi đang 100% vẫn 2% × hệ số), Q11 (chưa phân loại dưới SAD 2% × hệ số) — GIAO-CODEX §4.
- **CC-3 (PL-0, 20/11):** `hat_giong` để trường thường (phiếu §6); nếu muốn mã hóa sau thì cần đường giải mã cho màn engine (Admin).
- **CC-4 (PL-0, 20/11):** SDK 2.2.0 `doc_phieu` chấp nhận `chay_thu_demo: []`, nhưng CLI `kho_tri_thuc_sdk.thu` in `Phiếu chưa có ví dụ chay_thu_demo.`, mã thoát **1**. PL-0 chưa có năng lực nghiệp vụ chạy thật nên giữ danh sách rỗng, không dựng ví dụ thành công giả. Dừng phần DEMO tại đây theo lệnh giao; cần lead/Core thống nhất nghiệm thu khung hoặc chờ năng lực thật PL-2 thêm ví dụ. Không sửa SDK/hợp đồng.
- **Lưu ý C5 (PL-0, 20/11):** Phiếu §5.5 bắt buộc `ghi_ket_qua.so_cap_doi_bac`, mâu thuẫn phép kiểm mã trường không chứa `bac` tuyệt đối ở lệnh PL-0. Đã nêu để Anh xác nhận; tạm giữ trường số đếm đúng phiếu, test C5 chỉ ngoại lệ đúng cặp năng lực/trường này, không cho trả bậc/tỷ lệ/xác suất. Cần lead xác nhận khi review.
- **Bàn giao PL-0 (20/11):** Bắt đầu 21:00; khung và kiểm xong 21:15 (khoảng 0,25 giờ; PL-0 được tách 3 giờ theo GIAO-CODEX §1, phiếu §9 gộp PL-0/PL-0B 4 giờ). Đã sinh danh mục bằng công cụ, chỉ thêm GHI_CHU cho khung CHUA_LAM; chưa thêm CHUOI vì chưa có năng lực chạy được. Schema chép nguyên byte CRLF nguồn Windows và khóa `-text`; test băm so nguồn chỉ chuẩn hóa CRLF/LF trong RAM để chạy cả Linux (nguồn `_chung` chưa khóa eol), kiểm kê gói vẫn băm bytes nguyên trạng. Khi gộp demo PL-0B phải tính lại `sql/kiem_ke.json` bằng `tests/kiem_bam_goi.py --cap-nhat`. Không commit/push.
- **Lead xác nhận (20/11/2026):** (1) `so_cap_doi_bac` là số lần đổi bậc trong lượt ghi kết quả, đúng phiếu §5.5, không lộ bậc hay tỷ lệ của cặp nào → giữ; test C5 ngoại lệ đúng một trường này. (2) CC-4: PL-0 và PL-1 chưa có năng lực chạy thật nên `thu` mã 1 là đúng thực trạng, không dựng ví dụ giả. Lead mở PR theo chuỗi (PL-1 đặt nền trên nhánh PL-0, PL-2 trên PL-1) và **chỉ gộp vào main khi PL-2 có ví dụ `chay_thu_demo` đạt**, mã thoát 0.
