# MASK-B7 — hai lớp Local cho tệp, trạng thái chỉ RAM

Ngày 16/11/2026; PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia); chưa Core/Office/Local/Linux thật. Cloud tắt, không gọi/import engine khác, không dependency mới, không commit/push.

## Phạm vi và điều kiện

Đúng năm tệp mã/khai báo: `ho_so_tep.py`, `chuan_bi_tep.py`, `hau_kiem_tep.py`, `chay.py`, `engine.json`. Tái dùng B1…B6/R4/R5; không sửa phần văn bản R5, không thực hiện B8/B9. Gói tăng 1.4.0 → 1.5.0, giữ API v1/SDK 2.2.0/schema chung và bốn năng lực văn bản hiện hành.

Ba năng lực:

| Năng lực | Nhận → trả |
|---|---|
| `mask.chuan_bi_tep_ai_cuc_bo@1` | `tep` → `yeu_cau_ai` |
| `mask.hau_kiem_tep_van_ban@1` | `tra_loi_ai` → `van_ban_da_che` |
| `mask.hau_kiem_tep_giu_dinh_dang@1` | `tra_loi_ai` → `truong`, đúng bộ C |

Chuẩn bị nhận tệp trực tiếp hoặc JSON mẫu 5 `{tep, dinh_danh_da_biet?}`. Không thêm cờ quyền/dạng trả vào mẫu hoặc Cài đặt bước: port `dang_tra` của Core đã xác thực lựa chọn module/quy trình, ghim `van_ban|tep` và năng lực hậu kiểm trong RAM; gọi sai năng lực cuối bị chặn. Tệp con chỉ được đọc bằng `mo_tep`; CoreGia chuẩn chưa cấp quyền tệp con, fixture `CoreTepGia` cấp rõ quyền theo việc ở ngoài gói.

## Vòng đời và dữ liệu

`HoSoTepRAM` chỉ adapter quyền sở hữu của đúng kho R4 thuộc app. Bytes gốc/bản che, đối tượng reader/map/patch, gốc Unicode, bản quy tắc, kế hoạch/băm/phiên bản/dạng trả và phản hồi Local không ra ngăn/kho tệp/hồ sơ/tệp tạm/log/stderr/chuyen_tiep. Không kho RAM thứ hai hoặc snapshot dự phòng. R4 kiểm mã Core cấp, scope và instance xuyên bước; một chuỗi sống, một bước sở hữu, TTL từ `viec.cau_hinh` chụp đầu chuỗi, deadline Core nếu sớm hơn. Retry/đổi cấu hình không trượt hạn; timer và sự kiện Core dọn cả khi chờ AI.

Sau chuẩn bị, handler nhường lượt. Core giao từng đoạn Local và tập phản hồi tạm qua port. Chỉ đoạn `yeu_cau_ai.tai_lieu` cần thiết được bàn giao Local; không chuyển kèm hồ sơ/map hoặc bản che quy tắc. `chuyen_tiep.mask_2c` giữ đúng allowlist R5/AI-9: mã RAM, băm, chỉ số/biên đoạn và profile. `ho_so` có hình dạng metadata `ram-…` tương thích R5, **không có tệp tương ứng** và không dùng để tải/khôi phục.

Hồ sơ R4 giữ map các vùng reader B2/B3 và băng nguyên văn có ranh giới. Băng gồm mọi vùng chữ/attribute/metadata, cả nơi dùng shared string; thêm ngữ cảnh hàng cho ô bất biến Excel và scalar metadata của hai định dạng. Không chấp nhận thực thể đi qua hai vùng/ô hoặc sửa scalar không có miền patch. Scalar số metadata có dấu hiệu định danh bị lớp 1 chặn; Local nhận diện tên không thay lớp số/MST/tài khoản.

## Kiểm và phát hành

Tái dùng `lap_ke_hoach`, khuôn/profile/budget R5 và kiểm phản hồi/span của MASK-2c: 8.000 code point/đoạn, overlap 512, ≤128 đoạn, span ≤300, phản hồi/nguồn Local/hoàn tất/trích dẫn đúng từng đoạn. Nguồn giả, thiếu/trùng/đảo đoạn, offset sai, nghi vấn, cắt đầu ra, profile hoặc input đổi đều không phát hành. Python kiểm cả span đi qua ranh vùng, alias lớp 1, tiền/ngày và nhóm. AI chỉ thêm che bằng vị trí gốc qua primitive B5/B6; không gỡ chặn lớp 1.

Reader/writer B5/B6 đọc lại bytes thật, so map từng vùng và bytes/kiểu/style/tiền/ngày/ô số trước tạo kết quả/chốt metadata/upload. Kiểm tiền/ngày cuối áp chính sách nhãn số dạng ngày B5b, kể cả Excel. Giữ trần ZIP/XML/B1/B4 và báo cáo ≤256 KiB; bộ C tính trước kích thước tham chiếu tối đa trước chốt. Băng Local tính cả vùng lặp/ngữ cảnh vào 500.000 ký tự, có thể chặn sớm hơn tổng ký tự reader; reader đầu ra B5/B6 còn bảo thủ 500.000. Trần 2 triệu ký tự/8 MiB đầu ra không phải cam kết mọi tệp tới biên đều nhận được; B10 còn phải đo.

