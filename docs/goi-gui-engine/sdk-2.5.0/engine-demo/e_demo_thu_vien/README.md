# e_demo_thu_vien — Làm gọn văn bản (DEMO)

Năng lực `van_ban.gon_khoang_trang@1` nhận và trả `van_ban`. Thư viện ngoài
`ktt-demo-thu-vien==1.0.0` gộp khoảng trắng, tab và xuống dòng thành một dấu cách;
chữ và dấu tiếng Việt giữ nguyên. Ví dụ trong `chay_thu_demo` trả
`Xin chào, đây là DEMO. Dòng thứ hai.` Chỉ dùng dữ liệu DEMO.

Gói cần SDK `>=2.4.0 <3.0.0`. Trên Core có hỗ trợ cài thư viện offline: nhập
gói → Xem trước (có thư viện 1.0.0) → Duyệt cài → Bật → Chạy thử DEMO.
Core tự cấp SDK và cài thư viện vào `<gói đã cài>.thu-vien` cạnh gói;
Admin không cần cài wheel SDK hay thư viện bằng tay. Engine chỉ import
`kho_tri_thuc_sdk`, không dùng mã nguồn Core.

## Dựng lại wheel DEMO

Từ thư mục gói, chạy bằng Python 3.11 trở lên, không cần mạng hay công cụ build:

```text
python -B -X utf8 tao_wheel_demo.py
```

Script chứa toàn bộ mã thư viện, ghi wheel vào `wheels/`, in SHA-256.
Timestamp ZIP, thứ tự tệp và quyền được cố định; ZIP không nén, có RECORD băm
từng tệp. Chạy lại phải ra cùng bytes và cùng băm trong `requirements.lock`.
`wheels/` chỉ chứa wheel; không đặt SDK vào đây.

## Tự kiểm khi phát triển

Trong môi trường thử riêng đã có SDK và thư viện từ wheel DEMO, chạy:

```text
python -B -X utf8 -m kho_tri_thuc_sdk.thu .
```

CoreGia chỉ chạy năng lực trong bộ nhớ; không tự cài phụ thuộc cho tác giả.
Test `test_goi_e_demo_thu_vien` kiểm gói thật, cài bằng `cai_thu_vien` và chạy
tiến trình con chỉ có SDK do Core dựng cùng thư viện, không có `src`.
