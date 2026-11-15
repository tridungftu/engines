# Bàn giao MASK-B1 — 15/11/2026

Kết luận: **Đạt phạm vi cổng nội bộ MASK-B1; chưa đạt cổng nghiệm thu chung CLI SDK do thiếu nguồn quyền (0/2).** Chưa nối hoặc công bố năng lực tệp.

Đã làm: đúng ba tệp mã `doc_tep.py`, `zip_an_toan.py`, `xml_an_toan.py`. ZIP tiền kiểm EOCD trước danh mục, kiểm local/central/interval, header và tên, giải nén bounded đến EOF thật/CRC/bytes khai báo và thực. XML Expat stdlib chặn DTD/entity/XXE/PI, giữ khai báo XML hợp lệ, kiểm namespace/encoding, depth/node/ô/sheet/nội dung tổng. Kiểm part/content types/root/graph, part mồ côi và vùng cấm theo §7.2; chỉ trả đối tượng RAM khi cả gói đạt. Không ghi đĩa/mạng/log, không trả một phần; giữ nguyên hủy/ChuaRo. Có helper trần chiều ra/JSON cho các lát sau, chưa có writer/upload.

Kết quả kiểm: `kho_tri_thuc_sdk.thu` → **0/2 ĐẠT, mã 1**, cả hai lỗi “Chưa xác minh được phiên và quyền xử lý yêu cầu.”; pytest → **1248 passed, 4 xfailed, 190 subtests passed, 0 skipped, 99,42 giây, mã 0**. Riêng B1 **276 passed, 2,12 giây**; kiểm độc lập **ĐẠT, mã 0**; adapter DEMO **2/2 ĐẠT, mã 0**. Bốn xfail strict held-out lớp quy tắc giữ nguyên. [Lệnh và kết quả thật](KET-QUA-KIEM-MASK-B1.txt).

Thời gian thực tế: **13:50:00–14:37:27 ngày 15/11/2026 (UTC+07), 0.79 giờ** (bắt đầu theo handoff, kết thúc tại mốc chốt kết quả). Phiếu **6–8 giờ ƯỚC TÍNH**, độ khó `kho`.

Lệch khỏi phiếu / quyết định tạm đã dùng: không mở rộng phạm vi hoặc thêm tệp mã. Closure thực `zip.py` → `hoa_don_xml.py`; DOCX → `cau_truc.py` chỉ dùng để đối chiếu namespace/hai lỗi, không kéo reader/DTO. Chép chọn lọc và chuyển có sửa; nguồn, symbol, quyền, SHA bytes/LF trước–sau tại [NGUON.md](../goi/e_mask/NGUON.md). Không dùng API riêng/cảnh báo của zipfile; dùng `struct`/`zlib` và Expat stdlib. Profile mới từ chối data descriptor, ZIP extra/comment, XML comment, theme/phần chưa kiểm. Tổng ký tự vào được đếm bảo thủ cả text/tail/attribute và shared string từng ô; reader B2/B3 vẫn phải kiểm ngữ nghĩa/map, chưa coi đây là tệp đã che.

Cần Core / Chờ Anh mới phát sinh: cụ thể hóa **C-MB-03** ở VIEC.md về stream/trần download/upload trước cấp phát, 413, hủy/lease, budget RAM/thời gian/job/concurrency; B10 đo trên máy đích trước vận hành. Không có câu chờ Anh mới. Không sửa Core/SDK/nguồn mẫu/ngăn chung/manifest/handler, không thêm dependency/PDF/Office COM. PR **chờ lead mở**; không commit/push.

**Đã kiểm bằng Core giả (CoreGia) gói văn bản hiện có.** B1 kiểm cổng tệp trực tiếp trong RAM, chưa kiểm Core thật, Word/Excel/Local thật hoặc Linux thực tế, chưa đo peak RAM/CPU từng giai đoạn ở biên. Cloud giữ tắt; nợ held-out lớp quy tắc và các phụ thuộc hai lớp chưa được đóng bằng phép thử B1.

Các trần đã kiểm đúng/vượt tại cửa tương ứng: 1 MiB container vào/ra; 2 MiB/phần, 8 MiB giải nén tổng; 256 phần; ratio 200:1 cả phần nhỏ; depth 64; 100.000 node tổng nhiều XML/cả gói; 50 sheet, 20.000 ô nhiều sheet; 500.000 code point gồm metadata; 2.000.000 code point ra; bộ đếm 8 MiB UTF-8; JSON 256/64/32 KiB UTF-8. Với Unicode hợp lệ, 2 triệu code point chỉ tới 8.000.000 byte (<8 MiB), nên trần byte được kiểm riêng, không giả ca end-to-end vượt byte mà vẫn đúng trần ký tự. Các test cửa hạ tầng không thay benchmark cả chuỗi B + Local của B10.
