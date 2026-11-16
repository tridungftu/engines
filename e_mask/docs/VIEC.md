# VIỆC — danh sách việc duy nhất của project `e_mask`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| MASK-B6c | Hiệu năng che Excel nhiều hàng, gom quyền và cache RAM trong lượt | Phiếu lead 16/11/2026; sau B6/B6b | Xong mã/kiểm — 16/11/2026; mốc 3 giây chưa đạt ổn định | 2.000 hàng: 2,5479–5,6756 giây, median ba lượt cuối 5,6482; gần 1 MiB: 4,8568–11,8848 giây. 61 test mới; báo cáo §6 cuối sổ. PR: **chờ lead mở**. |
| MASK-B6b | Chặn ô số định danh giả tiền/ngày, xét format và giá trị thực | Phiếu lead 16/11/2026; sau B6 | Chờ Anh — 16/11/2026; xong mã, chưa đạt full xanh | 216 regression mới đạt; full 3318 passed, 1 failed ở test B6 cũ trái yêu cầu mới, 4 xfailed cũ, 190 subtests. Độc lập/diff mã 0, kiểm kê 55/55; CLI 0/2 thiếu quyền cũ. Đã đề nghị sửa đúng một test ngoài closure, chờ trả lời. PR: **chờ lead mở**. |
| MASK-B6 | Che Excel giữ format, shared/rich/inline/metadata, map chỉ RAM | Sau B3/B4 và R3…R6; MASK-P4; C-P4-01…05 | Xong mã/kiểm nội bộ / Chờ Core — 16/11/2026; chưa đạt nghiệm thu chung | Một runtime mới; B6 122/122. Full 2923 passed, 4 xfailed cũ, 190 subtests, 0 lỗi/skip; độc lập/diff mã 0, CLI 0/2 thiếu quyền. Nguồn 19/19, kiểm kê 55/55; PR: **chờ lead mở**. |

| MASK-B5b | Chặn số tài khoản/giấy tờ bị coi là ngày | Phiếu lead 16/11/2026; sau B5 | Chờ Anh — 16/11/2026; đã sửa mã, chưa đạt full xanh | Hai runtime Word/văn bản; 180 ca mới. Full: 2980 passed, 1 failed do assertion cũ buộc chặn nhầm ngày thật, 4 xfailed cũ. Cần duyệt sửa một assertion ngoài phạm vi; báo cáo §6 ở cuối sổ; PR: **chờ lead mở**. |
| MASK-B5 | Che Word trong whitelist, patch byte giữ format, map chỉ RAM đúng chuỗi | Sau B2/B4 và R3…R6; MASK-P4; C-P4-01…05 | Xong phần mã nội bộ / Chờ Core — 16/11/2026; chưa đạt nghiệm thu chung | Chỉ thêm `tep_word.py` trong bốn runtime được giao; B5 91/91 sau khóa ghi RAM với timer/hủy. CLI chuẩn 0/2 thiếu quyền; kiểm độc lập đạt. Kết quả full cuối, Cần Core và giờ thực tế tại mục B5 cuối sổ; PR: **chờ lead mở**. |
| MASK-R6 | Mở che văn bản/AI một lần từ map RAM bản cuối, nối R5/R4 và bàn giao đúng quyền | MASK-P4 §2/4/5; sau R3/R4/R5; C-P4-02/05 | Xong phần mã/kiểm R6 / Chờ Core — 16/11/2026; chưa đạt nghiệm thu chung | Đúng bốn runtime; R6 124/124, full 2646 passed, 1 failed kiểm kê ngoài closure, 4 xfailed cũ, 190 subtests, 0 skip. CLI 0/2 thiếu quyền; độc lập lỗi cùng kiểm kê; bản sao chỉ thay kiểm kê đạt; diff mã 0. Đã kiểm bằng Core giả (CoreGia); PR: **chờ lead mở**. Chi tiết/thời gian ở cuối sổ. |
| MASK-R7 | Admin chỉ metadata, xem tại Core và duyệt CAS cùng ID | MASK-P4 §3–5; sau R2; C-P4-06 | Xong phần adapter/UI giả / Chờ Core — 15/11/2026; chưa đạt nghiệm thu chung | Đúng hai runtime; không bản rõ/lọc tên, không ghi ngăn từ UI hoặc sao/xóa bí mật. Cửa biên nhận/quyền đang chờ Core; đã kiểm bằng Core giả (CoreGia), chưa UI Core thật. PR: **chờ lead mở**; kết quả thật/thời gian và C-P4-06 ở mục R7 cuối sổ. |
| MASK-R3 | Khảo sát ứng viên RAM, tìm chính xác qua kho R2, chặn mơ hồ alias | MASK-P4 §3–5; sau R2; câu 10 tối 15/11 | Chờ Core — kết thúc khảo sát 15/11/2026; **chưa đạt triển khai/nghiệm thu** | Đúng ba runtime; R3 25/25, full 2285 passed, 4 xfailed cũ, 190 subtests, 0 failed/skip; độc lập/diff mã 0, CLI 0/2 thiếu quyền. Ca gốc: 1 che đủ không chặn, 7 lọt bản khảo sát, 8 chặn trên 16. Báo nhầm câu thường: 4/18 = 22,22%. Không phát hành/Cloud. PR: **chờ lead mở**; số kiểm và C-P4-03 ở mục R3 bên dưới. |
| MASK-R4 | Kho ánh xạ chỉ RAM, ghim instance/quyền xuyên bước, TTL/timer/tiêu thụ một lần | MASK-P4 §2/4/5; C-P4-01/02; sau R1 | Xong phần kho/port CoreGia / Chờ Core — 15/11/2026; **chưa đạt nghiệm thu chung** | Đúng ba runtime theo phiếu; adapter chỉ ngoài gói, thiếu ghim/lifecycle thì runtime từ chối. [Báo cáo](BAO-CAO-MASK-R4.md). Chuyển nghiệp vụ cũ ở R2/R5/R6/B7 còn riêng; PR: **chờ lead mở**. |
| MASK-R2 | Adapter nhận diện SDK chỉ bí mật/metadata, không snapshot/map | MASK-P4 §2–5; sau R1; CĐ-36 | Xong phần adapter / Chờ Core — 15/11/2026; chưa đạt nghiệm thu chung | Đúng bốn runtime; R2 32/32, full 2260 passed, 4 xfailed cũ, 190 subtests passed, 0 failed/skip. Độc lập/diff mã 0; CLI chuẩn 0/2 thiếu quyền, C-P4-03 còn mở, tạo tên/tăng đếm bị chặn. PR: **chờ lead mở**; chi tiết ở mục MASK-R2 bên dưới. |
| MASK-R1 | Khai ngăn bí mật/alias, TTL SDK 2.2 và migration/kiểm kê | MASK-P4 §1–5; CĐ-36; câu 10 tối 15/11 | Xong sửa hồi quy / Chờ Core — 15/11/2026; **chưa đạt nghiệm thu chung** | Ngoại lệ lead cho sửa thêm chay.py/test: full pytest 2228 passed, 4 xfailed cũ, 190 subtests passed, 0 failed/skip; R1 46/46; độc lập mã 0, kiểm kê 50/50. CLI 0/2 thiếu quyền Core, C-P4-03 còn mở; kho RAM cũ giữ tới R2/R4. PR: **chờ lead mở**; kết quả thật ở mục MASK-R1 bên dưới. |
| MASK-P4 | Lập lại phiếu mở che cùng chu kỳ, map chỉ RAM và kho bí danh kín; chỉ tài liệu | Quyết định Anh tối 15/11 câu 10; CĐ-36 | Xong tài liệu — 15/11/2026; kiểm nền gói chưa đạt / Chờ Core | [Phiếu RAM](MASK-P4-MO-CHE-RAM.md): R1…R7 32–46 giờ ƯỚC TÍNH, B5…B10 sửa 36–56 giờ ƯỚC TÍNH, mỗi lát ≤5 tệp; TTL đề xuất 600 giây, cấu hình 60–900. Không code/commit/push; PR: **chờ lead mở**. P3 A không dùng; kết quả kiểm thật và C-P4-01…06 ở mục MASK-P4 bên dưới. |
| MASK-P3 | Thiết kế lại mở che/kho bí danh cho SDK 2.2.0, chỉ tài liệu | **CĐ-36 — Anh, 15/11/2026 16:28** | Xong tài liệu lịch sử — 15/11/2026; **A không dùng theo quyết định Anh 15/11 tối** | [Thiết kế P3 giữ truy vết](MASK-P3-MO-CHE-SDK-2.2.md): A/lát A/Q1…Q4 không còn giao/chờ chọn; MASK-P4 thay bằng B chỉ RAM, không hồ sơ Core, không giải mã bi_mat. Kết quả kiểm P3 giữ nguyên lịch sử. PR: **chờ lead mở**. |
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
| MASK-B4 | Writer ZIP giữ local record/payload nén, patch XML theo map và băm | Sau B1–B3; quyết định chiều câu 9 | Xong writer nội bộ — 15/11/2026; chưa đạt kiểm chung | Đúng ba runtime, B4 270 passed; toàn bộ cuối 2175 passed/2 failed deadline cũ MASK-2c-4/4 xfailed/190 subtests/0 skipped, CLI 0/2 thiếu quyền. [Báo cáo](BAO-CAO-MASK-B4.md), [lệnh/kết quả thật](KET-QUA-KIEM-MASK-B4.txt). Chỉ DEMO, Cloud tắt; PR: **chờ lead mở** |
| MASK-2b | Sửa theo kiểm độc lập: chấm điểm tên, giảm báo nhầm | MK-2, 18, 20; lệnh lead 15/11 lúc 09:47 | Xong phạm vi CoreGia — 15/11/2026 | t9: 0/32 lọt; t10: 2/41 báo nhầm (4,88%); 717 passed, 190 subtests. [Báo cáo](BAO-CAO-MASK-2b.md), [số đo](SO-DO-MASK-2b.json); PR: **chờ lead mở** |
| MASK-2c-P | Thiết kế lớp Local AI thứ hai và lệnh giao Codex, chỉ tài liệu | Quyết định Anh 15/11: "Thêm AI cục bộ" | Xong tài liệu — 15/11/2026 | [Phiếu Mask §6](GIAO-CODEX-e_mask.md#6-mask-2c--lớp-ai-cục-bộ), AI-9 ở phiếu Hỏi AI, đề xuất dữ liệu chung §6; 4 lát Mask + AI-9, tổng 31 giờ ƯỚC TÍNH triển khai. Chưa code/chưa đo model thật, Cloud tắt; PR: **chờ lead mở** |
| MASK-2c-1 | Map gốc/bản dò/bản che và snapshot bất biến qua port Core/Ngan | MASK-2b, MASK-3b…6; profile kỹ thuật lead duyệt 15/11 | Xong phạm vi CoreGia — 15/11/2026; chờ Core thật | Đúng bốn tệp mã; 866 passed, 4 xfailed giữ nguyên, 190 subtests; adapter DEMO 2/2, CLI chuẩn 0/2 thiếu quyền. [Báo cáo](BAO-CAO-MASK-2c-1.md); PR: **chờ lead mở** |
| MASK-2c-2 | Chuẩn bị yêu cầu Local, khuôn/profile/budget và kế hoạch đoạn | MASK-2c-1; profile kỹ thuật lead đã duyệt 15/11 | Xong phạm vi CoreGia — 15/11/2026; chờ Core/model thật | Đúng năm tệp mã, bản 1.1.0; 972 passed, 4 xfailed giữ nguyên, 190 subtests, 0 skipped; DEMO có quyền 2/2, CLI chuẩn 0/2 thiếu quyền. [Báo cáo](BAO-CAO-MASK-2c-2.md); PR: **chờ lead mở** |

Các số “lát 1…8/J8b” ở các dòng lịch sử là mã kế hoạch cũ; kế hoạch giao SDK 2.0 dùng `MASK-0…MASK-13` trong phiếu mới. Hoàn tất MASK-P không có nghĩa đã code, kiểm bằng CoreGia hoặc nối Core thật. MASK-P ước tính 1 giờ; tổng giờ 52–62 là dự toán triển khai sau, cập nhật lại sau khảo sát tệp MASK-7.

## MASK-R3 — kết thúc khảo sát ứng viên, 15/11/2026

**Kết luận: Chưa đạt triển khai/nghiệm thu — độ phủ giảm so với matcher danh mục DEMO, chi phí Core/Local thật chưa đo. Kết thúc khảo sát bằng giới hạn, giữ cửa phát hành đóng.** PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia); không commit/push.

**Đã làm:** ba runtime đúng bảng P4 §4: `che_van_ban.py`, `tra_cuu_dinh_danh.py`, `hau_kiem_ai.py`. Đầu dò mới tạo ứng viên có span từ detector/quy tắc/trường/danh sách của đầu vào hiện tại trong RAM; từng giá trị gọi `tim_ung_vien` của R2 qua `viec.ngan` SDK thật. Không liệt kê ngăn/dựng matcher danh mục trong nhánh mới, không fuzzy/prefix kho, không quét mọi chuỗi con hoặc giải mã. Kết quả ngăn chỉ metadata/null+cờ; tên mở che lấy đúng lát nguyên văn đầu vào, giữ NFD/Cf/hoa-thường/khoảng trắng. Cùng alias ứng với nhiều nguyên văn khác nhau thì hủy toàn lượt; không chọn tên đầu/chuỗi chuẩn hóa. Dò cùng giá trị chuẩn hóa một lần, kể cả kết quả không thấy; hai nhóm mâu thuẫn chặn.

Trần khảo sát đề xuất **2.000 giá trị phân biệt**, **20.000 vị trí**, **8 triệu ký tự** cộng dồn qua các lượt định vị giá trị detector; deadline monotonic tuyệt đối do caller tin cậy cấp, kiểm trước/sau RPC và giữa các lượt. Vượt trần/hạn, hủy, `ChuaRo`, metadata sai hoặc mơ hồ không trả phần đã làm; bỏ tham chiếu khi kết thúc. Deadline là hợp tác, không cắt ngang regex/RPC đang chạy; cần Core cưỡng chế budget. R4/R5 phải giữ **cùng** đối tượng lượt dò/budget cho toàn chuỗi, không tạo lại để né trần. `thu_thap_ung_vien` và `_tra_ung_vien_ram` nhận cùng `TraCuuDinhDanh`; điểm nối Local chỉ dùng sau kiểm `_span`/nguồn, chưa nối runtime Local. `khao_sat_che_chinh_xac` là wrapper khảo sát một lượt, đóng trong `finally`, không dùng wrapper này để giữ trạng thái xuyên bước. Giữ kiểm tiền/ngày/numeric độc lập và mọi kiểm nguồn/đủ đoạn/span Local.

**Cửa dừng:** nhánh SDK R2 trong che/hậu kiểm chặn cố định `MASK_R3_CHUA_CHUNG_MINH` trước giao dịch lịch sử, không có cờ bật khảo sát từ payload/cấu hình. Đầu dò không ghi kho, cấp alias tạm, chốt hay tạo phong bì phát hành. Phần `_che`/mở che RAM lịch sử vẫn giữ để bảo toàn hồi quy trước R5/R6; **chưa xóa matcher khỏi toàn gói hoặc hoàn tất chuyển consumer P4**. Hậu kiểm lịch sử đã bỏ đọc danh mục và chỉ so với vùng gốc đang có trong RAM. Không sửa handler/vòng đời R4 hoặc snapshot R5 để mở đường vượt closure.

**Đo DEMO mới:** [số đo từng ca, chỉ số đếm/mã/thời gian](SO-DO-MASK-R3.json), tái lập bằng `.venv/Scripts/python -B e_mask/tests/do_mask_r3.py`. Gold `tests/demo_mask_r3.json` đóng băng trước phép đo, SHA-256 `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; 16 tên cơ sở (6 tổ chức, 6 người, 4 địa chỉ), 18 câu thường và 64 biến thể. Soạn tách khỏi detector/tập cũ nhưng **chưa có người soạn độc lập**, chưa đủ held-out 45/75/15/15 của §6.6. Không chỉnh detector/ngưỡng sau khi xem số đo. Đối chứng matcher cũ chỉ chạy ngoài gói trên fixture DEMO đã đóng băng, không đọc tên/ngăn Core để bù.

| Bộ đo | Ca | Che đủ, không chặn | Lọt trong bản khảo sát | Chặn nghiệp vụ | Lỗi kỹ thuật | Matcher cũ che đủ gold |
|---|---:|---:|---:|---:|---:|---:|
| Tên cơ sở | 16 | 1 | 7 | 8 | 0 | 16/16 |
| NFD | 16 | 1 | 7 | 8 | 0 | 16/16 |
| Cf chèn | 16 | 1 | 7 | 8 | 0 | 16/16 |
| Cf thay khoảng trắng | 16 | 0 | 12 | 4 | 0 | 15/16 |
| Viết thường | 16 | 1 | 9 | 6 | 0 | 16/16 |

Đây là bản khảo sát trong RAM, **không có kết quả nghiệp vụ nào được phát hành**, không phải số lọt sau hai lớp Local. Tổng 80 ca dương gồm 16 cơ sở +64 biến thể, không tính thành 80 tên độc lập. Trong 8 ca cơ sở bị chặn có 3 ca đã che đủ gold nhưng còn nghi vấn khác; gold che đủ bất kể chặn là **4/16**, không coi 8 chặn là detector tìm đúng. 18 câu thường: **14 giữ nguyên, 0 che thừa, 4 chặn nghiệp vụ, 0 lỗi kỹ thuật**; báo nhầm theo §6.6 = **(che thừa hoặc chặn) 4/18 = 22,22%**. Chuỗi âm tiết thường đã duyệt không chứng minh chính nó đang là tên trong ngữ cảnh hiện tại. Local thật **0 lượt, chưa đo**; không công bố 0 lọt do mọi cửa vận hành bị đóng.

Chi phí CoreGia: 2.000 ứng viên không thấy cần đúng **2.000 RPC tìm định danh, 0,218428 giây**; ứng viên thứ 2.001 bị từ chối trước RPC, không cắt ngầm. Đây là phép tìm không thấy trên kho DEMO nhỏ, không đại diện trường hợp trúng/khóa/CAS/network hoặc quota Core thật. Mẫu thường lặp **500.000 ký tự**, 0 ứng viên/RPC, mất **11,150106 giây**; không đại diện văn bản đa dạng/nhiều thực thể. Chưa đo RAM đỉnh, chi phí model/chuỗi Local/Office, concurrency hoặc máy đích; không chốt trần/SLA bằng hai con số này. Cf thay khoảng trắng còn giảm khả năng tạo ứng viên; không dùng fuzzy hoặc tên giải mã để bù.

**Môi trường:** `.venv` trong worktree, Python 3.13.14, SDK 2.2.0 cài offline từ wheel repo `--no-index --no-deps`; SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp SHA256SUMS. Có jsonschema 4.26.0, pytest 9.1.1 qua `--system-site-packages`; không đổi dependency/lock. Các lệnh dùng `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `-B`. Kiểm kê bytes/SHA tự sinh lại đủ **51 tệp**, ngoài đúng ba runtime, bắt buộc theo SDK khi đổi gói đã khai migration; không đổi manifest/schema/SQL/Core/SDK.

**Kết quả kiểm:** [nguyên lệnh/kết quả thật](KET-QUA-KIEM-MASK-R3.txt). Đã kiểm bằng Core giả (CoreGia).

| Lệnh / phép kiểm | Kết quả thật cuối |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**, 1,17 giây. Cả hai DEMO thiếu xác minh phiên/quyền; không bỏ cửa quyền hoặc dùng adapter có quyền thay CLI chuẩn. Kế thừa C-MS22-01. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2285 passed, 4 xfailed cũ, 190 subtests passed, 0 failed, 0 skipped; 210,94 giây, mã 0**. Bốn xfail strict MASK-2b giữ nguyên lý do giới hạn quy tắc/nợ CAO. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**, 0,62 giây; không tham chiếu cấm, bytecode hoặc symlink trong gói. |
| Kiểm riêng R3 trước lượt full cuối | **25 passed, 1,31 giây, mã 0**, không skip/xfail. |
| Kiểm kê và `git diff --check` | **51/51 tệp** đủ bytes/SHA thực, trừ chính kiểm kê; **diff mã 0**. |

Ca R3 kiểm ngăn SDK/null+cờ thật, tên chỉ từ đầu vào RAM, alias nhiều nguyên văn bị chặn, Local dùng chung budget và không đếm lặp, 2.000/2.001 ứng viên/RPC, budget âm/sai kiểu, deadline trước/sau RPC, hủy/ChuaRo, metadata bị nguồn trả sai, caller đề nghị tên ngoài đầu vào không được gửi tìm, giữ tiền/ngày và cửa phát hành đóng. Giữ nguyên tất cả test an toàn cũ; không sửa hoặc bỏ test, không thêm skip/xfail. Hai lỗi mục tiêu ban đầu thuộc fixture/test R3 mới (chưa nạp từ điển; cấm nhầm cả bộ định vị detector thay vì cấm danh mục) đã được sửa; test hiện chặn liệt kê kho và buộc hậu kiểm không nhận danh mục. Không sửa detector/ngưỡng dựa trên gold.

