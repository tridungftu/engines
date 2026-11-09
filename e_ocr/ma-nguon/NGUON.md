# Nguồn và phụ thuộc OCR nội bộ — G3-GOI-17 / G3-GOI-20

phần mềm nội bộ, Anh xác nhận 06/11/2026, chỉ dùng nội bộ

Căn cứ: CD-096 A1, 06/11/2026 13:52, cuối
`docs/46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md` ở bản dự án chính.
Xác nhận này mở cổng nguồn ở `KE-HOACH-G3-GOI.md` §6.4;
không gán giấy phép mã nguồn mở cho nguồn nội bộ.

- Gói nguồn: **local-mask-ocr 2.1.0**, theo `D:\GPT\OCR\pyproject.toml`.
- Thư mục gốc chỉ đọc: `D:\GPT\OCR\mask_ocr`.
- Ngày lấy nguồn: **06/11/2026**. Không sửa hoặc ghi bytecode vào nguồn gốc.
- Đích: `vendor/mask_ocr/`, import qua namespace
  `kho_tri_thuc.engines.e_ocr.vendor.mask_ocr` trong ứng dụng;
  có thể nạp riêng package `e_ocr` để kiểm closure mà không có Core/SDK.

## Tập nguồn và SHA-256

Mỗi hàng tương ứng tệp cùng tên trong thư mục gốc nêu trên. SHA-256 tính
trực tiếp trên bytes, không chuẩn hóa xuống dòng. Nguồn có cả CRLF và LF:
`__init__.py` có 5 CRLF; `common.py` có 17 CRLF + 2 LF;
`extraction.py` có 218 CRLF + 141 LF; `layout.py`/`runtime.py` chỉ LF.
Phải giữ nguyên byte khi đưa vào git/checkout để không làm lệch mã băm.
Repo có `core.autocrlf=true`; lead cần khóa `-text` cho năm tệp nguồn
trước commit. `.gitattributes` ngoài whitelist lát 17 nên worker không sửa.

| Tệp trong gói | SHA-256 nguồn gốc | SHA-256 bản trong gói |
|---|---|---|
| `vendor/mask_ocr/__init__.py` | `d7c4302994002b7f2fc4b4986645e83115d7dfd4c0669004d5f0c107c0a0e2e6` | `d7c4302994002b7f2fc4b4986645e83115d7dfd4c0669004d5f0c107c0a0e2e6` |
| `vendor/mask_ocr/extraction.py` | `f573bb79a436fd2e968a4e8376b3128a973e81bed28d8398f1abdf6c092589a8` | `d66ddaef8e36b66d77a919993f6703c5d6fbb2dbfeccfd226e651117bffdb0b4` |
| `vendor/mask_ocr/layout.py` | `ae8f1310dfc4698c559bb15f56aae7d31389a675fa4924235b2b956b2da29a33` | `ae8f1310dfc4698c559bb15f56aae7d31389a675fa4924235b2b956b2da29a33` |
| `vendor/mask_ocr/common.py` | `e7daf60ac470ad47586e25ba5acdd0440246c52d22184bc7c39d5986f48791b7` | `e7daf60ac470ad47586e25ba5acdd0440246c52d22184bc7c39d5986f48791b7` |
| `vendor/mask_ocr/runtime.py` | `add0d540d63c5d01d47f00ae7faafc851d9b3dc13115fd905ca1a9eeb0916558` | `add0d540d63c5d01d47f00ae7faafc851d9b3dc13115fd905ca1a9eeb0916558` |

Bốn tệp giữ nguyên byte. `extraction.py` chỉ sửa câu cảnh báo chữ ẩn:
“Nội dung đọc được vẫn được đưa ra để Anh kiểm tra.” thành
“Nội dung đọc được vẫn được đưa ra để kiểm tra.” theo quy ước giao diện.
Không đổi thuật toán. Test hoàn nguyên đúng câu này trong RAM rồi so SHA
nguồn gốc, để phát hiện mọi thay đổi khác.

`vendor/__init__.py` là marker mới của gói; `vendor/mask_ocr/LICENSE` là
tệp mới ghi nguyên văn xác nhận nội bộ bên trên, vì nguồn không có LICENSE.
Hai tệp này không phải tệp sao chép từ công cụ cũ.

## Ranh giới sử dụng và phụ thuộc

- Dùng `extraction.extract_docx` và `layout.word_layout` cho DOCX do cổng
  OCR/ABBYY cung cấp. Giữ `common` và lazy import `runtime` trong whitelist.
  Không có đường dẫn máy phát triển hoặc thêm `sys.path` trong nguồn chép.
- Nguồn `local-mask-ocr 2.1.0` khai `PyMuPDF>=1.28.2,<2` và
  `defusedxml>=0.7.1,<1` trong pyproject. Đây là ràng buộc nguồn,
  không phải phiên bản đã cài. Cả hai **khai nhưng chưa cài/chưa dùng
  thật ở bản 1** trong môi trường đo ngày 07/11/2026; không ghim bừa
  thành dependency đã kiểm. Vendor vẫn import cả hai, nên nhánh DOCX
  và nhận dạng qua `image_text` chưa chạy được với dependency thật.
- G3-GOI-20 ghi phiên bản thư viện **đang cài** vào `requirements.lock`,
  gồm closure của pdfplumber và Pillow/numpy cho vùng; xem bảng dưới.
  Không cài/nâng thư viện hoặc thay phiên bản SDK; wheel SDK 1.4.1 vẫn
  là candidate theo `KE-HOACH-G3-GOI.md` §6.3, không ghim trong lock.
- Không chép model, cấu hình, dữ liệu, ứng dụng web, AI client hoặc các
  worker Tesseract/Paddle/VietOCR. Các nhánh OCR/PDF/ảnh legacy không được
  kích hoạt từ đường DOCX; không gọi `extract`, `ocr_ready`,
  `runtime.settings` hay `EnginePool` từ đường DOCX. OCR-VUNG/OCR-CHON
  dùng `image_text` khi có đủ dependency/model, không dùng worker legacy.
  `runtime.py` không đọc cấu hình hay khởi chạy worker khi import.
- Lát 17 kiểm closure parser trong gói. Adapter `van_ban.py`/`bang.py` hiện
  đã chuyển sang namespace vendor ở lát 18–19; chưa tuyên bố toàn bộ
  engine chạy độc lập với dependency thật hoặc ABBYY/Windows thật đã đạt.

## Ghim thư viện — G3-GOI-20, 07/11/2026

Đo bằng `importlib.metadata` trên **CPython 3.13.14, Windows x64**, đúng
môi trường chạy test của lát. Không dùng `pip freeze` toàn ứng dụng.
Giấy phép gói đã cài lấy từ trường `License-Expression`, `License` hoặc
classifier trong metadata; giữ thông báo giấy phép kèm các wheel khi dựng.
SHA-256 năm tệp vendor ở bảng trên được chép vào comment của lock và kiểm
đối chiếu tự động, không phải SHA-256 wheel tải về.

