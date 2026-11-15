# TX-6 — Biên bản bàn giao, 15/11/2026

Kết luận: **Chưa đạt kiểm chung trên checkout hiện tại** — phần công cụ,
chuỗi giả và venv mới đã kiểm; nguồn JSON E6 bị Git đổi CRLF làm sai băm,
CLI SDK chuẩn còn C-TX-04/C-TX-06. Không hạ cổng hoặc sửa nguồn chỉ đọc.
T3 **chưa đo**, N1 **chưa kiểm**; chưa thấy nền N1/model/cấu hình/biên bản
thật đã ghim trong worktree. Chưa chuyển bộ mặc định/lưu trữ.

## Phần đã thực hiện

- Hai chuỗi do CoreGia điều phối, ngăn DEMO nạp ngoài runtime: DOCX đọc
  bằng lõi thật hoặc PDF hợp lệ DEMO → OCR giả → chuẩn bị → Local AI giả
  → hậu kiểm → xuất `truong`. Kiểm schema, metadata/băm, đúng 37 mã,
  tiền còn đơn vị VND/ngày ISO, tải lại đủ JSON/Excel, snapshot không đổi
  khi bộ/cấu hình thay. Kiểm exporter có kiểu tiền/ngày được giữ trong bộ
  test TX-3; không tự chuyển bộ E1 thành kiểu chưa khai quy tắc.
- Node UI dùng KttCore giả; MayChuGia HTTP loopback cho tiến trình
  `app.chay()` đọc bootstrap stdin, hủy, mất phản hồi kết quả/kết thúc,
  retry cùng Idempotency-Key và chỉ ghi một lần trong Core giả.
- Hai công cụ T3/N1 và `.cmd` ASCII, chạy khô không mạng; discovery/transport
  tái dùng Hỏi AI, không gọi từ runtime Trích xuất. Không chạy `--that`.
  Kiểm thiếu cấu hình/số/nền, context trước gửi, cắt/từ chối/sai ID,
  `ChuaRo` dừng không gửi lại mù. N1 giữ `compare`/`da_do` của nguồn,
  kiểm ghim toàn bộ trước POST và có dấu nhận một lần theo băm nền.
- Nguồn/lock/SHA, cổng venv mới offline, mẫu nền chưa có số, mẫu biên bản
  và [checklist 17:00](TX-6-CHECKLIST-1700.md); phần Anh xem/bấm ≤30 phút,
  lead chạy trước phần chờ AI/OCR. **7 giờ công ước tính**, không gồm chờ
  máy/làm lại E6/batch. Công cụ b/c chỉ có đề xuất giờ riêng, chưa mở.

**đã kiểm bằng Core giả (CoreGia)**; NganBoNho/KttCore/OCR/Local giả chỉ
chứng minh đường ống. Chưa chứng nhận quyền module/pháp nhân, ACL, TTL,
lưu/đóng, ACK hay Core thật. **0 Cloud, 0 lượt Local AI/OCR máy thật**.

## Kết quả thực tế

Windows, Python 3.13.14; `.venv` kiểm dùng `--system-site-packages` để
dùng pytest 9.1.1/jsonschema 4.26.0 có sẵn và đã ghim. SDK 2.0.0 cài
wheel offline `--no-index --no-deps`, SHA-256 khớp
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Mọi Python dùng `-B`; pytest tắt tự nạp plugin. Không dependency mới.

