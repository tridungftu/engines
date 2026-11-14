# Nguồn gói OCR-2 — 14/11/2026

Giấy phép mã nội bộ: **phần mềm nội bộ, dùng nội bộ tập đoàn** theo quyết
định cuối của engine OCR.
Chuyển lõi từ `ma-nguon/` ngay trong repo; mã nguồn cũ giữ nguyên. Không
chép thư mục dữ liệu/cấu hình ABBYY hoặc model. OCR-2 chỉ chuyển phần cần
dùng của `vendor/mask_ocr` đã có trong repo; không đọc nguồn ngoài workspace.

| Phần | Nguồn / giấy phép |
|---|---|
| `engine.json`, `e_ocr/__init__.py`, `e_ocr/chay.py` | Từ khung OCR-0/OCR-1 theo API v1; tăng metadata phiên bản 1.0.2. `chay.py` giữ nguyên cho OCR-3, không đổi API |
| `e_ocr/lop_chu.py` | Chép và chuyển thể `ma-nguon/lop_chu.py`: giữ thuật toán đọc chữ ẩn, kiểm ma trận/xoay trang, tọa độ và trần; đổi kết quả sang schema chung, callback hủy SDK và bổ sung tự đếm trang/kiểm PNG/JPEG |
| `e_ocr/van_ban.py` | Chuyển từ `ma-nguon/van_ban.py` ở OCR-1; OCR-2 chỉ nối `doc_theo_nguon`, giữ đọc bằng SDK, lớp chữ sẵn, băm và phong bì |
| `e_ocr/bang.py` | Chuyển quy tắc ô trống/ô gộp, không suy bảng từ text và trần 100 hàng/40 cột từ `ma-nguon/bang.py`; đổi parser DOCX cũ sang đường kẻ/ký tự PDF sẵn có; chưa xuất Word |
| `e_ocr/abbyy.py` | Chuyển vai trò backend của `ma-nguon/abbyy.py` ở OCR-1; OCR-2 thêm lỗi có bằng chứng chưa nhận, callback đã nhận/chưa rõ và dùng cùng mã giữ hạn mức. Không nhập cổng/lượt bền cũ |
| `e_ocr/chon_nguon.py` | Chuyển thứ tự ưu tiên, bảo vệ đã nhận và bảng lý do từ `ma-nguon/chon_nguon.py`; thay sổ/cổng/lượt bền cũ bằng `KhoTam`, không gọi SDK riêng |
| `e_ocr/tesseract.py` | Chuyển nhánh `doc_mask_ocr`/`image_text` của mã cũ thành adapter CLI: render từng trang bằng pypdfium2 đã ghim, giữ trang native, đọc TSV có vị trí, điền chữ vào bảng vector. Không dùng MuPDF worker/model |
| `e_ocr/cau_hinh_may.py`, schema cấu hình | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `e_ocr/kho_tam.py` | Viết mới ở OCR-0; OCR-2 thêm `cap_nhat` để đọc–sửa–ghi một khóa nguyên tử. Khóa `msvcrt` trên Windows, `fcntl` trên Linux; không có thư viện ngoài |
| `e_ocr/vendor/mask_ocr/common.py` | Chép `ma-nguon/vendor/mask_ocr/common.py` (Extracted, normalize), thêm wrapper XML chuẩn chặn DTD/entity và XML khác UTF-8 |
| `e_ocr/vendor/mask_ocr/extraction.py` | Chuyển phần `paragraph_text`, `word_blocks`, `extract_docx` từ tệp cùng tên; giữ kiểm OPC/ảnh nhúng, trần và cảnh báo. PDF dùng lõi lớp chữ hiện có; ảnh cần caller cấp Tesseract qua `image_reader` |
| `e_ocr/vendor/mask_ocr/layout.py` | Chép riêng `word_layout` từ tệp cùng tên, giữ ô rỗng/gridSpan/vMerge và thứ tự. Bỏ parser PDF MuPDF, phần review và nhánh append của runtime khác |
| `e_ocr/vendor/mask_ocr/__init__.py`, `LICENSE` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
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
| pypdfium2 | 5.13.0 | BSD-3-Clause, Apache-2.0 và giấy phép dependency đi kèm; OCR-2 dùng render PDF cho Tesseract, giữ thông báo giấy phép đi kèm distribution |
| charset-normalizer | 3.4.7 | MIT; dependency pdfminer.six |
| cryptography | 49.0.0 | Apache-2.0 OR BSD-3-Clause; dependency pdfminer.six |
| cffi | 2.0.0 | MIT; dependency cryptography |
| pycparser | 3.0 | BSD-3-Clause; dependency cffi |

