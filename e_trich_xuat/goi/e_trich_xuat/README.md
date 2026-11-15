# Trích thông tin hợp đồng — TX-2, bản 0.3.0

Gói công bố **`trich.doc_docx@1`** (`tep` DOCX → `van_ban_tai_lieu`) và
**`trich.chuan_bi@1`** (`van_ban_tai_lieu` → một `yeu_cau_ai` phiên bản 1).
Hậu kiểm và xuất JSON/Excel thuộc TX-3, chưa đăng ký.
Phần đã chạy test: **đã kiểm bằng Core giả (CoreGia)**; chưa nối Core thật.

## Chuẩn bị yêu cầu AI — TX-2

Core cấp `tham_so` riêng cho từng việc; không sửa tham số quy trình chung
để truyền từng hợp đồng. Bộ và prompt thuộc module. Thiếu bộ hoặc prompt
thì từ chối; không có bộ XD/prompt dự phòng.

| Tham số | Quy ước |
|---|---|
| `bo_tham_so_json`, `bam_bo_tham_so` | Chuỗi snapshot và `sha256:<hex>` trên đúng bytes UTF-8 của chuỗi, trước parse; không strip/tuần tự hóa lại để băm |
| `ma_prompt`, `phien_ban_prompt`, `prompt` | Module cung cấp đủ ba giá trị; hai mã 1–200 ký tự ASCII chữ/số/`_.:-`; giữ nguyên prompt rồi nối giao thức dẫn chứng và danh sách mã/mô tả |
| `model_uu_tien` | Chuỗi model hoặc bỏ trống; đầu ra bỏ trống thành `null`; không tự chọn model |
| `ma_truong_can_trich_json` | Mặc định `[]` = mọi mã đang dùng theo thứ tự bộ; danh sách con giữ thứ tự yêu cầu, từ chối mã lạ/trùng/ngừng dùng |
| `yeu_cau_them_json` | Chỉ nhận `[]`; chưa duyệt mức 5, không sửa bộ để thêm câu hỏi |
| `ngan_sach_token_vao` | Mặc định đề xuất 16.000; số nguyên dương không vượt trần cấu hình engine, không hạ ngầm khi trần thay đổi |

Snapshot có `phien_ban: 1`, `module`, `loai_hop_dong`, `phien_ban_bo`,
`cac_dong`, `quy_tac`. Ba mã metadata không rỗng, tối đa 200 ký tự ASCII
chữ/số/`_.:-`; không mặc định loại hợp đồng. Mỗi dòng đủ đúng 10 khóa E1:
`ma, nhom, mo_ta, tk, bk, dung, muc, bat_buoc, loai_tru, luon_cloud`.
`dung`/`luon_cloud` là boolean, `muc` là integer 0–3, các cột khác là chuỗi.
Giữ thứ tự và cả dòng ngừng dùng; `luon_cloud` là cột nguồn, không bật Cloud.
`quy_tac` là mảng quy tắc E1 dạng `{kieu, ma_tham_so: [...], dieu_kien,
doi_chieu}`; rỗng nếu không có. Không nhận khóa snapshot/dòng/quy tắc ngoài
quy ước này, khóa JSON lặp, NaN/Infinity, số không hữu hạn hoặc mã trùng.

Bộ kiểm dòng `kho_tri_thuc_sdk.danh_muc_tham_so.kiem_tra_danh_muc` kiểm
các dòng/quy tắc; engine chỉ chuyển cột boolean sang Có/Không để gọi E1.
`ma_bam_noi_dung` (tùy chọn trong snapshot) phải khớp 64 chữ hex do E1
trả về trên 10 cột chuẩn hóa. `bam_tep_goc` (tùy chọn, `sha256:<hex>`) chỉ
là băm XLSX do module ghim, TX-2 không đọc XLSX để chứng thực nó.
Hai băm đó khác `bam_bo_tham_so` của snapshot có cả metadata/quy tắc.
Chuỗi JSON không canonical vẫn được kiểm trên đúng bytes đã gửi.

