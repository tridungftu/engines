# Thay đổi

## Chưa phát hành — 15/11/2026, MASK-B1 cổng ZIP/XML nội bộ

- Thêm đúng `doc_tep.py`, `zip_an_toan.py`, `xml_an_toan.py`; chưa gắn handler/năng lực tệp, giữ manifest 1.1.0. Chỉ stdlib/SDK, RAM, Cloud tắt.
- Áp trần thử nghiệm của phiếu §7.3: ZIP 1/8/2 MiB, 256 phần, ratio 200:1; XML depth 64/100.000 node tổng/50 sheet/20.000 ô/500.000 code point; helper chiều ra và JSON có trần riêng. Chặn tên/header/extra/comment, ZIP64/overlap/EOF/CRC/size giả, XXE/PI, quan hệ ngoài và part mồ côi/lạ; lỗi cố định, không trả một phần, giữ hủy.
- Lần closure mẫu, chép chọn lọc có nguồn/quyền/symbol/SHA bytes và LF trước–sau trong NGUON.md; không sửa nguồn mẫu hoặc thêm dependency. Profile và reader ngữ nghĩa/map các lát B2/B3 được phân biệt rõ.
- 276 test DEMO mới; toàn bộ 1248 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped. Kiểm độc lập đạt; adapter DEMO 2/2. CLI SDK chuẩn 0/2 do thiếu quyền như trước. Đã kiểm bằng Core giả (CoreGia) gói hiện có; chưa kiểm năng lực tệp nối Core/Office/Local thật.

## 1.1.0 — 15/11/2026, MASK-2c-2 chuẩn bị Local AI

- Thêm `mask.chuan_bi_ai_cuc_bo@1`, nhận cùng ba loại đầu vào che văn bản và chỉ trả `yeu_cau_ai`. Hai năng lực cũ giữ nguyên `tra`. Lớp MASK-2b chạy đầy đủ; còn sót, thiếu từ điển hoặc lỗi vẫn chặn.
- Snapshot Core bao nguyên hồ sơ MASK-2c-1, kết quả quy tắc đạt, prompt có mã/phiên bản do module/quy trình cấp, khuôn, profile và biên nhận budget/deadline. Băm JSON chuẩn/UTF-8; chỉ mục `chuan_bi_ai` qua ngăn chỉ giữ băm/tham chiếu. Không trả bản che trung gian.
- Đoạn phủ đủ gốc bất biến, tối đa 8.000 code point gồm overlap tối đa 512 mỗi phía, làm tròn vào biên an toàn và giữ ít nhất 300 khi đủ nguồn. Tối đa 128 đoạn; không cắt từ/NFD/Cf hoặc bỏ đuôi. Span gốc đã nhận diện và khuôn phản hồi đều bị chặn khi dài hơn 300.
- `chuyen_tiep.mask_2c` đúng profile đã được lead duyệt; chỉ Local, không gốc/map/danh sách tên. Giữ nguyên NFD/Cf/selector/tab/NBSP trong `tai_lieu`. Khuôn bắt buộc quét hết, liệt kê mọi người/tổ chức/địa chỉ và từng offset lặp.
- Cổng Core nội bộ phải ghim cấu hình, đo token từng đoạn với cả prompt/khuôn/đầu ra, giữ deadline bất biến, kiểm ACL/lease và bàn giao toàn kế hoạch. Thiếu cổng/budget/snapshot/quyền thì từ chối. Retry/mất ACK/CAS không cấp lại alias hoặc tăng đếm; hủy không nộp kết quả.

Đã kiểm bằng Core giả (CoreGia): 972 passed, 4 xfailed giữ nguyên, 190 subtests passed; DEMO có quyền 2/2, kiểm độc lập đạt. CLI SDK chuẩn 0/2 vì thiếu nguồn quyền. Chưa kiểm Core/model thật hoặc Linux thực tế; không công bố chạy dài thật, Cloud vẫn tắt. Không đổi Core/SDK/schema chung/nguồn cũ/dependency; đúng năm tệp mã theo phiếu.

## 1.0.0 — 15/11/2026, MASK-2c-1 map và snapshot nội bộ

