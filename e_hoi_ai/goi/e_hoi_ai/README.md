# e_hoi_ai — Hỏi AI (AI-1, AI-2, AI-3, AI-4)

Gói SDK 2.0.0, phiên bản 0.4.0, dùng lại khung AI-0 và lõi AI-1. Chỉ dùng thư viện chuẩn Python (Python ≥ 3.11) và `kho_tri_thuc_sdk` 2.0.0. Gọi Local theo API OpenAI-compatible hoặc Ollama native khi có khuôn; mọi đường bản 1 chỉ dùng provider Local.

- `ai.hoi_tai_lieu@1`: nhận `van_ban` hoặc `van_ban_tai_lieu`, trả bộ trường `tra_loi`, `co_can_cu`, `trich_dan`, `model`, `ly_do_chon_model`.
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

`khuon_tra_loi=null`: giữ khung và hậu kiểm AI-1, `du_lieu=null`. Khi có khuôn, phản hồi Local dùng đối tượng `{"du_lieu": <đối tượng đúng khuôn module>, "truong": [<giá trị nguyên văn và trích dẫn AI-1>]}`. Khuôn truyền Local bọc khuôn module trong `$defs/khuon`; chuyển gốc `$ref` nội bộ tương ứng, không sửa khuôn gốc. Cách bọc này giữ đồng thời dữ liệu có cấu trúc và dẫn chứng, không thay contract giữa các engine. Loại API lấy trực tiếp từ catalog AI-3 sau kiểm khả dụng trước POST, không dò metadata thêm để chọn khuôn. Ollama được xác định bằng metadata `/api/tags` hợp lệ: POST `/api/chat` kèm `format: <khuôn phản hồi chung>`. OpenAI-compatible: POST `/v1/chat/completions` kèm `response_format.type=json_schema` và `json_schema.schema` là cùng khuôn phản hồi. Không suy API từ tên model hoặc cổng, không thử chuyển API sau lỗi POST.

Kiểm `du_lieu` bằng tập con JSON Schema 2020-12 tự viết, offline: schema boolean; `type` (cả danh sách kiểu), `const`, `enum`; `properties`, `required`, `additionalProperties`, `minProperties`/`maxProperties`; `items`, `prefixItems`, `minItems`/`maxItems`, `uniqueItems`; `minLength`/`maxLength`; `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`; `allOf`, `anyOf`, `oneOf`, `not`; `$defs` và `$ref` nội bộ tới vị trí schema. Số nguyên phân biệt boolean; `multipleOf` kiểm bằng phân số để tránh sai số float. Chấp nhận các annotation `$schema`, `$id` ở gốc, `$comment`, `title`, `description`, `default`, `examples`; không tự áp default.

Đây là bộ kiểm **tối thiểu**, không phải toàn bộ Draft 2020-12: `pattern`, `format`, `unevaluatedProperties`, reference ngoài, vòng `$ref`, resource `$id` lồng và từ khóa lạ bị từ chối trước mạng bằng `KHUON_KHONG_HOP_LE`. Trần độ sâu schema 64 và ngân sách kiểm 100.000 bước; vượt ngân sách không được xem là khớp. Contract chung chỉ cho `du_lieu` là object khi có khuôn; schema chỉ nhận kiểu khác hoặc schema `false` không thể tạo kết quả phù hợp. Sai khuôn/JSON hỏng được hỏi lại đúng một lần, vẫn sai → `AI_TRA_SAI_KHUON`; lỗi HTTP/mạng vẫn là `LOCAL_AI_KHONG_SAN_SANG`, không tự hỏi lại.

Hậu kiểm nguyên văn và token số giống AI-1. Kiểm thêm mọi giá trị lá trong `du_lieu` có căn cứ ở trích dẫn đã xác minh; chỉ cho phép chuyển số nhóm nghìn dạng Việt sang số JSON và ngày DD/MM/YYYY sang YYYY-MM-DD. Giá trị null không đòi dẫn chứng; boolean cần nguyên văn `true`/`false`. Cách kiểm bảo thủ có thể hạ một kết quả diễn giải đúng về nghĩa. Theo quyết định bản 1, `bat_buoc_trich_dan=false` vẫn không bỏ hậu kiểm trích dẫn chung. Sai dẫn chứng hạ `trang_thai=khong_thay_can_cu`, `kiem_trich_dan.dat=false`, trả cảnh báo và giữ `du_lieu` đúng schema để bước hậu kiểm xét trạng thái; không tự hỏi lại vì lỗi dẫn chứng.

Trần `chuyen_tiep` 64 KiB, khuôn 32 KiB, đo bằng byte JSON UTF-8 chuẩn hóa: khóa sắp xếp, không khoảng trắng phân cách, `ensure_ascii=false`, `allow_nan=false`. Đúng ngưỡng được nhận, vượt một byte trả `VUOT_GIOI_HAN` trước mạng, không cắt. `chuyen_tiep` được sao lại theo JSON và test so byte chuẩn hóa; không đưa trường này vào prompt, yêu cầu Local hoặc nhật ký.