| Thư viện | Phiên bản / trạng thái | Giấy phép | Lý do dùng |
|---|---|---|---|
| pdfplumber | 0.11.10 — đã cài | MIT | Đọc lớp chữ PDF ABBYY, đếm trang; QD-TAM-20261106-12. |
| pdfminer.six | 20260107 — đã cài | MIT | Parser lớp chữ, phụ thuộc chính xác của pdfplumber. |
| pypdfium2 | 5.13.0 — đã cài | BSD-3-Clause, Apache-2.0, dependency licenses | pdfplumber bắt buộc khai; engine không gọi render qua thư viện này. Giữ giấy phép PDFium và các thành phần kèm wheel. |
| Pillow (`PIL`) | 12.3.0 — đã cài | MIT-CMU | Đọc PNG/JPEG, cắt vùng tứ giác; QD-TAM-20261106-13; cũng do pdfplumber yêu cầu. |
| numpy | 2.5.3 — đã cài | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | Tọa độ float32, kiểm hình học và kích thước vùng. |
| charset-normalizer | 3.4.7 — đã cài | MIT | Dependency của pdfminer.six để giải mã ký tự. |
| cryptography | 49.0.0 — đã cài | Apache-2.0 OR BSD-3-Clause | Dependency của pdfminer.six cho mã hóa PDF; giữ bản đang cài. |
| cffi | 2.0.0 — đã cài | MIT | Dependency của cryptography trên CPython. |
| pycparser | 3.0 — đã cài | BSD-3-Clause | Dependency của cffi trên CPython. |
| pymupdf | **Khai nhưng chưa cài/chưa dùng thật ở bản 1**; nguồn khai >=1.28.2,<2, không pin | AGPL / thương mại theo ghi nhận QD-TAM-20261106-12; chưa có metadata cài đặt để đối chiếu | Vendor import ngay; cần cho `image_text` và render PDF dự phòng. Chưa thể nhận dạng thật; lead chốt bản/giấy phép trước khi bổ sung. |
| defusedxml | **Khai nhưng chưa cài/chưa dùng thật ở bản 1**; nguồn khai >=0.7.1,<1, không pin | Chưa đối chiếu giấy phép trong môi trường vì chưa cài | Vendor/bộ đọc DOCX import XML an toàn; còn thiếu cho kiểm parser thật. Lead xác minh metadata/giấy phép khi bổ sung. |
| pytesseract | Chưa cài, **không dùng**, không pin | Không áp dụng cho closure hiện tại | Không có import trong engine; `image_text` dùng Tesseract tích hợp của MuPDF. |
| Tesseract (native) | CLI đã đo **5.5.3.20260724**; có **vie, eng, osd** | Apache-2.0 (Tesseract); chưa đối chiếu từng bộ ngôn ngữ/native dependency | Chỉ chạy `--version` / `--list-langs`, không OCR. CLI này không chứng minh bản Tesseract bên trong MuPDF hoặc model vendor sẵn sàng. |
| ABBYY | Cầu nối ngoài **tùy chọn**, chưa đo phiên bản tại lát này | Phần mềm thương mại, giấy phép triển khai riêng | Nguồn ưu tiên khi Core cấp backend; không là dependency pip và không ghim bộ cài/khóa. |

Chín pin chỉ bao phủ đường PDF lớp chữ/cắt ảnh và closure runtime của
chúng. Không đưa `packaging`, SDK, thư viện kiểm thử, extra docs/tests/XMP
của Pillow, VietOCR, Paddle hoặc dependency của toàn ứng dụng vào lock.
`typing-extensions` chỉ do cryptography yêu cầu khi Python <3.11, không
thuộc môi trường Python 3.13.14 đã đo. Chưa có hash wheel hay thử dựng venv
sạch trong lát này; hướng dẫn dựng/điều kiện thiếu ở `README.md`.

Kiểm bằng `tests.test_g3_goi_ocr_nguon`: SHA byte thực; tập tệp và quyền
nội bộ; closure cả lazy import; Python `-I -S` từ cwd ngoài repo, chặn
nguồn cũ/Core/SDK, đọc cấu hình/model, ghi tệp, mạng và tiến trình ngoài.
Ca mock chỉ mock hai dependency ngoài để kiểm import. Ca import/DOCX DEMO
với dependency thật báo **CHUA_KIEM/skip** nếu chưa được cài, không thay
parser/XML bằng mock rồi coi là đã kiểm thuật toán.

## OCR-NOI — PDF lớp chữ ABBYY

**QD-TAM-20261106-12 (lead chốt 06/11/2026):** dùng pdfplumber đã cài
để đọc PDF ABBYY có lớp chữ ẩn trên ảnh nền. pymupdf chưa có trong môi
trường và có giấy phép AGPL; không cài thêm để làm lát này. Có thể đảo
quyết định bằng cách chỉ thay lớp đọc trong `lop_chu.py` sau khi được chốt.

- `lop_chu.doc_lop_chu(bytes, huy=...)` import pdfplumber trong hàm;
  thiếu thư viện trả `LoiLopChu` tiếng Việt, import engine vẫn hoạt động.
  Chỉ đọc ký tự có sẵn trong RAM; không render PDF, OCR lại ảnh, gọi
  runtime/model, cấu hình hoặc dịch vụ ngoài.
- Trả `KetQuaLopChu` có cùng bốn trường `text`, `warnings`, `ocr_pages`,
  `pages` của `vendor.mask_ocr.common.Extracted`, `ocr_pages=0`.
  Không import trực tiếp lớp vendor vì `vendor.mask_ocr.__init__` nạp
  pymupdf/defusedxml ngay khi import; không thay vendor hoặc giả dependency.
  `pages` chứa `number`, `width`, `height`, `text`, `mode=native`,
  `source=ABBYY`, `blocks`, `units`, `issues`, `warnings`, `margins`.
  Khối `paragraph` trỏ `unit_ids` tới dòng; dòng là `units` với `parts`
  lưu từng từ. Khối/dòng/từ có `bbox` và `source=ABBYY`, ID chứa số trang.
  Vị trí dùng point, gốc trái trên MediaBox hiển thị sau phép xoay PDF.
  Đây là metadata nguồn đọc, không thay provenance/lease/ACK do Core cấp.
- Giới hạn 20 MiB, 60 trang, 500.000 ký tự. Bất kỳ trang nào thiếu lớp
  chữ, kể cả PDF chỉ có ảnh, đều trả `ma=OCR_PDF_KHONG_LOP_CHU` kèm số
  trang để lớp chọn nguồn chuyển mask_ocr. Không trả thành công một phần,
  không tự chạy OCR dự phòng hoặc sửa sổ hạn mức.
- `BackendABBYY.doc_lop_chu` kiểm phiên/ACL rồi đọc PDF kết quả Core cấp.
  Đường `BackendABBYY.ocr` trả DOCX hiện có giữ nguyên. Nối nguồn và cấp
  PDF từ ABBYY thật thuộc lát tiếp theo; chưa xác nhận Windows/ABBYY thật.
- `engines.e_ocr.tests.test_lop_chu`: PDF DEMO tối thiểu tự tạo trong RAM,
  ảnh nền + chữ ẩn ToUnicode, kiểm chữ Việt, tiền/ngày, khối/dòng/từ và
  vị trí (kể cả xoay 90°/180°/270°) bằng pdfplumber thật; kiểm lỗi thiếu
  dependency riêng bằng mock.

## Chuyển thể cắt vùng — OCR-VUNG, 06/11/2026

- Quyết định **QD-TAM-20261106-13**: môi trường có **Pillow 12.3.0** và
  **numpy 2.5.3**, không có OpenCV. Không cài thêm thư viện.
- Nguồn chuyển thể: `D:\GPT\OCR\mask_ocr\image_layout.py:73`, hàm
  `crop_quad`. Quyền dùng nội bộ theo xác nhận trên. Không chép toàn bộ
  `image_layout.py`; không sửa `vendor/mask_ocr/layout.py` hoặc SHA ghim.
- Đích `vung.py`: giữ điểm float32 theo thứ tự trên trái → trên phải →
  dưới phải → dưới trái. Rộng = max(int(khoảng cách 0–1), int(khoảng cách
  2–3), 2); cao = max(int(khoảng cách 0–3), int(khoảng cách 1–2), 2).
  Đổi thứ tự sang 0–3–2–1 cho `Image.transform(..., Image.Transform.QUAD)`
  với `Image.Resampling.BICUBIC`. QUAD của Pillow nội suy tứ giác, khác
  phép chiếu phối cảnh OpenCV; chỉ giữ logic thứ tự và kích thước đích,
  không tuyên bố ảnh cắt giống từng pixel hoặc đã đo độ chính xác OCR.
