# Báo cáo MASK-B8 — 16/11/2026

**Kết luận: Chưa đạt nghiệm thu chung** — mã mở tệp nội bộ và 207 ca B8 đã đạt bằng CoreGia; CLI còn thiếu quyền Core và kiểm kê thật ngoài phạm vi chưa cập nhật. PR: **chờ lead mở**.

**Đã làm:** đúng ba runtime trong năm tệp được giao: `mo_tep_word.py`, `mo_tep_excel.py`, `ho_so_tep.py`. Hai tệp `xml_word.py`/`xml_excel.py` giữ nguyên. Mở từ map RAM đúng mã Core cấp/scope/instance đã qua B7, R4 tiêu thụ một lần; không tra kho, giải mã bi_mat, tải gốc/map từ Core hoặc lưu hồ sơ dự phòng.

- Bản che nguyên SHA trả **chính bytes gốc còn RAM**, sau kiểm băm/trần/đủ map/quyền. Tệp AI sửa được kiểm lại toàn gói, patch trên chính tệp hiện gửi và đọc lại; giữ phần mới, format, metadata hỗ trợ, shared index, ô số/tiền/ngày và local record/payload bất biến.
- Nhận case/space, Word runs và Excel rich runs cùng ô khi duy nhất. Alias ngoài yêu cầu/hỏng/thiếu/mơ hồ, sheet phải đổi tên hoặc phần lạ/trần bị chặn cả tệp, không trả mở dở. Không dùng detector để che lại tên/số tài khoản vừa mở.
- `MoTepRAM.mo(viec, bytes, loai=..., ma_yeu_cau=..., dong_viec=...)` trả `TepDaMoRAM` nội bộ chỉ sau bàn giao cách ly và tiêu thụ R4. Dọn sau thành công/lỗi/hủy/TTL/mất ACK; `dong_viec=false` vẫn dọn, không cache bản rõ để retry. ChuaRo không tạo kết quả thành công giả. B9 mới đọc mẫu 7, đăng ký năng lực và bộ T.

**Kết quả kiểm thật trên mã chốt:**

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**: cả hai DEMO “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Nợ C-MS22-01 cũ, không nới gate. [Log](KET-QUA-KIEM-MASK-B8-SDK.txt) |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **3865 passed, 1 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 998,16 giây; mã 1**. Lỗi duy nhất `test_mask_r1.py::test_kiem_ke_day_du_bytes_va_sha_tung_tep` do kiểm kê thật chưa khớp gói. [Log](KET-QUA-KIEM-MASK-B8-PYTEST.txt) |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **Mã 1**, cùng kiểm kê; không nhận lệnh chuẩn đã đạt. [Log](KET-QUA-KIEM-MASK-B8-DOC-LAP.txt) |
| `.venv/Scripts/python -B -m pytest e_mask/tests/test_mask_b8.py -q` | **207 passed, 85,56 giây, mã 0**; không skip/xfail. [Log](KET-QUA-KIEM-MASK-B8-MUC-TIEU.txt) |
| Kiểm kê đề nghị ngoài gói | **60/60** đúng bytes/SHA; cùng bộ kiểm độc lập đạt khi chỉ thay nội dung kiểm kê bằng đề nghị trong RAM. Không thay kết quả lệnh chuẩn. [Đề nghị](KIEM-KE-MASK-B8-DE-NGHI.json), [đối chiếu](KET-QUA-KIEM-MASK-B8-KIEM-KE-DE-NGHI.txt) |
| `git diff --check` | **Mã 0**; chỉ cảnh báo EOL của NGUON và fixture R3. [Log](KET-QUA-KIEM-MASK-B8-DIFF.txt) |
| Nguồn/độc lập bổ sung | SHA **14/14** khớp hiện vật, **13 nguồn** giữ nguyên nội dung LF; AST/UTF-8/khoảng trắng **5/5**. Gói không có bytecode/symlink/tham chiếu cấm khi dùng kiểm kê đề nghị với cùng checker. [SHA](SHA-NGUON-MASK-B8.json) |

207 ca B8 phủ hai định dạng: SHA nguyên bytes, AI thêm/sửa/case/space/run/rich text/shared/metadata, encoding/entity, tiền/ngày/ô số, alias lạ-hỏng-thiếu/map mơ hồ, Admin duyệt giữa chuỗi, sai scope, restart/worker khác, hủy trước handler/khi rảnh/trong reader/patch/bàn giao, TTL/deadline, double-open hai luồng, retry/mất ACK, input đổi, trần vào/ra/ô và spy kho/upload/I/O/log. Bốn xfailed strict MASK-2b “giới hạn quy tắc, nợ CAO” giữ nguyên; không thêm skip/xfail hoặc đổi ngưỡng/gold.

**Thời gian thực tế:** **07:49:00–09:38:37 ngày 16/11/2026 (UTC+07), 1,83 giờ**, tính tới mốc chốt báo cáo; phiếu **6–10 giờ ƯỚC TÍNH**, độ khó `kho`. Bao gồm đọc tài liệu, dựng venv, triển khai, sửa fixture và chờ kiểm; không phải thời gian xử lý production hoặc benchmark.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** không vượt danh sách runtime; không sửa Core/SDK/nguồn cũ/API/manifest hoặc thêm dependency. Kiểm kê nằm ngoài năm tệp cho phép nên chỉ sinh đề nghị ngoài gói cho lead; đây là lý do chưa đạt đóng gói chung. Fixture R3 chỉ trả CRLF checkout về nguyên blob Git LF có SHA đã khóa `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`, không đổi gold/assertion. Với tệp AI sửa, alias đã phát hành bị xóa hoàn toàn cũng từ chối theo cách hiểu bảo thủ của yêu cầu alias thiếu. Reader đọc lại vẫn trần bảo thủ 500.000 ký tự; chưa hứa đạt đủ trần ra 2 triệu/8 MiB hoặc budget OS thật.

**Cần Core / Chờ Anh mới phát sinh:** kế thừa **C-P4-01/02/05** và **C-MS22-01**. Core cần binding quyền/affinity/lifecycle, `kiem_tep_mo` xác minh ACL đầu vào và budget, `ban_giao_cuoi` giữ scope/băm/lease/deadline qua chốt RAM và ACK, cách ly upload/kết quả; không dump map/gốc/traceback. Các port là protocol đề nghị, không phải API SDK 2.2.0 đã có. Lead áp dụng kiểm kê 60 tệp, commit và mở PR; B9 nối mẫu 7/bộ T, B10 nghiệm thu thật. Không có câu nghiệp vụ mới chờ Anh chọn lại.

Môi trường: Windows, Python **3.13.14**, venv tại worktree dùng công cụ test hệ thống đã ghim; SDK **2.2.0** cài `--no-index --no-deps` từ wheel repo, SHA **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** khớp phát hành. **Đã kiểm bằng Core giả (CoreGia)**, chỉ DEMO và AI sửa tệp giả lập; **chưa Core/Office/Local/Linux thật**, Cloud tắt. Không commit/push.
