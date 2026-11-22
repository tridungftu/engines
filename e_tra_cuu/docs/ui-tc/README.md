# Ảnh UI-TC — 21/11/2026

Ảnh chụp bằng Chromium headless, dựng **mã màn thật** với KttCore giả tại
`../../tests/ui/xem_ui_tc.html`. Chỉ dữ liệu DEMO; trang có CSP chặn kết nối
mạng. Không phải ảnh trong khung Core thật. Đã kiểm bằng Core giả (CoreGia)
cho nghiệp vụ và KttCore giả cho màn.

| Ảnh | Trạng thái | Kích thước |
|---|---|---|
| [Cơ bản desktop](co-ban-desktop.png) | Chưa đo; Nâng cao thu gọn | 1100 × 820 |
| [Cơ bản mobile](co-ban-mobile.png) | Một cột, Nâng cao thu gọn | 390 × 1120 |
| [Nâng cao desktop](nang-cao-desktop.png) | Đủ bộ quy tắc và 15 trần | 1100 × 2400 |
| [Lỗi nhập desktop](loi-nhap-desktop.png) | Trần số trang = 61; lỗi cạnh ô, không lưu | 1100 × 2400 |

So với ảnh mẫu: thẻ trắng trên nền xám nhạt, viền mảnh, tiêu đề và nhãn
trạng thái góc phải; hai cột trên desktop, một cột trên mobile; cảnh báo
vàng giải thích chưa có ngưỡng đo/phê duyệt. Bổ sung focus bàn phím, nhãn
gắn ô và thông báo lỗi cho trình đọc màn hình.

Để dựng lại, dùng Chromium headless đã cài, không cần tải thư viện hoặc
chạy máy chủ. Mở HTML bằng URL `file:///…/e_tra_cuu/tests/ui/xem_ui_tc.html`
với các cờ `--allow-file-access-from-files --disable-background-networking
--virtual-time-budget=1500 --window-size=1100,820 --screenshot=<ảnh>`.
Thêm `?nang_cao` để mở Nâng cao, `?loi` để dựng lỗi nhập. Thay kích thước
theo bảng trên. Tệp HTML chỉ phục vụ kiểm, không gửi trong gói engine.

`node --test e_tra_cuu/tests/ui/*.test.js`: đọc/lưu, lỗi nhập, CAS, thu
quyền, phản hồi chậm/unmount, chống lưu lặp, ngưỡng chỉ đọc, metadata schema,
XSS và cấm mạng. Kiểm nút kết nối/bí mật bốn ký tự cuối **không áp dụng**:
UI-TC không có máy/dịch vụ hoặc bí mật; test xác nhận không truy cập hai
cổng `thao_tac`/`bi_mat`, không tự thêm ô API key.
