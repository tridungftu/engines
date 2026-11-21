# Phân luồng kiểm tra — 0.1.0

Engine SDK 2.2.0 chia từng nghiệp vụ theo khâu vào Đỏ (cần người kiểm trước khi duyệt) hoặc Xanh, kèm lý do. Năm năng lực đã chạy thật trong bộ kiểm DEMO; đã kiểm bằng Core giả (CoreGia), chưa kiểm tích hợp Core thật.

## Trình soạn Cài đặt bước TS-PL — 21/11/2026

`ui/tham_so.js` dùng chung cho cả năm năng lực: danh mục loại, bộ phân loại,
ngưỡng PM/TE/SAD, chính sách và khuôn cột. Chỉ hiện ô được khai cho năng lực:
hóa đơn không có khuôn cột; ghi kết quả không có bộ phân loại/khuôn cột.
Mỗi ý là ô riêng, có hướng dẫn và mẫu; JSON trong Nâng cao chỉ đọc.
Nút **Chèn mẫu DEMO** chỉ điền thẻ đang chọn; **Bỏ thiết lập** xuất chuỗi rỗng,
giữ nguyên ý nghĩa mặc định của engine. **Kiểm tra cài đặt** không chạy nghiệp vụ,
không gọi máy/dịch vụ. TS-PL không có cấu hình engine hoặc bí mật để nhập.

Các cấu trúc JSON hiện hành (có mô tả ngắn và mẫu ở `mo_ta` trong
`engine.json`, dành cho ô văn bản chung khi Core chưa nạp được màn):

SDK 2.2.0 giới hạn `mo_ta` ở 500 ký tự, nên phần diễn giải đầy đủ từng cấp
được giữ trong bảng dưới và phần chính sách Admin. Core cần cửa D2 để hiển thị
biểu mẫu/hướng dẫn đầy đủ ngay nơi sửa bước; mô tả rút gọn chưa thay được cửa này.

| Tham số | Cấu trúc, bắt buộc, hướng dẫn và nghĩa khi trống |
|---|---|
| `danh_muc_loai_json` | Danh sách ≤ 100 đối tượng, mỗi dòng đủ `ma` (chuỗi chữ thường/số/gạch dưới, bắt đầu bằng chữ, ≤ 40, duy nhất, không dùng `chua_phan_loai`), `ten` (chuỗi không trống), `mo_ta` (chuỗi, cho rỗng). Trống tham số = danh mục rỗng. |
| `bo_phan_loai_json` | Đối tượng đủ `phien_ban: 1` (số nguyên), `quy_tac: []`. Mỗi quy tắc đủ `loai` (mã có trong danh mục), `khi` (danh sách ≥ 1 điều kiện nối HOẶC). Điều kiện có `tat_ca` (≥ 1 nhóm, mỗi nhóm ≥ 1 chuỗi từ khóa, HOẶC trong nhóm, VÀ giữa nhóm), `khong_co` (danh sách chuỗi loại trừ, tùy chọn = []). `=từ` khớp nguyên từ; `#` khớp ≥ 1 chữ số; không regex. Tối đa 200 từ mỗi quy tắc. Quy tắc xét từ trên xuống, khớp đầu tiên thắng. Trống = không có quy tắc. |
| `nguong_json` | Đối tượng có `pm`, `te`, `sad`; mỗi khối bắt buộc có `so` (số hoặc chuỗi thập phân dương, ≤ 18 chữ số nguyên, ≤ 6 chữ số lẻ), `tien_te` (3 chữ hoa). Cùng tiền tệ, `0 < SAD < TE ≤ PM`. Tệp có ngưỡng thì tệp thắng; trống tham số thì tệp phải gửi đủ ngưỡng. Màn giữ chính xác từng chữ số tiền, không chuyển tiền qua JavaScript Number. |
| `chinh_sach_json` | Đối tượng ghi đè từng khóa, tất cả tùy chọn; chỉ dùng số JSON, không chuỗi/boolean. Trống hoặc `{}` = mặc định. Các khóa, kiểu, điều kiện và mặc định ở bảng chính sách Admin bên dưới; `he_so` ghi đè từng cờ. Khi sửa thang bậc phải sửa đồng thời ngưỡng xuống và số mẫu. |
| `khuon_cot_json` | Đối tượng đủ `phien_ban: 1` (nguyên), `sheet` (chuỗi tên hoặc null = tự dò), `cot` (1–30 dòng), `dong_dung` (danh sách chuỗi, có thể []). Mỗi cột đủ `ma` (trường, không trùng), `tu_khoa` (danh sách tiêu đề không rỗng), `bat_buoc` (boolean). Phải có `ma`, `ngay`, `so_tien` và bật bắt buộc. Trường được phép ở bảng khuôn cột bên dưới; `thuoc_tinh.<khóa>` thêm thuộc tính. Tối đa 200 từ khóa cả dòng dừng; khớp ô có nội dung đầu tiên của dòng thì dừng. Trống chỉ dùng được cho JSON; Excel/CSV cần khuôn. |

Mẫu DEMO đủ năm ô (điền riêng giá trị từng khóa, không nhập cả đối tượng vào một ô):

