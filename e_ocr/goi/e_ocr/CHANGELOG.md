# Thay đổi

## Chưa phát hành — 21/11/2026 — UI-OCR

- Chia màn cấu hình thành ba thẻ ABBYY, Tesseract và Hạn mức, bố cục hai
  cột trên màn rộng/một cột trên màn hẹp; hướng dẫn, ví dụ và lỗi từng ô.
- Thêm hai nút kiểm qua cổng quản trị dự kiến; kiểm metadata/quyền Hot
  Folder, bộ cài/ngôn ngữ Tesseract, không gửi tài liệu hay trừ hạn mức.
- Giữ CAS, trạng thái và cửa sổ hạn mức 30 ngày; bỏ kết quả kiểm cũ khi
  sửa bản nháp. Chưa có cổng quản trị thì hiện thông báo chờ Core.
- Bổ sung mô tả/ví dụ schema mọi cấp và bản khai dự kiến trong
  `KHAI-SDK-2.1.json`; không đổi engine.json hoặc hành vi xử lý việc OCR.
- Đã kiểm bằng Core giả (CoreGia), máy giả và KttCore giả. Ảnh DEMO nằm
  ngoài gói chạy, tại `e_ocr/docs/anh-ui-ocr/`. Chưa nối Core/ABBYY thật.

## 1.0.9 — 15/11/2026 — OCR-9

- Chuyển sang SDK 2.2.0: dùng `viec.ngan`, `viec.cau_hinh`; trạng thái định
  kỳ dùng `app.ngan`/`app.cau_hinh`. Bỏ cổng RAM/cấu hình tạm khỏi runtime,
  chuyển nguyên bản cùng `KHAI-SDK-2.1.json` vào `e_ocr/LUU-TRU/OCR-9/`.
- Phiếu khai ba bảng ngăn, schema cấu hình, migration CREATE TABLE trong
  `eng_e_ocr`, đủ cột hệ thống; kiểm kê bytes/SHA-256 mọi tệp gói.
- Bỏ pháp nhân khỏi khóa/lọc/giá trị ghi. Lượt mới cập nhật bằng CAS giữ
  nguyên id; không dùng xóa. Giữ cửa sổ đúng 30 ngày và phương án B.
- Hàng ngày được Core ẩn sau 45 ngày. Chỗ giữ chuyển vào mốc CAS không
  hết hạn, bảo toàn lượt chưa rõ kể cả dừng engine hơn 45 ngày.
- SDK chưa nhận kiểu ngăn `json`: map nhỏ lưu JSON text có trần 64 KiB;
  đọc numeric dạng chuỗi bằng chuyển đổi số nguyên có kiểm. UI đọc cùng
  biểu diễn, tiếp tục dùng `KttCore.engine("e_ocr").cau_hinh` và CAS.
- Test dùng CoreGia SDK 2.2.0, giữ các ca hành vi cũ, bỏ hai test băm cổng
  tạm; thêm kiểm TTL, bản chụp cấu hình, id/CAS và kiểm kê SQL. CLI DEMO
  chuẩn chạy với cấu hình mặc định SDK, không còn cổng thay thế.
- Chưa có `giao_dien_quan_tri` trong manifest SDK 2.2.0; ghi “Cần Core”,
  chưa kiểm nạp màn, migration hoặc lưu dữ liệu trên Core thật.

## 1.0.8 — 15/11/2026 — OCR-8

- Sửa theo kiểm độc lập của lead: màn Admin đọc tổng hợp chưa rõ cấp engine,
  chỉ số đếm/ngày, cập nhật cùng lô với lượt; ba phần hiển thị bắt lỗi riêng.
  KttCore giả kiểm phạm vi pháp nhân theo NganBoNho.
- Dọn dần hàng hạn mức hết cửa sổ 30 ngày trong cùng lô; giữ nguyên chỗ giữ
  còn dở, khai lưu tối đa 45 ngày. Ngôn ngữ Tesseract dùng enum/ô chọn bốn giá trị.
- README cấm chạy thật trên RAM, ghi quyền thư mục cha Hot Folder và cách dọn
  tạm `.e-ocr-…`; phân biệt công cụ OCR-7 đọc JSON qua `--cau-hinh` do Anh tự chạy.
- Đã nối ngăn chung NGAN-0 (PR #34), giữ nguyên hai tệp mẫu chung.
  Khai báo bảng truyền vào RAM từ `KHAI-SDK-2.1.json`, khóa cấu hình `{}`;
  đọc `TrangNgan` và `KetQuaLenh` theo API chung, kết quả lô chỉ đọc sau commit.
- Dùng pháp nhân trong khóa/bộ lọc hoặc ngăn theo việc; chuyển ngoại lệ
  ngăn/cấu hình chung thành `LoiNghiepVu`, giữ mã và khả năng thử lại.
- Bật hai test băm mẫu sau chuẩn hóa CRLF→LF; sửa fixture và test cạnh
  tranh qua API public. Giữ phương án B, chống gửi ABBYY hai lần và lô
  nguyên tử giữ trang/lượt. Đã kiểm bằng Core giả (CoreGia): 273 passed,
  0 skipped; SDK DEMO 6/6 ĐẠT, kiểm độc lập đạt.
- Chuyển cấu hình, sổ hạn mức và lượt ABBYY sang cổng `Ngan`; SDK 2.0
  tạm dùng `NganBoNho`, không ghi cấu hình/sổ trên máy. Giữ nguyên tệp cũ
  để lead chuyển lưu trữ. Hai mẫu dùng chung đã nối NGAN-0.
- `lay_hoac_tao` theo pháp nhân + băm, giữ trang và ghi lượt trong một lô;
  CAS có thử lại, mốc dùng chung qua nửa đêm. Đóng khe đua OCR-4 số 1
  bằng kiểm lại quyết định đọc cũ và quyền xử lý có CAS.
- Giữ phương án B: lượt chưa rõ không gửi lại, không tự hết hạn/hoàn
  trang; chốt/hoàn đúng một lần khi có kết quả hoặc bằng chứng từ chối.
- Thêm màn cấu hình ABBYY/Tesseract, hạn mức 30 ngày, trạng thái ngăn
  cập nhật định kỳ và lượt chờ đối chiếu; lưu cấu hình bằng CAS.
- Khai SDK 2.1 riêng trong `KHAI-SDK-2.1.json`, giữ hợp đồng manifest 2.0.
- Đã kiểm bằng Core giả (CoreGia), ABBYY giả và KttCore/DOM giả của Node;
  chưa kiểm Core/ABBYY hoặc màn trình duyệt thật. RAM mất sau khởi động lại.

## OCR-6 — 14/11/2026

- Ghim hash wheel Windows/Linux, bổ sung kiểm máy sạch và cập nhật nguồn gói.

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