Ngăn R2/R3 tiếp tục chỉ tìm chính xác từng ứng viên, đọc metadata/null+cờ. Tên mới thiếu bảo đảm C-P4-03 vẫn bị chặn, không tạo alias tạm/ngăn rõ để làm xanh bài kiểm. `chot_metadata` là protocol đề nghị, chỉ nhận ID/alias/nhóm/row_version, tối đa 100 mục và chứng cứ băm bản cuối. Adapter CoreGia giả lập chống lặp và CAS/lô qua `viec.ngan`, chỉ tăng metadata số gặp một lần; **chưa có binding giao dịch/ACK này trong Core/SDK thật**, không coi fake là hoàn tất C-P4-03.

Sau xác nhận, bản che giữ định dạng upload bằng tên `mask-da-che.docx|xlsx`; không upload bản gốc/map. Core phải cách ly upload và kết quả tới sau chốt SDK, còn quyền/lease/hạn. ChuaRo khi chờ phản hồi/chứng thực Local giữ map còn hiệu lực; lỗi xác định dọn. Mất ACK chốt metadata/upload/bàn giao cuối → ChuaRo, dọn map, không chốt lại/tái tạo kết quả bằng map mới. Retry ACK SDK cùng Idempotency-Key không chạy handler lần hai. Sau hậu kiểm thành công, map cuối còn RAM cho R6/B8 cùng chu kỳ; sự kiện kết thúc hoặc TTL dọn ngay, không mở lại ngày sau.

## Cần Core và giới hạn nghiệm thu

- **C-P4-01/02:** mã yêu cầu/ACL/instance và phiên RAM tin cậy, ghim mọi bước, một chuỗi sống; sự kiện hủy/lỗi/lease/deadline/kết thúc khi Mask rảnh; bàn giao đồng bộ và không chạy lại sau tiêu thụ. Thiếu thì runtime từ chối.
- **C-P4-03:** chỉ mục băm/chuẩn hóa/duy nhất bí mật, quota dò, giao dịch metadata CAS/chống lặp xuyên lần giao/ACK. Không ghi ứng viên/map vào log hoặc dấu chống trùng; không giải mã. R3 chưa chứng minh chất lượng/chi phí, tên mới tiếp tục bị chặn.
- **C-P4-04:** điều phối đủ đoạn của băng Local, đo token thật gồm prompt/khuôn/input/output, xác thực nguồn AI-9 và băm tập phản hồi, kiểm tệp nguồn không đổi. Không cất hồ sơ gốc/map để khôi phục. Đã đọc đối chiếu allowlist/băm/offset/khuôn của `e_hoi_ai/hoi_mask.py`; B7 không gọi/import/sửa engine đó và chưa chạy AI-9/model thật.
- **C-P4-05:** quyền tệp con xuyên bước, streaming/trần trước SDK tải trọn RAM/413, budget CPU/RAM/thời gian chuỗi, cách ly và thu hồi upload mất ACK, không dump payload/traceback/crash/tệp tạm. CoreGia không chứng minh ACL/affinity/egress thật.
- Kiểm kê `sql/kiem_ke.json` ngoài đúng năm tệp được giao: giữ nguyên, sinh bản **đề nghị ngoài gói** cho lead áp dụng. Lệnh kiểm độc lập và test kiểm kê trên gói hiện tại phải báo lỗi thật cho tới khi lead cập nhật.

Không gọi kết quả là “0 lọt” hoặc nghiệm thu model/Office/Core thật. B8 mở tệp, B9 binding/bàn giao và B10 held-out/biên/Office/Local còn riêng. Không có câu chọn nghiệp vụ mới chờ Anh.

Kết quả lệnh và thời gian chốt được ghi tại mục MASK-B7 cuối `VIEC.md`; log từng lệnh ở các tệp `KET-QUA-KIEM-MASK-B7-*.txt`.

Kết quả chốt: B7 142/142; mục tiêu 146 passed; full 3244 passed, 1 failed kiểm kê, 4 xfailed cũ, 190 subtests, 0 skipped. CLI 0/2 mã 1 thiếu quyền; độc lập mã 1 cùng kiểm kê; bản đề nghị 58/58 đối chiếu đạt; diff mã 0. Mốc chốt kiểm 05:56:03 ngày 16/11/2026, từ 05:06:00 là 0,83 giờ; phiếu 8–10 giờ ƯỚC TÍNH. Đã kiểm bằng Core giả (CoreGia); chưa Core/Office/Local/Linux thật. PR: chờ lead mở; không commit/push.

Thời gian thực tế chốt bàn giao: 05:06:00–05:57:44 ngày 16/11/2026 (UTC+07), 0,86 giờ; các lệnh kiểm chốt trước đó lúc 05:56:03.
