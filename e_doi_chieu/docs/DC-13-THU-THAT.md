# DC-13 — Công cụ đo DEMO qua Core, Anh tự chạy

Ngày 15/11/2026 · PR: **chờ lead mở** · Ước tính: **3 giờ**.

**Đã kiểm bằng Core giả (CoreGia)** và adapter/pipe giả. Các phép đo
ABBYY/OCR/Local/Core thật, trình duyệt, quyền thật và hiệu lực module:
**CHỜ ANH TỰ CHẠY**. Codex không chạy `--that` trên môi trường thật.
Không coi số đo từ adapter giả là chất lượng thực tế.

## Chạy công cụ

Từ workspace, mặc định chỉ trả khung báo cáo trong RAM/stdout:

```text
e_doi_chieu\cong-cu\THU-DOI-CHIEU-THAT.cmd
```

Wrapper ASCII dùng `.venv\Scripts\python.exe`, không tự cài môi trường.
Linux dùng `.venv/bin/python -B e_doi_chieu/cong-cu/thu_doi_chieu_that.py`.
Không `--that`: không đọc bộ mẫu, mở handle, gọi mạng hoặc ghi báo cáo,
kể cả có truyền `--bao-cao`. Mã thoát 0 lúc này chỉ nghĩa chạy khô xong.

Chỉ Anh tự chạy lệnh dưới đây **sau khi Core có binding đã review**:

```text
e_doi_chieu\cong-cu\THU-DOI-CHIEU-THAT.cmd --that --bo-demo e_doi_chieu/cong-cu/DEMO-bo-thu-dc13.json --ma-phien DEMO-luot-001 --module demo --quy-trinh demo --cau-hinh-core demo --core-vao-fd 3 --core-ra-fd 4 --iou-ghep 0.5
```

Các mã `demo`, fd 3/4 và IoU 0.5 trong lệnh chỉ minh họa tham số. Host
Core phải cấp mã quy trình/module/cấu hình đã ghim và hai **CRT file
descriptor của pipe được kế thừa**; đây không phải Windows HANDLE thô,
đường tệp hay số cổng mạng. Windows host phải chuyển handle thành CRT fd
khi khởi động tiến trình. Chạy wrapper từ terminal thường không tự có
fd này. Công cụ từ chối fd chuẩn 0/1/2, fd trùng và tệp thường.

Công cụ **không nhận khóa**; host Core đã xác thực, gắn quyền cho phiên
pipe. Nếu Core cần khóa thì host nhận qua nhập ẩn/két/handle bảo mật;
không thêm tham số khóa, biến môi trường, tệp hay log cho công cụ này.
Không đọc `.env`, `cau_hinh.that.toml`, Hot Folder hoặc cấu hình máy.

`--han-giay` (mặc định 30, tối đa 60) chỉ là hạn chờ mỗi trao đổi với
host, không phải hạn engine hoặc số đo sức chứa. Host trả receipt ngay
khi nhận việc; công cụ đọc trạng thái một lần. Chưa xong thì trả
`ChuaRo(ma_tuong_quan)` và mã thoát 3. Mất ACK/kết nối/hủy bằng bàn phím
trong lúc gửi hay đọc cũng trả ChuaRo. **Không tự gửi lại, không tạo mã
phiên mới để thử lại.** Tra cứu các mã `DEMO-luot-001-1`, `-2`… trong Core;
Core phải chống trùng theo mã đó, giữ receipt bền và cung cấp lối xem lại
kết quả. Mã phiên tối đa 65 ký tự, phải mới cho một đợt đo mới.

Thiếu Core/OCR/Local/binding/cấu hình/phê duyệt DEMO →
`LoiNghiepVu("DC_CHUA_CO_MOI_TRUONG_THU", …)`, mã thoát 2. Nguồn báo
HUY → `DC_HUY`; báo LOI → `DC_LOI_NGUON_THU`. Không đổi lỗi thành Khớp.
Lỗi tham số/nguồn được thay bằng câu Việt cố định, không in dữ liệu lỗi
từ host. Chỉ `--help` in hướng dẫn tham số.