- Gốc dùng `BORDER_REPLICATE`. Bản chuyển thể từ chối trước khi cắt nếu
  điểm ngoài `[0, rộng−1] × [0, cao−1]`, không hữu hạn, trùng/thẳng hàng,
  vùng tự cắt/lõm hoặc diện tích bằng không. Không tự cắt biên/bù pixel.
  Ảnh và ảnh cắt tối đa 20 triệu pixel, bytes nguồn tối đa 20 MiB.
- Đọc PNG/JPEG từ bytes do Core cấp; vùng cắt mã hóa PNG trong RAM, gọi
  đúng `vendor.mask_ocr.extraction.image_text` (Tesseract vie+eng). Không
  gọi ABBYY, VietOCR/dual hay dựng OCR worker khác. Thiếu backend hoặc
  nhận dạng lỗi trả lỗi tiếng Việt, không trả văn bản giả/rỗng thay lỗi.
- `image_text` chỉ trả chữ, không trả confidence. `do_tin_cay=null`,
  `nghi_ngo=true`, lý do `chua_co_do_tin_cay`; chữ rỗng/thừa khoảng trắng
  có thêm `vung_rong`. Chưa thể phân loại điểm tin cậy cao/thấp; không tự
  đặt điểm/ngưỡng. `nguon_doc=mask_ocr_tesseract` chỉ nguồn đọc thực hiện.
- Function `ocr.trich_vung@1`: đầu vào `vung_anh.v1`, đầu ra
  `van_ban_vung.v1`; đăng ký tại `core/contract/ky_thuat.json`. Một bundle
  `contract/schemas.json` giữ cả closure của hai capability trong manifest,
  đúng nội dung Core, kèm ví dụ DEMO của contract vùng. Không đổi SDK.
- `chay.xu_ly_function` định tuyến function; `xu_ly_viec` nhận envelope
  Core gồm `capability`, `yeu_cau`, `du_lieu_ket_qua`, `revision_tep_truoc`.
  `yeu_cau` là payload `vung_anh.v1`; bytes lấy qua `SDKEngine.mo_doc`,
  kết quả JSON gửi qua `ghi_ket_qua`. Mất ACK chỉ gửi lại cùng kết quả,
  không OCR lại. Bootstrap mặc định vẫn `contracts=[]`; chưa công bố
  readiness OCR thật từ bộ kiểm mock hoặc backend DEMO.

Kiểm `engines.e_ocr.tests.test_vung`: Pillow/numpy thật cắt ảnh DEMO trong
RAM; mock OCR/IPC và dependency parser chưa có. Chưa chạy nhận dạng thật,
không đọc cấu hình/model/kho thật. Lát 20 ghim các gói hiện có; dựng môi
trường sạch và thử OCR thật thuộc lead/lát nghiệm thu sau. SDK 1.4.1 vẫn
chỉ candidate (§6.3).

## Chọn nguồn đọc — OCR-CHON, 07/11/2026

- `chon_nguon.ChonNguonOCR` ưu tiên ABBYY. Tự chuyển về tài liệu **gốc**
  qua `mask_ocr` khi không đủ hạn mức cho toàn bộ tài liệu, máy không kết
  nối, ABBYY lỗi/quá giờ hoặc `OCR_PDF_KHONG_LOP_CHU`. Không nhận kết quả
  một phần. Hủy việc không kích hoạt nguồn dự phòng; cả hai nguồn lỗi
  trả lỗi tiếng Việt, không trả văn bản giả/rỗng thay kết quả.
- Kết quả `KetQuaChonNguon` giữ bốn trường `text`, `warnings`, `ocr_pages`,
  `pages`, thêm `nguon_doc`, `ma_ly_do_chuyen`, `ly_do_chuyen`. Mã lý do
  nghiệp vụ nội bộ: `het_han_muc`, `khong_ket_noi`, `qua_thoi_gian`,
  `loi_nhan_dang`, `pdf_thieu_lop_chu`, `so_han_muc_can_kiem_tra`.
  Thông báo là câu tiếng Việt; không chuyển tiếp exception chứa đường
  dẫn/khóa. `.du_lieu()` trả dữ liệu để Core lưu trong phản hồi nguồn;
  không tạo contract mới hoặc tự cấp provenance/lease/ACK.
- Dùng **đúng đối tượng `CongOCR` và `tep_so_trang` Core cấp**, khóa
  `.lock`, cách ghi/gộp bền vững đang có. Đọc cả bản ghi cũ
  `[epoch, số trang]` và bản ghi mới `[epoch, số trang, mã giữ chỗ]`;
  bản ghi mới có UUID riêng cho **mỗi lần giữ trang**, kể cả khi thời
  điểm và số trang trùng nhau. Bản ghi cũ không có mã, vẫn tính hạn mức
  và không bao giờ bị hoàn bởi lượt mới.
  Không tạo sổ thứ hai, bảng hay migration. Đếm số trang PDF thực bằng
  pdfplumber; PNG/JPEG một trang, tối đa 20 MiB/60 trang như engine.
  Tạm giữ trước gửi bằng `ChonNguonOCR._giu_trang`, dùng lại
  `CongOCR._giu_trang`. Chỉ lưu con trỏ vào `CongOCR._giu_cho` **sau khi
  bản ghi đã lưu và đọc lại thấy đúng mã giữ chỗ**. Nếu `_ghi_so` lỗi/hủy
  sau khi đã lưu, thử đọc lại một lần trong cùng khóa: chỉ nhận con trỏ
  để hoàn khi xác nhận được chính bản ghi đó. Ghi lỗi trước lưu thì không
  có con trỏ và không ghi hoàn. Nếu cả xác nhận lẫn đọc phục hồi đều lỗi
  (kể cả `KeyboardInterrupt`), theo **QD-TAM-20261107-04**: không gọi
  ABBYY, không hoàn mù; giữ dư và đưa UUID vào danh sách chờ dùng chung
  theo từng sổ trong tiến trình. Lần đọc sổ thành công kế tiếp, trong
  cùng khóa, tự hoàn đúng bản ghi có UUID đó nếu thấy; chỉ bỏ chờ khi
  xác nhận không còn mã. Đọc thành công mà không thấy mã thì bỏ chờ,
  không ghi hoàn. Đọc/ghi đối chiếu lỗi thì tiếp tục giữ chờ; nhật ký
  không chứa đường dẫn hoặc lỗi gốc. `_hoan_trang` so đủ bản ghi có mã, không
  suy ra chủ sở hữu từ thời điểm/số trang. Sau KN4, giữ trang khi PDF ABBYY
  đã đọc đủ lớp chữ/đủ trang **hoặc chưa rõ ABBYY đã nhận**; chỉ hoàn khi
  chứng minh chưa gửi/chưa nhận. Hủy, lỗi hoặc timeout sau bắt đầu gửi
  không phải bằng chứng được hoàn. Không gọi ABBYY khi chưa xác nhận giữ
  trang. Khóa theo băm nội dung và pháp nhân chặn gửi lại trong tiến trình;
  chưa thay cơ chế chống trùng bền vững do Core quản lý.
- Giới hạn 5.000 trang trong **30 ngày trượt**, giữ nguyên quy ước sổ
  hiện có: bản ghi đúng mốc 30 ngày vẫn được tính, qua mốc thì hết hiệu
  lực. Dùng lại `_khoa_tep` của `lib/cong_ocr.py`: `threading.Lock` theo
  đường dẫn bảo vệ các luồng/đối tượng trong tiến trình; khóa byte đầu
  tệp `.lock` bằng `msvcrt.locking` trên Windows / `fcntl.lockf` trên POSIX
  bảo vệ **liên tiến trình** khi cùng tham gia cổng chung. Giữ tệp khóa,
  không thay bằng khóa riêng trong RAM. Rủi ro Review cũ không dùng khóa
  vẫn như `lib/cong_ocr.py` đã ghi.
  Khi sổ hỏng/không ghi được, chuyển nguồn với lý do cần kiểm tra sổ,
  không đặt hạn mức về 0. Nếu hoàn trang lỗi hoặc engine chết giữa lúc
  tạm giữ và hoàn tất, bản ghi có thể còn trong sổ, cần Core/lead đối
  chiếu; không khẳng định đã hoàn. Danh sách chờ chỉ ở trong RAM, mất
  khi tiến trình kết thúc; không thay sổ giao dịch của Core. Đường DOCX
  cũ cũng chờ đối chiếu khi cả hai lần đọc đều lỗi, dùng cùng mã giữ chỗ mới,
  giữ nguyên chính sách tính/hoàn trang theo trạng thái gửi.