- Ghi edit script từ từng khoảng thực tế trong vòng thay tên; giữ riêng gốc Unicode, bản dò NFC sau bỏ Cf/selector và bản che. Khoảng alias bao toàn bộ khoảng gốc; quan hệ NFD/Cf không được coi là song ánh hoặc bằng chứng che cả tên khi chỉ che prefix.
- Thêm cửa nội bộ `che_co_anh_xa`; kết quả công khai giữ nguyên cấu trúc. Map được kiểm phủ/ngữ nghĩa/băm trước phát hành; lớp MASK-2b còn chặn hoặc thiếu tài nguyên vẫn chặn.
- Snapshot/map/kế hoạch đoạn bất biến trong RAM, tuần tự hóa JSON chuẩn có băm và phiên bản. Kiểm kế hoạch do Core cấp: phủ đủ, biên từ/NFD/Cf, băm đoạn và các trần 8.000/512/128; thuật toán lập đoạn thuộc MASK-2c-2.
- Kho snapshot dùng port Core có quyền; Ngan chỉ giữ chỉ mục tham chiếu/băm. Thiếu quyền, tệp, chỉ mục hoặc băm/map sai thì từ chối; giữ ChuaRo, hủy và xung đột. Adapter CoreGia DEMO đặt ngoài gói.
- Giữ ngưỡng hiệu năng cũ: bỏ quét Cf với ASCII; nghi vấn số dài trùng toàn văn dùng khoảng khớp đúng chữ thay việc dựng lại bộ khung. Vẫn chặn, giữ tiền/ngày và offset; có kiểm đối chiếu matcher cũ.

Đã kiểm bằng Core giả (CoreGia); chưa nối Core/Local thật. Giữ bốn xfail held-out, Cloud tắt; không thêm năng lực, schema chung hoặc dependency.

## 1.0.0 — 15/11/2026, sửa MASK-2b theo kiểm độc lập

- Chấm điểm tên có căn cứ: ≥8 che, 4–7 chặn con_sot, <4 bỏ qua; chỉ nhận họ từ vn_surnames và 15 họ hiếm do lead cấp. Thêm âm tiết tên/đệm và từ ghép tự soạn, áp dụng từ ghép ở mọi vị trí; giữ Phan khi không thuộc cụm thường.
- Nhận danh xưng đầy đủ và a./c./ô./b., kể cả tên 1–3 âm tiết ngoài danh sách; phân biệt có/cô, chủ/chú, chí/chị và cụm chi phí/chu kỳ. Tên Latin có ngữ cảnh được chặn; nghi vấn đã che trọn như công ty không làm hỏng recall công ty cũ.
- Giữ số văn bản dạng số/năm sau nhãn số, gồm số 01/2026; mã có hậu tố chữ/tài khoản vẫn được kiểm. Giữ Cf/NFD, alias, tiền/ngày và hậu kiểm prefix/tên dài.
- Chuyển đủ 32 ca t9 và 41 câu t10 thành pytest tham số hóa, đưa hai văn bản tham khảo nguyên nội dung vào LUU-TRU ngoài gói. Đo thật: 0/32 lọt; báo nhầm 2/41 (4,88%), không che thừa; còn câu mập mờ và nhãn tài khoản 331. Pytest 717 passed, 190 subtests passed; DEMO 2/2 và kiểm độc lập đạt.

Đã kiểm bằng Core giả (CoreGia); CLI SDK chuẩn 0/2 vì thiếu quyền. Chỉ hai tệp runtime, không thêm dependency hoặc đổi API/ngăn/cấu hình chung. Nợ tên nước ngoài không ngữ cảnh và giới hạn từ vựng được ghi trong VIEC/báo cáo.

## 1.0.0 — 15/11/2026, MASK-2b tên người viết thường không nhãn

- Thêm bộ dò họ + 1–3 âm tiết không phụ thuộc hoa thường/dấu; dùng lại bốn từ điển sạch, thêm cụm thông dụng trùng họ trong mã, không thay tài nguyên đã duyệt.
- Che tên có danh xưng hoặc khớp tên chính thức sau bỏ dấu; giữ bí danh đã duyệt. Nghi vấn còn lại vào `con_sot` với lý do cố định, không phát hành; chặn cả trường hợp chỉ che prefix và danh mục trùng nhau sau bỏ dấu. Bí danh tạm không nâng thành tên đã duyệt.
- Hậu kiểm độc lập bộ dò cũ; giữ ánh xạ NFC/NFD/Cf, tiền/ngày và quyền/ngăn. Thêm test CoreGia, 30 câu DEMO nghiệp vụ và công cụ đo trước/sau với 14 mẫu có sẵn; các báo nhầm nền được báo riêng, không giấu hoặc sửa ngoài lát.

Đã kiểm bằng Core giả (CoreGia); CLI SDK chuẩn còn thiếu nguồn quyền. Không thêm dependency, không đổi API, ngăn hoặc cấu hình chung; phần tệp và bật Cloud vẫn ngoài phạm vi.

## 1.0.0 — 15/11/2026, MASK-7 khảo sát tệp

