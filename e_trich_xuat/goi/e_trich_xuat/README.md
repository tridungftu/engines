# Trích thông tin hợp đồng — TX-7, bản 0.5.0 (SDK 2.2.0)

TX-7 chuyển cấu hình/ngăn sang SDK 2.2.0, giữ năng lực và nghiệp vụ TX-6. Xem [`../../cong-cu/README.md`](../../cong-cu/README.md) và
[`../../docs/TX-6-KET-QUA.md`](../../docs/TX-6-KET-QUA.md).
Chỉ **đã kiểm bằng Core giả (CoreGia)**; T3/N1 máy thật chưa đo/chưa kiểm.

Gói công bố **`trich.doc_docx@1`** (`tep` DOCX → `van_ban_tai_lieu`) và
**`trich.chuan_bi@1`** (`van_ban_tai_lieu` → một `yeu_cau_ai` phiên bản 1).
Đã đăng ký **`trich.hau_kiem@1`** (`tra_loi_ai` → `bang_trich_xuat`) và
**`trich.xuat_ket_qua@1`** (`bang_trich_xuat` → `truong` tĩnh).
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
pháp nhân, ghim bộ/prompt/cấu hình theo việc; SDK 2.2.0 cấp bản chụp cấu hình cho việc; quyền ghim bộ/prompt
và phạm vi module vẫn cần Core xác nhận. C-TX-02 cần quyền/vòng đời đọc tệp xuyên bước trong
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

## Cấu hình và kiểm SDK 2.2.0

`engine.json` khai `cau_hinh.schema: "cau_hinh.schema.json"`, yêu cầu SDK
`>=2.2.0 <3.0.0`. Core kiểm schema và điền mặc định ngân sách **16.000**;
handler đọc đúng `viec.cau_hinh`, sao chép vào hồ sơ để thay đổi sau đó
không ảnh hưởng việc cũ. Thiếu trường bắt buộc vẫn trả `CHUA_CAU_HINH`.
Không có cache cấu hình nên không cần `@app.khi_doi_cau_hinh`.

Không còn bảng `cau_hinh` hoặc bảng ngăn TX khác; vì vậy không khai
`ngan_du_lieu`, `du_lieu.goi_migration`, không có SQL/kiểm kê SQL.
`KHAI-SDK-2.1.json`, `ngan.py`, `cau_hinh.py` tạm và script cổng DEMO cũ
được giữ nguyên tại `../../LUU-TRU/TX-7/`, không nằm trên đường chạy.
Màn `ui/cau_hinh.js` tiếp tục dùng
`KttCore.engine("e_trich_xuat").cau_hinh.doc()/luu(gia_tri, phien_ban)`.
SDK 2.2.0 chưa nhận khóa `giao_dien_quan_tri`; lead Core cần nối/review
màn theo cổng chung (C-TX-08), không thêm khóa ngoài schema manifest.

**Giới hạn SDK còn mở:**

- C-TX-06: CLI chỉ tự nạp `tep_demo` ở đầu vào loại `tep`, chưa nạp tệp
  hồ sơ được tham chiếu trong `tra_loi_ai`. CLI chuẩn hiện **4/5 ĐẠT,
  exit 1**, DEMO hậu kiểm ở `DANG_CHAY` sau 404. Không đổi ID tệp theo
  thứ tự cấp hoặc sửa handler/SDK để làm xanh. Giữ đủ năm ví dụ.
- C-TX-07: `Viec` chưa công bố `phien_ban_cau_hinh`. Hồ sơ mới ghi
  `phien_ban_cau_hinh: null` và `bam_cau_hinh` trên canonical JSON UTF-8
  của bản chụp. Hậu kiểm bắt buộc băm đúng; vẫn đọc hồ sơ cũ có phiên bản
  nguyên dương. Băm chỉ kiểm toàn vẹn, không chứng minh quyền/phiên bản Core.
- C-TX-05: chưa có hook công khai đổi câu lỗi trước handler. Hai hook
  `_ket_thuc`/`_ghi` đã kiểm lại trên 2.2.0; giữ khóa đúng phiên bản và
  chữ ký để dừng khi SDK thay đổi. SDK 2.2.0 đã ẩn nội dung exception
  khỏi log. Wrapper giữ câu lỗi DOCX/chuẩn bị đã cam kết.

