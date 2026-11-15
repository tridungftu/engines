# Thay đổi

## 0.1.0 — 15/11/2026 — TC-6 (chưa phát hành)

- Thực thi hai hậu kiểm Local `phan_tich_cau_hoi@1`, `xep_hang_lai@1`, đúng
  3 tệp mã cau_hoi.py/xep_hang.py/chay.py. Đọc lại snapshot/nguồn/quyền,
  tái dựng prompt/khuôn/map/ngân sách và băm toàn yêu cầu AI; tự kiểm quote.
- Tập thực thể/ý định bám căn cứ câu hỏi và danh mục Core cấp ngoài payload;
  giữ mã 0 đầu. Mơ hồ cần làm rõ, không chọn bừa khoản vay/hợp đồng. Cờ
  thời điểm từ câu hỏi/chính sách Core; “tháng này” theo mốc Core có múi giờ.
- Hàm đúng tên/phiên bản/schema/ý định/binding tham số/phạm vi Core; từ chối
  SQL/code/URL/khóa thừa. Module chưa chạy ghi chờ, không dữ liệu tầng 1 giả;
  Core chọn tầng tiếp, engine không thực thi hàm hoặc truy vấn.
- Xếp hạng đủ hoán vị mã, điểm hữu hạn đúng thang, tie giữ thứ tự Core.
  Giữ nguyên mọi ứng viên/nguồn/phiên bản/nội dung, không top-k ngầm.
  Chặn nhánh chuẩn bị AI khi 0 ứng viên; Core rẽ nhánh không AI.
- Snapshot kết quả và nguyên tập phụ thuộc/thực thể gửi Core, kiểm ACK/hủy;
  không cache/chỉ mục/nhật ký/cấu hình bền/tệp tạm. Mẫu Ngan/schema giữ nguyên.
- Đã kiểm bằng Core giả (CoreGia), Local giả theo protocol, 0 model/provider
  thật/Cloud. Seam phân giải chỉ là quy ước tạm C-TC-03, không chứng nhận RLS.
  Harness 17/17; CLI chuẩn vẫn 0/5 CHUA_CAU_HINH/mã 1. Số kiểm thực và thời
  gian ở docs/VIEC.md; chưa kiểm Core thật/AI thật/Linux.

## 0.1.0 — 15/11/2026 — TC-4 (chưa phát hành)

- Thực thi `tra_cuu.chuan_bi_ai@1` cho bốn tác vụ Local; kiểm lại snapshot,
  nguồn/quyền/cấu hình/tóm tắt. Prompt module bắt buộc, không dùng mặc định;
  model ưu tiên chỉ chuyển cho Hỏi AI. TC không gọi engine/model.
- Ngữ cảnh nguyên Unicode với mã đoạn/nguồn/ứng viên/hàm và map offset về
  nguồn/snapshot. Bốn khuôn đóng kết quả; xếp hạng đủ mã đúng một lần, hàm
  và tham số theo allowlist, giữ ref nội bộ. Không model cấp quyền/duyệt/Xanh.
- Ghim snapshot `cho_ai` tại Core với prompt/phiên bản/khuôn/ngữ cảnh/map/băm.
  `chuyen_tiep.tra_cuu` chỉ ref/băm/metadata, không toàn văn/danh mục/câu hỏi.
- Kiểm trần ký tự/bytes UTF-8/số lượng; vượt từ chối, không cắt/batch/Cloud.
  Token/context thực ghi chưa đo. Tầng 1 Python/thiếu bằng chứng đi nhánh
  Core bỏ AI, không tạo yêu cầu/phản hồi giả.
- Đã kiểm bằng Core giả (CoreGia), NganBoNho và consumer AI-2 có Local giả
  do tests điều phối, kể cả CHUA_RO; 0 Cloud/mạng. Harness thêm bốn tác vụ.
  CLI chuẩn vẫn 0/5 CHUA_CAU_HINH/mã 1; SDK còn lỗi tham số chung trước handler.
  Chi tiết kiểm thực và Cần Core trong docs/VIEC.md.

## 0.1.0 — 15/11/2026 — TC-3 (chưa phát hành)

- Thực thi `tra_cuu.cat_doan@1`: snapshot ghim qua Core, `cat_doan/da_nhan`
  → `da_cat_doan`; kiểm lại quyền/băm bytes/nguồn/cấu hình/metadata. Cấu hình
  lấy bản Ngan đã ghim, không đọc lại giá trị mới giữa chuỗi.
- Cắt Điều/Khoản rồi câu/khối/trang, ghép tới mục tiêu, giữ đủ đuôi và Unicode
  NFC/NFD. Mã đoạn ổn định theo nguồn/phiên bản/offset/bản thuật toán. Từ chối
  đơn vị không chia an toàn >8000, quá số đoạn/ngân sách; không cắt ngầm.
- Bảng giữ tiêu đề/ô gộp/ô rỗng và map từng ô; chỉ suy map khi chiếu TAB +
  LF/CRLF khớp chính xác, còn lại cần offset tường minh. Tiêu đề lặp đánh dấu
  ngữ cảnh, đoạn tổng hợp không giả một lát liên tục. Giữ hộp thực cấp khối/ô,
  DOCX không trang để null, không confidence/hộp suy đoán hoặc chỉ mục/vector.
- Đóng ba nợ TC-2: regex kênh ngoài chỉ ở định danh/tham chiếu; các object
  metadata/ứng viên/bằng chứng/mục danh mục từ chối khóa thừa; đọc luồng ngắn
  tiếp tới EOF/trần. Thêm .gitattributes cố định LF cho DEMO có băm bytes.
