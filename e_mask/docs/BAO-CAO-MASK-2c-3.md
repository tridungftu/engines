# Bàn giao MASK-2c-3 — 15/11/2026

**Kết luận: Đạt phạm vi MASK-2c-3 bằng CoreGia; chưa đạt nghiệm thu tích hợp CLI SDK chuẩn do thiếu nguồn quyền Core.** Đã kiểm bằng Core giả (CoreGia); chưa kiểm Core/model thật hoặc Linux thực tế. PR: **chờ lead mở**; không commit/push.

**Đã làm:** Đúng năm tệp mã được giao: `hau_kiem_ai.py`, `chay.py`, `phong_bi.py`, `kho_dinh_danh.py`, `engine.json`. Gói 1.2.0 thêm `mask.hau_kiem_ai_cuc_bo@1`, nhận duy nhất `tra_loi_ai`, trả cố định `van_ban_da_che` hiện có. Không mở che hoặc gọi AI/engine khác trong bước này.

Snapshot gốc/bản quy tắc/map và tập phản hồi chỉ được đọc qua `viec.mo_tep` với port Core tin cậy. Kiểm ACL, mã yêu cầu/phiên/module/người/tài liệu/pháp nhân, bytes/kích thước/SHA, map, prompt/khuôn/profile, yêu cầu AI và đủ đúng kế hoạch đoạn. Băm AI được tái tính trên **toàn phong bì `yeu_cau_ai` JSON chuẩn**, không dùng băm riêng tài liệu. Core phải chứng thực nguồn từng phản hồi AI-9/Local/hoàn tất và phần bổ sung tập phản hồi cuối; cờ caller/model không cấp quyền. Phản hồi rỗng vẫn cần khuôn hoàn chỉnh, kiểm trích dẫn và chứng cứ đủ đoạn.

Thực thể chắc được đối chiếu nguyên văn/code point/biên/tiền-ngày qua map, alias đã che trọn được giữ nguyên; nghi vấn, partial overlap, che prefix, loại/mức mâu thuẫn hoặc mép đoạn chưa có bản bao đủ đều chặn bằng lỗi cố định. Gom đúng span, giữ từng lần xuất hiện, thay vị trí từ phải sang trái; không replace toàn cục. NFD/Cf/selector có kiểm biên trên cả gốc và bản dò. Sau che thêm chạy hậu kiểm cũ, kiểm tiền/ngày toàn văn và numeric review thực trước chốt kho.

Dùng nguyên kho alias/hàng chờ/CAS/chống lặp. Lô nghiệp vụ >100 lệnh bị từ chối toàn bộ, không chia lô. Kiểm lại quyền/nguồn/deadline trước và sau chốt, ghi chứng cứ Core gắn SHA kết quả cuối trước trả. Hủy/mất lease/sai nguồn/thiếu đoạn không phát hành; đã nhận chưa trả hoặc mất ACK ghi chứng cứ giữ `ChuaRo`. Lỗi/log không có gốc, trích dẫn, đường máy hoặc thông điệp tùy ý của port.

**Kết quả kiểm:** Windows x64, Python 3.13.14; SDK 2.0.0 cài offline từ wheel repo, SHA-256 khớp `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Venv trong worktree dùng pytest 9.1.1 có sẵn qua system-site-packages; không dependency runtime mới. Mọi lệnh Python dùng `-B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

| Lệnh với `.venv/Scripts/python -B` | Kết quả thật | Mã thoát |
|---|---|---|
| `-m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT**; cả hai lỗi “Chưa xác minh được phiên và quyền xử lý yêu cầu.” | 1 |
| `-m pytest e_mask/tests -q` | **1109 passed, 4 xfailed, 190 subtests passed in 128.47s (0:02:08)**; 0 skipped | 0 |
| `e_mask/tests/kiem_doc_lap.py` | **ĐẠT**, không tham chiếu bị cấm/tệp biên dịch | 0 |
| `e_mask/tests/chay_demo.py` | **2/2 ĐẠT** qua quyền/ngăn DEMO ngoài gói | 0 |
| `git diff --check` | Không lỗi khoảng trắng | 0 |

[Kết quả lệnh thật](KET-QUA-KIEM-MASK-2c-3.txt). Có **137 test mới** cho nguồn Core giả, ba loại thực thể, tên lớp 1 bỏ sót, Unicode/alias/lặp/overlap/mép đoạn, JSON rỗng thật/giả, Cloud trộn đoạn, giả mã/băm/quyền/nguồn/map, prompt injection, timeout/ChuaRo, CAS thực, giới hạn lô/rollback, mất ACK và thu hồi quyền giữa các cửa. Hai test danh sách năng lực cập nhật từ 3 lên 4; các test cũ và **bốn xfail strict held-out lớp 1 giữ nguyên**. Các lượt lỗi phát triển được ghi cùng kết quả cuối, không hạ chuẩn detector/trích dẫn để làm xanh.

**Thời gian thực tế:** 13:47:00–14:13:07 ngày 15/11/2026 (UTC+07), **0.44 giờ**; mốc bắt đầu lead giao **13:47:00 ngày 15/11/2026 (UTC+07)**. Phiếu **8 giờ ƯỚC TÍNH**, độ khó **kho**.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** Không vượt năm tệp mã. `CongHauKiemAI` và hình dạng tập nguồn là port nội bộ đề nghị, adapter RAM nằm ngoài gói; chưa phải API SDK/Core đã có. Model phản hồi phải khớp model đã ghim budget, khác model dù Local vẫn từ chối tới khi chuẩn bị/đo lại. Giữ ba lớp trần: profile 1 MiB/phản hồi và đầu vào cuối; snapshot/tập phản hồi 64 MiB/tệp; ngăn ≤100 lệnh/lô. Không thêm schema chung/bảng ngăn hoặc sửa nguồn cũ/Core/SDK/dependency. CLI chuẩn mã 1 được giữ trung thực; dùng cổng DEMO có quyền như các lát trước.

**Cần Core / Chờ Anh mới phát sinh:** Đã cụ thể hóa C-M2C-01…05 trong [VIEC.md](VIEC.md): nguồn/hoàn tất AI-9 tin cậy, kho tệp ACL xuyên bước, ghép đủ yêu cầu/phản hồi, deadline bất biến, chốt ngăn bền và chứng cứ kết quả cuối trước Cloud. **Cửa Cloud phải chặn đường lớp 1 cũ thiếu chứng cứ lớp 2**; BAT_CLOUD vẫn False. Không có câu chờ Anh mới. Chưa đo held-out hai lớp, model thật hoặc egress máy AI; không kết luận 0 lọt. MASK-2c-4 và nợ CAO giữ mở.