Từ gốc repo, tạo `.venv` mới, cài wheel nội bộ rồi phụ thuộc đã ghim từ
kho wheel offline đã chuẩn bị cho nền tảng đang chạy:

```text
python -m venv .venv
.venv/Scripts/python -m pip install --no-index --no-deps docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl
.venv/Scripts/python -m pip install --no-index --no-deps --find-links KHO_WHEEL -r e_trich_xuat/goi/e_trich_xuat/requirements.lock -r e_trich_xuat/tests/requirements.lock
python -B -m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat
python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp
python -B e_trich_xuat/tests/kiem_doc_lap.py
```

Ba lệnh cuối dùng Python trong `.venv` (`Scripts/python` trên Windows,
`bin/python` trên Linux). Dùng `-B` hoặc `PYTHONDONTWRITEBYTECODE=1` để giữ
gói sạch bytecode. Phiên TX-7 dùng venv Python 3.13.14 mới, SDK 2.2.0,
phụ thuộc offline; `pip check` đạt. Nguồn phụ thuộc/lock ở `NGUON.md`.

Các test dùng ngăn/cấu hình của `CoreGia` 2.2.0, `dat_cau_hinh`,
`gay_xung_dot_ngan`, `xem_ngan`, không dùng ngăn RAM tự viết. Giữ các ca
hành vi cũ; ca xóa/RAM đổi sang cấm xóa/trạng thái và Core giữ dữ liệu qua
app mới. Các ca trần byte của lõi dùng phiếu test riêng để đi tới handler,
vì SDK mới đã chặn mọi chuỗi metadata dài trước handler; trần gói thật
không đổi. Helper nạp hồ sơ DEMO chỉ phục vụ unit fixture, không có cổng
CLI thay thế. **đã kiểm bằng Core giả (CoreGia)**; Linux/Core thật chưa kiểm.
Pytest **486 passed, 0 skipped**, kiểm độc lập exit 0.
TX-7 **chưa đạt nghiệm thu** vì C-TX-06; kết quả cuối tại `../../docs/VIEC.md`.


## Hậu kiểm và xuất — TX-3b, 15/11/2026

Anh đã duyệt `bang_trich_xuat` tại quyết định chiều 15/11, gồm bổ sung
TX-3-REVIEW. Schema nguồn ở `_chung/contract/`, bản tự chứa trong
`contract/bang_trich_xuat.schema.json`; test so SHA-256 sau CRLF→LF.
Payload có offset `unicode` theo code point Python; `dau_kiem_tam_e6`
chỉ là dấu kiểm tạm đối chiếu E6. `phan_hoi_ai` **chỉ kiểm toán**, có thể
chứa dẫn chứng giả/nội dung tài liệu: module không hiển thị mặc định và
không ghép cột từ đây. Dữ liệu chuẩn là `gia_tri` và `dan_chung` đã kiểm.

Hậu kiểm giữ `kieu=van_ban`, `kieu_da_chuyen=false` vì snapshot E1 chưa
khai quy tắc chuyển kiểu. Không tự đoán tiền/ngày hoặc tính TT-21.
Exporter hỗ trợ sáu kiểu chung, tiền có mã tiền tệ, ngày ISO, số dài bằng
text JSON; text không thành công thức Excel. Hai tệp JSON/Excel tạo trong
RAM và tải lên Core; chỉ trả `XONG` khi đủ hai tệp. Trường tĩnh:
`tep_json`, `tep_excel`, `so_tham_so`, `so_can_soat`, `co_can_cu`.
Module dùng JSON chuẩn để ghép cột, quyết định lưu và quản lý lịch sử.
Không ghi kết quả/bộ/lịch sử lên máy engine. E6/N1/Core thật chưa kiểm.

## Bằng chứng toàn chuỗi

