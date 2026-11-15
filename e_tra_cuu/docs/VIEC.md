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
| TC-P | Lập phiếu giao Codex theo SDK 2.0, chỉ tài liệu | Anh giao 15/11/2026; QĐ 15/11 câu 12 | Xong — 15/11/2026 | `GIAO-CODEX-e_tra_cuu.md`: 12 lát TC-0…TC-11, 45 giờ công ƯỚC TÍNH; TC-P 1 giờ ƯỚC TÍNH ngoài tổng; đề xuất loại `ho_so_tra_cuu` ở cuối tài liệu loại chung; PR: **chờ lead mở** |

**Phạm vi sau TC-P (15/11/2026):** các mã TC ở dòng 1–5 của bảng cũ là mã lịch sử từ DAC-TA §14, không phải lát code mới. Dùng bảng §3 của `GIAO-CODEX-e_tra_cuu.md` làm phiếu giao mới: TC-0 = khung SDK 2.0 + Ngan/cấu hình + kiem_doc_lap + KHAI-SDK-2.1; khảo sát PostgreSQL/kho/cache/SDK JS/nạp hàng loạt vẫn thuộc Core. Chưa giao hoặc làm TC-0…TC-11. Không có `ma-nguon/`, `goi/`, `tests/`, quyết định cuối/phiếu riêng trong worktree; không tạo chúng ở TC-P.

**Chờ Anh:** toàn bộ câu còn mở được gom **một bảng chọn duy nhất** TC-Q01…TC-Q15 tại phiếu §5.2; bảng này thay cách theo dõi “9 câu” ở dòng 6, không coi đề xuất là quyết định. TC-Q13 chặn kích hoạt schema/loại mới TC-1 trở đi; TC-Q14 chặn nhãn Xanh thật. Các chính sách vận hành chưa chốt không chặn khung/DEMO.

**Kiểm TC-P:** theo ngoại lệ riêng của lát chỉ tài liệu, không áp dụng ba lệnh engine AGENTS.md §5 khi chưa có gói/tests. Kiểm 12/12 khối lệnh §4 bằng regex Anh yêu cầu (fence mở ``` trơn), đủ TC-0…TC-11, không trùng, tổng giờ bảng = 45; `git diff --check` không lỗi. SDK 2.0.0 cài offline trong `.venv`, SHA-256 wheel khớp SHA256SUMS.txt. Chỉ kiểm tài liệu và đọc mã SDK, **chưa chạy engine/CoreGia**. Không commit/push; không tạo `goi/`, không sửa nguồn cũ.

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Bổ sung từ TC-P — 15/11/2026

- **C-TC-01:** SDK 2.1 ngăn/cấu hình/UI và CLI/CoreGia nạp cấu hình/tệp DEMO. Mẫu NGAN-0 đã có; TC-0 chép nguyên hai tệp, so băm CRLF→LF; RAM không phải lưu bền. Cấu hình đúng khóa `{}`; không `cau_hinh_may`/`kho_tam` cũ.
- **C-TC-02:** cửa chung ghép nguồn nhiều bước và cấp quyền tệp con xuyên bước/ACK, điều phối nhánh OCR/Local/TX. Runtime thiếu thì từ chối; không tự gọi engine/CSDL/đường máy. Chưa chứng minh runner 2.0 có fan-in.
- **C-TC-03:** danh mục/hàm/bằng chứng duyệt và ngữ cảnh thời điểm/quyền tin cậy; RLS pháp nhân + nhóm + người trước khi nguồn tới engine/AI. Băm/cờ tự khai không chứng minh quyền. Phạm vi M9/07 chỉ Local do Core thực thi; test CoreGia không chứng nhận quyền thật.
- **C-TC-04:** Kho tài liệu/pgvector/tìm lai/cache và hết hạn khi nguồn/duyệt/công bố/quyền đổi, K5/ba tầng/SDK JS thuộc Core. Engine chỉ trả kết quả/nguồn/thực thể/cờ; không lập kho thứ hai hoặc tuyên bố cache/K5 đã lưu.
- **C-TC-05:** SDK log an toàn, giới hạn loại riêng, lease/lỗi trần. Đã đọc wheel: `Viec.mo_tep` dùng trần tệp chung của bước; phiếu khai 20 MiB và tự kiểm JSON chính 1 MiB, không sửa private SDK. Tách trần từng tệp chỉ là đề nghị SDK sau này, không cần lách cổng hiện tại.
- **L-TC-01/02:** lead giao bổ sung embedding Local của Hỏi AI, nguồn vị trí/bảng OCR, Trích xuất trường mục tiêu và adapter bằng chứng đã duyệt; phân định dịch vụ Kho tài liệu theo G14, cấp bộ câu hỏi/đáp án DEMO nghiệp vụ. TC không sửa các engine khác.
- Chi tiết cửa/chặn/làm tạm: phiếu §5.1. Đề xuất `ho_so_tra_cuu` **chưa duyệt**, không tạo schema ở TC-P. Chưa có số đo model/context/chất lượng hay kiểm Core thật; công cụ thử thật ở lát cuối TC-11 do Anh tự chạy.
