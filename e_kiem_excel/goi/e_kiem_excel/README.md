# Kiểm và đọc Excel — 0.1.1 (EX-6)

Khung SDK 2.2.0 cho `excel.toan_ven@1` và `excel.doc_bang@1`.
Kiểm đuôi, chữ ký, ZIP/XML, trần ô trước khi nạp workbook. `excel.toan_ven@1`
chạy K1–K8, tải JSON và báo cáo Excel qua Core; số trong JSON là chuỗi thập phân.
K8 chỉ chạy khi bật `kiem_nguon_kl`. `excel.doc_bang@1` đọc được
khuôn `xay_dung_klgt` (EX-4) và `tong_quat` (EX-5).

K7 dựng cây trước K6, phân nhóm bằng bộ module truyền. Báo cáo giữ kiểu ô,
màu cờ, 15 sheet khi bật K8 và 12 sheet khi tắt; cả ZIP và XML sheet ghi trong RAM.

Ô đích nhận `Sheet!A1` (có thể có dấu `$` và tên sheet đặt trong nháy đơn),
phải thuộc workbook và giới hạn Excel. Nếu trống, tìm theo `nhan_o_dich_json`:
danh sách từ khóa, 80 dòng đầu/12 cột đầu của sheet hiện, số đầu trong sáu ô
bên phải nhãn. Không tìm được hoặc cả hai trống: một mục Kiểm soát K7.

`bo_nhom_json`: tối đa 30 nhóm, 200 từ khóa, 32 KiB UTF-8; xét nhóm theo thứ tự.
Từ khóa chứa chuỗi, `=tu` khớp nguyên từ, `#` khớp một hoặc nhiều chữ số;
các ký tự regex được hiểu nguyên văn. Không bộ nhóm: lá Chưa phân nhóm,
`so_ngoai_nhom = null`. Bộ Review TTKL thuộc module, chỉ ở fixture ngoài gói.
Mã dùng chung cho EX-5: `bo_nhom.kiem_tu_khoa(tu)`,
`bo_nhom.khop_tu_khoa(tu, van_ban)`; tự bỏ dấu/viết thường/gộp khoảng trắng.

Không mạng ngoài Core, không CSDL, không ngăn/cấu hình, không lưu dữ liệu trên máy.
DEMO hoàn toàn giả: Công ty DEMO Ánh Dương. Script sinh ở `tests/demo/sinh_demo.py`
ngoài gói. Cài thư viện bằng `requirements.lock` với `--require-hashes --no-deps`;
SDK cài riêng từ wheel 2.2.0 trong repo. Bật `PYTHONDONTWRITEBYTECODE=1` khi kiểm.

Trần đề xuất cuối EX-6: tệp 20 MiB; giải nén 128 MiB; 2.048 entry; 250.000 ô thực,
500.000 ô trong tổng hình chữ nhật các sheet; thời hạn Core 120 giây.
Số đo và giới hạn phép kiểm ghi trong `docs/VIEC.md` ngoài gói.
K7 giữ trần 14 tầng/12 mẫu mỗi dải của nguồn nhưng từ chối khi vượt,
không cắt ngầm; thêm trần 100.000 nút, 250.000 ô/dải, 500.000 lượt đọc ô.

SDK 2.2.0 kiểm MIME bằng chữ thường trong khi CoreGia trả MIME `.xlsm` có chữ
hoa. Cổng tạm chuẩn hóa MIME trước bộ kiểm, cho cả đầu vào gửi kèm và tải riêng;
không sửa phong bì gốc. Đợi Core/SDK sửa để bỏ lớp bọc này.

Đã kiểm bằng Core giả (CoreGia); chưa nối Core thật.

Kiểm kê SHA-256: `NGUON.md` và `tests/demo/bam-goi.json` ngoài gói (gồm cả
băm của NGUON.md). Cài sạch offline: `sh e_kiem_excel/tests/kiem_may_sach.sh
<thu_muc_wheel>` trên Linux Python 3.11; Windows dùng `tests/KIEM-MAY-SACH.cmd`
do Anh chạy. CI chuẩn bị wheel theo lock có hash rồi script cài hoàn toàn offline.

## Khuôn tổng quát (EX-5)

