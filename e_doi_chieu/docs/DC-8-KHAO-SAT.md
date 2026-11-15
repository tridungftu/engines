# DC-8 — Khảo sát và bản đầu vùng nghi sửa tay

15/11/2026 · PR: **chờ lead mở** · 7 giờ **ƯỚC TÍNH**, chưa cam kết tỷ lệ phát hiện.

**Kết luận: hoàn thành khảo sát/bản đầu; phương pháp ảnh chưa đạt để vận hành
độc lập.** Chọn `net_de_vung_chu / DC-8.1-thu-nghiem` để tạo ứng viên xem ảnh.
Đã đo thuật toán thật trên DEMO tổng hợp: **TP=3, FP=0, FN=3**, recall 50%.
Không cho kết luận không sửa tay, không bỏ chặn. Local vision **chưa đo**,
model/thời gian/RAM/chất lượng đều `null`. Không đổi tiêu chí nghiệm thu DC-13.

Đã kiểm bằng Core giả (CoreGia). Quyền/phép xoay/nguồn loại trừ được cấp bởi
adapter DEMO trong tests; chưa kiểm Core thật, scanner, OCR hoặc model thật.
DC-Q07/08: không kiểm đủ ký nháy hay dấu giáp lai từng trang. Q04 giữ sàn
Nghiêm trọng và yêu cầu xác nhận cho vùng nghi ngờ. Q13 chưa có nguồn model
được lead/Anh xác nhận; không tải/cài model, không mạng, 0 Cloud.

## 1. So sánh và căn cứ chọn

| Phương pháp | Dữ liệu/nguồn cần có | Ưu điểm | Nhược điểm và số đo hiện có |
|---|---|---|---|
| Pixel dựa vùng chữ, nét đè và nét chèn liên thông | PNG/JPEG trang đủ băm/kích thước; hộp từ OCR; metadata Core xác nhận đúng nguồn, tỷ lệ, xoay; Pillow ghim từ lock OCR | Chạy offline, truy được căn cứ hình học, không cần model; đã thực hiện được bằng nguồn cho phép | Nhạy nét mờ/nét dính chữ/ký chồng chữ. DEMO 12 ca: 3 TP, 0 FP, 3 FN; **chỉ chọn làm bản đầu hỗ trợ xem** |
| Hiệu ảnh bản Word render và scan sau căn chỉnh | Word render đúng phiên bản/font; cặp trang cùng nội dung; căn chỉnh biến dạng/scan có kiểm sai số và băm; bộ DEMO có đáp án | Có căn cứ nét dư so với bản in, có thể hỗ trợ nét nằm trong chữ | Dàn trang/độ nghiêng/nhiễu có thể tạo nét giả; nguồn render/căn chỉnh tin cậy chưa có. Chất lượng/thời gian/RAM: **null/chưa đo**; chưa triển khai |
| Local vision qua Core | Lead xác nhận model/phiên bản/băm/quyền dùng; máy đủ RAM/VRAM; Core cấp ảnh và nhận kết quả đầy đủ từng trang, hộp đúng hệ tọa độ; cùng bộ đáp án | Có thể dùng ngữ cảnh để phân biệt dấu/ký/sửa; đây là giả thuyết cần đo | Có thể bỏ sót/bịa vùng, tọa độ không ổn định; không thay bằng chứng pixel hoặc xác nhận người. Model/chất lượng/thời gian/RAM: **null/chưa đo**; engine không gọi AI |

Không chọn phương pháp vận hành cuối cùng chỉ bằng 12 ca tổng hợp. Không
chọn model theo tên hoặc suy đoán tài nguyên. Các nguồn/detector khác chưa
được cấp phải trình riêng, không tự thêm dependency hay cài từ mạng.

## 2. Thuật toán đã đo và giới hạn

Ảnh giải mã thực bằng Pillow: kiểm định dạng, số frame, EXIF, pixel trước
load, `verify` rồi `load`, ghép alpha lên nền trắng. Chỉ PNG/JPEG một trang;
không tự áp EXIF xoay, không tự deskew/crop. Không dựa vào màu mực.

Đưa ảnh về chiều đọc theo phép xoay Core cấp; lấy median chiều cao hộp từ
OCR làm đơn vị hình học. Quét **mọi dòng pixel** của toàn trang, lập run nét
tối và thành phần liên thông 8 lân cận. Hai nhóm ứng viên:

