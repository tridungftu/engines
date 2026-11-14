# Thay đổi

## 0.3.0 — 14/11/2026 — AI-2

- Nối `ai.hoi_theo_yeu_cau@1`: nhận `yeu_cau_ai`, trả đủ phong bì `tra_loi_ai`, nguồn gốc và vị trí trích dẫn.
- Truyền khuôn phản hồi chứa `du_lieu` và trích dẫn qua Ollama `/api/chat` (`format`) hoặc OpenAI-compatible (`response_format.json_schema`).
- Kiểm tập con JSON Schema 2020-12 offline bằng thư viện chuẩn, từ chối từ khóa chưa hỗ trợ; sai khuôn chỉ hỏi lại một lần rồi trả `AI_TRA_SAI_KHUON`.
- Giữ nguyên `chuyen_tiep` theo byte JSON chuẩn hóa, không gửi Local; từ chối vượt trần 64 KiB/32 KiB trước mạng.
- Giữ hậu kiểm trích dẫn AI-1, bổ sung đối chiếu dữ liệu có kiểu; kiểm lỗi Local, hủy và chống nộp trùng với 0 lượt Cloud.
- Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; kết quả kiểm cuối ghi trong `e_hoi_ai/docs/VIEC.md` của repo. Chưa kiểm Core thật hoặc model thật.

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
