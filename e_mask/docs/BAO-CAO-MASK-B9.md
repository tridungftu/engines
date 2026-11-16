# Báo cáo MASK-B9 — 16/11/2026

**Kết luận: Chưa đạt nghiệm thu chung** — xong mã và 131 ca mục tiêu B9; full còn hai lỗi hiệu năng/kiểm kê, CLI thiếu quyền Core. PR: **chờ lead mở**.

**Đã làm:** đúng năm tệp mã/phiếu, gói 1.6.0. Ba năng lực tệp B7 giữ loại trả cố định; thêm `mask.mo_che_tep@1` mẫu 7 → bộ T. Bảy định nghĩa năng lực cũ, API v1 và schema chung giữ nguyên; không đường che tệp bỏ Local.

- Mẫu 5/7 kiểm UTF-8/JSON nghiêm ngặt, khóa trùng, NaN/Infinity, độ sâu và trần, allowlist khóa/danh sách định danh; kiểm từng tham chiếu con 1 MiB, MIME/đuôi/bytes và quyền Core. Không path/URL, danh tính caller, tự đọc đĩa hoặc nguồn chứng thực từ payload. Tệp PDF/scan ngoài loạt B; OCR do Core điều phối, không gọi OCR/Cloud.
- Chốt metadata bằng chính `viec.ngan`: kiểm ID/phiên bản/alias với dữ liệu null+cờ, chỉ tăng số gặp trong một lô CAS ≤100. Core giữ quyền/dấu chống lặp, callback ghi đồng bộ đúng một lần. Vượt 100 từ chối trước ghi, CAS không ghi dở, không chia lô giả nguyên tử; ACK sau ghi chưa rõ không chốt lại.
- Mở bằng primitive B8 dưới handle RAM R4 của đúng chuỗi/instance, kiểm toàn bytes và tiền/ngày/trần trước upload. Tên đầu ra cố định `mask-da-mo-che.docx/xlsx`, bộ T đủ trường; bản che bộ C và `van_ban_da_che` chỉ mang chuỗi che vẫn theo B7. Nhánh đã phát hành văn bản không được caller chuyển thành tệp chưa từng phát hành.
- Cách ly upload bắt đầu trước byte đầu, bàn giao sau tiêu thụ RAM; B7 giữ cách ly qua biên nhường handle. Kiểm quyền/lifecycle/instance/deadline cả sau context bàn giao. Hủy/lỗi/TTL/mất RAM/alias thiếu-lạ-hỏng-mơ hồ không phát hành mở dở. `dong_viec=false` vẫn dọn; không map hoặc cache bản rõ để retry. Mất ACK sau tiếp nhận báo ChuaRo; Core giao lại kết quả đã tiếp nhận đúng quyền, không chạy mở lại.

Đã kiểm bằng Core giả (CoreGia), gồm HTTP qua MayChuGia và Local/AI sửa tệp giả. **Chưa Core/Office/Local/Linux thật**; Cloud tắt, chỉ DEMO, không thêm dependency, không engine-to-engine, không commit/push.

