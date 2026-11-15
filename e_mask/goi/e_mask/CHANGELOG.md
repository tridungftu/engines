## Chưa phát hành — 15/11/2026, MASK-B4 writer ZIP/XML nội bộ

- Thêm `ghi_zip.py`, `va_xml.py`, mở kiểm record trong `zip_an_toan.py`; đúng ba runtime, chỉ stdlib/SDK và RAM. Không đổi manifest/năng lực/handler hoặc bật Cloud; B7/B9 mới nối hai lớp và phát hành.
- Edit script ghim SHA ZIP/vùng/part/span; writer đọc lại B1+B2/B3, chặn span Unicode/byte chồng hoặc sai băm/map/CRC/size/offset. Kiểm tổng lệnh trước cấp phát map; không tin cây XML mutable của caller.
- Chép nguyên local record, payload nén và descriptor part bất biến; central chỉ sửa offset cần thiết. Part sửa giữ method/flags/thứ tự, cập nhật CRC/size/local/descriptor; không nén lại part khác hoặc đổi compression để tránh ratio. Không edit/no-op thì toàn ZIP bằng gốc.
- Patch byte text/attribute giữ markup/namespace/format ngoài span, không serialize toàn XML. UTF-8/UTF-16, entity/NFD/CR/CDATA, ST_Xstring/control của ô Excel và metadata XML thường có kiểm nghĩa sau đọc lại; shared string patch một lần, kiểm đủ mọi nơi dùng và mục chưa dùng. Giữ bytes ô số/ngày/style/merge.
- Kiểm trước/từng lần encode/ghi/đóng ZIP: 1 MiB output, 2 MiB/part, 8 MiB tổng, ratio 200 cùng toàn bộ trần B1/readers. Đọc lại output hiện còn trần bảo thủ 500.000 ký tự B1/B2/B3, có thể từ chối trước trần văn bản ra 2 triệu; giữ chặn này và ghi rõ để lead lập lát reader nếu cần mở rộng.
- DEMO có oracle SHA bytes giải nén/payload nén/local record, container 1 MiB/+1, part 2 MiB/tổng 8 MiB tại bước chuẩn bị patch, map/ZIP giả, XML hỏng dù CRC đúng, hủy/ChuaRo/không I/O hoặc log. Nguồn/quyền/SHA bytes+LF trước/sau tại NGUON; kết quả cuối ở `e_mask/docs/BAO-CAO-MASK-B4.md`.
- Kết quả cuối: riêng B4 **270 passed**; toàn bộ **2175 passed, 2 failed deadline cũ MASK-2c-4, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped**. Chưa đạt kiểm chung; CLI 0/2 thiếu quyền, DEMO có quyền 2/2 và kiểm độc lập đạt. Đã kiểm bằng Core giả (CoreGia); chưa Office/Core/Local thật. PR chờ lead mở, không commit/push.

## Chưa phát hành — 15/11/2026, gộp MASK-B2 + MASK-B3

- Giữ trọn reader Word/Excel và hai quy ước offset ZIP khi có data descriptor; cổng ZIP chung B2 áp cho XLSX, cổng B3 dùng chung kiểm tên 256.
- Thêm 18 ca hồi quy XLSX kiểu Office qua cả hai cổng, kiểm descriptor có/không chữ ký và chặn CRC/size sai, tên vượt 256. Giữ toàn bộ test B1/B2/B3; nguồn/SHA LF hiện hành ghi tại NGUON.md.
- Đã kiểm bằng Core giả (CoreGia); chưa Office/Core/Local thật. Cloud giữ tắt, không đổi API/SDK/dependency hoặc commit/hoàn tất merge.
- Kiểm sau gộp: 1907 passed, 4 xfailed cũ, 190 subtests passed, 0 skipped; kiểm độc lập đạt, DEMO có quyền 2/2. CLI SDK chuẩn 0/2 thiếu nguồn quyền như trước; lead cần stage do sandbox chặn Git index.

# Thay đổi

## Chưa phát hành — 15/11/2026, MASK-B2 reader Word nội bộ