## Cấu hình trong ngăn — AI-8, 15/11/2026

Engine đọc bản ghi duy nhất bảng `cau_hinh`, khóa `{}`, qua `doc_cau_hinh(ngan, schema)`. Schema trong gói là `cau_hinh.schema.json`: `local_ai.url`, `local_ai.timeout_giay` bắt buộc (số dương, tối đa 600 giây), `quy_tac_model` mặc định `[]`. Đọc mới từng việc; thiếu thì trả `CHUA_CAU_HINH`, hướng dẫn Admin vào Quản lý engine › Hỏi AI › Cấu hình. Không lưu cấu hình hay catalog xuống đĩa, không đọc biến cấu hình máy cũ.

`chon_ngan(app)` dùng `app.ngan` nếu có, nếu chưa có thì tạo RAM dùng chung trong phiên chạy và cảnh báo một lần ra stderr. `viec.ngan` được ưu tiên khi SDK cung cấp. Với SDK 2.0, RAM chỉ phục vụ kiểm thử và không giữ cấu hình sau khởi động lại. `cau_hinh_may.py` cùng schema cũ còn nguyên để lead chuyển LUU-TRU; không còn được import bởi đường chạy engine.

Hai tệp `ngan.py` và `cau_hinh.py` là bản tạm theo đặc tả NGAN-0, chưa phải bản sao chính thức. Test so băm đã viết, skip với lý do **chờ NGAN-0 gộp**. Khi có mẫu, lead thay nguyên hai tệp và bật test; đối chiếu các chữ ký trong VIEC.md trước khi thay.

`KHAI-SDK-2.1.json` khai hai bảng, schema cấu hình và màn quản trị, chưa ghép vào `engine.json` 2.0. Màn `ui/cau_hinh.js` xuất hàm mặc định `async (goc, KttCore = globalThis.KttCore)`, dùng DOM an toàn, kế thừa font Core; Core cần thống nhất cách nạp module. Chỉ gọi `.cau_hinh.doc/luu` và `.ngan.tim`. Cổng Cloud chỉ hiện “Chưa áp dụng ở bản 1”, không có nút bật. Trạng thái/model là kết quả kiểm gần nhất khi engine xử lý việc, không phải kết nối tức thời; chưa có nút discovery do API quản trị SDK chưa phát hành.

URL nhận địa chỉ gốc, `/v1` hoặc `/v1/chat/completions`, bắt buộc `http://<IP>:<cổng>`; `localhost` được đổi thẳng thành `127.0.0.1`. Chỉ loopback, RFC1918 và Tailscale (`100.64.0.0/10`, `fd7a:115c:a1e0::/48`); chặn IP công cộng, link-local, DNS, HTTPS, proxy và redirect. Đích Tailscale phải có IP nguồn Tailscale và socket được ghim IP nguồn. Discovery và kiểm khả dụng dùng cùng các ràng buộc mạng này.

AI-3 đặt logic trong `e_hoi_ai/chon_model.py`. Thử lần lượt các API trên cùng IP/cổng, kiểm đúng cấu trúc phản hồi:

| API | Loại phần mềm | ID nguyên gốc |
|---|---|---|
| `GET /api/tags` | `ollama` | `models[].name` (hoặc `model`) |
| `GET /api/v1/models` | `lm_studio` | `models[].key` |
| `GET /api/v0/models` (dự phòng native v1) | `lm_studio` | `data[].id` |
| `GET /v1/models` | `openai_compatible` | `data[].id` |

Không suy loại phần mềm hoặc chất lượng từ tên model/cổng. Catalog rỗng hợp lệ là kết quả có thẩm quyền, không chuyển API để tìm cách dùng model đã bị loại. Metadata chỉ rõ model từ xa, `type` khác `llm`, `state=not-loaded` hoặc `loaded_instances=[]` thì không khả dụng. Ollama tải model khi hỏi nên danh sách `/api/tags` không có cờ tải vẫn được xét; không khẳng định model đang chạy.

Catalog và loại API có đệm RAM 300 giây theo URL gốc, tối đa 64 endpoint. Kết quả discovery được lấy hoặc tạo theo `id_model` vào bảng `model_phat_hien`, cập nhật trạng thái bằng CAS, rồi đọc từ ngăn để chọn. Mỗi ID giữ địa chỉ, loại API, thứ tự, thời điểm và khả dụng; model mất/lỗi discovery được đánh dấu không khả dụng. Không lưu xuống đĩa. Mỗi lượt đọc metadata mới từ API đã nhận diện để chọn theo trạng thái hiện tại và kiểm lại trước POST chứa nội dung. Việc kiểm trạng thái không kéo dài TTL discovery. Nếu API cũ lỗi thì phát hiện lại; lỗi không được cache, không làm engine chết. Model mất giữa hai lượt được bỏ qua ngay khi cache còn hạn; model mất sau khi chọn thì từ chối trước POST. Không tự gửi lại POST.

