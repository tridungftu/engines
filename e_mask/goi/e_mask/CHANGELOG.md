## Chưa phát hành — 15/11/2026, MASK-R5 (tiếp lúc 23:50)

- Phân loại đủ 216 test: 207 ca an toàn dùng RAM R4 và ngăn SDK 2.2.0; 9 ca lưu snapshot đổi sang kiểm không lưu và lỗi rõ khi mất RAM. Giữ bốn xfailed cũ; fixture/công cụ snapshot cũ được lưu nguyên bản ngoài gói ở LUU-TRU.
- Theo chỉ dẫn tiếp lát, giữ hình dạng ho_so/bam_ho_so cho AI-9 bằng metadata ram-… không có tệp tương ứng. Validator chỉ nhận metadata RAM cố định và hậu kiểm đối chiếu đúng phiên/băm; không ghi/đọc hồ sơ Core. Không sửa e_hoi_ai hoặc schema/contract chung. Cần phối hợp AI-9: bỏ yêu cầu snapshot Core (AI-13).
- Giữ nguồn Local/đủ đoạn/span/Unicode/tiền-ngày/retry/quyền/TTL và Cloud tắt. Thiếu tài nguyên trả đúng MASK_THIEU_TAI_NGUYEN, không phát hành. Chay.py/R6 và các cửa Core còn thiếu vẫn fail-closed; kết quả thật ở VIEC/báo cáo R5, PR chờ lead mở. Đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật.

## Chưa phát hành — 15/11/2026, MASK-R5 (lượt đầu 22:17, lịch sử)

- Chuyển hồ sơ MASK-2c (gốc, bản quy tắc, edit map/Unicode, kế hoạch, phiên bản, cấu hình đã ghim và phản hồi Local) sang handle `KhoAnhXaRAM` của R4. Đóng cửa lưu/đọc snapshot `KhoHoSoAI`; chuẩn bị và hậu kiểm không đọc/ghi chỉ mục hoặc hồ sơ Core. Kho nhận diện chỉ tìm chính xác qua R2, không phục hồi danh mục bản rõ hoặc dùng kho RAM lịch sử để chốt.
- Chuyển tiếp nội bộ chỉ có mã RAM opaque, băm, chỉ số/biên đoạn và nhãn profile an toàn. Không `ho_so`/`tap_phan_hoi` tham chiếu tệp, không gốc/map. Core chọn từng đoạn qua port, Mask trả đúng một `yeu_cau_ai`; hậu kiểm nhận tập phản hồi Local tạm qua cửa tin cậy rồi kiểm nguồn và băm từng yêu cầu dựng lại từ RAM. Không gọi Hỏi AI/model từ Mask, không Cloud.
- Giữ kiểm đủ đoạn, Unicode NFD/Cf/code point, overlap/span/trích dẫn, alias lớp 1, tiền/ngày và hậu kiểm toàn văn. Kiểm đầu vào đã ghim và bytes tệp cùng tham chiếu bị đổi. Cùng alias khác nguyên văn chặn; alias → nguyên văn đúng tại span chỉ ở RAM. Lookup nhường việc/handle SDK khi chờ, giữ budget; tên mới thiếu bảo đảm C-P4-03 bị chặn trước ghi/phát hành.
- R4 dọn khi mất RAM, lỗi, hủy, TTL hoặc sự kiện kết thúc; replay hậu kiểm bị chặn. Chỉ `ChuaRo` lúc còn chờ Local/Core được giữ RAM trong hạn tuyệt đối. Sau chốt không giữ bản rõ/kết quả để tái chạy; Core quản ACK và cách ly kết quả tới chốt cuối.
- **Chưa nối runtime thật:** constructor yêu cầu truyền kho R4 rõ ràng; `chay.py` ngoài phạm vi R5 chưa truyền kho vào hai handler (điểm nối R6). AI-9 hiện bắt buộc profile tham chiếu snapshot; cần C-P4-04 thay phụ thuộc đó, không tạo tham chiếu giả hoặc sửa contract/schema chung. Adapter tích hợp chỉ nằm trong tests; các test snapshot cũ giữ nguyên và đang lỗi, không nhận full suite xanh. Kết quả thật và C-P4-01/02/04 tại VIEC/báo cáo R5; PR: chờ lead mở.
## Chưa phát hành — 15/11/2026, MASK-R7