Khuôn draft 2020-12 dùng `$defs`, bắt buộc đúng mọi mã được chọn và đủ
`gia_tri, don_vi, ghi_chu, trich_dan` trong mỗi ô. Dẫn chứng gồm `cau`
nguyên văn và offset Unicode `[bat_dau, ket_thuc)` trong đúng toàn văn;
không dùng byte/UTF-16 hoặc bịa trang. Chưa có căn cứ thì giá trị `null`,
dẫn chứng `[]`. Chuẩn bị chưa chứng nhận kết quả model; TX-3 kiểm lại từng ô.

| Giới hạn TX-2 | Giá trị |
|---|---:|
| Snapshot JSON UTF-8 / dòng đang dùng trong cả bộ | 64 KiB / 200 |
| Prompt cuối cùng, gồm giao thức/danh sách / toàn văn | 20.000 / 500.000 ký tự |
| Khuôn JSON UTF-8 / chuyển tiếp JSON UTF-8 | 32 KiB / 64 KiB |
| Chuyển tiếp thông thường, mục tiêu | ≤ 4 KiB |

Vượt trần từ chối, không cắt ô, bỏ trang, chọn top-k hoặc giảm số mã.
`ceil((ký tự prompt + tài liệu + JSON khuôn)/4)` chỉ sàng lọc ước lượng.
Hỏi AI vẫn phải kiểm token/context thực sau khi chọn model và thêm phần bọc,
gồm dự phòng đầu ra/reasoning; phần đó còn cần phối hợp A-TX-01.

Hồ sơ hậu kiểm JSON tạo hoàn toàn trong RAM, tải bằng `viec.tai_tep_ra`.
Hồ sơ giữ nguyên chuỗi/snapshot bộ, bản E1/quy tắc, tham số việc, yêu cầu,
toàn văn đã gửi, chỉ mục Điều/Khoản theo khoảng Unicode, vị trí DOCX/OCR,
các băm và cấu hình/phiên bản đã ghim. Băm yêu cầu trong hồ sơ tính trên
`yeu_cau_ai` trước khi gắn `chuyen_tiep`, tránh vòng tham chiếu băm hồ sơ.
`chuyen_tiep.trich_xuat` chỉ có metadata, băm, tham chiếu hồ sơ và SHA-256
của bytes tệp thực; không có bộ/toàn văn và không gửi phần này vào model.
Không tạo tệp tạm hoặc lưu hồ sơ/bộ trên máy engine.

**Hash không chứng minh quyền.** C-TX-01 cần Core xác nhận quyền module/
pháp nhân, ghim bộ/prompt/cấu hình theo việc; SDK 2.0 chỉ mô phỏng bản chụp
khi bắt đầu handler. C-TX-02 cần quyền/vòng đời đọc tệp xuyên bước trong
cùng chuỗi tới module lưu/đóng, gồm ACL và ACK lặp. Test CoreGia đọc hồ sơ
cũ bằng `mo_tep` qua bước AI giả không chứng nhận quyền/vòng đời Core thật.

## Đọc Word — TX-1

DOCX được Accept All bằng XML trong RAM. Tệp gốc không đổi;
`bam_dau_vao` là SHA-256 bytes gốc. Văn bản giữ thứ tự đoạn/bảng, ô rỗng,
ô gộp, số tự động. Không có dữ liệu phân trang thật nên `so_trang=0`,
`trang=[]`, có cảnh báo vị trí theo đoạn/Điều/Khoản. Trường tùy chọn
`khoi_docx` chứa cây đoạn/bảng/ô, gộp hàng/cột và offset Unicode nửa mở
`[bat_dau, ket_thuc)` trong đúng `van_ban`; không có trang/hộp giả.
Ô gộp chỉ có ô gốc trong danh sách `o`; biểu diễn văn bản để trống các
vị trí tiếp tục gộp, không lặp nội dung ô gốc. Ô rỗng thực sự vẫn có mặt.
Đầu/chân trang, chú thích và hình ảnh/đối tượng nhúng có cảnh báo khi gặp;
không nhận dạng chữ trong ảnh. Schema chung được chép nguyên byte vào `contract/`.

