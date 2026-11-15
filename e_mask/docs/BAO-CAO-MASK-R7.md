Kết luận: **Chưa đạt nghiệm thu chung** — MASK-R7 hoàn tất phần adapter/UI kiểm giả, full pytest xanh; CLI SDK chuẩn còn thiếu quyền tin cậy và C-P4-06 chưa nối Core. PR: **chờ lead mở**.

Đã làm:

- Đúng hai runtime theo MASK-P4 §4: `e_mask/duyet_dinh_danh.py`, `ui/duyet_dinh_danh.js`. UI `KttCore.engine("e_mask")` chỉ hiện ID/alias/nhóm/trạng thái/số gặp; không tên/lọc tên một phần hoặc ghi ngăn trực tiếp. Biên nhận chỉ opaque ID/phiên bản, không callback/export tên. Thiếu cửa/quyền/vé hoặc phiên đổi thì không duyệt.
- Duyệt/từ chối dùng quyền tin cậy kiểm cả quyền xem và duyệt, gắn phiên/vùng/ID/row_version và vé một lần; yêu cầu giữ quyền trong lô CAS. Primitive R2 sửa trạng thái cùng ID, thêm alias metadata duy nhất Junsky/MASK; không sao bí mật sang bảng khác, không null/cờ đè bí mật, không xóa. RAM R4 của chuỗi đang chạy giữ nguyên. Mất ACK/lỗi cửa sau ghi trả ChuaRo; không báo thành công hoặc tự gửi lại.
- Port `bien_nhan_duyet` và hai lệnh chung đề nghị qua `engine.thao_tac` chỉ kiểm bằng adapter ngoài gói, **không phải API/handler SDK đã đăng ký**. Không sửa manifest, Core/SDK/dependency hoặc mở API giải mã. C-P4-06 cần Core/lead chốt binding; runtime từ chối nếu chưa có.
- Logic Admin RAM cũ chuyển sang fixture test ngoài gói; sáu test/công cụ DEMO chỉ đổi import, AST 6/6 giữ nguyên mọi assertion cũ. Các test này kiểm hồi quy lịch sử, không chứng minh runtime R7; bộ mới kiểm riêng runtime R7 trên NganEngine/CoreGia thật với null+cờ. Không mạng ngoài/eval/HTML chưa lọc/storage/log.

Kết quả kiểm:

| Lệnh | Kết quả thật cuối |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**; cả hai “Chưa xác minh được phiên và quyền xử lý yêu cầu.” Kế thừa C-MS22-01, không bỏ cửa quyền để làm xanh. |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **2412 passed, 4 xfailed, 190 subtests passed, 0 failed, 0 skipped**, 241,42 giây, mã 0. Bốn xfail strict cũ “giới hạn quy tắc, nợ CAO” giữ nguyên. |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **ĐẠT, mã 0**, không tham chiếu cấm/bytecode/symlink trong gói. |
| `git diff --check` | **Mã 0**. |
| R7 + wrapper UI | **50 passed**, 2,26 giây, mã 0; gồm 49 Python + wrapper Node. Node trực tiếp **26/26**, không skip. |
| Kiểm kê | **52/52 tệp bytes LF + SHA-256**, trừ chính kiểm kê. |

Đã kiểm bằng Core giả (CoreGia) và KttCore giả; **chưa UI Core thật**, chưa ACL/Core/Local/Office/Linux thật. Test gồm null+cờ, thiếu quyền xem/duyệt/cửa/vé, vé sai ID/phiên/vùng/cờ tự khai, XSS/tên không DOM/log, CAS/alias trùng/rollback/hai Admin đồng thời/replay/thu hồi quyền/lỗi sau ghi/mất ACK, và RAM R4 không đổi sau Admin duyệt. Venv trong worktree, SDK 2.2.0 cài wheel offline (SHA khớp), có jsonschema 4.26.0; mọi Python dùng `-B` và tắt bytecode.

Lượt full đầu: **1 failed, 2403 passed, 4 xfailed, 190 subtests passed**, 231,47 giây, mã 1; lỗi duy nhất do fixture R3 checkout 42 CRLF. Chỉ khôi phục LF đúng nguyên blob Git và gold SHA `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; không thay dữ liệu/hash kỳ vọng/assertion. Lượt đầu thu thập trước khi thêm tám ca R7 cuối; lượt chốt gồm đầy đủ. Dòng trắng CHANGELOG phát hiện ở diff đã sửa, kiểm kê tính lại. [Lệnh/kết quả thật](KET-QUA-KIEM-MASK-R7.txt).

Thời gian thực tế: **22:17:00–22:37:37 ngày 15/11/2026 (UTC+07), 0.34 giờ**, mốc chốt kiểm và hồ sơ; phiếu **3–5 giờ ƯỚC TÍNH**, độ khó `vua`.

Lệch khỏi phiếu / quyết định tạm đã dùng: ngoài hai runtime có test/tài liệu và `sql/kiem_ke.json` tự sinh bắt buộc, đúng lệnh lead. Tách fixture hồi quy RAM để không để lại đường Admin RAM/chép/xóa bí mật trong gói. `cong-cu/chuyen_danh_muc_demo.py` lịch sử ngoài closure còn gọi `nhap_demo` đã bỏ, chưa chuyển công cụ; không dùng nó cho migration. Không tự thêm fallback/route/giải mã, không đổi nghiệp vụ hoặc nới kiểm an toàn.

Cần Core / Chờ Anh mới phát sinh: **C-P4-06** còn mở cho Xem dữ liệu chung, biên nhận không tên đúng phiên/người/vùng/ID/phiên bản/quyền xem+duyệt, chống replay/hết hạn/thu hồi, giữ quyền với CAS/ACK và binding hai lệnh chung/handler R7; migration dữ liệu cũ do Core/lead bảo vệ. Kế thừa **C-P4-03** và **C-MS22-01**, không nhận các bảo đảm bí mật/Core thật chỉ từ test metadata. Lead cần bảo đảm LF fixture R3 khi checkout để giữ kiểm SHA bytes; đây là vấn đề môi trường đã kiểm chứng, không đổi gold. Không có câu Chờ Anh chọn lại. Không commit/push, không sửa Core/SDK/dependency.
