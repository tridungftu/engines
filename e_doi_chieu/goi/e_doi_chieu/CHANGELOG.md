# Thay đổi

## DC-13 — 15/11/2026 · công cụ ngoài runtime, 0.9.0 chưa phát hành

- Công cụ đo DEMO và wrapper CMD ASCII ngoài gói, chạy khô mặc định;
  không đọc cấu hình máy/khóa, không mạng, không gọi engine/Hot Folder.
- Adapter handle đề nghị chờ Core review; chỉ gửi qua cửa chung Core khi
  Anh chọn --that và host xác minh môi trường/DEMO. Mất ACK/chưa xong
  trả ChuaRo, không retry. Kết quả về Core/RAM; chỉ --bao-cao mới ghi
  một JSON DEMO mới ngoài gói trong workspace, không chứa nguồn nhạy cảm.
- Chấm đáp án độc lập, tử/mẫu/null và lý do; vùng sửa tay tính vào cổng
  100% Nghiêm trọng, 0 sửa thật bị ẩn; không suy bảo đảm ngoài bộ mẫu.
  Thiếu đo tách thất bại; chưa đặt ngưỡng detector/lệch giả/OCR kém.
- Đã kiểm bằng Core giả (CoreGia); phép đo môi trường thật, trình duyệt,
  CAS/quyền và hiệu lực module: CHỜ ANH TỰ CHẠY. Không đổi runtime/API,
  không thêm dependency. Hướng dẫn: docs/DC-13-THU-THAT.md ngoài gói.

## DC-12 — 15/11/2026 · kiểm gói 0.9.0 chưa phát hành

- Harness ngoài runtime nạp tệp DEMO/ngăn CoreGia và mẫu NGAN-0 riêng;
  10 ca chuỗi, có đọc DOCX qua SDK, Local/OCR giả và xuất JSON/PDF.
  Đáp án độc lập: bắt 5/5 thay đổi Nghiêm trọng, 0/8 sửa thật bị ẩn thành
  nhiễu; giữ 12 điểm máy (7 Nghiêm trọng). Không suy accuracy ngoài bộ.
- Thêm kiểm toàn tuyến về dẫn chứng, lỗi nguồn, thiếu detector/ảnh/tọa độ,
  hủy/mất lease, ACK/CAS/chống trùng/quyền giả, không lưu đĩa/mạng; một
  tiến trình `app.chay()` nhận dòng khởi động qua MayChuGia HTTP loopback.
- Công cụ `.sh`/`.cmd` ASCII kiểm wheel/version/hash/tag và cài offline
  vào venv sạch; mặc định chạy khô. Thiếu wheel Pillow và wheel/hash
  test nên chưa cài máy sạch, chưa chạy Linux. NGUON bổ sung giấy phép/
  metadata dependency có sẵn, không dùng hash metadata thay hash wheel.
- Không sửa runtime/manifest/SDK/Core/schema nguồn/mẫu; CLI chuẩn giữ
  1 DOCX DEMO sạch. Đã kiểm bằng Core giả (CoreGia); chưa trình duyệt Core
  thật, ngăn bền/RLS, OCR/AI thật hoặc nghiệm thu detector. PR: chờ lead mở.

## DC-11 — 15/11/2026 · 0.9.0 chưa phát hành

- Lõi đề xuất/duyệt chưa đăng ký SDK, đọc xác nhận/cặp từ nguồn ghim;
  cấm đổi nghĩa/vùng bảo vệ/định danh/căn cứ không rõ. Một vị trí đếm một
  lần; ngưỡng phải đã đo/duyệt, đủ ngưỡng không tự duyệt.
- Admin qua adapter chung, kiểm lại nguồn/quyền/Q14/ngưỡng, CAS và một
  lô ngăn chốt đề xuất/nhật ký/bộ vô danh phiên bản mới. Không sửa snapshot
  cũ hoặc tự áp bộ mới vào kết quả máy. Màn chỉ đọc KttCore/textContent.
- DC-11-CH giữ ngưỡng khi lưu giới hạn; SQL 003 thêm hai cột, dữ liệu
  phiên bản 3, chưa chạy DB thật. Không dependency/Cloud/đĩa bền. Q14 và
  C-DC-03 bắt buộc trước vận hành thật; docs/DC-11-CONG-CORE và VIEC ghi
  hợp đồng/kết quả kiểm; PR: chờ lead mở.

