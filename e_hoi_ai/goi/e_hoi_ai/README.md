# e_hoi_ai — Hỏi AI (AI-2)

Gói SDK 2.0.0, phiên bản 0.3.0, dùng lại khung AI-0 và lõi AI-1. Chỉ dùng thư viện chuẩn Python (Python ≥ 3.11) và `kho_tri_thuc_sdk` 2.0.0. Gọi Local theo API OpenAI-compatible hoặc Ollama native khi có khuôn; mọi đường bản 1 chỉ dùng provider Local.

- `ai.hoi_tai_lieu@1`: nhận `van_ban` hoặc `van_ban_tai_lieu`, trả bộ trường `tra_loi`, `co_can_cu`, `trich_dan`, `model`.
- `ai.hoi_theo_yeu_cau@1`: nhận `yeu_cau_ai`, trả `tra_loi_ai`.
- Cả hai năng lực đã thực hiện; không có nội dung prompt mặc định chung.

## Hỏi tài liệu

Module cung cấp `ma_prompt`, `phien_ban_prompt`, `prompt`; có thể đặt `model_uu_tien`. Khi nhận `van_ban_tai_lieu`, engine lấy trường `van_ban` trong phong bì tài liệu. Trần văn bản và prompt: mỗi phần 500.000 ký tự; vượt trần thì từ chối, không cắt ngầm.

Khung chung buộc Local trả JSON với danh sách `truong`, mỗi mục có `gia_tri` và `trich_dan`. Giá trị phải được chép từ trích dẫn; trích dẫn phải xuất hiện nguyên văn trong tài liệu, đúng cả khoảng trắng. Engine kiểm thêm các token số đầy đủ, nên `100` không được coi là có trong nguồn chỉ có `1000`. Cách kiểm này bảo thủ: câu diễn giải khác nguyên văn cũng bị hạ, dù có thể đúng về nghĩa.

Danh sách rỗng được trả thành `không thấy căn cứ`, `co_can_cu=false`. Có mục sai định dạng, câu trích bịa, giá trị ngoài trích dẫn hoặc số ngoài nguồn thì hạ toàn bộ lượt, trả `không thấy căn cứ` kèm cảnh báo; không phát hành câu trả lời bịa. Phiếu có bốn trường tĩnh nên cảnh báo nằm trong `tra_loi`; `trich_dan` chỉ chứa các câu đã được kiểm hợp lệ, mỗi câu một dòng.

Prompt thiếu, rỗng hoặc chỉ có khoảng trắng trả `THIEU_PROMPT` trước mọi lời gọi mạng. Phiếu giữ `bat_buoc=true`; `mac_dinh=""` chỉ là sentinel để SDK chuyển cả trường hợp không gửi prompt tới bộ kiểm của engine. Sentinel không bao giờ được dùng để hỏi AI.

Local mất kết nối, timeout, model chưa sẵn sàng hoặc phản hồi HTTP hỏng/vượt trần trả `LOCAL_AI_KHONG_SAN_SANG`, `thu_lai_duoc=true`. Không tự gửi lại POST tới AI. SDK xử lý gửi lại kết quả về Core bằng cùng khóa chống trùng. Engine báo tiến độ trước/sau lượt gọi, kiểm hủy trước mạng và giữa các bước metadata; kết quả nhận sau tín hiệu hủy không được nộp. Lượt HTTP đang chờ có thể tiếp tục tới khi trả lời hoặc hết timeout.

Mỗi lượt ghi một dòng JSON kỹ thuật ra stderr: mã/phiên bản prompt, model, lý do chọn, thời gian ms và kết quả kiểm. Không ghi prompt, tài liệu, câu trả lời, URL hoặc lỗi gốc của dịch vụ.

## Hỏi theo yêu cầu — AI-2

`ai.hoi_theo_yeu_cau@1` nhận phong bì `yeu_cau_ai` phiên bản 1, dùng prompt, tài liệu và model ưu tiên trong phong bì; không lấy prompt từ cài đặt bước. Trả đủ metadata của `tra_loi_ai`, gồm phiên bản engine, SHA-256 của toàn bộ phong bì đầu vào theo JSON chuẩn hóa, chỉ số trích dẫn và cảnh báo. `bat_dau` bao gồm ký tự đầu, `ket_thuc` không bao gồm ký tự cuối, tính theo chỉ số chuỗi Python trong tài liệu gốc.

