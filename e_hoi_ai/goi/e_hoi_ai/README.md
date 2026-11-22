# e_hoi_ai — Hỏi AI (AI-11)

Gói SDK 2.2.0, phiên bản 0.11.0, dùng lại khung AI-0 và lõi AI-1. Chỉ dùng thư viện chuẩn Python (Python ≥ 3.11) và `kho_tri_thuc_sdk` 2.2.0. Gọi Local theo API OpenAI-compatible hoặc Ollama native khi có khuôn; mọi đường bản 1 chỉ dùng provider Local.

- `ai.hoi_tai_lieu@1`: nhận `van_ban` hoặc `van_ban_tai_lieu`, trả bộ trường `tra_loi`, `co_can_cu`, `trich_dan`, `model`, `ly_do_chon_model`.
- `ai.hoi_theo_yeu_cau@1`: nhận `yeu_cau_ai`, trả `tra_loi_ai`.
- `ai.hoi_mask_cuc_bo@1`: nhận `yeu_cau_ai`, trả `tra_loi_ai` có thực thể và span trên gốc, chỉ Local.
- Prompt nghiệp vụ thuộc module/quy trình, không lưu trong cấu hình engine.

## Cổng Cloud AI — UI-AI-2, 22/11/2026

Màn `ui/cloud.js` nạp như ES module `(goc, KttCore)`, chỉ qua `KttCore.engine('e_hoi_ai')`. Khai màn dự kiến tại `KHAI-SDK-2.1.json`; SDK 2.2.0 chưa nhận cửa D/F nên chưa khai vào `engine.json`. Không đổi manifest, schema, xử lý việc hoặc cờ Cloud của bản 1.

Nhà cung cấp, model, tỷ lệ kiểm và nút kiểm kết nối Cloud luôn khóa. Không kiểm Cloud thật khi bấm hoặc khi mở màn. API key có thể chuẩn bị riêng trong két Core nếu cửa F đã được cấp; lưu/xóa key không bật Cloud. Nếu chưa có cửa F hoặc không đủ quyền, ô key và nút ghi/xóa bị khóa, có hướng dẫn tải lại. Không có nút hiện bản rõ; sau lưu chỉ hiện `Đã lưu · ••••` cùng bốn ký tự cuối. Lỗi không hiển thị phản hồi thô.

Hợp đồng két **dự kiến, chỉ kiểm bằng KttCore giả**: `bi_mat.trang_thai(ten)`, `bi_mat.luu(ten, gia_tri, phien_ban)`, `bi_mat.xoa(ten, phien_ban)`, tên `khoa_api_anthropic`. Core trả `{da_luu, bon_ky_tu_cuoi, phien_ban}`; phiên bản số nguyên tăng đơn điệu cả khi xóa, CAS sai trả HTTP 409 / `BI_MAT_XUNG_DOT`. Đầu vào key 8–4096 ký tự không khoảng trắng; UI không kiểm tính hợp lệ với nhà cung cấp. Khi mất phản hồi, tranh chấp hoặc metadata sai, khóa ghi và yêu cầu tải lại để tránh báo thành công giả. Core phải kiểm quyền Admin, phạm vi engine, ghi kiểm toán và không bao giờ trả bản rõ về màn. Không ghi key vào ngăn/cấu hình/tệp/log của engine.

Nhật ký gửi ra ngoài chưa có cửa đọc chung: hiển thị cảnh báo và khóa nút xem, không đọc bảng chưa khai, không báo lịch sử rỗng hoặc số lượt giả. Cần Core cấp metadata có quyền/pháp nhân và phân trang; chi phí nếu có phải kèm mã tiền. Cloud vẫn chờ Mask và phê duyệt bản sau; M9/nhóm 07 chỉ Local.

Schema cấu hình Local hiện có đã có `title`/`description`/`examples` tiếng Việt ở mọi node; UI-AI-2 thêm kiểm tự động bảo toàn yêu cầu này, không thêm trường Cloud vào cấu hình xử lý việc.

