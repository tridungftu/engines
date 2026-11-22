# Thay đổi

## 0.1.3 — 22/11/2026

- SDK25: dùng cửa công khai SDK, bỏ lớp bọc nhật ký/MIME; chấp nhận câu lỗi
  chuẩn đã lọc của SDK. SDK 2.5.0 vẫn yêu cầu MIME `.xlsm` viết thường;
  ghi Cần Core chuẩn hóa trước khi giao việc. Không đổi nghiệp vụ.
- Công cụ kiểm độc lập đọc dependency từ lock mới; cài sạch và CI dùng SDK
  2.5.0 cùng wheel đi kèm. Thêm tự kiểm ASCII/khuôn lock, tên SDK bị cấm,
  đủ wheel đúng bản/SHA-256; giữ ba phiên bản thư viện đã ghim.
- Kèm thư viện để Core tự cài ngoại tuyến (phiếu lead Core 21/11, CĐ-50 mục 6): khai `phu_thuoc_python`, `requirements.lock` mỗi dòng một thư viện có SHA-256, đủ phụ thuộc gián tiếp, không còn dòng SDK; thư mục `wheels/` có đúng một wheel CPython 3.13 win_amd64 hoặc thuần Python cho mỗi dòng. Khoảng SDK nâng lên `>=2.4.0 <3.0.0` vì khóa này có từ SDK 2.4.0. Không đổi xử lý việc.

## 0.1.2 — 22/11/2026

- TS-EX: trình soạn Cài đặt bước. Theo `_chung/docs/GIAO-CODEX-UI-CAU-HINH.md`; không đổi xử lý việc. Màn chờ Core mở cửa D/D2/E/F mới hiện trong Core.

## TS-EX — 21/11/2026
- Thêm trình soạn ô đích, nhãn tìm, bộ nhóm và khuôn cột bằng trường/danh sách;
  giữ nguyên cấu trúc JSON v1, ngữ nghĩa điều kiện, thứ tự nhóm và trần hiện có.
- Thêm khai dự kiến D2 trong KHAI-SDK-2.1.json. Core quản lý đọc/lưu/CAS của
  bước quy trình; chưa khai khóa mới vào engine.json, không cất tham số vào engine.
- Bổ sung mô tả cấu trúc/mẫu cho ba tham số JSON trong manifest và README.
  Không sửa mã Python xử lý việc, dependency hoặc dữ liệu DEMO runtime.
- Đã kiểm bằng Core giả (CoreGia); màn chưa được nạp trong Core thật.

## 0.1.1 — 19/11/2026
- EX-6: rà đúng ba dependency runtime, tổng hợp nguồn/dòng cũ → tệp mới và SHA-256.
- Ghi cả XML worksheet trong RAM: wb.save(BytesIO) của openpyxl vẫn tạo tệp tạm;
  lớp ghi báo cáo riêng dùng BytesIO và đóng stream trong finally.
- Bổ sung kiểm máy sạch offline, CI Linux/Python 3.11, số đo toàn hai năng lực
  và mẫu sát trần ô/vùng/giải nén; đề xuất giữ 20 MiB/120 giây.
- Đã kiểm bằng Core giả (CoreGia); bản phát hành từ git do lead đóng sau commit.

## 0.1.0 — 19/11/2026
- EX-3: K8 sau công tắc `kiem_nguon_kl`, dùng bộ đọc bảng của EX-4; giữ phân loại,
  mức/mã/ô nguồn trên DEMO. Tính Decimal, giới hạn truy nguồn 8 tầng từ chối khi vượt.
- Báo cáo giữ kiểu ô, màu cờ và 15 sheet nguồn; tắt K8 còn 12 sheet. Ghi bằng
  openpyxl vào BytesIO, tải qua Core; công thức nguồn chỉ là chuỗi hiển thị.
- Tiền báo cáo có đơn vị rõ từ tệp hoặc để trống; JSON K8 giữ số thập phân cùng
  tiền tệ (null nếu chưa rõ). Hoàn tất `tep_bao_cao`, mở schema K8 ngoài gói.

## 0.1.0 — 18/11/2026
- EX-5: đọc khuôn `tong_quat`, kiểm cấu trúc/trần JSON, dùng chung matcher từ khóa
  của `bo_nhom.py`; tiêu đề nhiều tầng/ô gộp, cột bắt buộc/tùy chọn, dòng dừng,
  Decimal/ngày ISO/tiền tệ và cảnh báo dữ liệu. Thêm DEMO giá thành, báo giá, đáp án.
- EX-5: bỏ helper chuẩn hóa riêng EX-4; import trực tiếp hàm EX-1 từ `chuan_hoa.py`.

- EX-2: chuyển cây K7, chạy trước K6; cờ K6 tại BTH!J21 đã khớp mã gốc.
- Kiểm ô đích, tìm theo nhãn do module truyền; thiếu đích có một mục Kiểm soát.
- Bộ nhóm được kiểm cấu trúc/trần; hỗ trợ chứa chuỗi, nguyên từ và chữ số,
  không thực thi regex; không bộ thì Chưa phân nhóm và so_ngoai_nhom null.
- K2/K6 lấy nhóm/tài liệu từ bộ; hạ mức liên kết ngoài ở cột phụ theo cây nguồn.
- Mở schema JSON K7, giữ số Decimal; từ chối vượt trần cây thay vì cắt ngầm.
- Phụ lục A chỉ là fixture ngoài gói; báo riêng lệch nhóm 6 và hành vi dai/rong/cao.
- EX-1: chuyển SoDo, tham chiếu, chuẩn hóa Decimal và K1–K6; nạp bytes,
  bỏ thư mục liên kết ngoài; trả trường và tải JSON UTF-8 trong RAM.
- Kiểm hủy giữa các kiểm, TEP_HONG an toàn, trần JSON 20 MiB; schema ngoài gói
  chờ lead duyệt. K7/K8, phân nhóm và báo cáo Excel để trống/null theo lát.
- Test tương đương K1–K6 và ghi rõ sai khác một cờ K6 khi so bản gốc chạy đủ K7.
- EX-0: khung hai năng lực (tạm `CHUA_LAM`), cổng SDK có nhật ký an toàn.
- Kiểm tệp/ZIP/XML và trần trước openpyxl; bộ DEMO tự ghi công thức và giá trị lưu.

- EX-4: đọc khuôn `xay_dung_klgt`, giữ nhận diện/nhóm/khóa gốc; số dùng Decimal,
  giữ số tổng hợp 0 và số lẻ nhỏ, trả trường §4.2 và JSON §5.2 trong RAM.
- Ba cảnh báo: thành tiền lệch KL × đơn giá, số dạng chữ, khóa trùng; dừng ở Cộng.
- Tiền tệ lấy từ tham số hoặc đơn vị ghi rõ trong bảng; chưa rõ thì trường tiền null,
  JSON giữ số thập phân kèm đơn vị null; không mặc định VND. DEMO thứ ba chạy được.