**Thời gian thực tế:** **20:54:00–21:22:00 ngày 15/11/2026 (UTC+07), 0,47 giờ**, tại mốc chốt kiểm và báo cáo. Bắt đầu theo lead; phiếu **6–8 giờ ƯỚC TÍNH**, độ khó `kho`.

**Lệch khỏi phiếu / quyết định tạm:** dừng ở khảo sát theo cửa dừng Anh giao vì chưa chứng minh chất lượng/chi phí, chưa thay toàn bộ consumer lịch sử hoặc phát hành. Thêm hai trần kỹ thuật 20.000 vị trí/8 triệu ký tự dò như đề xuất thử, chưa coi là quyết định nghiệp vụ. Test an toàn cũ giữ nguyên; không bổ sung xfail/skip, không nâng ngưỡng hiệu năng. Ngoài ba runtime có test/tài liệu và kiểm kê tự sinh bắt buộc. Chưa Core/Local/Office/Linux thật; Cloud tắt, không engine-to-engine/mạng ngoài.

### Cần Core — MASK-R3

- **C-P4-03:** kế thừa chặn R2 về duy nhất bí mật theo vùng/phiên bản, `lay_hoac_tao`, CAS/lô ≤100 và dấu chống lặp sau mất ACK. Cần ghim nghĩa chuẩn hóa/chỉ mục, quota truy vấn/chống dò đoán và xác nhận không ghi ứng viên/băm vào log. 2.000 tìm chính xác không tự bảo đảm chi phí hoặc recall; tên đặc biệt/âm tiết thường/Cf thay khoảng trắng đang là khoảng thiếu cụ thể. Không đề nghị giải mã danh mục hoặc đọc tên cũ để bù. Chưa có bảo đảm thì giữ chặn tên mới/đếm/phát hành.
- **C-P4-04/05, phối hợp R4/R5:** cần nguồn Local thật đủ đoạn và cùng budget/ngữ cảnh/TTL RAM, không hồ sơ Core chứa map/gốc; Core cưỡng chế deadline/RAM/CPU/RPC cả chuỗi, bao gồm lúc detector hoặc RPC chưa trả. Đầu dò R3 chưa chứng minh các cửa đó. Giữ C-P4-01/02 cho ghim instance/vòng đời và C-MS22-01 cho CLI DEMO thiếu quyền. Không có câu Chờ Anh chọn lại nghiệp vụ; lead cần bộ DEMO có người soạn độc lập và phép đo Local/Core thật trước giao lát nâng chất lượng.

## MASK-R4 — kho ánh xạ RAM và vòng đời chuỗi, 15/11/2026

- Đúng ba tệp runtime `kho_anh_xa_ram.py`, `quyen_yeu_cau.py`, `chay.py`; chỉ SDK/stdlib, không sửa Core/SDK/dependency, không commit/push. PR: **chờ lead mở**. Thực tế **20:11:00–20:45:15 ngày 15/11/2026 (UTC+07), 0,57 giờ** tại mốc chốt kiểm/artifact, bắt đầu theo lead; phiếu **4–6 giờ ƯỚC TÍNH**, `kho`. [Báo cáo §6](BAO-CAO-MASK-R4.md), [lệnh/kết quả thật](KET-QUA-KIEM-MASK-R4.txt).
- Kho chỉ giữ một map sống trong RAM Mask, theo mã yêu cầu do port Core tin cậy cấp. Scope gồm phiên/module/người/tài liệu/pháp nhân/DEMO, instance và phiên RAM riêng của kho; mã caller/chuyen_tiep/viec_id không thay quyền. Cấp quyền tạo một lần ở Core; giữ dấu ID/hạn RAM để chặn tái tạo, không giữ kết quả mở. Restart/instance khác/mất RAM/hết hạn/đã tiêu thụ trả `MASK_ANH_XA_KHONG_CON`, yêu cầu chạy lại toàn chuỗi.
- TTL từ snapshot SDK ở bước đầu: mặc định 600, nguyên 60–900; deadline Core được port chiếu sang monotonic cùng tiến trình và lấy hạn sớm hơn. Retry/cấu hình mới không gia hạn. Hash đầu vào theo mã lượt Core, thay đổi thì dọn đúng map và từ chối. Một bước sở hữu; `cho_ai()` nhường handler/khóa khi ra `with`, không giữ handler chờ Hỏi AI. Chuỗi thứ hai và double-open không làm mất map khác.
- Timer daemon dọn khi rảnh, `finally` dọn mọi nhánh kết thúc; tín hiệu Core hủy/lỗi/kết thúc/mất quyền/lease và timeout đồng bộ với khởi tạo, nhận quyền mở, lần kiểm cuối và tiêu thụ. Chặn cả hủy đến trước khi tạo, sau checkpoint cuối hoặc timer xóa map giữa checkpoint/phép đọc. `ChuaRo` chỉ giữ RAM nếu đã chờ AI và còn hạn; mở luôn dọn kể cả mất ACK, Core không được gọi mở lại.
- Adapter vòng đời/đồng hồ/ghim giả chỉ trong `tests/ho_tro_ram.py`; fixture quyền DEMO cũ được nối mixin này, giữ nguyên test hành vi/an toàn cũ. Test R4 có các ca timer thread khi rảnh, đồng hồ giả, lỗi đặt lại timer không stderr, buffer còn memoryview, không I/O/log, sai quyền và nguồn thiếu, hai chuỗi/two-open/restart/đổi instance/retry đổi đầu vào. Đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật. Không có map/gốc/bytes đi qua port mới; Python chỉ bỏ tham chiếu, không bảo đảm xóa vật lý mọi bản sao RAM.
- R4 tạo API kho `buoc()` và chặn handler nếu chưa có cửa ghim/lifecycle. Handler nghiệp vụ cũ giữ để kiểm hồi quy bằng fixture ngoài gói; chưa nối kho RAM mới thay snapshot/ngăn cũ vì các tệp đó thuộc R2/R5/R6/B7. Không nhận đây là luồng che–Local–mở P4 đã tích hợp hoàn chỉnh hoặc có thể vận hành với SDK hiện tại.
- Nền trước sửa: **2227 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed; 181,60 giây, mã 1**. Kiểm kê nền sai bytes/SHA ở `e_mask/khoi_tao_ngan.py` và migration do xuống dòng checkout; không sửa hai tệp. Lượt full đầu sau R4: **2284 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed; 132,32 giây, mã 1**. Hai lượt tiếp theo trong quá trình bổ sung ca đua: **2302 passed / 150,82 giây** và **2304 passed / 149,80 giây**, đều chỉ một failure kiểm kê, cùng 4 xfailed/190 subtests. Lượt chốt sau sửa cuối: **2305 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests passed, 0 skipped; 147,49 giây, mã 1**. Kiểm riêng R4 **78 passed, 1,12 giây, mã 0**. Bốn xfail có lý do cũ “giới hạn quy tắc, nợ CAO”; không đổi ngưỡng hiệu năng/xfail/skip hoặc nới bộ kiểm độc lập.
- Kiểm kê R1 bao toàn bộ bytes gói, nên ba runtime mới/đổi và CHANGELOG cần được băm lại khi gộp. Đã xin ngoại lệ cho `sql/kiem_ke.json` do bảng §4 chỉ cho ba tệp mã/khai báo; chưa cập nhật khi chưa có phản hồi. Không âm thầm sửa tệp thứ tư hoặc thay bộ kiểm để che lỗi. CLI cuối **0/2 ĐẠT, mã 1**, cả hai `MASK_NGU_CANH_CHUA_XAC_MINH`; kiểm độc lập gói gốc **mã 1**, duy nhất kiểm kê không khớp; `git diff --check` **mã 0**. [Kiểm kê đề nghị ngoài gói](KIEM-KE-MASK-R4-DE-NGHI.json) có **51/51 tệp**; bản sao đóng gói dùng kiểm kê này qua kiểm độc lập **mã 0**, không thay kết quả kiểm gói gốc. Kết quả ba lệnh cuối và thời gian thật ở báo cáo; khi lead gộp R2 phải tạo lại kiểm kê, không áp mù bản đề nghị trước gộp.

### Cần Core — MASK-R4

- **C-P4-01 còn mở:** nguồn quyền xác thực mã chuỗi/pháp nhân/module/người/tài liệu/DEMO và ghim cùng instance + phiên RAM qua mọi bước/retry. Không spawn/failover để tiếp tục map cũ. Cấp quyền tạo đúng một lần cho chuỗi mới, không cấp lại sau restart/đã tiêu thụ; giữ mã lượt ổn định để đối chiếu băm. `so_viec_dong_thoi=1` không đủ. Protocol Python nội bộ trong R4 chưa phải API SDK đã có; không lấy đối tượng/cờ từ payload/cấu hình để tự chứng thực. Thiếu cửa thì `MASK_CHUOI_CHUA_GHIM` (thiếu quyền hoàn toàn giữ `MASK_NGU_CANH_CHUA_XAC_MINH`).
- **C-P4-02 còn mở:** kênh sự kiện vòng đời đã xác thực phải tới Mask khi rảnh ở bước AI; đối chiếu đủ scope/instance/phiên RAM và đồng bộ bàn giao kết quả cuối/ACK với điểm chốt tiêu thụ. Port chiếu deadline Core sang monotonic Mask, chỉ báo không có hạn sớm hơn bằng `None` khi đã biết chắc. TTL là dự phòng, không thay hủy ngay; kết quả cuối Core đã nhận được giao lại theo quyền, không gọi mở lại để phục hồi map/bản rõ. Không thêm route/kênh liên engine trong R4.
- Giữ C-P4-03/04/05/06 và phần R2/R3/R5/R6/B7 chưa tích hợp. Không có câu hỏi nghiệp vụ mới hoặc đề nghị giải mã `bi_mat`/lưu hồ sơ phục hồi. Cần lead băm lại kiểm kê sau gộp R2/R4; không dùng adapter DEMO thay cửa CLI chuẩn hoặc nhận là đã kiểm Core thật.
## MASK-R2 — adapter nhận diện chỉ bí mật/metadata, 15/11/2026

**Kết luận: Chưa đạt nghiệm thu chung — adapter R2 và full test đạt, CLI chuẩn vẫn thiếu cửa quyền và C-P4-03 còn mở.** PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia); không commit/push.

**Đã làm:** đúng bốn runtime `kho_ngan.py`, `kho_dinh_danh.py`, `kho_qua_core.py`, `khoi_tao_ngan.py`. `KhoDinhDanh.mo_kho_nhan_dien(viec)` trả `KhoNhanDienQuaCore`; chỉ dùng `viec.ngan` kiểu `NganEngine` SDK 2.2.0, kiểm lại nguồn quyền trước/sau đọc. `tim_ung_vien(gia_tri, nhom)` chuẩn hóa trong RAM theo phiên bản `NFC_CF_KHOANG_TRANG_LOWER_1`, tìm đúng giá trị bí mật cùng vùng/phiên bản, không lọc tên một phần/liệt kê danh mục hoặc băm tên không khóa. Phát hiện nhiều ID cùng giá trị hoặc nhóm mâu thuẫn thì chặn, không chọn dòng đầu hay gom null.

Kết quả chỉ ID, alias chính thức, nhóm/trạng thái/phiên bản/số gặp, null+cờ mã hóa. Alias đã có được tìm lại qua hai việc độc lập, không ghi thêm alias/đếm/map. Cột số của SDK trả chuỗi thập phân được kiểm là số nguyên không âm rồi chuyển về số đếm; không mock ngăn trả kiểu khác để làm xanh. Không giữ ứng viên/map/alias tạm, không tạo `cum`, `dau_gap`, JSON lồng hoặc snapshot phục hồi. Phần tìm ứng viên trong luồng che thuộc R3; RAM/consumer MASK-2c/handler thuộc R4/R5, mở che thuộc R6.

`KhoNganBiMat.sua_metadata` chỉ nhận ID opaque/phiên bản và allowlist nhãn/trạng thái, bỏ hẳn khóa bí mật/cờ/đếm/JSON. Primitive `duyet_cung_id` cho R7 đổi trạng thái trên chính ID, thêm alias chính thức trong cùng lô có CAS và duy nhất alias; không đọc-sao bí mật, không null đè bí mật. Không dùng `lay_hoac_tao` alias để âm thầm nhận alias thuộc ID khác. Từ chối bằng trạng thái, không xóa. Primitive này chưa là cửa Admin hoạt động: R7/C-P4-06 phải xác minh biên nhận xem/duyệt trước khi gọi, không có cờ tự khai quyền trong R2.

Lô tối đa 100 thay đổi, vượt chặn trước gửi và không chia giả nguyên tử. SDK retry giữ nguyên khóa lô; mất mọi ACK, kể cả HTTP 408 hoặc lỗi `NGAN_*` chưa xác định sau ghi, trả `ChuaRo` với mã tương quan an toàn. Đối tượng đã chưa rõ không gửi lô mới; giao lại đối tượng mới với phiên bản cũ chịu CAS, không cấp thêm alias hoặc tăng đếm. Không lưu kết quả/bản rõ để phục hồi. Mã tương quan/thông điệp từ nguồn không được đưa nguyên ra ngoài.

**C-P4-03 chặn tạo tên/tăng số gặp:** R1 hiện chỉ khai duy nhất ID/alias. SDK thật từ chối `lay_hoac_tao` theo bộ bí mật + vùng + phiên bản vì chưa khai ràng buộc đó; hai ID cùng bí mật vẫn ghi được trong CoreGia. R2 không giả có bảo đảm: `lay_hoac_tao`, `ghi_cho_duyet`, `ghi_nhan_gap_lai`/chốt snapshot mới trả `MASK_KHO_CAN_CORE`, không ghi gì. Không nhận cờ cấu hình/payload để mở khóa. Mọi cửa `AnhNgan`, `DauNgan`, `PortNgan`, `doc_het` lịch sử đều chặn `NganEngine`; chỉ giữ hành vi RAM cũ cho hồi quy tới khi R3/R4/R5 thay consumer, không sửa `chay.py` của R4.

**Môi trường:** `.venv` riêng trong worktree, Python 3.13.14, pytest 9.1.1, SDK 2.2.0 cài offline từ wheel repo với `--no-index --no-deps`; SHA-256 **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** khớp SHA256SUMS. Có `jsonschema` qua gói đã cài sẵn của máy (`--system-site-packages`), không thêm dependency chạy/khóa phụ thuộc. Các lệnh dùng `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `-B`.

**Kết quả kiểm:** đã kiểm bằng Core giả (CoreGia), [nguyên kết quả lệnh](KET-QUA-KIEM-MASK-R2.txt).

| Lệnh / phép kiểm | Kết quả thật cuối |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Cả hai DEMO: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Giữ nguyên cửa quyền; không nhận cấu hình/payload tự khai làm quyền. Kế thừa C-MS22-01. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2260 passed, 4 xfailed cũ, 190 subtests passed, 0 failed, 0 skipped; 150,03 giây; mã 0**. Bốn xfail strict của MASK-2b giữ nguyên lý do “giới hạn quy tắc, nợ CAO”; không thêm skip/xfail hoặc sửa test an toàn cũ. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; không tham chiếu cấm, bytecode/symlink trong gói. |
| Kiểm riêng R2 trước lượt full cuối | **32 passed, 1,16 giây; mã 0**, không skip/xfail. |
| Kiểm kê và `git diff --check` | **50/50 tệp** đủ bytes/SHA thực, trừ chính kiểm kê; **diff mã 0**. |

Ca R2 gồm null+cờ/tìm đúng, không lộ tên/băm ở khóa/metadata/log, hai việc CoreGia tranh cùng ID, DEMO–thật, CAS/duy nhất/rollback, lô 100/101, retry cùng khóa, mất mọi ACK/408 và không mở ngược kho. Wrapper chỉ spy/gây lỗi sau ngăn SDK thật, không mock kết quả trả tên thay null+cờ. Lượt full trước hai ca 408: **2258 passed, 4 xfailed cũ, 190 subtests passed, 151,77 giây; mã 0**. Lượt full đầu **2256 passed, 1 failed, 4 xfailed, 190 subtests, 122,40 giây**: phần bổ sung NGUON bị PowerShell đổi mã tiếng Việt; đã sửa và kiểm lại, không bỏ test. Lượt chốt 2260 là sau mọi sửa runtime.

**Thời gian thực tế:** **20:10:00–20:43:12 ngày 15/11/2026 (UTC+07), 0,55 giờ**, tại mốc chốt báo cáo; bắt đầu theo mốc lead. Phiếu **5–7 giờ ƯỚC TÍNH**, độ khó `kho`; không quy đổi ước tính thành thời gian thực tế.

**Lệch khỏi phiếu / quyết định tạm:** không đổi nghiệp vụ/API/SDK, không tự nhận bảo đảm Core còn thiếu. Ngoài bốn runtime có test/tài liệu và **sinh lại `sql/kiem_ke.json` theo bytes/SHA thực của 50 tệp**, bắt buộc khi đổi gói đã khai migration R1; không sửa nội dung migration, manifest, schema, nguồn cũ, Core/SDK hoặc dependency. Không nối luồng che mới/màn Admin ngoài R2, không dùng fallback RAM để tuyên bố hỗ trợ ngăn SDK. Cloud tắt; chưa kiểm Core/PostgreSQL/Local/Office/Linux thật.

### Cần Core — MASK-R2

- **C-P4-03 / duy nhất bí mật:** cần xác nhận bằng chứng và khai báo/chỉ mục duy nhất đúng bộ `(vung_du_lieu, phien_ban_chuan_hoa, gia_tri_chuan)` với băm do Core quản; `lay_hoac_tao` nguyên tử theo bộ đó, CAS/lô ≤100, quy tắc chuẩn hóa và hạn mức dò. Test hiện chứng minh khoảng thiếu, không chứng minh Core thật đã bảo đảm. Không xin giải mã hoặc tự tính băm công khai để lấp chỗ thiếu.
- **C-P4-03 / đếm gặp, giao lại:** cần dấu/lượt nguyên tử do Core cấp hoặc xác nhận để không tăng số gặp/tạo tên hai lần khi giao lại việc sau mất ACK. Khóa ngẫu nhiên theo mỗi lô của SDK chỉ bảo vệ gửi lại cùng lô, không tự bảo vệ lần chạy handler mới. Tới khi có bảo đảm này, đường tạo và đếm vẫn chặn; không ghi map/tên/snapshot vào dấu.
- Cần Core xác nhận quota/không log ứng viên hoặc băm, quyền theo vùng và bảo đảm trên Core thật. R2 mới kiểm CoreGia; giữ C-P4-01/02/04/05/06. R7 phải nối quyền/biên nhận Admin trước khi dùng primitive metadata; R3/R4/R5/R6 tích hợp theo closure riêng. Không phát sinh câu Chờ Anh chọn lại nghiệp vụ.

## MASK-R1 — khai ngăn bí mật và cấu hình SDK 2.2, 15/11/2026

### Cập nhật sửa hồi quy theo lệnh lead — 15/11/2026, bắt đầu 19:52

**Kết luận: Đạt yêu cầu sửa hồi quy MASK-R1; chưa đạt nghiệm thu chung vì CLI chuẩn thiếu cửa quyền Core và C-P4-03 còn mở.** PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia).

- Schema hiện có đã đặt default cho mọi trường mới: TTL mặc định 600, số nguyên 60–900, không trường bắt buộc thiếu default, không nhận khóa lạ. Không cần sửa schema. Nguyên nhân 440 failure là guard cũ trong `chay.py::_loi_cong` từ chối mọi snapshot cấu hình có trường sau khi SDK điền default.
- Theo ngoại lệ lead cho thêm `chay.py` ngoài giới hạn 5 tệp: bỏ guard chỉ được cấu hình rỗng, dùng kiểm schema của SDK 2.2.0. Giữ nguyên thứ tự xác minh ngữ cảnh/port và kiểm nghiệp vụ trong handler, mã lỗi cũ, hậu kiểm và kho RAM vận hành tới R2/R4. Không nối kho bí mật R1 vào handler, không bỏ kiểm schema/quyền hoặc thêm đường giải mã.
- Cập nhật test S22 về khai báo ngăn/migration R1 và snapshot TTL; kiểm handler qua CoreGia với cấu hình rỗng và TTL 60/600/900. Giữ nguyên 46 test R1 (có các ca TTL sai, khóa lạ, biên/default/snapshot) và bốn xfail cũ; không thêm skip/xfail. Cập nhật NGUON/CHANGELOG và kiểm kê theo bytes thực tế của gói.

Môi trường: `.venv/Scripts/python`, Python 3.13.14, SDK **2.2.0**; SHA-256 wheel offline **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** khớp `SHA256SUMS.txt`. Các lệnh dùng `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `-B`.