```json
{
  "danh_muc_loai_json": [{"ma":"thanh_toan_demo","ten":"Thanh toán DEMO","mo_ta":"Thanh toán nhà cung cấp DEMO"}],
  "bo_phan_loai_json": {"phien_ban":1,"quy_tac":[{"loai":"thanh_toan_demo","khi":[{"tat_ca":[["thanh toán","=chi"],["đợt #"]],"khong_co":["hủy"]}]}]},
  "nguong_json": {"pm":{"so":"5000000000","tien_te":"VND"},"te":{"so":"3000000000","tien_te":"VND"},"sad":{"so":"250000000","tien_te":"VND"}},
  "chinh_sach_json": {"ty_le_duoi_sad":0.02,"mau_sach_toan_bo":30,"he_so":{"NGAY_NGHI":1.5}},
  "khuon_cot_json": {"phien_ban":1,"sheet":null,"cot":[{"ma":"ma","tu_khoa":["Mã"],"bat_buoc":true},{"ma":"ngay","tu_khoa":["Ngày"],"bat_buoc":true},{"ma":"so_tien","tu_khoa":["Số tiền"],"bat_buoc":true},{"ma":"tien_te","tu_khoa":["Tiền tệ"],"bat_buoc":false}],"dong_dung":["Tổng cộng"]}
}
```

Khi gửi việc, giá trị của mỗi khóa trên là **chuỗi JSON**, như hợp đồng cũ.
Giới hạn ký tự/byte được kiểm ngay trên màn, không cắt nội dung. Chuỗi chưa sửa
được giữ nguyên từng byte; các khóa ngoài năm ô này cũng được giữ nguyên.
Sửa/xóa mã loại không tự đổi quy tắc: màn đánh dấu tham chiếu cần sửa.

### Nhúng vào màn bước Core (cửa D2, hợp đồng dự kiến)

Khai dự kiến ở `KHAI-SDK-2.1.json`; SDK 2.2.0 chưa nhận
`giao_dien_tham_so`, vì vậy không đưa khóa này vào `engine.json`.
Core nạp `ui/tham_so.css`, import ES module rồi gọi:

```js
const man = await mount(goc, {
  KttCore,
  nang_luc: "audit.phan_luong@1",
  tham_so,                       // snapshot ban đầu, cả các ô khác của bước
  phien_ban_tham_so,             // số nguyên không âm, CAS của bước/quy trình
  doc_tham_so,                   // () => Promise<{tham_so, phien_ban_tham_so}>
  luu_tham_so                    // (tham_so, phien_cu) => Promise<{phien_ban_tham_so}>
});
const giaTri = man.getValue();   // ném lỗi có danh sách trường sai nếu chưa hợp lệ
man.validate();                 // [{truong, duong_dan, thong_diep}]
man.destroy();                  // rời màn: xóa DOM, bỏ phản hồi muộn
```

`doc_tham_so`/`luu_tham_so` là callback **đề nghị** của màn bước, chưa phải API
SDK đã phát hành. Core kiểm quyền Admin, giới hạn/kiểu và CAS khi ghi bước;
trả phiên bản mới lớn hơn phiên cũ, 409 hoặc `NGAN_XUNG_DOT`/`THAM_SO_XUNG_DOT`
khi tranh chấp. Màn giữ nháp, khóa Lưu và yêu cầu Tải lại. Lỗi đọc/lưu không
đưa thông điệp kỹ thuật ra màn; không nhận phiên mới thì không báo đã lưu.
Thiếu callback, phiên CAS hoặc `KttCore.engine` thì chỉ soạn/kiểm, khóa Lưu.
Không dùng `cau_hinh.luu`/`ngan.ghi_lo` để lưu tham số của từng bước vào engine.
Màn không gọi mạng, không tạo API riêng; chỉ nhận cổng của chính engine.

Đã kiểm bằng Core giả (CoreGia), chưa kiểm tích hợp Core thật. Bộ Node chạy
`node --test e_phan_luong/tests/ui/tham_so.test.mjs`; pytest gọi lại bộ Node và
đối chiếu JSON với các bộ đọc Python hiện hành. Ảnh DEMO và cách dựng ở
`e_phan_luong/tests/ui/README.md` (ngoài gói).

## Dành cho người viết module

| Năng lực | Nhận → trả | Cách dùng |
|---|---|---|
| `audit.phan_luong@1` | `tep` → `truong` | JSON, Excel .xlsx, CSV UTF-8; module gán loại hoặc dùng quy tắc |
| `audit.chuan_bi_phan_loai@1` | `tep` → `yeu_cau_ai` | Quy tắc trước, chuẩn bị nội dung chưa khớp cho Local AI |
| `audit.phan_luong_sau_ai@1` | `tra_loi_ai` → `truong` | Kiểm kết quả AI và tham chiếu lô rồi phân luồng |
| `audit.phan_luong_hoa_don@1` | `truong` → `truong` | Sau `hoa_don.doc_xml@2` hoặc `hoa_don.doc_zip@1` |
| `audit.ghi_ket_qua@1` | `tep` → `truong` | Nhận JSON kết quả người kiểm, cập nhật thống kê |