## Chuẩn bị bộ mẫu và đáp án

1. Soạn Word hoàn toàn giả, có nhãn **DEMO**, ví dụ Công ty DEMO Ánh
   Dương, 1.000.000 VND, ngày dữ liệu `2026-10-30`. Không lấy hồ sơ thật
   rồi chỉ đổi tên. Có cả đoạn/bảng và hai ngôn ngữ nếu thuộc phạm vi.
2. Cài có chủ ý: tiền/ngày/MST có 0 đầu, thêm “không”, mất Điều/Khoản,
   thuê/thuế và các cặp đổi nghĩa; lưu danh sách đáp án độc lập. In,
   ký/gạch/chèn bằng tay, scan ở vài chất lượng khác nhau; có trang
   chỉ chữ ký/con dấu làm ca âm. Không kiểm đủ ký nháy/giáp lai đợt này.
3. Tải Word và PDF scan vào **kho Core DEMO** bằng cửa tải chung. Core
   xác minh dữ liệu giả, quyền/pháp nhân, phiên bản và băm từng tệp.
   Công cụ chỉ nhận `tep_id`, MIME và SHA-256, không đọc Word/PDF trên đĩa.
4. Lập manifest theo mẫu `cong-cu/DEMO-bo-thu-dc13.json`. Mẫu phát hành
   chỉ là khung giả với hash 0/1, **không có Word/scan thật tương ứng**;
   cần thay bằng tham chiếu/băm Core cấp. Không coi mẫu khung là phép đo.
   `dap_an_day_du=true` là cam kết bộ gán nhãn đã kiểm toàn bộ trang,
   không là bằng chứng rằng nguồn là DEMO; host Core phải xác minh riêng.
5. `diem[].neo` là khoảng Unicode code point `[bat_dau,ket_thuc)` trên
   **nguyên văn Word trước chuẩn hóa**, cùng đơn vị engine. Phép chèn
   dùng khoảng rỗng tại vị trí chèn. `nghiem_trong` ghi đáp án cần bắt
   ở mức đó; `sua_that` phân biệt thay đổi thực với ca OCR giả đã gán nhãn.
   Không chồng đáp án. Một điểm máy giao nhiều đáp án hoặc nhiều điểm
   máy giao một đáp án → chưa đo, cần Anh/lead sửa neo/gán nhãn, không
   cộng trùng hay suy đoán đã bắt đủ.
6. `vung_sua_tay[]` dùng trang từ 1, hộp `[x0,y0,x1,y1]` trong tọa độ
   trang nguồn OCR (host phải chuyển cùng hệ/đơn vị, kiểm ảnh/băm).
   `--iou-ghep` do Anh chọn và được lưu trong số đo: ngưỡng **ghép đáp
   án** một-một theo IoU giảm dần, không phải ngưỡng detector vận hành.
   Không truyền thì phép đo detector và tổng điểm Nghiêm trọng có vùng
   sửa tay để null. Không tự nhận nội dung chữ tay.

Manifest chỉ JSON trong workspace, tối đa 4 MiB, 1–100 ca, tối đa 60
trang/ca và 10.000 điểm/vùng. Vượt trần từ chối, không cắt. Không đọc
qua symlink/junction, thư mục gói/ma-nguon/var hoặc tên cấu hình bị cấm.
Đáp án được chấm trong RAM, **không gửi cho nguồn xử lý**.

## Binding handle đề nghị — Cần Core C-DC-08