| Lệnh / phép kiểm | Kết quả thật sau sửa hồi quy |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Cả hai DEMO trở lại mã cũ `MASK_NGU_CANH_CHUA_XAC_MINH`, câu “Chưa xác minh được phiên và quyền xử lý yêu cầu.”; không còn lỗi cấu hình. Không cấp quyền DEMO trong runtime để làm CLI xanh. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --basetemp=.pytest-tmp --tb=short` | **2228 passed, 4 xfailed cũ, 190 subtests passed, 0 failed, 0 skipped; 187,94 giây; mã 0**. Tăng 3 ca do tham số hóa kiểm handler TTL. |
| `.venv/Scripts/python -B -m pytest e_mask/tests/test_mask_r1.py -q --basetemp=.pytest-tmp-r1 --tb=short` | **46 passed, 0 failed/skip/xfail; 0,82 giây; mã 0**. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; giữ nguyên bộ kiểm. |
| Kiểm kê SQL và phạm vi migration | **50/50 tệp** đủ bytes/SHA-256, trừ chính kiểm kê; `_kiem_ke` và `_kiem_lenh_sql` đạt. Không đổi nội dung migration. |
| `git diff --check` | **ĐẠT, mã 0**. |

**Thời gian thực tế lượt sửa hồi quy:** **19:52:00–19:59:50 ngày 15/11/2026 (UTC+07), 0,13 giờ** tại mốc chốt kiểm; phiếu toàn lát R1 **4–6 giờ ƯỚC TÍNH**. Lượt R1 trước đó 0,34 giờ giữ riêng ở lịch sử bên dưới; không coi 4–6 giờ là ước tính riêng cho lượt sửa hồi quy này.

Không phát sinh Cần Core / Chờ Anh mới; các mục Cần Core — MASK-R1 bên dưới giữ nguyên. Chưa kiểm Core/PostgreSQL/Local/Office/Linux thật. Không commit/push.

### Lịch sử lượt R1 trước sửa hồi quy (18:57–19:17)

**Kết luận: Chưa đạt — phần khai báo và 46 test riêng R1 đạt, nhưng CLI chuẩn 0/2 và full pytest có 440 failure sau thay đổi TTL; C-P4-03 chưa đủ bảo đảm.** PR: **chờ lead mở**. Không nhận là đã xong nghiệm thu hoặc đã giữ toàn bộ test an toàn cũ xanh.

**Phạm vi:** đúng 5 tệp `engine.json`, `cau_hinh.schema.json`, `sql/001_tao_kho_bi_danh.sql`, `sql/kiem_ke.json`, `e_mask/khoi_tao_ngan.py`; ngoài ra test và VIEC/CHANGELOG. Bản gói 1.4.0 chưa phát hành, SDK `>=2.2.0 <3.0.0`, `cuc_bo`, `so_viec_dong_thoi=1`. Hai bảng phạm vi engine dùng chung tập đoàn: `dinh_danh` giữ tên gốc/chuẩn hóa trong hai cột `bi_mat:true`, metadata và ID opaque; `bi_danh` chỉ ID/alias chính thức/lịch sử/metadata. Không bảng map, mã yêu cầu, alias tạm theo chuỗi hoặc cột JSON. Migration chỉ tạo bảng/chú thích trong `eng_e_mask`, cột bí mật và dấu tra cứu kiểu `bytea` đúng mẫu. Không tự tạo chỉ mục duy nhất bí mật chưa được Core xác nhận. TTL mặc định 600, số nguyên 60–900; cửa đọc từ `viec.cau_hinh`, cửa ngăn chỉ nhận `NganEngine` SDK, không tạo ngăn dự phòng.

**Kiểm nền trước sửa:** Python 3.13.14, SDK 2.2.0 từ wheel offline, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp `SHA256SUMS.txt`; pytest 9.1.1 có sẵn qua venv `--system-site-packages`. `.venv/Scripts/python -B -m pytest e_mask/tests -q --tb=short` → **2179 passed, 4 xfailed, 190 subtests passed, 0 skipped; 166,75 giây; mã 0**. Bốn xfail lịch sử giữ nguyên. Đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật.

**Kết quả sau sửa:** dùng `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` và `-B`; đã kiểm bằng Core giả (CoreGia). Đầu dò riêng R1 dùng đúng manifest/schema/ngăn SDK, chỉ nằm ngoài gói; không thay handler thật.

| Lệnh / phép kiểm | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Cả hai báo “Cấu hình engine không hợp lệ. Hãy nhờ quản trị viên kiểm tra lại.” (`CAU_HINH_KHONG_HOP_LE` từ cổng cũ). |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **1785 passed, 440 failed, 4 xfailed, 190 subtests passed, 0 skipped; 94,88 giây; mã 1.** 46 test mới nằm trong 1785 passed. Bốn xfail “giới hạn quy tắc, nợ CAO” giữ nguyên, không thêm xfail/skip. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; cho đúng ngoại lệ migration đã khai/kiểm kê, không nới cấm import/kết nối/truy vấn lúc chạy. |
| `.venv/Scripts/python -B -m pytest e_mask/tests/test_mask_r1.py -q --tb=short` | **46 passed, 0 failed/skip/xfail; 0,72 giây; mã 0**: ghi/đọc/tìm chính xác null+cờ, không lộ băm/tên qua cửa đọc, sửa metadata/CAS/lô nguyên tử/alias duy nhất, khoảng thiếu duy nhất bí mật, TTL/default/bản chụp, không tạo ngăn RAM dự phòng, cấu trúc/schema/kiểm kê và chặn migration ngoài phạm vi. |
| Inventory và tệp mới | **50/50 tệp** khớp bytes + SHA-256, không tính chính kiểm kê; không bytecode/symlink. Kiểm UTF-8/khoảng trắng 6 tệp mã/khai báo/test mới hoặc đổi đạt. |
| `git diff --check` | **ĐẠT, mã 0**. |

Failure trải ở 10 tệp test cũ; gồm cổng cấu hình chặn trước nghiệp vụ và ba ca S22 chưa khớp khai báo/cấu hình mới. Nền đã xanh trước sửa, nên **không gọi 440 failure là lỗi nền**, không bỏ test cũ hoặc tiêm cấu hình rỗng để làm xanh. Lượt đầu kiểm riêng R1 có 9 failed/37 passed do đầu dò chưa đăng ký ba năng lực không dùng; đã sửa phần đăng ký test ngoài gói và kiểm lại 46/46, không sửa handler để né lỗi.

**Thời gian thực tế:** **18:57:00–19:17:14 ngày 15/11/2026 (UTC+07), 0,34 giờ** tại mốc chốt bàn giao (bắt đầu theo lead); phiếu **4–6 giờ ƯỚC TÍNH**, độ khó **kho**. Không quy đổi số giờ ước tính thành giờ thực tế.

**Lệch khỏi điều kiện đạt:** giữ đúng 5 tệp mã/khai báo nhưng chưa đạt yêu cầu test an toàn cũ xanh và chưa nối ngăn R1 vào runtime. Không dùng quyết định tạm để nới phạm vi, giải mã hoặc bật Cloud. Kiểm kê tính bytes thực tế của gói checkout hiện tại (48/50 tệp có CRLF); sau thay bytes/checkout/đóng gói phải tạo và kiểm lại inventory, không chuẩn hóa LF rồi gọi đó là SHA bytes thật. Chưa chạy Linux/Core/PostgreSQL/Local/Office thật.

**Điểm tích hợp đã phát hiện:** `chay.py::_loi_cong` cũ từ chối cấu hình khác rỗng; SDK điền TTL mặc định làm cấu hình có trường. R1 không được sửa `chay.py` ngoài bảng §4, không bỏ mặc định hoặc tiêm cấu hình rỗng trong test để che lỗi. Các test S22 còn khẳng định không khai ngăn/migration và cấu hình rỗng; giữ nguyên để báo kết quả thật. Kho RAM cũ trong `chay.py` chưa được thay, cửa R1 chưa được nối vào handler; không gọi đầu dò R1 là nghiệm thu vận hành. R2/R4 xử lý adapter/handler theo phiếu, cần lead chốt lát tích hợp để đạt yêu cầu test an toàn cũ xanh. Bộ kiểm độc lập được bổ sung ngoại lệ migration đã khai, kiểm kê đủ bytes/SHA và chỉ CREATE TABLE/COMMENT trong schema riêng; vẫn chặn mã kết nối/chạy truy vấn và tham chiếu cấm.

### Cần Core — MASK-R1

- **C-P4-03 còn mở:** SDK mẫu không chứng minh bảo đảm duy nhất/`lay_hoac_tao` theo bí mật + vùng + phiên bản chuẩn hóa trên Core thật. Khai hiện tại chỉ duy nhất ID/alias; test CoreGia chứng minh hai ID khác nhau cùng bí mật vẫn được ghi. Không coi kết quả null+cờ/tìm chính xác là chống trùng đã đạt. Core cần xác nhận chuẩn hóa/băm/chỉ mục/duy nhất/CAS/lô ≤100/hạn mức chống dò và không log ứng viên/băm; không xin đường giải mã.
- Các cửa C-P4-01/02/04/05/06 giữ nguyên theo P4, chưa chứng nhận. Thiếu bảo đảm bí mật thì chưa dùng kho này vận hành/chưa nhận đủ nghiệm thu. Không sửa Core/SDK, nguồn cũ hoặc bản khai lưu trữ; không commit/push.
- **Cần lead — tích hợp ngoài R1:** guard cấu hình và lựa chọn kho trong `chay.py` thuộc closure R2/R4, ngoài 5 tệp R1. Cần lát tích hợp phù hợp P4 để nhận TTL, nối adapter bí mật và bỏ kho RAM vận hành cũ; không chỉ bỏ guard rồi nối adapter cũ đang dùng khóa/JSON rõ. Đây là bất tương thích của mã engine/ranh giới lát, không phải lỗi SDK mới hoặc lý do xin Core giải mã. Không có câu Chờ Anh chọn lại nghiệp vụ.

## MASK-P4 — mở che RAM cùng chu kỳ, 15/11/2026

**Kết luận: Đạt phạm vi lập phiếu tài liệu; chưa đạt kiểm nền gói theo AGENTS.md §5.** PR: **chờ lead mở**. Chỉ bốn tệp Markdown: phiếu [MASK-P4-MO-CHE-RAM.md](MASK-P4-MO-CHE-RAM.md), phiếu giao, nhãn lịch sử P3 và VIEC; không đổi mã/manifest/SQL/schema/CHANGELOG gói, không commit/push.

**Đã làm:** thiết kế B chỉ RAM cùng chu kỳ, mã do Core cấp/ghim instance/TTL đề xuất 600 giây cấu hình 60–900/dọn ngay sau mở-hủy-lỗi-kết thúc-hết hạn; mất RAM lỗi rõ yêu cầu chạy lại, không mở thiếu. Kho chính thức chỉ alias+cột bí mật/metadata, tìm chính xác từng ứng viên qua băm, không matcher danh mục rõ; Admin chỉ metadata, xem tên tại Core. Lập R1…R7 (**32–46 giờ ƯỚC TÍNH**), sửa B5…B10 (**36–56 giờ ƯỚC TÍNH**), mỗi lát ≤5 tệp mã và khối lệnh tự đủ. Đánh dấu A của P3 **không dùng theo quyết định Anh 15/11 tối**, giữ nguyên lịch sử, không chờ chọn lại A/B/C. Các khối MASK-2c cũ chỉ để truy vết phần snapshot, R4/R5 chuyển sang RAM; Local hai lớp và Cloud tắt vẫn giữ.

**Môi trường kiểm thật:** `.venv` trong worktree, Python **3.13.14**, pytest **9.1.1**, SDK wheel offline **2.2.0**; SHA-256 **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** khớp `SHA256SUMS.txt`. Venv dùng gói kiểm có sẵn qua `--system-site-packages`, không mạng/không thêm dependency gói. Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` và dùng `-B`. **Đã kiểm bằng Core giả (CoreGia)** cho mã hiện có, chưa kiểm R/B mới, Core/Office/Local/Linux thật.

| Lệnh / phép kiểm | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Cả hai: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **1475 passed, 434 failed, 4 xfailed, 188 subtests passed, 0 skipped; 348,28 giây; mã 1.** Bốn xfail held-out quy tắc cũ giữ nguyên. Nhiều lỗi handler là `MASK_KHO_LOI`; hai subtest hiệu năng vượt 5 giây (7,864 và 7,042 giây). Không kết luận mọi lỗi do `bi_mat` hoặc một nguyên nhân SDK. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; không tham chiếu cấm/tệp biên dịch trong gói. |
| Regex khối lệnh mới | **7/7 MASK-R + 6/6 MASK-B5…B10 ĐẠT**; toàn bộ B **10/10** đọc được theo regex tiêu đề + fenced block. Bảng số tệp R/B đều ≤5; giờ/tệp/phụ thuộc khớp khối lệnh. |
| `git diff --check` và kiểm tệp mới chưa stage | **ĐẠT, mã 0**; tệp mới kiểm riêng UTF-8/NFC/fence/khoảng trắng, liên kết tương đối tồn tại. Cảnh báo LF→CRLF của Git không phải lỗi khoảng trắng. |

**Thời gian thực tế:** **18:21:00–18:37:41 ngày 15/11/2026 (UTC+07), 0,28 giờ**, theo mốc bắt đầu lead và giờ chốt bàn giao. Lệnh giao **không nêu giờ ƯỚC TÍNH riêng MASK-P4**, không lấy dự toán MASK-P cũ hoặc giờ R/B tương lai làm ước tính lát tài liệu này.

**Lệch khỏi phiếu / quyết định tạm:** không đổi phạm vi chỉ tài liệu, không dùng quyết định tạm thay câu 10/CĐ-36. Chạy đủ ba lệnh dù có lỗi nền, không sửa runtime/test để làm xanh. TTL/trần ứng viên là đề xuất kỹ thuật để đo, không trình bày như số đã được Anh duyệt. Chưa lấy kiểm tài liệu đạt làm nghiệm thu chung của engine.

### Cần Core — MASK-P4 (thay phần mâu thuẫn của P3/P2/MASK-2c)

- **C-P4-01:** mã yêu cầu từ Core/ACL tin cậy xuyên bước; ghim **cùng tiến trình/instance** cho mọi bước Mask, không spawn mỗi việc/failover tiếp tục; hàng chờ tối đa một chuỗi map sống. `cuc_bo` và `so_viec_dong_thoi=1` riêng lẻ không đủ. Thiếu thì runtime từ chối, chỉ adapter CoreGia.
- **C-P4-02:** báo kết thúc/hủy/lỗi/lease/deadline toàn chuỗi khi Mask đang rảnh, đồng bộ tiêu thụ một lần và bàn giao ACK; không gọi mở lại sau map đã dọn, mất RAM yêu cầu chạy mới. TTL là dự phòng, không thay việc báo hủy ngay.
- **C-P4-03:** xác nhận chuẩn hóa/băm/tìm chính xác `bi_mat`, duy nhất/lay_hoac_tao/CAS/lô ≤100/hạn mức chống dò; kết quả null+cờ/metadata, không log tên/băm, không đường giải mã. Đo lại độ phủ khi bỏ matcher danh mục rõ; thiếu bằng chứng chặn phát hành.
- **C-P4-04:** điều phối Local đủ đoạn/nguồn xác minh/quyền, thay snapshot chứa map/gốc của C-M2C-01/05, C-MB-01/02; Core không cất hoặc cấp lại hồ sơ ánh xạ để phục hồi. Lead điều chỉnh profile/sổ chung khi cần; P4 không sửa API/SDK/nguồn chung.
- **C-P4-05:** streaming/trần thực/413/budget RAM và thời gian cả chuỗi, quyền tệp/cách ly upload/ACK/ChuaRo; không dump payload/traceback/log/stderr/crash dump/tệp tạm bản rõ hoặc map. Kế thừa C-MB-03, không dùng giữ gốc tại Core để khứ hồi.
- **C-P4-06:** cửa Xem dữ liệu Core và biên nhận duyệt ID+phiên bản không tên, quyền xem/duyệt tách; UI engine không nhận bản rõ. Migration dữ liệu cũ/khóa/JSON/bản sao do Core/lead kiểm soát, không để engine đọc tên cũ chuyển hộ. Thiếu cửa thì giữ chờ, không duyệt mù.

Không còn câu Chờ Anh chọn A/B/C/Q1…Q4 của P3. Cần Core/lead xác nhận các cửa chung và đo TTL/budget/chất lượng; không hỏi lại cho phép giải mã `bi_mat` hoặc lưu ánh xạ. Các đề nghị lịch sử bên dưới về map/snapshot/gốc phục hồi **không còn hiệu lực**, các yêu cầu nguồn/quyền/CAS/trần/Admin không mâu thuẫn tiếp tục áp dụng theo phiếu P4.

## MASK-P3 — mở che/kho bí danh SDK 2.2.0, 15/11/2026

> **Lịch sử, bị MASK-P4 thay về nghiệp vụ:** A **không dùng theo quyết định Anh 15/11 tối**, không chờ Anh chọn Q1…Q4. Các đề nghị giữ map/hồ sơ, chỉ trả alias/tham chiếu, chuyển capability theo A bên dưới không giao nữa. CĐ-36 vẫn cấm giải mã `bi_mat`; quyền/Admin/tìm bí mật phù hợp được kế thừa ở C-P4-01…06.

- **Xong phạm vi tài liệu trình lead/Anh; kiểm nền gói chưa đạt.** PR: **chờ lead mở**. Chỉ thêm [MASK-P3-MO-CHE-SDK-2.2.md](MASK-P3-MO-CHE-SDK-2.2.md) và cập nhật VIEC; không sửa mã/manifest/schema/CHANGELOG gói, không commit/push. Đề xuất A, so sánh A/B/C, liệt kê các điểm cần bản rõ kể cả dò danh mục/giao lại; bảng tác động B5…B10, 7 lát ≤5 tệp với **32–46 giờ ƯỚC TÍNH** và Q1…Q4. Đây không phải code đã được giao hay chức năng đã triển khai.
- **CĐ-36 — Anh, 15/11/2026 16:28 (nguyên văn ý):** “KHÔNG mở đường Core giải mã hộ engine. Trường bi_mat chỉ mã hóa khi ghi, tìm theo băm, engine đọc ra null. Mask phải đổi cách gỡ che (ví dụ trả về bí danh hoặc mã tham chiếu, bản rõ chỉ người có quyền xem qua cửa Xem dữ liệu của Core). Không làm đường giải mã nào khác.” Không còn chờ phê duyệt đường giải mã. Không dùng module, tệp hồ sơ/snapshot, trường rõ hoặc JSON ánh xạ làm đường vòng. Các ghi chú cũ chờ đường giải mã trong tài liệu chung phải được lead thay theo CĐ-36; P3 không sửa tài liệu chung.
- A giữ alias/tệp AI sửa + tham chiếu; bản rõ xem tại Core đúng quyền. B8 không còn trả bytes gốc hay tệp đã khôi phục tên. Admin xem tại Core rồi duyệt ID/phiên bản, không đọc/chuyển bản rõ trong màn engine. Kho đề xuất một dòng thực thể có trường bí mật + metadata trạng thái, alias/lịch sử riêng, chống trùng bằng tìm bí mật/duy nhất do Core quản; không dùng tên chuẩn hóa làm khóa, không SHA tên công khai. Dò danh mục kín chưa chứng minh đủ thì chặn phát hành; Cloud giữ tắt.

**Môi trường và kết quả lệnh thật:** Windows, Python **3.13.14**, pytest **9.1.1**; venv `.venv` trong worktree dùng gói kiểm có sẵn (`--system-site-packages`), SDK cài wheel offline `--no-index --no-deps`, không thêm dependency vào gói. Wheel **2.2.0** SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp SHA256SUMS; kiểm phiên bản in **2.2.0**. Dùng `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `-B`; không tạo bytecode trong gói. Các kiểm này **đã kiểm bằng Core giả (CoreGia)** cho mã hiện có, không chứng nhận thiết kế A/Core thật/Office/Local hoặc Linux thật.

| Lệnh (SDK 2.2.0) | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**; cả hai: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --basetemp=.pytest-tmp-mask-p3` | **1475 passed, 432 failed, 4 xfailed, 190 subtests passed, 0 skipped; 96,37 giây; mã 1.** Bốn xfail cũ của held-out lớp quy tắc giữ nguyên, không bỏ/đổi test. Nhiều ca qua handler trả `MASK_KHO_LOI`; không kết luận mọi lỗi đều do trường `bi_mat` vì gói chưa khai/chuyển kho theo 2.2. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; không tham chiếu cấm/bytecode. |
| `.venv/Scripts/python -B e_mask/tests/chay_demo.py` (bổ sung) | **0/2 ĐẠT, mã 1**, cả hai `MASK_KHO_LOI`; đã kiểm bằng Core giả (CoreGia). |

