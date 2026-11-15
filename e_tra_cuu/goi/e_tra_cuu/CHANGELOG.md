# Thay đổi

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
