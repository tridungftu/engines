# Thay đổi

## 1.0.3 — 14/11/2026 — Gộp OCR-2 và OCR-3

- Hợp nhất chọn nguồn và xuất Word qua cùng lõi nhận dạng.

## 1.0.2 — 14/11/2026 — OCR-2

- Thêm `chon_nguon.py`, `tesseract.py` riêng; giữ nguyên `chay.py` để ghép
  OCR-3. ABBYY ưu tiên, chuyển khi hết hạn mức/tắt/lỗi chắc chắn chưa nhận;
  `chi_abbyy` không chuyển, `chi_tesseract` bỏ ABBYY và sổ.
- Sổ hạn mức `KhoTam` cập nhật nguyên tử, cửa sổ trượt đúng 30 ngày theo
  giây; giữ chỗ trước gửi, chỉ ghi trang đã dùng khi nguồn đã nhận. Đã nhận
  chưa trả → `ChuaRo`, không hoàn trang hoặc chạy Tesseract.
- Chuyển vendor mask_ocr phần PDF chữ sẵn, DOCX và bảng ô trống/ô gộp;
  OCR dùng Tesseract CLI + pypdfium2 đã ghim. Không thêm dependency/model.
- Thiếu executable/ngôn ngữ → `NGUON_DU_PHONG_CHUA_CAI`; có công cụ kiểm
  ASCII để Anh tự chạy, hướng dẫn ở `VIEC.md` mục **Cần cài**.
- **Đã kiểm bằng Core giả (CoreGia)**, mock cho CI và Tesseract thật bằng
  DEMO trên Windows; chưa kiểm Linux, ABBYY/Core thật hoặc cài máy sạch.
## 1.0.2 — 14/11/2026 — OCR-3

- Nối `ocr.xuat_word@1` vào lõi đọc chung, dựng DOCX trong bộ nhớ và gửi
  bằng `viec.tai_tep_ra`; tên `<tên gốc không phần mở rộng>-OCR.docx`.
- Giữ văn bản, ô trống, `gridSpan`/`vMerge` kể cả gộp hai chiều; kiểm đủ
  lưới ô, không tự thêm ô thiếu. Bảng giữ tọa độ point và kích thước lưới;
  mỗi trang nguồn là một section Word, giữ thứ tự và khổ trang.
- Tách `xuat_word.py`/`ban_giao.py`, không phụ thuộc kênh Core cũ, không
  ghi nội dung ra đĩa hoặc thêm dependency. Bản mask_ocr trong repo không
  có bộ ghi Word; chuyển quy tắc cấu trúc từ parser sang OOXML thư viện chuẩn.
- Thêm DEMO PDF có bảng 3 trang và test mở lại DOCX bằng zipfile/XML:
  đủ ô trống, gộp ngang/dọc, tọa độ, phân trang, tiền/ngày nguyên văn.
- Đã kiểm bằng Core giả (CoreGia); chưa kiểm Word/Core/ABBYY thật. Word
  có thể dàn lại chữ theo font; không cam kết hình thức khớp từng pixel.

## 1.0.1 — 14/11/2026 — OCR-1

- Chuyển bốn mô-đun lõi từ `ma-nguon/`, bỏ phụ thuộc Core/cổng OCR cũ;
  hai action đọc dùng chung lõi SDK 2.0.
- Đọc lớp chữ PDF kể cả chữ ẩn ABBYY, giữ dấu/tiền/ngày và tọa độ trang,
  dòng, từ; đọc bảng có đường kẻ, giữ ô trống/ô gộp. Không OCR lại ảnh nền.
- Hot Folder cục bộ: công bố tệp nguyên tử, chờ đúng mã tương quan, có
  thời hạn/hủy/dọn tạm; đã nhận chưa trả thì `ChuaRo`, không báo thành công.
- Tự đếm trang trước gửi, từ chối hơn 60 trang/tệp hỏng; trả băm đầu vào,
  nguồn đọc, phiên bản và cảnh báo; lỗi tiếng Việt không chứa đường dẫn.
- Thêm hai DEMO lớp chữ 3 trang vào phiếu để kiểm chung ngay trong OCR-1;
  test ABBYY giả chạy bằng luồng nền và PDF DEMO thuần Python.
- Ghim lại dependency đã có trong lock cũ; chưa làm lock wheel/máy sạch
  OCR-6. **Đã kiểm bằng Core giả (CoreGia)** trên Windows, chưa kiểm Linux,
  ABBYY/Core thật. Tesseract, Word, sổ hạn mức và lượt bền thuộc các lát sau.

## 1.0.0 — 14/11/2026 — OCR-0

- Tạo gói độc lập, phiếu 2.0 và ba hàm tạm trả `CHUA_LAM`.
- Thêm cấu hình JSON ngoài gói, schema cấu hình và kho JSON cho dữ liệu tạm.
- Kho ghi nguyên tử, khóa tệp thật trên Windows/Linux; kiểm cạnh tranh hai
  tiến trình bằng `spawn`.
- Chép schema `van_ban_tai_lieu` dùng chung, test so SHA-256; mẫu DEMO chỉ
  minh họa schema, chưa có DEMO xử lý OCR trong phiếu.
- Cổng đã kiểm bằng Core giả (CoreGia); chưa nối nguồn OCR hoặc Core thật.