- Đã kiểm bằng Core giả (CoreGia), harness 9/9; AI/Cloud=0, không ghi bền/tệp
  tạm. CLI chuẩn vẫn 0/5 do CHUA_CAU_HINH/mã 1; C-TC-01/02/03/05 còn chờ.
  Kết quả kiểm thực ở docs/VIEC.md; không chứng nhận RLS/Core thật hoặc Linux.

## 0.1.0 — 15/11/2026 — TC-2 (chưa phát hành)

- Thay stub nội bộ bằng tám năng lực/bốn loại đã duyệt; nhận yêu cầu đã làm,
  bảy handler chờ TC-3…8 trả CHUA_LAM, không kết quả giả.
- JSON chính băm bytes chính xác/≤1 MiB trước parse; đọc tệp con qua mo_tep,
  kiểm metadata/băm/phiên bản/nguyên phong bì OCR, 20 MiB/tệp và 64 MiB tổng.
  JSON nghiêm, trần văn bản/trang/danh mục/hàm/câu hỏi/ứng viên, lỗi Việt an toàn.
- Cấu hình + row_version từ một lần đọc ngăn; snapshot đầy đủ tải Core,
  hồ sơ ≤64 KiB chỉ ref/băm/tóm tắt. Không ghi cấu hình/sổ/cache/tệp tạm trên máy.
- Cửa nguồn/quyền độc lập với JSON; thiếu cửa/khác phạm vi từ chối rõ, không
  suy quyền/module từ prompt. Adapter tin cậy chỉ trong tests; tầng 1 không
  mở lại gốc/OCR. Cần Core C-TC-01/02/03/05, chưa chứng nhận quyền thật.
- Năm chay_thu_demo với bytes/băm thật; harness nạp NganBoNho và tệp con,
  đã kiểm bằng Core giả (CoreGia), mạng ngoài/Cloud=0. CLI SDK gốc vẫn lỗi
  CHUA_CAU_HINH/mã 1, cổng chuẩn chưa đạt; không sửa SDK hoặc tạo config DEMO
  ở runtime. Kết quả pytest/độc lập/harness thật tại docs/VIEC.md.

## 0.1.0 — 15/11/2026 — TC-1 (contract, chưa phát hành)

- TC-Q13 đã duyệt chiều 15/11: thêm schema `ho_so_tra_cuu` nguồn chung và bản
  chép gói; chép nguyên ba schema văn bản/yêu cầu AI/trả lời AI, kiểm băm LF.
- TC-1-CONTRACT chốt required/enum/trần, snapshot năm tác vụ, state/summary,
  băm/nguồn/offset, ngữ cảnh tin cậy và tám năng lực để TC-2 triển khai.
- Giữ manifest/chay.py khung TC-0 và 0 demo theo lệnh giao mới nhất; TC-2 thay
  đồng thời manifest/stub trước phát hành. Không thêm handler thành công giả.
- Test contract có adapter tệp con/quyền chỉ trong tests; khung và lỗi hiện có
  đã kiểm bằng Core giả (CoreGia), không chứng nhận handler nghiệp vụ/RLS thật.
  Không thêm dependency, không Cloud/AI/Core thật, không lưu bền trên máy.
- Cần Core C-TC-02/03/05; CLI 0 demo trả mã 1 vẫn ghi C-TC-01. Kết quả thật tại
  docs/VIEC.md, không diễn giải 0 demo là nghiệp vụ đạt.

## 0.1.0 — 15/11/2026 — TC-0

- Tạo khung SDK 2.0 với năng lực nội bộ `tra_cuu.kiem_khung@1`, luôn lỗi CHUA_LAM;
  chay_thu_demo=[] (0 demo, chưa kiểm nghiệp vụ). Chưa có quy trình người dùng
  phụ thuộc stub; phải thay năng lực đích trước phát hành. Theo lệnh TC-0 ghi mốc
  TC-1; phiếu TC-1 hiện dời sửa handler sang TC-2, chờ lead thống nhất mốc.
- Chép nguyên hai mẫu NGAN-0, kiểm băm sau CRLF→LF; giữ ngăn SDK khi có,
  dùng một ngăn RAM khi thiếu và cảnh báo stderr một lần.
- Schema cấu hình chỉ từ khóa mẫu hỗ trợ, cấm trường thừa; khóa cấu hình {},
  không tạo mặc định khi chưa có bản ghi; ngưỡng mặc định chưa đo.
- Bản khai SDK 2.1 riêng cho cau_hinh/dot_kiem và hai màn dự kiến TC-9;
  manifest vẫn 2.0, chưa khai ho_so_tra_cuu trước TC-Q13.
- Test DEMO: stub/cổng cấu hình đã kiểm bằng Core giả (CoreGia);
  CAS/unique/rollback/pháp nhân/cursor trực tiếp bằng NganBoNho;
  bộ quét import/kênh cấm/bytecode/liên kết trả 0/1. Không mạng/Cloud/lưu bền.
- Chưa kiểm nghiệp vụ, Core thật, UI hoặc Linux. Kết quả lệnh thực ở docs/VIEC.md
  của engine (ngoài gói).
- Cổng CLI chuẩn chưa đạt: SDK 2.0.0 trả mã 1 khi danh sách demo rỗng dù phiếu
  hợp lệ. Giữ nguyên 0 demo theo TC-0, ghi C-TC-01; không sửa SDK hoặc báo đạt giả.
