# Bộ XML DEMO HD-3 — Công ty DEMO Ánh Dương

Tất cả dữ liệu là giả. “Công ty DEMO Ánh Dương” là nhãn mô tả fixture, không phải trường `NBan/Ten` hoặc `NMua/Ten`: hai đường này ngoài allowlist. Không thêm `Ten` để tạo ca thành công giả.

| Fixture | Đáp án nguồn độc lập |
|---|---|
| `hoa-don-DEMO.xml` | Số `0000123`, ngày `2026-10-30`; 1000000 VND + 100000 VND = 1100000 VND |
| `hoa-don-le-DEMO.xml` | 1000000.123456 VND + 100000.012345 VND = 1100000.135801 VND; giữ từng chữ số |
| `hoa-don-thieu-DEMO.xml` | Thiếu KHHDon, NMua/MST rỗng, thiếu TgTTTBSo: ba trường SDK tương ứng null; tổng ABSENT, money HOLD |

`dap-an.json` được viết literal từ nội dung XML, không sinh từ parser. `bam-fixture.json` chỉ ghim SHA-256 và số bytes của ba fixture mới đang có, tính bằng hashlib độc lập với parser. Không dùng hoặc xác nhận hash golden cũ. Bản XML trong thư mục này phải giống bytes bản `goi/e_hoa_don/demo/`; UTF-8/LF, `.gitattributes` giữ nguyên bytes XML trên Windows/Linux. Bản checkout Windows của fixture tiền nguyên được chuẩn hóa từ CRLF về LF; hash bytes LF khớp pin HD-0 đã ghi, không đổi dữ liệu nguồn trong Git.

Ba ca đều thành công **bước đọc kỹ thuật** bằng Core giả (CoreGia); context=None, can_kiem_tra=true, identity/semantic digest null, thuế UNKNOWN, ghi nhận NOT_PERFORMED. TToan được đọc bổ sung nhưng ngoài semantic envelope V1: giữ TOTAL_SECTION_UNSUPPORTED/CONTENT_OUTSIDE_SUPPORTED_ENVELOPE, không gọi đây là nội dung hoàn toàn hỗ trợ. `test_hd_3.py` kiểm đủ 18 trường và JSON qua CoreGia.doc_tep, occurrence/locator/Decimal, tiền/thuế, bytes/hash; không chỉ kiểm XONG.

Ca 1.000 dòng (qua) và 1.001 dòng (bị chặn) sinh lúc test trong `tmp_path/DEMO`, không lưu fixture lớn trong gói. Các dòng được lặp để kiểm tài nguyên/ordinal, không dùng làm chứng cứ tổng 1.000 dòng đã đối chiếu nghiệp vụ. Ca âm nằm trong pytest, không đưa vào chay_thu_demo.

Đối chiếu ý đồ test tham chiếu (không chạy nguyên trạng các test cũ):

| Nguồn chỉ đọc | Ý đồ giữ lại | Bằng chứng hiện hành |
|---|---|---|
| `tests-tu-core/test_hoa_don_xml.py` | Strict path/namespace, occurrence, Decimal, thiếu/rỗng/0, context, thứ tự nguồn, money/relations | `test_hd_1.py`, `test_hd_3.py`: oracle literal + lõi thuần/CoreGia |
| `tests-tu-core/test_g3_goi_hd_reader.py` | SDK primitives/Issue, DTO bất biến, snapshot bytes, Decimal, import độc lập | `test_hd_3.py::test_dto_bat_bien_decimal_snapshot_va_issue_sdk`, `kiem_doc_lap.py`, `test_xml_sdk.py::test_loi_parser_khong_doi_thuat_toan` |
| `tests-tu-core/test_g3_goi_hd_anh_xa.py` | Thiếu context khác lỗi cấu trúc; không biến CHO thành CHUA_RO; lỗi invariant không bị che | `test_hd_1.py`, `test_hd_2.py`, `test_hd_3.py::test_loi_nghiep_vu_dung_lop_ma_cau_hd_1` |
| `tu-core-cu/tests/test_g3_hd_1.py` | Số 0 đầu, tiền/ngày/miền, nguồn thiếu/mơ hồ, hash/locator, không suy đủ hoặc tự cấp ID | `test_xml_sdk.py`, `test_hd_1.py`, `test_hd_2.py`, `test_hd_3.py` |

Các bài cũ dùng namespace Core/bridge, schema hoa_don.v1 và corpus/overlay không kèm bytes gốc; hợp đồng mới là hoa_don.doc_xml@2. Không kiểm pickle/alias Core hoặc nhận hash engine/context/bằng chứng cũ đã tương thích. ZIP/bảng kê/tải/Cloud/Node nằm ngoài HD-3, chưa được nghiệm thu. Không có skip/xfail cho các ca XML cần thiết.

Regression âm hiện hành: XML hỏng/profile/namespace/DOCTYPE/encoding, cấu trúc trùng, MIME sai; scalar trùng/mixed/rỗng/thiếu; số tiền sai ngữ pháp/vượt miền, currency thiếu, ngày sai, tổng lệch, thiếu TToan; bytes/JSON/dòng vượt trần; hủy, upload lỗi, mất ACK/retry và mất lease; stderr/lỗi/tiến độ không chứa canary. Test HD-1/HD-2 tiếp tục chạy cùng HD-3, không chép lại hoặc bỏ qua.