## DC-10 — 15/11/2026 · 0.8.0 chưa phát hành

- Thêm hai màn cấu hình/kết quả, CAS cấu hình, bộ lọc/nhiễu ẩn mặc định,
  nguyên văn hai phía/ảnh theo quyền Core và phần chưa kiểm rõ ràng.
  HTML là chữ; ngày/tiền có định dạng, không hiển thị mã kỹ thuật, không
  mạng ngoài/eval/HTML chưa lọc/ghi ngăn từ UI.
- Bốn lựa chọn xác nhận, nội dung/lý do bắt buộc; adapter nội bộ chỉ nhận
  danh tính/giờ/quyền Core tin cậy, không từ JSON UI. Nhật ký chỉ thêm +
  CAS lượt trong một lô, mã yêu cầu chống trùng/gửi lại, hai người khác
  nhau và thẩm quyền cấp hai theo Q03. Không đổi kết quả máy; Bản ký sai,
  mâu thuẫn hoặc thiếu kiểm giữ điều kiện chặn.
- Yêu cầu module chỉ qua adapter C-DC-04; thiếu cổng từ chối, thiếu ACK
  báo ChuaRo. Engine không mở hiệu lực hoặc phát sự kiện/gọi engine khác.
  Khai màn/quyền riêng trong KHAI-SDK-2.1, không thêm khóa UI vào manifest.
- SQL 002 chỉ thêm cột nhật ký, dữ liệu phiên bản 2; không chạy DB thật.
  Hai mẫu NGAN-0 chép nguyên làm tham chiếu/test RAM, runtime dùng SDK
  2.2.0. Không thêm dependency, không đĩa bền hoặc Cloud. Hợp đồng/chưa
  kiểm thật tại docs/DC-10-CONG-CORE; PR: **chờ lead mở**.
- Đã kiểm bằng Core giả (CoreGia): SDK DEMO **1/1 ĐẠT**, pytest
  **989 passed, 0 skipped** (47 ca DC-10); Node **22/22**, kiểm độc lập
  **ĐẠT**, kiểm kê **43 tệp** khớp bytes/SHA-256. Chưa kiểm Core thật,
  Linux hoặc nhật ký bền/hiệu lực thật. Báo cáo thực tế ở VIEC.md.

## DC-9 — 15/11/2026 · 0.7.1 chưa phát hành

- Thêm `doi_chieu.xuat_ket_qua@1`, trả đủ 11 trường tĩnh, JSON đầy đủ và
  PDF trong kho Core. Kiểm schema, snapshot đã ghim Ngăn, băm/quyền mọi
  nguồn, nguyên văn/offset/edit script, sàn mức, số đếm và giai đoạn.
  Hồ sơ còn điểm chờ phân loại không được xuất thành kết quả cuối.
- Tổng hợp năm kết luận; thiếu kiểm bắt buộc luôn Chưa đối chiếu được,
  giữ mọi điểm Nghiêm trọng/vùng sửa tay đã biết và đề nghị chặn bảo thủ.
  Cần xem khi đã kiểm đủ không tự chặn. Detector thử nghiệm DC-8 chưa
  đủ điều kiện kết luận sạch; không dùng danh sách rỗng thay kiểm đủ.
- Dùng lại validator DC-7 để tính lại ngoại lệ nhiễu từ nguồn; Core cần
  chuyển tiếp manifest OCR vùng khi ngoại lệ cần bằng chứng này.
- `chay.py` ghim cả đầu ra DC-8 bằng CAS/chống trùng để bước xuất kiểm
  được nguồn tin cậy; chỉ ghim khi đầu vào cũng đã được engine ghim.
- PDF tiếng Việt bằng Pillow đã ghim, font Roboto có nguồn/Apache 2.0
  đóng trong gói. Phân trang theo độ rộng thật, giữ mọi điểm/nhiễu/ảnh.
  Thiếu font/lỗi xuất trả lỗi nghiệp vụ; không thành công thiếu PDF.