**Kết quả kiểm thật:**

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**: cả hai DEMO thiếu nguồn phiên/quyền tin cậy. Nợ C-MS22-01 cũ, không nới gate. [Log](KET-QUA-KIEM-MASK-B9-SDK.txt) |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | **3996 passed, 2 failed, 4 xfailed cũ, 189 subtests passed, 0 skipped; 915,85 giây; mã 1**. Một subtest hiệu năng cũ `'1 '` mất 5,068 giây so với ngưỡng 5; một lỗi kiểm kê ngoài closure. [Kết quả thật](KET-QUA-KIEM-MASK-B9-PYTEST.txt) |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | **Mã 1**, kiểm kê thật chưa khớp gói. [Log](KET-QUA-KIEM-MASK-B9-DOC-LAP.txt) |
| B9 tệp + đầu dò ngăn SDK | **131 passed, 31,47 giây, mã 0**, không skip/xfail; gồm HTTP giả, mẫu 5/7, quyền/caller/instance/restart/lifecycle/TTL, ACK/partial upload, lô 0/1/100 và chặn 101, CAS và callback ghi hai lần/không ghi. |
| B7 hồi quy sau nối lô SDK/cách ly | **142 passed, 36,47 giây, mã 0**, không skip/xfail. Full suite là kết quả chốt sau các bổ sung cuối. |
| Kiểm kê đề nghị ngoài gói | **60/60** bytes/SHA khớp; cùng checker độc lập đạt khi chỉ thay kiểm kê trong RAM. Không sửa `sql/kiem_ke.json`. [Đề nghị](KIEM-KE-MASK-B9-DE-NGHI.json), [đối chiếu](KET-QUA-KIEM-MASK-B9-KIEM-KE-DE-NGHI.txt) |
| Nguồn/phạm vi | **4 nguồn giữ nguyên LF**, AST bốn runtime hợp lệ; đúng năm tệp mã/phiếu, bảy năng lực cũ giữ nguyên định nghĩa. [SHA nguồn/đích](SHA-NGUON-MASK-B9.json) |
| Kiểm lại riêng ca hiệu năng | **1 failed, 1 passed, 2 subtests passed; 17,91 giây; mã 1**. Mẫu `'1 '` mất **5,231 giây**, vẫn vượt 5; mã che/test/ngưỡng giữ nguyên. [Kết quả riêng](KET-QUA-KIEM-MASK-B9-HIEU-NANG-RIENG.txt) |
| `git diff --check` | **Mã 0**, chỉ cảnh báo Git LF→CRLF, không lỗi khoảng trắng. [Log](KET-QUA-KIEM-MASK-B9-DIFF.txt) |

Giữ bốn xfailed strict MASK-2b cũ về giới hạn quy tắc/nợ chất lượng, không thêm skip/xfail hoặc nới gold/ngưỡng. Fixture R3 chỉ trả CRLF checkout về nguyên blob Git LF, SHA khóa `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; nội dung vàng không đổi. Lượt mục tiêu đầu phát hiện lỗi seed test khi tạo app và khe lifecycle sau tiêu thụ; đã sửa và chạy lại, không gộp lượt lỗi thành số đạt. Ca hiệu năng tái hiện khi kiểm riêng; chưa xác định nguyên nhân hoặc chứng minh hồi quy so với nền, không loại failure khỏi báo cáo full.

**Thời gian thực tế:** **10:31:00–11:17:55 ngày 16/11/2026 (UTC+07), 0,78 giờ** tại mốc chốt kiểm/báo cáo; phiếu **4–8 giờ ƯỚC TÍNH**, độ khó `kho`. Bắt đầu theo lead; gồm đọc tài liệu, dựng môi trường, triển khai, sửa/kiểm test và chốt hiện vật, không gồm Core/Office/Local thật.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** không vượt năm tệp mã/phiếu. Kiểm kê ngoài closure chỉ sinh đề nghị ngoài gói cho lead nên chưa đạt đóng gói chung. Parser thêm trần kỹ thuật JSON sâu 64/node 100.000 trong trần bytes; không nới profile B hoặc TTL. Protocol chốt/bàn giao là đề nghị C-P4, chưa phải binding SDK/Core đã có. Không đổi các quyết định nghiệp vụ cũ về tiền/ngày, không tự nhận budget production hay chất lượng Local/Office.

**Cần Core / Chờ Anh mới phát sinh:** C-P4-01/02/03/04/05 và C-MS22-01; chi tiết binding/cách ly/quyền/ACK ở mục [Cần Core B9 trong VIEC](VIEC.md). Core cần xác nhận quyền tệp con, ghim/lifecycle và bàn giao qua các biên SDK, streaming/trần/413/budget OS, không dump payload/traceback/map. Lead cần xử lý riêng ca hiệu năng mã cũ ngoài năm tệp B9, áp dụng kiểm kê đúng bytes sau gộp, commit và mở PR. Không có câu nghiệp vụ mới chờ Anh chọn lại; mở muộn/tra toàn kho phải chuyển sang chuỗi RAM dùng một lần, không đổi đầu ra thành phương án A/tham chiếu.

Môi trường: Windows, Python **3.13.14**, `.venv` tại worktree dùng công cụ test hệ thống đã ghim; SDK **2.2.0** cài offline `--no-index --no-deps` từ wheel repo. SHA-256 wheel **0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984** khớp phát hành. Python chạy `-B`, không bytecode trong gói.