Mỗi khâu có nút/quy trình riêng, ví dụ `ktt_duyet`. Module giữ chi tiết giao dịch và đầu vào gốc, ghép trường trả về khi `quy_trinh.xong`. Người lập không xem luồng; người duyệt chỉ xem luồng, lý do và chứng từ thuộc quyền mình. Module thực thi quyền và yêu cầu mở cảnh báo trước nút Duyệt. Trường ra, JSON và Excel dành cho người duyệt không chứa tỷ lệ, xác suất hay bậc (C5).

Module lập Blob JSON, gửi multipart bằng `api.goi({tep: new File([blob], "lo-DEMO.json")})` tới `POST /api/v1/module/{ma}/nut/{nut}/chay`; khai `nhan_tep.mime` của nút có `application/json`. Cách tạm này dùng khi SDK trình duyệt 2.2.0 chưa có `nut.chay`.

### Đầu vào và đầu ra

JSON lô tối thiểu (mọi giá trị dưới đây là DEMO):

```json
{"phien_ban":1,"ma_module":"demo_thanh_toan","ky":"2026-11",
 "nguong":{"pm":{"so":"5000000000","tien_te":"VND"},
           "te":{"so":"3000000000","tien_te":"VND"},
           "sad":{"so":"250000000","tien_te":"VND"}},
 "nghiep_vu":[{"ma":"PC-DEMO-0001","ngay":"2026-10-30",
 "so_tien":{"so":"1000000","tien_te":"VND"},
 "doi_tac":"DEMO-NCC-01","dien_giai":"Thanh toán DEMO",
 "loai":null,"nhap_tay":false,"co_do_cung":false,"thuoc_tinh":{}}]}
```

`ma_module`, `ma`, `ngay`, `so_tien` bắt buộc; mã không trùng trong lô. `ma` dài 1–120, không ký tự điều khiển. Ngày `YYYY-MM-DD`; tiền là chuỗi thập phân, tối đa 18 chữ số nguyên và 6 chữ số lẻ, luôn kèm mã tiền tệ. Số âm so theo trị tuyệt đối (Q3). Có thể thêm `so_tien_quy_doi`, `tai_khoan_no`, `tai_khoan_co`, nội dung mở rộng trong `thuoc_tinh`. Khối `nguong` trong tệp ưu tiên hơn `nguong_json`; phải cùng tiền tệ và `0 < SAD < TE <= PM`. Không tự gán VND: thiếu đơn vị hoặc quy đổi thì dòng Đỏ `CHUA_RO_TIEN_TE` / `CHUA_QUY_DOI`.

Excel đọc giá trị đã lưu (`read_only`, `data_only`), không tính công thức; CSV UTF-8 có/không BOM, dấu `,` hoặc `;`. Đặt `ma_module`, `nguong_json`, `khuon_cot_json`; không nhận `.xls` cũ hoặc PDF. Khuôn cột xem phần Admin. Excel có thể đã mất chữ số sau khoảng 15 chữ số có nghĩa; dùng JSON chuỗi thập phân khi cần giữ chính xác.

Các bước phân luồng trả `ma_luot`, `luong`, `can_nguoi_kiem`, `canh_bao` (≤ 500 ký tự), `so_nghiep_vu`, `so_do`, `so_do_bat_buoc`, `so_do_chon_mau`, `so_xanh`, `so_chua_phan_loai`, `tong_tien_do`, `tep_json`, `tep_ds_do`, `bam_hat_giong`, `bam_dau_vao`, `phien_ban_engine`. `tep_json` chứa từng mã, luồng, lý do, cờ, loại, nguồn loại; `tep_ds_do` là Excel các dòng Đỏ, có cột trống ghi kết quả kiểm và loại đúng, không có Đỏ thì `null`. `tong_tien_do` cộng tiền so ngưỡng theo trị tuyệt đối; có dòng Đỏ chưa so được tiền tệ thì `null`. Phong bì trả `{"loai":"truong","truong":{...}}`; trường tệp là đối tượng `{tep_id, ten, mime, kich_thuoc}` do Core giữ.

### Chuỗi mẫu

```text
(a) JSON/Excel/CSV → audit.phan_luong@1 → trường ngăn module
(b) JSON/Excel/CSV → audit.chuan_bi_phan_loai@1
    → ai.hoi_theo_yeu_cau@1 → audit.phan_luong_sau_ai@1 → trường ngăn module
Hóa đơn XML → hoa_don.doc_xml@2 → audit.phan_luong_hoa_don@1
Hóa đơn ZIP → hoa_don.doc_zip@1 → audit.phan_luong_hoa_don@1
```

Core điều phối chuỗi (b); engine không gọi engine khác. Hai bước audit dùng cùng khâu, danh mục, quy tắc, ngưỡng và chính sách. Module cung cấp prompt; AI chỉ chọn mã trong danh mục. Nội dung khử trùng trước gửi: ≤ 5.000 giá trị; giá trị quá 2.000 ký tự để chưa phân loại, không cắt ngầm. Không cần AI vẫn trả `yeu_cau_ai` rỗng và `khong_can_ai: true`. Sai khuôn/không có căn cứ/tin cậy thấp để dòng chưa phân loại, kèm cảnh báo; nhà cung cấp khác `local` bị từ chối `KHONG_PHAI_LOCAL`.