- Tệp chỉ ở RAM; chỉ mục lượt xuất qua `viec.ngan`, gửi lại dùng kết quả
  đã chốt và kiểm lại quyền/băm hai tệp. Không sự kiện riêng/SQL/hiệu lực.
  Đã kiểm bằng Core giả (CoreGia); chi tiết và giới hạn tại VIEC.md.

## DC-S22 — 15/11/2026 · 0.7.1 chưa phát hành

- Chuyển sang SDK 2.2.0; cấu hình đọc bản chụp `viec.cau_hinh`, giữ
  `CHUA_CAU_HINH` khi thiếu trường bắt buộc; không còn bảng cấu hình.
- Bốn bảng khai thật trong manifest, SQL chỉ CREATE TABLE trong schema
  riêng, đủ cột hệ thống/kiểu/duy nhất và kiểm kê toàn gói bằng bytes/SHA.
- Mọi bảng pháp nhân qua `viec.ngan`; bỏ pháp nhân khỏi khóa/lọc, giữ
  CAS/chống trùng/thu hồi lượt/hủy. Dùng `lo.ket_qua` và đọc lại phiên bản
  bằng SDK; phong bì nhỏ tuần tự hóa JSON trong cột văn bản.
- Chuyển ba bản cổng tạm/bản khai vào LUU-TRU, không xóa. Test dùng
  `CoreGia.dat_cau_hinh/gay_xung_dot_ngan/xem_ngan`, giữ ca hành vi cũ.
- Gắn `$comment` vai trò trường DC-6 theo AI-12; kiểm tích hợp Hỏi AI từ
  `origin/main` trên 2.2.0 với provider Local giả, giữ `CHUA_RO` và 0 Cloud.
- Thêm kiểm nguyên tử/CAS, pháp nhân, bản chụp cấu hình, SQL/kiểm kê LF.
  Đã kiểm bằng Core giả (CoreGia); kết quả thật và giới hạn tại VIEC.md.
- Giữ ngưỡng hiệu năng cũ 2 giây: đệm phân tích tối đa 128 cụm tiền
  trong một lượt quét, giữ kết quả/vị trí riêng từng dòng. Ca 500.000 ký
  tự nhiều dòng lặp đo lại 0,5992 giây; không lưu đệm sau lượt quét.

## DC-7 — 15/11/2026 · 0.7.0 chưa phát hành

- Thêm `lech_dau.py`, `tu_dien.py`, nối `chay.py` sau so/hậu kiểm; không
  đổi capability/API/schema hoặc hai mẫu NGAN-0. Từ điển chỉ fixture
  DEMO ở tests, không có bộ mặc định trong gói; nguồn thật chờ DC-Q14.
- Phân nhóm từ edit script đã tái dựng; tra token đầy đủ/từ/âm tiết có
  phiên bản/băm/nguồn/giấy phép. Vắng mục giữ chưa biết/Cần xem; chỉ cặp
  vô nghĩa có chứng nhận cụ thể và ngoài vùng bảo vệ mới được xét nhiễu.
- Cặp có nghĩa cần Local AI đã kiểm trích dẫn và OCR lại đúng vùng cùng
  ra Word. Sáu cặp đổi nghĩa không tự được bỏ qua; cờ ABBYY không thay
  OCR lại. Manifest Core gắn đúng capability/kết quả nguồn, băm bản ký,
  phiên bản/trang/vùng/điểm/ảnh/offset; caller không tự cấp provenance.
  Thiếu/rỗng/khác OCR hoặc mất quyền kết quả giữ Cần xem, ảnh cắt nếu có.
- Tỷ lệ trang dùng số token OCR phân biệt bị lệch dấu trên tổng token
  trang; không đếm trùng edit/nút OCR, 0 token để null. Thiếu ngưỡng giữ
  chưa kiểm; bộ DEMO chỉ mô phỏng ngưỡng đã đo, DC-Q15 vẫn mở. Trang OCR
  kém giữ ảnh, nhóm nhiễu, riêng mọi điểm cứng và toàn bộ edit/điểm gốc.