**Chưa phải API/SDK đã phát hành.** Không thêm route `/doi-chieu`, không
import Core/engine, không nối engine trực tiếp. Host phải ánh xạ bốn thao
tác dưới đây vào **cửa chung Core** đã được review, điều phối toàn chuỗi
DC-12 (fan-in tệp, OCR trang/vùng, detector, Local-only, bỏ qua AI hợp
lệ, xuất đầy đủ JSON/PDF), cấp nguồn metadata và kết quả không bị cắt.
Không dùng văn bản tối đa 2.000 ký tự của màn Việc của tôi làm số đo.

Mỗi yêu cầu/phản hồi là một dòng JSON UTF-8, tối đa 4 MiB; không trùng
khóa/NaN/Infinity. Mọi yêu cầu có `phien_ban=1`, `thao_tac`,
`ma_tuong_quan`. Mọi phản hồi phải trả đúng `ma_tuong_quan`:

| Thao tác | Yêu cầu thêm | Phản hồi / trách nhiệm host |
|---|---|---|
| `kiem_moi_truong` | `module`, `quy_trinh`, `cau_hinh_core` là mã Core; `chi_local=true`, `nhan=DEMO`; `nguon_demo[]` chứa cặp tham chiếu Word/scan | `core_that`, `ocr_that`, `local_that`, `chi_local`, `bo_demo_da_xac_minh` đều true; `bam_cau_hinh` SHA-256 snapshot bất biến. Xác minh mọi tệp là DEMO/quyền/phạm vi trước gửi việc. Thiếu gì trả false/lỗi. |
| `gui_viec` | Bộ chọn trên + `word`, `scan`, `bam_cau_hinh`; không có đáp án | `trang_thai=DA_NHAN` hoặc `XONG/LOI/HUY/CHUA_RO`. Host chống trùng bền bằng mã tương quan; gọi quy trình chung Core, không gọi riêng engine từ công cụ. |
| `doc_viec` | Chỉ mã tương quan | Cùng trạng thái; `XONG` phải có bộ số đo bên dưới, nguồn/băm/phiên bản/quyền đã kiểm. Đang chạy trả CHUA_RO hoặc trạng thái chưa xong. |
| `luu_bao_cao` | `bao_cao`: chỉ số đo đã lọc | Host lưu qua Core trong cùng phạm vi, chống trùng; ACK `da_luu=true`. Mất ACK → ChuaRo, không tự nộp lại. |

Với `XONG`, host cấp các trường sau, không gửi nguyên văn, khóa, đường
máy, URL hay thông báo lỗi tùy ý. Công cụ chỉ đưa số/băm đã lọc ra báo cáo:

| Trường | Ý nghĩa / phần thiếu |
|---|---|
| `cloud` | Số lượt từ audit Core, bắt buộc integer 0. Không nhận boolean hoặc đếm tự khai từ model. Host phải chặn Cloud trước gửi. |
| `bam_word`, `bam_scan`, `bam_cau_hinh`, `so_trang` | Phải khớp đầu vào và snapshot; khác thì từ chối. Host kiểm lại bytes/quyền thật, hash không thay quyền. |
| `diem_day_du`, `diem[]` | Toàn bộ điểm **chữ** ở mọi mức, cả nhiễu/ẩn, không phân trang/cắt; mỗi điểm có `neo`, `muc` (`nghiem_trong/can_xem/hinh_thuc/nhieu_ocr`), `an_mac_dinh` bool. Không lẫn điểm detector vào đây. Có điểm không ánh xạ được về Word thì `diem_day_du=false`, không bỏ điểm rồi nói đủ. |
| `tu_abbyy[]` | Mỗi từ thật có `hop` hoặc null, `nghi_ngo` boolean hoặc null. Phải lấy từ ABBYY thật và ghim nguồn; không nội suy hộp/cờ từ OCR khác. `false` là có cờ, null là không có. Danh sách thiếu/null: chưa đo; danh sách đã đọc có từ nhưng thiếu toàn bộ hộp: đo được 0/N. |
| `ocr_vung[]` | Một boolean cho mỗi vùng thực sự đã OCR lại: có đọc ra Word hay không; host ghim nguồn/điểm/trang/hộp/băm qua C-DC-05. `so_vung_can_ocr` là mẫu số kế hoạch; thiếu/rỗng/không rõ nguồn không biến thành false/đã đo. |
| `tu_dien` | `bam`, `so_tu_kiem`, `so_tu_co_can_cu`. Băm bộ đã duyệt/giấy phép Q14; căn cứ không suy từ việc vắng từ. Từ điển fixture không được đánh dấu nguồn thật. |
| `detector_day_du`, `vung_sua_tay[]` | Đã quét mọi trang; danh sách vùng **được giữ hiện ở mức Nghiêm trọng** và có ảnh Core; mỗi vùng có `trang`, `hop` cùng hệ đáp án. Host kiểm phiên bản/băm/phương pháp trong cấu hình ghim và nguồn ảnh. Không nhận danh sách rỗng khi detector chưa chạy. |
| `giay_xu_ly_core`, `ram_dinh_bytes` | Thời gian xử lý và peak RAM **toàn tiến trình/chuỗi được host đo**, không giả bằng 0 hoặc dùng Python tracemalloc thay RAM tiến trình. Không đo được để null. Thời gian đợi công cụ được đo riêng. |
| `lech_dau_trang[]` | Đủ từng trang theo thứ tự, `so_tu`, `so_tu_lech`; mẫu số 0 → null có lý do. Thu tỷ lệ để trình ngưỡng OCR kém; không kết luận trang tốt khi chưa duyệt ngưỡng. |

