# Nguồn gói OCR — SDK25, 22/11/2026

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
không phải nguồn cấu hình runtime engine; runtime đọc ngăn và bản chụp viec.cau_hinh của SDK 2.5.x.

## Lịch sử OCR-9 — 15/11/2026

OCR-9 chuyển runtime sang ngăn/cấu hình SDK 2.2.0, sửa năm tệp Python,
UI và migration cùng lát theo phạm vi đã giao. Ba tệp cổng tạm/khai dự
kiến được giữ nguyên ở `e_ocr/LUU-TRU/OCR-9/`, ngoài gói chạy; không còn
test so băm với `_chung/mau-ma`. Nguồn SDK: wheel trong repo, băm khớp
`SHA256SUMS.txt`: `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`.
Không thêm thư viện runtime ngoài các pin cũ và SDK 2.2.0. Vì SDK chưa
nhận `json`, ba map nhỏ lưu JSON text trong cột `van_ban`, trần 64 KiB.
Giữ chỗ không TTL ở mốc CAS, hàng ngày được Core ẩn sau 45 ngày.

Môi trường kiểm: venv mới, SDK cài `--no-index --no-deps`. Máy không có
wheelhouse phụ thuộc và tải wheel qua pip bị ngắt kết nối. Đã cài offline
các tệp distribution đúng tám pin runtime sẵn trên máy, kiểm từng SHA
trong `RECORD`, không dùng system-site-packages. Công cụ kiểm dùng
pytest 9.1.1, jsonschema 4.26.0 và dependency sẵn có cùng cách đối chiếu
RECORD. Chưa xác nhận lại hash archive wheel phụ thuộc bằng cài máy sạch;
lock vẫn giữ các hash phát hành đã có của OCR-6.

## Nguồn tệp và thư viện

| Tệp | Nguồn / giấy phép |
|---|---|
| `.gitattributes` | OCR-9: giữ LF cho tệp văn bản, giữ nguyên bytes PDF/ảnh/DOCX. |
| `sql/001_tao_ngan.sql` | OCR-9 theo mẫu e_demo_ngan SDK 2.2.0; chỉ CREATE TABLE trong eng_e_ocr, bảy cột hệ thống và unique khớp phiếu; Core thực thi. |
| `sql/kiem_ke.json` | OCR-9, tạo từ bytes thực của mọi tệp gói trừ chính kiểm kê; không băm chuẩn hóa thay bytes thực. |
| `CHANGELOG.md` | Giữ lịch sử OCR-0…OCR-6; bổ sung OCR-8 và SDK25, phiên bản 1.0.11. |
| `NGUON.md` | Bảng nguồn nội bộ, một hàng mỗi tệp; không tự băm để tránh tự tham chiếu. |
| `README.md` | Hướng dẫn SDK 2.5.0; OCR-5 bổ sung DEMO; OCR-8 cập nhật nối NGAN-0, cấu hình trong ngăn và so băm LF. |
| `contract/cau_hinh_may.schema.json` | Viết mới theo `GIAO-CODEX-THU-TU.md` §2 và `GIAO-CODEX-e_ocr.md` §2; thư viện chuẩn Python |
| `contract/van_ban_tai_lieu.schema.json` | Chép từ `_chung/contract/van_ban_tai_lieu.schema.json`, chỉ chuẩn hóa xuống dòng LF, định nghĩa theo `LOAI-DU-LIEU-RIENG.md` §2.1; test so SHA-256 chuẩn hóa LF |
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
| `engine.json` | Phiếu 2.0, phiên bản 1.0.11; sáu DEMO PDF quét/PNG cho ba năng lực, nguon=chi_tesseract; giữ nguyên hợp đồng kỹ thuật. |
| `cau_hinh.schema.json` | Chuyển schema cấu hình máy cũ sang bản khai cấu hình trong ngăn; không thêm bí mật hoặc trường máy thật. |
| `ui/cau_hinh.js` | Viết mới OCR-8, JavaScript chuẩn và KttCore; form/DOM dùng textContent, không mạng ngoài hoặc thư viện frontend. |
| `requirements.lock` | Ghim phiên bản và SHA-256 wheel Windows x64, Linux x86_64; thư viện PyPI; SDK do Core cấp, không ghim trong lock. |
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