- Sàn/nhật ký DC-5 giữ nguyên; validator DC-7 tính lại từ nguồn tin cậy
  trước khi cho Python phân loại ứng viên tạm thành nhiễu. Không hạ điểm
  cứng hoặc mức AI đã nâng. DC-9 cần dùng validator DC-7 và tham chiếu
  `ho_so_truoc_dc7`; không tin các boolean trong kết quả như chứng cứ.
- Ngan/CAS/chống trùng; mỗi bước giữ cả snapshot tiền nhiệm và kết quả,
  không lưu gì bền trên engine. Giữ hủy/ACK/giao lại và phục hồi snapshot
  mất quyền từ nguồn còn quyền. Test DC-4/DC-6 cập nhật số snapshot theo
  hai bước độc lập, không giảm kiểm chống trùng; 0 Cloud.
- Đã kiểm bằng Core giả (CoreGia); kết quả ba lệnh, số đo và Cần Core
  ghi tại VIEC. Chưa khép từ điển/contract OCR vùng/ngưỡng/model thật hoặc
  nợ Hỏi AI C-DC-07. Không commit/push; PR: **chờ lead mở**.

## DC-6 — 15/11/2026 · 0.6.0 chưa phát hành

- Thêm chuẩn bị `ho_so_doi_chieu → yeu_cau_ai` và hậu kiểm
  `tra_loi_ai → ho_so_doi_chieu`, ba tệp runtime theo phiếu. Prompt/
  module/phiên bản bắt buộc nghiệp vụ, thiếu `THIEU_PROMPT`; giữ API/
  schema chung, hai mẫu NGAN-0 và DC-5/DC-8. Không thêm dependency.
- Ngữ cảnh nguyên văn có mã điểm/trái/phải; khuôn chặt không cho model
  cấp nguồn/quyền/sàn. Snapshot/bản đồ Unicode/yêu cầu ở tệp Core,
  chuyển tiếp chỉ tham chiếu/băm (DEMO ≤4 KiB); giữ nguyên qua Hỏi AI.
- Kiểm Local/cặp/băm/prompt/phiên bản, đủ mã không thừa/trùng, câu trích
  thuộc đúng block AI và quay đúng nguồn/điểm. Giữ sàn/Nghiêm trọng bằng
  snapshot DC-5 đọc lại độc lập từ Core; không chắc/trích sai giữ Cần xem.
  Hình thức/nhiễu lưu đề nghị chờ DC-7, chưa hạ sàn hoặc xóa điểm.
- Trần 100 điểm, ngữ cảnh 500.000 ký tự, khuôn 32 KiB/chuyển tiếp 64 KiB;
  vượt `DC_QUA_NGAN_SACH_AI`, không cắt/chia lượt. Không ứng viên thì
  Core chọn chuỗi không AI; gọi nhầm bị từ chối, không tạo phản hồi giả.
- Giữ/chốt/chống trùng bằng Ngan/CAS, tệp chỉ ở Core/RAM; kiểm hủy,
  mất ACK/giao lại cùng tham chiếu và một bản kết quả mỗi việc. Provider
  Cloud = 0, không gọi máy thật, không commit/push; PR: **chờ lead mở**.
- Đã kiểm bằng Core giả (CoreGia). Test handler Hỏi AI-2 hiện tại giữ
  đúng chuyển tiếp/băm và `ChuaRo`, nhưng còn lỗi coi metadata phân
  loại là giá trị trích xuất: phản hồi giữ thiếu căn cứ/Cần xem. Cần
  lead Hỏi AI khép C-DC-07; chi tiết/kết quả nghiệm thu tại VIEC.
- Kết quả cuối bằng venv: DEMO **1/1 ĐẠT**, pytest **796 passed,
  0 skipped** (88 ca DC-6), kiểm độc lập **ĐẠT**; cả ba mã thoát 0.
  Một lượt hiệu năng DC-5 từng vượt 2 giây; sáu ca chạy riêng lại và
  bộ tổng cuối đều đạt, không sửa bộ quét/ngưỡng. Số đo và giới hạn ở VIEC.

## DC-5 — sửa theo kiểm độc lập lead, 15/11/2026 · chưa phát hành

- Bỏ ReDoS ở nhận diện tiền chữ; quét token tuyến tính và kiểm hủy trong
  dòng dài. Hai mẫu tìm số kèm đơn vị cũng đổi thành quét số một lần rồi
  kiểm đơn vị phía sau, tránh quét lại dãy số dài thiếu đơn vị.
