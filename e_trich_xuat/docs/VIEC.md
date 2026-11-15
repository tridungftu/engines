# VIỆC — danh sách việc duy nhất của project `e_trich_xuat`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | TX-0: sửa bản nháp theo quyết định 15/11; T1/T2, phép đếm T3, ngăn/cấu hình/màn và nguồn E6 | TX-2, 3, 5, 7 | Xong | **15/11/2026** — [TX-0-THIET-KE.md](TX-0-THIET-KE.md); xong cập nhật tài liệu, chưa có số đo model thật/E6. Bản trước PR #4; PR cập nhật: **chờ lead mở** |
| 1 | Tách năng lực thành **chuẩn bị** và **hậu kiểm**; bỏ gọi AI trực tiếp (`ai_chung.py`) | TX-3 | Chờ làm | Theo CD-111 |
| 2 | E2/E5: nhận bộ từ việc của module, đủ metadata module/loại/phiên bản/hash | TX-2, 4, 5 | Chờ làm |  |
| 3 | E6: so từng byte bộ 37 xây dựng (cần tệp ghim `DANH_MUC_THAM_SO.xlsx`) | TX-7 | Chờ làm | `e_trich_xuat/tham-chieu/DANH_MUC_THAM_SO.xlsx`: **lead đã đặt 15/11 (PR #30)** + NGUON/SHA-256, xác nhận không dữ liệu thật theo đợt 2 §4; chưa kiểm E6 |
| 4 | Cung cấp E1 (kiểm Excel) + U1a/U1b cho module dùng lại; module tự đặt màn quản lý bộ tham số | TX-8, 14 | Chờ làm | C1/C2/C4 là việc của module |
| 5 | LHD-02b: bộ nháp thuê đất KCN + 3 hợp đồng DEMO (CRM giữ bộ) | TX-10 | Chờ Anh | Người nghiệp vụ duyệt |
| 6 | G3-GOI-37, N1 (một lần), TRICH-READY, N2 (buổi 17:00 ≤ 30 phút) | TX-12, 13 | Chờ làm |  |

## Cần Core (chuyển lead Core qua Anh)
- **C-TX-01 (14/11/2026):** xác nhận cửa gửi việc module nhận và ghim `tham_so` riêng từng việc (bộ JSON, hash, prompt, phiên bản), kiểm module/pháp nhân; công bố trần chuỗi/byte thực. Không dùng thao tác sửa cấu hình quy trình chung để truyền bộ theo mỗi hợp đồng. Engine API v1 đã khóa, không đề nghị tự thêm đầu vào thứ hai.
- **C-TX-02 (14/11/2026):** xác nhận quyền đọc qua SDK đối với tệp hồ sơ hậu kiểm do bước chuẩn bị tải lên rồi chuyển tham chiếu qua Hỏi AI; giữ tệp/kết quả cùng chuỗi tới khi module lưu/đóng; ca khác quyền và ACK lặp. SDK có `tai_tep_ra`/`mo_tep` nhưng TX-0 chưa kiểm Core thật phần cấp quyền/vòng đời xuyên bước.
- **C-TX-03 (cập nhật 15/11/2026, dài hạn):** đề nghị cửa chung **“trường do tham số quyết định”** (`truong_ra` động theo snapshot). Anh đã chốt đợt 1 bảng loại riêng + Excel, module tự ghép cột; bước xuất trả `truong` tĩnh là thiết kế thích nghi API hiện có, không thêm khóa ngoài manifest 2.0. Payload/schema chi tiết còn cần review.
- **C-TX-04 (15/11/2026):** ngăn và cấu hình/màn theo `_chung/docs/DE-NGHI-SDK-2.1.md` §2–5. Bảng cần: `cau_hinh`, phạm vi `engine`, một bản mặc định, giá trị JSON ≤ 64 KiB, CAS, không hết hạn; chi tiết `TX-0-THIET-KE.md` §6.3. Core thống nhất định danh bản ghi cấu hình hệ thống, `phien_ban_cau_hinh`/snapshot/sự kiện đổi; hỗ trợ `KttCore.engine("e_trich_xuat").cau_hinh`. Chờ mẫu NGAN-0 (chưa có trong worktree), tạm RAM qua `chon_ngan`, không tệp cấu hình/kho đĩa. Khi code khai riêng `KHAI-SDK-2.1.json`, không sửa phiếu 2.0. Cấu hình model/IP thuộc Hỏi AI, bộ thuộc module.
- Các quyết định tạm ở `_chung/docs/GIAO-CODEX-THU-TU.md` §2 về tệp cấu hình/kho đĩa/không có màn **đã được Anh thay ngày 15/11**: không lưu gì trên máy, có màn cấu hình engine nạp như màn module; schema chỉ đọc trong gói, giá trị qua ngăn; tệp tạm của việc dọn trong `finally`. Chạy thử DEMO vẫn dùng màn chung Core. TX-0 không sửa Core/SDK và chưa kiểm nối Core thật.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

## Cần phối hợp sau TX-0 — cập nhật 15/11/2026

- **Hỏi AI A-TX-01:** xác minh context hiệu dụng, ngân sách đầu ra/reasoning, cách đếm token và hỗ trợ `$defs` của model đã chọn; không gửi `chuyen_tiep` vào model; thống nhất trích dẫn từng ô với danh sách chung của `tra_loi_ai`. Phiếu AI-1/AI-2/AI-3 chưa đủ bằng chứng rằng phần kiểm context này đã có. Gemma chưa có ID cụ thể, ngữ cảnh máy thật **chưa rõ**.
- **Lead cấp cho TX-4:** `e_trich_xuat/tham-chieu/DANH_MUC_THAM_SO.xlsx` — **lead đã đặt 15/11 (PR #30)**, cùng `tham-chieu/NGUON.md` ghi SHA-256 thực và xác nhận chỉ danh mục tham số. Anh đã chốt nguồn bản review gốc (câu 7), không xin nguồn lại. Băm `05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd` là băm nguồn cũ, phải đối chiếu tệp được cấp, khác thì lead xác minh, không tự đổi ghim. Còn thiếu fixture/đáp án/bản vàng DEMO gồm Track Changes và câu hỏi nguồn. `MAC_DINH` chỉ khảo sát độ dài, không tự tạo Excel thay bản ghim hoặc tuyên bố E6 đạt.
- **T3 đo thật:** chạy lại Phụ lục A có 37 mã, tổng mẫu ngắn 7.865 ký tự/9.578 byte; token vào 1.967/20.971/60.981 vẫn là **ước lượng**. Số lượt AI thật **0**; context/token đầu vào/đầu ra/reasoning/thời gian của Qwen3 8B, gpt-oss 20B, Gemma **chưa đo**. Lead/Anh cấp biên bản máy thật theo thiết kế §5.5 trước kết luận một lượt đủ sức chứa; ID Gemma chưa rõ. Không suy chất lượng N1 từ phép đếm.
- **E6/N1:** thử một yêu cầu 37 trường thay cách hỏi theo nhóm + dò/rà lại của nguồn. Giữ nguyên cổng byte câu hỏi/bảng của E6 và N1 đúng một lần; nếu khác thì báo chưa đạt, trình lại phương án và giờ, không nới tiêu chí. Chưa chuyển bộ mặc định XD sang module.
- **TX-5:** wheel SDK 2.0.0 đã có E1 (`danh_muc_tham_so`), dùng lại qua SDK và bàn giao cho module; không chép thêm một bản kiểm Excel hoặc đặt U1a/U1b trong engine.

## Quyết định đã chốt / phần còn mở — 15/11/2026

| Nội dung | Trạng thái / nơi đối chiếu |
|---|---|
| T1 | **Đã chốt** Cài đặt bước JSON kiểu `van_ban` + băm, câu 5; Core còn cần xác nhận ghim theo việc/quyền/trần byte. Thiết kế §3, TX0-01 |
| T2 | **Đã chốt hướng** bảng loại riêng + Excel, module tự ghép cột và Cần Core “trường do tham số quyết định”, câu 5. Chi tiết payload/schema và bước xuất tĩnh vẫn là **“ĐỀ XUẤT TX-0, chờ Anh”** cuối loại chung, chưa tạo schema mới. TX0-02 |
| T3 | **Đã chốt phải đo thật bằng số**, chưa chốt một lượt luôn đủ. Một yêu cầu đủ trường chỉ là phương án thử; thiếu số máy thật thì chưa kết luận. Không đổi `yeu_cau_ai` thành batch trong TX-0. TX0-03/04 |
| Ngăn / cấu hình / màn | **Đã chốt nguyên tắc** câu 1, 2, 13; engine không lưu trên máy, tạm RAM qua Ngan, màn cấu hình engine. Bảng cấu hình theo thiết kế §6.3/C-TX-04. Hồ sơ hậu kiểm giữ ở kho tệp Core, còn cần xác nhận quyền/vòng đời, không đưa toàn văn vào ngăn cấu hình |
| E6 | **Nguồn đã chốt**, câu 7; lead đã đặt tệp (PR #30) ở `tham-chieu/` theo đợt 2 §4. Chưa kiểm E6, giữ nguyên tiêu chí 07/11 |
| Câu hỏi thêm / TT-21 | Đề xuất tối đa 5 câu; chưa duyệt chỉ nhận mảng rỗng. Giữ mô tả bộ 37, chưa tự sửa mâu thuẫn “suy ra” của TT-21 với chỉ dẫn cũ. TX0-06 |
| Ước giờ | **Còn mở:** TX-1…TX-6 **37 giờ công ước tính** (8/7/8/4/3/7), tăng 11 so 26 của lead, tăng 2 so nháp 35 để thêm ngăn/cấu hình/màn. Ngoài Core/module/AI, chờ máy và làm lại khi E6 không đạt. Lead tách TX-1a/1b nếu vượt ~5 tệp mã. TX0-07 |

## Phần đề xuất lưu trữ sau chuyển đổi — chưa chuyển, không xóa

Giữ nguyên toàn bộ `ma-nguon/`, `tu-core-cu/`, `tests-tu-core/`, shim và schema chung trong TX-0. Khi lead xác nhận thay thế/không còn consumer, đề xuất lưu bản lịch sử của vỏ socket trong `tich_hop.py`/`chay.py`, adapter gọi AI `ai_chung.py`/`tham_so._ai_legacy`, đường catalog máy cũ, CRUD danh mục/đọc `YEU_CAU_THEM.txt`, phần cập nhật `DANH_MUC_HD`/sửa tay của `vendor/review/xuat.py` và pipeline lặp trong `quy_trinh.py`. Chỉ tách phần không dùng; giữ thuật toán/chuẩn chấm còn cần đối chiếu. Bộ 37 chỉ đề xuất lưu trữ **sau E6 đạt**; bộ DV 30 và mẫu DV theo quyết định cuối, không đổi nhãn thành KCN để dùng lại nghiệp vụ.

## Bằng chứng cập nhật TX-0 — 15/11/2026, PR: chờ lead mở

| Kiểm / lệnh thật (Python `.venv/Scripts/python`, dùng `-B`) | Kết quả / giới hạn |
|---|---|
| Môi trường / wheel | Python **3.13.14**, SDK **2.0.0**; pip `--no-index --no-deps` xác nhận đúng bản, SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Dùng lại venv, không tải mạng |
| Phụ lục A / phiếu nháp | **37 mã**, số ký tự/byte/băm trùng bản nháp; 1.967/20.971/60.981 token vào **ước lượng**; khuôn 2.000 byte, bộ 11.216 byte. `kiem_phieu` → **0 lỗi, 4 năng lực**; không phải DEMO runtime |
| `-m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **exit 1**: không đọc được phiếu `engine.json`, vì TX-0 không có gói. **Chưa có x/x DEMO ĐẠT**, không có CoreGia được chạy |
| `-m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp` | Venv ban đầu thiếu pytest; dùng pytest có sẵn trên máy qua `PYTHONPATH` tạm → **exit 4**, chưa có `e_trich_xuat/tests`, **no tests ran**. Không cài thêm dependency runtime |
| `e_trich_xuat/tests/kiem_doc_lap.py` | **exit 2**: chưa có tệp, chưa kiểm độc lập gói mới |
| `-m pytest e_trich_xuat/ma-nguon/tests -q --basetemp=.pytest-tmp` | **3 passed, 1 failed**: test cũ kỳ vọng tên thư mục `e_trich_xuat` nhưng nay là `ma-nguon`. Không sửa nguồn/test chỉ đọc |
| `-m pytest e_trich_xuat/tests-tu-core e_trich_xuat/tu-core-cu/tests -q --basetemp=.pytest-tmp --tb=no` | **15 errors during collection**. Kiểm nguyên nhân bằng `--collect-only --tb=short` → **35 tests collected, 15 errors, exit 2**; thiếu module/fixture Core cũ và đường SQL cũ, chưa chạy được nhóm tham chiếu |
| Rà tài liệu cuối | **Đạt**: bốn tệp Markdown UTF-8 nghiêm ngặt, không BOM, NFC, không khoảng trắng cuối dòng, hàng rào Markdown cân bằng, các khối JSON đúng cú pháp; `git diff --check` **exit 0**. Hai chuỗi DOCX/OCR khớp manifest Hỏi AI/OCR hiện có; bốn loại chung trước §4 và Phụ lục A giữ nguyên. Chỉ sửa bốn tài liệu, không tạo gói/schema/XLSX, không sửa mã nguồn/Core/SDK |

Pytest dùng bản cài sẵn trên máy với `PYTHONPATH` chỉ trong tiến trình kiểm; đã bỏ biến sau kiểm, tắt plugin tự nạp và bytecode. Không tính test chưa chạy là skipped, không báo 0 lỗi. **Kết luận kiểm runtime: chưa đạt/chưa áp dụng cho lát tài liệu chưa có gói**; chưa kiểm CoreGia/Core thật, E6 hoặc N1. Thiết kế đã cập nhật theo hướng Anh chốt; phần số đo model thật và chi tiết contract còn mở đã ghi ở trên.

Thời gian phiên cập nhật 15/11/2026 (UTC+07): bắt đầu **07:29:00** theo lead, chốt kiểm tài liệu **07:40:11**; thực tế **0,19 giờ** so phiếu TX-0 **3 giờ ước tính**. Bản nháp 14/11 đã ghi riêng **0,32 giờ** phía dưới; tổng hai phiên khoảng **0,51 giờ**, không tính là công thực hiện TX-1…TX-6. Lệch khỏi nháp: đề xuất sau TX-0 tăng **35 → 37 giờ** để tính ngăn/cấu hình/màn; dùng lại pytest có sẵn để chạy test tham chiếu, không sửa mã nhằm xử lý lỗi ngoài phạm vi. Không commit/push; PR cập nhật: **chờ lead mở**.

## Bằng chứng bản nháp TX-0 — lịch sử 14/11/2026

| Kiểm | Kết quả thật / phạm vi |
|---|---|
| Môi trường | `.venv` trong worktree, Python **3.13.14**; cài wheel `--no-index --no-deps`, SDK in **2.0.0**. SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp `SHA256SUMS.txt` |
| Đếm DEMO, chạy Phụ lục A | **37 mã duy nhất**; prompt 3.638 ký tự, DEMO 2.227, khuôn 2.000 → **1.967 token ước lượng** (ký tự/4, làm tròn tổng). DEMO-20/60: 20.971/60.981 token vào ước lượng. Khuôn 2.000 byte ≤ 32 KiB; bộ 11.216 byte ≤ 64 KiB; không có số đo AI/N1 |
| Phiếu nháp trong Markdown | `kho_tri_thuc_sdk.engine.kiem_phieu` → **0 lỗi**, 4 năng lực, 4 loại riêng khai đúng tên; chỉ kiểm cấu trúc, chưa kiểm gói/entrypoint/DEMO runtime |
| Nhóm nguồn | Tái lập quy tắc `GROUP_MAX=8` trên `MAC_DINH` → **9 nhóm**: `8,1,5,3,3,4,3,7,3`; không chạy pipeline/AI |
| Ba lệnh AGENTS.md §5 | **Không áp dụng, không chạy** theo ghi chú lead: TX-0 chỉ tài liệu, chưa có `e_trich_xuat/goi/` và test mới. Không báo số passed/skip hoặc CoreGia giả |
| Kiểm tài liệu/diff cuối | Hai chuỗi DOCX/OCR khớp kiểu, cuối trả `truong`; 3 khối JSON đề xuất đúng cú pháp; dẫn chứng DEMO `[405:471]` khớp nguyên văn. Cả 3 tài liệu UTF-8 nghiêm ngặt, không BOM, NFC, không khoảng trắng cuối dòng; `git diff --check` **mã 0**. Nội dung loại chung cũ giữ nguyên; chỉ sửa/thêm đúng 3 tệp Markdown, không sửa mã/API/schema, không tạo `goi/` |

Thời gian: bắt đầu **14/11/2026 22:40:00** (UTC+07, theo lead), chốt kiểm tài liệu lúc **14/11/2026 22:59:17**; thực tế **0,32 giờ** so với phiếu TX-0 **3 giờ công ước tính**. Số thực tế là thời gian phiên TX-0, không phải giờ thực hiện TX-1…TX-6. Không commit/push; lead commit và mở PR.
