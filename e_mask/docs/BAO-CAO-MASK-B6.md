# Báo cáo MASK-B6 — 16/11/2026

**Kết luận: Chưa đạt nghiệm thu chung — mã/kiểm nội bộ B6 đã xong; CLI chuẩn thiếu quyền Core, chuỗi tệp hai lớp/phát hành và Core/Office/Local thật chưa kiểm.**

**Đã làm:** thêm duy nhất `e_mask/goi/e_mask/e_mask/tep_excel.py` trong tối đa bốn runtime được giao. Che shared/inline/rich text/metadata và ô/hàng/cột ẩn trong profile B3; patch shared một lần nhưng kiểm mọi nơi dùng/unused, không ghép hai ô độc lập. Đọc lại bytes ra và kiểm index/style/merge/kích thước/epoch/lexical, kiểu và bytes ô số/tiền/ngày. Sheet cần đổi và các blocker ngoài profile chặn cả workbook. Số General/metadata số cần che bị chặn, không biến thành chuỗi. Nguồn 19/19 giữ nguyên, nguồn/symbol/quyền/SHA bytes và LF trước/sau ở NGUON; kiểm kê 55/55 cập nhật, không đổi manifest/mã migration/dependency.

Map chuỗi/ô/rich run/byte, alias nguyên văn, gốc và bytes chỉ trong RAM R4 đúng mã Core/scope/instance; tìm chính xác qua kho R2/R3, không matcher danh mục rõ. TTL 600 giây cấu hình 60–900, không trượt retry, dọn qua timer/lifecycle/tiêu thụ/lỗi; khóa ghi ngăn dựng lại map sau hủy/hết hạn. Spy không ghi map/gốc qua Core/ngăn/tệp tạm/upload/log/stderr/chuyển tiếp. Primitive chỉ trả băm/số đếm và `CHO_LOCAL`, không tự nhận đã qua Local hoặc phát hành tệp. **Đã kiểm bằng Core giả (CoreGia)**; chưa Core/Office/Local/Linux thật, Cloud tắt.

**Kết quả kiểm:**

| Lệnh / bộ kiểm | Kết quả |
|---|---|
| `kho_tri_thuc_sdk.thu e_mask/goi/e_mask` bằng `.venv/Scripts/python -B` | **0/2 ĐẠT, mã 1**; 0,97 giây. Hai DEMO thiếu quyền/ngữ cảnh tin cậy Core. |
| `pytest e_mask/tests -q` bằng `.venv/Scripts/python -B -m` | **2923 passed, 4 xfailed cũ, 190 subtests passed, 0 failed, 0 skipped; 441,10 giây; mã 0**. |
| `e_mask/tests/kiem_doc_lap.py` bằng `.venv/Scripts/python -B` | **ĐẠT, mã 0**; 0,72 giây. |
| `git diff --check` | **Mã 0**; chỉ cảnh báo CRLF checkout của VIEC/gold R3. |
| B6 riêng / B3+B4 nền | **122 passed, 23,08 giây** / **569 passed, 26,84 giây**, đều mã 0, không skip/xfail. |

Bốn xfailed strict MASK-2b cũ “giới hạn quy tắc, nợ CAO” giữ nguyên. B6 kiểm shared nhiều sheet/rich runs/inline/metadata/attribute/ô ẩn/số 0 đầu/tiền-ngày/format/bytes bất biến/blockers, reader sau patch, spy không lưu map, quyền chéo/restart/instance/TTL/tiêu thụ một lần/hủy/ChuaRo/race khi ghi RAM và biên 32.767/32.768 UTF-16 cả vào-ra. Không dùng số kiểm này để nhận độ phủ Local/Office thật đã đạt. [Nguyên lệnh/kết quả](KET-QUA-KIEM-MASK-B6.txt), [số đo lệnh](KET-QUA-KIEM-MASK-B6.json).

**Thời gian thực tế:** **04:02:00–04:35:09 ngày 16/11/2026 (UTC+07), 0.55 giờ** tại mốc chốt kiểm/báo cáo; phiếu **6–10 giờ ƯỚC TÍNH**, độ khó `kho`.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** chỉ một runtime mới, không vượt closure bốn tệp. Giữ trần đọc lại bảo thủ 500.000 ký tự của B1/B3/B4/B5, chưa mở đủ trần ra 2.000.000; vẫn kiểm bytes/ZIP/trần ô chiều ra, không truncate. Chuẩn hóa fixture gold R3 CRLF về nguyên blob Git LF/SHA đã khóa, không đổi gold/assertion/ngưỡng hoặc thêm skip/xfail. Môi trường `.venv` dùng pytest 9.1.1/jsonschema 4.26.0 có sẵn qua `--system-site-packages`; SDK 2.2.0 cài offline đúng SHA `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`, không thêm dependency. Bộ bọc log đầu lỗi tìm tên executable trên Windows trước chạy lệnh con; đã dùng `python.exe` đúng `.venv` và chạy đủ các lệnh yêu cầu. Lỗi fixture/encoding ở lượt B6 đầu đã sửa trong test mới, không hạ cửa quyền/Local/quy tắc.

**Cần Core / Chờ Anh mới phát sinh:** **C-P4-01** mã Core/ACL/ghim instance; **02** vòng đời khi rảnh, deadline/lease/tiêu thụ/ACK; **03** bí mật/băm/duy nhất/CAS/lô/quota và nợ chất lượng R3; **04** Local tin cậy đủ mọi vùng/đoạn, cả ngữ cảnh ô số/metadata, không snapshot/map phục hồi; **05** ACL tải/trả, streaming/413/budget RAM/CPU/thời gian/cách ly upload và không dump payload. Chi tiết ở [VIEC](VIEC.md). C-MS22-01 CLI thiếu quyền giữ mở. B7/B8/B9/B10 là các lát riêng; không có câu chọn nghiệp vụ mới chờ Anh.

**Không commit/push; PR: chờ lead mở.**