- Cụm tiền chữ tối đa 64 từ; vượt giữ Cần xem, `khop=null`, nguyên văn
  đầy đủ. Bổ sung nghìn tỷ, hai nghìn linh năm, năm/lăm ở hàng chục và
  cách đọc gọn một trăm năm. Ngoài ngữ pháp vẫn chưa đủ kiểm.
- Ngoặc ngay sau một số tiền duy nhất, cùng dòng/ô, không cần nhãn:
  `1.000.000 đồng (hai triệu đồng)` → Nghiêm trọng; chữ không đọc được
  → Cần xem. Cụm mơ hồ/nhiều số/ngoặc lồng không tự ghép.
- Thuật toán `DC-5-2` không tái dùng kết quả cũ. Chỉ sửa hai tệp runtime
  và `tests/test_dc5.py`; giữ `_chung/**`, `ngan.py`, `cau_hinh.py` và API.
- Đã kiểm bằng Core giả (CoreGia): **629 passed, 0 skipped** (222 ca DC-5,
  thêm 49 ca), SDK DEMO **1/1 ĐẠT**, kiểm độc lập **ĐẠT**, cả ba lệnh mã 0.
  Bộ quét: `năm * 100000` **0,0640 giây**, `một trăm * 50000`
  **0,0690 giây**, 500.000 ký tự nhiều cụm tiền **0,4418 giây**;
  cùng một dòng **0,0482 giây**. Dãy số thiếu/có đơn vị khoảng 500.000
  ký tự (lấy thời gian lớn hơn giữa quét tiền và đặc trưng) **0,4450 /
  0,4591 giây**; tất cả <2 giây. Có test hủy giữa vòng quét/lập chỉ mục.
  Đây là số đo bộ quét bằng adapter DEMO, không phải toàn tuyến/OCR.
- SHA-256 LF hiện hành ở NGUON; PR: **chờ lead mở**. Chưa kiểm Core thật/
  Linux/OCR/model thật; không phát sinh Cần Core/Chờ Anh, không commit/push.

## DC-5 — 15/11/2026 · chưa phát hành

- Hoàn thiện `doi_chieu.so_van_ban@1` trong đúng ba tệp runtime:
  `quy_tac.py`, `tien_chu.py`, `chay.py`; dùng lại kiểm nguồn/căn/so DC-4,
  giữ nguyên API/schema/manifest, hai mẫu NGAN-0 và phần ảnh DC-8.
- Sàn Python và quy tắc trúng cho mọi điểm; quét toàn văn cùng vùng bảo
  vệ từ nhãn/metadata đã kiểm băm/offset. Chữ số, ngày/thời hạn, tiền/
  tiền tệ/tỷ lệ, định danh, phủ định/bắt buộc, cấu trúc và nghi nhầm OCR
  giữ Nghiêm trọng. Kiểm lại cả lát tương đương chuẩn hóa để không mất
  thay đổi mã/số/tên; NFC tương đương ngoài khác biệt nghiệp vụ vẫn giữ.
- Chỉ chuẩn phân cách số theo bộ ghim, giữ chuỗi 0 đầu; Decimal/int,
  không float hoặc đoán tiền tệ. Tiền snapshot `{so, tien_te}`; tiền lẻ
  dùng chuỗi thập phân chính xác, ngày đã phân tích dùng ISO.
- Kiểm số ↔ chữ ngay trong bản ký dù hai bản giống nhau. Đủ cụm/đơn vị
  và trái nhau → Nghiêm trọng; thiếu/mơ hồ/chưa hiểu ngữ pháp → Cần xem,
  `khop=null`, hạng mục chưa đủ kiểm. Không ghép qua dòng/ô.
- Nhật ký/sàn ghim băm, kiểm với snapshot gốc Core; chặn hạ mức, tự băm
  lại, thay căn cứ/xóa điểm. Áp lại không reset mức AI đã nâng. DC-6 còn
  phải kiểm nguồn/trích dẫn/Local; DC-5 không gọi AI hoặc Cloud.
