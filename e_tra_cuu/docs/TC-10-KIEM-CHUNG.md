# TC-10 — biên bản DEMO và giới hạn nghiệm thu

Ngày **15/11/2026**, nhánh `codex/e_tra_cuu-tc-10`, PR **chờ lead mở**.
Bắt đầu **18:45** theo lead; kết thúc **15/11/2026 19:25:59 (UTC+07:00)**, **0.68 giờ**. Ước tính phiếu **4 giờ**.

**Kết luận: Chưa đạt cổng nghiệm thu chung — CLI chuẩn còn lỗi cấu hình/cửa
nguồn. Phần DEMO và adapter hợp đồng đã kiểm bằng Core giả (CoreGia).**

## Phạm vi và bằng chứng

Không sửa Python/JS runtime; không cache, RLS, runner hoặc cổng provider mới
trong engine. Giữ SDK 2.2.0, API v1, bốn schema và lock runtime chỉ SDK wheel
repo + thư viện chuẩn. Không thêm dependency/nguồn ngoài, không commit/push.

`demo/tc-10/` có 38 ca, nguồn bytes/băm thật và đáp án riêng. Generator nguồn
và đáp án dùng giá trị đặt trước, không gọi runtime/model; khi chạy test chỉ
đọc fixture đã ghim. Bộ có tám nhóm/ràng buộc 03/04, CP/TNHH, nhựa/điện chờ,
VAY-A/B, câu không đáp án, đổi bản/hiệu lực, nhân sự 07, mâu thuẫn và thời điểm.
Mỗi trích dẫn ghim nguồn/phiên bản/băm/quote/offset Unicode nửa mở.

| Chỉ số, đơn vị một ca | Tất cả | Nhóm 02 | Skip/chưa đo/lỗi chạy |
|---|---:|---:|---:|
| Trả lời đúng toàn bộ khẳng định/tiền/ngày/thực thể/nhãn | 12/12 | 11/11 | 0/0/0 |
| Trích dẫn đúng toàn bộ nguồn/phiên bản/băm/offset | 12/12 | 11/11 | 0/0/0 |
| Từ chối đúng, bỏ khẳng định/số bịa | 6/6 | 6/6 | 0/0/0 |
| Phân loại đúng hoặc hàng chờ có lý do | 20/20 | 2/2 | 0/0/0 |

Báo tử/mẫu từng chỉ số; không trung bình. Ca không áp dụng không thuộc mẫu
số của chỉ số đó; skip/chưa đo có số riêng, lỗi chạy tính không đạt. Các test
biến đổi đáp án kiểm bộ chấm thực sự bắt sai tiền/ngày/thực thể/nguồn/offset,
phân loại điểm model cao nhưng sai, từ chối còn số bịa và skip/chưa đo.

**Đây là số đo cơ chế trên fixture giả.** Chưa duyệt bộ câu hỏi nghiệp vụ,
chưa đo accuracy model thật hoặc hiệu chỉnh ngưỡng, không kích hoạt nhóm.
TC-Q15 đã duyệt nguyên tắc duyệt bộ/ngưỡng trước bật từng nhóm, nhóm 02 trước.
Điểm model tự khai không thay đáp án; `accuracy_model_that=null`.

## Kiểm đã chạy

