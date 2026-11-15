# e_ocr — Nhận dạng văn bản: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- `QUYET-DINH-CUOI-e_ocr.md` (06/11 21:00) và `PHIEU-ENGINE-e_ocr.md`.
- Chỉ đạo của Anh về "chưa rõ" (phương án B). Anh cho phép mở kết nối tạm đến ABBYY.
- TL 57 §9: `ocr.trich_vung@1` phục vụ Đối chiếu bản ký.
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

**Hiện trạng** cập nhật OCR-5 (phiếu 14/11, thực hiện 15/11/2026), gói SDK
2.0 phiên bản 1.0.5; phần mã cũ còn ghi riêng khi chưa chuyển. Ký hiệu:
- ✅ có, đã kiểm thuần/mock
- 🟡 một phần
- ❌ chưa có

## 0. Kết luận
- **OCR là engine riêng.** Nguồn ưu tiên là **ABBYY FineReader Hot Folder**. Dự phòng là **mask_ocr chỉ nhánh Tesseract** (vie+eng).
- Năng lực v1:
  - đọc văn bản: có vị trí trang, có bản Word, giữ ô trống và ô gộp của bảng;
  - trích vùng `ocr.trich_vung@1`.
- **Đã kiểm bằng Core giả (CoreGia):** ba năng lực đọc tài liệu/đọc văn bản/xuất Word, ABBYY giả, Tesseract, hạn mức và lượt "chưa rõ" bền. Trích vùng/cầu nối HTTPS có khóa còn ở mã cũ, chưa đưa vào gói SDK 2.0.
- **Chưa:**
  - nối ABBYY thật (lát 9);
  - ca 1, 6, 8 của bài máy test trên gói SDK 2.0;
  - chạy trên Core thật.
- Phần đối chiếu và lượt OCR phía Core (`ocr_doi_chieu.py`, route, màn, SQL 126/130/131, hàm SDK `ocr_*_luot`) **đang là mã riêng trong Core**, phải đổi thành "lượt bền" chung.

## 1. Yêu cầu

