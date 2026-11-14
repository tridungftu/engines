# Nguồn gói OCR-4 — 15/11/2026

Giấy phép mã nội bộ: **phần mềm nội bộ, dùng nội bộ tập đoàn** theo quyết
định cuối của engine OCR.
Chuyển lõi từ `ma-nguon/` ngay trong repo; mã nguồn cũ giữ nguyên. Không
chép thư mục dữ liệu/cấu hình ABBYY hoặc model. OCR-2 chỉ chuyển phần cần
dùng của `vendor/mask_ocr` đã có trong repo; không đọc nguồn ngoài workspace.

| Tệp | Nguồn / giấy phép |
|---|---|
| `CHANGELOG.md` | Lịch sử OCR-0…OCR-3 giữ từ origin/main; bổ sung thay đổi OCR-4, phiên bản 1.0.4. |
| `NGUON.md` | Bảng nguồn nội bộ, chuẩn hóa một hàng mỗi tệp sau gộp OCR-4; không tự băm để tránh tự tham chiếu. |
| `README.md` | Hướng dẫn gói OCR-0…OCR-3 giữ từ origin/main; bổ sung nhật ký lượt, đối chiếu và biên nhận OCR-4. |
| `contract/cau_hinh_may.schema.json` | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte từ `_chung/contract/van_ban_tai_lieu.schema.json`, định nghĩa theo `LOAI-DU-LIEU-RIENG.md` §2.1; test so SHA-256 |
| `demo/DEMO-bang-3-trang.pdf` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `demo/DEMO-lop-chu-3-trang.pdf` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `demo/cau_hinh.demo.json` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `demo/van_ban_tai_lieu.demo.json` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `e_ocr/__init__.py` | Khung OCR-0…OCR-3 theo API v1; OCR-4 chỉ tăng metadata 1.0.4, giữ nguyên API và ba action |
| `e_ocr/abbyy.py` | Chuyển vai trò backend của `ma-nguon/abbyy.py` ở OCR-1; OCR-4 thêm đọc lại đúng mã, callback chốt trước dọn, biên nhận từ chối và dọn khi hủy/lỗi; chỉ ChuaRo giữ kết quả. Không nhập cổng/lượt bền cũ Bỏ lib/cong_ocr.py, kiểm phiên/ACL và cầu nối phụ thuộc Core cũ. |
| `e_ocr/ban_giao.py` | Thay vai trò bàn giao của `ma-nguon/ban_giao.py` bằng `viec.tai_tep_ra` SDK 2.0. Không chép `CongOCR`, cơ chế ACK/lease/nhật ký nội dung hoặc import SDK cũ; không giữ nội dung trên đĩa |
| `e_ocr/bang.py` | Chuyển quy tắc ô trống/ô gộp, không suy bảng từ text và trần 100 hàng/40 cột từ `ma-nguon/bang.py`; đổi parser DOCX cũ sang đường kẻ/ký tự PDF sẵn có; xuất Word qua mô-đun riêng |
| `e_ocr/cau_hinh_may.py` | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `e_ocr/chay.py` | Giữ nguyên cổng chính thức OCR-2/OCR-3 trên origin/main: ba action dùng chung trich_van_ban và bộ chọn nguồn, chỉ import SDK ngoài Core. |
| `e_ocr/chon_nguon.py` | Chuyển thứ tự ưu tiên, bảo vệ đã nhận và bảng lý do từ `ma-nguon/chon_nguon.py`; OCR-4 nối nhật ký bền, khóa lượt, ưu tiên đối chiếu trước chọn nguồn; không gọi SDK riêng |
| `e_ocr/kho_tam.py` | Viết mới ở OCR-0; OCR-4 thêm `cap_nhat_nhieu` để nhật ký và hạn mức cùng commit, khóa riêng theo lượt; giữ API một khóa. Khóa `msvcrt` trên Windows, `fcntl` trên Linux; không có thư viện ngoài |
| `e_ocr/lop_chu.py` | Chép và chuyển thể `ma-nguon/lop_chu.py`: giữ thuật toán đọc chữ ẩn, kiểm ma trận/xoay trang, tọa độ và trần; đổi kết quả sang schema chung, callback hủy SDK và bổ sung tự đếm trang/kiểm PNG/JPEG |
| `e_ocr/luot_abbyy.py` | Viết mới theo phương án B của OCR-4: UUID5 tất định, nhật ký metadata, chống trùng và đối chiếu hạn mức nguyên tử; chỉ thư viện chuẩn + SDK |
| `e_ocr/tesseract.py` | Chuyển nhánh `doc_mask_ocr`/`image_text` của mã cũ thành adapter CLI: render từng trang bằng pypdfium2 đã ghim, giữ trang native, đọc TSV có vị trí, điền chữ vào bảng vector. Không dùng MuPDF worker/model |
| `e_ocr/van_ban.py` | Chuyển từ `ma-nguon/van_ban.py` ở OCR-1; OCR-2 nối `doc_theo_nguon`; OCR-4 để bộ chọn đối chiếu lượt dở trước khi báo thiếu cấu hình; giữ lớp chữ sẵn, SDK và phong bì |
| `e_ocr/vendor/mask_ocr/LICENSE` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
| `e_ocr/vendor/mask_ocr/__init__.py` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
| `e_ocr/vendor/mask_ocr/common.py` | Chép `ma-nguon/vendor/mask_ocr/common.py` (Extracted, normalize), thêm wrapper XML chuẩn chặn DTD/entity và XML khác UTF-8 |
| `e_ocr/vendor/mask_ocr/extraction.py` | Chuyển phần `paragraph_text`, `word_blocks`, `extract_docx` từ tệp cùng tên; giữ kiểm OPC/ảnh nhúng, trần và cảnh báo. PDF dùng lõi lớp chữ hiện có; ảnh cần caller cấp Tesseract qua `image_reader` |
| `e_ocr/vendor/mask_ocr/layout.py` | Chép riêng `word_layout` từ tệp cùng tên, giữ ô rỗng/gridSpan/vMerge và thứ tự. Bỏ parser PDF MuPDF, phần review và nhánh append của runtime khác |
| `e_ocr/xuat_word.py` | Chuyển quy tắc lưới ô gốc/ô phủ, trần 100 hàng/40 cột từ `ma-nguon/bang.py`; đảo chiều quy tắc `gridSpan`/`vMerge` của `ma-nguon/vendor/mask_ocr/layout.py:word_layout` để ghi Word từ schema chung; kiểm thiếu/chồng ô, giữ nguyên tiền/ngày. ZIP/XML dựng mới bằng thư viện chuẩn Python, không thêm dependency |
| `engine.json` | Khung OCR-0…OCR-3 theo API v1; OCR-4 chỉ tăng metadata 1.0.4, giữ nguyên API và ba action |
| `requirements.lock` | Giữ nguyên pin dependency chính thức của OCR-2/OCR-3 trên origin/main; không thêm dependency ở OCR-4. |

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