Đối chiếu bổ sung SDK **2.0.0** (gói Mask chưa chuyển): SHA wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` khớp SHA256SUMS. CLI chuẩn vẫn **0/2, mã 1** thiếu quyền; kiểm độc lập **ĐẠT, mã 0**; adapter DEMO **2/2, mã 0**. Pytest toàn bộ dừng collection: **1 error, mã 1**, `test_mask_2c_4.py` nạp Hỏi AI đã dùng `NganXungDot` từ SDK 2.2.0 nên SDK 2.0.0 thiếu import này (13,24 giây lượt `--tb=no`; xác minh `--tb=short -x` 5,88 giây cùng lỗi). Không có kết quả pytest toàn bộ xanh dưới 2.0.0 để công bố. **Đã trả venv về SDK 2.2.0**; không sửa runtime/test để né lỗi. Đơn ca `test_core_gia_ten_da_duyet_bo_dau_giu_alias` dưới 2.2.0 cũng thất bại (1 failed, 4,34 giây), xác nhận lỗi nền handler. Giả thuyết từ đọc mã: `ngan_cua_viec` ưu tiên `viec.ngan` mới thay vì ngăn tạm tiêm trước đây; cần lát chuyển SDK kiểm tiếp, chưa kết luận nguyên nhân đủ cho 432 ca.

- `git diff --check`: **mã 0**; kiểm thêm UTF-8/NFC và khoảng trắng ở cả tệp mới chưa stage. Lệnh phụ `git diff --no-index --check -- /dev/null e_mask/docs/MASK-P3-MO-CHE-SDK-2.2.md` trả mã 1 vì có khác biệt/tệp mới, không báo lỗi khoảng trắng (chỉ cảnh báo LF sẽ thành CRLF). Không lấy kiểm tài liệu đạt thay cho ba lệnh kiểm gói chưa xanh.
- Thời gian thực tế: **17:44:00–17:58:55 ngày 15/11/2026 (UTC+07), 0,25 giờ**, theo giờ bắt đầu lead và mốc chốt bàn giao. Phiếu/lệnh giao **không ghi giờ ƯỚC TÍNH riêng MASK-P3**, không lấy 1 giờ của MASK-P cũ làm dự toán P3; 32–46 giờ là dự toán triển khai A sau này.
- **Lệch khỏi phiếu/quyết định tạm:** không sửa mã; không dùng quyết định tạm thay CĐ-36. Chạy thêm SDK 2.0.0 để phân biệt khả năng chạy gói cũ và bộ kiểm liên engine hiện tại; báo cả lỗi, không bỏ test hoặc nhận đủ nghiệm thu chung.

### Cần Core / Chờ Anh — MASK-P3, CĐ-36

- **C-P3-01 — Xem dữ liệu chung:** mở đúng dòng/phiên bản bằng tham chiếu opaque, kiểm quyền và audit mỗi lần; bản rõ chỉ trong cửa Core, không callback/API giải mã/export sang engine/module. Chưa có cửa thì chỉ metadata, không tự xây màn tên gốc.
- **C-P3-02 — Quyền/duyệt:** nguồn tin cậy yêu cầu–module–người–tài liệu–vùng và quan hệ alias, quyền xem tách quyền Admin; biên nhận ID/phiên bản không tên chống replay/thay đổi giữa xem và duyệt; đóng/thu hồi kiểm lại quyền. Không nhận `da_xem=true` tự khai.
- **C-P3-03 — Tìm/chống trùng bí mật:** xác nhận chuẩn hóa/phiên bản, tìm đúng giá trị, duy nhất/lay_hoac_tao/CAS theo bí mật+vùng, lô ≤100, không lộ băm/lỗi; hạn mức chống dò đoán. Có thể xem xét truy vấn nhiều ứng viên chung chỉ trả metadata; không quét/giải mã danh mục cho engine. Thiếu bằng chứng dò đủ thì chặn che/Cloud.
- **C-P3-04 — Hồ sơ/vòng đời:** tách quyền nguồn/map cho che/Local khỏi bước đối chiếu trả lời; không cho đọc gốc để trả hoặc inverse. Chốt chính sách tham chiếu sau đóng/hết hạn và giữ alias đang xử lý, kế thừa stream/trần/413/budget/cách ly upload, CAS/ACK/ChuaRo của C-MB-01…03/C-M2C-01…05.
- **C-P3-05 — Chuyển đổi:** quy trình Core bảo vệ cả khóa/cum/JSON/bản sao cũ và cấp ID mới, đối soát DEMO/số dòng/alias/quyền; không engine xuất bản rõ. Chuyển quy trình @1 cũ sang năng lực nghĩa mới, @1 không báo thành công giả. Không sửa Core/SDK trong P3.
- **Chờ Anh:** Q1…Q4 trong [thiết kế §7](MASK-P3-MO-CHE-SDK-2.2.md#7-bảng-cần-anh-chọn): trải nghiệm A, cửa dừng dò kín, phạm vi tham chiếu, Admin/đóng việc. Không hỏi chọn lại CĐ-36 hoặc mở bất kỳ đường giải mã khác.

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

## MASK-B4 — bàn giao writer ZIP/XML nội bộ, 15/11/2026

- **Chưa đạt nghiệm thu chung.** Mã writer hoàn tất đúng ba runtime `ghi_zip.py`, `va_xml.py`, `zip_an_toan.py`; PR **chờ lead mở**, không commit/push. [Báo cáo theo AGENTS.md §6](BAO-CAO-MASK-B4.md), [lệnh/kết quả thật](KET-QUA-KIEM-MASK-B4.txt), [snapshot SHA nguồn trước](SHA-NGUON-MASK-B4-TRUOC.json). Chép chọn lọc có quyền/symbol/SHA bytes+LF trước–sau trong NGUON; nguồn mẫu/Core/SDK/mẫu Ngan/manifest/handler không đổi.
- Writer nhận reader B1+B2/B3 và script ghim băm, dựng lại reader/map từ bytes, kiểm Unicode/byte không chồng và băm/CRC/size/offset/part. Giữ nguyên local record/payload nén/descriptor part bất biến; central chỉ đổi offset cần thiết. Part sửa cập nhật CRC/size theo đúng flags/method/descriptor; không nén lại part khác hoặc đổi compression để né ratio. Không edit/no-op thì toàn ZIP bằng gốc.
- Patch text/attribute theo byte span sau kiểm lexical/parser, giữ markup/namespace/format ngoài span. UTF-8/UTF-16/entity/NFD/CR/CDATA/ST đúng nghĩa; ST chỉ ô Excel, metadata giữ nghĩa XML thường. Shared patch một lần, so lại đủ vùng và mọi nơi dùng/unused. Tab/br/note không sửa như text; tên sheet cần đổi hoặc property sai kiểu từ chối. Đọc lại toàn container/XML qua B1/readers, không lấy preview thay hậu kiểm. Nợ tên 256 đã chặn trong `_kiem_ten` gốc.
- Trần trước/từng lần cấp phát/ghi/đóng ZIP gồm central+EOCD: 1 MiB output, 2 MiB/part, 8 MiB tổng, ratio 200 và các trần B1/readers. Nội dung dự kiến đếm cả shared lặp, 2 triệu code point/8 MiB UTF-8 và 32767 UTF-16/ô. **Cổng đọc lại B1/B2/B3 còn đếm bảo thủ 500.000 cả text/tail/attribute kỹ thuật**, nên có thể từ chối trước trần ra 2 triệu. Giữ chặn, không monkey-patch/nâng ngưỡng; cần lead tách lát reader chiều ra nếu muốn cam kết phần khuếch đại đó.
- **B4: 270 passed, 27,25 giây, mã 0.** Toàn bộ cuối: **2175 passed, 2 failed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 229,20 giây, mã 1**. Hai lỗi `test_timeout_cung_cli_dung_child_va_ghi_bao_cao_tung_phan` và `test_timeout_cung_giu_dem_doan_ai_da_xong` của MASK-2c-4 vẫn lặp ở deadline 2/5 giây; chưa xác lập nguyên nhân gốc. Không sửa tool/test cũ hoặc nới threshold. Lượt nguyên lệnh yêu cầu có thêm một subtest hiệu năng cũ 5,162 giây vượt 5 giây, đã qua ở lượt cuối; lượt temp trung gian thiếu thư mục cha đã sửa runner và chạy lại.
- CLI SDK chuẩn **0/2 ĐẠT, mã 1** thiếu xác minh phiên/quyền như trước; adapter DEMO **2/2 ĐẠT**, kiểm độc lập và `git diff --check` **mã 0**. AST/UTF-8/whitespace 5/5, SHA đích 3/3 và nguồn 4/4 giữ nguyên; AST B1 ngoài giới hạn tên giữ nguyên, không bytecode trong gói. Đã kiểm bằng Core giả (CoreGia) gói văn bản hiện có; writer tệp kiểm RAM/fixture Office DEMO, chưa Office/Core/Local thật hoặc Linux thực tế, chưa hai lớp trên tệp. Cloud tắt; không công bố năng lực/phát hành trước B7/B9.
- Thời gian thực tế **16:00:00–16:47:24 ngày 15/11/2026 (UTC+07), 0,79 giờ** tại mốc chốt kiểm artifact và hồ sơ cuối; phiếu **4–6 giờ ƯỚC TÍNH**, `kho`. Buffer dọn `finally`, không tệp tạm của engine, cấu hình/sổ/cache bền, bảng ngăn mới, mạng hoặc log tên/nội dung.

## Cần Core / Cần lead — kế thừa MASK-B4, 15/11/2026

- **C-MB-01/02:** Core giữ bytes nguồn/bản đã patch/map/script phiên bản+băm trong snapshot ACL, quyền mở tệp con xuyên bước và mã yêu cầu ổn định; chứng thực đủ Local hai lớp, CAS/chốt/kết quả/ACK và cách ly upload chưa phát hành. B4 chỉ trả bytes nội bộ đã kiểm ZIP/XML, không sinh bằng chứng an toàn/quyền cho caller và không tự gọi AI.
- **C-MB-03:** SDK/Core chặn download/upload 1 MiB đếm bytes thực trước cấp phát, streaming có hủy/lease, ánh xạ 413 đúng và budget RAM/CPU/thời gian/job/concurrency. Kiểm byte trong RAM ở B4 không chứng minh đoạn tải trước engine được bảo vệ. Giữ kế hoạch B10 đo máy đích và Anh tự chạy Office/Local thật.
- **Cần lead:** xử lý hai ca deadline MASK-2c-4 nêu trên trước khi nhận đạt kiểm chung; đánh giá/tách profile reader chiều ra nếu muốn nhận output trên bộ đếm bảo thủ 500.000. Không thêm câu chờ Anh hoặc sửa Core/SDK trong B4.

## MASK-S22 — kiểm nền trước Lead gộp (lịch sử), 15/11/2026

Mục này giữ số kiểm của lần giao trước. Lead đã gộp main trước lần làm hiện tại; trạng thái bàn giao mới ở mục MASK-S22 bên dưới.

- Nhánh `codex/e_mask-mask-s22` hiện ở B4 `b9dc179`; PR: **chờ lead mở**. Theo lệnh giao phải gộp `origin/main` trước khi sửa mã. Lệnh `git merge --no-commit origin/main` chưa thay đổi worktree: bị từ chối tạo `ORIG_HEAD.lock` trong metadata Git nằm ngoài vùng được phép ghi. **Cần lead gộp nền trong worktree này**, không commit/push từ Codex. Chưa triển khai migration hoặc sửa hai test deadline.
- Đã đọc AGENTS.md và tài liệu/mẫu SDK 2.2.0 trực tiếp từ `origin/main` (`12ed8db`) vì nền hiện tại chưa có chúng. Đã tạo `.venv` mới (Python 3.13.14), cài SDK bằng `--no-index --no-deps` từ bản wheel đọc nguyên bytes của cùng commit vào `.venv`; SHA-256 **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** khớp `SHA256SUMS.txt` của commit đó. Sau gộp phải cài/kiểm lại từ đường dẫn phát hành trong repo theo lệnh giao. Phụ thuộc kiểm nền sao offline từ bản đã cài: pytest 9.1.1, packaging 26.3, pluggy 1.6.0, pygments 2.21.0, iniconfig 2.3.0, colorama 0.4.6; chưa là lock phát hành của MASK-S22.
- Phạm vi đã xác định: CĐ-36/MASK-P3 giữ kho bí danh chạy RAM, không khai `ngan_du_lieu`/migration hoặc thêm thư mục SQL. SDK 2.2.0 tạo `viec.ngan` ở mọi việc và đặt lại `app.ngan` lúc chạy; mã Mask hiện chọn chúng thay kho RAM, cần tách cổng kho hiện tại khỏi thuộc tính SDK. Cấu hình engine qua `viec.cau_hinh`; prompt module/quy trình và quyền tin cậy vẫn theo cổng được giao, không lấy quyền từ cấu hình/payload.
- Kiểm nền trước sửa, **đã kiểm bằng Core giả (CoreGia)**: CLI SDK chuẩn **0/2 ĐẠT, mã 1**, giữ từ chối thiếu phiên/quyền; `kiem_doc_lap.py` **ĐẠT, mã 0**. Lệnh `.venv/Scripts/python -m pytest e_mask/tests -q --basetemp=.pytest-tmp` → **432 failed, 1745 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped, 205,48 giây, mã 1**. Đây là số nền trước migration trên SDK 2.2.0 nhưng mã vẫn B4, Hỏi AI chưa có AI-11/AI-12; chưa là nghiệm thu MASK-S22. Không bỏ hoặc sửa test để làm đẹp số nền.

## Cần Core / Cần lead — MASK-S22, 15/11/2026

- **C-S22-01:** SDK 2.2.0 `thu.main()` gọi thẳng `CoreGia().chay_thu_demo(app)`; `chay_thu_demo` chỉ cấp đầu vào/tham số/tệp DEMO, chưa có hook cấp cổng quyền tin cậy của Mask. `dat_cau_hinh` không thay thế xác minh phiên/module/người gửi/mã yêu cầu. Hai ví dụ hiện bị chặn đúng; không thể đạt CLI chuẩn bằng cách bỏ chặn, cờ DEMO trong runtime hoặc tự xác thực từ payload. Cần Core/lead thống nhất cơ chế DEMO tin cậy trước điều kiện CLI 2/2; không sửa wheel/SDK hoặc thêm cổng thay thế để báo đạt.
- **C-S22-02:** CĐ-36 cấm mở đường giải mã trường `bi_mat`; MASK-P3 đang chờ thiết kế lại mở che. Giữ ngoại lệ RAM của lệnh giao MASK-S22; không chuyển kho bí danh vào Core. Màn duyệt hiện dùng `KttCore.engine("e_mask").ngan` vẫn cần cơ chế nối với kho RAM do lead/Core thống nhất; không khai bảng Core giả để che khoảng thiếu này.

## MASK-S22 — chuyển SDK 2.2.0, 15/11/2026

- **Trạng thái: Chưa đạt điều kiện nghiệm thu chung — CLI 0/2 và một subtest hiệu năng vượt 5 giây.** PR: **chờ lead mở**. Không commit/push. Bắt đầu **18:04 ngày 15/11/2026 (UTC+07)** theo lệnh Lead; Kết thúc **18:45:35**, thực tế **0.69 giờ**; số kiểm thật tại [báo cáo MASK-S22](BAO-CAO-MASK-S22.md), [log lệnh](KET-QUA-KIEM-MASK-S22.txt).
- Venv mới `.venv`, bảo toàn venv cũ trong worktree; SDK 2.2.0 cài wheel repo `--no-index --no-deps`, SHA256 khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`. Phụ thuộc chạy ghim SDK 2.2.0; phụ thuộc kiểm offline ghim riêng, không thêm dependency chạy.
- Gói 1.3.0 khai khoảng SDK `>=2.2.0 <3.0.0`, schema cấu hình rỗng và đọc snapshot `viec.cau_hinh`. Hiện Mask không có trường engine bắt buộc; prompt/model Local thuộc module/quy trình qua port Core, không chuyển sai chủ sở hữu. Không có đệm cấu hình cần callback. Bảng cấu hình đã bỏ khỏi kho RAM; bộ đọc cấu hình tạm và bản khai SDK 2.1 chuyển nguyên byte tới `LUU-TRU/sdk_truoc_2_2/`.
- **Ngoại lệ riêng do Lead chốt:** giữ `ngan.py`/cổng kho bí danh RAM trong đường chạy; không chuyển `NganBoNho` nghiệp vụ sang ngăn Core, không khai `ngan_du_lieu`, không thêm thư mục/migration/kiểm kê dữ liệu. `app.kho_bi_danh_ram` tách khỏi `app.ngan` và không chọn `viec.ngan` cho kho bí danh. Mất RAM vẫn phải làm lại như trước. Giữ các thao tác dọn/xóa của cổng RAM hiện tại; không đưa chúng sang API 2.2.0. Không tạo đường giải mã; thiết kế mở che theo CĐ-36 còn thuộc MASK-P3. Màn duyệt giữ KttCore.engine, không có bảng cấu hình để chuyển; chỉ kiểm giả, chưa nối ngăn Core mới.
- Adapter Local ngoài gói đổi từ bảng cấu hình/ngăn AI cũ sang `CoreGia.dat_cau_hinh`/`xem_ngan` 2.2.0; không sửa Hỏi AI AI-11/AI-12. Hai ca deadline MASK-2c-4 tiêm `TimeoutExpired` tại checkpoint, giữ báo cáo từng phần/số đoạn đã xong; không dùng sleep hoặc ngưỡng thời gian máy để phán định. Các test HTTP Local giả/child CLI khác vẫn chạy thực. Không có bằng chứng kill process/model thật từ hai ca tín hiệu này.
- Giữ mọi ca hành vi/an toàn cũ; bỏ hai ca so băm mẫu tạm và phép so mẫu trong ca B3 theo lệnh giao. Thêm bốn ca S22 kiểm schema/cấu hình CoreGia, kho RAM không bị chọn nhầm ngăn SDK, không có bảng cấu hình, và CLI vẫn từ chối thiếu quyền. Test phiên bản đổi sang phiên bản manifest. Hai kiểm nguồn lịch sử dùng bằng chứng HD-9 đã gộp trước lát (`55f0f761fed03460a0039cd791da0684303ede88`), giữ nguyên băm B1/B4 cũ; nguồn engine khác không sửa. SHA LF hiện tại trong NGUON.
- Lượt toàn bộ đầu: **2176 passed, 5 failed (gồm 2 subtest hiệu năng), 4 xfailed, 188 subtests passed, 270,54 giây**. Đã sửa test ghim phiên bản và kiểm nguồn sau main; giữ nguyên ngưỡng hiệu năng 5 giây/timeout 12 giây, chạy riêng lại **1 passed, 3 subtests passed, 13,68 giây**. Lượt 2: **2178 passed, 3 failed (hai subtest hiệu năng và một fixture deadline), 4 xfailed, 188 subtests passed, 548,23 giây**. Đã cố định đồng hồ logic riêng của tool trong fixture deadline (không sửa time của SDK/HTTP); hai ca deadline kiểm lại **2 passed, 48 deselected, 5,32 giây**. Lượt chốt sau sửa: **2179 passed, 1 failed (subtest hiệu năng), 4 xfailed cũ, 189 subtests passed, 0 skipped, 376,45 giây; mã 1**. Cả hai deadline qua trong full suite. Ca hiệu năng `mau='1 '` đo **7,619 giây > 5 giây**; giữ nguyên mã/ngưỡng, chưa kết luận nguyên nhân trong S22. Cần Lead tổ chức kiểm hiệu năng ít tranh chấp tài nguyên hoặc giao lát tối ưu riêng. Không dùng lượt kiểm riêng đạt để nhận full suite xanh. CLI cuối **0/2, mã 1**; kiểm độc lập cuối **ĐẠT, mã 0**; `git diff --check` mã 0.
- Đã kiểm bằng Core giả (CoreGia). Chưa Core/Office/Local thật hoặc Linux thực tế. Chỉ DEMO; Cloud tắt. Không sửa `_chung/**`, bộ SDK, nguồn cũ hay engine khác. Năm tệp Python được sửa (bốn runtime, một công cụ); thêm/chỉnh khai báo manifest/schema và tài liệu/khóa phụ thuộc theo yêu cầu.

## Cần Core — MASK-S22, 15/11/2026

- **C-MS22-01 / CLI DEMO chuẩn:** `CoreGia.chay_thu_demo` chỉ đọc phong bì/tham số và `tep_demo`; CLI tạo CoreGia mới, không có cửa cấp quyền/mã yêu cầu Mask tin cậy. `dat_cau_hinh` chỉ dùng được qua Python, CLI không đọc cấu hình DEMO từng ví dụ; mặc định schema đủ cho Mask hiện tại nhưng không cấp được quyền. Hai ví dụ chuẩn cùng bị `MASK_NGU_CANH_CHUA_XAC_MINH`, **0/2 ĐẠT, mã 1**. Cần Core/SDK cung cấp cơ chế fixture tin cậy cho DEMO chung hoặc Lead chốt tiêu chí tương ứng. Không tự suy quyền từ cấu hình/payload, không đổi hai ví dụ thành no-op hoặc bỏ chúng, không dùng runner có quyền thay tiêu chí CLI.
- **C-MS22-02 / CĐ-36 và MASK-P3:** SDK 2.2.0 có ngăn/cấu hình thật nhưng trường bí mật đọc null; không mở đường giải mã. Kho bí danh RAM chỉ giữ tạm theo lệnh riêng Lead. Mở che/duyệt/dò danh mục và cổng quyền/snapshot tin cậy cần thiết kế P3 cùng cửa Core trước khi chuyển dữ liệu; S22 không coi đây là nợ giải mã cần bổ sung. Không vận hành màn duyệt cũ trên ngăn Core mới khi chưa thiết kế lại.
- Kế thừa các cửa C-M2C/C-MB còn mở ở trên; S22 không chứng minh ACL/lease/provenance/tokenizer/stream thật. Không có câu chờ Anh mới ngoài thiết kế P3 đã tồn tại. Ước tính riêng MASK-S22 chưa có trong phiếu/CHUYEN-SDK-2.2 §4, không tự đặt số để so sánh.
## MASK-R5 — tiếp lát, 15/11/2026 lúc 23:50

