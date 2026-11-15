# Nguồn gói OCR-8 — 15/11/2026

Giấy phép mã nội bộ: **phần mềm nội bộ, dùng nội bộ tập đoàn** theo quyết
định cuối của engine OCR.
Chuyển lõi từ `ma-nguon/` ngay trong repo; mã nguồn cũ giữ nguyên. Không
chép thư mục dữ liệu/cấu hình ABBYY hoặc model. OCR-2 chỉ chuyển phần cần
dùng của `vendor/mask_ocr` đã có trong repo; không đọc nguồn ngoài workspace.

OCR-8 sửa theo kiểm độc lập của lead ngày 15/11/2026: tổng hợp lượt chưa rõ
chỉ số đếm/ngày ở phạm vi engine, giao dịch CAS cùng lượt; dọn ngày hết cửa sổ,
khai lưu 45 ngày; schema/ô chọn đúng bốn ngôn ngữ Tesseract. Không thêm dependency.
Công cụ OCR-7 `e_ocr/cong-cu/thu_abbyy_that.py` và `THU-ABBYY-THAT.cmd` nằm
ngoài gói, mã nội bộ do Anh tự chạy. `--cau-hinh <JSON>` đọc tệp JSON Anh chỉ
định khi có `--that`; mặc định chạy khô không đọc cấu hình/không gửi PDF.
Đây là ngoại lệ cho công cụ kiểm OCR-7 theo quyết định Anh 15/11/2026,
không phải nguồn cấu hình runtime engine; runtime chỉ đọc ngăn.