Chọn `khuon = tong_quat`, truyền `khuon_cot_json` phiên bản 1 theo phiếu §4.2.
Khuôn đóng: đúng ba khóa `phien_ban`, `cot`, `dong_dung`; mỗi cột đúng bốn khóa
`ma`, `tu_khoa`, `bat_buoc`, `kieu`. Mã cột duy nhất, chữ thường không dấu,
chữ đầu là a–z, sau đó chữ/số/gạch dưới, tối đa 64 ký tự. Có ít nhất một cột
bắt buộc. Trần 30 cột, tổng 200 từ khóa (gồm dòng dừng), 32 KiB UTF-8.
Sai cấu trúc, trùng khóa JSON hoặc vượt trần trả `THAM_SO_KHONG_HOP_LE`.

Từ khóa gọi trực tiếp `bo_nhom.khop_tu_khoa`: bỏ dấu/không phân biệt hoa thường,
chứa chuỗi; `=...` khớp nguyên từ/cụm từ; `#` khớp ít nhất một chữ số.
Ký tự regex khác hiểu nguyên văn. `dong_dung` xét ô có giá trị ngoài cùng bên trái
trong các cột đã nhận diện; có thể dùng `=tong cong` để tránh khớp một phần nhãn.

Dò tiêu đề bắt đầu trong 40 dòng đầu, ghép tối đa 4 tầng, trải nội dung ô gộp
chỉ trong vùng tiêu đề. Chọn bảng nhiều cột khớp nhất, rồi ít tầng nhất, rồi dòng
trên cùng; hòa giữa các sheet thì lấy sheet trước. Không lấy sheet ẩn. Từ khóa
khớp nhiều cột hoặc hai mã cùng trỏ một cột thì bỏ ứng viên đó; không thấy ứng viên
đủ cột bắt buộc trả `KHONG_TIM_THAY_BANG`. Cột tùy chọn không có trả null.

Tệp JSON giữ phần đầu như §5.2, `cot` ánh xạ mã → chữ cột. Mỗi phần tử `dong`
gồm `vi_tri`, `nhom`, `la_nhom`, `du_cot_bat_buoc`, `gia_tri` (mã cột → giá trị),
`canh_bao`. Dòng thiếu cột bắt buộc vẫn giữ để kiểm tra và có cảnh báo, không tính
vào `so_dong`; một ô chữ duy nhất thuộc cột văn bản khi thiếu cột bắt buộc được coi
là tiêu đề nhóm. Ô sai kiểu trả null và cảnh báo; dòng đủ giá trị nguồn ở các cột
bắt buộc vẫn tính vào `so_dong`. `tong_hop` rỗng, hai trường giá trị hợp đồng/đề nghị
luôn null vì chỉ áp dụng khuôn xây dựng.

Số dùng Decimal, JSON là chuỗi thập phân; số lưu dạng chữ có cảnh báo. Mã hàng
dạng chữ giữ số 0 đầu. Ngày Excel có định dạng ngày, chuỗi ISO hoặc dd/mm/yyyy
được xuất `YYYY-MM-DD`; không suy ngày từ số serial chưa có định dạng.
Tiền tệ lấy từ tham số hoặc đơn vị ghi rõ như EX-4; chưa rõ thì cờ bật, JSON giữ
số nguồn với `tien_te: null` theo §5.2. Không tự gán đơn vị.

Hai ví dụ trong `chay_thu_demo`: bảng giá thành tiêu đề gộp nhiều tầng, bảng báo giá
đổi vị trí cột và sheet. Nguồn sinh, khuôn và đáp án ngoài gói tại `tests/demo/`.

## Trình soạn Cài đặt bước TS-EX — 21/11/2026

`ui/tham_so.js` xuất thành phần ES module cho cả hai năng lực. Mỗi ý là một
ô riêng, có nhãn/hướng dẫn/ví dụ; thêm/bỏ từ khóa, nhóm, điều kiện, cột và đổi
thứ tự trực tiếp. JSON chỉ đọc trong mục Nâng cao. Mẫu gắn nhãn DEMO;
không chứa bộ nhóm nghiệp vụ riêng của module. Không có cấu hình engine,
schema cấu hình, dịch vụ ngoài hay bí mật nên không cần nút kiểm kết nối,
két key hoặc thao tác quản trị Python. Nút Kiểm tra cài đặt chỉ kiểm cấu trúc;
engine tiếp tục kiểm sheet, bảng và dữ liệu khi xử lý tệp.

- Ô đích: chọn sheet từ danh sách Core cấp và nhập địa chỉ, hoặc để trống cả
  hai rồi soạn cụm từ tìm. Chưa có tệp mẫu: nhập tên sheet. Có ô đích thì
  engine ưu tiên ô đó; danh sách nhãn vẫn được giữ để không mất dữ liệu.
