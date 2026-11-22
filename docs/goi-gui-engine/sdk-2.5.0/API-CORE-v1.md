# API Core v1 cho module và engine

Nguồn: HOP-DONG-CONG.md bản 1.22 và hợp đồng lô 2; cửa module ↔ quy trình đối chiếu K138/K139 tại `da565ee` (cập nhật SDK 2.3.0 ngày 18/11/2026, KQ-NUT). Tài liệu này trích các hợp đồng tích hợp dành cho người viết module và engine; các ví dụ dùng dữ liệu giả.

## Mục lục

1. [Quy ước và lỗi](#1-quy-ước-và-lỗi)
2. [Manifest module 2.0](#2-manifest-module-20)
3. [Manifest engine 2.0 và dữ liệu](#3-manifest-engine-20-và-dữ-liệu)
4. [API engine](#4-api-engine)
5. [Quy trình, nút và Việc của tôi](#5-quy-trình-nút-và-việc-của-tôi)
6. [Thông báo](#6-thông-báo)

## 1. Quy ước và lỗi

Các khóa JSON dùng tiếng Việt không dấu, `snake_case`; URL dùng dấu gạch nối. Ngày giờ dùng ISO 8601 có múi giờ; ngày hiển thị dạng `dd/mm/yyyy`, tiền kèm mã tiền tệ. Manifest module và engine dùng `phien_ban_manifest: 2`. Gói không chứa mật khẩu, khóa hoặc địa chỉ, đường dẫn cố định của máy.

Lỗi API, SDK và thông báo dùng phong bì phẳng:

```json
{"ma":"QUY_TRINH_DA_DOI","thong_diep":"Quy trình vừa được người khác sửa. Mở lại để xem bản mới.","request_id":"abc","thu_lai_duoc":false,"chi_tiet":{}}
```

`chi_tiet` là tùy chọn. Giao diện giữ nguyên `thong_diep` từ máy chủ, không xưng hô; chỉ hiện thông điệp, còn `ma` và `request_id` nằm trong phần thu gọn “Chi tiết hỗ trợ”. Thông điệp không chứa dữ liệu nghiệp vụ, đường dẫn hoặc khóa.

| Mã | HTTP | Ý nghĩa |
|---|---:|---|
| `MAT_LEASE` | 409 | Engine không còn quyền giữ lượt việc. |
| `QUA_THOI_HAN` | — | Bước vượt thời hạn; Core đánh dấu lỗi và thu quyền giữ việc. |
| `QUY_TRINH_DA_AP_DUNG` | 409 | Quy trình đã áp dụng, không sửa trực tiếp. |
| `QUY_TRINH_DA_DOI` | 409 | Phiên bản quy trình đã thay đổi. |
| `QUY_TRINH_NOI_KHONG_KHOP` | 422 | Kiểu dữ liệu giữa các bước không khớp; `chi_tiet.loi` chứa `{buoc, thong_diep}`. |
| `QUY_TRINH_KHONG_HOP_LE` | 422 | Quy trình không hợp lệ. |
| `QUY_TRINH_KHONG_TIM_THAY` | 404 | Không tìm thấy quy trình. |
| `VIEC_KHONG_CHAY_LAI_DUOC` | 409 | Việc không thể chạy lại. |
| `GAN_NUT_DA_DOI` | 409 | Phiên bản cấu hình gắn nút đã thay đổi. |
| `GHEP_KHONG_HOP_LE` | 422 | Ghép trường không hợp lệ; `chi_tiet.loi` chứa `{dong, thong_diep}`, dòng 0 là lỗi chung. |

Module khai báo mã lỗi nghiệp vụ trong manifest. Khi mã chưa khai, Core dùng thông điệp chung và giữ mã trong chi tiết hỗ trợ.

## 2. Manifest module 2.0

Manifest khai báo giao diện, quyền, hành động, lỗi, dữ liệu, contract và nút. Ví dụ rút gọn dưới đây minh họa cấu trúc; các khối khai báo được mô tả tiếp bên dưới:

```json
{
  "phien_ban_manifest": 2, "loai": "module", "ma": "demo_ho_so", "ten": "Hồ sơ DEMO", "phien_ban": "1.0.0",
  "tuong_thich": {"core": ">=2.0.0 <3.0.0", "sdk": ">=2.0.0 <3.0.0"},
  "goi": {"tep_kiem_ke": "KIEM-KE.json", "thuat_toan_ma_bam": "sha256", "phu_thuoc_module": []},
  "backend": {"diem_vao": "backend.chay"},
  "tien_trinh": {"cong": {"nguon": "core_cap", "pham_vi": "loopback"}, "readiness": "kenh_dieu_khien", "thu_hoi": "drain_va_xac_nhan", "bi_mat": "stdin_hoac_handle", "ranh_giay_de_xuat": 300, "nhan_listener": "socket.fromshare", "che_do_mac_dinh": "tu_kich_hoat_tu_dong"},
  "giao_dien": {"diem_vao": "frontend/chinh.js", "tai_nguyen": ["frontend/chinh.js"], "trang_dau": "tong_quan", "phan": [{"ma": "tong_quan", "ten": "Tổng quan", "quyen_xem": "ho_so.xem"}]},
  "quyen": [{"ma": "ho_so.xem", "ten": "Xem hồ sơ"}, {"ma": "ho_so.lap", "ten": "Lập hồ sơ"}],
  "hanh_dong": [{"ma": "lap_ho_so", "ten": "Lập hồ sơ", "phuong_thuc": "POST", "duong_dan": "/ho-so", "quyen": "ho_so.lap", "dau_vao": "schema/lap_vao.v1.json", "dau_ra": "schema/lap_ra.v1.json", "kieu": "dong_bo", "chong_trung": true, "sdk_dung": ["ngan.them"]}],
  "ma_loi": [{"ma": "HO_SO_KHONG_TIM_THAY", "http": 404, "thong_diep": "Không tìm thấy hồ sơ."}],
  "du_lieu": {"ngan": [{"ma": "ho_so", "ten": "Hồ sơ", "cot": [{"ma": "noi_dung", "ten": "Nội dung", "kieu": "van_ban"}]}], "goi_migration": null},
  "contract": {"cong_bo": [], "su_kien_phat": [], "su_kien_nhan": []},
  "nut": [{"ma": "doc_tep", "ten": "Đọc tệp", "phan": "tong_quan", "thao_tac_dau": "tai_tep", "nhan_tep": {"mime": ["text/plain"], "toi_da_mib": 20}, "ngan_ket_qua": "ho_so", "quyen": "ho_so.lap", "sdk_dung": ["ngan.them"]}]
}
```

- `ma` khớp `^[a-z][a-z0-9_]{2,30}$`. `giao_dien.tai_nguyen` phải chứa `giao_dien.diem_vao`. Các khóa `tien_trinh.nhan_listener`, `tien_trinh.che_do_mac_dinh` và `goi.phu_thuoc_module` bắt buộc; danh sách phụ thuộc có thể rỗng. Core dùng phiên bản `2.0.0` để kiểm tra tương thích theo hợp đồng này.
- Quyền có dạng `<tai_nguyen>.<dong_tu>`, không gắn mã module; Core tự gắn tiền tố. Động từ chỉ gồm `xem`, `xem_du`, `lap`, `sua`, `kiem`, `duyet`, `huy`. Nút tạo bản ghi dùng `lap`, ghi vào bản ghi có sẵn dùng `sua`.
- Mỗi hành động khai `phuong_thuc`, `duong_dan`, `quyen`, schema đầu vào/ra nếu có, `kieu` là `dong_bo` hoặc `nen`, và `chong_trung`. Route công khai là `/api/v1/module/{ma}{duong_dan}`; đường dẫn có thể chứa `{id}`. Hành động nền trả `{"viec_id":"..."}`. Với `chong_trung: true`, gửi header `Idempotency-Key`; khóa lặp trả đúng câu trả lời đầu tiên, kể cả 4xx. Sau 4xx dứt khoát phải dùng khóa mới.
- Core kiểm phiên, trạng thái module, hành động, quyền và schema trước khi chuyển yêu cầu cho module; sau đó kiểm đầu ra. Hành động không khai trả 404. Khi cần chỉ rõ đối tượng quyền, khai `doi_tuong` với `ngan` và `id_tu` như `duong_dan.id` hoặc `than.ho_so_id`. `contract` tùy chọn của hành động trỏ tới contract đã công bố. `sdk_dung` liệt kê đúng tên thao tác SDK được dùng, ví dụ `viec.lay`, `tep.tai_len`, `ngan.doc`, `ngan.them`, `ngan.sua`.
- Mỗi ngăn là bảng trong khối riêng của module. Kiểu cột gồm `van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`, `khoa_noi`; `khoa_noi` chỉ tới `ngan_dich` cùng khối. Core thêm cột chuẩn `id`, `phap_nhan_id`, `nguoi_tao`, `tao_luc`, `sua_luc`, `ban_ghi_goc_id`, `da_luu_tru` và áp dụng cách ly theo pháp nhân. Không khai các cột chuẩn này.
- Pháp nhân được chọn trong từng module; Core giữ danh sách chung người dùng và pháp nhân để các module dùng lại.
- `contract.cong_bo[]` gồm `ma`, `phien_ban`, `schema`, `vi_du`, `truong[]`, `quyen_doc`, `ngan`; có thể khai `su_kien_phat[]`, `su_kien_nhan[]`. `quyen_doc` dùng mã quyền trong module.
- Module khai chỗ đặt nút; quản trị viên gắn quy trình và bảng ghép bên ngoài gói. Đánh dấu `data-ktt-nut="<ma_nut>"` hoặc gọi `sdk.nut.dat(ma_nut, phan_tu)`; nếu không đánh dấu, Core đặt nút ở thanh thao tác của phần. Chỉ nút đã gắn quy trình đang dùng và người dùng có quyền mới hiện.

**SDK 2.3.0 — khai đọc tệp kết quả (C-RV-01):** mã nút tối đa 32 ký tự, khớp `^[a-z][a-z0-9_]{0,31}$`. Hàm nhận `quy_trinh.xong` muốn liệt kê/đọc tệp phải tự khai `quy_trinh.ds_tep_ket_qua`, `quy_trinh.doc_tep_ket_qua` trong `nut[].sdk_dung` của nút tương ứng; hành động gọi đọc khai trong `hanh_dong[].sdk_dung`. Đây là hai thao tác **đọc**, không thuộc bộ mặc định. Module đã cài phải phát hành lại gói với khai báo mới. Ví dụ đoạn khai báo trong một nút (giữ các thao tác đang dùng):

```json
{"sdk_dung":["ngan.them","quy_trinh.ket_qua","quy_trinh.ds_tep_ket_qua","quy_trinh.doc_tep_ket_qua"]}
```

Ở nút mặc định, Core lọc quyền trước khi vẽ. Với `sdk.nut.dat(ma_nut, phan_tu, {tu_ve:true})`, module tự vẽ và **phải tự ẩn nút khi không có quyền** hoặc chưa có quy trình áp dụng; lấy danh sách nút được phép ở mục 5. Máy chủ vẫn từ chối 403 khi thiếu quyền. Xem cách gửi và nhận `viec_id` tại mục 5.

Backend SDK dùng bảng `{hanh_dong.ma: hàm}`; hàm nhận `yeu_cau` gồm `duong_dan`, `truy_van`, `than`, `ngu_canh` và trả dữ liệu theo schema hoặc ném lỗi nghiệp vụ đã khai. Truy cập ngăn của chính module qua `sdk.ngan(ma).them(dong)`, `.sua(id, dong)`, `.doc(loc, gioi_han, con_tro)`; `loc` là `{cot: gia_tri}` so bằng và kết quả đọc là `{danh_sach, con_tro_tiep}`.

Khi nhận `quy_trinh.xong`, SDK đọc thêm dữ liệu từ Core rồi gọi hàm nhận của module với thân như sau:

```json
{"tep_nut":{"tep_id":"tep-1","ten":"mau.txt","mime":"text/plain","kich_thuoc":12},"ghep":[{"ngan":"ho_so","cot":"noi_dung","gia_tri":"Nội dung"}]}
```

Module tự ghi kết quả và quyết định cột chứa `tep_nut` trong hàm nhận đã đăng ký ở bảng `SU_KIEN` của backend (xem mẫu module). Khai thao tác hàm nhận dùng trong `nut[].sdk_dung`. Module sở hữu nút không cần khai đăng ký nhận `quy_trinh.xong`.

## 3. Manifest engine 2.0 và dữ liệu

```json
{
  "phien_ban_manifest": 2, "loai": "engine", "ma": "e_demo_dem_tu", "ten": "Đếm từ DEMO", "phien_ban": "1.0.0",
  "tuong_thich": {"core": ">=2.0.0 <3.0.0", "api": "v1", "sdk": ">=2.0.0 <3.0.0"},
  "che_do_chay": "cuc_bo", "diem_vao": {"lenh": ["{python}", "-m", "demo.chay"], "thu_muc": "."},
  "nang_luc": [{"ma": "van_ban.dem_tu@1", "ten": "Đếm từ", "nhan": ["van_ban"], "tra": "truong", "truong_ra": [{"ma": "so_tu", "ten": "Số từ", "kieu": "so"}], "gioi_han": {"tep_toi_da_mib": 20, "mime": [], "ky_tu_toi_da": 1000000, "thoi_han_giay": 60}, "huy_duoc": true, "tham_so": [{"ma": "bo_dong_trong", "ten": "Bỏ dòng trống", "kieu": "co_khong", "mac_dinh": true}]}],
  "loai_du_lieu_rieng": [], "tai_nguyen": {"so_viec_dong_thoi": 1}, "readiness": {"thoi_han_giay": 30},
  "chay_thu_demo": [{"nang_luc": "van_ban.dem_tu@1", "ten": "Đếm từ DEMO", "dau_vao": {"loai": "van_ban", "van_ban": "Ví dụ"}, "tham_so": {}}], "bi_mat": [], "webhook": null
}
```

`ma` khớp `^e_[a-z0-9_]{2,29}$`, tối đa 31 ký tự. `che_do_chay` là `cuc_bo` hoặc `tu_xa`; `{python}` là Python do Core chọn, lệnh chạy trong thư mục gói. Engine không nhận thông tin đăng nhập cơ sở dữ liệu. `chay_thu_demo` chỉ chứa dữ liệu giả; `tep_demo`, nếu có, là đường dẫn bên trong gói. `webhook` có thể là `{"url":"...","su_kien":[]}`.

Ba loại gốc là `tep` (tham chiếu tệp trong kho Core), `van_ban` (chuỗi), `truong` (bộ trường có kiểu). Có thể khai `loai_du_lieu_rieng` bằng `{ma, ten}`; Core so khớp mã. Đầu ra bước trước phải nằm trong `nhan` của bước sau; bước đầu nhận tệp từ nút. `truong_ra[].kieu` dùng `van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`. `tham_so` có kiểu `van_ban`, `so`, `co_khong`, `chon`; kiểu `chon` khai `lua_chon` gồm `{ma, ten}`. Các khóa phụ gồm `mac_dinh`, `bat_buoc`, `mo_ta`, `toi_thieu`, `toi_da`.

Phong bì giữa các bước:

```json
{"loai":"tep","tep":{"tep_id":"tep-1","ten":"mau.txt","mime":"text/plain","kich_thuoc":12}}
```
```json
{"loai":"van_ban","van_ban":"Nội dung"}
```
```json
{"loai":"truong","truong":{"so_tu":2}}
```

Loại riêng dùng `{"loai":"<ma>","<ma>":"..."}`. Giá trị tiền là `{"so":100,"tien_te":"VND"}`, ngày là `YYYY-MM-DD`, không có giá trị dùng `null`. Mỗi lượt kèm `tham_so` và `ngu_canh` gồm `viec_id`, `buoc`, `phap_nhan_id`; không chứa thông tin đăng nhập. Giới hạn áp dụng cho đầu vào bước; ràng buộc nghiệp vụ riêng do engine tự kiểm và trả lỗi.

SDK engine có gói import `kho_tri_thuc_sdk`. Ví dụ xử lý một năng lực:

```python
from kho_tri_thuc_sdk.engine import Engine

app = Engine.tu_khai_bao("engine.json")

@app.nang_luc("van_ban.dem_tu@1")
def xu_ly(viec):
    return {"loai": "truong", "truong": {"so_tu": 2}}

app.chay()
```

## 4. API engine

Engine dùng `Authorization: Bearer <khóa engine>`, `X-KTT-Engine: <ma>`, `X-KTT-Instance: <mã phiên chạy>`; lệnh ghi thêm `Idempotency-Key`. Engine chỉ thấy việc của chính mình. Kết nối từ máy khác bắt buộc HTTPS.

Với `cuc_bo`, Core chạy lệnh khai báo trong gói rồi ghi ngay một dòng JSON UTF-8 kết thúc bằng xuống dòng vào stdin:

```json
{"core_url":"<địa chỉ Core>","khoa":"<khóa engine>","instance":"<mã phiên chạy>"}
```

Khi chạy thủ công dùng các biến `KTT_CORE_URL`, `KTT_ENGINE_KHOA`, `KTT_ENGINE_INSTANCE`. Khóa dài 16–512 ký tự ASCII; `instance` khớp `[A-Za-z0-9_.:-]{1,100}`. HTTP chỉ dùng cho địa chỉ loopback; kết nối ngoài máy dùng HTTPS.

| Thao tác | Route | Gửi → nhận |
|---|---|---|
| Sẵn sàng | `POST /api/v1/engine/{ma}/san-sang` | `{instance, phien_ban, nang_luc[]}` → `{cau_hinh}` |
| Nhận việc | `POST /api/v1/engine/{ma}/viec/nhan` | `{cho_toi_da_giay}` → 200 `{viec:{id, nang_luc, dau_vao, tham_so, ngu_canh, han_giu, lan_thu}}` hoặc 204; chờ tối đa 30 giây |
| Đọc đầu vào | `GET /api/v1/engine/viec/{id}/dau-vao` | Phong bì dữ liệu khi không gửi kèm lượt nhận |
| Đọc tệp | `GET /api/v1/engine/viec/{id}/tep/{tep_id}` | Luồng byte |
| Tải tệp kết quả | `POST /api/v1/engine/viec/{id}/tep` | Byte, `X-KTT-Ten-Tep`, `Content-Type` → `{tep_id}`; tên mã hóa percent-encoding UTF-8 |
| Gia hạn | `POST /api/v1/engine/viec/{id}/gia-han` | `{han_giu_giay}` → `{han_giu, huy}` |
| Tiến độ | `POST /api/v1/engine/viec/{id}/tien-do` | `{phan_tram, cau}` → `{huy}` |
| Nộp kết quả | `PUT /api/v1/engine/viec/{id}/ket-qua` | Phong bì dữ liệu → `{da_luu:true}` |
| Kết thúc | `POST /api/v1/engine/viec/{id}/ket-thuc` | `{trang_thai, loi?, ma_tuong_quan?}`; trạng thái `XONG`, `LOI`, `CHUA_RO`, `HUY` |
| Lượt bền | `POST /api/v1/engine/{ma}/luot-ben` | `{thao_tac, ma_tuong_quan, ...}`; thao tác dự kiến `giu`, `chot`, `doc` |

Ví dụ kết thúc lỗi:

```json
{"trang_thai":"LOI","loi":{"ma":"DU_LIEU_KHONG_HOP_LE","thong_diep":"Không đọc được dữ liệu.","thu_lai_duoc":false}}
```

Nộp kết quả và nhận xác nhận ghi bền trước khi kết thúc `XONG`. Hết hạn giữ mà không gia hạn, việc trở lại hàng chờ và tăng lượt thử. `409 MAT_LEASE` tại gia hạn, tiến độ, kết quả hoặc kết thúc nghĩa là engine đã mất quyền giữ việc và phải dừng xử lý lượt đó. Theo dõi `huy` trong phản hồi gia hạn, kể cả khi webhook không tới.

Khi mất quyền giữ, không nộp kết quả hoặc báo kết thúc; SDK cũng xử lý 404/410 như mất quyền giữ. Khi lỗi mạng, 429, 5xx hoặc `thu_lai_duoc: true`, gửi lại tối đa 3 lần với cùng `Idempotency-Key`. SDK xin hạn giữ 60 giây và gia hạn mỗi 20 giây; Core có thể trả hạn ngắn hơn. Quá thời hạn bước, Core kết thúc việc bằng lỗi `QUA_THOI_HAN`. Với kết quả chưa rõ, bản này báo `CHUA_RO` cùng `ma_tuong_quan` ở `ket-thuc`; các thao tác giữ/chốt/đọc lượt bền dành cho giai đoạn sau.

### 4.1 API #11–#15 — ngăn dữ liệu và cấu hình (SDK 2.2)

Các route dưới đây đều trả JSON, thành công là HTTP 200. `{ma}` phải trùng engine đã xác thực. Mọi API dùng ba header chung:

```http
Authorization: Bearer <khóa engine>
X-KTT-Engine: e_demo_ngan
X-KTT-Instance: demo-001
```

POST thêm `Content-Type: application/json`. Khi gọi trong việc, thêm `X-KTT-Viec: <id lượt>`: **giá trị là `viec.id` nhận từ `viec/nhan`** (id lượt giữ `lan_thu.id`), không phải id việc gốc `viec.ngu_canh["viec_id"]`. Core kiểm instance đang giữ lượt rồi tự lấy pháp nhân và việc; không nhận pháp nhân tùy ý trong thân. Không có header thì chỉ dùng được bảng phạm vi `engine`; bảng `phap_nhan` trả 422 `NGAN_CAN_VIEC`. Header nếu có cũng được kiểm ở #14/#15.

Gói khai `ngan_du_lieu[]` cùng `du_lieu.goi_migration`; bảng thường trong `eng_<ma>` phải cài xong. Ví dụ dưới dùng đúng các bảng/trường của `e_demo_ngan` bản 1.1.0. Định dạng phiếu, SQL và kiểm kê ở `engine/MAU-PHIEU-ENGINE.md` mục 11.

### #11. Đọc một bản ghi

**`POST /api/v1/engine/{ma}/ngan/{bang}/doc`**. Header: ba header chung, `Content-Type`; thêm `X-KTT-Viec` khi gọi trong lượt (bắt buộc với `dem_goi`). Không cần `Idempotency-Key`.

Thân: `khoa` là đối tượng không rỗng; `gom_het_han` là boolean, mặc định `false`. Trả `{ban_ghi, row_version}`; không thấy hoặc bị ẩn do hết hạn thì cả hai là `null`.

```http
POST /api/v1/engine/e_demo_ngan/ngan/dem_goi/doc
X-KTT-Viec: <id lượt đang giữ>
```
```json
{"khoa":{"ngay":"2026-11-15"},"gom_het_han":false}
```
```json
{"ban_ghi":{"id":"00000000-0000-0000-0000-000000000001","phap_nhan_id":"00000000-0000-0000-0000-000000000002","row_version":2,"tao_luc":"2026-11-15T10:00:00+07:00","sua_luc":"2026-11-15T10:01:00+07:00","het_han_luc":"2027-02-13T10:01:00+07:00","ngay":"2026-11-15","so_lan":"1","ghi_chu":null},"row_version":2}
```

Bản ghi chứa trường đã khai và `id`, `phap_nhan_id`, `row_version`, `tao_luc`, `sua_luc`, `het_han_luc`. Ngày là `YYYY-MM-DD`, thời điểm ISO 8601 có múi giờ; `so`/`so_tien` là chuỗi thập phân giữ nguyên, tiền có thêm `<ma>_tien_te`. HTTP `row_version` là số nguyên; SDK bọc thành `BanGhi`.

### #12. Tìm và phân trang

**`POST /api/v1/engine/{ma}/ngan/{bang}/tim`**. Header như #11, gồm `X-KTT-Viec` khi gọi trong lượt. Không cần khóa chống trùng.

| Khóa thân (đều tùy chọn) | Ý nghĩa |
|---|---|
| `loc` | Đối tượng `{truong: gia_tri}`, so bằng; mặc định `{}`. |
| `sap_xep` | Danh sách `{truong, giam}`; `giam` mặc định `false`. Không sắp xếp theo trường bí mật. Mặc định `[]`. |
| `gioi_han` | Số nguyên 1–500, mặc định 100. |
| `tiep` | Chuỗi con trỏ từ trang trước hoặc `null`; không tự sửa nội dung. |
| `gom_het_han` | Boolean, mặc định `false`. |

Trả `{danh_sach: [ban_ghi, ...], tiep: chuoi_hoac_null}`. Hết trang thì `tiep: null`; muốn lấy tiếp, gửi lại cùng điều kiện và `tiep` được trả. Ví dụ bảng phạm vi engine, không cần `X-KTT-Viec`:

```http
POST /api/v1/engine/e_demo_ngan/ngan/dinh_danh/tim
```
```json
{"loc":{"gia_tri":"CAN-CUOC-DEMO-001"},"sap_xep":[{"truong":"tao_luc","giam":true}],"gioi_han":100,"tiep":null,"gom_het_han":false}
```
```json
{"danh_sach":[{"id":"00000000-0000-0000-0000-000000000003","phap_nhan_id":null,"row_version":1,"tao_luc":"2026-11-15T10:00:00+07:00","sua_luc":null,"het_han_luc":null,"gia_tri":null,"gia_tri_da_ma_hoa":true,"bi_danh":"DEMO-001"}],"tiep":null}
```

Trường `bi_mat` ghi được bản rõ, tìm theo **đúng giá trị** qua băm, nhưng đọc luôn `null` kèm `<ma>_da_ma_hoa: true`; không trả cột băm/bản mã. Core không giải mã hộ engine (CĐ-36); Mask dùng bí danh hoặc mã tham chiếu.

### #13. Ghi một lô nguyên tử

**`POST /api/v1/engine/{ma}/ngan/ghi-lo`**. Header: ba header chung, `Content-Type`, `X-KTT-Viec` khi gọi trong lượt và **`Idempotency-Key` bắt buộc**, 8–200 ký tự thuộc `[A-Za-z0-9_.:-]`.

Thân chỉ có `lenh`, danh sách **1–100** lệnh. Mỗi lệnh gồm `thao_tac`, `bang`, cùng các trường tùy thao tác:

| Thao tác | Thân lệnh và kết quả |
|---|---|
| `them` | `gia_tri` đủ trường bắt buộc; tạo mới, `da_tao: true`. |
| `sua` | `khoa` không rỗng, `gia_tri` sửa một phần và `row_version` nguyên dương bắt buộc (tối đa `2**63 - 1`); CAS lệch trả 409 `NGAN_XUNG_DOT`. |
| `lay_hoac_tao` | `khoa` theo khóa khai báo/nhóm duy nhất, `gia_tri` bổ sung; đủ trường bắt buộc khi gộp khóa và giá trị. Đã có thì không sửa, trả id/phiên bản cũ, `da_tao: false`; chưa có thì tạo, `da_tao: true`. |

Không có thao tác xóa; `xoa` hoặc thao tác lạ trả 422 `NGAN_KHONG_XOA`. Một lệnh lỗi thì không lệnh nào được ghi. Trả `{ket_qua: [{id, row_version, da_tao}, ...]}` theo thứ tự lệnh. Ví dụ lấy hoặc tạo bộ đếm:

```http
POST /api/v1/engine/e_demo_ngan/ngan/ghi-lo
X-KTT-Viec: <id lượt đang giữ>
Idempotency-Key: demo-ngan-001
```
```json
{"lenh":[{"thao_tac":"lay_hoac_tao","bang":"dem_goi","khoa":{"ngay":"2026-11-15"},"gia_tri":{"so_lan":0}}]}
```
```json
{"ket_qua":[{"id":"00000000-0000-0000-0000-000000000001","row_version":1,"da_tao":true}]}
```

Sau khi đọc bản hiện tại bằng #11, ví dụ sửa với khóa chống trùng **mới** `demo-ngan-002`:

```json
{"lenh":[{"thao_tac":"sua","bang":"dem_goi","khoa":{"ngay":"2026-11-15"},"gia_tri":{"so_lan":1},"row_version":1}]}
```
```json
{"ket_qua":[{"id":"00000000-0000-0000-0000-000000000001","row_version":2,"da_tao":false}]}
```

Cùng `Idempotency-Key` và cùng byte thân yêu cầu thì trả kết quả đã lưu; đổi nội dung với khóa đã dùng trả 409 `KHOA_CHONG_TRUNG_KHAC_NOI_DUNG`. Khi mất phản hồi, gửi lại nguyên khóa và thân. Khi CAS xung đột, đọc lại, tính lại rồi lập lô mới với khóa mới; giới hạn số lần thử lại (mẫu 5 lần ở hướng dẫn mục 9.2).

`giu_toi_da_ngay` đặt `het_han_luc` khi tạo/sửa; `lay_hoac_tao` gặp bản đã có không gia hạn bản đó. Hết hạn chỉ ẩn ở #11/#12, đọc lại bằng `gom_het_han: true`; Core không tự xóa dữ liệu. Mỗi lệnh ghi có nhật ký kiểm toán chứa tham chiếu, không chép giá trị nghiệp vụ.

### #14. Đọc cấu hình engine

**`GET /api/v1/engine/{ma}/cau-hinh`**. Header: ba header chung; không cần `Content-Type`, `Idempotency-Key` hay thân yêu cầu. `X-KTT-Viec` tùy chọn, nếu gửi phải là lượt instance đang giữ.

Trả `{cau_hinh: {...}, phien_ban_cau_hinh: so_nguyen}` đã kiểm theo `cau_hinh.schema` và điền mặc định. Không khai schema thì trả `{"cau_hinh":{},"phien_ban_cau_hinh":0}`. Ví dụ gói mẫu có schema, chưa lưu cấu hình:

```http
GET /api/v1/engine/e_demo_ngan/cau-hinh
```
```json
{"cau_hinh":{"tien_to":"DEMO"},"phien_ban_cau_hinh":0}
```

Khi có schema, phản hồi `san-sang` và `viec/nhan` có thêm `cau_hinh`, `phien_ban_cau_hinh` ở **cấp ngoài cùng**, ngang cấp `viec` trong phản hồi nhận việc. SDK khởi tạo `app.cau_hinh`, chụp vào `viec.cau_hinh`; khi nhận thấy phiên bản tăng thì gọi #14 và `@app.khi_doi_cau_hinh`. Cấu hình không chứa bí mật.

### #15. Đếm hàng chờ của engine

**`GET /api/v1/engine/{ma}/hang-cho`**. Header và thân như #14; `X-KTT-Viec` tùy chọn và được kiểm nếu gửi. Chỉ trả số việc của engine đã xác thực:

```http
GET /api/v1/engine/e_demo_ngan/hang-cho
```
```json
{"so_viec_cho":3,"so_viec_dang_chay":1}
```

SDK tương ứng: `app.hang_cho()`. Hai số nguyên này là số đếm hàng chờ, không phải vị trí chờ của một việc.

### 4.2 Mã lỗi API #11–#15 (theo mã đang chạy)

Phong bì phẳng như mục 1; không bọc thêm `loi`. Ví dụ CAS:

```json
{"ma":"NGAN_XUNG_DOT","thong_diep":"Dữ liệu vừa thay đổi. Hãy đọc lại và thử lại.","request_id":"00000000-0000-0000-0000-000000000004","thu_lai_duoc":true}
```

| Mã | HTTP | Khi nào |
|---|---:|---|
| `NGAN_XUNG_DOT` | 409 | CAS lệch hoặc vi phạm duy nhất; `thu_lai_duoc: true`. |
| `NGAN_KHONG_XOA` | 422 | Lệnh xóa hoặc thao tác lạ trong lô. |
| `NGAN_KHONG_CO_BANG` | 404 | Bảng chưa khai trong ngăn của engine. |
| `NGAN_KHONG_THAY` | 404 | Sửa không thấy bản ghi theo khóa. |
| `NGAN_CAN_VIEC` | 422 | Bảng phạm vi pháp nhân, thiếu `X-KTT-Viec`. |
| `NGAN_DU_LIEU_SAI` | 422 | Sai kiểu, trường lạ/thiếu bắt buộc, cấu trúc lệnh/lô hoặc điều kiện tìm không hợp lệ. Lô rỗng cũng dùng mã này. |
| `NGAN_LO_QUA_LON` | 422 | Lô hơn 100 lệnh. |
| `ENGINE_NGAN_CHUA_SAN_SANG` | 409 | Ngăn chưa sẵn sàng hoặc chưa có điều kiện mã hóa/tra cứu bí mật. |
| `KHOA_CHONG_TRUNG_KHAC_NOI_DUNG` | 409 | Khóa chống trùng đã dùng cho thân yêu cầu khác. |
| `KHONG_DU_QUYEN` | 403 | `{ma}` khác thẻ; `X-KTT-Viec` không còn do instance giữ hoặc lượt không hợp lệ. |
| `KENH_XAC_THUC_KHONG_HOP_LE` | 401 | Thiếu/sai khóa, mã engine hoặc instance. |
| `KENH_KHONG_DU_QUYEN` | 403 | Gửi qua trình duyệt có `Origin` hoặc `Cookie`. |
| `YEU_CAU_KHONG_HOP_LE` | 400 | Thiếu/sai `Idempotency-Key`, JSON không phải đối tượng/hỏng hoặc độ dài thân sai. |
| `MIME_KHONG_HO_TRO` | 415 | Thân POST không rỗng nhưng Content-Type không phải JSON. |
| `VUOT_GIOI_HAN_KICH_THUOC` | 413 | Thân vượt giới hạn JSON 64 MiB. |
| `PHUONG_THUC_KHONG_HO_TRO` | 405 | Sai phương thức của route. |
| `LOI_NOI_BO` | 500 | Lỗi nội bộ; thông điệp không chứa chi tiết driver hay dữ liệu. |

Riêng #11–#15, lượt hết hạn/không còn được giữ ở `X-KTT-Viec` được route đổi thành **403 `KHONG_DU_QUYEN`**; không áp nguyên quy tắc `409 MAT_LEASE` của các API gia hạn/tiến độ/kết quả. Các mã lỗi bảng trên ngoài `NGAN_XUNG_DOT` có `thu_lai_duoc: false` theo các nhánh xử lý hiện tại.

## 5. Quy trình, nút và Việc của tôi

Quy trình gồm các bước hoặc nhóm bước. Khi kiểm và chạy, nhóm được trải phẳng; thứ tự dùng chung, đếm từ 1. Mỗi bước khai engine, năng lực và tham số:

```json
{"ten":"Đọc và đếm từ DEMO","trang_thai":"nhap","buoc":[{"thu_tu":1,"ma_engine":"e_demo_doc_tep","nang_luc":"tep.doc_van_ban@1","tham_so":{}}],"nhom_buoc":[]}
```

Quản trị viên dùng `GET /api/v1/quan-tri/engine`, `GET /api/v1/quan-tri/loai-du-lieu`, `GET` và `POST /api/v1/quan-tri/quy-trinh`, `GET` và `PUT /api/v1/quan-tri/quy-trinh/{id}`; `POST .../{id}/kiem`, `POST .../{id}/ap-dung`, `POST .../{id}/chay-thu`. Khi sửa nháp và áp dụng phải gửi `row_version` dạng chuỗi chữ số; lệch trả `QUY_TRINH_DA_DOI`. Quy trình đã áp dụng không sửa trực tiếp. Kiểm và áp dụng kiểm cả kiểu, bắt buộc, giới hạn và lựa chọn của tham số. Chạy thử nhận `{van_ban}` hoặc `{tep_demo:{ma_engine,duong_dan}}`.

Gắn nút qua `GET /api/v1/quan-tri/module/{ma}/nut`, `PUT /api/v1/quan-tri/module/{ma}/nut/{nut}`, `POST .../{nut}/ap-dung` và `POST .../{nut}/bo-gan`. Khi lưu nháp gửi:

```json
{"quy_trinh_id":"qt-1","ghep":[{"truong":"van_ban","ngan":"ho_so","cot":"noi_dung"}],"row_version":"1"}
```

Áp dụng gửi `{"row_version":"1"}` theo phiên bản đang mở. Phải ghép ít nhất một trường; kiểu trường và cột phải bằng nhau, cột thuộc ngăn của module, không ghép hai trường vào một cột. Cột bắt buộc chưa ghép tạo cảnh báo. Mỗi nút có một quy trình đang dùng; áp dụng cấu hình mới không đổi các việc đang chạy.

`GET /api/v1/module/{ma}/nut` với `X-Phap-Nhan-Id` trả các nút đã gắn quy trình đang dùng mà người đăng nhập có quyền tại pháp nhân:

```json
{"nut":[{"ma":"doc_tep","ten":"Đọc tệp","phan":"tong_quan","thao_tac_dau":"tai_tep","nhan_tep":{"mime":["text/plain"],"toi_da_mib":20}}]}
```

`POST /api/v1/module/{ma}/nut/{nut}/chay` nhận multipart một tệp, kiểm phiên, quyền và giới hạn tệp, rồi trả `{"viec_id":"viec-1","vi_tri_cho":1,"uoc_giay":30}`. Core chạy lần lượt các bước; xong phát `quy_trinh.xong`, lỗi phát `quy_trinh.loi` và dừng tại bước lỗi.

### 5.1 Gửi tệp và nhận mã việc (C-RV-02, SDK trình duyệt 2.3.0)

`sdk.nut.chay(ma_nut, tep, {idempotency_key?})` trả Promise `{viec_id, vi_tri_cho}`; `tep` là File/Blob, vị trí chờ là số nguyên không âm hoặc `null`. Mã module và pháp nhân lấy từ ngữ cảnh hiện tại, không nhận từ tham số. SDK gửi qua route chạy nút ở trên, kèm CSRF và khóa chống trùng tự sinh nếu không truyền. Khi gửi lại cùng ý định, giữ cùng khóa và cùng tệp; máy chủ vẫn kiểm phiên, quyền, loại/dung lượng tệp, pháp nhân và chống trùng.

Module lưu `viec_id` để nối về bản ghi của mình. Với nút mặc định, đăng ký `sdk.nut.khi_gui(ma_nut, cb)` để nhận cùng `{viec_id, vi_tri_cho}` sau khi gửi thành công; hàm trả về là hàm hủy đăng ký, gọi khi rời màn. Tùy chọn tự vẽ ở mục 2 không thay quyền máy chủ.

### 5.2 Đọc tệp kết quả (C-RV-01, SDK Python 2.3.0)

| Hàm trong backend/hàm nhận | Thao tác kênh (đọc) | Kết quả |
|---|---|---|
| `sdk.ket_qua.ds_tep(viec_id)` | `quy_trinh.ds_tep_ket_qua {viec_id}` | Danh sách `{tep_id, ten, mime, kich_thuoc, sha256}`; trên kênh bọc trong `{danh_sach}`. |
| `sdk.ket_qua.doc_tep(viec_id, tep_id)` | `quy_trinh.doc_tep_ket_qua {viec_id, tep_id}` | `bytes` từ luồng tệp, đã kiểm kích thước và SHA-256. |

Phải khai `sdk_dung` như mục 2. Chỉ đọc việc thuộc nút của chính module, cùng pháp nhân, đã **XONG**; chỉ tệp engine đã nộp trong kết quả lượt XONG của việc, không phải tệp đầu vào. Core đọc kho theo SHA-256, kiểm băm/kích thước và trần cấu hình, không vượt `GIOI_HAN_TEP = 20_971_520` byte (20 MiB); SDK kiểm lại descriptor, kích thước và SHA-256 trước khi trả bytes.

| Mã lỗi | Ý nghĩa |
|---|---|
| `KHONG_TIM_THAY` | Việc/tệp ngoài phạm vi, chưa XONG, không có kết quả (kể cả danh sách rỗng), tệp đầu vào hoặc tệp trong kho thiếu/sai băm/kích thước. |
| `VUOT_GIOI_HAN_KICH_THUOC` | Tệp vượt trần đọc của Core. |
| `CHUA_SAN_SANG` | Thiếu kho tệp ở Core hoặc thiếu kênh Core trong SDK. |
| `PHAN_HOI_SAI_CONTRACT` | SDK nhận JSON/luồng sai dạng, quá `GIOI_HAN_TEP`, sai kích thước hoặc SHA-256 phản hồi. |

Lỗi theo mục 1; hai thao tác là cửa kênh SDK, không thêm route HTTP công khai. SDK 2.3.0 chỉ thêm, tương thích ngược với 2.2.0.

### 5.3 Việc của tôi

`GET /api/v1/viec` và `GET /api/v1/viec/{id}` phục vụ Việc của tôi. Trạng thái bước là `cho`, `dang_chay`, `xong`, `loi`, `huy`. Danh sách trả `ten_viec`, `buoc`, `row_version`, `van_hanh.duoc_chay_lai`, `van_hanh.hang_cho`; dùng `van_hanh.hang_cho` làm nguồn vị trí và thời gian chờ. Chi tiết bước có thể có `dau_ra` và `loi`; văn bản đầu ra tối đa 2.000 ký tự, có cờ `da_cat` khi cắt.

```json
{"id":"viec-1","ten_viec":"Đọc tệp","buoc":[{"thu_tu":1,"ten":"Đọc văn bản","trang_thai":"dang_chay"}],"row_version":"1","van_hanh":{"duoc_chay_lai":false}}
```

Chạy lại dùng `POST /api/v1/viec/{id}/chay-lai` với `{"tu_buoc":1}` và giữ nguyên `viec_id`; hủy dùng `POST /api/v1/viec/{id}/huy`.

## 6. Thông báo

Phong bì sự kiện chỉ chứa tham chiếu, không chứa nội dung tài liệu hoặc bí mật:

```json
{"su_kien":"quy_trinh.xong","phien_ban":1,"id":"su-kien-1","luc":"2026-11-08T16:00:00+07:00","nguon":"core","ma_module":"demo_ho_so","viec_id":"viec-1","tham_chieu":{"ket_qua_id":"ket-qua-1"}}
```

Core gửi engine `viec.co_moi`, `viec.huy`, `engine.dung`; engine báo hoàn tất hoặc lỗi qua API kết quả và kết thúc. Core gửi module/người theo dõi `viec.da_nhan`, `viec.tien_do`, `viec.buoc_xong`, `quy_trinh.xong`, `quy_trinh.loi`, `viec.huy`. Riêng `quy_trinh.xong` gửi module sở hữu nút chỉ mang tham chiếu việc và kết quả; SDK đọc `tep_nut` và `ghep` trước khi gọi hàm nhận.

Module cùng Core nhận qua bus sự kiện. Đích HTTP nhận `POST` JSON với chữ ký HMAC-SHA256 trên `luc + "." + body` ở header `X-KTT-Chu-Ky`; bên nhận từ chối nếu lệch giờ quá 5 phút. Nếu không nhận 2xx, Core gửi lại sau 1 phút, 5 phút, 30 phút, 2 giờ, tối đa 24 giờ. Bên nhận phải bỏ qua `id` đã xử lý. Mất webhook không làm mất việc: engine tiếp tục kéo việc định kỳ.