**Trạng thái: Đạt điều kiện tiếp lát MASK-R5 (full pytest/độc lập/kiểm kê); chưa đạt nghiệm thu chung do CLI DEMO thiếu quyền Core.** PR: **chờ lead mở**. Tiếp đúng nhánh `codex/e_mask-mask-r5`, main đã có R7/DC-13; không merge/commit/push. Bắt đầu **15/11/2026 23:50 (UTC+07)** theo lead; phiếu **6–8 giờ ƯỚC TÍNH**, độ khó kho. Bảng phân loại đủ từng node ID ở [BAO-CAO-MASK-R5.md](BAO-CAO-MASK-R5.md), dữ liệu máy đọc ở [PHAN-LOAI-MASK-R5.json](PHAN-LOAI-MASK-R5.json).

- Đủ **216 ca: 207 (a), 9 (b)**. Ca an toàn chuyển fixture sang `KhoAnhXaRAM` R4 + ngăn SDK 2.2.0, giữ mục tiêu/span/Unicode/tiền-ngày/nguồn/đủ đoạn/retry/Cloud tắt. Ca chỉ khẳng định lưu snapshot chuyển sang không ghi ngăn/tệp/Core và mất RAM phải lỗi rõ; không thêm skip/xfail hoặc bỏ ca. Bốn xfailed lịch sử MASK-2b giữ nguyên.
- Ba fixture snapshot cũ cùng bản công cụ trước chuyển được giữ nguyên ở `e_mask/LUU-TRU/mask_2c_snapshot_core/`; không còn import snapshot fixture trong bộ hiện hành. Công cụ/fixture hiện hành dùng chính kho R4 của app, không tạo kho thứ hai qua payload, không đổi SDK/Core/AI-9 để giả kết nối runtime đã có.
- **Theo chỉ dẫn tiếp lát của Anh**, giữ hình dạng `chuyen_tiep.mask_2c.ho_so`/`bam_ho_so` để tương thích AI-9 đang có. `ho_so` chỉ metadata `ram-<mã opaque>`, tên/MIME cố định và độ dài trong RAM; không có tệp tương ứng, không được dùng để tải lại. Validator chỉ nhận metadata RAM đúng allowlist; hậu kiểm đối chiếu toàn bộ metadata/băm với RAM. AI-9 nguyên bản vẫn kiểm model/nguồn/HTTP/profile; không sửa `e_hoi_ai`. Đây là lớp tương thích tạm, không phục hồi thiết kế snapshot.
- Gốc/map/bản quy tắc/kế hoạch/phiên bản/budget/Local response vẫn chỉ RAM R4. Các port chỉ chuyển đoạn Local cần thiết và tập phản hồi không có yêu cầu/gốc/map; nguồn và băm được kiểm độc lập. Alias đã duyệt lấy qua ngăn SDK thật null+cờ; catalogue fixture độc lập gold/Local, tên mới thiếu C-P4-03 vẫn bị chặn. Sau chốt/mất RAM/terminal/TTL không cache hoặc khôi phục bản rõ; ChuaRo khi chờ chỉ giữ trong hạn tuyệt đối.
- Sửa riêng nhánh thiếu tài nguyên trong chuẩn bị để trả đúng `MASK_THIEU_TAI_NGUYEN`, giữ fail-closed và thông báo an toàn. Chỉ ba runtime R5 + một công cụ ngoài gói, cùng kiểm kê tự sinh, test/tài liệu; không vượt năm tệp mã/khai báo. Không thay API/schema/contract chung/manifest/SQL/dependency, không sửa Core/nguồn cũ.
- Lượt nền trong worktree mới: **2304 passed, 217 failed, 4 xfailed, 190 subtests passed, 157,05 giây**. 216 lỗi MASK-2c-1/2/3/4 = **18/39/133/26** và một lỗi kiểm kê sau gộp main. **Kết quả chốt: 2523 passed, 0 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 378,34 giây, mã 0.** Collection đủ 216/216 ca cũ; thêm hai ca chặn xung đột nhóm, marker skip/xfail giữ nguyên. CLI SDK **0/2 ĐẠT, mã 1**, thiếu quyền Core; kiểm độc lập và diff **mã 0**; kiểm kê **52/52 bytes LF/SHA**. Thực tế lượt tiếp **23:50:00 ngày 15/11/2026 → 00:32:52 ngày 16/11/2026 (UTC+07), 0,71 giờ**, so với **6–8 giờ ƯỚC TÍNH**. Log thật: [KET-QUA-KIEM-MASK-R5-TIEP.txt](KET-QUA-KIEM-MASK-R5-TIEP.txt); không lấy focused thay full. **Đã kiểm bằng Core giả (CoreGia)**; chưa Core/Local/Office/Linux thật, Cloud tắt.

### Cần Core / Cần phối hợp — MASK-R5

- **Cần phối hợp AI-9: bỏ yêu cầu snapshot Core** — lead giao **AI-13**. Khi consumer hỗ trợ metadata RAM riêng thì bỏ trường hình dạng tệp tương thích; không tạo/giữ snapshot thật trong thời gian chờ.
- **C-P4-01/02/04 còn mở:** mã/scope/ACL và nguồn Local tin cậy xuyên bước, ghim cùng instance RAM, điều phối đủ đoạn, thông báo hủy/lỗi/kết thúc khi Mask rảnh và đồng bộ ACK/lease/deadline. Các port Python vẫn chỉ adapter đề nghị, chưa là API SDK/Core có thật. `chay.py` chưa truyền đúng kho R4 vào hai handler, thuộc **R6**; không tự coi fixture là runtime đã nối.
- **C-P4-03/05 kế thừa:** tên mới/duy nhất/budget/đếm/CAS ở Core; log/crash dump, cách ly bàn giao và giới hạn RAM/RPC/tệp cần chứng minh trên Core/Local thật. Không dùng kho lịch sử/map dự phòng để vượt chặn. Không phát sinh câu nghiệp vụ chờ Anh.
- **C-MS22-01 còn mở:** CLI DEMO chuẩn thiếu cửa cấp quyền/mã tin cậy, không bỏ gate hoặc đổi ví dụ để báo đạt. Kết quả CLI thật vẫn phải báo riêng với full pytest.

## MASK-R7 — Admin metadata và duyệt cùng ID, 15/11/2026

- **Xong phần adapter/UI giả, chờ Core; chưa đạt nghiệm thu chung.** PR: **chờ lead mở**. Chỉ hai runtime đúng MASK-P4 §4: `e_mask/duyet_dinh_danh.py`, `ui/duyet_dinh_danh.js`. Kèm test/tài liệu và kiểm kê bytes LF tự sinh theo lệnh lead; không commit/push hoặc sửa Core/SDK/dependency. Bắt đầu **22:17 ngày 15/11/2026 (UTC+07)** theo lead; giờ kết thúc và kết quả cuối ở báo cáo R7 khi chốt kiểm.
- Runtime chỉ nhận `viec.ngan` SDK qua adapter R2; danh sách chiếu ID/alias/nhóm/trạng thái/số gặp, giữ row_version để CAS, phân trang 100 hàng. Không lọc tên, không nhận bản rõ hay dùng null/cờ để tự chứng thực đã xem. Duyệt và từ chối phải có vé opaque do cửa Core xác minh; kiểm cả quyền xem/duyệt, phiên/vùng/ID/phiên bản, giữ quyền trong lô CAS, không duyệt mù. Lỗi cố định không chứa dữ liệu nguồn; mất ACK hoặc lỗi cửa sau Core đã ghi trả ChuaRo, không gửi lại ngầm.
- Duyệt đổi trạng thái trên cùng `id_dinh_danh`, chỉ thêm alias metadata qua primitive R2. Junsky không trùng tiền tố MASK; alias duy nhất không phân biệt hoa/thường trong cùng vùng DEMO/THAT, lô alias+trạng thái rollback nguyên tử khi trùng/CAS. Từ chối đổi sang TU_CHOI; không xóa, không chép tên hay ghi null/cờ đè cột bí mật. Chuỗi RAM R4 đang chờ AI giữ map/alias đã ghim dù Admin vừa duyệt.
- UI dùng `KttCore.engine("e_mask")`, chỉ đọc metadata từ ngăn và gửi tham chiếu/phiên bản/vé/alias/quyết định qua cửa thao tác chung. Không `.ghi_lo`, API giải mã, callback/export tên, lọc tên một phần, mạng ngoài/eval/HTML chưa lọc/storage/log. Biên nhận và xác nhận kết quả phải đúng khuôn không tên; tải lại/đổi phiên/lỗi/mất ACK vô hiệu vé; chống double click và replay ở UI không thay xác minh Core.
- Logic RAM Admin MASK-6 được chuyển nguyên hành vi sang `tests/ho_tro_duyet_lich_su.py` ngoài gói. Sáu test/công cụ DEMO cũ chỉ đổi import fixture (AST đã đối chiếu 6/6), mọi assertion an toàn cũ giữ nguyên; các ca này là hồi quy lịch sử, **không phải bằng chứng runtime R7**. Bộ R7 mới kiểm runtime SDK/null+cờ thật. `cong-cu/chuyen_danh_muc_demo.py` ngoài closure còn gọi API RAM cũ đã bỏ; không dùng công cụ này trước khi lead giao chuyển riêng. Migration dữ liệu cũ chỉ Core/lead thực hiện, engine không đọc tên để chuyển.
- Môi trường `.venv` Python 3.13.14 tạo với `--system-site-packages`, SDK 2.2.0 cài offline wheel repo `--no-index --no-deps`, SHA-256 khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`. Có jsonschema 4.26.0 và pytest 9.1.1; không đổi lock/dependency. Các kiểm dùng `-B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.
- Đã kiểm bằng Core giả (CoreGia) và KttCore giả; chưa UI/Core/Local/Office/Linux thật. Không đăng ký năng lực hay lệnh Admin vào manifest vì ngoài closure; không tuyên bố luồng quản trị đã nối Core. Kết quả thật ở [báo cáo §6](BAO-CAO-MASK-R7.md) và [lệnh kiểm](KET-QUA-KIEM-MASK-R7.txt).

### Cần Core — MASK-R7 / C-P4-06

- **C-P4-06 còn mở:** Core cung cấp cửa Xem dữ liệu chung theo ID/phiên bản, bản rõ chỉ ở màn Core đúng quyền; chỉ trả biên nhận opaque + ID/row_version, không tên/callback/export sang UI engine. Biên nhận gắn phiên/người/vùng/ID/phiên bản, giới hạn thời hạn, chống replay; kiểm độc lập quyền xem và duyệt, giữ quyền/thu hồi đồng bộ với CAS và kết quả/ACK. Kiểm bằng CoreGia không chứng minh ACL/thu hồi/audit thật.
- `quyen.bien_nhan_duyet(...)` là **giao thức port nội bộ đề nghị**, context manager chỉ yield ID+row_version và không nuốt ngoại lệ. Adapter test nằm ngoài gói. UI dùng hai mã thao tác chung đề nghị `xem_du_lieu`/`quyet_dinh_duyet` qua `engine.thao_tac`; **SDK 2.2.0 chưa có bảo đảm/đăng ký các lệnh này**, Core/lead cần chốt binding chung và điều phối handler R7, không thêm route giải mã hay route riêng Mask. Lệnh xem phải mở màn do Core sở hữu, không giao bản rõ cho engine; lệnh quyết định nối port quyền R7. Có ngăn mà thiếu cửa/vé thì vẫn giữ chờ, không fallback ghi trực tiếp hoặc cờ tự khai.
- Migration kho cũ bảo vệ khóa/JSON/bản sao và bí mật do Core/lead làm; engine không đọc-sao tên sang bảng khác. Kế thừa C-P4-03 về duy nhất/CAS/anti-replay và hạn mức; không suy rằng chứng minh CAS/unique metadata ở CoreGia đã đóng các thiếu hụt chỉ mục bí mật của R2. Giữ **C-MS22-01**: CLI DEMO chuẩn vẫn thiếu cửa quyền tin cậy (0/2), không bỏ chặn để làm xanh.
- Không phát sinh câu Chờ Anh chọn lại nghiệp vụ. Công cụ chuyển danh mục RAM lịch sử cần lead tách lát nếu còn nhu cầu DEMO; không nới closure hai runtime R7.

### MASK-R7 — kết quả chốt

- **2412 passed, 4 xfailed cũ, 190 subtests passed, 0 failed/skip**, 241,42 giây, mã 0. Bộ R7/UI riêng 50 passed (49 Python + wrapper Node 26/26); không bỏ/đổi test an toàn cũ hoặc nới ngưỡng. CLI **0/2, mã 1** vẫn thiếu quyền Core; độc lập và `git diff --check` **mã 0**; kiểm kê **52/52 bytes LF**. Đã kiểm bằng Core giả (CoreGia), chưa UI Core thật; chưa đạt nghiệm thu chung.
- Full đầu 1 failed/2403 passed do fixture R3 checkout CRLF; khôi phục LF khớp nguyên blob Git và gold, không đổi dữ liệu/hash/assertion. Lead giữ LF fixture khi checkout vì tệp nằm ngoài gói đã ghim LF. Tám test R7 cuối được thêm sau lượt thu thập đầu và đều có trong full chốt.
- Thực tế **22:17:00–22:37:37 ngày 15/11/2026 (UTC+07), 0.34 giờ**; **3–5 giờ ƯỚC TÍNH**, `vua`. PR: **chờ lead mở**. [Báo cáo §6](BAO-CAO-MASK-R7.md); [lệnh/kết quả](KET-QUA-KIEM-MASK-R7.txt). C-P4-06/C-MS22-01 còn mở; không commit/push/Core/SDK/dependency.

## MASK-R6 — mở che văn bản/AI một lần từ RAM, 16/11/2026

**Trạng thái: xong phần mã/kiểm R6, chờ Core và lead cập nhật kiểm kê; chưa đạt nghiệm thu chung.** PR: **chờ lead mở**. Bắt đầu **00:52 ngày 16/11/2026 (UTC+07)** theo lead; phiếu **4–6 giờ ƯỚC TÍNH**, độ khó `kho`. [Báo cáo §6](BAO-CAO-MASK-R6.md), [full pytest](KET-QUA-KIEM-MASK-R6-PYTEST.txt).

- Đúng bốn runtime bảng MASK-P4 §4: `mo_che_ram.py`, `che_van_ban.py`, `chay.py`, `phong_bi.py`. Giữ `nhan/tra` và bộ M; không sửa Core/SDK/dependency/manifest/schema chung, không commit/push. Nối hai handler R5 vào đúng kho R4 của app; không tạo kho lịch sử dự phòng. Bước che quy tắc riêng vẫn chặn chất lượng R3; chuỗi Local dùng R5.
- Chỉ mở alias thực sự đã thay trong bản cuối `DA_HAU_KIEM`, đúng mã/quyền/scope/instance/phiên RAM. Giữ nguyên NFD/Cf/khoảng trắng gốc, nội dung AI thêm, khóa và kiểu tiền/ngày/số/boolean/null. Alias lạ/hỏng/thiếu/mơ hồ hoặc mất RAM trả lỗi Việt, không phần kết quả đã mở. Không tra ngược ngăn, tải nguồn/snapshot hoặc đổi sang kết quả chỉ alias/tham chiếu.
- Mở `tra_loi`, chuỗi lồng `du_lieu`, câu trích và dẫn chứng lồng. Thay chữ thì hạ kiểm nguyên văn/trích dẫn, tái tính trên map/gốc đang RAM; không xác định duy nhất thì offset null + cần kiểm lại. `dong_viec=false` vẫn trả `DA_DONG` và dọn map; có thông báo chuyển quy trình qua tiến độ/cảnh báo AI. Trần thử nghiệm sau mở 500.000 ký tự, vượt từ chối trước ghép, không cắt ngầm.
- R4 tiêu thụ/dọn một lần sau thành công/lỗi/hủy/ChuaRo. Ngắt vòng tham chiếu hàm duyệt và frame ngoại lệ của bàn giao, dọn map phụ trong `finally`; kiểm weakref cả khi tắt GC. Không có cache bản rõ để mở lại. Core bàn giao cuối phải giữ quyền/deadline và cách ly kết quả tới sau tiêu thụ, không Cloud. Thiếu binding thật tiếp tục fail-closed; protocol Python đề nghị chỉ kiểm bằng adapter ngoài gói.
- Mười test/công cụ lịch sử chỉ đổi import/điểm gọi mở: AST đối chiếu 10/10 giữ nguyên thân hàm/assertion/marker. Vỏ/mở tra ngược cũ giữ ở hai fixture ngoài gói, không là bằng chứng R6. Fixture R5 chỉ seed catalogue, chạy handler hiện hành thật. Ca âm snapshot tiếp tục chặn port chỉ có luu/doc. Không thêm skip/xfail, không nới ngưỡng; bốn xfailed MASK-2b cũ giữ nguyên.
- Lượt full đầu **2582 passed, 59 failed, 4 xfailed, 190 subtests passed; 390,94 giây**: 57 điểm gọi mở lịch sử, một gold R3 CRLF và một kiểm kê. Đã sửa điểm gọi/fixture; gold khôi phục nguyên blob Git LF với SHA cũ, không đổi dữ liệu/hash/assertion. Lượt full trước sửa vòng tham chiếu GC **2642 passed, 1 failed kiểm kê, 4 xfailed, 190 subtests passed; 377,00 giây**, không lấy lượt này thay full chốt sau sửa cuối.
- **Đã kiểm bằng Core giả (CoreGia)**; chưa Core/Local/Office/Linux thật. Chỉ dữ liệu DEMO, không Cloud. Kết quả full chốt, ba lệnh/diff và thời gian thực tế được ghi ở mục kết quả chốt bên dưới và báo cáo R6.

### Cần Core / Cần lead — MASK-R6, C-P4-02/05

- **C-P4-02 còn mở:** binding chung cho quyền/R4 và `CongMoCheRAM.ban_giao_cuoi` (protocol đề nghị, chưa phải API SDK). Core giữ scope/instance/lease/deadline/đầu vào bất biến, cách ly kết quả tới sau chốt tiêu thụ RAM, không nuốt ngoại lệ. Hủy/lỗi/quá hạn bỏ bàn giao chờ; sự kiện toàn chuỗi tới Mask khi rảnh hoặc trước SDK gọi handler. Mất ACK sau nhận dùng ChuaRo, Core giao lại kết quả đã tiếp nhận đúng quyền; không gọi mở lại/tạo map hoặc chuyển worker để cứu dữ liệu.
- **C-P4-05 còn mở:** ACL đầu vào JSON và bàn giao cuối đúng người/module, không Cloud; budget bytes/413/RAM/CPU/thời gian thật, cách ly kết quả chưa phát hành, đồng bộ tín hiệu hủy với ACK. Không dump payload/traceback/local variables hoặc map/bản rõ vào ngăn/tệp/log/stderr/crash dump. Không dùng đầu vào nguồn/snapshot làm đường phục hồi. CoreGia chưa chứng minh ACL/budget/độ bền Core thật hoặc mọi tình huống SDK mất ACK sau handler.
- **Cần lead áp kiểm kê sau gộp:** giữ nguyên `sql/kiem_ke.json` vì ngoài closure bốn runtime. [Kiểm kê đề nghị](KIEM-KE-MASK-R6-DE-NGHI.json) bao **53 tệp** thực tế; bản sao chỉ thay kiểm kê qua kiểm độc lập, không thay kết quả gói gốc. Không sửa bộ kiểm hoặc giấu failure này để báo đạt.
- Kế thừa C-P4-01/03/04, C-MS22-01 (CLI thiếu quyền) và phối hợp AI-13 về metadata RAM của AI-9. Không có câu nghiệp vụ mới chờ Anh chọn lại.

### MASK-R6 — kết quả chốt, 16/11/2026

- `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask`: **0/2 ĐẠT, mã 1**, hai ví dụ thiếu quyền tin cậy (`MASK_NGU_CANH_CHUA_XAC_MINH`). Không đổi ví dụ hoặc bỏ cửa quyền để báo đạt.
- `.venv/Scripts/python -B -m pytest e_mask/tests -q`: **2646 passed, 1 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 390,44 giây; mã 1**. Failure duy nhất `test_kiem_ke_day_du_bytes_va_sha_tung_tep`: kiểm kê gói chưa đổi do ngoài closure. Không bỏ/deselect failure hoặc nới bộ kiểm.
- `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py`: **mã 1**, duy nhất kiểm kê chưa khớp. Đề nghị **53/53** tệp đúng bytes/SHA sau sửa cuối; bản sao chỉ thay kiểm kê qua chính bộ kiểm **ĐẠT, mã 0**. Gói gốc vẫn báo chưa đạt. `git diff --check`: **mã 0**.
- R6 riêng sau sửa cuối **124 passed, 2,19 giây, mã 0**, gồm bốn ca weakref/GC tắt sau thành công/lỗi/hủy/ChuaRo. Kiểm CoreGia bổ sung alias tạm/Junsky case-space mềm **2/2 ĐẠT**. AST mười test/công cụ lịch sử **10/10** không đổi thân hàm/assertion; không thêm skip/xfail hoặc đổi bốn xfailed cũ “giới hạn quy tắc, nợ CAO”.
- Thực tế **00:52:00–01:41:32 ngày 16/11/2026 (UTC+07), 0,83 giờ**, tại mốc chốt kiểm/báo cáo, so với **4–6 giờ ƯỚC TÍNH**. [Lệnh/kết quả thật](KET-QUA-KIEM-MASK-R6.txt), [báo cáo §6](BAO-CAO-MASK-R6.md). Đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật; Cloud tắt. Không commit/push; PR: **chờ lead mở**.

