# Phân luồng kiểm tra — PL-2

Engine chia nghiệp vụ vào luồng Đỏ (người phải kiểm trước khi duyệt)
hoặc Xanh theo khâu, ngưỡng PM/TE/SAD, loại nghiệp vụ và chọn mẫu tái hiện được.
**PL-2 đã nối `audit.phan_luong@1` cho JSON**: phân loại module/quy tắc,
ngưỡng, chống chia nhỏ trong lô, tỷ lệ theo khâu × loại, cờ và chọn mẫu.
Excel/CSV trả `TEP_KHONG_HO_TRO` tới PL-6. Bốn năng lực còn lại trả
`CHUA_LAM`: “Năng lực đang được xây dựng.” Hồ sơ hành vi và chốt kỳ
chờ PL-4; hiện không suy cờ đối tác mới/số tiền bất thường khi chưa có hồ sơ.

| Năng lực | Nhận → trả | Phạm vi |
|---|---|---|
| `audit.phan_luong@1` | tep → truong | PL-2: phân luồng lô JSON; Excel/CSV chờ PL-6 |
| `audit.chuan_bi_phan_loai@1` | tep → yeu_cau_ai | Quy tắc trước, chuẩn bị dòng chờ Local AI |
| `audit.phan_luong_sau_ai@1` | tra_loi_ai → truong | Hậu kiểm phân loại AI rồi phân luồng |
| `audit.phan_luong_hoa_don@1` | truong → truong | Nối sau bước đọc hóa đơn |
| `audit.ghi_ket_qua@1` | tep → truong | Nhận kết quả kiểm, cập nhật thống kê |

Giới hạn khai báo: 20 MiB/tệp, 300 giây/bước (tạm, chưa đo), một việc đồng thời.
Tiền luôn kèm mã tiền tệ; không tự gán VND khi thiếu. Dữ liệu giữ lại đi qua
`viec.ngan` của Core; không tệp cấu hình, sổ hoặc bộ đệm bền trên máy engine.
Ngăn theo pháp nhân, không lưu chi tiết số tiền/ngày/đối tác/nội dung giao dịch.
`dong_luot` có `loai`, `nguon_loai` theo quyết định Q2 ngày 20/11/2026.

Trường ra đủ phiếu §5.5. `tep_json` có mã, luồng, lý do, cờ, loại và nguồn
loại từng dòng; metadata gồm mã lượt, khâu, module, phiên bản và các băm.
`canh_bao` chỉ gồm câu lý do cố định, tổng dưới 500 ký tự. `tep_ds_do = null`
tới PL-8: SDK 2.2.0 cho phép trường tệp không có giá trị. `tong_tien_do`
cộng tiền so ngưỡng (đã quy đổi nếu có, theo trị tuyệt đối); một dòng Đỏ
chưa so được tiền tệ làm tổng là `null`. Không dòng Đỏ thì tổng bằng không,
kèm tiền tệ ngưỡng.

Luật nộp lại Q5: đọc lượt hoàn tất gần nhất theo `luot.tao_luc` của cùng
(module, khâu, mã). Đỏ chưa có kết quả `dat`/`sai` → `NOP_LAI`;
`khong_kiem` chưa giải phóng. Đã kiểm hoặc lần gần nhất Xanh → xét bình
thường bằng hạt giống mới khi Core giao một việc mới. Kết quả kiểm đã ẩn
sau 365 ngày vẫn được đọc để giải phóng Đỏ trong thời gian lượt còn giữ
400 ngày; `khong_kiem` vẫn chưa giải phóng.

Core giao lại **cùng việc** dùng cùng mã lượt, tính bằng UTF-8:
`ma_luot = "PL-" + sha256("e_phan_luong|luot|" + viec.id + "|" + bam_dau_vao).hexdigest()`,
trong đó `bam_dau_vao = "sha256:" + sha256(bytes_dau_vao).hexdigest()`.
Đọc `luot(ma_luot)` trước khi chọn mẫu: đã có thì dùng lại
`bytes.fromhex(luot["hat_giong"])`; chưa có thì sinh hạt giống mới. Khi tra
`NOP_LAI`, bỏ qua chính mã lượt của việc hiện tại. Lượt đã hoàn tất đọc lại
quyết định từ `dong_luot`, giữ nguyên kết quả khi tỷ lệ/lịch sử nộp lại đã
đổi; cờ được tính từ đầu vào và bản chụp chính sách của việc. Cùng hạt giống, đầu vào,
`viec.id` và trạng thái ngăn trước lượt cho cùng tệp kết quả từng byte.