Giữ **nguyên đối tượng tệp** trong `chuyen_tiep.phan_luong.tep_lo`, cùng `phien_ban: 1`, `bam_tep`, `khau`, `khong_can_ai` trong khối `phan_luong`. Chuyển tiếp mục tiêu ≤ 4 KiB, trần phong bì chung 64 KiB. Core thật đòi đối tượng có khóa `tep_id` và tệp cùng việc; không thay bằng chuỗi ID trơn.

Hóa đơn XML: mã = `mau_so-ky_hieu-so_hoa_don-ma_so_thue_ban` (MST người bán nguyên văn để chống trùng giữa người bán; thiếu MST thì mã ba phần — Q12, Anh duyệt 21/11/2026: MST và hóa đơn công khai trên CSDL thuế, ngoại lệ C4 chỉ cột `ma`), ngày = `ngay_lap`, tiền = `tong_thanh_toan`, đối tác = `ma_so_thue_ban` (băm trước khi lưu ngăn), `can_kiem_tra: true` thành Đỏ cứng. ZIP mở `chi_tiet_nguon` qua Core; chỉ bỏ/đếm tệp lỗi hoặc không hỗ trợ và cảnh báo nguồn chưa đủ. Đặt `ma_module`, `nguong_json`, `loai_nghiep_vu` thuộc danh mục.

### Kết quả kiểm và nộp lại

```json
{"phien_ban":1,"ma_module":"demo_thanh_toan","ket_qua":[
 {"ma_luot":"PL-DEMO-…","ma":"PC-DEMO-0001","khau":"ktt_duyet",
  "ket_qua":"dat","so_tien_sai":{"so":"0","tien_te":"VND"},"loai_dung":null,"giai_thich":null}]}
```

`ket_qua` nhận `dat`, `sai`, `khong_kiem`. Dòng `sai` bắt buộc có `so_tien_sai` cùng tiền tệ ngưỡng; module quy đổi trước khi gửi (Q7). Gửi kèm `nguong` như lô hoặc đặt `nguong_json` ở bước ghi kết quả (Q1). Loại/nguồn loại đọc từ `dong_luot` (Q2); `loai_dung` nếu sửa phải thuộc danh mục. Kết quả tính cho loại đúng và đếm sai loại theo nguồn để Admin sửa quy tắc/prompt. Người kiểm, ghi chú, chứng từ giữ ở module.

**AI sai (Q13–Q16, Anh chốt 21/11/2026):** AI đã kiểm 100% trước bước này; tỷ lệ của engine là tỷ lệ giao người kiểm lại. Dòng `sai` mà AI chưa gắn cờ (`CO_DO_CUNG`) là **AI bỏ sót** → đổi bậc như phiếu (lên bậc ngay, trần 30% cho lỗi nhỏ, ≥ SAD về 30% + `rui_ro_cao`, ≥ TE 100%). Dòng AI đã gắn cờ mà sai thật là AI đúng → không đổi bậc (vẫn cộng thống kê rủi ro 12 tháng). Hạ bậc Clopper-Pearson giữ nguyên. AI bỏ sót hoặc AI phân loại sai (`loai_dung` khác loại AI gán) bắt buộc có `giai_thich` (≤ 2.000 ký tự; Excel cột "Giải thích"), thiếu → `THIEU_GIAI_THICH`, từ chối cả tệp trước khi ghi. Giải thích không lưu trong ngăn; chỉ đi sang tệp bài học.

Trả `so_dong_nhan`, `so_trung`, `so_ngoai_mau`, `so_cap_doi_bac`, `so_sua_loai`, `so_ai_sai`, `tep_bai_hoc`, `phien_ban_engine`. `tep_bai_hoc` (JSON, schema `tests/schema/tep_bai_hoc.schema.json`) là danh sách AI sai cho Admin: mã, loại, loại đúng, nguồn loại, nguồn mẫu, mức sai, giải thích, `da_ghi_truoc` khi gửi lại; không có AI sai thì `null`. Trùng (lượt, mã, khâu) bỏ qua và đếm; mã ngoài lượt ghi nguồn ngoài mẫu; lượt không tồn tại bị từ chối. `so_cap_doi_bac` chỉ là số cặp đã đổi, không tiết lộ bậc từng cặp.

Q5: xét lần hoàn tất gần nhất của cùng (module, khâu, mã). Đỏ chưa có kết quả `dat`/`sai` giữ Đỏ `NOP_LAI`; `khong_kiem` chưa giải phóng. Đã kiểm hoặc lần trước Xanh thì xét bình thường ở việc mới. Kết quả ẩn sau 365 ngày vẫn được tra để giải phóng trong thời gian lượt còn giữ 400 ngày. Core giao lại cùng việc dùng lại lượt và quyết định.

## Cài đặt và chính sách — chỉ dành cho Admin