| Lệnh / phép kiểm | Kết quả quan sát |
|---|---|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **3/5 ĐẠT, exit 1**; chuẩn bị thiếu cấu hình (`CHUA_CAU_HINH`, C-TX-04), hậu kiểm `DANG_CHAY` do thiếu tệp tham chiếu (C-TX-06) |
| `.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp-tx6-day-du-chot --tb=short` | **481 passed, 2 failed, 0 skipped in 26.23s, exit 1**; hai lỗi E6 sai băm do checkout CRLF đã có trước TX-6. **44 test TX-6 mới đạt**, không dùng staging thay hai test E6 nguồn thật |
| `.venv/Scripts/python -B e_trich_xuat/tests/kiem_doc_lap.py` | **ĐẠT, exit 0**; không bytecode/liên kết/import Core/kênh cũ trong gói |
| `.venv/Scripts/python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | **5/5 ĐẠT, exit 0**; nạp cấu hình DEMO qua ngăn và bytes hồ sơ, chạy đúng mẫu/handlers thật |
| `node --test e_trich_xuat/tests/ui/cau_hinh.test.mjs` | **6/6, 0 failed/skipped, exit 0** |
| `.cmd` T3 chạy khô | **9 tải/model, exit 0**, Local giả; [artifact](TX-6-T3-CHAY-KHO.json); T3 chưa đo |
| `.cmd` N1 chạy khô với staging test LF đúng băm | **2 ca, exit 0**, không tiêu thụ lượt N1; [artifact](TX-6-N1-CHAY-KHO.json); N1 chưa kiểm |
| `tests/kiem_may_sach.cmd` mặc định | **exit 1**: venv mới cài SDK/DEMO/T3 khô được, N1 từ chối nguồn JSON E6 sai SHA do CRLF |
| `tests/kiem_may_sach.cmd --bo-demo <staging-test-LF>/chap-nhan.json` | **exit 0**; venv mới, không system-site-packages/pytest/jsonschema; wheel/lock offline, SHA, độc lập, DEMO ngăn 5/5, T3/N1 khô; vẫn báo CLI chuẩn exit 1 riêng |
| `bash -n e_trich_xuat/tests/kiem_may_sach.sh` | **exit 0**, chỉ kiểm cú pháp shell trên Windows |
| Linux / CI / máy Windows OS sạch | **Chưa kiểm**; WSL chưa cài, không có Docker. Venv mới không được gọi là máy OS sạch |

## Chặn môi trường đã giữ nguyên

`core.autocrlf=true` đổi 82 dòng JSON vàng thường thành CRLF:

- SHA bytes hiện tại: `f3b521b77bba129a202b4b95b8f9f5928bf1f9fbdb430e2404575ac972612f2b`.
- SHA blob LF đã ghim: `25972ccba8878c293e830dcb37b0aef4a08ab23af50f4538eb7aad0f92deaaca`.

Các JSON tham số/vàng/băng AI còn lại cũng bị đổi xuống dòng. DOCX và
XLSX giữ đúng SHA. E6 hiện hành trên checkout thật trả **exit 3**, “Nguồn
đối chiếu không khớp mã kiểm tra.” Hai test E6 nguồn thật thất bại.
Không sửa fixture, băm, `kiem_e6.py` hoặc tiêu chí đã chốt. Đã báo lead
để phục hồi đúng bytes LF. Test riêng TX-6 staging các bản đúng bytes LF
và so lại băm đã ghim trước chạy khô; staging không là nghiệm thu E6.

## Phạm vi và phần chờ

Đúng **5 tệp mã ngoài tests/tài liệu**: ba Python trong `cong-cu/` và hai
`.cmd`. Runtime/manifest/schema/ngăn/cấu hình chung/Core/SDK/nguồn cũ
giữ nguyên; `requirements.lock` giữ SDK 2.0.0, không dependency runtime
mới. Không sửa nguồn tham chiếu, không xóa tệp, không commit/push.

C-TX-04/C-TX-06: lead review cổng DEMO có ngăn/hồ sơ thay thế, Core/SDK
cần cửa tương ứng cho CLI/màn DEMO chung; không nói CLI chuẩn đã đạt.
C-TX-01/02/05 và A-TX-01 vẫn mở như trước. Nền N1/máy thật và phục hồi
bytes checkout thuộc phần lead/Anh cần cung cấp; thiếu thì công cụ từ
chối, không tạo cấu hình runtime hoặc nền giả. Thời gian và kết quả kiểm
cuối ghi tại [VIEC.md](VIEC.md), PR: **chờ lead mở**.

Thời gian thực tế: **15/11/2026 13:09–14:01 (UTC+07), khoảng 0,87 giờ**
so với **7 giờ công ước tính**. Không chờ máy AI/OCR, không làm lại E6/batch.
Rà AST/JSON/ASCII/BOM trên 19 tệp mới đạt; SHA nguồn chung/nguồn cũ giữ
nguyên, `git diff --check` exit 0. Nhánh `codex/e_trich_xuat-tx-6`.