## MASK-B5 — Word chỉ RAM, 16/11/2026

**Kết luận: Xong mã/kiểm nội bộ B5; chưa đạt nghiệm thu chung vì CLI thiếu quyền và chuỗi tệp hai lớp/SDK thuộc B7/B9.** PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia); chưa Core/Office/Local/Linux thật, Cloud tắt. Không commit/push. [Báo cáo §6](BAO-CAO-MASK-B5.md), [SDK/độc lập/diff](KET-QUA-KIEM-MASK-B5.txt), [pytest cuối](KET-QUA-KIEM-MASK-B5-PYTEST.txt).

Chỉ thêm một runtime `goi/e_mask/e_mask/tep_word.py` trong bốn tệp được giao; không sửa các runtime B1/B2/B4/R2…R6, Core/SDK/nguồn cũ hoặc dependency. Che mọi vùng Word/metadata/attribute trong whitelist, tên tách run cùng vùng; không ghép ô/story. Chữ ẩn/bảng/ô gộp/đầu-chân/notes đều được đọc. Part/comment/revision/field/textbox/attribute chưa hiểu chặn toàn tệp. Patch khoảng byte có băm, reader lại bytes và đối chiếu từng vùng, giữ format/markup/bảng và record nén phần bất biến. NFD/Cf/tiền/ngày theo map/quy tắc; số/ngày custom giữ kiểu.

Gốc/map/bytes/patch/cache chỉ trong handle R4 đúng scope/instance; B5 chỉ trả băm/số đếm, luôn `CHO_LOCAL`, tập vùng đã kiểm Local rỗng. Primitive che bổ sung nhận vị trí gốc RAM, không chứng thực hai lớp. Kho SDK tìm chính xác từng ứng viên/null+cờ, không đọc danh mục/bản rõ; budget dùng chung mọi vùng. Alias nhiều nguyên văn, tên mới thiếu C-P4-03, lỗi/hủy/TTL đều chặn. TTL mặc định 600 giây, nguyên 60–900, không gia hạn khi retry. Ghi trạng thái khóa cùng timer/hủy R4, không dựng lại map sau dọn; không gọi port dưới khóa. Spy không ghi ngăn/tệp tạm/hồ sơ Core/upload/log/stderr/chuyển tiếp map.

Provenance/symbol/quyền/SHA bytes và LF trước/sau tại NGUON và [13 nguồn trước](SHA-NGUON-MASK-B5-TRUOC.json); 13/13 nguồn không đổi bytes, runtime mới trước chưa tồn tại. CHANGELOG và kiểm kê đóng gói 54 tệp đã cập nhật, không đổi manifest/schema/mã migration. Gold R3 chỉ trả CRLF về đúng bytes LF có SHA đã ghim; không đổi gold/test/ngưỡng hoặc thêm skip/xfail. Checkout Windows khác có thể phải giữ LF lại. Reader đọc lại vẫn bảo thủ 500.000 ký tự trước trần ra 2 triệu; không tự nới profile. B5 đối chiếu báo trùng số nằm trọn ngày ISO đã được MASK-2b nhận diện, vẫn kiểm đủ/map/span/số/tiền/ngày và chặn cảnh báo ngoài ngày.

Kiểm riêng B5 cuối **91 passed, 6,35 giây, mã 0**, gồm bốn ca TTL/hủy giữa checkpoint và ghi RAM. B2+B4+B5 trước khóa RAM cuối **512 passed, 31,48 giây, mã 0**. Lượt toàn bộ đầu (khởi chạy trong giai đoạn thêm tệp, không phải baseline bất biến): **2645 passed, 2 failed kiểm kê/gold CRLF, 4 xfailed cũ, 190 subtests; 398,46 giây**. Lượt sau kiểm kê/bytes gold, trước bốn ca đua RAM: **2734 passed, 4 xfailed cũ, 190 subtests; 389,21 giây, mã 0**, [log giữ lại](KET-QUA-KIEM-MASK-B5-PYTEST-TRUOC-DON-RAM.txt).

**Kết quả cuối:** pytest **2738 passed, 4 xfailed strict cũ “giới hạn quy tắc, nợ CAO”, 190 subtests passed, 0 failed, 0 skipped; 401,23 giây, mã 0**. CLI SDK **0/2 ĐẠT, mã 1**, thiếu xác minh phiên/quyền; kiểm độc lập **ĐẠT, mã 0**; `git diff --check` **mã 0** (còn cảnh báo checkout CRLF gold R3). Kiểm kê **54/54**, nguồn bytes/LF **13/13**, không bytecode. **Thời gian thực tế 02:00:00–02:46:36 ngày 16/11/2026 (UTC+07), 0,78 giờ**, so với **6–10 giờ ƯỚC TÍNH**, `kho`. PR **chờ lead mở**, không commit/push.

### Cần Core — MASK-B5

- **C-P4-01:** Core cấp/ghim mã yêu cầu, scope và cùng tiến trình/instance xuyên bước; không spawn/failover để cứu map. Handle/adapter CoreGia chưa chứng minh cửa thật.
- **C-P4-02:** sự kiện vòng đời khi rảnh, deadline/lease và tiêu thụ/bàn giao/ACK nguyên tử. B5 chưa upload/mở tệp; Core không gọi mở lại sau tiêu thụ.
- **C-P4-03:** duy nhất bí mật theo vùng/phiên bản, CAS/lô/tạo tên/chống lặp, quota chống dò đoán và không log truy vấn. Không giải mã danh mục; R3 chưa chứng minh chất lượng/chi phí, tên mới giữ chặn.
- **C-P4-04:** B7/AI-9/Core phải điều phối đủ đoạn, nguồn Local tin cậy và mọi vùng tệp; không hồ sơ map/gốc phục hồi. Nhãn `local` hoặc reader/primitive không chứng nhận hai lớp; B9 mới nối cửa phát hành.
- **C-P4-05:** quyền nguồn tệp/bàn giao đúng người-module, streaming/trần trước cấp phát SDK, 413, budget RAM/CPU/thời gian chuỗi, cách ly upload/mất ACK, không dump payload/map/log/crash. Office/Local thật và bộ biên B10 chưa kiểm. Không có câu nghiệp vụ mới chờ Anh chọn lại.

## MASK-R6b — sửa điểm VỪA/NHẸ rà bảo mật R6, 16/11/2026

**Trạng thái: đã sửa và kiểm đủ phạm vi được giao; chưa đạt do một kỳ vọng test R6 cũ trái yêu cầu mới, cần cho phép cập nhật test ngoài phạm vi.** PR: **chờ lead mở**. Bắt đầu **01:59 ngày 16/11/2026 (UTC+07)** theo lead; **2–3 giờ ƯỚC TÍNH**, độ khó vừa. Chỉ bốn runtime được giao, test R6b mới, VIEC/CHANGELOG/NGUON và kiểm kê; không commit/push, không sửa Core/e_hoi_ai/API v1/dependency.

- Dò alias/mảnh alias bằng automaton trie/failure-link chung, dựng một lần/lượt mở; giữ nhận diện case/space mềm, một ký tự lạ thay/chen và chặn nối qua vùng đã xét. Cây tiền tố chỉ được thử cạnh dãy ngoặc trong cửa sổ hữu hạn. Kiểm hạn/hủy mỗi **2.048 ký tự**, từng alias và các vòng duyệt; không cache bảng dò qua chuỗi. Đối chiếu **505 ca** với hàm trước sửa: **0 khác kết quả**.
- Trần kỹ thuật thử nghiệm **1.000 alias/map**, **10.000 chuỗi trong nội dung mở, kể cả khóa dict/câu trích**, thêm **200.000 nút bảng dò** để chặn phình RAM khi alias dài/phân tán. Trần nút là giới hạn triển khai bổ sung, không quyết định nghiệp vụ. Vượt trần trả **MASK_QUA_GIOI_HAN**, không cắt ngầm, map được dọn qua R4. Giữ trần tổng **500.000 ký tự**, tính cả khóa ở đầu vào; đếm chuỗi theo lượt xuất hiện, kể cả chuỗi rỗng.
- Hồ sơ có sẵn **anh_xa_cuoi.da_che**, đúng bản cuối R5 tạo phong bì và bàn giao trước khi đánh dấu **DA_HAU_KIEM**. Lấy tập alias xuất hiện trong chính bản này và giới hạn map mở vào tập đó; không đọc ngăn/snapshot hoặc thêm nơi lưu trữ. Bất biến phép thay đã chặn alias dư từ R6; kiểm tập xuất hiện là lớp chặn độc lập, có ca mô phỏng map cấp alias dư nhưng chưa giao. Không tuyên bố đây là bằng chứng ACK/binding Core thật.
- Khóa dict giữ nguyên theo contract; có alias hoặc mảnh alias thì **mo_day_du=False**, không báo đã mở đầy đủ. Giá trị/trích dẫn vẫn mở theo quy tắc R6. Chụp alias map dưới khóa timer, dùng bản sao riêng và kiểm lại vòng đời trước kết luận lỗi; timer dọn giữa kiểm map trả **MASK_ANH_XA_KHONG_CON**. Không dời/bỏ timer hoặc kéo dài TTL.
- Bỏ tham chiếu biến **ket/raw/chu/ai**, các mảnh bản rõ và kết quả cục bộ trong **finally** trước ngoại lệ đi ra; giữ lỗi Việt/hủy/ChuaRo và hành vi thành công. Test giữ ngoại lệ để kiểm frame handler và raw JSON, cùng kiểm weakref/GC cũ; không tuyên bố ghi đè vật lý mọi bản sao Python/port Core.
- Bộ mới **63 passed**, gồm 1.000 alias × 500.000 ký tự, tiền tố chung/phân biệt, trần alias/chuỗi/nút, alias bịa, khóa lồng, timer chạy luồng khác, hết hạn giữa chuỗi lớn và frame lỗi. Số đo trên mã cuối: dò chung **0,388130 giây** (cùng tiền tố), **0,689834 giây** (1.000 tiền tố phân biệt); handler CoreGia **0,630239 giây**, đều dưới **2 giây**; lệnh ba benchmark **3 passed in 2,51s**, mã **0**. Tính cả dựng bộ dò; phép đo handler không tính dựng fixture/giao việc. Số đo phụ thuộc máy và tải lúc chạy.
- Kiểm kê đã bao đủ **53 tệp** theo **bytes LF thực tế/SHA-256**, trừ chính kiểm kê; gỡ nợ kiểm kê R6. Fixture gold R3 được đưa về LF khớp nguyên SHA đã khóa **b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181**; không đổi nội dung/gold/assertion. `.venv` Python 3.13.14 dùng thư viện hệ thống có sẵn, SDK **2.2.0** cài offline wheel repo, SHA khớp; không thêm dependency. Các lệnh dùng **-B**, **PYTHONUTF8=1**, **PYTHONDONTWRITEBYTECODE=1**.
- **Đã kiểm bằng Core giả (CoreGia)**; chưa Core/Local/Office/Linux thật, Cloud tắt. Full pytest và giờ kết thúc ở kết quả chốt bên dưới; không dùng focused thay full.

### Cần Core / Cần lead — MASK-R6b

- **Cần Core — kết quả trả hai đường:** hiện kết quả mở che đi qua cả **CongMoCheRAM.ban_giao_cuoi** và **return handler/SDK**. Core cần chốt quyền, cách ly và ngữ nghĩa phát hành/ACK giữa hai đường, tránh bàn giao lặp hoặc lộ bản rõ ở kết quả/traceback/log SDK. R6b chỉ ghi nhận, không sửa Core hoặc thêm đường bàn giao.
- Kế thừa **C-P4-02/05** về binding quyền/lease/deadline, bàn giao sau tiêu thụ và cấm dump bản rõ; **C-MS22-01** vẫn mở: CLI DEMO chuẩn thiếu quyền Core, không đổi ví dụ/bỏ gate để báo đạt. Các điểm Core khác của R6 giữ nguyên.
- **Xung đột phạm vi test:** test R6 cũ **test_du_truong_ai_giu_khoa_kieu_noi_dung_moi_va_tinh_lai_trich** buộc giữ khóa alias và **mo_day_du=True** (dòng 46), trái mục 3 của phiếu R6b. Phạm vi chỉ cho thêm **test_mask_r6b.py**, nên chưa sửa test cũ/không thêm xfail hoặc bỏ test; đã đề nghị Anh cho cập nhật tối thiểu kỳ vọng thành **False**. Focused R6+R6b hiện **186 passed, 1 failed** đúng kỳ vọng cũ này. Không phát sinh câu chọn nghiệp vụ.

### MASK-R6b — báo cáo chốt theo AGENTS §6

**Kết luận: Chưa đạt — năm điểm R6b đã sửa, full suite còn đúng một test cũ có kỳ vọng trái yêu cầu về khóa dict; chưa được phép sửa tệp test đó.** Không bỏ test, thêm skip/xfail hoặc nới kiểm tra để làm xanh. Nợ quyền CLI Core còn nguyên.

**Đã làm:** bốn runtime đúng danh sách; automaton dò chung và trần tài nguyên, chỉ mở alias đã xuất hiện trong bản cuối đã giao, dò khóa dict/hạ cờ đầy đủ, chụp map dưới khóa timer và ưu tiên mã mất RAM, dọn biến bản rõ trong finally. Thêm **63 ca R6b**, cập nhật CHANGELOG/NGUON và kiểm kê **53/53** bytes LF/SHA-256. Đã kiểm bằng Core giả (CoreGia).

**Kết quả kiểm thật trên gói trong worktree:**

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Hai DEMO thiếu quyền/ngữ cảnh tin cậy Core; nợ **C-MS22-01** đã có. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2709 passed, 1 failed, 4 xfailed cũ, 190 subtests passed; 416,82 giây (6 phút 56 giây), mã 1**. Không skipped. Failure duy nhất **test_mask_r6.py:46** nêu trên. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**: không tham chiếu cấm/tệp biên dịch. Lượt đầu vướng chữ tên thư mục migration trong đoạn NGUON mới; đã sửa cách diễn đạt, không sửa bộ kiểm. |
| Đối chiếu toàn bộ kiểm kê | **53/53** đường dẫn/bytes/SHA-256 khớp, mọi tệp gói LF; không tính chính kiểm kê. Ca kiểm kê trong full pytest cũng qua. |
| Bộ R6b / benchmark cuối | **63 passed**, không skip/xfail; ba benchmark cuối **3 passed in 2,51s**, mỗi phép **0,388130 / 0,689834 / 0,630239 giây**, đều dưới 2 giây. |
| `git diff --check` | **Mã 0**; fixture gold chỉ đổi biểu diễn checkout về LF, không có nội dung diff. |

**Thời gian thực tế:** bắt đầu **01:59:00**, kết thúc chốt kiểm **02:20:23 ngày 16/11/2026 (UTC+07)**, **0,36 giờ**, so với **2–3 giờ ƯỚC TÍNH**. Chưa bao gồm lần sửa kỳ vọng test cũ nếu được cho phép sau đó.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** thêm trần kỹ thuật **200.000 nút bảng dò** để ràng buộc RAM của biến thể alias; không đổi API hoặc nghiệp vụ. Để nguyên kỳ vọng test R6 cũ do ngoài danh sách tệp cho sửa, nên chưa đạt tiêu chí full xanh. Chỉ chuẩn hóa LF của fixture gold để đúng SHA đã khóa, không thay gold/nội dung/assertion. Không commit/push.

**Cần Core / Chờ Anh mới phát sinh:** Core chốt hai đường **port ban_giao_cuoi + return handler** và các nợ **C-P4-02/05, C-MS22-01** nêu trên. Cần Anh/lead cho phép sửa duy nhất kỳ vọng **mo_day_du=True → False** trong test R6 cũ rồi chạy lại full suite; lý do là danh sách tệp R6b hiện chỉ cho thêm test mới. Không có câu chọn nghiệp vụ mới.


## MASK-B6 — Excel chỉ RAM, 16/11/2026

**Kết luận: Xong mã/kiểm nội bộ B6; chưa đạt nghiệm thu chung vì CLI thiếu quyền và còn cửa Core/tệp hai lớp thuộc B7/B9.** PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia); chưa Core/Office/Local/Linux thật, Cloud tắt. Không commit/push. [Báo cáo theo AGENTS §6](BAO-CAO-MASK-B6.md), [lệnh/kết quả thật](KET-QUA-KIEM-MASK-B6.txt).