Python ≥ 3.11; SDK `>=2.2.0 <3.0.0`. Cài wheel SDK đã đối chiếu SHA256SUMS bằng `pip install --no-index --no-deps <wheel-sdk>`, rồi:

```sh
python -m pip install --no-index --find-links <kho-wheel-offline> --require-hashes --no-deps -r requirements.lock
```

Core cài gói và migration `sql/001_tao_ngan.sql`, giữ cấu hình/dữ liệu trong ngăn theo pháp nhân; engine không kết nối CSDL, không lưu sổ/cấu hình/đệm bền trên máy. Không thêm pháp nhân vào khóa bảng. Một việc đồng thời; 20 MiB/tệp, 50.000 dòng/lô, 300 giây/bước (chưa có số đo Core thật). XLSX: ≤ 2.048 ZIP entry, 128 MiB giải nén, 250.000 ô, 500.000 ô trong vùng khai báo. Vượt trần từ chối, không cắt ngầm.

| Khóa Cài đặt bước | Giới hạn / mặc định | Dùng khi |
|---|---|---|
| `khau` | Bắt buộc 1–40, mã chữ thường/số/gạch dưới | Cả 5 năng lực |
| `ma_module` | ≤ 31; `^[a-z][a-z0-9_]*$`; rỗng | JSON lấy từ tệp; bảng/hóa đơn cần đặt |
| `nguong_json` | ≤ 4.096 ký tự; rỗng | Tệp thắng cấu hình; cần nếu không có trong tệp |
| `danh_muc_loai_json` | ≤ 16.384; rỗng; ≤ 100 loại | `[{ma,ten,mo_ta}]`, mã ≤ 40; không khai `chua_phan_loai` |
| `truong_phan_loai` | ≤ 60; rỗng | `dien_giai`, `tai_khoan_no`, `tai_khoan_co`, `thuoc_tinh.<khóa>` |
| `bo_phan_loai_json` | ≤ 32.768, 32 KiB; rỗng | Quy tắc xét theo thứ tự, khớp đầu tiên thắng |
| `chinh_sach_json` | ≤ 8.192, 8 KiB; rỗng = mặc định | Chính sách Admin bên dưới |
| `ty_le_duoi_sad` | 0–1; 0,02 | JSON chính sách ưu tiên hơn khóa bước |
| `cua_so_chia_nho_ngay` | Số nguyên ≥ 1; 7 | Các bước phân luồng |
| `khuon_cot_json` | ≤ 32.768, 32 KiB; rỗng | Đọc Excel/CSV |
| `tien_te` | ≤ 3, mã 3 chữ hoa; rỗng | Bảng thiếu cột tiền tệ, không mặc định |
| `ma_prompt`, `phien_ban_prompt`, `prompt` | Rỗng; cần cung cấp khi chuẩn bị AI | Chỉ `chuan_bi_phan_loai`; phiếu chưa đặt trần riêng |
| `model_uu_tien` | Rỗng | Chỉ `chuan_bi_phan_loai`, model Local |
| `nguong_tin_cay` | 0–1; 0,7 | Chỉ `phan_luong_sau_ai` |
| `loai_nghiep_vu` | Rỗng, mã phải trong danh mục | Chỉ hóa đơn |

Bước `ghi_ket_qua` chỉ khai `khau`, `ma_module`, `nguong_json`, `danh_muc_loai_json`, `chinh_sach_json`; dùng đúng tập khóa mỗi năng lực trong `engine.json`.
Quy tắc mẫu: `{"phien_ban":1,"quy_tac":[{"loai":"thanh_toan_ncc","khi":[{"tat_ca":[["thanh toan"]],"khong_co":[]}]}]}`. So bỏ dấu/chữ thường; `=tu` nguyên từ, `#` một hoặc nhiều chữ số, không regex. Module gán loại hợp lệ ưu tiên hơn quy tắc, rồi AI.

Khuôn cột phải có đủ bốn khóa `phien_ban`, `sheet`, `cot`, `dong_dung`;
`sheet: null` để dò sheet, tối đa 30 cột và 200 từ khóa tổng cộng. Ví dụ DEMO:

```json
{"phien_ban":1,"sheet":null,"cot":[
 {"ma":"ma","tu_khoa":["Mã"],"bat_buoc":true},
 {"ma":"ngay","tu_khoa":["Ngày"],"bat_buoc":true},
 {"ma":"so_tien","tu_khoa":["Số tiền"],"bat_buoc":true},
 {"ma":"tien_te","tu_khoa":["Tiền tệ"],"bat_buoc":false}],
 "dong_dung":["Cộng","Tổng cộng"]}
```

Có thể ánh xạ thêm `so_tien_quy_doi`, `tien_te_quy_doi`, `loai`, `doi_tac`,
nội dung, cờ hoặc `thuoc_tinh.<khóa>`. Ngày chuỗi nhận ISO hoặc DD/MM/YYYY.

### `chinh_sach_json` (Admin)

JSON object chỉ nhận các khóa sau; giá trị số là số JSON, không chuỗi/boolean. Khóa vắng giữ mặc định; khóa lạ/trùng hoặc giá trị sai bị từ chối.