- Seam ABBYY do Core/lát kết nối tiêm: `san_sang() -> bool` và
  `doc_pdf(raw, duoi, huy=...) -> bytes PDF`. Backend phải có thời hạn
  chờ hữu hạn và báo `TimeoutError`/`OCR_QUA_GIO` khi quá giờ; lớp chọn
  nguồn không tạo luồng gửi còn chạy ngầm sau timeout. Seam này **chỉ
  vận chuyển, không tự tính trang**. `BackendABBYY.ocr` hiện trả DOCX
  và tự qua cổng/sổ, nên không dùng làm seam PDF (tránh đếm hai lần).
  KN4 đã có `BackendKetNoiABBYY` nhận client KN3 do Core cấp; KN-CHOT
  chỉ truyền `ma_yeu_cau` cho client/backend mới, giữ giao diện backend
  cũ. Cầu và client **mặc định tắt**, chưa nối cầu ABBYY thật hoặc công
  bố readiness từ test giả.
- Dự phòng dùng `vendor.mask_ocr.extraction.image_text` hiện có, nhánh
  Tesseract. PDF render từng trang trong RAM bằng pymupdf với cùng
  `PDF_LOCK` của vendor, 150 dpi, giới hạn 20 triệu pixel/trang; không
  gọi `extract_pdf` vì gói chưa kèm `page_worker.py`. PNG/JPEG truyền
  thẳng `image_text`. Không tạo OCR pool/worker hoặc thêm thư viện.
  Chỉ có chữ từng trang; không tự đặt vị trí chữ hoặc confidence.
  Thiếu pymupdf/model/backend trả lỗi, không thay dependency bằng mock
  rồi coi là đã chạy nhận dạng thật. Phiên bản SDK không thay đổi.
- `chay.xu_ly_tai_lieu(..., chon_nguon=...)` nối lớp chọn nguồn với bytes
  do Core kiểm quyền; `chay.trang_thai_nguon(chon_nguon=...)` cung cấp dữ
  liệu cho màn quản lý engine ở lát sau. Không sửa luồng DEMO/vùng hoặc
  tự bật capability/readiness thật trong bootstrap.
- `trang_thai()` trả hạn mức đã dùng/còn lại, ngày bắt đầu cửa sổ trượt
  dạng **dd/mm/yyyy**, trạng thái máy **sẵn sàng / không kết nối / lỗi
  gần nhất** và thông báo lỗi đã giới hạn. Khi đang xử lý, số đã dùng
  gồm trang tạm giữ; khi không đọc được sổ, số đã dùng/còn lại là `null`.
  Trạng thái lỗi máy gần nhất giữ trong phiên engine; sổ hạn mức bền
  vững qua khởi động lại. Hàm không đọc cấu hình hay két bí mật.

Kiểm `engines.e_ocr.tests.test_chon_nguon`: backend ABBYY/Tesseract giả,
PDF/PNG DEMO và đọc lớp chữ thật, năm nhánh nguồn, sổ bền/cửa sổ trượt,
hai luồng cùng giữ trang với Barrier/Event chèn giữa đọc và ghi sổ
(đã kiểm mutation bỏ khóa: test đỏ), hủy và lỗi ghi/hoàn sổ, không thành công
giả khi cả hai nguồn lỗi. Chuỗi A/B/C cố định đồng hồ: A lưu thành công,
B ghi lỗi trước lưu, C lưu trước khi B hoàn; sổ phải còn đúng A/C và B
không ghi hoàn. Test này đỏ trên cơ chế cũ (còn 1 thay vì 2 trang), xanh
sau sửa. Ba mutation chạy trong RAM bị test bắt: đặt con trỏ trước ghi,
hoàn theo hai cột, khôi phục cơ chế cũ gây hoàn nhầm C. Kiểm thêm UUID
khác nhau khi trùng thời điểm/số trang, xác nhận sai mã, sổ hai/ba cột
và giữ nguyên cả bản ghi cũ trùng nhau.
Có ca PDF một trang: ghi sổ thật rồi lỗi đọc xác nhận, ABBYY không được
gọi, hoàn về đúng sổ ban đầu và hết con trỏ giữ chỗ; kiểm cả sổ rỗng và
sổ có trang trước đó. Kiểm thêm hủy ở bước xác nhận và thoát bất thường
sau giữ trang. Ca mock đường DOCX cũ kiểm lỗi xác nhận không gọi gửi,
không để con trỏ trong RAM và không tự thay đổi trang đã lưu.
Bộ `engines/e_ocr/tests` vòng 3: trước 70 ok / 0 fail /
0 error / 1 skip; sau 80 ok / 0 fail / 0 error / 1 skip (81 ca, thêm 10).
Vòng 4: tái hiện ghi thật thành công rồi lỗi cả hai lần đọc (sổ dư 1 trang,
ABBYY 0 lần); 7 ca mới trước sửa có 1 ok / 6 fail / 0 error / 0 skip.
Kiểm đối chiếu qua đối tượng khác cùng sổ ở lượt xem trạng thái kế tiếp,
lượt giữ tiếp theo hoàn trước kiểm hạn mức, hoàn đúng UUID giữa các hàng
trùng thời điểm/số trang, không hoàn hai lần; không thấy mã thì bỏ chờ;
lỗi ghi hoàn và lỗi đọc xác nhận hoàn giữ chờ; Review chèn lại UUID sau
xác nhận vẫn chờ đối chiếu; cả hai vị trí đọc bị `KeyboardInterrupt`
không làm mất mã chờ hay thay lỗi gốc. Có kiểm đường DOCX cũ.
Bộ `engines/e_ocr/tests`: trước 80 ok / 0 fail / 0 error / 1 skip;
sau 89 ok / 0 fail / 0 error / 1 skip (90 ca, thêm 9).
`tests.test_cong_ocr`: trước 17 ok / 3 fail / 0 error / 0 skip;
sau 20 ok / 0 fail / 0 error / 0 skip. Sửa assertion định dạng sổ mới
ba cột và vẫn giữ bản ghi hai cột cũ, gồm ca hai tiến trình ghi chung.
`tests.test_cong_ocr` đã kiểm khóa OS bằng hai tiến trình DEMO; danh sách
chờ đối chiếu chỉ có hiệu lực trong tiến trình tạo lượt giữ.
Chưa chạy ABBYY hoặc Tesseract thật; nghiệm thu
máy và nối cầu PDF do lead/lát kế tiếp thực hiện.

## OCR-MAY-1 — bộ DEMO và bài máy engine, 07/11/2026

Phạm vi theo `QUYET-DINH-CUOI-e_ocr.md` §5, **phần 1**: engine độc lập
với màn Core/server/PostgreSQL, cầu ABBYY **giả**, không mạng. Không thay
engine, SDK, requirements hoặc nguồn vendor; chưa nghiệm thu tổng thể
qua màn hoặc ABBYY thật.

### Bộ DEMO

`tests/demo/tao_bo_demo.py:tao_bo_demo(thu_muc)` chỉ sinh tệp mới trong
thư mục tạm được test cấp; không tự xóa và không lưu nhị phân vào git:

- PDF quét 3 trang: mỗi trang là ảnh JPEG đầy đủ, **không có lớp chữ**;
  có bảng 4 hàng × 3 cột, một ô trống và một ô gộp 3 cột.