Giới hạn đều từ chối bằng lỗi, không cắt nội dung:

| Giới hạn | Giá trị |
|---|---:|
| Bytes DOCX / thời hạn bước tại Core | 20 MiB / 120 giây |
| Tổng dung lượng giải nén khai báo / một XML | 64 MiB / 16 MiB |
| Số thành phần ZIP / tỷ lệ giải nén | 2.048 / 200:1 |
| Số nút / độ sâu một cây XML | 200.000 / 128 |
| Toàn văn / phong bì kết quả JSON UTF-8 | 500.000 ký tự / 20 MiB |
| Ô / cột bảng / bảng lồng | 50.000 / 256 / 16 mức |

DTD/entity, ZIP có đường không hợp lệ, thành phần trùng, liên kết, mã hóa
hoặc phương pháp nén chưa hỗ trợ bị từ chối. Không chuyển `.doc`, không
dùng Word, không OCR/AI hoặc gọi engine khác. Số lượt Cloud: **0**.
Các DOCX hiếm có `vMerge continue` chứa chữ, `w:tr` không có `w:tc`, hoặc
lệch `gridSpan` bị từ chối **cả tài liệu**, không bỏ riêng dòng/ô lỗi.

## Cấu hình và cổng kiểm

`cau_hinh.schema.json` chỉ là tài nguyên khai cấu trúc. Giá trị nằm trong
bảng `cau_hinh`, phạm vi `engine`, khóa `{}`, giá trị trực tiếp là dict cấu
hình, không hết hạn; cập nhật bằng CAS `row_version`.
Màn `ui/cau_hinh.js` dùng `KttCore.engine("e_trich_xuat").cau_hinh.doc/luu`;
đầu vào/đầu ra cổng màn là `{gia_tri, phien_ban_cau_hinh}`. Export `nap`
(đồng thời default) nhận `{goc, KttCore}` và trả hàm tháo màn. Cần lead Core
review adapter nạp màn trước cài. UI chỉ có trần ngân sách và nút Lưu;
model/IP thuộc Hỏi AI, bộ tham số thuộc module.

Thiếu bản ghi không làm engine chết. DOCX độc lập với ngân sách AI nên hai
DEMO DOCX không cần cấu hình. TX-2 gọi `ghim_cau_hinh(viec, app)` trước xử lý,
trả `CHUA_CAU_HINH` nếu thiếu; chỉ điền mặc định 16.000 vào bản đã có.
Hàm đọc một bản và giữ phiên bản; ưu tiên snapshot SDK 2.1 trên việc nếu có.
SDK 2.1 sẽ tự xử lý `engine.cau_hinh_doi`; thay đổi cấu hình không sửa bản
chụp của việc cũ. Chưa có API/sự kiện này trong SDK 2.0.0.