- Thêm bằng chứng/test DEMO và công cụ đo ngoài gói; trình trần tệp/đầu ra/ZIP, nguồn hoặc phương án và giờ mới cho MASK-8…11. Chưa thêm năng lực/thuật toán tệp hoặc dependency; chưa triển khai phần thiếu.
- Sửa mô tả NGUON về kho/cấu hình cũ đã chuyển LUU-TRU; nhánh chết trong chốt kho đã được lát trước loại bỏ, không sửa mã chạy.

Văn bản đã kiểm bằng Core giả (CoreGia); helper tệp cũ chỉ kiểm nguồn độc lập. Trần/phương án chờ Anh/lead; Core thật, Word/Excel thực và PDF/OCR chưa kiểm trong MASK-7.

## 1.0.0 — 15/11/2026, sửa an toàn theo kiểm độc lập của lead

- Bỏ mọi Cf/variation selector trước dò NFC, giữ ánh xạ về nguyên văn; che tên có ký tự vô hình, NFD, NBSP, tab/xuống dòng và mã số bị tách. Bỏ ký tự vô hình còn lại; kiểm chặn tại phong bì, từ chối nếu không ánh xạ được.
- Bí danh tạm riêng cho từng mã yêu cầu; chặn mở/ghi tham chiếu chéo, kể cả mã chưa duyệt không mang tiền tố MASKTAM. Giữ mã chính thức/Junsky ổn định và quyền mở trong cùng pháp nhân.
- Bọc ngoại lệ ngăn/port bằng thông điệp cố định, không để traceback mang tên gốc; bổ sung kiểm stdout/stderr. Chặn chốt bản che không đạt, thay nhánh đóng yêu cầu không được dùng.
- Chuyển nguyên hai mô-đun lưu trên máy và schema cũ ra ngoài gói, sang LUU-TRU; kiểm độc lập chặn mã đọc biến cấu hình máy và import hiện vật lưu trữ. Giữ các test lịch sử qua helper ngoài gói.

Đã kiểm bằng Core giả (CoreGia); chưa kiểm Core thật. Không đổi mẫu ngăn/cấu hình chung, không thêm dependency.

## 1.0.0 — 15/11/2026, nối MASK-3b với NGAN-0

- Đã nối ngăn chung NGAN-0; giữ nguyên hai tệp mẫu, bật test so băm LF cho mẫu và từ điển.
- Khai báo bảng bằng `bang` từ KHAI-SDK-2.1; dùng TrangNgan/KetQuaLenh, view pháp nhân và cấu hình dict/None đúng API chung.
- Giữ ngăn được cấp; RAM mặc định có đủ khai báo. Chuyển ngoại lệ chung thành LoiNghiepVu ở biên SDK, giữ mã lỗi khi đọc snapshot.
- Dọn trường cũ bằng xóa/tạo lại nguyên tử có CAS; tính đủ trần 100 lệnh. Giữ các test an toàn MASK-5 và ChuaRo/chống đếm lặp.

Đã kiểm bằng Core giả (CoreGia), qua cổng DEMO có quyền tin cậy trong tests; không gọi Cloud. Ngăn/quyền Core thật vẫn còn chờ.

## 1.0.0 — 15/11/2026, MASK-3b → MASK-6

- Thay kho tệp trên đường chạy bằng cổng ngăn; RAM tạm khi chưa có SDK 2.1. CAS bảo vệ toàn bộ alias, hàng chờ, đếm gặp, tham chiếu và dấu lượt.
- Chốt bộ tiền tố MASKCT/MASKCN/MASKDC/MASKMST/MASKTK/MASKKHAC/MASKTAM; giữ mã Junsky hợp lệ, chặn mã trùng tiền tố.
- Thêm schema và handler che/mở văn bản, mở chuỗi trong dữ liệu/trích dẫn AI; trích dẫn đổi chữ phải kiểm lại.
- Chép bốn từ điển sạch của lead, kiểm SHA; không ghi tài liệu xuống đĩa.
- Thêm duyệt/từ chối, đóng/dọn, chuyển danh mục DEMO và màn quản trị qua KttCore.
- Giữ tín hiệu ChuaRo cả khi ghi dấu lỗi; giao lại không tăng đếm, không thay kết quả đã chốt.

Đã kiểm bằng Core giả (CoreGia). Còn chờ SDK/ngăn thật, nguồn danh tính tin cậy và tích hợp màn vào Core. CLI SDK chuẩn không tiêm nguồn quyền, hai ví dụ bị chặn. Chưa kiểm Core thật hoặc Cloud.


## MASK-2b — 15/11/2026

- Dò ranh giới tên khi Cf thay dấu cách giữa các âm tiết, giữ ánh xạ về nguyên văn và không mở rộng danh sách từ.
- Ghi nhận held-out lead: lọt 4/45, báo nhầm 15/75 (20%); nợ CAO vẫn mở, Cloud tắt cứng. Đã kiểm bằng Core giả (CoreGia).
