# VIỆC — danh sách việc duy nhất của project `e_mask`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| MASK-2c-4 | Công cụ đo Local ngoài gói và gold DEMO ứng viên | Sau MASK-2c-3; quyết định Anh “Thêm AI cục bộ” | Xong phần công cụ/mock — 15/11/2026; **Chờ Anh/lead đo độc lập** | Đúng ba tệp mã/dữ liệu ngoài gói; không sửa runtime. 45 tên/45 ngữ cảnh +75 câu thường +15 tổ chức +15 địa chỉ +12 biến thể; chưa lead đóng băng gold độc lập. [Báo cáo](BAO-CAO-MASK-2c-4.md); PR: **chờ lead mở**; nợ CAO/Cloud tắt giữ nguyên |
| MASK-2c-3 | Hậu kiểm Local, xác minh nguồn và che bổ sung theo span | Sau MASK-2c-2, AI-9; profile lead đã duyệt 15/11 | Xong phạm vi CoreGia — 15/11/2026; chờ Core/model thật | Đúng năm tệp mã, bản 1.2.0; 1109 passed, 4 xfailed giữ nguyên, 190 subtests, 0 skipped; DEMO có quyền 2/2, CLI chuẩn 0/2 thiếu quyền. [Báo cáo](BAO-CAO-MASK-2c-3.md); PR: **chờ lead mở** |
| 0 | Đọc yêu cầu chung/SDK 2.0, yêu cầu Mask và lập kế hoạch lát có giờ ước tính; trình Anh qua lead | MASK-P | Xong — 14/11/2026 (lập phiếu) | [GIAO-CODEX-e_mask.md](GIAO-CODEX-e_mask.md): 14 lát MASK-0…13, 52–62 giờ ước tính chưa đo; phần tệp có điều kiện, chưa triển khai; PR: **chờ lead mở** |
| 1 | Chuyển kho bí danh sang **ngăn của engine** theo cổng chung (thay `mask.py`/`kho_mask.py`/SQL 113, 117–120 trong Core) | MK-10, 19 | Chờ Core | Bàn cùng lead Core qua Anh |
| 2 | J8b: đối soát mất xác nhận | — | Chờ làm |  |
| 3 | Lát 4: màn duyệt danh sách chờ (Admin) — giao diện của engine | MK-15, 16 | Chờ làm |  |
| 4 | Lát 5: màn thử che/mở che DEMO | — | Bỏ — 15/11/2026 | Anh chốt bỏ `PHIEU-MASK-CHAY-THU-DEMO.md` (QUYET-DINH-ANH-20261115 câu 10); thử DEMO dùng màn Chạy thử chung của Core |
| 5 | Lát 8: che/mở che Word/Excel (mẫu 5–8) | §1.3; quyết định Anh chiều 15/11 câu 9 | Chờ làm theo B — 15/11/2026 | Anh cần nhận tệp giữ định dạng; MASK-P2 đã lập lại phiếu MASK-B1…B10, chưa code tệp |
| 6 | Lát 6: 8 contract (Anh duyệt tên) → lát 7: bài 11 bước | — | Chờ làm |  |
| MASK-P | Lập phiếu giao Codex theo SDK 2.0; chỉ tài liệu, không tạo gói/không sửa nguồn | MK-1…6, 10…22 | Xong — 14/11/2026 | [Phiếu giao](GIAO-CODEX-e_mask.md): 14 lát, 52–62 giờ ước tính có điều kiện. Regex 14/14 khối đạt; 5 mục/bảng lát/tổng giờ khớp; UTF-8/NFC và kiểm khoảng trắng đạt, `git diff --check` mã 0. Ba lệnh kiểm gói AGENTS.md §5 không áp dụng theo ngoại lệ lát chỉ tài liệu; không chạy hoặc nhận là đã kiểm bằng CoreGia. Đề xuất `van_ban_da_che` ở cuối sổ chung mang nhãn **ĐỀ XUẤT MASK-P, chờ Anh**. Không commit/push; PR: **chờ lead mở** |
| MASK-3 | Port kho/quyền, kho tạm và chống trùng sau MASK-2 | MK-10…13, 16…19 | Xong phạm vi port/CoreGia — 14/11/2026 | Chỉ DEMO; đúng bốn tệp mã. Pytest 225 passed, 190 subtests passed; kiểm độc lập ĐẠT. CLI SDK 0/2 ĐẠT do handler MASK-5 còn stub; chưa đạt nghiệm thu chung. PR: **chờ lead mở** |
| MASK-3b | Kho MASK-3 qua Ngan, tiền tố MASK, bản khai SDK 2.1 | Quyết định 15/11 câu 2, 8; kiểm độc lập của lead | Xong phần sửa an toàn — 15/11/2026; đã nối ngăn chung NGAN-0; chờ Core thật | Bỏ Cf/selector và che theo vị trí gốc; bí danh tạm riêng từng yêu cầu; bọc lỗi/log; hiện vật lưu trên máy đã ra LUU-TRU. PR: **chờ lead mở** |
| MASK-4 | Phong bì và schema ba loại riêng | MK-20 | Xong phạm vi CoreGia — 15/11/2026 | Schema chung/bản gói so SHA; kiểm UTF-8/JSON/trần lồng. PR: **chờ lead mở** |
| MASK-5 | Hai handler văn bản SDK và mở che dữ liệu/trích dẫn AI | MK-12…14, 18, 20, 21 | Xong phạm vi CoreGia — 15/11/2026; chờ quyền thật | DEMO qua port ngoài gói; CLI chuẩn vẫn bị chặn do thiếu quyền. PR: **chờ lead mở** |
| MASK-6 | Duyệt/từ chối, đóng/dọn, chuyển DEMO và màn Admin | MK-11, 15…19, 22 | Xong phạm vi CoreGia/KttCore giả — 15/11/2026 | Màn trong gói; chưa nạp trong Core thật. PR: **chờ lead mở** |
| MASK-7 | Khảo sát từng vùng tệp, đo DEMO và trình phương án/trần | MK-1, 4, 21; quyết định 15/11 câu 11 | Xong khảo sát — 15/11/2026; Anh đã chọn B chiều cùng ngày | [Bảng bằng chứng và phương án](MASK-7-KHAO-SAT-TEP.md), [số đo thật](SO-DO-MASK-7.json). Câu 9 chiều thay trạng thái chờ cũ: dùng trần thử nghiệm §5, lập lại phiếu ở MASK-P2; chưa code tệp. PR: **chờ lead mở** |
| MASK-P2 | Lập lại MASK-8…11 theo phương án B, chỉ tài liệu | Quyết định Anh chiều 15/11 câu 9 | Xong tài liệu — 15/11/2026 | [Phiếu §7](GIAO-CODEX-e_mask.md#7-mask811-theo-phương-án-b): 10 lát MASK-B1…B10, 54–80 giờ ƯỚC TÍNH, mỗi lát ≤5 tệp mã, đủ khối tự đủ; regex 10/10. Chưa code/chưa kiểm Office/Local thật, Cloud tắt; PR: **chờ lead mở** |
| MASK-B1 | Cổng ZIP/XML, whitelist OOXML và trần thử nghiệm | MASK-7, MASK-P2; quyết định chiều câu 9 | Xong cổng nội bộ — 15/11/2026; chưa nối năng lực tệp | Đúng ba tệp mã; 276 test mới, toàn bộ 1248 passed/4 xfailed giữ nguyên/190 subtests/0 skipped; CLI chuẩn 0/2 thiếu quyền, adapter CoreGia hiện có 2/2. [Báo cáo](BAO-CAO-MASK-B1.md), [kết quả thật](KET-QUA-KIEM-MASK-B1.txt); PR: **chờ lead mở** |
| MASK-B2 | Reader Word mọi vùng trong profile, map Unicode/run/attribute/byte | Sau B1; quyết định chiều câu 9 | Xong reader nội bộ và gộp B3 — 15/11/2026; chưa nối năng lực tệp | Đúng ba tệp runtime, 155 test mới; B1+B2 431 passed; toàn bộ 1540 passed/4 xfailed/190 subtests/0 skipped. CLI 0/2 thiếu quyền, adapter CoreGia 2/2. [Báo cáo](BAO-CAO-MASK-B2.md), [kết quả thật](KET-QUA-KIEM-MASK-B2.txt); PR: **chờ lead mở** |
| MASK-2b | Sửa theo kiểm độc lập: chấm điểm tên, giảm báo nhầm | MK-2, 18, 20; lệnh lead 15/11 lúc 09:47 | Xong phạm vi CoreGia — 15/11/2026 | t9: 0/32 lọt; t10: 2/41 báo nhầm (4,88%); 717 passed, 190 subtests. [Báo cáo](BAO-CAO-MASK-2b.md), [số đo](SO-DO-MASK-2b.json); PR: **chờ lead mở** |
| MASK-2c-P | Thiết kế lớp Local AI thứ hai và lệnh giao Codex, chỉ tài liệu | Quyết định Anh 15/11: "Thêm AI cục bộ" | Xong tài liệu — 15/11/2026 | [Phiếu Mask §6](GIAO-CODEX-e_mask.md#6-mask-2c--lớp-ai-cục-bộ), AI-9 ở phiếu Hỏi AI, đề xuất dữ liệu chung §6; 4 lát Mask + AI-9, tổng 31 giờ ƯỚC TÍNH triển khai. Chưa code/chưa đo model thật, Cloud tắt; PR: **chờ lead mở** |
| MASK-2c-1 | Map gốc/bản dò/bản che và snapshot bất biến qua port Core/Ngan | MASK-2b, MASK-3b…6; profile kỹ thuật lead duyệt 15/11 | Xong phạm vi CoreGia — 15/11/2026; chờ Core thật | Đúng bốn tệp mã; 866 passed, 4 xfailed giữ nguyên, 190 subtests; adapter DEMO 2/2, CLI chuẩn 0/2 thiếu quyền. [Báo cáo](BAO-CAO-MASK-2c-1.md); PR: **chờ lead mở** |
| MASK-2c-2 | Chuẩn bị yêu cầu Local, khuôn/profile/budget và kế hoạch đoạn | MASK-2c-1; profile kỹ thuật lead đã duyệt 15/11 | Xong phạm vi CoreGia — 15/11/2026; chờ Core/model thật | Đúng năm tệp mã, bản 1.1.0; 972 passed, 4 xfailed giữ nguyên, 190 subtests, 0 skipped; DEMO có quyền 2/2, CLI chuẩn 0/2 thiếu quyền. [Báo cáo](BAO-CAO-MASK-2c-2.md); PR: **chờ lead mở** |

Các số “lát 1…8/J8b” ở các dòng lịch sử là mã kế hoạch cũ; kế hoạch giao SDK 2.0 dùng `MASK-0…MASK-13` trong phiếu mới. Hoàn tất MASK-P không có nghĩa đã code, kiểm bằng CoreGia hoặc nối Core thật. MASK-P ước tính 1 giờ; tổng giờ 52–62 là dự toán triển khai sau, cập nhật lại sau khảo sát tệp MASK-7.

## MASK-2c-4 — bàn giao công cụ ngoài gói, 15/11/2026

- **Sửa theo kiểm độc lập lead — 15/11/2026; PR: chờ lead mở. Đã kiểm bằng Core giả (CoreGia); CHƯA ĐO Local thật.** Không commit/push, không sửa runtime gói.
- Bổ sung **28 ca** (18 người, 5 tổ chức, 5 địa chỉ), tổng **190 ca/124 gold span**. Tên không dấu/Hoa đầu chữ/IN HOA/danh xưng/2–4 âm tiết/sáu họ từ thường; tổ chức/địa chỉ không DEMO trong span và đủ năm khung; sáu ca mép/overlap kiểm theo kế hoạch thực. 28/28 định danh không trùng sau chuẩn hóa trên 803 tệp UTF-8 Git quản lý (trừ bộ mới/đường cấm). Giữ nguyên 162 ca cũ/development/hồi quy.
- Băm nội dung mới: `b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad`. Trạng thái **ỨNG VIÊN, chờ lead đóng băng**, không nhận held-out độc lập.
- Báo cáo tách chặn trước AI / có đoạn AI-9 XONG / chưa có đoạn xong; giữ mẫu số lọt và báo nhầm riêng từng nhóm cùng tổng. **0 lọt trên ca bị chặn trước AI là hiển nhiên.** Thêm đếm span/ký tự che ngoài hợp gold ở cả ca có định danh.
- `--timeout` mặc định 120 giây × số đoạn, `--timeout-toi-da` mặc định 3600; CLI dùng process mỗi ca để dừng cứng và giữ checkpoint/ca trước. Timeout ghi chưa đo đủ theo ca; ngoại lệ vẫn xuất JSON từng phần trước thoát. `.cmd` ASCII/CRLF; báo cáo ngoài repo hoặc đúng thư mục riêng được chỉ định, không ghi đè.
- Kiểm lượt sửa: tool **50 passed, 0 skipped, 41,13 giây, mã 0**; toàn Mask **1159 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 160,89 giây, mã 0**; SDK CLI **0/2 mã 1** thiếu quyền; DEMO có quyền **2/2**, độc lập và chạy khô đạt. Chi tiết [báo cáo](BAO-CAO-MASK-2c-4.md), [kết quả lệnh](KET-QUA-KIEM-MASK-2c-4.txt). Thời gian **15:01–15:23:45, 0,38 giờ** (phiếu 5 giờ ƯỚC TÍNH, không có ước tính riêng lượt sửa).
- Cần Core/Chờ Anh: không phát sinh mới; giữ các mục C-M2C-01…05 ở dưới và chờ lead đóng băng/Anh đo Local. Cloud giữ tắt.

### Lịch sử bàn giao trước kiểm lead (14:22–14:53)

- **Đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả; **CHƯA ĐO Local thật**. Không có tỷ lệ lọt/báo nhầm Local thật để công bố. PR: **chờ lead mở**, không commit/push.
- Kiểm cuối: Mask **1143 passed, 4 xfailed giữ nguyên, 190 subtests passed**, riêng tool **34 passed** sau chỉnh metadata/đích báo cáo; Hỏi AI **560 passed**; tất cả 0 skipped trên Windows. DEMO Mask **2/2**, Hỏi AI **3/3 + 1 AI-9**, hai kiểm độc lập và `git diff --check` đạt. CLI chuẩn Mask **0/2 mã 1** thiếu quyền, Hỏi AI **0/3 mã 1** thiếu cấu hình. [Kết quả lệnh thật](KET-QUA-KIEM-MASK-2c-4.txt). Thời gian **14:22–14:53, 0,52 giờ** (5 giờ ƯỚC TÍNH).
- `cong-cu/thu_mask_local_ai_that.py` mặc định chạy khô không mạng; `.cmd` ASCII, trích dẫn Python/script/tham số, chạy được khi thư mục có khoảng trắng. Chỉ `--that --url --model` mới cho gửi DEMO. `--bao-cao` tùy chọn, JSON mới ngoài thư mục engine, không ghi đè; chỉ đếm/phiên bản/băm/thời gian, không gốc/trích dẫn/URL/path/mã mở che.
- Adapter ngoài gói gọi chuẩn bị Mask → AI-9 → hậu kiểm Mask bằng CoreGia, lặp đủ đoạn và ghép phản hồi trước hậu kiểm; giữ kiểm IP/model/context/budget/hoàn tất của AI-9, chặn model tự dự phòng khác model Anh chỉ định. Cấu hình và snapshot chỉ RAM/ngăn DEMO. **Biên nhận tokenizer/budget và chứng thực Core là fixture**; không là bằng chứng Core/tokenizer/ACL thật.
- JSON mới là **ứng viên do Codex soạn**, chưa được lead xác nhận độc lập: 162 ca, 96 gold span; 45 tên cơ sở/45 ngữ cảnh, 75 câu thường (giữ cả mập mờ), 15 tổ chức, 15 địa chỉ, 12 biến thể NFD/Cf/selector/tab/NBSP/lặp/overlap/mép đoạn/văn bản dài. Tách `development` và bốn ca lead cũ; biến thể không tăng mẫu số 45. SHA nội dung: `a32a84a90f5f3391761f07a24ccdad4a5349f52626c7564fddef0c0cbb1ea076`.
- Hai chế độ dùng cùng bộ; bộ chấm độc lập detector dựng lại khoảng alias từ hai chuỗi và ngăn đã chốt, kiểm phủ toàn gold span và dò bỏ dấu/Cf/khoảng trắng/dấu câu. Báo riêng phát hành che đủ/còn lọt/chặn nghiệp vụ/lỗi kỹ thuật/chưa rõ; báo nhầm tính hợp che thừa hoặc chặn nghiệp vụ/75, kèm số hợp lệ/tổng; không dùng timeout/sai khuôn/model thiếu làm “0 lọt đạt”. Có số đoạn kế hoạch/xong, p50/p95, số gọi provider Local và Cloud.
- Test bốn ca lead cũ: AI giả báo đủ thì che hết. **AI chỉ cứu được khi báo đủ; AI báo thiếu một phần tên thì phần còn lại vẫn lọt.** Không sửa detector/prompt dựa trên bộ ứng viên rồi nhận cùng bộ là held-out mới.

### Cần Core / Chờ Anh — MASK-2c-4

- Giữ mở **C-M2C-01…05**: snapshot/quyền xuyên bước, điều phối đủ đoạn/deadline, nguồn AI-9 và chứng cứ bước cuối, cửa Cloud, ngăn CAS/lượt bền. CoreGia không chứng nhận các cửa này. Không viết route/Core/SDK riêng.
- Lead giữ khâu soạn/đóng băng gold độc lập trước đo; bộ ứng viên này chưa là nghiệm thu held-out độc lập. Nếu dùng bộ đã xem để chỉnh, phải thay bộ nghiệm thu mới. Lead xác nhận backend chạy model tại chỗ và chặn egress Cloud trước chạy thật.
- Chờ Anh chạy `cong-cu/THU-MASK-LOCAL-AI-THAT.cmd` theo hướng dẫn trong báo cáo. Nợ **CAO** chỉ xem xét sau lead review đủ bằng chứng và Core thật; **Local đạt cũng không bật Cloud**.
- Không chạm `e_hoi_ai` trong lát này; nợ transport AI-9 sau POST lead đã nêu giữ nguyên, lỗi đó vẫn là lỗi kỹ thuật/chưa rõ khi đo, không đổi thành thành công/rỗng.

## MASK-2c-3 — bàn giao hậu kiểm Local, 15/11/2026

- **Đạt phạm vi CoreGia; đã kiểm bằng Core giả (CoreGia).** PR: **chờ lead mở**; không commit/push. [Báo cáo theo AGENTS.md §6](BAO-CAO-MASK-2c-3.md), [kết quả lệnh thật](KET-QUA-KIEM-MASK-2c-3.txt). Chưa kiểm Core/model thật hoặc Linux thực tế.
- Đúng năm tệp mã được giao; bản 1.2.0 thêm `mask.hau_kiem_ai_cuc_bo@1`, một đầu vào `tra_loi_ai`, đầu ra `van_ban_da_che`. Đọc snapshot/tập nguồn có quyền từ Core, chứng thực từng phản hồi AI-9/Local/hoàn tất và giữ chuyển tiếp nguyên vẹn; băm AI trên toàn phong bì yêu cầu JSON chuẩn. Rỗng không tự là an toàn.
- Đối chiếu code point, map, biên NFD/Cf/selector; giữ alias lớp 1 và chặn partial overlap/prefix/nghi vấn/mâu thuẫn/mép đoạn chưa có bản bao đủ. Gom đúng span, giữ lần lặp; che thêm phải → trái qua kho hiện có. Hậu kiểm cũ và kiểm tiền/ngày/numeric review toàn văn phải đạt trước chốt. CAS/rollback/chống lặp giữ nguyên, >100 lệnh từ chối toàn bộ; Core ghi chứng cứ SHA kết quả cuối trước trả.
- **1109 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 128.47 giây; mã 0**, gồm 137 test mới. DEMO có quyền **2/2 ĐẠT**, độc lập và `git diff --check` mã 0. CLI SDK chuẩn **0/2, mã 1** vì thiếu nguồn quyền, không nới runtime để làm xanh. Có kiểm mất ACK/ChuaRo/timeout/CAS thực/thu hồi quyền/hủy và không rò gốc. Không chạy AI/model thật hoặc đo held-out hai lớp; nợ CAO và MASK-2c-4 vẫn mở. 0 Cloud/engine-to-engine từ Mask.
- Thời gian thực tế: 13:47:00–14:13:07 ngày 15/11/2026 (UTC+07), **0.44 giờ** (bắt đầu 13:47:00 theo lead); phiếu **8 giờ ƯỚC TÍNH**, độ khó **kho**. C-M2C-01…05 đã cụ thể ở mục Cần Core: port tin cậy, nguồn hoàn tất, kho ACL, chứng cứ hai lớp và cửa Cloud chặn đường cũ. Không có câu chờ Anh mới; Cloud vẫn tắt, không sửa Core/SDK/schema chung/nguồn cũ/dependency.

## MASK-2b — sửa theo kiểm độc lập, 15/11/2026

- **Đạt phạm vi sửa**, đã kiểm bằng Core giả (CoreGia). Kết luận bàn giao 09:42 trước đây bị lead bác; lần sửa bắt đầu 09:47. Chỉ hai tệp runtime, không đổi ngăn/cấu hình/từ điển chung. PR: **chờ lead mở**; không commit/push. [Báo cáo](BAO-CAO-MASK-2b.md), [lệnh kiểm thật](KET-QUA-KIEM-MASK-2b.txt).
- Chấm điểm có căn cứ: ≥8 che, 4–7 con_sot chặn, <4 bỏ qua. Bổ sung họ hiếm theo lệnh lead, âm tiết tên/đệm và cụm ghép tự soạn; danh xưng đầy đủ/viết tắt; tên Latin có ngữ cảnh chặn. Giữ `số 01/2026`. Hai script DEMO chuyển nguyên nội dung vào `LUU-TRU/rv_mask_2b`, 73 literal thành pytest tham số hóa, không thực thi script tham khảo.
- t9 **6/32 lọt → 0/32** (30 tiếng Việt: 22 chặn/8 che; 2 nước ngoài: đều chặn). t10 **28 chặn + 1 che thừa → 2 chặn, 0 che thừa**, báo nhầm **29/41 → 2/41 (4,88%)**, đếm cả ca mập mờ. Còn ca 2 `lê thị hoa đơn gốc` và ca 7 số sổ cái 331 bị lớp nhãn tài khoản cũ chặn; chi tiết lý do trong báo cáo/số đo.
- **717 passed, 190 subtests passed, 0 skipped, 43,68 giây, mã 0** (172 test mới + 545 cũ); Cf/bí danh/bốn ví dụ/recall cũ đều đạt. Adapter DEMO **2/2, mã 0**; kiểm độc lập **ĐẠT, mã 0**. CLI SDK chuẩn **0/2, mã 1** vì thiếu nguồn quyền. Chưa kiểm Core thật/Linux/Cloud.
- Tập đo cũ vẫn 1/14 và 2/30 báo nhầm, không tăng. Thời gian 09:47:00–10:15:57 ngày 15/11/2026 (UTC+07), **0.48 giờ thực tế**; không có ước tính riêng lượt sửa MASK-2b, MASK-2 gốc 3 giờ ước tính. Cần Core/Chờ Anh mới: **không**, các phụ thuộc tích hợp giữ nguyên.
- **Nợ còn lại:** tên nước ngoài không ngữ cảnh, tên nối gạch/nháy, N.V. An, họ/tên ngoài danh sách hoặc trùng địa danh/cụm thường; phân biệt số sổ cái 331 với tài khoản ngân hàng ở bộ nhãn chung. Không coi số đo này là recall vận hành hoặc đủ điều kiện bật Cloud.

## MASK-7 — bàn giao khảo sát, 15/11/2026

- **Kết luận: Đạt phạm vi khảo sát/test DEMO; chưa đạt nghiệm thu chung CLI SDK chuẩn.** PR: **chờ lead mở**. Không commit/push; không thêm mã chạy, UI, dependency hoặc năng lực tệp. Báo cáo: [bằng chứng/phương án/trần](MASK-7-KHAO-SAT-TEP.md); [số đo](SO-DO-MASK-7.json); [kết quả lệnh thật](KET-QUA-KIEM-MASK-7.txt).
- **Đã làm:** bảng Word 6 vùng và Excel 8 vùng; 16 test chứng minh hỗ trợ/giới hạn từ nguồn repo. Word accept có thể giữ nguyên byte; Excel formula/link có disclosure vẫn có thể xuất tên gốc; values-only cắt ô/đổi sheet. Sửa hai mô tả NGUON về hiện vật đã ra LUU-TRU. Nhánh chết trong chốt kho đã được lát trước bỏ, không cần sửa mã.
- **Đã kiểm bằng Core giả (CoreGia):** adapter văn bản **2/2 ĐẠT, mã 0**. CLI `python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` **0/2 ĐẠT, mã 1** vì thiếu nguồn quyền tin cậy, không thành công giả. Pytest toàn `e_mask/tests`: **438 passed, 190 subtests passed, 0 skipped, 32.52 giây; mã 0**. Khảo sát riêng **16 passed, 0 skipped, 0.28 giây; mã 0**. `kiem_doc_lap.py` **ĐẠT, mã 0**. Khối lệnh phiếu **14/14**, UTF-8 **9/9**, AST **3/3**, SHA nguồn LF **5/5**, `git diff --check` mã 0.
- **Đo:** 12 ca, 11 hoàn tất và 1 timeout tiến trình đo 60 giây (văn bản 500.000 ký tự đa dạng có tracemalloc); không bịa RAM/thời gian hoàn tất cho ca đó. Ca lặp 500.000 → 927.097 ký tự, 41.689126 giây có đo cấp phát, peak OS 167.227.392 byte. Helper tệp chỉ kiểm độc lập, không phải năng lực tệp qua CoreGia. Cần đo tải/máy đích/biên trước chốt trần production.
- **Thời gian thực tế:** 08:59:00–09:16:54 ngày 15/11/2026 (UTC+07), 0.30 giờ thực tế; phiếu MASK-7 2 giờ ước tính. Lượt khảo sát đầu sửa tên trường sai trong test; lượt đo đầu timeout, đã ghi riêng và chạy lại để lưu đủ ca. Không sửa nguồn cũ.
- **Lệch phiếu/quyết định tạm:** không triển khai phần thiếu; đề xuất B ZIP/XML whitelist, tách MASK-8…11 thành 8 lát con **54–80 giờ ước tính mới**, tổng triển khai **85–111 giờ ước tính** nếu Anh chọn đủ B. Phương án A chờ lead cung cấp closure sạch, C giữ văn bản. Trần đề nghị chỉ là tập thử cần phê duyệt/đo biên, không là ngưỡng đã chứng minh; chưa áp dụng manifest/handler. 20/80 MiB và JSON 4 MiB chỉ là mốc kỹ thuật cũ.
- **Chờ Anh/lead:** chốt trần vào/ra/ZIP và nguồn/phương án + giờ MASK-8…11. Chưa chốt thì không code; thiết kế lỗi `MASK_TEP_CHUA_HO_TRO`/`MASK_TEP_CHUA_CHOT_GIOI_HAN` bằng LoiNghiepVu, không thành công rỗng. PDF chọn tệp từ chối rõ; scan để Core OCR, Mask không gọi OCR.
- **Chưa kiểm:** Core/ngăn/quyền/browser thật, Linux thực tế, Word/Excel mở thật/giữ bố cục/mở che sau AI sửa, PDF/chuỗi OCR, ZIP và các trần đề xuất tại biên, Cloud/Junsky/danh mục thật. 0 lượt Cloud/engine khác. Cần Core mới ở mục tương ứng: quyền tệp cùng việc, trần upload/download/output/budget job và luồng có hủy.

## MASK-3b — sửa an toàn theo kiểm độc lập, 15/11/2026

- Phạm vi theo lệnh lead lúc **08:25 ngày 15/11/2026 (UTC+07)**; PR: **chờ lead mở**, không commit/push. Giữ nguyên `_chung/**`, `ngan.py`, `cau_hinh.py`, nguồn cũ và hợp đồng chung.
- Bỏ mọi Unicode Cf và variation selector trước dò NFC; giữ ánh xạ về nguyên văn, che cả ký tự vô hình chen giữa định danh. Dò bổ sung tên qua tab/xuống dòng; kiểm NFD/NBSP, MST/STK và bảo toàn tiền/ngày. Kết quả không còn ký tự vô hình; phong bì chặn nếu còn, vị trí không ánh xạ được trả `MASK_DAU_VAO`.
- Bí danh tạm chỉ thuộc yêu cầu sinh ra nó, không tái dùng giữa hai yêu cầu; không ghi tham chiếu chéo. Mã chính thức đã duyệt vẫn dùng được trong cùng pháp nhân. Danh sách chờ không tăng số cụm mới khi chỉ cấp alias tạm khác cho cùng cụm. Giữ retry/CAS/đếm gặp/duyệt/từ chối/dọn.
- Lỗi bất ngờ của ngăn/port được bọc bằng thông điệp cố định và `raise ... from None`; test bắt stdout/stderr cả che/mở/duyệt/lỗi. Công ty đã duyệt giữ mã Junsky; chốt từ chối bản che không đạt thay nhánh đóng yêu cầu không được dùng.
- Chuyển nguyên `kho_tam.py`, `cau_hinh_may.py`, `schemas/cau_hinh_may.schema.json` sang `e_mask/LUU-TRU/mask_truoc_ngan/`; chỉ test lịch sử nạp qua helper ngoài gói. Kiểm độc lập chặn mã đọc biến cấu hình máy và import mã lưu trữ. `git mv` bị sandbox từ chối do Git index ngoài worktree; đã dùng Move-Item, giữ nguyên byte; **lead stage rename khi commit**.
- Tách nhóm để lead review, do các phát hiện nằm ở nhiều lớp: **A** Unicode/phong bì: `types.py`, `che_van_ban.py`, `phong_bi.py` (3 tệp); **B** quyền alias/lỗi cổng: `kho_qua_core.py`, `kho_ngan.py`, `chay.py` (3 tệp); **C** chuyển lưu trữ: 3 hiện vật, không sửa nội dung. Test/tài liệu ngoài giới hạn 5 tệp mã mỗi nhóm.
- **Đã kiểm bằng Core giả (CoreGia)**: pytest **422 passed, 190 subtests passed, 0 skipped**, 31.39 giây; adapter DEMO **2/2**, Node/KttCore giả **4/4**, kiểm độc lập và `git diff --check` mã 0. CLI SDK chuẩn **0/2, mã 1**, vẫn chặn thiếu nguồn quyền thật; không đổi cổng để vượt kiểm. [Báo cáo sửa an toàn](BAO-CAO-SUA-AN-TOAN-MASK-3b-6.md) và [kết quả lệnh thật](KET-QUA-KIEM-SUA-AN-TOAN-MASK-3b-6.txt) có đủ các lệnh AGENTS.md §5 và lệnh lead yêu cầu.
- Thời gian phiên: **08:25:00–08:54:41 ngày 15/11/2026 (UTC+07), 0.49 giờ**; MASK-3b ước tính **3 giờ**, không có dự toán riêng cho vòng sửa này. Chưa chạy Linux/Core thật hoặc Cloud.

## MASK-3b — nối ngăn chung NGAN-0, 15/11/2026

- **Xong phạm vi nối NGAN-0; đã nối ngăn chung NGAN-0** (PR chung #34 đã gộp). PR: **chờ lead mở**; không commit/push. Giữ nguyên `_chung/**`, hai tệp mẫu trong gói và các test an toàn MASK-5; 0 lượt Cloud.
- Khai báo đủ năm bảng từ `KHAI-SDK-2.1.json/ngan_du_lieu`, dùng khóa `bang`; đọc TrangNgan/KetQuaLenh, view pháp nhân và cấu hình dict/None theo mẫu. RAM mặc định có khai báo, giữ ngăn được cấp; không thay đổi phạm vi engine của bảng định danh chung.
- Giữ mã/thông điệp/khả năng thử lại của ngoại lệ chung tại biên SDK và khi đọc snapshot. Xung đột nghiệp vụ vẫn `MASK_XUNG_DOT`. Mất ACK vẫn `ChuaRo`, giao lại không đếm lặp. Dọn trường cũ bằng xóa/tạo lại có CAS trong cùng lô; tính đủ trần 100 lệnh.
- Bật cả hai test so băm mẫu; mẫu và bốn từ điển đều so sau đổi CRLF thành LF, không skip. Chỉ sửa năm tệp mã/khai báo (chưa tính test/tài liệu), không thêm dependency.
- **Đã kiểm bằng Core giả (CoreGia)** trên Windows/Python 3.13.14, SDK 2.0.0 từ wheel offline đã khớp SHA256SUMS; pytest 9.1.1 có sẵn. Chưa kiểm Linux thực tế/Core thật. Phiên nối này **08:10:00–08:19:24 ngày 15/11/2026 (UTC+07), khoảng 0.16 giờ**, so với MASK-3b **3 giờ ước tính** trong phiếu; không có dự toán riêng cho lần nối lại.

Kết quả thật, dùng `.venv/Scripts/python`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chưa xác minh được phiên và quyền xử lý yêu cầu."
[LỖI] Mở che DEMO: "Chưa xác minh được phiên và quyền xử lý yêu cầu."
0/2 ĐẠT; mã thoát 1: CLI SDK 2.0 chưa tiêm quyền tin cậy.

python e_mask/tests/chay_demo.py
[ĐẠT] Che văn bản DEMO XONG
[ĐẠT] Mở che DEMO XONG
Đã kiểm bằng Core giả (CoreGia).
2/2 ĐẠT; mã thoát 0: cổng thay thế có sẵn, tiêm ngăn/quyền DEMO ngoài gói.

python -m pytest e_mask/tests -q --basetemp=.pytest-tmp
280 passed, 190 subtests passed in 33.00s
Mã thoát 0; 0 skipped, gồm test Node/KttCore giả và các test an toàn cũ.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát 0.
```

Lệch/giới hạn: dùng cổng DEMO thay thế theo lệnh giao, không coi CLI SDK chuẩn đã đạt. Cần Core mới: không; các việc ngăn thật/quyền/mã ổn định/lease, HMAC, lô lớn và nạp màn vẫn ở mục Cần Core bên dưới. SHA-256 LF của tệp bàn giao ghi trong `goi/e_mask/NGUON.md`.

## MASK-0 — 14/11/2026

- Xong khung MASK-0; PR: **chờ lead mở**. Hai năng lực văn bản trả `CHUA_LAM`, chưa kích hoạt vận hành. Cấu hình chỉ chấp nhận đối tượng rỗng, chờ whitelist tài nguyên detector; Linux dùng đường DEMO tường minh.
- Đã kiểm bằng Core giả (CoreGia): hai handler trả lỗi, không báo `XONG`; cổng DEMO nghiệp vụ **chưa đạt** do stub. `kho_tri_thuc_sdk.thu`: 0/2 ĐẠT, mã thoát 1; pytest: 9 passed, 0 skipped; kiểm độc lập: mã thoát 0.
- Mã cũ giữ nguyên; hiện vật không mang sang gói theo mục MASK-P để lead xem xét lưu trữ sau. Nhu cầu Core đã ghi bên dưới; MASK-0 không phát sinh yêu cầu mới.

## MASK-1 — 14/11/2026

- **Xong phạm vi lõi thuần**, chỉ DEMO; PR: **chờ lead mở**. Bắt đầu 23:53 ngày 14/11/2026, kết thúc 00:03:55 15/11/2026 (UTC+07), khoảng **0.18 giờ thực tế**, so với **3 giờ ước tính** trong phiếu. Lát qua nửa đêm; giữ ngày giao 14/11 theo handoff.
- Chép đúng năm tệp `nguon/privacy/{__init__,types,core,company_names,person_names}.py` vào gói. Giữ KnownText, chuẩn hóa/vị trí, tên dài ưu tiên, bảo vệ số, numeric_review; hỗ trợ NFC/NFD bằng bản dò có ánh xạ vị trí gốc. Đổi sang `[[...]]`, giữ mã Junsky, không cắt số thứ tự lớn. [NGUON.md](../goi/e_mask/NGUON.md) có đường nguồn, SHA byte trước/sau và SHA LF cho checkout Linux/Windows.
- Bản chép đã tách encrypt/decrypt bảng, xuất Word/TXT/ZIP và import cryptography/python-docx. Không thêm thư viện chạy ngoài SDK. Detector import khi gọi; thiếu thì từ chối, không trả kiểm giả. `suggest` chỉ gợi ý thủ công có trần 500 dòng, không dùng che tự động. Phần nguồn cũ giữ nguyên, để lead xét chuyển lưu trữ sau, không xóa/di chuyển.
- **Đã kiểm bằng Core giả (CoreGia)**: pytest **54 passed, 0 skipped**, mã 0; gồm 9 ca MASK-0 và 45 ca MASK-1. Kiểm độc lập **ĐẠT**, mã 0. Ca thuần kiểm NFC/NFD/khoảng trắng/vị trí, tên dài, giữ Junsky, số tự sinh lớn, mã số DEMO không nhầm tiền/ngày, giữ `1.000.000 VND` và `30/10/2026`, phát hiện mất/thêm/đổi số; import sạch chỉ với thư viện chuẩn không đọc tài nguyên/ghi tệp/chạy nguồn ngoài.
- Cổng vẫn giữ nguyên hai handler MASK-0, trả `LoiNghiepVu("CHUA_LAM", "Chức năng này chưa được hoàn tất.")`, không xuất văn bản hoặc cụm gốc. CLI SDK **0/2 ĐẠT, mã 1** do hai stub theo phiếu; **chưa đạt DEMO nghiệp vụ, chưa hoàn tất che/mở che, chưa kích hoạt vận hành**. numeric_review chưa thay hậu kiểm tiền/ngày độc lập ở MASK-2.
- Lệch nền checkout: lúc bắt đầu nhánh chưa chứa MASK-0. Đã khôi phục đúng 10 tệp `e_mask/` từ commit `c3e68148b5db837912a40ea39aa4539f53c3fca0` (đọc Git object vào worktree; giữ nguyên năm tệp mã/phiếu của MASK-0). Lệnh Git restore không ghi được index của worktree ngoài vùng cho phép nên dùng đọc object; không đổi index, không commit/push. Lead đồng bộ dependency trước khi mở PR để diff MASK-1 chỉ còn năm tệp lõi, test và tài liệu.
- Quyết định tạm: dùng họ tiền tố MASK đã có trong fixture cũ, chỉ cho helper DEMO; còn chờ lead xác nhận không trùng mã Junsky thật. Kho cấp mã chung/kiểm quyền thuộc MASK-3. Không có yêu cầu Core mới phát sinh; các mục Cần Core phía dưới giữ nguyên.

Ba lệnh bắt buộc đã chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1 (0/2 ĐẠT, đúng giới hạn stub của MASK-1).

python -m pytest e_mask/tests -q
54 passed in 0.59s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

## MASK-2 — 14/11/2026

- **Xong phạm vi lõi detector/hậu kiểm**, chỉ DEMO; PR: **chờ lead mở**. Bắt đầu **00:06 ngày 15/11/2026**, kết thúc **00:19:10 ngày 15/11/2026** (UTC+07), **0.22 giờ thực tế**, so với **3 giờ ước tính** trong phiếu. Giữ ngày giao 14/11 theo handoff.
- Đúng năm tệp mã chạy: chép `nguon/privacy/detectors.py`, `leftovers.py`, `che_van_ban.py`; sửa `core.py`; thêm `tai_nguyen.py`. Tận dụng toàn bộ test_che_van_ban và kho RAM DEMO chuyển vào `tests/ho_tro_kho_demo.py`, bỏ import tests/tools/Core cũ. Chỉ sửa `e_mask/`, giữ nguyên `ma-nguon/` và các bản tham chiếu; không commit/push.
- Giữ trần 500.000/500/300/20, KnownText/NFD/vị trí, nhãn nhiều dòng, hậu kiểm regex độc lập detector, Counter tiền/ngày của bản gốc đầy đủ, số bắt đầu 0/MST/tài khoản theo ngữ cảnh. Ca 501 email DEMO che đủ 501. Chuỗi bệnh lý chưa kiểm hết chặn văn bản; bí danh hỏng không che khuất dấu vết tên/tiền/ngày. numeric_review dùng NUL giữ ranh giới số, mở che giữ mã chữ thường/dấu chấm/gạch nối, không bắt mã nằm dính trong chữ khác.
- Bốn nguồn sạch chưa có: mặc định `MASK_THIEU_TAI_NGUYEN`. `nap_cau_hinh` chỉ nạp whitelist tin cậy (đường tuyệt đối ngoài gói + SHA-256), đủ bốn tệp, snapshot nguyên bộ; lỗi/thu hồi cấu hình xóa cache cũ. Không có nguồn tải, từ điển thay thế hoặc fallback vận hành. Từ vựng DEMO được mock tường minh ngoài gói, xóa cache mỗi ca. Hàm nạp là cấu hình nội bộ dành cho adapter sau; chưa mở schema cấu hình máy MASK-0 hoặc cho payload tự cấp whitelist/quyền.
- Còn sót/lỗi detector/chưa kiểm đủ/tiền-ngày thay đổi → không công bố văn bản. Mở che thêm kết quả kiểm nội bộ, không đóng yêu cầu nếu kiểm tiền/ngày thất bại; không thay mẫu 1–4 hoặc manifest. Adapter MASK-5 phải đổi kết quả chặn sang `LoiNghiepVu` mã `MASK_DINH_DANH_CHUA_DAT` hoặc `MASK_TIEN_NGAY_THAY_DOI`, câu cố định, không dùng nội dung gốc/str(lỗi). Kho/quyền chỉ là port được bên tin cậy tiêm, không tự cấp mã yêu cầu hoặc xác thực.
- **Đã kiểm bằng Core giả (CoreGia)** ở đường stub; lõi kiểm bằng fixture kho/từ vựng DEMO ngoài gói. Pytest **149 passed, 190 subtests passed, 0 skipped**, mã 0, **15,69 giây**. Bao gồm đúng/vượt trần, 501 cụm, NFD/vị trí, nhãn nhiều dòng, mất/thêm/đổi tiền-ngày, thiếu từng tài nguyên, whitelist/SHA/cache, lỗi detector, bí danh hỏng. Ba chuỗi 500.000 ký tự `1; `, `1, `, `1 ` đo **1,685 / 1,737 / 2,433 giây**; giữ ngưỡng cũ **≤5 giây xử lý, timeout tiến trình con 12 giây**. Đo trên Windows/Python 3.13.14; chưa chạy Linux thực tế, test dùng API đa nền tảng.
- CLI SDK vẫn **0/2 ĐẠT, mã 1** do hai stub `CHUA_LAM` theo phiếu. Kiểm độc lập **ĐẠT, mã 0**, không tệp biên dịch/tham chiếu bị cấm. `git diff --check` mã 0. SDK **2.0.0**, cài offline wheel `--no-index --no-deps`, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Dùng venv riêng với công cụ pytest sẵn có qua system-site-packages, không thêm dependency chạy.
- **Giới hạn:** heuristic có thể bỏ lọt tên người viết thường không nhãn; có test ghi nhận giới hạn, không coi kết quả “không tìm thấy” là bằng chứng đủ điều kiện Cloud. Nguồn sạch/quyền/kho Core thật chưa có, cổng DEMO nghiệp vụ chưa đạt; 0 lượt Cloud và không gọi engine khác.
- Lệch phiếu: không mở rộng phạm vi; thêm kiểm tiền/ngày nội bộ khi mở để chặn dữ liệu kho bất thường. Chờ lead whitelist bốn tài nguyên. Không phát sinh yêu cầu Core mới; kênh cấu hình/ngăn/quyền đã nằm trong mục **Cần Core**.

Ba lệnh kiểm bắt buộc đã chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` (pytest thêm `-s` để ghi số đo hiệu năng):

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1; 0/2 ĐẠT, đường stub theo phiếu MASK-2.

python -m pytest e_mask/tests -q -s
Hiệu năng '1; ': 1.685 giây
Hiệu năng '1, ': 1.737 giây
Hiệu năng '1 ': 2.433 giây
149 passed, 190 subtests passed in 15.69s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

## MASK-3 — 14/11/2026

- **Xong phạm vi port/kho tạm/chống trùng**, chỉ DEMO; PR: **chờ lead mở**. Giữ ngày giao 14/11 theo handoff. Bắt đầu **00:22 ngày 15/11/2026** (UTC+07); mốc kết thúc và giờ thực tế ghi tại đoạn cuối mục này. Phiếu ước tính **5 giờ**, chưa phải số đo. **Chưa đạt điều kiện nghiệm thu chung** vì hai DEMO ở CLI SDK vẫn là stub thuộc MASK-5.
- Đúng bốn tệp mã chạy: `kho_tam.py`, `kho_dinh_danh.py`, `kho_qua_core.py`, `quyen_yeu_cau.py`. Tái dùng protocol `Kho` của MASK-2 và snapshot/nhật ký/chốt của `ma-nguon/kho_qua_core.py`; không phục hồi cổng cũ hoặc tự đặt API ngăn. `ma-nguon/`, các bản tham chiếu, SDK và Core giữ nguyên; không commit/push.
- `KhoTam` dùng `KTT_ENGINE_DU_LIEU`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\e_mask\du-lieu\` trên Windows; Linux cần đường DEMO tuyệt đối tường minh. Khóa tệp riêng bằng khóa đa tiến trình của hệ điều hành, JSON đọc/đổi/ghi trong cùng khóa; ghi tạm, flush/fsync, `os.replace` cùng thư mục. Từ chối tệp hỏng, đường trong gói/liên kết và lỗi đọc/ghi/khóa bằng `MASK_KHO_TAM_LOI`, không tự tạo kho RAM thay thế. Mã opaque cũng băm trước khi lưu; schema đóng chỉ có băm và mã trạng thái số. Không lưu tên gốc, danh mục, bảng ánh xạ, toàn văn, nội dung che hay kết quả mở che.
- Kho lâu dài và quyền là port nội bộ **chưa có transport SDK 2.0**. Mặc định thiếu kho → `MASK_KHO_CHUA_NOI`; thiếu danh tính tin cậy → `MASK_NGU_CANH_CHUA_XAC_MINH`. Không nhận danh tính từ đầu vào/tham số/pháp nhân. `NguCanhTinCay` do bên cấp quyền tiêm, gắn phiên/module/người/tài liệu/vùng; Core giả cấp mã yêu cầu/lượt ổn định theo việc/bước. Không ép mã opaque thành UUID/64 ký tự, không đưa `lan_thu` vào khóa. Mã yêu cầu mở thiếu/sai/đã đóng hoặc sai chủ bị từ chối.
- Giữ hai thao tác port cũ `snapshot_luot`, `chot_luot`; `chot_luot` với nhật ký rỗng là cửa đọc lại lượt đã chốt, vẫn kiểm quyền. Bên cấp quyền được gọi lại tại snapshot/chốt/đọc lại; port kho phải tự kiểm quyền/lease trong giao dịch. Bảng chung toàn tập đoàn, tách vùng DEMO/thật; không chia theo pháp nhân hoặc giới hạn bảng tra vào bí danh đã tham chiếu của một yêu cầu.
- Nhật ký trong RAM chỉ gửi về kho được phép. Bên kho giả chốt nguyên tử alias/hàng chờ/đếm gặp/tham chiếu/yêu cầu/kết quả, CAS xung đột → `MASK_XUNG_DOT`, `thu_lai_duoc=True`. Lượt đã chốt chỉ đọc từ port, không chạy lại callback/cấp alias/đếm mới. Kết quả đọc lại vẫn qua chặn an toàn. Tiền tố cấp bí danh MASK-3 nằm một chỗ tại `TIEN_TO_TU_SINH = 'MASK'`; chỉ DEMO, còn chờ Anh xác nhận không trùng Junsky thật. Không đổi matcher/tiền tố của lõi MASK-1…2 ngoài phạm vi lát.
- Trước chốt ghi dấu mã/băm. Bên lưu trữ đã nhận chốt mà chưa trả → lưu mã trạng thái chưa rõ, băm chốt và mã tương quan suy từ mã lượt đã băm, rồi `raise ChuaRo`. Khởi động lại/giao lại luôn hỏi snapshot port trước; nếu kho còn đang chờ thì tiếp tục `ChuaRo`, không chạy nghiệp vụ lại. Không phục hồi kết quả từ JSON. Dấu cục bộ nói đã chốt nhưng port mất trạng thái → từ chối xung đột. Mất ACK kết quả SDK do chính SDK gửi lại; không có vòng gửi cũ.
- `KhoBoNho` chuyển từ helper MASK-2 vào `tests/ho_tro_core_gia.py`, ngoài gói chạy; helper cũ chỉ chuyển tiếp import để giữ test. Fixture kho/quyền gắn phiên/module/người/tài liệu và cấp mã, không nhận cờ tự khai từ payload. Hai vùng trong test đều là dữ liệu giả; nhãn `THAT` chỉ để kiểm tách vùng, không có hồ sơ thật. Không thêm dependency chạy ngoài SDK/thư viện chuẩn.
- **Đã kiểm bằng Core giả (CoreGia)** và port kho/quyền giả: **225 passed, 190 subtests passed, 0 skipped**, mã 0, **19,91 giây**. Đủ **11/11 vector_kho_luot.json nguyên bản**; snapshot/nhật ký/bản sao; hai tiến trình tranh ghi JSON và hai tiến trình engine chốt cùng bên kho giả (một chốt, một xung đột, sau retry dùng cùng alias); rollback tại sáu mốc; gặp lại/chống đếm lặp; sai module/người/tài liệu/vùng/mã và thu hồi quyền ở từng cửa; bảng chung; `ChuaRo` sau commit hoặc nguồn còn chờ; mất 1 và cả 4 ACK kết quả SDK, giao lại cùng việc/bước và khởi tạo lại engine. Kiểm byte mọi tệp kho tạm không chứa tên/toàn văn DEMO, kể cả sau mở che.
- Chạy trên **Windows/Python 3.13.14**, chưa chạy Linux thực tế; mã/test có nhánh Windows/Linux và multiprocessing `spawn`. Các kiểm này **không phải bằng chứng bền PostgreSQL, RLS, CAS hoặc quyền Core thật**. Bốn tài nguyên sạch và kho/quyền thật vẫn chờ; 0 lượt Cloud, không gọi engine khác. Duyệt/từ chối/dọn thuộc MASK-6, handler nghiệp vụ thuộc MASK-5; chưa tự nối vào manifest.

Ba lệnh kiểm bắt buộc chạy bằng `.venv/Scripts/python`, với `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; venv cài SDK offline từ wheel đã so SHA256SUMS, phiên bản 2.0.0. Công cụ pytest dùng bản có sẵn qua system-site-packages:

```text
python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chức năng này chưa được hoàn tất."
[LỖI] Mở che DEMO: "Chức năng này chưa được hoàn tất."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1; 0/2 ĐẠT, hai stub chưa nối thuộc MASK-5.

python -m pytest e_mask/tests -q
225 passed, 190 subtests passed in 19.91s
Mã thoát: 0; 0 skipped.

python e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát: 0.
```

Lệch phiếu / quyết định tạm: không mở rộng tập bốn tệp mã; giữ adapter tạm chỉ trong tests để kiểm port qua CoreGia, hai handler sản phẩm vẫn stub. Không tự đặt API ngăn khi SDK thiếu transport; Cần Core được cụ thể hóa bên dưới. **Thời gian thực tế:** bắt đầu 00:22, kết thúc **00:50:53 ngày 15/11/2026** (UTC+07), **0.48 giờ**, so với **5 giờ ước tính** trong phiếu.

## Nợ từ kiểm MASK-2 — ghi nhận 14/11/2026, không vá trong MASK-3

- **Nợ CAO tên người viết thường không nhãn: đã đóng trong phạm vi MASK-2b — 15/11/2026**, đã kiểm bằng Core giả (CoreGia); PR: **chờ lead mở**. Họ trong từ điển, tổng 2–4 âm tiết được dò sau bỏ dấu/hoa thường; ca nghi ngờ chặn phát hành bằng `con_sot`, không trả `van_ban_da_che`. Không dùng kết quả DEMO để xác nhận đủ điều kiện bật Cloud. Giới hạn/ngoại lệ và số đo thật tại [báo cáo MASK-2b](BAO-CAO-MASK-2b.md).
- Tên viết tắt dạng **N.V. An**: còn nợ kiểm nhận diện/hậu kiểm; không coi MASK-3 là đã xử lý.
- Khác biệt **numeric_review với NUL**: cần đối chiếu riêng với nguồn, giữ ranh giới số và chứng minh tiền/ngày; không sửa trong lát kho/quyền.
- **Báo nhầm nền đo ở MASK-2b:** 1/14 mẫu cũ che thừa chữ DEMO; tập bổ sung có 1 câu ngày ISO bị lớp số/ngày cũ chặn và 1 câu che thừa chữ DEMO. Đã có trước MASK-2b, không tăng trên hai tập đo; giữ nguyên và ghi chi tiết trong báo cáo, chưa sửa ở lát tên người.

## Cần Core (chuyển lead Core qua Anh)

### Cụ thể hóa MASK-2c-3 — 15/11/2026

- **C-M2C-01/03:** nối `tao_app(cong_hau_kiem_ai=...)` với `CongHauKiemAI`. Các phương thức `kiem_quyen`, `kiem_han`, `chung_thuc`, `ban_giao` là port nội bộ đề nghị, **chưa phải API/transport SDK 2.0**. Quyền phải được kiểm nguyên tử ngay trong `mo_tep` và từng thao tác, gắn mã yêu cầu/phiên/module/người/tài liệu/pháp nhân/vùng/lease; cùng việc/bước giữ mã lượt ổn định khi giao lại. Không dùng cờ caller/model làm quyền hoặc chứng cứ.
- **C-M2C-02/03:** Core giữ tập JSON chuẩn `mask-2c-phan-hoi.json` có `phien_ban`, `ma_yeu_cau`, `ke_hoach`, `phan_hoi`. Mỗi phần gồm nguyên phong bì `yeu_cau_ai`, `tra_loi_ai` và `nguon` (`engine`, `nang_luc`, `nha_cung_cap`, `model`, `trang_thai`, `hoan_tat` với `giao_thuc`, `ket_thuc`). Nguồn phải là AI-9/Local/XONG và hoàn tất `stop`; Core chứng thực bytes/băm từng cặp từ sổ nguồn, kế hoạch và snapshot gốc, không tin nội dung `nguon` tự khai trong tệp. Giữ nguyên phản hồi gốc; bản giao cuối chỉ thêm tham chiếu+băm tập phản hồi. `bam_dau_vao` là SHA JSON chuẩn toàn phong bì yêu cầu.
- **Bằng chứng hoàn tất:** AI-9 không thêm finish vào schema chung. Core cần nguồn tin cậy cho hoàn tất transport/API (hoặc chứng thực phiên thực thi AI-9 đã kiểm đủ done/finish), không tạo `stop` từ `khong_thay_can_cu`. Nguồn đã nhận nhưng chưa trả phải `ChuaRo` trước giao bước 3, kể cả nếu còn payload rỗng tạm. Chưa có bằng chứng từ đường thực thì từ chối. Model phải khớp model đã ghim budget trong snapshot; fallback Local khác model cần chuẩn bị/đo budget lại, không tự lấy budget model cũ.
- **C-M2C-04:** `ban_giao` ghi bền, chống lặp chứng cứ nguồn `mask.hau_kiem_ai_cuc_bo@1`, băm đề nghị nguồn/tập phản hồi, số đoạn, SHA phong bì kết quả cuối và SHA văn bản trước ACK. Cửa Cloud kiểm chứng cứ này gắn đúng bytes kết quả và quyền; chặn đường `mask.che_van_ban@1` cũ thiếu lớp 2 dù cùng loại và hai cờ đạt. Không đẩy mã yêu cầu/snapshot/chuyển tiếp/trích dẫn gốc/băm nội bộ lên Cloud; prompt chứa dữ liệu cũng phải qua Mask. **BAT_CLOUD vẫn False**, chưa có cửa thật hoặc phép đo thật.
- **C-M2C-05:** dùng nguyên kho/Ngan CAS hiện có, không thêm bảng. Alias/hàng chờ/dấu gặp/lượt trong một lô nghiệp vụ; >100 lệnh chặn toàn bộ. Core cần staging/chốt nguyên tử chung nếu muốn vượt trần; không chia lô phía engine. Ghi đã nhận mất ACK phải `ChuaRo`, Core đối soát đúng mã/băm trước giao lại; quyền/lease phải bao trùm giao dịch ngăn. Ngăn RAM và adapter ngoài gói không chứng nhận độ bền/RLS thật.
- **Trần nội bộ:** kế thừa profile 1 MiB/phản hồi và đầu vào bước cuối; snapshot và tập phản hồi tối đa 64 MiB/tệp. Vượt từ chối, không cắt. SDK 2.0 tải cả tệp vào RAM trước engine kiểm nên Core còn phải chặn byte/budget RAM/deadline trước tải. Chưa đo context/chất lượng/model/Core thật; MASK-2c-4 và nợ CAO vẫn mở. Không có câu chờ Anh mới.

### Cụ thể hóa MASK-2c-2 — 15/11/2026

- **C-M2C-01:** nối `tao_app(cong_chuan_bi_ai=...)` với port `CongChuanBiAI`, kế thừa quyền kho tệp của MASK-2c-1. Đây là giao diện nội bộ đề nghị, **không phải API/transport đã có trong SDK 2.0**. Core phải kiểm ACL/lease nguyên tử trong từng thao tác, cấp mã yêu cầu ổn định và giữ nguyên phiên/module/người/tài liệu/pháp nhân/vùng qua các bước. Tệp tên kỹ thuật `mask-2c-ho-so.json`, bytes/kích thước/SHA thực; dọn tệp chưa có chỉ mục khi CAS lỗi. Snapshot chuẩn bị bao nguyên `HoSoAI` và kết quả quy tắc đạt, cấu hình prompt, khuôn, profile, biên nhận. Không để Hỏi AI đọc ngăn riêng Mask.
- **C-M2C-02:** Core cung cấp `cau_hinh` từ module/quy trình (mã/phiên bản/prompt chứa `CHI_DAN_BAT_BUOC`, model, provider `local`), ghim từ lần đầu; `kiem_ngan_sach` phải dùng tokenizer/model thực trên gốc Core đang giữ, kiểm **mọi đoạn**, cả prompt/khuôn/đầu ra và thời gian toàn chuỗi. Biên nhận gắn SHA đề nghị đầy đủ, tên tokenizer/model, số token từng đoạn, context/đầu ra, hạn Local và deadline tuyệt đối. `kiem_han` không kéo dài hạn khi retry. `ban_giao` xác nhận snapshot và bytes chuẩn yêu cầu đầu, ghim toàn kế hoạch để Core lặp/ghép đủ đoạn và nguồn. Mask lập đề nghị phủ đủ; Core duyệt/ghim, không coi tự chia đoạn là đã có API chuỗi. Thiếu phương thức/biên nhận/sức chứa/thời hạn thì từ chối, không công bố chạy dài thật.
- **C-M2C-05:** khai bảng ngăn `chuan_bi_ai` theo hằng nội bộ `KHAI_NGAN_CHUAN_BI_AI` (khóa `bam_yeu_cau`, phạm vi engine). Chỉ giữ băm input/đề nghị/biên nhận và tham chiếu+băm snapshot; `lay_hoac_tao` ghim từ đầu, chốt tham chiếu có CAS. Chưa sửa `KHAI-SDK-2.1.json`/manifest bằng khóa SDK chưa nhận. Ngăn Core phải gắn engine/quyền/lease, không đọc chéo engine; kiểm trước/sau ở Mask không thay giao dịch quyền thật của Core.
- **C-M2C-03/04 giữ nguyên:** chứng thực AI-9 Local cho từng đoạn, ghép tập phản hồi và nguồn cuối, hậu kiểm MASK-2c-3, chứng cứ hai lớp trước Cloud còn ở các lát sau. Không có adapter gọi engine khác trong gói. CoreGia chỉ giả quyền/ngăn/tokenizer/deadline; chưa chứng nhận Core thật hay sức chứa model. Không có câu chờ Anh mới.

### MASK-2b sửa kiểm độc lập — 15/11/2026

Không phát sinh yêu cầu Core mới. CLI chuẩn còn thiếu nguồn quyền tin cậy như đã ghi dưới đây; cổng DEMO CoreGia không chứng nhận quyền/ngăn Core thật.

### Bổ sung MASK-7 — 15/11/2026

- Core xác minh tham chiếu tệp con trong JSON thuộc cùng việc và quyền tải vào/ra/kết quả theo module/người/tài liệu. Ngăn/quyền thật và đối soát bàn giao tiếp tục chờ như MASK-6.
- SDK 2.0 đọc trọn `mo_tep` vào RAM: cần giới hạn input/output/upload chung, đếm byte thực/luồng có hủy, budget RAM/thời gian/job/concurrency và lỗi 413 đúng. Trần engine sau đọc không bảo vệ RAM phần tải trước đó. Không sửa Core/SDK trong MASK-7.
- Trần trình Anh và các phương án A/B/C tại [báo cáo MASK-7 §5–6](MASK-7-KHAO-SAT-TEP.md). Các số đề xuất chưa được phê duyệt hoặc kiểm biên; không khai năng lực tệp. PDF yêu cầu tệp thiết kế từ chối rõ; scan để Core OCR, Mask không gọi OCR.

### Sửa an toàn MASK-3b — 15/11/2026

Không thêm API/schema chung. Port snapshot nội bộ nay cung cấp danh sách bí danh tạm được dùng của đúng yêu cầu từ tham chiếu trong ngăn; thiếu thì từ chối dùng bí danh tạm có sẵn. Khi nối Core thật, phải giữ ràng buộc này trong giao dịch và quyền server. SDK vẫn cần nhật ký an toàn cho lỗi ngoài phạm vi handler; engine đã bọc lỗi ngăn/port trong phạm vi được giao. Các phụ thuộc ngăn/quyền thật bên dưới giữ nguyên.

### Bổ sung MASK-3b → MASK-6 — 15/11/2026

- **NGAN-0:** đã nối ngăn chung NGAN-0 ngày 15/11/2026; hai bản trong gói giữ nguyên mẫu, hai test so băm đã bật và chuẩn hóa LF. Không sửa `_chung/**`. Phần còn chờ là ngăn/quyền thật SDK/Core 2.1, không còn chờ mẫu chung.
- **Ngăn SDK 2.1:** cấp `app.ngan`/`viec.ngan`, giao dịch nguyên tử, CAS/duy nhất và quyền trên cả năm bảng engine. Bản khai tại `goi/e_mask/KHAI-SDK-2.1.json`; phiếu SDK 2.0 không thêm trường. RAM mất dữ liệu khi khởi động lại.
- **Quyền/mã yêu cầu:** Core cấp module/người gửi/tài liệu/vùng cùng mã ổn định theo việc/bước; kiểm lease và quyền tại đọc/chốt, kể cả đọc kết quả/tệp đã đóng. SDK 2.0 chưa có nguồn này. CLI chuẩn 0/2 ĐẠT là chặn thiếu quyền; adapter `tests/chay_demo.py` tiêm quyền DEMO mới kiểm được nghiệp vụ.
- **Khóa HMAC do Core cấp:** dấu/băm nội bộ hiện vẫn SHA-256 không muối; chưa tự tạo khóa hoặc đổi băm công bố theo hợp đồng. Cần cổng bí mật/khóa HMAC của Core trước khi làm. Nợ mất ChuaRo khi ghi dấu lỗi đã đóng bằng test lỗi sau khi nguồn nhận chốt.
- **Lô lớn:** API ngăn đề nghị tối đa 100 lệnh. Engine từ chối toàn bộ nếu số thay đổi vượt mức này, không chia lô làm mất nguyên tử. Cần giao dịch lớn/staging có chốt nguyên tử để hỗ trợ tài liệu nhiều cụm; detector không bị cắt ở 500.
- **Màn quản trị:** nạp `ui/duyet_dinh_danh.js` như module; chốt chữ ký hàm nạp/default export và dạng trả `doc/tim/ghi_lo` của KttCore, kiểm `admin_core` phía Core cho mọi lần đọc/ghi; quét/review mã màn. Đã kiểm bằng Node/KttCore giả, chưa có bằng chứng trình duyệt thật.
- **Giao lại:** chỉ lưu định danh/lựa chọn/băm/số đếm vào ngăn, không cache toàn văn hay kết quả AI. Tái tạo kết quả và đối chiếu băm đã chốt; tài nguyên/logic đổi khiến khác kết quả thì chặn `MASK_XUNG_DOT`. Cần cửa đọc lại kết quả gốc có kiểm quyền của Core để đối soát qua các lần nâng phiên bản.
- Trần kỹ thuật JSON mẫu 1/3 là 4 MiB; trần tệp nghiệp vụ/đầu ra và phần Word/Excel/PDF vẫn thuộc MASK-7, chưa triển khai trong đợt này. Nguồn từ điển sạch của lead đã dùng theo lệnh giao mới nhất; không dùng fixture thay thế trên đường handler.

- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Bổ sung MASK-P — 14/11/2026

- Hợp đồng API v1/SDK 2.0 đã khóa; các yêu cầu cổng lịch sử phía trên phải đối chiếu lại theo [phiếu SDK 2.0](GIAO-CODEX-e_mask.md#5-cần-core--chờ-anh-của-engine-này), không khôi phục socket/route/SQL riêng Mask.
- **Ngăn engine + CAS/ghi lô nguyên tử/duy nhất:** bảng tên gốc–bí danh, cụm chờ, yêu cầu và tham chiếu tạm là dữ liệu lâu dài. `kho_tam.py` theo quyết định tạm chỉ lưu mã/băm/số đếm, không được lưu tên gốc/toàn văn/kết quả mở che. Băm không khôi phục tên gốc; khi chưa có port ngăn thì xử lý thật phải `MASK_KHO_CHUA_NOI`, kho DEMO chỉ ở fixture ngoài gói. Cần Core chốt chuyển dữ liệu/cửa 113, 117–120 sang ngăn chung.
- **Danh tính/mã yêu cầu:** SDK hiện chỉ có `viec_id`, `buoc`, `phap_nhan_id`, thiếu module/người gửi/tài liệu đã xác minh. Core phải cấp mã ổn định và kiểm quyền khi snapshot/chốt/mở che/đọc lại/tải tệp; không nhận danh tính tự khai trong tham số/config, không lấy pháp nhân làm quyền mở che. Cần xác nhận tham chiếu tệp con trong JSON cùng việc đi qua `mo_tep`.
- **Chốt và mất ACK (J8b):** đối soát ghi kho/kết quả, giao lại không cấp/đếm/đóng trùng; lượt bền #10 khi bên lưu trữ đã nhận chốt mà chưa trả. Chưa có API ngăn/giữ-chốt-đọc thì chỉ kiểm bằng port giả; không tự khai API mới.
- Kênh cấu hình tới `Engine`, nhật ký/thẻ trạng thái, UI ngăn/màn thử chung chỉ Admin; màn duyệt/lọc kiểu Excel còn thiếu, không tự nối màn riêng cũ. Core kiểm nguồn sinh `van_ban_da_che` và chuỗi Mask → Cloud, kiểm quyền cả đọc kết quả/tệp, không chỉ tin mã loại/cờ caller. Hỏi AI bản 1 vẫn tắt Cloud.
- Tên tám contract lịch sử/`noi_dung_da_che.v1` cần lead đối chiếu cổng mới; không đổi nghĩa lượt/hạn/danh mục của bản đã công bố. Bộ kết quả mở che `truong` không tự nối vào Trích xuất đang nhận `tra_loi_ai`; cần thiết kế riêng nếu có chuỗi đó.

### Cụ thể hóa MASK-3 — 14/11/2026

- **Ngăn/transport chung:** triển khai cổng SDK đọc snapshot, CAS/duy nhất và ghi lô nguyên tử bao trùm định danh/alias mới, hàng chờ, dấu gặp theo yêu cầu, tham chiếu tạm, trạng thái yêu cầu và kết quả. Bốn tệp MASK-3 chỉ định nghĩa port nội bộ, không thêm route/thao tác ngăn công bố. Chuyển bảng lâu dài vào ngăn hạn chế quyền, không lưu tên gốc vào kho tạm.
- **Danh tính và mã ổn định:** Core cấp từ phiên đã xác minh module/người gửi/tài liệu/vùng, gắn việc/bước/lease và mã yêu cầu/lượt; cùng việc/bước giữ nguyên mã qua `lan_thu` và khởi động lại. Kiểm quyền trong cùng giao dịch tại snapshot/chốt/đọc lại, kể cả kết quả/tệp của lượt mở che đã đóng. Mã đã đóng chỉ đọc lại đúng lượt đã chốt, không mở lượt mới. `phap_nhan_id` không làm phạm vi bảng hoặc quyền mở che.
- **Chốt chưa rõ:** port phải phân biệt đã chốt, xác nhận chưa chốt/không còn chốt đang chờ, và đang chờ/chưa biết; trạng thái cuối phải `ChuaRo`. Đối soát theo mã ổn định trước khi xử lý lại, giữ dấu/băm và kết quả ở kho được phép. Bổ sung lượt bền chung #10 khi SDK có; không đổi cơ chế nộp kết quả/ACK vốn do SDK quản.
- **Chứng minh trên hệ lưu trữ thật:** cần kiểm nguyên tử/CAS/rollback/khởi động lại, độ bền và kiểm quyền trong ngăn thật trước nối vận hành. Hai tiến trình với port RAM giả và JSON khóa tệp không thay cho nghiệm thu PostgreSQL/Core thật.

## Chờ Anh / lead — MASK-P

**Cập nhật 15/11/2026:** các mục dưới đây là lịch sử MASK-P. Anh đã chốt ngăn RAM/cấu hình engine, bốn loại chung, chi tiết `van_ban_da_che`, tiền tố MASK và bỏ màn thử riêng. Bốn từ điển sạch đã được lead đặt, lệnh giao mới nhất xác nhận đã duyệt và đã dùng trong MASK-3b…6. Phần còn chờ giữ ở mục Cần Core mới và MASK-7.

- Chốt đề xuất bổ sung `van_ban_da_che` ở [cuối sổ loại riêng](../../_chung/docs/LOAI-DU-LIEU-RIENG.md#3-đề-xuất-mask-p-chờ-anh--chi-tiết-van_ban_da_che), Q1/Q3/Q4 theo phiếu thứ tự; không coi Q2 dành cho OCR là quyền lưu tên gốc của Mask xuống JSON.
- Cấp whitelist bốn tài nguyên detector sạch, chốt tiền tố tự sinh/tạm không trùng Junsky và đặc tả bản xuất danh mục sạch/quan hệ tên khác. Không dùng danh mục thật làm fixture; chuyển thật cần Anh xác nhận số dòng trước/sau.
- MASK-7 trình số đo DEMO, trần tệp/đầu ra, nguồn hoặc phương án cho Word giữ bố cục, sheet/chart Excel và mở che tệp còn thiếu; chỉ triển khai phần thiếu sau khi được chốt, ước lại giờ trước làm.
- Giữ việc chờ duyệt màn thử DEMO/tên contract theo cổng chung; Anh/lead chạy công cụ Windows và bài 11 bước sau khi Core đủ cửa, ca OCR chưa nối ghi “chưa kiểm”.

## Hiện vật không mang sang gói — ghi nhận MASK-P

Vỏ `ma-nguon/chay.py`, `vong_doi.py`, shim, contract bốn mẫu cũ, helper mã hóa bảng và các bản tham chiếu SQL/route/UI không dùng cho gói SDK 2.0. Giữ nguyên, không xóa/di chuyển trong MASK-P; lead xem xét chuyển `LUU-TRU/` sau khi có gói thay thế và kiểm đủ.

## Bàn giao MASK-3b → MASK-6 — 15/11/2026

- **Xong phạm vi triển khai bằng CoreGia/KttCore giả; chưa đạt nghiệm thu chung CLI SDK chuẩn.** PR: **chờ lead mở**. Không commit/push. Chi tiết, API/tham số Ngan và phân lát: [báo cáo bàn giao](BAO-CAO-MASK-3b-6.md).
- Thời gian: **07:39:00–08:09:07 ngày 15/11/2026 (UTC+07), 0.50 giờ thực tế; phiếu 13 giờ ước tính (3 + 2 + 5 + 3).** Không tách thời gian thực tế từng lát trong cùng phiên.
- Đã kiểm bằng Core giả (CoreGia): CLI SDK chuẩn **0/2 ĐẠT, mã 1**, cả hai chặn `MASK_NGU_CANH_CHUA_XAC_MINH` do thiếu nguồn quyền. Adapter `tests/chay_demo.py` với port DEMO ngoài gói **2/2 ĐẠT, mã 0**.
- Pytest với `--basetemp=.pytest-tmp`: **269 passed, 2 skipped, 190 subtests passed, 24.30 giây; mã 0**. Hai skip đúng lý do **“chờ NGAN-0 gộp”**, so băm `ngan.py` và `cau_hinh.py`; các test SHA schema/từ điển không skip.
- Kiểm độc lập **ĐẠT, mã 0**; Node/KttCore giả **4/4 ĐẠT, mã 0**; công cụ chuyển DEMO mặc định chạy khô, mã 0; `git diff --check` mã 0. [Nhật ký đầy đủ](KET-QUA-KIEM-MASK-3b-6.txt). Chưa kiểm Linux thực tế, trình duyệt/Core thật hoặc Cloud.
- Lệch/điểm còn lại: hai bản bọc trong gói chờ mẫu NGAN-0; giữ tệp kho/cấu hình cũ làm hiện vật, không trên đường chạy. Thêm màn duyệt và dùng nguồn sạch theo lệnh mới. Cần Core/SDK: nguồn quyền/mã ổn định, ngăn thật, khóa HMAC, giao dịch trên 100 lệnh, nạp/review màn và đọc lại kết quả qua nâng phiên bản; đã ghi tại mục Cần Core. Không có câu hỏi mới cần Anh duyệt.


## MASK-2b — kiểm held-out và ranh giới Cf (15/11/2026)

PR: **chờ lead mở**. Đã bổ sung bản dò ranh giới Cf và test hồi quy; đã kiểm bằng Core giả (CoreGia). Nợ **CAO vẫn mở**: held-out do lead đo lọt 4/45 tên, báo nhầm 15/75 câu thường (20%); quy tắc và danh sách không bảo đảm 0 lọt, Cloud giữ tắt cứng. Không vá từng ca held-out.

**Cần Core:** nguồn xác minh phiên/quyền cho CLI SDK và tích hợp thật vẫn chưa có; hai ví dụ CLI hiện bị từ chối.

## MASK-2c-P — thiết kế lớp AI cục bộ, 15/11/2026

**Quyết định của Anh 15/11/2026 (nguyên văn): "Thêm AI cục bộ"** — trước khi bật Cloud, thêm lớp AI cục bộ (Local AI) nhận diện tên người như lớp an toàn thứ hai cho Mask.

- **Xong phạm vi tài liệu**; PR: **chờ lead mở**. Chỉ sửa bốn tệp Markdown: phiếu Mask §6, phiếu Hỏi AI §6, sổ loại riêng §6, VIEC.md này. Không sửa runtime/test/schema/manifest/Core/SDK, không commit/push.
- Thiết kế Core điều phối quy tắc MASK-2b → AI-9 hỏi Local trên gốc → Mask đối chiếu/che bổ sung. Không engine-to-engine; kiểm bắt buộc Local ở cả AI-9 và bước 3; mọi lỗi/timeout/ChuaRo/sai khuôn/thiếu đoạn đều không phát hành. Bản quy tắc chỉ là snapshot nội bộ, cửa Cloud tương lai cần chứng cứ bước 3 gắn băm bản cuối. Có map gốc ↔ bản dò ↔ đã che, Cf/NFD, chia đoạn/overlap/gom trùng, mã yêu cầu ổn định, ngăn và quyền snapshot.
- Lập **MASK-2c-1…4 (25 giờ ƯỚC TÍNH) + AI-9 (6 giờ ƯỚC TÍNH), tổng 31 giờ ƯỚC TÍNH**, mỗi lát ≤5 tệp, có độ khó và khối lệnh tự đủ. MASK-2c-P chưa có giờ ước tính riêng trong phiếu giao; không lấy 31 giờ triển khai hoặc 1 giờ MASK-P cũ làm dự toán lát P này.
- Sổ loại chung bổ sung **ĐỀ XUẤT MASK-2c-P, chờ Anh** cho profile trong chuyen_tiep; không tạo loại mới/đổi schema đã duyệt. Core giữ snapshot/tập phản hồi; chưa có cửa tin cậy thì fail-closed, CoreGia chỉ là phép thử. Chi tiết profile cần duyệt; quyết định thêm Local đã có, không hỏi lại quyết định đó.
- Bộ held-out yêu cầu mới hoàn toàn ≥45 tên viết thường +≥75 câu thường (thêm tổ chức/địa chỉ và biến thể Unicode/đoạn), đóng băng gold độc lập trước chạy. Mục tiêu lọt=0 sau hai lớp; báo nhầm bằng tử/mẫu thật, phân biệt chặn nghiệp vụ với lỗi kỹ thuật. Công cụ .cmd mặc định chạy khô do MASK-2c-4 giao làm; **chưa tạo .cmd/chưa chạy Local AI thật** ở lát tài liệu này. Codex không có model thật; Anh chạy bằng DEMO sau triển khai.
- **Nợ CAO MASK-2b vẫn mở:** held-out lead 4/45 lọt, 15/75 báo nhầm (20%). Chưa đo lớp AI, không tuyên bố 0 lọt đã đạt và không bật Cloud.

Kiểm thực tế ngày 15/11/2026 bằng `.venv/Scripts/python -B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; SDK 2.0.0 cài offline từ wheel repo, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. Venv dùng `--system-site-packages` để dùng pytest 9.1.1 sẵn có, không tải mạng/thêm dependency vào gói.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chưa xác minh được phiên và quyền xử lý yêu cầu."
[LỖI] Mở che DEMO: "Chưa xác minh được phiên và quyền xử lý yêu cầu."
0/2 ĐẠT; mã thoát 1 (giới hạn quyền Core đã biết, không nới để làm xanh).

.venv/Scripts/python -B -m pytest e_mask/tests -q
741 passed, 4 xfailed, 190 subtests passed in 24.79s
Mã thoát 0; 0 skipped. Bốn xfail strict là bốn ca tên held-out lớp quy tắc đã biết, không phải kết quả lớp AI.

.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát 0.

.venv/Scripts/python -B e_mask/tests/chay_demo.py
[ĐẠT] Che văn bản DEMO XONG
[ĐẠT] Mở che DEMO XONG
Đã kiểm bằng Core giả (CoreGia).
2/2 ĐẠT; mã thoát 0 (adapter quyền/ngăn DEMO ngoài gói có sẵn).
```

Đã kiểm bằng Core giả (CoreGia) **gói hiện có**, không phải chuỗi Local mới. Chưa kiểm Linux thực tế/Core thật/model thật/Cloud. Regex được giao với MULTILINE|DOTALL đọc **5/5 khối mới**, tổng **13/13** khối phù hợp mã `MASK-2c-\d+|AI-\d+` ở hai phiếu (4 Mask mới +8 AI cũ +1 AI mới); `git diff --check` mã 0. Thời gian thực tế: **11:59:00–12:11:12 ngày 15/11/2026 (UTC+07), 0.20 giờ**. Phiếu giao không có giờ ước tính riêng cho MASK-2c-P; 31 giờ là ƯỚC TÍNH các lát triển khai tương lai.

## Cần Core — bổ sung MASK-2c-P, 15/11/2026

| Mã | Cửa chung cần có | Khi chưa có |
|---|---|---|
| C-M2C-01 | Nút/chuỗi giữ gốc và snapshot bản quy tắc+map, quyền tệp con qua nhiều bước, cấp mã yêu cầu ổn định đúng module/người/tài liệu/pháp nhân/DEMO | Adapter CoreGia ngoài gói; runtime từ chối thiếu quyền/snapshot, không tự mở tệp/đọc kho engine khác |
| C-M2C-02 | Lặp kế hoạch đoạn phủ đủ, cấp yeu_cau_ai từng đoạn, giữ/ghép mọi tra_loi_ai, ghim băm/prompt/khuôn/profile/model; deadline/hủy/ChuaRo và phát lại không trùng | Không công bố chuỗi dài đã chạy thật; thiếu một đoạn không phát hành |
| C-M2C-03 | Chứng thực nguồn AI-9 chỉ Local cho mọi đoạn; bản giao cuối bổ sung tham chiếu tập phản hồi do Core tạo, lưu phản hồi gốc để đối chiếu | Không tin nha_cung_cap/cờ local do caller tự khai; fail-closed |
| C-M2C-04 | Cửa trước Cloud kiểm nguồn Mask bước 3 và chứng cứ hai lớp gắn SHA bản cuối; chặn đường che quy tắc cũ/giả loại, lọc metadata và prompt chưa che | Cloud giữ tắt; không chỉ dựa loai/con_sot/kiem_tien_ngay |
| C-M2C-05 | SDK 2.1 ngăn CAS/lô nguyên tử/chống lặp + bàn giao kết quả và mất ACK, vòng đời snapshot tới khi đóng yêu cầu | Dùng NganBoNho đúng mẫu; mất RAM không giữ chứng cứ đạt, không lưu đệm bền máy engine |

Đây là yêu cầu cho cổng điều phối chung, **không** route/màn/SQL riêng Mask. Chưa sửa Core/SDK trong MASK-2c-P. Ngoài Core: lead xác minh Local server chạy model tại chỗ, chặn egress Cloud và đóng băng gold held-out; chỉ IP riêng/nhãn local không chứng minh server không chuyển tiếp.

## Cần Core — cụ thể hóa MASK-2c-1, 15/11/2026

- **C-M2C-01:** nối port nội bộ `CongHoSoAI` vào kho tệp Core. Core kiểm quyền/lease ngay trong từng thao tác lưu/đọc, gắn đúng mã yêu cầu, phiên, module, người, tài liệu, pháp nhân và DEMO; cấp tham chiếu/kích thước/băm thật. Kiểm trước/sau ở engine không thay được kiểm quyền nguyên tử phía Core. Tên kỹ thuật cố định `mask-2c-ho-so.json`, không tên gốc/path; tệp bất biến, vòng đời tới khi đóng yêu cầu, dọn tệp chưa có chỉ mục khi chốt ngăn lỗi. Chưa có port/quyền/tham chiếu thì từ chối; adapter CoreGia chỉ ở tests.
- **C-M2C-02:** Core cấp kế hoạch đoạn bất biến có các khoảng chính phủ đủ và băm từng đoạn; MASK-2c-1 chỉ lưu/kiểm kế hoạch. Thuật toán lập đoạn, ghim prompt/khuôn/profile, token budget, điều phối và deadline thuộc MASK-2c-2 trở đi; chưa chạy Local thật.
- **C-M2C-05:** thêm bảng chỉ mục `ho_so_ai`, khóa `bam_yeu_cau`, phạm vi engine qua ngăn SDK 2.1. Khai báo nội bộ tạm `KHAI_NGAN_HO_SO_AI` dùng nguyên API NGAN-0; chưa sửa phiếu SDK 2.0/bản mẫu. Chỉ giá trị băm, phiên bản và tham chiếu tệp, không gốc/bản che/map. `lay_hoac_tao` giữ cùng chỉ mục cho retry; khác băm cùng yêu cầu từ chối. Core cần bảo đảm chốt quyền/ngăn/vòng đời tệp; không nhận phép thử RAM là bằng chứng giao dịch Core thật.

Các mục này làm rõ phụ thuộc đã ghi C-M2C-01/02/05, không yêu cầu route riêng và không thêm câu chờ Anh. Profile `chuyen_tiep.mask_2c` đã được lead duyệt 15/11 theo lệnh giao; không hỏi lại các nhãn “chưa duyệt” lịch sử của lát P.

## MASK-P2 — lập lại phiếu tệp theo B, 15/11/2026

**Quyết định của Anh, câu 9 chiều 15/11:** “Cần tệp giữ định dạng → phương án B” trong [_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md](../../_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md). Chọn ZIP/XML Python thư viện chuẩn, whitelist OOXML và từ chối phần lạ; dùng **trần thử nghiệm MASK-7 §5**, đo lại tại biên trước đề nghị vận hành. Không còn chờ Anh chọn lại phương án/trần thử nghiệm; các dòng chờ ở báo cáo/phiếu cũ là lịch sử.

- **Đạt phạm vi tài liệu MASK-P2**, PR: **chờ lead mở**. Chỉ sửa `GIAO-CODEX-e_mask.md` và `VIEC.md`; không sửa code/test/schema/manifest/Core/SDK/nguồn mẫu, không commit/push. Bốn khối MASK-8…11 cũ giữ nguyên nội dung, thêm dòng **THAY BỞI MASK-P2 — 15/11/2026** vào từng khối.
- Phiếu §7 có bảng 10 lát **MASK-B1…B10, 54–80 giờ ƯỚC TÍNH**, mỗi lát ≤5 tệp mã, độ khó `kho`/`vua`, phụ thuộc và khối giao việc tự đủ. Bảng bằng chứng từng vùng chọn che có map hoặc từ chối rõ; comments/revisions/sheet ẩn/chart/formula/link/nhúng/macro/phần chưa kiểm không được giữ với cảnh báo rồi báo che đủ. Giữ bytes phần không chạm; tệp che không sửa mở lại đúng bytes gốc, AI-sửa mở trên bản đang gửi và giữ nội dung mới.
- Văn bản rút từ tệp phải qua **MASK-2b + MASK-2c/AI-9 Local do Core điều phối** trước phát hành; không handler gọi engine khác, không đường tắt quy tắc. Snapshot gốc/map/bản che ở kho tệp Core ACL, chỉ mục qua Ngan/RAM; không lưu máy engine. Cloud giữ tắt. Đã ghi nguồn và SHA LF thực của bốn mẫu ZIP/XLSX/DOCX, yêu cầu **CHÉP + NGUON/SHA**, không import chéo engine; mẫu writer workbook mới/reader chỉ thân không bị nhận nhầm là đã giữ định dạng/quét đủ.
- **B10** giao bộ held-out tệp DEMO mới có gold/SHA, đo mọi biên thử nghiệm, công cụ `.cmd` ASCII mặc định chạy khô; **Anh tự chạy** Word/Excel/Local thật, Codex chỉ kiểm mock. Chưa tạo bộ tệp/công cụ này trong MASK-P2. PDF tách khỏi loạt B, cần phiếu riêng; không nhận đã thực hiện MASK-8b PDF dự kiến cũ.
- Khoảng **54–80 giờ** là ước tính phân rã mới, không phải thời gian thực tế; phân bổ lại phần PDF sang bảo toàn byte/tích hợp hai lớp/held-out. Không gồm 25 giờ MASK-2c +6 giờ AI-9 đã lập phiếu, công Core/SDK/chờ Anh, hoặc mở rộng OOXML ngoài whitelist. Không cộng máy móc tổng dự án 85–111 giờ khảo sát cũ. MASK-P2 **không có dự toán giờ riêng** trong lệnh giao.

Kiểm thực tế bằng `.venv/Scripts/python -B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; Python **3.13.14**, SDK **2.0.0** cài offline từ wheel repo, SHA-256 **a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892** khớp `SHA256SUMS.txt`. Venv `--system-site-packages` dùng pytest **9.1.1** có sẵn, không mạng/dependency mới của gói.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask
[LỖI] Che văn bản DEMO: "Chưa xác minh được phiên và quyền xử lý yêu cầu."
[LỖI] Mở che DEMO: "Chưa xác minh được phiên và quyền xử lý yêu cầu."
Engine e_mask 1.0.0: có ví dụ chạy thử DEMO chưa đạt.
0/2 ĐẠT; mã thoát 1 (thiếu nguồn quyền Core đã biết, không nới handler).

.venv/Scripts/python -B -m pytest e_mask/tests -q
866 passed, 4 xfailed, 190 subtests passed in 62.12s (0:01:02)
Mã thoát 0; 0 skipped. Bốn xfail strict là bốn tên held-out lớp quy tắc đã biết; chưa là phép đo Local.

.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập, không có tham chiếu bị cấm hoặc tệp biên dịch.
Mã thoát 0.

.venv/Scripts/python -B e_mask/tests/chay_demo.py
[ĐẠT] Che văn bản DEMO XONG
[ĐẠT] Mở che DEMO XONG
Đã kiểm bằng Core giả (CoreGia).
2/2 ĐẠT; mã thoát 0 (adapter quyền/ngăn DEMO ngoài gói hiện có).
```

Đã kiểm bằng Core giả (CoreGia) **gói văn bản hiện có**, không phải năng lực tệp B/Local mới. Chưa kiểm Linux thực tế, Core thật, Word/Excel thật hoặc model thật; 0 lượt Cloud. Regex đúng biểu thức trong lệnh giao, dùng MULTILINE|DOTALL, đọc **10/10** khối mới; tổng giờ **54–80**, đánh dấu **4/4** khối cũ và so toàn bộ nội dung cũ còn nguyên sau dòng đánh dấu; SHA LF **4/4** nguồn khớp, `git diff --check` mã 0.

Thời gian thực tế: **13:37:00–13:49:23 ngày 15/11/2026 (UTC+07), 0.21 giờ** (mốc kiểm hoàn tất); MASK-P2 không có giờ ước tính riêng, **54–80 giờ** dành cho triển khai tương lai. Không lấy 1 giờ MASK-P cũ làm dự toán P2.

## Cần Core — bổ sung MASK-P2, 15/11/2026

| Mã | Cửa chung cần có | Khi chưa có |
|---|---|---|
| C-MB-01 (kế thừa C-M2C-01/02/03) | Giữ bytes gốc/bản che và map/patch/kế hoạch bất biến trong kho tệp ACL tới khi đóng, quyền tham chiếu con xuyên bước/module/người/tài liệu; điều phối và chứng thực đủ Local trên mọi vùng, ghim dạng trả/năng lực cuối/băm tệp cuối | Adapter CoreGia ngoài gói; thiếu snapshot/quyền/nguồn/đoạn thì từ chối, không phát hành tệp chỉ qua quy tắc |
| C-MB-02 (kế thừa C-M2C-05) | Ngan thật CAS/ghi lô nguyên tử/chốt alias+kết quả/mất ACK; cách ly upload trước phát hành, dọn tệp mồ côi khi chốt lỗi, giữ gốc có quyền cho khứ hồi đúng byte | RAM theo mẫu, ChuaRo khi đã nhận chưa xác nhận; không tự tạo cache máy/đường tải bỏ quyền hoặc coi giao dịch RAM là Core thật |
| C-MB-03 (kế thừa MASK-7 §7) | Trần streaming/download/upload đếm bytes thực trước cấp phát, ánh xạ 413, budget RAM/thời gian/job/concurrency và hủy trên máy đích | Engine áp trần thử nghiệm sau cổng SDK hiện có, chưa chứng minh giới hạn tải trước engine; B10 đo biên/đề nghị lead/Core trước vận hành |

Không yêu cầu route/SQL/màn riêng Mask, không sửa Core/SDK trong P2. Không có câu mới chờ Anh quyết phương án; chờ Anh chạy Office/Local sau khi B10 được triển khai.

## MASK-2c-1 — bàn giao map và snapshot, 15/11/2026

- **Đạt phạm vi nội bộ; đã kiểm bằng Core giả (CoreGia).** PR: **chờ lead mở**; không commit/push. [Báo cáo theo AGENTS.md §6](BAO-CAO-MASK-2c-1.md), [kết quả lệnh thật, gồm các lượt hiệu năng lỗi và lượt cuối](KET-QUA-KIEM-MASK-2c-1.txt).
- Đúng bốn tệp mã: `anh_xa_ai.py`, `ho_so_ai.py`, `che_van_ban.py`, `nguon/privacy/types.py`. Map từ khoảng thay thực tế, ba hệ gốc/NFC-Cf/che; quan hệ NFD nhiều-một, điểm neo Cf bị bỏ, alias dài/ngắn/lặp và kiểm bao trọn tên. Snapshot đóng băng cả chuỗi/map/kế hoạch, băm chuỗi/bytes và phiên bản; không ghi đĩa engine, Ngan chỉ chỉ mục.
- Cửa `che_co_anh_xa` chỉ nội bộ, lớp 1 chặn hoặc thiếu tài nguyên vẫn chặn; không đổi manifest/API/kết quả công khai. Plan chỉ lưu/kiểm kế hoạch Core cấp; tạo yêu cầu/thuật toán chia đoạn/Local AI thuộc các lát sau. Port kho tệp tin cậy và adapter DEMO ngoài gói; kiểm quyền/mã/tham chiếu/băm tại lưu/đọc/retry, giữ ChuaRo/hủy/CAS.
- **125 test mới**, toàn bộ **866 passed, 4 xfailed, 190 subtests passed, 0 skipped, 78,34 giây, mã 0**. Bốn xfail strict held-out lớp 1 giữ nguyên. NFD/Cf thay dấu cách/selector/tab/NBSP, span chồng/prefix, tiền/ngày, biên 500000/500001, snapshot/map/băm hỏng, quyền/tệp/chỉ mục thiếu và không ghi đĩa đều có kiểm.
- CLI SDK chuẩn **0/2 ĐẠT, mã 1**: cả hai lỗi “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Adapter **2/2 ĐẠT, mã 0**; kiểm độc lập **ĐẠT, mã 0**; `git diff --check` mã 0. Chưa kiểm Linux thực tế/Core thật/model thật; 0 Cloud/engine khác.
- Trong quá trình có lượt lỗi hiệu năng; đã bỏ quét Cf cho ASCII và định vị trực tiếp nghi vấn số dài trùng toàn văn, vẫn chặn với cùng offset. Test cũ/ngưỡng 5 giây/timeout 12 giây giữ nguyên; có đối chiếu KnownText. Trần snapshot mới 64 MiB là giới hạn kỹ thuật nội bộ, không là trần upload Core đã nghiệm thu.
- Thời gian thực tế: **12:12:00–12:59:54 ngày 15/11/2026 (UTC+07), 0.80 giờ**; phiếu **6 giờ ƯỚC TÍNH**. Cần Core: cụ thể hóa C-M2C-01/02/05 ở trên; không có câu chờ Anh mới, không sửa mẫu chung/Core/SDK/schema/nguồn cũ hoặc thêm dependency.

## MASK-2c-2 — bàn giao chuẩn bị Local, 15/11/2026

- **Đạt phạm vi nội bộ; đã kiểm bằng Core giả (CoreGia).** PR: **chờ lead mở**; không commit/push. [Báo cáo theo AGENTS.md §6](BAO-CAO-MASK-2c-2.md), [kết quả lệnh thật, gồm lượt lỗi fixture và lượt cuối](KET-QUA-KIEM-MASK-2c-2.txt).
- Đúng năm tệp mã được giao; bản 1.1.0 thêm `mask.chuan_bi_ai_cuc_bo@1`, giữ `tra` hai năng lực cũ. Chạy đủ lớp MASK-2b, giữ snapshot quy tắc đạt tại Core, không trả bản che trung gian. Mã yêu cầu do quyền Core cấp, không nhận tự khai từ payload.
- Kế hoạch phủ đủ gốc ≤500.000, đoạn ≤8.000 code point gồm overlap tối đa 512 mỗi phía, làm tròn vào biên an toàn và đủ 300 khi có nguồn; ≤128 đoạn. Không cắt từ/NFD/Cf/đuôi; span gốc nhận diện >300 thì từ chối. Prompt có mã/phiên bản do module/quy trình cấp, khuôn đủ các trường ở §6.3, profile/khuôn/prompt/đoạn có băm chuẩn; gốc Unicode nguyên vẹn chỉ Local, chuyển tiếp không gốc/map/tên.
- Snapshot chuẩn bị bao hồ sơ MASK-2c-1, kết quả quy tắc và prompt/khuôn/profile/biên nhận; Core giữ tệp có ACL, Ngan chỉ giữ băm/tham chiếu. Ghim input/config/model/budget/deadline từ đầu, retry/mất ACK/ChuaRo/CAS không cấp lại alias hoặc tăng đếm. Cổng Core/tokenizer/deadline thiếu hoặc snapshot/quyền mất thì chặn; chưa có API chuỗi thật.
- **972 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 89.92 giây; mã 0**, gồm 106 test mới. DEMO có quyền **2/2 ĐẠT, mã 0**; kiểm độc lập và `git diff --check` mã 0. CLI SDK chuẩn **0/2, mã 1**, thiếu nguồn quyền đúng giới hạn cũ. Lượt toàn bộ đầu có 3 lỗi fixture MASK-3 nạp manifest mới nhưng chỉ cài hai handler; đã sửa adapter dùng phiếu con tương ứng, giữ nguyên ca/kiểm chống trùng. Không kiểm Core/model thật hoặc Linux thực tế; số token trong adapter là fixture, không công bố chạy dài/0 lọt thật. 0 Cloud/engine-to-engine; nợ CAO và bốn xfail held-out giữ nguyên.
- Thời gian thực tế: **13:02:00–13:31:40 ngày 15/11/2026 (UTC+07), 0.49 giờ**; phiếu **6 giờ ƯỚC TÍNH**, độ khó **kho**. Cần Core: C-M2C-01/02/05 cụ thể ở trên; C-M2C-03/04 và AI-9/hậu kiểm/đo thật còn ở các lát sau. Không có câu chờ Anh mới; không sửa Core/SDK/nguồn cũ/schema chung/dependency.

## MASK-B1 — bàn giao cổng ZIP/XML, 15/11/2026

- **Đạt phạm vi nội bộ; chưa đạt CLI SDK chuẩn do thiếu nguồn quyền.** PR: **chờ lead mở**, không commit/push. [Báo cáo AGENTS.md §6](BAO-CAO-MASK-B1.md), [kết quả lệnh thật](KET-QUA-KIEM-MASK-B1.txt). Đã kiểm bằng Core giả (CoreGia) **gói văn bản hiện có**, cổng B1 kiểm trực tiếp RAM; chưa nhận tệp đã nối.
- Đúng ba tệp mã: `doc_tep.py`, `zip_an_toan.py`, `xml_an_toan.py`. Lần closure `zip.py` → `hoa_don_xml.py`; DOCX → `cau_truc.py` chỉ đối chiếu lỗi/namespace, không kéo reader/DTO. Chép chọn lọc, quyền/symbol/SHA bytes và LF trước–sau tại NGUON.md; không sửa nguồn mẫu/Core/SDK/ngăn chung/manifest hoặc các handler đang thuộc MASK-2c-3.
- ZIP tiền kiểm EOCD trước cấp phát central directory; chặn ZIP64/multidisk/prefix tự chạy/đuôi/gap/overlap/local-central sai, tên trùng NFC/casefold/path/percent alias, symlink/encrypted/method/header lạ. Extra/comment ZIP ngoài whitelist rỗng đều từ chối. Giải nén `zlib` có trần đến EOF thật/CRC/bytes, kể cả khai nhỏ giấu đuôi; không dùng ZipExtFile hoặc hook cảnh báo toàn cục.
- XML Expat stdlib không regex thay parser, chặn DTD/entity/XXE/PI/comment/encoding/namespace lạ kể cả chưa dùng; khai báo XML hợp lệ qua sự kiện riêng. Kiểm content types/root/graph và part mồ côi, quan hệ ngoài/URI/path, nhúng/macro/vùng lạ theo §7.2. Whitelist node/attribute là cửa đầu vào; B2/B3 còn phải đọc/map/kiểm ngữ nghĩa trước hai lớp.
- Đúng/vượt mọi trần thử nghiệm được kiểm tại cửa tương ứng. Đếm bảo thủ text/tail/attribute và shared string từng ô dùng, không preview. UTF-8 ra 8 MiB có test bộ đếm riêng vì 2 triệu code point tối đa chỉ 8.000.000 byte. Chưa có writer/upload; helper kiểm chiều ra/JSON dành cho B4/B7/B9, không nhận đã kiểm trần tải Core trước engine.
- **1248 passed, 4 xfailed, 190 subtests passed, 0 skipped, 99,42 giây, mã 0**; 276 test B1 mới (gồm 300 lượt biến đổi byte). Từng lỗi kiểm không output một phần/mạng/ghi đĩa/log; hủy/ChuaRo truyền nguyên, buffer dọn finally. CLI chuẩn **0/2, mã 1**; adapter DEMO **2/2, mã 0**; kiểm độc lập **ĐẠT, mã 0**. Bốn xfail strict held-out lớp quy tắc giữ nguyên, chưa đo Local/Cloud.
- Chỉ DEMO, Cloud tắt; không thêm dependency/PDF/Office COM. Không lưu máy engine hoặc tạo trạng thái/bảng ngăn mới, mọi dữ liệu việc chỉ RAM; giữ mẫu Ngan hiện có cho các lát giữ dữ liệu sau. Chưa chạy Linux/Core/Word/Excel/Local thật, chưa đo peak RAM/thời gian từng giai đoạn ở biên. B10 còn phải đo cả chuỗi, không lấy thời gian pytest thay benchmark.
- Thời gian thực tế: **13:50:00–14:37:27 ngày 15/11/2026 (UTC+07), 0.79 giờ** (bắt đầu theo handoff, kết thúc tại mốc chốt kết quả). Phiếu **6–8 giờ ƯỚC TÍNH**, độ khó `kho`. `git diff --check` mã 0; UTF-8/AST/whitespace 5/5 tệp mã/test mới; SHA bytes/LF 3/3 đích và nguồn mẫu không đổi. Không phát sinh câu chờ Anh mới.

## Cần Core — cụ thể hóa MASK-B1, 15/11/2026

- **C-MB-03 / stream và tải:** API/SDK phải cấp stream có hủy/lease và đếm bytes thực, chặn download/upload **1 MiB mỗi chiều trước cấp phát/tải trọn RAM**, không chỉ tin Content-Length/metadata. `mo_tep` SDK 2.0 đang tải cả tệp rồi mới giao cho engine, nên kiểm B1 sau nhận bytes không bảo vệ đoạn tải trước đó. B4/B9 phải kiểm bytes ra riêng trước upload; Core cũng phải áp trần tại cửa chung.
- **C-MB-03 / 413:** ánh xạ lỗi giới hạn tải 413 thành lỗi giới hạn chuẩn và câu Việt an toàn, không nhầm lỗi liên lạc; không nuốt hủy/mất lease hoặc đổi thành kết quả rỗng. Ghi rõ trần và chiều bị từ chối bằng mã/số đếm, không tên/path/nội dung. Không nới SDK hoặc handler để làm xanh CLI thiếu quyền trong B1.
- **C-MB-03 / budget:** lead/Core chốt RAM/CPU/thời gian/job/concurrency trên máy đích, deadline xuyên download → ZIP/XML → reader → Local → writer → upload, giới hạn hàng chờ và thu hồi việc/hủy. 60s văn bản/300s tệp chỉ dự toán kỹ thuật, không hard cap production đã chứng minh. B10 đo đúng/vượt biên với entropy/node/ô/alias dài và peak Python/OS từng giai đoạn rồi trình điều chỉnh nếu cần.
- **C-MB-01/02 kế thừa:** ACL/quyền tệp con/snapshot gốc và bản che, Ngan CAS/lô nguyên tử/đối soát ACK, chứng thực đủ hai lớp do Core điều phối vẫn chờ. B1 không tự triển khai cache/kho bền/cửa ngoài cổng chung và không coi phép thử RAM là Core thật.

## MASK-B2 — bàn giao reader Word nội bộ, 15/11/2026

- **Đạt phạm vi reader nội bộ; chưa đạt CLI SDK chuẩn do thiếu quyền.** PR: **chờ lead mở**; không commit/push. [Báo cáo theo AGENTS.md §6](BAO-CAO-MASK-B2.md), [lệnh và kết quả thật](KET-QUA-KIEM-MASK-B2.txt). Đã kiểm bằng Core giả (CoreGia) **gói văn bản hiện có**; reader tệp kiểm trực tiếp RAM, chưa nối năng lực hoặc chạy hai lớp trên tệp.
- Đúng ba runtime: `doc_word.py`, `xml_word.py`, khối MASK-B2 riêng trong `doc_tep.py`. Chép chọn lọc story/notes từ DC, run/merge từ TX; không import chéo hoặc kéo closure `.cau_truc`, không Accept All/make_docx/bỏ vùng/cảnh báo thay quét. Nguồn/quyền/symbol/SHA bytes+LF trước–sau trong NGUON, manifest băm trước ở `SHA-NGUON-MASK-B2-TRUOC.json`; nguồn mẫu và hai tệp ZIP/XML B1 không đổi.
- Đọc mọi story trong profile, chữ ẩn và core/app/custom có kiểu; style/latent style/lvlText/theme/property name và mọi scalar custom đều có map/tổng quét, kể cả số/bool/ngày có thể mang mã định danh. ID style/font chỉ hằng an toàn, các giá trị cấu trúc kiểm theo profile; chưa phân loại thì từ chối. Giữ nguyên NFD/Cf, map Unicode code point từng vùng về node/run/attribute và byte part XML gốc, phân biệt SHA tệp/text và offset ZIP/DEFLATE. Không nối qua đoạn/ô/story, không bỏ chữ ở ô nối hoặc note chưa có tham chiếu; giữ tham chiếu lặp đủ vị trí.
- Cổng B2 mở `0x0006` DEFLATE/descriptor 12 hoặc 16 byte có đối chiếu local-central/CRC/size, B1 kiểm lại payload và trần. Container/local record/payload nén/offset gốc giữ nguyên, `le_cuoi` bao descriptor. Theme Word và app chuẩn được kiểm; fixture DEMO đủ các part chuẩn và style matrix có ba phần tử mỗi danh sách. Chỉ mô phỏng cấu trúc Office, chưa kiểm Word thật. Excel tối thiểu kiểm được cờ ZIP chung; theme/calcChain/reader Excel thuộc B3.
- Trần thử nghiệm §7.3 giữ nguyên, bổ sung đếm 20.000 ô Word vật lý kể cả trống/ô nối. Tổng logic mọi vùng/metadata/style/theme/ký hiệu đếm khi đọc ≤500.000; B1 vẫn đếm bảo thủ cả text/tail/attribute kỹ thuật. Gold từng vùng/vị trí, tên qua ba run khác style có NFD/Cf/entity, merge/notes lặp/ẩn, UTF-8/BOM/UTF-16/ngoài BMP/CDATA/CR, các giá trị/graph/namespace/unsupported sai và không output dở/I/O/mạng/hủy đều có kiểm. Dữ liệu việc chỉ RAM, dọn finally; chưa thêm trạng thái/bảng Ngan.
- **1540 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 142,45 giây, mã 0**. B1+B2 **431 passed, 12,39 giây**, gồm 155 test B2 mới. Trần logic reader 500.000/+1 được thử độc lập với trần B1 bằng text cộng tab. Kiểm độc lập ĐẠT, DEMO có quyền **2/2**, CLI chuẩn **0/2, mã 1** thiếu xác minh phiên/quyền; không nới chặn. AST/UTF-8/whitespace/SHA bytes+LF ba runtime đạt, không bytecode trong gói, `git diff --check` mã 0. Chưa Linux/Core/Office/Local thật, chưa benchmark biên từng giai đoạn; Cloud tắt, nợ held-out lớp quy tắc giữ nguyên.
- Thời gian thực tế **14:47:00–15:44:23 ngày 15/11/2026 (UTC+07), 0,72 giờ** tại mốc chốt kiểm; phiếu **6–8 giờ ƯỚC TÍNH**, `kho`. Giới hạn tên 256 và flags/descriptor đặt trong wrapper `doc_tep` để giữ ba runtime; hàm ZIP độc lập B1 không đổi, các reader phải qua cổng chung. Không sửa Core/SDK/mẫu ngăn/manifest/handler, không dependency/COM/PDF và không có câu chờ Anh mới.

## Cần Core — cụ thể hóa MASK-B2, 15/11/2026

- **C-MB-01 / biên vùng:** kế hoạch Local và snapshot phải giữ mã/chỉ số vùng, story/đoạn/ô/note và map Unicode→node/run/attribute/byte; phủ đủ text metadata/style/theme cùng text thân. Không nối các ô/story để suy tên, không chỉ gửi preview hoặc chỉ thân cho Local. SHA text từng vùng khác SHA bytes tệp; map byte thuộc XML giải nén nguyên gốc, lưu cùng container gốc và băm trong kho Core có ACL tới khi đóng yêu cầu. B2 chỉ trả đối tượng RAM, chưa tự công bố hợp đồng snapshot mới.
- **C-MB-02/03 kế thừa:** Ngan thật/CAS/lô/chốt kết quả/mất ACK, cách ly upload, quyền tệp con, chứng thực đủ AI-9 Local, stream/trần trước cấp phát/413 và budget RAM/thời gian/job/concurrency vẫn chờ như B1/P2. B10 đo cả chuỗi trên máy đích; phép thử reader và CoreGia không chứng minh Office mở/lưu không repair hoặc chất lượng hai lớp đạt. Không thêm route/SQL riêng hoặc lưu đệm máy engine để bù.
## MASK-B3 — reader Excel, 15/11/2026

- **Đạt phạm vi nội bộ; CLI SDK chuẩn chưa đạt do thiếu nguồn quyền.** PR: **chờ lead mở**; không commit/push. Thực tế **14:47:00–15:36:14 ngày 15/11/2026 (UTC+07), 0,82 giờ** theo mốc chốt kiểm, phiếu **6–8 giờ ƯỚC TÍNH**, độ khó `kho`. Bàn giao và kết quả thật tại [BAO-CAO-MASK-B3.md](BAO-CAO-MASK-B3.md), [KET-QUA-KIEM-MASK-B3.txt](KET-QUA-KIEM-MASK-B3.txt).
- Đúng ba tệp mã được giao: `doc_excel.py`, `xml_excel.py`, một khối Excel riêng nối cuối `doc_tep.py`. AST 37 định nghĩa/câu lệnh B1 cũ giữ nguyên; không sửa mã Word/nguồn mẫu/Core/SDK/manifest/handler/Ngan chung, không thêm dependency/COM/PDF hoặc import engine khác. Chép chọn lọc `chu_xml` của Hóa đơn; quyền/symbol/SHA bytes và LF trước–sau ở NGUON.md, nguồn Excel cũ chỉ đối chiếu.
- Reader quét đủ mọi ô/shared/inline/rich text, hàng/cột ẩn, shared chưa dùng, tên sheet và properties thuộc profile. Map Unicode ↔ node/run/attribute/byte thực, đủ UTF-8/UTF-16/entity/ST/CR/NFD/Cf; không nối hai ô hoặc preview/cắt 32767. Shared gốc có danh sách mọi nơi dùng; dữ liệu nhạy cảm chỉ nội bộ, `repr` không chứa tên.
- Raw value/type/style/XML ô số/boolean/serial ngày giữ nguyên; kiểm thêm style hiệu lực kế thừa hàng/cột, epoch, indices, numFmt allowlist, font, merge/ref. Tên sheet và TitlesOfParts liên quan là vùng không được sửa; B6/B7 phải cho cả hai lớp kiểm, đề nghị đổi thì từ chối. Mọi phần/attribute chưa phân loại, sheet hidden/veryHidden, formula/cache/definedNames, comment/persons/chart/drawing/media/nhúng/macro/externalLink/connection hoặc part mồ côi bị chặn cả gói bằng lỗi Việt cố định.
- Tương thích ZIP Office theo handoff: cờ nén 0x0006 và descriptor 12/16 bytes, CRC/size/local/central/interval/EOF thực đều kiểm; giữ offset record/payload riêng cho B4. Theme chỉ grammar và giá trị đã kiểm, `calcChain` **chỉ rỗng** để không trái yêu cầu chặn mọi formula/cache. Fixture DEMO mô phỏng Excel lưu đủ shared/styles/theme/core/app/custom/calcChain rỗng, không phải chứng cứ đã mở bằng Excel thật.
- 299 test B3 DEMO: gold từng vùng, shared lặp/unused/rich/NFD/Cf/ST/entity/CR, metadata tên và attribute, tất cả blocker và quan hệ đánh tráo/mồ côi, cells đúng/vượt 20.000, sheet 50/51, node thật 100.000/100.001; tiền 1000000 VND/ngày 2026-10-30 theo giá trị+style. CDATA trong part cần map bị chặn vì chưa có profile patch chứng minh. Hủy/ChuaRo truyền nguyên, không output dở/I/O/log hoặc trạng thái bền; Ngan RAM theo mẫu không đổi. Toàn bộ trần B1 tiếp tục áp; B10 còn phải đo RAM/thời gian trên máy đích.
- Chưa gắn reader vào SDK, chưa chạy MASK-2b/Local trên tệp, chưa writer/che/mở che hoặc phát hành kết quả tệp. Gói văn bản **đã kiểm bằng Core giả (CoreGia)**, reader B3 kiểm trực tiếp RAM; chưa Core/Excel/Local thật hoặc Linux thực tế. Cloud tắt, không lời gọi engine/model/mạng ngoài.
- Kết quả cuối: **1684 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 156,15 giây, mã 0**. Lượt mục tiêu B3 + một test nguồn cũ **300 passed, 5,54 giây**. CLI SDK chuẩn **0/2, mã 1**, cả hai thiếu quyền; adapter DEMO **2/2, mã 0**; kiểm độc lập và `git diff --check` **mã 0**. SHA đích 3/3, UTF-8/AST/whitespace 5/5, AST B1 37/37. Hai lượt kiểm toàn bộ trung gian lỗi tài liệu nguồn đã được sửa bằng cập nhật SHA/cách ghi bảng B3; không sửa hoặc bỏ test cũ để làm xanh.

## Cần Core — kế thừa MASK-B3, 15/11/2026

- Giữ **C-MB-01/02**: kho tệp ACL giữ bytes gốc/bản che/map mọi vùng, quyền xuyên bước, đủ Local được Core chứng thực, CAS/chốt/kết quả/ACK nguyên tử và cách ly upload chưa phát hành. Reader không thêm kho máy hoặc dùng cờ caller để tự nhận đã qua hai lớp. Thiếu cửa vẫn từ chối khi B7/B9 nối.
- Giữ **C-MB-03**: trần download/upload 1 MiB đếm byte thực trước cấp phát, streaming có hủy/lease, ánh xạ 413 và budget RAM/CPU/thời gian/concurrency; kiểm RAM sau SDK không chứng minh đoạn tải trước engine an toàn. Không sửa Core/SDK hoặc nâng trần thử nghiệm trong B3.
- Bàn giao nội bộ cho **B4/B6/B7**: writer phải chép nguyên descriptor tới `le_cuoi_ban_ghi`, phân biệt payload tới `le_cuoi`; patch shared một lần nhưng hậu kiểm mọi nơi dùng/unused, không bỏ tên sheet/metadata khỏi Local. Mọi vùng `duoc_sua=False` cần đổi phải chặn, không rename mù. Chưa có câu chờ Anh mới; Excel/Local thật theo B10 do Anh chạy sau.

## MASK-B2 — giải xung đột gộp MASK-B3, 15/11/2026

- Đã hợp nhất đầy đủ hai khối Word/Excel trong `doc_tep.py` và cả hai phía NGUON/CHANGELOG/VIEC; PR: **chờ lead mở**. Không commit/push hoặc `merge --continue`.
- Giữ cổng ZIP chung B2 cho cả DOCX/XLSX và cổng Excel B3, dùng chung kiểm tên tối đa 256. Giữ hai quy ước offset: Word/chung `le_cuoi` bao descriptor; Excel `le_cuoi` hết payload, `le_cuoi_ban_ghi` bao descriptor.
- Thêm 18 ca hồi quy XLSX DEMO trong RAM qua cả cổng chung/reader Excel: DEFLATE cờ 0x0006 + descriptor có/không chữ ký, CRC/size nén/size gốc sai phải chặn, tên 256/257. Không sửa hoặc bỏ test B1/B2/B3.
- Kết quả thật: `.venv/Scripts/python -B -m pytest e_mask/tests -q --basetemp=.pytest-tmp` → **1907 passed, 4 xfailed cũ, 190 subtests passed, 0 skipped**, 196.80 giây, mã 0; `kiem_doc_lap.py` → ĐẠT/mã 0; `chay_demo.py` → **2/2 ĐẠT**, mã 0. CLI `-m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` → **0/2**, mã 1: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Giữ từ chối đúng, không nới quyền để làm xanh CLI. SDK 2.0.0/wheel đã đối chiếu SHA256SUMS.
- Đã kiểm bằng Core giả (CoreGia); reader chỉ RAM, chưa Office/Core/Local thật hoặc Linux thực tế; Cloud tắt. Đối chiếu xác nhận không mất dòng tài liệu cả hai nhánh; bốn reader/profile và test B1/B2/B3 giữ nguyên nội dung LF. `git diff --check` đạt.
- Git: đã xóa toàn bộ dấu xung đột trong bốn tệp. `git add` bị sandbox từ chối tạo `index.lock` vì Git index nằm ngoài worktree; bốn tệp vẫn `UU`, **lead cần stage** cùng test mới. Giữ `MERGE_HEAD`, không commit/`merge --continue`/push.
- Thời gian phiên gộp: **15:46:00–15:54:33 ngày 15/11/2026 (UTC+07), 0.14 giờ**; MASK-B2 trong phiếu **6–8 giờ ước tính**, không có dự toán riêng cho việc gộp.
- **Cần Core / Chờ Anh mới phát sinh:** không; giữ nguyên các mục Cần Core của B2/B3 và giới hạn CLI thiếu nguồn quyền.