| Khóa | Mặc định | Điều kiện |
|---|---|---|
| `bac` | `[0.30,0.20,0.10,0.05]` | Giảm nghiêm ngặt trong (0,1] |
| `nguong_xuong` | `[0.10,0.05,0.03]` | [0,1], dài bằng số bậc trừ 1 |
| `mau_toi_thieu` | `[30,60,100]` | Số nguyên dương, dài như `nguong_xuong` |
| `ty_le_chua_phan_loai` | 0,30 | [0,1]; cố định ở vùng chọn mẫu, không xuống bậc |
| `mau_sach_toan_bo` | 30 | Số nguyên dương |
| `nguong_diem_rui_ro` | 0,10 | [0,1] |
| `do_tin_cay` | 0,95 | (0,1), cận trên một phía Clopper-Pearson |
| `he_so` | Hai cờ đầu ×2, bốn cờ sau ×1,5 | Object theo mã cờ dưới đây, mỗi hệ số ≥ 1 |
| `don_vi_so_tron` | 10000000 | Số nguyên dương, đơn vị tiền ngưỡng |
| `ty_le_duoi_sad` | 0,02 | [0,1]; ghi đè khóa bước cùng tên |
| `san` | 0,05 | [0,1], sàn vùng chọn mẫu |
| `toi_thieu_ho_so_doi_tac_moi` | 0 | Số nguyên ≥ 0 |

Các cờ: `SO_TIEN_BAT_THUONG` (trên phân vị 95, cần ≥ 50 nghiệp vụ), `DOI_TAC_MOI`, `SO_TRON`, `NGAY_NGHI`, `CUOI_KY` (3 ngày cuối tháng), `NHAP_TAY`. Mặc định `toi_thieu_ho_so_doi_tac_moi = 0`: lượt đầu coi mọi đối tác có mã là mới; ví dụ `{"toi_thieu_ho_so_doi_tac_moi":50}` để đợi đủ lịch sử. Đối tác đã gặp trong 12 tháng không mang cờ mới.

Tiền ≥ TE bắt buộc Đỏ (≥ PM có lý do riêng). Vùng SAD ≤ tiền < TE: `p = min(1, max(san, p_bac × tích hệ số))`. Dưới SAD luôn `p = min(1, ty_le_duoi_sad × tích hệ số)` (Q4), kể cả cặp đang kiểm toàn bộ (Q10) hoặc chưa phân loại (Q11). Chế độ 100% và mức cố định 30% của `chua_phan_loai` chỉ áp vùng chọn mẫu.

Kết quả kiểm cập nhật ngay cho lượt sau: chỉ mẫu ngẫu nhiên đã kiểm dùng ước lượng xuống bậc, cần đủ mẫu từ lần đổi bậc và cận trên đạt ngưỡng. Lỗi nhỏ lên một bậc; lỗi ≥ SAD về bậc đầu và nhãn rủi ro cao; lỗi ≥ TE kiểm toàn bộ tới đủ 30 mẫu sạch. Đang kiểm toàn bộ, chỉ lỗi ≥ TE đặt lại bộ đếm sạch (Q6). Lỗi ngoài mẫu về bậc đầu và gắn nhãn. `chua_phan_loai` không đổi bậc/chế độ. Admin đổi thang: bậc cũ không còn trong thang được đưa tới bậc gần nhất không thấp hơn, không dùng mẫu cũ để xuống ngay; toàn thang thấp hơn bậc cũ thì kiểm toàn bộ.

### Hồ sơ hành vi và kiểm toán (Admin)

Chia nhỏ gom tiền tuyệt đối theo băm đối tác và ngày qua mọi loại trong cùng khâu, mặc định 7 ngày; đối tác cùng mã ở module khác có băm khác. Khoản riêng dưới TE nhưng tổng đạt TE bị `NGHI_CHIA_NHO`. Q8: không khử trùng riêng dòng nộp lại trong việc mới. Đây là giới hạn đã được Anh chốt; TE do Admin quản lý. Phân biệt với Core giao lại **cùng việc**, dùng dấu hoàn tất `luot` tránh cộng hai lần.

Hồ sơ hành vi được cộng trong **CÙNG lô nguyên tử với dấu `luot`**; Core giao lại việc không cộng hai lần. Chỉ khi một lô có **trên 99 loại**, phần dư ghi trước, không nguyên tử; phần dư không có cùng bảo đảm chống cộng lại khi lỗi giữa chừng. `dong_luot` ghi trước theo lô ≤ 100; `luot` ghi sau cùng. Xung đột CAS đọc lại/thử lại tối đa 3 lần, quá mức trả `NGAN_BAN`, cho phép thử lại.

