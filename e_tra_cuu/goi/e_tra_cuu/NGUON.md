# Nguồn và phụ thuộc — TC-0, 15/11/2026

Gói mới theo phiếu `e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md` §1–5,
API-ENGINE-v1 và hai hướng dẫn SDK 2.0.0. Không có lõi cũ tại chỗ để chuyển;
không tạo `ma-nguon/`. Mã khung/schema/test mới viết trong lát TC-0.

| Thành phần | Nguồn nội bộ repo | Phiên bản / SHA-256 |
|---|---|---|
| SDK | `docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | 2.0.0 · `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `e_tra_cuu/ngan.py` | `_chung/mau-ma/ngan.py`, NGAN-0, PR #34 theo lead | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_tra_cuu/cau_hinh.py` | `_chung/mau-ma/cau_hinh.py`, NGAN-0, PR #34 theo lead | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |

Hai mẫu chép nguyên bytes bằng Copy-Item, không sửa hoặc import `_chung` ở runtime.
Test so SHA-256 **chỉ đổi CRLF thành LF**, không strip/biên tập.
Băm SDK tính trên wheel nguyên bytes, đã khớp `SHA256SUMS.txt`.

Runtime chỉ thư viện chuẩn Python >=3.11 và SDK 2.0.0; ghim SDK trong
`requirements.lock`. Không thêm thư viện ngoài. Pytest 9.1.1 là công cụ test có
sẵn qua venv `--system-site-packages`, không đóng gói và không phải dependency
runtime. Kiểm thực tế trên Windows/Python 3.13.14; chưa chạy Linux.

SDK và hai mẫu lấy từ bộ nguồn nội bộ được giao. Metadata wheel không khai trường
License; không tự suy diễn giấy phép nguồn ngoài. Lát này không tải/nhúng mã,
mô hình hoặc dữ liệu bên ngoài. Không chép schema của loại chưa duyệt TC-Q13.
Chỉ dữ liệu DEMO trong test, không tài liệu thật; không mạng/Cloud khi kiểm.
