# MASK-S22 — báo cáo bàn giao

Ngày 15/11/2026. Nhánh `codex/e_mask-mask-s22`, xếp trên MASK-B4 và main Lead đã gộp. PR: **chờ lead mở**; không commit/push.

**Kết luận: Chưa đạt điều kiện nghiệm thu chung** — CLI chuẩn còn 0/2 do SDK chưa cấp được nguồn quyền/mã yêu cầu tin cậy cho Mask; pytest còn một subtest hiệu năng cũ vượt ngưỡng 5 giây. Hai ca deadline đã qua trong lượt toàn phần.

**Đã làm:** venv mới và wheel SDK 2.2.0 offline, SHA256 khớp; ghim khóa phụ thuộc; gói 1.3.0 với khoảng SDK 2.2.0 và schema cấu hình rỗng theo hiện trạng. Handler đọc snapshot `viec.cau_hinh`; không còn bảng cấu hình RAM hoặc bộ đọc cấu hình tạm trên đường chạy. Bản khai 2.1 và bộ đọc tạm giữ nguyên byte trong `LUU-TRU/sdk_truoc_2_2/`.

Kho bí danh giữ RAM theo ngoại lệ Lead/CĐ-36, tách khỏi `app.ngan`/`viec.ngan`; không khai bảng ngăn hoặc migration/kiểm kê. Không có trường cấu hình engine bắt buộc để sinh `CHUA_CAU_HINH`; prompt/model Local vẫn thuộc module/quy trình qua port Core. Không có đệm cấu hình cần callback. Không đổi nghiệp vụ mở che hoặc thêm đường giải mã. Màn duyệt giữ KttCore.engine, chỉ còn kiểm với bản giả, chờ P3 trước khi nối ngăn Core mới.

Adapter công cụ Local ngoài gói dùng CoreGia 2.2.0 (`dat_cau_hinh`, `xem_ngan`) cho Hỏi AI AI-11/AI-12. Hai test deadline giữ ca trước AI và sau một đoạn hoàn tất, tiêm hết hạn tại checkpoint với đồng hồ logic riêng của tool; không lấy tốc độ chuẩn bị của máy làm tín hiệu hết hạn. Provider HTTP giả/SDK dùng đồng hồ riêng nguyên bản; các ca HTTP timeout và child CLI khác vẫn chạy thực. Hai ca này không phải phép đo kill process/model thật.

Giữ ca hành vi/an toàn, CAS/chống trùng/quyền và bốn xfail strict held-out cũ (giới hạn lớp quy tắc, nợ CAO), không thêm skip. Chỉ bỏ so băm mẫu tạm theo yêu cầu. Thêm bốn ca S22. Sửa test ghim phiên bản; băm tham chiếu nguồn HD-9 đã gộp được ghi riêng, không thay băm lịch sử hoặc mã nguồn engine khác. Năm tệp Python sửa; các khai báo/khóa phụ thuộc/tài liệu kèm theo yêu cầu.

**Kết quả kiểm:** đã kiểm bằng Core giả (CoreGia), chỉ DEMO, Cloud tắt.

| Kiểm | Kết quả thật hiện có |
|---|---|
| SHA wheel | Khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`; SDK in 2.2.0 |
| `python -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | **0/2 ĐẠT, mã 1**; cả hai `MASK_NGU_CANH_CHUA_XAC_MINH` |
| `python -m pytest e_mask/tests -q --basetemp=.pytest-tmp` | **2179 passed, 1 failed (subtest hiệu năng), 4 xfailed, 189 subtests passed, 0 skipped; 376,45 giây, mã 1** |
| `python e_mask/tests/kiem_doc_lap.py` | ĐẠT, mã 0 |
| Băm LF/AST/JSON/phạm vi | 8/8 băm đích khớp; AST/JSON đạt; chỉ đổi e_mask; không có bytecode trong gói |
| Kiểm kê migration | Không áp dụng: không có bảng ngăn/migration theo ngoại lệ Lead |

Lượt toàn bộ đầu: 2176 passed, 5 failed (hai subtest hiệu năng, test phiên bản và hai kiểm nguồn), 4 xfailed, 188 subtests passed, 270,54 giây. Đã sửa phiên bản/nguồn. Lượt 2 còn hai subtest hiệu năng >5 giây và một fixture deadline hết hạn trước checkpoint. Sau cố định đồng hồ fixture, hai ca deadline kiểm riêng 2 passed, 48 deselected, 5,32 giây. Lượt chốt: hai deadline đã qua; chỉ còn subtest `mau='1 '` tại `test_che_van_ban.py::test_hieu_nang_ba_chuoi_benh_ly_500_nghin_ky_tu`, đo **7,619 giây > 5 giây**. Mã/ca/ngưỡng hiệu năng 5 giây và timeout con 12 giây không sửa. Ca này từng đạt khi kiểm riêng, nhưng kết quả đó không thay được lần full suite còn lỗi; nguyên nhân chậm chưa được kết luận trong S22. Cần Lead tổ chức kiểm hiệu năng ít tranh chấp tài nguyên hoặc giao lát tối ưu riêng, không nới ngưỡng để nhận đạt. [Log lượt 2](KET-QUA-KIEM-MASK-S22-LUOT-2.txt), [log chốt](KET-QUA-KIEM-MASK-S22.txt).

**Thời gian thực tế:** 18:04:00–18:45:35 ngày 15/11/2026 (UTC+07), **0.69 giờ**. Bắt đầu theo mốc Lead giao. Phiếu/CHUYEN-SDK-2.2 §4 chưa ghi ước tính riêng MASK-S22; không tự suy một số ước tính để so sánh.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** áp dụng ngoại lệ Lead riêng Mask: giữ cổng kho RAM và các lệnh dọn hiện hành, chưa chuyển sang ngăn SDK; `ngan.py` còn trong runtime vì ngoại lệ này. Schema rỗng do chưa có cấu hình engine thực tế. Không bỏ hoặc đổi hai DEMO thành no-op, không dùng runner có quyền thay tiêu chí CLI. Không đổi Core/SDK/API/schema chung, nguồn cũ hay engine khác.

**Cần Core / Chờ Anh mới phát sinh:** C-MS22-01: SDK/CLI DEMO chưa có cửa fixture quyền/mã yêu cầu Mask tin cậy; CLI cũng không nạp cấu hình DEMO từng ví dụ, chỉ mặc định schema (Mask hiện không cần trường bắt buộc). C-MS22-02: thiết kế P3 phải tuân CĐ-36, không mở đường giải mã; đây là nợ đã tồn tại. Các cửa ACL/lease/provenance/tokenizer/stream kế thừa còn phải kiểm thật. Chưa kiểm Linux/Core/Office/Local thật; không có câu chờ Anh mới trong lát này. Chi tiết tại mục Cần Core trong [VIEC](VIEC.md).
