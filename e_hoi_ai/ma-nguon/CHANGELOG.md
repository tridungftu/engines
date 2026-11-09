# CHANGELOG — e_hoi_ai

## AI-LAT8-CHUAN-BI — 08/11/2026

- Thêm công cụ thử ba model Local qua cổng AI chung, mặc định chạy khô,
  khóa Cloud và có ca mất kết nối, để lead kiểm khả năng phục vụ của máy AI.
- Kèm tệp `.cmd` ASCII để mở công cụ trên Windows; phần chuẩn bị đã gộp
  chưa phải bằng chứng nghiệm thu model Local thật hoặc toàn luồng Core.

## Chuỗi Hỏi AI bản 1 — 08/11/2026

- Hoàn tất ghép chuỗi trên contract v2 đã có, ghim function, prompt/phiên
  bản và nguồn do Core xác minh theo pháp nhân; giữ v1 tương thích, trả
  “Không thấy căn cứ” khi thiếu cơ sở để câu trả lời bám đúng hồ sơ.
- Runtime nhận việc qua kênh engine chuẩn, giữ lease và bàn giao kết quả
  đến khi Core xác nhận, tránh gọi AI lại khi chỉ mất phản hồi bàn giao.
- Chọn model Local theo module/function với ưu tiên và dự phòng; bỏ
  model tắt/mất, chế độ Cố định không tự chuyển. Readiness và runtime
  dùng chung quy tắc trên discovery mới để chọn đúng model còn sẵn sàng.
- Ghi provenance gồm module/function, prompt/phiên bản, model, lý do chọn
  và kết quả kiểm; chống trùng khi phát lại, không ghi nội dung prompt
  hoặc câu trả lời vào nhật ký, để truy vết mà không lưu nội dung hồ sơ.
- Bản 1 chỉ Local; mã đã gộp và kiểm thuần/mock chưa chứng minh model
  Local thật hoặc toàn luồng đã nghiệm thu, chưa mở Cloud.

## AI-LAT3 vòng 4 — 08/11/2026

- Manifest được đọc tối đa 64 KiB + 1 byte; thiếu/hỏng/sai phiên bản
  chặn readiness bằng `AI_GOI_HONG_PHIEN_BAN` với thông báo “Gói Hỏi AI
  hỏng phiên bản.” Import không văng lỗi đọc/JSON thô; không tạo worker
  hoặc cổng AI khi gói hỏng, vẫn thu hồi tài nguyên bootstrap.
- `NGUON.md` có bảng SHA-256 bytes thực của 14 tệp hiện hành: mã Python,
  toàn bộ `lib/`, manifest, contract, pyproject và lock; loại tests/cache.
  Kiểm bảng đầy đủ, băm 64 ký tự và mutation đổi một byte ở từng tệp.
- Ghi rõ yêu cầu SDK Python >=1.5.0 trong NGUON/pyproject; giữ cách Core
  cấp SDK, không thêm dependency hoặc đổi SDK. Mẫu OCR chưa nêu mức SDK
  tối thiểu và chưa có pyproject; lead đối chiếu artifact đã duyệt.

| Mốc thuần/mock | ok | fail | error | skip |
|---|---:|---:|---:|---:|
| Trước sửa vòng 4 | 197 | 0 | 0 | 0 |
| Sau sửa, cùng bộ + 7 ca mới | 204 | 0 | 0 | 0 |

Bộ chạy bằng Python/PYTHONPATH của handoff: `test_g3_ai_1a`, `1b`, `2`,
hai lớp thuần/mock `test_g3_ai_4a.AIThuanTest`/`AIRuntimeV2Test`,
`test_g3_ai_4b`, `5b`, `test_g3_goi_ai_loi`, `test_g3_goi_ai_mau`,
`engines.e_hoi_ai.tests.test_doc_lap` và `test_goi_hoi_ai`. Không chạy
lớp Windows mở listener thật, PostgreSQL, server hoặc toàn bộ nền v6.
Không có lỗi/skip mới trong phạm vi đã chạy. Lead giữ đúng bytes CRLF/LF
khi đóng gói; bảng băm không chuẩn hóa xuống dòng.

## AI-LAT3 — 08/11/2026 (0.1.1-demo.1)

- Đồng bộ metadata `0.1.1.dev1` (PEP 440) với manifest `0.1.1-demo.1`;
  readiness đọc phiên bản từ manifest trong gói, không giữ hằng riêng.
- Khai báo hai package engine/lib và dữ liệu cần phân phối; giữ nguyên
  contract v2, adapter, cổng Local và cơ chế kiểm model trước readiness.
- Thêm `requirements.lock` cho closure SDK đã đo: cryptography 49.0.0,
  cffi 2.0.0, pycparser 3.0; ghi lý do, giấy phép và giới hạn môi trường.
  Không cài/nâng thư viện, đổi SDK hoặc ghim wheel 1.4.1 candidate.
- Bổ sung kiểm đóng gói thuần/mock theo mẫu OCR: ranh giới import,
  metadata/lock và readiness; không gọi AI, PostgreSQL hoặc server thật.
- Chưa build/cài wheel độc lập: runtime thiếu setuptools và SDK wheel
  được duyệt; chưa nghiệm thu model Local thật hoặc vận hành Core.

Kiểm trước/sau bằng Python 3.13.14 và PYTHONPATH của handoff, chỉ
thuần/mock (không PostgreSQL/server):

| Mốc | ok | fail | error | skip |
|---|---:|---:|---:|---:|
| Trước sửa, 9 module liên quan | 193 | 0 | 0 | 0 |
| Sau sửa, cùng bộ + 14 ca đóng gói mới | 207 | 0 | 0 | 0 |

Readiness: Bootstrap thật dùng JSON trong RAM, provider/vòng nhận việc
giả; kiểm phiên bản từ manifest, đổi phiên bản trong RAM, contract v2,
DEMO không công bố contract thật và model chưa sẵn sàng bị chặn.
Không có lỗi/skip mới trong phạm vi đã chạy; không chạy toàn bộ nền v6.

## 0.1.0-demo.1 (G3-GOI-01, 05/11/2026)
- Chuyển nguyên trạng `bi_mat.py`, `chay.py`, `dto.py`, `hoi.py`, `nhat_ky.py`, `engine.json` từ `src/kho_tri_thuc/engines/e_hoi_ai/` sang `engines/e_hoi_ai/` (git mv, không đổi nội dung).
- Thêm shim namespace tại đường cũ, `__init__.py` marker, `contract/schemas.json`, `contract/vi_du.json`, tài liệu và test độc lập.
