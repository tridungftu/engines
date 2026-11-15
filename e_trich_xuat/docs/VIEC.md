# VIỆC — danh sách việc duy nhất của project `e_trich_xuat`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | TX-0: sửa bản nháp theo quyết định 15/11; T1/T2, phép đếm T3, ngăn/cấu hình/màn và nguồn E6 | TX-2, 3, 5, 7 | Xong | **15/11/2026** — [TX-0-THIET-KE.md](TX-0-THIET-KE.md); xong cập nhật tài liệu, chưa có số đo model thật/E6. Bản trước PR #4; PR cập nhật: **chờ lead mở** |
| TX-P | Hoàn thiện lệnh giao TX-1…TX-6, bảng chọn TX0-06 và độ khó gợi ý | TX-0 §8; quyết định 15/11 | Xong | **15/11/2026** — [GIAO-CODEX-e_trich_xuat.md](GIAO-CODEX-e_trich_xuat.md), sáu khối tự đủ theo dự toán **37 giờ ước tính** (8/7/8/4/3/7), màn cấu hình ở TX-1, công cụ đo T3/N1 ở TX-6 do Anh tự chạy; XLSX E6 đã đặt (PR #30). Chỉ tài liệu; PR: **chờ lead mở** |
| TX-1 | Khung SDK 2.0, ngăn/cấu hình/UI và đọc DOCX/Track Changes | TX-0 §8; TX-15, 12 | Xong | **15/11/2026 — đã nối ngăn chung NGAN-0** (PR #34); **đã kiểm bằng Core giả (CoreGia)**: SDK DEMO **2/2 ĐẠT**, pytest **73 passed, 0 skipped**, Node UI **6/6**, độc lập **exit 0**. Hai test SHA chạy bắt buộc sau CRLF→LF. Tổng TX-1 **8 giờ ước tính**; PR: **chờ lead mở**. Linux/Core thật chưa chạy; SDK 2.1 và màn Core còn cần review |
| TX-2 | Snapshot/hash, prompt/khuôn đủ mã, hồ sơ hậu kiểm tại Core và ngân sách | TX-2, 3, 4, 16, 17 | Chờ Core | **15/11/2026** — xong code/test phần engine; **đã kiểm bằng Core giả (CoreGia)**: pytest **164 passed, 0 skipped**, độc lập **exit 0**, DEMO có ngăn **3/3 ĐẠT**. CLI SDK chuẩn **2/3 ĐẠT, exit 1**, TX-2 `CHUA_CAU_HINH`; trình lead cổng DEMO có ngăn thay thế, C-TX-04. Chưa kiểm Linux/Core thật. **7 giờ ước tính**; PR: **chờ lead mở** |
| TX-3 | Hậu kiểm từng ô, bảng đề xuất và xuất JSON/Excel | TX-3, 5, 6 | Chờ Anh | **15/11/2026** — xong lõi/test DEMO, **chưa đăng ký runtime/schema**, chờ lead/Anh review chi tiết. Sửa kiểm độc lập trong 5 tệp mã, đóng hai nợ TX-2; **đã kiểm bằng Core giả (CoreGia)**. Pytest/CLI/DEMO và đề xuất payload ở biên bản sửa review dưới; **8 giờ ước tính**. PR: **chờ lead mở** |
| TX-4b | E6 giá trị từng mã + dẫn chứng, bộ DEMO chuẩn | TX-7, TX-2/3; quyết định chiều 15/11 | Đang làm | **15/11/2026** — phép đo **2/2 ca, 74/74 mã khớp vàng**, 74/74 dẫn chứng hợp lệ; byte E1/tham số/văn bản trùng. **Chờ lead duyệt** DEMO/vàng, manifest giữ “chờ lead”, E6 exit 2; không làm lại nhiều lượt. **đã kiểm bằng Core giả (CoreGia)**; pytest **412 passed, 0 skipped**, CLI **2/3 ĐẠT, exit 1** (C-TX-04), có ngăn **5/5 ĐẠT**, độc lập **exit 0**. [TX-4-E6.md](TX-4-E6.md); TX-4 **4 giờ ước tính**, TX-4b chưa có dự toán riêng. PR: **chờ lead mở** |
| 1 | Tách năng lực thành **chuẩn bị** và **hậu kiểm**; bỏ gọi AI trực tiếp (`ai_chung.py`) | TX-3 | Đang làm | TX-2 đã có `trich.chuan_bi@1`, không gọi AI; hậu kiểm/xuất còn ở TX-3, theo CD-111 |
| 2 | E2/E5: nhận bộ từ việc của module, đủ metadata module/loại/phiên bản/hash | TX-2, 4, 5 | Xong | **15/11/2026 — TX-2**, snapshot/prompt/cấu hình riêng từng việc đã kiểm bằng Core giả (CoreGia); quyền module/pháp nhân và ghim Core thật còn C-TX-01 |
| 3 | E6: byte E1/văn bản + giá trị 37 mã/dẫn chứng | TX-7 | Đang làm | **15/11/2026 — TX-4b**: băm XLSX/E1 giữ nguyên; hai hợp đồng DEMO tự soạn + vàng độc lập đã đo đạt 74/74; **nghiệm thu chờ lead**, chưa review bố cục PNG vì renderer thiếu pdf2image. Câu hỏi/bảng/phản hồi chỉ tham khảo theo quyết định chiều, không mở nhiều lượt. [TX-4-E6.md](TX-4-E6.md). PR: **chờ lead mở** |
| 4 | Cung cấp E1 (kiểm Excel) + U1a/U1b cho module dùng lại; module tự đặt màn quản lý bộ tham số | TX-8, 14 | Chờ làm | C1/C2/C4 là việc của module |
| 5 | LHD-02b: bộ nháp thuê đất KCN + 3 hợp đồng DEMO (CRM giữ bộ) | TX-10 | Chờ Anh | Người nghiệp vụ duyệt |
| 6 | G3-GOI-37, N1 (một lần), TRICH-READY, N2 (buổi 17:00 ≤ 30 phút) | TX-12, 13 | Chờ làm |  |

## Cần Core (chuyển lead Core qua Anh)
- **C-TX-01 (14/11/2026):** xác nhận cửa gửi việc module nhận và ghim `tham_so` riêng từng việc (bộ JSON, hash, prompt, phiên bản), kiểm module/pháp nhân; công bố trần chuỗi/byte thực. Không dùng thao tác sửa cấu hình quy trình chung để truyền bộ theo mỗi hợp đồng. Engine API v1 đã khóa, không đề nghị tự thêm đầu vào thứ hai.
- **C-TX-02 (14/11/2026):** xác nhận quyền đọc qua SDK đối với tệp hồ sơ hậu kiểm do bước chuẩn bị tải lên rồi chuyển tham chiếu qua Hỏi AI; giữ tệp/kết quả cùng chuỗi tới khi module lưu/đóng; ca khác quyền và ACK lặp. SDK có `tai_tep_ra`/`mo_tep` nhưng TX-0 chưa kiểm Core thật phần cấp quyền/vòng đời xuyên bước.
- **C-TX-03 (cập nhật 15/11/2026, dài hạn):** đề nghị cửa chung **“trường do tham số quyết định”** (`truong_ra` động theo snapshot). Anh đã chốt đợt 1 bảng loại riêng + Excel, module tự ghép cột; bước xuất trả `truong` tĩnh là thiết kế thích nghi API hiện có, không thêm khóa ngoài manifest 2.0. Payload/schema chi tiết còn cần review.
- **C-TX-04 (cập nhật TX-1, 15/11/2026):** ngăn và cấu hình/màn theo `_chung/docs/DE-NGHI-SDK-2.1.md` §2–5. Bảng `cau_hinh`, phạm vi `engine`, khóa `{}`, giá trị trực tiếp là dict cấu hình, CAS `row_version`, không hết hạn; đã khớp quy ước NGAN-0. Core cần thống nhất định danh/bảo đảm một bản ghi, `phien_ban_cau_hinh`, snapshot và `engine.cau_hinh_doi`; hỗ trợ `KttCore.engine("e_trich_xuat").cau_hinh`. Đã có seam đọc một bản, ưu tiên snapshot của việc, test mô phỏng thay đổi không sửa bản cũ; chưa có SDK 2.1 thật. `KHAI-SDK-2.1.json` đã khai riêng, phiếu 2.0 không thêm khóa. Màn export `nap({goc, KttCore})`/default, cổng đọc/lưu `{gia_tri, phien_ban_cau_hinh}`; **lead Core review cách nạp màn và mã màn trước cài**. Model/IP thuộc Hỏi AI, bộ thuộc module.
- **C-TX-05 (mới từ TX-1, 15/11/2026):** SDK 2.0 kiểm MIME/kích thước trước handler, trả `LOAI_TEP_KHONG_NHAN`/câu lỗi khác TX-1; có thể in traceback khi gặp lỗi bất ngờ. Gói kế thừa `Engine.tu_khai_bao`, bọc hẹp `_ket_thuc` chỉ với `trich.doc_docx@1` để trả đúng `TEP_KHONG_HO_TRO`/`VUOT_GIOI_HAN`, bọc `_ghi` để không lộ traceback. Vòng việc/lease/hủy/ACK vẫn do SDK xử lý; không sửa SDK. Cần SDK có hook công khai cho thông điệp lỗi/nhật ký an toàn, lead kiểm lại hai seam nội bộ khi nâng phiên bản.
- **Bổ sung C-TX-04 từ TX-P (15/11/2026):** CLI `kho_tri_thuc_sdk.thu` 2.0 chưa có cửa nạp cấu hình ngăn cho DEMO cần cấu hình. Phiếu giao yêu cầu báo kết quả lệnh chuẩn riêng và thêm `tests/chay_demo_voi_ngan_gia.py` nạp cấu hình DEMO vào `NganBoNho` trước `CoreGia.chay_thu_demo`, trình lead review cổng thay thế trong lúc chờ SDK; không tự tạo cấu hình mặc định trong engine hay dùng tệp cấu hình để làm xanh. Đây là giới hạn cần xử lý ở lát code, TX-P không chạy runtime để chứng nhận.
- **Bổ sung C-TX-04 từ TX-2 (15/11/2026):** đã chạy thật CLI SDK: **2/3 ĐẠT, exit 1**, DEMO `trich.chuan_bi@1` thiếu cấu hình, mã `CHUA_CAU_HINH`. Cổng `tests/chay_demo_voi_ngan_gia.py` nạp cấu hình DEMO bằng lô vào ngăn RAM trước `CoreGia.chay_thu_demo`: **3/3 ĐẠT, exit 0**. Trình lead chấp nhận cổng thay thế, không coi ba lệnh chuẩn đều xanh. **Core cần xác nhận `KHAI-SDK-2.1.json`, bảng `cau_hinh`: khóa `[]`/`doc(..., {})`, giá trị cấu hình kiểu `json`, singleton/CAS**, thích nghi với quy ước bản ghi hệ thống; bản khai hiện có cột ngân sách kiểu `so`, chưa chứng minh ánh xạ JSON hệ thống. Không sửa mẫu NGAN-0, Core hoặc SDK để lấp thiếu.
- **Bổ sung C-TX-01/02 từ TX-2 (15/11/2026):** hash chỉ kiểm toàn vẹn; module/pháp nhân/quyền prompt phải do Core ghim theo việc. Đã mô phỏng hai module dùng chung app/ngăn đồng thời, đổi bộ/cấu hình giữa chuỗi không sửa hồ sơ cũ. Đã tải hồ sơ thật trong RAM lên CoreGia, kiểm SHA-256 bytes, chuyển qua AI giả rồi bước sau đọc bằng `viec.mo_tep`. CoreGia chỉ dò tham chiếu trong đầu vào; **không chứng nhận ACL, cùng chuỗi/pháp nhân/module, TTL tới lưu/đóng hoặc ACK lưu/đóng của Core thật**. Hủy sau tải tệp có thể để tệp tạm ở Core tới khi vòng đời C-TX-02 dọn; engine không lưu nó trên máy.
- **Bổ sung C-TX-05 từ TX-2 (15/11/2026):** sửa `_ghi` chỉ che dòng “Lỗi khi xử lý việc”/traceback, giữ dòng mã lỗi SDK. Test RuntimeError chứa chuỗi bí mật DEMO chạy end-to-end qua CoreGia không lộ stderr/kết quả. Runtime và test chốt SDK `2.0.0`, chữ ký `_ket_thuc(self, dt, viec, cfg, trang_thai, *, loi=None, ma_tuong_quan=None)`/`_ghi(self, cau)`; khác thì chặn khởi động, phải review lại trước nâng SDK.
- Các quyết định tạm ở `_chung/docs/GIAO-CODEX-THU-TU.md` §2 về tệp cấu hình/kho đĩa/không có màn **đã được Anh thay ngày 15/11**: không lưu gì trên máy, có màn cấu hình engine nạp như màn module; schema chỉ đọc trong gói, giá trị qua ngăn; tệp tạm của việc dọn trong `finally`. Chạy thử DEMO vẫn dùng màn chung Core. TX-0 không sửa Core/SDK và chưa kiểm nối Core thật.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

- **Bổ sung C-TX-02/04 từ TX-3 (15/11/2026):** lõi hậu kiểm/xuất chỉ kiểm bằng CoreGia, quyền/module/pháp nhân/TTL/ACK lưu-đóng vẫn là mô phỏng. Khi JSON đã tải nhưng Excel lỗi/hủy, không nộp kết quả; Core cần dọn tệp tải dở theo vòng đời chung. CLI chuẩn vẫn **2/3 ĐẠT, exit 1, CHUA_CAU_HINH**; cổng có ngăn **5/5 ĐẠT** gồm hai DEMO TX-3 chưa đăng ký, trình lead xác nhận như TX-2. Payload/schema và bước xuất tĩnh chờ lead/Anh review tại **TX-3-REVIEW.md**; chưa tạo schema nguồn hoặc đăng ký runtime, không tự đổi contract.

## Cần phối hợp sau TX-0 — cập nhật 15/11/2026
- **TX-4 / lead (15/11/2026):** đã xác minh XLSX PR #30, không cần cấp lại tệp này. Cần fixture hợp đồng thường/Track Changes, snapshot/prompt hai module, băng AI giả cố định và bản vàng đủ sáu artifact được lead chấp nhận, kèm SHA/biên bản. `tests/kiem_e6.py` mặc định **exit 2**, “Thiếu nguồn đối chiếu E6.”; `--chan-doan` cũng luôn **exit 2**. Hai DEMO kỹ thuật chưa được duyệt đã lộ khác byte thật; giữ E6, không nhận 375 test passed là E6 đạt. Phương án làm lại riêng tại [TX-4-E6.md](TX-4-E6.md): batch có contract mới **12–18 giờ ước tính** hoặc lặp v1 Core điều phối **18–24 giờ ước tính**, chưa gồm Core/AI/module; chưa triển khai và không tính vào 4 giờ TX-4. Cần xử lý cả tương thích bảng/phản hồi, không chỉ số lượt. Giữ C-TX-01/02/04/A-TX-01, chưa phát sinh API mới hoặc đo N1/Core thật.
- **Cần phối hợp AI-2: bước Hỏi AI phải bao/thoát nội dung** (sửa review TX-3, 15/11/2026). Test Trích xuất xác nhận tài liệu chứa chỉ dẫn/dấu phân cách/JSON giả chỉ đi vào trường `tai_lieu`, không sửa prompt hệ thống hoặc khuôn; chưa chứng nhận lớp bọc request tới model của Hỏi AI.

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

## Bàn giao TX-2 — 15/11/2026, PR: chờ lead mở

**Kết luận: Chưa đạt cổng CLI chuẩn — đã xong code/test phần TX-2 bằng CoreGia;
CLI SDK 2.0.0 chưa nạp cấu hình ngăn, trình lead cổng DEMO có ngăn thay thế.**
Không tuyên bố ba lệnh xanh hoặc chứng nhận Core/model thật.

Đã làm:

- Bản gói **0.3.0**, thêm năng lực thật `trich.chuan_bi@1`, một `yeu_cau_ai`
  phiên bản 1; schema chung chép nguyên byte, test SHA. Không sửa loại thành batch.
- SHA-256 trên đúng UTF-8 chuỗi bộ trước parse; JSON nghiêm với khóa lặp,
  NaN/Infinity/1e9999/Unicode không hợp lệ. Dùng E1 SDK kiểm đúng 10 cột,
  quy tắc và mã, giữ dòng ngừng dùng/thứ tự. Tách băm XLSX, nội dung E1,
  snapshot có module/loại/phiên bản/quy tắc; thiếu/sai không mặc định XD.
- Danh sách rỗng lấy mọi mã đang dùng, danh sách con giữ thứ tự yêu cầu,
  từ chối mã lạ/trùng/ngừng dùng; hỏi thêm chỉ nhận `[]`.
- Prompt bắt buộc của module, nối giao thức nguyên văn/offset Unicode;
  khuôn 2020-12 `$defs` đủ mọi mã. Chặn snapshot 64 KiB/200 dòng đang dùng,
  prompt cuối 20.000 ký tự, toàn văn 500.000, khuôn 32 KiB, chuyển tiếp
  64 KiB. Không top-k/bỏ trang/cắt ô; ngân sách mặc định 16.000, không vượt
  trần ngăn và không hạ ngầm. Ghim cấu hình/phiên bản trước xử lý handler.
- Hồ sơ JSON trong RAM qua `tai_tep_ra`, đủ chuỗi/bộ/quy tắc, đúng văn bản
  gửi AI/vị trí, yêu cầu, băm và cấu hình đã ghim. Chuyển tiếp chỉ metadata/
  tham chiếu/băm, DEMO dưới 4 KiB; không đưa bộ/toàn văn vào chuyển tiếp
  hoặc phần này vào model. Bước AI và bước đọc hồ sơ sau nó dùng giả.
- Đóng nợ TX-1 về log, test RuntimeError và SDK fail-closed, ghi xác nhận
  khai cấu hình kiểu JSON vào Cần Core. README ghi rõ DOCX `vMerge continue`
  có chữ, `w:tr` không có `w:tc`, lệch `gridSpan` đều bị từ chối **cả tài liệu**;
  trần tỷ lệ giải nén **200:1**.

Phạm vi gồm **4 tệp Python runtime** (`chay.py`, `tich_hop.py`, `tham_so.py`,
`cau_truc.py`) và phiếu đăng ký năng lực; schema chung là tài nguyên chép
nguyên byte. Không tách thêm lát hoặc đổi 7 giờ ước tính. Không sửa hai mẫu
NGAN-0, Core, SDK, `ma-nguon/` hoặc các thư mục tham chiếu; không xóa tệp,
không commit/push, không thêm dependency runtime. Hậu kiểm/xuất/E6/N1 vẫn
thuộc lát sau; không công bố độ chính xác hoặc sức chứa model thật.

### Kết quả kiểm thực tế

Môi trường `.venv/Scripts/python -B` trong worktree; Python **3.13.14**,
SDK **2.0.0** cài wheel offline `--no-index --no-deps`, SHA-256 khớp
`SHA256SUMS.txt`: `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Venv dùng `--system-site-packages` để nhận pytest **9.1.1**, jsonschema
**4.26.0** có sẵn, đã ghim test; không tải mạng. Khi kiểm đặt `PYTHONUTF8=1`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

| Lệnh đã chạy đúng trong worktree | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/3 ĐẠT, exit 1**; hai DOCX đạt; “Chuẩn bị đủ trường từ snapshot DEMO” trả `CHUA_CAU_HINH` với câu cố định của TX-1, CLI chưa nạp ngăn |
| `.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q` | **164 passed in 2.38s, 0 skipped, exit 0**, gồm Node/KttCore giả và SHA hai mẫu NGAN-0 sau CRLF→LF |
| `.venv/Scripts/python -B e_trich_xuat/tests/kiem_doc_lap.py` | **[ĐẠT], exit 0**, không import Core/kênh cũ, không bytecode hoặc liên kết trong gói |
| `.venv/Scripts/python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | **3/3 ĐẠT, exit 0**; nạp cấu hình DEMO bằng ngăn RAM trước `CoreGia.chay_thu_demo`, không cờ tệp/env hoặc nhánh tự cấu hình trong engine |

**đã kiểm bằng Core giả (CoreGia)**: đủ mã/khuôn/dẫn chứng, JSON lặp khóa/
mã/thiếu/sai hash, E1 có dòng ngừng dùng/quy tắc, ba băm riêng, giới hạn byte
UTF-8 và ký tự (cả sát trần), đủ 200 mã trong một request, danh sách con,
hỏi thêm bị chặn, cấu hình thiếu/đổi, ngân sách sát/vượt trần, vị trí Unicode
với emoji/dấu tổ hợp và nguồn DOCX/OCR DEMO, hai module đồng thời trên cùng
app/ngăn, hồ sơ/băm đúng, snapshot cũ không đổi. Consumer AI-2 thật nhận và
kiểm khuôn mới trong test, **không gọi model**; chuỗi AI/đọc lại hồ sơ dùng giả.
Mất ACK tệp/kết quả/kết thúc đều gửi lại cùng khóa và chỉ ghi một lần; hủy
không nộp kết quả. Chặn ghi đĩa/gọi mạng trong ca runtime; RuntimeError DEMO
không lộ dữ liệu ra log, mã lỗi vận hành vẫn giữ. **0 Cloud, 0 model thật.**

Linux **chưa chạy thực tế**: `wsl --list --quiet` xác nhận WSL chưa cài,
không có Docker; không cài hoặc đổi Windows. Test không phụ thuộc đường
Windows hoặc dịch vụ thật; cần lead chạy lại trên Linux. Core thật/ACL/TTL/
lưu-đóng/context thực của Hỏi AI chưa chứng nhận, giữ C-TX-01/02/04 và A-TX-01.

Thời gian thực tế (UTC+07), **15/11/2026**: bắt đầu **08:38:00**, kết thúc
**09:01:55**, khoảng **0.40 giờ**; phiếu TX-2 **7 giờ công ước tính**.
PR: **chờ lead mở**. Rà cuối: **36 băm** nguồn/gói/kiểm khớp, **15 tệp**
đổi/thêm đúng UTF-8/AST/JSON/phạm vi; `git diff --check` sạch.

## Nối ngăn chung NGAN-0 — TX-1, 15/11/2026, PR: chờ lead mở

**Kết luận: Đạt — đã nối ngăn chung NGAN-0**, đã kiểm bằng Core giả (CoreGia)
trên Windows. NGAN-0 đã gộp main tại PR #34; đóng mục chờ mẫu chung, còn
C-TX-04/C-TX-05 về Core/SDK thật. Biên bản TX-1 ban đầu bên dưới là lịch sử
trước khi lead thay hai tệp mẫu; quy ước hiện hành nằm ở mục này.

- Giữ nguyên hai tệp `ngan.py`/`cau_hinh.py` lead đã chép; không sửa `_chung/**`.
  Hai test so SHA-256 sau đổi CRLF→LF chạy bắt buộc, **2/2 đạt, không skip**.
- `tao_app` truyền `KHAI-SDK-2.1.json/ngan_du_lieu` vào `NganBoNho` khi SDK
  chưa cấp ngăn; giữ ngăn SDK đã có. Không thêm khóa vào `engine.json` 2.0.
- Cấu hình singleton `doc("cau_hinh", {})`, giá trị dict trực tiếp;
  `doc_cau_hinh` trả dict hoặc None. Đọc một bản để ghim cùng phiên bản,
  ưu tiên ngăn/snapshot của việc, điền default trên bản sao, không ghi ngược.
- Bắt riêng `NganXungDot`/`NganKhongHopLe`/`CauHinhKhongHopLe` ở biên xử lý,
  đổi sang `LoiNghiepVu` bằng đúng mã/câu/cờ thử lại của mẫu chung.
- Test dùng `KetQuaLenh.ban_ghi/gia_tri/row_version/da_tao` sau commit và
  `TrangNgan.danh_sach/tiep`; bảng DEMO khai tường minh, phạm vi pháp nhân
  trong khóa/bộ lọc hoặc `cho_phap_nhan`. Giữ kiểm CAS/rollback và snapshot
  riêng engine, thêm lỗi cấu hình sai qua CoreGia, giữ ngăn SDK, không đọc chéo.
- Test DOCX dùng jsonschema **4.26.0** có sẵn (dependency của SDK) thay
  `kiem_schema` riêng của bản tạm; chỉ trong test, không tải mạng. Ghim cùng
  pytest **9.1.1** tại `tests/requirements.lock`, không thêm runtime.
  NGAN-0 không cam kết trần JSON 64 KiB của bản tạm; kiểm cấu hình theo schema
  engine (chỉ một số nguyên 1024–100000), không giữ kỳ vọng trần cũ trong test.

Môi trường: `.venv/Scripts/python`, Python **3.13.14**, SDK **2.0.0**;
`pip install --no-index --no-deps` xác nhận đúng wheel trong repo,
SHA-256 khớp `SHA256SUMS.txt`:
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`; riêng tiến trình kiểm, `PYTHONPATH`
ưu tiên `.venv/Lib/site-packages`, sau đó site-packages Python nền có sẵn
để dùng pytest/jsonschema; không cài mạng, không đổi hệ thống.

| Lệnh thật | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/2 ĐẠT, exit 0**, hai ví dụ DOCX thường/Track Changes; không cần cổng thay thế vì DOCX không cần cấu hình AI |
| `.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp` | **73 passed in 1.29s, 0 skipped, exit 0**; bao gồm Node UI **6 pass, 0 fail, 0 skip** và hai test SHA |
| `.venv/Scripts/python -B e_trich_xuat/tests/kiem_doc_lap.py` | **[ĐẠT], exit 0**, không import Core/kênh cũ, không bytecode/liên kết |

Phạm vi: chỉ sửa trong worktree, không commit/push, không xóa tệp;
không sửa API, SDK, nguồn cũ hay hai mẫu ngăn. **0 Cloud**, không AI/OCR thật.
Linux/Core thật chưa chạy; không phát sinh quyết định cần Anh.

Thời gian nối NGAN-0 (UTC+07), **15/11/2026**: bắt đầu **08:26:00**; kết thúc **08:34:17**; thực tế **0.14 giờ**. Phiếu TX-1 tổng **8 giờ công ước tính**, không có dự toán riêng cho lần nối này. PR: **chờ lead mở**.

## Bàn giao TX-1 ban đầu — lịch sử trước nối NGAN-0, 15/11/2026

**Kết luận:** đạt các kiểm tra phần Codex trên Windows, **đã kiểm bằng Core giả (CoreGia)**;
chưa chứng nhận Linux/Core thật hoặc bản NGAN-0 chính thức. Hai nhóm theo lệnh giao:
TX-1a có 5 tệp mã (khung/ngăn/cấu hình/UI), TX-1b có 1 tệp `docx.py` chuyển
lõi từ hai nguồn cũ; xem [TX-1-PHAM-VI.md](TX-1-PHAM-VI.md). Giữ tổng 8 giờ
công ước tính, cùng worktree/nhánh được lead giao; lead tách commit/PR, Codex không commit/push.

Đã làm:

- Gói `goi/e_trich_xuat/` SDK 2.0 hợp lệ, bản `0.2.0`, chỉ công bố
  `trich.doc_docx@1`; hai DOCX DEMO xác định, có nhãn trong nội dung. Không
  đăng ký stub hoặc năng lực TX-2/3. Schema `van_ban_tai_lieu` chép nguyên byte.
- Chuyển có sửa Accept All/Numbering, đọc bytes SDK trong RAM, băm gốc;
  giữ thứ tự, ô rỗng/gộp, bảng lồng/content control và số tự động theo từng
  danh sách. Giữ nội dung Unicode, offset theo đúng văn bản. `so_trang=0`,
  `trang=[]`; cây `khoi_docx` tùy chọn không mang trang/hộp giả. Vùng chưa
  đọc (đầu/chân trang, chú thích, ảnh/đối tượng nhúng) có cảnh báo cố định.
- Trần 20 MiB đầu vào, 120 giây khai tại Core; giới hạn ZIP/XML được kiểm
  trước đọc/giải nén XML, DTD bị chặn; trần nội dung/JSON/bảng từ chối cả
  việc, không cắt ngầm. Lỗi tiếng Việt không kèm dữ liệu/đường dẫn.
  Có tiến độ/kiểm hủy tại các chặng và vòng đọc; không tạo tệp tạm.
- Cấu hình qua ngăn RAM tạm, mặc định 16.000 chỉ điền khi bản ghi đã có;
  không tự ghi vào ngăn hoặc tài nguyên gói. DOCX độc lập cấu hình AI;
  kiểm thiếu cấu hình dùng một năng lực chỉ có trong test trên CoreGia,
  không đưa năng lực kiểm vào manifest/runtime.
- Màn một ô ngân sách và nút Lưu qua cổng KttCore, CAS lỗi bằng tiếng Việt,
  không HTML động hoặc mạng ngoài. Khai ngăn/cấu hình/màn ở tệp SDK 2.1 riêng.
  Nguồn/lock/SHA-256 và CHANGELOG đầy đủ; chỉ chuẩn Python + SDK trong runtime.

### Kết quả lệnh thực

Môi trường `.venv` trong worktree: Python **3.13.14**, SDK **2.0.0** cài offline
`--no-index --no-deps`; băm wheel khớp SHA256SUMS:
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Pytest có sẵn trên máy được đưa vào `PYTHONPATH` riêng của tiến trình kiểm,
ưu tiên thư mục SDK trong `.venv`, tắt tự nạp plugin và bytecode;
không thêm dependency runtime hoặc dùng mạng. Ba engine SDK mẫu cũng đã chạy đạt.

| Lệnh thật | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/2 ĐẠT, exit 0**: “Đọc hợp đồng DOCX DEMO”, “Chấp nhận Track Changes DOCX DEMO”; có đúng một cảnh báo RAM trên stderr |
| `.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q` | **66 passed, 2 skipped in 2.03s, exit 0**; cả hai skip so SHA `ngan.py`, `cau_hinh.py`, lý do **"chờ NGAN-0 gộp"** |
| `.venv/Scripts/python -B e_trich_xuat/tests/kiem_doc_lap.py` | **exit 0**; `[ĐẠT] Gói độc lập: không import Core/kênh cũ, không bytecode hoặc liên kết.` |
| `node --test e_trich_xuat/tests/ui/cau_hinh.test.mjs` | **6 pass, 0 fail, 0 skipped**; pytest cũng gọi bộ Node này |
| Kiểm SHA/UTF-8/JSON/khoảng trắng | **18 tệp SHA-256 khớp** (16 tệp gói ngoài NGUON + 2 nguồn cũ), schema chung nguyên byte; UTF-8 không BOM, JSON hợp lệ, không khoảng trắng cuối dòng |

Dòng kết của CLI SDK thực tế: `Engine e_trich_xuat 0.2.0: mọi ví dụ chạy thử DEMO đều đạt.`
Pytest đã kiểm DOCX có/không Track Changes, dòng/ô bị xóa, nối đoạn qua
phần chèn, bảng ô rỗng/gộp/lồng/content control, style/số đa cấp, tệp hỏng/
sai MIME, bytes thực vượt trần hoặc lệch khai báo, ZIP/XML vượt trần trước đọc,
DTD UTF-8/UTF-16, hủy khi đọc và tại các mốc tiến độ, mất ACK không nộp trùng,
chặn ghi tệp/mạng trong runtime, log không lộ nội dung. Ngăn có kiểm rollback
toàn lô, CAS sai không ghi, chỉ mục duy nhất, hai luồng lấy hoặc tạo, đọc/tìm
theo pháp nhân, RAM mất ở phiên mới. UI kiểm đọc/lưu/phiên bản/CAS/thiếu bản ghi,
giới hạn nhập, chặn gửi lặp và lỗi không lộ chi tiết. Không AI/OCR thật, **0 Cloud**.

Linux **chưa chạy thực tế**: máy hiện không có runtime Linux/WSL. Test dùng
thư viện chuẩn, mock metadata liên kết Windows, không phụ thuộc COM/OCR/đường
máy thật. Không đánh dấu Linux là passed hoặc thêm skip để giả kết quả.

### API ngăn đã dùng — gửi lead đối chiếu NGAN-0

Runtime engine chỉ cần:

- `chon_ngan(app)` → ưu tiên `app.ngan`; fallback `NganBoNho()`, tái dùng RAM
  trên cùng app, cảnh báo stderr một lần trên tiến trình.
- `ngan.doc(bang, khoa)`, cụ thể `doc("cau_hinh", {"ma": "mac_dinh"})` →
  `None` hoặc `.gia_tri` (bản ghi `{ma, gia_tri}`) và `.row_version`.
- `doc_cau_hinh(ngan, schema)` → `None` hoặc dict đã điền mặc định/kiểm schema.
  `ghim_cau_hinh` đưa bản ghi vừa đọc qua cổng chỉ đọc để không đọc lệch
  phiên bản; trả `{gia_tri, phien_ban_cau_hinh}`. Nếu SDK có snapshot của việc,
  dùng `viec.cau_hinh`/`viec.phien_ban_cau_hinh`; nếu có `viec.ngan`, ưu tiên nó.

Bản tạm và bộ test hợp đồng còn dùng:

- `NganBoNho(khai_bao=None, *, phap_nhan_id=None)`; khai bảng có
  `bang/pham_vi/khoa/duy_nhat`. Trên ngăn gốc, bảng `phap_nhan` bắt buộc
  `phap_nhan_id` trong `khoa/loc`; chỉ mục có phạm vi pháp nhân.
- `tim(bang, loc=None, gioi_han=100, tiep=None)` → `{danh_sach: [BanGhi], tiep}`;
  giới hạn 1–500, mốc tiếp tạm là chuỗi offset. Runtime TX-1 chưa gọi `tim`.
- `with ngan.lo() as lo`: `them(bang, khoa, gia_tri)`,
  `sua(bang, khoa, gia_tri, *, row_version)`, `xoa(bang, khoa, *, row_version)`,
  `lay_hoac_tao(bang, khoa_duy_nhat, gia_tri)`; tối đa 100 lệnh, cả lô nguyên tử,
  CAS/duy nhất sai → `NganXungDot`, `thu_lai_duoc=True`.
- Test đọc `lo.ket_qua` sau with: mỗi phần tử có `row_version`, `da_tao`,
  `ban_ghi` (`BanGhi.gia_tri/row_version`). Đây là hình dạng tạm để test;
  mã engine không phụ thuộc kết quả ghi lô này. Không sao chép sâu toàn kho.

Lệch/tạm đã dùng: hai tệp ngăn viết trong gói theo ghi chú lead, chờ thay
NGAN-0; hai hook nội bộ SDK tại C-TX-05; chưa kiểm Linux hoặc Core thật.
Cần Core: NGAN-0/C-TX-04 và review màn, C-TX-05; các C-TX-01…03/A-TX-01
giữ cho lát sau. Không phát sinh quyết định nghiệp vụ cần Anh. Không sửa/xóa
`ma-nguon`, nguồn tham chiếu, schema chung, Core/SDK; không commit/push.

Kiểm cuối TX-1: `git diff --check` **exit 0**; phạm vi chỉ gói/test mới, `TX-1-PHAM-VI.md` và `VIEC.md`; UTF-8/JSON/AST/hàng rào Markdown đạt. Không có tệp bị xóa, không sửa nguồn chỉ đọc, không commit/push.

Thời gian TX-1 (UTC+07), **15/11/2026**: bắt đầu **07:52:00** theo lead; kết thúc **08:24:58**; thực tế **0,55 giờ**, so với phiếu **8 giờ công ước tính**. PR: **chờ lead mở**.

## Bằng chứng TX-P — 15/11/2026, PR: chờ lead mở

- Chỉ sửa `docs/GIAO-CODEX-e_trich_xuat.md` và `docs/VIEC.md`; không tạo gói/màn/công cụ runtime, không sửa nguồn cũ/Core/SDK, không commit/push. Bảng chọn giữ đủ năm câu TX0-06 còn mở và không chặn TX-1…TX-3; không coi việc hoàn thiện phiếu là duyệt payload hoặc cho phép code ngay.
- Kiểm regex theo mẫu Anh giao, bắt đầu `^### TX-n —` và lấy nội dung giữa hai dòng ba backtick trơn (thay `n` bằng từng số 1…6, bật MULTILINE/DOTALL): **6/6 khối đọc được**; từng khối có đầu vào/đầu ra, `LoiNghiepVu`, test `CoreGia` + `NganBoNho`, chỉ DEMO, giờ ước tính và điều kiện đạt. `git diff --check`: **exit 0**. Kiểm thêm UTF-8/hàng rào/phạm vi diff; không tính đây là test runtime.
- Ba lệnh AGENTS.md §5 **không áp dụng, không chạy** theo yêu cầu riêng TX-P chỉ tài liệu; ghi chú lead yêu cầu chạy chung được thay bằng chỉ dẫn cụ thể này. Không báo số DEMO/pytest passed hoặc nhận đã kiểm bằng Core giả (CoreGia) cho TX-P.
- Môi trường `.venv` trong worktree, Python **3.13.14**, SDK **2.0.0** cài từ wheel repo bằng `--no-index --no-deps`; SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp `SHA256SUMS.txt`, không mạng/dependency mới.

Thời gian TX-P (UTC+07): bắt đầu **15/11/2026 07:42:00** theo lead; kết thúc **15/11/2026 07:51:09**; thực tế **0.15 giờ**. Phiếu chưa có giờ ước tính riêng cho TX-P; **37 giờ** là dự toán TX-1…TX-6, không phải dự toán lát tài liệu này.

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

## Bàn giao TX-3 — 15/11/2026, PR: chờ lead mở

**Kết luận: Chưa đạt cổng đăng ký/CLI chuẩn — đã xong lõi và test DEMO
hậu kiểm + xuất theo cấu trúc đề xuất, chờ lead/Anh review payload/schema
chi tiết và bước xuất tĩnh.** Không đăng ký runtime hoặc tạo schema
`bang_trich_xuat` trước duyệt. Hướng T2 bảng + Excel giữ nguyên.

Đã làm đúng **5 tệp Python lõi**: `hau_kiem.py`, `kiem_tra.py`,
`logic.py`, `xlsx_mini.py`, `xuat.py`; không sửa nền TX-2. Chưa cần
tách TX-3a/3b ở phạm vi hiện tại; tổng dự toán vẫn **8 giờ công ước tính**.
Chi tiết review tại [TX-3-REVIEW.md](TX-3-REVIEW.md).

- Hồ sơ mở qua `viec.mo_tep`, kiểm bytes/hash/phiên bản và quan hệ với bộ
  E1/module/loại/prompt/văn bản/khuôn/ngân sách đã ghim. Không đọc bộ hay
  cấu hình đang kích hoạt; hash không thay quyền Core. Băm gốc tài liệu,
  băm toàn văn và băm request AI được tách rõ.
- Kiểm độc lập từng ô, đúng lát chuỗi Python, Unicode ngoài BMP/dấu tổ hợp.
  Câu giả/thiếu căn cứ/AI bỏ sót về null/cần soát với lý do riêng, giữ
  nguyên phản hồi AI. Mã lạ/trùng/đảo thứ tự/sai cấu trúc bị từ chối;
  mã thiếu bổ sung ô null đúng vị trí, không mất dòng. Không tin cờ chung.
- Chép có sửa logic L1–L5 và dấu kiểm legacy riêng cho E6. XD chạy đủ,
  loại khác chỉ L1/L4 và quy tắc E1 đã ghim; phạm vi hỏi có mục tiêu không
  bị buộc có mã ngoài danh sách. Vi phạm logic giữ giá trị có căn cứ,
  không tự sửa. Bộ TX-2 chưa khai quy tắc chuyển kiểu: giữ tiền/ngày
  nguyên văn ở hậu kiểm, không đoán tiền tệ/tính TT-21 hoặc sửa bộ 37.
- DOCX chưa phân trang để trang/hộp null, giữ đoạn/Điều/Khoản. Câu qua
  nhiều trang/khối OCR được tách theo offset thực và giữ từng hộp nguồn,
  câu AI gốc vẫn ở phản hồi riêng. Không lấy tọa độ của câu lặp đầu tiên.
- Bảng ≤200 dòng, phong bì UTF-8 ≤20 MiB; số đếm/cờ đúng quan hệ.
  Xuất `truong` tĩnh đủ hai tệp và ba trường tổng hợp; JSON canonical,
  Excel chuẩn Python trong RAM, text không thành công thức, giữ số dài/
  Unicode/tiền/ngày/nguyên văn. Kiểm ô 32.767 đơn vị UTF-16 trước escape,
  bỏ cắt ngầm; BytesIO đóng finally cả lỗi/hủy. Không XONG thiếu tệp.
- Phiếu **runtime 2.0 bản 0.3.0 giữ nguyên**, chỉ có hai năng lực TX-1/2.
  Phiếu đề xuất trong RAM của `tests/mau_tx3.py` hợp lệ SDK 2.0,
  có hai năng lực/hai DEMO TX-3; schema `tra_loi_ai` chép nguyên byte,
  không sửa bốn loại chung. Module vẫn sở hữu ghép cột/lưu/lịch sử.

### Kết quả kiểm thực tế

Môi trường `.venv/Scripts/python -B`, Python **3.13.14**, SDK **2.0.0**
từ wheel repo, băm khớp `SHA256SUMS.txt`:
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Venv dùng `--system-site-packages`; pytest **9.1.1**, jsonschema **4.26.0**
có sẵn và đã ghim test. Không mạng/dependency runtime mới. Khi kiểm đặt
`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, tắt plugin tự nạp pytest.

| Lệnh thật trong worktree | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/3 ĐẠT, exit 1**; hai DOCX đạt, TX-2 `CHUA_CAU_HINH` vì CLI chưa nạp ngăn, giữ C-TX-04; không tự cấu hình để xanh |
| `.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q` | **275 passed in 3.81s, 0 skipped, exit 0** |
| `.venv/Scripts/python -B e_trich_xuat/tests/kiem_doc_lap.py` | **[ĐẠT], exit 0**; không import Core/kênh cũ, không bytecode/symlink trong gói |
| `.venv/Scripts/python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | **5/5 ĐẠT, exit 0**: ba DEMO runtime có ngăn và hai DEMO TX-3 đề xuất, ghi rõ chưa đăng ký; cổng thay thế chờ lead xác nhận |

**đã kiểm bằng Core giả (CoreGia)**: DOCX/OCR giả → chuẩn bị → AI giả →
hậu kiểm → xuất; bước cuối `truong`. Đã kiểm đúng/sai offset, câu giả khi
cờ chung true, thiếu/null/mã lạ/trùng/đảo thứ tự, snapshot sai hash/module/
phiên bản, bộ đổi giữa chuỗi, logic theo loại, đúng 200 dòng, đúng 20 MiB/
vượt một byte, ô sát/vượt trần, tải lại đủ JSON/Excel, xuất lỗi, hủy giữa
writer/tại các chặng, mất ACK tệp/kết quả/kết thúc không nộp trùng, chặn ghi
đĩa/mạng và lỗi/log không lộ nội dung DEMO. **0 Cloud/model thật**.

Linux **chưa chạy thực tế** trong worktree Windows; lệnh `wsl --list --quiet` xác nhận WSL chưa cài, không có Docker; chưa chứng nhận
Core thật/ACL/TTL/lưu-đóng, E6/N1 hoặc context/chất lượng model thật.
Quyền/vòng đời tệp chỉ mô phỏng C-TX-02, tệp đã tải trước lỗi/hủy do Core
dọn theo cổng đó. Không sửa Core/SDK/nguồn cũ, không xóa tệp, không commit/push.

Thời gian thực tế (UTC+07), **15/11/2026**: bắt đầu **09:03:00** theo lead,
kết thúc **09:31:41**, khoảng **0.48 giờ** so với phiếu
**8 giờ công ước tính**. PR: **chờ lead mở**. Rà cuối: **50 SHA khớp**, **16 tệp** đổi/thêm
đúng UTF-8/AST/JSON/phạm vi, đúng **5 tệp lõi**; manifest/mẫu NGAN-0 giữ
nguyên, chưa có schema bảng. `git diff --check` theo cấu hình repo **exit 0**.

## Sửa kiểm độc lập TX-3 — 15/11/2026, PR: chờ lead mở

Kết luận: **Đạt phần sửa review trong engine; chưa đạt cổng CLI chuẩn** do
C-TX-04 đã có. Trạng thái TX-3 giữ **Chờ Anh** duyệt chi tiết payload,
chưa đăng ký `bang_trich_xuat`/năng lực/schema hoặc nối runtime mới.

Đã làm:
- Chặn đủ 9 cặp số khớp một phần do lead nêu; giữ hai ca đúng và kiểm thêm
  dấu âm, ngày, NBSP, biên chữ/số, strip đối xứng, lần xuất hiện đúng phía sau.
  Cách chấm cũ không đổi; đổi tên trường tạm đối chiếu thành `dau_kiem_tam_e6`.
- `so_tien.so` chỉ int (không bool) hoặc chuỗi thập phân chính xác; float bị
  từ chối. Round trip JSON/Excel giữ kiểu chuỗi, số dài và phần thập phân.
- Đóng nợ TX-2: nguồn/hồ sơ mỗi phần ≤20 MiB JSON UTF-8; trang ≤2.000 và
  ≤8 MiB; cảnh báo ≤200 và ≤64 KiB. Kiểm trước deepcopy/tải, có ca sát trần
  và vượt một byte, tái hiện 50.000 trang + 20.000 cảnh báo ×1.000 ký tự →
  `VUOT_GIOI_HAN`, 0 tệp/kết quả đã nộp. Không cắt ngầm.
- Hồ sơ chỉ lưu toàn văn nguồn một lần thay vì chép thêm trong request;
  hậu kiểm dựng lại request đầy đủ để kiểm băm. Test cả hồ sơ gọn và TX-2 cũ.
- Test prompt injection giữ nguyên prompt hệ thống/giao thức/khuôn; nội
  dung chen chỉ ở `tai_lieu`. **Cần phối hợp AI-2: bước Hỏi AI phải bao/thoát nội dung**.
- Đề xuất payload có `don_vi_offset:"unicode"`, `kieu_da_chuyen:false`;
  `phan_hoi_ai` chỉ kiểm toán, có thể lộ nội dung, module không hiển thị
  mặc định. Chi tiết **ĐỀ XUẤT TX-0, chờ Anh** tại `TX-3-REVIEW.md`.

Kết quả kiểm thực tế — **đã kiểm bằng Core giả (CoreGia)**, Windows,
Python 3.13.14 / SDK 2.0.0 (wheel khớp SHA-256), pytest 9.1.1;
`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`:

| Lệnh thật | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/3 ĐẠT, exit 1**; TX-2 thiếu cấu hình ngăn `CHUA_CAU_HINH`, giữ C-TX-04 |
| `.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp` | **337 passed in 4.11s, 0 skipped, exit 0** |
| `.venv/Scripts/python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | **5/5 ĐẠT, exit 0**, gồm hai DEMO đề xuất chưa đăng ký |
| `.venv/Scripts/python -B e_trich_xuat/tests/kiem_doc_lap.py` | **[ĐẠT], exit 0**, không bytecode/liên kết/import Core/kênh cũ |
| `git -c core.safecrlf=false diff --check` | **exit 0** |

Regression trước sửa: **16 failed, 23 passed** trong nhóm token/tiền mới,
bao gồm đủ 9 lỗi số của lead; sau sửa toàn bộ nhóm/bộ kiểm đều đạt.
Không mạng/dependency runtime mới, **0 Cloud/model thật**; Linux/Core thật,
ACL/TTL/lưu-đóng, E6/N1 và context/chất lượng model **chưa kiểm**.

Thời gian thực tế (UTC+07), **15/11/2026**: bắt đầu **09:35:00** theo lead,
kết thúc **09:52:25**, **0.29 giờ** cho đợt sửa review; phiếu TX-3
**8 giờ công ước tính** cho cả lát, không phải dự toán riêng đợt sửa này.

Lệch khỏi phiếu / quyết định tạm: đúng **5 tệp mã sửa** trong đợt review,
gồm hai tệp TX-2 để đóng nợ được giao; không đổi `_chung/**`, `ngan.py`,
`cau_hinh.py`, manifest hoặc đăng ký năng lực. Do giới hạn cấm sửa `_chung/**`
và ngoại lệ §4 chưa được xác nhận, phần bổ sung đề xuất TX-0 được ghi trọn
ở `TX-3-REVIEW.md` để lead đồng bộ riêng §4; giữ nhãn **ĐỀ XUẤT**.
NGUON cập nhật SHA-256 sau CRLF→LF; không sửa nguồn cũ, không xóa tệp,
không commit/push. PR: **chờ lead mở**.

Cần Core / Chờ Anh: giữ C-TX-01/02/04 và A-TX-01; chờ duyệt chi tiết
`bang_trich_xuat`, phối hợp AI-2 bao/thoát nội dung và lead xác nhận cổng
DEMO có ngăn thay CLI SDK 2.0. Không phát sinh API/năng lực đã đăng ký mới.

## Bàn giao TX-4 — 15/11/2026, PR: chờ lead mở

**Lịch sử trước quyết định chiều: tiêu chí byte câu hỏi/bảng/phản hồi và
đề nghị làm lại nhiều lượt dưới đây đã được thay thế bởi TX-4b.** Xem
biên bản TX-4b cuối tài liệu và bản hiện tại `TX-4-E6.md`.

Kết luận: **Chưa đạt điều kiện E6 — nghiệm thu chưa kiểm do thiếu nguồn
được lead chấp nhận; chẩn đoán kỹ thuật đã thấy khác byte câu hỏi/bảng/phản hồi.**

Đã làm: xác minh băm XLSX thật khớp NGUON/nguồn cũ; E1 đủ 37 mã đúng thứ
tự/10 tiêu đề/370 ô nguyên văn, ghi riêng băm XLSX/E1/snapshot. Thêm ba tệp
ngoài runtime `tests/kiem_e6.py`, `doi_chieu_cu_e6.py`, `test_e6.py`; wrapper
chỉ đọc nguồn, giữ nhóm/dò/rà lại, AI giả cố định và Track Changes. Báo cáo
[TX-4-E6.md](TX-4-E6.md) và artifact chẩn đoán đi kèm ghi đủ offset/độ dài/
băm. Công cụ mặc định và chế độ chẩn đoán đều **exit 2**, không nhận E6 đạt.

Kết quả kiểm: `kho_tri_thuc_sdk.thu` **2/3 ĐẠT, exit 1** (`CHUA_CAU_HINH`,
CLI SDK 2.0/C-TX-04); pytest **375 passed in 11.68s, 0 skipped, exit 0**;
kiểm độc lập **[ĐẠT], exit 0**; DEMO có ngăn **5/5 ĐẠT, exit 0** (hai DEMO
TX-3 chỉ đăng ký trong RAM). **đã kiểm bằng Core giả (CoreGia)**. AST/UTF-8/
NFC/artifact tái lập và `git diff --check` đạt. Python 3.13.14, SDK 2.0.0
wheel offline khớp SHA; không thêm dependency, không mạng/AI thật, **0 Cloud**.
Linux/Core thật/ACL/TTL/lưu-đóng và N1/T3 thật **chưa kiểm**.

Thời gian thực tế: **15/11/2026 09:54:00–10:12:54 (UTC+07), 0,32 giờ**;
phiếu **4 giờ công ước tính**, chưa gồm làm lại T3 khi E6 thất bại.

Lệch khỏi phiếu / quyết định tạm đã dùng: chưa có fixture/bản vàng E6 được
lead chấp nhận nên chỉ kiểm cơ chế bằng DEMO kỹ thuật, không chứng nhận
tương đương hoặc tạo đáp án để đạt. Nguồn cũ có 9/8 câu hỏi ở hai mẫu so
với 1 câu hỏi mới; bộ/tham số/văn bản trùng nhưng ba phần còn lại khác.
Không nới cổng; không sửa runtime/manifest/schema/Core/SDK/mã cũ/hai mẫu
NGAN-0 hoặc ghim nguồn, không chuyển bộ/lưu trữ, không xóa/commit/push.

Cần Core / Chờ Anh mới phát sinh: **không thêm API đã triển khai**; giữ
C-TX-01/02/04/A-TX-01 và chờ duyệt TX-3. Lead cấp nguồn/bản vàng đúng checklist
trong biên bản; trình lựa chọn làm lại riêng batch **12–18 giờ ước tính**
hoặc lặp v1 **18–24 giờ ước tính**, chưa gồm Core/module/AI. Không tự mở code
batch/nhiều vòng hoặc chuyển bộ trước E6 đạt.

## Bàn giao TX-5 — 15/11/2026, PR: chờ lead mở

Kết luận: **Chưa đạt điều kiện kiểm chung CLI** do SDK 2.0 CLI chưa cấp ngăn cấu hình (C-TX-04); phần bàn giao module và kiểm Core giả đã thực hiện.

Đã làm: `ban-giao-module/` có helper thuần gọi trực tiếp E1, chuyển snapshot giữ đủ 10 cột/dòng ngừng dùng/quy tắc và ba băm; tài liệu ánh xạ nguồn E1/U1a/U1b, trách nhiệm và quyền module/Core, ví dụ nạp/lỗi/ghim việc. Không chép E1, không thay bộ 37, không mở route/SQL/UI/kho engine. Test DEMO đối chiếu SDK, lỗi Excel/hash và hai module đổi bộ với việc cũ; **đã kiểm bằng Core giả (CoreGia)**, ngăn RAM chỉ chứa cấu hình engine.

Kiểm Windows, Python venv / SDK 2.0.0 offline, SHA-256 wheel khớp SHA256SUMS; 0 Cloud, không mạng/dependency runtime mới:

- `python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat`: **2/3 ĐẠT, exit 1**, DEMO chuẩn bị thiếu cấu hình `CHUA_CAU_HINH`; giới hạn CLI SDK 2.0/C-TX-04 như TX-2.
- `python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp`: **381 passed, 0 skipped, exit 0**.
- `python -B e_trich_xuat/tests/kiem_doc_lap.py`: **ĐẠT, exit 0**.
- `python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py`: **5/5 ĐẠT, exit 0**; hai năng lực TX-3 đăng ký chỉ trong RAM.

Linux và Core thật chưa chạy. Thời gian 15/11/2026 **10:15–10:19 UTC+07**, khoảng **0,07 giờ**, ước tính **3 giờ công**. Không sửa Core/SDK/nguồn cũ, không commit/push.

Cần Core: giữ C-TX-01 (xác thực module/pháp nhân, ghim snapshot và prompt theo từng việc, giới hạn thực), C-TX-04 (ngăn cấu hình trong cổng chạy thử); giữ các mục C-TX-02/03 và A-TX-01 đã nêu. Module tự triển khai kho bộ, phân quyền, lịch sử, so sánh, chạy thử và kích hoạt; chưa khẳng định đã cài. E6, payload hậu kiểm/xuất và năng lực chưa đăng ký vẫn chờ quyết định/duyệt như TX-4.

## Bàn giao TX-4b — 15/11/2026, PR: chờ lead mở

Kết luận: **Chưa đạt điều kiện bàn giao chung** — phép đo E6 đạt trên
2/2 ca (74/74 mã và dẫn chứng), nhưng nghiệm thu E6 chờ lead duyệt bộ
DEMO/vàng; CLI chuẩn còn C-TX-04. Quyết định chiều 15/11 thay tiêu chí
byte câu hỏi/bảng/phản hồi của biên bản TX-4 lịch sử bên trên.

Đã làm: sửa công cụ/adapter/test E6 theo giá trị sau hậu kiểm TX-3,
chỉ strip đầu/cuối, báo đủ bốn loại kết quả từng mã và lý do; giữ so
byte E1/tham số/văn bản. Bộ tham-chieu/e6 có hai DOCX DEMO tự soạn
(thường/Track Changes), hai băng AI cố định biểu diễn cùng đáp án nghiệp
vụ, hai snapshot module, vàng 37 mã/câu căn cứ soạn từ chính văn bản,
manifest SHA-256 từng nguồn với chap_nhan_lead: “chờ lead”. Công cụ soạn
không đọc đầu ra engine làm vàng và từ chối ghi đè nguồn khác bytes.
Không có mã khác trong phép đo; vàng không sửa theo đầu ra. Chi tiết
[TX-4-E6.md](TX-4-E6.md), [artifact](TX-4b-ket-qua.json),
[CHANGELOG](CHANGELOG.md).

Kết quả kiểm thực tế: **đã kiểm bằng Core giả (CoreGia)**, Windows,
Python 3.13.14 / SDK 2.0.0 offline (wheel khớp SHA), pytest 9.1.1:

| Lệnh qua .venv/Scripts/python -B | Kết quả |
|---|---|
| -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat | **2/3 ĐẠT, exit 1**; chuẩn bị thiếu cấu hình CHUA_CAU_HINH, C-TX-04 |
| -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp | **412 passed in 16.26s, 0 skipped, exit 0** |
| e_trich_xuat/tests/kiem_doc_lap.py | **[ĐẠT], exit 0** |
| e_trich_xuat/tests/chay_demo_voi_ngan_gia.py | **5/5 ĐẠT, exit 0** |
| e_trich_xuat/tests/kiem_e6.py | **exit 2**, ket_qua_do=dat, trang_thai=chua_kiem; cả 2 ca 37/37 mã khớp vàng, 37/37 dẫn chứng đúng |

AST/8 SHA-256/ZIP-XML hai DOCX/artifact và git diff --check đạt. Bộ E1,
tham số và toàn văn trùng byte ở cả hai ca; nguồn cũ 9 câu hỏi/mới 1,
các khác biệt DTO/bảng/phản hồi chỉ tham khảo. Track Changes nhận đúng
2 thay đổi; chấp nhận giá mới 2.200.000 VND.

Thời gian thực tế: **15/11/2026 12:36:00–12:52:14 (UTC+07), 0.27 giờ**;
ước tính phiếu TX-4 **4 giờ công**, chưa có dự toán TX-4b riêng.

Lệch khỏi phiếu / quyết định tạm đã dùng: CHANGELOG của lát ở docs vì
Anh cấm sửa goi/**; bộ DEMO/vàng do Codex soạn theo giao việc TX-4b,
lead chưa duyệt, không tự chứng nhận. Chưa render kiểm bố cục DOCX:
renderer skill documents dừng do thiếu pdf2image; đã kiểm ZIP/XML/styles,
Accept All và hai reader nhưng chưa thay cho kiểm PNG/Word. Giữ nguyên
nguồn cũ/Core/SDK/ghim XLSX; không sửa goi/**, không làm lại nhiều lượt,
không thêm dependency/mạng, không commit/push; **0 Cloud/AI thật**.

Cần Core / Chờ Anh mới phát sinh: **không thêm API Core mới**; giữ
C-TX-01/02/04/A-TX-01, CLI SDK 2.0 cần cửa nạp cấu hình ngăn. Lead cần
duyệt hai DEMO, băng/vàng và xem trực quan DOCX trước ghi “đã duyệt” kèm
bien_ban_lead. Chưa kiểm Linux/Core thật/ACL/TTL/vòng đời tệp, T3/N1/model
thật; TX-3b đăng ký năng lực là lát song song, ngoài phạm vi TX-4b.