| Mã | Yêu cầu | Căn cứ |
|---|---|---|
| OCR-1 | Engine riêng. Nghiệm thu hai tầng: máy test engine trước, nghiệm thu tổng thể sau | QĐ §1 |
| OCR-2 | Tận dụng `D:\GPT\OCR\abbyy-hotfolder` (ưu tiên) và `D:\GPT\OCR\mask_ocr`. Từ mask_ocr chỉ lấy: nhánh Tesseract, đọc PDF có chữ sẵn, DOCX, giữ bảng, xuất Word, hàng chờ, chống trùng. Giấy phép: phần mềm nội bộ, dùng nội bộ tập đoàn | QĐ §1, lát 1 |
| OCR-3 | **Không chép** các thư mục `in\`, `out\`, `jobs\`, `state\` của abbyy-hotfolder (có khóa API). Không chép VietOCR, model của VietOCR, review dual. Không xóa mã cũ | QĐ lát 1 |
| OCR-4 | Đọc văn bản → `van_ban_tai_lieu.v1`: theo trang, có vị trí; trả kèm bản Word | QĐ lát 2 |
| OCR-5 | Giữ ô trống, ô gộp và vị trí bảng trong kết quả Word | QĐ lát 3 |
| OCR-6 | Ghim phiên bản thư viện và nguồn; hướng dẫn cài môi trường sạch; ghim theo khung SDK đã gộp | QĐ lát 6 |
| OCR-7 | **OCR-NOI:** dùng lớp chữ PDF ("text under image") của ABBYY, đổi sang cấu trúc kết quả chung; không OCR lại ảnh nền | QĐ |
| OCR-8 | **OCR-CHON:** ABBYY trước. Tự chuyển sang mask_ocr khi (a) hết hạn mức **5.000 trang/30 ngày**, (b) máy ABBYY tắt, (c) ABBYY lỗi hoặc quá giờ. Kết quả ghi rõ nguồn đọc. Màn Quản lý engine hiện hạn mức đã dùng/còn lại và trạng thái máy ABBYY | QĐ |
| OCR-9 | **OCR-KETNOI:** mở cầu nối để máy chủ Core gọi tới máy ABBYY. Có khóa; chỉ nhận từ địa chỉ máy chủ Core; log không lộ khóa và đường dẫn | QĐ |
| OCR-10 | **OCR-VUNG `ocr.trich_vung@1`:** dùng lại `crop_quad`; trả chữ kèm cờ nghi ngờ | QĐ; TL 57 |
| OCR-11 | **OCR-MAY:** bộ DEMO giả và bài máy test độc lập gồm 9 ca (mục 3) | QĐ §5 |
| OCR-12 | Thử ABBYY thật trên **máy hiện tại** (tạm) với PDF DEMO (lát 9). Anh đã cho phép mở kết nối tạm | QĐ lát 9; Anh 07/11 |
| OCR-13 | **"Chưa rõ" bền (phương án B):** khi ABBYY đã nhận việc nhưng chưa trả, giữ lượt và hạn mức; không báo thành công giả; lần sau chốt bằng cùng mã tương quan; chỉ hoàn trang khi có căn cứ | Anh 07/11 (B); CR-3…CR-7 |
| OCR-14 | Chống gửi trùng cùng nội dung trong một pháp nhân (theo băm) | QĐ §5 ca 3; KN4 |
| OCR-15 | Lỗi dễ hiểu với tệp quá cỡ, quá trang, tệp hỏng. Không trừ hạn mức sai. Hủy được việc đang chờ | QĐ §5 ca 7 |
| OCR-16 | Nhật ký: thời gian chờ và chạy, nguồn đọc của từng ca | QĐ §5 ca 9 |

**Không có trong v1:** VietOCR, chế độ dual, màn duyệt điểm khác nhau, `ocr.trich_bang@1`, OCR hóa đơn giấy, OCR bảng kê.
**Để sau (khi xong engine):** chuyển ABBYY lên máy chủ; khi đó chạy lại ca 2, 5, 8.

## 2. Hiện trạng

| Mã | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|
| OCR-2, OCR-3 | ✅ | `cau_noi_abbyy.py`, `abbyy.py`, `vendor\` (G3-GOI-17); không chép thư mục có khóa |
| OCR-4, OCR-5 | ✅ CoreGia | PDF DEMO quét qua ABBYY giả trả lớp chữ, có vị trí; Word tải từ CoreGia, kiểm 3 bảng, ô trống/ô gộp và tiền/ngày. Tiền tố `w:` chuẩn. Tesseract với bảng chỉ có trong ảnh chưa suy cấu trúc bảng; có cảnh báo, chưa kiểm Word/ABBYY thật |
| OCR-6 | 🟡 | Gói SDK 2.0 đã ghim phiên bản và bảng nguồn/băm tệp; không dùng PyMuPDF/defusedxml. Hash wheel đa nền tảng và cài máy sạch thuộc lát OCR-6 |
| OCR-7 | ✅ mock | OCR-NOI: đọc theo trang, khối, dòng, từ, tọa độ. PDF thiếu lớp chữ bị từ chối để chuyển nguồn |
| OCR-8 | 🟡 | Đã kiểm bằng Core giả: hết hạn mức/ABBYY tắt tự chuyển Tesseract, ghi lý do. Có dependency dự phòng; executable/vie+eng cần cài riêng. Màn hạn mức chờ Core |
| OCR-9 | 🟡 | KN1–KN4 + KN-CHOT: cầu HTTPS kiểm khóa và IP, chống nhận trùng. **Mặc định tắt, chưa nối ABBYY thật**. Công cụ mở/đóng kết nối tạm ở `tu-core-cu\tools\` |
| OCR-10 | 🟡 | OCR-VUNG ở mã cũ đã kiểm mock; chưa khai năng lực trong SDK 2.0, chờ thiết kế cùng `e_doi_chieu` |
| OCR-11 | ✅ CoreGia trong phạm vi OCR-5 | `tests/test_ocr_may.py`: ca 2, 3, 4, 5, 7, 9 đã kiểm bằng Core giả; bộ DEMO chỉ dữ liệu giả. Ca 1, 6, 8 ngoài đợt này; chưa nghiệm thu UI |
| OCR-12 | ❌ | Chưa chạy ABBYY thật |
| OCR-13 | ✅ CoreGia | OCR-4 (phiếu 14/11, hoàn tất 15/11/2026): đã kiểm bằng Core giả (CoreGia), giữ/chốt/hoàn đúng một lần sau App mới hoặc tiến trình chết thật. Tạm dùng `kho_tam`; thay bằng lượt bền chung #10 khi Core có. Không dùng SDK riêng OCR |
| OCR-14 | ✅ CoreGia | OCR-4: chống trùng bền theo pháp nhân + băm trong `kho_tam`, không mất khi khởi động lại; ghi nguyên tử trước gửi, khóa đa tiến trình. Đã kiểm bằng Core giả (CoreGia), gồm hai tiến trình gửi trùng/cùng lấy kết quả muộn; chưa ABBYY/Core thật |
| OCR-15, OCR-16 | ✅ CoreGia | Quá 20 MiB, 61 trang, hỏng/hủy không trừ hạn mức sai; stderr có thời gian chờ nguồn/chạy và nguồn đọc, không nội dung/đường dẫn, kể cả lỗi bất ngờ. SDK chưa cấp mốc chờ Core; chưa nghiệm thu màn hình |

## 3. Bài máy test cuối (OCR-MAY, 9 ca, chỉ DEMO)

| Ca | Thao tác và kết quả phải thấy |
|---|---|
| 1 | Mở Quản lý engine → OCR: đúng phiên bản, ABBYY sẵn sàng, thấy hạn mức |
| 2 | Gửi PDF DEMO khi ABBYY bật: nguồn = ABBYY; có vị trí trang; tải được Word; tiền và ngày khớp đáp án; bảng đủ ô trống, ô gộp |
| 3 | Gửi 2 ảnh liên tiếp và 1 tệp trùng: báo số việc đang chờ; không xử lý trùng |
| 4 | Giả hết hạn mức: tự chuyển mask_ocr; ghi số đo đúng/sai (Anh chốt ngưỡng sau lần đo đầu) |
| 5 | Tắt cầu nối ABBYY: tự chuyển, không treo, ghi lý do |
| 6 | Gửi vùng cắt: trả chữ kèm cờ nghi ngờ |
| 7 | Tệp quá cỡ, quá trang, hỏng; hủy việc: lỗi dễ hiểu, không trừ hạn mức sai |
| 8 | Gọi cầu nối không có khóa → bị chặn; có khóa → được; log không lộ khóa |
| 9 | Nhật ký có thời gian chờ/chạy và nguồn đọc từng ca |

**Bộ DEMO:**
- PDF quét 3 trang có bảng;
- 2 ảnh;
- Word đáp án: "Công ty DEMO Ánh Dương", 1.000.000 VND, ngày 30/10/2026;
- 1 ảnh vùng cắt;
- PDF 61 trang, tệp lớn hơn 20 MiB, tệp hỏng.

### Bằng chứng OCR-5 — đã kiểm bằng Core giả (CoreGia)

- Ca 2: PDF ảnh 3 trang qua ABBYY giả, ba năng lực; Word tải từ CoreGia
  có 3 bảng 4×3, 10 ô gốc/bảng, một ô trống và ô đầu gộp 3 cột; nguyên
  văn tên công ty/tiền/ngày. Bản Word đáp án sinh riêng, nhãn DEMO.
- Ca 3: hai ảnh PNG/JPEG và ảnh gửi trùng cùng pháp nhân; số việc chờ
  3→2→1→0, thứ tự nhận PNG rồi JPEG, chỉ hai lần gửi ABBYY. Lượt trùng
  nhận cùng mã `CHUA_RO`; trả muộn/giao lại chốt đúng, chỉ tính 2 trang.
  Đây là quan sát CoreGia trong test, chưa phải màn hàng chờ Core thật.
- Ca 4: hạn mức bằng 0 tự chuyển Tesseract; lưu JSON số đo 3 trường ×
  3 trang. Tesseract thật trên máy: **9 đúng/0 sai/9 phép đối chiếu** tên
  công ty, tiền và ngày; fixture giả cũng 9/9 nhưng không là đo OCR.
  Chưa áp ngưỡng nghiệm thu, chưa đo độ chính xác toàn văn hoặc cấu trúc
  bảng ảnh; không dùng 9/9 để kết luận mọi chữ đúng.
- Ca 5: ABBYY tắt, ảnh JPEG chuyển Tesseract giả, có lý do, không tiêu
  hạn mức; kết thúc được, không chờ vô hạn.
- Ca 7: quá cỡ bị SDK chặn trước action; 61 trang/tệp hỏng bị engine
  từ chối trước nguồn; hủy lúc ABBYY chưa nhận rút tệp và nhả chỗ giữ.
- Ca 9: stderr JSON có nguồn, trạng thái và thời gian chờ ABBYY/chạy;
  kiểm cả Word, văn bản thuần, lớp chữ sẵn, lỗi, hủy, `CHUA_RO` và ngoại
  lệ bất ngờ có chứa chuỗi DEMO/đường dẫn. Không lộ nội dung/đường dẫn.
  Chưa có mốc vào hàng chờ trong SDK nên không suy thời gian chờ Core.
- **Ca 1 ngoài đợt này:** chờ thẻ trạng thái/hạn mức chung của Core.
  **Ca 6:** chờ chốt trích vùng cùng `e_doi_chieu`. **Ca 8:** chờ bí mật
  theo tên và cầu nối có khóa; đợt 1 chỉ Hot Folder cùng máy.
- Sáu ví dụ `chay_thu_demo` dùng PDF quét/PNG cho ba năng lực, chỉ
  Tesseract; `tests/chay_demo.py` tự dùng giả nếu thiếu bộ đọc và ghi rõ.
  PDF 61 trang, >20 MiB, tệp hỏng chỉ sinh trong thư mục tạm lúc test.
  Đã kiểm Windows; chưa chạy Linux, ABBYY/Core thật hoặc máy sạch.

## 4. Thư mục
| Thư mục | Nội dung |
|---|---|
| `ma-nguon\` | 38 tệp: `abbyy.py`, `cau_noi_abbyy.py`, `ket_noi_abbyy.py`, `chon_nguon.py`, `lop_chu.py`, `van_ban.py`, `bang.py`, `vung.py`, `ban_giao.py`, `chay.py`, `vendor\`, `lib\`, `contract\`, `tests\` |
| `tests-tu-core\` | 18 test cũ trong Core (kênh lượt OCR, đối chiếu, hot folder M9) |
| `tu-core-cu\src\` | `ha_tang\cong_ocr.py` (thế hệ cũ) |
| `tu-core-cu\tests\`, `tools\` | `test_abbyy_ket_noi_tam.py`, `abbyy_ket_noi_tam.py`, `MO-` / `DONG-KET-NOI-ABBYY-TAM.cmd` |
| `tu-core-cu\phia-core\` | Bản sao mã riêng OCR trong Core: `ocr_doi_chieu.py`, `routes_ocr_doi_chieu.py`, `ocr_doi_chieu.js`, SQL 126/130/131 |
| `docs\` | Quyết định cuối, phiếu, khảo sát "chưa rõ", khảo sát kết nối |

## 5. Thứ tự đề xuất
1. Gói độc lập theo cổng chung. Bỏ hàm SDK riêng; dùng lượt bền chung khi Core có.
2. Cài máy sạch (OCR-6), thẻ trạng thái/hạn mức chung của Core (ca 1), trích vùng (ca 6), cầu nối có khóa (ca 8). Ca 3 đã kiểm bằng Core giả ở OCR-5.
3. Lát 9: ABBYY thật trên máy hiện tại bằng PDF DEMO.
4. Ghép Core (K1–K6) → nghiệm thu tổng thể.

## 6. Chờ Anh (không chặn code)
- Xác nhận giấy phép FineReader Corporate cho dùng tự động phục vụ nhiều người qua máy chủ (trước khi chuyển ABBYY lên máy chủ).
- Chuyển các hợp đồng PDF ở `abbyy-hotfolder\in\` và DOCX ở `out\` vào thư mục lưu trữ.
- Ngưỡng đạt đúng/sai của mask_ocr: chốt sau lần đo đầu.