| Lệnh / cổng | Kết quả thật |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu` | **0/12, mã 1**; 5 `CHUA_CAU_HINH`, 7 `TC_CHUA_CO_CUA_CORE` |
| `.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q` | **1330 passed, 0 skipped, 80.06 giây**, mã 0 |
| `.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py` | **ĐẠT**, mã 0; không import cấm/bytecode/liên kết |
| Harness `chay_demo_voi_core_gia.py` | **55/55** hồi quy; **38/38** ca theo đáp án, 31 lượt Local giả trong bộ chấm, **0 Cloud/mạng ngoài/provider thật**, mã 0 |
| `node --test e_tra_cuu/tests/ui/*.test.js` | **30 passed, 0 skipped**, mã 0; chỉ KttCore giả |
| `KIEM-MAY-SACH.cmd --bao-cao ...` | Windows: SDK offline/import riêng đạt, bytecode trong gói **0**; CLI **0/12/mã 1**, tạm đã dọn |
| `bash -n e_tra_cuu/tests/kiem_may_sach.sh` | Mã 0, **chỉ kiểm cú pháp qua Git Bash trên Windows** |

Kiểm kê **141/141 tệp** khớp bytes/SHA-256 nguyên trạng; `git diff --check`
không lỗi. Lượt toàn bộ đầu có 1329 đạt/1 lỗi vì kiểm kê cũ được đọc trong
lúc cập nhật fixture; sau cập nhật và cố định gói đã chạy lại đúng lệnh đầy
đủ, kết quả cuối ở bảng trên. Không bỏ hoặc skip test kiểm kê.

Harness giữ nguyên 12 ví dụ manifest, nạp cấu hình `dat_cau_hinh`, tệp con
và quyền qua adapter chỉ trong tests. Bảy ví dụ bổ sung có snapshot/AI Local/
giấy cấp/băm bytes đóng băng trong gói, bao phủ đủ tám năng lực. Tái nạp bằng
`them_tep` thật; không có ID/băm placeholder được nhận như nguồn có thật.
CLI chưa có cửa nạp fixture; không giảm ví dụ hoặc thêm default runtime.

Các chuỗi nhận → chuẩn bị → handler Hỏi AI/Local giả → hậu kiểm → xuất chạy
qua CoreGia. Cắt đoạn Python và tầng 1 không LLM có chuỗi riêng. Xuất JSON
giữ tiền tệ/ngày/offset/nguồn/snapshot; tệp/băm được tái kiểm. Bốn cặp số đo
được ghi qua `viec.ngan` vào bài `DEMO-TC10`, gửi lại không nhân số đếm.

Adapter hợp đồng kiểm thiếu/chưa duyệt/hết hiệu lực/thấp ngưỡng/ngoài trường
ở tầng 1 rồi mới tầng 2; tầng 3 trả 202 chờ, chạy callback nền sau. Cache chỉ
giữ tham chiếu, khớp pháp nhân/phạm vi/thực thể, kiểm mọi nguồn, hết hiệu lực
khi đổi phiên bản/nhóm/duyệt/công bố/thu quyền/hiệu lực; có bỏ qua cache và
không tái dùng câu phụ thuộc thời điểm. Nguồn ngoài quyền bị loại trước đọc
nội dung/dựng AI; M9/07 mọi nhánh Local. Chỉ **adapter test**, không chứng nhận
Core thật, RLS, cache, K5, HTTP nghiệp vụ hoặc điều phối nền thật.

Hủy/mất lease/mất ACK/hết lượt gửi lại không nộp XONG giả; gửi lại cùng khóa
không nhân ghi. Local đã nhận chưa trả giữ `ChuaRo` ở engine Hỏi AI sở hữu
lượt. Hai ca MayChuGia chạy tiến trình `app.chay` đọc bootstrap stdin, HTTP
loopback thật và xác thực đúng; thiếu cấu hình/cửa nguồn từ chối đúng.

## Chưa kiểm và Cần Core

- **C-TC-01/02/05:** nạp cấu hình/quyền/tệp con đúng cổng `thu` và dữ liệu
  tin cậy xuyên bước. Lead review fixture/loader bổ sung, không coi harness
  thay cổng chuẩn. Cấu hình/ngăn dùng SDK 2.2.0; NganBoNho lịch sử không
  đưa lại runtime, hai bản lưu trữ và bốn schema vẫn so băm CRLF→LF.
- **C-TC-03/04:** RLS/cache/runner/K5/quyền mọi nguồn/ngữ cảnh Local trên
  Core thật chưa kiểm; adapter giả chỉ là yêu cầu đối chiếu hợp đồng.
- **TC-Q15/L-TC-02:** bộ DEMO/ngưỡng thật chờ duyệt trước bật nhóm, TC-11
  đo Local thật do Anh chạy. TC-Q06 tiếp tục không tự xóa.
- Không có WSL/Linux nên chưa chạy Linux. `.sh` mới kiểm cú pháp. Venv máy
  sạch chỉ SDK; pytest/harness dùng dependency test đã ghim chạy riêng.
  Core/RLS/model/vector/trình duyệt thật, lưu bền, tải 20/150 người chưa kiểm;
  không tính các mục đó là đạt hoặc skip của bộ DEMO.