- Snapshot/chống trùng/CAS/chủ/hạn chiếm qua Core/Ngan; trần điểm và
  bytes tính cả bằng chứng/nhật ký, không cắt danh sách. Vùng dài tham
  chiếu bằng offset/băm tới nguyên văn, tránh nhân cả dòng vào mỗi điểm.
- Đã kiểm bằng Core giả (CoreGia): DEMO **1/1 ĐẠT**, pytest **580 passed,
  0 skipped** (173 ca DC-5), kiểm độc lập **ĐẠT**, cả ba lệnh mã 0.
  Ma trận 29 cặp dương + 29 cặp không lệch; 4 ca tiền nội bộ trái số và
  8 ca tiền nội bộ khớp. Bắt đủ các điểm cài trong bộ này, không suy tỷ
  lệ thực tế. Chưa kiểm Core thật/Linux/OCR/model thật; PR: **chờ lead mở**.
  Không sửa `ma-nguon/`, không commit/push. Chi tiết tại VIEC/README.
## DC-8 — 15/11/2026 · 0.4.8 chưa phát hành

- Thêm `doi_chieu.phat_hien_sua_tay@1` ở khối đăng ký riêng: nhận hồ sơ
  `da_nhan/da_so`, đọc ảnh/băm/byte/pixel và phép đổi tọa độ tin cậy Core;
  quét toàn ảnh, giữ trang/phương pháp/phiên bản, PNG vùng có ngữ cảnh và
  snapshot mới trong kho Core. Không đọc chữ tay, không ghi đĩa/mạng/Cloud.
- Detector pixel thử nghiệm gạch đè/nét chèn gần chữ; không dùng màu mực
  hoặc mặc định nét ngoài OCR là sửa. Bổ sung duy nhất Pillow 12.3.0 và đúng
  hai hash wheel từ lock OCR; NGUON ghi môi trường có sẵn, chưa kiểm máy sạch.
- Chữ ký/dấu/ký nháy chỉ loại khi đủ căn cứ và không chồng nội dung; vùng
  chưa rõ vẫn cắt để xem, tách nguồn metadata khỏi phát hiện pixel. Giữ
  sàn Nghiêm trọng/xác nhận, điểm lệch cũ và đề nghị chặn; chưa kiểm đủ.
- Đo **thuật toán thật** trên 12 ca DEMO/11 raster: **3 TP, 0 FP, 3 FN,
  recall 50%**. Chưa đạt vận hành độc lập, `sua_tay=chua_kiem`, không kết
  luận không sửa tay. Local vision chưa đo, mọi số đo/model để null.
  Công cụ Q13 + `.cmd` ASCII đã chạy khô, không gọi model; khảo sát, đáp án,
  số đo thô và dự toán bổ sung ở docs DC-8. Không đổi tiêu chí DC-13.
- Đã kiểm bằng Core giả (CoreGia): SDK DEMO **1/1 ĐẠT**; pytest
  **486 passed, 0 skipped** (79 ca DC-8); kiểm độc lập mã 0. Adapter Core
  và detector giả chỉ kiểm giao thức, không dùng tính accuracy. Chưa kiểm
  Core thật/Linux/model/OCR/scan thật. PR: **chờ lead mở**; không commit/push.

## DC-4 — 15/11/2026 · 0.4.0 chưa phát hành

- Thêm `doi_chieu.so_van_ban@1`, đúng ba tệp runtime `can_chinh.py`,
  `so_chu.py`, `chay.py`; nhận `da_nhan`, trả `da_so`, ghim nguồn/bộ và
  snapshot tiền nhiệm, tải snapshot mới lên Core; chỉ mục/lượt qua Ngan.
- Căn Điều/Khoản/câu, bảng/dòng/ô và bảng lồng; giữ ô trống/gộp, đoạn lặp,
  chèn/xóa nguyên khoản và đuôi. Neo theo lần xuất hiện/LIS; so ký tự chỉ
  trong cụm nhỏ, cụm chưa có neo được giữ toàn bộ. Không căn được thì lỗi.
- Edit script tái dựng đủ nguyên văn lẫn chuẩn hóa hai bên; biên Unicode
  không tách phần NFC co/giãn dùng chung nguồn. Mã điểm ổn định, nguyên
  văn/offset/vị trí/căn cứ; lượt bỏ dấu chỉ gắn `chi_lech_dau`, không xóa.
