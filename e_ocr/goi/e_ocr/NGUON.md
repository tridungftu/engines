# Nguồn gói OCR-8 — 15/11/2026

Giấy phép mã nội bộ: **phần mềm nội bộ, dùng nội bộ tập đoàn** theo quyết
định cuối của engine OCR.
Chuyển lõi từ `ma-nguon/` ngay trong repo; mã nguồn cũ giữ nguyên. Không
chép thư mục dữ liệu/cấu hình ABBYY hoặc model. OCR-2 chỉ chuyển phần cần
dùng của `vendor/mask_ocr` đã có trong repo; không đọc nguồn ngoài workspace.

| Tệp | Nguồn / giấy phép |
|---|---|
| `CHANGELOG.md` | Giữ lịch sử OCR-0…OCR-6; bổ sung OCR-8, phiên bản 1.0.8. |
| `NGUON.md` | Bảng nguồn nội bộ, một hàng mỗi tệp; không tự băm để tránh tự tham chiếu. |
| `README.md` | Hướng dẫn SDK 2.0; OCR-5 bổ sung DEMO, nguồn giả ngoài gói, cách ly cấu hình/kho và giới hạn số đo nhật ký. |
| `contract/cau_hinh_may.schema.json` | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte từ `_chung/contract/van_ban_tai_lieu.schema.json`, định nghĩa theo `LOAI-DU-LIEU-RIENG.md` §2.1; test so SHA-256 |
| `demo/DEMO-bang-3-trang.pdf` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `demo/DEMO-lop-chu-3-trang.pdf` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `demo/cau_hinh.demo.json` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `demo/van_ban_tai_lieu.demo.json` | JSON DEMO từ OCR-0 minh họa schema/cấu hình. Hai PDF lớp chữ 3 trang (không bảng/có bảng ô trống và gộp ngang) sinh bằng mã thuần `tests/demo/tao_pdf.py`, chuyển thể bộ sinh `ma-nguon/tests/test_lop_chu.py`; nhãn ảnh DEMO và chữ ẩn ToUnicode, không font hệ thống/model. Test OCR-3 còn có cấu trúc DEMO gộp cả ngang/dọc, không là hồ sơ thật |
| `e_ocr/__init__.py` | Khung theo API v1; OCR-8 đồng bộ metadata 1.0.8. |
| `e_ocr/abbyy.py` | Chuyển vai trò backend của `ma-nguon/abbyy.py` ở OCR-1; OCR-4 thêm đọc lại đúng mã, callback chốt trước dọn, biên nhận từ chối và dọn khi hủy/lỗi; chỉ ChuaRo giữ kết quả. Không nhập cổng/lượt bền cũ Bỏ lib/cong_ocr.py, kiểm phiên/ACL và cầu nối phụ thuộc Core cũ. |
| `e_ocr/ban_giao.py` | Thay vai trò bàn giao của `ma-nguon/ban_giao.py` bằng `viec.tai_tep_ra` SDK 2.0. Không chép `CongOCR`, cơ chế ACK/lease/nhật ký nội dung hoặc import SDK cũ; không giữ nội dung trên đĩa |
| `e_ocr/bang.py` | Chuyển quy tắc ô trống/ô gộp, không suy bảng từ text và trần 100 hàng/40 cột từ `ma-nguon/bang.py`; đổi parser DOCX cũ sang đường kẻ/ký tự PDF sẵn có; xuất Word qua mô-đun riêng |
| `e_ocr/cau_hinh_may.py` | Giữ nguyên mã OCR-0, chỉ tham chiếu/kiểm hồi quy; OCR-8 bỏ khỏi đường chạy, chờ lead chuyển LUU-TRU. |
| `e_ocr/chay.py` | Ba action SDK 2.0; OCR-8 nhận ngăn, thêm luồng cập nhật trạng thái ABBYY vào ngăn, không đổi phong bì. |
| `e_ocr/chon_nguon.py` | Chuyển sổ ngày sang Ngan trong OCR-8, mốc CAS chung, giữ nguyên chính sách chọn nguồn/phương án B. |
| `e_ocr/kho_tam.py` | Giữ nguyên mã OCR-0/OCR-4, chỉ tham chiếu/kiểm hồi quy; OCR-8 bỏ khỏi đường chạy, chờ lead chuyển LUU-TRU. |
| `e_ocr/lop_chu.py` | Chép và chuyển thể `ma-nguon/lop_chu.py`: giữ thuật toán đọc chữ ẩn, kiểm ma trận/xoay trang, tọa độ và trần; đổi kết quả sang schema chung, callback hủy SDK và bổ sung tự đếm trang/kiểm PNG/JPEG |
| `e_ocr/luot_abbyy.py` | Phương án B của OCR-4; OCR-8 dùng lay_hoac_tao, lô ngăn/CAS và quyền xử lý theo mã lượt; đóng nợ khe đua OCR-4 số 1. |
| `e_ocr/tesseract.py` | Chuyển nhánh `doc_mask_ocr`/`image_text` của mã cũ thành adapter CLI: render từng trang bằng pypdfium2 đã ghim, giữ trang native, đọc TSV có vị trí, điền chữ vào bảng vector. Không dùng MuPDF worker/model |
| `e_ocr/van_ban.py` | Chuyển lõi OCR-1…4; OCR-8 đọc cấu hình từ ngăn theo schema, giữ lớp chữ sẵn và phong bì SDK. |
| `e_ocr/vendor/mask_ocr/LICENSE` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
| `e_ocr/vendor/mask_ocr/__init__.py` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
| `e_ocr/vendor/mask_ocr/common.py` | Chép `ma-nguon/vendor/mask_ocr/common.py` (Extracted, normalize), thêm wrapper XML chuẩn chặn DTD/entity và XML khác UTF-8 |
| `e_ocr/vendor/mask_ocr/extraction.py` | Chuyển phần `paragraph_text`, `word_blocks`, `extract_docx` từ tệp cùng tên; giữ kiểm OPC/ảnh nhúng, trần và cảnh báo. PDF dùng lõi lớp chữ hiện có; ảnh cần caller cấp Tesseract qua `image_reader` |
| `e_ocr/vendor/mask_ocr/layout.py` | Chép riêng `word_layout` từ tệp cùng tên, giữ ô rỗng/gridSpan/vMerge và thứ tự. Bỏ parser PDF MuPDF, phần review và nhánh append của runtime khác |
| `e_ocr/xuat_word.py` | Chuyển thể quy tắc ô trống/ô gộp từ ma-nguon/bang.py và vendor/mask_ocr/layout.py; ZIP/XML thư viện chuẩn. OCR-5 đăng ký namespace w/xml chuẩn; không đổi thuật toán bảng. |
| `engine.json` | Phiếu 2.0, phiên bản 1.0.8; sáu DEMO PDF quét/PNG cho ba năng lực, nguon=chi_tesseract; giữ nguyên hợp đồng kỹ thuật. |
| `e_ocr/ngan.py` | Bản tạm viết mới theo DE-NGHI-SDK-2.1 §3 và GIAO-CODEX-DOT-2 §2 bằng thư viện chuẩn; NGAN-0 chưa có trong worktree. Lead thay nguyên tệp khi gộp mẫu chung. |
| `e_ocr/cau_hinh.py` | Bản tạm viết mới theo API doc_cau_hinh(ngan, schema), chỉ thư viện chuẩn; kiểm schema tối thiểu, chờ NGAN-0 như ngan.py. |
| `cau_hinh.schema.json` | Chuyển schema cấu hình máy cũ sang bản khai cấu hình trong ngăn; không thêm bí mật hoặc trường máy thật. |
| `KHAI-SDK-2.1.json` | Viết mới theo DE-NGHI-SDK-2.1 §2–5; bốn bảng ngăn, schema và màn quản trị; không đưa trường mới vào manifest 2.0. |
| `ui/cau_hinh.js` | Viết mới OCR-8, JavaScript chuẩn và KttCore; form/DOM dùng textContent, không mạng ngoài hoặc thư viện frontend. |
| `requirements.lock` | Ghim phiên bản và SHA-256 wheel Windows x64, Linux x86_64; SDK nội bộ và thư viện PyPI. |
| `e_ocr/nhat_ky.py` | Viết mới OCR-5, thư viện chuẩn + SDK: ContextVar cách ly số đo, JSON stderr chỉ mã cố định; chuyển lỗi bất ngờ thành LoiNghiepVu an toàn, giữ lỗi transport/hủy/chưa rõ. |
| `demo/DEMO-1-trang.jpg` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-1-trang.png` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-ABBYY-gia-1-trang.pdf` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-ABBYY-gia-3-trang.pdf` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-dap-an.docx` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-dap-an.json` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-quet-3-trang.pdf` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-vung-da-cat.png` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |
| `demo/DEMO-vung.png` | Sinh từ tests/demo/tao_bo_demo.py chuyển từ ma-nguon/tests/demo/tao_bo_demo.py; dữ liệu giả có nhãn DEMO, Pillow đã ghim + PDF thuần Python, Word bằng bộ ghi OOXML gói; giấy phép nội bộ. Bản ABBYY-gia chỉ dùng cho mock, Word/JSON chỉ là đáp án. |

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

OCR-6 dùng hash SHA-256 từ metadata phát hành PyPI cho wheel Windows x64 CPython 3.13 và Linux x86_64 CPython 3.13; SDK lấy từ wheel trong repo. Pillow được dùng trực tiếp; PyMuPDF và defusedxml không được dùng. Script máy sạch yêu cầu nguồn wheel PyPI hoặc wheelhouse đã chuẩn bị; SDK cài offline.

Băm SHA-256 nguyên byte các tệp trong gói (không tự băm `NGUON.md` để tránh tự tham chiếu):

```text
aeddb6e290d09b7ca683e77123969e48500dda0e3dfed632461e3db4929a0028  cau_hinh.schema.json
e678b078fe3d474a269b53289204d9362e11a0b418733d28b503ffbeebbcf98b  CHANGELOG.md
bc1af1f36a1b4de11f47395c56ffe2030e1a6202f4ca21740f36c86166376893  contract/cau_hinh_may.schema.json
d73a80f276eef43536ee14810ef46a1df73d476a9b4f02cc4f3bd163f4d73902  contract/van_ban_tai_lieu.schema.json
8521635ce091f072c116ae64a5064b1d3baba70c78dfb6a4fcdffb212e9dfbd9  demo/cau_hinh.demo.json
f69f1adf0b91d21d093fab6a8ac5b276daa2fcb44038f544fcdfa6bd92a117c7  demo/DEMO-1-trang.jpg
c36869332d46eea25ff7f2b265da081d2c8ab6f345dced1b38cce56ffeff316e  demo/DEMO-1-trang.png
a254b5361b26e2eef7b8cf26c1f15e87e4bee008421eec60c8cfb41d1fcec90d  demo/DEMO-ABBYY-gia-1-trang.pdf
79445753d110c93ca5b6e714bd63e990d253ff270478da3c713c71efdea87a59  demo/DEMO-ABBYY-gia-3-trang.pdf
5e2aa5781c934df99f3289deef68c6397968e625d75febb64374f1ea9918720a  demo/DEMO-bang-3-trang.pdf
f3726f407bdc2daa24ad646b85ff8a9701ba3bc1eb417f16effe4ffd8cc6049d  demo/DEMO-dap-an.docx
22420732b1666a4d1dd2ecd872069bfd6b9cad6028c639e660ac0406145828fc  demo/DEMO-dap-an.json
9c62de68d53c5433d46378e73b8199c34904c2a6e308ec6616db4243229e5879  demo/DEMO-lop-chu-3-trang.pdf
2f57eb1431a6bf05ce245dc8aea01ebb8449213e69de83e178f1afc2e1cbeab3  demo/DEMO-quet-3-trang.pdf
3b4fe5051351530778e101cd857e85d2b0b0804a0bd5655f58708a8f3159c642  demo/DEMO-vung-da-cat.png
c36869332d46eea25ff7f2b265da081d2c8ab6f345dced1b38cce56ffeff316e  demo/DEMO-vung.png
d406d94e40aa25046ee87084931f69a1595ed6dd2c9386869ddc8e905dab05e3  demo/van_ban_tai_lieu.demo.json
f3a4c825acb9a9f8498fbdce6268f5a64d2cab80fd45399dc67c2cf303f5bb87  e_ocr/__init__.py
87e58327635de9e2549714c690168e573abf96e8e0f8d21dfe9aaf727fcd1037  e_ocr/abbyy.py
e488040c45310ef0776d3c529e3e0d5586651c39bcb042c82bb728657358dd10  e_ocr/ban_giao.py
98bf4fb94199a65ce197864a9b169cf80be727ee65e76ec0249ddb9e6342ca35  e_ocr/bang.py
6c3b393338e666ad94b22b9f80561a6c830684ee873ab44d0eb137a7e090e197  e_ocr/cau_hinh.py
3dd03176ef7ec59364be1d8ba3e8b21a04b9feaca3d08e57e5b23aea37f31625  e_ocr/cau_hinh_may.py
b8c0e2bc631bc142c3e061acdfb3cd11a4e7333258a6f155b6e679ce48b130a1  e_ocr/chay.py
0a590aa7a3358ddaabaeb9481d27c6354d17deea733084f916131c5c91bcb053  e_ocr/chon_nguon.py
69045a82652147f76d8e5273ba6bc1c199b20c86282d2483e4600cda1512931a  e_ocr/kho_tam.py
3f62ce0659ab866444c96d11df4f8e2ad6f1b61ab79394c0635a60cd609203c4  e_ocr/lop_chu.py
d2da3aede862ffee8b8821303d8420ec2c01fb402920f775eefa02996164e8ff  e_ocr/luot_abbyy.py
8ff2817062cbd9ba0d91262892bcb97f3bdff3e6ec9629a41254626c582882ce  e_ocr/ngan.py
27ef11e06b1e3ed1c54873a2849b9b32951ade738a20c7586ec983ba7b9200e0  e_ocr/nhat_ky.py
dfbc642c1d0a04115f5ed5894e4622b515a4c6e11a17ce16c9f60e93e40e1254  e_ocr/tesseract.py
2a30eb8989c7521ab6c2cff54ba5e237716a2f2795879e6ca489d1251a7d56b2  e_ocr/van_ban.py
b29f50e2662f897fd771a7cff297cabaf7e74ee4ed9a36bf71f18d7c1fe1edb5  e_ocr/vendor/mask_ocr/__init__.py
c2c2095c2a15deeb091ad96e23324ee5bd3e2c7fdf1972ed291a8c3cf3c67577  e_ocr/vendor/mask_ocr/common.py
1e1a0282230b16b06ef5fdad87664c72d1ff47ed7fd7aeaa44ec24815248b9e7  e_ocr/vendor/mask_ocr/extraction.py
fc31ae693905e1c544204d3be3e706bf4e7f9d1fd9e470dc31b1463491131d9c  e_ocr/vendor/mask_ocr/layout.py
09809e497efb6db53f33b883dafd008d495f22d1549657da5f2578abc2b9b728  e_ocr/vendor/mask_ocr/LICENSE
17f282a755ee25d934bcc9157dbc2c14e8b671b10d3dfed22c06553a47eb0494  e_ocr/xuat_word.py
7cdd66690ae82e2efcc2b1401b77e26014c0a988685920868fff93c2c70a4e7c  engine.json
cebb434669da4c4ce6a926a2e006d6f9c47325c2f0ddf02546972bc79dfbb909  KHAI-SDK-2.1.json
4a489b9507ee79e7070a234ab03acf9c453e44aa9080b94360de4462d279fbf5  README.md
ae7a61b60beb17381431df4ac0d8908afe21164381ab305983f76b9d7792792d  requirements.lock
10150cc470f1416a63d960ba3d227228e17b48a5fbb07874f867ad62ab30bd21  ui/cau_hinh.js
```
