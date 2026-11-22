# Ảnh UI-MASK — chưa chụp được trong phiên 21/11/2026

Chưa có PNG và chưa kiểm bố cục bằng browser thật. Không dùng ảnh vẽ lại thay ảnh màn chạy.

Fixture DEMO đã có tại `e_mask/tests/ui/xem_thu.html`, dùng đúng module và stylesheet trong gói cùng KttCore giả trong RAM. Chạy từ gốc repo:

```text
.venv/Scripts/python -B -m http.server 8766 --bind 127.0.0.1 --directory .
```

Mở `http://127.0.0.1:8766/e_mask/tests/ui/xem_thu.html`; chụp màn rộng 1280 px và màn hẹp 390 px. Nội dung có nhãn DEMO, ngày 21/11/2026, không tên gốc hoặc bí mật. Nút Lưu/Tải lại và màn duyệt chạy bằng fixture, không gọi Core thật hoặc dịch vụ ngoài.

Giới hạn môi trường đã gặp:

- CUA browser hai lần timeout khi khởi tạo; khung browser tích hợp trả `The browser access host is unavailable`.
- Chrome headless không dựng được ảnh: GPU process không dùng được; các lần dựng khác không hoàn thành, không có PNG.
- Computer Use từ chối Microsoft Edge và Google Chrome: `Computer Use was not approved to use Microsoft Edge` / `Computer Use was not approved to use Google Chrome`.

Tiêu chí PR kèm ảnh vẫn chưa đạt; cần quyền công cụ browser trước khi chụp và đối chiếu với hai ảnh mẫu.