Kiểm UI không mạng: `node --test e_hoi_ai/tests/ui/cau_hinh.test.mjs e_hoi_ai/tests/ui/cloud.test.mjs` từ gốc repo (cũng được gọi trong pytest). Dựng ảnh bằng `node e_hoi_ai/tests/ui/chup_anh_cloud_demo.mjs`; `UI_CHROME` có thể chỉ định Chrome trên Linux. HTML và ảnh DEMO rộng/hẹp/lỗi/CAS tại `e_hoi_ai/docs/anh-ui-ai-2/`, ngoài gói chạy. Đã kiểm bằng Core giả (CoreGia); chưa nối Core hoặc Cloud thật. CLI SDK độc lập còn lỗi thiếu cấu hình DEMO như AI-11, không thay bằng kết quả bộ bổ sung.

## Nhận diện Local AI-9 — 15/11/2026

Profile `chuyen_tiep.mask_2c` đã được lead duyệt ngày 15/11 theo sổ loại chung §6. Kiểm đủ trường, local bắt buộc, phiên bản, tham chiếu kỹ thuật an toàn, dạng SHA-256, hệ offset, chỉ số/số đoạn và khoảng đoạn. Tái tính băm prompt UTF-8, khuôn JSON chuẩn và đoạn gốc; một đoạn duy nhất còn đối chiếu băm gốc. Trần đoạn 8.000 code point, tối đa 128 đoạn, gốc tối đa 500.000, span tối đa 300; vượt từ chối. Engine không mở snapshot hoặc đọc ngăn riêng của Mask. Băm snapshot/profile/bản che và độ phủ toàn gốc nhiều đoạn phải được Core/Mask kiểm lại với bytes có quyền; payload không tự cấp quyền hoặc chứng thực nguồn.

Model nhận prompt do module cấp và đúng đoạn gốc, giữ nguyên NFD/Cf/selector. Khuôn được truyền trực tiếp; model trả duy nhất `{da_quet_het:true,thuc_the:[{loai,nguyen_van,bat_dau,ket_thuc,muc}]}`, sau đó engine đặt đối tượng ấy vào `tra_loi_ai.du_lieu`. Mọi object đóng, đủ required, loại `nguoi|to_chuc|dia_chi`, mức `chac|nghi_ngo`. Không nhận JSON rào Markdown/thiếu/khóa trùng/NaN/Infinity/ngoài khuôn. AI-9 không tự hỏi lại; sai JSON/khuôn/span là lỗi và không có kết quả. Quy tắc hỏi lại AI-2 giữ nguyên.

Kiểm span bằng số nguyên Python (không nhận bool/float), `0 <= a < b <= len(goc)` và `goc[a:b] == nguyen_van`. Giữ riêng trích dẫn mỗi lần xuất hiện; nhãn/mức/offset không cần xuất hiện trong câu trích. Rỗng hợp lệ trả `khong_thay_can_cu`, `kiem_trich_dan.dat=true`, `du_lieu` đúng khuôn và trích dẫn rỗng; không chứng minh đã nhận diện hết hoặc đủ điều kiện Cloud. `nha_cung_cap=local` do engine đặt; `bam_dau_vao` vẫn là SHA JSON chuẩn của toàn phong bì yêu cầu. `chuyen_tiep` được giữ nguyên byte JSON chuẩn hóa, không gửi ra model; không đưa snapshot/mã yêu cầu vào wire/log.

Budget AI-9: toàn body JSON đầu vào ≤64 KiB; dự trù bảo thủ `byte UTF-8 body + 256 + 8192 token đầu ra` phải nằm trong context server khai. Đây không phải số đếm tokenizer chính xác hoặc số đo model thật. Ollama lấy context đang chạy qua `/api/ps`; API tương thích đọc `loaded_context_length` hoặc `context_length` của đúng model tại endpoint discovery. Không lấy `max_context_length` làm context đang dùng; thiếu/sai metadata thì từ chối trước POST. Server không công bố trường này chưa chạy AI-9 được; cần lead xác minh/đo server thật. Đầu ra giới hạn 8192 token và 2.000.000 byte; chạm dấu cắt hoặc vượt trần không được lấy phần đầu làm kết quả.