- Run ngang đủ dài, cắt phần giữa nhiều hộp từ hoặc vượt chiều rộng một
  hộp từ: `gach_de`. Chỉ đưa chữ OCR của các hộp thực giao nét vào
  `chu_in_bi_de`, ghi nguồn `ocr_giao_net_gach`; đây không phải tự đọc lại
  chữ in/khẳng định nội dung đã bị đổi.
- Thành phần liên thông có độ rộng/cao/mật độ và biến thiên phù hợp, gần
  dòng chữ, phần chồng hộp chữ không quá lớn: `net_chen_gan_chu`. Không coi
  mọi nét ngoài OCR, mực màu, đường gạch dưới hoặc vật thể xa dòng là sửa tay.

Ngưỡng nằm trong `THAM_SO`, có băm trong snapshot; chúng là ngưỡng kỹ thuật
**chỉ đo DEMO**, chưa phải ngưỡng đã duyệt vận hành. Nét xám 190 bị bỏ bởi
ngưỡng 160 là một FN công bố, không sửa đáp án để tăng recall. Nét nối vào
chữ in cũng có thể bị lọc nhầm. Thuật toán không tự đọc nội dung chữ tay.

Trần: 60 trang, 20 triệu pixel/ảnh, 20 MiB/tệp, 128 MiB bytes đầu vào duy
nhất/việc; trần thấp hơn trong cấu hình/snapshot vẫn có hiệu lực. Trần việc
900 giây, 10.000 vùng gồm cả vùng cần xem từ metadata; 20.000 từ/trang,
100.000 run/trang và 200.000 lượt dựng chỉ mục dải ngang. Vượt trần từ chối
`DC_QUA_GIOI_HAN`, không cắt ngầm. Hủy được kiểm trong đọc/đổi tọa độ/quét
dòng/thành phần/cắt/tải ảnh và trước nộp snapshot.

## 3. Cửa ảnh tin cậy cần Core cấp

Đầu vào năng lực vẫn **nguyên** `ho_so_doi_chieu` phiên bản 1, nhận
`da_nhan` hoặc `da_so`; chỉ có `tham_so.che_do=day_du`. Không đổi schema
chung hoặc API v1/SDK 2.0. Metadata dưới đây là **quy ước adapter tạm cần
Core review**, giống nguồn phân trang ở DC-4; không thêm route hoặc trường
manifest riêng cho Core. Runtime không tự gắn metadata từ JSON caller.

`ngu_canh.doi_chieu_anh` do Core tin cậy gắn:

```json
{
  "phien_ban": 1,
  "ma_cap": "DEMO-cap-001",
  "bam_ho_so": "sha256:<băm bytes snapshot đầu vào>",
  "bam_ban_ky": "sha256:<băm PDF đã ký>",
  "trang": [{
    "so": 1,
    "bam_anh": "sha256:<băm PNG/JPEG thực>",
    "rong_nguon": 480, "cao_nguon": 240, "don_vi": "pt",
    "he_toa_do": "goc_tren_trai",
    "ti_le": 2, "xoay": 90, "rong_px": 480, "cao_px": 960,
    "vung_loai_tru": [{
      "loai": "chu_ky", "hop": [325, 80, 375, 120],
      "can_cu": {"nguon": "core_xac_nhan", "ma": "DEMO-vung-001", "bam_anh": "sha256:<băm cùng ảnh>"}
    }]
  }]
}
```

Các băm minh họa phải thay bằng băm thật, không dùng mẫu này làm fixture đạt.
Danh sách ảnh/OCR/metadata phải đúng thứ tự và phủ chính xác `1..so_trang`.
Đọc ảnh qua `viec.mo_tep`; đối chiếu băm bytes và kích thước API thật, kiểm
pixel trước giải mã; không đọc đường máy/URL/base64 từ caller. Snapshot
khớp nguyên phong bì đã băm; đọc lại nguồn/text/bộ và các tham chiếu cũ
trong phạm vi quyền hiện tại. Không đổi bộ giữa lượt.

Hệ nguồn `pt` hoặc `px`, gốc trên trái, hộp nửa mở `[x0,y0,x1,y1)` hữu hạn
trong trang. `xoay` là 0/90/180/270 độ theo chiều kim đồng hồ từ nguồn sang
ảnh; engine xoay ngược để quét. Cần Core xác nhận ảnh là **toàn trang**, chưa
crop/skew hoặc biến dạng khác. Kích thước phải khớp tỷ lệ đã cấp, chỉ chấp
nhận làm tròn raster ≤0,51 pixel. Ánh xạ dùng biên raster thực theo từng
trục để không vượt biên vì làm tròn; không suy DPI từ tên tệp. Biến đổi khác
chưa mô tả được thì từ chối `DC_THIEU_ANH`.