- Đúng ba tệp runtime: `doc_word.py`, `xml_word.py`, khối B2 riêng trong `doc_tep.py`. Chép chọn lọc walker DC/TX, ghi quyền/symbol/SHA bytes và LF trước–sau; không import chéo engine, không sửa nguồn mẫu/Core/SDK, không thêm dependency/COM/PDF hoặc handler/năng lực tệp.
- Đọc thân/bảng/run/đầu-chân/notes/chữ ẩn, core/app/custom thuộc profile và text/attribute trong styles/numbering/theme. Mọi scalar custom có map/tổng quét, gồm cả số/bool/ngày có thể mang mã định danh. Mỗi vùng giữ biên riêng, text Unicode gốc/SHA riêng, map node/run/style/ẩn/attribute và byte từng code point. Giữ NFD/Cf; entity/CR/CDATA/UTF-8/UTF-16/ngoài BMP có map, không ghép qua đoạn/ô/story. Giữ text cả ô gộp nối và note chưa có tham chiếu; kiểm note lặp/tham chiếu sai.
- Kiểm cấu trúc/giá trị trước coi thuộc tính bất biến: ID style/font chỉ tập hằng có kiểm; tên style/theme/property được quét có map. Comments/revision/author markup, field/textbox/content control/extension/media/nhúng/phần lạ từ chối cả gói với câu cố định. Dữ liệu việc chỉ RAM, dọn bảng/buffer trong finally; chưa chạy hai lớp MASK-2b + Local trên tệp.
- Cổng chung thêm cờ ZIP bit 1–2 của DEFLATE và descriptor bit 3 có/không chữ ký, kiểm CRC/size/local-central trước cho B1 kiểm lại payload. Giữ bytes/offset gốc; `le_cuoi` bao descriptor, payload dài `so_byte_nen`. Thêm theme Word có kiểm và app properties chuẩn; tên part/target dài hơn 256 bị chặn trong wrapper B2 để giữ giới hạn ba tệp. Reader/theme/calcChain Excel thuộc B3, không sửa `doc_excel.py`/`xml_excel.py`.
- 155 test B2 mới; riêng B1+B2 **431 passed**. Toàn bộ **1540 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped**; kiểm độc lập đạt, adapter DEMO 2/2. CLI SDK chuẩn 0/2 thiếu nguồn quyền như trước. Đã kiểm bằng Core giả (CoreGia) gói văn bản hiện có; reader B2 kiểm trực tiếp RAM, chưa Office/Core/Local thật hoặc Linux thực tế. Cloud tắt; PR chờ lead mở, không commit/push.
## Chưa phát hành — 15/11/2026, MASK-B3 reader XLSX nội bộ

- Thêm `doc_excel.py`, `xml_excel.py` và một khối Excel riêng trong `doc_tep.py`; giữ nguyên AST B1, manifest và handler. Chỉ SDK/stdlib, không import engine khác, nguồn cũ hoặc thêm dependency; Cloud tắt.
- Đọc đủ shared/inline/rich text mọi ô, gồm hàng/cột ẩn, mục shared chưa dùng, tên sheet và core/app/custom properties thuộc profile. Map Unicode hai chiều về run/text/attribute/bytes UTF-8/UTF-16, entity/ST_Xstring/CR/NFD/Cf; không nối hai ô hoặc cắt 32767.
- Giữ raw value/type/style/XML ô số, boolean và serial ngày, cả style kế thừa hàng/cột và epoch; kiểm numFmt/font/style/merge và miền giá trị attribute. Tên sheet cần thay thì chặn; sheet ẩn, formula/cache/definedNames, liên kết ngoài, bình luận/chart/drawing/nhúng/macro/part lạ hoặc mồ côi đều từ chối cả gói.
- Thêm profile có kiểm cho theme và ZIP Office cờ nén/data descriptor; kiểm CRC/size, giữ bytes/offset gốc cho B4. CalcChain chỉ nhận rỗng; phần chứa tham chiếu công thức vẫn chặn. Nguồn/quyền/SHA bytes và LF trước–sau tại NGUON.md.
- Test DEMO gold, đối kháng và đúng/vượt 20.000 ô, 50 sheet, 100.000 node; tiền 1000000 VND/ngày 2026-10-30 theo raw value và style, hủy/ChuaRo/không I/O/không output dở. Reader chỉ nội bộ cho B6/B7, chưa Excel/Local thật hoặc năng lực tệp. Kết quả đầy đủ ghi tại `e_mask/docs/BAO-CAO-MASK-B3.md`.
- 299 test B3; toàn bộ 1684 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped. DEMO có quyền 2/2, kiểm độc lập và diff đạt; CLI SDK chuẩn 0/2 vì thiếu nguồn quyền. Đã kiểm bằng Core giả (CoreGia) gói văn bản hiện có, reader chỉ kiểm trực tiếp RAM. CDATA trong part cần map bị chặn vì chưa có profile patch chứng minh.
## 15/11/2026 — MASK-2c-4 sửa theo kiểm lead (không đổi runtime 1.2.0)

- Bổ sung 28 ca DEMO mới ngoài gói: 18 người không dấu/Hoa đầu chữ/IN HOA/danh xưng/mép/overlap, 5 tổ chức và 5 địa chỉ không có DEMO trong span, đủ năm khung. Tổng 190 ca/124 gold span, SHA mới; **ỨNG VIÊN, chờ lead đóng băng**.
- Công cụ tách mẫu số chặn trước AI/AI-9 thực sự hoàn tất đoạn/chưa có đoạn xong và tổng; lọt/báo nhầm riêng, không nhận 0 lọt ở ca bị chặn trước AI là thành tích AI. Đo che vượt gold cả ở ca có định danh bằng số span/ký tự.
- Thêm --timeout mặc định 120 giây × số đoạn và trần cấu hình; CLI cách ly ca bằng process để timeout cứng, giữ kết quả từng phần và số đoạn xong; ngoại lệ xuất báo cáo trước thoát. `.cmd` ASCII/CRLF; đích báo cáo ngoài repo hoặc thư mục riêng chỉ định rõ, không ghi đè.
- Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; chưa đo Local/Core thật. Giữ nguyên runtime, API, dependency và trạng thái Cloud tắt.