Ghi từng lô tối đa 100 dòng, rồi ghi `luot` sau cùng. Dòng mới dùng
`lay_hoac_tao`; nếu `dong_luot` đã có nhưng chưa có dấu hoàn tất `luot`,
sửa bằng CAS (`sua`, `row_version`) theo quyết định hiện tại. Lần chạy dở
có thể dùng hạt giống khác khi chạy lại; toàn bộ dòng cũ được sửa trước khi
ghi dấu hoàn tất, không lẫn quyết định giữa hai lần. Lượt đã hoàn tất giữ
nguyên các dòng ngăn khi Core giao lại.

Admin đổi thang bậc: bậc đã lưu không còn trong thang mới được đưa về bậc
gần nhất không thấp hơn, không dùng mẫu tích lũy của bậc cũ để xuống ngay.
Nếu cả thang mới thấp hơn bậc đã lưu, chuyển chế độ kiểm toàn bộ (100%).

## Công thức để kiểm toán viên chạy lại

Lấy hạt giống 32 byte từ 64 ký tự hex ở ngăn `luot` (chỉ Admin được xem),
đầu vào gốc và phiên bản engine/chính sách tại thời điểm chạy. Mã hóa các mã
bằng UTF-8, giữ nguyên thứ tự byte và dấu phân cách `0x1f`:

```python
from hashlib import sha256
from fractions import Fraction

hat_giong = bytes.fromhex(luot["hat_giong"])
raw = (hat_giong + b"\x1f" + ma_module.encode("utf-8")
       + b"\x1f" + khau.encode("utf-8") + b"\x1f" + ma.encode("utf-8"))
h = int.from_bytes(sha256(raw).digest(), "big")
duoc_chon = Fraction(h, 2**256) < Fraction(p)
```

`p` phải lấy bằng Decimal/phân số, không qua float. Vùng chọn mẫu:
`p = min(1, max(san, p_bac × tích hệ số cờ))`; dưới SAD:
`p = min(1, ty_le_duoi_sad × tích hệ số cờ)` (mặc định 0,02).
Lớp ngưỡng/cờ bắt buộc và luật nộp lại được áp riêng trước chọn mẫu.
`ma_module` và `khau` đã kiểm dạng mã thường/số/gạch dưới trong
`phan_luong.py`; `ma` đã kiểm không có ký tự điều khiển trong `doc_lo.py`.
Do đó các mã không thể chứa dấu phân cách `0x1f`. Dùng bytes 32 byte để
chọn; không dùng chuỗi hex 64 ký tự làm hạt giống trực tiếp. Khi kiểm lại
phải giữ cùng trạng thái ngăn trước lượt (đặc biệt tỷ lệ và lịch sử nộp lại).
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

## Tự kiểm PL-2

Chạy ba lệnh AGENTS.md bằng Python của venv, đặt `PYTHONDONTWRITEBYTECODE=1`
để không tạo bytecode trong gói. `chay_thu_demo` chạy
`demo/lo-nho-DEMO.json` với khâu `ktt_duyet`, danh mục, bộ quy tắc và
trường phân loại DEMO trong Cài đặt bước; ngưỡng nằm trong tệp.
Pytest chạy lô 500 dòng, C4/C5, Q2/Q4/Q5, khứ hồi hex/bytes, thứ tự ghi
và tái hiện từng byte trên cùng đầu vào/hạt giống/trạng thái ngăn.
Mọi kết quả này đã kiểm bằng Core giả (CoreGia), chưa nối Core thật.
Sau mọi thay đổi gói (kể cả demo PL-0B), tính lại kiểm kê bằng
`python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat` từ gốc repo.