ABBYY là phần mềm thương mại ngoài pip; quyền triển khai/giấy phép vẫn
theo các việc chờ Anh có sẵn. Không chép hoặc gọi ABBYY thật.
Tesseract CLI và `vie`/`eng` là thành phần ngoài pip, giấy phép Apache-2.0
theo thông báo của distribution Tesseract/tessdata; không đưa executable
hoặc traineddata vào gói. Chỉ chạy thật với ảnh DEMO trong một test khi
máy có executable và đủ ngôn ngữ; CI dùng mock, test thật skip có lý do nếu
thiếu. Công cụ kiểm ASCII ở `e_ocr/cong-cu/KIEM-TESSERACT.cmd` nằm ngoài gói.
Không thêm dependency; bỏ tham chiếu MuPDF/defusedxml của vendor cũ vì
hai thư viện chưa được ghim/cài ở môi trường này. XML chuẩn chặn DTD/entity
trước parse, chỉ nhận UTF-8. Chưa thêm MIME DOCX vào phiếu đã khóa.

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
9c240b24274ed4c3cabd6d5d454810a50de3c95d252e5d04af5e26b446c71162  CHANGELOG.md
bc1af1f36a1b4de11f47395c56ffe2030e1a6202f4ca21740f36c86166376893  contract/cau_hinh_may.schema.json
d73a80f276eef43536ee14810ef46a1df73d476a9b4f02cc4f3bd163f4d73902  contract/van_ban_tai_lieu.schema.json
8521635ce091f072c116ae64a5064b1d3baba70c78dfb6a4fcdffb212e9dfbd9  demo/cau_hinh.demo.json
9c62de68d53c5433d46378e73b8199c34904c2a6e308ec6616db4243229e5879  demo/DEMO-lop-chu-3-trang.pdf
d406d94e40aa25046ee87084931f69a1595ed6dd2c9386869ddc8e905dab05e3  demo/van_ban_tai_lieu.demo.json
603a5e0d4eade53b2d78fb0091c93f849f8dbdf7839e3929c94a9ac58750b53f  e_ocr/__init__.py
c2d21612f07dbdb34afbe33da4417a03e031a75fa0f82b8b8d1c318d9db8200a  e_ocr/abbyy.py
98bf4fb94199a65ce197864a9b169cf80be727ee65e76ec0249ddb9e6342ca35  e_ocr/bang.py
3dd03176ef7ec59364be1d8ba3e8b21a04b9feaca3d08e57e5b23aea37f31625  e_ocr/cau_hinh_may.py
f7eef209a9a9a21f6a0f2bad6d39faeb8ad86c7970f9a5a1f6c983896664c098  e_ocr/chay.py
476f286792732275abdad91d28ca9025e70c520109f14a427e979bb7a0a15a38  e_ocr/chon_nguon.py
5cd8ef1f2b827abbe983f383dfa1a6e59d3faf065a1652cd94621dc9d74c0fc2  e_ocr/kho_tam.py
3f62ce0659ab866444c96d11df4f8e2ad6f1b61ab79394c0635a60cd609203c4  e_ocr/lop_chu.py
6c7fec7a0497f3d0fa9ac1ae7037fb2b4c15dc12471b61f38a999dcc8da3c029  e_ocr/tesseract.py
144310e48918fbb769d59684d41355c2c00250b0bbd1aaf1428976f8b427a622  e_ocr/van_ban.py
b29f50e2662f897fd771a7cff297cabaf7e74ee4ed9a36bf71f18d7c1fe1edb5  e_ocr/vendor/mask_ocr/__init__.py
c2c2095c2a15deeb091ad96e23324ee5bd3e2c7fdf1972ed291a8c3cf3c67577  e_ocr/vendor/mask_ocr/common.py
1e1a0282230b16b06ef5fdad87664c72d1ff47ed7fd7aeaa44ec24815248b9e7  e_ocr/vendor/mask_ocr/extraction.py
fc31ae693905e1c544204d3be3e706bf4e7f9d1fd9e470dc31b1463491131d9c  e_ocr/vendor/mask_ocr/layout.py
09809e497efb6db53f33b883dafd008d495f22d1549657da5f2578abc2b9b728  e_ocr/vendor/mask_ocr/LICENSE
2a16f9820ccdb33105918a18b0c54a7e9326659e9631ca9e2682e58a4f7f1927  engine.json
69e9856d114928a742f19a63cc77d2e3f3ce761ad5e7f509f6364a8a1a11dca6  README.md
917a399a315c90024b0385f893f51d2bf4d9595b68888de07bd866beed0fb2b7  requirements.lock
```
