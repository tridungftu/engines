# VIỆC — danh sách việc duy nhất của project `e_mask`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc yêu cầu chung/SDK 2.0, yêu cầu Mask và lập kế hoạch lát có giờ ước tính; trình Anh qua lead | MASK-P | Xong — 14/11/2026 (lập phiếu) | [GIAO-CODEX-e_mask.md](GIAO-CODEX-e_mask.md): 14 lát MASK-0…13, 52–62 giờ ước tính chưa đo; phần tệp có điều kiện, chưa triển khai; PR: **chờ lead mở** |
| 1 | Chuyển kho bí danh sang **ngăn của engine** theo cổng chung (thay `mask.py`/`kho_mask.py`/SQL 113, 117–120 trong Core) | MK-10, 19 | Chờ Core | Bàn cùng lead Core qua Anh |
| 2 | J8b: đối soát mất xác nhận | — | Chờ làm |  |
| 3 | Lát 4: màn duyệt danh sách chờ (Admin) — giao diện của engine | MK-15, 16 | Chờ làm |  |
| 4 | Lát 5: màn thử che/mở che DEMO | — | Bỏ — 15/11/2026 | Anh chốt bỏ `PHIEU-MASK-CHAY-THU-DEMO.md` (QUYET-DINH-ANH-20261115 câu 10); thử DEMO dùng màn Chạy thử chung của Core |
| 5 | Lát 8: che/mở che Word/Excel (mẫu 5–8) | §1.3 | Chờ làm |  |
| 6 | Lát 6: 8 contract (Anh duyệt tên) → lát 7: bài 11 bước | — | Chờ làm |  |
| MASK-P | Lập phiếu giao Codex theo SDK 2.0; chỉ tài liệu, không tạo gói/không sửa nguồn | MK-1…6, 10…22 | Xong — 14/11/2026 | [Phiếu giao](GIAO-CODEX-e_mask.md): 14 lát, 52–62 giờ ước tính có điều kiện. Regex 14/14 khối đạt; 5 mục/bảng lát/tổng giờ khớp; UTF-8/NFC và kiểm khoảng trắng đạt, `git diff --check` mã 0. Ba lệnh kiểm gói AGENTS.md §5 không áp dụng theo ngoại lệ lát chỉ tài liệu; không chạy hoặc nhận là đã kiểm bằng CoreGia. Đề xuất `van_ban_da_che` ở cuối sổ chung mang nhãn **ĐỀ XUẤT MASK-P, chờ Anh**. Không commit/push; PR: **chờ lead mở** |
| MASK-3 | Port kho/quyền, kho tạm và chống trùng sau MASK-2 | MK-10…13, 16…19 | Xong phạm vi port/CoreGia — 14/11/2026 | Chỉ DEMO; đúng bốn tệp mã. Pytest 225 passed, 190 subtests passed; kiểm độc lập ĐẠT. CLI SDK 0/2 ĐẠT do handler MASK-5 còn stub; chưa đạt nghiệm thu chung. PR: **chờ lead mở** |
| MASK-3b | Kho MASK-3 qua Ngan, tiền tố MASK, bản khai SDK 2.1 | Quyết định 15/11 câu 2, 8; kiểm độc lập của lead | Xong phần sửa an toàn — 15/11/2026; đã nối ngăn chung NGAN-0; chờ Core thật | Bỏ Cf/selector và che theo vị trí gốc; bí danh tạm riêng từng yêu cầu; bọc lỗi/log; hiện vật lưu trên máy đã ra LUU-TRU. PR: **chờ lead mở** |
| MASK-4 | Phong bì và schema ba loại riêng | MK-20 | Xong phạm vi CoreGia — 15/11/2026 | Schema chung/bản gói so SHA; kiểm UTF-8/JSON/trần lồng. PR: **chờ lead mở** |
| MASK-5 | Hai handler văn bản SDK và mở che dữ liệu/trích dẫn AI | MK-12…14, 18, 20, 21 | Xong phạm vi CoreGia — 15/11/2026; chờ quyền thật | DEMO qua port ngoài gói; CLI chuẩn vẫn bị chặn do thiếu quyền. PR: **chờ lead mở** |
| MASK-6 | Duyệt/từ chối, đóng/dọn, chuyển DEMO và màn Admin | MK-11, 15…19, 22 | Xong phạm vi CoreGia/KttCore giả — 15/11/2026 | Màn trong gói; chưa nạp trong Core thật. PR: **chờ lead mở** |
| MASK-7 | Khảo sát từng vùng tệp, đo DEMO và trình phương án/trần | MK-1, 4, 21; quyết định 15/11 câu 11 | Xong khảo sát — 15/11/2026; Chờ Anh/lead chốt phần tệp | [Bảng bằng chứng và phương án](MASK-7-KHAO-SAT-TEP.md), [số đo thật](SO-DO-MASK-7.json). Không thêm thuật toán/năng lực tệp; MASK-8…11 chưa code. PR: **chờ lead mở** |
| MASK-2b | Đóng nợ CAO tên người viết thường không nhãn | MK-2, 18, 20; lệnh giao 15/11 | Xong phạm vi CoreGia — 15/11/2026 | Bộ dò không phụ thuộc chữ hoa/dấu; tên có danh xưng/đã duyệt được che, nghi vấn vào con_sot để chặn phát hành. [Báo cáo](BAO-CAO-MASK-2b.md), [số đo](SO-DO-MASK-2b.json); PR: **chờ lead mở** |

Các số “lát 1…8/J8b” ở các dòng lịch sử là mã kế hoạch cũ; kế hoạch giao SDK 2.0 dùng `MASK-0…MASK-13` trong phiếu mới. Hoàn tất MASK-P không có nghĩa đã code, kiểm bằng CoreGia hoặc nối Core thật. MASK-P ước tính 1 giờ; tổng giờ 52–62 là dự toán triển khai sau, cập nhật lại sau khảo sát tệp MASK-7.

## MASK-2b — bàn giao, 15/11/2026

- **Đạt phạm vi MASK-2b**, đóng nợ CAO trong phạm vi họ/tên được mô tả; đã kiểm bằng Core giả (CoreGia). Hai tệp runtime, không sửa ngăn/cấu hình chung hoặc từ điển. PR: **chờ lead mở**; không commit/push. [Báo cáo](BAO-CAO-MASK-2b.md), [lệnh kiểm thật](KET-QUA-KIEM-MASK-2b.txt).
- Pytest: **545 passed, 190 subtests passed, 0 skipped, 29,81 giây, mã 0**; 107 test riêng MASK-2b. Adapter DEMO **2/2 ĐẠT, mã 0**; kiểm độc lập **ĐẠT, mã 0**. CLI SDK chuẩn **0/2 ĐẠT, mã 1** do thiếu nguồn quyền, không thành công giả. Core thật/Linux/Cloud chưa kiểm.
- Đo báo nhầm trước/sau: 14 mẫu cũ **1/14 (7,14%)**, 30 câu bổ sung **2/30 (6,67%)**, không tăng trên hai tập. 29 câu không tên không bị chặn được kiểm riêng. Bốn ví dụ giao việc: **4/4 lọt trước → 0/4 lọt sau**, hai che/hai chặn; không suy ra recall chung.
- Thời gian **09:19–09:42:22 ngày 15/11/2026 (UTC+07), khoảng 0.39 giờ**. Không có dự toán riêng MASK-2b; MASK-2 gốc 3 giờ ước tính. Cần Core/Chờ Anh mới: **không**; các phụ thuộc ngăn/quyền/nguồn sinh trước Cloud giữ nguyên.

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
