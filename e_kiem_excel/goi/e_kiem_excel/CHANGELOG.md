# Thay đổi

## 0.1.0 — 18/11/2026
- EX-0: khung hai năng lực (tạm `CHUA_LAM`), cổng SDK có nhật ký an toàn.
- Kiểm tệp/ZIP/XML và trần trước openpyxl; bộ DEMO tự ghi công thức và giá trị lưu.

- EX-4: đọc khuôn `xay_dung_klgt`, giữ nhận diện/nhóm/khóa gốc; số dùng Decimal,
  giữ số tổng hợp 0 và số lẻ nhỏ, trả trường §4.2 và JSON §5.2 trong RAM.
- Ba cảnh báo: thành tiền lệch KL × đơn giá, số dạng chữ, khóa trùng; dừng ở Cộng.
- Tiền tệ lấy từ tham số hoặc đơn vị ghi rõ trong bảng; chưa rõ thì trường tiền null,
  JSON giữ số thập phân kèm đơn vị null; không mặc định VND. DEMO thứ ba chạy được.