`khuon_tra_loi=null`: giữ khung và hậu kiểm AI-1, `du_lieu=null`. Khi có khuôn, phản hồi Local dùng đối tượng `{"du_lieu": <đối tượng đúng khuôn module>, "truong": [<giá trị nguyên văn và trích dẫn AI-1>]}`. Khuôn truyền Local bọc khuôn module trong `$defs/khuon`; chuyển gốc `$ref` nội bộ tương ứng, không sửa khuôn gốc. Cách bọc này giữ đồng thời dữ liệu có cấu trúc và dẫn chứng, không thay contract giữa các engine. Ollama được xác định bằng metadata `/api/tags` hợp lệ: POST `/api/chat` kèm `format: <khuôn phản hồi chung>`. OpenAI-compatible: POST `/v1/chat/completions` kèm `response_format.type=json_schema` và `json_schema.schema` là cùng khuôn phản hồi. Không suy API từ tên model hoặc cổng, không thử chuyển API sau lỗi POST.

Kiểm `du_lieu` bằng tập con JSON Schema 2020-12 tự viết, offline: schema boolean; `type` (cả danh sách kiểu), `const`, `enum`; `properties`, `required`, `additionalProperties`, `minProperties`/`maxProperties`; `items`, `prefixItems`, `minItems`/`maxItems`, `uniqueItems`; `minLength`/`maxLength`; `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`; `allOf`, `anyOf`, `oneOf`, `not`; `$defs` và `$ref` nội bộ tới vị trí schema. Số nguyên phân biệt boolean; `multipleOf` kiểm bằng phân số để tránh sai số float. Chấp nhận các annotation `$schema`, `$id` ở gốc, `$comment`, `title`, `description`, `default`, `examples`; không tự áp default.

Đây là bộ kiểm **tối thiểu**, không phải toàn bộ Draft 2020-12: `pattern`, `format`, `unevaluatedProperties`, reference ngoài, vòng `$ref`, resource `$id` lồng và từ khóa lạ bị từ chối trước mạng bằng `KHUON_KHONG_HOP_LE`. Trần độ sâu schema 64 và ngân sách kiểm 100.000 bước; vượt ngân sách không được xem là khớp. Contract chung chỉ cho `du_lieu` là object khi có khuôn; schema chỉ nhận kiểu khác hoặc schema `false` không thể tạo kết quả phù hợp. Sai khuôn/JSON hỏng được hỏi lại đúng một lần, vẫn sai → `AI_TRA_SAI_KHUON`; lỗi HTTP/mạng vẫn là `LOCAL_AI_KHONG_SAN_SANG`, không tự hỏi lại.

Hậu kiểm nguyên văn và token số giống AI-1. Kiểm thêm mọi giá trị lá trong `du_lieu` có căn cứ ở trích dẫn đã xác minh; chỉ cho phép chuyển số nhóm nghìn dạng Việt sang số JSON và ngày DD/MM/YYYY sang YYYY-MM-DD. Giá trị null không đòi dẫn chứng; boolean cần nguyên văn `true`/`false`. Cách kiểm bảo thủ có thể hạ một kết quả diễn giải đúng về nghĩa. Theo quyết định bản 1, `bat_buoc_trich_dan=false` vẫn không bỏ hậu kiểm trích dẫn chung. Sai dẫn chứng hạ `trang_thai=khong_thay_can_cu`, `kiem_trich_dan.dat=false`, trả cảnh báo và giữ `du_lieu` đúng schema để bước hậu kiểm xét trạng thái; không tự hỏi lại vì lỗi dẫn chứng.

Trần `chuyen_tiep` 64 KiB, khuôn 32 KiB, đo bằng byte JSON UTF-8 chuẩn hóa: khóa sắp xếp, không khoảng trắng phân cách, `ensure_ascii=false`, `allow_nan=false`. Đúng ngưỡng được nhận, vượt một byte trả `VUOT_GIOI_HAN` trước mạng, không cắt. `chuyen_tiep` được sao lại theo JSON và test so byte chuẩn hóa; không đưa trường này vào prompt, yêu cầu Local hoặc nhật ký.

## Cấu hình máy

`e_hoi_ai.cau_hinh_may.doc_cau_hinh()` đọc JSON ngoài gói theo biến `KTT_ENGINE_CAU_HINH`. Khi biến chưa đặt, dùng `%PROGRAMDATA%\KhoTriThuc\engines\e_hoi_ai\cau_hinh.json`. Khi không có `PROGRAMDATA` (ví dụ Linux), không tự tìm tệp khác.

Thiếu tệp: trả `None`, không làm engine dừng khởi động. Việc hỏi tài liệu trả lỗi nghiệp vụ `CHUA_CAU_HINH` khi chưa có cấu hình. Đọc lại tệp ở mỗi lần gọi, không ghi tệp hoặc nhật ký nội dung cấu hình.

