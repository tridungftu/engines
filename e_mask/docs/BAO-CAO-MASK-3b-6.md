# Bàn giao MASK-3b → MASK-6 — 15/11/2026

Kết luận: **Đạt phạm vi triển khai bằng CoreGia/KttCore giả; chưa đạt nghiệm thu chung qua CLI SDK chuẩn.** Hai handler có nghiệp vụ thật nhưng SDK 2.0 chưa cung cấp nguồn quyền/mã yêu cầu tin cậy của Mask, nên CLI chuẩn bị chặn 0/2. Adapter DEMO ngoài gói tiêm quyền/ngăn, chạy đúng hai ví dụ manifest đạt 2/2. Chưa kiểm Core thật, chưa bật Cloud.

PR: **chờ lead mở**. Worktree/nhánh `codex/e_mask-mask-3b`; không commit/push. Không sửa mẫu chung NGAN-0, nguồn cũ, tham chiếu hoặc bộ SDK đã khóa.

## Đã làm

- **MASK-3b:** cổng `Ngan` và `NganBoNho` tạm, cấu hình đọc từ ngăn; port kho dùng năm bảng `dinh_danh`, `bi_danh_tam`, `cho_duyet`, `ma_yeu_cau`, `dau_gap`, tất cả phạm vi engine, tách vùng DEMO/thật. Dòng CAS chung mỗi vùng bảo vệ đọc nhiều bảng và chốt nguyên tử alias/hàng chờ/đếm/tham chiếu/yêu cầu/dấu lượt; mọi xung đột thành `MASK_XUNG_DOT`, thử lại được. Không ghi kho JSON trên đường handler.
- Bộ tiền tố chốt MASKCT/MASKCN/MASKDC/MASKMST/MASKTK/MASKKHAC/MASKTAM. Mã Junsky giữ nguyên, chặn họ tiền tố đã dành riêng; có ca mã Junsky DEMO và va chạm UUID không làm ghi đè tên gốc.
- **MASK-4:** tạo schema chung `van_ban_da_che`, chép ba schema vào gói và so SHA. Kiểm JSON UTF-8, khóa trùng, NaN, kiểu boolean, trường lồng, trần văn bản/danh sách/chuyển tiếp; không mang metadata OCR/tên gốc vào kết quả che.
- **MASK-5:** handler che văn bản trực tiếp/OCR/JSON và mở che JSON/AI. Mở cả câu trả lời, giá trị chuỗi trong dữ liệu, câu trích; giữ kiểu/khóa/metadata và nội dung AI thêm. Câu trích đổi chữ bị hạ kết luận kiểm nguyên văn, đánh dấu cần kiểm lại, không tự suy offset mới. Chỉ đóng khi được yêu cầu và mở đầy đủ; bí danh lạ có vị trí đường trường.
- Bốn từ điển sạch từ `e_mask/tham-chieu/tu-dien/` đã chép vào gói, nạp với kiểm SHA; test so byte với tham chiếu. Theo lệnh giao mới nhất, dùng bản đã được Anh duyệt; ghi chú “chờ Anh” trong nguồn tham chiếu là lịch sử, không sửa bản tham chiếu. Không dùng fixture thay thế trên đường handler.
- **MASK-6:** duyệt/từ chối, đóng/dọn qua ngăn; bí danh tạm còn mở được cho các yêu cầu đang xử lý, kể cả sau duyệt/từ chối. Dọn dùng cùng CAS với việc thêm tham chiếu. Màn `ui/duyet_dinh_danh.js` qua `KttCore.engine("e_mask").ngan`, lọc theo tên/nhóm/số gặp, chỉ chèn text. Công cụ chuyển DEMO chạy khô mặc định, không đọc danh mục thật, chạy lần hai không thêm trùng.
- **Đóng nợ MASK-3:** ghi dấu lỗi sau khi nguồn nhận chốt không làm mất `ChuaRo`. Dấu/chọn định danh cho phép tái tạo khi giao lại; băm kết quả phát hiện thay đổi tài nguyên/logic, không âm thầm đổi kết quả đã chốt. Không cất văn bản hoặc kết quả AI trong ngăn.

## Phân lát/tập mã để lead tách PR