- Admin chỉ liệt kê ID/alias/nhóm/trạng thái/số gặp; UI dùng `KttCore.engine("e_mask")`, không tên hay lọc tên một phần. Chỉ nhận biên nhận ID/phiên bản opaque từ cửa Xem dữ liệu Core; không callback/export bản rõ, không mạng ngoài/HTML chưa lọc/log.
- Duyệt/từ chối qua port quyền tin cậy kiểm cả quyền xem và duyệt, phiên/vùng/ID/phiên bản và vé một lần, giữ quyền trong lô CAS. Thiếu cửa hoặc phiên bản đổi thì giữ chờ, không tự khai đã xem hoặc ghi ngăn trực tiếp từ UI. C-P4-06 chưa có trong SDK; giao thức adapter chỉ kiểm ngoài gói, chưa đăng ký/nối thao tác Admin Core thật.
- Dùng primitive R2 sửa trạng thái tại cùng ID; chỉ thêm alias metadata duy nhất theo vùng, không sao tên sang bảng khác, không ghi null/cờ đè bí mật, không xóa. Junsky không trùng tiền tố MASK; alias tự sinh đúng nhóm. Không chạm kho RAM R4 của chuỗi đang chạy; mất ACK trả ChuaRo, không tự duyệt lại.
- Logic Admin RAM lịch sử chuyển sang fixture ngoài gói để giữ hồi quy cũ; runtime không còn nhập danh mục RAM/đóng/dọn theo thiết kế cũ. Công cụ `cong-cu/chuyen_danh_muc_demo.py` lịch sử chưa chuyển trong closure R7, không dùng để migration dữ liệu thật. Core/lead quản migration cũ theo C-P4-06.
- Đã kiểm bằng Core giả (CoreGia) và KttCore giả; chưa UI Core thật. Chỉ hai runtime theo phiếu, kèm test/tài liệu và kiểm kê bytes LF tự sinh; không sửa Core/SDK/dependency, không commit/push. Kết quả thật và thời gian ghi ở VIEC/báo cáo R7; PR: chờ lead mở.

## Chưa phát hành — 15/11/2026, MASK-R3 kết thúc khảo sát ứng viên

- Thêm lõi khảo sát RAM `tra_cuu_dinh_danh.py` và đầu dò trong `che_van_ban.py`: ứng viên từ detector/quy tắc/trường/danh sách của đầu vào hiện tại; gọi `tim_ung_vien` R2 bằng đúng giá trị, nhận metadata/null+cờ. Không liệt kê ngăn/dựng matcher danh mục, không fuzzy/prefix hoặc thử mọi chuỗi con trong nhánh mới. Không giải mã, ghi ngăn, cấp alias tạm hoặc phát hành từ đầu dò.
- Ghép alias với nguyên văn tại span gốc, giữ NFD/Cf/hoa-thường/khoảng trắng. Cùng alias nhưng nguyên văn khác nhau thì chặn toàn lượt. Dò lặp cùng giá trị chuẩn hóa chỉ tính một ứng viên; chia sẻ lượt dò/budget giữa quy tắc và điểm nối Local trong `hau_kiem_ai.py`.
- Trần khảo sát 2.000 giá trị phân biệt, 20.000 vị trí, 8 triệu ký tự qua các lượt định vị; kiểm hạn tuyệt đối/hủy trước và sau RPC. Vượt trần/hạn không trả phần đã làm; dọn tham chiếu khi lỗi/kết thúc lượt. Đây là budget đề xuất, deadline hợp tác không thay cơ chế cưỡng chế Core. Giữ kiểm tiền/ngày và nguồn/span/đủ đoạn Local.
- **Chưa chứng minh chất lượng/chi phí, kết thúc khảo sát bằng giới hạn.** 16 ca gốc: 1 che đủ không chặn, 7 lọt trong bản khảo sát, 8 chặn; 18 câu thường: 14 giữ nguyên, 4 chặn, 0 che thừa, báo nhầm theo §6 = 4/18 (22,22%). Biến thể và số đo riêng ở VIEC. Không lấy 0 phát hành làm 0 lọt; chưa đo Local thật/held-out có người soạn độc lập.
- Cửa SDK nhận diện R2 trong che/hậu kiểm bị chặn cố định `MASK_R3_CHUA_CHUNG_MINH`, không rơi về matcher/snapshot RAM lịch sử. Nhánh RAM lịch sử trong `che_van_ban.py` giữ nguyên để hồi quy tới R5/R6; chưa tuyên bố xóa matcher khỏi toàn gói hoặc nối P4 vận hành. Hậu kiểm lịch sử bỏ đọc danh mục, chỉ dùng vùng gốc đã có trong RAM. R4/R5/R6 và C-P4-03/04/05 còn mở; Cloud tắt.
- Đúng ba runtime R3; không sửa handler/vòng đời của R4, Core/SDK hoặc dependency. Kiểm kê bytes/SHA tự sinh lại theo gói SDK. Đã kiểm bằng Core giả (CoreGia), chỉ DEMO; PR: chờ lead mở. Số kiểm thật trong VIEC và báo cáo R3.