Schema ở `contract/cau_hinh_may.schema.json`. `local_ai.url` và `local_ai.timeout_giay` là bắt buộc; thời hạn phải là số dương. `quy_tac_model` tùy chọn, mỗi mục phải có đủ mẫu prompt, model ưu tiên và danh sách dự phòng. Các trường lạ, JSON lỗi hoặc trùng khóa bị từ chối bằng thông báo tiếng Việt không chứa dữ liệu đầu vào. Không chứa bí mật; URL không được có thông tin đăng nhập, query hoặc fragment.

URL nhận địa chỉ gốc, `/v1` hoặc `/v1/chat/completions`, bắt buộc `http://<IP>:<cổng>`; `localhost` được đổi thẳng thành `127.0.0.1`. Chỉ loopback, RFC1918 và Tailscale (`100.64.0.0/10`, `fd7a:115c:a1e0::/48`); chặn IP công cộng, link-local, DNS, HTTPS, proxy và redirect. Đích Tailscale phải có IP nguồn Tailscale và socket được ghim IP nguồn. Trước POST chứa tài liệu, engine đọc `/v1/models` và `/api/tags` (nếu có) để từ chối model từ xa/Cloud hoặc model chưa có trên máy.

AI-1 chọn `model_uu_tien` nếu có; nếu không, lấy `uu_tien` của quy tắc đầu tiên khớp `ma_prompt`. Chưa có model thì trả lỗi có thể thử lại. Chưa tự phát hiện hoặc dùng danh sách dự phòng; phần này thuộc AI-3.

Ví dụ dưới đây chỉ là cấu hình DEMO; chép vào tệp **ngoài gói** nếu cần kiểm bộ đọc:

```json
{
  "local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60},
  "quy_tac_model": [
    {"mau_ma_prompt": "demo.*", "uu_tien": "model-demo", "du_phong": []}
  ]
}
```

## Contract

Ba schema `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai` trong `contract/` là bản sao nguyên byte từ `_chung/contract/` trong repo. Pytest kiểm SHA-256 từng cặp; gói chạy độc lập không truy cập thư mục `_chung/`.

Các schema dùng Draft 2020-12, cho phép thêm trường tùy chọn để giữ tương thích phiên bản 1. `dong`, `tu`, `nghi_ngo` không bắt buộc; ô bảng trống và ô gộp được giữ lại. Giới hạn dung lượng JSON UTF-8 của `khuon_tra_loi` (32 KiB) và `chuyen_tiep` (64 KiB) được AI-2 kiểm khi xử lý.

## Kiểm AI-1 và AI-2

Chạy trong worktree, đặt `PYTHONDONTWRITEBYTECODE=1` để không sinh bytecode trong gói. Với PowerShell:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
.venv/Scripts/python -m pytest e_hoi_ai/tests -q
.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
```

Lệnh SDK cần Local AI được cấu hình bên ngoài gói. Để chạy không cần máy AI thật hoặc mạng ngoài:

```powershell
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
```

Bộ chạy bật Local giả ở `127.0.0.1` trên cổng do hệ điều hành chọn, ghi cấu hình DEMO vào thư mục tạm ngoài gói, rồi gọi **nguyên lệnh** `python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai` bằng tiến trình con. Đóng server và dọn cấu hình tạm sau kiểm. Ví dụ DEMO tối thiểu và bộ chạy được đưa lên AI-1 để kiểm đủ cổng chung; AI-4 sẽ mở rộng.

Kết quả AI-2 ngày 14/11/2026: SDK thu **1/1 ĐẠT** (DEMO hỏi tài liệu kế thừa AI-1), pytest **238 passed, 0 skipped**, kiểm độc lập mã **0**. Trong đó 97 ca mới AI-2 kiểm Local giả + CoreGia và bộ kiểm khuôn, gồm hai kiểu API, đúng/sai khuôn, một lần hỏi lại, không khuôn, chuyển tiếp nguyên vẹn, đúng/vượt ngưỡng byte UTF-8, hủy và mất xác nhận. Các test Local HTTP đếm provider Cloud **0 lượt**, chặn mạng ngoài và phân giải DNS. **Đã kiểm bằng Core giả (CoreGia)** trên Windows/Python 3.13.14; chưa chạy thực tế trên Linux. Chưa kiểm Core thật hoặc model thật. Nguồn lõi và QA đối chiếu độc lập được ghi ở `NGUON.md`.
