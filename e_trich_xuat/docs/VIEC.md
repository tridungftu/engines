# VIỆC — danh sách việc duy nhất của project `e_trich_xuat`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | TX-0: khảo sát mã, trả lời T1–T3, phiếu SDK 2.0 nháp và ước giờ để trình Anh | TX-2, 3, 5 | Xong | 14/11/2026 — [TX-0-THIET-KE.md](TX-0-THIET-KE.md); hoàn tất tài liệu, chờ Anh chốt thiết kế trước TX-1. PR: **chờ lead mở** |
| 1 | Tách năng lực thành **chuẩn bị** và **hậu kiểm**; bỏ gọi AI trực tiếp (`ai_chung.py`) | TX-3 | Chờ làm | Theo CD-111 |
| 2 | E2/E5: nhận bộ từ việc của module, đủ metadata module/loại/phiên bản/hash | TX-2, 4, 5 | Chờ làm |  |
| 3 | E6: so từng byte bộ 37 xây dựng (cần tệp ghim `DANH_MUC_THAM_SO.xlsx`) | TX-7 | Chờ làm | Thiếu tệp ghim |
| 4 | Cung cấp E1 (kiểm Excel) + U1a/U1b cho module dùng lại; module tự đặt màn quản lý bộ tham số | TX-8, 14 | Chờ làm | C1/C2/C4 là việc của module |
| 5 | LHD-02b: bộ nháp thuê đất KCN + 3 hợp đồng DEMO (CRM giữ bộ) | TX-10 | Chờ Anh | Người nghiệp vụ duyệt |
| 6 | G3-GOI-37, N1 (một lần), TRICH-READY, N2 (buổi 17:00 ≤ 30 phút) | TX-12, 13 | Chờ làm |  |

## Cần Core (chuyển lead Core qua Anh)
- **C-TX-01 (14/11/2026):** xác nhận cửa gửi việc module nhận và ghim `tham_so` riêng từng việc (bộ JSON, hash, prompt, phiên bản), kiểm module/pháp nhân; công bố trần chuỗi/byte thực. Không dùng thao tác sửa cấu hình quy trình chung để truyền bộ theo mỗi hợp đồng. Engine API v1 đã khóa, không đề nghị tự thêm đầu vào thứ hai.
- **C-TX-02 (14/11/2026):** xác nhận quyền đọc qua SDK đối với tệp hồ sơ hậu kiểm do bước chuẩn bị tải lên rồi chuyển tham chiếu qua Hỏi AI; giữ tệp/kết quả cùng chuỗi tới khi module lưu/đóng; ca khác quyền và ACK lặp. SDK có `tai_tep_ra`/`mo_tep` nhưng TX-0 chưa kiểm Core thật phần cấp quyền/vòng đời xuyên bước.
- **C-TX-03 (14/11/2026, dài hạn):** `truong_ra` động theo snapshot. Đợt 1 đề xuất `bang_trich_xuat` + `trich.xuat_ket_qua@1` trả `truong` tĩnh, không thêm khóa ngoài manifest 2.0.
- Các cửa chung K1–K5, Chạy thử DEMO và cấu hình theo `_chung/docs/GIAO-CODEX-THU-TU.md`; SDK/API v1 đã có hợp đồng. TX-0 không coi tài liệu khảo sát 08/11 là bằng chứng các cửa đó vẫn chưa làm; chưa có kiểm nối Core thật. Không làm màn riêng cho engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

## Cần phối hợp sau TX-0 — 14/11/2026

- **Hỏi AI A-TX-01:** xác minh context hiệu dụng, ngân sách đầu ra/reasoning, cách đếm token và hỗ trợ `$defs` của model đã chọn; không gửi `chuyen_tiep` vào model; thống nhất trích dẫn từng ô với danh sách chung của `tra_loi_ai`. Phiếu AI-1/AI-2/AI-3 chưa đủ bằng chứng rằng phần kiểm context này đã có. Gemma chưa có ID cụ thể, ngữ cảnh máy thật **chưa rõ**.
- **Lead cấp cho TX-4:** `DANH_MUC_THAM_SO.xlsx` đúng SHA-256 `05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd`, fixture/đáp án/bản vàng DEMO gồm Track Changes và câu hỏi nguồn. Chưa có tệp ghim/fixture tại đường test cũ trong worktree. `MAC_DINH` chỉ dùng khảo sát độ dài, không được tự tạo Excel thay bản ghim hoặc tuyên bố E6 đạt.
- **E6/N1:** thử một yêu cầu 37 trường thay cách hỏi theo nhóm + dò/rà lại của nguồn. Giữ nguyên cổng byte câu hỏi/bảng của E6 và N1 đúng một lần; nếu khác thì báo chưa đạt, trình lại phương án và giờ, không nới tiêu chí. Chưa chuyển bộ mặc định XD sang module.
- **TX-5:** wheel SDK 2.0.0 đã có E1 (`danh_muc_tham_so`), dùng lại qua SDK và bàn giao cho module; không chép thêm một bản kiểm Excel hoặc đặt U1a/U1b trong engine.

## Chờ Anh — thiết kế TX-0

