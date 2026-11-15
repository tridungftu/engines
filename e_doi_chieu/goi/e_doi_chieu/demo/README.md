# DEMO bản Word đã chốt

`DEMO-ban-chot.docx` chứa Công ty DEMO Ánh Dương, 1.000.000 VND, ngày
2026-10-30; bảng có ô trống và ô gộp ngang/dọc. Hoàn toàn dữ liệu giả.
Tệp nhỏ, tạo xác định từ helper ngoài gói tại `e_doi_chieu/tests/test_dc2.py`;
băm nguyên bytes ghi trong NGUON.md. Không có sửa đổi/comment/quan hệ ngoài.

DC-12 giữ đúng một ví dụ này trong `chay_thu_demo`, chạy bằng CLI SDK
chuẩn, không cần máy AI. Chuỗi có tệp con/ngăn/Local/OCR giả ở ngoài gói:
`e_doi_chieu/tests/chay_demo_voi_core_gia.py` (10 ca). Đáp án văn bản
giả ở `tests/fixtures/DEMO-dap-an-dc12.json`; không thêm ID tệp chưa
nạp hoặc cờ DEMO vào runtime. Chi tiết và phần chưa kiểm máy thật:
`e_doi_chieu/docs/DC-12-KIEM-VA-GIOI-HAN.md`.