Transport chung kiểm Ollama `done=true,done_reason=stop` hoặc OpenAI-compatible `finish_reason=stop`. Lỗi kết nối chắc chắn trước gửi là `LOCAL_AI_KHONG_SAN_SANG`, có thể thử lại. Từ lúc bắt đầu gửi POST, timeout/mất phản hồi/body thiếu theo Content-Length hoặc HTTP 202 → `ChuaRo` với mã tương quan riêng; không retry/fallback. Phản hồi hoàn chỉnh sai nguồn/JSON/hoàn tất bị từ chối. Giữ IP trực tiếp, bind nguồn Tailscale, cấm DNS/proxy/redirect và metadata remote/cloud. Hủy/mất lease dừng trước nộp. Các quy tắc trích dẫn hỏi–đáp cũ giữ nguyên.

Ba DEMO hỏi–đáp trong manifest giữ tương thích công cụ AI-7. `tests/chay_demo_voi_local_gia.py` chạy thêm một ca AI-9 bằng snapshot bytes thật trong kho RAM CoreGia; `--sdk-thu` kiểm riêng ba mẫu manifest. Đã kiểm bằng Core giả (CoreGia), không chứng nhận ACL/provenance hoặc model thật. Trước dùng thật lead phải xác nhận model chạy tại chỗ và chặn egress Cloud; IP private/nhãn local chưa chứng minh điều này. `BAT_CLOUD=False`, không khai năng lực Cloud.

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

Đây là bộ kiểm **tối thiểu**, không phải toàn bộ Draft 2020-12: `pattern`, `format`, `unevaluatedProperties`, reference ngoài, vòng `$ref`, resource `$id` lồng và từ khóa lạ bị từ chối trước mạng bằng `KHUON_KHONG_HOP_LE`. Trần độ sâu schema 64 và ngân sách kiểm 100.000 bước; vượt ngân sách không được xem là khớp. Contract chung chỉ cho `du_lieu` là object khi có khuôn; schema chỉ nhận kiểu khác hoặc schema `false` không thể tạo kết quả phù hợp. Ở năng lực hỏi theo yêu cầu cũ, sai khuôn/JSON hỏng được hỏi lại đúng một lần, vẫn sai → `AI_TRA_SAI_KHUON`. Lỗi trước gửi là `LOCAL_AI_KHONG_SAN_SANG`; sau khi POST có thể đã gửi mà mất phản hồi/timeout hoặc 202 thì `ChuaRo`, không tự hỏi lại.

Hậu kiểm nguyên văn và token số giống AI-1. Kiểm thêm mọi giá trị lá trong `du_lieu` có căn cứ ở trích dẫn đã xác minh; chỉ cho phép chuyển số nhóm nghìn dạng Việt sang số JSON và ngày DD/MM/YYYY sang YYYY-MM-DD. Giá trị null không đòi dẫn chứng; boolean cần nguyên văn `true`/`false`. Cách kiểm bảo thủ có thể hạ một kết quả diễn giải đúng về nghĩa. Theo quyết định bản 1, `bat_buoc_trich_dan=false` vẫn không bỏ hậu kiểm trích dẫn chung. Sai dẫn chứng hạ `trang_thai=khong_thay_can_cu`, `kiem_trich_dan.dat=false`, trả cảnh báo và giữ `du_lieu` đúng schema để bước hậu kiểm xét trạng thái; không tự hỏi lại vì lỗi dẫn chứng.

Trần `chuyen_tiep` 64 KiB, khuôn 32 KiB, đo bằng byte JSON UTF-8 chuẩn hóa: khóa sắp xếp, không khoảng trắng phân cách, `ensure_ascii=false`, `allow_nan=false`. Đúng ngưỡng được nhận, vượt một byte trả `VUOT_GIOI_HAN` trước mạng, không cắt. `chuyen_tiep` được sao lại theo JSON và test so byte chuẩn hóa; không đưa trường này vào prompt, yêu cầu Local hoặc nhật ký.

## Cấu hình và ngăn SDK 2.2.0 — AI-11, 15/11/2026

Cấu hình đọc từ bản chụp `viec.cau_hinh` do Core kiểm theo `cau_hinh.schema.json`; không còn bảng `cau_hinh`. `local_ai.url` và `local_ai.timeout_giay` bắt buộc cho việc cần Local AI (số dương, tối đa 600 giây), `quy_tac_model` mặc định `[]`. Chưa khai `local_ai` thì vẫn khởi động được; khi nhận việc trả `CHUA_CAU_HINH`, hướng dẫn Admin vào Quản lý engine › Hỏi AI › Cấu hình. Hook `@app.khi_doi_cau_hinh` xóa đệm discovery khi Core báo cấu hình thay đổi.