Thư viện ngoài SDK được ghim trong `requirements.lock`; SDK do Core cấp. Các pin giữ đúng
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

OCR-6 dùng hash SHA-256 từ metadata phát hành PyPI cho wheel Windows x64 CPython 3.13 và Linux x86_64 CPython 3.13; SDK lấy từ wheel trong repo. Pillow được dùng trực tiếp; PyMuPDF và defusedxml không được dùng. SDK25: script máy sạch cài SDK 2.5.0 từ repo và thư viện vào thư mục riêng bằng wheel đã kèm gói; Linux CI dùng wheelhouse riêng đúng hash Linux trong lock. Bước cài luôn ngoại tuyến.


Băm SHA-256 các tệp trong gói: chuẩn hóa CRLF→LF cho văn bản; binary giữ
nguyên bytes. Bỏ `NGUON.md` và `sql/kiem_ke.json` để tránh vòng tự tham
chiếu. Kiểm kê SQL tính bytes thực, có cả NGUON.md, chỉ bỏ chính kiểm kê.

```text
6beb62195291ac96a8b00005b52b380a2c55b5e1d7f8156c5cd69d5711ca708a  .gitattributes
3d169a8fe9eb70b92846c6bbd491da696c6ce1d46fd94dc9b78942e95be06fba  cau_hinh.schema.json
116c46d648b57b2b96d32ea7b742f73b74bfa67541cb02fe93ee76a6b7c10443  CHANGELOG.md
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
692f7d59997554769204e26aba4e8162f095f15c10a8af727318a97eafd866c4  e_ocr/__init__.py
56b2968c588e22b70196ffad44cfec2a5e54f8b8647bec710af76d6e43e9bf35  e_ocr/abbyy.py
73d301dcaa535454871daaa3685819001c55cccabc881619971f8322244ad606  e_ocr/ban_giao.py
b11102034a8b77d18bf2a5043c05ac2d1f71a12614a7fb3a7f87f60056c1b5ad  e_ocr/bang.py
298732214730d25b21e98b63e6af92f4159c4c2f1a9599de0a86719ec6023046  e_ocr/cau_hinh_may.py
b69af156a2c8baa049d4a6d994bdca350fbc382d3796aed3681ff4bdef945b61  e_ocr/chay.py
10a80dcbdcb33fa9cc076ed796717087543113da981684b36dede2e123ccce02  e_ocr/chon_nguon.py
16dbcd9625c7cdf4d19df1cfbac7ff7a619bc2f008eecb99b1232f421c2e6a0d  e_ocr/kho_tam.py
46abf54b034eed40233efac67f0f50e2c8a7e46b446b0e75fca6d59e3c749115  e_ocr/lop_chu.py
ea3374d5930033d65e237d7f3a694c0fb18157558f199d547361b2641903b58e  e_ocr/luot_abbyy.py
28603912217c0ac6b6d6d5b5c3982ac0a3b436970f26d7a26afc0bc619b6f9b2  e_ocr/nhat_ky.py
d0d980205aeed5a6353e33fc8ae601dfcdc318d364543bcef54f575870407da3  e_ocr/quan_tri.py
6c7fec7a0497f3d0fa9ac1ae7037fb2b4c15dc12471b61f38a999dcc8da3c029  e_ocr/tesseract.py
e03196ef3a0c100dcf276c06f51668c6f955a7dd1f4bb3721ecef67cf9abf838  e_ocr/van_ban.py
44e314dab34037d5f9060eb80be0a03e440c2a4fe0da68641eb9c4db31da210d  e_ocr/vendor/mask_ocr/__init__.py
95876167119b631b669366ea2feb494c0be9c9171f705d8d6f1365fe04dd498b  e_ocr/vendor/mask_ocr/common.py
0bfa7df02ebfdccbf28390a8ded135e580df4345a9d15ff8e0c4fc35d8e380e4  e_ocr/vendor/mask_ocr/extraction.py
aac81c7cf8d09c7eace619fb4543b69dd7211c1095e88a65940b0b7291ba953e  e_ocr/vendor/mask_ocr/layout.py
7f0205ee63a89a6634e1443b165e06968884b07bd5c3aa27129d3dad9a728c66  e_ocr/vendor/mask_ocr/LICENSE
9ade7360ae708ba872814a082cb77ca60e1577d6aec39be9559bbd5bad9335e9  e_ocr/xuat_word.py
88a7ceb71e2cc2a6f1f2b2dd3c4b7946e4ff01a39d925a56185d213e3888a949  engine.json
186de0edff3ed0d80da41fc554da9f03ee4e084c3115ef2848f8fce6f9418a42  KHAI-SDK-2.1.json
db238421229908aeecf1d495f74884898c94cdb2303c489eab713cac3a084d8e  README.md
a460111dcf886a0996ea00309d922e3b55ce6d59178abdc9080439e7ef3b22cc  requirements.lock
ef41e4e79fc3e2c198040cbb2d7ad46be3b55c9aa46f91453040b267b824fe2b  sql/001_tao_ngan.sql
39603a9db08faa2554036b56e09aff8116ebde83b30d0fe22c88e29f8a7b7f64  ui/cau_hinh.js
19f705ada2530c1167abacb171925dd886168931e0a7b78f5bffcae5c6b5be75  wheels/cffi-2.0.0-cp313-cp313-win_amd64.whl
3946fa46a0cf3e4c8cb1cc52f56bb536310d34f25f01ca9b6c16afa767dab110  wheels/charset_normalizer-3.4.7-cp313-cp313-win_amd64.whl
e5dfc1e64de5677cec922ffa8da89c546d0415bf6efdf081842e5d44c84e1f0e  wheels/cryptography-49.0.0-cp311-abi3-win_amd64.whl
366585ba97e80dffa8f00cebe303d2f381884d8637af4ce422f1df3ef38111a9  wheels/pdfminer_six-20260107-py3-none-any.whl
7741ea81bf165b474b153e6789d10d18e06b6ddcf3ec84289c3ef2fed6802580  wheels/pdfplumber-0.11.10-py3-none-any.whl
1cca606cd25738df4ed873d5ad46bbdb3d83b5cbca291f6b4ff13a4df6b0bbe8  wheels/pillow-12.3.0-cp313-cp313-win_amd64.whl
b727414169a36b7d524c1c3e31839a521725078d7b2ff038656844266160a992  wheels/pycparser-3.0-py3-none-any.whl
47dcca2a8d507b5fd24f94c3c9d48fb379430f097bc20f01beff6c963ffbcedb  wheels/pypdfium2-5.13.0-py3-none-win_amd64.whl
```