Thứ tự chọn: `model_uu_tien` khả dụng → duyệt `quy_tac_model` theo thứ tự cấu hình, mỗi quy tắc khớp `ma_prompt` xét `uu_tien` rồi từng `du_phong` → model khả dụng đầu tiên theo thứ tự API. Mẫu `m4.*` và `*` phân biệt hoa/thường. Không còn model thì trả `LOCAL_AI_KHONG_SAN_SANG`, có thể thử lại. Quy tắc được đọc riêng từng lượt, không thay cấu hình chung.

Kết quả có `ly_do_chon_model`: `model_uu_tien`, `quy_tac_ma_prompt`, `du_phong_quy_tac_ma_prompt` hoặc `model_dau_tien_kha_dung`. AI-2 dùng lại `CongAI.chon_model(..., kiem_huy=...)` và trường lý do đã có trong `KetQuaAI`; luồng `chay.py` không thay đổi.

Ví dụ dưới đây chỉ là cấu hình DEMO để nạp qua ngăn hoặc màn cấu hình:

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

## Cổng kiểm AI-4

Chạy trong worktree, đặt `PYTHONDONTWRITEBYTECODE=1` để không sinh bytecode trong gói. Với PowerShell:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
.venv/Scripts/python -m pytest e_hoi_ai/tests -q
.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
```

`chay_demo_voi_local_gia.py` là **cổng đạt thay cho** `python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai` theo phiếu AI-4/AI-8. Bộ chạy bật Local giả trên loopback, nạp cấu hình DEMO qua `NganBoNho.lo().them`, rồi gọi `CoreGia().chay_thu_demo(app)`. Không tạo tệp cấu hình hoặc dùng `KTT_ENGINE_CAU_HINH`; khôi phục ngăn ban đầu trong `finally`. Mọi ví dụ phải `XONG`, bộ ví dụ khác rỗng và số lượt Local khớp thì mã thoát bằng 0. Dùng thêm `--sdk-thu` để chạy đúng hàm CLI SDK thu với cùng cấu hình/ngăn/Local giả. Lệnh SDK thu chạy riêng không được cấp cấu hình nên trả `CHUA_CAU_HINH` (hành vi có chủ đích), không được tự mặc định DEMO vào đường chạy thật.

Bộ UI `node --test e_hoi_ai/tests/ui/cau_hinh.test.mjs` được pytest gọi tự động; cần Node có sẵn, không cài thư viện hoặc gọi mạng. Kiểm lưu CAS, xung đột tiếng Việt, giữ dự phòng, phân trang, thêm/bỏ quy tắc, lỗi đọc và Cloud không có công tắc. Đây là DOM/KttCore giả, chưa nghiệm thu trình duyệt/Core thật. Công cụ AI-7 giữ nguyên `--url`, không đọc tệp cấu hình.

Phiếu có ba ví dụ chỉ dùng hợp đồng GIẢ DEMO của Công ty DEMO Ánh Dương, mã DEMO-001: hỏi 1.000.000 VND và 30/10/2026 có trích dẫn; hỏi người bảo lãnh không có trong tài liệu → `không thấy căn cứ`; `ai.hoi_theo_yeu_cau@1` có khuôn tiền `{"so": 1000000, "tien_te": "VND"}` và ngày `2026-10-30`. Ngày DD/MM/YYYY chỉ nằm trong văn bản nguồn/trích dẫn, dữ liệu có kiểu dùng YYYY-MM-DD.

`tests/test_demo_va_khoi_dong.py` đối chiếu đáp án, khuôn, vị trí trích dẫn và chuyển tiếp; kiểm mã thoát khi DEMO lỗi/rỗng. Test HTTP bật `MayChuGia`, chạy tiến trình Python thật, cấp dòng khởi động JSON qua stdin và gọi `app.chay()` không truyền đường truyền. Kiểm nhận việc, đọc đầu vào qua HTTP, xác thực, nộp kết quả trước kết thúc, khóa chống trùng và 0 lượt Cloud; mọi kết nối chỉ loopback.

Kết quả AI-2 ngày 14/11/2026: SDK thu **1/1 ĐẠT** (DEMO hỏi tài liệu kế thừa AI-1), pytest **238 passed, 0 skipped**, kiểm độc lập mã **0**. Trong đó 97 ca mới AI-2 kiểm Local giả + CoreGia và bộ kiểm khuôn, gồm hai kiểu API, đúng/sai khuôn, một lần hỏi lại, không khuôn, chuyển tiếp nguyên vẹn, đúng/vượt ngưỡng byte UTF-8, hủy và mất xác nhận. Các test Local HTTP đếm provider Cloud **0 lượt**, chặn mạng ngoài và phân giải DNS. **Đã kiểm bằng Core giả (CoreGia)** trên Windows/Python 3.13.14; chưa chạy thực tế trên Linux. Chưa kiểm Core thật hoặc model thật. Nguồn lõi và QA đối chiếu độc lập được ghi ở `NGUON.md`.

Kết quả AI-3 ngày 14/11/2026: SDK thu **1/1 ĐẠT**, pytest **176 passed, 0 skipped**, kiểm độc lập mã **0**. Các test Local HTTP đếm provider Cloud **0 lượt**, chặn mạng ngoài và phân giải DNS. **Đã kiểm bằng Core giả (CoreGia)** trên Windows/Python 3.13.14; chưa chạy thực tế trên Linux, Core thật hoặc model thật. Nguồn lõi chuyển sang và thay đổi AI-3 được ghi ở `NGUON.md`.

## Kết quả AI-4 — 14/11/2026

Cổng DEMO Local giả **3/3 ĐẠT** (mã 0); pytest **283 passed, 0 skipped** trong 39.12 giây; kiểm độc lập mã **0**. Kiểm thêm lệnh SDK thu với Local giả/cấu hình DEMO cấp trước: **3/3 ĐẠT**. **Đã kiểm bằng Core giả (CoreGia)** và HTTP loopback qua MayChuGia trên Windows/Python 3.13.14; chưa kiểm Linux/Core thật/model thật. Bản bàn giao và kết quả lệnh thật nằm ở `e_hoi_ai/docs/VIEC.md` trong repo.

## Kết quả việc gộp AI-2 và AI-3 — 14/11/2026

Bản gộp `0.4.0`: SDK thu **1/1 ĐẠT** qua `chay_demo_voi_local_gia.py`; pytest **278 passed, 0 skipped**; kiểm độc lập mã **0**. Giữ đủ 97 ca AI-2 và 35 ca AI-3 cùng 141 ca nền, thêm 5 ca giao thoa: bốn kiểu API có khuôn/dự phòng/cache/đếm GET và hủy trong discovery. **Đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả trên Windows/Python 3.13.14; chưa kiểm Linux/Core thật/model thật.
## Khung Cloud AI-6 — 14/11/2026

`nha_cung_cap.py` tách `NhaCungCapLocal` và `NhaCungCapCloud` (Anthropic Messages / OpenAI Chat Completions). Cloud chỉ nhận khóa qua constructor; không đọc env, tệp hoặc kho bí mật. Transport HTTPS dùng host cố định, không proxy, redirect hoặc tự gửi lại. Đây là khung chưa kiểm với API thật; không bảo đảm tương thích mọi model Cloud. Không chuyển các tùy chọn fallback/beta hay danh sách model Cloud cũ.

`BAT_CLOUD = False` cố định trong mã, không có ô cấu hình bật. Cả `cloud.hoi_cloud` và phương thức provider kiểm cờ; hai năng lực đã đăng ký chỉ gọi provider `local`, kể cả Local lỗi hoặc sai khuôn. `engine.json`, `bi_mat[]`, loại dữ liệu khai báo và `chay_thu_demo` giữ nguyên ở lát này.

`hoi_cloud` chỉ nhận phong bì `van_ban_da_che` phiên bản 1, bắt buộc `con_sot=[]` và `kiem_tien_ngay is True`. Phần văn bản phải chứa yêu cầu cùng dữ liệu đã qua Mask; hàm không có tham số prompt thô. Chỉ trường `van_ban` ra provider ngoài, cùng chỉ dẫn định dạng cố định và tên model. Metadata, mã mở che và `chuyen_tiep` không đi ra Cloud. Mã mở che xuất hiện trong nội dung/model bị từ chối; kết quả chép mã gốc vào `chuyen_tiep.ma_yeu_cau`, ưu tiên mã trên phong bì khi có xung đột. Trần 64 KiB tính sau khi thêm mã; trần văn bản 500.000 ký tự, vượt thì từ chối. Hàm hậu kiểm trích dẫn trên văn bản đã che và trả `tra_loi_ai`; mở che do bước sau qua Core thực hiện.

Test chỉ thay cờ trong bộ nhớ và tiêm Cloud giả; chặn socket/DNS. Không sử dụng khóa thật, không gọi Cloud thật. Đã kiểm bằng Core giả (CoreGia) cho hai năng lực Local; chưa kiểm Core thật hoặc model thật. Bản 2 cần bí mật Core, Mask, chính sách Cloud theo module và ngăn dữ liệu trước khi nối đường vận hành.
