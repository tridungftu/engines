**có thể dùng lại hàng việc và biên nhận Core, chưa cần bảng/cột mới**. Tuy nhiên hiện chưa có cửa kiểm–giữ lượt nguyên tử theo **băm nội dung + pháp nhân**; điều kiện chặn trước lát 9 vẫn chưa đạt.

Dưới đây, `C = src/kho_tri_thuc/core`, `S = src/kho_tri_thuc/sdk_core`, `E = engines/e_ocr`. Tham chiếu **@KN4** lấy từ `lat/ocr-kn4` (`e31054a0`); phần còn lại đọc tại worktree (`b206dd00`).

1. **Sổ hạn mức hiện là tệp JSON do `CongOCR` quản lý, không nằm trong CSDL.** Không thấy lớp `SoHanMuc` trong mã khảo sát. Core cấp đường dẫn `tep_so_trang`; mỗi dòng chứa thời điểm, số trang, tùy chọn UUID giữ trang; đọc theo cửa sổ 30 ngày, ghi bằng `fsync`/`replace`, có khóa tệp. Tham chiếu: `E/lib/cong_ocr.py:251`, `:297`, `:314`, `:350`.

   Các con trỏ `_giu_cho`, `_cho_doi_chieu` vẫn ở RAM; UUID trong sổ hiện được sinh riêng, chưa phải mã tương quan gửi ABBYY (`E/lib/cong_ocr.py:264`, `:355`). Khóa theo băm và dấu “chưa rõ” của KN4 cũng chỉ ở RAM: **@KN4 `E/chon_nguon.py:44`, `:241`, `:321`**. Vì vậy trang đã giữ có thể còn trên đĩa nhưng dấu chặn gửi lại bị mất.

2. **Core có nền lưu bền phù hợp, nhưng chưa dùng nguyên trạng được.**

   - `loi.hang_viec` có `CHUA_RO`, lease, thế hệ, chống trùng; `loi.lan_thu_trang_thai` lưu lịch sử và mã đối chiếu: `C/sql/014_viec.sql:57`, `:132`. Khóa duy nhất hiện gồm **pháp nhân + module + khóa**, chưa bảo vệ xuyên module.
   - `loi_tai_lieu.bien_nhan_core` có trạng thái và JSON `ket_qua`; `CHUA_RO` không tự hết hạn: `C/sql/011_tiep_nhan.sql:141`, `:270`. Có thể **thêm dòng biên nhận gắn `viec_id`, băm, mã tương quan, số trang, UUID giữ trang**. Nhưng cửa hiện tại tra theo cả module/người tạo, và `ma_bam` là băm envelope, không phải băm tệp (`:303`, `:308`); cần cửa Core chuyên biệt.
   - `ban_giao_engine` của migration 068 dành cho kết quả đã bàn giao, bắt buộc có `ket_qua_id`; không phù hợp làm dấu trước gửi: `C/sql/068_ket_qua_engine.sql:114`, `:206`.
   - Migration 105 đã có xử lý bước gián đoạn; **107 mới xuất hiện trong kế hoạch, chưa có tệp trong worktree**: `docs/47-core/g3/PHIEU-ENGINE-chuoi.md:57`.

   **Đề xuất:** biên nhận giữ trạng thái lượt ABBYY; hàng việc giữ trạng thái công việc. Khi fallback Mask thành công, việc có thể `XONG` nhưng biên nhận ABBYY vẫn `CHUA_RO`.

3. **Chưa có operation đọc “băm X/pháp nhân P còn lượt chưa rõ”.** Kênh engine hiện chỉ có sáu operation tại `S/kenh_khung.py:66`; `viec.lay` thuộc kênh module và đọc theo ID việc (`S/viec.py:96`).

   Khuyến nghị bổ sung các operation **đề xuất** `engine.ocr_kiem_tra`, `engine.ocr_giu_luot`, `engine.ocr_chot_luot`, gắn với lease. Core tự xác định pháp nhân và kiểm băm từ nguồn đã cấp. Hướng này cần phối hợp phát hành SDK lát 34.

   Có thể dùng carrier `engine.doc_dau_vao` như Mask (`C/kenh_engine.py:247`), giảm thay đổi wire; đổi lại phải thiết kế và kiểm contract/provider OCR riêng. Đây chưa phải cửa có sẵn cho OCR. **Không đổi/ghim SDK trong khảo sát; 1.4.1 vẫn candidate** (`KE-HOACH-G3-GOI.md:355`).