- Một ảnh PNG và một JPEG, mỗi ảnh một trang; ảnh vùng cùng tứ giác
  pixel và ảnh cắt đáp án 1080 × 340. Thứ tự điểm: trên trái, trên phải,
  dưới phải, dưới trái; tứ giác nằm trong `DEMO-dap-an.json`.
- JSON UTF-8 có nhãn DEMO, đáp án từng dòng/trang, cấu trúc bảng và vùng;
  ba trường bắt buộc: **Công ty DEMO Ánh Dương**, **1.000.000 VND**,
  **30/10/2026**. Không lấy hồ sơ hoặc cấu hình từ ngoài bộ sinh.
- Word đáp án chỉ sinh khi đã có `python-docx`; môi trường hiện tại có
  nên đã sinh và kiểm 3 bảng, ô trống/ô gộp. Nếu thiếu thì dùng JSON và
  ghi rõ trong JSON/test skip, không cài thêm. Word này **là đáp án**,
  chưa chứng minh engine đã xuất Word từ PDF.
- PDF 61 trang, PDF lớn đúng 20 MiB + 1 byte và PDF hỏng.
- Hai PDF trả về của cầu giả (3 trang/1 trang): cùng bytes ảnh nền với
  bản quét, thêm lớp chữ ẩn Unicode có tọa độ. PDF ghi bằng stdlib,
  ảnh dùng Pillow đã ghim; không thêm thư viện sinh PDF. Cần font Arial
  hoặc DejaVu Sans sẵn có để vẽ đúng dấu; thiếu font thì báo lỗi rõ.

### Cách chạy

PowerShell, cwd là worktree OCR-MAY. Dùng đúng Python ngoài AppData:

```powershell
$env:PYTHONPATH = 'D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức\.claude\worktrees\lat-ocr-may\src;D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức\.claude\worktrees\lat-ocr-may\tests;D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức\var\app-runtime\app-runtime-20261019-092310-807\deps'
$env:PYTHONDONTWRITEBYTECODE = '1'
& 'D:\KTT-CD060-DEMO\python313\python.exe' -X utf8 -B -m unittest engines.e_ocr.tests.test_ocr_may -v
```

Chạy toàn bộ test engine trước/sau bằng cùng hai biến môi trường:

```powershell
& 'D:\KTT-CD060-DEMO\python313\python.exe' -X utf8 -B -m unittest discover -s engines\e_ocr\tests -v
```

Không chạy `tests.test_v3`, `tests.test_v7` hoặc test PostgreSQL. Bài máy
chặn mở socket và tiến trình ngoài, không tự tạo Hot Folder thật. Tệp
DEMO và nhật ký giữ ở thư mục tạm `ktt-ocr-may-demo-*` / `ktt-ocr-may-fixture-*`
để lead xem; không tự dọn. Không in đường dẫn vào nhật ký bài máy.

### Bằng chứng theo 9 ca

| Ca §5 | Đã kiểm ở mức engine | CHUA_KIEM / ranh giới |
|---|---|---|
| 1 | — | Skip: cần màn Quản lý engine Core, phiên bản và readiness ABBYY thật. |
| 2 | PDF quét qua cầu giả → nguồn ABBYY, đủ 3 trang; đọc lớp chữ thật bằng pdfplumber; chữ Việt/tiền/ngày khớp JSON; dòng/từ có vị trí trong trang; sổ dùng đúng 3 trang. | Skip riêng phần Word/bảng đầu ra: đường PDF lớp chữ chưa xuất Word/ô bảng. Word DEMO chỉ là đáp án. |
| 3 | PNG rồi JPEG qua cầu giả → mỗi ảnh 1 trang, nội dung khớp đáp án, sổ dùng đúng 2 trang. | Skip chống gửi trùng/số việc chờ/thứ tự hàng chờ: thuộc Core, engine không có hàng chờ. |
| 4 | Sổ giả đã dùng 5.000 trang → mask_ocr, có nguồn/lý do, không gửi ABBYY hoặc trừ thêm; cầu giả báo hết hạn mức cũng hoàn phần tạm giữ. | Nhận dạng/đo thật skip do thiếu pymupdf, defusedxml; không cài thêm. Test định tuyến dùng bộ đọc giả, không tính thành số đo chất lượng. |
| 5 | Tắt cầu giả → mask_ocr, lý do không kết nối, không gửi ABBYY, không trừ hạn mức. | Bộ đọc dự phòng giả; chưa đo OCR thật hoặc thời gian cầu thật tắt. |
| 6 | Định tuyến trích vùng; cắt ảnh bằng Pillow/numpy thật, so từng pixel với ảnh cắt đáp án; chữ/cờ nghi ngờ/thiếu confidence đúng. | Hàm nhận dạng vùng giả; chưa kiểm chất lượng Tesseract vùng. |
| 7 | Quá 20 MiB/quá 60 trang/hỏng → DataError với câu tiếng Việt; không thành công giả, không gọi hai nguồn, sổ giữ nguyên; hủy trước nhận dạng không trừ trang. | Skip hủy việc đang chờ Core. |
| 8 | — | Skip: cần cầu ABBYY thật và phép mở kết nối từ máy khác/Core; không gọi mạng trong lát này. |
| 9 | JSONL bài máy + stdout: ngày giờ dd/mm/yyyy, thời gian chạy, nguồn/không áp dụng, kết quả/skip/lý do từng ca; lỗi kết nối giả chứa đường dẫn/khóa được loại khỏi phản hồi/log. | Thời gian chờ là null vì engine không có hàng chờ. Nhật ký hàng chờ/màn Core chưa kiểm; JSONL là bằng chứng của test, không phải log sản phẩm. |

Ca 4 khi đủ dependency/model sẽ dùng đúng `doc_mask_ocr`/`image_text`
trong gói, Tesseract **vie+eng** thật; runtime chỉ nhận cấu hình DEMO trong
RAM, không đọc settings thật. Nếu thiếu model của engine thì skip có lý do,
không dùng readiness CLI bên ngoài thay thế. Nếu có model nhưng nhận dạng
lỗi thì test **error**, không đổi thành skip/thành công giả. Số đo ghi
**đúng/sai trên 9 trường nguyên văn** (3 trường × 3 trang), chi tiết từng
trường/trang; trạng thái `DA_DO_CHUA_CHOT_NGUONG`. Ngưỡng đạt chất lượng
chờ chốt sau lần đo đầu, không tự đặt ngưỡng hoặc đo bằng chữ giả.

Nhật ký ghi `DA_KIEM_ENGINE_GIA` cho phần giả và `CHUA_KIEM` cho phần
chưa làm; không gộp các ca skip thành đạt toàn bộ OCR. Số giây tổng nhóm
engine xuất ở dòng `OCR-MAY-1`; thời gian toàn module (gồm kiểm bộ sinh
DEMO) nằm ở dòng `Ran ... tests in ...s` của unittest.

Kết quả đo ngày **07/11/2026**, cùng Python/môi trường nêu trên:

| Bộ test | ok | fail | error | skip | Tổng | Giây |
|---|---:|---:|---:|---:|---:|---:|
| Engine trước thay đổi | 95 | 0 | 0 | 1 | 96 | 7,080 |
| OCR-MAY chạy riêng | 12 | 0 | 0 | 6 | 18 | 2,785 |
| Engine sau thay đổi | 107 | 0 | 0 | 7 | 114 | 8,884 |

Không thêm lỗi so với nền engine trước sửa; 6 skip mới đều là các phần
`CHUA_KIEM` trong bảng trên. Lần chạy sau có 15 bản ghi cho các phần của
9 ca, tổng nhóm engine OCR-MAY **1,418 giây**; lần chạy module riêng
**0,0464 phút**. Đã xem ảnh DEMO: đúng dấu, nhãn DEMO, bảng/ô trống/ô gộp
rõ. Lead còn chốt dependency/model/giấy phép trước đo OCR thật, ngưỡng
chất lượng sau đo, và lịch kiểm màn/hàng chờ/Word/cầu nối thật.

