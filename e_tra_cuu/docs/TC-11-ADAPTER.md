# TC-11 — ranh giới adapter bài đo, 15/11/2026

Đây là **seam Python nội bộ của công cụ đo**, chỉ được kiểm bằng adapter giả;
không phải hợp đồng API Core mới, không yêu cầu Core triển khai route riêng.
`CoreThat.kiem_moi_truong` hiện luôn từ chối trước mạng/khóa. Không tự chạy
`--that`. Bản giao chưa thể đo thật dù Anh đã có địa chỉ Core.

API-CORE-v1 §5 có cửa chạy nút module chung
`POST /api/v1/module/{ma}/nut/{nut}/chay` và xem/hủy việc. Tuy nhiên chạy thử
quản trị chỉ nhận văn bản/`tep_demo`, chi tiết việc có thể cắt văn bản 2.000 ký
tự. Chúng không xác nhận đầy đủ discovery/runtime/context/tokenizer, fan-in,
quyền tệp con, kết quả đo không cắt và nơi giữ báo cáo. API-ENGINE-v1 §c.2 là
cửa **engine nhận việc**, không dùng làm cửa nộp bài thử. Không ghép các cửa
này theo phỏng đoán; CoreGia không chứng minh Core đã có chúng.

Sau khi lead nhận hợp đồng public của Core, adapter phải dùng cửa chung đã
được xác nhận, chỉ nhận địa chỉ và bộ DEMO do Anh cấp; tắt redirect/proxy tự
động không được duyệt, TLS cho máy khác. Xác thực theo hợp đồng public bằng
nhập ẩn/handle; không CLI/env/tệp/log. Không gọi trực tiếp engine/provider,
không import engine khác, không SQL, không sửa cấu hình hệ thống.

Các phương thức công cụ đang kiểm (không tự nhận đối tượng qua CLI):

| Seam | Dữ liệu / yêu cầu |
|---|---|
| `kiem_moi_truong(ghim)` | Bằng chứng Core/AI/OCR/TX/embedding: mỗi mục `co_that`, `bam_kiem`. `ghim` phải khớp; `chi_local=true`. Đúng ba vai trò `gpt_oss_20b`, `qwen3_8b`, `gemma`, ID riêng đúng discovery; mỗi model có `id`, `runtime`, `phien_ban`, `context_hieu_dung`, `bam_phat_hien`, `local=true`. Không suy họ/capability từ tên. |
| embedding | Cùng metadata discovery; thêm `lead_chon=true`, `ho_tro_nhung=true`, `bam_kiem_tieng_viet`. Thiếu một mục từ chối đúng `TC_CHUA_CO_MOI_TRUONG_THU`. |
| `chuan_bi(ca, model, ghim)` | Core chuẩn bị câu hỏi/nguồn từ bộ đã nạp đúng quyền; không đáp án hoặc trường `local` giả. Trả `ma_tuong_quan` **trước gửi**, `goi_ai` đúng đường đã ghim và `bam_noi_dung_gui`. Nhánh AI cần `nguon_dem=tokenizer_runtime`, `day_du_khung=true`, `model_id`, `token_vao`, `token_ra_du_phong`; đếm đầy đủ prompt/khuôn/context/wrapper. Không có tokenizer thì chưa đo, vượt context thì từ chối trước gửi. |
| `gui_viec(ca, model, plan)` | Một lần nộp qua cửa chung Core; không retry tự động. Nhận `ma_tuong_quan` khớp plan. 202/CHO/CHUA_RO hoặc mất ACK → `ChuaRo` cùng mã; dừng cả lượt, không batch/resubmit. Core giữ cơ chế chống trùng/lượt đang chạy. |
| `nhan_ket_qua(ticket)` | `XONG` mới có `dau_ra` đầy đủ không cắt theo JSON xuất TC. Nhánh AI phải khớp `model_id`, `model_phien_ban`, `runtime`, `local=true`; mọi nhánh khớp `ghim`, `bam_noi_dung_gui`, `cat_ngam=false`, `batch=false`. CHUA_RO/CHO/mất phản hồi giữ chưa rõ; HUY dừng nộp tiếp. |
| `so_do` | Chỉ sao số với `nguon=runtime_qua_core`: `context_hieu_dung`, `token_vao/ra`, `thoi_gian_runtime_giay`, `thoi_gian_core_giay`, `so_doan`, `so_ung_vien`. Số thiếu/sai là null + lý do; không nhận ký tự/4 là token runtime. Discovery context thật được ghi riêng cho nhánh AI; đường Python không có token/context model. |
| `bien_ban_core()` | Theo danh sách cố định `CA_CORE`: trạng thái dat/khong_dat + băm biên bản, chỉ từ Core. Thiếu cửa để chưa kiểm. Tải riêng thêm `bai_tai_rieng=true`, số người và đồng thời thực đo; không suy tải từ thời gian model. Adapter giả luôn gắn nhãn đã kiểm giả. |
| `giu_bao_cao(report)` | Giữ RAM hoặc gửi Core có quyền; nếu chưa có cửa thì không fallback ghi đĩa. Chỉ `--bao-cao` mới xuất một artifact DEMO trong workspace chỉ định. |

