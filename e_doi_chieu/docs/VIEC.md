# VIỆC — danh sách việc duy nhất của project `e_doi_chieu`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | DC-0: khảo sát ABBYY (tọa độ từ, cờ nghi ngờ), từ điển tiếng Việt, cách phát hiện sửa tay; dựng bộ mẫu | — | Chờ làm |  |
| 2 | DC-1: đọc DOCX, chuẩn hóa, kiểm trang, căn đoạn, so 2 lượt, quy tắc cứng | DC-a…g | Chờ làm |  |
| 3 | DC-2: lệch dấu 5 bước + dùng `ocr.trich_vung@1` + phân loại qua chuỗi (Local) | DC-f, h | Chờ làm |  |
| 4 | DC-3: phát hiện vùng sửa tay | DC-j | Chờ làm |  |
| 5 | Schema `loi_doi_chieu`, quy trình, sự kiện chặn/mở chặn | DC-l | Chờ Core |  |
| 6 | 8 câu trả lời sau (đặc tả §13) | — | Chờ Anh |  |
| DC-P | Lập phiếu giao Codex theo SDK 2.0 và quyết định 15/11 | DC-a…n | Xong — 15/11/2026 | PR: **chờ lead mở**. Phiếu `GIAO-CODEX-e_doi_chieu.md`: 14 lát DC-0…DC-13, 57 giờ **ƯỚC TÍNH**, bảng độ khó và 14 khối lệnh; 17 câu chọn gom duy nhất tại §5.2. Chỉ tài liệu, chưa tạo gói/chưa code; chờ duyệt thiết kế và giao từng lát. |

**Cập nhật sau DC-P:** hàng 0…6 phía trên giữ làm lịch sử cách chia lát cũ, không dùng để giao code. Mã DC-0…DC-13 và phụ thuộc hiện hành theo phiếu mới §3; 8 nhóm câu cũ đã tách/gom thành DC-Q01…DC-Q17 (§5.2), chưa phải 17 quyết định đã chốt. Mọi trạng thái triển khai vẫn Chờ làm/Chờ Core/Chờ Anh tương ứng.

- Kiểm kê 15/11: không có `ma-nguon/`, `goi/`, `tests/`, `QUYET-DINH-CUOI-*`, `PHIEU-ENGINE-*.md` trong engine; không truy cập mã K2 ngoài workspace, không có mã cũ tại chỗ để port.
- Đề xuất loại `ho_so_doi_chieu` đã ghi **ĐỀ XUẤT DC-P, chờ Anh** ở cuối `_chung/docs/LOAI-DU-LIEU-RIENG.md` §5; chưa tạo schema/kích hoạt. Tái dùng nguyên ba loại `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`; không đổi `bang_trich_xuat`.
- Quy tắc mới: không lưu gì bền trên máy engine; cấu hình/chỉ mục/danh mục/xác nhận qua `Ngan`, snapshot/ảnh/báo cáo qua kho tệp Core; màn trong `goi/e_doi_chieu/ui/`. Không dùng `cau_hinh_may`/`kho_tam` cũ.
- Kiểm DC-P ngày 15/11/2026: regex theo yêu cầu đọc **14/14 khối** §4 (DC-0…DC-13, fence mở trơn); đủ §1…§5; tổng bảng **57 giờ ƯỚC TÍNH**; bảng chọn **17 mã duy nhất**; `git diff --check` mã thoát 0; phạm vi đúng **3 tệp Markdown**, không tạo `goi/`, `ma-nguon/`, `tests/`. Ba lệnh AGENTS.md §5 **không áp dụng cho lát chỉ tài liệu**, theo yêu cầu riêng DC-P; không ghi kết quả CoreGia hoặc test engine như đã chạy.

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

**Bổ sung DC-P — 15/11/2026 (PR: chờ lead mở):** mục cổng chung cũ ở trên là lịch sử, chưa được kiểm lại Core thật. Chi tiết cửa cần hiện hành tại phiếu §5.1:

| Mã | Thiếu / yêu cầu cửa chung | Ảnh hưởng và cách làm tạm |
|---|---|---|
| C-DC-01 | NGAN-0 và SDK 2.1: ngăn lô/CAS/duy nhất/phạm vi, cấu hình, nạp màn | `_chung/mau-ma/` chưa có trong worktree lúc lập phiếu; DC-0 chờ lead gộp mẫu. Sau đó RAM/KttCore giả; bản khai riêng KHAI-SDK-2.1, không thêm khóa mới vào manifest 2.0 |
| C-DC-02 | Ghép hai tài liệu/tệp con, quyền/vòng đời giữa bước, Local-only và điều phối OCR lại/bỏ qua AI | CoreGia + adapter test; runtime thiếu quyền/nguồn từ chối. Không đọc đĩa, không tự gọi engine khác/fan-in |
| C-DC-03 | Xác nhận chỉ-thêm, danh tính/giờ/quyền tin cậy, CAS/chống trùng; quyền xem hồ sơ/duyệt từ điển | Chỉ mô phỏng khi chưa có cửa; UI không ghi ngăn trực tiếp để vượt kiểm quyền. RAM không chứng minh lưu bền/xác nhận thật |
| C-DC-04 | Cửa sự kiện/mapping module cho chặn/mở hiệu lực, giữ tầng 1, thông báo và chưa kiểm được | Engine trả kết quả/cờ, module quyết định trạng thái. Không tự tạo route, schema SQL hoặc phát sự kiện riêng |
| C-DC-05 | Lead OCR chốt OCR vùng SDK 2.0, tọa độ/cờ nghi ngờ/ảnh; nguồn phân trang Word nếu có | Chưa có bằng chứng giữ Cần xem/chưa kiểm; không bịa trang/hộp hoặc coi mã OCR vùng cũ là đã tích hợp |
| C-DC-06 | Log SDK an toàn, kiểm trần sâu loại riêng, lease và ánh xạ lỗi trần tệp theo SDK 2.1 §7 | Tự kiểm sâu và log mã chung; giữ nợ SDK rõ, không sửa SDK/Core trong engine |

Nguồn lead cần cấp L-DC-01: mẫu ngăn, từ điển/font/detector có nguồn/băm/giấy phép và dependency offline; K2 chỉ khi lead cung cấp bản tham chiếu trong workspace. Thiếu nguồn dùng DEMO để test giao thức, không coi là detector/từ điển đã đạt.