Handle phải từ host tin cậy, gắn phiên/pháp nhân/quyền; các boolean/băm
trong JSON tự chúng không chứng minh nguồn hoặc quyền. Chưa có binding
được review thì không chạy thật. Core phải khép C-DC-01…06/08 trước
nghiệm thu đầy đủ; công cụ không bù thiếu bằng OCR/AI riêng.

## Cách đọc số đo và giữ bằng chứng

- Mỗi tỷ lệ có `tu_so`, `mau_so`, `gia_tri`, `ly_do`. Chưa đo giữ null,
  mẫu số 0 không thành 0%. Không cộng bỏ các ca thiếu số đo để báo đạt.
- `nghiem_trong` = số điểm chữ bắt đúng mức và hiện + số vùng sửa tay
  ghép được / tổng điểm chữ Nghiêm trọng cài + tổng vùng sửa tay cài.
  Có thêm `nghiem_trong_chu` và detector recall/precision để xem riêng.
- `sua_that_bi_an`: tử số là sửa chữ thật khớp điểm bị ẩn/`nhieu_ocr`;
  mẫu số gồm mọi sửa chữ thật và vùng sửa tay cài. Chỉ tính khi toàn bộ
  vùng sửa tay đã bắt và giữ hiện Nghiêm trọng; nếu mất vùng, chưa biết
  bị ẩn hay bỏ sót thì tử số null. `sua_that_chu_bi_an` giữ phép đo chữ
  riêng. `sua_that_bo_sot` đếm sửa chữ không tìm thấy và vùng chưa bắt /
  tổng sửa thật. Có bỏ sót giữ KHONG_DAT; không dùng số 0 bị ẩn để che
  bỏ sót. Không suy rằng detector rỗng là sạch.
- Lệch giả/trang = số điểm chữ `can_xem` không ứng với sửa thật trong
  đáp án đầy đủ / số trang scan. Detector có precision/recall riêng.
  Thông lượng trang/giây và điểm/giây có tử/mẫu; số trang/số điểm thực
  tế nằm từng ca. Đây là sức chứa **đã thử**, chưa là trần tối đa model.
- `cong_chat_luong=DAT_TREN_BO_DEMO` chỉ khi bắt đủ **100%** Nghiêm
  trọng, **0** sửa thật bị ẩn và không bỏ sót sửa chữ thật. Một thất bại
  đã đo giữ KHONG_DAT dù còn trường chưa đo. Hai chỉ tiêu này **không
  chứng minh bảo đảm trên mọi tài liệu**.