Thiếu ảnh/trang/quyền ảnh/hệ tọa độ, ảnh hỏng, EXIF chưa chuẩn hóa →
`DC_THIEU_ANH`. Sai băm/metadata bytes đã ghim → `DC_SAI_NGUON`. Thiếu/sai
phiên bản phương pháp, thiếu hộp từ OCR hoặc detector không chứng minh quét
toàn trang → `DC_CHUA_CO_BO_PHAT_HIEN`; không trả `[]` giả. Thiếu toàn bộ cấu
hình vẫn theo cổng chung `CHUA_CAU_HINH`. Lỗi bất ngờ được lớp bọc an toàn
đổi thành `DC_LOI_XU_LY`, không log nội dung/path/exception gốc. `ChuaRo`,
lỗi SDK và hủy được bảo toàn; không báo thành công thay nguồn đang treo.

## 4. Chữ ký, dấu và bảo toàn kết quả

Chỉ loại ứng viên nằm **trọn** trong vùng chữ ký/con dấu/ký nháy mà Core
đã xác nhận đúng băm ảnh, và toàn vùng đó không chồng hộp khối/dòng/từ có
nội dung hợp đồng. Không chỉ nhìn vùng nhỏ chứa một nét để bỏ toàn khối.
Thiếu căn cứ hoặc chồng chữ → `can_xem=true`, không loại. Nếu detector chưa
tạo ứng viên tại vùng chưa thể loại trừ, vẫn cắt vùng để người xem, gắn
`nguon_ung_vien=metadata_can_xem`; **không tính là detector đã phát hiện**.
Ứng viên pixel mang `nguon_ung_vien=detector_pixel`.

Mỗi vùng giữ mã ổn định có số trang/băm ảnh, `hop` theo hệ nguồn,
`hop_anh_px` của nét và `hop_cat_anh_px` có lề để xem ngữ cảnh, PNG thực từ
`tai_tep_ra`, băm/kích thước ảnh cắt, phương pháp/phiên bản, căn cứ,
`chu_tay=null`, `muc_san=muc=nghiem_trong`, `bat_buoc_xac_nhan=true`.
Không xóa/đổi các điểm lệch, sàn hoặc kiểm đã có từ DC-4/DC-5.

Snapshot mới `giai_doan=da_quet_anh`, trỏ snapshot tiền nhiệm; `quet_anh.trang`
ghi đúng trang đã quét, băm ảnh, số pixel, phạm vi toàn ảnh, biến đổi, căn
cứ loại trừ và số ứng viên pixel/metadata tách riêng. Ghim băm tham số/cấu
hình/metadata; chất lượng hồ sơ thực để `null`. Quét toàn pixel không chứng
minh recall đủ: **`kiem_tra.sua_tay=chua_kiem`, `da_kiem_du=false`,
`ket_luan=null`, `de_nghi_chan=true`** luôn được giữ trong bản thử nghiệm.
Danh sách rỗng khi đã quét có nghĩa không tạo được ứng viên, không là bằng
chứng không có sửa tay. DC-9 phải giữ trạng thái này khi tổng hợp.

Quét xong mọi trang mới tải crop; mọi ảnh/snapshot kết quả qua kho Core,
không tệp tạm hoặc đệm trên đĩa. Context manager đóng ảnh/BytesIO khi
lỗi/hủy. Nếu hủy/lỗi sau một lần tải Core, Core cần thu hồi tệp mồ côi theo
vòng đời việc; engine không tự xóa hồ sơ hoặc dùng sổ đĩa.

## 5. Phép đo thật trên DEMO tổng hợp

Nguồn xác định: `tests/demo_sua_tay.py`; 12 ca/11 raster khác nhau, vì ca
chữ ký và ký nháy dùng cùng nét nhưng metadata khác. Ảnh 480×240, font mặc
định đóng gói trong Pillow, hộp từ OCR giả đã biết; 6 vùng sửa có đáp án.
Đây **không** phải OCR/model/ảnh scan thực, không có tập kiểm độc lập.
Kết quả detector giả chỉ kiểm giao thức, tuyệt đối không vào bảng đo này.

Đáp án/ảnh băm/hộp detector/kết quả từng ca và thời gian lưu nguyên tại
`DC-8-SO-DO-DEMO.json`. Ghép vùng một-một theo IoU lớn nhất, IoU ≥0,3:

