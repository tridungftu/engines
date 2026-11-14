# Thử Local AI bằng DEMO

1. Cài Python 3.11+, tạo `.venv` tại gốc worktree và cài SDK 2.0.0 từ wheel trong repo.
2. Chạy `e_hoi_ai\cong-cu\THU-LOCAL-AI-THAT.cmd` để kiểm tra chế độ khô, không gọi mạng.
3. Trên máy có Tailscale, chạy trong Command Prompt: `e_hoi_ai\cong-cu\THU-LOCAL-AI-THAT.cmd --that --url http://<IP-LOCAL>:<PORT>`.
4. Xem bảng từng model và tệp `ket-qua-local-demo-*.json` trong thư mục chạy; ca Local tắt là giả lập, Cloud phải bằng 0.
5. Ca hiện dùng DEMO trong manifest trên nhánh AI-3; bộ AI-4 chưa có trên nhánh này và cần đối chiếu sau khi gộp.