Catalog dùng `viec.ngan` của SDK, bảng `model_phat_hien` phạm vi engine, khai trực tiếp trong `engine.json`; không có fallback RAM. Các trường ngăn chỉ dùng kiểu SDK hỗ trợ: `api` là chuỗi JSON (`van_ban`/SQL `text`); thứ tự số được đọc bằng `int` vì SDK trả `so` dạng chuỗi. Khi cập nhật chỉ gửi trường nghiệp vụ, không gửi lại cột hệ thống. Không có lệnh xóa; model mất được đánh dấu không khả dụng. `sql/001_tao_model_phat_hien.sql` chỉ tạo bảng trong `eng_e_hoi_ai`; Core thực hiện migration, engine không chạy SQL.

`sql/kiem_ke.json` kiểm byte và SHA-256 của mọi tệp gói trừ chính nó. Các tệp gói dùng LF (quy định tại `e_hoi_ai/.gitattributes`). `NGUON.md` băm LF, trừ chính nó và kiểm kê sinh cuối để tránh vòng tự tham chiếu; kiểm kê cuối bao gồm cả `NGUON.md`.

Cổng tạm `ngan.py`, `cau_hinh.py`, `ngan_engine.py` và `KHAI-SDK-2.1.json` đã chuyển nguyên byte vào `e_hoi_ai/LUU-TRU/AI-11/`, ngoài gói chạy. `cau_hinh_may.py` cùng schema cũ giữ để công cụ/test lịch sử tham chiếu; runtime không import hay đọc tệp cấu hình máy.

Màn `ui/cau_hinh.js` xuất hàm mặc định `async (goc, KttCore = globalThis.KttCore)`, dùng DOM an toàn. Màn Máy AI tách IP/cổng, có Kiểm tra kết nối, Tự tìm máy AI, Cập nhật model và bảng thêm/bỏ/sắp thứ tự quy tắc cùng model dự phòng. Model lấy từ máy qua thao tác quản trị; giá trị cũ chưa khả dụng vẫn được giữ khi mở/sửa, không tự thay cấu hình. Không thêm trường model mặc định hoặc tùy chọn rà hợp đồng của ảnh mẫu vì không thuộc cấu hình engine hiện hành. Thời hạn chờ và đường dẫn API ở Nâng cao; lưu giữ đường dẫn cũ và dùng CAS. Xung đột giữ dữ liệu đang sửa, khóa Lưu đến khi Tải lại cấu hình. Màn rộng hai cột, màn hẹp một cột, có lỗi cạnh ô. Cloud vẫn chỉ hiện “Chưa áp dụng ở bản 1”; màn Cloud và bí mật thuộc UI-AI-2.

Chỉ dùng `KttCore.engine("e_hoi_ai").cau_hinh.doc/luu`, `.ngan.tim`, `.thao_tac`; không gọi mạng từ trình duyệt. `KHAI-SDK-2.1.json` mới chỉ khai D/E dự kiến (bản cũ của AI-8 vẫn ở LUU-TRU). SDK 2.2.0 chưa nhận khai màn/thao tác: Core cần nạp màn với quyền Admin, chuyển tác vụ ưu tiên đến ba hàm `e_hoi_ai.quan_tri` theo bản khai. Các hàm chưa đăng ký vào `chay.py` hoặc `engine.json`; không thay năng lực xử lý việc. Trạng thái lúc mở màn ghi rõ model từ lần kiểm trước, chỉ nút kiểm mới xác nhận kết nối hiện tại.

Thao tác quản trị Python chỉ GET metadata qua discovery và bảo vệ mạng có sẵn; không gửi prompt/tài liệu, không chạm Cloud hoặc bí mật, không lưu tệp. Kiểm kết nối/lấy model nhận `{url, timeout_giay}` (URL bỏ trống dùng snapshot cấu hình, timeout mặc định 2 giây, trên 0 đến 5); trả `{url, ket_noi, models:[{id_model,kha_dung}], kiem_luc, thong_diep}` và cập nhật ngăn catalog bằng CAS. Dịch vụ trả danh sách rỗng vẫn là kết nối được, chưa có model khả dụng. Thất bại kết nối trả `ket_noi:false`; lỗi ngăn vẫn là lỗi, không báo thành công giả. Mọi GET dùng bộ phát hiện riêng để không thay cache việc đang chạy.