OCR-3 giữ nguyên thư viện đã ghim. Bản `vendor/mask_ocr` trong repo chỉ
chứa parser/khôi phục layout, **không có bộ ghi Word** để chép nguyên;
chỉ chuyển thể quy tắc biểu diễn ô gộp, không chép cả vendor hoặc các
import PyMuPDF/defusedxml chưa được ghim. Giấy phép phần nguồn chuyển thể:
**phần mềm nội bộ, dùng nội bộ tập đoàn**, theo quyết định cuối của engine.

Môi trường `.venv --system-site-packages` dùng thư viện sẵn có và pytest;
chưa là cài máy sạch. Lock hiện chỉ ghim phiên bản, không dùng
`--require-hashes`; hash wheel Windows/Linux và bài máy sạch thuộc OCR-6.
SHA-256 wheel SDK phát hành, đã so với
`docs/goi-gui-engine/sdk-2.0.0/SHA256SUMS.txt`:

```text
a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892  kho_tri_thuc_sdk-2.0.0-py3-none-any.whl
```

Băm SHA-256 nguyên byte các tệp trong gói sau gộp (không tự băm `NGUON.md` để tránh tự tham chiếu):

```text
f0e6f391a8d84b52d7262f4f6c488841b4e4c8082c701412594348e191d4e7f8  CHANGELOG.md
bc1af1f36a1b4de11f47395c56ffe2030e1a6202f4ca21740f36c86166376893  contract/cau_hinh_may.schema.json
d73a80f276eef43536ee14810ef46a1df73d476a9b4f02cc4f3bd163f4d73902  contract/van_ban_tai_lieu.schema.json
8521635ce091f072c116ae64a5064b1d3baba70c78dfb6a4fcdffb212e9dfbd9  demo/cau_hinh.demo.json
5e2aa5781c934df99f3289deef68c6397968e625d75febb64374f1ea9918720a  demo/DEMO-bang-3-trang.pdf
9c62de68d53c5433d46378e73b8199c34904c2a6e308ec6616db4243229e5879  demo/DEMO-lop-chu-3-trang.pdf
d406d94e40aa25046ee87084931f69a1595ed6dd2c9386869ddc8e905dab05e3  demo/van_ban_tai_lieu.demo.json
b3443a0d8d8e27b37ea3da3c5812514e7256a70f22e323d588c289af0668ee1b  e_ocr/__init__.py
1730d0be8b1be29e99f524a7e51feac95167e0f950854cc93bfa783b3df9cbf8  e_ocr/abbyy.py
e488040c45310ef0776d3c529e3e0d5586651c39bcb042c82bb728657358dd10  e_ocr/ban_giao.py
98bf4fb94199a65ce197864a9b169cf80be727ee65e76ec0249ddb9e6342ca35  e_ocr/bang.py
3dd03176ef7ec59364be1d8ba3e8b21a04b9feaca3d08e57e5b23aea37f31625  e_ocr/cau_hinh_may.py
cb0ecfd43016b2c2db4eb00649228f4b9b9ad405bb441f8dbe2407487317d003  e_ocr/chay.py
230e7dc7861c2c73b571dc7eb43e0e4a0e0d5b832d1b9c6e7f555829a39edcb8  e_ocr/chon_nguon.py
16dbcd9625c7cdf4d19df1cfbac7ff7a619bc2f008eecb99b1232f421c2e6a0d  e_ocr/kho_tam.py
3f62ce0659ab866444c96d11df4f8e2ad6f1b61ab79394c0635a60cd609203c4  e_ocr/lop_chu.py
6e6d5c064d21c68aac0ddc5842681167e23aad827f53410ca6ad11a20d3dae80  e_ocr/luot_abbyy.py
dfbc642c1d0a04115f5ed5894e4622b515a4c6e11a17ce16c9f60e93e40e1254  e_ocr/tesseract.py
5c2c53567f65d674b763671f61b342476c18316f6df6bb48e34450363301cd19  e_ocr/van_ban.py
b29f50e2662f897fd771a7cff297cabaf7e74ee4ed9a36bf71f18d7c1fe1edb5  e_ocr/vendor/mask_ocr/__init__.py
c2c2095c2a15deeb091ad96e23324ee5bd3e2c7fdf1972ed291a8c3cf3c67577  e_ocr/vendor/mask_ocr/common.py
1e1a0282230b16b06ef5fdad87664c72d1ff47ed7fd7aeaa44ec24815248b9e7  e_ocr/vendor/mask_ocr/extraction.py
fc31ae693905e1c544204d3be3e706bf4e7f9d1fd9e470dc31b1463491131d9c  e_ocr/vendor/mask_ocr/layout.py
09809e497efb6db53f33b883dafd008d495f22d1549657da5f2578abc2b9b728  e_ocr/vendor/mask_ocr/LICENSE
29789376d2089fb4f9695aba51d9f19a1d61e949003c11e2a75e5f860012fa94  e_ocr/xuat_word.py
df091a8c9e136731829bdf1699619913629959efda1c479fff32232475fd3b65  engine.json
db71556e3cda66aa85c0dfae56038ffabc542a22ea9e1652465a1a254dcdca2f  README.md
917a399a315c90024b0385f893f51d2bf4d9595b68888de07bd866beed0fb2b7  requirements.lock
```