- Giữ ứng viên chưa phân loại, không kết luận sạch. Kiểm Điều/Khoản kể cả
  trong Điều bị đảo. Bằng chứng trang cần liên kết Core tin cậy và ảnh có
  băm trùng; thiếu bằng chứng/đổi dàn trang giữ `chua_kiem` (C-DC-05).
- Trần điểm/ký tự/bytes/snapshot/300 giây, hủy theo cụm và tiến độ không
  nội dung. CAS/chủ lượt/chống trùng, tái dùng có quyền và phục hồi tệp
  Core thiếu; không đĩa bền, Cloud hay gọi engine khác.
- Đã kiểm bằng Core giả (CoreGia): SDK DEMO **1/1 ĐẠT**; pytest **407 passed,
  0 skipped** (110 ca DC-4); kiểm độc lập mã 0. Đo riêng lõi: 450.000 ký tự
  lặp **1,1848 giây**, 500 bảng **0,1856 giây**; không là số đo OCR/Core thật.
  PR: **chờ lead mở**. Không sửa API/schema chung/mẫu NGAN-0/ma-nguon;
  không commit/push. Chi tiết nguồn gốc phân trang tạm ở README/VIEC.

## DC-3 — 15/11/2026 · 0.3.0 chưa phát hành

Sửa theo kiểm độc lập lead, cùng phạm vi DC-3:

- Thêm hạn chiếm lượt trong ngăn, cấu hình thời hạn riêng hoặc mặc định
  thời hạn bước + 60 giây; CAS chiếm lại lượt quá hạn, mã chủ riêng ngăn
  worker cũ chốt/cleanup đè chủ mới. Chưa quá hạn trả `DC_DANG_XU_LY`.
- Hồ sơ Core cũ không đọc được chuyển `can_thu_lai` bằng CAS rồi dựng lại
  từ nguồn hiện tại đã kiểm quyền/băm/trần; sai băm vẫn từ chối.
- Khóa chống trùng ghim mã cặp, cảnh báo và băm cấu hình (gồm trần).
- Dựng chỉ mục văn bản → tập trang một lần, kiểm hủy trong vòng dài;
  12.000 nút OCR lề lặp đo riêng **0,1190 giây**, test `< 2 giây` đạt.
- Soft hyphen chỉ gom khoảng trắng liền kề, map không qua vùng đã bỏ.
  Bảng test 14 cặp vẫn phân biệt, 7 cặp bằng nhau theo bộ ghim và kiểm
  tắt từng quy tắc; thêm ca phục hồi, tranh lượt, chủ cũ quay lại và hủy.
- Đã kiểm bằng Core giả (CoreGia): pytest **297 passed, 0 skipped**
  (144 ca DC-3); DEMO Word **1/1 ĐẠT**; kiểm độc lập mã 0. Chưa kiểm
  Core thật/Linux; ngăn RAM/quyền tệp/đồng hồ/lease thật còn theo VIEC.
  SHA-256 LF hiện hành tại NGUON; PR: **chờ lead mở**, không commit/push.

Bản bàn giao trước kiểm độc lập:

- Thêm `doi_chieu.nhan_cap@1`: băm bytes yêu cầu trước parse JSON nghiêm,
  kiểm nguồn/tham chiếu/phiên bản/quyền qua SDK, đọc lại Word bằng DC-2,
  từ chối OCR rỗng/lỗi, thiếu tệp/quyền, sai băm và vượt trần.
- Snapshot đầy đủ tải Core, phong bì schema chỉ tham chiếu/băm/trạng thái;
  mới `da_nhan`, các số chưa đo null, không kết luận Khớp. Cấu hình/bộ đã
  ghim qua ngăn, thiếu cấu hình trả `CHUA_CAU_HINH`.
- NFC/khoảng trắng/nháy/gạch/ngắt dòng có map Unicode về nguyên văn/cấu
  trúc, giữ dấu/ô rỗng/gộp, không bịa trang Word; đầu/chân/số trang chỉ bỏ
  có căn cứ/whitelist, tiền/mã và nội dung thân giống header vẫn giữ.