Tự tìm nhận `{danh_sach_url?: [...]}` (tối đa 16 phần tử); thử địa chỉ đầu vào, cấu hình, catalog trong Core và loopback 11434/1234. Tổng tối đa 16 URL duy nhất, vượt thì từ chối; 4 luồng, mỗi đích tối đa 4 GET × 1 giây, khai hạn tác vụ 30 giây. Không quét toàn subnet hoặc gọi DNS; IP LAN mới cần nhập tay. Trả `{danh_sach:[kết_quả_kiểm], so_da_kiem}`. Tìm không ghi catalog để không chuyển model cùng ID sang máy chưa chọn; chọn máy rồi Kiểm tra kết nối để cập nhật. Core có thể cấp danh sách ứng viên LAN/Tailscale qua cửa chung sau này.

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

Ví dụ dưới đây chỉ là cấu hình DEMO để nạp qua `CoreGia.dat_cau_hinh("e_hoi_ai", ...)` hoặc màn cấu hình:

```json
{
  "local_ai": {"url": "http://127.0.0.1:12345", "timeout_giay": 60},
  "quy_tac_model": [
    {"mau_ma_prompt": "demo.*", "uu_tien": "model-demo", "du_phong": []}
  ]
}
```

## Contract

Ba schema `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai` trong `contract/` giữ nội dung từ `_chung/contract/` trong repo, chỉ chuẩn hóa xuống dòng LF. Pytest kiểm SHA-256 LF từng cặp; gói chạy độc lập không truy cập thư mục `_chung/`.

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

Lệnh nghiệm thu chuẩn vẫn là `.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai`. Wheel 2.2.0 hiện tự tạo `CoreGia()` rỗng trong CLI, không có tham số/fixture cấu hình DEMO hay dịch vụ Local giả; ba ví dụ nhận `CHUA_CAU_HINH`. Đây là điểm **Cần Core**, nên AI-11 chưa đạt toàn bộ điều kiện nghiệm thu. Không thay cổng hoặc gắn nhánh giả lập vào runtime.

`chay_demo_voi_local_gia.py` chỉ là hồi quy bổ sung: bật Local giả trên loopback, gọi `CoreGia(app).dat_cau_hinh(...)`, chạy nguyên ba ví dụ và một ca AI-9. Không còn tùy chọn `--sdk-thu`. Test khác dùng CoreGia riêng mỗi ca, ngăn thật của SDK, `gay_xung_dot_ngan` và `xem_ngan`; không còn test so băm cổng tạm. Đã kiểm bằng Core giả (CoreGia), chưa kiểm Core thật/model thật/Linux.


Bộ UI `node --test e_hoi_ai/tests/ui/cau_hinh.test.mjs` được pytest gọi tự động; cần Node có sẵn, không cài thư viện hoặc gọi mạng. Kiểm đọc/phân trang, lưu/CAS/tải lại, lỗi nhập cạnh ô, thứ tự quy tắc/dự phòng, các nút kiểm/tìm thành công/thất bại, phản hồi cũ khi sửa địa chỉ, không lộ chi tiết lỗi, Cloud không có công tắc hoặc ô bí mật. UI-AI-1 không gọi `.bi_mat`; kiểm “chỉ 4 ký tự cuối” thuộc màn API key UI-AI-2. Đây là DOM/KttCore giả. `node e_hoi_ai/tests/ui/dung_anh_demo.mjs` dựng HTML từ chính màn gói, CSP chặn mạng ngoài. `node e_hoi_ai/tests/ui/chup_anh_demo.mjs` dùng Chrome headless/CDP trên loopback, cố định viewport rộng/hẹp, kiểm không tràn ngang rồi chụp ba ảnh ở `e_hoi_ai/docs/anh-ui-ai-1/`; có thể đặt `UI_CHROME` nếu Chrome ở vị trí khác. Đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật. Công cụ AI-7 giữ nguyên `--url`, không đọc tệp cấu hình.

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