| Tệp | Nguồn / giấy phép |
|---|---|
| `CHANGELOG.md` | Giữ lịch sử OCR-0…OCR-6; bổ sung OCR-8, phiên bản 1.0.8. |
| `NGUON.md` | Bảng nguồn nội bộ, một hàng mỗi tệp; không tự băm để tránh tự tham chiếu. |
| `README.md` | Hướng dẫn SDK 2.0; OCR-5 bổ sung DEMO; OCR-8 cập nhật nối NGAN-0, cấu hình trong ngăn và so băm LF. |
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
| `e_ocr/chay.py` | Ba action SDK 2.0; OCR-8 nhận ngăn, cập nhật trạng thái; nối NGAN-0 bằng khai báo bảng RAM và chuyển ngoại lệ chung tại biên SDK. |
| `e_ocr/chon_nguon.py` | Chuyển sổ ngày sang Ngan trong OCR-8; đọc TrangNgan chung, giữ mốc CAS và chính sách chọn nguồn/phương án B. |
| `e_ocr/kho_tam.py` | Giữ nguyên mã OCR-0/OCR-4, chỉ tham chiếu/kiểm hồi quy; OCR-8 bỏ khỏi đường chạy, chờ lead chuyển LUU-TRU. |
| `e_ocr/lop_chu.py` | Chép và chuyển thể `ma-nguon/lop_chu.py`: giữ thuật toán đọc chữ ẩn, kiểm ma trận/xoay trang, tọa độ và trần; đổi kết quả sang schema chung, callback hủy SDK và bổ sung tự đếm trang/kiểm PNG/JPEG |
| `e_ocr/luot_abbyy.py` | Phương án B của OCR-4; OCR-8 dùng lay_hoac_tao, lô ngăn/CAS; nối NGAN-0 đọc TrangNgan/KetQuaLenh sau commit; đóng nợ khe đua OCR-4 số 1. |
| `e_ocr/tesseract.py` | Chuyển nhánh `doc_mask_ocr`/`image_text` của mã cũ thành adapter CLI: render từng trang bằng pypdfium2 đã ghim, giữ trang native, đọc TSV có vị trí, điền chữ vào bảng vector. Không dùng MuPDF worker/model |
| `e_ocr/van_ban.py` | Chuyển lõi OCR-1…4; OCR-8 đọc dict/None từ cấu hình chung, chuyển lỗi tại chay.py; giữ lớp chữ sẵn và phong bì SDK. |
| `e_ocr/vendor/mask_ocr/LICENSE` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
| `e_ocr/vendor/mask_ocr/__init__.py` | Vỏ import và giấy phép theo mã cũ/quyết định cuối; **phần mềm nội bộ, dùng nội bộ tập đoàn**. Không chép runtime dual, worker/model VietOCR hoặc model Tesseract |
| `e_ocr/vendor/mask_ocr/common.py` | Chép `ma-nguon/vendor/mask_ocr/common.py` (Extracted, normalize), thêm wrapper XML chuẩn chặn DTD/entity và XML khác UTF-8 |
| `e_ocr/vendor/mask_ocr/extraction.py` | Chuyển phần `paragraph_text`, `word_blocks`, `extract_docx` từ tệp cùng tên; giữ kiểm OPC/ảnh nhúng, trần và cảnh báo. PDF dùng lõi lớp chữ hiện có; ảnh cần caller cấp Tesseract qua `image_reader` |
| `e_ocr/vendor/mask_ocr/layout.py` | Chép riêng `word_layout` từ tệp cùng tên, giữ ô rỗng/gridSpan/vMerge và thứ tự. Bỏ parser PDF MuPDF, phần review và nhánh append của runtime khác |
| `e_ocr/xuat_word.py` | Chuyển thể quy tắc ô trống/ô gộp từ ma-nguon/bang.py và vendor/mask_ocr/layout.py; ZIP/XML thư viện chuẩn. OCR-5 đăng ký namespace w/xml chuẩn; không đổi thuật toán bảng. |
| `engine.json` | Phiếu 2.0, phiên bản 1.0.8; sáu DEMO PDF quét/PNG cho ba năng lực, nguon=chi_tesseract; giữ nguyên hợp đồng kỹ thuật. |
| `e_ocr/ngan.py` | Bản chung `_chung/mau-ma/ngan.py`, NGAN-0 (PR #34), lead đã chép; giữ nguyên, test so SHA-256 sau chuẩn hóa CRLF→LF. Chỉ thư viện chuẩn. |
| `e_ocr/cau_hinh.py` | Bản chung `_chung/mau-ma/cau_hinh.py`, NGAN-0 (PR #34), lead đã chép; giữ nguyên, test so SHA-256 sau chuẩn hóa CRLF→LF. Chỉ thư viện chuẩn. |
| `cau_hinh.schema.json` | Chuyển schema cấu hình máy cũ sang bản khai cấu hình trong ngăn; không thêm bí mật hoặc trường máy thật. |
| `KHAI-SDK-2.1.json` | Viết mới theo DE-NGHI-SDK-2.1 §2–5; bốn bảng ngăn, schema và màn; nối NGAN-0 sửa bảng cấu hình về khoa: []; không đổi manifest 2.0. |
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

Băm SHA-256 các tệp trong gói (không tự băm `NGUON.md` để tránh tự tham chiếu).
Quy ước LF: với tệp văn bản `.py`, `.md`, `.json`, `.js`, `.lock` và
`LICENSE`, thay byte CRLF (`0D 0A`) bằng LF (`0A`) trước khi băm; không
đổi BOM, encoding hoặc byte khác. Tệp nhị phân DEMO băm nguyên byte.
Quy ước này áp dụng cả hai bản mẫu NGAN-0, không cần sửa tệp mẫu khi
Git chuyển kiểu xuống dòng trên Windows.

```text
ad152ecfb225dc8b0c3bf6e6db1a8524a2e07e79649c9808257911253a15041e  cau_hinh.schema.json
4352e20961e95d85890084827b6c14b4a01d774335f89a2cba5a0771236f3a41  CHANGELOG.md
1b56ef1a5de686b4359857b68ad86bd909d250714fbc7f43c44e0e78887b0f04  contract/cau_hinh_may.schema.json
81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977  contract/van_ban_tai_lieu.schema.json
e6a148a20c0bda845df9beff217e86657f63c6c75bc3fa0a0e292d389f6551cd  demo/cau_hinh.demo.json
f69f1adf0b91d21d093fab6a8ac5b276daa2fcb44038f544fcdfa6bd92a117c7  demo/DEMO-1-trang.jpg
c36869332d46eea25ff7f2b265da081d2c8ab6f345dced1b38cce56ffeff316e  demo/DEMO-1-trang.png
a254b5361b26e2eef7b8cf26c1f15e87e4bee008421eec60c8cfb41d1fcec90d  demo/DEMO-ABBYY-gia-1-trang.pdf
79445753d110c93ca5b6e714bd63e990d253ff270478da3c713c71efdea87a59  demo/DEMO-ABBYY-gia-3-trang.pdf
5e2aa5781c934df99f3289deef68c6397968e625d75febb64374f1ea9918720a  demo/DEMO-bang-3-trang.pdf
f3726f407bdc2daa24ad646b85ff8a9701ba3bc1eb417f16effe4ffd8cc6049d  demo/DEMO-dap-an.docx
c5a46dc43d03e3306d2e532c9465cea330e429fa16da62909ef2b6659a5d3259  demo/DEMO-dap-an.json
9c62de68d53c5433d46378e73b8199c34904c2a6e308ec6616db4243229e5879  demo/DEMO-lop-chu-3-trang.pdf
2f57eb1431a6bf05ce245dc8aea01ebb8449213e69de83e178f1afc2e1cbeab3  demo/DEMO-quet-3-trang.pdf
3b4fe5051351530778e101cd857e85d2b0b0804a0bd5655f58708a8f3159c642  demo/DEMO-vung-da-cat.png
c36869332d46eea25ff7f2b265da081d2c8ab6f345dced1b38cce56ffeff316e  demo/DEMO-vung.png
76c99fe7d0a0c286f5e210c569233f4195cae188cb71ca56d0b04036b06d872e  demo/van_ban_tai_lieu.demo.json
e8872ef7b80c7774aa878b846e90ba90f71b86e434fa3016c1cb2886339a3a88  e_ocr/__init__.py
56b2968c588e22b70196ffad44cfec2a5e54f8b8647bec710af76d6e43e9bf35  e_ocr/abbyy.py
73d301dcaa535454871daaa3685819001c55cccabc881619971f8322244ad606  e_ocr/ban_giao.py
b11102034a8b77d18bf2a5043c05ac2d1f71a12614a7fb3a7f87f60056c1b5ad  e_ocr/bang.py
7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252  e_ocr/cau_hinh.py
298732214730d25b21e98b63e6af92f4159c4c2f1a9599de0a86719ec6023046  e_ocr/cau_hinh_may.py
d5ce6c204551508b44ff13de047714b4e7f63b95c004defdb3c3ba7124e8fbc7  e_ocr/chay.py
7b2d946daccb73421d718e249393d47933bcb24f8813c2f5acc0fe1f644afecb  e_ocr/chon_nguon.py
16dbcd9625c7cdf4d19df1cfbac7ff7a619bc2f008eecb99b1232f421c2e6a0d  e_ocr/kho_tam.py
46abf54b034eed40233efac67f0f50e2c8a7e46b446b0e75fca6d59e3c749115  e_ocr/lop_chu.py
65bef4bd7c406188d5a507f309ca36ed1e79d1eb97936259b31fdb631793fe81  e_ocr/luot_abbyy.py
2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0  e_ocr/ngan.py
28603912217c0ac6b6d6d5b5c3982ac0a3b436970f26d7a26afc0bc619b6f9b2  e_ocr/nhat_ky.py
6c7fec7a0497f3d0fa9ac1ae7037fb2b4c15dc12471b61f38a999dcc8da3c029  e_ocr/tesseract.py
c245888380ba316880a7ca330cdf757604257ddad35c9e1f597ccbe167f15aa6  e_ocr/van_ban.py
44e314dab34037d5f9060eb80be0a03e440c2a4fe0da68641eb9c4db31da210d  e_ocr/vendor/mask_ocr/__init__.py
95876167119b631b669366ea2feb494c0be9c9171f705d8d6f1365fe04dd498b  e_ocr/vendor/mask_ocr/common.py
0bfa7df02ebfdccbf28390a8ded135e580df4345a9d15ff8e0c4fc35d8e380e4  e_ocr/vendor/mask_ocr/extraction.py
aac81c7cf8d09c7eace619fb4543b69dd7211c1095e88a65940b0b7291ba953e  e_ocr/vendor/mask_ocr/layout.py
7f0205ee63a89a6634e1443b165e06968884b07bd5c3aa27129d3dad9a728c66  e_ocr/vendor/mask_ocr/LICENSE
9ade7360ae708ba872814a082cb77ca60e1577d6aec39be9559bbd5bad9335e9  e_ocr/xuat_word.py
09ceeef8b76bbc84295452f8036362d2d38a4e02d4f67378cbe22c79d7a6f357  engine.json
6f1fb097084a73ed858756a71ddea4c0b630fd0fbba39fe039b18a63604f6bd3  KHAI-SDK-2.1.json
85d035028dbaeb0ddcea10ecbab142963a8ba134d79e373a63f05339441a7fe3  README.md
a6e0b765087fa3707acab44063cb697610f231657a410b88ae1ff6e3bae2107c  requirements.lock
8c77c591da623286527f5acc0336ebee47682dc3bec56e0949441a19e789bbe8  ui/cau_hinh.js
```