| Phần | Tập mã chính | Lý do |
|---|---|---|
| MASK-3b-A | `ngan.py`, `cau_hinh.py`, `kho_ngan.py`, `kho_qua_core.py`, `kho_dinh_danh.py` | 5 tệp; ngăn và nối kho |
| MASK-3b-B | `KHAI-SDK-2.1.json`, `tai_nguyen.py`, `tu_dien/SHA256.json` | Khai báo/nguyên liệu sạch; bốn tệp txt là dữ liệu đi kèm |
| MASK-4 | `phong_bi.py`, schema chung mới và ba bản gói | 5 tệp mã/schema |
| MASK-5 | `chay.py`, `phong_bi.py`, `engine.json` | Nối handler/adapter và ví dụ; một tệp tiếp tục từ MASK-4 |
| MASK-6 | `duyet_dinh_danh.py`, `ui/duyet_dinh_danh.js`, `cong-cu/chuyen_danh_muc_demo.py` | 3 tệp mã; màn mới theo lệnh đợt 2 |

Test/tài liệu và dòng bỏ qua thư mục tạm pytest ở `.gitignore` là phần hỗ trợ. Không tạo thêm nhánh/commit trong bàn giao này; lead quyết định tách các PR khi gộp dependency.

## API Ngan đã dùng để đối chiếu NGAN-0

| Hàm/thuộc tính | Tham số/dạng dùng |
|---|---|
| `chon_ngan(app)` | Ưu tiên `app.ngan`; thiếu dùng RAM của cùng app, cảnh báo stderr một lần. Handler ưu tiên `viec.ngan` và chọn lại khi SDK gắn ngăn thật |
| `ngan.doc(bang, khoa)` | Khóa các bảng Mask là `{vung, khoa}`; trả `None` hoặc đối tượng `.gia_tri`, `.row_version` |
| `ngan.tim(bang, loc=..., gioi_han=500, tiep=...)` | `loc={vung}`; đọc hết các trang. Trả `{danh_sach: [BanGhi], tiep}` |
| `with ngan.lo() as lo` | Chốt khi ra khỏi with; lỗi trong lô không ghi gì |
| `lo.them(bang, khoa, gia_tri)` | Thêm dòng mới; vi phạm duy nhất là xung đột |
| `lo.sua(bang, khoa, gia_tri, row_version=...)` | Thay giá trị dòng; CAS bắt buộc, khóa giữ nguyên |
| `lo.xoa(bang, khoa, row_version=...)` | Xóa có CAS |
| `lo.lay_hoac_tao(bang, khoa, gia_tri)` | Khởi tạo dòng CAS chung một lần; không phụ thuộc giá trị trả khi engine chạy |
| `NganXungDot` | Adapter bắt và đổi sang `LoiNghiepVu("MASK_XUNG_DOT", ..., thu_lai_duoc=True)` |
| `doc_cau_hinh(ngan, schema)` | Đọc `cau_hinh` với khóa `{ma: "cau_hinh"}`, giá trị ở `.gia_tri["gia_tri"]`; thiếu trả `None`. Mask hiện không cần cấu hình nên chỉ kiểm hợp đồng helper |

Các bảng được khai trong `KHAI-SDK-2.1.json`; mọi dòng Mask ghi đều có test đối chiếu trường. Bản bọc tạm chỉ thư viện chuẩn. Test helper còn kiểm `NganBoNho(bang=[{ma, khoa, duy_nhat, pham_vi}], phap_nhan_id=...)`, `theo_phap_nhan(id)` và kết quả lô `.ket_qua`: đây là tiện ích test của bản tạm, **mã nghiệp vụ không phụ thuộc các tiện ích đó**. Cần lead đối chiếu dạng trang tìm/khóa cấu hình với mẫu NGAN-0 chính thức.

Màn giả định browser API `ngan.doc(bang, khoa)`, `ngan.tim(bang, {loc, gioi_han, tiep})`, `ngan.ghi_lo({lenh})`, dòng `{gia_tri, row_version}`. Kiểm quyền server thuộc Core; không lấy cờ Admin từ payload. Python dùng port tin cậy `quyen.xac_minh(...)` có sẵn; thao tác Admin dùng port `xac_minh_admin()` trả vùng đã xác minh.

