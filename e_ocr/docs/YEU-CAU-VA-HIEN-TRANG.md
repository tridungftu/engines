# e_ocr — Nhận dạng văn bản: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- `QUYET-DINH-CUOI-e_ocr.md` (06/11 21:00) và `PHIEU-ENGINE-e_ocr.md`.
- Chỉ đạo của Anh về "chưa rõ" (phương án B). Anh cho phép mở kết nối tạm đến ABBYY.
- TL 57 §9: `ocr.trich_vung@1` phục vụ Đối chiếu bản ký.
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

**Hiện trạng** đối chiếu `ma-nguon\CHANGELOG.md` (tới OCR-CR-4, 08/11). Ký hiệu:
- ✅ có, đã kiểm thuần/mock
- 🟡 một phần
- ❌ chưa có

## 0. Kết luận
- **OCR là engine riêng.** Nguồn ưu tiên là **ABBYY FineReader Hot Folder**. Dự phòng là **mask_ocr chỉ nhánh Tesseract** (vie+eng).
- Năng lực v1:
  - đọc văn bản: có vị trí trang, có bản Word, giữ ô trống và ô gộp của bảng;
  - trích vùng `ocr.trich_vung@1`.
- **Phần lõi đã có và kiểm bằng mock:** đọc lớp chữ PDF ABBYY, trích vùng, chọn nguồn tự chuyển, cầu nối HTTPS có khóa, lượt "chưa rõ" bền, ghim thư viện.
- **Chưa:**
  - nối ABBYY thật (lát 9);
  - ca 1, 3, 8 của bài máy test;
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
| OCR-4, OCR-5 | 🟡 | `van_ban.py`, `bang.py`, `ban_giao.py`. Chưa đo trên PDF thật |
| OCR-6 | ✅ | G3-GOI-20 (`4ccc9048`): `requirements.lock` cho CPython 3.13.14/Windows x64, bảng giấy phép. pymupdf và defusedxml đã khai nhưng chưa dùng thật |
| OCR-7 | ✅ mock | OCR-NOI: đọc theo trang, khối, dòng, từ, tọa độ. PDF thiếu lớp chữ bị từ chối để chuyển nguồn |
| OCR-8 | 🟡 | OCR-CHON có mã; **còn thiếu dependency cho nguồn dự phòng**. Màn hạn mức chưa có |
| OCR-9 | 🟡 | KN1–KN4 + KN-CHOT: cầu HTTPS kiểm khóa và IP, chống nhận trùng. **Mặc định tắt, chưa nối ABBYY thật**. Công cụ mở/đóng kết nối tạm ở `tu-core-cu\tools\` |
| OCR-10 | ✅ mock | OCR-VUNG. **Chưa có điểm tin cậy** từ nguồn nhận dạng; chưa đo độ chính xác |
| OCR-11 | 🟡 | OCR-MAY-1: đã có bài cho ca 2, 4, 5, 6, 7, 9. **Ca 1, 3, 8 chưa** |
| OCR-12 | ❌ | Chưa chạy ABBYY thật |
| OCR-13 | 🟡 | CR-4: giữ lượt và hạn mức khi "chưa rõ". Phía Core dùng **mã riêng OCR** (`ocr_doi_chieu.py`, SQL 126/130/131, SDK `ocr_giu_luot` / `ocr_chot_luot` / `ocr_doc_luot`) → cần "lượt bền" chung |
| OCR-14 | 🟡 | KN4: chống trùng theo băm. Dấu chống trùng chỉ trong bộ nhớ, **mất khi khởi động lại** |
| OCR-15, OCR-16 | 🟡 | Có trong bài máy test; chưa nghiệm thu trên màn hình |

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
2. Bổ sung dependency dự phòng, màn hạn mức (giao diện của engine), ca 1, 3, 8.
3. Lát 9: ABBYY thật trên máy hiện tại bằng PDF DEMO.
4. Ghép Core (K1–K6) → nghiệm thu tổng thể.

## 6. Chờ Anh (không chặn code)
- Xác nhận giấy phép FineReader Corporate cho dùng tự động phục vụ nhiều người qua máy chủ (trước khi chuyển ABBYY lên máy chủ).
- Chuyển các hợp đồng PDF ở `abbyy-hotfolder\in\` và DOCX ở `out\` vào thư mục lưu trữ.
- Ngưỡng đạt đúng/sai của mask_ocr: chốt sau lần đo đầu.
