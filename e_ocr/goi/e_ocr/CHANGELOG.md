# Thay đổi

## 1.0.5 — 14/11/2026 — OCR-5 (thực hiện 15/11/2026)

- Bộ DEMO hoàn toàn giả: PDF ảnh 3 trang có bảng ô trống/ô gộp, PNG/JPEG,
  Word/JSON đáp án; bộ sinh ở tests, ca lỗi/quá cỡ chỉ sinh lúc test.
- Sáu ví dụ SDK cho PDF quét/PNG và cả ba năng lực, chỉ Tesseract.
  Công cụ CoreGia ngoài gói tự dùng Tesseract giả khi thiếu bộ đọc.
- OCR-MAY ca 2/3/4/5/7/9: ABBYY giả, hàng chờ/gửi trùng, đo tiền/ngày,
  chuyển nguồn, lỗi/hủy và nhật ký stderr; ca 1/6/8 ghi rõ ngoài đợt này.
- Nhật ký chỉ chứa mã cố định, nguồn và thời gian chờ nguồn/chạy; chặn
  traceback ngoại lệ bất ngờ tại action, giữ ngoại lệ hủy/chưa rõ/transport.
- Đăng ký namespace `w`/`xml` chuẩn cho Word; kiểm document.xml có `w:`.
- Đã kiểm bằng Core giả (CoreGia); giữ nguyên ba nợ OCR-4 trong VIEC.md,
  không thay giao thức Hot Folder hoặc thư viện.

## 1.0.4 — 14/11/2026 — OCR-4

- Giải gộp 15/11/2026 trên nền OCR-2/OCR-3 chính thức (1.0.3); giữ xuất
  Word qua bộ chọn nguồn và toàn bộ 181 test main, thêm 37 test OCR-4.

- Lưu lượt ABBYY bền theo pháp nhân + băm + lần gửi; ghi `dang_gui` và
  giữ hạn mức trong một giao dịch nhiều khóa trước khi công bố tệp.
- Giao lại/việc mới cùng nội dung đối chiếu kết quả đúng mã trước; lượt
  chưa rõ không gửi lại, không chuyển Tesseract hoặc tự hoàn hạn mức.
- Khóa theo mã lượt đa tiến trình; khởi động lại chốt kết quả muộn và sổ
  đúng một lần. Thao tác #10 `luot-ben` sẽ thay nhật ký tạm khi Core có.
- Hủy/lỗi sau khi ABBYY đã trả PDF phải dọn kết quả kể cả chưa đọc bytes;
  chỉ `ChuaRo` giữ PDF/biên nhận để đối chiếu. Chốt bền lỗi không làm mất PDF.
- Biên nhận từ chối rõ, đúng mã và không tiêu trang mới cho phép hoàn,
  sau khi đã rút/dọn tệp vào còn chờ. Không rút được thì tiếp tục ChuaRo;
  lỗi parser hoặc không có kết quả không được tự hoàn. Quy ước Hot Folder
  tạm được ghi trong README, chưa kiểm trên ABBYY thật.
- Test CoreGia/ABBYY giả gồm tiến trình chết thật, App mới, giao lại,
  hai tiến trình trùng tệp/cùng lấy kết quả muộn, hủy và lỗi ghi bền.

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