## Trạng thái sau KN4 / OCR-KN-CHOT — 07/11/2026

- KN4 (`b36f8f5c`, `e39646ab`) nối backend được tiêm, chặn gửi trùng
  cùng nội dung trong một pháp nhân, giữ mã tương quan và trang hạn mức
  khi chưa rõ ABBYY đã nhận. Khóa và dấu “chưa rõ” **chỉ ở trong bộ nhớ**;
  mất sau khởi động lại, chưa bảo vệ nhiều tiến trình. Dấu lượt chưa rõ
  không tự hết hạn trong tiến trình; không tự gửi lại hoặc hoàn trang.
- KN-CHOT (`2525b639`, `8c22d4d5`) giữ giao diện backend cũ, giới hạn
  đọc kết quả Hot Folder và tệp bàn giao. Bản sửa KN2 (`c756c674`,
  `64b8053c`) kiểm cả kích thước trước đọc và số byte đọc thực tế; bản
  cuối giữ trần tại adapter/client, không thêm tham số vào backend cũ.
- **Mặc định tắt, chưa nối ABBYY thật.** Lưu bền dấu chưa rõ, giữ lượt
  nguyên tử theo băm nội dung/pháp nhân và đối chiếu hạn mức phía Core
  vẫn là **điều kiện chặn trước lát 9**, theo
  [KS-OCR-CHUA-RO.md](../../docs/47-core/g3/KS-OCR-CHUA-RO.md).
  Chưa đổi SDK; wheel 1.4.1 vẫn chỉ là candidate (§6.3).

Các mục KN1–KN3 dưới đây ghi nhận từng mốc trước KN4; trạng thái hiện tại
và các giới hạn chưa khép được nêu ở trên.

## KN1 — tách vận chuyển PDF Hot Folder, 07/11/2026

- `lib/cong_ocr.py:HotFolderPDF` là adapter cục bộ có `san_sang()` và
  `doc_pdf(raw, duoi='pdf', *, huy=None) -> bytes`. Giữ tham số `duoi`
  để khớp cách `ChonNguonOCR` gọi backend cho PDF/PNG/JPEG. KN2/KN3 có
  thể thay adapter bằng backend HTTPS cùng giao diện; KN1 không mở mạng,
  bind socket hoặc tự nối adapter vào Core/bootstrap.
- **Mặc định tắt** (`bat=False`). Khởi tạo không dò filesystem, đọc cấu
  hình/két bí mật hoặc tạo thư mục. Khi Core cấp thư mục và bật tường
  minh, `san_sang()` chỉ kiểm bốn thư mục `in`, `out`, `tam`, `nhan` đã
  tồn tại; lỗi truy cập trả không sẵn sàng. Đây là trạng thái đường cục
  bộ, **chưa xác nhận ABBYY đang chạy**. Bên triển khai phải chuẩn bị
  thư mục và cấu hình ABBYY xuất PDF lớp chữ cùng mã việc vào `out`;
  không suy readiness thật từ kết quả mock.
- `_VanChuyenHotFolder` dùng lại cơ chế ghi `.part` rồi đổi tên vào
  `in`, chờ kết quả ổn định theo kích thước/thời điểm sửa, nhận bằng
  đổi tên sang `nhan` rồi kiểm lại. PDF chỉ nhận đúng `<mã việc>.pdf`,
  không lấy DOCX hoặc kết quả của lượt khác. Adapter dùng chung khóa
  `in.lock` với DOCX, không gửi lại tự động. Thời hạn/hủy được kiểm cả
  khi chờ khóa và chờ kết quả, theo nhịp `nghi`; nhịp khóa không lớn hơn
  `cho_toi_da`. Kiểm deadline theo nhịp nên có thể trễ tối đa một nhịp
  chờ khóa Python. Không tạo luồng gửi chạy ngầm sau timeout.
- Transport chỉ kiểm dấu đầu/cuối PDF đã ghi xong, không đếm trang hoặc
  đọc lớp chữ. `ChonNguonOCR` tiếp tục dùng `doc_lop_chu` để xác nhận
  PDF hợp lệ, đủ lớp chữ và đủ số trang trước khi chấp nhận kết quả.
  Không thêm dependency hoặc đổi SDK; wheel 1.4.1 vẫn là candidate
  theo `KE-HOACH-G3-GOI.md` §6.3.
- `CongOCR.ocr()` vẫn trả DOCX, dùng đệm DOCX và sổ cũ. Callback hoàn
  trang khi chưa gửi/rút được đầu vào chỉ được đường DOCX truyền vào
  phần vận chuyển dùng chung. Giữ nguyên toàn bộ giữ/hoàn trang theo
  UUID, bản ghi hai/ba cột và đối chiếu QD-TAM-20261107-04. Adapter PDF
  không giữ/hoàn trang, không đọc/ghi sổ hoặc dùng đệm DOCX. Dọn theo
  mã việc và hẹn dọn kết quả muộn 120 giây giữ như cơ chế hiện có;
  trong test mọi thao tác này đều là filesystem/Timer giả trong RAM.
- **Giới hạn tại mốc KN1, trước KN4:** lớp chọn nguồn khi đó hoàn trang
  sau thất bại, kể cả khi ABBYY có thể đã nhận và tiêu trang; DOCX cũ
  giữ trang nếu không rút được đầu vào. KN4 đã giữ lượt chưa rõ trong
  bộ nhớ; lưu bền/đối chiếu phía Core vẫn chặn trước lát 9 như trên.
  `san_sang()` cục bộ không thay kiểm máy thật.

Kiểm mới `engines.e_ocr.tests.test_hot_folder_pdf`: 27 ca thuần/mock,
filesystem/khóa/đồng hồ/Timer trong RAM, chặn socket và tiến trình ngoài.
Đã kiểm PDF lớp chữ DEMO đọc thật, PNG/JPEG, nối `ChonNguonOCR` thật với
sổ mock, sai mã/định dạng, tệp còn ghi dở, thay tệp giữa stat/rename,
hủy và timeout trước/sau nhận, tranh khóa, lỗi ABBYY/ghi tệp, dọn đúng
mã và regression vận chuyển DOCX. Không đọc nguồn `abbyy-hotfolder`
ngoài repo hoặc thư mục `in/out/jobs/state` thật; chưa chạy ABBYY thật.

| Bộ test (Python/môi trường theo handoff KN1) | ok | fail | error | skip | Tổng |
|---|---:|---:|---:|---:|---:|
| Engine trước KN1 | 107 | 0 | 0 | 7 | 114 |
| Engine sau KN1 | 134 | 0 | 0 | 7 | 141 |
| `tests.test_cong_ocr` trước KN1 | 20 | 0 | 0 | 0 | 20 |
| `tests.test_cong_ocr` sau KN1 | 20 | 0 | 0 | 0 | 20 |

Không thêm lỗi hoặc skip so với nền chạy trước sửa. Không chạy PostgreSQL,
server, `tests.test_v3` hoặc `tests.test_v7`. Không commit; lead giữ bước này.

## KN2 — dịch vụ cầu HTTPS trên máy ABBYY, 07/11/2026

`cau_noi_abbyy.py` chỉ dùng thư viện chuẩn và `lib.cong_ocr.HotFolderPDF`
đã có. Không đổi SDK, dependency, bootstrap Core, sổ trang hoặc transport
KN1. Không đọc cấu hình thường/két bí mật, tạo thư mục hay bind socket khi
import/khởi tạo. Mặc định **tắt** (`CauHinhCauNoi.bat=False`).

