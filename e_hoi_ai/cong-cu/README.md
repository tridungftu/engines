# Thử Local AI bằng DEMO
1. Cài Python 3.11+ và Python Launcher (`py`) trên Windows.
2. Chạy `e_hoi_ai\cong-cu\THU-LOCAL-AI-THAT.cmd`; nếu thiếu `.venv`, công cụ tự tạo và cài SDK từ wheel trong repo.
3. Mặc định là chạy khô, không gọi mạng; chạy thật từ Command Prompt với `e_hoi_ai\cong-cu\THU-LOCAL-AI-THAT.cmd --that --url http://<IP Tailscale máy AI>:<cổng>`.
4. Công cụ thử từng model với ba ca `chay_thu_demo` trong `engine.json`, hiển thị đáp án, trích dẫn và thời gian.
5. Xem tệp `ket-qua-local-demo-*.json` trong thư mục chạy; ca Local tắt là giả lập, số lượt Cloud phải bằng 0.