- Bộ nhóm: nhóm đầu tiên khớp được chọn. Mỗi nhóm có nhiều điều kiện (OR).
  Trong một điều kiện, ghép văn bản các vùng đã chọn, mọi cụm phải khớp (AND);
  trong từng cụm chỉ cần một từ khóa (OR), và không có từ khóa loại trừ.
- Khuôn cột: mã cột kết quả, từ khóa tiêu đề, kiểu và công tắc bắt buộc;
  danh sách nhãn dòng dừng. Cần ít nhất một cột bắt buộc. Chuyển về khuôn
  xây dựng vẫn giữ bộ cột đã soạn; bộ đó chỉ được dùng với `tong_quat`.

Từ khóa: chuỗi thường = chứa chuỗi; tiền tố `=` = khớp nguyên từ/cụm từ;
`#` = một hoặc nhiều chữ số. Không phân biệt dấu/hoa thường; ký tự regex
khác được hiểu nguyên văn. Không cắt ngầm nội dung vượt trần.

### Cấu trúc tham số hiện có (dùng cả khi Core còn hiện ô JSON chung)

| Tham số / trường | Kiểu | Bắt buộc | Ý nghĩa và giá trị cho phép |
|---|---|---|---|
| `o_dich` | chuỗi | không | `Sheet!A1`, hỗ trợ `$` và nháy đơn tên sheet; tới XFD1048576, tối đa 512 ký tự; trống thì tìm nhãn |
| `nhan_o_dich_json` | chuỗi JSON mảng chuỗi | không | Mảng không rỗng nếu đã điền; từng từ khóa không rỗng; tối đa 4 KiB UTF-8; trống không tìm nhãn |
| `bo_nhom_json` | chuỗi JSON object | không | Trống: Chưa phân nhóm, số ngoài nhóm chưa xác định; tối đa 32 KiB UTF-8 |
| ↳ `phien_ban` | số nguyên | có | Luôn 1 |
| ↳ `ten_bo` | chuỗi | có | Tên bộ không rỗng |
| ↳ `nhom` | mảng object | có | 1–30 nhóm, xét theo thứ tự |
| ↳ `nhom[].ma` | chuỗi | có | Mã không rỗng, duy nhất trong bộ |
| ↳ `nhom[].ten` | chuỗi | có | Tên không rỗng, duy nhất; không dùng Chưa phân nhóm hoặc Ngoài nhóm — cần giải thích |
| ↳ `nhom[].tai_lieu` | chuỗi | có | Tài liệu cần đối chiếu, không rỗng |
| ↳ `nhom[].khi` | mảng object | có | Ít nhất một điều kiện; OR giữa các điều kiện |
| ↳ `khi[].vung` | mảng chuỗi | có | Ít nhất một, không trùng: `tieu_de_cot`, `ten_sheet`, `nhan_dong` |
| ↳ `khi[].tat_ca` | mảng mảng chuỗi | có | Ít nhất một cụm; mỗi cụm ít nhất một từ khóa. AND giữa các cụm, OR trong từng cụm |
| ↳ `khi[].khong_co` | mảng chuỗi | không | Có thể rỗng; loại trừ nếu gặp bất kỳ từ khóa nào |
| `kiem_nguon_kl` | boolean | không | Mặc định false; bật kiểm K8 |
| `khuon` | chuỗi chọn | có, có mặc định | `xay_dung_klgt` hoặc `tong_quat`; mặc định xây dựng |
| `khuon_cot_json` | chuỗi JSON object | khi tổng quát | Đúng các trường dưới, tối đa 32 KiB UTF-8 |
| ↳ `phien_ban` | số nguyên | có | Luôn 1 |
| ↳ `cot` | mảng object | có | 1–30 cột; ít nhất một cột bắt buộc |
| ↳ `cot[].ma` | chuỗi | có | Duy nhất, bắt đầu a–z, chữ thường/số/gạch dưới; tối đa 64 ký tự |
| ↳ `cot[].tu_khoa` | mảng chuỗi | có | Không rỗng; tiêu đề khớp ít nhất một từ khóa |
| ↳ `cot[].kieu` | chuỗi chọn | có | `van_ban`, `so`, `so_tien`, `ngay` |
| ↳ `cot[].bat_buoc` | boolean | có | true: phải nhận diện được cột |
| ↳ `dong_dung` | mảng chuỗi | có | Có thể rỗng; trống đọc đến hết bảng |
| `tien_te` | chuỗi | không | Trống hoặc 3 chữ hoa, ví dụ VND, USD; không tự gán VND |