- Chỉ thêm `goi/e_mask/e_mask/tep_excel.py` trong tối đa bốn runtime được giao. Chuyển có sửa khung B5, dùng nguyên reader B3/writer B4, detector và kho tìm chính xác R2/R3, map/kiểm R5 và handle R4. Không sửa nguồn cũ, Core, SDK, manifest, mã migration, lock hoặc thêm dependency; không gọi/import engine khác từ runtime.
- Che mọi chuỗi shared/inline/rich text/metadata thuộc profile, mọi ô/hàng/cột ẩn; không ghép tên giữa hai ô độc lập. Shared có một nguồn, patch một lần, kiểm mọi nơi dùng và unused; primitive bổ sung Local cập nhật tất cả ô cùng index. Đọc lại bytes sau patch và so chuỗi/tọa độ/index/style/merge/epoch/lexical và bytes ô số. Giữ markup, kích thước và payload/record nén part bất biến qua B4. Tên sheet cần đổi, hidden/veryHidden sheet, formula/cache/definedNames/links/comments/chart/nhúng/part lạ chặn cả workbook.
- Ô số General/metadata số có định danh cần che bị chặn; không đổi số thành chuỗi. Kiểu tiền/ngày với format whitelist, số 0 đầu, boolean/error và metadata ngày/số được giữ; không làm tròn hoặc chuyển float. Hai lớp Local còn phải kiểm ngữ cảnh của ô/metadata bất biến. Map Unicode/NFD/Cf/rich run/byte và alias nguyên văn chỉ RAM; mơ hồ alias chặn.
- Handle R4 ràng buộc mã Core/scope/instance; TTL đề xuất 600 giây, nguyên 60–900, hạn tuyệt đối không trượt retry. Khóa ghi cùng timer/hủy; không tái tạo map sau dọn. Lỗi/hủy/kết thúc/hết hạn/tiêu thụ dọn RAM, không snapshot/ngăn map/tệp tạm/log/stderr/chuyển tiếp. Primitive chỉ trả băm/số đếm, luôn `CHO_LOCAL` và tập vùng kiểm Local rỗng; không upload hoặc có năng lực phát hành tệp trong B6.
- Trần ZIP/bytes/nút/ô/sheet và 32.767 UTF-16 áp cả chiều ra; vượt từ chối, không cắt. Reader B1/B3/B4 còn bảo thủ 500.000 ký tự khi đọc lại, sớm hơn trần ra 2.000.000; giữ profile và ghi giới hạn, không nới trong closure này. Các biên production/RAM/Office/Local thuộc B10/Core.
- Nguồn/symbol/quyền/SHA bytes và LF trước/sau ở NGUON và [bản chụp 19 nguồn](SHA-NGUON-MASK-B6-TRUOC.json); 19/19 nguồn giữ nguyên bytes. Kiểm kê gói tự sinh đủ 55 tệp, không thay manifest/mã migration. Gold R3 chỉ trả CRLF về nguyên blob Git LF có SHA đã khóa `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; không đổi gold, assertion, ngưỡng hoặc thêm skip/xfail.
- Kiểm nền B3/B4 trước triển khai: **569 passed, 26,84 giây, mã 0**. Bộ B6 cuối: **122 passed, 23,08 giây, mã 0**, không skip/xfail. Lượt đầu test mới lỗi encoding fixture và fixture tên sheet/khai báo số; đã sửa dữ liệu thử, không hạ cửa quyền/Local/quy tắc hoặc sửa test cũ.

### Cần Core — MASK-B6

- **C-P4-01:** Core cấp mã yêu cầu ổn định, xác minh ACL người/module/tài liệu/pháp nhân/DEMO và ghim cùng tiến trình/instance. Adapter CoreGia không chứng minh cửa thật, không dùng mã caller hoặc failover để phục hồi map.
- **C-P4-02:** sự kiện toàn chuỗi khi Mask rảnh, đồng bộ deadline/lease/hủy/tiêu thụ/bàn giao/ACK; không mở lại sau tiêu thụ. Mất xác nhận dùng ChuaRo, mất RAM phải chạy mới cả chuỗi. B6 chỉ kiểm lifecycle/tiêu thụ R4, mở Excel thực tế thuộc B8.
- **C-P4-03:** tìm chính xác bí mật/null+cờ, duy nhất/CAS/lô/tạo tên/chống lặp và quota chống dò đoán/không log truy vấn. Không giải mã danh mục; nợ chất lượng/chi phí R3 còn mở, tên mới chưa đủ bảo đảm tiếp tục chặn.
- **C-P4-04:** B7/AI-9/Core điều phối Local đủ mọi vùng/đoạn và xác minh nguồn, gồm mọi nơi dùng shared, sheet name/metadata và ngữ cảnh ô số bất biến. Không hồ sơ map/gốc phục hồi; cờ local do caller không làm chứng cứ. B6 không có cổng phát hành và không tự đóng nợ hai lớp.
- **C-P4-05:** quyền tải/trả đúng người/module; streaming/trần 1 MiB trước cấp phát SDK, 413, budget RAM/CPU/thời gian cả chuỗi; cách ly upload chưa phát hành và ACK. Không dump payload/traceback/map/gốc ra log/stderr/crash hoặc tệp tạm. Chưa Office/Local/Core thật; không có câu chọn nghiệp vụ mới chờ Anh.


### MASK-B6 — kết quả chốt theo AGENTS §6

| Lệnh / phép kiểm | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1; 0,97 giây**. Hai ví dụ thiếu nguồn ngữ cảnh/quyền Core (`MASK_NGU_CANH_CHUA_XAC_MINH`); giữ cửa chặn, không thay CLI bằng adapter có quyền. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2923 passed, 4 xfailed cũ, 190 subtests passed, 0 failed, 0 skipped; 441,10 giây; mã 0**. Bốn xfail strict “giới hạn quy tắc, nợ CAO” giữ nguyên. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0; 0,72 giây**, không tham chiếu cấm/tệp biên dịch. |
| `git diff --check` | **Mã 0**, chỉ cảnh báo checkout CRLF ở VIEC/gold R3; không lỗi khoảng trắng. |
| Bộ B6 / nền B3+B4 | **122 passed, 23,08 giây, mã 0** / **569 passed, 26,84 giây, mã 0**; không skip/xfail trong hai bộ này. |
| Provenance / kiểm kê / UTF-8/AST/LF | **19/19 nguồn** giữ nguyên bytes, SHA đích khớp NGUON; **55/55 tệp** đủ bytes/SHA; ba Python mới/fixture **3/3 đạt**, gói **0 bytecode**. |

**Thời gian thực tế:** **04:02:00–04:35:09 ngày 16/11/2026 (UTC+07), 0.55 giờ** tại mốc chốt kiểm/báo cáo; phiếu **6–10 giờ ƯỚC TÍNH**, độ khó `kho`.

**Lệch khỏi phiếu / quyết định tạm:** không vượt phạm vi; chỉ một runtime trong tối đa bốn tệp. Thêm kiểm ô số/metadata số không thể patch thì chặn; không đổi số sang chuỗi. Giữ trần reader chiều đọc lại bảo thủ 500.000 như B3/B4/B5, chưa mở đủ trần ra 2.000.000. Chỉ đưa fixture gold R3 về nguyên LF có SHA đã khóa, không đổi nội dung/gold/test/ngưỡng. `.venv` dùng `--system-site-packages` để dùng pytest/jsonschema sẵn có, SDK 2.2.0 cài offline wheel đúng SHA; không thêm dependency. Bộ bọc log lần đầu chưa chạy lệnh con do Windows cần đường `python.exe`; đã sửa bộ bọc rồi chạy đủ bốn lệnh với chính Python của `.venv`, tham số không đổi.

**Cần Core / Chờ Anh mới phát sinh:** kế thừa **C-P4-01…05** chi tiết ở trên và C-MS22-01 về CLI thiếu quyền; B7/B8/B9/B10 vẫn riêng, không nhận Local/Office/Core thật đạt. Không có câu chọn nghiệp vụ mới chờ Anh. Lead commit/mở PR, **PR: chờ lead mở**.

## MASK-B5b — số tài khoản/giấy tờ dạng ngày, 16/11/2026

**Trạng thái: Chờ Anh — mã đã sửa, chưa đạt full xanh do assertion cũ trái yêu cầu giữ ngày thật. PR: chờ lead mở.** Bắt đầu **04:02:00 ngày 16/11/2026 (UTC+07)** theo lead; **2–3 giờ ƯỚC TÍNH**, độ khó vừa. Đã kiểm bằng Core giả (CoreGia); chưa Core/Local/Office/Linux thật, Cloud tắt. Không commit/push.

- Sửa đúng hai runtime `tep_word.py`, `che_van_ban.py`; thêm `test_mask_b5b.py`, cập nhật CHANGELOG/NGUON/kiểm kê. Ngày được miễn phải hợp lịch, năm 1900–2100; nhãn tài khoản/giấy tờ/MST có/không dấu, hoa/thường, NFD/Cf, có/không hai chấm thắng hình dạng ngày. Cửa sổ 120 ký tự trước số, không qua biên đoạn/trường `;`, tab, `|`; cảnh báo từ nhãn không bị bỏ vì trùng vùng ngày. Giữ nguyên hai mẫu ngày thật đã giao và kiểm lịch nhuận.
- Sáu ca lọt được kiểm cả Word đọc lại bytes thật và văn bản; có kiểm trực tiếp nhánh miễn `_kiem_vung`, nhãn viết tắt/không dấu, ngày hợp lịch nhưng là định danh, ngày sai lịch và nhãn/số tách run. Trường hợp không che an toàn phải từ chối, không trả bản rõ. Không đổi API v1, lưu map ngoài RAM, sửa Core/e_hoi_ai hoặc mã Excel.
- Tái chạy trên runtime HEAD trước B5b: Word **6/6 trả số rõ, 0 từ chối**; runtime sau sửa **0/6 trả số rõ, 6/6 từ chối an toàn**. Thêm chốt độc lập giữ hiệu lực nhãn R5 khi hơn 120 ký tự khoảng trắng ngăn nhãn và số; bốn ca hồi quy trực tiếp nhánh miễn cho tài khoản/TK/CCCD/account. Bộ Word/văn bản/held-out trên mã runtime cuối **347 passed, 190 subtests passed; 49,71 giây, mã 0**. Bộ MASK-2c cùng B5b trước chốt nhãn xa: **593 passed; 304,93 giây, mã 0**, không coi là số kiểm mã runtime cuối.
- Held-out MASK-2c **190 ca, 115 có gold, 75 câu thường**, SHA nội dung vẫn `sha256:b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad`. Đối chiếu trực tiếp mã HEAD trước sửa và mã sau: **28 → 28** ca còn nguyên gold ở **nhánh quy tắc RAM lịch sử**, câu thường bị chặn **14/75 → 12/75**; chỉ T35/T36 đổi do ngày thật ISO không còn bị báo nhầm (đã chuẩn hóa alias ngẫu nhiên khi so). Đây không phải số đo Local/hai lớp, không tuyên bố 0 lọt vận hành. Test mới ghim SHA và hai chỉ tiêu không giảm; không đổi bộ gold hay luật tên từ held-out.
- Checkout fixture R3 có CRLF: chỉ trả về đúng byte LF của gold đã khóa, SHA `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; không đổi nội dung/gold/assertion hoặc SHA kỳ vọng. Mọi tệp gói hiện LF. Môi trường `.venv` Python 3.13.14, dùng thư viện hệ thống đã có, SDK 2.2.0 cài offline wheel SHA khớp; không thêm dependency. Các lệnh kiểm dùng `-B`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`.

### Kết quả kiểm và báo cáo §6 — MASK-B5b

**Kết luận: Chưa đạt — sáu ca lọt đã bị chặn, nhưng full suite còn một assertion cũ bắt buộc chặn nhầm ngày thật ISO; chưa được phép sửa tệp test đó.** Không bỏ test, thêm skip/xfail hoặc giữ báo nhầm trong runtime để làm xanh.

**Đã làm:** hai runtime đúng phạm vi, 180 ca B5b mới, cập nhật CHANGELOG/NGUON và kiểm kê 54/54 tệp LF. Word trước/sau trên sáu ca chứng minh **6 → 0** trường hợp trả số rõ. Ngày thật giữ nguyên; nhãn và lịch dùng chung cho văn bản/Word, nhãn R5 độc lập thắng cửa sổ gần. Held-out không giảm theo phép đo đã ghi phía trên. Đã kiểm bằng Core giả (CoreGia).

**Kết quả kiểm thật trên mã cuối:**

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Cả hai DEMO: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Nợ **C-MS22-01** đã có; không đổi gate/manifest/DEMO. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --tb=short` | **2980 passed, 1 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 439,37 giây, mã 1**. Duy nhất `test_mask_2b.py:201`, kết quả `[]`, kỳ vọng `[15]`; chi tiết và đề nghị một assertion bên dưới. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; không tham chiếu bị cấm hoặc bytecode trong gói. |
| Đối chiếu bytes LF/SHA-256/provenance | **54/54 tệp khớp**, trừ chính kiểm kê; hai SHA runtime sau sửa có trong NGUON; không bytecode. |
| B5b + B5 + văn bản trên mã cuối | **347 passed, 190 subtests passed; 49,71 giây, mã 0**, gồm 180 ca B5b mới. |
| `git diff --check` | **Mã 0**; Git cảnh báo checkout LF→CRLF ở tài liệu/fixture R3, nội dung gold không đổi. |

Lượt full trước chốt bảo vệ nhãn R5 ở xa: **2976 passed, 1 failed cùng assertion trên, 4 xfailed cũ, 190 subtests passed; 450,74 giây, mã 1**. Đã chạy lại full sau chốt mã; dùng kết quả **2980 passed** làm số kiểm cuối. Không dùng focused thay full.

**Thời gian thực tế:** **04:02:00–04:30:09 ngày 16/11/2026 (UTC+07), 0,47 giờ** tại mốc chốt kiểm; so với **2–3 giờ ƯỚC TÍNH**. Chưa gồm việc sửa assertion cũ nếu được duyệt sau đó.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** giữ đúng danh sách runtime, không thêm dependency, không đổi API v1 hay mã Excel. Cửa sổ gần 120 ký tự là lựa chọn triển khai trong yêu cầu cửa sổ hữu hạn; giữ cảnh báo nhãn R5 độc lập. Chỉ trả byte LF fixture R3 về đúng SHA đã khóa, không đổi nội dung/gold/test/ngưỡng. Chưa sửa assertion cũ do ngoài danh sách tệp cho phép; không commit/push.

**Cần Core / Chờ Anh mới phát sinh:** cần Anh/lead cho phép đổi duy nhất kỳ vọng `[15] → []` trong test cũ nêu dưới rồi chạy lại full suite. Không phát sinh cổng Core/SDK mới; nợ CLI quyền **C-MS22-01** và cửa P4/B5 giữ nguyên.

### Cần Core — MASK-B5b

Không phát sinh cổng Core/SDK hoặc câu nghiệp vụ mới. Kế thừa **C-MS22-01** (quyền/ngữ cảnh CLI DEMO) và các cửa P4/B5 về ghim chuỗi, vòng đời RAM, nguồn Local và bàn giao; B5b không chứng nhận các cửa này.

**Chờ Anh/lead về phạm vi test cũ:** `test_mask_2b.py::test_do_lap_lai_co_nguon_khong_bia_mau` bắt buộc `vi_tri_chan_nham == [15]`, tức câu ngày thật ISO “Đáo hạn khoản vay vào ngày 2026-10-30.” phải bị chặn nhầm. B5b giữ đúng ngày thật làm kết quả thành `[]`. Đã trình thay đúng một assertion `[15] → []`, không skip/xfail/đổi ngưỡng bảo mật; chưa sửa vì tệp nằm ngoài danh sách cho phép của phiếu. Đo lại riêng đã xác minh failure này, không phải lỗi giữ tiền/ngày hoặc lọt định danh.

## MASK-B6b — 16/11/2026, ô số Excel giả tiền/ngày

**Phạm vi:** sửa duy nhất runtime `goi/e_mask/e_mask/tep_excel.py`; thêm `tests/test_mask_b6b.py`; cập nhật VIEC/CHANGELOG/NGUON/kiểm kê. `xml_excel.py` không cần sửa: reader B3 đã chuyển `formatCode` khai báo sang style hiệu lực và từ chối khai lại ID builtin dưới 164. Không mở rộng profile, API v1, ngăn/RAM hoặc sửa các tệp B7/Core/e_hoi_ai. Không commit/push; PR: **chờ lead mở**.

- Phân loại theo tập `formatCode` chính xác; builtin chỉ tra mặc định khi không có khai báo. Bỏ miễn kiểm theo ID hoặc tìm y/d/h/s đơn lẻ. Chặn cả tệp khi ngày ngoài miền 1900–2100; xét epoch 1900 `[1,73416)` và 1904 `[0,71954)`, phần lẻ là giờ.
- Tiền vẫn qua detector số; số nguyên từ 9 chữ số, kể cả exponent/.0/dấu, bị chặn. Với phần lẻ, chỉ dung sai cảnh báo nhóm số phủ toàn giá trị sau khi hai vế thập phân riêng qua detector; nghi vấn khác hoặc chưa quét đủ đều chặn. Decimal chỉ dùng để kiểm trong RAM, không sửa số/format/bytes đầu ra. Chặn exponent cực đoan trước mở rộng chuỗi.
- **216 test B6b đạt (10,59 giây, mã 0):** các ID 5–8, 14, 22, 41–47, format riêng, khai lại ID bị reader từ chối, style kế thừa hàng/cột, ngày ngoài miền/biên hai epoch, detector chưa quét đủ và dọn RAM khi lỗi. Tiền `1500000`, `1234567.89`, tiền âm/.00 và ngày `46325` giữ nguyên bytes/số/format.
- Chạy cùng **12 workbook DEMO** trên module HEAD trước sửa và module sau: **12/12 → 0/12** trả số `123456789012` nguyên văn; sau sửa **12/12** từ chối an toàn. Không dùng kết quả này làm chứng nhận Local/Office/Core thật.
- Held-out MASK-2c **190 ca, 115 có gold, 75 câu thường**; SHA nội dung vẫn `sha256:b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad`. Nhánh quy tắc lịch sử vẫn **28** ca còn nguyên gold, **12/75** câu thường bị chặn, bằng baseline hiện tại sau B5b. Không đổi detector văn bản/gold/ngưỡng, không tuyên bố 0 lọt Local/hai lớp. Byte LF của fixture 2c và R3 khớp đúng blob Git/SHA khóa sau khi trả CRLF checkout về LF.
- Môi trường `.venv` Python 3.13.14 với thư viện test hệ thống đã có; SDK 2.2.0 cài offline wheel SHA `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`, không thêm dependency. Lệnh Python dùng `-B`; lệnh xuất tiếng Việt dùng `PYTHONIOENCODING=utf-8`. Đã kiểm bằng Core giả (CoreGia), Cloud tắt, chưa Core/Local/Office/Linux thật.

### Chờ Anh/lead — kỳ vọng test B6 cũ trái phiếu B6b

`test_mask_b6.py::test_so_tien_lon_format_tien_giu_nguyen_bytes` bắt buộc `1000000000` (10 chữ số nguyên) được cho qua chỉ vì style tiền, trái yêu cầu mới “độ dài chữ số ≥9 không có phần thập phân … giống ô General”. Focused B6+B6b trước bổ sung ca biên: **315 passed, 1 failed** duy nhất ở test này; không giữ bypass trong runtime để làm xanh.

Đã gửi đề nghị mở rộng phạm vi đúng một test: giữ nguyên workbook/số nguồn, đổi tên thành `test_so_tien_lon_format_tien_nghi_dinh_danh_bi_chan`; thay ba dòng `che`/lấy trạng thái/khẳng định giữ số bằng `chan(b, goi_office(p), ds=[], ma='MASK_TEP_CHUA_HO_TRO')`. Không bỏ test, skip/xfail hoặc giảm ngưỡng. Tệp cũ chưa sửa vì ngoài danh sách được giao; bộ mới đã có regression chặn `1000000000` độc lập.

### Cần Core — MASK-B6b

Không phát sinh cổng Core/SDK mới. Kế thừa **C-MS22-01** (CLI DEMO thiếu phiên/quyền tin cậy: 0/2 ĐẠT, mã 1) và C-P4-01…05 của B6/B7; không nới gate hoặc đổi manifest để né lỗi. Kiểm độc lập **ĐẠT, mã 0**; kiểm kê bao đủ **55/55** tệp gói theo bytes LF/SHA, trừ chính kiểm kê.

### Báo cáo §6 — MASK-B6b

**Kết luận: Chưa đạt — đã chặn 12/12 ca bypass và 216 test mới xanh; full còn duy nhất một test B6 cũ yêu cầu hành vi trái phiếu mới.**

**Đã làm:** sửa một runtime đúng phạm vi, ưu tiên formatCode thực tế và kiểm miền serial ngày theo epoch; tiền vẫn dò số định danh, giữ tiền/ngày thật nguyên bytes/format. Bổ sung test B6b, CHANGELOG/NGUON và kiểm kê 55/55. Không đổi API v1, reader, Core/e_hoi_ai hoặc tệp B7; map chỉ RAM. Đã kiểm bằng Core giả (CoreGia), Cloud tắt; chưa Core/Local/Office/Linux thật.