Giữ hai chuỗi DOCX lõi thật hoặc PDF/OCR giả → chuẩn bị → Local AI giả →
hậu kiểm → xuất `truong`, kiểm tệp JSON/Excel và snapshot sau đổi cấu hình.
Node kiểm UI bằng KttCore giả; MayChuGia kiểm HTTP loopback, stdin, hủy,
ACK lặp. Công cụ TX-6 chuyển cách nạp cấu hình sang CoreGia 2.2.0;
không gọi model thật, không phát sinh lượt Cloud. T3/N1 máy thật chưa đo.
`tests/kiem_may_sach.py --tao-venv --kho-wheel KHO_WHEEL` cài runtime mới
bằng kho offline; trả lỗi nếu CLI chuẩn chưa đạt, không quy đổi thành đạt.
Linux dùng `TX7_KHO_WHEEL` với `tests/kiem_may_sach.sh`.

## TS-TX — trình soạn bộ tham số nhúng trong module, 21/11/2026

Màn `ui/soan_bo_tham_so.js` dùng trong phần quản lý bộ tham số của từng
module theo quyết định 07/11. Nhập Excel E1, sửa đủ 10 cột, thêm/xóa dòng
và quy tắc, kiểm lỗi tại ô, tính băm rồi xuất đúng hai chuỗi Cài đặt bước.
Bộ/lịch sử/kích hoạt và phân quyền thuộc module. Màn không lưu trên máy,
không có kho bộ riêng trong ngăn engine, không gọi AI hoặc mạng ngoài.

Hợp đồng nhúng dự kiến (chưa có trong SDK/Core thật):

```javascript
const man = await nap({
  goc, KttCore,
  tham_so: {bo_tham_so_json, bam_bo_tham_so}, // bỏ khi tạo bộ mới
  dinh_danh: {module: "module_demo", loai_hop_dong: "DEMO", phien_ban_bo: "demo-1"},
  phien_ban: 7, // CAS của bản ghi MODULE, không phải phiên bản nội dung bộ
  luu: async (thamSo, phienBan) => {
    // Module kiểm quyền và CAS; trả {phien_ban: phiên bản mới}.
    // Nếu tranh chấp, ném lỗi status=409; không tự ghi đè/thử lại.
    return luuBoCuaModule(thamSo, phienBan);
  }
});
const thamSo = await man.xuat(); // hai chuỗi, hoặc null nếu lỗi/đang bận
man.dong(); // hủy listener, bỏ phản hồi muộn
```

Không truyền `luu`: nút Xuất chỉ trả tham số qua `man.xuat()` và hiển thị
bản chỉ đọc trong Nâng cao, không báo đã lưu. Có `luu`: module chịu trách
nhiệm đọc bộ ban đầu cùng phiên bản CAS và kiểm CAS nguyên tử phía server;
409 khóa lưu đến khi host nạp lại màn với bản mới. Các tham số khác của
bước (prompt, chọn trường...) do host giữ và ghép cùng hai trường xuất.

Màn chỉ gọi `KttCore.engine("e_trich_xuat").thao_tac("soan_bo_tham_so", dauVao)`.
Hàm thuần dự kiến `e_trich_xuat.soan_bo.ham_thao_tac(tac)` nhận `tac.dau_vao`:

| Lệnh | Dữ liệu bắt buộc | Ý nghĩa |
|---|---|---|
| `doc_bo` | `tham_so`: object gồm hai chuỗi | Kiểm băm và cấu trúc bộ đang ghim |
| `nhap_excel` | `bo`: định danh; `tep_base64`: chuỗi base64 bytes .xlsx | E1 đọc Excel ≤2 MiB, giải nén ≤16 MiB; giữ quy tắc và băm tệp gốc |
| `kiem_bo` | `bo`: object theo bảng dưới | E1 kiểm bảng đã sửa, chuẩn hóa, tính băm và kiểm bằng cửa nhận việc |

Trả `{dat, bo, tham_so, loi, canh_bao}`; khi lỗi không trả `tham_so`.
`loi[]` gồm `truong` (ví dụ `cac_dong.0.ma`) và `thong_bao` tiếng Việt.
Excel sai không thay bảng hiện tại. Nhập Excel thay toàn bộ dòng/quy tắc;
sửa bảng giữ `bam_tep_goc` để truy nguyên, tính lại `ma_bam_noi_dung` và
băm snapshot. Mã/nội dung băm chỉ hiển thị trong Nâng cao. Màn giữ cờ
`luon_cloud` của E1; cờ này không cấp quyền bật hoặc gọi Cloud.