Mỗi bộ nhóm/khuôn cột có tối đa 200 từ khóa, gồm loại trừ hoặc dòng dừng.
Tất cả từ khóa phải không rỗng và dấu `=` phải có cụm từ theo sau. Cấu trúc
object đóng, không thêm khóa ngoài bảng. UI từ chối nguồn sai kiểu/khóa
trùng/khóa lạ/phiên bản khác; giữ nguồn, khóa lưu, cho tải lại hoặc chèn mẫu
thay từng phần. Lỗi nhập hiện cạnh trường và phần báo lỗi. Mẫu tối thiểu:

```json
{
  "o_dich": "BTH!J39",
  "nhan_o_dich_json": "[\"=tổng cộng\",\"giá trị đề nghị\"]",
  "bo_nhom_json": "{\"phien_ban\":1,\"ten_bo\":\"Nhóm DEMO\",\"nhom\":[{\"ma\":\"don_gia\",\"ten\":\"Đơn giá DEMO\",\"tai_lieu\":\"Bảng giá DEMO\",\"khi\":[{\"vung\":[\"tieu_de_cot\"],\"tat_ca\":[[\"đơn giá\"]],\"khong_co\":[\"tạm tính\"]}]}]}",
  "kiem_nguon_kl": false
}
```

```json
{
  "khuon": "tong_quat",
  "khuon_cot_json": "{\"phien_ban\":1,\"cot\":[{\"ma\":\"ma_hang\",\"tu_khoa\":[\"=mã hàng\"],\"bat_buoc\":true,\"kieu\":\"van_ban\"}],\"dong_dung\":[\"=tổng cộng\"]}",
  "tien_te": "VND"
}
```

Nếu điền trực tiếp vào từng ô JSON chung thì chỉ dán nội dung JSON của
tham số đó, không dán cả object bọc chứa các tham số như hai ví dụ trên.
Các nút Chèn mẫu DEMO trong trình soạn tự xuất đúng chuỗi, không cần gõ JSON.

### Cửa D2 đang chờ Core

Khai **dự kiến** tại `KHAI-SDK-2.1.json`; không phải API SDK mới đã phát hành.
Core nạp `default(goc, KttCore, nguCanh)` với `nang_luc` đã ghim và hai callback
do màn bước của Core sở hữu:

- `doc()` → `{tham_so, phien_ban, ds_sheet?}`. Có thể truyền bản tham số trực
  tiếp thay callback để nhúng chỉ xuất dữ liệu. Không truyền tệp/đường máy.
- `luu(tham_so, phien_ban)` → `{phien_ban}` mới: Core kiểm quyền, phiên bản
  bước (CAS), kiểu/trần và ghi kiểm toán. 409 / `THAM_SO_XUNG_DOT` khóa lưu
  tới khi tải lại; bản sửa vẫn trên màn. Thiếu callback/phiên bản thì không
  bật Lưu. Lỗi không có xác nhận phiên bản mới không được báo đã lưu.
- Thành phần trả `{xuat, kiem, nap, huy}`. `xuat()` trả bản sao mọi tham số,
  JSON vẫn là chuỗi; lỗi có `{truong,cau}`. Core có thể tự dùng `xuat()` ở
  nút lưu chung. `huy()` tháo màn khi rời bước.

Không lưu tham số quy trình qua `.cau_hinh`/`.ngan` của engine; không tự mở
cổng mạng hoặc HTTP. TS-EX không cần gọi API engine nào. Khi các lát khác
cần API engine thì chỉ dùng `KttCore.engine(ma)`. Cửa D2 phải được lead Core
thống nhất/nối thật; hiện **đã kiểm bằng Core giả (CoreGia)**, chưa nối Core thật.

Kiểm UI: `node --test e_kiem_excel/tests/ui/tham_so.test.mjs` (Node, không
mạng, không npm dependency); pytest chạy lại Node và cho 6 bộ tham số do UI
xuất chạy trên CoreGia. Ảnh DEMO và script chụp nằm ngoài gói tại
`docs/anh-TS-EX/` và `tests/ui/chup_man.mjs`. Script chụp dùng Edge headless
trên Windows, hoặc biến `KTT_TRINH_DUYET` trỏ Chromium trên Linux; không dùng
hồ sơ trình duyệt thật. Node và trình duyệt chỉ là công cụ test, không thêm
vào dependency runtime Python.
