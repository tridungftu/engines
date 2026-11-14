# Nguồn gói OCR-1 — 14/11/2026

Phần mềm nội bộ, dùng nội bộ tập đoàn theo quyết định cuối của engine OCR.
Chuyển lõi từ `ma-nguon/` ngay trong repo; mã nguồn cũ giữ nguyên. Không
chép thư mục dữ liệu/cấu hình ABBYY, model hay vendor/mask_ocr trong OCR-1.

| Phần | Nguồn / giấy phép |
|---|---|
| `engine.json`, `e_ocr/__init__.py`, `e_ocr/chay.py` | Từ khung OCR-0 theo API v1, nối hai action chung lõi, tăng metadata phiên bản 1.0.1; chỉ dùng SDK ngoài Core |
| `e_ocr/lop_chu.py` | Chép và chuyển thể `ma-nguon/lop_chu.py`: giữ thuật toán đọc chữ ẩn, kiểm ma trận/xoay trang, tọa độ và trần; đổi kết quả sang schema chung, callback hủy SDK và bổ sung tự đếm trang/kiểm PNG/JPEG |
| `e_ocr/van_ban.py` | Chép và thay lớp vỏ `ma-nguon/van_ban.py`: bỏ contract/UUID/DOCX và Core cũ; dùng `viec.mo_tep`, lớp chữ/Hot Folder, băm đầu vào và schema SDK 2.0 |
| `e_ocr/bang.py` | Chuyển quy tắc ô trống/ô gộp, không suy bảng từ text và trần 100 hàng/40 cột từ `ma-nguon/bang.py`; đổi parser DOCX cũ sang đường kẻ/ký tự PDF sẵn có; chưa xuất Word |
| `e_ocr/abbyy.py` | Chuyển vai trò backend của `ma-nguon/abbyy.py`, viết lại vận chuyển Hot Folder cục bộ; bỏ `lib/cong_ocr.py`, kiểm phiên/ACL và cầu nối phụ thuộc Core cũ; chỉ dùng thư viện chuẩn + SDK |
| `e_ocr/cau_hinh_may.py`, schema cấu hình | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `e_ocr/kho_tam.py` | Viết mới; khóa tệp thư viện chuẩn `msvcrt` trên Windows, `fcntl` trên Linux; không có thư viện ngoài |
| `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte từ `_chung/contract/van_ban_tai_lieu.schema.json`, định nghĩa theo `LOAI-DU-LIEU-RIENG.md` §2.1; test so SHA-256 |
| `demo/` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. PDF lớp chữ 3 trang sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model |
| SDK 2.0.0 | Wheel do Core phát hành trong repo; giữ nguyên điều khoản của bộ phát hành. Không đóng wheel vào gói engine |

SDK và dependency được ghim trong `requirements.lock`. Các pin giữ đúng
phiên bản đo được trong `ma-nguon/requirements.lock`, không cài/nâng qua
mạng; bỏ numpy do không dùng ở OCR-1. Giấy phép theo bảng nguồn cũ và
metadata gói cài; khi dựng wheel phải giữ mọi thông báo giấy phép đi kèm.

| Thư viện | Phiên bản | Giấy phép / vai trò |
|---|---|---|
| pdfplumber | 0.11.10 | MIT; đọc lớp chữ, trang và đường kẻ PDF |
| pdfminer.six | 20260107 | MIT; parser do pdfplumber yêu cầu |
| Pillow (`PIL`) | 12.3.0 | MIT-CMU; kiểm tệp ảnh PNG/JPEG và dependency của pdfplumber |
| pypdfium2 | 5.13.0 | BSD-3-Clause, Apache-2.0 và giấy phép dependency đi kèm; dependency bắt buộc của pdfplumber, không gọi render |
| charset-normalizer | 3.4.7 | MIT; dependency pdfminer.six |
| cryptography | 49.0.0 | Apache-2.0 OR BSD-3-Clause; dependency pdfminer.six |
| cffi | 2.0.0 | MIT; dependency cryptography |
| pycparser | 3.0 | BSD-3-Clause; dependency cffi |

ABBYY là phần mềm thương mại ngoài pip; quyền triển khai/giấy phép vẫn
theo các việc chờ Anh có sẵn. OCR-1 không chép hoặc gọi ABBYY thật.
Không dùng PyMuPDF/defusedxml vì chưa được ghim trong lock cũ.

Môi trường `.venv --system-site-packages` dùng thư viện sẵn có và pytest;
chưa là cài máy sạch. Lock hiện chỉ ghim phiên bản, không dùng
`--require-hashes`; hash wheel Windows/Linux và bài máy sạch thuộc OCR-6.
SHA-256 wheel SDK phát hành, đã so với
`docs/goi-gui-engine/sdk-2.0.0/SHA256SUMS.txt`:

```text
a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892  kho_tri_thuc_sdk-2.0.0-py3-none-any.whl
```

Băm SHA-256 các tệp trong gói (không tự băm `NGUON.md` để tránh tự tham chiếu):

```text
c4338ed6792e2e2d0cffb4083eb566d6912690266551207b7c027553f961a90a  CHANGELOG.md
bc1af1f36a1b4de11f47395c56ffe2030e1a6202f4ca21740f36c86166376893  contract/cau_hinh_may.schema.json
d73a80f276eef43536ee14810ef46a1df73d476a9b4f02cc4f3bd163f4d73902  contract/van_ban_tai_lieu.schema.json
8521635ce091f072c116ae64a5064b1d3baba70c78dfb6a4fcdffb212e9dfbd9  demo/cau_hinh.demo.json
9c62de68d53c5433d46378e73b8199c34904c2a6e308ec6616db4243229e5879  demo/DEMO-lop-chu-3-trang.pdf
d406d94e40aa25046ee87084931f69a1595ed6dd2c9386869ddc8e905dab05e3  demo/van_ban_tai_lieu.demo.json
e88490948ec9e2c587d7cffee052cfb666d914611cfd0e7bf32a9fc775a8c92c  e_ocr/__init__.py
f30fe4200efed852b5fe7fc3f6b80960f78be4eb8dfa472d16987a53e8a4969b  e_ocr/abbyy.py
b11102034a8b77d18bf2a5043c05ac2d1f71a12614a7fb3a7f87f60056c1b5ad  e_ocr/bang.py
3dd03176ef7ec59364be1d8ba3e8b21a04b9feaca3d08e57e5b23aea37f31625  e_ocr/cau_hinh_may.py
f7eef209a9a9a21f6a0f2bad6d39faeb8ad86c7970f9a5a1f6c983896664c098  e_ocr/chay.py
be5439b78fcc2838d6a3ed32fb23dcf30707f49c430b18a14945a9b824c3b0de  e_ocr/kho_tam.py
46abf54b034eed40233efac67f0f50e2c8a7e46b446b0e75fca6d59e3c749115  e_ocr/lop_chu.py
b494b15b05d426669417dfdcffb8798447b824b6f91a0f4ccc75802269812fe2  e_ocr/van_ban.py
e84d8027cef16e729d581112d887568c15844a7278a3bf0de5ae3341ff2a0ae8  engine.json
0760df89056562df15e75647e71d5d50b44f336c34f5f6f6b126301f63d7914a  README.md
2bf61ea863cb6d43816f64206acc6475a1f0f505fd56fa9c0d8c5e9105f94142  requirements.lock
```