## Chưa phát hành — 15/11/2026, MASK-R4

- Thêm kho `KhoAnhXaRAM` một chuỗi theo mã Core cấp, kiểm quyền module/người/tài liệu/pháp nhân/DEMO, ghim instance và phiên RAM. Một bước sở hữu; mở tiêu thụ một lần, không phục hồi khi restart/đổi instance hoặc cache bản rõ sau mở.
- TTL chụp đầu chuỗi từ cấu hình SDK (600 giây, số nguyên 60–900), đồng hồ monotonic, lấy deadline Core nếu sớm hơn, không trượt khi retry/đổi cấu hình. Đầu vào cùng lượt đổi thì từ chối. Trả handler sau bước che nhưng giữ RAM tới bước tiếp theo; chuỗi khác không đẩy map đang sống ra.
- Timer daemon dọn cả khi chờ AI; `finally` dọn khi mở/hủy/lỗi/kết thúc/mất quyền/lease. Đồng bộ timer và tín hiệu kết thúc với khởi tạo/mở/chốt kết quả, chặn phát hành nếu RAM đã mất; lỗi cố định `MASK_ANH_XA_KHONG_CON` yêu cầu chạy lại cả chuỗi. Không ghi map/gốc/bytes vào ngăn/tệp/tạm/hồ sơ/log/stderr/chuyen_tiep.
- Cửa ghim/vòng đời là protocol nội bộ còn thiếu ở SDK/Core (C-P4-01/02); handler từ chối khi thiếu, không suy quyền từ dữ liệu việc hoặc `so_viec_dong_thoi=1`. Adapter CoreGia chỉ ngoài gói. Chuyển nghiệp vụ cũ khỏi kho/snapshot và nối mở che mới thuộc R2/R5/R6/B7, chưa thực hiện trong R4.
- Đã kiểm bằng Core giả (CoreGia); chưa Core/Local/Office/Linux thật. Kết quả kiểm và giới hạn kiểm kê/CLI ghi tại `e_mask/docs/VIEC.md` và `e_mask/docs/BAO-CAO-MASK-R4.md`. PR: chờ lead mở.
## Chưa phát hành — 15/11/2026, MASK-R2 adapter nhận diện bí mật

- Thêm `KhoNganBiMat` dùng đúng `viec.ngan.doc/tim/lo` SDK 2.2.0. Ứng viên chỉ tìm bằng giá trị chính xác ở cột bí mật, cùng vùng và phiên bản chuẩn hóa; trả ID/alias/metadata/null+cờ, không băm tên công khai hoặc nạp danh mục bản rõ. Số gặp đọc theo chuỗi thập phân của SDK.
- `KhoDinhDanh.mo_kho_nhan_dien` và `KhoNhanDienQuaCore` kiểm nguồn quyền trước/sau truy cập. Dùng lại alias chính thức qua nhiều việc; không giữ ứng viên/map/alias tạm hoặc snapshot. Mở che từ kho bị chặn; ánh xạ thuộc R4/R6.
- Bản vá metadata bỏ hoàn toàn khóa bí mật và cờ mã hóa. Primitive cho R7 duyệt trên cùng ID bằng CAS, tạo alias chính thức trong cùng lô với ràng buộc duy nhất; từ chối bằng trạng thái, không xóa. Primitive nội bộ chưa thay cửa xác minh biên nhận Admin C-P4-06.
- Lô metadata tối đa 100 lệnh; vượt từ chối trước khi gửi, không chia giả nguyên tử. SDK gửi lại cùng khóa lô; mất mọi ACK chuyển `ChuaRo`, khóa đối tượng ghi chưa rõ, không tự thử lô mới/cấp alias hoặc tăng đếm lại. Giao lại dùng ID và phiên bản cũ chịu CAS.
- **C-P4-03 còn mở:** R1 chưa có duy nhất/`lay_hoac_tao` theo bí mật + vùng + phiên bản chuẩn hóa hoặc dấu gặp chống lặp xuyên lần giao việc. Tạo tên mới và tăng số gặp bị chặn `MASK_KHO_CAN_CORE`; không thêm cờ cấu hình để bỏ chặn. Hạn mức dò/không log ứng viên và bảo đảm Core thật vẫn cần xác nhận.
- Đúng bốn tệp runtime của R2; phần RAM lịch sử giữ nguyên hành vi hồi quy, chặn nhận `NganEngine` tại mọi cửa snapshot/dấu/liệt kê cũ. R3/R4/R5 chuyển consumer/handler theo phiếu, không sửa `chay.py` của R4. Kiểm kê gói được sinh lại theo bytes thực tế. Test và số kiểm thật ở VIEC, đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật. Cloud tắt; PR chờ lead mở, không commit/push.