| Quyết định | Đề xuất của Codex / nơi đối chiếu |
|---|---|
| T1 | JSON + hash trong snapshot từng việc; Core kiểm quyền và ghim bất biến. `TX-0-THIET-KE.md` §3, TX0-01 |
| T2 và loại mới | `bang_trich_xuat` + bước xuất tĩnh; đề xuất **“ĐỀ XUẤT TX-0, chờ Anh”** đã bổ sung cuối `_chung/docs/LOAI-DU-LIEU-RIENG.md`. Chưa tạo schema mới. TX0-02 |
| T3 | Một yêu cầu đủ trường có điều kiện, không đổi `yeu_cau_ai` thành batch ở đợt này; giữ E6 nguyên điều kiện. TX0-03/04 |
| Hồ sơ hậu kiểm | Giữ tệp tạm Core, chỉ chuyển tham chiếu/băm qua `chuyen_tiep`, cần Core xác nhận quyền/vòng đời. TX0-05 |
| Câu hỏi thêm / TT-21 | Đề xuất tối đa 5 câu; chưa duyệt chỉ nhận mảng rỗng. Giữ mô tả bộ 37, chưa tự sửa mâu thuẫn “suy ra” của TT-21 với chỉ dẫn cũ. TX0-06 |
| Ước giờ | TX-1…TX-6: **35 giờ công ước tính** (6/7/8/4/3/7), tăng 9 so 26 giờ của lead; ngoài Core/module/AI, chờ máy và làm lại khi E6 không đạt. TX0-07 |

## Phần đề xuất lưu trữ sau chuyển đổi — chưa chuyển, không xóa

Giữ nguyên toàn bộ `ma-nguon/`, `tu-core-cu/`, `tests-tu-core/`, shim và schema chung trong TX-0. Khi lead xác nhận thay thế/không còn consumer, đề xuất lưu bản lịch sử của vỏ socket trong `tich_hop.py`/`chay.py`, adapter gọi AI `ai_chung.py`/`tham_so._ai_legacy`, đường catalog máy cũ, CRUD danh mục/đọc `YEU_CAU_THEM.txt`, phần cập nhật `DANH_MUC_HD`/sửa tay của `vendor/review/xuat.py` và pipeline lặp trong `quy_trinh.py`. Chỉ tách phần không dùng; giữ thuật toán/chuẩn chấm còn cần đối chiếu. Bộ 37 chỉ đề xuất lưu trữ **sau E6 đạt**; bộ DV 30 và mẫu DV theo quyết định cuối, không đổi nhãn thành KCN để dùng lại nghiệp vụ.

## Bằng chứng TX-0 — PR: chờ lead mở

| Kiểm | Kết quả thật / phạm vi |
|---|---|
| Môi trường | `.venv` trong worktree, Python **3.13.14**; cài wheel `--no-index --no-deps`, SDK in **2.0.0**. SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp `SHA256SUMS.txt` |
| Đếm DEMO, chạy Phụ lục A | **37 mã duy nhất**; prompt 3.638 ký tự, DEMO 2.227, khuôn 2.000 → **1.967 token ước lượng** (ký tự/4, làm tròn tổng). DEMO-20/60: 20.971/60.981 token vào ước lượng. Khuôn 2.000 byte ≤ 32 KiB; bộ 11.216 byte ≤ 64 KiB; không có số đo AI/N1 |
| Phiếu nháp trong Markdown | `kho_tri_thuc_sdk.engine.kiem_phieu` → **0 lỗi**, 4 năng lực, 4 loại riêng khai đúng tên; chỉ kiểm cấu trúc, chưa kiểm gói/entrypoint/DEMO runtime |
| Nhóm nguồn | Tái lập quy tắc `GROUP_MAX=8` trên `MAC_DINH` → **9 nhóm**: `8,1,5,3,3,4,3,7,3`; không chạy pipeline/AI |
| Ba lệnh AGENTS.md §5 | **Không áp dụng, không chạy** theo ghi chú lead: TX-0 chỉ tài liệu, chưa có `e_trich_xuat/goi/` và test mới. Không báo số passed/skip hoặc CoreGia giả |
| Kiểm tài liệu/diff cuối | Hai chuỗi DOCX/OCR khớp kiểu, cuối trả `truong`; 3 khối JSON đề xuất đúng cú pháp; dẫn chứng DEMO `[405:471]` khớp nguyên văn. Cả 3 tài liệu UTF-8 nghiêm ngặt, không BOM, NFC, không khoảng trắng cuối dòng; `git diff --check` **mã 0**. Nội dung loại chung cũ giữ nguyên; chỉ sửa/thêm đúng 3 tệp Markdown, không sửa mã/API/schema, không tạo `goi/` |

Thời gian: bắt đầu **14/11/2026 22:40:00** (UTC+07, theo lead), chốt kiểm tài liệu lúc **14/11/2026 22:59:17**; thực tế **0,32 giờ** so với phiếu TX-0 **3 giờ công ước tính**. Số thực tế là thời gian phiên TX-0, không phải giờ thực hiện TX-1…TX-6. Không commit/push; lead commit và mở PR.