- Ngăn chống trùng `lay_hoac_tao`, CAS chốt/nhường thử lại không đè chủ
  khác; cùng bytes với ID mới vẫn một lượt nhưng tái dùng phải có quyền
  tới snapshot và mọi tham chiếu cũ. Không lưu sổ đĩa/Cloud/engine khác.
- PNG kiểm CRC/DEFLATE/dòng/pixel; JPEG kiểm khung/kích thước, chưa giải mã
  DCT/quét. Giới hạn, nguồn gốc tệp và phục hồi chủ lượt theo lease còn
  cần Core/DC-8; chi tiết README/VIEC, không sửa API/SDK/schema chung.
- Khép test nợ DC-2: handler ném lỗi lạ chứa bí mật DEMO không lộ stderr
  khi chạy end-to-end CoreGia; ghi nợ field/AlternateContent từ chối toàn
  tài liệu, không nới trong lát này.
- Đã kiểm bằng Core giả (CoreGia): SDK DEMO Word 1/1 ĐẠT; pytest
  **237 passed, 0 skipped** (84 ca DC-3); kiểm độc lập mã 0. Chưa kiểm
  Core thật/Linux; PR: **chờ lead mở**; không commit/push.

## DC-2 — 15/11/2026 · 0.2.0 chưa phát hành

- Triển khai đọc DOCX trong RAM qua SDK, SHA-256 bytes thật, giữ nguyên văn,
  bảng lồng/ô trống/gộp ngang dọc và offset Unicode. Đọc cả thân, đầu/chân
  trang và chú thích; `so_trang=0`, `trang=[]`, không render/trang/hộp giả.
- Chặn sửa đổi/comment ở mọi phần XML Word bằng `DC_WORD_CHUA_CHOT`;
  không Accept All. Vùng chưa hỗ trợ/hỏng trả `DC_WORD_KHONG_DOC_DUOC`.
- Bảo vệ ZIP/XML/quan hệ ngoài, trần trước giải nén và bytes/EOF/CRC thật;
  không tin kích thước tự khai để bỏ đuôi. Không OCR/AI/Cloud/nhúng/mạng.
- Thêm DEMO DOCX sạch thực vào manifest; đúng ba tệp runtime của lát.
  Nguồn/băm TX-1 tại NGUON.md; phạm vi và quy ước nguyên văn tại README.
- Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest 153 passed,
  0 skipped; kiểm độc lập mã 0. Khép nợ DEMO rỗng của DC-0/DC-1.
  Chưa kiểm Core thật/Linux; không commit/push.

## DC-1 — 15/11/2026 · 0.1.0 chưa phát hành

- Thêm schema `ho_so_doi_chieu` theo DC-Q17 đã duyệt; chép nguyên ba schema
  chung `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, test so băm LF với
  `_chung/contract/`. Không sửa schema cấu hình DC-0 hoặc mẫu NGAN-0.
- Khai đúng tên bốn loại đã duyệt trong manifest; sửa nhãn tiếng Việt.
  Chỉ giữ khung Word `CHUA_LAM`, chưa thêm handler nhận cặp/đối chiếu.
- Đặc tả JSON cặp, snapshot/băm/giai đoạn và khảo sát nguồn tại
  `e_doi_chieu/docs/DC-1-KHAO-SAT.md`. Quyền tệp con/OCR vùng/ngưỡng detector
  vẫn cần Core/đo thật; không dùng đường máy để bù nguồn thiếu.
- Đã kiểm bằng Core giả (CoreGia): pytest 46 passed, 0 skipped; kiểm độc lập
  mã 0. `thu` giữ 0 demo nghiệp vụ, SDK 2.0 trả mã 1 do danh sách rỗng;
  chưa đạt điều kiện kiểm chung. Không mạng/Cloud hoặc lưu dữ liệu bền.

## 0.1.0 ? 15/11/2026

- DC-0: khung SDK 2.0, khai b?o d? ki?n SDK 2.1, ng?n RAM v? c?u h?nh; ??c Word tr? CHUA_LAM. ?? ki?m b?ng Core gi? (CoreGia); ch?a ki?m nghi?p v?.