## 1.4.0 — 15/11/2026, MASK-R1 (chưa phát hành)

- Khai kho nhận diện `dinh_danh` và kho bí danh chính thức/lịch sử `bi_danh` theo SDK 2.2.0; khóa ID opaque, không trường JSON hoặc quan hệ yêu cầu–alias–tên. Hai cột `gia_tri_goc`/`gia_tri_chuan` đều bí mật; không giải mã hoặc tự giữ khóa/băm tên.
- Thêm migration trong schema riêng và kiểm kê bytes/SHA-256 mọi tệp gói trừ chính kiểm kê, theo mẫu SDK. Chỉ bảo đảm duy nhất ID/alias; duy nhất theo bí mật còn **C-P4-03**, chưa đủ nghiệm thu.
- Khai `thoi_han_anh_xa_giay` mặc định 600, số nguyên 60–900 qua cấu hình SDK; thêm cửa lấy `viec.ngan` không tạo ngăn dự phòng. Chưa triển khai map, timer hay nối adapter/nghiệp vụ R2–R7.
- Giữ nguyên bản khai cũ ở LUU-TRU. Giữ `cuc_bo`, một việc đồng thời và khoảng SDK `>=2.2.0 <3.0.0`. Chỉ DEMO, không Cloud.
- Bổ sung tích hợp theo ngoại lệ lead 15/11: bỏ guard chỉ cho cấu hình rỗng trong `chay.py::_loi_cong`, dùng snapshot đã kiểm schema/điền default của SDK. Giữ nguyên thứ tự kiểm ngữ cảnh/port và mã lỗi nghiệp vụ trong handler, cùng kho RAM cũ tới R2/R4; không đổi kiểm an toàn hoặc nối kho R1 vào vận hành. Schema đã có default cho mọi trường mới (TTL 600, số nguyên 60–900), không cần sửa schema.
- Test S22 cập nhật khai báo ngăn/migration R1 và snapshot TTL, kiểm handler thật qua CoreGia với cấu hình rỗng và TTL 60/600/900; giữ kiểm từ chối cấu hình sai ở R1 và các ca an toàn cũ. Đã kiểm bằng Core giả (CoreGia); kết quả thật, giới hạn CLI và thời gian ở `e_mask/docs/VIEC.md`, mục MASK-R1.

## 1.3.0 — 15/11/2026, MASK-S22 (chưa phát hành)

- Nâng SDK 2.2.0, khai schema cấu hình rỗng đúng hiện trạng; handler đọc `viec.cau_hinh`. Lưu trữ nguyên byte bản khai 2.1 và bộ đọc cấu hình tạm; bỏ bảng cấu hình khỏi kho RAM.
- Theo ngoại lệ Lead/CĐ-36, giữ cổng kho bí danh RAM; tách khỏi ngăn SDK, không khai bảng/migration, không thêm đường giải mã. MASK-P3 xử lý thiết kế nghiệp vụ sau.
- Adapter công cụ Local dùng cấu hình và ngăn CoreGia 2.2.0 cho Hỏi AI AI-11/AI-12; hai test deadline dùng checkpoint xác định, không đo tải máy. Giữ các ca hành vi/an toàn cũ; chỉ bỏ so băm mẫu tạm.
- Đã kiểm bằng Core giả (CoreGia). CLI chuẩn vẫn bị chặn ở cả hai ví dụ do thiếu cửa cấp quyền/mã yêu cầu tin cậy; Cần Core, chưa đạt điều kiện nghiệm thu chung. Pytest lượt chốt: 2179 passed, một subtest hiệu năng cũ failed, 4 xfailed giữ nguyên, 189 subtests passed, 0 skipped; hai ca deadline đã qua. Kiểm độc lập đạt. Kết quả lệnh và thời gian cuối tại `e_mask/docs/BAO-CAO-MASK-S22.md`.

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