`bo_tham_so_json` là chuỗi JSON UTF-8 của object, không được bỏ trống.
`bam_bo_tham_so` là chuỗi `sha256:` + 64 số hex, băm **đúng bytes UTF-8
của chuỗi đã xuất**, không băm JSON được host định dạng lại. Trần 64 KiB
cho cả bộ, tối đa 200 dòng đang dùng; vượt thì từ chối, không cắt ngầm.
Nhập khi tạo/kích hoạt bộ của module; không có bộ hợp lệ thì engine từ chối,
không chọn bộ mặc định.

| Trường object bộ | Kiểu / bắt buộc | Ý nghĩa và giá trị cho phép |
|---|---|---|
| `phien_ban` | integer / có | Luôn là `1` |
| `module`, `loai_hop_dong`, `phien_ban_bo` | string / có | Mã `[A-Za-z0-9_.:-]{1,200}`; định danh module, loại, bản nội dung |
| `cac_dong` | array object / có | Giữ thứ tự, gồm cả dòng ngừng dùng; ít nhất một dòng Dùng |
| `quy_tac` | array object / có | `[]` nếu không hậu kiểm theo quy tắc |
| `ma_bam_noi_dung` | string / không | Băm nội dung dòng do E1 tính; luôn tính lại sau sửa |
| `bam_tep_goc` | string / không | `sha256:` + 64 hex của tệp nhập gốc |

| Trường mỗi dòng | Kiểu / bắt buộc | Ý nghĩa và mẫu |
|---|---|---|
| `ma` | string / có | 2–3 chữ in hoa, dấu -, 2–3 chữ số; `TT-01`; không trùng |
| `nhom` | string / có | Tên nhóm không rỗng; `Thông tin chung` |
| `mo_ta` | string / có | Mô tả cho AI không rỗng, ≤1.000 ký tự |
| `tk`, `bk` | string / có | Từ khóa tiêu đề/nội dung; phân cách `;`, mỗi từ ≤60 ký tự; chỉ `tk` dùng `@mo_dau`; rỗng nếu không dùng |
| `dung` | boolean / có | Có đưa vào trích xuất; ví dụ `true` |
| `muc` | integer / có | Mức quan trọng 0–3; ví dụ `1` |
| `bat_buoc`, `loai_tru` | string / có | Từ khóa bắt buộc/loại trừ, cùng trần như trên; rỗng nếu không dùng |
| `luon_cloud` | boolean / có | Cờ E1, mặc định `false`; không bật dịch vụ Cloud |

Mỗi quy tắc có đủ `kieu` (string), `ma_tham_so` (array string, mã có trong
bảng, không lặp), `dieu_kien` (string), `doi_chieu` (string).
`Tổng tỷ lệ`: một hoặc nhiều mã, điều kiện `=`/`<=`, đối chiếu `100`.
`Ngày không sau`: một mã, `<=`, đối chiếu một mã khác.
`Có thì phải có`: một mã, điều kiện rỗng, đối chiếu một mã khác.

Mẫu bộ tối thiểu (dùng màn để tính băm sau khi sửa):

```json
{"phien_ban":1,"module":"module_demo","loai_hop_dong":"DEMO","phien_ban_bo":"demo-1","quy_tac":[],"cac_dong":[{"ma":"TT-01","nhom":"Thông tin chung","mo_ta":"Trích tên hợp đồng DEMO","tk":"tên","bk":"","dung":true,"muc":1,"bat_buoc":"","loai_tru":"","luon_cloud":false}]}
```

Khai dự kiến tại `KHAI-SDK-2.1.json` mục TS-TX; không đổi `engine.json`.
Core cần D2 + thao tác E có kiểm quyền; module cần host nhúng và callback
CAS. Chưa có decorator quản trị ở SDK 2.2.0 nên không đăng ký giả vào runtime.
Adapter CoreGia chỉ trong test. **đã kiểm bằng Core giả (CoreGia)**.
Ảnh dựng bằng KttCore giả: `../../docs/anh-ts-tx/`; tái dựng trang bằng
`python -B e_trich_xuat/tests/ui/dung_anh_ts_tx.py`. Không có máy ngoài hoặc
bí mật trong lát này; ca kết nối/mask 4 ký tự cuối không áp dụng cho TS-TX.