## 15/11/2026 — MASK-2c-4, công cụ ngoài gói (runtime giữ 1.2.0)

- Thêm công cụ đo DEMO mặc định khô/không mạng và `.cmd` ASCII; adapter CoreGia ngoài gói điều phối chuẩn bị → AI-9 → hậu kiểm đủ đoạn. Không sửa runtime engine, Core/SDK, dependency hoặc mở Cloud.
- Bộ gold ứng viên mới: 45 tên/45 ngữ cảnh, 75 câu thường, 15 tổ chức, 15 địa chỉ và 12 biến thể riêng; có băm, tách development/bốn ca lead cũ. **Chưa lead đóng băng/gold độc lập; chưa là nghiệm thu held-out độc lập.**
- Chấm hai chế độ trên cùng bộ; tách chặn nghiệp vụ/lỗi kỹ thuật/ChuaRo khỏi lọt và che đủ; báo nhầm bằng hợp che thừa/chặn trên toàn mẫu, kèm mẫu hợp lệ, số span/đoạn và p50/p95. Báo cáo tùy chọn không chứa nội dung gốc/URL/path/mã mở che, không lưu runtime report trong engine.
- Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả. **CHƯA ĐO Local thật**; AI báo thiếu một phần tên vẫn có thể lọt. Chờ Anh chạy `.cmd`, lead review gold/bằng chứng và Core thật; nợ CAO giữ mở, Cloud giữ tắt.

## Chưa phát hành — 15/11/2026, MASK-B1 cổng ZIP/XML nội bộ

- Thêm đúng `doc_tep.py`, `zip_an_toan.py`, `xml_an_toan.py`; chưa gắn handler/năng lực tệp, giữ manifest 1.1.0. Chỉ stdlib/SDK, RAM, Cloud tắt.
- Áp trần thử nghiệm của phiếu §7.3: ZIP 1/8/2 MiB, 256 phần, ratio 200:1; XML depth 64/100.000 node tổng/50 sheet/20.000 ô/500.000 code point; helper chiều ra và JSON có trần riêng. Chặn tên/header/extra/comment, ZIP64/overlap/EOF/CRC/size giả, XXE/PI, quan hệ ngoài và part mồ côi/lạ; lỗi cố định, không trả một phần, giữ hủy.
- Lần closure mẫu, chép chọn lọc có nguồn/quyền/symbol/SHA bytes và LF trước–sau trong NGUON.md; không sửa nguồn mẫu hoặc thêm dependency. Profile và reader ngữ nghĩa/map các lát B2/B3 được phân biệt rõ.
- 276 test DEMO mới; toàn bộ 1248 passed, 4 xfailed giữ nguyên, 190 subtests passed, 0 skipped. Kiểm độc lập đạt; adapter DEMO 2/2. CLI SDK chuẩn 0/2 do thiếu quyền như trước. Đã kiểm bằng Core giả (CoreGia) gói hiện có; chưa kiểm năng lực tệp nối Core/Office/Local thật.
## 1.2.0 — 15/11/2026, MASK-2c-3 hậu kiểm Local và che bổ sung

- Thêm `mask.hau_kiem_ai_cuc_bo@1`: một đầu vào `tra_loi_ai`, đầu ra cố định `van_ban_da_che`. Chỉ đọc snapshot/tập phản hồi qua tham chiếu có quyền của Core; thiếu port chứng thực nguồn AI-9/Local, hoàn tất hoặc đủ đoạn thì từ chối.
- Kiểm bytes/SHA snapshot, map, toàn yêu cầu AI JSON chuẩn, prompt/khuôn/profile và chuyển tiếp nguyên vẹn. Mảng rỗng không được thay chứng cứ; kiểm lại schema/span/trích dẫn từng vị trí, cả NFD/Cf/selector. Một đoạn Cloud, sai quyền, phản hồi cắt, overlap mâu thuẫn hoặc prefix che một phần đều chặn.
- Giữ alias lớp 1; che thêm thực thể chắc theo vị trí phải → trái, gom đúng span và giữ các lần xuất hiện khác. Dùng nguyên kho alias/hàng chờ/CAS/chống lặp; hậu kiểm cũ và kiểm tiền/ngày toàn văn phải đạt trước chốt. Vượt 100 lệnh từ chối toàn bộ, không chia lô.
- Core ghi chứng cứ nguồn bước 3 và băm kết quả cuối trước trả. Hủy/mất lease/quyền, hết hạn hoặc mất ACK không phát hành; nguồn đã nhận chưa trả giữ `ChuaRo`. Không mở che, không gọi engine/model, không lưu bền tại máy engine.

Đã kiểm bằng Core giả (CoreGia): 1109 passed, 4 xfailed giữ nguyên, 190 subtests passed; 0 skipped. DEMO có quyền 2/2, kiểm độc lập đạt; CLI chuẩn 0/2 thiếu quyền. Chưa kiểm Core/model thật hoặc Linux thực tế, chưa đo held-out hai lớp. Cloud vẫn tắt; đúng năm tệp mã, không dependency/Core/SDK/schema chung/nguồn cũ.

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
