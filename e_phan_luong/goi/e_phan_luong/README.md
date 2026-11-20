# Phân luồng kiểm tra — PL-0

Engine dự kiến chia nghiệp vụ vào luồng Đỏ (người phải kiểm trước khi duyệt)
hoặc Xanh theo khâu, ngưỡng PM/TE/SAD, loại nghiệp vụ và chọn mẫu tái hiện được.
**PL-0 chỉ dựng khung**: mọi năng lực hiện trả lỗi `CHUA_LAM`:
“Năng lực đang được xây dựng.” Chưa có ví dụ `chay_thu_demo` chạy được.

| Năng lực | Nhận → trả | Mục đích sau khi triển khai |
|---|---|---|
| `audit.phan_luong@1` | tep → truong | Phân luồng lô JSON/Excel/CSV |
| `audit.chuan_bi_phan_loai@1` | tep → yeu_cau_ai | Quy tắc trước, chuẩn bị dòng chờ Local AI |
| `audit.phan_luong_sau_ai@1` | tra_loi_ai → truong | Hậu kiểm phân loại AI rồi phân luồng |
| `audit.phan_luong_hoa_don@1` | truong → truong | Nối sau bước đọc hóa đơn |
| `audit.ghi_ket_qua@1` | tep → truong | Nhận kết quả kiểm, cập nhật thống kê |

Giới hạn khai báo: 20 MiB/tệp, 300 giây/bước (tạm, chưa đo), một việc đồng thời.
Tiền luôn kèm mã tiền tệ; không tự gán VND khi thiếu. Dữ liệu giữ lại đi qua
`viec.ngan` của Core; không tệp cấu hình, sổ hoặc bộ đệm bền trên máy engine.
Ngăn theo pháp nhân, không lưu chi tiết số tiền/ngày/đối tác/nội dung giao dịch.
`dong_luot` có `loai`, `nguon_loai` theo quyết định Q2 ngày 20/11/2026.

## Công thức để kiểm toán viên chạy lại (triển khai ở các lát sau)

Lấy hạt giống 32 byte từ 64 ký tự hex ở ngăn `luot` (chỉ Admin được xem),
đầu vào gốc và phiên bản engine/chính sách tại thời điểm chạy. Mã hóa các mã
bằng UTF-8, giữ nguyên thứ tự byte và dấu phân cách `0x1f`:

```python
from hashlib import sha256
from fractions import Fraction

raw = (hat_giong + b"\x1f" + ma_module.encode("utf-8")
       + b"\x1f" + khau.encode("utf-8") + b"\x1f" + ma.encode("utf-8"))
h = int.from_bytes(sha256(raw).digest(), "big")
duoc_chon = Fraction(h, 2**256) < Fraction(p)
```

`p` phải lấy bằng Decimal/phân số, không qua float. Vùng chọn mẫu:
`p = min(1, max(san, p_bac × tích hệ số cờ))`; dưới SAD:
`p = min(1, ty_le_duoi_sad × tích hệ số cờ)` (mặc định 0,02).
Lớp ngưỡng/cờ bắt buộc và luật nộp lại được áp riêng trước chọn mẫu.
Băm hạt giống là `sha256:<SHA256(hat_giong)>`. Để chạy lại cần hạt giống gốc,
không chỉ băm; C4 không cho lưu chi tiết đầu vào trong ngăn engine nên module
phải giữ đầu vào và snapshot chính sách phục vụ kiểm toán.
Kết quả cho người duyệt không mang tỷ lệ, xác suất hay bậc. Riêng
`ghi_ket_qua.so_cap_doi_bac` là số cặp đã đổi, theo phiếu §5.5, không phải bậc.

## Nhúng module và điều kiện Core

Mỗi khâu dùng một nút/quy trình riêng. Module tự lập Blob JSON, gửi multipart
bằng `api.goi({tep: new File([blob], "lo-DEMO.json")})` tới
`POST /api/v1/module/{ma}/nut/{nut}/chay`; nút khai `nhan_tep.mime` có
`application/json`. SDK trình duyệt 2.2.0 chưa có `nut.chay`.
Phân quyền người lập/người duyệt/Admin thuộc module và Core.

Chuỗi Local AI do Core điều phối; engine không gọi engine khác. Giữ nguyên
đối tượng tệp `{tep_id, ten, mime, kich_thuoc}` do `tai_tep_ra` trả ở
`chuyen_tiep.phan_luong.tep_lo`, cùng băm tệp, khâu và cờ `khong_can_ai`.
Core thật đòi đối tượng có khóa `tep_id` và tệp cùng việc. CoreGia 2.2.0
chỉ so chuỗi con trong đầu vào và kho tệp toàn cục; test hình dạng nghiêm
không chứng nhận quyền/vòng đời tệp ở Core thật. Cần chạy thật Blob và
chuỗi ba bước trên Core tập; đã kiểm bằng Core giả (CoreGia).

## Tự kiểm PL-0

Chạy ba lệnh AGENTS.md bằng Python của venv, đặt `PYTHONDONTWRITEBYTECODE=1`
để không tạo bytecode trong gói. `kho_tri_thuc_sdk.thu` báo
“Phiếu chưa có ví dụ chay_thu_demo.”, mã thoát 1: không coi là DEMO đạt.
Pytest kiểm hợp đồng/tiện ích ngăn; không thay cho nghiệm thu nghiệp vụ.
Sau mọi thay đổi gói (kể cả demo PL-0B), tính lại kiểm kê bằng
`python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat` từ gốc repo.
