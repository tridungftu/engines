# Tra cứu tài liệu — khung TC-0

Phiên bản 0.1.0, SDK 2.0.0, chỉ dùng nội bộ trước phát hành.
`tra_cuu.kiem_khung@1` nhận tệp JSON, khai đầu ra `truong.trang_thai` kiểu
`van_ban`, nhưng handler luôn báo `CHUA_LAM`: “Chức năng tra cứu đang được hoàn thiện.”
Chưa có quy trình người dùng phụ thuộc stub. Theo lệnh giao TC-0, TC-1 cần xử lý
việc thay stub bằng năng lực đích trước phát hành; phiếu TC-1 hiện chuyển thao tác
đổi manifest/handler sang TC-2. Lead cần thống nhất mốc này, không phát hành stub.
Không khai loại `ho_so_tra_cuu` khi TC-Q13 chưa duyệt.

`chay_thu_demo=[]`: **0 demo, chưa kiểm nghiệp vụ**. Gói chưa có năng lực tra cứu
nghiệp vụ, không có ví dụ thành công giả, không tạo cấu hình DEMO lúc chạy.

## Khởi động và cấu hình

Core khởi động trong thư mục gói bằng `{python} -B -m e_tra_cuu.chay`;
`Engine.tu_khai_bao` kiểm manifest 2.0 và `app.chay()` dùng cổng SDK chung.
Core cần dùng `-B` hoặc `PYTHONDONTWRITEBYTECODE=1` khi chạy gói để tránh bytecode.

`ngan.py`, `cau_hinh.py` chép nguyên mẫu NGAN-0. SDK có `app.ngan` thì giữ nguyên;
thiếu mới gắn một `NganBoNho(khai_bao)` dùng lại trong tiến trình. Cảnh báo RAM ra
stderr một lần; khởi động lại mất dữ liệu. Không tệp cấu hình/sổ/cache bền,
không Cloud, không kết nối mạng ngoài, không SQL hoặc gọi engine khác.

Giá trị cấu hình là một bản ghi `cau_hinh`, khóa `{}`, trong ngăn.
Schema và bản khai SDK 2.1 là metadata chỉ đọc, không phải nơi lưu giá trị cấu hình.
`yeu_cau_cau_hinh(ngan)` dành cho handler cần cấu hình ở các lát sau:

- Thiếu bản ghi: `CHUA_CAU_HINH`, câu hướng dẫn Admin vào Cấu hình; khởi động vẫn được.
- Sai kiểu/trường/trần: `CAU_HINH_KHONG_HOP_LE`; ngoại lệ ngăn đổi sang lỗi SDK an toàn.
- Bản ghi phải có `phien_ban=1` và `quy_tac_nhom={tep_id,bam}`; băm dạng SHA-256.
  Tham chiếu/băm không tự chứng minh quyền hoặc nguồn hợp lệ; kiểm nguồn ở TC-2.
- Default chỉ điền trên bản sao sau khi có bản ghi. `phan_loai.trang_thai=chua_do`
  không có số ngưỡng mặc định. `da_do` phải có `nguong` và `bam_bo_do`;
  trạng thái chưa đo không được mang hai trường này. Metadata này chưa chứng nhận
  chất lượng hoặc cho phép kích hoạt nhóm nghiệp vụ (TC-Q15).
- `cat_doan` mặc định mục tiêu 2000 ký tự, đơn vị tối đa 8000, tối đa 5000 đoạn;
  mục tiêu không vượt trần đơn vị. `ngan_sach` chứa các trần thiết kế phiếu §2.3,
  chỉ cho giảm. Đây chưa là số đo token/context/model thực tế.

Khi cần CAS dùng `ngan.doc("cau_hinh", {})` lấy `row_version`.
`phien_ban` là phiên bản cấu trúc cấu hình, khác phiên bản CAS.
Ghim cấu hình/row_version nhất quán theo từng việc thuộc TC-2.

## Bản khai dự kiến SDK 2.1

`KHAI-SDK-2.1.json` tách khỏi manifest 2.0:

- `cau_hinh`: phạm vi engine, khóa rỗng, không unique bổ sung.
- `dot_kiem`: phạm vi pháp nhân, khóa `ma_dot`, unique `[phap_nhan_id,ma_dot]`;
  chỉ metadata/băm, tử số/mẫu số trong `chi_so`, tham chiếu+băm báo cáo Core.
  Không ghi câu hỏi/nguyên văn, không đặt TTL khi chính sách chưa duyệt.
- Hai màn dự kiến `ui/cau_hinh.js`, `ui/trang_thai.js`, quyền `admin_core`;
  **chưa có mã UI**, làm ở TC-9, dùng `KttCore.engine("e_tra_cuu")` và Core kiểm quyền.

Mọi thao tác `dot_kiem` phải có pháp nhân tin cậy trong `khoa/loc` từng lệnh,
ưu tiên `viec.ngan`; RAM dùng view cùng pháp nhân. Ngăn gốc RAM phục vụ test,
không thay phân quyền Core. Không dùng cursor đổi bảng/bộ lọc/pháp nhân.

## Kiểm từ gốc repo

Python >=3.11. Tạo `.venv` bằng `python -m venv --system-site-packages .venv`
để dùng pytest 9.1.1 có sẵn; không tải mạng. Cài SDK từ wheel trong repo:

```powershell
.venv/Scripts/python -B -m pip install --no-index --no-deps --find-links docs/goi-gui-engine/sdk-2.0.0 --require-hashes -r e_tra_cuu/goi/e_tra_cuu/requirements.lock
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
```

Linux đổi `Scripts/python` thành `bin/python`, đặt hai biến môi trường tương ứng.
Test chặn mạng, chỉ DEMO. Stub và cổng cấu hình **đã kiểm bằng Core giả (CoreGia)**;
handler kiểm cấu hình chỉ đăng ký trong test, không thay stub runtime.
CAS/unique/rollback/pháp nhân/cursor kiểm trực tiếp trên `NganBoNho`.
Symlink của bộ quét kiểm bằng giả lập cờ, không yêu cầu Windows cấp quyền tạo symlink.
Chưa kiểm Core thật, lưu bền, UI thật hoặc Linux.

**Kết quả CLI thực tế SDK 2.0.0:** đã kiểm/nạp được phiếu nhưng in
`Phiếu chưa có ví dụ chay_thu_demo.` và trả **mã 1** khi danh sách rỗng.
Vì TC-0 bắt buộc giữ 0 demo, cổng CLI mã 0 của AGENTS.md §5 **chưa đạt**.
Không sửa SDK, thêm demo thành công giả hoặc coi mã 1 là đạt.
Cần Core C-TC-01 bổ sung cách kiểm khung không demo ở bản SDK sau;
pytest và kiểm độc lập đã trả 0, chi tiết trong VIEC.md. Chưa nghiệm thu nghiệp vụ.