Q9: tối đa **20.000 đối tác mỗi (khâu, loại)**; bỏ đối tác lâu không gặp nhất (hòa kỳ thì theo băm), ghi số đã bỏ vào log kỹ thuật và thêm câu cảnh báo vào `canh_bao` của lượt. Lịch sử chống chia nhỏ chỉ cộng khoản < TE và bỏ ngày nghiệp vụ sau ngày xử lý + 1 (giờ Việt Nam). Hồ sơ ghi tiền tệ ngưỡng; lô sau có ngưỡng khác tiền tệ thì bỏ số liệu tiền cũ, giữ tập đối tác, kèm cảnh báo. Ngăn giữ `luot`, `dong_luot` 400 ngày; kết quả kiểm 365 ngày. Hồ sơ chỉ giữ biểu đồ tiền gộp, băm đối tác, tổng theo băm/ngày cửa sổ gần nhất; không giữ chi tiết giao dịch, diễn giải, mã đối tác thô (C4). Đầu tháng theo giờ Việt Nam chốt tháng trước: bản chụp `chot_ky`, tính lại số 12 tháng, làm mới hồ sơ cùng lô nguyên tử; chỉ chốt một lần.

Kiểm toán viên cần hạt giống gốc 32 byte trong `luot` (chỉ Admin), đầu vào, snapshot chính sách và trạng thái ngăn trước lượt do module giữ:

```python
from hashlib import sha256
from fractions import Fraction
hat_giong = bytes.fromhex(luot["hat_giong"])
raw = (hat_giong + b"\x1f" + ma_module.encode("utf-8")
       + b"\x1f" + khau.encode("utf-8") + b"\x1f" + ma.encode("utf-8"))
h = int.from_bytes(sha256(raw).digest(), "big")
duoc_chon = Fraction(h, 2**256) < Fraction(p)
```

`p` là Decimal/phân số, không float; không dùng trực tiếp 64 ký tự hex làm hạt giống. `bam_hat_giong = "sha256:" + SHA256(hat_giong)`; các mã không có ký tự điều khiển nên không chứa dấu phân cách `0x1f`. `bam_dau_vao = "sha256:" + SHA256(bytes_dau_vao)`; `ma_luot = "PL-" + SHA256(UTF8("e_phan_luong|luot|" + viec.id + "|" + bam_dau_vao))`. Cùng việc hoàn tất dùng lại hạt giống/quyết định; cùng đầu vào, việc, hạt giống, trạng thái trước lượt tái hiện từng byte.

## Lỗi cho người dùng (§7)

| Mã | Câu tiếng Việt |
|---|---|
| `TEP_KHONG_HO_TRO` | Chỉ nhận tệp JSON, Excel .xlsx hoặc CSV UTF-8. |
| `DU_LIEU_KHONG_HOP_LE` | Dữ liệu nghiệp vụ chưa đúng mẫu. Vui lòng kiểm tra lại tệp gửi. |
| `THIEU_NGUONG` | Chưa có ngưỡng PM/TE/SAD hợp lệ cho kỳ này. Quản trị viên cần nhập ngưỡng. |
| `THAM_SO_KHONG_HOP_LE` | Cài đặt bước chưa đúng. Quản trị viên kiểm tra lại cài đặt của quy trình. |
| `KHONG_PHAI_LOCAL` | Bước phân loại chỉ nhận kết quả từ AI nội bộ. |
| `CHUOI_KHONG_KHOP` | Không khớp dữ liệu giữa các bước. Vui lòng chạy lại kiểm tra cảnh báo. |
| `LUOT_KHONG_TON_TAI` | Không tìm thấy lượt phân luồng. Vui lòng chạy lại kiểm tra cảnh báo. |
| `NGAN_BAN` | Dữ liệu thống kê đang được cập nhật. Vui lòng thử lại sau ít phút. |
| `VUOT_GIOI_HAN` | Tệp vượt giới hạn xử lý. Vui lòng tách lô nhỏ hơn. |
| `THIEU_GIAI_THICH` | Dòng AI kiểm sai cần ghi giải thích để AI học từ lỗi. Vui lòng điền cột Giải thích rồi gửi lại. |

## Đang chờ Core