Khai ngăn/cấu hình/màn dự kiến nằm riêng ở `KHAI-SDK-2.1.json`, không thêm
khóa vào phiếu 2.0. `chon_ngan(app)` ưu tiên `app.ngan`; tạm dùng RAM và cảnh
báo stderr một lần. Khởi động lại sẽ mất cấu hình. Đã nối ngăn chung NGAN-0
(PR #34): hai tệp ngăn/cấu hình giữ nguyên bản chung, test so SHA-256 sau
khi đổi CRLF thành LF. RAM nhận khai báo từ `KHAI-SDK-2.1.json/ngan_du_lieu`.
Không lưu cấu hình/bộ/log/kết quả
trên máy. Đường DOCX không tạo tệp tạm.

SDK 2.0 kiểm MIME/kích thước trước handler với câu lỗi khác phiếu TX-1.
`EngineTrichXuat` kế thừa `Engine.tu_khai_bao`, chỉ bọc `_ket_thuc` để dịch
hai lỗi đó sang lỗi TX-1. `_ghi` chỉ che dòng “Lỗi khi xử lý việc” hoặc
traceback, giữ các dòng SDK có mã lỗi để chẩn đoán vận hành. Khởi động
chặn SDK khác 2.0.0 hoặc chữ ký `_ghi`/`_ket_thuc` đã đổi, chờ review hook.
Vòng việc,
gia hạn, hủy và ACK vẫn do SDK thực hiện. Cần Core cung cấp hook công khai
(C-TX-05); khi nâng SDK phải kiểm lại hai seam này, không sửa SDK/wheel.

Từ gốc repo, dùng `.venv/Scripts/python -B` trên Windows hoặc
`.venv/bin/python -B` trên Linux:

```text
python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat
python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp
python -B e_trich_xuat/tests/kiem_doc_lap.py
python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py
node --test e_trich_xuat/tests/ui/cau_hinh.test.mjs
```

Luôn chạy `-B` hoặc `PYTHONDONTWRITEBYTECODE=1` để giữ gói sạch bytecode.
Test chỉ dùng DEMO, CoreGia, NganBoNho và KttCore giả; không cần mạng.
Ngày 15/11/2026: pytest **164 passed, 0 skipped**; độc lập **exit 0**.
CLI SDK chuẩn **2/3 ĐẠT, exit 1**: DEMO TX-2 trả `CHUA_CAU_HINH` vì CLI
2.0.0 chưa nạp ngăn. Cổng `chay_demo_voi_ngan_gia.py` nạp cấu hình DEMO
qua `NganBoNho` trước `CoreGia.chay_thu_demo`: **3/3 ĐẠT, exit 0**.
Trình lead cổng DEMO có ngăn thay thế trong lúc chờ C-TX-04; không thêm
cờ cấu hình tệp/env hoặc tự cấu hình trong runtime để làm xanh CLI.
Máy kiểm phiên này là Windows; Linux chưa chạy thực tế (WSL chưa cài,
không có Docker). Test dùng API Python/Node đa nền tảng. Core thật chưa kiểm.


## Lõi TX-3 chờ review chi tiết — 15/11/2026

Đã có lõi hậu kiểm và xuất JSON/Excel trong gói nhưng **chưa đăng ký**
`trich.hau_kiem@1`, `trich.xuat_ket_qua@1` hoặc schema
`bang_trich_xuat`. Manifest/runtime hiện vẫn chỉ công bố hai năng lực
TX-1/2. Hướng bảng + Excel đã chốt; xem
[chi tiết review](../../docs/TX-3-REVIEW.md) trước khi đăng ký.

Cổng `tests/chay_demo_voi_ngan_gia.py` ngoài gói chạy ba DEMO runtime có
ngăn và hai DEMO TX-3 trong phiếu RAM chỉ cho test: **5/5 ĐẠT**,
**đã kiểm bằng Core giả (CoreGia)**. CLI SDK chuẩn vẫn **2/3 ĐẠT, exit 1**,
TX-2 thiếu cấu hình ngăn; chờ lead xác nhận cổng thay thế/C-TX-04.
Không tự tạo cấu hình trong engine.

Hậu kiểm hiện giữ `van_ban` vì bộ E1 của TX-2 chưa khai cách chuyển kiểu;
không tự đoán tiền/ngày hoặc tính TT-21. Exporter kiểm và giữ kiểu đã khai
trong bảng: tiền có mã tiền tệ, ngày ISO, số dài bằng text JSON; text không
thành công thức Excel. Tệp JSON là dữ liệu chuẩn để module ghép cột.
Không ghi kết quả/bộ/lịch sử lên máy engine; module quyết định lưu.