- `ket_luan_do=CHUA_DO` khi thiếu phép đo cần thiết; `KHONG_DAT` khi có
  thất bại đã biết; `CHO_ANH_DUYET_NGUONG` khi đủ số đo và qua hai cổng.
  Không tự đặt ngưỡng detector/lệch giả/OCR kém, không bật module. Mã
  thoát 2 khi chưa đo/không đạt, 3 khi chưa rõ, 130 khi hủy trước gửi.
- Kết quả ưu tiên ACK về Core; stdout/RAM vẫn có khung số đo. Chỉ khi Anh
  thêm `--bao-cao e_doi_chieu/docs/DEMO-ket-qua-dc13.json` mới ghi thêm
  **một** JSON DEMO mới trong workspace, ngoài gói. Không ghi đè, không
  lưu khóa/đường máy/tep_id/nội dung văn bản hoặc lỗi nguồn. Đây là công
  cụ đo ngoài runtime, không là kho hay cấu hình engine. Không tạo tệp
  tạm; handle duplicate đóng bằng `with/finally`; host phải đóng pipe
  khi timeout/hủy để worker chờ đọc kết thúc. Không có retry nền.

## Anh kiểm trên trình duyệt Core thật

Mọi dòng sau giữ **CHỜ ANH TỰ CHẠY**; pytest không đánh dấu đã đạt:

| Ca kiểm | Thao tác và bằng chứng DEMO cần lưu trong kho Core |
|---|---|
| Hai cột/ảnh | Mở đúng cặp/phiên bản; Word và ảnh crop cùng vị trí, có OCR; bật xem nhiễu, kiểm không mất điểm, thử màn hẹp; lưu ảnh màn DEMO. |
| Bốn xác nhận | Lỗi OCR / thay đổi đã thống nhất (nội dung đúng bắt buộc) / bản ký sai / không ảnh hưởng (lý do bắt buộc); lưu receipt/journal chỉ thêm, nguồn người/giờ từ Core. |
| CAS | Hai phiên cùng row_version; một thắng, bên kia lỗi xung đột và tải lại; journal không đè/mất, không nhân đôi khi mất ACK. |
| Quyền | Người phụ trách được giao quyền; người nộp/khác pháp nhân/không quyền bị từ chối xem, tải ảnh, xác nhận, ghi ngăn trực tiếp; quyền bị thu hồi ngay lúc commit. |
| Chặn | Khi có Nghiêm trọng/sửa tay/chưa kiểm đủ hoặc “Bản ký sai”, module giữ chặn, dữ liệu tầng 1 không được duyệt; lưu trạng thái module và thông báo đúng người Q01. |
| Mở hiệu lực | Đủ xác nhận hợp lệ, không mâu thuẫn/bản ký sai; Core/module tính lại điều kiện, ACK và trạng thái thực; chỉ cờ engine không đủ làm bằng chứng. |
| Hai người Q03 | Đã chọn có theo quyết định 15/11: thay đổi Nghiêm trọng đã thống nhất cần hai người khác nhau, người duyệt có quyền cấp hai; một người chưa mở, người sai quyền không mở; lưu cả hai receipt và trạng thái sau cùng. |

Giữ ảnh màn/receipt/JSON/PDF DEMO trong kho Core cùng mã tương quan,
phiên bản/băm nguồn, thời điểm và cấu hình đo; tránh chụp thanh địa chỉ,
token, thư mục máy hoặc thông tin ngoài DEMO. Nếu cần xuất file bằng
chứng, Anh chọn đích workspace riêng; công cụ này chỉ ghi JSON khi có
`--bao-cao`. Sau đo trình Anh bảng số đo và ngưỡng đề xuất kèm điều kiện
áp dụng; nếu thiếu chất lượng thì lập lát bổ sung, không giảm cổng.