| Chỉ số | Đo trên bộ DEMO này |
|---|---:|
| TP / FP / FN | 3 / 0 / 3 |
| Recall vùng | 3/6 = 50% |
| Precision vùng | 3/3 = 100%, chỉ 3 dự đoán |
| Lệch giả/trang | 0/12 = 0, không suy rộng |
| Thời gian 12 ca, có tracemalloc | 0,152430 giây |
| Đỉnh cấp phát Python được tracemalloc thấy | 297.204 bytes |
| RAM tiến trình/native Pillow, VRAM | null/chưa đo |
| Local vision: mọi chỉ số | null/chưa đo |

Ba ca phát hiện: gạch qua chữ, nét chèn, nét sát chữ in. Ba FN: ký chồng
chữ, nét mờ, nét mảnh trong chữ. Bộ âm tính có chữ ký/dấu/ký nháy được cấp
vùng đủ căn cứ, chữ in màu, nét xa chữ và trang không vết. Trong runtime,
vùng ký chồng vẫn xuất để xem nhờ metadata cảnh báo; điều đó **không** sửa
FN của thuật toán thành TP. Nguồn loại trừ thật còn phụ thuộc Core.

Lệnh tái đo: `.venv/Scripts/python e_doi_chieu/cong-cu/do_sua_tay_demo.py --do-demo`.
Thời gian/RAM thay theo máy, không dùng số này làm trần nghiệm thu hoặc
cam kết latency. Cả số đo chất lượng và giới hạn của bộ đều được giữ.

## 6. Công cụ Q13 và việc tiếp theo

`cong-cu/DO-SUA-TAY-DEMO.cmd` (ASCII) gọi `--chay-kho`: đã chạy khô, mã 0,
in nguồn cần có và băm 12 ca, không quét máy/model hoặc gọi mạng. CLI cũng
nhận `--do-demo --ket-qua-vision <JSON-DEMO-Core-xuất>` để chấm file export.
Nó không gửi ảnh tới Local AI hoặc gọi engine khác. File export phải có:

```json
{"phien_ban":1,"nguon":"core_local","model":"DEMO-model",
 "phien_ban_model":"DEMO-1","bam_model":"sha256:<64 hex>",
 "giay_phep":"<nguồn giấy phép lead đã kiểm>","giay_tong":null,"ram_dinh_bytes":null,
 "trang":[{"ma":"gach","bam_anh":"sha256:<băm DEMO>",
           "da_quet_toan_trang":true,"hop":[[30,93,311,96]]}]}
```

Cần đủ 12 ca đúng băm/hộp hệ nguồn; mẫu rút gọn trên không hợp lệ để chấm.
Core/lead dựng ảnh bằng cùng generator, cấp cho model qua luồng Core được
duyệt, đo thời gian/RAM thật rồi xuất. CLI không chứng nhận nguồn/quyền/
giấy phép chỉ từ nhãn JSON: kết quả chấm ghi rõ chưa xác minh nguồn và
không đủ điều kiện vận hành. Không có file đo thật thì giữ `null`.

**Cần Core:** C-DC-02 quyền/vòng đời mọi tệp con và ảnh ra; C-DC-05 nguồn
ảnh và biến đổi toàn trang/từ OCR/vùng loại trừ có provenance thật, điều
phối Local vision; C-DC-04 không mở chặn khi detector còn `chua_kiem`;
C-DC-01/06 ngăn bền/log SDK an toàn giữ nợ hiện hành. Không có câu xin đổi
phạm vi Q07/08 hoặc cho phép engine gọi model trực tiếp.

**Dự toán bổ sung, chưa được giao/phê duyệt:**

- Chuẩn bị bộ DEMO in/ký/sửa/scan thật có quyền dùng và đáp án vùng,
  chất lượng scan đa dạng, kiểm nguồn tọa độ/loại trừ: **4–6 giờ ước tính**.
- Nhánh ảnh có bản render và căn chỉnh được kiểm: **8–12 giờ ước tính**
  sau khi Core cấp render/font/quan hệ trang; đo lại FN/FP, không giảm tiêu chí.
- Nhánh so sánh Local vision qua Core: **6–10 giờ ước tính** sau khi lead
  cấp model/giấy phép/tài nguyên; không gồm tải/cài, chờ máy hoặc huấn luyện.

Chọn nhánh tiếp sau khi nguồn và phép đo thật có đủ; không cộng cả hai
nhánh thành cam kết. Detector hiện tại chưa đạt, chưa thay bằng ngưỡng dễ
hơn hoặc coi mock là chất lượng thật. Kết quả ba lệnh bắt buộc, thời gian
thực tế và trạng thái bàn giao ghi tại `VIEC.md`.
