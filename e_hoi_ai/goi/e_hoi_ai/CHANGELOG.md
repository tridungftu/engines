# Thay đổi

## AI-4 — 14/11/2026 — DEMO và kiểm khởi động (trên gói 0.4.0)

- Mở rộng `chay_thu_demo` thành ba ca DEMO: tiền/ngày có căn cứ, câu không có đáp án, yêu cầu có khuôn tiền kèm VND/ngày ISO.
- Bộ chạy Local giả gọi trực tiếp `CoreGia().chay_thu_demo(app)`; cấu hình tạm nằm dưới `tests/`. Đây là cổng đạt thay lệnh SDK thu riêng cần máy AI.
- Thêm kiểm đáp án và cổng lỗi/rỗng; chạy tiến trình thật nhận stdin qua `MayChuGia` HTTP loopback cho cả hai năng lực, xác thực và nộp kết quả trước kết thúc; 0 lượt Cloud.
- Đã kiểm bằng Core giả (CoreGia); kết quả kiểm AI-4 ghi ở `e_hoi_ai/docs/VIEC.md`. Không sửa lõi Local/Cloud hoặc hợp đồng SDK/API.

## 0.4.0 — 14/11/2026 — Gộp AI-2 và AI-3

- Giữ phát hiện/chọn model, cache, lý do chọn và bảo vệ mạng AI-3 cùng toàn bộ xử lý khuôn AI-2.
- `_kiem_model` trả loại API từ catalog đã kiểm khả dụng; không thêm GET để chọn cách gửi khuôn.
- Luồng hỏi theo yêu cầu truyền kiểm hủy vào bộ chọn model trước khi gọi mạng.
- Hợp nhất tài liệu hai lát, cập nhật SHA-256; kết quả kiểm việc gộp ghi trong `e_hoi_ai/docs/VIEC.md`.

## 0.3.0 — 14/11/2026 — AI-2

- Nối `ai.hoi_theo_yeu_cau@1`: nhận `yeu_cau_ai`, trả đủ phong bì `tra_loi_ai`, nguồn gốc và vị trí trích dẫn.
- Truyền khuôn phản hồi chứa `du_lieu` và trích dẫn qua Ollama `/api/chat` (`format`) hoặc OpenAI-compatible (`response_format.json_schema`).
- Kiểm tập con JSON Schema 2020-12 offline bằng thư viện chuẩn, từ chối từ khóa chưa hỗ trợ; sai khuôn chỉ hỏi lại một lần rồi trả `AI_TRA_SAI_KHUON`.
- Giữ nguyên `chuyen_tiep` theo byte JSON chuẩn hóa, không gửi Local; từ chối vượt trần 64 KiB/32 KiB trước mạng.
- Giữ hậu kiểm trích dẫn AI-1, bổ sung đối chiếu dữ liệu có kiểu; kiểm lỗi Local, hủy và chống nộp trùng với 0 lượt Cloud.
- Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; kết quả kiểm cuối ghi trong `e_hoi_ai/docs/VIEC.md` của repo. Chưa kiểm Core thật hoặc model thật.

## 0.3.0 — 14/11/2026 — AI-3

- Thêm mô-đun `chon_model.py`: phát hiện Ollama, LM Studio native v1/v0, OpenAI-compatible từ API; giữ ID và thứ tự nguồn, không xếp hạng model.
- Catalog trong bộ nhớ 300 giây; kiểm khả dụng mới mỗi lượt và trước POST, không dùng model đã biến mất hoặc metadata chỉ rõ từ xa/chưa tải/không phải LLM.
- Chọn theo tham số ưu tiên, quy tắc prompt và dự phòng có thứ tự, rồi model khả dụng đầu tiên; không có model trả lỗi có thể thử lại.
- Thêm trường `ly_do_chon_model` vào kết quả hỏi tài liệu và phiếu gói. Không thay SDK/API/Core; giữ điểm nối để AI-2 dùng chung.
- Đã kiểm bằng Core giả (CoreGia): SDK thu 1/1 ĐẠT; pytest 176 passed, 0 skipped; kiểm độc lập mã 0; Cloud 0 lượt. Chưa kiểm Linux/Core thật/model thật.

## 0.2.0 — 14/11/2026 — AI-1

- Chuyển lõi Local, DTO và adapter từ mã cũ; nối `ai.hoi_tai_lieu@1` qua SDK 2.0.
- Giữ chặn DNS/proxy/redirect, chỉ dùng IP loopback/LAN/Tailscale và kiểm model trước khi gửi tài liệu.
- Kiểm trích dẫn nguyên văn, giá trị thuộc trích dẫn và số liệu thuộc nguồn; hạ kết quả sai kèm cảnh báo.
- Prompt thiếu/rỗng trả `THIEU_PROMPT`; Local lỗi trả `LOCAL_AI_KHONG_SAN_SANG` có thể thử lại; 0 lượt Cloud.
- Thêm tiến độ, kiểm hủy, nhật ký metadata ra stderr và DEMO tối thiểu qua HTTP Local giả.
- Đã kiểm bằng Core giả (CoreGia): SDK thu 1/1 ĐẠT; pytest 141 passed, 0 skipped; kiểm độc lập mã 0. Chưa chạy thực tế trên Linux, Core thật hoặc model thật.

## 0.1.0 — 14/11/2026 — AI-0

- Dựng khung SDK 2.0.0 với hai năng lực tạm trả `CHUA_LAM`.
- Thêm ba contract dữ liệu dùng chung và schema cấu hình máy.
- Đọc JSON ngoài gói, cho phép khởi động khi thiếu cấu hình.
- Đã kiểm bằng Core giả (CoreGia); chưa có DEMO hỏi AI thành công (AI-4).