- `CauNoiABBYY(cau_hinh, ...).xu_ly(yeu_cau) -> PhanHoi` là khung xử lý
  đồng bộ, nhận `YeuCau(ket_noi, headers, luong, ...)` từ transport tin cậy;
  không tự mở kết nối. `chay(cau_hinh)` mới bind và phục vụ HTTPS khi
  `bat=True`. Vận hành phải cấp thư mục Hot Folder đã chuẩn bị và
  `SSLContext(PROTOCOL_TLS_SERVER)` đã nạp chứng thư, tối thiểu TLS 1.2;
  mã không có đường HTTP thuần hoặc tự tạo chứng thư.
- Khóa bytes được bootstrap tin cậy cấp **trong RAM**, dài 32–256 byte
  ASCII in được, không có khoảng trắng. Không có CLI, args, env hoặc
  tệp cấu hình cấp khóa. Không nạp/ghi két trong lát này. Không đưa khóa
  hoặc đường dẫn Hot Folder vào `repr` của cấu hình/yêu cầu.
- Giao thức dành cho KN3: `POST /ocr/pdf`, body PDF bytes;
  `Authorization: Bearer <khóa do vận hành cấp>`, `Content-Type:
  application/pdf`, một `Content-Length` dương và `X-Request-ID` dạng
  UUID do Core cấp. Không nhận đường dẫn/endpoint qua payload. Thành
  công trả nguyên PDF bằng `application/pdf`; lỗi JSON UTF-8 có
  `thong_bao` tiếng Việt. Header phản hồi `X-Correlation-ID` là mã mới
  ngẫu nhiên do dịch vụ sinh, không dùng mã từ client làm mã log.
- Mỗi yêu cầu kiểm **cả** khóa bằng `hmac.compare_digest` và IP từ
  `ket_noi.getpeername()`. Không dùng IP trong body, header hoặc
  `client_address`; bỏ qua `X-Forwarded-For`. Chỉ nhận các IP chính xác
  do vận hành cấp, không nhận CIDR/hostname. Chuẩn hóa IPv4-mapped IPv6.
  Server còn chặn IP socket ngoài danh sách trước handshake TLS.
  Firewall/ACL/chứng thư và phép nối thật do lead/vận hành thực hiện.
- Mặc định: PDF vào tối đa **20 MiB**, PDF ra **40 MiB**; tổng đọc body,
  chờ và OCR **300 giây**; chờ lượt xử lý tối đa **10 giây**; handshake,
  toàn bộ header, một lần đọc body và ghi phản hồi **10 giây** mỗi pha.
  Đọc theo khối tối đa 64 KiB; header có deadline tuyệt đối để tránh
  kéo dài bằng cách gửi nhỏ giọt. Một lượt ABBYY đang chạy + tối đa
  **4** lượt đang đọc/chờ; tối đa **8** luồng HTTP và backlog **8**.
  Đầy thì từ chối ngay; không tạo hàng chờ hoặc worker OCR vô hạn.
  Giới hạn cấu hình phải dương/hữu hạn, riêng số chờ cho phép bằng 0.
- Mã được giữ atomically trước đọc body và gửi ABBYY; không bỏ mã sau
  thành công, lỗi, hủy bất thường hoặc timeout. Trùng mã trả **409**,
  không đọc lại body/gọi ABBYY, kể cả nội dung mới khác. Tối đa **10.000**
  mã trong RAM; đầy trả **503**, không tự loại mã cũ. Từ chối vì đầy
  hàng hoặc sai xác thực/đầu vào trước nhận không giữ mã. Timeout trả
  **504**; không tự gửi lại. Deadline truyền qua `huy` của HotFolderPDF,
  không tạo luồng gửi chạy tiếp sau khi trả timeout. Deadline hợp tác
  có độ trễ theo nhịp khóa/đọc filesystem của adapter KN1, không phải
  cơ chế cưỡng bức ngắt I/O của hệ điều hành.
- Log chỉ có bốn trường: `ma_tuong_quan`, `ket_qua` (HTTP status),
  `thoi_gian_giay`, `so_trang`. `so_trang=null` vì transport không đếm
  trang; không lấy số trang do client tự khai. Không log header, nội
  dung, tên/đường dẫn, IP, mã yêu cầu client hoặc exception gốc.
  Tắt access/error log của `http.server`, traceback của `socketserver`;
  lỗi parser trả câu cố định, không phản chiếu URL/header độc hại.
  Phản hồi đóng kết nối và `Cache-Control: no-store`.
- PDF ABBYY phải được cấu hình có lớp chữ. Dịch vụ kiểm dấu đầu/cuối và
  dung lượng kết quả; `ChonNguonOCR`/`doc_lop_chu` ở Core tiếp tục xác
  nhận PDF, lớp chữ và đủ số trang. Dịch vụ không tính/giữ/hoàn trang.

Kiểm mới `engines.e_ocr.tests.test_cau_noi_abbyy`: **35 ca** thuần/mock;
chặn filesystem, socket và tiến trình ngoài; body/PDF DEMO trong RAM.
Kiểm khóa thiếu/sai/Unicode/header trùng, IP sai/socket lỗi/XFF giả,
quá cỡ/đầu vào hỏng, gửi trùng khi đang chạy/sau thành công/sau lỗi,
hàng chờ đồng thời và giới hạn mã, deadline header/body/hàng/adapter,
PDF đầu ra sai/quá cỡ, log đúng allowlist, import/cờ tắt/TLS và lỗi
transport. Có chạy HTTP parser thật với socket/luồng giả, không bind
socket hoặc khởi động server thật. Các test khởi động server thay toàn
bộ server bằng mock.

Chạy đúng Python và `PYTHONPATH` do handoff cấp, lệnh
`-X utf8 -B -m unittest discover -s engines\e_ocr\tests -v`:

| Bộ test | ok | fail | error | skip | Tổng | Giây |
|---|---:|---:|---:|---:|---:|---:|
| Engine trước KN2 | 134 | 0 | 0 | 7 | 141 | 9,314 |
| Engine sau KN2 | 169 | 0 | 0 | 7 | 176 | 7,315 |

Không thêm lỗi/skip so với nền engine trước sửa. Không chạy PostgreSQL,
server thật, `tests.test_v3` hoặc `tests.test_v7`. Không commit; lead commit.

**Lead cần chốt trước nối thật:** điểm bootstrap cấp khóa/chứng thư/IP
Core, giới hạn vận hành và đối chiếu bền sau timeout. KN3 client và
KN4 giữ lượt chưa rõ trong bộ nhớ đã có. Mã chống trùng **chỉ sống
trong phiên dịch vụ**, mất sau khởi động lại; Core phải giữ trạng thái
bền và đối chiếu các lượt chưa rõ trước khi gửi lại/khởi động lại.
Không công bố readiness hay nghiệm thu ABBYY/TLS thật từ kết quả mock.

## KN3 — client HTTPS phía Core, 07/11/2026

`ket_noi_abbyy.py:KetNoiABBYY` dùng thư viện chuẩn, mặc định **tắt**.
`KetNoiABBYY().san_sang()` trả `False`; import/khởi tạo/kiểm sẵn sàng
không mở mạng, đọc cấu hình/két bí mật/CA, hoặc dò máy ABBYY. Khi bật,
`san_sang()` chỉ xác nhận cấu hình cục bộ; chưa chứng minh cầu đang chạy.

Bootstrap tin cậy cấp `CauHinhKetNoi(bat=True, may_chu=..., khoa=...,
tls=...)` trong RAM. `may_chu` là hostname/IP riêng, không phải URL;
cổng mặc định 9443, route cố định `/ocr/pdf`. `khoa` bytes 32–256 byte
ASCII in được, không khoảng trắng, chỉ đi trong `Authorization: Bearer`.
Không đọc khóa từ tệp/args/env, không đưa vào URL, repr hoặc log.
Client không có logger, tắt HTTP debug kể cả khi debug mặc định của lớp
chuẩn đã bật; không dùng proxy từ env, không redirect hoặc tự gửi lại.