4. **Đối chiếu và chống đua phải do Core quyết định.**

   Core khóa theo `(pháp nhân, băm)`, kiểm và ghi dấu giữ lượt trong **một transaction**, commit trước gửi ABBYY. Chặn cả lượt đang chạy lẫn chưa rõ; chỉ đọc rồi gửi sẽ có khoảng đua. Lease bảo vệ một việc, chưa bảo vệ hai việc khác ID cùng nội dung.

   Đề xuất giai đoạn đầu: **Admin đối chiếu bằng chứng, Core chốt “đã tiêu trang” hoặc yêu cầu hoàn trang**. Chưa thấy tác vụ tự động tương ứng. `viec_xep_lai` chỉ nhận bằng chứng rồi xếp lại, không đối chiếu ABBYY/hoàn hạn mức (`C/sql/014_viec.sql:504`).

   Quét `out` hiện chưa đủ: cầu sinh mã tương quan riêng, Hot Folder sinh mã tệp khác; còn lịch dọn kết quả muộn — **@KN4 `E/cau_noi_abbyy.py:142`, `:215`; `E/lib/cong_ocr.py:172`, `:552`**. Cần gắn bền các mã trước khi tự động hóa. Không thấy kết quả không phải bằng chứng được hoàn trang.

**Chia lát đề xuất**, tên tệp mới cần lead khóa whitelist trước giao:

| Lát | Tệp, gồm test — tối đa 3 |
|---|---|
| Lưu bền/khóa/CAS | Migration mới + `tests/test_ocr_doi_chieu_sql.py` |
| Cửa Core | `C/ocr_doi_chieu.py`, `C/kenh_engine.py`, `tests/test_ocr_doi_chieu_core.py` |
| SDK, phối hợp lát 34 | `S/engine.py`, `S/kenh_khung.py`, `tests/test_ocr_doi_chieu_sdk.py` |
| Nối bộ chọn/sổ trang | `E/chon_nguon.py`, `E/lib/cong_ocr.py`, `E/tests/test_chon_nguon.py` |
| Gắn mã cầu–Hot Folder | `E/cau_noi_abbyy.py`, `E/lib/cong_ocr.py`, `E/tests/test_cau_noi_abbyy.py` |
| Chính sách thử lại | `C/chuoi.py`, `C/dich_vu_engine.py`, `tests/test_ocr_thu_lai.py` |
| Admin API | `C/routes_quan_tri.py`, `C/ung_dung.py`, `tests/test_ocr_doi_chieu_admin.py` |
| Admin UI, cùng đợt API | `C/ui/engine.js`, `C/ui/index.html`, `tests/ocr_doi_chieu.cjs` |

**Migration:** số kế tiếp sau 122 là **123**; đề xuất **124 nếu lead giữ 123 cho Mask chạy thử**. Chỉ thêm hàm/quyền cần thiết và dòng biên nhận; không sửa migration lịch sử.

**Rủi ro/test cần khóa:** crash giữa CSDL–sổ JSON phải phục hồi theo UUID bền và không hoàn hai lần; hai tiến trình, khác module/người tạo, cùng băm; khác pháp nhân; mất phản hồi sau commit; lease hết hạn; fallback thành công nhưng ABBYY chưa rõ; kết quả đến muộn. Chuỗi hiện suy tác động ngoài từ `ra_cloud`, có thể coi OCR nội bộ là an toàn để thử lại — cần sửa trước nối thật (`C/chuoi.py:271`). PG đồng thời do lead kiểm.

**Tệp đổi: 0; không tạo tệp, không commit; Git sạch đầu/cuối.** Test trước/sau cùng **54 ca Core thuần/mock: 54/0/0/0** theo thứ tự **ok/fail/error/skip**; không thêm lỗi trong tập đã chạy. Không chạy luồng OCR tạo tệp, ABBYY thật hoặc PostgreSQL.

**Lead cần chốt:** phạm vi chặn xuyên module trong cùng pháp nhân; operation riêng hay carrier; số migration; bằng chứng được phép hoàn trang và whitelist từng lát.