## Wheel kèm gói (22/11/2026)

Thư mục `wheels/` chứa wheel tải từ PyPI (pypi.org) đúng phiên bản và SHA-256 ghi ở `requirements.lock`; đã đối chiếu với băm PyPI ghim từ trước nếu có. Nền CPython 3.13 win_amd64 hoặc thuần Python; `cryptography` chỉ phát hành dạng `cp311-abi3`, đã thử cài và chạy trên Python 3.13.14 sạch. Giấy phép của từng thư viện nằm trong `*.dist-info` của wheel. Không sửa wheel.

## SDK25 — 22/11/2026

SDK phát triển/test: `docs/goi-gui-engine/sdk-2.5.0/kho_tri_thuc_sdk-2.5.0-py3-none-any.whl`,
SHA-256 `b235b513deb557f65f5a90c81e1d81e9b51799093fdaefb3bb5c5e1e954d2b55`,
đối chiếu `SHA256SUMS.txt` cùng thư mục. SDK không nằm trong lock hoặc wheels
của engine; Core cấp SDK 2.5.x. Không đổi phiên bản tám thư viện đã có.
`chay.py`, `luot_abbyy.py`, `quan_tri.py` chỉ cập nhật chú thích phiên bản SDK;
nghiệp vụ giữ nguyên. `KHAI-SDK-2.1.json` vẫn là gợi ý lịch sử, chưa là hợp đồng SDK.

Bảng băm tái sinh bằng `.venv\Scripts\python -B -X utf8 e_ocr/tests/cap_nhat_bam.py`:
NGUON chuẩn hóa LF trước; `sql/kiem_ke.json` băm bytes thực sau cùng.
Các wheel không sửa byte; nguồn PyPI và giấy phép theo bảng thư viện phía trên.