`tls` phải là `SSLContext` do vận hành/bootstrap nạp CA/chứng thư tin cậy,
`CERT_REQUIRED`, `check_hostname=True`, tối thiểu TLS 1.2. Không có đường
HTTP, bỏ kiểm chứng thư, tự tạo chứng thư hoặc tự chọn CA. Context được
kiểm lại trước kết nối và trước khi gửi khóa. CA/hostname/chứng thư hết
hạn không hợp lệ phải bị tầng TLS từ chối trước khi gửi header hoặc PDF.
Không thay SDK/requirements; wheel SDK 1.4.1 vẫn chỉ là candidate.

`doc_pdf(raw, duoi='pdf', *, huy=None, ma_yeu_cau=None) -> bytes` khớp
cách `ChonNguonOCR` gọi. Chỉ nhận PDF bytes có dấu đầu/cuối hợp lệ;
đuôi ảnh bị từ chối bằng lỗi sạch để bên gọi dùng nguồn dự phòng. Không
đếm trang, đọc lớp chữ hoặc giữ/hoàn hạn mức. PNG/JPEG qua cầu PDF cần
lát nối chuyển đổi/định tuyến, không giả gửi ảnh với MIME PDF.

- Gửi một POST, `Content-Type: application/pdf`, `Content-Length` và
  `X-Request-ID` UUID. Core có thể cấp UUID ổn định; nếu không, mỗi lần
  gọi sinh UUID mới. Mã được trả trong lỗi để đối chiếu; Core/KN4 cần
  giữ liên hệ bền giữa UUID và việc trước khi gửi. Client không có sổ
  chống trùng riêng; bridge KN2 chặn UUID đã nhận trong phiên dịch vụ.
- Mặc định PDF vào tối đa **20 MiB**, ra **40 MiB**; timeout kết nối/TLS
  **10 giây**, từng I/O gửi/đọc **310 giây**, tổng lượt **330 giây**.
  Thời gian đọc đủ chờ deadline 300 giây của KN2. Các giới hạn phải
  dương/hữu hạn. Gửi/đọc theo khối tối đa 64 KiB; không giải nén phản
  hồi. Có/không `Content-Length`, kể cả chunked, chỉ đọc tối đa giới
  hạn + 1 byte; header khai quá cỡ bị chặn trước đọc body.
- Hủy được trước kết nối, trước gửi và giữa các khối. Một luồng giám
  sát mỗi lượt, nhịp 50 ms, chỉ `shutdown`/đóng socket để ngắt chờ HTTP
  khi hủy hoặc hết deadline tổng; không gửi hoặc chạy OCR ngầm. Luồng
  được dừng/join khi trả kết quả. Vẫn giữ socket TLS để ngắt đọc khi
  `http.client` đã tách socket khỏi connection do `Connection: close`.
  Phân giải DNS do hệ điều hành quản lý: không thể cưỡng bức ngắt DNS
  bằng timeout socket; hủy/deadline được nhận ngay khi connect trả quyền.
  Nhu cầu deadline cứng cả DNS cần lead chốt ở phần vận hành/KN4.
- Thành công phải HTTP 200, MIME PDF, body đúng dấu PDF; từ chối header
  trùng, độ dài sai, encoding nén hoặc framing không hợp lệ. Lớp
  `doc_lop_chu` hiện có vẫn kiểm PDF thật/lớp chữ/đủ trang sau vận chuyển.
  Body lỗi HTTP không được đọc hoặc phản chiếu. Ngoại lệ gốc/cleanup
  được xóa trước khi ném lỗi mới, không đính kèm header/body/khóa gốc.

`LoiKetNoiABBYY` kế thừa `DataError`, có `ma`/`code`, `ma_yeu_cau`,
`nguyen_nhan`, `chua_ro_da_nhan`. Mã nội bộ dành cho Core/hỗ trợ, không
đưa nguyên mã lên màn nghiệp vụ:

| Trường hợp | Mã | Chưa rõ đã nhận |
|---|---|---|
| Không kết nối, chưa gửi | `ABBYY_KHONG_KET_NOI` | False |
| Timeout trước gửi | `OCR_QUA_GIO` | False |
| TLS/chứng thư bị từ chối trước gửi | `ABBYY_CHUNG_THU` | False |
| HTTP 401 | `ABBYY_KHOA_SAI` | False |
| HTTP 403 của KN2 | `ABBYY_KHOA_HOAC_IP` | False |
| HTTP 409 | `ABBYY_YEU_CAU_TRUNG` | True |
| HTTP 503 | `ABBYY_BAN` | False |
| Mất phản hồi/reset/timeout sau bắt đầu gửi, body thiếu so độ dài; HTTP 504 | `ABBYY_CHUA_RO_DA_NHAN` | True |
| Sai MIME/framing/PDF hoặc quá cỡ sau gửi | `ABBYY_PHAN_HOI_SAI` / `ABBYY_PHAN_HOI_QUA_CO` | True |
| HTTP 502 | `ABBYY_LOI_XU_LY` | True |
| Hủy | `OCR_HUY` | True nếu đã bắt đầu gửi |

Đánh dấu đã bắt đầu gửi **trước** `endheaders`: gửi một phần rồi lỗi
không chứng minh được chưa nhận. Khi mã chính là `ABBYY_CHUA_RO_DA_NHAN`,
`nguyen_nhan` vẫn phân biệt timeout (`OCR_QUA_GIO`) và mất kết nối
(`ABBYY_KHONG_KET_NOI`). Không hoàn trang hoặc gửi lại từ client.

**Hai điểm phải xử lý trước nối thật, ngoài whitelist KN3:**

1. KN2 trả cùng HTTP 403/cùng body cho sai khóa và sai IP; client không
   thể tách chắc chắn hai nguyên nhân. Hiện giữ mã tổng hợp trung thực,
   có nhận riêng HTTP 401 nếu giao thức sau này bổ sung. Lead chốt giữ
   thông báo chung hay mở lát sửa giao thức KN2 để phân biệt.
2. Tại mốc KN3, `ChonNguonOCR` còn hoàn trang sau mọi thất bại và chưa
   đọc `chua_ro_da_nhan`. KN4 đã giữ lượt chưa rõ, gồm cả hủy/quá cỡ/
   sai dạng sau gửi, nhưng dấu chỉ ở trong bộ nhớ. Lưu bền và đối chiếu
   phía Core vẫn chưa có; chưa được bật cầu thật dựa riêng kết quả mock.

Kiểm mới `engines.e_ocr.tests.test_ket_noi_abbyy`: **31 ca**, hoàn toàn
HTTP/socket giả, PDF DEMO trong RAM; chặn socket/DNS/filesystem/tiến trình
thật. Có chạy `HTTPSConnection.connect` và HTTP parser chuẩn trên socket
giả; TLS mock từ chối CA/hostname/chứng thư hết hạn; kiểm POST/khóa chỉ
header/UUID, KN2 thật xử lý trong RAM, trùng mã, timeout/reset/gửi dở,
phản hồi sai/quá cỡ/chunked, hủy trước/trong gửi/chờ header/body, deadline,
đóng tài nguyên, HTTP debug tắt và khóa không lộ qua log/ngoại lệ.

Chạy đúng Python/PYTHONPATH của handoff, cwd worktree KN3:
`-X utf8 -B -m unittest discover -s engines\e_ocr\tests`.

| Bộ test | ok | fail | error | skip | Tổng | Giây |
|---|---:|---:|---:|---:|---:|---:|
| Engine trước KN3 | 169 | 0 | 0 | 7 | 176 | 8,192 |
| Engine sau KN3 | 200 | 0 | 0 | 7 | 207 | 6,069 |

Không thêm lỗi/skip so với nền chạy trước sửa. Không chạy PostgreSQL,
server, mạng/ABBYY/TLS thật, `tests.test_v3` hoặc `tests.test_v7`.
Không commit; lead commit. Bootstrap cấp khóa/CA và nghiệm thu máy thật
do lead/vận hành thực hiện sau các điểm chốt trên.