- **CC-1:** phát hành `nut.chay` trong SDK; kiểm multipart/Blob/nút JS trên Core tập. CoreGia chỉ kiểm byte JSON, chưa chứng minh nút thực tế.
- **CC-2:** CoreGia cần khớp quyền/phạm vi cùng việc/pháp nhân khi mở tệp chuyển tiếp; chạy thật chuỗi ba bước và ZIP hóa đơn trên Core tập. Kiểm hình dạng `tep_id` nghiêm không thay kiểm quyền thật.
- **CC-3:** hạt giống hiện là trường thường chỉ Admin đọc. Muốn mã hóa cần đường giải mã Core phục vụ kiểm toán, chưa tự đổi sang trường bí mật.
- **CC-4:** vướng CLI với demo rỗng là lịch sử PL-0/PL-1, đã có ví dụ thật từ PL-2; không còn chặn đóng gói hiện hành.
- **CC-5:** màn Admin bảng tỷ lệ `ui/bang_ty_le.js` chỉ đọc. SDK 2.2.0 từ chối `giao_dien_quan_tri`, chưa có `KttCore.engine(ma)`; màn dừng an toàn. Cần phát hành cơ chế gắn màn/cổng ngăn và lead nối cảnh báo Q9; chưa xác nhận Admin xem được bảng trên Core thật.
- **CC-7:** engine chỉ hậu kiểm `nha_cung_cap = local` trên `tra_loi_ai`; `yeu_cau_ai` chung chưa có khóa bắt buộc Local để Core từ chối TRƯỚC khi gửi (quy ước `nha_cung_cap_bat_buoc` hiện chỉ có ở hồ sơ Mask). Bước AI của Core cấu hình nhầm Cloud thì diễn giải đã rời máy trước khi engine báo `KHONG_PHAI_LOCAL`. Cần cửa chung ở Core.
- **Giới hạn đã biết:** Core giao lại việc trong lúc lần đầu còn chạy (quá `thoi_han_giay`) thì hai lần chạy có thể sinh hai hạt giống; `luot` và tệp ra theo lần ghi dấu trước, `dong_luot` có thể theo lần sau. Giao lại SAU khi lượt xong thì luồng và lý do giữ nguyên bản đã lưu; cột `co` tính lại theo hồ sơ mới nên có thể khác lần đầu.
- **CC-6 (không còn chặn):** `viec.ngan.tim` chỉ lọc bằng (=), chưa có `ma IN [...]`. Từ PL-9F/9H/9I engine không còn đọc ngăn từng dòng: dò rỗng một lần, quét trang 500 dòng theo lượt/khâu với ngân sách ceil(số mã/10) trang, vượt ngân sách mới quay về đọc từng mã. Đo trên ngăn giả có chỉ mục (PL-9G, 21/11): 50.000 dòng phân luồng 526–631 lần gọi Core, engine thuần 10–24 giây; ghi kết quả 50.000 dòng 723–1.130 lần gọi, engine thuần 3–10 giây. **Ước tính, chưa đo trên Core thật**, giả định 10 ms/lần gọi: ≤ 31 giây, dưới hạn 300 giây. Lô ghi 100 lệnh hoặc trang 500 dòng trên Core thật có thể chậm hơn 10 ms; cần đo một lần trên Core tập. Lọc `IN` ở Core vẫn giảm thêm số trang quét khi lịch sử lớn.
- **Giới hạn đã biết (PL-9F/9I):** khi quét, engine giữ trong RAM các dòng lịch sử của chính các mã trong lô (không giữ mã khác); mã nộp lại nhiều lần làm bộ nhớ tăng theo số lần. Ghi kết quả dùng bản đọc chống trùng lấy trước ở lần thử đầu; việc khác ghi chen cùng khóa thì lô xung đột, lần thử lại đọc từng khóa nên không ghi trùng, chỉ tốn thêm một lần thử.

## Kiểm và đóng gói

Từ gốc repo, đặt `PYTHONDONTWRITEBYTECODE=1`, dùng Python của `.venv`:

```sh
python -B e_phan_luong/tests/kiem_bam_goi.py --cap-nhat
python -B -m kho_tri_thuc_sdk.thu e_phan_luong/goi/e_phan_luong
python -B -m pytest e_phan_luong/tests -q
KIEM_SAU=1 python -B -m pytest e_phan_luong/tests -q
python -B e_phan_luong/tests/kiem_doc_lap.py
sh e_phan_luong/tests/kiem_may_sach.sh <kho-wheel-offline>
```

Lệnh pytest mặc định là **kiểm nhanh**, chạy mỗi lần sửa: giữ 20 trạng thái đầu
cùng hạt giống của PL-9F/9H/9I và mọi ca biên cố định. Các ca đánh dấu `sau`
tự bỏ qua với lý do "kiểm sâu: đặt KIEM_SAU=1". Lệnh có `KIEM_SAU=1` là
**kiểm sâu**, chạy đủ 240 trạng thái và các ca quy mô lớn/hiệu năng.
PowerShell dùng `$env:KIEM_SAU="1"` trước lệnh pytest; trở về kiểm nhanh bằng
`Remove-Item Env:KIEM_SAU`. CI luôn chạy kiểm sâu; lead chạy kiểm sâu trước khi
xin gộp main, hoặc yêu cầu chạy khi cần.

Linux CI yêu cầu Python 3.11; Git Bash dùng được khi `PYTHON` trỏ Python 3.11. Windows: Anh tự chạy `e_phan_luong\tests\KIEM-MAY-SACH.cmd <kho-wheel-offline>`. Script tạo venv tạm, cài offline theo hash, chép gói, kiểm dependency/kiểm kê/DEMO/độc lập. Adapter `test_pl9c_dong_goi.py --kiem-ke` gọi `kiem_bam_goi.kiem` có sẵn; không cần kiểm kê ngoài gói thứ hai. Môi trường thử giữ lại cho việc xem bằng chứng, không đưa vào git.

ZIP thử bytes worktree dùng chính `kiem_ten`, `kiem_ke_sql`, `tao_zip` của `_chung/cong-cu/dong_goi.py`:
`python -B e_phan_luong/tests/test_pl9c_dong_goi.py --dong-goi-thu <thư-mục-mới-ngoài-repo>`.
Lead sau commit chạy CLI phát hành từ bytes git:
`python -B _chung/cong-cu/dong_goi.py --engine e_phan_luong --ref HEAD --nhan PL-9 --ra <thư-mục-mới-ngoài-repo>`.
Không gọi ZIP từ HEAD cũ là bản phát hành của worktree chưa commit.