## Kết quả kiểm

Đã kiểm bằng Core giả (CoreGia), dữ liệu DEMO; KttCore là bản giả chạy Node, không mạng. Nhật ký đầy đủ, mã thoát và phiên bản môi trường tại [KET-QUA-KIEM-MASK-3b-6.txt](KET-QUA-KIEM-MASK-3b-6.txt). Kết quả cuối: pytest **269 passed, 2 skipped, 190 subtests passed** (24.30 giây), mã 0; kiểm độc lập mã 0; Node **4/4**, mã 0; adapter DEMO **2/2**, mã 0; CLI SDK chuẩn **0/2**, mã 1 vì thiếu nguồn quyền; công cụ chuyển DEMO chạy khô mã 0; `git diff --check` mã 0.

Hai skip có chủ đích: so SHA `ngan.py` và `cau_hinh.py`, lý do chính xác **“chờ NGAN-0 gộp”**. Không sửa/tạo mẫu trong `_chung/mau-ma/**`.

Các ca mới gồm CAS/rollback/duy nhất, hai luồng lay_hoac_tao, tách pháp nhân, dấu gặp và giao lại, mất ACK/chốt chưa rõ, hủy, trùng alias, băm kết quả, trần/UTF-8/JSON, khứ hồi AI, sai module/người/tài liệu/vùng, hai yêu cầu giữ alias, dọn tranh chốt, import lặp và màn giả. Test lịch sử kho tệp giữ nguyên để bảo toàn hiện vật; không dùng kho đó trên đường handler mới. Chưa chạy Linux thực tế trong bàn giao này.

## Lệch khỏi phiếu / quyết định tạm

- NGAN-0 đang làm song song: viết bản bọc tạm **trong gói** theo lệnh lead, chưa thể chép/so SHA thật. Hai test so băm được chuẩn bị và skip.
- Theo quyết định 15/11, bỏ đường ghi kho/cấu hình tệp. Hai tệp `kho_tam.py`, `cau_hinh_may.py` giữ nguyên để lead chuyển `LUU-TRU/` sau, không xóa/di chuyển; handler và kho mới không import chúng.
- Màn duyệt được làm ngay trong MASK-6 theo lệnh mới, thay giới hạn chưa làm UI của phiếu cũ. Bốn từ điển lấy từ nguồn sạch đã duyệt, thay fixture trên đường handler.
- Chỉ giữ lựa chọn định danh/băm/số đếm của lượt, tái tạo kết quả trong RAM; nếu khác băm đã chốt thì từ chối. Không vượt quy tắc cấm cache tài liệu/kết quả mở che.
- Giao dịch đề nghị SDK tối đa 100 lệnh: vượt từ chối toàn bộ, không chia thành nhiều lô. JSON mẫu 1/3 có trần kỹ thuật 4 MiB như mức thử cũ; không coi đây là trần tệp nghiệp vụ được duyệt. Hai giới hạn này được nêu rõ trong README và mục Cần Core.

## Cần Core / Chờ Anh mới phát sinh

Chi tiết ở [VIEC.md — Cần Core](VIEC.md): mẫu NGAN-0, ngăn SDK 2.1, nguồn quyền/mã yêu cầu, kiểm lease/đọc kết quả, khóa HMAC, giao dịch lớn, hợp đồng nạp màn và review Core. CLI chuẩn vẫn bị chặn đúng quyền. Không có câu hỏi mới cần Anh phê duyệt trong phạm vi đã giao; trần tệp/phần Word/Excel/PDF chờ MASK-7 theo kế hoạch.

## Thời gian

Giờ bắt đầu theo lead: **07:39 ngày 15/11/2026 (UTC+07)**. Giờ kết thúc **08:09:07**, thời gian thực tế **0.50 giờ**. Ước tính phiếu: MASK-3b **3 giờ**, MASK-4 **2 giờ**, MASK-5 **5 giờ**, MASK-6 **3 giờ**, tổng **13 giờ ước tính**; không tách thời gian thực tế từng lát vì triển khai nối tiếp trong cùng phiên.
