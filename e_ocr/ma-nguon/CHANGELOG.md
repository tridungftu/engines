# Lịch sử thay đổi engine OCR

## OCR-CR-4 — 08/11/2026

- Khi Core cấp SDK hỗ trợ lượt bền, kiểm và giữ lượt trước khi gửi
  ABBYY, chốt theo phiên bản sau khi nhận kết quả; chặn gửi lại tài liệu
  đã xử lý hoặc đang chờ đối chiếu để tránh xử lý trùng.
- Giữ lượt và hạn mức khi “chưa rõ” ABBYY đã nhận; chỉ hoàn trang khi có
  bằng chứng chưa nhận, chưa xử lý. Khi hủy, kiểm cả dấu vết kết quả và
  biên nhận để tránh hoàn nhầm trang đã dùng.
- Giữ đường tương thích khi chưa có SDK hỗ trợ; các kiểm thử dùng SDK và
  ABBYY giả, chưa nghiệm thu kết nối ABBYY thật.

## OCR-KN-CHOT — 07/11/2026

- Giữ giao diện backend cũ, chặn gửi trùng cùng nội dung trong một pháp
  nhân; giới hạn đọc kết quả Hot Folder và tệp bàn giao.
  Commit: `2525b639`, `8c22d4d5`.
- Cầu mặc định tắt, chưa nối ABBYY thật. Dấu “chưa rõ” chỉ trong bộ nhớ;
  lưu bền và đối chiếu là điều kiện chặn trước lát 9, theo
  [KS-OCR-CHUA-RO.md](../../docs/47-core/g3/KS-OCR-CHUA-RO.md).

## OCR-KN4 — 07/11/2026

- Nhận backend ABBYY do Core cấp; chống gửi trùng theo băm nội dung và
  pháp nhân, giữ mã tương quan và trang hạn mức khi chưa rõ đã nhận.
  Commit: `b36f8f5c`, `e39646ab`.
- Khóa và dấu chống trùng chỉ trong bộ nhớ; chưa bảo vệ qua khởi động
  lại hoặc nhiều tiến trình, chưa đủ điều kiện bật cầu thật.

## OCR-KN3 — 07/11/2026

- Thêm client HTTPS xác minh chứng thư, gửi khóa trong header và mã
  chống trùng; có thời hạn, trần phản hồi, hủy và báo mất xác nhận sau gửi.
  Commit: `543e3e9f`.
- Mặc định tắt; chỉ kiểm bằng kết nối giả, chưa nghiệm thu TLS/ABBYY thật.

## OCR-KN2 — 07/11/2026

- Thêm cầu HTTPS kiểm khóa và IP kết nối, chống nhận trùng, giới hạn
  thời gian/hàng chờ/dung lượng; chặn kết quả quá cỡ cả khi tệp lớn thêm.
  Commit: `1d71d577`, `c756c674`, `64b8053c`.
- Mặc định tắt; mã chống trùng chỉ sống trong phiên dịch vụ, chưa nối
  ABBYY thật hoặc chứng minh an toàn sau khởi động lại.

## OCR-KN1 — 07/11/2026

- Tách vận chuyển Hot Folder dùng chung, thêm adapter nhận PDF lớp chữ;
  giữ đường DOCX và sổ hạn mức hiện có. Commit: `b1bfd884`.
- Adapter mặc định tắt, không tự tính trang; trạng thái thư mục cục bộ
  chưa chứng minh ABBYY đang chạy.

## OCR-MAY-1 — 07/11/2026

- Thêm bộ tài liệu DEMO và bài kiểm engine cho ca 2, 4, 5, 6, 7, 9
  với ABBYY giả. Commit: `912267d0`.
- Ca 1, 3, 8 còn chưa kiểm; chưa nghiệm thu màn hình, chuỗi xử lý và
  ABBYY thật từ kết quả kiểm engine.

## G3-GOI-20 · GOI-OCR-GHIM — 07/11/2026

- Thêm `requirements.lock` cho CPython 3.13.14/Windows x64: ghim đúng
  metadata đang cài của pdfplumber, pdfminer.six, pypdfium2, Pillow, numpy,
  charset-normalizer, cryptography, cffi, pycparser; không cài/nâng gói.
- Ghi lý do dùng từng gói, dependency bắc cầu và SHA-256 nguồn gốc/bản
  vendor đã có trong `NGUON.md`; không thay byte vendor hoặc thuật toán.
- Ghi pymupdf/defusedxml là khai nhưng chưa cài/chưa dùng thật ở bản 1,
  không pin theo cận dưới khai báo. pytesseract không được engine dùng.
  Tesseract CLI báo 5.5.3.20260724, có vie/eng/osd; chưa kiểm OCR thật
  hoặc bản Tesseract tích hợp trong MuPDF.
- Bổ sung bảng giấy phép theo metadata, hướng dẫn môi trường sạch,
  dependency/model còn thiếu, biến môi trường và cầu ABBYY ngoài tùy chọn.
- Kiểm tĩnh trong `tests/test_doc_lap.py`: closure mọi import bên thứ ba
  (kể cả vendor/lazy), exact pin, lý do ngoại lệ/bắc cầu, phiên bản
  metadata và SHA vendor; có ca âm cho thiếu/thừa/ghim gói chưa cài.
- Giữ khung SDK đã gộp; không đổi version, không ghim wheel SDK 1.4.1
  candidate theo `KE-HOACH-G3-GOI.md` §6.3. Thử OCR/ABBYY thật và chốt
  dependency còn thiếu thuộc lead/các lát sau.
- Commit: `4ccc9048`.

## OCR-CHON — 07/11/2026

- Ưu tiên ABBYY, chuyển nguồn dự phòng khi hết hạn mức, máy lỗi/quá giờ
  hoặc PDF thiếu chữ; giữ/hoàn đúng lượt, chờ đối chiếu khi sổ chưa rõ.
  Commit: `6b429e7b`, `0b704f7f`, `57ac951d`, `18c5e364`.
- Không nhận kết quả một phần; còn thiếu dependency cho nguồn dự phòng
  thật, chưa nối ABBYY thật.

## OCR-VUNG — 07/11/2026

- Đọc vùng tứ giác, kiểm biên trước khi cắt, trả chữ kèm nguồn và cờ
  nghi ngờ; giữ hướng dẫn chọn lại vùng khi lỗi. Commit: `5066150c`, `e83f5fac`.
- Chưa có điểm tin cậy từ nguồn nhận dạng; chưa đo độ chính xác OCR thật.

## OCR-NOI — 07/11/2026

- Đọc lớp chữ PDF ABBYY theo trang, khối, dòng, từ và tọa độ; chặn
  hướng chữ không chắc chắn hoặc tọa độ sai. Commit: `0785acbe`, `af09f6b8`.
- Không nhận dạng lại ảnh nền; PDF thiếu lớp chữ bị từ chối để chuyển
  nguồn, chưa xác nhận đầu ra ABBYY thật.