Manifest `--ghim` là JSON DEMO `phien_ban=1`, chỉ đúng các trường:
`nhan`, `phien_ban`, `engine`, `danh_muc`, `cau_hinh`, `prompt`.
Ba mục đầu mỗi mục `{phien_ban,bam}`; `prompt` ánh xạ bốn tác vụ AI sang
`{ma,phien_ban,bam}`. Đây là tham chiếu bản ghim trên Core, **không** phải
JSON giá trị cấu hình trên máy. Hash bytes của manifest do lead cấp qua
`--bam-ghim`. Bản ghim của Core phải khớp trước gửi và khi đọc kết quả.

Bộ đầu vào giữ cấu trúc TC-10: `bam-DEMO.json`, `bo-ca-DEMO.json`,
`dap-an-DEMO.json`, nguồn DEMO. Công cụ kiểm bytes/băm/phiên bản của nguồn,
ID ca duy nhất và tập đáp án khớp. Bốn tỷ lệ dùng cùng quy tắc chấm TC-10;
không dựa điểm model. Ca chưa chạy/từ chối context không được tính đạt hoặc
giả thành mẫu số đã đo. Số ca chưa xong và số dự kiến luôn giữ riêng từng
model, kể cả khi dừng giữa chừng. Bộ TC-10 hiện có 38 ca phân loại/trả lời;
ba tác vụ cắt đoạn, câu hỏi/hàm và xếp hạng cần lead ghim thêm đáp án
`du_lieu` đầy đủ đúng cấu trúc kết quả, gồm cả vị trí/tham số/hoán vị ứng viên.
Không có đáp án thì không coi đã kiểm ba tác vụ này. Tiền/ngày được so cùng
thực thể/trường/mã tiền tệ, ngoài việc kiểm trích dẫn đúng nguồn/bản/offset.

Danh sách Core thật gồm RLS hai pháp nhân/nhóm 07 trước AI, quyền mọi nguồn
cache, thực thể A/B, hết cache theo phiên bản/nhóm/thu quyền/duyệt/công bố,
Tra lại từ đầu, dừng tầng 1/2 và tầng 3 nền HTTP 202, K5 mới/mâu thuẫn,
trích dẫn đúng trang hoặc không có trang, UI cấu hình/trạng thái trong khung
Core, PostgreSQL/pgvector/unaccent/pg_trgm, bài tải 20 đồng thời/150 người.
Không có bằng chứng thì báo chưa kiểm, không tổng hợp thành nghiệm thu.
TC-Q06 tiếp tục **không tự xóa**. TC-Q08/15 chờ số đo thật và lead/Anh review,
không tự chốt model/ngưỡng hoặc kích hoạt nhóm.