**Kết quả kiểm thật trên mã cuối:**

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Hai DEMO: “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Nợ C-MS22-01 cũ; không đổi gate/manifest/DEMO. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --tb=short` | **3318 passed, 1 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 477,77 giây; mã 1**. Duy nhất `test_mask_b6.py::test_so_tien_lon_format_tien_giu_nguyen_bytes`, dòng 565. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**; không tham chiếu bị cấm hoặc bytecode trong gói. |
| `pytest e_mask/tests/test_mask_b6b.py -q` qua Python `.venv`, `-B -m` | **216 passed, 10,59 giây, mã 0**; không skip/xfail. |
| Kiểm kê / nguồn / tệp B7 | **55/55 tệp LF khớp bytes/SHA-256**, trừ chính kiểm kê; runtime sau đúng SHA tại NGUON. `engine.json`, `xml_excel.py` và các tệp B7 có trong worktree giữ nguyên bytes HEAD. |
| `git diff --check` | **Mã 0**; chỉ cảnh báo checkout LF→CRLF ở hai fixture đã trả về blob LF đúng SHA khóa. |

**Thời gian thực tế:** **05:06–05:23 ngày 16/11/2026 (UTC+07), khoảng 0,28 giờ** tại mốc chốt kiểm/báo cáo; phiếu **2–3 giờ ƯỚC TÍNH**, độ khó vừa. Không cộng thời gian chờ duyệt sửa test cũ sau bàn giao.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** giữ đúng danh sách tệp cho phép; không sửa `test_mask_b6.py` ngoài closure khi chưa được trả lời. Do đó chưa đạt yêu cầu full xanh; không bỏ test, thêm skip/xfail hoặc nới runtime để giữ bypass. Miền ngày dùng cận lịch chính xác đến hết năm 2100 theo epoch, thay vì khoảng ví dụ 73050. Chuẩn hóa hai fixture CRLF checkout về nguyên blob Git LF để giữ SHA, không đổi gold/ngưỡng. Không thêm dependency, commit hoặc push.

**Cần Core / Chờ Anh mới phát sinh:** không có cổng Core/SDK mới; C-MS22-01 và C-P4-01…05 giữ nguyên. Chờ Anh/lead cho phép đổi đúng test B6 cũ theo bản thay cụ thể ở mục trên, rồi chạy lại full suite. PR: **chờ lead mở**.

## MASK-B6b l??t 2 ? 16/11/2026, ch?nh quy t?c ? ti?n theo lead

**Tr?ng th?i: ??t ?i?u ki?n MASK-B6b l??t 2** ? full pytest xanh, ki?m ??c l?p m? 0, ki?m k? kh?p; CLI SDK c?n n? quy?n C-MS22-01 c?. PR: **ch? lead m?**. B?t ??u **05:46 ng?y 16/11/2026 (UTC+07)** theo lead; **1 gi? ??C T?NH**, ?? kh? v?a. Quy?t ??nh d??i ??y thay quy t?c ? ti?n v? y?u c?u ??i test B6 ? l??t 1; k?t qu? l?ch s? l??t 1 kh?ng l? k?t qu? m? hi?n t?i.

Quy?t ??nh lead 16/11: ? ti?n ?12 ch? s? nguy?n gi? nguy?n; r?i ro c?n l?i: s? ??nh danh ?12 ch? s? c? ? ??nh d?ng ti?n s? kh?ng b? d? ? ch? Anh x?c nh?n.

- FormatCode th?c t? TI?N/K? TO?N: ph?n l? kh?c 0 ho?c s? nguy?n ?12 ch? s? kh?ng t?nh d?u gi? nguy?n bytes/format, b? d? h?nh d?ng ??nh danh; s? nguy?n ?13 ch? s? qua c?ng c?a General. Decimal ch? d?ng trong RAM ?? ph?n lo?i, kh?ng s?a lexical c?a ?. Gi? quy t?c serial ng?y l??t 1, General/0 v? ch?t exponent c?c ?oan tr??c m? r?ng chu?i.
- Khai b?o ds v?n ch?n nh? tr??c; b? sung t?m ch?nh x?c gi? tr? ? ti?n/serial ng?y trong ng?n b? m?t, c?ng v?ng/quy?n R4 qua SDK, kh?ng ??c b?n r? ho?c li?t k? kho. ? ti?n ki?m c? raw value v? d?ng s? g?n/d?u/tr? tuy?t ??i ?? exponent/.00 kh?ng n? ???c gi? tr? ?? khai. Cache RAM ?2.000 ?ng vi?n; v??t t? ch?i, ki?m h?n/quy?n tr??c/sau truy v?n, kh?ng ghi ng?n ho?c map ra ngo?i RAM.
- Ch? s?a m?t runtime `tep_excel.py`; gi? nguy?n test B6 `test_so_tien_lon_format_tien_giu_nguyen_bytes` v?i `1000000000`. C?p nh?t test B6b, CHANGELOG/NGUON/ki?m k?; kh?ng s?a reader/Core/SDK/t?p B7, kh?ng th?m dependency, kh?ng commit/push. Gi? c?c thay ??i B6b l??t 1 c? s?n trong worktree v? d? li?u DEMO/SHA ?? kh?a.
- Focused sau s?a m? cu?i: **414 passed, 20,71 gi?y, m? 0** ? `test_mask_b6b.py`; l??t B6+B6b tr??c b? sung ca bi?n/ng?y/ng?n cu?i **505 passed, 39,58 gi?y, m? 0**. Full sau c?ng m?i l? k?t qu? ch?t.
- M?i tr??ng `.venv` Python **3.13.14**, SDK **2.2.0**, wheel offline SHA-256 **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** kh?p SHA256SUMS. Python ch?y `-B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`. ?? ki?m b?ng Core gi? (CoreGia); ch?a Core/Local/Office/Linux th?t, Cloud t?t.

### C?n Core / Ch? Anh ? MASK-B6b l??t 2

Kh?ng ph?t sinh c?ng Core/SDK m?i. K? th?a **C-MS22-01**: CLI DEMO chu?n thi?u quy?n/ng? c?nh tin c?y; gi? gate/manifest/DEMO. C-P4-01?05 c?a B6/B7 gi? nguy?n. Ch? Anh x?c nh?n r?i ro ? ti?n ?12 ch? s? ?? n?u; vi?c ?p d?ng quy?t ??nh lead trong l?t n?y ?? ???c giao, kh?ng ch? m?i s?a.

### B?o c?o ?6 ? MASK-B6b l??t 2

**K?t lu?n: ??t ?i?u ki?n l??t 2** ? ti?n ??ng quy?t ??nh lead, pytest to?n b? xanh v?i ??ng b?n xfailed c?, ki?m ??c l?p m? 0 v? ki?m k? kh?p. Nghi?m thu chung qua CLI SDK v?n ch?a ??t do n? quy?n C-MS22-01 ?? c?; kh?ng nh?n l? ?? n?i Core th?t.

**?? l?m:** gi? m? B6b l??t 1, ch? ch?nh runtime `tep_excel.py` theo formatCode th?c t?: ? TI?N/K? TO?N c? ph?n l? kh?c 0 ho?c s? nguy?n ?12 ch? s? gi? nguy?n bytes/format; s? nguy?n ?13 ch? s? ?p gate General. ??nh danh khai trong ds/ng?n b? m?t v?n ch?n; ng?y gi? mi?n serial l??t 1. C?p nh?t B6b, CHANGELOG/NGUON v? ki?m k?; test B6 c? v?i `1000000000` gi? nguy?n v? qua trong full suite. ?? ki?m b?ng Core gi? (CoreGia), ch? DEMO; ch?a Core/Local/Office/Linux th?t, Cloud t?t.

**K?t qu? ki?m th?t tr?n m? cu?i:**

| L?nh / ph?p ki?m | K?t qu? |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ??T, m? 1**; c? hai DEMO: ?Ch?a x?c minh ???c phi?n v? quy?n x? l? y?u c?u.? N? C-MS22-01 c?, gi? nguy?n gate/manifest/DEMO. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --tb=short` | **3517 passed, 4 xfailed c?, 190 subtests passed, 0 failed, 0 skipped; 474,98 gi?y (7 ph?t 54,98 gi?y), m? 0**. B?n xfailed strict MASK-2b ?gi?i h?n quy t?c, n? CAO? gi? nguy?n; kh?ng th?m skip/xfail. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **??T, m? 0**; kh?ng tham chi?u c?m ho?c bytecode trong g?i. |
| Focused B6b sau s?a cu?i | **414 passed, 20,71 gi?y, m? 0**, kh?ng skip/xfail. |
| ??i chi?u ki?m k? | **55/55** ???ng d?n/bytes LF/SHA-256 kh?p, tr? ch?nh ki?m k?; SHA runtime hi?n t?i ??ng NGUON. |
| Ph?m vi / diff | Test B6 c?, manifest, reader `xml_excel.py`, `chay.py` gi? nguy?n n?i dung HEAD; kh?ng s?a t?p B7. `git diff --check` **m? 0** sau b? d?ng tr?ng cu?i VIEC; ch? c?n c?nh b?o LF?CRLF do c?u h?nh checkout. |

**Th?i gian th?c t?:** **05:46:00?06:01:37 ng?y 16/11/2026 (UTC+07), 0.26 gi?** t?i m?c ch?t ki?m/b?o c?o, so v?i **1 gi? ??C T?NH**, ?? kh? v?a. M?c b?t ??u theo lead; kh?ng c?ng gi? l??t 1 ho?c th?i gian ch? gi?a hai l??t.

**L?ch kh?i phi?u / quy?t ??nh t?m ?? d?ng:** kh?ng c? l?ch nghi?p v?; ?p ??ng quy?t ??nh lead l??t 2 thay ?i?m 2 l??t 1. Kh?ng c?n s?a `test_mask_b6.py` v? k? v?ng nguy?n tr?ng ?? ph? h?p. B? sung ki?m kh?p ch?nh x?c ng?n b? m?t cho c?c ? ???c mi?n detector ?? b?o ??m khai b?o ??nh danh th?ng format; gi? gi?i h?n exponent k? thu?t l??t 1 v? t? ch?i v??t budget, kh?ng c?t ng?m. Kh?ng s?a Core/SDK/reader/API v1, th?m dependency, commit ho?c push.

**C?n Core / Ch? Anh m?i ph?t sinh:** kh?ng c?ng Core/SDK m?i; k? th?a C-MS22-01 v? C-P4-01?05. Quy?t ??nh lead 16/11: ? ti?n ?12 ch? s? nguy?n gi? nguy?n; r?i ro c?n l?i: s? ??nh danh ?12 ch? s? c? ? ??nh d?ng ti?n s? kh?ng b? d? ? ch? Anh x?c nh?n. Tr??ng h?p ?? khai trong ds/ng?n b? m?t v?n ch?n. PR: **ch? lead m?**.

## MASK-B6c — 16/11/2026, hiệu năng che Excel nhiều hàng

**Kết luận hiệu năng: Chưa đạt ổn định mốc 2.000 hàng × 5 cột ≤3 giây.** Hai lượt từng đạt 2,5479 và 2,6978 giây, nhưng các lượt cuối 3,2709 / 5,6482 / 5,6756 giây, median **5,6482 giây**; không dùng riêng số tốt nhất để nhận đạt. Mục tiêu gần 1 MiB ≤60 giây đạt: **4,8568–11,8848 giây**. Chỉ sửa hai runtime `tep_excel.py`, `doc_excel.py`; thêm `test_mask_b6c.py`. PR: **chờ lead mở**. Không commit/push. Đã kiểm bằng Core giả (CoreGia); không phải Core/Local/Office/Linux thật. Nghiệm thu chung qua CLI vẫn có nợ quyền C-MS22-01 cũ.

### Phương pháp và số đo thật

- Profiler `cProfile` trước sửa, DEMO 200 hàng × 5 cột: **50,2794 giây**, **154.407** lần `quyen.xac_minh`, 38.279.921 function calls. `_BuocRAM.kiem`: **22,929 giây cumulative**; `ten_nguoi.tim`: **18,343 giây**; bốn lần reader `doc_excel`: **21,926 giây**. Thời gian cumulative lồng nhau, không cộng lại. Đây là phép đo có overhead profiler, không so trực tiếp với số không profiler của lead.
- Profiler trên mã cuối, cùng 200 hàng: **0,6827 giây**, **34** xác minh, **1.126.738** calls; reader cumulative **0,470 giây**, mapper worksheet **0,183 giây**, clone bản đọc **0,049 giây**; detector tên còn 11 lượt thay vì 2.002 lượt baseline. Tải máy từng lượt khác nhau; chỉ dùng profile để xác định điểm nóng và số lời gọi, không suy SLA từ tỷ lệ thời gian profiler.
- Đo không profiler tuần tự trên cùng máy. Generator `nhieu_hang` ở test B6c: A = tên công ty DEMO cần che, B = văn bản thường, C = số General `123`, D = tiền dạng text `1.000.000 VND`, E = ngày dạng text `2026-10-30`. Bốn cột text là inlineStr, một phép thay mỗi hàng. Sinh tệp/seed CoreGia ngoài khoảng đo; khoảng đo gồm nhận bước R4, che, writer, kiểm bytes ra, kết thúc/dọn RAM; không có RPC mạng/Office/Local thật.

| Mẫu DEMO | Bytes / cách ZIP | Giây thực tế | Xác minh quyền | Kết quả |
|---|---:|---:|---:|---|
| 200 hàng × 5 cột, cả hai runtime HEAD trước B6c | 5.057 / DEFLATE | **4,6024** | **154.407** | 200 phép thay |
| Cùng 200 hàng, mã cuối | 5.057 / DEFLATE | **0,2433** | **32** | 200 phép thay; SHA bytes ra bằng baseline |
| 2.000 hàng × 5 cột, mã cuối | 35.196 / DEFLATE | **2,5479** | **182** | 2.000 phép thay; **đạt ≤3 giây** |
| 3.550 hàng × 5 cột, gần 1 MiB | **1.039.053 = 0,991 MiB / ZIP STORED** | **4,8568** | **318** | 3.550 phép thay; **đạt ≤60 giây** |
| 40.000 hàng × 5 cột | 673.645 / DEFLATE | **0,0028** | **4** | Từ chối `MASK_QUA_GIOI_HAN`, không trả bản che |

**Các lượt tái đo sau full cuối (cùng mã/băm/dữ liệu):** 2.000 hàng lần đầu **4,0603 giây, 194 xác minh**; ba lượt kế tiếp **3,2709 / 5,6482 / 5,6756 giây**, tương ứng **190 / 199 / 199 xác minh**, median **5,6482 giây**. Mẫu 0,991 MiB tái đo **11,8848 giây, 365 xác minh**. Không có thay đổi runtime giữa các lượt. **Nguyên nhân biến động chưa được xác minh**; không quy chắc cho tải máy hoặc dùng giả định để loại các lượt chậm. Giữ toàn bộ số đo, không tăng timeout để nhận đạt mốc 3 giây.

Mã cuối đã có thêm lượt đo độc lập 2.000 hàng **2,6978 giây, 184 xác minh**, cùng băm đầu ra. Không đổi thời hạn/lease để lấy số đạt. Băm bytes ra 200 hàng trước/sau đều `sha256:aa3a43f59ff9d39e427faeba9a91742b9204bb1a524202228133187cbbdb406f`; 2.000 hàng `sha256:d193403a7f5eec502ee0e08ce49314ec1216fa8af2534bd11f68399974a0a75e`; 3.550 hàng `sha256:3fc886ffba2b967f4af4b7fc61910b0606a434943605319540fb5359aa15d319`. Với cùng 200 hàng đo tuần tự cuối: thời gian giảm **18,92 lần**, số xác minh giảm **99,979%**.

Các lượt phát triển 2.000 hàng ghi nhận 37,7067 → 18,5781 → 12,5941 → 5,5621 → 3,5097 giây khi lần lượt thêm tối ưu và tải máy thay đổi; chúng không phải kết quả mã cuối. Hai lượt thử baseline 2.000 hàng bị SDK hủy theo lease của fixture trực tiếp, kể cả lần thử vòng gia hạn. **Không có baseline 2.000 hàng hoàn tất trên workload B6c**, không suy từ 200 hàng; số lead 41,5 giây là tham khảo workload khác. Harness hiện dùng vòng gia hạn SDK cho primitive gọi trực tiếp; không tắt gate lease. Tùy chọn `--truoc` nạp cả hai runtime HEAD trong RAM, giữ identity DTO và khôi phục alias reader sau đo, không ghi tệp nguồn cũ.

**Giới hạn:** ZIP STORED gần 1 MiB không đại diện cho 40.000 hàng nén. Profile hiện giữ 1 MiB container, 2 MiB/part, 8 MiB giải nén, 20.000 ô, 100.000 nút XML và 500.000 ký tự. Mẫu 40.000 × 5 vượt nhiều giới hạn và bị từ chối tại gate ZIP. Không tuyên bố hỗ trợ khối lượng đó. Mục tiêu gần 1 MiB đã đạt, **không cần đề nghị tăng trần thời hạn xlsx**; giữ nguyên `engine.json`, gồm mốc 300 giây. Worksheet UTF-16/entity/CR/LF/tab/encoding khác giữ mapper cũ để bảo toàn kết quả; không khẳng định mọi hình dạng XLSX đạt cùng tốc độ.

Lệnh tái đo: `.venv/Scripts/python -B e_mask/tests/test_mask_b6c.py 2000`; `3550 --khong-nen` cho gần 1 MiB; `200 --profile` cho profiler; `200 --truoc` cho baseline hai runtime; `40000 --vuot-tran` cho gate từ chối. Chỉ sinh dữ liệu DEMO trong RAM.

### Thay đổi và giữ nguyên kết quả

- `_BuocExcel` bọc handle R4 trong primitive, không monkeypatch handle/port dùng chung. Checkpoint cục bộ mỗi 64 callback hoặc 10 ms; xác minh đầy đủ Core mỗi 4.096 callback hoặc 50 ms. Khoảng thời gian tính khi vòng xử lý chạy, không phải SLA của RPC/parser đang chặn. Kiểm đầy đủ trước ghi RAM và trước trả; truy cập kho giữ xác minh trước/sau R2. Scope/deadline mới không kéo dài TTL; hủy/lifecycle/timer dọn R4 như cũ.
- Cache map theo **chuỗi Unicode chính xác**, không gộp NFC/NFD/Cf/hoa-thường. Cache hit vẫn cộng đủ budget ký tự/vị trí từng ô; alias mơ hồ vẫn từ chối. Cache số chỉ giữ kiểm thành công trong lượt; không đổi B6b, format/lexical hoặc trần. Cùng map bất biến chỉ kiểm/gộp alias một lần; map khác nhau vẫn kiểm xung đột nguyên văn.
- Profiler chứng minh reader là điểm nóng nên dùng `doc_excel.py` đúng phạm vi cho phép. `_map_excel` dùng byte index của Expat chỉ trên worksheet UTF-8 đơn giản **sau** gate B1/B3; mỗi tag/attribute/leaf đối chiếu cây độc lập B1. Không thay parser/gate nghiệp vụ, không serialize XML để đoán offset. UTF-16/entity/CR/LF/tab/CDATA/encoding khác đi nguyên `xml_excel.map_xml`. ST không chứa `_x` giữ nguyên ChuXML đã được parser kiểm.
- Cache reader tối đa hai bản theo **toàn bytes**, không chỉ băm; trả cây XML, dataclass/map/ZIP độc lập để sửa đối tượng caller không làm bẩn bản chuẩn hoặc né `doc_lai_nguon`. Ngoài callback cache riêng của primitive, reader vẫn kiểm đầy đủ. Cache/handle dọn trong `finally`, không qua lượt/retry hoặc ra ngăn/tệp/log.
- **61 test B6c**: 28 ca checkpoint/cache/budget/Unicode mơ hồ/scope/quyền/deadline/hủy/TTL/mất lease/bản đọc độc lập/dọn RAM/số RPC; thêm 32 ca so **toàn bộ map** nhanh với map lexical cũ trên rich runs, Unicode NFC/NFD/Cf/emoji, entity/ST, UTF-8/BOM/UTF-16/UTF-16BE và fallback newline; thêm một ca khai báo encoding ngoài UTF-8 sau hơn 200 byte vẫn bắt buộc đi map cũ. B6/B6b giữ nguyên test, không thêm skip/xfail.
- Held-out MASK-2c giữ SHA nội dung `sha256:b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad`; không sửa gold/detector văn bản. Fixture R3 checkout CRLF chỉ trả về nguyên blob Git LF, SHA `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`, không đổi nội dung/assertion; không có diff nội dung Git.
- Worktree giao **chưa có** `ho_so_tep.py` hoặc `test_mask_b7.py`; VIEC chỉ có phiếu/phụ thuộc B7, không có báo cáo B7 hoàn tất để đối chiếu. Không tạo/sửa B7/B8; lead cần chạy lại tích hợp B7 sau gộp. Không sửa Core/e_hoi_ai/API v1/manifest hoặc nguồn cũ.

### Cần Core — MASK-B6c

Không phát sinh cổng Core/SDK mới. Kế thừa **C-MS22-01**: CLI chuẩn thiếu quyền/ngữ cảnh tin cậy, 0/2 ĐẠT; giữ gate/manifest/DEMO. Các cửa **C-P4-01…05** về ghim, vòng đời/lease, ngăn bí mật, nguồn Local và bàn giao giữ nguyên. Số đo CoreGia không gồm độ trễ RPC thật; cần đo tích hợp khi có cửa Core. Không có câu hỏi nghiệp vụ mới.

### Báo cáo §6 — MASK-B6c

**Kết luận: Chưa đạt ổn định mục tiêu 3 giây** — full suite xanh và mốc gần 1 MiB đạt, nhưng median ba lượt 2.000 hàng cuối còn 5,6482 giây. CLI chuẩn vẫn thiếu quyền Core cũ; không nhận đã nối Core thật.

**Đã làm:** hai runtime đúng phạm vi, gom quyền/checkpoint, cache RAM lượt và reader độc lập, map worksheet UTF-8 đơn giản bằng Expat sau gate; 61 test mới; CHANGELOG/NGUON/kiểm kê 55/55, `phien_ban=1.4.0` bằng manifest. Đã kiểm bằng Core giả (CoreGia), không commit/push; PR: **chờ lead mở**.

**Kết quả kiểm thật:**

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**. Hai DEMO thiếu phiên/quyền tin cậy; C-MS22-01 cũ, giữ gate/manifest. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q --tb=short` | **3578 passed, 4 xfailed cũ, 190 subtests passed, 0 failed, 0 skipped; 3990,42 giây (1:06:30); mã 0**. Không thêm skip/xfail. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**, đã chạy lại sau sửa metadata nguồn/kiểm kê cuối. |
| Focused B6c trên mã cuối | **61 passed, 2,06 giây, mã 0**. |
| Kiểm kê sau sửa bảng SHA nguồn | **55/55** bytes LF/SHA/đường dẫn khớp; `phien_ban=1.4.0` bằng manifest; ca `test_kiem_ke_day_du_bytes_va_sha_tung_tep` chạy lại **1 passed, 0,14 giây, mã 0**. Chỉ sửa tài liệu/kiểm kê sau full, runtime giữ nguyên. |
| `git diff --check` | **Mã 0**; cảnh báo checkout LF→CRLF ở VIEC/fixture R3, không đổi gold. |

Lịch sử kiểm: trước tối ưu mapper, full **3545 passed, 4 xfailed, 190 subtests**, 376,84 giây. Lượt sau mapper bị **1 failed (kiểm kê), 3576 passed, 4 xfailed, 190 subtests**, 309,67 giây vì cập nhật chốt encoding/kiểm kê khi suite đang chạy; đã đồng bộ rồi giữ nguyên mã và chạy lại full đạt **3578 passed** nêu trên. Không dùng focused thay full, không che mã thoát CLI. Thời gian full cuối ghi đúng 3990,42 giây, không thay bằng thời gian lượt nhanh trước.

**Thời gian thực tế:** **07:20:00–09:12:21 ngày 16/11/2026 (UTC+07), 1.87 giờ** tại mốc chốt kiểm/báo cáo; bắt đầu theo lead. Phiếu **2–3 giờ ƯỚC TÍNH**, độ khó vừa.

**Lệch khỏi phiếu / quyết định tạm:** chưa đạt ổn định mốc 3 giây; không đổi nghiệp vụ/phạm vi tệp; dùng `doc_excel.py` vì profiler xác nhận điểm nóng. Mẫu gần 1 MiB là ZIP STORED trong profile, không thay bằng chứng 40.000 hàng nén; trường hợp đó từ chối theo trần sẵn có. Giữ mọi gate/engine.json/API v1, không thêm dependency; SDK 2.2.0 offline SHA khớp, `.venv` dùng thư viện test hệ thống đã có. Tối ưu mapper chỉ trong reader được phép sửa, `xml_excel.py` giữ nguyên.

**Cần Core / Chờ Anh mới phát sinh:** không cổng mới; C-MS22-01/C-P4-01…05 giữ nguyên. Chưa có B7 trong worktree để kiểm tích hợp, cần lead gộp và tái kiểm; không nhận B7 đã xanh. Không có câu hỏi nghiệp vụ mới.
